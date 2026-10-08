import os
"""Pick unseen commits. rtb: non-merge commits on HEAD touching a homed file under src/ or tests/, excluding every commit
used by homescan-exp (case + control + its exclusion list + groundtruth invalidating commits). tool: last 300 commits of
HEAD, non-merge, touching a homed program file. Seed 20261001, 15 each."""
import sys, json, random, statistics as st
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from vcommon import *
E = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tune")
CAP = 8
EXCL = {"b2fc512", "c177791", "d98b4ca", "5ec931e", "0ffba7d", "8ff8c95", "0b2499a", "e606947", "7413936"}
EXCL |= {l.split("\t")[1] for l in open(E + "/all.tsv")}

def pool_rows(repo, commits, filt):
    rows = []
    for c in commits:
        code = repo.code_files(c)
        if not code: continue
        hm = repo.homes_ordered(c)
        homed = [f for f in code if f in hm and filt(f)]
        if not homed: continue
        notes = home_notes(repo, c, code)
        rows.append({"commit": c[:8], "code_files": len(code), "homed_code_files": len([f for f in code if f in hm]), "home_notes": notes})
    return rows

out = {}
r = Repo("rtb")
rc = r.git("rev-list", "--no-merges", "HEAD").split()
rrows = pool_rows(r, rc, lambda f: f.startswith(("src/", "tests/")))
rpool = [x for x in rrows if x["commit"][:7] not in EXCL]
rpool.sort(key=lambda x: x["commit"])
rsel = random.Random(20261001).sample(rpool, 15)
out["rtb"] = dict(n_nonmerge=len(rc), n_pool_before_excl=len(rrows), n_pool=len(rpool), excluded=sorted(EXCL), picked=rsel)

t = Repo("tool")
tc_all = t.git("rev-list", "--max-count=300", "HEAD").split()
tc = t.git("rev-list", "--no-merges", "--max-count=300", "HEAD").split()
tc = [c for c in tc_all if c in set(tc)]
trows = pool_rows(t, tc, lambda f: True)
tpool = sorted(trows, key=lambda x: x["commit"])
tsel = random.Random(20261001).sample(tpool, 15)
for x in tsel:
    x["n_home_notes"] = len(x["home_notes"]); x["run_notes"] = x["home_notes"][:CAP]; x["skipped_notes"] = max(0, len(x["home_notes"]) - CAP)
for x in rsel:
    x["n_home_notes"] = len(x["home_notes"]); x["run_notes"] = x["home_notes"]; x["skipped_notes"] = 0
out["tool"] = dict(n_last300=len(tc_all), n_nonmerge=len(tc), n_pool=len(tpool), picked=tsel)

def dist(rows):
    k = [len(x["home_notes"]) for x in rows]
    return dict(n=len(k), mean=round(st.mean(k), 2), median=st.median(k), max=max(k), hist={str(v): k.count(v) for v in sorted(set(k))})
out["dist"] = {"rtb_pool": dist(rpool), "rtb_picked": dist(rsel), "tool_pool": dist(tpool), "tool_picked": dist(tsel),
               "tool_pool_touching_scripts_lumos": sum(1 for x in tpool if "scripts/lumos" in t.code_files(x["commit"])),
               "tool_pool_gt8": sum(1 for x in tpool if len(x["home_notes"]) > CAP)}
json.dump(out, open(VAL + "/selection.json", "w"), ensure_ascii=False, indent=1)
json.dump({"rtb_pool": rpool, "tool_pool": tpool}, open(VAL + "/pool_homes.json", "w"), ensure_ascii=False, indent=0)
with open(VAL + "/units.tsv", "w") as f:
    f.write("unit\trepo\tcommit\tnote\n")
    for g, sel in (("R", rsel), ("T", tsel)):
        for i, x in enumerate(sel):
            for j, n in enumerate(x["run_notes"]):
                f.write(f"{g}{i+1:02d}n{j+1}\t{'rtb' if g=='R' else 'tool'}\t{x['commit']}\t{n}\n")
print(json.dumps(out["dist"], ensure_ascii=False, indent=1))
for g, sel in (("R", rsel), ("T", tsel)):
    for i, x in enumerate(sel):
        print(g, i + 1, x["commit"], x["code_files"], x["n_home_notes"], x["skipped_notes"])
