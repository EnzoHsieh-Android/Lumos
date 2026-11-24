severity: major

## 整體判讀

先用一句比喻交代。這份設計像先把 64 個碗整批丟進洗碗機,沒破就收工,有破再逐個檢查。思路本身站得住:合併只會把壞法判成存活,漏判的方向是「多擋一次要人看」,不會讓壞程式過閘。

我讀到的問題集中在「補丁與原文銜接」的地方:

- 介面只寫了一個布林參數,卻要承載好幾種資訊。
- 條款裡有一個子案例照字面寫不出測試。
- 有一處交叉引用指錯節。
- 幾處「所以是假、所以一致」的宣稱,在邊角情形下對不上程式碼。

推送閘讀治理帳那一道(缺紀錄、過期、守的測試雜湊、回報上限)在新形狀下判法沒有改變,詳見逐節走查。

## findings

### 接線只給一個布林 merge,承載不了 S7、S8、S11 要的資訊
severity: major
blocking: 是

位置:〈做法〉5 接線,對照〈做法〉2 時限與〈做法〉3 斷路器。

〈做法〉5 只說 `cmd_guard_kill` 多一個選用參數 `merge`,「真」就照 2、3 做,舊否決比對也說「只給 `cmd_guard_kill` 加選用參數 `merge`」。但 2、3 與條款要求的至少有三樣,布林帶不出來:

- **剩餘總時限。** 合併基準與每支單支基準的上限要不超過「`--max-seconds` 從 `t0` 算起的餘額」。`cmd_guard_kill` 目前沒有 `t0` 或 `max_seconds`,只有 `should_stop` 回呼,而回呼只回真假,給不出秒數(`scripts/lumos:28301`)。
- **斷路器跳開要回傳。** S8 要求 run 事件的 `merge_tripped` 是真。斷路器的狀態活在 `cmd_guard_kill` 內部,而 run 事件由 `_choice_kill_report` 寫。現行回傳通道只有 rc、`result_out`(給 kill-add 用)與 `on_row` 的列,spec 沒指定哪一條承載它。
- **`merged`、`single` 計數與 `judged` 的來源。** 每列的 `judged` 要在 `hk.flush` 裡組字典時帶出去(`on_row` 字典是 flush 寫死的鍵)。run 事件的 `merged`、`single` 要由 `_ChoiceKillRun` 彙整,spec 沒說從哪裡彙整。

具體例子:實作者照字面只加 `merge: bool`,S7(「合併基準的上限應不超過剩下的總時限」)寫不出測試,S8 的 `merge_tripped` 到不了 run 事件。這是介面缺口,不是措辭問題。

引句:「多一個選用參數 `merge`(真:照 2、3 做;同一個 `group` 連續、而且 file、old、new、also 都相同的配方是同一個壞法)」
引句:「每次單支基準與合併基準的上限都不超過這次呼叫剩下的總時限(`--max-seconds` 從 `t0` 算起的餘額)」
引句:「run 那筆 `merge_tripped` 是真」

佐證:
- file: `scripts/lumos:28301`(`cmd_guard_kill` 簽章沒有時限參數)
- file: `scripts/lumos:28648`(`_KillHooks` 只有 `should_stop` 回呼)

### RETIRE-IF ③ 把斷路器指到〈做法〉4,斷路器實際寫在〈做法〉3
severity: minor
blocking: 否

〈做法〉4 是「中斷與時限」,沒有斷路器。斷路器是〈做法〉3 的第三個項目。三個月後的接手者照引用去 4 找會找不到。其餘交叉引用我都核對過,都對得上:
- 〈做法〉5(`_gov_row` 的 `ck`)
- 〈做法〉3(合併快篩)
- 〈用詞〉(乾淨、判法)
- 〈預期效益〉、〈人裁紀錄〉

引句:「累計 10 次以上呼叫裡,斷路器跳開(見〈做法〉4)的超過三成」
引句:「同一個平台組連續 5 個壞法的合併快篩」

### S5 的「基準帶不確定標記」案例在合併模式下不可能發生
severity: minor
blocking: 否

這一條也牽涉「照字面寫成測試」的要求。

- 程式裡的 `b_unsure` 是存基準時 `bool(mstate["unsure"])` 的值(`scripts/lumos:28459`)。
- 〈做法〉2 讓合併模式的所有單支基準都在第一個壞法之前、乾淨的樹上量完,此時 `mstate["unsure"]` 一定是空集合。
- 所以 `b_unsure` 在合併模式下恆為假。〈做法〉2 自己也寫了「逐支流程一定用乾淨樹的基準」。
- S5 的條款文字與預期值表第二案「基準帶不確定標記」,不用特殊改造就觸發不了。〈做法〉3 把它列為跳過條件也是空轉。
- 同一處還有兩個不清楚的地方:
  - 「`_mtime_unsure`」其實是寫在結果列上、跑完才設的鍵。跑之前判斷用的是 `mt_ok` 加 `mstate["unsure"]`(`scripts/lumos:28503`),spec 沒有對應。
  - 「不跑合併,直接逐支流程」沒說要先把已寫入的壞法還原。不還原的話,逐支流程讀檔時 `old` 命中 0 次,會把整批判成 drifted。

引句:「基準帶不確定標記(`b_unsure`)→ 不跑合併,直接逐支流程」
引句:「逐支流程一定用乾淨樹的基準」

### 「weak 一律是假」與現行還原後的弱證據蓋法在邊角情形不同
severity: minor
blocking: 否

〈做法〉3 說合併快篩乾淨時各列 `weak` 是假,理由是弱證據來源上面都排除了。但現行程式在壞法還原之後,若還原的修改時間沒錯開,會把當次結果的 `mt_ok` 設假,並蓋上 `_mtime_unsure`(`scripts/lumos:28503`)。

具體例子:合併快篩全綠,但還原後修改時間沒錯開(粗時間精度的檔案系統)。

- 現行逐支流程這支壞法會記弱證據,判成 no_result「弱證據」。
- 合併路徑照 spec 字面會記 `weak=false` 的存活。
- 同一個輸入在 `--no-merge` 與合併下判定不同。這與 S13 的「除 `judged` 與 run 新欄,輸出與帳相同」衝突。

spec 沒說合併路徑的還原後檢查要不要回頭影響那幾列。

引句:「上面已排除所有弱證據來源,所以是假」

### 合併快篩全綠時「每支守的測試各交一列 survived」與基準不綠拿掉的測試對不起來
severity: minor
blocking: 否

〈做法〉2 說單支基準不綠就「照現在記 abort 拿掉」,合併基準只含單支綠的測試。〈做法〉3 卻寫乾淨時「每支守的測試各交一列 survived」。字面實作會把單支基準不綠的測試也交成 survived 列,蓋掉本該記的 abort 列。

這會產生兩個差異:
- 帳上 `aborted` 清單與 `--no-merge` 不同(`scripts/lumos:78208` 的 `aborted` 由列的 verdict 推出),又與 S13 衝突。
- 〈做法〉1 的「守的測試至少 2 支」是在量基準之前算的。拿掉不綠的之後只剩 1 支時,仍照合併處理,與「至少 2 支才合併」的意思不符。

引句:「這個平台組這支壞法的每支守的測試各交一列 survived」
引句:「單支不綠照現在記 abort 拿掉」

### 完整名的算法引用 classname 與 name,但 junit() 只回合併好的 id
severity: minor
blocking: 否

〈用詞〉的完整名定義用的是結果檔案例的 `classname` 與 `name` 兩個欄位。`test_quality.junit()` 回的案例只有 `id`(`classname::name` 連成一串)、`status`、`assertion_failure`、`reason`(`scripts/test_quality.py:229`),沒有獨立的 `classname` 與 `name`。實作者要自己決定怎麼拆 `id`:

- 第一個 `::` 拆。
- classname 為空字串時 `id` 開頭就是 `::`。
- 兩個 `$` 與 `(`、`[` 的處理順序。

S15 的預期值表沒有涵蓋空 `classname`。

引句:「結果檔一筆案例的 `classname` 把 `$` 換成 `.` 之後,加 `.`,加 `name` 去掉參數尾巴(第一個 `(` 或 `[` 起到結尾)」

### 斷路器會把「壞法編不過」當成合併沒跑乾淨而累計
severity: minor
blocking: 否

斷路器的計數條件包含「rc 不是 0 但沒有失敗案例」與「結果資料夾不在」。壞法編不過時,Gradle 的 rc 非 0、結果資料夾被刪過所以不存在,正好符合這兩項。

具體例子:連續 5 個壞法編不過(型別替換類壞法常見)。合併在這個平台組被停用,但合併本身沒有任何問題。

spec 把 `_KILL_COMPILE_RE` 的樣式只用在 S4 的判定,沒有把它排除在斷路器計數之外。RETIRE-IF ③ 的「斷路器跳開超過三成」會被這類情形灌水,導致誤把合併撤掉。

引句:「rc 不是 0 但沒有失敗案例、結果資料夾不在」

### 合併基準階段收到第一個中斷訊號,可能要等很久
severity: minor
blocking: 否

〈做法〉4 只讓第一個訊號當場收掉合併快篩的程序群組,基準階段「照現在」等正在跑的那支跑完。

但〈做法〉2 把合併基準的上限定成 `min(max(600 秒, 下限, 30 秒 × 支數), 剩下的總時限)`。64 支時是 1920 秒,遠大於現行單支基準的 600 秒。合併基準掛住時,第一個 SIGTERM 要等到上限才返回。

「中斷」隱患段說「等待回到現在的量級」,只對合併快篩成立。S7 的「基準階段收到第一個中斷訊號 應 在下一支基準之前停」也沒涵蓋合併基準本身。

引句:「逐支流程與基準階段的中斷照現在(等正在跑的那一支跑完,約 5–6 秒)」
引句:「合併基準上限 = min(max(600 秒, 下限, 30 秒 × 支數), 剩下的總時限)」

### 其他平台已殺掉這個壞法時,合併快篩要不要略過沒寫
severity: minor
blocking: 否

`cmd_guard_kill` 依平台分組依序處理,同一個 `group` 在某平台被決定性殺掉後,其他平台的配方由 `hk.between` 記成略過(`scripts/lumos:28441`)。〈做法〉3 的合併快篩排在「套壞法」之後,而略過判斷在 `between`,spec 沒有說快篩前要不要先查 `hk.stopped`。

具體例子:平台 A 逐支殺掉這個壞法,平台 B 的快篩還是會跑一次(1–5 分鐘),再被丟掉。S10 只測了 A 先全存活、B 再殺掉的順序。

引句:「合併在每個平台組各自判。某個平台組判全部存活就交出那個平台組這支壞法的存活列」

### 治理帳 ck 子字典目前沒有 ran,與「既有的 ran」的說法不符
severity: minor
blocking: 否

〈做法〉5 說 `judged`、`merged`、`single`、`merge_tripped` 與「既有的 `ran`」照 `_gov_row` 現有的 choice-kill `ck` 慣例加進去。實際上:

- `ran` 只在 `_GOV_FIELD_TYPES` 裡有型別登記。
- `ck` 子字典白名單是 file、fp、killing_test、changed、mutant_lines、secs、reasons、site(`scripts/lumos:18553`),沒有 `ran`。

RETIRE-IF ② 與 S11 都要從 `ck` 讀 `ran`,所以 `ran` 也要加進白名單。spec 的「既有」會讓實作者以為不用動。

引句:「`judged`、`merged`、`single`、`merge_tripped` 與既有的 `ran` 照 `_gov_row` 現有的 choice-kill `ck` 子字典慣例加進去」

### 人裁紀錄第四筆(c4)的殘句與新形狀不符
severity: minor
blocking: 否

第六筆(第二輪後換形狀)明列了被取代的是第五筆、第一筆,以及第二筆的環境變數名。第四筆說的「測試互相影響記錯殺掉它的測試(c4)」在新形狀下不可能發生,因為合併永遠不判殺掉。這一筆既沒被取代,也沒被改寫。

三個月後的接手者讀到「放行,寫成已知限制」,找不到對應的已知限制。〈實務隱患〉只寫了漏殺(把該殺的記成存活),沒有 c4 或 rb4 的對應。

引句:「測試互相影響記錯殺掉它的測試(c4)與放行檔蓋過帳(rb4)放行,寫成已知限制」

### 預期效益表假設一次呼叫跑完,與預設旗標不符
severity: minor
blocking: 否

「合併快篩」那一列把一次性單支基準約 6 分鐘加上合併基準約 1 分鐘算一次,等於假設一次呼叫跑完 183 個壞法。但 choice-kill 預設是 `--max-mutants 30`、`--max-seconds 1800`(`scripts/lumos:78012`、`scripts/lumos:78013`)。照預設跑約 7 次呼叫,每次都付約 7 分鐘開頭成本,約 49 分鐘,表上沒有。

RETIRE-IF ② 用 `secs ÷ ran` 的中位數比上線前後,而上線前的呼叫沒有開頭量齊的成本,所以分母小的呼叫會被拉高,比較基準不對等。〈做法〉6 的基線有帶 `--max-mutants 200 --max-seconds 86400`,但表頭沒註明「合併快篩」一列用同樣的長時限。

引句:「一次性單支基準約 6 分鐘 + 合併基準約 1 分鐘」
引句:「同一專案上線後 run 事件 `merged` 大於 0 的呼叫,`secs` 除以 `ran` 的中位數」

### 回退要找 merged 存活的行,但沒有指令可以列
severity: minor
blocking: 否

〈回退〉叫人「從帳上 `judged` 為 merged 的存活找」,但 `lumos choice-points`、`gov --stats` 都沒有被要求顯示每筆的 `judged`。S11 只要求 `gov` 在 `ck` 帶出欄位,沒有列出清單的指令。三個月後的接手者只能自己 `grep` 帳檔。

引句:「要挑哪些行,從帳上 `judged` 為 merged 的存活找」

## 逐節走查

- **白話、WHY、PRIOR-ART、REVISIT:** 已讀,無 finding。出處與 `_run_cmd_expand`、`test_quality.junit`、`_secev_junit_facts` 的引用都找得到(`scripts/lumos:28053`、`scripts/lumos:9046`、`scripts/test_quality.py:250`)。
- **RETIRE-IF:** 有交叉引用錯誤,見上。
- **舊否決比對:**
  - 規格閘那條平行否決存在。
  - guard-kill 的「另抽一支共用的殺傷力函式」確實有三處。
  - 改動選擇點計劃〈用詞〉殺掉判定的「基準只跑一次」與本案相容。
  - 已讀,無 finding。
- **實測(來源):** 「基準每條測試指令第一次用到時才量、每次呼叫重新量」與程式碼一致(`scripts/lumos:28455`)。已讀,無 finding。
- **用詞:** 完整名定義的欄位對不上 `junit()` 的回傳,見上。`junit()` 在任何 `<error>` 或 suite 層 errors 大於 0 時直接丟 `suite_error`(`scripts/test_quality.py:269`),所以「案例是 error」的分支實際上走不到,但不影響判定方向(都走逐支)。
- **做法 1:**
  - 單一入口的引用都存在。`_gradle_task_list`(`scripts/lumos:76986`)、`_SR_MODULE_PART`、`_test_name_ok`、`_name_collision_reason` 都在。
  - 不改 `_gradle_test_module` 的理由成立:它只認 `:test` 結尾(`scripts/lumos:77001`)。
  - `_run_cmd_expand` 對 `'*{method}'` 的引號處理與 S1 預期的 `'*aCase'` 一致。
  - 結果資料夾圍欄由 S14 守。
  - 本節沒有獨立的 finding。
- **做法 2:** 有兩條 finding,見上(基準不綠拿掉、中斷)。
- **做法 3:** 有三條 finding,見上(weak、S5、斷路器)。
- **做法 4:**
  - 第一個訊號走同一個處理器,是對的(`scripts/lumos:76614`)。
  - `_KILL_RUN_LIVE` 已登記合併程序,新增的模組層變數是重複登記,不衝突。
  - spec 沒寫 `_kill_run` 怎麼知道這次是合併快篩(多一個參數?)。這是實作細節,併入 finding 1 的介面缺口。
- **做法 5:** 有 finding,見上。`judged`、`merged`、`single`、`merge_tripped` 在 `_GOV_FIELD_TYPES` 與帳檔裡沒有同名欄位的衝突(我查了 `docs/.governance-log.jsonl`,零筆)。
- **做法 6:** 已讀,無 finding。`--max-mutants`、`--max-seconds` 參數在 `scripts/lumos:82114` 起存在,而且沒有上限檢查。
- **落點:** 規格閘 choice-kill 那條 WHY 的「強 killed、編不過、逾時就停」、改動選擇點計劃〈用詞〉殺掉判定、〈實務隱患〉的「同一壞法殺掉就停」都找得到,改法是各補一句,寫得清楚。手冊的兩處(`06-代碼審與推送.md` 的 choice-kill 列與 `lumos-code-loop/SKILL.md`)也存在。已讀,無 finding。
- **預期效益:** 算術核對:
  - 存活 92–137 個、被殺 46–91 個,與 183 個吻合。
  - 3.9 與 6.2 小時各自是極端組合的結果,成立。
  - 掛住 9 個乘以 2.5 至 5 分鐘約等於 0.37 至 0.75 小時,成立。
  - 有一條 finding(呼叫次數),見上。
- **不做、驗收條款、預期值表:**
  - S1 到 S18 在條款與表兩邊編號一一對上。
  - [test:] 名稱 S1 到 S15 共 15 支,現有測試檔裡一支都沒有,只有 `t_choice_guard_kill_new_params` 已存在(S12 擴充)。
  - S16 到 S18 是 `[manual:]`。
  - S4 條款列的七種情形與表上七案一一對得上。
  - 可照字面寫成測試的缺口只有 S5 的「基準帶不確定標記」(見上),以及 S7、S8 取決於上述介面缺口。
- **回退:** 有一條 finding(找不到清單指令)。舊版 lumos 讀帳不認得新欄位就略過,與程式一致:`_choice_ledger_index` 只檢查 `file`、`fp`、`verdict` 三個字串(`scripts/lumos:78061`)。
- **實務隱患:** 風險類逐類:
  - **守衛面:** 漏殺是安全方向,但存活判定會被 `carried` 機制固定,直到守的測試雜湊變動才重跑(`scripts/lumos:78334` 起的 `_choice_kill_pick`)。這是現有行為,不是新問題。spec 說靠 S18 抽查,合理。
  - **資源:** 8MB 與 64MB 上限有寫。
  - **效能:** 有寫,但預期效益表有上述缺口。
  - **回滾:** 有寫。
  - **相容:** 舊帳與舊版讀法無變化。
  - **併發:** 有寫。
- **依據來源、人裁紀錄、審計修正紀錄:** 有殘句,見上(第四筆 c4)。審計修正紀錄 r1 那一段保留了已被拿掉的 `merge_ver` 與 `--recheck`,但明標為 r1,且 r2 一段說明已拿掉,不算殘句。

## 圖譜固定席節點逐條判

- **Systems/guard-kill(★INVARIANT★ rc 優先序、--json 純度):** 不影響。合併只在傳了 `merge` 時走,不傳時行為不變(S12)。`choice-kill` 呼叫時標準輸出被整段收起,`--json` 的 stdout 一行 JSON 不受影響。但「merge 不傳時行為不變」要靠 finding 1 提到的介面補完才能守住。
- **Systems/test-quality-cli:** 不影響。本案只呼叫既有的 `junit()`,不改它。
- **Systems/lumos-cli-lifecycle(re-inject 不動 sentinel 外內容):** 不影響,本案不碰 re-inject。
- **Systems/bound-tests-gate(合約測試閘逐支真跑):** 不影響。它走 `_run_bound_tests`,不走 `cmd_guard_kill` 的新分支。
- **Systems/lumos-cli-read(search 預設排除 superseded):** 不影響,本案不碰搜尋。
- **Systems/pitfalls-code-loop(★RISK★):** 不影響。本案不改 pitfalls 的分級與代碼審流程。
- **Verification/測試品質第四輪修補驗證:** 不影響,本案不改 `junit()` 的拒收規則。
- **Systems/規格閘(落點):** 不影響既有守衛行為。choice-kill 那條 WHY 要補一句,落點寫得清楚。

發現共 13 條
