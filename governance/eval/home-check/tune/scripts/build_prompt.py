import sys, re, json
sys.path.insert(0, __file__.rsplit("/",1)[0])
from common import *

DIFF_CAP = 100_000  # chars of program diff per prompt

def split_diff(d):
    parts = re.split(r"(?m)^(?=diff --git )", d)
    return [p for p in parts if p.strip()]

def truncated_diff(commit, files, cap=DIFF_CAP):
    if not files:
        return "(無)", False, 0, 3
    d = git("show", "--format=", "-U3", commit, "--", *files)
    total = len(d)
    for u in (3, 1, 0):
        d = git("show", "--format=", f"-U{u}", commit, "--", *files)
        if len(d) <= cap:
            return d, u != 3, total, u
    parts = split_diff(d)
    order = sorted(range(len(parts)), key=lambda i: len(parts[i]))
    out = [None]*len(parts); remaining = cap; left = len(parts)
    for i in order:
        share = remaining // left
        p = parts[i]
        if len(p) <= share:
            out[i] = p
        else:
            cut = p[:share]; cut = cut[:cut.rfind("\n")+1]
            omitted = p[len(cut):].count("\n")
            out[i] = cut + f"[截斷:本檔 diff 另有 {omitted} 行未列出]\n"
        remaining -= len(out[i]); left -= 1
    return "".join(out), True, total, 0

def numbered(text):
    return "\n".join(f"{i+1:4d}| {l}" for i, l in enumerate(text.split("\n")))

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]{3,}")
def relevant_lines(note_text, diff_text, keep_banner=False):
    """V2: keep only note blocks mentioning a distinctive identifier from +/- diff lines."""
    toks = set()
    for l in diff_text.splitlines():
        if (l.startswith("+") or l.startswith("-")) and not l.startswith(("+++", "---")):
            for t in IDENT.findall(l):
                if "_" in t or re.search(r"[a-z][A-Z]", t) or t.isupper():
                    toks.add(t)
    lines = note_text.split("\n")
    # blocks: split on blank lines / headings; frontmatter summary lines each own block
    keep = set()
    blocks, cur = [], []
    for i, l in enumerate(lines):
        if not l.strip() or l.startswith("#"):
            if cur: blocks.append(cur); cur = []
            if l.startswith("#"):
                keep.add(i)
                if keep_banner:  # V4: keep the section's first non-blank line (where retraction banners live)
                    for j in range(i+1, min(i+4, len(lines))):
                        if lines[j].strip() and not lines[j].startswith("#"):
                            keep.add(j); break
            continue
        if l.startswith("  ") and re.match(r"^\s+(WHY|RULE|PITFALL|KEY|FACT|FLOW|DEP|REVISIT|TEST)", l):
            if cur: blocks.append(cur); cur = []
            blocks.append([i]); continue
        cur.append(i)
    if cur: blocks.append(cur)
    hit = set()
    for b in blocks:
        s = "\n".join(lines[i] for i in b)
        if any(t in s for t in toks):
            hit.update(b)
    keep |= hit
    out = []; prev = -2
    for i in sorted(keep):
        if i != prev + 1: out.append("   …| (略)")
        out.append(f"{i+1:4d}| {lines[i]}"); prev = i
    return "\n".join(out), len(hit), len(toks)

HEAD = """你是知識筆記的校對員。下面有兩份材料:
(一) 一次提交的程式 diff。只含這篇筆記負責(about_code 列了)的程式檔{trunc}。這次提交另外改到的程式檔只列檔名:{others}
(二) 管這些程式檔的那篇知識筆記,是這次提交之後的版本{partial},每行開頭是行號。

問題:以下 diff 讓這篇筆記的哪幾行敘述變得不成立?逐行列出行號、原句、為什麼。{histrule}沒有就答「無」。
{extra}
輸出格式:先簡短說明,最後用一個 ```json 區塊給清單,每項 {{"line": 行號, "quote": "原句(節錄即可)", "why": "為什麼不成立"{evfield}}};沒有就給 []。

===== (一) 程式 diff =====
{diff}
===== (二) 筆記 {note}(提交 {commit} 之後) =====
{notetext}
"""

EXTRA_V1 = """
額外要求:每一項都必須引用 diff 裡的具體一行(以 + 或 - 開頭,逐字抄)當證據,說明那一行怎麼推翻筆記那句話。引用不出 diff 行的就不要列。
"""

_HM = {}
def _homes(commit):
    if commit not in _HM: _HM[commit] = homes_map(commit)
    return _HM[commit]

HIST_V3 = ("只有明寫「已撤除/已失效/已被取代/原寫…已失效」的句子或掛了這類橫幅的節才算歷史、不列。"
           "其他句子即使帶日期、放在「代碼審 rN」「Phase N」這類節裡,只要它用現在式描述程式現在怎麼做、"
           "綁了哪支測試([test:…])、或寫成規則(RULE/PITFALL/WHY 的現況部分),讀者就會當成現況,一律要檢查。")

def build(commit, note, variant="P0"):
    text = note_at(commit, note)
    ac = about_code(text)
    code = [f for f in changed_files(commit) if is_code(f)]
    mine = [f for f in code if f in ac]
    hm = _homes(commit)
    pkgs = {f.split("/")[2] for f in mine if f.startswith("src/rtb/") and f.count("/") >= 3}
    orphan_tests = [f for f in code if f.startswith("tests/") and f not in hm and f not in mine
                    and f.count("/") >= 2 and f.split("/")[1] in pkgs]
    given = mine + orphan_tests
    others = [f for f in code if f not in given]
    diff, trunc, total, ctx = truncated_diff(commit, given)
    others_s = "無" if not others else ("、".join(others[:40]) + (f" …等共 {len(others)} 支" if len(others) > 40 else ""))
    trunc_s = ""
    if orphan_tests:
        trunc_s += ",另加同套件目錄裡沒有家的測試檔(" + "、".join(orphan_tests) + ")"
    if trunc:
        trunc_s += f"(原始 diff {total} 字元,超過 {DIFF_CAP} 上限:上下文縮成 {ctx} 行" + (",仍超過的再各檔平均截斷,截掉處有註明" if "[截斷:" in diff else "") + ")"
    meta = {"commit": commit, "note": note, "variant": variant, "home_files": mine, "orphan_tests": orphan_tests, "diff_context": ctx, "diff_chars_given": len(diff), "other_code_files": len(others),
            "diff_chars_full": total, "diff_truncated": trunc, "note_lines": text.count("\n")+1}
    if variant in ("V2", "V4"):
        nt, nhit, ntok = relevant_lines(text, diff, keep_banner=(variant == "V4"))
        meta.update(v2_kept_lines=nhit, v2_tokens=ntok)
        partial = "的節錄(只留提到 diff 裡識別字的段落與所有標題,其他以「(略)」代替)"
    else:
        nt = numbered(text); partial = "全文"
    hist = HIST_V3 if variant in ("V3", "V4") else "講歷史的句子(帶日期的紀錄、已標撤除的節)不算。"
    p = HEAD.format(histrule=hist, trunc=trunc_s, others=others_s, partial=partial,
                    extra=EXTRA_V1 if variant == "V1" else "",
                    evfield=', "evidence": "引用的 diff 行"' if variant == "V1" else "",
                    diff=diff, note=note, commit=commit, notetext=nt)
    meta["prompt_chars"] = len(p)
    return p, meta

if __name__ == "__main__":
    cid, commit, note, variant = sys.argv[1:5]
    p, meta = build(commit, note, variant)
    open(f"{EXP}/prompts/{cid}.{variant}.txt", "w").write(p)
    json.dump(meta, open(f"{EXP}/prompts/{cid}.{variant}.meta.json", "w"), ensure_ascii=False, indent=1)
    print(cid, variant, meta["prompt_chars"], meta["diff_truncated"], meta.get("v2_kept_lines"))
