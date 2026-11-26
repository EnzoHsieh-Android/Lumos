severity: major

以下結論都對照過 `scripts/lumos` 的現況。

**1.** 範圍 2 的準備物件呼叫點。
severity: major
blocking: 是
引句:「guard-kill 在 `_kill_merge_iter` 先量齊基準的同一個位置呼叫它」
- `cmd_guard_kill` 只有 `merge` 不是 None 時才建 `mctx`、才走 `_kill_merge_iter`(`scripts/lumos:28481-28483`);沒給就直接用 `plist`。
- 進了 `_kill_merge_iter`,`_kill_merge_ready` 也有許多條件直接回 None 而不量基準(`scripts/lumos:29028-29060`)。這些條件包括 flaky、`node_dirty`、指令形狀不支援、`指令過長`、`合併道不足 2 支`、`時限不夠`。回 None 時 `yield from c.plist` 後直接 return。
- 照字面實作,以下情況準備物件不會被呼叫,合批編譯檢查與覆蓋整個靜默失效:
  - `choice-kill --no-merge`。
  - 守的測試少於 2 支。
  - 筆記有未提交改動。
  - 時限不夠。
- 範圍 7 只把 `--no-merge` 列為 `--reach-only` 的衝突旗標,一般 run 帶 `--no-merge` 的行為沒寫。S5 的「恰跑一次、壞法階段不再量」也沒有不合併路徑的案例。
- 〈用詞〉寫「對每個平台組呼叫它一次」,與範圍 2 的位置互相矛盾。
- 呼叫點要獨立於合併能不能做。

**2.** `--reach-only` 怎麼走進 guard-kill。
severity: major
blocking: 是
引句:「照常交準備物件、不產配方之外的事:只做覆蓋基準與分析」
- `--reach-only` 沒有壞法,也就沒有配方。`cmd_guard_kill` 的 docstring 寫「零配方/缺 run_cmd/config 壞=2」。
- 「只做覆蓋基準」要在 guard-kill 那棵樹裡做,spec 沒說沒配方時怎麼讓它建樹並呼叫準備物件。
- 它補的是既有存活行的 reach,這些行的壞法要重挑,但沒說重挑後是否要交配方、是否要過合批編譯。
- 「不產配方之外的事」這句本身不通順。
- S11 預期值表只列行為,沒列這條呼叫路徑。

**3.** `cov_sha` 的定義循環,而且讀端算不出來。
severity: major
blocking: 是
引句:「`cov_sha`(str:經過或可能經過這一行的守的測試名與所在檔 blob、壞法所在檔 blob,依名排序後算)」
- 「經過這一行的測試」要靠覆蓋資料才知道,覆蓋資料只在 guard-kill 樹裡實跑覆蓋基準時才有。
- 但下列讀端都要在沒跑覆蓋時算出「現在的 `cov_sha`」:
  - 範圍 6「reach 有效:最新一筆 reach 的 `cov_sha` 等於現在算出的值」。
  - `_choice_kill_pick`(`scripts/lumos:79072`),在 guard-kill 之前決定帶過去或重跑。
  - choice-points。
  - 推送閘的 `_choice_push_read`,讀 B 版。
- 續跑快取只在同一個 `at_sha` 有效,不同提交就沒有覆蓋資料可算。
- S8「`cov_sha` 跟現在不同應印未分類」、S21「`cov_sha` 變了不帶過去」都無法實作。
- 需要改成讀端算得出來的鍵,例如「全部守的測試名與 blob 加壞法所在檔 blob」,或明寫讀端怎麼取得覆蓋。

**4.** 覆蓋基準每換一個 `at_sha` 就全部重跑。
severity: major
blocking: 是
引句:「同一個 `at_sha` 再跑時直接取用,被中斷的 run 下次接著跑」
- 處置第 1、2、3 層本來就要改計劃或測試,必然產生新提交、新 `at_sha`,快取整個失效。
- 〈用詞〉速度段自己估 169 支測試要多約 4 分鐘加 773 秒,每次處置後重量都是約 17 分鐘。
- 預設總時限 `_CHOICE_MAX_SECONDS` 是 1800 秒(`scripts/lumos:78739`)。覆蓋基準就吃掉大半,剩下的時間不足以編譯和跑壞法,測試被判「時間不夠」而算不明,最後退成全跑。
- S18 對照的「2633 秒」也超過預設時限,spec 沒提要帶多大的 `--max-seconds`。
- 這與使用者「不要又變回十幾個小時」衝突。
- 快取鍵已含測試所在檔 blob,但覆蓋還取決於正式碼,所以不能直接沿用 blob。修法是把正式碼變動納進鍵,或明說每次重量並把時限與預期值改寫。

**5.** `--no-cov`、`--cov-audit` 沒有定義。
severity: major
blocking: 是
引句:「跟 `--no-cov`、`--only`、`--max-mutants`、`--no-merge` 同給時 rc2」
- 現有 `choice-kill` 旗標只有 `--only`、`--max-mutants`、`--max-seconds`、`--no-merge`(`scripts/lumos:82898-82901`)。
- `--no-cov`、`--cov-audit N` 只在範圍 5、7、S21、回退裡被提到,沒有任何一節把它們列為新旗標,也沒寫語意。
- 缺的內容包括 argparse 定義、`cmd_choice_kill` 簽名、`--no-cov` 對 run 事件 `cov` 的值(`off`?)、說明表。
- 回退第 1 條與 S21 都依賴它。

**6.** init script 的內容沒交代,和「不改使用者 Gradle 設定」並存。
severity: major
blocking: 是
引句:「不自動改使用者專案的 Gradle 設定檔(只靠每次呼叫的 init script)」
- 實務隱患的 PITFALL 寫「AGP 在開 enableUnitTestCoverage 後才套 jacoco 外掛」。spec 全文沒有任何一處說 init script 要替專案打開 `enableUnitTestCoverage`,只提 includeNoLocationClasses 與分析任務。
- 覆蓋資料檔的位置由 AGP 決定,而且「`<變體>UnitTest`」。多模組、多變體時要複製哪一份、哪個模組,沒說。
- 預設 `compile_cmd` 的 `./gradlew :<模組>:compileDebugUnitTestKotlin` 也有同樣的缺口。
  - `<模組>` 怎麼從壞法所在檔或 `run_cmd` 推出來,沒寫。
  - 一批壞法跨模組時要不要多次編譯,沒寫。
  - 專案用別的變體或 flavor 時編譯對象就錯了。
- 這些都是照字面做不出來的部分。

**7.** `_choice_push_judge` 拆子原因的接點。
severity: minor
blocking: 否
引句:「擋不擋、回報上限、放行鍵不變」
- `by["存活"]` 是被 `_choice_cap_pick` 抽中的行(`scripts/lumos:79591`),`_CHOICE_PUSH_REASONS` 同時決定列印順序與 `blocked` 事件的 `reasons`(`scripts/lumos:79778-79786`)。
- 子原因名稱換掉後,「同一個 B 同一組原因不重記」的去重鍵會改變,舊帳的 `reasons: [["存活", n]]` 與新帳不再對得上。這點 spec 沒寫。
- `_choice_push_judge` 要多收 aux 參數,簽名跟 `site="pass"` 預判的呼叫端要一起改。這點只在範圍 6 一句帶過,沒列出呼叫端。

**8.** gov「第一次判定」在 `via: "cov"` 之後少算。
severity: minor
blocking: 否
引句:「照現在數 `attempt == 1 and via == "run"`」
- 某行第一次是 `none` 記 `via: "cov"`、`attempt` 1。之後帶過去規則讓它重跑時,`attempt` 變 2、`via` 是 `run`。
- 這一行永遠不進「第一次判定」,gov 的存活率分母因此漏掉它。這個分母是為論文式的首次判定統計設的。

**9.** 抽查與 `none` 事件的寫入順序。
severity: minor
blocking: 否
引句:「殺掉了就記 `cov-audit` 事件 `killed: true`、那一行改用殺掉的結果記壞法事件」
- 範圍 3 說 `none` 的行 choice-kill 直接記存活事件,範圍 5 說抽到的行跑全部測試後再改記。兩者的先後沒定。
- 斷路後「其餘 `none` 改成照跑」,但其餘 `none` 若已先寫了 `via: "cov"` 的存活事件,同一個 run 內同一行就有兩筆終態,`attempt` 計數也會錯。
- 「隨機抽」也讓 S19 的測試無法重現。要說明用 `run_id` 做種子,還是測試怎麼固定。

**10.** 準備物件換掉整行(`exhausted`)時 run 事件的計數。
severity: minor
blocking: 否
引句:「那一行在挑壞法時狀態是 `exhausted`(跟乾節點 `arid` 同一層級的行狀態,不是處置判定),不擋、不跑」
- `exhausted` 是在合批編譯檢查之後、於 guard-kill 內才發現的。
- 前面 choice-kill 已把這行算進 `todo`、`mutant_lines`、`ran`、「還有 N 個沒跑」的提示(`scripts/lumos:79349`)。
- 這種行該算在哪個計數沒寫。`--max-mutants` 的名額會被它佔掉,卻沒有任何判定事件。

**各節簡述**
- 〈白話〉:已讀,除以上與覆蓋基準有關的各點外,無 finding。
- 〈舊否決比對〉:已讀,無 finding。與 guard-kill 筆記的「不抽共用函式」一致;`cmd_guard_kill` 其他呼叫端是 `scripts/lumos:27703`、`scripts/lumos:77396`、`scripts/lumos:84388`,都不傳 `prep` 就不變。
- 〈回退〉:已讀,無 finding。第 2 條說 `exhausted` 要重新挑得 `lint-waive`,但 `exhausted` 本來不擋,這句與前文自相矛盾,只是文件精度(minor)。
- 〈實務隱患〉:已讀,無 finding。逐類答覆:併發、金流、對外送出、不可逆都標已排除且理由成立。守衛面已標「不排除」。
- 治理帳與 gov 讀端:已讀,無 finding。
  - `_GOV_FIELD_TYPES` 已有 `file/fp/new_sha/run_id/row/killing_test/judged`。
  - `_choice_ledger_index` 只收 gate 與 kind 都是 choice-kill,新 kind 不會混進去(`scripts/lumos:78787`)。
  - `_BOOKKEEPING_DIRS` 加一個目錄符合先例(`scripts/lumos:41617`)。
  - `_gate_event_fit` 簽名可用(`scripts/lumos:1884`)。
- `lint-waive choice:`、`situation-rule --plan/--clause/--point`、`_kt_sit_quote_norm`:都確認存在,無 finding。
- 圖譜鏡頭 `Systems/guard-kill`、`Systems/規格閘`:不影響 `rc` 優先序與 `--json` 純淨兩條合約。`prep` 沒傳時行為不變。

總結:最高等級是 major,blocking 共 6 條
