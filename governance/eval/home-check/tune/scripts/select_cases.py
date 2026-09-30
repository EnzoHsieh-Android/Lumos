import os
import json, sys
sys.path.insert(0, __file__.rsplit("/",1)[0])
from common import *
gt = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "stale-ref", "groundtruth.json")))
rows = []
for g in gt:
    c = g["invalidating"]
    ok = re.fullmatch(r"[0-9a-f]{7}", c)
    if not ok:
        rows.append((g["id"], g["note"], c, "-", "-", "-", "失效提交不是單一提交")); continue
    files = changed_files(c)
    code = [f for f in files if is_code(f)]
    note_changed = f"{KB}/{g['note']}" in files
    text = note_at(c, g["note"])
    ac = about_code(text or "")
    inter = [f for f in code if f in ac]
    needle_present = [n for n in g["needles"] if text and n in text]
    rows.append((g["id"], g["note"], c, len(code), "Y" if note_changed else "N", len(inter), ";".join(inter[:6]), "needle在提交後版本:" + str(len(needle_present)) + "/" + str(len(g["needles"]))))
with open(EXP + "/case_selection.tsv", "w") as f:
    f.write("id\tnote\tinv_commit\tcode_files_changed\tnote_changed_in_commit\thome_overlap_count\toverlap_files\tneedle\n")
    for r in rows:
        f.write("\t".join(map(str, r)) + "\n")
print(open(EXP + "/case_selection.tsv").read())
