#!/opt/homebrew/bin/python3
"""判定原稿(編號 判定 誤報形狀 理由)接上發現資料 → <prefix>.judge.tsv,並印 A/B 兩版、兩層的計數。"""
import json, sys, collections
prefix = sys.argv[1]
rows = [json.loads(l) for l in open(f"{prefix}.findings.jsonl")]
J = {}
for ln in open(f"{prefix}.judge.raw.tsv"):
    if ln.strip():
        i, v, shape, why = ln.rstrip("\n").split("\t")
        J[int(i)] = (v, shape, why)
ids = json.load(open(f"{prefix}.sample.ids.json"))
assert set(ids) == set(J), (set(ids) ^ set(J))
with open(f"{prefix}.judge.tsv", "w") as fh:
    fh.write("編號\t層\t層理由\tB\t筆記:行\t名稱\t消失提交\tblame\t判定\t誤報形狀\t理由\n")
    for i in ids:
        r = rows[i]
        v, shape, why = J[i]
        fh.write("\t".join(map(str, [i, r["layer"], r["layer_reason"], "B" if r["B"] else "-", f"{r['path']}:{r['line']}",
                 "、".join(r["names"]), ",".join(sorted({r['meta'][n]['vanish'][:8] for n in r['names']})),
                 (r["blame"] or "")[:8], v, shape, why])) + "\n")
def cnt(sel):
    c = collections.Counter(J[i][0] for i in sel)
    return f"n={len(sel)} 真={c['真']} 灰={c['灰']} 不是={c['不是']}"
H = [i for i in ids if rows[i]["layer"] == "handle"]
L = [i for i in ids if rows[i]["layer"] != "handle"]
print("A 全樣本", cnt(ids)); print("A 要處理", cnt(H)); print("A 只列出(抽樣)", cnt(L))
print("B 全樣本∩B", cnt([i for i in ids if rows[i]["B"]]))
print("B 要處理∩B", cnt([i for i in H if rows[i]["B"]])); print("B 只列出∩B", cnt([i for i in L if rows[i]["B"]]))
print("B 排掉的", cnt([i for i in ids if not rows[i]["B"]]))
print("誤報形狀", collections.Counter(J[i][1] for i in ids if J[i][0] != "真"))
