import os
import json, re, glob, sys
EXP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def flags(uid, v):
    d = json.load(open(f"{EXP}/outputs/{uid}.{v}.json"))
    m = re.findall(r"```json\s*(.*?)```", d["result"], re.S)
    items = json.loads(m[-1]) if m else []
    return items, d
if __name__ == "__main__":
    rows = []
    for f in sorted(glob.glob(EXP+"/outputs/*.json")):
        if f.endswith((".wall.json",)): continue
        uid, v = f.rsplit("/",1)[1].split(".")[:2]
        items, d = flags(uid, v)
        for it in items:
            rows.append((uid, v, it.get("line"), (it.get("quote") or "")[:80].replace("\n"," "), (it.get("why") or "")[:160].replace("\n"," ")))
    for r in rows: print("\t".join(map(str,r)))
