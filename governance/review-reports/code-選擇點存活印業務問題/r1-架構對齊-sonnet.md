severity: minor

**1. 分層與依賴方向:對齊**
- `_choice_why_line` 放在 `_CHOICE_STATUS_TEXT` 與 `_choice_pick` 前面的常數與小工具區(`scripts/lumos:77881`),跟 choice 那一段的小工具同層。
- 它只呼叫同層的 `_kill_esc`(`scripts/lumos:26905`),沒有跨層直呼。
- 它的資料來自型錄列:`_choice_pick` 回傳的壞法字典多一個 `"why": row.get("why")`(`scripts/lumos:78461`)。
- 型錄列的 `"why"` 鍵本來就由規則包自檢的 `_choice_row` 產生,取自「為什麼行為不同」欄(`configs/ast-grep/kotlin-android/check.py:1457`)。這沒有另開讀型錄的路。
- `cmd_choice_points` 原本內嵌的迴圈主體抽成 `_choice_points_line`(`scripts/lumos:78663`)。呼叫方向是 `cmd_choice_points` 呼叫它,它呼叫 `_choice_why_line`、`_CHOICE_STATUS_TEXT`、`_kill_esc`。
- choice-kill 的 `finish` 同樣呼叫 `_choice_why_line`(`scripts/lumos:79247` 附近),兩處共用一個函式,沒有複製兩份。
- 對照:`cmd_choice_points` 原迴圈在 `scripts/lumos:78700` 附近,`finish` 的 `ab` 印法在 `scripts/lumos:79255` 附近。

**2. 命名與錯誤處理:大致對齊,有一條 minor**
- 輸出方式對齊。
  - choice-kill 用 `print(..., file=self.out)` 加 `self.out.flush()`,跟同函式的結果行一致。
  - choice-points 用 `print` 到 stdout,跟鄰居一致。
  - 兩處都過 `_kill_esc`。
- 判存活的方式不同但有理由。
  - choice-kill 用 `verdict == "survived"`。
  - choice-points 只拿得到帳上狀態文字,所以用 `st.startswith("存活")`。
  - `_choice_ledger_status` 回的存活字串有「存活(合併快篩判)」與「存活」兩種(`scripts/lumos:78621`、`scripts/lumos:78623`),前綴比對兩種都涵蓋。
- 測試命名 `t_choice_survivor_why` 跟 `t_choice_kill_verdicts` 同系列,也用同樣的 `_ck_repo`、`_ck_run`、`_ck_loc`、`_CHOICE_MAIN`、`_ck_cleanup` 夾具。
- 沒有新增例外或錯誤回傳路徑。
- 不對齊 1(minor):`_choice_points_line` 名稱叫 `line`,實際回傳的是 list(0 或 1 行加上選配的為什麼行)。鄰居 `_choice_why_line` 回字串,語意不一致。
severity: minor
  blocking: 否
  引句:「def _choice_points_line(x, status):」

**3. 第二種做法:沒有**
- 沒有自創已有同功能的工具:跳脫沿用 `_kill_esc`,狀態字串沿用 `_CHOICE_STATUS_TEXT`。
- 沒有新輸出路徑,也沒有新的讀型錄方式。
- 兩條輸出路徑共用同一個 `_choice_why_line`,沒有各寫一份。
- 佔位字 `("", "—", "(無)")` 是寫在這支函式裡的字面值。我沒查到鄰居有共用的佔位常數可以沿用,所以不判第二種做法。

不對齊共 1 條,其中 major 0 條。

額外觀察,不列 finding:
- 工作樹有未追蹤的 `governance/review-reports/code-選擇點存活印業務問題/`,是審查材料本身。
- 表態記錄裡的 py-* 各題我只看這份 diff 的範圍,沒有發現與「全是同步程式」矛盾的內容。
