severity: minor

## F1 規則包節點的 WHY 行寫「逐列查完後是 0」，實際自檢印的是 2 列
severity: minor
blocking: 否
引句:「2026-11-07 逐列查完後是 0 [出處:[[Projects/Android寫法型錄逐列查證_計劃]]」
佐證: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md`（本 diff 新增的 WHY 行）
失敗場景：
- 我在 catalog-verify 跑 `python3.14 configs/ast-grep/kotlin-android/check.py --catalog-only`，輸出「型錄問題 0 個」和「還沒逐列查證 2 列:API-14、TEST-31」。
- 同一份 diff 裡計劃筆記驗收條款 S2 寫的是 2 列。
- 這句 WHY 和 S2 互相矛盾，也和實際輸出不符。下一個 session 的 AI 會以為沒有待處理的列，而 API-14、TEST-31 兩條會擋的規則其實還等人裁。
- 這是過期數字，不影響執行，所以只算 minor。

## F2 完整檢查路徑多印一行的行為沒有測試
severity: minor
blocking: 否
引句:「rc = m.main(["--catalog-only"])」
佐證: `configs/ast-grep/kotlin-android/check.py`（`main` 內，完整檢查那一段呼叫 `_print_unverified()`）
失敗場景：
- 計劃做法 5 和 diff 說明都寫「`--catalog-only` 與完整檢查都多印」。
- 測試只呼叫 `main(["--catalog-only"])`，完整檢查路徑沒走。我用 grep 查過，全 repo 的測試都沒有碰這個路徑。
- 把完整檢查那段的 `_print_unverified()` 刪掉，`t_kt_catalog_unverified_rows` 照綠。這是讀碼推得，我沒有實際改壞再跑。
- ⑤ 讀的是真型錄，只檢查輸出含「還沒逐列查證」這幾個字。把數字印成 0，或把清單截成別的格式，⑤ 也照綠。
- 被保護的行為只是提醒、不影響退出碼，所以不升到 major。

## 逐項核對結果（沒發現問題）
- **「出處不全只准提示級」**
  - `--catalog-only` 回報「型錄問題 0 個」。
  - 我另外用 main_rows 比對 34 列有標記的列：其中只有 TEST-12 名稱裡的 "coroutines" 字串恰好吻合規則檔名，那是比對上的誤判，其餘都沒有掛 `rules/` 會擋的規則。
  - API-14 和 TEST-31 刻意不標，與計劃一致。
- **統計節數字**
  - 我用 main_rows 重算：總列數 473、出處不全 34、有〔查證〕的 459、沒有的 14（473 − 459）。
  - 這 14 列包含 API-14、TEST-31 兩列，加上標了出處不全、也沒有〔查證〕的列。
  - 和統計節寫的相符。
  - 計劃寫的 331 列（verified 312、weak 16、contradicted 3）加起來也對得上。
- **CO-27 和 UI-100 的網址**
  - UI-100：我抓了原頁。compose-rules 寫的是以 `Previews` 當前綴，Slack compose-lints 寫的是以 `Previews` 當後綴，與改寫後的內容一致。
  - CO-27：kotlinx.coroutines 的 `withContext` 頁面有「because of having the same dispatcher…」那句。
- **抽查另外三列**
  - STATE-21：type-safety 頁面確實寫了 `toRoute`，只是示範的接收者是 `NavBackStackEntry`，我沒找到 `SavedStateHandle` 的明確示範。這是弱支持，沒有發現相反的說法。
  - DATA-37 和 FLOW-8：只確認了網址有寫進來源欄，沒有逐頁比對。
- **正規式的邊界輸入**
  - 來源欄有多個〔〕時，`[^〕]*` 不會跨括號，所以不會把〔併:…網址〕誤判成查證紀錄。
  - 〔查證〕沒有網址的會被當成沒查證。
  - 日期只檢查格式，`2026-13-45` 這種不合法日期也會算查過。這是現有型錄格式的限制，目前型錄裡沒有這種列。
- **名稱判斷的一致性**
  - 名稱含「出處不全」但不是「(出處不全)」標記的列，在目前型錄裡一列都沒有。
  - 所以 `catalog_unverified` 用「出處不全」、`catalog_problems` 用「(出處不全)」的差異，沒有造成實際不一致。
- **欄位數不足的列**
  - `main_rows` 會略過欄位數不對的列，這些列由 `catalog_problems` 回報。
  - `catalog_unverified` 不會因此出錯。

## 固定席逐條判定
- **Systems/kotlin規則包**
  - 型錄單一來源的 WHY 行：不受影響，因為 `--catalog-only` 回報型錄問題 0 個，`t_kotlin_catalog_rows_wired` 屬於 `-k kt_catalog` 子集。
  - 「誤報超過一成降級」的 RULE：不受影響，因為這批沒動任何規則等級。
  - 只有 F1 的 WHY 行數字過期。
- **Systems/測試假綠形態 ★INVARIANT★**
  - 新測試有「★前置★ 四列都被主表讀到」的前置斷言，證明被測的路徑確實執行過。
  - 合約沒有被破壞。
  - ⑤ 對真型錄的斷言力道偏弱，已列在 F2。
- **其餘固定席**（授權與歸屬、bound-tests-gate、canary-audit、guard-kill、lumos-cli-lifecycle 等）：不影響，因為它們只是被 `scripts/test_lumos.py` 連帶推出，而該檔只新增一支測試函式。
- **測試**：我跑了 `python3.14 scripts/test_lumos.py -k kt_catalog`，35 個通過、0 個失敗。

## 角色卡
- **be-api-compat**：沒有對外 API 變更。
- **be-authz**：沒有新增或改動端點。

總結:全篇最高等級為 minor
