severity: minor

**整體判斷**:新機制放對層、旗標與擋下風格照 `--finding-kind`/`--finding-source` 走,沒有引入結構性的第二種做法。有 3 條 minor(都是計劃沒講清楚、實作時容易岔出第二套寫法)和 1 個 ⚠。

## 1. 分層與依賴方向:對齊
- 寫側放 `cmd_canary`,跟 `--finding-kind`/`--finding-severity` 同一段。形式檢查在驗證區塊,同輪帳比對在讀進同迴圈帳之後、寫帳之前,跟 `--finding-source` 的兩段式一樣。對照:`scripts/lumos:19740`(`--finding-kind` 形式檢查)、`scripts/lumos:19777`(`--finding-source` 形式檢查)、`scripts/lumos:20021`(讀同迴圈帳 `_lrows` 後的核對)。
- 讀側走 `cmd_gov` 的 canary mapper 白名單與 `_GOV_FIELD_TYPES`。處置閘不讀這欄,跟 `finding_kinds` 一樣是純遙測。對照:`scripts/lumos:18510`、`scripts/lumos:18365`。
- 統計段加在 `_render_gov_stats` 的「發現在修什麼」後面。對照:`scripts/lumos:18113`。
- 範本加在 `_disposal_tpl()`,位置同 `--regression-set`。對照:`scripts/lumos:24852`。
- 小提醒(不算不對齊):既有核對段被 `if loop and round_id and outcome is None` 包著(`scripts/lumos:20021`)。計劃要「不帶 `--round` 也算」,所以新檢查不能直接塞進那個條件,得自己一個進入點。

## 2. 命名與錯誤處理:大致對齊,2 條 minor
對齊的部分:旗標名 `--finding-seat`、`id=值` 寫法、`action="append"`、rc 2、`擋下:--finding-seat …` 句式、「要跟 `--findings-set` 一起給」。對照:`scripts/lumos:81537`、`scripts/lumos:19636`。

不對齊:

### A1 覆蓋規則跟鄰居不同
severity: minor
blocking: 否
覆蓋規則跟 `--finding-kind`/`--finding-severity` 不同。這兩個是「給了就要 `set(x) == F` 全集」(`scripts/lumos:19751`、`scripts/lumos:19770`),`--finding-source` 是子集。計劃寫的是「必填時才要覆蓋,且全集是發現清單加重現不到清單」,「選填但給了」的情況沒說該擋全集還是只驗鍵 ⊆ 全集。
引句:「必填時,發現清單與重現不到清單的每個 id 都要有席位,缺的逐一點名。」

### A2 旗標名寫錯
severity: minor
blocking: 否
計劃的統計段引句寫 `gov --since-days`,但實際旗標是 `--since`(`scripts/lumos:81463`,參數 `since_days`)。照字面實作會多長出一個不存在的旗標。
引句:「`gov --since-days` 給得比 56 小時,照它給的;窗口取兩者較小」

## 3. 第二種做法:2 條 minor

### A3 生效日判法半套
severity: minor
blocking: 否
生效日的判法半套。計劃寫「照 `_CHOICE_SINCE` 的寫法」(日期常數加環境變數覆寫)。但 `_CHOICE_SINCE` 是用在推送閘,不是「迴圈首筆帳早於生效日」的判法。
- 專案裡「迴圈首筆帳」的既有做法:帶時區的 ISO 常數,用 `_loop_ts_key` 比,用 `_loop_first_ts_key` 取首筆,不回溯,沒有環境變數。壞 ts 時 `fail` 不放行。對照:`scripts/lumos:15770`(`_SECURITY_SEAT_SINCE`)、`scripts/lumos:13876`(`_CLAUSE_GATE_SINCE`)、`scripts/lumos:15936`(`_loop_first_ts_key`)、`scripts/lumos:36926`(壞 ts 的 fail 與首筆比對)。
- 日期常數加環境變數覆寫的既有做法(`_choice_since`、`_plan_sources_since`、`_kt_sit_spec_since`)比的是計劃建立日或推送當天,不是帳上 ts。對照:`scripts/lumos:77754`、`scripts/lumos:14744`、`scripts/lumos:74373`。
- 計劃把兩條路各取一半(YYYY-MM-DD 加環境變數去比帳上 ts),沒說怎麼換成可比的鍵、壞 ts 怎麼辦。實作若自己寫日期字串比對,就會長出第三種比法。
- 建議在計劃寫明:生效日換成 `_loop_ts_key` 可比的鍵,首筆取自已讀進來的 `_lrows`、排除結局帳(`_is_outcome_row`),壞 ts 沿用 `fail`。
引句:「生效日:常數 `_FINDING_SEAT_SINCE`,設成合進主線的隔天;環境變數 `LUMOS_FINDING_SEAT_SINCE` 供測試覆寫,不是 YYYY-MM-DD 就用常數。」
⚠ 要不要升 major 交編排者:計劃字面沒自創比法,只是沒講,所以我判 minor;若認為「日期常數比 ts」本身就是第二套,可升。

### A4 讀側型別檢查沒點名既有共用函式
severity: minor
blocking: 否
讀側型別檢查沒點名既有共用函式。`_finding_sources_typed`(`scripts/lumos:37051`)的註解寫明「寫側、處置閘、gov 讀帳共用這一支」,`_gov_event_types_ok` 另外單獨呼叫它(`scripts/lumos:18398`)。計劃⑥只寫「型別檢查(值要是字串清單)」,同形狀(dict 且值為字串清單)該重用或泛化這一支,別另寫一份。
引句:「治理帳讀側認得這欄:型別檢查(值要是字串清單)與 canary 列的欄位白名單都加上它」

- 統計窗口:`_render_gov_stats` 已有 `since_days`/`cutoff`(`scripts/lumos:18066`、`scripts/lumos:18074`),鄰居各段都吃這個窗口。計劃在段內再疊固定 56 天(取較小)。這是使用者 2026-11-21 裁定的,不算違規,但算段內第二個窗口,實作請從已傳入的 `cutoff` 往下算,別另讀時鐘。

## 4. 落點:合理,寫進既有那篇
- `--finding-source`、`--regression-set` 都已在 `Systems/loop-convergence-recording` 落地(grep 證實);`--finding-kind` 的家是 `finding-refute` 與 `每輪修補差異派工`。新旗標是載體記帳欄位加 `loop next` 範本,跟 `--finding-source`/`--regression-set` 同族,該寫進 `loop-convergence-recording`,不必另開。該節點只管 `scripts/lumos`(about_code),符合計劃改動的檔。
- 補一點:統計段那一小段(逐席沒用率)讀側歸 `gov`。`loop-convergence-recording` 有「gov 串接」節(`Systems/loop-convergence-recording.md:132`),寫在那裡就好。

不對齊共 4 條,其中 major 0 條。
