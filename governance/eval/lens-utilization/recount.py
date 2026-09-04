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
REDIRECT_RE = re.compile(r">>?\s*(\S+)")
HEREDOC_RE = re.compile(r"<<-?\s*['\"]?\w+")
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
    t = os.path.normpath(tok.replace("\\", "/").strip("'\"`,;:"))
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


def classify_bash(cmd: str, slug: str) -> tuple[set[str], set[str], set[str], set[str]]:
    """回 (讀到的節點, 寫回的節點, lumos context/show/contracts 的詞, search 的詞)。
    寫回=重導向到筆記 / sed -i / heredoc 腳本裡該路徑附近有 write_text;讀=讀動詞帶筆記路徑 / 腳本裡該路徑附近有 read_text|open。
    純拼字串提到路徑(commit message 之類)兩者都不算。切段/切詞沿用 check-graph-sync。"""
    import shlex
    read, wrote, lumos_terms, search_terms = set(), set(), set(), set()
    if HEREDOC_RE.search(cmd):
        lines = cmd.split("\n")
        for k, ln in enumerate(lines):
            for tok in TOKEN_RE.findall(ln):
                n = norm_note(tok, slug)
                if not n:
                    continue
                window = "\n".join(lines[k:k + 4])
                if "read_text" in window or "open(" in window and (".read" in window or "'r'" in window or '"r"' in window):
                    read.add(n)
                if "write_text" in window or "open(" in window and ("'w'" in window or '"w"' in window or "'a'" in window or '"a"' in window):
                    wrote.add(n)
                for m in REDIRECT_RE.finditer(ln):
                    n2 = norm_note(m.group(1), slug)
                    if n2:
                        wrote.add(n2)
        return read, wrote, lumos_terms, search_terms
    for seg in _segment_command(cmd):
        for m in REDIRECT_RE.finditer(seg):
            n2 = norm_note(m.group(1), slug)
            if n2:
                wrote.add(n2)
        st = _tokens_of(seg)
        if not st:
            continue
        j = 0
        while j < len(st) and ("=" in st[j] and not st[j].startswith("-")):
            j += 1
        if j >= len(st):
            continue
        verb = os.path.basename(st[j]); args = st[j + 1:]
        if verb == "sed" and any(a == "-i" or a.startswith("-i") for a in args):
            for a in args:
                n = norm_note(a, slug)
                if n: wrote.add(n)
        elif verb in READ_VERBS:
            for a in args:
                n = norm_note(a, slug)
                if n: read.add(n)
        elif verb.endswith("lumos") and args:
            sub = args[0]
            try:
                raw = shlex.split(seg)
            except ValueError:
                raw = st
            terms = [a for a in raw[raw.index(sub) + 1:] if not a.startswith("-")] if sub in raw else [a for a in args[1:] if not a.startswith("-")]
            if sub in LUMOS_CMDS:
                lumos_terms.update(terms); lumos_terms.add("".join(terms))
            elif sub == "search":
                search_terms.update(terms); search_terms.update(w for t2 in terms for w in t2.split())
    return read, wrote, lumos_terms, search_terms


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
               "anchored": anchor is not None, "ftype": ftype, "touched": [], "pre_touched": [], "wrote_back": [], "search_touched": [], "ambiguous": []}
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
                    hit_read, hit_write, terms, sterms = set(), set(), set(), set()
                    if it.get("name") == "Read":
                        n = norm_note(str((it.get("input") or {}).get("file_path", "")), slug)
                        if n: hit_read.add(n)
                    elif it.get("name") == "Bash":
                        hit_read, hit_write, terms, sterms = classify_bash(str((it.get("input") or {}).get("command", "")), slug)
                    for t in terms:
                        if t in stems:
                            if len(stems[t]) == 1: hit_read.add(stems[t][0])
                            else:
                                for pth in stems[t]:
                                    if pth not in row["ambiguous"]: row["ambiguous"].append(pth)
                    bucket = row["touched"] if j > anchor[0] else row["pre_touched"]
                    for n in hit_read & pinset:
                        if n not in bucket: bucket.append(n)
                    for n in hit_write & pinset:
                        if j > anchor[0] and n not in row["wrote_back"]: row["wrote_back"].append(n)
                    for t in sterms:
                        for s, plist in stems.items():
                            for p in plist:
                                if t and t in s and p not in row["search_touched"] and j > anchor[0]:
                                    row["search_touched"].append(p)
        row["any"] = bool(row["touched"])
        rows.append(row)
    return rows, bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True); ap.add_argument("--projects", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--json", action="store_true"); ap.add_argument("--out")
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
    C = collections.Counter
    denom = [r for r in rows if r["n_pinned"] > 0 and r["ftype"] != "scratch" and r["anchored"]]
    rep = {
        "files_scanned": len(files), "bad_lines": bad, "broken_files": broken, "pushes_total": len(rows),
        "by_role": dict(C("sub" if r["is_subagent"] else "main" for r in rows)),
        "by_header": dict(C(r["header_version"] for r in rows)),
        "empty_pinned": sum(1 for r in rows if r["n_pinned"] == 0), "unanchored": sum(1 for r in rows if not r["anchored"]),
        "scratch_or_outside": sum(1 for r in rows if r["ftype"] == "scratch"), "pinned_incomplete": sum(1 for r in rows if not r["pinned_complete"]),
        "denominator": len(denom),
        "n_pinned_dist": dict(sorted(C(r["n_pinned"] for r in denom).items())),
        "any_by_ftype": {k: {"n": v, "any": sum(1 for r in denom if r["ftype"] == k and r["any"])} for k, v in C(r["ftype"] for r in denom).items()},
        "any_by_pinned_bucket": {k: {"n": v, "any": sum(1 for r in denom if _bucket(r["n_pinned"]) == k and r["any"])} for k, v in C(_bucket(r["n_pinned"]) for r in denom).items()},
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
         "推送後有碰到任一篇 pinned(any)——★分型讀,不合併★:"]
    for k, v in rep["any_by_pinned_bucket"].items():
        L.append(f"  |pinned| {k}:{v['n']} 次,any {v['any']}")
    for k, v in rep["any_by_ftype"].items():
        L.append(f"  檔型 {k}:{v['n']} 次,any {v['any']}")
    L.append(f"另列:推送前已碰 {rep['pre_touched_rows']}、只寫回未讀 {rep['wrote_back_rows']}、search 碰(弱證據) {rep['search_touched_rows']}")
    L.append(f"session 叢聚:{rep['sessions']}")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
