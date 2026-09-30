#!/opt/homebrew/bin/python3
"""staleref 量測:段落提到的程式名稱,在段落寫下之後定義被改過 → 標可能過時。

唯讀:只對 <exp>/rtb 這個 --shared clone 跑 git 讀取指令。
用法: staleref.py <repo> <measure_commit> <outdir>
"""
import ast, builtins, collections, json, keyword, os, re, subprocess, sys, time

REPO, M, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
KDIR = "docs/rtb-production-agent-demo-knowledge"
CODE_PREFIXES = ("src/", "tests/")
T0 = time.time()
timing = {}


def git(*args):
    return subprocess.run(["git", "-C", REPO, "-c", "core.quotepath=off", *args], capture_output=True, check=True).stdout.decode("utf-8", "replace")


class Cat:
    def __init__(self):
        self.p = subprocess.Popen(["git", "-C", REPO, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.cache = {}

    def get(self, sha):
        if sha is None or set(sha) == {"0"}:
            return None
        if sha in self.cache:
            return self.cache[sha]
        self.p.stdin.write((sha + "\n").encode()); self.p.stdin.flush()
        hdr = self.p.stdout.readline().decode().split()
        if hdr[1] == "missing":
            return None
        n = int(hdr[2]); data = self.p.stdout.read(n); self.p.stdout.read(1)
        s = data.decode("utf-8", "replace")
        self.cache[sha] = s
        return s


cat = Cat()
ID_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
FLAG_RE = re.compile(r"--[a-z][a-z0-9-]*[a-z0-9]")


def py_defs(src):
    """回傳 {名稱: sorted list of 定義原文};函式/類別/模組層與類別層常數賦值。解析失敗回 None。"""
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return None
    out = collections.defaultdict(list)

    def seg(node):
        s = ast.get_source_segment(src, node) or ""
        deco = "".join((ast.get_source_segment(src, d) or "") for d in getattr(node, "decorator_list", []))
        return deco + s

    def targets(t):
        if isinstance(t, ast.Name):
            yield t.id
        elif isinstance(t, (ast.Tuple, ast.List)):
            for e in t.elts:
                yield from targets(e)

    def walk(body, top):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                out[node.name].append(seg(node))
                walk(node.body, False)
            elif top is not None and isinstance(node, (ast.Assign, ast.AnnAssign)):
                ts = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in ts:
                    for n in targets(t):
                        out[n].append(seg(node))
            elif isinstance(node, (ast.If, ast.Try, ast.With, ast.For, ast.While)):
                for attr in ("body", "orelse", "finalbody"):
                    walk(getattr(node, attr, []) or [], top)
                for h in getattr(node, "handlers", []) or []:
                    walk(h.body, top)

    # 模組層與類別層的賦值算定義;函式內的區域變數不算
    def walk_top(body):
        walk(body, True)
    walk_top(tree.body)
    return {k: sorted(v) for k, v in out.items()}


_defcache, _tokcache = {}, {}
def py_defs_b(sha, src):
    if sha not in _defcache:
        _defcache[sha] = py_defs(src)
    return _defcache[sha]
def tok_counts_b(sha, src):
    if sha not in _tokcache:
        _tokcache[sha] = tok_counts(src)
    return _tokcache[sha]


def tok_counts(src):
    c = collections.Counter(ID_RE.findall(src))
    c.update(FLAG_RE.findall(src))
    return c


# ---------- 1. 歷史索引:每個提交改了哪些定義 / 哪些字的出現次數 / 哪些檔 ----------
t = time.time()
commit_time = {}
for line in git("log", "--format=%H %ct %P", M).splitlines():
    h, ct, *parents = line.split()
    commit_time[h] = int(ct)
nonmerge = [h for h in git("rev-list", "--no-merges", M).split()]
def_changes = collections.defaultdict(set)    # name -> {commit}
tok_changes = collections.defaultdict(set)    # token -> {commit}
file_changes = collections.defaultdict(set)   # path -> {commit}
ever_defined, ever_tokens, ever_paths = set(), set(), set()
raw_by_commit = collections.defaultdict(list)
_cur = None
for ln in git("log", "--no-merges", "--root", "--no-renames", "--raw", "--no-abbrev", "--format=@@%H", M, "--", "src", "tests").splitlines():
    if ln.startswith("@@"):
        _cur = ln[2:]
    elif ln.startswith(":"):
        raw_by_commit[_cur].append(ln)
for h in nonmerge:
    for ln in raw_by_commit.get(h, []):
        meta, path = ln.split("\t", 1)
        if not path.startswith(CODE_PREFIXES):
            continue
        _, _, old, new, status = meta[1:].split()
        file_changes[path].add(h); ever_paths.add(path)
        a, b = cat.get(old) or "", cat.get(new) or ""
        ca, cb = tok_counts_b(old, a), tok_counts_b(new, b)
        ever_tokens.update(cb); ever_tokens.update(ca)
        for k in set(ca) | set(cb):
            if ca[k] != cb[k]:
                tok_changes[k].add(h)
        if path.endswith(".py"):
            da, db = (py_defs_b(old, a) if a else {}), (py_defs_b(new, b) if b else {})
            if da is None or db is None:   # 語法壞掉就退回用出現次數
                continue
            ever_defined.update(da); ever_defined.update(db)
            for k in set(da) | set(db):
                if da.get(k) != db.get(k):
                    def_changes[k].add(h)
timing["history_index_s"] = round(time.time() - t, 2)

# ---------- 2. 量測點的程式樹 ----------
t = time.time()
tree_blobs = {}
for ln in git("ls-tree", "-r", M, "--", "src", "tests").splitlines():
    meta, p = ln.split("\t", 1)
    tree_blobs[p] = meta.split()[2]
tree_files = list(tree_blobs)
now_tokens, now_defined = collections.Counter(), set()
for p in tree_files:
    s = cat.get(tree_blobs[p]) or ""
    now_tokens.update(tok_counts_b(tree_blobs[p], s))
    if p.endswith(".py"):
        d = py_defs_b(tree_blobs[p], s)
        if d:
            now_defined.update(d)
now_paths = set(tree_files)
basename_idx = collections.defaultdict(set)
for p in now_paths | ever_paths:
    basename_idx[os.path.basename(p)].add(p)
pkg_names = {p.split("/")[1] for p in tree_files if p.startswith("src/") and p.count("/") >= 2}
STOP = set(keyword.kwlist) | set(dir(builtins)) | set(sys.stdlib_module_names) | pkg_names | {
    "self", "cls", "python", "pytest", "ruff", "mypy", "pip", "git", "noqa", "src", "tests", "docs", "main"}
timing["tree_index_s"] = round(time.time() - t, 2)


def resolve_file(ref, universe):
    ref = ref.strip("./")
    hits = {p for p in universe if p == ref or p.endswith("/" + ref)}
    return hits


def module_file(dotted, universe):
    base = dotted.replace(".", "/")
    for cand in (f"src/{base}.py", f"src/{base}/__init__.py", f"{base}.py", f"{base}/__init__.py"):
        if cand in universe:
            return {cand}
    return set()


WIKI = re.compile(r"\[\[[^\]]*\]\]")
BT = re.compile(r"`([^`\n]+)`")
PATH_RE = re.compile(r"[A-Za-z0-9_./-]*[A-Za-z0-9_-]\.(?:py|toml)(?![A-Za-z0-9_])")
DOTTED = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+")
UNDERSCORE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+(?![A-Za-z0-9_])")
CAMEL = re.compile(r"(?<![A-Za-z0-9_])(?:[a-z]+[A-Z][A-Za-z0-9]*|[A-Z][a-z0-9]+[A-Z][A-Za-z0-9]*)(?![A-Za-z0-9_])")


UNIV = {False: (set(now_tokens), now_defined, now_paths),
        True: (ever_tokens | set(now_tokens), ever_defined | now_defined, now_paths | ever_paths)}


def extract(text, ever=False):
    """回傳 (identifiers, flags, files)。只保留量測點程式樹找得到的(ever=True 時放寬到歷史上出現過)。"""
    text = WIKI.sub(" ", text)
    ids, flags, files = set(), set(), set()
    tokset, defset, puniv = UNIV[ever]

    def add_id(x):
        if len(x) < 2 or x in STOP or x.startswith("__"):
            return
        if x in defset or x in tokset:
            ids.add(x)

    def add_path(x):
        hits = resolve_file(x, puniv)
        if not hits and "/" not in x:
            hits = {p for p in basename_idx.get(x, ()) if p in puniv}
        files.update(hits)
        return bool(hits)

    rest = text
    for span in BT.findall(text):
        s = span
        for pth in PATH_RE.findall(s):
            add_path(pth)
        s = PATH_RE.sub(" ", s)
        for f in FLAG_RE.findall(s):
            if f in tokset:
                flags.add(f)
        s = FLAG_RE.sub(" ", s)
        for d in DOTTED.findall(s):
            mf = module_file(d, puniv)
            if mf:
                files.update(mf)
            for part in d.split("."):
                add_id(part)
        s = DOTTED.sub(" ", s)
        for x in ID_RE.findall(s):
            add_id(x)
    rest = BT.sub(" ", text)
    for pth in PATH_RE.findall(rest):
        add_path(pth)
    rest = PATH_RE.sub(" ", rest)
    for x in UNDERSCORE.findall(rest) + CAMEL.findall(rest):
        add_id(x)
    return ids, flags, files


def changes_of(ids, flags, files):
    """回傳 {名稱: set(改動提交)};判法見報告。"""
    out = {}
    for x in ids:
        if x in def_changes or x in now_defined or x in ever_defined:
            out[x] = def_changes.get(x, set())
        else:
            out[x] = tok_changes.get(x, set())
    for f in flags:
        out[f] = tok_changes.get(f, set())
    for p in files:
        out["file:" + p] = file_changes.get(p, set())
    return out


# ---------- 3. 筆記切段 + blame ----------
t = time.time()
notes = [p for p in git("ls-tree", "-r", "--name-only", M, "--", KDIR).splitlines() if p.endswith(".md")]
DATE_RE = re.compile(r"20\d\d-\d\d-\d\d")


def blame(path):
    out, cur, info = [], None, {}
    for ln in git("blame", "--line-porcelain", M, "--", path).splitlines():
        if re.match(r"^[0-9a-f]{40} ", ln):
            cur = ln.split()[0]
        elif ln.startswith("\t"):
            out.append(cur)
    return out


def segment(lines):
    """回傳 [(start, end, kind, fmfield)],行號 1 起算、含頭尾。"""
    segs = []
    i, n = 0, len(lines)
    fm_end = -1
    if lines and lines[0].strip() == "---":
        for j in range(1, n):
            if lines[j].strip() == "---":
                fm_end = j
                break
    if fm_end > 0:
        j = 1
        field = None
        while j < fm_end:
            ln = lines[j]
            m = re.match(r"^([A-Za-z_]+):", ln)
            if m:
                field = m.group(1)
                segs.append((j + 1, j + 1, "fm_key", field))
            elif field == "summary" and ln.strip():
                segs.append((j + 1, j + 1, "summary", field))
            elif ln.strip():
                segs.append((j + 1, j + 1, "fm_other", field))
            j += 1
        i = fm_end + 1
    cur = None
    for j in range(i, n):
        ln = lines[j]
        if not ln.strip():
            if cur:
                segs.append((cur, j, "body", None)); cur = None
        elif ln.lstrip().startswith("#"):
            if cur:
                segs.append((cur, j, "body", None)); cur = None
            segs.append((j + 1, j + 1, "heading", None))
        else:
            if cur is None:
                cur = j + 1
    if cur:
        segs.append((cur, n, "body", None))
    return segs


def fm_value(lines, key):
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        m = re.match(rf"^{key}:\s*(\S+)", ln)
        if m:
            return m.group(1)
    return None


import datetime
def day_of(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d")


INV = {h for h in nonmerge if h[:7] in {"b2fc512", "c177791", "d98b4ca", "0ffba7d", "8ff8c95", "0b2499a", "5ec931e"}}
revcache = {}
def after_set(p):
    if p not in revcache:
        revcache[p] = set(git("rev-list", "--no-merges", M, f"^{p}").split())
    return revcache[p]


code_commits_by_day = [(h, day_of(commit_time[h])) for h in nonmerge]
def after_day(d):
    return {h for h, dd in code_commits_by_day if dd > d}


paras = []
for path in notes:
    text = git("show", f"{M}:{path}")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    bl = blame(path)
    note_upd = fm_value(lines, "updated") or fm_value(lines, "date") or fm_value(lines, "created")
    last_heading_date = None
    for (s, e, kind, field) in segment(lines):
        seg_text = "\n".join(lines[s - 1:e])
        if kind == "heading":
            dd = DATE_RE.findall(seg_text)
            last_heading_date = dd[0] if dd else None
        commits = [bl[k - 1] for k in range(s, e + 1)]
        pmax = max(commits, key=lambda c: commit_time.get(c, 0))
        pmin = min(commits, key=lambda c: commit_time.get(c, 0))
        in_scope = kind in ("summary", "body", "heading")
        rec = dict(note=path[len(KDIR) + 1:], start=s, end=e, kind=kind, field=field, in_scope=in_scope,
                   text=seg_text, p_max=pmax, p_min=pmin, p_max_day=day_of(commit_time[pmax]),
                   p_min_day=day_of(commit_time[pmin]), note_updated=note_upd)
        dd = DATE_RE.findall(seg_text)
        rec["para_date"] = dd[0] if dd else (last_heading_date if kind == "body" else None)
        for tag, ever in (("now", False), ("ever", True)):
            ids, fl, fs = extract(seg_text, ever)
            ch = changes_of(ids, fl, fs)
            rec[f"names_{tag}"] = sorted(ch)
            windows = {
                "V0_blame_max": after_set(pmax),
                "V1_blame_min": after_set(pmin),
                "V2_note_updated": after_day(note_upd) if note_upd else after_set(pmax),
                "V3_para_date": after_day(rec["para_date"]) if rec["para_date"] else after_set(pmax),
            }
            if tag == "now":
                rec["_win"] = {k: sorted(h[:7] for h in w & INV) for k, w in windows.items()}
            for vname, win in windows.items():
                trig = {n: sorted(c & win, key=lambda h: commit_time[h]) for n, c in ch.items() if c & win}
                key = f"{vname}|{tag}"
                rec[key] = bool(trig) and in_scope
                rec[key + "|trig"] = {n: [h[:9] for h in v] for n, v in trig.items()}
        paras.append(rec)
timing["notes_eval_s"] = round(time.time() - t, 2)
timing["total_s"] = round(time.time() - T0, 2)

os.makedirs(OUT, exist_ok=True)
allnames = {n for r in paras for n in r["names_ever"]}
kinds = {}
for n in allnames:
    if n.startswith("file:"):
        kinds[n] = "file"
    elif n.startswith("--"):
        kinds[n] = "flag"
    elif n in def_changes or n in now_defined or n in ever_defined:
        kinds[n] = "def"
    else:
        kinds[n] = "tok"
json.dump(kinds, open(os.path.join(OUT, "name_kinds.json"), "w"), ensure_ascii=False)
json.dump({"now_defined": sorted(now_defined), "now_paths": sorted(now_paths), "now_tokens": sorted(now_tokens)}, open(os.path.join(OUT, "now_index.json"), "w"), ensure_ascii=False)
with open(os.path.join(OUT, "paragraphs.jsonl"), "w") as f:
    for r in paras:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
stats = {"measure_commit": M, "notes": len(notes), "timing": timing,
         "paragraphs_in_scope": sum(r["in_scope"] for r in paras),
         "paragraphs_in_scope_with_names_now": sum(r["in_scope"] and bool(r["names_now"]) for r in paras)}
for k in [k for k in paras[0] if k.startswith("V") and not k.endswith("|trig")]:
    stats["flagged|" + k] = sum(bool(r[k]) for r in paras)
json.dump(stats, open(os.path.join(OUT, "stats.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(stats, ensure_ascii=False, indent=1))
