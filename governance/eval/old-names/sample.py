#!/opt/homebrew/bin/python3
"""抽樣(固定種子 20260930):要處理層優先全抽(超過 30 就從要處理層抽 30),不夠從只列出層補到 30。
每筆做一份卷宗:那一行全文、名稱、消失提交的標題與刪除處 diff 片段、量測點全 repo 還有沒有這個字樣(grep -F)。"""
import json, random, subprocess, sys
repo, prefix, vault, tip = sys.argv[1:5]
rows = [json.loads(l) for l in open(f"{prefix}.findings.jsonl")]
for i, r in enumerate(rows):
    r["id"] = i
H = [r for r in rows if r["layer"] == "handle"]
L = [r for r in rows if r["layer"] != "handle"]
rng = random.Random(20260930)
if len(H) >= 30:
    smp = rng.sample(H, 30)
else:
    smp = H + rng.sample(L, min(30 - len(H), len(L)))


def g(*a):
    return subprocess.run(["git", "-C", repo, *a], capture_output=True).stdout.decode("utf-8", errors="replace")


with open(f"{prefix}.sample.dossier.txt", "w") as fh:
    for r in smp:
        fh.write(f"=== #{r['id']} {r['layer']}({r['layer_reason']}) B={r['B']} {r['path']}:{r['line']} blame={str(r['blame'])[:8]}\n")
        fh.write(f"TEXT: {r['text']}\n")
        for n in r["names"]:
            m = r["meta"][n]
            fh.write(f"  NAME {n} kinds={m['kinds']} vanish={m['vanish'][:8]} {g('log','-1','--format=%ci %s',m['vanish']).strip()}\n")
            fh.write(f"    origins={m['origins']}\n")
            d = g("show", "--format=", "-U0", m["vanish"], "--", *m["origins"])
            hits = [x for x in d.split("\n") if n in x][:4]
            for x in hits:
                fh.write(f"    diff: {x[:200]}\n")
            gr = g("grep", "-n", "-F", "-e", n, tip, "--", ".", f":!{vault}", ":!governance")
            gl = [x for x in gr.split("\n") if x][:3]
            fh.write(f"    tip-grep({len([x for x in gr.split(chr(10)) if x])}): {gl}\n")
        fh.write("\n")
json.dump([r["id"] for r in smp], open(f"{prefix}.sample.ids.json", "w"))
print(len(H), len(L), len(smp))
