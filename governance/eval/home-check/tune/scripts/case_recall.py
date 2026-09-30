import json, sys
sys.path.insert(0, __file__.rsplit("/",1)[0])
from parse import flags, EXP
NL = json.load(open(EXP+"/needle_lines.json"))
V = ["P0","V1","V2","V3","V3r2","V4"]
with open(EXP+"/case_recall.tsv","w") as f:
    f.write("case\tunit\tcommit\tneedle_lines\t" + "\t".join(V) + "\n")
    for gid, nv in NL.items():
        row = []
        for v in V:
            items, _ = flags(nv["prompt"], v)
            lines = {int(i["line"]) for i in items}
            row.append("HIT" if lines & set(nv["needle_lines"]) else "miss")
        f.write(f"{gid}\t{nv['prompt']}\t{nv['commit']}\t{nv['needle_lines']}\t" + "\t".join(row) + "\n")
print(open(EXP+"/case_recall.tsv").read())
