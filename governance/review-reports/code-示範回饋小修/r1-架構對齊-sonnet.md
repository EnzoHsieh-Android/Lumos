severity: major

**1. 分層與依賴方向:對齊**
- 補後綴寫在 `cmd_new` 內,接在名稱檢查之後(`scripts/lumos:22679` 起)。`cmd_new` 原本就在同一段做名稱檢查與擋下,位置與鄰居一致。
- 新增的兩列放進既有的 `_REQUIREMENT_FACETS`(`scripts/lumos:27870`),沿用 id/stage/q/when 四個鍵,列的順序也依 stage 排。形狀與 `perf-target` 等舊列相同。
- 沒有新增函式,也沒有跨層呼叫。
- 測試放在 `t_new_path_traversal` 附近,並用 `mkvault()` 與 `run()`。這與 `scripts/test_lumos.py` 裡 `t_new_teaches_tags` 的寫法一致。facet 測試沿用 `pitfalls --stage` 的呼叫方式,與 `t_backend_qo_stage_facets_only`(`scripts/test_lumos.py:57182`)相同。

**2. 命名與錯誤處理:部分不對齊**
- 命名沒問題:`req-scale`、`arch-sync` 都符合既有的 `req-`、`arch-` 前綴。
- 訊息不對齊。`cmd_new` 內其他攔截都是 `擋下:…` 加 `file=sys.stderr` 並 `return 2`(`scripts/lumos:22679` 起的 `擋下:名稱不能有斜線`、`擋下:--plan/--systems`)。附帶說明用 `提醒:…` 加 stderr。
- 新增這行是無前綴、走 stdout:`print(f"名稱補成 {name}_計劃(…)")`。
- 這行印在後面幾道攔截之前。之後如果被 `--plan` 檢查、`--code` 檢查或「已經有了」(`scripts/lumos:22727`)擋下,使用者會先看到「名稱補成」,最後卻沒建檔。
- 先例:全專案沒有任何指令在建檔時偷偷改使用者給的名稱。
  - 找到的自動補類程式都是補欄位或內部參數,例如 `scripts/lumos:21533` 補 `ended`、`scripts/lumos:39826` 的 `_drift_sh` 補 `./`。
  - 這些都不是使用者要建的筆記名稱。
- 計劃筆記的 `_計劃` 結尾慣例在現有程式裡走 lint 提醒:`scripts/lumos:6894` 的 `_nl_rule_lands_in` 只對 `_計劃.md` 檢查 lands_in,不對不合慣例的檔名做改寫。

severity: minor
blocking: 否 — 只是訊息前綴、串流與印出時機和鄰居不同,結構沒變。
引句:「print(f"名稱補成 {name}_計劃(計劃筆記的慣例;要建調研筆記就用 {name}_調研)")」

**3. 第二種做法:不對齊**
- `cmd_new` 對不合慣例或不合法的輸入,既有做法一律是擋下並回 `return 2`,沒建檔。這包括路徑逃脫、不認得的類型、旗標用在錯的類型、名稱撞名。
- 新碼對不合慣例的名稱改成靜默改寫後照常建檔,這是第二種處理方式。
- 同層的做法是擋下,並在擋下訊息裡教使用者怎麼改,例如「請改用 <名>_計劃」。
- 這會有實際後果:`lumos new project 訂單下單` 的輸出檔名與使用者打的不同。腳本或 AI 若接著用原名去 `set` 或 `append`,會找不到節點。
- 計劃書的 RETIRE-IF 也寫了「改回只提醒」,可見作者自己也在「擋、提醒、自動改」之間猶豫。
- ⚠ 要不要保留自動補,是產品取捨,我只判「跟既有做法不一樣」,交編排者裁。
- facet 兩列只是擴充既有表,沒有第二種做法。

severity: major
blocking: 是 — 引入專案原本沒有的「靜默改使用者輸入」做法,既有同類輸入都是擋下並教怎麼改。
引句:「if ntype == "project" and not name.endswith(("_計劃", "_調研")):」

不對齊共 2 條,其中 major 1 條
