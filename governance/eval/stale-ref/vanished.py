#!/opt/homebrew/bin/python3
"""變體 V5:只在「段落提到的名稱,在段落寫下之後被刪掉(量測點已沒有定義/檔案)」時標。
名稱來源用 ever(歷史上出現過的也算),窗口分別用 blame_max 與 blame_min。"""
import json, random, sys
EXP = sys.argv[1]
paras = [json.loads(l) for l in open(f"{EXP}/out/paragraphs.jsonl")]
kinds = json.load(open(f"{EXP}/out/name_kinds.json"))
idx = json.load(open(f"{EXP}/out/now_index.json"))
now_def, now_paths = set(idx["now_defined"]), set(idx["now_paths"])
gt = json.load(open(f"{EXP}/groundtruth.json"))


def vanished(n):
    k = kinds.get(n)
    if k == "def":
        return n not in now_def
    if k == "file":
        return n[5:] not in now_paths
    return False


res = {}
for base in ("V0_blame_max|ever", "V1_blame_min|ever"):
    fl = [p for p in paras if p[base] and any(vanished(n) for n in p[base + "|trig"])]
    rec = []
    for g in gt:
        ps = [p for p in fl if p["note"] == g["note"] and any(nd in p["text"] for nd in g["needles"])]
        if ps:
            rec.append(g["id"])
    res[base] = {"flagged": len(fl), "recall_ids": rec}
    if base.startswith("V0"):
        smp = random.Random(20260930).sample(fl, min(15, len(fl)))
        res[base]["sample15"] = [{"note": p["note"], "start": p["start"], "end": p["end"],
                                  "vanished": {n: p[base + "|trig"][n] for n in p[base + "|trig"] if vanished(n)}} for p in smp]
json.dump(res, open(f"{EXP}/out/vanished.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "sample15"} for k, v in res.items()}, ensure_ascii=False, indent=1))
