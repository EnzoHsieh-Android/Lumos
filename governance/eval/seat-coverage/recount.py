#!/usr/bin/env python3
"""席間覆蓋率離線重算(2026-09-03)。

什麼時候用:想知道「一個審查席會漏掉同儕找到的多少真缺陷」時重跑這支,不需要派任何 agent。
資料源=docs/.canary-log.jsonl 的 capture_counts 欄(每個相異缺陷被幾席同時抓到)。
唯讀、零配額、零副作用。輸出直接印,數字要進圖譜就自己抄。
"""
import json, collections, statistics as st, sys, pathlib

LEDGER = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs/.canary-log.jsonl")


def rate(rs):
    """回 (獨家數, 相異缺陷數, 百分比)。獨家=capture_counts 裡值為 1 的項。"""
    t = s = 0
    for r in rs:
        for x in r["capture_counts"]:
            t += 1
            s += (x == 1)
    return s, t, (s / t * 100 if t else 0.0)


def main():
    rows = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    cc = [r for r in rows if r.get("capture_counts")]
    if not cc:
        print("帳上沒有 capture_counts 欄——這支算不出東西。")
        return 1

    # ── 母體與抽樣偏誤自查(先講清楚這批資料涵蓋什麼,再報數字) ──
    d = sorted(r["ts"][:10] for r in cc if r.get("ts"))
    fs = [r for r in rows if "findings_set" in r]
    d2 = sorted(r["ts"][:10] for r in fs if r.get("ts"))
    print(f"帶 capture_counts 的帳列 {len(cc)} 筆,日期 {d[0]}～{d[-1]}")
    print(f"帶 findings_set 的帳列 {len(fs)} 筆,日期 {d2[0]}～{d2[-1]}(兩者只在窄窗重疊,故同時帶兩者的很少)")
    a = [r["findings"] for r in cc if isinstance(r.get("findings"), int)]
    b = [r["findings"] for r in rows
         if not r.get("capture_counts") and "findings_set" in r and isinstance(r.get("findings"), int)]
    print(f"抽樣偏誤自查——有填計數的輪 findings 中位 {st.median(a)}/平均 {st.mean(a):.1f};"
          f" 沒填的輪 中位 {st.median(b)}/平均 {st.mean(b):.1f}(接近=沒有偏向簡單輪)")
    print()

    # ── 主結果:剔掉可能只有一席的輪才算數 ──
    solo = [r for r in cc if max(r["capture_counts"]) == 1]
    multi = [r for r in cc if max(r["capture_counts"]) >= 2]
    print("獨家發現率(只有一個席位抓到的缺陷佔比):")
    print("  全部(含可能單席的輪)      %5.1f%%  (%d/%d)" % (rate(cc)[2], rate(cc)[0], rate(cc)[1]))
    print("  ★剔掉 max=1 的輪(確定多席)  %5.1f%%  (%d/%d)★" % (rate(multi)[2], rate(multi)[0], rate(multi)[1]))
    print("     ↑ 這個才是主數字:max=1 的輪每個缺陷必然是獨家,混進去會灌高")
    print()
    print("按「最多幾席同時抓到同一個缺陷」分層(看加席位的邊際效果):")
    for k in (2, 3, 4):
        g = [r for r in cc if max(r["capture_counts"]) == k]
        s, t, p = rate(g)
        print(f"  最多 {k} 席   輪數{len(g):4d} 缺陷{t:5d} 獨家{s:5d} = {p:5.1f}%")
    print()

    # ── 獨家發現是真缺陷還是誤報:用「零放行輪」繞開順序假設 ──
    # capture_counts 是無 id 的計數陣列,無法直接對到 findings_set 的 id;
    # 但若該輪 accepted_set 為空(零放行),則所有發現都被折入,獨家發現必然也在其中——集合層推論,不靠順序。
    both = [r for r in cc if "findings_set" in r]
    clean = [r for r in both if not (r.get("accepted_set") or [])]
    s, t, p = rate(clean)
    print(f"獨家發現是不是誤報——同時帶兩種資料的 {len(both)} 輪中,零放行的 {len(clean)} 輪:")
    print(f"  相異缺陷 {t}、獨家 {s} = {p:.1f}%,且該輪零放行 → ★這些獨家發現全部被折入(編排者認可是真的)★")
    F = sum(len(r["findings_set"]) for r in fs)
    A = sum(len(r.get("accepted_set") or []) for r in fs)
    print(f"  對照全帳:發現 {F} 條、附理由放行 {A} 條 = {A/F*100:.1f}%(這套流程幾乎不判誤報)")
    print()

    # ── 誠實界線 ──
    byround = collections.defaultdict(set)
    for r in rows:
        byround[(r.get("loop"), r.get("round"))].add(r.get("auditor"))
    true_solo = sum(1 for r in solo if len(byround[(r.get("loop"), r.get("round"))]) == 1)
    print("誠實界線:")
    print(f"  · max=1 的 {len(solo)} 輪裡,帳上確實只有 1 個 auditor 的只有 {true_solo} 輪"
          f"——其餘 {len(solo)-true_solo} 輪是多席卻零重疊。")
    print("  · capture_counts 是編排者手填,不是機器獨立量到的,與審查報告同一層天花板。")
    print("  · 「獨家」量的是席間分歧;它等於真漏抓,靠的是上面那條零放行推論,不是直接證據。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
