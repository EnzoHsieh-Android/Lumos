import os
import json, re, csv, sys
VAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def flags(uid):
    d = json.load(open(f"{VAL}/outputs/{uid}.json"))
    m = re.findall(r"```json\s*(.*?)```", d["result"], re.S)
    items = json.loads(m[-1]) if m else []
    return items, d
def units():
    return list(csv.DictReader(open(VAL + "/units.tsv"), delimiter="\t"))
if __name__ == "__main__":
    tot = 0; n = 0
    with open(VAL + "/flagged.tsv", "w") as f:
        f.write("unit\trepo\tcommit\tnote\tline\tquote\twhy\n")
        for u in units():
            try: items, d = flags(u["unit"])
            except Exception as e: print("ERR", u["unit"], e); continue
            tot += d["total_cost_usd"]; n += 1
            for it in items:
                f.write("\t".join([u["unit"], u["repo"], u["commit"], u["note"], str(it.get("line")),
                        (it.get("quote") or "").replace("\n", " ").replace("\t", " "), (it.get("why") or "").replace("\n", " ").replace("\t", " ")]) + "\n")
    print("calls", n, "cost", round(tot, 4))
