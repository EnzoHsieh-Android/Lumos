#!/usr/bin/env python3
"""主 session 鏡頭利用率——唯讀重算(Projects/主session鏡頭利用率_計劃 第一段;零新元件)。

讀 ~/.claude/projects/*/ 的逐字稿(主+subagents/),只認 impact-hook 的注入附件
(attachment.type == hook_additional_context 且 hookName ∈ PreToolUse:Edit|Write|MultiEdit),
從注入全文解析「必看」固定席(新舊兩種標頭),以 toolUseID 對到那次 Edit/Write 的行序當錨點,
統計錨點之後同一份逐字稿裡有沒有碰到 pinned 節點(Read / 讀動詞 Bash 含圖譜路徑 /
lumos context|show|contracts <stem>;heredoc 三分法;search 另計)。
★只出分佈,不出單一命中率、不設門檻;印到 stdout;不寫任何帳★。
用法: python3 recount.py --repo <repo 根> [--projects ~/.claude/projects] [--json] [--out 檔]
"""
from __future__ import annotations
import argparse, collections, glob, json, os, re, subprocess, sys
from pathlib import Path

HOOKS = {"PreToolUse:Edit", "PreToolUse:Write", "PreToolUse:MultiEdit"}
# ── Codex 逐字稿(Projects/Codex完全支援_計劃 S3,2026-09-04)──
# ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl;第一行 session_meta(cwd、cli_version、source=exec|{"subagent":…});
# hook 的 additionalContext 記成 response_item/message role=developer(impact-hook 的「必看——」在主代理稿;
# SubagentStart 的「LUMOS-LENS range=」在子代理稿);沒有 toolUseID 可對,錨=同一輪內下一個 custom_tool_call
# (input 含 tools.apply_patch)——是啟發式,rows 標 harness=codex 讓讀表的人分得開。
CODEX_TRANSCRIPT_VERSIONS = {"0.144.1"}
_CX_CMD_RE = re.compile(r'(?<![\w$])["\']?cmd["\']?\s*:\s*"((?:[^"\\]|\\.)*)"')
_CX_PATCH_RE = re.compile(r'"((?:[^"\\]|\\.)*\*\*\* Begin Patch(?:[^"\\]|\\.)*)"')
_CX_HDR_RE = re.compile(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+?)\s*$")
LENS_HDR = re.compile(r"^LUMOS-LENS range=(\S+) 第 (\d+)/(\d+) 席")


def _cx_unescape(x: str) -> str:
    try:
        return json.loads('"' + x + '"')
    except ValueError:
        return x.replace("\\n", "\n").replace('\\"', '"')


def _cx_text(p: dict) -> str:
    c = p.get("content")
    if isinstance(c, list):
        return "\n".join(str(it.get("text", "")) for it in c if isinstance(it, dict))
    return str(c or p.get("message") or "")


def _load_hook_helpers():
    """沿用現役 Stop hook 的 Bash 切段/切詞與圖譜根定位(不自造第二套;code-loop r1 架構席)。hook 檔名帶連字號,用 SourceFileLoader 載。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    here = Path(__file__).resolve()
    hook = here.parents[3] / "scripts" / "hooks" / "claude" / "check-graph-sync.py"
    loader = SourceFileLoader("lens_cgs", str(hook)); spec = importlib.util.spec_from_loader("lens_cgs", loader)
    m = importlib.util.module_from_spec(spec); loader.exec_module(m)
    return m._segment_command, m._tokens_of, m.find_graph_root


_segment_command, _tokens_of, _find_graph_root = _load_hook_helpers()
REDIRECT_RE = re.compile(r"(?<![<>])(?:\d?>>?|&>|>\|)\s*([^\s>&|;]+)")   # 認 > >> 1> &> >|;不吃 2>&1(目標以 & 開頭被排除)、不吃 <<
HEREDOC_RE = re.compile(r"(?<!<)<<(?!<)-?\s*['\"]?\w+")           # 排除 <<<(here-string)
QUOTED_RE = re.compile(r"\"(?:\\.|[^\"\\])*\"|'[^']*'")
SCRIPT_HINTS = ("read_text", "write_text", "open(")


def _strip_quoted(s: str) -> str:
    """把引號內字串挖掉(留空白佔位),重導向/切段只看殼層語法,不看字串內容(code-loop r2 s1:commit message 提到路徑旁有 > 被誤判)。"""
    return QUOTED_RE.sub(lambda m: " " * len(m.group(0)), s)


SUBSHELL_RE = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")
COMPLEX_RE = re.compile(r"<<|\$\(|`|\bpython3?\b[^\n]*\s-c\s")


def _safe_tokens(seg: str) -> list:
    """沿用 check-graph-sync 的切詞;它對不成對引號會★自己吞掉例外回空★(r3 架構/通才席:try/except 到不了),
    所以「回空但輸入非空」才是退回正規式的條件,★不得整段靜默消失★。"""
    toks = _tokens_of(seg)
    if not toks and seg.strip():
        toks = TOKEN_RE.findall(seg)
    return [w.strip("$") for x in toks for w in x.split() if w.strip("$")]


def _split_subshells(cmd: str) -> list[str]:
    """把 $(…)/`…` 的內容拆成獨立段(各自有自己的動詞),外層保留佔位——不再把括號拍平成同一段(r3 正確性席:cat 變外層動詞)。"""
    inner = [m.group(1) or m.group(2) or "" for m in SUBSHELL_RE.finditer(cmd)]
    outer = SUBSHELL_RE.sub(" SUBSHELL ", cmd)
    return [outer] + [x for x in inner if x.strip()]


def _script_marks(text: str, slug: str) -> tuple[set[str], set[str]]:
    """腳本文字(heredoc 或 python -c)裡每個筆記路徑:同一行或它被賦給的變數(含 `with open(p) as f`)後續的
    read_text/write_text/open 決定讀/寫;變數被重新賦值就停止追蹤(r3 通才席)。★啟發式,低信心層★——
    只寫入 loose 欄,不進 strict any。"""
    read, wrote = set(), set()
    lines = text.split("\n")
    for k, ln in enumerate(lines):
        for tok in TOKEN_RE.findall(ln):
            n = norm_note(tok, slug)
            if not n:
                continue
            esc = re.escape(tok.strip("'\"`,;:"))
            scopes = [ln]
            m = re.search(r"(\w+)\s*=\s*[^=\n]*" + esc, ln) or re.search(r"open\([^)]*" + esc + r"[^)]*\)\s*as\s+(\w+)", ln)
            var = m.group(1) if m else None
            if var:
                for ln2 in lines[k + 1:]:
                    if re.match(r"\s*" + re.escape(var) + r"\s*=[^=]", ln2):
                        break   # 重新賦值→停止追蹤
                    if re.search(r"\b" + re.escape(var) + r"\.(read_text|write_text|read|write)\b|open\(\s*" + re.escape(var) + r"\b", ln2):
                        scopes.append(ln2)
            joined = "\n".join(scopes)
            if re.search(r"read_text|\.read\(\)|open\([^)]*['\"]r['\"]", joined):
                read.add(n)
            if re.search(r"write_text|\.write\(|open\([^)]*['\"][wa]['\"]", joined):
                wrote.add(n)
    return read, wrote


HDR_OLD = re.compile(r"^必看\(合約/事故固定席 (\d+)\):")
HDR_NEW = re.compile(r"^必看——這 (\d+) 篇")
PIN_LINE = re.compile(r"^\s+\S+(?:\s+★[^★]+★)?\s+(.+?\.md)(?:\s|$)")   # 事故行沒有 ★TAG★;節點路徑可含空白(非貪婪到 .md)
READ_VERBS = {"cat", "sed", "head", "tail", "less", "grep", "rg", "bat", "more"}
LUMOS_CMDS = {"context", "show", "contracts"}
TOKEN_RE = re.compile(r"[^\s'\"`;|&()<>]+")


def repo_paths(repo: Path) -> set[str]:
    out = {str(repo.resolve())}
    try:
        r = subprocess.run(["git", "-C", str(repo), "worktree", "list", "--porcelain"], capture_output=True, text=True, timeout=10)
        for line in r.stdout.splitlines():
            if line.startswith("worktree "):
                out.add(str(Path(line[9:]).resolve()))
    except Exception:
        pass
    return out


def vault_slug(repo: Path) -> str | None:
    g = _find_graph_root(repo)
    return g.name if g else None


def norm_note(tok: str, slug: str) -> str | None:
    """絕對/相對路徑 → 圖譜相對路徑(Systems/x.md);不是圖譜路徑回 None。"""
    t = os.path.normpath(tok.replace("\\", "/").strip().strip("'\"`,;:").strip())
    key = f"docs/{slug}/"
    i = t.find(key)
    if i < 0:
        return None
    rel = t[i + len(key):]
    return rel if rel.endswith(".md") else None


def parse_pins(content) -> tuple[str, list[str], bool]:
    text = content if isinstance(content, str) else "\n".join(str(c) if not isinstance(c, dict) else str(c.get("text", "")) for c in (content or []))
    ver, pins, complete = "none", [], True
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        m = HDR_OLD.match(ln) or HDR_NEW.match(ln)
        if not m:
            continue
        ver = "old" if HDR_OLD.match(ln) else "new"
        n = int(m.group(1))
        for ln2 in lines[i + 1:]:
            pm = PIN_LINE.match(ln2)
            if pm:
                pins.append(pm.group(1))
            elif ln2.strip() == "" or not ln2.startswith("  "):
                break
        complete = len(pins) >= n
        break
    return ver, pins, complete


def classify_bash(cmd: str, slug: str) -> tuple[set[str], set[str], set[str], set[str], set[str]]:
    """回 (高信心讀, 啟發式讀, 寫回, lumos context/show/contracts 的詞, search 的詞)。
    高信心讀=單純段落(無 heredoc/子殼/python -c)裡讀動詞帶筆記路徑;啟發式讀=腳本/heredoc/子殼內判出來的(低信心,報表分開印)。
    寫回=引號外重導向(> >> 1> &> >|)到筆記 / sed -i / 腳本內就近 write。純拼字串提到路徑兩者都不算。"""
    import shlex
    strict, loose, wrote, lumos_terms, search_terms = set(), set(), set(), set(), set()
    complex_cmd = bool(COMPLEX_RE.search(cmd))
    if HEREDOC_RE.search(cmd) or re.search(r"\bpython3?\b[^\n]*\s-c\s", cmd):
        r2, w2 = _script_marks(cmd, slug); loose |= r2; wrote |= w2
        for m in REDIRECT_RE.finditer(_strip_quoted(cmd.split("\n")[0])):
            n2 = norm_note(m.group(1), slug)
            if n2: wrote.add(n2)
        return strict, loose, wrote, lumos_terms, search_terms
    for idx, piece in enumerate(_split_subshells(cmd)):     # 先拆子殼再切段:否則 ; | 會把 $(…) 切成不成對的半截
        for seg in _segment_command(piece):
            bare = _strip_quoted(seg)
            for m in REDIRECT_RE.finditer(bare):
                n2 = norm_note(m.group(1), slug)
                if n2: wrote.add(n2)
            st = _safe_tokens(seg)
            if not st:
                continue
            j = 0
            while j < len(st) and ("=" in st[j] and not st[j].startswith("-")):
                j += 1
            if j >= len(st):
                continue
            verb = os.path.basename(st[j]); args = st[j + 1:]
            if verb in ("python", "python3") and args and os.path.basename(args[0]).endswith("lumos"):   # `python3 scripts/lumos …`(Codex 稿常見;S3)
                j += 1; verb = os.path.basename(st[j]); args = st[j + 1:]
            target = strict if (idx == 0 and not complex_cmd) else loose   # 子殼內/複合指令的讀=啟發式
            if verb == "sed" and any(a == "-i" or a.startswith("-i") for a in args):
                for a in args:
                    n = norm_note(a, slug)
                    if n: wrote.add(n)
            elif verb in READ_VERBS:
                for a in args:
                    n = norm_note(a, slug)
                    if n: target.add(n)
            elif verb.endswith("lumos") and args:
                sub = args[0]
                try:
                    raw = shlex.split(seg)
                except ValueError:
                    raw = st
                terms = [a for a in raw[raw.index(sub) + 1:] if not a.startswith("-")] if sub in raw else [a for a in args[1:] if not a.startswith("-")]
                if sub in LUMOS_CMDS:
                    lumos_terms.update(terms); lumos_terms.add("".join(terms))
                    for t2 in terms:   # 帶路徑的節點名(Systems/a.md、Systems/a)也對到 stem(S3;Claude 稿多用裸名,Codex 稿實看帶路徑)
                        base = t2.rsplit("/", 1)[-1]
                        lumos_terms.add(base[:-3] if base.endswith(".md") else base)
                elif sub == "search":
                    search_terms.update(terms); search_terms.update(w for t2 in terms for w in t2.split())
    return strict, loose, wrote, lumos_terms, search_terms


def scan_codex_file(path: Path, slug: str, repo_set: set[str]):
    """Codex rollout → rows(同 scan_file 的欄位,多 harness=codex)。版本不在 fixture 表 → 跳過並回 (rows, bad, skipped=True)。"""
    rows = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return rows, 0
    objs, bad = [], 0
    for ln in lines:
        if not ln.strip():
            continue
        try:
            objs.append(json.loads(ln))
        except Exception:
            bad += 1
    if not objs or objs[0].get("type") != "session_meta":
        return rows, bad
    meta = objs[0].get("payload") or {}
    if str(meta.get("cli_version") or "") not in CODEX_TRANSCRIPT_VERSIONS:
        return rows, bad
    cwd = str(Path(str(meta.get("cwd") or "")).resolve()) if meta.get("cwd") else ""
    if not cwd or not any(cwd == r or cwd.startswith(r + "/") for r in repo_set):
        return rows, bad
    is_sub = meta.get("thread_source") == "subagent" or isinstance(meta.get("source"), dict)
    sid = meta.get("session_id") or meta.get("id")
    for idx, o in enumerate(objs):
        p = o.get("payload") or {}
        if o.get("type") != "response_item" or p.get("type") != "message" or p.get("role") != "developer":
            continue
        txt = _cx_text(p)
        first = txt.split("\n", 1)[0].strip()
        lens = LENS_HDR.match(first)
        if lens:
            rows.append({"session_id": sid, "is_subagent": is_sub, "harness": "codex", "hook_name": "SubagentStart:dispatch-lens",
                         "header_version": "lens", "file": "", "n_pinned": 0, "pinned_complete": True, "anchored": True, "ftype": "repo",
                         "lens_range": lens.group(1), "lens_seat": f"{lens.group(2)}/{lens.group(3)}",
                         "touched": [], "touched_loose": [], "pre_touched": [], "wrote_back": [], "search_touched": [], "any": False, "any_loose": False})
            continue
        if not (HDR_OLD.match(first) or HDR_NEW.match(first)):
            continue
        ver, pins, complete = parse_pins(txt)
        # 錨=同輪內離注入最近的 apply_patch 呼叫(先往後找,沒有再往前找——0.144.1 實看兩種順序都有);
        # 目標檔=其 patch 標頭第一個路徑;同輪內找不到 apply_patch → 退而取最近的任一 custom_tool_call(anchored 仍 True 但 file 空)
        def _is_boundary(o2):
            q2 = o2.get("payload") or {}
            return (o2.get("type") == "event_msg" and q2.get("type") == "user_message") or \
                   (o2.get("type") == "response_item" and q2.get("type") == "message" and q2.get("role") == "user")
        def _patch_target(q2):
            inp2 = q2.get("input") if isinstance(q2.get("input"), str) else ""
            for m in _CX_PATCH_RE.finditer(inp2):
                for ln2 in _cx_unescape(m.group(1)).split("\n"):
                    h = _CX_HDR_RE.match(ln2.strip())
                    if h:
                        return h.group(1).strip()
            return ""
        anchor, target, fallback = None, "", None
        for direction in (1, -1):
            j = idx + direction
            while 0 <= j < len(objs) and not _is_boundary(objs[j]):
                q = objs[j].get("payload") or {}
                if objs[j].get("type") == "response_item" and q.get("type") == "custom_tool_call":
                    t = _patch_target(q)
                    if t:
                        anchor, target = j, t
                        break
                    if fallback is None:
                        fallback = j
                j += direction
            if anchor is not None:
                break
        if anchor is None and fallback is not None:
            anchor = fallback
        ftype = "scratch" if ("/scratchpad/" in target or "/tmp/" in target) else ("repo" if target else "unknown")
        row = {"session_id": sid, "is_subagent": is_sub, "harness": "codex", "hook_name": "PreToolUse:apply_patch",
               "header_version": ver, "file": target, "n_pinned": len(pins), "pinned_complete": complete,
               "anchored": anchor is not None, "ftype": ftype, "touched": [], "touched_loose": [], "pre_touched": [], "wrote_back": [], "search_touched": []}
        if anchor is not None and pins:
            pinset = set(pins); stems = {}
            for pth in pins:
                stems.setdefault(pth.rsplit("/", 1)[-1][:-3], []).append(pth)
            row["ambiguous"] = []
            for j, o2 in enumerate(objs):
                q = o2.get("payload") or {}
                if o2.get("type") != "response_item" or q.get("type") != "custom_tool_call":
                    continue
                inp = q.get("input") if isinstance(q.get("input"), str) else ""
                for m in _CX_CMD_RE.finditer(inp):
                    cmd = _cx_unescape(m.group(1))
                    hit_read, hit_loose, hit_write, terms, sterms = classify_bash(cmd, slug)
                    for t in terms:   # lumos show/context/contracts <詞> → 對到釘住節點(同 scan_file:單一 stem 才算命中)
                        if t in stems:
                            if len(stems[t]) == 1:
                                hit_read.add(stems[t][0])
                            else:
                                for pth in stems[t]:
                                    if pth not in row["ambiguous"]:
                                        row["ambiguous"].append(pth)
                    bucket = row["touched"] if j > anchor else row["pre_touched"]
                    for n in sorted(hit_read & pinset):
                        if n not in bucket:
                            bucket.append(n)
                    if j > anchor:
                        for n in sorted(hit_loose & pinset):
                            if n not in row["touched_loose"]:
                                row["touched_loose"].append(n)
                        for n in sorted(hit_write & pinset):
                            if n not in row["wrote_back"]:
                                row["wrote_back"].append(n)
                        for t in sterms:
                            for st, plist in stems.items():
                                for pth in plist:
                                    if t and t in st and pth not in row["search_touched"]:
                                        row["search_touched"].append(pth)
        row["any"] = bool(row["touched"]); row["any_loose"] = bool(row["touched"] or row["touched_loose"])
        rows.append(row)
    return rows, bad


def scan_file(path: Path, slug: str, repo_set: set[str]):
    rows = []
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return rows, 0
    objs, bad = [], 0
    for ln in lines:
        try:
            objs.append(json.loads(ln))
        except Exception:
            bad += 1
    # cwd 篩:任一行 cwd 在 repo/worktree 之下才算本專案
    cwds = {str(Path(o.get("cwd")).resolve()) for o in objs if isinstance(o, dict) and o.get("cwd")}
    if not any(any(c == r or c.startswith(r + "/") for r in repo_set) for c in cwds):
        return rows, bad
    is_sub = "/subagents/" in str(path)
    # 索引 tool_use by id → 行序
    tu_index = {}
    for idx, o in enumerate(objs):
        if o.get("type") != "assistant":
            continue
        for it in (o.get("message", {}).get("content") or []):
            if isinstance(it, dict) and it.get("type") == "tool_use":
                tu_index[it.get("id")] = (idx, it.get("name"), it.get("input") or {})
    seen = set()
    for idx, o in enumerate(objs):
        att = o.get("attachment") if isinstance(o.get("attachment"), dict) else None
        if not att or att.get("type") != "hook_additional_context" or att.get("hookName") not in HOOKS:
            continue
        tid = att.get("toolUseID")
        if not tid or tid in seen:
            continue
        seen.add(tid)
        ver, pins, complete = parse_pins(att.get("content"))
        anchor = tu_index.get(tid)
        target = (anchor[2].get("file_path") if anchor else "") or ""
        ftype = "scratch" if ("/scratchpad/" in target or "/tmp/" in target or (target and not any(target.startswith(r) for r in repo_set) and target.startswith("/"))) else ("test" if "test" in os.path.basename(target).lower() else "code")
        row = {"session_id": o.get("sessionId") or o.get("session_id"), "is_subagent": is_sub, "hook_name": att.get("hookName"),
               "header_version": ver, "file": target, "n_pinned": len(pins), "pinned_complete": complete,
               "anchored": anchor is not None, "ftype": ftype, "touched": [], "touched_loose": [], "pre_touched": [], "wrote_back": [], "search_touched": [], "ambiguous": []}
        if anchor and pins:
            pinset = set(pins); stems = {}
            for pth in pins:
                stems.setdefault(pth.rsplit("/", 1)[-1][:-3], []).append(pth)
            for j, o2 in enumerate(objs):
                if o2.get("type") != "assistant":
                    continue
                for it in (o2.get("message", {}).get("content") or []):
                    if not (isinstance(it, dict) and it.get("type") == "tool_use"):
                        continue
                    hit_read, hit_loose, hit_write, terms, sterms = set(), set(), set(), set(), set()
                    if it.get("name") == "Read":
                        n = norm_note(str((it.get("input") or {}).get("file_path", "")), slug)
                        if n: hit_read.add(n)
                    elif it.get("name") == "Bash":
                        hit_read, hit_loose, hit_write, terms, sterms = classify_bash(str((it.get("input") or {}).get("command", "")), slug)
                    for t in terms:
                        if t in stems:
                            if len(stems[t]) == 1: hit_read.add(stems[t][0])
                            else:
                                for pth in stems[t]:
                                    if pth not in row["ambiguous"]: row["ambiguous"].append(pth)
                    bucket = row["touched"] if j > anchor[0] else row["pre_touched"]
                    for n in hit_read & pinset:
                        if n not in bucket: bucket.append(n)
                    if j > anchor[0]:
                        for n in hit_loose & pinset:
                            if n not in row["touched_loose"]: row["touched_loose"].append(n)
                    for n in hit_write & pinset:
                        if j > anchor[0] and n not in row["wrote_back"]: row["wrote_back"].append(n)
                    for t in sterms:
                        for s, plist in stems.items():
                            for p in plist:
                                if t and t in s and p not in row["search_touched"] and j > anchor[0]:
                                    row["search_touched"].append(p)
        row["any"] = bool(row["touched"])                          # 高信心:Read 工具/單純讀動詞/lumos 指令
        row["any_loose"] = bool(row["touched"] or row["touched_loose"])   # 加啟發式(heredoc/腳本/子殼),低信心
        rows.append(row)
    return rows, bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True); ap.add_argument("--projects", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--json", action="store_true"); ap.add_argument("--out")
    ap.add_argument("--codex-sessions", default=os.path.join(os.environ.get("CODEX_HOME") or os.path.expanduser("~/.codex"), "sessions"),
                    help="Codex rollout 逐字稿根目錄(預設 $CODEX_HOME/sessions 或 ~/.codex/sessions;不存在就只讀 Claude)")
    a = ap.parse_args()
    repo = Path(a.repo).resolve(); slug = vault_slug(repo)
    if not slug:
        print("擋下:repo 下找不到 docs/*-knowledge", file=sys.stderr); return 2
    repo_set = repo_paths(repo)
    files = glob.glob(os.path.join(a.projects, "*", "*.jsonl")) + glob.glob(os.path.join(a.projects, "*", "*", "subagents", "agent-*.jsonl"))
    rows, bad, broken = [], 0, 0
    for f in files:
        try:
            r, b = scan_file(Path(f), slug, repo_set); rows.extend(r); bad += b
        except Exception as e:   # 一份壞逐字稿不能讓整份報表死掉(同 recount.py 慣例:壞資料跳過並計數)
            broken += 1; print(f"跳過 {f}: {type(e).__name__}", file=sys.stderr)
    for r in rows:
        r.setdefault("harness", "claude")
    cx_files = glob.glob(os.path.join(a.codex_sessions, "**", "rollout-*.jsonl"), recursive=True) if os.path.isdir(a.codex_sessions) else []
    for f in cx_files:
        try:
            r, b = scan_codex_file(Path(f), slug, repo_set); rows.extend(r); bad += b
        except Exception as e:
            broken += 1; print(f"跳過 {f}: {type(e).__name__}", file=sys.stderr)
    files = files + cx_files
    C = collections.Counter
    denom = [r for r in rows if r["n_pinned"] > 0 and r["ftype"] != "scratch" and r["anchored"]]
    rep = {
        "files_scanned": len(files), "bad_lines": bad, "broken_files": broken, "pushes_total": len(rows),
        "by_role": dict(C("sub" if r["is_subagent"] else "main" for r in rows)),
        "by_harness": dict(C(r.get("harness", "claude") for r in rows)),
        "codex_lens_rows": sum(1 for r in rows if r.get("hook_name") == "SubagentStart:dispatch-lens"),
        "codex_files": len(cx_files),
        "by_header": dict(C(r["header_version"] for r in rows)),
        "empty_pinned": sum(1 for r in rows if r["n_pinned"] == 0), "unanchored": sum(1 for r in rows if not r["anchored"]),
        "scratch_or_outside": sum(1 for r in rows if r["ftype"] == "scratch"), "pinned_incomplete": sum(1 for r in rows if not r["pinned_complete"]),
        "denominator": len(denom),
        "n_pinned_dist": dict(sorted(C(r["n_pinned"] for r in denom).items())),
        "any_by_ftype": {k: {"n": v, "any": sum(1 for r in denom if r["ftype"] == k and r["any"]), "any_loose": sum(1 for r in denom if r["ftype"] == k and r["any_loose"])} for k, v in C(r["ftype"] for r in denom).items()},
        "any_by_pinned_bucket": {k: {"n": v, "any": sum(1 for r in denom if _bucket(r["n_pinned"]) == k and r["any"]), "any_loose": sum(1 for r in denom if _bucket(r["n_pinned"]) == k and r["any_loose"])} for k, v in C(_bucket(r["n_pinned"]) for r in denom).items()},
        "pre_touched_rows": sum(1 for r in denom if r["pre_touched"]), "wrote_back_rows": sum(1 for r in denom if r["wrote_back"]),
        "search_touched_rows": sum(1 for r in denom if r["search_touched"]),
        "sessions": dict(C(r["session_id"] for r in denom).most_common()),
    }
    text = json.dumps({"summary": rep, "rows": rows}, ensure_ascii=False, indent=1) if a.json else _render(rep)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


def _bucket(n):
    return "1" if n == 1 else ("2-4" if n <= 4 else ("5-10" if n <= 10 else "11+"))


def _render(rep):
    L = ["主 session 鏡頭利用率——歷史逐字稿重算(只出分佈,不出命中率,不設門檻)",
         f"掃了 {rep['files_scanned']} 份逐字稿(壞行 {rep['bad_lines']}、跳過壞檔 {rep['broken_files']});impact 注入 {rep['pushes_total']} 次:主/子 {rep['by_role']},標頭版 {rep['by_header']}",
         f"不進分母:固定席空 {rep['empty_pinned']}、對不到錨點 {rep['unanchored']}、scratch/repo 外 {rep['scratch_or_outside']};固定席清單不全 {rep['pinned_incomplete']}",
         f"分母(有固定席、非 scratch、有錨點)={rep['denominator']};|pinned| 分佈 {rep['n_pinned_dist']}",
         "推送後有碰到任一篇 pinned——★分型讀,不合併★;any=高信心證據(Read 工具/單純讀動詞/lumos 指令),any_loose=加上啟發式(heredoc/腳本/子殼,低信心):"]
    for k, v in rep["any_by_pinned_bucket"].items():
        L.append(f"  |pinned| {k}:{v['n']} 次,any {v['any']}(loose {v['any_loose']})")
    for k, v in rep["any_by_ftype"].items():
        L.append(f"  檔型 {k}:{v['n']} 次,any {v['any']}(loose {v['any_loose']})")
    L.append(f"另列:推送前已碰 {rep['pre_touched_rows']}、只寫回未讀 {rep['wrote_back_rows']}、search 碰(弱證據) {rep['search_touched_rows']}")
    L.append(f"session 叢聚:{rep['sessions']}")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
