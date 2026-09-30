"""Independent re-judge. Seeded 1/3 sample (min 15) of flagged lines -> prompt with the line + line number + full note +
the same program diff the judge saw; the reviewer can Read/Grep/Glob code snapshots of the commit (after/) and its parent
(before/). The reviewer is NOT told the line was flagged by a tool nor given my verdict."""
import sys, json, csv, random, os, subprocess, math
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from vcommon import *

REVIEW_Q = """請判斷一篇知識筆記裡的某一行,在一次程式提交之後是否仍然成立。

材料:
(一) 這次提交的程式 diff(只含這篇筆記負責的程式檔;超過上限時有截斷,截斷處有註明)。
(二) 這篇筆記在這次提交之後的全文,每行開頭是行號。
(三) 你可以用 Read / Grep / Glob 讀程式碼快照:目前目錄下 `after/` 是這次提交之後的程式碼,`before/` 是這次提交之前(父提交)的程式碼。只有程式檔,沒有筆記。

要判斷的是第 {line} 行:
> {text}

請把這一行歸成下面四類之一:
- DRIFT:這次提交讓它不成立(提交前它與程式相符,提交後不符)。
- PRE:提交後它與程式不符,但不是這次提交造成的(提交前就已經不符,或不符的原因與這次改動無關)。
- BORDER:邊界情況,說得通也說不通(例如用詞含糊、只有部分不準、要看怎麼解讀)。
- HOLDS:提交後仍然成立;或這一行不是在描述程式現況(例如明寫已撤除/已失效、只是記錄過去某次當時的情形)。

必要時去讀快照裡的程式確認,不要只憑 diff 猜。先簡短說明依據(引用你讀到的程式或 diff 行),最後一行只寫:VERDICT: DRIFT|PRE|BORDER|HOLDS 其中之一。

===== (一) 程式 diff(提交 {commit}) =====
{diff}
===== (二) 筆記 {note}(提交 {commit} 之後) =====
{notetext}
"""

def export(repo, commit, dest):
    if os.path.isdir(dest): return
    os.makedirs(dest)
    if repo.name == "rtb":
        paths = [p for p in ("src", "tests", "scripts") if repo.git("ls-tree", commit, p, check=False).strip()]
    else:
        code = repo.code_files(commit)
        dirs = {"scripts"} | {f.rsplit("/", 1)[0] for f in code if not f.startswith("scripts/")}
        paths = sorted(d for d in dirs if repo.git("ls-tree", commit, d, check=False).strip())
    a = subprocess.run(["git", "-C", repo.path, "archive", commit, *paths], capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", dest], input=a.stdout, check=True)

if __name__ == "__main__":
    repos = {"rtb": Repo("rtb"), "tool": Repo("tool")}
    rows = list(csv.DictReader(open(VAL + "/flagged.tsv"), delimiter="\t"))
    keyed = sorted({(r["unit"], int(r["line"])): r for r in rows}.items())
    k = max(15, math.ceil(len(keyed) / 3)); k = min(k, len(keyed))
    pick = sorted(random.Random(20261001).sample(keyed, k))
    os.makedirs(VAL + "/review/prompts", exist_ok=True); os.makedirs(VAL + "/review/outputs", exist_ok=True)
    with open(VAL + "/review/sample.tsv", "w") as f:
        f.write("rid\tunit\trepo\tcommit\tnote\tline\n")
        for i, ((unit, line), r) in enumerate(pick):
            repo = repos[r["repo"]]; c = r["commit"]
            parent = repo.git("rev-parse", c + "^").strip()
            base = f"{VAL}/review/snap/{r['repo']}_{c}"
            export(repo, c, base + "/after"); export(repo, parent, base + "/before")
            _, meta = build_v3(repo, c, r["note"])
            text = repo.note_at(c, r["note"])
            given = meta["home_files"] + meta["orphan_tests"]
            diff, *_ = truncated_diff(repo, c, given)
            ltxt = text.split("\n")[line - 1]
            p = REVIEW_Q.format(line=line, text=ltxt, commit=c, diff=diff, note=r["note"], notetext=numbered(text))
            rid = f"V{i+1:02d}"
            open(f"{VAL}/review/prompts/{rid}.txt", "w").write(p)
            f.write(f"{rid}\t{unit}\t{r['repo']}\t{c}\t{r['note']}\t{line}\n")
    print("flagged lines", len(keyed), "sampled", k)
