severity: minor

主程式載入這件事,新增的 `sarif_gate_rule_ids` 跟 check.py 既有做法有三處不一樣,都是形狀不同而不是結構錯。三處都在 `configs/ast-grep/kotlin-android/check.py`,全部列為 minor。

## 問 1:分層與依賴方向

方向一致。check.py 是規則包的自檢,往上借 `scripts/lumos`;`_kt_sit_row_check` 與 `_lint_run_and_parse` 也都由 `load_lumos()` 取得,沒有 import 主程式或繞過 `load_lumos()`。

但借用的形狀不同。情境題的 `situation_sample_problems(lumos=None)` 吃一個已載入的模組參數,只在 `lumos is None` 時才呼叫一次 `load_lumos()`。`sarif_gate_rule_ids` 沒有這個參數,每次呼叫都自己 `load_lumos()`。`SARIF_PROBES` 有兩筆,所以每次 `check()` 會多執行兩次約 4 萬行的 `scripts/lumos` 的 `exec_module`,加上情境題那一次共三次。

## F1 借主程式沒有可注入的模組參數,每次呼叫重新載入
severity: minor
blocking: 否
引句:「        return None, "lumos:" + why     # 呼叫端認這個前綴、另報一句,跟情境題證據樣式自測的寫法一樣」
佐證:file: `configs/ast-grep/kotlin-android/check.py:723`(對照 `check.py:474-477` 情境題的 `lumos=None` 參數與載入一次的寫法)

## 問 2:命名與錯誤處理

載入失敗時另報一句的做法,文字與情境題一致:兩處都是「要載入 scripts/lumos:」加 `why`。但訊號傳法不同。情境題在同一個函式裡判斷,直接回問題清單。SARIF 版把失敗原因塞進回傳值,用字串前綴 `"lumos:"` 傳給呼叫端,呼叫端再用 `why.startswith("lumos:")` 和 `why[6:]` 判斷。`load_lumos()` 本身回 `(模組或 None, 原因或 None)`,同一類失敗在 check.py 裡有了第二種編碼。

另外兩處小差異。`except Exception as e` 只回 `type(e).__name__`,而 `load_lumos` 同類的寫法是帶類別名加訊息。逾時判斷改成用 `time.monotonic()` 比較耗時,既有的 `scan` 與 `loaded_count` 是接 `subprocess.TimeoutExpired`。後者無法避免,因為逾時發生在主程式內;我也沒有逐一驗過 `scripts/lumos` 的 `_lint_run_and_parse` 逾時時的回傳,所以這點標 ⚠。

## F2 載入失敗靠字串前綴傳訊號
severity: minor
blocking: 否
引句:「        if got is None and why.startswith("lumos:"):」
佐證:file: `configs/ast-grep/kotlin-android/check.py:723-727`(對照 `check.py:474-477` 直接回問題;`check.py:432` 的 `(mod, why)` 元組慣例)

## F2b 錯誤原因的寫法與 `load_lumos` 同類 except 不同
severity: minor
blocking: 否
引句:「        return None, f"{type(e).__name__}"」
佐證:file: `configs/ast-grep/kotlin-android/check.py:731`(對照 `check.py:446` 的 `載入 {path} 失敗({e.__class__.__name__}:{e})`)

## F2c 函式內 `import time`,逾時判斷用耗時比較
severity: minor
blocking: 否
引句:「        if time.monotonic() - t0 >= SCAN_TIMEOUT:」
佐證:file: `configs/ast-grep/kotlin-android/check.py:720-734`(對照檔首 `check.py:11-17` 沒有 `time`;`loaded_count` 與 `scan` 用 `except subprocess.TimeoutExpired`)

## 問 3:第二種做法

借主程式的做法沒有分裂成兩套機制:兩處仍都走 `load_lumos()`,沒有另寫載入器,也沒有自己重寫 SARIF 解析。第二種的只有上述 F1 的「每次呼叫自己載入」。修補把 `sarif_rule_ids` 改名為 `sarif_gate_rule_ids`,並改成 `(值, 原因)` 回傳。對照 `scan()` 失敗回 `None`、`loaded_count` 回 `(None, None)`,回傳形狀在同一檔又多了一種(`(None, 原因)`)。`situation_sample_problems` 也回帶原因的結果,所以這點算是接近既有做法。

我沒跑 test_lumos.py 的 `t_kotlin_rulepack_samples`,也沒核對新增的改壞案例,因為派工詞只要求對照 check.py 的借用形狀。

不對齊共 4 條
