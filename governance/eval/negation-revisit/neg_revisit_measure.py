#!/usr/bin/env python3
"""否定現況句配回頭條件:上線前量測(計劃 Projects/否定現況句配回頭條件_計劃)。

問的是:如果筆記形狀擋多一種形狀——「新寫的『還沒有/尚未…』現況句,同一處沒有回頭條件就提醒」——
在歷史上會提醒多少行、其中多少已經配了、字眼表誤觸多少。只讀 git,不擋、不寫任何 repo。
零依賴;行的區塊、圍欄、行內程式碼、REVISIT 判定借 scripts/lumos 的同一批函式(跟 note-shape 一致)。

用法(repo 要是完整 clone,只讀):
  python3 neg_revisit_measure.py scan --repo <clone> --vault <圖譜路徑> (--head <提交> --n 300 | --commits <清單檔>) --tag tc --out hits.jsonl
  python3 neg_revisit_measure.py rtb182 --rtb <rtb clone> --out rtb182.txt     # 舊句實驗同一組 182 個提交
  python3 neg_revisit_measure.py summary --hits a.jsonl [b.jsonl ...] [--labels labels.json]
  python3 neg_revisit_measure.py sample --hits a.jsonl b.jsonl --pool narrow|broadonly --n 30 --seed 20260930
"""
import argparse
import importlib.machinery
import importlib.util
import json
import random
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TC_ROOT = HERE.parents[2]


def _load_lumos():
    p = str(TC_ROOT / "scripts" / "lumos")
    loader = importlib.machinery.SourceFileLoader("lumos_mod", p)
    spec = importlib.util.spec_from_loader("lumos_mod", loader)
    m = importlib.util.module_from_spec(spec)
    sys.modules["lumos_mod"] = m
    loader.exec_module(m)
    return m


LM = _load_lumos()

# ── 字眼表 ──
# 窄表=計劃提議的規則要認的字眼:講「現在缺、之後會有」的時間性否定。寬表=窄表加上一般否定字(對照組,量誤觸)。
NARROW_ZH = ("還沒", "尚未", "仍未", "尚無", "暫無", "待補", "目前沒有", "現在沒有", "目前無", "目前還不",
             "現在還不", "未實作", "未上線", "未接", "未做", "未支援", "未完成", "未定義", "未補")
NARROW_EN = ("not yet", "TODO", "TBD", "yet to")
BROAD_ZH = ("沒有", "沒", "未", "不存在", "缺", "無", "不會")
BROAD_EN = ("missing", "no", "lack", "lacks", "absent", "does not exist", "doesn't exist")
# 否定字眼其實不是在講缺東西的固定組合(從窄寬兩表的比對裡先扣掉;量測也分開算它們誤觸幾次)
NOT_LACK = ("未來", "有沒有", "未必", "無論", "無法", "並無", "沒問題", "沒有問題", "無誤", "無關", "無妨",
            "毫無", "無效", "無窮", "未知", "未曾", "未經", "no-verify", "no longer")
HIST_MARK = ("當時", "原本", "原先", "曾", "之前", "以前", "那時", "起初", "後來", "已補", "已修", "修掉",
             "改成", "改為", "已經有", "現在有了", "已上線", "已做完")
RULE_MARK = ("不准", "不要", "別", "禁止", "不得", "勿", "一律不", "不應")


def _rx(words):
    parts = []
    for w in sorted(set(words), key=len, reverse=True):
        e = re.escape(w)
        parts.append(r"(?<![A-Za-z0-9_-])" + e + r"(?![A-Za-z0-9_-])" if w.isascii() else e)
    return re.compile("|".join(parts), re.I)


RX_NARROW = _rx(NARROW_ZH + NARROW_EN)
RX_BROAD = _rx(BROAD_ZH + BROAD_EN)
RX_NOTLACK = _rx(NOT_LACK)
RX_HIST = _rx(HIST_MARK)
RX_RULE = _rx(RULE_MARK)
CLAUSE_CUT = re.compile(r"[。;；!?！？]")


def _mask_notlack(s):
    """把不是在講缺東西的固定組合遮掉,回 (遮後字串, 遮掉幾處)。"""
    n = [0]

    def rep(m):
        n[0] += 1
        return "\0" * len(m.group(0))
    return RX_NOTLACK.sub(rep, s), n[0]


def _clause_at(s, pos):
    a = 0
    for m in CLAUSE_CUT.finditer(s):
        if m.end() <= pos:
            a = m.end()
        else:
            return s[a:m.start()]
    return s[a:]


QUOTE_PAIRS = (("「", "」"), ("『", "』"), ("“", "”"), ("\"", "\""))
# 「還沒 X 的 Y」「還沒 X 時/前 …」「還沒 X → …」:否定字眼在修飾語或條件子句裡,講的是程式怎麼處理「還沒 X」的資料,不是現況缺東西
RX_MODIFIER = re.compile(r"^[^,，、。;；:：()（）「」]{0,8}?(的|時|前|→)")
# 工具自己寫的預告句(guard plan 寫、guard settle 轉正時改寫;存量漂移甲 c1 已經管)
TEMPLATE_MARKS = ("TEST:還沒有測試在守這條", "]預告這條合約但還沒做:")


def _in_quote(s, pos):
    for a, b in QUOTE_PAIRS:
        depth = 0
        for ch in s[:pos]:
            if a == b and ch == a:
                depth ^= 1
            elif ch == a:
                depth += 1
            elif ch == b and depth:
                depth -= 1
        if depth:
            return True
    return False


def _live(masked, m):
    """這一處否定字眼算不算「在講現況缺東西」:不在引號裡(是在提這個字)、不在修飾語或條件子句裡。"""
    if _in_quote(masked, m.start()):
        return False
    return not RX_MODIFIER.match(masked[m.end():])


def classify_text(probe):
    """一行看得見的字 → 比對結果 dict(沒有任何否定字眼回 None)。
    narrow/broad 是字面命中;narrow_live 是扣掉引號內、修飾語與條件子句之後還在的窄表命中(細化規則用)。"""
    masked, n_notlack = _mask_notlack(probe)
    nar = list(RX_NARROW.finditer(masked))
    bro = list(RX_BROAD.finditer(masked))
    if not nar and not bro and not n_notlack:
        return None
    live = [m for m in nar if _live(masked, m)]
    hits = live or nar or bro
    clauses = [_clause_at(masked, m.start()) for m in hits]
    return {
        "narrow": sorted({m.group(0) for m in nar}),
        "narrow_live": sorted({m.group(0) for m in live}),
        "broad": sorted({m.group(0) for m in bro}),
        "notlack": n_notlack,
        "hist": any(RX_HIST.search(c) for c in clauses),
        "rule": any(RX_RULE.search(c) for c in clauses),
        "template": any(t in probe for t in TEMPLATE_MARKS),
        "inline_revisit": "REVISIT:" in probe,
    }


# ── 第三版判定(設計審 r1 折入後;計劃〈做法〉1 照這一版)──
# 跟上面細化版的差別:①歷史/規則字眼只看否定字眼所在的那一小段(逗號、頓號、冒號、括號、破折號、英文句點也切),
# 引號裡的字與 RULE 等行內欄位([since:…][retire:…]…)不算,歷史字眼要出現在否定字眼前面才算,規則字眼拿掉「別」;
# ②修飾語按字眼種類與位置判:講「有沒有」的(目前沒有、還沒有、尚無…)後面接「的」不算修飾語,時/前要接斷句或虛詞才算;
# ③英文 TODO/TBD/Todo 分大小寫,另認「not/no/n't … yet」;④不看 decisions 區塊、RETIRE-IF 行與「為什麼還不做:」樣板。
NARROW_V3_EN_CS = ("TODO", "TBD", "Todo")
NARROW_V3_EN_CI = ("not yet", "yet to")
RULE_MARK_V3 = tuple(w for w in RULE_MARK if w != "別")
EXIST_TOKENS = ("目前沒有", "現在沒有", "尚無", "暫無", "目前無")
FIELD_RX = re.compile(r"\[(?:since|retire|until|confirmed|status|applies|test|audit|kill|rollback|guard|src|git|manual|by|"
                      r"來源|when-[a-z]+):[^\]]*\]")
SEG_CUT_V3 = re.compile(r"[。;；!?！？,，、:：()（）]|——|—|\.(?=\s|$)")
RX_NARROW_V3 = re.compile("|".join(
    [re.escape(w) for w in sorted(NARROW_ZH, key=len, reverse=True)]
    + [r"(?<![A-Za-z0-9_-])" + re.escape(w) + r"(?![A-Za-z0-9_-])" for w in NARROW_V3_EN_CS]
    + [r"(?i:(?<![A-Za-z0-9_-])" + re.escape(w) + r"(?![A-Za-z0-9_-]))" for w in NARROW_V3_EN_CI]
    + [r"(?i:(?<![A-Za-z])(?:not|no|n't)(?![A-Za-z])[^.;,!?]{0,40}?(?<![A-Za-z])yet(?![A-Za-z]))"]))
RX_HIST_V3 = re.compile("|".join(re.escape(w) for w in sorted(HIST_MARK, key=len, reverse=True)))
RX_RULE_V3 = re.compile("|".join(re.escape(w) for w in sorted(RULE_MARK_V3, key=len, reverse=True)))
MOD_BREAK = set(" \t,，、。;；:：!?！？()（）「」『』") | set("就才會要先再也都便即")
MOD_STOP = set(",，、。;；:：()（）「」『』“”\"") | {" "}
TEMPLATE_V3 = ("TEST:還沒有測試在守這條", "]預告這條合約但還沒做:")


def _quote_spans(s):
    spans = []
    for a, b in QUOTE_PAIRS:
        start = None
        for i, ch in enumerate(s):
            if start is None and ch == a:
                start = i
            elif start is not None and ch == b and i != start:
                spans.append((start, i + 1))
                start = None
    return spans


def _is_modifier_v3(masked, m):
    """否定字眼後面(不跨標點與空白、最多 8 字)有沒有接修飾語或條件子句的記號。"""
    tok = m.group(0)
    exist = tok in EXIST_TOKENS or (tok == "還沒" and masked[m.end():m.end() + 1] == "有")
    for j in range(m.end(), min(len(masked), m.end() + 9)):
        ch = masked[j]
        if ch in MOD_STOP:
            return False
        if ch == "→" or masked[j:j + 3] == "的時候":
            return True
        if ch == "的" and not exist:
            return True
        if ch in "時前":
            nxt = masked[j + 1:j + 2]          # 看整行的下一個字,不是視窗的(設計審 r2 正確性 F7)
            if nxt == "" or nxt in MOD_BREAK:
                return True
    return False


def _segment(s, pos):
    a = 0
    for m in SEG_CUT_V3.finditer(s):
        if m.end() <= pos:
            a = m.end()
        elif m.start() > pos:
            return a, m.start()
    return a, len(s)


def classify_v3(probe):
    """第三版:一行看得見的字 → {narrow, live, kept}(沒有窄表字眼回 None)。
    live=不在引號裡、不是修飾語的那幾處;kept=live 裡、所在那一小段沒有規則字眼、前面沒有歷史字眼的那幾處。"""
    s = FIELD_RX.sub(lambda m: "\0" * len(m.group(0)), probe)
    masked, _n = _mask_notlack(s)
    nar = list(RX_NARROW_V3.finditer(masked))
    if not nar:
        return None
    spans = _quote_spans(masked)
    unq = list(masked)
    for a, b in spans:
        for k in range(a, b):
            unq[k] = "\0"
    unq = "".join(unq)
    live = [m for m in nar if not any(a <= m.start() < b for a, b in spans) and not _is_modifier_v3(masked, m)]
    kept = []
    for m in live:
        a, b = _segment(masked, m.start())
        seg_before, seg = unq[a:m.start()], unq[a:b]
        if RX_RULE_V3.search(seg) or RX_HIST_V3.search(seg_before):
            continue
        kept.append(m)
    return {"narrow": sorted({m.group(0) for m in nar}), "live": sorted({m.group(0) for m in live}),
            "kept": sorted({m.group(0) for m in kept})}


def excluded_v3(probe, region):
    """第三版不看的行 → 原因字串或 None。列表與引用記號用 scripts/lumos 的 `_REVISIT_MARK_RE`(全檔唯一那一份,
    設計審 r2 架構對齊 F4),不自己另寫。"""
    t = probe.strip()
    if region not in ("body", "summary"):
        return "region"
    bare = LM._REVISIT_MARK_RE.sub("", t, count=1)
    if any(x in t for x in TEMPLATE_V3) or bare.startswith("為什麼還不做:"):
        return "template"
    if bare.startswith("RETIRE-IF:"):
        return "retire"
    return None


# ── git ──


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo, "-c", "core.quotePath=off", *args], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={r.returncode}: {r.stderr[:300]!r}")
    return r.stdout.decode("utf-8", "replace")


HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def added_lines(repo, parent, commit, vault, renames=False):
    """這個提交在圖譜 .md 新增或改寫的行 → {路徑: {新行號}}。預設 --no-renames(改名過來的整篇算新寫;第一、二版與
    第三版的數字都是這個口徑);renames=True 用 -M,跟 note-shape 提交前的 `_ns_diff` 一致(上線後重放用)。"""
    out, cur, ln = {}, None, 0
    diff = git(repo, "diff", "--unified=0", "-M" if renames else "--no-renames", "--no-color", "--no-ext-diff",
               parent, commit, "--", vault)
    for line in diff.split("\n"):
        if line.startswith("+++ "):
            p = line[4:]
            cur = p[2:] if p.startswith("b/") and p.endswith(".md") else None
            continue
        m = HUNK_RE.match(line)
        if m:
            ln = int(m.group(1))
            continue
        if cur and line.startswith("+"):
            out.setdefault(cur, set()).add(ln)
            ln += 1
    return out


def _revisit_near(lines, regions, i, span=3):
    """第 i 行(從 1 起)前後 span 行、同一區塊裡有沒有 REVISIT:回 'cond'/'date'/None(有條件式優先)。"""
    kinds = set()
    for j in range(max(1, i - span), min(len(lines), i + span) + 1):
        if j == i or regions[j - 1] != regions[i - 1]:
            continue
        k, _r = LM._revisit_split(LM._strip_inline_markup(lines[j - 1])[0])
        if k in ("cond", "date"):
            kinds.add(k)
    return "cond" if "cond" in kinds else ("date" if "date" in kinds else None)


def _shape(probe):
    t = probe.lstrip()
    if t.startswith("|"):
        return "table"
    if t.startswith("#"):
        return "heading"
    m = re.match(r"^(?:[-*+]\s+)?([A-Z][A-Z-]+):", t)
    return m.group(1) if m else "prose"


def scan_note(text, new_nos):
    """一篇筆記終點全文 + 新行號 → 命中列。"""
    lines = text.split("\n")
    regions = LM._notelines_regions(text)
    vis = {no for no, _l in LM._visible_lines(lines)}
    note_has_cond = any(LM._revisit_split(LM._strip_inline_markup(x)[0])[0] == "cond" for x in lines)
    rows, stats = [], Counter()
    for i in sorted(new_nos):
        if i < 1 or i > len(lines) or regions[i - 1] == "other" or i not in vis:
            continue
        probe = LM._strip_inline_markup(lines[i - 1])[0]
        if not probe.strip():
            continue
        if LM._revisit_split(probe)[0] is not None:
            stats["revisit_lines"] += 1
            continue
        stats["lines"] += 1
        c = classify_text(probe)
        c3 = classify_v3(probe)
        if c is None and c3 is None:
            continue
        if c is None:
            c = {"narrow": [], "narrow_live": [], "broad": [], "notlack": 0, "hist": False, "rule": False,
                 "template": False, "inline_revisit": "REVISIT:" in probe}
        c["v3"] = c3
        c["v3_excluded"] = excluded_v3(probe, regions[i - 1])
        c.update({"line": i, "region": regions[i - 1], "shape": _shape(probe), "text": lines[i - 1].strip()[:240],
                  "paired": _revisit_near(lines, regions, i), "note_has_cond": note_has_cond})
        rows.append(c)
    return rows, stats


def cmd_scan(a):
    if a.commits:
        commits = [x.strip() for x in Path(a.commits).read_text().split() if x.strip()]
    else:
        commits = git(a.repo, "log", "--no-merges", "--format=%H", f"-{a.n}", a.head).split()
    tot, fh = Counter(), open(a.out, "w", encoding="utf-8")
    for c in commits:
        parents = git(a.repo, "log", "-1", "--format=%P", c).split()
        if not parents:
            continue
        tot["commits"] += 1
        per = added_lines(a.repo, parents[0], c, a.vault, renames=a.renames)
        tot["commits_touching_notes"] += bool(per)
        date = git(a.repo, "log", "-1", "--format=%ad", "--date=short", c).strip()
        for p, nos in per.items():
            text = git(a.repo, "show", f"{c}:{p}")
            rows, st = scan_note(text, nos)
            tot.update(st)
            for r in rows:
                r.update({"repo": a.tag, "commit": c[:8], "date": date, "note": p[len(a.vault) + 1:]})
                r["id"] = f"{a.tag}:{c[:8]}:{r['note']}:{r['line']}"
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    fh.write(json.dumps({"_meta": dict(tot), "tag": a.tag}, ensure_ascii=False) + "\n")
    fh.close()
    print(json.dumps(dict(tot), ensure_ascii=False))
    return 0


def cmd_rtb182(a):
    sys.path.insert(0, str(TC_ROOT / "governance" / "eval" / "drift-exam" / "old-sentence"))
    import old_sentence_exp as exp    # 同一組提交:067f005 以前、非合併、動到 .py
    ctx = exp.Ctx(a.rtb, exp.RTB_VAULT)
    cs = exp._rtb_code_commits(argparse.Namespace(skip_sweep=False, limit=None), ctx)
    Path(a.out).write_text("\n".join(cs) + "\n")
    print(len(cs))
    return 0


def load_hits(paths):
    rows, metas = [], {}
    for p in paths:
        for ln in Path(p).read_text(encoding="utf-8").splitlines():
            d = json.loads(ln)
            if "_meta" in d:
                metas[d["tag"]] = d["_meta"]
            else:
                rows.append(d)
    return rows, metas


def funnel(rows, refined=True):
    """窄表命中 →(細化:扣工具預告句 → 扣引號/修飾語/條件子句)→ 扣歷史 → 扣規則句 → 扣已配 = 會被提醒。
    refined=False 是第一版(只有窄表、歷史、規則、已配),留著對照。回 (各階段計數, 會被提醒的列)。"""
    rows = [r for r in rows if r["narrow"] or r["broad"] or r["notlack"]]   # 只有第三版命中的列不進前兩版
    st = {"broad_or_narrow": len(rows)}
    cur = [r for r in rows if r["narrow"]]
    st["narrow"] = len(cur)
    if refined:
        cur = [r for r in cur if not r["template"]]
        st["minus_template"] = len(cur)
        cur = [r for r in cur if r["narrow_live"]]
        st["minus_quote_modifier"] = len(cur)
    cur = [r for r in cur if not r["hist"]]
    st["minus_hist"] = len(cur)
    cur = [r for r in cur if not r["rule"]]
    st["minus_rule"] = len(cur)
    st["paired_cond"] = sum(r["paired"] == "cond" for r in cur)
    st["paired_date"] = sum(r["paired"] == "date" for r in cur)
    if refined:    # 第一版沒認行內的 REVISIT(第一次抽樣就是從那個母體抽的,照留才能重現)
        st["paired_inline"] = sum(bool(r["inline_revisit"]) and not r["paired"] for r in cur)
        remind = [r for r in cur if not r["paired"] and not r["inline_revisit"]]
    else:
        remind = [r for r in cur if not r["paired"]]
    st["remind"] = len(remind)
    return st, remind


def funnel_v3(rows):
    """第三版:窄表命中 → 扣不看的行(區塊、樣板、RETIRE-IF)→ 扣引號與修飾語 → 扣規則句與歷史句 = 會提醒。
    「已配」只認那一行本身是條件式回頭條件,而 REVISIT 行本來就不看,所以沒有「扣已配」這一步。
    回 (各階段計數, 會提醒的列, 修飾語或引號這步丟掉的列, 規則或歷史這步丟掉的列)。"""
    cur = [r for r in rows if r.get("v3")]
    st = {"narrow": len(cur)}
    cur = [r for r in cur if not r.get("v3_excluded")]
    st["minus_excluded"] = len(cur)
    drop_mod = [r for r in cur if not r["v3"]["live"]]
    cur = [r for r in cur if r["v3"]["live"]]
    st["minus_quote_modifier"] = len(cur)
    drop_hr = [r for r in cur if not r["v3"]["kept"]]
    cur = [r for r in cur if r["v3"]["kept"]]
    st["remind"] = len(cur)
    return st, cur, drop_mod, drop_hr


def _per_repo(rows, metas):
    for tag in sorted({r["repo"] for r in rows} | set(metas)):
        rs = [r for r in rows if r["repo"] == tag]
        f1, _r1 = funnel(rs, refined=False)
        f, remind = funnel(rs)
        by_commit = Counter(r["commit"] for r in remind)
        print(f"\n[{tag}] meta={metas.get(tag)}")
        print("  漏斗(第一版):", json.dumps(f1, ensure_ascii=False))
        print("  漏斗(細化):", json.dumps(f, ensure_ascii=False))
        print(f"  有提醒的提交 {len(by_commit)};每個有提醒的提交行數 中位 "
              f"{sorted(by_commit.values())[len(by_commit) // 2] if by_commit else 0} 最多 {max(by_commit.values(), default=0)}")
        s3, rem3, _dm, _dh = funnel_v3(rs)
        bc3 = Counter(r["commit"] for r in rem3)
        v3c = sorted(bc3.values())
        print("  漏斗(第三版):", json.dumps(s3, ensure_ascii=False),
              f"有提醒的提交 {len(bc3)} 中位 {v3c[len(v3c) // 2] if v3c else 0} 最多 {max(v3c, default=0)}",
              " 形狀:", dict(Counter(r["shape"] for r in rem3).most_common(6)))
        print("  區塊:", dict(Counter(r["region"] for r in remind)), " 形狀:", dict(Counter(r["shape"] for r in remind).most_common(8)))
        print("  窄表字眼(提醒列):", dict(Counter(w for r in remind for w in r["narrow"]).most_common(20)))
        print("  寬表字眼(全部命中列):", dict(Counter(w for r in rs for w in r["broad"]).most_common(20)))
        print("  固定組合被扣掉的行:", sum(1 for r in rs if r["notlack"]))


def _label_table(rows, labels):
    byid = {r["id"]: r for r in rows}
    for pool in ("narrow", "refined", "broadonly", "v3", "v3drop"):
        ls = [v for k, v in labels.items() if v.get("pool") == pool]
        if not ls:
            continue
        cnt = Counter(v["label"] for v in ls)
        print(f"\n[人工判 {pool}] n={len(ls)} ", dict(cnt))
        print("  真的那幾行該配哪種條件:", dict(Counter(v["key"] for v in ls if v["label"] == "T")))
        if pool == "broadonly":
            tok = Counter()
            for k, v in labels.items():
                if v.get("pool") == pool and v["label"] != "T" and k in byid:
                    tok.update(byid[k]["broad"])
            print("  寬表誤觸(非真列)各字眼出現次數:", dict(tok.most_common()))


def cmd_summary(a):
    rows, metas = load_hits(a.hits)
    _per_repo(rows, metas)
    for refined in (False, True):
        f, _r = funnel(rows, refined=refined)
        print(f"\n[合計] 漏斗({'細化' if refined else '第一版'}):", json.dumps(f, ensure_ascii=False))
    print("\n[合計] 漏斗(第三版):", json.dumps(funnel_v3(rows)[0], ensure_ascii=False))
    if a.labels:
        _label_table(rows, json.loads(Path(a.labels).read_text(encoding="utf-8")))
    return 0


def cmd_sample(a):
    """narrow=第一版會提醒的列;refined=細化後會提醒的列(--exclude 排掉已判過的,當留出樣本);broadonly=只中寬表、沒中窄表的列。"""
    rows, _m = load_hits(a.hits)
    if a.pool == "narrow":
        pool = funnel(rows, refined=False)[1]
    elif a.pool == "refined":
        pool = funnel(rows)[1]
    elif a.pool == "v3":
        pool = funnel_v3(rows)[1]
    elif a.pool == "v3drop":
        _s, _k, dm, dh = funnel_v3(rows)
        pool = dm + dh
    else:
        pool = [r for r in rows if not r["narrow"] and r["broad"] and not r["paired"]]
    if a.exclude:
        seen = set(json.loads(Path(a.exclude).read_text(encoding="utf-8")))
        pool = [r for r in pool if r["id"] not in seen]
    rnd = random.Random(a.seed)
    pick = rnd.sample(sorted(pool, key=lambda r: r["id"]), min(a.n, len(pool)))
    print(f"# pool={a.pool} 母體 {len(pool)} 抽 {len(pick)} seed={a.seed}")
    for r in pick:
        print(json.dumps({"id": r["id"], "narrow": r["narrow"], "broad": r["broad"], "text": r["text"]}, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--repo", required=True)
    s.add_argument("--vault", required=True)
    s.add_argument("--head", default="HEAD")
    s.add_argument("--n", type=int, default=300)
    s.add_argument("--commits")
    s.add_argument("--tag", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--renames", action="store_true", help="用 -M 取新行(跟 note-shape 提交前一致;上線後重放用)")
    r = sub.add_parser("rtb182")
    r.add_argument("--rtb", required=True)
    r.add_argument("--out", required=True)
    m = sub.add_parser("summary")
    m.add_argument("--hits", nargs="+", required=True)
    m.add_argument("--labels")
    p = sub.add_parser("sample")
    p.add_argument("--hits", nargs="+", required=True)
    p.add_argument("--pool", choices=("narrow", "refined", "broadonly", "v3", "v3drop"), required=True)
    p.add_argument("--exclude", help="已判過的 id 清單(JSON 陣列檔)")
    p.add_argument("--n", type=int, default=30)
    p.add_argument("--seed", type=int, default=20260930)
    a = ap.parse_args()
    return {"scan": cmd_scan, "rtb182": cmd_rtb182, "summary": cmd_summary, "sample": cmd_sample}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
