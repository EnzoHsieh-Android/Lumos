severity: minor

**1. 分層與依賴方向:對齊,沒有跨層直呼。**
- `_choice_why_line` 放在 `_CHOICE_STATUS_TEXT` 旁邊。它只做顯示字串加 `_kill_esc` 跳脫,不碰帳或型錄,跟鄰居的顯示層小函式同層。
- `_choice_points_lines(x, status)` 把 `cmd_choice_points` 迴圈裡的列印抽成回傳字串清單的小函式,形狀同 `_doctor_metric_lines`(`scripts/lumos:4756`,回傳 `out` 行清單、由呼叫端印)。`cmd_choice_points` 照舊負責 `print`。
- 型錄的「為什麼行為不同」欄走既有路徑:`configs/ast-grep/kotlin-android/check.py:1457` 讀成 `"why"`,`_choice_pick` 的回傳字典多帶 `"why": row.get("why")`,印的那端再用 `mut.get("why")` 取。這跟 `also` 鍵的帶法(`scripts/lumos:79224`、`:78673` 用 `mut.get("also")`)一致。
- `_ChoiceKillRun` 的 `finish` 在原本那行 `print(..., file=self.out)` 後面加印,仍走 `self.out`,沒有繞過既有輸出管道。

**2. 命名與錯誤處理:大致對齊,有一處不對齊。**
- 命名:`_choice_why_line`、`_choice_points_lines` 都是 `_choice_` 前綴加名詞,結尾 `_line(s)` 跟 `_doctor_metric_lines`、`_kt_sit_reminder_lines` 同型。
- 跳脫:型錄文字有過 `_kill_esc`,跟鄰居一致。
- 錯誤處理:新函式不丟例外,空值、「—」、「(無)」回空字串,印的那端用 `if wl:` 判斷。這跟 `mut.get("also")` 這類「沒有就不印」的寫法一致。
- 不對齊的一處:鄰居印出來的外來文字都截長度。`shown` 用 `[:_CHOICE_SHOW_MAX]`(`scripts/lumos:78670`),`reason` 用 `[:160]`(`scripts/lumos:79254`),`_kill_esc(str(e))[:160]`(`scripts/lumos:78701`)。這次的 `_kill_esc(w)` 沒有任何長度上限,型錄那一欄寫很長時整段原樣印出。結構是對的,只是輸出上限的慣例沒跟上。

severity: minor
引句:「return "" if w in ("", "—", "(無)") else f"      為什麼行為不同:{_kill_esc(w)}"」
blocking: 否

**3. 第二種做法:沒有引入。**
- 「存活那一行底下多印一行」沿用既有的行清單加 `print` 做法,沒有新的輸出通道、旗標或帳欄位。
- 測試沿用 `_ck_repo`、`_ck_run`、`_ck_cleanup` 夾具,以及 `GRAPHCTL` 子程序呼叫 `choice-points --diff main..HEAD --repo`(跟 `scripts/test_lumos.py:144787` 同寫法)。純函式檢查用 `_load_lumos_inproc`(`scripts/test_lumos.py:242`)。
- 用顯示字串前綴「存活」判斷要不要印,已是附理由放行的那一條,不再報。

不對齊共 1 條,其中 major 0 條。
