severity: minor

審查甲三(r3,最後一輪)。兩條 finding,都是 minor,沒有 blocking。

## 逐項查證(乾淨的部分)

- **統計各數的取數**:在真型錄上逐條核對正規式,取到的行和數字都對。
  - 引句:「want += [(f"各級含 {lv}", rf"- 各級\(列的級含該字母[^\n]*?{lv} (\d+)"」
  - 各級兩行的 A 到 D 沒有串行或取錯。
  - 規則包 error / warning / info / hint 取對。`info 12` 前面有空白,所以 `\b` 不會因為中文字而失效。
  - 逐列查證那行有日期也有列數,`:(\d+) 列` 取到的是列數。
- **主題名比對**:`\bCO ` 沒有被 ARCH 或別處的字誤取。這個比對只在「- 各主題:」那一行內做,而且只取第一次出現。
  - 引句:「rf"- 各主題:[^\n]*?\b{t} (\d+)"」
- **rules 是 None**:跳過規則包那三組數字,`--catalog-only` 和推送前自檢走的都是 `load_rules()`,不受影響。
  - 引句:「if rules is not None:」
- **找不到統計節**:回報「找不到〈統計〉節」,沒有崩潰。我拿掉整個統計節實測過。
- **待查證節切節**:`_pending_table` 的 `j > i` 判斷在統計節缺席或順序顛倒時,會退回取到檔尾。
  - 引句:「sec = text[i:j] if j > i else text[i:]」
- **雙向比對邏輯**:「該列但沒列」「不該列卻列」「兩格寫不寫內容」三種情況都對。
  - `want == (cell.strip() in _PENDING_EMPTY)` 這一行,我四種組合都算過。
  - 兩欄列(`| API-3 | — |`)不會崩,而且正確報出代號格不一致。
  - 引句:「if want == (cell.strip() in _PENDING_EMPTY):」
- **接進 catalog_problems 後的呼叫端**:`python3.14 scripts/test_lumos.py -k kt_catalog` 是 81 passed,`-k kotlin_rulepack` 是 209 passed,`check.py --catalog-only` 是 0 個問題。
  - 新測試 t_kt_catalog_stats_consistent 只花 0.4 秒,沒有變慢。
  - 我找到的少數測試直接傳假規則(`catalog_problems([{...}])`),它們都是依規則 id 過濾結果,所以統計不一致不會讓它們變紅。
  - 引句:「problems += pending_problems(text, rows) + stats_problems(text, rows, rules)」
- **會擋的 `kt-webview-mixed-content-always`(誤報重點)**:用真 sgconfig 掃了 11 個輸入。
  - 沒報的:`AppSettings` 型別的 `s.mixedContentMode = 0`(只看變數名,不看型別)、`== 0` 比較、`0L`、`resolve(0,1)`、`BuildConfig.DEBUG` 成立那一支。
  - 報了且該報的:`apply{}` 內的賦值、`!BuildConfig.DEBUG`、`DEBUG` 的 else 分支、具名參數 `mode = 0`。
  - 引句:「webView.settings.setMixedContentMode(resolve(0, 1)) // GOOD 0 是內層呼叫的參數」
  - 沒找到具體誤報場景,不交 finding。
- **角色卡**:這份改動是 ast-grep 規則和型錄自檢,沒有新增或改動任何 API 端點、欄位或授權檢查,`be-api-compat`、`be-authz` 兩題都不適用。
- **圖譜鏡頭**:派工單沒附固定席筆記,不逐條判。

## Findings

### 1. `pending_problems` 遇到只有編號一格的待查證列會崩(`IndexError`)
severity: minor
blocking: 否

- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint-2/configs/ast-grep/kotlin-android/check.py` 裡 `pending_problems` 的 `for want, cell, what in (...)` 那一行(對應 r3-repair.patch 的 `+` 行)。
- 輸入:〈待查證〉節手寫了一列 `| API-3 |`(只有編號,沒有其他格)。
- 走到的行:`_pending_table` 把它切成 `['API-3']`。`pending_problems` 對第三格有 `pc[2] if len(pc) > 2 else ""` 的保護,第二格卻直接寫 `pc[1]`。
- 結果:整個 `catalog_problems` 噴 `IndexError`,用 `--catalog-only` 或推送前的規則包自檢會看到 traceback,看不到「這列欄位不足」的訊息。
- 重現:把型錄複本的 `\n## 統計` 前插入 `\n| API-3 |\n`,再呼叫 `catalog_problems(load_rules())`,得到 `CRASH IndexError list index out of range`。
- 對照:同一列寫成 `| API-3 | — |` 就正常報「待查的規則代號格跟主表對不上」。
- 附不出一條會擋推送的後果,所以是 minor(推送仍會被擋,因為退出碼非零;缺的只是訊息品質)。
- 引句:「for want, cell, what in ((code, pc[1], "待查的規則代號"), (src, pc[2] if len(pc) > 2 else "", "待核對的來源")):」

### 2. 〈統計〉裡計劃範圍 6 點名要重數的幾個數,自檢沒核對,改錯照綠
severity: minor
blocking: 否

- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-sec-lint-2/docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:79`
- 規格行寫「〈統計〉用程式重數:總列數、各主題、各級、情境、待查證、規則包條數(含不接閘條數)、被會擋的規則守到的列數、逐列查證列數」。
- `_stats_expected` 的清單裡沒有「情境」(形狀類 426、語意類 106)和「被會擋的規則守到的列數」(128)。「級的組合」、「出處不全 35」、「人裁 4」也沒核對。
- 我在型錄複本上改了這些數,`catalog_problems(load_rules())` 都回傳 `[]`:`形狀類 426→400`、`守到的列數 128→1`、`級的組合 A 207→A 100`、`出處不全的列:35→1`。
- 這些數不在驗收條款 S4 的列舉裡(總列數、各主題、規則包條數、不接閘),型錄統計節說明句也只列出實際核對的那幾個數,沒有騙人。
- 所以只是覆蓋不全,不是守衛失效。第 81 行的描述範圍比第 79 行窄,兩行沒有交代為什麼收窄,建議補一句,或把情境和守到的列數納入核對。
- 引句:「〈統計〉用程式重數:總列數、各主題、各級、情境、待查證、規則包條數(含不接閘條數)、被會擋的規則守到的列數、逐列查證列數。」(取自 r3-repair.patch 的上下文行)

## 總結

最高等級 minor,blocking 0 條(共 2 條 finding,都是 minor)。

臨時目錄 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/審查甲三-sonnet/` 留著,內有 `probe.py`、`cat.md`、`src/main/kotlin/T.kt`。沒有改 repo 任何檔。
