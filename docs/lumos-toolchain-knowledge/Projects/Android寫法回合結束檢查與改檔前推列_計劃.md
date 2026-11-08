---
type: project
status: done
created: 2026-11-06
updated: 2026-11-06
tags:
  - type/project
  - status/done
  - scope/stack-knowledge
related:
  - "[[Projects/Android寫法寫完當下自動檢查_計劃]]"
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
  - "[[Projects/Android寫法語意情境表態與盲判_計劃]]"
  - "[[Systems/graph-sync-coverage]]"
  - "[[Systems/改檔前推播]]"
  - "[[Systems/hook逾時預算]]"
  - "[[Systems/棧別提問表態閘]]"
  - "[[Systems/pitfalls-code-loop]]"
lands_in:
  - Systems/回合結束寫法檢查
  - Systems/改檔前推播
  - Systems/棧別提問表態閘
  - Systems/hook逾時預算
  - Systems/graph-sync-coverage
  - Systems/pitfalls-code-loop
pending_questions:
  - id: Q1
    text: 收工寫法檢查要不要從既有「同會談只擋一次」延伸成「同一批告警擋一次、同一回合(prompt_id)最多三批、下一回合重算」?建議:要——同一批不重擋已防住永遠解不了的條件,回合內三批上限防卡死(Claude Code 連續八次續做上限會因呼叫工具歸零,不算兜底);只擋一次的話續做時新冒出的另一批告警等到推送才看到
    class: 擋停策略
    stage: 架構
    status: 已決
    blocking: true
    decision: "#d1"
  - id: Q2
    text: 沒有知識圖譜的 Android 專案這一版不推決策列(沿用棧別題同一組條件、不改 impact 找不到圖譜時的 rc3 介面),可以嗎?建議:可以——接 lumos 的消費專案都有圖譜,真遇到沒圖譜的專案再照 REVISIT 改
    class: 範圍
    stage: 需求
    status: 已決
    decision: "#d2"
  - id: Q3
    text: 每次送出提示都多跑一支 Python 鉤子記回合起點,成本可以接受嗎?自答:可以,實測啟動 0.03 到 0.05 秒,沒宣告 ast-grep 的專案讀一個檔就結束
    class: 效能
    stage: 效能
    status: 自答
    source: 本計劃〈實驗〉E10,2026-11-06 實測
decisions:
  - content: Q1:寫法檢查的擋停延伸成同一批告警只擋一次、同一回合(prompt_id)最多三批;下一回合重新計算(設計審 r1 通才 F1 收窄,原寫同一會談)
    id: d1
    context: 既有決策是同會談只擋一次(收工點名);寫法檢查修完一批可能又寫出新的一批
    why_chosen: 編排者依使用者授權原話「我要睡了，你有裁量權、簽核權」代裁,使用者在場可改;只擋一次會讓第二批新告警直接漏過,三批上限避免卡死
    decided: 2026-11-06
    valid: true
  - content: Q2:沒有知識圖譜的 Android 專案這一版先不推決策列,列天花板加 REVISIT
    id: d2
    context: 推列依賴 cmd_impact,沒圖譜回 rc3
    why_chosen: 編排者依使用者授權原話「我要睡了，你有裁量權、簽核權」代裁,使用者在場可改;先把有圖譜的路做穩
    decided: 2026-11-06
    valid: true
---
# Android寫法回合結束檢查與改檔前推列_計劃

> 白話:兩個「寫的當下就提醒」的機制。①**回合結束寫法檢查**:像收工前有人看一眼你這回合寫的程式——AI 每回合要收工時,對「這一回合改過、還沒提交」的檔跑規則包,有新增告警就擋下叫它先修;②**改檔前推相關列**:像動手前遞一張小抄——AI 要改 kt 檔時,把型錄〈情境決策表〉跟這次寫入內容相關的一到三列推到眼前。兩者都從 [[Projects/Android寫法寫完當下自動檢查_計劃]] 第二輪設計審後拆出(2026-11-06)。本版照拆出時留下的十一組待解問題逐組改寫,每組先查官方文件或做實驗再定(見〈待解問題〉與〈實驗〉)。使用者目標原話:「目標是把Android靜態能先掃描的實務隱患都先處理過」。

PRIOR-ART: ①回合邊界:官方鉤子頁對 `prompt_id` 的定義是「UUID identifying the user prompt currently being processed」(https://code.claude.com/docs/en/hooks.md ,共通欄位);`UserPromptSubmit` 在送出提示時觸發。實驗 E1(2.1.319)實測 `claude -p` 與 `--resume` 下送出提示與 Stop 帶同一個 `prompt_id`、續做不再觸發送出提示;**背景任務或排程喚醒的回合觸不觸發送出提示,官方沒寫、本案還沒量**(實驗 E11 列為實作前必跑,行為定義見範圍 2 第 3 條)——採用:提示送出時記回合起點,不再自己用收工時刻推算;不選:SessionStart(一個會談只一次,切不出回合)、逐字稿猜回合開頭(r1 邊界席實測約 15% 首筆沒時間欄)。②擋停迴圈:官方原文「Check this value or process the transcript to avoid blocking on a condition that will never resolve」(Stop input 段);另有連續八次續做上限,但官方寫明這個計數「resets each time Claude calls a tool」,續做修檔一定會呼叫工具,所以它不能當兜底——採用「同一回合(`prompt_id`)裡同一批告警只擋一次、最多三批」當自己的判斷,`stop_hook_active` 那次照查(才查得到續做的修正)。③另開一支收工鉤子:官方說同一事件的鉤子並行跑(同頁),實驗 E2 實測兩支各回 block 時模型兩段理由都收到並照做——採用:寫法檢查開新檔 `stop-lint-hook.py`,不塞進既有收工點名那支(預算各算各的)。④鉤子與 lumos 的介面:沿用 lumos 既有 `--json`「最後一行是 JSON」慣例(收工點名那支呼叫 `impact --json` 就是這樣讀),不用文字解析;(推送前掛鉤的 `LUMOS-BLOCKS:` 是另一條給文字模式用的機讀行,兩者並存、各管各的呼叫端,不是本案的前例。)⑤工作樹改動清單:`git --no-optional-locks status --porcelain=v1 -z`(porcelain 是 git 給程式解析的穩定格式 https://git-scm.com/docs/git-status#_porcelain_format_version_1 ;`--no-optional-locks` 不順手改寫索引 https://git-scm.com/docs/git#Documentation/git.txt---no-optional-locks ;實驗 E4 實測一般 `status` 與 `git diff` 會改寫索引、這個不會)。⑥決策列比對放進棧別提問表態閘已在線上的那一段(`cmd_impact` 算 `stack_questions_applicable` 的地方),讀表、觸發字正規式與 Kotlin 剝註解字串都用盲判那條線建的共用函式(`_kt_decision_table`、`_kt_trigger_re`、`_strip_c_comments(kotlin=True)`),不另建。⑧鉤子共用程式(代碼審 r1 改正):既有鉤子之間共用**有兩種做法、分流規則在 [[Systems/hook信任邊界]]〈2026-09-08 訂正〉**——會讓安全檢查失效的(可信來源解析、逾時預算)每支鉤子留逐字複本、守衛逐字比對;只是功能退化的(標記目錄、標記檔名消毒與 O_EXCL 佔名額、檔名消毒、git 防護)走底線開頭的共用模組(先例 `_hookevent.py`)加 `sys.path.insert` 匯入,複製清單與錨點清單兩道守衛一起加。原寫「只有一種做法」是設計審時沒讀到那篇訂正段;本案照分流規則做,不用 importlib 載另一支鉤子。⑦常用觸發字:資訊檢索的文件頻率概念(出現在太多文件的詞區辨力低,https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html )——採用:拿 Now in Android 310 支 kt 檔量文件頻率,超過 8% 的觸發字列進停用字表。
RETIRE-IF: 回合結束寫法檢查上線後連續三個月治理帳零筆 `stop-lint` 擋下事件,而推送前閘同期照樣擋過新增告警 → 降成只在代碼審通過前跑、拿掉這支鉤子;改檔前推列上線三個月後,對消費專案近三個月 kt 提交的增行離線重播決策列比對,命中列數為零 → 拿掉推列,平均每次 kt 改檔推出超過 2 列 → 觸發字收窄或改成只在代碼審派工材料附列。

## 決策

WHY:寫法檢查開新的一支收工鉤子,不併進收工點名那支 [出處:2026-11-06 實驗 E2、E3;第二輪設計審架構席 ⚠1、資源席 F2、通才席 F6] [因:官方鉤子並行跑、兩支 block 理由都送到模型,拆開後各自佔名額各自輸出、各自時間上限,第二輪的「名額先佔輸出延後」與「時間預算漏項」兩組問題整個消失] [不選:同一支裡兩道並列——要改 `_BUDGET_START` 時點、把上限提到 55 秒,還要擋既有那道的七條提早返回] [代價:多一支註冊、多一次 Python 啟動(約 0.03 到 0.05 秒,實驗 E10)]
WHY:回合起點在送出提示時記,收工時不推進任何狀態 [出處:2026-11-06 實驗 E1;第二輪通才 F3、F5,邊界 F1、F2,資源 F1、F9] [因:`claude -p` 這種單回合會談也有送出提示事件,第一次收工就查得到;收工不寫時間戳,續做那輪改的檔在續做的收工照樣落在回合起點之後] [不選:收工時寫時間戳、第一次收工不查——單回合會談永遠不被查,S7 手動驗收照字面跑不過]
WHY:檔集仍以工作樹狀態為底(問版本控制;代碼審 r3 起不跑 `git status`,改走只用不經內容過濾器的 git 指令的 `_wt_changed_nofilter`),再用修改時間不早於回合起點收窄,承接 2026-09-18 收工點名改問版本控制的決策,不是翻案 [出處:[[Systems/graph-sync-coverage]] 2026-09-18 那條;第二輪架構席 F3] [因:09-18 否決的是「從逐字稿列舉工具名」(漏 shell 寫的檔),本案底集照樣問版本控制、shell 寫的檔照樣看得到;收窄是因為新增告警要先分出「這回合碰過的」,否則每個新會談第一回合都會被前人留下的未提交改動擋一次] [代價:時間戳被保留成舊值的檔(`mv`、`cp -p`)漏掉,見〈天花板〉]
WHY:決策列比對併進棧別提問那條通道,不另起剝字串與觸發比對 [出處:第二輪架構席 F1、F2,邊界席 F8] [因:`cmd_impact` 已在同一段對 kt 編輯跑棧別題觸發比對、由鉤子印;決策列放同一段、同一組啟用條件,剝字串與觸發式用盲判那條線建在主程式的共用函式,只多一個輸出鍵 `decision_rows`(列要帶編號給鉤子去重,題目沒有)] [不選:本案自己寫 Kotlin 剝字串或觸發比對(`_strip_c_comments` 註明全庫只此一個入口)、另一條平行通道]
WHY:擋停上限與去重綁回合(會談加 `prompt_id`),不綁整個會談 [出處:本篇設計審 r1 通才席 F1;官方 `prompt_id` 定義] [因:綁會談時一個長會談第一回合用光三批,之後每回合都不檢查;同一批告警在後面回合重現也永遠不擋] [不選:每次送出提示清掉本會談的標記——要多寫一個刪檔動作,而且跟「只有擋過的會談才留標記」的既有性質打架]
WHY:同一回合 `stop_hook_active` 為真照樣檢查,翻掉 [[Projects/README審視五修_計劃]] d2 那句「stop_hook_active 兩家語意相同(已續做過=不再擋)」在本道的適用 [出處:該篇 d2;本篇設計審 r1 依據席 F5;決策 d1] [因:那句是給收工點名那道的(點名只要提醒一次);寫法檢查要查得到續做時的修正與新冒出的另一批,續做那次不查就等於修完不驗。防迴圈改靠同批不重擋加每回合三批上限,不靠 `stop_hook_active`] [代價:同一回合最多多擋兩次]
WHY:記帳由鉤子在真的擋下、輸出寫出去之後才做 [出處:本篇設計審 r1 通才席 F2;既有「判定函式只回傳、帳由呼叫層寫」慣例] [因:`lint-new` 判 blocked 時鉤子還可能因同批或上限而不擋,在 lint-new 裡記會把一次擋下記成多筆,RETIRE-IF 量的「零筆」永遠不會成立] [不選:lint-new 帶 `--record-gate` 自己記(原設計)] [代價:真的擋下時多一次 lumos 啟動,約 0.8 秒,只發生在擋下那次]
WHY:鉤子共用程式搬進底線開頭的共用模組 `_hookshared.py`,走 `sys.path.insert` 匯入 [出處:本篇設計審 r1 架構對齊席 F1;既有 `_hookevent.py` 做法] [因:不加它的最小解是「新鉤子用 importlib 載 `check-graph-sync.py`」,但 `scripts/hooks/claude/` 沒有任何鉤子這樣做,而且會連帶帶起那支的模組層狀態(例如 `_BUDGET_START`);另一個最小解「抄一份」則是那支檔註解記過「邏輯抄一份、一邊改另一邊沒跟上」吃過虧] [代價:`check-graph-sync.py` 要改成從共用模組匯入,它的既有測試要跟著確認]

## 用詞

- **回合起點**:這一回合使用者送出提示的時刻。新鉤子在每一次 `UserPromptSubmit` 都把 `{prompt_id, 時刻}` 寫到 `~/.cache/lumos/stop-turn/<會談>`,不看當下目錄有沒有 `.lumos/lint.json`(會談中途用工作樹切到有宣告的 repo 時也有起點;目錄用共用模組的 `_cache_dir_under_home` 建、同一個信任檢查與七天清理)。收工時只讀不寫。
- **這一回合碰過的檔**:工作樹上有未提交改動(`git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` 列得到、不是刪除)而且修改時間不早於回合起點的程式碼檔;`.lumos/` 底下的一律不算(含新增告警閘的快照暫存 `.lumos/lintbase-*`)。由 lumos 算(`lint-new --since`),鉤子不自己列檔。
- **工作樹檢查**:`lumos lint-new --worktree`:基準是 HEAD 那一版、現在版直接讀工作樹的檔,跑新增告警比對。新增告警閘本體見 [[Systems/pitfalls-code-loop]]。
- **一批告警、批次雜湊**:一次工作樹檢查新增告警的指紋多重集合(同一指紋出現幾次也算),排序後串起來取 sha256 前 16 碼。由 lumos 算、放進 JSON,鉤子不重算。
- **自動執行白名單**:回合結束只准跑的宣告命令形狀,寫死在 lumos、不讀專案設定(被打開的專案自己的設定不可信)。判法見範圍 1 第 5 條。
- **工具鏈根**:主程式 `_kt_toolchain_root()` 回的目錄(盲判那條線建的):執行中那支 `scripts/lumos` 往上兩層(`Path(__file__).resolve().parent.parent`),那裡有 `skills/lumos-project-notes` 就是它;沒有(被複製進消費專案)就退回 `_lumos_src()`(`LUMOS_HOME` 或 `~/harness/lumos-toolchain`)。白名單比對前再取一次真實路徑。這樣被複製進專案的那份 lumos 不會把專案自己當成可信根。
- **規則包**:`configs/ast-grep/kotlin-android/` 底下的 ast-grep 規則與它的 `sgconfig.yml`(第一批 [[Projects/Android協程與API寫法機械檢查標準_計劃]] 做的)。
- **收工點名**:既有收工鉤子 `scripts/hooks/claude/check-graph-sync.py`(改了程式沒動筆記就點名、同會談擋一次),見 [[Systems/graph-sync-coverage]]。本案新鉤子跟它並列,不改它。
- **冷卻窗**:改檔前鉤子 `impact-hook.py` 既有的機制:同一會談同一支檔 20 分鐘內再改,只跑事故比對的快速路徑(`--incidents-only`),不跑完整影響推播,見 [[Systems/改檔前推播]]。
- **新增告警閘的狀態與退出碼**:`_lint_new_verdict` 的八種狀態,`lint-new` 照它分三類——擋(blocked)rc1;乾淨或刻意不查(clean、warn、off、no-config、no-files)rc0;沒檢查到(not-checked:宣告的命令一條都沒跑;env-unavailable:工具沒裝或逾時)rc3;參數錯 rc2。
- **席位代號**:「第二輪通才席 F3」這類寫法指設計審卷證 `governance/review-reports/android寫法寫完當下自動檢查/r2-<席>-sonnet.md` 裡那一條;本篇自己的設計審卷證在 `governance/review-reports/android寫法回合結束檢查與改檔前推列/`。
- **決策列**:型錄 `skills/kotlin-idioms/checks-catalog.md`〈情境決策表〉的一列,第一欄 `D-<n>`。
- **觸發字比對 `_kt_trigger_re`**:照 [[Projects/Android寫法語意情境表態與盲判_計劃]]〈用詞〉「候選列」那條的定義(本案改採它,兩案一致):觸發字 `re.escape`;只在觸發字開頭是英數或底線時要求前一個字元不是英數或底線,只在結尾是英數或底線時要求後一個字元不是英數或底線;分大小寫。**歸屬盲判那條線**:已建在它的工作樹 `android-situation-evidence` 的 `scripts/lumos`,位置在 `_kt_decision_table` 下面,回正規式字串;本案只呼叫、不建、不測它本身。

## 範圍(做)

0. **開工方式(相依)**:白名單的工具鏈根、決策表讀表、觸發字正規式、Kotlin 剝註解字串都在盲判那條線的分支 `EnzoHsieh-Android/android-situation-evidence`。照編排者裁決(使用者 2026-11-06:主線不會再動、全部做完再一起推):實作在本機整合分支上進行——**先把那條分支合進來再開工**,不另寫同名函式、不等主線;範圍 1 到 3 都在合進來之後做。
1. **`lint-new` 多一個工作樹模式**(`scripts/lumos`):
   1. 旗標:`--worktree`、`--since <epoch 秒>`、`--json`、`--pgid-file <路徑>`(工具群組登記檔,見第 7 條)、`--budget <秒>`(新增;現在的 `lint-new` 沒有這個旗標,鉤子照舊帶會被參數解析擋成 rc2)。`--budget` 兩種模式都收:覆寫設定檔 `lint_new.budget_sec`(預設 300),從指令一開始起算,要是正數,0、負數或不是數字 rc2;不給照設定檔。`--diff` 與 `--worktree` 恰好給一個,都給或都沒給 rc2;`--since`、`--pgid-file` 只能跟 `--worktree` 一起給,否則 rc2。判定函式 `_lint_new_verdict` 多一個明示參數「終點是工作樹」,不走「終點解不出來 → 環境不可用」那條既有路徑(那條照舊)。
   2. 改動清單:新寫解析函式 `_porcelain_v1_entries(raw)` → `[(X, Y, 路徑, 舊路徑或 None)]`:X 或 Y 任一格是 `R`、`C` 都多吃一欄舊路徑(實驗 E6:`git add -N` 加 `mv` 會出 ` R 新|舊|`,R 在第二格)。既有 `_porcelain_z_paths` 已會吃舊路徑,但只回路徑、丟掉狀態碼與舊路徑,本案三樣都要;所以把切欄邏輯搬進新函式,`_porcelain_z_paths` 改成呼叫它再只取路徑(長度不到 4 的片段照舊略過),它的兩個既有呼叫端行為不變、既有測試釘住。另兩處自己解 porcelain 而且要狀態碼的 `_tg_rb_pending`、`_handoff_files` 也改成呼叫新函式(這樣帶狀態碼的解析只剩一份,不是從兩份變三份),兩處既有行為不變、既有測試釘住。衝突(任一格 `U`,或 `AA`、`DD`)不掃、列成「衝突中、沒檢查」。基準:`R`/`C` 沿著舊路徑**追回 HEAD 有的那一端**——舊路徑本身在 HEAD 有就用它;沒有就看它是不是清單裡另一筆改名的新路徑(先 `git mv` 再 `mv` 再 `git add -N` 會出兩筆串起來的 `R  b/Foo.kt|a/Foo.kt|` 與 ` R b/Foo2.kt|b/Foo.kt|`,第二筆的舊路徑只在索引裡),是就繼續往回追(最多追清單筆數那麼多步,遇到重複就停);追不到才算基準為空,並在 JSON 的 `skipped` 與人讀輸出列「改名追不到原檔,整支當新檔」。工作樹上已不存在的「新路徑」(鏈的中間那一端)不掃;`??` 與 `A`(HEAD 沒有這支)基準為空,但同一份清單裡有已刪除(`D`)的檔、檔名(不含目錄)相同而且唯一時,拿那支的 HEAD 內容當基準(搬套件會改 `package` 行);讀基準用一次 `git cat-file --batch`。
   3. 整次不檢查、rc3 的情況(各印一句原因):repo 正在合併、rebase、cherry-pick 或 revert(`git rev-parse --git-path` 找 `MERGE_HEAD` 等);沒有 HEAD;宣告檔不乾淨——`git cat-file -e HEAD:.lumos/lint.json` 失敗,或 `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all --ignored=matching -- .lumos/lint.json .lumos/config.json` 有任何輸出(實驗 E5:這樣未追蹤 `??`、被忽略 `!!`、有修改都抓得到,而且不改寫索引;不用 `git diff --quiet`,實驗 E4 實測它帶了 `--no-optional-locks` 照樣改寫索引);碰過的檔超過 50 支(印「這回合改了太多檔,留給推送前閘」)。代碼審 r3 起:「沒有 HEAD」只認 `rev-parse --verify -q HEAD` 回 1,其他退出碼(git 出錯)算沒能檢查(`failed`);宣告檔在不在 HEAD 改用 `ls-tree` 問(成功而且沒輸出才是不在),乾不乾淨改走不跑 status 的 `_wt_changed_nofilter` 加 `ls-files -o -i --exclude-standard`(status 會經內容過濾器)。
   4. 給 `--since` 時只看「這一回合碰過的檔」;交集是空的 → no-files(rc0)。所有 git 呼叫都帶 `--no-optional-locks`;路徑一律相對 `git rev-parse --show-toplevel`。
   5. **自動執行白名單**(只在工作樹模式套用):`shlex` 切詞後——第一個詞恰好是 `ast-grep`;第二個是 `scan`;恰好一個 `--config`/`-c`,它的值只能是絕對路徑或以 `$HOME/`、`${HOME}/` 開頭(這是整條命令唯一准出現 `$` 的地方),把開頭那段換成 `os.path.expanduser("~")` 後取 `os.path.realpath`,要落在 `<工具鏈根>/configs/ast-grep/` 底下(用 `os.path.commonpath` 比,實驗 E7:字串前綴擋不住 `..` 與符號連結,真實路徑擋得住);其餘每個詞只能是 `{LINT_FILES}`、`{LINT_FILES_CSV}`、`--format`/`--json`(含 `=值`)及其值、`--filter`、`--globs` 及其值,外加恰好一個 `>` 接 `{LINT_SARIF_OUT}`;`--config` 值以外不得含 `;`、`|`、`&`、反引號、`$`、`<`、`>>`、`*`、`?`、`~`、換行;`-U`、`--update-all`、`-i`、`--interactive`、`--custom-languages` 一律不准。通過的命令在送進既有 `_lint_spawn`(shell 執行)之前,把 `--config` 的值換成 `shlex.quote(真實路徑)`,所以送出去的命令不含 `$`。不合的命令列成「工作樹模式不跑」;一條都沒跑時是 not-checked(rc3),不是 clean。依賴層 `lint-deps.json` 工作樹模式全部不跑。路徑大小寫:macOS 預設檔案系統不分大小寫,`realpath` 不校正大小寫,`commonpath` 卻分大小寫比;所以「真實路徑字面對不上、但用 `os.path.samefile` 比 `configs/ast-grep/` 這一層是同一個目錄」時照樣擋,原因另印一句「設定檔路徑大小寫跟工具鏈實際目錄不同(例如 `harness` 對 `Harness`),照實際大小寫改宣告」。換進 `{LINT_FILES}`、`{LINT_FILES_CSV}` 的每個相對路徑在工作樹模式一律加 `./` 前綴,`-` 開頭的檔名不會被 ast-grep 當成選項。
   6. 作弊比對要兩個提交,工作樹模式不跑,輸出註明「作弊比對留給推送前閘」。單條命令保底:既有設定 `per_cmd_floor_sec` 預設 30 秒(剩餘預算不到它就不跑那條),鉤子給的預算約 19 秒,照用會每條都不跑、永遠 rc3;所以工作樹模式改用程式常數 `_LINT_NEW_WORKTREE_FLOOR_SEC = 1`,不讀設定檔的 `per_cmd_floor_sec`(專案設定不能讓收工那道永遠不跑);`--diff` 模式照舊 30 秒。預算不夠沒跑到的命令在工作樹模式歸「沒檢查到」(rc3),不擋。
   7. **收尾**(主程式現在沒有任何訊號處理器,這是新慣例,記進 [[Systems/hook逾時預算]]):工作樹模式一進來就先裝 SIGTERM 處理器,再做任何開程序或建快照的事。開每個檢查工具時用 `signal.pthread_sigmask` 先擋住 SIGTERM,`_lint_spawn` 開出程序(既有,`start_new_session=True`,所以工具在自己的程序群組)後**先登記再解除擋住**:登記兩處——模組層清單,以及鉤子用 `--pgid-file <路徑>` 指定的檔(一行一個群組編號,寫完 flush);工具結束就從兩處拿掉。處理器對清單裡每個群組呼叫既有 `_kill_proc_group`——它**直接送 SIGKILL、沒有寬限**,刻意照用:檢查工具是唯讀掃描,沒有要它自己收的東西,結果檔是 lint-new 開的暫存 SARIF、由 lint-new 自己刪;接著刪掉這次的快照目錄,印「被中止」後 rc3。寬限只放在上一層(鉤子對 lint-new 先 SIGTERM、1 秒寬限讓它自己收),寬限過了還在,鉤子自己去打登記檔裡的工具群組(見範圍 2 第 4 條)。不加登記檔的最小解是「只靠 lint-new 的處理器」,不夠:處理器沒跑完就被 SIGKILL 時,工具在新 session 裡,鉤子殺 lint-new 的群組打不到它們(本篇設計審 r1 可行性席 F2)。
   8. `--json`:人讀訊息照印到 stderr;stdout 最後一行是一個 JSON 物件 `{status, rc_class, batch, total, new:[{file, line, rule, message, fp, waive_cmd}], undone:[…], skipped:[…], reason, unchecked_kind}`,`new` 是全部新增告警(不受 20 條顯示上限),`batch` 是批次雜湊;`unchecked_kind` 只在 rc3 時有值:`deliberate`(刻意不查)、`timeout`(時間預算或參數長度不夠沒跑到)、`failed`(沒能檢查),判定裡沒寫明的 rc3 一律 `failed`(代碼審 r2 乙組)。
   9. **記帳**:工作樹檢查本身不寫帳。另給一個只記帳的用法 `lumos lint-new --record-stop-block <批次雜湊> --count <條數> --prompt <prompt_id> --repo <根>`(跟 `--diff`、`--worktree` 互斥,其餘旗標一概不收),用既有 `_gate_event_or_warn` 寫一筆 `stop-lint` 擋下事件就結束、rc0;`stop-lint` 登記進 `_KNOWN_GATES`。只由鉤子在真的擋下、輸出寫出去之後呼叫(範圍 2 第 6 條)。這是「`lint-new` 不寫治理帳」的唯一例外。不加這個用法的最小解是「鉤子自己寫治理帳檔」,不夠:帳的格式與寫入規則在 `_gate_event` 一處,鉤子不能匯入主程式,抄一份就是第二個寫帳者。
2. **新鉤子 `scripts/hooks/claude/stop-lint-hook.py`**,註冊在 `UserPromptSubmit` 與 `Stop` 兩個事件(同一支檔,依 payload 的 `hook_event_name` 分流;註冊命令由 `_hook_cmd` 產生,會帶 `--budget 30`,Codex 目標另帶 `--harness codex`,鉤子只讀 `--budget`、其他參數一律忽略)。**登記點全列**(漏一處就有既有守衛翻紅或靜默失效):①`merge-claude-settings.py` 的 `HOOK_BUDGET` 新增一值 30 秒與兩個事件的註冊;②主程式 `_GLOBAL_CLAUDE_HOOKS`(否則 `_prune_dangling` 剪掉註冊);③主程式 `_VENDORED_TREE_FILES`(有測試逐檔比對 `scripts/hooks` 底下受版控的檔,少登記會翻紅,消費專案裡這支也會被推送閘當成產品碼)——新鉤子與新共用模組 `_hookshared.py` 兩支都要登記;④`enforcement_status` 裡 Claude 與 Codex 兩份寫死的存活清單各加一行(`stop-lint-hook`、`codex-stop-lint-hook`);⑤`__main__` 用 `_hookevent.guard("stop-lint-hook", __file__, main)` 包住 `main`(照 `check-graph-sync.py`),跑完、逾時、出錯才記得到。**共用程式**:`_cache_dir_under_home`、`_mkdir_under_home`、`_stop_dir_ok`、`_safe_path`、`_trusted_lumos`、`_harden_git_env`(含 `_GIT_UNSAFE_CONFIG`)、`_outer_budget`、`_inner_budget` 從 `check-graph-sync.py` 搬進新共用模組 `scripts/hooks/claude/_hookshared.py`(只用標準庫、不做任何模組層 I/O),兩支鉤子都 `sys.path.insert` 本目錄後 `from _hookshared import …`;`check-graph-sync.py` 照名字匯入回來,外部看到的名字不變。實作時先搜它的既有測試有沒有替換這幾個名字(替換 `cgs._stop_dir_ok` 這種寫法搬家後打不到共用模組裡的呼叫),有就改成替換共用模組那邊;搬完它的既有測試全綠。匯入失敗整支靜默結束(rc0)。`main()` 在預篩過後第一件事呼叫一次 `_inner_budget()`(它的起算點第一次呼叫才記);外層秒數由它從 `sys.argv` 的 `--budget` 讀,預設給 30。
   1. **找專案與預篩(收工時才做)**:先只用標準庫做:專案根取 `CLAUDE_PROJECT_DIR` 或 payload 的 `cwd`,往上找第一個有 `.git` 的目錄當 repo 根;repo 根沒有 `.lumos/lint.json`,或檔裡沒有 `ast-grep` 字樣(只是省一次 lumos 啟動的預篩,不是安全判斷),整支靜默結束——**預篩在匯入共用模組之前**,沒宣告的專案每次收工只付 Python 啟動加讀一個檔。
   2. **送出提示時**:每一次都記(不預篩 repo):匯入共用模組,會談編號非空、目錄過信任檢查,就覆寫 `stop-turn/<會談>`(先寫暫存檔再 `os.replace`);不輸出任何東西、rc0。共用模組只用標準庫,匯入成本由實驗 E12 量(實作時跑,超過 0.1 秒就把送出提示這條路改成不匯入、只用標準庫寫檔)。
   3. **收工時**:條件依序——`LUMOS_STOP_LINT_OFF` 與 `LUMOS_STOP_BLOCK_OFF` 都不是 1;會談編號非空;讀得到 `stop-turn/<會談>`;payload 有 `prompt_id` 而且跟紀錄相同。**payload 缺 `prompt_id` 一律當對不上**。對不上或沒紀錄:stderr 印一行「這回合沒記到起點,不檢查」——payload 的 `background_tasks` 或 `session_crons` 非空時這行改成「這回合是背景工作或排程喚醒的,沒記到起點,不檢查」(官方 Stop 段說這兩個欄位是用來分辨這類回合的),然後結束。這類回合到底有沒有送出提示事件、帶的是新的還是舊的 `prompt_id`,由實驗 E11 量;若量到它們帶舊的 `prompt_id` 而且跟紀錄相同,起點會落在上一個使用者提示的時刻,多算前一回合碰過的檔——那是多查不是漏查,照樣進同一套去重。**`stop_hook_active` 為真照樣查**(理由見〈決策〉,防迴圈靠下面的批次去重與每回合上限)。
   4. 呼叫 `<可信 lumos> lint-new --worktree --since <起點> --json --pgid-file <stop-turn/<會談>.pgids> --repo <repo 根> --budget <內層-2,至少 1>`,先 `_harden_git_env()`,子程序 `start_new_session=True`。等到內層時限(30 × 0.7 − 已耗)它仍在跑:對 lint-new 的群組送 SIGTERM、給 1 秒寬限讓它自己收;寬限過了還在,就對 lint-new 的群組和登記檔裡每個群組都送 SIGKILL(送之前確認那個群組編號仍是存活程序的群組,`os.killpg(g, 0)` 不丟例外才送),刪掉登記檔,這次不擋。鉤子自己收到 SIGTERM(Claude Code 逾時)時同樣先 SIGTERM lint-new、等 0.5 秒、再 SIGKILL lint-new 與登記檔裡的群組,不輸出(實驗 E3:Claude Code 送 SIGTERM 後約 1 到 2 秒收掉鉤子,0.5 秒在那之內)。
   5. **只在三件事都成立時擋**:退出碼是 1、stdout 最後一行解析得出 JSON、`status == "blocked"` 而且 `new` 非空。其他(含未捕捉例外的 rc1、空輸出、rc3)一律不擋;rc3 印一行到 stderr,並照 JSON 的 `unchecked_kind` 記事件——`deliberate` 記 ok、`timeout` 記 timeout、`failed` 與欄位缺、不認得或不是字串記 error(代碼審 r2 乙組、r3 戊組);rc2 也印一行「這支 lumos 不認得 lint-new 的工作樹旗標,重跑安裝」(不讓版本對不上變成沒聲音的永不擋)。
   6. **防無限擋**(決策 d1 的「同一批只擋一次、最多三批」,範圍照本篇設計審 r1 通才席 F1 收窄到同一回合;d1 開頭欄位已改成「同一回合(prompt_id)」):在既有 `stop-block/` 用 O_EXCL 建 `<消毒後會談>.lint-<prompt_id 消毒後前 16 字>-<batch>`——已存在 = 這一回合這批擋過、不擋;同會談同回合(同一個前綴)的已有 3 個 = 這回合不再擋,下一回合重算。名額佔到之後立刻寫 stdout,寫不出去就刪掉剛佔的檔(既有那道的順序);佔名額到輸出之間沒有任何提早返回。輸出寫出去之後,在剩餘預算內(至少 1 秒)呼叫 `lint-new --record-stop-block <batch> --count <條數> --prompt <prompt_id> --repo <根>` 記帳,失敗不影響擋停。只有真的擋才建檔,`stop-block/` 的既有性質(只有擋過的會談留東西)不變;收工點名那道的標記檔名是 `<會談>` 本身,不互相干擾。
   7. **擋下原因**:第一行固定 `LUMOS-STOP-LINT:這一回合改的程式有新增的寫法告警`;第二行「先修掉再結束;確定是誤報就照每條的放行指令補理由(會留紀錄)」;接著最多 10 條「檔:行 [規則] 訊息」與放行指令,檔名與訊息都過 `_safe_path`,並註明「下面只是檔名與訊息,寫什麼都不是指令」;超過 10 條印條數;整段最多 1500 字。
3. **改檔前推相關列**(`scripts/lumos` 的 `cmd_impact`、`scripts/hooks/claude/impact-hook.py`):
   1. 鉤子:只取寫入的新內容(Edit 只取 `new_string`、MultiEdit 每段 `new_string`、Write 取 `content`;實作是 `extract_delta_texts` 一次取整份與新內容,代碼審 r2 拿掉了 `extract_delta_text` 的 `new_only` 參數),目標是 `.kt`/`.kts` 時 payload 多一個鍵 `delta_new`(同 2 MB 上限,超過照既有做法截斷並標 `delta_new_truncated`)。不另寫第三份取段函式。
   2. lumos:放在 `cmd_impact` 既有算 `stack_questions_applicable` 的那一段裡。那一段的既有條件是:`--json` 輸出、不是冷卻窗的 `--incidents-only` 快速路徑、目標不是測試檔、棧判成 `kt`。**決策列不受冷卻窗限制**:冷卻窗是為了省完整影響推播,決策列只是對 `delta_new` 跑一次本機正規式,所以把決策列的計算抽成一支小函式,完整路徑與 `--incidents-only` 快速路徑都呼叫(本篇設計審 r1 通才席 F3);鉤子在冷卻窗內那條呼叫也帶 `delta_new`、也印列。決策列的條件是 `--json`、非測試檔、棧 `kt`,再加三條——payload 的 `delta_new` 是字串、這支檔沒被判成伺服端 Kotlin(`_stack_platform_excluded` 回的是要拿掉的題號集合,不是整檔排除;決策列不是題,所以判法定成「集合裡不含 `kt-compose`」——用 `kt-compose` 是因為它是既有題表裡固定存在、標 `android_only` 的題,不像盲判那條線的 `kt-situation` 只在決策表讀得到時才加進題表;含 `kt-compose` 就是這支檔判成全伺服端)、決策表讀得到。算法:整段 `delta_new` 先過 `_strip_c_comments(…, blank_strings=True, keep_newlines=True, kotlin=True)`(盲判那條線加的 Kotlin 模式:巢狀區塊註解、字串樣板 `${…}` 裡的程式碼照算),再用每列每個觸發字的 `_kt_trigger_re` 比;停用列(`retired`)跳過;一列命中至少一個觸發字就算,照命中的不同觸發字數多寡、再照表序,最多回 10 列 `[{id, situation, standard, alt, hits}]`(欄名照 `_kt_decision_table` 的列字典)。
   3. 讀表:**歸屬盲判那條線**,本案只呼叫。它已在 `android-situation-evidence` 工作樹的 `scripts/lumos` 建好 `_kt_decision_table(path=None)` → `(列清單, 問題或 None)`,透過共用的 `_load_hook_file` 借用規則包自檢程式 `check.py` 新增的 `dt_table`(依表頭名稱取欄;既有的 `catalog_problems` 是固定 7 欄依欄序讀,`_cells`、`dt_triggers` 是兩邊共用的切格與觸發字解析);模組載入時讀一次存成 `_KT_DT_ROWS`、`_KT_DT_ERR`。本案用那兩個值:有錯就不推、不報錯(型錄讀不到的提醒歸盲判那條線印)。
   4. 鉤子印列:在既有印棧別題那一段之後,逐列用既有 `_voice_once(會談, "row-<D-n>")`,取前三列沒推過的印「[決策表 D-n] 情境|標準寫法|不適用時」;既有「影響脈絡是空就不印」那條判空改成也看 `decision_rows`(有要印的列就印)。沒印出的列下次還能推。判空要改的是鉤子這邊(`_ranked_ctx` 那條「results、棧別題、lane 都空就不注入」再加看 `decision_rows`),不是 lumos 那一段。標記檔落在 `<系統暫存目錄>/lumos-impact-<會談>/voice-row-D-n`;清理靠既有 `_ttl_lazy_cleanup`:每次改檔前鉤子跑時,刪掉目錄本身修改時間超過 24 小時的 `lumos-impact-*` 目錄——所以是「這個會談最後一次新增標記後 24 小時」整個目錄一起清,不是每個標記各算 24 小時。
   5. 型錄停用字:型錄格式檢查的 `STOP_TRIGGERS` 加 `Composable`、`Inject`、`Modifier`(實驗 E9:在 Now in Android 310 支 kt 檔的文件頻率 15.5%、14.5%、9.4%,超過 8% 門檻),D-33、D-34、D-39 的觸發字同批改寫成較專一的字(或寫「(無)」)。門檻管的是字、不是列:D-49 以列計 10%,但它每個觸發字都低於 8%(最高 `runTest` 6.8%),不改;列太常推的情況交 RETIRE-IF 的「平均每次推出超過 2 列」量。
4. **筆記**:新開 [[Systems/回合結束寫法檢查]](`--code scripts/hooks/claude/stop-lint-hook.py --code scripts/hooks/claude/_hookshared.py`,共用模組的家也在這篇,負責:回合起點紀錄、收工呼叫工作樹檢查與擋停;不負責:新增告警判定本體、收工點名);[[Systems/hook逾時預算]] 記新一值 30 秒與「這支逾時要殺子程序」的例外(它不快取、結果過時就作廢,跟該篇「超時放手」那條針對的派工鏡頭快取不同);[[Systems/graph-sync-coverage]] 記兩支收工鉤子檔集定義的差別;[[Systems/改檔前推播]]、[[Systems/棧別提問表態閘]] 記 `decision_rows`;[[Systems/pitfalls-code-loop]] 只留指向新篇的連結。

## 不做

- 推送前閘與 `lint-new --diff` 的判定結果不變(範圍 1 加的是明示參數與旗標,既有測試釘住)。
- 不在收工鉤子裡呼叫模型;收工不跑白名單以外的命令(detekt 等等代碼審通過前或推送前閘)。
- 既有收工點名那支(`check-graph-sync.py`)行為與 40 秒上限不動。
- 專案沒有知識圖譜時不推決策列(決策 d2;沿用棧別題同一組條件;見〈天花板〉與 REVISIT)。
- 不新增第二份帶狀態碼的 porcelain 解析:`_porcelain_z_paths`、`_tg_rb_pending`、`_handoff_files` 三處都改走新函式(範圍 1 第 2 條)。
- 不新寫 Kotlin 剝字串、讀決策表、觸發字正規式或工具鏈根的函式:四支都歸盲判那條線([[Projects/Android寫法語意情境表態與盲判_計劃]]),本案在合進那條分支後才開工。

## 待解問題(第二輪設計審四席十一組)→ 處理

1. **自動執行白名單繞得過、正例自相矛盾** → 已處理(範圍 1 第 5 條):`--config` 值取真實路徑後用 `commonpath` 比,落在 `<工具鏈根>/configs/ast-grep/`;`$HOME` 只准出現在 `--config` 值開頭;正例改用 `linter精選目錄` 的真實範本;工具鏈根定成主程式 `_kt_toolchain_root()` 回的目錄。依據:實驗 E7、Python `os.path.realpath`/`commonpath` 官方文件。
2. **回合邊界算法有洞** → 已處理(用詞「回合起點」、範圍 2 第 2、3 條):改在 `UserPromptSubmit` 記起點、收工只讀不寫;`stop_hook_active` 那次照查;rc3 或被殺不會推進任何狀態。依據:官方鉤子文件、實驗 E1(`-p` 也觸發、續做不再觸發送出提示、`prompt_id` 不變)。
3. **鉤子與 `lint-new` 之間沒有機讀介面** → 已處理(範圍 1 第 8 條、範圍 2 第 5 條):`--json` 最後一行帶全部指紋與批次雜湊;鉤子只在 rc1+JSON+blocked 三者都成立時擋,例外的 rc1 不擋。依據:lumos 既有 `--json` 慣例、`LUMOS-BLOCKS:` 前例。
4. **擋停名額先佔、輸出延後會永久遺失** → 已處理:寫法檢查拆成獨立鉤子,佔名額後立刻輸出、寫不出就退名額,中間沒有提早返回。依據:實驗 E2(兩支並行、兩段理由都送到)。
5. **時間預算算式漏項** → 已處理:不再跟既有那道共用預算。新鉤子 30 秒上限、內層 21 秒、子程序逾時 SIGTERM 加 1 秒 SIGKILL,最壞約 22.5 秒加啟動,離 Claude Code 送 SIGTERM 的 30 秒留 7 秒;既有那道 40 秒照舊、跟它並行,使用者等的是兩者較長的那個。依據:實驗 E2、E3(逾時送 SIGTERM、不理會約 1 到 2 秒內被收掉)。
6. **git 呼叫細節** → 已處理(範圍 1 第 2、3、4 條):宣告檔改用帶 `--ignored=matching` 的 `status` 判;不用 `git diff --quiet`;新寫的解析函式誠實標成新寫,R 在任一格都吃舊路徑;`A` 跟 `??` 同一套基準;`.lumos/` 由 lumos 端排除、鉤子不列檔。依據:實驗 E4、E5、E6。
7. **另起第二套做法** → 已處理:不寫 `_kotlin_strip`(用盲判那條線在既有 `_strip_c_comments` 加的 `kotlin=True` 模式);決策列放進棧別題那一段(同一組啟用條件,另加三條,見範圍 3 第 2 條;不是呼叫 `_stack_applicability` 本身,那支用預編好的題目樣式);檔集承接 09-18 決策(〈決策〉第三條);SIGTERM 收尾用既有 `_kill_proc_group`;`delta_new` 是既有取段函式加參數;讀表與觸發字正規式用盲判那條線建的 `_kt_decision_table`、`_kt_trigger_re`;觸發字邊界兩案統一採第三批的定義。
8. **改檔前推列細節** → 已處理:沒圖譜時不推(不改 `cmd_impact` 的 rc3 介面,列成天花板;2026-11-06 裁定為決策 d2);常用字改用語料量文件頻率決定停用字(實驗 E9),型錄三列同批改寫。
9. **鉤子取檔與專案根** → 已處理:鉤子不自己跑 `git status`,檔清單全在 lumos 用 `-z` 算;擋下原因的檔名與訊息過 `_safe_path`;鉤子往上找 `.git` 定 repo 根並帶 `--repo`;沒有 `ast-grep` 字樣的宣告不啟動 lumos。
10. **決策關係沒寫明** → 已處理:「同會談只擋一次」與「stop_hook_active 為真不再擋」出自 [[Projects/README審視五修_計劃]] d2,針對收工點名那道;本案新道「同一回合同批一次、最多三批、續做照查」是對它在本道的翻案,理由見〈決策〉;2026-11-06 裁定為決策 d1(本篇設計審 r1 後範圍收窄到回合);擋下原因固定標頭 `LUMOS-STOP-LINT:`;拆成另一支鉤子(〈決策〉第一條);鉤子不看 rc3 的意思,只看 JSON 的 status。
11. **撤除條件量不到** → 已處理:回合結束檢查由鉤子在真的擋下後呼叫 `lint-new --record-stop-block` 寫一筆治理帳(本篇設計審 r1 後從「lint-new 判 blocked 就記」改過來),三個月後 `lumos gov` 數得到;改檔前推列改用離線重播量(RETIRE-IF),不在每次改檔寫帳(`_hookevent` 明定只記「活著沒」不記成效)。

REVISIT:2026-12-15 照〈待解問題〉十一組改寫成完整設計(先查世界:回合起點事件、鉤子機讀輸出),跑規格閘與設計審 [closed:2026-11-06 十一組已逐組處理,見〈待解問題〉;設計審待派]

## 實驗(2026-11-06,暫存區,不動 repo)

- **E1 回合事件(Claude Code 2.1.319,`claude -p`)**:臨時設定檔掛 SessionStart、UserPromptSubmit、Stop 記錄 payload。結果:`-p` 下三種事件都觸發;Stop 回 `decision: block` 後模型照理由續做(寫出 fruit.txt);續做後的 Stop 帶 `stop_hook_active: true`,**這段續做不觸發** UserPromptSubmit;同一回合的送出提示與兩次 Stop 的 `prompt_id` 相同;`--resume` 下一回合送出提示換新的 `prompt_id`。Stop payload 鍵:`background_tasks、cwd、effort、hook_event_name、last_assistant_message、permission_mode、prompt_id、session_crons、session_id、stop_hook_active、transcript_path`。結論:回合起點可用送出提示事件記,單回合會談也查得到。
- **E2 兩支 Stop 並行同時擋**:兩支各回不同理由的 block。結果:兩支在 5 毫秒內同時啟動(並行),各自一個程序群組(pgid = pid);模型兩段理由都收到並各做一次。結論:拆成獨立鉤子可行。
- **E3 逾時訊號**:第三支 Stop 設 `timeout: 2`、接 SIGTERM 但不結束。結果:2 秒整收到 SIGTERM(15);不理會時約 1 到 2 秒內程序消失(最後一筆存活紀錄在 SIGTERM 後 1.06 秒);Claude Code 不等它,照常往下。結論:鉤子要在上限前自己收掉子程序;被 SIGTERM 時要轉給子程序群組。
- **E4 git 會不會改寫索引(git 2.39.2)**:檔案只 `touch` 過(內容沒變)時比對 `.git/index` 雜湊。`git --no-optional-locks status --porcelain=v1 -z -uall` 不變;`git --no-optional-locks diff-index --quiet HEAD` 不變但回 1(只看時間戳,誤判有修改);`git --no-optional-locks diff --quiet HEAD` **改寫**;一般 `git status` **改寫**。結論:只用帶 `--no-optional-locks` 的 `status`。
- **E5 宣告檔沒追蹤或被忽略**:未追蹤的 `.lumos/config.json`,`diff-index --quiet` 回 0(漏);`status ... --ignored=matching -- <檔>` 印 `??`;寫進 `.git/info/exclude` 後不帶 `--ignored` 什麼都不印、帶了印 `!!`;只 `touch` 過的 `lint.json` 不印;索引不變。
- **E6 改名狀態碼**:`cp` 到新目錄、`git add -N`、刪舊檔 → v1 輸出 ` R b/Foo.kt|a/Foo.kt|`(R 在第二格);另一組 `git add` 新檔 → `A  b/Bar.kt|`。
- **E7 白名單路徑**:`<根>/configs/ast-grep/../../proj/sgconfig.yml` 與 `<根>/configs/ast-grep/evil/sgconfig.yml`(evil 是指向專案的符號連結)字串前綴都通過、真實路徑加 `commonpath` 都擋下;相對路徑 `sgconfig.yml` 擋下;合法路徑通過。
- **E8 既有剝註解對 Kotlin 片段**:`'"'` 字元字面值,`_strip_c_comments` 與 `_stack_norm_line` 都沒把後面的 `.flatMapLatest` 剝掉(對);巢狀 `/* /* */ flatMapLatest */`,`_strip_c_comments` 漏出 `flatMapLatest`、`_stack_norm_line` 整行不算;字串樣板 `"${flow.flatMapLatest {…}}"` 兩者都剝成空(樣板裡的觸發字不算);沒收尾的字串片段只影響那一行。結論(前掃後更新):這兩個邊角是既有正規式掃描做不到的;盲判那條線已在 `_strip_c_comments` 加 `kotlin=True` 模式專門處理巢狀註解與字串樣板,本案改用它,只剩 Edit 片段本身切在字串或註解中間的情況(見〈天花板〉5)。
- **E9 觸發字文件頻率**:型錄 56 列的觸發字,對 Now in Android(本機複本 310 支 kt 檔,排除 build)算「出現在幾成檔案」。超過 5% 的:`Composable` 15.5%、`Inject` 14.5%、`Modifier` 9.4%、`runTest` 6.8%;以列計,D-39 17%、D-33 16%、D-34 11%、D-49 10%;整檔命中至少一列的佔 64%。結論:8% 門檻收前三個字;每次改檔只看寫入內容、最多推三列、同列同會談只推一次,剩下的量交 RETIRE-IF。
- **E10 Python 啟動成本**:`python3.14 -c 'import json,sys,os,time,pathlib'` 三次 0.03、0.03、0.05 秒——送出提示事件每回合多付這麼多。
- **E11(實作前必跑)背景任務與排程喚醒的回合**:互動模式下用 `run_in_background` 開一個會結束的背景指令、另設一個一分鐘後觸發的排程,讓 Claude Code 自己起回合;記下這兩種回合有沒有 `UserPromptSubmit`、Stop 的 `prompt_id` 是新是舊、`background_tasks` 與 `session_crons` 內容。量到之後回頭改範圍 2 第 3 條的描述(行為定義先照「對不上就不檢查並印一行」)。綁 S12。
  - **結果(2026-11-06,Claude Code 2.1.319,互動模式用 expect 開、另用 `claude -p` 量背景那半,臨時設定檔掛三個事件記 payload)**:①背景指令結束 → Claude Code 起一個新回合,**有** `UserPromptSubmit`(提示內容是 `<task-notification>…`)、帶**新的** `prompt_id`,那回合的 Stop 帶同一個新編號、`background_tasks` 已是空的;`-p` 模式同形(行程會等背景結束再收)。②一次性排程到點 → 同樣**有** `UserPromptSubmit`(提示內容就是排程的提示)、新 `prompt_id`、Stop 同編號、`session_crons` 已清空。③開背景與排程的那一回合,自己的 Stop 帶 `background_tasks`(status running)與 `session_crons`(一筆)非空,`prompt_id` 跟它自己的送出提示相同。④`-p` 模式下排程到點前行程就結束,排程不會觸發。
  - **對設計的意思**:這兩種回合都記得到起點,照一般回合檢查;範圍 2 第 3 條「對不上就不檢查並印一行」的退路照留(Codex、舊版或日後改版才會走到),背景或排程那一句只在真的對不上時印。`background_tasks` 非空**不代表**沒記到起點(③),所以那一句只換措辭、不拿來當判斷條件。新發現的漏網:背景指令在**開它的那回合收工之後**才寫的檔,修改時間早於通知回合的起點,兩個回合都不算——列進〈天花板〉1。
- **E12(實作時跑)共用模組匯入成本**:`python3.14 -c 'import sys; sys.path.insert(0, "scripts/hooks/claude"); import _hookshared'` 三次;超過 0.1 秒就照範圍 2 第 2 條改。
  - **結果(2026-11-06)**:匯入本身 3.4、3.6、3.6 毫秒,整個程序 0.03 秒三次——遠低於 0.1 秒,送出提示那條路照原設計匯入共用模組。
- **E13(實作時跑)ast-grep 給了 `--config` 還讀不讀專案設定**(r2 快照留的說法,S3 要實測一次):臨時 venv 裝 ast-grep 0.51.1,專案根放一份 `sgconfig.yml` 加一條自訂規則。結果:帶 `--config <工具鏈規則包>` 只出規則包的告警、專案那條不出;不帶 `--config` 才吃專案那份。白名單要求恰好一個 `--config` 的理由成立。同次取了一份真 SARIF 當測試假工具的樣本(相對路徑給相對 uri、絕對路徑給百分比編碼的絕對 uri、`-` 開頭的檔名要 `./` 才不被當選項)。
- **S12 實機驗收(2026-11-06,Claude Code 2.1.319、`claude -p`、sonnet,暫存區實驗專案複本照範本接好、真 ast-grep 0.51.1)**:三次各約 31 到 35 秒(含模型)。三次第一次收工都被擋、原因首行 `LUMOS-STOP-LINT:`、帶檔:行、型錄編號與放行指令;提示裡指定要用 GlobalScope 的兩次,模型續做時選擇照放行指令寫理由放行(之後收工放行);提示說「被擋就照建議修」的那次,續做改成注入的 `applicationScope`、收工放行,全程只擋一次。
- **Codex(codex-cli 0.160.0,專案層 `.codex/hooks.json` 掛記錄鉤子、`codex exec --dangerously-bypass-hook-trust`)**:送出提示事件**帶 `turn_id`、沒有 `prompt_id`**(鍵:cwd、hook_event_name、model、permission_mode、prompt、session_id、transcript_path、turn_id)。這台帳號試的三個模型都被伺服器拒絕(model_not_found),回合走不到收工,收工事件帶什麼、`turn_id` 對不對得上**沒量到**。照現在的程式,Codex 下收工會因缺 `prompt_id` 一律印「沒記到起點」不檢查(安全但沒作用);要不要改認 `turn_id` 或照 S12 改成不註冊,交編排者裁。→ 2026-11-08 編排者裁:改認 `turn_id`。這台帳號 Codex 的模型仍全被伺服器拒絕、跑不出回合,改讀官方原始碼 `codex-rs/core/src/hook_runtime.rs`:送出提示與收工兩事件的 `turn_id` 都取 `turn_context.sub_id`,同一回合相同;鉤子的回合編號改成 `prompt_id` 沒有就用 `turn_id`,測試 t_stop_lint_hook_codex_turn_id。在 Codex 上實跑擋下的回頭條件見 [[Systems/回合結束寫法檢查]]。
- **留到實作時實測、已轉成條款**:Codex 的送出提示與收工事件帶不帶同一個回合編號(既有調研記到 Codex 有 `UserPromptSubmit` 與 `turn_id`,沒實測跟 Stop 對不對得上)→ S12;`lint-new` 的 SIGTERM 收尾、白名單、JSON 要等實作 → S1 到 S4 的測試;ast-grep 給了 `--config` 就不再往上找專案設定(r2 快照的說法)→ S3 實作時實測一次。

## 實務隱患

- **效能熱路徑**:送出提示每回合多一次 Python 啟動(約 0.03 到 0.05 秒,E10);收工那支跟收工點名並行,使用者多等的是 `max(兩支)`,寫法檢查最壞約 22.5 秒、通常是 lumos 啟動約 0.8 秒加 ast-grep 幾支檔毫秒級;沒宣告 `ast-grep` 的專案不啟動 lumos。改檔前多讀一次型錄表(一次指令內快取)。
- **擋錯人**:共用工作目錄時,別的會談同時改的檔修改時間也晚於回合起點,會被算進來;擋下訊息每條帶檔名,模型自己判斷,出口是放行;全域規則本來就要求各會談各用工作樹。lint-new 例外的 rc1 不會誤擋(要 JSON 且 status=blocked)。
- **擋停迴圈**:同一回合同一批只擋一次、最多三批;Claude Code 的連續八次續做上限會因呼叫工具而歸零(官方原文),不算兜底。
- **併發**:兩支收工鉤子並行,各用不同標記檔名;同會談兩次收工不會同時發生;回合起點用暫存檔加 `os.replace` 原子覆寫。
- **資源釋放**:鉤子逾時先 SIGTERM lint-new、1 秒寬限讓它自己收工具群組與快照,寬限過了鉤子自己 SIGKILL lint-new 與登記檔裡的工具群組;工具先登記再解除訊號擋住,不會有開了沒登記的空窗;SIGKILL 漏掉的快照照既有規則一天後清,而且 `.lumos/` 底下的檔不算碰過的檔。
- **資安**:回合結束會自動執行被打開專案宣告的命令。只准白名單(寫死在 lumos、逐詞驗、設定檔路徑取真實路徑比對、送 shell 前把 `$HOME` 換成引號包好的絕對路徑);宣告檔沒提交、被忽略或有修改時不跑;鉤子跑 git 前套既有 `_harden_git_env`(關掉會執行指令的兩個 git 設定);擋下原因裡的檔名與告警訊息當資料消毒。跟收工點名那支「被打開的資料夾不准指使我們執行指令」同一個威脅模型。
- **回滾**:見〈回退〉;新鉤子是新檔,撤註冊即停。
- **時鐘與修改時間**:`mv`、`cp -p`、`git checkout` 舊版會保留舊修改時間,那支檔不算這回合碰過,推送前閘兜底。
- **相依案**:[[Projects/Android寫法語意情境表態與盲判_計劃]](分支 `EnzoHsieh-Android/android-situation-evidence`)擁有 `_kt_decision_table`、`_kt_trigger_re`、`_kt_toolchain_root`、`_strip_c_comments` 的 `kotlin=True` 模式、`check.py` 的 `dt_table`,也擁有它們本身的測試;本案在本機整合分支先合那條分支再開工(範圍 0)。合進來之後棧別題通道對 kt 編輯也會印它的 `kt-situation` 題(推送前要表態);本案的決策列是同一張表的列內容,兩者並存。
- **舊否決對照(2026-11-06 跑 `lumos rejections` 按概念比對)**:2026-07-06 撤的是「每回合刷屏的收工提醒」,本案只在真有新增告警時擋、同批一次,不同形;[[Systems/android-e2e-acceptance]]「中斷時先送 TERM 等寬限再 KILL、不直接 KILL」跟本案鉤子收子程序同向;母計劃記的三條(新增告警閘出錯就放行、改檔前推播零命中不講、收工鉤子只印一行)照舊。沒撞到。
- 已排除:金流:不碰付款或點數
- 已排除:對外送出:檢查只在本機跑,不送資料出去
- 已排除:不可逆:新增鉤子、旗標與輸出鍵,退提交即回原狀;治理帳只追加
- 守衛面:新增回合結束擋停、改了 `lint-new` 判定函式的參數,屬守衛面,走完整設計審

## 驗收條款

- [S1] 當工作樹有未提交的 kt 改動、跑 `lumos lint-new --worktree --since <回合起點>` 時,新增一條規則包告警 應 rc1 並印檔:行、訊息、放行指令;修改時間早於回合起點的檔 應 不檢查;只動到 HEAD 已有告警所在檔但沒新增 應 rc0;未追蹤與 `A` 狀態的新 kt 檔裡的告警 應 算新增;搬到別的目錄並改了 `package` 行的檔(含 `git add -N` 之後狀態碼 R 在第二格)裡原有的告警 應 不算新增;先 `git mv` 再 `mv` 再 `git add -N` 的兩段改名鏈 應 追回 HEAD 的原檔、原有告警 應 不算新增;改名鏈追不到原檔時 應 整支當新檔並列在 skipped;`_porcelain_z_paths`、`_tg_rb_pending`、`_handoff_files` 改走新函式後 應 跟改之前同輸出;檔名以 `-` 開頭時 應 照樣被當成檔案檢查;合併衝突中的檔 應 列成沒檢查;合併或 rebase 進行中 應 rc3;`.lumos/` 底下的檔 應 不掃;碰過的檔超過 50 支 應 rc3 並印留給推送前閘;沒裝工具 應 rc3 並印「沒裝 ast-grep」;宣告的命令全都不在白名單 應 rc3;`.lumos/lint.json` 不在 HEAD、或它與 `.lumos/config.json` 未追蹤、被忽略或有修改 應 rc3;沒有 HEAD 應 rc3;跑完後 `.git/index` 應 跟跑之前位元組相同(含檔案只被 touch 過的情況);`--diff` 與 `--worktree` 都給或都沒給、或 `--since` 沒配 `--worktree` 應 rc2 [test:t_lint_new_worktree]
- [S2] 當 `lumos lint-new --worktree --json` 跑完時,stdout 最後一行 應 是 JSON,含 status、全部新增告警(超過 20 條也全列)與批次雜湊;同一指紋多出一處 應 換批次雜湊;順序不同的同一批 應 得到同一個雜湊;工作樹檢查本身 應 不寫治理帳;`--record-stop-block` 應 只寫一筆 `stop-lint` 事件、rc0,跟 `--diff` 或 `--worktree` 一起給 應 rc2 [test:t_lint_new_worktree_json]
- [S3] 當自動執行白名單檢查一條命令時,`ast-grep scan --config $HOME/harness/lumos-toolchain/configs/ast-grep/kotlin-android/sgconfig.yml --format sarif {LINT_FILES} > {LINT_SARIF_OUT}`(工具鏈根就在那裡時)應 通過,而且送進 shell 的命令 應 不含 `$`;`--config` 是相對路徑、含 `..` 落到 `configs/ast-grep/` 外、或經符號連結指到外面 應 不通過;第一個詞是 `sg`、`bash`、`./ast-grep` 應 不通過;帶 `-U`、`--update-all`、`-i`、`--custom-languages` 應 不通過;沒給 `--config` 或給兩個 應 不通過;`$HOME` 出現在 `--config` 值開頭以外、或含 `;`、`>>`、第二個 `>`、`*` 應 不通過;`.lumos/config.json` 寫任何鍵 應 放寬不了;宣告路徑大小寫跟工具鏈實際目錄不同時 應 不通過並印大小寫那句原因 [test:t_lint_new_worktree_allowlist]
- [S4] 當工作樹模式的 `lint-new` 跑檢查工具時收到 SIGTERM,應 用 `_kill_proc_group` 收掉登記過的工具程序群組、刪掉快照目錄、印「被中止」並 rc3;開工具到登記完成之間收到的 SIGTERM 應 等登記完才處理、那支工具 應 照樣被收掉;工具結束後 應 從 `--pgid-file` 拿掉 [test:t_lint_new_worktree_sigterm]
- [S5] 當新鉤子收到 `UserPromptSubmit` 時,應 把 `prompt_id` 與時刻原子寫進 `stop-turn/<會談>`、stdout 不輸出、rc0;repo 根沒有 `.lumos/lint.json` 時 應 照樣寫;會談編號空或目錄不可信時 應 不寫也不出錯 [test:t_stop_lint_turn_start]
- [S6] 當新鉤子收到 `Stop`、回合起點之後改過的 kt 檔有新增告警時,應 回 `decision: block`,原因第一行是 `LUMOS-STOP-LINT:`、含檔:行、規則訊息與放行指令、檔名含換行或反引號時 應 被消毒;`stop_hook_active` 為真而告警是同一批 應 不擋;續做後變成另一批 應 再擋;同一回合第四批 應 不擋、下一回合(新 `prompt_id`)同一批 應 再擋;沒有回合起點紀錄、`prompt_id` 對不上或 payload 缺 `prompt_id` 應 不檢查並在 stderr 印一行,帶 `background_tasks` 或 `session_crons` 時 應 印背景或排程那一句;真的擋下而且輸出寫出去之後 應 呼叫一次 `--record-stop-block`,同批不擋或超過上限而不擋時 應 不呼叫;沒宣告 `ast-grep` 的專案 應 不匯入共用模組就結束;lint-new 退出碼 1 但輸出不是 JSON、或 status 不是 blocked 應 不擋;`LUMOS_STOP_LINT_OFF=1` 或 `LUMOS_STOP_BLOCK_OFF=1` 應 不跑;`lint_new.gate` 設 warn 應 不擋;stdout 寫不出去時 應 刪掉剛佔的名額;`stop-block/` 裡 應 只有擋過的會談留下檔案;既有收工點名那支 應 照舊、它的標記不受影響 [test:t_stop_lint_hook]
- [S7] 當 `lint-new` 超過新鉤子的內層時限時,鉤子 應 對它送 SIGTERM、1 秒寬限內它自己收掉就不再送別的;寬限過了還在時 應 對 lint-new 與登記檔裡每個還存活的工具群組送 SIGKILL;結束後 應 沒有留下任何工具程序與 `.lumos/lintbase-*` 以外的殘留、不擋,整支在 30 秒上限內結束;鉤子自己收到 SIGTERM 時 應 照同順序收掉 lint-new 與工具群組、不輸出 [test:t_stop_lint_hook_timeout]
- [S8] 當安裝程式產生註冊時,`UserPromptSubmit` 與 `Stop` 應 各有一筆指向 `stop-lint-hook.py`、時間上限 30 秒;`check-graph-sync.py` 的上限 應 仍是 40;`stop-lint-hook.py` 應 在 `_GLOBAL_CLAUDE_HOOKS` 裡;`stop-lint-hook.py` 與 `_hookshared.py` 應 都在 `_VENDORED_TREE_FILES` 裡(既有逐檔比對測試綠);`enforcement_status` 的 Claude 與 Codex 兩份存活清單 應 各有新鉤子一行;新鉤子 `__main__` 應 用 `_hookevent.guard` 包 `main`;Codex 目標 應 照既有對照表原樣產生兩筆 [test:t_stop_lint_hook_registration]
- [S14] 當共用程式從 `check-graph-sync.py` 搬進 `_hookshared.py` 之後,`check-graph-sync.py` 的既有測試 應 全綠、它對外的函式名 應 照樣找得到;`scripts/hooks/claude/` 底下 應 沒有任何鉤子用 importlib 載另一支鉤子 [test:t_hookshared_move_keeps_graph_sync]
- [S9] 當改檔前鉤子的目標是 kt 檔、寫入的新內容含決策表某列觸發字時,impact 的 JSON 應 多 `decision_rows`,鉤子 應 印那一列;觸發字只出現在註解、字串或 Edit 的 `old_string` 裡 應 不推;觸發字前後緊接英數或底線 應 不算、前面是 `.` 應 算;大小寫不同 應 不算;命中超過三列 應 只印命中字數最多的三列、沒印的下次還能推;同會談同列第二次 應 不推;既有影響脈絡是空的 應 照樣印列;目標是測試檔、不是 kt/kts、或專案沒有圖譜 應 不推;冷卻窗內第二次改同一支檔、寫入的新內容含沒推過那列的觸發字時 應 照樣推;型錄讀不到 應 不推也不報錯;觸發字在巢狀註解或字串樣板的字串部分裡 應 不推、在字串樣板 `${…}` 的程式碼裡 應 推;這支 kt 檔判成伺服端(平台排除集合含 `kt-compose`)時 應 不推 [test:t_impact_hook_kotlin_decision_rows]
- [S10] 當 `cmd_impact` 算決策列時,停用列 應 不出現在 `decision_rows`;觸發字是空清單(「(無)」)的列 應 永遠不出現;`_KT_DT_ERR` 有值時 應 沒有 `decision_rows` 鍵也不報錯;回的列欄位 應 是 id、situation、standard、alt、hits [test:t_impact_decision_rows_table_states]
- [S13] 當 `lumos lint-new --worktree --budget 5` 跑時,單條命令保底 應 是 1 秒(設定檔 `lint_new.per_cmd_floor_sec` 30 不影響工作樹模式),預算 應 從指令一開始起算;`--diff` 模式 應 照舊用 30 秒保底;`--budget` 覆寫設定檔的 `budget_sec` 應 兩種模式都生效;`--budget` 給 0、負數或不是數字 應 rc2;收工鉤子收到 lint-new 的 rc2 時 應 在 stderr 印「重跑安裝」那一行而且不擋 [test:t_lint_new_budget_flag]
- [S11] 當型錄格式檢查遇到觸發字 `Composable`、`Inject`、`Modifier` 時,應 報「觸發字含常用字」;改寫後的型錄 應 通過檢查 [test:t_catalog_stop_triggers]
- [S12] 當在實驗專案複本照範本接好、用 `claude -p` 讓 AI 在一回合裡寫進一處規則包會抓的壞寫法並收工時,應 被擋下、續做改好後收工放行;Codex 照樣跑一次時,送出提示與收工的回合編號 應 對得上,對不上就記下並把 Codex 改成不註冊這支;背景任務與排程喚醒的回合 應 記下有沒有送出提示事件與 `prompt_id` 新舊(實驗 E11) [manual:暫存區實驗專案複本各用 claude -p 與 codex exec 實跑一次,另在互動模式跑實驗 E11,記下擋下訊息、續做結果、耗時、Codex 兩事件的回合編號、背景與排程回合的事件與欄位]

## 預期值表

| 條款 | 輸入 | 預期 | 來源 |
|---|---|---|---|
| S1 | 工作樹一支 kt 檔新增一處 `GlobalScope.launch`(規則包會抓),修改時間晚於 `--since` | rc1,印檔:行與放行指令;`.git/index` 雜湊前後相同 | 本計劃範圍 1;實驗 E4 |
| S1 | 同上但只 touch `.lumos/lint.json`、內容不變 | 照常檢查,不判宣告檔有修改 | 實驗 E5 |
| S1 | `.lumos/config.json` 未追蹤或被 `.git/info/exclude` 忽略 | rc3,印宣告檔不乾淨 | 實驗 E5;第二輪邊界席 F6 |
| S2 | 25 條新增告警 | JSON 的 new 有 25 條、total 25;人讀輸出只列 20 條 | 第二輪通才席 F4 |
| S3 | `linter精選目錄` 範本命令,工具鏈根是 `~/harness/lumos-toolchain` | 通過,送出的命令含引號包好的絕對路徑、不含 `$` | 實驗 E7;`Systems/linter精選目錄` 範本 |
| S3 | `--config $HOME/harness/lumos-toolchain/configs/ast-grep/../../x/sgconfig.yml` | 不通過 | 實驗 E7;第二輪通才席 F1 |
| S6 | 第一次收工有一批新增告警;續做沒修(同一批)再收工 | 第一次擋、第二次不擋 | 官方鉤子文件 stop_hook_active 段;實驗 E1 |
| S6 | lint-new 退出碼 1、stdout 是 traceback | 不擋 | 第二輪通才席 F4 |
| S7 | lint-new 卡住不結束 | 內層時限到送 SIGTERM、1 秒後 SIGKILL,不擋,總時間小於 30 秒 | 實驗 E3 |
| S8 | 跑安裝產生註冊 | 兩個事件各一筆新鉤子、上限 30;收工點名仍 40 | 本計劃範圍 2 |
| S9 | Edit 的 `new_string` 含 D-n 觸發字,`old_string` 含另一列觸發字 | 只推 D-n | 母計劃第二輪快照(卷證 r2-snapshot.md)的 S5「Edit 的舊字串裡 應 不推」 |
| S9 | 寫入內容觸發字只在 `/* /* … */ … */` 或 `"…"` 裡;另一處在 `"${flow.觸發字 {…}}"` 的大括號裡 | 前者不推、後者推 | 實驗 E8;盲判計劃〈用詞〉Kotlin 剝註解與字串 |
| S11 | 觸發字 `Composable` | 格式檢查報常用字 | 實驗 E9 |
| S4 | 工作樹模式跑一支會睡 30 秒的假檢查工具,第 1 秒送 SIGTERM | 假工具的程序群組已不存在、`.lumos/lintbase-*` 快照目錄已刪、印「被中止」、rc3 | 本計劃範圍 1 第 7 條;既有 `_kill_proc_group` |
| S5 | `UserPromptSubmit` payload 帶 session_id 與 prompt_id,repo 根有含 `ast-grep` 的 `.lumos/lint.json` | `stop-turn/<會談>` 內容是那個 prompt_id 與時刻、stdout 空、rc0;換成沒有 lint.json 的 repo 則不建檔 | 官方鉤子文件 UserPromptSubmit 段;實驗 E1 |
| S10 | 決策表一列標停用、一列觸發字寫「(無)」,寫入內容碰到這兩列的字;另一案把型錄路徑指到不存在的檔 | 兩列都不推;型錄不在時沒有 `decision_rows` 鍵、rc0 | 盲判那條線的 `_kt_decision_table` 列字典;第二輪邊界席 F8 |
| S13 | `.lumos/config.json` 設 `per_cmd_floor_sec: 30`,跑 `lint-new --worktree --budget 5`,宣告一條很快的 ast-grep 命令 | 命令有跑、不是 not-checked | 設計審前掃 ③「保底與預算沒對上」;既有 `_LINT_NEW_DEFAULTS` |
| S13 | `lint-new --worktree --budget 0` | rc2 | 設計審前掃 ③「`--budget` 漏列」 |
| S12 | 實驗專案複本,`claude -p` 一回合寫進 `GlobalScope.launch` 後收工 | 第一次收工被擋、原因首行 `LUMOS-STOP-LINT:`;續做改好後收工放行;Codex 兩事件回合編號對得上或記下對不上 | 實驗 E1、E2;第二輪通才席 F3 |
| S1 | `git mv a/Foo.kt b/Foo.kt`、再 `mv b/Foo.kt b/Foo2.kt`、`git add -N b/Foo2.kt`,`b/Foo2.kt` 保留原有告警並改 `package` 行 | 原有告警不算新增、rc0 | 本篇設計審 r1 可行性席 F1 實跑 |
| S6 | 同一會談第一回合擋滿三批,第二回合(新 `prompt_id`)寫出新的新增告警 | 第二回合照擋 | 本篇設計審 r1 通才席 F1 |
| S6 | 同一批第一次擋下、續做沒修再收工 | 治理帳只多一筆 `stop-lint` | 本篇設計審 r1 通才席 F2 |
| S9 | 第一次 Edit 沒觸發字,5 分鐘後(冷卻窗內)第二次 Edit 加進 D-n 的觸發字 | 第二次推 D-n | 本篇設計審 r1 通才席 F3 |
| S7 | lint-new 的 SIGTERM 處理器被換成什麼都不做、工具是睡 60 秒的假程序 | 1 秒寬限後鉤子 SIGKILL 掉 lint-new 與假工具群組,沒有殘留 | 本篇設計審 r1 可行性席 F2 |
| S8 | 跑安裝並跑 `lumos enforcement` | 新鉤子在兩份存活清單裡出現;`_VENDORED_TREE_FILES` 逐檔比對測試綠 | 本篇設計審 r1 依據席 F3 |
| S14 | 搬完共用程式後跑 `check-graph-sync.py` 的既有測試 | 全綠 | 本篇設計審 r1 架構對齊席 F1 |

## 回退

退回本案的提交:`lint-new` 少了工作樹模式(`--diff` 不受影響);重跑安裝後新鉤子的兩筆註冊消失(檔不在白名單後 `_prune_dangling` 也會剪);`stop-turn/` 與 `stop-block/*.lint-*` 照七天清理自然消失;改檔前不再推列;型錄停用字與三列觸發字改回原樣;治理帳已寫的 `stop-lint` 事件留著(只追加,讀的人看不懂就略過)。

## 天花板

1. 只看這一回合碰過、還沒提交的檔;同一回合先寫後提交的檔、修改時間被保留成舊值的檔、被逾時殺掉那回合的檔、沒記到起點的回合、背景指令在開它的那回合收工之後才寫的檔(實驗 E11:通知回合的起點晚於寫檔時刻),等代碼審通過前或推送前閘。
2. 回合結束只跑白名單命令(現在只有 ast-grep);detekt 這類工具的新增告警要等代碼審通過前或推送前閘。
3. 共用工作目錄時,別的會談同時改的檔會被算進來。
4. 搬檔配基準只認唯一的同名檔;一次改超過 50 支檔的回合不檢查。代碼審 r3 起找改動不跑 `git status`(會經內容過濾器):已暫存的改名只認「HEAD 與索引同一物件」的,工作樹那一側換了檔名又改了內容的(`git add -N` 加 `mv`)認不出、整支當新檔;用了真過濾器的專案(LFS、autocrlf)工作樹原樣跟索引裡轉過的不同,會多查幾支。方向都是多查不漏查;例外是標了 assume-unchanged 與 skip-worktree 的檔照 git status 不比對工作樹,改了不會被點名(代碼審 r5 起)。
5. 決策列只看寫入的片段:Edit 的 `new_string` 若從字串或註解中間切起,剝字串會對錯邊,那一段的觸發字可能多算或漏算。
6. 沒有知識圖譜的專案不推決策列(決策 d2)。
7. 停用字門檻用一個開源專案(Now in Android)量出來;別的專案的常用字可能不同。
8. 收工點名呼叫的影響分析(`impact --worktree-nofilter`)不用 git diff 算改動行,改成兩版各數每行出現幾次再相減(代碼審 r4 起,線性時間;difflib 最壞平方時間,重複行多的 2 萬行檔實測 57 秒):行序不保留,只移動位置的行不算改動(git diff 會列成一刪一加),新版多出來的行(+)全部排在前面、舊版多出來的(-)排在後面(代碼審 r5 起;原本 - 在前,刪得多的檔會把新增的行截掉),超過 4000 字時先截掉的是被刪的舊行,截掉的那一段跟 git diff 不同(git diff 照 hunk 先刪後加)——主要影響非 pinned 的排名分數;`content:` 事故的比對也吃這段改動內容,邊緣情況可能多或少一筆。先判是不是程式碼才讀內容(`_impact_diff_seed_ok`;它收 .png 這類副檔名,這種檔照讀、受總量上限管,含 NUL 的當二進位、沒有改動行);每支上限 1MB、兩版合計上限 8MB(`_IMPACT_WT_READ_TOTAL`),超過的、路徑含換行或結尾是 CR 的,查詢文字只用路徑、列進 `query_path_only`。
9. PATH 有空項時,使用者自己打的 git、以及掛鉤第一行的 env bash 本身就可能解到目前目錄,這是環境層缺口,工具只保證自己不再多開一條路(代碼審 r6 起三支 shell 掛鉤在 `set -u` 之後先把 PATH 濾成只剩絕對項,Python 入口在 r5 已由 `_clean_path_env` 洗過;第一行在任何程式碼執行前就被解析,改成 `#!/bin/bash` 會在 bash 不在 /bin 的系統壞掉,所以不改)。

REVISIT:2027-02-15 查有沒有接了規則包、卻沒有知識圖譜的 Android 消費專案;有就把決策列改到 `cmd_impact` 找不到圖譜之前也算(天花板 6)
REVISIT:2027-05-06 拿一個消費專案的 kt 檔重量一次觸發字文件頻率,超過 8% 的補進停用字表(天花板 7)

## 依據來源

| 機制 | 依據 | 網址或實測 | 在哪看得到 |
|---|---|---|---|
| 回合起點用送出提示事件 | 官方:`prompt_id`「UUID identifying the user prompt currently being processed」、`UserPromptSubmit` 在送出提示時觸發;Claude Code 自己起的回合有沒有送出提示事件,官方沒寫 | https://code.claude.com/docs/en/hooks.md ;實驗 E1(`-p`、`--resume`);E11 待跑 | 〈實驗〉E1、E11,〈決策〉第二條 |
| 續做照查、靠回合內批次去重防迴圈 | 官方原文「Check this value or process the transcript to avoid blocking on a condition that will never resolve」;八次續做上限「resets each time Claude calls a tool」,不能當兜底 | https://code.claude.com/docs/en/hooks.md (Stop input 段) | 範圍 2 第 3、6 條;〈決策〉第五、六條 |
| 拆成獨立收工鉤子 | 官方:同事件鉤子並行;實測兩支 block 理由都送到 | https://code.claude.com/docs/en/hooks ;實驗 E2 | 〈決策〉第一條 |
| 鉤子收 lint-new(有寬限) | 實測 Claude Code 逾時先送 SIGTERM、不理會約 1 到 2 秒內收掉;本案照同形對 lint-new 先 SIGTERM、1 秒後 SIGKILL | 實驗 E3 | 範圍 2 第 4 條;[[Systems/hook逾時預算]] |
| lint-new 收檢查工具(無寬限) | 既有 `_kill_proc_group` 直接對程序群組送 SIGKILL;檢查工具唯讀、沒東西要自己收 | `scripts/lumos` 的 `_kill_proc_group` | 範圍 1 第 7 條 |
| 工具先登記再開跑、鉤子打得到工具群組 | `signal.pthread_sigmask` 擋住訊號的空窗;新 session 的群組只能直接 killpg | https://docs.python.org/3/library/signal.html#signal.pthread_sigmask ;本篇設計審 r1 可行性席 F2 | 範圍 1 第 7 條、範圍 2 第 4 條 |
| 鉤子共用模組 | 既有 `_hookevent.py` 走 `sys.path.insert` 匯入;新鉤子五個登記點 | `scripts/hooks/claude/_hookevent.py`;本篇設計審 r1 架構對齊席 F1、依據席 F3 | 範圍 2 開頭 |
| 改名鏈追回原檔 | 實測兩段改名在 porcelain v1 出兩筆串起來的改名 | 本篇設計審 r1 可行性席 F1 實跑(git 2.39.2) | 範圍 1 第 2 條 |
| 機讀介面 `--json` 最後一行 | lumos 既有 `impact --json` 讀法(取最後一行解析) | `check-graph-sync.py` 的 `_impact_missing` | 範圍 1 第 8 條 |
| 工作樹清單不改寫索引 | git 官方 `--no-optional-locks`(工作樹模式一律帶 `GIT_OPTIONAL_LOCKS=0`);porcelain v1 只剩狀態碼的寫法沿用,代碼審 r3 起清單不跑 `git status`、改走 `_wt_changed_nofilter` | https://git-scm.com/docs/git#Documentation/git.txt---no-optional-locks ;https://git-scm.com/docs/git-status#_porcelain_format_version_1 ;實驗 E4、E6 | 範圍 1 第 2、3 條 |
| 宣告檔乾淨判法 | 代碼審 r3 起不用 `git status`(會經內容過濾器):兩支宣告檔的未提交改動走 `_wt_changed_nofilter`,被忽略的用 `git ls-files -o -i --exclude-standard`(只列被忽略的未追蹤檔);原本的 `git status --ignored=matching` 已被取代 | https://git-scm.com/docs/git-ls-files (-o、-i、--exclude-standard);實驗 E5;governance/review-reports/code-android寫法回合結束檢查/r3-intake.md | 範圍 1 第 3 條;`_lint_wt_unready`;t_lwt_r3_nofilter_attack |
| 白名單路徑比對 | Python `os.path.realpath`(解 `..` 與符號連結)、`os.path.commonpath` | https://docs.python.org/3/library/os.path.html ;實驗 E7 | 範圍 1 第 5 條 |
| 白名單資安動機 | 收工點名那支既有「被打開的資料夾不准指使我們執行指令」與 `_harden_git_env`;ast-grep 設定可宣告自訂語言載入原生程式庫 | https://ast-grep.github.io/reference/sgconfig.html | 範圍 1 第 5 條、〈實務隱患〉資安 |
| 決策列併進棧別題那一段 | 既有 `cmd_impact` 算 `stack_questions_applicable` 那段的啟用條件;盲判那條線的 `_strip_c_comments(kotlin=True)`、`_kt_decision_table` | 實驗 E8;`android-situation-evidence` 工作樹 `scripts/lumos`(2026-11-06 查) | 〈決策〉第四條、範圍 3 第 2、3 條;[[Systems/棧別提問表態閘]] |
| 觸發字邊界定義 | [[Projects/Android寫法語意情境表態與盲判_計劃]]〈用詞〉候選列;實作在盲判那條線的 `_kt_trigger_re` | `android-situation-evidence` 工作樹 `scripts/lumos` | 用詞 `_kt_trigger_re` |
| 工作樹模式保底與 `--budget` | 既有 `_LINT_NEW_DEFAULTS`(`budget_sec` 300、`per_cmd_floor_sec` 30)與「剩餘預算不到保底就不跑」的判法 | `scripts/lumos` 的 `_LINT_NEW_DEFAULTS`、`_lint_new_config` | 範圍 1 第 1、6 條;S13 |
| 停用字用文件頻率 | 資訊檢索 IDF 概念 | https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html ;實驗 E9 | 範圍 3 第 5 條 |
| 撤除條件量得到 | 既有治理帳記帳路徑 `_gate_event_or_warn`,由呼叫層在真的擋下後記;`_hookevent` 只記活著沒、不記成效 | `scripts/hooks/claude/_hookevent.py` 檔頭說明;本篇設計審 r1 通才席 F2 | 範圍 1 第 9 條、範圍 2 第 6 條、RETIRE-IF |
| Codex 是否同形 | 既有調研記到 Codex 有 UserPromptSubmit、Stop、`turn_id`;第三方部落格(未核官方);2026-11-06 實測送出提示帶 `turn_id` 不帶 `prompt_id`,收工沒量到 | [[Projects/Codex工作流整合_調研]];https://codex.danielvaughan.com/2026/03/26/codex-cli-hooks-deep-dive ;〈實驗〉Codex 那條 | 範圍 2 第 3 條;[[Systems/回合結束寫法檢查]] PITFALL |
| 背景與排程回合也記得到起點 | 實測背景指令結束、一次性排程到點都觸發送出提示、帶新 `prompt_id` | 實驗 E11(Claude Code 2.1.319) | 範圍 2 第 3 條、〈天花板〉1 |
| 給了 `--config` 不吃專案設定 | ast-grep 0.51.1 實測;設定檔說明頁 | https://ast-grep.github.io/reference/sgconfig.html ;實驗 E13 | 範圍 1 第 5 條 |
| 共用模組匯入不拖慢送出提示 | 實測匯入 3.5 毫秒、整個程序 0.03 秒 | 實驗 E12 | 範圍 2 第 2 條 |
| 批次雜湊 | 指紋多重集合排序後取 sha256 前 16 碼(Python 標準庫 hashlib) | https://docs.python.org/3/library/hashlib.html | 用詞「批次雜湊」、S2 |
| 工作樹改動清單與基準讀取 | `git cat-file --batch` 一次讀多個 HEAD 物件 | https://git-scm.com/docs/git-cat-file#_batch_output | 範圍 1 第 2 條 |
| 原子寫回合起點 | `os.replace` 同一檔案系統上是原子的 | https://docs.python.org/3/library/os.html#os.replace | 範圍 2 第 2 條 |
| 名額先佔 | `os.open` 帶 `O_CREAT|O_EXCL` 已存在就失敗;既有收工點名同一做法 | https://docs.python.org/3/library/os.html#os.open ;`scripts/hooks/claude/check-graph-sync.py` 的 `_stop_mark_write` | 範圍 2 第 6 條 |
| 工作樹模式不開 shell 執行(代碼審 r1) | Python 官方 subprocess〈Security Considerations〉:不開 shell 時所有字元原樣傳給程式;開 `shell=True` 時引號由應用程式自己負責 | https://docs.python.org/3/library/subprocess.html#security-considerations ;r1-intake.md〈先查世界〉 | `scripts/lumos` 的 `_lint_wt_argv`、`_lint_spawn_argv`;t_lwt_r1_shellfree_argv |
| HEAD 沒有的物件以行尾判(代碼審 r1) | git 官方 BATCH OUTPUT:不存在的物件輸出 `<object> SP missing LF`,object 名可含空白 | https://git-scm.com/docs/git-cat-file#_batch_output | `_lint_wt_blobs`;t_lwt_r1_space_path_blob |
| 查狀態時關掉內容過濾器(代碼審 r1;已被取代) | 已被取代:代碼審 r3 起找改動不跑會經內容過濾器的指令,見下面「找改動不跑 status」那列;r1 的做法是給 `filter.<名>.clean` 空指令並設 `required=false`,名字含非 UTF-8 位元組時列不到 | https://git-scm.com/docs/gitattributes#_filter ;r1-intake.md 資安席 F2;r3-intake.md〈先查世界〉 | `_lint_wt_filter_args` 已在 r2 拿掉 |
| 開程序到登記之間的訊號先記下(代碼審 r1) | 訊號遮罩跨 fork/exec 由子程序繼承,擋著開出去的子程序收不到那個訊號 | https://man7.org/linux/man-pages/man7/signal.7.html (Signal mask and pending signals);自測 S7② | `stop-lint-hook.py` 的 `_on_sigterm`;t_slh_r1_spawn_window_term |
| 不信任 repo 的 git 參數只有一份(代碼審 r2,r3 收窄) | git 官方:沒有選項或環境變數能讓 git 不讀 repo 自己的 `.git/config`(`GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` 只管全域與系統層),命令列 `-c` 優先;`core.fsmonitor`、`diff.external` 的值會被當成指令執行。現況:`_git_untrusted_c` 只給固定三項 `core.fsmonitor=false`、`core.hooksPath=/dev/null`、`diff.external=`(r3 起不再列過濾器名字逐個關);跟鉤子那份 `_GIT_UNSAFE_CONFIG` 只差 `core.hooksPath` | https://git-scm.com/docs/git ;https://git-scm.com/docs/git-config (core.fsmonitor、diff.external、core.hooksPath);r2-intake.md、r3-intake.md〈先查世界〉 | `_GIT_UNTRUSTED_FIXED`;t_lwt_r2_untrusted_single_source;t_r4note_untrusted_two_lists |
| 沒檢查到的種類由 lint-new 明寫(代碼審 r2) | 外層照欄位判、不靠推測;判定裡沒寫明的一律算沒能檢查(寧可記失敗) | governance/review-reports/code-android寫法回合結束檢查/r2-intake.md〈先查世界〉 | 範圍 1 第 8 條、範圍 2 第 5 條 |
| 佔位符展開共用核心(代碼審 r2) | 既有 `_lint_cmd_with_files` 宣告唯一實作(三處各寫一份時漏一處出事);字串版與參數清單版只差跳脫 | `scripts/lumos` 的 `_lint_cmd_with_files` 說明;r2-intake.md〈先查世界〉 | 範圍 1 第 5 條 |
| 找改動不跑 status(代碼審 r3) | git 官方 `hash-object --no-filters`:「Hash the contents as is, ignoring any input filter that would have been chosen by the attributes mechanism, including the end-of-line conversion」;`--stdin-paths` 一行一個路徑(含換行、開頭是引號、結尾是 CR 的路徑表達不了,當改過) | https://git-scm.com/docs/git-hash-object ;governance/review-reports/code-android寫法回合結束檢查/r3-intake.md〈先查世界〉、r4-正確性-sonnet.md F2 | `_wt_changed_nofilter`(主程式與 `check-graph-sync.py` 逐字複本);t_lwt_r3_nofilter_attack;t_r4wt_cr_name |
| 索引的模式、物件編號與路徑基準(代碼審 r3、r4) | git 官方 `ls-files -s`:輸出「mode bits, object name and stage number」;`--full-name`:「forces paths to be output relative to the project top directory」;`rev-parse --show-toplevel`、`--show-prefix` 取 repo 根與子目錄前綴(代碼審 r4:被檢查目錄是子目錄時 `ls-tree --full-tree`、`hash-object` 從根算,`ls-files` 從目前目錄算) | https://git-scm.com/docs/git-ls-files ;https://git-scm.com/docs/git-rev-parse ;r4-正確性-sonnet.md F1 | `_wt_changed_nofilter`、`_git_toplevel`(r5 起 lint-new、影響分析、`cmd_impact_diff` 共用這一支取根;收工點名鉤子 `_repo_top` 把狀態表路徑接在 repo 根上;r6 起狀態表出口 `_git_status_entries` 只回專案底下的條目,同 prek 的 monorepo 做法 https://prek.j178.dev/monorepos/ );t_r4wt_monorepo_subdir;t_r5sub_hook_e2e;t_r5sub_impact_cli;t_r6del_status_entries_scope |
| 工具寫檔上限(代碼審 r3) | Python 官方 `resource.RLIMIT_FSIZE`:「The maximum size of a file which the process may create」;超過時程序收到 SIGXFSZ。上限是 SARIF 讀取上限加 `_LINT_WT_FSIZE_SLACK`(1MB) | https://docs.python.org/3/library/resource.html#resource.RLIMIT_FSIZE ;r3-資源-sonnet.md F1 | `_lint_wt_fsize_cap`;t_lwt_r3_tool_fsize_limit |
| 影響分析改動行用數次數相減(代碼審 r4) | Python 官方 difflib:「SequenceMatcher is quadratic time for the worst case」,重複行多的 2 萬行檔實測 57 秒;改用 `collections.Counter` 兩版各數每行出現幾次再相減(線性時間;查詢文字只給事故正規式比對與排名用,行序不重要) | https://docs.python.org/3/library/difflib.html ;https://docs.python.org/3/library/collections.html#collections.Counter ;r4-通才-sonnet.md F2 | `_impact_line_delta`、`_impact_wt_nofilter`;t_r4imp_counter_speed |
| 鉤子找 lumos 只認絕對路徑(代碼審 r4) | `shutil.which` 照 PATH 逐項找,空項或 `.` 會解成相對路徑、從目前目錄(被打開的資料夾)找到同名檔(r4 資安席實跑);同根因的工具解析在 r3 已改成先解成絕對路徑 | https://docs.python.org/3/library/shutil.html#shutil.which ;`scripts/lumos` 的 `_lint_wt_resolve_tool`;r4-資安-sonnet.md F1 | 五支鉤子的 `_trusted_lumos`;t_r4hook_relative_lumos |
| 索引旗標照 git status:sparse-checkout 與 skip-worktree(代碼審 r5) | git 官方 `ls-files -t` 的旗標表「S skip-worktree」、`-v`「Similar to -t, but use lowercase letters for files that are marked as assume unchanged」;sparse-checkout 圈外的檔就是索引裡帶 skip-worktree 的條目。`git status` 不比這兩類檔的工作樹、只報 HEAD 對索引(實跑:暫存過再標 skip-worktree 的檔 status 是 `M `)。官方同段寫 `-t`「semi-deprecated」、建議腳本改用 status——本案正是為了不跑 status 才改用 ls-files,`-v` 的輸出格式在 git 2.39 實測穩定 | https://git-scm.com/docs/git-ls-files ;https://git-scm.com/docs/git-sparse-checkout ;https://git-scm.com/docs/git-update-index (--skip-worktree、--assume-unchanged);r5-正確性-sonnet.md F1 | `_wt_changed_nofilter`(主程式與 `check-graph-sync.py` 逐字複本);t_r5wt_sparse_checkout_no_delete;t_r5wt_skip_worktree_unchanged |
| 入口把 PATH 洗成只剩絕對項(代碼審 r5) | POSIX〈Environment Variables〉PATH:「A zero-length prefix is a legacy feature that indicates the current working directory」,寫成連續兩個冒號、開頭冒號或結尾冒號;`.` 與其他相對項也從目前目錄解。Python 官方 `os.get_exec_path` 照 PATH 逐項拆、子程序照這份清單找,空字串的 PATH 拆出一個空項;`os.defpath` 是沒設 PATH 時的預設。ast-grep(r3)、lumos(r4)、git(r5)同類第三次,依同類兩輪換形狀,改成入口洗一次、整個程序吃乾淨的 PATH | https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap08.html ;https://docs.python.org/3/library/os.html#os.get_exec_path ;既有 `_lint_wt_resolve_tool`、`_trusted_lumos`(照留當縱深);r5-資安-sonnet.md F1 | `_clean_path_env`(主程式 `main()` 與八支鉤子入口第一句,逐字複本);t_r5path_attack;t_r5path_clean_rules;t_r5path_hooks_verbatim |
| shell 掛鉤也先洗 PATH、找到的 python 要是絕對路徑(代碼審 r6) | Go 1.19 起 `os/exec` 不透過相對於目前目錄的 PATH 項解析程式(找到的是相對路徑時回 `ErrDot`);CWE-427〈Uncontrolled Search Path Element〉的防護建議:呼叫其他程式前先清理 PATH,只用完整路徑。Python 入口 r5 已洗,三支 shell 掛鉤(pre-push、pre-commit、post-commit)同一根因第四次被打穿,在 `set -u` 之後第一段濾 PATH(空了退回 `/usr/bin:/bin`);找 python 那段(七份逐字複本)取到的不是絕對路徑就當找不到,當第二層 | https://pkg.go.dev/os/exec ;https://cwe.mitre.org/data/definitions/427.html ;r6-資安-sonnet.md F1 | 三支掛鉤的 path-clean 段、python-launcher 段的 `_lumos_any_python`;t_r6sh_path_attack;t_r6sh_path_rules;t_r6sh_path_verbatim;t_r6sh_launcher_relative |

## 審計修正紀錄

- 拆出(2026-11-05):母計劃第二輪設計審 36 條加 2 條的一部分落在本案機制,依根因分七組;卷證 governance/review-reports/android寫法寫完當下自動檢查/。
- r1(2026-11-05,四席 sonnet):42 條/blocking 19;白名單改寫死、`lint-new` 自己接 SIGTERM、沿用既有狀態解法與標記寫法,回合邊界改用回合時間戳;逐條去向在 r1-intake.md。
- r2(2026-11-06,四席 sonnet):折入後依根因分十一組,照熔斷提示拆成本篇。
- 改寫(2026-11-06):十一組逐組處理,見〈待解問題〉;先做實驗 E1 到 E10(官方鉤子文件、`claude -p` 實測、git 索引實測、NIA 語料量觸發字頻率)再定設計;主要改變是寫法檢查拆成獨立鉤子、回合起點改在送出提示時記、鉤子與 lumos 之間改用 JSON、決策列併進棧別題通道。設計審待派(新卷證目錄)。

- 本篇 r1(2026-11-06,4 席):19 條/blocking 9/擋停與去重改綁回合、記帳移到鉤子真擋之後、冷卻窗不擋決策列、改名鏈追回原檔、工具群組先登記再開跑且鉤子打得到、背景與排程回合列實驗不當官方行為寫、相依改成整合分支先合第三批、新鉤子五個登記點全列、共用程式改走底線共用模組。
- 席報告與收貨:governance/review-reports/android寫法回合結束檢查與改檔前推列/(r1-通才-sonnet.md、r1-可行性-sonnet.md、r1-依據-sonnet.md、r1-架構對齊-sonnet.md、r1-intake.md)。

| 席 條 | 等級 | 去向 |
|---|---|---|
| 通才 F1 會談級上限與去重 | major 擋 | 折入:範圍 2 第 6 條改綁(會談, `prompt_id`, 批次);〈決策〉新 WHY;S6 與預期值。d1 開頭欄位已在 ede88ffb9 改成同一回合 |
| 通才 F2 記帳灌水 | major 擋 | 折入:範圍 1 第 9 條改成只記帳用法、範圍 2 第 6 條擋下並輸出後才呼叫;S2、S6 與預期值 |
| 通才 F3 冷卻窗擋掉決策列 | major 擋 | 折入:範圍 3 第 2 條決策列抽小函式、兩條路徑都算;〈不做〉、天花板 6 拿掉冷卻窗;S9 與預期值 |
| 通才 F4 缺 `prompt_id`、切工作樹沒起點 | minor | 折入:缺 `prompt_id` 當對不上;送出提示每次都記、不預篩 repo;S5、S6 |
| 通才 F5 自己起的回合沒量 | minor | 折入:列實驗 E11、S12 加案例(同依據 F1) |
| 可行性 F1 改名鏈 | major 擋 | 折入:範圍 1 第 2 條追回 HEAD 有的那端、追不到列 skipped;S1 與預期值 |
| 可行性 F2 SIGKILL 打不到工具群組 | major 擋 | 折入:範圍 1 第 7 條先擋訊號、登記(含 `--pgid-file`)再解除;範圍 2 第 4 條寬限後鉤子打登記的群組;S4、S7 與預期值 |
| 可行性 F3 大小寫 | minor | 折入:範圍 1 第 5 條另印大小寫原因;S3 |
| 可行性 F4 `-` 開頭檔名 | minor | 折入:工作樹模式檔名加 `./` 前綴;S1 |
| 依據 F1 自己起的回合當官方行為寫 | major 擋 | 折入:PRIOR-ART ① 改寫成官方原文加「沒寫、沒量」;範圍 2 第 3 條定行為(印背景或排程那一句);實驗 E11;依據表第一列 |
| 依據 F2 相依先後矛盾 | major 擋 | 折入:照裁決新增範圍 0「本機整合分支先合第三批分支再開工」;〈不做〉、相依案同步 |
| 依據 F3 登記點漏列 | major 擋 | 折入:範圍 2 開頭列五個登記點(含 `_hookshared.py` 進 `_VENDORED_TREE_FILES`);S8 |
| 依據 F4 官方措辭、八次上限 | minor | 折入:PRIOR-ART ② 用官方原文、寫明八次上限因呼叫工具歸零不算兜底;實務隱患、依據表 |
| 依據 F5 d1 舊決策出處 | minor | 折入:〈決策〉新 WHY 寫出 [[Projects/README審視五修_計劃]] d2 與翻案理由;待解第 10 組 |
| 依據 F6 平台排除題號 | minor | 折入:範圍 3 第 2 條定成「集合不含 `kt-compose`」;S9 |
| 依據 F7 載入成本與預篩順序 | minor | 折入:範圍 2 第 1 條預篩在匯入之前;送出提示路徑的匯入成本列實驗 E12 |
| 架構對齊 F1 importlib 載鉤子 | major 擋 | 折入:共用程式搬進 `_hookshared.py` 走 `sys.path.insert`;〈決策〉新 WHY;S14 |
| 架構對齊 F2 porcelain 三份 | minor | 折入:`_tg_rb_pending`、`_handoff_files` 一起收編;〈不做〉;S1 |
| 架構對齊 F3 訊號處理新慣例 | minor | 折入:範圍 1 第 7 條寫明新慣例並記進 [[Systems/hook逾時預算]](範圍 4 已列該篇) |

- 實作(2026-11-06):條款 S1 到 S14 的字面都沒改寫;下面是實作時多做或照條款精神調整的地方,理由逐條寫:
  - **第六個登記點**:新鉤子與 `_hookshared.py` 另要進錨點清單 `ANCHOR_FILES`(既有守衛 t_anchor_covers_all_auto_running_hooks 要求每支版控裡的 hook 都在裡面;計劃五個登記點沒列到)。錨點基準 `governance/anchor-baseline.json` 要人跑 anchor approve 補上,補之前 t_anchor_files_match_baseline 是紅的。S8 的測試多驗這一點。
  - **既有守衛的調整**(①②在代碼審 r1 撤回或收窄,見下面〈代碼審 r1〉):①可信來源漂移守衛原本要求每支用到 `_trusted_lumos` 的鉤子自己定義一份,改成「從 `_hookshared` 匯入也算」(共用模組那份照樣逐字比對);②匯入純度探針(t_handoff_hook_import_is_pure)原本只准讀 hook 自己與標準庫,收工點名改從同目錄匯入共用模組後,匯入系統必然讀那支檔、列一次 hook 目錄,放寬成也准這兩件(其他兄弟檔照樣違規);③三條寫死數量的測試照新增的註冊與存活清單加一(Codex 註冊 6→8、enforcement 列 25→27、unknown 12→13)。②是放寬守衛,交編排者裁。
  - **收工點名模組層**:匯入路徑改用 `os.path.abspath` 而不是 `resolve()`,匯入這支檔不碰檔案系統中繼資料;共用模組匯入失敗時整支靜默放行(`_SHARED_OK`)。
  - **白名單比條款嚴**:通過的命令整條重組(佔位符與 `>` 原樣、其餘每個詞 `shlex.quote`),不只換 `--config` 的值;禁用參數藏在 `--filter`、`--globs` 的值裡也擋(變異測試發現只靠「不在白名單」擋不到這種,補了斷言)。
  - **`-` 開頭檔名**:快照路徑一律是絕對路徑,換進 `{LINT_FILES}` 的不會以 `-` 開頭,`./` 前綴由構造保證、沒有另寫一段(S1⑨ 照樣驗)。
  - **工作樹模式的 `.lumos/lint-deps.json`、作弊比對**:照範圍 1 不跑;人讀輸出第一行提醒「作弊比對留給推送前閘」。
  - **決策 d1 開頭欄位**:已在 ede88ffb9 改成「同一回合(prompt_id)」;代碼審 r1 修正時把待解 Q1 的題目文字一起改成同一回合。
- 實作期驗收:E11、E12、E13 與 S12 結果見〈實驗〉;每道新檢查各改壞一次的結果在交付回報裡(變異複本與 git clone --shared,清 `__pycache__` 再跑)。
- **代碼審 r1(2026-11-06,七席 sonnet,範圍 `d241a3212..41f1b9abc`)**:35 條/major 10,依根因分五組全數折入;卷證 governance/review-reports/code-android寫法回合結束檢查/(七份席報告、r1-intake.md 的重現表與〈先查世界〉、r1-fix.json 逐條對測試)。設計審漏網一條:〈PRIOR-ART〉⑧ 寫「只有一種做法」,沒讀到 [[Systems/hook信任邊界]] 的分流規則(已改正)。
  - **甲 shell 執行**:工作樹模式白名單通過的命令不再交給 shell——`_lint_wt_argv` 照整詞展開佔位符組參數清單、`shell=False` 執行,SARIF 由程式把標準輸出接到檔案;佔位符不准當旗標值(`{`、`}` 進禁字);放行指令先消毒各組成再 `shlex.quote`(`_lint_waive_part`),鉤子照原樣印、不截斷,看起來不是那樣產生的整行不印;擋下原因按條累加到 1500 字、結尾「另 N 條」一定留得下(範圍 2 第 7 條「整段最多 1500 字」照守,只是不再硬截)。推送前的 `--diff` 模式照舊走 shell,不在這輪。
  - **乙 靜默失效**:`cat-file --batch` 以行尾 ` missing` 判、格式對不上或 git 失敗整次 rc3(不再當全部新檔);鉤子吞掉的逾時與失敗照 `_hookevent.mark` 記 timeout/error(刻意不查的 rc3 照記 ok);起點紀錄的時刻壞掉、payload 的 cwd 不是字串都當沒記到起點;沒有 `os.killpg` 的平台只收 lint-new 本身;status off(含 `LUMOS_SKIP_LINT_NEW`)鉤子印一行;lint-new 的 SIGTERM 處理器一併刪暫存 SARIF,SIGINT 與例外路徑先收工具群組再往上丟;鉤子開 lint-new 到登記之間收到的 SIGTERM 先記下、登記完補跑(★不用 `pthread_sigmask`:遮罩會被子程序繼承,lint-new 自己的 SIGTERM 收尾就跑不到——自測 S7② 當場抓到★)。
  - **丙 資源**:碰過的檔超過 50 支在讀任何 HEAD 內容之前就回 rc3;刪除檔只讀「有同名新增檔要拿它配對」的那幾支。
  - **丁 鉤子共用分流**:可信來源解析與逾時預算搬回每支鉤子的逐字複本,守衛恢復逐字比對、另要求「解析函式以外沒有自己從 PATH 找 lumos、真的呼叫它」與「用到預算的鉤子自己有那段」;標記檔名消毒(`_mark_name`)與 O_EXCL 佔名額(`_claim_mark`)搬進共用模組,收工點名的擋停標記與去重紀錄、收工寫法檢查的名額都走它;匯入純度探針的放寬只給真的匯入共用模組的鉤子、只給匯入系統自己那一次。收程序群組不抽共用:兩支(收工寫法檢查、記憶清掃)語意不同(一支有寬限與登記檔、一支直接殺),各自用平台判斷。
  - **戊 其餘**:`.kts` 裁定不推決策列、鉤子不送 `delta_new`;伺服端判法改用情境題自己的題號 `_KT_SIT_QID`(範圍 3 第 2 條原寫 `kt-compose`,同一組 Android 專屬判斷不借別題題號);決策列比對改用 `_kt_sit_rows_rx` 的預編譯樣式加字集合預篩;工作樹模式的 git 呼叫改走 `_lens_git`(多一個標準輸入參數);判定結果骨架兩種模式共用 `_lint_new_out`;`lint-new` 說明改成「檢查本身不寫治理帳,只有 --record-stop-block 記一筆」;改 kt 檔時整份與新內容一次取段;決策列「挑到就落標記」接受並寫明(PreToolUse 看不到編輯成不成功);工作樹模式的 git 呼叫關掉 repo 設定裡每個內容過濾器(`-c filter.<名>.clean= … required=false`,名字收不了整次 rc3)。合約席的測試缺口(rebase-apply 等四種狀態、`--budget` 起算、退出碼不是 1 不擋、上限 50 的邊界)都補了案例。
- **代碼審 r2(2026-11-07,七席 sonnet,範圍 `41f1b9abc..a1456f8f6` 的修補差異)**:25 條/major 6,依根因分五組全數折入;卷證同目錄(七份席報告、r2-intake.md 的重現表與〈先查世界〉、r2-fix.json 逐條對測試)。第一輪 35 條各席核對都已修好(資源席重跑刪大檔:4GB → 375MB)。
  - **甲 git 不信任參數單一來源**:主程式只留一份 `_git_untrusted_c`(原本 spec-freeze 一份、工作樹模式一份,各漏一項):固定關 `core.fsmonitor`、`core.hooksPath`、`diff.external`,每個過濾器的 clean、smudge、process 給空並設 `required=false`;工作樹模式的 status 一律 `--ignore-submodules=all`(子 repo 自己的過濾器名字列不到)。四條執行途徑(fsmonitor、clean、process、子 repo 過濾器)各一支用真 git 造記號檔的測試。主程式會讀工作樹的 git 呼叫盤點過:工作樹模式實際只有 `_lint_wt_*` 那幾支加讀 HEAD 內容的批次讀取,都走它;收工點名鉤子自己的 status 與它呼叫的 `impact --diff HEAD` 同族、這輪不動,回頭條件寫在 [[Systems/hook信任邊界]]。
  - **乙 失效分類明示**:`--json` 多 `unchecked_kind`;過濾器關不掉、git 算不出工作樹改動、讀不出 HEAD 內容三條標 `failed`,鉤子照欄位記 ok/timeout/error、欄位缺或不認得記 error。
  - **丙 佔位符展開一份**:抽出 `_lint_placeholder_words`,字串版與參數清單版都呼叫它;用不用 shell 只剩 `argv=` 一種傳法(`_lint_spawn_argv` 併回 `_lint_spawn`,參數清單版只把找不到執行檔或沒權限當沒裝)。
  - **丁 測試缺口**:空窗補跑的測試加「遠小於內層時限就結束」;過濾器 process、訊息長度掃邊界、放行指令含換行與控制字元、起點時刻 0 與負數、標記檔名獨立期望表、匯入純度探針兩條腿、可信來源守衛擋別名與 getattr 與裸名,各補斷言。每道新加或改過的判斷在複本裡各改壞一次:55 處 54 處翻紅;沒紅的是鉤子對 SIGINT 的兩層收法(處理器與 finally 各自都收得到,拿掉其中一層另一層照樣收,兩層各自另有會紅的案例:SIGHUP 釘處理器、例外路徑釘 finally)。
  - **戊 其餘**:起點紀錄超大整數與深層巢狀不崩;鉤子 SIGINT、SIGHUP 也收 lint-new;讀 HEAD 內容先問大小(工作樹那一版已超過上限的不讀基準);SARIF 讀取上限 64MB;開跑前清過期的暫存 SARIF;拿掉無用匯入與 `new_only`;`_mark_event` 三份逐字相同並有守衛;`_killpg` 註解照實寫三種平台判法。資安席 F2(ast-grep 照 PATH 找)不改程式,回頭條件寫在 [[Systems/pitfalls-code-loop]]。
- **代碼審 r3(2026-11-07,七席 sonnet,範圍 `a1456f8f6..8717114b0` 的修補差異)**:22 條/major 5,依編排者裁定分六組;三條附理由放行(正確性 F3 超大檔縮小後舊告警當新增、資源 F2 64MB 上限下記憶體約 0.9GB、架構對齊 F5 `_nodehome_cat_*` 沒帶 GIT_OPTIONAL_LOCKS),其餘折入;卷證同目錄(七份席報告、r3-fix.json 逐條對測試)。
  - **甲 換形狀:不跑會經內容過濾器的指令**:列過濾器名字逐個關第三次被打穿(名字含非 UTF-8 位元組時 `--get-regexp` 列不到),整類拿掉。找工作樹改動改走 `_wt_changed_nofilter`(`ls-tree -r`、`ls-files -s`、`ls-files -o`、`hash-object --no-filters --stdin-paths` 跟索引比,索引記的時間大小沒變而且比索引檔早寫的不算雜湊);`_git_untrusted_c` 只留固定三項;收工點名鉤子放逐字複本加守衛。代價:用了 LFS、autocrlf 這類真過濾器的專案會多查幾支、工作樹那側換檔名又改內容的改名當新檔(天花板 4),方向都是多查不漏查。收工點名呼叫的影響分析照編排者裁定加鉤子專用選項 `--worktree-nofilter`(只准搭 `--diff HEAD --sync-check`):候選與模式走 `_wt_changed_nofilter`,改動內容用 difflib 算(事故的 `content:` 觸發吃改動內容,只用路徑會漏報),其他呼叫端行為不變。
  - **乙 git 出錯不當刻意不查**:沒有 HEAD 只認 `rev-parse --verify -q` 回 1;宣告檔在不在 HEAD 改用 `ls-tree` 問;其他退出碼一律 `failed`。
  - **丙 SARIF 上限只管工作樹模式**:推送前閘照舊整份解析(原本超過上限會被歸成環境不可用、自動放行)。
  - **丁 逐字複本守衛擋重複定義**:`_trusted_lumos`、`_mark_event`、`_wt_changed_nofilter` 三組守衛要求每支檔恰好一個定義,擋改綁、匯入別名與字串指名。
  - **戊 失效分類收成一處**:判定層不補預設,`report_only`、`sep_emptied` 各自明寫 `deliberate`,沒寫明的由 JSON 層落 `failed`;`timeout` 用常數;鉤子遇到不是字串的種類值記 error。
  - **己 其餘**:三支鉤子讀 stdin 統一接壞形狀 rc0;工作樹模式的工具先解成絕對路徑(PATH 空項、相對路徑、repo 裡的同名檔都不跑)、子程序設 `RLIMIT_FSIZE`;起點 inf、匯入純度探針「只放共用模組」補案例;範圍 2 第 5 條補寫 rc3 照 `unchecked_kind` 記事件;`pre` 一律往下傳;門檻判斷收成 `_lint_over_limit`。
- **代碼審 r4(2026-11-07,七席 sonnet,範圍 `8717114b0..ffce2c71a` 的修補差異)**:18 條/major 8,依編排者裁定分五組;兩條附理由放行(合約 F1 守衛擋不住字串拼接的間接 PATH 查找、資源 F3 工具正常結束後的子孫程序),其餘折入;卷證同目錄(七份席報告、r4-fix.json 逐條對測試)。
  - **甲 路徑基準一律是 repo 根**:`_wt_changed_nofilter`(兩份逐字複本)先取 `rev-parse --show-toplevel`,之後每個 git 指令帶 `-C <根>`、`ls-files` 加 `--full-name`、`paths` 補 `--show-prefix`;lint-new `--worktree` 的 `--repo` 指子目錄時改在 repo 根判;影響分析從根讀檔。
  - **乙 影響分析自己算差異**:改動行改用兩版數行次數相減(`_impact_line_delta`,線性時間);先判是不是程式碼才讀內容、兩版合計上限 8MB、工作樹那一版逐支讀逐支放;路徑含換行或結尾是 CR 的只用路徑;刪除檔模式取 HEAD、首行讀 HEAD 那一版;整形抽成 `_impact_hunk_query`、`_impact_mode_entry`、`_impact_wants_head`,git diff 那條也呼叫。
  - **丙 鉤子找 lumos 只認絕對路徑**:五支鉤子 `_trusted_lumos` 的 `_ok` 第一步拒相對路徑。
  - **丁 找改動的邊界**:檔名結尾是 CR 的當改過;補時間等於索引檔時間、時間同大小不同、雜湊行數對不上、兩支同內容刪除檔四個案例。
  - **戊 筆記與小清理**:〈依據來源〉補五列、三列改成現況或標已被取代;`_git_untrusted_c` 拿掉不用的參數;種類寫在哪的註解照實改;兩份不信任清單的差異照實寫、守衛改雙向。
