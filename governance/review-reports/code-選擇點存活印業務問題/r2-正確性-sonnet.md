severity: clean

總結:最高等級是 clean。上輪的兩條發現都修到了,修補沒有引入新問題,同類位置也沒有漏掉的。

**修補有沒有真的修到**
- 「①沒蓋到合併快篩判的存活」已修到。`scripts/lumos:78674` 用 `st.startswith("存活")` 判斷。帳上狀態字樣在 `_choice_ledger_status`(`scripts/lumos:78621`、`78625`)只有「存活」「存活(合併快篩判)」「已放行」「過期(…)」「跑不出結果」「殺掉 by …」「帳讀不了」。只有前兩種以「存活」開頭,其他字樣都不會多印。
- 新測試直接呼叫 `_choice_points_rows`,四種狀態的行數斷言是 `[2, 2, 1, 1]`。
  - 我走過一次改壞:把判斷改成 `st == "存活"`,「合併快篩判」那格會變成 1 行,測試就紅。所以這條測試有抓錯能力。
  - 反過來,漏掉「存活」前綴判斷時,「跑不出結果」與「已放行」那格會變成 2 行,也會紅。
- 「②`_choice_points_line` 改名」已修到。`scripts/lumos` 裡舊名已無殘留,唯一呼叫處在 `scripts/lumos:78699` 附近,已跟著換成 `_choice_points_rows`。

**修補有沒有引入新問題**
- 沒有。這次只動了函式名、呼叫端與測試,`_choice_points_rows` 的邏輯跟上輪相同。

**各個邊界輸入的走查**
- 型錄的 `why` 欄:`configs/ast-grep/kotlin-android/check.py:1457` 一律 `get("為什麼行為不同")`,鍵一定存在。`_choice_pick` 用 `row.get("why")`,沒有這個鍵時是 None。
- None、空字串、只有空白、「—」、「(無)」:`_choice_why_line` 都回空字串,不印。
- 含換行或連續空白:`" ".join(str.split())` 壓成一行。
- 控制字元與雙向覆寫字元:經過 `_kill_esc`,輸出已跳脫。
- 壞法字典多一個 `why` 鍵:`mutant` 字典只有 `_choice_points_rows` 與 `_ChoiceKillRun.finish`(`scripts/lumos:79257`)讀它。寫帳走 `_choice_event_extra`,參數是明列的欄位,不整包序列化,所以帳與 JSON 都不變。
- 冪等:純輸出,沒有狀態。

**推送前閘與 code-loop 預判**
- `scripts/lumos` 內的 `_choice_push_*`、`cmd_choice_points`、`_ChoiceKillRun` 不會在程式裡剖析這兩個指令的 stdout。
- `_ChoiceKillRun` 的 `finish` 印到 `self.out`;`redirect_stdout` 只包住 `cmd_guard_kill` 的內層,不影響這行。判定、rc、擋不擋都不變。
- 既有測試 `t_choice_kill_merge_rollback_lines`(S21)用「行含 `_CHOICE_MAIN`」篩行。新增那行是縮排的「為什麼行為不同:…」,不含檔路徑,所以不會誤入篩選;型錄裡的 `why` 也沒有放檔名。

**未標 finding 的觀察**
- 「為什麼行為不同」那行沒有像同函式其他欄位那樣截長度(`[:80]`、`[:160]`),但型錄是 repo 內自己的受控檔,我給不出具體的失敗場景,所以不標。

主要檔案:`scripts/lumos`(77880 `_choice_why_line`、78664 `_choice_points_rows`、79257 呼叫處)、`scripts/test_lumos.py`(149428 `t_choice_survivor_why`)。
