#!/opt/homebrew/bin/python3
"""拆解被標段落:觸發名稱種類、筆記類別、段落種類;另算「只認定義名+檔名」子變體的標數與召回。"""
import collections, json, random, sys
EXP = sys.argv[1]
paras = [json.loads(l) for l in open(f"{EXP}/out/paragraphs.jsonl")]
kinds = json.load(open(f"{EXP}/out/name_kinds.json"))
gt = json.load(open(f"{EXP}/groundtruth.json"))
VARS = [k for k in paras[0] if k.startswith("V") and not k.endswith("|trig")]
out = {}
# 抽樣可重現性檢查
fl = [p for p in paras if p["V0_blame_max|now"]]
smp = random.Random(20260930).sample(fl, 30)
out["sample_ids"] = [f"{p['note']}:{p['start']}" for p in smp]

for v in VARS:
    f = [p for p in paras if p[v]]
    d = {"flagged": len(f)}
    d["by_kind"] = collections.Counter(p["kind"] for p in f)
    d["by_dir"] = collections.Counter(p["note"].split("/")[0] for p in f)
    d["n_trig_names_median"] = sorted(len(p[v + "|trig"]) for p in f)[len(f) // 2] if f else 0
    for sub, allowed in (("def_only", {"def"}), ("file_only", {"file"}), ("def+file", {"def", "file"}), ("tok_or_flag_only", {"tok", "flag"})):
        keep = [p for p in f if any(kinds.get(n) in allowed for n in p[v + "|trig"])]
        d["survive_" + sub] = len(keep)
    out[v] = d

# 子變體 S:只認定義名+檔名(不認只靠出現次數的字與命令列旗標)的召回
rec = {}
for v in VARS:
    hit = []
    for g in gt:
        ps = [p for p in paras if p["note"] == g["note"] and any(n in p["text"] for n in g["needles"])]
        ok = any(p[v] and any(kinds.get(n) in ("def", "file") for n in p[v + "|trig"]) for p in ps)
        on = any(p[v] and any(kinds.get(n) in ("def", "file") and any(h[:7] in g["inv_code"] for h in hs) for n, hs in p[v + "|trig"].items()) for p in ps)
        hit.append((g["id"], ok, on))
    rec[v] = {"flag": [i for i, ok, on in hit if ok], "on_target": [i for i, ok, on in hit if on]}
out["recall_def+file"] = rec
json.dump(out, open(f"{EXP}/out/breakdown.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
