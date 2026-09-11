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
# ★Codex 解析核心(版本表/兩個正規式/反跳脫)不在這裡自造,向 check-graph-sync.py 借(同 _load_hook_helpers 的借法;
# code-codex-s3 r1 架構席:兩份版本表會各自漂)★——見下方 _load_hook_helpers 回傳。
LENS_HDR = re.compile(r"^LUMOS-LENS range=(\S+) 第 (\d+)/(\d+) 席")


def _codex_text(p: dict) -> str:
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
    return m


_cgs = _load_hook_helpers()
CODEX_TRANSCRIPT_VERSIONS = _cgs.CODEX_TRANSCRIPT_VERSIONS       # 單源:改版只補 hook 那一張表
_CODEX_EXEC_CMD_RE, _CODEX_APPLY_PATCH_RE, _CODEX_PATCH_HDR_RE = _cgs._CODEX_EXEC_CMD_RE, _cgs._CODEX_APPLY_PATCH_RE, _cgs._CODEX_PATCH_HDR_RE
_js_unescape = _cgs._js_unescape


_segment_command, _tokens_of, _find_graph_root = _cgs._segment_command, _cgs._tokens_of, _cgs.find_graph_root
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
            if verb in ("python", "python3") and args and os.path.basename(args[0]) == "lumos":   # `python3 scripts/lumos …`(Codex 稿常見;S3;basename 恰為 lumos,notlumos 不算——r1 外家 #4)
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
                    for t2 in terms:   # 帶路徑的節點名(Systems/a.md、Systems/a)→ 完整相對路徑精確比對釘住清單,★不降成裸 stem★
                        if "/" in t2:  # (裸 stem 會把 Other/a.md 撞成 Systems/a.md;code-codex-s3 r1 單reviewer F2)
                            lumos_terms.add(t2 if t2.endswith(".md") else t2 + ".md")
                elif sub == "search":
                    search_terms.update(terms); search_terms.update(w for t2 in terms for w in t2.split())
    return strict, loose, wrote, lumos_terms, search_terms


def _read_jsonl(path) -> tuple[list, int]:
    """逐字稿逐行 json → (物件, 壞行數)。壞行(含空行、寫到一半的尾行)只跳過那一行、其餘照讀——scan_file / scan_codex_file /
    run_misses 共用這一份(代碼審 r1 架構席 B2;外家 C4:一行壞 JSON 不能丟掉整份逐字稿)。讀不到檔 → ([], 0)。"""
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return [], 0
    objs, bad = [], 0
    for ln in lines:
        try:
            objs.append(json.loads(ln))
        except Exception:
            bad += 1
    return objs, bad


def _under_repo(cwd: str, repo_set) -> bool:
    return any(cwd == r or cwd.startswith(r + "/") for r in repo_set)


def _claude_in_repo(objs, repo_set) -> bool:
    """Claude 逐字稿:任一行 cwd 在 repo/worktree 之下才算本專案。"""
    cwds = {str(Path(o.get("cwd")).resolve()) for o in objs if isinstance(o, dict) and o.get("cwd")}
    return any(_under_repo(c, repo_set) for c in cwds)


def _codex_meta(objs, path, repo_set) -> tuple[dict | None, str]:
    """Codex rollout 的 session_meta → (payload, "ok");不是 Codex 稿 / 版本不在認得的表(stderr 一行、不猜格式,同 check-graph-sync
    的處置)/ cwd 不在本 repo → (None, 原因)。scan_codex_file 與 run_misses 共用這一份(代碼審 r1 架構席 B2、外家 C3)。"""
    if not objs or not isinstance(objs[0], dict) or objs[0].get("type") != "session_meta":
        return None, "not_codex"
    meta = objs[0].get("payload") or {}
    if str(meta.get("cli_version") or "") not in CODEX_TRANSCRIPT_VERSIONS:
        print(f"跳過 {Path(path).name}: Codex 逐字稿版本 {meta.get('cli_version') or '?'} 不在認得的表 {sorted(CODEX_TRANSCRIPT_VERSIONS)}(不猜格式)", file=sys.stderr)
        return None, "version"
    cwd = str(Path(str(meta.get("cwd") or "")).resolve()) if meta.get("cwd") else ""
    if not cwd or not _under_repo(cwd, repo_set):
        return None, "other_repo"
    return meta, "ok"


def scan_codex_file(path: Path, slug: str, repo_set: set[str]):
    """Codex rollout → rows(同 scan_file 的欄位,多 harness=codex)。版本不在 fixture 表 → stderr 一行、回 ([], bad)(同 check-graph-sync 的處置)。
    壞行計數同 scan_file(空行也算壞行,兩邊一致)。"""
    rows = []
    objs, bad = _read_jsonl(path)
    meta, _why = _codex_meta(objs, path, repo_set)
    if meta is None:
        return rows, bad
    is_sub = meta.get("thread_source") == "subagent" or isinstance(meta.get("source"), dict)
    sid = meta.get("session_id") or meta.get("id")
    used_anchors = set()   # 一個 apply_patch 只能當一次錨(同輪兩次注入共用會張冠李戴;code-codex-s3 r1 單reviewer F1)
    for idx, o in enumerate(objs):
        p = o.get("payload") or {}
        if o.get("type") != "response_item" or p.get("type") != "message" or p.get("role") != "developer":
            continue
        txt = _codex_text(p)
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
            for m in _CODEX_APPLY_PATCH_RE.finditer(inp2):
                for ln2 in _js_unescape(m.group(1)).split("\n"):
                    h = _CODEX_PATCH_HDR_RE.match(ln2.strip())
                    if h:
                        return h.group(1).strip()
            return ""
        # 兩個方向各找同輪內最近的一個 apply_patch,取距離小的(code-codex-s3 r1 外家 #1:先往後找會讓前一行的輸給後面較遠的);
        # 同輪內完全沒有 apply_patch → anchored False(外家 #2:不拿任意 exec 當錨,免得沒工具關聯的注入進 denominator)
        anchor, target = None, ""
        cands = []
        for direction in (1, -1):
            j = idx + direction
            while 0 <= j < len(objs) and not _is_boundary(objs[j]):
                q = objs[j].get("payload") or {}
                if objs[j].get("type") == "response_item" and q.get("type") == "custom_tool_call" and j not in used_anchors:
                    t = _patch_target(q)
                    if t:
                        cands.append((abs(j - idx), j, t))
                        break
                j += direction
        if cands:
            _, anchor, target = min(cands)
            used_anchors.add(anchor)
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
                for m in _CODEX_EXEC_CMD_RE.finditer(inp):
                    cmd = _js_unescape(m.group(1))
                    hit_read, hit_loose, hit_write, terms, sterms = classify_bash(cmd, slug)
                    for t in terms:   # lumos show/context/contracts <詞> → 對到釘住節點(同 scan_file:單一 stem 才算命中;帶路徑精確對)
                        if "/" in t:
                            if t in pinset:
                                hit_read.add(t)
                            continue
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
    objs, bad = _read_jsonl(path)
    if not _claude_in_repo(objs, repo_set):   # cwd 篩:任一行 cwd 在 repo/worktree 之下才算本專案
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
                        if "/" in t:                       # 完整相對路徑:精確對釘住清單
                            if t in pinset: hit_read.add(t)
                            continue
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


# ══ 推播漏網量測(Projects/推播miss量測_計劃,2026-09-11)══════════════════════════════════════
# 上面的鏡頭利用率只看「推了的有沒有被讀」;這一段看反面——沒推卻被讀的(miss)。錨點是每一次編輯本身
# (零推播也有一列),讀取歸給最近一次「有關」的編輯,分類問 lumos impact(不在這裡另寫比對)。
# ★只出清單與分佈,不出命中率、不設門檻;週跑存推導列(不存原文、不存查詢字串)★。
import datetime as _dt
import hashlib as _hashlib
import time as _time

SEC_FREE = re.compile(r"^可能相關的 (\d+) 篇")
SEC_RESCUE = re.compile(r"^另外 (\d+) 篇分數不高但直接提到這個檔")
SEC_LANE = re.compile(r"^守衛面參考——這 (\d+) 篇")
SEC_LEGACY = re.compile(r"^(直接提到這個檔的筆記|透過連結間接牽到的筆記|這個檔過去出過的事故\(改之前先看\)):\s*$")
SEC_STACK = re.compile(r"^\[.+ 效能檢核——")
MULTI_NOTE = re.compile(r"^\(多檔 patch 只算了前 \d+ 檔,其餘只列名:(.*)\)\s*$")
INSTRUCTION_PREFIX = "動手前看一眼上面這些筆記"
SCORE_LINE = re.compile(r"^\s+\d+(?:\.\d+)?\s+\S+\s+(.+?\.md)(?:\s|$)")            # 分數 種類詞 節點路徑(路徑可含空白)
TRUNC_LINE = re.compile(r"^\s+\((?:\+(\d+) 條低分截斷,沒列出來|另有 (\d+) 條守衛面參考未列出)\)\s*$")
LEGACY_NODE = re.compile(r"(?:^|\s)((?:[^\s/]+/)+[^\s]+?\.md)(?=\s|$)")
PUSH_MARKERS = (HDR_OLD, HDR_NEW, SEC_FREE, SEC_RESCUE, SEC_LANE, SEC_LEGACY)


def parse_push(content) -> dict:
    """推播注入全文 → {nodes, complete, truncated, impact_skipped}。
    四段都認:必看(新舊標頭,PIN_LINE)、可能相關/另外 N 篇/守衛面參考(分數行);舊版三段也認。
    效能檢核題段、多檔 patch 的「只算了前 N 檔」說明、收尾指示、框線認得、跳過;截斷行記數、不算推了。
    某段解析到的行數少於標頭 N、段裡有讀不懂的行、或遇到認不得的段標頭 → complete=False(整筆不下 miss 結論:
    沒讀全的那段可能正好有被讀的那篇)。多檔 patch 的多塊逐塊掃,取聯集。"""
    text = content if isinstance(content, str) else "\n".join(
        str(c) if not isinstance(c, dict) else str(c.get("text", "")) for c in (content or []))
    nodes, skipped = set(), []
    st = {"sec": None, "want": 0, "got": 0, "complete": True, "trunc": 0}

    def close():
        if st["sec"] in ("pin", "score") and st["got"] < st["want"]:
            st["complete"] = False
        st["sec"] = None

    for ln in text.split("\n"):
        if not ln.strip() or "─────" in ln:
            close(); continue
        if not ln.startswith((" ", "\t")):
            close()
            m = HDR_OLD.match(ln) or HDR_NEW.match(ln)
            if m:
                st.update(sec="pin", want=int(m.group(1)), got=0); continue
            m = SEC_FREE.match(ln) or SEC_RESCUE.match(ln) or SEC_LANE.match(ln)
            if m:
                st.update(sec="score", want=int(m.group(1)), got=0); continue
            if SEC_LEGACY.match(ln):
                st.update(sec="legacy", want=0, got=0); continue
            if SEC_STACK.match(ln):
                st["sec"] = "skip"; continue
            m = MULTI_NOTE.match(ln)
            if m:
                skipped += [x.strip() for x in m.group(1).split(",") if x.strip()]; continue
            if ln.startswith(INSTRUCTION_PREFIX):
                continue
            st["complete"] = False; st["sec"] = "unknown"; continue
        s = ln.strip()
        if st["sec"] in ("skip", "unknown") or s.startswith("(這次編輯內容超過"):
            continue
        if st["sec"] == "pin":
            pm = PIN_LINE.match(ln)
            if pm:
                nodes.add(pm.group(1)); st["got"] += 1
            else:
                st["complete"] = False
        elif st["sec"] == "score":
            tm = TRUNC_LINE.match(ln)
            if tm:
                st["trunc"] += int(tm.group(1) or tm.group(2)); continue
            sm = SCORE_LINE.match(ln)
            if sm:
                nodes.add(sm.group(1)); st["got"] += 1
            else:
                st["complete"] = False
        elif st["sec"] == "legacy":
            lm = LEGACY_NODE.search(ln)
            if lm:
                nodes.add(lm.group(1))
            else:
                st["complete"] = False
        else:
            st["complete"] = False   # 縮排行卻不在任何認得的段裡
    close()
    return {"nodes": nodes, "complete": st["complete"], "truncated": st["trunc"], "impact_skipped": skipped}


def _is_push_text(text: str) -> bool:
    return any(p.match(ln) for ln in str(text).split("\n") for p in PUSH_MARKERS)


def _rel_to_repo(fp, repo_set):
    """編輯目標 → repo 相對路徑;在 repo(含 worktree)之外回 None(不建列)。"""
    p = os.path.normpath(str(fp or ""))
    if not p or p == ".":
        return None
    if not os.path.isabs(p):
        return None if p.startswith("..") else p
    for r in sorted(repo_set, key=len, reverse=True):
        if p.startswith(r + os.sep):
            return p[len(r) + 1:]
    return None


def _ts_epoch(ts) -> float | None:
    try:
        return _dt.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def _iso_week_local(ts) -> str | None:
    """逐字稿時間是 UTC;換成本機時區再算 ISO 週(跟 shell 端 date +%G-W%V 同一個時區)。"""
    t = _ts_epoch(ts)
    if t is None:
        return None
    y, w, _ = _dt.datetime.fromtimestamp(t).isocalendar()   # 不帶 tz 的 fromtimestamp=本機時區
    return f"{y}-W{w:02d}"


def _effective_ts(objs) -> list:
    """每一行的時間:缺時間的行沿用同一份逐字稿前一行的時間(計劃 S4;代碼審 r1 外家 C7);前面都沒有 → None(不收、計數)。"""
    out, last = [], None
    for o in objs:
        t = o.get("timestamp") if isinstance(o, dict) else None
        if t:
            last = t
        out.append(last)
    return out


def _tool_results(objs) -> dict:
    """tool_use_id → (是否錯誤, 輸出文字)。"""
    out = {}
    for o in objs:
        if not isinstance(o, dict) or o.get("type") != "user":
            continue
        content = (o.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for it in content:
            if isinstance(it, dict) and it.get("type") == "tool_result":
                c = it.get("content")
                txt = c if isinstance(c, str) else "\n".join(str(x.get("text", "")) if isinstance(x, dict) else str(x) for x in (c or []))
                err = bool(it.get("is_error")) or txt.lstrip().startswith("<tool_use_error>")
                out[it.get("tool_use_id")] = (err, txt)
    return out


def _resolve_terms(terms, node_index) -> tuple[set, set]:
    """lumos context/show/contracts 的詞 → 節點(完整路徑直接用;裸名在節點清單裡唯一才認,不唯一記 ambiguous)。"""
    hit, amb = set(), set()
    if not node_index:
        return hit, amb
    for t in terms:
        if "/" in t:
            n = t if t.endswith(".md") else t + ".md"
            if n in node_index["paths"]:
                hit.add(n)
            continue
        c = node_index["stems"].get(t[:-3] if t.endswith(".md") else t, [])
        if len(c) == 1:
            hit.add(c[0])
        elif len(c) > 1:
            amb.update(c)
    return hit, amb


def analyze_claude(objs, slug, repo_set, hook_ok, node_index=None) -> dict:
    """一份 Claude 逐字稿 → 事件:edits(只取 hook 會處理的檔)、pushes(toolUseID → parse_push)、reads(讀成功的節點)。
    事件先後=(行序, 同一則訊息裡第幾個工具呼叫):同一則訊息先改檔再讀筆記,讀取排在那次編輯之後(代碼審 r1 單reviewer A1);
    時間用 _effective_ts(缺時間的行沿用前一行)。"""
    results = _tool_results(objs)
    ts_of = _effective_ts(objs)
    edits, pushes, reads = [], {}, []
    for idx, o in enumerate(objs):
        if not isinstance(o, dict):
            continue
        att = o.get("attachment") if isinstance(o.get("attachment"), dict) else None
        if att and att.get("type") == "hook_additional_context" and att.get("hookName") in HOOKS and att.get("toolUseID"):
            pushes[att["toolUseID"]] = parse_push(att.get("content"))
            continue
        if o.get("type") != "assistant":
            continue
        for pos, it in enumerate((o.get("message") or {}).get("content") or []):
            if not (isinstance(it, dict) and it.get("type") == "tool_use"):
                continue
            name, inp, tid, at, ts = it.get("name"), (it.get("input") or {}), it.get("id"), (idx, pos), ts_of[idx]
            if name in ("Edit", "Write", "MultiEdit"):
                rel = _rel_to_repo(inp.get("file_path"), repo_set)
                if rel and hook_ok(rel):
                    edits.append({"idx": at, "ts": ts, "id": tid, "files": [rel]})
            elif name == "Read":
                n = norm_note(str(inp.get("file_path", "")), slug)
                err = results.get(tid, (True, ""))[0]
                if n and not err:
                    reads.append({"idx": at, "ts": ts, "node": n})
            elif name == "Bash":
                strict, _lo, _w, terms, _s = classify_bash(str(inp.get("command", "")), slug)
                hit, _amb = _resolve_terms(terms, node_index)
                for n in sorted(strict | hit):
                    reads.append({"idx": at, "ts": ts, "node": n})
    return {"edits": edits, "pushes": pushes, "reads": reads}


def build_miss_rows(ev, relate, existed, session, harness, ttl_sec: float = 1200.0) -> list[dict]:
    """事件 → 每支被改的檔一列。每筆讀取只算一次:往前找最近一次「跟這篇有關」的編輯,都沒有才給最近一次;
    讀的是那支檔看得到的推播 → 記進 used(推了、之後讀了);那次編輯之前(同一份逐字稿)就讀過的不算;編輯當下還不存在的另計 after_the_fact。
    列上存 pushed(看得到的推播節點)與 used,週檔答得出「推了哪些、之後讀了哪些」(計劃 S4;代碼審 r1 外家 C1)。
    ★冷卻窗逐檔算★(實作時真資料發現:W36 零推播 81%):hook 對一支檔真的推過(開窗)之後,冷卻窗內(ttl_sec,預設 20 分)再改
    只跑事故快速路、不重推整份,也不延長窗——那支檔這次看得到的=開窗那次的推播 ∪ 窗內快速路推的(cooldown_inherited),
    窗外沒推才算零推播。hook 的冷卻記號本來就逐檔,所以多檔 patch 裡只有真的在窗內的檔沿用(代碼審 r1 外家 C2);
    窗內這次自己也有推播(事故快速路)照樣併上開窗那次(代碼審 r1 編排者重現時自找)。"""
    edits = sorted(ev["edits"], key=lambda e: e["idx"])
    sh = _hashlib.sha256(str(session).encode("utf-8")).hexdigest()[:12]
    rows, seen, win = {}, {}, {}   # seen:(編輯, 檔) 看得到的節點;win:檔 → 冷卻窗(開窗時間、窗內累計看過的節點、清單完整否)
    for e in edits:
        real, t = ev["pushes"].get(e["id"]), _ts_epoch(e["ts"])
        for f in e["files"]:
            w = win.get(f)
            in_cd = w is not None and t is not None and 0 <= t - w["t0"] < ttl_sec
            nodes = set(real["nodes"]) if real else set()
            complete = bool(real["complete"]) if real else True
            if in_cd:
                nodes |= w["nodes"]; complete = complete and w["complete"]
                w["nodes"], w["complete"] = set(nodes), complete
            elif real is not None and t is not None:
                win[f] = {"t0": t, "nodes": set(nodes), "complete": complete}
            seen[(e["idx"], f)] = nodes
            rows[(e["idx"], f)] = {"session": sh, "harness": harness, "ts": e["ts"], "file": f,
                                   "zero_push": real is None and not in_cd, "cooldown_inherited": in_cd,
                                   "pushed_n": len(nodes), "pushed": sorted(nodes), "used": [],
                                   "pushed_complete": bool(complete and e.get("pair_ok", True)),
                                   "impact_skipped": bool(real and f in real["impact_skipped"]),
                                   "misses": [], "after_the_fact": []}
    for rd in sorted(ev["reads"], key=lambda r: r["idx"]):
        prior = [e for e in edits if e["idx"] < rd["idx"]]
        if not prior:
            continue
        target = None
        for e in reversed(prior):
            for f in e["files"]:
                if relate(rd["node"], f)[0]:
                    target = (e, f); break
            if target:
                break
        if target is None:
            target = (prior[-1], prior[-1]["files"][0])
        e, f = target
        row = rows[(e["idx"], f)]
        if rd["node"] in seen[(e["idx"], f)]:
            if rd["node"] not in row["used"]:
                row["used"].append(rd["node"])
            continue
        if any(r["node"] == rd["node"] and r["idx"] < e["idx"] for r in ev["reads"]):
            continue
        if any(m["node"] == rd["node"] for m in row["misses"]) or rd["node"] in row["after_the_fact"]:
            continue
        if not existed(rd["node"], e["ts"]):
            row["after_the_fact"].append(rd["node"]); continue
        cls, about_also = relate(rd["node"], f)
        row["misses"].append({"node": rd["node"], "class": cls or "unknown", "about_also": bool(about_also)})
    return [rows[k] for k in sorted(rows)]


def relate_from(impact, about, node, f) -> tuple:
    """(類別, about_also):impact 的 direct 或 incidents 有這篇 → 規則內(impact 會把帶事故觸發的直連節點從 direct 移到
    incidents,兩個都看);否則 about_code 含 F → 關於欄。impact 算不到(逾時/超預算=None)→ 一律判不出。"""
    if impact is None:
        return (None, False)
    ab = f in about.get(node, set())
    direct = {x.get("node") for x in (impact.get("direct") or [])} | {x.get("node") for x in (impact.get("incidents") or [])}
    if node in direct:
        return ("rule", ab)
    return ("about", False) if ab else (None, False)


_LUMOS_MOD = None


def _load_lumos_main():
    """借 lumos 本體的開頭欄位解析(split_frontmatter / parse_frontmatter / as_list / _posix_norm),about_code 跟 impact
    讀到的同一份(代碼審 r1 單reviewer A3、外家 C8:自己寫的正規式漏了單值寫法,真圖譜有兩篇這樣寫);載法同
    governance/eval/k1_stop_replay.py。懶載入:要讀 about_code 才載。"""
    global _LUMOS_MOD
    if _LUMOS_MOD is None:
        import importlib.util
        from importlib.machinery import SourceFileLoader
        p = Path(__file__).resolve().parents[3] / "scripts" / "lumos"
        loader = SourceFileLoader("lens_lumos_main", str(p)); spec = importlib.util.spec_from_loader("lens_lumos_main", loader)
        m = importlib.util.module_from_spec(spec); sys.modules["lens_lumos_main"] = m; loader.exec_module(m)
        _LUMOS_MOD = m
    return _LUMOS_MOD


def _about_map(vault: Path) -> dict:
    """節點 → about_code 路徑集合。清單與單值(`about_code: scripts/lumos`)照本體 parse_frontmatter + as_list 讀;
    本體把單行 `[a, b]` 整串當一個值,這裡多拆一步——量的是作者寫了哪些檔(真圖譜目前沒有非空的單行寫法)。"""
    lm = _load_lumos_main()
    norm = getattr(lm, "_posix_norm", lambda x: str(x).strip())
    out = {}
    for p in vault.rglob("*.md"):
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm, _body = lm.split_frontmatter(t)
        if fm is None:
            continue
        vals = []
        for v in lm.as_list(lm.parse_frontmatter(fm)[0].get("about_code")):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                vals += [lm.strip_quotes(x.strip()) for x in v[1:-1].split(",")]
            else:
                vals.append(v)
        vals = {norm(v) for v in vals if v.strip()}
        if vals:
            out[str(p.relative_to(vault))] = vals
    return out


def _node_index(vault: Path) -> dict:
    paths = {str(p.relative_to(vault)) for p in vault.rglob("*.md")}
    stems = {}
    for n in paths:
        stems.setdefault(n.rsplit("/", 1)[-1][:-3], []).append(n)
    return {"paths": paths, "stems": stems}


def _budget(seconds: float) -> dict:
    """整次執行共用一把總時間預算(計劃 S4:同 replay_weekly 的 BUDGET_SECONDS;代碼審 r1 外家 C5:原本只管 impact,
    git 子行程與掃逐字稿都沒上限):掃逐字稿、叫 impact、叫 git 都從同一個期限扣。"""
    return {"deadline": _time.monotonic() + float(seconds), "hit": False, "impact_timeouts": 0, "git_skipped": 0}


def _left(budget) -> float:
    return float("inf") if budget is None else budget["deadline"] - _time.monotonic()


def _make_relater(repo: Path, vault: Path, budget: dict | None = None, timeout: float = 60.0):
    """relate(node, F):每支 F 跑一次 `lumos impact --file F --json`(同一次執行內快取);每個子行程逾時 timeout 秒、
    也不超過預算剩下的時間;預算用完就不再叫——那些 F 記判不出(budget["hit"])。
    閉包記狀態,同 scripts/lumos 的記憶化寫法(代碼審 r1 架構席 B3)。"""
    about = _about_map(vault)
    lumos = Path(__file__).resolve().parents[3] / "scripts" / "lumos"
    cache = {}

    def impact(f):
        if f in cache:
            return cache[f]
        left = _left(budget)
        if left <= 0:
            budget["hit"] = True; cache[f] = None; return None
        data = None
        try:
            r = subprocess.run([sys.executable, str(lumos), "--vault", str(vault), "impact", "--file", f, "--json"],
                               cwd=str(repo), capture_output=True, text=True, timeout=min(timeout, max(1.0, left)))
            if r.returncode == 0:
                data = json.loads(r.stdout)
        except subprocess.TimeoutExpired:
            if budget is not None:
                budget["impact_timeouts"] += 1
        except Exception:
            data = None
        cache[f] = data
        return data

    return lambda node, f: relate_from(impact(f), about, node, f)


def _make_existence(repo: Path, vault: Path, budget: dict | None = None):
    """existed(node, ts):那篇筆記在編輯當下存不存在——git 最早加入時間(--follow,改名不洗掉)或檔案系統建立時間,任一早於編輯就算存在。
    只看 git 會錯排「早就寫好、還沒提交」的;只看建立時間會被重新 clone 洗成新的。兩個都查不到(檔已刪)當作存在。
    git 也吃總預算:用完就不叫 git(git_skipped 計數)、一律當存在——只剩建立時間不足以判「事後才有」(新 clone 會把它洗成新的,
    漏網會整批掉進事後才有而消失);那篇的分類多半也記判不出(impact 吃同一把預算),照計劃「剩下的記判不出」。"""
    cache = {}

    def existed(node, ts):
        t = _ts_epoch(ts)
        if t is None:
            return True
        if node not in cache:
            left = _left(budget)
            if left <= 0:
                budget["hit"] = True; budget["git_skipped"] += 1
                cache[node] = None
            else:
                git_t = birth = None
                try:
                    rel = str((vault / node).relative_to(repo))
                    out = subprocess.run(["git", "-C", str(repo), "log", "--follow", "--diff-filter=A", "--format=%ct", "--", rel],
                                         capture_output=True, text=True, timeout=min(20.0, max(1.0, left))).stdout.split()
                    git_t = min(int(x) for x in out) if out else None
                except Exception:
                    pass
                try:
                    birth = getattr(os.stat(vault / node), "st_birthtime", None)
                except OSError:
                    pass
                cache[node] = (git_t, birth)
        if cache[node] is None:
            return True
        git_t, birth = cache[node]
        if git_t is None and birth is None:
            return True
        return (git_t is not None and git_t <= t) or (birth is not None and birth <= t)

    return existed


SEARCH_RANKED = re.compile(r"(?m)^\((?:共 (\d+) 篇候選|候選 (\d+);)")        # 現行「(共 N 篇候選」與舊版「(候選 N;」
SEARCH_RESULT_LINE = re.compile(r"(?m)^\s+\d+(?:\.\d+)?\s+(?:[^\s/]+/)+\S*?\.md\b")    # 排名結果行「  11.902  Projects/x.md」
SEARCH_LEGACY = re.compile(r"(?m)^(\d+) 處 / (\d+) 篇")
_Q_HIDE = str.maketrans({";": "\x00", "&": "\x01", "|": "\x02", "\n": "\x03"})
_Q_SHOW = str.maketrans({"\x00": ";", "\x01": "&", "\x02": "|", "\x03": "\n"})
_REDIRECT_TOKS = ("2>", "1>", "&>", ">", "<")
_CONTINUATION_RE = re.compile(r"\\\n[ \t]*")


def _search_segments(cmd: str) -> list[list[str]]:
    """一次呼叫裡每段 lumos search 的查詢詞。切段沿用 hook 的 _segment_command(; && || | 都切,管線後段本來就不含 search)、
    切詞沿用 _safe_tokens,不另寫第二套(代碼審 r1 架構席 B1);換行也是殼層的指令分隔,先逐行(代碼審 r1 外家 C6)。
    _segment_command 不看引號,所以引號內的 ; & | 換行先換成佔位字元,切完換回;反斜線接換行是續行、同一條指令,先接回再逐行
    (代碼審 r2 單reviewer D1:沒接回時 `lumos search \\` 換行接查詢詞,查詢詞只剩一個反斜線)。"""
    out = []
    cmd = _CONTINUATION_RE.sub(" ", cmd)
    for line in QUOTED_RE.sub(lambda m: m.group(0).translate(_Q_HIDE), cmd).split("\n"):
        for seg in _segment_command(line):
            toks = [w.translate(_Q_SHOW) for w in _safe_tokens(seg)]
            for i, tk in enumerate(toks):
                if os.path.basename(tk).endswith("lumos") and i + 1 < len(toks) and toks[i + 1] == "search":
                    terms = []
                    for w in toks[i + 2:]:
                        if w.startswith(_REDIRECT_TOKS):
                            break
                        if not w.startswith("-"):
                            terms.append(w)
                    out.append(terms)
                    break
    return out


def _search_verdict(text: str) -> str:
    t = str(text or "")
    for ln in t.splitlines():
        ln = ln.strip()
        if ln.startswith("{") and '"candidates"' in ln:
            try:
                d = json.loads(ln)
                return "zero" if int(d.get("candidates", -1)) == 0 else "hit"
            except Exception:
                pass
    try:
        d = json.loads(t)
        if isinstance(d, dict) and "candidates" in d:
            return "zero" if int(d["candidates"]) == 0 else "hit"
    except Exception:
        pass
    m = SEARCH_RANKED.search(t)
    if m:
        return "zero" if int(m.group(1) or m.group(2)) == 0 else "hit"
    m = SEARCH_LEGACY.search(t)
    if m:
        return "zero" if int(m.group(2)) == 0 else "hit"
    # 計數行常被 `| head -N` 切掉(它在最後一行);看得到排名結果行就是有命中。零命中只認明寫 0 的那一行,絕不從「沒有計數行」推論
    if SEARCH_RESULT_LINE.search(t):
        return "hit"
    return "undetermined"


def _search_event(cmd: str, output, bg: bool, ts) -> dict | None:
    segs = _search_segments(cmd)
    if not segs:
        return None
    q = " ".join(segs[0])
    if bg or len(segs) != 1 or output is None:
        return {"ts": ts, "query": q, "verdict": "undetermined"}
    return {"ts": ts, "query": q, "verdict": _search_verdict(output)}


def search_events_claude(objs) -> list[dict]:
    """Bash 呼叫裡的 lumos search 配它的輸出(tool_use id → tool_result);恰好一段含 search 才判,背景執行判不出。"""
    results = _tool_results(objs)
    ts_of = _effective_ts(objs)
    out = []
    for idx, o in enumerate(objs):
        if not isinstance(o, dict) or o.get("type") != "assistant":
            continue
        for it in ((o.get("message") or {}).get("content") or []):
            if isinstance(it, dict) and it.get("type") == "tool_use" and it.get("name") == "Bash":
                inp = it.get("input") or {}
                res = results.get(it.get("id"))
                ev = _search_event(str(inp.get("command", "")), res[1] if res else None, bool(inp.get("run_in_background")), ts_of[idx])
                if ev:
                    out.append(ev)
    return out


def analyze_codex(objs, slug, repo_set, hook_ok, node_index=None) -> tuple[dict, list]:
    """Codex rollout → (事件, 零命中事件)。編輯=apply_patch(一個 patch 可改多檔,推播是多塊合成一份→每支檔共用聯集);
    推播附件沒有呼叫編號,沿用既有做法配同一輪最近的 apply_patch;同一輪有兩個以上 apply_patch → 那幾列配不準、不猜。
    事件先後=(行序, 在那次呼叫程式碼裡的位置):同一次呼叫先 apply_patch 再 exec 讀筆記,讀取排在編輯之後(代碼審 r1 單reviewer A1)。"""
    edits, pushes, reads, searches = [], {}, [], []
    ts_of = _effective_ts(objs)
    outputs = {}
    for o in objs:
        if not isinstance(o, dict):
            continue
        p = o.get("payload") or {}
        if o.get("type") == "response_item" and p.get("type") == "custom_tool_call_output":
            outv = p.get("output")
            outputs[p.get("call_id")] = outv if isinstance(outv, str) else "\n".join(
                str(x.get("text", "")) if isinstance(x, dict) else str(x) for x in (outv or []))
    turn, turn_of, patches_in_turn = 0, {}, collections.Counter()
    for idx, o in enumerate(objs):
        if not isinstance(o, dict):
            continue
        p = o.get("payload") or {}
        if (o.get("type") == "event_msg" and p.get("type") == "user_message") or \
           (o.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "user"):
            turn += 1
        turn_of[idx] = turn
        if o.get("type") != "response_item" or p.get("type") != "custom_tool_call":
            continue
        inp = p.get("input") if isinstance(p.get("input"), str) else ""
        ts = ts_of[idx]
        files, first = [], None
        for m in _CODEX_APPLY_PATCH_RE.finditer(inp):
            for ln2 in _js_unescape(m.group(1)).split("\n"):
                h = _CODEX_PATCH_HDR_RE.match(ln2.strip())
                if h:
                    rel = _rel_to_repo(h.group(1).strip(), repo_set)
                    if rel and hook_ok(rel) and rel not in files:
                        files.append(rel)
                        first = m.start() if first is None else first
        if files:
            edits.append({"idx": (idx, first), "ts": ts, "id": f"cx{idx}", "files": files, "turn": turn})
            patches_in_turn[turn] += 1
        cmds = [(m.start(), _js_unescape(m.group(1))) for m in _CODEX_EXEC_CMD_RE.finditer(inp)]
        for at, cmd in cmds:
            strict, _lo, _w, terms, _s = classify_bash(cmd, slug)
            hit, _amb = _resolve_terms(terms, node_index)
            for n in sorted(strict | hit):
                reads.append({"idx": (idx, at), "ts": ts, "node": n})
        segs_total = sum(len(_search_segments(c)) for _at, c in cmds)
        for _at, cmd in cmds:
            if _search_segments(cmd):
                ev = _search_event(cmd, outputs.get(p.get("call_id")) if (len(cmds) == 1 and segs_total == 1) else None, False, ts)
                if ev:
                    searches.append(ev)
    for e in edits:
        e["pair_ok"] = patches_in_turn[e["turn"]] <= 1
    for idx, o in enumerate(objs):
        if not isinstance(o, dict):
            continue
        p = o.get("payload") or {}
        if o.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "developer":
            txt = _codex_text(p)
            if not _is_push_text(txt):
                continue
            same = [e for e in edits if e["turn"] == turn_of[idx]]
            if not same:
                continue
            e = min(same, key=lambda e: abs(e["idx"][0] - idx))
            pushes[e["id"]] = parse_push(txt)
    return {"edits": edits, "pushes": pushes, "reads": reads}, searches


def _hook_filter(repo: Path):
    """用 impact hook 自己的判斷函式決定哪些檔會被推播(文件、排除路徑 hook 本來就不管,不建列)。"""
    import importlib.util
    from importlib.machinery import SourceFileLoader
    hook = Path(__file__).resolve().parents[3] / "scripts" / "hooks" / "claude" / "impact-hook.py"
    loader = SourceFileLoader("lens_impact_hook", str(hook)); spec = importlib.util.spec_from_loader("lens_impact_hook", loader)
    mod = importlib.util.module_from_spec(spec); loader.exec_module(mod)
    return lambda rel: bool(mod._decide_one(rel, str(repo)))


def run_misses(repo: Path, projects: str, codex_sessions: str, week: str | None = None,
               budget: float = 300.0, impact_timeout: float = 60.0) -> dict:
    """掃逐字稿 → {rows, searches, summary, budget_hit}。給 week 就只收編輯時間(本機時區)落在那個 ISO 週的列與搜尋。
    兩段走、共用一把總預算(代碼審 r1 外家 C5):先掃完逐字稿收事件(純讀檔)——預算用完就不再開新檔、沒掃的計數
    files_unscanned;再逐份叫 impact / git 分類——預算用完就不再叫,剩下的記判不出。兩種都標 budget_hit,資料不完整但有標記。"""
    repo = repo.resolve(); slug = vault_slug(repo)
    if not slug:
        raise SystemExit("擋下:repo 下找不到 docs/*-knowledge")
    vault = repo / "docs" / slug
    repo_set = repo_paths(repo)
    idx_nodes = _node_index(vault)
    hook_ok = _hook_filter(repo)
    bud = _budget(budget)
    relate, existed = _make_relater(repo, vault, bud, impact_timeout), _make_existence(repo, vault, bud)
    ttl_min = 20   # hook 的冷卻窗:同 impact-hook 讀 .lumos/impact.json 的 ttl_min(預設 20 分)
    try:
        ttl_min = max(1, int(json.loads((repo / ".lumos" / "impact.json").read_text(encoding="utf-8")).get("ttl_min", 20)))
    except Exception:
        pass
    in_week = (lambda ts: _iso_week_local(ts) == week) if week else (lambda ts: True)
    files = [("claude", f) for f in glob.glob(os.path.join(projects, "*", "*.jsonl")) + glob.glob(os.path.join(projects, "*", "*", "subagents", "agent-*.jsonl"))]
    if os.path.isdir(codex_sessions):
        files += [("codex", f) for f in glob.glob(os.path.join(codex_sessions, "**", "rollout-*.jsonl"), recursive=True)]
    C = collections.Counter
    sessions, searches, cnt = [], [], C()
    for harness, f in files:
        if _left(bud) <= 0:
            bud["hit"] = True; cnt["files_unscanned"] += 1; continue
        try:
            objs, bad = _read_jsonl(f)
            cnt["bad_lines"] += bad
            if harness == "claude":
                if not _claude_in_repo(objs, repo_set):
                    continue
                ev, sx = analyze_claude(objs, slug, repo_set, hook_ok, idx_nodes), search_events_claude(objs)
                sid = next((o.get("sessionId") for o in objs if isinstance(o, dict) and o.get("sessionId")), Path(f).stem)
            else:
                meta, why = _codex_meta(objs, f, repo_set)
                if meta is None:
                    cnt["codex_version_skipped"] += why == "version"
                    continue
                ev, sx = analyze_codex(objs, slug, repo_set, hook_ok, idx_nodes)
                sid = meta.get("session_id") or Path(f).stem
            cnt["edits_without_time"] += sum(1 for e in ev["edits"] if e["ts"] is None)
            if any(in_week(e["ts"]) for e in ev["edits"]):
                sessions.append((ev, sid, harness))
            searches += [s for s in sx if in_week(s["ts"])]
        except SystemExit:
            raise
        except Exception as e:
            cnt["broken_files"] += 1; print(f"跳過 {f}: {type(e).__name__}", file=sys.stderr)
    rows = []
    for ev, sid, harness in sessions:
        try:
            rows += [r for r in build_miss_rows(ev, relate, existed, sid, harness, ttl_min * 60) if in_week(r["ts"])]
        except Exception as e:
            cnt["broken_files"] += 1; print(f"跳過一個 {harness} 工作階段的分類: {type(e).__name__}", file=sys.stderr)
    ok_rows = [r for r in rows if r["pushed_complete"]]
    summary = {
        "week": week, "files_scanned": len(files) - cnt["files_unscanned"], "files_unscanned": cnt["files_unscanned"],
        "broken_files": cnt["broken_files"], "bad_lines": cnt["bad_lines"], "codex_version_skipped": cnt["codex_version_skipped"],
        "edits_without_time": cnt["edits_without_time"], "rows": len(rows),
        "zero_push_rows": sum(1 for r in rows if r["zero_push"]), "cooldown_rows": sum(1 for r in rows if r.get("cooldown_inherited")),
        "incomplete_rows": len(rows) - len(ok_rows),
        "miss_by_class": dict(C(m["class"] for r in ok_rows for m in r["misses"])),
        "about_also": sum(1 for r in ok_rows for m in r["misses"] if m["about_also"]),
        "after_the_fact": sum(len(r["after_the_fact"]) for r in rows),
        "searches": len(searches), "search_zero": sum(1 for s in searches if s["verdict"] == "zero"),
        "search_undetermined": sum(1 for s in searches if s["verdict"] == "undetermined"),
        "impact_timeouts": bud["impact_timeouts"], "git_skipped": bud["git_skipped"], "budget_hit": bud["hit"],
    }
    return {"rows": rows, "searches": searches, "summary": summary, "budget_hit": bud["hit"]}


def _atomic_json(path: Path, data) -> None:
    """寫暫存(pid 尾碼,同 refresh_labels._atomic_write_json)→ 讀回自驗 → os.replace。比鄰居多一步讀回:週檔是版控產物,
    寫壞的檔換上去就會被提交出去(本 repo 改共用檔的原子寫入慣例:寫暫存→自驗→換名)。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    text = json.dumps(data, ensure_ascii=False, indent=1)
    tmp.write_text(text, encoding="utf-8")
    json.loads(tmp.read_text(encoding="utf-8"))
    os.replace(tmp, path)


def write_archive(rep: dict, week: str, archive_dir: Path) -> tuple[Path, Path]:
    """版控那份 weekly/<週>.json 只放推導列(工作階段雜湊、repo 相對檔名、節點名、分類、計數);
    查詢字串另寫 local/<週>-queries.json(那個目錄 gitignore——agent 打的自由文字不進公開 repo)。同週重跑覆寫同一份。"""
    arc = Path(archive_dir)
    weekly = arc / "weekly" / f"{week}.json"
    local = arc / "local" / f"{week}-queries.json"
    _atomic_json(weekly, {"week": week, "summary": rep["summary"], "budget_hit": rep["budget_hit"], "rows": rep["rows"]})
    _atomic_json(local, {"week": week, "zero_hit_queries": sorted({s["query"] for s in rep["searches"] if s["verdict"] == "zero"}),
                         "undetermined": sum(1 for s in rep["searches"] if s["verdict"] == "undetermined")})
    return weekly, local


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
