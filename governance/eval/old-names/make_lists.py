#!/opt/homebrew/bin/python3
"""把參考實作的發現分三層寫成待處理清單(給人或模型逐筆修):
①已逐筆判過、判真或灰 ②過濾最嚴(F1+F2+F3+B)但沒判過 ③其餘 F1+F2(只當參考)。已判「不是」的不列。
用法: make_lists.py <名> <repo> <tip> <vault>"""
import json, sys
sys.path.insert(0, ".")
import oldnames_ref as R
name, repo, tip, vault = sys.argv[1:5]
M = R.load()
env = M._drift_tree_env(repo, tip, vault)
rows = [json.loads(l) for l in open(f"out/{name}.findings.jsonl")]
J = {}
_jp = f"out/{name}.judge.tsv"
for ln in (open(_jp) if __import__("os").path.exists(_jp) else ()):
    p = ln.rstrip("\n").split("\t")
    if p and p[0].isdigit():
        J[int(p[0])] = (p[8], p[10] if len(p) > 10 else "")
def meta(r):
    n = env.notes[r["path"]]
    return M._drift_str(n, "type"), M._drift_str(n, "status")
def f12(r):
    t, s = meta(r)
    return s not in ("superseded", "archived", "stale") and t != "verification"
def f123b(r):
    t, s = meta(r)
    return f12(r) and not (t == "project" and s == "done" and r["layer_reason"] != "summary") and r["B"]
tiers = {1: [], 2: [], 3: []}
for i, r in enumerate(rows):
    if i in J:
        if J[i][0] in ("真", "灰"):
            tiers[1].append((i, r, J[i]))
    elif f123b(r):
        tiers[2].append((i, r, None))
    elif f12(r):
        tiers[3].append((i, r, None))
title = {1: "已逐筆判過:真或灰(先修這層)", 2: "過濾最嚴那版列出、還沒判過(照同一標準自己判)", 3: "其餘(誤報多,有空再看)"}
out = [f"# {name} 存量舊名清單(量測點 {tip[:8]})", "",
       "每筆 = 筆記裡還在講、但程式裡已經刪掉的名稱。判準:讀的人照這句去找會找不到東西或做錯事 = 該改;句子本身在講歷史 = 不用改(或補歷史字眼)。", ""]
for k in (1, 2, 3):
    out += [f"## 第 {k} 層:{title[k]}({len(tiers[k])} 筆)", ""]
    for i, r, j in tiers[k]:
        names = "、".join(f"`{n}`" for n in r["names"])
        extra = f" — 判{j[0]}:{j[1]}" if j else ""
        out.append(f"- `{r['path']}:{r['line']}` 名稱 {names}(消失於 {'、'.join(sorted({m['vanish'][:8] for m in r['meta'].values()}))},原在 {'、'.join(sorted({o for m in r['meta'].values() for o in m['origins']}))}){extra}")
        out.append(f"  > {r['text'][:240]}")
    out.append("")
open(f"out/{name}.todo.md", "w").write("\n".join(out))
print(name, {k: len(v) for k, v in tiers.items()})
