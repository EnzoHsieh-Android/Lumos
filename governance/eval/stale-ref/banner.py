#!/opt/homebrew/bin/python3
"""變體 V5b / V0b:在 V5(名稱已消失)與 V0 之上,略過「所在章節標題或章節第一段帶撤除/失效/快照字樣」的段落。"""
import json, re, sys
EXP = sys.argv[1]
paras = [json.loads(l) for l in open(f"{EXP}/out/paragraphs.jsonl")]
kinds = json.load(open(f"{EXP}/out/name_kinds.json"))
idx = json.load(open(f"{EXP}/out/now_index.json"))
now_def, now_paths = set(idx["now_defined"]), set(idx["now_paths"])
gt = json.load(open(f"{EXP}/groundtruth.json"))
BAN = re.compile(r"撤除|已撤|已失效|快照|不是現況|已被取代|superseded")
banner = {}
by_note = {}
for p in paras:
    by_note.setdefault(p["note"], []).append(p)
for note, ps in by_note.items():
    cur = False; after_heading = 0
    for p in ps:
        if p["kind"] == "heading":
            cur = bool(BAN.search(p["text"])); after_heading = 1
        elif p["kind"] == "body":
            if after_heading == 1 and BAN.search(p["text"].split("\n")[0]):
                cur = True
            after_heading = 0
        banner[(note, p["start"])] = cur if p["kind"] in ("body", "heading") else False
def vanished(n):
    k = kinds.get(n)
    return (k == "def" and n not in now_def) or (k == "file" and n[5:] not in now_paths)
res = {}
for name, pred in (("V0b|now", lambda p: p["V0_blame_max|now"]),
                   ("V5b", lambda p: p["V0_blame_max|ever"] and any(vanished(n) for n in p["V0_blame_max|ever|trig"]))):
    fl = [p for p in paras if pred(p) and not banner[(p["note"], p["start"])]]
    rec = [g["id"] for g in gt if any(p["note"] == g["note"] and any(nd in p["text"] for nd in g["needles"]) for p in fl)]
    res[name] = {"flagged": len(fl), "recall_ids_raw": rec}
v = json.load(open(f"{EXP}/out/vanished.json"))["V0_blame_max|ever"]["sample15"]
res["V5_sample15_banner_auto"] = {f"V{i:02d}": banner[(s["note"], s["start"])] for i, s in enumerate(v, 1)}
s30 = json.load(open(f"{EXP}/out/sample30.json"))
res["V0_sample30_banner_auto"] = {f"{s['i']:02d}": banner[(s["note"], s["start"])] for s in s30}
json.dump(res, open(f"{EXP}/out/banner.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False))
