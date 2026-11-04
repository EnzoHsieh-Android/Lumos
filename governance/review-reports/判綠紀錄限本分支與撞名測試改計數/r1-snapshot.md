---
type: project
status: doing
created: 2026-11-03
updated: 2026-11-03
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/規格閘
  - Systems/test-guard
related:
  - "[[Projects/紅燈版實跑三缺口_計劃]]"
  - "[[Projects/規格閘紅燈測試快照_計劃]]"
---
# 判綠紀錄限本分支與撞名測試改計數_計劃

> 白話:紅燈版實跑三缺口(PR #154)合併後回 mOrangePos 考場做平板實機驗收,又抓到一個問題:治理帳被 git 忽略時,別條分支留下的「判綠」紀錄會漏到新分支,新分支一個紅燈版都存不到、不出聲。順手收掉三件小事:主線 CI 連兩次紅的那支效能測試、代碼審 r5 放行時寫進回頭條件的三引號常值斷言與兩處註解、考場的 lumos 版本。

## 名詞

- 紅燈版:規格閘判出紅的那一刻,把那支 Kotlin/Java 測試檔整份存下;推送前比對拿它當新測試的改動前版本,抓「把預期值改成實作輸出」這類作弊。
- 判綠紀錄:規格閘判出綠的測試記一筆(spec-gate-green 事件),之後同一支測試再判紅也不存紅燈版(判綠過的不算實作前的版本)。
- 治理帳:docs/.governance-log.jsonl,規格閘留痕與判綠紀錄都寫在這裡;設計上要進版控,mOrangePos 從 2026-06 起把它設成 git 忽略。
- 祖先:git 歷史上,從目前 HEAD 往回走得到的提交。
- 分岔點:這條分支跟主線分開的那一版提交;治理帳被 git 忽略時,那一版的提交裡根本沒有治理帳。
- head_sha:寫治理帳事件時自動記下的當下 HEAD(40 碼);git 叫不起來時不寫這欄。
- 考場:mOrangePos 的演練工作樹與只留本機的分支,拿來實機驗 lumos,不推、不併。
- 撞名:`-t`/`-g` 這類用名字篩測試的參數,會連帶選中別支名字相近的測試。標題索引(`_TitleIndex`)是把整個平台的測試標題建成可查的索引,每個平台建一次,之後每個綁定名(條款 `[test:]` 寫的測試名)只在它上面查。
- 比對工具:`lumos test-guard`,拿改動前版本對照新測試抓作弊;它列的 tq/assert-weakened 是「斷言變少、相等比對變少,或實際值被換成常值」。
- 逃逸帳與撤回:設計審或代碼審放行後才被抓到的缺陷記進逃逸帳;記錯的用撤回(追加一筆 withdraw),清單標已撤回、統計不算。

## 問題與最小解

立案(2026-11-03,Enzo 原話):看完實機驗收結果後「處理掉」。

1. **判綠紀錄跨分支漏過來**:`_redbase_branch_rows` 拿工作目錄的治理帳減掉分岔點那一版,算出「這條分支自己寫的」紀錄。治理帳被忽略時分岔點那一版根本沒有,工作目錄裡所有分支留下的紀錄都被當成這條分支的。考場實測:上一條分支實作完成後補跑留下的判綠紀錄(head_sha 9101c0b,不是新分支的祖先)漏到從設計重來的新分支,五支測試全被判成「曾判綠,不算實作前的版本」,一個紅燈版都沒存(卷證在考場本機分支 drill/service-charge-e2e2 的 drill-evidence/redbase-realrun2/)。同一份計劃在任何分支判綠過一次,之後所有分支都失去比對作弊的起點。
2. **效能測試在 CI 上時好時壞**:`t_name_collision_scales` 要證「撞名判定每個平台只建一次標題索引」,卻每次直接傳原始標題清單給 `_name_filter_collisions`,等於每個名字都重建一次 22000 筆的索引;本機 5.8 秒,CI 連兩次 16.2、18.5 秒超過 15 秒門檻(PR #153 的 CI 與合併後主線 CI)。
3. **代碼審 r5 放行時寫的回頭條件**(見 [[Projects/紅燈版實跑三缺口_計劃]] 做法 1):`_TG_CONST_PAT` 不認三引號字串;`_tg_ident` 的說明寫錯傳進去的函式;`_TG_LIT_PAT` 的註解沒寫明跟 `_C_STRIP_PAT` 的差別。
4. **考場的 lumos 是舊版**:還不認得撤回的逃逸紀錄(新版 `cmd_loop_escape` 的說明寫舊版會把它印成可疑列、統計多算;舊版行為沒實測)。

最小解:①讀這條分支的紀錄時,只留帶的 head_sha 是目前 HEAD 祖先(或就是 HEAD)的;head_sha 指的提交在完整 repo 裡已經不存在(分支刪掉、物件被 git 清掉)也算不是祖先、丟掉;沒帶 head_sha、淺複製裡找不到、git 叫不起來或逾時的照舊留(這幾類跟現在一樣)。代價:本 repo 推送前要把本機提交壓成一個,壓掉的提交上的判綠紀錄之後就不算數,「判綠過不存紅燈版」這條保護在壓提交後變鬆(見實務隱患的天花板);②效能測試改成走正式的快取路徑 `_name_collision_reason`、數標題索引建了幾次(1000 個名字只建 1 次),牆上時間只留寬鬆的安全網;③`_TG_CONST_PAT` 補三引號、兩處註解改對;④考場分支跑 lumos update(只動考場本機分支,不碰 mOrangePos 主目錄)。

PRIOR-ART: 判斷一筆紀錄屬不屬於目前分支,git 的標準問法是 `git merge-base --is-ancestor <提交> HEAD`(rc 0 是祖先、1 不是、其他是錯誤;https://www.kernel.org/pub/scm/git/git-manpages.git/tree/man1/git-merge-base.1);用它過濾測試紀錄時,被壓掉或 rebase 掉的提交的紀錄也會被濾掉(本案寫成天花板)。效能測試改數次數:要證的是「不重做」這個行為,數建構次數是確定性的檢查,不受機器快慢影響;牆上時鐘門檻只能證「這台機器夠快」(本 repo 測試品質標準的抓錯證據原則)。
RETIRE-IF: 治理帳在所有消費專案都進版控、而且切分支時工作目錄的治理帳一定跟著換時,第 1 項的祖先過濾就多餘,可以拿掉 [retire:人裁] [until:2027-05-03]

## 做法

1. **判綠紀錄只認本分支的**:`_redbase_branch_rows` 收齊紀錄後,把各筆的 head_sha 去重,逐一問 `git merge-base --is-ancestor <head_sha> HEAD`(走既有的 `_lens_git_dl`,整批共用一個 10 秒截止時間):
   - rc 0 留;rc 1 丟;
   - 其他回傳碼(提交物件不存在時是 128):再用既有的 `_push_rev` 問那個提交在不在——查得到但判不了照舊留;查不到而且 repo 不是淺複製(`rev-parse --is-shallow-repository` 回 false)就丟(完整 repo 裡不存在的提交不可能在 HEAD 的歷史上);淺複製照舊留(歷史被截掉,查不到不代表不是祖先);
   - 沒有 head_sha、不像提交編號(既有的 `_LENS_SHA_RE`)、git 叫不起來或過了截止時間,照舊留;
   - 不同的 head_sha 超過 200 個就整批照舊留(不逐一問)。過了截止時間或超過 200 個時印一句說明,講這一批照舊沒過濾。
   規格閘留痕與判綠紀錄都過這道(兩種都由 `_gate_event` 寫入,head_sha 由它自己跑 `git rev-parse HEAD` 補上)。`_redbase_branch_state` 拿同一批列判「判綠過沒」與找「上一份紅燈版」,過濾後兩者都只看本分支歷史上的紀錄(別條分支的上一份紅燈版也不再拿來去重,這是預期效果)。
2. **效能測試改數次數**:`t_name_collision_scales` 改成走 `_name_collision_reason`:
   - 暫時把 `_raw_test_titles` 換成回傳那 22000 筆標題,把 `_TitleIndex` 換成會計數的子類(`_name_filter_collisions` 用 isinstance 判是不是索引,換成函式會丟錯),兩者都在 finally 換回(載入的模組是全測試共用的單例);
   - pentry 給 `name_filter: regex_tail`(給 `ident` 會直接回 None、不建索引,測試空轉);
   - 同一個 cache 底下 1000 個名字,`_TitleIndex` 要恰好建 1 次;牆上時間 60 秒內只當安全網(本機實測 0.29 秒)。
3. **三引號常值斷言與註解**:
   - `_TG_CONST_PAT` 的字串那段改成用 `_TG_LIT_PAT`(已認三引號),不另寫一份;`_TG_LIT_PAT` 現在定義在 `_TG_CONST_PAT` 後面,要把它的定義搬到前面。`_TG_CONST_PAT` 有三處 fullmatch(判預期值是常值、判實際值是常值、判兩邊都常值),三處都會一起認得三引號,不只 S4;
   - `_tg_ident` 說明改成「只換字串外壓法的呼叫端傳 fold(例如 `_tg_ws_keep_strings` 傳 `_tg_ws_collapse`)」;
   - `_TG_LIT_PAT` 註解寫明跟 `_C_STRIP_PAT` 的主要差別:它要求字串收尾、只認 `"""`、單行雙引號與單字元 `'x'`;`_C_STRIP_PAT` 還收沒收尾的字串、三個單引號、C# 的 `@"…"`、反引號,而且連註解一起吞;
   - [[Projects/紅燈版實跑三缺口_計劃]] 做法 1 那行「已知漏判」與它的 REVISIT 標成已處理(`[closed:日期 理由]`),指回本計劃。
4. **考場更新 lumos**:考場本機分支跑 `lumos update`,照 S5 的判準看 `lumos loop escape --list`;不推、不併,也不碰 mOrangePos 主目錄(那裡有別人的改動)。

## 驗收條款

- [S1] 當治理帳裡有別條分支(head_sha 不是目前 HEAD 的祖先)留下的判綠紀錄時,規格閘應照樣存那支測試的紅燈版 [test:t_spec_gate_redbase_green_other_branch]
- [S2] 當判綠紀錄的 head_sha 是目前 HEAD 的祖先、或紀錄沒有 head_sha 時,規格閘應照舊不存那支測試的紅燈版 [test:t_spec_gate_redbase_green_other_branch]
- [S6] 當判綠紀錄的 head_sha 指的提交在完整 repo 裡已不存在時,規格閘應照樣存那支測試的紅燈版 [test:t_spec_gate_redbase_green_other_branch]
- [S3] 當 1000 個綁定名在同一個 cache 底下判撞名時,標題索引應只建一次 [test:t_name_collision_scales]
- [S4] 當測試把 `assertEquals(1, f())` 換成兩邊都是三引號字串常值的 `assertEquals("""a""", """a""")` 時,比對工具應列 tq/assert-weakened [test:t_tq_guard_string_comma_args]
- [S5] 當考場分支更新 lumos 之後,撤回的逃逸紀錄應標成已撤回、不算進統計 [manual:考場本機分支跑 lumos update 後 lumos loop escape --list,標頭有「其中 2 筆已撤回(統計不算)」、那兩筆原列尾端有 ★已撤回★、沒有等級印成問號的列]

## 回退

四項各自獨立:第 1 項拿掉 `_redbase_branch_rows` 的祖先過濾;第 2 項把測試改回量時間;第 3 項把 `_TG_CONST_PAT` 改回單行字串樣式、註解改回;第 4 項考場分支 git 還原 lumos 那幾支檔。

## 實務隱患
- 已排除:金流:只改規格閘紅燈版的判綠過濾、比對工具的常值判法與一支測試,不碰收費或扣款流程
- 已排除:對外送出:不寄信不推播,只多叫本機 git
- 已排除:不可逆:改判讀與測試,沒有資料遷移;改壞了回退就回來
- 守衛面:第 1 項改的是規格閘決定存不存紅燈版的判斷,第 3 項改比對工具的判讀,走設計審與代碼審
- 效能:祖先判斷每個不同的 head_sha 問一次 git(查不到時多問一次在不在),一條分支的判綠紀錄通常不到十筆;整批共用 10 秒截止時間,超過 200 個就整批照舊,不逐一問
- 天花板一:壓過或 rebase 過的分支,壓掉的提交上的判綠紀錄不再算數(head_sha 不再是祖先),那支測試之後判紅會存紅燈版(比對起點換成那一版,不會漏比,只是「判綠過不存」這條保護在壓提交後變鬆)
- 天花板二:過濾的粒度是「提交歷史」不是「分支」。判綠時實作還沒提交、之後從同一個 HEAD 開新分支重來,那筆判綠紀錄的 head_sha 仍是新分支的祖先,照舊會被認成判綠過、不存紅燈版。考場實測那次(判綠在實作提交之後)不屬這種
- 天花板三:淺複製(例如 CI 只抓最近幾個提交)裡查不到的 head_sha 照舊留,別條分支的紀錄在淺複製裡可能漏過來;規格閘紅燈版在開發機上跑,CI 不存紅燈版

## 審計修正紀錄
