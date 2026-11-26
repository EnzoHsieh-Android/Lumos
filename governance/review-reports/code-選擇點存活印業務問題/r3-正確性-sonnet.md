severity: clean

總結:最高等級是 clean。三問與逐 hunk 檢查都沒有找出會出錯的輸入。

**修補三問**
- 修到沒:有。`_choice_points_rows` 改名 `_choice_points_lines`,全 repo 只剩三處,分別是定義 `scripts/lumos:78662`、呼叫 `scripts/lumos:78709`、測試 `scripts/test_lumos.py:149438`。grep 舊名 `_choice_points_rows` 在 `scripts` 與 `docs` 下零命中,沒有漏改的呼叫處。
- 新問題:沒有。同名 `def _choice_points_lines` 只有一處,沒有跟既有函式撞名。
- 同類位置:輸出行清單的函式都沒再用 `rows` 命名。`_choice_push_show` 回的是字串行,但不是這次 diff 新增的,也不在本主題範圍。

**逐 hunk 走過的輸入**
- 壞法字典多一個 `why` 鍵:型錄解析 `_choice_row` 本來就產出 `"why": get("為什麼行為不同")`(`configs/ast-grep/kotlin-android/check.py:1457`),`_choice_pick` 取 `row.get("why")` 有出處。壞法字典是記憶體裡的內部物件,`_choice_event_extra` 與帳不序列化 `mut`,新鍵不會被別處比對或寫進帳。
- 欄位為空、只有空白、`None`、`—`、`(無)`:`_choice_why_line` 先 `" ".join(split())` 再比對,四種都回空字串,測試有逐一驗。
- 控制字元:輸出走 `_kill_esc`,跳脫沒漏。
- 帳上狀態字樣:`_choice_ledger_status` 只產出 `存活`、`存活(合併快篩判)`、`已放行`、`過期(…)`、`跑不出結果`。`startswith("存活")` 只命中前兩種,`過期` 與 `跑不出結果` 不誤印。`not_unique` 與 `unrun` 的字樣不以「存活」開頭,不誤印。
- `choice-kill` 一路:只在 `verdict == "survived"` 時多印。`self.out` 與原行同一個串流,順序固定在原行之後、`flush` 之前。
- 長度:型錄實際最長 134 字,印時沒截斷,其他欄位有截斷。沒有具體失敗場景,不標。

**本案特定**
- 推送前閘與 `code-loop pass` 的判斷只看 rc 與帳,這次只換輸出,不改判定,所以不會因此改變擋或不擋。
- 型錄裡 53 列「為什麼行為不同」都是長句,另有 2 列是「排序方向相反」,沒有佔位字。

**測試**
- 測試不是結構檢查:行為斷言有逐一驗內容與位置,涵蓋 `_choice_points_lines` 四種帳上狀態、`choice-kill` 存活與殺掉、`choice-points` 讀帳存活與殺掉。
- 我沒有實際跑測試或做翻紅實驗,只讀了 diff 與真代碼。
