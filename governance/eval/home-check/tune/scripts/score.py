import json, csv, sys, statistics as st
sys.path.insert(0, __file__.rsplit("/",1)[0])
from parse import flags, EXP
J = {(r["unit"], int(r["line"])): r["category"] for r in csv.DictReader(open(EXP+"/line_judgments.tsv"), delimiter="\t")}
NL = json.load(open(EXP+"/needle_lines.json"))
units = [l.split("\t")[0] for l in open(EXP+"/all.tsv")]
cases = [u for u in units if not u.startswith("K")]; ctrl = [u for u in units if u.startswith("K")]
out = open(EXP+"/per_call.tsv","w")
out.write("unit\tvariant\tflagged_lines\tNEEDLE\tTP\tTRUE_PRE\tBORDER\tFP\tprompt_chars\tinput_tokens\toutput_tokens\tcost_usd\tduration_s\tunjudged\n")
summ = {}
for v in ["P0","V1","V2","V3","V3r2","V4"]:
    agg = dict(calls=0, flagged=0, NEEDLE=0, TP=0, TRUE_PRE=0, BORDER=0, FP=0, cost=[], dur=[], inp=[], ctrl_flag=0, ctrl_fp=0, ctrl_true=0, ctrl_border=0)
    hits = []
    for u in units:
        items, d = flags(u, v)
        lines = sorted({int(i["line"]) for i in items if str(i.get("line","")).isdigit() or isinstance(i.get("line"), int)})
        cats = {c: 0 for c in ["NEEDLE","TP","TRUE_PRE","BORDER","FP"]}; unj = []
        for L in lines:
            c = J.get((u, L))
            if c is None: unj.append(L); continue
            cats["FP" if c.startswith("FP") else c] += 1
        us = d["usage"]; inp = us["input_tokens"] + us["cache_creation_input_tokens"] + us["cache_read_input_tokens"]
        pc = len(open(f"{EXP}/prompts/{u}.{v}.txt").read())
        out.write(f"{u}\t{v}\t{len(lines)}\t" + "\t".join(str(cats[k]) for k in ["NEEDLE","TP","TRUE_PRE","BORDER","FP"]) +
                  f"\t{pc}\t{inp}\t{us['output_tokens']}\t{d['total_cost_usd']:.4f}\t{d['duration_ms']/1000:.1f}\t{','.join(map(str,unj))}\n")
        agg["calls"] += 1; agg["flagged"] += len(lines)
        for k in cats: agg[k] += cats[k]
        agg["cost"].append(d["total_cost_usd"]); agg["dur"].append(d["duration_ms"]/1000); agg["inp"].append(inp)
        if u in ctrl:
            agg["ctrl_flag"] += len(lines); agg["ctrl_fp"] += cats["FP"]; agg["ctrl_true"] += cats["TP"]+cats["TRUE_PRE"]; agg["ctrl_border"] += cats["BORDER"]
        if u in cases:
            for gid, nv in NL.items():
                if nv["prompt"] == u and set(nv["needle_lines"]) & set(lines): hits.append(gid)
    summ[v] = dict(recall=f"{len(hits)}/9", hits=sorted(hits), flagged=agg["flagged"], needle_lines=agg["NEEDLE"], tp_other=agg["TP"],
                   true_pre=agg["TRUE_PRE"], border=agg["BORDER"], fp=agg["FP"],
                   precision_strict=round((agg["NEEDLE"]+agg["TP"])/agg["flagged"],3) if agg["flagged"] else None,
                   precision_true=round((agg["NEEDLE"]+agg["TP"]+agg["TRUE_PRE"])/agg["flagged"],3) if agg["flagged"] else None,
                   ctrl_flag_per_call=agg["ctrl_flag"]/10, ctrl_fp_per_call=agg["ctrl_fp"]/10, ctrl_true=agg["ctrl_true"], ctrl_border=agg["ctrl_border"],
                   cost_mean=round(st.mean(agg["cost"]),4), cost_median=round(st.median(agg["cost"]),4), cost_max=round(max(agg["cost"]),4),
                   dur_mean=round(st.mean(agg["dur"]),1), dur_max=round(max(agg["dur"]),1), inp_mean=int(st.mean(agg["inp"])), inp_max=max(agg["inp"]))
json.dump(summ, open(EXP+"/summary.json","w"), ensure_ascii=False, indent=1)
for v, s in summ.items(): print(v, json.dumps(s, ensure_ascii=False))
