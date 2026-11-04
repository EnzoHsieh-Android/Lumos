---
type: project
status: doing
created: 2026-11-04
updated: 2026-11-04
tags:
  - type/project
  - status/doing
  - scope/guards-gates
lands_in:
  - Systems/規格閘
  - Systems/reversibility-governance-ledger
  - Systems/bound-tests-gate
  - Systems/代碼審修正關卡
related:
  - "[[Projects/規格閘紅燈測試快照_計劃]]"
  - "[[Projects/規格落成可驗收條件_計劃]]"
  - "[[Projects/業務簽核留痕_計劃]]"
  - "[[Projects/Android測試防竄改檢查_計劃]]"
  - "[[Systems/test-quality-evidence]]"
decisions:
  - content: 風險高、生效日之後的計劃,在 PR 檢查時(lumos pr-evidence --base --head,CI 的 pull_request 事件呼叫)做基準重播:這個 PR 改到的測試檔裡、新行為條款綁的測試,在 PR 目標分支的分岔點(配上 head 的測試檔)要紅、在 head 要綠;唯一會擋的是新行為測試在舊程式上就綠,其他證明不了的情況記成判不了;規格閘對紅綠照舊只印不擋。改寫 Systems/規格閘「風險高照半套:紅綠只印不擋」與 Projects/規格閘紅燈測試快照_計劃〈四、不做〉「不改風險高計劃「不強制先紅」的規則」
    id: d1
    context: 審查帳 133 份計劃裡風險高 102 份(77%),只有 13 份跑出過紅;風險高的沒有紅燈版,預期值被改成實作輸出時只剩審查,而審查本身也是 AI 判斷
    why_chosen: Enzo 原話:風險高的測試到底是不是實在的測試;設計審 r1(另寫翻帳找紅)與 r2(沿用風險低推送前檢查)兩輪都在帳與留痕的接縫上抓到大量誤擋與繞過,同類兩輪換形狀;Enzo 要求搜世界解後裁「換成基準重播(推薦)」——devops-cli 的 fail-to-pass 與 PRProof 都是從 git 直接在分岔點重播,不用帳、不管先寫後寫
    decided: 2026-11-04
    valid: true
  - content: 紅要紅在斷言上(讀 Gradle 報告判紅因)移到第二批,跟建置檔與變異測試一起在考場實跑後設計;第一批照現有判法(退出碼判紅、弱證據不算)
    id: d2
    context: 規格閘拿退出碼判紅,Kotlin 的 TODO() 丟 NotImplementedError 也算紅,這種紅只證明程式不存在
    why_chosen: 設計審 r1 三席獨立實測:整批跑完才讀報告會被同類別後一支覆蓋、借來的斷言白名單漏掉 Mockito verify 與 assertAll、失敗內文截在 4000 字讀不到 Caused by、passed 與逾時會被判紅;這些都要在每支測試跑完當下讀 Gradle 輸出,得先實跑
    decided: 2026-11-04
    valid: true
  - content: 先紅模式的風險高計劃要有預期值表,整張表的指紋要有簽核才推得上去;預設請人簽,沒有互動終端記成 AI 簽也放行,不設金鑰、不防代簽。改寫 Projects/業務簽核留痕_計劃「何時該簽由人/流程判，工具不擋」:這類計劃的預期值表改由工具要求;跟 Projects/規格落成可驗收條件_計劃 d9「不補人簽門」(管的是風險低四行已排除理由的自我認證)是不同對象,不翻它
    id: d3
    context: 先紅、紅燈版、防竄改比對都只證明測試會抓錯,證明不了預期值符合需求;現有 signoff 沒有閘讀、也不綁內容
    why_chosen: Enzo 原話:也不用搞金鑰這麼麻煩，預設就是人簽，但也不用防止代簽這件事情，有些工作走向就是無人看顧，隨著AI越來越強，本來就想把人慢慢抽離;AI 也能簽,所以無人看顧的流程不會被這道卡住,人抽離多少由統計看
    decided: 2026-11-04
    valid: true
  - content: 拆兩批:第一批是推送前基準重播、預期值表與整表簽核;第二批是 Gradle 執行端(紅要紅在斷言上、建置與 CI 讓測試不跑、改到的行跑變異測試)另開計劃
    id: d4
    context: 第二批要實際跑 Gradle、選變異測試工具(含付費的 Arcmutate),細節得先在 Android 考場試跑才定得了
    why_chosen: 第一批全在 Python 這側、本 repo 測得到;第二批沒試跑就寫條款,設計審會一直抓到想像出來的細節
    decided: 2026-11-04
    valid: true
  - content: 整張預期值表一個指紋、改了任何一格整張重簽,不做逐列簽;表格條款欄寫裸編號 S3,不加方括號
    id: d5
    context: 設計審 r1:逐列簽的人/AI 歸屬與統計無定義、刪列或刪整節可繞過;表格寫 [S3] 會被條款解析當成第二次定義而擋
    why_chosen: 預期值表只對風險高計劃、每條新行為一兩列,表小,整張重簽的成本低;逐列指紋的歸屬規則換來的只有少簽幾列
    decided: 2026-11-04
    valid: true
  - content: 生效開關看計劃的日期:開頭欄位 created 與計劃第一次進 git 歷史的日期(_plan_first_commit)取較晚者,對純日期常數 _HIGH_RISK_EVIDENCE_SINCE(同 _NOTE_LINT_PLAN_SINCE 寫法);都讀不到才當成生效日之後。不看審查帳的迴圈首筆帳或設計審判定檔
    id: d6
    context: 設計審 r2:審查帳在消費專案被 git 忽略、乾淨 clone 讀不到首筆帳;判定檔路徑由檔名推的迴圈編號對不上 56 篇帶底線的計劃與帶後綴的迴圈
    why_chosen: 兩個來源都進版控、哪台機器都讀得到、跟迴圈編號無關;只看 created 不可信(lumos set 就能改,_plan_first_commit 的說明這樣寫),所以跟 git 歷史取較晚者(設計審 r3)
    decided: 2026-11-04
    valid: true
  - content: 基準重播放在 PR 檢查,不放推送前掛鉤
    id: d7
    context: 設計審 r3、r4 在推送前那條路上連續抓到推送形狀的接縫:掛鉤與 lumos 版本錯開讓既有閘失效、增量或累計範圍互相矛盾、直推主線算不出分岔點、推標籤、冷樹卡在推送前
    why_chosen: Enzo 定的「同類 major 連兩輪先查方向」查到:devops-cli 的 fail-to-pass 與 PRProof 都在 CI 的 Pull Request 檢查跑,基準是 PR 目標分支;社群共識是 CI 才是最終依據、昂貴檢查放 CI;Enzo 裁「換位置到 PR 檢查(推薦)」
    decided: 2026-11-04
    valid: true
pending_questions:
  - id: Q1
    text: 第二批的變異測試工具用付費的 Arcmutate(有 Kotlin 協程與 inline 的垃圾變異過濾、git 改動模式,價格未公開)還是開源 PIT 加 Android 外掛分支(免費,但 Kotlin 垃圾變異沒過濾、改動模式已被移除要自己算)?建議:先兩個都在考場試跑,比垃圾變異比例與耗時再定
    class: 成本
    stage: 實作
    status: 延後
    reason: 第二批另開計劃,先在考場試跑兩種工具再問人
---
# 高風險測試證據加嚴_計劃

> 白話:現在越危險的功能,工具對它的測試反而管得越鬆——風險低的計劃要求每條新行為的測試在實作前先紅,風險高的只印不擋,交給設計審與代碼審。但審查本身也是 AI 在判斷,拿它補最重要的那一塊說不通。這份計劃在 PR 檢查時對「這個 PR 真的在實作的風險高計劃」做一次基準重播:把它新行為條款綁的測試,放到分岔點那一版的舊程式上跑,必須紅;放到推送版上跑,必須綠——證明測試真的在驗這次的改動,跟測試先寫後寫無關。預期值寫成一張表、每列寫需求來源,推送前整張表要有人簽(預設人簽,AI 簽也放行但記下來)。「紅要紅在斷言上」、建置檔讓測試不跑、改到的行跑變異測試這三件要讀 Gradle 的輸出,排第二批。

## 名詞

- 風險高/風險低:規格閘的門判定(`_door_judge`)判的:任一硬訊號命中(連到標了金流、對外送出、不可逆、守衛面的節點等),或〈實務隱患〉缺任一類「已排除」行,就是風險高;作者只能往嚴調。那四行「已排除」是作者自填的。
- 新行為條款:驗收條款裡沒標 `[keeps]`、綁了 `[test:]` 的那幾條;標 `[keeps]` 的是「維持既有行為」,測試本來就該綠。
- head:PR 的頂端提交(CI 從 pull_request 事件拿;本機手動跑時自己給)。
- 分岔點:head 跟 PR 目標分支的 merge-base;PR 檢查時就是「這個 PR 開始之前」那一版。
- 基準重播:開兩個隔離工作樹(`_isolated_worktree`,殺傷力驗證與修正關卡已在用),一個是分岔點、一個是推送版;把這個 PR 新增或改過的測試檔(`_nodehome_is_test` 判的)從 head 複製進分岔點那一棵,正式程式碼留舊版;兩棵各跑一次計劃綁的測試(`_spec_gate_judge_items`,修正關卡已拿它在隔離工作樹裡跑;樹的準備也跟修正關卡共用)。新行為測試在舊版紅、head 綠,叫「證實」。世界上同樣的做法叫 fail-to-pass(見調研)。
- 對照組:基準重播時,標 `[keeps]` 的條款測試在舊版也要綠;head 那一棵的新行為測試要綠,也是對照——兩棵是同一種方式建的,環境壞了兩棵都會壞。對照組不綠時不算證實、也不擋,記成判不了。
- 弱證據:規格閘紅、綠之外的第三種判定,意思是「這次跑的結果證明不了什麼」——一支都沒跑到、篩選選中好幾支、被跳過(`_spec_gate_verdict`)。
- 生效日:程式常數 `_HIGH_RISK_EVIDENCE_SINCE`,純日期,寫法同 `_NOTE_LINT_PLAN_SINCE`,值取實作合併日的隔天;計劃的日期取開頭欄位 `created` 與計劃第一次進 git 歷史的日期(`_plan_first_commit`)兩者較晚的,都讀不到才當成生效日之後。
- 預期值表:計劃裡一節 `## 預期值表`,底下一張表,逐列寫「哪條條款、輸入什麼、預期什麼、這個預期從哪條需求來」。
- 表指紋:整張預期值表的內容指紋,任一格改了任何一個字就變;換行符號、格子頭尾的空白不算。
- 簽核:有人看過預期值表、確認每列對得上需求,工具記下表指紋與簽的是人還是 AI。
- 治理帳與審查帳:治理帳是 `docs/.governance-log.jsonl`,各道閘的事件都寫這裡,進版控;審查帳是 `docs/.canary-log.jsonl`,消費專案預設被 git 忽略。本計劃新寫的事件與讀的簽核都只在治理帳。
- 判不了:基準重播證明不了「測試有在驗」、也證明不了「沒在驗」的情況(對照組不綠、head 不綠、弱證據、環境起不來);記一筆事件、不擋。唯一會擋的反證是「新行為測試在舊程式上就綠」。
- 考場:mOrangePos 的演練工作樹與只留本機的分支,拿來實機驗 lumos,不推、不併。
- 逃逸帳:審查放行之後,在實作、CI、正式環境才被發現的洞,用 `lumos loop escape` 記下來的帳。

## 問題與最小解

立案(2026-11-04,Enzo 原話):「風險高的靠review 補位？ 但是重點在於，風險高的測試，到底是不是實在的測試」「直接開新計劃，網路印證方向、做法，排除已有人實驗無效的坑」。設計審 r2 之後 Enzo 要求「搜世界解」,並裁「換成基準重播(推薦)」。

1. **風險高的計劃幾乎都沒有先紅的證據**:審查帳裡規格閘留痕 458 筆(2026-09-17 到 11-03)共 133 份計劃;每份取最新一筆看風險,風險高 102 份(77%);這 102 份裡,任何一筆留痕跑出過紅的只有 13 份(只看最新一筆是 7 份)。風險高的沒有紅燈版,推送前比對抓不到「預期值被改成實作的輸出」,只剩審查。
2. **預期值對不對需求,工具完全沒管**:先紅、紅燈版、防竄改比對都只證明「測試會抓錯」,證明不了預期值本身對;前面每一關都過、預期值寫成打八折而需求是打九折,照樣上線。現有 `lumos signoff` 記一筆「誰點了頭」(棄置合約時 `guard abandon` 會讀它帶的參照),不綁內容,也沒有推送前的閘讀它。
3. **「紅」不分原因**(第二批):Kotlin/Java 的測試輸出讀不出跑了幾支(`_RAN_EVIDENCE` 沒有這兩種),只能照退出碼判;編譯失敗、`--tests` 篩不到、被測程式還是 `TODO()`,全都判紅。

最小解:前兩輪設計審證明,要從帳上證明「實作前紅過」得接好幾個既有機制的接縫(r1 另寫一套翻帳、r2 沿用風險低的推送前檢查,兩輪各抓到大量誤擋與繞過)。改成直接從 git 算:分岔點的舊程式就是「還沒實作」的版本,在它上面跑新測試必須紅——不用帳、不用判設計審過了沒、不管先寫後寫,連「實作寫完再搬走造假紅」也不怕(重播用的是真的舊版)。r3、r4 再證明放在推送前會碰上推送的各種形狀(版本錯開、增量或累計、直推主線、標籤、冷樹卡在推送前),所以跟世界上的做法一樣放在 PR 檢查,基準就是 PR 的目標分支。預期值表與簽核另外新增。

PRIOR-ART:fail-to-pass 基準重播是世界上已有的做法:devops-cli 的 `ci fail-to-pass`(在暫存目錄建分岔點的樹、把推送版的測試覆蓋上去、只認呼叫階段失敗、收集錯誤不算數、要有附理由的不適用出口、另設自檢重播已知提交)、PRProof(分岔點 git 工作樹加複製改過的測試檔,舊版紅且推送版綠才判 PROVEN,跑不可靠回 ERROR);只要求「修前紅、修後綠」不夠的實證(UTBoost,ACL 2025:Verified 裡 26/500 題測試不足、345 個錯誤修補被判通過)與 PRProof 自承「錯的修補配錯的測試照樣 PROVEN」,所以預期值另外要人簽。簽核綁內容指紋、內容改了舊簽作廢,同 GitHub「推新提交作廢舊核可」與 Gerrit copyCondition;表格解析照 GFM 表格規則(格內 `\|` 是字面管線),欄數不符時不照 GFM 補或丟,一律擋。借用:`_isolated_worktree` 與修正關卡的樹準備(抽成共用)、`_nodehome_name_status`、`_note_text_at_rev` 與 `_note_from_text`、`_gov_rows_at`、`_lumos_config_at_ref`、`_spec_gate_judge_items`、`_spec_gate_twoway_static`、`_clause_check_twoway`、`_redbase_row_reason` 的逾時規則、`_nodehome_is_test`、`_plan_first_commit`、`_NOTE_LINT_PLAN_SINCE` 的生效寫法、新增告警閘「自己放寬開關照起點判」的做法、`_h2_section_lines`、`_real_chars`、`_waive_origin_tty`、lint-waive 的 `origin` 欄與端到端驗收的簽核人取法、既有 `signoff` 閘名、CI 既有的 pull_request 工作流程;自建:`pr-evidence` 指令的串接、預期值表解析、表指紋。
RETIRE-IF:生效後連續 90 天,治理帳的 `base-replay-failed` 與 `expected-unsigned` 兩種擋下事件都是 0,而且同期逃逸帳裡沒有一筆描述是「測試預期值抄實作」或「測試沒在驗」——代表這兩道沒在擋任何東西,改回只印;或 `expected-signed` 事件裡 origin 是 ai 的連續 90 天佔 100% 且逃逸帳沒有預期值類的洞,簽核這道改成只記不擋;或 `pr-evidence-skipped` 佔 `pr-evidence-skipped` 加 `base-replay-proven` 加 `base-replay-failed` 的一半以上,代表重播在實務上跑不起來,回頭檢討做法。

## 調研結論(2026-11-04,四路網路調研)

- **只靠先紅不夠,要配紅燈版與變異測試**:UTBoost(上)與 PatchDiff(Wang、Pradel、Liu,ICSE 2026:通過測試的修補 29.6% 行為跟標準解不同)。先紅是入場券;「事後把實作搬走造假紅」查不到專門對策,對最終程式跑變異測試跟先寫後寫的順序無關,是第二批要補的那一塊。
- **Gradle 報告分不出紅的原因**:Gradle 的 JUnit XML(`JUnitXmlResultWriter`)把 `errors` 寫死成 0,所有例外都歸 `<failure>`;要看失敗的型別。Truth、AssertJ、kotlin.test、MockK 的 verify 都丟 `AssertionError` 子類;Kotlin `TODO()` 丟 `NotImplementedError`(繼承 `Error`,不是 `AssertionError`)。
- **證明「紅發生在實作之前」靠不住**:用提交順序認定 TDD 的研究(Borle 等,EMSE 2017)得放寬到晚一週提交也算才收得到樣本;Fucci 等(TSE 2017)發現順序本身沒有重要影響。不走這條。
- **AI 看得到實作,預期值就會照實作寫**:Konstantinou 等(2024/2026 v2)斷言「mainly capture the actual program behavior」;Charoosaei 等(2026)AI 測試 8–17% 把錯誤行為寫成預期值,其中 83–91% 之後一直通過。支持「預期值逐列寫需求來源」。
- **人工核可會鬆**:審查留言只有 14% 講缺陷(Bacchelli、Bird 2013);先看到 AI 的答案再問人對不對,人多半只看 AI 指的地方(Tufano 2024)。所以只對風險高的要簽,表要小,每列帶出處。
- 已被證明無效、這份計劃避開的:拿 XML 的 failure/error 分紅因;把 LLM 判官當唯一的閘(SWE 類任務上監看器只抓 42–50% 作弊,ImpossibleBench);只靠 TDD 提示詞(TDAD 預印本:回歸錯誤升到 9.94%);用提交順序證明先寫測試;簽核不綁內容(簽完再改預期值等於沒簽)。
- 設計審 r1(2026-11-04)後補查:GFM 表格規則裡格內 `\|` 是字面管線;欄數少於表頭補空格、多於表頭丟掉多的(本計劃不照這個寬鬆做法,見 PRIOR-ART)。
- 設計審 r2(2026-11-04)後 Enzo 要求搜世界解:fail-to-pass 基準重播。devops-cli 的 `ci fail-to-pass`(在暫存目錄建分岔點的樹、覆蓋推送版的測試、只認呼叫階段失敗、收集錯誤不算、附理由的不適用出口、自檢重播已知提交;它踩過重播環境把每支都弄紅、檢查形同虛設的坑,issue #3124);PRProof(分岔點 git 工作樹加複製改過的測試,舊版紅且推送版綠才 PROVEN,跑不可靠回 ERROR;自承「錯的修補配錯的測試照樣 PROVEN」)。另有 verify-fix 這類「沒修紅、修了綠」的指令。用提交順序或時間認定先寫測試,沒有找到可靠的工具。

## 做法

### 第一批(本次實作):PR 檢查時的基準重播,加預期值表與簽核

0. **實驗與兩次世界查證**:
   - 最小實驗(設計審 r3 後):在本 repo 開推送版與分岔點兩棵隔離工作樹、只把測試檔覆蓋進分岔點,用 `_spec_gate_judge_items` 跑。呼叫新函式的測試推送版綠、分岔點紅;不依賴改動的新測試兩邊都綠;既有測試兩邊都綠;每支每棵約 2.7 秒;測試跑紅會留下暫存現場。紀錄在 `governance/review-reports/高風險測試證據加嚴/r3-intake.md`。
   - 世界查證(設計審 r4 後,Enzo 新定的「同類 major 連兩輪先查方向」):基準重播的方向對,但世界上的做法(devops-cli 的 fail-to-pass、PRProof)都放在 CI 的 Pull Request 檢查,基準是 PR 的目標分支;社群共識是 CI 才是最終依據、昂貴的檢查放 CI,推送前掛鉤只當方便。r4 抓到的接縫(掛鉤與 lumos 版本錯開、增量或累計範圍、直推主線、推標籤、冷樹卡在推送前)都來自放在推送前。Enzo 裁「換位置到 PR 檢查(推薦)」。紀錄在 `governance/review-reports/高風險測試證據加嚴/r4-intake.md`。
1. **一支獨立指令**:`lumos pr-evidence --base <提交> --head <提交> [--json]`。
   - 不猜推送的形狀:兩端都由呼叫者明確給;指令內部先算 `git merge-base <base> <head>` 當分岔點(PR 的目標分支往前走過也對)。算不出 merge-base、或分岔點就是 head:印一句、寫一筆 `pr-evidence-skipped` 事件、rc0。
   - CI:本 repo `.github/workflows/ci.yml` 的 pull_request 事件加一步,呼叫 `lumos pr-evidence --base ${{ github.event.pull_request.base.sha }} --head ${{ github.event.pull_request.head.sha }}`;這個工作流程已經 `fetch-depth: 0`(完整歷史)。消費專案的 CI 範例寫進 lumos-project-notes 的說明;沒有 CI 的專案在開 PR 前手動跑 `lumos pr-evidence --base origin/main --head HEAD`。
   - 推送前掛鉤不動、不加參數(版本錯開的問題因此不存在)。
   - 回傳碼:有一份計劃確定不過(第 5 點唯一的擋、第 7、8 點表與簽不過)rc1;其他(含工具自己出錯)rc0。整支包一層:任何沒預期的例外都印原因、寫 `pr-evidence-skipped`、rc0——工具壞了不擋所有人,同推送前檢查的既有約定。
2. **哪些計劃要查**(一律讀 head 那一版):
   - `git -c core.quotePath=false diff -z --name-status -M <分岔點> <head>` 的改檔清單(用既有的 `_nodehome_name_status` 解析,路徑含 tab 或換行也切得對)裡,檔名以 `_計劃.md` 結尾、在 head 版本存在的計劃檔。
   - 用 `_note_text_at_rev` 讀 head 版本的計劃文字、`_note_from_text` 組成筆記物件(同 load_vault 的解析,不另寫一套);`type: project`、至少一條 `[SN]` 條款、門重判(`_door_judge`)是風險高、生效日判定(第 6 點)在生效日之後,才算。
   - 計劃開頭欄位 `base_replay_skip` 是字串、用 `_real_chars` 數至少 10 個字時,這份計劃不重播(第 4、5 點),印出理由、寫 `pr-evidence-skipped`;預期值表與簽核照查。欄位不是字串(例如寫成清單)當成沒寫、印一句。要能用 `lumos set` 寫,`base_replay_skip` 加進 `SCALAR_KEYS`、`_KNOWN_FRONTMATTER_KEYS`、`remove` 允許的鍵。
3. **要重播哪些測試**:
   - 計劃的新行為條款(沒標 `[keeps]`、綁了 `[test:]`)綁的測試裡,定義在這次改檔清單裡的測試檔的那幾支(用 head 那棵樹的 `_platform_test_index` 找每支測試在哪個檔)。前一批已經合進主線、這次沒改到的測試不重播——它們在分岔點本來就綠,重播只會誤擋。這次一支都沒有就印一句、不重播。
   - 對照組:標 `[keeps]` 的條款綁的測試(計劃建立前就存在,分岔點本來就該綠)。
   - 重播前在 head 那份計劃上呼叫 `_spec_gate_twoway_static` 與 `_clause_check_twoway`(綁的測試存在、不同條款不能綁同一支);兩支各加選填參數換掉寫死的「風險低」前綴、「全部條款都靠人驗……走小改動閘」與「或把門升成單向」那幾句,`_spec_gate_twoway_static` 另加一個起點參數把 head 傳給它裡面的 `_plan_first_commit`(不沿 HEAD 找)。這兩支不過算第 5 點的「確定不過」。
4. **兩棵工作樹**:
   - 用 `_isolated_worktree` 開分岔點與 head 兩棵(前綴 `lumos-replay-`,建樹前清同前綴的殘骸);同一次執行好幾份計劃共用兩棵樹。建樹失敗算判不了(第 5 點)。
   - 樹的準備抽成一支共用函式,修正關卡與這裡都用它(現在是寫在 `cmd_fix_check` 裡的一段,出錯直接 return 2;抽出來改成回傳「準備好沒、說明、哪些平台釘不住版本」,由呼叫端決定擋或放——修正關卡照舊擋,這裡算判不了):設定檔用 head 版本那份 `.lumos/config.json` 覆蓋進兩棵樹(新參數;修正關卡照舊「樹裡沒有才複製」);依賴資料夾照 `fix_check.link_deps` 開關與 `_LINT_DEP_DIRS` 的清單用 `_lint_link_deps` 連回主目錄;平台根在樹外、沒進版控、是子模組或符號連結的,標成釘不住版本,那個平台不重播。
   - 覆蓋測試檔:改檔清單裡兩邊都判成測試(`_nodehome_is_test` 帶 `_nodehome_layout`)的新增或修改檔,從 head 複製進分岔點那棵;改名的(舊路徑與新路徑都是測試檔)先刪分岔點那棵的舊路徑再複製新的;刪掉的測試檔在分岔點那棵也刪;只搬內容、不帶檔案模式,符號連結不複製。舊路徑不是測試檔的改名不動舊路徑(不刪正式程式)。
   - 跑測試:`_spec_gate_judge_items` 與 `_run_bound_tests` 各加兩個選填參數一路傳下去(既有呼叫端不帶、行為不變):每支逾時、要覆蓋的環境變數;`_kill_run` 加 `env` 參數。逾時用 `LUMOS_REPLAY_TEST_TIMEOUT`(讀不懂、不是正數、nan、inf 都用預設 900 秒);環境變數覆蓋 `TMPDIR`,指到隔離工作樹自己的暫存資料夾底下,測試跑紅留下的現場跟樹一起收。不另設總預算——整體上限交給 CI 工作的 timeout-minutes。
   - 平台的測試指令沒有 `{method}` 的,那個平台不重播(同 `_spec_gate_runnable` 的判法,但逐平台判,不是一個平台缺就全部略過);樹裡沒有那個平台根資料夾的(這次新增的模組),那個平台在分岔點不跑、算判不了。
5. **判定**(逐支,不合條款):
   - 列的第 6 欄(原始細節)以「超時」開頭的紅,改成弱證據(借 `_redbase_row_reason` 的同一條規則,抽成共用小函式)。
   - **唯一確定不過(擋)**:任一支要重播的新行為測試在分岔點是綠——「這支測試在還沒改的程式上就過了,沒在驗這次的改動」;印出計劃、條款、測試名,寫一筆 `base-replay-failed` 事件(hard)。
   - **證實**:要重播的每一支在分岔點紅、在 head 綠,而且對照組在分岔點全綠;寫一筆 `base-replay-proven` 事件(帶計劃與支數,回頭條件數得到分母)。
   - **判不了(不擋,寫 `pr-evidence-skipped` 並講原因)**:對照組在分岔點不綠(編譯型語言常見:新測試在同一模組編不過,連帶對照組也紅)、新行為測試在 head 不綠(CI 的全套測試本來就會擋)、分岔點是弱證據或逾時、建樹失敗、平台釘不住版本。理由:這些情況證明不了「測試有在驗」,也證明不了「沒在驗」;只有「舊程式上就綠」是確定的反證。
   - 分岔點的紅是例外、編譯失敗還是斷言失敗,第一批不分(第二批第 7 點);證實訊息裡照實印「分岔點的紅沒分原因」。
6. **生效日與開關**:
   - 常數 `_HIGH_RISK_EVIDENCE_SINCE`(純日期,值取實作合併日的隔天,同專案「設隔日不設當日」的慣例)。計劃的日期取開頭欄位 `created` 與計劃第一次進 git 歷史的日期兩者較晚的;後者由 `_plan_first_commit`(加起點參數,從 head 找)回的提交再用 `git show -s --format=%cs` 取。淺複製(`git rev-parse --is-shallow-repository` 是 true)時只看 `created`;兩個都讀不到才當成生效日之後。比較用「不早於」(等於當天算生效)。
   - `.lumos/config.json` 加 `pr_evidence: {"gate": "block|warn|off"}`(預設 block;同 `lint_new.gate`、`security_evidence.gate` 的區塊寫法),從 head 那一版讀(`_lumos_config_at_ref`);head 把它放寬(block 改 warn 或 off、warn 改 off)時改照分岔點那一版判,同新增告警閘對「這次自己放寬開關」的做法,PR 不能自己關掉這道;壞值照 `_note_shape_config` 的先例當 block 並印警告。warn 只印不擋、off 整道不跑(含第 7 點規格閘的表格檢查),兩者都寫一筆事件。
7. **預期值表**(只對第 2 點選出、而且至少有一條新行為條款的計劃;全標 keeps 的不要求表):
   - 找節:`_h2_section_lines` 找 `## 預期值表`(它本來就回 `(行號, 原始行)`),替它加一個選填參數回報標題出現幾次,兩次以上算格式錯。節不存在、節裡沒有表、表寫在圍欄裡都算「沒有表」。表格列連續看的是行號相連,中間隔了小標題或圍欄的兩段不併成一張表。
   - 表的範圍:去掉行首 0 到 3 個空白後以 `|` 開頭的行是表格列;第一個表格列是表頭,往下行號連續的表格列都是表;之後同一節裡又出現去掉行首空白後以 `|` 開頭的行(不論縮排),算格式錯「表後面還有表格列」。
   - 拆格:一次逐字元掃過,`\\` 是字面 `\`、`\|` 是字面 `|`(不當分隔),其他反斜線照留,遇到沒被跳脫的 `|` 就切;切完後第一格與最後一格去掉空白後是空的(外側管線、含行尾空白)就丟掉,只丟這兩格。這支拆格寫成共用函式;專案裡另外兩處寬鬆的拆法用途不同、不改,寫回筆記時註明三者的關係。
   - 每一格去掉頭尾空白、做 NFC。表頭四格依序是「條款」「輸入」「預期」「來源」;第二列是分隔列,四格都要符合 `:?-{3,}:?`;資料列至少一列、每列剛好四格、四格都不能是空的;每格最多 2000 字、表最多 500 列(超過算格式錯,簽核時印得完)。
   - 條款欄完全符合 `S` 加不以 0 開頭的數字(`s3`、`S03`、全形都算格式錯),一列一條,不加方括號;寫不存在的條款、或寫標了 `[keeps]` 的條款,算格式錯。每條新行為條款(含只有 `[manual:]` 的)至少一列;來源欄用 `_real_chars` 數至少 4 個字。
   - 規格閘對門判風險高、生效日之後、至少一條新行為條款的計劃也做同一個檢查(插在 `_spec_gate_clause_part` 之後),不過就擋 rc1,讓設計審看得到表;受第 6 點開關管。
   - 範例寫進 lumos-project-notes 的寫法說明:`| S2 | 單筆消費 1000 元 | 折扣 100 元 | 需求文件〈滿額折扣〉第 2 點:滿 1000 打九折 |`。
8. **表指紋與簽核**:
   - 表指紋:資料列依序、每列四格組成清單,`json.dumps(…, ensure_ascii=False)` 之後算 sha256(JSON 編碼不會撞)。
   - `lumos signoff <計劃> --expected --note "<一句>"`:計劃文字只讀一次(工作目錄那份,簽的人看的就是它),同一份文字做表格檢查、算指紋、印給人看。資格:門判風險高、生效日之後、至少一條新行為條款(跟 status 無關,所以實作完、status 改成 done 之後也能簽);不合資格或表格檢查不過 rc2、不寫;同時帶 `--by` 或 `--ref` 是用法錯,rc2。
   - 誰簽的:用 `_waive_origin_tty`,整張表一列一行、每格各自過 `_out_clean`,跟「確認這張預期值表對得上需求?」一起放進提示;`_waive_origin_tty` 與 `_confirm_tty` 各加選填的「沒同意時印什麼」(預設照舊印「沒放行」,這裡傳「沒簽」)與選填逾時(這裡傳 300 秒;有設環境變數 `LUMOS_TTY_TIMEOUT` 時以環境變數為準,測試靠它縮短)。答 y 記 human;答 n 或 Ctrl-C 印「沒簽」、rc1、不寫;沒有互動終端或逾時,記 ai、印一句「記成 AI 簽」。不設金鑰、不防代簽(d3)。
   - 治理帳事件:閘 `signoff`、kind `expected-signed`、`nodes` 帶計劃,欄位 `plan`、`table_sha`、`row_count`、`origin`(human 或 ai)、`who`(人簽照 `_e2e_who`,AI 簽寫 `ai`)、`token`、`note`(截到 200 字);hard 為否;`origin` 加進 `_GOV_FIELD_TYPES`。不走 `_gate_event_fit`;寫不進去 rc2。帶 `--expected` 時不寫 `signed_off` 與 `.signoff-log.jsonl`。
   - 簽核事件寫在治理帳(帳本白名單裡),跟功能一起提交;代碼審留痕之後才簽的,用留痕後那個固定訊息的帳本提交帶上(`chore(lumos): 記錄代碼審通過`)。
   - 跟 lint-waive、端到端驗收放行的 `--ack` 不同是刻意的:AI 簽的不會在 doctor 與開場一直列到人看過(d3)。
9. **PR 檢查時查表與簽**(第 2 點選出、至少一條新行為條款的計劃,用 head 版本):
   - 重做第 7 點的表格檢查(整節刪掉、改成沒有來源、表後加列,都會被擋)。
   - 用 `_gov_rows_at(<repo>, <head>, <needle>, <keep>)` 讀 head 版本的治理帳(兩版治理帳的讀法只留這一份;壞行跳過,整檔讀不到回 unreadable),篩 `signoff` 閘 `expected-signed` 事件;head 的表指紋要等於某一筆 `plan` 相同(NFC 後比)的事件的 `table_sha`。只在工作目錄、沒提交的簽核不算。整檔讀不到算判不了(寫 skipped、不擋)。
   - 沒有對上的就擋(rc1),印簽核指令,寫 `expected-unsigned` 事件(hard)。
   - 放行時,對上的事件(同一張表簽過好幾次取最晚一筆)`origin` 是 ai,印一行「預期值表由 AI 簽」不擋。
   - `lumos gov --stats`:`_gov_row` 對 `signoff` 閘的 `expected-signed` 帶出 `token` 與 `origin`(token 進去重鍵);統計輸出新增一行「預期值表簽核:人 N 次、AI M 次」。
10. **跟著改的說法**(同一個提交改掉;改注入範本照前例升小版號、寫 CHANGELOG):
   - 程式:`HELP_WHEN` 加 `pr-evidence`、`HELP_WHEN["spec-gate"]` 與 spec-gate、signoff 的參數說明補新行為。
   - CI:`.github/workflows/ci.yml` 加第 1 點那一步。
   - 注入範本(`scripts/templates/graph-discipline.md`)「風險高再進實作前的審查迴圈」後面補一句:風險高計劃要寫預期值表並簽核,PR 檢查時會做基準重播;本 repo 的 `CLAUDE.md` 與 `AGENTS.md` 重新注入。
   - 手冊:lumos-design-loop 的 SKILL.md(description、步驟 10〈過了之後〉補「測試寫在要改的測試檔裡,PR 檢查會重播;預期值表要簽」)、reference.md、templates.md 講推送前行為那幾句;lumos-code-loop 的 SKILL.md 補簽核放的位置;lumos-project-notes 的 SKILL.md 與 reference.md 講 signoff 的地方補 `--expected` 跟「業務確認」的差別、`commands/INDEX.md`、`commands/05-設計審查迴圈.md`、`commands/03-寫回圖譜.md`;消費專案 CI 範例。
   - 使用者文件:`docs/指令參考.md` 與 `docs/command-reference.md`、`ARCHITECTURE.md` 的規格閘流程、`docs/心智模型.md` 與 `docs/mental-model.md`、`docs/methodology/圖譜即合約.md`;`assets/spec-gate-zh.svg` 與 `assets/spec-gate-en.svg` 的圖說補一格。
   - 圖譜:`Systems/規格閘`(負責範圍補預期值表檢查;風險高照半套那幾行補「PR 檢查另有基準重播」)、`Systems/reversibility-governance-ledger`(新 kind 的 WHY、補負責範圍)、`Systems/代碼審修正關卡`(樹的準備抽成共用)、`Projects/雙向門放行_計劃`、`Projects/規格閘紅燈測試快照_計劃`〈四、不做〉、`Projects/業務簽核留痕_計劃`;基準重播新指令開一篇家(`lumos new system pr-evidence --code scripts/lumos`,負責範圍寫清楚),lands_in 補上。
11. **會紅的既有測試**:規格閘的預期值表檢查只對「門判風險高、生效日之後、至少一條新行為條款」的計劃;測試的計劃產生器(`_sg_plan`、`_sg_plan2`、`_sg_plan_linked`、`_qo_plan` 與直接寫 `type: project` 的那批)不帶 `created`,而且多數沒有 git 歷史——會被當成生效日之後。產生器統一補一個早於生效日的 `created`,沒有產生器、直接寫檔的那批逐支補;生效常數照 `_cap_real_cutoff` 的寫法讓測試能改。`t_spec_gate_help_says_low_risk_blocks`、`t_spec_gate_oneway_keeps_halfset` 照新說法看;修正關卡的 `t_fix_check_tree_setup` 與釘「釘不住版本」訊息的那幾支,在樹準備抽成共用後要照跑綠;`signoff` 參數的字串測試照新說法改。

### 第二批(另開計劃實作):Gradle 執行端

第二批要實際跑 Gradle,得先在 Android 考場試跑才定得了細節;本計劃只定方向與已知的坑,不寫驗收條款。

7. **紅要紅在斷言上(Kotlin/Java)**:第一批的基準重播會把分岔點上的編譯失敗當成紅;第二批讓重播與規格閘都分得出紅因。設計審 r1 已抓到的坑,第二批照這些設計(卷證在 `governance/review-reports/高風險測試證據加嚴/`):
   - 報告要在每支測試那一次執行結束當下讀(`_run_bound_tests` 現在整批跑完才回結果,同類別的 `TEST-<類別>.xml` 會被後一支覆蓋;平行跑時同一個 build 目錄互蓋)。
   - 不能只借 `_secev_junit_facts`:它只回「狀態、是不是斷言」,分不出「有型別但不是斷言」與「沒有型別」,`junit()` 的失敗內文截在 4000 字,`Caused by:` 常在截掉的那段;`scripts/test_quality.py` 有部署指紋,只借不改。
   - 斷言型別的判法不用逐一列字表(Mockito 的 `WantedButNotInvoked`、JUnit5 的 `MultipleFailuresError`、AssertJ、Kotest 的多重失敗都不在現有白名單),照 [[Systems/test-guard]] 已有的做法「照型別名字的字尾認」,另外補 Mockito 的 verify 例外(`WantedButNotInvoked`、`ArgumentsAreDifferent` 這類字尾不是 Error 或 Failure,字尾規則認不出,要看套件名);例外鏈只看 `Caused by:` 行與 type 屬性,不看斷言訊息(訊息裡可能本來就有那幾個例外名)。
   - 報告裡那支是 passed 或 skipped 時不算紅;測試逾時、走目錄逾時都不算紅(同紅燈版「逾時的紅不算」與 guard-kill 的 `timed_out_weak`)。
   - JUnit5 在報告裡的名字可能帶 `()` 或參數化的 `[n]`,比對規則要在考場實測後定;Maven 的報告在 `target/surefire-reports`。
   - 還有:單一報告檔要設大小上限(同安全證據閘的 `_SECEV_FILE_MAX`);找報告走目錄要排除 `node_modules`、`.git`、`Pods`;跑在手機上的測試報告沒有失敗型別,要另外判;「找不到報告判弱證據」與「走目錄逾時」的失效方向要一致(都不算紅)。
8. **建置檔與 CI 讓測試不跑**:不走「比對建置檔字串」當主力(變數、`gradle.properties`、`buildSrc`/`build-logic`、init script 都繞得過,test-guard 已否決「再補一輪字表」);改兩層:
   - 只在這次改到建置相關檔(`*.gradle*`、`gradle.properties`、`buildSrc/`、`build-logic/`、`junit-platform.properties`、`META-INF/services/`、`robolectric.properties`)時,工具帶一支 repo 外的 init script 讀每個 Test 任務實際生效的設定(`ignoreFailures`、`enabled`、`onlyIf`、篩選、`dryRun`、`failOnNoDiscoveredTests`、`unitTests.isReturnDefaultValues`、測試原始碼目錄),跟進版控的設定快照比,有變就列候選、要放行理由。
   - 有跑全套的地方(CI 或推送前)比 JUnit 報告的測試總數、跳過數與快照:總數下降或跳過數上升要理由(CI-Odor,Vassallo 等 ICSE 2019 的判法;受訪開發者 53.3% 贊成直接判失敗)。`isReturnDefaultValues` 這種測試照跑照綠的,只有第一層抓得到。
   - 已知不要做的:把 `failOnNoDiscoveredTests` 當安全網(有篩選、沒原始碼、dryRun 都不擋);看到 `continue-on-error` 就擋(CD-Linter 回報的這類 47% 被維護者拒絕,要限定在跑測試的那一步);把 `paths-ignore`、`junit.jupiter.conditions.deactivate`、`failFast` 當削弱。
9. **CI 對改到的行跑變異測試**(風險高計劃):
   - 照 Google 的三條:只變異改到而且有測試覆蓋的行、每行最多一個變異、跳過不值得測的地方(log、analytics、逾時常數)。Google 的數字:每個改動的變異數中位數全量 820、每行一個 77、再去掉不值得測的剩 7(Petrović 等,TSE 2021)。
   - 擋的是「每個活下來的變異都有處置(補測試殺掉,或附理由放行)」,不擋分數百分比(Google 不擋;flaky 讓分數平均飄 4 個百分點,Shi 等 ISSTA 2019;分數跟抓真 bug 的相關性控制測試數後是 weak,Papadakis 等 ICSE 2018)。
   - 放行紀錄綁檔案、行、變異寫法與程式指紋,程式改了就失效;「改到行卻 0 個變異」要報出來,不當通過。另放一個一定要被抓到的植入變異當自檢,防變異根本沒套上。
   - 只能跑本機單元測試(src/test);跑在手機上的測試沒有工具支援。工具選擇見待決問題。
   - 跟舊否決的關係:[[Projects/guard殺傷力驗證_計劃]] d1 決定合約的殺傷力驗證「不自動產生變異」,理由是等價變異不可判定、誤報 4–39%、零依賴;另外守衛閘門的世界解調研記了自動變異工具 2026-08-26 退場。這裡不一樣的地方:活下來的變異不直接判失敗,而是要處置(等價的附理由放行),誤報的代價從「擋下」變成「多寫一句理由」;引入外部變異工具跟零依賴家規衝突,第二批開計劃時要先過這一關(只在 CI 跑、不進 lumos 本體,或另找零依賴做法);第二批開計劃時要拿真實專案量「活下來但被判沒用」的比例(Google 早期 85%、調過不值得測的過濾後降到 11–20%),考場試跑超過一半就縮成只提醒。
   - 已知不要做的:追 100%、全量跑、擋百分比、把高分當預期值正確(Konstantinou、Zhao 等 ISSTA 2026)、讓 LLM 自己判等價就放行(Meta ACH 的 LLM 判等價 recall 0.47)、用開源 PIT 已移除的 `scmMutationCoverage`、沒人維護的 pitest-kotlin、原版 gradle-pitest-plugin(跟 Android 不相容)。
REVISIT:2026-12-15 第二批開計劃(與 [[Projects/Android測試防竄改檢查_計劃]] 第二批、[[Systems/test-guard]] 建置檔那條回頭條件同一天);先在考場試跑每支測試當下讀報告、init script 讀設定與兩種變異工具

## 不做

- 不在推送前跑:推送的形狀太多(版本錯開、增量或累計、直推主線、標籤),世界上的做法與社群共識都放在 PR 檢查(r4 世界查證)。推送前掛鉤不改。
- 不在規格閘證明「實作前紅過」,也不在帳上找紅的紀錄:PR 檢查時的基準重播已經證明「這支測試在沒有這次改動的程式上不會過」,跟先寫後寫無關。
- 不分紅的原因(例外、編譯失敗、斷言)(見第二批第 7 點);基準重播照現有判法:退出碼判紅、弱證據不算、逾時不算紅。
- 不重播這次沒改到的測試(前一批已在主線上的),也不重播只因連到同一個系統節點的計劃。
- 不檢查預期值表跟測試裡的預期值字面一致:那是語意比對,紅燈版與審查管;本計劃只管表存在、格式對、有來源、有簽。
- 不管「產生預期值時有沒有給模型看實作」:工具看不到對話裡給了什麼,留在寫法說明與審查。
- 不對風險低、全標 keeps、或生效日早於常數的計劃做重播、要求預期值表與簽核。
- 不設金鑰簽、不防 AI 代簽、AI 簽的不在開場與 doctor 一直提醒(Enzo 2026-11-04 原話:「也不用搞金鑰這麼麻煩，預設就是人簽，但也不用防止代簽這件事情，有些工作走向就是無人看顧，隨著AI越來越強，本來就想把人慢慢抽離」)。
- 不快取重播結果、不另設總預算:整體上限交給 CI 工作的 timeout-minutes。

## 驗收條款

- [S1] 當 lumos pr-evidence --base <B> --head <H> 的改檔清單裡有一份 _計劃.md、有條款、門判風險高、生效日之後的計劃時,應對它做預期值表與簽核檢查,並對它這次改到的測試檔裡的新行為測試做基準重播 [test:t_pr_evidence_selects_plan]
- [S2] 當計劃檔名不是 _計劃.md、沒有條款、門判風險低、生效日早於常數、或不在改檔清單裡時,應不查這份計劃 [test:t_pr_evidence_skips_plan]
- [S3] 當新行為條款綁的測試不在這次改檔清單的測試檔裡(前一批已合進主線)時,應不重播那幾支並印一句 [test:t_pr_evidence_only_changed_tests]
- [S4] 當算不出 merge-base、分岔點就是 head、或指令內部丟出沒預期的例外時,應印出原因、寫一筆 pr-evidence-skipped 事件並回 0 [test:t_pr_evidence_tool_failure_open]
- [S5] 當要重播的新行為測試在分岔點(配上 head 的測試檔)紅、在 head 綠,而且 keeps 測試在分岔點綠時,應判證實、寫一筆 base-replay-proven 事件並回 0 [test:t_pr_evidence_fail_to_pass]
- [S6] 當要重播的任一支新行為測試在分岔點就綠時,應回 1、印出計劃條款與測試名,並寫一筆 base-replay-failed 事件 [test:t_pr_evidence_green_on_base]
- [S7] 當 keeps 測試在分岔點不綠、新行為測試在 head 不綠、分岔點是弱證據或逾時、或平台釘不住版本時,應判判不了、寫 pr-evidence-skipped 並講原因、不擋 [test:t_pr_evidence_undetermined]
- [S8] 當兩條新行為條款綁同一支測試、全部條款都標 keeps、或標 keeps 的測試在計劃建立前不存在時,應回 1 並講原因,訊息不出現風險低字樣 [test:t_pr_evidence_static_checks]
- [S9] 當計劃的 base_replay_skip 是字串而且用 _real_chars 數至少 10 個字時,應不重播、印出理由並寫 pr-evidence-skipped,預期值表與簽核照查;不是字串或不夠長時應當成沒寫;lumos set 應寫得進這個鍵 [test:t_pr_evidence_skip_reason]
- [S10] 當這個 PR 把一支測試檔改名時,分岔點那一棵應先刪掉舊路徑再放新路徑;舊路徑不是測試檔時應不動它 [test:t_pr_evidence_renamed_test]
- [S11] 當主工作目錄的設定檔沒進版控、或專案有依賴資料夾時,兩棵樹應拿得到 head 的設定與依賴;重播跑紅的測試留下的暫存現場應跟樹一起收掉 [test:t_replay_tree_prep_shared]
- [S12] 當計劃的 created 早於生效日、但第一次進 git 歷史的日期在生效日之後時應當成生效日之後;淺複製時應只看 created [test:t_high_risk_evidence_since]
- [S13] 當 pr_evidence.gate 是 warn 時應只印不擋、是 off 時整道不跑(含規格閘的表格檢查),兩者都寫一筆事件;head 把它放寬時應照分岔點那一版判 [test:t_pr_evidence_gate_switch]
- [S14] 當預期值表的節出現兩次、不存在、表寫在圍欄裡、表後面還有表格列(含縮排的)、表頭不是那四欄、分隔列不對、沒有資料列、某列不是剛好四格或有空格、某格超過 2000 字或超過 500 列、條款欄不是 S 加不以 0 開頭的數字或寫了不存在或標 keeps 的條款、某條新行為條款沒有任何一列、或來源欄用 _real_chars 數不到 4 個字時,檢查應擋下並逐項列出;全標 keeps 的計劃應不要求表 [test:t_expected_table_check]
- [S15] 當格裡有 \| 或 \\、或格尾是 \| 時,拆格應還原成字面 | 與 \;行尾有空白的外側管線應丟掉;行首縮排 1 到 3 個空白的表格列應算進表;條款欄寫 S3 時,條款解析應不把那一列當成條款定義 [test:t_expected_table_parse]
- [S16] 當任一格改了一個字(含 m² 改成 m2、格內兩個空白改成一個)時表指紋應改變;兩張只差在格裡夾分隔字元位置的表指紋應不同;只改換行符號或格子頭尾空白時表指紋應不變 [test:t_expected_table_fingerprint]
- [S17] 當執行 lumos signoff <計劃> --expected --note <一句> 而表格檢查通過時,應寫一筆 signoff 閘、kind expected-signed 的治理帳事件,帶 plan、table_sha、row_count、origin、who、token、nodes,不寫開頭欄位 signed_off 與 .signoff-log.jsonl;status 是 done 的計劃也能簽;答 y 記 human,沒有互動終端或逾時記 ai 並印記成 AI 簽,答 n 印沒簽、回 1 而且不寫 [test:t_signoff_expected_table]
- [S18] 當表格檢查不過、計劃不需要預期值表簽核、同時帶 --by 或 --ref、或治理帳寫不進去時,lumos signoff --expected 應回 2 而且不寫事件 [test:t_signoff_expected_refuse]
- [S19] 當 pr-evidence 查的計劃在 head 的預期值表檢查不過,或 head 的表指紋不在 head 版本治理帳裡任何一筆同計劃的 expected-signed 事件裡(只在工作目錄、沒提交的簽核不算)時,應回 1、印出簽核指令,並寫一筆 expected-unsigned 事件 [test:t_pr_evidence_expected_unsigned]
- [S20] 當 pr-evidence 放行、對上的最晚一筆簽核事件 origin 是 ai 時,應印一行預期值表由 AI 簽而且不擋;lumos gov --stats 應印出預期值表簽核的人簽與 AI 簽次數,同一個提交簽兩次算兩次 [test:t_pr_evidence_ai_signed]
- [S21] 當門判風險高、生效日之後、至少一條新行為條款的計劃跑規格閘而預期值表檢查不過時,規格閘應擋下(rc1)並逐項列出 [test:t_spec_gate_expected_table_high]
- [S22] 當 CI 的 pull_request 工作流程跑時,應有一步以 PR 的 base 與 head 提交呼叫 lumos pr-evidence [test:t_ci_runs_pr_evidence]

## 回退

三種關法,由輕到重:專案層把 `.lumos/config.json` 的 `pr_evidence.gate` 設成 off(整道不跑,事件照記);全面關掉就把 `_HIGH_RISK_EVIDENCE_SINCE` 設成遠未來(計劃日期兩個來源都讀不到的,仍當生效日之後——要連它們也關,就用前一種開關);CI 那一步拿掉、指令整段拿掉。樹的準備抽成共用函式那一步,修正關卡照舊用它,不跟著退。`signoff --expected` 寫的治理帳事件是追加的,回退後留著無害;`expected-signed`、`base-replay-proven`、`base-replay-failed`、`pr-evidence-skipped`、`expected-unsigned` 五個 kind 留在帳上無害;計劃開頭的 `base_replay_skip` 欄留著無害。第 10 點寫回的說法跟著改回;已經升的版號不倒退,回退本身再升一版。

## 實務隱患
- 已排除:金流:只新增 PR 檢查指令、規格閘的表格檢查與簽核指令,不碰收費或扣款流程
- 已排除:對外送出:不寄信不推播,只讀本機 git、計劃與帳、寫本機治理帳
- 已排除:不可逆:治理帳是追加的;生效常數與專案開關讓既有計劃不受影響,改壞了回退就回來;隔離工作樹離開時收掉
- 守衛面:新增 PR 檢查會擋的兩道(基準重播、預期值簽核)與規格閘的表格檢查,走設計審與代碼審
- 效能:每次 PR 檢查最多開兩棵工作樹(多份計劃共用),只重播這次改到的測試檔裡的新行為測試;本 repo 實測每支每棵約 2.7 秒,Android 冷樹第一次編譯要幾分鐘;單支逾時預設 900 秒,整體上限由 CI 工作的 timeout-minutes 管
- 資源:兩棵工作樹在系統暫存資料夾,離開時收掉,被強殺的殘骸超過一天後同前綴清掉;重播子程序的暫存目錄指到樹底下
- 併發:同一個 PR 連推兩次,CI 既有的 concurrency 設定會取消舊的那次;兩個 PR 同時跑,各自的工作樹資料夾不同
- 誤擋:測試依賴的資料檔不在測試目錄、這次又新增了,分岔點那一棵沒有它,新行為測試會因為缺檔紅——被當成證實(放過);既有行為的測試依賴這次改過的非測試資料檔,對照組可能不綠——記成判不了、不擋
- 天花板一:測試在分岔點紅只證明「它依賴這次的改動」,證明不了它驗得夠細(邊界寫錯照樣過);第二批的變異測試補
- 天花板二:只在 PR 檢查時跑;不開 PR 直接推主線、或消費專案沒有 CI 也沒手動跑,這道不會跑。lumos repo 自己的主線改動都走 PR
- 天花板三:AI 簽的跟人簽的放行效果一樣;這是刻意的(d3),人抽離的程度只能從統計看
- 天花板四:分岔點的紅不分是例外、編譯失敗還是斷言失敗;第二批第 7 點補
- 天花板五:全靠 `[manual:]` 的新行為條款沒有測試可重播,只有預期值表與簽核管它
- 天花板六:對照組在分岔點不綠時記成判不了、不擋——編譯型語言新測試與對照組在同一模組時常發生,這時基準重播實際上沒在擋,只有 `pr-evidence-skipped` 的統計看得到
- 天花板七:壓過提交或 rebase 會讓計劃「第一次進 git 歷史」的日期變新,生效日之前就開始的計劃可能因此被當成新計劃——寧可多查
- 相容:新計劃要照新格式寫預期值表,寫法說明與擋下訊息都附範例;條款欄不加方括號這點擋下訊息要講清楚
REVISIT:2027-02-04 看治理帳:`pr-evidence-skipped` 佔全部重播結果的比例,與其中「對照組不綠」那一類的數量;判不了超過一半就先處理天花板六(第二批的紅因判讀讓編譯失敗的對照組能分辨),再回頭看觸發條件

## 審計修正紀錄

- r1(2026-11-04,4 席:正確性、邊界、整合、架構對齊):68 條/blocking 41 條(席報告總結句:正確性 blocker 1、major 13,邊界 major 15,整合 major 8,架構對齊 major 3)/結論:另寫一套推送前翻帳找紅與讀 Gradle 報告判紅因,誤擋與繞過太多;Enzo 裁換形狀——風險高設計審過後直接套風險低的雙向檢查(d1),紅因判讀移第二批(d2),預期值表改整表簽、條款欄寫裸編號(d5)。
- r1 卷證:`governance/review-reports/高風險測試證據加嚴/`(四份席報告、r1-intake.md 逐條去向)。
- 新增機制前的最小解自問(r1 時的設計,r2 起先紅模式與 `red_first` 已整個拿掉,這行只當歷史):先紅模式不加新指令、新帳欄只有留痕的 `red_first` 一個(不加它,推送前分不出「風險高但已驗先紅」與「風險高只印」的留痕,就得回到翻全部舊帳找紅,r1 已證明那條路誤擋多);簽核用既有 `signoff` 指令加 `--expected` 旗標(不加它,預期值表沒有任何綁內容的簽核紀錄可查)。
- r2(2026-11-04,4 席:正確性、邊界、整合、架構對齊):62 條/blocking 22 條(席報告總結句:正確性 8、邊界 7、整合 6、架構對齊 1)/結論:沿用風險低推送前檢查的接縫裡藏著寫死「風險低」的假設(欄位白名單剝掉 red_first、done 寬待、全靠人驗走小改動閘、已做完短路、測試名互異只對低、判定檔與迴圈編號對不上、首筆帳在乾淨 clone 讀不到);同一類問題連兩輪,Enzo 要求搜世界解後裁換成推送前基準重播(d1 改寫、d6),帳與留痕不再參與判定。
- r2 卷證:`governance/review-reports/高風險測試證據加嚴/`(r2 四份席報告、r2-intake.md)。
- 新增機制前的最小解自問(r2):計劃開頭欄位 `base_replay_skip`(不加它,重播在某些專案環境跑不起來時沒有出口,只剩 `--no-verify`,而那條全域規則不准;世界解 devops-cli 也設了同樣的附理由出口);`signoff --expected` 旗標(不加它,預期值表沒有任何綁內容的簽核紀錄可查)。
- r3(2026-11-04,4 席:正確性、邊界、整合、架構對齊):54 條/blocking 25 條(席報告總結句:正確性 9、邊界 7、整合 6、架構對齊 3,其中 blocker 2 條都是分岔點)/結論:主幹站住、r2 的接縫問題已修好;剩基準重播接上真實推送流程的具體問題——分岔點要跟主線算、樹的準備要跟修正關卡共用、要讀推送版、觸發與程式檔的定義、逾時與合條款要借既有規則、表格縮排列與拆格、開關與生效日。跑滿三輪,Enzo 裁「先做最小實驗再加開第四輪」;實驗確認重播機制可行並量到測試跑紅會留下暫存現場。
- r3 卷證:`governance/review-reports/高風險測試證據加嚴/`(r3 四份席報告、r3-intake.md 含實驗紀錄)。
- 新增機制前的最小解自問(r3):專案層開關 `high_risk_evidence`(不加它,專案遇到重播大量誤擋時只能改程式常數或逐份寫跳過理由;其他會擋的閘都有同樣的開關);重播專用逾時與總預算兩個環境變數(不加它,冷樹第一次編譯會撞到現有 180 秒逾時、上百支測試沒有上限);`_waive_origin_tty` 的兩個選填參數(不加它,簽核訊息會印「沒放行」、30 秒逾時讓讀表的人被記成 AI 簽)。
- r4(2026-11-04,人裁加開,4 席:正確性、邊界、整合、架構對齊):51 條/blocking 19 條(席報告總結句:正確性 8、邊界 4、整合 5、架構對齊 2)/結論:r3 的修補大多到位;剩下的接縫幾乎都來自「放在推送前」(掛鉤與 lumos 版本錯開、推送範圍增量或累計、直推主線、推標籤、冷樹),另有讀推送版治理帳與組筆記物件要借既有的單一來源、全標 keeps 的計劃預期值表死鎖、工具自己出錯變成擋推送。依 Enzo 新定的「同類 major 連兩輪先查方向」查世界:基準重播方向對、但世界都放在 PR 檢查;Enzo 裁「換位置到 PR 檢查(推薦)」(d7)。
- r4 卷證:`governance/review-reports/高風險測試證據加嚴/`(r4 四份席報告、r4-intake.md 含派審前的借用前提核對與世界查證)。
- 新增機制前的最小解自問(r4):`lumos pr-evidence` 新指令(不加它,只能把重播塞進 `spec-gate --push-check`,那是推送前的入口,r3、r4 的接縫都來自那裡);`base-replay-proven` 事件(不加它,證實的計劃跟沒觸發的分不開,回頭條件沒有分母)。
