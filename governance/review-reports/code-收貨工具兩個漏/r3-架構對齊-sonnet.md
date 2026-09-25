severity: major

## 問 1:分層與依賴方向

對齊。`_report_findings_missing_severity` 改成呼叫既有的 `_h2_section_lines`/`_visible_lines`,跟鄰居 `_rollback_section_chars`(scripts/lumos:5316-5320)、`_door_exclusions`(scripts/lumos:5414-5416)是同一種「特徵函式呼叫共用找節工具」的方向,沒有反向呼叫、沒有新開一層。patch 註解本身也點名這件事:

引句:「找段用既有的 _h2_section_lines(代碼審 r2 架構席:找節邏輯不准長出第三套」

佐證:scripts/lumos:7254-7255(呼叫端註解)、scripts/lumos:5298(`_h2_section_lines` 定義,新加 `level` 參數但預設值 2 保留舊行為,兩個舊呼叫點 scripts/lumos:5318、scripts/lumos:5416 都不用改)。

`_report_findings_missing_severity(lines, top)` 收到的 `lines` 是 `_report_normalize_issues` already 用 `text.splitlines()` 切好的 list(scripts/lumos:7204),新碼裡 `text = "\n".join(lines)` 再轉回整段字串餵給 `_h2_section_lines`——這是型別轉換,不是新分層,跟舊呼叫點原本就吃 `text` 整段字串一致。

## 問 2:命名與錯誤處理

對齊。回傳形狀沒變,還是 `(行號, 訊息, 原始行)` 三元組,訊息文字逐字保留:

引句:「這條發現沒有自己的一行 severity: <值>(檔首判成非 clean 時,每個 F 段都要有;要請審查席自己補)」

佐證:scripts/lumos:7269(新碼)與 patch 裡刪掉的舊碼同一句,錯誤處理維持「回給呼叫端印出來要人改」的既有慣例,沒有另外 raise 或改用別的訊息格式。變數命名(`heads`、`rows`、`no`/`ln`)跟同函式家族的 `_door_exclusions` 用 `found`/`linenos`、`_rollback_section_chars` 用 `rows`/`no` 同一套簡短小寫慣例,沒有引入新命名風格。

## 問 3:第二種做法

### F1 同一個 patch 內,標題層級用兩種不同算法算

`_h2_section_lines` 判斷「同層或更高層標題」時用字串運算數 `#` 的個數:

引句:「len(ln) - len(ln.lstrip("#")) <= level and ln[len(ln)」

severity: major
blocking: yes

但緊接著在同一個 patch 裡,`_report_findings_missing_severity` 建 `heads` 清單算每個 F 標題的層級時,改用正則擷取群組長度:

引句:「heads = [(no, ln, len(m.group(1))) for no, ln in _visible_lines」

同一個概念(算 ATX 標題的 `#` 深度)在同一支 patch 裡出現兩種算法。而且 `len(ln) - len(ln.lstrip("#"))` 這個「算某字元連續出現次數」的寫法在專案裡已有前例——縮排計算就是這樣寫的:

佐證:scripts/lumos:3244 `indent = len(ln) - len(ln.lstrip(" "))`。

`heads` 那行的正則擷取寫法沒有沿用這個既有算法,是這支 patch 自己另開的第二種量法,不是跟鄰居不一致而是跟「自己另一半」不一致——正是這輪題目點名的「補丁與原文接縫處的新不一致」。

佐證:scripts/lumos:5308(`_h2_section_lines` 內)、scripts/lumos:7260-7261(`heads` 清單)。

### F2 comprehension 裡 bind 正則結果改用清單包一層,沒有沿用專案已有的海象運算子寫法

`heads` 清單推導式裡,要在同一輪迴圈拿到 `re.match` 的結果又要用它篩選,寫法是:

引句:「for m in [re.match(r"^(#{2,6})\s*F\d+\b", ln, re.I)] if m]」

severity: minor
blocking: no

專案裡已經有兩處用海象運算子做一模一樣的事(在 comprehension 內 bind 一個查找結果、順便當篩選條件),沒有用「包成單元素清單再迭代」這種寫法:

佐證:scripts/lumos:8176 `seats = len({a for r in latest if (a := r.get("auditor"))})`;scripts/lumos:9683 `len({a for r in [last] if (a := r.get("auditor"))})`。

python-idioms skill 沒有明文禁止或建議哪一種,證據較弱(只有兩個既有前例,且情境是 set comprehension 不是 list comprehension),標 minor 不擋。

---

不對齊共 2 條,其中 major 1 條。
