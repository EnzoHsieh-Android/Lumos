"""K=1 誤停率分層回放(2026-08-05;r1-s2 修正版:乾淨輪=真 gate 三條合取)。
v1 缺陷(A案 design-loop r1 s2 席抓到):「乾淨輪」漏算 capture-recapture 殘餘條件——
真 gate(_loop_status_panel)是三條合取(輪有效∧存活≤minor∧殘餘<1,無 counts=fail-closed),
v1 只算前兩條 → 18 個「乾淨」panel 輪有 11 個真 gate 根本不會放行,n 高估。
修:import 主檔 _estimate_remaining_defects(單一實作),panel 層乾淨輪補殘餘條件。
legacy 層無 counts 概念,維持雙條件並在輸出標注語意差。路徑改吃參數(v1 硬編碼絕對路徑)。"""
import importlib.machinery, importlib.util, json, pathlib, sys
from collections import OrderedDict

_HERE = pathlib.Path(__file__).resolve()
_loader = importlib.machinery.SourceFileLoader("lumos_main", str(_HERE.parent.parent.parent / "scripts" / "lumos"))
_spec = importlib.util.spec_from_loader("lumos_main", _loader)
_lm = importlib.util.module_from_spec(_spec)
sys.modules["lumos_main"] = _lm
_loader.exec_module(_lm)
_est = _lm._estimate_remaining_defects

SEV_BAD = {"major", "blocker"}

def rounds_of(recs):
    if not any("round" in r for r in recs):
        return [("__seq%d" % i, [r]) for i, r in enumerate(recs)], "legacy"
    groups = OrderedDict()
    for r in recs:
        groups.setdefault(r.get("round", "?"), []).append(r)
    return list(groups.items()), "panel"

def clean_round(recs, mode):
    if mode == "legacy":
        r = recs[0]
        return r.get("kind") == "caught" and r.get("severity") in ("clean", "minor")
    ca = sum(1 for r in recs if r.get("kind") == "caught")
    mi = sum(1 for r in recs if r.get("kind") == "missed")
    worst_bad = any(r.get("severity") in SEV_BAD for r in recs)
    if not (ca >= 2 and mi == 0 and not worst_bad):
        return False
    cc = next((r["capture_counts"] for r in recs if r.get("capture_counts")), None)
    if cc is None:
        return False   # 真 gate fail-closed:無 counts=未證枯竭,不算乾淨
    try:
        return _est(cc) < 1.0
    except Exception:
        return False

def dirty_major(recs):
    return any(r.get("severity") in SEV_BAD for r in recs)

def analyze(path, repo):
    loops = OrderedDict()
    for l in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        try: d = json.loads(l)
        except ValueError: continue
        if d.get("kind") not in ("caught", "missed") or not d.get("loop"): continue
        loops.setdefault(d["loop"], []).append(d)
    out = {}
    for lp, recs in loops.items():
        rnds, mode = rounds_of(recs)
        kind = "code" if lp.startswith("code-") else "design"
        st = out.setdefault((mode, kind), dict(clean_follow=0, rebound=0, censored=0, loops=set(), cases=[]))
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
        note = "(真 gate 三條合取)" if mode == "panel" else "(雙條件;legacy 無 counts 概念,語意較鬆)"
        print(f"  [{mode}·{kind}-loop]{note} loops={len(st['loops'])}  乾淨輪且有後續={n}  其後冒≥major={r}/{n}  右截尾={c}")
        for lp, rid, seq in st["cases"]:
            s = " → ".join(f"{rid2}:{sev}({km})" for rid2, sev, km in seq)
            print(f"      ↩ {lp} @ {rid}: {s}")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("ledgers", nargs="*", help="tag=path 對;預設 toolchain 自帳+landmark(存在才跑)")
    a = ap.parse_args()
    pairs = [x.split("=", 1) for x in a.ledgers] if a.ledgers else []
    if not pairs:
        pairs = [("toolchain", str(_HERE.parent.parent.parent / "docs" / ".canary-log.jsonl"))]
        lm = pathlib.Path.home() / "backend" / "LandmarkMember" / "docs" / ".canary-log.jsonl"
        if lm.exists():
            pairs.append(("landmark", str(lm)))
    for tag, path in pairs:
        if pathlib.Path(path).exists():
            analyze(path, tag)
        else:
            print(f"== {tag} == (帳不存在:{path},跳過)")

main()
