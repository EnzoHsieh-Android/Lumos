#!/opt/homebrew/bin/python3
"""rtb 對 2026-09-28 量測點:稽核 20 處逐處看 A/B 有沒有列到;沒列到的診斷原因(needle 所在行有沒有消失名稱、被哪條過濾擋)。"""
import os
import json, sys, subprocess
sys.path.insert(0, ".")
import oldnames_ref as R
M = R.load()
GT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "stale-ref", "groundtruth.json")
root, tip, vault = "rtb", "c4daa8fce2cdd3f22dc703313d5928195adfeb1a", "docs/rtb-production-agent-demo-knowledge"
rows = [json.loads(l) for l in open("out/rtb.findings.jsonl")]
gone = json.load(open("out/rtb.gone.json"))
names = set(gone)
idx = M._drift_m1_name_index(names)
out = []
for g in json.load(open(GT)):
    text = subprocess.run(["git", "-C", root, "show", f"{tip}:{vault}/{g['note']}"], capture_output=True).stdout.decode("utf-8-sig")
    lines = text.split("\n")
    regs = M._notelines_regions(text)
    vis = {i for i, _ in M._visible_lines(lines)}
    ret = M._drift_m1_retired(lines, regs, vis)
    hit_lines = sorted({i + 1 for i, ln in enumerate(lines) for nd in g["needles"] if nd in ln})
    A = [r for r in rows if r["path"] == g["note"] and r["line"] in hit_lines]
    B = [r for r in A if r["B"]]
    diag = []
    for ln_no in hit_lines:
        ln = lines[ln_no - 1]
        raw = M._drift_m1_line_names(idx, ln)
        rx = M._drift_m1_name_rx(raw) if raw else None
        whole = sorted({m.group(0) for m in rx.finditer(ln)}) if rx else []
        cl = M._DriftM1Clauses(ln)
        hist = sorted({m.group(0) for m in rx.finditer(ln) if cl.hist(m.start())}) if rx else []
        diag.append({"line": ln_no, "region": regs[ln_no - 1], "visible": ln_no in vis, "retired": ret[ln_no],
                     "gone_names_in_line": whole, "hist_filtered": hist, "text": ln.strip()[:200]})
    out.append({"id": g["id"], "note": g["note"], "A": bool(A), "B": bool(B),
                "A_names": sorted({n for r in A for n in r["names"]}), "B_names": sorted({n for r in B for n in r["B_names"]}),
                "needle_lines": hit_lines, "diag": diag})
json.dump(out, open("out/rtb.recall.json", "w"), ensure_ascii=False, indent=1)
for o in out:
    print(o["id"], "A" if o["A"] else "-", "B" if o["B"] else "-", o["A_names"], o["needle_lines"],
          [(d["line"], d["region"], d["retired"], d["gone_names_in_line"], d["hist_filtered"]) for d in o["diag"]])
print("A:", sum(o["A"] for o in out), "B:", sum(o["B"] for o in out))
