#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""canary_snr.py — canary 題目效度 SNR(S2 前瞻層;plan:Projects/驗證層自證三件_計劃)

borrow ClawBench variance decomposition:每題 SNR = 跨席分辨力 ÷ 同席重跑雜訊。
分子 = 各席 caught 率的跨席變異(這題分不分得開不同席位)
分母 = 各席內跨 run 的 caught 變異之均值(同席同題重跑的雜訊)

資料結構(--matrix JSON):[{"plant","seat","run_id","caught"}...]——固定題×多席×重跑,
與 canary_calibration.py 的判定矩陣同構(run_id 區分重跑批次)。
★docs/.canary-log.jsonl 不是本腳本的合法輸入★:該帳每筆為一次性植入,無同題重跑配對鍵
(plan r1 blocker:母體錯置)。

裁決規則(plan 折入,全機械):
- 任一席同題重跑 < MIN_RUNS(3) → no-verdict(樣本不足,不裁決)
- 分母 = 0(席內重跑全同)→ no-verdict(★非高訊號★——分不出「穩定」與「樣本太少剛好全同」)
- SNR < 1 → swap-candidate(在量猜運氣,標記換題候選;★換題恆人裁★)
- SNR ≥ 1 → keep(邊界 1 歸不換)

恆 rc0(觀測;輸入壞損 rc2 fail loud)。零依賴 stdlib。
"""
import argparse
import json
import sys

MIN_RUNS = 3          # 同題重跑下限(plan 射程聲明:題層 ≥3)
SNR_SWAP_BELOW = 1.0  # SNR<1=換題候選;邊界 1 歸不換


def _var(xs):
    """母體變異數(n 分母;比較用途,不做推論統計)。"""
    n = len(xs)
    if n == 0:
        return 0.0
    m = sum(xs) / n
    return sum((x - m) ** 2 for x in xs) / n


def judge_plants(rows):
    """rows -> [{plant, verdict, snr, seats, min_runs}](plant 排序)。純函數,無 I/O。"""
    plants = {}
    for r in rows:
        plants.setdefault(r["plant"], {}).setdefault(r["seat"], []).append(bool(r["caught"]))
    out = []
    for plant in sorted(plants):
        seats = plants[plant]
        runs_per_seat = [len(v) for v in seats.values()]
        min_runs = min(runs_per_seat)
        if min_runs < MIN_RUNS or len(seats) < 2:
            out.append({"plant": plant, "verdict": "no-verdict", "snr": None,
                        "seats": len(seats), "min_runs": min_runs,
                        "reason": f"樣本不足(席數 {len(seats)}/重跑下限 {min_runs}<{MIN_RUNS})"})
            continue
        seat_rates = [sum(v) / len(v) for v in seats.values()]
        numer = _var(seat_rates)                                  # 跨席分辨力
        denom = sum(_var(v) for v in seats.values()) / len(seats)  # 同席重跑雜訊均值
        if denom == 0.0:
            out.append({"plant": plant, "verdict": "no-verdict", "snr": None,
                        "seats": len(seats), "min_runs": min_runs,
                        "reason": "分母=0(席內重跑全同)——不裁決,非高訊號"})
            continue
        snr = numer / denom
        verdict = "swap-candidate" if snr < SNR_SWAP_BELOW else "keep"
        out.append({"plant": plant, "verdict": verdict, "snr": round(snr, 4),
                    "seats": len(seats), "min_runs": min_runs})
    return out


def main():
    ap = argparse.ArgumentParser(description="canary 題目效度 SNR(觀測恆 rc0;換題恆人裁)")
    ap.add_argument("--matrix", required=True, help="判定矩陣 JSON:[{plant,seat,run_id,caught}...]")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()
    try:
        with open(a.matrix, encoding="utf-8") as f:
            rows = json.load(f)
        assert isinstance(rows, list) and all(
            {"plant", "seat", "run_id", "caught"} <= set(r) for r in rows)
    except (OSError, ValueError, AssertionError) as e:
        print(f"ERROR: 矩陣讀取/格式失敗: {e}", file=sys.stderr)
        return 2
    res = judge_plants(rows)
    if a.as_json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        for r in res:
            extra = f"  ({r['reason']})" if r.get("reason") else ""
            print(f"{r['plant']}\t{r['verdict']}\tsnr={r['snr']}\tseats={r['seats']}"
                  f"\tmin_runs={r['min_runs']}{extra}")
        print("★觀測非閘:swap-candidate 只是候選,換題恆人裁;低 SNR 可能是 eval-awareness 偽訊號★")
    return 0


if __name__ == "__main__":
    sys.exit(main())
