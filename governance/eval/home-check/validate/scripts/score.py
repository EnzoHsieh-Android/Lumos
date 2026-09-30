import os
import json, csv, re, statistics as st, sys
VAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(units_file, judg_file):
    J = {(r["unit"], int(r["line"])): r["category"] for r in csv.DictReader(open(f"{VAL}/{judg_file}"), delimiter="\t")}
    rows = []
    for u in csv.DictReader(open(f"{VAL}/{units_file}"), delimiter="\t"):
        d = json.load(open(f"{VAL}/outputs/{u['unit']}.json"))
        m = re.findall(r"```json\s*(.*?)```", d["result"], re.S)
        items = json.loads(m[-1]) if m else []
        lines = sorted({int(i["line"]) for i in items})
        cats = {k: 0 for k in ("TP", "TRUE_PRE", "BORDER", "FP")}; unj = []
        for L in lines:
            c = J.get((u["unit"], L))
            if c is None: unj.append(L)
            else: cats[c] += 1
        us = d["usage"]; inp = us["input_tokens"] + us["cache_creation_input_tokens"] + us["cache_read_input_tokens"]
        meta = json.load(open(f"{VAL}/prompts/{u['unit']}.meta.json"))
        rows.append(dict(u, flagged=len(lines), **cats, unjudged=unj, cost=d["total_cost_usd"], inp=inp, out=us["output_tokens"],
                         dur=d["duration_ms"] / 1000, prompt_chars=meta["prompt_chars"], trunc=meta["diff_truncated"]))
    return rows
main = load("units.tsv", "line_judgments.tsv"); supp = load("units_supp.tsv", "line_judgments_supp.tsv")
sel = json.load(open(f"{VAL}/selection.json"))
with open(f"{VAL}/per_call.tsv", "w") as f:
    keys = ["unit", "repo", "commit", "note", "flagged", "TP", "TRUE_PRE", "BORDER", "FP", "prompt_chars", "inp", "out", "cost", "dur", "trunc", "unjudged"]
    f.write("\t".join(keys) + "\n")
    for r in main + supp:
        f.write("\t".join(str(round(r[k], 4) if isinstance(r[k], float) else r[k]) for k in keys) + "\n")
summ = {}
def agg(rows, name):
    fl = sum(r["flagged"] for r in rows); c = {k: sum(r[k] for r in rows) for k in ("TP", "TRUE_PRE", "BORDER", "FP")}
    costs = [r["cost"] for r in rows]
    summ[name] = dict(calls=len(rows), flagged=fl, **c, unjudged=sum(len(r["unjudged"]) for r in rows),
                      precision_TP=round(c["TP"] / fl, 3) if fl else None,
                      precision_TP_or_PRE=round((c["TP"] + c["TRUE_PRE"]) / fl, 3) if fl else None,
                      non_FP=round((fl - c["FP"]) / fl, 3) if fl else None,
                      calls_with_flags=sum(1 for r in rows if r["flagged"]),
                      cost_total=round(sum(costs), 4), cost_mean=round(st.mean(costs), 4), cost_median=round(st.median(costs), 4), cost_max=round(max(costs), 4),
                      inp_mean=int(st.mean(r["inp"] for r in rows)), inp_max=max(r["inp"] for r in rows),
                      dur_mean=round(st.mean(r["dur"] for r in rows), 1), dur_max=round(max(r["dur"] for r in rows), 1))
agg([r for r in main if r["repo"] == "rtb"], "rtb"); agg([r for r in main if r["repo"] == "tool"], "tool_main_first8")
agg(supp, "tool_supp_edited_homes"); agg(main, "all_main")
# per commit
pc = []
for g, pre in (("rtb", "R"), ("tool", "T")):
    for i, x in enumerate(sel[g]["picked"]):
        rs = [r for r in main if r["unit"].startswith(f"{pre}{i+1:02d}n")]
        ss = [r for r in supp if r["unit"].startswith(f"S{i+1:02d}n")] if g == "tool" else []
        cost = sum(r["cost"] for r in rs)
        per_note = cost / len(rs)
        pc.append(dict(id=f"{pre}{i+1:02d}", repo=g, commit=x["commit"], code_files=x["code_files"], home_notes=x["n_home_notes"], run=len(rs),
                       skipped=x["skipped_notes"], flagged=sum(r["flagged"] for r in rs), TP=sum(r["TP"] for r in rs), TRUE_PRE=sum(r["TRUE_PRE"] for r in rs),
                       BORDER=sum(r["BORDER"] for r in rs), FP=sum(r["FP"] for r in rs), cost=round(cost, 4),
                       cost_all_homes_est=round(per_note * x["n_home_notes"], 3),
                       wall_parallel_s=round(max(r["dur"] for r in rs), 1), serial_s=round(sum(r["dur"] for r in rs), 1),
                       supp_run=len(ss), supp_flagged=sum(r["flagged"] for r in ss), supp_cost=round(sum(r["cost"] for r in ss), 4)))
with open(f"{VAL}/per_commit.tsv", "w") as f:
    f.write("\t".join(pc[0].keys()) + "\n")
    for r in pc: f.write("\t".join(map(str, r.values())) + "\n")
for g in ("rtb", "tool"):
    rows = [r for r in pc if r["repo"] == g]
    summ[f"push_{g}"] = dict(cost_run_mean=round(st.mean(r["cost"] for r in rows), 4), cost_run_max=max(r["cost"] for r in rows),
                            cost_all_homes_est_mean=round(st.mean(r["cost_all_homes_est"] for r in rows), 3),
                            cost_all_homes_est_max=max(r["cost_all_homes_est"] for r in rows),
                            wall_parallel_mean_s=round(st.mean(r["wall_parallel_s"] for r in rows), 1))
lum = [r for r in pc if r["repo"] == "tool" and r["skipped"]]
summ["push_tool_scripts_lumos_commits"] = dict(n=len(lum), home_notes_mean=round(st.mean(r["home_notes"] for r in lum), 1),
    cost_first8_mean=round(st.mean(r["cost"] for r in lum), 4), cost_all_homes_est_mean=round(st.mean(r["cost_all_homes_est"] for r in lum), 3),
    cost_all_homes_est_max=max(r["cost_all_homes_est"] for r in lum))
rv = []
for r in csv.DictReader(open(f"{VAL}/review/sample.tsv"), delimiter="\t"):
    d = json.load(open(f"{VAL}/review/outputs/{r['rid']}.json"))
    v = re.findall(r"VERDICT:\s*(DRIFT|PRE|BORDER|HOLDS)", d["result"]); rv.append((r, v[-1] if v else "NONE", d["total_cost_usd"]))
J = {(r["unit"], r["line"]): r["category"] for r in csv.DictReader(open(f"{VAL}/line_judgments.tsv"), delimiter="\t")}
MAP = {"TP": "DRIFT", "TRUE_PRE": "PRE", "BORDER": "BORDER", "FP": "HOLDS"}
with open(f"{VAL}/review_table.tsv", "w") as f:
    f.write("rid\tunit\tline\tmine\treviewer\tagree\tcost\n")
    for r, v, c in rv:
        mine = MAP[J[(r["unit"], r["line"])]]
        f.write(f"{r['rid']}\t{r['unit']}\t{r['line']}\t{mine}\t{v}\t{int(mine == v)}\t{c:.4f}\n")
tab = list(csv.DictReader(open(f"{VAL}/review_table.tsv"), delimiter="\t"))
pos = lambda x: x in ("DRIFT", "PRE")
summ["review"] = dict(n=len(tab), exact_agree=sum(int(t["agree"]) for t in tab),
    reviewer_counts={k: sum(1 for t in tab if t["reviewer"] == k) for k in ("DRIFT", "PRE", "BORDER", "HOLDS")},
    mine_counts={k: sum(1 for t in tab if t["mine"] == k) for k in ("DRIFT", "PRE", "BORDER", "HOLDS")},
    agree_real_vs_not=sum(1 for t in tab if pos(t["mine"]) == pos(t["reviewer"])),
    cost=round(sum(c for _, _, c in rv), 4))
summ["total_spend_usd"] = round(summ["all_main"]["cost_total"] + summ["tool_supp_edited_homes"]["cost_total"] + summ["review"]["cost"], 4)
json.dump(summ, open(f"{VAL}/summary.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(summ, ensure_ascii=False, indent=1))
