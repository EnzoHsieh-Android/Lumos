severity: minor

**1. 分層與依賴方向:對齊。**
- 新的 `_choice_why_line` 放在 `_CHOICE_STATUS_TEXT` 正下方的常數區。它只呼叫 `_kill_esc`,與同區其他小函式相同。
- 呼叫它的兩處是 `_choice_points_rows`(`cmd_choice_points` 的下一層)和 `_ChoiceKillRun` 印存活行的那一處(`scripts/lumos:79257`),都是原本就負責輸出的位置。沒有跨層直呼。
- 「為什麼」欄的來源沒有另開讀型錄的路。型錄列本來就帶 `"why": get("為什麼行為不同")`(`configs/ast-grep/kotlin-android/check.py:1457`),`_choice_pick` 的回傳字典只多帶 `row.get("why")`,和同一字典已帶 `row`、`category`、`template` 的做法一致(`scripts/lumos:78461`)。
- 新增的鍵不會進帳,帳只吃 `identity`(`_choice_event_extra`)。

**2. 命名與錯誤處理:大致對齊,有兩處不一致。**

`_choice_points_rows` 回傳的是「要印的行字串清單」,命名卻用 `_rows`。
- 鄰居的 `_metric_rows`(`scripts/lumos:4740`)和 `_secev_backing_rows`(`scripts/lumos:9594`)回的是資料列。
- 回字串行的鄰居一律用 `_lines` 後綴,例如 `_doctor_metric_lines`(`scripts/lumos:4756`)、`_choice_merge_event_line`(`scripts/lumos:28890`)。

severity: minor
blocking: 否
引句:「def _choice_points_rows(x, status):」

`_choice_points_rows` 用顯示字串的前綴判斷存活。
- 鄰居 `_choice_ledger_status`(`scripts/lumos:78621-78623`)是用判定鍵(`disp`、`survived`)產生顯示字串,推送小結也用 `_CHOICE_PUSH_REASONS` 的鍵(`scripts/lumos:79460`、`79591`)分類。這裡改成反過來讀顯示文字,「存活(合併快篩判)」恰好也以「存活」開頭才沒漏。
- 結構上是能用的,所以列 minor。

severity: minor
blocking: 否
引句:「wl = _choice_why_line(mut.get("why")) if st.startswith("存活") else ""」

其他都對齊:
- 跳脫走 `_kill_esc`。
- choice-kill 這側用 `print(..., file=self.out)`。
- choice-points 這側用 `print`,和原本逐行 print 等價。
- 沒有新例外路徑。

**3. 第二種做法:沒有引入。**
- 沒有自創已有的工具函式:空白正規化用 `" ".join(x.split())`,跳脫用 `_kill_esc`。
- 沒有另一套輸出路徑,也沒有另一套讀型錄的方式。
- 測試對照 `t_choice_kill_verdicts`(`scripts/test_lumos.py:144285`)。它沿用 `_ck_repo`/`_ck_run`、`_load_lumos_inproc()`(全檔 989 處)、`subprocess.run([sys.executable, GRAPHCTL, "choice-points", …])`(`scripts/test_lumos.py:143705`、`143748`)的既有寫法。

⚠ 無需交編排者的不確定項。

不對齊共 2 條,其中 major 0 條
