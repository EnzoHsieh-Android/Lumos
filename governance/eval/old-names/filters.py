#!/opt/homebrew/bin/python3
"""最小修法的離線模擬(不改 lumos):用量測點筆記的 type/status 過濾發現,看全體筆數與已判樣本的真/不是怎麼變。"""
import json, sys, collections
sys.path.insert(0, ".")
import oldnames_ref as R
M = R.load()
for name, repo, tip, vault in (("rtb", "rtb", "c4daa8fce2cdd3f22dc703313d5928195adfeb1a", "docs/rtb-production-agent-demo-knowledge"),
                               ("tool", "tool", "70d0843d3fcc5e294a1a15629b44485f1abb553c", "docs/lumos-toolchain-knowledge")):
    env = M._drift_tree_env(repo, tip, vault)
    rows = [json.loads(l) for l in open(f"out/{name}.findings.jsonl")]
    J = {}
    for ln in open(f"out/{name}.judge.raw.tsv"):
        if ln.strip():
            i, v, *_ = ln.split("\t"); J[int(i)] = v
    def meta(r):
        n = env.notes[r["path"]]
        return (M._drift_str(n, "type"), M._drift_str(n, "status"))
    tally = collections.Counter(meta(r) for r in rows)
    print(f"== {name} 全體發現按 (type,status):", dict(tally))
    variants = {
        "A 原樣": lambda r: True,
        "F1 去 status superseded/archived": lambda r: meta(r)[1] not in ("superseded", "archived", "stale"),
        "F1+F2 再去 verification": lambda r: meta(r)[1] not in ("superseded", "archived", "stale") and meta(r)[0] != "verification",
        "F1+F2+F3 done 的 project 只看摘要": lambda r: meta(r)[1] not in ("superseded", "archived", "stale") and meta(r)[0] != "verification"
            and not (meta(r)[0] == "project" and meta(r)[1] == "done" and r["layer_reason"] != "summary"),
    }
    for k, f in variants.items():
        keep = [i for i, r in enumerate(rows) if f(r)]
        for suffix, sel in (("", keep), ("+B", [i for i in keep if rows[i]["B"]])):
            s = [i for i in sel if i in J]
            c = collections.Counter(J[i] for i in s)
            h = sum(1 for i in sel if rows[i]["layer"] == "handle")
            print(f"  {k}{suffix}: 全體 {len(sel)}(要處理 {h}/只列出 {len(sel)-h});樣本內 {len(s)} 筆 真{c['真']} 灰{c['灰']} 不是{c['不是']}")
