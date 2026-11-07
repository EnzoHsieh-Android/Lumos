severity: minor

三問都對照了 check.py 與 test_lumos.py 的鄰居和 scripts/lumos。以下是不一致的地方,其中沒有跨層直呼,也沒有引入專案原本沒有的做法(major 一條都沒有)。

## 問 1:分層與依賴方向

新碼放在 check.py,位置與依賴方向跟鄰居一致。

- `sarif_rule_ids` 放在 `scan()` 和 `loaded_count()` 之間(patch 第 104 行,check.py:685、:737 附近)。它被 `check()` 呼叫,沿用 `_TIMED_OUT`、`HERE`、`SCAN_TIMEOUT`,依賴方向跟 `scan()` 相同。
- `SARIF_PROBES` 放在模組層常數區,跟 `CONFIGS`、`MSG_MAX` 的寫法一致。
- check.py 沒有 import scripts/lumos,新碼也沒有,守住零依賴的邊界。
- `load_rules()` 沿用 `CONFIGS` 迴圈,把第四個目錄自動讀進來,沒有另開讀法。
- 測試的假 `sg` 腳本也在同一層,沒有越界。

### F1 load_rules 的 docstring 沒跟著改
severity: minor
blocking: 否
引句:「一條規則都沒讀到(rules/、rules-review/、rules-hints/、rules-unwired/ 都是空的?)」
佐證: `configs/ast-grep/kotlin-android/check.py:66`(`load_rules` 的 docstring 仍寫「讀三個規則目錄」,CONFIGS 已是四組;patch 同步改了 check() 的訊息,漏了這句)

## 問 2:命名與錯誤處理

錯誤回傳都是 `(id, 訊息)` 二元組,跟鄰居一樣。`sarif_rule_ids` 逾時和 OSError 回 None 的做法也跟 `scan()` 一致:`TimeoutExpired` 設 `_TIMED_OUT`、`OSError` 回 None、`returncode` 不在 (0, 1) 回 None、解析失敗回 None,而不是丟例外。

### F2 catalog_problems 用 `r.get("dir")`,message_problems 用 `r["dir"]`
severity: minor
blocking: 否
引句:「缺 dir 鍵照不在 unwired 算」
佐證: `configs/ast-grep/kotlin-android/check.py:393`(`catalog_problems` 新增 `r.get("dir")`)對照 `check.py:668`(`message_problems` 的 `r["dir"]`、`_DIR_SEVERITY.get(r["dir"], ())`)。同檔兩個鄰居對 dir 鍵的讀法不同,是為了讓既有的改壞案例(假規則沒帶 dir)繼續能跑,但容錯口徑不一致。

### F3 新測試名跟同主題的測試命名家族不同
severity: minor
blocking: 否
引句:「def t_kt_rulepack_unwired_dir():」
佐證: `scripts/test_lumos.py:126513`(新測試)對照 `:126344`(`t_kotlin_rulepack_samples`)和 `:126480`(`t_kotlin_rulepack_messages_cite_catalog`)。規則包測試同家族用 `t_kotlin_rulepack_*`,新測試改用 `t_kt_rulepack_*`。檔裡 `t_kt_*` 前綴確實存在(例如 `:128565` 的 `t_kt_catalog_unverified_rows`),但那批是型錄與判旗標的家族,同一個 `_ktpack` 規則包家族沒有 `t_kt_rulepack_*` 先例。

### F4 新測試帶 print 頭尾,同家族規則包測試不帶
severity: minor
blocking: 否
引句:「print("  ✓ t_kt_rulepack_unwired_dir")」
佐證: `scripts/test_lumos.py:126518`、`:126546`(新增)對照 `:126344–126480`(`t_kotlin_rulepack_samples`、`t_kotlin_rulepack_messages_cite_catalog` 都不印頭尾)。`:128570` 的 `t_kt_catalog_unverified_rows` 有印,所以這個寫法在檔內有先例,只是同族沒有。⚠ 判不準這算不算違反慣例。

## 問 3:第二種做法

### F5 sarif_rule_ids 是 scan() 的第三份子程序複本
severity: minor
blocking: 否
引句:「r = subprocess.run([sg, "scan", "--config", str(HERE / cfg), "--format", "sarif", str(target)],」
佐證: `configs/ast-grep/kotlin-android/check.py:685–711`(`scan`)和 `:737–750`(`loaded_count`)已經是同一套「run、逾時設旗標、OSError 回 None」的複本,`sarif_rule_ids` 是第三份。結構與鄰居一致,沒有另起一套呼叫方式,所以不算 major。只是三份各自維護同一段樣板。

- **SARIF 解析**:`sarif_rule_ids` 只取 `ruleId` 集合,而 scripts/lumos:42321 起的新增告警閘 SARIF 解析是取位置與訊息的完整 claims,用途不同。check.py 不能載入主程式,這點在圖譜 WHY(Systems/kotlin規則包.md:37)已記為刻意,所以我不列為第二種做法。⚠ 該 WHY 只談剝圍欄,沒談 SARIF。圖譜 REVISIT(:45)提到 check.py 已可借 load_lumos,SARIF 這支也受同一條 REVISIT 影響。
- **假 ast-grep 腳本**:`:126446` 的 junk 寫法是 `case "$*" in *--inspect*) exec sg ...`,新增的 fake 寫法是 `case ... *"--format sarif"*) body;; esac` 後 `exec sg "$@"`。兩者都是 shell 腳本加 `mkdtemp` 加 `chmod 0o755`,沒有引入新的假工具做法(例如 monkeypatch)。
- **暫存清理**:新假腳本的 `mkdtemp` 沒有清理,跟 junk 一樣。這是沿用鄰居做法,不算不對齊,但全域暫存清理規則要求用完刪掉,屬於鄰居的既有債,不計入。

不對齊共 5 條
