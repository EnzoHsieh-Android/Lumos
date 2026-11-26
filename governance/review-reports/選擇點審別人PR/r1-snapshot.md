---
type: project
status: todo
created: 2026-11-26
updated: 2026-11-26
tags:
  - type/project
  - status/todo
  - scope/guards-gates
lands_in:
  - Systems/guard-kill
related:
  - "[[Projects/改動選擇點都要有需求守住_計劃]]"
  - "[[Projects/選擇點變異加速第四段_計劃]]"
  - "[[Projects/選擇點變異加速_計劃]]"
---
# 選擇點審別人PR_計劃

## 白話

現在的選擇點變異(`lumos choice-kill`)只審自己的分支:改到的每一行找一個「換個寫法照樣編得過、行為卻不同」的壞法,跑這次碰到的計劃綁的測試,沒被抓到的(存活)回指到計劃條款,問作者「規格沒寫、測試太弱,還是無所謂」。

這份要讓它也能審**別人發的 PR**,包括沒裝 lumos 的 repo。別人的 PR 通常沒有我們的計劃、可能也沒有知識圖譜與 lumos 設定,所以換三件事:

1. **跑哪些測試**:照順序找——PR 碰到的計劃綁的測試(對方也用 lumos 時)、PR 自己改到或新增的測試、改到的正式碼所在模組的全部測試類別。
2. **怎麼判**:每個壞法只跑**一次合併呼叫**(把選到的測試合成一次 Gradle 呼叫):有任何一支失敗就算「被抓到」,全部通過就是存活。不量每支的單支基準、不追是哪支殺的——審別人只報存活點,用不到是哪支殺的。
3. **存活回指到哪裡**:照順序找——對方 repo 既有筆記的合約與規則(有圖譜時)、PR 描述與連結的 issue;都對不到就寫成一題留給作者的審查問題(「第 42 行 `>=` 改成 `>` 測試全綠,這個邊界是刻意的嗎?」)。

好比幫別人校稿:自己的稿子有大綱可以對;別人的稿子沒大綱,就對照出版社的體例、再對照作者附的說明,都對不到的就在頁邊打一個問號。

這份要回答的實驗問題跟主實驗同一個:語法樹變異的回指,能不能把「AI 沒做、或隨意決定」攔下來——只是對象從自審換成審別人。

## 已定的(使用者 2026-11-26 裁)

- D1 入口:`lumos choice-review <PR 編號>`(GitHub PR;輸入只收編號,不收分支名);只讀不寫對方分支,不推、不提交。
- D2 執行對方程式碼:同 repo PR(`isCrossRepository` 為 false)照常跑;fork PR 預設只出靜態選擇點清單、不跑測試,帶 `--trust` 才跑。
- D3 帳:不寫、不讀任何治理帳與殺傷力帳(被審 repo 的、使用者 repo 的都一樣);結果只進報告。
- D4 對外留言:預設不留言,只出本機報告;`--comment` 才用 `gh pr comment` 貼一則整份報告。
- D5 範圍:連沒裝 lumos 的 repo 也要能跑;對方 PR 頭提交沒有 `.lumos/config.json` 時,用 `--run-cmd` 臨時指定測試指令(要帶 `{method}`),沒給就只出靜態清單。第一版只支援 Gradle 的 JVM 單元測試(Kotlin、Java;JUnit 的 `@Test`)。
- D6 判法:審別人時每個壞法只跑一次合併呼叫,有失敗就算被抓到、全通過算存活,不量單支基準、不歸因到哪一支(這碰到一筆舊否決,見〈舊否決比對〉)。
- D7 做法:選擇點的掃描與挑壞法那段(`choice-points` 已經讀 git 樹、可帶 `--repo`)加參數接受「哪個 repo、哪個提交」;判定另寫一支小執行器,重用合併快篩的套壞法、組合併指令、跑、判讀、還原那幾支函式;不經 `cmd_guard_kill` 與 `_ChoiceKillRun`(那兩支會讀寫帳、量單支基準)。

WHY:審別人的 PR 時,測試來源照「碰到的計劃 → PR 改到的測試 → 改到模組的全部測試類別」順序找,存活回指照「對方 repo 的合約與規則 → PR 描述與 issue → 寫成問題」順序找 [出處:使用者 2026-11-26 問「能不能針對別人發的 PR 做一遍 Review,但這樣會沒有他那邊的規格可以回指」,並裁連沒裝 lumos 的 repo 也要能跑] [因:別人的 PR 沒有我們的計劃,choice-kill 碰不到計劃就整個不跑] [不選:只做靜態清單不跑測試(看不出測試守不守得住,失去主要價值);要求對方先寫計劃(別人的 PR 做不到)] [代價:回指不到條款時只能出問題,判斷交回作者] [test:t_choice_review_test_source_ladder]
WHY:審別人時每個壞法只跑一次合併呼叫,有失敗算被抓到、全通過算存活,不量單支基準、不歸因 [出處:使用者 2026-11-26 裁「審別人時可以」;設計前掃量到模組 200 支測試光量單支基準就要約 3000 秒] [因:審別人只報存活點,「是哪支殺的」用不到;單支基準是 N 次 Gradle 呼叫] [不選:照自審的跑法(大模組很慢、要設支數上限);合併判殺掉也進自審(自審要回指條款,舊否決照舊)] [代價:報告不寫是哪支測試抓到的;合併裡有測試之間互相影響時,判定可能跟逐支不同] [test:t_choice_review_merged_judge]
WHY:fork 來的 PR 預設不執行測試,要 `--trust` 才跑 [出處:PIT 維護者說 PR 留言外掛不適合 fork 來的 PR(可能是惡意來源),GitHub 對 fork PR 只給最小權限的權杖] [因:變異測試要跑 PR 的測試,等於執行別人的程式] [不選:一律跑(本機會執行不可信程式碼);一律不跑(同 repo 的同事 PR 也失去價值)] [代價:同 repo PR 不設防,帳號被盜的同事 PR 會照跑(見〈實務隱患〉)] [test:t_choice_review_fork_static_only]

PRIOR-ART: ①Google 的差異式變異測試只變異改到的行,把存活的壞法當成自動審查意見顯示在作者與審查者的審查畫面,審查者可一鍵標「沒幫助」(https://arxiv.org/pdf/2102.11378);後續研究統計存活壞法有 38% 被改程式或補測試解決(https://research.google/pubs/please-fix-this-mutant-how-do-developers-resolve-mutants-surfaced-during-code-review/)。採用「存活就是一則審查意見」與「每行最多一個壞法」(本工具已照它做)。②PIT 的 GitHub 外掛把存活壞法貼成 PR 留言與行內註記,但維護者寫明不適合 fork 來的 PR,後來改成兩段工作流程(分析不帶寫入權、另一段再留言)(https://blog.pitest.org/dont-let-your-code-dry 、https://blog.pitest.org/oss-pitest-pr)。採用「fork 預設不跑」與「留言要另外明講」。
RETIRE-IF: 上線後累計審 20 個 PR,存活點變成作者改程式或補測試的比例低於 10%(Google 的 38% 的四分之一)→ 審別人 PR 的存活點多半是雜訊,撤掉 `choice-review`,只留自審。
REVISIT:2027-01-31 數 choice-review 審過的 PR 數與存活點的去向,照 RETIRE-IF 判。

## 舊否決比對

- [[Projects/選擇點變異加速_計劃]] 與第二段:「合併直接判殺掉」被否決(第一版設計審兩輪 24 條卡在歸因與作廢,使用者 2026-11-23 否決)。否決的理由是自審要知道「哪支測試守著哪條條款」。審別人只報存活點、不回指條款到測試,理由不成立;使用者 2026-11-26 裁「審別人時可以」。自審的 choice-kill 照舊不變。

## 用詞

- **壞法、存活、選擇點、合併快篩**:沿用 [[Projects/改動選擇點都要有需求守住_計劃]] 與 [[Projects/選擇點變異加速_計劃]]〈用詞〉。
- **被抓到**:這個壞法的合併呼叫結果檔裡至少一支 failure 或 error。
- **同 repo PR**:`gh pr view --json isCrossRepository` 回 false。其餘是 fork PR。
- **PR 頭提交、基底提交**:`gh pr view --json headRefOid,baseRefOid`;範圍是 `merge-base(基底, 頭)..頭`。
- **審查樹**:用 `_isolated_worktree` 在使用者 repo 建、檢出 PR 頭提交的隔離工作樹;所有套壞法、跑測試都在這棵樹裡。
- **模組**:Gradle 子專案,判法同既有 `_gradle_module_parts`:正式碼路徑 `<模組目錄>/src/main/...` 的 `<模組目錄>`;模組的測試是 `<模組目錄>/src/test/` 底下的檔(不含 `src/androidTest/`)。
- **測試類別**:測試檔裡宣告了至少一個 `@Test`(照既有 `KOTLIN_TEST_RE`;Java 加一條同形的 `@Test … void <名>(` 規則)的類別,完整名是套件名加類別名。
- **測試來源階梯**:做法 3 的三層;取第一層有測試的,報告寫明用的是哪一層。
- **回指**:報告裡每個存活點附的「這個選擇點該對照哪一句」:回指層(合約、PR 描述、問題)與那一句的原文。
- **回指階梯**:做法 5 的三層;每個存活點取第一層對得到的。

## 做法

1. **取 PR**:`gh pr view <編號> --json headRefOid,baseRefOid,isCrossRepository,title,body,closingIssuesReferences,url`;`git fetch <remote> pull/<編號>/head`(remote 取使用者 repo 裡 URL 指向這個 GitHub repo 的那個);拿不到(非 GitHub、權限)就停、印原因。建審查樹,收尾整個刪。
2. **測試指令**:審查樹裡有 `.lumos/config.json` 而且有 kotlin-junit 平台 → 用它的 `run_cmd`;否則用 `--run-cmd`;都沒有 → 只出靜態清單(報告開頭寫「沒有測試指令,只做靜態清單」)。`run_cmd` 要過既有 `_choice_merge_shape`(恰好一個 `{method}`、接在 `--tests` 後、恰好一個 Gradle 單元測試任務),不過就只出靜態清單並寫原因。
3. **測試來源階梯**:①審查樹有知識圖譜而且範圍碰到進行中計劃 → 計劃綁的測試(既有 `_choice_spec_calc`,碰不到或算不出來都當這層沒有、不中止);②PR 改到或新增的測試檔裡的測試方法(`git show <頭提交>:<檔>` 的文字套測試名規則);③改到的正式碼所在模組的全部測試類別(每個類別一段 `--tests '<類別完整名>'`)。組出的合併指令超過既有長度上限 → 照類別名排序截到上限內,報告列出沒涵蓋的類別。
4. **判定**(新的小執行器 `_review_judge`):
   - 先在乾淨的審查樹跑一次合併基準:結果不是「通過」→ 從結果檔挑出失敗的測試拿掉再跑一次;還不通過 → 停、報告寫「基準就不過,判不了」。
   - 掃描:既有 `_choice_changed`、`_choice_compute` 加 `repo`、`at_sha` 參數,讀審查樹的 git 物件(不讀工作目錄、不要求 HEAD、不要求乾淨)。
   - 每個壞法:既有 `_kill_merge_apply` 套 → `_kill_run` 跑(上限照合併快篩 `_choice_merge_screen_cap`)→ `_choice_merge_classify` 判 → `_kill_merge_restore` 還原。通過 → 存活;有失敗 → 被抓到;編不過 → 編不過;沒跑乾淨(逾時等)→ 跑不出結果,事件行看得出掛住的那支就寫進報告。
   - 挑壞法照既有順序,`--max-mutants`(預設 30)、`--max-seconds`(預設 1800)夾住;時限到了停在壞法之間。
   - 不呼叫 `cmd_guard_kill`、`_ChoiceKillRun`、`_choice_record`、`_choice_gate_event`;不讀 `_choice_kill_ledger`。
5. **回指階梯**:①審查樹有知識圖譜 → 讀節點內文,取 ★INVARIANT★ 合約行(既有 `INVARIANT_RE`)與摘要裡的 `RULE:` 行(既有 `_slot_summary_entries` 取摘要條目的那套),行內反引號路徑或節點 `about_code` 含存活點所在檔的 → 回指那一行;②PR 描述與連結 issue 的內文裡,存活點所在檔名或所在函式名(掃描時已知)字面出現的那一句 → 回指那一句,寫「字面對到、語意待人判」;③都對不到 → 寫成問題:哪一行、從什麼改成什麼、測試全綠,問「刻意的嗎?是就補測試,不是就是隨手決定」。
6. **報告**:Markdown,寫到 `--out`(預設系統暫存資料夾、印出路徑)。開頭:PR、範圍、是否執行測試與原因、測試來源層、測試指令來源(設定檔或 `--run-cmd`)、跑了幾個壞法、時限有沒有用完、沒涵蓋的測試類別。每個存活點一段:檔、行、壞法(原文→改法)、回指層與原文、問題。被抓到、編不過、跑不出結果只列數量與清單(不展開)。`--comment` 時用 `gh pr comment <編號> --body-file <報告>` 貼一則。

## 落點

- [[Systems/guard-kill]]:新增 `choice-review` 指令、`_review_judge` 執行器、掃描兩支函式加 `repo`/`at_sha` 參數。

## 不做

- 不做行內註記(PR review API 的逐行留言):先看一則整份留言有沒有用。
- 不在 CI 裡自動跑:先人手跑、量雜訊比。
- 不替對方寫計劃或補測試。
- 不改自審的 choice-kill:判法、帳、單支基準都照舊。
- 不用測試地圖(`testmap affected`):地圖是本機檔、審查樹裡沒有,而且輸出是測試檔不是方法;之後有需要再加一層。
- 不支援 Gradle 以外的測試框架:第一版先做 JVM 單元測試。

## 驗收條款

- [S1] 當 PR 是同 repo PR、審查樹沒有圖譜、改到 1 個正式碼檔與 1 個測試檔、帶 `--run-cmd` 時,choice-review 應 用 PR 改到的測試檔裡的測試(第二層),報告開頭 應 寫「測試來源:PR 改到的測試」與「測試指令:--run-cmd」;沒改到測試檔時 應 用那個模組的全部測試類別(第三層) [test:t_choice_review_test_source_ladder]
- [S2] 當 PR 是 fork PR、沒帶 `--trust` 時,choice-review 應 只出選擇點清單、不跑任何測試、報告開頭 應 寫「fork PR,沒帶 --trust,只做靜態清單」;帶 `--trust` 時 應 照常跑 [test:t_choice_review_fork_static_only]
- [S3] 當壞法的合併呼叫全部通過時 應 判存活、列進報告;有一支失敗時 應 判被抓到、只計數;基準在乾淨樹上就有一支失敗時 應 拿掉那支重跑基準,兩次都不過 應 停、寫「基準就不過,判不了」 [test:t_choice_review_merged_judge]
- [S4] 當存活點所在檔出現在某個 ★INVARIANT★ 合約行的反引號路徑裡時,報告那一段 應 回指那一行;只在 PR 描述裡字面對到檔名時 應 回指那一句並寫「語意待人判」;都對不到時 應 寫成問題 [test:t_choice_review_backref_ladder]
- [S5] 當沒帶 `--comment` 時,choice-review 應 不呼叫任何對外寫入(`gh pr comment`);帶了 應 只貼一則留言 [test:t_choice_review_comment_opt_in]
- [S6] 當跑完時,使用者 repo 的治理帳、殺傷力帳、工作目錄檔案與目前分支 應 都沒變,審查樹 應 已刪 [test:t_choice_review_no_writes]
- [S7] 當審查樹沒有 `.lumos/config.json`、也沒帶 `--run-cmd` 時,choice-review 應 只出靜態清單並寫「沒有測試指令」;`--run-cmd` 不帶 `{method}` 時 應 只出靜態清單並寫原因 [test:t_choice_review_no_config]
- [S8] 當在實驗專案找一個真的 PR 跑時,存活點數、回指各層分布與花費時間 應 記下來 [manual:在 Android 實驗專案開一個小 PR,跑 lumos choice-review,寫進驗證紀錄]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 同 repo PR、沒圖譜、改 1 正式碼 1 測試檔、帶 --run-cmd;另案沒改測試檔 | 一:用第二層、報告寫來源與指令;二:用第三層 | 本計劃第一條 WHY;D5 |
| S2 | fork PR 不帶 --trust;另案帶 | 一:只出清單、不跑測試;二:照常跑 | 本計劃第三條 WHY;PIT fork 限制 |
| S3 | 合併全過;另案一支失敗;另案基準一支失敗;另案基準兩次都不過 | 一:存活;二:被抓到;三:拿掉重跑;四:停、寫判不了 | 本計劃第二條 WHY;D6 |
| S4 | 存活點在合約行反引號路徑;另案只在描述字面對到;另案都對不到 | 一:回指合約行;二:回指描述那句、寫語意待人判;三:寫成問題 | 本計劃第一條 WHY |
| S5 | 不帶 --comment;另案帶 | 一:沒有對外寫入;二:一則留言 | 本計劃 D4(使用者裁照預設) |
| S6 | 跑完 | 兩本帳、工作目錄、分支沒變,審查樹已刪 | 本計劃 D3(使用者裁照預設) |
| S7 | 沒設定沒 --run-cmd;另案 --run-cmd 沒 {method} | 只出靜態清單、寫原因 | 本計劃 D5(使用者裁連沒裝的也要能跑) |
| S8 | 實驗專案真 PR | 記存活數、回指分布、時間 | 本計劃〈白話〉實驗問題 |

## 回退

- 先關不還原:不叫 `choice-review` 就沒有影響;它不寫帳,自審的 choice-kill 不變。
- 還原功能提交即可,沒有資料要遷移;掃描兩支函式新加的參數預設值等於現在的行為。

## 實務隱患

- 執行對方程式碼:同 repo PR 不設防,帳號被盜的同事 PR 會照跑;fork PR 要 `--trust`。報告開頭印出這次有沒有執行測試、為什麼。
- 合併判法的盲點:測試之間互相影響時(前一支改了共用狀態),合併的結果可能跟逐支不同;審別人只用來挑存活點,報告寫明「合併判定」。
- 基準不過:對方 PR 本身就有紅的測試時,拿掉失敗那支重跑一次;還不過就停。
- 大模組:第三層每個測試類別一段,超過指令長度上限就截斷並列出沒涵蓋的類別;受 `--max-seconds` 夾住。
- 回指第二層只做字面對照:檔名或函式名出現在描述裡不代表描述在講這個邊界,報告一律寫「語意待人判」。
- `.git` 會變:建審查樹在使用者 repo 的 `.git/worktrees` 登記一筆、`git fetch` 會寫物件;收尾 `worktree remove`、物件留著(正常的 fetch 行為)。S6 只比帳、工作目錄檔案與目前分支。
- 已排除:金流:只在本機跑測試
- 已排除:對外送出:預設不送;`--comment` 是使用者明講才送,只貼一則留言
- 已排除:不可逆:不寫任何帳、不改分支,審查樹收尾刪掉
- 已排除:守衛面:不改任何推送前的閘,也不改自審的 choice-kill

## 依據來源

| 機制 | 依據 | 出處 |
|---|---|---|
| 存活壞法當審查意見 | Google 差異式變異測試 | https://arxiv.org/pdf/2102.11378 、https://research.google/pubs/please-fix-this-mutant-how-do-developers-resolve-mutants-surfaced-during-code-review/ |
| fork PR 不預設執行、留言另明講 | PIT GitHub 外掛的限制與兩段工作流程 | https://blog.pitest.org/dont-let-your-code-dry 、https://blog.pitest.org/oss-pitest-pr |
| 同 repo 判斷用 isCrossRepository | gh pr view 可用欄位(前掃實測 baseRepository 不存在) | 實測 2026-11-26:`gh pr view --json baseRepository` 回 Unknown JSON field |

## 人裁紀錄

- 使用者 2026-11-26:「有個需求，這個選擇點review，能不能多個功能，是針對別人發的PR做一遍Review？ 但這樣會沒有他那邊的規格可以回指，對嗎？」;看完分析後:「起草設計」;三個預設(fork 預設只做靜態清單、不寫帳、預設不留言):「照預設」;「工具的pr選擇點是不是可以先做」。
- 使用者 2026-11-26(前掃後):範圍「連沒裝的也要能跑」;判法「審別人時可以」(每個壞法只跑一次合併、不歸因);做法「給核心加參數」。

## 審計修正紀錄
