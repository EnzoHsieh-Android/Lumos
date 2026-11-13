#!/usr/bin/env python3
"""Kotlin 規則包自我檢查(Projects/Android協程與API寫法機械檢查標準_計劃 S1、S2)。

白話:每條規則拿自己的壞例樣本跑,要至少命中兩處;拿好例樣本跑,要零命中而且好例至少兩段;
規則訊息要以型錄裡真的有的編號開頭、不超過 120 字、寫明修法、不含 $ 變數;
另外有一棵「祖先目錄叫 test 的正式碼」樣本,只該掃測試碼的規則對它不准命中。

用法:python3 check.py [--sg <ast-grep 執行檔>] [--json]
退出碼:0 全過、1 有問題、2 找不到 ast-grep。零依賴(只用標準庫)。
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG = HERE.parents[2] / "skills" / "kotlin-idioms" / "checks-catalog.md"
# 行為測試範本:型錄 C 列通電批次寫「範本 T<n>」時要在這份檔有 `## T<n> ` 那一節([[Projects/Android行為測試範本與架構測試_計劃]])
TEMPLATES = HERE.parents[2] / "skills" / "kotlin-idioms" / "test-templates.md"
# 四級:rules=會擋(error/warning);rules-review=語意覆核級(info,形狀分不出對錯,範本還沒接,
# 接不接見 [[Projects/規則包覆核兩級接新增告警閘_計劃]] 待人裁);rules-hints=提示級(hint,預設不接);
# rules-unwired=不接閘(任何等級):引用型錄出處不全列的規則,與還沒在真專案量過誤報的新規則
CONFIGS = (("rules", "sgconfig.yml"), ("rules-review", "sgconfig-review.yml"), ("rules-hints", "sgconfig-hints.yml"),
           ("rules-unwired", "sgconfig-unwired.yml"))
SEVERITIES = ("error", "warning", "info", "hint")
_DIR_SEVERITY = {"rules-hints": ("hint",), "rules-review": ("info",), "rules": ("error", "warning"), "rules-unwired": SEVERITIES}
MSG_MAX = 120          # 新增告警閘解析 SARIF 時把訊息截在 120 字
REVIEW_FP_PREFIX = "review-fp-"   # 好例樣本裡記「語意覆核級或不接閘規則已知會誤報」的檔名開頭,改規則形狀時拿來對照
CROSS_PREFIX = "cross-"          # 好例樣本裡放「別條規則的壞寫法、用來證明本條不重複報」的檔名開頭;好例的跨規則檢查略過它,但它一定要被別條規則命中
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
    """讀四個規則目錄 → [{id, severity, message, dir, file, test_only, ignores}];同一檔多份文件以 --- 分隔。
    ignores 是那份文件 `ignores:` 用引號括住的路徑清單,單行 `[...]` 與多行 `- '...'` 兩種寫法都讀(沒寫就是空清單)。"""
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
                ign = re.search(r"^ignores:\s*\[(.*)\]\s*(?:#.*)?$", doc, re.M) or \
                    re.search(r"^ignores:\s*(?:#.*)?\n((?:[ \t]+-[^\n]*\n?)+)", doc, re.M)   # 單行 [...] 或多行 - 清單
                rules.append({"id": m.group(1), "severity": sev.group(1) if sev else "",
                              "message": text, "dir": d, "config": cfg, "file": f.name,
                              "test_only": _files_block_is_test_only(doc),
                              "ignores": re.findall(r"['\"]([^'\"]+)['\"]", ign.group(1)) if ign else []})
    return rules


def catalog_ids():
    """型錄主表裡的編號(〈待查證〉節以後不算)。"""
    text = CATALOG.read_text(encoding="utf-8")
    cut = text.find("\n## 情境決策表")   # 主表在決策表之前;決策表的 D-n 與來源索引的編號都不是規則該引的編號
    main = text if cut < 0 else text[:cut]
    return {m.group(1) for m in map(_MAIN_ROW_RE.match, main.splitlines()) if m}, text


_CELL_RE = re.compile(r'(?<!\\)\|(?=(?:[^`]*`[^`]*`)*[^`]*$)')   # 反引號裡的直線不算欄位分隔
# 主表的主題前綴只列這一處:主表列的認法與〈統計〉各主題列數都從這裡來(代碼審 第二批 r3 架構對齊甲三:不准另抄一份)
_MAIN_TOPICS = ("API", "FLOW", "STATE", "CO", "UI", "ARCH", "DATA", "TEST", "PERF")
_MAIN_ROW_RE = re.compile(r"^\|\s*((?:" + "|".join(_MAIN_TOPICS) + r")-\d+)\s*\|")
_MAIN_COLS = 12      # 編號|名稱|壞寫法形狀|標準寫法|後果|現成規則|級|情境怎麼認|接電方式|通電批次|實測狀態|來源
# 決策表依表頭名稱取欄(scripts/lumos 的 _kt_decision_table 同一套);這幾欄一定要有
_DT_HEADER = ("列編號", "情境", "標準寫法", "不適用時", "觸發字", "證據樣式", "對應檢查", "來源")
_RETIRED = "(停用)"
_SWITCH = "(換列)"     # 「不適用時」格子的明確標記:這一列的例外是換到別列,不准選例外寫法
_WEAK_SRC = ("未開頁核對", "搜尋摘要", "無網址")
# 第四批通電批次的判定口徑(Projects/Android現成檢查接上CI與推送前_計劃 範圍 4;口徑原文在型錄〈輸入與口徑〉)。
# 預設關的規則照官方規則頁列舉:Slack compose-lints 的兩條穩定性檢查與 M2 API(https://slackhq.github.io/compose-lints/rules/ ;
# ComposeRememberMissing 已移除),compose-rules 外掛自帶設定 active: false 的三條。
B4_DEFAULT_OFF = frozenset((
    "ComposeUnstableReceiver", "ComposeUnstableCollections", "ComposeM2Api", "ComposeRememberMissing",
    "unstable-collections", "UnstableCollections", "preview-naming", "PreviewNaming", "material-two", "Material2"))
# 資安包:= Google 的 com.android.security.lint:lint,掛在 Android Lint 上、同一個 CI 步驟跑([[Projects/Android資安與崩潰靜態檢查補齊_計劃]] 範圍 3);
# 它 24 條的檢查頁(googlesamples.github.io/android-custom-lint-rules/checks/<id>.md.html)2026-11-08 逐頁看過都沒有 disabled by default,B4_DEFAULT_OFF 不加
_B4_LINT = re.compile(r"(?:androidx(?:\.[\w.]+)?|內建|資安包|slack|Android Lint):\s*([A-Z][A-Za-z0-9]+)")
_B4_CR = re.compile(r"cr:compose:([\w-]+)")
# 「間接」「相關」「需標註」= 那條現成檢查擋不到這列的壞寫法(2026-11-08 代碼審 code-型錄批一列也寫批四 r1 審查席 F1:TEST-23、UI-1、PERF-2);
# 「只管…」「只部分涵蓋」= 擋得到其中一部分,照算接電
_B4_SKIP = ("待查", "預設關", "相近", "opt-in", "間接", "相關", "需標註")
B4_TAG_LINT = "CI 範本:Android Lint"
B4_TAG_CR = "推送前:detekt 外掛 compose-rules"


def batch4_candidates(rule_col):
    """一列現成規則欄 → 第四批的候選 [(標籤, 規則碼)](去重、照出現順序;[[Projects/型錄接電要附證據_計劃]] 〈用詞〉候選)。
    以「;」「、」切段;某段含 androidx:、androidx.<套件>:、內建:、資安包:、slack:、Android Lint: 接大寫開頭的規則碼,或含 cr:compose:<規則>,
    而且那段不含 _B4_SKIP 裡任一個註記字樣,規則碼不是 B4_DEFAULT_OFF 才算。排除字只會讓候選變少(少宣稱)。"""
    out = []
    for seg in re.split(r"[;；、]", rule_col):
        if any(w in seg for w in _B4_SKIP):
            continue
        for tag, pat in ((B4_TAG_LINT, _B4_LINT), (B4_TAG_CR, _B4_CR)):
            out += [(tag, code) for code in pat.findall(seg) if code not in B4_DEFAULT_OFF and (tag, code) not in out]
    return out


def batch4_expected_tags(rule_col):
    """一列現成規則欄 → 有候選的第四批標籤(清單,依 Android Lint、compose-rules 順序)。"""
    tags = {tag for tag, _code in batch4_candidates(rule_col)}
    return [tag for tag in (B4_TAG_LINT, B4_TAG_CR) if tag in tags]



# 〈接電證據〉節的真跑樣本:自檢只驗樣本檔名恰好是 <編號>.kt.txt 而且存在。樣本有沒有照壞寫法欄寫、有沒有另加會觸發檢查的呼叫,
# 不用字面規則判——實作時「只准加外殼」的逐行比對連兩包被打穿(壞寫法欄多是文字描述、XML 與 Gradle 有必寫結構、「沒寫 X」型的列
# 最長那段反引號是正確寫法),改由代碼審派一席逐支對照壞寫法欄判讀([[Projects/型錄接電要附證據_計劃]]〈天花板〉)


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
    # 回合結束檢查與改檔前推列計劃實驗 E9:Now in Android 的文件頻率超過 8%(15.5%、14.5%、9.4%),改檔前推列會每次都亮
    "Composable", "Inject", "Modifier",
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
        pats = _snippets(part)
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


def _section(text, title):
    """型錄一節的文字(從「## <title>」那行到下一個「## 」之前);找不到回 None。〈來源縮寫〉、〈待查證〉、〈接電證據〉共用這一套切法。"""
    i = text.find("\n## " + title)
    if i < 0:
        return None
    j = text.find("\n## ", i + 1)
    return text[i:j] if j >= 0 else text[i:]


def _abbr_table(text):
    """〈來源縮寫〉表 → {縮寫: 那一列的網址或說明};找不到那一節回 None。catalog_problems 與 dt_table 共用(縮寫表只讀一套)。"""
    sec = _section(text, "來源縮寫")
    if sec is None:
        return None
    out = {}
    for ln in sec.splitlines():
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


# 〈接電證據〉節([[Projects/型錄接電要附證據_計劃]] 範圍 1、3):每個候選(編號,標籤,檢查)恰好一筆判定,批四標籤以判定為準
_WIRING_TITLE = "接電證據"
_WIRING_COLS = 7          # 編號|標籤|檢查|判定|等級|理由|出處
_WIRING_VERDICTS = ("擋得到", "擋不到")
_WIRING_LEVELS = ("Fatal", "Error", "Warning", "Hint", "Informational", "detekt", "沒報")
_WIRING_BLOCKING = {B4_TAG_LINT: ("Fatal", "Error", "Warning"), B4_TAG_CR: ("detekt",)}
_WIRING_ENV_RE = re.compile(r"^真跑環境:\d{4}-\d{2}-\d{2},AGP \d+(?:\.\d+)+,Gradle \d+(?:\.\d+)+", re.M)
_WIRING_RUN_RE = re.compile(r"^\u3014真跑 \d{4}-\d{2}-\d{2}:([^\u3015]+)\u3015$")
_WIRING_NO_BUILD = "樣本編不過:"
_BATCH4_RE = re.compile(r"批四\(([^)]*)\)")


def wiring_dir():
    return HERE / "samples" / "lint-wiring"


def wiring_table(text):
    """〈接電證據〉節 → (判定列清單 [欄位], 節的文字或 None)。讀法照 _pending_table:_MAIN_ROW_RE 認列、_cells 切欄。"""
    sec = _section(text, _WIRING_TITLE)
    if sec is None:
        return [], None
    return [_cells(ln) for ln in sec.splitlines() if _MAIN_ROW_RE.match(ln)], sec


def _batch4_have(batch):
    """通電批次欄 → (批四括號寫的標籤清單或 None, 位置問題)。整格找全部批四括號(代碼審 r1 審查席 a2:只看告警帶寫法之後的第一個,
    寫在別的子段或寫兩個都漏):超過一個、或不在「告警帶寫法=」那段值裡(兩者之間不准有別的「=」),都報。"""
    ms = list(_BATCH4_RE.finditer(batch))
    if not ms:
        return None, []
    i = batch.find("告警帶寫法=")
    probs = ["〈接電證據〉通電批次的批四括號只准一個"] if len(ms) > 1 else []
    if i < 0 or ms[0].start() < i or "=" in batch[i + len("告警帶寫法="):ms[0].start()]:
        probs.append("〈接電證據〉通電批次的批四只准寫在「告警帶寫法=」那段值裡")
    return [t.strip() for t in ms[0].group(1).split(";")], probs


def wiring_problems(text, rows):
    """〈接電證據〉節跟主表雙向對得上、每筆格式對、樣本檔在,而且有候選的列通電批次的批四標籤恰好等於判定擋得到的標籤。"""
    table, sec = wiring_table(text)
    if sec is None:
        return [("<catalog>", "找不到〈接電證據〉節")]
    out = [] if _WIRING_ENV_RE.search(sec) else [("<catalog>", "〈接電證據〉缺「真跑環境:<日期>,AGP <版本>,Gradle <版本>…」那一行")]
    seen, hits = set(), {}
    for c in table:
        out += [(c[0], p) for p in _wiring_entry_problems(c, rows, seen, hits)]
    for rid, c in rows.items():
        out += [(rid, p) for p in _wiring_row_problems(rid, c, seen, hits)]
    return out


def _wiring_entry_problems(c, rows, seen, hits):
    """〈接電證據〉一筆判定 → 問題;順手把(編號,標籤,檢查)記進 seen、擋得到的標籤記進 hits。"""
    rid = c[0]
    if len(c) != _WIRING_COLS:
        return [f"〈接電證據〉欄位數 {len(c)},應為 {_WIRING_COLS}"]
    tag, code, verdict, level, why, src = c[1:]
    if rid not in rows:
        return ["〈接電證據〉的列不在主表"]
    key = (rid, tag, code)
    if key in seen:
        return [f"〈接電證據〉判定重複:{tag} {code}"]
    seen.add(key)
    out = [] if (tag, code) in batch4_candidates(rows[rid][5]) else [f"〈接電證據〉判定的檢查不是候選:{tag} {code}"]
    if verdict not in _WIRING_VERDICTS or level not in _WIRING_LEVELS:
        return [*out, f"〈接電證據〉判定或等級不是固定值:{verdict} {level}"]
    if verdict == "擋得到":
        if level not in _WIRING_BLOCKING.get(tag, ()):
            out.append(f"〈接電證據〉等級跟判定矛盾:{tag} {code} 擋得到卻是 {level}")
        hits.setdefault(rid, set()).add(tag)
    elif not why.strip():
        out.append(f"〈接電證據〉擋不到要寫理由:{tag} {code}")
    return out + _wiring_source_problems(src, rid, why)


def _wiring_row_problems(rid, c, seen, hits):
    """主表一列 → 候選沒判定的、批四標籤跟判定不一致的問題。沒有候選的列(例:批四(現成規則))照舊值,但不准寫接電標籤。"""
    cands = batch4_candidates(c[5])
    out = [f"〈接電證據〉要補判定:{tag} {code}" for tag, code in cands if (rid, tag, code) not in seen]
    have, where = _batch4_have(c[9])
    have = have or []
    out += where
    if not cands:
        if any(t in (B4_TAG_LINT, B4_TAG_CR) for t in have):
            out.append("〈接電證據〉通電批次寫了接電標籤,但現成規則欄沒有候選(沒有口徑認得的現成檢查)")
        return out
    want = [t for t in (B4_TAG_LINT, B4_TAG_CR) if t in hits.get(rid, set())]
    if have != want:
        out.append("〈接電證據〉通電批次的批四標籤跟判定不一致:要寫" + ("「批四(" + ";".join(want) + ")」" if want else "沒有批四"))
    return out


def _wiring_source_problems(src, rid, why):
    """一筆判定的出處 → 問題。真跑:樣本檔名恰好是 <編號>.kt.txt 而且存在;查證:重用 _VERIFIED_RE、理由以樣本編不過開頭。"""
    m = _WIRING_RUN_RE.match(src.strip())
    if m:
        if m.group(1) != f"{rid}.kt.txt":
            return [f"〈接電證據〉樣本檔名不是 {rid}.kt.txt:{m.group(1)}"]
        return [] if (wiring_dir() / m.group(1)).is_file() else [f"〈接電證據〉樣本檔不存在:{m.group(1)}"]
    if _VERIFIED_RE.fullmatch(src.strip()):
        return [] if why.startswith(_WIRING_NO_BUILD) else [f"〈接電證據〉出處是查證時理由要以「{_WIRING_NO_BUILD}」開頭"]
    return ["〈接電證據〉出處要是\u3014真跑 日期:檔名\u3015或\u3014查證 日期:網址\u3015"]


def catalog_problems(rules=None):
    """型錄自己的格式檢查(計劃 S3,與第二、三批要的觸發字停用字、出處要求)。不需要 ast-grep。"""
    problems = []
    text = CATALOG.read_text(encoding="utf-8")
    i_dt, i_pend = text.find("\n## 情境決策表"), text.find("\n## 待查證")
    if i_dt < 0 or i_pend < 0:
        return [("<catalog>", "找不到〈情境決策表〉或〈待查證〉節")]
    dt = text[i_dt:i_pend]
    rows = main_rows(text, problems)   # 主表的讀法只在 main_rows 一處(編號重複、欄位數也在那裡報)
    # 〈來源縮寫〉表登記過的縮寫才算來源;TBD、TODO 這類大寫佔位字不算
    abbrs = _abbr_table(text)
    if abbrs is None:
        # 記一筆、照樣往下檢查(縮寫當空集合),一次報齊其他問題
        problems.append(("<catalog>", "找不到〈來源縮寫〉節(來源欄的縮寫要對照它)"))
        abbrs = {}
    for rid, c in rows.items():
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
        if m and m.group(1) in weak_ids and r.get("dir") != "rules-unwired":   # 缺 dir 鍵照不在 unwired 算
            problems.append((r["id"], f"引用出處不全的 {m.group(1)},只准放 rules-unwired/"))
    problems += template_problems(rows)   # 主表只讀一次:把上面讀好的列交過去
    problems += pending_problems(text, rows) + wiring_problems(text, rows) + stats_problems(text, rows, rules)
    return problems


# 〈待查證〉節的口徑(型錄〈待查證〉節說明句):現成規則欄含「待查」,或來源欄標 _WEAK_SRC 的前兩種字樣。
# 不含第三種「無網址」:只寫無網址的列要標(出處不全),不列進〈待查證〉
_PENDING_SRC = _WEAK_SRC[:2]
_PENDING_EMPTY = ("—", "")


def _pending_table(text):
    """〈待查證〉節的列 → ({編號: 欄位(補到三欄)}, 重複的編號);節尾是下一個 `## `(同 _abbr_table)。找不到這一節回 ({}, [])。"""
    sec = _section(text, "待查證")
    if sec is None:
        return {}, []
    rows, dup = {}, []
    for ln in sec.splitlines():
        m = _MAIN_ROW_RE.match(ln)
        if m:
            if m.group(1) in rows:
                dup.append(m.group(1))
            rows[m.group(1)] = [*_cells(ln), "", ""][:3]   # 少寫格子的列照空格判,不讓 pc[1]、pc[2] 崩
    return rows, dup


def _pending_need(c):
    """主表一列 → (代號還待查, 來源還待核對)。"""
    return "待查" in c[5], any(w in c[11] for w in _PENDING_SRC)


def pending_problems(text, rows):
    """〈待查證〉節跟主表雙向對得上([[Projects/Android資安靜態檢查補齊第二批_計劃]] 範圍 6):該列的都列、不該列的不列,
    兩格寫不寫內容跟主表那列還有沒有待查、待核對一致(沒有就寫 —)。"""
    pend, dup = _pending_table(text)          # 找不到〈待查證〉節時 catalog_problems 開頭就先報了
    out = [(rid, "〈待查證〉編號重複") for rid in dup]
    for rid, c in rows.items():
        if any(_pending_need(c)) and rid not in pend:
            out.append((rid, "主表還有待查或待核對的來源,〈待查證〉沒列"))
    for rid, pc in pend.items():
        if rid not in rows:
            out.append((rid, "〈待查證〉的列不在主表"))
            continue
        code, src = _pending_need(rows[rid])
        if not (code or src):
            out.append((rid, "主表已解決,〈待查證〉還列著"))
            continue
        for want, cell, what in ((code, pc[1], "待查的規則代號"), (src, pc[2], "待核對的來源")):
            if want == (cell.strip() in _PENDING_EMPTY):
                out.append((rid, f"〈待查證〉的「{what}」格跟主表對不上(主表{'還有' if want else '已沒有'},這格要{'寫內容' if want else '寫 —'})"))
    return out


def _stats_expected(text, rows, rules):
    """〈統計〉每個要核對的數 → [(標籤, 在〈統計〉找數字的正規式, 重數的值)]。rules 是 None 時不核對規則包那幾個。"""
    pend, _dup = _pending_table(text)
    need = [_pending_need(rows[r]) for r in pend if r in rows]
    cs = rows.values()
    want = [("總列數", r"- 總列數:(\d+)", len(rows))]
    want += [(f"{t} 列數", rf"- 各主題:[^\n]*?\b{t} (\d+)", sum(1 for r in rows if r.split("-")[0] == t)) for t in _MAIN_TOPICS]
    want += [(f"級的組合 {g}", rf"- 級的組合:(?:|[^\n]*?、){re.escape(g)} (\d+)", sum(1 for c in cs if c[6] == g))
             for g in sorted({c[6] for c in cs})]
    want += [("形狀類", r"- 情境:形狀類 (\d+)", sum(1 for c in cs if c[7].startswith("形狀"))),
             ("語意類", r"- 情境:[^\n]*?語意類 (\d+)", sum(1 for c in cs if c[7].startswith("語意"))),
             ("出處不全", r"- 出處不全的列:(\d+)", sum(1 for c in cs if "(出處不全)" in c[1])),
             ("人裁", r"- 出處不全的列:[^\n]*?人裁的列:(\d+)", sum(1 for c in cs if "(人裁)" in c[1]))]
    want += [(f"各級含 {lv}", rf"- 各級\(列的級含該字母[^\n]*?{lv} (\d+)", sum(1 for c in rows.values() if lv in c[6]))
             for lv in "ABCD"]
    want += [(f"各級首字 {lv}", rf"- 各級\(以第一個字母計[^\n]*?{lv} (\d+)", sum(1 for c in rows.values() if c[6][:1] == lv))
             for lv in "ABCD"]
    want += [("逐列查證", r"- 逐列查證[^\n]*?:(\d+) 列", sum(1 for c in rows.values() if _VERIFIED_RE.search(c[11]))),
             ("待查證", r"- 待查證:(\d+) 列", len(pend)),
             ("待查證代號待查", r"- 待查證:[^\n]*?規則代號待查 (\d+) 列", sum(1 for a, _b in need if a)),
             ("待查證來源待核對", r"- 待查證:[^\n]*?來源待核對 (\d+) 列", sum(1 for _a, b in need if b)),
             ("接電證據", r"- 接電證據:(\d+) 筆", len(wiring_table(text)[0]))]
    _head, api_rows, _has = _api_table(text)
    reach_rows, _rhas = _unreach_table(text)
    items = [x for _n, its, _r in api_rows for x in its]
    want += [("API 公開名稱", r"- API 決策點:公開名稱 (\d+)", len(api_rows))]
    want += [(f"API 歸屬 {k}", rf"- API 決策點:[^\n]*?{k} (\d+)", sum(1 for x in items if _api_item_kind(x) == k))
             for k in ("D-n", "撞名", "決策不問主表列", "決策不問代碼審", "無決策")]
    want += [("叫不出的單位", r"- 叫不出的壞寫法:(\d+) 個", len(reach_rows))]
    want += [(f"叫不出改由 {k}", rf"- 叫不出的壞寫法:[^\n]*?{k} (\d+)", sum(1 for _a, _b, _c, ro, _w in reach_rows if ro.split(" ")[0] == k))
             for k in ("規則", "範本", "代碼審", "不是寫法")]
    if rules is not None:
        want += [("規則包條數", r"- 規則包條數:(\d+)", len(rules)),
                 ("不接閘條數", r"- 規則包條數:[^\n]*?其中 (\d+) 條在不接閘", sum(1 for r in rules if r.get("dir") == "rules-unwired"))]
        want += [(f"規則包 {k}", rf"- 規則包條數:[^\n]*?\b{k} (\d+)", sum(1 for r in rules if r.get("severity") == k))
                 for k in ("error", "warning", "info", "hint")]
        want += [("被會擋的規則守到的列數", r"- 被會擋的規則守到的列數[^\n]*?:(\d+)\s*$", _guarded_rows(rows, rules))]
    return want


def _guarded_rows(rows, rules):
    """〈統計〉「被會擋的規則守到的列數」的口徑(那一行的括號原文):通電批次欄含「告警帶寫法=批一」,而且現成規則欄或實測狀態欄
    提到至少一條 rules/ 底下的規則 id(id 前後不接字母、數字、連字號)。"""
    pats = [re.compile(r"(?<![\w-])" + re.escape(r["id"]) + r"(?![\w-])") for r in rules if r.get("dir") == "rules"]
    return sum(1 for c in rows.values() if "告警帶寫法=批一" in c[9] and any(p.search(c[5] + " " + c[10]) for p in pats))


def stats_problems(text, rows, rules=None):
    """〈統計〉節手寫的數字要等於從主表、〈待查證〉與規則檔重數的值(同上計劃範圍 6;節說明句寫明是手寫)。"""
    i = text.find("\n## 統計")
    if i < 0:
        return [("<catalog>", "找不到〈統計〉節")]
    st = text[i:]
    out = []
    for label, pat, n in _stats_expected(text, rows, rules):
        m = re.search(pat, st, re.M)
        got = int(m.group(1)) if m else None
        if got != n:
            out.append(("<catalog>", f"〈統計〉{label} 寫 {got},重數是 {n}"))
    return out


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


# ── API 決策點與壞寫法反查(Projects/情境決策點窮舉與壞寫法要叫得出_計劃)──────────────────────────────
# 推送前的情境題只在「被問到」時守得住。兩道自檢讓「沒被問到」不再沒人知道:
# ①〈API 決策點〉:協程核心函式庫的公開名稱(釘版 klib 清單 + 手列的 JVM 專屬名稱)每個恰好歸類一次,歸到情境列的要被
#   那列觸發字搜得到,反過來觸發字搜得到的名稱也要歸到那列;
# ②〈叫不出的壞寫法〉:情境列每個對應檢查的每段壞寫法片段(沒有片段算一個 <無片段>),單獨包成一支檔要叫得出那一列,
#   叫不出就要在表上寫明改由誰抓,改由在片段層級驗(規則看壞例樣本的 // BAD 行、範本看那個對應檢查的壞寫法小節)。
# 兩道都要借 scripts/lumos 的觸發字比對與切段(同 situation_sample_problems),所以不放進 catalog_problems。
_API_TITLE = "API 決策點"
_UNREACH_TITLE = "叫不出的壞寫法"
_API_ANCHORS = ("flatMapLatest", "Mutex", "Lazily", "UNLIMITED", "trySend")
_API_MIN_NAMES = 300
_API_HEAD_RE = re.compile(r"^母體:kotlinx-coroutines-core (\S+),klib (\S+) sha256 ([0-9a-f]{64}),jvm (\S+) sha256 ([0-9a-f]{64})\s*$", re.MULTILINE)
_API_SKIP_NAMES = frozenset(("equals", "hashCode", "toString", "copy", "values", "valueOf", "entries"))
_API_SIG_RE = re.compile(r"^([\w.]+)/([^|]+)\|(.*)$")
_API_ITEM_RE = re.compile(r"^(?:(D-[1-9]\d*)|撞名 (D-[1-9]\d*)|決策不問 ((?:[A-Z]+-[1-9]\d*)|代碼審)|(無決策))$")
_STOPWORD_REASON = "停用字,不帶決策:"
_HOMONYM_REASON = "同名異義:"
_NO_SNIPPET = "<無片段>"
_ROUTE_RE = re.compile(r"^(?:規則 (kt-[\w-]+)|範本 (T\d+)|(代碼審)|(不是寫法))$")
_SINGLE_IDENT_RE = re.compile(r"^[A-Za-z_][\w.]*(?:\(\))?$")
BAD_HEADING_RE = re.compile(r"^### 壞寫法[::]\s*([A-Z]+-\d+)(?=\s|$)")   # 範本檔每組裡的壞寫法小節;小節到下一個 ### 或 ## 為止
SCAN_FAILED = object()   # --sg 模式但掃描逾時或失敗:反查的「規則」改由一律判問題(跟「不在 --sg 模式」的 None 分開)
_REACH_TEST_PATH = "app/src/test/java/x/XTest.kt"
_REACH_MAIN_PATH = "app/src/main/java/x/X.kt"


def coroutines_api_dir():
    return HERE / "coroutines-api"


def _cap(n):
    return n[:1].upper() + n[1:]


def _api_klib_decls(ktext):
    """klib 清單 → ([(套件, 鏈段落, 接收者完整名或 None, 是不是屬性, 是不是平台限定)], {完整名: object|enum})。只讀簽名註解。"""
    decls, kinds, seen_decl, pending = [], {}, False, False
    for ln in ktext.splitlines():
        if ln.strip().startswith("// Targets:"):
            pending = seen_decl          # 檔頭那一行(第一個宣告之前)不算平台標註
            continue
        decl, _sep, sig = ln.partition(" // ")
        m = _API_SIG_RE.match(sig.strip()) if _sep else None
        if not m or not decl.strip():
            continue
        seen_decl = True
        pkg, chain, rest = m.groups()
        if re.search(r"\bobject\b", decl):
            kinds[f"{pkg}/{chain}"] = "object"
        elif re.search(r"\benum class\b", decl):
            kinds[f"{pkg}/{chain}"] = "enum"
        recv = re.match(r"@([\w.]+)\{", rest)
        decls.append((pkg, chain.split("."), recv.group(1) if recv else None, bool(re.search(r"\b(?:val|var)\b", decl)), pending))
        pending = False
    return decls, kinds


def _api_companions(jtext):
    """klib 清單不標伴生物件;伴生物件在 JVM 是外層類別的靜態欄位(`static final field Factory L…/Channel$Factory;`)→ {完整名}。"""
    out = set()
    for typ in re.findall(r"static final field (?:\w+) L([\w/]+\$\w+);", jtext):
        pkg_path, cls = typ.rsplit("/", 1)
        out.add(pkg_path.replace("/", ".") + "/" + cls.replace("$", "."))
    return out


def _api_skip(pkg, parts, companions):
    name = parts[-1]
    return (name.startswith(("<", "_")) or name in _API_SKIP_NAMES or re.fullmatch(r"component\d+", name) is not None
            or "$" in name or "-impl" in name or any(seg in ("internal", "debug") for seg in pkg.split("."))
            or f"{pkg}/{'.'.join(parts)}" in companions)


def _api_visible(pkg, parts, recv, is_prop, companions, kinds):
    """可見寫法:object 成員、伴生物件成員、列舉值寫成「外層.名稱」(伴生物件那段拿掉);頂層擴充屬性寫成「接收者.名稱」;其他沒有。"""
    name, parent = parts[-1], f"{pkg}/{'.'.join(parts[:-1])}"
    if len(parts) > 1 and (parent in companions or kinds.get(parent) in ("object", "enum")):
        kept = [p for k, p in enumerate(parts[:-1]) if f"{pkg}/{'.'.join(parts[:k + 1])}" not in companions]
        return {".".join([*kept, name])}
    if recv and is_prop and len(parts) == 1:
        return {f"{recv.split('.')[-1]}.{name}"}
    return set()


def _api_jvm_only(only, jtext, names):
    """jvm-only.txt 每一行「名稱 | JVM 清單裡的寫法」→ 加進 names,回問題清單。"""
    probs = []
    if not only.is_file():
        return probs
    for no, ln in enumerate(only.read_text(encoding="utf-8").splitlines(), 1):
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        left, _sep, right = (x.strip() for x in ln.partition("|"))
        if not left or not right:
            probs.append(("<api>", f"jvm-only.txt 第 {no} 行要寫「名稱 | JVM 清單裡的寫法」"))
        elif right not in jtext:
            probs.append(("<api>", f"jvm-only.txt 第 {no} 行右欄「{right}」不在 JVM 清單"))
        elif left in names:
            probs.append(("<api>", f"jvm-only.txt 第 {no} 行「{left}」klib 已有,不用手列"))
        else:
            names[left] = set()
    return probs


def _api_names(api_dir, version):
    """母體 → ({名稱: 可見寫法集合}, 問題清單)。只讀 klib 清單每行的簽名註解(`套件/鏈|…`),不解析宣告部分(泛型、fun interface
    這類形狀 klib 文法沒有公開規格);JVM 專屬名稱只來自同目錄的 jvm-only.txt(左欄名稱 | 右欄 JVM 清單裡的寫法)。"""
    try:
        ktext = (api_dir / f"kotlinx-coroutines-core-{version}.klib.api").read_text(encoding="utf-8")
        jtext = (api_dir / f"kotlinx-coroutines-core-{version}.api").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {}, [("<api>", f"讀不到母體檔({e.__class__.__name__}:{e})")]
    decls, kinds = _api_klib_decls(ktext)
    companions = _api_companions(jtext)
    names, limited = {}, {}
    for pkg, parts, recv, is_prop, lim in decls:
        if _api_skip(pkg, parts, companions):
            continue
        names.setdefault(parts[-1], set()).update(_api_visible(pkg, parts, recv, is_prop, companions, kinds))
        limited[parts[-1]] = limited.get(parts[-1], True) and lim
    for n in [n for n, lim in limited.items() if lim and n not in jtext and _cap(n) not in jtext]:
        del names[n]
    return names, _api_jvm_only(api_dir / "jvm-only.txt", jtext, names)


def _api_shapes(name, vis, reverse=False):
    """名稱的比對形狀:正向與停用字比簡名、可見寫法、簡名(;反向只比簡名與簡名((不然 object 名當觸發字會逼每個成員歸屬)。"""
    return {name, name + "("} | (set() if reverse else set(vis))


def _api_table(text):
    """〈API 決策點〉→ (母體那一行的比對結果或 None, [(名稱, 歸屬項清單, 理由)], 節是否存在)。"""
    sec = _section(text, _API_TITLE)
    if sec is None:
        return None, [], False
    rows = []
    for ln in sec.splitlines():
        if not ln.startswith("|") or re.match(r"^\|\s*(?:名稱\s*\||-{3})", ln):
            continue
        c = [*_cells(ln), "", "", ""][:3]
        rows.append((c[0].strip("`"), [x.strip() for x in _norm(c[1]).split("、") if x.strip()], c[2]))
    return _API_HEAD_RE.search(sec), rows, True


def _api_item_kind(x):
    """歸屬項 → 統計用的種類:D-n、撞名、決策不問主表列、決策不問代碼審、無決策;認不得回空字串。"""
    m = _API_ITEM_RE.match(x)
    if not m:
        return ""
    if m.group(1):
        return "D-n"
    if m.group(2):
        return "撞名"
    if m.group(3):
        return "決策不問代碼審" if m.group(3) == "代碼審" else "決策不問主表列"
    return "無決策"


def _unpipe(s):
    """表格跳脫的 \\| 還原成 |;型錄格子的還原只走這一支。"""
    return s.replace("\\|", "|")


def _snippets(cell):
    """格子 → 反引號片段清單(\\| 照 _unpipe 還原;不做長度或字元過濾)。主表壞寫法欄、決策表證據樣式、〈叫不出的壞寫法〉片段格都走這一支。"""
    return [_unpipe(s) for s in re.findall(r"`([^`]+)`", cell)]


def _word_in(lumos, needle, hay):
    return re.search(lumos._kt_trigger_re(needle), hay) is not None


def _referenced_checks(dt_rows):
    return {cid for r in dt_rows if not r["retired"] for cid in re.findall(r"[A-Z]+-\d+", r["checks"])}


def _api_mother_problems(head, api_dir):
    """母體兩份檔的 sha256 → 問題。"""
    out = []
    ver = head.group(1)
    for kind, want in (("klib", head.group(3)), ("jvm", head.group(5))):
        p = api_dir / f"kotlinx-coroutines-core-{ver}{'.klib' if kind == 'klib' else ''}.api"
        got = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
        if got != want:
            out.append(("<api>", f"{kind} 母體 {p.name} 的 sha256 跟第一行對不上(母體被改過或檔不在)"))
    return out


class _ApiCtx:
    """API 決策點核對要用的東西一次備好:母體名稱、決策表、觸發字正規式、被情境列引用的主表列。"""

    def __init__(self, lumos, rows, names, dt_rows):
        self.lumos, self.rows, self.names = lumos, rows, names
        self.by_id = {r["id"]: r for r in dt_rows}
        self.rx = {r["id"]: [re.compile(lumos._kt_trigger_re(t)) for t in r["triggers"]] for r in dt_rows if not r["retired"]}
        self.refd = _referenced_checks(dt_rows)

    def mentioned_by(self, shapes):
        """哪些被情境列引用的主表列,壞寫法片段裡以整字寫到這些形狀。"""
        return [cid for cid in sorted(self.refd) if cid in self.rows
                and any(_word_in(self.lumos, s, sn) for s in shapes for sn in _snippets(self.rows[cid][2]))]


def _api_item_problems(ctx, name, m, reason=""):
    """一個歸屬項 → 問題清單。"""
    shapes = _api_shapes(name, ctx.names[name])
    d, crash, ask = m.group(1) or m.group(2), m.group(2), m.group(3)
    if d:
        r = ctx.by_id.get(d)
        if r is None or r["retired"]:
            return [f"{d} 不在決策表或是停用列"]
        return [] if any(p.search(s) for p in ctx.rx[d] for s in shapes) else [f"{'撞名 ' if crash else ''}{d} 的觸發字搜不到這個名稱"]
    if not ask:
        return []
    hit = ctx.mentioned_by(shapes)
    if ask == "代碼審":
        if not hit or _norm(reason).startswith(_HOMONYM_REASON):
            return []          # 片段寫到的同名字是別的東西:理由以「同名異義:」開頭寫明,不必硬指不相干的列
        return [f"決策不問 代碼審,但 {'、'.join(hit)} 的壞寫法片段寫到它(要指向那一列;片段裡的同名字是別的東西就把理由寫成「{_HOMONYM_REASON}…」)"]
    return [] if ask in hit else [f"決策不問 {ask}:那一列不是情境列的對應檢查,或它的壞寫法片段沒有以整字寫到這個名稱"]


def _api_row_problems(ctx, table):
    """表上每一列 → (問題清單, {名稱: (歸屬項, 理由)})。"""
    out, seen, attrs = [], set(), {}
    for name, items, reason in table:
        if name in seen:
            out.append((name, "〈API 決策點〉同一個名稱出現兩列"))
            continue
        seen.add(name)
        if not reason.strip():
            out.append((name, "理由不准空白"))
        if name not in ctx.names:
            out.append((name, "表上有、母體沒有(升版拿掉或打錯)"))
            continue
        parsed = [_API_ITEM_RE.match(x) for x in items]
        if not items or not all(parsed) or len(set(items)) != len(items) or ("無決策" in items and len(items) > 1):
            out.append((name, f"歸屬欄寫法不對:「{'、'.join(items)}」(五種:D-n、撞名 D-n、決策不問 <主表列編號>、決策不問 代碼審、無決策;無決策只能單獨)"))
            continue
        attrs[name] = (items, reason)
        out += [(name, p) for m in parsed for p in _api_item_problems(ctx, name, m, reason)]
    out += [(name, "母體裡有、表上沒有(升版多出來的名稱要分類)") for name in sorted(set(ctx.names) - seen)]
    return out, attrs


def _api_sync_problems(ctx, attrs):
    """反向同步(每一列各自覆蓋)與停用字規則 → 問題清單。"""
    out = []
    for rid, pats in ctx.rx.items():
        for name, (items, _r) in attrs.items():
            if rid not in items and f"撞名 {rid}" not in items and any(
                    p.search(s) for p in pats for s in _api_shapes(name, ctx.names[name], reverse=True)):
                out.append((name, f"{rid} 的觸發字搜得到它,歸屬要有 {rid} 或 撞名 {rid}"))
    for name, (items, reason) in attrs.items():
        if items == ["無決策"] and STOP_TRIGGERS & _api_shapes(name, ctx.names[name]) and not _norm(reason).startswith(_STOPWORD_REASON):
            out.append((name, f"停用字表裡的名稱標無決策,理由要以「{_STOPWORD_REASON}」開頭並寫為什麼"))
    return out


def api_decision_problems(text, rows, api_dir=None, lumos=None):
    """〈API 決策點〉自檢 → [(名稱或 <api>, 原因)](計劃範圍 1、2)。rows 是 main_rows 的結果。"""
    if lumos is None:
        lumos, why = load_lumos()
        if lumos is None:
            return [("<api>", "要載入 scripts/lumos:" + why)]
    api_dir = Path(api_dir) if api_dir else coroutines_api_dir()
    head, table, has = _api_table(text)
    if not has:
        return [("<api>", f"找不到〈{_API_TITLE}〉節")]
    if head is None:
        return [("<api>", f"〈{_API_TITLE}〉第一行要是「母體:kotlinx-coroutines-core <版本>,klib <網址> sha256 <值>,jvm <網址> sha256 <值>」")]
    out = _api_mother_problems(head, api_dir)
    names, nprobs = _api_names(api_dir, head.group(1))
    out += nprobs
    missing_anchor = [a for a in _API_ANCHORS if a not in names]
    if missing_anchor or len(names) < _API_MIN_NAMES:
        out.append(("<api>", f"抽法壞了:名稱 {len(names)} 個(下限 {_API_MIN_NAMES}),抽不到錨點 {missing_anchor}"))
    dt_rows, dprobs = dt_table(text)
    if dprobs:
        return out + [(a, "決策表讀不懂,API 決策點自檢沒跑完:" + b) for a, b in dprobs]
    ctx = _ApiCtx(lumos, rows, names, dt_rows)
    row_probs, attrs = _api_row_problems(ctx, table)
    return out + row_probs + _api_sync_problems(ctx, attrs)


def _reach_units(text, rows, dt_rows):
    """反查單位 → [(情境列, 對應檢查, 片段或 <無片段>)];停用列不算,觸發字寫(無)的列照算。"""
    out = []
    for r in dt_rows:
        if r["retired"]:
            continue
        for cid in re.findall(r"[A-Z]+-\d+", r["checks"]):
            if cid not in rows:
                continue
            sn = _snippets(rows[cid][2])
            out += [(r["id"], cid, s) for s in sn] if sn else [(r["id"], cid, _NO_SNIPPET)]
    return out


def _reachable(lumos, unit, dt_rows):
    rid, cid, snip = unit
    if snip == _NO_SNIPPET:
        return False
    path = _REACH_TEST_PATH if cid.startswith("TEST-") else _REACH_MAIN_PATH
    if not lumos._kt_sit_path_ok(path):
        return False
    code = "class X {\n    fun f() {\n        " + snip + "\n    }\n}\n"
    return any(rid in sg["rows"] for sg in lumos._kt_sit_text_segments(path, code, dt_rows))


def _unreach_table(text):
    """〈叫不出的壞寫法〉→ ([(情境列, 對應檢查, 片段, 改由, 理由)], 節是否存在)。片段格整格恰好是一段反引號才取內文,
    其餘(<無片段>、多段、反引號外還有字)照整格原文,對不上反查單位就會被報;兩種都做 \\| 還原。"""
    sec = _section(text, _UNREACH_TITLE)
    if sec is None:
        return [], False
    rows = []
    for ln in sec.splitlines():
        if not re.match(r"^\|\s*D-\d+\s*\|", ln):
            continue
        c = [*_cells(ln), "", "", "", "", ""][:5]
        sn = _snippets(c[2])
        whole = len(sn) == 1 and re.fullmatch(r"`[^`]*`", c[2]) is not None
        rows.append((c[0], c[1], sn[0] if whole else _unpipe(c[2]), c[3], c[4]))
    return rows, True


def _norm_code(s):
    """比對用:字串字面值清空、連續空白折成一個。"""
    s = re.sub(r'"(?:[^"\\\n]|\\.)*"', '""', s)
    return re.sub(r"\s+", " ", s).strip()


def _parts_in_order(lumos, snip, hay):
    """片段以 … 或 ... 切段後,各段依序以整字出現在 hay 裡。"""
    parts = [p.strip() for p in re.split(r"…|\.\.\.", _norm_code(snip)) if p.strip()]
    if not parts:
        return False          # 片段只有 … 或空白:沒有東西可比,不算比到
    pos = 0
    for part in parts:
        m = re.compile(lumos._kt_trigger_re(part)).search(hay, pos)
        if not m:
            return False
        pos = m.end()
    return True


_BAD_MARK_RE = re.compile(r"//\s*BAD(?![A-Za-z])")
_ANNOTATION_NAME_RE = re.compile(r"[\w.:]+")
_BRACKET_PAIRS = {"(": ")", "<": ">", "[": "]"}


def _balanced_end(code, i, j):
    """code[i][j] 是開括號 → 配對到的收尾括號之後的位置 (行, 欄);只數同一種括號,可跨行;到檔尾都沒關回 None。"""
    op, cl, depth = code[i][j], _BRACKET_PAIRS[code[i][j]], 0
    while i < len(code):
        while j < len(code[i]):
            c = code[i][j]
            depth += (c == op) - (c == cl)
            j += 1
            if depth == 0:
                return i, j
        i, j = i + 1, 0
    return None


def _one_annotation_end(code, i, j):
    """code[i][j] 是 `@` → 這一個註記結束後的位置 (行, 欄);`@[…]` 整組配對,`@名稱` 後面可接任意層 <…> 與 (…)。括號到檔尾都沒關回 None。"""
    j += 1
    if j < len(code[i]) and code[i][j] == "[":
        return _balanced_end(code, i, j)
    m = _ANNOTATION_NAME_RE.match(code[i], j)
    j = m.end() if m else j
    for opener in "<(":
        if j < len(code[i]) and code[i][j] == opener:
            end = _balanced_end(code, i, j)
            if end is None:
                return None
            i, j = end
    return i, j


def _annotation_end(code, k):
    """第 k 行起的註記段 → 註記之後的第一行程式在哪一行。照結構逐字元讀,不列舉寫法(一個註記怎麼讀見 _one_annotation_end),
    一行可放幾個註記、參數可跨行。
    回 k:第 k 行不是以 @ 開頭,或註記後面同一行就接著程式(例 `@Composable fun A()`);
    回 i(>k):註記跨行、在第 i 行收尾後同一行接著程式;回 i+1:註記到第 i 行行尾就結束(整行只有註記),要從下一行繼續找。
    括號到檔尾都沒關,當成不是註記,回 k。字串已先剝空,參數裡的字串不影響括號配對。"""
    i, j = k, len(code[k]) - len(code[k].lstrip())
    if not code[i][j:].startswith("@"):
        return k
    while True:
        while j < len(code[i]) and code[i][j] in " \t":
            j += 1
        if j >= len(code[i]):
            return i + 1
        if code[i][j] != "@":
            return i
        end = _one_annotation_end(code, i, j)
        if end is None:
            return k
        i, j = end


def _sample_abs(f):
    """壞例檔路徑 → 比對用的絕對路徑字串(ast-grep 回報的相對路徑以 HERE 為基準);_bad_lines 與 check() 的起訖行索引共用。"""
    p = Path(f)
    return str((p if p.is_absolute() else HERE / p).resolve())


def _next_statement(code, start):
    """從第 start 行(0 起)往下,跳過空行與只有註記的段落 → (語句開頭那一行, 比對用的程式);找不到回 None。
    語句是那一行加上接著以 . 或 ?. 開頭的續行。"""
    nxt = start
    while True:
        nxt = next((k for k in range(nxt, len(code)) if code[k].strip()), None)
        if nxt is None:
            return None
        end = _annotation_end(code, nxt)
        if end == nxt:
            break
        nxt = end
    stmt = [code[nxt]]
    for k in range(nxt + 1, len(code)):
        if not code[k].lstrip().startswith((".", "?.")):
            break
        stmt.append(code[k])
    return nxt, _norm_code(" ".join(stmt))


def _bad_lines_in(lumos, text):
    """一支壞例檔的全文 → ([(行號, 比對用的程式)], 問題或 None)。規則見 _bad_lines。"""
    raw = text.split("\n")
    code = lumos._strip_c_comments(text, blank_strings=True, keep_newlines=True, kotlin=True).split("\n")
    kept = lumos._strip_c_comments(text, blank_strings=False, keep_newlines=True, kotlin=True).split("\n")
    if not len(raw) == len(code) == len(kept):
        return [], "去註解後行數對不上,判不了哪幾行標了 // BAD"
    out = []
    for no, ln in enumerate(raw, 1):
        if len(_BAD_MARK_RE.findall(ln)) <= len(_BAD_MARK_RE.findall(kept[no - 1])):
            continue                     # 這行的標記都還在「只拿掉註解」的版本裡=都在字串裡,不算
        if code[no - 1].strip():
            out.append((no, _norm_code(code[no - 1])))
            continue
        hit = _next_statement(code, no)
        if hit is not None:
            out.append((hit[0] + 1, hit[1]))
    return out, None


def _bad_lines(lumos, samples_dir, rule_id):
    """samples/bad/<id>/ 底下標了 // BAD 的行 → ([(檔的絕對路徑, 行號, 比對用的程式)], 問題)。標記整字認(//BAD、// BAD:、
    // BAD-NEXT 都算,// BADGE 不算);同一行有程式就比那一行,標記單獨一行就比它標的下一個語句(_next_statement:
    下一個有程式的行,加上接著以 . 或 ?. 開頭的續行;只有註記的行跳過,註記照 _annotation_end 的結構讀(任意層括號、泛型、
    @[…]、參數跨行),註記後面同一行接著程式的不跳)。去註解用 scripts/lumos 的 Kotlin 剝法;
    標記要在註解裡才算(字串裡的 // BAD 不算)。三份行一律只照 \\n 切(換頁字元、U+2028 不斷行,跟 ast-grep 的行號一致)。"""
    out, probs = [], []
    for f in sorted((samples_dir / "bad" / rule_id).rglob("*.kt*")):
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            probs.append(f"壞例檔 {f.name} 讀不了({e.__class__.__name__})")
            continue
        lines, why = _bad_lines_in(lumos, text)
        if why:
            probs.append(f"壞例檔 {f.name} {why}")
        out += [(_sample_abs(f), no, ln) for no, ln in lines]
    return out, probs


def _fence_body(templates_text, group, cid):
    """範本檔某一組裡標題是「### 壞寫法:<cid>」的每個小節的圍欄內文(同編號多節取聯集),併成一份字串。
    找組走 template_sections;圍欄內外走 _visible_lines(keep_fenced 有無兩次的差就是圍欄內的行),不另寫圍欄判定。"""
    lines = templates_text.splitlines()
    secs = template_sections(templates_text)
    starts = [i for g, i in secs if g == group]
    if not starts:
        return ""
    a = starts[0]
    b = min([i for _g, i in secs if i > a] or [len(lines)])
    outside = {no - 1 for no, _ln in _visible_lines(lines)}
    out, inside = [], False
    for no, ln in _visible_lines(lines, keep_fenced=True):
        i = no - 1
        if not a <= i < b:
            continue
        if i in outside:
            if ln.startswith("#"):
                m = BAD_HEADING_RE.match(_norm(ln))
                inside = bool(m and m.group(1) == cid)
        elif inside:
            out.append(ln)
    return "\n".join(out)


def _reach_unit_problems(lumos, units, listed, dt_rows):
    """每個反查單位:叫不出卻沒列、叫得出卻還列著 → 問題。"""
    out = []
    for u in units:
        reach = _reachable(lumos, u, dt_rows)
        if not reach and u not in listed:
            out.append((u[0], f"{u[1]} 的片段「{u[2]}」叫不出 {u[0]},〈{_UNREACH_TITLE}〉沒有這一列"))
        elif reach and u in listed:
            out.append((u[0], f"{u[1]} 的片段「{u[2]}」現在叫得出,〈{_UNREACH_TITLE}〉這一列過期了"))
    return out


def bad_snippet_reach_problems(text, rows, rules=None, samples_dir=None, templates_text=None, scan_index=None, lumos=None):
    """〈叫不出的壞寫法〉自檢 → [(情境列或 <reach>, 原因)](計劃範圍 3)。scan_index:None=不在 --sg 模式、只做靜態核對;
    SCAN_FAILED=--sg 但掃描失敗;字典 {(規則 id, 檔的絕對路徑): [(起始行, 結束行)]}=照起訖行核。"""
    if lumos is None:
        lumos, why = load_lumos()
        if lumos is None:
            return [("<reach>", "要載入 scripts/lumos:" + why)]
    if templates_text is None:
        templates_text = TEMPLATES.read_text(encoding="utf-8") if TEMPLATES.is_file() else ""
    env = {"lumos": lumos, "rows": rows, "by_rule": {r["id"]: r for r in (load_rules() if rules is None else rules)},
           "samples": Path(samples_dir) if samples_dir else HERE / "samples", "templates": templates_text, "scan_index": scan_index}
    dt_rows, dprobs = dt_table(text)
    if dprobs:
        return [(a, "決策表讀不懂,反查沒跑:" + b) for a, b in dprobs]
    table, has = _unreach_table(text)
    if not has:
        return [("<reach>", f"找不到〈{_UNREACH_TITLE}〉節")]
    units = _reach_units(text, rows, dt_rows)
    listed, out = {}, []
    for r, c, s, route, why in table:
        if (r, c, s) in listed:
            out.append((r, f"〈{_UNREACH_TITLE}〉同一個(情境列, 對應檢查, 片段)出現兩列:{c}「{s}」"))
        listed[(r, c, s)] = (route, why)
    out += _reach_unit_problems(lumos, units, listed, dt_rows)
    uset = set(units)
    for (rid, cid, snip), (route, why) in listed.items():
        if (rid, cid, snip) not in uset:
            out.append((rid, f"〈{_UNREACH_TITLE}〉的 {cid}「{snip}」不是反查單位(片段已不在壞寫法欄,或那一對已有片段卻寫 {_NO_SNIPPET})"))
        else:
            out += [(rid, f"{cid}「{snip}」:{p}") for p in _route_problems(env, cid, snip, route, why)]
    return out


def _rule_route_problems(env, cid, snip, rule_id):
    """改由「規則 <id>」→ 問題清單:規則在 rules/、訊息編號對、片段在 // BAD 行、--sg 時起訖行涵蓋。"""
    r = env["by_rule"].get(rule_id)
    if r is None or r.get("dir") != "rules" or not r["message"].startswith(f"[{cid}]"):
        return [f"規則 {rule_id} 不在會擋的 rules/、或訊息開頭不是 [{cid}]"]
    lines, probs = _bad_lines(env["lumos"], env["samples"], rule_id)
    if probs:
        return probs
    hits = [(f, no) for f, no, ln in lines if _parts_in_order(env["lumos"], snip, ln)]
    if not hits:
        return [f"片段不在 samples/bad/{rule_id}/ 標了 // BAD 的行上"]
    idx = env["scan_index"]
    if idx is SCAN_FAILED:
        return ["--sg 掃描逾時或失敗,驗不了規則有沒有報出這一行"]
    if isinstance(idx, dict) and not any(a <= no <= b for f, no in hits for a, b in idx.get((rule_id, f), ())):
        return [f"規則 {rule_id} 在壞例檔報出的節點,起訖行沒有涵蓋片段所在的 // BAD 行"]
    return []


def _template_route_problems(env, cid, snip, group):
    """改由「範本 T<n>」→ 問題清單:不是單一識別字、跟通電批次對得上、片段在那組該對應檢查的壞寫法小節程式裡。"""
    if _SINGLE_IDENT_RE.match(snip.strip()):
        return ["片段只是一個識別字,不准用範本背書(只能用規則或代碼審)"]
    if behavior_value(env["rows"][cid][9]) != f"範本 {group}":
        return [f"範本 {group} 跟 {cid} 通電批次的「行為測試或正向約束=」對不上"]
    if _fence_regions(env["templates"].splitlines(), False)[1]:
        # 寬鬆讀法也關不上的圍欄:CommonMark 讓它吃到檔尾,後面各組的標題與程式都算進去,哪段屬於哪一組判不準,直接報
        return [f"範本檔有沒關的圍欄,判不準範本 {group} 的小節程式到哪裡為止;先把圍欄關上"]
    body = _norm_code(_fence_body(env["templates"], group, cid))
    if not body:
        return [f"範本 {group} 沒有「### 壞寫法:{cid}」小節的程式"]
    return [] if _parts_in_order(env["lumos"], snip, body) else [f"片段不在範本 {group} 的「### 壞寫法:{cid}」小節程式裡"]


def _route_problems(env, cid, snip, route, why):
    m = _ROUTE_RE.match(route.strip())
    if not m or not why.strip():
        return ["改由只收「規則 <id>」「範本 T<n>」「代碼審」「不是寫法」四種,理由不准空白"]
    rule_id, group, review, _notcode = m.groups()
    if snip == _NO_SNIPPET and not review:
        return [f"{_NO_SNIPPET} 只准改由代碼審"]
    if rule_id:
        return _rule_route_problems(env, cid, snip, rule_id)
    if group:
        return _template_route_problems(env, cid, snip, group)
    return []


_BEHAVIOR_RE = re.compile(r"行為測試或正向約束=([^;]*)")
_TEMPLATE_VALUE_RE = re.compile(r"範本 (T\d+)")
TEMPLATE_HEADING_RE = re.compile(r"^## (T\d+)(?:[ \t]|$)")   # 範本檔一組一節的標題;測試端也用這一條


def behavior_value(batch_cell):
    """通電批次格子裡「行為測試或正向約束=」那一段的值(到分號為止);沒有這一段回 None。
    「範本 T<n>」只在這一段才算引用範本(型錄〈輸入與口徑〉的定義)。測試端也呼叫這一支,不另抄。"""
    m = _BEHAVIOR_RE.search(batch_cell)
    return m.group(1).strip() if m else None


def main_rows(text=None, problems=None):
    """型錄主表(〈情境決策表〉之前)欄數對的列 → {編號: 欄位}。主表的唯一讀法:catalog_problems、
    template_problems 與測試都走這裡。給了 problems 就把編號重複、欄位數不對記進去(重複時後面那列為準)。"""
    text = CATALOG.read_text(encoding="utf-8") if text is None else text
    cut = text.find("\n## 情境決策表")
    main = text if cut < 0 else text[:cut]
    rows, seen = {}, set()
    for ln in main.splitlines():
        m = _MAIN_ROW_RE.match(ln)
        if not m:
            continue
        rid, c = m.group(1), _cells(ln)
        if rid in seen and problems is not None:
            problems.append((rid, "編號重複"))
        seen.add(rid)
        if len(c) != _MAIN_COLS:
            if problems is not None:
                problems.append((rid, f"欄位數 {len(c)},應為 {_MAIN_COLS}"))
            continue
        rows[rid] = c
    return rows


_VERIFIED_RE = re.compile(r"\u3014查證 \d{4}-\d{2}-\d{2}:[^\u3015]*https?://[^\u3015]*\u3015")  # 查證紀錄的龜甲括號寫成跳脫,免 ruff 誤認成英文括號
_UNVERIFIED_SHOW = 20


def catalog_unverified(text=None):
    """主表裡還沒逐列查證的列編號([[Projects/計劃依據來源必填_計劃]] S5):來源欄沒有查證紀錄(龜甲括號包的「查證 YYYY-MM-DD:網址」)、名稱也沒標
    (出處不全)。只有縮寫或只有網址的都算(網址可能只是縮寫展開的首頁)。讀表走 main_rows(主表唯一讀法);
    只回清單、不進 catalog_problems,呼叫端另印一行,不改退出碼。"""
    out = []
    for rid, c in main_rows(text).items():
        name, src = c[1], c[11]
        if "(出處不全)" not in name and not _VERIFIED_RE.search(src):
            out.append(rid)
    return out


def _print_unverified():
    ids = catalog_unverified()
    more = f" 等 {len(ids)} 列" if len(ids) > _UNVERIFIED_SHOW else ""
    print(f"還沒逐列查證 {len(ids)} 列" + (f":{'、'.join(ids[:_UNVERIFIED_SHOW])}{more}" if ids else "") + "(只提醒,不影響退出碼)")


def _fence_regions(lines, strict):
    """圍欄區段 → (區段清單, 收尾時還有沒有圍欄開著);區段是 (開頭行索引, 收尾行索引或 None)。
    ★刻意的另一份★:規則照 CommonMark(https://spec.commonmark.org/0.31.2/#fenced-code-blocks),口徑跟
    scripts/lumos 的 `_fence_regions` / `_visible_lines`(全檔唯一的圍欄判定)逐條對齊——縮排最多 3 格、
    tab 開頭不算、收尾要同字元且長度不短於開頭、strict 時收尾行除圍欄字元只准空白;本檔零依賴(只用標準庫)、
    scripts/lumos 沒有 .py 副檔名,不能 import 借用。兩份是否一致由 t_kotlin_template_fence_parity 機械比對。"""
    fence, start, regions = None, None, []
    for i, ln in enumerate(lines):
        indent = len(ln) - len(ln.lstrip(" "))
        s = ln.lstrip(" ")
        if not (indent <= 3 and not ln.startswith("\t") and s.startswith(("```", "~~~"))):
            continue
        ch = s[0]
        run = len(s) - len(s.lstrip(ch))
        if fence is None:
            fence, start = (ch, run), i
            continue
        if ch == fence[0] and run >= fence[1] and (not strict or s[run:].strip() == ""):
            regions.append((start, i))
            fence = None
    if fence is not None:
        regions.append((start, None))
    return regions, fence is not None


def _visible_lines(lines, keep_fenced=False):
    """圍欄外的行 → [(行號從 1 起, 原始行)]。先照 CommonMark 嚴格讀;讀完還有圍欄沒關,整份退回寬鬆讀法
    (同字元、長度夠就算關)——跟 scripts/lumos 的 `_visible_lines` 同一個取捨。keep_fenced=True 時也留圍欄★內★的行
    (圍欄標記行本身照樣不留;沒關的圍欄只有開頭那行是標記,內文一路到檔尾,照 CommonMark),同 scripts/lumos 的 keep_fenced。"""
    def _scan(strict):
        regions, unterminated = _fence_regions(lines, strict)
        hidden = set()
        for a, b in regions:
            if keep_fenced:
                hidden.update({a} if b is None else {a, b})
            else:
                hidden.update(range(a, (b if b is not None else len(lines) - 1) + 1))
        return [(i + 1, ln) for i, ln in enumerate(lines) if i not in hidden], unterminated
    out, unterminated = _scan(True)
    if unterminated:
        out, _ = _scan(False)
    return out


def template_sections(text):
    """範本檔 → [(組代號, 標題行索引)],只認圍欄外、符合 TEMPLATE_HEADING_RE 的標題。測試端切段也用這一支。"""
    out = []
    for no, ln in _visible_lines(text.splitlines()):
        m = TEMPLATE_HEADING_RE.match(ln)
        if m:
            out.append((m.group(1), no - 1))
    return out


def template_problems(rows=None):
    """通電批次的「行為測試或正向約束=」寫「範本 T<n>」的主表列,範本檔要有那一節(標題規則見
    TEMPLATE_HEADING_RE,圍欄裡的不算);沒有就報那一列。值以「範本」開頭卻不是「範本 T<n>」整段
    (例「範本 T3(備註)」「範本T3」)報格式錯,不靜默略過。範本檔不存在或不是 UTF-8 報一筆。
    只驗「指得到那一節」,範本內容對不對靠實驗與驗證紀錄。不需要 ast-grep。"""
    rows = main_rows() if rows is None else rows
    refs, problems = [], []
    for rid, c in rows.items():
        v = behavior_value(c[9]) or ""
        m = _TEMPLATE_VALUE_RE.fullmatch(v)
        if m:
            refs.append((rid, m.group(1)))
        elif v.startswith("範本"):
            problems.append((rid, f"「行為測試或正向約束=」的範本值要寫成「範本 T<n>」整段,這裡是「{v}」"))
    if not refs:
        return problems
    if not TEMPLATES.is_file():
        return [*problems, ("<templates>", "找不到範本檔")]
    try:
        text = TEMPLATES.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        return [*problems, ("<templates>", f"範本檔不是 UTF-8:第 {e.start} 個位元組讀不了({e.reason})")]
    have = {g for g, _i in template_sections(text)}
    return problems + [(rid, f"範本檔沒有 {g} 節") for rid, g in refs if g not in have]


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
            problems.append((rid, f"{r['dir']}/ 只收 {'/'.join(_DIR_SEVERITY.get(r['dir'], ()))} 級(hint 放 rules-hints/、info 放 rules-review/、還沒量過或出處不全的放 rules-unwired/)"))
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
    """跑一次 ast-grep,回 [(ruleId, file, 起始行)](行從 1 起算,ast-grep 報的是比對到的節點的起始行);
    失敗或之前已逾時回 None。"""
    got = scan_ranges(sg, cfg, target)
    return None if got is None else [(rid, f, a) for rid, f, a, _b in got]


def scan_ranges(sg, cfg, target):
    """同 scan,但每筆多回節點的結束行:[(ruleId, file, 起始行, 結束行)]。反查的「規則」改由要看起訖行涵蓋片段那一行
    (Projects/情境決策點窮舉與壞寫法要叫得出_計劃 範圍 4;既有 scan 的三元組呼叫端不動)。"""
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
                out.append((d["ruleId"], d["file"], d["range"]["start"]["line"] + 1, d["range"]["end"]["line"] + 1))
            except (ValueError, KeyError, TypeError):
                return None   # 輸出讀不懂就當這次掃描跑不起來,由呼叫端報「跑不起來」,不噴 traceback

    return out


# 規則包 SARIF 輸出的自檢(Projects/規則包覆核兩級接新增告警閘_計劃 做 3):新增告警閘讀的是 SARIF,覆核與提示級在 SARIF 裡是 note;
# 各拿一條規則的壞例樣本用它自己目錄的設定掃,結果裡要有那條規則,換 ast-grep 版本時工具鏈 CI 會紅
SARIF_PROBES = (("sgconfig-review.yml", "kt-livedata-setvalue-background"), ("sgconfig-hints.yml", "kt-value-assign-background"))


def sarif_gate_rule_ids(sg, cfg, target):
    """用新增告警閘讀 SARIF 的同一支 scripts/lumos `_lint_run_and_parse` 掃一次 → (閘讀得到的 ruleId 集合, 原因)。
    閘讀 SARIF 時要工具名、每筆的檔案位置與訊息,缺一個就靜默略過那筆(代碼審 r1 通才 F1:只看 ruleId 的話,
    換版本拿掉位置時探針照綠、閘卻讀到零筆);借同一支,閘讀得到才算有。跑不起來、逾時、主程式載不進來回 (None, 原因),不丟例外。"""
    import time
    if _TIMED_OUT[0]:
        return None, "之前已逾時"
    lm, why = load_lumos()
    if lm is None:
        return None, "lumos:" + why     # 呼叫端認這個前綴、另報一句,跟情境題證據樣式自測的寫法一樣
    t0 = time.monotonic()
    try:
        claims, ok = lm._lint_run_and_parse("", str(HERE), timeout=SCAN_TIMEOUT,
                                            argv=[sg, "scan", "--config", str(HERE / cfg), "--format", "sarif", str(target)])
    except Exception as e:      # 主程式那支在各種異常輸入下都不該丟,丟了就當跑不起來,不讓自檢噴 traceback
        return None, f"{type(e).__name__}"
    if not ok:
        if time.monotonic() - t0 >= SCAN_TIMEOUT:
            _TIMED_OUT[0] = True
        return None, "沒產出閘讀得懂的 SARIF"
    return {c.get("rule") for c in claims if c.get("file") and c.get("message")}, None


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
        if f.name.startswith((REVIEW_FP_PREFIX, CROSS_PREFIX)):
            continue      # 已知誤報樣本與跨規則邊界案例不算「好例」段數
        n += sum(1 for ln in f.read_text(encoding="utf-8").splitlines() if _DECL_RE.match(ln))
    return n


def check(sg):
    _TIMED_OUT[0] = False
    problems = []
    rules = load_rules()
    if not rules:
        problems.append(("<pack>", "一條規則都沒讀到(rules/、rules-review/、rules-hints/、rules-unwired/ 都是空的?)"))
    ids = [r["id"] for r in rules]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        problems.append(("<pack>", "id 重複:" + ", ".join(dup)))
    cat_ids, _cat_text = catalog_ids()
    problems += message_problems(rules, cat_ids)
    problems += catalog_problems(rules)
    lumos, lumos_why = load_lumos()
    problems += situation_sample_problems(lumos=lumos) if lumos else [("<situation>", "證據樣式自測要載入 scripts/lumos:" + lumos_why)]
    cat_text = CATALOG.read_text(encoding="utf-8")
    cat_rows = main_rows(cat_text)
    problems += api_decision_problems(cat_text, cat_rows, lumos=lumos) if lumos else [("<api>", "要載入 scripts/lumos:" + lumos_why)]
    for d, cfg in CONFIGS:
        want = sum(1 for r in rules if r["dir"] == d)
        got, skipped = loaded_count(sg, cfg)
        if got is None:
            problems.append(("<pack>", f"{cfg} 讀不到載入條數(掃描逾時或 ast-grep 跑不起來)"))
        elif got != want or skipped:
            problems.append(("<pack>", f"{cfg} 載入 {got} 條(略過 {skipped}),規則檔裡有 {want} 個 id"))
    by_id = {r["id"]: r for r in rules}
    for cfg, rid in SARIF_PROBES:
        want_dir = next(d for d, c in CONFIGS if c == cfg)
        if by_id.get(rid, {}).get("dir") != want_dir:     # 探針規則改名或搬走時講清楚,不要看起來像 SARIF 壞了(代碼審 r1 邊界 F4)
            problems.append(("<pack>", f"SARIF 探針的樣本規則 {rid} 不在 {want_dir}/,SARIF_PROBES 要換一條"))
            continue
        got, why = sarif_gate_rule_ids(sg, cfg, HERE / "samples" / "bad" / rid)
        if got is None and why.startswith("lumos:"):
            problems.append(("<pack>", f"SARIF 自測要載入 scripts/lumos:{why[6:]}"))
            break
        if got is None:
            problems.append(("<pack>", f"SARIF 掃壞例樣本跑不起來({cfg},{rid}:{why})"))
        elif rid not in got:
            problems.append(("<pack>", f"SARIF 掃壞例樣本沒有新增告警閘讀得到的 {rid} 結果({cfg})"))
    review_ids = {r["id"] for r in rules if r["dir"] in ("rules-review", "rules-unwired")}
    blocking_ids = {r["id"] for r in rules if r["dir"] == "rules"}
    # 每份設定檔對壞例、好例各掃一次,再依樣本所在目錄(samples/<bad|good>/<規則 id>/…)歸到各條規則
    hits = {}
    cross_hits = {}        # (好例所屬規則, 命中的會擋規則) → 處數;好例應該是標準寫法,別條會擋規則也不該報
    cross_files_hit = set()   # cross- 檔被別條規則命中過(證明它真的是跨規則邊界案例)
    scan_index = None
    for kind in ("bad", "good"):
        for d, cfg in CONFIGS:
            ranged = scan_ranges(sg, cfg, HERE / "samples" / kind)
            if kind == "bad" and d == "rules":
                # 反查的「規則」改由要看會擋規則在壞例報出的節點起訖行(同一次掃描,不另掃)
                scan_index = SCAN_FAILED if ranged is None else {}
                for rule_id, f, a, b in ranged or ():
                    scan_index.setdefault((rule_id, _sample_abs(f)), []).append((a, b))
            got = None if ranged is None else [(rid, f, a) for rid, f, a, _b in ranged]
            if got is None:
                problems.append(("<pack>", f"{cfg} 掃 samples/{kind} 跑不起來"))
                continue
            for rule_id, f, _line in got:
                owner = _sample_owner(f, kind)
                if kind == "good" and Path(f).name.startswith(REVIEW_FP_PREFIX) and rule_id in review_ids:
                    continue      # 語意覆核級或不接閘規則已知的形狀誤報:記在樣本裡、改形狀時對照,不算好例誤報
                if kind == "good" and owner and rule_id != owner:
                    if Path(f).name.startswith(CROSS_PREFIX):
                        cross_files_hit.add(str(Path(f)))
                    elif rule_id in blocking_ids:
                        cross_hits[(owner, rule_id)] = cross_hits.get((owner, rule_id), 0) + 1
                hits[(kind, owner, rule_id)] = hits.get((kind, owner, rule_id), 0) + 1
    for (owner, rule_id), n in sorted(cross_hits.items()):
        problems.append((owner, f"好例被會擋規則 {rule_id} 命中 {n} 處(好例要照每條會擋規則的標準寫;刻意放別條的壞寫法證明不重複報,要搬到 {CROSS_PREFIX} 開頭的檔)"))
    for f in sorted((HERE / "samples" / "good").rglob(CROSS_PREFIX + "*.kt")):
        rel = str(f.relative_to(HERE))
        if not any(h == rel or h.endswith("/" + rel) or h == str(f) for h in cross_files_hit):
            problems.append((_sample_owner(rel, "good") or "<pack>", f"{rel} 以 {CROSS_PREFIX} 開頭卻沒被別條規則命中(不是跨規則邊界案例就改回一般好例)"))
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
    if lumos:
        problems += bad_snippet_reach_problems(cat_text, cat_rows, rules=rules, scan_index=scan_index, lumos=lumos)
    else:
        problems.append(("<reach>", "要載入 scripts/lumos:" + lumos_why))
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
                for (i, f, _line) in got:
                    if any(r["id"] == i for r in test_only):
                        problems.append((i, "只掃測試碼的規則命中了祖先目錄叫 test 的正式碼:" + f))
    return rules, problems


def main(argv):
    if "--catalog-only" in argv:
        rules = load_rules()
        lumos, why = load_lumos()
        text = CATALOG.read_text(encoding="utf-8")
        rows = main_rows(text)
        if lumos:
            probs = [*catalog_problems(rules), *situation_sample_problems(lumos=lumos), *api_decision_problems(text, rows, lumos=lumos),
                     *bad_snippet_reach_problems(text, rows, rules=rules, lumos=lumos)]
        else:
            probs = [*catalog_problems(rules), ("<lumos>", "證據樣式自測、API 決策點與反查要載入 scripts/lumos:" + why)]
        for rid, why in probs:
            print(f"{rid}: {why}")
        print(f"型錄問題 {len(probs)} 個")
        _print_unverified()
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
        _print_unverified()
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
