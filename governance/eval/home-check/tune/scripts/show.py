import sys
sys.path.insert(0, __file__.rsplit("/",1)[0])
from common import *
unit = {l.split("\t")[0]: l.rstrip("\n").split("\t")[1:] for l in open(EXP+"/all.tsv")}
uid = sys.argv[1]; c, n = unit[uid]
t = note_at(c, n).split("\n")
for a in sys.argv[2:]:
    L = int(a)
    h = max([i for i in range(L) if t[i].startswith("#")], default=None)
    print(f"=== {uid} L{L}  heading L{h+1 if h is not None else '-'}: {t[h] if h is not None else ''}")
    if h is not None:
        for j in range(h+1, min(h+4, L-1)):
            if t[j].strip(): print(f"   [節首 L{j+1}] {t[j][:300]}")
    print(f"   >> {t[L-1][:700]}")
