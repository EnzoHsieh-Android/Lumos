"""For every non-merge commit touching code: which notes are homes of changed code files (as of that commit)."""
import sys, json, subprocess, random
sys.path.insert(0, __file__.rsplit("/",1)[0])
from common import *
cat = subprocess.Popen(["git","-C",RTB,"cat-file","--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
blob_ac = {}
def blob_text(sha):
    cat.stdin.write((sha+"\n").encode()); cat.stdin.flush()
    hdr = cat.stdout.readline().split()
    n = int(hdr[2]); data = cat.stdout.read(n); cat.stdout.read(1)
    return data.decode("utf-8", "replace")
def homes(rev):
    m = {}
    for line in git("ls-tree","-r",rev,KB).splitlines():
        meta, path = line.split("\t",1)
        if not path.endswith(".md"): continue
        sha = meta.split()[2]
        if sha not in blob_ac: blob_ac[sha] = about_code(blob_text(sha))
        for f in blob_ac[sha]: m.setdefault(f, []).append(path[len(KB)+1:])
    return m
commits = git("rev-list","--no-merges","--reverse","HEAD").split()
rows = []
for c in commits:
    files = changed_files(c)
    code = [f for f in files if is_code(f)]
    if not code: continue
    hm = homes(c)
    notes = sorted({n for f in code for n in hm.get(f, [])})
    homed = [f for f in code if f in hm]
    changed_notes = [f[len(KB)+1:] for f in files if f.startswith(KB+"/")]
    rows.append({"commit": c[:7], "code_files": len(code), "homed_code_files": len(homed), "home_notes": notes,
                 "home_notes_changed_in_commit": [n for n in notes if n in changed_notes]})
json.dump(rows, open(EXP+"/commit_homes.json","w"), ensure_ascii=False, indent=0)
with_home = [r for r in rows if r["home_notes"]]
import statistics as st
k = [len(r["home_notes"]) for r in with_home]
print("commits total", len(commits), "code-touching", len(rows), "with >=1 home", len(with_home))
print("home notes per code commit (with home): mean %.2f median %s max %d" % (st.mean(k), st.median(k), max(k)))
k2 = [len(r["home_notes"]) for r in rows]
print("home notes per code commit (all code commits): mean %.2f median %s" % (st.mean(k2), st.median(k2)))
print("dist", sorted(k))
