import os
import json, random
EXP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = json.load(open(EXP+"/commit_homes.json"))
EXCL = {"b2fc512","c177791","d98b4ca","5ec931e","0ffba7d","8ff8c95","0b2499a","e606947","7413936"}
pool = [r for r in rows if r["home_notes"] and r["commit"] not in EXCL]
rng = random.Random(20260930)
pick = rng.sample(pool, 10)
with open(EXP+"/control.tsv","w") as f:
    for i, r in enumerate(pick):
        note = rng.choice(r["home_notes"])
        f.write(f"K{i+1:02d}\t{r['commit']}\t{note}\n")
print(open(EXP+"/control.tsv").read(), "pool", len(pool))
