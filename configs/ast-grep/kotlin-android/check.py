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
MSG_MAX = 120
REVIEW_FP_PREFIX = "review-fp-"   # 好例樣本裡記「語意覆核級規則已知會誤報、要靠盲判排除」的檔名開頭
SCAN_TIMEOUT = 120     # 一次掃描的上限(秒);正常不到一秒,卡住時不要拖到外層測試逾時          # 新增告警閘解析 SARIF 時把訊息截在 120 字
# 好例「一段」= 頂格開頭的宣告(函式、類別、物件、介面、帶註記的宣告)
_DECL_RE = re.compile(r"^(?:@|fun |suspend fun |private |internal |public |class |data class |object |interface |abstract |open |sealed |enum |val |var |inline )")
# 檢查會談暫存區路徑(型錄落地時要拿掉)
_SCRATCH_RE = re.compile(r"(/private/tmp/|/tmp/claude-|lumos-scratch|scratchpad/)")
TEST_ONLY_ANCESTOR = HERE / "samples" / "ancestor-named-test"


def _files_block_is_test_only(doc):
    """這條規則的 files: 區塊(只看那一段,不看 ignores 或訊息)是不是只列測試目錄。"""
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
_DT_COLS = 7         # 列編號|情境|標準寫法|不適用時|觸發字|對應檢查|來源
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
    i_src = text.find("\n## 來源縮寫")
    if i_src < 0:
        return [("<catalog>", "找不到〈來源縮寫〉節(來源欄的縮寫要對照它)")]
    i_src_end = text.find("\n## ", i_src + 5)
    abbrs = set(re.findall(r"^\|\s*([A-Z][A-Z0-9-]+)\s*\|", text[i_src:i_src_end if i_src_end >= 0 else len(text)], re.M))
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
            if not (re.search(r"https?://", src) or any(re.search(r"(?<![A-Z0-9-])" + re.escape(a) + r"(?![A-Z0-9-])", src) for a in abbrs)):
                problems.append((rid, "來源沒有網址或來源縮寫"))
    referenced, d_seen = set(), []
    for ln in dt.splitlines():
        if not re.match(r"^\|\s*D-\d+\s*\|", ln):
            continue
        c = _cells(ln)
        did = c[0]
        if len(c) != _DT_COLS:
            problems.append((did, f"決策表欄位數 {len(c)},應為 {_DT_COLS}"))
            continue
        d_seen.append(did)
        trig = [t.strip().strip("`") for t in re.split(r"[、,,]", c[4]) if t.strip()]
        if c[4].strip() in ("(無)", "\uff08無\uff09"):
            trig = []      # 刻意不設觸發字:這個情境沒有不常見的字面特徵,不出情境段,只靠規則包與代碼審
        elif not trig:
            problems.append((did, "觸發字不准空(刻意不設寫「(無)」)"))
        bad = [t for t in trig if t in STOP_TRIGGERS]
        if bad:
            problems.append((did, "觸發字含常用字:" + "、".join(bad)))
        if not c[6]:
            problems.append((did, "來源不准空"))
        refs = set(re.findall(r"[A-Z]+-\d+", c[5]))
        for r in sorted(refs - set(rows)):
            problems.append((did, f"對應檢查 {r} 不在型錄主表"))
        referenced |= refs
    want = [f"D-{i}" for i in range(1, len(d_seen) + 1)]
    if d_seen != want:
        problems.append(("<決策表>", "列編號要從 D-1 連號"))
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
            d = json.loads(ln)
            out.append((d["ruleId"], d["file"]))
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
    for d, cfg in CONFIGS:
        want = sum(1 for r in rules if r["dir"] == d)
        got, skipped = loaded_count(sg, cfg)
        if got != want or skipped:
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
                if kind == "good" and owner == rule_id and Path(f).name.startswith(REVIEW_FP_PREFIX) and rule_id in review_ids:
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
            for d, cfg in CONFIGS:
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
        probs = catalog_problems(load_rules())
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
