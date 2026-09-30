#!/opt/homebrew/bin/python3
"""補充量測:①發現的名稱按消失提交分佈 ②rtb 的 b2fc512 那次推送若當時就有 m1,本體會列幾筆(對照存量版)。"""
import json, sys, time, collections, subprocess
sys.path.insert(0, ".")
import oldnames_ref as R
M = R.load()
M._drift_m1_cache_dir = lambda: None
out = {}
for name, repo in (("rtb", "rtb"), ("tool", "tool")):
    rows = [json.loads(l) for l in open(f"out/{name}.findings.jsonl")]
    c = collections.Counter()
    for r in rows:
        for v in {r["meta"][n]["vanish"] for n in r["names"]}:
            c[v] += 1
    out[name + "_vanish_dist"] = [(v[:8], k, subprocess.run(["git", "-C", repo, "log", "-1", "--format=%cs", v],
                                   capture_output=True, text=True).stdout.strip()) for v, k in c.most_common(12)]
b = "b2fc5122f1001197d9bd34fcfa9c7d2290955a91"
p = R.git("rtb", "rev-parse", b + "^").decode().strip()
t0 = time.time()
res = M._drift_old_sentence_check("rtb", p, b, "docs/rtb-production-agent-demo-knowledge", time.monotonic() + 600)
out["m1_on_b2fc512"] = {"state": res["state"], "handle": len(res["handle"]), "listed": len(res["listed"]),
                        "candidates": res["candidates"], "sec": round(time.time() - t0, 1)}
json.dump(out, open("out/extra.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
