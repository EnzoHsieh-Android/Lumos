#!/opt/homebrew/bin/python3
"""把 20 處真漂移對到段落,列每個變體標到沒。輸出 out/recall.json 與人讀的 out/recall.txt。"""
import json, subprocess, sys
EXP = sys.argv[1]
paras = [json.loads(l) for l in open(f"{EXP}/out/paragraphs.jsonl")]
gt = json.load(open(f"{EXP}/groundtruth.json"))
REPO = f"{EXP}/rtb"
M = json.load(open(f"{EXP}/out/stats.json"))["measure_commit"]
VARS = [k for k in paras[0] if k.startswith("V") and not k.endswith("|trig")]


def ctime(h):
    return subprocess.run(["git", "-C", REPO, "log", "-1", "--format=%ci %h %s", h], capture_output=True, text=True).stdout.strip()


res = []
lines = []
for g in gt:
    hits = [p for p in paras if p["note"] == g["note"] and any(n in p["text"] for n in g["needles"])]
    row = {"id": g["id"], "paragraphs": [], "flag": {}, "on_target": {}, "inv_in_window": {}}
    inv = g.get("inv_code", [])
    for v in VARS:
        row["flag"][v] = any(p[v] for p in hits)
        row["on_target"][v] = any(p[v] and any(h[:7] in inv for cs in p[v + "|trig"].values() for h in [c[:7] for c in cs]) for p in hits)
        row["inv_in_window"][v] = any(any(i in p["_win"][v.split("|")[0]] for i in inv) for p in hits if p["in_scope"])
    for p in hits:
        row["paragraphs"].append({k: p[k] for k in ("start", "end", "kind", "field", "in_scope", "p_max", "p_min", "p_max_day", "p_min_day", "note_updated", "para_date", "names_now", "names_ever")}
                                 | {v + "|trig": p[v + "|trig"] for v in VARS})
    res.append(row)
    lines.append(f"== {g['id']} {g['note']}  失效提交:{g['invalidating']}")
    for p in hits:
        lines.append(f"  L{p['start']}-{p['end']} kind={p['kind']} in_scope={p['in_scope']} blame_max={ctime(p['p_max'])}")
        lines.append(f"    blame_min={ctime(p['p_min'])} note_updated={p['note_updated']} para_date={p['para_date']}")
        lines.append(f"    names_now={p['names_now']}")
        lines.append(f"    names_ever-now={sorted(set(p['names_ever'])-set(p['names_now']))}")
        for v in VARS:
            if p[v + '|trig']:
                lines.append(f"    {v}: {p[v]} trig={p[v+'|trig']}")
    lines.append("  FLAG " + " ".join(f"{v}={int(row['flag'][v])}" for v in VARS))
    lines.append("  ONTARGET " + " ".join(f"{v}={int(row['on_target'][v])}" for v in VARS))
    lines.append("  INV_IN_WINDOW " + " ".join(f"{v}={int(row['inv_in_window'][v])}" for v in VARS if v.endswith('|now')))
tot = {v: sum(r["flag"][v] for r in res) for v in VARS}
tot_on = {v: sum(r["on_target"][v] for r in res) for v in VARS}
lines.append("RECALL_ONTARGET " + json.dumps(tot_on, ensure_ascii=False))
lines.append("RECALL " + json.dumps(tot, ensure_ascii=False))
json.dump({"rows": res, "recall": tot, "recall_on_target": tot_on}, open(f"{EXP}/out/recall.json", "w"), ensure_ascii=False, indent=1)
open(f"{EXP}/out/recall.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
