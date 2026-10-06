severity: minor

## 第 1 問:分層與依賴方向

結構對齊。新碼放在 `_kill_*` 殺傷力區段,跟鄰居同一層:file: `scripts/lumos:15088`(`_kill_p2_unbound`)沿用 `_kill_p2_survived`(file: `scripts/lumos:15205`)的形狀,吃 P2 掃描回傳的 `ctx`,回 `[(stem 清單, 一行文字)]`。它呼叫既有的 `resolve_test_refs`(file: `scripts/lumos:5621`)、`_kill_method_name`(file: `scripts/lumos:14655`)、`_kill_node_arg`、`_kill_show`、`_kill_esc`。kill-add 這邊,`_kill_add_after_lock`(file: `scripts/lumos:15365`)在鎖外呼叫新提醒,跟 `_kill_add_warn`(file: `scripts/lumos:15139`)同一個位置與時機,鎖內只多帶出合約行。doctor 端插在 `run_doctor` 的 P2 段尾(file: `scripts/lumos:3388` 一帶),跟 survived 提醒同段。`_KNOWN_GATES`(file: `scripts/lumos:7995`)與 `_GOV_LOCAL_PAIRS`(file: `scripts/lumos:1320`)都同步加了 check-p2t,跟 check-p2s 一樣。沒有跨層直呼。

## 第 2 問:命名與錯誤處理

大致對齊。命名 `_kill_*` / `_doctor_*` / `check-p2t`、測試 `t_*` 與 `_kb_` 前綴,都照 `_kill_*`、`check-p2s`、`_kr_` 的慣例。提醒走 stderr「⚠ 提醒:」、只提醒不改 rc、整段 try/except 兜底,跟 `_kill_add_warn` 一致。doctor 端用 `warn_soft` 加 `gov_events.append({"gate": ..., "kind": "warned", "hard": False, "nodes": [...]})`,跟 P2 survived(file: `scripts/lumos:3395`)同形。不一致只有 F3(`_doctor_p2_unbound` 把 `warn_soft` 當參數傳入)。

## 第 3 問:第二種做法

沒有「另一套定位合約行」或「另一套跳脫」的實質分叉,但有三處小重複或不對稱,列在 F1~F3。
- `_kill_find_contract` 的比對條件與 `_guard_kill_add_locked` 原迴圈逐字相同,是把它抽出來,不算新做法。但既有的兩處定位迴圈沒一起收:`cmd_guard_bind`(file: `scripts/lumos:14576`,用 `TEST_REF_RE.sub`,故意不同)與 `cmd_guard_audit`(file: `scripts/lumos:16326`,用 `INV_TAG_RE.sub`,跟新函式條件相同)。後者是現成的第二份。`_kill_rm` 走的是 `KILL_REF_RE` 加配方身分(file: `scripts/lumos:15720`),不是同一種定位,不算重複。
- `shlex.quote` 與既有跳脫:顯示用的字串走 `_kill_show` / `_kill_esc`,跟鄰居一致;只有指令參數那一處直接 `import shlex`。

## F1 合約行定位只收了一半,`cmd_guard_audit` 的同條件迴圈仍在
severity: minor
blocking: 否
新函式的說明寫「kill-add 定位與 doctor 對回合約行共用這一支,不另寫第二套」,但 `cmd_guard_audit` 的定位迴圈(`INV_TAG_RE.sub`、同樣的 many/none 判斷與同樣的錯誤訊息)沒改用它。結構上沒有新增分叉(只是抽出而已),但「不另寫第二套」的宣稱過頭,同一條件現在有兩份。`cmd_guard_bind` 用 `TEST_REF_RE`,條件不同,不算。
引句:「kill-add 定位與 doctor 對回合約行共用這一支,不另寫第二套。」

## F2 `_kill_norm_method` 在 `_kill_method_name` 之外再加一層拆殼
severity: minor
blocking: 否
既有 `_kill_method_name`(file: `scripts/lumos:14655`)已經做「去平台前綴、去 Kotlin 反引號」,並且寫明「kill 與算背書共用」。新函式在外面再包一層 `strip().strip("`").strip()`,而且只在這組比對用。倉庫其他位置(file: `scripts/lumos:5891`、`scripts/lumos:46232`)仍是各自 `strip("`")`。屬於「又多一個拆殼點」,但包住了舊函式而不是平行重寫,所以判 minor。更一致的做法是把空白處理併進 `_kill_method_name`,或在說明裡指到背書那邊的拆殼並寫明為何不能共用。
引句:「方法名正規化:去前後空白、去 Kotlin 反引號、再去空白——合約清單與配方兩側都過這一支(兩側原本拆殼方式不同)。」

## F3 `_doctor_p2_unbound` 把 `warn_soft` 當參數傳入
severity: minor
blocking: 否
`warn_soft` 是 `run_doctor` 的區域函式(file: `scripts/lumos:1669`)。既有的 `_doctor_*` 輔助(例如 `_doctor_stale_rules` file: `scripts/lumos:3823`、`_doctor_replacement_lines`、`_doctor_metric_lines`)都是只回行、由 `run_doctor` 自己印與落帳;P2 survived 也是 `_kill_p2_survived` 算、`run_doctor` 印。這支是第一個把區域印出函式和 `gov_events` 串列都傳進模組層函式的。屬於處理方式不一致,而不是新分層:算與印本來就拆成 `_kill_p2_unbound`(算)與 `_doctor_p2_unbound`(印),只是印的那半該回 `(行, 事件)` 由 `run_doctor` 內嵌處理,或照 survived 那段把 try/印/落帳留在 `run_doctor`。diff 自己也承認是為了降低 `run_doctor` 的複雜度,屬刻意取捨,不是疏忽。
引句:「warn_soft 是 run_doctor 裡的區域函式,由它傳進來」

## F4 指令參數引號直接 `import shlex`,沒用 `_sh_quote`
severity: minor
blocking: 否
倉庫有現成的 `_sh_quote`(file: `scripts/lumos:436`,「印給人照貼的指令裡的一個參數加 shell 引號」)。`_kill_binding_msg` 在函式內 `import shlex` 再 `shlex.quote(inv)`。同檔 `_kill_node_arg` 也是函式內 `import shlex`,另有十多處這樣寫,所以這個檔案裡兩種寫法並存,不算新引入;但同一功能已有命名工具,新碼仍應選 `_sh_quote`。不涉及控制字元風險:`inv` 先過 `_path_special_chars` 才進 `shlex.quote`。
引句:「fix = (f"要讓推送閘也守它:lumos guard bind {na} {shlex.quote(inv)} {meth}{pf}"」

⚠ 交編排者:`_kill_find_contract` 以後該不該連 `cmd_guard_audit` 一起收,是範圍取捨,我不硬判。本審查員沒有任何一條判 major:沒找到跨層直呼,也沒找到平行重寫的定位或跳脫實作。

不對齊共 4 條,其中 major 0 條
