#!/usr/bin/env python3
"""舊句偵測實驗(機制①):程式改了、筆記還在講舊東西的句子,推送時能不能機械列出來、會不會誤列一堆。

只算分數,不擋任何東西;不進 scripts/lumos、不接任何掛鉤。計劃:Projects/舊句偵測實驗_計劃。
零依賴(標準庫 + 同 repo 的 scripts/lumos 當模組借幾支純函式,確保 delguard / Check Y 是照原樣重放)。

用法(兩個 repo 都要是完整 clone,只讀):
  python3 old_sentence_exp.py run   --rtb <rtb clone> [--tc <工具鏈 clone>] [--out results.json]
  python3 old_sentence_exp.py time  --rtb <rtb clone> --tc <工具鏈 clone>
  python3 old_sentence_exp.py q6    --rtb <rtb clone> --tc <工具鏈 clone>
  python3 old_sentence_exp.py show  --out results.json --cand P5 [--repo tc]   # 列出某候選的命中明細
  python3 old_sentence_exp.py revisit --repo <repo> --vault <圖譜> --pairs <檔> --out <json>   # 舊句檢查兩週回頭量(P4r3)
"""
import argparse
import ast
import importlib.machinery
import importlib.util
import json
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
TC_ROOT = HERE.parents[3]
EXAM = HERE.parent / "rtb-2026-09-28.json"
RTB_VAULT = "docs/rtb-production-agent-demo-knowledge"
TC_VAULT = "docs/lumos-toolchain-knowledge"
RTB_TIP = "067f005"


def _load_lumos():
    p = str(TC_ROOT / "scripts" / "lumos")
    loader = importlib.machinery.SourceFileLoader("lumos_mod", p)
    spec = importlib.util.spec_from_loader("lumos_mod", loader)
    m = importlib.util.module_from_spec(spec)
    sys.modules["lumos_mod"] = m
    loader.exec_module(m)
    return m


LM = _load_lumos()

# ───────────────────────── git 讀取 ─────────────────────────


class Repo:
    """只讀:所有 git 都帶 -C;blob 用一支常駐 cat-file --batch 讀。"""

    def __init__(self, path, vault):
        self.path = str(path)
        self.vault = vault
        self._cat = None
        self._trees = {}
        self._blobs = {}

    def git(self, *args, binary=False, check=True):
        r = subprocess.run(["git", "-C", self.path, "-c", "core.quotePath=off", *args],
                           capture_output=True)
        if check and r.returncode not in (0, 1):
            raise RuntimeError(f"git {args[:3]} rc={r.returncode}: {r.stderr[:300]!r}")
        return r.stdout if binary else r.stdout.decode("utf-8", "replace")

    def blob(self, sha):
        if sha in self._blobs:
            return self._blobs[sha]
        if self._cat is None:
            self._cat = subprocess.Popen(["git", "-C", self.path, "cat-file", "--batch"],
                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self._cat.stdin.write((sha + "\n").encode())
        self._cat.stdin.flush()
        hdr = self._cat.stdout.readline().decode().split()
        size = int(hdr[2])
        data = self._cat.stdout.read(size)
        self._cat.stdout.read(1)
        txt = data.decode("utf-8", "replace")
        self._blobs[sha] = txt
        return txt

    def tree(self, commit):
        if commit in self._trees:
            return self._trees[commit]
        out = self.git("ls-tree", "-r", "-z", "--full-tree", commit, binary=True)
        t = {}
        for rec in out.split(b"\0"):
            if not rec:
                continue
            meta, path = rec.split(b"\t", 1)
            parts = meta.split()
            if parts[1] != b"blob":
                continue
            t[path.decode("utf-8", "replace")] = parts[2].decode()
        self._trees[commit] = t
        return t

    def parent(self, commit):
        return self.git("rev-parse", commit + "^").strip()

    def full(self, commit):
        return self.git("rev-parse", commit).strip()

    def close(self):
        if self._cat:
            self._cat.stdin.close()
            self._cat.wait()
            self._cat = None


# ───────────────────────── 程式檔與符號抽取 ─────────────────────────

PROSE_DIRS = ("docs/", "governance/")   # 同 delguard:散文與帳本不算活著的程式
SKIP_SEG = tuple(d for d in LM._DELGUARD_EXCLUDE_DIRS)
TEXT_EXTS = {".py", ".sh", ".ps1", ".js", ".ts", ".json", ".toml", ".yml", ".yaml", ".cfg", ".ini",
             ".txt", ".kt", ".java", ".cs", ".swift", ".dart", ".go", ".rs", ".vue", ".sql"}
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
FLAG_RE = re.compile(r"(?<![A-Za-z0-9_-])--[a-z][a-z0-9-]{2,}(?![A-Za-z0-9_-])")


def _excluded(path):
    return (path.startswith(PROSE_DIRS) or any(path.startswith(s) or ("/" + s) in path for s in SKIP_SEG)
            or path.endswith(LM._DELGUARD_EXCLUDE_LOCKFILES))


class Code:
    """每個 blob 只剖一次(依 blob 雜湊快取),跨提交共用。"""

    def __init__(self, repo):
        self.repo = repo
        self._py = {}
        self._kind = {}
        self._raw = {}
        self._words = {}
        self.stats = {"parse_fail": set(), "cond_only": 0}

    def kind(self, path, sha):
        """'py' | 'other' | None(不是程式)。無副檔名看 shebang。"""
        key = (path, sha)
        if key in self._kind:
            return self._kind[key]
        k = None
        if not _excluded(path) and not path.endswith(".md"):
            ext = os.path.splitext(path)[1].lower()
            if ext == ".py":
                k = "py"
            elif ext == "":
                head = self.repo.blob(sha)[:120]
                if head.startswith("#!"):
                    k = "py" if "python" in head.split("\n", 1)[0] else "other"
            elif ext in TEXT_EXTS:
                k = "other"
        self._kind[key] = k
        return k

    def py(self, sha):
        """回 dict 或 None(剖不動)。defs=ast.walk 抓到的 def/class + 模組層/類別層指派名;
        consts=模組層大寫常數→正規化值;flags=add_argument 的 --旗標;idents=程式裡出現過的所有識別字
        (名稱、屬性、參數、字串內容切詞)——給「終點存不存在」用。"""
        if sha in self._py:
            return self._py[sha]
        src = self.repo.blob(sha)
        try:
            tree = ast.parse(src)
        except (SyntaxError, ValueError, RecursionError):
            self._py[sha] = None
            self.stats["parse_fail"].add(sha)
            return None
        defs, top, consts, flags, idents, strs = set(), set(), {}, set(), set(), set()
        for node in ast.walk(tree):
            _scan_ident(node, defs, idents, strs)
            if isinstance(node, ast.Call):
                _scan_add_argument(node, flags)
        _collect_assigns(tree.body, True, defs, top, consts)
        # 只在條件式/巢狀位置定義的 def(r1 邊界 F8 問的盲點):頂層與類別內抽法會漏掉的量
        info = {"defs": defs, "top": top, "consts": consts, "flags": flags,
                "idents": idents, "strflags": strs}
        self._py[sha] = info
        return info

    def words(self, sha):
        """[A-Za-z0-9_]+ 連續段集合;前 8000 字元有 NUL 視為二進位(同 git grep -I)回 None。"""
        if sha not in self._words:
            txt = self.repo.blob(sha)
            self._words[sha] = None if "\0" in txt[:8000] else set(re.findall(r"[A-Za-z0-9_]+", txt))
        return self._words[sha]

    def raw_tokens(self, sha):
        if sha not in self._raw:
            txt = self.repo.blob(sha)
            if len(txt) > 3_000_000:
                txt = txt[:3_000_000]
            self._raw[sha] = (set(IDENT_RE.findall(txt)), set(FLAG_RE.findall(txt)))
        return self._raw[sha]


def _scan_ident(node, defs, idents, strs):
    """一個 AST 節點對 defs / idents / strs 的貢獻(py() 的逐節點部分)。"""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        defs.add(node.name)
        idents.add(node.name)
    elif isinstance(node, (ast.Name, ast.Attribute, ast.arg, ast.keyword)):
        v = getattr(node, "id", None) or getattr(node, "attr", None) or getattr(node, "arg", None)
        if v:
            idents.add(v)
    elif isinstance(node, ast.alias):
        idents.update(IDENT_RE.findall(node.name))
        if node.asname:
            idents.add(node.asname)
    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
        s = node.value
        idents.update(IDENT_RE.findall(s))
        strs.update(FLAG_RE.findall(s))
        if s.startswith("--"):
            strs.add(s.split("=")[0])


def _scan_add_argument(node, flags):
    f = node.func
    fname = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
    if fname == "add_argument":
        for a in node.args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value.startswith("--"):
                flags.add(a.value)


_DEF_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _assign_pairs(st):
    if isinstance(st, ast.Assign):
        return list(st.targets), st.value
    if isinstance(st, ast.AnnAssign):
        return [st.target], st.value
    return [], None


def _target_names(t):
    return [t] if isinstance(t, ast.Name) else [e for e in getattr(t, "elts", []) if isinstance(e, ast.Name)]


def _sub_blocks(st):
    if isinstance(st, ast.If):
        return [st.body, st.orelse]
    if isinstance(st, ast.Try):
        return [st.body, st.orelse] + [h.body for h in st.handlers] + [st.finalbody]
    return []


def _record_targets(tgts, val, module, defs, consts):
    for t in tgts:
        for n in _target_names(t):
            defs.add(n.id)
            if module and n.id.isupper() and val is not None:
                consts[n.id] = _norm_const(val)


def _collect_assigns(body, module, defs, top, consts):
    for st in body:
        tgts, val = _assign_pairs(st)
        _record_targets(tgts, val, module, defs, consts)
        if isinstance(st, _DEF_NODES) and module:
            top.add(st.name)
        if isinstance(st, ast.ClassDef):
            top.update(s2.name for s2 in st.body if isinstance(s2, _DEF_NODES))
            _collect_assigns(st.body, False, defs, top, consts)
        if module:
            for blk in _sub_blocks(st):
                _collect_assigns(blk, True, defs, top, consts)


def _norm_const(v):
    """常數值:字面量正規化字串;清單/tuple 另記長度;運算式標 expr(r1 邊界 F7)。"""
    try:
        lit = ast.literal_eval(v)
        n = len(lit) if isinstance(lit, (list, tuple, set, frozenset, dict)) else None
        return ("lit", repr(lit), n)
    except Exception:
        n = len(v.elts) if isinstance(v, (ast.Tuple, ast.List, ast.Set)) else None
        return ("expr", ast.unparse(v) if hasattr(ast, "unparse") else "", n)


# ───────────────────────── 筆記解析 ─────────────────────────

RETIRE_WORDS = ("撤除", "撤掉", "作廢", "已失效", "已過時", "不是現況", "被取代", "已凍結", "superseded",
                "已結案", "歷史紀錄", "Superseded")
NOT_YET = re.compile(r"(尚未|還沒|未)(撤除|撤掉|作廢|失效|取代|凍結|結案)")
# P4r3(舊句檢查計劃設計審 r1 收窄):節中引用區塊撤除行要同一行還有範圍宣告字,才從那行到節尾不看
SCOPE_WORDS = ("下面", "以下", "本節", "這一節", "整篇", "之後")
HIST_WORDS = (*LM.NEG_LEXICONS["zh"],
    "撤除", "撤掉", "拿掉", "原寫", "原本", "原先", "不再", "舊版", "舊的", "刪除", "刪掉", "取代", "搬到",
    "搬去", "改為", "改叫", "改成", "曾", "前身", "撤", "刪", "拔掉", "去掉", "不帶", "沒有")
HIST_WORDS2 = (*HIST_WORDS, "當時叫", "擴成", "改名為")
# 英文字眼要整字比(不然 test_..._stays_dead_... 這種測試名會因為含 dead 被當成歷史句豁免)
HIST_RX = re.compile("|".join(
    (r"(?<![A-Za-z0-9_])" + re.escape(w) + r"(?![A-Za-z0-9_])") if w.isascii() else re.escape(w)
    for w in sorted(set(HIST_WORDS), key=len, reverse=True)))
HIST_RX2 = re.compile("|".join(
    (r"(?<![A-Za-z0-9_])" + re.escape(w) + r"(?![A-Za-z0-9_])") if w.isascii() else re.escape(w)
    for w in sorted(set(HIST_WORDS2), key=len, reverse=True)))
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
TESTREF_RE = re.compile(r"\[test:([^\]]+)\]")
BACKTICK_SYM_RE = re.compile(r"^(?:--[a-z][a-z0-9-]+|[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*(?:\(\))?)$")


def _shape_ok(name):
    """r1 設計的形狀過濾:4 字以上、含底線或大小寫混合(旗標與路徑另計)。"""
    if name.startswith("--") or "/" in name or name.endswith(".py"):
        return True
    return len(name) >= 4 and ("_" in name or (any(c.isupper() for c in name) and any(c.islower() for c in name)))


def _is_banner(line):
    s = line.strip()
    if not s or s[0] not in ">(（":
        return False
    if NOT_YET.search(s):
        return False
    return any(w in s for w in RETIRE_WORDS)


class Note:
    def __init__(self, path, text):
        self.path = path
        self.lines = text.split("\n")
        try:
            self.regs = LM._notelines_regions(text)
        except Exception:
            self.regs = ["body"] * len(self.lines)
        self.vis = {i for i, _ in LM._visible_lines(self.lines)}
        self.about = self._about(text)
        self.type = self._type()
        n = len(self.lines)
        self.ret_bq_near = [False] * (n + 1)   # r1 字面:只認引用區塊、只算最近一個小標題
        self.ret_full = [False] * (n + 1)      # 加嚴版:引用區塊或括號行、子節繼承
        self.ret_full2 = [False] * (n + 1)     # P4r2:ret_full + 節內任一行獨立引用區塊含撤除字樣,從那行到節尾(含子節)
        self.ret_full3 = [False] * (n + 1)     # P4r3:同 P4r2,但那行引用區塊還要含範圍宣告字(SCOPE_WORDS)
        self._bq_mid = []                      # (行號, 所在節層級;0=第一個標題之前)
        stack = []   # [(level, bq_flag, full_flag)]
        i = 0
        while i < n:
            ln = self.lines[i]
            lno = i + 1
            if self.regs[i] == "body" and lno in self.vis:
                m = HEAD_RE.match(ln)
                if m:
                    lvl = len(m.group(1))
                    while stack and stack[-1][0] >= lvl:
                        stack.pop()
                    j = i + 1
                    while j < n and not self.lines[j].strip():
                        j += 1
                    first = self.lines[j] if j < n else ""
                    bq = first.lstrip().startswith(">") and _is_banner(first)
                    full = _is_banner(first)
                    stack.append((lvl, bq, full))
            if self.regs[i] == "body":
                self.ret_bq_near[lno] = bool(stack and stack[-1][1])
                self.ret_full[lno] = any(s[2] for s in stack)
            i += 1
        # P4r2:節中任意位置的引用區塊撤除行 → 該行到節尾(下一個同層或更高層標題之前)都不看
        self.ret_full2 = self._mid_retire(lambda ln: True)
        # P4r3:同上,但那一行還要有範圍宣告字(「golden 已凍結」這種描述動作的句子不算宣告)
        self.ret_full3 = self._mid_retire(lambda ln: any(w in ln for w in SCOPE_WORDS))
        # 標題行本身若落在仍有效的標記內不會發生(上面已把 l>=標題層級的標記移除)

    def _mid_retire(self, extra_ok):
        out = list(self.ret_full)
        lvl_now, marks = 0, []   # marks: [(起始行, 層級)]
        for i2, ln2 in enumerate(self.lines):
            lno2 = i2 + 1
            if self.regs[i2] != "body" or lno2 not in self.vis:
                continue
            m2 = HEAD_RE.match(ln2)
            if m2:
                lvl_now = len(m2.group(1))
                marks = [(a, lv) for a, lv in marks if lv < lvl_now]  # 同層或更高層的標題結束了它
                continue
            if ln2.lstrip().startswith(">") and _is_banner(ln2) and extra_ok(ln2):
                marks.append((lno2, lvl_now))
            if marks:
                out[lno2] = True
        return out

    def _about(self, text):
        fm, _ = LM.split_frontmatter(text)
        out, cur = [], False
        for ln in fm or []:
            m = LM.TOP_KEY_RE.match(ln)
            if m:
                cur = m.group(1) == "about_code"
                continue
            if cur:
                s = ln.strip()
                if s.startswith("- "):
                    out.append(s[2:].strip().strip('"').strip("'").strip("`"))
        return out

    def _type(self):
        for ln in self.lines[1:40]:
            if ln.startswith("type:"):
                return ln.split(":", 1)[1].strip()
            if ln.strip() == "---":
                break
        return ""

    def scan_lines(self):
        """要掃的行:正文、摘要、決策欄的散文;跳過圍欄內與其他開頭欄位。"""
        for i, ln in enumerate(self.lines):
            lno = i + 1
            if self.regs[i] in ("body", "summary", "decisions") and lno in self.vis:
                yield lno, ln


class Vault:
    def __init__(self, repo):
        self.repo = repo
        self._notes = {}

    def notes(self, commit):
        t = self.repo.tree(commit)
        pre = self.repo.vault + "/"
        out = {}
        for p, sha in t.items():
            if p.startswith(pre) and p.endswith(".md"):
                if sha not in self._notes:
                    self._notes[sha] = Note(p[len(pre):], self.repo.blob(sha))
                n = self._notes[sha]
                if n.path != p[len(pre):]:
                    n = Note(p[len(pre):], self.repo.blob(sha))
                out[p[len(pre):]] = n
        return out


def _clause_has_hist(line, pos, rx=None):
    """提到名稱的那一句(括號內就只看括號內;括號外把括號內容剝掉)裡有沒有歷史/撤除字眼。"""
    depth_open = []
    span = None
    for i, ch in enumerate(line):
        if ch in "(（":
            depth_open.append(i)
        elif ch in ")）" and depth_open:
            a = depth_open.pop()
            if a < pos < i and (span is None or a > span[0]):
                span = (a, i)
    if span is None and depth_open and depth_open[-1] < pos:
        span = (depth_open[-1], len(line))
    if span is not None:
        seg = line[span[0] + 1:span[1]]
        rel = pos - span[0] - 1
    else:
        seg = re.sub(r"[(（][^()（）]*[)）]", lambda m: "\0" * len(m.group(0)), line)
        rel = pos
    cuts = [m.end() for m in re.finditer(r"[。;；!?！？]", seg) if m.end() <= rel]
    a = cuts[-1] if cuts else 0
    m2 = re.search(r"[。;；!?！？]", seg[rel:])
    b = rel + m2.start() if m2 else len(seg)
    clause = seg[a:b]
    return bool((rx or HIST_RX).search(clause))


# ───────────────────────── 一次推送範圍的共用材料 ─────────────────────────


class Push:
    """一個推送範圍(base..tip)的共用材料,各候選懶載入。"""

    def __init__(self, ctx, base, tip):
        self.ctx, self.base, self.tip = ctx, base, tip
        self.repo = ctx.repo
        self._m = {}

    def memo(self, k, fn):
        if k not in self._m:
            self._m[k] = fn()
        return self._m[k]

    # 改到的檔
    def changes(self, renames):
        def f():
            args = ["diff", "--name-status", "-z", "--no-ext-diff"] + (["-M"] if renames else ["--no-renames"]) + [self.base, self.tip]
            out = self.repo.git(*args, binary=True).decode("utf-8", "replace").split("\0")
            res, i = [], 0
            while i < len(out) and out[i]:
                st = out[i]
                if st[0] in "RC":
                    res.append((st[0], out[i + 1], out[i + 2]))
                    i += 3
                else:
                    res.append((st[0], out[i + 1], out[i + 1]))
                    i += 2
            return res
        return self.memo(("chg", renames), f)

    def code_changes(self, renames):
        """[(status, 起點路徑, 終點路徑, kind)] 只收程式檔。"""
        def f():
            bt, tt = self.repo.tree(self.base), self.repo.tree(self.tip)
            res = []
            for st, a, b in self.changes(renames):
                sha = tt.get(b) or bt.get(a)
                path = b if b in tt else a
                k = self.ctx.code.kind(path, sha) if sha else None
                if k:
                    res.append((st, a, b, k))
            return res
        return self.memo(("cchg", renames), f)

    def tip_notes(self):
        return self.memo("tipn", lambda: self.ctx.vault.notes(self.tip))

    def base_notes(self):
        return self.memo("basen", lambda: self.ctx.vault.notes(self.base))

    def new_lines(self):
        """這次範圍裡新寫或改過的筆記行 {筆記相對路徑: set(終點行號)}(-M 認改名)。"""
        def f():
            raw = self.repo.git("diff", "--no-ext-diff", "-U0", "-M", "--no-color", self.base, self.tip,
                                "--", self.repo.vault, binary=True)
            added = LM._notelines_parse_added(raw)
            pre = self.repo.vault + "/"
            return {p[len(pre):]: {n for n, _ in v} for p, v in added.items() if p.startswith(pre)}
        return self.memo("newl", f)

    def defs_of(self, commit, path):
        sha = self.repo.tree(commit).get(path)
        if not sha:
            return set(), True
        info = self.ctx.code.py(sha)
        if info is None:
            return None, False
        return info["defs"] | info["flags"], True

    def tip_all_defs(self):
        def f():
            s = set()
            for p, sha in self.repo.tree(self.tip).items():
                if self.ctx.code.kind(p, sha) == "py":
                    info = self.ctx.code.py(sha)
                    if info:
                        s |= info["defs"] | info["flags"]
            return s
        return self.memo("tipdefs", f)

    def tip_haystack(self):
        """終點「程式裡找得到」的識別字、旗標、路徑:py 用 ast(連字串內容),其他非散文文字檔用切詞。"""
        def f():
            ids, flags, paths, bases = set(), set(), set(), set()
            for p, sha in self.repo.tree(self.tip).items():
                paths.add(p)
                bases.add(p.rsplit("/", 1)[-1])
                k = self.ctx.code.kind(p, sha)
                if k == "py":
                    info = self.ctx.code.py(sha)
                    if info:
                        ids |= info["idents"] | info["defs"]
                        flags |= info["flags"] | info["strflags"]
                        continue
                if k or (not _excluded(p) and os.path.splitext(p)[1].lower() in TEXT_EXTS):
                    a, b = self.ctx.code.raw_tokens(sha)
                    ids |= a
                    flags |= b
            return ids, flags, paths, bases
        return self.memo("hay", f)

    def _added_elsewhere(self, py_chg):
        out = set()
        for st, a, b, _k in py_chg:
            tdefs, _ok = self.defs_of(self.tip, b)
            bdefs, _ok = self.defs_of(self.base, a) if st != "A" else (set(), True)
            if tdefs is not None and bdefs is not None:
                out |= (tdefs - bdefs)
        return out

    @staticmethod
    def _still_alive(n, mode, tipdefs, hay, added_elsewhere):
        if mode in ("repo", "loose") and n in tipdefs:
            return True
        if mode == "loose" and (n in hay[0] or n in hay[1]):
            return True
        return mode == "move" and n in added_elsewhere

    def _gone_defs(self, mode, py_chg):
        gone, unparsable = {}, []
        added_elsewhere = self._added_elsewhere(py_chg) if mode == "move" else set()
        tipdefs = self.tip_all_defs() if mode in ("repo", "loose") else None
        hay = self.tip_haystack() if mode == "loose" else None
        for st, a, b, _k in py_chg:
            if st == "A":
                continue
            bdefs, _ok = self.defs_of(self.base, a)
            tdefs, _ok = self.defs_of(self.tip, b) if st != "D" else (set(), True)
            if bdefs is None or tdefs is None:
                unparsable.append(a)
                continue
            for n in bdefs - tdefs:
                if not self._still_alive(n, mode, tipdefs, hay, added_elsewhere):
                    gone.setdefault(n, set()).add(a)
        return gone, unparsable

    def _gone_paths(self, mode, chg, gone):
        """被刪或改名的舊路徑(改名配對模式下,-M 認到的改名不算消失)。"""
        tt = self.repo.tree(self.tip)
        tip_bases = {p.rsplit("/", 1)[-1] for p in tt}
        for st, a, _b, _k in chg:
            if st == "D" or (st == "R" and mode != "move"):
                gone.setdefault(a, set()).add(a)
                bn = a.rsplit("/", 1)[-1]
                if bn not in tip_bases:
                    gone.setdefault(bn, set()).add(a)

    def disappeared(self, mode, shape=True):
        """消失的名稱 → 起點原本所在的檔(集合)。mode: file | repo | move | loose
        (loose=全 repo 比之外,終點程式裡任何地方(識別字、字串內容、其他程式檔)還出現這個名稱就不算消失)。
        剖不動的那一版:整支檔不算(不能當成全部消失),記在 unparsable。"""
        def f():
            chg = self.code_changes(mode == "move")
            py_chg = [c for c in chg if c[3] == "py"]
            gone, unparsable = self._gone_defs(mode, py_chg)
            self._gone_paths(mode, chg, gone)
            if shape:
                gone = {n: v for n, v in gone.items() if _shape_ok(n)}
            return gone, unparsable
        return self.memo(("gone", mode) if shape else ("gone", mode, "noshape"), f)

    def changed_consts(self):
        def f():
            out = {}
            for st, a, b, k in self.code_changes(True):
                if k != "py" or st in "AD":
                    continue
                bs, ts = self.repo.tree(self.base).get(a), self.repo.tree(self.tip).get(b)
                bi, ti = self.ctx.code.py(bs), self.ctx.code.py(ts)
                if not bi or not ti:
                    continue
                for n, v in bi["consts"].items():
                    if n in ti["consts"] and ti["consts"][n] != v:
                        out.setdefault(n, set()).add(a)
            return out
        return self.memo("consts", f)

    def homes_any(self):
        """家(讀法甲):範圍裡任何一支改到的程式檔,起點或終點樹上 about_code 列了它的筆記。"""
        def f():
            paths = set()
            for _st, a, b, _k in self.code_changes(True):
                paths.add(a)
                paths.add(b)
            out = set()
            for nm in (self.tip_notes(), self.base_notes()):
                for rel, n in nm.items():
                    if paths & set(n.about):
                        out.add(rel)
            return out
        return self.memo("homeany", f)

    def homes_of(self, files):
        """家(讀法乙):這些起點檔的家——起點樹與終點樹的 about_code 都算(改名後終點已換新路徑也認)。"""
        key = ("homeof", frozenset(files))

        def f():
            fs = set(files)
            for _st, a, b, _k in self.code_changes(True):
                if a in fs:
                    fs.add(b)
            out = set()
            for nm in (self.tip_notes(), self.base_notes()):
                for rel, n in nm.items():
                    if fs & set(n.about):
                        out.add(rel)
            return out
        return self.memo(key, f)


class FormalCode(Code):
    """程式檔判定改成跟正式工具(舊句檢查 m1)同一套:排除清單同 _excluded、Python 用 _drift_probe_is_py、
    其他程式檔用 _nodehome_code_kind(副檔名清單 _NODEHOME_CODE_EXTS、大小寫敏感)或沒副檔名的 #!。
    只給 revisit 用(舊句檢查計劃設計審 r3 外家否決席:回頭量的母體要跟正式工具一樣);run 的 P4r、P4r2、P4r3 仍用 Code。"""

    def kind(self, path, sha):
        key = (path, sha)
        if key in self._kind:
            return self._kind[key]
        k = None
        if not _excluded(path) and not path.endswith(".md"):
            ck = LM._nodehome_code_kind(path)
            if path.endswith(".py"):
                k = "py"
            elif ck == "shebang?":
                head = self.repo.blob(sha)[:200]
                if LM._drift_probe_is_py(path, head):
                    k = "py"
                elif head.startswith("#!"):
                    k = "other"
            elif ck == "ext":
                k = "other"
        self._kind[key] = k
        return k


class Ctx:
    def __init__(self, repo_path, vault, formal=False):
        self.repo = Repo(repo_path, vault)
        self.code = (FormalCode if formal else Code)(self.repo)
        self.vault = Vault(self.repo)
        self._hist = None

    def history_defs(self):
        """全歷史 py 定義索引(每個歷史 blob 剖一次)——r1 想用 git log -G 做的「曾經定義過」的便宜替代。"""
        if self._hist is None:
            out = self.repo.git("rev-list", "--objects", "--all")
            s = set()
            for ln in out.splitlines():
                parts = ln.split(" ", 1)
                if len(parts) == 2 and (parts[1].endswith(".py") or parts[1] == "scripts/lumos") and not _excluded(parts[1]):
                    info = self.code.py(parts[0])
                    if info:
                        s |= info["defs"] | info["flags"]
            self._hist = s
        return self._hist


# ───────────────────────── 候選判法 ─────────────────────────


def _mk_rx(names):
    ids = sorted((n for n in names if not n.startswith("--") and "/" not in n and "." not in n), key=len, reverse=True)
    others = sorted((n for n in names if n not in set(ids)), key=len, reverse=True)
    parts = []
    if ids:
        parts.append(r"(?<![A-Za-z0-9_])(?:" + "|".join(map(re.escape, ids)) + r")(?![A-Za-z0-9_])")
    if others:
        parts.append(r"(?<![A-Za-z0-9_/.-])(?:" + "|".join(map(re.escape, others)) + r")(?![A-Za-z0-9_-])")
    return re.compile("|".join(parts)) if parts else None


def cand_P(push, spec):
    """P 家族:規格欄位
       dis: file|repo|move        消失怎麼判
       newlines: skip|keep        這次新寫/改過的行跳不跳
       retire: bq_near|full       撤除節怎麼認(r1 字面 vs 括號行+子節繼承)
       clause: bool               提到名稱的那一句有撤除/歷史字眼就不列
       home: any|origin|none      「家」怎麼算(none=全部算要處理)
       ghost: None|test|all|all_hist  新寫的行提到終點找不到的名稱也列
    回 [(筆記, 行號, 層, 觸發名)]"""
    pc = _PCtx(push, spec)
    hits = {}
    _p_name_hits(pc, hits)
    if spec.get("ghost"):
        _p_ghost_hits(pc, hits)
    return [(r, ln, lay, toks) for (r, ln), (lay, toks) in hits.items()]


class _PCtx:
    """cand_P 一次判定共用的狀態:推送、規格、終點筆記、消失名稱、家(讀法甲)、新寫的行。"""

    def __init__(self, push, spec):
        self.push = push
        self.spec = spec
        self.notes = push.tip_notes()
        self.gone, _unp = push.disappeared(spec["dis"], spec.get("shape", True))
        self.newl = push.new_lines() if spec["newlines"] == "skip" or spec.get("ghost") else {}
        self.rx = _mk_rx(self.gone.keys())
        self.home_any = push.homes_any() if spec["home"] in ("any", "origin", "origin_fb") else set()

    def layer(self, rel, lno, toks, ghost=False):
        spec = self.spec
        n = self.notes[rel]
        if spec["home"] == "none":
            return "handle"
        if n.regs[lno - 1] == "summary":
            return "handle"
        if spec["home"] == "any" or ghost:
            return "handle" if rel in self.home_any else "list"
        origins = set()
        for t in toks:
            origins |= self.gone.get(t, set())
        if rel in self.push.homes_of(origins):
            return "handle"
        if spec["home"] == "origin_fb":
            # 消失名稱原本那支檔沒有任何家(常見:測試檔)時,退回讀法甲
            homeless = {o for o in origins if not self.push.homes_of({o})}
            if homeless and rel in self.home_any:
                return "handle"
        return "list"

    def retired(self, n, lno):
        return {"full": n.ret_full, "full2": n.ret_full2, "full3": n.ret_full3}.get(self.spec["retire"], n.ret_bq_near)[lno]

    def hist_skip(self, ln, pos):
        return self.spec["clause"] and _clause_has_hist(ln, pos)


def _p_name_hits(pc, hits):
    spec = pc.spec
    if not pc.rx:
        return
    for rel, n in pc.notes.items():
        nl = pc.newl.get(rel, set()) if spec["newlines"] == "skip" else set()
        for lno, ln in n.scan_lines():
            if lno in nl or pc.retired(n, lno):
                continue
            toks = []
            for m in pc.rx.finditer(ln):
                if spec["clause"] and _clause_has_hist(ln, m.start(), HIST_RX2 if spec.get("hist2") else None):
                    continue
                toks.append(m.group(0))
            if toks:
                hits[(rel, lno)] = (pc.layer(rel, lno, toks), sorted(set(toks)))


def _ghost_tests(pc, ln, tipdefs):
    """新寫的行裡 [test:名] 在終點找不到的名稱。"""
    out = []
    for m in TESTREF_RE.finditer(ln):
        for nm in re.split(r"[,、\s]+", m.group(1)):
            nm = nm.strip()
            if IDENT_RE.fullmatch(nm or "-") and nm not in tipdefs and not pc.hist_skip(ln, m.start()):
                out.append(nm)
    return out


def _ghost_inline(pc, ln, m, tip_hay):
    """一個反引號片段:終點找不到就回名稱,否則 None。"""
    ids, flags, paths, bases = tip_hay
    s = m.group(0).strip("`").strip()
    if s.endswith(".py"):
        if s not in paths and s.rsplit("/", 1)[-1] not in bases and not pc.hist_skip(ln, m.start()):
            return s
        return None
    if not BACKTICK_SYM_RE.match(s):
        return None
    s2 = s[:-2] if s.endswith("()") else s
    if s2.startswith("--"):
        ok = s2 in flags
    else:
        last = s2.split(".")[-1]
        if not _shape_ok(last):
            return None
        ok = last in ids
    if ok or pc.hist_skip(ln, m.start()):
        return None
    return s2 if s2.startswith("--") else s2.split(".")[-1]


def _ghost_all(pc, ln, tip_hay):
    out = []
    for m in LM.INLINE_CODE_RE.finditer(ln):
        g = _ghost_inline(pc, ln, m, tip_hay)
        if g is not None:
            out.append(g)
    flags = tip_hay[1]
    for m in FLAG_RE.finditer(ln):
        if m.group(0) not in flags and not pc.hist_skip(ln, m.start()):
            out.append(m.group(0))
    return out


def _p_ghost_hits(pc, hits):
    g = pc.spec["ghost"]
    tip_hay = pc.push.tip_haystack()
    tipdefs = pc.push.tip_all_defs()
    hist = pc.push.ctx.history_defs() if g == "all_hist" else None
    for rel, lnos in pc.newl.items():
        n = pc.notes.get(rel)
        if n is None:
            continue
        for lno in sorted(lnos):
            if lno > len(n.lines) or n.regs[lno - 1] not in ("body", "summary", "decisions") or lno not in n.vis:
                continue
            if pc.retired(n, lno):
                continue
            ln = n.lines[lno - 1]
            ghosts = _ghost_tests(pc, ln, tipdefs)
            if g in ("all", "all_hist"):
                ghosts += _ghost_all(pc, ln, tip_hay)
            if hist is not None:
                ghosts = [x for x in ghosts if x in hist]
            if ghosts:
                prev = hits.get((rel, lno))
                lay = pc.layer(rel, lno, [], ghost=True)
                toks = sorted(set(ghosts) | set(prev[1] if prev else []))
                if prev and prev[0] == "handle":
                    lay = "handle"
                hits[(rel, lno)] = (lay, toks)


WAKE_WORDS = ("尚未", "還沒", "目前沒有", "沒有正式", "屬後續", "未定義", "待補", "未實作", "還不存在", "尚無")


def cand_W(push, spec):
    """新增程式檔喚醒「還沒有」句:新增檔的家(終點樹)裡含否定未來字眼的行,只列不擋。"""
    notes = push.tip_notes()
    added = [b for st, a, b, _k in push.code_changes(True) if st == "A"]
    if not added:
        return []
    out = []
    for rel, n in notes.items():
        if set(added) & set(n.about):
            for lno, ln in n.scan_lines():
                if any(w in ln for w in WAKE_WORDS) and not n.ret_full[lno]:
                    out.append((rel, lno, "list", ["<新增檔>"]))
    return out


# ───── W2 家族(新增名稱否定句;Projects/新增名稱否定句檢查_計劃):m1 的反方向 ─────
# 推送範圍裡「起點沒有、終點新定義」的名稱(同 m1 的三類:def/class/指派、add_argument 旗標、程式檔路徑與檔名,
# 同一個形狀過濾),筆記裡同一句同時出現該名稱與否定字眼的行。只量、不擋;不動 P 家族任何一支。
NEG_ZH_W2 = ("沒有", "還沒", "尚未", "未", "不存在", "缺", "待補", "尚無")
NEG_EN_W2 = ("not yet", "missing", "no", "lack", "lacks", "absent", "TODO", "TBD", "does not exist",
             "doesn't exist", "not exist")
NEG_RX_W2 = re.compile("|".join(
    [re.escape(w) for w in sorted(NEG_ZH_W2, key=len, reverse=True)]
    + [r"(?i:(?<![A-Za-z0-9_])" + re.escape(w) + r"(?![A-Za-z0-9_]))" for w in sorted(NEG_EN_W2, key=len, reverse=True)]))
# 句內歷史字眼(W2h):P4r2/P4r3 的 54 個字眼,去掉本身就是否定字眼或含否定字眼的(沒有、不存在、未使用、從未…)
HIST_W2 = tuple(w for w in dict.fromkeys(HIST_WORDS2)
                if not any(z in w for z in NEG_ZH_W2) and w.lower() not in {e.lower() for e in NEG_EN_W2})
HIST_RX_W2 = re.compile("|".join(
    (r"(?<![A-Za-z0-9_])" + re.escape(w) + r"(?![A-Za-z0-9_])") if w.isascii() else re.escape(w)
    for w in sorted(HIST_W2, key=len, reverse=True)))


def _w2_clause(line, pos):
    """同 _clause_has_hist 的「那一句」切法(括號內只看括號內、括號外先遮掉不含括號的括號對、再用句號分號切),
    回 (那一句的文字, 那一句在 line 裡的起點)。遮掉的括號內容換成 \\0、長度不變,所以位置對得上。"""
    depth_open = []
    span = None
    for i, ch in enumerate(line):
        if ch in "(（":
            depth_open.append(i)
        elif ch in ")）" and depth_open:
            a = depth_open.pop()
            if a < pos < i and (span is None or a > span[0]):
                span = (a, i)
    if span is None and depth_open and depth_open[-1] < pos:
        span = (depth_open[-1], len(line))
    if span is not None:
        seg, off = line[span[0] + 1:span[1]], span[0] + 1
    else:
        seg, off = re.sub(r"[(（][^()（）]*[)）]", lambda m: "\0" * len(m.group(0)), line), 0
    rel = pos - off
    cuts = [m.end() for m in re.finditer(r"[。;；!?！？]", seg) if m.end() <= rel]
    a = cuts[-1] if cuts else 0
    m2 = re.search(r"[。;；!?！？]", seg[rel:])
    b = rel + m2.start() if m2 else len(seg)
    return seg[a:b], off + a


def _w2_neg_ok(line, m, near):
    """名稱 m 所在那一句有沒有否定字眼(不算名稱本身那一段);near 是整數時,否定字眼要在名稱前後 near 字內。"""
    clause, c0 = _w2_clause(line, m.start())
    ns, ne = m.start() - c0, m.end() - c0
    for g in NEG_RX_W2.finditer(clause):
        if g.start() < ne and g.end() > ns:
            continue
        if near is None or max(0, g.start() - ne, ns - g.end()) <= near:
            return True
    return False


def _w2_hist(line, m):
    clause, c0 = _w2_clause(line, m.start())
    ns, ne = m.start() - c0, m.end() - c0
    return any(not (g.start() < ne and g.end() > ns) for g in HIST_RX_W2.finditer(clause))


def _w2_base_defs(push):
    """起點樹所有 Python 檔的定義與旗標聯集(tip_all_defs 的起點版;m1 判消失用終點語料,W2 判新增用起點語料)。"""
    def f():
        s = set()
        for p, sha in push.repo.tree(push.base).items():
            if push.ctx.code.kind(p, sha) == "py":
                info = push.ctx.code.py(sha)
                if info:
                    s |= info["defs"] | info["flags"]
        return s
    return push.memo("w2basedefs", f)


def _w2_new_paths(push, chg, new):
    """這次新增的程式檔路徑;檔名只有起點樹任何位置都沒有同名檔才算新增(m1 _gone_paths 的反方向)。"""
    base_bases = {p.rsplit("/", 1)[-1] for p in push.repo.tree(push.base)}
    for st, _a, b, _k in chg:
        if st == "A":
            new.setdefault(b, set()).add(b)
            bn = b.rsplit("/", 1)[-1]
            if bn not in base_bases:
                new.setdefault(bn, set()).add(b)


def w2_appeared(push, shape=True):
    """新增的名稱 → 終點所在的檔(集合)。定義名與旗標:改到的 Python 檔終點那版有、起點那版沒有,而且起點語料
    所有 Python 檔都沒定義(從 a.py 搬到 b.py 不算);路徑:這次新增的程式檔(--no-renames,改名=刪+加)的路徑,
    檔名只有起點樹任何位置都沒有同名檔才算。剖不動的那一版整支不算。"""
    def f():
        chg = push.code_changes(False)
        new, unparsable = {}, []
        basedefs = None
        for st, a, b, k in chg:
            if k != "py" or st == "D":
                continue
            tdefs, _ok = push.defs_of(push.tip, b)
            bdefs, _ok = push.defs_of(push.base, a) if st != "A" else (set(), True)
            if tdefs is None or bdefs is None:
                unparsable.append(b)
                continue
            fresh = tdefs - bdefs
            if fresh:
                basedefs = basedefs if basedefs is not None else _w2_base_defs(push)
                for n in fresh - basedefs:
                    new.setdefault(n, set()).add(b)
        _w2_new_paths(push, chg, new)
        if shape:
            new = {n: v for n, v in new.items() if _shape_ok(n)}
        return new, unparsable
    return push.memo(("w2new", shape), f)


def cand_W2(push, spec):
    """W2 家族:spec 欄位 near(None=同一句;整數=否定字眼在名稱前後幾字內)、old(只看這次沒新寫也沒改過的行)、
    hist(那一句另有歷史字眼就不列)。撤除節照 P4r3(ret_full3);分層照 P4r3(任一改到程式檔的家或摘要=要處理)。"""
    new, _unp = w2_appeared(push, spec.get("shape", True))
    rx = _mk_rx(new.keys())
    if not rx:
        return []
    notes = push.tip_notes()
    newl = push.new_lines() if spec.get("old") else {}
    homes = push.homes_any()
    out = []
    for rel, n in notes.items():
        nl = newl.get(rel, set())
        for lno, ln in n.scan_lines():
            if n.ret_full3[lno] or lno in nl:
                continue
            toks = [m.group(0) for m in rx.finditer(ln)
                    if _w2_neg_ok(ln, m, spec.get("near")) and not (spec.get("hist") and _w2_hist(ln, m))]
            if toks:
                lay = "handle" if (n.regs[lno - 1] == "summary" or rel in homes) else "list"
                out.append((rel, lno, lay, sorted(set(toks))))
    return out


CJK_RUN_RE = re.compile(r"[一-鿿]{4,}")


def _cjk4(txt):
    out = set()
    for m in CJK_RUN_RE.finditer(txt):
        s = m.group(0)
        out.update(s[i:i + 4] for i in range(len(s) - 3))
    return out


def _w2z_base_grams(push):
    """起點樹所有程式檔(同 Code.kind 的範圍)出現過的中文四字片段聯集;依 blob 快取在 ctx 上。"""
    cache = push.ctx.__dict__.setdefault("_w2z_blob", {})

    def f():
        s = set()
        for p, sha in push.repo.tree(push.base).items():
            if push.ctx.code.kind(p, sha):
                if sha not in cache:
                    cache[sha] = _cjk4(push.repo.blob(sha))
                s |= cache[sha]
        return s
    return push.memo("w2zbase", f)


def w2z_new_grams(push):
    """這次改到的程式檔新增行裡的中文四字片段,起點樹任何程式檔都沒出現過的(新概念的中文說法,例:「比例上限」)。"""
    def f():
        paths = sorted({b for st, _a, b, _k in push.code_changes(False) if st != "D"})
        if not paths:
            return set()
        raw = push.repo.git("diff", "--no-ext-diff", "-U0", "--no-color", "--no-renames", push.base, push.tip,
                            "--", *paths)
        added = set()
        for ln in raw.splitlines():
            if ln.startswith("+") and not ln.startswith("+++"):
                added |= _cjk4(ln)
        return added - _w2z_base_grams(push) if added else set()
    return push.memo("w2znew", f)


def cand_W2z(push, spec):
    """探索用:名稱比對抓不到 A3/A7(句子裡沒有新名稱),試「新增程式的中文說法」對上否定句——
    改到的程式檔新增行(註解、docstring、字串)裡起點程式沒出現過的中文四字片段,在這次沒新寫的筆記行裡、
    跟否定字眼同一句而且在前後 near 字內。分層同 W2。"""
    grams = w2z_new_grams(push)
    if not grams:
        return []
    near = spec.get("near", 10)
    notes = push.tip_notes()
    newl = push.new_lines()
    homes = push.homes_any()
    out = []
    for rel, n in notes.items():
        nl = newl.get(rel, set())
        for lno, ln in n.scan_lines():
            if n.ret_full3[lno] or lno in nl or not NEG_RX_W2.search(ln):
                continue
            toks = set()
            for g in NEG_RX_W2.finditer(ln):
                clause, c0 = _w2_clause(ln, g.start())
                gs, ge = g.start() - c0, g.end() - c0
                win = clause[max(0, gs - near - 3):ge + near + 3]
                toks |= _cjk4(win) & grams
            if toks:
                lay = "handle" if (n.regs[lno - 1] == "summary" or rel in homes) else "list"
                out.append((rel, lno, lay, sorted(toks)))
    return out


def cand_V(push, spec):
    """改值的常數:家筆記(讀法乙)裡提到那個常數名的行,只列。"""
    notes = push.tip_notes()
    ch = push.changed_consts()
    ch = {k: v for k, v in ch.items() if _shape_ok(k)}
    rx = _mk_rx(ch.keys())
    if not rx:
        return []
    out = []
    for rel, n in notes.items():
        for lno, ln in n.scan_lines():
            toks = sorted({m.group(0) for m in rx.finditer(ln)})
            if toks:
                origins = set().union(*(ch[t] for t in toks))
                lay = "handle" if rel in push.homes_of(origins) else "list"
                out.append((rel, lno, lay, toks))
    return out


def _dg_alive_gitgrep(push, toks, rx):
    """原樣:git grep -w -F 多個 -e(delguard 的 _delguard_confidence 就是這樣下)。只在 time 量成本時用——
    不設上限時 b2fc512 有 1157 個 token,macOS 內建 git 跑超過 10 分鐘沒跑完。"""
    alive = set()
    cmd = ["grep", "-n", "-I", "-w", "-F"]
    for t in toks:
        cmd += ["-e", t]
    cmd += [push.tip, "--", ".", f":(exclude){push.repo.vault}"] + [f":(exclude){d.rstrip('/')}" for d in LM._DELGUARD_ALL_EXCLUDE_DIRS]
    out = push.repo.git(*cmd)
    for line in out.splitlines():
        parts = line.split(":", 3)
        if len(parts) < 4:
            continue
        alive.update(rx.findall(parts[3]))
    return alive


def _dg_alive_fast(push, toks):
    """同語意的快做法:t 在某檔「整字出現」(ASCII \\b)⟺ t 是那支檔 [A-Za-z0-9_]+ 連續段之一。
    排除範圍照 git grep 那行:圖譜、根目錄的 docs/ governance/ 與建置目錄;-I 跳過二進位檔。"""
    alive = set()
    excl = [push.repo.vault + "/"] + [d for d in LM._DELGUARD_ALL_EXCLUDE_DIRS]
    tokset = set(toks)
    for pth, sha in push.repo.tree(push.tip).items():
        if any(pth.startswith(e) for e in excl):
            continue
        words = push.ctx.code.words(sha)
        if words is None:
            continue
        alive |= tokset & words
    return alive


def cand_DG(push, spec):
    """delguard 原樣重放:抽法用 scripts/lumos 的 _delguard_parse_diff(同一支函式);信心=終點樹
    git grep 全域零命中為 high;掃整份圖譜每一行(不剝圍欄、不看撤除)。cap=40 是原樣,nocap 是加測。
    層:high→handle、low→list(delguard 本身只提醒,這裡借它的信心分兩層)。"""
    raw = push.repo.git("-c", "diff.noprefix=false", "-c", "diff.mnemonicPrefix=false", "diff", "--no-ext-diff",
                        "--no-textconv", "-M", "--no-color", push.base, push.tip)
    parsed = LM._delguard_parse_diff(raw, push.repo.vault)
    toks = parsed["tokens"] if spec.get("nocap") else parsed["tokens"][:LM.DELGUARD_TOKEN_CAP]
    if not toks:
        return []
    rx = re.compile(r"\b(?:" + "|".join(map(re.escape, sorted(toks, key=len, reverse=True))) + r")\b", re.ASCII)
    alive = _dg_alive_gitgrep(push, toks, rx) if spec.get("gitgrep") else _dg_alive_fast(push, toks)
    res = []
    for rel, n in push.tip_notes().items():
        for i, ln in enumerate(n.lines, 1):
            if not rx.search(ln):
                continue
            ts = sorted(set(rx.findall(ln)))
            hi = any(t not in alive for t in ts)
            res.append((rel, i, "handle" if hi else "list", ts))
    return res


def _checky_profile(repo, t):
    prof = dict(LM.SYMBOL_PROFILES["csharp"])
    neg = LM.NEG_LEXICONS["zh"]
    cfg = t.get(".lumos/config.json")
    if cfg:
        try:
            c = json.loads(repo.blob(cfg))
            if c.get("symbol_profile") in LM.SYMBOL_PROFILES:
                prof = dict(LM.SYMBOL_PROFILES[c["symbol_profile"]])
            if isinstance(c.get("neg_extra"), list):
                neg = tuple(neg) + tuple(c["neg_extra"])
        except Exception:
            pass
    return prof, neg


def _checky_shaper(prof):
    sym_re = re.compile(prof["shape_re"])
    ext_re = re.compile(r"\.(aspx|html|cs|js|vue|sql|ps1|yml|json|md|kt|py)$", re.I)
    sufs, dot_ok = tuple(prof.get("suffixes") or ()), prof.get("dotted_ok", True)

    def shaped(s):
        if "/" in s or " " in s or ext_re.search(s):
            return False
        if any(ch.isdigit() for ch in s) or s.isupper():
            return False
        if not sym_re.match(s):
            return False
        if sufs and any(s.endswith(x) for x in sufs):
            return True
        return dot_ok and "." in s
    return shaped


def _checky_hay(repo, t):
    parts = []
    for p, sha in t.items():
        segs = p.split("/")
        if any(sg in LM.CODE_SKIP_DIRS for sg in segs[:-1]):
            continue
        if os.path.splitext(p)[1].lower() in LM.CODE_EXTS_T:
            parts.append(repo.blob(sha))
    return "\n".join(parts)


def _checky_note(rel, n, shaped, neg, h, ghosts):
    seen = set()
    for lno, ln in LM._visible_lines(n.lines):
        isneg = any(k in ln for k in neg)
        for raw in LM.INLINE_CODE_RE.findall(ln):
            s = raw.strip("`").strip()
            if not shaped(s) or (rel, s) in seen:
                continue
            seen.add((rel, s))
            if not isneg and s.split(".")[-1] not in h:
                ghosts[(rel, s)] = lno


def _checky_tree(push, commit):
    """doctor Check Y 在某一棵樹上的原樣重放(只掃 Systems、行級否定豁免、substring 草堆)。回 {(筆記, 符號): 行號}。"""
    repo = push.repo
    t = repo.tree(commit)
    prof, neg = _checky_profile(repo, t)
    shaped = _checky_shaper(prof)
    h = push.memo(("cyhay", commit), lambda: _checky_hay(repo, t))
    notes = push.tip_notes() if commit == push.tip else push.base_notes()
    ghosts = {}
    for rel, n in sorted(notes.items()):
        if n.type == "system":
            _checky_note(rel, n, shaped, neg, h, ghosts)
    return ghosts


def cand_CY(push, spec):
    """Check Y 借來當推送閘:終點樹的幽靈符號減掉起點樹就有的(=這次推送新冒出來的)。"""
    tip = _checky_tree(push, push.tip)
    if spec.get("tip_only"):
        return [(r, ln, "handle", [s]) for (r, s), ln in tip.items()]
    base = _checky_tree(push, push.base)
    return [(r, ln, "handle", [s]) for (r, s), ln in tip.items() if (r, s) not in base]


BASE_P = dict(dis="file", newlines="skip", retire="bq_near", clause=False, home="any", ghost=None)
_K = dict(newlines="keep", retire="full", clause=True)
CANDS = {
    "DG": (cand_DG, {}, "delguard 原樣(抽 40 個被刪識別字、全圖譜每行掃;高信心=終點全 repo 零命中)"),
    "DGnc": (cand_DG, {"nocap": True}, "delguard 不設 40 個上限"),
    "DGgit": (cand_DG, {"gitgrep": True}, "delguard 原樣(信心那步真的下 git grep,只給 time 量成本)"),
    "CY": (cand_CY, {}, "doctor Check Y 差分(終點新冒出的幽靈符號)"),
    "P0": (cand_P, dict(BASE_P), "r1 設計字面:逐檔比、跳過新寫行、只認引用區塊撤除、家=任一改到檔"),
    "P1": (cand_P, dict(BASE_P, dis="repo"), "P0 改全 repo 比"),
    "P2": (cand_P, dict(BASE_P, dis="move"), "P0 改改名配對"),
    "P2L": (cand_P, dict(BASE_P, dis="loose"), "P0 改「終點程式裡哪裡都找不到才算消失」"),
    "P3": (cand_P, dict(BASE_P, dis="move", newlines="keep"), "P2 + 新寫的行也看"),
    "P3r": (cand_P, dict(BASE_P, dis="repo", newlines="keep"), "P1 + 新寫的行也看"),
    "P3L": (cand_P, dict(BASE_P, dis="loose", newlines="keep"), "P2L + 新寫的行也看"),
    "P4": (cand_P, dict(BASE_P, dis="move", **_K), "P3 + 括號撤除行/子節繼承 + 句內歷史字眼豁免"),
    "P4r": (cand_P, dict(BASE_P, dis="repo", **_K), "P3r + 撤除/歷史過濾"),
    "P4L": (cand_P, dict(BASE_P, dis="loose", **_K), "P3L + 撤除/歷史過濾"),
    "P4r2": (cand_P, dict(BASE_P, dis="repo", **dict(_K, retire="full2"), hist2=True), "P4r + 歷史字眼多 3 詞組 + 節中引用區塊撤除行到節尾不看"),
    "P4r3": (cand_P, dict(BASE_P, dis="repo", **dict(_K, retire="full3"), hist2=True), "P4r2,但節中引用區塊撤除行要同一行有範圍宣告字(舊句檢查計劃 r1 收窄;正式工具的驗收以它為準)"),
    "P4r3c": (cand_P, dict(BASE_P, dis="repo", **dict(_K, retire="full3", clause=False), hist2=True), "P4r3 關掉句內歷史字眼過濾(revisit 量漏報用)"),
    "P4r3s": (cand_P, dict(BASE_P, dis="repo", **dict(_K, retire="full3"), hist2=True, shape=False), "P4r3 拿掉形狀過濾(revisit 量漏報用)"),
    "P4r3r": (cand_P, dict(BASE_P, dis="repo", **_K, hist2=True), "P4r3 不看撤除節②(只留節開頭①;revisit 量②藏了哪些行用)"),
    "P4rb": (cand_P, dict(BASE_P, dis="repo", home="origin", **_K), "P4r,家=消失名稱原本那支檔的家(讀法乙)"),
    "P4rc": (cand_P, dict(BASE_P, dis="repo", home="origin_fb", **_K), "P4r,家=讀法乙;原本那支檔沒家時退回讀法甲"),
    "P4rn": (cand_P, dict(BASE_P, dis="repo", home="none", **_K), "P4r,不分層(全部算要處理)"),
    "P5": (cand_P, dict(BASE_P, dis="repo", ghost="test", **_K), "P4r + 新寫行的 [test:] 名在終點找不到也列"),
    "P6": (cand_P, dict(BASE_P, dis="repo", ghost="all", **_K), "P4r + 新寫行提到終點找不到的任何符號/旗標/路徑"),
    "P6h": (cand_P, dict(BASE_P, dis="repo", ghost="all_hist", **_K), "P6 但懸空名限「歷史上曾定義過」"),
    "W": (cand_W, {}, "新增程式檔喚醒家裡的「尚未/還沒」句(只列)"),
    "V": (cand_V, {}, "改值的常數:家裡提到常數名的行"),
    # W2 家族(新增名稱否定句檢查計劃的實驗;不進 run 的預設候選,要用 --cands 點名)
    "W2": (cand_W2, {}, "新增名稱 + 同一句有否定字眼"),
    "W2n": (cand_W2, {"near": 10}, "W2,否定字眼要在名稱前後 10 字內"),
    "W2o": (cand_W2, {"old": True}, "W2,只看這次沒新寫也沒改過的行"),
    "W2h": (cand_W2, {"hist": True}, "W2,那一句另有歷史字眼(原本、改成…)就不列"),
    "W2on": (cand_W2, {"old": True, "near": 10}, "W2o + W2n"),
    "W2onh": (cand_W2, {"old": True, "near": 10, "hist": True}, "W2o + W2n + W2h"),
    "W2z": (cand_W2z, {"near": 10}, "探索:新增程式行裡起點沒有的中文四字片段 + 舊行否定字眼 10 字內"),
}
_OPT_IN = {"DGgit"} | {k for k in CANDS if k.startswith("W2")}


def run_cand(ctx, name, base, tip, push=None):
    fn, spec, _d = CANDS[name]
    push = push or Push(ctx, base, tip)
    return fn(push, spec)


# ───────────────────────── 考卷與計分 ─────────────────────────


def load_exam():
    d = json.load(open(EXAM, encoding="utf-8"))
    m1 = [q for q in d if q.get("exam_event") == "mechanism1_experiment"]
    nd = [q for q in d if q["verdict"] != "drift"]
    return m1, nd


def locate(notes, q):
    n = notes.get(q["note"])
    if n is None:
        return None, set()
    key = q["text"][:60]
    return n, {i + 1 for i, ln in enumerate(n.lines) if key in ln}


def grade(hits, notes, q):
    _n, lnos = locate(notes, q)
    if not lnos:
        return "句子不在", []
    mine = [h for h in hits if h[0] == q["note"] and h[1] in lnos]
    if any(h[2] == "handle" for h in mine):
        return "擋到", sorted({t for h in mine for t in h[3]})
    if mine:
        return "只列", sorted({t for h in mine for t in h[3]})
    if any(h[0] == q["note"] for h in hits):
        return "點到", []
    return "漏", []


def stats(xs):
    if not xs:
        return {"n": 0}
    s = sorted(xs)
    return {"n": len(s), "mean": round(sum(s) / len(s), 2), "p50": s[len(s) // 2],
            "p90": s[min(len(s) - 1, int(len(s) * 0.9))], "max": s[-1], "nonzero": sum(1 for x in s if x)}


def _dump_rows(hits, notes):
    return [{"note": h[0], "line": h[1], "layer": h[2], "tokens": h[3], "text": notes[h[0]].lines[h[1] - 1][:220]} for h in hits]


def _run_exam(ctx, names, m1, res):
    """① 9 題"""
    for q in m1:
        c = q["invalidating_commits"][0]
        base = ctx.repo.parent(c)
        push = Push(ctx, base, c)
        notes = push.tip_notes()
        for nm in names:
            hits = run_cand(ctx, nm, base, c, push)
            st, toks = grade(hits, notes, q)
            res["exam"].setdefault(nm, {})[q["id"]] = {"status": st, "tokens": toks, "commit": c}
        print(f"exam {q['id']} done", file=sys.stderr)


def _rtb_code_commits(a, ctx):
    log = [] if a.skip_sweep else ctx.repo.git("log", "--no-merges", "--format=%H", RTB_TIP).split()
    commits = []
    for c in log:
        try:
            base = ctx.repo.parent(c)
        except Exception:
            continue
        p = Push(ctx, base, c)
        if any(k == "py" for *_x, k in p.code_changes(True)):
            commits.append(c)
    return commits[:a.limit] if a.limit else commits


def _rtb_one_commit(a, ctx, names, nd, res, c, per, ndhits):
    base = ctx.repo.parent(c)
    push = Push(ctx, base, c)
    notes = push.tip_notes()
    for nm in names:
        hits = run_cand(ctx, nm, base, c, push)
        hd = sum(1 for h in hits if h[2] == "handle")
        per[nm][c[:7]] = {"handle": hd, "list": len(hits) - hd}
        for q in nd:
            st, toks = grade(hits, notes, q)
            if st in ("擋到", "只列"):
                ndhits[nm][q["id"]].append({"commit": c[:7], "status": st, "tokens": toks})
        if a.dump and hits:
            res.setdefault("dumpall", {}).setdefault(nm, {})[c[:7]] = _dump_rows(hits, notes)
        if a.dump and c[:7] in ("b2fc512",):
            res.setdefault("dump", {}).setdefault(nm, {})[c[:7]] = _dump_rows(hits, notes)


def _run_rtb_sweep(a, ctx, names, nd, res):
    """② rtb 每個動到程式的提交(067f005 以前、非合併):噪音 + 13 題非漂移誤列"""
    commits = _rtb_code_commits(a, ctx)
    res["meta"]["rtb_commits"] = len(commits)
    per = {nm: {} for nm in names}
    ndhits = {nm: {q["id"]: [] for q in nd} for nm in names}
    t0 = time.time()
    for idx, c in enumerate(commits):
        _rtb_one_commit(a, ctx, names, nd, res, c, per, ndhits)
        if idx % 20 == 0:
            print(f"rtb {idx}/{len(commits)} {time.time() - t0:.0f}s", file=sys.stderr)
    res["meta"]["rtb_parse_fail_blobs"] = len(ctx.code.stats["parse_fail"])
    for nm in names:
        res["rtb"][nm] = {"per": per[nm],
                          "handle": stats([v["handle"] for v in per[nm].values()]),
                          "list": stats([v["list"] for v in per[nm].values()]),
                          "b2fc512": per[nm].get("b2fc512")}
        res["nd"][nm] = {k: v for k, v in ndhits[nm].items() if v}


def _run_tc(a, names, res):
    """③ 工具鏈最近 50 個提交"""
    tctx = Ctx(a.tc, TC_VAULT)
    tl = tctx.repo.git("log", "--format=%H", f"-{a.tc_n}", a.tc_head).split()
    res["meta"]["tc_commits"] = len(tl)
    tper = {nm: {} for nm in names}
    details = {nm: [] for nm in names}
    code_commits = 0
    for c in tl:
        base = tctx.repo.parent(c)
        push = Push(tctx, base, c)
        has_code = any(True for _ in push.code_changes(True))
        code_commits += has_code
        notes = push.tip_notes()
        subj = tctx.repo.git("log", "-1", "--format=%s", c).strip()
        for nm in names:
            hits = run_cand(tctx, nm, base, c, push)
            hd = sum(1 for h in hits if h[2] == "handle")
            tper[nm][c[:8]] = {"handle": hd, "list": len(hits) - hd, "code": has_code, "subject": subj}
            for h in hits:
                details[nm].append({"commit": c[:8], "note": h[0], "line": h[1], "layer": h[2], "tokens": h[3],
                                    "text": notes[h[0]].lines[h[1] - 1][:260]})
    res["meta"]["tc_code_commits"] = code_commits
    res["meta"]["tc_parse_fail_blobs"] = len(tctx.code.stats["parse_fail"])
    for nm in names:
        vals = list(tper[nm].values())
        res["tc"][nm] = {"per": tper[nm],
                         "handle": stats([v["handle"] for v in vals]),
                         "list": stats([v["list"] for v in vals]),
                         "handle_code_only": stats([v["handle"] for v in vals if v["code"]]),
                         "details": details[nm]}
    tctx.repo.close()


def cmd_run(a):
    names = a.cands.split(",") if a.cands else [n for n in CANDS if n not in _OPT_IN]
    m1, nd = load_exam()
    if a.extra_exam:   # 例:--extra-exam A7(考卷裡不屬機制①、但要看某候選有沒有列到的題;照它的失效提交跑)
        want = a.extra_exam.split(",")
        m1 = m1 + [q for q in json.load(open(EXAM, encoding="utf-8")) if q["id"] in want and q not in m1]
    res = {"cands": {n: CANDS[n][2] for n in names}, "exam": {}, "rtb": {}, "tc": {}, "nd": {}, "meta": {}}
    ctx = Ctx(a.rtb, RTB_VAULT)
    _run_exam(ctx, names, m1, res)
    _run_rtb_sweep(a, ctx, names, nd, res)
    ctx.repo.close()
    if a.tc:
        _run_tc(a, names, res)
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    report(res, names)


def report(res, names):
    m1ids = ["A1", "A2", "A3", "C1", "C2", "C3", "D1", "D2", "D3"]
    m1ids += [i for i in (res["exam"][names[0]] if names and res["exam"].get(names[0]) else {}) if i not in m1ids]
    print("\n== 9 題(擋到=那一句在要處理層;只列=那一句只在只列出層;點到=同篇別句)==")
    print("cand  " + " ".join(f"{i:>4}" for i in m1ids) + "  擋到 列出")
    for nm in names:
        e = res["exam"][nm]
        row = [e[i]["status"] for i in m1ids]
        blk = sum(1 for s in row if s == "擋到")
        lst = sum(1 for s in row if s in ("擋到", "只列"))
        print(f"{nm:5} " + " ".join(f"{s:>3}" for s in row) + f"  {blk:>3} {lst:>3}")
    print("\n== rtb 噪音(每個動到程式的提交,要處理/只列出)與 13 題非漂移誤列 ==")
    for nm in names:
        r = res["rtb"][nm]
        ndl = res["nd"][nm]
        ndh = [k for k, v in ndl.items() if any(x["status"] == "擋到" for x in v)]
        print(f"{nm:5} b2fc512={r['b2fc512']}  handle={r['handle']}  list={r['list']}  非漂移誤列(任一層)={sorted(ndl)} 要處理層={ndh}")
    if res.get("tc"):
        print("\n== 工具鏈最近提交噪音 ==")
        for nm in names:
            r = res["tc"][nm]
            print(f"{nm:5} handle={r['handle']} list={r['list']} code-only handle={r['handle_code_only']}")


def cmd_show(a):
    res = json.load(open(a.out, encoding="utf-8"))
    if a.repo == "tc":
        for d in res["tc"][a.cand]["details"]:
            if a.layer and d["layer"] != a.layer:
                continue
            print(f"{d['commit']} [{d['layer']}] {d['note']}:{d['line']} ← {','.join(d['tokens'])}\n    {d['text']}")
    else:
        for d in res.get("dump", {}).get(a.cand, {}).get("b2fc512", []):
            if a.layer and d["layer"] != a.layer:
                continue
            print(f"[{d['layer']}] {d['note']}:{d['line']} ← {','.join(d['tokens'])}\n    {d['text']}")


def cmd_time(a):
    """每個候選在單次推送上的耗時:每次都開新的 Ctx(冷快取,含讀樹、剖檔、讀筆記),量牆鐘時間,重複 3 次取中位數。"""
    names = a.cands.split(",") if a.cands else list(CANDS)
    targets = [("rtb", a.rtb, RTB_VAULT, "b2fc512"), ("rtb", a.rtb, RTB_VAULT, "c177791"),
               ("rtb", a.rtb, RTB_VAULT, "5ec931e")]
    if a.tc:
        tl = Repo(a.tc, TC_VAULT).git("log", "--format=%H %s", "-50", a.tc_head).splitlines()
        feats = [ln.split()[0] for ln in tl if " feat" in ln or " fix" in ln][:2]
        for c in feats:
            targets.append(("tc", a.tc, TC_VAULT, c[:8]))
    print("cand  " + " ".join(f"{t[0]}:{t[3]:>9}" for t in targets))
    for nm in names:
        row = []
        for _r, path, vault, c in targets:
            xs = []
            for _ in range(3):
                ctx = Ctx(path, vault)
                base = ctx.repo.parent(c)
                t0 = time.perf_counter()
                run_cand(ctx, nm, base, c)
                xs.append(time.perf_counter() - t0)
                ctx.repo.close()
            row.append(statistics.median(xs))
        print(f"{nm:5} " + " ".join(f"{x:>13.2f}" for x in row), flush=True)


def cmd_q6(a):
    """歷史過濾的成本:①r1 設想的 git log -G 單名;②改成一次建全歷史定義索引。另量條件式/巢狀定義只有 walk 抓得到的量。"""
    for label, path, vault, tip in (("rtb", a.rtb, RTB_VAULT, RTB_TIP), ("tc", a.tc, TC_VAULT, a.tc_head)):
        if not path:
            continue
        ctx = Ctx(path, vault)
        for nm in ("held_rule", "RenewalSkipped", "EXAM_HOLD") if label == "rtb" else ("_lens_py_defs", "cmd_drift_history", "t_checky_swift_and_typescript_profiles"):
            t0 = time.perf_counter()
            out = ctx.repo.git("log", "--all", "--format=%h", "-G", rf"(def|class) {nm}", "--", "*.py", "scripts/lumos")
            print(f"{label} git log -G {nm}: {time.perf_counter() - t0:.1f}s, {len(out.split())} 個提交")
        t0 = time.perf_counter()
        h = ctx.history_defs()
        print(f"{label} 全歷史定義索引:{time.perf_counter() - t0:.1f}s,{len(h)} 個名稱,剖不動 {len(ctx.code.stats['parse_fail'])} 個 blob")
        # 條件式/巢狀:walk 有、頂層+類別內沒有
        t = ctx.repo.tree(tip)
        walk_only, tot, exprc, allc = set(), set(), 0, 0
        for p, sha in t.items():
            if ctx.code.kind(p, sha) == "py":
                info = ctx.code.py(sha)
                if not info:
                    print(f"  {label}@{tip} 剖不動:{p}")
                    continue
                fn_defs = {n for n in info["defs"]}
                tot |= fn_defs
                walk_only |= {n for n in info["defs"] - info["top"]}
                for _k, v in info["consts"].items():
                    allc += 1
                    exprc += v[0] == "expr"
        print(f"  {label}@{tip}: 定義名 {len(tot)},不在頂層/類別直屬(巢狀、條件式、或是指派名){len(walk_only)};模組層大寫常數 {allc} 個,值是運算式 {exprc} 個")
        ctx.repo.close()


def _scan_one(rows, listed, where, nm, tipdefs, hist):
    rel, n, lno, ln, m = where
    if not IDENT_RE.fullmatch(nm or "-") or nm in tipdefs:
        return
    rows["all"] += 1
    if n.ret_full[lno]:
        rows["retired"] += 1
    elif _clause_has_hist(ln, m.start()):
        rows["hist_clause"] += 1
    else:
        k = "ever" if nm in hist else "never"
        rows[k] += 1
        listed.add((rel, lno, k))


def cmd_scan(a):
    """只有一棵樹時(健檢):筆記點名的 [test:] 名在這棵樹找不到的有幾處;分「歷史上曾定義過」與「從沒存在過」。"""
    ctx = Ctx(a.rtb, RTB_VAULT)
    push = Push(ctx, RTB_TIP, RTB_TIP)
    tipdefs = push.tip_all_defs()
    hist = ctx.history_defs()
    notes = push.tip_notes()
    m1, nd = load_exam()
    rows = {"all": 0, "retired": 0, "hist_clause": 0, "ever": 0, "never": 0}
    listed = set()
    for rel, n in notes.items():
        for lno, ln in n.scan_lines():
            for m in TESTREF_RE.finditer(ln):
                for nm in re.split(r"[,、\s]+", m.group(1)):
                    _scan_one(rows, listed, (rel, n, lno, ln, m), nm.strip(), tipdefs, hist)
    print("rtb@067f005 懸空 [test:] 名:", rows)
    for q in m1 + nd:
        _n, lnos = locate(notes, q)
        kinds = {k for (r, ln, k) in listed if r == q["note"] and ln in lnos}
        if kinds or q["id"] in ("D5", "D6", "D4"):
            print(f"  {q['id']} ({q['verdict']}): {sorted(kinds) or '沒列'}")
    ctx.repo.close()


NEG_BANNER_RE = re.compile(r"(未被|沒有|沒被|並未|尚未被|還沒被)(撤除|撤掉|作廢|失效|取代|凍結|結案)|撤除條件|撤掉條件")


def _rv_rows(hs, notes):
    return {(h[0], h[1]): {"note": h[0], "line": h[1], "layer": h[2], "tokens": sorted(set(h[3])),
                           "text": notes[h[0]].lines[h[1] - 1][:260]} for h in hs}


def _rv_released(var, main_):
    """變體多出來的:同一行比名稱集合,差集非空就算放過,只帶差出來的名稱(r3 外家否決席、正確性席:
    原本只比(筆記, 行),一行裡只放過部分名稱時算不到)。"""
    out_ = []
    for k, v in var.items():
        extra = sorted(set(v["tokens"]) - set(main_[k]["tokens"] if k in main_ else ()))
        if extra:
            out_.append(dict(v, tokens=extra, line_also_in_main=k in main_))
    return out_


def cmd_revisit(a):
    """舊句檢查兩週回頭量(Projects/舊句檢查_計劃〈做法〉4):--pairs 每行一組 <base>..<head>(從治理帳 extra.base_sha 與 head_sha 抽)。
    程式檔判定用 FormalCode(跟正式工具同一套)。「多出來」按同一行的名稱集合相減算,鍵是(筆記, 行, 名稱)。
    每一組:P4r3 的命中、關掉句內字眼過濾多出來的行(P4r3c 減 P4r3)、拿掉形狀過濾多出來的行(P4r3s 減 P4r3)、
    不看撤除節②多出來的行(P4r3r 減 P4r3,也就是②實際藏起來的命中);
    再對每組終點的圖譜數只因撤除節②(P4r3 那種)被豁免的非空行與觸發行,以及帶否定或「撤除條件」字樣的撤除行。只讀。"""
    ctx = Ctx(a.repo, a.vault, formal=True)   # 程式檔判定跟正式工具同一套(FormalCode)
    out = {"pairs": [], "retire2": {}, "neg_banner": {}}
    for raw in open(a.pairs, encoding="utf-8"):
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        base, tip = raw.split("..", 1)
        base, tip = ctx.repo.full(base), ctx.repo.full(tip)
        push = Push(ctx, base, tip)
        notes = push.tip_notes()

        main_ = _rv_rows(run_cand(ctx, "P4r3", base, tip, push), notes)
        noclause = _rv_rows(run_cand(ctx, "P4r3c", base, tip, push), notes)
        noshape = _rv_rows(run_cand(ctx, "P4r3s", base, tip, push), notes)
        noretire2 = _rv_rows(run_cand(ctx, "P4r3r", base, tip, push), notes)
        out["pairs"].append({"base": base, "head": tip, "hits": list(main_.values()),
                             "clause_released": _rv_released(noclause, main_),
                             "shape_released": _rv_released(noshape, main_),
                             "retire2_released": _rv_released(noretire2, main_)})
        if tip not in out["retire2"]:
            per, neg = {}, []
            for rel, n in notes.items():
                cnt = sum(1 for lno, ln in n.scan_lines() if ln.strip() and n.ret_full3[lno] and not n.ret_full[lno])
                if cnt:
                    per[rel] = {"lines": cnt, "triggers": [i + 1 for i, ln in enumerate(n.lines)
                                                           if n.regs[i] == "body" and (i + 1) in n.vis
                                                           and ln.lstrip().startswith(">") and _is_banner(ln)
                                                           and any(w in ln for w in SCOPE_WORDS)]}
                neg += [f"{rel}:{i + 1}" for i, ln in enumerate(n.lines)
                        if n.regs[i] == "body" and (i + 1) in n.vis and _is_banner(ln) and NEG_BANNER_RE.search(ln)]
            out["retire2"][tip] = per
            out["neg_banner"][tip] = neg
        p = out["pairs"][-1]
        print(f"{base[:8]}..{tip[:8]} 命中 {len(p['hits'])}(要處理 {sum(1 for h in p['hits'] if h['layer'] == 'handle')})"
              f" 字眼過濾放過 {len(p['clause_released'])} 形狀過濾放過 {len(p['shape_released'])} 撤除節②放過 {len(p['retire2_released'])}"
              f" 撤除節②豁免 {sum(v['lines'] for v in out['retire2'][tip].values())} 行 否定撤除行 {len(out['neg_banner'][tip])}")
    ctx.repo.close()
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "time", "q6", "show", "scan", "revisit"])
    ap.add_argument("--rtb")
    ap.add_argument("--tc")
    ap.add_argument("--tc-head", default="HEAD")
    ap.add_argument("--tc-n", type=int, default=50)
    ap.add_argument("--out", default=str(HERE / "results.json"))
    ap.add_argument("--cands")
    ap.add_argument("--cand")
    ap.add_argument("--repo", default="tc")   # show:tc|rtb;revisit:repo 路徑
    ap.add_argument("--vault", default=TC_VAULT)
    ap.add_argument("--pairs")
    ap.add_argument("--layer")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dump", action="store_true", default=True)
    ap.add_argument("--skip-sweep", action="store_true")
    ap.add_argument("--extra-exam", default="")   # run:考卷裡額外照失效提交跑的題號(逗號分隔,例 A7)
    a = ap.parse_args()
    {"run": cmd_run, "time": cmd_time, "q6": cmd_q6, "show": cmd_show, "scan": cmd_scan, "revisit": cmd_revisit}[a.cmd](a)


if __name__ == "__main__":
    main()
