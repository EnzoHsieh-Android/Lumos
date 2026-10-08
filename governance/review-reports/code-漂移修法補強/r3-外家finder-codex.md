severity: minor

## F1 超量清單指令繞過現存目錄名與格式字元處理

severity: minor  
blocking: 否  
引句:「return (f"git --literal-pathspecs -c core.quotePath=off show --name-only --diff-filter=AR --format= {sha} -- {rr}/"」  
file: `scripts/lumos:28039`  
file: `scripts/test_lumos.py:53761`

1. 當卷證目錄超過 20 個，主清單用 `_drift_c4_same_commit` 把 Git 的 NFC 名稱映射回磁碟實際名稱；補充指令卻直接以 `git show | awk` 輸出 Git 名稱。
2. 唯讀重現中，Git 回 `code-Café`、現存集合只有 NFD 的 `code-Café`，主清單正確回傳後者，但補充指令沒有任何 NFC→現存名稱映射。
3. 該指令也沒有 `_drift_c4_show_name` 的格式字元跳脫；使用者照貼後，含 RLO／零寬字元的隱藏目錄會以原始控制字元輸出。
4. 超量測試只建立 ASCII 名稱；NFD 與格式字元測試都未超過 20 個，因此沒有測到被改壞的補充指令分支。

## F2 兩態掃描沒有受刪除守衛總 deadline 約束

severity: minor  
blocking: 否  
引句:「before = _vendored_state(root, "HEAD")[0]」  
file: `scripts/lumos:29585`  
file: `scripts/lumos:29637`  
file: `scripts/lumos:33249`

1. 任何碰到工具檔的 staged diff 都會先完整執行 HEAD、暫存區兩次 `_vendored_state`；共啟動 36 次 Git 子程序。
2. 每次 `_lens_git` 各自最多等 20 秒，而 `cmd_delguard_check` 要到兩態全部算完後才呼叫 `_over()`；設定的總 deadline 無法中止這段。
3. 唯讀注入重現：設定 deadline 為 0.10 秒、每次 Git 呼叫延遲 0.01 秒，實際得到 `git_calls=36`、耗時 0.519 秒，最後才回報 timeout。預設 15 秒下，慢速物件庫或部分 clone 同樣可能讓 pre-commit 遠超時限。
4. 新測試驗了集合結果，但沒有驗證呼叫次數、剩餘時間傳遞或總耗時。

## 圖譜鏡頭逐條判定

- `Systems/存量漂移守衛`：主清單符合現存名稱與格式字元規則；F1 顯示超量補充路徑未遵守同一規則。
- `Systems/bound-tests-gate`：未改動合約測試解析、執行或阻擋判定。
- `Systems/guard-kill`：未改動回傳碼優先序或 JSON stdout 契約。
- `Systems/授權與歸屬`：未修改 vendored 白名單或授權檔處理。
- `Systems/測試假綠形態`：兩態主要分支具前置斷言；F1、F2 所述分支仍未被測試穿過。
- `Systems/lumos-cli-read`：未改動搜尋的 superseded／stale 濾網。
- `Systems/lumos-cli-lifecycle`：未改動 reinject 範圍或 sentinel 外內容。
- `Systems/design-loop`：未改動處置閘、計劃審材或條款綁定判定。

最高等級:minor