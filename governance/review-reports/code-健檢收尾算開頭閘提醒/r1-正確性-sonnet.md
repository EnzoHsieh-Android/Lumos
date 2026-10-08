severity: minor

## F1 三道「工具鏈設成擋」的開頭提醒沒有任何測試釘住計數
severity: minor
blocking: 否
引句:「_top_soft.append("筆記形狀擋")」
file: `scripts/lumos:1298`
1. 實測(clone 的暫存副本,清過 pycache):把 `_soft` 初始值改回 `{"segs": 0, "lines": 0, "heads": []}`,`t_doctor_summary_admits_soft_reminders` 確實翻紅(5 過 1 敗);還原後 6 過。所以「初始值」這個改動有被釘住。
2. 但釘住的只有「工具鏈本身跑 doctor 時會印的那一行」(存量漂移檢查 warn)。每支檔有家、筆記形狀、筆記內容審三處在工具鏈是 block,doctor 不會印,測試跑不到這三個 `_top_soft.append`。單獨刪掉其中任一個 append,該測試仍綠。
3. 影響:未來這三處若漏算,測試不會抓。建議補一個隔離 vault 把三道設成 warn/off 的案例,斷言「另有 N 段」等於實印 ⚠ 數。不影響本次正確性。

## F2 except 分支印的那行不算進段數(與測試的 ⚠ 計數一致,但語意上是漏網)
severity: minor
blocking: 否
引句:「print(f"  (筆記形狀擋的健檢提醒算不出來:{_e.__class__.__name__})")」
file: `scripts/lumos:1300`
1. 該行不含 ⚠,不進 `_top_soft`,與測試用「  ⚠ 」計數的口徑一致,所以測試不會因此紅。
2. 但這代表「提醒算不出來」這個狀況在收尾行是隱形的(收尾仍可能寫 0 段)。若視為提醒,應算一段;若刻意不算,建議在註解寫明。
3. 極端情形:若 helper 是回傳 list(現況三支皆是 `out` list),例外只會發生在 helper 內、回傳前,不會出現「已 append 一半又丟例外」造成的重複算。

## 已核對、無問題
- 四處各 append 一次、各自一行對一個 ⚠,無重複算;單條字串內含 `\n`(CI 貼步驟)仍只印一個 `  ⚠ `,段=條=1,與 `warn_soft` 之外的口徑一致。
- 每支檔有家那處的 `_nh_mode != "on"` 只在該條件下 append,與印出條件相同。
- `heads`:全檔只有 `scripts/lumos:1333`、`:1349` 兩處 append,沒有任何讀取者,初始值改成非空列表不影響用途。
- 治理帳 `soft=` 在 `scripts/lumos:3177` 取 `_soft['segs']`,語意從「正文各段」變成「開頭閘提醒 + 正文各段」,數值會多出最多 4;是預期的修正(與收尾行一致),但歷史帳的 soft= 序列在 2026-09-30 前後不可直接比較(該站點附近或筆記可加一句)。
- 實跑 doctor:收尾「另有 24 段」與實印 ⚠ 段數相符(測試 n_hard==0 分支斷言 n_soft==印出數,通過)。

最高等級:minor
