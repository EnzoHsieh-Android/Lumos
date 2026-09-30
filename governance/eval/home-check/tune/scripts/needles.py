import os
import sys, json
sys.path.insert(0, __file__.rsplit("/",1)[0])
from common import *
gt = {g["id"]: g for g in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "stale-ref", "groundtruth.json")))}
cases = {"A1":("b2fc512","A1"),"A2":("c177791","A2"),"A3":("d98b4ca","A3"),"C1":("b2fc512","C"),"C2":("b2fc512","C"),"C3":("b2fc512","C"),"D1":("b2fc512","D1"),"D2":("5ec931e","D2"),"D3":("b2fc512","D3")}
out = {}
for gid,(c,pid) in cases.items():
    g = gt[gid]; t = note_at(c, g["note"]).split("\n")
    lines = sorted({i+1 for i,l in enumerate(t) for n in g["needles"] if n in l})
    out[gid] = {"prompt": pid, "commit": c, "note": g["note"], "needle_lines": lines}
    print(gid, pid, lines, g["needles"])
json.dump(out, open(EXP+"/needle_lines.json","w"), ensure_ascii=False, indent=1)
