import sys, json, csv
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from vcommon import *
repos = {"rtb": Repo("rtb"), "tool": Repo("tool")}
tot = 0
for row in csv.DictReader(open(VAL + "/units.tsv"), delimiter="\t"):
    p, m = build_v3(repos[row["repo"]], row["commit"], row["note"])
    m["unit"] = row["unit"]
    open(f"{VAL}/prompts/{row['unit']}.txt", "w").write(p)
    json.dump(m, open(f"{VAL}/prompts/{row['unit']}.meta.json", "w"), ensure_ascii=False, indent=1)
    tot += len(p)
    print(row["unit"], m["prompt_chars"], m["diff_chars_given"], m["diff_chars_full"], m["diff_truncated"], m["note_chars"], len(m["home_files"]), m["orphan_tests"], m["note"])
print("total chars", tot)
