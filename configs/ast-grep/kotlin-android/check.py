#!/usr/bin/env python3
"""Kotlin 規則包自我檢查(Projects/Android協程與API寫法機械檢查標準_計劃 S1、S2)。

白話:每條規則拿自己的壞例樣本跑,要至少命中兩處;拿好例樣本跑,要零命中而且好例至少兩段;
規則訊息要以型錄裡真的有的編號開頭、不超過 120 字、寫明修法、不含 $ 變數;
另外有一棵「祖先目錄叫 test 的正式碼」樣本,只該掃測試碼的規則對它不准命中。

用法:python3 check.py [--sg <ast-grep 執行檔>] [--json]
退出碼:0 全過、1 有問題、2 找不到 ast-grep。零依賴(只用標準庫)。
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE.parents[2] / "skills" / "kotlin-idioms" / "checks-catalog.md"
# 三級:rules=會擋(error/warning);rules-review=語意覆核級(info,形狀分不出對錯、要盲判代理逐筆判,
# [[Projects/規則包語意覆核級命中走盲判_計劃]] 接上前不擋);rules-hints=提示級(hint,預設不接)
CONFIGS = (("rules", "sgconfig.yml"), ("rules-review", "sgconfig-review.yml"), ("rules-hints", "sgconfig-hints.yml"))
SEVERITIES = ("error", "warning", "info", "hint")
_DIR_SEVERITY = {"rules-hints": ("hint",), "rules-review": ("info",), "rules": ("error", "warning")}
MSG_MAX = 120          # 新增告警閘解析 SARIF 時把訊息截在 120 字
REVIEW_FP_PREFIX = "review-fp-"   # 好例樣本裡記「語意覆核級規則已知會誤報、要靠盲判排除」的檔名開頭
SCAN_TIMEOUT = 120     # 一次掃描的上限(秒);正常不到一秒,卡住時不要拖到外層測試逾時
# 好例「一段」= 頂格開頭的宣告(函式、類別、物件、介面、帶註記的宣告)
_DECL_RE = re.compile(r"^(?:@|fun |suspend fun |private |internal |public |class |data class |object |interface |abstract |open |sealed |enum |val |var |inline )")
# 檢查會談暫存區路徑(型錄落地時要拿掉)
_SCRATCH_RE = re.compile(r"(/private/tmp/|/tmp/claude-|lumos-scratch|scratchpad/)")
TEST_ONLY_ANCESTOR = HERE / "samples" / "ancestor-named-test"


def _strip_yaml_comment(ln):
    """去掉一行 YAML 的註解:`#` 在行首或前面是空白、而且不在引號裡才算註解(YAML 1.2 規格);整行註解變空行。"""
    q = None
    for i, ch in enumerate(ln):
        if q:
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
        elif ch == "#" and (i == 0 or ln[i - 1] in " \t"):
            return ln[:i].rstrip()
    return ln


def _files_block_is_test_only(doc):
    """這條規則的 files: 區塊(只看那一段,不看 ignores 或訊息)是不是只列測試目錄。"""
    # 先去掉註解(整行與行尾):註解裡提到 src/main 不算 files 區塊的內容,頂格註解也不該把區塊截斷
    doc = "\n".join(_strip_yaml_comment(ln) for ln in doc.splitlines())
    m = re.search(r"^files:(.*?)(?=^[A-Za-z_\"'][^\n]*:)", doc + "\nzz:", re.M | re.S)
    if not m:
        return False
    block = m.group(1)
    return bool(re.search(r"src/(test|androidTest|testFixtures)", block)) and "src/main" not in block


def load_rules():
    """讀三個規則目錄 → [{id, severity, message, dir, file}];同一檔多份文件以 --- 分隔。"""
    rules = []
    for d, cfg in CONFIGS:
        for f in sorted((HERE / d).glob("*.yml")):
            for doc in re.split(r"^---\s*$", f.read_text(encoding="utf-8"), flags=re.M):
                m = re.search(r"^id:\s*(\S+)", doc, re.M)
                if not m:
                    continue
                sev = re.search(r"^severity:\s*(\S+)", doc, re.M)
                msg = re.search(r"^message:\s*(.+)$", doc, re.M)
                text = msg.group(1).strip() if msg else ""
                if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
                    text = text[1:-1].replace("''", "'") if text[0] == "'" else text[1:-1]
                rules.append({"id": m.group(1), "severity": sev.group(1) if sev else "",
                              "message": text, "dir": d, "config": cfg, "file": f.name,
                              "test_only": _files_block_is_test_only(doc)})
    return rules


def catalog_ids():
    """型錄主表裡的編號(〈待查證〉節以後不算)。"""
    text = CATALOG.read_text(encoding="utf-8")
    cut = text.find("\n## 情境決策表")   # 主表在決策表之前;決策表的 D-n 與來源索引的編號都不是規則該引的編號
    main = text if cut < 0 else text[:cut]
    return {m.group(1) for m in map(_MAIN_ROW_RE.match, main.splitlines()) if m}, text


_CELL_RE = re.compile(r'(?<!\\)\|(?=(?:[^`]*`[^`]*`)*[^`]*$)')   # 反引號裡的直線不算欄位分隔
_MAIN_ROW_RE = re.compile(r"^\|\s*((?:API|FLOW|STATE|CO|UI|ARCH|DATA|TEST|PERF)-\d+)\s*\|")
_MAIN_COLS = 12      # 編號|名稱|壞寫法形狀|標準寫法|後果|現成規則|級|情境怎麼認|接電方式|通電批次|實測狀態|來源
# 決策表依表頭名稱取欄(scripts/lumos 的 _kt_decision_table 同一套);這幾欄一定要有
_DT_HEADER = ("列編號", "情境", "標準寫法", "不適用時", "觸發字", "證據樣式", "對應檢查", "來源")
_RETIRED = "(停用)"
_SWITCH = "(換列)"     # 「不適用時」格子的明確標記:這一列的例外是換到別列,不准選例外寫法
_WEAK_SRC = ("未開頁核對", "搜尋摘要", "無網址")
# 觸發字停用字表:這些字幾乎每支 Kotlin 檔都有,當觸發字會讓改檔前推列與情境題每次都亮(第二、三批計劃的依賴)
STOP_TRIGGERS = frozenset((
    "map", "filter", "forEach", "let", "run", "apply", "also", "with", "if", "else", "when", "try", "catch",
    "val", "var", "fun", "class", "object", "return", "suspend", "launch", "async", "await", "flow", "Flow",
    "collect", "first", "take", "list", "List", "remember", "enabled", "Job", "cancel", "data", "String",
    "Int", "Unit", "null", "true", "false", "this", "it", "get", "set", "value", "state", "State",
    # r1 接手席點名的(第二、三批設計審):型別名或方法名太泛,出現在大量無關程式裡
    "Exception", "Result", "Response", "insert", "offset", "sealed", "onClick", "isActive", "key", "test",
    "version", "size", "token", "edit", "Application", "Intent", "Context", "delay", "Dao", "Repository",
    # 第三批設計審 r2 通才席:幾乎每支 ViewModel 或資料層都有,當觸發字會讓每次推送都出一堆情境段
    "suspend fun", "StateFlow", "withContext", "viewModelScope", "Deferred", "Dispatchers.IO", "Dispatchers.Default",
))


def _cells(line):
    return [c.strip() for c in _CELL_RE.split(line)[1:-1]]


_NONE_TRIGGER = "(無)"


def dt_triggers(cell):
    """決策表觸發字格子 → (觸發字清單, 問題或 None)。「(無)」(全形半形括號都認)= 刻意不設,回空清單:
    這個情境沒有不常見的字面特徵,不出情境段,只靠規則包與代碼審。"""
    norm = cell.replace("\uff08", "(").replace("\uff09", ")")
    trig = [t.strip().strip("`") for t in re.split(r"[、,，]", norm) if t.strip()]
    if _NONE_TRIGGER in trig:
        if len(trig) > 1:
            return [], "「(無)」是刻意不設觸發字,不能跟其他觸發字並列"
        return [], None
    if not trig:
        return [], "觸發字不准空(刻意不設寫「(無)」)"
    return trig, None


def _norm(cell):
    """全形括號與冒號換成半形(型錄格子兩種都有人寫)。"""
    return cell.replace("（", "(").replace("）", ")").replace("：", ":")


def dt_evidence_parse(cell):
    """證據樣式格子「主:… ;例外:…」→ ({"main": [正規式…] 或 None, "alt": …} 或 None, 問題清單)。每段是「(無)」或一到三條
    反引號包住的 Python 正規式,每條要編譯得過;表格裡跳脫過的直線還原成 | 再編。scripts/lumos 借用這一支讀表(只有這一套)。"""
    norm = _norm(cell).strip()
    if not norm.startswith("主:") or norm.count("例外:") != 1:
        return None, ["證據樣式要寫成「主:… ;例外:…」"]
    main, alt = norm[len("主:"):].split("例外:", 1)
    probs, out = [], {}
    for key, name, part in (("main", "主", re.sub("[;；]+$", "", main.strip()).strip()), ("alt", "例外", alt.strip())):
        if part == _NONE_TRIGGER:
            out[key] = None
            continue
        pats = [x.replace("\\|", "|") for x in re.findall(r"`([^`]+)`", part)]
        if not 1 <= len(pats) <= 3 or re.sub(r"`[^`]+`", "", part).strip():
            probs.append(f"證據樣式的{name}:要寫「(無)」或一到三條反引號包住的正規式")
            continue
        for x in pats:
            try:
                re.compile(x)
            except re.error as e:
                probs.append(f"證據樣式的{name} `{x}` 編譯不過({e})")
        out[key] = pats
    return (None if probs else out), probs


def dt_evidence(cell):
    """證據樣式格子 → 問題清單(空=合法);解析見 dt_evidence_parse。"""
    return dt_evidence_parse(cell)[1]


def _dt_header(dt):
    """決策表表頭 → {欄名: 位置};缺欄回 (None, 問題)。"""
    for ln in dt.splitlines():
        if ln.startswith("| ") and not re.match(r"^\|\s*D-\d+\s*\|", ln):
            cols = {name: i for i, name in enumerate(_cells(ln))}
            missing = [n for n in _DT_HEADER if n not in cols]
            return (None, "決策表表頭缺欄:" + "、".join(missing)) if missing else (cols, None)
    return None, "找不到決策表表頭"


def dt_row(get):
    """決策表一列(get(欄名) 取格子)→ (列 dict 或 None, 讀不懂的問題清單)。只管讀得懂讀不懂(scripts/lumos 讀到問題就整張表不用);
    常用字、來源、停用列寫法這類格式要求在 catalog_problems。
    列:{id, situation, standard, alt(不適用時), triggers, evidence{main, alt}, retired(停用列), switch(換列的列), checks(對應檢查), source(來源格)}。
    停用列不讀觸發字與證據樣式(當成沒有);換列的列認「不適用時」格子裡的明確標記「(換列)」,不從中文用語推,而且例外一定要是(無)。"""
    retired = _RETIRED in _norm(get("情境"))
    row = {"id": get("列編號"), "situation": get("情境"), "standard": get("標準寫法"), "alt": get("不適用時"),
           "triggers": [], "evidence": {"main": None, "alt": None}, "retired": retired,
           "switch": _SWITCH in _norm(get("不適用時")), "checks": get("對應檢查"), "source": get("來源")}
    if retired:
        return row, []
    trig, err = dt_triggers(get("觸發字"))
    ev, probs = dt_evidence_parse(get("證據樣式"))
    probs = ([err] if err else []) + probs
    if ev and row["switch"] and ev["alt"] is not None:
        probs.append(f"「不適用時」標了{_SWITCH}(換到別列)的列,證據樣式的例外要寫(無)")
    if probs:
        return None, probs
    row.update(triggers=trig, evidence=ev)
    return row, []


def dt_table(text):
    """型錄全文 → (列清單, 讀不懂的問題清單 [(列編號或 <決策表>, 原因)])。依表頭名稱取欄(欄位順序可以換);
    列編號要從 D-1 連號。scripts/lumos 用 importlib 借這一支讀表(Projects/Android寫法語意情境表態與盲判_計劃 範圍 1;
    代碼審 r1 架構對齊席:原本兩邊各寫一套、必有欄數已經分歧)。
    同一輪順手帶出處(給盲判材料,範圍 4):每列多 refs(來源格展開成網址)與 check_refs(對應檢查在型錄主表的 id、名稱、來源、網址),
    縮寫照〈來源縮寫〉表;主表或縮寫表找不到時那幾格留空、不報錯(讀得懂讀不懂歸這支的問題清單與 catalog_problems;
    代碼審 code-android情境題盲判 r1 架構對齊 F6:原本另有 dt_sources 再走一輪決策表)。"""
    i = text.find("\n## 情境決策表")
    if i < 0:
        return [], [("<決策表>", "找不到〈情境決策表〉節")]
    j = text.find("\n## ", i + 5)
    dt = text[i:j if j >= 0 else len(text)]
    hdr, herr = _dt_header(dt)
    if herr:
        return [], [("<決策表>", herr)]
    rows, probs, seen = [], [], []
    for ln in dt.splitlines():
        if not re.match(r"^\|\s*D-\d+\s*\|", ln):
            continue
        c = _cells(ln)
        did = c[0]
        if len(c) != len(hdr):
            probs.append((did, f"決策表欄位數 {len(c)},應為 {len(hdr)}"))
            continue
        seen.append(did)
        row, rp = dt_row(lambda name, c=c: c[hdr[name]])
        probs += [(did, p) for p in rp]
        if row:
            rows.append(row)
    abbrs, main = _abbr_table(text) or {}, _main_names(text)
    for row in rows:
        row["refs"] = _src_expand(row["source"], abbrs)
        row["check_refs"] = [{"id": cid, "name": main.get(cid, ("", ""))[0], "source": main.get(cid, ("", ""))[1],
                              "refs": _src_expand(main.get(cid, ("", ""))[1], abbrs)}
                             for cid in dict.fromkeys(re.findall(r"[A-Z]+-\d+", row["checks"]))]
    if not seen or seen != [f"D-{k}" for k in range(1, len(seen) + 1)]:
        # 列編號只准往後加、不准重排或重用;刪列時那一列在情境欄標(停用)留著(Projects/Android寫法語意情境表態與盲判_計劃 範圍 1)
        probs.append(("<決策表>", "列編號要從 D-1 連號(刪列時標(停用)留著,不要拿掉或重排)"))
    return rows, probs


def _abbr_table(text):
    """〈來源縮寫〉表 → {縮寫: 那一列的網址或說明};找不到那一節回 None。catalog_problems 與 dt_table 共用(縮寫表只讀一套)。"""
    i = text.find("\n## 來源縮寫")
    if i < 0:
        return None
    j = text.find("\n## ", i + 5)
    out = {}
    for ln in text[i:j if j >= 0 else len(text)].splitlines():
        m = re.match(r"^\|\s*([A-Z][A-Z0-9-]+)\s*\|", ln)
        if m:
            c = _cells(ln)
            out[m.group(1)] = c[1] if len(c) >= 2 else ""
    return out


def _abbr_hit(abbr, cell):
    """格子裡有沒有這個縮寫(前後不接大寫英數或連字號)。"""
    return re.search(r"(?<![A-Z0-9-])" + re.escape(abbr) + r"(?![A-Z0-9-])", cell) is not None


def _main_names(text):
    """型錄主表 → {編號: (名稱, 來源)};同一個編號只認第一列。"""
    main = {}
    for ln in text.splitlines():
        m = _MAIN_ROW_RE.match(ln)
        if m:
            c = _cells(ln)
            if len(c) >= 2:
                main.setdefault(m.group(1), (c[1], c[-1]))
    return main


def _src_expand(cell, abbrs):
    """來源格 → 出處清單:格子裡的網址照收,登記在〈來源縮寫〉表的縮寫換成那一列寫的網址或說明(網址在前,縮寫依縮寫表順序,不重複)。"""
    out = []
    for u in re.findall(r"https?://[^\s)〕、;,，]+", cell):
        if u not in out:
            out.append(u)
    for a, url in abbrs.items():
        if _abbr_hit(a, cell):
            for u in re.findall(r"https?://[^\s)〕、;,，]+", url) or [url]:
                if u not in out:
                    out.append(u)
    return out


def _dt_row_lint(get):
    """決策表一列的格式要求(讀得懂之外):停用列的觸發字與證據樣式都要是(無)、觸發字不含常用字、來源不准空。"""
    if _RETIRED in _norm(get("情境")):
        trig, _e = dt_triggers(get("觸發字"))
        ok_ev = re.fullmatch(r"主:\(無\);\s*例外:\(無\)", _norm(get("證據樣式")))
        return [] if not trig and ok_ev else ["停用列的觸發字要寫(無)、證據樣式要寫「主:(無);例外:(無)」(不再出段)"]
    trig, _e = dt_triggers(get("觸發字"))
    probs = []
    bad = [t for t in trig if t in STOP_TRIGGERS]
    if bad:
        probs.append("觸發字含常用字:" + "、".join(bad))
    if not get("來源"):
        probs.append("來源不准空")
    return probs


def catalog_problems(rules=None):
    """型錄自己的格式檢查(計劃 S3,與第二、三批要的觸發字停用字、出處要求)。不需要 ast-grep。"""
    problems = []
    text = CATALOG.read_text(encoding="utf-8")
    i_dt, i_pend = text.find("\n## 情境決策表"), text.find("\n## 待查證")
    if i_dt < 0 or i_pend < 0:
        return [("<catalog>", "找不到〈情境決策表〉或〈待查證〉節")]
    main, dt = text[:i_dt], text[i_dt:i_pend]
    rows, seen = {}, set()
    # 〈來源縮寫〉表登記過的縮寫才算來源;TBD、TODO 這類大寫佔位字不算
    abbrs = _abbr_table(text)
    if abbrs is None:
        # 記一筆、照樣往下檢查(縮寫當空集合),一次報齊其他問題
        problems.append(("<catalog>", "找不到〈來源縮寫〉節(來源欄的縮寫要對照它)"))
        abbrs = {}
    for ln in main.splitlines():
        m = _MAIN_ROW_RE.match(ln)
        if not m:
            continue
        rid, c = m.group(1), _cells(ln)
        if rid in seen:
            problems.append((rid, "編號重複"))
        seen.add(rid)
        if len(c) != _MAIN_COLS:
            problems.append((rid, f"欄位數 {len(c)},應為 {_MAIN_COLS}"))
            continue
        rows[rid] = c
        name, std, kind, wire, batch, src = c[1], c[3], c[7], c[8], c[9], c[11]
        if not std or not wire or not batch:
            problems.append((rid, "標準寫法、接電方式、通電批次不准空"))
        if kind.startswith("形狀") and not ("告警帶寫法" in wire or "行為測試或正向約束" in wire):
            problems.append((rid, "形狀類要有「告警帶寫法」或「行為測試或正向約束」"))
        if kind.startswith("語意"):
            if "表態對程式" not in wire:
                problems.append((rid, "語意類要有「表態對程式」"))
            if "(人裁)" not in name and "盲判席" not in wire:
                problems.append((rid, "語意類(沒標人裁)要有「盲判席」"))
        if "(出處不全)" not in name:
            if any(w in src for w in _WEAK_SRC):
                problems.append((rid, "來源還寫著未核對或無網址,要補查證網址或標(出處不全)"))
            if not (re.search(r"https?://", src) or any(_abbr_hit(a, src) for a in abbrs)):
                problems.append((rid, "來源沒有網址或來源縮寫"))
    referenced = set()
    _dt_rows, dt_probs = dt_table(dt)          # 讀得懂讀不懂:跟 scripts/lumos 同一支
    problems += dt_probs
    hdr, _herr = _dt_header(dt)
    for ln in dt.splitlines() if hdr else []:
        if not re.match(r"^\|\s*D-\d+\s*\|", ln):
            continue
        c = _cells(ln)
        did = c[0]
        if len(c) != len(hdr):
            continue                              # 欄位數不對已經在 dt_table 報過
        problems += [(did, p) for p in _dt_row_lint(lambda name, c=c: c[hdr[name]])]
        refs = set(re.findall(r"[A-Z]+-\d+", c[hdr["對應檢查"]]))
        for r in sorted(refs - set(rows)):
            problems.append((did, f"對應檢查 {r} 不在型錄主表"))
        referenced |= refs
    for rid, c in rows.items():
        if c[7].startswith("語意") and rid not in referenced and "(出處不全)" not in c[1] and "(人裁)" not in c[1]:
            problems.append((rid, "語意類沒有被任何決策表列收進去"))
    if _SCRATCH_RE.search(text):
        problems.append(("<catalog>", "型錄裡有指向會談暫存區的路徑"))
    weak_ids = {rid for rid, c in rows.items() if "(出處不全)" in c[1]}
    for r in rules or []:
        m = re.match(r"\[([A-Z]+-\d+)\]", r["message"])
        if m and m.group(1) in weak_ids and r["severity"] != "hint":
            problems.append((r["id"], f"引用出處不全的 {m.group(1)},只准 hint 級"))
    return problems


# ── 證據樣式自測(代碼審 code-android情境題與表態對程式 r1 D1)──────────────────────────────
# 每列證據樣式附正例與反例,經 scripts/lumos 真的切段與核對程式跑過:正例(那列標準寫法、例外寫法的範例程式)要對得上樣式,
# 反例(對應檢查列的壞寫法)要對不上樣式。推送前對不上只提醒、記帳、待盲判(代碼審 r2 換形狀),這裡守的是樣式本身沒壞:
# 正例被樣式拒絕=提醒會誤報、反例被樣式接受=提醒會漏;做不到的那一段改寫(無)交盲判。依據:ast-grep test 的 valid/invalid
# (https://ast-grep.github.io/guide/test-rule.html )、Semgrep 的 ok/ruleid(https://docs.semgrep.dev/writing-rules/testing-rules )。
# 樣本放 samples/situation/<列編號>.kt.txt(一支檔放很多段互不相干的片段,不是能編譯的 Kotlin,所以不用 .kt),一支檔多段,
# 每段一行標題 `// === <種類> <說明>` 開頭;種類:main-ok、alt-ok(那個寫法的正例)、bad(每個有樣式的寫法都要擋)、
# bad main、bad alt(只對那個寫法擋:壞寫法剛好是另一個寫法的合法長相時用)。
_SIT_SAMPLE_HEAD = re.compile(r"^// === (main-ok|alt-ok|bad main|bad alt|bad)(?=\s|$)(.*)$")


def situation_dir():
    return HERE / "samples" / "situation"


def situation_samples(rid):
    """samples/situation/<列編號>.kt.txt → [(種類, 標題, 程式)];沒有這支檔回 [];第一個標題前的字不收(檔頭說明)。"""
    p = situation_dir() / f"{rid}.kt.txt"
    if not p.is_file():
        return []
    out, cur = [], None
    for ln in p.read_text(encoding="utf-8").split("\n"):
        m = _SIT_SAMPLE_HEAD.match(ln)
        if m:
            cur = [m.group(1), (m.group(1) + m.group(2)).strip(), []]
            out.append(cur)
        elif cur is not None:
            cur[2].append(ln)
    return [(k, title, "\n".join(body).rstrip("\n") + "\n") for k, title, body in out]


def load_lumos():
    """把旁邊的 scripts/lumos 當模組載入(不寫 __pycache__)→ (模組或 None, 原因或 None)。"""
    import importlib.machinery
    import importlib.util
    path = HERE.parents[2] / "scripts" / "lumos"
    if not path.is_file():
        return None, f"找不到 {path}"
    prev = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        loader = importlib.machinery.SourceFileLoader("lumos_for_kt_pack_check", str(path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
    except Exception as e:   # 別支檔,什麼都可能炸:變成一句原因
        return None, f"載入 {path} 失敗({e.__class__.__name__}:{e})"
    finally:
        sys.dont_write_bytecode = prev
    return mod, None


def _sit_first_pass(lm, segs, row, variant):
    """這些段裡有沒有哪一行當 evidence 能過這個寫法的核對 → (段, 行號) 或 None;同時回第一句擋下的原因。"""
    why = None
    for sg in segs:
        for ln in range(sg["start"], sg["end"] + 1):
            ans = {"applies": True, "variant": variant, "evidence": f"{sg['file']}:{ln}"}
            pr = lm._kt_sit_row_check(sg, row["id"], ans, row)
            if pr is None:
                return (sg, ln), None
            why = why or pr
    return None, why


def situation_sample_problems(lumos=None):
    """證據樣式自測 → [(列編號, 原因)]。lumos=已載入的 scripts/lumos 模組(預設載入旁邊那支)。
    每列每個不是(無)的寫法要有至少一段正例、整列(有任何樣式時)要有至少一段反例;每段樣本整支當新增,經
    lumos 的 _kt_sit_text_segments 切段(觸發字要中、要切得出含這一列的段),再拿段範圍每一行當 evidence 經 _kt_sit_row_check 核:
    正例要有一行對得上,反例要每一行都對不上(推送前會提醒)。(無)的寫法有正例或反例、沒有任何樣式的列有樣本、樣本檔對不到列,都算問題(樣本沒有作用)。"""
    rows, probs = dt_table(CATALOG.read_text(encoding="utf-8"))
    if probs:
        return [(a, "決策表讀不懂,證據樣式自測沒跑:" + b) for a, b in probs]
    if lumos is None:
        lumos, why = load_lumos()
        if lumos is None:
            return [("<situation>", "證據樣式自測要載入 scripts/lumos:" + why)]
    out = []
    ids = {r["id"] for r in rows}
    for f in sorted(situation_dir().glob("*.kt.txt")) if situation_dir().is_dir() else []:
        if f.name[:-len(".kt.txt")] not in ids:
            out.append((f.name, "樣本檔對不到決策表的列"))
    for r in rows:
        if r["retired"]:
            continue
        rid, ev = r["id"], r["evidence"]
        variants = [v for v in ("main", "alt") if ev[v]]
        samples = situation_samples(rid)
        if not variants:
            if samples:
                out.append((rid, "證據樣式兩段都是(無),樣本沒有作用(拿掉樣本檔)"))
            continue
        kinds = {k for k, _t, _c in samples}
        for v in variants:
            if f"{v}-ok" not in kinds:
                out.append((rid, f"證據樣式的{'主' if v == 'main' else '例外'}沒有正例({v}-ok:{'標準寫法' if v == 'main' else '不適用時的例外寫法'}的範例程式)"))
        if not any(k.startswith("bad") for k in kinds):
            out.append((rid, "證據樣式沒有反例(bad:對應檢查列的壞寫法範例)"))
        for kind, title, code in samples:
            segs = [sg for sg in lumos._kt_sit_text_segments(f"{rid}.kt", code, rows) if rid in sg["rows"]]
            if not segs:
                out.append((rid, f"樣本「{title}」切不出含這一列的段(觸發字沒中,這段樣本測不到樣式)"))
                continue
            if kind.endswith("-ok"):
                v = kind[:-3]
                if not ev[v]:
                    out.append((rid, f"樣本「{title}」:這個寫法的證據樣式是(無),正例沒有作用"))
                    continue
                got, why = _sit_first_pass(lumos, segs, r, v)
                if got is None:
                    out.append((rid, f"正例「{title}」對不上樣式(推送前會誤報提醒):{why}"))
                continue
            targets = [kind.split()[1]] if " " in kind else variants
            for v in targets:
                if not ev[v]:
                    out.append((rid, f"樣本「{title}」:{v} 的證據樣式是(無),反例沒有作用"))
                    continue
                got, _why = _sit_first_pass(lumos, segs, r, v)
                if got is not None:
                    out.append((rid, f"反例「{title}」沒提醒({v}:evidence 指第 {got[1]} 行就對得上;壞寫法被當成照做)"))
    return out


def message_problems(rules, cat_ids):
    """每條規則的 id、severity、放哪個目錄、message 格式(計劃 S2)。不需要 ast-grep。"""
    problems = []
    for r in rules:
        rid, msg = r["id"], r["message"]
        if not rid.startswith("kt-"):
            problems.append((rid, "id 要用 kt- 前綴"))
        if r["severity"] not in SEVERITIES:
            problems.append((rid, f"severity 只能是 {'/'.join(SEVERITIES)}"))
        if r["severity"] not in _DIR_SEVERITY.get(r["dir"], ()):
            problems.append((rid, f"{r['dir']}/ 只收 {'/'.join(_DIR_SEVERITY.get(r['dir'], ()))} 級(hint 放 rules-hints/、info 放 rules-review/)"))
        m = re.match(r"\[([A-Z]+-\d+)\]", msg)
        if not m:
            problems.append((rid, "message 要以 [型錄編號] 開頭"))
        elif m.group(1) not in cat_ids:
            problems.append((rid, f"message 的編號 {m.group(1)} 不在型錄主表"))
        if len(msg) > MSG_MAX:
            problems.append((rid, f"message {len(msg)} 字,超過 {MSG_MAX}"))
        if ";" not in msg or not ("改用" in msg or "改成" in msg):
            problems.append((rid, "message 要有分號,並寫「改用」或「改成」"))
        if "$" in msg:
            problems.append((rid, "message 不准含 $"))
    return problems


_TIMED_OUT = [False]   # 一次掃描逾時後,這次自我檢查剩下的掃描都不跑(避免卡住時每次各等滿上限)


def scan(sg, cfg, target):
    """跑一次 ast-grep,回 [(ruleId, file)];失敗或之前已逾時回 None。"""
    if _TIMED_OUT[0]:
        return None
    try:
        r = subprocess.run([sg, "scan", "--config", str(HERE / cfg), "--json=stream", str(target)],
                           capture_output=True, text=True, cwd=str(HERE), timeout=SCAN_TIMEOUT)
    except subprocess.TimeoutExpired:
        _TIMED_OUT[0] = True
        return None
    except OSError:
        return None
    if r.returncode not in (0, 1):
        return None
    out = []
    for ln in r.stdout.splitlines():
        if ln.strip():
            try:
                d = json.loads(ln)
                out.append((d["ruleId"], d["file"]))
            except (ValueError, KeyError, TypeError):
                return None   # 輸出讀不懂就當這次掃描跑不起來,由呼叫端報「跑不起來」,不噴 traceback

    return out


def loaded_count(sg, cfg):
    if _TIMED_OUT[0]:
        return (None, None)
    try:
        r = subprocess.run([sg, "scan", "--config", str(HERE / cfg), "--inspect", "summary", str(HERE / "samples" / "good")],
                           capture_output=True, text=True, cwd=str(HERE), timeout=SCAN_TIMEOUT)
    except subprocess.TimeoutExpired:
        _TIMED_OUT[0] = True
        return (None, None)
    except OSError:
        return (None, None)
    m = re.search(r"effectiveRuleCount=(\d+),skippedRuleCount=(\d+)", r.stderr)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def _sample_owner(f, kind):
    """命中檔屬於哪條規則的樣本:samples/<kind>/<規則 id>/…;只看規則包底下那一段,祖先目錄叫什麼都不影響。"""
    p = Path(f)
    try:
        p = p.resolve().relative_to(HERE.resolve()) if p.is_absolute() else p
    except ValueError:
        return ""
    parts = p.parts
    return parts[2] if len(parts) > 2 and parts[0] == "samples" and parts[1] == kind else ""


def good_cases(path):
    n = 0
    for f in Path(path).rglob("*.kt"):
        if f.name.startswith(REVIEW_FP_PREFIX):
            continue      # 已知誤報樣本不算「好例」段數
        n += sum(1 for ln in f.read_text(encoding="utf-8").splitlines() if _DECL_RE.match(ln))
    return n


def check(sg):
    _TIMED_OUT[0] = False
    problems = []
    rules = load_rules()
    if not rules:
        problems.append(("<pack>", "一條規則都沒讀到(rules/、rules-review/、rules-hints/ 都是空的?)"))
    ids = [r["id"] for r in rules]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        problems.append(("<pack>", "id 重複:" + ", ".join(dup)))
    cat_ids, _cat_text = catalog_ids()
    problems += message_problems(rules, cat_ids)
    problems += catalog_problems(rules)
    problems += situation_sample_problems()
    for d, cfg in CONFIGS:
        want = sum(1 for r in rules if r["dir"] == d)
        got, skipped = loaded_count(sg, cfg)
        if got is None:
            problems.append(("<pack>", f"{cfg} 讀不到載入條數(掃描逾時或 ast-grep 跑不起來)"))
        elif got != want or skipped:
            problems.append(("<pack>", f"{cfg} 載入 {got} 條(略過 {skipped}),規則檔裡有 {want} 個 id"))
    review_ids = {r["id"] for r in rules if r["dir"] == "rules-review"}
    # 每份設定檔對壞例、好例各掃一次,再依樣本所在目錄(samples/<bad|good>/<規則 id>/…)歸到各條規則
    hits = {}
    for kind in ("bad", "good"):
        for _d, cfg in CONFIGS:
            got = scan(sg, cfg, HERE / "samples" / kind)
            if got is None:
                problems.append(("<pack>", f"{cfg} 掃 samples/{kind} 跑不起來"))
                continue
            for rule_id, f in got:
                owner = _sample_owner(f, kind)
                if kind == "good" and Path(f).name.startswith(REVIEW_FP_PREFIX) and rule_id in review_ids:
                    continue      # 語意覆核級規則已知的形狀誤報:記在樣本裡給盲判對照,不算好例誤報
                hits[(kind, owner, rule_id)] = hits.get((kind, owner, rule_id), 0) + 1
    for r in rules:
        rid = r["id"]
        bad, good = HERE / "samples" / "bad" / rid, HERE / "samples" / "good" / rid
        if not bad.is_dir():
            problems.append((rid, "缺壞例樣本 samples/bad/" + rid))
        else:
            n = hits.get(("bad", rid, rid), 0)
            if n < 2:
                problems.append((rid, f"壞例只命中 {n} 處,至少要 2"))
        if not good.is_dir():
            problems.append((rid, "缺好例樣本 samples/good/" + rid))
        else:
            n = hits.get(("good", rid, rid), 0)
            if n:
                problems.append((rid, f"好例誤報 {n} 處"))
            if good_cases(good) < 2:
                problems.append((rid, "好例至少要兩段(頂格宣告算一段)"))
    test_only = [r for r in rules if r["test_only"]]
    if test_only:
        if not TEST_ONLY_ANCESTOR.is_dir():
            problems.append(("<pack>", "缺 samples/ancestor-named-test(祖先目錄叫 test 的正式碼樣本)"))
        else:
            for _d, cfg in CONFIGS:
                got = scan(sg, cfg, TEST_ONLY_ANCESTOR)
                if got is None:
                    problems.append(("<pack>", f"{cfg} 掃 samples/ancestor-named-test 跑不起來"))
                    continue
                for (i, f) in got:
                    if any(r["id"] == i for r in test_only):
                        problems.append((i, "只掃測試碼的規則命中了祖先目錄叫 test 的正式碼:" + f))
    return rules, problems


def main(argv):
    if "--catalog-only" in argv:
        probs = catalog_problems(load_rules()) + situation_sample_problems()
        for rid, why in probs:
            print(f"{rid}: {why}")
        print(f"型錄問題 {len(probs)} 個")
        return 1 if probs else 0
    sg = None
    if "--sg" in argv:
        i = argv.index("--sg")
        if i + 1 >= len(argv):
            print("--sg 後面要給 ast-grep 執行檔路徑", file=sys.stderr)
            return 2
        sg = argv[i + 1]
    sg = sg or shutil.which("ast-grep")   # 不退去找 sg:Linux 上 sg 是切換群組的系統工具
    if not sg or not os.access(sg, os.X_OK):
        print("找不到 ast-grep(帶 --sg <路徑>)", file=sys.stderr)
        return 2
    rules, problems = check(sg)
    if "--json" in argv:
        print(json.dumps({"rules": len(rules), "problems": problems}, ensure_ascii=False))
    else:
        for rid, why in problems:
            print(f"{rid}: {why}")
        print(f"規則 {len(rules)} 條,問題 {len(problems)} 個")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
