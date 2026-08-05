"""K=1 誤停率分層回放(2026-08-05,A 案立案證據)。
分層:legacy 循序(無 round 欄;一筆=一輪) vs panel(round 欄;W 席一輪)。
乾淨輪定義依各層自己的語意;severity 取帳面(辯方後存活 max=閘自己消費的變數)。
右截尾另計不混入分母。"""
import json, pathlib, sys
from collections import OrderedDict

SEV_BAD = {"major", "blocker"}

def rounds_of(recs):
    """回 [(rid, [rec,...])] 依出現序;無 round 欄=每筆自成一輪。"""
    if not any("round" in r for r in recs):
        return [("__seq%d" % i, [r]) for i, r in enumerate(recs)], "legacy"
    groups = OrderedDict()
    for r in recs:
        groups.setdefault(r.get("round", "?"), []).append(r)
    return list(groups.items()), "panel"

def clean_round(rnds, mode):
    recs = rnds
    if mode == "legacy":
        r = recs[0]
        return r.get("kind") == "caught" and r.get("severity") in ("clean", "minor")
    ca = sum(1 for r in recs if r.get("kind") == "caught")
    mi = sum(1 for r in recs if r.get("kind") == "missed")
    worst_bad = any(r.get("severity") in SEV_BAD for r in recs)
    return ca >= 2 and mi == 0 and not worst_bad

def dirty_major(rnds):
    return any(r.get("severity") in SEV_BAD for r in rnds)

def analyze(path, repo):
    loops = OrderedDict()
    for l in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        try: d = json.loads(l)
        except ValueError: continue
        if d.get("kind") not in ("caught", "missed") or not d.get("loop"): continue
        loops.setdefault(d["loop"], []).append(d)
    out = {}
    for lp, recs in loops.items():
        if len(recs) < 2 and "round" not in recs[0]: pass
        rnds, mode = rounds_of(recs)
        kind = "code" if lp.startswith("code-") else "design"
        key = (mode, kind)
        st = out.setdefault(key, dict(clean_follow=0, rebound=0, censored=0, loops=set(), cases=[]))
        for i, (rid, rr) in enumerate(rnds):
            if not clean_round(rr, mode): continue
            later = rnds[i+1:]
            if not later:
                st["censored"] += 1
                continue
            st["clean_follow"] += 1
            if any(dirty_major(x[1]) for x in later):
                st["rebound"] += 1
                seq = [(x[0], max((r.get("severity") or "?") for r in x[1]),
                        "".join("C" if r.get("kind")=="caught" else "M" for r in x[1])) for x in rnds]
                st["cases"].append((lp, rid, seq))
        for _ in rnds: st["loops"].add(lp)
    print(f"== {repo} ==")
    for (mode, kind), st in sorted(out.items()):
        n, r, c = st["clean_follow"], st["rebound"], st["censored"]
        rate = f"{r}/{n}" if n else "0/0"
        print(f"  [{mode}·{kind}-loop] loops={len(st['loops'])}  乾淨輪且有後續={n}  其後冒≥major={rate}  右截尾(乾淨即末輪)={c}")
        for lp, rid, seq in st["cases"]:
            s = " → ".join(f"{rid2}:{sev}({km})" for rid2, sev, km in seq)
            print(f"      ↩ {lp} @ {rid}: {s}")
    return out

analyze("docs/.canary-log.jsonl", "toolchain")
analyze("/Users/enzo/backend/LandmarkMember/docs/.canary-log.jsonl", "landmark")
