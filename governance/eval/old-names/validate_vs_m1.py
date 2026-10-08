#!/opt/homebrew/bin/python3
"""對照:挑幾個提交,直接跑 m1 本體(_drift_old_sentence_check,定義快取關掉)看它的消失名稱,
跟參考實作在同一個提交記下的粗候選比(m1 的 gone = 粗候選 - 那個提交的終點語料)。"""
import json, sys, time, collections
sys.path.insert(0, ".")
import oldnames_ref as R
M = R.load()
M._drift_m1_cache_dir = lambda: None
repo, vault, gonef, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
gone = json.load(open(gonef))
# 從 gone.json 的 events 收集 (提交 -> 名稱)
per = collections.defaultdict(set)
for name, m in gone.items():
    for c, _f in m["events"]:
        per[c].add(name)
cs = sorted(per, key=lambda c: -len(per[c]))[:n]
out = []
for c in cs:
    p = R.git(repo, "rev-parse", c + "^").decode().strip()
    res = M._drift_old_sentence_check(repo, p, c, vault, time.monotonic() + 600)
    m1 = set(res["gone"])
    mine = per[c]
    # mine 只含量測點仍消失的;m1 的是那個提交當下消失的。比:mine ⊆ m1?
    out.append({"commit": c[:8], "m1_state": res["state"], "m1_gone": len(m1), "mine_still_gone": len(mine),
                "mine_minus_m1": sorted(mine - m1)[:10]})
print(json.dumps(out, ensure_ascii=False, indent=1))
