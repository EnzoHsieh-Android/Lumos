severity: major

問 1 分層與依賴方向:整體對齊——檢查讀治理帳加 git、不載圖譜,同 `_dispositions_verdict` 與 `_codeloop_read_from_ledger`(`scripts/lumos:36139`);破壞測試寫帳、表態檢查讀帳,同 cmd_dispositions 先例;`_dispositions_verdict` 本身不寫帳(`scripts/lumos:37261`)。

**A1 派工鏡頭改成讀治理帳**
severity: major
blocking: 是
引句:「現行附表態的 `_lens_dispositions_lines` 只讀表態標記、不讀治理帳,所以要多讀一次治理帳的 `guard-kill` 事件」
既有決策「鏡頭只讀 marker 不掃帳」寫在 `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:38`;`_lens_dispositions_lines` 只收已載入的 rec(`scripts/lumos:34822`);快取鍵只吃表態記錄 sha256(`scripts/lumos:35775`,暖機沿用 LUMOS_LENS_DISP_KEY)。這是新的跨層呼叫與第二條快取失效路徑;較貼近現況的做法是背書狀態在上游算好寫進表態記錄再交給鏡頭。⚠ 交編排者:不做 S11 是範圍取捨。

問 2 命名與錯誤處理:設定三段式與 `drift_check.old_sentence`(`scripts/lumos:28778`)、`note_shape.gate`(`scripts/lumos:24736`)同一套;壞值進 warnings 同 `_stack_questions_config`(`scripts/lumos:21417`)。

**A3 事件命名**
severity: minor
blocking: 否
引句:「再用既有的治理帳寫入(`_gate_event_or_warn`,不改變呼叫端判定)為每條配方各寫一筆 `kind=guard-kill`」
慣例是 gate=閘名、kind=動作或判定(`scripts/lumos:1179`);破壞測試已映射成 gate=kill、kind=七態(`scripts/lumos:7292`);`_gate_event` 對名單外閘名不寫(`scripts/lumos:1220`);新 kind 要判斷是否登記 LOOP_NOT_CLOSE_EVENTS(`scripts/lumos:9205`)。

**A4 欄位 commit**
severity: minor
blocking: 否
引句:「欄位 `node`、`invariant`、`test`、`platform`、`verdict`、`commit`(跑的當下 HEAD)」
`_gate_event_build` 已保留 commit 為 7 碼短 sha(`scripts/lumos:1185`),extra 會覆蓋;完整 sha 既有欄名是 head_sha(`scripts/lumos:1207`)。

**A5 並列、互不影響與 gate=off 提早 return 不符**
severity: minor
blocking: 否
引句:「跟既有的 `stack_questions.gate`(控制整個表態閘 all/high-only/off)並列、互不影響。」
`_dispositions_verdict` 在 mode=off 或 high-only 非 high 時提早 return(`scripts/lumos:37271`)。⚠ 交編排者。

問 3 第二種做法:

**A2 證據過期判法另寫一套**
severity: major
blocking: 是
引句:「從那筆的 `commit` 到被推送版本之間,`files` 裡任一支檔有改動 → 「背書過期,要重跑破壞測試」。」
專案現有證據有效性只有 `_codeloop_record_valid`(`scripts/lumos:37133`):同 sha,或祖先且中間只動簿記檔;表態與 code-loop pass 共用。設計另寫祖先加配方檔改動,是第二種;也沒沿用 _disp_git_timeout 與 rc 128 三態。合理做法是先呼叫 `_codeloop_record_valid`,額外條件疊在後面;只看配方檔要明說是刻意放寬並附理由。
重複落帳 minor 可接受:gov 已把 kill-log 映射成 gate=kill(`scripts/lumos:7292`),同一筆判定會以兩種 kind 出現,設計沒說去重。

問 4 落點:消費端落 Systems/棧別提問表態閘(99 行、管三支檔)、生產端落 Systems/guard-kill(75 行、管一支檔),方向合理,不需另開;gov 讀法沒列家(minor,⚠ 交編排者)。沒有 tension 表態可核對。

不對齊共 5 條,其中 major 2 條
