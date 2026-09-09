#!/usr/bin/env python3
"""usage_scan:從本機 Claude Code 逐字稿(~/.claude/projects/<slug>/*.jsonl)量「token 花在哪」。

零依賴、唯讀。回答四個問題,每一段都印「這是什麼數字、為什麼在意」:
  A. 每次請求的 context 多大(token,去重後按 message.id 算,逐字稿一個 content block 一行、usage 會重複)
  B. 工具輸出直接進 context 的字元數,按工具、按 Bash 指令家族分
  C. 「駐留成本」= 字元數 × 之後還有幾次請求(壓縮點歸零)——進了 context 的東西每一輪都要再被讀一次
  D. Read / cat 類讀檔:命中 ≥N 行大檔的次數與字元(對照 Spotify shunt 的 350 行擋檔門檻)

用法:
    python3 scripts/usage_scan.py [--days 14] [--project-dir <逐字稿目錄>] [--min-lines 350] [--top 20]

出身:2026-09-09 吸收 Spotify Portal/shunt 調研(Projects/Spotify-shunt吸收_調研)——先量再裁要不要抄。
"""
import argparse
import glob
import json
import os
import re
import sys
import time
from collections import defaultdict


def _content_len(c):
    if isinstance(c, str):
        return len(c)
    if isinstance(c, list):
        return sum(len(x.get("text", "")) if isinstance(x, dict) else len(str(x)) for x in c)
    return len(str(c))


_READ_CMD = re.compile(r"^\s*(cat|sed -n|head|tail|less|more)\b")


def _family(cmd: str) -> str:
    c = cmd.strip()
    c = re.sub(r"^(cd\s+[^&;\n]+(&&|;)\s*)+", "", c)
    c = re.sub(r"^(\w+=\S+\s*(&&|;)?\s*)+", "", c)
    toks = c.split()
    if not toks:
        return "?"
    a, b = toks[0], (toks[1] if len(toks) > 1 else "")
    if a in ("scripts/lumos", "./scripts/lumos", "lumos"):
        return f"lumos {b}"
    if a == "python3" and b.endswith("test_lumos.py"):
        return "test_lumos.py"
    if a == "python3":
        return "python3 script/-c"
    if a == "git":
        return f"git {b}"
    return a[:18]


def _default_project_dir(cwd: str) -> str:
    slug = cwd.replace("/", "-")
    return os.path.expanduser(f"~/.claude/projects/{slug}")


def _nlines(path, cache):
    if path in cache:
        return cache[path]
    try:
        with open(path, "rb") as f:
            n = sum(1 for _ in f)
    except Exception:
        n = -1
    cache[path] = n
    return n


def scan(project_dir: str, days: int, min_lines: int):
    cut = time.time() - days * 86400
    files = sorted(f for f in glob.glob(os.path.join(project_dir, "*.jsonl")) if os.path.getmtime(f) > cut)
    tot = dict(input=0, cache_read=0, cache_create=0, output=0)
    prompts, firsts, after_compact = [], [], []
    by_tool = defaultdict(lambda: [0, 0])          # name -> [chars, calls]
    by_tool_res = defaultdict(int)
    by_fam = defaultdict(lambda: [0, 0])
    by_fam_res = defaultdict(int)
    sizes = defaultdict(list)
    asst_direct = asst_res = 0
    read_big = [0, 0]; read_small = [0, 0]; read_gone = 0   # [chars, calls]
    bash_read = [0, 0]
    read_targets = defaultdict(lambda: [0, 0])
    lines_cache = {}
    compact_markers = 0
    for f in files:
        seen = set(); first = None; pending_compact = False
        events = []; meta = {}
        with open(f, errors="replace") as _fh:   # code-反面詞 r1 單席 f6:原本裸 open 靠 refcount 關檔
            lines_ = list(_fh)
        for line in lines_:
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get("type"); m = d.get("message") or {}
            if d.get("isCompactSummary") or t == "summary":
                compact_markers += 1; pending_compact = True; events.append(("compact", None, 0)); continue
            if t == "assistant":
                L = 0
                for c in m.get("content") or []:
                    if not isinstance(c, dict):
                        continue
                    if c.get("type") == "tool_use":
                        meta[c["id"]] = (c.get("name"), c.get("input") or {})
                        L += len(json.dumps(c.get("input") or {}, ensure_ascii=False))
                    elif c.get("type") == "text":
                        L += len(c.get("text", ""))
                events.append(("turn", None, L))
                mid = m.get("id")
                if mid in seen:
                    continue
                seen.add(mid)
                u = m.get("usage") or {}
                p = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                if p:
                    prompts.append(p)
                    tot["input"] += u.get("input_tokens", 0); tot["cache_read"] += u.get("cache_read_input_tokens", 0)
                    tot["cache_create"] += u.get("cache_creation_input_tokens", 0); tot["output"] += u.get("output_tokens", 0)
                    if first is None:
                        first = p; firsts.append(p)
                    if pending_compact:
                        after_compact.append(p); pending_compact = False
            elif t == "user":
                for c in m.get("content") or []:
                    if not (isinstance(c, dict) and c.get("type") == "tool_result"):
                        continue
                    name, inp = meta.get(c.get("tool_use_id"), ("?", {}))
                    L = _content_len(c.get("content"))
                    fam = _family(inp.get("command", "")) if name == "Bash" else None
                    events.append(("result", (name, fam), L))
                    by_tool[name][0] += L; by_tool[name][1] += 1; sizes[name].append(L)
                    if name == "Bash":
                        by_fam[fam][0] += L; by_fam[fam][1] += 1
                        if _READ_CMD.match(inp.get("command", "")):
                            bash_read[0] += L; bash_read[1] += 1
                    elif name == "Read":
                        p = inp.get("file_path", "?"); n = _nlines(p, lines_cache)
                        read_targets[p][0] += L; read_targets[p][1] += 1
                        if n < 0:
                            read_gone += L
                        elif n >= min_lines:
                            read_big[0] += L; read_big[1] += 1
                        else:
                            read_small[0] += L; read_small[1] += 1
        # 駐留:每筆輸出 × 它之後(同一壓縮段內)還有幾次請求
        n = len(events); later = [0] * n; cnt = 0
        for i in range(n - 1, -1, -1):
            k = events[i][0]
            if k == "compact":
                cnt = 0
            later[i] = cnt
            if k == "turn":
                cnt += 1
        for i, (k, key, L) in enumerate(events):
            if k == "turn":
                asst_direct += L; asst_res += L * later[i]
            elif k == "result":
                name, fam = key
                by_tool_res[name] += L * later[i]
                if name == "Bash":
                    by_fam_res[fam] += L * later[i]
    return dict(files=files, tot=tot, prompts=prompts, firsts=firsts, after_compact=after_compact,
                by_tool=by_tool, by_tool_res=by_tool_res, by_fam=by_fam, by_fam_res=by_fam_res, sizes=sizes,
                asst_direct=asst_direct, asst_res=asst_res, read_big=read_big, read_small=read_small,
                read_gone=read_gone, bash_read=bash_read, read_targets=read_targets, lines_cache=lines_cache,
                compact_markers=compact_markers)


def _pct(a, b):
    return 100.0 * a / b if b else 0.0


def report(r, days, min_lines, top):
    out = []
    P = out.append
    ps = sorted(r["prompts"]); n = len(ps)
    P(f"逐字稿:{len(r['files'])} 個 session,{days} 天內有動;去重後請求 {n:,} 次;壓縮點 {r['compact_markers']} 次")
    if not n:
        P("沒有可算的請求(目錄空或逐字稿沒有 usage 欄位)。"); return "\n".join(out)
    t = r["tot"]
    P("")
    P("A. context 大小(每次請求送進模型的 token;快取讀取也算,因為每輪都要再讀一次)")
    P(f"   總量 input={t['input']:,} cache_read={t['cache_read']:,} cache_create={t['cache_create']:,} output={t['output']:,}")
    P(f"   每次請求 p50={ps[n//2]:,} p90={ps[int(n*.9)]:,} max={ps[-1]:,} 平均={sum(ps)//n:,}")
    fs = sorted(r["firsts"])
    P(f"   session 第一次請求(=固定底盤:系統提示+CLAUDE.md+skill+記憶)p50={fs[len(fs)//2]:,} max={fs[-1]:,}")
    ac = sorted(r["after_compact"])
    if ac:
        P(f"   壓縮後第一次請求 p50={ac[len(ac)//2]:,} max={ac[-1]:,}(n={len(ac)})")
    b = {"<100k": 0, "100-200k": 0, "200-400k": 0, ">=400k": 0}
    for p in ps:
        b["<100k" if p < 1e5 else "100-200k" if p < 2e5 else "200-400k" if p < 4e5 else ">=400k"] += p
    s = sum(b.values())
    P("   token 量按 context 大小分桶:" + "  ".join(f"{k} {_pct(v, s):.0f}%" for k, v in b.items()))
    P("   → 桶越靠右佔比越高,代表成本主要來自「session 拉得很長、context 很大」,而不是單筆輸出很大。")
    P("")
    P("B. 工具輸出直接進 context 的字元(≈ token×4;這是 Spotify shunt 省的那種)")
    tot_d = sum(v[0] for v in r["by_tool"].values()); tot_r = sum(r["by_tool_res"].values())
    P(f"   合計 {tot_d:,} 字元(≈{tot_d//4:,} token);模型自己的輸出(文字+工具參數)={r['asst_direct']:,} 字元")
    for k, (ch, calls) in sorted(r["by_tool"].items(), key=lambda x: -x[1][0])[:8]:
        P(f"   {k:<22} {ch:>11,} 字元 {_pct(ch, tot_d):5.1f}%  {calls:>6,} 次  駐留佔比 {_pct(r['by_tool_res'][k], tot_r):5.1f}%")
    P("")
    P("C. 駐留成本(字元 × 之後同一壓縮段內還有幾次請求)——誰真的貴")
    P(f"   模型自身輸出 {r['asst_res']:,}  vs  全部工具輸出 {tot_r:,}  → 比值 {r['asst_res']/max(tot_r,1):.2f}")
    P("   → 比值 >1 代表模型自己寫的東西(長腳本、長回覆)比工具吐回來的更佔 context。")
    P("   Bash 指令家族(直接字元 / 次數 / 平均 / 駐留佔比):")
    tot_b = sum(v[0] for v in r["by_fam"].values()); tot_br = sum(r["by_fam_res"].values())
    for k, (ch, calls) in sorted(r["by_fam"].items(), key=lambda x: -x[1][0])[:top]:
        P(f"   {k:<26} {ch:>10,} {calls:>5} 次 平均 {ch//max(calls,1):>6,}  駐留 {_pct(r['by_fam_res'][k], tot_br):4.1f}%")
    P("   單筆大小分布(看有沒有「一筆就很大」的輸出):")
    for name, ls in sorted(r["sizes"].items(), key=lambda x: -sum(x[1]))[:6]:
        ls.sort(); m = len(ls)
        P(f"   {name:<12} n={m:>6} max={ls[-1]:>7,} p50={ls[m//2]:>6,} p90={ls[int(m*.9)]:>6,} p99={ls[int(m*.99)]:>6,} >10k={sum(1 for x in ls if x>10000)}")
    P("")
    P(f"D. 讀檔命中 ≥{min_lines} 行大檔(Spotify 的擋檔門檻)")
    rd = r["by_tool"]["Read"][0]
    P(f"   Read 工具:≥{min_lines} 行 {r['read_big'][0]:,} 字元 / {r['read_big'][1]} 次;<{min_lines} 行 {r['read_small'][0]:,} 字元 / {r['read_small'][1]} 次;檔已不在 {r['read_gone']:,}")
    P(f"   Bash cat/sed -n/head/tail:{r['bash_read'][0]:,} 字元 / {r['bash_read'][1]} 次(平均 {r['bash_read'][0]//max(r['bash_read'][1],1):,};小=已經是定點讀)")
    P(f"   大檔讀取佔全部工具輸出:{_pct(r['read_big'][0], tot_d):.2f}%  ← 這個數字小,擋檔 hook 就沒得省")
    P("   Read 最花的檔(字元 / 次數 / 行數):")
    home = os.path.expanduser("~")
    for p, (ch, calls) in sorted(r["read_targets"].items(), key=lambda x: -x[1][0])[:top // 2]:
        P(f"   {ch:>10,} {calls:>3}x 行數={r['lines_cache'].get(p, -1):>6}  {p.replace(home, '~')}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--days", type=int, default=14, help="只看這幾天內有動的逐字稿(預設 14)")
    ap.add_argument("--project-dir", default=None, help="逐字稿目錄;預設從目前工作目錄推 ~/.claude/projects/<slug>")
    ap.add_argument("--min-lines", type=int, default=350, help="大檔門檻(行;預設 350,同 Spotify shunt)")
    ap.add_argument("--top", type=int, default=20)
    a = ap.parse_args(argv)
    pd = a.project_dir or _default_project_dir(os.getcwd())
    if not os.path.isdir(pd):
        print(f"找不到逐字稿目錄:{pd}\n用 --project-dir 指定 ~/.claude/projects/ 底下對應這個 repo 的資料夾。", file=sys.stderr)
        return 2
    print(report(scan(pd, a.days, a.min_lines), a.days, a.min_lines, a.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
