Reading additional input from stdin...
OpenAI Codex v0.153.2
--------
workdir: /Users/enzo/harness/lumos-toolchain
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: read-only
reasoning effort: low
reasoning summaries: none
session id: 01a07ae6-8946-7b20-9762-fcb6c8e76317
--------
user
你是外家否決席(不是編排者那一家)。這是**外部第三方投稿的設計 spec 第二版**,任務是找出作者沒看到的洞。

工作目錄 /Users/enzo/harness/lumos-toolchain(唯讀查證,不要改任何檔)
凍結審材:governance/review-reports/進度從提交推導-v2/r1-snapshot.md(192 行)
★第一版的完整卷證(五席報告+前掃)在 `governance/review-reports/進度從提交推導/`——請自己去讀★

**背景**:第一版被五席打死(去重後九群、六個 blocker 級),Enzo 裁整份重寫。第一版的做法是「工作項用 [SN] 條款標記取名、完成的提交掛 git trailer、進度從 git 與 CI 算」。第二版整個換掉,核心變成:

> ★不推論「完成」,只報告「這個任務宣告的證據現在是什麼狀態」——對計劃宣告的測試名當場在工作樹上跑,回報「不存在 / 存在但紅 / 存在且綠」。沒有第四種叫完成。★

**已跑過不要重報**:refcheck(v2 零檔案宣稱)、prose-lint(零命中)、pitfalls --check(零命中)、前掃四類。前掃已折入六項:①「重用既有 spec-trace 抽取」是假前提(它抽的是 [SN] 條款,與測試名無關)②「doctor Check Y 會抓測試名漂移」不成立(它只掃 type:system,實作計畫全是 type:project,而且刻意排除有正當理由)③47ms 那個數字被誤用(量的是 v1 已死的 trailer 掃描)④補測 v2 真效能(單任務 0.8–1.88 秒;關鍵字不精確命中一整族 23.4 秒)⑤樣式清單補齊(含抽不出識別碼的中文散文型)⑥「任務段」分母無唯一機械定義(73/74/83 都量過)。

**火力集中處**

1. ★**第二版是不是只是把問題換個地方?**★ 逐條對第一版的六個 blocker 群,判斷 v2 的處理是真解掉還是換說法。特別是 r1 說「打穿根因前提」的那兩條:**未提交態**、**提交夾帶**。v2 說「讀工作樹不讀提交歷史」就解了——真的嗎?

2. ★**「當場跑測試」這個新核心自己有沒有新的洞?**★ 它讀的是工作樹**現狀**:
   - 那麼「綠」證明了什麼?會不會因為**別人**的改動而綠/而紅?
   - 兩個 session 共用同一棵工作樹(這個 repo 有記錄在案的事故),一邊正在改、一邊跑查詢,結果可信嗎?
   - `-k` 是子字串比對——宣告 `t_impact` 會不會把 `t_impact_bfs` 也拉進來,讓一個任務「借」到別的任務的綠?**實測一次。**

3. ★**三態夠不夠?**★ 測試被 skip、超時、環境跑不動、名字打錯、還沒寫——這五種在輸出上分不分得出來?分不出來會不會又生出假狀態?

4. **d3 是 Enzo 裁的**(完成判準掛實作端看測試、功能級)。v2 說自己「不推論完成」——**那 v2 到底有沒有實現 d3?** 還是它其實悄悄放棄了 Enzo 要的東西、只做了一個較弱的查詢?這一條請直說。

5. **這份會不會其實不該做**:它自己仍寫著「本案的價值還沒有本地證據」。用這個專案自己的判準(有症狀、有消費者、最小解在哪一層)衡量,立案成立嗎?第一版被打死之後,這個問題更該問。

6. 有沒有**第五條路**:不用測試、不用 trailer、不用 CI,也能讓「做到哪」變成算得出來的?

**規則**
- 每條 finding 附 `引句:「<逐字 ≥10 字,抄自凍結審材>」`(★引句內不要再包「」★)、`severity: blocker|major|minor`、`blocking: 是/否`(兩欄不得矛盾)。
- 審材外證據用 `file: \`路徑:行號\``(反引號必加),不得用引句格式主張審材外內容。
- 敘述每條 ≤3 句,不准「可能/建議考慮」這種收尾。
- 報告第一行寫一行獨立的 `severity: <本輪最高>`;乾淨也要寫 `severity: clean`。
- ★沒實際查證過的猜測不要寫成 finding★。你能開檔、能跑指令,請用。
hook: SessionStart
hook: SessionStart
hook: SessionStart Completed
hook: SessionStart Completed
codex
我會用 `lumos-project-notes` 依圖譜規矩進場，先查凍結審材與第一版卷證的脈絡，再逐項做唯讀驗證；`-k` 子字串問題會直接實測。
exec
/bin/zsh -lc 'python3 scripts/lumos search "進度 提交 推導"' in /Users/enzo/harness/lumos-toolchain
 succeeded in 431ms:
(多詞回退:你查的整串詞在未作廢的節點的可見文字裡找不到完全一致的,改成每個詞分開查、有出現就算;逐詞覆蓋 進度:20  提交:28  推導:28)
(已隱藏 3 筆作廢結果;要看的話加 --include-superseded)
提醒:命中≠查完——搜尋只告訴你「哪裡可能有」,不是完整內容;光看摘要就判「圖譜沒記」以前真的出過錯。下結論前先讀全文:lumos show <節點>
 11.820  Projects/進度從提交推導_計劃.md  [進度,提交,推導]
    17 [KEY]: KEY:立案(2026-09-07,Enzo 裁「首要工作=讓做到哪一步也能同步並且可信」後再切一刀)——★本案不是做進度追蹤器,是讓「完成」那個動作自己留下紀錄★
    19 [KEY]: KEY:★症狀數字(2026-09-07 當場量)★:Projects 標進行中 43 篇其中 17 篇 >30 天沒動;一篇 status=done 的實作計畫 60 個框 0 …
    20 [KEY]: KEY:★因果鏈沒有分叉,斷點在最前面★——工作項沒有在筆記之外還活著的識別碼 → 提交掛不上 → 沒有可追加的紀錄 → 完成狀態只能手寫 → 一定漂
    21 [KEY]: KEY:★PRIOR-ART 最強的一條:不用發明格式★——git 原生有 trailer,`git log --format='%(trailers:key=X,valueonl…
    22 [KEY]: KEY:設計三步(各可獨立交付)=[S1] 工作項取名(只定慣例不寫程式)/[S2] 完成的提交掛 `Task: <識別碼>` trailer/[S3] 唯讀查詢從 git 算進度…
    24 [KEY]: KEY:★誠實天花板:最多蓋到四分之三★——74 個任務段裡 56 個(75%)抽得出對應測試名,剩 18 個天生沒有(改 skill 散文/圖譜回填/真機驗收);那類沒有提交可掛…
    25 [KEY]: KEY:★待裁四題★①識別碼從哪來(沿用 50 群的 #N / 每份計劃 T1..Tn 會撞名 / 計劃名+任務號)②trailer 鍵名(避開既有與世界慣例語意衝突)③「完成」定…
    26 [KEY]: KEY:驗收線=不讀勾選框就答得出每個工作項有沒有被提交掛過與最後一次何時;對那 18 個算不出來的**明說算不出來**;三步各有測試且 ★fixture 用真的呼叫 git 產生…
    … 還有 17 處
  7.097  Projects/執行DAG_調研.md  [進度,提交]
    14 [KEY]: KEY:★腐化數字(★量測時點 2026-09-07,含活計數,引用必帶時點★)★:Projects 標 doing 43 篇(母體 155,含本篇自己)、其中 17 篇 >30 …
    16 [KEY]: KEY:★settle 前例極性被翻轉(外家 f3)★——`.lumos/settle/公開精簡版-settle.json` 35 條原本被當「可抄的結構化進度前例」,實查是**死…
    50 [body]: PRIOR-ART:①最小解在既有機制層——「唯一下一動作」的神諭已經有了(`lumos loop next`,只讀帳本結構不讀散文),只差一個「列出現在開著的迴圈」的入口;結構化…
    68 [body]: 1. **實作計畫筆記的任務拆解**——T1..Tn、「包①→②→③嚴格順序」、每任務寫明改哪/測什麼/斷言什麼,底下「進度」段記日期與教訓。
    100 [body]: | [[Projects/全repo審視_計劃]] 的 50 群主清單 | **表格沒有「做完沒」這一欄** | 進度靠翻 git 提交訊息裡的 `#編號` 回推;開頭「一件都還沒…
    107 [body]: 1. **只讀結構不讀散文的進度指令**:`lumos loop verify-progress` 的 help 自述「不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)」…
    108 [body]: 2. **★結構化逐條進度清單——原稿當成正面前例,外家查證後翻成反證★**:`.lumos/settle/公開精簡版-settle.json`,35 條,每條 `{id, kin…
    170 [body]: - **commit trailer / session manifest**:解「提交夾帶、歸屬讀不出來」,成本極低。
  7.004  Issues/推新分支時風險分級拿空樹當起點.md  [提交,推導]
    15 [KEY]: KEY:★這是刻意的 fallback 不是 bug★——scripts/hooks/pre-push 範圍推導三分支,註解明寫「新 ref(含首推 main:遠端無此 ref)→…
    17 [KEY]: KEY:誠實界線——影響面比第一眼小:這個 repo 慣例是本地開分支、本地合併、★只推 main★(實查遠端只有 main 一個分支,本地有 8 個功能分支+多筆 merge 提…
    31 [body]: `scripts/hooks/pre-push` 的範圍推導有三條分支,註解寫得很清楚:
    56 [body]: - **這個 repo 的慣例是本地開分支、本地合併、只推 main**。實查:遠端 `git ls-remote --heads Lumos` ★只有 `main` 一個分支★,…
  6.957  Systems/guard-kill.md  [提交,推導]
    16 [KEY]: KEY:宣告式壞法(人寫,從業務行為推導非實作反轉;繞開等價變異不可判定)｜run_cmd由config宣告(platforms.X.run_cmd/legacy test.run…
    18 [★DEBT★]: KEY:★DEBT★ hydration(未提交帶入)與lockfile v1砍(否決位裁);E2E maestro {method}不適用;冷build成本;submodule不…
  6.166  Projects/guard殺傷力驗證_計劃.md  [提交,推導]
    49 [★INVARIANT★]: 1. **壞法由人宣告，不自動生成；配方存節點級 `kill_recipes` frontmatter 欄位（r1 折入：不進 decisions——decisions 是節點級平…
    52 [body]: 3. **原始碼層隔離 + baseline 前置（r1 折入：正名——worktree 只隔離檔案，不隔離 DB/埠/外部狀態）**：對**配方 platform 的 repo …
    80 [body]: - HEAD 基準：worktree **看不到**主樹未 commit 的新測試檔、kill 以已提交內容跑（r2 descope 的反向迴歸）。
    87 [body]: - dirty 工作樹警告：未提交變更時 kill 印警告且以 HEAD 內容跑。
    98 [body]: - **r1（2026-07-10，panel W=5：4 canaried opus（新出題程序首跑：載重錨定+haiku 探針 4/4 probe:pass+事故庫無匹配走輪替…
    115 [body]: - ISO 26262 fault injection、DO-178C requirements-based coverage（需求推導壞法、人審把關）
  5.142  Projects/loop三輪壓縮_計劃.md  [提交,推導]
    18 [KEY]: KEY:收斂判準(2026-07-09交叉查文獻升級)=falsification-存活(辯方零≥major,borrow falsification>voting)∧低分歧(W審…
    52 [body]: 一輪 panel 收斂 = **四條合取**(全建在 framing 汙染不到的結構上;推導與文獻見下「散文收斂」節):
    87 [body]: - **F3 agreement 形式定義(2026-07-09 交叉查文獻升級:從二值門檻→falsification+低分歧+自適應提交)**:收斂判準**不是**「辯方後 m…
    90 [body]: - **③ 自適應提交(borrow CGES 2511.02603 / DASE 2605.04236)**:round-1 panel 若 falsification 後**全…
  3.824  Verification/2026-08-04_design-loop重設計落地T1-T7.md  [進度]
    24 [body]: **計畫**：[[Projects/design-loop重設計_實作計畫]]（逐包進度與教訓記於該節點〈進度〉）
  3.803  Systems/anchor-integrity.md  [提交]
    67 [body]: ## ★簽名檔本身沒提交,是這道守衛的天生破口(2026-09-06 實際被 CI 咬到)★
    69 [body]: **發生什麼**:折完一輪代碼審要推,推送前的閘擋我「把關檔改過沒簽名」。我簽了名、也把改動提交了——但只提交了知識庫那個資料夾,而**簽名檔放在治理資料夾底下**,沒進去。推送過…
    76 [body]: **最坑的地方**:CI 的錯誤訊息會叫你「重新核可並留理由」——照做也沒用,因為問題根本不是沒簽名,是簽了沒提交。訊息把人指向錯的方向,而這種紅燈又特別像「守衛壞了」。
    78 [body]: **怎麼修的**:推送前的閘多一道——簽名檔如果處在「改過但沒提交」的狀態就擋下,訊息直接講「沒提交」並給提交指令,不叫人再簽一次。守衛配的是**行為測試不是字串比對**:真的搭一…
  3.789  Issues/同工作區多session並行改動.md  [提交]
    13 [KEY]: KEY:2026-08-22 一天三型:①數字漂移(紅得像自己改壞的)②提交夾帶(git add -A 把對方全部交付一起 commit、訊息只寫自己那件)③變數共用(結果好但純靠…
    15 [KEY]: KEY:候選解多兩條——(d) 同工作區 session 互相通報(這次真正管用的就是對方主動傳訊,機器對機器不是人轉述;它擋的是誤修與提交夾帶,不是壞檔本身,而且要兩邊都記得);…
    40 [body]: ### ② 提交夾帶:訊息完全對不上內容
    74 [body]: - **(b) 提交時提醒**:pre-commit 看 `git diff --cached` 涉及的檔,若有檔案的
    114 [body]: - 前三型(數字漂移、提交夾帶、變數共用)都是**事後**才發現,但發現時證據還在。
    122 [body]: - **沒有夾帶**:我最後一個提交(08b0e61)時間點剛好在對方開始改之前,查證過沒有夾到。
    135 [body]: ★它擋的是「誤修」與「提交夾帶」,不是壞檔本身★——知道有人在動那支檔,你就不會去修它。
    202 [body]: 那能擋掉的是**誤修**(第四型裡差一點發生的破壞性補救),以及第二型的提交夾帶。
    … 還有 1 處
  3.763  Projects/code階段強化_計劃.md  [推導]
    18 [KEY]: KEY:[S3]性質測試席(選配,r1/r2 修)——開席=兩機械錨(tier=high ∧ impact 命中星標合約節點)+人工核純函式+具推導源(docstring/型別/圖…
    23 [DECISION]: DECISION:[2026-07-18]S4 拒收記理由防重提;S3 觸發改開席四要件(兩機械錨+一人工核+推導源查核,r1-r3 逐輪收窄);S3 免辯方路由撤除(r1 三方共…
    57 [body]: **現況與舊帳**:07-15 圖譜判「自動生成 property 測試 oracle 不可靠」(agent 自己發明錯誤期望→誤報)。Anthropic 2026-07 配方:推…
    60 [★INVARIANT★]: - **觸發(開席四要件=兩機械錨+一人工核+一推導源查核,r1 收窄、r2 增訂、r3 正名)**:①tier=high **且** ②`lumos impact --diff`…
    61 [body]: - **流程**:席位 agent 讀 diff 涉及的純邏輯函式+文件/型別註解 → 推導 2-3 條性質(從文件推導,禁憑空)→ 該棧 PBT 框架寫測試(C#=CsCheck…
    62 [★INVARIANT★]: - **產出(r1 撤免辯方)**:反例的**可重現性**免爭(那是機械事實);性質的**合法性必過辯方**——辯方(依 S5 預設 Codex)專問:「這條性質真是該函式的業務合…
    123 [body]: 10. [s2] S3 缺「無文件純函式」擋板(硬推=自證 oracle 復辟)→ 開席第四要件:具推導源,缺源不開席留痕。
  3.721  Systems/開發工作流總覽.md  [提交]
    17 [FLOW]: FLOW:①寫計劃(先查圖譜三步;開審第一輪先列出主題已有的節點,避免重複開案)→②設計送審(design-loop:派工時自動把相關節點附給每個審查員[2026-09-05 起 …
    75 [body]: | ③ | impact hook+Stop hook+pre-commit(兩家同一批) | 每次提交都同步節點;收工沒補的當下擋一次(兩家) |
  3.696  Verification/2026-08-24_節點還原SOP落地.md  [提交]
    5 [fm:valid_under]: valid_under: "skill/索引/範本/hook 六處同步版(2026-08-24);探針語料 23 題;Landmark 實跑於 HEAD=28310ee 未提交工作…
    10 [KEY]: KEY:[S7] 實跑=CMS_Landmark(真 brownfield:三年 C# 商業系統、零圖譜、自有 repo):init --no-hooks→骨架 MOC→兩節點(限…
    27 [body]: - Landmark 的改動(vault 5 篇+CLAUDE.md 注入區塊):✅ Enzo 裁**擱置**(2026-08-26)——維持未提交、不收版控、不裝 hooks;該…
  3.695  Issues/真相源實質單一作者.md  [提交]
    14 [KEY]: KEY:本 repo 提交 1,329 筆,其中同一人(Enzo/t)1,311 筆佔 98.6%;另兩位作者合計 18 筆
    37 [body]: | 作者 | 提交數 |
  3.687  Verification/2026-07-04_pitfalls-code-loop.md  [推導]
    11 [fm:valid_under]: valid_under: cmd_pitfalls 三模式(PITFALL_CLASSES 詞表+剝除對齊 assess_spec 含防呆+--check 節檢查+--diff p…
    15 [VERIFY]: VERIFY:行號推導人工+機器雙驗;pattern 去重疊(SELECT/寫入)證第6條非死碼;三道防污染語意經 review 逐條確認;gate G2 段一字未動比對
  3.664  Projects/圖譜結構化查詢_計劃.md  [進度]
    33 [★INVARIANT★]: | risk/金流 且帶 ★INVARIANT★ | search「金流」32 筆噪音 / contracts 全庫 21 條人肉挑 | 土法模擬 8(實收 7:1 筆為待辦散文誤…
    62 [body]: ## 進度
  3.662  Issues/loop-next吐不可宣告的tier.md  [推導]
    53 [body]: `LOOP_TIERS = ("light", "standard", "high")`。**`legacy` 不是可宣告值**——它只是「無定錨舊帳 ＋ legacy 格式」的推…
    70 [body]: | `legacy`（推導） | 1 | **6** |
    107 [body]: **兩條現場成立前置**：① `tier == "legacy"` 且 `phase == "plant-canary"`（證明真的走到 legacy 推導路徑）
  3.660  Projects/關係層主網_實作計畫.md  [進度,提交]
    54 [body]: **進度：M1✅ M2✅ M3✅ M4✅——整包完工（2026-07-15，全套 1103 tests 綠）**：[[Verification/2026-07-15_主網M1_決策…
    73 [body]: - ID 穩定性：一旦指派，即使決策被 supersede 也**保留原 id**（翻案是加 `valid:false`、不刪不換號）；reindex 只補缺、不重排既有。**唯一…
    112 [body]: - **並行（🟠，D10 折入：降宣稱+釘實作形）**：append-only 免 in-place lost-update；寫入走**專用 helper——O_APPEND fd…
  3.651  Issues/探針沙盒能推到真遠端.md  [提交]
    26 [body]: **發現方式**:下午推正式提交被拒(遠端領先),看到「probe snapshot」這個只該出現在沙盒裡的訊息。
    27 [body]: 已用 `--force-with-lease` 覆蓋(確認上面只有那一筆、沒吃掉真提交)。
    35 [body]: 本 repo 歷史上所有 `t@t.t` 提交同此。身分已改 `8yinpro@gmail.com`(本 repo,不動全域)。
  3.641  Verification/2026-07-16_replay校準baseline_v0.md  [推導]
    16 [KEY]: KEY:三結論——①haiku 剖面=grep 可得能抓(白名單/詞不存在),推理/交叉對照型全滅→pre-flight 的 haiku 只配機械清單,語意審最低配 sonnet …
    61 [body]: 3. **洩漏效應分層**:sonnet 先獨立推導、拿 code 演化當驗算並主動揭露;haiku 直接抄。釘住對 haiku 反而提升(答案卡拿走後 grep 到的就是真缺陷態…
  3.548  Projects/loop機械脊椎M1包_計劃.md  [推導]
    19 [KEY]: KEY:#1 loop next——`lumos loop next <id> [--json] [--tier standard|high|light]` 唯讀讀 canary-…
    24 [KEY]: KEY:落地同步義務(七項,由折入衍生,枚舉寫死)——skills/lumos-design-loop/SKILL.md(record 時序 C4/手算 N 改指 next/lig…
    51 [body]: - **無 `--tier` 的身分推導（r3 折入；r7 Codex 終確認統一——原兩處「預設 standard」殘句與 tier 定錨規則分叉，high 可被合法降 stan…
    60 [body]: - `width`：tier→席數（light=1／standard=3／high=5；`--tier` 不給→**依身分推導（定錨優先，見上；r7 統一——舊「預設 standa…
    63 [body]: - **席數下限（r4 新 major；r5 legacy 值；r6 Codex 終判雙補——①數記錄筆數可被同席重複 append 灌滿 ②tier 不持久化，下次省略 --ti…
    135 [body]: - **C1 next 輸入不足不得宣告 converged（major）**：gate 合取依賴 --need/--spec/--repo/--panel——next 改為完整 …
    143 [body]: - **S1-F-CAP（major）**：無 --tier 預設 standard 與 cap 的 legacy 判定自相矛盾——改帳面格式推導（legacy→1/6；panel…
    178 [body]: - **r1（附加式 canary，panel 4 sonnet＋Codex 帶餌＋Codex 無餌否決＋spec 合規席）**：canary 2/5 輪無效——**植入工藝第三筆…
  3.470  Projects/結清式收斂_計劃.md  [進度]
    18 [KEY]: KEY:★首個真實 loop dogfood(2026-07-31,對象=[[Projects/公開精簡版_計劃]];該 spec 兩輪 panel 未收斂、capture-rec…
    42 [body]: - [S3] **獨立進度驗證器（LoopTrap 貴的那半）**：收斂／進度判斷由一個**看不到被審材料**的小驗證器覆核——只讀帳面結構欄位（findings 計數、settl…
    134 [body]: - **進度會累積**：14/35 已結清且只要 spec sha 不動就不必重做；K-streak 模式下每輪重來。這是結清模式對長 spec 的真實優勢。
  3.451  Projects/節點靜態先驗_調研.md  [推導]
    22 [body]: **值得做，但不是「每節點手填三個數字」——是三個機械推導、可消融的 ranking features。**
    50 [body]: ## 手標 vs 機械推導（裁定）
    52 [body]: 特徵機械推導、語意由人標：人只負責既有 type/status/合約/邊;嚴禁手填 `authority: 0.83` 類浮點（GIGO/漂移/自我強化）;若需例外只開離散可 li…
  3.420  Verification/2026-07-29_CI回流閉環v1落地.md  [推導]
    54 [body]: **修法＝把守衛面推廣**：新增 `t_docs_enumeration_drift`，把「禁止手寫數字／列舉」從指令數擴到三類機械可推導事實——
    59 [body]: **通則入帳**：凡文件宣稱一個「可從碼機械推導的清單或數字」，就該有一條這樣的測試——否則它遲早漂移，而且是靠人發現。
    85 [body]: - 值域守衛範圍加上 `Systems/guard-kill.md`（圖譜節點本身），態數宣稱也改為從碼推導；同時清掉 code 裡
  3.381  Systems/delguard.md  [提交]
    27 [KEY]: KEY:[2026-09-06]★逾時降級的真因是命中行數,不是 token 數★——帳上 30% 執行是逾時降級(守衛在半盲狀態下擋人)。原以為跟 token 數有關,量出來是:…
  3.369  Verification/2026-07-28_settle收斂閘.md  [進度]
    42 [body]: - S2（結構化壓縮）與 S3（獨立進度驗證器）未實作、未在本篇認領範圍（方括號條款記號僅用於上方 S1 認領行,此處刻意不用——spec-trace 提及即認領）。
  3.345  Verification/2026-07-28_S2S3壓縮與驗證器.md  [進度]
    21 [body]: # Verification: S2 結構化壓縮＋S3 獨立進度驗證器（2026-07-28）
  3.266  Projects/版本發布流程_計劃.md  [進度,提交]
    167 [body]: ## 進度(2026-09-06 全 repo 審視補記)
    190 [body]: - **[S8] `lumos --version`**:印版本標籤 + 內容指紋(短碼、分支、有沒有未提交的改動),
  3.238  Systems/pitfalls-code-loop.md  [推導]
    29 [FLOW]: FLOW:pitfalls spec 模式(剝除對齊 assess_spec+防呆→掃 PITFALL_CLASSES 四類→印通用 4 問(3 固定+1 風險類反問,2026-0…
    48 [fm:context]: context: 使用者質疑代碼 canary 污染風險比 spec 嚴重(假 hunk 改變語意、reviewer 推導衍生幻影 findings)
  3.214  Projects/doctor-run事件_計劃.md  [推導]
    35 [body]: - ★「已清」的判讀方式★:本事件**不**列受檢節點(nodes 恆空);「某節點已清」由讀帳方推導=「該 run 有 doctor-run 標記,但該 run 內沒有該節點的 …
    51 [body]: - **std r1(2026-08-21,三席同門+外家 gemini)**:major 1(s1:過濾落在 `ded` 上會連 stats 一起濾掉,測試只斷 gate 名會假…
  3.201  Projects/全repo審視_計劃.md  [進度,提交]
    12 [body]: > 白話:2026-09-05 夜到 09-06,派 16 個不同鏡頭的乾淨 agent 把整個 repo 掃一遍找可優化處,每條再派兩個反方(一個查事實、一個查圖譜先例與家規)去…
    88 [body]: ## (舊)中途進度快照
    135 [body]: - repo 根目錄有一支 5 位元組的測試殘骸(內容是字面空陣列),跟著一個自主迴圈的 commit 被順手提交。
    318 [body]: - **為什麼**:新手照 ONBOARDING 走,第一步就撞到 2026-06-26 拆掉、至今被靜默吞掉的 ./install.sh --copy(以為拿到複製版,其實是 s…
    482 [body]: - 同步改了提交前守衛的排除清單(既有漂移守衛會逐項比對兩份清單),加一條測試釘住。
    503 [body]: - **★blocker:我把硬閘弄鬆了★**。刪除守衛的排除清單跟提交前守衛的豁免清單,有一條既有的漂移守衛逼它們逐字相同。我加了治理目錄到前者,為了讓漂移守衛過,就機械照抄到後…
    531 [body]: - **定案:聯集合併**。這幾本是 append-only 的 JSONL,正確解是把兩邊的行取聯集:本機那份讀進記憶體 → 還原到已提交版 → 拉 → 把本機獨有的行補回去。非…
    538 [body]: - **★blocker:資料會靜默遺失★**。聯集合併用「集合判有沒有」,而帳本是事件序列不是集合。審查席對本 repo 實際量:治理帳有 487 行內容完全重複、用量帳有 8 …
    … 還有 4 處
  3.152  Verification/2026-08-22_狀態表過期偵測.md  [進度]
    13 [body]: > 白話:一篇筆記用表格記進度,某一格寫著「待辦」,但那格連到的節點早就做完了。
  3.116  Systems/canary-audit.md  [提交]
    43 [KEY]: KEY:提交的文件永遠不含 canary;token(CANARY-<hex>)只是定位記號,非「抓到」的機械證明——唯一算數的是審計員正確描述了那個瑕疵
    117 [body]: 1. 在工作副本植 1 個**純加性** canary,給唯一 token。**提交的文件永遠不含 canary。**
  3.071  Verification/2026-08-22_guard-kill首次真跑.md  [推導]
    28 [body]: - 壞法是人宣告的,沒有自動生成;這是設計如此(從業務行為推導,不從實作反轉)。
  3.038  Verification/2026-08-08_風險類反問v1落地.md  [推導]
    21 [body]: ## 設計脈絡(Enzo 一連串追問推導)
  2.970  Projects/派工編制資料化_計劃.md  [推導]
    55 [body]: ★**code/standard(循序單 reviewer)v1 不入表、編制對帳不涵蓋**(r1 整合席 blocker,CLI 實測重現):既有 `cmd_loop_next`…
    66 [body]: - kind 判定用 loop id 前綴三值規則(同 S1;**per-command 訊息刻意不同**:loop next 無對帳可跳,indeterminate→roster…
    93 [body]: 2. `t_loop_next_roster`:design/standard 與 code/high 的 `loop next --json` 含 roster 欄且席組成正確;…
  2.964  Verification/2026-08-23_關於欄位離線預標驗證.md  [進度]
    34 [body]: 更糟的是中途查進度時看到 71 個子行程,**就跟 Enzo 說「它真的在逐篇讀所以慢」**——
  2.958  Issues/簿記白名單漏canary與bypass帳.md  [提交]
    27 [body]: Enzo 指示「優化這些部分」——`_BOOKKEEPING_FILES`(scripts/lumos)補 `docs/.canary-log.jsonl` + `docs/.by…
  2.937  Projects/prepush主幹範圍修法_計劃.md  [推導]
    40 [body]: - **逐 ref 推導檢查範圍**：
    49 [body]: - 原 merge-base 推導整段移除（被 stdin 範圍取代）。**git 語意誠實記（r2 Codex#3 minor）**：`remote_sha..local_sha…
    53 [body]: - **旗標名＝`--diff`（r1 s4-F3 折入，原 `--range` 與全 CLI 不一致）**：對齊 `pitfalls --diff`/`cochange --di…
  2.936  Projects/檔案測試依賴地圖_計劃.md  [提交]
    114 [body]: 7. 陳舊三訊號：①非祖先 sha；②build 後候選檔 commit；②′build 後刪檔；③未提交工作區改動；
    126 [body]: 19. 陳舊③：工作區未提交改動觸發（porcelain 解析）；CJK 檔名於②③命中（quotePath）；
    156 [body]: - map 陳舊誤導 → [S2] 三訊號軟提示（祖先鏈＋build 後候選檔異動＋未提交工作區改動）。
    177 [body]: - [major 折入] ① 測試檔判定句「完整檔名 vs stem」自相矛盾 → 拆三子句各自明定比對域（席1+席2）；② `foo_spec` 示例與綴詞表矛盾（會種回 r3 …
    181 [body]: [major] ①駝峰邊界殺自家旗艦例（`.` 前字元）→ 邊界改「前字元非大寫」＋縮寫類取捨記帳（席2+席3）；②剝離規則未複述判定兩套規則＋`ABTest`/`Foo_TEST…
  2.885  Systems/lumos-cli-lifecycle.md  [提交]
    28 [★DEBT★]: KEY:★DEBT★ pull 成功但來源工作區髒(未提交改動)仍會被 vendor 出去——本輪未擋,因來源 repo 的 docs/.governance-log.jsonl …
  2.776  Verification/2026-07-31_slim-claude-md注入.md  [推導]
    49 [body]: - 最初嘗試用「依既有內容結尾自動判斷分隔符」(0/1/2 個換行三種情況)的寫法,推導卸載時要精確逆算分隔符長度過於脆弱;改用「固定分隔符恆為一個 `\n`」的規則後,插入與移除…
  2.729  Verification/2026-07-28_testmap落地與Landmark轉正.md  [提交]
    31 [body]: - 覆蓋 [S3] 全 25 項：naming 各型（含點分 basename 去尾點、`_spec` 直剝、`Foo_TESTS` 底線不敏感、同名唯一 `__tests__/B…
  2.632  Verification/2026-07-31_slim-claude-md第三次裁定取代與備份還原.md  [提交]
    84 [body]: `python3 scripts/test_lumos.py -k slim`——187 checks 全綠(含既有 t_slim_gate/t_slim_readme_asser…
  2.614  Projects/節點還原SOP_計劃.md  [推導]
    15 [KEY]: KEY:★v2-r2 審計(2026-08-24,5 席;arch 零發現)★:「乾淨」判準修正=機械閘為準(現行 panel K=2 連續兩輪,v2-r1 誤明定 K=1;--d…
    197 [body]: - **v2-r3(2026-08-24,5 席,v2 上限輪)**:原始 16 條(s1=2、s2=2、s3=6、arch=2、ext=4),去重約 10,全數折入、零放行。實錘…
    206 [body]: ★達上限未收斂後 Enzo 裁甲(2026-08-24,d7)★:開新編號 `node-restore-sop-v2` 審一輪 v4 delta(r3 折入面+d6 使用場景節+問…
  2.449  Projects/標註刷新_實作計畫.md  [進度]
    106 [body]: - [ ] 圖譜:Verification/2026-08-18_標註刷新落地(plan_refs 雙指計劃+實作計畫)、兩計劃節點 status/進度、retrieval-ran…
  2.391  Projects/地基盤點2026-08-26_調研.md  [進度]
    68 [body]: ## 執行進度
  2.357  Projects/design-loop重設計_實作計畫.md  [進度]
    125 [body]: ## 進度
  2.270  Projects/已知坑機械前置_計劃.md  [推導]
    18 [body]: > 緣起(2026-08-08,Enzo 一連串追問推導出的設計):事故記帳只接「已爆的坑」(先踩才有);世界已知坑(如 refresh-token→single-flight)不…
  2.259  Projects/test-layers軟提醒_實作計畫.md  [進度]
    138 [body]: (pre-commit 會要圖譜同步:本 task 屬計畫執行中,末 task 統一收圖譜——先 `git commit --no-verify` 或把本實作計畫節點 status…
  2.218  Verification/2026-09-07_loop-list開著的迴圈.md  [提交]
    25 [body]: > 或看 git 有哪些沒提交的審查報告資料夾——因為問下一步、問過不過、問審到哪,
  2.192  Systems/外部對照-code衍生wiki.md  [推導]
    76 [body]: openwiki 每條優勢都來自同一個賭注：「文件應是 code 的衍生投影、可丟可重生」。**代價是它裝不下任何 code 裡沒有的東西**——沒有「這條是合約、改＝breaki…
  2.033  Systems/autonomous-iteration-loop.md  [進度]
    84 [fm]: - content: orchestrator-prompt 三修(2026-08-30):①claude -p 活性紀律——派 Agent 後必須同一回合等到結果,散文收尾=本輪…
    149 [body]: - 2026-08-30 **prompt 三修(d8,d7 首輪真跑陣亡後的續修)**:①★claude -p 活性紀律★——派 Agent 必須同一回合等到結果,散文收尾=本輪…
  1.944  Projects/關係層傳播守衛_計劃.md  [進度]
    165 [body]: ## 七、落地順序（實際進度）
  1.941  Projects/自足性審計閉環_計劃.md  [提交]
    76 [body]: 快照 commit 之後才刪,583 個被追蹤的檔全變成未提交刪除,範圍刀每次必判越界,修復鏈名存實亡)★:
    105 [body]: [[Issues/同工作區多session並行改動]] 的「提交夾帶」實例,v5-r1 s1f4★;單行訊息含三 model,本案自定測試釘)。
  1.858  Projects/精簡版update指令_計劃.md  [提交]
    63 [body]: 2. `t_slim_update_behavior`:產物以假 HOME 執行——①無 `~/.lumos-slim`→rc2+指路訊息;②fixture 造本地 git 源+c…
  1.664  Projects/Android側UI測試綁圖譜工作流_實作計畫.md  [推導]
    228 [body]: （★不要寫 `"multiplatform": true`★——那是回傳的推導結果、程式從不讀；★maestro 的 `root` 不能是 `.`★——會讓 doctor 掃整個 …
  1.622  Projects/檢索優化_計劃.md  [進度]
    337 [body]: ## 實作進度
  1.620  Projects/decision_refs自動養成_實作計畫.md  [進度]
    58 [body]: > **進度（2026-07-15）**：P ✅ + T1 ✅（[[Verification/2026-07-15_decision_refs養成_P前置_T1回寫]]）+ cod…
  1.386  Projects/收斂閘漏項敏感度v2_計劃.md  [推導]
    229 [body]: - **日報那句「宣稱 vs 實作沒有機械比對」是錯的**:`t_docs_command_count`(`scripts/test_lumos.py:17258`)與 `t_do…
  1.274  Systems/測試假綠形態.md  [提交]
    168 [body]: **發生什麼**:我把十處「條件不成立就印一條綠然後結束」改成走正式的跳過通道,順手加了一條守衛「跑完卻一條斷言都沒有就判紅」。然後我在提交訊息裡寫:**「全套 3841 綠、零命…
  1.244  Projects/Android側UI測試綁圖譜工作流_計劃.md  [推導]
    287 [★INVARIANT★]: - **r2（2026-08-11，delta 輪 2 席：sonnet 新宣稱正確性／opus 折入一致性與整合；canary 1 caught 1 missed）**：★這輪抓…
  0.000  Projects/pitfalls-lint-integration_計劃.md  []
    29 [fm:context]: context: 使用者三連問(偏科有 linter?其他平台?通則也有?)推導出——規則庫社群已維護且更新更快、更準(AST 級)、免腐化
  0.000  Systems/check-r-guard.md  []
    36 [fm]: - content: 組件 8(graph-discipline.md)+9(SKILL.md)+10(t_marker_doc_sync tuple 加 "[guard:")須同…
  0.000  Systems/design-loop.md  []
    76 [fm:why_chosen]: why_chosen: 由 N 機械推導 a→b→c→d→a 輪替,免狀態、可從 loop_status 輪歷史重現;canary 校準鐵則=「認真審抓得到但不一眼看穿」(太細不公…
  0.000  Verification/2026-07-15_主網M3_cascade帳本.md  []
    10 [fm]: - "行帶 event 判別欄;折疊只折 transition、同粒度鍵取物理序最後一筆;torn 行跳過(=未提交)"
  0.000  Verification/2026-07-22_prepush範圍修法落地.md  []
    9 [fm]: - "動 scripts/hooks/pre-push 的 stdin/範圍推導/逐 ref 迴圈"

(共 66 篇候選,照相關性排序;想照檔名排加 --legacy)

exec
/bin/zsh -lc "sed -n '1,240p' /Users/enzo/.agents/skills/lumos-project-notes/SKILL.md" in /Users/enzo/harness/lumos-toolchain
 succeeded in 0ms:
---
name: lumos-project-notes
description: 專案知識圖譜(docs/{project}-knowledge/)的進場與讀寫——任何任務開始要搞懂「這個模組/欄位/流程為什麼這樣、邊界在哪、哪些不能改、會波及什麼」時先用 lumos 查,不要直接 grep/Read;改完 code 要寫回決策/驗證/合約;收工體檢。觸發:正要 grep 或讀 code 去理解既有系統、排查、對外支援、查 DB、改名/刪除東西、開工掌握現況、收工寫回、問「圖譜有沒有記」。指令全集按情境分類在 commands/INDEX.md。
---
# lumos 專案知識圖譜——一頁手冊

圖譜記「為什麼、邊界、不能改的、驗過沒」;code 只記「現在長怎樣」。圖譜跟行為事實(測試、實際執行、生產觀測)對不上時,不自動信圖譜——查清哪邊錯,立一篇事故筆記。主工具 `lumos`(python3 零依賴,自動找 `docs/*-knowledge/`)。**別用 Grep/Read/Edit/Write 直接碰圖譜的 .md 開頭欄位**——會繞過自驗和防護;正文段落用 Edit 可以。

**指令怎麼找**:`commands/INDEX.md`(本目錄,4k)——先看「grep 衝動對照表」,再按你正在做的事開九個子檔之一。下面只列每個階段最常用的。

## 1. 進場(每個子任務都重來,不是 session 開頭一次)

| 你在想… | 敲 |
|---|---|
| 這件事為什麼這樣 / 圖譜記了嗎 | `lumos search <詞>` → `lumos context <節點>`;0 命中先換同義詞;**中文概念之間加空白**(`作廢 收回 點數`,別黏成一句) |
| 動這段有什麼不能碰 | `lumos contracts <節點>` |
| 要讀全文再下結論 | `lumos show <節點>`(search 只給索引行;拿摘要判「沒記」以前真的錯過——值在筆記第 64 行,靠摘要判成沒有) |
| 篩條件(金流 / 未收案 / 連到 X) | `lumos query --tag 家族/值 [--active] [--linked <節點>]` |
| 開工掌握現況 | `lumos query --tag status/doing`;`lumos recent --days 7` |
| 圖譜空或稀疏(接手 brownfield) | 走節點還原 SOP:`commands/09-節點還原.md`(七步;需要才產節點、有就照慣例用) |

看到筆記有 `core_refs:` 或 `CORE:` → 權威在跨專案核心圖譜,改那邊(`lumos-core-knowledge` skill)。
**查得到才算先行**(Landmark 實測):0 筆看「逐詞覆蓋」標 ★ 的詞換同義詞,換三次再問人,別轉 grep;大節點先 `--brief`;單篇內部新舊打架時摘要有日期的 KEY 行 > 正文,衝突影響決策去 code 裁再回頭修。
**分清你在哪種 session**:本機 Claude Code(含手機/網頁遙控本機)有本機 git 憑證、能 push;網頁版 claude.ai/code 是雲端沙盒,對主分支沒 push 權、只能推 feature branch——「遙控」不等於「遠端版」,曾騙到 AI 一次。
被催「直接改、不用解釋」也一樣:不解釋可以,不查不行——改 code 前至少 `lumos impact --file <檔>` 一行。

## 2. 動手前

- `lumos impact --file <檔>` / `--diff <範圍>`:哪些筆記、驗證、決策會受影響(Edit 前 hook 也會塞一份,但只推你碰到的檔)。
- `lumos pitfalls --diff <範圍>`:風險分級;`tier: high` 要過代碼審(`lumos-code-loop`)。
- 要刪 / 改名東西:`lumos search <舊名> --code` 逐句判哪些筆記還在講它。
- 改了環境 / 流程 / 設定(版本、金鑰、hook、排程):`lumos stale --candidate --match <關鍵字>` 列出寫了「改到這個就該重驗」的驗證紀錄。
- 設計、spec、計劃一律寫成 `Projects/<主題>_計劃` 筆記(`type: project`),不寫到別的路徑;動筆前一行 `PRIOR-ART:`(最小解在哪層 / 世界解過沒 / 借用‧自建‧採用)。

## 3. 寫回(同一次工作內;pre-commit 擋「改 code 沒動圖譜」)

| 要做 | 敲 |
|---|---|
| 新筆記 | `lumos new <system\|issue\|verification\|project> <名>`;驗證紀錄加 `--plan <計劃> --systems <節點>` 自動雙向連 |
| 改狀態 / 日期 | `lumos set <節點> <欄位> <值>`(日期不加引號) |
| 加 / 刪清單項 | `lumos append <節點> <欄位> "[[x]]"` / `lumos remove …` |
| 記決策 / 翻案 | `lumos decision-add <節點> "<內容>" --decided <日期>` / `lumos decision-supersede` |
| 正文段落 | Edit;寫完 `lumos lint <節點>` |

**四條血換的開頭欄位鐵則**:① 多個連結一行一項,擠成一串會長假筆記 ② `summary: |` 區塊裡的 `[[連結]]` 不算連結,要關聯另放 list 欄位 ③ 值含「冒號+空格」要引號或區塊 ④ 同層不能重複鍵。用指令寫天生避開;手改才會踩。

**合約標記(動筆前掃一眼;不確定就不標,嚴禁看 code 反推)**:
```
KEY:★INVARIANT★ <業務合約,改=破壞性> [test:測試名] [audit:模型/日期] [kill:recipes]
KEY:★DEBT★ <偶然行為,可改>
KEY:★IRREVERSIBLE★ <做了回不去> [rollback:decisions]     KEY:★CHECKPOINT★ <改了難救>(建議補 [rollback:])
```
- 綁測試 / 留審計走指令:`lumos guard bind <節點> "<KEY 片段>" <測試名>`、`lumos guard audit …`;裸合約 doctor 擋,未審計 pre-push 擋。綁之前對照 [[Systems/測試假綠形態]](最隱蔽的一型:現場根本走不到被測分支;修 bug 的翻紅測試要配一條「現場成立」的前置斷言)。
- 外部不可逆(信已寄、下游已吃)用 `[guard:decisions]` 寫怎麼防重複。`[test:]` 只證程式對,「規則還符不符合業務」要人確認:`lumos signoff`。
- 從 code 重建的筆記先 `lumos set <節點> regen from-scratch/<日期>`,每條主張標 `[src:]`/`[git:]`/`推測:`/`佚失:`;佚失就寫佚失,嚴禁編。

**摘要區塊**(Systems/Issues 必有):`FLOW:`流程 `KEY:`關鍵概念 `DEP:`依賴 `TEST:`測試;Issues 用 `FLAG:`(只收 TECHNICAL/DECISION/ORIGIN) `DECISION:` `KEY:`。已結案的 Issue 正文第一段要有結案橫幅(status 在開頭欄位,`show --body-only` 看不到,讀者會把修好的當現況)。
**標籤**:`type/` `status/`(值域 lint 硬擋)、`priority/` P0–P3、`scope/`(feature/ area/ 已停用)、`risk/` 金流‧對外送出‧不可逆‧守衛面、`flag/`。

**決策與驗證**:重大決策填四欄(context / alternatives≥2 / why_chosen / trade_offs),缺資訊問人不編。驗證紀錄填 `valid_under`(前提)與 `revalidate_when`(何時重驗),用 `plan_refs` 指回計劃;漏掛 `lumos sync-verified-by --apply`。計劃結案前 `lumos spec-trace <計劃>` 看哪些條款沒人認領。

**承認風險的鐵則**(Enzo 2026-08-22 裁):筆記或訊息裡寫「沒機械守衛 / 只提醒不擋 / 單次量測 / 這數字是拍的」這類承認句,**旁邊必須有「什麼時候回頭看」**(週報、重驗條件、revalidate_when、到期日);寫不出重驗條件的,就是該處理不該承認。**回頭條件要接電**(2026-08-31 回訪案):帶日期的寫成獨立一行 `REVISIT:YYYY-MM-DD 一句要做什麼`(緊鄰原句,doctor 到期會唸、逾 14 天沒人動升級週報);綁事件的明寫事件入口——純散文=52 件盤點實證的死文。

## 4. 收工

1. `lumos lint <每篇動過的>` → `lumos doctor`(紅的段先修;`--verbose` 看全部提醒)。
2. code 有「拿掉 / 反轉」的改動:把那些名字逐個 `lumos search <名> --code`,逐句判筆記還成不成立,不成立當場改或標作廢。動到畫面 → 補可重放的 UI flow 並 `[test:<平台>:<flow>]` 綁回(沒裝置要明寫「未驗+原因」)。
3. 圖譜實質更新後:派乾淨 agent 只讀圖譜還原脈絡,對不上就補到一致,留痕 `lumos self-audit <節點>`。
4. push 後(專案有宣告 ci 區塊才有):`lumos ci-wait`,紅就當輪修,修不完要在收尾明講。
5. 跨 session 傳訊只傳「指標+觸發」(我動了哪篇、你去讀哪篇),不傳內容本身;規則權威在圖譜不在誰的記憶。

## 再深一層(按需開,別一次全讀)

| 要做 | 開 |
|---|---|
| 某個指令的旗標與用法 | `commands/0N-*.md`(INDEX 指到)或 `lumos <cmd> --help` |
| 合約鏈深規、[audit:] 五問、guard 工作流、防帶風向 | `reference.md`〈★INVARIANT★ → `[audit:]` 獨立合法性審計〉〈★INVARIANT★ → `[test:]` 綁定〉〈`lumos guard`〉 |
| 決策四欄完整版、驗證紀錄完整規格、同步規則 | `reference.md`〈Properties〉〈同步規則〉 |
| 開頭欄位鐵則、標籤家族、摘要區塊、結案橫幅、退場自問、跨 session 傳訊、CI 細則全文 | `reference.md`〈寫入規範與紀律全文〉 |
| 自足性審計 prompt、交叉審計變體 | `reference.md`〈圖譜更新後：Sonnet agent 自足性審計〉〈變體 B：圖譜×程式碼交叉審計〉 |
| maestro UI flow 派工要求 | `reference.md`〈產 maestro UI flow 的派工要求〉 |
| 資料夾位置 | `docs/{slug}-knowledge/{Projects,Systems,Issues,Verification,MOC}`;某主題 >5 篇建 MOC |

exec
/bin/zsh -lc 'python3 scripts/lumos context Projects/進度從提交推導_計劃.md --brief && python3 scripts/lumos show Projects/進度從提交推導_計劃.md' in /Users/enzo/harness/lumos-toolchain
 succeeded in 542ms:
# Projects/進度從提交推導_計劃.md
type:project | status:doing | created:2026-09-07 | updated:2026-09-07
summary:
  FLAG:TECHNICAL
  KEY:立案(2026-09-07,Enzo 裁「首要工作=讓做到哪一步也能同步並且可信」後再切一刀)——★本案不是做進度追蹤器,是讓「完成」那個動作自己留下紀錄★
→ 連出 (5):
  • Issues/同工作區多session並行改動.md [open]
  • Projects/全repo審視_計劃.md [doing]
  • Projects/執行DAG_調研.md [doing]
  • Projects/驗形式與驗內容_調研.md [doing]
  • Systems/loop-convergence-recording.md [done]
← 連入 (0):
---
type: project
status: doing
created: 2026-09-07
updated: 2026-09-07
tags:
  - type/project
  - status/doing
related:
  - "[[Projects/執行DAG_調研]]"
  - "[[Projects/驗形式與驗內容_調研]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Issues/同工作區多session並行改動]]"
  - "[[Projects/全repo審視_計劃]]"
summary: |-
  FLAG:TECHNICAL
  KEY:立案(2026-09-07,Enzo 裁「首要工作=讓做到哪一步也能同步並且可信」後再切一刀)——★本案不是做進度追蹤器,是讓「完成」那個動作自己留下紀錄★
  KEY:★根因:完成與記錄是兩件事★——審查迴圈準,是因為「完成一輪」與「記下一輪」是**同一個動作**(那筆帳就是工作成果,不可能做了沒記/記了沒做);實作歪,是因為成果是程式碼、記錄是另外去勾框,兩件事分開就一定漂
  KEY:★症狀數字(2026-09-07 當場量)★:Projects 標進行中 43 篇其中 17 篇 >30 天沒動;一篇 status=done 的實作計畫 60 個框 0 個勾(12 任務×5 步驟,全是實作步驟)、另一篇 39 個框全勾——★並列才是重點:同 repo 同格式,有人維護有人不維護,而沒有任何東西會知道差別★;50 群主清單無「做完沒」欄、進度靠翻提交訊息回推;近 120 筆提交帶編號的只有 6 筆(且全集中在那份有編號的清單上)
  KEY:★因果鏈沒有分叉,斷點在最前面★——工作項沒有在筆記之外還活著的識別碼 → 提交掛不上 → 沒有可追加的紀錄 → 完成狀態只能手寫 → 一定漂
  KEY:★PRIOR-ART 最強的一條:不用發明格式★——git 原生有 trailer,`git log --format='%(trailers:key=X,valueonly=true)'` 一個旗標查得出;**本 repo 每筆提交已經在產 trailer**(近 30 筆 100% 帶 Co-Authored-By/Claude-Session),所以是加一個鍵不是加一套機制。讀取端★用 git 原生解析、不自己寫正則撈提交訊息★(自己撈=又一個「形式對內容不一定對」的地方)
  KEY:設計三步(各可獨立交付)=[S1] 工作項取名(只定慣例不寫程式)/[S2] 完成的提交掛 `Task: <識別碼>` trailer/[S3] 唯讀查詢從 git 算進度,★不寫回筆記★(寫回去就又變成會漂的手寫狀態),樣板照 `loop verify-progress`「只讀結構不讀散文」
  KEY:★範圍刀★不建第二張圖/不建任務狀態檔(執行DAG_調研已裁:手維護狀態檔正是本案要消滅的)/不做認領租約多agent派工/不碰審查迴圈那條線(已會動,動它只有下跌空間)/不做跨任務依賴(依賴建立在「完成」之上,本案是它的前置)/不自動改筆記 status 欄
  KEY:★誠實天花板:最多蓋到四分之三★——74 個任務段裡 56 個(75%)抽得出對應測試名,剩 18 個天生沒有(改 skill 散文/圖譜回填/真機驗收);那類沒有提交可掛或掛了也證明不了,★本案對它們無效、不假裝有效,輸出要明說「這類算不出來」★
  KEY:★待裁四題★①識別碼從哪來(沿用 50 群的 #N / 每份計劃 T1..Tn 會撞名 / 計劃名+任務號)②trailer 鍵名(避開既有與世界慣例語意衝突)③「完成」定義=有提交掛過就算,還是要加「綁的測試綠」——★後者看似更嚴但外家 f2 已證明「測試綠≠任務完成」(多任務共用一個測試/只寫跑全套/既有測試開工前就綠),加了不一定更準可能只是更貴★ ④先唯讀查詢還是一開始就讓 pre-commit 提醒
  KEY:驗收線=不讀勾選框就答得出每個工作項有沒有被提交掛過與最後一次何時;對那 18 個算不出來的**明說算不出來**;三步各有測試且 ★fixture 用真的呼叫 git 產生不手刻★(2026-09-07 教訓:手刻 fixture 導致 code-loop 那半是死碼)
decisions:
  - content: 用 git trailer 承載工作項識別碼,不自建格式、不建任務狀態檔
    id: d1
    context: 要讓「完成」自己留下紀錄,需要一個機器可讀的欄位把提交跟工作項綁起來。選項:自訂提交訊息格式再寫正則撈、開一份任務狀態檔、或用 git 原生 trailer
    why_chosen: git trailer 是原生標準,`git log --format='%(trailers:key=X,valueonly=true)'` 一個旗標就查得出,不必自寫解析(自寫正則撈提交訊息=又一個「形式對、內容不一定對」的地方);而且本 repo 每筆提交已經在產 trailer(近 30 筆 100% 帶 Co-Authored-By/Claude-Session),是加一個鍵不是加一套機制。任務狀態檔已於 執行DAG_調研 裁掉:手維護的狀態正是本案要消滅的東西。代價:綁死 git(非 git 專案不適用);trailer 要靠寫提交的人記得加,沒有機械守衛前一樣會漏
    decided: 2026-09-07
    valid: false
    superseded_by: d7
    ended: 2026-09-07
  - content: 本案明說只蓋四分之三:沒有程式碼可掛的工作(skill 散文/圖譜回填/真機驗收)不假裝算得出來
    id: d2
    context: 先前量到 74 個任務段裡 56 個(75%)抽得出對應測試名,剩 18 個天生沒有——那類沒有提交可掛,或掛了也證明不了什麼
    why_chosen: 家規要求承認風險要附回頭條件、寫不出判準就明說靠人;而把算不出來的東西輸出成「未完成」或靜默略過,都會讓使用者以為算過了——那正是本 repo 反覆抓到的假綠形態。代價:這個工具永遠有一塊盲區,不能宣稱『進度全自動』
    decided: 2026-09-07
    valid: true
  - content: 完成判準掛實作端、看測試:功能級測試套綠 + 相依功能無回歸;明確不做散文級判準
    id: d3
    context: Enzo 裁。原本待裁三選項:有提交掛過就算完成 / 加上綁的測試綠 / 散文級判斷。外家 f2 曾證明「測試綠≠任務完成」(多任務共用一個測試、有的只寫跑全套、既有測試開工前就綠)
    why_chosen: ★f2 打的是任務級,Enzo 裁的是功能級,三條反對在功能級各自失效★:共用測試在功能級就是同一個功能的測試、既有測試已綠對新功能不成立、只寫跑全套在功能級正是「相依無回歸」那一半的定義。所以不是繞過外家,是換到 f2 打不到的粒度。代價:①功能級是二元的,答不出「做到第幾步」,接手需要的解析度要靠任務級測試名另外給(且不得用來宣告完成)②判準的品質等於測試的品質,弱測試=假綠,靠既有翻紅釘紀律頂著③沒有測試可掛的工作型別完全不在射程內
    decided: 2026-09-07
    valid: true
  - content: 識別碼沿用既有 [SN] 條款標記,定址比照決策寫成 <計劃節點rel>#S1
    id: d4
    context: 三選項:沿用 50 群那套 #N(只存在於那一份清單)、每份計劃自己給 T1..Tn(跨計劃撞名)、計劃節點名+任務號
    why_chosen: 不發明新方案:①[SN] 標記是既有慣例且已有消費者(spec-trace 用它看哪些條款沒被驗證認領)②定址形狀已有前例(決策是 <節點rel>#dN,程式裡有格式驗證與 dangling 偵測,可照抄)③識別碼從計劃節點自己長出來,不必維護第二份登記簿。代價:計劃節點改名會讓舊 trailer 指不到——但決策定址有同一個問題,不是本案新引入的風險
    decided: 2026-09-07
    valid: false
    superseded_by: d7
    ended: 2026-09-07
  - content: trailer 鍵名用 Lumos-Task:
    id: d5
    context: "候選 Task: / Refs: / Lumos-Task:;本 repo 現有 trailer 是 Co-Authored-By 與 Claude-Session"
    why_chosen: "比照既有的 Claude-Session: 命名空間形態;Refs:/Fixes:/Closes: 在 git 生態各有既定語意、借用製造歧義;Task: 太泛將來可能撞別的工具。代價:字長,但由提交模板產生、人不必自己打(Co-Authored-By 就是這樣運作)"
    decided: 2026-09-07
    valid: false
    superseded_by: d7
    ended: 2026-09-07
  - content: 「綠」的來源用 CI 那筆,不用 code-loop pass
    id: d6
    context: 兩個候選都按版本記:governance/code-loop/main.json 的 {head_sha,status} 與 lumos ci-status 的 {sha,conclusion}
    why_chosen: ★code-loop pass 記的是「審查過了」不是「測試綠了」,狀態值裡還有 skipped——拿它當測試結果就是借一個紀錄表達它沒有的意思,正是本 repo 今天抓了一整天的病★;CI 那筆語意就是對的(實查 JSON 帶 sha 與 conclusion,本地讀不打網路)。代價不小:CI 只在推送後跑,本機未推的工作查不到,所以必須把「還沒推=未知」與「未完成」分開輸出——混在一起就是新的假綠
    decided: 2026-09-07
    valid: false
    superseded_by: d7
    ended: 2026-09-07
  - content: v2 核心:不推論「完成」,只報告「這個任務宣告的證據現在是什麼狀態」——對計劃宣告的測試名當場在工作樹上跑,回報「不存在/存在但紅/存在且綠」
    id: d7
    context: r1 五席四席判 blocker。六個 blocker 群的共同形狀:每一條都來自「拿一個代理物(trailer / CI 紀錄)去推論完成」,而每個代理物都有縫,每條縫都生出一個**假完成**——正是本案要消滅的病
    why_chosen: ★不推論就沒有縫★:識別碼問題消失(任務的名字就是它宣告的測試名,那是程式碼裡真實存在的符號,天生唯一可定址,改名會被既有 doctor Check Y 抓到);trailer 四種靜默失敗全部消失(不用 trailer);CI 對應問題消失(當場跑,只跑宣告的那幾個不是全套);★未提交態解決——讀工作樹不讀提交歷史,session 做到一半還沒 commit 照樣看得見,而 r1 指出那正是最急迫最常見的一格★;提交夾帶不影響(不依賴提交歸屬);f2 的反對被正面處理不是躲開(不宣稱測試綠=完成,推論交給讀的人)。★與 trailer 的關鍵差別:trailer 寫錯的輸出跟沒寫一樣(靜默),測試名寫錯的輸出是「不存在」(看得見)★。代價:只覆蓋有宣告測試名的約 75%;跑測試要時間(只跑子集,要量);答不出「相依功能有沒有回歸」那一半
    decided: 2026-09-07
    valid: true
---
# 進度從提交推導_計劃

> 白話:現在「這件事做到哪一步」是人手寫在筆記裡的,所以會漂——有一篇計劃狀態寫「做完了」,
> 裡面 60 個勾選框一個都沒勾。本案要把它換成**算出來的**:每個工作項給一個名字,
> 完成它的那個提交把名字掛上去,進度就從 git 算,沒有東西需要人維護。

> **本篇用到的三個詞**:「外家」=不是編排者那一家的審查席(本 repo 慣例上是 Codex);「f2」=某輪外家報告的第 2 條發現(此處指 [[Projects/執行DAG_調研]] 那輪);「編排者」=負責派審查員、判讀報告、折入修正的那個角色(本案是主對話的 AI);「群」=[[Projects/全repo審視_計劃]] 把 130 條發現去重合併後、可獨立交付的分組。

PRIOR-ART(★v2 重寫;原稿整段在替已死的 trailer 背書,前掃 ③ 抓到是重寫殘留★):①**最小解在既有機制層**——v2 不新增任何資料格式:任務的名字就是它**已經宣告在計劃裡的測試函式名**,跑法用既有的測試子集入口(`-k <關鍵字>`,前掃實跑驗過可用)。②本家可抄的樣板=`loop verify-progress` 的 help 逐字:「不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)。」③世界解:GitHub `Closes #N` 綁 forge;beads / Task Master 已於 [[Projects/執行DAG_調研]] d1 裁「可借形狀、不借實作」。④不採用新依賴:只用 python3 stdlib 與既有測試入口。★⑤ v1 的 git trailer 路線已在 r1 被打死(四種靜默失敗),d1/d2/d5/d6 四條決策全部翻案;本節不再替它背書。★

## 問題(有症狀、有數字、有消費者)

**症狀**:任何一個 session 都答不出「這件實作做到哪一步了」。

**當場量到的數字(2026-09-07)**:

| 量到什麼 | 數字 |
|---|---|
| Projects 標「進行中」 vs 超過 30 天沒動 | **46 篇 / 其中 17 篇**(★快照 2026-09-07 傍晚;原稿寫 43 是當天稍早的量測,差的 3 篇是同日新增、含本篇自己★。「17 篇」前掃機械重算吻合) |
| 一篇 `status: done` 的實作計畫,裡面的勾選框 | **60 個框,0 個打勾**(12 任務 × 5 步驟,全是實作步驟不是驗收清單) |
| 另一篇實作計畫的勾選框 | **39 個框,全部打勾** |
| [[Projects/全repo審視_計劃]] 的 50 群主清單 | **沒有「做完沒」這一欄**;進度靠翻提交訊息回推 |
| 近 120 筆提交帶項目編號的 | **6 筆**(而且全部集中在那份有編號的主清單上) |

★第二、三列並列才是重點★:同一個 repo、同一種格式,**有人維護有人不維護,而沒有任何東西會知道差別**。

**消費者**:①接手的 session(現在只能讀散文猜)②Enzo 本人(問「做到哪」要人回答)③無人自跑的迴圈(未來)。

## 根因:完成與記錄是兩件事

- **審查迴圈為什麼準**:★「完成一輪」和「記下一輪」是**同一個動作**★——那筆帳本身就是工作成果。不可能做了沒記,也不可能記了沒做。
- **實作為什麼歪**:工作成果是程式碼,記錄是另外去勾一個框。**兩件事分開就一定會漂**;那 60 個沒勾的框就是這樣來的。

**所以本案不是「做一個進度追蹤器」,是「讓完成那個動作自己留下紀錄」。**

## ★v1 死在哪、v2 怎麼改(2026-09-07,設計審 r1 五席四席判 blocker,Enzo 裁整份重寫)★

**六個 blocker 群的共同形狀,收斂成一句**:每一條都來自**拿一個代理物去推論「完成」**,而每個代理物都有縫,★每條縫都生出一個假完成★——正是本案存在的理由要消滅的病。

| r1 打死的 | 死因 | v2 怎麼處理 |
|---|---|---|
| 識別碼用 `[SN]` | 粒度錯(是設計階段標記不是任務單位;本篇自己的 [S1][S2][S3] 就是三段設計步驟)+ 對本文舉的兩篇症狀零覆蓋(它們用 `### Task N`) | ★不需要識別碼★——任務的名字就是它宣告的測試名 |
| 完成 = 提交掛 trailer | 四種靜默失敗:錯字無攔截、訊息結尾非鍵值形狀整段消失(連既有兩個一起)、squash 吃掉、revert 不帶 | ★不用 trailer★ |
| 綠 = CI 那筆 | CI 綁 push 的 tip sha(中間提交結構性查不到)、`ci-status` 只回最後一筆、同 sha 重跑轉綠被舊的紅蓋過、凍結當時綠→永久假完成 | ★不讀 CI,當場跑宣告的那幾個測試★ |
| 根因「完成與記錄是同一動作」 | 多 session 提交夾帶時 trailer 只掛夾帶者的;★未提交態完全不可見,而那是「做到一半」最急迫最常見的一格★ | ★讀工作樹,不讀提交歷史★ |
| 「換粒度躲開 f2」的論證 | 反駁②自己寫明只在新功能成立,但判準涵蓋增修既有功能;且連結了會反駁自己的姊妹研究卻從未回應 | ★不躲——不宣稱「測試綠=完成」★ |
| 任務級解析度 | 沒有可執行的資料源(CI 的 JSON 是 workflow 級無逐測試欄位) | 資料源就是測試名本身 |

**r1 沒有攻擊、因此保留的**:上面的診斷與數字(全部被獨立重算吻合)、根因分析、範圍刀、零依賴家規、以及「否掉 code-loop pass」這個判斷本身。~~效能也被兩席各自量過:全量掃描 47 毫秒~~ → ★**前掃指出這句被誤用**★:那 47 毫秒量的是 **v1 已死的 trailer 全量掃描**,不是 v2 的「當場跑測試」。**放在這裡會被讀成「v2 效能已驗過」,實際沒有。真實數字見下面誠實天花板。**

## v2 核心:不推論「完成」,只報告「證據現在是什麼狀態」

★這是整個 v2 的那一刀★:**停止推論,直接報事實。**

- 計劃裡每個任務**已經宣告了它的測試名**(先前量過:74 個任務段裡 56 個有,約 75%)。
- 查詢就做一件事:**對這份計劃宣告的每個測試名,現在在工作樹上跑一次,回報三種狀態之一——「不存在 / 存在但紅 / 存在且綠」。**
- ★不說「完成」,說「它宣告的證據現在是什麼狀態」。推論交給讀的人。★

**為什麼這樣就沒有縫**:縫是「代理物與事實之間的落差」;不做推論,就沒有那段落差可以漏。

**與 v1 最關鍵的一個差別(直接回應 r1 的靜默失敗批評)**:
- trailer **寫錯的輸出跟沒寫一樣**(都是查無資料)——★靜默★。
- 測試名**寫錯的輸出是「不存在」**——★看得見★。**這一條仍然成立,但它的機械支撐要換人。**
- ★**前掃推翻原稿的舉證**★:原稿說「既有 doctor Check Y 本來就會抓這種漂移」——**不成立**。Check Y **只掃 `type: system` 節點**,而 14 份實作計畫全是 `type: project`;程式碼註解還明講為什麼刻意排除:「Projects 提的是『打算做的方法』(還沒寫),對那些節點報 repo 查無是**誤報而非發現**」。
- ★而且那個理由是對的,所以**不能**把 Check Y 擴到 Projects★——那會製造誤報。**正確的說法是:「不存在」在本案的查詢裡是三態之一、是合法資訊,不是錯誤;它的可見性由本案自己的輸出保證,不靠既有健檢。**

## 設計

### [S1] 抽取:從計劃節點讀出「任務 → 宣告的測試名」

- ★**前掃推翻原稿:沒有「既有測試名抽取」可以重用**★——`SPEC_CLAUSE_RE` 抽的是 `[SN]` 設計條款,`cmd_spec_trace` 做的是條款級追溯,**跟測試函式名毫無關係**。原稿寫「重用既有抽取」是空的前提,撤回。
- 所以 [S1] **是新寫一份抽取**。既然是新寫,就要正面回應 r1 架構席那條:`(.+?)#(d\d+)` 此刻有三份互不共用(前掃精確重數確認,其中兩份各自 inline、沒呼叫現成的 `_dref_parse`)。★本案的抽取一開始就要寫成單一函式並被測試釘住,不得重演那個形態。★
- **一個測試服務多個任務要偵測並報告**(f2 的原始案例:某計劃 Task 1–5 全部往同一個測試函式裡續加斷言)。★偵測到就明說「這幾個任務宣告同一個測試,分不出誰做完」★,不假裝分得出。

### [S2] 查詢:當場跑,只跑宣告的那幾個

- 跑法用既有的測試子集入口(`-k <關鍵字>`),不跑全套。
- 三態輸出:不存在 / 存在但紅 / 存在且綠。**沒有第四種「完成」。**
- 唯讀、不寫回筆記、不改任何狀態欄。

### [S3] 慣例:讓「宣告測試名」這件事被看見

- 現況 75% 的任務段已經在寫,**這是既有慣例不是新規定**。
- 缺的那些,查詢輸出裡明列「這幾個任務沒有宣告測試,算不出來」——★不靜默略過,也不顯示成未完成★。

## 範圍刀(明確不做)

- **不建第二張圖、不建任務狀態檔、不做認領租約、不碰審查迴圈那條線、不自動改 status 欄**(v1 的五條全部保留)。
- **不做跨任務依賴**——依賴建立在「完成」之上,而本案刻意不判完成。
- ★**不答「可以出貨了沒」**★:Enzo 裁的判準有兩半,本案只碰得到「這個功能的測試綠不綠」,**答不出「相依功能有沒有回歸」**(那要全套,查不起)。那一半仍歸推送前的閘與 CI,**不在本案射程**。
- **不用 git trailer、不讀 CI**——v1 的兩條主機制在 r1 被打死,v2 不留殘骸。

## ★誠實天花板★

- **只覆蓋約 75%**:沒有宣告測試的任務(改 skill 散文、圖譜回填、真機驗收)算不出來,**輸出明說算不出來**。★r1 之後仍成立,而且那 18 個還沒逐一分類。★
- **「宣告測試名」這一步仍是自律**:人要在計劃裡寫。但★寫錯是看得見的(報「不存在」),不是靜默的★——這是它跟 v1 的 trailer 的本質差別。
- **跑測試要時間——★前掃已補量,結論是「看關鍵字精不精確」★**:單一任務粒度很快(`-k impact_cli_skeleton` 2 條 0.8 秒、`-k spec_trace` 12 條 1.88 秒,大半是啟動開銷);**但關鍵字不夠精確會命中一整族**——`-k impact` 命中 305 條、**23.4 秒**。
- ★所以這是一條新的真實邊界:宣告的測試名要夠精確,否則查詢會從 1 秒變成 20 秒以上★。原稿完全沒提到這件事,要進設計(例如:抽到的關鍵字命中數超過門檻就拒跑並報「這個宣告太寬」)。
- **一個測試服務多個任務時分不出誰做完**:偵測得到、但解不掉,只能報告。

## 待裁(留給 v2 的設計審)

- 測試名抽取要用什麼樣式?前掃實數:`` `t_xxx` `` 235 次、全大寫 `TEST:` 40 次(是摘要欄位不是任務級)、中文「測試:」40 次、`-k xxx` 25 次、`**Test**:` 7 次。★最棘手的是中文「測試:」那種——純散文、連反引號或關鍵字都沒有,**根本抽不出可執行識別碼**★(例:某實作計畫寫「測試:對 fixture 跑 delta --json:已判不重出……跑紅」)。要不要先釘一個樣式,還是接受抽不到就報「沒有宣告」。
- ★「任務段」這個分母本身沒有唯一機械定義★:同一批筆記上量過 73 / 74 / 83 三個數(切法不同)。設計要明講用哪一種切法,否則覆蓋率這個數字永遠對不齊。
- 跑不動的環境(沒裝依賴、要真機)怎麼報?算「不存在」還是第四態?
- 那 18 個沒有測試的任務段,要不要在本案處理,還是明講不處理。

## 驗收線

- 對一份真實的實作計畫,**不讀它的勾選框、不讀任何提交**,答出每個任務宣告的測試現在是三態的哪一態。
- **在一棵有未提交改動的工作樹上照樣答得出來**(★這是 v1 死掉的那一格,v2 必須當場證明★)。
- 沒有宣告測試的任務段,輸出**明說算不出來**。
- 一個測試被多個任務宣告時,輸出**明說分不出誰做完**。
- 測試 fixture ★用真的呼叫產生,不手刻★(2026-09-07 教訓)。

exec
/bin/zsh -lc "rg --files governance/review-reports/進度從提交推導 governance/review-reports/進度從提交推導-v2 && nl -ba governance/review-reports/進度從提交推導-v2/r1-snapshot.md | sed -n '1,240p'" in /Users/enzo/harness/lumos-toolchain
 succeeded in 0ms:
governance/review-reports/進度從提交推導-v2/r1-codex-prompt.txt
governance/review-reports/進度從提交推導-v2/r1-外家codex.md
governance/review-reports/進度從提交推導-v2/r1-intake.md
governance/review-reports/進度從提交推導-v2/r1-snapshot.md
governance/review-reports/進度從提交推導/r1-codex-prompt.txt
governance/review-reports/進度從提交推導/r1-邊界.md
governance/review-reports/進度從提交推導/r1-snapshot.md
governance/review-reports/進度從提交推導/r1-intake.md
governance/review-reports/進度從提交推導/r1-dispatch.json
governance/review-reports/進度從提交推導/r1-外家codex.md
governance/review-reports/進度從提交推導/r1-接手.md
governance/review-reports/進度從提交推導/r1-正確性.md
governance/review-reports/進度從提交推導/r1-架構對齊.md
     1	---
     2	type: project
     3	status: doing
     4	created: 2026-09-07
     5	updated: 2026-09-07
     6	tags:
     7	  - type/project
     8	  - status/doing
     9	related:
    10	  - "[[Projects/執行DAG_調研]]"
    11	  - "[[Projects/驗形式與驗內容_調研]]"
    12	  - "[[Systems/loop-convergence-recording]]"
    13	  - "[[Issues/同工作區多session並行改動]]"
    14	  - "[[Projects/全repo審視_計劃]]"
    15	summary: |-
    16	  FLAG:TECHNICAL
    17	  KEY:立案(2026-09-07,Enzo 裁「首要工作=讓做到哪一步也能同步並且可信」後再切一刀)——★本案不是做進度追蹤器,是讓「完成」那個動作自己留下紀錄★
    18	  KEY:★根因:完成與記錄是兩件事★——審查迴圈準,是因為「完成一輪」與「記下一輪」是**同一個動作**(那筆帳就是工作成果,不可能做了沒記/記了沒做);實作歪,是因為成果是程式碼、記錄是另外去勾框,兩件事分開就一定漂
    19	  KEY:★症狀數字(2026-09-07 當場量)★:Projects 標進行中 43 篇其中 17 篇 >30 天沒動;一篇 status=done 的實作計畫 60 個框 0 個勾(12 任務×5 步驟,全是實作步驟)、另一篇 39 個框全勾——★並列才是重點:同 repo 同格式,有人維護有人不維護,而沒有任何東西會知道差別★;50 群主清單無「做完沒」欄、進度靠翻提交訊息回推;近 120 筆提交帶編號的只有 6 筆(且全集中在那份有編號的清單上)
    20	  KEY:★因果鏈沒有分叉,斷點在最前面★——工作項沒有在筆記之外還活著的識別碼 → 提交掛不上 → 沒有可追加的紀錄 → 完成狀態只能手寫 → 一定漂
    21	  KEY:★PRIOR-ART 最強的一條:不用發明格式★——git 原生有 trailer,`git log --format='%(trailers:key=X,valueonly=true)'` 一個旗標查得出;**本 repo 每筆提交已經在產 trailer**(近 30 筆 100% 帶 Co-Authored-By/Claude-Session),所以是加一個鍵不是加一套機制。讀取端★用 git 原生解析、不自己寫正則撈提交訊息★(自己撈=又一個「形式對內容不一定對」的地方)
    22	  KEY:設計三步(各可獨立交付)=[S1] 工作項取名(只定慣例不寫程式)/[S2] 完成的提交掛 `Task: <識別碼>` trailer/[S3] 唯讀查詢從 git 算進度,★不寫回筆記★(寫回去就又變成會漂的手寫狀態),樣板照 `loop verify-progress`「只讀結構不讀散文」
    23	  KEY:★範圍刀★不建第二張圖/不建任務狀態檔(執行DAG_調研已裁:手維護狀態檔正是本案要消滅的)/不做認領租約多agent派工/不碰審查迴圈那條線(已會動,動它只有下跌空間)/不做跨任務依賴(依賴建立在「完成」之上,本案是它的前置)/不自動改筆記 status 欄
    24	  KEY:★誠實天花板:最多蓋到四分之三★——74 個任務段裡 56 個(75%)抽得出對應測試名,剩 18 個天生沒有(改 skill 散文/圖譜回填/真機驗收);那類沒有提交可掛或掛了也證明不了,★本案對它們無效、不假裝有效,輸出要明說「這類算不出來」★
    25	  KEY:★待裁四題★①識別碼從哪來(沿用 50 群的 #N / 每份計劃 T1..Tn 會撞名 / 計劃名+任務號)②trailer 鍵名(避開既有與世界慣例語意衝突)③「完成」定義=有提交掛過就算,還是要加「綁的測試綠」——★後者看似更嚴但外家 f2 已證明「測試綠≠任務完成」(多任務共用一個測試/只寫跑全套/既有測試開工前就綠),加了不一定更準可能只是更貴★ ④先唯讀查詢還是一開始就讓 pre-commit 提醒
    26	  KEY:驗收線=不讀勾選框就答得出每個工作項有沒有被提交掛過與最後一次何時;對那 18 個算不出來的**明說算不出來**;三步各有測試且 ★fixture 用真的呼叫 git 產生不手刻★(2026-09-07 教訓:手刻 fixture 導致 code-loop 那半是死碼)
    27	decisions:
    28	  - content: 用 git trailer 承載工作項識別碼,不自建格式、不建任務狀態檔
    29	    id: d1
    30	    context: 要讓「完成」自己留下紀錄,需要一個機器可讀的欄位把提交跟工作項綁起來。選項:自訂提交訊息格式再寫正則撈、開一份任務狀態檔、或用 git 原生 trailer
    31	    why_chosen: git trailer 是原生標準,`git log --format='%(trailers:key=X,valueonly=true)'` 一個旗標就查得出,不必自寫解析(自寫正則撈提交訊息=又一個「形式對、內容不一定對」的地方);而且本 repo 每筆提交已經在產 trailer(近 30 筆 100% 帶 Co-Authored-By/Claude-Session),是加一個鍵不是加一套機制。任務狀態檔已於 執行DAG_調研 裁掉:手維護的狀態正是本案要消滅的東西。代價:綁死 git(非 git 專案不適用);trailer 要靠寫提交的人記得加,沒有機械守衛前一樣會漏
    32	    decided: 2026-09-07
    33	    valid: false
    34	    superseded_by: d7
    35	    ended: 2026-09-07
    36	  - content: 本案明說只蓋四分之三:沒有程式碼可掛的工作(skill 散文/圖譜回填/真機驗收)不假裝算得出來
    37	    id: d2
    38	    context: 先前量到 74 個任務段裡 56 個(75%)抽得出對應測試名,剩 18 個天生沒有——那類沒有提交可掛,或掛了也證明不了什麼
    39	    why_chosen: 家規要求承認風險要附回頭條件、寫不出判準就明說靠人;而把算不出來的東西輸出成「未完成」或靜默略過,都會讓使用者以為算過了——那正是本 repo 反覆抓到的假綠形態。代價:這個工具永遠有一塊盲區,不能宣稱『進度全自動』
    40	    decided: 2026-09-07
    41	    valid: true
    42	  - content: 完成判準掛實作端、看測試:功能級測試套綠 + 相依功能無回歸;明確不做散文級判準
    43	    id: d3
    44	    context: Enzo 裁。原本待裁三選項:有提交掛過就算完成 / 加上綁的測試綠 / 散文級判斷。外家 f2 曾證明「測試綠≠任務完成」(多任務共用一個測試、有的只寫跑全套、既有測試開工前就綠)
    45	    why_chosen: ★f2 打的是任務級,Enzo 裁的是功能級,三條反對在功能級各自失效★:共用測試在功能級就是同一個功能的測試、既有測試已綠對新功能不成立、只寫跑全套在功能級正是「相依無回歸」那一半的定義。所以不是繞過外家,是換到 f2 打不到的粒度。代價:①功能級是二元的,答不出「做到第幾步」,接手需要的解析度要靠任務級測試名另外給(且不得用來宣告完成)②判準的品質等於測試的品質,弱測試=假綠,靠既有翻紅釘紀律頂著③沒有測試可掛的工作型別完全不在射程內
    46	    decided: 2026-09-07
    47	    valid: true
    48	  - content: 識別碼沿用既有 [SN] 條款標記,定址比照決策寫成 <計劃節點rel>#S1
    49	    id: d4
    50	    context: 三選項:沿用 50 群那套 #N(只存在於那一份清單)、每份計劃自己給 T1..Tn(跨計劃撞名)、計劃節點名+任務號
    51	    why_chosen: 不發明新方案:①[SN] 標記是既有慣例且已有消費者(spec-trace 用它看哪些條款沒被驗證認領)②定址形狀已有前例(決策是 <節點rel>#dN,程式裡有格式驗證與 dangling 偵測,可照抄)③識別碼從計劃節點自己長出來,不必維護第二份登記簿。代價:計劃節點改名會讓舊 trailer 指不到——但決策定址有同一個問題,不是本案新引入的風險
    52	    decided: 2026-09-07
    53	    valid: false
    54	    superseded_by: d7
    55	    ended: 2026-09-07
    56	  - content: trailer 鍵名用 Lumos-Task:
    57	    id: d5
    58	    context: "候選 Task: / Refs: / Lumos-Task:;本 repo 現有 trailer 是 Co-Authored-By 與 Claude-Session"
    59	    why_chosen: "比照既有的 Claude-Session: 命名空間形態;Refs:/Fixes:/Closes: 在 git 生態各有既定語意、借用製造歧義;Task: 太泛將來可能撞別的工具。代價:字長,但由提交模板產生、人不必自己打(Co-Authored-By 就是這樣運作)"
    60	    decided: 2026-09-07
    61	    valid: false
    62	    superseded_by: d7
    63	    ended: 2026-09-07
    64	  - content: 「綠」的來源用 CI 那筆,不用 code-loop pass
    65	    id: d6
    66	    context: 兩個候選都按版本記:governance/code-loop/main.json 的 {head_sha,status} 與 lumos ci-status 的 {sha,conclusion}
    67	    why_chosen: ★code-loop pass 記的是「審查過了」不是「測試綠了」,狀態值裡還有 skipped——拿它當測試結果就是借一個紀錄表達它沒有的意思,正是本 repo 今天抓了一整天的病★;CI 那筆語意就是對的(實查 JSON 帶 sha 與 conclusion,本地讀不打網路)。代價不小:CI 只在推送後跑,本機未推的工作查不到,所以必須把「還沒推=未知」與「未完成」分開輸出——混在一起就是新的假綠
    68	    decided: 2026-09-07
    69	    valid: false
    70	    superseded_by: d7
    71	    ended: 2026-09-07
    72	  - content: v2 核心:不推論「完成」,只報告「這個任務宣告的證據現在是什麼狀態」——對計劃宣告的測試名當場在工作樹上跑,回報「不存在/存在但紅/存在且綠」
    73	    id: d7
    74	    context: r1 五席四席判 blocker。六個 blocker 群的共同形狀:每一條都來自「拿一個代理物(trailer / CI 紀錄)去推論完成」,而每個代理物都有縫,每條縫都生出一個**假完成**——正是本案要消滅的病
    75	    why_chosen: ★不推論就沒有縫★:識別碼問題消失(任務的名字就是它宣告的測試名,那是程式碼裡真實存在的符號,天生唯一可定址,改名會被既有 doctor Check Y 抓到);trailer 四種靜默失敗全部消失(不用 trailer);CI 對應問題消失(當場跑,只跑宣告的那幾個不是全套);★未提交態解決——讀工作樹不讀提交歷史,session 做到一半還沒 commit 照樣看得見,而 r1 指出那正是最急迫最常見的一格★;提交夾帶不影響(不依賴提交歸屬);f2 的反對被正面處理不是躲開(不宣稱測試綠=完成,推論交給讀的人)。★與 trailer 的關鍵差別:trailer 寫錯的輸出跟沒寫一樣(靜默),測試名寫錯的輸出是「不存在」(看得見)★。代價:只覆蓋有宣告測試名的約 75%;跑測試要時間(只跑子集,要量);答不出「相依功能有沒有回歸」那一半
    76	    decided: 2026-09-07
    77	    valid: true
    78	---
    79	# 進度從提交推導_計劃
    80	
    81	> 白話:現在「這件事做到哪一步」是人手寫在筆記裡的,所以會漂——有一篇計劃狀態寫「做完了」,
    82	> 裡面 60 個勾選框一個都沒勾。本案要把它換成**算出來的**:每個工作項給一個名字,
    83	> 完成它的那個提交把名字掛上去,進度就從 git 算,沒有東西需要人維護。
    84	
    85	> **本篇用到的三個詞**:「外家」=不是編排者那一家的審查席(本 repo 慣例上是 Codex);「f2」=某輪外家報告的第 2 條發現(此處指 [[Projects/執行DAG_調研]] 那輪);「編排者」=負責派審查員、判讀報告、折入修正的那個角色(本案是主對話的 AI);「群」=[[Projects/全repo審視_計劃]] 把 130 條發現去重合併後、可獨立交付的分組。
    86	
    87	PRIOR-ART(★v2 重寫;原稿整段在替已死的 trailer 背書,前掃 ③ 抓到是重寫殘留★):①**最小解在既有機制層**——v2 不新增任何資料格式:任務的名字就是它**已經宣告在計劃裡的測試函式名**,跑法用既有的測試子集入口(`-k <關鍵字>`,前掃實跑驗過可用)。②本家可抄的樣板=`loop verify-progress` 的 help 逐字:「不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)。」③世界解:GitHub `Closes #N` 綁 forge;beads / Task Master 已於 [[Projects/執行DAG_調研]] d1 裁「可借形狀、不借實作」。④不採用新依賴:只用 python3 stdlib 與既有測試入口。★⑤ v1 的 git trailer 路線已在 r1 被打死(四種靜默失敗),d1/d2/d5/d6 四條決策全部翻案;本節不再替它背書。★
    88	
    89	## 問題(有症狀、有數字、有消費者)
    90	
    91	**症狀**:任何一個 session 都答不出「這件實作做到哪一步了」。
    92	
    93	**當場量到的數字(2026-09-07)**:
    94	
    95	| 量到什麼 | 數字 |
    96	|---|---|
    97	| Projects 標「進行中」 vs 超過 30 天沒動 | **46 篇 / 其中 17 篇**(★快照 2026-09-07 傍晚;原稿寫 43 是當天稍早的量測,差的 3 篇是同日新增、含本篇自己★。「17 篇」前掃機械重算吻合) |
    98	| 一篇 `status: done` 的實作計畫,裡面的勾選框 | **60 個框,0 個打勾**(12 任務 × 5 步驟,全是實作步驟不是驗收清單) |
    99	| 另一篇實作計畫的勾選框 | **39 個框,全部打勾** |
   100	| [[Projects/全repo審視_計劃]] 的 50 群主清單 | **沒有「做完沒」這一欄**;進度靠翻提交訊息回推 |
   101	| 近 120 筆提交帶項目編號的 | **6 筆**(而且全部集中在那份有編號的主清單上) |
   102	
   103	★第二、三列並列才是重點★:同一個 repo、同一種格式,**有人維護有人不維護,而沒有任何東西會知道差別**。
   104	
   105	**消費者**:①接手的 session(現在只能讀散文猜)②Enzo 本人(問「做到哪」要人回答)③無人自跑的迴圈(未來)。
   106	
   107	## 根因:完成與記錄是兩件事
   108	
   109	- **審查迴圈為什麼準**:★「完成一輪」和「記下一輪」是**同一個動作**★——那筆帳本身就是工作成果。不可能做了沒記,也不可能記了沒做。
   110	- **實作為什麼歪**:工作成果是程式碼,記錄是另外去勾一個框。**兩件事分開就一定會漂**;那 60 個沒勾的框就是這樣來的。
   111	
   112	**所以本案不是「做一個進度追蹤器」,是「讓完成那個動作自己留下紀錄」。**
   113	
   114	## ★v1 死在哪、v2 怎麼改(2026-09-07,設計審 r1 五席四席判 blocker,Enzo 裁整份重寫)★
   115	
   116	**六個 blocker 群的共同形狀,收斂成一句**:每一條都來自**拿一個代理物去推論「完成」**,而每個代理物都有縫,★每條縫都生出一個假完成★——正是本案存在的理由要消滅的病。
   117	
   118	| r1 打死的 | 死因 | v2 怎麼處理 |
   119	|---|---|---|
   120	| 識別碼用 `[SN]` | 粒度錯(是設計階段標記不是任務單位;本篇自己的 [S1][S2][S3] 就是三段設計步驟)+ 對本文舉的兩篇症狀零覆蓋(它們用 `### Task N`) | ★不需要識別碼★——任務的名字就是它宣告的測試名 |
   121	| 完成 = 提交掛 trailer | 四種靜默失敗:錯字無攔截、訊息結尾非鍵值形狀整段消失(連既有兩個一起)、squash 吃掉、revert 不帶 | ★不用 trailer★ |
   122	| 綠 = CI 那筆 | CI 綁 push 的 tip sha(中間提交結構性查不到)、`ci-status` 只回最後一筆、同 sha 重跑轉綠被舊的紅蓋過、凍結當時綠→永久假完成 | ★不讀 CI,當場跑宣告的那幾個測試★ |
   123	| 根因「完成與記錄是同一動作」 | 多 session 提交夾帶時 trailer 只掛夾帶者的;★未提交態完全不可見,而那是「做到一半」最急迫最常見的一格★ | ★讀工作樹,不讀提交歷史★ |
   124	| 「換粒度躲開 f2」的論證 | 反駁②自己寫明只在新功能成立,但判準涵蓋增修既有功能;且連結了會反駁自己的姊妹研究卻從未回應 | ★不躲——不宣稱「測試綠=完成」★ |
   125	| 任務級解析度 | 沒有可執行的資料源(CI 的 JSON 是 workflow 級無逐測試欄位) | 資料源就是測試名本身 |
   126	
   127	**r1 沒有攻擊、因此保留的**:上面的診斷與數字(全部被獨立重算吻合)、根因分析、範圍刀、零依賴家規、以及「否掉 code-loop pass」這個判斷本身。~~效能也被兩席各自量過:全量掃描 47 毫秒~~ → ★**前掃指出這句被誤用**★:那 47 毫秒量的是 **v1 已死的 trailer 全量掃描**,不是 v2 的「當場跑測試」。**放在這裡會被讀成「v2 效能已驗過」,實際沒有。真實數字見下面誠實天花板。**
   128	
   129	## v2 核心:不推論「完成」,只報告「證據現在是什麼狀態」
   130	
   131	★這是整個 v2 的那一刀★:**停止推論,直接報事實。**
   132	
   133	- 計劃裡每個任務**已經宣告了它的測試名**(先前量過:74 個任務段裡 56 個有,約 75%)。
   134	- 查詢就做一件事:**對這份計劃宣告的每個測試名,現在在工作樹上跑一次,回報三種狀態之一——「不存在 / 存在但紅 / 存在且綠」。**
   135	- ★不說「完成」,說「它宣告的證據現在是什麼狀態」。推論交給讀的人。★
   136	
   137	**為什麼這樣就沒有縫**:縫是「代理物與事實之間的落差」;不做推論,就沒有那段落差可以漏。
   138	
   139	**與 v1 最關鍵的一個差別(直接回應 r1 的靜默失敗批評)**:
   140	- trailer **寫錯的輸出跟沒寫一樣**(都是查無資料)——★靜默★。
   141	- 測試名**寫錯的輸出是「不存在」**——★看得見★。**這一條仍然成立,但它的機械支撐要換人。**
   142	- ★**前掃推翻原稿的舉證**★:原稿說「既有 doctor Check Y 本來就會抓這種漂移」——**不成立**。Check Y **只掃 `type: system` 節點**,而 14 份實作計畫全是 `type: project`;程式碼註解還明講為什麼刻意排除:「Projects 提的是『打算做的方法』(還沒寫),對那些節點報 repo 查無是**誤報而非發現**」。
   143	- ★而且那個理由是對的,所以**不能**把 Check Y 擴到 Projects★——那會製造誤報。**正確的說法是:「不存在」在本案的查詢裡是三態之一、是合法資訊,不是錯誤;它的可見性由本案自己的輸出保證,不靠既有健檢。**
   144	
   145	## 設計
   146	
   147	### [S1] 抽取:從計劃節點讀出「任務 → 宣告的測試名」
   148	
   149	- ★**前掃推翻原稿:沒有「既有測試名抽取」可以重用**★——`SPEC_CLAUSE_RE` 抽的是 `[SN]` 設計條款,`cmd_spec_trace` 做的是條款級追溯,**跟測試函式名毫無關係**。原稿寫「重用既有抽取」是空的前提,撤回。
   150	- 所以 [S1] **是新寫一份抽取**。既然是新寫,就要正面回應 r1 架構席那條:`(.+?)#(d\d+)` 此刻有三份互不共用(前掃精確重數確認,其中兩份各自 inline、沒呼叫現成的 `_dref_parse`)。★本案的抽取一開始就要寫成單一函式並被測試釘住,不得重演那個形態。★
   151	- **一個測試服務多個任務要偵測並報告**(f2 的原始案例:某計劃 Task 1–5 全部往同一個測試函式裡續加斷言)。★偵測到就明說「這幾個任務宣告同一個測試,分不出誰做完」★,不假裝分得出。
   152	
   153	### [S2] 查詢:當場跑,只跑宣告的那幾個
   154	
   155	- 跑法用既有的測試子集入口(`-k <關鍵字>`),不跑全套。
   156	- 三態輸出:不存在 / 存在但紅 / 存在且綠。**沒有第四種「完成」。**
   157	- 唯讀、不寫回筆記、不改任何狀態欄。
   158	
   159	### [S3] 慣例:讓「宣告測試名」這件事被看見
   160	
   161	- 現況 75% 的任務段已經在寫,**這是既有慣例不是新規定**。
   162	- 缺的那些,查詢輸出裡明列「這幾個任務沒有宣告測試,算不出來」——★不靜默略過,也不顯示成未完成★。
   163	
   164	## 範圍刀(明確不做)
   165	
   166	- **不建第二張圖、不建任務狀態檔、不做認領租約、不碰審查迴圈那條線、不自動改 status 欄**(v1 的五條全部保留)。
   167	- **不做跨任務依賴**——依賴建立在「完成」之上,而本案刻意不判完成。
   168	- ★**不答「可以出貨了沒」**★:Enzo 裁的判準有兩半,本案只碰得到「這個功能的測試綠不綠」,**答不出「相依功能有沒有回歸」**(那要全套,查不起)。那一半仍歸推送前的閘與 CI,**不在本案射程**。
   169	- **不用 git trailer、不讀 CI**——v1 的兩條主機制在 r1 被打死,v2 不留殘骸。
   170	
   171	## ★誠實天花板★
   172	
   173	- **只覆蓋約 75%**:沒有宣告測試的任務(改 skill 散文、圖譜回填、真機驗收)算不出來,**輸出明說算不出來**。★r1 之後仍成立,而且那 18 個還沒逐一分類。★
   174	- **「宣告測試名」這一步仍是自律**:人要在計劃裡寫。但★寫錯是看得見的(報「不存在」),不是靜默的★——這是它跟 v1 的 trailer 的本質差別。
   175	- **跑測試要時間——★前掃已補量,結論是「看關鍵字精不精確」★**:單一任務粒度很快(`-k impact_cli_skeleton` 2 條 0.8 秒、`-k spec_trace` 12 條 1.88 秒,大半是啟動開銷);**但關鍵字不夠精確會命中一整族**——`-k impact` 命中 305 條、**23.4 秒**。
   176	- ★所以這是一條新的真實邊界:宣告的測試名要夠精確,否則查詢會從 1 秒變成 20 秒以上★。原稿完全沒提到這件事,要進設計(例如:抽到的關鍵字命中數超過門檻就拒跑並報「這個宣告太寬」)。
   177	- **一個測試服務多個任務時分不出誰做完**:偵測得到、但解不掉,只能報告。
   178	
   179	## 待裁(留給 v2 的設計審)
   180	
   181	- 測試名抽取要用什麼樣式?前掃實數:`` `t_xxx` `` 235 次、全大寫 `TEST:` 40 次(是摘要欄位不是任務級)、中文「測試:」40 次、`-k xxx` 25 次、`**Test**:` 7 次。★最棘手的是中文「測試:」那種——純散文、連反引號或關鍵字都沒有,**根本抽不出可執行識別碼**★(例:某實作計畫寫「測試:對 fixture 跑 delta --json:已判不重出……跑紅」)。要不要先釘一個樣式,還是接受抽不到就報「沒有宣告」。
   182	- ★「任務段」這個分母本身沒有唯一機械定義★:同一批筆記上量過 73 / 74 / 83 三個數(切法不同)。設計要明講用哪一種切法,否則覆蓋率這個數字永遠對不齊。
   183	- 跑不動的環境(沒裝依賴、要真機)怎麼報?算「不存在」還是第四態?
   184	- 那 18 個沒有測試的任務段,要不要在本案處理,還是明講不處理。
   185	
   186	## 驗收線
   187	
   188	- 對一份真實的實作計畫,**不讀它的勾選框、不讀任何提交**,答出每個任務宣告的測試現在是三態的哪一態。
   189	- **在一棵有未提交改動的工作樹上照樣答得出來**(★這是 v1 死掉的那一格,v2 必須當場證明★)。
   190	- 沒有宣告測試的任務段,輸出**明說算不出來**。
   191	- 一個測試被多個任務宣告時,輸出**明說分不出誰做完**。
   192	- 測試 fixture ★用真的呼叫產生,不手刻★(2026-09-07 教訓)。

exec
/bin/zsh -lc 'for f in governance/review-reports/進度從提交推導/r1-邊界.md governance/review-reports/進度從提交推導/r1-外家codex.md governance/review-reports/進度從提交推導/r1-接手.md governance/review-reports/進度從提交推導/r1-正確性.md governance/review-reports/進度從提交推導/r1-架構對齊.md governance/review-reports/進度從提交推導/r1-intake.md; do echo "$f"; nl -ba "$f"; done' in /Users/enzo/harness/lumos-toolchain
 succeeded in 0ms:
governance/review-reports/進度從提交推導/r1-邊界.md
     1	severity: blocker
     2	
     3	# 邊界可執行席 r1
     4	
     5	## F-bnd-1 ★blocker★ 「兩級解析度」沒有落成任何交付步驟
     6	severity: blocker
     7	blocking: 是
     8	引句:「★但不必換判準就能補★:先前量過,74 個任務段裡 **56 個(75%)** 自己就寫了對應的測試函式名。」
     9	[S1][S2][S3] 全部只圍繞 [SN] 與 trailer,沒有一步是「讀任務級測試名並查現況」;驗收線只驗得到 [SN]/trailer 那一層。甲節自承那是「接手最需要的那一格」。
    10	
    11	## F-bnd-2 ★blocker★ [SN] 是設計階段粗粒度標記,不是「單一提交可完成」的任務單位
    12	severity: blocker
    13	blocking: 是
    14	引句:「**標記已經有**:計劃裡寫 `[S1]`/`[S2]` 是既有慣例,而且**已經有消費者**」
    15	file: `docs/lumos-toolchain-knowledge/Projects/進度從提交推導_計劃.md:102`
    16	file: `docs/lumos-toolchain-knowledge/Projects/中心性重驗排程_計劃.md:29`
    17	本篇自己的 [S1][S2][S3] 就是三段設計步驟不是任務;32 篇含 [SN] 的筆記中 11 篇是章節標題,其餘每個 [SN] 仍對應整塊功能設計。沿用它當工作項識別碼,天生答不出甲節要的細粒度。
    18	
    19	## F-bnd-3 ★blocker★ trailer 格式地雷:前一行不是鍵值形狀,整段靜默消失
    20	severity: blocker
    21	blocking: 是
    22	引句:「讀取端:`git log --format='%(trailers:key=Task,valueonly=true)'`」
    23	實測 git 2.39.2:body 結尾若非鍵值形狀,`%(trailers)` 整段回空——連 `Co-Authored-By` 一起消失且無錯誤訊息。本 repo 習慣以長散文/編號清單收尾,離這個地雷不遠;「漏加」與「加了但格式錯」輸出完全相同。
    24	
    25	## F-bnd-4 ★blocker★ 同 sha 重跑轉綠,判定仍被舊的紅蓋過
    26	severity: blocker
    27	blocking: 是
    28	引句:「CI 那筆的語意就是對的。」
    29	file: `scripts/lumos:16487`
    30	對同一 sha 先記 failure、重跑轉 success,`cmd_ci_status` 仍回報紅——[D6] 選的綠訊號在 rerun 修 flake 這個常見場景下卡死。
    31	
    32	## F-bnd-5 decision_refs 的 dangling 攔截在 CLI 寫入路徑,手打 trailer 無等效攔截
    33	severity: major
    34	blocking: 是
    35	引句:「定址形狀已經有:決策的定址是 `<節點rel>#dN`(程式裡有格式驗證與 dangling 偵測)。」
    36	file: `scripts/lumos:10401`
    37	file: `scripts/lumos:10405`
    38	commit 當下沒有攔截點擋錯字或不存在的 [SN];錯字一旦 push 就永久寫入歷史,無安全事後修正路徑。
    39	
    40	## F-bnd-6 `cmd_ci_status` 沒有 sha 參數
    41	severity: major
    42	blocking: 否
    43	引句:「所以本案不必新建測試結果帳,接既有的即可」
    44	file: `scripts/lumos:16454`
    45	資料可重用沒錯,但讀取碼要新寫,不是接既有指令就好。
    46	
    47	## F-bnd-7 revert 不帶 trailer → 永久卡住的假完成
    48	severity: major
    49	blocking: 是
    50	引句:「完成它的那個提交把名字掛上去,進度就從 git 算」
    51	`git revert --no-edit` 產生的訊息只有 `This reverts commit <sha>.`,不複製任何 trailer;[S3] 仍回報原工作項有提交掛過,無訊號反映已被撤銷。
    52	
    53	## F-bnd-8 「未知」其實是三種不同狀況
    54	severity: major
    55	blocking: 否
    56	引句:「★「還沒推」= **未知**,不是「未完成」★」
    57	file: `.github/workflows/ci.yml:5`
    58	「本機還沒推」「已推但分支不觸發 workflow」「已推但忘了記帳」在帳上輸出完全一樣;方向沒錯但文字要講清楚是哪一種。
    59	
    60	## F-bnd-9 多 session 夾帶 commit 打穿根因前提
    61	severity: major
    62	blocking: 是
    63	引句:「★「完成一輪」和「記下一輪」是**同一個動作**★」
    64	file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:42`
    65	既有事故:一邊 `git add -A` 把另一邊全部交付一起 commit、訊息只寫自己那件。夾帶時 trailer 只掛夾帶者的識別碼,被夾帶的工作項不會被記到——「這個 commit 的 diff 對應這個 trailer」的假設本身不成立。
    66	
    67	## F-bnd-10 [SN] 重新編號比改名更隱蔽
    68	severity: major
    69	blocking: 否
    70	引句:「計劃節點改名會讓舊 trailer 指不到」
    71	插入新條款把 S3 變 S4 之後,舊 trailer 的 #S3 靜默指向不同內容,且無偵測手段;是 D4 未涵蓋的獨立假完成來源。
    72	
    73	## 規模與空集合(乾淨)
    74	severity: clean
    75	本 repo 1740 筆提交,`git log --all` 全量 trailer 掃描實測 47ms,無效能疑慮;零 [SN]/零提交/空 CI 帳三種空集合可比照 `cmd_spec_trace` 既有前例。
    76	
    77	## 總結
    78	severity: blocker;blocking 7 條(F-bnd-1,2,3,4,5,7,9),major 非 blocking 3 條。
governance/review-reports/進度從提交推導/r1-外家codex.md
     1	Reading additional input from stdin...
     2	OpenAI Codex v0.153.2
     3	--------
     4	workdir: /Users/enzo/harness/lumos-toolchain
     5	model: gpt-5.6-sol
     6	provider: openai
     7	approval: never
     8	sandbox: read-only
     9	reasoning effort: low
    10	reasoning summaries: none
    11	session id: 01a07aad-cdab-7c51-b959-dee599ab6446
    12	--------
    13	user
    14	你是外家否決席(不是編排者那一家)。這是一份**外部第三方投稿的設計 spec**,任務是找出作者沒看到的洞。
    15	
    16	工作目錄 /Users/enzo/harness/lumos-toolchain(唯讀查證,不要改任何檔)
    17	被審的凍結審材:governance/review-reports/進度從提交推導/r1-snapshot.md(200 行)
    18	真正的計劃節點:docs/lumos-toolchain-knowledge/Projects/進度從提交推導_計劃.md
    19	技術棧:python3 stdlib、零外部依賴;單檔 CLI `scripts/lumos`、測試 `scripts/test_lumos.py`
    20	
    21	**這份在主張什麼**:現在「這件事做到哪一步」是人手寫在筆記裡所以會漂;改成算的——工作項用既有的 `[SN]` 條款標記取名(定址 `<計劃節點rel>#S1`,比照決策的 `#dN`)、完成它的提交掛 `Lumos-Task:` git trailer、進度從 git 與 CI 算出來、★不寫回筆記★。完成判準由專案主人裁定:掛在實作端看測試,功能級=該功能測試套綠 + 相依功能無回歸,明確不做散文級判準。
    22	
    23	**已經跑過、不要重報**:機械 refcheck(1 條檔案宣稱,ok)、模糊措辭掃描(零命中)、前掃四類(已折入三條語意修正:spec-trace 的 [SN] 實際使用率、一處引句改逐字、trailer 產生機制其實是 AI 手打不是模板)。
    24	
    25	**火力集中處**
    26	
    27	1. **★六條決策(D1-D3 與 frontmatter d1-d6)裡,哪一條的理由站不住?★** 逐條查。特別是:
    28	   - d6/D3「用 CI 那筆、不用 code-loop pass」——理由是「code-loop 記的是審查過了不是測試綠了,而且狀態值有 skipped」。**這個理由對嗎?去讀那兩個東西實際記什麼。** 有沒有可能 CI 那筆其實更不可靠(例如只記最後一次、不是每個 commit 都有)?
    29	   - d4/D1「沿用 [SN],定址比照 `#dN`」——**決策定址真的可以照抄嗎?** `#dN` 的 id 是工具指派且承諾穩定(翻案也保留原號);`[SN]` 是人手寫在散文裡的,穩定性一樣嗎?
    30	   - d3「完成判準功能級」——作者主張外家先前的反對(測試綠≠任務完成)在功能級失效。**這個「換粒度就躲開反對」的論證有沒有漏洞?**
    31	
    32	2. **★這份自己承認「只蓋四分之三」,那四分之一怎麼辦沒答★**。沒有測試可掛的工作(改 skill 散文、圖譜回填)在這個系統裡會長什麼樣?會不會永遠顯示成「沒人做過」——而那正是它要消滅的假狀態?
    33	
    34	3. **[S2] 靠人記得加 trailer,零機械守衛**(前掃已抓到並寫進審材)。這跟本案主張的「不靠人維護」有多大落差?**有沒有更小的做法能拿掉這個自律依賴?**
    35	
    36	4. **有沒有第四條路**:不用 trailer、不用 [SN],也能讓「做到哪」變成算得出來的?作者只想了一條。
    37	
    38	5. **這份會不會其實不該做**:它自己寫「本案的價值還沒有本地證據」。用這個專案自己的判準(有症狀、有消費者、最小解在哪一層)衡量,立案成立嗎?
    39	
    40	**規則**
    41	- 每條 finding 附 `引句:「<逐字 ≥10 字,抄自凍結審材>」`、`severity: blocker|major|minor`、`blocking: 是/否`(兩欄不得矛盾:blocking:否↔minor)。
    42	- 審材外的證據用 `file: \`路徑:行號\``(反引號必加),不得用引句格式主張審材外內容。
    43	- 敘述每條 ≤3 句,不准「可能/建議考慮」這種收尾。
    44	- 報告第一行寫一行獨立的 `severity: <本輪最高>`;乾淨也要寫 `severity: clean`。
    45	- ★沒實際查證過的猜測不要寫成 finding★。你能開檔、能跑指令,請用。
    46	hook: SessionStart
    47	hook: SessionStart
    48	hook: SessionStart Completed
    49	hook: SessionStart Completed
    50	codex
    51	我會依外家否決席規格做唯讀查證；先用 `lumos` 進圖譜，再逐條核對凍結審材、計劃節點，以及 CI／code-loop 的實際落帳語意。
    52	exec
    53	/bin/zsh -lc 'python3 scripts/lumos search "進度 提交 推導"' in /Users/enzo/harness/lumos-toolchain
    54	 succeeded in 415ms:
    55	(多詞回退:你查的整串詞在未作廢的節點的可見文字裡找不到完全一致的,改成每個詞分開查、有出現就算;逐詞覆蓋 進度:20  提交:28  推導:28)
    56	(已隱藏 3 筆作廢結果;要看的話加 --include-superseded)
    57	提醒:命中≠查完——搜尋只告訴你「哪裡可能有」,不是完整內容;光看摘要就判「圖譜沒記」以前真的出過錯。下結論前先讀全文:lumos show <節點>
    58	 11.832  Projects/進度從提交推導_計劃.md  [進度,提交,推導]
    59	    17 [KEY]: KEY:立案(2026-09-07,Enzo 裁「首要工作=讓做到哪一步也能同步並且可信」後再切一刀)——★本案不是做進度追蹤器,是讓「完成」那個動作自己留下紀錄★
    60	    19 [KEY]: KEY:★症狀數字(2026-09-07 當場量)★:Projects 標進行中 43 篇其中 17 篇 >30 天沒動;一篇 status=done 的實作計畫 60 個框 0 …
    61	    20 [KEY]: KEY:★因果鏈沒有分叉,斷點在最前面★——工作項沒有在筆記之外還活著的識別碼 → 提交掛不上 → 沒有可追加的紀錄 → 完成狀態只能手寫 → 一定漂
    62	    21 [KEY]: KEY:★PRIOR-ART 最強的一條:不用發明格式★——git 原生有 trailer,`git log --format='%(trailers:key=X,valueonl…
    63	    22 [KEY]: KEY:設計三步(各可獨立交付)=[S1] 工作項取名(只定慣例不寫程式)/[S2] 完成的提交掛 `Task: <識別碼>` trailer/[S3] 唯讀查詢從 git 算進度…
    64	    24 [KEY]: KEY:★誠實天花板:最多蓋到四分之三★——74 個任務段裡 56 個(75%)抽得出對應測試名,剩 18 個天生沒有(改 skill 散文/圖譜回填/真機驗收);那類沒有提交可掛…
    65	    25 [KEY]: KEY:★待裁四題★①識別碼從哪來(沿用 50 群的 #N / 每份計劃 T1..Tn 會撞名 / 計劃名+任務號)②trailer 鍵名(避開既有與世界慣例語意衝突)③「完成」定…
    66	    26 [KEY]: KEY:驗收線=不讀勾選框就答得出每個工作項有沒有被提交掛過與最後一次何時;對那 18 個算不出來的**明說算不出來**;三步各有測試且 ★fixture 用真的呼叫 git 產生…
    67	    … 還有 25 處
    68	  7.098  Projects/執行DAG_調研.md  [進度,提交]
    69	    14 [KEY]: KEY:★腐化數字(★量測時點 2026-09-07,含活計數,引用必帶時點★)★:Projects 標 doing 43 篇(母體 155,含本篇自己)、其中 17 篇 >30 …
    70	    16 [KEY]: KEY:★settle 前例極性被翻轉(外家 f3)★——`.lumos/settle/公開精簡版-settle.json` 35 條原本被當「可抄的結構化進度前例」,實查是**死…
    71	    50 [body]: PRIOR-ART:①最小解在既有機制層——「唯一下一動作」的神諭已經有了(`lumos loop next`,只讀帳本結構不讀散文),只差一個「列出現在開著的迴圈」的入口;結構化…
    72	    68 [body]: 1. **實作計畫筆記的任務拆解**——T1..Tn、「包①→②→③嚴格順序」、每任務寫明改哪/測什麼/斷言什麼,底下「進度」段記日期與教訓。
    73	    100 [body]: | [[Projects/全repo審視_計劃]] 的 50 群主清單 | **表格沒有「做完沒」這一欄** | 進度靠翻 git 提交訊息裡的 `#編號` 回推;開頭「一件都還沒…
    74	    107 [body]: 1. **只讀結構不讀散文的進度指令**:`lumos loop verify-progress` 的 help 自述「不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)」…
    75	    108 [body]: 2. **★結構化逐條進度清單——原稿當成正面前例,外家查證後翻成反證★**:`.lumos/settle/公開精簡版-settle.json`,35 條,每條 `{id, kin…
    76	    170 [body]: - **commit trailer / session manifest**:解「提交夾帶、歸屬讀不出來」,成本極低。
    77	  7.005  Issues/推新分支時風險分級拿空樹當起點.md  [提交,推導]
    78	    15 [KEY]: KEY:★這是刻意的 fallback 不是 bug★——scripts/hooks/pre-push 範圍推導三分支,註解明寫「新 ref(含首推 main:遠端無此 ref)→…
    79	    17 [KEY]: KEY:誠實界線——影響面比第一眼小:這個 repo 慣例是本地開分支、本地合併、★只推 main★(實查遠端只有 main 一個分支,本地有 8 個功能分支+多筆 merge 提…
    80	    31 [body]: `scripts/hooks/pre-push` 的範圍推導有三條分支,註解寫得很清楚:
    81	    56 [body]: - **這個 repo 的慣例是本地開分支、本地合併、只推 main**。實查:遠端 `git ls-remote --heads Lumos` ★只有 `main` 一個分支★,…
    82	  6.958  Systems/guard-kill.md  [提交,推導]
    83	    16 [KEY]: KEY:宣告式壞法(人寫,從業務行為推導非實作反轉;繞開等價變異不可判定)｜run_cmd由config宣告(platforms.X.run_cmd/legacy test.run…
    84	    18 [★DEBT★]: KEY:★DEBT★ hydration(未提交帶入)與lockfile v1砍(否決位裁);E2E maestro {method}不適用;冷build成本;submodule不…
    85	  6.167  Projects/guard殺傷力驗證_計劃.md  [提交,推導]
    86	    49 [★INVARIANT★]: 1. **壞法由人宣告，不自動生成；配方存節點級 `kill_recipes` frontmatter 欄位（r1 折入：不進 decisions——decisions 是節點級平…
    87	    52 [body]: 3. **原始碼層隔離 + baseline 前置（r1 折入：正名——worktree 只隔離檔案，不隔離 DB/埠/外部狀態）**：對**配方 platform 的 repo …
    88	    80 [body]: - HEAD 基準：worktree **看不到**主樹未 commit 的新測試檔、kill 以已提交內容跑（r2 descope 的反向迴歸）。
    89	    87 [body]: - dirty 工作樹警告：未提交變更時 kill 印警告且以 HEAD 內容跑。
    90	    98 [body]: - **r1（2026-07-10，panel W=5：4 canaried opus（新出題程序首跑：載重錨定+haiku 探針 4/4 probe:pass+事故庫無匹配走輪替…
    91	    115 [body]: - ISO 26262 fault injection、DO-178C requirements-based coverage（需求推導壞法、人審把關）
    92	  5.144  Projects/loop三輪壓縮_計劃.md  [提交,推導]
    93	    18 [KEY]: KEY:收斂判準(2026-07-09交叉查文獻升級)=falsification-存活(辯方零≥major,borrow falsification>voting)∧低分歧(W審…
    94	    52 [body]: 一輪 panel 收斂 = **四條合取**(全建在 framing 汙染不到的結構上;推導與文獻見下「散文收斂」節):
    95	    87 [body]: - **F3 agreement 形式定義(2026-07-09 交叉查文獻升級:從二值門檻→falsification+低分歧+自適應提交)**:收斂判準**不是**「辯方後 m…
    96	    90 [body]: - **③ 自適應提交(borrow CGES 2511.02603 / DASE 2605.04236)**:round-1 panel 若 falsification 後**全…
    97	  3.824  Verification/2026-08-04_design-loop重設計落地T1-T7.md  [進度]
    98	    24 [body]: **計畫**：[[Projects/design-loop重設計_實作計畫]]（逐包進度與教訓記於該節點〈進度〉）
    99	  3.803  Systems/anchor-integrity.md  [提交]
   100	    67 [body]: ## ★簽名檔本身沒提交,是這道守衛的天生破口(2026-09-06 實際被 CI 咬到)★
   101	    69 [body]: **發生什麼**:折完一輪代碼審要推,推送前的閘擋我「把關檔改過沒簽名」。我簽了名、也把改動提交了——但只提交了知識庫那個資料夾,而**簽名檔放在治理資料夾底下**,沒進去。推送過…
   102	    76 [body]: **最坑的地方**:CI 的錯誤訊息會叫你「重新核可並留理由」——照做也沒用,因為問題根本不是沒簽名,是簽了沒提交。訊息把人指向錯的方向,而這種紅燈又特別像「守衛壞了」。
   103	    78 [body]: **怎麼修的**:推送前的閘多一道——簽名檔如果處在「改過但沒提交」的狀態就擋下,訊息直接講「沒提交」並給提交指令,不叫人再簽一次。守衛配的是**行為測試不是字串比對**:真的搭一…
   104	  3.790  Issues/同工作區多session並行改動.md  [提交]
   105	    13 [KEY]: KEY:2026-08-22 一天三型:①數字漂移(紅得像自己改壞的)②提交夾帶(git add -A 把對方全部交付一起 commit、訊息只寫自己那件)③變數共用(結果好但純靠…
   106	    15 [KEY]: KEY:候選解多兩條——(d) 同工作區 session 互相通報(這次真正管用的就是對方主動傳訊,機器對機器不是人轉述;它擋的是誤修與提交夾帶,不是壞檔本身,而且要兩邊都記得);…
   107	    40 [body]: ### ② 提交夾帶:訊息完全對不上內容
   108	    74 [body]: - **(b) 提交時提醒**:pre-commit 看 `git diff --cached` 涉及的檔,若有檔案的
   109	    114 [body]: - 前三型(數字漂移、提交夾帶、變數共用)都是**事後**才發現,但發現時證據還在。
   110	    122 [body]: - **沒有夾帶**:我最後一個提交(08b0e61)時間點剛好在對方開始改之前,查證過沒有夾到。
   111	    135 [body]: ★它擋的是「誤修」與「提交夾帶」,不是壞檔本身★——知道有人在動那支檔,你就不會去修它。
   112	    202 [body]: 那能擋掉的是**誤修**(第四型裡差一點發生的破壞性補救),以及第二型的提交夾帶。
   113	    … 還有 1 處
   114	  3.764  Projects/code階段強化_計劃.md  [推導]
   115	    18 [KEY]: KEY:[S3]性質測試席(選配,r1/r2 修)——開席=兩機械錨(tier=high ∧ impact 命中星標合約節點)+人工核純函式+具推導源(docstring/型別/圖…
   116	    23 [DECISION]: DECISION:[2026-07-18]S4 拒收記理由防重提;S3 觸發改開席四要件(兩機械錨+一人工核+推導源查核,r1-r3 逐輪收窄);S3 免辯方路由撤除(r1 三方共…
   117	    57 [body]: **現況與舊帳**:07-15 圖譜判「自動生成 property 測試 oracle 不可靠」(agent 自己發明錯誤期望→誤報)。Anthropic 2026-07 配方:推…
   118	    60 [★INVARIANT★]: - **觸發(開席四要件=兩機械錨+一人工核+一推導源查核,r1 收窄、r2 增訂、r3 正名)**:①tier=high **且** ②`lumos impact --diff`…
   119	    61 [body]: - **流程**:席位 agent 讀 diff 涉及的純邏輯函式+文件/型別註解 → 推導 2-3 條性質(從文件推導,禁憑空)→ 該棧 PBT 框架寫測試(C#=CsCheck…
   120	    62 [★INVARIANT★]: - **產出(r1 撤免辯方)**:反例的**可重現性**免爭(那是機械事實);性質的**合法性必過辯方**——辯方(依 S5 預設 Codex)專問:「這條性質真是該函式的業務合…
   121	    123 [body]: 10. [s2] S3 缺「無文件純函式」擋板(硬推=自證 oracle 復辟)→ 開席第四要件:具推導源,缺源不開席留痕。
   122	  3.721  Systems/開發工作流總覽.md  [提交]
   123	    17 [FLOW]: FLOW:①寫計劃(先查圖譜三步;開審第一輪先列出主題已有的節點,避免重複開案)→②設計送審(design-loop:派工時自動把相關節點附給每個審查員[2026-09-05 起 …
   124	    75 [body]: | ③ | impact hook+Stop hook+pre-commit(兩家同一批) | 每次提交都同步節點;收工沒補的當下擋一次(兩家) |
   125	  3.697  Verification/2026-08-24_節點還原SOP落地.md  [提交]
   126	    5 [fm:valid_under]: valid_under: "skill/索引/範本/hook 六處同步版(2026-08-24);探針語料 23 題;Landmark 實跑於 HEAD=28310ee 未提交工作…
   127	    10 [KEY]: KEY:[S7] 實跑=CMS_Landmark(真 brownfield:三年 C# 商業系統、零圖譜、自有 repo):init --no-hooks→骨架 MOC→兩節點(限…
   128	    27 [body]: - Landmark 的改動(vault 5 篇+CLAUDE.md 注入區塊):✅ Enzo 裁**擱置**(2026-08-26)——維持未提交、不收版控、不裝 hooks;該…
   129	  3.695  Issues/真相源實質單一作者.md  [提交]
   130	    14 [KEY]: KEY:本 repo 提交 1,329 筆,其中同一人(Enzo/t)1,311 筆佔 98.6%;另兩位作者合計 18 筆
   131	    37 [body]: | 作者 | 提交數 |
   132	  3.687  Verification/2026-07-04_pitfalls-code-loop.md  [推導]
   133	    11 [fm:valid_under]: valid_under: cmd_pitfalls 三模式(PITFALL_CLASSES 詞表+剝除對齊 assess_spec 含防呆+--check 節檢查+--diff p…
   134	    15 [VERIFY]: VERIFY:行號推導人工+機器雙驗;pattern 去重疊(SELECT/寫入)證第6條非死碼;三道防污染語意經 review 逐條確認;gate G2 段一字未動比對
   135	  3.665  Projects/圖譜結構化查詢_計劃.md  [進度]
   136	    33 [★INVARIANT★]: | risk/金流 且帶 ★INVARIANT★ | search「金流」32 筆噪音 / contracts 全庫 21 條人肉挑 | 土法模擬 8(實收 7:1 筆為待辦散文誤…
   137	    62 [body]: ## 進度
   138	  3.663  Issues/loop-next吐不可宣告的tier.md  [推導]
   139	    53 [body]: `LOOP_TIERS = ("light", "standard", "high")`。**`legacy` 不是可宣告值**——它只是「無定錨舊帳 ＋ legacy 格式」的推…
   140	    70 [body]: | `legacy`（推導） | 1 | **6** |
   141	    107 [body]: **兩條現場成立前置**：① `tier == "legacy"` 且 `phase == "plant-canary"`（證明真的走到 legacy 推導路徑）
   142	  3.663  Projects/關係層主網_實作計畫.md  [進度,提交]
   143	    54 [body]: **進度：M1✅ M2✅ M3✅ M4✅——整包完工（2026-07-15，全套 1103 tests 綠）**：[[Verification/2026-07-15_主網M1_決策…
   144	    73 [body]: - ID 穩定性：一旦指派，即使決策被 supersede 也**保留原 id**（翻案是加 `valid:false`、不刪不換號）；reindex 只補缺、不重排既有。**唯一…
   145	    112 [body]: - **並行（🟠，D10 折入：降宣稱+釘實作形）**：append-only 免 in-place lost-update；寫入走**專用 helper——O_APPEND fd…
   146	  3.652  Issues/探針沙盒能推到真遠端.md  [提交]
   147	    26 [body]: **發現方式**:下午推正式提交被拒(遠端領先),看到「probe snapshot」這個只該出現在沙盒裡的訊息。
   148	    27 [body]: 已用 `--force-with-lease` 覆蓋(確認上面只有那一筆、沒吃掉真提交)。
   149	    35 [body]: 本 repo 歷史上所有 `t@t.t` 提交同此。身分已改 `8yinpro@gmail.com`(本 repo,不動全域)。
   150	  3.642  Verification/2026-07-16_replay校準baseline_v0.md  [推導]
   151	    16 [KEY]: KEY:三結論——①haiku 剖面=grep 可得能抓(白名單/詞不存在),推理/交叉對照型全滅→pre-flight 的 haiku 只配機械清單,語意審最低配 sonnet …
   152	    61 [body]: 3. **洩漏效應分層**:sonnet 先獨立推導、拿 code 演化當驗算並主動揭露;haiku 直接抄。釘住對 haiku 反而提升(答案卡拿走後 grep 到的就是真缺陷態…
   153	  3.549  Projects/loop機械脊椎M1包_計劃.md  [推導]
   154	    19 [KEY]: KEY:#1 loop next——`lumos loop next <id> [--json] [--tier standard|high|light]` 唯讀讀 canary-…
   155	    24 [KEY]: KEY:落地同步義務(七項,由折入衍生,枚舉寫死)——skills/lumos-design-loop/SKILL.md(record 時序 C4/手算 N 改指 next/lig…
   156	    51 [body]: - **無 `--tier` 的身分推導（r3 折入；r7 Codex 終確認統一——原兩處「預設 standard」殘句與 tier 定錨規則分叉，high 可被合法降 stan…
   157	    60 [body]: - `width`：tier→席數（light=1／standard=3／high=5；`--tier` 不給→**依身分推導（定錨優先，見上；r7 統一——舊「預設 standa…
   158	    63 [body]: - **席數下限（r4 新 major；r5 legacy 值；r6 Codex 終判雙補——①數記錄筆數可被同席重複 append 灌滿 ②tier 不持久化，下次省略 --ti…
   159	    135 [body]: - **C1 next 輸入不足不得宣告 converged（major）**：gate 合取依賴 --need/--spec/--repo/--panel——next 改為完整 …
   160	    143 [body]: - **S1-F-CAP（major）**：無 --tier 預設 standard 與 cap 的 legacy 判定自相矛盾——改帳面格式推導（legacy→1/6；panel…
   161	    178 [body]: - **r1（附加式 canary，panel 4 sonnet＋Codex 帶餌＋Codex 無餌否決＋spec 合規席）**：canary 2/5 輪無效——**植入工藝第三筆…
   162	  3.471  Projects/結清式收斂_計劃.md  [進度]
   163	    18 [KEY]: KEY:★首個真實 loop dogfood(2026-07-31,對象=[[Projects/公開精簡版_計劃]];該 spec 兩輪 panel 未收斂、capture-rec…
   164	    42 [body]: - [S3] **獨立進度驗證器（LoopTrap 貴的那半）**：收斂／進度判斷由一個**看不到被審材料**的小驗證器覆核——只讀帳面結構欄位（findings 計數、settl…
   165	    134 [body]: - **進度會累積**：14/35 已結清且只要 spec sha 不動就不必重做；K-streak 模式下每輪重來。這是結清模式對長 spec 的真實優勢。
   166	  3.452  Projects/節點靜態先驗_調研.md  [推導]
   167	    22 [body]: **值得做，但不是「每節點手填三個數字」——是三個機械推導、可消融的 ranking features。**
   168	    50 [body]: ## 手標 vs 機械推導（裁定）
   169	    52 [body]: 特徵機械推導、語意由人標：人只負責既有 type/status/合約/邊;嚴禁手填 `authority: 0.83` 類浮點（GIGO/漂移/自我強化）;若需例外只開離散可 li…
   170	  3.420  Verification/2026-07-29_CI回流閉環v1落地.md  [推導]
   171	    54 [body]: **修法＝把守衛面推廣**：新增 `t_docs_enumeration_drift`，把「禁止手寫數字／列舉」從指令數擴到三類機械可推導事實——
   172	    59 [body]: **通則入帳**：凡文件宣稱一個「可從碼機械推導的清單或數字」，就該有一條這樣的測試——否則它遲早漂移，而且是靠人發現。
   173	    85 [body]: - 值域守衛範圍加上 `Systems/guard-kill.md`（圖譜節點本身），態數宣稱也改為從碼推導；同時清掉 code 裡
   174	  3.381  Systems/delguard.md  [提交]
   175	    27 [KEY]: KEY:[2026-09-06]★逾時降級的真因是命中行數,不是 token 數★——帳上 30% 執行是逾時降級(守衛在半盲狀態下擋人)。原以為跟 token 數有關,量出來是:…
   176	  3.370  Verification/2026-07-28_settle收斂閘.md  [進度]
   177	    42 [body]: - S2（結構化壓縮）與 S3（獨立進度驗證器）未實作、未在本篇認領範圍（方括號條款記號僅用於上方 S1 認領行,此處刻意不用——spec-trace 提及即認領）。
   178	  3.345  Verification/2026-07-28_S2S3壓縮與驗證器.md  [進度]
   179	    21 [body]: # Verification: S2 結構化壓縮＋S3 獨立進度驗證器（2026-07-28）
   180	  3.268  Projects/版本發布流程_計劃.md  [進度,提交]
   181	    167 [body]: ## 進度(2026-09-06 全 repo 審視補記)
   182	    190 [body]: - **[S8] `lumos --version`**:印版本標籤 + 內容指紋(短碼、分支、有沒有未提交的改動),
   183	  3.239  Systems/pitfalls-code-loop.md  [推導]
   184	    29 [FLOW]: FLOW:pitfalls spec 模式(剝除對齊 assess_spec+防呆→掃 PITFALL_CLASSES 四類→印通用 4 問(3 固定+1 風險類反問,2026-0…
   185	    48 [fm:context]: context: 使用者質疑代碼 canary 污染風險比 spec 嚴重(假 hunk 改變語意、reviewer 推導衍生幻影 findings)
   186	  3.214  Projects/doctor-run事件_計劃.md  [推導]
   187	    35 [body]: - ★「已清」的判讀方式★:本事件**不**列受檢節點(nodes 恆空);「某節點已清」由讀帳方推導=「該 run 有 doctor-run 標記,但該 run 內沒有該節點的 …
   188	    51 [body]: - **std r1(2026-08-21,三席同門+外家 gemini)**:major 1(s1:過濾落在 `ded` 上會連 stats 一起濾掉,測試只斷 gate 名會假…
   189	  3.203  Projects/全repo審視_計劃.md  [進度,提交]
   190	    12 [body]: > 白話:2026-09-05 夜到 09-06,派 16 個不同鏡頭的乾淨 agent 把整個 repo 掃一遍找可優化處,每條再派兩個反方(一個查事實、一個查圖譜先例與家規)去…
   191	    88 [body]: ## (舊)中途進度快照
   192	    135 [body]: - repo 根目錄有一支 5 位元組的測試殘骸(內容是字面空陣列),跟著一個自主迴圈的 commit 被順手提交。
   193	    318 [body]: - **為什麼**:新手照 ONBOARDING 走,第一步就撞到 2026-06-26 拆掉、至今被靜默吞掉的 ./install.sh --copy(以為拿到複製版,其實是 s…
   194	    482 [body]: - 同步改了提交前守衛的排除清單(既有漂移守衛會逐項比對兩份清單),加一條測試釘住。
   195	    503 [body]: - **★blocker:我把硬閘弄鬆了★**。刪除守衛的排除清單跟提交前守衛的豁免清單,有一條既有的漂移守衛逼它們逐字相同。我加了治理目錄到前者,為了讓漂移守衛過,就機械照抄到後…
   196	    531 [body]: - **定案:聯集合併**。這幾本是 append-only 的 JSONL,正確解是把兩邊的行取聯集:本機那份讀進記憶體 → 還原到已提交版 → 拉 → 把本機獨有的行補回去。非…
   197	    538 [body]: - **★blocker:資料會靜默遺失★**。聯集合併用「集合判有沒有」,而帳本是事件序列不是集合。審查席對本 repo 實際量:治理帳有 487 行內容完全重複、用量帳有 8 …
   198	    … 還有 4 處
   199	  3.152  Verification/2026-08-22_狀態表過期偵測.md  [進度]
   200	    13 [body]: > 白話:一篇筆記用表格記進度,某一格寫著「待辦」,但那格連到的節點早就做完了。
   201	  3.117  Systems/canary-audit.md  [提交]
   202	    43 [KEY]: KEY:提交的文件永遠不含 canary;token(CANARY-<hex>)只是定位記號,非「抓到」的機械證明——唯一算數的是審計員正確描述了那個瑕疵
   203	    117 [body]: 1. 在工作副本植 1 個**純加性** canary,給唯一 token。**提交的文件永遠不含 canary。**
   204	  3.071  Verification/2026-08-22_guard-kill首次真跑.md  [推導]
   205	    28 [body]: - 壞法是人宣告的,沒有自動生成;這是設計如此(從業務行為推導,不從實作反轉)。
   206	  3.039  Verification/2026-08-08_風險類反問v1落地.md  [推導]
   207	    21 [body]: ## 設計脈絡(Enzo 一連串追問推導)
   208	  2.970  Projects/派工編制資料化_計劃.md  [推導]
   209	    55 [body]: ★**code/standard(循序單 reviewer)v1 不入表、編制對帳不涵蓋**(r1 整合席 blocker,CLI 實測重現):既有 `cmd_loop_next`…
   210	    66 [body]: - kind 判定用 loop id 前綴三值規則(同 S1;**per-command 訊息刻意不同**:loop next 無對帳可跳,indeterminate→roster…
   211	    93 [body]: 2. `t_loop_next_roster`:design/standard 與 code/high 的 `loop next --json` 含 roster 欄且席組成正確;…
   212	  2.964  Verification/2026-08-23_關於欄位離線預標驗證.md  [進度]
   213	    34 [body]: 更糟的是中途查進度時看到 71 個子行程,**就跟 Enzo 說「它真的在逐篇讀所以慢」**——
   214	  2.958  Issues/簿記白名單漏canary與bypass帳.md  [提交]
   215	    27 [body]: Enzo 指示「優化這些部分」——`_BOOKKEEPING_FILES`(scripts/lumos)補 `docs/.canary-log.jsonl` + `docs/.by…
   216	  2.938  Projects/prepush主幹範圍修法_計劃.md  [推導]
   217	    40 [body]: - **逐 ref 推導檢查範圍**：
   218	    49 [body]: - 原 merge-base 推導整段移除（被 stdin 範圍取代）。**git 語意誠實記（r2 Codex#3 minor）**：`remote_sha..local_sha…
   219	    53 [body]: - **旗標名＝`--diff`（r1 s4-F3 折入，原 `--range` 與全 CLI 不一致）**：對齊 `pitfalls --diff`/`cochange --di…
   220	  2.936  Projects/檔案測試依賴地圖_計劃.md  [提交]
   221	    114 [body]: 7. 陳舊三訊號：①非祖先 sha；②build 後候選檔 commit；②′build 後刪檔；③未提交工作區改動；
   222	    126 [body]: 19. 陳舊③：工作區未提交改動觸發（porcelain 解析）；CJK 檔名於②③命中（quotePath）；
   223	    156 [body]: - map 陳舊誤導 → [S2] 三訊號軟提示（祖先鏈＋build 後候選檔異動＋未提交工作區改動）。
   224	    177 [body]: - [major 折入] ① 測試檔判定句「完整檔名 vs stem」自相矛盾 → 拆三子句各自明定比對域（席1+席2）；② `foo_spec` 示例與綴詞表矛盾（會種回 r3 …
   225	    181 [body]: [major] ①駝峰邊界殺自家旗艦例（`.` 前字元）→ 邊界改「前字元非大寫」＋縮寫類取捨記帳（席2+席3）；②剝離規則未複述判定兩套規則＋`ABTest`/`Foo_TEST…
   226	  2.886  Systems/lumos-cli-lifecycle.md  [提交]
   227	    28 [★DEBT★]: KEY:★DEBT★ pull 成功但來源工作區髒(未提交改動)仍會被 vendor 出去——本輪未擋,因來源 repo 的 docs/.governance-log.jsonl …
   228	  2.776  Verification/2026-07-31_slim-claude-md注入.md  [推導]
   229	    49 [body]: - 最初嘗試用「依既有內容結尾自動判斷分隔符」(0/1/2 個換行三種情況)的寫法,推導卸載時要精確逆算分隔符長度過於脆弱;改用「固定分隔符恆為一個 `\n`」的規則後,插入與移除…
   230	  2.729  Verification/2026-07-28_testmap落地與Landmark轉正.md  [提交]
   231	    31 [body]: - 覆蓋 [S3] 全 25 項：naming 各型（含點分 basename 去尾點、`_spec` 直剝、`Foo_TESTS` 底線不敏感、同名唯一 `__tests__/B…
   232	  2.633  Verification/2026-07-31_slim-claude-md第三次裁定取代與備份還原.md  [提交]
   233	    84 [body]: `python3 scripts/test_lumos.py -k slim`——187 checks 全綠(含既有 t_slim_gate/t_slim_readme_asser…
   234	  2.615  Projects/節點還原SOP_計劃.md  [推導]
   235	    15 [KEY]: KEY:★v2-r2 審計(2026-08-24,5 席;arch 零發現)★:「乾淨」判準修正=機械閘為準(現行 panel K=2 連續兩輪,v2-r1 誤明定 K=1;--d…
   236	    197 [body]: - **v2-r3(2026-08-24,5 席,v2 上限輪)**:原始 16 條(s1=2、s2=2、s3=6、arch=2、ext=4),去重約 10,全數折入、零放行。實錘…
   237	    206 [body]: ★達上限未收斂後 Enzo 裁甲(2026-08-24,d7)★:開新編號 `node-restore-sop-v2` 審一輪 v4 delta(r3 折入面+d6 使用場景節+問…
   238	  2.450  Projects/標註刷新_實作計畫.md  [進度]
   239	    106 [body]: - [ ] 圖譜:Verification/2026-08-18_標註刷新落地(plan_refs 雙指計劃+實作計畫)、兩計劃節點 status/進度、retrieval-ran…
   240	  2.392  Projects/地基盤點2026-08-26_調研.md  [進度]
   241	    68 [body]: ## 執行進度
   242	  2.357  Projects/design-loop重設計_實作計畫.md  [進度]
   243	    125 [body]: ## 進度
   244	  2.271  Projects/已知坑機械前置_計劃.md  [推導]
   245	    18 [body]: > 緣起(2026-08-08,Enzo 一連串追問推導出的設計):事故記帳只接「已爆的坑」(先踩才有);世界已知坑(如 refresh-token→single-flight)不…
   246	  2.260  Projects/test-layers軟提醒_實作計畫.md  [進度]
   247	    138 [body]: (pre-commit 會要圖譜同步:本 task 屬計畫執行中,末 task 統一收圖譜——先 `git commit --no-verify` 或把本實作計畫節點 status…
   248	  2.219  Verification/2026-09-07_loop-list開著的迴圈.md  [提交]
   249	    25 [body]: > 或看 git 有哪些沒提交的審查報告資料夾——因為問下一步、問過不過、問審到哪,
   250	  2.193  Systems/外部對照-code衍生wiki.md  [推導]
   251	    76 [body]: openwiki 每條優勢都來自同一個賭注：「文件應是 code 的衍生投影、可丟可重生」。**代價是它裝不下任何 code 裡沒有的東西**——沒有「這條是合約、改＝breaki…
   252	  2.034  Systems/autonomous-iteration-loop.md  [進度]
   253	    84 [fm]: - content: orchestrator-prompt 三修(2026-08-30):①claude -p 活性紀律——派 Agent 後必須同一回合等到結果,散文收尾=本輪…
   254	    149 [body]: - 2026-08-30 **prompt 三修(d8,d7 首輪真跑陣亡後的續修)**:①★claude -p 活性紀律★——派 Agent 必須同一回合等到結果,散文收尾=本輪…
   255	  1.944  Projects/關係層傳播守衛_計劃.md  [進度]
   256	    165 [body]: ## 七、落地順序（實際進度）
   257	  1.942  Projects/自足性審計閉環_計劃.md  [提交]
   258	    76 [body]: 快照 commit 之後才刪,583 個被追蹤的檔全變成未提交刪除,範圍刀每次必判越界,修復鏈名存實亡)★:
   259	    105 [body]: [[Issues/同工作區多session並行改動]] 的「提交夾帶」實例,v5-r1 s1f4★;單行訊息含三 model,本案自定測試釘)。
   260	  1.859  Projects/精簡版update指令_計劃.md  [提交]
   261	    63 [body]: 2. `t_slim_update_behavior`:產物以假 HOME 執行——①無 `~/.lumos-slim`→rc2+指路訊息;②fixture 造本地 git 源+c…
   262	  1.665  Projects/Android側UI測試綁圖譜工作流_實作計畫.md  [推導]
   263	    228 [body]: （★不要寫 `"multiplatform": true`★——那是回傳的推導結果、程式從不讀；★maestro 的 `root` 不能是 `.`★——會讓 doctor 掃整個 …
   264	  1.623  Projects/檢索優化_計劃.md  [進度]
   265	    337 [body]: ## 實作進度
   266	  1.621  Projects/decision_refs自動養成_實作計畫.md  [進度]
   267	    58 [body]: > **進度（2026-07-15）**：P ✅ + T1 ✅（[[Verification/2026-07-15_decision_refs養成_P前置_T1回寫]]）+ cod…
   268	  1.387  Projects/收斂閘漏項敏感度v2_計劃.md  [推導]
   269	    229 [body]: - **日報那句「宣稱 vs 實作沒有機械比對」是錯的**:`t_docs_command_count`(`scripts/test_lumos.py:17258`)與 `t_do…
   270	  1.274  Systems/測試假綠形態.md  [提交]
   271	    168 [body]: **發生什麼**:我把十處「條件不成立就印一條綠然後結束」改成走正式的跳過通道,順手加了一條守衛「跑完卻一條斷言都沒有就判紅」。然後我在提交訊息裡寫:**「全套 3841 綠、零命…
   272	  1.245  Projects/Android側UI測試綁圖譜工作流_計劃.md  [推導]
   273	    287 [★INVARIANT★]: - **r2（2026-08-11，delta 輪 2 席：sonnet 新宣稱正確性／opus 折入一致性與整合；canary 1 caught 1 missed）**：★這輪抓…
   274	  0.000  Projects/pitfalls-lint-integration_計劃.md  []
   275	    29 [fm:context]: context: 使用者三連問(偏科有 linter?其他平台?通則也有?)推導出——規則庫社群已維護且更新更快、更準(AST 級)、免腐化
   276	  0.000  Systems/check-r-guard.md  []
   277	    36 [fm]: - content: 組件 8(graph-discipline.md)+9(SKILL.md)+10(t_marker_doc_sync tuple 加 "[guard:")須同…
   278	  0.000  Systems/design-loop.md  []
   279	    76 [fm:why_chosen]: why_chosen: 由 N 機械推導 a→b→c→d→a 輪替,免狀態、可從 loop_status 輪歷史重現;canary 校準鐵則=「認真審抓得到但不一眼看穿」(太細不公…
   280	  0.000  Verification/2026-07-15_主網M3_cascade帳本.md  []
   281	    10 [fm]: - "行帶 event 判別欄;折疊只折 transition、同粒度鍵取物理序最後一筆;torn 行跳過(=未提交)"
   282	  0.000  Verification/2026-07-22_prepush範圍修法落地.md  []
   283	    9 [fm]: - "動 scripts/hooks/pre-push 的 stdin/範圍推導/逐 ref 迴圈"
   284	
   285	(共 66 篇候選,照相關性排序;想照檔名排加 --legacy)
   286	
   287	codex
   288	`lumos` 已命中真正計劃節點。接著我會按專案的唯讀審計路徑讀完整節點與審材，並用程式碼與帳本格式反查每項理由，不把計劃摘要當成證據終點。
   289	exec
   290	/bin/zsh -lc "sed -n '1,260p' /Users/enzo/.agents/skills/lumos-project-notes/SKILL.md" in /Users/enzo/harness/lumos-toolchain
   291	 succeeded in 0ms:
   292	---
   293	name: lumos-project-notes
   294	description: 專案知識圖譜(docs/{project}-knowledge/)的進場與讀寫——任何任務開始要搞懂「這個模組/欄位/流程為什麼這樣、邊界在哪、哪些不能改、會波及什麼」時先用 lumos 查,不要直接 grep/Read;改完 code 要寫回決策/驗證/合約;收工體檢。觸發:正要 grep 或讀 code 去理解既有系統、排查、對外支援、查 DB、改名/刪除東西、開工掌握現況、收工寫回、問「圖譜有沒有記」。指令全集按情境分類在 commands/INDEX.md。
   295	---
   296	# lumos 專案知識圖譜——一頁手冊
   297	
   298	圖譜記「為什麼、邊界、不能改的、驗過沒」;code 只記「現在長怎樣」。圖譜跟行為事實(測試、實際執行、生產觀測)對不上時,不自動信圖譜——查清哪邊錯,立一篇事故筆記。主工具 `lumos`(python3 零依賴,自動找 `docs/*-knowledge/`)。**別用 Grep/Read/Edit/Write 直接碰圖譜的 .md 開頭欄位**——會繞過自驗和防護;正文段落用 Edit 可以。
   299	
   300	**指令怎麼找**:`commands/INDEX.md`(本目錄,4k)——先看「grep 衝動對照表」,再按你正在做的事開九個子檔之一。下面只列每個階段最常用的。
   301	
   302	## 1. 進場(每個子任務都重來,不是 session 開頭一次)
   303	
   304	| 你在想… | 敲 |
   305	|---|---|
   306	| 這件事為什麼這樣 / 圖譜記了嗎 | `lumos search <詞>` → `lumos context <節點>`;0 命中先換同義詞;**中文概念之間加空白**(`作廢 收回 點數`,別黏成一句) |
   307	| 動這段有什麼不能碰 | `lumos contracts <節點>` |
   308	| 要讀全文再下結論 | `lumos show <節點>`(search 只給索引行;拿摘要判「沒記」以前真的錯過——值在筆記第 64 行,靠摘要判成沒有) |
   309	| 篩條件(金流 / 未收案 / 連到 X) | `lumos query --tag 家族/值 [--active] [--linked <節點>]` |
   310	| 開工掌握現況 | `lumos query --tag status/doing`;`lumos recent --days 7` |
   311	| 圖譜空或稀疏(接手 brownfield) | 走節點還原 SOP:`commands/09-節點還原.md`(七步;需要才產節點、有就照慣例用) |
   312	
   313	看到筆記有 `core_refs:` 或 `CORE:` → 權威在跨專案核心圖譜,改那邊(`lumos-core-knowledge` skill)。
   314	**查得到才算先行**(Landmark 實測):0 筆看「逐詞覆蓋」標 ★ 的詞換同義詞,換三次再問人,別轉 grep;大節點先 `--brief`;單篇內部新舊打架時摘要有日期的 KEY 行 > 正文,衝突影響決策去 code 裁再回頭修。
   315	**分清你在哪種 session**:本機 Claude Code(含手機/網頁遙控本機)有本機 git 憑證、能 push;網頁版 claude.ai/code 是雲端沙盒,對主分支沒 push 權、只能推 feature branch——「遙控」不等於「遠端版」,曾騙到 AI 一次。
   316	被催「直接改、不用解釋」也一樣:不解釋可以,不查不行——改 code 前至少 `lumos impact --file <檔>` 一行。
   317	
   318	## 2. 動手前
   319	
   320	- `lumos impact --file <檔>` / `--diff <範圍>`:哪些筆記、驗證、決策會受影響(Edit 前 hook 也會塞一份,但只推你碰到的檔)。
   321	- `lumos pitfalls --diff <範圍>`:風險分級;`tier: high` 要過代碼審(`lumos-code-loop`)。
   322	- 要刪 / 改名東西:`lumos search <舊名> --code` 逐句判哪些筆記還在講它。
   323	- 改了環境 / 流程 / 設定(版本、金鑰、hook、排程):`lumos stale --candidate --match <關鍵字>` 列出寫了「改到這個就該重驗」的驗證紀錄。
   324	- 設計、spec、計劃一律寫成 `Projects/<主題>_計劃` 筆記(`type: project`),不寫到別的路徑;動筆前一行 `PRIOR-ART:`(最小解在哪層 / 世界解過沒 / 借用‧自建‧採用)。
   325	
   326	## 3. 寫回(同一次工作內;pre-commit 擋「改 code 沒動圖譜」)
   327	
   328	| 要做 | 敲 |
   329	|---|---|
   330	| 新筆記 | `lumos new <system\|issue\|verification\|project> <名>`;驗證紀錄加 `--plan <計劃> --systems <節點>` 自動雙向連 |
   331	| 改狀態 / 日期 | `lumos set <節點> <欄位> <值>`(日期不加引號) |
   332	| 加 / 刪清單項 | `lumos append <節點> <欄位> "[[x]]"` / `lumos remove …` |
   333	| 記決策 / 翻案 | `lumos decision-add <節點> "<內容>" --decided <日期>` / `lumos decision-supersede` |
   334	| 正文段落 | Edit;寫完 `lumos lint <節點>` |
   335	
   336	**四條血換的開頭欄位鐵則**:① 多個連結一行一項,擠成一串會長假筆記 ② `summary: |` 區塊裡的 `[[連結]]` 不算連結,要關聯另放 list 欄位 ③ 值含「冒號+空格」要引號或區塊 ④ 同層不能重複鍵。用指令寫天生避開;手改才會踩。
   337	
   338	**合約標記(動筆前掃一眼;不確定就不標,嚴禁看 code 反推)**:
   339	```
   340	KEY:★INVARIANT★ <業務合約,改=破壞性> [test:測試名] [audit:模型/日期] [kill:recipes]
   341	KEY:★DEBT★ <偶然行為,可改>
   342	KEY:★IRREVERSIBLE★ <做了回不去> [rollback:decisions]     KEY:★CHECKPOINT★ <改了難救>(建議補 [rollback:])
   343	```
   344	- 綁測試 / 留審計走指令:`lumos guard bind <節點> "<KEY 片段>" <測試名>`、`lumos guard audit …`;裸合約 doctor 擋,未審計 pre-push 擋。綁之前對照 [[Systems/測試假綠形態]](最隱蔽的一型:現場根本走不到被測分支;修 bug 的翻紅測試要配一條「現場成立」的前置斷言)。
   345	- 外部不可逆(信已寄、下游已吃)用 `[guard:decisions]` 寫怎麼防重複。`[test:]` 只證程式對,「規則還符不符合業務」要人確認:`lumos signoff`。
   346	- 從 code 重建的筆記先 `lumos set <節點> regen from-scratch/<日期>`,每條主張標 `[src:]`/`[git:]`/`推測:`/`佚失:`;佚失就寫佚失,嚴禁編。
   347	
   348	**摘要區塊**(Systems/Issues 必有):`FLOW:`流程 `KEY:`關鍵概念 `DEP:`依賴 `TEST:`測試;Issues 用 `FLAG:`(只收 TECHNICAL/DECISION/ORIGIN) `DECISION:` `KEY:`。已結案的 Issue 正文第一段要有結案橫幅(status 在開頭欄位,`show --body-only` 看不到,讀者會把修好的當現況)。
   349	**標籤**:`type/` `status/`(值域 lint 硬擋)、`priority/` P0–P3、`scope/`(feature/ area/ 已停用)、`risk/` 金流‧對外送出‧不可逆‧守衛面、`flag/`。
   350	
   351	**決策與驗證**:重大決策填四欄(context / alternatives≥2 / why_chosen / trade_offs),缺資訊問人不編。驗證紀錄填 `valid_under`(前提)與 `revalidate_when`(何時重驗),用 `plan_refs` 指回計劃;漏掛 `lumos sync-verified-by --apply`。計劃結案前 `lumos spec-trace <計劃>` 看哪些條款沒人認領。
   352	
   353	**承認風險的鐵則**(Enzo 2026-08-22 裁):筆記或訊息裡寫「沒機械守衛 / 只提醒不擋 / 單次量測 / 這數字是拍的」這類承認句,**旁邊必須有「什麼時候回頭看」**(週報、重驗條件、revalidate_when、到期日);寫不出重驗條件的,就是該處理不該承認。**回頭條件要接電**(2026-08-31 回訪案):帶日期的寫成獨立一行 `REVISIT:YYYY-MM-DD 一句要做什麼`(緊鄰原句,doctor 到期會唸、逾 14 天沒人動升級週報);綁事件的明寫事件入口——純散文=52 件盤點實證的死文。
   354	
   355	## 4. 收工
   356	
   357	1. `lumos lint <每篇動過的>` → `lumos doctor`(紅的段先修;`--verbose` 看全部提醒)。
   358	2. code 有「拿掉 / 反轉」的改動:把那些名字逐個 `lumos search <名> --code`,逐句判筆記還成不成立,不成立當場改或標作廢。動到畫面 → 補可重放的 UI flow 並 `[test:<平台>:<flow>]` 綁回(沒裝置要明寫「未驗+原因」)。
   359	3. 圖譜實質更新後:派乾淨 agent 只讀圖譜還原脈絡,對不上就補到一致,留痕 `lumos self-audit <節點>`。
   360	4. push 後(專案有宣告 ci 區塊才有):`lumos ci-wait`,紅就當輪修,修不完要在收尾明講。
   361	5. 跨 session 傳訊只傳「指標+觸發」(我動了哪篇、你去讀哪篇),不傳內容本身;規則權威在圖譜不在誰的記憶。
   362	
   363	## 再深一層(按需開,別一次全讀)
   364	
   365	| 要做 | 開 |
   366	|---|---|
   367	| 某個指令的旗標與用法 | `commands/0N-*.md`(INDEX 指到)或 `lumos <cmd> --help` |
   368	| 合約鏈深規、[audit:] 五問、guard 工作流、防帶風向 | `reference.md`〈★INVARIANT★ → `[audit:]` 獨立合法性審計〉〈★INVARIANT★ → `[test:]` 綁定〉〈`lumos guard`〉 |
   369	| 決策四欄完整版、驗證紀錄完整規格、同步規則 | `reference.md`〈Properties〉〈同步規則〉 |
   370	| 開頭欄位鐵則、標籤家族、摘要區塊、結案橫幅、退場自問、跨 session 傳訊、CI 細則全文 | `reference.md`〈寫入規範與紀律全文〉 |
   371	| 自足性審計 prompt、交叉審計變體 | `reference.md`〈圖譜更新後：Sonnet agent 自足性審計〉〈變體 B：圖譜×程式碼交叉審計〉 |
   372	| maestro UI flow 派工要求 | `reference.md`〈產 maestro UI flow 的派工要求〉 |
   373	| 資料夾位置 | `docs/{slug}-knowledge/{Projects,Systems,Issues,Verification,MOC}`;某主題 >5 篇建 MOC |
   374	
   375	exec
   376	/bin/zsh -lc 'python3 scripts/lumos context Projects/進度從提交推導_計劃.md --brief && python3 scripts/lumos show Projects/進度從提交推導_計劃.md' in /Users/enzo/harness/lumos-toolchain
   377	 succeeded in 450ms:
   378	# Projects/進度從提交推導_計劃.md
   379	type:project | status:doing | created:2026-09-07 | updated:2026-09-07
   380	summary:
   381	  FLAG:TECHNICAL
   382	  KEY:立案(2026-09-07,Enzo 裁「首要工作=讓做到哪一步也能同步並且可信」後再切一刀)——★本案不是做進度追蹤器,是讓「完成」那個動作自己留下紀錄★
   383	→ 連出 (5):
   384	  • Issues/同工作區多session並行改動.md [open]
   385	  • Projects/全repo審視_計劃.md [doing]
   386	  • Projects/執行DAG_調研.md [doing]
   387	  • Projects/驗形式與驗內容_調研.md [doing]
   388	  • Systems/loop-convergence-recording.md [done]
   389	← 連入 (0):
   390	---
   391	type: project
   392	status: doing
   393	created: 2026-09-07
   394	updated: 2026-09-07
   395	tags:
   396	  - type/project
   397	  - status/doing
   398	related:
   399	  - "[[Projects/執行DAG_調研]]"
   400	  - "[[Projects/驗形式與驗內容_調研]]"
   401	  - "[[Systems/loop-convergence-recording]]"
   402	  - "[[Issues/同工作區多session並行改動]]"
   403	  - "[[Projects/全repo審視_計劃]]"
   404	summary: |-
   405	  FLAG:TECHNICAL
   406	  KEY:立案(2026-09-07,Enzo 裁「首要工作=讓做到哪一步也能同步並且可信」後再切一刀)——★本案不是做進度追蹤器,是讓「完成」那個動作自己留下紀錄★
   407	  KEY:★根因:完成與記錄是兩件事★——審查迴圈準,是因為「完成一輪」與「記下一輪」是**同一個動作**(那筆帳就是工作成果,不可能做了沒記/記了沒做);實作歪,是因為成果是程式碼、記錄是另外去勾框,兩件事分開就一定漂
   408	  KEY:★症狀數字(2026-09-07 當場量)★:Projects 標進行中 43 篇其中 17 篇 >30 天沒動;一篇 status=done 的實作計畫 60 個框 0 個勾(12 任務×5 步驟,全是實作步驟)、另一篇 39 個框全勾——★並列才是重點:同 repo 同格式,有人維護有人不維護,而沒有任何東西會知道差別★;50 群主清單無「做完沒」欄、進度靠翻提交訊息回推;近 120 筆提交帶編號的只有 6 筆(且全集中在那份有編號的清單上)
   409	  KEY:★因果鏈沒有分叉,斷點在最前面★——工作項沒有在筆記之外還活著的識別碼 → 提交掛不上 → 沒有可追加的紀錄 → 完成狀態只能手寫 → 一定漂
   410	  KEY:★PRIOR-ART 最強的一條:不用發明格式★——git 原生有 trailer,`git log --format='%(trailers:key=X,valueonly=true)'` 一個旗標查得出;**本 repo 每筆提交已經在產 trailer**(近 30 筆 100% 帶 Co-Authored-By/Claude-Session),所以是加一個鍵不是加一套機制。讀取端★用 git 原生解析、不自己寫正則撈提交訊息★(自己撈=又一個「形式對內容不一定對」的地方)
   411	  KEY:設計三步(各可獨立交付)=[S1] 工作項取名(只定慣例不寫程式)/[S2] 完成的提交掛 `Task: <識別碼>` trailer/[S3] 唯讀查詢從 git 算進度,★不寫回筆記★(寫回去就又變成會漂的手寫狀態),樣板照 `loop verify-progress`「只讀結構不讀散文」
   412	  KEY:★範圍刀★不建第二張圖/不建任務狀態檔(執行DAG_調研已裁:手維護狀態檔正是本案要消滅的)/不做認領租約多agent派工/不碰審查迴圈那條線(已會動,動它只有下跌空間)/不做跨任務依賴(依賴建立在「完成」之上,本案是它的前置)/不自動改筆記 status 欄
   413	  KEY:★誠實天花板:最多蓋到四分之三★——74 個任務段裡 56 個(75%)抽得出對應測試名,剩 18 個天生沒有(改 skill 散文/圖譜回填/真機驗收);那類沒有提交可掛或掛了也證明不了,★本案對它們無效、不假裝有效,輸出要明說「這類算不出來」★
   414	  KEY:★待裁四題★①識別碼從哪來(沿用 50 群的 #N / 每份計劃 T1..Tn 會撞名 / 計劃名+任務號)②trailer 鍵名(避開既有與世界慣例語意衝突)③「完成」定義=有提交掛過就算,還是要加「綁的測試綠」——★後者看似更嚴但外家 f2 已證明「測試綠≠任務完成」(多任務共用一個測試/只寫跑全套/既有測試開工前就綠),加了不一定更準可能只是更貴★ ④先唯讀查詢還是一開始就讓 pre-commit 提醒
   415	  KEY:驗收線=不讀勾選框就答得出每個工作項有沒有被提交掛過與最後一次何時;對那 18 個算不出來的**明說算不出來**;三步各有測試且 ★fixture 用真的呼叫 git 產生不手刻★(2026-09-07 教訓:手刻 fixture 導致 code-loop 那半是死碼)
   416	decisions:
   417	  - content: 用 git trailer 承載工作項識別碼,不自建格式、不建任務狀態檔
   418	    id: d1
   419	    context: 要讓「完成」自己留下紀錄,需要一個機器可讀的欄位把提交跟工作項綁起來。選項:自訂提交訊息格式再寫正則撈、開一份任務狀態檔、或用 git 原生 trailer
   420	    why_chosen: git trailer 是原生標準,`git log --format='%(trailers:key=X,valueonly=true)'` 一個旗標就查得出,不必自寫解析(自寫正則撈提交訊息=又一個「形式對、內容不一定對」的地方);而且本 repo 每筆提交已經在產 trailer(近 30 筆 100% 帶 Co-Authored-By/Claude-Session),是加一個鍵不是加一套機制。任務狀態檔已於 執行DAG_調研 裁掉:手維護的狀態正是本案要消滅的東西。代價:綁死 git(非 git 專案不適用);trailer 要靠寫提交的人記得加,沒有機械守衛前一樣會漏
   421	    decided: 2026-09-07
   422	    valid: true
   423	  - content: 本案明說只蓋四分之三:沒有程式碼可掛的工作(skill 散文/圖譜回填/真機驗收)不假裝算得出來
   424	    id: d2
   425	    context: 先前量到 74 個任務段裡 56 個(75%)抽得出對應測試名,剩 18 個天生沒有——那類沒有提交可掛,或掛了也證明不了什麼
   426	    why_chosen: 家規要求承認風險要附回頭條件、寫不出判準就明說靠人;而把算不出來的東西輸出成「未完成」或靜默略過,都會讓使用者以為算過了——那正是本 repo 反覆抓到的假綠形態。代價:這個工具永遠有一塊盲區,不能宣稱『進度全自動』
   427	    decided: 2026-09-07
   428	    valid: true
   429	  - content: 完成判準掛實作端、看測試:功能級測試套綠 + 相依功能無回歸;明確不做散文級判準
   430	    id: d3
   431	    context: Enzo 裁。原本待裁三選項:有提交掛過就算完成 / 加上綁的測試綠 / 散文級判斷。外家 f2 曾證明「測試綠≠任務完成」(多任務共用一個測試、有的只寫跑全套、既有測試開工前就綠)
   432	    why_chosen: ★f2 打的是任務級,Enzo 裁的是功能級,三條反對在功能級各自失效★:共用測試在功能級就是同一個功能的測試、既有測試已綠對新功能不成立、只寫跑全套在功能級正是「相依無回歸」那一半的定義。所以不是繞過外家,是換到 f2 打不到的粒度。代價:①功能級是二元的,答不出「做到第幾步」,接手需要的解析度要靠任務級測試名另外給(且不得用來宣告完成)②判準的品質等於測試的品質,弱測試=假綠,靠既有翻紅釘紀律頂著③沒有測試可掛的工作型別完全不在射程內
   433	    decided: 2026-09-07
   434	    valid: true
   435	  - content: 識別碼沿用既有 [SN] 條款標記,定址比照決策寫成 <計劃節點rel>#S1
   436	    id: d4
   437	    context: 三選項:沿用 50 群那套 #N(只存在於那一份清單)、每份計劃自己給 T1..Tn(跨計劃撞名)、計劃節點名+任務號
   438	    why_chosen: 不發明新方案:①[SN] 標記是既有慣例且已有消費者(spec-trace 用它看哪些條款沒被驗證認領)②定址形狀已有前例(決策是 <節點rel>#dN,程式裡有格式驗證與 dangling 偵測,可照抄)③識別碼從計劃節點自己長出來,不必維護第二份登記簿。代價:計劃節點改名會讓舊 trailer 指不到——但決策定址有同一個問題,不是本案新引入的風險
   439	    decided: 2026-09-07
   440	    valid: true
   441	  - content: trailer 鍵名用 Lumos-Task:
   442	    id: d5
   443	    context: "候選 Task: / Refs: / Lumos-Task:;本 repo 現有 trailer 是 Co-Authored-By 與 Claude-Session"
   444	    why_chosen: "比照既有的 Claude-Session: 命名空間形態;Refs:/Fixes:/Closes: 在 git 生態各有既定語意、借用製造歧義;Task: 太泛將來可能撞別的工具。代價:字長,但由提交模板產生、人不必自己打(Co-Authored-By 就是這樣運作)"
   445	    decided: 2026-09-07
   446	    valid: true
   447	  - content: 「綠」的來源用 CI 那筆,不用 code-loop pass
   448	    id: d6
   449	    context: 兩個候選都按版本記:governance/code-loop/main.json 的 {head_sha,status} 與 lumos ci-status 的 {sha,conclusion}
   450	    why_chosen: ★code-loop pass 記的是「審查過了」不是「測試綠了」,狀態值裡還有 skipped——拿它當測試結果就是借一個紀錄表達它沒有的意思,正是本 repo 今天抓了一整天的病★;CI 那筆語意就是對的(實查 JSON 帶 sha 與 conclusion,本地讀不打網路)。代價不小:CI 只在推送後跑,本機未推的工作查不到,所以必須把「還沒推=未知」與「未完成」分開輸出——混在一起就是新的假綠
   451	    decided: 2026-09-07
   452	    valid: true
   453	---
   454	# 進度從提交推導_計劃
   455	
   456	> 白話:現在「這件事做到哪一步」是人手寫在筆記裡的,所以會漂——有一篇計劃狀態寫「做完了」,
   457	> 裡面 60 個勾選框一個都沒勾。本案要把它換成**算出來的**:每個工作項給一個名字,
   458	> 完成它的那個提交把名字掛上去,進度就從 git 算,沒有東西需要人維護。
   459	
   460	> **本篇用到的三個詞**:「外家」=不是編排者那一家的審查席(本 repo 慣例上是 Codex);「f2」=某輪外家報告的第 2 條發現(此處指 [[Projects/執行DAG_調研]] 那輪);「編排者」=負責派審查員、判讀報告、折入修正的那個角色(本案是主對話的 AI);「群」=[[Projects/全repo審視_計劃]] 把 130 條發現去重合併後、可獨立交付的分組。
   461	
   462	PRIOR-ART:①★最小解在既有機制層,而且不用發明格式★——**git 原生就有 trailer**(提交訊息尾端的 `鍵: 值` 欄位),`git log --format='%(trailers:key=X,valueonly=true)'` 一個旗標就查得出來;**本 repo 每一筆提交已經在產 trailer**(近 30 筆 100% 帶 `Co-Authored-By`/`Claude-Session`),所以是加一個鍵,不是加一套新機制。②本家已有可抄的樣板=審查迴圈那條線(`loop verify-progress` 的 help 逐字:「不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)。」)。③世界解:GitHub 的 `Closes #N` 是同型但綁在 forge 上;beads / Task Master 那類已於 [[Projects/執行DAG_調研]] d1 裁定「可借形狀、不借實作」(零依賴家規)。④不採用新依賴:全案只用 git 與 python3 stdlib。
   463	
   464	## 問題(有症狀、有數字、有消費者)
   465	
   466	**症狀**:任何一個 session 都答不出「這件實作做到哪一步了」。
   467	
   468	**當場量到的數字(2026-09-07)**:
   469	
   470	| 量到什麼 | 數字 |
   471	|---|---|
   472	| Projects 標「進行中」 vs 超過 30 天沒動 | **46 篇 / 其中 17 篇**(★快照 2026-09-07 傍晚;原稿寫 43 是當天稍早的量測,差的 3 篇是同日新增、含本篇自己★。「17 篇」前掃機械重算吻合) |
   473	| 一篇 `status: done` 的實作計畫,裡面的勾選框 | **60 個框,0 個打勾**(12 任務 × 5 步驟,全是實作步驟不是驗收清單) |
   474	| 另一篇實作計畫的勾選框 | **39 個框,全部打勾** |
   475	| [[Projects/全repo審視_計劃]] 的 50 群主清單 | **沒有「做完沒」這一欄**;進度靠翻提交訊息回推 |
   476	| 近 120 筆提交帶項目編號的 | **6 筆**(而且全部集中在那份有編號的主清單上) |
   477	
   478	★第二、三列並列才是重點★:同一個 repo、同一種格式,**有人維護有人不維護,而沒有任何東西會知道差別**。
   479	
   480	**消費者**:①接手的 session(現在只能讀散文猜)②Enzo 本人(問「做到哪」要人回答)③無人自跑的迴圈(未來)。
   481	
   482	## 根因:完成與記錄是兩件事
   483	
   484	- **審查迴圈為什麼準**:★「完成一輪」和「記下一輪」是**同一個動作**★——那筆帳本身就是工作成果。不可能做了沒記,也不可能記了沒做。
   485	- **實作為什麼歪**:工作成果是程式碼,記錄是另外去勾一個框。**兩件事分開就一定會漂**;那 60 個沒勾的框就是這樣來的。
   486	
   487	**所以本案不是「做一個進度追蹤器」,是「讓完成那個動作自己留下紀錄」。**
   488	
   489	## 設計(三步,每步可獨立交付)
   490	
   491	### [S1] 工作項要有一個在筆記之外還活著的名字
   492	
   493	- 現況:審查迴圈有(編號＋第幾輪)、50 群主清單有(`#N`),**其餘實作工作沒有任何識別碼**。
   494	- 沒有名字 → 提交掛不上 → 沒有可追加的紀錄 → 完成狀態只能手寫 → 一定漂。**這條因果鏈沒有分叉,斷點在最前面。**
   495	- 本步只定慣例與格式,不寫程式。
   496	
   497	### [S2] 完成的動作把名字掛上去(用 git trailer,不發明格式)
   498	
   499	- 提交訊息尾端加一行 `Task: <識別碼>`(鍵名待裁,見開放問題)。
   500	- 讀取端:`git log --format='%(trailers:key=Task,valueonly=true)'`——★git 原生解析,不自己寫正則去撈提交訊息★(自己撈=又一個「形式對、內容不一定對」的地方)。
   501	
   502	### [S3] 進度用算的,不給人維護
   503	
   504	- 新增唯讀查詢:某個計劃的每個工作項,有沒有提交掛過它、最後一次是什麼時候、動了哪些檔。
   505	- ★狀態不寫回筆記★——寫回去就又變成一份會漂的手寫狀態。要看就當場算。
   506	- 樣板照 `loop verify-progress`:它的 help 逐字寫「不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)。」
   507	
   508	## 範圍刀(明確不做)
   509	
   510	- **不建第二張圖、不建任務狀態檔**——[[Projects/執行DAG_調研]] 已裁:手維護的狀態檔正是本案要消滅的東西。
   511	- **不做認領/租約/多 agent 派工**——同上,現在買不到什麼。
   512	- **不碰審查迴圈那條線**——它已經會動,動它只有下跌空間。
   513	- **不做跨任務依賴(A 卡 B)**——依賴建立在「完成」之上;完成先可信,依賴才有意義。本案是它的前置,不是它。
   514	- **不自動改筆記的 `status` 欄**——本案只提供查詢。
   515	
   516	## ★誠實天花板:這條路最多蓋到四分之三★
   517	
   518	- 先前量過:74 個任務段裡 **56 個(75%)** 抽得出對應的測試函式名;**剩下 18 個是天生沒有**——改 skill 散文、圖譜回填、真機驗收這類。
   519	- **那一類沒有提交可掛,或掛了也證明不了什麼。** 本案對它們**無效**,不假裝有效。
   520	- ★但「25% 全部無解」講太滿(2026-09-07 自查)★:其中一部分**有非散文的訊號**可用——真機驗收有 maestro 測試(既有合約行就綁著 `maestro:smoke_05_manual_discount_over_100` 這種)、圖譜回填有 `lumos doctor` 與 `spec-trace` 可判。**真正無解的是改 skill 散文那一類。** 實際比例沒量過,★要裁射程前應先把 18 個逐一分類★。
   521	- ★不寫「之後再想辦法」——寫不出判準就明說這一段靠人★,並在輸出裡標成「這類算不出來」,不要讓使用者以為算過了。
   522	
   523	## ★第一版裁決(2026-09-07,Enzo 委任編排者裁;送設計審前的 v1)★
   524	
   525	三題全裁,兩題直接借既有前例、一題否掉一個看似方便的選項:
   526	
   527	### [D1] 識別碼 = 沿用既有的 `[SN]` 條款標記,定址寫成 `<計劃節點rel>#S1`
   528	
   529	★不發明新方案★,三個現成理由:
   530	- **標記已經有**:計劃裡寫 `[S1]`/`[S2]` 是既有慣例,而且**已經有消費者**——`spec-trace` 的用途就是「計劃結案前看哪些條款沒有驗證紀錄認領」。
   531	- **定址形狀已經有**:決策的定址是 `<節點rel>#dN`(程式裡有格式驗證與 dangling 偵測)。`#S1` 完全比照,連驗證邏輯都可以照抄。
   532	- **不必維護登記簿**:識別碼從計劃節點自己長出來,沒有第二份要同步的東西。
   533	
   534	**代價(明寫)**:計劃節點改名會讓舊 trailer 指不到——★但決策定址有同一個問題,所以這不是本案引入的新風險,是沿用既有取捨★。
   535	
   536	### [D2] trailer 鍵名 = `Lumos-Task:`
   537	
   538	- **比照本 repo 既有形態**:現在每筆提交都帶 `Claude-Session:`,同樣是「命名空間-用途」的連字號形式。
   539	- **避開世界慣例的語意**:`Refs:`/`Fixes:`/`Closes:` 在 git 生態各有既定意思,借用會製造歧義;`Task:` 太泛,將來可能撞別的工具。
   540	- **代價**:字長。~~但它由提交模板產生,人不必自己打~~ → ★**前掃 ④-11 推翻(而且這條最痛)**★:實查 `git config commit.template` 指向的檔案是**空的**——`Co-Authored-By`/`Claude-Session` 真正的產生方式是**AI 每次提交時照 session 指示手動打進去**,★不是 git 機制自動代入,沒有任何機械強制力★。
   541	  所以正確的代價是:**字長,而且要靠寫提交的人記得加**。
   542	  ★這帶出一個設計級的問題,交給席位判,前掃不自行裁★:本案整個 [S2] 都建立在「提交會掛 trailer」上,而那一步**目前是純自律**——這跟本案自己主張的「讓完成自己留下紀錄、不靠人維護」精神有落差。**沒有守衛的 trailer,漏掉的那些工作項會長期顯示成『沒人做過』,而那正是本案要消滅的假狀態。**
   543	
   544	### [D3] 「綠」的來源 = **CI 那筆,不用 code-loop pass**
   545	
   546	★這題我否掉看似方便的那個選項★:
   547	
   548	- `code-loop pass` 記的是**「審查過了」**,不是「測試綠了」;而且它的狀態值裡有 `skipped`。**拿它當測試結果,就是借一個紀錄去表達它沒有的意思**——那正是本 repo 今天一整天在抓的病(「形式對、內容不成立」)。
   549	- CI 那筆的語意就是對的。實查其 JSON:`{"sha": "9854ba5…", "conclusion": "success", "run_id": …, "branch": "main", "workflow": "CI"}`——★按版本記、帶結論、本地讀不打網路★(`lumos ci-status`)。
   550	- **代價(明寫,而且不小)**:CI 只在推送後跑,**本機還沒推的工作查不到**。所以要接受一個語意:★「還沒推」= **未知**,不是「未完成」★——輸出必須分得出這兩者,混在一起就是新的假綠。
   551	
   552	## 待裁的開放問題(留給設計審)
   553	
   554	3. ~~**「完成」怎麼定義**~~ → ★**已裁(2026-09-07 Enzo)**:完成判準掛在**實作端**,看**測試有沒有過**;判的是「整個功能有沒有完成」+「相依功能有沒有回歸」。**明確不做散文級判準。**★
   555	
   556	   **★這個切法躲開了外家 f2 的反對,而且是有理由的躲開,不是繞過★**:f2 打的是**任務級**「測試綠=任務完成」——Task 1–5 全部往同一個 `t_delguard()` 裡續加斷言,那個測試綠分不出誰做完了。
   557	   但 Enzo 裁的是**功能級**:①功能級「這個功能的測試套綠」不受共用測試影響(共用的正是同一個功能的測試) ②「既有測試開工前就綠」對**新功能**不成立(它的測試本來不存在) ③「有的任務只寫跑全套」在功能級不是缺陷,**那就是「相依功能沒回歸」這一半的定義**。
   558	   ★三條反對在功能級各自失效——所以這不是無視外家,是換了一個 f2 打不到的粒度。★
   559	- **要不要擋**:先做唯讀查詢,還是一開始就讓 pre-commit 提醒「這批改動沒掛任何工作項」?★編排者傾向先唯讀★(理由:本案的價值還沒有本地證據,先擋會逼出湊數的 trailer=製造假資料),但沒有量過,留給審。
   560	- ★**原稿寫「`[SN]` 目前實際沒人寫」——不屬實,前掃逐篇實跑推翻(④-4)**★:全 repo 158 篇計劃逐篇跑 `spec-trace`,**32 篇真的寫了 `[SN]`,其中 13 篇被真實的 Verification 完整認領(rc=0)**,另 19 篇部分未認領;126 篇未啟用。
   561	  ★這條反而強化 D1★:不是「慣例存在但沒人用」,是**已經在用、而且已經有 13 篇完整跑通**——沿用它的成本比原稿估的更低。
   562	  (原稿那句還跟本文自己「spec-trace 已經有消費者」直接打架,同一份文件內互相矛盾,已改。)
   563	- 仍待審的是**覆蓋率**:126/158 沒寫。要不要同時處理「怎麼讓人真的寫」,是設計審該打的點。
   564	- **那 18 個「沒有測試可掛」的任務段還沒逐一分類**(先前只知道總數);射程要收在哪,得先分類。
   565	
   566	## ★裁定之後浮出來的兩個新問題(Enzo 裁完才看得到)★
   567	
   568	### 甲、功能級是二元的,但「接手」需要更細
   569	
   570	本案的來源需求是「agent 做到一半,任何 session 接得下去」。
   571	
   572	- **功能級判準只答得出「完成 / 沒完成」。** 一個功能拆 12 個任務、agent 停在第 7 個 → 功能測試是紅的 → 你只知道「沒完成」,**不知道「做到第 7 個」**。★那正好是接手最需要的那一格。★
   573	- **但不必換判準就能補**:先前量過,74 個任務段裡 **56 個(75%)** 自己就寫了對應的測試函式名。所以**同一個判準可以有兩種解析度**:
   574	  - **功能級**(是否完成)= 該功能的測試套 + 全套回歸 → **這是 Enzo 裁的那個,是「完成」的權威**。
   575	  - **任務級**(做到哪)= 逐個任務宣告的測試名綠了沒 → **只當接手用的進度指示,不當完成判準**(f2 的反對在這一級仍然成立,所以★不得用它宣告完成★)。
   576	- ★兩級必須語意分明:一個是判定,一個是提示。混用就會把 f2 打過的洞再開一次。★
   577	
   578	### 乙、「綠」是**什麼時候**的綠
   579	
   580	- 若指「現在跑一次是綠的」→ 每次查進度都要跑全套(約 8 分鐘),**查不起**。
   581	- 若指「宣告完成的那個版本上是綠的」→ 要有一筆按版本記的結果。
   582	- ★好消息:這筆紀錄已經存在★——`governance/code-loop/main.json` 就是 `{head_sha, status}` 形態(實查:`head_sha: c103e324…`,`status: passed`);另有 `lumos ci-status`(只讀上次 CI 結果、不打網路)。
   583	- **所以本案不必新建測試結果帳,接既有的即可**。★來源已於 [D3] 裁定=CI 那筆、不用 code-loop pass★(本節原本把它寫成「還沒裁」,是撰寫順序造成的殘留,前掃 ③ 抓到,已改)。
   584	
   585	## 驗收線(這份計劃算不算做成)
   586	
   587	- 能對一份真實的實作計畫,**不讀它的勾選框**,答出每個工作項有沒有被提交掛過、最後一次何時。
   588	- 對那 18 個「天生算不出來」的任務段,**輸出明說算不出來**,不含糊。
   589	- 三步各自有測試;測試 fixture ★用真的呼叫 git 產生,不手刻★(2026-09-07 教訓:手刻 fixture 導致 code-loop 那半是死碼)。
   590	
   591	exec
   592	/bin/zsh -lc "nl -ba governance/review-reports/進度從提交推導/r1-snapshot.md | sed -n '1,240p'
   593	rg -n \"ci-status|ci_status|code-loop|code_loop|head_sha|conclusion|skipped|passed|decision_refs|#d|spec-trace|\\[S[0-9]+\\]\" scripts/lumos scripts/test_lumos.py governance/code-loop .github 2>/dev/null | head -n 300" in /Users/enzo/harness/lumos-toolchain
   594	 succeeded in 0ms:
   595	     1	---
   596	     2	type: project
   597	     3	status: doing
   598	     4	created: 2026-09-07
   599	     5	updated: 2026-09-07
   600	     6	tags:
   601	     7	  - type/project
   602	     8	  - status/doing
   603	     9	related:
   604	    10	  - "[[Projects/執行DAG_調研]]"
   605	    11	  - "[[Projects/驗形式與驗內容_調研]]"
   606	    12	  - "[[Systems/loop-convergence-recording]]"
   607	    13	  - "[[Issues/同工作區多session並行改動]]"
   608	    14	  - "[[Projects/全repo審視_計劃]]"
   609	    15	summary: |-
   610	    16	  FLAG:TECHNICAL
   611	    17	  KEY:立案(2026-09-07,Enzo 裁「首要工作=讓做到哪一步也能同步並且可信」後再切一刀)——★本案不是做進度追蹤器,是讓「完成」那個動作自己留下紀錄★
   612	    18	  KEY:★根因:完成與記錄是兩件事★——審查迴圈準,是因為「完成一輪」與「記下一輪」是**同一個動作**(那筆帳就是工作成果,不可能做了沒記/記了沒做);實作歪,是因為成果是程式碼、記錄是另外去勾框,兩件事分開就一定漂
   613	    19	  KEY:★症狀數字(2026-09-07 當場量)★:Projects 標進行中 43 篇其中 17 篇 >30 天沒動;一篇 status=done 的實作計畫 60 個框 0 個勾(12 任務×5 步驟,全是實作步驟)、另一篇 39 個框全勾——★並列才是重點:同 repo 同格式,有人維護有人不維護,而沒有任何東西會知道差別★;50 群主清單無「做完沒」欄、進度靠翻提交訊息回推;近 120 筆提交帶編號的只有 6 筆(且全集中在那份有編號的清單上)
   614	    20	  KEY:★因果鏈沒有分叉,斷點在最前面★——工作項沒有在筆記之外還活著的識別碼 → 提交掛不上 → 沒有可追加的紀錄 → 完成狀態只能手寫 → 一定漂
   615	    21	  KEY:★PRIOR-ART 最強的一條:不用發明格式★——git 原生有 trailer,`git log --format='%(trailers:key=X,valueonly=true)'` 一個旗標查得出;**本 repo 每筆提交已經在產 trailer**(近 30 筆 100% 帶 Co-Authored-By/Claude-Session),所以是加一個鍵不是加一套機制。讀取端★用 git 原生解析、不自己寫正則撈提交訊息★(自己撈=又一個「形式對內容不一定對」的地方)
   616	    22	  KEY:設計三步(各可獨立交付)=[S1] 工作項取名(只定慣例不寫程式)/[S2] 完成的提交掛 `Task: <識別碼>` trailer/[S3] 唯讀查詢從 git 算進度,★不寫回筆記★(寫回去就又變成會漂的手寫狀態),樣板照 `loop verify-progress`「只讀結構不讀散文」
   617	    23	  KEY:★範圍刀★不建第二張圖/不建任務狀態檔(執行DAG_調研已裁:手維護狀態檔正是本案要消滅的)/不做認領租約多agent派工/不碰審查迴圈那條線(已會動,動它只有下跌空間)/不做跨任務依賴(依賴建立在「完成」之上,本案是它的前置)/不自動改筆記 status 欄
   618	    24	  KEY:★誠實天花板:最多蓋到四分之三★——74 個任務段裡 56 個(75%)抽得出對應測試名,剩 18 個天生沒有(改 skill 散文/圖譜回填/真機驗收);那類沒有提交可掛或掛了也證明不了,★本案對它們無效、不假裝有效,輸出要明說「這類算不出來」★
   619	    25	  KEY:★待裁四題★①識別碼從哪來(沿用 50 群的 #N / 每份計劃 T1..Tn 會撞名 / 計劃名+任務號)②trailer 鍵名(避開既有與世界慣例語意衝突)③「完成」定義=有提交掛過就算,還是要加「綁的測試綠」——★後者看似更嚴但外家 f2 已證明「測試綠≠任務完成」(多任務共用一個測試/只寫跑全套/既有測試開工前就綠),加了不一定更準可能只是更貴★ ④先唯讀查詢還是一開始就讓 pre-commit 提醒
   620	    26	  KEY:驗收線=不讀勾選框就答得出每個工作項有沒有被提交掛過與最後一次何時;對那 18 個算不出來的**明說算不出來**;三步各有測試且 ★fixture 用真的呼叫 git 產生不手刻★(2026-09-07 教訓:手刻 fixture 導致 code-loop 那半是死碼)
   621	    27	decisions:
   622	    28	  - content: 用 git trailer 承載工作項識別碼,不自建格式、不建任務狀態檔
   623	    29	    id: d1
   624	    30	    context: 要讓「完成」自己留下紀錄,需要一個機器可讀的欄位把提交跟工作項綁起來。選項:自訂提交訊息格式再寫正則撈、開一份任務狀態檔、或用 git 原生 trailer
   625	    31	    why_chosen: git trailer 是原生標準,`git log --format='%(trailers:key=X,valueonly=true)'` 一個旗標就查得出,不必自寫解析(自寫正則撈提交訊息=又一個「形式對、內容不一定對」的地方);而且本 repo 每筆提交已經在產 trailer(近 30 筆 100% 帶 Co-Authored-By/Claude-Session),是加一個鍵不是加一套機制。任務狀態檔已於 執行DAG_調研 裁掉:手維護的狀態正是本案要消滅的東西。代價:綁死 git(非 git 專案不適用);trailer 要靠寫提交的人記得加,沒有機械守衛前一樣會漏
   626	    32	    decided: 2026-09-07
   627	    33	    valid: true
   628	    34	  - content: 本案明說只蓋四分之三:沒有程式碼可掛的工作(skill 散文/圖譜回填/真機驗收)不假裝算得出來
   629	    35	    id: d2
   630	    36	    context: 先前量到 74 個任務段裡 56 個(75%)抽得出對應測試名,剩 18 個天生沒有——那類沒有提交可掛,或掛了也證明不了什麼
   631	    37	    why_chosen: 家規要求承認風險要附回頭條件、寫不出判準就明說靠人;而把算不出來的東西輸出成「未完成」或靜默略過,都會讓使用者以為算過了——那正是本 repo 反覆抓到的假綠形態。代價:這個工具永遠有一塊盲區,不能宣稱『進度全自動』
   632	    38	    decided: 2026-09-07
   633	    39	    valid: true
   634	    40	  - content: 完成判準掛實作端、看測試:功能級測試套綠 + 相依功能無回歸;明確不做散文級判準
   635	    41	    id: d3
   636	    42	    context: Enzo 裁。原本待裁三選項:有提交掛過就算完成 / 加上綁的測試綠 / 散文級判斷。外家 f2 曾證明「測試綠≠任務完成」(多任務共用一個測試、有的只寫跑全套、既有測試開工前就綠)
   637	    43	    why_chosen: ★f2 打的是任務級,Enzo 裁的是功能級,三條反對在功能級各自失效★:共用測試在功能級就是同一個功能的測試、既有測試已綠對新功能不成立、只寫跑全套在功能級正是「相依無回歸」那一半的定義。所以不是繞過外家,是換到 f2 打不到的粒度。代價:①功能級是二元的,答不出「做到第幾步」,接手需要的解析度要靠任務級測試名另外給(且不得用來宣告完成)②判準的品質等於測試的品質,弱測試=假綠,靠既有翻紅釘紀律頂著③沒有測試可掛的工作型別完全不在射程內
   638	    44	    decided: 2026-09-07
   639	    45	    valid: true
   640	    46	  - content: 識別碼沿用既有 [SN] 條款標記,定址比照決策寫成 <計劃節點rel>#S1
   641	    47	    id: d4
   642	    48	    context: 三選項:沿用 50 群那套 #N(只存在於那一份清單)、每份計劃自己給 T1..Tn(跨計劃撞名)、計劃節點名+任務號
   643	    49	    why_chosen: 不發明新方案:①[SN] 標記是既有慣例且已有消費者(spec-trace 用它看哪些條款沒被驗證認領)②定址形狀已有前例(決策是 <節點rel>#dN,程式裡有格式驗證與 dangling 偵測,可照抄)③識別碼從計劃節點自己長出來,不必維護第二份登記簿。代價:計劃節點改名會讓舊 trailer 指不到——但決策定址有同一個問題,不是本案新引入的風險
   644	    50	    decided: 2026-09-07
   645	    51	    valid: true
   646	    52	  - content: trailer 鍵名用 Lumos-Task:
   647	    53	    id: d5
   648	    54	    context: "候選 Task: / Refs: / Lumos-Task:;本 repo 現有 trailer 是 Co-Authored-By 與 Claude-Session"
   649	    55	    why_chosen: "比照既有的 Claude-Session: 命名空間形態;Refs:/Fixes:/Closes: 在 git 生態各有既定語意、借用製造歧義;Task: 太泛將來可能撞別的工具。代價:字長,但由提交模板產生、人不必自己打(Co-Authored-By 就是這樣運作)"
   650	    56	    decided: 2026-09-07
   651	    57	    valid: true
   652	    58	  - content: 「綠」的來源用 CI 那筆,不用 code-loop pass
   653	    59	    id: d6
   654	    60	    context: 兩個候選都按版本記:governance/code-loop/main.json 的 {head_sha,status} 與 lumos ci-status 的 {sha,conclusion}
   655	    61	    why_chosen: ★code-loop pass 記的是「審查過了」不是「測試綠了」,狀態值裡還有 skipped——拿它當測試結果就是借一個紀錄表達它沒有的意思,正是本 repo 今天抓了一整天的病★;CI 那筆語意就是對的(實查 JSON 帶 sha 與 conclusion,本地讀不打網路)。代價不小:CI 只在推送後跑,本機未推的工作查不到,所以必須把「還沒推=未知」與「未完成」分開輸出——混在一起就是新的假綠
   656	    62	    decided: 2026-09-07
   657	    63	    valid: true
   658	    64	---
   659	    65	# 進度從提交推導_計劃
   660	    66	
   661	    67	> 白話:現在「這件事做到哪一步」是人手寫在筆記裡的,所以會漂——有一篇計劃狀態寫「做完了」,
   662	    68	> 裡面 60 個勾選框一個都沒勾。本案要把它換成**算出來的**:每個工作項給一個名字,
   663	    69	> 完成它的那個提交把名字掛上去,進度就從 git 算,沒有東西需要人維護。
   664	    70	
   665	    71	> **本篇用到的三個詞**:「外家」=不是編排者那一家的審查席(本 repo 慣例上是 Codex);「f2」=某輪外家報告的第 2 條發現(此處指 [[Projects/執行DAG_調研]] 那輪);「編排者」=負責派審查員、判讀報告、折入修正的那個角色(本案是主對話的 AI);「群」=[[Projects/全repo審視_計劃]] 把 130 條發現去重合併後、可獨立交付的分組。
   666	    72	
   667	    73	PRIOR-ART:①★最小解在既有機制層,而且不用發明格式★——**git 原生就有 trailer**(提交訊息尾端的 `鍵: 值` 欄位),`git log --format='%(trailers:key=X,valueonly=true)'` 一個旗標就查得出來;**本 repo 每一筆提交已經在產 trailer**(近 30 筆 100% 帶 `Co-Authored-By`/`Claude-Session`),所以是加一個鍵,不是加一套新機制。②本家已有可抄的樣板=審查迴圈那條線(`loop verify-progress` 的 help 逐字:「不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)。」)。③世界解:GitHub 的 `Closes #N` 是同型但綁在 forge 上;beads / Task Master 那類已於 [[Projects/執行DAG_調研]] d1 裁定「可借形狀、不借實作」(零依賴家規)。④不採用新依賴:全案只用 git 與 python3 stdlib。
   668	    74	
   669	    75	## 問題(有症狀、有數字、有消費者)
   670	    76	
   671	    77	**症狀**:任何一個 session 都答不出「這件實作做到哪一步了」。
   672	    78	
   673	    79	**當場量到的數字(2026-09-07)**:
   674	    80	
   675	    81	| 量到什麼 | 數字 |
   676	    82	|---|---|
   677	    83	| Projects 標「進行中」 vs 超過 30 天沒動 | **46 篇 / 其中 17 篇**(★快照 2026-09-07 傍晚;原稿寫 43 是當天稍早的量測,差的 3 篇是同日新增、含本篇自己★。「17 篇」前掃機械重算吻合) |
   678	    84	| 一篇 `status: done` 的實作計畫,裡面的勾選框 | **60 個框,0 個打勾**(12 任務 × 5 步驟,全是實作步驟不是驗收清單) |
   679	    85	| 另一篇實作計畫的勾選框 | **39 個框,全部打勾** |
   680	    86	| [[Projects/全repo審視_計劃]] 的 50 群主清單 | **沒有「做完沒」這一欄**;進度靠翻提交訊息回推 |
   681	    87	| 近 120 筆提交帶項目編號的 | **6 筆**(而且全部集中在那份有編號的主清單上) |
   682	    88	
   683	    89	★第二、三列並列才是重點★:同一個 repo、同一種格式,**有人維護有人不維護,而沒有任何東西會知道差別**。
   684	    90	
   685	    91	**消費者**:①接手的 session(現在只能讀散文猜)②Enzo 本人(問「做到哪」要人回答)③無人自跑的迴圈(未來)。
   686	    92	
   687	    93	## 根因:完成與記錄是兩件事
   688	    94	
   689	    95	- **審查迴圈為什麼準**:★「完成一輪」和「記下一輪」是**同一個動作**★——那筆帳本身就是工作成果。不可能做了沒記,也不可能記了沒做。
   690	    96	- **實作為什麼歪**:工作成果是程式碼,記錄是另外去勾一個框。**兩件事分開就一定會漂**;那 60 個沒勾的框就是這樣來的。
   691	    97	
   692	    98	**所以本案不是「做一個進度追蹤器」,是「讓完成那個動作自己留下紀錄」。**
   693	    99	
   694	   100	## 設計(三步,每步可獨立交付)
   695	   101	
   696	   102	### [S1] 工作項要有一個在筆記之外還活著的名字
   697	   103	
   698	   104	- 現況:審查迴圈有(編號＋第幾輪)、50 群主清單有(`#N`),**其餘實作工作沒有任何識別碼**。
   699	   105	- 沒有名字 → 提交掛不上 → 沒有可追加的紀錄 → 完成狀態只能手寫 → 一定漂。**這條因果鏈沒有分叉,斷點在最前面。**
   700	   106	- 本步只定慣例與格式,不寫程式。
   701	   107	
   702	   108	### [S2] 完成的動作把名字掛上去(用 git trailer,不發明格式)
   703	   109	
   704	   110	- 提交訊息尾端加一行 `Task: <識別碼>`(鍵名待裁,見開放問題)。
   705	   111	- 讀取端:`git log --format='%(trailers:key=Task,valueonly=true)'`——★git 原生解析,不自己寫正則去撈提交訊息★(自己撈=又一個「形式對、內容不一定對」的地方)。
   706	   112	
   707	   113	### [S3] 進度用算的,不給人維護
   708	   114	
   709	   115	- 新增唯讀查詢:某個計劃的每個工作項,有沒有提交掛過它、最後一次是什麼時候、動了哪些檔。
   710	   116	- ★狀態不寫回筆記★——寫回去就又變成一份會漂的手寫狀態。要看就當場算。
   711	   117	- 樣板照 `loop verify-progress`:它的 help 逐字寫「不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)。」
   712	   118	
   713	   119	## 範圍刀(明確不做)
   714	   120	
   715	   121	- **不建第二張圖、不建任務狀態檔**——[[Projects/執行DAG_調研]] 已裁:手維護的狀態檔正是本案要消滅的東西。
   716	   122	- **不做認領/租約/多 agent 派工**——同上,現在買不到什麼。
   717	   123	- **不碰審查迴圈那條線**——它已經會動,動它只有下跌空間。
   718	   124	- **不做跨任務依賴(A 卡 B)**——依賴建立在「完成」之上;完成先可信,依賴才有意義。本案是它的前置,不是它。
   719	   125	- **不自動改筆記的 `status` 欄**——本案只提供查詢。
   720	   126	
   721	   127	## ★誠實天花板:這條路最多蓋到四分之三★
   722	   128	
   723	   129	- 先前量過:74 個任務段裡 **56 個(75%)** 抽得出對應的測試函式名;**剩下 18 個是天生沒有**——改 skill 散文、圖譜回填、真機驗收這類。
   724	   130	- **那一類沒有提交可掛,或掛了也證明不了什麼。** 本案對它們**無效**,不假裝有效。
   725	   131	- ★但「25% 全部無解」講太滿(2026-09-07 自查)★:其中一部分**有非散文的訊號**可用——真機驗收有 maestro 測試(既有合約行就綁著 `maestro:smoke_05_manual_discount_over_100` 這種)、圖譜回填有 `lumos doctor` 與 `spec-trace` 可判。**真正無解的是改 skill 散文那一類。** 實際比例沒量過,★要裁射程前應先把 18 個逐一分類★。
   726	   132	- ★不寫「之後再想辦法」——寫不出判準就明說這一段靠人★,並在輸出裡標成「這類算不出來」,不要讓使用者以為算過了。
   727	   133	
   728	   134	## ★第一版裁決(2026-09-07,Enzo 委任編排者裁;送設計審前的 v1)★
   729	   135	
   730	   136	三題全裁,兩題直接借既有前例、一題否掉一個看似方便的選項:
   731	   137	
   732	   138	### [D1] 識別碼 = 沿用既有的 `[SN]` 條款標記,定址寫成 `<計劃節點rel>#S1`
   733	   139	
   734	   140	★不發明新方案★,三個現成理由:
   735	   141	- **標記已經有**:計劃裡寫 `[S1]`/`[S2]` 是既有慣例,而且**已經有消費者**——`spec-trace` 的用途就是「計劃結案前看哪些條款沒有驗證紀錄認領」。
   736	   142	- **定址形狀已經有**:決策的定址是 `<節點rel>#dN`(程式裡有格式驗證與 dangling 偵測)。`#S1` 完全比照,連驗證邏輯都可以照抄。
   737	   143	- **不必維護登記簿**:識別碼從計劃節點自己長出來,沒有第二份要同步的東西。
   738	   144	
   739	   145	**代價(明寫)**:計劃節點改名會讓舊 trailer 指不到——★但決策定址有同一個問題,所以這不是本案引入的新風險,是沿用既有取捨★。
   740	   146	
   741	   147	### [D2] trailer 鍵名 = `Lumos-Task:`
   742	   148	
   743	   149	- **比照本 repo 既有形態**:現在每筆提交都帶 `Claude-Session:`,同樣是「命名空間-用途」的連字號形式。
   744	   150	- **避開世界慣例的語意**:`Refs:`/`Fixes:`/`Closes:` 在 git 生態各有既定意思,借用會製造歧義;`Task:` 太泛,將來可能撞別的工具。
   745	   151	- **代價**:字長。~~但它由提交模板產生,人不必自己打~~ → ★**前掃 ④-11 推翻(而且這條最痛)**★:實查 `git config commit.template` 指向的檔案是**空的**——`Co-Authored-By`/`Claude-Session` 真正的產生方式是**AI 每次提交時照 session 指示手動打進去**,★不是 git 機制自動代入,沒有任何機械強制力★。
   746	   152	  所以正確的代價是:**字長,而且要靠寫提交的人記得加**。
   747	   153	  ★這帶出一個設計級的問題,交給席位判,前掃不自行裁★:本案整個 [S2] 都建立在「提交會掛 trailer」上,而那一步**目前是純自律**——這跟本案自己主張的「讓完成自己留下紀錄、不靠人維護」精神有落差。**沒有守衛的 trailer,漏掉的那些工作項會長期顯示成『沒人做過』,而那正是本案要消滅的假狀態。**
   748	   154	
   749	   155	### [D3] 「綠」的來源 = **CI 那筆,不用 code-loop pass**
   750	   156	
   751	   157	★這題我否掉看似方便的那個選項★:
   752	   158	
   753	   159	- `code-loop pass` 記的是**「審查過了」**,不是「測試綠了」;而且它的狀態值裡有 `skipped`。**拿它當測試結果,就是借一個紀錄去表達它沒有的意思**——那正是本 repo 今天一整天在抓的病(「形式對、內容不成立」)。
   754	   160	- CI 那筆的語意就是對的。實查其 JSON:`{"sha": "9854ba5…", "conclusion": "success", "run_id": …, "branch": "main", "workflow": "CI"}`——★按版本記、帶結論、本地讀不打網路★(`lumos ci-status`)。
   755	   161	- **代價(明寫,而且不小)**:CI 只在推送後跑,**本機還沒推的工作查不到**。所以要接受一個語意:★「還沒推」= **未知**,不是「未完成」★——輸出必須分得出這兩者,混在一起就是新的假綠。
   756	   162	
   757	   163	## 待裁的開放問題(留給設計審)
   758	   164	
   759	   165	3. ~~**「完成」怎麼定義**~~ → ★**已裁(2026-09-07 Enzo)**:完成判準掛在**實作端**,看**測試有沒有過**;判的是「整個功能有沒有完成」+「相依功能有沒有回歸」。**明確不做散文級判準。**★
   760	   166	
   761	   167	   **★這個切法躲開了外家 f2 的反對,而且是有理由的躲開,不是繞過★**:f2 打的是**任務級**「測試綠=任務完成」——Task 1–5 全部往同一個 `t_delguard()` 裡續加斷言,那個測試綠分不出誰做完了。
   762	   168	   但 Enzo 裁的是**功能級**:①功能級「這個功能的測試套綠」不受共用測試影響(共用的正是同一個功能的測試) ②「既有測試開工前就綠」對**新功能**不成立(它的測試本來不存在) ③「有的任務只寫跑全套」在功能級不是缺陷,**那就是「相依功能沒回歸」這一半的定義**。
   763	   169	   ★三條反對在功能級各自失效——所以這不是無視外家,是換了一個 f2 打不到的粒度。★
   764	   170	- **要不要擋**:先做唯讀查詢,還是一開始就讓 pre-commit 提醒「這批改動沒掛任何工作項」?★編排者傾向先唯讀★(理由:本案的價值還沒有本地證據,先擋會逼出湊數的 trailer=製造假資料),但沒有量過,留給審。
   765	   171	- ★**原稿寫「`[SN]` 目前實際沒人寫」——不屬實,前掃逐篇實跑推翻(④-4)**★:全 repo 158 篇計劃逐篇跑 `spec-trace`,**32 篇真的寫了 `[SN]`,其中 13 篇被真實的 Verification 完整認領(rc=0)**,另 19 篇部分未認領;126 篇未啟用。
   766	   172	  ★這條反而強化 D1★:不是「慣例存在但沒人用」,是**已經在用、而且已經有 13 篇完整跑通**——沿用它的成本比原稿估的更低。
   767	   173	  (原稿那句還跟本文自己「spec-trace 已經有消費者」直接打架,同一份文件內互相矛盾,已改。)
   768	   174	- 仍待審的是**覆蓋率**:126/158 沒寫。要不要同時處理「怎麼讓人真的寫」,是設計審該打的點。
   769	   175	- **那 18 個「沒有測試可掛」的任務段還沒逐一分類**(先前只知道總數);射程要收在哪,得先分類。
   770	   176	
   771	   177	## ★裁定之後浮出來的兩個新問題(Enzo 裁完才看得到)★
   772	   178	
   773	   179	### 甲、功能級是二元的,但「接手」需要更細
   774	   180	
   775	   181	本案的來源需求是「agent 做到一半,任何 session 接得下去」。
   776	   182	
   777	   183	- **功能級判準只答得出「完成 / 沒完成」。** 一個功能拆 12 個任務、agent 停在第 7 個 → 功能測試是紅的 → 你只知道「沒完成」,**不知道「做到第 7 個」**。★那正好是接手最需要的那一格。★
   778	   184	- **但不必換判準就能補**:先前量過,74 個任務段裡 **56 個(75%)** 自己就寫了對應的測試函式名。所以**同一個判準可以有兩種解析度**:
   779	   185	  - **功能級**(是否完成)= 該功能的測試套 + 全套回歸 → **這是 Enzo 裁的那個,是「完成」的權威**。
   780	   186	  - **任務級**(做到哪)= 逐個任務宣告的測試名綠了沒 → **只當接手用的進度指示,不當完成判準**(f2 的反對在這一級仍然成立,所以★不得用它宣告完成★)。
   781	   187	- ★兩級必須語意分明:一個是判定,一個是提示。混用就會把 f2 打過的洞再開一次。★
   782	   188	
   783	   189	### 乙、「綠」是**什麼時候**的綠
   784	   190	
   785	   191	- 若指「現在跑一次是綠的」→ 每次查進度都要跑全套(約 8 分鐘),**查不起**。
   786	   192	- 若指「宣告完成的那個版本上是綠的」→ 要有一筆按版本記的結果。
   787	   193	- ★好消息:這筆紀錄已經存在★——`governance/code-loop/main.json` 就是 `{head_sha, status}` 形態(實查:`head_sha: c103e324…`,`status: passed`);另有 `lumos ci-status`(只讀上次 CI 結果、不打網路)。
   788	   194	- **所以本案不必新建測試結果帳,接既有的即可**。★來源已於 [D3] 裁定=CI 那筆、不用 code-loop pass★(本節原本把它寫成「還沒裁」,是撰寫順序造成的殘留,前掃 ③ 抓到,已改)。
   789	   195	
   790	   196	## 驗收線(這份計劃算不算做成)
   791	   197	
   792	   198	- 能對一份真實的實作計畫,**不讀它的勾選框**,答出每個工作項有沒有被提交掛過、最後一次何時。
   793	   199	- 對那 18 個「天生算不出來」的任務段,**輸出明說算不出來**,不含糊。
   794	   200	- 三步各自有測試;測試 fixture ★用真的呼叫 git 產生,不手刻★(2026-09-07 教訓:手刻 fixture 導致 code-loop 那半是死碼)。
   795	governance/code-loop/feat__claude-reinject.json:2:  "head_sha": "ff86c560b6f3cbc2ff516cf6b99cfbb8e3362591",
   796	governance/code-loop/feat__claude-reinject.json:3:  "status": "passed",
   797	governance/code-loop/feat__claude-reinject.json:4:  "note": "SDD 6-task TDD loop(每task fresh implementer+sonnet review+fix)+ opus whole-branch 終審 Ready to merge 無 Critical/Important;等價 code-loop 終審",
   798	governance/code-loop/feat__test-layers-reminder.json:2:  "head_sha": "9d78c58459fa6ecea461788bd03719abe7a05bca",
   799	governance/code-loop/feat__test-layers-reminder.json:3:  "status": "passed",
   800	.github/workflows/ci.yml:16:          fetch-depth: 0   # code-loop gate 要算 before..sha 的 diff(體檢 #5)
   801	.github/workflows/ci.yml:33:      - name: code-loop gate (push 後盾;體檢 #5)
   802	.github/workflows/ci.yml:48:          python scripts/lumos code-loop check --diff "$BEFORE..$SHA" --at-sha "$SHA" --branch "$BRANCH" --repo . || {
   803	.github/workflows/ci.yml:51:              echo "::error::tier=high 代碼無 code-loop 留痕——本機 pre-push 被繞過(--no-verify)或留痕失效;補 lumos code-loop pass|skip --note 後重推"
   804	governance/code-loop/feat__codeloop-guard.json:2:  "head_sha": "9b195c4dc14847ff9666fbabf9a1e6be5c40a2ab",
   805	governance/code-loop/feat__codeloop-guard.json:3:  "status": "passed",
   806	governance/code-loop/feat__codeloop-guard.json:4:  "note": "SDD 5-task loop + opus whole-branch 對抗終審 Ready to merge(無 Critical/Important);等價 code-loop 終審",
   807	governance/code-loop/feat__stack-perf-questions.json:2:  "head_sha": "4fdf8ca79f1cfdb05cab1fa43fee1f32c0ed8121",
   808	governance/code-loop/feat__stack-perf-questions.json:3:  "status": "skipped",
   809	governance/code-loop/feat__public-slim-handoff.json:2:  "head_sha": "7fa0c0cf82ab042caa7154305825e144ccb964ec",
   810	governance/code-loop/feat__public-slim-handoff.json:3:  "status": "passed",
   811	governance/code-loop/feat__public-slim-handoff.json:4:  "note": "code-slim-handoff 六輪對抗審收斂:6/6 canary caught,K-streak=2(r5/r6 存活 findings 皆 0),G2 枯竭[0,0]。存活未修 minor 各附理由:①slim-gen.py 死 import re(不進交付包,接手者看不到)②slim-scan skill 名子字串比對無詞邊界(定位=出候選交人裁,多一條噪音無害)③prose 形態跳過 <4 字元指令(誤報率取捨,交付文字已逐條人裁)④uninstall symlink 迴圈無防循環(需人為造 A→B→A,一次性腳本)⑤slim-gen.py 註解混簡體(不進交付包)。無 stack_questions(pitfalls manifest 未帶)。真跑優先:全套 1911 passed 0 failed;Landmark clone 端到端實跑 install→uninstall CLAUDE.md byte-equal、git status 全空",
   812	governance/code-loop/main.json:2:  "head_sha": "15f892e9b06495e63647a71f188030e09094cfb9",
   813	governance/code-loop/main.json:3:  "status": "passed",
   814	scripts/lumos:157:#   把中間的真散文整段吞掉)。這兩個假設在 code-loop r2/r4 各造成實測的靜默錯答:
   815	scripts/lumos:933:    # ── ★未閉合 frontmatter(2026-08-03 code-loop r4 抓到的既有 major)★ ──
   816	scripts/lumos:1241:    # [S3] 中心性重驗排程:兩清單各自按 PR 降冪重排(僅顯示序;gov 寫入序=上方掃描迴圈,不動)
   817	scripts/lumos:1325:                continue   # r3-F2:code-loop 零前掃步驟,計數它=逼偽宣告
   818	scripts/lumos:1468:    # 這本帳有四個整檔讀者(rewrite 血緣查詢、gov 彙整、code-loop 的 CI fallback、週回放),
   819	scripts/lumos:1553:    #   設計見 Projects/關係層傳播守衛_計劃 [S6](phase-1 MVP,免前置、純 frontmatter)。
   820	scripts/lumos:1579:    #   本就掃全圖,補網不需;主網 proactive 連鎖才需 P0)。設計見 Projects/關係層傳播守衛_計劃 [S7]。
   821	scripts/lumos:1625:                # [M1] E2 首判精化:鄰居有 decision_refs → 只在指到「那條」翻案決策時才標
   822	scripts/lumos:1627:                # [自動養成 不對稱信任] 抑制向只讀 decision_refs(human/cascade),**不讀 decision_refs_ai**
   823	scripts/lumos:1629:                refs = [str(x).strip() for x in as_list(notes[arel].fields.get("decision_refs"))]
   824	scripts/lumos:1750:    # Check E3: 意圖鏈斷義(軟,不擋,不計 issues)——[M1/S8] 精確版:decision_refs(全域格式
   825	scripts/lumos:1751:    #   <節點rel>#dN,M1/P2 決策穩定 ID)指向的那條決策已 valid:false → 本驗證建在被推翻的意圖上。
   826	scripts/lumos:1753:    #   設計見 Projects/關係層主網_實作計畫 M1;取代母計劃 [S8] 的高噪音 advisory。
   827	scripts/lumos:1757:        # [自動養成 不對稱信任] firing 向讀「聯集」decision_refs + decision_refs_ai(放寬)
   828	scripts/lumos:1759:        # [code-loop r1 A/C-minor] (rel,ref) 去重:過渡態同 ref 可能兩欄都有,避免重複通報虛胖計數
   829	scripts/lumos:1761:        for ref in as_list(n.fields.get("decision_refs")) + as_list(n.fields.get("decision_refs_ai")):
   830	scripts/lumos:1768:                e3_dangling.append(f"{rel} → {s} (格式非 <節點rel>#dN)")
   831	scripts/lumos:2138:    # Check F: linter 宣告檔健康(lint接線收口 [S1]:SARIF 橋最後一哩——宣告了跑不動的
   832	scripts/lumos:2376:    ★為什麼不用 `FENCE_RE.sub("")`(2026-08-03 code-loop r2,全局哨兵抓到,附兩處實測重現)★:
   833	scripts/lumos:2412:    ★為什麼所有人都必須走這裡(2026-08-03 code-loop r2/r4)★:原本各處自己用
   834	scripts/lumos:2444:    ★為什麼要抽出來(2026-08-03 code-loop r1,slot3 附實測)★:多詞回退的預檢原本自己
   835	scripts/lumos:2561:            # (2026-08-03 code-loop r1,slot3 附實測;slot2 同一處判 minor,依規矩取高)
   836	scripts/lumos:3504:    "decision_refs", "decision_refs_ai", "pitfall_when", "pitfall_ask", "pitfall_source",
   837	scripts/lumos:3787:            print(f"(opt-in 未啟用) {rel} 無 [SN] 條款標記——要追溯就在規格 bullet 加 [S1]/[S2]…")
   838	scripts/lumos:3797:        # 已知設計限制:多計劃 Verification 提及 [S1] 會同時記入兩計劃的 S1
   839	scripts/lumos:3862:                "check-j", "check-k", "check-r", "check-s", "check-s2", "ci", "code-loop", "design-loop", "kill", "signoff", "bound-tests",
   840	scripts/lumos:4045:         "gate": "L2", "kind": "bypassed", "hard": False, "nodes": [], "detail": d.get("subject", "")})
   841	scripts/lumos:4068:         # [S2] second 行的 verdict/ref 併進 detail(否則分歧訊號在治理帳全程隱形)
   842	scripts/lumos:4078:             "gate": "ci", "kind": d.get("conclusion", "?"), "hard": False, "nodes": [],
   843	scripts/lumos:4170:        # [S2] 第二判者分帳(否則 overturn 分歧只在 detail 字串裡、看不到彙總)
   844	scripts/lumos:4247:# 嚴重度綁定機械掃 [S1](2026-08-26):severity 值序單一常數——原三處字面複製
   845	scripts/lumos:4250:# 生效日:只給讀側([S2] 歷史掃分新舊帳)消費;寫側每筆 ts 天生=now 恆為「新」,
   846	scripts/lumos:4255:# 改制回測 [S2]:判定制度版本常數——d5 判定語意改版就 bump;golden 閉包記它,
   847	scripts/lumos:4342:    定位=第二層縱深:生效日(2026-08-26)前的歷史帳=advisory;生效日後抓到低報=寫側 [S1]
   848	scripts/lumos:4370:        tag = "這筆是生效日後的新帳——寫側本應拒帳,代表 [S1] 有 bug,開 Issue 攤人" if era_new else "歷史帳(生效日前),寫側不溯及"
   849	scripts/lumos:4373:        tag = "生效日後的新帳不該掃不出宣告行(寫側本應拒帳)——查 [S1]" if era_new else "歷史帳相容:格式無法機械驗,僅提醒"
   850	scripts/lumos:4462:        # 改制回測 [S2]①(2026-08-26):spec 路徑一併入帳——replay --freeze 補漏靠它反查
   851	scripts/lumos:4474:    # 且 diff 大小是主導混淆變數)。本專案十輪 code-loop 的 diff 從 332 到 2770 行,
   852	scripts/lumos:4494:    # 為什麼開新欄——[S4] 七天彙總要機器回讀「這輪怎麼收+花多少」;塞 note 散文是
   853	scripts/lumos:4499:        _OUTCOMES = ("converged", "skipped",
   854	scripts/lumos:4647:    # ── 嚴重度綁定機械掃 [S1] 寫側強制(2026-08-26)★行為改變★:審查席帳列
   855	scripts/lumos:4815:    走 [S1] 同一自驗 helper(唯一鍵=自身新 token);loop status 天然忽略(second 行無 loop 欄)。
   856	scripts/lumos:4869:    """異質 panel 接線(code-loop 三輪壓縮):把多個 finder 各自找到的 finding-key
   857	scripts/lumos:4870:    彙成 capture-recapture 輸入。code-loop 的 finder 是**異質**的——LLM reviewer、
   858	scripts/lumos:4891:    """capture_counts 型別守衛(2026-08-14 code-loop r1 s2 席):回純 int list,壞型回 None。
   859	scripts/lumos:4930:    """M1包 判定輪加驗(code-loop 補審 r1 折入:cluster 與無-cluster 兩路皆須過,不得繞):
   860	scripts/lumos:5248:    fails += _panel_extra_checks(latest, min_seats, spec)   # M1包:cluster 路不得繞過(code-loop r1)
   861	scripts/lumos:5270:    """異質 panel 接線的機械生產者(code-loop 三輪壓縮):把各 finder 的 finding-key
   862	scripts/lumos:5349:        cur = _sha256_file(spec_path)   # OSError 上拋——呼叫端統一 rc2(code-loop r2:panel/light 原轉字串成 rc1,與 G1 不對稱)
   863	scripts/lumos:5379:    """[S2] 結構化壓縮(結清式收斂_計劃,2026-07-28):長跑上下文不交通用摘要——規則式三欄:
   864	scripts/lumos:5421:# ★code-loop 那組的 nodes 欄永遠是空陣列★(148 筆全空)——因為那本帳認的是「分支 + 版本」
   865	scripts/lumos:5423:# 第一版把兩組混在同一個集合裡用 nodes 比對,結果 code-loop 那半是死碼,
   866	scripts/lumos:5427:# code-loop 這組只能從自由文字的 detail 認編號(慣例上 detail 開頭就是編號)。
   867	scripts/lumos:5430:# REVISIT:2026-11-07 正解是讓 code-loop pass/skip 收一個 --loop 參數、把編號寫進 nodes,
   868	scripts/lumos:5432:LOOP_CLOSE_EVENTS_BY_DETAIL = {("code-loop", "passed"), ("code-loop", "skipped")}
   869	scripts/lumos:5440:# ★誠實記★:code-loop 的放行事件早得多(最早 2026-07-05),比這個日期早六週。
   870	scripts/lumos:5441:# 上面那個日期只用在「設計審那組」的免責聲明,不涵蓋 code-loop 那組。
   871	scripts/lumos:5473:# ——實測 code-234 唯一那筆審查記錄比 code-loop 過閘晚 8 分鐘、code-kill 晚 14 分鐘,
   872	scripts/lumos:5497:    - code-loop 那組:nodes 永遠空,只能從自由文字 detail 認編號——所以要先知道有哪些編號
   873	scripts/lumos:5543:    (code-loop 那組早得多,最早 2026-07-05)——所以「沒關門」只等於「帳面沒看到關門事件」,
   874	scripts/lumos:5544:    不等於「沒做完」。code-loop 那組還多一層:它的編號只在自由文字裡,認法是啟發式,
   875	scripts/lumos:5824:    """[S3] 獨立進度驗證器(結清式收斂_計劃,2026-07-28):看不到被審材料的覆核原語——
   876	scripts/lumos:5904:    """settle 收斂閘([S1] 結清式收斂_計劃,2026-07-28):清單全結清 ∧ G1 refcheck ∧ G3(末筆 result=現檔)。
   877	scripts/lumos:6071:        print("擋下:--stage 必填(在哪一站發現:實作/code-loop/CI/prod/使用者回報…)——缺階段的逃逸帳之後做不了「在哪一站漏的」分層統計", file=sys.stderr)
   878	scripts/lumos:6150:        # [S1] rc2 互斥/前置群(fail-closed;結清式收斂_計劃 2026-07-28)
   879	scripts/lumos:6223:        except OSError as e:   # G3 --spec 不可讀:與 legacy G1 對稱 rc2(code-loop r2 折入)
   880	scripts/lumos:6252:        except OSError as e:   # 與 legacy G1 對稱 rc2(code-loop r2 折入)
   881	scripts/lumos:6260:            fails.append(f"席數不足(min-seats={min_seats};空 auditor 不計席——code-loop r1 折入)")
   882	scripts/lumos:6347:    if min_seats:   # legacy gate 消費;**逐輪**驗非空(code-loop r2 Codex:整窗聯集會讓「一有一空」過關)
   883	scripts/lumos:6360:        except OSError as e:   # 對稱 G1 rc2(code-loop r2 折入;G1 讀 text 過≠hash 讀 bytes 必過,race 窗)
   884	scripts/lumos:6409:# 編制數字單源=本表(skill 散文降解說);數值逐條抄自 lumos-design-loop/lumos-code-loop SKILL 現值。
   885	scripts/lumos:6527:    auditors, skipped = [], 0
   886	scripts/lumos:6533:            skipped += 1
   887	scripts/lumos:6543:            skipped += 1
   888	scripts/lumos:6548:    return auditors, skipped
   889	scripts/lumos:6554:    roster對帳併入問閘 [S1]:only_rid=只對這一輪(同時抑制內部 dispatch glob 補漏——問閘尾端用);
   890	scripts/lumos:6616:        auditors, _skipped = _roster_dispatch_entries(loop_dir, rid) if loop_dir.is_dir() else ([], 0)
   891	scripts/lumos:6636:                msg += ";此席編制為 fail-closed(本行僅轉述編制對照,不裁決;處置見 code-loop skill)"
   892	scripts/lumos:6929:    if panel_fmt:   # 讀側損壞守衛不得因缺 --spec 提前 return 而繞過(code-loop r2 折入)
   893	scripts/lumos:6978:    # ── tier↔格式一致性(code-loop r1 折入:格式推導可被繞——high 漏帶 --round 會走鬆的 legacy 閘;
   894	scripts/lumos:7033:            # [T5 design-loop重設計] 處置閘模板(選用;record_cmd 原樣保留給 code-loop/舊流程)
   895	scripts/lumos:7147:                             light=light, min_seats=width)   # 恆傳(light/legacy=1;code-loop r1 折入)
   896	scripts/lumos:7654:    """[S3] 歸因:綁定測試名的任一出現處,其行起(含同行)5 行窗內有失敗標記,
   897	scripts/lumos:7723:                      file=(sys.stderr if as_json else sys.stdout))   # [S3] --json 純度
   898	scripts/lumos:7764:                  file=(sys.stderr if as_json else sys.stdout))   # [S3] --json 純度:診斷一律 stderr
   899	scripts/lumos:7829:                    # [S3] timeout 降弱證據(不再計 killed):掛掉可能是環境非變異
   900	scripts/lumos:7909:        # [S3] 措辭收斂:「咬得住」只配全強殺;混弱證據分列(unattributed+timeout 同桶)
   901	scripts/lumos:8461:    """[S1] 中心性/PPR helper(中心性重驗排程_計劃+檢索PPR邊權_計劃,2026-07-28):
   902	scripts/lumos:8586:    # bare 模式:風險加權排序([S2][S3] 中心性重驗排程_計劃;--legacy 保字母序=舊行為)
   903	scripts/lumos:9905:    id_mode = re.fullmatch(r"#d\d+", match.strip())
   904	scripts/lumos:9907:        # [M1/R12] #dN 精確定址:比對項內 id 行
   905	scripts/lumos:9924:                             f"候選: {cands} …改用更長的片段,或用 --match \"#dN\" 指定編號")
   906	scripts/lumos:9953:    # [M1/P2] 讀 target 的 id → 組全域格式 <rel>#d<N> 回傳(下游 header/CASCADE/--from 同格式,無裸碼流出)
   907	scripts/lumos:9989:    [M1/P2]:指派穩定 id d<max+1> 並回傳 (rc, 全域決策id <rel>#d<N>);dispatcher 解包後
   908	scripts/lumos:10036:    到所有有 decisions 的節點(decision_refs 自動養成前置 P;顯式指令、非隱式改)。
   909	scripts/lumos:10045:            except (ValueError, RuntimeError, OSError) as e:   # [code-loop r1 A] 補 OSError:寫檔面(磁碟滿/權限)
   910	scripts/lumos:10113:    [code-loop r1] O_NOFOLLOW 拒 symlink 終點(字元白名單擋不住,CX1);os.write 回傳驗滿寫
   911	scripts/lumos:10171:            # [code-loop r1 CX2] 必要欄位齊才算合法 header——空殼 {"event":"header"} 會讓
   912	scripts/lumos:10190:    # [code-loop r1 A3] fullmatch 非 match——match+$ 會放過尾端換行(re 的 $ 容忍結尾 \n)
   913	scripts/lumos:10197:        raise ValueError(f"--from 要寫完整的 <筆記路徑>#d<編號>,只給裸的 {from_id} 不收(不帶路徑會跟別篇的同號決策搞混)")
   914	scripts/lumos:10198:    if not re.fullmatch(r".+#d\d+", from_id.strip()):
   915	scripts/lumos:10199:        raise ValueError(f"--from 格式要是 <筆記路徑>#d<編號>,你給的是: {from_id}")
   916	scripts/lumos:10226:    """[decision_refs 自動養成 T1] 把精確 decision_ref(<rel>#dN)append 到 field
   917	scripts/lumos:10227:    (decision_refs=human/cascade-confirmed | decision_refs_ai=AI 填)。**exact-string dedup**
   918	scripts/lumos:10228:    ——不用 link_target(它 split('#') 會把 #dN 剝掉,導致同節點不同決策誤 dedup 成一條)。
   919	scripts/lumos:10231:    # [code-loop r1 CX3/B + delta] 顯式拒 " / \ / 任何 C0 控制字元(<0x20,含裸 \r/\n/\t)——
   920	scripts/lumos:10232:    #   strip_quotes 不反跳脫、CRLF 檔案守衛只認 \r\n 序列認不出裸 CR;合法 <rel>#dN 永不含這些。
   921	scripts/lumos:10256:# ═══════════ decision_refs 自動養成 T3(dref-v4;六原語,乾淨雙欄)═══════════
   922	scripts/lumos:10257:# 設計:Projects/decision_refs自動養成_實作計畫.md ★v4 現行 spec★(dref-v4 三輪收斂)。
   923	scripts/lumos:10258:# 不對稱信任(T1 已建):E2 抑制只讀 decision_refs 正欄、E3 firing 讀聯集;此六原語不動 E2/E3 讀側。
   924	scripts/lumos:10264:    """ref '<節點>#dN' → (節點字面, did) 或 None(格式不合)。"""
   925	scripts/lumos:10279:    """兩 ref 是否同一決策:正規化 tuple 相等。只吃「ref」(a/b 皆 <節點>#dN),故 did 恆有值
   926	scripts/lumos:10297:    """已填集合=decision_refs ∪ decision_refs_ai 的正規化 tuple(略去解不到的)。"""
   927	scripts/lumos:10302:    for fld in ("decision_refs", "decision_refs_ai"):
   928	scripts/lumos:10312:    回 (cands, skipped_no_id):cands=[(target_rel, did, content, valid)],三具名邊 fwd 解到的
   929	scripts/lumos:10314:    cands, skipped = [], 0
   930	scripts/lumos:10322:                    skipped += 1
   931	scripts/lumos:10330:    return cands, skipped
   932	scripts/lumos:10339:        cands, skipped = _dref_candidates(env, rel, tidx)
   933	scripts/lumos:10341:            if skipped:
   934	scripts/lumos:10362:    """[V2] 列某節點候選決策(含翻案),讀側去重已填,附 skipped_no_id。"""
   935	scripts/lumos:10369:    cands, skipped = _dref_candidates(env, rel, tidx)
   936	scripts/lumos:10380:                        "skipped_no_id": skipped}, ensure_ascii=False))
   937	scripts/lumos:10386:        if skipped:
   938	scripts/lumos:10387:            print(f"  (略過 {skipped} 條無 id 決策——先 reindex 才能被 ref)")
   939	scripts/lumos:10394:    """[V3] 寫 decision_refs_ai:存在性驗證+正規化冪等(已在正欄→no-op)。"""
   940	scripts/lumos:10401:        print(f"擋下:ref 要寫成 <節點>#dN 且節點解得到: {ref!r}", file=sys.stderr)
   941	scripts/lumos:10409:    for r in as_list(n.fields.get("decision_refs")):
   942	scripts/lumos:10411:            print(f"✓ {ref} 已在 decision_refs 正欄(human 確認過),不重複塞 ai 欄")
   943	scripts/lumos:10413:    for r in as_list(n.fields.get("decision_refs_ai")):
   944	scripts/lumos:10415:            print(f"✓ {ref} 已在 decision_refs_ai(冪等 no-op)")
   945	scripts/lumos:10418:    _append_decision_ref(env, rel, "decision_refs_ai", canon)
   946	scripts/lumos:10419:    print(f"✓ add-ai {rel}: decision_refs_ai += {canon}(標 by:ai;E3 firing 生效、抑制不了 E2)")
   947	scripts/lumos:10430:    fields = [("decision_refs", "human/confirmed")] if by == "human" else \
   948	scripts/lumos:10431:             [("decision_refs_ai", "ai")] if by == "ai" else \
   949	scripts/lumos:10432:             [("decision_refs", "human/confirmed"), ("decision_refs_ai", "ai")]
   950	scripts/lumos:10448:    flds = ["decision_refs"] if by == "human" else ["decision_refs_ai"] if by == "ai" \
   951	scripts/lumos:10449:           else ["decision_refs", "decision_refs_ai"]
   952	scripts/lumos:10496:    正欄 = as_list(n.fields.get("decision_refs")) if n else []
   953	scripts/lumos:10523:    """[V6] _ai→decision_refs 抽查蓋章(升級可抑制 E2)。正規化全操作+dangling 拒+覆蓋提醒+雙欄原子。"""
   954	scripts/lumos:10530:        print(f"擋下:ref 要寫成 <節點>#dN 且節點解得到: {ref!r}", file=sys.stderr)
   955	scripts/lumos:10538:    in_main = [v for v in as_list(n.fields.get("decision_refs")) if _dref_same(env, v, ref)]
   956	scripts/lumos:10539:    in_ai = [v for v in as_list(n.fields.get("decision_refs_ai")) if _dref_same(env, v, ref)]
   957	scripts/lumos:10551:    if not as_list(n.fields.get("decision_refs")) and (other or no_id_dead):
   958	scripts/lumos:10563:    if "decision_refs_ai" in struct:
   959	scripts/lumos:10564:        s, e, _k = struct["decision_refs_ai"]
   960	scripts/lumos:10570:        if "decision_refs_ai" in struct:
   961	scripts/lumos:10571:            _sa, _ea, _ = struct["decision_refs_ai"]
   962	scripts/lumos:10578:        if _st.get("decision_refs") not in (None, "list"):   # s1-f4:非清單型清楚擋
   963	scripts/lumos:10579:            print("擋下:decision_refs 欄位不是清單型,沒辦法 promote 進去(先修正 frontmatter)", file=sys.stderr)
   964	scripts/lumos:10581:        _fm_list_insert(fm, "decision_refs", '"' + canon + '"')
   965	scripts/lumos:10585:        main_hits = sum(1 for v in as_list(f.get("decision_refs")) if _dref_same(env, v, ref))
   966	scripts/lumos:10586:        ai_hits = sum(1 for v in as_list(f.get("decision_refs_ai")) if _dref_same(env, v, ref))
   967	scripts/lumos:10588:    atomic_write_verify(path, new_lines, "decision_refs", _check)
   968	scripts/lumos:10614:    # [decision_refs 自動養成 T1] confirm = 地面真相「鄰居依賴這條決策」→ 回寫 decision_ref。
   969	scripts/lumos:10615:    #   provenance 雙欄不對稱信任:by ai → decision_refs_ai(E3 firing 生效、E2 抑制碰不到);
   970	scripts/lumos:10616:    #   by human → decision_refs(可抑制 E2)。prune 不回寫(判無關=不記依賴)。
   971	scripts/lumos:10617:    #   回寫失敗=軟警告不回滾(帳本才是地面真相,decision_refs 是衍生、可從帳本重建)。
   972	scripts/lumos:10619:        # [code-loop r1 C-medium] fail-**safe**:只有明確 by==human 才落可信正欄;非 ai/human
   973	scripts/lumos:10621:        field = "decision_refs" if by == "human" else "decision_refs_ai"
   974	scripts/lumos:10624:                print(f"  ↳ decision_refs 養成: {nrel}.{field} += {from_id.strip()}")
   975	scripts/lumos:10626:            # [code-loop r1 CX2] 不過度承諾:reconcile 命令尚未實作(列 future),此處僅記帳本已提交
   976	scripts/lumos:10661:    多跳/visited 交 [S4] 編排(resume/判斷閘)。回 (neighbors=[(src,etype,invariant數)], ambigs=[(字面,候選數)])。"""
   977	scripts/lumos:11960:    舊硬編碼 tuple 曾漏 code-loop 等;同步修 install.sh 同款漂移)。"""
   978	scripts/lumos:12083:_GLOBAL_CLAUDE_HOOKS = ("check-graph-sync.py", "impact-hook.py", "ci-status-hook.py", "lumos-entry-hook.py", "dispatch-lens-hook.py")
   979	scripts/lumos:12099:# code-loop-guard.py:2026-07-06 ADR 撤除 Stop nag(見 Projects/code-loop必用守衛_計劃)——早過相容期,直接刪。
   980	scripts/lumos:12109:_RETIRED_CLAUDE_HOOKS = ("code-loop-guard.py", "verification-rot-check.py")
   981	scripts/lumos:12214:    ★sandbox_mode 只當提示,實測不擋寫檔——唯讀靠父代理 --sandbox read-only★。回 created|unchanged|skipped-foreign|skipped-not-dir(對齊 _reinject_claude_block 的 created/unchanged 詞彙)。"""
   982	scripts/lumos:12218:        return "skipped-not-dir"
   983	scripts/lumos:12223:        return "skipped-not-dir"
   984	scripts/lumos:12229:            return "skipped-foreign"
   985	scripts/lumos:12427:    # 存在性判定=scripts/lumos(真正要執行的檔;code-loop r1 F3:與 get.sh 同判準,免部分 clone 下兩端不一致)
   986	scripts/lumos:12497:                except Exception as e:                           # code-loop r1 F2:init 內部炸(權限/磁碟)別裸 traceback
   987	scripts/lumos:12501:                    # code-loop r1 F2:cmd_init 對 vendor 失敗只印警告仍回 0(rc 判定是死碼)
   988	scripts/lumos:12637:    "scripts/hooks/claude/ci-status-hook.py",       # 推送後回報 CI 狀態
   989	scripts/lumos:12931:        # roster對帳併入問閘 [S1]:問閘當輪異常轉述(異常才發聲;advisory 恆不動 rc)。
   990	scripts/lumos:12953:        # 嚴重度綁定機械掃 [S3](2026-08-26):問閘收尾對判定輪逐席跑第二層 severity 對帳。
   991	scripts/lumos:12956:        # 生效日後的帳列抓到低報=寫側 [S1] 有 bug(本應拒帳)——轉述+指路開 Issue,converged 不自動撤。
   992	scripts/lumos:12986:    # (r3-F2:code-loop 零前掃步驟,code 的 intake 是撈回紀錄非前掃紀錄——計數它=逼偽宣告)。
   993	scripts/lumos:13336:    # 2026-07-07 事故)。★r1 審:_GLOBAL_CLAUDE_HOOKS 有 4 支,原本漏檢 ci-status(CI 紅燈後備網)★。
   994	scripts/lumos:13341:                          ("sessionstart-ci-status-hook", "ci-status-hook.py"),
   995	scripts/lumos:13376:                          ("codex-sessionstart-ci-status-hook", "ci-status-hook.py"),
   996	scripts/lumos:13851:# 簿記檔白名單(單一源,兩個消費者:pitfalls --diff 掃描排除 + code-loop 留痕失效豁免)。
   997	scripts/lumos:13862:# ★真效果只在 code-loop 留痕豁免這第二消費者★:pitfalls 那端 canary-log 早被
   998	scripts/lumos:13868:_BOOKKEEPING_DIR = "governance/code-loop/"
   999	scripts/lumos:13990:    共用的單一實作(lint接線收口 [S1]②:I/O+parse+驗證不留兩份會漂移的複本)。
  1000	scripts/lumos:14138:            # Finding 1: guard run-level structure — malformed run skipped, not crashed
  1001	scripts/lumos:14614:        print(f"baseline updated ({n_ok} modules, {n_skip} skipped)")
  1002	scripts/lumos:14780:    # 型別守衛(三個門檻一致 fail-open;code-loop r1:只守 min_support 是不對稱缺口)
  1003	scripts/lumos:14984:    `--- x`,那樣會被當檔頭吃掉、整行 token 靜默漏抽(2026-08-11 code-loop r1 s5 F6)。"""
  1004	scripts/lumos:14994:    2026-08-11 code-loop r1 C);stopword 表剔除;
  1005	scripts/lumos:15009:        # (r2 code-loop 折入:r1 兩席點名、上一修波漏掉)
  1006	scripts/lumos:15056:        # (r2 code-loop 折入:N5)
  1007	scripts/lumos:15093:        # 2026-08-11 code-loop r1 B)。len<3 的行(如 `Binary file … matches`)直接丟。
  1008	scripts/lumos:15132:                # 才輪到下一次檢查,deadline 直接超支(2026-08-11 code-loop r1 H)
  1009	scripts/lumos:15151:       不是「只掛連結」,一律 False(保守朝報;2026-08-11 code-loop r1 N / spec C5)。"""
  1010	scripts/lumos:15217:        # 且 "." 前綴會讓每個檔都判成 vault、路徑相對計算全歪 → 靜默 rc0(2026-08-11 code-loop r1 E)
  1011	scripts/lumos:15230:            # 實際是沒掃到東西的失敗(r2 code-loop 折入:N3①)。丟進既有 except
  1012	scripts/lumos:15304:                # gr_rel=="." 早退同語意:不落帳(code-loop r1 s2)
  1013	scripts/lumos:15359:    回 dict {"claims", "tier"[, "lint_ran", "lint_skipped", "filtered"]};git 錯回 None(呼叫端印錯)。
  1014	scripts/lumos:15430:        # fallback: no_lint 或無 config → 維持 regex-only 輸出(不加 lint_ran/lint_skipped)
  1015	scripts/lumos:15441:    lint_skipped = []
  1016	scripts/lumos:15450:            lint_skipped.append(cmd)
  1017	scripts/lumos:15464:           "lint_ran": lint_ran, "lint_skipped": lint_skipped,
  1018	scripts/lumos:15503:        # 為什麼在這裡:code-loop skill 要求「派 reviewer 前跑 impact --diff 並附 manifest
  1019	scripts/lumos:15519:              "(貼內容不貼路徑;code-loop skill 步驟 2)——2026-08-30 盤點時 28 份 code 派工單 0 份做過這步,審查席因此判不了爆炸半徑")
  1020	scripts/lumos:16198:# conclusion 三分類(計劃 [S1] 矩陣)。**白名單制**:綠只認列舉值,非綠非紅一律「未定」——
  1021	scripts/lumos:16200:_CI_GREEN = ("success", "neutral", "skipped")
  1022	scripts/lumos:16242:    fields = "databaseId,attempt,status,conclusion,displayTitle,url,workflowName"
  1023	scripts/lumos:16277:            if st.get("conclusion") == "failure":
  1024	scripts/lumos:16295:    """寫帳(去重鍵 run_id:attempt:conclusion;helper 不 upsert 故應用層先掃)。回 rc。"""
  1025	scripts/lumos:16317:    """[S1] push 後同輪等 CI 結論。綠 rc0/紅 rc1/未定·逾時·no-run·工具缺席 rc0/帳寫失敗·參數錯 rc2。"""
  1026	scripts/lumos:16331:                print(f"CI {r.get('conclusion', '?'):<12} {r.get('workflow', '?')}"
  1027	scripts/lumos:16374:        red = [r for r in done if (r.get("conclusion") or "") in _CI_RED]
  1028	scripts/lumos:16381:                            "conclusion": r.get("conclusion"), "url": r.get("url", ""),
  1029	scripts/lumos:16393:                    "conclusion": r.get("conclusion"), "url": r.get("url", ""),
  1030	scripts/lumos:16398:            # conclusion 三分類(計劃 [S1] 矩陣;2026-07-29 外審實錘實作只做紅/非紅二分):
  1031	scripts/lumos:16401:            odd = [r for r in out if (r.get("conclusion") or "") not in _CI_GREEN]
  1032	scripts/lumos:16403:                names = "、".join(sorted({(r.get("conclusion") or "?") for r in odd}))
  1033	scripts/lumos:16419:                                     "sha": sha, "conclusion": "no-run", "url": "",
  1034	scripts/lumos:16425:                                f"lumos ci-status 再確認一次")
  1035	scripts/lumos:16428:                                     "sha": sha, "conclusion": "timeout-waiting", "url": "",
  1036	scripts/lumos:16442:        concl = r.get("conclusion") or "?"
  1037	scripts/lumos:16445:               "workflow": r.get("workflow", ""), "conclusion": concl,
  1038	scripts/lumos:16454:def cmd_ci_status(env, repo_dir=None, as_json=False):
  1039	scripts/lumos:16455:    """[S3] 唯讀查最後一次 CI 結果(不打網路,供離線與 hook)。恆 rc0。"""
  1040	scripts/lumos:16489:        last = (next((r for r in same if (r.get("conclusion") or "") in _CI_RED), None)
  1041	scripts/lumos:16490:                or next((r for r in same if (r.get("conclusion") or "") not in _CI_GREEN), None)
  1042	scripts/lumos:16509:    print(f"CI {last.get('conclusion', '?')} {(last.get('sha') or '')[:7]}"
  1043	scripts/lumos:16725:    # [S1] 設計審收斂重定義(2026-08-25):保守首版,寧漏勿噪;詞表在下一個真實設計迴圈([S6])校準
  1044	scripts/lumos:16734:    """spec 白話健檢([S1] 設計審收斂重定義 2026-08-25):掃中文模糊措辭。
  1045	scripts/lumos:17770:    """code-loop 橋接:對整段 diff 的每支改動 code 檔跑 ranked impact(query=該檔 hunk 文字),
  1046	scripts/lumos:17842:            _pm["query_gated"] = True   # 觀測欄聚合轉發(r1 f5:code-loop 鏡頭可見)
  1047	scripts/lumos:17921:# ── code-loop 留痕(Task 1) ────────────────────────────────────────────────────
  1048	scripts/lumos:17985:def _lens_cache_path(repo_root, base_sha, head_sha):
  1049	scripts/lumos:17988:    key = hashlib.sha256(f"{os.path.realpath(str(repo_root))}|{base_sha}|{head_sha}|schema{_LENS_SCHEMA}".encode("utf-8")).hexdigest()   # 帶 schema 版本:v1.1 舊快取自然 miss(v1.2 r2 外家)
  1050	scripts/lumos:18098:def _lens_hunks_base_ranges(repo_root, base_sha, head_sha, path, timeout=10):
  1051	scripts/lumos:18100:    r = _lens_git(repo_root, "diff", "-U0", base_sha, head_sha, "--", path, quote=True)
  1052	scripts/lumos:18116:def _lens_fallback(root, base_sha, head_sha, changed_files, base_tree, base_modes, deadline, cache_note=""):
  1053	scripts/lumos:18130:        return [_LENS_FB_HEADER, "既有相依:略(預算不足)", _LENS_FB_FOOT], "skipped-timeout", meta
  1054	scripts/lumos:18210:                ranges, pure_add, deleted = _lens_hunks_base_ranges(root, base_sha, head_sha, f)
  1055	scripts/lumos:18727:    base_sha, head_sha = _lens_full_sha(root, base_ref), _lens_full_sha(root, head_ref)
  1056	scripts/lumos:18728:    if not base_sha or not head_sha:
  1057	scripts/lumos:18739:    cpath = _lens_cache_path(root, base_sha, head_sha)
  1058	scripts/lumos:18825:        bound_status = "skipped-no-config"
  1059	scripts/lumos:18831:        fb_lines, fallback_status, _fb_meta = _lens_fallback(root, base_sha, head_sha, list(data.get("files") or []), base_tree, base_modes, deadline)
  1060	scripts/lumos:18849:           "base": base_sha, "head": head_sha, "cache_hit": False}
  1061	scripts/lumos:18932:    skipped_files, too_generic = [], []
  1062	scripts/lumos:18935:            skipped_files.append(f); continue
  1063	scripts/lumos:18943:            skipped_files.append(f); continue
  1064	scripts/lumos:18969:        bound_status = "skipped-no-config"
  1065	scripts/lumos:18973:        lines.append(f"計劃提到並找得到的程式檔:{', '.join(code_files)}——沒牽到任何帶合約/事故的節點" + (f";太泛不列:{', '.join(too_generic)}" if too_generic else "") + (f";超預算沒算:{', '.join(skipped_files)}" if skipped_files else ""))
  1066	scripts/lumos:18976:        lines.append(f"計劃提到並找得到的程式檔:{', '.join(code_files) if code_files else '(沒有)'}" + (f";超預算沒算:{', '.join(skipped_files)}" if skipped_files else "") + (f";太泛不列(一個檔牽超過 {_LENS_SPEC_MAX_PER_FILE} 篇):{', '.join(too_generic)}" if too_generic else ""))
  1067	scripts/lumos:18991:    out = {"text": "\n".join(lines), "mode": "spec", "code_files": code_files, "skipped_files": skipped_files, "too_generic": too_generic,
  1068	scripts/lumos:19022:    """讀 governance/code-loop/<branch>.json;不存在回 None。"""
  1069	scripts/lumos:19025:    p = Path(repo_root) / "governance" / "code-loop" / f"{safe}.json"
  1070	scripts/lumos:19035:    """marker 檔不在時(governance/code-loop/ 被 gitignore,CI 的乾淨 checkout 一定沒有)
  1071	scripts/lumos:19036:    退而讀 tracked 的 docs/.governance-log.jsonl:取該分支最後一筆 gate=code-loop 事件,
  1072	scripts/lumos:19037:    還原成 marker 同形 dict(status/head_sha/note)。沒有就回 None。
  1073	scripts/lumos:19047:            if not line or '"code-loop"' not in line:
  1074	scripts/lumos:19053:            if ev.get("gate") == "code-loop" and ev.get("branch") == branch and ev.get("head_sha"):
  1075	scripts/lumos:19059:    return {"status": last.get("kind"), "head_sha": last.get("head_sha"),
  1076	scripts/lumos:19063:def _codeloop_write(repo_root, branch, status, note, head_sha, ts):
  1077	scripts/lumos:19064:    """寫 governance/code-loop/<branch>.json。"""
  1078	scripts/lumos:19067:    d = Path(repo_root) / "governance" / "code-loop"
  1079	scripts/lumos:19069:    rec = {"head_sha": head_sha, "status": status, "note": note, "ts": ts}
  1080	scripts/lumos:19074:def _codeloop_gov_log(repo_root, branch, status, note, head_sha, ts):
  1081	scripts/lumos:19075:    """把 code-loop 事件 append 到 docs/.governance-log.jsonl(同 bypass-log 哲學)。
  1082	scripts/lumos:19083:    if not head_sha:
  1083	scripts/lumos:19087:        commit_short = head_sha[:7]
  1084	scripts/lumos:19090:            "gate": "code-loop", "kind": status,
  1085	scripts/lumos:19092:            "detail": note, "branch": branch, "head_sha": head_sha,
  1086	scripts/lumos:19102:# 改到相依功能時,impact 固定席上的合約綁了什麼測試,在 code-loop check(pre-push 每次都呼叫)就真跑一遍;
  1087	scripts/lumos:19215:    """回 dict{status, ran, red:[…], secs, reason}。status ∈ green/red/skipped/no-config/no-pins/no-bound/diff-unavailable。"""
  1088	scripts/lumos:19219:        _bound_tests_log(repo_root, "skipped", [], note)
  1089	scripts/lumos:19220:        return {"status": "skipped", "ran": 0, "red": [], "secs": 0.0, "reason": note}
  1090	scripts/lumos:19265:        head_sha = _codeloop_git_head(repo_root)
  1091	scripts/lumos:19272:                if mb == head_sha:
  1092	scripts/lumos:19309:        rec_sha = rec.get("head_sha", "")
  1093	scripts/lumos:19311:        if rec_sha == marker_sha and rec_status in ("passed", "skipped"):
  1094	scripts/lumos:19314:        # 簿記白名單豁免([[Issues/code-loop-pass自失效追尾]] 2026-08-04):pass 自己會往
  1095	
  1096	exec
  1097	/bin/zsh -lc "nl -ba scripts/lumos | sed -n '16180,16525p'
  1098	nl -ba scripts/lumos | sed -n '19020,19335p'
  1099	ls -l governance/code-loop governance/ci-status 2>/dev/null
  1100	git ls-files 'governance/code-loop/*' 'governance/ci-status/*' 'docs/.ci-*' 'docs/.governance-log.jsonl'
  1101	tail -n 20 docs/.ci-status.jsonl 2>/dev/null
  1102	tail -n 20 docs/.governance-log.jsonl 2>/dev/null" in /Users/enzo/harness/lumos-toolchain
  1103	 succeeded in 0ms:
  1104	 16180	        print(f"map built at {m['built_at']} ({bac[:8]})")
  1105	 16181	        if stale:
  1106	 16182	            print("testmap: map 可能過期,建議 rebuild", file=sys.stderr)
  1107	 16183	        if suggests:
  1108	 16184	            for s in suggests:
  1109	 16185	                print(f"  {s['conf']:.2f} {s['test']} [{','.join(s['sources'])}]")
  1110	 16186	        else:
  1111	 16187	            print("（無建議）")
  1112	 16188	        if uncovered:
  1113	 16189	            print("無已知測試:")
  1114	 16190	            for f in uncovered:
  1115	 16191	                print(f"  {f}")
  1116	 16192	    return 0
  1117	 16193	
  1118	 16194	
  1119	 16195	# ── CI 回流閉環(vault-free 讀寫帳;設計 [[CI回流閉環_計劃]] v1=direct only) ──────────
  1120	 16196	
  1121	 16197	CI_LOG_NAME = ".ci-log.jsonl"
  1122	 16198	# conclusion 三分類(計劃 [S1] 矩陣)。**白名單制**:綠只認列舉值,非綠非紅一律「未定」——
  1123	 16199	# cancelled/action_required/stale 與任何未知/未來新增值都走未定,不得靜默判綠(fail toward 不放行)。
  1124	 16200	_CI_GREEN = ("success", "neutral", "skipped")
  1125	 16201	_CI_RED = ("failure", "timed_out", "startup_failure")
  1126	 16202	
  1127	 16203	
  1128	 16204	def _ci_config(repo_root):
  1129	 16205	    """讀 .lumos/config.json 的 ci 區塊。回 (enabled, cfg)。
  1130	 16206	    總開關:未宣告 ci 區塊=功能全關(行為與未安裝逐字相同);config 壞損→退「全關」(fail-safe 到零侵入)。"""
  1131	 16207	    import json
  1132	 16208	    path = Path(repo_root) / ".lumos" / "config.json"
  1133	 16209	    try:
  1134	 16210	        data = json.loads(path.read_text(encoding="utf-8"))
  1135	 16211	    except (OSError, ValueError):
  1136	 16212	        return False, {}
  1137	 16213	    ci = data.get("ci") if isinstance(data, dict) else None
  1138	 16214	    if not isinstance(ci, dict):
  1139	 16215	        if ci is not None:
  1140	 16216	            print("⚠ .lumos/config.json 的 ci 非物件——CI 回流功能關閉(fail-safe)", file=sys.stderr)
  1141	 16217	        return False, {}
  1142	 16218	    wf = ci.get("workflow")
  1143	 16219	    if wf is not None and not isinstance(wf, (str, list)):
  1144	 16220	        print("⚠ ci.workflow 需字串或字串陣列——CI 回流功能關閉(fail-safe)", file=sys.stderr)
  1145	 16221	        return False, {}
  1146	 16222	    return True, ci
  1147	 16223	
  1148	 16224	
  1149	 16225	def _ci_gh(repo_root, args, timeout=60):
  1150	 16226	    """跑 gh(cwd=repo_root)。回 (rc, stdout, err_or_None);gh 缺席回 (None,"",訊息)。"""
  1151	 16227	    import subprocess
  1152	 16228	    try:
  1153	 16229	        r = subprocess.run(["gh"] + args, cwd=str(repo_root), capture_output=True,
  1154	 16230	                           text=True, timeout=timeout)
  1155	 16231	    except FileNotFoundError:
  1156	 16232	        return None, "", "gh 未安裝"
  1157	 16233	    except (OSError, subprocess.TimeoutExpired) as e:
  1158	 16234	        return None, "", f"gh 執行失敗: {e}"
  1159	 16235	    return r.returncode, r.stdout, (None if r.returncode == 0 else (r.stderr or "").strip()[:200])
  1160	 16236	
  1161	 16237	
  1162	 16238	def _ci_list_runs(repo_root, sha, workflows):
  1163	 16239	    """查該 sha 的 run。workflows=None→全部;字串/陣列→逐支各查一次後合併(--workflow 是單值旗標)。
  1164	 16240	    回 (runs, err)。用 gh 原生 --commit 過濾(client-side 比對會被 gh 預設 limit 20 擠掉=假綠)。"""
  1165	 16241	    import json
  1166	 16242	    fields = "databaseId,attempt,status,conclusion,displayTitle,url,workflowName"
  1167	 16243	    names = ([workflows] if isinstance(workflows, str) else list(workflows or [None]))
  1168	 16244	    out, seen = [], set()
  1169	 16245	    for name in names:
  1170	 16246	        args = ["run", "list", "--commit", sha, "--json", fields, "--limit", "100"]
  1171	 16247	        if name:
  1172	 16248	            args += ["--workflow", name]
  1173	 16249	        rc, so, err = _ci_gh(repo_root, args)
  1174	 16250	        if rc is None or rc != 0:
  1175	 16251	            return None, (err or "gh run list 失敗")
  1176	 16252	        try:
  1177	 16253	            rows = json.loads(so or "[]")
  1178	 16254	        except ValueError:
  1179	 16255	            return None, "gh 輸出非 JSON"
  1180	 16256	        for r in rows if isinstance(rows, list) else []:
  1181	 16257	            key = (r.get("databaseId"), r.get("attempt"))
  1182	 16258	            if key not in seen:
  1183	 16259	                seen.add(key)
  1184	 16260	                out.append(r)
  1185	 16261	    return out, None
  1186	 16262	
  1187	 16263	
  1188	 16264	def _ci_failed_step(repo_root, run_id):
  1189	 16265	    """失敗步驟名取自 jobs JSON(非 log 文字解析);多個全列以 ';' 串接。"""
  1190	 16266	    import json
  1191	 16267	    rc, so, _err = _ci_gh(repo_root, ["run", "view", str(run_id), "--json", "jobs"])
  1192	 16268	    if rc is None or rc != 0:
  1193	 16269	        return ""
  1194	 16270	    try:
  1195	 16271	        jobs = (json.loads(so or "{}") or {}).get("jobs") or []
  1196	 16272	    except ValueError:
  1197	 16273	        return ""
  1198	 16274	    hits = []
  1199	 16275	    for j in jobs if isinstance(jobs, list) else []:
  1200	 16276	        for st in (j.get("steps") or []):
  1201	 16277	            if st.get("conclusion") == "failure":
  1202	 16278	                hits.append(f"{j.get('name', '?')}/{st.get('name', '?')}")
  1203	 16279	    return ";".join(hits)
  1204	 16280	
  1205	 16281	
  1206	 16282	def _ci_fail_log(repo_root, run_id):
  1207	 16283	    """log 尾段:先取尾 40 行、再截 4000 字(兩上限依序)。"""
  1208	 16284	    rc, so, _err = _ci_gh(repo_root, ["run", "view", str(run_id), "--log-failed"])
  1209	 16285	    if rc is None or not so:
  1210	 16286	        return ""
  1211	 16287	    return "\n".join(so.splitlines()[-40:])[:4000]
  1212	 16288	
  1213	 16289	
  1214	 16290	def _ci_log_path(env):
  1215	 16291	    return env.vault.parent / CI_LOG_NAME
  1216	 16292	
  1217	 16293	
  1218	 16294	def _ci_write(env, rec):
  1219	 16295	    """寫帳(去重鍵 run_id:attempt:conclusion;helper 不 upsert 故應用層先掃)。回 rc。"""
  1220	 16296	    import json
  1221	 16297	    path = _ci_log_path(env)
  1222	 16298	    key = rec["dedup_key"]
  1223	 16299	    try:
  1224	 16300	        with open(path, encoding="utf-8", errors="replace") as f:
  1225	 16301	            for line in f:
  1226	 16302	                if not line.strip():
  1227	 16303	                    continue
  1228	 16304	                try:
  1229	 16305	                    d = json.loads(line)
  1230	 16306	                except ValueError:
  1231	 16307	                    continue
  1232	 16308	                if isinstance(d, dict) and d.get("dedup_key") == key:
  1233	 16309	                    return 0        # 已記過,跳過(不算失敗)
  1234	 16310	    except OSError:
  1235	 16311	        pass
  1236	 16312	    return _jsonl_append_verified(path, rec, "dedup_key", key)
  1237	 16313	
  1238	 16314	
  1239	 16315	def cmd_ci_wait(env, timeout=1800.0, repo_dir=None, sha=None, branch=None,
  1240	 16316	                grace=30.0, as_json=False):
  1241	 16317	    """[S1] push 後同輪等 CI 結論。綠 rc0/紅 rc1/未定·逾時·no-run·工具缺席 rc0/帳寫失敗·參數錯 rc2。"""
  1242	 16318	    import json
  1243	 16319	    import datetime
  1244	 16320	    import subprocess
  1245	 16321	    import time
  1246	 16322	
  1247	 16323	    def emit(verdict, runs=None, note=None, rc=0):
  1248	 16324	        payload = {"sha": sha, "verdict": verdict, "runs": runs or []}
  1249	 16325	        if as_json:
  1250	 16326	            print(json.dumps(payload, ensure_ascii=False))
  1251	 16327	        else:
  1252	 16328	            if note:
  1253	 16329	                print(note)
  1254	 16330	            for r in (runs or []):
  1255	 16331	                print(f"CI {r.get('conclusion', '?'):<12} {r.get('workflow', '?')}"
  1256	 16332	                      f" {(r.get('sha') or '')[:7]} → {r.get('url', '')}")
  1257	 16333	                # 失敗證據必須進**文字**輸出:只塞 --json 等於人跑指令看不到任何可修的線索
  1258	 16334	                # (2026-07-29 外審實錘:README/skill/計劃都承諾會印,實作只進 json)
  1259	 16335	                if r.get("failed_step"):
  1260	 16336	                    print(f"  失敗步驟: {r['failed_step']}")
  1261	 16337	                if r.get("log_tail"):
  1262	 16338	                    print("  log 尾段:")
  1263	 16339	                    for ln in str(r["log_tail"]).splitlines():
  1264	 16340	                        print(f"    {ln}")
  1265	 16341	            print(f"→ 判定: {verdict}")
  1266	 16342	        return rc
  1267	 16343	
  1268	 16344	    root = repo_dir or _anchor_repo_root(None)
  1269	 16345	    if root is None or not Path(root).is_dir():
  1270	 16346	        print(f"擋下:--repo-dir 指的目錄不存在: {repo_dir!r}", file=sys.stderr)
  1271	 16347	        return 2
  1272	 16348	    enabled, cfg = _ci_config(root)
  1273	 16349	    if not enabled:
  1274	 16350	        return emit("disabled", note="(未宣告 .lumos/config.json 的 ci 區塊,CI 回流功能關閉)")
  1275	 16351	    def _git_out(*a):
  1276	 16352	        try:
  1277	 16353	            r = subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True,
  1278	 16354	                               timeout=30)
  1279	 16355	        except (OSError, subprocess.TimeoutExpired):
  1280	 16356	            return ""        # git 缺席/逾時也 fail-open(絕不 traceback)
  1281	 16357	        return r.stdout.strip() if r.returncode == 0 else ""
  1282	 16358	    if not sha:
  1283	 16359	        sha = _git_out("rev-parse", "HEAD") or None
  1284	 16360	    if not branch:
  1285	 16361	        branch = _git_out("rev-parse", "--abbrev-ref", "HEAD")
  1286	 16362	    if not sha:
  1287	 16363	        print("ci-wait: 取不到 HEAD sha(空 repo?),跳過", file=sys.stderr)
  1288	 16364	        return emit("unavailable")
  1289	 16365	
  1290	 16366	    deadline = time.time() + float(timeout)
  1291	 16367	    graced = 0                    # 等過幾個 grace 窗(no-run 要連等三個才下結論)
  1292	 16368	    while True:
  1293	 16369	        runs, err = _ci_list_runs(root, sha, cfg.get("workflow"))
  1294	 16370	        if runs is None:
  1295	 16371	            print(f"ci-wait: {err}(fail-open,不擋任何流程)", file=sys.stderr)
  1296	 16372	            return emit("unavailable")
  1297	 16373	        done = [r for r in runs if r.get("status") == "completed"]
  1298	 16374	        red = [r for r in done if (r.get("conclusion") or "") in _CI_RED]
  1299	 16375	        if red:                       # 任一紅即紅:立刻早退(不等其餘)
  1300	 16376	            out = []
  1301	 16377	            for r in red:
  1302	 16378	                rid = r.get("databaseId")
  1303	 16379	                out.append({"run_id": rid, "attempt": r.get("attempt", 1),
  1304	 16380	                            "workflow": r.get("workflowName", "?"), "sha": sha,
  1305	 16381	                            "conclusion": r.get("conclusion"), "url": r.get("url", ""),
  1306	 16382	                            "failed_step": _ci_failed_step(root, rid),
  1307	 16383	                            "log_tail": _ci_fail_log(root, rid)})
  1308	 16384	            rc_w = _ci_record(env, out, sha, branch)
  1309	 16385	            return rc_w if rc_w else emit("red", out, rc=1)
  1310	 16386	        if runs and len(done) == len(runs):
  1311	 16387	            if graced < 1:            # 全綠前再等一個 grace 期(晚註冊 run 緩解,非保證)
  1312	 16388	                graced += 1
  1313	 16389	                time.sleep(min(float(grace), max(0.0, deadline - time.time())))
  1314	 16390	                continue
  1315	 16391	            out = [{"run_id": r.get("databaseId"), "attempt": r.get("attempt", 1),
  1316	 16392	                    "workflow": r.get("workflowName", "?"), "sha": sha,
  1317	 16393	                    "conclusion": r.get("conclusion"), "url": r.get("url", ""),
  1318	 16394	                    "failed_step": "", "log_tail": ""} for r in done]
  1319	 16395	            rc_w = _ci_record(env, out, sha, branch)
  1320	 16396	            if rc_w:
  1321	 16397	                return rc_w
  1322	 16398	            # conclusion 三分類(計劃 [S1] 矩陣;2026-07-29 外審實錘實作只做紅/非紅二分):
  1323	 16399	            # 綠=全部落在 _CI_GREEN;非綠非紅(cancelled/action_required/stale,含未知未來值)
  1324	 16400	            # =未定,rc0 但**不得判綠**——「完成且沒紅」不等於「通過」。
  1325	 16401	            odd = [r for r in out if (r.get("conclusion") or "") not in _CI_GREEN]
  1326	 16402	            if odd:
  1327	 16403	                names = "、".join(sorted({(r.get("conclusion") or "?") for r in odd}))
  1328	 16404	                return emit("undetermined", out,
  1329	 16405	                            note=f"非成功但無失敗步驟可歸因({names}):不進修復路徑,請人判")
  1330	 16406	            return emit("green", out)
  1331	 16407	        if not runs:                  # no-run 快速路徑:等幾個 grace 窗仍零 → 收工,不白等
  1332	 16408	            # ★等一個 grace 窗不夠★(2026-09-06 實測):推送後 GitHub 註冊 run 可能要好幾分鐘,
  1333	 16409	            # 那次 14:02 推、14:15:46 才出現 run,而 ci-wait 判了 no-run。而家規明說 no-run
  1334	 16410	            # 不算過,誤報等於叫人去查一個不存在的觸發條件問題。改成連續等三個窗才下結論。
  1335	 16411	            # ★沒有完全診斷清楚★:那次 ci-wait 從 14:02 跑到 14:18 卻仍回 no-run,單靠加窗
  1336	 16412	            # 未必解釋得完(可能是 API 查詢的分支/sha 條件或回傳延遲),所以下面訊息改成講
  1337	 16413	            # 「等了多久沒看到」而不是斷言「沒有觸發」。REVISIT:2026-10-06 看帳上還有沒有 no-run。
  1338	 16414	            if graced < 3:
  1339	 16415	                graced += 1
  1340	 16416	                time.sleep(min(float(grace), max(0.0, deadline - time.time())))
  1341	 16417	                continue
  1342	 16418	            rc_w = _ci_record(env, [{"run_id": None, "attempt": 0, "workflow": "",
  1343	 16419	                                     "sha": sha, "conclusion": "no-run", "url": "",
  1344	 16420	                                     "failed_step": "", "log_tail": ""}], sha, branch)
  1345	 16421	            return rc_w if rc_w else emit(
  1346	 16422	                "no-run", note=f"等了約 {int(float(grace) * 3)} 秒仍查不到這個 sha 的 workflow run"
  1347	 16423	                                f"——可能是還沒註冊(推完馬上問常撞到)、也可能是 workflow 的 "
  1348	 16424	                                f"branch/path 條件不含這次改動。★no-run 不算過★:過幾分鐘用 "
  1349	 16425	                                f"lumos ci-status 再確認一次")
  1350	 16426	        if time.time() >= deadline:
  1351	 16427	            rc_w = _ci_record(env, [{"run_id": None, "attempt": 0, "workflow": "",
  1352	 16428	                                     "sha": sha, "conclusion": "timeout-waiting", "url": "",
  1353	 16429	                                     "failed_step": "", "log_tail": ""}], sha, branch)
  1354	 16430	            return rc_w if rc_w else emit(
  1355	 16431	                "timeout", note=f"逾時({timeout:.0f}s)未出結論,請手動查 gh run list")
  1356	 16432	        time.sleep(min(15.0, max(1.0, deadline - time.time())))
  1357	 16433	
  1358	 16434	
  1359	 16435	def _ci_record(env, rows, sha, branch):
  1360	 16436	    """把結果逐筆寫帳;任一筆寫失敗即回 rc2(自驗失敗優先於紅燈)。"""
  1361	 16437	    import datetime
  1362	 16438	    ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
  1363	 16439	    for r in rows:
  1364	 16440	        rid = r.get("run_id")
  1365	 16441	        att = r.get("attempt", 0)
  1366	 16442	        concl = r.get("conclusion") or "?"
  1367	 16443	        key = (f"{rid}:{att}:{concl}" if rid else f"nosha:{sha}:{concl}")
  1368	 16444	        rec = {"ts": ts, "run_id": rid, "attempt": att, "sha": sha, "branch": branch,
  1369	 16445	               "workflow": r.get("workflow", ""), "conclusion": concl,
  1370	 16446	               "title": r.get("title", ""), "url": r.get("url", ""),
  1371	 16447	               "failed_step": r.get("failed_step", ""), "dedup_key": key}
  1372	 16448	        rc = _ci_write(env, rec)
  1373	 16449	        if rc != 0:
  1374	 16450	            return rc
  1375	 16451	    return 0
  1376	 16452	
  1377	 16453	
  1378	 16454	def cmd_ci_status(env, repo_dir=None, as_json=False):
  1379	 16455	    """[S3] 唯讀查最後一次 CI 結果(不打網路,供離線與 hook)。恆 rc0。"""
  1380	 16456	    import json
  1381	 16457	    import datetime
  1382	 16458	    root = repo_dir or _anchor_repo_root(None)
  1383	 16459	    if root is None or not Path(root).is_dir():
  1384	 16460	        print(f"擋下:--repo-dir 指的目錄不存在: {repo_dir!r}", file=sys.stderr)
  1385	 16461	        return 2
  1386	 16462	    enabled, _cfg = _ci_config(root)
  1387	 16463	    if not enabled:
  1388	 16464	        if as_json:
  1389	 16465	            print(json.dumps({"verdict": "disabled"}, ensure_ascii=False))
  1390	 16466	        else:
  1391	 16467	            print("(未宣告 ci 區塊,CI 回流功能關閉)")
  1392	 16468	        return 0
  1393	 16469	    rows = []
  1394	 16470	    try:
  1395	 16471	        with open(_ci_log_path(env), encoding="utf-8", errors="replace") as f:
  1396	 16472	            for line in f:
  1397	 16473	                if not line.strip():
  1398	 16474	                    continue
  1399	 16475	                try:
  1400	 16476	                    d = json.loads(line)
  1401	 16477	                except ValueError:
  1402	 16478	                    continue
  1403	 16479	                if isinstance(d, dict):
  1404	 16480	                    rows.append(d)
  1405	 16481	    except OSError:
  1406	 16482	        rows = []
  1407	 16483	    # 「最後一筆」不等於「最新結論」:同一 sha 多支 workflow 各記一筆,檔尾那筆可能正好是綠的、
  1408	 16484	    # 把紅的蓋掉(2026-07-29 沿 SessionStart hook 同型修法)。取最新 sha 的**全部**筆、報最壞的。
  1409	 16485	    last = None
  1410	 16486	    if rows:
  1411	 16487	        newest_sha = rows[-1].get("sha")
  1412	 16488	        same = [r for r in rows if r.get("sha") == newest_sha] or [rows[-1]]
  1413	 16489	        last = (next((r for r in same if (r.get("conclusion") or "") in _CI_RED), None)
  1414	 16490	                or next((r for r in same if (r.get("conclusion") or "") not in _CI_GREEN), None)
  1415	 16491	                or same[-1])
  1416	 16492	    if last is None:
  1417	 16493	        if as_json:
  1418	 16494	            print(json.dumps({"verdict": "no-data"}, ensure_ascii=False))
  1419	 16495	        else:
  1420	 16496	            print("(尚無 CI 紀錄——先跑 lumos ci-wait)")
  1421	 16497	        return 0
  1422	 16498	    if as_json:
  1423	 16499	        print(json.dumps(last, ensure_ascii=False))
  1424	 16500	        return 0
  1425	 16501	    stale = ""
  1426	 16502	    try:
  1427	 16503	        age = (datetime.datetime.now().astimezone()
  1428	 16504	               - datetime.datetime.fromisoformat(last.get("ts", ""))).total_seconds()
  1429	 16505	        if age > 86400:
  1430	 16506	            stale = "  ⚠ 資料可能過期(>24h),跑 lumos ci-wait 更新"
  1431	 16507	    except (ValueError, TypeError):
  1432	 16508	        pass
  1433	 16509	    print(f"CI {last.get('conclusion', '?')} {(last.get('sha') or '')[:7]}"
  1434	 16510	          f" [{last.get('workflow', '')}] → {last.get('url', '')}"
  1435	 16511	          f"  (檢查於 {last.get('ts', '?')}){stale}")
  1436	 16512	    if last.get("failed_step"):
  1437	 16513	        print(f"  失敗步驟: {last['failed_step']}")
  1438	 16514	    return 0
  1439	 16515	
  1440	 16516	
  1441	 16517	
  1442	 16518	def _fold_mirror_sections(text):
  1443	 16519	    """掃 text 回傳所有「鏡像段」標籤清單,供 fold-check 列舉複查用。
  1444	 16520	
  1445	 16521	    鏡像段定義(設計 §2.1):
  1446	 16522	      1. frontmatter summary block → "summary"
  1447	 16523	      2. body 內每個 ```json fence → "```json fence N"(1-indexed)
  1448	 16524	      3. ## …審計修正紀錄(含節號前綴如 ## §5 審計修正紀錄)
  1449	 16525	      4. ## …誠實天花板(含節號前綴如 ## §4 誠實天花板)
  1450	 19020	
  1451	 19021	def _codeloop_read(repo_root, branch):
  1452	 19022	    """讀 governance/code-loop/<branch>.json;不存在回 None。"""
  1453	 19023	    import json
  1454	 19024	    safe = _codeloop_branch_filename(branch)
  1455	 19025	    p = Path(repo_root) / "governance" / "code-loop" / f"{safe}.json"
  1456	 19026	    if not p.exists():
  1457	 19027	        return _codeloop_read_from_ledger(repo_root, branch)
  1458	 19028	    try:
  1459	 19029	        return json.loads(p.read_text(encoding="utf-8"))
  1460	 19030	    except Exception:
  1461	 19031	        return None
  1462	 19032	
  1463	 19033	
  1464	 19034	def _codeloop_read_from_ledger(repo_root, branch):
  1465	 19035	    """marker 檔不在時(governance/code-loop/ 被 gitignore,CI 的乾淨 checkout 一定沒有)
  1466	 19036	    退而讀 tracked 的 docs/.governance-log.jsonl:取該分支最後一筆 gate=code-loop 事件,
  1467	 19037	    還原成 marker 同形 dict(status/head_sha/note)。沒有就回 None。
  1468	 19038	    2026-08-22 實紅:CI 後盾 #5 上線後第一筆 tier=high 推送因 marker 不在 checkout 而假紅。"""
  1469	 19039	    import json
  1470	 19040	    path = Path(repo_root) / "docs" / ".governance-log.jsonl"
  1471	 19041	    if not path.exists():
  1472	 19042	        return None
  1473	 19043	    last = None
  1474	 19044	    try:
  1475	 19045	        for line in path.read_text(encoding="utf-8").splitlines():
  1476	 19046	            line = line.strip()
  1477	 19047	            if not line or '"code-loop"' not in line:
  1478	 19048	                continue
  1479	 19049	            try:
  1480	 19050	                ev = json.loads(line)
  1481	 19051	            except Exception:
  1482	 19052	                continue
  1483	 19053	            if ev.get("gate") == "code-loop" and ev.get("branch") == branch and ev.get("head_sha"):
  1484	 19054	                last = ev
  1485	 19055	    except OSError:
  1486	 19056	        return None
  1487	 19057	    if last is None:
  1488	 19058	        return None
  1489	 19059	    return {"status": last.get("kind"), "head_sha": last.get("head_sha"),
  1490	 19060	            "note": last.get("detail"), "ts": last.get("ts"), "_source": "ledger"}
  1491	 19061	
  1492	 19062	
  1493	 19063	def _codeloop_write(repo_root, branch, status, note, head_sha, ts):
  1494	 19064	    """寫 governance/code-loop/<branch>.json。"""
  1495	 19065	    import json
  1496	 19066	    safe = _codeloop_branch_filename(branch)
  1497	 19067	    d = Path(repo_root) / "governance" / "code-loop"
  1498	 19068	    d.mkdir(parents=True, exist_ok=True)
  1499	 19069	    rec = {"head_sha": head_sha, "status": status, "note": note, "ts": ts}
  1500	 19070	    (d / f"{safe}.json").write_text(
  1501	 19071	        json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
  1502	 19072	
  1503	 19073	
  1504	 19074	def _codeloop_gov_log(repo_root, branch, status, note, head_sha, ts):
  1505	 19075	    """把 code-loop 事件 append 到 docs/.governance-log.jsonl(同 bypass-log 哲學)。
  1506	 19076	    vault 找不到 / 非 git repo → 靜默跳過。"""
  1507	 19077	    import json
  1508	 19078	    import subprocess
  1509	 19079	    # 找 docs 目錄(repo root 下的 docs/)
  1510	 19080	    docs = Path(repo_root) / "docs"
  1511	 19081	    if not docs.is_dir():
  1512	 19082	        return
  1513	 19083	    if not head_sha:
  1514	 19084	        return
  1515	 19085	    path = docs / ".governance-log.jsonl"
  1516	 19086	    try:
  1517	 19087	        commit_short = head_sha[:7]
  1518	 19088	        event = {
  1519	 19089	            "ts": ts, "commit": commit_short,
  1520	 19090	            "gate": "code-loop", "kind": status,
  1521	 19091	            "hard": False, "nodes": [],
  1522	 19092	            "detail": note, "branch": branch, "head_sha": head_sha,
  1523	 19093	        }
  1524	 19094	        with open(path, "a", encoding="utf-8") as f:
  1525	 19095	            f.write(json.dumps(event, ensure_ascii=False) + "\n")
  1526	 19096	    except OSError:
  1527	 19097	        pass
  1528	 19098	
  1529	 19099	
  1530	 19100	
  1531	 19101	# ── 受波及合約測試真跑閘(Projects/受波及合約測試真跑閘_計劃;design-loop bound-tests-gate-c r1 PASS)────
  1532	 19102	# 改到相依功能時,impact 固定席上的合約綁了什麼測試,在 code-loop check(pre-push 每次都呼叫)就真跑一遍;
  1533	 19103	# 紅/懸空/方法名不合法 → BLOCKED。掛在「擋」的路徑(check)不掛「記錄」的路徑(pass)——r1 架構席抓的。
  1534	 19104	# 假綠三防:①測試名要在該平台真測試集合(同 Check T);②去重鍵=解析後完整指令(同 kill);③方法名重驗同 kill。
  1535	 19105	# fail-open 四情境(無 run_cmd / diff 算不出 / 無固定席 / 固定席沒綁)都寫 gate=bound-tests 帳,零觸發看得見。
  1536	 19106	_BOUND_TESTS_WHOLE_SUITE_TIMEOUT = 600.0   # 同 kill baseline 的下限
  1537	 19107	
  1538	 19108	
  1539	 19109	def _bound_tests_log(repo_root, kind, nodes, note):
  1540	 19110	    """治理帳 gate=bound-tests(獨立 gate,kind 裸結果詞;fail-open,寫不進不影響判定)。"""
  1541	 19111	    try:
  1542	 19112	        vault = _vault_in(repo_root)
  1543	 19113	        if vault is not None:
  1544	 19114	            _append_governance_log(vault, [{"gate": "bound-tests", "kind": kind, "hard": kind == "red",
  1545	 19115	                                            "nodes": list(nodes), "note": note}])
  1546	 19116	    except Exception:
  1547	 19117	        pass
  1548	 19118	
  1549	 19119	
  1550	 19120	def _bound_tests_for_diff(repo_root, diff_range):
  1551	 19121	    """impact 固定席 → 各節點 ★INVARIANT★ 的 [test:] → (node, platform, method, status)。
  1552	 19122	    status ∈ real / dangling / fake / bad-name。回 (items, reason_if_none)。"""
  1553	 19123	    import io as _io, contextlib as _ctx, json as _json
  1554	 19124	    buf = _io.StringIO()
  1555	 19125	    try:
  1556	 19126	        with _ctx.redirect_stdout(buf), _ctx.redirect_stderr(_io.StringIO()):
  1557	 19127	            rc = cmd_impact_diff(diff_range, repo=str(repo_root), as_json=True)
  1558	 19128	    except SystemExit:
  1559	 19129	        rc = 2
  1560	 19130	    except Exception:
  1561	 19131	        rc = 2
  1562	 19132	    if rc != 0:
  1563	 19133	        return [], "diff-unavailable"
  1564	 19134	    try:
  1565	 19135	        data = _json.loads(buf.getvalue().strip().splitlines()[-1])
  1566	 19136	    except Exception:
  1567	 19137	        return [], "diff-unavailable"
  1568	 19138	    pins = [r["node"] for r in data.get("results", []) if r.get("pinned") and r.get("contract")]
  1569	 19139	    if not pins:
  1570	 19140	        return [], "no-pins"
  1571	 19141	    vault = _vault_in(repo_root)
  1572	 19142	    if vault is None:
  1573	 19143	        return [], "no-pins"
  1574	 19144	    try:
  1575	 19145	        env = Env(vault)
  1576	 19146	        _, split, default, methods_for, hay_for = _platform_test_index(repo_root)
  1577	 19147	    except Exception as e:   # 設定檔壞(多平台沒填 default_platform 等)→ fail-open 記 no-config,不能炸成假 rc1
  1578	 19148	        return [], f"no-config:{str(e)[:80]}"
  1579	 19149	    items = []
  1580	 19150	    for node in pins:
  1581	 19151	        n = env.notes.get(node) or env.notes.get(node[:-3] if node.endswith(".md") else node + ".md")
  1582	 19152	        if n is None:
  1583	 19153	            continue
  1584	 19154	        inv, _ = extract_contracts(n)
  1585	 19155	        for x in inv:
  1586	 19156	            try:
  1587	 19157	                pairs = resolve_test_refs(x, split, default)
  1588	 19158	            except ValueError as e:
  1589	 19159	                items.append((node, "?", str(e)[:60], "bad-name")); continue
  1590	 19160	            for plat, method in pairs:
  1591	 19161	                if not _KILL_METHOD_OK_RE.fullmatch(method or ""):
  1592	 19162	                    items.append((node, plat, method, "bad-name")); continue
  1593	 19163	                try:
  1594	 19164	                    mset = methods_for(plat)
  1595	 19165	                    real = method in mset or ("." in method and method.rsplit(".", 1)[-1] in mset)   # Class.Method 寫法:集合是扁平方法名
  1596	 19166	                    fake = (not real) and (method in (hay_for(plat) or ""))
  1597	 19167	                except Exception:
  1598	 19168	                    real, fake = False, False
  1599	 19169	                items.append((node, plat, method, "real" if real else ("fake" if fake else "dangling")))
  1600	 19170	    if not items:
  1601	 19171	        return [], "no-bound"
  1602	 19172	    return items, None
  1603	 19173	
  1604	 19174	
  1605	 19175	def _run_bound_tests(repo_root, items):
  1606	 19176	    """逐 (platform, method) 真跑;去重鍵=解析後完整指令。回 results[(node, plat, method, verdict, detail, secs)]。"""
  1607	 19177	    import shlex as _shlex, os as _os
  1608	 19178	    try:
  1609	 19179	        pdata = load_platforms(repo_root)
  1610	 19180	    except ValueError as e:
  1611	 19181	        return None, f"config platforms 壞: {e}"
  1612	 19182	    plats = pdata["platforms"]
  1613	 19183	    per_test = float(_os.environ.get("LUMOS_TEST_TIMEOUT", "180") or 0) or None   # 同 runner 變數;0=不限
  1614	 19184	    results, seen = [], {}
  1615	 19185	    for node, plat, method, status in items:
  1616	 19186	        if status != "real":
  1617	 19187	            results.append((node, plat, method, "red", {"dangling": "綁的測試在程式碼裡找不到(懸空)",
  1618	 19188	                                                       "fake": "綁的名字不是真的測試方法(偽證據)",
  1619	 19189	                                                       "bad-name": "測試名不合法或平台前綴未定義"}[status], 0.0))
  1620	 19190	            continue
  1621	 19191	        pentry = plats.get(plat) or {}
  1622	 19192	        run_cmd = pentry.get("run_cmd")
  1623	 19193	        if not run_cmd:
  1624	 19194	            return None, "no-config"
  1625	 19195	        whole = "{method}" not in run_cmd
  1626	 19196	        cmd = run_cmd if whole else run_cmd.replace("{method}", _shlex.quote(method))
  1627	 19197	        root = str(pentry.get("root") or repo_root)
  1628	 19198	        key = (root, cmd)
  1629	 19199	        if key in seen:
  1630	 19200	            rc, tail, secs, to = seen[key]
  1631	 19201	        else:
  1632	 19202	            timeout = max(_BOUND_TESTS_WHOLE_SUITE_TIMEOUT, per_test or 0) if whole else per_test
  1633	 19203	            rc, tail, secs, to = _kill_run(cmd, root, timeout if timeout else 10 ** 6)
  1634	 19204	            seen[key] = (rc, tail, secs, to)
  1635	 19205	        if to:
  1636	 19206	            results.append((node, plat, method, "red", f"超時(>{int(timeout)}s)", secs))
  1637	 19207	        elif rc != 0:
  1638	 19208	            results.append((node, plat, method, "red", f"rc={rc} {tail[-120:].strip()}", secs))
  1639	 19209	        else:
  1640	 19210	            results.append((node, plat, method, "green", "whole-suite" if whole else "", secs))
  1641	 19211	    return results, None
  1642	 19212	
  1643	 19213	
  1644	 19214	def _bound_tests_check(repo_root, diff_range, skip=False, skip_note=""):
  1645	 19215	    """回 dict{status, ran, red:[…], secs, reason}。status ∈ green/red/skipped/no-config/no-pins/no-bound/diff-unavailable。"""
  1646	 19216	    import os as _os
  1647	 19217	    if skip or _os.environ.get("LUMOS_SKIP_BOUND_TESTS") == "1":
  1648	 19218	        note = skip_note or ("env LUMOS_SKIP_BOUND_TESTS=1" if not skip else "")
  1649	 19219	        _bound_tests_log(repo_root, "skipped", [], note)
  1650	 19220	        return {"status": "skipped", "ran": 0, "red": [], "secs": 0.0, "reason": note}
  1651	 19221	    if str(diff_range or "").startswith("4b825dc642cb6eb9a060e54bf8d69288fbee4904"):
  1652	 19222	        # 新分支首推:pre-push 給的是 EMPTY_TREE..sha(整個 repo 當 diff),固定席=全庫合約,跟這次改動無關 → fail-open
  1653	 19223	        _bound_tests_log(repo_root, "diff-unavailable", [], "新分支首推無 merge-base,受波及範圍不可算")
  1654	 19224	        return {"status": "diff-unavailable", "ran": 0, "red": [], "secs": 0.0, "reason": "新分支首推,受波及範圍不可算(整個 repo 當 diff 沒意義);下次推送就會算"}
  1655	 19225	    items, why = _bound_tests_for_diff(repo_root, diff_range)
  1656	 19226	    if why:
  1657	 19227	        kind = why.split(":", 1)[0]
  1658	 19228	        _bound_tests_log(repo_root, kind, [], why if ":" in why else diff_range)
  1659	 19229	        return {"status": kind, "ran": 0, "red": [], "secs": 0.0, "reason": why}
  1660	 19230	    results, err = _run_bound_tests(repo_root, items)
  1661	 19231	    if results is None:
  1662	 19232	        _bound_tests_log(repo_root, "no-config", sorted({i[0] for i in items}), err)
  1663	 19233	        return {"status": "no-config", "ran": 0, "red": [], "secs": 0.0, "reason": err}
  1664	 19234	    red = [(n, p, m, d) for n, p, m, v, d, _ in results if v == "red"]
  1665	 19235	    secs = round(sum(r[5] for r in results), 1)
  1666	 19236	    ran = sum(1 for r in results if r[3] == "green")
  1667	 19237	    if red:
  1668	 19238	        _bound_tests_log(repo_root, "red", sorted({r[0] for r in red}), f"{len(red)} 紅/{len(results)}")
  1669	 19239	        return {"status": "red", "ran": ran, "red": red, "secs": secs,
  1670	 19240	                "reason": "受波及合約的測試沒過:" + ";".join(f"{n} [{m}] {d}" for n, p, m, d in red[:6])}
  1671	 19241	    _bound_tests_log(repo_root, "green", sorted({r[0] for r in results}), f"{ran} 綠 {secs}s")
  1672	 19242	    return {"status": "green", "ran": ran, "red": [], "secs": secs, "reason": f"受波及合約測試 {ran} 支全綠({secs}s)"}
  1673	 19243	
  1674	 19244	def _codeloop_guard_verdict(repo_root, diff_range=None, at_sha=None, branch=None, skip_bound=False, skip_note=""):
  1675	 19245	    """判定式:tier=high(pitfalls --diff <range> --no-lint --json)
  1676	 19246	    AND 無有效 pass/skip 留痕 → blocked=True。
  1677	 19247	    留痕座標(prepush範圍修法 #2):at_sha/branch 給了則綁該座標(hook 傳被推送 ref 的
  1678	 19248	    local_sha 與 remote_ref 分支),否則讀當前 checkout HEAD/branch(向後相容)。
  1679	 19249	    diff_range 給了則跳 merge-base 推導直接算 tier;否則沿 merge-base..HEAD 現行為。
  1680	 19250	    fail-open:pitfalls 出錯 / 非 git / 無 merge-base → tier 視作非 high(不 blocked)。
  1681	 19251	    回傳 dict{blocked:bool, reason:str, tier:str}。
  1682	 19252	    """
  1683	 19253	    import json as _json
  1684	 19254	    import subprocess as _sp
  1685	 19255	
  1686	 19256	    # 留痕比對座標:優先用傳入的(hook 綁被推送 ref),否則讀 checkout
  1687	 19257	    _codeloop_guard_verdict.last_bound = None   # 每次呼叫先清,提早 fail-open 的分支不會拿到上一輪的殘留
  1688	 19258	    marker_sha = at_sha or _codeloop_git_head(repo_root)
  1689	 19259	    marker_branch = branch or _codeloop_git_branch(repo_root)
  1690	 19260	    if not marker_sha:
  1691	 19261	        return {"blocked": False, "reason": "無法取得 HEAD sha(fail-open)", "tier": "unknown"}
  1692	 19262	
  1693	 19263	    if diff_range is None:
  1694	 19264	        # 現行為:merge-base..HEAD 推導(向後相容)
  1695	 19265	        head_sha = _codeloop_git_head(repo_root)
  1696	 19266	        mb = None
  1697	 19267	        for base_branch in ("main", "master"):
  1698	 19268	            r = _sp.run(["git", "merge-base", "HEAD", base_branch],
  1699	 19269	                        capture_output=True, text=True, cwd=str(repo_root))
  1700	 19270	            if r.returncode == 0 and r.stdout.strip():
  1701	 19271	                mb = r.stdout.strip()
  1702	 19272	                if mb == head_sha:
  1703	 19273	                    return {"blocked": False, "reason": "merge-base == HEAD(無 branch diff)", "tier": "standard"}
  1704	 19274	                break
  1705	 19275	        if not mb:
  1706	 19276	            return {"blocked": False, "reason": "無 merge-base(fail-open)", "tier": "unknown"}
  1707	 19277	        diff_range = f"{mb}..HEAD"
  1708	 19278	
  1709	 19279	    # 2.5 受波及合約測試真跑(不分 tier;紅就擋)
  1710	 19280	    bt = _bound_tests_check(repo_root, diff_range, skip=skip_bound, skip_note=skip_note)
  1711	 19281	    _codeloop_guard_verdict.last_bound = bt
  1712	 19282	    if bt["status"] == "red":
  1713	 19283	        return {"blocked": True, "reason": bt["reason"], "tier": "unknown", "bound_tests": bt}
  1714	 19284	
  1715	 19285	    # 3. 跑 pitfalls --diff <range> --no-lint --json 取 tier
  1716	 19286	    try:
  1717	 19287	        import sys as _sys
  1718	 19288	        graphctl = Path(__file__).resolve()
  1719	 19289	        r = _sp.run([_sys.executable, str(graphctl), "pitfalls",
  1720	 19290	                     "--diff", diff_range, "--no-lint", "--json",
  1721	 19291	                     "--repo", str(repo_root)],
  1722	 19292	                    capture_output=True, text=True, cwd=str(repo_root))
  1723	 19293	        if r.returncode != 0:
  1724	 19294	            return {"blocked": False, "reason": f"pitfalls 失敗(fail-open): {r.stderr.strip()[:120]}", "tier": "unknown"}
  1725	 19295	        lines = [l for l in r.stdout.splitlines() if l.strip().startswith("{")]
  1726	 19296	        if not lines:
  1727	 19297	            return {"blocked": False, "reason": "pitfalls 無 JSON 輸出(fail-open)", "tier": "unknown"}
  1728	 19298	        data = _json.loads(lines[0])
  1729	 19299	        tier = data.get("tier", "standard")
  1730	 19300	    except Exception as e:
  1731	 19301	        return {"blocked": False, "reason": f"pitfalls 例外(fail-open): {e}", "tier": "unknown"}
  1732	 19302	
  1733	 19303	    if tier != "high":
  1734	 19304	        return {"blocked": False, "reason": f"tier={tier}(非 high)", "tier": tier}
  1735	 19305	
  1736	 19306	    # 4. 讀留痕,pass/skip 且 sha == marker_sha → 有效(marker_sha/marker_branch 綁被推送 ref 或 checkout)
  1737	 19307	    rec = _codeloop_read(repo_root, marker_branch)
  1738	 19308	    if rec is not None:
  1739	 19309	        rec_sha = rec.get("head_sha", "")
  1740	 19310	        rec_status = rec.get("status", "")
  1741	 19311	        if rec_sha == marker_sha and rec_status in ("passed", "skipped"):
  1742	 19312	            _src = "治理帳" if rec.get("_source") == "ledger" else "marker"
  1743	 19313	            return {"blocked": False, "reason": f"有效留痕({rec_status}@{marker_sha[:8]},來源 {_src})", "tier": tier}
  1744	 19314	        # 簿記白名單豁免([[Issues/code-loop-pass自失效追尾]] 2026-08-04):pass 自己會往
  1745	 19315	        # tracked 的治理帳 append 一行,照「先 commit 再 push」直覺把它 commit 進去,
  1746	 19316	        # HEAD 前進 → pass 自失效 → 追尾。豁免=留痕 sha 之後的 commit ★只動簿記檔★
  1747	 19317	        # 且留痕 sha 是目標 sha 的★祖先★(改寫史拒認)→ 留痕仍有效。
  1748	 19318	        # 「HEAD 移動→作廢」的原意=pass 不得蓋到新★代碼★——任何非白名單檔一動照樣失效。
  1749	 19319	        if rec_sha and rec_sha != marker_sha and rec_status in ("passed", "skipped"):
  1750	 19320	            _WL_FILES, _WL_DIR = _BOOKKEEPING_FILES, _BOOKKEEPING_DIR
  1751	 19321	            _anc = _sp.run(["git", "merge-base", "--is-ancestor", rec_sha, marker_sha],
  1752	 19322	                           capture_output=True, text=True, cwd=str(repo_root))
  1753	 19323	            if _anc.returncode == 0:
  1754	 19324	                _df = _sp.run(["git", "diff", "--name-only", rec_sha, marker_sha],
  1755	 19325	                              capture_output=True, text=True, cwd=str(repo_root))
  1756	 19326	                _files = [f.strip() for f in _df.stdout.splitlines() if f.strip()]
  1757	 19327	                if _df.returncode == 0 and all(
  1758	 19328	                        f in _WL_FILES or f.startswith(_WL_DIR) for f in _files):
  1759	 19329	                    _src = "治理帳" if rec.get("_source") == "ledger" else "marker"
  1760	 19330	                    return {"blocked": False,
  1761	 19331	                            "reason": (f"有效留痕({rec_status}@{rec_sha[:8]},來源 {_src}+簿記豁免:"
  1762	 19332	                                       f"其後 {len(_files)} 檔皆白名單)"),
  1763	 19333	                            "tier": tier}
  1764	 19334	        # 留痕存在但 sha 不符或狀態不對
  1765	 19335	        if rec_sha != marker_sha:
  1766	governance/code-loop:
  1767	total 48
  1768	-rw-r--r--@ 1 enzo  staff  286 Jul  6 01:20 feat__claude-reinject.json
  1769	-rw-r--r--@ 1 enzo  staff  245 Jul  5 21:34 feat__codeloop-guard.json
  1770	-rw-r--r--@ 1 enzo  staff  834 Aug  1 10:11 feat__public-slim-handoff.json
  1771	-rw-r--r--@ 1 enzo  staff  440 Jul 19 21:27 feat__stack-perf-questions.json
  1772	-rw-r--r--@ 1 enzo  staff  773 Jul 17 17:05 feat__test-layers-reminder.json
  1773	-rw-r--r--@ 1 enzo  staff  256 Sep  7 14:48 main.json
  1774	git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
  1775	git: error: couldn't create cache file '/tmp/xcrun_db-tf0WWGfN' (errno=Operation not permitted)
  1776	git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
  1777	git: error: couldn't create cache file '/tmp/xcrun_db-Yd3UZtvK' (errno=Operation not permitted)
  1778	docs/.governance-log.jsonl
  1779	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s", "kind": "warned", "hard": false, "nodes": ["hook信任邊界"]}
  1780	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s", "kind": "warned", "hard": false, "nodes": ["hook逾時預算"]}
  1781	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s", "kind": "warned", "hard": false, "nodes": ["授權與歸屬"]}
  1782	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s2", "kind": "warned", "hard": false, "nodes": ["嚴謹度分配偏向機械層"]}
  1783	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s2", "kind": "warned", "hard": false, "nodes": ["主動影響幅度偵測_計劃"]}
  1784	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s2", "kind": "warned", "hard": false, "nodes": ["閘觸發帳統計_計劃"]}
  1785	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s2", "kind": "warned", "hard": false, "nodes": ["anchor-integrity"]}
  1786	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s2", "kind": "warned", "hard": false, "nodes": ["bound-tests-gate"]}
  1787	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s2", "kind": "warned", "hard": false, "nodes": ["design-loop"]}
  1788	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s2", "kind": "warned", "hard": false, "nodes": ["linter精選目錄"]}
  1789	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s2", "kind": "warned", "hard": false, "nodes": ["loop-convergence-recording"]}
  1790	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s2", "kind": "warned", "hard": false, "nodes": ["lumos-cli-read"]}
  1791	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-s2", "kind": "warned", "hard": false, "nodes": ["slim-get-一行安裝"]}
  1792	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-e3", "kind": "warned", "hard": false, "nodes": ["2026-09-03_派工攔截點實測"]}
  1793	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-e3", "kind": "warned", "hard": false, "nodes": ["2026-09-03_派工攔截點實測"]}
  1794	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-e3", "kind": "warned", "hard": false, "nodes": ["2026-09-04_Codex完全支援S0安裝層驗收"]}
  1795	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-e3", "kind": "warned", "hard": false, "nodes": ["2026-09-04_Codex完全支援S1hook適配驗收"]}
  1796	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-e3", "kind": "warned", "hard": false, "nodes": ["2026-09-04_Codex完全支援S2迴圈編排驗收"]}
  1797	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "check-e3", "kind": "warned", "hard": false, "nodes": ["2026-09-04_Codex完全支援S3量測驗收"]}
  1798	{"ts": "2026-09-07T14:50:08+08:00", "commit": "15f892e", "gate": "doctor-run", "kind": "ran", "hard": false, "nodes": [], "note": "issues=0 gates=3 soft=7"}
  1799	
  1800	exec
  1801	/bin/zsh -lc "nl -ba governance/code-loop/main.json
  1802	nl -ba docs/.ci-log.jsonl | tail -n 30
  1803	nl -ba scripts/lumos | sed -n '19034,19076p'
  1804	nl -ba scripts/lumos | sed -n '19303,19460p'
  1805	rg -n \"def cmd_code_loop|code-loop pass|choices=.*passed|status.*skipped|_codeloop_write\" scripts/lumos | tail -n 40
  1806	rg -n \"def cmd_spec_trace|spec_trace|CLAUSE|\\[S\\\\d|re\\.find.*S\" scripts/lumos | head -n 80" in /Users/enzo/harness/lumos-toolchain
  1807	 succeeded in 0ms:
  1808	     1	{
  1809	     2	  "head_sha": "15f892e9b06495e63647a71f188030e09094cfb9",
  1810	     3	  "status": "passed",
  1811	     4	  "note": "code-batch13b:同一批,補錨點簽名 commit 後重跑留痕。6 席 23 條全折、accepted 為空。全套 4162 綠。",
  1812	     5	  "ts": "2026-09-07T14:46:15+08:00"
  1813	     6	}
  1814	    88	{"ts": "2026-09-05T09:40:02+08:00", "run_id": 33936233760, "attempt": 1, "sha": "5a94b1adc955366d8d775ac62942f70370ed4f72", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/33936233760", "failed_step": "", "dedup_key": "33936233760:1:success"}
  1815	    89	{"ts": "2026-09-05T10:03:46+08:00", "run_id": 33937260619, "attempt": 1, "sha": "7ec54955de2ac769756c08f491111453d02a12cb", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/33937260619", "failed_step": "", "dedup_key": "33937260619:1:success"}
  1816	    90	{"ts": "2026-09-05T10:23:05+08:00", "run_id": 33938283719, "attempt": 1, "sha": "1992c14fccd3cd82f4c6e55e2ec8e10a402bb308", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/33938283719", "failed_step": "", "dedup_key": "33938283719:1:success"}
  1817	    91	{"ts": "2026-09-05T13:16:00+08:00", "run_id": 33946265310, "attempt": 1, "sha": "a24f4bb7e175338772c0c67701916962f2bc586e", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/33946265310", "failed_step": "", "dedup_key": "33946265310:1:success"}
  1818	    92	{"ts": "2026-09-05T16:48:38+08:00", "run_id": 33955754946, "attempt": 1, "sha": "2dc1d5ed0057c781a431c1db41967956402078d4", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/33955754946", "failed_step": "", "dedup_key": "33955754946:1:success"}
  1819	    93	{"ts": "2026-09-05T17:25:28+08:00", "run_id": 33957251373, "attempt": 1, "sha": "bea4f04e537d015eb586321d4b4793a62cc0b895", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/33957251373", "failed_step": "", "dedup_key": "33957251373:1:success"}
  1820	    94	{"ts": "2026-09-05T17:59:12+08:00", "run_id": 33959012251, "attempt": 1, "sha": "7753be7cad2fa7e8b30c1dde9e145e59c003a406", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/33959012251", "failed_step": "", "dedup_key": "33959012251:1:success"}
  1821	    95	{"ts": "2026-09-05T18:28:15+08:00", "run_id": 33960001119, "attempt": 1, "sha": "b0b40600893795a78a16c69d547c68888654790d", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/33960001119", "failed_step": "", "dedup_key": "33960001119:1:success"}
  1822	    96	{"ts": "2026-09-06T03:08:52+08:00", "run_id": 33985574220, "attempt": 1, "sha": "271dec6ed284688e9afc5c8429d305a3f26c7008", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/33985574220", "failed_step": "", "dedup_key": "33985574220:1:success"}
  1823	    97	{"ts": "2026-09-06T05:06:06+08:00", "run_id": null, "attempt": 0, "sha": "e93d1233086bd2913eafa90e4606672bccca01fd", "branch": "main", "workflow": "", "conclusion": "no-run", "title": "", "url": "", "failed_step": "", "dedup_key": "nosha:e93d1233086bd2913eafa90e4606672bccca01fd:no-run"}
  1824	    98	{"ts": "2026-09-06T05:57:22+08:00", "run_id": 33993909501, "attempt": 1, "sha": "6433dc9f2674bdaa0e297022eefbd1f9a42434d1", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/33993909501", "failed_step": "", "dedup_key": "33993909501:1:success"}
  1825	    99	{"ts": "2026-09-06T12:30:24+08:00", "run_id": 34011106448, "attempt": 1, "sha": "b1c9851dc1aa6ecca39880b42ca03fe022e68207", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34011106448", "failed_step": "", "dedup_key": "34011106448:1:success"}
  1826	   100	{"ts": "2026-09-06T13:26:57+08:00", "run_id": 34013371022, "attempt": 1, "sha": "136d9d50b2472975a8af7378a16cc6a2d0390483", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34013371022", "failed_step": "", "dedup_key": "34013371022:1:success"}
  1827	   101	{"ts": "2026-09-06T14:18:42+08:00", "run_id": null, "attempt": 0, "sha": "7bfd1a7150b1dc891f84869bdd03363a78ef8604", "branch": "main", "workflow": "", "conclusion": "no-run", "title": "", "url": "", "failed_step": "", "dedup_key": "nosha:7bfd1a7150b1dc891f84869bdd03363a78ef8604:no-run"}
  1828	   102	{"ts": "2026-09-06T14:28:45+08:00", "run_id": 34016038218, "attempt": 1, "sha": "7bfd1a7150b1dc891f84869bdd03363a78ef8604", "branch": "main", "workflow": "CI", "conclusion": "failure", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34016038218", "failed_step": "test/Full test suite", "dedup_key": "34016038218:1:failure"}
  1829	   103	{"ts": "2026-09-06T15:01:44+08:00", "run_id": 34017373701, "attempt": 1, "sha": "7542879db15b615aee3e4e12e93b89c1560c1af3", "branch": "main", "workflow": "CI", "conclusion": "failure", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34017373701", "failed_step": "test/自主迴圈測試", "dedup_key": "34017373701:1:failure"}
  1830	   104	{"ts": "2026-09-06T15:33:12+08:00", "run_id": 34018715718, "attempt": 1, "sha": "e29620c1836fcf94aed1cd7e915ddedc661761d6", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34018715718", "failed_step": "", "dedup_key": "34018715718:1:success"}
  1831	   105	{"ts": "2026-09-06T17:29:25+08:00", "run_id": 34024003908, "attempt": 1, "sha": "30dd7b5135f102d9cf8fad07da8a18afceaed086", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34024003908", "failed_step": "", "dedup_key": "34024003908:1:success"}
  1832	   106	{"ts": "2026-09-06T18:51:44+08:00", "run_id": 34027860593, "attempt": 1, "sha": "1cf59bab9596740f50a8803f15f24fa811bada58", "branch": "main", "workflow": "CI", "conclusion": "failure", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34027860593", "failed_step": "test/Anchor verify (baseline 缺失必紅)", "dedup_key": "34027860593:1:failure"}
  1833	   107	{"ts": "2026-09-06T19:33:48+08:00", "run_id": 34029830724, "attempt": 1, "sha": "065efdc138de56e0226e10ef37e716f1d85c020c", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34029830724", "failed_step": "", "dedup_key": "34029830724:1:success"}
  1834	   108	{"ts": "2026-09-06T20:38:01+08:00", "run_id": 34032858690, "attempt": 1, "sha": "58036f3d5d5e06898f52c00648c6e3a33918c5d3", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34032858690", "failed_step": "", "dedup_key": "34032858690:1:success"}
  1835	   109	{"ts": "2026-09-06T21:45:53+08:00", "run_id": 34036247495, "attempt": 1, "sha": "126c7060a67ca600152f3f876a1968f87342863f", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34036247495", "failed_step": "", "dedup_key": "34036247495:1:success"}
  1836	   110	{"ts": "2026-09-06T23:20:32+08:00", "run_id": 34041081962, "attempt": 1, "sha": "78898661c69c3caf83cabbffc525336e3d6ef373", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34041081962", "failed_step": "", "dedup_key": "34041081962:1:success"}
  1837	   111	{"ts": "2026-09-07T01:48:29+08:00", "run_id": 34048843146, "attempt": 1, "sha": "092e2e6e2150ca89123e315a692f349dee724818", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34048843146", "failed_step": "", "dedup_key": "34048843146:1:success"}
  1838	   112	{"ts": "2026-09-07T04:26:51+08:00", "run_id": 34057187025, "attempt": 1, "sha": "4096f0de0c357f461a3fac96e30fa467cd5ac73b", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34057187025", "failed_step": "", "dedup_key": "34057187025:1:success"}
  1839	   113	{"ts": "2026-09-07T06:15:29+08:00", "run_id": 34062668713, "attempt": 1, "sha": "0dc48b69055d8dee93856136d4b459864d79c5e3", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34062668713", "failed_step": "", "dedup_key": "34062668713:1:success"}
  1840	   114	{"ts": "2026-09-07T07:09:53+08:00", "run_id": 34065313967, "attempt": 1, "sha": "60f2914aa5560f4438334e01f069ef6ef5d4ff30", "branch": "main", "workflow": "CI", "conclusion": "failure", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34065313967", "failed_step": "test/Full test suite", "dedup_key": "34065313967:1:failure"}
  1841	   115	{"ts": "2026-09-07T08:33:21+08:00", "run_id": 34069329240, "attempt": 1, "sha": "08c8ec0d97024b3ca85ac74944cf00f35a4f2f18", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34069329240", "failed_step": "", "dedup_key": "34069329240:1:success"}
  1842	   116	{"ts": "2026-09-07T08:58:38+08:00", "run_id": 34070636871, "attempt": 1, "sha": "4a42dede02fea8c8468e8c29b23a06ed660f6b1d", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34070636871", "failed_step": "", "dedup_key": "34070636871:1:success"}
  1843	   117	{"ts": "2026-09-07T13:15:34+08:00", "run_id": 34085131143, "attempt": 1, "sha": "9854ba5c0b63d5a2180999b4ada6c7a0770b81e9", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34085131143", "failed_step": "", "dedup_key": "34085131143:1:success"}
  1844	 19034	def _codeloop_read_from_ledger(repo_root, branch):
  1845	 19035	    """marker 檔不在時(governance/code-loop/ 被 gitignore,CI 的乾淨 checkout 一定沒有)
  1846	 19036	    退而讀 tracked 的 docs/.governance-log.jsonl:取該分支最後一筆 gate=code-loop 事件,
  1847	 19037	    還原成 marker 同形 dict(status/head_sha/note)。沒有就回 None。
  1848	 19038	    2026-08-22 實紅:CI 後盾 #5 上線後第一筆 tier=high 推送因 marker 不在 checkout 而假紅。"""
  1849	 19039	    import json
  1850	 19040	    path = Path(repo_root) / "docs" / ".governance-log.jsonl"
  1851	 19041	    if not path.exists():
  1852	 19042	        return None
  1853	 19043	    last = None
  1854	 19044	    try:
  1855	 19045	        for line in path.read_text(encoding="utf-8").splitlines():
  1856	 19046	            line = line.strip()
  1857	 19047	            if not line or '"code-loop"' not in line:
  1858	 19048	                continue
  1859	 19049	            try:
  1860	 19050	                ev = json.loads(line)
  1861	 19051	            except Exception:
  1862	 19052	                continue
  1863	 19053	            if ev.get("gate") == "code-loop" and ev.get("branch") == branch and ev.get("head_sha"):
  1864	 19054	                last = ev
  1865	 19055	    except OSError:
  1866	 19056	        return None
  1867	 19057	    if last is None:
  1868	 19058	        return None
  1869	 19059	    return {"status": last.get("kind"), "head_sha": last.get("head_sha"),
  1870	 19060	            "note": last.get("detail"), "ts": last.get("ts"), "_source": "ledger"}
  1871	 19061	
  1872	 19062	
  1873	 19063	def _codeloop_write(repo_root, branch, status, note, head_sha, ts):
  1874	 19064	    """寫 governance/code-loop/<branch>.json。"""
  1875	 19065	    import json
  1876	 19066	    safe = _codeloop_branch_filename(branch)
  1877	 19067	    d = Path(repo_root) / "governance" / "code-loop"
  1878	 19068	    d.mkdir(parents=True, exist_ok=True)
  1879	 19069	    rec = {"head_sha": head_sha, "status": status, "note": note, "ts": ts}
  1880	 19070	    (d / f"{safe}.json").write_text(
  1881	 19071	        json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
  1882	 19072	
  1883	 19073	
  1884	 19074	def _codeloop_gov_log(repo_root, branch, status, note, head_sha, ts):
  1885	 19075	    """把 code-loop 事件 append 到 docs/.governance-log.jsonl(同 bypass-log 哲學)。
  1886	 19076	    vault 找不到 / 非 git repo → 靜默跳過。"""
  1887	 19303	    if tier != "high":
  1888	 19304	        return {"blocked": False, "reason": f"tier={tier}(非 high)", "tier": tier}
  1889	 19305	
  1890	 19306	    # 4. 讀留痕,pass/skip 且 sha == marker_sha → 有效(marker_sha/marker_branch 綁被推送 ref 或 checkout)
  1891	 19307	    rec = _codeloop_read(repo_root, marker_branch)
  1892	 19308	    if rec is not None:
  1893	 19309	        rec_sha = rec.get("head_sha", "")
  1894	 19310	        rec_status = rec.get("status", "")
  1895	 19311	        if rec_sha == marker_sha and rec_status in ("passed", "skipped"):
  1896	 19312	            _src = "治理帳" if rec.get("_source") == "ledger" else "marker"
  1897	 19313	            return {"blocked": False, "reason": f"有效留痕({rec_status}@{marker_sha[:8]},來源 {_src})", "tier": tier}
  1898	 19314	        # 簿記白名單豁免([[Issues/code-loop-pass自失效追尾]] 2026-08-04):pass 自己會往
  1899	 19315	        # tracked 的治理帳 append 一行,照「先 commit 再 push」直覺把它 commit 進去,
  1900	 19316	        # HEAD 前進 → pass 自失效 → 追尾。豁免=留痕 sha 之後的 commit ★只動簿記檔★
  1901	 19317	        # 且留痕 sha 是目標 sha 的★祖先★(改寫史拒認)→ 留痕仍有效。
  1902	 19318	        # 「HEAD 移動→作廢」的原意=pass 不得蓋到新★代碼★——任何非白名單檔一動照樣失效。
  1903	 19319	        if rec_sha and rec_sha != marker_sha and rec_status in ("passed", "skipped"):
  1904	 19320	            _WL_FILES, _WL_DIR = _BOOKKEEPING_FILES, _BOOKKEEPING_DIR
  1905	 19321	            _anc = _sp.run(["git", "merge-base", "--is-ancestor", rec_sha, marker_sha],
  1906	 19322	                           capture_output=True, text=True, cwd=str(repo_root))
  1907	 19323	            if _anc.returncode == 0:
  1908	 19324	                _df = _sp.run(["git", "diff", "--name-only", rec_sha, marker_sha],
  1909	 19325	                              capture_output=True, text=True, cwd=str(repo_root))
  1910	 19326	                _files = [f.strip() for f in _df.stdout.splitlines() if f.strip()]
  1911	 19327	                if _df.returncode == 0 and all(
  1912	 19328	                        f in _WL_FILES or f.startswith(_WL_DIR) for f in _files):
  1913	 19329	                    _src = "治理帳" if rec.get("_source") == "ledger" else "marker"
  1914	 19330	                    return {"blocked": False,
  1915	 19331	                            "reason": (f"有效留痕({rec_status}@{rec_sha[:8]},來源 {_src}+簿記豁免:"
  1916	 19332	                                       f"其後 {len(_files)} 檔皆白名單)"),
  1917	 19333	                            "tier": tier}
  1918	 19334	        # 留痕存在但 sha 不符或狀態不對
  1919	 19335	        if rec_sha != marker_sha:
  1920	 19336	            reason = f"tier=high 且留痕 sha 過時(留痕={rec_sha[:8]} 目標={marker_sha[:8]};非純簿記增量)"
  1921	 19337	        else:
  1922	 19338	            reason = f"tier=high 且留痕狀態無效({rec_status!r})"
  1923	 19339	        return {"blocked": True, "reason": reason, "tier": tier}
  1924	 19340	
  1925	 19341	    # 5. 無留痕
  1926	 19342	    return {"blocked": True, "reason": "tier=high 且無留痕(尚未跑 code-loop pass/skip)", "tier": tier}
  1927	 19343	
  1928	 19344	
  1929	 19345	def cmd_code_loop(subcmd, note=None, repo=None, as_json=False, diff_range=None, at_sha=None, marker_branch=None, skip_bound=False):
  1930	 19346	    """code-loop 留痕讀寫。
  1931	 19347	    pass  → status=passed(綁 HEAD sha);
  1932	 19348	    skip  → status=skipped(綁 HEAD sha,留逃生痕);
  1933	 19349	    check → 跑判定式回報 verdict(blocked=tier=high∧無有效留痕);--json 輸出 verdict dict。
  1934	 19350	    rc: 0=OK / 1=check:blocked / 2=參數錯。
  1935	 19351	    """
  1936	 19352	    # resolve repo root
  1937	 19353	    if repo is not None:
  1938	 19354	        repo_root = Path(repo)
  1939	 19355	        if not repo_root.is_dir():
  1940	 19356	            print(f"擋下:--repo 指的不是目錄: {repo}", file=sys.stderr)
  1941	 19357	            return 2
  1942	 19358	    else:
  1943	 19359	        repo_root = None
  1944	 19360	        for cand in (Path.cwd(), *Path.cwd().parents):
  1945	 19361	            if (cand / ".git").exists():
  1946	 19362	                repo_root = cand
  1947	 19363	                break
  1948	 19364	        if repo_root is None:
  1949	 19365	            print("擋下:找不到 git 專案根目錄,用 --repo 指定", file=sys.stderr)
  1950	 19366	            return 2
  1951	 19367	
  1952	 19368	    branch = _codeloop_git_branch(repo_root)
  1953	 19369	    head_sha = _codeloop_git_head(repo_root)
  1954	 19370	    if not head_sha:
  1955	 19371	        print("擋下:問不到目前的 git 版本號(git 指令失敗?)", file=sys.stderr)
  1956	 19372	        return 2
  1957	 19373	    ts = _codeloop_git_ts(repo_root)
  1958	 19374	
  1959	 19375	    if subcmd in ("pass", "skip"):
  1960	 19376	        status = "passed" if subcmd == "pass" else "skipped"
  1961	 19377	        _codeloop_write(repo_root, branch, status, note or "", head_sha, ts)
  1962	 19378	        _codeloop_gov_log(repo_root, branch, status, note or "", head_sha, ts)
  1963	 19379	        label = "✅" if status == "passed" else "⏭"
  1964	 19380	        what = "審查通過,已留痕" if status == "passed" else "刻意跳過審查,已留痕"
  1965	 19381	        print(f"{label} code-loop {status}:{what}(分支 {branch},版本 {head_sha[:8]})" + (f"——{note}" if note else ""))
  1966	 19382	        print("  這筆紀錄只認目前這個版本:之後再改任何程式碼(工具自己的紀錄檔除外)它就失效,要重跑一次 pass 或 skip。")
  1967	 19383	        return 0
  1968	 19384	
  1969	 19385	    if subcmd == "check":
  1970	 19386	        # Task 2: 完整判定式(tier-high∧無有效留痕 → blocked)
  1971	 19387	        import json as _cljson
  1972	 19388	        if skip_bound and not (note or "").strip():
  1973	 19389	            print("擋下:--skip-bound-tests 要帶 --note 寫為什麼不跑受波及合約的測試(會進治理帳被統計)", file=sys.stderr)
  1974	 19390	            return 2
  1975	 19391	        verdict = _codeloop_guard_verdict(repo_root, diff_range=diff_range,
  1976	 19392	                                          at_sha=at_sha, branch=marker_branch,
  1977	 19393	                                          skip_bound=skip_bound, skip_note=note or "")
  1978	 19394	        bt = getattr(_codeloop_guard_verdict, "last_bound", None)
  1979	 19395	        if bt is not None and "bound_tests" not in verdict:
  1980	 19396	            verdict["bound_tests"] = bt
  1981	 19397	        blocked = verdict["blocked"]
  1982	 19398	        reason = verdict["reason"]
  1983	 19399	        tier = verdict["tier"]
  1984	 19400	        if as_json:
  1985	 19401	            print(_cljson.dumps(verdict, ensure_ascii=False))
  1986	 19402	        else:
  1987	 19403	            if blocked:
  1988	 19404	                print(f"⚠ code-loop check: BLOCKED——這次高風險改動還不能推(分支 {branch},版本 {head_sha[:8]}):{reason}",
  1989	 19405	                      file=sys.stderr)
  1990	 19406	            else:
  1991	 19407	                print(f"✅ code-loop check: OK——可以推(分支 {branch},版本 {head_sha[:8]},tier={tier}):{reason}")
  1992	 19408	            if bt is not None:
  1993	 19409	                _st = bt.get("status")
  1994	 19410	                if _st in ("green", "red"):
  1995	 19411	                    print(f"  受波及合約測試:{bt.get('reason')}", file=sys.stderr if _st == "red" else sys.stdout)
  1996	 19412	                    if _st == "red":
  1997	 19413	                        print("  真的跑不了(外部 DB 不在、環境缺)→ 留痕跳過:\n    lumos code-loop check --diff <範圍> --skip-bound-tests --note \"<為什麼>\"", file=sys.stderr)
  1998	 19414	                elif _st == "no-config":
  1999	 19415	                    print("  提醒:這個專案沒設測試指令(.lumos/config.json 的 test.run_cmd),受波及合約的測試沒有跑——合約測試閘等於沒開。")
  2000	 19416	        return 1 if blocked else 0
  2001	 19417	
  2002	 19418	    print(f"擋下:沒有 {subcmd!r} 這個子命令", file=sys.stderr)
  2003	 19419	    return 2
  2004	 19420	
  2005	 19421	
  2006	 19422	
  2007	 19423	# ── 每個子指令「這是幹嘛 / 什麼時候用」(Projects/工具鏈補強十件_計劃 #3)──────────
  2008	 19424	# 來源=skills/lumos-project-notes/commands/ 索引子檔的情境欄;建完 parser 由 _fill_help_when 灌進
  2009	 19425	# 每個子指令的 description,讓 `lumos X --help` 第一行就講人話。t_every_subcommand_has_when 釘非空。
  2010	 19426	HELP_WHEN = {
  2011	 19427	    "doctor": "整個圖譜健不健康。收工前跑;紅的段先修,--verbose 看全部提醒,--ci 給 pre-push 和 CI 用。",
  2012	 19428	    "links": "這篇筆記連出去哪些筆記。改上游前看下游用。",
  2013	 19429	    "backlinks": "哪些筆記連到這篇。想知道「誰依賴它」的時候。",
  2014	 19430	    "map": "以某篇為中心把關係展成樹。想看這一帶長什麼樣。",
  2015	 19431	    "context": "進場第一步之二:這篇的來龍去脈、合約、前提、鄰居一次攤開。search 定位到之後用。",
  2016	 19432	    "show": "讀一篇筆記全文。search 只給索引行,下結論前要用它讀全文。",
  2017	 19433	    "contracts": "動某模組前看有什麼不能碰:列出標成 ★INVARIANT★ / ★DEBT★ 的規則與綁的測試。",
  2018	 19434	    "lint": "剛寫完一篇,確認沒寫壞(欄位、標籤、合約標記)。比 doctor 快,只看這篇。",
  2019	 19435	    "gov": "這篇或這段時間被哪幾道閘攔過。--stats 給純數字表。",
  2020	 19436	    "canary": "審查迴圈的記帳:record 記一輪結果,second 找人覆核某一筆。",
  2021	 19437	    "second": "覆核某一筆審查判定,必須換不同的人。",
  2022	 19438	    "record": "記一輪審查結果:誰審的、嚴重度、幾條發現、各自怎麼處置、審的是哪份文件(指紋)。",
  2023	 19439	    "severity-check": "懷疑某席帳面嚴重度跟報告對不上(低報)時,對單筆帳列機械對帳;歷史帳 advisory、新帳抓到=寫側 bug 開 Issue。",
  2024	 19440	    "decision-refs": "decision_refs 自動養成 T3:AI 回填舊筆記背書哪條決策。backlog 列該補的、candidates 列候選、add-ai 寫 AI 欄、promote 人工蓋章升級。",
  2025	 19441	    "backlog": "列該跑 suggest 的節點(結構可達候選還沒填完的)。回填一批的起點。",
  2026	 19442	    "candidates": "列某節點的候選決策(它 typed 邊指到的節點的決策),Claude 讀內容判實作哪條。",
  2027	 19443	    "add-ai": "把 Claude 判定的 decision_ref 寫進 decision_refs_ai(標 by:ai;E3 生效、抑制不了 E2)。",
  2028	 19444	    "promote": "人抽查後把 AI 填的 ref 蓋章升進正欄(升級成可抑制 E2);dangling 拒、印覆蓋提醒。",
  2029	 19445	    "loop": "審查迴圈的查詢:list 先看有哪些編號開著、next 問下一步、status 問過不過、verify-progress 只讀帳本、canary-stats 看歷史抓漏率。",
  2030	 19446	    "status": "這個審查編號過關了沒。多人審加 --panel,嚴格處置閘加 --disposal,單人 --light,結清模式 --settle。",
  2031	 19447	    "compress": "長跑的審查上下文太長,規則式壓成三欄。",
  2032	 19448	    "verify-progress": "不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)。",
  2033	 19449	    "next": "每輪開頭問:第幾輪、要幾人、派誰、怎麼記帳。第一次一定帶 --tier。",
  2034	 19450	    "list": "先看有哪些審查編號還開著——next/status/verify-progress 都要編號,這支給你編號。",
  2035	 19451	    "canary-stats": "各審查員歷史抓到/漏掉比率。觀測用,不影響過不過。",
  2036	 19452	    "replay": "收斂後把判定凍成標準答案(--freeze),或懷疑判定邏輯/帳被動過時對閉包重算比對(--golden)。週跑自動抽查也走它。",
  2037	 19453	    "capture-counts": "多個找錯工具的結果合併估漏網,吐給 record --capture-counts。",
  2038	 19454	    "guard": "合約綁測試那一套:list 看狀態、scaffold 產骨架、bind 綁上、audit 留審計、trace 看證據鏈、kill 驗殺傷力。",
  2039	 19455	    "list": "每條合約綁測試的狀態:真綁 / 懸空 / 偽證據 / 裸 / 未審。",
  2040	 19456	    "scaffold": "幫某條合約產一個測試骨架(預設紅燈,斷言留 TODO)。",
  2041	 19457	    "prune": "剪掉填錯的 decision_ref(正規化定位;--by 移該欄、無 --by 兩欄都移)。",
  2042	 19458	    "bind": "把寫好的測試綁回合約的 KEY 行([test:])。別手改。",
  2043	 19459	    "audit": "某條合約被不知道脈絡的人審過了,留 [audit:] 戳記。",
  2044	 19460	    "trace": "某條合約 → 守衛測試 → 驗證紀錄的證據鏈,反向可查爆炸半徑。",
  2045	5430:# REVISIT:2026-11-07 正解是讓 code-loop pass/skip 收一個 --loop 參數、把編號寫進 nodes,
  2046	18825:        bound_status = "skipped-no-config"
  2047	18969:        bound_status = "skipped-no-config"
  2048	19063:def _codeloop_write(repo_root, branch, status, note, head_sha, ts):
  2049	19215:    """回 dict{status, ran, red:[…], secs, reason}。status ∈ green/red/skipped/no-config/no-pins/no-bound/diff-unavailable。"""
  2050	19220:        return {"status": "skipped", "ran": 0, "red": [], "secs": 0.0, "reason": note}
  2051	19311:        if rec_sha == marker_sha and rec_status in ("passed", "skipped"):
  2052	19319:        if rec_sha and rec_sha != marker_sha and rec_status in ("passed", "skipped"):
  2053	19342:    return {"blocked": True, "reason": "tier=high 且無留痕(尚未跑 code-loop pass/skip)", "tier": tier}
  2054	19345:def cmd_code_loop(subcmd, note=None, repo=None, as_json=False, diff_range=None, at_sha=None, marker_branch=None, skip_bound=False):
  2055	19348:    skip  → status=skipped(綁 HEAD sha,留逃生痕);
  2056	19376:        status = "passed" if subcmd == "pass" else "skipped"
  2057	19377:        _codeloop_write(repo_root, branch, status, note or "", head_sha, ts)
  2058	20205:        ("skip", "顯式跳過 code-loop 並留痕(status=skipped;同 bypass 哲學)"),
  2059	546:    """改制回測 [S1/S2](2026-08-26):gate 判定回放。
  2060	1241:    # [S3] 中心性重驗排程:兩清單各自按 PR 降冪重排(僅顯示序;gov 寫入序=上方掃描迴圈,不動)
  2061	1553:    #   設計見 Projects/關係層傳播守衛_計劃 [S6](phase-1 MVP,免前置、純 frontmatter)。
  2062	1579:    #   本就掃全圖,補網不需;主網 proactive 連鎖才需 P0)。設計見 Projects/關係層傳播守衛_計劃 [S7]。
  2063	1753:    #   設計見 Projects/關係層主網_實作計畫 M1;取代母計劃 [S8] 的高噪音 advisory。
  2064	2138:    # Check F: linter 宣告檔健康(lint接線收口 [S1]:SARIF 橋最後一哩——宣告了跑不動的
  2065	3764:SPEC_CLAUSE_RE = re.compile(r"\[S(\d+)\]")
  2066	3767:def cmd_spec_trace(env, node, as_json=False):
  2067	3781:    ids = sorted({int(m) for m in SPEC_CLAUSE_RE.findall(text)})
  2068	3787:            print(f"(opt-in 未啟用) {rel} 無 [SN] 條款標記——要追溯就在規格 bullet 加 [S1]/[S2]…")
  2069	3797:        # 已知設計限制:多計劃 Verification 提及 [S1] 會同時記入兩計劃的 S1
  2070	3803:        for m in SPEC_CLAUSE_RE.findall(vtext):
  2071	4068:         # [S2] second 行的 verdict/ref 併進 detail(否則分歧訊號在治理帳全程隱形)
  2072	4170:        # [S2] 第二判者分帳(否則 overturn 分歧只在 detail 字串裡、看不到彙總)
  2073	4247:# 嚴重度綁定機械掃 [S1](2026-08-26):severity 值序單一常數——原三處字面複製
  2074	4250:# 生效日:只給讀側([S2] 歷史掃分新舊帳)消費;寫側每筆 ts 天生=now 恆為「新」,
  2075	4255:# 改制回測 [S2]:判定制度版本常數——d5 判定語意改版就 bump;golden 閉包記它,
  2076	4342:    定位=第二層縱深:生效日(2026-08-26)前的歷史帳=advisory;生效日後抓到低報=寫側 [S1]
  2077	4370:        tag = "這筆是生效日後的新帳——寫側本應拒帳,代表 [S1] 有 bug,開 Issue 攤人" if era_new else "歷史帳(生效日前),寫側不溯及"
  2078	4373:        tag = "生效日後的新帳不該掃不出宣告行(寫側本應拒帳)——查 [S1]" if era_new else "歷史帳相容:格式無法機械驗,僅提醒"
  2079	4462:        # 改制回測 [S2]①(2026-08-26):spec 路徑一併入帳——replay --freeze 補漏靠它反查
  2080	4494:    # 為什麼開新欄——[S4] 七天彙總要機器回讀「這輪怎麼收+花多少」;塞 note 散文是
  2081	4647:    # ── 嚴重度綁定機械掃 [S1] 寫側強制(2026-08-26)★行為改變★:審查席帳列
  2082	4783:    """[S1 oracle品質包] append 一行 JSONL + 讀回自驗(成功宣稱與證據綁死)。
  2083	4814:    """[S2 oracle品質包] canary 判定的第二判者留痕(抽樣分權,telemetry-only)。
  2084	4815:    走 [S1] 同一自驗 helper(唯一鍵=自身新 token);loop status 天然忽略(second 行無 loop 欄)。
  2085	5379:    """[S2] 結構化壓縮(結清式收斂_計劃,2026-07-28):長跑上下文不交通用摘要——規則式三欄:
  2086	5824:    """[S3] 獨立進度驗證器(結清式收斂_計劃,2026-07-28):看不到被審材料的覆核原語——
  2087	5904:    """settle 收斂閘([S1] 結清式收斂_計劃,2026-07-28):清單全結清 ∧ G1 refcheck ∧ G3(末筆 result=現檔)。
  2088	6150:        # [S1] rc2 互斥/前置群(fail-closed;結清式收斂_計劃 2026-07-28)
  2089	6554:    roster對帳併入問閘 [S1]:only_rid=只對這一輪(同時抑制內部 dispatch glob 補漏——問閘尾端用);
  2090	7636:    """[S3 oracle品質包] 保留完整輸出供歸因(上限 256KB;超限取頭尾各半、對齊換行邊界
  2091	7654:    """[S3] 歸因:綁定測試名的任一出現處,其行起(含同行)5 行窗內有失敗標記,
  2092	7723:                      file=(sys.stderr if as_json else sys.stdout))   # [S3] --json 純度
  2093	7764:                  file=(sys.stderr if as_json else sys.stdout))   # [S3] --json 純度:診斷一律 stderr
  2094	7829:                    # [S3] timeout 降弱證據(不再計 killed):掛掉可能是環境非變異
  2095	7909:        # [S3] 措辭收斂:「咬得住」只配全強殺;混弱證據分列(unattributed+timeout 同桶)
  2096	8461:    """[S1] 中心性/PPR helper(中心性重驗排程_計劃+檢索PPR邊權_計劃,2026-07-28):
  2097	8586:    # bare 模式:風險加權排序([S2][S3] 中心性重驗排程_計劃;--legacy 保字母序=舊行為)
  2098	10661:    多跳/visited 交 [S4] 編排(resume/判斷閘)。回 (neighbors=[(src,etype,invariant數)], ambigs=[(字面,候選數)])。"""
  2099	12931:        # roster對帳併入問閘 [S1]:問閘當輪異常轉述(異常才發聲;advisory 恆不動 rc)。
  2100	12940:                # 留痕([S1c]):收集完、印完才一次性寫;寫入自身再包一層,失敗只損留痕不吞輸出(r3 e-f3)
  2101	12953:        # 嚴重度綁定機械掃 [S3](2026-08-26):問閘收尾對判定輪逐席跑第二層 severity 對帳。
  2102	12956:        # 生效日後的帳列抓到低報=寫側 [S1] 有 bug(本應拒帳)——轉述+指路開 Issue,converged 不自動撤。
  2103	13081:    """[S1 連結缺失補全,2026-08-07](plan:Projects/連結缺失補全_計劃;borrow TLR 離線候選
  2104	13229:    """[S1 有講沒做對帳,2026-08-06](plan:Projects/驗證層自證三件_計劃;borrow evidra
  2105	13990:    共用的單一實作(lint接線收口 [S1]②:I/O+parse+驗證不留兩份會漂移的複本)。
  2106	16198:# conclusion 三分類(計劃 [S1] 矩陣)。**白名單制**:綠只認列舉值,非綠非紅一律「未定」——
  2107	16317:    """[S1] push 後同輪等 CI 結論。綠 rc0/紅 rc1/未定·逾時·no-run·工具缺席 rc0/帳寫失敗·參數錯 rc2。"""
  2108	16398:            # conclusion 三分類(計劃 [S1] 矩陣;2026-07-29 外審實錘實作只做紅/非紅二分):
  2109	16455:    """[S3] 唯讀查最後一次 CI 結果(不打網路,供離線與 hook)。恆 rc0。"""
  2110	16725:    # [S1] 設計審收斂重定義(2026-08-25):保守首版,寧漏勿噪;詞表在下一個真實設計迴圈([S6])校準
  2111	16734:    """spec 白話健檢([S1] 設計審收斂重定義 2026-08-25):掃中文模糊措辭。
  2112	18926:    for m in re.findall(r"\[\[((?:Systems|Issues)/[^\]|#]+)", text):
  2113	19772:    lc = lsub.add_parser("compress", help="[S2] 結構化壓縮:長跑上下文規則式三欄(白名單壓不掉/證據/未結)")
  2114	19775:    lv = lsub.add_parser("verify-progress", help="[S3] 獨立進度驗證器:直讀帳只吃結構欄位,散文注入免疫")
  2115	20166:    p = sub.add_parser("seat-check", help="[S1 有講沒做對帳] 席報告對 dispatch manifest:unreported/out_of_scope(vault-free;觀測恆 rc0/輸入壞損 rc2)")
  2116	20417:        return cmd_spec_trace(env, args.node, as_json=args.st_json)
  2117	20623:            #   (M4 [S1] 觸發端將在此用 decision_id 呼 cascade_surface——屆時包獨立 try/except)
  2118	
  2119	exec
  2120	/bin/zsh -lc "nl -ba scripts/lumos | sed -n '3748,3812p'
  2121	nl -ba scripts/lumos | sed -n '9920,10030p'
  2122	rg -n \"reindex.*decision|decision.*reindex|def cmd_reindex|next.*id|preserv|保留原 id\" scripts/lumos scripts/test_lumos.py | head -n 120
  2123	nl -ba governance/review-reports/進度從提交推導/r1-snapshot.md | sed -n '163,215p'" in /Users/enzo/harness/lumos-toolchain
  2124	 succeeded in 0ms:
  2125	  3748	                "寫不出來就八成只是某個模組的個別設計,★請改寫成限定範圍★"
  2126	  3749	                "(誤報可加 [test:] 或改寫語氣消音)")
  2127	  3750	
  2128	  3751	    if not errs and not warns:
  2129	  3752	        print(f"✓ lint {rel} — 0 問題")
  2130	  3753	        return 0
  2131	  3754	    print(f"lint {rel}")
  2132	  3755	    for e in errs:
  2133	  3756	        print(f"  ✗ {e}")
  2134	  3757	    for w in warns:
  2135	  3758	        print(f"  ⚠ {w}")
  2136	  3759	    print(f"\n{len(errs)} error / {len(warns)} warning"
  2137	  3760	          + ("(error 不修,提交會被擋)" if errs else "(warning 不擋,但建議順手補)"))
  2138	  3761	    return 1 if errs else 0
  2139	  3762	
  2140	  3763	
  2141	  3764	SPEC_CLAUSE_RE = re.compile(r"\[S(\d+)\]")
  2142	  3765	
  2143	  3766	
  2144	  3767	def cmd_spec_trace(env, node, as_json=False):
  2145	  3768	    """條款級追溯(RTM 輕量版):計劃 body 的 [SN] 條款 × 回指 Verification 的認領。
  2146	  3769	    rc:全認領=0;有未認領=1;計劃無 [SN] 標記=0(opt-in 未啟用)。唯讀。"""
  2147	  3770	    import json
  2148	  3771	    rel = env.find(node)
  2149	  3772	    if rel is None:
  2150	  3773	        print(f"擋下:圖譜裡找不到叫 {node} 的筆記,先確認名稱或路徑(lumos search <關鍵字> 可以找)", file=sys.stderr)
  2151	  3774	        return 2
  2152	  3775	    plan_stem = env.notes[rel].stem
  2153	  3776	    try:
  2154	  3777	        text = (env.vault / rel).read_text(encoding="utf-8-sig")
  2155	  3778	    except OSError as ex:
  2156	  3779	        print(f"擋下:{ex}", file=sys.stderr)
  2157	  3780	        return 2
  2158	  3781	    ids = sorted({int(m) for m in SPEC_CLAUSE_RE.findall(text)})
  2159	  3782	    if not ids:
  2160	  3783	        if as_json:
  2161	  3784	            print(json.dumps({"plan": rel, "clauses": {}, "unclaimed": [],
  2162	  3785	                              "opt_in": False}, ensure_ascii=False))
  2163	  3786	        else:
  2164	  3787	            print(f"(opt-in 未啟用) {rel} 無 [SN] 條款標記——要追溯就在規格 bullet 加 [S1]/[S2]…")
  2165	  3788	        return 0
  2166	  3789	    claims = {i: [] for i in ids}
  2167	  3790	    for vrel, n in env.notes.items():
  2168	  3791	        if not vrel.startswith("Verification/"):
  2169	  3792	            continue
  2170	  3793	        prs = n.fields.get("plan_refs")
  2171	  3794	        prs = prs if isinstance(prs, list) else ([prs] if prs else [])
  2172	  3795	        if not any(plan_stem in str(x) for x in prs):
  2173	  3796	            continue   # 沒回指本計劃的提及不算認領(防偶然文字)
  2174	  3797	        # 已知設計限制:多計劃 Verification 提及 [S1] 會同時記入兩計劃的 S1
  2175	  3798	        # (條款 ID 只有數字無計劃域)——一篇 Verification 盡量只回指一個計劃
  2176	  3799	        try:
  2177	  3800	            vtext = (env.vault / vrel).read_text(encoding="utf-8-sig")
  2178	  3801	        except OSError:
  2179	  3802	            continue
  2180	  3803	        for m in SPEC_CLAUSE_RE.findall(vtext):
  2181	  3804	            i = int(m)
  2182	  3805	            if i in claims:
  2183	  3806	                claims[i].append(vrel)
  2184	  3807	    unclaimed = [i for i in ids if not claims[i]]
  2185	  3808	    if as_json:
  2186	  3809	        print(json.dumps({"plan": rel, "clauses": {f"S{i}": claims[i] for i in ids},
  2187	  3810	                          "unclaimed": [f"S{i}" for i in unclaimed]}, ensure_ascii=False))
  2188	  3811	    else:
  2189	  3812	        for i in ids:
  2190	  9920	            # [M1/R12] 選擇端唯一命中:first-match 會「先改錯項、再用錯項 id 精確驗證它改成功」
  2191	  9921	            cands = "; ".join(first_line(fm[st].split("content:", 1)[-1].strip(), 40)
  2192	  9922	                              for (st, _) in hits[:5])
  2193	  9923	            raise ValueError(f"「{match}」命中 {len(hits)} 條決策,分不清要改哪條,不敢亂猜。"
  2194	  9924	                             f"候選: {cands} …改用更長的片段,或用 --match \"#dN\" 指定編號")
  2195	  9925	    st, en = hits[0]
  2196	  9926	    valid_line = None
  2197	  9927	    for i in range(st, en + 1):
  2198	  9928	        if re.match(rf"^{pad}valid:\s", fm[i]):   # 只認精確 sub_indent(Bug5:移除過寬 fallback,免誤命中子清單)
  2199	  9929	            valid_line = i
  2200	  9930	            break
  2201	  9931	    if valid_line is None:
  2202	  9932	        raise ValueError("這條決策沒有 valid 欄位(或縮排不是兩個空白),工具不敢自動翻案,請手動處理或先修結構")
  2203	  9933	    # Bug3: 已 superseded 不重插(免重複鍵)。同 sub_indent 已有 superseded_by → 拒
  2204	  9934	    for i in range(st, en + 1):
  2205	  9935	        if re.match(rf"^{pad}superseded_by:\s", fm[i]):
  2206	  9936	            raise ValueError("這條決策已經被翻案過了(有 superseded_by),不重複翻;要改成被誰取代請手動編輯")
  2207	  9937	    fm[valid_line] = f"{pad}valid: false"
  2208	  9938	    # [P1] ended 選填 → 缺則自動補今日(E2 時序法要 ended 才判得了「鄰居晚於翻案沒?」)
  2209	  9939	    if not ended:
  2210	  9940	        ended = datetime.date.today().isoformat()
  2211	  9941	    ins = [f"{pad}superseded_by: {_fmt_decision_value(by)}", f"{pad}ended: {ended}"]
  2212	  9942	    fm[valid_line + 1:valid_line + 1] = ins
  2213	  9943	    # [P1] supersede = 對本節點的實質編輯 → 同步 bump 頂層 updated(單次 atomic,同一份 fm;
  2214	  9944	    #   不串第二個寫命令避免半完成)。有則就地換、無則插在 decisions: 前(不動決策區索引)。
  2215	  9945	    today = datetime.date.today().isoformat()
  2216	  9946	    upd_i = next((k for k, ln in enumerate(fm) if re.match(r"^updated:\s", ln)), None)
  2217	  9947	    if upd_i is not None:
  2218	  9948	        fm[upd_i] = f"updated: {today}"
  2219	  9949	    else:
  2220	  9950	        dec_i = next((k for k, ln in enumerate(fm) if re.match(r"^decisions:\s*$", ln)), len(fm))
  2221	  9951	        fm[dec_i:dec_i] = [f"updated: {today}"]
  2222	  9952	    new_lines = lines[:1] + fm + lines[e_fm:]
  2223	  9953	    # [M1/P2] 讀 target 的 id → 組全域格式 <rel>#d<N> 回傳(下游 header/CASCADE/--from 同格式,無裸碼流出)
  2224	  9954	    did = None
  2225	  9955	    for i in range(st, en + 1):
  2226	  9956	        m = re.match(rf"^{pad}id:\s*(d\d+)\s*$", fm[i])
  2227	  9957	        if m:
  2228	  9958	            did = m.group(1)
  2229	  9959	            break
  2230	  9960	    gid = f"{rel}#{did}" if did else None
  2231	  9961	
  2232	  9962	    def _check(_fields):
  2233	  9963	        for d in parse_decisions(_fm_of(new_lines)):
  2234	  9964	            # [M1] 有 id → ID 精確驗證(content 子字串重疊會驗錯項);無 id(未 reindex 舊節點)→ 退回 content 驗證
  2235	  9965	            hit = (str(d.get("id", "")).strip() == did) if did \
  2236	  9966	                else (needle in nfc(str(d.get("content", ""))))
  2237	  9967	            if hit:
  2238	  9968	                return str(d.get("valid", "")).lower() == "false" and "superseded_by" in d
  2239	  9969	        return False
  2240	  9970	    atomic_write_verify(path, new_lines, "decisions", _check)
  2241	  9971	    _tag = f" [{gid}]" if gid else ""
  2242	  9972	    print(f"✓ supersede {rel}: 決策「{match[:30]}」→ valid:false + superseded_by + ended={ended} (updated bump {today}){_tag}")
  2243	  9973	    return 0, gid
  2244	  9974	
  2245	  9975	
  2246	  9976	def _max_decision_id(fm_lines):
  2247	  9977	    """[M1/P2] 掃 decisions[] 既有 id: d<N>,回最大 N(無則 0)。新號=max+1(不重排既有、
  2248	  9978	    不回收缺號——ID 穩定性合約:翻案後永不重用)。"""
  2249	  9979	    mx = 0
  2250	  9980	    for d in parse_decisions(fm_lines):
  2251	  9981	        m = re.fullmatch(r"d(\d+)", str(d.get("id", "")).strip())
  2252	  9982	        if m:
  2253	  9983	            mx = max(mx, int(m.group(1)))
  2254	  9984	    return mx
  2255	  9985	
  2256	  9986	
  2257	  9987	def cmd_decision_add(env, rel, content, decided, context=None, why=None):
  2258	  9988	    """T3 巢狀手術:append 一條新 ADR 決策到 decisions[](無則建)。surgical line-based。
  2259	  9989	    [M1/P2]:指派穩定 id d<max+1> 並回傳 (rc, 全域決策id <rel>#d<N>);dispatcher 解包後
  2260	  9990	    CLI 對外仍只回整數 rc。"""
  2261	  9991	    if not DATE_RE.match(decided):
  2262	  9992	        raise ValueError(f"擋下:--decided 要寫成 年-月-日(例如 2026-08-22),你給的是 {decided}")
  2263	  9993	    path = env.vault / rel
  2264	  9994	    lines, s_fm, e_fm = load_raw_for_edit(path)
  2265	  9995	    fm = lines[1:e_fm]
  2266	  9996	    loc = decisions_items(fm)
  2267	  9997	    new_id = f"d{_max_decision_id(fm) + 1}"
  2268	  9998	    if loc is None:
  2269	  9999	        # 無 decisions key → 在 fm 末尾建
  2270	 10000	        item_indent, sub = 2, 4
  2271	 10001	        block = [f'{" "*item_indent}- content: {_fmt_decision_value(content)}',
  2272	 10002	                 f"{' '*sub}id: {new_id}"]
  2273	 10003	        if context:
  2274	 10004	            block.append(f'{" "*sub}context: {_fmt_decision_value(context)}')
  2275	 10005	        if why:
  2276	 10006	            block.append(f'{" "*sub}why_chosen: {_fmt_decision_value(why)}')
  2277	 10007	        block += [f"{' '*sub}decided: {decided}", f"{' '*sub}valid: true"]
  2278	 10008	        fm = fm + ["decisions:"] + block
  2279	 10009	    else:
  2280	 10010	        _, e_block, items, item_indent, sub = loc
  2281	 10011	        ip, sp = " " * item_indent, " " * sub
  2282	 10012	        block = [f"{ip}- content: {_fmt_decision_value(content)}", f"{sp}id: {new_id}"]
  2283	 10013	        if context:
  2284	 10014	            block.append(f"{sp}context: {_fmt_decision_value(context)}")
  2285	 10015	        if why:
  2286	 10016	            block.append(f"{sp}why_chosen: {_fmt_decision_value(why)}")
  2287	 10017	        block += [f"{sp}decided: {decided}", f"{sp}valid: true"]
  2288	 10018	        last = items[-1][1] if items else e_block
  2289	 10019	        fm[last + 1:last + 1] = block
  2290	 10020	    new_lines = lines[:1] + fm + lines[e_fm:]
  2291	 10021	    needle = nfc(content)
  2292	 10022	
  2293	 10023	    def _check(_fields):
  2294	 10024	        # [M1] ID 精確驗證:新 id 那條存在且 content 相符(取代純 content 子字串——重疊時驗錯項)
  2295	 10025	        return any(str(d.get("id", "")).strip() == new_id
  2296	 10026	                   and needle in nfc(str(d.get("content", "")))
  2297	 10027	                   for d in parse_decisions(_fm_of(new_lines)))
  2298	 10028	    atomic_write_verify(path, new_lines, "decisions", _check)
  2299	 10029	    print(f"✓ decision-add {rel}: 記下一條決策「{content[:30]}」(編號 {new_id},目前有效)")
  2300	 10030	    return 0, f"{rel}#{new_id}"
  2301	scripts/lumos:1791:                   "修正 ref 格式/目標;若目標節點決策未編號先跑 lumos decision-reindex <節點>")
  2302	scripts/lumos:5059:        if rid_ in groups and next(reversed(groups)) != rid_:
  2303	scripts/lumos:5137:                pcc = next((r["capture_counts"] for r in groups[prev_rid] if r.get("capture_counts")), None)
  2304	scripts/lumos:5416:# next/status/verify-progress 全都強制要 loop_id,卻沒有任何入口能先知道有哪些編號在飛,
  2305	scripts/lumos:6663:def _roster_next_payload(loop_id, eff_tier):
  2306	scripts/lumos:6909:def cmd_loop_next(env, loop_id, tier=None, as_json=False, need=2, spec=None, repo=None, orchestrator=None):
  2307	scripts/lumos:6993:        out = {"phase": phase, "tier": eff_tier, "orchestrator": eff_orch, "round": n_next, "width": width,
  2308	scripts/lumos:6995:        _roster, _rnote = _roster_next_payload(loop_id, eff_tier)
  2309	scripts/lumos:7096:            print(f"[next] {loop_id}:現在狀態 {phase},分級 {eff_tier},接下來第 {n_next} 輪,"
  2310	scripts/lumos:9913:            raise ValueError(f"找不到編號 {match} 的決策,可能這篇的決策還沒編號;先跑:\n    lumos decision-reindex {rel}")
  2311	scripts/lumos:10033:def cmd_decision_reindex(env, rel=None, all_mode=False):
  2312	scripts/lumos:10043:                cmd_decision_reindex(env, r)
  2313	scripts/lumos:10357:            print(f"  (另有 {omitted_all_no_id} 個節點候選決策全無 id、悄悄不列——是漏 reindex 還是真沒關聯?先 lumos decision-reindex --all)")
  2314	scripts/lumos:12743:        if rid_ in groups and next(reversed(groups)) != rid_:
  2315	scripts/lumos:19484:    "decision-reindex": "舊筆記的決策沒編號,補上 dN。--all 全部。",
  2316	scripts/lumos:19802:    ll = lsub.add_parser("list", help="哪些審查迴圈還開著(帳面沒關門的);next/status 都要 loop_id,這支先給你編號")
  2317	scripts/lumos:19980:    p = sub.add_parser("decision-reindex", help="[M1/P2] 回填遷移:對無 id 決策從既有最大 id+1 接續編號(冪等);--all 批次套用全部決策節點(decision_refs 養成前置)")
  2318	scripts/lumos:19982:    p.add_argument("--all", action="store_true", dest="reindex_all", help="批次套用到所有有 decisions 的節點(顯式指令)")
  2319	scripts/lumos:20480:            return cmd_loop_next(env, args.loop_id, tier=args.next_tier, as_json=args.next_json, orchestrator=args.next_orch,
  2320	scripts/lumos:20607:    if args.cmd == "decision-reindex" and getattr(args, "reindex_all", False):
  2321	scripts/lumos:20609:            return cmd_decision_reindex(env, all_mode=True)
  2322	scripts/lumos:20614:    if args.cmd in ("decision-supersede", "decision-add", "decision-reindex"):
  2323	scripts/lumos:20615:        if args.cmd == "decision-reindex" and not args.note:
  2324	scripts/lumos:20616:            print("擋下:decision-reindex 要給一篇筆記,或用 --all 全部重編", file=sys.stderr)
  2325	scripts/lumos:20624:            if args.cmd == "decision-reindex":
  2326	scripts/lumos:20625:                return cmd_decision_reindex(env, rel)
  2327	scripts/lumos:20656:            # 單節點 decision-supersede/add/reindex 皆走 atomic_write_verify 寫檔,IO 例外(磁碟滿/
  2328	scripts/test_lumos.py:1655:    check("M1 d1 翻案且保留原 id(不刪不換號)",
  2329	scripts/test_lumos.py:1688:          r.returncode == 2 and "decision-reindex" in r.stderr, r.stderr)
  2330	scripts/test_lumos.py:1691:def t_decision_reindex():
  2331	scripts/test_lumos.py:1700:    r = run(v, "decision-reindex", "Mix")
  2332	scripts/test_lumos.py:1708:    r = run(v, "decision-reindex", "Mix")
  2333	scripts/test_lumos.py:1715:    r = run(v, "decision-reindex", "None")
  2334	scripts/test_lumos.py:1716:    check("reindex 無 decisions → rc=2", r.returncode == 2, r.stderr)
  2335	scripts/test_lumos.py:1948:def t_decision_reindex_all():
  2336	scripts/test_lumos.py:1956:    r = run(v, "decision-reindex", "--all")
  2337	scripts/test_lumos.py:1963:    r = run(v, "decision-reindex", "--all")
  2338	scripts/test_lumos.py:1965:    r = run(v, "decision-reindex")   # 無 node 無 --all
  2339	scripts/test_lumos.py:6497:def t_uninstall_preserves_regular_bin():
  2340	scripts/test_lumos.py:7014:def t_deinit_remove_vendored_preserves_user_files():
  2341	scripts/test_lumos.py:13764:def t_reinject_preserves_outside():
  2342	scripts/test_lumos.py:13779:        check("reinject_preserves_outside: status==updated",
  2343	scripts/test_lumos.py:13795:        check("reinject_preserves_outside: 前綴 byte-equal",
  2344	scripts/test_lumos.py:13798:        check("reinject_preserves_outside: 後綴 byte-equal",
  2345	scripts/test_lumos.py:18123:    r = run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "claude", "--json")
  2346	scripts/test_lumos.py:18132:          "cluster_hint" in run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "claude").stdout, "")
  2347	scripts/test_lumos.py:18138:    r2 = run(v, "loop", "next", lid, "--json", "--spec", str(spec), "--repo", str(v.parent))
  2348	scripts/test_lumos.py:18212:    d = _j.loads(run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "claude", "--json").stdout)
  2349	scripts/test_lumos.py:18934:    r = run(v, "loop", "next", lid, "--json", "--spec", str(spec), "--repo", str(v.parent))
  2350	scripts/test_lumos.py:20375:    keep = set("""append archive backlinks context contracts decision-add decision-reindex
  2351	scripts/test_lumos.py:20882:def t_slim_uninstall_backs_up_and_preserves_custom_files():
  2352	scripts/test_lumos.py:22304:    keep = set("""append archive backlinks context contracts decision-add decision-reindex
  2353	scripts/test_lumos.py:23862:    s01 = next((c["unjudged"] for c in d["cases"] if c["id"] == "S01"), [])
  2354	scripts/test_lumos.py:23865:    e01 = next((c["unjudged"] for c in d["cases"] if c["id"] == "E01"), [])
  2355	scripts/test_lumos.py:25058:        r = run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "claude")
  2356	scripts/test_lumos.py:26402:    r = run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "claude", "--json", expect_rc=1)
  2357	scripts/test_lumos.py:26417:    rt = run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "claude", expect_rc=1)
  2358	scripts/test_lumos.py:26440:    r3 = run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "claude", "--json", "--spec", str(spec), "--repo", str(v.parent))
  2359	scripts/test_lumos.py:27719:    r = run(v, "loop", "next", lid, "--tier", "standard")
  2360	scripts/test_lumos.py:27721:    r = run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "codex", "--json")
  2361	scripts/test_lumos.py:27724:    r = run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "codex")
  2362	scripts/test_lumos.py:27731:    r = run(v, "loop", "next", lid, "--orchestrator", "claude")
  2363	scripts/test_lumos.py:27733:    r = run(v, "loop", "next", lid)
  2364	scripts/test_lumos.py:27754:    d = _j.loads(run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "codex", "--json").stdout)
  2365	scripts/test_lumos.py:27782:    dj = _j.loads(run(v, "loop", "next", lid, "--tier", "standard", "--orchestrator", "codex", "--json").stdout)   # lid 尚無記錄,零記錄兩旗標都要帶
  2366	scripts/test_lumos.py:29430:    loop next/status/verify-progress 全都強制要 loop_id,而沒有任何入口能先知道有哪些編號在飛,
  2367	   163	## 待裁的開放問題(留給設計審)
  2368	   164	
  2369	   165	3. ~~**「完成」怎麼定義**~~ → ★**已裁(2026-09-07 Enzo)**:完成判準掛在**實作端**,看**測試有沒有過**;判的是「整個功能有沒有完成」+「相依功能有沒有回歸」。**明確不做散文級判準。**★
  2370	   166	
  2371	   167	   **★這個切法躲開了外家 f2 的反對,而且是有理由的躲開,不是繞過★**:f2 打的是**任務級**「測試綠=任務完成」——Task 1–5 全部往同一個 `t_delguard()` 裡續加斷言,那個測試綠分不出誰做完了。
  2372	   168	   但 Enzo 裁的是**功能級**:①功能級「這個功能的測試套綠」不受共用測試影響(共用的正是同一個功能的測試) ②「既有測試開工前就綠」對**新功能**不成立(它的測試本來不存在) ③「有的任務只寫跑全套」在功能級不是缺陷,**那就是「相依功能沒回歸」這一半的定義**。
  2373	   169	   ★三條反對在功能級各自失效——所以這不是無視外家,是換了一個 f2 打不到的粒度。★
  2374	   170	- **要不要擋**:先做唯讀查詢,還是一開始就讓 pre-commit 提醒「這批改動沒掛任何工作項」?★編排者傾向先唯讀★(理由:本案的價值還沒有本地證據,先擋會逼出湊數的 trailer=製造假資料),但沒有量過,留給審。
  2375	   171	- ★**原稿寫「`[SN]` 目前實際沒人寫」——不屬實,前掃逐篇實跑推翻(④-4)**★:全 repo 158 篇計劃逐篇跑 `spec-trace`,**32 篇真的寫了 `[SN]`,其中 13 篇被真實的 Verification 完整認領(rc=0)**,另 19 篇部分未認領;126 篇未啟用。
  2376	   172	  ★這條反而強化 D1★:不是「慣例存在但沒人用」,是**已經在用、而且已經有 13 篇完整跑通**——沿用它的成本比原稿估的更低。
  2377	   173	  (原稿那句還跟本文自己「spec-trace 已經有消費者」直接打架,同一份文件內互相矛盾,已改。)
  2378	   174	- 仍待審的是**覆蓋率**:126/158 沒寫。要不要同時處理「怎麼讓人真的寫」,是設計審該打的點。
  2379	   175	- **那 18 個「沒有測試可掛」的任務段還沒逐一分類**(先前只知道總數);射程要收在哪,得先分類。
  2380	   176	
  2381	   177	## ★裁定之後浮出來的兩個新問題(Enzo 裁完才看得到)★
  2382	   178	
  2383	   179	### 甲、功能級是二元的,但「接手」需要更細
  2384	   180	
  2385	   181	本案的來源需求是「agent 做到一半,任何 session 接得下去」。
  2386	   182	
  2387	   183	- **功能級判準只答得出「完成 / 沒完成」。** 一個功能拆 12 個任務、agent 停在第 7 個 → 功能測試是紅的 → 你只知道「沒完成」,**不知道「做到第 7 個」**。★那正好是接手最需要的那一格。★
  2388	   184	- **但不必換判準就能補**:先前量過,74 個任務段裡 **56 個(75%)** 自己就寫了對應的測試函式名。所以**同一個判準可以有兩種解析度**:
  2389	   185	  - **功能級**(是否完成)= 該功能的測試套 + 全套回歸 → **這是 Enzo 裁的那個,是「完成」的權威**。
  2390	   186	  - **任務級**(做到哪)= 逐個任務宣告的測試名綠了沒 → **只當接手用的進度指示,不當完成判準**(f2 的反對在這一級仍然成立,所以★不得用它宣告完成★)。
  2391	   187	- ★兩級必須語意分明:一個是判定,一個是提示。混用就會把 f2 打過的洞再開一次。★
  2392	   188	
  2393	   189	### 乙、「綠」是**什麼時候**的綠
  2394	   190	
  2395	   191	- 若指「現在跑一次是綠的」→ 每次查進度都要跑全套(約 8 分鐘),**查不起**。
  2396	   192	- 若指「宣告完成的那個版本上是綠的」→ 要有一筆按版本記的結果。
  2397	   193	- ★好消息:這筆紀錄已經存在★——`governance/code-loop/main.json` 就是 `{head_sha, status}` 形態(實查:`head_sha: c103e324…`,`status: passed`);另有 `lumos ci-status`(只讀上次 CI 結果、不打網路)。
  2398	   194	- **所以本案不必新建測試結果帳,接既有的即可**。★來源已於 [D3] 裁定=CI 那筆、不用 code-loop pass★(本節原本把它寫成「還沒裁」,是撰寫順序造成的殘留,前掃 ③ 抓到,已改)。
  2399	   195	
  2400	   196	## 驗收線(這份計劃算不算做成)
  2401	   197	
  2402	   198	- 能對一份真實的實作計畫,**不讀它的勾選框**,答出每個工作項有沒有被提交掛過、最後一次何時。
  2403	   199	- 對那 18 個「天生算不出來」的任務段,**輸出明說算不出來**,不含糊。
  2404	   200	- 三步各自有測試;測試 fixture ★用真的呼叫 git 產生,不手刻★(2026-09-07 教訓:手刻 fixture 導致 code-loop 那半是死碼)。
  2405	
  2406	exec
  2407	/bin/zsh -lc "nl -ba .github/workflows/ci.yml | sed -n '1,220p'
  2408	python3 scripts/lumos ci-status --json
  2409	python3 - <<'PY'
  2410	import json
  2411	from pathlib import Path
  2412	rows=[]
  2413	for i,l in enumerate(Path('docs/.ci-log.jsonl').read_text().splitlines(),1):
  2414	 try: d=json.loads(l)
  2415	 except: continue
  2416	 rows.append((i,d.get('sha'),d.get('conclusion')))
  2417	print('records',len(rows),'unique_shas',len({x[1] for x in rows}))
  2418	print('last',rows[-1])
  2419	PY" in /Users/enzo/harness/lumos-toolchain
  2420	 exited 1 in 166ms:
  2421	{"ts": "2026-09-07T13:15:34+08:00", "run_id": 34085131143, "attempt": 1, "sha": "9854ba5c0b63d5a2180999b4ada6c7a0770b81e9", "branch": "main", "workflow": "CI", "conclusion": "success", "title": "", "url": "https://github.com/EnzoHsieh-Android/Lumos/actions/runs/34085131143", "failed_step": "", "dedup_key": "34085131143:1:success"}
  2422	zsh:3: can't create temp file for here document: operation not permitted
  2423	
  2424	codex
  2425	severity: blocker
  2426	
  2427	1. [S2] 的漏記會被系統當成真實未完成，核心目標因此無法成立。  
  2428	引句:「沒有守衛的 trailer,漏掉的那些工作項會長期顯示成『沒人做過』」  
  2429	severity: blocker；blocking: 是。最小閉環是 `commit-msg` 對非簿記提交強制有效 `Lumos-Task`，並提供帶理由、可統計的顯式豁免；唯讀查詢不能先於這道寫入守衛交付。
  2430	
  2431	2. D3 選 CI 的語意方向正確，但現有紀錄不是每個 trailer commit 都有對應結果。  
  2432	引句:「CI 那筆的語意就是對的。實查其 JSON」  
  2433	severity: major；blocking: 是。workflow 只在 push 到 main 時執行，CI 結果綁 push 的 tip SHA；一次推多個 commit 時，中間帶 trailer 的 commit 沒有自己的 CI 紀錄，且 `ci-status` 只取帳尾最新 SHA，不能回答歷史工作項：file: `.github/workflows/ci.yml:4`、file: `scripts/lumos:16454`、file: `scripts/lumos:16487`。
  2434	
  2435	3. D1 把 `[SN]` 的可編輯標號誤當成 `#dN` 的穩定 ID。  
  2436	引句:「`#S1` 完全比照,連驗證邏輯都可以照抄」  
  2437	severity: major；blocking: 是。`spec-trace` 只是從全文正則收集數字並用集合去重，沒有指派、唯一性、改號或刪號守衛；決策 ID 則由工具以 `max+1` 指派且不回收，兩者沒有同一穩定性契約：file: `scripts/lumos:3764`、file: `scripts/lumos:3781`、file: `scripts/lumos:9976`、file: `scripts/lumos:9997`。
  2438	
  2439	4. d3 所稱三條反對在功能級「各自失效」不成立。  
  2440	引句:「既有測試已綠對新功能不成立(它的測試本來不存在)」  
  2441	severity: major；blocking: 是。既有功能的擴充、修錯與重構仍沿用既有測試套，而新測試也能在功能未完整時先寫成綠；CI 只證明該 SHA 通過現有 oracle，沒有證明 spec 所稱功能邊界已全部實現。
  2442	
  2443	5. 四分之一盲區只有輸出措辭，沒有可執行的分類規則。  
  2444	引句:「真正無解的是改 skill 散文那一類。實際比例沒量過」  
  2445	severity: major；blocking: 是。系統尚不能從 `[SN]` 判定一項屬於 skill 散文、圖譜回填或真機驗收，因此也無法可靠輸出「算不出來」而不是「沒人做過」；審材自己仍把 18 項逐一分類列為未完成前置，卻已先裁定架構：file: `governance/review-reports/進度從提交推導/r1-snapshot.md:129`、file: `governance/review-reports/進度從提交推導/r1-snapshot.md:175`。
  2446	
  2447	6. 「識別碼是唯一斷點」漏掉了審材自己量出的更小第四條路。  
  2448	引句:「這條因果鏈沒有分叉,斷點在最前面」  
  2449	severity: major；blocking: 是。56/74 任務已帶對應測試名，測試名本身即可作既有識別：由計劃抽出測試名、用 git 歷史定位新增或修改它的 commit，再以該 commit 是否為成功 CI SHA 的祖先算進度，首版不必新增 `[SN]` 或 trailer；這條零新寫入格式的基線沒有先做實驗便被排除。
  2450	
  2451	7. 立案證據證明「手寫狀態會漂」，尚未證明新查詢會被使用或能改善接手。  
  2452	引句:「本案的價值還沒有本地證據,先擋會逼出湊數的 trailer」  
  2453	severity: major；blocking: 是。現有數字量的是陳舊筆記與編號稀少，不是接手者答錯、查詢頻率或因此返工；在加入永久 trailer 契約前，應先用第 6 條的唯讀原型對真實接手問題量命中率，否則尚未通過本專案「症狀—消費者—最小層」的立案線。
  2454	hook: Stop
  2455	hook: Stop Completed
  2456	tokens used
  2457	90,330
  2458	severity: blocker
  2459	
  2460	1. [S2] 的漏記會被系統當成真實未完成，核心目標因此無法成立。  
  2461	引句:「沒有守衛的 trailer,漏掉的那些工作項會長期顯示成『沒人做過』」  
  2462	severity: blocker；blocking: 是。最小閉環是 `commit-msg` 對非簿記提交強制有效 `Lumos-Task`，並提供帶理由、可統計的顯式豁免；唯讀查詢不能先於這道寫入守衛交付。
  2463	
  2464	2. D3 選 CI 的語意方向正確，但現有紀錄不是每個 trailer commit 都有對應結果。  
  2465	引句:「CI 那筆的語意就是對的。實查其 JSON」  
  2466	severity: major；blocking: 是。workflow 只在 push 到 main 時執行，CI 結果綁 push 的 tip SHA；一次推多個 commit 時，中間帶 trailer 的 commit 沒有自己的 CI 紀錄，且 `ci-status` 只取帳尾最新 SHA，不能回答歷史工作項：file: `.github/workflows/ci.yml:4`、file: `scripts/lumos:16454`、file: `scripts/lumos:16487`。
  2467	
  2468	3. D1 把 `[SN]` 的可編輯標號誤當成 `#dN` 的穩定 ID。  
  2469	引句:「`#S1` 完全比照,連驗證邏輯都可以照抄」  
  2470	severity: major；blocking: 是。`spec-trace` 只是從全文正則收集數字並用集合去重，沒有指派、唯一性、改號或刪號守衛；決策 ID 則由工具以 `max+1` 指派且不回收，兩者沒有同一穩定性契約：file: `scripts/lumos:3764`、file: `scripts/lumos:3781`、file: `scripts/lumos:9976`、file: `scripts/lumos:9997`。
  2471	
  2472	4. d3 所稱三條反對在功能級「各自失效」不成立。  
  2473	引句:「既有測試已綠對新功能不成立(它的測試本來不存在)」  
  2474	severity: major；blocking: 是。既有功能的擴充、修錯與重構仍沿用既有測試套，而新測試也能在功能未完整時先寫成綠；CI 只證明該 SHA 通過現有 oracle，沒有證明 spec 所稱功能邊界已全部實現。
  2475	
  2476	5. 四分之一盲區只有輸出措辭，沒有可執行的分類規則。  
  2477	引句:「真正無解的是改 skill 散文那一類。實際比例沒量過」  
  2478	severity: major；blocking: 是。系統尚不能從 `[SN]` 判定一項屬於 skill 散文、圖譜回填或真機驗收，因此也無法可靠輸出「算不出來」而不是「沒人做過」；審材自己仍把 18 項逐一分類列為未完成前置，卻已先裁定架構：file: `governance/review-reports/進度從提交推導/r1-snapshot.md:129`、file: `governance/review-reports/進度從提交推導/r1-snapshot.md:175`。
  2479	
  2480	6. 「識別碼是唯一斷點」漏掉了審材自己量出的更小第四條路。  
  2481	引句:「這條因果鏈沒有分叉,斷點在最前面」  
  2482	severity: major；blocking: 是。56/74 任務已帶對應測試名，測試名本身即可作既有識別：由計劃抽出測試名、用 git 歷史定位新增或修改它的 commit，再以該 commit 是否為成功 CI SHA 的祖先算進度，首版不必新增 `[SN]` 或 trailer；這條零新寫入格式的基線沒有先做實驗便被排除。
  2483	
  2484	7. 立案證據證明「手寫狀態會漂」，尚未證明新查詢會被使用或能改善接手。  
  2485	引句:「本案的價值還沒有本地證據,先擋會逼出湊數的 trailer」  
  2486	severity: major；blocking: 是。現有數字量的是陳舊筆記與編號稀少，不是接手者答錯、查詢頻率或因此返工；在加入永久 trailer 契約前，應先用第 6 條的唯讀原型對真實接手問題量命中率，否則尚未通過本專案「症狀—消費者—最小層」的立案線。
governance/review-reports/進度從提交推導/r1-接手.md
     1	severity: blocker
     2	
     3	# 整合/知識同步(接手)席 r1
     4	
     5	## F-hnd-1 ★blocker★ D3「換粒度躲開 f2」的論證留了口子,且與已連結筆記直接衝突
     6	severity: blocker
     7	blocking: 是
     8	引句:「「既有測試開工前就綠」對**新功能**不成立(它的測試本來不存在)」
     9	file: `docs/lumos-toolchain-knowledge/Projects/驗形式與驗內容_調研.md:70`
    10	反駁②自己明寫只在「新功能」成立,但完成判準通用涵蓋「增修既有功能」;對那一類,f2 原話在功能級一樣成立。且被連結的姊妹研究把「測試綠≠完成」歸為 AI 特有的形式≠內容通病、根因與粒度無關——該篇被連結卻從未被實質回應。
    11	
    12	## F-hnd-2 任務級解析度沒有可執行的資料源
    13	severity: major
    14	blocking: 是
    15	引句:「逐個任務宣告的測試名綠了沒」
    16	[S1][S2][S3] 沒有一步能回答「某個測試現在綠不綠」;S3 只從 git log 讀提交,而 CI 的 JSON 是 workflow 級(sha/conclusion/workflow/run_id/failed_step),沒有逐測試欄位。要嘛現場跑(與乙節「查不起」同源),要嘛新資料源,兩者都沒指定。
    17	
    18	## F-hnd-3 決策定址有兩項 [SN] 沒有的機械保障
    19	severity: major
    20	blocking: 是
    21	引句:「`#S1` 完全比照,連驗證邏輯都可以照抄」
    22	file: `scripts/lumos:10034`
    23	file: `scripts/lumos:1766`
    24	file: `scripts/lumos:3764`
    25	①`decision-reindex` docstring 明寫「不重排既有、不回收缺號」②Check E3 對照 frontmatter 顯式 id 清單做真 dangling 偵測。`[SN]` 只是裸正則抓 body,無登記簿、無防重排;人手插入新任務重編號無工具攔,舊 trailer 靜默指向錯的任務。
    26	
    27	## F-hnd-4 提交夾帶會直接腐化 trailer 歸屬(已連結、零討論)
    28	severity: major
    29	blocking: 是
    30	引句:「"[[Issues/同工作區多session並行改動]]"」
    31	file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:40`
    32	被夾帶那一邊的任務即使真的做完,提交訊息與 trailer 只寫夾帶者自己的識別碼,S3 會回報「沒人動過」——正是本案要消滅的假狀態,而全文零討論。
    33	
    34	## F-hnd-5 ★未提交的進行中工作完全不可見,而那正是核心情境★
    35	severity: major
    36	blocking: 是
    37	引句:「本案的來源需求是「agent 做到一半,任何 session 接得下去」。」
    38	S2/S3 整套建立在「已提交」之上;session 動手但尚未 commit 就中斷(context 用盡、當機、關終端機),S3 給的訊號跟「從來沒人碰過」一模一樣——恰是「做到一半」裡最急迫最常見的時間點,含誠實天花板段全文未提。
    39	
    40	## F-hnd-6 正文 [D1][D2][D3] 與 frontmatter d1/d2/d3 撞號但內容不同
    41	severity: minor
    42	blocking: 否
    43	引句:「### [D1] 識別碼 = 沿用既有的 `[SN]` 條款標記」
    44	正文 D1/D2/D3 實際是 frontmatter 的 d4/d5/d6;大小寫不同故機械不會混,但一篇通篇在講「識別碼要唯一可定址」的文件自己先撞了一次號。
    45	
    46	## F-hnd-7 「S1 不寫程式」與「三步各自有測試」字面打架
    47	severity: minor
    48	blocking: 否
    49	引句:「本步只定慣例與格式,不寫程式」
    50	
    51	## F-hnd-8 沒有機制驗證 trailer 宣稱的任務與該提交 diff 有對應
    52	severity: minor
    53	blocking: 否
    54	引句:「提交訊息尾端加一行 `Task: <識別碼>`(鍵名待裁,見開放問題)。」
    55	任何瑣碎提交都能掛任意任務號;甲節「只當提示不當判準」部分緩解故評 minor,但接手者當真會被誤導。
    56	
    57	## 機械查證結論
    58	引句、指令 help、統計數字全數通過(spec-trace 32/13/19/126 對 158 篇實跑完全吻合);洞出在論證層。
    59	severity: blocker;blocking 5 條(1 blocker + 4 major),另 3 條 minor。
governance/review-reports/進度從提交推導/r1-正確性.md
     1	severity: blocker
     2	
     3	# 正確性/邏輯席 r1
     4	
     5	## F-cor-1 正文 [D1][D2][D3] 與 frontmatter 真實 id d4/d5/d6 不一致
     6	severity: major
     7	blocking: 是
     8	引句:「識別碼沿用既有 [SN] 條款標記,定址比照決策寫成 <計劃節點rel>#S1」
     9	file: `scripts/lumos:1765`
    10	機械檢查只認小寫 `d` 加數字;若有人依正文標籤寫 `#D1` 會被 doctor Check E3 判懸空,而不是找到 d4。
    11	
    12	## F-cor-2 「三個詞」其實定義了四個
    13	severity: minor
    14	blocking: 否
    15	引句:「本篇用到的三個詞**:「外家」=不是編排者那一家的審查席」
    16	
    17	## F-cor-3 ★blocker★ 識別碼對本文自己舉的頭號症狀完全無效
    18	severity: blocker
    19	blocking: 是
    20	引句:「[D1] 識別碼 = 沿用既有的 `[SN]` 條款標記,定址寫成 `<計劃節點rel>#S1`」
    21	引句:「60 個框,0 個打勾**(12 任務 × 5 步驟,全是實作步驟不是驗收清單)」
    22	file: `docs/lumos-toolchain-knowledge/Projects/主動影響幅度偵測_實作計畫.md:51`
    23	file: `docs/lumos-toolchain-knowledge/Projects/執行DAG_調研.md:152`
    24	兩篇旗艦範例都用 `### Task N` 標題、全文 `[SN]` 出現 0 次;用這個識別碼查它們,答案永遠是「無工作項」而不是「有工作項但沒提交掛」。且姊妹研究外家的「洞一」(任務切分格式不統一、有整篇切不出任務)本文完全沒折入,只折了洞二,D1 依據不完整。
    25	
    26	## F-cor-4 squash 會讓 trailer 靜默消失
    27	severity: major
    28	blocking: 是
    29	引句:「git 原生解析,不自己寫正則去撈提交訊息」
    30	git 只認訊息結尾那一段連續的鍵值區塊;squash 串接後不在最後一段的 `Lumos-Task:` 會被靜默漏掉、不報錯。scratch repo 當場重現。
    31	
    32	## F-cor-5 `#dN` 不撞號靠機械指派,`[SN]` 沒有對應工具
    33	severity: major
    34	blocking: 是
    35	引句:「不必維護登記簿**:識別碼從計劃節點自己長出來,沒有第二份要同步的東西」
    36	file: `scripts/lumos:10033`
    37	file: `scripts/lumos:3764`
    38	file: `scripts/lumos:3797`
    39	`#dN` 有 `decision-reindex` 機械指派遞增 id;`[SN]` 一律手打、無 spec-reindex。程式自帶已知限制註解:多計劃 Verification 提及 [S1] 會同時記入兩計劃的 S1。D1 代價段只提「改名會指不到」。
    40	
    41	## F-cor-6 CI 綁 push 的 tip sha,中間提交結構性查不到
    42	severity: major
    43	blocking: 是
    44	引句:「CI 只在推送後跑,**本機還沒推的工作查不到**」
    45	file: `.github/workflows/ci.yml:6`
    46	file: `scripts/lumos:16238`
    47	一次 push 只起一個 run、綁當下 HEAD;一次推多個提交時中間那些永遠沒有屬於自己 sha 的紀錄——不是暫時未知,是永久未知,乙節沒處理。
    48	
    49	## F-cor-7 `ci-status` 只回最後一筆,答不了歷史 sha
    50	severity: major
    51	blocking: 是
    52	引句:「另有 `lumos ci-status`(只讀上次 CI 結果、不打網路)」
    53	file: `scripts/lumos:16454`
    54	file: `scripts/lumos:16487`
    55	`newest_sha = rows[-1].get("sha")`,無參數指定歷史 sha;要答「S1 當時綠不綠」必須繞過它自己解析帳檔,乙節沒提要多做這一步。
    56	
    57	## F-cor-8 凍結當時綠 → 永久假完成,打穿判準自己那一半
    58	severity: major
    59	blocking: 是
    60	引句:「宣告完成的那個版本上是綠的」
    61	引句:「功能級測試套綠 + 相依功能無回歸;明確不做散文級判準」
    62	若後續提交把 S1 依賴的東西改壞,查詢仍讀舊 sha 的紀錄,S1 永遠顯示完成——直接打穿 d3 宣稱的「相依功能有沒有回歸」那一半。
    63	
    64	## 總結
    65	severity: blocker;blocking 共 7 條(1 blocker + 6 major),另 1 條 minor。
governance/review-reports/進度從提交推導/r1-架構對齊.md
     1	severity: major
     2	
     3	# 架構對齊席 r1(嚴重度已正規化:high→major、medium-high→major、low→minor)
     4	
     5	## F-arch-1 定址解析「照抄」會疊上第四份重複實作
     6	severity: major
     7	blocking: 是
     8	引句:「定址形狀已經有:決策的定址是 `<節點rel>#dN`(程式裡有格式驗證與 dangling 偵測)。`#S1` 完全比照,連驗證邏輯都可以照抄。」
     9	file: `scripts/lumos:1632`
    10	file: `scripts/lumos:1766`
    11	file: `scripts/lumos:10265`
    12	同一份檔案裡 `(.+?)#(d\d+)` 獨立出現三處、互不共用(doctor Check E2 閉包 / Check E3 / `_dref_parse` 官方版)。這是進行式的既有漂移,「照抄」等於再疊一份給 `#SN`。
    13	
    14	## F-arch-2 `[SN]` 抽取沒承諾與 spec-trace 共用同一個正則
    15	severity: major
    16	blocking: 是
    17	引句:「本步只定慣例與格式,不寫程式。」
    18	file: `scripts/lumos:3764`
    19	file: `scripts/lumos:3781`
    20	既有 `SPEC_CLAUSE_RE` 已在解析 `[SN]`;全文只承諾格式層沿用,程式層是否共用完全沒交代,有長出第二套解析的風險。
    21	
    22	## F-arch-3 新指令落在 CLI 哪個位置沒定案
    23	severity: minor
    24	blocking: 否
    25	引句:「樣板照 `loop verify-progress`:它的 help 逐字寫「不看散文,只從帳本結構欄位看審到哪了」
    26	file: `scripts/lumos:19747`
    27	`loop` 分組語意鎖定「審計/設計審查迴圈」,與「實作任務從 git 推進度」不同領域。⚠ 判不準交編排者:文字沒排除誤讀也沒給替代位置。
    28	
    29	## F-arch-4 唯讀查詢的 rc / --json / 壞行處置慣例三者都沒寫
    30	severity: minor
    31	blocking: 否
    32	引句:「新增唯讀查詢:某個計劃的每個工作項,有沒有提交掛過它、最後一次是什麼時候、動了哪些檔。」
    33	file: `scripts/lumos:5682`
    34	file: `scripts/lumos:16454`
    35	file: `scripts/lumos:3768`
    36	既有三支唯讀查詢對「恆 rc0 或有無未認領回 rc1」「壞行怎麼標」各有明確慣例語言,本設計 S3 全段未提。
    37	
    38	## F-arch-5 (乾淨)零依賴與單檔 CLI 家規有守
    39	severity: clean
    40	引句:「④不採用新依賴:全案只用 git 與 python3 stdlib。」
    41	
    42	## F-arch-6 (乾淨)CI 讀取重用既有指令,沒長出第三套讀法
    43	severity: clean
    44	引句:「CI 那筆的語意就是對的。」
    45	file: `scripts/lumos:16454`
    46	
    47	## F-arch-7 trailer 讀取實際呼叫形狀沒寫
    48	severity: minor
    49	blocking: 否
    50	引句:「讀取端:`git log --format='%(trailers:key=Task,valueonly=true)'`」
    51	file: `scripts/lumos:16351`
    52	既有子行程慣例用清單參數不做字串插補;repo 內目前無 trailer 解析,非重複實作,只是實作階段提醒。
    53	
    54	## 總結
    55	一、二不是留白,是設計文字主動選擇複製而非重用/泛化,而 repo 此刻就攤著三份互不呼叫的 `#dN` 正則當反例。建議退回 D1:這輪就要寫明共用哪個函式。
    56	severity: major
governance/review-reports/進度從提交推導/r1-intake.md
     1	preflight-4: ran
     2	
     3	# r1 前掃留痕(進度從提交推導)
     4	
     5	派工:一個 sonnet agent,固定四類清單(未定義詞 / 壞引用 / 範圍自相矛盾 / ★機械宣稱驗語意★),唯讀查證。
     6	處置原則照 skill:①②③與存在類=直接修真檔、不算 findings;語意類=修真檔並逐條留痕(修改前→後);動到核心裁定的=升級為正式 finding 交席位,前掃不自行改裁定。
     7	
     8	## ① 未定義的詞(3 條,直接修真檔)
     9	
    10	「外家 f2」「編排者」「50 群的『群』」——本文內部推不出意思,要點開別篇才懂。
    11	處置:檔首加一段當場解釋四個詞。
    12	
    13	## ② 壞引用
    14	
    15	**零命中。** 五個連結節點、`governance/code-loop/main.json`、三個指令、`maestro:smoke_05_manual_discount_over_100` 這個例子,全部實查存在。
    16	
    17	## ③ 範圍自相矛盾(1 條,直接修真檔)
    18	
    19	- 前:第 187 行「要裁的只剩『用 code-loop 那筆、CI 那筆,還是兩者都要』」
    20	- 後:「來源已於 [D3] 裁定=CI 那筆、不用 code-loop pass(本節原本把它寫成『還沒裁』,是撰寫順序造成的殘留)」
    21	- 成因:乙節先寫、D3 後裁,沒回頭改乙節。
    22	
    23	## ④ 機械宣稱驗語意(逐條:前→後)
    24	
    25	**屬實、不用改的 7 條**:git trailer 格式字串可用(實跑)/近 30 筆 100% 帶兩個 trailer(重數)/`spec-trace` help 逐字相符且真的解析 `[SN]` 比對 `plan_refs`(讀 `cmd_spec_trace`)/決策定址有三層檢查(doctor Check E3 的 `re.fullmatch(r"(.+?)#(d\d+)")`+resolve+驗 id)/`skipped` 是合法狀態值(`grep` 到 skip 子指令與事件集合)/`ci-status` 按版本記帶結論且**函式內只有本地 `open()`、無任何網路呼叫**(讀 `cmd_ci_status`)/近 120 筆帶編號 6 筆且全對應主清單編號。
    26	
    27	**★不屬實,已改 3 條★**
    28	
    29	1. **[SN] 使用率**
    30	   - 前:「`[SN]` 目前實際沒人寫(spec-trace 回 opt-in 未啟用)」
    31	   - 實測:158 篇計劃逐篇跑 → **32 篇有寫、其中 13 篇被 Verification 完整認領(rc=0)**、19 篇部分未認領、126 篇未啟用。
    32	   - 後:改寫成上述實測數字,並註明★這反而強化 D1★(沿用成本比原估更低);仍待審的是覆蓋率。
    33	   - 附帶:原稿那句與本文自己「spec-trace 已經有消費者」同篇打架,一併消解。
    34	
    35	2. **引句不是逐字**
    36	   - 前:`loop verify-progress` help 自述「不看散文,只從帳本結構欄位看審到哪」(缺「了」與括號說明);摘要另一處還把語序倒過來寫成「只讀結構不讀散文」卻加引號。
    37	   - 後:兩處都改成逐字「不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)。」
    38	
    39	3. **★trailer 產生機制(前掃自己找到的,清單沒列)★**
    40	   - 前:「它由提交模板產生,★人不必自己打★(`Co-Authored-By` 就是這樣運作的)」
    41	   - 實查:`git config commit.template` 指到的檔**是空的**;真正機制是 **AI 每次提交照 session 指示手動打**,git 層沒有自動代入。
    42	   - 後:代價改成「字長,而且要靠寫提交的人記得加」。
    43	   - ★升級為交席位審的問題(前掃不自行裁)★:[S2] 整段建立在「提交會掛 trailer」上,而那一步**目前純自律、零機械守衛**——與本案主張的「不靠人維護」有落差;漏掉的工作項會長期顯示成「沒人做過」,正是本案要消滅的假狀態。
    44	
    45	## 附帶重算(前掃主動查的)
    46	
    47	- 「Projects 標進行中 43 篇」→ 精確重算 **46 篇**(差的 3 篇是同日新增、含本篇自己);「>30 天沒動 17 篇」**吻合**。已改並標快照時間。
    48	- 「60 框 0 勾 / 39 框全勾」兩個例子**精確吻合**,連「12 任務×5 步驟」都對得上。

codex
第一輪對照已確認：v2 確實移除了 trailer／CI 的原機制，但「讀工作樹」只消除了版本不可見，沒有消除工作樹的作者歸屬與並行污染。接著我會把三態與 `-k` 的實際退出語意釘死，避免只做概念批評。
exec
/bin/zsh -lc "rg -n '"'^'"\\s*def t_impact|t_impact' scripts/test_lumos.py | head -40 && python3 scripts/test_lumos.py -k t_impact" in /Users/enzo/harness/lumos-toolchain
 exited 1 in 211ms:
Traceback (most recent call last):
  File "/Users/enzo/harness/lumos-toolchain/scripts/test_lumos.py", line 29625, in <module>
    sys.exit(main())
             ~~~~^^
  File "/Users/enzo/harness/lumos-toolchain/scripts/test_lumos.py", line 24848, in main
    _run_root = _isolate_environment()
  File "/Users/enzo/harness/lumos-toolchain/scripts/test_lumos.py", line 24734, in _isolate_environment
    real_tmp = tempfile.gettempdir()
  File "/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/tempfile.py", line 312, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ~~~~~~~~~~~^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/tempfile.py", line 305, in _gettempdir
    tempdir = _get_default_tempdir()
  File "/opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/lib/python3.14/tempfile.py", line 222, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
                            "No usable temporary directory found in %s" %
                            dirlist)
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/enzo/harness/lumos-toolchain']

exec
/bin/zsh -lc "nl -ba scripts/test_lumos.py | sed -n '24670,24930p'; nl -ba docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md | sed -n '1,230p'; nl -ba docs/lumos-toolchain-knowledge/Projects/驗形式與驗內容_調研.md | sed -n '55,90p'" in /Users/enzo/harness/lumos-toolchain
 succeeded in 0ms:
 24670	    check("enforcement: 缺 pre-commit inactive", by.get("git-pre-commit") == "inactive", str(by))
 24671	    check("enforcement: 缺 CI inactive", by.get("ci-workflow") == "inactive", str(by))
 24672	
 24673	
 24674	def t_enforcement_summary_excludes_unknown():
 24675	    m = _load_lumos_inproc()
 24676	    root, home = _enforcement_fixture(all_active=True)
 24677	    rows = m.enforcement_status(root=root, home=home)
 24678	    n_active, n_total, n_unknown = m.enforcement_summary(rows)
 24679	    # r1 審:別寫成 summary 公式的套套邏輯——用具體數字釘。全裝好的 fixture:8 active(4 hook+2 hook檔+... 實際數)、
 24680	    # required-status 恆 unknown。這裡釘「至少 8 active、恰 1 unknown(只有遠端那列)」。
 24681	    # hermetic fixture 沒建 CLAUDE.md/anchor-baseline,所以 vendored-cli 誠實 unknown(無版本可判)、anchor inactive。
 24682	    # 恰兩列 unknown:vendored-cli(無 CLAUDE.md)+ required-status-check(遠端測不到)。別寫成 summary 公式的套套邏輯。
 24683	    unknown_layers = sorted(r["layer"] for r in rows if r["status"] == "unknown")
 24684	    # 2026-09-04 Codex完全支援 S0:fixture 的 home 沒有 ~/.codex → Codex 八列(5 hook+cli+skills+agents-md)
 24685	    # 一律 unknown(不適用,不是壞;入口 hook 才不會對沒裝 Codex 的機器每 session 唸)
 24686	    codex_layers = ["agents-md", "codex-agent", "codex-cli", "codex-sessionstart-ci-status-hook", "codex-subagentstart-dispatch-lens-hook", "codex-session-entry-hook",
 24687	                    "codex-stop-graph-sync-hook", "codex-pretooluse-impact-hook", "codex-skills"]
 24688	    check("enforcement: unknown 恰=vendored+遠端+Codex 不適用八列", unknown_layers == sorted(["required-status-check", "vendored-cli"] + codex_layers), str(unknown_layers))
 24689	    check("enforcement: n_unknown 恰 11", n_unknown == 11, f"{n_unknown}")
 24690	    check("enforcement: 四 hook+pre-commit+pre-push+python+ci 共 8 active", n_active == 8, f"active={n_active} rows={[(r['layer'],r['status']) for r in rows]}")
 24691	    check("enforcement: total = 非unknown列數", n_total == len(rows) - n_unknown, f"total={n_total} rows={len(rows)}")
 24692	
 24693	
 24694	def t_enforcement_never_raises_on_missing():
 24695	    m = _load_lumos_inproc()
 24696	    # 完全不存在的 root/home 也不該炸(fail-open 自身可觀測)
 24697	    bad = Path(tempfile.mkdtemp(prefix="gctl-enf-bad-")) / "nope"
 24698	    rows = m.enforcement_status(root=bad, home=bad)
 24699	    # r1 審:別留 >=8 的鬆口,釘死列數(5 hook+pre-commit+pre-push+python+vendored+ci+anchor+required = 12;2026-09-03 加 dispatch-lens;
 24700	    # 2026-09-04 Codex完全支援 S0 加 9 列:codex-hook×5+codex-cli+claude-skills+codex-skills+agents-md = 21)
 24701	    check("enforcement: 缺目錄不炸、回恰 22 列(d6 加 codex-agent)", isinstance(rows, list) and len(rows) == 22, f"{len(rows)}: {[r['layer'] for r in rows]}")
 24702	
 24703	
 24704	def _isolate_environment():
 24705	    """★把整輪測試關進拋棄式的家目錄與暫存目錄★(2026-09-06 全 repo 審視 #11)。
 24706	
 24707	    出身:兩支 install 測試直接跑 `lumos install --force` 而且沒帶任何環境隔離,
 24708	    所以★每跑一次全套,開發機真正的 ~/.claude 與 ~/.agents 底下的 skill 連結就被
 24709	    刪掉重建一次★(實測:連結的 inode 從 37184038 變成 37197577)。同型事故發生過兩次
 24710	    ——2026-08-01 刪掉真機的 hook、2026-09-02 重連真 skills——兩次之後「假 HOME 是
 24711	    最低門檻」都只寫在事故筆記裡,沒有任何機制擋住。
 24712	
 24713	    另一半是暫存殘骸:系統暫存目錄底下累積了 34 萬個 gctl-* 測試殘骸,連 `ls` 都會卡住。
 24714	    測試自己用的是 `tempfile.mkdtemp(prefix="gctl-...")`,沒有人收尾。
 24715	
 24716	    ★為什麼修在唯一進入點★:跟 main() 裡清 git 環境變數同一個理由——替代方案是「每支會碰
 24717	    家目錄的測試各自隔離」,那是幾十個呼叫點的分支簿記,天生會漏(這個專案已經漏過兩次)。
 24718	    關在進入點,對現有與未來新增的測試都自動成立。
 24719	
 24720	    ★為什麼這次抽成函式,而前兩個同型前例是就地展開的★(r1 架構席問的,答案寫在這裡免得
 24721	    以後有人以為是隨手寫的):清 git 環境變數那段是 7 行的 pop 迴圈、檔頭那個版本釘是 3 行,
 24722	    就地展開讀起來就是一段敘事。這一段要建目錄、寫一份 git 身分設定、還要掃系統暫存目錄
 24723	    做修剪,量體差一個數量級,塞進 main() 會把「這輪要跑哪些測試」的主線淹掉;而且它有
 24724	    回傳值(這一輪的根,收尾要用),就地展開會多一個裸露的區域變數。**論證形狀一樣
 24725	    (唯一進入點),只是實作成函式**——不是另立一套隔離手法。
 24726	
 24727	    既有的 per-call 假家目錄 helper(_teardown_run / _codex_run 那種)不受影響也沒變多餘:
 24728	    它們要的是「內容由那支測試自己控制、可以拿來斷言」的假家目錄,跟這裡的全域兜底互補。
 24729	    兩者疊起來時,呼叫端自己帶的 env 覆寫一律贏。
 24730	
 24731	    回傳這一輪的根目錄(收尾要用)。
 24732	    """
 24733	    import os, tempfile, shutil, time
 24734	    real_tmp = tempfile.gettempdir()
 24735	    root = Path(tempfile.mkdtemp(prefix="gctl-run-", dir=real_tmp))
 24736	
 24737	    # ① 暫存:之後所有 tempfile.mkdtemp() 與子進程的 TMPDIR 都落在這一輪的根底下
 24738	    tempfile.tempdir = str(root)
 24739	    os.environ["TMPDIR"] = str(root)
 24740	
 24741	    # ② 家目錄:換成拋棄式的
 24742	    home = root / "home"
 24743	    (home / ".config").mkdir(parents=True, exist_ok=True)
 24744	    # git 在沒有全域設定的家目錄下會抱怨身分;先給一份,免得測試裡的 git 指令噴錯
 24745	    (home / ".gitconfig").write_text(
 24746	        "[user]\n\tname = lumos-test\n\temail = lumos-test@example.invalid\n"
 24747	        "[init]\n\tdefaultBranch = main\n", encoding="utf-8")
 24748	    os.environ["HOME"] = str(home)
 24749	    os.environ["USERPROFILE"] = str(home)
 24750	    # CODEX_HOME 若在開發機上設過,會繞過假家目錄直接打到真的 ~/.codex
 24751	    os.environ.pop("CODEX_HOME", None)
 24752	    # ★LUMOS_HOME 不是使用者家目錄,是「lumos 來源 repo 在哪」★——一開始我把它也設成假家目錄,
 24753	    #   結果有支測試找不到來源就跳過了(跑得到變跑不到=覆蓋悄悄少掉,是比 skip 數字才發現)。
 24754	    #   它的預設值是 ~/harness/lumos-toolchain,家目錄一換成假的那條路就斷了。
 24755	    # ★但不能無條件指向「這個 repo」★(r1 外家席抓到):這支測試檔會被複製進消費專案,
 24756	    #   在那邊 repo 根就是消費專案自己,於是「vendored 的工具是不是最新版」這條檢查會
 24757	    #   **拿自己跟自己比,永遠判最新**——過期的工具在消費端會被說成沒問題,是假綠。
 24758	    #   所以只有確認自己就是來源 repo 時才指向自己;不是的話讓它保持找不到,
 24759	    #   那條路本來就該走跳過通道(誠實的「沒驗到」勝過假的「驗過了」)。
 24760	    repo_root = Path(GRAPHCTL).resolve().parent.parent
 24761	    if (repo_root / "skills" / "lumos-project-notes").is_dir():
 24762	        os.environ["LUMOS_HOME"] = str(repo_root)
 24763	    else:
 24764	        os.environ.pop("LUMOS_HOME", None)
 24765	
 24766	    # ③ 修剪舊殘骸:只碰「已標記結束」或「超過一天沒動」的本輪型根目錄。
 24767	    #    ★不按數量硬刪★——hook 會平行起 runner,刪掉別人正在用的根就是製造假紅。
 24768	    try:
 24769	        cutoff = time.time() - 86400
 24770	        pruned = 0
 24771	        with os.scandir(real_tmp) as it:
 24772	            for e in it:
 24773	                if not e.name.startswith("gctl-run-") or not e.is_dir(follow_symlinks=False):
 24774	                    continue
 24775	                p = Path(e.path)
 24776	                done = (p / ".finished").exists()
 24777	                try:
 24778	                    old = e.stat(follow_symlinks=False).st_mtime < cutoff
 24779	                except OSError:
 24780	                    continue
 24781	                if done or old:
 24782	                    shutil.rmtree(p, ignore_errors=True)
 24783	                    pruned += 1
 24784	                    if pruned >= 200:      # 一輪最多清這麼多,不要讓收尾變成掃地大會
 24785	                        break
 24786	    except OSError:
 24787	        pass
 24788	    return root
 24789	
 24790	
 24791	def main():
 24792	    # ★把 git 的環境變數從進程 env 清掉(2026-08-01,pre-push 假紅實錘)★
 24793	    #
 24794	    # 症狀:同一個 commit、同一棵樹,直接跑 `python3 scripts/test_lumos.py` 是
 24795	    # 2039 passed / 0 failed,但由 pre-push hook 跑同一支就 3~5 條紅,而且每次
 24796	    # 紅的條數還不一樣。
 24797	    #
 24798	    # 真因:`git push` 會把 `GIT_DIR` 這類變數 export 給 hook,hook 再把整個
 24799	    # env 傳給測試進程。大量測試會自己 `git init` 一個臨時 repo 再對它下 git
 24800	    # 指令——但 `GIT_DIR` 一旦存在就★覆蓋 cwd 推斷★,那些 git 指令全部打到
 24801	    # 本 repo 而不是臨時 repo,行為當然對不上。實測把 `GIT_DIR` 指向本 repo
 24802	    # 再跑,紅的條數暴增到 65,機制確認。
 24803	    #
 24804	    # 為什麼修在這裡:替代方案是「每個建臨時 repo 的測試各自清 env」——那是
 24805	    # 幾十個呼叫點的分支簿記,天生會漏(本專案 2026-08-01 才因為同型的分支簿記
 24806	    # 漏一條被代碼審抓到)。清在唯一進入點,對現有與未來新增的測試都自動成立。
 24807	    #
 24808	    # ★為什麼這不是把閘關掉★:清掉的是「測試進程該用哪個 repo」的外部注入,
 24809	    # 不是任何斷言。清完之後 hook 跑出來的結果會跟人手跑的一致——閘從「會給
 24810	    # 假紅」變成「可信」,是加嚴不是放寬。一個持續給假紅的閘,下一次就會被人
 24811	    # 用 --no-verify waive 掉,那才是真的把閘關掉。
 24812	    import os as _os_env
 24813	    for _v in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX",
 24814	               "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
 24815	        _os_env.environ.pop(_v, None)
 24816	
 24817	    # ★參數要嚴格解析★(2026-09-06 全 repo 審視 #12):原本用的是「不認得的參數就靜默丟掉」,
 24818	    # 於是 `--help`、打錯的旗標、甚至直接打測試名(情境錄音裡真的有人這樣敲),全部會被當成
 24819	    # 「沒帶任何條件」→ **直接跑滿八分鐘的全套**。實測:`--help` 當場把全套跑起來了。
 24820	    # 對照組 Codex 就曾因為在對話裡跑全套而超時。
 24821	    import argparse as _ap
 24822	    _p = _ap.ArgumentParser(
 24823	        prog="test_lumos.py",
 24824	        description="lumos 的測試執行器。不帶參數=跑全套(約 8 分鐘);"
 24825	                    "要跑子集就給關鍵字,它會比對測試函式名。")
 24826	    _p.add_argument("keyword_pos", nargs="?", default=None, metavar="關鍵字",
 24827	                    help="跟 -k 一樣(直接打名字比較順手)")
 24828	    _p.add_argument("-k", dest="keyword", default=None, help="只跑名稱含此字串的測試")
 24829	    _p.add_argument("--list", action="store_true", help="只列出測試名稱,不跑")
 24830	    _p.add_argument("--keep-tmp", action="store_true",
 24831	                    help="跑完不要刪這一輪的暫存根目錄(要進去翻現場時用)")
 24832	    _p.add_argument("-x", "--exitfirst", action="store_true",
 24833	                    help="第一支紅就停(不用等剩下的跑完才看到)")
 24834	    _p.add_argument("--ff", action="store_true",
 24835	                    help="上次紅過的先跑(配 -x 用,最快知道修好沒)")
 24836	    _p.add_argument("--seed", type=int, default=None, metavar="N",
 24837	                    help="用這個亂數種子打亂測試順序,探順序相依;紅了會把種子印出來讓你重現")
 24838	    _p.add_argument("--shard", default=None, metavar="第幾片/共幾片",
 24839	                    help="只跑其中一片(例:2/4)。推送前的閘用它把八分鐘拆成幾片同時跑")
 24840	    _p.add_argument("--json-summary", default=None, metavar="檔案",
 24841	                    help="把這一片的結果(過/紅/跳過/紅的是哪幾支)寫成 JSON,給彙總的人讀")
 24842	    _args = _p.parse_args()
 24843	    if _args.keyword and _args.keyword_pos:
 24844	        print("擋下:關鍵字給了兩次(-k 一次、直接打一次),只留一個", file=sys.stderr)
 24845	        return 2
 24846	    if _args.keyword_pos:
 24847	        _args.keyword = _args.keyword_pos
 24848	    _run_root = _isolate_environment()
 24849	    try:
 24850	        tests = [v for k, v in sorted(globals().items()) if k.startswith("t_")]
 24851	        if _args.shard:
 24852	            # ★分片★:把測試名排序後平均切成 N 片,只跑第 I 片。
 24853	            # 切的依據是「排序後的位置」,不是執行順序——所以同一個 I/N 每次拿到的內容一樣,
 24854	            # 跟 --seed 打不打亂無關(打亂只影響片內順序)。
 24855	            try:
 24856	                _i, _n = (int(x) for x in _args.shard.split("/", 1))
 24857	            except ValueError:
 24858	                print(f"擋下:--shard 要寫成「第幾片/共幾片」,例如 2/4;收到的是 {_args.shard!r}",
 24859	                      file=sys.stderr)
 24860	                return 2
 24861	            if _n < 1 or not (1 <= _i <= _n):
 24862	                print(f"擋下:--shard {_args.shard} 不合理(第幾片要在 1 到共幾片之間)", file=sys.stderr)
 24863	                return 2
 24864	            tests = [t for k, t in enumerate(tests) if k % _n == _i - 1]
 24865	            print(f"這是第 {_i} 片(共 {_n} 片),分到 {len(tests)} 支")
 24866	            if not tests:
 24867	                print(f"擋下:第 {_i} 片一支測試都沒分到——片數比測試數還多,或切法寫錯了;"
 24868	                      f"跑了個寂寞不算通過", file=sys.stderr)
 24869	                return 1
 24870	        if _args.list:
 24871	            # ★r1 折入★:原本 --list 排在關鍵字與分片之前,所以 `--shard 2/4 --list` 會列出全部
 24872	            # ——正好是「想確認某一片分到哪些」時最需要的資訊,卻給了錯的答案。移到篩選之後。
 24873	            for _t in tests:
 24874	                print(_t.__name__)
 24875	            return 0
 24876	
 24877	        # ★上次紅過的先跑★:配 -x 用,修完重跑幾秒就知道好了沒,不用等八分鐘。
 24878	        # ★r1 折入:排序必須在分片之後★——原本先重排再分片,而各片是獨立行程、
 24879	        #   讀到的快取可能不同(某片先跑完就把快取覆蓋掉了),於是「第 k 支」對不同片
 24880	        #   指的不是同一支,**各片聯集不再等於全部:有些跑兩次、有些一次都沒跑**。
 24881	        #   分片先做(在穩定的排序清單上切),重排只影響片內順序,聯集就永遠正確。
 24882	        # ★r1 折入:快取只在來源 repo 寫★——這支測試檔會被複製進消費專案,
 24883	        #   而安裝時只幫 docs/ 底下寫忽略規則,不會忽略 .lumos/,所以在消費端寫這個檔
 24884	        #   等於污染別人的工作樹。
 24885	        _is_src = (Path(GRAPHCTL).resolve().parent.parent / "skills" / "lumos-project-notes").is_dir()
 24886	        _cache_dir = Path(GRAPHCTL).resolve().parent.parent / ".lumos"
 24887	        _cache = _cache_dir / (f"test-cache-shard{_args.shard.replace('/', 'of')}.json"
 24888	                               if _args.shard else "test-cache.json")
 24889	        _last_failed = []
 24890	        if _is_src:
 24891	            try:
 24892	                import json as _jc
 24893	                for _f in sorted(_cache_dir.glob("test-cache*.json")):
 24894	                    _last_failed += _jc.loads(_f.read_text(encoding="utf-8")).get("failed", [])
 24895	            except (OSError, ValueError):
 24896	                pass
 24897	        if _args.ff and _last_failed:
 24898	            _lf = set(_last_failed)
 24899	            _n_first = len([t for t in tests if t.__name__ in _lf])
 24900	            tests = [t for t in tests if t.__name__ in _lf] + [t for t in tests if t.__name__ not in _lf]
 24901	            print(f"上次紅過的 {_n_first} 支排到最前面")
 24902	        elif _args.ff:
 24903	            print("(沒有上次紅過的紀錄,照原順序跑)")
 24904	        if _args.seed is not None:
 24905	            # ★順序相依探針★:預設關,只給每日治理跑;紅了印種子讓人原樣重現。
 24906	            import random as _rnd
 24907	            _rnd.Random(_args.seed).shuffle(tests)
 24908	            print(f"這輪用種子 {_args.seed} 打亂了順序(要重現同一種順序就帶同一個種子)")
 24909	        if _args.keyword:
 24910	            tests = [t for t in tests if _args.keyword in t.__name__]
 24911	            if not tests:
 24912	                # 假綠洞修補:-k 選中 0 案例 ≠ 全綠——「跑了個寂寞」必須紅,
 24913	                # 否則消費 rc 的一方(hook/CI 等機制)會把「沒驗」當「驗過」。
 24914	                print(f"✗ -k '{_args.keyword}' 選中 0 個測試(t_ 名單無此子字串)——視為失敗", file=sys.stderr)
 24915	                return 1
 24916	        print(f"lumos 測試({len(tests)} 案例)")
 24917	        global FAIL, SKIP
 24918	        _failed_names = []
 24919	        for t in tests:
 24920	            _round_fail_before = FAIL
 24921	            try:
 24922	                # ★單一處的自動規則,不往每支測試塞一行★:`t_slim_*` 整族驗的是「交付包」
 24923	                # (slim/ 底下的產物 + slim-gen/slim-scan),那是來源 repo 專用。用前綴在
 24924	                # 這裡一次涵蓋,★新增的 t_slim_* 自動繼承★——往 40 個函式各插一行才是
 24925	                # 會漏的分支簿記(本專案 2026-08-01 剛因同型簿記漏一條被代碼審抓到)。
 24926	                # 判定仍是狀態驅動:`slim/` 真的在(來源 repo)就照跑,零行為改變。
 24927	                if t.__name__.startswith("t_slim_"):
 24928	                    _need_src("slim")
 24929	                _fail_before, _pass_before = FAIL, PASS
 24930	                _t_start = _time_slow.time()
     1	---
     2	type: issue
     3	status: open
     4	created: 2026-08-22
     5	updated: 2026-08-22
     6	aliases: []
     7	tags:
     8	  - type/issue
     9	  - status/open
    10	summary: |-
    11	  FLAG:ORIGIN
    12	  KEY:症狀=同一台機器同一個工作目錄開兩個對話一起做事,改動互相波及;git 不會攔,四層閘(git / pre-commit / pre-push / doctor / hook)沒有一層的輸入裡有「session」這個維度
    13	  KEY:2026-08-22 一天三型:①數字漂移(紅得像自己改壞的)②提交夾帶(git add -A 把對方全部交付一起 commit、訊息只寫自己那件)③變數共用(結果好但純靠人主動講)
    14	  KEY:★2026-09-07 第四型(新)★=對方存到一半的壞檔讓這邊每個指令都失敗,而且★錯誤訊息長得像自己造成的★;這型是瞬時的(壞檔只存在幾秒,事後查不到現場),而且會誘發破壞性補救(差一點就去「修」對方寫到一半的檔)
    15	  KEY:候選解多兩條——(d) 同工作區 session 互相通報(這次真正管用的就是對方主動傳訊,機器對機器不是人轉述;它擋的是誤修與提交夾帶,不是壞檔本身,而且要兩邊都記得);★(e) 寫側做原子存檔(寫 tmp→自驗→原子改名),壞檔窗口是零而不是幾秒,而且★單邊就能生效的解天生比雙邊解可靠★;(e) 是這個 repo 本來就有的慣例(scripts/lumos 就有現成函式、圖譜至少六篇寫過),只是沒人套用在「AI 改共用工具檔」上
    16	  KEY:★我在寫這篇時自己又犯一次同型★——第一版寫「(d) 是唯一能處理瞬時壞檔的做法」,被另一個 session 更正、查證後確認我錯;而那句話寫下去的時間距離我寫完 [[Issues/把自己的推論寫成repo明文寫過]] 不到一小時。「唯一/一定/不可能/從來沒有」跟引號一樣,寫下去之前要先查
    17	  KEY:★更正「(d) 是唯一能處理瞬時壞檔那一型」的說法(寫的那一邊 2026-09-07 補)★——瞬時壞檔的成因在**寫的那一邊分兩次存檔**,中間留下語法壞掉的窗口;本 repo 既有慣例「寫入一律 tmp→自驗→atomic」本來就擋得住,只是那次沒套用在「改共用工具檔」上。★(e) 寫側原子存檔比 (d) 互相通報更根治★:通報要兩邊都記得,原子存檔只要寫的那一邊做;(d) 仍有價值,但價值在「知道有人在動這支檔」不在「防壞檔」
    18	  KEY:現在就照做的三條紀律=①多開時逐檔 git add 不准 -A ②指令突然壞掉且錯誤指向共用檔時先看那支檔的修改時間,幾秒前被動過就是別人在寫、不要動手修 ③不要替另一個 session 修它寫到一半的東西
    19	  DECISION:2026-09-01 Enzo 委任裁:誤報量測不辦(無自然數據源,硬量=再造假指標);維持「三型再犯時回看」的事件入口。2026-09-07 第四型觸發回看,結論=先照上面三條紀律,REVISIT:2026-10-07 第五次再犯就把 (b) 或 (d) 做成機械
    20	---
    21	# 同工作區多session並行改動
    22	
    23	> ★2026-09-01 Enzo 委任裁:誤報量測不辦——無自然數據源,硬量=再造假指標(引圖譜率案同週教訓);維持「三型再犯時回看」的事件入口★
    24	
    25	> 白話:同一台機器、同一個工作目錄開兩個 Claude 對話一起做事,改動會互相波及。
    26	> **git 不會攔,也沒有任何工具會喊。** 2026-08-22 一天撞到三次,兩次有實害。
    27	
    28	## 三次實例(全部同一天,2026-08-22)
    29	
    30	### ① 數字漂移:A 改的、B 修的、擋了測試
    31	
    32	一邊把 `gov` 彙整的其中一本帳(rot-queue)的 loader 拆掉(寫帳的 hook 前一天已撤,留著是假名額),
    33	但沒更新 [[Systems/reversibility-governance-ledger]] 裡「7 源」那個 Check N 可重算標記。
    34	
    35	另一邊(不知情)跑全套測試,紅了一條——`t_claude_block_matches_template` 釘死
    36	「本 repo doctor 整體 0 issues」,而 Check N 抓到 7 宣稱 vs 6 實測。
    37	
    38	**★這條紅看起來像自己改壞的★**,查了半天才確定是另一個 session 的改動。
    39	
    40	### ② 提交夾帶:訊息完全對不上內容
    41	
    42	一邊做完自己的功能,`git add -A` 一掃,把另一邊當天全部的交付(三件功能 + 六篇圖譜改動)
    43	一起 commit 進去,**訊息只寫自己的那件**。
    44	
    45	被夾帶的內容本身是完整的(code 與測試沒被拆開),所以**沒有品質風險,但歷史讀不出真相**。
    46	發現時還沒 push,已 amend 補一段「同批夾帶:…」載明來源。
    47	
    48	★如果那時已經 push,就只能留一筆對不上的歷史★——這是本條最接近實害的一次。
    49	
    50	### ③ 變數共用:結果是好的,但純靠人主動講
    51	
    52	一邊新加的閘要用超時控制,直接沿用另一邊當天加的 `LUMOS_TEST_TIMEOUT`,沒有另立變數,
    53	並主動傳訊說「你若改它的語意,這邊跟著動」。
    54	
    55	**結果是好的**——沒長出第二個平行變數。但這完全來自那一邊主動開口,
    56	**沒有任何機制會告訴你「你要改的這個東西,另一個 session 正在依賴」**。
    57	
    58	## 為什麼現有的閘全部接不住
    59	
    60	- **git**:同一個工作目錄就是同一棵樹,兩邊的改動天生混在一起。`git status` 分不出誰改的。
    61	- **pre-commit / pre-push**:驗的是「這批改動合不合規」,不問「這批改動是不是同一個人的」。
    62	- **`lumos doctor`**:驗圖譜一致性,對「改動來自幾個 session」沒有概念。
    63	- **hook 推的必看合約**:推的是「你碰的檔關聯到哪些筆記」,不是「這個檔另一個 session 也在碰」。
    64	
    65	**四層閘沒有一層的輸入裡有「session」這個維度。**
    66	
    67	## 最小解形狀(★未立案,待裁★)
    68	
    69	判準照家規:有症狀(三次,兩次有實害)、有消費者(同時開兩個對話的人=Enzo 本人),
    70	但**最小解在哪一層還沒想清楚**,所以只記不做:
    71	
    72	- **(a) 零機制,純紀律**:多開之前先講好誰動哪些檔。★問題:紀律沒有機械守衛,
    73	  而本 repo 已有一整張 [[Issues/散文紀律沒有退場機制]] 在講這型的失效。★
    74	- **(b) 提交時提醒**:pre-commit 看 `git diff --cached` 涉及的檔,若有檔案的
    75	  mtime 明顯早於本 session 起始時間 → 印一句「這批可能夾帶了別人的改動」。
    76	  ★零依賴、可機械判、不擋。但 mtime 是弱訊號,誤報率沒量過。★
    77	- **(c) 用 git worktree 隔離**:各開各的工作樹,從根本上不共用。
    78	  ★最乾淨,但代價是兩邊看不到對方的即時改動,而今天有幾次「看得到」反而是好事
    79	  (數字漂移是另一邊順手修掉的)。★
    80	
    81	**我的傾向是 (b)**,理由:(a) 沒守衛、(c) 代價大且會擋掉今天證明有用的互相補位。
    82	但 (b) 的誤報率沒量過,量之前不該立案。
    83	
    84	## 重驗條件
    85	
    86	**下一次同工作區多開對話時,看這三型有沒有再犯。** 再犯一次、或出現一次
    87	「已 push 才發現夾帶」的實害 → 升級為待處理,先量 (b) 的誤報率。
    88	
    89	## 這條不涵蓋什麼
    90	
    91	- **不涵蓋跨機器/跨 repo 的並行**——那是 [[Projects/跨session傳訊用途調研]] 的射程。
    92	- **不涵蓋「兩個 session 該不該同時開」**——今天的實跑證明對審本身價值很高
    93	  (另一邊打掉了三個站不住的提案、抓到一個會出事的超時設定)。
    94	  ★本條只談「共用同一棵工作樹」的代價,不談協作本身。★
    95	
    96	---
    97	
    98	## 第四次(2026-09-07):新型——**對方存到一半的壞檔,讓我這邊每個指令都失敗**
    99	
   100	事件入口成立(那條裁定寫的是「三型再犯時回看」),而且這次是**前三型都沒有的第四型**。
   101	
   102	### 發生什麼
   103	
   104	同一棵工作樹,一邊在跑設計審迴圈、一邊在做執行 DAG 調研並實作一支新子命令。
   105	調研那邊改到 `scripts/lumos` 的過程中,檔案短暫處於**語法壞掉**的狀態
   106	(字串裡出現真的換行)。這邊在那個瞬間跑 `lumos lint`,拿到的是 Python 的語法錯誤。
   107	
   108	★關鍵是它長得不像別人造成的★:訊息是「`scripts/lumos` 第 5341 行字串沒收尾」,
   109	第一反應會是「我自己剛剛寫壞了什麼」。我開始查損壞範圍、準備動手修——
   110	**再看一次發現它自己好了,檔案修改時間是 7 秒前。** 那時才確定是另一邊正在即時寫。
   111	
   112	### 為什麼這型比前三型更難
   113	
   114	- 前三型(數字漂移、提交夾帶、變數共用)都是**事後**才發現,但發現時證據還在。
   115	- 這一型是**瞬時的**:壞檔可能只存在幾秒。等你去查,現場已經沒了,
   116	  而你手上只有一個看起來像自己造成的錯誤訊息。
   117	- **它會誘發破壞性的補救**:我差一點就動手「修」對方寫到一半的檔。
   118	  真的修下去,就是兩邊同時改同一段——比原本的問題嚴重得多。
   119	
   120	### 這次沒有實害的原因,以及它有多脆
   121	
   122	- **沒有夾帶**:我最後一個提交(08b0e61)時間點剛好在對方開始改之前,查證過沒有夾到。
   123	  ★但這是運氣,不是機制★——我整場用的都是 `git add -A`,正是第二型點名的那個動作。
   124	- **沒有誤修**:因為我多看了一次修改時間。★如果我第一次就動手,就出事了★。
   125	
   126	### 這次真正管用的是什麼(值得記,因為它不在上面任何一個候選解裡)
   127	
   128	**對方主動傳了一則訊息過來**,列出它動了哪些檔、明說它不會 commit、並提醒不要用 `-A`。
   129	這跟第三型「純靠人主動講」是同一件事——**但這次是機器對機器講的,不是人轉述**。
   130	
   131	所以最小解的候選清單要多一條:
   132	
   133	- **(d) 同工作區的 session 之間直接互相通報**:開工時廣播「我要動哪些檔」,
   134	  收工時廣播「我停手了」。成本近乎零。
   135	  ★它擋的是「誤修」與「提交夾帶」,不是壞檔本身★——知道有人在動那支檔,你就不會去修它。
   136	  問題:要兩邊都記得,忘了講就沒有。
   137	- **(e) 寫側做原子存檔**(★寫的那一邊自己就能解決,不必兩邊配合★):
   138	  寫暫存檔 → 自驗(對 Python 檔就是重新 parse 一次)→ 原子改名。
   139	  **壞檔窗口是零,不是「幾秒」**。
   140	  ★這條是這個 repo 本來就有的慣例,只是從來沒有人把它套用在「AI 改共用工具檔」上★:
   141	  圖譜裡至少六篇計劃寫過「寫入一律 tmp→自驗→atomic」這條約束,
   142	  而且 `scripts/lumos:9202` 有一支 `atomic_write_verify` 已經把這個形狀實作出來。
   143	  **單邊就能生效的解,天生比雙邊解可靠**——(d) 要兩邊都記得,(e) 只要寫的那一邊做。
   144	
   145	  ★精修(造成方 2026-09-07 開檔複驗後補):那支函式不能直接拿來用★——
   146	  它的射程是**筆記的開頭欄位**:會去 parse frontmatter、確認要寫的欄位值真的寫進去了、
   147	  並比對「有沒有引入新的 lint 指紋」,失敗就丟掉暫存檔、原檔不動。
   148	  ★拿它去寫一支 `.py` 會直接爆掉★(那支檔沒有 frontmatter 可 parse)。
   149	  所以可借的是**形狀**不是函式本身;而且它的自驗比「`ast.parse` 過得去」更嚴——
   150	  它問的是「寫回去的值真的是我要的嗎、有沒有順手弄壞別的東西」。
   151	  改 Python 原始碼的對應物是:寫 tmp → `ast.parse` → (可選)跑一次相關測試子集 → `os.replace`。
   152	  **這個精修本身就是「宣稱程式碼是怎樣」那一型**:寫「現成函式就在那裡」讀起來像可以直接呼叫,
   153	  實際上射程完全不同——要開檔看過才知道。
   154	
   155	### ★我在這一段自己又犯了一次同型★
   156	
   157	上面 (d) 那條,我第一版寫的是「**它是唯一能處理瞬時壞檔那一型的做法**」。
   158	另一個 session 更正我,我去查證之後確認**它是對的、我那句「唯一」是錯的**——
   159	(e) 不但存在,而且更好,而且是這個 repo 自己的既有慣例。
   160	
   161	**時間點值得記**:我寫那句「唯一」的時候,距離我寫完
   162	[[Issues/把自己的推論寫成repo明文寫過]](內容就是「我把沒查過的東西寫成肯定句」)不到一小時。
   163	★同一個病在同一小時內換一種形狀再犯:那次是編引言,這次是說「唯一」。★
   164	共同形狀還是那個——**需要一個結論來收尾,就順手寫了一個絕對的說法,而且沒查。**
   165	「唯一」「一定」「不可能」「從來沒有」這幾個詞,跟引號一樣,寫下去之前要先查。
   166	
   167	### 這次得到的可操作紀律(不是候選解,是現在就照做的)
   168	
   169	1. **多開時一律逐檔 `git add`,不准 `-A`**。這條之前就寫在第二型裡,但沒有人在遵守——
   170	   ★包括我自己整場都在犯★。
   171	2. **指令突然壞掉、而錯誤指向一支共用檔時,先看那支檔的修改時間**。
   172	   幾秒前被動過就是別人在寫,**不要動手修**。
   173	3. **不要替另一個 session 修它寫到一半的東西**——等它說停手。
   174	
   175	### ★寫的那一邊怎麼造成的(2026-09-07 由造成方補;只有寫的人知道)★
   176	
   177	**成因是「分兩次存檔」,不是「寫得慢」。**
   178	
   179	那次改 `scripts/lumos` 是用腳本做字串替換再整檔寫回。第一次寫進去的內容裡,
   180	字串常數中的換行跳脫被產生器展開成**真的換行**,檔案當場語法壞掉;
   181	發現後第二次寫回才修好。**兩次寫入之間大約一分鐘,樹上放著一支壞檔。**
   182	
   183	★這裡的關鍵:本 repo 早就有一條慣例能擋住它★——實作計畫的共同約束寫著
   184	**「寫入一律 tmp→自驗→atomic」**。那條一直被當成「工具寫帳本」時的規矩,
   185	**沒有人把它套用在「AI 自己改共用工具檔」上**。這次證明兩者是同一件事。
   186	
   187	**寫側的最小解(成本近乎零,只要寫的那一邊做)**:
   188	
   189	1. 產生新內容 → 寫到暫存檔;
   190	2. 就地自驗(Python 檔就 `ast.parse`,JSON 就 `json.loads`);
   191	3. 驗過才原子換上去(`os.replace`)。
   192	
   193	這樣壞檔的窗口是**零**,而不是「幾秒」。
   194	
   195	### 因此要更正上面一句話
   196	
   197	上面寫「(d) 同工作區 session 互相通報**是唯一**能處理瞬時壞檔那一型的做法」——**這句不成立**。
   198	
   199	- **(e) 寫側原子存檔**才是根治:它消掉的是壞檔本身,而不是消掉「被誤判成自己造成的」這個後果。
   200	- 而且 **(e) 只需要寫的那一邊做**,(d) 要兩邊都記得廣播——★單邊就能生效的解,天生比雙邊解可靠★。
   201	- **(d) 仍然有價值,但價值不在防壞檔**:它的價值是「知道現在有人在動這支檔」,
   202	  那能擋掉的是**誤修**(第四型裡差一點發生的破壞性補救),以及第二型的提交夾帶。
   203	
   204	### 這一段不涵蓋什麼
   205	
   206	- **(e) 沒有機械守衛**,跟 (a)(d) 一樣是紀律;差別只在它是單邊的。要做成機械得攔 AI 的寫檔動作,
   207	  那是另一個層級的東西,本次不主張。
   208	- **本次沒有量過**「分兩次存檔」在日常改動裡佔多少比例——只知道這次是這樣。
   209	
   210	REVISIT:2026-10-07 若第五次再犯(任何型),就是紀律解已經證明不夠,
   211	把 (b) 提交時提醒 或 (d) session 互相通報 其中一條做成機械。
    55	> 這篇是那個歸納,加上世界對它的見解與數字。
    56	
    57	PRIOR-ART:★世界有大量研究,而且給得出數字★——①引用支持力:14 個模型×130 題,「連結打得開」94–100%、「內容同主題」>80%、★「來源真的支持該主張」24–77%★(arXiv 2605.06635);②記憶下毒:內容篩檢對 360 筆假事實★一筆都攔不下★,且作者主張這類「原理上」篩不出來(arXiv 2608.21230);③機械強制 vs 散文治理:2400 案對照,★純文字治理有 27% 是「化妝式合規」★,機械強制降到 7.4%(arXiv 2605.14744)。這三條分別對應本 repo 的 `[src:]`、AI 回寫、與「散文紀律 vs 機械守衛」家規。
    58	
    59	## 這篇的歸納(★是我的歸納,不是查到的;推翻條件寫在最後★)
    60	
    61	兩份調研的存活缺口攤開後分成**兩族**,混在一起談會誤判:
    62	
    63	**家族甲:宣稱與現實脫鉤,而且沒有東西會發現。**
    64	- 勾選框沒人勾、`status/doing` 停滯、翻案待辦零判定、提醒喊 185 次沒人理、settle 35 條全部規格雜湊過期。
    65	- 共同點:**狀態是手寫的,沒有可重算的來源,寫下去就開始漂**。
    66	- ★這一族已有被證明有效的自家解法★:`loop verify-progress` 的 help 自述「不看散文,只從帳本結構欄位看審到哪」——狀態從證據算,不給人維護。
    67	
    68	**家族乙:機械檢查了「形式」,沒檢查「內容」。**
    69	- `[src:路徑:行號]` 驗路徑在不在,不驗那行支不支持主張。
    70	- 「測試存在且綠」驗測試綠,不驗那個任務做完了(見 [[Projects/執行DAG_調研]] 外家 f2)。
    71	- 引句檢查驗那句話在不在快照裡(字串包含比對),不驗那句話有沒有被正確使用。
    72	- `--accept-reason` 驗非空,不驗理由成不成立。
    73	- `seat-check` 驗引句錨得進派工材料,不驗引句支不支持那條發現。
    74	
    75	★家族甲是紀律病,人也會犯;家族乙是 **AI 特有**的★——AI 極擅長生產「形式完全正確、內容不成立」的東西:一個真實的行號、一句真的存在的引文、一個非空的理由、一個綠色的測試。**每一項都通過機械檢查,而整體是錯的。**
    76	
    77	## 這個 repo 在家族乙已經做過三件事,結局不同
    78	
    79	| 面向 | 現況 | 證據 |
    80	|---|---|---|
    81	| **判官被人改過了嗎** | **有機制、活著** | `lumos anchor verify` 比對測試/hook 檔雜湊,不符 rc1 |
    82	| **判官醒著嗎** | ★試過,量完停用★ | canary 協議 2026-08-14 Enzo 裁停——「caught/missed 譯不出『認真』且無下游消費=空轉」([[Systems/canary-audit]] status:deferred) |
    83	| **證據支不支持主張** | ★空的★ | 見上;而接手煙霧偵測角色的引句檢查**本身也是形式檢查** |
    84	
    85	**所以「缺什麼」的答案不是「沒意識到」,是「這一族的第三格從來沒有人站上去過」。**
    86	
    87	## 世界的見解(逐條附數字與出處)
    88	
    89	### 1. 引用存在 ≠ 引用支持:世界已經把它拆成三層來量
    90	

exec
/bin/zsh -lc "nl -ba scripts/test_lumos.py | sed -n '24905,25030p'; git status --short" in /Users/enzo/harness/lumos-toolchain
 succeeded in 0ms:
 24905	            # ★順序相依探針★:預設關,只給每日治理跑;紅了印種子讓人原樣重現。
 24906	            import random as _rnd
 24907	            _rnd.Random(_args.seed).shuffle(tests)
 24908	            print(f"這輪用種子 {_args.seed} 打亂了順序(要重現同一種順序就帶同一個種子)")
 24909	        if _args.keyword:
 24910	            tests = [t for t in tests if _args.keyword in t.__name__]
 24911	            if not tests:
 24912	                # 假綠洞修補:-k 選中 0 案例 ≠ 全綠——「跑了個寂寞」必須紅,
 24913	                # 否則消費 rc 的一方(hook/CI 等機制)會把「沒驗」當「驗過」。
 24914	                print(f"✗ -k '{_args.keyword}' 選中 0 個測試(t_ 名單無此子字串)——視為失敗", file=sys.stderr)
 24915	                return 1
 24916	        print(f"lumos 測試({len(tests)} 案例)")
 24917	        global FAIL, SKIP
 24918	        _failed_names = []
 24919	        for t in tests:
 24920	            _round_fail_before = FAIL
 24921	            try:
 24922	                # ★單一處的自動規則,不往每支測試塞一行★:`t_slim_*` 整族驗的是「交付包」
 24923	                # (slim/ 底下的產物 + slim-gen/slim-scan),那是來源 repo 專用。用前綴在
 24924	                # 這裡一次涵蓋,★新增的 t_slim_* 自動繼承★——往 40 個函式各插一行才是
 24925	                # 會漏的分支簿記(本專案 2026-08-01 剛因同型簿記漏一條被代碼審抓到)。
 24926	                # 判定仍是狀態驅動:`slim/` 真的在(來源 repo)就照跑,零行為改變。
 24927	                if t.__name__.startswith("t_slim_"):
 24928	                    _need_src("slim")
 24929	                _fail_before, _pass_before = FAIL, PASS
 24930	                _t_start = _time_slow.time()
 24931	                run_with_timeout(t, TIMEOUT_OVERRIDE.get(t.__name__, TEST_TIMEOUT_SEC))
 24932	                SLOWEST.append((_time_slow.time() - _t_start, t.__name__))
 24933	                # ★跑完卻一條斷言都沒有=沒驗過,判紅★(2026-09-06 全 repo 審視 #13)
 24934	                # 跟「-k 選中 0 支判紅」同一個理由:綠燈必須代表「驗過而且過了」,不能代表
 24935	                # 「什麼都沒發生」。原本有十處寫成 check(…, True) 當跳過用,那是把「沒驗」
 24936	                # 記成 PASS;已全部改走 _SrcOnly 跳過通道,這條是防它再長回來的機械守衛。
 24937	                if FAIL == _fail_before and PASS == _pass_before:
 24938	                    FAIL += 1
 24939	                    print(f"  ✗ {t.__name__}: 跑完了但一條斷言都沒有(沒驗過≠通過;"
 24940	                          f"真的不該在這台跑就 raise _SrcOnly 走跳過通道)")
 24941	                elif FAIL > _fail_before:
 24942	                    # 殺傷力驗證歸因用(2026-08-22 首跑判「弱證據」):失敗要跟測試名同一行,
 24943	                    # lumos guard kill 的 _kill_attribute 才能把紅燈歸到綁定測試頭上。
 24944	                    print(f"  ✗ FAILED {t.__name__}({FAIL - _fail_before} 條斷言)")
 24945	            except _SrcOnly as e:
 24946	                SKIP += 1
 24947	                SKIPPED_NAMES.append(t.__name__)   # r1:只記總數的話,「換了一支跳過」量不到
 24948	                print(f"  - skip {t.__name__}: {e}")
 24949	            except TestTimeout as e:
 24950	                # ★判紅不判 skip★:沒跑完 = 沒驗過。名字印出來,才知道要去修哪一支。
 24951	                FAIL += 1
 24952	                print(f"  ✗ TIMEOUT {t.__name__}: {e}"
 24953	                      f"(調整:LUMOS_TEST_TIMEOUT=<秒>,0=不設限)")
 24954	            except Exception as e:
 24955	                FAIL += 1
 24956	                print(f"  ✗ {t.__name__} EXCEPTION: {e}")
 24957	            # 這一支有沒有紅,決定要不要進「上次紅過」的快取,以及 -x 要不要停在這裡
 24958	            if FAIL > _round_fail_before:
 24959	                _failed_names.append(t.__name__)
 24960	                if _args.exitfirst:
 24961	                    print(f"  停在第一支紅的({t.__name__});"
 24962	                          f"修完用 --ff -x 重跑,它會先跑這幾支")
 24963	                    if _args.seed is not None:
 24964	                        print(f"  這輪是打亂順序跑的,要原樣重現請帶 --seed {_args.seed}")
 24965	                    break
 24966	        # 把紅的名字留下來給 --ff 用(全綠就清空,免得舊名字一直排前面)
 24967	        # ★r1 折入:原子寫入★——沿用專案既有的 .lumos/*.json 寫法(寫暫存檔再 rename),
 24968	        #   不是直接覆蓋;分片時各片各寫各的檔名,不會互相蓋掉。
 24969	        if _is_src:
 24970	            try:
 24971	                import json as _jc2, os as _osc
 24972	                _cache.parent.mkdir(parents=True, exist_ok=True)
 24973	                _tmpc = _cache.with_suffix(_cache.suffix + ".lumos-tmp")
 24974	                _tmpc.write_text(_jc2.dumps({"failed": _failed_names}, ensure_ascii=False),
 24975	                                 encoding="utf-8")
 24976	                _osc.replace(_tmpc, _cache)
 24977	            except OSError:
 24978	                try:
 24979	                    _tmpc.unlink()
 24980	                except (OSError, NameError):
 24981	                    pass
 24982	        if SLOWEST:
 24983	            top = sorted(SLOWEST, reverse=True)[:5]
 24984	            print(f"\n最慢 5 支(超時上限 {TEST_TIMEOUT_SEC}s;餘裕 = 上限 / 最慢):")
 24985	            for sec, name in top:
 24986	                lim = TIMEOUT_OVERRIDE.get(name, TEST_TIMEOUT_SEC)
 24987	                ratio = (lim / sec) if sec > 0 else float("inf")
 24988	                flag = "  ⚠ 餘裕不足 3 倍" if ratio < 3 else ""
 24989	                lim_note = f"/上限 {lim}s" if name in TIMEOUT_OVERRIDE else ""
 24990	                print(f"  {sec:6.1f}s  {name}{lim_note}  (餘裕 {ratio:.0f}x){flag}")
 24991	        if _args.json_summary:
 24992	            # 機讀摘要:分片時給彙總的人讀(每片各寫一份)
 24993	            import json as _jsum
 24994	            try:
 24995	                Path(_args.json_summary).write_text(_jsum.dumps(
 24996	                    {"passed": PASS, "failed": FAIL, "skipped": SKIP,
 24997	                     "failed_names": _failed_names, "skipped_names": SKIPPED_NAMES,
 24998	                     "shard": _args.shard}, ensure_ascii=False), encoding="utf-8")
 24999	            except OSError as _e:
 25000	                print(f"  (寫不出機讀摘要:{_e})", file=sys.stderr)
 25001	        tail = f", {SKIP} skipped(來源 repo 專用)" if SKIP else ""
 25002	        print(f"\n{'─'*40}\n{PASS} passed, {FAIL} failed{tail}")
 25003	        # ★跳過的支數要有基準線★(2026-09-06 全 repo 審視 #11 現場學到的):
 25004	        # 我把一個環境變數設錯,害一支測試找不到來源就靜默跳過——全套照樣「零紅」,
 25005	        # 是我自己去比 skip 從 0 變 1 才發現。**跑得到變跑不到=覆蓋悄悄少掉,而它不會紅。**
 25006	        # 所以在這裡對基準線比一次:超過就出聲(只在跑全套時比,-k 子集本來就會跳很多)。
 25007	        # ★超過基準線要判紅,不是印個提醒就算★(r1 外家席抓到):只印不紅的話,
 25008	        # 覆蓋退化照樣以成功狀態碼離開,CI 與推送閘收到的還是 rc0——那就等於沒有這道基準線。
 25009	        # 只在「基準線有意義」的環境判:來源 repo(消費端本來就會跳過一批來源專用的)
 25010	        # 且非 Windows(Windows 分支的跳過是合法的)。其餘環境只印一行觀測,不判紅。
 25011	        if not _args.keyword and SKIP > EXPECTED_SKIP_MAX:
 25012	            _baseline_applies = (Path(GRAPHCTL).resolve().parent.parent / "skills" / "lumos-project-notes").is_dir() \
 25013	                and sys.platform != "win32"
 25014	            print(f"  這次跳過 {SKIP} 支,比預期上限 {EXPECTED_SKIP_MAX} 支多。"
 25015	                  f"跳過不會出現在紅字裡,但它代表那些測試這輪沒驗到。")
 25016	            # r1 折入:只印總數的話,「本來跳 A、現在改跳 B」這種換人的漂移量不到
 25017	            # ——兩邊相減淨額一樣。所以把名字列出來,人一眼看得出換的是誰。
 25018	            print(f"  跳過的是:{', '.join(SKIPPED_NAMES)}")
 25019	            if _baseline_applies:
 25020	                FAIL += 1
 25021	                print(f"  ✗ 判紅:這台是來源 repo 又不是 Windows,所有跳過通道的條件本來都不成立"
 25022	                      f"——多出來的跳過幾乎一定是現場被弄壞了(例如某個環境變數設錯,害測試找不到它要的東西)。")
 25023	                print(f"  確認過而且合理的話,把 EXPECTED_SKIP_MAX 調成 {SKIP} 並在旁邊寫一句為什麼,"
 25024	                      f"或設 LUMOSEXPECTED_SKIP_MAX=<數字> 暫時放行。")
 25025	            else:
 25026	                print(f"  (這台不是來源 repo 或是 Windows,跳過本來就會多,所以只記不判紅)")
 25027	        return 1 if FAIL else 0
 25028	    finally:
 25029	        # ★收尾一定要跑到★(r1 外家席抓到):原本寫在 return 之前,所以 `-k` 打錯字的早退、
 25030	        # Ctrl-C、以及測試迴圈外的例外通通會繞過它,把整個現場留在系統暫存目錄裡等一天後
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-P8qjNOmP' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tnlv4y7h' (errno=Operation not permitted)
 M README.en.md
 M README.md
 M docs/.canary-log.jsonl
 M docs/.governance-log.jsonl
 M docs/.usage-log.jsonl
 M "docs/lumos-toolchain-knowledge/Projects/\346\257\217\346\227\245\346\262\273\347\220\206wrapper\346\264\273\350\221\227\346\262\222_\350\250\210\345\212\203.md"
 M governance/.gitignore
 M governance/install-watchdog.sh
 M governance/wrapper-watchdog.sh
 M scripts/test_lumos.py
?? assets/lumos-icon.png
?? "docs/lumos-toolchain-knowledge/Projects/Agentflow\345\220\270\346\224\266_\350\252\277\347\240\224.md"
?? "docs/lumos-toolchain-knowledge/Projects/\351\200\262\345\272\246\345\276\236\346\217\220\344\272\244\346\216\250\345\260\216_\350\250\210\345\212\203.md"
?? "docs/lumos-toolchain-knowledge/Projects/\351\251\227\345\275\242\345\274\217\350\210\207\351\251\227\345\205\247\345\256\271_\350\252\277\347\240\224.md"
?? governance/rel-cascade/c-20260907073644-b400540a.jsonl
?? governance/rel-cascade/c-20260907073644-fcd8c840.jsonl
?? governance/rel-cascade/c-20260907075249-e3db946b.jsonl
?? governance/rel-cascade/c-20260907075250-33216948.jsonl
?? governance/review-reports/agentflow-absorption/
?? governance/review-reports/code-batch14/
?? "governance/review-reports/\351\200\262\345\272\246\345\276\236\346\217\220\344\272\244\346\216\250\345\260\216-v2/"
?? "governance/review-reports/\351\200\262\345\272\246\345\276\236\346\217\220\344\272\244\346\216\250\345\260\216/"

exec
/bin/zsh -lc "python3 -c 'import ast,pathlib; p=pathlib.Path(\"scripts/test_lumos.py\"); m=ast.parse(p.read_text()); ns=sorted(n.name for n in m.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith(\"t_\") and \"t_impact\" in n.name); print(len(ns)); print(\"\\n\".join(ns))'" in /Users/enzo/harness/lumos-toolchain
 succeeded in 684ms:
42
t_impact_about_giant_file
t_impact_about_hit
t_impact_basename_match
t_impact_bfs_backlink
t_impact_bfs_cycle_and_depth
t_impact_bfs_depth_limit
t_impact_bfs_tuple_fields
t_impact_cli_skeleton
t_impact_config
t_impact_contract
t_impact_contract_risk_axis
t_impact_core_refs_leaf
t_impact_cross_direct_node_dedup
t_impact_depth_config_integration
t_impact_diff
t_impact_direct_rescue
t_impact_end_to_end
t_impact_hard_pin_lane
t_impact_hook_filter_and_rc
t_impact_hook_find_lumos_real
t_impact_hook_incidents_inject
t_impact_hook_inject
t_impact_hook_main_ttl_wiring
t_impact_hook_registration_source
t_impact_hook_shebang_and_ttl_mark
t_impact_hook_stack_questions
t_impact_hook_ttl
t_impact_hook_v11_delta_and_format
t_impact_incidents_indirect_dedup
t_impact_incidents_main_only
t_impact_incidents_regression
t_impact_incidents_section
t_impact_incidents_smoke
t_impact_json_schema_and_sort
t_impact_multisource_bfs_min_hop
t_impact_node_mode
t_impact_query_gate_e2e
t_impact_query_junk_unit
t_impact_ranked
t_impact_reverse_lookup
t_impact_via_body_wikilink_fallback
t_impact_via_both_directions

exec
/bin/zsh -lc "rg -n '價值|本地證據|接手|最小解' governance/review-reports/進度從提交推導-v2/r1-snapshot.md docs/lumos-toolchain-knowledge/Projects/執行DAG_調研.md | head -80; nl -ba scripts/test_lumos.py | sed -n '24821,24833p;24909,24917p;24931,24956p;25001,25028p'" in /Users/enzo/harness/lumos-toolchain
 succeeded in 0ms:
docs/lumos-toolchain-knowledge/Projects/執行DAG_調研.md:12:  KEY:★「缺執行記憶」是事實錯誤★——現有三套:實作計畫的 T1..Tn 任務拆解(含「包①→②→③嚴格順序」)、status 欄+`query --active`、自主迴圈 `governance/backlog.jsonl`(185 筆,價值分/衰減/熔斷/單一在飛)
docs/lumos-toolchain-knowledge/Projects/執行DAG_調研.md:34:    why_chosen: 本 repo 零依賴家規(python3 stdlib);三者要解的問題(把待辦從對話搬到可查的地方)這裡已有三套機制在做,借的價值在「依賴是第一等公民」這個形狀,不在它們的儲存層。代價:失去它們的生態(看板 UI、MCP server),自己做要自己維護
docs/lumos-toolchain-knowledge/Projects/執行DAG_調研.md:50:PRIOR-ART:①最小解在既有機制層——「唯一下一動作」的神諭已經有了(`lumos loop next`,只讀帳本結構不讀散文),只差一個「列出現在開著的迴圈」的入口;結構化逐條進度清單也已有自家前例(見下「兩個可抄的前例」);原子認領+租約原語同樣現成(`dispatch-lens --arm/--claim`,10 分 TTL)。②世界解過——五條路線見下,但★沒有任何一條給出對照組數據★,「任務 DAG 對 coding agent 有用」目前是共識不是證據。③不採用新依賴(零依賴家規):beads 需要一個可版控的 SQL 資料庫,Task Master/Backlog.md 是 npm 生態,三者皆出局為「可借形狀、不借實作」。
docs/lumos-toolchain-knowledge/Projects/執行DAG_調研.md:70:  3. **自主迴圈的待辦帳**(`governance/backlog.jsonl`,185 筆)——有價值分、每日衰減、已涵蓋永久排除、熔斷、「同時只准一件在飛」。
docs/lumos-toolchain-knowledge/Projects/執行DAG_調研.md:128:| ★資料工程三十年教訓(本案最有價值的一條)★ | **Airflow(任務中心) vs Dagster(資產中心)** | Dagster:宣告你要的資產與它該多新鮮,**讓系統自己算現在該跑什麼** | 核心主張=**任務是錯的抽象**。排程模型從「告訴系統何時跑」倒過來變成「宣告期望狀態」。★「該做什麼」不是存起來的,是算出來的★ |
governance/review-reports/進度從提交推導-v2/r1-snapshot.md:45:    why_chosen: ★f2 打的是任務級,Enzo 裁的是功能級,三條反對在功能級各自失效★:共用測試在功能級就是同一個功能的測試、既有測試已綠對新功能不成立、只寫跑全套在功能級正是「相依無回歸」那一半的定義。所以不是繞過外家,是換到 f2 打不到的粒度。代價:①功能級是二元的,答不出「做到第幾步」,接手需要的解析度要靠任務級測試名另外給(且不得用來宣告完成)②判準的品質等於測試的品質,弱測試=假綠,靠既有翻紅釘紀律頂著③沒有測試可掛的工作型別完全不在射程內
governance/review-reports/進度從提交推導-v2/r1-snapshot.md:87:PRIOR-ART(★v2 重寫;原稿整段在替已死的 trailer 背書,前掃 ③ 抓到是重寫殘留★):①**最小解在既有機制層**——v2 不新增任何資料格式:任務的名字就是它**已經宣告在計劃裡的測試函式名**,跑法用既有的測試子集入口(`-k <關鍵字>`,前掃實跑驗過可用)。②本家可抄的樣板=`loop verify-progress` 的 help 逐字:「不看散文,只從帳本結構欄位看審到哪了(防被報告措辭帶風向)。」③世界解:GitHub `Closes #N` 綁 forge;beads / Task Master 已於 [[Projects/執行DAG_調研]] d1 裁「可借形狀、不借實作」。④不採用新依賴:只用 python3 stdlib 與既有測試入口。★⑤ v1 的 git trailer 路線已在 r1 被打死(四種靜默失敗),d1/d2/d5/d6 四條決策全部翻案;本節不再替它背書。★
governance/review-reports/進度從提交推導-v2/r1-snapshot.md:105:**消費者**:①接手的 session(現在只能讀散文猜)②Enzo 本人(問「做到哪」要人回答)③無人自跑的迴圈(未來)。
 24821	    import argparse as _ap
 24822	    _p = _ap.ArgumentParser(
 24823	        prog="test_lumos.py",
 24824	        description="lumos 的測試執行器。不帶參數=跑全套(約 8 分鐘);"
 24825	                    "要跑子集就給關鍵字,它會比對測試函式名。")
 24826	    _p.add_argument("keyword_pos", nargs="?", default=None, metavar="關鍵字",
 24827	                    help="跟 -k 一樣(直接打名字比較順手)")
 24828	    _p.add_argument("-k", dest="keyword", default=None, help="只跑名稱含此字串的測試")
 24829	    _p.add_argument("--list", action="store_true", help="只列出測試名稱,不跑")
 24830	    _p.add_argument("--keep-tmp", action="store_true",
 24831	                    help="跑完不要刪這一輪的暫存根目錄(要進去翻現場時用)")
 24832	    _p.add_argument("-x", "--exitfirst", action="store_true",
 24833	                    help="第一支紅就停(不用等剩下的跑完才看到)")
 24909	        if _args.keyword:
 24910	            tests = [t for t in tests if _args.keyword in t.__name__]
 24911	            if not tests:
 24912	                # 假綠洞修補:-k 選中 0 案例 ≠ 全綠——「跑了個寂寞」必須紅,
 24913	                # 否則消費 rc 的一方(hook/CI 等機制)會把「沒驗」當「驗過」。
 24914	                print(f"✗ -k '{_args.keyword}' 選中 0 個測試(t_ 名單無此子字串)——視為失敗", file=sys.stderr)
 24915	                return 1
 24916	        print(f"lumos 測試({len(tests)} 案例)")
 24917	        global FAIL, SKIP
 24931	                run_with_timeout(t, TIMEOUT_OVERRIDE.get(t.__name__, TEST_TIMEOUT_SEC))
 24932	                SLOWEST.append((_time_slow.time() - _t_start, t.__name__))
 24933	                # ★跑完卻一條斷言都沒有=沒驗過,判紅★(2026-09-06 全 repo 審視 #13)
 24934	                # 跟「-k 選中 0 支判紅」同一個理由:綠燈必須代表「驗過而且過了」,不能代表
 24935	                # 「什麼都沒發生」。原本有十處寫成 check(…, True) 當跳過用,那是把「沒驗」
 24936	                # 記成 PASS;已全部改走 _SrcOnly 跳過通道,這條是防它再長回來的機械守衛。
 24937	                if FAIL == _fail_before and PASS == _pass_before:
 24938	                    FAIL += 1
 24939	                    print(f"  ✗ {t.__name__}: 跑完了但一條斷言都沒有(沒驗過≠通過;"
 24940	                          f"真的不該在這台跑就 raise _SrcOnly 走跳過通道)")
 24941	                elif FAIL > _fail_before:
 24942	                    # 殺傷力驗證歸因用(2026-08-22 首跑判「弱證據」):失敗要跟測試名同一行,
 24943	                    # lumos guard kill 的 _kill_attribute 才能把紅燈歸到綁定測試頭上。
 24944	                    print(f"  ✗ FAILED {t.__name__}({FAIL - _fail_before} 條斷言)")
 24945	            except _SrcOnly as e:
 24946	                SKIP += 1
 24947	                SKIPPED_NAMES.append(t.__name__)   # r1:只記總數的話,「換了一支跳過」量不到
 24948	                print(f"  - skip {t.__name__}: {e}")
 24949	            except TestTimeout as e:
 24950	                # ★判紅不判 skip★:沒跑完 = 沒驗過。名字印出來,才知道要去修哪一支。
 24951	                FAIL += 1
 24952	                print(f"  ✗ TIMEOUT {t.__name__}: {e}"
 24953	                      f"(調整:LUMOS_TEST_TIMEOUT=<秒>,0=不設限)")
 24954	            except Exception as e:
 24955	                FAIL += 1
 24956	                print(f"  ✗ {t.__name__} EXCEPTION: {e}")
 25001	        tail = f", {SKIP} skipped(來源 repo 專用)" if SKIP else ""
 25002	        print(f"\n{'─'*40}\n{PASS} passed, {FAIL} failed{tail}")
 25003	        # ★跳過的支數要有基準線★(2026-09-06 全 repo 審視 #11 現場學到的):
 25004	        # 我把一個環境變數設錯,害一支測試找不到來源就靜默跳過——全套照樣「零紅」,
 25005	        # 是我自己去比 skip 從 0 變 1 才發現。**跑得到變跑不到=覆蓋悄悄少掉,而它不會紅。**
 25006	        # 所以在這裡對基準線比一次:超過就出聲(只在跑全套時比,-k 子集本來就會跳很多)。
 25007	        # ★超過基準線要判紅,不是印個提醒就算★(r1 外家席抓到):只印不紅的話,
 25008	        # 覆蓋退化照樣以成功狀態碼離開,CI 與推送閘收到的還是 rc0——那就等於沒有這道基準線。
 25009	        # 只在「基準線有意義」的環境判:來源 repo(消費端本來就會跳過一批來源專用的)
 25010	        # 且非 Windows(Windows 分支的跳過是合法的)。其餘環境只印一行觀測,不判紅。
 25011	        if not _args.keyword and SKIP > EXPECTED_SKIP_MAX:
 25012	            _baseline_applies = (Path(GRAPHCTL).resolve().parent.parent / "skills" / "lumos-project-notes").is_dir() \
 25013	                and sys.platform != "win32"
 25014	            print(f"  這次跳過 {SKIP} 支,比預期上限 {EXPECTED_SKIP_MAX} 支多。"
 25015	                  f"跳過不會出現在紅字裡,但它代表那些測試這輪沒驗到。")
 25016	            # r1 折入:只印總數的話,「本來跳 A、現在改跳 B」這種換人的漂移量不到
 25017	            # ——兩邊相減淨額一樣。所以把名字列出來,人一眼看得出換的是誰。
 25018	            print(f"  跳過的是:{', '.join(SKIPPED_NAMES)}")
 25019	            if _baseline_applies:
 25020	                FAIL += 1
 25021	                print(f"  ✗ 判紅:這台是來源 repo 又不是 Windows,所有跳過通道的條件本來都不成立"
 25022	                      f"——多出來的跳過幾乎一定是現場被弄壞了(例如某個環境變數設錯,害測試找不到它要的東西)。")
 25023	                print(f"  確認過而且合理的話,把 EXPECTED_SKIP_MAX 調成 {SKIP} 並在旁邊寫一句為什麼,"
 25024	                      f"或設 LUMOSEXPECTED_SKIP_MAX=<數字> 暫時放行。")
 25025	            else:
 25026	                print(f"  (這台不是來源 repo 或是 Windows,跳過本來就會多,所以只記不判紅)")
 25027	        return 1 if FAIL else 0
 25028	    finally:

codex
severity: blocker

## F1　v2 沒解「做到哪」，只把輸出降級成當下測試觀測

引句:「不說「完成」,說「它宣告的證據現在是什麼狀態」。推論交給讀的人。」

severity: blocker  
blocking: 是  
原需求的消費者要回答「做到哪」，v2 卻明令不作這個判定；讀者仍須人工把測試狀態推論成進度，原本的漂移責任只是從作者移給讀者。這不是解掉六個 blocker 的共同根因，而是撤回原交付目標。

## F2　d3 被實質放棄，v2 沒有實現 Enzo 裁定

引句:「本案只碰得到「這個功能的測試綠不綠」,答不出「相依功能有沒有回歸」」

severity: blocker  
blocking: 是  
d3 明定完成判準為「功能級測試套綠＋相依功能無回歸」，v2 刪掉後半、又禁止宣告完成，因此沒有實現 d3，只交付較弱的任務測試查詢。把另一半留給推送閘與 CI 不構成同一查詢的功能級判準。

## F3　「讀工作樹」只解可見性，未解未提交態的歸屬與並行污染

引句:「未提交態解決——讀工作樹不讀提交歷史,session 做到一半還沒 commit 照樣看得見」

severity: blocker  
blocking: 是  
共用工作樹沒有 session 維度，當場綠或紅可能來自另一個 session，查詢既不能說是哪個任務造成，也不能產生一致時間點的快照；目前事故帳已記錄紅燈誤歸因與瞬時壞檔。file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:35`；file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:60`；file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:104`

## F4　提交夾帶沒有消失，只是不再看得見

引句:「提交夾帶不影響(不依賴提交歸屬)」

severity: major  
blocking: 是  
v2 不再錯讀 trailer 歸屬，但共用工作樹中的夾帶改動仍能令任務測試轉綠，查詢無法分辨成果由誰或哪個任務產生；它消除的是歸屬欄位，不是歸屬問題。既有事故已證實同一棵樹的內容與提交訊息能完全對不上。file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:40`

## F5　`-k` 實測證實可以借到整族測試的綠

引句:「跑法用既有的測試子集入口(`-k <關鍵字>`),不跑全套。」

severity: blocker  
blocking: 是  
當場以 `t_impact` 查選擇集合，原始碼中沒有名為 `t_impact` 的測試，卻因子字串規則命中 42 支 `t_impact_*`；若它們全綠，設計會把不存在的宣告報成「存在且綠」。執行器明寫子字串篩選而非精確匹配。file: `scripts/test_lumos.py:24828`；file: `scripts/test_lumos.py:24909`

## F6　三態會把「沒驗到」偽裝成綠或紅

引句:「回報三種狀態之一——「不存在 / 存在但紅 / 存在且綠」」

severity: blocker  
blocking: 是  
skip 在 `-k` 子集中只增加 `SKIP`、不增加 `FAIL`，最後仍可 rc0，因此會被三態模型誤報「存在且綠」；超時與環境例外則都增加 `FAIL`，會和斷言失敗一起被壓成「存在但紅」。file: `scripts/test_lumos.py:24945`；file: `scripts/test_lumos.py:24949`；file: `scripts/test_lumos.py:25011`；file: `scripts/test_lumos.py:25027`

## F7　「不存在」同樣混合兩種相反事實

引句:「測試名寫錯的輸出是「不存在」——看得見」

severity: major  
blocking: 是  
名字打錯與測試尚未實作都會得到同一輸出，但前者是計劃引用損壞，後者是正常的未提交進度；只把它顯示出來沒有使狀態變真。三態至少必須分成「未宣告／精確名稱不存在／skip／環境不可執行／超時／斷言紅／綠」。

## F8　立案證明了症狀，仍未證明這個產品形狀有消費價值

引句:「消費者:①接手的 session(現在只能讀散文猜)②Enzo 本人(問「做到哪」要人回答)③無人自跑的迴圈(未來)」

severity: major  
blocking: 是  
陳舊勾選框證明手寫進度會漂，但沒有實例證明接手者會用「逐項現跑測試」，且關鍵字一寬便需 23.4 秒、完整計劃還要逐名重複啟動。第三個消費者仍是未來式，前兩個要的是「做到哪」，而本案明說不回答它，因此尚未通過「症狀—消費者—最小層」的立案線。

## 第五條路

有：把實作改成結構化任務帳的原子轉移——由執行入口取得 task id、套用該任務的 changeset，成功落檔時在同一原子動作追加 receipt；進度從 receipt 帳本折疊，不用測試、trailer 或 CI。這條沿用審查迴圈「成果動作本身就是記錄」的形狀，但必須限制所有受管任務都經該入口，否則又退化成另一份靠自律維護的狀態檔。
hook: Stop
hook: Stop Completed
tokens used
96,632
severity: blocker

## F1　v2 沒解「做到哪」，只把輸出降級成當下測試觀測

引句:「不說「完成」,說「它宣告的證據現在是什麼狀態」。推論交給讀的人。」

severity: blocker  
blocking: 是  
原需求的消費者要回答「做到哪」，v2 卻明令不作這個判定；讀者仍須人工把測試狀態推論成進度，原本的漂移責任只是從作者移給讀者。這不是解掉六個 blocker 的共同根因，而是撤回原交付目標。

## F2　d3 被實質放棄，v2 沒有實現 Enzo 裁定

引句:「本案只碰得到「這個功能的測試綠不綠」,答不出「相依功能有沒有回歸」」

severity: blocker  
blocking: 是  
d3 明定完成判準為「功能級測試套綠＋相依功能無回歸」，v2 刪掉後半、又禁止宣告完成，因此沒有實現 d3，只交付較弱的任務測試查詢。把另一半留給推送閘與 CI 不構成同一查詢的功能級判準。

## F3　「讀工作樹」只解可見性，未解未提交態的歸屬與並行污染

引句:「未提交態解決——讀工作樹不讀提交歷史,session 做到一半還沒 commit 照樣看得見」

severity: blocker  
blocking: 是  
共用工作樹沒有 session 維度，當場綠或紅可能來自另一個 session，查詢既不能說是哪個任務造成，也不能產生一致時間點的快照；目前事故帳已記錄紅燈誤歸因與瞬時壞檔。file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:35`；file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:60`；file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:104`

## F4　提交夾帶沒有消失，只是不再看得見

引句:「提交夾帶不影響(不依賴提交歸屬)」

severity: major  
blocking: 是  
v2 不再錯讀 trailer 歸屬，但共用工作樹中的夾帶改動仍能令任務測試轉綠，查詢無法分辨成果由誰或哪個任務產生；它消除的是歸屬欄位，不是歸屬問題。既有事故已證實同一棵樹的內容與提交訊息能完全對不上。file: `docs/lumos-toolchain-knowledge/Issues/同工作區多session並行改動.md:40`

## F5　`-k` 實測證實可以借到整族測試的綠

引句:「跑法用既有的測試子集入口(`-k <關鍵字>`),不跑全套。」

severity: blocker  
blocking: 是  
當場以 `t_impact` 查選擇集合，原始碼中沒有名為 `t_impact` 的測試，卻因子字串規則命中 42 支 `t_impact_*`；若它們全綠，設計會把不存在的宣告報成「存在且綠」。執行器明寫子字串篩選而非精確匹配。file: `scripts/test_lumos.py:24828`；file: `scripts/test_lumos.py:24909`

## F6　三態會把「沒驗到」偽裝成綠或紅

引句:「回報三種狀態之一——「不存在 / 存在但紅 / 存在且綠」」

severity: blocker  
blocking: 是  
skip 在 `-k` 子集中只增加 `SKIP`、不增加 `FAIL`，最後仍可 rc0，因此會被三態模型誤報「存在且綠」；超時與環境例外則都增加 `FAIL`，會和斷言失敗一起被壓成「存在但紅」。file: `scripts/test_lumos.py:24945`；file: `scripts/test_lumos.py:24949`；file: `scripts/test_lumos.py:25011`；file: `scripts/test_lumos.py:25027`

## F7　「不存在」同樣混合兩種相反事實

引句:「測試名寫錯的輸出是「不存在」——看得見」

severity: major  
blocking: 是  
名字打錯與測試尚未實作都會得到同一輸出，但前者是計劃引用損壞，後者是正常的未提交進度；只把它顯示出來沒有使狀態變真。三態至少必須分成「未宣告／精確名稱不存在／skip／環境不可執行／超時／斷言紅／綠」。

## F8　立案證明了症狀，仍未證明這個產品形狀有消費價值

引句:「消費者:①接手的 session(現在只能讀散文猜)②Enzo 本人(問「做到哪」要人回答)③無人自跑的迴圈(未來)」

severity: major  
blocking: 是  
陳舊勾選框證明手寫進度會漂，但沒有實例證明接手者會用「逐項現跑測試」，且關鍵字一寬便需 23.4 秒、完整計劃還要逐名重複啟動。第三個消費者仍是未來式，前兩個要的是「做到哪」，而本案明說不回答它，因此尚未通過「症狀—消費者—最小層」的立案線。

## 第五條路

有：把實作改成結構化任務帳的原子轉移——由執行入口取得 task id、套用該任務的 changeset，成功落檔時在同一原子動作追加 receipt；進度從 receipt 帳本折疊，不用測試、trailer 或 CI。這條沿用審查迴圈「成果動作本身就是記錄」的形狀，但必須限制所有受管任務都經該入口，否則又退化成另一份靠自律維護的狀態檔。
