severity: major

**F1**
severity: major
blocking: 是,照字面實作會讓 S2 寫不出任何事件,或撞上治理帳的讀者。
兩個事件的閘名都沒指定。
引句:「再用既有的治理帳寫入(`_gate_event_or_warn`,不改變呼叫端判定)為每條配方各寫一筆 `kind=guard-kill`」
file: `scripts/lumos:1220` `_gate_event` 對不在 `_KNOWN_GATES` 的閘名不寫。
file: `scripts/lumos:6943` 名單沒有 guard-kill、contract-evidence。
file: `scripts/lumos:7020` gov 用 `_KNOWN_GATES` 算未出現的閘。
file: `scripts/test_lumos.py:6458` t_gov_stats_gate_drift 掃所有 gate 字面值。
file: `scripts/lumos:7291` gov 已用 .kill-log.jsonl 當 gate=kill 來源,重用會算兩次。
file: `scripts/lumos:9207` 掛 code-loop 閘要登記 LOOP_NOT_CLOSE_EVENTS,否則 t_loop_close_kinds_classified 翻紅。
回退節說讀者只有本案與 gov 統計,實際 gov 去重、loop-close 分類、名單都是讀者。

**F2**
severity: major
blocking: 是,欄位對不上會讓去重把多筆併成一筆。
引句:「欄位 `node`、`invariant`、`test`、`platform`、`verdict`、`commit`(跑的當下 HEAD)、`files`(配方改到的檔)」
file: `scripts/lumos:1147` `_gate_event_build` 固定產出 commit(7 碼)、nodes、note、detail。
file: `scripts/lumos:7236` gov 去重鍵 (commit, nodes, gate, kind, token, check),多條配方會被折成一筆。
guard kill 現行存 rev-parse --short;短碼歧義沒處理。

**F3**
severity: major
blocking: 是,正常情況下就查不到背書。
「找同一個測試名」沒有比對規則;配方 --test 選填,沒帶時事件存什麼沒說。
引句:「找同一個測試名、`verdict=killed` 的最新一筆」
file: `scripts/lumos:36954` `_dispositions_split_test` 裸名歸 default 平台。

**F4**
severity: major
blocking: 是,背書連這支測試守的就是這題問的事都證不了。
任何配方 killed 一次就對任何被標題目算強證據。
引句:「找同一個測試名、`verdict=killed` 的最新一筆」

**F5**
severity: major
blocking: 是,改弱測試本身不會讓背書過期。
files 只是配方改的檔;測試檔未提交時事件綁的 HEAD 沒有這支測試。
引句:「從那筆的 `commit` 到被推送版本之間,`files` 裡任一支檔有改動 → 「背書過期,要重跑破壞測試」。」
file: `scripts/lumos:13096` 有未提交變更時以 HEAD 為基準的警告。
file: `scripts/lumos:37228` 要求被推版本的樹有測試名。

**F6**
severity: major
blocking: 是,核心流程漏了一步,消費專案照文件走會卡住。
事件寫在未提交的工作樹帳,CI 只讀被追蹤的帳;淺 clone 會讓每題判沒有背書。
引句:「做不到的就老實表態成「待辦」或「不適用」,不准用「已處理」矇過去。」
file: `scripts/lumos:36139` `_codeloop_read_from_ledger`。
file: `scripts/lumos:18250` 忽略清單屬實。

**F7**
severity: major
blocking: 是,字面實作 meta 讀不到 evidence 欄。
meta row 只有 id/question/applicable/triggered_by;`_ev` 是 satisfied 與 tension(suggested) 共用,放進 _ev 會連 tension 一起套。
引句:「在 `_STACK_QUESTION_SPECS` 的題目上加一個欄位 `evidence: "contract"`」
file: `scripts/lumos:21484` `_stack_applicability` meta row 欄位。
file: `scripts/lumos:37295` `_ev` 共用驗證。

**F8**
severity: major
blocking: 是,標的清單漏掉同類題,而且有一題把不相關的子問題一起綁住。
漏標 py-parallel、node-parallel、kt-coroutines、cs-async、py-memory、vue-watch、dart-async;cs-data、java-data 是綜合題;sql 棧通常沒有 test 平台。
引句:「`swift-concurrency`、`java-concurrency`、`fe-race`、`sql-transaction`。」

**F9**
severity: major
blocking: 是,技能文件與筆記對現況的描述會在上線後說錯。
引句:「技能文件(lumos-project-notes 寫合約那節、lumos-code-loop 表態那段)各加一小段」
file: `skills/lumos-code-loop/SKILL.md:12` 與 `skills/lumos-code-loop/reference.md:199` 寫「工具只驗證據存在、不驗答案對錯」。
file: `skills/lumos-code-loop/reference.md:562` 同句。
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:6` 指令表只提 stack_questions.gate。
file: `skills/lumos-project-notes/reference.md:590` guard kill 說明沒提寫治理帳。
file: `scripts/lumos:7057` gov 表態段只彙總 dispositions。

**F10**
severity: minor
blocking: 否,設定值語意落差。
引句:「設定寫壞照預設,並照 `_stack_questions_config` 既有慣例把說明放進回傳的 warnings」
file: `scripts/lumos:21417`

**F11**
severity: minor
blocking: 否,判定位置沒指明。
引句:「本案在沒有 docs/ 的專案比照合約測試那一關、不做背書判定,不加重那個死結。」
file: `scripts/lumos:1234`

**F12**
severity: minor
blocking: 否,輸出純度沒有新測試。
引句:「新增的治理帳寫入不得印任何東西到 stdout。」

**F13**
severity: minor
blocking: 否,實務隱患漏了快取新鮮度與效能預算。
引句:「資源:無新檔案、無新行程。」
file: `scripts/lumos:34871` 快取 TTL 1200 秒。

引用核對:十篇筆記與函式名、八個題目 id 皆存在。緣起、用詞、不做:已讀,無 finding。

更正總計:blocking 是 9 條(F1–F9),blocking 否 4 條(F10–F13)。
