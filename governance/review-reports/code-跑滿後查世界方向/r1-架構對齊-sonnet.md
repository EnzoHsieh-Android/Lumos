severity: minor

## 一、分層與依賴方向

結論:沒有跨層直呼,也沒有共用判定反過來依賴呼叫端。

- `_cap_world_case`(`scripts/lumos:22406`)、`_retro_world_empty`(22424)、`_retro_world_check`(22440)都是純判定。它們不寫帳、不印訊息、不讀檔。`_retro_world_check` 透過 `bad(欄位, 原因)` 回呼報錯,跟 `_cap_retro_check` 內部的 `bad`(22507)是同一種形狀。專案裡本來就有帶 `bad` 參數的輔助函式,例如 `_repo_path_unsafe_why(root, rel, bad)`(51553)。
- 依賴方向沒變:`_cap_retro_status`(22673)呼叫 `_cap_retro_check`,`_cap_retro_check` 呼叫 `_cap_world_case` 和 `_retro_world_check`,沒有反向。
- 印提醒的動作留在命令層:`cmd_loop_retro`(23098 起,stderr,前綴 `[retro]`,跟同函式既有的 `[retro] 寫到…` 同一種)、`cmd_loop_cap_decision`、`cmd_loop_retro_stats`。
- 「合格回顧的唯一判定」仍只有 `_cap_retro_check`。`cmd_loop_retro` 在讀檔失敗那一支先用 `_cap_world_case(dec)` 算一次(23076),之後被 `_cap_retro_check` 回傳的 case 覆蓋。這是必要的,不算重算。

未發現不對齊。

## 二、命名與錯誤處理

結論:常數與函式的命名、錯誤處理、印訊息大致跟鄰居一致,只有一處命名偏離。

- 對得上的部分:
  - `_RETRO_WORLD_VERDICTS`(22130)是 kebab-case 英文 slug 的 tuple,跟 `_RETRO_FAMILIES`(22119)、`_RETRO_TARGETS`(22121)同形。
  - verdict 不在清單時的訊息用 `f"{_esc_clean(repr(v), 40)} 不在固定清單(…)"`,跟 22569 的 `family` 驗法逐字同形。
  - `_CAP_WORLD_HINT`、`_CAP_WORLD_FILL` 是中文訊息常數,跟 `_RETRO_DOSSIER_UNSAFE`(22328)同一種做法。
  - `_CAP_WORLD_CHECK_SINCE` 放在用它的區塊旁,沒有環境變數覆寫,跟 `_SECURITY_SEAT_SINCE`(14809)、`_LANDING_GATE_SINCE`(35429)一致。ts 解不開時偏嚴,跟 `grammar = first is None or first >= …`(14999)同方向。
  - `_cap_world_case` 回傳 `"required"|"optional"|"ignored"` 這種字串列舉,跟 `_cap_retro_status` 的 state 字串同一類。

### A1 `_cap_retro_fix_cmd_base` 的後綴跟專案「外殼加本體」的命名慣例不同
severity: minor
blocking: 否 — 結構對(外殼加本體),只是後綴偏離;不是第二種做法
引句:「def _cap_retro_fix_cmd_base(root, loop_id, state):」
file: `scripts/lumos:43361`(`_e2e_gate_body`)、`scripts/lumos:62440`(`_testmap_build_inner`)、`scripts/lumos:66982`(`_cmd_dispatch_lens_impl`)
- 專案裡「同一件事拆成外殼加本體」的函式,後綴用 `_body`、`_inner`、`_impl`,docstring 寫「…的本體」。新函式的 docstring 同樣寫「本體」,但後綴用了 `_base`。
- `_base` 在這個專案多半指 git 的基準點或基準提交:`_range_base`(61432)、`_lens_default_base`(65394)、`_codeloop_default_base`(70561)、`_fix_dispatch_base`(21541)。讀名字容易誤會。
- 建議改成 `_inner` 或 `_body`。

### A2 `_cap_retro_status` 的 `world_case` 是回傳 dict 裡唯一沒有初始值的鍵
severity: minor
blocking: 否 — 結構對,只是回傳形狀有一個鍵不固定
引句:「probs, data, res["world_case"] = _cap_retro_check(root, loop_id, dec, rows, rows_err, raw=raw)」
file: `scripts/lumos:22624`(`res = {"applies": False, … "data": None}` 開頭就列齊固定鍵)
- `res` 一開始把全部鍵列齊,讀的人可以預期每個鍵都在。`world_case` 只在走到 `_cap_retro_check` 才出現,docstring 寫「讀過回顧檔時才有」。retro-stats 因此得用 `st.get("world_case")`。
- 把下標寫進拆包目標也是專案裡沒有的寫法。
- 建議在 `res` 初始就放 `"world_case": None`。
- `_cap_retro_check` 回傳由兩個值改三個值本身跟既有慣例一致。專案裡 `_retro_parse` 回 `(data, perr)`、`_prov_read` 回 `(狀態, 路徑, 位元組)` 都是這種形狀,兩個呼叫端也都改齊了。

## 三、第二種做法

結論:沒有引入「第二種做法」。有兩處呼叫端的用法跟既有的唯一決定處不一致,都是結構對、細節偏。

- 網址驗法:新的 `re.fullmatch(r"(?i)https?://\S+", uu)`(22479)是專案裡第一個「檢查引用網址形狀」的地方。專案裡唯一另一處碰網址解析的是 `_secev_target_host`(10351),它用 `urlsplit` 取主機做授權判斷,目的不同。計劃筆記 PRIOR-ART 已說明刻意不解析的理由。兩者不重疊,不算第二套。
- 情況判定:仍只有 `_cap_world_case` 一支。
- 「`_cap_retro_fix_cmd` 拆成外殼加本體」本身符合專案既有的拆法(見 A1,只有後綴不同)。

### A3 `_cap_retro_fix_cmd` 是「唯一決定處」,但新的 `case=None` 讓部分呼叫端沒傳就悄悄少一句
severity: minor
blocking: 否 — 決定仍在一處,只是呼叫端不一致;計劃筆記做法 1 沒有把 doctor 與 retro-stats 列進去,看起來是刻意的
引句:「def _cap_retro_fix_cmd(root, loop_id, state, case=None):」
file: `scripts/lumos:2742`(doctor I2)、`scripts/lumos:23129`(retro-stats 的 `ent["cmd"]`)、`scripts/lumos:23032`、`scripts/lumos:23038`(`--template --write` 兩處擋下訊息)
- 函式開頭的說明仍寫「處置閘、canary 擋下、loop next、doctor、retro-stats、--check、--template --write 都呼叫它」,並說「每種狀態都給走得通的指令」。
- 這次新增的選填 `case`,有四處呼叫端各自重複寫 `_cap_world_case(st['decision'])`:22808、22850、22905、22963。上面三處不傳。
- 結果:同一個「要求世界查證但回顧沒有或過期」的迴圈,在 doctor 和 retro-stats 看不到「把查方向的結論寫進 world_check」那句,在擋下訊息和處置閘看得到。
- 建議二選一:
  - 讓不傳的呼叫端也傳。
  - 把 `case` 改成必傳,並在說明裡明寫哪幾處刻意不給。

### A4 `cmd_loop_cap_decision` 另外讀一次時鐘、組一筆假人裁,而不是用帳上那筆
severity: minor
blocking: 否 — 判定函式還是同一支,只是輸入來源跟其他四處不同;⚠ 判不準要不要升級,交編排者
引句:「now = _dt.datetime.now().astimezone().isoformat(timespec="seconds")」
file: `scripts/lumos:22905`(`_cap_retro_next_lines` 從 `st["decision"]` 即帳上那筆取 case)、`scripts/lumos:1601`(`_gate_event_build` 自己產 ts)
- 其他呼叫端的 case 都來自治理帳上的人裁事件。這裡在 `_gate_event` 寫完帳之後,另外讀一次時鐘,拼成 `{'decision': decision, 'ts': now}` 再丟進 `_cap_world_case`。
- 註解寫「跟剛寫進帳的那筆人裁同一刻」,但實際是兩次讀時鐘,不是同一刻。如果帳上 ts 是 `…23:59:59`、這裡讀到 `…00:00:00` 跨過 `_CAP_WORLD_CHECK_SINCE`,提示會跟之後 `--check` 判的 case 不一致。
- 另一條路是記完後用 `_cap_retro_status` 讀回帳上那筆,跟 `_cap_retro_next_lines` 同一種做法。

不對齊共 4 條,其中 major 0 條
