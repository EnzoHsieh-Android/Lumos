severity: major

我只讀 `scripts/lumos`、`guard-kill.md` 和被審材料,沒跑任何指令。因為審查席的 Bash 擋「gh」這個字,既有 gh 呼叫的寫法是用 `_ci_` 前綴的 helper 名去找的。

## 1. 分層與依賴方向

既有分工是三層。掃描與挑壞法在 `_choice_compute`、`cmd_choice_points`,挑壞法的 CLI 掛在 argparse 的 `choice-points`(file: `scripts/lumos:78563`、`scripts/lumos:78655`、`scripts/lumos:82858`)。批次與記帳由 `cmd_choice_kill` 負責,它把判定交給 `_ChoiceKillRun`,再經 `cmd_guard_kill` 執行(file: `scripts/lumos:79346`)。判定與還原是 `cmd_guard_kill` 內部那一組 `_kill_merge_*`(file: `scripts/lumos:29202`)。

新計劃讓 `_review_judge` 繞過 `cmd_guard_kill`,直接呼叫 `_kill_merge_apply`、`_kill_merge_restore` 等內部函式。這有兩個對不齊的地方:

- **`guard-kill` 的家寫明它是唯一判法。** `responsibility` 寫「也是人裁(situation-rule)與改動選擇點(choice-kill)臨時配方的唯一判法(它們只用選用參數接上)」。第 49 行的 WHY 還有一條既有否決「不選:另抽一支共用的殺傷力函式」。自審與人裁的做法是加選用參數接上 `cmd_guard_kill`,而不是另寫執行器。計劃〈舊否決比對〉只比對了「合併直接判殺掉」那一筆,沒比對這條。
- **那幾個 `_kill_merge_*` 函式吃的 `c` 是 `cmd_guard_kill` 內部組出來的現場。** 它是 `types.SimpleNamespace`,有 `plat`、`pentry`、`run_dir`、`wt`、`wt_real`、`baselines`、`mstate`、`hk`、`results`、`override` 等約 20 個欄位(file: `scripts/lumos:28479`)。`_kill_merge_apply` 會讀 `c.baselines[...][4]`、`c.mstate`、`c.override`;`_kill_merge_restore` 失敗時會寫 `c.results`(file: `scripts/lumos:29202`、`scripts/lumos:29086`)。計劃說「不量單支基準」,卻沒說這個 `c` 由誰、怎麼組。只能偽造一份,或把函式抽出來改簽名,兩條路計劃都沒寫。

另外,`_choice_kill_base` 要求範圍右端是 HEAD 且工作目錄乾淨(file: `scripts/lumos:79087`)。審別人時不要求,這是 D3、D7 明講的刻意差異,不算不對齊。

## 2. 命名與錯誤處理

- **指令名**:`choice-review` 跟 `choice-points`、`choice-kill` 同族,沒問題。
- **旗標**:`--max-mutants`、`--max-seconds` 沿用既有名稱與預設值(file: `scripts/lumos:82880`)。`--out` 在 argparse 裡已有先例,`dest` 用 `<縮寫>_out`(file: `scripts/lumos:83151`)。`--run-cmd`、`--trust`、`--comment` 在 `scripts/lumos` 裡找不到同名旗標,是新詞但不衝突。
- **輸入形式**:既有選擇點指令用 `--diff`、`--branch` 給範圍,新指令是位置參數 PR 編號。這是 D1 已定的,不列為不對齊。
- **錯誤處理**:計劃沒寫退出碼約定,既有的約定如下。
  - `cmd_choice_kill` 是 0 全部有效處置、1 有存活、2 跑不出結果或前置檢查不過。
  - `choice-points` 另用 3 表示 ast-grep 不在、沒檢查到。
  - 錯誤訊息走 `_situation_rule_say` 或 `print(..., file=sys.stderr)`,並過 `_kill_esc` 清字(file: `scripts/lumos:78655`)。
- **報告格式**:`choice-points` 與 `choice-kill` 都把人讀輸出印在 stdout,沒有寫檔先例。`--out` 的 Markdown 報告檔是新形式,計劃只說預設放系統暫存資料夾。暫存目錄用 `tempfile.mkdtemp` 是專案慣例(file: `scripts/lumos:28113`),這點對齊。

## 3. 第二種做法

- **測試名掃描(第二套)**:計劃說「Java 加一條同形的 `@Test … void <名>(` 規則」。但 `JAVA_TEST_RE` 早已存在,而且平台表 `method_re` 已經把 `.java` 對到它(file: `scripts/lumos:6081`、`scripts/lumos:6232`、`scripts/lumos:6242`)。`KOTLIN_TEST_RE` 同在 6067 行。再加一條規則就是第二套測試名掃描,而且已有的那條經過多輪審查加上了長度上限與括號感知。
- **呼叫 gh**:既有 helper 是 `_ci_gh(repo_root, args, timeout=60)`。它回 `(rc, stdout, err)`,gh 不存在時回「gh 未安裝」,其他呼叫端都用它(file: `scripts/lumos:67828`,呼叫在 `scripts/lumos:67852`、`scripts/lumos:67870`、`scripts/lumos:67887`)。計劃寫的是直接下 `gh pr view` 與 `gh pr comment`,沒說用 `_ci_gh`。照字面做會多一種 gh 呼叫寫法。
- **選 remote**:計劃自訂「URL 指向這個 GitHub repo 的那個 remote」。既有 `_lens_default_remote` 是用上游設定、`origin`、唯一遠端的順序選(file: `scripts/lumos:70680`)。這可能是第二種選法,計劃沒說明為什麼不沿用。
- **碰到的計劃與守的測試**:階梯第一層寫「既有 `_choice_spec_calc`」,但它只算「碰到的計劃」。「守的測試」是 `_choice_guard` 算的(file: `scripts/lumos:78858`、`scripts/lumos:78875`)。計劃沒點到 `_choice_guard`,第一層實際怎麼取測試不清楚。
- **合併判法與自審並存**:分工寫得清楚。〈白話〉、D6、第二條 WHY 與〈舊否決比對〉都說「審別人只報存活點,自審照舊」。口徑差別是,自審的合併快篩一旦失敗就交回逐支流程(`_kill_merge_screen` 回 "single",file: `scripts/lumos:29294`),審別人則直接判「被抓到」。這是有意的第二種判法,而且已寫明,所以不單獨列為不對齊。唯一漏的是第 1 問提到的「唯一判法」那條。

## 4. 落點

`lands_in` 只列 `Systems/guard-kill`,有兩處不合。

- **`guard-kill` 責任範圍明寫「不負責:挑哪些行產生壞法(規格閘的選擇點那段)」。** 新指令負責取 PR、掃描、挑壞法、測試來源階梯、回指階梯和報告,其中大部分不是殺傷力判定。
- **三份相關選擇點計劃的 `lands_in` 都是 `規格閘` 加 `guard-kill`(`改動選擇點都要有需求守住` 還加 `kotlin規則包`)。** 本計劃只列一篇,跟鄰居不一致。

建議 `lands_in` 補 `Systems/規格閘`,或為 `choice-review` 另開一篇 Systems 節點。判定執行器歸 `guard-kill`,指令與階梯與報告歸新篇或 `規格閘`。

## Findings

severity: major
blocking: 是
引句:判定另寫一支小執行器,重用合併快篩的套壞法、組合併指令、跑、判讀、還原那幾支函式
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:8`、`docs/lumos-toolchain-knowledge/Systems/guard-kill.md:49`。新執行器另起一條判定路徑,與「唯一判法」和「不選:另抽一支共用的殺傷力函式」衝突,〈舊否決比對〉也沒列這筆。

severity: major
blocking: 是 ⚠(判不準算跨層直呼還是合理重用,交編排者)
引句:每個壞法:既有 `_kill_merge_apply` 套 → `_kill_run` 跑
file: `scripts/lumos:28479`、`scripts/lumos:29202`。這些函式吃 `cmd_guard_kill` 內部組的 `c`(含 `baselines`、`mstate`、`results`),計劃沒說 `_review_judge` 怎麼取得或抽出它,而且「不量單支基準」與 `_kill_merge_apply` 讀 `c.baselines` 相衝。

severity: major
blocking: 是
引句:Java 加一條同形的 `@Test … void <名>(` 規則
file: `scripts/lumos:6081`(`JAVA_TEST_RE`)、`scripts/lumos:6242`(`.java` 的 `method_re`)。已有 Java 測試名規則,另加一條是第二套測試名掃描。

severity: minor
blocking: 否
引句:`gh pr view <編號> --json headRefOid,baseRefOid,isCrossRepository,title,body,closingIssuesReferences,url`
file: `scripts/lumos:67828`(`_ci_gh`)、`scripts/lumos:70680`(`_lens_default_remote`)。對 GitHub 的呼叫與 remote 選擇沒說沿用既有 helper。

severity: minor
blocking: 否
引句:掃描:既有 `_choice_changed`、`_choice_compute` 加 `repo`、`at_sha` 參數,讀審查樹的 git 物件
file: `scripts/lumos:77926`、`scripts/lumos:78563`、`scripts/lumos:78655`。這兩支與 `cmd_choice_points` 已經有 `repo_root`/`repo`、`at_sha`,計劃所說「要加參數」與現況對不上。`_choice_changed` 還只收 `.kt`,但 D5 說支援 Java,計劃沒說 Java 的掃描怎麼做。

severity: minor
blocking: 否 ⚠(計劃屬規格層,對齊面輕,交編排者)
引句:**報告**:Markdown,寫到 `--out`(預設系統暫存資料夾、印出路徑)
file: `scripts/lumos:78655`、`scripts/lumos:79346`。既有選擇點指令把人讀輸出印 stdout,也有退出碼約定(0/1/2、3 表示沒檢查到);計劃沒寫退出碼約定,報告檔的形式在選擇點這一帶是首例。

severity: minor
blocking: 否
引句:新增 `choice-review` 指令、`_review_judge` 執行器、掃描兩支函式加 `repo`/`at_sha` 參數
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:8`(責任範圍「不負責:挑哪些行產生壞法」)、`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:10`(`lands_in` 為規格閘加 guard-kill)。落點只列一篇,與鄰居計劃不一致,指令主體超出 `guard-kill` 的負責範圍。

不對齊共 7 條,其中 major 3 條
