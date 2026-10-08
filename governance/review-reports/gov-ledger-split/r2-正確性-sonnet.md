severity: major

# r2 正確性審(sonnet)——治理帳例行紀錄分流_計劃

白話:這份設計的核心是三道「該不該留版控」的閘門。我拿程式裡每個真的寫治理帳的地方去套,發現門檻有兩個漏洞:有一個「人用旗標繞過」的痕跡、和一個「真的擋了推送」的紀錄,會被規則誤判成例行觀察、掉進本機帳。另外「種類名單」用的是黑名單寫法,跟文中「分錯只會偏吵、不會偏丟」那句互相打架。

## 〈做法〉1 分流規則(逐呼叫點套用結果)

套用方式:閘名 = 觀察型名單內、`hard` 為假、種類不在留痕名單,三者同時成立才進本機帳。

已套完且結果正確(進本機或留版控皆與設計意圖一致):doctor-run/ran、check-* 的 warned、ledger-growth、daily-wrapper、delguard 的 ok、nodehome-check 的 passed/warned、note-shape 的 hinted/warned、note-reread 的 none/covered/reminded、drift-check 的 passed/warned/range-unavailable、bound-tests 的 green/red-advisory/range-unavailable/no-config/whole-suite-deferred、spec-gate-run 進本機;check-r 與 check-j 的 blocked(hard 真)、note-shape/nodehome-check/drift-check 的 blocked(hard 真)、各閘 skipped/skipped-env/fail-open/relaxed/degraded/acked/fix/recorded/waived/approved/prepare、code-loop/fix-check/design-loop/anchor/canary/lint-new/note-audit 整閘留版控。

套不上的有以下三條。

1. bound-tests 的 `skipped-flag` 不在留痕名單,人用旗標繞過合約測試的痕跡會進本機帳
引句:「種類不在「留痕種類」名單上:skipped、skipped-env、fail-open、relaxed、degraded(略過、繞道、放寬設定、工具出錯自動放行的痕跡)」
severity: major
blocking: 是——繞道痕跡在 CI 與別台機器看不到,正是〈實務隱患〉守衛面說三道保險要擋的事,判準屬正確性缺陷。
- 實際寫帳:`_bound_tests_check` 對 `--skip-bound-tests --note` 記的 kind 是 `skipped-flag`(只有環境變數那條才叫 skipped-env)。file: `scripts/lumos:42844`;經 `_bound_tests_log` 寫,`hard` 恆為 `kind == "red-blocked"` 即假。file: `scripts/lumos:42465`。
- 套規則:bound-tests 在觀察型名單、hard 假、`skipped-flag` 不在留痕名單(名單只列 skipped 與 skipped-env)——三條全過,進本機帳。
- 後果:這是帶 `--note` 理由的人為繞道(`scripts/lumos:42836` 的註解稱它為「逃生門…會留痕」,理由要讓別人看見)。分流之後換台機器、CI、全新副本都看不到有人繞過合約測試。同類:check-j 的 `shallow-skip`(gate 屬 doctor 各段 check-*,hard 假,種類不在名單),file: `scripts/lumos:5787`,它的註解明說「shallow 降級=顯性+僅 doctor --ci 留痕,不得靜默」。
- 修法方向:留痕種類名單補 `skipped-flag`、`shallow-skip`;但單補治標,見下面第 3 條。

2. bound-tests 的 `unfilterable` 會擋推送,卻以 `hard` 為假寫帳,「hard 為假 = 不是擋人」這條前提不成立
引句:「這筆不是擋人的紀錄(`hard` 為假)」
severity: major
blocking: 是——真的擋下推送的紀錄被規則歸成本機例行觀察,與〈實務隱患〉「`hard` 為真一律留」的保險假設矛盾。
- 寫帳端:`_bound_tests_log(repo_root, "unfilterable", …)`,hard 被算成 `kind == "red-blocked"`,即假。file: `scripts/lumos:42945`、`scripts/lumos:42465`。
- 擋人端:高風險推送中 `bt["status"] in ("red", "unfilterable") and not bound_advisory` 回 `blocked: True`。file: `scripts/lumos:43783`;單獨跑 bound-tests 子命令時也 rc=1。file: `scripts/lumos:43028`。原始碼註解明講「證不出跑過」跟紅一樣擋。
- 套規則:bound-tests 在觀察型名單、hard 假、`unfilterable` 不在留痕名單,進本機帳。被擋的人需要提交逃生旗標(第 1 條),擋人的那筆原始證據卻不在版控帳。
- 結論:hard 欄位不是「擋人」的可靠指標,至少 bound-tests 一個閘就把「擋」與 hard 脫鉤。規則 2 要嘛改成名單上逐種類寫明,要嘛把 bound-tests 整閘排除、或把 `unfilterable` 加入留痕名單並把 hard 改對(寫帳端的 hard 計算也是要動的程式)。

3. 閘名用白名單、種類用黑名單,新增種類落進本機帳,與文中「分錯只會偏吵,不會偏丟」自相矛盾
引句:「新增的閘或種類沒放進名單,就照舊進版控帳——分錯只會偏吵,不會偏丟。」
severity: major
blocking: 是——這句承諾對「新增的種類」是反的,第 1、2 條就是它的現成實例;S2 條款也只測已知種類,擋不住這類漏。
- 閘名那半成立:不在觀察型名單的新閘照舊留版控。種類那半不成立:留痕種類是「排除名單」,觀察型閘底下沒列進去的種類(`skipped-flag`、`shallow-skip`、`unfilterable`,以及未來任何新結果詞)規則 3 都會判成「不在留痕名單」而進本機。實際方向是偏丟。
- 修法方向:規則 3 反過來寫成「觀察型種類」白名單(passed、ran、ok、green、warned、hinted、none、covered、reminded、spec-gate-run、range-unavailable、no-config、whole-suite-deferred、red-advisory、fast、stale 等逐個列),沒列的一律留版控;或每個觀察型閘各自列自己的本機種類。這樣新增種類才真的偏吵不偏丟。
- 測試缺口:S2 測試名單只該拿「觀察型閘 × 非觀察型種類」做窮舉,現在看不出它會測 `skipped-flag`。

4. 觀察型閘名單寫「doctor 各段 check-*」,但名單被規定是常數(「各放一個常數」),沒說比對方式
引句:「閘名在「觀察型閘」名單上:doctor-run、doctor 各段 check-*、ledger-growth」
severity: minor
blocking: 否——可在實作時補一句,但文字沒寫死比對法會出兩種實作。
- `_KNOWN_GATES` 逐個列 check-cascade、check-e1…check-s11、check-lint-decl、check-p2 等,並沒有統一前綴規則。file: `scripts/lumos:7771`。用 `startswith("check-")` 與用 `_KNOWN_GATES` 內建名單結果相同,但新加 check-* 時前者自動進本機、後者要補名單;文中「兩份名單是唯一定義」讀起來是後者,「各段 check-*」讀起來是前者。
- 搭配第 3 條:前綴規則會把 check-j 的 `shallow-skip` 一併吃進本機。

## 〈做法〉5 讀者

5. 「doctor 的 spec-gate 比例段」把兩個不同的讀者混成一個,只有後半讀治理帳
引句:「doctor 的 spec-gate 比例段與 S18 度量改成讀兩本(抽一支模組層級的小函式給它們共用,`cmd_gov` 的 `load` 不搬)」
severity: minor
blocking: 否——只影響 S3 測試該釘在哪,不影響判定。
- S12 段的「有條款的計劃比例」讀的是 `.canary-log.jsonl` 與 Projects 筆記,不讀治理帳。file: `scripts/lumos:2842`。只有同段後半的「最近一次紅綠弱證據」讀治理帳的 `spec-gate-run`。file: `scripts/lumos:2869`。S3 說「spec-gate 比例段…兩本合起來算」,比例段合不合都沒差,真正要合的是紅綠弱證據那段。
- 順序風險:該處用 `_latest[node] = note` 以檔內順序取「最後一筆」。兩本合併時必須先讀版控帳再讀本機帳,否則舊的版控紀錄會蓋掉新的本機紀錄;設計沒規定順序。S3 條款只比「計數」,不比「最後一筆」。
- S18 度量:`_gov_metric_events` 以 `_gov_tail_bytes` 讀檔尾並回「最舊一筆時間」供暖機判斷,且入口有 `gl.is_file()` 守門。file: `scripts/lumos:3867`、`scripts/lumos:3695`。合併兩本時「最舊時間」該取哪個、版控帳不存在只有本機帳時守門怎麼走,設計都沒講(天花板 2 只講了跨機器的計數問題)。

## 〈範圍〉〈盤點〉使用紀錄帳

6. 「只有本機的使用統計在讀」與事實不符,且漏掉這本帳已宣告的未來讀者與到期條件
引句:「只有本機的使用統計在讀,沒有任何判定讀它。」
severity: minor
blocking: 否——停止追蹤本身不影響任何判定,但設計依據的敘述是錯的,且和一條尚未結案的回頭條件衝突。
- 程式裡沒有任何讀者(grep 只有寫入端 `scripts/lumos:16186`),也沒有「使用統計」命令去讀它;前半句是錯的,後半句才對。
- 這本帳 2026-08-21 被裁「不砍」的理由是「frecency 的種子語料,有宣告的未來讀者」,並掛 `REVISIT:2026-11-19`(零程式讀者就退場)。file: `docs/lumos-toolchain-knowledge/Verification/2026-08-21_工具鏈體檢修復批.md:41-43`、`docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md:67`。停止追蹤等於提前讓「跨機器累積語料」這個目的消失,設計沒提這兩處,也沒列進〈做法〉6 要同步改的筆記。

## 〈做法〉4 忽略規則與 init

7. 舊 vault 缺 `docs/.gitignore` 時不建,本機帳會變成未追蹤檔,甚至被 `git add -A` 提交成追蹤檔
引句:「`docs/.gitignore` 存在而缺這一行就在尾端追加,不存在就不建(維持「只加不覆寫」)」
severity: minor
blocking: 否——設計已承認「偏吵」,但沒承認它會永久把本機帳變成追蹤檔。
- 實際可達:2026-08-21 之前建 vault 的專案,忽略規則寫在 vault 裡而不是 docs/(`scripts/lumos:20870-20876` 的註解自述),`_scaffold_project` 遇到既有 vault 直接 return(`scripts/lumos:20865`),`_init_additive_setup` 只補 governance/.gitignore(`scripts/lumos:20885-20905`)。這類專案恰是本案盤點裡「本 repo」的同款情形,卻沒有給 root `.gitignore` 的對應處理。
- 後果:升級後第一次例行操作就多出 `?? docs/.governance-local.jsonl`——雲端工作階段看到的「有未提交改動」提醒照舊;一旦被提交,之後每次例行寫入都弄髒追蹤檔,S1 永遠不成立。
- 修法方向:`docs/.gitignore` 不存在而 vault 存在時也建出來(內容只含缺的那一行),不算覆寫。

## 〈驗收條款〉S1 與環境

8. S1「推送後所有進版控檔位元組不變」在淺層 clone 不成立 ⚠
引句:「當一次提交、推送與幾次 `lumos show`、`lumos context` 都只產生例行紀錄時,所有進版控的檔 應 一個位元組都不變」
severity: minor
blocking: 否——取決於雲端環境的 clone 深度,我沒法在本機確認。
- 淺層 clone 下 pre-push 的 note-shape、note-audit、note-reread、drift-check 都會寫 `skipped-env`「shallow clone」。file: `scripts/lumos:29680`、`scripts/lumos:30343`。`skipped-env` 在留痕名單,所以每次推送會往版控帳寫最多四行。CLAUDE 環境文件顯示雲端 session 的 `clone_depth` 預設 50(淺層),若本案動機的那種環境是淺層,工作目錄推送後仍然是髒的。
- 這是留痕名單把「環境結構性條件」和「人為繞道」混在同一個種類 `skipped-env` 的結果;〈天花板〉1 沒涵蓋它。⚠ 判不準:需要確認雲端 session 實際是否為淺層 clone,再決定「shallow clone」這類結構性略過是否改進本機帳(它不是人的繞道,但寫成種類名單要能區分,例如以 note 欄或獨立種類)。

## 實務隱患(逐類)

- 併發:無新增問題——本機帳與版控帳同層同批寫者,各自 `open(..., "a")`,併發樣貌沿用現況;設計明講不改原子性。兩寫入器的逐筆分流在同一批內分別開檔也沒有交錯風險。
- 回滾:無新增問題——還原提交後舊版不讀本機帳,只少了統計;`_pull_source_or_abort` 的聯集合併對「來源端 usage-log 被停止追蹤」也能處理(檔不存在時它取空串,`scripts/lumos:20585-20618`)。
- 相容:有,見第 7 條(舊 vault 缺忽略檔)。
- 資安/注入:無——本機帳內容與版控帳同源同欄位,不增加新的輸入面。
- 金流/對外送出/不可逆:無——設計已排除,兩本都只追加。
- 可執行性:第 3、4 條的名單比對法與第 5 條的合併順序,設計沒寫死,實作者各寫各的。

## 各節覆蓋

- 前言/PRIOR-ART/RETIRE-IF/REVISIT:已讀,無 finding。
- 〈盤點〉:第 6 條。其餘(7 本帳、四支直接寫入者、判定類讀者只讀 code-loop/fix-check/design-loop)已逐項查證屬實:判定類讀者(`scripts/lumos:1250`、`10198`、`11146`、`12367`、`42312`)讀的確實只有那三閘,hooks 與 `.github` 不直接寫治理帳。
- 〈範圍〉:已讀,無 finding。
- 〈做法〉1:第 1、2、3、4 條。
- 〈做法〉2:已讀,無 finding(`CI_LOG_NAME`/`_ci_log_path` 在 `scripts/lumos:38432`、`38525`,同層路徑說法屬實)。
- 〈做法〉3:已讀,無 finding(`_gate_event` 回 False、`_append_governance_log` 靜默吞錯與現況一致,`scripts/lumos:1358-1362`、`1425-1432`)。
- 〈做法〉4:第 7 條。
- 〈做法〉5:第 5 條。lint-new 自動放行計數只認 gate=lint-new 且 kind=fail-open(`scripts/lumos:25543`),fail-open 留版控,不改正確。
- 〈做法〉6:第 6 條(漏列筆記同步)。
- 〈實務隱患〉:第 1、2、3 條直接牴觸守衛面的三道保險。
- 〈驗收條款〉:第 8 條;S2 對第 3 條的測試缺口已併入。
- 〈回退〉〈天花板〉〈審計修正紀錄〉:已讀,無 finding。

## 總結

最嚴重 severity: major;blocking 條數:3(第 1、2、3 條)。
