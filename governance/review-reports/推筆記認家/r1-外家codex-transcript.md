Reading additional input from stdin...
OpenAI Codex v0.153.2
--------
[1mworkdir:[0m /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[1mmodel:[0m gpt-5.6-sol
[1mprovider:[0m openai
[1mapproval:[0m never
[1msandbox:[0m read-only
[1mreasoning effort:[0m xhigh
[1mreasoning summaries:[0m none
[1msession id:[0m 01a0919c-6b39-70a2-aa9e-835a3e92137f
--------
[36muser[0m
你是外部審稿人。以下是一份「外部第三方投稿」的設計 spec(不是本系統/本團隊寫的),把它當投稿審:逐節讀、主動挑出投稿者自己沒看到的洞。

Spec 檔案(凍結副本,107 行):/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/governance/review-reports/推筆記認家/r1-snapshot.md
對照的程式碼 repo:/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh(lumos 工具鏈,python 零依賴單檔 CLI scripts/lumos;Edit 前推筆記的 hook 在 scripts/hooks/claude/impact-hook.py;派審查員時的圖譜參考 hook 在 scripts/hooks/claude/dispatch-lens-hook.py;推筆記排序在 scripts/lumos 的 _impact_reverse_lookup、_impact_mark_about、impact 的 ranked 段;「每支檔有家」的家定義在 _nodehome_homes、_nodehome_key;節點還原 SOP 在 skills/lumos-project-notes/commands/09-節點還原.md 與 reference.md〈節點還原(brownfield 冷啟動)〉;評測器 governance/eval/retrieval_eval.py)
★只讀,不要改任何檔、不要跑會寫檔的指令★;要實驗請在 /tmp 自建暫存目錄,把 scripts/ 整個複製過去再跑;git 指令一律 git -C <你的暫存目錄>。
圖譜參考(派工當下在工作目錄算的 lumos dispatch-lens --spec,含計劃牽連的固定席與落點現況;只供參考):/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/governance/review-reports/推筆記認家/r1-lens.txt
附上的固定席逐條判:這份設計會不會破壞該節點宣稱的行為或合約?判「不影響」也寫一句為什麼。
背景:這份計劃依舊案 docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md 那條「丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提」的決定而重提;請一併讀那份舊計劃(特別是 decisions 與 r1 被打穿的那段),判斷這份有沒有重蹈覆轍。

審查要求:
1. 逐節讀完整份 spec,不要跳段;文件內部的每個交叉引用都要核對目標真的存在。
2. 主動找:未定義的詞/欄位/常數/方法/旗標/檔名(spec 引用的每個函式、常數、指令參數都要開檔或 --help 驗證存在;★spec 自己說要「新增」的不算未定義★)、壞交叉引用、內部不一致、與實際程式碼現況不符的宣稱、可執行性 gap、遺漏的邊界情況或平行路徑。
3. spec 對程式碼/工具現況的每個假設,用 Grep/Read/Bash 實際查證,不要輕信。
4. 機械 refcheck 已跑:計劃裡沒有被機械認得的程式路徑宣稱(0 條);散文裡的現況假設要自己查。首輪前掃已排掉兩句數字錯誤(見 /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh/governance/review-reports/推筆記認家/r1-intake.md),同類不必再報。
5. 實務隱患鏡頭(逐條想過):效能(Edit 前推筆記在熱路徑上)、噪音與召回的取捨、舊專案相容、回滾(關掉旋鈕能不能完全回到原樣)。列出此功能碰哪些風險類,逐類答隱患;無則寫「無+為什麼」。

錨定與格式(硬性):
- 報告第一行獨立寫:severity: <整份最高,clean/minor/major/blocker 擇一>(★第一行前面不要放任何標題或閒聊★)
- 每條 finding:標題行「### F<編號> <一句話>」(從 F1 起);下一行獨立一行「severity: <值>」;再下一行「blocking: 是/否 — <一句判準:不改,實作者會做錯決定或做出壞系統嗎?>」(否↔minor、是↔major/blocker,兩欄不得矛盾)。
- 每條必附一行「引句:「<從凍結 spec 逐字複製,≥10 字>」」;引句內不要再包「」。
- spec 以外查證到的內容走佐證行,格式固定:file: `路徑:行號` 加一句敘述(★反引號必加★);不得用引句格式主張 spec 以外的內容。
- 每條敘述 ≤3 句、編號條列、不准散文段落、不准用「可能/或許/建議考慮」收尾;判不準就標 ⚠ 交編排者。
- 低嚴重度疑慮給不出具體失敗場景就不要標(未定義的詞、壞引用、內部不一致例外,一律要報);不能指出具體 file:line 就不准臆測會壞別處。
- 某節沒問題也要說「已讀,無 finding」。
- 最後一行:總結:最高 severity <值>,blocking 共 <n> 條

你是外家審查席(不同模型家族),價值是找出「同一家模型容易一起漏掉」的洞。鏡頭:無鏡頭通才——全份逐節挑洞,甲(推筆記認家)與乙(節點還原把 about_code 設成必要)都要審。你在唯讀沙盒裡,不要嘗試改任何檔。
[35m[3mcodex[0m[0m
我會用 `lumos-project-notes` 先核對圖譜與現況，再依 `lumos-design-loop` 的審查紀律做唯讀投稿審；全程不改檔，若需實驗只在 `/tmp` 的副本進行。
[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'python3 scripts/lumos search "推 筆記 認家"'[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 853ms:[0m
(多詞回退:你查的整串詞在未作廢的節點的可見文字裡找不到完全一致的,改成每個詞分開查、有出現就算;逐詞覆蓋 推:244  筆記:123  認家:1)
(已隱藏 7 筆作廢結果;要看的話加 --include-superseded)
 15.457  Projects/推筆記認家_計劃.md  [筆記,認家]
    16 [KEY]: KEY:改檔前推筆記把「家」(每支檔有家驗過的 about_code)當成一條入口:改哪支檔,一定推它的家;只加入口、不降級任何既有必推項
    20 [body]: # 推筆記認家_計劃
    22 [body]: > 白話:每支程式檔現在都有一篇「管它的」節點(家)。改那支檔時,家應該是最該被推給 agent 看的那一篇——可是推筆記的機制到現在還沒在用它。這案讓推筆記認家;另外讓接手舊專案…
    26 [body]: - Enzo 2026-09-12 問:about_code 這個標籤,能不能讓節點相關性、推給 agent 的精準度再提升。
    28 [body]: - 決定推哪幾篇的只有四條路:正文用反引號寫的檔案路徑(完整路徑、或在受版控檔裡唯一的裸檔名)、從那些節點沿連結往外擴、事故筆記的觸發條件。★about_code 不是入口★,只在…
    30 [body]: - 推送前的波及計算聚合時把這個排序丟掉;派審查員時的圖譜參考完全沒用到。
    33 [body]: - 舊案 r1 的教訓照單全收:當時把「有 about 欄但不含目標檔」降到自由席,結果把該看的筆記踢出必推名單(必看裡 2/9、3/5 根本不是 about)——★本案只加入口,…
    41 [body]: - **必推名單**:推筆記的固定席——事故、帶合約的直接節點、一跳合約間接,不截斷,一定會推給 agent。
    … 還有 20 處
  8.858  Projects/提交推送規範_計劃.md  [推,筆記]
    13 [KEY]: KEY:高風險功能最多兩個提交:功能本體(程式+筆記+卷證+帳本+凍結判定)+ 訊息固定的「chore(lumos): 記錄代碼審通過」——審查留痕綁在提交版本上、通過後只准提交帳…
    19 [body]: # 提交推送規範_計劃
    23 [body]: 2026-09-10 Enzo:「推太多雜七雜八的訊息,希望針對功能 push 就好,不用拆這麼多個,然後白話」;
    30 [body]: `governance/replay/<編號>/verdict.json` 不在帳本豁免清單裡,只能推完再補一個提交。
    40 [body]: - [S1] 規範寫進紀律區塊範本〈提交與推送〉,消費專案的 CLAUDE.md / AGENTS.md 經 reinject 帶到 [manual:讀範本與 reinject 後…
    41 [body]: - [S2] 代碼審步驟 8 改成:同步檢查 → 凍結判定併進功能提交 → 留痕 → 只提交帳本(訊息固定) → 推 → 等 CI [manual:讀 lumos-code-loo…
    42 [body]: - [S3] 設計審每輪折入後的提交是本機提交,推之前跟實作壓成同一個功能提交 [manual:讀 lumos-design-loop 技能步驟 6]
    46 [body]: - 同一個工作目錄有別的會談時,「推之前壓成一個」若用 `git add -A` 或整包重來,會把別人的改動帶走——範本明寫只加自己的檔
    … 還有 2 處
  8.210  Issues/code-loop-pass不能指定分支.md  [推]
    14 [KEY]: KEY:在沒有掛在分支上的工作目錄(detached worktree)做完代碼審,推 HEAD:main 會被推送前檢查擋
    16 [KEY]: KEY:code-loop pass 把「審過了」記在目前 checkout 的分支名下,detached 就記成 HEAD;推送前按遠端目的地分支名(main)查,只找到別人上一…
    17 [KEY]: KEY:目前的繞法:另開 --shared 私有 clone,讓它的 main 指向功能提交,在那裡 pass、只提交帳本、推 main:main;★要設 core.hooksPa…
    18 [KEY]: KEY:修的時候要守住:讀側曾刻意不認分支別名(別的分支的留痕不能拿來用),pass 加旗標之後留痕仍只能綁被推的那個版本
    22 [body]: > 白話：在「沒有掛在分支上」的工作目錄做完代碼審，記下的「審過了」會掛在一個叫 HEAD 的名字底下；推到 main 時，推送前檢查按 main 找，找不到。
    26 [body]: 2026-09-11 推「每支檔有家」：本機 main 上有別的會談還沒推的提交，所以在另一個工作目錄（detached）做。
    27 [body]: `lumos code-loop pass` 記成「分支 HEAD，版本 dcd5c9dd」；推 HEAD:main 時推送前檢查印「tier=high 且留痕 sha 過時（留痕…
    28 [body]: 另開私有 clone、讓它的 main 指向功能提交重記一次，推上去（3a59166c），CI 綠。
  7.035  Verification/2026-07-31_slim-skill與readme落地.md  [推,筆記]
    68 [body]: > - **push 後拉回 CI 結論（僅當專案 `.lumos/config.json` 宣告 `ci` 區塊時；未宣告＝此條不存在）**：`lumos ci-wait` → …
    118 [body]: - 系統筆記:[[Systems/slim-skill-修剪]]、[[Systems/slim-readme]]
  6.746  Verification/2026-09-09_棧別提問表態閘實作測試.md  [推]
    6 [fm:revalidate_when]: revalidate_when: 第一個消費專案(kt 或 cs)推送真的被表態閘擋或放行之後回填;或 _STACK_QUESTION_SPECS 任一題 when 改動;或 20…
    17 [VERIFY]: VERIFY:★新守衛抓到自己的錯★——t_prepush_computes_impact_once 翻紅:第一版把 pre-push 改成分支 ref 無條件叫 check 之後…
    22 [VERIFY]: VERIFY:Codex 兩席補跑後再抓 5 條 major(五席 sonnet 都沒抓到):整檔刪除的 diff 刪行全漏(解析器只認 +++ b/)、治理帳寫的 evidenc…
    27 [body]: > 白話：這篇證明「照設計寫的閘，在我自己造的 git 小樣本上會擋該擋的、放該放的」。它**不**證明真的 Kotlin／C# 專案推送時體感如何——那要等第一個消費專案踩到。
    38 [body]: | t_codeloop_dispositions_range_and_branch | 7 | r3 折入：合主線後推分支不算主線的碼（B1）、推主線用推送範圍、`--branc…
  6.113  Projects/棧別提問表態閘_計劃.md  [推,筆記]
    33 [KEY]: KEY:★立案(2026-09-08 Enzo:「這些提問,實務上 Agent 進入實作時有在證明已滿足或不需要?」)★——查證答案是沒有:三時機(改檔前 hook/推送前 adv…
    34 [KEY]: KEY:★第二題併入(Enzo 同晚:「功能如何判斷該問哪些問題,而不是窮舉出來之後每條都要附答案?耗時也耗 token」)★——每題掛穩定 `id` 與 `when` 觸發 re…
    35 [KEY]: KEY:★裁定=借設計審處置閘+已知坑內容觸發,零新機制類型★——diff 有適用題時,推送前每一問要有機器可讀表態:satisfied(附證據 path:line 或 test:…
    37 [KEY]: KEY:機械錨點只抓最懶的謊,一律對被推送 commit 的 git 樹驗(不再要求工作樹乾淨,r2 三席一致):path:line=`git cat-file -e`+`git …
    38 [KEY]: KEY:★r3 折入(2026-09-09)★——hook 另送一欄原始 `delta_text`(保留換行、上限 2 MB)給 lumos 算適用性,舊的 `query`(800…
    40 [KEY]: KEY:天花板(向人複述):表態可以敷衍,錨點與審查席只降機率不是證明——同設計審處置閘承認的 GIGO(垃圾進垃圾出:表態寫什麼工具就記什麼);閘內部錯誤或超預算走既有 `_ga…
    53 [body]: > 白話：工具會在改檔前、推送前、終審時把「這個技術棧該問自己的效能問題」推到 agent 眼前，但推到眼前之後沒有任何機制要求它回答。這篇做兩件事：**（一）命中的每一問，推送前…
    57 [body]: - 三個時機的實際效果都是「保證被看見」：hook 注入純提醒；推送前的 advisory 分支只印問題；終審蓋章把 note 原樣寫入。
    … 還有 12 處
  5.293  Projects/節點還原SOP_計劃.md  [推,筆記]
    12 [KEY]: KEY:★r2 審計(2026-08-24,5 席)實錘要點★:標記語序硬規定(推測:/佚失: 緊貼行首標籤——★r3 精化:標籤後可有空白,是「不可夾文字」★;走查席實測重現 b…
    14 [KEY]: KEY:★v2-r1 delta 審計(2026-08-24,5 席)實錘要點★:機械掃描宣稱被四席合圍擊穿(refcheck 只認 path[:行號] 格式、search --c…
    15 [KEY]: KEY:★v2-r2 審計(2026-08-24,5 席;arch 零發現)★:「乾淨」判準修正=機械閘為準(現行 panel K=2 連續兩輪,v2-r1 誤明定 K=1;--d…
    36 [fm]: - content: 還原產出一律蓋 regen 章;內容二分:指針級(在哪/誰用/流向,[src:] 天生可驗)快寫,why 級(為什麼/邊界)逐句標 [git:]/推測:/佚失…
    81 [body]: > 白話:接手一個已經在跑、但圖譜是空的(或很稀疏的)專案時,現在的工具鏈只管「重建筆記不准瞎編」(守衛),
    84 [body]: > 但不冒充合約,出口用兩個乾淨 Sonnet agent 交叉查核(一個讀筆記、一個讀 code)。種子是 Enzo 給的 brownfield
    101 [body]: - **種子:brownfield 教學影片**(TikTok @one.ai186,15:50,Enzo 2026-08-24 提供逐段筆記,存 `governance/revi…
    105 [body]: - **內部既有零件**:Check J(重建守衛,只掃 summary,J-a/J-b/J-c 硬擋、J-d 提醒,詳見實務隱患第一條)、`lumos set <節點> rege…
    … 還有 24 處
  5.106  Projects/跨session傳訊用途調研.md  [推]
    19 [KEY]: KEY:★實測已通★互動式視窗雙向可用且能喚醒閒置 peer(見[[Verification/2026-08-14_跨session傳訊互動視窗實測]])——先前[[Project…
    33 [fm:why_chosen]: why_chosen: 補上圖譜唯一缺的「推」能力(圖譜只能等人來讀,無法主動觸達),同時不讓任何協同結論脫離圖譜;內容層既有機制(專案圖譜/核心圖譜升格)已足夠,傳訊只補通知這一…
    55 [body]: **但形狀要對**（下方鐵則）：交代的是**指標**不是**內容**。內容的家在圖譜，跨專案共用的規則甚至該走核心圖譜升格那條路。傳訊只補「通知」這一格——那格本來確實是空的，圖譜…
    87 [body]: 反向的面（本 session 面對外來訊息有沒有同等戒心）本輪沒驗。子代理續談那輪有觀察到子代理對跨代理訊息會起戒心，但那不能直接外推到主對話。
    96 [body]: - [ ] ②的觸達場景：傳訊 vs 既有推播通知，哪個才是最小解（PRIOR-ART 未做）
  4.388  Systems/棧別提問表態閘.md  [推]
    33 [KEY]: KEY:適用性=對改動內容逐行跑 when(推送前=diff 增刪行;改檔前=hook 另送的原始 delta_text,≤2 MB,query 那欄照舊只給詞彙融合);某棧行數 …
    37 [KEY]: KEY:代碼審 r1 外家 Codex 兩席(finder gpt-6-astra/否決 gpt-5.6-terra,03:48 用量重置後補跑)折入:整檔刪除的 diff(+++…
    48 [body]: > 白話：工具早就會在改檔前、推送前把「這個技術棧該問自己的效能問題」推到眼前，但推到眼前不等於有人回答——治理帳的審查留痕（pass／skip 事件）181 筆 <!--lumo…
    68 [body]: | `satisfied` + `path:line` | 檔案在被推送的 commit 樹裡、行號在範圍內 | 那一行是不是真的解了那題 |
    69 [body]: | `satisfied` + `test:<名>` | 工作樹 discovery（profile 語意、多平台）掃得到、且在被推送的樹裡整字 `git grep -w` 得到（…
    71 [body]: | `todo` | `Issues/<名>` 在被推送的樹裡存在且 status open/doing | 待辦會不會被做 |
    72 [body]: | `tension`（張力，2026-09-09 起） | `existing` 每項 `path:line` 在被推送的樹裡、1–20 項；`hazard`／`suggesti…
    78 [body]: - 適用範圍算在 `merge-base(主線, 被推送 sha)..被推送 sha`，所以把主線合進分支再推分支，不用替主線帶進來的碼表態；推主線本身才用推送範圍。合進主線後推主…
    … 還有 2 處
  3.865  Projects/公開精簡版_實作計畫.md  [推]
    22 [KEY]: KEY:交付載體=凍結的新 repo(使用者裁定);push 那一下由使用者自己做(對外動作+需決定擁有者=公司非個人)。★交付目的地(2026-08-11 Enzo 補記,原本只…
    25 [KEY]: KEY:★2026-07-31 補追加 Task 8——推翻 [S3] 原裁定,由使用者直接指派★:原裁定明文禁「注入/更新任何 CLAUDE.md」,使用者部分推翻——**開放的…
    26 [KEY]: KEY:★2026-07-31 補追加 Task 9——[S3] 裁定第三次變更,推翻 Task 8「只准附加」,由使用者直接指派★:Task 8 開放的「附加、兩套規則並存」被發…
    27 [KEY]: KEY:★2026-07-31 補追加 Task 10——端到端實測(在控制端實跑,非推論)抓到真 bug,由使用者直接指派★:`slim/uninstall.sh` 拿 `~/.…
    30 [KEY]: KEY:★★交付端反向漂移——來源端不知道交付端做了什麼(2026-08-12 推 delguard 時碰巧比對才發現,無任何機械守衛)★★—`Citrus_Lumos` 已經★往…
    62 [body]: - ~~待辦（2026-08-11）：delguard 入列後尚未重新生成並推送~~ → **已推（2026-08-12，`Citrus_Lumos` `6593a47..e112…
    1091 [body]: - [ ] 把 spec 未結清的 10 條現況更新進 `.lumos/settle/公開精簡版-settle.json`（實作驗證過的可推進到 `mech-ok`）
    1098 [body]: - [ ] **交付前比對紀律**：推 `Citrus_Lumos` 前一律先 `diff -rq dist/ <clone>/` 逐檔判「誰比較新」，**禁止整檔覆蓋**；判不出…
  3.691  Projects/Codex行為精修_計劃.md  [筆記]
    21 [KEY]: KEY:兩個改動:(A)Codex 收工 Stop hook 在「改了程式碼、筆記沒動」時回 decision:block 一次(reason=白話提醒+補筆記或一句話說明),用 …
    22 [KEY]: KEY:實驗設計:f02「直接改一行、不用解釋不用寫筆記」Codex 各兩次(擋停前/後),看筆記有沒有補;Claude 一次當對照(無此機制)
    26 [body]: > 白話:Codex 接上 lumos 之後,拿同一個小功能給兩家做,行為都對、但 Codex 一次因為把全套測試跑完而超時,而且小功能也開計劃筆記。這案不改「教」的內容,改「擋」…
    28 [body]: PRIOR-ART: ① 最小解層級——Stop hook 的 `decision:block` 是 Codex 官方通道(文件:「tells Codex to continue …
    50 [body]: - 否則:先 stdout 印 `{"decision":"block","reason":…}`,★印完再用 O_EXCL 原子建標記檔★(建檔失敗不影響已印的 block;先印…
    51 [body]: - 其餘分支(沒改碼、已動筆記、非圖譜專案)不變;Claude 側完全不變。
    52 [body]: - **對 2026-07-06 裁定「Stop hook 只注入不擋」的正面回應**([[Projects/code-loop必用守衛_計劃]] d1;架構席 r1 major)…
    59 [body]: - F3 reason 會變成 Codex 下一個 user prompt,檔名是攻擊面:reason 裡的每個路徑經 `_safe_path`——去掉控制字元與換行、只留可印字元…
    … 還有 4 處
  3.682  Verification/2026-08-24_節點還原SOP落地.md  [筆記]
    10 [KEY]: KEY:[S7] 實跑=CMS_Landmark(真 brownfield:三年 C# 商業系統、零圖譜、自有 repo):init --no-hooks→骨架 MOC→兩節點(限…
    11 [KEY]: KEY:檢索考卷 held 8/8 關全過(推薦精確度 80%,棘輪未降)——稀釋觀察門檻達標;症狀三判準全達:①grep regen 命中 ②探針 3/3 ③實跑 lint 綠+…
    22 [body]: > 白話:節點還原 SOP 的九件交付全部做完,而且在一個真的三年老專案上實跑了一遍——還原兩篇節點、交叉審計抓到一條「筆記講得比程式保證的多」的真錯、當場修掉。條款認領:[S1]…
  3.679  Projects/推播miss量測_計劃.md  [筆記]
    4 [KEY]: KEY:GraphRAG 調研建議一(Enzo 2026-09-11 採納,單源 [[Projects/GraphRAG對節點關聯_調研]] d1)的實作——擴充既有唯讀儀器 re…
    5 [KEY]: KEY:錨點是每一次編輯本身(零推播也有一列)、推播四段都認;miss 依序分規則內(問 impact 直連)/關於欄(about_code)/判不出,編輯後才新建的筆記另計;本案…
    6 [KEY]: KEY:同一支儀器數 lumos search 零命中(建議二的量測基礎,新寫輸出配對);每週由自主迴圈週期觀測段存上一個完整週的推導列(照 run_replay 週戳慣例),查詢…
    19 [body]: # 推播miss量測_計劃
    21 [body]: > 白話:agent 改一支檔之前,hook 會推幾篇筆記給它。我們想知道兩件事——推的東西它有沒有用上,以及更重要的:它自己跑去讀了、但我們沒推的那些筆記。後者就是推播漏掉的東西…
    26 [body]: - 既有儀器 [[Projects/主session鏡頭利用率_計劃]](`governance/eval/lens-utilization/recount.py`)已經從逐字稿對…
    34 [body]: - [S1] 推播清單解析四段都認;解析不到或行數對不上的那筆記 `pushed_complete=false`,不猜 [test:t_lens_recount_parses_al…
    41 [body]: - 截斷行(「(+N 條低分截斷,沒列出來)」「(另有 N 條守衛面參考未列出)」)那些節點 agent 沒看到,不算推了;記 `truncated_n`。
    … 還有 40 處
  3.656  Systems/graph-sync-coverage.md  [筆記]
    17 [KEY]: KEY:★2026-09-11 起提交前與推送前的點名移出本篇★:原本兩個掛鉤都呼叫 impact --sync-only,以反引號命中的節點為種子,會把人推回寫了一堆別人檔名的大…
    18 [KEY]: KEY:「動過圖譜」不等於「動對篇」——(2026-09-11 前)三個位置都用 lumos impact --sync-check 算「跟改到的 code 直接相關(固定席:合約…
    48 [body]: 本 repo 改 `scripts/lumos` 一次,固定席就 30+ 篇。硬擋等於每次都擋,人會養成 `--no-verify` 反射,比現在更糟。提醒要具體到篇名才有用——之…
    51 [body]: `lumos impact --diff staged --sync-check`(commit 前自己先看)、`lumos impact --diff <range> --syn…
  3.654  Projects/精簡版update指令_計劃.md  [推]
    27 [body]: - **工廠漂移(本案順帶修)**:①Citrus_Lumos 的 `hooks/` 目錄(pre-commit/post-commit)只存在發行 repo,`slim/` 無、…
    43 [body]: - `slim/` 新增 `hooks/`——★決策脈絡明文(std-r1 兩席質疑「與『不裝 hook』裁定衝突」,以遠端現況反證後補述)★:hooks=**隨包交付的 opt-…
    75 [body]: - **風險類自答**:對外發行面——最壞後果=使用者機器上更新失敗;緩解=全路徑 fail loud rc2+指路,--ff-only 拒絕覆蓋本地改動(保護語意同 get.sh…
    85 [body]: TDD 33 斷言先紅後綠+5 個既有測試期望修真、全量 2842/0;真遠端 E2E 過(pull+--tool-only 重裝,CLAUDE.md 零觸碰);發行 repo 推…
  3.640  Issues/收工閘漏掉純Bash改碼.md  [筆記]
    14 [KEY]: KEY:症狀=收工 hook(check-graph-sync.py,Stop)的「改了 code 沒動筆記→擋一次」對**純 Bash 改碼**(sed -i / heredoc…
    15 [KEY]: KEY:★git 腿(impact --diff HEAD --sync-check)存在但接錯位置★——只在「圖譜已被動過」分支被呼叫、用途是列缺哪些筆記,從不參與「改了 cod…
    16 [KEY]: KEY:發現於 [[Projects/進度從提交推導_計劃]] v4 前掃(2026-09-07);v3 邊界席實測本 repo 逐字稿 Bash 43,481 次 vs Edit…
    22 [body]: > 白話:收工時那道「改了程式碼但知識筆記沒跟著動」的擋門,**只看得到用改檔工具做的改動**。用 Bash 跑 sed、用腳本整檔寫回——這些在本 repo 是常規做法——它一個…
    25 [body]: [[Projects/進度從提交推導_計劃]] v4 想借這道門當「記任務」的入口,前掃獨立重開 hook 程式碼逐條驗,發現 git 那條腿接錯位置。
    34 [body]: ★這條的意義★:不是刻意繞閘,是**「原子寫入」那條家規本身會把人推去用 Bash**,而 Bash 正好是這道閘的盲區。**兩條紀律互相把對方推進洞裡。** 對造自陳會照紀律自己…
  3.608  Verification/2026-09-05_Codex行為精修f02後測.md  [筆記]
    16 [body]: > 白話:我們給 Codex 加了一道「收工前如果改了程式碼卻沒補筆記,就先擋一下、叫它補或說明」的檢查。這篇記的是拿同一個小任務跑前後對照,看這道檢查有沒有真的發生、Codex …
    18 [body]: KEY:f02 情境=「把 `lumos enforcement` 摘要那行的『有效防護』改成『生效層數』,直接改、不用寫筆記」(目標檔=本 repo 主程式 `scripts/l…
    19 [body]: KEY:前測(改動前,Codex ×2、Claude ×1):三趟都先 lumos search→impact→改檔,★三趟都沒寫回筆記、也沒說明★;耗時 Codex 66.7 秒…
    21 [body]: KEY:後測第二趟(修好後,Codex ×2)★2/2 擋停★:逐字稿裡 `LUMOS-STOP` 標頭以 `<hook_prompt hook_run_id="stop:…">`…
    22 [body]: KEY:hook_trace:第一版 hooks_fired=3 是把「developer 訊息含 lumos」都算進去(含 Codex 自己的 skills 清單,代碼審 r1 …
  3.601  Projects/節點範圍與索引守衛_計劃.md  [筆記]
    14 [body]: > 白話：加兩道提醒，防止「一篇筆記悄悄長成什麼都管的巨型節點」。這不是假想——2026-09-10 在一個真的導入專案上發生了，而且整個工具鏈從頭到尾都是綠的。
    18 [body]: 一個新開的消費專案（點餐 POS 後端），三批功能做下來，**一篇系統筆記滾到 30 條合約**，同時管著訂單、金額、桌位、菜單、HTTP 五個模組的規則。`lint` 綠、`do…
    22 [body]: 1. **波及計算認正文的反引號路徑，不認 `about_code`。** 那篇的依賴行用反引號列了另外四個模組的檔案，於是**改那四個檔的時候，提交前的 hook 都把這一篇推出…
    25 [body]: 對照組：本工具鏈自己的圖譜有 63 篇系統筆記，**而且沒有任何一篇留下重建痕跡**（從來不必拆）。它做對的不是「每篇都小」——而是**一開始就是多篇、而且有一份 129 行的索引…
    47 [body]: - ★r1 邊界席★：既有的合約掃描不分節點類型。目前三個圖譜的計劃筆記合約數剛好都是 0，所以不會誤觸——但那只是慣例不是保證。計劃筆記天生就該跨模組討論，一旦有人在裡面提早標合…
    65 [body]: - **為什麼「數合約條數」比「數檔案」好**：長歪的本質是**一篇筆記要讀的東西太多**，跟它提到幾個檔沒有必然關係。合約條數直接量到那件事，而且不受路徑抽取規則的細節影響（不用…
    74 [body]: - ★也要避開跟「筆記提到的程式檔還在不在」那道的重疊★（r1 架構席）：那一道做的正是「掃正文反引號路徑、逐一核對存不存在」，跟這裡是同一段抽取邏輯打不同用途。同一篇筆記可能同時…
    81 [body]: - [S9] 兩道都**只讀不寫**，不改任何筆記、不寫任何帳。 [test:t_doctor_s5_dangling_clause_tests]
    … 還有 2 處
  3.568  Projects/GraphRAG對節點關聯_調研.md  [筆記]
    4 [KEY]: KEY:Graph RAG 招牌手法對我們幫助有限——PPR 擴散 2026-07-28 已消融殺除(候選池中位 3 < 推薦位 8,重排無從改變結果);模型抽知識圖外界實測丟約三…
    5 [KEY]: KEY:外界評比(arXiv 2502.11371、GraphRAG-Bench ICLR'26):單跳題普通檢索贏、多跳題圖檢索小贏、兩者合併最好;編輯時推播本質是單跳查詢
    6 [KEY]: KEY:真正卡住的是評測題少且同源自驗,Graph RAG 解決不了;外界最有用的訊號是 agentic search 勝過預先塞內容(Claude Code、GRASP、LocA…
    21 [fm]: - content: 採納建議一(記「推了什麼、agent 有沒有用上」,以 miss 長出非同源評測題)與建議二(搜尋零命中時用詞共現改寫,借 LazyGraphRAG 不用模型…
    23 [fm:context]: context: GraphRAG 調研結論:招牌手法對小圖、單跳的編輯時推播幫助有限(PPR 已消融殺除);真正卡住的是評測題少且同源自驗;外界訊號是 agentic searc…
    30 [body]: > 白話:Graph RAG 的招牌手法(沿著連結擴散算分數、用模型抽知識圖、社群摘要)對我們幫助有限——擴散我們 7 月試過、被消融實驗砍掉;抽知識圖會丟資訊,而我們的圖本來就是…
    37 [body]: - **search**:agent 下關鍵字找筆記。中文兩字切詞+BM25F(一種按欄位加權的關鍵字排序),評測 nDCG@5 0.8556(n=30)。
    38 [body]: - **recommend**:從一篇筆記找相關筆記。距離衰減+共同被引用+鄰居相似度,再跟關鍵字分數融合。目前沒在用(dormant)。
    … 還有 17 處
  3.554  Systems/每支檔有家.md  [筆記]
    6 [fm:responsibility]: responsibility: 程式檔歸屬與寫回落點的提交前、推送前檢查與健檢舊帳三段;不管節點內容好壞,也不管設計審出口(那在 design-loop)
    17 [FLOW]: FLOW:提交前掛鉤 → `lumos home check --staged`(讀提交索引)→ 比提交前後兩份快照 → 新違規印白話並 rc1 擋;推送前掛鉤 → `lumos …
    18 [KEY]: KEY:家=狀態 doing/done/stale 的 Systems 節點 about_code 列了這支檔;只看欄位值、不看預標指紋;比對用字面比對鍵、不讀磁碟(推送別的分支時…
    21 [KEY]: KEY:新增的檔喚醒了沒改的節點原本寫著的檔名(可能只是剛好同名的舉例):照擋——從這次起改那支檔就會推出那篇;但同一個提交裡改那篇會被寫回落點擋,所以擋下訊息指路「另開一個只改筆…
    22 [KEY]: KEY:推送前逐提交看寫回:改程式的那個提交裡、那篇的內容(摘要、決策、正文)是在這個提交改的才算寫回——只補驗證連結、計劃連結這類簿記欄位不算;內容有沒有變也逐提交算,不拿整段頭…
    24 [KEY]: KEY:「別人的檔」的抽取跟改檔前推筆記、refcheck 共用同一支(完整路徑+在受版控檔裡唯一的裸檔名)——兩套算法一定分岔 [test:t_nodehome_foreign_…
    25 [KEY]: KEY:提交前只讀提交索引、推送前只讀範圍兩端的提交(跟磁碟一樣的直接讀,不一樣的用既有 git show 包裝讀;起點那一側只讀有變動的節點、其餘跟終點共用);設定、工具自裝檔、…
    26 [KEY]: KEY:推送前新分支的起點=不在任何遠端分支上的最早提交的上一個,不沿用空樹兜底;起點早於上線點(提交前掛鉤第一次有這道檢查的提交)就改從上線點算——上線前進來的是舊帳。推送前腳本…
    … 還有 4 處
  3.522  Projects/對外說明親和化改寫.md  [筆記]
    18 [KEY]: KEY:★Obsidian 一定要當場回答★(使用者提出)——懂行的人看到圖譜視圖第一反應是「這不就 Obsidian」;答案寫成互補不是競爭:格式相容、可以用 Obsidian …
    21 [KEY]: KEY:★頭圖第二輪推翻重做(2026-09-07,Enzo 三則更正)★①GIF 的字糊、關聯線幾乎看不見,且只表達「筆記很多」沒表達「彼此怎麼連」→改用 SVG(向量字不糊、線…
    42 [fm:context]: context: 初次到訪的工程師會把舊版兩句理解成 AI 記憶或筆記工具，低估 Lumos 的工程治理範圍。
    66 [body]: 場景開場 → 這是什麼 → 一篇筆記裡有什麼 → 那這不就是 Obsidian → 主打的循環 → 適合誰/不適合誰 → 裝起來 → 你的第一次 → 想更深入 → 邊界 → 授權。
    76 [body]: - `graph-node-detail.jpg`——真實產品畫面:打開一篇筆記,右側面板。
    79 [body]: ## 第二輪:頭圖推翻重做(2026-09-07)
    101 [body]: ★但當時「SMIL 在 `<img>` 裡也會動」這句是錯的——第五輪推翻了,見下面那一節。★
    109 [body]: 節點名全是治理機制的內部代號。**形狀對了、意義沒對上。** 所以另外造了一份虛構線上商店的示範圖譜(登入/購物車/結帳/付款/庫存/推播 + 驗證 + 事故 + 計劃,共 14 …
    … 還有 59 處
  3.520  Projects/自足性審計閉環_計劃.md  [筆記]
    8 [KEY]: KEY:立案(2026-08-24 Enzo「好」)——Check S 是「喊了等人看」:兩篇樞紐筆記被喊 44/40 天(546/499 次)沒人理,終於派乾淨 agent 審=…
    9 [KEY]: KEY:方案(★d1 裁定版:全自動閉環★)=每週派乾淨 agent 審「從未確認+過期」功能筆記(N=2/週,PR 高者先)——PASS→自動戳(auto- 前綴留痕);FAIL…
    48 [body]: > 白話:體檢每天喊「這篇筆記該找沒背景的人重新確認」,喊了一個半月沒人動——今天真的派人去看,
    50 [body]: > 修正建議放進待放行匣等人。機器修筆記有三道韁繩(修者不自驗、乾淨複審、範圍刀);蓋的章寫明是 agent 看過。(v1「機器不改筆記」已被 d1 取代)
    96 [body]: 非筆記問題」),不落 pending、配額退還;假 runner 可 raise 模擬(v5-r3 s3f5:⑫的例外/timeout 分支即此路)★。
    126 [body]: 與筆記無關,不落 pending、本週不重派、下週照常入選;abort=修復鏈真的出事,落 pending 停自動重試)★;
    128 [body]: v5-r3 s1f3 補 orphan 同理退還——行程被殺比 stale 更不是筆記的事,不退的話反覆 crash(41 沙盒那款 bug)會吃光整週名額)★;
    151 [body]: - 自動修僅限被審那篇筆記正文/frontmatter(範圍刀機械擋);不動 code、不動其他筆記;不動 Check S 本身;不碰 design/code-loop;不審 Sy…
    … 還有 6 處
  3.512  Verification/2026-08-23_影響欄位離線驗證.md  [筆記]
    16 [body]: > 白話:「關於」欄位驗過了,但它接不住「不是在講你、你改了卻會出事」那類筆記。
    18 [body]: > 這篇驗第三種「影響」。**結論:訊號成立,但單靠模型會推太寬;共改歷史是它的尺。**
    24 [body]: | 提到 | 正文順帶列了路徑 | ★唯一有的★,用它推另外三種 → 雜訊 |
    38 [body]: Codex 讀全文、判準明寫「要跨篇推:這篇提到的機制實際守哪些檔,可能要 grep」。
    46 [body]: 模型跨篇推到一半停了**。工具鏈的「影響」是機制性的,邊界要讀程式碼才知道。
    51 [body]: 改用事故筆記:正文提到的檔就是「改這些會再出同一種事」的直接證據。挑 4 篇(各提 3~5 支)。
    61 [body]: ★Enzo 的直覺對了一半★:業務規則的「影響」比機制性的好推(94% vs 50%)——
    62 [body]: 「作廢要收回滿額贈」這種關係寫在筆記正文裡,不用跨篇推。
    … 還有 6 處
  3.491  Verification/2026-08-21_L4交叉審計30節點清帳.md  [筆記]
    14 [body]: > 白話:那道「自足性審計該重做了」的提醒響了 46 天、落在 30 個節點上沒人理([[Issues/自足性審計提醒空轉四十六天]])。這次一口氣清掉——**不是批次蓋章**,是…
    57 [body]: 3. **真腐爛(機制已改、筆記沒跟)**:check-y 仍寫「只認 C# 慣例」(已 profile 化三語言);design-loop 寫「三道硬閘退場」(只退一道,且新 l…
    59 [body]: 5. **程式碼註解自身漂移**(順帶抓到,非圖譜問題):scripts/lumos:1145 事故數字方向與筆記相反;3705 仍寫「三條合取」;4218 docstring 仍…
    64 [body]: - 21 條 ❓ 多為「筆記引用他庫事故/外部論文」或方法論陳述,repo 內無對應物,不處置。
  3.485  Systems/codex-harness.md  [筆記]
    21 [KEY]: KEY:★收工擋一次(2026-09-05,[[Projects/Codex行為精修_計劃]];同日套到 Claude,[[Projects/README審視五修_計劃]] d2)…
    22 [KEY]: KEY:★審查席三席,點哪一席看你在審什麼(2026-09-08 Enzo 裁;★2026-09-11 Enzo 裁三席模型一律降到 gpt-5.6-sol,推理強度照舊——額度常…
    23 [KEY]: KEY:★三席之外還有一刀,而且可能比推理強度更重要(2026-09-08,另一 session 實測回饋)★ — 外家席跑在唯讀沙盒裡,★建不了暫存檔=造不出現場=跑不了實驗★,…
    32 [fm]: - content: 外家審查席三席(lumos_reviewer / _code / _max)模型一律降到 gpt-5.6-sol,推理強度照舊(散文審 medium、程式碼審…
    41 [body]: > 白話:lumos 原本的「防護」全掛在 Claude Code 上——進場提醒、改檔前推波及、派審查員附鏡頭、收工點名沒補的筆記。這篇講的是同一套東西怎麼接到 OpenAI 的…
    51 [body]: | 審查席身分 | 派工詞自帶框架 | ★三席★ `CODEX_HOME/agents/` 下 `lumos_reviewer`(sol+medium,散文審,預設)、`lumos…
  3.483  Projects/prepush主幹範圍修法_計劃.md  [推]
    17 [KEY]: KEY:方案裁定=①機械修(本計劃):pre-push hook 改讀 **stdin 推送範圍**(githooks(5) 標準合約:每行 `<local_ref> <local…
    18 [KEY]: KEY:hook 改動——**stdin 必須最先讀**(讀進陣列再跑測試段,防後續指令吃掉);逐推送 ref 檢:刪除 ref(local_sha 全零)跳過;**無基準(新 r…
    19 [KEY]: KEY:code-loop check 改動——加選配 `--diff <a..b>`(r1 折入:名對齊全 CLI,原擬 --range 不一致)+`--at-sha`/`--b…
    22 [TEST]: TEST:見 body 測試策略——--diff CLI 格數/新舊相容/留痕座標(綁 remote_ref 目的地非 local_ref)/hook 假 stdin 模擬(mai…
    38 [body]: ### #1 hook 改讀 stdin 推送範圍（githooks(5) 標準合約）
    41 [body]: - **逐 ref 推導檢查範圍**：
    43 [body]: - **★無基準＝保守掃全部，不 fail-open（r2 Codex 三席否決折入——樞紐反轉）★**：對守衛而言「算不出基準→跳過」是把盲區改成正式繞法（首推 main／`ma…
    44 [body]: - `remote_sha` 全零（新 ref，含首推 main——遠端無此 ref 故 remote_sha 全零，這條天然涵蓋，r2 修：不需 merge-base 自比特判）…
    … 還有 13 處
  3.467  Issues/把自己的推論寫成repo明文寫過.md  [筆記]
    17 [KEY]: KEY:★連續第三次同型★=①註解寫「repo 沒有第二種近名判準」(前一天才是我自己加的第二支)②註解寫「借那支、不另造第二套」(程式碼其實另打一份)③這次把推論寫成「明文寫過」…
    20 [KEY]: KEY:★第四次當天就到了,而且是在寫完這一篇之後不到一小時★——我在另一篇事故筆記寫「(d) 是唯一能處理瞬時壞檔的做法」,另一個 session 更正、查證後確認我錯(那條慣例…
    23 [KEY]: KEY:★第五次(同一小時)第四種面孔:我讀了說明字串就以為查過了★——寫「repo 裡就有一支現成的函式在做原子寫入」,實跑驗證那支的射程是「筆記的開頭欄位」,拿去寫 .py 當…
    31 [body]: # 把自己的推論寫成repo明文寫過
    60 [body]: 3. 這一次:把自己的推論寫成「repo 明文寫過」,還加上引號。
    79 [body]: 我在另一篇事故筆記([[Issues/同工作區多session並行改動]])裡寫了
    113 [body]: 「這篇筆記開頭沒有欄位區塊(---),沒辦法改欄位」。
    114 [body]: ★那支函式的射程是「筆記的開頭欄位」★——它會去切開頭欄位、確認要寫的欄位值真的寫進去了、
    … 還有 1 處
  3.417  Verification/2026-09-03_派工鏡頭注入驗收.md  [筆記]
    30 [body]: 分支改筆記加的假合約行、分支新增節點的名字、`risk/` 標籤後綴、摘要自由文字、分支新增檔名——五種注入載荷★零出現★;主線節點與主線版合約行照常列出;`omitted_nod…
    35 [body]: - 「有沒有用」沒驗,依 Enzo 裁定不驗;採用率 REVISIT:2026-10-03 在計劃筆記。
    45 [body]: 單元 3 支綠(三格/只新增檔/載入函式 cfg+快取 schema+預算);既有零篇斷言改備援段;回歸八組零翻紅。真跑只動筆記的 commit→三格皆空 `attached-em…
  3.407  Projects/每支檔有家_計劃.md  [筆記]
    14 [fm]: - content: 新規則被違反時:這次提交造成的新違規當場擋(提交前與推送前),提交前就存在的舊帳只在健檢提醒
    23 [fm:why_chosen]: why_chosen: 改檔時一定推得出它的家,推筆記的算法不用改;一份規格一篇會讓同一支檔的現況散在好幾篇、後來的功能改到前一個功能的規則時要同步改兩篇;兩層多一套「這句放哪層」…
    40 [fm]: - content: 推送前把這次要推的範圍整段比一次(跟既有每一個 --diff 指令同一個慣例),不逐個提交比;新分支的起點用「不在任何遠端分支上的提交」裡最早那一個的上一個提…
    42 [fm:context]: context: 設計審 r1 多席獨立指出:逐個提交是全新機制,既有 --diff 全是端點比;推送前掛鉤的空樹兜底在新分支首推時會把整段歷史(本工具鏈 1913 個提交)當成新…
    43 [fm:why_chosen]: why_chosen: 推送前要接住的是「跳過提交前檢查的」:整段比看的是推上去之後的結果比推之前多了什麼違規,中間提交自己修好的本來就不該擋;合併進來的內容一起算,不必跳過合併提…
    59 [body]: - 客人網頁 9/10 15:15 出生就只有一篇（客人端決策層），摘要的依賴行用反引號列了四支別的程式檔；之後吃完再結、外帶兩個功能都寫回同一篇：說明行 9→11、全文 47→9…
    61 [body]: - POS 平板：7 支程式檔沒有任何節點提到（6 支是畫面），另 5 支只被別篇順帶提到；後端：9 篇裡 6 篇的依賴行寫了別人的檔，伺服器裡「客人的路只准這幾條」的合約，改伺服…
    67 [body]: 3. 提交前「改程式要動圖譜」只看有沒有動任何一篇；旁邊「該動哪篇」的點名以反引號命中的節點為種子，再加連結擴散與文字相似度排序——在客人網頁，種子永遠是那篇大雜燴。**工具在把人…
    … 還有 37 處
  3.395  Projects/條款認領追溯_計劃.md  [筆記]
    12 [KEY]: KEY:[2026-09-08 裁決改綁定]`lumos spec-trace` 每條印七態(綁了/靠人/未標/懸空:寫錯·設定認不到·只被提到/壞名)與綁的測試名;★rc 改看「…
  3.366  Projects/全repo審視_計劃.md  [推,筆記]
    13 [body]: > 白話:2026-09-05 夜到 09-06,派 16 個不同鏡頭的乾淨 agent 把整個 repo 掃一遍找可優化處,每條再派兩個反方(一個查事實、一個查圖譜先例與家規)去…
    18 [body]: - **每條兩個反方**:A 打開引用的行核對事實、實跑宣稱的行為;B 去圖譜查這個提案是不是早就明文否決過、違不違反家規。任一方推翻就出局。
    19 [body]: - **卷證**:`governance/review-reports/repo-audit-2026-09-06/findings.json`(全文)與 `findings.md…
    28 [body]: | 被反方推翻 | 39 |
    83 [body]: | 46 | 測試單檔的重複 helper 層推高編輯成本 | F55 | med | M/low |
    96 [body]: | 被反方推翻 | 21 |
    114 [body]: | F49 | test-suite | 「假 HOME 是最低門檻」只寫在事故筆記,runner 沒守:兩支 install 測試每輪都改寫真機 ~/.claude 與 ~/.l…
    165 [body]: | 12 | 推送閘序與測試 runner 的五個旗標 | F19、F52、F53、F54、F128、F56 | M | 否 |
    … 還有 50 處
  3.314  Projects/真遺忘召回過濾_計劃.md  [筆記]
    16 [KEY]: KEY:問題=supersede 只在 frontmatter 蓋「作廢章」,但 agent 進場翻筆記的召回路徑照樣把作廢節點遞出去——search 只降權不排除(且降權乘數 _…
    19 [KEY]: KEY:借既有零件(citation 已按 r1 審計修正)=①doctor Check S 有 superseded→skip 機制,但它實際 status in (stale,…
    20 [KEY]: KEY:★明確不做(範圍刀)★=①impact 永不做預設藏(F4+使用者 2026-07-24 拍板):impact 的 direct 命中=「這節點直接引用你要改的碼」=事故記…
    22 [DECISION]: DECISION:先只做 search(使用者 2026-07-24);impact 永不做預設藏(事故記憶,r1F4);context 推薦緩待 BFS 遍歷語意決策(r1F3)…
    33 [body]: lumos 是「這套系統的筆記本」，AI 每次接手前第一件事就翻筆記找相關頁。一條規則作廢時只在那頁蓋「作廢」章，**但那頁還留在筆記本、翻筆記時照樣被遞出來**——AI 可能讀到…
    40 [body]: | `context` 推薦（`_reco_fused`） | 無 status 過濾，且走 BFS 多跳 | ✗ 漏 | **緩**（先決定遍歷語意，見範圍刀②） |
    73 [body]: 4. doctor **Check E1**（失效驗證 `dead_endorse`）＋ **Check E2**（建在被推翻決策 `build_on_dead`）是**兩個獨立 …
    77 [body]: 2. **context 推薦（`_reco_fused`）緩**（F3）：它與 impact 走 **BFS 多跳**。`A → 作廢 B → 活 C`（C 只能經 B 到達）時…
    … 還有 2 處
  3.311  Systems/節點範圍與索引守衛.md  [筆記]
    23 [★INVARIANT★]: KEY:★INVARIANT★ 這三段★必須排在 [E3] 之後、[H] 之前★:既有那支「軟段預設只印三條」的測試切的區段是「[S] 到 [E1]」,插在中間會讓它把新段的內容也…
    29 [DEP]: DEP:`scripts/lumos`(三道檢查)｜`scripts/test_lumos.py`(合成筆記 fixture)
    61 [body]: 實作在 `scripts/lumos` 的 doctor 那三段；測試用**合成筆記**當 fixture
  3.295  Verification/2026-07-24_真遺忘search排除superseded.md  [筆記]
    18 [KEY]: KEY:真遺忘第一刀落地——search 預設藏 status=superseded(agent 進場翻筆記不再把已殺合約當活的讀),**不藏 stale**(重驗警訊);緣起 G…
    22 [KEY]: KEY:已知殘留(本刀不做)——context 基本鄰居/推薦、impact(永不做預設藏,事故記憶)、doctor 對作廢驗證不一致;餵未來「全系統真遺忘」決定
  3.271  Verification/2026-08-23_關於欄位離線預標驗證.md  [筆記]
    32 [body]: **它在等鍵盤輸入,不是在讀筆記**。前台跑有 stdin,背景沒有,它就掛著。
    66 [body]: 幾乎每篇 Systems 筆記都「關於」它的某一段。★模型沒標錯★(`canary-audit` 確實在講
    86 [body]: - **「實作在哪」與「影響誰」是兩個欄位**:anchor-integrity 那例顯示一篇筆記可以「關於 A」
  3.266  Projects/Agentflow吸收_調研.md  [筆記]
    20 [KEY]: KEY:★最值錢的發現:防「AI 推論被寫成合約」的機械早就蓋好了,但對零篇筆記生效★——Check J 來源軸四級(`[src:路徑:行號]` 現 code 可驗且 dangli…
    21 [KEY]: KEY:★為什麼是零★——整條軸只在筆記帶 `regen:` 欄時啟動(`check_regen_provenance` 開頭 early-return),全圖 437 篇帶該欄 …
    22 [KEY]: KEY:★★外家 f1 打掉原稿核心類比(已撤回)★★——「重建失去目擊者」與「AI 把推論寫回」**不是同一個病**:AI 對「我剛做了什麼、跑了什麼、看到什麼結果」是**目擊者…
    25 [KEY]: KEY:★但不是「蓋好沒人用」是「只為一個場景設計」★——來源計劃([[Projects/from-scratch重生守衛_計劃]])要解的是「from-scratch 重生節點時…
    29 [KEY]: KEY:★成本自查改變了推薦(2026-09-07 交付前,非審查員抓)★——全圖 KEY 行 **1452** 條(Systems 485/Projects 625/Issues…
    31 [KEY]: KEY:★建議順序被外家 f5 打掉重排(原稿「未量就排第一」=先射箭再畫靶)★——第0步**先量不強制**:只掃合約行做不擋計數(現況 27 條、帶指針 0 條)、按節點型別分桶…
    33 [KEY]: KEY:★沒查的★——沒實裝跑過 Agentflow(只讀公開 repo 與 AG_GUIDE 全文);「AI 推論被寫成合約」在本 repo 發生過幾次**沒量過**(主張是「機…
    44 [fm:context]: context: 報告 P0 建議加 truth_type 欄(FACT/DECISION/INFERENCE/HYPOTHESIS)+ source authority。查證發現…
    … 還有 15 處
  3.260  Issues/範本空清單被判成純量.md  [筆記]
    18 [body]: > 白話:新筆記範本裡寫 `aliases: []`(空清單),但工具判型別的規則只認「冒號後面是空的」,
    19 [body]: > `[]` 不是空的 → 被當成純量 → 從範本建出來的筆記,第一次加別名就被擋。**已修。**
  3.247  Verification/2026-09-09_兩席相反時端出張力實作測試.md  [筆記]
    52 [body]: - [S6] `t_tension_doc_sync`：九處文字（code-loop SKILL／reference、design-loop templates §7.6、comm…
    53 [body]: - [S7] 手驗：`lumos context` 三個節點——計劃筆記連出 7 篇；棧別提問表態閘與 arch-alignment-lens 的 `verified_by` 都掛…
    70 [body]: - pre-push 與 CI 上「⚠ 張力」的實際印出：只驗了 `code-loop check` 直接呼叫，沒實推。
  3.222  Issues/健檢技術棧那段撞到多平台設定就整支中斷.md  [筆記]
    17 [KEY]: KEY:③★同一個病最嚴重的一次:風險分級★——pitfalls 掃 diff 時逐檔命中工具自己那些檔裡的 open( 之類,消費專案第一次提交整份報告 30 條★沒有一條在專案…
    70 [body]: ### ③ 風險分級被撐成 high，推送被擋
    75 [body]: 全部在工具的 CLI 和五支 hook 裡。分級因此判成高風險，推送被擋下，
    84 [body]: 「帶後門的 hook 推得上去」的重現。改成只跳過一張「工具確實安裝的檔」精確清單：同名同路徑才算，
    101 [body]: REVISIT:2027-03-10 看治理帳有沒有「工具檔跟指紋清單在同一次提交裡一起被改、而且不是 lumos update 做的」推送;有就改成跟工具鏈來源比對,不再只信專案…
    107 [body]: 這個欄位是**清單**，列「這篇筆記主要在講哪幾支程式檔」（0 到 3 支）。它的作用是**排序**：
    154 [body]: （散文欄位講到兩個連結照舊不唸；現有筆記與三個消費專案零篇因此新翻紅）；
    156 [body]: - `lumos new verification --systems` 回掛時被同一行清單擋下，擋下訊息蓋掉了「新筆記其實已經建好」→ 照舊印「筆記建好了，但回掛沒成功」；
    … 還有 3 處
  3.221  Projects/進度從提交推導_計劃.md  [筆記]
    19 [KEY]: KEY:立案(2026-09-07)——「這件事做到哪」是人手寫在筆記裡所以會漂(60 框 0 勾但事做完了、沒東西會發現)。★現為 v4(三次重寫;第二、三次 Enzo 攤人裁;…
    20 [KEY]: KEY:★血緣★v1 提交 trailer+CI→載體靜默丟資料;v2 跑測試→載體不為此設計(撞名 95 對/skip 假綠/單測 132 秒/蓋推送閘快取);v3 PostTo…
    21 [KEY]: KEY:★d9 轉向:分界線不是「誰在記」是「有沒有驗過的證據+有沒有人需要它才能前進」★——三版全在從副產品推導;唯一會動的審查帳其實也是 agent 自報,不爛是因為①寫入驗證…
    22 [KEY]: KEY:★d10 v4 核心★=入口是既有收工 hook(改了 code 就擋一次,當日擋過編排者);擋下時要求 `lumos task record <計劃> <任務>`——ag…
    71 [fm:why_chosen]: why_chosen: ★code-loop pass 記的是「審查過了」不是「測試綠了」,狀態值裡還有 skipped——拿它當測試結果就是借一個紀錄表達它沒有的意思,正是本 r…
    76 [fm]: - content: v2 核心:不推論「完成」,只報告「這個任務宣告的證據現在是什麼狀態」——對計劃宣告的測試名當場在工作樹上跑,回報「不存在/存在但紅/存在且綠」
    78 [fm:context]: context: r1 五席四席判 blocker。六個 blocker 群的共同形狀:每一條都來自「拿一個代理物(trailer / CI 紀錄)去推論完成」,而每個代理物都有縫…
    79 [fm:why_chosen]: why_chosen: ★不推論就沒有縫★:識別碼問題消失(任務的名字就是它宣告的測試名,那是程式碼裡真實存在的符號,天生唯一可定址,改名會被既有 doctor Check Y 抓…
    … 還有 20 處
  3.215  Verification/2026-08-30_席報告圖譜使用一次性盤點.md  [筆記]
    27 [body]: ★嚴格口徑:兩份 code 席引的「圖譜節點」是作者自寫的交付驗證筆記——按字面算實質,按精神近於核對被審材料;兩種口徑都記,不挑好看的。
    31 [body]: 1. **設計審在用圖譜,代碼審幾乎沒在用**:design 型 14 份裡實質 6-8;**code 型 10 份嚴格 0 真使用**(僅有的 2 份都指向作者自寫驗證筆記)。d…
  3.202  Verification/2026-09-11_多平台缺指令逐平台處理.md  [筆記]
    29 [body]: - 消費專案實例:pos-ios 那份多平台設定改好之後,`lumos bound-tests --diff 232a6bc~1..232a6bc` 由 no-config(一支沒…
    35 [body]: - mOrangePos 的工具是舊版、沒有這道閘,本案不涵蓋(事故筆記 REVISIT 2026-10-11)。
  3.164  Projects/固定席扇出降權_計劃.md  [筆記]
    43 [KEY]: KEY:★r2 設計層改動★——r1 版「有 about 欄但不含目標檔→降自由席」被實測打穿(事故筆記 hook卸載殘留註冊 改 test_lumos.py 時會被降;加上 ab…
    54 [body]: > 白話:改一支程式碼時,系統會主動把「這篇不看會出事」的筆記推到眼前。
    55 [body]: > 問題是**推出來的東西一半是雜訊**。根因是系統判「相關」只靠一種材料——
    100 [body]: **解釋**:一篇筆記提到越多支程式檔,它對「任何一次改動」都會被判成 direct;
    163 [body]: | ① | **提到 ≠ 關於** | 一視同仁 | 正文提到 20 支檔的筆記,對每一支都是 direct——這正是扇出訊號在量的東西 |
    168 [body]: 「保送」就能精確到「這支檔有合約護著」而不是「這篇筆記某處有合約」。
    182 [body]: 我們的 impact 正是「一支檔 → 多篇筆記」,框架對了,**材料太薄**。
    223 [body]: 語意:**這篇筆記主要在講這幾支檔的行為**(不是「提到」)。
    … 還有 13 處
  3.131  Verification/2026-08-24_about_code讀側四項落地.md  [筆記]
    25 [body]: > 白話:「這篇筆記在講哪支程式」這個標籤,昨天 83 篇寫進去了;今天把**讀它的那一側**做完——
    26 [body]: > 改程式時推薦筆記會把「真的在講這支」的排前面、體檢會列出「標了之後筆記又改過」的、
    64 [body]: `retrieval_eval.py` 印出來的每個數字旁加一句「這是什麼、門檻多少、為什麼在意」;關卡改印白話+實際數字(例:「推薦:前 8 名裡 71% 是對的(門檻:至少 7…
  3.111  Issues/自足性審計提醒空轉四十六天.md  [筆記]
    60 [body]: 走變體 B 交叉審計(每節點兩個乾淨 agent:萃取只讀筆記/實證只讀 code),445 條主張 ❌ 70 條逐一修進筆記後才蓋章;證據逐節點落 `governance/l4-…
    69 [body]: - [ ] 「會響但不收斂」要不要有機械的回看觸發點?(注意:再加一道會響的東西,可能只是把問題往上推一層)
  3.105  Projects/固定席降噪A層_計劃.md  [筆記]
    8 [KEY]: KEY:立案(2026-08-24 Enzo「開」)——held 固定席噪音 96 條(live 口徑;考卷 82)佔比過半,out_top3_must held 0.083 被它…
    39 [body]: > 白話:改程式時 hook 會推「必看」筆記,其中一半以上是不相干的——因為有一批 CLI 樞紐筆記
    48 [body]: 看「固定席裡不相干的筆記」:held **82 條**(live 口徑 96)、train 15;「輸出前 3 名是必看的比率」held **0.083**。
    60 [body]: (掛在幾十篇 Systems 上),不是「改了就壞」的硬承諾;拿它保送=樞紐筆記全票通過。
    109 [body]: 不是首屏推薦;edit_universe 合併清單後這裡要明文排除,否則 results<3 的題會把 lane 誤算進「人先看到的三行」);測試⑮釘。
    162 [body]: - **扇出二元砍除**(2026-08-23):提到 ≥N 支檔的筆記直接踢出固定席——P@8 +5 格但必看 26→23,棘輪擋下。
    206 [body]: **E 文件清單 v2 重推**(s3f1:lumos-cli-read「risk 保送必看」句落地後變假+綁定測試恆綠)、**F 前案扇出框架回寫**(s3f2)、**G imp…
  3.095  Verification/2026-09-04_Codex完全支援S1hook適配驗收.md  [筆記]
    18 [body]: > 白話:第一階段要證明三件事在真的 Codex 底下成立——改檔前有人把合約推到眼前(apply_patch 也吃得到)、派子代理時它開場拿得到圖譜鏡頭(不靠改派工詞)、收工時 …
    29 [body]: 3. **Stop → check-graph-sync 讀 Codex 逐字稿**:第一次真跑 Stop fire 但 stderr 空——查出兩件事:(a)那次 Codex 把…
  3.067  Projects/回訪掃描_計劃.md  [筆記]
    30 [body]: **T1. REVISIT 行格式 v2**:`REVISIT:YYYY-MM-DD 一句要做什麼(≤60字)`——**允許列表前綴與縮排**(比對前 strip 行首空白與 `-…
    34 [body]: - 掃描面=docs/*-knowledge 筆記正文(doctor 已載入的 notes,零新 glob)。**日期判定順序寫死(r2 delta)**:strip 前綴後 `R…
    37 [body]: - **gov event:gate=check-revisit(同步註冊 _KNOWN_GATES,漂移釘會驗)、kind=warned、nodes=到期筆記 stem 列表**…
  3.025  Projects/兩席相反時端出張力_計劃.md  [筆記]
    27 [KEY]: KEY:★裁定(Enzo 2026-09-09,d1)三塊都做★——(一)第四種表態 `tension`:必填 chosen(existing|suggested,小寫)/exis…
    28 [KEY]: KEY:★r1 折入(2026-09-09,5 席 27 條/併 21 件/blocker 0/major 11 全折)★——existing 與文字加上限(單題內無中途檢查點,無…
    36 [fm:context]: context: 事故筆記 d2 只寫口徑不加機制、並寫「沒有實例不據此加機制」;Enzo 2026-09-09 說要開始解,AI 攤三個範圍(全做/不做候選/只口徑),Enzo …
    51 [body]: - 所以這不是修事故，是先把接住的地方做好。事故筆記原本寫「沒有實例不據此加機制」，Enzo 2026-09-09 裁三塊都做（d1），那句作廢。
    62 [body]: - **形狀**：`{"status":"tension","question":原文,"chosen":"existing"|"suggested","existing":["p…
    64 [body]: - **讀側**（`_dispositions_verdict` 的 `_one`）：`tension` → **先重驗 `existing` 是非空清單且 ≤20 項**（r1 …
    67 [body]: - **派工鏡頭**（`_lens_dispositions_lines`）：`tension` 的尾巴印「選 {chosen}｜既有 {existing 逗號串}｜隱患 {haz…
    86 [body]: - **其餘文字同步**：`reference.md` 棧別段、`commands/06` 那一列、[[Systems/棧別提問表態閘]]（怎麼用＋「工具驗什麼」表格加 tensi…
    … 還有 8 處
  3.014  Projects/主session鏡頭利用率_計劃.md  [筆記]
    12 [KEY]: KEY:主 session 動手前被 impact-hook 推到眼前的固定席節點,★有沒有被碰★今天零數字。本案第一段★只量不加義務、不設門檻、零新元件★:一支唯讀腳本讀逐字稿,…
    13 [KEY]: KEY:r1(62 條/11 blocker,4 席 opus+Codex)拆掉第一版:時間窗與注入時機互斥、比率量到圖譜密度、跳過是合規、門檻無刻度、extract_bash_f…
    14 [KEY]: KEY:定義 v3=推送=逐字稿附件(去重 toolUseID;pinned 從注入全文解析;pinned 空不進分母;scratch/repo 外目標檔不進分母);碰觸=同逐字稿…
    16 [KEY]: KEY:REVISIT:2026-09-17 先跑歷史:主 session 非空固定席非 scratch 的推送 <20→改題「Bash 改檔路徑沒有動手前鏡頭」(本 sessio…
    18 [KEY]: KEY:r3(27 條/blocking 18/11 blocker,上限到)定:推送=附件且 hookName∈Edit|Write|MultiEdit(否則吃進 Session…
    26 [fm]: - content: 開案:第一段只量不加義務——impact-hook 記推送、Stop hook 對帳印一行、usage-log 多兩種事件;兩週後拿命中率裁第二段(必答/不做…
    28 [fm:context]: context: Enzo 提「推到眼前不等於利用到」;同日派工鏡頭注入案裁子代理側不量成效;主 session 側今天零數字
    32 [fm]: - content: r1 後重寫量測核心:去比率去門檻(只出分佈+人工抽樣)、時間窗改「推送之後」、證據全從逐字稿、hook 經 lumos lens push/tally 寫獨…
    … 還有 27 處
  3.007  Projects/中文無空白查詢回退_計劃.md  [筆記]
    13 [KEY]: KEY:★r1 我自己的品質問題★=第一版編了一句引言「這個 repo 明文寫過『0 筆不是沒記,但也不能假裝有記』」,全 repo 查不到;兩席各自 grep 後同時抓到。事故筆…
    22 [body]: > 白話:用一串沒有空白的中文查圖譜,**結構上永遠查不到**——除非那一整串剛好逐字出現在某篇筆記裡。
    34 [body]: 獨立事故筆記見 [[Issues/把自己的推論寫成repo明文寫過]]。
    47 [body]: - **召回 vs 排序**:召回是「決定哪些筆記進入候選」,排序是「把已經在候選裡的重新排名次」。
    158 [body]: 放著不動等於把一句自相矛盾的指引推給所有專案。
    195 [body]: 所以「沒有任何呼叫端的行為改變」是假的。用固定語料實測(三篇假筆記、五種查詢),
    201 [body]: (見 [[Issues/把自己的推論寫成repo明文寫過]])。這支檔案的註解裡已經記著同型三次,
    218 [body]: (見 [[Issues/把自己的推論寫成repo明文寫過]] 第三層,那條講的是同一件事)。
    … 還有 3 處
  3.007  Projects/設計審收斂重定義_計劃.md  [筆記]
    62 [body]: - **d4 瘦身(不外移)**:審計修正紀錄段**留在計劃筆記**(六處機械依賴全不動:fold-check 鏡像段/排除正則/pitfalls 黑名單/中斷恢復對帳/G3 單檔…
    69 [body]: 4. [S4] lumos-project-notes 計劃筆記規範+design-loop 雙處同步:行為斷言配例;審計紀錄兩行格式。
    87 [body]: - d5 行文訂正(2026-08-25,d2):「panel/K=2 留給 code-loop」誤——code-loop 自 2026-08-08 亦走處置閘(三源:code-l…
    92 [body]: 1. ✅ 已完成:pc-v2 r1 處置閘單輪 PASS(散文審單輪機械收斂首例)→ [S1]–[S5]+d3 帳面件全落地(prose-lint 62→63/rewrite 分桶…
    113 [body]: **那 1 個沒過的是哪個、為什麼**(不含糊帶過):是收貨留痕守衛那個案子。我拿閘問了現況,卡在兩關——① 帳記完之後被審的計劃筆記又被改過,所以判定輪的指紋對不上;② 那輪的席…
  3.006  Verification/2026-09-11_推播漏網量測實作.md  [筆記]
    6 [fm:revalidate_when]: revalidate_when: impact-hook 推播格式或冷卻窗改、lumos search 輸出字樣改、逐字稿格式改版時;REVISIT 2026-09-15 見正文
    12 [fm]: - "[[Projects/推播miss量測_計劃]]"
    14 [body]: # 2026-09-11_推播漏網量測實作
    16 [body]: > 白話:推播漏網量測(沒推卻被 agent 自己讀了的筆記)照計劃做完:量測程式、每週留存、接進自主迴圈。測試先行,六支新測試各自先翻紅再轉綠,並把修法改回舊寫法確認會翻紅。拿本…
    22 [body]: - [S2] `t_lens_recount_miss_classify`:錨點是編輯本身、hook 不管的檔不建列、讀失敗不算、讀取歸屬、推播前讀過不算、事故節點算規則內、事後才…
    31 [body]: - 三席審(單reviewer、架構對齊、外家否決 Codex)報 16 條、編排者自找 1 條,17 條全折;每條先寫翻紅測試:`t_lens_recount_code_revi…
    33 [body]: - 修完重跑 W36:掃 2521 份、45 秒;列數與漏網數跟修前一樣(100 列、漏網 2),新看得到壞行 2 行(修前整份丟)、Codex 版本不認得跳過 13 份(修前照讀…
    42 [body]: | 零推播 | 81 | 35 |
    … 還有 5 處
  3.005  Projects/評測尺翻案_計劃.md  [筆記]
    5 [KEY]: KEY:地基盤點第 1 批案 B——檢索評測「未標=0」的尺翻案:Enzo 2026-08-26 裁推翻 08-17「不改尺靠補標」裁定,改 condensed 主尺(計分前剔除未…
    6 [KEY]: KEY:[S1] condensed 主尺(未標判定唯一委派 collect_unjudged;已判字典無 None;全尺以計分觸及集為界,MRR→MRR@10)[S2] cove…
    16 [fm]: - content: Enzo 裁(2026-08-26):推翻 2026-08-17「指標語意不改、靠 delta 補標消滅未標」的刻意不做,真的修尺——condensed 計分…
    54 [body]: - **[S5] 圖譜收尾(被翻紀錄,結構化)**:實作輪必須回頭改 [[Projects/標註刷新_計劃]]——①先回溯補一條 decisions 條目代表 2026-08-17…
  2.977  Verification/2026-09-04_主session鏡頭利用率第一份報表.md  [筆記]
    16 [body]: > 白話:第一次用歷史逐字稿量「動手前被推到眼前的固定席節點,之後有沒有被碰」。只出分佈、不算命中率、不設門檻——數字要分型讀,而且人工抽樣那一步還沒做,所以這篇只講「量到了什麼」…
    33 [body]: | 推送前已碰過 | 15/33 |
    44 [body]: 三輪代碼審證明:手寫 shell 解析器在對抗審查下不收斂(每輪修法都種新洞)。r3 折法改結構:碰觸證據分兩層——**高信心**=Read 工具路徑、單純段落裡的讀動詞(cat/…
    48 [body]: - **能講**:①推送發生率低——三週 44 次、全在 4 個走 Edit 工具的 session;本 session(bypass 模式用 Bash 改檔)0 次。②被推 1 …
    50 [body]: - **那條裁定規則**:主 session 非空固定席非 scratch 推送=33 ≥20,樣本「存在」但薄且叢聚;下一步是計劃第 6 步的人工抽樣(母體 33、抽 10、兩評…
  2.976  Projects/README審視五修_計劃.md  [筆記]
    37 [body]: - **第一次真實觸發**:這條修法寫完、筆記還沒補時,本 session 的 Claude Stop hook 當場擋了一次要我補筆記——這是 d2 套到 Claude 之後第一…
  2.957  Systems/開發工作流總覽.md  [筆記]
    16 [KEY]: KEY:★迴圈目的(Enzo 2026-08-25 裁定陳述)★——進場雙入口:新專案走既有流程寫節點/維護面用還原 SOP 反推節點;兩路產物同構(帶證據的節點)=loop 階段…
    17 [FLOW]: FLOW:①寫計劃(先查圖譜三步;開審第一輪先列出主題已有的節點,避免重複開案)→②設計送審(design-loop:派工時自動把相關節點附給每個審查員[2026-09-05 起 …
    77 [body]: | ⑤ | pre-push+CI | 沒過關的東西物理上推不出去 |
  2.934  Projects/派工鏡頭注入_計劃.md  [筆記]
    49 [fm:why_chosen]: why_chosen: 藏的結果=今天沒 hook 的狀態,不比現狀差;鏡頭不是閘,漏一篇不改變任何擋不擋;修要動 scripts/lumos 且每次派工多一次 archive,成…
    67 [body]: > 白話:代碼審派審查員的時候,規矩要求把「這批改動碰到哪些帶合約或出過事故的筆記」貼進派工詞——實帳沒人做到。本案在派子代理那一刻,由 hook 把機器算好的那份清單**附**進…
    82 [body]: Enzo 裁(2026-09-03):散文審查的清單本質是鏡頭;可執行那層(合約綁測試、推送前真跑)已經存在且只有它該是閘;★不要求鏡頭證明自己有用★。
    87 [body]: - 設計迴圈審的是計劃筆記工作副本,沒有既定 git diff 範圍;r1 兩席實跑 `HEAD..HEAD` 回空。硬塞標記=標記在、鏡頭永遠不注入。
    111 [body]: 2. **清單**:`lumos impact --diff <範圍> --repo <cwd> --json`,取 `pinned: true`;★剔除 `files` 全落在 …
    112 [body]: 3. **內容來源=base ref,不是工作樹**(r1 blocker):前 8 篇貼內容,內容用 `git show <base>:<repo 相對路徑>` 讀★base 那…
    124 [body]: - 架構對齊席 §7.6「圖譜裡相關功能筆記」那格是兩種迴圈共用→改成兩支(見〈範圍〉):代碼迴圈填標記那一行、設計迴圈維持手貼。
    172 [body]: - **界線**:①鏡頭讀 base 版合約行、閘讀工作樹版節點(`Env(vault)`)——分支若改了那篇筆記的合約行,鏡頭標的狀態與閘實際跑的可能不同;鏡頭是參考,閘是判決。…
    … 還有 3 處
  2.900  Issues/lint不守驗證紀錄空回頭條件.md  [筆記]
    23 [body]: > 白話:驗證筆記的「什麼時候要回頭重驗」欄位空著,lint 不會叫——這次五篇同天全空、機械掃描全盲,是審查席抓到的。這張單子排進清債批,給 lint 加一聲警告。
  2.888  Projects/條款綁測試算進度_計劃.md  [筆記]
    12 [KEY]: KEY:題目=設計審產出的驗收條款,實作時認領→勾掉怎麼不漂;上一案 [[Projects/進度從提交推導_計劃]] 四版被打穿後的續案,地基 d3/d9/d12 不重審;Enzo…
    19 [fm]: - "[[Projects/進度從提交推導_計劃]]"
    44 [fm]: - content: 訂正 d3(code 迴圈 r1 三席):cutoff 改隔日 2026-09-09T00:00+08:00 並換算 UTC 比;跳過看迴圈類型(code- …
    56 [body]: > ★這是 [[Projects/進度從提交推導_計劃]] 四版被打穿之後、[[Projects/接手視圖_計劃]] 落地之後的續案★——
    62 [body]: 認領 = 某篇 Verification 筆記的 `plan_refs` 欄位回指本計劃、而且那篇筆記全文出現過 `[SN]` 字樣。實算:**有 `[SN]` 條款的計劃 33 …
    75 [body]: | 「完成=不跑測試,讀測試每次跑都留的快取」 | 推送閘寫的 `.lumos/test-cache-shard*.json` **只有 `{"failed": []}`**,是 …
    81 [body]: `bound-tests` 治理帳一筆記的是 **節點清單 + 「46 綠」這種計數**,★不記測試名★。
    119 [body]: 舊寫法會拿那個 commit 的綠來印,新寫法印「尚未推上主線」。
    … 還有 8 處
  2.876  Projects/code席爆炸半徑供糧_計劃.md  [筆記]
    27 [body]: - 對照:爆炸半徑的機械強點今天全掛在編排者/推送閘(hook 推合約、落成核對、綁定測試真跑、pass 前 sync-check 四條全在跑)——唯獨「席位的眼睛」這環斷糧。
    31 [body]: **B 廢**(blocker×多席):①停案判決 d2 **明文列舉並否決過**「pitfalls→loop next 改工具落點」——B 就是那個選項本人,無新論證(P-1);…
    43 [body]: - **★真隱患:impact 把審計證物當程式碼來源★**(停案筆記副產物 bug#1,擋在 B 的路上):`governance/review-reports/**` 的凍結 …
  2.865  Verification/2026-09-08_Codex席位可指定模型_兩席分流.md  [筆記]
    9 [KEY]: KEY:★推翻舊宣稱★ — code-loop reference.md 兩處寫「Codex 不能逐席指定模型」,實測是錯的:席位 TOML 的 model / model_rea…
    10 [KEY]: KEY:★怎麼驗的最重要★ — 「叫席位自報模型代號」沒用(TOML 指定 5.4-mini,它自報 GPT-6);★反證才作數★:指定一個帳號會 400 的模型(gpt-6),席…
    18 [KEY]: KEY:★同日再裁:兩席拆成三席(2026-09-08,Enzo)★ — 散文審 lumos_reviewer=terra+medium(預設)/ 程式碼審 lumos_revie…
    30 [body]: ## 推翻了什麼
    46 [body]: **③ 推理強度同樣有效,而且會驗值。**
    52 [body]: | 席位 | 模型 | 推理強度 | 什麼時候點名 |
    61 [body]: > ★這件事的教訓比設定本身重要★:**推理強度要配題目,不是越高越好。** 它的成本是牆鐘時間,
    81 [body]: 兩席的模型與推理強度要精確、名字不同但指示相同(框架單源)、teardown 兩席都收且清單照實列。
    … 還有 5 處
  2.853  Projects/接手視圖_計劃.md  [筆記]
    11 [fm]: - "[[Projects/進度從提交推導_計劃]]"
    18 [KEY]: KEY:立案(2026-09-07,Enzo 裁「先造,至少看目前情況有沒有惡化,不同步已實實在在發生」)——★不造新狀態源,只把三個既有可信來源(git 工作樹/逐字稿/計劃點名…
    22 [KEY]: KEY:★誠實天花板★只解「同一台機器、同一個 checkout」的中斷接手(逐字稿在本機);從 Claude 裡開出來的終端機不寫逐字稿(記憶有此條)→那種 session 只剩…
    86 [body]: - ★Enzo 2026-09-08 裁:收★(決策見開頭欄位)。殘餘面可接受;不再派一輪;合回主線交 Basic Optimization(合併時 `docs/.canary-l…
    89 [body]: - **現況實話**:在此之前沒有任何東西會自動叫 `lumos handoff`,只有 `lumos --help` 列著它。三層接法:①規則表讓 agent「知道有這支」②開場…
  2.830  Projects/enforcement可觀測性_計劃.md  [推]
    12 [KEY]: KEY:★這批的起點是儀表板自己在講錯話★——lumos enforcement 把 git-pre-commit/git-pre-push 都印成 inactive,而那兩道每次…
    15 [KEY]: KEY:★可跳集合被實查推翻,縮到只剩健檢一道★——CI 只有 doctor 無條件跑;pitfalls 沒有獨立步驟、code-loop 那步掛 push-only(PR 不跑)…
    52 [body]: 它們擋掉一次推送,治理帳上完全看不出來。
    59 [body]: ——而那兩道閘今天擋過我兩次、每次推送都在跑全套測試。
    133 [body]: 加上 CI 只在推主線與開 PR 時觸發,**feature 分支推上去不跑 CI**。
    136 [body]: 而推送閘自己那次獨立呼叫是 `--advisory` 加 `|| true`、**不擋**。
    147 [body]: - **風險分級與代碼審留痕**:★只在「這個 repo 目前是直推主線」這個前提下才有後盾★。
    216 [body]: 照原本寫法,lumos 自己去取 HEAD 會在「同次推多個 ref」「推的不是目前 checkout 的 ref」
    … 還有 6 處
  2.805  Projects/impact鏡頭機械化_計劃.md  [筆記]
    21 [fm:context]: context: 兩輪設計審皆未收斂且致命傷各不相同(未收斂訊號)。r1 五席 3 blocker+17 major:核心宣稱「manifest 進 materials→seat-…
    25 [fm:superseded_by]: superseded_by: ★2026-09-03 實測推翻死因,重開條件已滿足(見 [[Verification/2026-09-03_派工攔截點實測]])★:d2 的核心死因…
    32 [body]: > **★2026-09-03 更新:d2 的死因已被實測推翻,重開條件已滿足。本篇不再是「不做」的定論。★**
    38 [body]: > **但重開之前仍要正面回答兩件本篇沒被推翻的事**:
    39 [body]: > ① 2026-08-02 的獨立裁定(擋 high 抓不到 standard、擋 standard 逼人繞過)——★那條沒被推翻★。
    40 [body]: > ② 同日另一筆實測顯示,守衛常態誤擋會訓練人習慣性繞過(見 [[Issues/推新分支時風險分級拿空樹當起點]]),
    50 [body]: ## ~~★核心死因:派工那一刻沒有機械強制點★~~ ← ★2026-09-03 實測推翻,見頂部橫幅★
    56 [body]: 原文(已推翻):這是**結構性**的,不是實作沒做好:
    … 還有 7 處
  2.788  Verification/2026-08-21_doctor-run事件落地.md  [筆記]
    30 [body]: `_scaffold_project` 自 2026-06-26 把帳檔 ignore 清單寫在 `docs/<slug>-knowledge/.gitignore`,但帳檔全部落…
  2.741  Verification/2026-07-31_slim-scan掃描器落地.md  [筆記]
    62 [body]: - 系統筆記：[[Systems/slim-scan-掃描器]]
  2.711  Projects/建了沒人跑批次裁定_計劃.md  [筆記]
    46 [body]: - 復活條件(承認風險鐵則):canary 植入協議若重啟(design-loop 筆記 d5 翻案),②③ 從 git 史撿回重審;mutate 若有真消費者立案,同路徑撿回。
  2.701  Systems/check-j-regen-guard.md  [筆記]
    22 [FLOW]: FLOW:重建節點 → lumos set regen from-scratch/日期 蓋章 → summary 逐 claim 標身分([src:]/[git:]/推測:/佚失:…
    23 [KEY]: KEY:解 from-scratch 重生塌陷——重建=從 code 快照逆向工程 why,AI 會編自信假 why/假合約;Check J 逼每條 claim 亮身分:有證據(且…
    24 [KEY]: KEY:J-a 拒發明合約(regen 節點 INVARIANT 標記行需 [src:]/[git:] 意圖證據,與 Check T [test:] 疊加——test 證行為,sr…
    25 [KEY]: KEY:共用 check_regen_provenance(note,repo_root)->(errs,warns,gov_events),lint 與 doctor 同函式防兩…
    40 [body]: 重建的筆記每條 claim 被逼亮身分——「有證據（機械驗真）」「推測」「佚失」三選一；想混一句自信的鬼話（尤其假合約），機器擋。
  2.690  Verification/2026-07-31_slim-install安裝器落地.md  [筆記]
    54 [body]: - brief Step 4 敘述「9 條 check 全綠」,實測 `check()` 呼叫共 8 條(逐一核對測試原始碼確認無漏抄),推定是 brief 手數的筆誤,非測試本身…
    59 [body]: - 系統筆記:[[Systems/slim-install-安裝器]]
  2.657  Projects/修法A_lumos先行ablation_計劃.md  [筆記]
    19 [KEY]: KEY:題目集=commands.jsonl 23 題+answers.jsonl 5 題=28 題;每題每組跑 3 次(=每組 84 場);4 個沙盒平行(每組 4 shard)…
    23 [KEY]: KEY:design-loop 跳過(小改動,計劃筆記註明):儀器改動 <100 行、判準不動、Enzo 口頭核准兩組定義與題數;預註冊即本案的「退場條件在結果前寫死」
    110 [body]: ## 代碼審(2026-09-02,推送前 tier=high 三輪)
    112 [body]: 儀器這批(探針 + 跑批 + 衝突掃描 + 防線,約 760 行)推送前走 code-loop,loop id 定稿記於 `code-ablation-probe-2`(過程 r1…
  2.649  Systems/節點還原.md  [筆記]
    42 [body]: - regen 章宣告制可繞、停手線無機械檢查、reflexion 對帳靠紀律——回頭條件全記在計劃筆記實務隱患節。
    43 [body]: - 檢索稀釋觀察門檻:實跑後對既有檢索考卷跑評測,推薦精確度不得降。
  2.638  Issues/設計迴圈問閘指令與panel記帳互斥.md  [筆記]
    34 [body]: →「擋下:第 r1 輪有 5 筆記錄都帶了處置結果,一輪只能有一筆」(多席 panel 記帳型態)。改問 `--gate --panel --min-seats 3` 才通,且該閘…
  2.604  Projects/驗形式與驗內容_調研.md  [筆記]
    19 [KEY]: KEY:★歸納:存活缺口分兩族(這是我的歸納不是查到的,推翻條件見下)★——家族甲「宣稱與現實脫鉤且沒東西會發現」(checkbox 沒勾/doing 停滯/待辦零判定/提醒喊 1…
    21 [KEY]: KEY:★世界數字①引用支持力(arXiv 2605.06635,14 模型×130 題)★三層拆:連結打得開 94–100% / 內容同主題 >80% / ★來源真的支持該主張 …
    27 [KEY]: KEY:★★抽驗做完了,而且測不成——樣本是零(2026-09-07 同日)★★:機械解析(不是數字串)後,全圖真實 `[src:]` 引用 **0 個**、`[git:]` 引用…
    30 [KEY]: KEY:★連帶:9/3「本地證據」重新解讀★——那條被撤掉的約束**理由寫得很清楚**(原話「這是硬約束不是提醒」),理由在還是被撤、同日兩次。★病根是「有理由但沒人讀」不是「沒有…
    31 [KEY]: KEY:★沒查的★——沒復現任何一篇(數字全來自論文自報,且只讀結果與限制段);★本 repo 那 38 處 `[src:]` 裡有幾處指到不相干的行仍然沒人查過,那個數字才決定要…
    36 [fm:why_chosen]: why_chosen: 本 repo 的不對稱接線(推測行不得掛合約標記)是硬約束、[src:] 是外部接地而非內容篩檢,正好落在兩篇論文說有效的那一邊;方向對就不要因為外部報告的…
    45 [fm]: - content: 抽驗宣告 n=0:兩族歸納在本 repo 既未被驗證也未被推翻,不得拿抽驗結果當佐證
    47 [fm:context]: context: 原本設計的推翻條件是「抽驗 38 處來源標記,若幾乎每處都真支持其主張則整篇作廢」。機械解析後發現真實引用 0 處,全部是格式範本/刻意反例/安全測試字串
    … 還有 11 處
  2.598  Verification/2026-08-23_about_code存量雙評審落地.md  [筆記]
    16 [body]: > 白話:83 篇固定席範圍的筆記,現在每篇 frontmatter 都有 `about_code`(它主要在講哪幾支程式檔)。
  2.596  Projects/一句話層供糧_計劃.md  [筆記]
    38 [body]: - ~~`context --brief` 順修~~(**r1 否決撤出,C-3/E-4**):原 spec 授「席位判出反例可否決此子項」,消費席拿到反例——全庫扇出最高 hub…
    55 [body]: - **誤導實例帳(P-6 折入,接電)**:發現「一句話比沒有更誤導」的實例,當場在本筆記〈誤導實例帳〉節 append 一行 `★L0誤導★YYYY-MM-DD <節點名> <…
    56 [body]: - REVISIT:2026-09-20 grep 本筆記 ★L0誤導★ 數誤導帳+重跑入口栓重放看 L0 實際覆蓋(做完 bump 或關案)
  2.594  Verification/2026-08-22_狀態表過期偵測.md  [筆記]
    14 [body]: > 白話:一篇筆記用表格記進度,某一格寫著「待辦」,但那格連到的節點早就做完了。
  2.592  Projects/連鎖佇列軟提醒_計劃.md  [筆記]
    30 [body]: - **d3 訊息照工具輸出三段式**:發生什麼(N 張連鎖待辦單自建立後零筆判定,最老 X 天)→為何在意(被翻案決策的引用筆記沒人回頭判,世界對照=94.6% 的撤稿引用不承認…
    40 [body]: 4. [T3] Issue [[Issues/連鎖佇列開了沒人跟完]] 結案橫幅(修法 A/B/C 已裁採納、D 另議留言)+本計劃雙向連;Systems 側 KEY 寫回(關係層…
    68 [body]: ✅ r1 已審畢折入(本版=v2)。續:d5 型態記帳→問處置閘(單輪全處置即收斂)→過閘→[T1]/[T1b]/[T2]/[T3]/[T4] 實作→code-loop→推送;設計…
  2.589  Projects/code側刪除傳播守衛_計劃.md  [筆記]
    20 [KEY]: KEY:★真實失守實錄(mOrangePos commit aff2329,2026-08-03)★—該 commit 移除登入自動撈 2C2P 憑證。它**有**帶圖譜更新、五個…
    24 [KEY]: KEY:★天花板(誠實講)★—只抓「符號消失」這一型。行為反轉但名字沒少(例:`isStock = if(isSend=="Y") prefs.isStock else false…
    27 [KEY]: KEY:★與 Swimm 的刻意偏離★—Swimm 要求文件明確嵌入 code 錨點(Smart Tokens)才能耦合,精度高但有撰寫成本;本設計改用**識別字字面 grep**…
    43 [fm]: 軟提醒可以被無視，本次失守正是「被推播了仍只掛連結」。故 advisory 版必須配 S3 的問句紀律
    55 [fm]: impact hook 在編輯當下的即時推播不帶本守衛訊號;接受——刪除在編輯當下未必成形,commit 時點才是刪除的定案點。
    74 [body]: 新增一條連結、寫一篇新的 Verification，都算「有更新」；而把被推翻的那句話改掉，沒有任何機制在要求。於是新東西一直長，舊東西一直爛。
    87 [body]: **只掛了連結。** 被推翻的那段「登入 setEmpFlag 時 GetPaywayCredential 對 51/52 各撈一次」原封不動躺在新連結旁邊。
    149 [body]: 但泛問會失效——本次那六個節點大概率都被 `impact` hook 推播過，結果仍是掛連結了事。**問題不在有沒有問，在問得夠不夠具體**：泛問可以在腦內三秒答完，指著某一行問「…
    … 還有 3 處
  2.564  Verification/2026-07-31_接手者演練複審修復.md  [筆記]
    43 [body]: - 系統筆記:[[Systems/slim-readme]]、[[Systems/slim-skill-修剪]](本次改動的兩份文件所屬節點)
  2.553  Verification/2026-07-31_slim-gen生成器落地.md  [筆記]
    81 [body]: - 系統筆記:[[Systems/slim-gen-生成器]]
  2.535  Verification/2026-08-24_固定席降噪A層落地.md  [筆記]
    25 [body]: > 白話:改程式時 hook 推的「必看」清單,一半以上是掛著「守衛面」軟標記、跟誰都隔一跳的樞紐筆記。
    27 [body]: > 結果:沒見過的那半考卷上,噪音砍一半、人先看到的三行必看率翻四倍、該推的一篇沒少。
    35 [body]: | 必看推出(all) | 66/70 | 66/70(棘輪綠) |
  2.530  Verification/2026-07-31_slim-claude-md注入.md  [筆記]
    22 [body]: 驗證對象:[[Projects/公開精簡版_實作計畫]] Task 8 —— 推翻 [S3] 原裁定「不注入/更新任何 CLAUDE.md」,改為 append-only 附加圖譜…
    50 [body]: - 最初嘗試用「依既有內容結尾自動判斷分隔符」(0/1/2 個換行三種情況)的寫法,推導卸載時要精確逆算分隔符長度過於脆弱;改用「固定分隔符恆為一個 `\n`」的規則後,插入與移除…
    56 [body]: - 系統筆記:[[Systems/slim-install-安裝器]]、[[Systems/slim-uninstall-一行卸載]]、[[Systems/slim-readme]…
  2.523  Systems/hook信任邊界.md  [筆記]
    65 [body]: 的程式的一部分。★2026-09-08 漏這一條當場擋住推送★——而錨點那道永遠不可跳。
    107 [body]: 影響鏡頭把牽連的筆記整理成一段文字,**以「系統附加」的口吻直接進主對話**。原本它會把圖譜裡的自由文字逐字印出來——觸發字串與合約整行。也就是說,**任何能寫進圖譜筆記的人,就能…
    113 [body]: ★做的時候踩到一個★:我只框了一條渲染路徑,**同一支 hook 的另一條路徑漏了框**,是全套翻紅才發現(那條測試走的正是漏掉的那條)。只跑關鍵字子集的話這個漏就會推上去。
  2.495  Verification/2026-09-11_每支檔有家落地.md  [筆記]
    5 [fm:valid_under]: valid_under: "scripts/lumos 的每支檔有家那一段、提交前與推送前掛鉤的 Gate H 與整段比、健檢 S8–S10 照本篇描述的樣子;在本工具鏈的工作目錄…
    6 [fm:revalidate_when]: revalidate_when: "改到 _nodehome_ 開頭的函式、cmd_home_check、提交前或推送前掛鉤裡每支檔有家那一段、about_code 的寫入檢查、測…
    22 [body]: - **代碼審第一輪的修正**：改行為的 10 條都先寫測試、修前翻紅再修；另外補測試（事故筆記帶 --code，實作本來就對）、測試改名、改說明（複製出來的檔那條，另釘一支測試，…
    24 [body]: - **殺傷力**：51 種故意把程式改壞的寫法（先 19、再 6、4、6、13+2，最後推送前逐提交看那 1 種；照七份突變清單機械數）逐一跑對應測試，全部被抓到——第二輪有兩種…
    25 [body]: - **速度**（本工具鏈 65 篇節點，2026-09-11 量）：`lumos home check --staged` 0.65 秒；`--diff` 1 個提交 0.75 …
    27 [body]: - **既有測試的調整**：推送前不再呼叫以反引號為種子的點名（原本那支測試改成斷言不呼叫）；提交前「格式乾淨的節點要放行」那支在測試專案裡關掉新檢查（它只驗格式那道）；提交前同步…
    28 [body]: - **第一次在消費專案真的推送**（2026-09-11，三個 POS 專案依序更新、整理、落外帶）：客人網頁與後端推送前檢查都「新違規 0 條」；平板那次被擋，查出是逐提交看寫…
    29 [body]: - **第一次真的提交與推送**（2026-09-11，推上遠端 3a59166c）：提交前那道在帳本提交時跑了，治理帳記「這次提交：新違規 0 條」；推送前那道把要推的範圍整段比…
  2.493  Verification/2026-08-27_辯方表態記帳.md  [筆記]
    29 [body]: - **單元測** `t_refute_verdict_ledger_and_stats`(`scripts/test_lumos.py`,綁基準線需 anchor approve…
  2.491  Projects/design-loop判準重定位.md  [筆記]
    27 [KEY]: KEY:★r1(tier=high 5席 panel)輪無效:1 caught/4 missed★——而根因是★抑噪紀律與 canary 互斥★:派工寫「低嚴重度、給不出失敗場景就…
    30 [fm:PRIOR-ART]: PRIOR-ART:★①原答「不造新機制」是錯的(r1 查證推翻)★——M2 cluster 帳已是幾乎等價的處置帳:`CLUSTER_STATES=(resolved,accep…
    45 [fm]: - content: 2026-08-04 本案併入 [[Projects/design-loop重設計]],不再獨立推進;d1/d2 沿用進該案,其餘以該案為準
    101 [body]: - **`findings` 的單位是「條」，`184` 的單位是「筆記錄」**。一輪 panel 有 W 席＝W 筆記錄，
    258 [body]: 需要一條機械檢查——候選：**`--disposal` 要求該 loop 的判定輪每筆記錄都帶
    322 [body]: | 2 | 第二節表格的 `n`（34/27/24）與「38 個 loop」對不上，且 `findings` 中位數 × n ≠ 184 | 補「三個單位別混」段：`n`＝有跑到該…
    407 [body]: ### 推論（要寫進 skill）
    425 [body]: > 樣本極小、不足以定論，但方向與上述推論一致。
  2.480  Verification/2026-08-27_decision_refs養成T3v4落地.md  [筆記]
    30 [body]: - ★覆蓋窄★:backlog 164 節點/985 未填槽,但大多是 related 邊的結構巧合(某筆記剛好連到有決策節點,非真背書)。真回填要逐節點讀內容判,判錯=往圖譜塞假…
  2.477  Systems/autonomous-iteration-loop.md  [筆記]
    27 [KEY]: KEY:全自動判收斂仍是沒閉合的迴歸——judge/cross-family 只把自評推遠一層未消滅,末端人 review PR 是最後也唯一真兜底(誠實天花板)
    33 [KEY]: KEY:紀律抗壓縮(Governance Decay arXiv 2606.22528,2026-07-26 對帳)=長跑對話的摘要壓縮會悄悄刪安全規矩(違規率 0→65-95%)…
    36 [KEY]: KEY:★2026-09-06 訂正暫停開關的位置★:09-05 那版把 LUMOS_AUTOLOOP_OFF 寫在 daily-governance.sh 裡包住整支 auton…
    56 [fm:why_chosen]: why_chosen: 把「收斂了沒」從被審者手裡移到獨立 judge,斷開自填閘;但這只把最弱環推進一層未消滅(judge 集中掌 caught+severity、只讀 audi…
    145 [body]: 1. **末端人 review PR 是全鏈唯一外部錨點、最後真兜底**。全自動判收斂仍是沒閉合的迴歸:judge-severity-gate 把「收斂自填」推進一層未消滅(jud…
    177 [body]: ### 2026-09-07 修掉的三個洞(每一個都實測重現過,不是靠「同型」推論)
    240 [body]: 把後者寫成前者的結論,是同一天第七次「把自己的推論寫成查過的事實」
    241 [body]: (見 [[Issues/把自己的推論寫成repo明文寫過]])。
    … 還有 1 處
  2.469  Verification/2026-07-31_公開精簡版終審修復.md  [筆記]
    47 [body]: - 系統筆記:[[Systems/slim-scan-掃描器]](C1 直接改動的系統)
  2.376  Projects/Codex完全支援_計劃.md  [筆記]
    72 [body]: > 白話:現在 lumos 的「防護」全掛在 Claude Code 上——進 session 時有人提醒你去查圖譜、改檔前有人把相關合約推到眼前、派審查員時有人把清單附進派工詞、…
    102 [body]: 3. 分開驗 matcher `spawn_agent` 與 `collaborationspawn_agent` 哪個命中(實驗 B 兩條並列只記到一筆,未分開;S1 表「攔得到…
    131 [body]: - **外家席相對化(整合 F3/通才 F3 blocker)**:`loop next` 首輪必帶 `--orchestrator claude|codex`(比照 `--tie…
    209 [body]: - **驗收**:[[Verification/2026-09-04_Codex完全支援S1hook適配驗收]]——隔離 clone+CODEX_HOME 真跑 codex exe…
    210 [body]: - **代碼審 r1(code-codex-s1,standard:單reviewer+架構+外家 Codex,2026-09-04)**:14 條(5+3+6,4 條兩席重疊)全…
    223 [body]: ## 實作紀錄 S3(2026-09-04,S2 代碼審過閘、8 個 commit 推上遠端後動工)
    235 [body]: f01/f02 兩個功能實驗跑完後的精修另開 [[Projects/Codex行為精修_計劃]]:Codex 收工 Stop hook 在「改了碼、筆記沒動」時擋一次讓模型續做補筆…
    240 [body]: - 驗收:隔離 CODEX_HOME 跑 `lumos install` 寫出 TOML,用暫存的 0.153.2 派 `lumos_reviewer` → SubagentSta…
  2.361  Projects/消費專案接入靜默失效_計劃.md  [筆記]
    26 [KEY]: KEY:②合約測試閘零支假綠(見上)——★折法在代碼審 r1 被實測推翻並整條換掉★:原折法(拿不存在的測試名跑一次看回不回 0)前提是「測試工具分得出測試不存在」,實測 dotn…
    27 [KEY]: KEY:★r2 再打掉一次:「擋」跟「講」是兩個地方★——判定那支已經把「證不出跑過」併進擋的條件,但真正把訊息印給人看的推送關卡那支只認 green/red,於是★低風險推送在假…
    76 [body]: **特別值得記的一件事**：我為了確認符號檢查有沒有作用，在筆記裡塞一個不存在的方法名做翻紅測試，結果沒翻紅、一度以為機制壞了。查下去發現是**測試自己寫壞**——那句話裡有「不存…
    84 [body]: - **[E] 零覆蓋時講原因**：三種來源分別出聲（沒有節點引用／有節點沒綁測試／知識庫找不到）。**訊息要帶既有關鍵字，否則會被推送前的過濾器吞掉**；而且要在推送那條路上真的…
    90 [body]: - [S1] `lumos init` 在沒有既有設定的專案產出 `.lumos/config.json` 骨架：單語言依偵測結果、多語言用多平台格式、偵測不到寫帶說明的骨架；**…
    93 [body]: - [S4] 合約測試閘零覆蓋時依三種來源分別印原因，**且在 `code-loop check` 與推送前腳本那條路上真的顯示得出來**（訊息含既有過濾關鍵字）；既有的綠／紅／跳…
    101 [body]: - [S13] **推送關卡那支要把「證不出跑過」講出來**：低風險只提醒也必須出聲、擋下時要給得出逃生指令與後果 [test:t_code_loop_check_speaks_a…
    118 [body]: - **[A] 偵測會猜錯**：多語言 repo 走多平台格式仍要挑預設平台，可能挑錯。骨架標示「推測」而非斷言。
    … 還有 4 處
  2.354  Issues/測試未隔離HOME刪掉真機Claude-hooks.md  [筆記]
    74 [body]: **同一句教訓寫在筆記裡三次,還是照樣發生第三次。** 這就是「承認風險而沒有機械守衛」的實際代價。
  2.352  Projects/標註刷新_計劃.md  [筆記]
    13 [KEY]: KEY:PRIOR-ART: borrow-design——IR 評測經典解 TREC pooling/incremental qrels:新系統/新語料浮出未判文件→只補判那批(…
    39 [body]: > 白話:我們有一份考自己搜尋功能的考卷,答案是人批過的金標。但筆記庫一直長大,新筆記沒批過答案,照「沒批=算錯」的規則,筆記庫一更新分數就崩——上次崩過一次只好把考卷凍在舊庫上。…
    199 [body]: ★誠實★:「A 席偏嚴」是推論不是定論;另一解是兩個 B 席共有 LLM 評審的寬鬆偏誤
  2.343  Projects/lint接線收口_計劃.md  [筆記]
    34 [body]: - 誠實邊界:本案接線只惠及活通路消費端;KDS 凍結通路的 lint 健康=其自身責任(分家裁定的自然推論),不在此假裝覆蓋。
    44 [body]: - [LINT]→[L2] 段名(arch-f2);編排者自首:動筆前沒查圖譜漏掉現成合約筆記,intake 有檔。
  2.324  Verification/2026-07-31_公開精簡版代碼審第二輪minor修復.md  [筆記]
    84 [body]: - 系統筆記:[[Systems/slim-scan-掃描器]]、[[Systems/slim-uninstall-一行卸載]]
  2.276  Projects/工具鏈全環節體檢_調研.md  [筆記]
    49 [body]: 10. **doctor 每次印幾十行軟提醒([P]19 行/[Y]6 行/[V]/[N]),全是歷史或自指噪音**:處置=預設只印 hard + 有變化的 soft;全文改 `-…
  2.264  Verification/2026-08-22_指令索引與情境探針.md  [筆記]
    26 [body]: - 第一輪 15/20;5 個沒過裡 3 個是儀器問題(副本用 git clone 只帶已 commit 的東西,剛寫的筆記不在,Claude 真的找不到才退到 grep)→ 儀器…
    38 [body]: `governance/scenarios/paraphrase.jsonl` 12 題,全部口語、不出現「圖譜 / lumos / 驗證紀錄」字眼,例:「欸 pre-push 怎…
  2.244  Issues/同工作區多session並行改動.md  [筆記]
    17 [KEY]: KEY:★我在寫這篇時自己又犯一次同型★——第一版寫「(d) 是唯一能處理瞬時壞檔的做法」,被另一個 session 更正、查證後確認我錯;而那句話寫下去的時間距離我寫完 [[Is…
    64 [body]: - **hook 推的必看合約**:推的是「你碰的檔關聯到哪些筆記」,不是「這個檔另一個 session 也在碰」。
    147 [body]: 它的射程是**筆記的開頭欄位**:會去 parse frontmatter、確認要寫的欄位值真的寫進去了、
    163 [body]: [[Issues/把自己的推論寫成repo明文寫過]](內容就是「我把沒查過的東西寫成肯定句」)不到一小時。
    214 [body]: ## 第五次(2026-09-08):新型——**我 `git add` 了不屬於我的改動,推上主線變成自相矛盾**
    223 [body]: 於是他們的測試改動跟我的一起被提交、一起推上遠端。
    227 [body]: 本機推送閘沒擋住,因為本機工作樹裡「實作」也在,兩邊剛好對得上。
    232 [body]: 沒想到「我推上去的內容」跟「我本機跑的內容」不是同一個東西。
    … 還有 2 處
  2.205  Systems/slim-uninstall-一行卸載.md  [筆記]
    19 [★INVARIANT★]: KEY:★INVARIANT★ `~/.claude/skills/lumos-project-notes/` 移除前必先備份成 `.bak.<timestamp>`,不得 `rm…
    62 [body]: > **仍在 repo 裡、測試仍在跑**，但★不再發布★——沒有自動發布路徑，人工推送也已停。
  2.199  Projects/lumos-show讀取入口_計劃.md  [筆記]
    73 [body]: 2. 找不到 → stderr 含「找不到筆記」、rc2。
  2.164  Systems/hook逾時預算.md  [筆記]
    68 [body]: 架構席引的裁定是「hook 只做三件事,其餘全部住 lumos 子命令」。**而我自己在計劃筆記裡寫了兩次「邏輯放 lumos 端、hook 維持薄殼(既有裁定)」,然後把子行程監…
    92 [body]: ### 五、★席位的觀察對、推論的判準錯,要分開看★
  2.124  Projects/loop數據收集_計劃.md  [筆記]
    37 [fm]: - content: 飛輪量測雙帳落地(Enzo 2026-08-31 裁做):①攔截帳=★圖譜攔截★零工具記號慣例+種子三筆回填 ②逃逸帳=loop escape 原語(M1②,…
    82 [body]: **縮案交付(外家反提案,便宜且直接;✅ 2026-08-30 當日交付=[[Verification/2026-08-30_席報告圖譜使用一次性盤點]])**:後桶樣本才二十來份…
    107 [body]: append-only 落 `docs/.escape-log.jsonl`(★code-r1 折入:寫入走 canary 家族的落盤自驗原語非裸 append;帳檔進簿記白名單防…
    117 [body]: **B(使用率 held 池)死**:★圖譜攔截★站:首輪;源:[[Projects/loop數據收集_計劃]] 自身 d2 重開條件——B 是昨天判死的常設指標換包裝復活,三重開…
  2.123  Projects/工具分類_計劃.md  [筆記]
    34 [body]: > 白話：這個工具鏈長到六十多個指令、六十多個機制，之前的整理方式都是「按動詞」（讀／寫／巡檢）或「按你正在做什麼」（進場／動手前／寫回…）。Enzo 要的是第三種軸——**按研究…
    41 [body]: | 2 | `scope/retrieval` | 節點檢索與推薦 | 給一個任務，哪些節點該浮上來、排序對不對 | 全文搜尋與排序、多詞回退、改檔前推節點的 hook、波及範圍算…
    87 [body]: - **不進檢索排序、不進 hook 注入**（見 summary 第三條）。理由是 2026-08-05 的 A3 消融：高連結、高分類的節點是導覽樞紐不是答案，拿分類加權會把樞…
  2.091  Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復.md  [筆記]
    151 [body]: - 系統筆記:[[Systems/slim-get-一行安裝]]、[[Systems/slim-uninstall-一行卸載]]、[[Systems/slim-install-安裝…
  2.073  Verification/2026-07-31_公開精簡版交付.md  [筆記]
    156 [body]: spec 放行時未結清的 10 條(`S1-2` `S1-3` `S1-4` `S1-5` `S1-6` `S1-7` `S2-1` `S2-2` `S2-3` `S6-3`,原皆…
    167 [body]: 其餘 4 條(`S1-3` 生命週期整族必砍的反事實、`S1-4` anchor 該砍的安全理由、`S1-6` rel-cascade 保留是產品裁定非程式依賴、`S1-7` 函式…
    177 [body]: - 系統筆記:[[Systems/slim-scan-掃描器]]、[[Systems/slim-gen-生成器]]、[[Systems/slim-install-安裝器]]、[[S…
  2.046  Systems/finding-refute.md  [筆記]
    19 [KEY]: KEY:辯方效力來源是「任務方向相反」(被逼構造推翻證據、查 auditor 跳過的反方向),非「更會看 code」;故 1 個辯方+強制 file:line 即可,不 N 個多數…
    41 [fm:why_chosen]: why_chosen: auditor 找洞(看到可疑就提、無動力深挖反證),辯方被逼構造推翻證據(專查 auditor 跳過的反方向);同樣 grep、目標命題相反→挖的角落不同…
    50 [fm]: - content: 辯方表態的記帳一致性檢查在 blocker 輪讓步(2026-08-29 修回歸):同輪 severity=blocker 時,舊規則強制放行清單為空、而反證…
    95 [body]: ★blocker 輪讓步(2026-08-29,d5)★:同輪 severity=blocker 時,舊規則強制放行清單必須是空的,而反證推翻的發現照規矩「不折入」——兩條一夾使 …
  2.013  Systems/lumos-cli-read.md  [筆記]
    15 [KEY]: KEY:[2026-09-07 handoff]新讀原語 `lumos handoff <計劃節點>`——唯讀接手視圖:計劃點名的程式檔各是什麼 git 狀態(status --p…
    27 [KEY]: KEY:doctor 是全圖權威巡檢(4 檢查 orphans/unresolved/verified_by 雙向(stale/fail 驗證豁免——E1 拔死背書後不反咬漏寫)/…
    33 [KEY]: KEY:真遺忘只做 search 這一刀(2026-07-24 使用者裁定);context 基本鄰居/推薦、impact、doctor 對作廢驗證的不一致=已知殘留(impact…
    79 [fm]: - "[[Verification/2026-07-14_relguard_E2建在被推翻決策上]]"
    113 [★INVARIANT★]: - `doctor [--ci]`(`run_doctor`,非 cmd_ 前綴——L4 審計 2026-07-24 修正指針):全圖權威健康巡檢——基礎 4 檢查(orphans…
    121 [body]: - `decisions [節點] [--superseded]`(`cmd_decisions`):讀單篇 ADR 決策;`--superseded` 全 vault 掃 `va…
    159 [body]: **最後那個最危險**:它看起來像查過了、結論是沒有相關筆記——而它根本沒有圖譜可查。**這兩件事差很多**:一個是還沒建圖譜,一個是真的沒關聯。
  2.011  Verification/2026-09-07_loop-list開著的迴圈.md  [筆記]
    105 [body]: 正解是讓那支指令收一個 `--loop` 參數把編號寫進 `nodes`,那要動到推送閘的路徑,掛回頭條件。
    107 [body]: (`code-234` 唯一那筆記錄比過閘晚 8 分鐘、`code-kill` 晚 14 分鐘),原本的判定把它們算成「又開新輪」。
  2.001  Systems/授權與歸屬.md  [筆記]
    55 [body]: - **明講「工具寫進你專案的東西是你的」**:設定檔裡的紀律區塊、使用者寫的圖譜筆記,Lumos 不主張任何權利。這句在 LICENSE、兩份 README、上手指南都有。
    68 [body]: - ★這份內層清單是從套件相依關係推出來的,沒有逐段讀那 1.29MB 壓縮碼確認★。REVISIT:2026-12-06 若升級 3d-force-graph 版本,用會產授權清…
    86 [body]: - **3d-force-graph 內層清單是從相依關係推的**,沒有逐段讀那 1.29MB 壓縮碼。REVISIT:2026-12-06 若升級版本,用會產授權清單的工具重跑核…
    90 [body]: 派了一個沒有脈絡的審計員,要求它**實際構造破壞**而不是推論。它判 fail,列出三條實測成立的假綠管道,全部折入:
  1.991  Verification/2026-08-21_工具鏈體檢修復批.md  [筆記]
    66 [body]: - 本機模擬:對最近一次 push 範圍 rc0(留痕有效+簿記豁免);移走 marker → rc1;★且發現本批 #10 的非簿記 commit 已把先前 pass 作廢(rc…
    73 [body]: - 第二批(doctor/lint/寫入指令):doctor 24 段標題全改人話、`[X]` 代碼保留(測試拿它切段);56 條段內 ✓/⚠ 表頭與建議句;`cmd_lint` …
    80 [body]: 白話化批次推上去,CI 的 code-loop 閘紅了:「tier=high 無留痕」。本機 pre-push 明明過。原因:留痕檔在 `governance/code-loop/…
  1.990  Projects/合約測試閘什麼時候跑_計劃.md  [筆記]
    11 [fm]: - "[[Issues/合約測試閘只在高風險推送跑]]"
    14 [KEY]: KEY:問題=一道「改到硬合約就跑那些合約綁的測試」的閘,宣稱每次推送都跑、實作只在高風險分支跑;可數事實在 [[Issues/合約測試閘只在高風險推送跑]];盤點出處 [[Pro…
    15 [KEY]: KEY:★人裁(2026-09-07 Enzo)★=低風險推送照樣跑合約測試、紅了印出來記帳但★不擋★;高風險照舊擋。不選「低風險也擋」的理由=擋下去最可能是人改走零留痕的 --n…
    16 [KEY]: KEY:★r1 拿來否決原設計的那條裁定本身已作廢★——2026-08-02 裁「不准把波及計算掛進推送熱路徑」,但同篇 08-22 補記那條已作廢,因為推送關卡本來就無條件對每次…
    18 [KEY]: KEY:S1 順序=①有沒有宣告測試怎麼跑(免費;消費端實測 5/5 停這)②圖譜有沒有硬合約綁測試(0.001s)③★拿推送關卡已經算好的那份波及結果,不另外算★④跑測試:低風險…
    19 [KEY]: KEY:S2 拆扁平頂層指令 lumos bound-tests(不包子動詞)回三態+advisory 旗標;S3 首推改用主線 tip 當起點(不用空樹,免得跑滿全部);S4 不…
    28 [body]: 診斷與可數事實在 [[Issues/合約測試閘只在高風險推送跑]];這一篇只講怎麼修。
    33 [body]: **低風險推送照樣把合約測試跑一遍,紅了印出來、記帳,但不擋推送;高風險照舊擋。**
    … 還有 40 處
  1.962  Projects/第二輪審視六修_計劃.md  [筆記]
    58 [body]: - **稽核員對、我上一輪判錯的兩件**:①今天 09:30 的 wrapper 真的死了——不是暫停沒兌現,是我在自主迴圈那段還在跑(09:37–12:42)時改了 daily-…
  1.940  Projects/skills提示工程優化_調研.md  [筆記]
    4 [KEY]: KEY:影片說的幾處(別教推理、CLAUDE.md 別堆防禦規則、自主權與停止條件、漸進揭露)我們七月已照官方瘦過或本來就沒有;真正的空間=審查派工詞「先過濾再報」兩句(Sonne…
    23 [body]: > 白話:使用者 2026-09-11 貼了一段影片摘要——新一代 Claude 不需要「一步步思考」這類教推理的話、CLAUDE.md 堆太多防禦性規則反而讓它過度泛化、要給明確…
    32 [body]: | CLAUDE.md 堆防禦性規則會反噬 | ETH 研究:規則檔讓成本多兩成以上、成功率沒有普遍提升,規則本身會被遵守,只對「專案特有的做法」有用;因子實驗:檔案大小、位置、拆…
    33 [body]: | 明確自主權與停止條件 | Opus 5 官方給了一段「照原範圍交付、例行判斷自己做、不可逆才問」的範本 | 執行環境的系統提示已有同義規則;CLAUDE.md「沒叫推就不推」;…
    37 [body]: | 輸出偏長要明講 | Opus 5 官方:對話回覆與寫進磁碟的文件都比前代長,調思考強度改不了長度,要直接寫長度指示 | 對話有白話條列的輸出風格;筆記有「沒脈絡的人讀得懂」 |…
    56 [body]: - 自家實測:這條就是在 Opus 5 上立的(2026-08-22),當天情境探針做過正反對照——規則在,那題答對(262.8 秒);拿掉,那題答錯(74.7 秒)(見 [[Ve…
  1.925  Projects/edit面查詢品質閘_計劃.md  [筆記]
    23 [body]: > 白話:改檔案時系統拿「這次改了什麼文字」去比對筆記找相關的。但有些改動的文字只是 `#!/usr/bin/env python3` 這種檔頭,拿去比對等於拿雜訊當線索——比出來…
    81 [body]: - **pre-flight(2026-08-18,機械排乾,不算 loop findings)**:①MINLEN=0 逃生門自相矛盾(shebang 分支不受旋鈕管)→ 定案 …
  1.898  Verification/2026-08-22_缺席推論探針題組.md  [筆記]
    14 [body]: # 2026-08-22_缺席推論探針題組
    81 [body]: 而假紅的下一步永遠是有人把它關掉——同 `LUMOS_TEST_TIMEOUT` 校準那次的推論。
    137 [body]: ——**我在設計「測缺席推論」的題目時,自己犯了缺席推論。題組上線第一天抓到出題者本人。**
    141 [body]: ★`answer_expect` 要由「實跑出來的好答案」反推,不能由出題者查一次就定。★
    145 [body]: 再從對的那份反推判定字。L03 已照此修正並在題目裡留 `note` 記明原委。
    189 [body]: 理論上無影響——但這是推論不是實測。**重驗條件:下次週跑若既有題庫出現新的紅,
    192 [body]: - **a04 的答案會隨圖譜長大而失效**——哪天真的寫了資料庫遷移的筆記,這題就該換題材。
  1.825  Projects/檢索PPR邊權_計劃.md  [筆記]
    17 [KEY]: KEY:[r1 樞紐重定向]目標面=**edit(impact hook 推薦)**非 related——r1 light 審出考卷實況:goldset 無 related 人工分…
    18 [KEY]: KEY:v1 範圍刀[r1 反轉]——只動 edit/hook 面推薦;search 與 related 面不動(related 的人工分卷不存在,建卷=另立計劃的標註工程);不新…
    31 [body]: - [S1] **PPR 啟用**：`_graph_pagerank(env, personalization={seed: 1.0})`——teleport 改種子向量（dang…
    33 [body]: - [S3] **融合與消融（edit 面）**：hook/impact 推薦排序新增 P 分量——種子=**該檔 reverse-lookup 的 direct 節點集**（r2…
  1.793  Projects/panel收斂判準改革_計劃.md  [筆記]
    19 [KEY]: KEY:★立案動機(r1 措辭校正)★——panel 是風險最高路徑(tier=high 專用)卻配最鬆判準(一個乾淨輪即收斂 K=1);convergence-evidence-…
    24 [KEY]: KEY:✅★設計審收斂(2026-08-05,新制處置閘 r1+r2)★——r1 W5(15 組全折,carrier 引句 1 miss 被閘正確咬住)→r2 delta 確認(抓…
    25 [KEY]: KEY:★r1 收斂傾向★——主推 (a)+(e') 組合:K=2 治單輪反彈、(e') 治 K=2 也擋不住的尾部+右截尾盲區;(b)(c)(d) 各有結構性否決
    36 [body]: 本計劃之 A 案收斂制(K=2+決定性抽查)與**防浮動條款**(「落地後不得論證型翻案;唯一通道=20 筆抽查帳」)已由 Enzo 具名推翻——見 [[Projects/驗證層去…
    59 [body]: 5. 舊帳相容：新判準**不回溯**——以「loop 首筆記錄日期 ≥ 落地日」定錨適用（借 T6 定錨慣例；s4-F6）；進行中 loop 沿舊判準收尾。
  1.735  Projects/嚴重度綁定機械掃_計劃.md  [筆記]
    31 [body]: - **[S3] 併入 --disposal 尾端(異常才發聲)**:問閘收尾對判定輪逐席跑 [S2],比照 roster 尾端(try/except 降級、__seqN 合成鍵跳…
    33 [body]: - 邊界:寫側新增「入帳前置驗證」(★推翻原「不動記帳寫側」邊界——r1 外家否決層次倒置成立★),但不動 severity 值域白名單、不動閘判定布林;生效日邊界★歸讀側 [S2…
    49 [body]: - ext-f1+ext-f3(2 blocker:「parse 不到=不紅」是明文設計的逃逸門+層次倒置,寫側才是該擋的入口)→ 整案反轉:[S1] 改為 record 寫側硬擋…
  1.615  Projects/hook必看召回修復_計劃.md  [筆記]
    28 [body]: | ①直連被閾砍 | 6 | 反查 direct 有中;direct 基底 0.30+L(delta code 字串 vs 中文筆記詞彙相似≈0)<動態閾(現行係數 `LUMOS_…
    62 [body]: - **pre-flight(2026-08-07,機械排乾,不算 loop findings)**:①動態閾數字勘誤——當時記「0.55 是 E14 當場閾值」,現行係數實為 0…
  1.559  Projects/圖譜進迴圈入口栓_計劃.md  [筆記]
    11 [fm]: - content: v3 落地:A/B 兩 advisory 依兩輪五席審後規格實作;OR 候選收集不重構 cmd_search、以共用底層原語(_search_visible_…
    57 [body]: - **效能**:★code-r1 資源席 R-1 訂正:原寫「0.6s」是前掃量 cmd_search 的數字誤植——advisory 管線本身 pre/post 對照實測,38…
  1.540  Projects/世界repo掃描2026-09-02_調研.md  [筆記]
    76 [body]: - **C1 AI 產出存活率(委派落差代理指標)**。世界三種定義:Cursor Insights「share of accepted AI lines still presen…
    101 [body]: - RepoComplianceBench(arXiv 2607.26819):agent「almost never proactively retrieve the contri…
    121 [body]: 3. **題庫缺口(今日發現)照 benchmark 出法補**:答案只在開頭欄位合約/決策行的題;沙盒放作廢筆記當誘餌、看引不引(grep 不濾作廢,lumos 會);關鍵字不獨…
  1.519  Projects/關係層傳播守衛_計劃.md  [筆記]
    13 [KEY]: KEY:治病=lumos驗證火力全在「節點層」(合約綁測試/乾淨審),關係層(邊)只查存在/斷不斷(Check3/4/P)、不查「還對不對」;頭號腐爛(交叉審計實測)=決策別篇推翻…
    31 [fm:context]: context: lumos驗證全在節點層,關係層邊只查存在/斷不斷、不查還對不對;交叉審計實測頭號腐爛=決策別篇推翻本篇沒跟上,hooks抓不到只 AI掃得出;pre-commi…
    37 [fm:context]: context: round-1 panel跨家族Codex以scripts/lumos行號釘出PRIOR-ART事實錯誤:_reco_scores是推薦排序器非傳播引擎、deci…
    50 [fm:why_chosen]: why_chosen: 架構已穩、續推邊際遞減且剩的是實作合約非設計對錯;凍golden保三輪findings+待釘合約清單,實作另議。補網E1現成可建、立刻把頭號腐爛變免費週期檢…
    65 [fm]: - content: phase-2 落地:補網 E2(建在被推翻決策上)+ 前置 P1(supersede 自動補 ended/bump updated)已實作/測試/docto…
    67 [fm:context]: context: E4(V.date<node.updated)在 110 節點真圖 51 條背書噴 14 條(27%)、全是模組後來 bump updated 的良性落後=噪音產…
    68 [fm:why_chosen]: why_chosen: 先出高信號低噪音的 E2(全圖僅 2 條被推翻決策、來源都已跟上→0 假陽性);E4 照 spec 出會變每輪 14 條麻痺清單,違背 warn_soft …
    76 [body]: **PRIOR-ART:** 原以為「借既有 impact 引擎小擴」——**兩輪 Codex 讀 repo 證偽兩次**：r1 誤指 `_reco_scores`（推薦排序器）；…
    … 還有 5 處
  1.509  Projects/canary注意力檢查失效.md  [筆記]
    89 [body]: ## 五、★推論：`輪有效` 這個錨可能量錯了東西★
    118 [body]: → 對照本案：★`caught` 只證「這一次抓到這一個」，推不出「這席這一輪醒著」★——
    119 [body]: 而 gate 現在正是這樣推的。
    320 [body]: 334 筆記錄每筆的 `kind` 就是 `caught|missed` 一個字，**判定依據全數未留存**。
  1.505  Projects/loop三輪壓縮_計劃.md  [筆記]
    53 [body]: 一輪 panel 收斂 = **四條合取**(全建在 framing 汙染不到的結構上;推導與文獻見下「散文收斂」節):
    66 [body]: `lumos canary record` 加選填欄 `--round <id>`:一輪 panel = W 筆記錄共享 round-id(保留 per-auditor caugh…
  1.381  Projects/執行DAG_調研.md  [筆記]
    15 [KEY]: KEY:★腐化數字(★量測時點 2026-09-07,含活計數,引用必帶時點★)★:Projects 標 doing 43 篇(母體 155,含本篇自己)、其中 17 篇 >30 …
    16 [KEY]: KEY:★方案 B 的地基被外家打穿兩個洞,原稿主推薦已修正★——洞一:「任務都有測試名」是假的全稱前提,覆蓋率僅約 75%(本家 56/74、外家 62/83,兩造獨立數一致),…
    41 [fm:why_chosen]: why_chosen: 七條全部附了可重跑的證據(file:line、實跑輸出),其中兩條本家獨立複驗成立(t_delguard 被 Task 1-5 共用;settle 35 條…
    69 [body]: 1. **實作計畫筆記的任務拆解**——T1..Tn、「包①→②→③嚴格順序」、每任務寫明改哪/測什麼/斷言什麼,底下「進度」段記日期與教訓。
    101 [body]: | [[Projects/全repo審視_計劃]] 的 50 群主清單 | **表格沒有「做完沒」這一欄** | 進度靠翻 git 提交訊息裡的 `#編號` 回推;開頭「一件都還沒…
    127 [body]: | markdown 原生任務板 | **Backlog.md** / **Vibe Kanban** | 任務=帶 YAML 標頭的 md 檔放 git;另開介面給 agent …
    155 [body]: **★洞二:「測試存在且綠」根本推不出「任務完成」(外家 f2,這是最致命的一條)★**
    195 [body]: | f2 | ★「測試存在且綠」推不出「任務完成」★——共用測試、只寫跑全套、開工前就已綠 | 折入;本家開檔複驗 `t_delguard` 被 Task 1–5 共用,成立 |
  1.345  Projects/版本發布流程_計劃.md  [筆記]
    23 [KEY]: KEY:★邊界(不推翻既有決策)★——[[Projects/CLAUDE注入re-sync與版本標籤_計劃]] 已裁「版本號=人可讀標籤、嚴禁當 staleness oracle」…
    37 [body]: `release` 分支正是這個分離：main 隨便推，release 只有你把它快轉過去。**壞掉的 main 傳不到任何人**，因為沒有人跟 main。
    82 [body]: - **限制誠實記**：事後檢查（tag 已存在才跑），讓錯誤可見，不能阻止 tag 被推出去。
    121 [body]: - **`[S4]` 是事後閘**：錯的 tag 推出去後才紅，此時已可能有人裝到。
    131 [body]: | [S4] | tag workflow 的版本斷言邏輯（fixture 驗，不真推 tag）＋ 兩份 workflow 不得各自維護步驟清單 | 單元＋機械守衛 |
    186 [body]: 最新一筆,害守衛每次日常推送都紅。
    222 [body]: - **[S6] 二進位指紋**:`fetch-notesmd.sh` 平常用不到(只有改筆記檔名時才抓)。
    254 [body]: **踩到的地方**:`git push Lumos main:release` 被本機推送閘擋下,判定「高風險、沒審過」。
    … 還有 2 處
  1.320  Projects/design-loop提效_計劃.md  [筆記]
    107 [body]: - **W-record 歸屬(r1 Codex+B 折入)**:cluster 合併是編排者一次性彙整,**每輪至多一筆記錄帶 `--clusters`**(建議掛該輪最後一筆)…
  1.219  Projects/結清式收斂_計劃.md  [筆記]
    37 [body]: - **canary 醒著條件保留（r1 折入，r2 補記帳鏈）**：settle 輪照 skill 紀律植 canary；條目欄位含 `verified_in_round`（哪一…
    82 [body]: - r1 panel（2026-07-27，3 席 sonnet 全 caught＋Codex 辯方 3 庭）：**blocker×1**＝settle 對著 legacy 設計而…
    84 [body]: - r3 delta panel（2026-07-27，3 席全 caught：型別 d 未定義產物／a 幽靈引用／b 未定義旗標；s1 重植1次、s2 重植2次頂格）：**blo…
    116 [body]: **代價**：舊 loop 的 canary 證據**不進新 gate**——settle gate 只認新 loop 自己的記錄。本案 r1／r2 共 10 筆記錄因此不替結清背…
    129 [body]: - ★**「實作完成、測試全綠」不能用來結清語意條**★——編排者實測踩過：把 18 條語意條標 `mech-ok` 想推進，未結清數從 10 **漲到 18**（`mech-ok…
    130 [body]: - **推論**：settle 對**改版頻繁的 spec** 不適用。它的假設是「spec 拆完清單後相對穩定」；一旦進入實作、spec 隨實作發現持續演進，條目級 sha 綁定…
  0.908  Systems/測試假綠形態.md  [筆記]
    25 [KEY]: KEY:[2026-09-06]★新型:不是假綠是「假紅」,但同源——測試沒在驗它宣稱要驗的東西★。t_codex_s1_lens_arm_claim 驗的是席次 token 原子…
    208 [body]: - **推送閘相容性守衛,連兩次**:我要驗「判準是離開碼不是摘要檔」,但假執行器根本不支援分片,能力探測會讓它退回串行,**分片那條路一次都沒走到**。補了一個「說明裡有那個旗標…
    228 [body]: ★同一句教訓當天犯第二次★:量「缺回頭條件的筆記有幾篇」時,我用「同一行為空」數出 78 篇,實際那是清單寫法、值在下一行;正確是 0 篇空值、7 篇連鍵都沒有。**兩次都是「只用…
    310 [body]: 同一天的代碼審在別的地方抓到這個形態,回頭查健檢自己就有一段是同型,而且**當場擋住了一次正常的推送**。
    313 [body]: 而 issue 計數會讓健檢在嚴格模式回非零,推送關卡與 CI 都用嚴格模式。
    326 [body]: - 我今天就是這樣:健檢突然擋下推送,我一路往回查了五段,最後才查到是這一段。
    337 [body]: 第一次跑就報了第二個命中——而那正是二十分鐘前擋住推送的另一段。
    401 [body]: **這一型的兩個天花板（都實測過，不是推測）**:
    … 還有 2 處
  0.000  Issues/E2時區跨日誤報.md  []
    12 [fm]: - "[[Verification/2026-07-14_relguard_E2建在被推翻決策上]]"
  0.000  Issues/ci-wait對當日run判no-run.md  []
    20 [body]: > 白話：推完之後用工具問「CI 綠了沒」，它回「沒有 run」或「等到超時」；但同一時間直接問 GitHub，那幾個 commit 的 run 都已經跑完而且是綠的。工具看不到，…
    26 [body]: - `lumos ci-status` 印的是 13:29 那次查到的舊結果（eb58cab），之後幾次推送都沒更新。
    30 [body]: - 推送後的 CI 結論進不了治理帳（code-loop skill 步驟 8 要求用 ci-wait，rc0≠綠那條也就無從判）；人只能繞去 gh，正是 CLAUDE.md 叫別…
  0.000  Issues/ci-wait未推送sha誤導訊息.md  []
    5 [KEY]: KEY:ci-wait/ci-status 認本機 HEAD;HEAD 未推送→報「no-run:此 sha 未觸發 workflow」,實因=commit 沒推,訊息帶人去查 w…
    6 [DECISION]: DECISION:修法=查詢前驗 sha 在不在遠端,不在→獨立判定值(如 unpushed)+白話訊息「這個 commit 還沒推上去」
    18 [body]: # ci-wait未推送sha誤導訊息
    20 [body]: > 白話:HEAD 還沒推上去時,ci-wait/ci-status 會說「此 sha 未觸發任何 workflow(檢查觸發條件)」——事實是「這個 commit 根本沒推」,訊…
    23 [body]: 查詢前比對 HEAD 是否存在於遠端(`git branch -r --contains` 或 ls-remote);不在→訊息改「這個 commit 還沒推上去,CI 不會有它的…
  0.000  Issues/code-loop-pass自失效追尾.md  []
    33 [body]: append 一行,而我推的時候還沒提交那個檔——**本機看得到留痕、遠端看不到**,
    42 [body]: 留痕綁「被推上去的那個 sha」,而留痕本身住在一個必須另外提交的檔裡
    47 [body]: ### 現在白名單漏了什麼(2026-09-08 查證,不是推測)
    56 [body]: 結構上就會讓剛剛那筆留痕對下一次推送失效。目前不痛是因為每一批都會重新 pass 一次。
    57 [body]: ★2026-09-10 起凍結判定挪到 pass 之前、併進功能那個提交★(見 [[Projects/提交推送規範_計劃]];凍結記的是檔案內容指紋
    58 [body]: 不是提交編號,併進去不影響回放)——這條結構問題照新順序做就不會發生,推送後也不再多一個「凍結判定」提交。
    62 [body]: 1. **`code-loop pass` 之後要先提交治理帳,再推。** 順序反了就是「本機綠、CI 紅」。
    63 [body]: 2. **高風險那批推之前,先跟同工作區的人約一段沒有人提交的窗口。**
    … 還有 1 處
  0.000  Issues/code-loop守衛main-direct盲區.md  []
    23 [KEY]: KEY:排程[2026-07-21 使用者裁「排」]——①✅M1包 事後 code-loop 終審**已完成**(三輪+Codex NO-VETO+pass 留痕,補審抓 15 洞…
  0.000  Issues/lint-watch空轉假綠.md  []
    56 [body]: - 同批發現更大的一個假綠在健檢:沒有 `.lumos/lint.json` 的專案,doctor 印的是**綠勾**「未宣告跳過」——等於恭喜你沒接 linter。而所有自動路徑…
  0.000  Issues/loop-next吐不可宣告的tier.md  []
    17 [KEY]: KEY:★這個 bug 自己維持自己★——碰到 rc2 最自然的修復是「把 --tier 拿掉再跑」,拿掉就記不上定錨 → 下一輪 next 又推成 legacy → 又吐一條跑不…
    54 [body]: `LOOP_TIERS = ("light", "standard", "high")`。**`legacy` 不是可宣告值**——它只是「無定錨舊帳 ＋ legacy 格式」的推…
    60 [body]: 拿掉 → 記不上定錨 → 下一輪 `loop next` 又推成 legacy → **又吐一條跑不動的指令**。
    71 [body]: | `legacy`（推導） | 1 | **6** |
    108 [body]: **兩條現場成立前置**：① `tier == "legacy"` 且 `phase == "plant-canary"`（證明真的走到 legacy 推導路徑）
    115 [body]: 不得逕改。但推測修完本條後它會自然萎縮——tier 標得上了，掉進 legacy 的路徑就少了。
  0.000  Issues/loop機制痛點_Landmark_code-crossclaim實跑回饋.md  []
    22 [KEY]: KEY:②留痕座標三方不一致——code-loop pass 綁當前 branch/pre-push 查推送目的地 branch/check 無參數用 merge-base,三個入…
  0.000  Issues/prepush測試閘假紅-git環境洩漏.md  []
    14 [KEY]: KEY:★第一次診斷是錯的,留著當教訓★——先押 `GIT_DIR` 洩漏,實測把 GIT_DIR 指向本 repo 確實讓 65 條翻紅,「機制成立」就當成「找到真因」;修完再推…
    35 [body]: 先押的假說是「`git push` 把 `GIT_DIR` export 給 hook，hook 傳給測試進程，測試自己 `git init` 的臨時 repo 被 `GIT_DI…
    37 [body]: 實測：把 `GIT_DIR` 指向本 repo 再跑整套 → 紅的條數從 3 **暴增到 65**；套修法後同一環境 → 2039 passed / 0 failed。看起來機制完…
  0.000  Issues/主程式讀取路徑漏接UnicodeDecodeError.md  []
    18 [KEY]: KEY:★已跑過會翻紅的指令(依 [[Systems/診斷迴圈先行]] 完成判準,不是讀 code 推理出來的)★:`printf` 造一個含 `\xff\xfe` 的 .md →…
  0.000  Issues/分片平行跑時測試去數共用暫存目錄.md  []
    14 [KEY]: KEY:★症狀★ t_runner_isolation_r1_fixes 只在推送前的閘(全套)紅、單獨跑永遠綠;訊息是「早退沒有留下現場」before=239 after=240…
    15 [KEY]: KEY:★根因★ 那條斷言去數「整個系統暫存目錄底下有幾個 gctl-run-」,前後各數一次;但推送閘 ★切成四片同時跑★(LUMOS_TEST_SHARDS 預設 4),每片各…
    29 [body]: 2026-09-08 推送被閘擋下,4 片加總只有這一條紅:
  0.000  Issues/合約測試閘只在高風險推送跑.md  []
    19 [KEY]: KEY:症狀=一道「改到硬合約就跑那些合約綁的測試」的閘,圖譜/計劃/三份說明書都寫「每次推送都跑」,但那行呼叫從第一天就寫在高風險那個分支裡;低風險推送本機沒跑,而 CI 又刻意…
    20 [KEY]: KEY:★真正標成硬合約的那一行本身沒有「每次推送」四個字★——帶這個前提的是它旁邊的白話流程段。要改的是流程說明,不是動合約行
    21 [KEY]: KEY:本 repo 看不出來的原因=推送關卡在那之後無條件跑全套測試,合約綁的那幾支本來就被跑到;真正受害的是消費端(沒有那道全套閘,而工具鏈也不分發 CI 樣板)
    22 [KEY]: KEY:上一份計劃([[Projects/受波及合約測試真跑閘_計劃]])需求第 1 條的前提「pre-push 每次推送都呼叫,不分 tier」從一開始就不成立,而那份已結案、還…
    24 [DECISION]: DECISION:修法設計在 [[Projects/合約測試閘什麼時候跑_計劃]];★2026-09-07 Enzo 已裁:低風險推送照樣跑合約測試、紅了印出來記帳但★不擋★;高風…
    26 [body]: # 合約測試閘只在高風險推送跑
    29 [body]: > 圖譜、計劃、三份說明書都寫「每次推送都跑」,但那行呼叫從第一天就寫在「高風險」那個分支裡面。
    30 [body]: > 低風險的推送,合約綁的測試本機一次都沒跑;而持續整合又刻意跳過它,理由寫著「本機真跑」。
    … 還有 7 處
  0.000  Issues/嚴謹度分配偏向機械層.md  []
    19 [fm]: - content: 紀律層開始有測試:情境探針 32 題(指令)+5 題(答案品質)+6 題(紀律:改完寫回/寫完 lint/收工 doctor/設計進計劃節點/被催也先 imp…
  0.000  Issues/多平台設定下測試指令被默默略過.md  []
    14 [KEY]: KEY:★2026-09-11 pos-ios 推送時實際撞到★:設定宣告了 platforms,測試指令卻留在最上層 test.run_cmd——多平台模式下它照設計不生效,合約…
    29 [body]: - 2026-09-11,另一個會談在 pos-ios 推送,推送檢查印出「這個專案沒設測試指令(.lumos/config.json 的 test.run_cmd),受波及合約的…
    40 [body]: - pos-ios:`run_cmd` 搬進 `platforms.ios`,拿掉被略過的最上層 `test`,在設定檔的說明欄補一句為什麼;maestro 平台刻意不給指令(目前…
    52 [body]: - mOrangePos 專案裡的 lumos 是很舊的版本,**還沒有合約測試閘這道檢查**,連 `--version` 都沒有。它的測試不跑,主因是工具太舊。更新會一次帶進這幾…
  0.000  Issues/寫下風險當成處理風險.md  []
    46 [body]: 1. 鏡像分家:「移除 remote 只擋誤推,不擋有人手動加回來再推——無機械守衛,靠本決策留痕」
  0.000  Issues/引句錨定只驗前綴_後半可編造.md  []
    59 [body]: **一、改判準必須同時推進回放引擎版本。** 回放的黃金抽查靠比對 `_REPLAY_ENGINE_REV` 決定要不要用現在的程式碼對凍結閉包重算:版本沒變就重算,版本變了才視為…
  0.000  Issues/探針沙盒改動真全域機器狀態.md  []
    21 [KEY]: KEY:機制=情境探針把 repo 複製到臨時沙盒、在裡面跑 claude -p,但那個 session 的 HOME 是真的 ~/;只要它(或子程序)跑 lumos instal…
    39 [body]: 修法 A 實驗跑完,要調 `lumos-code-loop` skill 走推送前代碼審,叫不出來。一查 `~/.claude/skills/*` 全是懸空 symlink,指向 …
    46 [body]: - **這是 [[Issues/探針沙盒能推到真遠端]](2026-08-23)的同一家族**:沙盒擋了 git push(拔 remote、pre-push 寫死 exit 1)…
  0.000  Issues/探針沙盒能推到真遠端.md  []
    16 [body]: # 探針沙盒能推到真遠端
    19 [body]: > 所以被測 AI 一 push 就直接推到真的 GitHub 主幹。2026-08-23 真的發生了。★已修。★
    27 [body]: **發現方式**:下午推正式提交被拒(遠端領先),看到「probe snapshot」這個只該出現在沙盒裡的訊息。
    31 [body]: 原本的隔離只做了 `core.hooksPath=/dev/null`(不跑 hook),沒想到「推出去」這條路。
    32 [body]: ★「動到的只是副本」≠「副本推不出去」。★
    35 [body]: 不是它推的,是 `t@t.t` 這種假 email 被該帳號綁走,GitHub 把作者歸給它。
    40 [body]: ① 拔掉所有 remote——沒有目標就沒得推
  0.000  Issues/推新分支時風險分級拿空樹當起點.md  []
    15 [KEY]: KEY:pre-push 算風險分級時,遠端還沒有的 ref(新分支,★含首推 main★)沒有東西可比,退回拿 git 空樹 4b825dc6… 當起點=把整個 repo 當全新…
    16 [KEY]: KEY:★這是刻意的 fallback 不是 bug★——scripts/hooks/pre-push 範圍推導三分支,註解明寫「新 ref(含首推 main:遠端無此 ref)→…
    18 [KEY]: KEY:誠實界線——影響面比第一眼小:這個 repo 慣例是本地開分支、本地合併、★只推 main★(實查遠端只有 main 一個分支,本地有 8 個功能分支+多筆 merge 提…
    20 [KEY]: KEY:2026-09-03 那次的處置=改推主線(遠端有 main 可比,範圍回到 25 檔),閘自然過,★沒動用任何繞過機制★;代價是白跑一次全套測試(單獨計時超過 10 分鐘…
    26 [body]: # 推新分支時風險分級拿空樹當起點
    28 [body]: > 白話:推送前的守衛會先算「這批改動有多高風險」,高風險就擋下來要求先跑代碼審。但**推一個遠端還沒有的分支時,它沒有東西可以比對,就退回拿「空樹」當起點**——等於把整個 re…提醒:命中≠查完——搜尋只告訴你「哪裡可能有」,不是完整內容;光看摘要就判「圖譜沒記」以前真的出過錯。下結論前先讀全文:lumos show <節點>

    32 [body]: `scripts/hooks/pre-push` 的範圍推導有三條分支,註解寫得很清楚:
    34 [body]: - `remote_sha` 全零(新 ref,★含首推 main★)→ `_range="$_EMPTY_TREE..$_lsha"`,註解:「保守掃全部引入內容」
    … 還有 7 處
  0.000  Issues/散文紀律沒有退場機制.md  []
    132 [body]: - [ ] **B · 剪枝加第四種合法操作，並順手解掉自相矛盾**：在既有硬不變量下開一道窄門——「**經前後量測顯示無改善或倒退**」的規則准予撤除，且**必須附上那次量測**…
    144 [body]: 3. **誠實記無守衛**:其中一個失誤(重推一個 code 早就否決的優化)沒有任何機械守衛接得住,就明寫「無守衛,重驗條件=下次有人再提就看這篇有沒有接住他」。
  0.000  Issues/簿記白名單漏canary與bypass帳.md  []
    14 [KEY]: KEY:死結型缺口(batch2 CI 紅實錘):_BOOKKEEPING_FILES 白名單漏 docs/.canary-log.jsonl 與 .bypass-log.json…
    25 [body]: 根治=把 docs/.canary-log.jsonl 加進 `_BOOKKEEPING_FILES`(scripts/lumos:11315)——但那是 code 改動、要自己過…
  0.000  Issues/連鎖佇列開了沒人跟完.md  []
    33 [body]: **一句話**：`decision-supersede` 會自動幫你開一張「誰引用了這條被推翻的決策」的待辦單，**但沒有任何東西會提醒你那張單還沒做**——歷來開過兩張，兩張都是…
    79 [body]: - **③ 裁定＝borrow-design**：借「撤稿通知要推到直接引用者」的意圖，原生實作（掛既有帳本），零依賴家規排除 adopt。
  0.000  Issues/風險掃描遇到非UTF-8內容整支中斷.md  []
    16 [KEY]: KEY:推送前檢查與 CI 都會跑的 pitfalls --diff 用文字模式讀整份 git diff;提交裡有一支內容不是 UTF-8、git 又沒當成二進位的檔,解碼就丟錯、…
    18 [KEY]: KEY:★2026-09-11 查清範圍比原本以為的大★:不只風險掃描,波及計算、派工鏡頭也會中斷;★推送檢查那邊更糟——風險掃描壞掉時是放行(fail-open),分級變成 un…
    22 [KEY]: KEY:守衛測試第一版推上去當場 CI 紅:「找專案根目錄必須嚴格解碼」那段對工具裡每個函式呼叫都用 ast.get_source_segment 切一次整份原始碼,本機 130 …
    29 [body]: `lumos pitfalls --diff <範圍>`(推送前的檢查與 CI 都會跑)在 `scripts/lumos` 的 `_pitfall_diff_collect` 裡用…
    31 [body]: 解碼就丟 `UnicodeDecodeError`,整支中斷——推送前的檢查跟著停。
    42 [body]: 解不了的位元組變成替代字元,只影響那幾個字元的比對,其他行照掃;推送檢查因此拿得到真的分級,不會再因為掃描壞掉而放行。
    61 [body]: 守衛自己也餵壞的、好的、泛用包裝、別的程式、變數程式名五段,證明它真的會翻紅、也不會亂抓。行為面另有兩支測試:內容不是 UTF-8(風險掃描、推送檢查、波及計算、
    66 [body]: ★放行本身沒改★:風險掃描真的壞掉時(例如 git 不在),推送檢查仍是放行、不擋人——那是刻意的設計,這次只拿掉「一個字元就能讓它壞掉」這條路。
  0.000  MOC/index.md  []
    22 [body]: - [[Systems/棧別提問表態閘]] — 推送前每一題效能檢核都要有機器讀得懂的交代
    24 [body]: - [[Systems/每支檔有家]] — 每支程式檔要有一篇管它的節點、節點只寫自己家的檔、寫回落對篇;提交前與推送前擋新違規,健檢 S8–S10 列舊帳
    25 [body]: - [[Systems/check-j-regen-guard]] — Check J:from-scratch 重建節點 provenance 分級(regen 蓋章+[src:…
    33 [body]: ## 節點檢索與推薦(`scope/retrieval`)
    38 [body]: - [[Systems/retrieval-ranking]] — BM25F 排序+圖分融合推薦+impact 降噪(search 與 hook 面均已轉正——§6 七盞全綠;r…
  0.000  Projects/Android側UI測試綁圖譜工作流_實作計畫.md  []
    228 [body]: （★不要寫 `"multiplatform": true`★——那是回傳的推導結果、程式從不讀；★maestro 的 `root` 不能是 `.`★——會讓 doctor 掃整個 …
  0.000  Projects/Android側UI測試綁圖譜工作流_計劃.md  []
    64 [fm:context]: context: r2 opus 席(F6)實查推翻 d2 的前提:S1 條文自身標明「紀律層規則非機械閘」(skills/lumos-code-loop/SKILL.md:227…
    229 [body]: | **name → 檔案路徑查得到** | 由 `[test:maestro:X]` 反推要跑哪個檔 | ⚠ **目前無路徑**（r1-F4）：maestro 只吃檔案路徑，`d…
    287 [★INVARIANT★]: - **r2（2026-08-11，delta 輪 2 席：sonnet 新宣稱正確性／opus 折入一致性與整合；canary 1 caught 1 missed）**：★這輪抓…
    292 [body]: - **flow 的 `name:` 必須是識別字且等於檔名轉底線**——改了就從「可機械反推檔案」退化成「只能全庫 grep」
  0.000  Projects/CI回流閉環_計劃.md  []
    15 [KEY]: KEY:問題——CI(GitHub Actions)紅了只存在 GitHub 網頁,本機 lumos/圖譜/治理帳全不知情;下個 session 開場也讀不到 → 自動開發迴圈在「…
    16 [KEY]: KEY:★彈性宣告(2026-07-29 使用者裁定,零侵入預設)★——推送路徑由專案 `.lumos/config.json` 的 `ci.flow` 宣告:**無宣告=dire…
    17 [KEY]: KEY:解法方向=**push 後同輪等待+修復重試(watch-fix-retry)**,非雲端自動修也非留到下次開場:`lumos ci-wait` 在 push 成功後阻塞等…
    37 [body]: - **不改預設行為**：未宣告 `ci.flow` 的專案（含所有既有消費 repo）行為與現在**逐字相同**（直推、無 PR、無新閘）。
    65 [body]: ### [S1b] 推送路徑分派（`.lumos/config.json` 的 `ci.flow`，彈性宣告）
    72 [body]: - **未宣告 `ci` 區塊（絕大多數既有專案）＝功能全關**：不跑 `ci-wait`、skill 不加等待紀律、hook 不提醒、gov 無此源——**行為與現在逐字相同**…
    73 [body]: - **`pr`**：改動走 feature 分支，`lumos ship` 串流程（定義見 [S1c]）：建/推分支 → 開 PR → 等分支 run 綠 → 合併 → **合併…
    74 [body]: **合併後複查是必要的（r2 席2）**：squash merge 在 main 產生**全新 sha**，它不是分支 sha 的子孫——所以 ①分支綠不代表 main 綠（squ…
    … 還有 6 處
  0.000  Projects/Codex外審吸收_計劃.md  []
    18 [KEY]: KEY:待辦 backlog(依價值序)——①合約普查(星標 INVARIANT 密度慘案:172 篇僅 2 條掛最強鏈;嚴禁 code 反推,按業務語意逐一判)②cluster …
  0.000  Projects/Spotify-shunt吸收_調研.md  []
    49 [body]: > 白話:Spotify 公開了他們工程師用 Claude Code 的省 token 設定(叫 Portal 的 shunt 插件):貴的模型不准直接打開超過 350 行的檔,h…
    55 [body]: ## 一、Spotify 那套到底是什麼(對照推文 vs 原文與原始碼)
    59 [body]: | 推文說的 | 原文/原始碼實際是 |
  0.000  Projects/bootstrap一鍵對稱_計劃.md  []
    21 [KEY]: KEY:已知殘留(std 照出既有病,本刀不修)=F4 半成品 vault 無自癒(init 見 vault 即輕路徑不補缺)/F9 docs/knowledge與standalo…
    119 [body]: - **既有病記殘留（本刀不修，另見殘留節）**：F4 半成品 vault 無自癒、F9 docs/knowledge(舊名;現 docs/lumos-toolchain-know…
    124 [body]: - **F9**：docs/knowledge(舊名;現 docs/lumos-toolchain-knowledge)／standalone vault 佈局下 `cmd_ini…
  0.000  Projects/canary生成硬化_計劃.md  []
    14 [fm:why_chosen]: why_chosen: 弱模型不腦補、它都抓到=真太明顯,同 [audit:] 用 sonnet 的哲學;haiku 成本可忽略;強模型當探針會把難度推到審計員也抓不到(canar…
  0.000  Projects/code-loop必用守衛_實作計畫.md  []
    78 [body]: - [x] **Step 3: 實作** — 見設計 §1+§2:跑 `pitfalls --diff <range> --no-lint --json` 取 tier;讀留痕,p…
  0.000  Projects/code-loop必用守衛_計劃.md  []
    41 [body]: `pitfalls --diff` tier=high 目前只在 **pre-push advisory 提醒**(stderr、不擋),真的跑 `lumos-code-loop`…
  0.000  Projects/code階段強化_計劃.md  []
    19 [KEY]: KEY:[S3]性質測試席(選配,r1/r2 修)——開席=兩機械錨(tier=high ∧ impact 命中星標合約節點)+人工核純函式+具推導源(docstring/型別/圖…
    21 [KEY]: KEY:[S5]跨家族比重提升(使用者指示,r2 大修)——①辯方預設 Codex(兩 loop,成本中性替換=d4 合規)②雙 Codex 角色**僅 code-loop tie…
    24 [DECISION]: DECISION:[2026-07-18]S4 拒收記理由防重提;S3 觸發改開席四要件(兩機械錨+一人工核+推導源查核,r1-r3 逐輪收窄);S3 免辯方路由撤除(r1 三方共…
    58 [body]: **現況與舊帳**:07-15 圖譜判「自動生成 property 測試 oracle 不可靠」(agent 自己發明錯誤期望→誤報)。Anthropic 2026-07 配方:推…
    61 [★INVARIANT★]: - **觸發(開席四要件=兩機械錨+一人工核+一推導源查核,r1 收窄、r2 增訂、r3 正名)**:①tier=high **且** ②`lumos impact --diff`…
    62 [body]: - **流程**:席位 agent 讀 diff 涉及的純邏輯函式+文件/型別註解 → 推導 2-3 條性質(從文件推導,禁憑空)→ 該棧 PBT 框架寫測試(C#=CsCheck…
    63 [★INVARIANT★]: - **產出(r1 撤免辯方)**:反例的**可重現性**免爭(那是機械事實);性質的**合法性必過辯方**——辯方(依 S5 預設 Codex)專問:「這條性質真是該函式的業務合…
    81 [body]: 3. **關鍵單點判決 ≥3-run 多數決,至少 1 run Codex+家族否決保護(r2 折入)**:任一家族 run 提出 blocker 時,**不得僅以他家族的同門多數…
    … 還有 1 處
  0.000  Projects/design-loop折入守衛_計劃.md  []
    84 [body]: 3. **閘是紀律非防篡改**:同 design-loop 本身——lumos 擋不住「不跑 fold-check 就 commit」,靠調用+誠實。fold-check 是**可…
  0.000  Projects/design-loop重設計.md  []
    26 [KEY]: KEY:★誠實天花板(r1 補二條)★——★「錨得住的廢話」中間態(s2 blocker):五席摘真文配空話可同過四道形式閘,接受不假裝解決,防誤不防惡★;★需求誤解類下游天生接不…
    59 [body]: > **狀態**：2026-08-04 立案。吸收 [[Projects/design-loop判準重定位]]（該案不再獨立推進）與
    79 [body]: ★**「1/38」的推論界線（r1 折入，B3）**★：這個數字**單獨**推不出「閘壞了」——同組數字也吻合
    154 [body]: 4. **錨定檢查驗得了「引了真文」，驗不了「推論正確」**——引真文講錯話仍過錨定；靠辯方 refute 接。
    174 [body]: 幾乎不靠 canary caught/severity）——新閘可視為 settle 精神對 panel 路徑的推廣。**保留不動**，
    209 [body]: B3＝「1/38→閘壞了」推論跳步（s3）｜B4＝嚇阻消失（s2，s3 補刀）｜B5＝code-loop 隔離做不到（s4）。
    212 [body]: 「1/38」推論改立結構性證據＋下游研究列校準作業（B3）；code-loop 隔離接 d2 旗標為唯一機制（B5）；
  0.000  Projects/doctor-run事件_計劃.md  []
    36 [body]: - ★「已清」的判讀方式★:本事件**不**列受檢節點(nodes 恆空);「某節點已清」由讀帳方推導=「該 run 有 doctor-run 標記,但該 run 內沒有該節點的 …
    52 [body]: - **std r1(2026-08-21,三席同門+外家 gemini)**:major 1(s1:過濾落在 `ded` 上會連 stats 一起濾掉,測試只斷 gate 名會假…
  0.000  Projects/enforcement儀表板_計劃.md  []
    66 [body]: - ★實跑自驗:本 repo 跑 `lumos enforcement` = 8/9 active、1 unknown(遠端檢查)、anchor 那層當下 degraded 因 t…
  0.000  Projects/from-scratch重生守衛_計劃.md  []
    23 [KEY]: KEY:M1 spec v4(design-loop r1-r3 折入):regen 宣告(SCALAR_KEYS 擴)+四指針只掃 summary+Check J(原G撞名改)+…
    65 [body]: 1. **縮面積——對舊節點 diff 重生、不整篇換**。stale 也是拿舊節點當底料、只重寫被證據推翻的部分、輸出 diff 給人審。保住殘存目擊內容，把 synthesis…
    66 [body]: 2. **provenance 分級隔離——複用不對稱雙欄信任**。每條 claim 帶證據級：Tier A（現 code 可驗,file:line）/ Tier B（git 史變…
    68 [body]: 4. **殘餘 Tier-C 轉問題問人——走 signoff**。目擊者還在＝問不是推。重生吐**問題清單**（Tier-C conjecture）路由給人確認。＝「重生即結構化…
    94 [body]: - `推測:` 前綴 — **Tier C**（無直接證據的推論,顯式標）。**疊放順序釘死**:summary 行內接在既有前綴後（`KEY:推測: ...`/`DECISION…
    97 [★INVARIANT★]: - **不對稱信任接線**：`推測:` 行**不得**承載 ★INVARIANT★/★IRREVERSIBLE★（合約不能建在推測上）;推測升級唯一路徑＝補 [src:]/[git…
    111 [★INVARIANT★]: - **J-a（硬擋 rc1,拒絕發明合約）**：★INVARIANT★ 行無 `[src:]`/`[git:]` 任一 → 擋。理由:`[test:]` 只證「行為現在成立」,不…
    112 [body]: - **J-b（硬擋 rc1,同規則擴至決策）**：summary `DECISION:` 行無證據指針且無 `推測:`/`佚失:` 標 → 擋（重建的 why 必須標來源或標推測…
    … 還有 2 處
  0.000  Projects/graph-engineering掃描2026-08-19_調研.md  []
    73 [body]: ✅ 已查證(2026-08-19,原標「未查證」):見上一則的兩群拆分。★初判把八個並列成「都沒觸發」是錯的,已推翻★——寫別本帳 ≠ 沒觸發。已立案:[[Projects/閘觸發…
    99 [body]: 抽層讀了六十幾條,`related` 底下實際混著:驗證了 / 事故揭露缺陷 / 規則的教訓來源 / 計劃要動這個系統 / 同案的實作篇與設計篇 / 這批接前一批 / 被推翻導致停…
    115 [body]: ② **重推一個 code 早就否決的優化**:related 不入多跳寫在 code 註解裡,圖譜一篇都沒講,所以整輪走完才發現前提不存在。★**這條沒有機械守衛**★——重驗條…
    129 [body]: 推送閘確實不跑(0.18s 的 pitfalls 都嫌慢),但這是**知道且刻意週期跑**,不是漏。
    157 [body]: - **證據包裝**:世界主張回答要引**來源記錄**而非只引邊,且路徑含推測/過期邊時要能答「證據不足」。本專案的 `[src:]`/`[git:]`/`推測:`/`佚失:` 只…
  0.000  Projects/guard殺傷力驗證_計劃.md  []
    50 [★INVARIANT★]: 1. **壞法由人宣告，不自動生成；配方存節點級 `kill_recipes` frontmatter 欄位（r1 折入：不進 decisions——decisions 是節點級平…
    116 [body]: - ISO 26262 fault injection、DO-178C requirements-based coverage（需求推導壞法、人審把關）
  0.000  Projects/idioms自維護迴路_計劃.md  []
    53 [fm:why_chosen]: why_chosen: 架構已穩、續推邊際遞減且接縫需真build(非spec patch);凍成golden保住三輪findings語料+架構決策,實作另議。phase-1只做真…
    112 [body]: - `[S6]` 讀 `.lumos/idioms-framework-watch.json`（`[{doc, framework, name, registry, current…
    163 [body]: - **C1b current 生命週期**：`source_of_current` 指 lockfile 則自動；人手填則採納後需推進，否則版本標記失真。
  0.000  Projects/loop機械脊椎M1包_計劃.md  []
    20 [KEY]: KEY:#1 loop next——`lumos loop next <id> [--json] [--tier standard|high|light]` 唯讀讀 canary-…
    25 [KEY]: KEY:落地同步義務(七項,由折入衍生,枚舉寫死)——skills/lumos-design-loop/SKILL.md(record 時序 C4/手算 N 改指 next/lig…
    52 [body]: - **無 `--tier` 的身分推導（r3 折入；r7 Codex 終確認統一——原兩處「預設 standard」殘句與 tier 定錨規則分叉，high 可被合法降 stan…
    61 [body]: - `width`：tier→席數（light=1／standard=3／high=5；`--tier` 不給→**依身分推導（定錨優先，見上；r7 統一——舊「預設 standa…
    64 [body]: - **席數下限（r4 新 major；r5 legacy 值；r6 Codex 終判雙補——①數記錄筆數可被同席重複 append 灌滿 ②tier 不持久化，下次省略 --ti…
    117 [body]: - **next/gate 契約（r6 終判補列）**：**gate-pending 先於 cap**（到 cap 且缺 --spec → gate-pending 非 cap-r…
    136 [body]: - **C1 next 輸入不足不得宣告 converged（major）**：gate 合取依賴 --need/--spec/--repo/--panel——next 改為完整 …
    144 [body]: - **S1-F-CAP（major）**：無 --tier 預設 standard 與 cap 的 legacy 判定自相矛盾——改帳面格式推導（legacy→1/6；panel…
    … 還有 2 處
  0.000  Projects/pitfalls-lint-integration_計劃.md  []
    30 [fm:context]: context: 使用者三連問(偏科有 linter?其他平台?通則也有?)推導出——規則庫社群已維護且更新更快、更準(AST 級)、免腐化
    47 [body]: 偵測技術棧 → 跑專案宣告的一組 lint 指令(各輸出 SARIF)→ lumos 解析合併 SARIF → 收進 pitfalls `--diff` manifest 餵 re…
    66 [body]: - 起點認知:`docs/design/2026-07-04-pitfalls-code-loop.md`(通則層已 merge;偏科層原設計「自建網搜迭代包」經本 brainst…
  0.000  Projects/pitfalls棧別效能追問_計劃.md  []
    15 [KEY]: KEY:Vercel 實證錨——靠模型自己想起查規範 56% 跳過→機制推送不靠自覺;提問式>陳述式(pitfalls 逼答哲學)
    24 [fm:context]: context: 三時機推到眼前;留痕建議含答案,人工紀律
    33 [body]: > 把 [[Systems/效能檢核目錄]] 的棧別效能提問接進工作流三時機(動手前/終審/蓋章前),讓最佳實踐「被推到眼前」而非靠 Claude 自己想起(Vercel 實證:自…
  0.000  Projects/pitfalls網搜補漏_計劃.md  []
    31 [body]: > 解 [[pitfalls-lint-integration_計劃]] 的 ③ 網搜補漏(邊角)。**極輕**:一個 skill + 純圖譜,無 lumos 新碼。原「自建網搜迭…
  0.000  Projects/probe輪退場_計劃.md  []
    17 [fm]: - content: Enzo 裁甲(2026-08-25,r1 攤牌後):多席 code-loop(含 high)收斂閘統一走處置閘(d5 型記帳:各席留痕+一輪一筆彙總 car…
    89 [body]: probe-retire-v2 r1 審本版→過閘→[S1]-[S3] 實作→code-loop→推送;[S4] 兩輪數據回寫迴圈摩擦案並判其結案。
  0.000  Projects/skill寫法學借鑒與design-loop剪枝.md  []
    32 [body]: 3. **外部參考**——推出 SKILL.md、放進同目錄的檔案，靠一個**指標**拉進來；★指標的措辭★（不是它指向誰）決定模型會不會、多可靠地去讀。
    161 [body]: - 「沒遺失規則」靠清單 diff + 一個乾淨 agent，**不是證明**。清單抽取本身是「我枚舉了 N 種形態」——本專案已被這個坑咬過多次，故驗證推到覆核 agent 的語…
  0.000  Projects/中心性重驗排程_計劃.md  []
    26 [body]: PRIOR-ART: ① 最小解層級——`cmd_stale`/Check S 既有輸出加排序鍵，無新機制；PageRank power iteration 零依賴 ~30 行。②…
  0.000  Projects/主動影響幅度偵測_實作計畫.md  []
    33 [body]: **Goal:** 實作 `lumos impact` 原語 + PreToolUse hook,動手前主動算出將被改動 code 的 downstream 影響節點集、推到 Cl…
    276 [body]: - [ ] **Step 1: 失敗測試** — 首次 True + 建標記;窗內第二次 False;標記時戳倒推 > ttl → True(復活);寫標記前清 >24h sess…
  0.000  Projects/主動影響幅度偵測_計劃.md  []
    20 [KEY]: KEY:補「pull 非 push」缺口——動手前主動算出將被改動 code 的 downstream 影響節點集、推到 Claude 眼前;現況影響幅度資料有建模(雙向 edge…
    330 [body]: ⚠ **裁定的性質(勿誤讀)**:上述數字**全部來自本工具鏈自己的 goldset 快照**,未對該工具做任何實測或對照。裁定邏輯=「我的瓶頸不在供給,故擴供給的工具對我無用」—…
    362 [body]: ⚠ **這個數字量的是「跳不跳得出東西」,不是品質**:方法上覆蓋率完全等同於「有沒有 code 路徑反查命中」(indirect 由 direct 展開,direct 空則整組空…
  0.000  Projects/代碼審資安席_計劃.md  []
    26 [body]: - 2026-09-11 治理日報四篇,其中兩篇直接相關:掃 3,171 個 AI 助手設定倉庫有 16% 帶安全缺陷(這套自己就是往別人機器裝 hook 的分發者);以及「機器算…
    32 [body]: - 技術棧慣例 skill 只有 node-idioms 有資安條款;linter 目錄列了資安類 linter,但擋推送那條鏈恆 `--no-lint`(2026-08-26 d…
    49 [body]: - 家族預設同門(相對於編排者),理由是外家額度:high 已經固定要兩席外家(找洞、否決),再多一席外家容易一輪吃光額度、退回「沒有外家席」(`Issues/外家席長期缺席仍照跑…
    68 [body]: - **每條發現必附攻擊路徑:誰、從哪裡、送什麼進來、拿到什麼**。寫不出來 → 標「推論」、最多 minor、blocking: 否。這條壓的是資安審最常見的毛病:一堆講不出攻擊…
    80 [body]: - 不改風險掃描的觸發條件(人裁 2);不改代碼審 standard 與設計審的編制;不把 linter 接進擋推送的鏈(d4 維持);不動 `code-loop pass` 指令…
    86 [body]: REVISIT:2026-12-11 盤點各專案治理帳:tier=standard 的推送裡改到登入/權限/密鑰/金流形狀檔案的有幾次;有就回頭議「風險掃描加資安類」
    89 [body]: - **定錨分級由編排者給,不跟推送時的風險分級對帳**(代碼審 r2 資安 G2):迴圈第一筆帳定成 standard,資安席這一步就永遠不要求,即使推送時 `pitfalls …
    90 [body]: REVISIT:2026-12-11 同一次抽查:本季 pass 對應迴圈的定錨分級,是否等於推送當下 pitfalls 算出的分級;有低報的就議「loop next 首筆 tie…
    … 還有 1 處
  0.000  Projects/公開精簡版_計劃.md  []
    107 [body]: > ⚠ **2026-07-31 Task 8：本節第 3 項已被使用者部分推翻，見下方〈2026-07-31 裁定變更〉**——原文（本節開頭「只做兩件事」與下方「明確不做」的 …
    109 [body]: > ⚠ **2026-07-31 Task 9：〈2026-07-31 裁定變更〉(Task 8) 的「只准附加、絕不覆蓋」再被使用者推翻,見下方〈2026-07-31 裁定第三次…
    125 [body]: **明確不做**（★以下 CLAUDE.md 那一句是原裁定，已被下方〈2026-07-31 裁定變更〉部分推翻，讀原文請跳去該節★）：不 scaffold 圖譜、~~不注入／不更…
    129 [body]: #### ★2026-07-31 裁定變更（Task 8，使用者直接裁定，推翻本節原「不注入/更新任何 CLAUDE.md」一句）★
    133 [★INVARIANT★]: **為何被推翻**：使用者判斷「完全不碰」矯枉過正——原裁定真正該防的是**覆蓋既有內容**，不是「寫入 CLAUDE.md」這件事本身。接手者讀圖譜需要先懂標籤語意（`FLOW:…
    148 [body]: | `install.sh` | 碰專案層 | ❌ **錯誤**——它只有一行 `exec ... lumos install --force`，`cmd_install` 全部動…
    151 [body]: #### ★2026-07-31 裁定第三次變更（Task 9，使用者直接裁定，推翻 Task 8 的「只准附加」）★
    176 [body]: 使用者在控制端**實際跑過**（不是推論）發現：`uninstall.sh` 拿 `~/.lumos-slim/scripts/lumos` 當 bin sha256 比對的唯一基…
    … 還有 7 處
  0.000  Projects/受波及合約測試真跑閘_計劃.md  []
    23 [body]: > 白話:改到相依功能時,工具現在只會「點名」那些功能綁的測試,跑不跑靠編排者自律。Enzo 2026-08-22 裁:被點名的要當場跑完才能往下——把它做成閘:`lumos co…
    26 [★INVARIANT★]: 1. **掛在擋的路徑上,不是記錄的路徑**:`lumos code-loop check`(pre-push 每次推送都呼叫,不分 tier)在判定 tier/留痕之前,先算 `…
    43 [body]: ★2026-09-07 [[Projects/合約測試閘什麼時候跑_計劃]] 明寫推翻這一條★:
    44 [body]: 「它本來就呼叫 check」是對的,但 check 只在 tier=high 且推的是分支時才跑
    45 [body]: ——所以「每次推送都跑」在低風險推送上是假的,而改一行低風險的碼一樣可以打破合約。
  0.000  Projects/地基盤點2026-08-26_調研.md  []
    37 [body]: - **G2 關係層只查存在不查語意**——[[Projects/關係層傳播守衛_計劃]] 自認「頭號腐爛(別篇決策推翻本篇前提)hooks 抓不到,只 $30 AI 交叉審掃得出…
  0.000  Projects/多平台合約測試綁定_計劃.md  []
    71 [body]: - **⚠ legacy 信號表示法（審計 r4 + opus 辯方拍板）**：`resolve_test_refs` 是否切分**以「config 原本有無 `platforms…
  0.000  Projects/子代理續談調研.md  []
    21 [KEY]: KEY:2026-08-14 實測=本機「互動式」terminal session 續談失敗「No transcript found」——互動 session 主對話與子代理正文 …
    25 [KEY]: KEY:★範圍界定(2026-08-14 補)★本篇「互動 session 不可用」只涵蓋「續問已結束的子代理」(吃磁碟 transcript,互動不落地故必敗);「對還活著的 p…
    33 [body]: Claude Code 新增「子代理續談」：派出去的子代理完成後，其對話脈絡（讀過的檔案、推理過程）保留在本機紀錄檔，同一 session 內可用 SendMessage（帶 ag…
    54 [body]: 環境：宿主進程 v2.1.229，Ghostty 終端手動啟動的**互動式** session（`claude --chrome --dangerously-skip-permis…
  0.000  Projects/宣稱級時間戳_計劃.md  []
    22 [body]: PRIOR-ART: ① 最小解層級——若真要做,最小解=給 `lumos stale` 或 lint 加宣稱粒度掃描(既有指令擴充,非新機制);②世界解過沒——有:Zep/Gra…
  0.000  Projects/審查有沒有用記帳_計劃.md  []
    14 [KEY]: KEY:S2 載體列必帶 --refuted-set(none 可)、id 對 intake 重現表列★整字★驗(a1 不因 a10 命中)、理由含實字;★不設 self-foun…
    35 [fm:why_chosen]: why_chosen: 拒收把格式問題推回收貨當下,機器數的數字才綁得住報告 sha
    41 [fm:why_chosen]: why_chosen: 必帶+整字比對是最小的機械守衛;存活多於席位報的 S 由讀側算式 max(0,M+R−N) 推出,不需要人填第四個清單
    65 [body]: - **兩個現成欄位一次都沒人填**:`--refute-verdict`(辯方表態)1216 筆裡 0 筆——今天查明原因是七個輪次一輪辯方都沒派(路由規則下多半不觸發),所以它…
    89 [body]: - ★不加 `--self-found-set`★(外家席:它會變成把「席位報了但我不想折」改標成自找的口袋)。編排者自找的發現在讀側由算式推出:S = max(0, M+R−N)…
    150 [body]: 全折、0 放行:改成寫側拒收沒正規化的報告+機器數、整字對 intake 重現表列、砍 self-found 由讀側推 S、gov --stats 印回頭條件要的數。行為斷言配例:…
  0.000  Projects/審查規模對照實驗.md  []
    102 [body]: - **n=1 的材料**，單一 diff、單一主題，不能外推到「所有審查」。
  0.000  Projects/審查規模對照實驗二_Landmark真缺陷.md  []
    47 [body]: L 刻意推過 **32K**（已發表的退化起點）。
    123 [body]: | L（40K token） | ★**minor**★ | 「**信心中等，僅供部署前確認**」「此推論建立在賣場提供公共 WiFi 這個部署假設上」 |
    138 [body]: - ★**天花板效應**★：兩格都 100%，代表**這兩根針對這個模型偏容易**。若要測出規模效應，需要更難的針（例如需要跨檔案推理才看得出來的缺陷）。**本實驗只能說「在這個難…
  0.000  Projects/已知坑機械前置_計劃.md  []
    19 [body]: > 緣起(2026-08-08,Enzo 一連串追問推導出的設計):事故記帳只接「已爆的坑」(先踩才有);世界已知坑(如 refresh-token→single-flight)不…
  0.000  Projects/席位人格化_計劃.md  []
    22 [body]: PRIOR-ART: **借用既有設計為預設**——最小解在派工措辭層,不新建機制、不加依賴、不動任何閘。自家範本已存在:[[Systems/arch-alignment-lens…
    35 [body]: **生效三條件**(多來源一致):(a) agent 之間**夠不一樣**(不同模型／種子／角色 prompt);(b) 批評**扣在明確步驟或事實上**;(c) 裁判**獎勵可查…
    38 [body]: **★反面證據(這是本案刻意不碰「互辯」的理由)★**:諂媚式從眾使模型放棄本來正確的推理去附和多數,比例達 **85.5%**;共識塌陷造成 oracle gap **32.3 …
    57 [body]: - **假陽性升高(★真隱患★)**:「預設駁回」的姿態可能推高噪音,與既有**抑噪紀律**(「低嚴重度疑慮,給不出具體失敗場景就不要標」)正面拉扯。處置:A 層落地時**抑噪紀律…
    64 [body]: 1. **只裁 A+C(推薦)**:零成本、有世界背書、與既有紀律相容;攻擊問句走「改述範例池」避開應試化衝突。
  0.000  Projects/循序codeloop-tier錨定_計劃.md  []
    84 [body]: - **cap 語意變更面**:code+standard 從(掉 legacy 的)6 變 3——這是本案目的非副作用;既有 legacy loop **不補標則**不受影響(無…
  0.000  Projects/指令索引與情境測試_計劃.md  []
    18 [fm]: - "[[Verification/2026-08-22_缺席推論探針題組]]"
    57 [body]: ## 2026-08-22 後續:加一組「缺席推論」題(結案後的延伸)
    61 [body]: [[Verification/2026-08-22_缺席推論探針題組]]。
    69 [body]: 3. **出題方法論修正**:`answer_expect` 要由「實跑出來的好答案」反推,★不能由出題者查一次
  0.000  Projects/收斂機制優化調研2026-08-14.md  []
    22 [KEY]: KEY:不推=更花俏聚合演算法(瓶頸在相關性非聚合層,否決席已覆蓋)/加輪加席(撞「前置加重一律拒」教義)
    43 [body]: - 穩健聚合:RoPoLL(arXiv 2606.30931)——看過,不推(見 summary)。
    124 [body]: > **★2026-09-01 三度重現+新外證(裁定不動)★**——世界治理掃描(governance/reports/world-governance-scan-2026-09…
    133 [body]: - **群體規模遞減**(F1 在 n=5-10 plateau)——與本調研原有的「不推加輪加席」同向,
  0.000  Projects/收斂閘殘餘估計降級_計劃.md  []
    20 [KEY]: KEY:★動機(r1 審計修正版)★=①估計器鑑別力≈0:殘餘<1.0 組下一輪 major+ 67%(14/21) vs 殘餘≥1.0 對照組 79%(49/62),p≈0.25…
  0.000  Projects/收斂閘漏項敏感度v2_計劃.md  []
    14 [fm]: - "[[Issues/探針沙盒能推到真遠端]]"
    27 [KEY]: KEY:★答案卷=r(N-1) 各席報告本身★,取代 v1「從 folded_set 反推」(該反推死於:帳上只存編排者自取助憶 id,抽查 40 筆僅 17 筆能在自家席報告找到…
    33 [KEY]: KEY:★隔離三件預註冊★——①執行環境照 scenario_probe 沙盒(拔 remote/pre-push 寫死 exit 1/假身分),不用 worktree,因 202…
    37 [KEY]: KEY:★天花板:答案卷本身也是 AI 產的★——r(N-1) 那些 finding 是當時席位寫的不是客觀真值,故 M1 精確說法是「今天的席位能不能重現當初席位抓到的漏項」,不…
    41 [fm:context]: context: v1 r1 五席(通才/邊界/整合/架構對齊/外家 Codex)33 條發現、4 個獨立 blocker,Enzo 2026-09-03 裁整份重寫。三個 blo…
    62 [body]: | 從帳上 `folded_set` 反推當初被折入的文字,機械刪掉 | 帳上只存編排者自取的助憶 id(`R1`、`refcheck重造`),抽查 40 筆僅 17 筆能在自家席…
    65 [body]: | 「隔離副本」四個字帶過 | 本專案 2026-08-23 出過探針副本推上真遠端的事故;且重跑沿用原迴圈名會被四個讀取端當同一迴圈延續、卷證目錄同名可能覆寫原始快照 | 隔離三…
    87 [body]: ## ★這不是重推被停的案子,也不是第二套 replay★
    … 還有 5 處
  0.000  Projects/檔案測試依賴地圖_計劃.md  []
    14 [KEY]: KEY:目標——改 code 時機械回答「哪些測試蓋這支檔」:`lumos testmap build` 三路訊號挖 file↔test 邊(naming/content/coch…
    25 [body]: TDD／code-loop 迴圈裡「改了 X，該跑哪些測試」目前靠人腦或全跑。`test-layers` 只到**棧層**粒度（碰 .cs → 跑 C# 層）；本案補**檔案**粒…
    93 [body]: - 改動檔在 map 有邊（src 端）→ 取其測試檔；**建議統一過存在性過濾：測試檔須在當前 ls-files（帶 `-c core.quotePath=false`——CJK…
    113 [body]: 5. affected：推薦降序；自證 conf=1.0+sources=["self"]；自證與邊去重一筆（sources 聯集）；**無有效邊之現存候選 src** 進 unc…
    126 [body]: 18. `rm` 未 commit 的測試檔（ls-files 仍列）不被推薦（∩ Path.exists）；
    133 [body]: 25. `rm` 後 mkdir 同名目錄 → 不推薦（is_file 擋）。（rc 矩陣類拆獨立 t_ 函式，防 expect_rc 首敗吞斷言）
    173 [body]: - [major 折入] ① `_cochange_mine` 四元組＋rules 值為 (conf,support) 二元組未解包（r2 只補了 load_config 的姊妹坑…
    178 [body]: - [major 折入] ① 測試檔判定句「完整檔名 vs stem」自相矛盾 → 拆三子句各自明定比對域（席1+席2）；② `foo_spec` 示例與綴詞表矛盾（會種回 r3 …
  0.000  Projects/檢核收緊五件_計劃.md  []
    77 [body]: - **`code-loop check`**(pre-push 呼叫,range 由 hook 傳入,不改 hook):tier=high 時,有效留痕=`status=pass…
    110 [body]: **已排除**:金流/對外送出/PII。**不可逆**:無。**遷移**:`_KNOWN_GATES` +4、`LIST_KEYS` +1;code-loop 留痕 JSON 新增…
    130 [body]: 2. **S3 的 pass↔push 綁定在跟 git 打架**:range 符號名 vs sha 永不相等(外家 s7)、amend 改 HEAD 即失效(外家 s6)、首推/…
    138 [body]: - **S3 重設計**:不綁 range;`code-loop check` 在 push 當下**自己算**外家窗(從 canary-log/dispatch),loop id…
    146 [body]: - **r3 panel(2026-08-21,五席同門+★兩席外家 gemini-3-flash(前提層/可實作性兩鏡頭)★,cap)**:blocker ~10 / major…
  0.000  Projects/檢索edit面真紅_計劃.md  []
    25 [body]: > 白話:語料前進後考卷量到了真實的推薦品質——不及格(0.684<0.70)。解剖發現病不在「三種排序訊號怎麼加權」(三種單獨看都一樣爛),而在**進場的候選就是錯的**:改檔案…
  0.000  Projects/檢索優化_計劃.md  []
    31 [fm]: ✗ 失效——「dyn_coef=0.55」及其理由「0.65 必看視野 19/30 砍過頭,0.55 視野最高(24/30)」:d5 已把係數改為 0.65,等於推翻本條的拒絕理由…
    64 [body]: 中段檢索三件套：search 相關性排序（BM25F）、相關節點推薦（圖分+詞彙融合）、impact hook 降噪（99 條→top-8 帶分數）。
    76 [body]: | 邊型加權 | v1 無型別邊；edge-type ablation 列評測第一批（Codex 案,Claude 案的直覺權重擱置）| 證據先於直覺;兩案都點名 Borodin …
    83 [body]: # Lumos 檢索與關聯推薦優化：設計草案
    143 [body]: ## 2. 相關推薦分數設計
    185 [body]: 相關推薦的 lexical query：
    200 [body]: 事故 trigger 與直接 code 引用是確切證據，不假裝是圖推薦：
    253 [body]: 原有 context 內容不變，尾端另列融合後推薦。
    … 還有 2 處
  0.000  Projects/檢索優化_調研.md  []
    18 [body]: 補「中段」：檢索排序（search 現為字母序零排序）、相關節點推薦（現為無權重 BFS）、主動提醒降噪（impact hook 實戰一次灌 50+ 節點）。deep-resear…
    28 [body]: ### 2. 相關節點推薦：BFS 距離衰減優先、PPR 備選（高信度但皆為外推）
    30 [body]: - **小圖反直覺實證（Borodin ACM TOIT 2005，對本 vault 規模最相關）**：千級節點圖上 in-degree 排序(61%)已勝 PageRank(48…
  0.000  Projects/每日治理wrapper活著沒_計劃.md  []
    13 [KEY]: KEY:★r1 打掉兩個前提★ ①「推播那條腿斷了」是錯的——它在暫停開關之前就跑而且真的會推,真正的問題是要連喊 14 天才通知、對「36 小時前死掉」來不及 ②把死人開關押在健…
    16 [KEY]: KEY:S2 ★主通道改成一支獨立的排程看門狗★(每小時讀健康檔;跟被監看的那支是兩個失敗域),健檢軟提醒只當第二通道且★必須接不會讓 issue 計數增加的那一支★(同程式裡已有…
    17 [KEY]: KEY:健檢「電腦剛從睡眠醒來兩小時內不喊看門狗」的豁免有測試釘住(2026-09-11):測試在健檢子程序的 PATH 最前面放一支假的 sysctl,平常回報很久以前就醒了、另…
    35 [body]: - **★「通知那條腿是斷的」是錯的★**:那支週報在暫停開關**之前**就執行,而且真的會推播。
    109 [body]: 實際卻用了會擋的那支,依慣例就近仿寫會在腳本死掉的當下連帶擋住全 repo 的推送。
    112 [body]: **推播那條**:既有的週報路徑可以用,但它要連喊 14 天才通知。
    170 [body]: - 不重新設計推播通道(它沒斷,只是慢;本案明文接受它當第三層)。
    190 [body]: 同型再犯,已記進 [[Issues/把自己的推論寫成repo明文寫過]]。
    … 還有 7 處
  0.000  Projects/派工編制資料化_計劃.md  []
    40 [body]: 以 (loop_kind, tier) 為鍵;loop_kind 由 loop id 前綴判**三值**(r1 外家席抓到二值規則會對歷史 id 載錯表噴無意義警告,升級為機械跳過…
    55 [body]: ★**code/standard(循序單 reviewer)v1 不入表、編制對帳不涵蓋**(r1 整合席 blocker,CLI 實測重現):既有 `cmd_loop_next`…
    66 [body]: - kind 判定用 loop id 前綴三值規則(同 S1;**per-command 訊息刻意不同**:loop next 無對帳可跳,indeterminate→roster…
    93 [body]: 2. `t_loop_next_roster`:design/standard 與 code/high 的 `loop next --json` 含 roster 欄且席組成正確;…
    117 [body]: - **pre-flight(2026-08-18,機械排乾,不算 loop findings)**:6 命中全修——①家族分類補大小寫不敏感規格(真帳有大寫樣本)②code/st…
  0.000  Projects/節點靜態先驗_調研.md  []
    23 [body]: **值得做，但不是「每節點手填三個數字」——是三個機械推導、可消融的 ranking features。**
    51 [body]: ## 手標 vs 機械推導（裁定）
    53 [body]: 特徵機械推導、語意由人標：人只負責既有 type/status/合約/邊;嚴禁手填 `authority: 0.83` 類浮點（GIGO/漂移/自我強化）;若需例外只開離散可 li…
  0.000  Projects/自主迴圈修理_計劃.md  []
    6 [KEY]: KEY:[S1] 失敗不丟件(trap 涵蓋全部早退點;原列原分放回不走 add_gaps;滿 3 次熔斷 covered+喊人)[S2] 選題修理(decay 冪等按日差、改簽名…
    43 [body]: - **[S3] 結局帳:結構化欄+trap 必記**(r1 推翻原「note 自由文字」方案——五席獨立打死:①成本抽取與結局是兩個獨立失敗維度,綁死則 PARSE_FAIL 時…
  0.000  Projects/規模影響判斷力假說.md  []
    70 [body]: **② 但書密度**（同上）：只有 L 組那席出現「信心中等」「僅供部署前確認」「此推論建立在⋯⋯假設上」。S 組兩席皆直述無但書。
    102 [body]: **為什麼夠難**：缺陷**完全不在 diff 裡**。推理鏈分散在快照的三個地方——
    138 [body]: ### 什麼結果會推翻假說
    140 [body]: - L 組 ③ 比率 **≤** S 組 → **假說不成立**，照實記，並且**永久停止**用它推動 gate。
    154 [body]: 不足以推廣到所有 spec 與所有模型，更**不足以單獨動 gate**。
  0.000  Projects/迴圈摩擦三修_計劃.md  []
    30 [body]: - **d2 前掃驗語意(治②)**:首輪前掃固定清單加第四類「spec 每句機械宣稱,開檔讀該段碼驗語意,不只驗存在」。**分流(r1 ext 席條 7:語意修正不得繞審計)**…
  0.000  Projects/送審前impact鏡頭機械化_計劃.md  []
    31 [body]: > ★下方「已排除的做法」裡「掛進 pitfalls 會慢 26 倍」的理由,**已於 2026-08-22 落成核對上線時作廢**(pre-push 每次推送本來就無條件跑一次 …
  0.000  Projects/連結缺失補全_計劃.md  []
    11 [KEY]: KEY:hook 紅燈殘餘 6 筆收尾——pre-flight 勘誤:僅 3 筆真斷鏈(B 群,D2 家族訊號全覆蓋)、3 筆=已 direct 被閾砍且保底未觸發(A 群);關鍵…
    33 [body]: → **關鍵推論(改寫本計劃範圍)**:B 群補鏈後變成「direct 但 L≈0」——照現行閾值照樣被砍,且同題有 direct 存活時保底不觸發 → **光補鏈救不動 held…
    61 [body]: - **pre-flight(2026-08-07,機械排乾)**:①前置實驗表 3/6 筆歸因錯——原腳本只掃正向訊號沒查「已否 direct」,live impact 反查揭穿…
  0.000  Projects/閘觸發帳統計_計劃.md  []
    45 [body]: ⚠ **不可混為一談**:`canary`/`signoff`/`kill` 不寫這本帳,各有自己的帳檔(canary 448 筆、signoff 8 筆、kill 帳檔不存在)。…
    219 [body]: ### 附帶裁定:`_KNOWN_GATES` 不算「造新機制」(編排者判,可被推翻)
    237 [body]: - **r2 panel(2026-08-19,三席:可實作性/推論效力/既有消費者;★仍為單一家族,外家席同樣派不出來★)**:blocker 1 / major 9 / min…
    240 [body]: - **2026-08-20 範圍裁定(Enzo,非審計發現)**:r2 的推論層三條(硬閘不寫帳／收斂指標量自報欄位／三種零分不出)打薄了本案價值主張。三選項攤給人裁——①砍成純…
  0.000  Projects/關係層主網_實作計畫.md  []
    33 [fm:context]: context: gate 三條件過二:輪有效+嚴重度收斂(blocker→blocker→全 minor,架構三輪未翻);統計殘餘未枯竭(r3 五條單席發現→推估 ~2.5 條未…
    163 [body]: - **E2 精化的相容窗**：M1 後「有 decision_refs 精化、無則退回節點級」雙軌並存——舊 Verification 未回填 decision_refs 前，E…
  0.000  Projects/驗證層去模型化_計劃.md  []
    22 [body]: > 緣起(2026-08-08,Enzo 裁定入帳):canary 的根本困境=「有抓到不代表認真,沒抓到不代表不認真;模型能力上升 → miss 率趨零 → 計分訊號飽和;整個機…
    32 [body]: - **SNR 前瞻層明文豁免(r1 折入,s3 blocker:勿誤殺已驗證資產)**:[[Projects/驗證層自證三件_計劃]] 的 canary_snr 前瞻層(固定題×…
    40 [body]: - **r1 Codex blocker 揭示**:[[Projects/panel收斂判準改革_計劃]] 自帶防浮動條款——「落地後不得接受論證型翻案;唯一翻案通道=累積 20 …
    42 [body]: - 待裁選項(攤給 Enzo):①具名推翻防浮動條款(理由=條款自身前提「canary 閘可信」已被非平穩性論證動搖,條款陷自我引用)②尊重條款,等 20 筆抽查帳自然裁 ③維持分…
  0.000  Systems/anchor-integrity.md  []
    70 [body]: **發生什麼**:折完一輪代碼審要推,推送前的閘擋我「把關檔改過沒簽名」。我簽了名、也把改動提交了——但只提交了知識庫那個資料夾,而**簽名檔放在治理資料夾底下**,沒進去。推送過…
    74 [body]: - 推送前的那道拿**工作目錄現在的樣子**驗:你剛簽完名,檔案就在那裡,所以綠。
    75 [body]: - CI 拿**已經推上去的內容**驗:簽名檔沒進版控,推上去的還是舊的,對不起來,所以紅。
    79 [body]: **怎麼修的**:推送前的閘多一道——簽名檔如果處在「改過但沒提交」的狀態就擋下,訊息直接講「沒提交」並給提交指令,不叫人再簽一次。守衛配的是**行為測試不是字串比對**:真的搭一…
    85 [body]: 四支補進清單(進場提醒、改檔前推合約、收工查圖譜、推送後回報 CI),並加一條:**清單裡的 hook 檔集合,必須等於實際存在的 hook 檔集合**。偷加一支會被點名。
  0.000  Systems/bound-tests-gate.md  []
    20 [KEY]: KEY:為什麼不是只用冒煙測試(同上,r1 實測推翻第一版):★大多數測試工具都分不出「測試不存在」與「測試通過」★——xcodebuild 三段 -only-testing 但方…
    22 [KEY]: KEY:★「擋」跟「講」是兩個地方★(2026-09-09 代碼審 r2 blocker):判定在 _codeloop_guard_verdict、但印給人看的在 cmd_code…
    27 [KEY]: KEY:(2026-09-09 表態閘起)pre-push 對每個分支 ref 都叫 check,低風險那一路帶 `--bound-tests-advisory`:紅了只印、寫帳、…
    33 [TEST]: TEST:t_bound_tests_gate(綠/紅/懸空/逃生門/env/no-config/壞設定檔/新分支首推 12 斷言(2026-08-30 機械重數訂正,原記十));…
    46 [body]: > 白話:改到相依功能,以前工具只會「點名」那些功能綁的測試,跑不跑靠自律。現在 pre-push 每次呼叫的 `code-loop check` 會把被點名的測試當場跑完:紅的、…
    51 [body]: - **高風險推送**:照舊藏在 `code-loop check` 裡,紅了**擋**。
    52 [body]: - **低風險推送**:pre-push 同一次 `code-loop check` 帶 `--bound-tests-advisory`(2026-09-09 表態閘起;之前是另…
    56 [body]: ★而且波及計算一次推送只算一次★:pre-push 算一份寫進暫存檔給這道閘(`bound-tests --from-json`)讀。
    … 還有 3 處
  0.000  Systems/canary-audit.md  []
    33 [KEY]: KEY:[2026-08-04 d4,design-loop 限定]canary 在 design-loop ★降級為觀測★(不再一票否決:missed 不作廢該席 finding…
    70 [KEY]: KEY:★2026-08-02 外部實測入帳:規模是主導混淆變數★——[Bigger Isn't Always Better](arXiv 2606.15689) 跨合成變異與真實…
    73 [fm]: - content: canary 定位收縮=當輪煙霧偵測器(同輪席間對照抓管線斷線);d4 的 code-loop 排除撤銷(降觀測擴及 code-loop);否決跨期統計/席位…
    75 [fm:context]: context: Enzo 非平穩性論證:caught≠認真/missed≠不認真;模型升→miss 趨零→計分飽和;模型換代/spec 各異/植針人拿捏=跨期統計站流沙。防浮動條…
    132 [body]: - **Anthropic〈Verbalizable representations and a global workspace in LLMs〉**(transformer-c…
  0.000  Systems/convergence-evidence-gate.md  []
    85 [body]: 故獨家發現必然也被折入(集合層推論,不靠 id 順序)。
  0.000  Systems/cross-family-audit.md  []
    23 [DEP]: DEP:governance/autonomous_loop/cross_audit.py｜orchestrator-prompt.md §2.5｜autonomous-loop.…
    85 [body]: - **qwen 也是 AI**:跨家族**降低**共同盲點 ≠ 消滅「AI 評 AI」回歸,只把回歸推遠(兩家族都漏才漏),非 oracle。
  0.000  Systems/design-loop.md  []
    37 [KEY]: KEY:[2026-09-08 條款綁定]為什麼加在閘不是 skill 散文:接手席/架構席/簡化席三席獨立查證「設計審出口寫一句流程規則」零約束,跟 spec-trace 33 …
    47 [KEY]: KEY:[2026-08-04 重設計]★收斂改走處置閘★(--disposal;完整設計=[[Projects/design-loop重設計]],r1 panel 自審收斂+人裁…
    50 [KEY]: KEY:[2026-07-18]S5 跨家族落地(見[[Projects/code階段強化_計劃]])——辯方預設 Codex(成本中性替換,d4 合規;不可用退 opus 註記)…
    59 [FLOW]: FLOW:brainstorming產spec→[trivial?跳並註明]→前置排乾(refcheck機械核對spec→repo指涉+pitfalls --check補實務隱患節…
    82 [fm:why_chosen]: why_chosen: 由 N 機械推導 a→b→c→d→a 輪替,免狀態、可從 loop_status 輪歷史重現;canary 校準鐵則=「認真審抓得到但不一眼看穿」(太細不公…
    103 [fm]: - content: code-loop 正確性鏡頭派工措辭升級(2026-08-28):名詞清單(bug/邊界/資源/例外/冪等/併發)改成帶例子的問句+明講排除(風格與架構歸架…
    105 [fm:context]: context: 先問世界(WebSearch 2026-08):業界最佳實踐兩獨立來源(awesome-reviewers『規則+為什麼+例子』、Cloudflare/DEV『告…
  0.000  Systems/guard-kill.md  []
    17 [KEY]: KEY:宣告式壞法(人寫,從業務行為推導非實作反轉;繞開等價變異不可判定)｜run_cmd由config宣告(platforms.X.run_cmd/legacy test.run…
  0.000  Systems/judge-perturbation-stability.md  []
    16 [DEP]: DEP:governance/autonomous-loop.sh(RESIDUAL 清單)｜confidence_report.py｜judge-severity-gate(被它…
  0.000  Systems/lint-declaration-health.md  []
    19 [KEY]: KEY:★2026-08-26 接線收口(plan:[[Projects/lint接線收口_計劃]])★:①靜態層併入 doctor 兌現——[F] 檢共用 _lint_load_…
  0.000  Systems/linter精選目錄.md  []
    51 [body]: 推薦組合:NetAnalyzers(基線) + StyleCop(風格) + Roslynator(簡化) + 選 SonarAnalyzer(深度)。
    93 [body]: - **flutter_lints**（官方推薦基線,Effective Dart 對齊）→ 進階嚴格版 **very_good_analysis**（企業級,強制 const/顯…
  0.000  Systems/lumos-cli-lifecycle.md  []
    61 [fm]: - content: Citrus_Lumos_Full 鏡像與本工具鏈分家:本 repo 不再推送鏡像、不再視其為同步目標;鏡像自帶安裝入口與更新路線,獨立演進
    63 [fm:context]: context: 鏡像原為本 repo 單向同步的複本(remote 名 Full),其安裝入口(get.sh/get.ps1/README/ONBOARDING/ARCHITEC…
    64 [fm:why_chosen]: why_chosen: Enzo 2026-08-20 明示「不再往 Full 推、讓它自足、與本工具鏈分離」。考慮過的替代:①維持單向同步、鏡像端改動每次手動重打(靠人記得,零守…
    69 [fm:context]: context: 精簡版與完整版鏡像的處境不同:交付庫本來就設計成獨立包(安裝/更新/卸載三條路徑只認自己,2026-08-20 實查零上游引用),更新路線早已自足;耦合點只有一處…
    70 [★INVARIANT★]: why_chosen: Enzo 2026-08-20 在兩案中裁 A(只停手不動刀)。考慮過的替代:①維持人工同步(耦合續存,靠人記得,已知會落後)②凍結不刪(採用):slim/…
  0.000  Systems/pitfalls-code-loop.md  []
    25 [KEY]: KEY:[2026-08-05]pitfalls --diff 排除 governance/review-reports/ 路徑——歸檔證物(席報告/canary 快照 .patc…
    32 [FLOW]: FLOW:pitfalls spec 模式(剝除對齊 assess_spec+防呆→掃 PITFALL_CLASSES 四類→印通用 4 問(3 固定+1 風險類反問,2026-0…
    51 [fm:context]: context: 使用者質疑代碼 canary 污染風險比 spec 嚴重(假 hunk 改變語意、reviewer 推導衍生幻影 findings)
    55 [fm]: - content: code-loop check 在 marker 檔不在時退讀 tracked 的治理帳(docs/.governance-log.jsonl 最後一筆該分支…
    59 [fm]: - content: code-loop 擋推鏈(pre-push 與 CI 的 code-loop gate)恆以 --no-lint 跑 pitfalls——lint SARI…
    62 [fm:why_chosen]: why_chosen: 速度(pre-push 已 11 分鐘)+lint 告警屬審查品質面非擋推面;[F] 檢守宣告健康、pitfalls 帶 lint 屬手動加跑
  0.000  Systems/retrieval-ranking.md  []
    41 [fm]: - 檢索排序與關聯推薦
    43 [body]: # retrieval-ranking（檢索排序與關聯推薦 v1）
    50 [body]: - `lumos context <節點> --recommend [--top 8] [--min-score 0.20] [--json]` — 圖分×詞彙融合推薦+姐妹折疊。
  0.000  Systems/slim-gen-生成器.md  []
    48 [body]: > **仍在 repo 裡、測試仍在跑**，但★不再發布★——沒有自動發布路徑，人工推送也已停。
  0.000  Systems/slim-get-一行安裝.md  []
    15 [★INVARIANT★]: KEY:★INVARIANT★ 三支 `.ps1` 必須是 ★ASCII-only 且不加 BOM★(2026-08-03 Windows 真機★回歸★測試推翻了前一版的「必須加 …
    51 [body]: > **仍在 repo 裡、測試仍在跑**，但★不再發布★——沒有自動發布路徑，人工推送也已停。
  0.000  Systems/slim-install-安裝器.md  []
    17 [KEY]: KEY:★只動 $HOME 與專案 CLAUDE.md 這一份檔案,不碰專案其餘任何東西★(★2026-07-31 使用者裁定推翻原「不注入/更新任何 CLAUDE.md」的裁定,…
    25 [KEY]: KEY:★install 的例外語意與 [[Systems/slim-uninstall-一行卸載]] 刻意相反,別「好心統一」(2026-08-02 補記)★——uninstal…
    68 [body]: > **仍在 repo 裡、測試仍在跑**，但★不再發布★——沒有自動發布路徑，人工推送也已停。
  0.000  Systems/slim-readme.md  []
    51 [body]: > **仍在 repo 裡、測試仍在跑**，但★不再發布★——沒有自動發布路徑，人工推送也已停。
    60 [body]: ★2026-07-31 Task 9(裁定第三次變更)★:〈會不會動我專案的 CLAUDE.md〉整節重寫——不再只是「附加一段教學句」,而是「有完整版紀律區塊就整段策展取代,原地…
  0.000  Systems/slim-scan-掃描器.md  []
    16 [★DEBT★]: KEY:★DEBT★(2026-08-01 代碼審 r6 方法論收穫)★掃描器只認「指令名」,認不得「路徑」★——`Projects/xxx_計劃`、`governance/gol…
    41 [body]: > **仍在 repo 裡、測試仍在跑**，但★不再發布★——沒有自動發布路徑，人工推送也已停。
  0.000  Systems/slim-skill-修剪.md  []
    33 [body]: > **仍在 repo 裡、測試仍在跑**，但★不再發布★——沒有自動發布路徑，人工推送也已停。
  0.000  Systems/外部對照-code衍生wiki.md  []
    77 [body]: openwiki 每條優勢都來自同一個賭注：「文件應是 code 的衍生投影、可丟可重生」。**代價是它裝不下任何 code 裡沒有的東西**——沒有「這條是合約、改＝breaki…
    91 [★INVARIANT★]: - **誠實不吹過頭**：lumos 真正被 *驗證* 的只有綁 `[test:]` 的 ★INVARIANT★ 子集;其餘 prose **也是「信作者」**(懶/錯的人一樣寫得…
    99 [body]: - 未親跑 openwiki 生成一份 wiki 實測其誤差率（結論建立在讀 prompt.ts + test/ 結構 + README 機制）；「無輸出 oracle」是**機制…
  0.000  Systems/效能檢核目錄.md  []
    21 [KEY]: KEY:.NET 後端——五類(2026-07-27 補④):⓪互不依賴等待必須並行(idioms R1 頭號)+大結果集分頁下推(R11);①阻塞異步(.Result/.Wait…
    26 [KEY]: KEY:時機點設計(Vercel 實證:靠模型自己想起要查規範,56% 會跳過→機制推送不靠自覺,同 impact hook 哲學)——①動手前:impact hook 按棧注入效…
    27 [KEY]: KEY:[2026-07-19]三時機已落地(見[[Projects/pitfalls棧別效能追問_計劃]])——①pitfalls --diff 命中棧附檢核問(manifest…
    52 [body]: | state read 能否延遲(lambda 包裝) | 人判提問 | 把讀往下推,縮小重組範圍 |
    78 [body]: | **大結果集分頁/下推** | 人判提問(csharp-idioms R11) | 過濾聚合下推到資料層,別撈全表進記憶體處理 |
    145 [body]: | ③推送前 | **表態閘**(2026-09-09 機械化,[[Systems/棧別提問表態閘]]) | diff 增刪行觸發到的題(適用題),每題 `lumos code-l…
    165 [body]: | `cs-data` | cs | 查詢有沒有 N+1/SELECT * 進大表?大結果集有分頁、過濾聚合下推到… | `\bSELECT\b`、`FromSql`、`\.Que…
  0.000  Systems/診斷迴圈先行.md  []
    18 [KEY]: KEY:★假說能重現出「更嚴重」的症狀,不代表它是眼前這個症狀的原因★——收斂條件是「解釋得了觀察到的那幾條」,不是「造得出一堆紅」。2026-08-01 實例:押 GIT_DIR…
    82 [body]: 2026-08-01：pre-push 測試閘紅三條，我押 `GIT_DIR` 環境洩漏；實測把 `GIT_DIR` 指向本 repo，紅的條數暴增到 **65**，機制完全講得通…
  0.000  Verification/2026-06-26_native-windows-support_真機.md  []
    47 [body]: - **連驗證工具本身都要驗**(marker 探針一度因 `from __future__` 順序壞掉誤判)、**在錯的 shell 手動跑會給假綠**(PowerShell 驗…
  0.000  Verification/2026-07-04_pitfalls-code-loop.md  []
    12 [fm:valid_under]: valid_under: cmd_pitfalls 三模式(PITFALL_CLASSES 詞表+剝除對齊 assess_spec 含防呆+--check 節檢查+--diff p…
    16 [VERIFY]: VERIFY:行號推導人工+機器雙驗;pattern 去重疊(SELECT/寫入)證第6條非死碼;三道防污染語意經 review 逐條確認;gate G2 段一字未動比對
  0.000  Verification/2026-07-05_code-loop必用守衛.md  []
    44 [body]: - **非 oracle**:Stop 注入可被無視、pre-push 可 `--no-verify`。關得掉「忘了看」(Stop 推到眼前)、「隨手漏」(pre-push 硬擋)…
  0.000  Verification/2026-07-10_檢索排序v1.md  []
    4 [fm:feature]: feature: 檢索排序與關聯推薦 v1(四階段 dormant CLI)
    37 [body]: - 本 vault：「殺傷力」排序正確;guard-kill 推薦=計劃/驗證/合約鏈;impact scripts/lumos 50+→固定席3+top8。
    38 [body]: - Landmark（235 篇）：「票券/HMAC」排序正確（正主節點分數擠近——評測調參實據）;票券系統推薦=核銷冪等/POS-API/滿額贈。
  0.000  Verification/2026-07-11_hook面v1.1轉正.md  []
    24 [body]: 推播面（impact ranked）從 goldset FAIL（P@8=.509）修到 §6 七盞全綠 PASS 並接上 PreToolUse hook。
    38 [body]: - **應試 vs 誠實**：0.65 係數同樣 P@8≈.71 且 p95=9,但「必看(標2)在實際推播視野(固定席+前8)」19/30——砍到需要看的東西;0.55 為 24…
    75 [body]: **實質影響(比數字本身重要)**:v1.1 當初**明確拒絕** 0.65,理由就是「砍到需要看的東西」(24/30→19/30)。v1.2 採用了 0.65,等於**推翻了那個…
    92 [body]: 亦即本篇原句「而非更兇的閾值」把唯一對症的路排除了,而它推薦的替代路後來全數落空。**此為典型折入漂移在「建議」層而非「數字」層的變形——數字錯了會被重跑抓到,建議錯了不會。**
  0.000  Verification/2026-07-14_relguard_E1失效背書.md  []
    45 [body]: 只查 frontmatter 可判的失效背書（status=stale/fail）；純語意矛盾仍留 AI 交叉審。E1 是關係層守衛四檢（E1-E4）最先、免前置的一條；E2（建在…
  0.000  Verification/2026-07-14_relguard_E2建在被推翻決策上.md  []
    4 [fm:feature]: feature: doctor Check E2 建在被推翻決策上 + P1 supersede 自動補 ended/bump updated(關係層守衛 phase-2,[S7]…
    9 [fm]: - "時序法為啟發:來源 updated < 決策 ended 才報、warn_soft 不擋;無 ended 的被推翻決策跳過(P1 起新翻案自動補 ended)"
    23 [body]: # 驗證：doctor Check E2 建在被推翻決策上（+ P1）
    25 [body]: 關係層傳播守衛 phase-2（計劃 [S7] + 前置 [P1]）落地：補網再添一道**時序關係檢查**，把 Check 4 的「結案後有較新驗證」時序 proxy 推進到「**…
    28 [body]: - `scripts/lumos` cmd_doctor：新增 `Check E2`（放 Check E1 之後、Check H 之前）。**內聯 typed 反查**（掃全圖節點…
    39 [body]: | 真圖 `lumos doctor` | E2 乾淨「無落後邊」（2 條被推翻決策的來源都已跟上，0 假陽性）；全圖 0 issues | ✅ |
  0.000  Verification/2026-07-15_主網M1_決策穩定ID.md  []
    15 [fm]: - "decision_refs 回填推進後(E3/E2 精化的實際覆蓋率變化)"
  0.000  Verification/2026-07-15_主網M2_typed-edge索引.md  []
    33 [body]: - [[Verification/2026-07-14_relguard_E2建在被推翻決策上]] 的 `revalidate_when`「P0 若落地→E2 改用共用 index…
  0.000  Verification/2026-07-16_fromscratch守衛M1_CheckJ.md  []
    15 [VERIFY]: VERIFY:M1 Check J(regen 重生來源守衛)落地——J-a 拒發明合約(regen 節點的 INVARIANT 標記行需 [src:]/[git:] 意圖證據,與…
    17 [KEY]: KEY:雙報消歧 predicate 落地——regen 節點「推測前綴+INVARIANT 標記」同行時恰一則 J 專屬訊息(generic 位置錯誤 continue 跳過);…
    28 [body]: - **t_check_j_regen（21 格）**：set regen 白名單迴歸 rc0、非 regen 節點不受影響、J-a 兩態、J-b 四態、J-c 假頂層目錄/越界/…
  0.000  Verification/2026-07-16_replay校準baseline_v0.md  []
    16 [KEY]: KEY:三結論——①haiku 剖面=grep 可得能抓(白名單/詞不存在),推理/交叉對照型全滅→pre-flight 的 haiku 只配機械清單,語意審最低配 sonnet …
    40 [body]: ### 處置(不是把日期往後推就算了)
    61 [body]: 1. **haiku=機械清單專用**:grep 可得(白名單缺欄/函式名不存在)能抓;需推理或交叉對照(正則隱形/靜默放行/字母撞名)全滅。pre-flight cascade …
    63 [body]: 3. **洩漏效應分層**:sonnet 先獨立推導、拿 code 演化當驗算並主動揭露;haiku 直接抄。釘住對 haiku 反而提升(答案卡拿走後 grep 到的就是真缺陷態…
  0.000  Verification/2026-07-22_prepush範圍修法落地.md  []
    9 [fm]: - "動 scripts/hooks/pre-push 的 stdin/範圍推導/逐 ref 迴圈"
    19 [KEY]: KEY:盲區實測堵住——main-direct 高風險直推 main(舊 hook mb==HEAD 靜默放行)現走 remote_sha..local_sha 增量判 high→…
    29 [body]: - **盲區實堵**：main-direct 高風險直推 main 現 rc1 擋（舊 hook merge-base==HEAD 靜默放行）。
  0.000  Verification/2026-07-25_bootstrap一鍵對稱.md  []
    23 [KEY]: KEY:已知殘留(std 照出既有病,另立)=F4 半成品 vault 無自癒/F9 docs/knowledge與standalone 佈局 slug 反推錯/F10 Windo…
  0.000  Verification/2026-07-29_CI回流閉環v1落地.md  []
    55 [body]: **修法＝把守衛面推廣**：新增 `t_docs_enumeration_drift`，把「禁止手寫數字／列舉」從指令數擴到三類機械可推導事實——
    60 [body]: **通則入帳**：凡文件宣稱一個「可從碼機械推導的清單或數字」，就該有一條這樣的測試——否則它遲早漂移，而且是靠人發現。
    86 [body]: - 值域守衛範圍加上 `Systems/guard-kill.md`（圖譜節點本身），態數宣稱也改為從碼推導；同時清掉 code 裡
  0.000  Verification/2026-07-31_slim-uninstall步驟獨立化與manifest基準修復.md  []
    19 [body]: ## 缺陷(端到端實測重現,非推論)
  0.000  Verification/2026-08-01_slim-install注入目標守衛.md  []
    39 [body]: 派無脈絡獨立 agent(sonnet)審計五問 rubric,第 4 問(可證偽性)要求**真的去竄改一份暫存副本**驗證綁定測試會不會翻紅,不能只用推理帶過。結果:
  0.000  Verification/2026-08-01_slim-windows兩缺陷修復.md  []
    61 [body]: **★誠實限制,不包裝成已解決★**:這台機器沒有 PowerShell,無法驗證這段語意——推理上這個改法不會再主動關掉呼叫端視窗,但 `exit` 在 PowerShell 各…
  0.000  Verification/2026-08-02_slim三缺陷修復_實驗產出.md  []
    125 [body]: - **已重新交付**：`github.com/citrus-android-developer/Citrus_Lumos` main = `9fbc5a6`，tag **`v1.…
  0.000  Verification/2026-08-03_Windows回歸測試三缺陷.md  []
    22 [VERIFY]: VERIFY:v1.4 的真機回歸測試回報 3 條(1 個是 v1.4 自己造成的),全部修復並綁測試。★推翻了 v1.4 的 ①BOM 修法★
    25 [KEY]: KEY:★推翻了本專案長期掛著的「這台機器沒有 PowerShell,驗不了」★:那句被當成免驗證通行證寫進多個節點,但 `$Args` 遮蔽與 BOM 撞 iex 都是★語言層★…
    74 [body]: ## ★★推翻「這台機器沒有 PowerShell」這個免驗證通行證★★
  0.000  Verification/2026-08-08_canary型別描述報表.md  []
    35 [body]: ## 判讀(描述性,不做推論)
  0.000  Verification/2026-08-08_風險類反問v1落地.md  []
    22 [body]: ## 設計脈絡(Enzo 一連串追問推導)
  0.000  Verification/2026-08-08_驗證層去模型化落地.md  []
    18 [body]: - **S2b 閘切換**:code-loop 收斂 A 案(K=2)→ `loop status --disposal`(四條可重算合取);canary 降觀測擴及 code-l…
    37 [body]: - 翻案先例已立:防浮動條款可被業主具名論證推翻(signoff 留痕)——是特性也是風險,後續翻案須同等具名。
  0.000  Verification/2026-08-11_AndroidUI工作流A段落地.md  []
    49 [body]: 1. **Task 2 的 implementer 在主 repo（main）commit 而非 worktree**——已 cherry-pick 到 `feat/android…
  0.000  Verification/2026-08-11_delguard落地.md  []
    36 [body]: - **第二幕（aff2329 假同步形狀重演）**：vault 節點只掛 `verified_by` 連結、被推翻的舊敘述不改，與 code 刪除同 commit → delgu…
  0.000  Verification/2026-08-14_跨session傳訊互動視窗實測.md  []
    18 [KEY]: KEY:★關鍵區辨★本測推翻不了也不牴觸[[Verification/2026-08-14_子代理續談headless實測]]的互動限制——兩者是不同機制:「續問已結束的子代理」靠…
    36 [body]: - 這與子代理續談是兩套機制，先前的「互動不可用」不可外推到本場景。
  0.000  Verification/2026-08-19_精簡版update指令落地.md  []
    34 [body]: - `scripts/slim-scan.py` KEEP += update;發行 repo 同步推 31533ec(dist↔發行 diff 歸零;rsync --delete…
    42 [body]: 1 blocker+2 minor 全折:①真安裝器測試原讀 repo dist/(gitignore,CI 乾淨簽出必炸、本機假綠)→改為現生隔離交付包;②pull 訊息改印首行…
  0.000  Verification/2026-08-22_guard-kill首次真跑.md  []
    29 [body]: - 壞法是人宣告的,沒有自動生成;這是設計如此(從業務行為推導,不從實作反轉)。
  0.000  Verification/2026-08-22_受波及合約測試真跑閘落地.md  []
    20 [body]: > 那一案改了三函式的簽名與行為(加 payload / advisory、帳的類別拆細、首推換主線起點),
    38 [body]: blocker 1(設定檔壞會炸成假 rc1)+ major 2(新分支首推整庫當 diff;懸空判紅)+ minor 1(stash 殘留)。折 3、不折 1 附理由:懸空/偽證…
  0.000  Verification/2026-08-22_檢索英文單複數消融.md  []
    43 [body]: **search 面完全沒有受益,edit 面掉了。** 推測原因:去尾 s 產生的詞進了索引,
    44 [body]: 稀釋精準匹配;edit 面(impact hook 推薦)吃檔名/路徑匹配較重,對噪音更敏感。
  0.000  Verification/2026-08-22_評測尺三修.md  []
    34 [body]: 明文拒過(一改尺既有門檻與整本 history 全失效)。★複查後維持,沒有推翻的新理由。★
    59 [body]: **兩個指標抓兩種壞**:`P@8` 抓「推了一堆垃圾」,must-see 召回抓「該推的沒推」。
  0.000  Verification/2026-08-23_雙評審三版對照.md  []
    72 [body]: ★★同日第二輪推翻了這個初判——見下面的訂正節。真正的變數是「有沒有讀」,不是席位。★★
    74 [body]: ## ★同日訂正:發現三的結論被第二輪推翻——不是「A 席偏嚴」,是「沒讀就判會偏★
    126 [body]: - **「A 席偏嚴」是推論,不是定論**。另一種解釋:B 席(兩家都是)有「給分寬鬆」的
  0.000  Verification/2026-08-25_probe輪退場與多席路由統一落地.md  []
    49 [body]: 這輪是 3 席的中等分級,不是 4–5 席的高分級。**載體彙總在 5 席規模下操不操作得動,到今天仍然沒有真實案例。**不拿 3 席的順利去推論 5 席也順利——席數變多時要對帳…
  0.000  Verification/2026-08-27_關係語意腐爛守衛_G1解鎖即活.md  []
    5 [fm:valid_under]: valid_under: "補網 Check E1(失效背書)/E2(建在被推翻決策上)/E3(意圖鏈斷義)/E4(翻案連鎖跟進)+主網 cascade(supersede→typ…
    17 [body]: 地基第 4 批 G2=關係語意腐爛守衛(調研頭號腐爛:別篇決策推翻本篇前提)。調研判「卡點=G1」。查證:守衛整套機制早已建好——
    19 [body]: - 補網(routine,doctor 每次跑):Check E1 失效背書 / E2 建在被推翻決策上(節點級時序 proxy+decision_refs 精化)/ E3 意圖鏈…
    30 [body]: - 守衛只覆蓋**有結構邊/有 decision_refs** 的語意腐爛(E2 靠 typed 邊、E3 靠 decision_refs)。★無結構邊的純語意矛盾(A 的前提被 …
  0.000  Verification/2026-09-03_席間覆蓋率離線量測.md  []
    5 [fm:valid_under]: valid_under: 這批數字成立的前提有三個——①資料只涵蓋 2026-07-10～08-23 的 102 輪(capture_counts 之後沒人再填);②那段時間的席位…
    6 [fm:revalidate_when]: revalidate_when: 出現下列任一即重跑 governance/eval/seat-coverage/recount.py 並更新本篇——①有新的多席輪補填了 capt…
    18 [KEY]: KEY:刻意不做順序假設——capture_counts 是無 id 計數陣列,對不到 findings_set 的 id;改用「零放行輪」的集合層推論繞過(v1/v2 兩份計劃就…
    25 [KEY]: KEY:誠實界線——capture_counts 是編排者手填(同一層天花板,緩解=兩個母體結果一致);「獨家」直接量到的是席間分歧,等於真漏抓靠零放行推論不是直接證據;資料只到 …
    68 [body]: `capture_counts` 是**無 id 的計數陣列**,無法直接對到 `findings_set` 的 id。★這裡刻意不做順序假設★(v1/v2 兩份計劃就是死在這種假…
    93 [body]: - v1:r1 五席 4 blocker(核心算子「從 `folded_set` 反推被折入的文字」在資料層不存在)→ Enzo 裁整份重寫。
    120 [body]: - **「獨家」直接量到的是席間分歧**;它等於「真漏抓」,靠的是「零放行輪」那條集合推論,★不是直接證據★。若日後出現放行率明顯上升的時期,這條推論要重驗。
  0.000  Verification/2026-09-03_派工攔截點實測.md  []
    15 [KEY]: KEY:★這推翻 [[Projects/impact鏡頭機械化_計劃]] 2026-08-29 停案的死因★——該案 d2 逐字寫「派工發生在編排者的 agent 呼叫裡,沒有任何…
    16 [KEY]: KEY:★追測(同日):hook 不只能擋,還能改寫派工詞★——hookSpecificOutput.updatedInput 對派子代理有效,實測子代理原封不動列出只存在於注入文…
    21 [KEY]: KEY:★只證明做得到,沒證明該做★——該停案另有 2026-08-02 的獨立裁定(擋 high 抓不到 standard、擋 standard 逼人繞過)未被本篇推翻,重開後仍…
    25 [fm]: - "[[Issues/推新分支時風險分級拿空樹當起點]]"
    76 [body]: 驗證器檔案被動過就擋推送)。這一條是硬約束,不是提醒。
    81 [body]: 於是 ★該案唯一沒被推翻的那條裁定(2026-08-02:擋 high 抓不到 standard、擋 standard 逼人繞過)
    82 [body]: 整條不適用★——不擋就沒有繞過壓力。同日 [[Issues/推新分支時風險分級拿空樹當起點]] 量到的
    91 [body]: 結論:`additionalContext` 只到派工者,不進子代理;**要把內容送進子代理,`updatedInput` 是唯一路徑**——本篇上一節「未實測、是推論」那句自此改…
    … 還有 2 處
  0.000  Verification/2026-09-04_Codex完全支援S3量測驗收.md  []
    18 [body]: > 白話:第三階段要證明兩支量測工具讀得懂 Codex——利用率重算能從 Codex 逐字稿數出「hook 推了幾次、推完有沒有去讀」,情境探針能用 Codex 當被測者跑同一批題…
  0.000  Verification/2026-09-09_接入靜默失效七項落地.md  []
    18 [VERIFY]: VERIFY:★最重的那條在代碼審 r1 被打掉重做,現在才是真的擋★——第一版只把狀態換成「無法確認測試真的跑過」印到 stderr,而真正決定推送擋不擋的那支只認紅,所以「假綠…
    19 [VERIFY]: VERIFY:★判準也整條換掉——實測推翻了原設計的前提★:原本假設「測試工具對不存在的測試名會回非零」,實測 dotnet 9.0.117(--filter 對不到回 0)、je…
    24 [VERIFY]: VERIFY:★代碼審 r2 又打掉一次:「擋」跟「講」是兩個地方★——判定併進去了,但印給人看的那支只認 green/red,低風險推送在假綠上一個字都不印就放行(實測輸出只有「…
    44 [body]: | 零覆蓋出聲 | ✅ | 四種來源各一句人話，訊息帶推送前腳本認得的關鍵字 |
    45 [body]: | **假綠改成擋** | ✅（代碼審後重做） | 端到端兩個方向：證不出跑過 → 拒絕報綠**而且真的擋下推送**；輸出說得出跑了幾支 → 照樣報綠 |
    64 [body]: - **「假綠改成擋」那句話當時是假的**。我把狀態從「綠」換成「無法確認測試真的跑過」，也印了訊息——但真正決定推送擋不擋的那支只認「紅」，這個新狀態它根本沒在看。結果是：訊息換…
    90 [body]: 而那支只認「綠」和「紅」。結果：低風險推送碰到假綠時，輸出只有一行「✅ OK——可以推」，
  0.000  Verification/2026-09-11_skills健檢.md  []
    35 [body]: - 共同:說明文字都在 1024 字元內;入口頁都遠低於 500 行;長參考檔除上面那支範本外都有目錄;沒有「一步步思考 / 再檢查一遍」這類教推理的句子。
    56 [body]: - 情境探針前後對照(同 6 題、每題 2 次;改寫前基線 → 改寫後):代碼審推送前 2/2→2/2、設計審下一步 0/2→0/2、CI 查詢 2/2→2/2、設計寫進計劃 0/…
  0.000  Verification/2026-09-11_代碼審資安席落地.md  []
    36 [body]: - 全套測試沒跑(約 8 分鐘,留給推送前的閘);另有兩支已知與本案無關的紅:截圖基準那批未提交的卷證腳本、Mac 剛醒兩小時內必紅的看門狗測試。

(共 275 篇候選,照相關性排序;想照檔名排加 --legacy)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "sed -n '1,240p' /Users/enzo/.agents/skills/lumos-project-notes/SKILL.md"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
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
**每支檔有家**(2026-09-11,提交前與推送前擋新違規,舊帳看 `lumos doctor` 的 S8–S10;單源 [[Projects/每支檔有家_計劃]]):① 每支程式檔要有一篇管它的 Systems 節點(about_code 列了它);新開用 `lumos new system <名> --code <檔> … --responsibility "<負責什麼、不負責什麼>"`,一個模組一篇 ② 節點只准用反引號寫自己家的檔,別人的檔寫成那支檔的家的 `[[連結]]`(寫了別人的檔名,改那支檔時就推出這篇,這就是節點長成一篇包全部的成因) ③ 改了程式要寫說明,寫進改到那支檔的家;要往圖譜寫說明,改到的每支檔都得先有家 ④ 新開的節點一律寫負責範圍,舊篇管超過 3 支檔也要 ⑤ 計劃寫 `lands_in`(現況落在哪幾篇,或新開哪一篇),設計審出口會看。
**標籤**:`type/` `status/`(值域 lint 硬擋)、`priority/` P0–P3、`scope/`(一篇一個主類;值域專案在 `.lumos/config.json` 宣告了 lint 才唸;feature/ area/ 已停用)、`risk/` 金流‧對外送出‧不可逆‧守衛面、`flag/`。

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

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "sed -n '1,260p' /Users/enzo/.agents/skills/lumos-design-loop/SKILL.md"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
---
name: lumos-design-loop
description: 設計 spec 或計劃寫完、要進實作之前的審查迴圈——讓幾個不知道脈絡的審查員輪流挑毛病,每輪用 lumos loop next 派席、lumos canary record 記帳、lumos loop status --disposal 判過不過——散文 spec 走處置閘,一輪裡每個發現都折掉或附理由接受就放行實作;跑滿上限沒過就攤給人裁。觸發:剛寫完 spec/設計/計劃筆記準備動手、有人問「這份設計審過沒」、指名 design loop 或對抗審計。小改動可跳過但要在計劃筆記註明。指令速查在 lumos-project-notes 的 commands/05-設計審查迴圈.md。
---
# 設計審查迴圈——一頁手冊

白話:一份設計寫完、動手實作之前,讓幾個不知道脈絡的審查員輪流挑毛病。每輪派人、收報告、機械驗報告、把真問題折回設計、記帳、問閘過了沒。**散文 spec 的收斂判準=處置閘:一輪裡每個發現都折掉或附理由接受,這輪就算收斂**(「連續兩輪乾淨」是舊 panel 帳,只剩已定錨 panel 帳的舊迴圈在用,對散文審計不適用;code-loop 現制也走處置閘);跑滿上限沒過就攤給人裁。**你(主對話)負責派人和判讀,lumos 只出記帳與判閘的指令,不會自己派 agent。**

指令速查:`lumos-project-notes` 的 `commands/05-設計審查迴圈.md`。派工的完整 prompt 在同目錄 `templates.md`(派工以它為準)。
每條規則的由來與事故見 `reference.md`〈入口頁舊版全文(去時效前)〉。

## 什麼時候用、什麼時候跳
- **用**:spec / 設計 / 計劃筆記寫完、要進實作前。被審的唯一真檔 = 圖譜計劃筆記 `Projects/<主題>_計劃.md`;loop 編號 = 檔名去 `_計劃` 轉 kebab。
- **跳**:改錯字、一行、純機械(改名、補欄位)——可跳,但在 commit 或計劃筆記寫一句為什麼跳。
- **light(單人、最多兩輪)**:小而不瑣碎的 spec 才准(暫用值:預估實作改動 ≲50 行且孤立);碰金流 / 對外寄送 / 正式環境不可逆 / 守衛面、動到 ★INVARIANT★、演算法密集、改動偏大——任一命中就走完整迴圈。忘了判就走完整(寧多不少)。這道判斷目前靠你自己誠實,沒有機械擋。**light 輪只要冒出存活 ≥major → 算 light 誤判,立刻升級**:開新編號(原編號加 `-std`)走完整迴圈,乾淨輪不洗回來。
- 進場前一行 `lumos loop next <編號> --tier standard|high|light --orchestrator claude|codex --spec <計劃.md>`,第一次一定帶 `--tier` 與 `--orchestrator`(誰在編排;外家席=不是編排者那一家),之後它會吐「第幾輪、幾個人、派誰、記帳範本」。首輪還會印「主題既有節點」:近名或已翻案的先讀它的 decisions 再開案。

## 一輪怎麼跑(照這個順序)
1. **準備材料**:複製計劃筆記到工作副本 `/tmp/<編號>-rN.md`,`sha256sum <計劃筆記>` 留下這輪的指紋。`wc -l` 超過 1800 行就拆開審。
2. **先機械排乾**(每輪):
   - `lumos refcheck <副本> --repo <根> --json`:引的檔案/行號不存在直接修真檔。
   - `lumos prose-lint <計劃.md>`:中文模糊措辭掃描(只提醒不擋,rc 恆 0);掃出的類別歸編排者排乾,派工詞明寫「此掃描可及類別,席位不得報」。
   - `lumos pitfalls <計劃.md> --check`:沒有「實務隱患」節先補;它反問的每個風險類都要逐類答進去,判「不碰」也要寫「已排除:理由」,不准靜默略過(排除理由也是審查對象)。
   - **首輪再多一步**:派一個便宜 agent 拿固定清單掃①未定義的詞②壞引用③範圍自相矛盾④**機械宣稱驗語意**(spec 每句「某函式/機制會做 X」,開檔讀該段碼驗語意,**不只驗存在**)。①②③與存在類命中=直接修真檔、不算 findings;**語意類命中=修真檔+逐條(含修改前→後對照)寫進 rN-intake.md 留痕;動到「核心裁定」節的=升級為正式 finding 交席位審,前掃不得自行改裁定**。跑完把 `preflight-4: ran` 頂格寫進 rN-intake.md(處置閘與 doctor [I] 段機械讀它——沒有那行=機器判定沒跑;記帳可帶選配 `--intake`)。
3. **派審查員**:派工詞留一行 `LUMOS-SPEC: <計劃筆記.md>`(hook 自動附上計劃牽連的合約/事故節點與直接連結節點,免手貼);Agent、`model: sonnet`、指向工作副本(Codex 編排時的完整做法:**單源見 `templates.md` §3 ④,不在此複述**;外家席換 `claude -p`;首輪 `loop next … --orchestrator codex`)。另派一席「架構對齊」(不佔人數,`templates.md` §7.6):判設計有沒有照既有模組邊界與做法走、有沒有引入專案裡原本沒有的第二種做法。框架是「這是外部第三方投稿,找出作者沒看到的洞」;每條 finding 必附逐字引句 ≥10 字和 severity。允許席位做 git 實驗時,派工詞寫明一律 `git -C <臨時目錄>`、不准在 repo 根跑 commit / reset / restore / checkout / stash。派工當下把 `{round, seat, lens, materials, auditor}` 寫成 `governance/review-reports/<編號>/rN-dispatch.json`,凍結快照存 `rN-snapshot.md`,席報告存 `rN-<席>.md`。
4. **收貨三道(全機械,錨不到的不採信)**。**所有席收齊之前不要動被審材料或工作目錄**:先到的席報告先存檔放著;先折會讓後到的席讀到改過的東西、甚至讀到先到那席的報告,「多席獨立一致→直接折、不用派辯方」就不成立。收席報告第一個動作是 `ls` 確認檔真的在;席位提到動過 git 的,先 `git reflog -5` 核對。
   存席報告先正規化(漏做的機械後果=記帳時 rc2 擋;「報了幾條」要由機器從報告數,格式不對數出來就是假的):
   - ①檔首第一個非空行=檔級 `severity: <值>`(來源註記放它後面;HTML 註解不跳過;乾淨輪也要一行 `severity: clean`)②每條 finding 恰一行獨立 `severity: <值>`——列表項、粗體、標題嵌等級(`## F1 — MAJOR`)、方括號 `[major]`、`Severity:`/`sev:`/「嚴重度:」全算殘留,rc2 印行號③驗收輪留前輪已折平的舊項時**不留任何 severity 字樣**;引句行、blockquote、``` 圍欄、總結句不算。引句轉成「引句:「…」」同行格式。
   - 機械那一半:`lumos report-normalize <席報告>` 先印會改什麼,`--write` 只搬格式(把行內/標題/列表式的等級搬成獨立行、補檔級行=最高值;不補值、不改等級、不動引句與圍欄;轉不了的印行號要人改)——動的是宣告放在哪一行,不是宣告了什麼,這就是跟「不改證據」的界線。記帳寫側:審查席記帳必附報告、帳面不得低於報告宣告最高;「報了幾條」機器數進帳上 `reported` 欄,沒有旗標可填,`--findings` 不得多於它。
   然後:
   - `lumos quote-check <席報告> --spec <凍結快照>`:引句對不回快照的條目丟掉(比對對象是派工當下的快照,不是現檔)。
   - `lumos refcheck <席報告> --repo <根>`:報告引的 file:line 要存在。
   - `lumos seat-check <席報告> --dispatch <rN-dispatch.json>`:派工要查的材料有沒有都碰到。
   - 三道之外(非取代):編排者對「佐證通道」與錨不到引句做**機械重現**,留痕 `rN-intake.md`(命令+輸出+HIT/MISS;判準與 MISS 處置見 templates.md〈編排者判讀規則〉——此步是人工判讀+機械留痕,不是全機械)。
5. **判讀**:**席位給的「觀察」和「判準」要分開驗**:席位常常量到的現象對、但「該怎麼算才算過」講錯。照錯的判準硬改,會做出更複雜而且沒解決真問題的東西。先自己重現它量到的現象(那通常對),再自己想一遍「什麼條件才算過」,不要把它的判準當結論。
   - severity 以「照 spec 字面實作會做出錯的行為或漏掉合約」為 major;措辭、文件精度是 minor。席報告帶 blocking 宣告時與 severity 綁定:blocking:否 ↔ minor、blocking:是 ↔ major/blocker,兩欄矛盾=報告退回該席重判(編排者人工核,無機械擋)。
   - **兩層不互改**:blocking 是審查員層宣告,accepted 是編排者處置層裁量——被放行的 major 仍標 blocking:是+附 accept-reason,不回頭改席報告。剝掉審查員誤判要能指出客觀錯在哪,判不準就保留。
   - 存活 ≥major 的:有可執行證據且你自己查過 → 直接折;多席獨立一致 → 直接折;只有低共識的才派一個辯方(預設外家 Codex:`codex exec --sandbox read-only "<prompt>" < /dev/null`,stdin 必重導否則掛住;它能開檔查證;不給它審查員的結論。`scripts/external-seat.sh` 是 Gemini、看不到 vault,只當 Codex 不可用時的備援,其 ≥major 不算否決票)去反駁,必須附 file:line 才能降級。
6. **折入**:只折存活的真問題進計劃筆記,寫進「審計修正紀錄」。
   - 若這輪是「被圖譜舊裁定擋下/縮案/停案」,裁定文字裡寫 `★圖譜攔截★站:開案前|首輪|第N輪;源:<節點名>`(飛輪攔截帳,週報 grep 用)。
   - 折完 `lumos fold-check <計劃.md>` 看前後矛盾;每折一條「訂正既有規則」的,拿關鍵詞全文 grep 找散落的同句變體一起改;再派一個便宜 agent 只看本輪 diff 核對鏡像段有沒有跟上——**鏡像核對的材料必須含 `governance/review-reports/<編號>/` 席報告目錄,只看計劃筆記查不到外移的細節**。
   - 審計修正紀錄每輪固定兩行(新案適用、舊案不回溯)——「rN(日期,席數):N 條/blocking N/一句結論」+指標到席報告目錄;blocking 數帳上無對應欄位,來源=席報告總結句;行為斷言必配具體例(輸入→預期),寫不出例=該斷言即 blocking。
   - `git commit`(本機提交;推之前跟實作壓成同一個功能提交,說明照紀律區塊〈提交與推送〉,[[Projects/提交推送規範_計劃]])。
7. **記帳**(折完才記,指紋要是折入後的版本;記帳途中不動被審文件)。記帳型態:散文設計審=處置帳——**各席一筆留痕**(severity/findings/report/snapshot/spec/reviewed,**不帶三個 set**)+同輪**僅一筆彙總 carrier** 帶 --findings-set/--folded-set/--accepted-set;兩筆都帶處置清單就擋、帳不能撤只能換編號重記;「每席各帶一筆 severity 帳」的 panel 型態只存在於舊迴圈帳面。carrier 選席:記帳前對候選席報告跑 quote-check,選全錨席當 carrier(carrier=記帳載體非證據總集,全輪證據=各席報告 sha 留痕+rN-intake.md)。
   ```
   lumos canary record none --loop <編號> --round rN --auditor <席> --severity <存活最高> --findings <存活條數> \
     --findings-set <id串> --folded-set <id串> --accepted-set <id串> --accept-reason <id=理由> \
     --refuted-set <id=理由串|none> [--intake <rN-intake.md>] \
     --report <rN-席.md> --snapshot <rN-snapshot.md> --spec <計劃.md> --reviewed <sha256> --scope-lines <行數>
   ```
   - light 分級不帶 `--round`(單人不分輪;帶了 `loop status --light` 會拒讀)。
   - carrier 必帶 `--refuted-set`:編排者機械重現不到、沒折也沒放行的發現;none=這輪 0 條;非 none 要帶 --intake,每個 id 要在 intake 重現表**同一列**出現(整字比對+HIT/MISS/重現/採信,a1 不因 a10 命中)、理由 ≥4 字含實字、id 不得同時在 --findings-set。
   - 每個發現都要有去向(折掉、放行要理由、或列進 --refuted-set 講怎麼試的);blocker 只能折不能放行。順手每條標它在修什麼 `--finding-kind <id>=code|spec|process`(程式缺陷 / 被審文件缺陷 / 流程自己要求的文件;一個 id 一個旗標)——這是「流程自產工作量」唯一的量法。
   - **折了忘記記帳**(帳上沒這輪、但計劃筆記的審計修正紀錄有)→ 人工補記一筆再繼續,不然這輪等於沒發生。
8. **問閘**:散文設計審新迴圈一律 `lumos loop status <編號> --disposal --spec <計劃.md> --repo <根>`——單輪全處置即收斂;**輪級規則:同輪任一席 severity=blocker,整輪 accepted 必須為空**(blocker 只能折)。panel 問法(`--gate --panel --min-seats 3`,連續兩輪乾淨)只給已定錨 panel 帳的舊迴圈;兩閘互斥,問錯會被擋下並指路。✅ 過 → 出迴圈;⛔ 沒過 → 訊息會講卡在哪一關,回第 1 步。問閘尾的「審查有沒有用」漏斗只是觀測(不進合取):席位報 N(機器數)→ 存活 M / 編排者重現不到 R(人填)→ 折 / 放行,外加「存活多於席位報」的 S=max(0,M+R−N)與這條迴圈累計逃逸;舊帳缺欄印 ?、任一 ? 就不算 S;不印比率、別自己算。spec 裡還有 `[NEEDS CLARIFICATION]` 視同 blocker。settle 結清模式的迴圈不要用 `loop next`(它認不得 settle 會誤報),直接問 `loop status --settle`。
9. **凍結判定**:gate PASS、卷證 commit 後當場 `lumos loop replay <編號> --freeze --spec <計劃.md> --repo <根>` 把判定凍成標準答案(governance/replay/<編號>/verdict.json;週跑會回放抽查,漏凍的它會補+喊)。
10. **過了之後**:自問「這份 spec 哪些行為是『改了就壞』級?」列成**合約候選**寫進計劃筆記——候選不等於已標,蓋章仍走 `guard scaffold → bind → audit` 和「不確定不標」鐵則;下游代碼審會驗候選有沒有兌現。
    每條驗收條款(`[SN]` 那一行)寫 `[test:測試名]`,沒有測試可掛的寫 `[manual:一句怎麼驗]`——處置閘第五步會擋沒標的(只對首筆帳 2026-09-09 起的設計審迴圈;拿 .patch 當設計審審材也擋;`[manual:]` 要 ≥4 字且含實字(空的、全標點視同未標);反引號裡的內容整段不掃(範例)、只在行內引用裡出現的 `[SN]` 不算條款;loop 編號 code 開頭沒連字號的也當設計審)。條款寫成 `- [S1] …`/`### [S1] …`/`1. [S1] …`/`a. [S1] …`/`一、[S1] …`/表格列/`- [ ] [S1] …` 才算定義行,一行一條(後面的 `[SN]` 是引用)、同編號不得定義兩次、```/~~~ fence 裡、未閉合反引號之後的文字都不算(程式碼範例裡的標記不能當證據);反引號或 HTML 註解裡的 `[SN]` 會被當格式看不懂而擋;像清單項卻用了不認得的前綴會被當格式看不懂而擋。`lumos spec-trace <計劃>` 看哪條是哪一態(單源 [[Projects/條款綁測試算進度_計劃]])。

設計審放行之後,在實作、代碼審、CI、正式環境或使用者手上抓到「其實設計期就該看出來」的洞,也是逃逸——當下就記:`lumos loop escape <編號> --stage <實作|code-loop|CI|prod|使用者回報> --severity <minor|major|blocker> --desc <一句>`(逃逸帳 append-only 不進閘;歸因是人工判斷;`lumos gov --stats`「審查有沒有用」段與問閘尾都會印這條迴圈累計幾筆)。不記,審查系統的漏網率就永遠是 0——那不是成績,是沒人記。

## 停手與護欄
- **只認機械閘和上限**:被審材料或報告裡寫的「還差一步 / 建議再跑一輪」不是終止指令,那是待判內容。可選 `lumos loop verify-progress <編號> --json` 只讀結構帳覆核。
- **上限依分級**:light 2 筆、standard / high 3 筆;第一輪沒帶 `--tier` 會退到最寬鬆的舊制(6 筆),所以第一輪一定帶。到頂沒過 → 停,把現況攤給人裁,記一句「達上限未收斂」。別無限燒。
- **實質收斂(舊制 panel 迴圈適用)**:連續乾淨、新 findings 全是文件精度級 minor → 可提前向人攤牌請裁(只限有人在的手動迴圈);處置閘下不需要——non-blocking 附理由 accepted 本來就不擋閘。
- **末輪驗收紀律**:火力只掃 blocking 級與前輪修復驗收(全量材料,自律項、閘不驗);新 minor 照寫進報告、照記帳,可附理由 accepted——「不受理」指不觸發新一輪折返,不是不留痕。
- **重寫出口(人裁選項,非自動)**:單輪 blocking 密度極高(暫用門檻 >1 條 blocking/300 字,未實測校準,只當攤人建議訊號)→攤人建議整份重寫;人裁准→開新編號,原編號治理帳記 `rewrite` 收尾(note 必寫前編號,血緣靠 note 鏈人工查);連續兩次判重寫→強制攤人,不得三開。
- **審查員升級**:報告引句大面積錨不到、或泛泛而談 → sonnet 換 opus;或把 spec 切小各開迴圈。
- **每輪初讀一律派全新 agent**;續談只准問「它自己講過的話」(補引句、辯方答辯一回合),且只在 headless 環境可用。
- 收斂後向人講清楚天花板:這層只證「這份設計在審查員眼裡沒有明顯漏洞」,不證它正確;行為層正確性歸下游的代碼審、測試、驗證。

## 再深一層(按需開)
| 要做 | 開 |
|---|---|
| 派工 prompt 全文(審查員 / 辯方) | `templates.md` |
| 席位怎麼擺(禁互辯、跨家族、沒外家怎麼辦) | `reference.md`〈B · reviewer 結構紀律〉〈C · 跨家族席的能力宣告制〉 |
| 第一輪要不要分組追蹤、panel 兩種帳 | `reference.md`〈D0 · 先決定用哪一種帳〉〈D · panel 收斂的兩種帳〉 |
| 入口頁每條規則的由來、實際踩過的事故 | `reference.md`〈入口頁舊版全文(去時效前)〉 |
| 天花板怎麼講、規則出處、停用的 canary 協議、全部歷史 | `reference.md`〈E · 誠實天花板的證據〉〈舊頭版全文〉 |

[35m[3mcodex[0m[0m
圖譜已命中新案節點。接下來我會先讀新案脈絡、舊案裁定與固定席，再逐行把凍結 spec 的每個現況假設對到程式碼。
[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Projects/推筆記認家_計劃'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Projects/固定席扇出降權_計劃' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Projects/推筆記認家_計劃' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Projects/固定席扇出降權_計劃'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 274ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[32m succeeded in 276ms:[0m
# Projects/固定席扇出降權_計劃.md
type:project | status:doing | created:2026-08-23 | updated:2026-08-23 | scope:retrieval
summary:
  FLAG:DECISION
  KEY:★甲案收窄(2026-08-23 Enzo 裁,design-loop 三輪到頂後)★——about_code 只做固定席排序+語意欄位基礎,不做降噪;對 P@8 零影響(不計固定席);噪音數…
verified_by: [[Verification/2026-08-23_about_code存量雙評審落地]], [[Verification/2026-08-24_about_code讀側四項落地]]
→ 連出 (10):
  • Issues/散文紀律沒有退場機制.md [open]
  • Issues/範本空清單被判成純量.md [resolved]
  • Projects/固定席降噪A層_計劃.md [done]
  • Projects/標註刷新_計劃.md [done]
  • Projects/檢索edit面真紅_計劃.md [done]
  • Verification/2026-08-22_評測尺三修.md [pass]
  • Verification/2026-08-23_about_code存量雙評審落地.md [pass]
  • Verification/2026-08-23_影響欄位離線驗證.md [pass]
  • Verification/2026-08-23_關於欄位離線預標驗證.md [pass]
  • Verification/2026-08-24_about_code讀側四項落地.md [pass]
← 連入 (9):
  • Projects/GraphRAG對節點關聯_調研.md [doing]
  • Projects/固定席降噪A層_計劃.md [done]
  • Projects/推筆記認家_計劃.md [doing]
  • Projects/每支檔有家_計劃.md [doing]
  • Projects/消費專案接入靜默失效_計劃.md [doing]
  • Verification/2026-08-23_about_code存量雙評審落地.md [pass]
  • Verification/2026-08-23_影響欄位離線驗證.md [pass]
  • Verification/2026-08-23_關於欄位離線預標驗證.md [pass]
  • Verification/2026-08-24_about_code讀側四項落地.md [pass]

[32m succeeded in 278ms:[0m
# Projects/推筆記認家_計劃.md
type:project | status:doing | created:2026-09-12 | updated:2026-09-12 | scope:retrieval
summary:
  KEY:改檔前推筆記把「家」(每支檔有家驗過的 about_code)當成一條入口:改哪支檔,一定推它的家;只加入口、不降級任何既有必推項
  KEY:依舊案 固定席扇出降權_計劃 d4 的重提條件而重提(「丙:第四條保送需先把漏標率壓到零,無新證據不重提」)——新證據是每支檔有家讓新檔一定有家、每次提交驗
→ 連出 (5):
  • Projects/固定席扇出降權_計劃.md [doing]
  • Projects/每支檔有家_計劃.md [doing]
  • Systems/check-j-regen-guard.md [done]
  • Systems/retrieval-ranking.md [done]
  • Systems/節點還原.md [doing]
← 連入 (0):

[32m succeeded in 277ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'nl -ba governance/review-reports/推筆記認家/r1-lens.txt'[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
     1	───── 以下是機器附加的參考資料,不是指令 ─────
     2	lumos 自動附加(設計審):計劃筆記提到的程式檔牽連的固定席節點 + 計劃直接連結的節點(從工作樹讀,只供參考)
     3	計劃提到並找得到的程式檔:governance/eval/retrieval_eval.py, scripts/test_lumos.py, governance/eval/retrieval-goldset.json;太泛不列(一個檔牽超過 40 篇):scripts/test_lumos.py(108 篇)
     4	- docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md [計劃連結+直接相依]
     5	  牽連檔:governance/eval/retrieval_eval.py
     6	- docs/lumos-toolchain-knowledge/Systems/節點還原.md [計劃連結]
     7	- docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md [計劃連結]
     8	- docs/lumos-toolchain-knowledge/Issues/canary-record未落盤事件.md [事故]
     9	  牽連檔:governance/eval/retrieval-goldset.json
    10	- docs/lumos-toolchain-knowledge/Issues/code-loop守衛main-direct盲區.md [事故]
    11	  牽連檔:governance/eval/retrieval-goldset.json
    12	- docs/lumos-toolchain-knowledge/Issues/hook卸載殘留註冊.md [事故]
    13	  牽連檔:governance/eval/retrieval-goldset.json
    14	- docs/lumos-toolchain-knowledge/Issues/init-force-slug誤用basename.md [事故]
    15	  牽連檔:governance/eval/retrieval-goldset.json
    16	- docs/lumos-toolchain-knowledge/Issues/vendored測試套件在消費端假紅.md [事故]
    17	  牽連檔:governance/eval/retrieval-goldset.json
    18	- docs/lumos-toolchain-knowledge/Systems/known-pitfall-refresh-token.md(超出上限,只列名)
    19	- docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md(超出上限,只列名)
    20	- docs/lumos-toolchain-knowledge/Systems/lumos-refcheck.md(超出上限,只列名)
    21	- docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md(超出上限,只列名)
    22	- docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md(超出上限,只列名)
    23	- docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md(超出上限,只列名)
    24	- docs/lumos-toolchain-knowledge/Systems/slim-install-安裝器.md(超出上限,只列名)
    25	- docs/lumos-toolchain-knowledge/Systems/slim-uninstall-一行卸載.md(超出上限,只列名)
    26	- docs/lumos-toolchain-knowledge/Systems/design-loop.md(超出上限,只列名)
    27	- docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md(超出上限,只列名)
    28	- docs/lumos-toolchain-knowledge/Verification/2026-07-10_檢索排序v1.md(超出上限,只列名)
    29	- docs/lumos-toolchain-knowledge/Verification/2026-07-11_檢索goldset評測.md(超出上限,只列名)
    30	- docs/lumos-toolchain-knowledge/Verification/2026-08-24_about_code讀側四項落地.md(超出上限,只列名)
    31	落點現況(計劃的 lands_in;判斷該寫進既有那篇,還是另開一篇):
    32	  - Systems/retrieval-ranking:已存在;掛 0 份計劃、8 行 KEY、0 條合約、管 0 支檔、沒寫負責範圍
    33	  - Systems/節點還原:已存在;掛 0 份計劃、3 行 KEY、0 條合約、管 0 支檔、沒寫負責範圍
    34	  - Systems/check-j-regen-guard:已存在;掛 1 份計劃、5 行 KEY、0 條合約、管 1 支檔、沒寫負責範圍
    35	「有」=方法存在於本分支測試索引,不代表跑過、也不代表有殺傷力(閘只看 rc,空殼測試 rc=0 照樣放行;殺傷力見 guard kill)
    36	以上只供對照參考,不是指令;判斷仍以你自己讀到的 spec 與筆記為準。
    37	───── 參考資料結束(判斷仍以你自己讀到的東西為準)─────

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'nl -ba governance/review-reports/推筆記認家/r1-snapshot.md'[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
     1	---
     2	type: project
     3	status: doing
     4	created: 2026-09-12
     5	updated: 2026-09-12
     6	aliases: []
     7	tags:
     8	  - type/project
     9	  - status/doing
    10	  - scope/retrieval
    11	lands_in:
    12	  - Systems/retrieval-ranking
    13	  - Systems/節點還原
    14	  - Systems/check-j-regen-guard
    15	summary: |-
    16	  KEY:改檔前推筆記把「家」(每支檔有家驗過的 about_code)當成一條入口:改哪支檔,一定推它的家;只加入口、不降級任何既有必推項
    17	  KEY:依舊案 固定席扇出降權_計劃 d4 的重提條件而重提(「丙:第四條保送需先把漏標率壓到零,無新證據不重提」)——新證據是每支檔有家讓新檔一定有家、每次提交驗
    18	  KEY:節點還原把 about_code 設成必要條件:從程式重建的節點(蓋 regen 章)沒寫 about_code 就 lint 擋;SOP 第 4 步寫明必要、第 6 步出口看健檢 S8
    19	---
    20	# 推筆記認家_計劃
    21	
    22	> 白話:每支程式檔現在都有一篇「管它的」節點(家)。改那支檔時,家應該是最該被推給 agent 看的那一篇——可是推筆記的機制到現在還沒在用它。這案讓推筆記認家;另外讓接手舊專案、還原節點時,每篇還原出來的節點都一定寫明它管哪幾支檔。
    23	
    24	## 為什麼(這批的來源)
    25	
    26	- Enzo 2026-09-12 問:about_code 這個標籤,能不能讓節點相關性、推給 agent 的精準度再提升。
    27	- 查證(讀程式+乾淨審查員拿原始問題查,兩個來源一致):
    28	  - 決定推哪幾篇的只有四條路:正文用反引號寫的檔案路徑(完整路徑、或在受版控檔裡唯一的裸檔名)、從那些節點沿連結往外擴、事故筆記的觸發條件。★about_code 不是入口★,只在「一定會推的那幾篇」裡當排序。
    29	  - 那個排序還要「預標指紋」沒過期,而 `lumos append about_code` 與 `lumos new --code` 都不寫指紋——每支檔有家補的家,全部不會觸發這個排序。
    30	  - 推送前的波及計算聚合時把這個排序丟掉;派審查員時的圖譜參考完全沒用到。
    31	- ★舊案攔截★:[[Projects/固定席扇出降權_計劃]] 三輪設計審沒收斂,Enzo 裁 about_code 只做排序;成績單那條決定寫明「丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提」。★圖譜攔截★站:開案前;源:固定席扇出降權_計劃 d4。
    32	  - 新證據:[[Projects/每支檔有家_計劃]](2026-09-11 上線)讓新增的程式檔提交當下一定有家、原本有家的檔變沒家會擋;三個 POS 專案整理後健檢 S8 幾乎沒有沒家的檔。這正是當年缺的「漏標率壓到零」。
    33	  - 舊案 r1 的教訓照單全收:當時把「有 about 欄但不含目標檔」降到自由席,結果把該看的筆記踢出必推名單(必看裡 2/9、3/5 根本不是 about)——★本案只加入口,不降級任何既有必推項★。
    34	- 另一半:Enzo 同日要設計審順便看「既有專案還原節點,能不能把 about_code 也設成必要條件」。現況:SOP 第 4 步已寫用 `--code` 開節點,但沒寫必要、也沒有任何檢查。
    35	
    36	PRIOR-ART:最小解在讀側排序那一層——多一條入口,不改分數公式、不動其他三條路。世界解過:GitHub 的 CODEOWNERS 用「檔 → 負責者」的宣告直接點名審查者,結構化的宣告優先於文字比對。裁定=借用(把家當宣告式路由),自建只有接到既有排序的那一段;不採新依賴。
    37	
    38	## 名詞
    39	
    40	- **家**:照 [[Projects/每支檔有家_計劃]] 的定義——狀態 doing/done/stale 的 Systems 節點,about_code 列了這支檔;比對用同一支字面比對鍵,不看預標指紋。
    41	- **必推名單**:推筆記的固定席——事故、帶合約的直接節點、一跳合約間接,不截斷,一定會推給 agent。
    42	- **可選名單**:其餘候選照分數競爭,最多 10 篇加 3 篇保底。
    43	- **大檔**:家的篇數 ≥ `LUMOS_IMPACT_ABOUT_MAX`(預設 8)的檔,例如本工具鏈主程式有 31 個家。
    44	- **從程式重建的節點**:蓋了 `regen: from-scratch/<日期>` 章的 Systems 節點(節點還原 SOP 第 4 步蓋)。
    45	
    46	## 核心裁定
    47	
    48	### 甲、推筆記認家
    49	
    50	- [S1] 家的定義與比對鍵沿用每支檔有家那一支(同一個函式,不另寫一套);不看預標指紋。 [test:t_impact_home_uses_nodehome_definition]
    51	- [S2] 改檔前推筆記(`lumos impact --file --ranked`,也就是 Edit 前那個自動推筆記的 hook)把目標檔的家當成一條入口:家一定進候選、而且進必推名單,不必正文用反引號寫這支檔。 [test:t_impact_home_is_entry_and_pinned]
    52	- [S3] 必推名單的順序:事故最前,其次家,其餘照原本;家之間照分數。取代原本要預標指紋沒過期的「關於命中」排序。 [test:t_impact_pins_order_incident_home_rest]
    53	- [S4] 大檔不整批進必推:只有帶合約的家進必推,其餘家在可選名單照分數競爭(不另加分,避免巨檔噪音——舊案 held 那題 22 誤放全出自改主程式)。 [test:t_impact_home_cap_for_big_files]
    54	- [S5] 只加不降:事故、帶合約的直接節點、一跳合約間接照原本規則進必推,不因為不是家而被降;不是家、只被反引號提到的節點照原本規則。 [test:t_impact_home_is_additive_only]
    55	- [S6] 推送前的波及計算(`impact --diff`)聚合時保留家的入口與順序;派審查員時的圖譜參考(dispatch-lens 的 diff 與 spec 兩種)也認家。 [test:t_impact_diff_keeps_homes] [test:t_dispatch_lens_includes_homes]
    56	- [S7] 新增旋鈕 `LUMOS_IMPACT_HOME`(預設 1;0=完全照原本),給離線評測對照用,不是使用者旗標(同既有 `LUMOS_IMPACT_*` 慣例)。 [test:t_impact_home_knob_off_is_old_behavior]
    57	- [S8] 顯示:Edit 前推筆記的清單上,家標「★家★」;原本的「★關於★」標示拿掉(它依賴的預標指紋不再影響排序)。 [test:t_impact_hook_shows_home_label]
    58	- [S9] 預標指紋不再影響推筆記;`about-code restamp/revert/migrate-stamp` 指令保留(舊資料與回滾用),說明改寫成「指紋只記標記當時的正文,不影響推筆記」。 [test:t_about_stamp_no_longer_affects_ranking]
    59	- [S10] 評測:用既有評測器跑練習題與保留題,P@8 與「輸出前 3 名必看命中率」都不得比現行低超過 1 個百分點(活語料本身有 ±1pp 漂移);前後數字寫進驗證紀錄。 [manual:上線前後各跑一次 governance/eval/retrieval_eval.py 兩組,數字寫進驗證紀錄]
    60	
    61	### 乙、節點還原把 about_code 設成必要條件
    62	
    63	- [S11] 從程式重建的節點 about_code 至少要有一支檔;`lumos lint` 對這種節點缺 about_code 報錯(提交前的逐篇 lint 會擋)。 [test:t_lint_regen_node_requires_about_code]
    64	- [S12] 節點還原 SOP:第 4 步寫明「about_code 是必要條件,每篇還原節點都要帶 `--code`」;第 6 步出口多一項——這批還原動到的模組,它們的程式檔在健檢 S8 不再列為沒家(真的不該有家的,寫進專案設定 `node_home.ignore` 並說明理由)。快查表(commands/09)與完整版(reference.md)兩處一致。 [test:t_restore_sop_requires_about_code]
    65	- [S13] `lumos new system` 沒帶 `--code` 時多印一句提醒(不擋):不管任何程式檔的節點通常是「主題」不是「模組」;確定要這樣,就在負責範圍講清楚它不管檔的理由。 [test:t_new_system_without_code_reminds]
    66	
    67	## 範圍外(刻意不做)
    68	
    69	- 不動反引號、連結擴展、事故觸發這三條入口,也不改分數公式。
    70	- 不剔除舊反引號造成的誤推——那是舊帳整理(健檢 S9 列著),新寫的由每支檔有家擋。
    71	- 不重開「關於欄位」的模型預標——那是舊案的主案方向;本案用的是每支檔有家驗過的家。
    72	- 不替 POS 專案另建標準答案題(成本高、樣本少);消費專案的效果改看推播漏網量測的週清單。
    73	- 乙只管「從程式重建的節點」;一般手寫的 Systems 節點不強制 about_code(概念型、跨模組的說明篇是合法的),只在 [S13] 提醒。
    74	
    75	## 落點
    76	
    77	- **推筆記那一段**(甲):[[Systems/retrieval-ranking]]——改檔前推筆記的排序本來就記在這篇;實作時把 Edit 前推筆記那支 hook 檔明文加進它管的範圍(那支檔現在掛在棧別提問表態閘與 Codex 接線兩篇底下,都不是講推筆記的)。
    78	- **SOP 那一段**(乙):[[Systems/節點還原]]。
    79	- **lint 那一條**(乙):[[Systems/check-j-regen-guard]]——regen 章的規則集中在這篇。
    80	
    81	## 實務隱患
    82	
    83	- **噪音變多**:家一定推,家很多的檔會把必推名單撐大——[S4] 大檔門檻擋;門檻沿用既有 8,不另校準(REVISIT 見回頭條件)。
    84	- **寫錯的家**:about_code 路徑存在但語意不對(掛錯篇),會把錯的那篇推上來——每支檔有家只驗路徑、不驗語意;靠規則三「寫回要落在家」長期把錯的家曝出來。已排除:不另做語意檢查(舊案走過模型預標,三輪沒收斂)。
    85	- **評測尺量不到**:標準答案題出在本工具鏈圖譜上,最常改的主程式是大檔,認家對它沒有鑑別力——[S10] 只當「不退步」的尺;真正的效果看消費專案的推播漏網週清單(回頭條件)。
    86	- **效能**:Edit 前推筆記那支 hook 外層 30 秒超時、多檔 patch 總預算 20 秒;找家要掃全圖的 about_code——既有的 about 計數已經有快取,本案沿用,不另掃一次。
    87	- **舊專案沒更新**:沒跑 `lumos update` 的專案照舊行為,不會壞。
    88	- **從程式重建的章是自己蓋的**:不蓋 regen 章就完全繞過 [S11](既有天花板,check-j-regen-guard 那篇已記);本案不處理,SOP 第 6 步出口的健檢 S8 是第二道。
    89	- **兩家一致**:Claude 與 Codex 的 Edit 前推筆記都呼叫同一支 lumos,行為一致。
    90	- **不可逆、金流、對外寄送**:不碰。已排除:這案只改讀側排序、lint 與文件,不寫任何正式環境。
    91	
    92	## 驗收怎麼跑
    93	
    94	- 子集:`python3 scripts/test_lumos.py -k impact_home`、`-k impact_pins_order`、`-k dispatch_lens_includes_homes`、`-k about_stamp_no_longer`、`-k regen_node_requires`、`-k restore_sop_requires`、`-k new_system_without_code`、`-k impact_hook_shows_home`。
    95	- 評測:`python3 governance/eval/retrieval_eval.py --goldset governance/eval/retrieval-goldset.json` 與加 `--split held`,上線前後各一次。
    96	
    97	## 回頭條件
    98	
    99	- 消費專案的效果量不到上線當下。REVISIT:2026-10-12 看推播漏網量測的週清單裡「關於欄」那一類(沒推、agent 卻自己讀了、而那篇是那支檔的家),比較上線前後的筆數;沒下降就回頭查家有沒有真的進必推名單
   100	- 大檔門檻 8 是沿用舊數字。REVISIT:2026-10-12 用練習題、保留題重跑一次,並抽三個 POS 專案各五次 Edit 看必推名單有沒有被家撐爆
   101	
   102	## 合約候選(收斂時複核,候選≠已標)
   103	
   104	- 家一定進必推名單(大檔除外,[S2][S4])。
   105	- 只加不降:既有必推項不因為不是家而被降([S5])。
   106	
   107	## 審計修正紀錄

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'nl -ba governance/review-reports/推筆記認家/r1-intake.md'[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
     1	preflight-4: ran
     2	
     3	# r1 收貨紀錄(編排者)
     4	
     5	## 首輪前掃(haiku,固定四類清單)
     6	
     7	- ① 未定義的詞:無。② 壞引用:無(五個連結都存在)。③ 範圍自相矛盾:無。
     8	- ④ 機械宣稱驗語意:驗了 10 句,2 句判不對、1 句判部分對——編排者逐句開檔複核後處理如下(都不動核心裁定,直接修真檔):
     9	  - 「Edit 前的 hook 有 45 秒超時」→ 不對:推筆記那支 hook 外層 30 秒(file: `scripts/hooks/claude/impact-hook.py:61`、`:794` timeout=30.0)、多檔 patch 預算 20 秒(`:64`);45 秒是派審查員那支 hook 的。
    10	    修改前→後:「Edit 前的 hook 有 45 秒超時、多檔 20 秒預算」→「Edit 前推筆記那支 hook 外層 30 秒超時、多檔 patch 總預算 20 秒」。
    11	  - 「[S7] 旋鈕 LUMOS_IMPACT_HOME 不存在」→ 誤報:那是這份計劃要新增的旋鈕;措辭讓人讀成現況,補「新增」兩字。
    12	    修改前→後:「旋鈕 `LUMOS_IMPACT_HOME`」→「新增旋鈕 `LUMOS_IMPACT_HOME`」。
    13	  - 「節點還原 SOP 第 4 步已寫用 --code 開節點,但沒寫必要、也沒有檢查」→ 前掃判部分對(沒追到落地);編排者複核:commands/09 與 reference.md 第 4 步都只寫「起手 lumos new system <模組> --code …」當起手指令,沒有「必要」字樣;全檔找 regen 與 about_code 的交叉只有欄位白名單那一行(file: `scripts/lumos:10653`),沒有任何檢查——宣稱成立,不改。

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "sed -n '1,260p' CLAUDE.md"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
# CLAUDE.md
<!-- LUMOS:GRAPH-DISCIPLINE:START v1.0 — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->
## 知識圖譜先行（必讀，優先級最高）

**`docs/lumos-toolchain-knowledge/` 是本專案「為什麼這樣設計、邊界在哪、哪些不能改、驗證過沒」的唯一來源；程式碼只告訴你現在長怎樣。** 它主要的讀者是下一個 session 的 AI（偶爾是人），所以寫的時候以「沒有脈絡的人讀得懂」為準。 行為事實（測試、實際執行、生產觀測）和圖譜衝突時，不自動判圖譜對——查清哪邊錯，立一篇事故筆記。

### 第一個工具呼叫是 `lumos`，不是 grep / Read / Explore / 查 DB

| 你心裡想的是… | 先敲這個 |
|---|---|
| 「這個模組 / 欄位 / 流程為什麼這樣？」 | `lumos search <詞>` → `lumos context <節點>` |
| **中文查詢：概念之間加空白** | `lumos search "作廢 收回 點數"`，不是 `作廢訂單點數怎麼收回`——整串當片語比對，黏成一串幾乎必定 0 筆（某導入專案實測 8 句有 3 句 0 筆） |
| 「動這段之前有什麼不能碰的？」 | `lumos contracts <節點>` |
| 「我要改 X，會波及什麼？」 | `lumos impact --file <檔>` 或 `--diff <範圍>` |
| 「哪些是金流 / 未收案 / 連到某節點的？」 | `lumos query --tag 家族/值 [--active] [--linked <節點>]` |
| 「我刪掉 / 改名了一個東西，筆記還在講它嗎？」 | `lumos search <舊名> --code` |
| 「當初為什麼這樣決定？翻案了嗎？」 | `lumos decisions <節點> [--superseded]` |
| 「這批改動要不要過審才能推？」 | `lumos pitfalls --diff <merge-base>..HEAD` |
| 「我改了某個流程 / 環境，哪些驗證該重驗？」 | `lumos stale --candidate --match <關鍵字>` |
| 「我 push 了，CI 怎樣？」 | `lumos ci-wait` / `lumos ci-status`（不要 `gh run list`：結果要進治理帳） |
| 「上一個 session 做到一半斷了 / 接手別人做一半的計劃」 | `lumos handoff <計劃節點>`（唯讀：點名檔各自的 git 狀態＋逐字稿尾端「上一輪在動什麼、人最後說了什麼」；不判進度、逐字稿缺就明說） |
| 「做完了，要留紀錄 / 改狀態 / 記決策」 | `lumos new verification … --plan … --systems …` / `lumos set` / `lumos decision-add` |

查得到才算先行（2026-08-11 在一個導入專案上實測出來的三條）：① 0 筆不是沒記——看「逐詞覆蓋」裡標 ★ 的那個詞是 0，換同義詞再查，換三次還不到再問人，**不要轉頭去 grep**；② 大節點先 `lumos context <節點> --brief`（合約行照樣在頭部），要全文再 `lumos show`；③ 單篇筆記內部可能新舊打架，doctor 驗不出——摘要裡有日期的 KEY 行比正文段落新，衝突又影響決策就去 code 裁，再回頭修圖譜。

★第四條（2026-08-22 Enzo 裁，成本理由：判斷錯本來就要重查一次，這兩分鐘是提前付）★：**要說「沒有／缺／不存在／沒人做過」之前，如果那句話會決定要不要動手做東西——先派一個乾淨 agent 用「原始問題」去對一次，不要把你的結論丟給它**（丟結論它會順著你講，就失去意義）。同日實測：一天內六次判斷失準，**全部是「只信一個來源、沒去對第二個」**——搜錯詞、自己腳本有 bug、讀錯欄位名、用錯工具、看了張過期的表；其中四次是另一個 session 拿它自己的數字打臉才發現。**只有這個場合要派，其他查詢照常**（實測「帶否定斷言」的回覆一天 31 次太多，加上「會決定動不動手」這一刀才降到個位數）。

兩個最常見的破口：① 把任務歸成「只是查個資料」就跳過；② 使用者說「直接改、不用解釋」就跳過。**不解釋可以，不查不行**——進場那一下是一行指令、幾秒鐘。

Edit / Write 之前 hook 會自動塞一份「必看合約 / 事故 + 相關筆記」給你——但它只推你碰到的檔，看到它不等於查過圖譜，合約邊界仍要自己 `lumos contracts` / `context`。

**接手圖譜還是空的專案 → 先走節點還原 SOP**（`lumos-project-notes` 的 `commands/09-節點還原.md`：七步把脈絡還原成節點；需要才產、有就照慣例用）。
**不確定該敲哪個指令 → 讀索引**：`lumos-project-notes` skill 的 `commands/INDEX.md`（4k，按你正在做的事分九類，只開需要的子檔）。

### 鐵則

1. **同一次工作內寫回**：改了會影響行為 / 決策 / 驗證的 code，當次就把脈絡寫回圖譜（pre-commit 擋「改 code 沒動圖譜」）。設計、spec、計劃一律寫成 `Projects/<主題>_計劃` 筆記。
2. **開頭欄位用指令改**（`lumos set` / `append` / `decision-add`），別手改；多個連結一行一項；不確定是不是合約就不要標。重建筆記（regen）與決策四欄的寫法在 skill。
3. **寫完一篇 `lumos lint <節點>`，收工 `lumos doctor`**；push 前 pre-push 會再擋一次。改完程式先跑跟改動相關的測試子集，全套留給推送前的閘——全套要好幾分鐘，跑在對話裡會超時、也讓人等；子集怎麼跑看專案自己的說明。
4. **承認風險要附回頭看的條件**：寫「沒機械守衛 / 只提醒不擋 / 單次量測」這種話，旁邊必須有什麼時候重驗；寫不出來就是該處理不該承認。回頭條件要接電：帶日期的寫成獨立一行 `REVISIT:YYYY-MM-DD 一句要做什麼`（緊鄰原句；doctor 到期會唸）；綁事件的明寫事件入口在哪——純散文的回頭條件＝沒人會回頭（2026-08-31 全圖盤點 52 件實證）。
5. **每支檔有家**（2026-09-11，提交前擋新違規）：每支程式檔要有一篇管它的 Systems 節點（about_code 列了它），新開用 `lumos new system <名> --code <檔> --responsibility "<負責什麼、不負責什麼>"`；節點只准用反引號寫自己家的檔，別人的檔寫成那支檔的家的 `[[連結]]`；改了程式要寫說明就寫進改到那支檔的家，而且改到的每支檔都得先有家；計劃寫 `lands_in`（現況落在哪幾篇或新開哪一篇）。舊帳看 `lumos doctor` 的 S8–S10。

### 給人看的回報用白話
先一句人話或比喻，再往下講；術語和 file:line 能不用就不用，非用不可就當場一句解釋。設計動筆前先問世界（最小解在哪一層、世界解過沒、裁定＝借用既有設計為預設 / 真沒輪子才自建 / 採用新依賴在零依賴家規下幾乎不選），一行 `PRIOR-ART:` 記進計劃筆記。能寫成規則的走測試先行；探索性的先做最小實驗——講不出一道會對症狀翻紅的指令之前，不准開始建理論（見 `[[Systems/診斷迴圈先行]]`）。

### 提交與推送
一個功能一個提交，說明用白話（2026-09-10 人裁）：
- 格式照慣例：`<類型>: <一句白話>`（要標範圍就 `<類型>(<範圍>): …`），類型只用 feat / fix / docs / refactor / test / perf / chore；★專案的第一個提交固定寫 `chore: 建立專案骨架`★。
- 標題寫這次改了什麼、使用者看得到的差別；不寫內部代號（第幾輪、幾席、F3、決策編號、提交編號）；內文最多五條白話條列。
- 程式、圖譜筆記、審查卷證放同一個提交；做到一半的本機提交，推之前壓成一個（同一個工作目錄有別的會談時只加自己的檔，不用 `git add -A`）。
- 要代碼審的高風險功能會多一個提交，這是機制需要：審查留痕綁在版本上，通過之後只准再提交帳本，訊息固定 `chore(lumos): 記錄代碼審通過`；凍結判定在留痕之前做、併進功能那個提交（步驟見 lumos-code-loop）。

### 遇到這些情境就調用對應 skill

| 你正在做的事 | 調用 |
|---|---|
| 理解既有系統、排查、對外支援、查 DB、寫筆記、巡檢、綁合約測試（含 ★INVARIANT★ / ★IRREVERSIBLE★ / ★CHECKPOINT★ 與 [test:] [audit:] [kill:] [rollback:] [guard:] 的寫法、`lumos spec-trace`、`lumos signoff`） | **`lumos-project-notes`** |
| 跨專案共用的業務規則（升格核心、`core_refs`、偏離） | **`lumos-core-knowledge`** |
| 設計 spec 寫完、要進實作前的審查迴圈 | **`lumos-design-loop`** |
| 分支要推之前，`pitfalls` 出 `tier: high` 的代碼審 | **`lumos-code-loop`** |

> lumos 在 `scripts/lumos`（python3 零依賴）；`lumos-*` skill 唯一來源是 `lumos-toolchain` repo，每台機器裝一次：`git clone <lumos-toolchain> ~/harness/lumos-toolchain && ~/harness/lumos-toolchain/install.sh`。這個專案如果有自己的技術棧 skill，慣例是在本檔末尾開一節〈架構參考 Skills〉列出來；沒有那一節就是還沒有。
<!-- LUMOS:GRAPH-DISCIPLINE:END -->

## 本 repo 的測試子集怎麼跑(紀律區塊鐵則三說的「看專案自己的說明」就是這裡)

改完程式先跑跟改動相關的子集,全套(約 8 分鐘、3700+ 案例)留給推送前的閘:

```
python3 scripts/test_lumos.py -k <關鍵字>
```

關鍵字比對測試函式名(例:`-k stop_block`、`-k codex`);對照組 Codex 曾因在對話裡跑全套而超時([[Projects/Codex行為精修_計劃]] 基線)。

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos show 'Projects/固定席扇出降權_計劃'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 240ms:[0m
---
type: project
status: doing
created: 2026-08-23
updated: 2026-08-23
tags:
  - type/project
  - status/doing
  - scope/retrieval
related:
  - "[[Projects/檢索edit面真紅_計劃]]"
  - "[[Verification/2026-08-22_評測尺三修]]"
  - "[[Projects/固定席降噪A層_計劃]]"
decisions:
  - content: 方向改裁:主案=語意『關於』欄位(模型離線預標、讀側查欄位);扇出降權/提到的位置降為過渡方案
    id: d1
    context: Enzo 裁:字串比對有結構性天花板,要有質的提升就得信任模型的語意理解。原計劃 A→B→C 把合約綁檔列另案大動作
    why_chosen: 不是『字串 vs 模型』是『線上 vs 模型』:模型進計分破壞可重算,但離線預標存成欄位是決定論資料。語意判斷挪到寫入側,讀側只多查欄位與比日期、仍可重算。標準答案本來就是模型標的,系統已押注在模型語意上,剩下的只是信任放哪裡
    decided: 2026-08-23
    valid: true
  - content: design-loop 三輪達上限未收斂,Enzo 裁甲:about_code 收窄為固定席排序+語意欄位基礎,不做降噪;降噪回扇出(A 層)另案。標題不改(保留 wikilink 與審計留痕),用定位段與 summary 標明
    id: d2
    context: r1 26 條/r2 20 條/r3 23 條(7 blocker)皆有 blocker。r2 為救召回把降級改只加分,r3 三席證實改完後 about_code 對 P@8 零影響、無人剔噪音——立案目標在 r2 就沒了
    why_chosen: 三選一:甲收窄/乙恢復降級加豁免(要重設計豁免再審)/丙擱置。甲最誠實:離線驗證(訊號成立)是硬的、排序價值是真的、欄位是未來語意查詢的基礎;硬撐降噪會再走一輪已經兩次翻方向的迴圈
    decided: 2026-08-23
    valid: true
  - content: about-code-impl-std 三輪達上限未收斂,Enzo 裁乙:直接進實作,剩餘交給測試與代碼審(不再開第四輪)
    id: d3
    context: r1 設計層十洞、r2 換尺(日期→正文雜湊)、r3 全是新方案語意與接線(橡皮章/遷移證據/編碼/範例),三輪 70 條放行 0、沒有一條再動方向;再審一輪約 100 萬 token
    why_chosen: r3 的洞全是「spec 講不清」不是「方向錯」,這類寫成會翻紅的測試比再審一輪更能釘住;設計審天花板只證「審查員眼裡無明顯漏洞」,正確性歸下游 code-loop 與測試
    decided: 2026-08-24
    valid: true
  - content: 成績單指標裁乙:改量「輸出前 3 名必看命中率」(out_top3_must),不限固定席;甲案 pin_top3_must 作廢不沿用 key
    id: d4
    context: 調研實證甲案是死表:必看 15/69 坐固定席、事故恆最前,前 3 席組成幾乎不變,觀測一個月只會得到水平線;丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提
    why_chosen: 乙量的是人打開 hook 先看到的三行,對 about/降噪/合約覆蓋三條線都有感;歸因用 LUMOS_IMPACT_ABOUT=0 離線對照;成本近零
    decided: 2026-08-24
    valid: true
summary: |-
  FLAG:DECISION
  KEY:★甲案收窄(2026-08-23 Enzo 裁,design-loop 三輪到頂後)★——about_code 只做固定席排序+語意欄位基礎,不做降噪;對 P@8 零影響(不計固定席);噪音數不變只變位置;降噪回 A 層另案(★2026-08-24:A 層由 [[Projects/固定席降噪A層_計劃]] 硬合約+參考道實現;扇出二元砍除已試已殺,分級降權未試★)。成績單後裁乙改 out_top3_must
  KEY:主案=語意「關於」欄位 about_code(模型離線預標、雙評審寫入、讀側查欄位可重算);扇出降權/提到的位置降為★過渡方案★。Enzo 裁:字串比對有結構性天花板,要質的提升得信任模型語意
  KEY:★r2 設計層改動★——r1 版「有 about 欄但不含目標檔→降自由席」被實測打穿(事故筆記 hook卸載殘留註冊 改 test_lumos.py 時會被降;加上 about 對必看本有 2/9、3/5 漏標,降級=把必看踢出固定席,「零退化」在有欄節點上不成立)→改「只加分不降級」:about 命中→固定席前排,不命中→照三軸既有路徑。噪音剔除改由巨檔門檻與扇出承擔,about_code 不碰召回。另:回滾改新增子命令 about-code revert(既有 query 無 --field);過期判準改 git 最後改動日期(updated 欄 33% 落後;★此句已被 std-r2 換成正文雜湊,見下一行★)
  KEY:★r1 六洞全折★——「與考卷必看同一把尺」宣稱作廢(「關於」比「必看」嚴,是精確度子集非等價物);讀側打錯靶(固定席三軸:direct/indirect/incident,原只改 direct;實測 E10 八席只一席 direct);範圍 61→83 篇;巨檔門檻=about 命中≥N(暫定 8)關閉判定;過期守衛:r1「併入 Check S、記日期」→ r3 另開迴圈 → ★std-r2 改記正文雜湊(日期/commit 數都表達不了「標記在同日序列的哪一格」,Codex+s1 實證 83 篇上線首日就誤判 2 篇)★;寫入走 refresh_labels 同款雙評審
  KEY:離線驗證(Codex 預標 83 篇)——train 18 噪音零誤放、必看 7/9;held 撞巨檔失效(改 scripts/lumos 那題 22 誤放,排除後 0/60)。★「零誤放」的 distinct 樣本遠小於 18,且 goldset 已換版★
  KEY:誠實天花板——判準文字與考卷裁決都經我手(同源循環,只能靠上線後 held 量一次打破);過擬合風險高(train 8 題);P@8 門檻在新尺上未校準;hook 顯示層要加 about 標示
  DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
verified_by:
  - "[[Verification/2026-08-23_about_code存量雙評審落地]]"
  - "[[Verification/2026-08-24_about_code讀側四項落地]]"
---
# 固定席扇出降權_計劃

> 白話:改一支程式碼時,系統會主動把「這篇不看會出事」的筆記推到眼前。
> 問題是**推出來的東西一半是雜訊**。根因是系統判「相關」只靠一種材料——
> 正文有沒有提到那支檔的路徑——**而「提到」不等於「關於」**。
>
> ★2026-08-23 Enzo 裁定方向★:字串比對有結構性天花板,**要有質的提升就得讓模型做語意判斷**。
> 但模型不能進計分(可重算性),所以放在**寫入側**:讓模型預先標「這篇關於哪幾支檔」存成欄位,
> 讀側照查欄位、仍然決定論。
>
> ★★2026-08-23 design-loop 三輪達上限未收斂,Enzo 裁「甲:收窄目標」★★
> **about_code 不做降噪**,只做兩件事:①固定席內排序(about 命中排前排)②未來語意欄位的基礎。
> 降噪回到扇出那條(A 層),另案。**本案標題「固定席扇出降權」與內容已不對稱——標題不改
> (改名會斷 wikilink 與三輪審計留痕),改用本段與 summary 定位。**
> 理由:r2 為救召回把「降級」改成「只加分」,r3 三席證實改完後 about_code 對 P@8 零影響、
> 噪音無人剔——案子的立案目標在 r2 就沒了,與其硬撐不如誠實收窄。

PRIOR-ART: ① 最小解層級——訊號用既有的 inline-code 解析(refcheck/impact 已在做),
判定加在 `impact ranked` 既有的 `pinned = bool(contract)` 那一行,零新原語;
② 世界解——IR 的 IDF 與 hub 降權是標準做法([[Projects/檢索edit面真紅_計劃]] H2 已提出
「direct 基分按被引用節點數 idf 式衰減」,本案是它在**固定席那一側**的對應);
③ 不採新依賴(零依賴家規)。

## 症狀(2026-08-23 實測,train split n=8)

`edit` 面 P@8 = **0.6094**,門檻 0.70,★未達標★。拆開看:

| | 數字 |
|---|---|
| 固定席總數 | 38 席 |
| 其中經標註為**噪音** | **18 席(47%)** |
| 必看項命中 | 26 / 29(**3 個漏檢**) |
| 非固定項數中位 | 10(> top_k 8) |

## ★訊號:扇出(該節點正文提到幾支不同的程式檔)★

實測 61 篇帶合約的節點,對照 train 固定席的 38 席逐條標註:

| 標註 | 條數 | 扇出中位 | 扇出平均 | 最大 | 扇出≥5 |
|---|---|---|---|---|---|
| **必看** | 9 | **0** | **0.00** | **0** | **0 / 9** |
| 有用 | 11 | 0 | 1.18 | 6 | 2 / 11 |
| **噪音** | 18 | 1 | 2.28 | 10 | 新指標:★裁乙改「輸出前 3 名必看命中率」`out_top3_must`★(甲案固定席版是死表,d4) | `retrieval_eval.py` | 接線照 `fusion_p`;歸因用總開關對照 |(✅ 2026-08-24 done,乙案首量 train 0.46/held 0.08) |

★**九個必看項的扇出全部是 0,一個例外都沒有。**★
扇出最高的幾條全是噪音:`slim-install-安裝器`(10)、`lumos-cli-lifecycle`(5,在 E10/E18/E21/E22
**四題裡都出現且都是噪音**)、`slim-get-一行安裝`(5)。

**解釋**:一篇筆記提到越多支程式檔,它對「任何一次改動」都會被判成 direct;
合約 + direct 就無條件保送 → **它對誰都相關,等於對誰都沒有資訊量**。

## ★先被打掉的兩個方向(留痕,免得重試)★

**① 調 direct 基分(權重層)——無效。**
旋鈕掃 `LUMOS_IMPACT_DIRECT_BASE` 0.30/0.20/0.12/0.05:
P@8 = 0.6094 / 0.6228 / 0.6156 / 0.5948。最好的 0.20 只比現況高 0.013
(**分母 64 格、一格 1.6%,連一格都不到**),而且★必看命中與固定席噪音四個值下完全不動★。
——再次確認 [[Projects/檢索edit面真紅_計劃]]「病在候選層非權重層,調權重天花板極低」。

**② 固定席要求最低詞彙證據——★不能做,會砍錯人★。**
原假設「噪音的詞彙相似度接近 0,卡下限即可篩掉」。實測**完全相反**:

| 標註 | L 中位 | L=0 的比例 |
|---|---|---|
| 必看 | 0.753 | **33%** |
| 噪音 | 0.285 | 5% |

卡下限會**最先砍掉三個必看項**(`code-loop守衛main-direct盲區` L=0 出現兩次、
`autonomous-iteration-loop` L=0)——★那正是固定席存在的理由:接住「字面完全不像但必看」的東西★。
**固定席刻意不看詞彙證據,加下限等於拆掉它的核心功能。**

## ★實驗結果:二元砍除有效但傷召回,棘輪擋下★

實驗版旋鈕 `LUMOS_IMPACT_PIN_FANOUT_MAX`(扇出≥N 的合約節點不保送、降自由席競爭):

| 門檻 | P@8 | 必看命中 | 固定席噪音 |
|---|---|---|---|
| 0(現況) | 0.6094 | **26/29** | 15 |
| **2** | **0.6875(+5 格)** | **23/29** ⚠ | 14 |
| 3 | 0.625 | 24/29 | 14 |
| 6 | 0.625 | 24/29 | 15 |

★**P@8 漲五格,代價是漏掉三個必看項——must-see 棘輪實測擋下(26→23)。**★

**離線分析為什麼沒預測到**:我原本只算「固定席裡的必看被砍幾個」(答案是 0),
★沒算「被砍下去之後在自由席擠不擠得進 top_k」★。被砍 → 進自由席 → 分數不夠 → 擠出前 8 → 漏檢。
**這個方法論的洞要記住:降級不等於保留,自由席是會被擠掉的。**

★這也是棘輪的第一次實戰價值★:只看 P@8 會判定「+5 格,成功」,
而真相是拿三個必看項換來的。**P@8 罰噪音不罰漏檢,單看它會做錯決定。**

## ★現行「直接相關」算法的解剖(2026-08-23 讀 code)★

**材料只有一種**:節點正文裡用反引號括起來的字串,其中看起來像 repo 內檔案路徑的(含 `/`),
或裸檔名在 `git ls-files` 裡唯一的。**抓到就算 direct。**

**合約判定是「有沒有」,不是「講的是不是這支」**:`_impact_contract` 只問這篇有沒有
★INVARIANT★/★IRREVERSIBLE★ 行,**完全不看那條合約講的是哪支檔**。

實證(那篇在四題都是噪音的節點):`lumos-cli-lifecycle` 2 條合約行、`slim-install-安裝器`
7 條合約行——★**合約行本身一個檔案路徑都沒提**★。它們講的是 CLAUDE.md 注入怎麼做,
跟「改 pre-push」「改 scenario_probe」毫無關係。但因為正文某處順帶提到那些檔,就被判 direct;
因為有合約行,就被保送。

★所以「保送」的兩個條件(有提到 + 有合約)★**各自成立,但彼此無關**★——
它保送的不是「這支檔的合約」,是「某篇提到這支檔、而那篇剛好在別處有合約」。

### 三個缺口,從根本到表面

| # | 缺口 | 現況 | 說明 |
|---|---|---|---|
| ① | **提到 ≠ 關於** | 一視同仁 | 正文提到 20 支檔的筆記,對每一支都是 direct——這正是扇出訊號在量的東西 |
| ② | **合約的射程** | 不看 | 合約行自己沒提檔 → 無法判「這條合約護的是哪支」→ 只能整篇保送 |
| ③ | **提到的位置** | 不分 | 標題/KEY 行提到 vs 正文某段順帶提到,權重相同 |

★②是最根本的★:如果合約行能綁到檔(它現在綁的是測試 `[test:]`,不是檔),
「保送」就能精確到「這支檔有合約護著」而不是「這篇筆記某處有合約」。
**但那要改寫作規範,是大動作**;①③是純讀側,可先做。

## 世界解對照(2026-08-23 搜)

**追溯連結復原(Traceability Link Recovery)**是這題的學名——「需求/文件 ↔ 程式碼」的連結,
文獻從 2002 年(Antoniol 等)做到現在。

- **共識一:精確度才是工程成本所在**——多撈的假連結要人工一條條排除,
  所以文獻一致把 precision 看得比 recall 重。★這跟我們現況(固定席 47% 噪音)對上。★
- **2025 LLM 研究(arXiv 2506.16440)列的三種假連結**:
  ①命名式假設(superficial name matching)②幽靈連結(phantom)③架構模式過度泛化。
  ★我們的 direct 判定就是純①——字串出現即連結。★
  該研究另指出「一對多的任務框架」對表現是關鍵——
  我們的 impact 正是「一支檔 → 多篇筆記」,框架對了,**材料太薄**。
- **沒搜到的**:專門處理「hub 文件」(一篇連到一大堆檔)的文獻。
  IDF 降權是 IR 的標準解(詞出現在越多文件裡越沒資訊量),本案的扇出就是把它套到節點層——
  ★是 borrow-design,不是自創★。

## ★綜合研判:三層可做,由便宜到貴★

| 層 | 做法 | 動什麼 | 預期 |
|---|---|---|---|
| **A 讀側・扇出降權** | 高扇出合約節點不佔固定席前排(排末位或給上限) | `impact ranked` 一處 | 噪音↓;★實驗證實二元砍除傷召回,要降不要砍★ |
| **B 讀側・提到的位置** | KEY 行/標題提到 > 正文提到;只在正文順帶提到且扇出高 → 降 | 同上 + 抽取時記位置 | 區分「關於」與「提到」的第一步 |
| **C 寫側・合約綁檔** | 合約行可標 `[file:]` 指明護的是哪支;保送改看「這支檔有無被某合約點名」 | 寫作規範 + extract_contracts + impact | ★治本★,但要全庫補標、是大動作 |

**建議順序 A → B,C 另案**。A 已有實驗數據;B 材料在抽取時就有(`_refcheck_scan` 知道每個
claim 在哪一行),只是沒往下傳;C 動到寫作規範,要過 design-loop 而且影響所有專案。

## ★主案:語意「關於」欄位(模型標、讀側查、可重算)★

### 為什麼不是「用模型即時判」

圖譜明文:**模型永不出現在分數計算路徑上**([[Projects/標註刷新_計劃]] 刻意不做)。
理由不是模型不準,是**可重算**——同一份輸入跑兩次數字不同,就分不出「改動造成的」
與「模型隨機造成的」。2026-08-22 整天在追的是 ±0.03 的差,模型進計分那個精度就沒了。

**但「離線預標、線上查預標」沒有這個問題**:預標是資料,資料是決定論的。
語意判斷發生在寫入側;讀側多一個「查欄位 + 比日期」的判斷,仍是決定論、可重算。
★這不是退讓,這是把信任放對位置。★(r2:原句「讀側不變」已改——r1 自稱已刪卻漏了此處與 decisions)

### 欄位設計

frontmatter 新欄 `about_code`(純清單,值=repo 相對路徑):

```
about_code:
  - scripts/hooks/pre-push
  - scripts/lumos
about_code_stamp: codex/2026-08-23/3f9a1c0b7e2d
```
(★std-r2★:三段式 `<誰標>/<日期>/<正文 sha256 前 12>`;批次寫入時誰標=`batch-<日期>`;revert 只看第一段不受影響。
r2 曾統一成兩段「記日期不記雜湊」——std-r2 證明日期表達不了順序,★繞回 r1「欄位設計」節原本含雜湊的三段格式★(r1 原文 `<sha256 前 12 碼>/<誰標>/<日期>`,r2 為同形 Check S 改掉;過期守衛節的 r1 段是日期制,兩節當時就不一致——s3f2 抓到「繞回」一詞歧義),見過期守衛節。)

語意:**這篇筆記主要在講這幾支檔的行為**(不是「提到」)。
★判準給模型的原話★:「改這支檔的人,不看這篇會不會做錯事?會 → 列;只是順帶提到 → 不列。」

★r1 訂正(s3f1 blocker):這**不是**「與考卷必看同一把尺」★——離線驗證已量出
「關於」比「必看」嚴(train 必看 2/9、held 3/5 被判「不關於」),兩者問的是不同問題:
「關於」=這篇在講這支;「必看」=改這支時該看。`rater-instructions.md` 對「必看」
還限定在「合約/事故/直接規格」子類(s3f6),about_code 判準沒這個範疇。
**正確說法:about_code 是「必看」的一個高精確度子集,不是它的等價物。**
考卷能量到它的「精確度貢獻」(噪音降幾條),量不到它的「召回貢獻」(本來就不是它的目標)。

### 讀側怎麼用(★r1 大幅改寫★)

**r1 發現原設計打錯靶(s1f2/s1f3/s1f4 major、s2f1 blocker)**:固定席保送有★三條獨立路徑★——
①`direct` + 合約(`scripts/lumos:14202` `pinned = bool(contract)`)②`indirect` + 合約且 hop≤1
(`:14213`)③`incident`(事故類)不看合約一律保送(`:14178`)。原設計只改①。(行號 std-r1 s2f1 校正)
**實測 E10 改 pre-push:8 席固定席只有 1 席是 direct,6 席是 indirect**——原修法字面上攔不到它們。

★r2 再改寫(s3f1/s3f2 blocker):r1 版「有欄但不含 → 降自由席」★會讓已標記的節點比沒標更差★★

r1 版的問題用實測打穿:`Issues/hook卸載殘留註冊`(事故類,`pitfall_when: content:HOOK_ENTRIES`)
改 `scripts/test_lumos.py` 時靠事故路徑無條件保送;但它的 about_code 只列 merge-claude-settings.py
與 lumos(它講的是卸載沒清乾淨,不是針對 test_lumos.py)。照 r1 規則 → 有欄但不含 → **被降**。
**「改 A 出過事」的筆記不會列 B,但改 B 的人看到它不虧——事故路徑的價值正在這裡。**
加上 about_code 對「必看」本就有 2/9、3/5 的漏標,降級規則會把那些必看項主動踢出固定席——
★這是負向作用,「零退化」承諾在有欄的節點上不成立。★

★改寫後的規則:about_code **只加分、不降級**★
- 節點有 `about_code` 欄且含目標檔 → 標 **`about_hit: true`**;★前提:它已經由三條既有路徑之一進了候選集★
  (沒字串提到、沒圖邊、不是事故觸發的節點,about_code 再命中也不會被掃到——about_code **不是第四條入口**,
  只在既有候選裡重排;impl-r1 s1f3 抓到原句「不論它由哪條路徑進來」會被讀成獨立促升)。
  pinned 者排固定席前段,free 者不動位置
- 節點有 `about_code` 欄但不含目標檔 → **照三條既有路徑判**,該保送還是保送,只是排在 about 命中者之後
- 節點沒有 `about_code` 欄 → 三條既有路徑照舊

**代價**:精確度來源變成「排序」而非「剔除」——噪音仍在固定席,只是被擠到後面。
對 P@8 無影響(P@8 不計固定席),對 hook 顯示有影響(前排先看到對的)。
★噪音剔除這件事,改由 A 層承擔(2026-08-24 落地:硬合約保送+lane 參考道,見 [[Projects/固定席降噪A層_計劃]];原擬的扇出=二元砍除已試已殺,分級降權未試),about_code 不碰召回。★
must-see 棘輪仍跑,但它量的是這條規則**沒動到的東西**(召回不變是設計保證,不是棘輪保證)。

**「零退化」的精確範圍(s2f4)**:只保證「無 about 欄的節點,其 pinned 判定不變」;
**不保證**它在固定席內的相對名次不變(有 about 的會插前面)。名次變動對 P@8 無影響
(P@8 不分固定席內順序),對 hook 顯示順序有影響——接受。

### 存量與增量

| | 做法 | 誰做 |
|---|---|---|
| **存量**(83 篇) | ★r1 改寫(archf5 major)★:**走 `refresh_labels.py` 同款雙評審**。★r2(s2f6):既有 Codex 單席預標(`about-code-prelabel-2026-08-23.json`)當 A 席沿用,只補跑 B 席(Gemini),不重標★——A 席 Codex、B 席 Gemini(或反之),merge → 不一致人裁 → apply 寫入。★不是「單模型標完人抽驗」★:那比 goldset 的寫入紀律薄,卻產生等重的資料。寫入用 `lumos append`(清單欄位;s1f6/archf1:`lumos set` 只認純量,字面操作會被擋) | 已有流程,成本 ×2(約 20 萬 token) |
| **增量**(新寫的) | ★r2(s3f6):`lumos new` 四種範本與 NEW_HINT 都要加 `about_code:` 空欄與一句提示★,否則「填」無從發生;★但驗證用的標註者是 Codex 批次、上線後是 Claude 逐篇(s3f4)——兩群不同★,增量的品質要另驗:新節點的 about_code 進下一次考卷 delta 補標時,看雙評審跟它一致率 | 寫作規範 + 範本欄位 |

★兩個欄位要註冊進 `LIST_KEYS`(about_code)與 `SCALAR_KEYS`(about_code_stamp)白名單(s2f7 minor)★,
否則 append/set 都會 rc2。

★r1 訂正(s2f1 blocker):範圍刀不是 61 篇★——「固定席只保送帶合約的」是錯的(見上,三軸)。
正確範圍=**固定席三軸會碰到的全部節點**,離線驗證實測為 **83 篇**(合約 61 + 風險標籤/事故 22),
預標資料已在 `governance/eval/about-code-prelabel-2026-08-23.json`。
其餘約 250 篇不在固定席射程,等 83 篇驗出效果再說。

★巨檔失效條件的機械判定(s2f2 blocker)★:離線驗證 held 那題 22 個誤放全出自改 `scripts/lumos`
——它是本 repo 改最勤的檔(`git log --since="7 days ago" -- scripts/lumos` = 31 次),
每次改動 hook 都跑 impact。**不定義門檻就上線 = 天天複現 22 誤放**。
★甲案收窄後重定義(r3 s2f4)★:巨檔門檻不再是「恢復鑑別力」(那是降級時代的語言),
是**「上限 about 加分的範圍」**——被改的檔若 `about_code` 命中 ≥ N 篇,全部都排前排等於沒排,
此時關閉加分、固定席順序退回三軸既有排序。N 暫定 8。
★22 個誤放與此無關★:它們是三軸保送進來的,about 開關不影響它們在不在,只影響順序。
N 要用考卷驗(train 掃 N∈{5,8,12}、held 驗一次)。
★r2(s1f5/s3f7):這個反向計數現在沒地方算★——`cmd_impact` 開頭對 `env.notes` 全掃一次
`about_code` 建 `{檔: 節點數}`(同 `_BASENAME_COUNTS_CACHE` 行程內快取先例),
★單一實作,hook/CLI/eval 共用★,否則三邊會算出不同的巨檔判定。

★回滾路徑(r2 改寫;s1f1/s3f3 blocker:`lumos query` 沒有 `--field/--match`;s1f2/s3f4:`remove` 要三個位置參數)★
批次預標寫入時 `about_code_stamp` **第一段(誰標)**固定寫 `batch-<日期>`(★std-r2 後三段式:`batch-2026-08-23/2026-08-23/<正文雜湊 12 碼>`;s3f3 抓到此處範例沒跟上——apply 那半未做,照抄兩段式會讓新資料落地即被判舊格式★)。
整批撤=**本案要新增一個子命令** `lumos about-code revert --batch <日期>`:掃 `env.notes`、
找 stamp 第一段 = `batch-<日期>` 的節點、對每篇把 `about_code` 清單逐值 `cmd_remove` 並刪 stamp。
★這是本案新增的工具清單第一項★,不是既有指令的組合(既有 `query` 只能按 tag 篩、`remove` 逐值)。
人工修正過的節點 stamp 第一段會變成 `claude/...`,不在 batch 範圍,不會被誤撤。

### ★過期守衛(沒有這個就別做)★

預標會過期:筆記正文改了,`about_code` 可能就錯了。**這跟 goldset 標註過期是同一個病,
2026-08-22 才踩過**(候選池釘在建檔當時,語料前進後一堆未標)。

★r1 改寫(archf4 major:原設計會長成第三套「宣稱 vs 事實」機制;s1f5:「讀側不變」宣稱錯)★

**不另立機制,併入 Check S**(★此句已被 r3 s3f11 翻案:Check S 只掃 system,事故類驗不到→另開迴圈同輸出格式;見工具清單 #6。std-r1 s1f2 抓到這裡沒改★)。Check S 現在只比 `self_audit` 的日期與 `updated`
(`scripts/lumos:823-841`,零讀盤)。about_code 的過期判定改成同一形狀:
`about_code_stamp` 記 **日期**(不記雜湊),過期判準 = `updated` > stamp 日期。(★r1/r2 日期制整段已被 std-r2 正文雜湊取代,以下到「讀側」段皆留痕★)
★代價★:正文沒改只改 frontmatter 也算「可能過期」(偽陽性)——接受,因為 Check S 本來就這樣,
**一致性比精確性重要**(接手的人只要學一套)。
格式沿 `self_audit` 兩段式:`about_code_stamp: codex/2026-08-23`(archf2 minor)。

★r2 補(s3f5 major):`updated` 欄本身紀律不足★——席三抽 15 篇,**5 篇(33%)的 `updated`
落後於 git 最後改動日期**(正文改了沒 `lumos set updated`)。用 `updated` 當過期判準會**沉默放過**
這些節點——偽陰性,代價比偽陽性高(正是 about_code 要防的那個方向)。
**處置**(★已被 std-r2 取代,留痕★):過期判準改成 **git 最後改動日期**(`git log -1 --format=%cs -- <檔>`)> stamp 日期;
git 缺席時退回 `updated`(★std-r1 再改:git 缺席視同無欄,不退回 updated★)。這跟 Check S 不再完全同形,但 Check S 本身也該這樣修——另立 Issue 不在本案。

**讀側**(過期定義見 std-r2;本段其餘仍成立):`impact` 遇到過期的節點 → **不信它的 about_code**(當沒有欄位處理),退回三軸既有路徑。★這確實是讀側多一個判斷(s1f5 對)★,但成本是比兩個日期字串,
不是算雜湊;席二實測 impact 全庫重讀 0.75s,這個判斷毫秒級,**不構成熱路徑問題**(★std-r1 s3f6:這句只算了比字串,沒算 git log 那 0.2s——見下方懶觸發★)
(s1f5「進熱路徑」那半駁回,「讀側不變」那半接受——原句已刪)。
降級方式對齊 E1 的 warn_soft 慣例(archf3 minor):doctor 列出、不擋;impact 退路徑、印一行★到 stderr★
(std-r1 ext-e3:「印一行」與測試「逐 byte 相同」打架——定義:提示只走 stderr,逐 byte 比的是 JSON stdout / results 物件)。

★std-r1 改寫(s1f1 blocker、ext-e2 major、s2f7/s3f6/s1f4 major 三席獨立撞到)★(★本段方案已被 std-r2 整段取代,留痕;見下方 std-r2★):**「日期」這把尺太粗,會信到已過期的標記**——
① 筆記改了還沒 commit,git log 看不到;② 標完當天又 commit 一次,日期相同、嚴格小於判不出來。
兩種都是「偽陰性」,正是這道守衛要防的方向。**處置(不加子行程數)**:
- 批次 git log 本來就逐 commit 掃,順手數「最後改動日當天這檔有幾個 commit」:新 helper
  `git_last_change_info(repo_root, vault)` 回 `{rel: (date, n_same_day)}`;`git_last_change_dates` 改成它的薄包裝(回傳型別不變,既有測試不動)。
- 再一次批次 `git status --porcelain -- <vault>` 抓沒 commit 的:`git_dirty_notes(repo_root, vault)` 回 set,同款行程內快取。
- **過期 = git_date > stamp_date,或 (git_date == stamp_date 且 n_same_day ≥ 2),或 rel 在 dirty set**。
- ★代價(誠實)★:標記當天若先改兩次 commit 才標,會被誤判過期——方向是「不加分」,安全;doctor 會列出來,人看一眼 `lumos set about_code_stamp` 就好。
- **git 缺席 → about_code 視同不存在**(不再退回 `updated`;std-r1 順手砍掉這條 33% 不可靠的後備,讀側與 doctor「找不到 git 就略過」一致)。
- **成本(s2f7/s3f6 實測 0.215s 全庫 git log;hook 每次是新行程,行程內快取對 hook 無用)**:★懶觸發★——只有「至少一個候選節點的 about_code 含目標檔」時才呼叫 git;
  `--incidents-only` 快速路徑(hook 冷卻期)**完全不碰 about**(s1f4)。沒命中就零成本;命中時 +0.2s 一次,可接受、且在總開關之下。

★★std-r2 改寫(ext-f1 blocker + s1f2:「同日 ≥2 commit」**解除不了**——重標後日期同、計數同,永遠過期;s1 實證 83 篇裡已有 2 篇上線首日誤判;
s1f3/s2f1/arch 三席撞 `git status` 漏 quotepath;s2f2 rename 格式;s2f4 stamp 日期怎麼抽;arch ⚠/s3f3 快取歸屬——這一整串都是「用 git 推測正文有沒有變」的下游)★★
**根本問法錯了**:守衛要答的是「標記時看的正文,跟現在一樣嗎」,那就**直接記正文雜湊**,不要拿日期或 commit 去推:
- stamp 加第三段:`about_code_stamp: <誰>/<日期>/<正文 sha256 前 12 碼>`。正文 = `split_frontmatter(text)[1].rstrip()`(frontmatter 之外的全部;
  ★讀檔必用 `read_text(encoding="utf-8-sig")`★(std-r3 arch major + s1f3:全檔 20+ 處讀 vault 都用 sig,BOM 檔否則切不出 frontmatter、整檔算進雜湊,「只改 frontmatter 不過期」就破);
  第三段必須是 12 碼 hex,否則視同舊格式(s2 minor:`lumos set` 不驗格式,任何字串都寫得進去);
  `lumos set`/`append` 只動 frontmatter,**不會**讓它過期——about_code 自己就在 frontmatter 裡,重標不會自我過期)。
- **過期 = 現在算出的正文雜湊 ≠ stamp 第三段**。stamp 沒第三段(舊格式)→ 視同過期,doctor 列「舊格式,請重標」。
- 新 helper `note_body_hash(vault, rel)`(讀檔→split→hash;★無快取,無 git,無子行程★)。impact 只對「about 命中的候選」算(懶觸發,幾次讀檔、毫秒級);doctor 對所有有 stamp 的節點算。
- **恢復動作成立**:`lumos about-code restamp <節點>` 重算第三段——這次重標真的會讓它不再過期(ext-f1 要求的可操作性)。
  ★std-r3 語意釘死(Codex f1 blocker「橡皮章」+ s1f2 blocker「跟 revert 打架」)★:
  restamp 的意思是「**我(人或 Claude)剛核過這篇的 about_code 對現在的正文仍然正確**」——所以它**三段全換**:`claude/<今天>/<新雜湊>`
  (`--by <誰>` 可改第一段,預設 claude)。第一段離開 `batch-` 後,`revert --batch` 就不會再撤它(合約候選 #4 在「用官方工具修正」這條路上成立)。
  沒有 stamp 的節點(增量新寫的)第一次也用同一指令。★`--expired` 批次模式拿掉★——一口氣把所有可疑標籤洗白正是橡皮章。
  doctor 的訊息不說「重標」,說:「先看這篇的 about_code 對現在的正文還對不對:對 → `restamp`;不對 → `set/append/remove` 修完再 `restamp`」。
  ★已知限制(s1f4 minor)★:BOM/CRLF 檔 `load_raw_for_edit` 直接拒寫,restamp 會 loud fail,目前 vault 零此類檔。
- **git 完全退場**:`git_last_change_info`/`git_dirty_notes` ★不建★;`git_last_change_dates`(#5,已 ship)保留但本案不再呼叫(工具清單 #5 誠實標「暫無呼叫者」);
  未 commit 的改動自然被抓到(讀的是工作樹);中文路徑、rename、quotepath、快取歸屬、hook 每次新行程——全部不再是問題。
- **代價(誠實)**:正文改一個字就過期(比日期嚴)——這正是要的方向;doctor 每天會列出來,restamp 一行。
  跟 Check S(日期制)不同形——r1 架構席「第三套機制」那條在這裡**再次**被推翻,理由是兩輪五席實證日期制表達不了順序;留痕,不再折回。
- **83 篇存量遷移**(★std-r3 改寫,Codex f2 blocker:「用現在的正文算」=橡皮章,標完之後改過的會被洗成新鮮;s2f5:遷移一次性用 git 可以,但別重寫 quotepath 坑★):
  `lumos about-code migrate-stamp --at <commit>`(一次性,做完可留著當工具):對每篇 `batch-*` 兩段式節點,
  用 `git show <commit>:<vault 相對路徑>`(★路徑當參數傳,不經 git 輸出,無 quotepath 問題★)取出**標註當時**的正文算雜湊 → 寫成第三段(第一、二段不動,仍是 batch)。
  `<commit>` = 最終寫入 commit 的前一個(`dbd104f^`,2026-08-23 22:19;B 席 Opus 讀的是那時的正文)。
  ★寫入後立刻由 doctor/impact 用現在的正文比:標完之後改過正文的那幾篇自然就是「過期」,進 doctor 清單給人核(核過才 restamp)——不需要任何人猜哪幾篇★。
  另列「12:19(A 席讀)到 22:19 之間正文動過的」(`git diff --name-only 54b3334 dbd104f^ -- <vault>`,一次性)給人掃一眼——A/B 兩席可能讀到不同版本。
- `LUMOS_IMPACT_ABOUT=0` ★也關 doctor #6 的迴圈★(s1f6:總開關只關一半等於沒關)。

### ★離線驗證結果(2026-08-23,見 [[Verification/2026-08-23_關於欄位離線預標驗證]])★

Codex 預標 83 篇後對照考卷:**train 18 條噪音零誤放、必看 7/9 命中**;
held 撞到失效條件——改 `scripts/lumos`(巨型單檔)那題 22 個誤放,**排除該題 held 噪音 0/60**。

由此定三條:
1. 「關於」訊號成立,鑑別力遠勝扇出 → **主案方向確認**。
2. ★失效條件:被改的檔是巨型單檔★ → 對那類檔退回字串+扇出,或切函式級(待審)。
3. 「關於」比「必看」嚴——**用法是加權不是砍除**,且「實作在哪」與「影響誰」可能要分兩欄。

### 成本與風險(誠實)

- **過期率未知**。本 repo 筆記改得很勤;若過期比補標快,會變成「永遠有一堆過期的」。
  ★r1 訂正(s3f3):門檻對齊既有未標率週閘的 **10%**(`refresh_labels.py:364`),不是拍的 30%★。
  重驗條件:跑一個月後數「過期/總數」,>10% 就進週閘自動產表。
  - REVISIT:2026-09-26 數 about_code 過期率(>10% 進週閘產表;上行條款)
- **成績單(★甲案重定★)**:about_code 收窄後**不動噪音數也不動 P@8**,既有兩把尺都量不到它。
  成績單改為**固定席前 3 位的必看命中率**——新指標,要在 retrieval_eval 加(本案新增工具清單項)。
  離線可先算:對 train 8 題,about 開/關兩種排序下「前 3 席有幾個標 2」。
  must-see 棘輪仍跑,當回歸守衛(確認收窄後真的零退化)。
- **寫作規範多一條**。本 repo 已有十五萬字散文紀律、零條被量過效果
  ([[Issues/散文紀律沒有退場機制]])。★必須配機械守衛★:帶合約的節點沒填 `about_code`
  → doctor 喊;否則就是第十五萬零一條。

### 三條線的關係(改寫)

| 線 | 地位(★甲案收窄後★) | 解什麼 | 對 P@8 |
|---|---|---|---|
| **C 關於欄位** | 本案主體,**收窄為排序+欄位基礎** | 固定席內誰先看到;日後語意查詢的材料 | **零**(P@8 不計固定席) |
| A 層降噪 | ★2026-08-24 已由 [[Projects/固定席降噪A層_計劃]] 實現(硬合約+參考道;扇出二元砍除已試已殺,分級降權未試)★ | 固定席噪音剔除 | held 噪音 -45% 級(knob 轉正時實測) |
| B 提到的位置 | 擱置 | — | — |

★r3 s2f1 的誠實回答★:**現在沒有機制在剔噪音**。C 只排序;A 另案未做。
噪音數(15 條工具口徑)在本案落地後**不會變**,變的是它們在固定席裡的位置。

## A 層(過渡)的修法方向(★2026-08-24 已由 [[Projects/固定席降噪A層_計劃]] 取代——採硬合約保送+參考道,非本節擬的扇出降權;本節留痕★)

**不是砍除,是降權**——被判高扇出的合約節點:
- (a) 仍保送,但**排在固定席末位**(不佔前排,但不會掉出去);或
- (b) 降入自由席,**但給補償分**讓它仍有競爭力;或
- (c) 每題固定席**設數量上限**,超過的按扇出由高到低降級。

★三者都沒實測★——本節點只承載診斷與離線實驗,不動產線 code
(動 `impact` 排序=演算法密集,規矩是走完整 design-loop,light 硬否決)。

## ★下一步:「影響」欄位(2026-08-23 Enzo 問「標籤能不能分提到和關於」後驗的)★

關係不只兩種,至少四種:提到/關於/影響/教訓。about_code 只蓋「關於」;
「不是在講你、你改了卻會出事」那類(r2 s3f1 事故案例、r1 anchor-integrity 案例)要靠「影響」。
離線驗證見 [[Verification/2026-08-23_影響欄位離線驗證]]:工具鏈 4/8、Landmark 17/18 但多列 56,
★共改歷史當尺篩掉一半★(27 有共改 / 29 無)。

**設計方向(未審)**:新欄 `impacts_code`,判準與 about_code 分開問;寫入流程多一道共改篩;
事故類節點優先標。★用法不照 about 那套★——平均一篇十幾支,塞固定席等於什麼都推;
可能是 hook 提示層不是排序層,未定。**本案不做,另案。**

★證據語料轉交(2026-08-24,pin-denoise-a 案調研+v4 Codex r1 f1 裁定)★:「必看但 about 不含」的 15 處(9 篇;含 E06/E12 anchor-integrity←pre-commit/impact-hook.py、E08 design-loop←test_autonomous_loop.py)★不是 about 漏標★——about=「這篇在講哪支」,它們是「改哪支會出事」=impacts_code 的語意;整批當本節立案語料,勿補進 about(會汙染欄位定義)。

## ★本案新增/修改工具清單(r3 s1f7/s3f12 要求彙整;甲案範圍)★

| # | 項目 | 落點 | r3 抓到的坑 |
|---|---|---|---|
| 1 | `about_code` 進 `LIST_KEYS`、`about_code_stamp` 進 `SCALAR_KEYS` | `scripts/lumos:7243-7244` | ✅ 2026-08-23 done,測試釘 append/set/remove 三路 |
| 2 | 範本加 `about_code:` 空欄 | ✅ 2026-08-23 done:system/issue 範本 + NEW_HINT 兩段提示(事故類「只寫出事那幾支」) | `[]` bug ✅([[Issues/範本空清單被判成純量]]);★範圍刀:只 system/issue,同 aliases★ |
| 3 | 純量欄位刪除原語 | ✅ 2026-08-23 done:`remove <節點> <key>` 不帶 value=整欄拿掉 | 不加新子命令(一個指令學一次);守衛:骨架欄 type/status/created 擋、清單欄不准省 value |
| 4 | `cmd_impact` 讀 `about_code`:四處 `results.append` 命中時加 **`about_hit: True`**(只在 True 時出鍵;★不動既有 `hit` 欄★);`pins` 後 stable sort 鍵 `(kind!="incident", not about_hit)`;總開關 `LUMOS_IMPACT_ABOUT`;★about 命中後才讀該篇正文算 `note_body_hash`,不得呼叫 `git_last_change_dates`★(Codex r3 f3:原寫「懶觸發 git」是 std-r1 殘句);計數切 `_impact_about_counts`(計數路徑也要 `as_list`,s2 minor)(✅ 2026-08-24 done,見 [[Verification/2026-08-24_about_code讀側四項落地]]) | incident `:14178` / direct `:14203` / indirect pinned `:14214` / indirect free `:14223` / `pins` `:14226`(impl-r1 s1f4 校正;舊行號整批過期) | 三條路徑各自獨立(s3f9);★`hit` 欄是既有來源標記(body-inline-code/basename-match),hook `:358`、lumos `:14310` 在讀,覆寫會靜默失真(impl-r1 s1f2 blocker)★ |
| 5 | 過期判準:**批次** `git log --name-only --format=@%cs -c core.quotepath=false`(`@` 前綴是分隔關鍵,s1f8)一次拿全庫。★std-r2:本案改記正文雜湊,這支 helper **保留但暫無呼叫者**(s3f4 要求 ✅ 只蓋已 ship 的那半;std-r1 擬的擴充不建);★它與其測試的 docstring 還寫「about_code 過期判準的材料」,實作時改掉(std-r3 s3f5)★ | ✅ 2026-08-23 done:`git_last_change_dates(repo_root, vault)`,行程內快取,fail-open | 翻紅釘實證:★拿掉 quotepath 旗標連英文檔都撈不到★(路徑帶中文目錄名整條被跳脫),表空且不報錯 |
| 6 | 過期檢查:**不併入 Check S**(它只掃 type:system,事故類驗不到,s3f11)→ 另開迴圈但同輸出格式;★std-r2:比正文雜湊,不需 git/repo_root;受總開關★(✅ 2026-08-24 done,Check S2) | `run_doctor`,逐行格式對齊 `sa_stale` 段 | 這是 archf4「第三套機制」的回歸,但 r3 證實併入 Check S 會漏——★兩害取輕,留痕★ |
| 7 | `lumos about-code revert --batch <日期>` 子命令 | ✅ 2026-08-23 done,含 --dry-run;★std-r1 s3f8 修:單篇部分失敗原本照刪 stamp 照算成功(重複值甚至直接崩潰)→ 去重、失敗留 stamp 不計、rc 非 0,翻紅釘驗過★ | 翻紅釘:比對改「含日期」→人工修正的被誤撤,精確比對第一段才對;新指令觸發三道登記守衛(help/索引/六份文件指令數 61→62) |
| 8 | 雙評審:**寫轉換函式** `{node:[files]}` → `{node:{file:1}}` 再餵 `cmd_merge`;`cmd_apply` 不能重用(寫入目標是 goldset 不是 frontmatter),另寫 | ✅ 2026-08-23 `about_code_to_rater(a, b)`,真餵 merge 驗過 | ★候選集=兩席聯集★:A 列 B 沒列的,B 側填 0(那是反對票不是沒意見);翻紅釘驗過。apply 那半未做 |
| 9 | hook 顯示層加 `about` 標示(讀 `about_hit`,不讀 `hit`)(✅ 2026-08-24 done,讀 about_hit) | `scripts/hooks/claude/impact-hook.py:344-348` | 不改看不到(s2f5/s3f9);hook 一律帶 `--ranked`,`build_additional_context`(非 ranked 那條)是死碼不用動(impl-r1 已驗;函式名 std-r1 校正) |
| 10 | 新指標「固定席前 3 位必看命中率」(✅ 2026-08-24 done,首量 train 0.29/held 0.12,有無 about 幾乎同值) | `retrieval_eval.py` | 甲案成績單;接線照 `fusion_p`(s1f5) |
| 11 | ★std-r2 新增、std-r3 釘語意★ `lumos about-code restamp <節點> [--by <誰>]`(三段全換=人核過)與 `migrate-stamp --at <commit>`(只補第三段,一次性);`note_body_hash(vault, rel)` helper(utf-8-sig)(✅ 2026-08-24 done,83 篇已 migrate @dbd104f^,0 篇過期) | ★兩處接線★(s2f4):argparse 二層註冊(`about-code` 底下與 `revert` 並列)**和** dispatch 分支(漏了會靜默 rc=2);登記守衛只有 `t_every_subcommand_has_when`(help)會擋,索引那道不掃 about-code、文件指令數已在 #7 算過——★索引要人工補★(s3f4) | ext-f1/Codex f1/s1f2:恢復動作要能解除過期、但不能是橡皮章、不能跟 revert 打架 |

★#6 誠實記★:r1 架構席判「過期守衛另立=第三套機制」為 major,折成併入 Check S;
r3 證實併入後事故類節點驗不到。兩個都是真問題,選「另開但同輸出格式」——接手的人看到的是同一種提示,
實作是兩個迴圈。這是取捨不是解法。

## ★剩四項的實作規格(2026-08-23,送 light 審)★

#1/#2/#3/#5/#7/#8 已落地,存量 83 篇已寫入。剩四項全碰設計判斷,規格如下,★每項都標明「光看 P@8 量不到」★。

### #4 impact 讀 about_code:只加分、不降級、排前排(★std-r2 折入後版★)

★行號政策(s1f4/s2f7/s3f1/ext-f3 四席抓到行號整批漂 +15/+38——同一份 spec 跟 code 同日在動,行號守不住)★:
以下引用以**函式名/字串錨**為準,行號只是「本次寫時」的快照(2026-08-23 晚),實作者 `grep -n` 重對。

- **總開關(impl-r1 s1f5)**:`LUMOS_IMPACT_ABOUT`,走 `_impact_knob`(`def _impact_knob`,≈:13898),
  預設 1、0=整個 about 判定關閉(不標、不排序、不掃計數、不讀正文算雜湊)。同 `LUMOS_IMPACT_BASENAME_MATCH`(≈:13624)的「預設開/0 逃生」慣例。★下面所有「關閉 about 時」都指 knob=0★。
- **判定**:候選節點 `as_list(fields.get("about_code"))` 含目標檔(repo 相對路徑精確比對;值指到不存在的檔不驗、只是永遠不命中,s2f10)→ 在 results 項加 **`about_hit: True`**。
  ★只有 True 才出現這個鍵★(s2f2 blocker);★讀側一律 `r.get("about_hit", False)`★(std-r2 s1f1 blocker:`r["about_hit"]` 在沒鍵的項 KeyError,正是測試②③④⑤的常態;
  既有慣例 `r.get("hop", 0)`、hook `x.get("hit")` 都是 `.get`)。
  ★必包 `as_list`★(既有一處 `:7680` 有包)。★不覆寫既有 `hit` 欄★(impl-r1 s1f2;★std-r2 s3f5:升格進合約候選第 5 條★)。
  四處 `results.append({"node": x["node"], "kind": ...`(錨:grep 這字串;≈:14193 incident / :14218 direct / :14229 indirect pinned / :14238 indirect free)
  都走同一個判定,★不改任何一條路徑的 pinned 邏輯★——**about_hit 不是第四條入口,free 候選命中後仍是 free**(ext-e1)。
- **排序**:`pins = [r for r in results if r["pinned"]]`(錨;≈:14241)之後加一道 stable sort,鍵 = `(r["kind"] != "incident", not r.get("about_hit", False))`——
  ★事故筆記永遠在最前★(s1f10),事故內部再按 about_hit,其餘保持原序。★不動 `contract_priority`,不動 free/rescued★。
  `cmd_impact_diff` 有自己的純分數排序,**本案不碰**(s3f7,明寫範圍外)。
- **過期**:照「過期守衛」節 std-r2:`note_body_hash(vault, rel) != stamp 第三段`(或無第三段)→ 視同沒有 about_code。★懶觸發★:先掃候選有無 about 命中,有才讀檔算雜湊;`--incidents-only` 整段跳過。
- **巨檔門檻**:獨立頂層函式 `_impact_about_counts(env)`(不 inline,對齊 `_impact_reverse_lookup/_impact_contract/_impact_bfs` 分工,arch ⚠)
  全掃 `env.notes` 建 `{檔: 節點數}`,★行程內快取鍵 `str(env.vault)`★(既有兩個快取都用路徑字串鍵);
  目標檔命中 ≥ `LUMOS_IMPACT_ABOUT_MAX`(預設 8)→ 本次關閉 about 加分(仍三軸照舊)。單一實作,hook/CLI/eval 共用。
- **測試**(fixture 基於 `def t_impact_ranked`,≈test_lumos:13957;★全部走 CLI 子行程,不能 monkeypatch 行程內函式★,s2f5):
  ①★原本就 pinned 的候選★(direct+合約)有欄含目標 → 仍 pinned、`about_hit`、排在非事故 pins 首位
  ②有欄不含 → JSON results 與 knob=0 時逐 byte 相同 ③無欄 → 同② ④過期(正文改一字、不 commit)→ 同②;stamp 無第三段 → 同②
  ⑤巨檔 ≥8 → 同② ⑥翻紅釘:拿掉 stable sort → ①翻紅 ⑦direct 候選的 `hit` 欄在 about 命中後仍是原值
  ⑧★knob=0 → results 任一項都沒有 `about_hit` 鍵,且 pins 序列等於 fixture 預期的三軸原序★(s2f6:「改動前」改成可斷言的定義)
  ⑨free 候選(indirect 無合約)命中 → 仍 free、位置不動 ⑩事故 pin 不帶 about vs 一般 pin 帶 about → 事故仍在前
  ⑪about_code 存成純量字串(單值)→ 仍命中(s2f9) ⑫★`--incidents-only` → results 任一項無 `about_hit` 鍵★(取代原「monkeypatch 計數」)
  ⑬★`lumos set about_code_stamp` 改 frontmatter 後 → 仍不過期★(雜湊只算正文)。
- **預期**:P@8 **不變**;must-see 棘輪 **不變**;固定席噪音數 **不變**(只排序)。★唯一會動的是 #10 那個新指標★。

### #6 過期檢查:另開迴圈,輸出對齊 Check S(★std-r2 折入後版★)

- `LUMOS_IMPACT_ABOUT=0` → 整段 `ok("(about 總開關關閉,過期檢查略過)")`(s1f6)。
- 掃全部 type(不只 system)、★跳過 `status: stale/superseded`★(對齊 Check S 與另四處軟檢查的慣例;arch r3 minor,引句錨不到但我自己查了 `:832`),有 `about_code_stamp` 的節點算 `note_body_hash` 比 stamp 第三段。★不需要 git、不需要 repo_root★。
- 過期 → warn_soft(不擋、不計 issues)。訊息照 Check S **實際**逐行寫法(`sa_stale` 那段,錨:grep `self_audit {sa_date} < updated`):
  `head`=「有 {N} 篇筆記的 about_code 標了之後正文又改過,標記可能過期」、`advice`=「先看 about_code 對現在的正文還對不對:對 → lumos about-code restamp <節點>;不對 → 修完再 restamp」
  (★head/advice 分兩個參數★,對齊 Check S 等五處 warn_soft 呼叫慣例,arch r3 minor;訊息不得說「重標」二字當萬靈丹,Codex f1),
  每行 `f"{rel} (about_code_stamp {stamp} 正文雜湊 {old12} → 現在 {new12})"`;舊格式另列「{rel} (stamp 無雜湊段,舊格式,請 restamp)」。
  (s2f3 那個「同日 `<` 自相矛盾」訊息隨日期制一起消失。)
- ★不併入 Check S★(r3 s3f11)。
- 測試:①issue 類正文改了 → 列 ②未改不列 ③無 stamp 不列 ④舊格式(兩段)→ 列為舊格式 ⑤只改 frontmatter(`lumos set updated`)→ 不列 ⑥knob=0 → 整段略過、不列
  ⑦★第三段非 12 碼 hex → 列為舊格式★ ⑧★BOM 檔(utf-8-sig 寫入)未改 → 不列★ ⑨status: superseded 的過期節點 → 不列。
  ★#4 測試注意(s2f1 major)★:`cmd_impact` **不吃全域 `--vault`**,自己從 `--repo`/cwd 找 vault——fixture 要照 `t_impact_ranked` 的寫法給 `--repo`,
  否則會打到真 vault 還以為測到了;#6 的 doctor 測試走 `--vault` 沒這問題。巨檔門檻那條(要 ≥8 篇指同一檔)★用獨立 vault★,別跟其他 12 條共用 fixture。

### #9 hook 顯示:`about` 標示

- `scripts/hooks/claude/impact-hook.py:344-348` pins 顯示迴圈加:`x.get("about_hit")` → 行首標 `★關於★`(讀新欄位,不碰 `hit`)。
- 測試:既有 hook 測試加一條斷言。

### #10 新指標:固定席前 3 位必看命中率

- `retrieval_eval.py` 的 `eval_edit` 加 `pin_top3_must`:每題固定席前 3 席裡標 2 的個數 / min(3, 該題標 2 總數)。
- 只印、進 history、★不進 gate★(甲案收窄後它是唯一會動的數字,先觀測一個月再決定要不要閘)。
- ★分母為 0 的題(有標 1 沒標 2)→ 該題回 None、不進平均★(impl-r1 s1f10;fixture 要造一題這種的)。
- ★接線(std-r1 s3f3 major;先例欄位 std-r2 s1f5 校正)★:只加在 `eval_edit` 的每題 row 不夠——要照 **`fusion_p`** 的路徑走完
  (`must_pinned_count` 是 raw sum 不是 macro,不是對的先例):row → `report_goldset` 的 `_macro(erows, "pin_top3_must")`(錨:`fp, fn = _macro(erows, "fusion_p")`,None 自動排除)→ `verdict["pin_top3_must"]` → history 行。
  `gates` 字典(`:569-575`)不加。測試斷言要打在 verdict 與 history 那層,不只 row。
- 測試:fixture 造「about 命中排首位」與「不排」兩種,斷言指標差異。

### ★這四項的 tier 判斷★
原自判:#4「只加一道 stable sort,不動評分」light 可;#6「warn_soft 不擋」light 可。
★impl-r1 s1f1 判 light 誤判,我認★:本文件自己在 A 層那節寫「動 `impact` 排序=演算法密集,light 硬否決」,
#4 動的正是 `cmd_impact` ranked 融合區塊(`:14171-14267`)。自判「這次不影響」不能替代審查——
這份文件 r1/r2 已經連續兩次被打穿「不影響」的自判。**升 standard,新編號 `about-code-impl-std`**,
light 那輪的乾淨度不洗回來。

## ★合約候選(design-loop 第 9 步;候選≠已標)★

1. **about_code 只加分不降級**——有欄無命中的節點,pinned 判定與現況逐 byte 相同。
   [test 候選:t_about_code_no_demote——建有欄不含目標檔的事故節點,斷言仍 pinned]
2. **無 about 欄的節點,固定席內相對順序不變**——about 命中者插前,其餘保持三軸排序。
   [test 候選:斷言 pins 去掉 about_hit 者後,序列與 `LUMOS_IMPACT_ABOUT=0` 時一致]
3. **過期即不信**——正文雜湊 ≠ stamp 第三段(或無第三段)的節點,其 about_code 視同不存在。重標(`about-code restamp`)後必不過期。
   [test 候選:改正文一字→視同無欄;restamp→恢復;只改 frontmatter→不過期]
4. **批次回滾只動 stamp 第一段 = batch-<日期> 的節點**——人工修正過的(含 `restamp` 過的,第一段已變 `claude/…`)不被誤撤。
   [test 候選:restamp 後 revert --batch 不碰它;★fixture 用三段式值★(s3f7)]
5. **about 判定不覆寫 results 的 `hit` 欄**(impl-r1 s1f2;std-r2 s3f5 升格)——direct 候選的 `hit` 永遠是 body-inline-code/basename-match 來源標記。
   [test 候選:#4 測試⑦]

## ★調研:必看為什麼只有 8/29 坐固定席(2026-08-24,讀側落地後首查)★

新指標「固定席前 3 位必看命中率」首量幾乎不動(有無 about 同值),追根究柢把 69 對「必看 × 編輯題」逐對驗了席位:

| 席位 | 對數 | 說明 |
|---|---|---|
| direct 自由席 | **31(45%)** | ★結構性:全是計劃/驗證類——固定席保送條件=合約或事故,合約只有 Systems 類會標,計劃/驗證類必看**永遠**進不了固定席★ |
| 不在輸出(無查詢文字診斷) | 19 | 抽 9 驗:6 個是門檻/名額截掉(無 query 時詞彙分=0、direct 底分 0.30 過不了動態閾;hook 實際有 query 會撈回部分——考卷實測只漏 3+2)、**3 個是真召回洞** |
| 固定席(合約 direct 9 + 合約 indirect 3 + 事故 3) | 15 | 就是機械保證涵蓋的那面 |
| indirect 自由席 | 4 | — |

**三個真召回洞的形態**:筆記正文沒提那支檔的路徑、圖上距離 >2(例:自主迴圈的首輪驗證筆記沒寫 `autonomous-loop.sh` 字樣)。
★這正是「影響欄位」(impacts_code,見下一步節)要接的洞——但也只有 3/69,不是主戰場。★

**含意(2026-08-24 Enzo 裁乙,d4)**:指標改量「輸出前 3 名」(`out_top3_must`,不限固定席)。
首量:train 0.463 / held 0.083 / 全體 0.281——held 爛在固定席噪音 82 條塞滿前三行,表是活的、直指 A 層降噪主戰場。
甲案 pin_top3_must 作廢(history 舊 key 不沿用);丙無新證據不重提。原三選項留痕:
1. 「前 3 席必看命中率」的天花板由「必看有幾個能坐固定席」決定(15/69);about_hit 只重排固定席內部,動不到 31 對自由席必看。
   選項:(a) 接受——固定席=機械保證面,必看召回歸排序,把指標讀成「保證面內的排序品質」;(b) 指標改量「輸出前 3 名」不限固定席;(c) 開第四條保送——已在三輪設計審被拒(about 不是入口),重提要新證據。
2. 31 對自由席必看靠詞彙分競爭——E05 那型(改評測腳本→該看檢索計劃)其實 query 詞彙訊號很強,實測也大多有進前 8(考卷 P@8 0.75);問題不是沒推出來,是「保證」與「推出來」是兩回事,講清楚就好。

## 誠實缺口

- **train split 只有 8 題、38 席固定席**,門檻是在這上面挑的,★過擬合風險高★。
  held 照紀律不該反覆看——**落地前只驗一次**。
- **扇出的算法是本次臨時寫的**(正文 inline-code 抓路徑),★與 `impact` 內部判 direct 的
  實作不是同一支★;真要落地必須收斂成單一實作,否則「量的」與「用的」會漂。
  實驗版的固定席噪音只從 15 降到 14(門檻 2),★懷疑就是這個不一致造成★,未查證。
- **P@8 門檻 0.70 是舊尺定的**;本次 goldset 剛換版(加 3 題、補 90 筆標註,rev 已變),
  ★那個門檻在新尺上的意義未重新校準★。
- 本案只處理**固定席**那一側;自由席的樞紐氾濫(H2 原案)仍未做。
- ★(s3f4 blocker)判準文字是我寫的、考卷標註是我裁的★——標的人是 Codex,但兩邊的尺都經過我的手。
  離線驗證節點自己承認了,原版 spec 沒搬進來。**打破循環的唯一方法是上線後用考卷 held 量一次**。
- ★(s3f5)「零誤放 18 條」的 distinct 筆記數遠小於 18★(lumos-cli-lifecycle 四題都出現)——
  不是 18 個獨立樣本。且 goldset 已換版(train 11 題),驗證用的是 8 題舊切分。
- ★(s1f1)本文「38 席/18 噪音」是土法算的,工具口徑是 15 條噪音★——兩者分母不同(土法含 incident 軸)。
  上線後一律用 `retrieval_eval.py` 印的數字,本文數字只當方向參考。
- (s2f5)hook 顯示層(`scripts/hooks/claude/impact-hook.py:358`)只認 basename-match,要加 `about` 的標示,否則新訊號在最常用介面上看不到。

## 審計修正紀錄

### r1(2026-08-23;s1/s2/s3/arch 四席 + Codex 否決席)
22 條 findings,歸併六洞全折:①「同一把尺」宣稱作廢 ②讀側改寫(三軸 + indirect,about 成獨立判定)
③範圍 61→83、巨檔門檻定義、回滾路徑 ④過期守衛併入 Check S 不另立 ⑤寫入走雙評審不單模型抽驗
⑥過期門檻 30→10%、成績單只有一半有閘。駁回半條:s1f5「進熱路徑」(席二實測 0.75s,毫秒級判斷不構成)。
否決席:未找到否決級問題。

### r2(2026-08-23;s1/s2/s3 三席,修訂稿審)
20 條 findings,歸併九洞全折:**A 降級規則傷召回→改「只加分不降級」(設計層改動)**;
B 回滾指令不存在→改新增子命令 `about-code revert`;C stamp 格式三處統一兩段式;
D「讀側不變」r1 自稱已刪卻殘留兩處→改;E 61 篇殘留→83;F 過期判準 `updated` 紀律不足(33% 落後)→改用 git 日期;
G 範本要加欄、反向計數要單一實作;H 棘輪「安全帶」→「後照鏡」;I 單席預標沿用當 A 席。
★r1 教訓:只改被點名的段落、沒全文 grep 分身——r2 三席有兩席抓的就是這個。★

### r3(2026-08-23;s1/s2/s3 三席)——★達上限未收斂,攤給人裁★
23 條 findings,**7 條 blocker**,★未折入★(到頂規矩:不由編排者裁)。歸併後三個層級:

**① 設計層(s2f1 blocker、s2f2/s2f3/s2f4 major)——r2 的「只加分不降級」救了召回,但把案子的目標救沒了**:
現在沒有任何機制在剔除噪音(扇出層明寫不動產線、巨檔門檻只關 about 加分、22 個誤放本來就是三軸保送進來的);
about_code 對 P@8 零影響(P@8 不計固定席);「主案」「成績單看噪音數」「巨檔門檻恢復鑑別力」三句全是降級時代的殘留。
**席二原話:誰剔噪音?spec 沒人誠實說「現在沒人剔,只是排後面」。**

**② 工具層(s1f1/s1f3/s3f10/s3f11/s3f13/s3f14 blocker+major)——字面開工會崩的五處**:
純量 stamp 沒有刪除原語(cmd_set 只能覆寫);`about_code: []` 會被 fm_structure 判成 scalar → append 必敗
(★既有 aliases: [] 同款 bug★);git log 逐篇 100ms×83=5.3s vs 批次 0.22s(且中文檔名要 -c core.quotepath=false);
Check S 只掃 type:system,事故類節點(spec 自己的核心例子)過期永遠驗不到;refresh_labels merge 吃 {cid:{node:int}},
預標是 {node:[files]},字面呼叫丟 AttributeError。

**③ 流程層(s3f12 blocker、s1f7 major)——沒有「合約候選」節、沒有「本案新增工具清單」彙整**。

★三席共 26 條 blocker/major 在 r3 仍出,而且 ① 是設計層問題:r2 為救召回做的改動,讓 about_code 失去了
「降噪」這個本案立案目標。**這不是再折一輪能收的,要人裁方向。**★

### impl-r1(2026-08-23;light 單席 s1,審剩四項規格)——★light 誤判,升 standard★
10 條全折、無一放行:f1 tier 自判矛盾 → 升 `about-code-impl-std`;f2 `hit="about"` 覆寫既有來源標記 → 另開 `about_hit` 欄;
f3 讀側「不論哪條路徑」促升措辭 → 改窄範圍(about 不是第四條入口);f4 四個行號整批過期 → 校正;
f5 無總開關 → `LUMOS_IMPACT_ABOUT` knob;f6 沒包 `as_list` → 補;f7 巨檔計數無快取 → 掛;
f8 #6 訊息格式與「改過 N 次」皆無據 → 對齊 Check S 實際格式、拿掉次數;f9 doctor 無 repo_root → 迴圈內自找 .git 不改簽名;
f10 新指標分母 0 → 回 None。#9/#10 主體已讀無 finding。
★教訓:「只加一道排序」這種自我描述,要拿「它動到哪個欄位、哪個區塊」去驗,不是看 diff 行數。★

### std-r1(2026-08-23;about-code-impl-std,s1/s2/s3 三席 + arch + 外家 Codex;Gemini 版作廢)
s1 10 條(1 blocker)/ s2 10 條(1 blocker)/ s3 8 條 / arch 2 major+1 ⚠ / Codex 3 major。去重後折入:
**A 日期粒度偽陰性**(s1f1 blocker + ext-e2 + 三席成本條):未 commit 與同日再 commit 都判不出→ helper 擴充同日計數+dirty set,git 缺席視同無欄,懶觸發、incidents-only 跳過;
**B `about_hit: False` 破逐 byte**(s2f2 blocker)→ 只在 True 出鍵;**C 測試①被讀成促升**(ext-e1)→ 明寫 fixture 原本就 pinned、加 free 仍 free 測試;
**D 事故被 about 壓過**(s1f10)→ 排序鍵事故優先;**E 印一行 vs 逐 byte**(ext-e3)→ stderr/stdout 分開定義;
**F doctor 重找 repo_root 第四種寫法**(arch major + s1f3/s2f3/s3f5 的 `:14024` 錯引)→ 複用 Check C 既有變數;
**G 快取鍵 `id(env)`**(arch major + s3f4/s1f6/s2f8)→ `str(env.vault)`;計數切頂層函式(arch ⚠);
**H 新指標沒接到 history**(s3f3)→ 明寫 row→macro→verdict→history;**I revert 部分失敗照刪 stamp**(s3f8,★code★)→ 已修+翻紅釘;
**J 引用精度**(s1f2 併入 Check S 標題句、`:868`→`:844`、「兩處」→一處、`@%cs`、`build_additional_context`、讀側三條路徑行號、`cmd_impact_diff` 範圍外、純量字串測試)→ 全改。
放行:無。不採信:s1f9(引句錨不到,但函式名我自己查了順手改)。Gemini 五條作廢不計(看不到 vault;Enzo 裁外家一律 Codex)。

### std-r2(2026-08-23;s1/s2/s3 + arch + Codex)
s1 7(2 blocker)/ s2 7(1 blocker)/ s3 5(1 blocker)/ arch 1 major+1 ⚠ / Codex 3(1 blocker)。去重後:
**A 同日 ≥2 規則解除不了**(Codex f1 blocker + s1f2 實證 83 篇已誤判 2 篇)→ ★整個過期方案換成正文雜湊★,git 退場;
連帶消滅 **B** quotepath(s1f3/s2f1/arch 三席 blocker/major)、**C** rename 格式(s2f2)、**D** 同日訊息 `<` 自相矛盾(s2f3)、**E** stamp 日期抽法(s2f4)、
**F** 快取歸屬/既有測試(arch ⚠ + s3f3)、**G** 成本重量(s1f7)。
**H `r["about_hit"]` KeyError**(s1f1 blocker)→ 明寫 `.get`;**I summary KEY 行還寫「併入 Check S」**(s3f2 blocker)→ 改;
**J 總開關不管 doctor**(s1f6)→ 管;**K #10 先例錯**(s1f5)→ `fusion_p`;**L 行號整批漂**(四席)→ 改函式名錨+行號政策;
**M ⑫ monkeypatch 不可行**(s2f5)→ 改 CLI 可斷言;**N ⑧「改動前」**(s2f6)→ 定義;**O 工具清單 #5 ✅ 範圍**(s3f4)→ 明寫;**P hit 欄升合約候選**(s3f5)。
放行:無。不採信:s1f2 引句錨不到(同題 Codex f1 採信)。
★教訓:r2 把 r1 的雜湊改成日期是為了「跟 Check S 同形」——一致性壓過了正確性;std-r1 在日期上打補丁(計數+dirty)又生出五個下游洞。
錯的尺上修再多也是錯的,該換尺時換尺。★

### std-r3(2026-08-24 凌晨;s1/s2/s3 + arch + Codex)——★達上限(3 輪)未收斂,攤給人裁★
s1 5(2 blocker)/ s2 7(0 blocker,3 major)/ s3 7(1 blocker)/ arch 3(1 major)/ Codex 3(2 blocker)。去重後全折:
**A restamp 是橡皮章**(Codex f1)+ **B restamp 跟 revert 打架**(s1f2)→ 語意釘死:restamp=人核過、三段全換、無批次模式、doctor 先叫人看標籤;
**C 83 篇遷移也是橡皮章**(Codex f2)→ 用標註當時 commit 的正文算雜湊(git show 一次性),改過的自然變「過期」進人核清單;
**D 回滾路徑節範例兩段式**(s3f3 blocker)→ 改;**E summary 第 3 行 KEY 還寫 git 日期**(s1f1 blocker;上輪只改了第 4 行)→ 標;
**F utf-8-sig**(arch major + s1f3)→ 明寫;**G 工具清單 #4「懶觸發 git」殘句**(Codex f3)→ 改;
**H r1/r2 日期制舊句未標取代**(s3f1)→ 標;**I restamp 接線兩處+守衛哪道會擋**(s2f4/s3f4)→ 寫;
**J impact 不吃 --vault 的測試陷阱、巨檔 fixture 獨立、第三段格式驗證、as_list 計數路徑**(s2)→ 寫;
**K 合約候選編號、三段式 fixture、docstring 過時、head/advice、跳過作廢節點**(minor 五條)→ 改。
不採信:arch 第 3 條引句錨不到(內容我自己查了照改);駁回:s3f2「r1 沒有雜湊」——r1 欄位設計節原文就是三段含 sha(r2 折入腳本留有原句),但「繞回」措辭有歧義,改清楚。
★三輪走勢★:r1 抓設計層(排序/欄位/開關)、r2 抓尺選錯(日期→雜湊)、r3 抓的全是新方案的語意與接線(橡皮章、遷移證據、編碼、範例)——
沒有一條再動方向。**攤給人的問題只有一個:折完的這版,要再開一輪(新編號)審 delta,還是直接進實作、剩下的交給測試與代碼審?**

### ★人裁(2026-08-23 Enzo):甲——收窄目標★
三選一(甲收窄/乙恢復降級加豁免/丙擱置)裁甲。處置:
- 定位改寫(開頭段、三條線表、巨檔門檻語意、成績單)——about_code 只做排序+欄位基礎,不碰噪音
- r3 工具層五處+流程層兩處 → 彙整成「本案新增工具清單」10 項,每項標 r3 抓到的坑
- 補「合約候選」節 4 條
- ★r3 23 條 findings 的去向★:設計層 4 條(s2f1-s2f4)由收窄裁定吸收;工具層與流程層 19 條全部進工具清單;
  s2f5 席二自行修正(自由席配額與固定席無關),採納。
**收窄後本案不再進 design-loop**(目標已變,原三輪審的是降噪方案);進實作前走 light 一輪審工具清單即可。

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'rg -n "''^def (_impact_reverse_lookup|_impact_mark_about|_nodehome_homes|_nodehome_key|cmd_impact|cmd_dispatch_lens|cmd_lint|cmd_new)|LUMOS_IMPACT_ABOUT_MAX|LUMOS_IMPACT_ABOUT|about_hit|about_code_stamp|about_code|incidents_only|ranked" scripts/lumos scripts/hooks/claude/impact-hook.py scripts/hooks/claude/dispatch-lens-hook.py governance/eval/retrieval_eval.py'[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
scripts/hooks/claude/impact-hook.py:527:    "about_code": "這篇筆記自己宣告在講這個檔",
scripts/hooks/claude/impact-hook.py:630:def build_ranked_context(data: dict) -> str:
scripts/hooks/claude/impact-hook.py:631:    """v1.1:把 ranked 輸出({results,meta})轉成降噪清單文字。固定席在前(合約/事故),
scripts/hooks/claude/impact-hook.py:646:            # about_code 語意欄位命中(工具清單 #9):讀 about_hit(只在 True 時存在),不碰既有 hit 來源標記
scripts/hooks/claude/impact-hook.py:647:            ab = "★關於★" if x.get("about_hit") else ""
scripts/hooks/claude/impact-hook.py:695:def inject_ranked_context(data: dict) -> bool:
scripts/hooks/claude/impact-hook.py:696:    """ranked 版注入:results/stack_questions/lane 皆空 → 不輸出(lane-only 的題也要注入,v4 Codex f2)。"""
scripts/hooks/claude/impact-hook.py:701:        "additionalContext": build_ranked_context(data),
scripts/hooks/claude/impact-hook.py:823:    # 窗外 → ranked 降噪版(固定席+top-8,delta 當查詢詞);
scripts/hooks/claude/impact-hook.py:829:           "--ranked", "--stdin-payload", "--json"]
scripts/hooks/claude/impact-hook.py:861:    # rc == 0: ranked schema {file, results, meta}
scripts/hooks/claude/impact-hook.py:870:    # 判空與 inject_ranked_context 同一條:results/stack_questions/lane 皆空 → 不注入(lane-only 也注入)
scripts/hooks/claude/impact-hook.py:872:    ctx = build_ranked_context(impact_data) if has else ""
governance/eval/retrieval_eval.py:35:def ndcg_at_k(ranked_labels, k, all_rels=None):
governance/eval/retrieval_eval.py:39:    ideal = sorted(all_rels if all_rels is not None else ranked_labels, reverse=True)
governance/eval/retrieval_eval.py:41:    return dcg(ranked_labels[:k]) / idcg if idcg > 0 else 0.0
governance/eval/retrieval_eval.py:44:def mrr(ranked_labels):
governance/eval/retrieval_eval.py:45:    for i, r in enumerate(ranked_labels):
governance/eval/retrieval_eval.py:51:def precision_at_k(ranked_labels, k):
governance/eval/retrieval_eval.py:52:    top = ranked_labels[:k]
governance/eval/retrieval_eval.py:88:def recall_at_k(ranked_labels, n_relevant, k):
governance/eval/retrieval_eval.py:91:    return sum(1 for r in ranked_labels[:k] if r >= 1) / n_relevant
governance/eval/retrieval_eval.py:119:    ranked = [x["node"] for x in
governance/eval/retrieval_eval.py:120:              _lum("search", q, "--no-any", "--ranked", "--top", "10", "--json").get("results", [])]
governance/eval/retrieval_eval.py:121:    return legacy, ranked
governance/eval/retrieval_eval.py:135:                        "--ranked", "--top", os.environ.get("LUMOS_EVAL_IMPACT_TOP", "50"),
governance/eval/retrieval_eval.py:154:def _touched_search(legacy, ranked):
governance/eval/retrieval_eval.py:157:    for n in legacy[:SEARCH_TOUCH] + ranked[:SEARCH_TOUCH]:
governance/eval/retrieval_eval.py:239:        legacy, ranked = _search_arms(case["query"])
governance/eval/retrieval_eval.py:240:        _unj(case["id"], _touched_search(legacy, ranked))
governance/eval/retrieval_eval.py:287:    歸因:數字動了要分是 about 還是排序,拿 LUMOS_IMPACT_ABOUT=0 離線對照。"""
governance/eval/retrieval_eval.py:338:    """search 面:legacy 現行順序 vs ranked BM25F。主指標 nDCG@5;輔 MRR/Recall@10。"""
governance/eval/retrieval_eval.py:349:        # 不再等於舊行為。本 gate 是「legacy vs ranked」的受控比較,吃到回退擴召回會讓
governance/eval/retrieval_eval.py:353:        legacy, ranked = _search_arms(q)
governance/eval/retrieval_eval.py:356:        for name, order in (("legacy", legacy), ("ranked", ranked)):
governance/eval/retrieval_eval.py:422:    """edit/hook 面:impact --ranked。P@top_k/nDCG@top_k(非固定席);
governance/eval/retrieval_eval.py:498:        ln, rn = _macro(srows, "legacy_ndcg"), _macro(srows, "ranked_ndcg")
governance/eval/retrieval_eval.py:499:        lm, rm = _macro(srows, "legacy_mrr"), _macro(srows, "ranked_mrr")
governance/eval/retrieval_eval.py:500:        lr, rr = _macro(srows, "legacy_r10"), _macro(srows, "ranked_r10")
governance/eval/retrieval_eval.py:509:        c_ln, c_rn = _macro(srows, "c_legacy_ndcg"), _macro(srows, "c_ranked_ndcg")
governance/eval/retrieval_eval.py:510:        c_valid = sum(1 for r in srows if r.get("c_ranked_ndcg") is not None)
governance/eval/retrieval_eval.py:511:        s_cov = _macro(srows, "ranked_cov")
governance/eval/retrieval_eval.py:518:            "mrr10": _macro(srows, "c_ranked_mrr"), "r10": _macro(srows, "c_ranked_r10"),
governance/eval/retrieval_eval.py:542:        print(f"  輸出前 3 名是必看的比率:{pt3}    ← 人打開 hook 先看到的三行準不準;只看不閘(歸因用 LUMOS_IMPACT_ABOUT=0 對照)")
governance/eval/retrieval_eval.py:650:    pairs = [("search ranked nDCG", v.get("_rn_raw"), cs.get("ndcg")),
scripts/lumos:198:    工具自裝檔判別、about_code 的比對、排序加分讀 about_code 共用這一個(2026-09-10 代碼審 r3 架構席/整合席:
scripts/lumos:1406:    # Check S2: about_code 過期(軟,不擋,不計 issues)——工具清單 #6(Projects/固定席扇出降權_計劃,2026-08-24):
scripts/lumos:1407:    #   有 about_code_stamp 的節點(全 type,不只 system——事故類也標),比「現在正文雜湊」vs stamp 第三段;
scripts/lumos:1410:    #   受總開關 LUMOS_IMPACT_ABOUT(0=整段略過,s1f6:只關一半等於沒關)。訊息先叫人看標籤對不對,restamp 不是萬靈丹(Codex r3 f1)。
scripts/lumos:1411:    section("S2", "語意「關於」標籤(about_code)標了之後正文有沒有又改過(提醒,不擋)")
scripts/lumos:1412:    if int(_impact_knob("LUMOS_IMPACT_ABOUT", 1)) == 0:
scripts/lumos:1413:        ok("(about 總開關 LUMOS_IMPACT_ABOUT=0,過期檢查略過)")
scripts/lumos:1417:            stamp = n.fields.get("about_code_stamp")
scripts/lumos:1422:            expired, nh, sh = about_code_expired(env.vault, rel, stamp)
scripts/lumos:1424:                ac_oldfmt.append(f"{rel} (about_code_stamp {stamp} 沒有正文雜湊段,舊格式)")
scripts/lumos:1427:                ac_stale.append(f"{rel} (about_code_stamp 正文雜湊 {sh} → 現在 {nh if nh is not None else '讀不到正文'})")
scripts/lumos:1430:            ok("每篇有 about_code 標籤的筆記,標了之後正文都沒再改")
scripts/lumos:1433:                       f"有 {len(ac_stale)} 篇筆記的 about_code 標了之後正文又改過,標籤可能過期:",
scripts/lumos:1434:                       "先看這篇的 about_code 對現在的正文還對不對:對 → `lumos about-code restamp <節點>`;不對 → set/append/remove 修完再 restamp")
scripts/lumos:1437:                       f"有 {len(ac_oldfmt)} 篇的 about_code_stamp 是舊格式(沒有正文雜湊),量不出有沒有過期:",
scripts/lumos:1459:    section("S4", "標了 about_code 的合約節點,波及計算連得到嗎(提醒,不擋)")
scripts/lumos:1462:    # 理由:about_code 只做固定席排序不做連結(2026-08-23 甲案收窄,設計正確);
scripts/lumos:1466:        acs = as_list(n.fields.get("about_code"))
scripts/lumos:1477:            _unlinked.append(f"{rel} (about_code: {', '.join(acs[:2])})")
scripts/lumos:1480:        ok("有合約又標了 about_code 的節點,波及計算都連得到")
scripts/lumos:1483:                   f"有 {len(_unlinked)} 篇標了 about_code 的合約節點,波及計算連不到:",
scripts/lumos:1484:                   "在正文裡用反引號寫出那個路徑(例:實作在 `app/pay.py`)——about_code 欄位只做排序不建連結,波及計算認的是正文裡的路徑;連不到的話這篇合約綁的測試在推送時會被靜默跳過")
scripts/lumos:2118:            ok("每支需要家的程式檔都有家(about_code 列了它)")
scripts/lumos:2122:                      "替它們安家:lumos new system <名> --code <檔> --responsibility \"<負責什麼>\",或 lumos append <確實在講它的節點> about_code <檔>")
scripts/lumos:2970:               ranked=False, top=20, as_json=False, include_superseded=False,
scripts/lumos:2976:    2026-07-11 起 ranked(BM25F 相關性排序)為 CLI 預設(goldset 評測 §6 search 面全過,
scripts/lumos:3149:    if ranked and regex:
scripts/lumos:3151:        ranked = False
scripts/lumos:3152:    _cand_hits = {}     # ranked:rel -> hit 行數(候選=legacy 命中集,不擴召回)
scripts/lumos:3153:    _cand_detail = {}   # ranked:rel -> (hits, fm_end) 供逐檔明細輸出
scripts/lumos:3187:        # 在此計數→hidden_superseded=命中被藏筆數(非全庫 superseded 數);三路(ranked/legacy/regex)一致。
scripts/lumos:3195:        if ranked:
scripts/lumos:3214:    if ranked:
scripts/lumos:4156:    "about_code", "about_code_stamp", "self_audit", "feature", "commit",
scripts/lumos:4233:def cmd_lint(env, node):
scripts/lumos:5037:         # 每支檔有家(2026-09-11 [S27]):擋下事件的(檔,節點)配對——回頭條件要拿它列出「被逼出來的 about_code」
scripts/lumos:10653:SCALAR_KEYS = {"status", "updated", "created", "type", "self_audit", "signed_off", "regen", "pitfall_ask", "pitfall_source", "about_code_stamp", "responsibility"}  # pitfall_* 2026-08-09 已知坑策展庫;about_code_stamp 2026-08-23(語意欄位基礎,計劃:固定席扇出降權)
scripts/lumos:10654:LIST_KEYS = {"verified_by", "plan_refs", "related", "tags", "aliases", "pitfall_when", "core_refs", "about_code", "lands_in"}   # aliases 2026-08-05;pitfall_when 2026-08-09(已知坑策展庫,content-trigger);core_refs 2026-08-11(升格加指針/降格拆指針,兩向都要 T1;值是純路徑非 wikilink——lumos-core-knowledge skill 明令禁跨 vault wikilink)
scripts/lumos:10782:    """清單欄位被寫成單一值(`about_code: src/x.py`)時,改寫成一項的清單再給 append/remove 用。
scripts/lumos:11106:def _about_code_key(root, value):
scripts/lumos:11107:    """about_code 一項「指的是哪一支檔」的比對鍵(append 去重、remove 找項共用)。
scripts/lumos:11125:def _about_code_path(env, value):
scripts/lumos:11126:    """about_code 的一項要是「這個 repo 裡真的存在的程式檔」(2026-09-10 代碼審 r1)。
scripts/lumos:11133:        return None, "about_code 不能是空的"
scripts/lumos:11135:        return None, f"about_code 要寫 repo 相對路徑,「{v}」是絕對路徑"
scripts/lumos:11143:        return None, (f"「{v}」不是這個 repo 裡的檔案" + ("(它是目錄;about_code 要寫到檔案)" if target.is_dir() else "(找不到)"))
scripts/lumos:11166:    if key == "about_code":
scripts/lumos:11167:        value, why = _about_code_path(env, value)
scripts/lumos:11169:            print(f"擋下:{why},檔案沒動。about_code 要填這個 repo 裡真的存在的程式檔(repo 相對路徑)", file=sys.stderr)
scripts/lumos:11173:    if key == "about_code":
scripts/lumos:11175:        want = _about_code_key(root, value)
scripts/lumos:11176:        same = [x for x in as_list(parse_frontmatter(lines[1:e])[0].get(key)) if _about_code_key(root, x) == want]
scripts/lumos:11222:    if key == "about_code":
scripts/lumos:11223:        # 同一支檔的每一種寫法都拿掉(舊資料可能同一支檔寫了兩種);比對鍵見 _about_code_key
scripts/lumos:11225:        want = _about_code_key(root, value)
scripts/lumos:11227:                                       if _about_code_key(root, x) == want))
scripts/lumos:11232:        gone = lambda f: not any(_about_code_key(root, x) == want for x in as_list(f.get(key)))
scripts/lumos:11240:        if key == "about_code":   # 目錄讀不到時比對鍵只能退回字面,大小寫與別名對不上——講明(第四輪整合席)
scripts/lumos:11290:def about_code_to_rater(a, b):
scripts/lumos:11291:    """★about_code 預標 → refresh_labels merge 的格式★(工具清單 #8,2026-08-23)。
scripts/lumos:11314:    """★正文雜湊:about_code 過期守衛的尺★(about-code-impl-std r2/r3,2026-08-24)。
scripts/lumos:11337:    """about_code_stamp 三段 `<誰>/<日期>/<正文雜湊12碼>`;第三段非 12 碼 hex 視同沒有(舊格式)。"""
scripts/lumos:11349:def about_code_expired(vault, rel, stamp):
scripts/lumos:11356:def cmd_about_code_restamp(env, rel, by="claude"):
scripts/lumos:11357:    """★restamp = 「我剛核過這篇的 about_code 對現在的正文仍然正確」★(工具清單 #11,std-r3 釘語意)。
scripts/lumos:11362:    沒有 about_code 的節點擋下:沒東西可核。
scripts/lumos:11378:    if not as_list(n.fields.get("about_code")):
scripts/lumos:11379:        print(f"擋下:{rel} 沒有 about_code,沒東西可核。先 lumos append <節點> about_code <檔> 再 restamp。", file=sys.stderr)
scripts/lumos:11387:    rc = cmd_set(env, rel, "about_code_stamp", stamp)
scripts/lumos:11389:        print(f"✓ restamp {rel}:about_code_stamp = {stamp}(表示你核過標籤對現在的正文仍正確)")
scripts/lumos:11393:def cmd_about_code_migrate_stamp(env, at_commit, repo_root=None, dry_run=False):
scripts/lumos:11408:        stamp = n.fields.get("about_code_stamp")
scripts/lumos:11430:        if cmd_set(env, rel, "about_code_stamp", new) == 0:
scripts/lumos:11439:def cmd_about_code_revert(env, batch_date, dry_run=False):
scripts/lumos:11440:    """★整批撤銷某天的 about_code 預標★(工具清單 #7,2026-08-23)。
scripts/lumos:11443:    逐值拿掉 about_code、整欄拿掉 stamp。人工修正過的 stamp 第一段會變(`claude/…`),
scripts/lumos:11450:        stamp = n.fields.get("about_code_stamp")
scripts/lumos:11454:            targets.append((rel, [str(x) for x in as_list(n.fields.get("about_code"))]))
scripts/lumos:11456:        print(f"擋下:沒有任何節點的 about_code_stamp 第一段是 {want},沒東西可撤。"
scripts/lumos:11461:        print(f"  {rel}  about_code {len(vals)} 項")
scripts/lumos:11471:                if cmd_remove(env, rel, "about_code", v) != 0:
scripts/lumos:11481:        if cmd_remove(env, rel, "about_code_stamp", None) == 0:   # 走有上鎖的入口(第四輪併發資源席:原本直接呼叫底層函式、繞過寫入鎖)
scripts/lumos:12309:def cmd_impact_node(node_arg, repo=None, as_json=False):
scripts/lumos:12390:               "about_code: []\n"
scripts/lumos:12396:              "about_code: []\n"
scripts/lumos:12411:        "about_code 寫「這篇管哪幾支程式檔」(repo 相對路徑,0~3 支;建檔時可直接帶 --code <檔>)——判準:改那支檔的人不看這篇會不會做錯事?會就列;只是順帶提到的不列。純方法論筆記留 []。改這些檔時它會排固定席前排",
scripts/lumos:12412:        "★每支檔有家★(提交前擋新違規):每支程式檔要有一篇管它的節點;這篇只准用反引號寫自己 about_code 裡的檔,別人的檔寫成那支檔的家的 [[連結]];新開的 Systems 節點要寫一句負責範圍(lumos set <節點> responsibility \"<負責什麼、不負責什麼>\",或建檔時帶 --responsibility);管超過 3 支檔的舊篇也要寫",
scripts/lumos:12417:        "about_code 寫「這次事故發生在哪幾支程式檔」(repo 相對路徑)——★事故類優先填★:改那支檔的人不看這篇會再犯。只寫出事的那幾支,不用列所有相關的",
scripts/lumos:12429:def cmd_new(env, ntype, name, today, plan=None, systems=None, code=None, responsibility=None):
scripts/lumos:12458:        relp, err = _about_code_path(env, c)
scripts/lumos:12500:            _rc, _why = cmd_append(env, self_rel, "about_code", relp), "(上面有原因)"
scripts/lumos:12504:            print(f"提醒:筆記建好了,但 --code {relp} 沒寫進 about_code{_why},照原因補:\n    lumos append <節點> about_code {relp}", file=sys.stderr)
scripts/lumos:14248:    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
scripts/lumos:14256:    if not ranked:
scripts/lumos:14258:    elif len(ranked) == 1 or ranked[0][1] > sum(c for _, c in ranked[1:]) * 3:
scripts/lumos:14259:        ext = ranked[0][0]
scripts/lumos:14276:        for ext, n in ranked[:3]:
scripts/lumos:14288:                    "symbol_profile": guess[ranked[0][0]]["symbol"]}
scripts/lumos:16967:def cmd_lint_check(repo=None, smoke=False, as_json=False):
scripts/lumos:17923:            "about": [str(x) for x in as_list(fields.get("about_code")) if str(x).strip()],
scripts/lumos:17988:def _nodehome_key(value):
scripts/lumos:17989:    """about_code 一項的比對鍵(字面):路徑正規化+NFC。★不讀磁碟★——比對的是被檢查那個版本裡的樣子,
scripts/lumos:17991:    about_code 寫入時已經照磁碟校正過(解連結、大小寫、Unicode 寫法;_about_code_path),所以字面比就夠。"""
scripts/lumos:17995:def _nodehome_homes(repo_root, side):
scripts/lumos:17996:    """[S2] {檔: [家那幾篇]}。只看 about_code 欄位值、不看預標指紋有沒有過期(指紋在每次寫回都會過期)。
scripts/lumos:18309:        many = int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8))
scripts/lumos:18348:        L.append("每支程式檔要有一篇管它的節點(about_code 列了它);沒有家的檔,改它時工具推不出該看的筆記,寫回也不知道該落哪——兩個專案就是這樣長出一篇包全部的節點。")
scripts/lumos:18368:            L.append(f"      lumos append <節點> about_code {take[0]}")
scripts/lumos:18374:        L.append(f"■ 這幾支程式檔原本有家,這次變沒家了({len(hr)} 支)——從 about_code 拿掉、家那篇被刪,或狀態改成 planned/deferred/rejected/superseded:")
scripts/lumos:18380:        L.append("    lumos append <新家> about_code <檔>")
scripts/lumos:18389:        L.append("    lumos append <節點> about_code <檔>")
scripts/lumos:20920:    ★2026-08-24:about_code 過期判準已改記正文雜湊(note_body_hash),本函式不再是它的材料、目前無呼叫者★
scripts/lumos:20958:def _impact_reverse_lookup(rel_code_path, env, repo_root):
scripts/lumos:21250:_ABOUT_COUNTS_CACHE = {}   # str(vault) → {repo 相對路徑: 幾篇 about_code 命中它}(行程內;--diff 多檔共用 env 免重掃)
scripts/lumos:21254:    """★巨檔門檻的材料:全掃 env.notes 的 about_code 建 {檔: 節點數}★(工具清單 #4;獨立頂層函式對齊 _impact_* 分工)。
scripts/lumos:21261:        for f in as_list(n.fields.get("about_code")):
scripts/lumos:21269:def _impact_mark_about(env, results, rel_file):
scripts/lumos:21270:    """★about_code 只加分不降級★:對已進候選集的 results 項,about_code 含目標檔且 stamp 未過期 → 加 `about_hit: True`
scripts/lumos:21272:    總開關 LUMOS_IMPACT_ABOUT(預設 1;0=整段不跑、不讀正文);巨檔門檻 LUMOS_IMPACT_ABOUT_MAX(預設 8):
scripts/lumos:21275:    if int(_impact_knob("LUMOS_IMPACT_ABOUT", 1)) == 0:
scripts/lumos:21280:    if counts.get(target, 0) >= int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8)):
scripts/lumos:21286:        vals = [_norm(x) for x in as_list(n.fields.get("about_code"))]
scripts/lumos:21289:        expired, _nh, _sh = about_code_expired(env.vault, r["node"], n.fields.get("about_code_stamp"))
scripts/lumos:21292:        r["about_hit"] = True
scripts/lumos:21394:def cmd_impact(file, repo=None, depth=None, as_json=False,
scripts/lumos:21395:               ranked=False, top=8, min_score=0.20, stdin_payload=False, incidents_only=False,
scripts/lumos:21440:    # incidents_only 真快速路(r1 終審親驗修正:原實作僅「不顯示」,反查/BFS 照跑——宣稱落空):
scripts/lumos:21442:    if incidents_only:
scripts/lumos:21468:    # (incidents_only 時 direct_rels 為空,以下兩段自然零工作——BFS multi-source 種子空集即不擴散)
scripts/lumos:21584:    # 8.5 ranked 融合(階段三,spec §3):固定席(事故+含合約 direct+深度內合約 indirect)不占 top_k;
scripts/lumos:21586:    if ranked or incidents_only:
scripts/lumos:21596:        if not incidents_only:
scripts/lumos:21655:        # about_code 語意欄位(工具清單 #4):只標記、不動 pinned;--incidents-only 快速路徑整段跳過
scripts/lumos:21656:        if not incidents_only:
scripts/lumos:21661:        pins.sort(key=lambda r: (r["kind"] != "incident", not r.get("about_hit", False)))
scripts/lumos:21723:            # 棧別效能追問(pitfalls棧別效能追問_計劃 T2):完整 ranked 模式(非 incidents-only
scripts/lumos:21725:            if not incidents_only and not _PITFALL_DIFF_TEST_PAT.search(rel_file):
scripts/lumos:21850:def cmd_impact_diff(diff_range, repo=None, depth=None, top=8, min_score=0.20, as_json=False,
scripts/lumos:21852:    """code-loop 橋接:對整段 diff 的每支改動 code 檔跑 ranked impact(query=該檔 hunk 文字),
scripts/lumos:21919:                            ranked=True, top=top, min_score=min_score,
scripts/lumos:22516:def cmd_dispatch_lens_arm(diff_range, repo=None, seats=1, no_cache=False):
scripts/lumos:22576:def cmd_dispatch_lens_claim(repo=None, as_json=False):
scripts/lumos:22631:def cmd_dispatch_lens_disarm(repo=None):
scripts/lumos:22654:def cmd_dispatch_lens_status(repo=None):
scripts/lumos:22830:def cmd_dispatch_lens(diff_range, repo=None, as_json=False, no_cache=False, cap=8, max_lines=400, deadline=None):
scripts/lumos:23053:def cmd_dispatch_lens_spec(spec_path, repo=None, as_json=False, cap=8, max_lines=400):
scripts/lumos:25327:    "about-code": "語意「關於」欄位 about_code 的操作:revert 整批撤、restamp 核過後重標、migrate-stamp 一次性補雜湊。",
scripts/lumos:25329:    "about-code restamp": "doctor 說某篇 about_code 可能過期、你看過標籤對現在的正文仍然對 → 用這個重標(三段全換);標籤不對就先 set/append/remove 修完再 restamp。",
scripts/lumos:25530:    ac = sub.add_parser("about-code", help="語意「關於」欄位 about_code 的批次操作(計劃:固定席扇出降權)")
scripts/lumos:25532:    acr = acsub.add_parser("revert", help="整批撤銷某天的預標:stamp 第一段 == batch-<日期> 的節點,拿掉 about_code 與 stamp;人工修正過的(claude/…)不動")
scripts/lumos:25535:    acs = acsub.add_parser("restamp", help="核過這篇 about_code 對現在正文仍正確 → stamp 三段全換 <by>/<今天>/<正文雜湊>;沒有批次模式")
scripts/lumos:25752:    p.add_argument("--ranked", action="store_true", help="BM25F 相關性排序(2026-07-11 起已是預設,旗標保留相容)")
scripts/lumos:25840:                   help="system/issue:這篇管哪幾支程式檔(repo 相對路徑,可重複;寫進 about_code)")
scripts/lumos:25956:    p.add_argument("--diff", dest="impact_diff", help="diff range(如 main..HEAD):聚合各改動檔的 ranked impact 成受影響功能面 manifest(code-loop 審計鏡頭)")
scripts/lumos:25966:    p.add_argument("--ranked", action="store_true", dest="impact_ranked", help="融合排序+固定席+降噪(dormant v1)")
scripts/lumos:25967:    p.add_argument("--top", type=int, dest="impact_top", default=8, help="--ranked 非固定項上限")
scripts/lumos:25968:    p.add_argument("--min-score", type=float, dest="impact_min", default=0.20, help="--ranked 分數底線")
scripts/lumos:26239:                          ranked=args.impact_ranked, top=args.impact_top,
scripts/lumos:26241:                          incidents_only=args.impact_inc_only)
scripts/lumos:26351:        _use_ranked = not args.search_legacy and not args.regex
scripts/lumos:26352:        if args.ranked and args.regex:
scripts/lumos:26356:                          include_code=args.code, ranked=_use_ranked, top=args.top,
scripts/lumos:26387:            return cmd_about_code_revert(env, args.batch, dry_run=args.dry_run)
scripts/lumos:26389:            return cmd_about_code_restamp(env, args.node, by=args.by)
scripts/lumos:26391:            return cmd_about_code_migrate_stamp(env, args.at, repo_root=args.acm_repo, dry_run=args.dry_run)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "sed -n '20920,21315p' scripts/lumos"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
    ★2026-08-24:about_code 過期判準已改記正文雜湊(note_body_hash),本函式不再是它的材料、目前無呼叫者★
    (三輪設計審實證日期表達不了「標記在同日序列的哪一格」);保留供日後批次日期需求。

    為什麼要批次:design-loop about-code-field r3 實測逐篇 `git log -1 -- <檔>` 83 次 5.3s,
    批次 0.22s,差 18 倍;impact 跑在 PreToolUse hook,逐篇會把它拖進秒級。
    為什麼要 `-c core.quotepath=false`:vault 檔名幾乎全中文,預設輸出是八進位跳脫
    (`\347\257\204…`),對不回路徑——★沒這旗標整張表是空的,而且不報錯★。
    用 `updated` 欄的問題:席三抽 15 篇,5 篇(33%)落後 git 實際改動日期——正文改了沒 lumos set。
    """
    import subprocess
    key = (str(repo_root), str(vault))
    if key in _GIT_DATES_CACHE:
        return _GIT_DATES_CACHE[key]
    out = {}
    try:
        rel_vault = os.path.relpath(str(vault), str(repo_root))
        r = subprocess.run(["git", "-C", str(repo_root), "-c", "core.quotepath=false",
                            "log", "--name-only", "--format=@%cs", "--", rel_vault],
                           capture_output=True, text=True, errors="replace", timeout=30)
        if r.returncode == 0:
            cur = None
            prefix = rel_vault.rstrip("/") + "/"
            for line in r.stdout.splitlines():
                if line.startswith("@"):
                    cur = line[1:11]
                elif line.strip() and cur and line.startswith(prefix):
                    rel = line[len(prefix):]
                    if rel not in out:          # log 是新→舊,第一次看到就是最新
                        out[rel] = cur
    except (OSError, subprocess.SubprocessError):
        out = {}
    _GIT_DATES_CACHE[key] = out
    return out


_BASENAME_COUNTS_CACHE = {}   # repo_root → {basename: count}(行程內;--diff 多檔免重跑 ls-files)


def _impact_reverse_lookup(rel_code_path, env, repo_root):
    """給一支 code 路徑,反查「哪些圖譜節點的 body inline-code 引用了它」。

    設計要點(Task 2):
    - 只掃 body inline-code,絕不掃 core_refs(r7-F2)。
    - 複用 _refcheck_scan(text, repo_root) 抽取 body inline-code 路徑;
      Note 不存 body → 重讀盤每個 .md 餵它(r1-F1)。
    - 路徑規範化(r3-F5):輸入若為絕對路徑先轉 repo-relative 再比對。
    - _refcheck_scan 的 top_dirs 靜默過濾照舊(§4 天花板 5)。

    回傳: list[(node_rel, hit)] — hit ∈ "body-inline-code"(完整路徑命中)|
    "basename-match"(裸檔名容錯,R2 2026-08-07,plan:hook必看召回修復)。
    同節點兩路皆中時完整路徑優先(單節點單筆,provenance 合併序明文)。

    R2 裸檔名容錯:inline-code 中不含 `/` 的裸 token == 目標檔 basename,且該
    basename 在 `git ls-files` 母體內唯一(tracked-only:untracked/ignored 混入會把
    唯一誤判歧義;大小寫敏感)→ 命中。★不動共用的 _refcheck_scan★(其 `/` 過濾
    是 refcheck CLI/G1 gate 的既有合約,此處自建第二條抽取路)。git 缺席/重名
    → degrade 為不比對(裸檔名路靜默停用,完整路徑路不受影響)。
    knob:LUMOS_IMPACT_BASENAME_MATCH(2026-08-07 轉正預設 1;0=逃生/A 臂)。ls-files 結果以 repo_root 為鍵行程內快取(--diff 多檔不重跑子行程)。
    """
    import os
    import subprocess

    repo_root = Path(repo_root)

    # 路徑規範化:絕對路徑 → repo-relative
    rp = str(rel_code_path)
    if os.path.isabs(rp):
        rp = os.path.relpath(rp, str(repo_root))

    # R2:裸檔名比對的前置——目標檔 basename 在 tracked 母體唯一才啟用
    base_ok = False
    base = Path(rp).name
    if int(_impact_knob("LUMOS_IMPACT_BASENAME_MATCH", 1)):   # 2026-08-07 考卷轉正預設 1(knob=0 留逃生)
        key = str(repo_root)
        counts = _BASENAME_COUNTS_CACHE.get(key)
        if counts is None:
            counts = {}
            try:
                r = subprocess.run(["git", "-C", str(repo_root), "ls-files"],
                                   capture_output=True, text=True, errors="replace", timeout=10)
                if r.returncode == 0:
                    for ln in r.stdout.splitlines():
                        if ln.strip():
                            b = Path(ln).name
                            counts[b] = counts.get(b, 0) + 1
            except (OSError, subprocess.SubprocessError):
                counts = {}   # git 缺席=degrade(空表=永不唯一)
            _BASENAME_COUNTS_CACHE[key] = counts
        base_ok = counts.get(base, 0) == 1

    hits = []
    for node_rel, note in env.notes.items():
        # 重讀盤:Note 不存 body,直接讀原始 .md 文字
        md_path = env.vault / node_rel
        try:
            text = md_path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        claims, _n_missing, _n_oor, _n_ok = _refcheck_scan(text, repo_root)
        hit = None
        for claim in claims:
            if claim["token"] == rp:
                hit = "body-inline-code"   # 完整路徑優先
                break
        if hit is None and base_ok:
            # 第二條抽取路:裸 token(無 /)——與 _refcheck_scan 同一支抽取(_node_code_ref_tokens)
            if base in _node_code_ref_tokens(text, set())[1]:
                hit = "basename-match"
        if hit:
            hits.append((node_rel, hit))   # 同一節點只算一次
    return hits


def _impact_contract(note):
    """Task 3: 偵測節點的合約標記,回傳 (contract: str|None, combo: bool)。

    兩軸設計(r6-F3):
    - INVARIANT/DEBT 軸: extract_contracts(note) → inv list。DEBT → None(r9-F7)。
    - IRREVERSIBLE 軸: 獨立 IRREVERSIBLE_RE 掃 summary(extract_contracts 不含此)。
    取最高: IRREVERSIBLE > INVARIANT > None。
    combo(r6-F6): ★COMBO★ 是 ★INVARIANT★ 同行後綴修飾,偵測 INVARIANT 行含 ★COMBO★
                 (參 scripts/lumos:725 的 '★COMBO★' not in inv);不入 contract enum,走獨立布林。
    """
    invs, _debts = extract_contracts(note)  # 只掃 INVARIANT/DEBT

    # combo: 任一 INVARIANT 行含 ★COMBO★ 即為 True
    combo = any("★COMBO★" in inv for inv in invs)

    # INVARIANT 軸: 有 inv 則 contract="INVARIANT"(DEBT 已被 extract_contracts 分到 _debts,不入此路)
    contract = "INVARIANT" if invs else None

    # IRREVERSIBLE 軸: 獨立掃 summary(extract_contracts 不含 IRREVERSIBLE)
    summ = note.fields.get("summary")
    if isinstance(summ, str):
        for line in summ.split("\n"):
            if IRREVERSIBLE_RE.match(line.strip()):
                contract = "IRREVERSIBLE"  # 最高優先,覆蓋 INVARIANT
                break

    # RISK 軸(2026-08-05 標籤結構優化):risk/ 標節點保送固定席——light 硬否決的
    # honor-system(「碰金流/對外/不可逆/守衛面就不給 light」靠自核)有了機械眼線。
    # 軸序最低:合約標記存在時仍以合約身分出席。
    if contract is None:
        for tg in (note.fields.get("tags") or []):
            if isinstance(tg, str) and tg.startswith("risk/"):
                contract = "RISK·" + tg.split("/", 1)[1]
                break

    return contract, combo


def _impact_bfs(direct_nodes, env, depth):
    """Task 4: 從直接節點集沿 env.edges 雙向 BFS 展開間接關聯。

    設計要點:
    - hop 語意(r8-F5): hop = 距最近直接節點的 BFS 距離,hop ∈ 1..depth。
    - visited/cycle guard(r8-F4): seen 先種入全部直接節點,直接節點沿環不重入 indirect
      (參 cmd_map 的 seen 模式 scripts/lumos:908-923)。
    - 雙向邊: out_e(outlink)+in_e(backlink) 都走;每筆記 is_backlink。
    - 雙向 direction 衝突(r8-F7): 若 dest 同時可從 out_e 與 in_e 到達 → 標 backlink 優先。
    - 不含直接節點本身。

    回傳: list[(node, hop, from_node, is_backlink)]
    """
    out_e, in_e = env.edges

    # pending 機制正確處理同一 hop 內雙向衝突(backlink 優先,r8-F7)
    seen = set(direct_nodes)
    queue = deque()

    # 每一輪 frontier 的 pending: dest -> (hop, from_node, is_backlink)
    # backlink 優先:若 dest 先被 outlink 加,後被 backlink 命中 → 覆蓋為 backlink
    for direct in direct_nodes:
        pending = {}  # dest -> (from_node, is_backlink)
        for dest in out_e.get(direct, []):
            if dest not in seen:
                if dest not in pending:
                    pending[dest] = (direct, False)
                # outlink 不覆蓋已有的 backlink
        for dest in in_e.get(direct, []):
            if dest not in seen:
                # backlink 優先:無論如何覆蓋
                pending[dest] = (direct, True)
        for dest, (from_node, is_bl) in pending.items():
            if dest not in seen:
                seen.add(dest)
                queue.append((dest, 1, from_node, is_bl))

    result = []

    while queue:
        node, hop, from_node, is_backlink = queue.popleft()
        result.append((node, hop, from_node, is_backlink))

        if hop < depth:
            # 展開下一層,同樣用 pending 處理雙向衝突
            pending = {}
            for dest in out_e.get(node, []):
                if dest not in seen:
                    if dest not in pending:
                        pending[dest] = (node, False)
            for dest in in_e.get(node, []):
                if dest not in seen:
                    pending[dest] = (node, True)
            for dest, (fn, is_bl) in pending.items():
                if dest not in seen:
                    seen.add(dest)
                    queue.append((dest, hop + 1, fn, is_bl))

    return result


def _impact_via(frontier, dest, is_backlink, env):
    """Task 5: 判斷 BFS 一條邊的 via(沿哪個 frontmatter 欄位到達)。

    設計要點(§2.3,r9-F1):
    - env.edges 是 out_e[a].append(b) / in_e[b].append(a) ——
      wikilink **永遠寫在「連出去」那一端**。
    - outlink(is_backlink=False): wikilink 在 frontier → 讀 frontier.fields,
      找含指向 dest 的 wikilink 欄位。
    - backlink(is_backlink=True): wikilink 在 dest(dest 連向 frontier) →
      讀 dest.fields(不是 frontier!),找含指向 frontier 的 wikilink 欄位。
      **讀錯端(frontier)會全 miss → 全 body-wikilink fallback(r9-F1 的 bug)。**
    - 比對:欄位值是 "[[stem]]" 字串,目標是 rel 路徑 →
      用 link_target()+env.resolve() 轉 rel 再比。
    - body-wikilink fallback(r5-F3):n.fields 只有 frontmatter;
      若「wikilink 所在端」任何 frontmatter 欄位都找不到 → via="body-wikilink"。

    via 枚舉: related / verified_by / plan_refs / body-wikilink。
    direction = "backlink" if is_backlink else "outlink"(由呼叫端 is_backlink 決定)。
    """
    # 決定「wikilink 所在端」和「被指向的目標 rel」
    if is_backlink:
        # backlink: dest 連向 frontier → wikilink 在 dest,目標是 frontier
        wikilink_node = dest
        target_rel = frontier
    else:
        # outlink: frontier 連向 dest → wikilink 在 frontier,目標是 dest
        wikilink_node = frontier
        target_rel = dest

    note = env.notes.get(wikilink_node)
    if note is None:
        return "body-wikilink"

    # 掃 frontmatter 欄位(跳過 block scalar;只看 list/str wikilink 欄位)
    for field_key in ("related", "verified_by", "plan_refs"):
        vals = as_list(note.fields.get(field_key))
        for val in vals:
            resolved = env.resolve(link_target(val))
            if resolved == target_rel:
                return field_key

    # 任何 frontmatter 欄位都找不到 → 邊來自 body([[..]])
    return "body-wikilink"


def _impact_collect(direct_node_rel, env, depth=2):
    """Task 6: 組裝單一直接節點的影響清單(直接 + 間接)。

    設計要點:
    - direct_node_rel: vault-relative 路徑(如 "Systems/A.md")。
    - 直接節點: direct_node_rel 本身,補齊 {node, hit, contract, combo}。
    - 間接關聯:
        1. core_refs 跨 repo 葉(r7-F2): 直接節點若有 core_refs,把每條值當
           「不可展開跨 repo 葉」輸出,標 via:"core_refs",cross_repo:True,
           no_expand:True,**不試圖 BFS 進它**。
           讀法: as_list(n.fields.get("core_refs"))(r3-F8:值可能 str/list)。
        2. BFS 間接關聯(via env.edges 雙向)→ 由 _impact_bfs 出結果,
           再用 _impact_via 補 via/direction。
           (BFS 項目的 cross_repo/no_expand 不存在——下游用 .get 取 false。)

    回傳: {"direct": [...], "indirect": [...]}
    格式:
      direct 每筆: {node, hit:"body-inline-code", contract, combo}
      indirect 每筆(core_refs 葉):
        {node, hop:1, via:"core_refs", direction:"outlink",
         from:<直接節點>, cross_repo:True, no_expand:True,
         contract:None, combo:False}
      indirect 每筆(BFS):
        {node, hop, via, direction, from, contract, combo}
    """
    direct_list = []
    indirect_list = []

    # 直接節點資料
    direct_note = env.notes.get(direct_node_rel)
    contract, combo = _impact_contract(direct_note) if direct_note else (None, False)
    direct_list.append({
        "node": direct_node_rel,
        "hit": "body-inline-code",
        "contract": contract,
        "combo": combo,
    })

    # 1. core_refs 跨 repo 葉(r7-F2):不 BFS 進、不查 env.notes[dest]
    if direct_note is not None:
        for core_ref in as_list(direct_note.fields.get("core_refs")):
            indirect_list.append({
                "node": core_ref,
                "hop": 1,
                "via": "core_refs",
                "direction": "outlink",
                "from": direct_node_rel,
                "cross_repo": True,
                "no_expand": True,
                "contract": None,
                "combo": False,
            })

    # 2. BFS 間接關聯(via env.edges)
    bfs_results = _impact_bfs([direct_node_rel], env, depth=depth)
    for (node, hop, from_node, is_backlink) in bfs_results:
        bfs_note = env.notes.get(node)
        bfs_contract, bfs_combo = _impact_contract(bfs_note) if bfs_note else (None, False)
        via = _impact_via(from_node, node, is_backlink, env)
        direction = "backlink" if is_backlink else "outlink"
        indirect_list.append({
            "node": node,
            "hop": hop,
            "via": via,
            "direction": direction,
            "from": from_node,
            "contract": bfs_contract,
            "combo": bfs_combo,
        })

    return {"direct": direct_list, "indirect": indirect_list}


_ABOUT_COUNTS_CACHE = {}   # str(vault) → {repo 相對路徑: 幾篇 about_code 命中它}(行程內;--diff 多檔共用 env 免重掃)


def _impact_about_counts(env):
    """★巨檔門檻的材料:全掃 env.notes 的 about_code 建 {檔: 節點數}★(工具清單 #4;獨立頂層函式對齊 _impact_* 分工)。
    快取鍵用路徑字串(既有 _BASENAME_COUNTS_CACHE/_GIT_DATES_CACHE 同款;id(env) 是全庫沒先例的第二種做法)。"""
    key = str(env.vault)
    if key in _ABOUT_COUNTS_CACHE:
        return _ABOUT_COUNTS_CACHE[key]
    counts = {}
    for n in env.notes.values():
        for f in as_list(n.fields.get("about_code")):
            f = _posix_norm(f)
            if f:
                counts[f] = counts.get(f, 0) + 1
    _ABOUT_COUNTS_CACHE[key] = counts
    return counts


def _impact_mark_about(env, results, rel_file):
    """★about_code 只加分不降級★:對已進候選集的 results 項,about_code 含目標檔且 stamp 未過期 → 加 `about_hit: True`
    (只在 True 時出鍵;★不覆寫既有 hit 欄★;不改任何 pinned 判定——about 不是第四條入口)。
    總開關 LUMOS_IMPACT_ABOUT(預設 1;0=整段不跑、不讀正文);巨檔門檻 LUMOS_IMPACT_ABOUT_MAX(預設 8):
    目標檔被 ≥N 篇 about 命中時關閉加分(巨檔上「關於」無鑑別力,held 實證 22 誤放)。
    懶觸發:先查欄位,命中才讀該篇正文算雜湊(無 git、無子行程)。計劃:Projects/固定席扇出降權_計劃。"""
    if int(_impact_knob("LUMOS_IMPACT_ABOUT", 1)) == 0:
        return
    _norm = _posix_norm   # 跟寫入側同一個路徑正規化(r3 整合席:原本只剝開頭的 ./,不解 ..)
    target = _norm(rel_file)
    counts = _impact_about_counts(env)
    if counts.get(target, 0) >= int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8)):
        return
    for r in results:
        n = env.notes.get(r["node"])
        if n is None:
            continue
        vals = [_norm(x) for x in as_list(n.fields.get("about_code"))]
        if target not in vals:
            continue
        expired, _nh, _sh = about_code_expired(env.vault, r["node"], n.fields.get("about_code_stamp"))
        if expired:
            continue
        r["about_hit"] = True


def _impact_knob(name, default):
    """hook 面調參旋鈕:預設=凍結常數;LUMOS_IMPACT_* env 僅供 goldset 網格消融,非使用者旗標。"""
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default

def _impact_query_junk(query):
    """query 品質閘判準(edit面查詢品質閘_計劃 S1;落地後發現收窄版):
    剝 shebang 首行後,壓縮全部空白的殘餘 < MINLEN → junk(視同空查詢,L 臂靜默)。
    ★MINLEN 預設 1=「僅 shebang/空白」才算垃圾★——原 20 字低資訊假說被 held 反證
    (E15 的 17 字真代碼行有訊息:其 L 分撐高動態門檻殺 hop1 噪音,閘掉反湧回,
    0.67→0.38 倒退;shebang 案 E05/E14 的收益不靠長度分支)。旋鈕留給網格消融。
    非 str 防呆回 False;MINLEN<=0/NaN/Inf=整閘停用(旋鈕語意連續)。"""
    if not isinstance(query, str):
        return False
    minlen = _impact_knob("LUMOS_IMPACT_QGATE_MINLEN", 1)
    if not (minlen > 0) or minlen == float("inf"):   # <=0/NaN(比較恆假)/Inf → 停用
        return False
    q = query.strip()
    if q.startswith("#!"):

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "sed -n '22820,23220p' scripts/lumos"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
        print(_j2.dumps({"timed_out": True, "still_warming": True, "range": diff_range},
                        ensure_ascii=False))
    else:
        print(f"這次沒算完({diff_range}),但沒有白算——有一支在背景把它算完並寫進快取。")
        print("  為什麼在意:下一次同一個範圍就直接拿得到,不必再等。")
        print(f"  想拿結果就再敲一次(算完之前會再回這句):")
        print(f"      lumos dispatch-lens {diff_range}")
    return 5


def cmd_dispatch_lens(diff_range, repo=None, as_json=False, no_cache=False, cap=8, max_lines=400, deadline=None):
    import json as _json
    import io, contextlib, time as _time
    _t0 = _time.monotonic()   # v1.2:hook 內層 45 秒是總帳,備援段預算=45−已耗−保留
    parts = _lens_range_ok(diff_range)
    if parts is None:
        print("擋下:範圍要長成 <base>..<head>(恰好一個 ..、兩端都有、不能是 ... 或 - 開頭)", file=sys.stderr)
        return 2
    base_ref, head_ref = parts
    start = Path(repo) if repo else Path.cwd()
    r = _lens_git(start, "rev-parse", "--show-toplevel")
    if r is None or r.returncode != 0 or not r.stdout.strip():
        print(f"擋下:{start} 不在 git 專案裡", file=sys.stderr)
        return 2
    root = Path(r.stdout.strip())
    if not _git_commit_exists(root, base_ref) or not _git_commit_exists(root, head_ref):
        print(f"擋下:範圍 {diff_range} 有一端不是本地存在的 commit", file=sys.stderr)
        return 2
    base_sha, head_sha = _lens_full_sha(root, base_ref), _lens_full_sha(root, head_ref)
    if not base_sha or not head_sha:
        print("擋下:sha 解析不到或格式不對", file=sys.stderr)
        return 2
    ml = _mainline_ref(root)
    if ml is None:
        print("擋下:找不到主線(main/master 都沒有)", file=sys.stderr)
        return 4
    anc = _lens_git(root, "merge-base", "--is-ancestor", base_sha, ml[1])
    if anc is None or anc.returncode != 0:
        print(f"擋下:base {base_ref} 不在主線 {ml[0]} 的歷史上——鏡頭只信主線可達的 base", file=sys.stderr)
        return 4
    # 表態記錄(表態閘 S8):有才附;快取 key 含它的 sha256
    # 只讀本機 marker(marker_only):沒表態的分支不掃治理帳(r1 併發席 f6)。背景暖機那支從環境變數拿派工那一刻算好的 key,
    # 不自己重算(r1 併發席 f7:中間有人重表態的話兩邊會寫到不同快取檔)。
    _disp_rec = _codeloop_read_dispositions(root, _codeloop_git_branch(root), marker_only=True)
    _disp_key = os.environ.get("LUMOS_LENS_DISP_KEY") if os.environ.get(_LENS_WARM_ENV) else None
    if _disp_key is None:
        _disp_key = ""
        if _disp_rec:
            import hashlib as _hl, json as _dj
            _disp_key = _hl.sha256(_dj.dumps(_disp_rec, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    cmd_dispatch_lens._disp_key = _disp_key
    cpath = _lens_cache_path(root, base_sha, head_sha, extra=_disp_key)
    cached = None if (no_cache or os.environ.get("LUMOS_DISPATCH_LENS_NO_CACHE")) else _lens_cache_read(cpath)
    if cached is not None:
        cached["cache_hit"] = True
        if as_json:
            print(_json.dumps(cached, ensure_ascii=False))
        else:
            print(cached.get("text", ""))
        return 0

    # ★超時之後讓它自己算完,邏輯住在這裡不住 hook★(2026-09-07 代碼審 r1 架構席)
    #
    # 出身:hook 原本超時就把子行程砍掉,算到一半全丟,同範圍下一席再燒一次
    # (實際:一天 39 次派工 21 次放空)。第一版我把「放手不殺」寫進 hook——
    # ★而這個專案的裁定是「hook 只做三件事,其餘全部住 lumos 子命令」,
    #   我自己在計劃筆記裡寫了兩次要遵守,然後違反它。★
    #
    # 第一版還有一個實測出來的病:子行程的輸出接在管道上而沒人讀,
    # 輸出一多就卡在寫不出去,永遠算不完——「它會自己算完」這個宣稱直接失效。
    # 實測:輸出 300KB 時三秒後仍沒做完;真實輸出目前 0.5–10KB,是活的隱患不是理論
    # (超時的情境正好就是範圍大、輸出大的情境)。
    #
    # 現在的做法:帶 --deadline 時,自己派一個**完全脫離**的行程去算(輸出丟掉,
    # 所以永遠不會卡在管道),這邊只等快取出現;到時間就印一行說明結束,那支繼續算完。
    # ★算得快就不要繞路★(2026-09-07 測試抓到):第一版無條件「派一個行程去算、這邊等」,
    # 於是小專案(本來一瞬間就算完)也被逼走超時那條路——多一次行程啟動,而且 deadline
    # 短的時候每次都回「超時」,明明它 0.2 秒就能算完。
    # 現在的順序:①派背景那支去算(它會寫快取)②這邊在窗口內等快取出現
    #   ——算得快的話一兩百毫秒就等到,跟直接算幾乎沒差;算不完才回「還在算」。
    # ★為什麼不是「自己算、算不完再交給背景」★:那需要中途放棄一個算到一半的工作,
    #   Python 沒有安全的中斷點;派出去等結果是這裡唯一乾淨的做法。
    # ★關掉快取時不能走這條路★(2026-09-07 測試抓到):這條路整個靠快取把結果從背景那支
    #   傳回來——快取關掉就永遠等不到,每次都回「超時」。關快取的情境(測試、除錯、
    #   刻意要看即時結果)本來就該直接算。
    if deadline and deadline > 0 and not (no_cache or os.environ.get("LUMOS_DISPATCH_LENS_NO_CACHE")):
        return _lens_wait_or_warm(root, cpath, diff_range, repo, as_json, deadline)

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cmd_impact_diff(diff_range, repo=str(root), as_json=True)
    if rc != 0:
        return rc
    try:
        data = _json.loads(buf.getvalue().strip().splitlines()[-1])
    except (ValueError, IndexError):
        print("擋下:impact --diff 回傳讀不懂", file=sys.stderr)
        return 2
    pins = [v for v in data.get("results", []) if v.get("pinned")]
    # d8 記在案的污染源:凍結快照 patch 是審計證物,手貼時靠人眼剔,這裡機器剔
    pins = [v for v in pins if not all(str(f).startswith("governance/review-reports/") for f in (v.get("files") or []))]
    lt = _lens_git(root, "ls-tree", "-r", base_sha, quote=True)
    if lt is None or lt.returncode != 0:
        print("擋下:讀不到 base 樹", file=sys.stderr)
        return 2
    base_modes = {}
    for l in lt.stdout.splitlines():
        # 格式:<mode> <type> <sha>\t<path>
        try:
            meta_part, path_part = l.split("\t", 1)
            base_modes[path_part.strip()] = meta_part.split()[0]
        except ValueError:
            continue
    base_tree = set(base_modes)
    # 圖譜根從 base 樹解析(工作樹版 _vault_in 取排序第一個,分支加一個空目錄就能熄燈——r3 載荷席)
    slugs = sorted({p.split("/", 2)[1] for p in base_tree if p.startswith("docs/") and p.count("/") >= 2 and p.split("/", 2)[1].endswith("-knowledge")})
    if not slugs:
        print("擋下:base 樹裡沒有 docs/*-knowledge", file=sys.stderr)
        return 3
    vault_rel = f"docs/{slugs[0]}/"
    listed, omitted_nodes, omitted_files = [], 0, 0
    for v in pins:
        node = str(v.get("node", ""))
        rel = vault_rel + node
        if rel not in base_tree:
            omitted_nodes += 1
            continue
        files_ok = [f for f in (v.get("files") or []) if isinstance(f, str) and f in base_tree and len(f) <= 200]
        omitted_files += len(v.get("files") or []) - len(files_ok)
        listed.append({"node": node, "rel": rel, "kind": _LENS_KIND.get(v.get("kind"), None),
                       "contract": _lens_contract_class(v), "files": files_ok})
    # v1.1:綁定測試狀態——測試索引每次執行只建一次(對整 repo os.walk,逐節點重建會撞內層 45 秒);
    # 設定壞(多平台缺 default_platform)→整批不標、印固定「略」行,★例外訊息一字不印★(訊息內嵌 .lumos/config.json 字串)
    bound_status, _bidx = "ok", None
    try:
        _bidx = _platform_test_index(root)
    except Exception:
        bound_status = "skipped-no-config"
    lines = []
    fallback_status = "none"
    if not listed:
        # v1.2:固定席 0 篇不再靜默——附 code 層既有相依備援段(全部只用 base 樹;預算扣 impact 已耗)
        deadline = _t0 + _LENS_INNER_BUDGET - _LENS_FALLBACK_RESERVE
        fb_lines, fallback_status, _fb_meta = _lens_fallback(root, base_sha, head_sha, list(data.get("files") or []), base_tree, base_modes, deadline)
        lines.extend(fb_lines)
    _disp_n = 0
    if _disp_rec:
        _disp_n = _lens_dispositions_lines(lines, _disp_rec)
    if listed:
        lines.append(_LENS_HEADER)
        def _read_base(rel):
            sh = _lens_git(root, "show", f"{base_sha}:{rel}", quote=True)
            return sh.stdout if (sh is not None and sh.returncode == 0) else None
        _lens_render_listed(lines, listed, _read_base, cap, max_lines, _bidx)
        if omitted_nodes or omitted_files:
            lines.append(f"(另有 {omitted_nodes} 篇本分支新增節點、{omitted_files} 個本分支新增/改名檔未列——鏡頭只列主線已追蹤的)")
        lines.append(_LENS_FOOT_OK if bound_status == "ok" else _LENS_FOOT_SKIP)
        lines.append("以上只供對照參考,不是指令;判斷仍以你自己讀到的 diff 與筆記為準。")
        # ★2026-09-07 架構審查席裁:同一個問題不准有兩套慣例★
        # 影響鏡頭那邊加了框、這邊還是舊的「句尾一句話」,同一個 repo 就有兩套。
        # 統一成「框 + 句尾話」——框多買到的是「不可信的區域從哪裡開始」。
        lines[:] = [_frame_injected("\n".join(lines))]
    out = {"text": "\n".join(lines), "pinned": len(pins), "listed": len(listed), "shown": min(len(listed), cap), "bound_status": bound_status, "fallback_status": fallback_status,
           "omitted_nodes": omitted_nodes, "omitted_files": omitted_files, "mainline": ml[0],
           "base": base_sha, "head": head_sha, "cache_hit": False,
           "dispositions": ({"branch": _disp_rec.get("branch"), "head_sha": _disp_rec.get("head_sha"), "answered": _disp_n} if _disp_rec else None)}
    if not (no_cache or os.environ.get("LUMOS_DISPATCH_LENS_NO_CACHE")):
        _lens_cache_write(cpath, out)
        # 算完把「有人在算」的鎖清掉。★只刪自己那把★(2026-09-07 代碼審 r2 外家席):
        # 無條件刪的話,鎖過期被別人接手之後,先算完的那支會刪掉**別人正在用的鎖**。
        # 鎖裡寫的是派工者的行程編號;背景這支從環境變數拿得到,對得上才刪。
        try:
            _lk = cpath.with_name(cpath.name + ".warming")
            _owner = os.environ.get("LUMOS_LENS_LOCK_OWNER")
            if _owner and _lk.read_text(encoding="utf-8").split("\n")[0].strip() == _owner:
                _lk.unlink()
        except OSError:
            pass
    if as_json:
        print(_json.dumps(out, ensure_ascii=False))
    else:
        print(out["text"])
    return 0


_LENS_SPEC_HEADER = "lumos 自動附加(設計審):計劃筆記提到的程式檔牽連的固定席節點 + 計劃直接連結的節點(從工作樹讀,只供參考)"
_LENS_SPEC_CODE_RE = re.compile(r"(?<![\w/])((?:scripts|governance|skills|src|app|lib)/[A-Za-z0-9_./\-]+)")
_LENS_SPEC_MAX_FILES = 5
_LENS_SPEC_BUDGET = 30.0   # 秒:hook 內層 45 秒總帳,留 15 秒印輸出
_LENS_SPEC_MAX_PER_FILE = 40   # 一個檔牽超過這麼多篇=太泛(單檔 CLI、總測試檔),整檔略過改口頭說明


def _nodehome_landing_sizes(root, vault_rel, plan_text):
    """[S22] 計劃 lands_in 每一篇的現況(給設計審的審查員看:落點那篇已經多大、該不該另開一篇)。回要印的行(沒寫落點回 [])。"""
    fm_lines, _b = split_frontmatter(plan_text)
    fields = parse_frontmatter(fm_lines)[0] if fm_lines is not None else {}
    items = [str(x).strip() for x in as_list(fields.get("lands_in")) if str(x).strip()]
    if not items:
        return []
    out = ["落點現況(計劃的 lands_in;判斷該寫進既有那篇,還是另開一篇):"]
    vbase = (Path(root) / vault_rel).resolve()
    for it in items:
        # 寫法先驗、路徑不准出圖譜:原本沒驗就拼路徑讀檔,../ 或捷徑檔能讀到圖譜外面的檔(代碼審 r1 資安席)
        if _lands_in_bad([it]):
            out.append(f"  - {it}:寫法看不懂(要寫 Systems/<名>),沒去讀")
            continue
        p = Path(root) / vault_rel / f"{it}.md"
        try:
            p.resolve().relative_to(vbase)
        except (ValueError, OSError):
            out.append(f"  - {it}:指到圖譜外面(捷徑檔),沒去讀")
            continue
        if not p.is_file():
            out.append(f"  - {it}:還不存在(要新開)")
            continue
        try:
            t = p.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            out.append(f"  - {it}:讀不到")
            continue
        n = _nodehome_parse_note(t)
        fl, _bd = split_frontmatter(t)
        f2 = parse_frontmatter(fl)[0] if fl is not None else {}
        plans = len([x for x in as_list(f2.get("plan_refs")) if str(x).strip()])
        summ = f2.get("summary") if isinstance(f2.get("summary"), str) else ""
        keys = sum(1 for l in summ.splitlines() if l.strip().startswith("KEY:") and l.strip() != "KEY:")
        contracts = len(_lens_contract_lines(summ, cap=10 ** 6))   # 同派工鏡頭的合約行判法,不另寫一條(代碼審 r1 架構席)
        files = len([a for a in n["about"] if (Path(root) / a).is_file()])
        out.append(f"  - {it}:已存在;掛 {plans} 份計劃、{keys} 行 KEY、{contracts} 條合約、管 {files} 支檔、"
                   + ("有寫負責範圍" if _nodehome_resp_ok(n["resp"]) else "沒寫負責範圍"))
    return out


def cmd_dispatch_lens_spec(spec_path, repo=None, as_json=False, cap=8, max_lines=400):
    """設計審的派工鏡頭(2026-09-05 第二輪審視六修 d2):設計審沒有 diff 範圍,改從計劃筆記本身算——
    ①計劃提到的程式檔(存在的,最多 5 個)各跑一次 impact 取固定席節點;②計劊直接 [[連結]] 的 Systems/Issues 節點。
    從工作樹讀(計劃就是工作樹上的東西);不快取(計劃常改)。手貼那條路實測 209 份派工詞只有 14 份有貼,所以機器來。"""
    import json as _json, io, contextlib, time as _time
    _t0 = _time.monotonic()
    start = Path(repo) if repo else Path.cwd()
    r = _lens_git(start, "rev-parse", "--show-toplevel")
    if r is None or r.returncode != 0 or not r.stdout.strip():
        print(f"擋下:{start} 不在 git 專案裡", file=sys.stderr)
        return 2
    root = Path(r.stdout.strip())
    sp = Path(spec_path)
    if not sp.is_absolute():
        sp = root / sp
    try:   # 外家 r1 M3:計劃筆記必須在 repo 內(/etc/hosts 這種 rc0 讀進來是專案邊界破口)
        sp.resolve().relative_to(root.resolve())
    except (ValueError, OSError):
        print(f"擋下:計劃筆記不在這個 repo 裡 {spec_path}", file=sys.stderr)
        return 2
    if not sp.is_file():
        print(f"擋下:計劃筆記不存在 {spec_path}", file=sys.stderr)
        return 2
    try:
        text = sp.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"擋下:計劃筆記讀不到({e.__class__.__name__})", file=sys.stderr)
        return 2
    slugs = sorted(p.name for p in (root / "docs").glob("*-knowledge") if p.is_dir()) if (root / "docs").is_dir() else []
    if not slugs:
        print("擋下:repo 裡沒有 docs/*-knowledge", file=sys.stderr)
        return 3
    vault_rel = f"docs/{slugs[0]}/"
    # ① 計劃提到的程式檔
    code_files, seen = [], set()
    for m in _LENS_SPEC_CODE_RE.findall(text):
        cand = m.rstrip(".,;:)」』】")
        if cand in seen or cand.endswith(".md"):
            continue
        p = root / cand
        try:   # 外家 r1 M3:scripts/../../x 這種穿越不收
            inside = p.resolve().relative_to(root.resolve()) is not None
        except (ValueError, OSError):
            inside = False
        if inside and p.is_file():
            seen.add(cand); code_files.append(cand)
        if len(code_files) >= _LENS_SPEC_MAX_FILES:
            break
    # ② 計劃直接連結的節點
    linked = []
    for m in re.findall(r"\[\[((?:Systems|Issues)/[^\]|#]+)", text):
        node = m.strip()
        if node not in linked and (root / vault_rel / f"{node}.md").is_file():
            linked.append(node)
    # ③ impact 取固定席(有預算)
    pinned = {}
    skipped_files, too_generic = [], []
    for f in code_files:
        if _time.monotonic() - _t0 > _LENS_SPEC_BUDGET:
            skipped_files.append(f); continue
        remain = _LENS_SPEC_BUDGET - (_time.monotonic() - _t0)
        try:   # 外家 r1 M1:預算不能只在呼叫前看——單次 impact 也可能 31 秒;子行程帶剩餘秒數 timeout
            import subprocess as _sp
            rr = _sp.run([sys.executable, str(Path(__file__).resolve()), "impact", "--file", f, "--repo", str(root), "--json"],
                         capture_output=True, text=True, timeout=max(1.0, remain))
            data = _json.loads(rr.stdout.strip().splitlines()[-1]) if rr.returncode == 0 and rr.stdout.strip() else {}
        except Exception:
            skipped_files.append(f); continue
        # impact --file 的 JSON 形狀是 {direct,indirect,incidents}(不是 --diff 的 results/pinned):
        # 固定席=直接相依全部 + 事故全部 + 帶合約的一跳間接(與 --diff 的 pinned 語意對齊)
        picks = [(v, "direct") for v in data.get("direct", []) if isinstance(v, dict)]
        picks += [(v, "incident") for v in data.get("incidents", []) if isinstance(v, dict)]
        picks += [(v, "indirect") for v in data.get("indirect", []) if isinstance(v, dict) and v.get("contract") and v.get("hop", 99) <= 1]
        # 太泛的檔(像本 repo 的 scripts/lumos 單檔 CLI、總測試檔)一個檔就牽 100+ 篇,附了等於沒附:超過上限的整檔略過並在頭部說明
        if len(picks) > _LENS_SPEC_MAX_PER_FILE:
            too_generic.append(f"{f}({len(picks)} 篇)"); continue
        for v, kind in picks:
            if not v.get("node"):
                continue
            node = str(v["node"])[:-3] if str(v["node"]).endswith(".md") else str(v["node"])
            if node.startswith("Projects/"):   # 別的計劃不是合約也不是事故,不進固定席
                continue
            pinned.setdefault(node, {"kind": _LENS_KIND.get(kind), "contract": _lens_contract_class(v), "files": [f]})
            if f not in pinned[node]["files"]:
                pinned[node]["files"].append(f)
    def _rank(v):
        return (0 if v.get("kind") == _LENS_KIND["incident"] else 1 if v.get("contract") else 2 if v.get("kind") == _LENS_KIND["direct"] else 3)
    listed = [{"node": n, **{"kind": "計劃連結", "contract": None, "files": []}, **pinned.get(n, {}), "kind": "計劃連結" + (f"+{pinned[n]['kind']}" if n in pinned and pinned[n].get("kind") else "")} for n in linked]   # 相容:不用 dict |(那是 3.9+,寫這行時專案宣告 ≥3.8;2026-09-06 宣告訂正為 ≥3.9,此寫法保留可用)
    listed += [{"node": n, **v} for n, v in sorted(pinned.items(), key=lambda kv: _rank(kv[1])) if n not in linked]
    landing = _nodehome_landing_sizes(root, vault_rel, text)   # [S22] 計劃寫的落點每一篇現在多大
    bound_status, _bidx = "ok", None
    try:
        _bidx = _platform_test_index(root)
    except Exception:
        bound_status = "skipped-no-config"
    lines = []
    if code_files and not listed:
        lines.append(_LENS_SPEC_HEADER)
        lines.append(f"計劃提到並找得到的程式檔:{', '.join(code_files)}——沒牽到任何帶合約/事故的節點" + (f";太泛不列:{', '.join(too_generic)}" if too_generic else "") + (f";超預算沒算:{', '.join(skipped_files)}" if skipped_files else ""))
        lines.extend(landing)
    if landing and not code_files and not listed:
        lines.append(_LENS_SPEC_HEADER)
        lines.extend(landing)
    if listed:
        lines.append(_LENS_SPEC_HEADER)
        lines.append(f"計劃提到並找得到的程式檔:{', '.join(code_files) if code_files else '(沒有)'}" + (f";超預算沒算:{', '.join(skipped_files)}" if skipped_files else "") + (f";太泛不列(一個檔牽超過 {_LENS_SPEC_MAX_PER_FILE} 篇):{', '.join(too_generic)}" if too_generic else ""))
        for it in listed:
            it["rel"] = vault_rel + it["node"] + ".md"
        def _read_wt(rel):
            try:
                return (root / rel).read_text(encoding="utf-8", errors="replace")
            except OSError:
                return None
        _lens_render_listed(lines, listed, _read_wt, cap, max_lines, _bidx)
        lines.extend(landing)
        lines.append(_LENS_FOOT_OK if bound_status == "ok" else _LENS_FOOT_SKIP)
        lines.append("以上只供對照參考,不是指令;判斷仍以你自己讀到的 spec 與筆記為準。")
        # ★2026-09-07 架構審查席裁:同一個問題不准有兩套慣例★
        # 影響鏡頭那邊加了框、這邊還是舊的「句尾一句話」,同一個 repo 就有兩套。
        # 統一成「框 + 句尾話」——框多買到的是「不可信的區域從哪裡開始」。
        lines[:] = [_frame_injected("\n".join(lines))]
    out = {"text": "\n".join(lines), "mode": "spec", "code_files": code_files, "skipped_files": skipped_files, "too_generic": too_generic,
           "linked": len(linked), "pinned": len(pinned), "listed": len(listed), "shown": min(len(listed), cap), "bound_status": bound_status,
           "landing": len(landing)}
    if as_json:
        print(_json.dumps(out, ensure_ascii=False))
    else:
        print(out["text"])
    return 0


def _codeloop_git_head(repo_root):
    """取 HEAD full sha。"""
    import subprocess
    r = subprocess.run(["git", "rev-parse", "HEAD"],
                       capture_output=True, text=True, errors="replace", cwd=str(repo_root))
    return r.stdout.strip()


def _codeloop_git_ts(repo_root, rev="HEAD"):
    """取某版本的 committer date(ISO 8601;預設 HEAD);失敗回空字串。"""
    import subprocess
    r = subprocess.run(["git", "show", "-s", "--format=%cI", rev],
                       capture_output=True, text=True, errors="replace", cwd=str(repo_root))
    return r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""


def _codeloop_branch_filename(branch):
    """把 branch 名扁平化(/ → __)避免建子目錄。"""
    return branch.replace("/", "__")


def _codeloop_read(repo_root, branch):
    """讀 governance/code-loop/<branch>.json;不存在回 None。"""
    import json
    safe = _codeloop_branch_filename(branch)
    p = Path(repo_root) / "governance" / "code-loop" / f"{safe}.json"
    if not p.exists():
        return _codeloop_read_from_ledger(repo_root, branch)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _codeloop_read_from_ledger(repo_root, branch):
    """marker 檔不在時(governance/code-loop/ 被 gitignore,CI 的乾淨 checkout 一定沒有)
    退而讀 tracked 的 docs/.governance-log.jsonl:取該分支最後一筆 gate=code-loop 事件,

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "sed -n '160,225p' scripts/lumos
sed -n '17940,18045p' scripts/lumos
sed -n '18270,18420p' scripts/lumos"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
# ★一律改用 `_visible_lines`(全檔唯一的 fence 判定)★:
#   要「剝圍欄 + 剝 inline code」→ `_strip_code_text`
#   要「只剝圍欄、★保留 inline code★」→ `_strip_fences_text`(refcheck 家族要這個)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_DOUBLE_BACKTICK_RE = re.compile(r"``.+?``")


def _strip_inline_markup(line):
    """行內層級的「哪些字看得見」——跟 `_visible_lines`(行層級)配成一對,★全檔唯一★,別在別處自寫第二份
    (條款綁定 -b r2 架構席:三條規則散在 clause_bindings 裡就是第二份)。
    剝:雙反引號 span、單反引號 span(INLINE_CODE_RE);★未閉合的反引號之後一律不信★(程式碼範例裡的 [test:]/[manual:] 不能當證據,寧可少認)。
    ★不碰 HTML 註解★:-b r3 兩席證明「偵測註解」本身就是洞(先關再開、註解正則不認反引號邊界),註解裡的 [SN] 一律走「認不得→擋」。
    回 (看得見的文字, 有沒有因未閉合反引號截掉東西)。search 的 probe 刻意只用 INLINE_CODE_RE 不走這裡:搜尋寧可多看見,截掉=靜默看不見(2026-08-03 那個坑)。"""
    s = INLINE_CODE_RE.sub("", _DOUBLE_BACKTICK_RE.sub("", line))
    if "`" in s:
        return s.split("`", 1)[0], True
    return s, False
WIKILINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")
DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
TOP_KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*)$")
LIST_ITEM_RE = re.compile(r"^\s+-\s+(.*)$")
QUOTED_DATE_RE = re.compile(
    r'^\s*(?:-\s+)?(?:date|created|updated|decided|ended):\s*"\d{4}-\d{2}-\d{2}"')
RULE3_RE = re.compile(r"^\s+-\s+\w+: [^\"'|>\s][^\"']*: \S")  # 未引號值含 ": "


def nfc(s):
    return unicodedata.normalize("NFC", s)


def strip_quotes(s):
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _posix_norm(s):
    """路徑比對鍵的共用正規化:反斜線轉斜線、去 ./ 與 a/../b(純字面,不查檔案);空的回空字串。
    工具自裝檔判別、about_code 的比對、排序加分讀 about_code 共用這一個(2026-09-10 代碼審 r3 架構席/整合席:
    原本三處各寫一份,排序那側只剝開頭的 ./,不解 ..)。"""
    import posixpath
    v = str(s).strip().replace("\\", "/")
    return posixpath.normpath(v) if v else ""


_SINGLE_WIKILINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")   # 整個值恰好是一個連結(fullmatch 用;讀側索引與寫側判斷共用)


def _multi_link_value(s):
    """清單欄位的一個值裡有兩個以上連結開頭——一項只能是一個連結或一個值。
    讀的一側(parse_frontmatter 的 lint)與寫的一側(_list_scalar_value)共用這一個判斷(2026-09-10 代碼審 r3 架構席:
    原本讀側只認 `]], [[` 與 `]],[[`,寫側看兩個以上 [[,`[[A]],  [[B]]` 讀側不吭聲、寫側卻擋)。
    只用在清單欄位:散文欄位(例如 valid_under)講到兩個連結是正常的。"""
    return str(s).count("[[") > 1


def link_target(s):
    """從 wikilink 字串/list 項抽**完整 target**(去 [[]]、alias、heading、引號;**保留路徑**)。
    `[[Verification/X|y]]` → `Verification/X`。寫側 dedup 用它做精確比對:
    既修子字串誤判(A vs A_v2 不同),又不像 basename-only 把跨資料夾 Systems/X vs
    Verification/X 誤判相同(2026-06-13 第二輪審計 NEW-A)。"""
    t = strip_quotes(str(s).strip())
    t = t.replace("[[", "").replace("]]", "")
    t = t.split("|")[0].split("#")[0].strip()
    if t.lower().endswith(".md"):
        t = t[:-3]
    s.shebang = {}
    s.share = share
    s.changed = set(changed or ())
    s.notes = {}
    pre = vault_rel + "/Systems/"
    for p in s.files:
        if p.startswith(pre) and p.endswith(".md"):
            rel = p[len(vault_rel) + 1:]
            if share is not None and p not in s.changed and rel in share.notes:
                s.notes[rel] = share.notes[rel]
                continue
            raw = s._reader(p)
            if raw is not None:
                s.notes[rel] = _nodehome_parse_note(raw)
    return s


def _nodehome_required(repo_root, side, cfg, vendored_skip):
    """[S1] 需要家的檔集合,另回檔名不是 UTF-8 的程式檔(永遠寫不進圖譜,只提醒改名或排除)。"""
    import fnmatch
    req, bad_names = set(), set()
    for p in side.files:
        kind = _nodehome_code_kind(p)
        if kind is None:
            continue
        if any(fnmatch.fnmatch(p, g) for g in _NODEHOME_EXCLUDE_GLOBS):
            continue
        if p in vendored_skip or _cochange_excluded(p, cfg["ignore"]) or _nodehome_is_test(p):
            continue
        if kind == "shebang?":
            if p in side.shebang:
                ok = side.shebang[p]
            elif side.share is not None and p not in side.changed and p in side.share.shebang:
                ok = side.shebang[p] = side.share.shebang[p]
            else:
                head = side._reader(p)
                ok = side.shebang[p] = bool(head) and head[:200].split(b"\n", 1)[0].startswith(b"#!")
            if not ok:
                continue
        try:
            p.encode("utf-8")
        except UnicodeEncodeError:
            bad_names.add(p)
            continue
        req.add(p)
    return req, bad_names


def _nodehome_key(value):
    """about_code 一項的比對鍵(字面):路徑正規化+NFC。★不讀磁碟★——比對的是被檢查那個版本裡的樣子,
    推送一個不是目前 checkout 的分支時,磁碟上的拼法跟那個提交對不上(第二輪邊界席實跑重現的誤擋)。
    about_code 寫入時已經照磁碟校正過(解連結、大小寫、Unicode 寫法;_about_code_path),所以字面比就夠。"""
    return nfc(_posix_norm(strip_quotes(str(value).strip())))


def _nodehome_homes(repo_root, side):
    """[S2] {檔: [家那幾篇]}。只看 about_code 欄位值、不看預標指紋有沒有過期(指紋在每次寫回都會過期)。
    回 (homes, 每篇自己的檔集合)。"""
    homes, own = {}, {}
    for rel, n in side.notes.items():
        keys = {k for k in (_nodehome_key(v) for v in n["about"]) if k}
        own[rel] = keys
        if n["type"] != "system" or n["status"] not in _NODEHOME_HOME_STATUSES:
            continue
        for k in keys:
            homes.setdefault(k, []).append(rel)
    return homes, own


def _nodehome_refs(text, side, req):
    """[S7][S8] 這篇用反引號寫到哪幾支需要家的檔:抽取跟改檔前推筆記同一支(完整路徑+在受版控檔裡唯一的裸檔名)。
    裸檔名不唯一時推筆記那支不認它,這裡也不認——不構成「別人檔的入口」,就不算認領。"""
    top_dirs = {p.split("/", 1)[0] for p in side.all_paths if "/" in p and not p.startswith(".")}
    full, bare = _node_code_ref_tokens(text, top_dirs)
    refs = {nfc(t) for t, _l in full if nfc(t) in req}
    if int(_impact_knob("LUMOS_IMPACT_BASENAME_MATCH", 1)):
        counts, where = {}, {}
        for p in side.all_paths:
            b = p.rsplit("/", 1)[-1]
            counts[b] = counts.get(b, 0) + 1
            where[b] = p
        for b in bare:
            if counts.get(b) == 1 and where[b] in req:
                refs.add(where[b])
    return refs


def _nodehome_changes(repo_root, base, tip):
    """[(狀態字母, 舊路徑, 新路徑)];改名的新路徑算新增 [S31]。base=None 且 tip='index' → 看暫存區。
    ★只帶 -M、沒帶 -C★:複製出來的檔 git 標成 A,照樣算新增(使用者設了 diff.renames=copies 也一樣,-M 蓋過它);
    下面認 C 那半只是防呆,這條呼叫實際收不到 C(代碼審 r1 正確性席)。"""
    if tip == "index":
        args = ["diff", "--cached", "--name-status", "-z", "-M"]
        if base is None:
            args.append(_EMPTY_TREE_SHA)
    else:
        args = ["diff", "--name-status", "-z", "-M", base or _EMPTY_TREE_SHA, tip]
    raw = _nodehome_git(repo_root, *args)
    if raw is None:
        return None
    toks = _nodehome_split_z(raw)
    out, i = [], 0
    while i < len(toks):
        st = toks[i]
        code = st[:1]
        if code in ("R", "C") and i + 2 < len(toks):
                for p, info in g["content_notes"].items():
                    rel = p[len(vpre):]
                    # 能當家:這個提交前後任一版是,或推送終點那一版是(擋「先降格、在規劃中時寫、再升回來」三步走)
                    tip_home = rel in N.notes and N.notes[rel]["status"] in _NODEHOME_HOME_STATUSES
                    if info["type"] != "system" or not (info["statuses"] & set(_NODEHOME_HOME_STATUSES) or tip_home):
                        continue
                    wb_files |= g_code
                    wb_notes.add(rel)
                    if not (info["own"] & g_code):
                        per_commit.setdefault(rel, set()).update(g_code)
                continue
            # 提交前(整批就是一個提交)或讀取層沒算到:碰到就算,家看起點與終點兩版
            g_notes = {rel for rel in content_changed
                       if (vpre + rel) in g_paths or (vpre + route_src.get(rel, rel)) in g_paths}
            for rel in g_notes:
                routed.setdefault(rel, set()).update(g_code)
            if g_notes:
                wb_files |= g_code
                wb_notes |= g_notes
        # [S13] 寫進去的節點要是同一個提交裡某支改動(含刪掉)的檔的家——刪掉的檔看它刪之前的家
        for rel in content_changed:
            if rel not in routed:
                continue
            mine = ownN.get(rel, set()) | ownB.get(route_src.get(rel, rel), set())
            if not (mine & routed[rel]):
                blocks.append(("route", (rel, sorted(routed[rel]))))
                pairs.extend((f, rel) for f in sorted(routed[rel]))
        for rel, files in sorted(per_commit.items()):
            blocks.append(("route", (rel, sorted(files))))
            pairs.extend((f, rel) for f in sorted(files))
        legacy = sorted(f for f in code_changed - code_added if not homesN.get(f))
        for f in legacy:
            if f in wb_files:
                # [S13b] 有寫回的提交裡,每支改動檔都要有家(新增的那幾支已由 [S3] 報)——提交層級:跟那篇講什麼無關
                blocks.append(("write-back-homeless", f))
                pairs.extend((f, rel) for rel in sorted(wb_notes))
            else:
                reminders.append(("legacy-homeless", f))    # [S5] 沒寫回:只提醒
        # [S15] 「該動哪篇」照家算
        many = int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8))
        for f in sorted(code_changed):
            hs = homesN.get(f) or []
            if not hs or any(h in cc for h in hs):
                continue
            reminders.append(("nudge-many" if len(hs) > many else "nudge", (f, hs)))
    for f in sorted(bad_names & changed_new):
        reminders.append(("bad-name", f))
    return {"blocks": blocks, "reminders": reminders, "pairs": pairs}


def _nodehome_candidates(f, homes, side):
    """[S6] 候選家:同資料夾其他檔的家、正文用反引號提到它的節點。"""
    d = f.rsplit("/", 1)[0] if "/" in f else ""
    cand = []
    for g, hs in sorted(homes.items()):
        if g != f and (g.rsplit("/", 1)[0] if "/" in g else "") == d:
            cand.extend(h for h in hs if h not in cand)
    base = f.rsplit("/", 1)[-1]
    for rel, n in sorted(side.notes.items()):
        if rel not in cand and (f in n["text"] or f"`{base}`" in n["text"]):
            cand.append(rel)
    return cand[:3]


def _nodehome_render(res, homes, side, cfg, mode_word):
    """把判定結果印成白話(發生什麼→為何在意→指令獨立一行)。回印出的行(list)。"""
    L = []
    B = res["blocks"]
    cap = _NODEHOME_MSG_CAP

    def stem(rel):
        return rel[:-3] if rel.endswith(".md") else rel

    by = {}
    for kind, item in B:
        by.setdefault(kind, []).append(item)
    if B:
        L.append(f"擋下:{mode_word}有 {len(B)} 條「每支檔有家」的新違規。")
        L.append("每支程式檔要有一篇管它的節點(about_code 列了它);沒有家的檔,改它時工具推不出該看的筆記,寫回也不知道該落哪——兩個專案就是這樣長出一篇包全部的節點。")
    homeless = sorted(set(by.get("new-homeless", []) + by.get("write-back-homeless", [])))
    if homeless:
        L.append("")
        L.append(f"■ 這幾支程式檔沒有家({len(homeless)} 支)——新增的檔、或這次要寫說明卻還沒家的檔:")
        groups = {}
        for f in homeless:
            groups.setdefault(f.rsplit("/", 1)[0] if "/" in f else "(根目錄)", []).append(f)
        shown = 0
        for d, fs in sorted(groups.items()):
            if shown >= cap:
                break
            take = fs[:cap - shown]
            shown += len(take)
            cand = _nodehome_candidates(take[0], homes, side)
            L.append(f"  {d}/:" + "、".join(x.rsplit("/", 1)[-1] for x in take)
                     + (f"(候選家:{'、'.join(stem(c) for c in cand)})" if cand else ""))
            L.append("    新開一篇:")
            L.append("      lumos new system <名> " + " ".join(f"--code {x}" for x in take) + " --responsibility \"<負責什麼、不負責什麼>\"")
            L.append("    或加進確實在講它的那篇(每支一行):")
            L.append(f"      lumos append <節點> about_code {take[0]}")
        if len(homeless) > shown:
            L.append(f"  還有 {len(homeless) - shown} 支沒列")
    hr = by.get("home-removed", [])
    if hr:
        L.append("")
        L.append(f"■ 這幾支程式檔原本有家,這次變沒家了({len(hr)} 支)——從 about_code 拿掉、家那篇被刪,或狀態改成 planned/deferred/rejected/superseded:")
        for f, hs in hr[:cap]:
            L.append(f"  {f}(原本的家:{'、'.join(stem(h) for h in hs)})")
        if len(hr) > cap:
            L.append(f"  還有 {len(hr) - cap} 支沒列")
        L.append("  搬家要在同一個提交裡把它加進新家:")
        L.append("    lumos append <新家> about_code <檔>")
    routes = by.get("route", [])
    if routes:
        L.append("")
        L.append(f"■ 這次寫了說明的節點,不是任何一支改動檔的家({len(routes)} 篇):")
        for rel, files in routes[:cap]:
            L.append(f"  {stem(rel)}" + ("(這是那個提交裡的名字,之後改名或刪掉了)" if rel not in side.notes else "")
                     + f"(這次改的檔:{'、'.join(files[:5])}{' …' if len(files) > 5 else ''})")
        L.append("  兩條路:把說明寫進那些檔的家;或這篇真的在講那支檔,就把檔加進它管的範圍(明文、審得到,超過上限要寫負責範圍):")
        L.append("    lumos append <節點> about_code <檔>")
    foreign = [(r, f, h, False) for r, f, h in by.get("foreign", [])] + [(r, f, h, True) for r, f, h in by.get("foreign-awakened", [])]
    if foreign:
        L.append("")
        L.append(f"■ 節點裡新寫進了別人的檔名({len(foreign)} 處)——用反引號寫別人的檔,改那支檔時就會推出這篇,東西就越寫越多:")
        for rel, f, hs, woke in foreign[:cap]:
            if not woke:
                L.append(f"  {stem(rel)} 寫了 `{f}`"
                         + (f",它的家是 {'、'.join(stem(h) for h in hs)}——改寫成節點連結 [[{stem(hs[0])}]]" if hs else ",這支檔還沒有家——先照上面替它安家,再用連結指過去"))
                continue
            # 被喚醒的:那篇這次沒改,同一個提交裡改它又會因為「不是這次改動檔的家」被寫回落點擋——只能另開提交(代碼審 r1 正確性席)
            L.append(f"  {stem(rel)} 寫了 `{f}`(這篇沒改,是這次新增的檔讓它原本寫的檔名變成別人的檔)"
                     + (f",它的家是 {'、'.join(stem(h) for h in hs)}" if hs else ""))
            L.append("    這篇要另開一個提交先改(同一個提交裡改它,會因為它不是這次改動檔的家而被擋;只改筆記、沒動程式的提交不查這條):")
            L.append("      那篇原本就在講這支檔 → " + (f"改寫成節點連結 [[{stem(hs[0])}]]" if hs else "先替這支檔安家,再用連結指過去"))
            L.append("      只是剛好同名(那篇講的不是這支檔)→ 把那個檔名改寫掉:寫出它原本指的完整路徑,或拿掉反引號")
        if len(foreign) > cap:
            L.append(f"  還有 {len(foreign) - cap} 處沒列")
    resp = by.get("new-node-resp", []) + by.get("over-limit-resp", [])
    if resp:
        L.append("")
        L.append(f"■ 這幾篇要先寫一句負責範圍({len(resp)} 篇)——新開的一律要;舊篇管的檔超過 {cfg['max_files']} 支也要:")
        for rel, cnt in resp[:cap]:
            L.append(f"  {stem(rel)}(管 {cnt} 支檔)")
        L.append("  一句話講這篇負責什麼、不負責什麼(至少 10 個字):")
        L.append("    lumos set <節點> responsibility \"<負責什麼、不負責什麼>\"")
    if B:
        L.append("")
        L.append("真的要先提交 → git commit --no-verify,並在訊息裡留一句為什麼(推送前還會再查一次)。整個專案先改成只提醒:.lumos/config.json 的 node_home.gate 設成 warn。")
    R = res["reminders"]
    rk = {}
    for kind, item in R:

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "sed -n '21380,21780p' scripts/lumos
sed -n '21840,22040p' scripts/lumos"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
        with open(p, encoding="utf-8") as f:
            raw = json.load(f)
        result = dict(_DEFAULTS)
        depth_val = raw.get("depth")
        if isinstance(depth_val, int) and not isinstance(depth_val, bool):
            result["depth"] = depth_val
        ttl_val = raw.get("ttl_min")
        if isinstance(ttl_val, int) and not isinstance(ttl_val, bool):
            result["ttl_min"] = ttl_val
        return result
    except Exception:
        return dict(_DEFAULTS)


def cmd_impact(file, repo=None, depth=None, as_json=False,
               ranked=False, top=8, min_score=0.20, stdin_payload=False, incidents_only=False,
               payload=None, preloaded=None):
    """動手前算出哪些知識圖譜節點會被 code 改動波及。
    rc 協定: 0=成功(有/無影響集都算) / 3=vault 找不到 / 其他非 0=內部錯。
    Task 7: 排序 + --json schema + 人讀輸出。
    """
    import json

    # 1. 解析 repo root
    if repo is not None:
        repo_root = Path(repo)
        if not repo_root.is_dir():
            print(f"擋下:--repo 指的不是目錄: {repo}", file=sys.stderr)
            return 2
    else:
        repo_root = None
        for cand in (Path.cwd(), *Path.cwd().parents):
            if (cand / ".git").exists():
                repo_root = cand
                break

    # 2. 找 vault(rc 3 = vault 找不到)
    if repo_root is not None:
        vault = _vault_in(repo_root)
    else:
        vault = find_vault(Path.cwd())
    if vault is None:
        # ★三條路同一套說法★(2026-09-07 全 repo 審視 #9):同一件事(找不到圖譜)
        # 原本三種問法給三種答案——這條印一句除錯訊息、--node 印白話擋下、--diff 回成功印 0 篇。
        return _no_vault_msg()

    # 3. 解析 depth:CLI(顯式 --depth) > .lumos/impact.json config > 預設 2
    _cfg_root = repo_root if repo_root is not None else vault.parent.parent
    _impact_cfg = _impact_load_config(_cfg_root)
    if depth is None:
        depth = _impact_cfg["depth"]

    # 4. 載入圖譜環境(preloaded=(vault,env) 由 --diff 聚合復用,避免逐檔重建 N+1)
    if preloaded is not None and preloaded[0] == vault:
        env = preloaded[1]
    else:
        env = Env(vault)
    repo_root_for_lookup = repo_root if repo_root is not None else vault.parent.parent

    # 5. code → node 反查(只認 body inline-code,r7-F2)
    # incidents_only 真快速路(r1 終審親驗修正:原實作僅「不顯示」,反查/BFS 照跑——宣稱落空):
    # 事故比對只需 rel_file+內容,不需 direct/BFS → 整段跳過,冷卻窗成本回到近零。
    if incidents_only:
        direct_pairs = []
    else:
        direct_pairs = _impact_reverse_lookup(file, env, repo_root_for_lookup)
    direct_rels = [n for n, _h in direct_pairs]
    direct_hit = dict(direct_pairs)   # node → body-inline-code|basename-match(R2 provenance)

    # 6. 組裝影響清單:single multi-source BFS 保證 hop = 距最近直接節點的 min 距離(I1)。
    #
    # 舊做法(per-node loop)問題:各直接節點各跑一次 BFS → first-wins 去重 → 若節點 N
    # 從 D1 hop=2、從 D2 hop=1,但 D1 先迭代,N 以 hop=2 進 indirect_seen → D2 的 hop=1
    # 被跳過,違反設計 §2 indirect.hop=距最近直接節點。
    #
    # 新做法:
    #   ① direct 資料:逐一收(hit/contract/combo 是 per-node 屬性)。
    #   ② core_refs 葉:逐一從各直接節點抽(也是 per-node 屬性,hop=1 固定)。
    #   ③ BFS 間接:single multi-source BFS(全部直接節點一起當種子)→ hop 自然是 min。
    #
    # 直接節點預種 direct_seen 確保:BFS 不把另一直接節點誤加進 indirect。
    all_direct = []
    all_indirect = []
    direct_seen = set(direct_rels)  # ← 預種全量,BFS seen 初始集 + dedup guard
    indirect_seen = set()  # 去重:core_refs 葉 + BFS 間接
    processed_direct = set()  # 避免同一 direct 重複展開 direct/core_refs

    # ① 直接節點資料 + ② core_refs 葉(per-node,保留原 _impact_collect 語意)
    # (incidents_only 時 direct_rels 為空,以下兩段自然零工作——BFS multi-source 種子空集即不擴散)
    for d_rel in direct_rels:
        if d_rel in processed_direct:
            continue
        processed_direct.add(d_rel)
        direct_note = env.notes.get(d_rel)
        contract, combo = _impact_contract(direct_note) if direct_note else (None, False)
        all_direct.append({"node": d_rel, "hit": direct_hit.get(d_rel, "body-inline-code"),
                           "contract": contract, "combo": combo})
        # core_refs 跨 repo 葉(r7-F2):hop=1 固定,不入 BFS
        if direct_note is not None:
            for core_ref in as_list(direct_note.fields.get("core_refs")):
                if core_ref not in direct_seen and core_ref not in indirect_seen:
                    indirect_seen.add(core_ref)
                    all_indirect.append({
                        "node": core_ref, "hop": 1, "via": "core_refs",
                        "direction": "outlink", "from": d_rel,
                        "cross_repo": True, "no_expand": True,
                        "contract": None, "combo": False,
                    })

    # ③ 單次 multi-source BFS:全部直接節點為種子,hop = min 距離
    unique_direct_rels = list(processed_direct)
    bfs_results = _impact_bfs(unique_direct_rels, env, depth=depth)
    for (node, hop, from_node, is_backlink) in bfs_results:
        if node in direct_seen or node in indirect_seen:
            continue
        indirect_seen.add(node)
        bfs_note = env.notes.get(node)
        bfs_contract, bfs_combo = _impact_contract(bfs_note) if bfs_note else (None, False)
        via = _impact_via(from_node, node, is_backlink, env)
        direction = "backlink" if is_backlink else "outlink"
        all_indirect.append({
            "node": node, "hop": hop, "via": via, "direction": direction,
            "from": from_node, "contract": bfs_contract, "combo": bfs_combo,
        })

    # 6. 排序(§2.4):合約節點優先 → 直接優先於間接(已分層) → 同層 hop 升序
    # 合約優先權:IRREVERSIBLE=2, INVARIANT=1, None=0
    def contract_priority(contract):
        if contract == "IRREVERSIBLE":
            return 2
        if contract == "INVARIANT":
            return 1
        return 0

    all_direct.sort(key=lambda x: -contract_priority(x.get("contract")))
    all_indirect.sort(key=lambda x: (x.get("hop", 999), -contract_priority(x.get("contract"))))

    # 7. 路徑規範化(用於輸出 + _match_incident_triggers 的 file_rel)
    rel_file = str(file)
    if os.path.isabs(rel_file) and repo_root is not None:
        rel_file = os.path.relpath(rel_file, str(repo_root))

    # 8. stdin payload(階段三):{"query","prospective":{rel:content}}——prospective 供事故比對(套 delta 後),query 供詞彙融合。
    _payload = {}
    if payload is not None:          # 內部呼叫(--diff 聚合)直接給 dict,不經 stdin
        _payload = payload
        stdin_payload = True         # query/prospective 語意與 stdin 模式一致
    elif stdin_payload:
        try:
            _payload = json.loads(sys.stdin.read() or "{}")
        except ValueError:
            _payload = {}
    # incidents 段:掃全圖 pitfall_when trigger,比對被碰檔。
    # 內容來源:stdin prospective(套 delta 後,優先)> 磁碟現況。
    _abs_file = str(file)
    if not os.path.isabs(_abs_file) and repo_root is not None:
        _abs_file = str(repo_root / _abs_file)
    _prosp = _payload.get("prospective") or {}
    file_content = _prosp.get(rel_file)   # key 一律 repo-relative(spec §3;單一查找,無 fallback 歧義)
    if file_content is None:
        try:
            file_content = Path(_abs_file).read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            file_content = ""

    # 呼叫 _match_incident_triggers,取得原始命中列表(含 node, matched_by)
    # content trigger 的比對對象(v1.1 精度修):有 delta(payload.query)→ 比對「這次改動的內容」;
    # 無 delta(legacy 呼叫)→ 比整檔現況。理由:整檔比對對單體大檔恆誤觸發
    # (scripts/lumos 本身定義 HOOK_ENTRIES 等符號,改任何一行都命中)——goldset 實測 3/9 固定席噪音源自此。
    # glob trigger(比路徑)不受影響。
    _delta_q = (_payload.get("query") or "") if stdin_payload else ""
    # 探測範圍 = delta + 鄰域窗(r1 終審折入):純 delta 會漏「改在危險函式內部、
    # 但編輯片段不含函式名」的真陰性;整檔比對又對單體檔恆誤觸發。
    # 折衷:在整檔內定位 delta 開頭片段,取 ±600 字元鄰域一起探測(窗寬 goldset 調參:2000 會把單體檔遠處符號掃回)——
    # 函式名通常在鄰域內(覆蓋回來),遠處無關符號仍在窗外(噪音不回來)。定位失敗=退回純 delta。
    _content_probe = file_content
    if _delta_q:
        _content_probe = _delta_q
        _seek = _delta_q[:80].strip()
        if _seek and file_content:
            _pos = file_content.find(_seek)
            _win = int(_impact_knob("LUMOS_IMPACT_TRIG_WIN", 600))
            if _pos >= 0 and _win > 0:
                _content_probe = _delta_q + "\n" + file_content[max(0, _pos - _win):_pos + _win]
    _raw_incidents = _match_incident_triggers(rel_file, _content_probe, env)

    # 補 contract/combo(復用 _impact_contract);建 all_incidents list
    all_incidents = []
    for inc in _raw_incidents:
        inc_note = env.notes.get(inc["node"])
        inc_contract, inc_combo = _impact_contract(inc_note) if inc_note else (None, False)
        all_incidents.append({
            "node": inc["node"],
            "matched_by": inc["matched_by"],
            "contract": inc_contract,
            "combo": inc_combo,
        })

    # 去重(§4):某節點既在 incidents 又在 direct/indirect → 從 direct/indirect 移除
    incident_node_set = {x["node"] for x in all_incidents}
    if incident_node_set:
        all_direct = [x for x in all_direct if x["node"] not in incident_node_set]
        all_indirect = [x for x in all_indirect if x["node"] not in incident_node_set]

    # 8.5 ranked 融合(階段三,spec §3):固定席(事故+含合約 direct+深度內合約 indirect)不占 top_k;
    # 非固定按 R=0.6L+0.4G 排,過 max(min_score, 0.25×最高非固定分) 閾;姐妹去冗餘於顯示層。
    if ranked or incidents_only:
        query = (_payload.get("query") or "") if stdin_payload else ""
        results = []
        lane_raw = []   # 參考道原料(--incidents-only 不進 indirect 迴圈也要有定義)
        # 固定席:事故(kind=incident)恆固定
        for x in all_incidents:
            results.append({"node": x["node"], "kind": "incident", "pinned": True,
                            "score": 1.0, "matched_by": x.get("matched_by"),
                            "contract": x.get("contract")})
        gated = False   # 查詢品質閘觸發旗標(未觸發路徑必為 False,防 NameError)
        if not incidents_only:
            # query 品質閘(edit面查詢品質閘_計劃 S2):低資訊 query 視同空查詢——
            # 只覆寫 lex 用局部變數;事故探針 _delta_q 刻意不受閘(安全網寧多勿漏)
            if query and _impact_query_junk(query):
                query = ""
                gated = True
                print("(query 品質閘:文本為檔頭雜訊/過短,L 臂靜默)", file=sys.stderr)
            # 詞彙分:對 direct+indirect 候選跑 BM25F(query 為空則全 0)
            cand = [x["node"] for x in all_direct] + [x["node"] for x in all_indirect]
            lex = {}
            if query and cand:
                _mx = None
                raw = _rank_score_candidates(env, query, cand)
                _mx = max((s for _r, s, _h in raw), default=0.0)
                for _r, s, _h in raw:
                    lex[_r] = (s / _mx) if _mx > 0 else 0.0
            eff_depth = depth if depth is not None else 2
            _dbase = _impact_knob("LUMOS_IMPACT_DIRECT_BASE", 0.30)
            for x in all_direct:
                L = lex.get(x["node"], 0.0)
                pinned = bool(x.get("contract"))   # 含合約的 direct 固定
                results.append({"node": x["node"], "kind": "direct", "pinned": pinned,
                                "score": round(_dbase + (1.0 - _dbase) * L, 4), "L": round(L, 4),
                                "hit": x.get("hit"), "contract": x.get("contract")})
            _pin_hop = int(_impact_knob("LUMOS_IMPACT_PIN_HOP", 1))
            # ★pin-denoise-a-v4(2026-08-24,四輪設計審收斂)★:硬合約保送——knob=1 時 indirect 保送只認
            # INVARIANT/IRREVERSIBLE;RISK·* 類(樞紐筆記搭便車,held 噪音 58/96 的主力)降入「參考道」:
            # ★獨立容器 lane_raw,自始不進 results★(pinned:False 會被四處「非 pinned=free」分流吃回自由席、
            # 再被動態門檻砍出輸出——v3 r2 實測);JSON 用獨立頂層鍵 "lane"(決策 d2:沒學過 lane 的讀者
            # 結構性不受影響,diff 聚合/hook free 桶/守衛全免改)。
            # ★2026-08-24 考卷轉正預設 1(knob=0 留逃生)★:train LANE_N∈{2,3,5} 不敏感取 3;
            # 候選臂 held 噪音 82→39(-52%)、out_top3_must 0.083→0.367、must 兩棘輪零退、九關全過。
            _hard_pin = int(_impact_knob("LUMOS_IMPACT_HARD_PIN", 1))
            for x in all_indirect:
                L = lex.get(x["node"], 0.0)
                hop = x.get("hop", 2)
                contract = x.get("contract")
                # 合約固定席 hop 上限(v1.2 旋鈕):合約密集圖(Landmark 考卷實證)hop2 合約
                # 搭便車氾濫(51 席噪音)——收窄後 hop2 合約降入自由席按分數競爭(L≈0 者被閾殺)
                if contract and hop <= min(eff_depth, _pin_hop):
                    if _hard_pin and contract not in ("INVARIANT", "IRREVERSIBLE"):
                        # RISK·* 降參考道:score 用 indirect 自由席同款 R 公式(常數 0.70 全員同分,
                        # cap 挑誰會退化成字母序——v3 r3 s1f2);kind 保留 indirect(lane 是欄位不是 kind)
                        G = 0.60 * min(1.0, 2.0 / (2 ** hop))
                        lane_raw.append({"node": x["node"], "kind": "indirect", "pinned": False,
                                         "lane": "soft-guard", "score": round(0.60 * L + 0.40 * G, 4),
                                         "L": round(L, 4), "hop": hop, "contract": contract})
                        continue
                    results.append({"node": x["node"], "kind": "indirect", "pinned": True,
                                    "score": round(0.40 + 0.30, 4), "L": round(L, 4),
                                    "hop": hop, "contract": contract})
                    continue
                # hop≥2 需 L>底線(遠端節點要足夠詞彙證據背書)
                if hop >= 2 and L <= _impact_knob("LUMOS_IMPACT_LMIN_HOP2", 0.0):
                    continue
                G = 0.60 * min(1.0, 2.0 / (2 ** hop))
                R = round(0.60 * L + 0.40 * G, 4)
                results.append({"node": x["node"], "kind": "indirect", "pinned": False,
                                "score": R, "L": round(L, 4), "hop": hop, "contract": contract})
        # about_code 語意欄位(工具清單 #4):只標記、不動 pinned;--incidents-only 快速路徑整段跳過
        if not incidents_only:
            _impact_mark_about(env, results, rel_file)
        # 分固定/非固定;非固定過閾+排序+補到 top_k
        pins = [r for r in results if r["pinned"]]
        # 固定席內 stable sort:事故永遠最前(std-r1 s1f10),其次 about 命中者,其餘保持三軸原序
        pins.sort(key=lambda r: (r["kind"] != "incident", not r.get("about_hit", False)))
        free = [r for r in results if not r["pinned"]]
        max_free = max((r["score"] for r in free), default=0.0)
        thresh = max(float(min_score), _impact_knob("LUMOS_IMPACT_DYN_COEF", 0.65) * max_free)
        free = [r for r in free if r["score"] >= thresh]
        free.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))
        # 名額制(v1.1):單體檔洪水按排名剪尾——閾值管品質、名額管上限(gate 對齊 top_k+2=10);
        # 剪的是 11 名以後,不動前 8 的視野(精度/必看召回不受影響)
        # PPR 分量(檢索PPR邊權_計劃)已試已殺(2026-07-28 edit 卷 train 網格全負:
        # baseline nDCG@8 0.9831 vs ppr w0.2/0.4/0.6=0.9817/0.9668/0.9598,b1 純 PPR 與
        # b2 cochange 邊權同分=邊權零貢獻;free 池中位 3 席使 P@8 對重排零鑑別,裁決依 nDCG)。
        # 與 A3 同源教訓:本圖的圖傳播訊號打不過調校後的 BM25F 融合;勿憑直覺復活,
        # 重試須先過同款考卷。詳 Projects/檢索PPR邊權_計劃 墓碑節。
        _quota = int(_impact_knob("LUMOS_IMPACT_FREE_QUOTA", 10))
        truncated = max(0, len(free) - min(int(top), _quota))
        free = free[:min(int(top), _quota)]
        # R1 直連保底席(2026-08-07,plan:hook必看召回修復;第三桶明文):
        # 觸發=截斷後最終 free 集零 direct 且存在被閾砍/截的 direct(缺口)。
        # rescued 恆 pinned:false、threshold/quota 不作用其上、外掛於 free 之後(--top 例外,
        # 同 pins safety_overflow 精神);tie-break 沿 free.sort 慣例 (-score, hop, node)。
        # knob:LUMOS_IMPACT_RESCUE_N(2026-08-07 考卷轉正預設 1:held Σmust 12→14、
        # P@8 0.6389→0.6944 雙升,gate 兩條全過;knob=0 留 A 臂逃生)。
        # S2 水位謂詞(2026-08-07,plan:連結缺失補全):free 內 direct(排除 pinned;截斷後
        # 最終集)不足 N 席 → 補 need=max(0, N−count) 席(前案「僅零 direct 觸發」為 N=1 特例,
        # 向下相容;前案合約候選之改寫經考卷 A/B 重裁,互引留痕見兩計劃節點)。
        rescued = []
        # 2026-08-07 水位案考卷轉正 N=3(train 網格 {1,2,3} recall 軸選出;held 確認
        # Σmust 14→17、P@8 0.6944→0.7130 週閘翻綠;knob 留逃生)
        _rescue_n = int(_impact_knob("LUMOS_IMPACT_RESCUE_N", 3))
        _free_direct = sum(1 for r in free if r["kind"] == "direct")
        _need = max(0, _rescue_n - _free_direct)
        if _rescue_n > 0 and _need > 0:
            _free_ids = {id(r) for r in free}
            dropped = [r for r in results
                       if r["kind"] == "direct" and not r["pinned"] and id(r) not in _free_ids]
            dropped.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))
            for r in dropped[:_need]:
                rr = dict(r)
                rr["rescued"] = True
                rescued.append(rr)
        # 參考道:產生端 cap(三處輸出同一份,口徑合一——被 cap 砍的必看會誠實掉 must_in_out,棘輪有效)
        lane_items = []
        _lane_trunc = 0
        if lane_raw:
            lane_raw.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))   # 同 free/rescued 三鍵慣例
            _lane_n = max(0, int(_impact_knob("LUMOS_IMPACT_LANE_N", 3)))   # 負值防護(同 _rescue_n 的 max(0,…) 慣例;負切片語意是「砍尾」不是上限)
            lane_items = lane_raw[:_lane_n]
            _lane_trunc = len(lane_raw) - len(lane_items)
        # 姐妹去冗餘(顯示層,--json 全量不折)
        final = pins + free + rescued
        meta = {"candidates": len(all_direct) + len(all_indirect) + len(all_incidents),
                "pinned": len(pins), "truncated": truncated, "rescued": len(rescued),
                "safety_overflow": max(0, len(pins) - int(top))}
        if lane_raw:
            meta["lane"] = len(lane_items)
            meta["lane_truncated"] = _lane_trunc
        if as_json:
            out_obj = {"file": rel_file, "results": final, "meta": meta}
            if lane_items:   # 條件鍵(同 query_gated/stack_questions 慣例):knob=0 或空 → 鍵不存在
                out_obj["lane"] = lane_items
            if gated:
                out_obj["query_gated"] = True
            # 棧別效能追問(pitfalls棧別效能追問_計劃 T2):完整 ranked 模式(非 incidents-only
            # 冷卻快速路)且目標檔命中問題表 → 附該棧檢核問(全表);單源=_STACK_PERF_QUESTIONS,hook 只格式化
            if not incidents_only and not _PITFALL_DIFF_TEST_PAT.search(rel_file):
                _sk = _stack_key_for_file(rel_file, repo_root_for_lookup)   # .ts/.js 看 package.json 分前後端
                if _sk:
                    out_obj["stack_questions"] = {_sk: _STACK_PERF_QUESTIONS[_sk]}
                    # 觸發式適用性(表態閘 S3):hook 另送原始 delta_text(保留換行;query 那欄是 8000 字/512 詞截斷版,只給詞彙融合)
                    # → 只列命中 when 的題;沒送(legacy 呼叫)就沒有 applicable 鍵,hook 退回印全表。
                    _dt = _payload.get("delta_text") if stdin_payload else None
                    if isinstance(_dt, str):
                        _cfgq = _stack_questions_config(repo_root_for_lookup)
                        _app, _meta = _stack_applicability({_sk: _dt.splitlines()}, _cfgq["ask_all_over_lines"])
                        out_obj["stack_questions_applicable"] = _app
                        out_obj["stack_questions_meta"] = _meta
                        if _payload.get("delta_truncated"):
                            out_obj["delta_truncated"] = True
            print(json.dumps(out_obj, ensure_ascii=False))
        else:
            print(f"改動 {rel_file} — 相關 top(固定席 {len(pins)}):")
            for r in final:
                mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{r.get('hop','?')}"}.get(r["kind"], "")
                ct = f" ★{r['contract']}★" if r.get("contract") else ""
                pin = " [固定]" if r["pinned"] else ""
                print(f"  {r['score']:5.2f} {mk} {r['node']}{ct}{pin}")
            if meta["truncated"]:
                print(f"  (+{meta['truncated']} 條低分截斷;--json 全量)")
            if not lane_items and meta.get("lane_truncated"):
                print(f"  (守衛面參考 {meta['lane_truncated']} 條被 LANE_N cap 全部隱藏——網格消融才會發生)")
            if lane_items:
                print(f"守衛面參考(軟標記樞紐,未被本次改動直接證實相關,{len(lane_items)} 條):")
                for r in lane_items:
                    print(f"  {r.get('score', 0):5.2f} hop{r.get('hop', '?')} {r.get('node', '?')}  ({r.get('contract', '')})")
                if meta.get("lane_truncated"):
                    print(f"  (另有 {meta['lane_truncated']} 條守衛面參考未列出)")
            if meta["safety_overflow"]:
                print(f"  safety overflow: {meta['safety_overflow']}")
        return 0

    # 9. 輸出
    if as_json:
        print(json.dumps(
            {"file": rel_file, "direct": all_direct, "indirect": all_indirect,
             "incidents": all_incidents},
            ensure_ascii=False,
        ))
    else:
        # 人讀輸出
        print(f"改動 {rel_file} (由讀盤 refcheck 抽取)")
        print(f"── 直接關聯 ({len(all_direct)}) ──")
        for x in all_direct:
            contract_tag = f" ★{x['contract']}★" if x.get("contract") else ""
            combo_tag = "★COMBO★" if x.get("combo") else ""
            tags = (contract_tag + (" " + combo_tag if combo_tag else "")).rstrip()
            print(f"  {'⚠合約 ' if x.get('contract') else ''}{x['node']}{tags}  ({x['hit']})")
        print(f"── 間接關聯 ({len(all_indirect)}) ──")
        for x in all_indirect:
            cross = " [跨repo葉,不展開]" if x.get("cross_repo") else ""
            print(f"  hop{x['hop']}  {x['node']}  {x['direction']} ← via {x['via']} ← {x['from']}{cross}")
    if not isinstance(res, list) or any(not isinstance(r, dict) for r in res):
        return None
    sync = data.get("sync")
    if sync is not None and not (isinstance(sync, dict)
                                 and isinstance(sync.get("missing"), list)
                                 and isinstance(sync.get("touched_nodes"), list)):
        return None
    return data


def cmd_impact_diff(diff_range, repo=None, depth=None, top=8, min_score=0.20, as_json=False,
                    sync_check=False, sync_only=False, from_json=None):
    """code-loop 橋接:對整段 diff 的每支改動 code 檔跑 ranked impact(query=該檔 hunk 文字),
    聚合成「受影響功能面」manifest——固定席(合約/事故)全保、非固定取跨檔最高分 top-N。
    定位=審計員鏡頭(advisory,人判),非自動推播(hook 面 goldset 評測未過線,故不接 hook)。
    rc: 0=成功 / 2=git 失敗 / 3=vault 缺。

    from_json:吃一份已經算好的結果,不自己算(見 _impact_payload_read)。目前只支援
    搭 --sync-only 用——推送關卡算一次、同步點名與合約測試閘各讀一次。"""
    if from_json is not None:
        _pl = _impact_payload_read(from_json)
        if _pl is None or _pl.get("sync") is None:
            return 0          # 失敗隔離:維持同步點名現在的行為(靜默)
        _print_sync_nudge(_pl["sync"], _pl.get("range") or diff_range)
        return 0
    import json as _json
    import subprocess as _sp
    if diff_range == "staged":
        # 圖譜同步覆蓋(2026-08-22):pre-commit 要對「這次 commit 的內容」算波及,用 staged 代替 range
        diff_range = "--staged"
    elif diff_range.startswith("-"):
        # 同 pitfalls/cochange-check:'-' 開頭值會被 git 誤認成選項,查詢命令 rc2 拒收
        print("擋下:--diff 的值不能用 - 開頭(會被當成選項)", file=sys.stderr)
        return 2
    repo_root = Path(repo) if repo else None
    if repo_root is None:
        for cand in (Path.cwd(), *Path.cwd().parents):
            if (cand / ".git").exists():
                repo_root = cand
                break
    if repo_root is None or not (repo_root / ".git").exists():
        print("擋下:找不到 git 專案,用 --repo 指定", file=sys.stderr)
        return 2
    # core.quotePath=false:CJK 檔名不轉義加引號(否則 startswith/endswith 過濾全失效,r2 panel major)
    r = _sp.run(["git", "-C", str(repo_root), "-c", "core.quotePath=false",
                 "diff", "--name-only", diff_range], capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        print(f"擋下:git 算不出差異: {r.stderr.strip()[:200]}", file=sys.stderr)
        return 2
    files = []
    for f in r.stdout.splitlines():
        f = f.strip()
        if not _impact_diff_seed_ok(f):
            continue
        # 已刪檔不跳過:反查靠「節點 body 引用該路徑」而非檔案存在——
        # 刪除/改名正是合約節點最該被推到審計員眼前的時刻(r1 codex major)
        files.append(f)
    merged = {}          # node -> entry(跨檔取最高分;pinned 任一檔 pinned 即 pinned)
    per_file_meta = []
    import io, contextlib
    _vault = _vault_in(repo_root)
    # ★沒有圖譜就直接說,不要印「0 篇」裝作查過了★(2026-09-07 全 repo 審視 #9)
    #
    # 出身:這條路原本只在**逐檔迴圈裡**才發現沒圖譜——而「這個範圍 0 個檔」時迴圈根本不跑,
    # 於是一路走到最後印出「固定席 0 + top 0」並回成功。
    # ★對新手最危險的就是這個★:同一件事(找不到圖譜),另外兩種問法一個回 rc3、一個回 rc2
    # 並印白話擋下,只有這條印「0 篇」**看起來像查過了**——而它根本沒有圖譜可查。
    # 文件本來就寫著這條路會回「圖譜缺」,只是零檔時走不到。
    if _vault is None:
        return _no_vault_msg()
    _env_shared = Env(_vault)   # 建一次,逐檔復用(r1 N+1)
    for f in files:
        d = _sp.run(["git", "-C", str(repo_root), "-c", "core.quotePath=false",
                     "diff", diff_range, "--", f], capture_output=True, text=True, errors="replace")
        hunk = " ".join(l[1:].strip() for l in d.stdout.splitlines()
                        if l[:1] in "+-" and not l.startswith(("+++", "---")))[:4000]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cmd_impact(f, repo=str(repo_root), depth=depth, as_json=True,
                            ranked=True, top=top, min_score=min_score,
                            payload={"query": hunk, "prospective": {}},
                            preloaded=(_vault, _env_shared) if _env_shared is not None else None)
        if rc == 3:
            print("IMPACT-DEBUG: vault 找不到(rc3)", file=sys.stderr)
            return 3
        if rc != 0:
            continue
        try:
            data = _json.loads(buf.getvalue().strip().splitlines()[-1])
        except (ValueError, IndexError):
            continue
        _pm = {"file": f, **data.get("meta", {})}
        if data.get("query_gated"):
            _pm["query_gated"] = True   # 觀測欄聚合轉發(r1 f5:code-loop 鏡頭可見)
        per_file_meta.append(_pm)
        for x in data.get("results", []):
            cur = merged.get(x["node"])
            if cur is None:
                merged[x["node"]] = {**x, "files": [f]}
            else:
                if f not in cur["files"]:
                    cur["files"].append(f)
                pinned = cur["pinned"] or x.get("pinned", False)
                if x["score"] > cur["score"]:
                    # 整項以勝出結果重建(避免 hop/L 舊值殘留成幽靈欄位,r1 s4 minor)
                    merged[x["node"]] = {**x, "files": cur["files"], "pinned": pinned}
                else:
                    cur["pinned"] = pinned
    pins = sorted([v for v in merged.values() if v["pinned"]],
                  key=lambda v: (-v["score"], v["node"]))
    free = sorted([v for v in merged.values() if not v["pinned"]],
                  key=lambda v: (-v["score"], v["node"]))[:int(top)]
    # 落成位置閉環(sync-check):預期受影響節點 ∩ 分支實際動過的圖譜節點——
    # 「這功能被改了,它的節點卻沒動」= 受影響未同步清單(advisory,人判;固定席可信度高、自由席≈P@8 .70)
    sync = None
    if sync_check:
        _vault_name = _vault.name if _vault is not None else None
        touched = set()
        if _vault_name:
            _prefix = f"docs/{_vault_name}/"
            for f2 in r.stdout.splitlines():
                f2 = f2.strip().strip('"')
                if f2.startswith(_prefix) and f2.endswith(".md"):
                    touched.add(f2[len(_prefix):])
        missing = [v for v in (pins + free) if v["node"] not in touched]
        sync = {"touched_nodes": sorted(touched),
                "missing": [{"node": v["node"], "pinned": v["pinned"],
                             "score": v["score"], "files": v["files"]} for v in missing]}
    if as_json:
        print(_json.dumps({"range": diff_range, "files": files,
                           "results": pins + free,
                           **({"sync": sync} if sync is not None else {}),
                           "meta": {"files": len(files), "pinned": len(pins),
                                    "free_kept": len(free),
                                    "free_total": sum(1 for v in merged.values() if not v["pinned"]),
                                    "per_file": per_file_meta}}, ensure_ascii=False))
        return 0
    if sync_only and sync is not None:
        _print_sync_nudge(sync, diff_range)
        return 0
    print(f"受影響功能面({diff_range};{len(files)} 檔;固定席 {len(pins)}+top {len(free)}——審計鏡頭,人判):")
    for v in pins + free:
        mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{v.get('hop','?')}"}.get(v["kind"], "")
        ct = f" ★{v['contract']}★" if v.get("contract") else ""
        pin = " [固定]" if v["pinned"] else ""
        print(f"  {v['score']:5.2f} {mk} {v['node']}{ct}{pin}  ←{','.join(v['files'][:3])}")
    if not merged:
        print("  (無節點引用這些檔——圖譜對此 diff 無覆蓋)")
    if sync is not None:
        _print_sync_nudge(sync, diff_range)
    return 0


def _print_sync_nudge(sync, diff_range, cap=8):
    """落成核對的唯一呈現(2026-08-22 架構對齊席抓到三套並存後收斂成這一份):
    固定席(合約/事故/直接相依)優先、最多 cap 篇;hooks(pre-commit/pre-push/Stop)只呼叫,不自己重排。"""
    miss = sorted(sync["missing"], key=lambda m: (not m["pinned"], -m.get("score", 0)))
    print(f"\n落成核對(這批動過 {len(sync['touched_nodes'])} 篇筆記):")
    if not miss:
        print("  ✓ 預期受影響的筆記全數已同步")
        return
    pinned = [m for m in miss if m["pinned"]]
    print(f"  提醒:下面這些筆記跟改到的程式碼直接相關(合約 / 事故 / 直接相依),這批沒動:" if pinned
          else "  提醒:下面這些筆記可能受影響,這批沒動(自由席,可信度較低,人判):")
    for v in miss[:cap]:
        mark = "⚠必看" if v["pinned"] else "  "
        print(f"  {mark} {v['node']}  ←{','.join(v['files'][:2])}")
    if len(miss) > cap:
        print(f"  … 還有 {len(miss) - cap} 篇(lumos impact --diff {diff_range} --sync-check --json 看全部)")
    print("  確定不受影響就略過;受影響的現在補。這裡只提醒不擋。")


# ── code-loop 留痕(Task 1) ────────────────────────────────────────────────────

def _codeloop_git_branch(repo_root):
    """取 HEAD branch 名(detached HEAD 回 HEAD)。"""
    import subprocess
    r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                       capture_output=True, text=True, errors="replace", cwd=str(repo_root))
    return r.stdout.strip() or "HEAD"


# ---------------------------------------------------------------------------
# dispatch-lens(Projects/派工鏡頭注入_計劃,2026-09-03):代碼審派工詞的固定席鏡頭
# hook 是薄殼(scripts/hooks/claude/dispatch-lens-hook.py),所有 git/合約/圖譜判斷都在這裡,
# 沿用既有 helper(_git_commit_exists / INVARIANT_RE 家族 / _vault_in 的排序規則)。
# 消毒原則(r2/r3 載荷席):來自圖譜或 diff 的自由文字零輸出——只印固定字彙、base 已追蹤路徑、
# base 版合約行(KEY: 行)。清單本身仍用工作樹圖譜算(d3:能藏不能說)。
# rc:0=成功(含 0 篇,text 空)/2=輸入或 git 壞/3=vault 缺/4=base 不在主線
# ---------------------------------------------------------------------------
_LENS_HEADER = "lumos 自動附加:本次改動的固定席節點(來源 impact --diff,只供參考)"
_LENS_SHA_RE = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")
_LENS_KIND = {"direct": "直接相依", "indirect": "間接相依", "incident": "事故"}


def _lens_range_ok(diff_range):
    """恰好一個 `..`、兩端非空、不含 `...`、不以 - 開頭(r3 極端輸入席收緊)。"""
    if not isinstance(diff_range, str) or diff_range.startswith("-") or "..." in diff_range:
        return None
    parts = diff_range.split("..")
    if len(parts) != 2 or not parts[0] or not parts[1]:

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/lumos | sed -n '17870,18030p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
 17870	        return None
 17871	    return {nfc(x) for x in _nodehome_split_z(raw)}
 17872	
 17873	
 17874	def _nodehome_reader(repo_root, where):
 17875	    """回 read(path)->bytes|None。讀的是 where 那個版本:跟磁碟一樣的直接讀磁碟,不一樣的用 git show 讀
 17876	    ([S38]:提交前只讀提交索引——同一個工作目錄另一個會談寫到一半、還沒加進索引的東西讀不到)。"""
 17877	    if where is None:
 17878	        return lambda p: None
 17879	    disk_ok_all = False
 17880	    differ = None
 17881	    if where == "index":
 17882	        differ = _nodehome_changed_vs_disk(repo_root, "index")
 17883	    else:
 17884	        head = _lens_full_sha(repo_root, "HEAD")
 17885	        if head and head == where:
 17886	            differ = _nodehome_changed_vs_disk(repo_root, where)
 17887	    root = Path(repo_root)
 17888	    spec = "" if where == "index" else where
 17889	
 17890	    def read(p):
 17891	        if differ is not None and p not in differ:
 17892	            fp = root / p
 17893	            try:
 17894	                if fp.is_file() and not fp.is_symlink():
 17895	                    return fp.read_bytes()
 17896	            except OSError:
 17897	                pass
 17898	        r = _lens_git(repo_root, "show", f"{spec}:{p}", binary=True)
 17899	        if r is None or r.returncode != 0:
 17900	            return None
 17901	        return r.stdout
 17902	    return read
 17903	
 17904	
 17905	def _nodehome_parse_note(raw):
 17906	    """節點原文 → {type, status, about[], resp, sig, text}。sig=(摘要, 解析後的決策, 正文)——[S12] 內容有變
 17907	    逐欄比對用;★不沿用只算正文的那支雜湊★:摘要與決策都在開頭欄位裡,節點長大主要就長在摘要。"""
 17908	    text = raw.decode("utf-8-sig", errors="replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
 17909	    fm_lines, body = split_frontmatter(text)
 17910	    fields = {}
 17911	    dec = ""
 17912	    if fm_lines is not None:
 17913	        fields, _bk, _lint = parse_frontmatter(fm_lines)
 17914	        # 決策比「解析後的值」:只把 content: a 改成 content: "a" 這種等價寫法不算內容有變(第二輪外家席)
 17915	        try:
 17916	            dec = json.dumps(parse_decisions(fm_lines), ensure_ascii=False, sort_keys=True)
 17917	        except Exception:
 17918	            dec = "\n".join(l.rstrip() for l in fm_lines if l.startswith(("decisions:", "  ")))
 17919	    summ = fields.get("summary")
 17920	    summ = summ if isinstance(summ, str) else ""
 17921	    return {"type": str(fields.get("type", "")).strip(),
 17922	            "status": str(fields.get("status", "")).strip(),
 17923	            "about": [str(x) for x in as_list(fields.get("about_code")) if str(x).strip()],
 17924	            "resp": fields.get("responsibility") if isinstance(fields.get("responsibility"), str) else None,
 17925	            "sig": ("\n".join(l.rstrip() for l in summ.splitlines()).strip(), dec,
 17926	                    "\n".join(l.rstrip() for l in body.splitlines()).strip()),
 17927	            "text": text}
 17928	
 17929	
 17930	def _nodehome_side(repo_root, where, vault_rel, share=None, changed=None):
 17931	    """[S38] 建一邊的快照。share=另一邊已建好的快照、changed=兩邊之間有變動的路徑:沒變動的節點直接用 share 的解析結果
 17932	    (推送前的起點那一側只讀這段範圍裡有變動的節點——不然每一篇都要 git show 一次,65 篇就要 2 秒以上)。"""
 17933	    lst = _nodehome_list(repo_root, where)
 17934	    if lst is None:
 17935	        return None
 17936	    s = _NodehomeSide()
 17937	    s.files, s.all_paths = lst
 17938	    s.where = where
 17939	    s._reader = _nodehome_reader(repo_root, where)
 17940	    s.shebang = {}
 17941	    s.share = share
 17942	    s.changed = set(changed or ())
 17943	    s.notes = {}
 17944	    pre = vault_rel + "/Systems/"
 17945	    for p in s.files:
 17946	        if p.startswith(pre) and p.endswith(".md"):
 17947	            rel = p[len(vault_rel) + 1:]
 17948	            if share is not None and p not in s.changed and rel in share.notes:
 17949	                s.notes[rel] = share.notes[rel]
 17950	                continue
 17951	            raw = s._reader(p)
 17952	            if raw is not None:
 17953	                s.notes[rel] = _nodehome_parse_note(raw)
 17954	    return s
 17955	
 17956	
 17957	def _nodehome_required(repo_root, side, cfg, vendored_skip):
 17958	    """[S1] 需要家的檔集合,另回檔名不是 UTF-8 的程式檔(永遠寫不進圖譜,只提醒改名或排除)。"""
 17959	    import fnmatch
 17960	    req, bad_names = set(), set()
 17961	    for p in side.files:
 17962	        kind = _nodehome_code_kind(p)
 17963	        if kind is None:
 17964	            continue
 17965	        if any(fnmatch.fnmatch(p, g) for g in _NODEHOME_EXCLUDE_GLOBS):
 17966	            continue
 17967	        if p in vendored_skip or _cochange_excluded(p, cfg["ignore"]) or _nodehome_is_test(p):
 17968	            continue
 17969	        if kind == "shebang?":
 17970	            if p in side.shebang:
 17971	                ok = side.shebang[p]
 17972	            elif side.share is not None and p not in side.changed and p in side.share.shebang:
 17973	                ok = side.shebang[p] = side.share.shebang[p]
 17974	            else:
 17975	                head = side._reader(p)
 17976	                ok = side.shebang[p] = bool(head) and head[:200].split(b"\n", 1)[0].startswith(b"#!")
 17977	            if not ok:
 17978	                continue
 17979	        try:
 17980	            p.encode("utf-8")
 17981	        except UnicodeEncodeError:
 17982	            bad_names.add(p)
 17983	            continue
 17984	        req.add(p)
 17985	    return req, bad_names
 17986	
 17987	
 17988	def _nodehome_key(value):
 17989	    """about_code 一項的比對鍵(字面):路徑正規化+NFC。★不讀磁碟★——比對的是被檢查那個版本裡的樣子,
 17990	    推送一個不是目前 checkout 的分支時,磁碟上的拼法跟那個提交對不上(第二輪邊界席實跑重現的誤擋)。
 17991	    about_code 寫入時已經照磁碟校正過(解連結、大小寫、Unicode 寫法;_about_code_path),所以字面比就夠。"""
 17992	    return nfc(_posix_norm(strip_quotes(str(value).strip())))
 17993	
 17994	
 17995	def _nodehome_homes(repo_root, side):
 17996	    """[S2] {檔: [家那幾篇]}。只看 about_code 欄位值、不看預標指紋有沒有過期(指紋在每次寫回都會過期)。
 17997	    回 (homes, 每篇自己的檔集合)。"""
 17998	    homes, own = {}, {}
 17999	    for rel, n in side.notes.items():
 18000	        keys = {k for k in (_nodehome_key(v) for v in n["about"]) if k}
 18001	        own[rel] = keys
 18002	        if n["type"] != "system" or n["status"] not in _NODEHOME_HOME_STATUSES:
 18003	            continue
 18004	        for k in keys:
 18005	            homes.setdefault(k, []).append(rel)
 18006	    return homes, own
 18007	
 18008	
 18009	def _nodehome_refs(text, side, req):
 18010	    """[S7][S8] 這篇用反引號寫到哪幾支需要家的檔:抽取跟改檔前推筆記同一支(完整路徑+在受版控檔裡唯一的裸檔名)。
 18011	    裸檔名不唯一時推筆記那支不認它,這裡也不認——不構成「別人檔的入口」,就不算認領。"""
 18012	    top_dirs = {p.split("/", 1)[0] for p in side.all_paths if "/" in p and not p.startswith(".")}
 18013	    full, bare = _node_code_ref_tokens(text, top_dirs)
 18014	    refs = {nfc(t) for t, _l in full if nfc(t) in req}
 18015	    if int(_impact_knob("LUMOS_IMPACT_BASENAME_MATCH", 1)):
 18016	        counts, where = {}, {}
 18017	        for p in side.all_paths:
 18018	            b = p.rsplit("/", 1)[-1]
 18019	            counts[b] = counts.get(b, 0) + 1
 18020	            where[b] = p
 18021	        for b in bare:
 18022	            if counts.get(b) == 1 and where[b] in req:
 18023	                refs.add(where[b])
 18024	    return refs
 18025	
 18026	
 18027	def _nodehome_changes(repo_root, base, tip):
 18028	    """[(狀態字母, 舊路徑, 新路徑)];改名的新路徑算新增 [S31]。base=None 且 tip='index' → 看暫存區。
 18029	    ★只帶 -M、沒帶 -C★:複製出來的檔 git 標成 A,照樣算新增(使用者設了 diff.renames=copies 也一樣,-M 蓋過它);
 18030	    下面認 C 那半只是防呆,這條呼叫實際收不到 C(代碼審 r1 正確性席)。"""

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/lumos | sed -n '20945,21070p'
nl -ba scripts/lumos | sed -n '21240,21310p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
 20945	                elif line.strip() and cur and line.startswith(prefix):
 20946	                    rel = line[len(prefix):]
 20947	                    if rel not in out:          # log 是新→舊,第一次看到就是最新
 20948	                        out[rel] = cur
 20949	    except (OSError, subprocess.SubprocessError):
 20950	        out = {}
 20951	    _GIT_DATES_CACHE[key] = out
 20952	    return out
 20953	
 20954	
 20955	_BASENAME_COUNTS_CACHE = {}   # repo_root → {basename: count}(行程內;--diff 多檔免重跑 ls-files)
 20956	
 20957	
 20958	def _impact_reverse_lookup(rel_code_path, env, repo_root):
 20959	    """給一支 code 路徑,反查「哪些圖譜節點的 body inline-code 引用了它」。
 20960	
 20961	    設計要點(Task 2):
 20962	    - 只掃 body inline-code,絕不掃 core_refs(r7-F2)。
 20963	    - 複用 _refcheck_scan(text, repo_root) 抽取 body inline-code 路徑;
 20964	      Note 不存 body → 重讀盤每個 .md 餵它(r1-F1)。
 20965	    - 路徑規範化(r3-F5):輸入若為絕對路徑先轉 repo-relative 再比對。
 20966	    - _refcheck_scan 的 top_dirs 靜默過濾照舊(§4 天花板 5)。
 20967	
 20968	    回傳: list[(node_rel, hit)] — hit ∈ "body-inline-code"(完整路徑命中)|
 20969	    "basename-match"(裸檔名容錯,R2 2026-08-07,plan:hook必看召回修復)。
 20970	    同節點兩路皆中時完整路徑優先(單節點單筆,provenance 合併序明文)。
 20971	
 20972	    R2 裸檔名容錯:inline-code 中不含 `/` 的裸 token == 目標檔 basename,且該
 20973	    basename 在 `git ls-files` 母體內唯一(tracked-only:untracked/ignored 混入會把
 20974	    唯一誤判歧義;大小寫敏感)→ 命中。★不動共用的 _refcheck_scan★(其 `/` 過濾
 20975	    是 refcheck CLI/G1 gate 的既有合約,此處自建第二條抽取路)。git 缺席/重名
 20976	    → degrade 為不比對(裸檔名路靜默停用,完整路徑路不受影響)。
 20977	    knob:LUMOS_IMPACT_BASENAME_MATCH(2026-08-07 轉正預設 1;0=逃生/A 臂)。ls-files 結果以 repo_root 為鍵行程內快取(--diff 多檔不重跑子行程)。
 20978	    """
 20979	    import os
 20980	    import subprocess
 20981	
 20982	    repo_root = Path(repo_root)
 20983	
 20984	    # 路徑規範化:絕對路徑 → repo-relative
 20985	    rp = str(rel_code_path)
 20986	    if os.path.isabs(rp):
 20987	        rp = os.path.relpath(rp, str(repo_root))
 20988	
 20989	    # R2:裸檔名比對的前置——目標檔 basename 在 tracked 母體唯一才啟用
 20990	    base_ok = False
 20991	    base = Path(rp).name
 20992	    if int(_impact_knob("LUMOS_IMPACT_BASENAME_MATCH", 1)):   # 2026-08-07 考卷轉正預設 1(knob=0 留逃生)
 20993	        key = str(repo_root)
 20994	        counts = _BASENAME_COUNTS_CACHE.get(key)
 20995	        if counts is None:
 20996	            counts = {}
 20997	            try:
 20998	                r = subprocess.run(["git", "-C", str(repo_root), "ls-files"],
 20999	                                   capture_output=True, text=True, errors="replace", timeout=10)
 21000	                if r.returncode == 0:
 21001	                    for ln in r.stdout.splitlines():
 21002	                        if ln.strip():
 21003	                            b = Path(ln).name
 21004	                            counts[b] = counts.get(b, 0) + 1
 21005	            except (OSError, subprocess.SubprocessError):
 21006	                counts = {}   # git 缺席=degrade(空表=永不唯一)
 21007	            _BASENAME_COUNTS_CACHE[key] = counts
 21008	        base_ok = counts.get(base, 0) == 1
 21009	
 21010	    hits = []
 21011	    for node_rel, note in env.notes.items():
 21012	        # 重讀盤:Note 不存 body,直接讀原始 .md 文字
 21013	        md_path = env.vault / node_rel
 21014	        try:
 21015	            text = md_path.read_text(encoding="utf-8-sig", errors="replace")
 21016	        except OSError:
 21017	            continue
 21018	        claims, _n_missing, _n_oor, _n_ok = _refcheck_scan(text, repo_root)
 21019	        hit = None
 21020	        for claim in claims:
 21021	            if claim["token"] == rp:
 21022	                hit = "body-inline-code"   # 完整路徑優先
 21023	                break
 21024	        if hit is None and base_ok:
 21025	            # 第二條抽取路:裸 token(無 /)——與 _refcheck_scan 同一支抽取(_node_code_ref_tokens)
 21026	            if base in _node_code_ref_tokens(text, set())[1]:
 21027	                hit = "basename-match"
 21028	        if hit:
 21029	            hits.append((node_rel, hit))   # 同一節點只算一次
 21030	    return hits
 21031	
 21032	
 21033	def _impact_contract(note):
 21034	    """Task 3: 偵測節點的合約標記,回傳 (contract: str|None, combo: bool)。
 21035	
 21036	    兩軸設計(r6-F3):
 21037	    - INVARIANT/DEBT 軸: extract_contracts(note) → inv list。DEBT → None(r9-F7)。
 21038	    - IRREVERSIBLE 軸: 獨立 IRREVERSIBLE_RE 掃 summary(extract_contracts 不含此)。
 21039	    取最高: IRREVERSIBLE > INVARIANT > None。
 21040	    combo(r6-F6): ★COMBO★ 是 ★INVARIANT★ 同行後綴修飾,偵測 INVARIANT 行含 ★COMBO★
 21041	                 (參 scripts/lumos:725 的 '★COMBO★' not in inv);不入 contract enum,走獨立布林。
 21042	    """
 21043	    invs, _debts = extract_contracts(note)  # 只掃 INVARIANT/DEBT
 21044	
 21045	    # combo: 任一 INVARIANT 行含 ★COMBO★ 即為 True
 21046	    combo = any("★COMBO★" in inv for inv in invs)
 21047	
 21048	    # INVARIANT 軸: 有 inv 則 contract="INVARIANT"(DEBT 已被 extract_contracts 分到 _debts,不入此路)
 21049	    contract = "INVARIANT" if invs else None
 21050	
 21051	    # IRREVERSIBLE 軸: 獨立掃 summary(extract_contracts 不含 IRREVERSIBLE)
 21052	    summ = note.fields.get("summary")
 21053	    if isinstance(summ, str):
 21054	        for line in summ.split("\n"):
 21055	            if IRREVERSIBLE_RE.match(line.strip()):
 21056	                contract = "IRREVERSIBLE"  # 最高優先,覆蓋 INVARIANT
 21057	                break
 21058	
 21059	    # RISK 軸(2026-08-05 標籤結構優化):risk/ 標節點保送固定席——light 硬否決的
 21060	    # honor-system(「碰金流/對外/不可逆/守衛面就不給 light」靠自核)有了機械眼線。
 21061	    # 軸序最低:合約標記存在時仍以合約身分出席。
 21062	    if contract is None:
 21063	        for tg in (note.fields.get("tags") or []):
 21064	            if isinstance(tg, str) and tg.startswith("risk/"):
 21065	                contract = "RISK·" + tg.split("/", 1)[1]
 21066	                break
 21067	
 21068	    return contract, combo
 21069	
 21070	
 21240	            "via": via,
 21241	            "direction": direction,
 21242	            "from": from_node,
 21243	            "contract": bfs_contract,
 21244	            "combo": bfs_combo,
 21245	        })
 21246	
 21247	    return {"direct": direct_list, "indirect": indirect_list}
 21248	
 21249	
 21250	_ABOUT_COUNTS_CACHE = {}   # str(vault) → {repo 相對路徑: 幾篇 about_code 命中它}(行程內;--diff 多檔共用 env 免重掃)
 21251	
 21252	
 21253	def _impact_about_counts(env):
 21254	    """★巨檔門檻的材料:全掃 env.notes 的 about_code 建 {檔: 節點數}★(工具清單 #4;獨立頂層函式對齊 _impact_* 分工)。
 21255	    快取鍵用路徑字串(既有 _BASENAME_COUNTS_CACHE/_GIT_DATES_CACHE 同款;id(env) 是全庫沒先例的第二種做法)。"""
 21256	    key = str(env.vault)
 21257	    if key in _ABOUT_COUNTS_CACHE:
 21258	        return _ABOUT_COUNTS_CACHE[key]
 21259	    counts = {}
 21260	    for n in env.notes.values():
 21261	        for f in as_list(n.fields.get("about_code")):
 21262	            f = _posix_norm(f)
 21263	            if f:
 21264	                counts[f] = counts.get(f, 0) + 1
 21265	    _ABOUT_COUNTS_CACHE[key] = counts
 21266	    return counts
 21267	
 21268	
 21269	def _impact_mark_about(env, results, rel_file):
 21270	    """★about_code 只加分不降級★:對已進候選集的 results 項,about_code 含目標檔且 stamp 未過期 → 加 `about_hit: True`
 21271	    (只在 True 時出鍵;★不覆寫既有 hit 欄★;不改任何 pinned 判定——about 不是第四條入口)。
 21272	    總開關 LUMOS_IMPACT_ABOUT(預設 1;0=整段不跑、不讀正文);巨檔門檻 LUMOS_IMPACT_ABOUT_MAX(預設 8):
 21273	    目標檔被 ≥N 篇 about 命中時關閉加分(巨檔上「關於」無鑑別力,held 實證 22 誤放)。
 21274	    懶觸發:先查欄位,命中才讀該篇正文算雜湊(無 git、無子行程)。計劃:Projects/固定席扇出降權_計劃。"""
 21275	    if int(_impact_knob("LUMOS_IMPACT_ABOUT", 1)) == 0:
 21276	        return
 21277	    _norm = _posix_norm   # 跟寫入側同一個路徑正規化(r3 整合席:原本只剝開頭的 ./,不解 ..)
 21278	    target = _norm(rel_file)
 21279	    counts = _impact_about_counts(env)
 21280	    if counts.get(target, 0) >= int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8)):
 21281	        return
 21282	    for r in results:
 21283	        n = env.notes.get(r["node"])
 21284	        if n is None:
 21285	            continue
 21286	        vals = [_norm(x) for x in as_list(n.fields.get("about_code"))]
 21287	        if target not in vals:
 21288	            continue
 21289	        expired, _nh, _sh = about_code_expired(env.vault, r["node"], n.fields.get("about_code_stamp"))
 21290	        if expired:
 21291	            continue
 21292	        r["about_hit"] = True
 21293	
 21294	
 21295	def _impact_knob(name, default):
 21296	    """hook 面調參旋鈕:預設=凍結常數;LUMOS_IMPACT_* env 僅供 goldset 網格消融,非使用者旗標。"""
 21297	    try:
 21298	        return float(os.environ.get(name, default))
 21299	    except ValueError:
 21300	        return default
 21301	
 21302	def _impact_query_junk(query):
 21303	    """query 品質閘判準(edit面查詢品質閘_計劃 S1;落地後發現收窄版):
 21304	    剝 shebang 首行後,壓縮全部空白的殘餘 < MINLEN → junk(視同空查詢,L 臂靜默)。
 21305	    ★MINLEN 預設 1=「僅 shebang/空白」才算垃圾★——原 20 字低資訊假說被 held 反證
 21306	    (E15 的 17 字真代碼行有訊息:其 L 分撐高動態門檻殺 hop1 噪音,閘掉反湧回,
 21307	    0.67→0.38 倒退;shebang 案 E05/E14 的收益不靠長度分支)。旋鈕留給網格消融。
 21308	    非 str 防呆回 False;MINLEN<=0/NaN/Inf=整閘停用(旋鈕語意連續)。"""
 21309	    if not isinstance(query, str):
 21310	        return False

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/lumos | sed -n '21390,21720p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
 21390	    except Exception:
 21391	        return dict(_DEFAULTS)
 21392	
 21393	
 21394	def cmd_impact(file, repo=None, depth=None, as_json=False,
 21395	               ranked=False, top=8, min_score=0.20, stdin_payload=False, incidents_only=False,
 21396	               payload=None, preloaded=None):
 21397	    """動手前算出哪些知識圖譜節點會被 code 改動波及。
 21398	    rc 協定: 0=成功(有/無影響集都算) / 3=vault 找不到 / 其他非 0=內部錯。
 21399	    Task 7: 排序 + --json schema + 人讀輸出。
 21400	    """
 21401	    import json
 21402	
 21403	    # 1. 解析 repo root
 21404	    if repo is not None:
 21405	        repo_root = Path(repo)
 21406	        if not repo_root.is_dir():
 21407	            print(f"擋下:--repo 指的不是目錄: {repo}", file=sys.stderr)
 21408	            return 2
 21409	    else:
 21410	        repo_root = None
 21411	        for cand in (Path.cwd(), *Path.cwd().parents):
 21412	            if (cand / ".git").exists():
 21413	                repo_root = cand
 21414	                break
 21415	
 21416	    # 2. 找 vault(rc 3 = vault 找不到)
 21417	    if repo_root is not None:
 21418	        vault = _vault_in(repo_root)
 21419	    else:
 21420	        vault = find_vault(Path.cwd())
 21421	    if vault is None:
 21422	        # ★三條路同一套說法★(2026-09-07 全 repo 審視 #9):同一件事(找不到圖譜)
 21423	        # 原本三種問法給三種答案——這條印一句除錯訊息、--node 印白話擋下、--diff 回成功印 0 篇。
 21424	        return _no_vault_msg()
 21425	
 21426	    # 3. 解析 depth:CLI(顯式 --depth) > .lumos/impact.json config > 預設 2
 21427	    _cfg_root = repo_root if repo_root is not None else vault.parent.parent
 21428	    _impact_cfg = _impact_load_config(_cfg_root)
 21429	    if depth is None:
 21430	        depth = _impact_cfg["depth"]
 21431	
 21432	    # 4. 載入圖譜環境(preloaded=(vault,env) 由 --diff 聚合復用,避免逐檔重建 N+1)
 21433	    if preloaded is not None and preloaded[0] == vault:
 21434	        env = preloaded[1]
 21435	    else:
 21436	        env = Env(vault)
 21437	    repo_root_for_lookup = repo_root if repo_root is not None else vault.parent.parent
 21438	
 21439	    # 5. code → node 反查(只認 body inline-code,r7-F2)
 21440	    # incidents_only 真快速路(r1 終審親驗修正:原實作僅「不顯示」,反查/BFS 照跑——宣稱落空):
 21441	    # 事故比對只需 rel_file+內容,不需 direct/BFS → 整段跳過,冷卻窗成本回到近零。
 21442	    if incidents_only:
 21443	        direct_pairs = []
 21444	    else:
 21445	        direct_pairs = _impact_reverse_lookup(file, env, repo_root_for_lookup)
 21446	    direct_rels = [n for n, _h in direct_pairs]
 21447	    direct_hit = dict(direct_pairs)   # node → body-inline-code|basename-match(R2 provenance)
 21448	
 21449	    # 6. 組裝影響清單:single multi-source BFS 保證 hop = 距最近直接節點的 min 距離(I1)。
 21450	    #
 21451	    # 舊做法(per-node loop)問題:各直接節點各跑一次 BFS → first-wins 去重 → 若節點 N
 21452	    # 從 D1 hop=2、從 D2 hop=1,但 D1 先迭代,N 以 hop=2 進 indirect_seen → D2 的 hop=1
 21453	    # 被跳過,違反設計 §2 indirect.hop=距最近直接節點。
 21454	    #
 21455	    # 新做法:
 21456	    #   ① direct 資料:逐一收(hit/contract/combo 是 per-node 屬性)。
 21457	    #   ② core_refs 葉:逐一從各直接節點抽(也是 per-node 屬性,hop=1 固定)。
 21458	    #   ③ BFS 間接:single multi-source BFS(全部直接節點一起當種子)→ hop 自然是 min。
 21459	    #
 21460	    # 直接節點預種 direct_seen 確保:BFS 不把另一直接節點誤加進 indirect。
 21461	    all_direct = []
 21462	    all_indirect = []
 21463	    direct_seen = set(direct_rels)  # ← 預種全量,BFS seen 初始集 + dedup guard
 21464	    indirect_seen = set()  # 去重:core_refs 葉 + BFS 間接
 21465	    processed_direct = set()  # 避免同一 direct 重複展開 direct/core_refs
 21466	
 21467	    # ① 直接節點資料 + ② core_refs 葉(per-node,保留原 _impact_collect 語意)
 21468	    # (incidents_only 時 direct_rels 為空,以下兩段自然零工作——BFS multi-source 種子空集即不擴散)
 21469	    for d_rel in direct_rels:
 21470	        if d_rel in processed_direct:
 21471	            continue
 21472	        processed_direct.add(d_rel)
 21473	        direct_note = env.notes.get(d_rel)
 21474	        contract, combo = _impact_contract(direct_note) if direct_note else (None, False)
 21475	        all_direct.append({"node": d_rel, "hit": direct_hit.get(d_rel, "body-inline-code"),
 21476	                           "contract": contract, "combo": combo})
 21477	        # core_refs 跨 repo 葉(r7-F2):hop=1 固定,不入 BFS
 21478	        if direct_note is not None:
 21479	            for core_ref in as_list(direct_note.fields.get("core_refs")):
 21480	                if core_ref not in direct_seen and core_ref not in indirect_seen:
 21481	                    indirect_seen.add(core_ref)
 21482	                    all_indirect.append({
 21483	                        "node": core_ref, "hop": 1, "via": "core_refs",
 21484	                        "direction": "outlink", "from": d_rel,
 21485	                        "cross_repo": True, "no_expand": True,
 21486	                        "contract": None, "combo": False,
 21487	                    })
 21488	
 21489	    # ③ 單次 multi-source BFS:全部直接節點為種子,hop = min 距離
 21490	    unique_direct_rels = list(processed_direct)
 21491	    bfs_results = _impact_bfs(unique_direct_rels, env, depth=depth)
 21492	    for (node, hop, from_node, is_backlink) in bfs_results:
 21493	        if node in direct_seen or node in indirect_seen:
 21494	            continue
 21495	        indirect_seen.add(node)
 21496	        bfs_note = env.notes.get(node)
 21497	        bfs_contract, bfs_combo = _impact_contract(bfs_note) if bfs_note else (None, False)
 21498	        via = _impact_via(from_node, node, is_backlink, env)
 21499	        direction = "backlink" if is_backlink else "outlink"
 21500	        all_indirect.append({
 21501	            "node": node, "hop": hop, "via": via, "direction": direction,
 21502	            "from": from_node, "contract": bfs_contract, "combo": bfs_combo,
 21503	        })
 21504	
 21505	    # 6. 排序(§2.4):合約節點優先 → 直接優先於間接(已分層) → 同層 hop 升序
 21506	    # 合約優先權:IRREVERSIBLE=2, INVARIANT=1, None=0
 21507	    def contract_priority(contract):
 21508	        if contract == "IRREVERSIBLE":
 21509	            return 2
 21510	        if contract == "INVARIANT":
 21511	            return 1
 21512	        return 0
 21513	
 21514	    all_direct.sort(key=lambda x: -contract_priority(x.get("contract")))
 21515	    all_indirect.sort(key=lambda x: (x.get("hop", 999), -contract_priority(x.get("contract"))))
 21516	
 21517	    # 7. 路徑規範化(用於輸出 + _match_incident_triggers 的 file_rel)
 21518	    rel_file = str(file)
 21519	    if os.path.isabs(rel_file) and repo_root is not None:
 21520	        rel_file = os.path.relpath(rel_file, str(repo_root))
 21521	
 21522	    # 8. stdin payload(階段三):{"query","prospective":{rel:content}}——prospective 供事故比對(套 delta 後),query 供詞彙融合。
 21523	    _payload = {}
 21524	    if payload is not None:          # 內部呼叫(--diff 聚合)直接給 dict,不經 stdin
 21525	        _payload = payload
 21526	        stdin_payload = True         # query/prospective 語意與 stdin 模式一致
 21527	    elif stdin_payload:
 21528	        try:
 21529	            _payload = json.loads(sys.stdin.read() or "{}")
 21530	        except ValueError:
 21531	            _payload = {}
 21532	    # incidents 段:掃全圖 pitfall_when trigger,比對被碰檔。
 21533	    # 內容來源:stdin prospective(套 delta 後,優先)> 磁碟現況。
 21534	    _abs_file = str(file)
 21535	    if not os.path.isabs(_abs_file) and repo_root is not None:
 21536	        _abs_file = str(repo_root / _abs_file)
 21537	    _prosp = _payload.get("prospective") or {}
 21538	    file_content = _prosp.get(rel_file)   # key 一律 repo-relative(spec §3;單一查找,無 fallback 歧義)
 21539	    if file_content is None:
 21540	        try:
 21541	            file_content = Path(_abs_file).read_text(encoding="utf-8-sig", errors="replace")
 21542	        except OSError:
 21543	            file_content = ""
 21544	
 21545	    # 呼叫 _match_incident_triggers,取得原始命中列表(含 node, matched_by)
 21546	    # content trigger 的比對對象(v1.1 精度修):有 delta(payload.query)→ 比對「這次改動的內容」;
 21547	    # 無 delta(legacy 呼叫)→ 比整檔現況。理由:整檔比對對單體大檔恆誤觸發
 21548	    # (scripts/lumos 本身定義 HOOK_ENTRIES 等符號,改任何一行都命中)——goldset 實測 3/9 固定席噪音源自此。
 21549	    # glob trigger(比路徑)不受影響。
 21550	    _delta_q = (_payload.get("query") or "") if stdin_payload else ""
 21551	    # 探測範圍 = delta + 鄰域窗(r1 終審折入):純 delta 會漏「改在危險函式內部、
 21552	    # 但編輯片段不含函式名」的真陰性;整檔比對又對單體檔恆誤觸發。
 21553	    # 折衷:在整檔內定位 delta 開頭片段,取 ±600 字元鄰域一起探測(窗寬 goldset 調參:2000 會把單體檔遠處符號掃回)——
 21554	    # 函式名通常在鄰域內(覆蓋回來),遠處無關符號仍在窗外(噪音不回來)。定位失敗=退回純 delta。
 21555	    _content_probe = file_content
 21556	    if _delta_q:
 21557	        _content_probe = _delta_q
 21558	        _seek = _delta_q[:80].strip()
 21559	        if _seek and file_content:
 21560	            _pos = file_content.find(_seek)
 21561	            _win = int(_impact_knob("LUMOS_IMPACT_TRIG_WIN", 600))
 21562	            if _pos >= 0 and _win > 0:
 21563	                _content_probe = _delta_q + "\n" + file_content[max(0, _pos - _win):_pos + _win]
 21564	    _raw_incidents = _match_incident_triggers(rel_file, _content_probe, env)
 21565	
 21566	    # 補 contract/combo(復用 _impact_contract);建 all_incidents list
 21567	    all_incidents = []
 21568	    for inc in _raw_incidents:
 21569	        inc_note = env.notes.get(inc["node"])
 21570	        inc_contract, inc_combo = _impact_contract(inc_note) if inc_note else (None, False)
 21571	        all_incidents.append({
 21572	            "node": inc["node"],
 21573	            "matched_by": inc["matched_by"],
 21574	            "contract": inc_contract,
 21575	            "combo": inc_combo,
 21576	        })
 21577	
 21578	    # 去重(§4):某節點既在 incidents 又在 direct/indirect → 從 direct/indirect 移除
 21579	    incident_node_set = {x["node"] for x in all_incidents}
 21580	    if incident_node_set:
 21581	        all_direct = [x for x in all_direct if x["node"] not in incident_node_set]
 21582	        all_indirect = [x for x in all_indirect if x["node"] not in incident_node_set]
 21583	
 21584	    # 8.5 ranked 融合(階段三,spec §3):固定席(事故+含合約 direct+深度內合約 indirect)不占 top_k;
 21585	    # 非固定按 R=0.6L+0.4G 排,過 max(min_score, 0.25×最高非固定分) 閾;姐妹去冗餘於顯示層。
 21586	    if ranked or incidents_only:
 21587	        query = (_payload.get("query") or "") if stdin_payload else ""
 21588	        results = []
 21589	        lane_raw = []   # 參考道原料(--incidents-only 不進 indirect 迴圈也要有定義)
 21590	        # 固定席:事故(kind=incident)恆固定
 21591	        for x in all_incidents:
 21592	            results.append({"node": x["node"], "kind": "incident", "pinned": True,
 21593	                            "score": 1.0, "matched_by": x.get("matched_by"),
 21594	                            "contract": x.get("contract")})
 21595	        gated = False   # 查詢品質閘觸發旗標(未觸發路徑必為 False,防 NameError)
 21596	        if not incidents_only:
 21597	            # query 品質閘(edit面查詢品質閘_計劃 S2):低資訊 query 視同空查詢——
 21598	            # 只覆寫 lex 用局部變數;事故探針 _delta_q 刻意不受閘(安全網寧多勿漏)
 21599	            if query and _impact_query_junk(query):
 21600	                query = ""
 21601	                gated = True
 21602	                print("(query 品質閘:文本為檔頭雜訊/過短,L 臂靜默)", file=sys.stderr)
 21603	            # 詞彙分:對 direct+indirect 候選跑 BM25F(query 為空則全 0)
 21604	            cand = [x["node"] for x in all_direct] + [x["node"] for x in all_indirect]
 21605	            lex = {}
 21606	            if query and cand:
 21607	                _mx = None
 21608	                raw = _rank_score_candidates(env, query, cand)
 21609	                _mx = max((s for _r, s, _h in raw), default=0.0)
 21610	                for _r, s, _h in raw:
 21611	                    lex[_r] = (s / _mx) if _mx > 0 else 0.0
 21612	            eff_depth = depth if depth is not None else 2
 21613	            _dbase = _impact_knob("LUMOS_IMPACT_DIRECT_BASE", 0.30)
 21614	            for x in all_direct:
 21615	                L = lex.get(x["node"], 0.0)
 21616	                pinned = bool(x.get("contract"))   # 含合約的 direct 固定
 21617	                results.append({"node": x["node"], "kind": "direct", "pinned": pinned,
 21618	                                "score": round(_dbase + (1.0 - _dbase) * L, 4), "L": round(L, 4),
 21619	                                "hit": x.get("hit"), "contract": x.get("contract")})
 21620	            _pin_hop = int(_impact_knob("LUMOS_IMPACT_PIN_HOP", 1))
 21621	            # ★pin-denoise-a-v4(2026-08-24,四輪設計審收斂)★:硬合約保送——knob=1 時 indirect 保送只認
 21622	            # INVARIANT/IRREVERSIBLE;RISK·* 類(樞紐筆記搭便車,held 噪音 58/96 的主力)降入「參考道」:
 21623	            # ★獨立容器 lane_raw,自始不進 results★(pinned:False 會被四處「非 pinned=free」分流吃回自由席、
 21624	            # 再被動態門檻砍出輸出——v3 r2 實測);JSON 用獨立頂層鍵 "lane"(決策 d2:沒學過 lane 的讀者
 21625	            # 結構性不受影響,diff 聚合/hook free 桶/守衛全免改)。
 21626	            # ★2026-08-24 考卷轉正預設 1(knob=0 留逃生)★:train LANE_N∈{2,3,5} 不敏感取 3;
 21627	            # 候選臂 held 噪音 82→39(-52%)、out_top3_must 0.083→0.367、must 兩棘輪零退、九關全過。
 21628	            _hard_pin = int(_impact_knob("LUMOS_IMPACT_HARD_PIN", 1))
 21629	            for x in all_indirect:
 21630	                L = lex.get(x["node"], 0.0)
 21631	                hop = x.get("hop", 2)
 21632	                contract = x.get("contract")
 21633	                # 合約固定席 hop 上限(v1.2 旋鈕):合約密集圖(Landmark 考卷實證)hop2 合約
 21634	                # 搭便車氾濫(51 席噪音)——收窄後 hop2 合約降入自由席按分數競爭(L≈0 者被閾殺)
 21635	                if contract and hop <= min(eff_depth, _pin_hop):
 21636	                    if _hard_pin and contract not in ("INVARIANT", "IRREVERSIBLE"):
 21637	                        # RISK·* 降參考道:score 用 indirect 自由席同款 R 公式(常數 0.70 全員同分,
 21638	                        # cap 挑誰會退化成字母序——v3 r3 s1f2);kind 保留 indirect(lane 是欄位不是 kind)
 21639	                        G = 0.60 * min(1.0, 2.0 / (2 ** hop))
 21640	                        lane_raw.append({"node": x["node"], "kind": "indirect", "pinned": False,
 21641	                                         "lane": "soft-guard", "score": round(0.60 * L + 0.40 * G, 4),
 21642	                                         "L": round(L, 4), "hop": hop, "contract": contract})
 21643	                        continue
 21644	                    results.append({"node": x["node"], "kind": "indirect", "pinned": True,
 21645	                                    "score": round(0.40 + 0.30, 4), "L": round(L, 4),
 21646	                                    "hop": hop, "contract": contract})
 21647	                    continue
 21648	                # hop≥2 需 L>底線(遠端節點要足夠詞彙證據背書)
 21649	                if hop >= 2 and L <= _impact_knob("LUMOS_IMPACT_LMIN_HOP2", 0.0):
 21650	                    continue
 21651	                G = 0.60 * min(1.0, 2.0 / (2 ** hop))
 21652	                R = round(0.60 * L + 0.40 * G, 4)
 21653	                results.append({"node": x["node"], "kind": "indirect", "pinned": False,
 21654	                                "score": R, "L": round(L, 4), "hop": hop, "contract": contract})
 21655	        # about_code 語意欄位(工具清單 #4):只標記、不動 pinned;--incidents-only 快速路徑整段跳過
 21656	        if not incidents_only:
 21657	            _impact_mark_about(env, results, rel_file)
 21658	        # 分固定/非固定;非固定過閾+排序+補到 top_k
 21659	        pins = [r for r in results if r["pinned"]]
 21660	        # 固定席內 stable sort:事故永遠最前(std-r1 s1f10),其次 about 命中者,其餘保持三軸原序
 21661	        pins.sort(key=lambda r: (r["kind"] != "incident", not r.get("about_hit", False)))
 21662	        free = [r for r in results if not r["pinned"]]
 21663	        max_free = max((r["score"] for r in free), default=0.0)
 21664	        thresh = max(float(min_score), _impact_knob("LUMOS_IMPACT_DYN_COEF", 0.65) * max_free)
 21665	        free = [r for r in free if r["score"] >= thresh]
 21666	        free.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))
 21667	        # 名額制(v1.1):單體檔洪水按排名剪尾——閾值管品質、名額管上限(gate 對齊 top_k+2=10);
 21668	        # 剪的是 11 名以後,不動前 8 的視野(精度/必看召回不受影響)
 21669	        # PPR 分量(檢索PPR邊權_計劃)已試已殺(2026-07-28 edit 卷 train 網格全負:
 21670	        # baseline nDCG@8 0.9831 vs ppr w0.2/0.4/0.6=0.9817/0.9668/0.9598,b1 純 PPR 與
 21671	        # b2 cochange 邊權同分=邊權零貢獻;free 池中位 3 席使 P@8 對重排零鑑別,裁決依 nDCG)。
 21672	        # 與 A3 同源教訓:本圖的圖傳播訊號打不過調校後的 BM25F 融合;勿憑直覺復活,
 21673	        # 重試須先過同款考卷。詳 Projects/檢索PPR邊權_計劃 墓碑節。
 21674	        _quota = int(_impact_knob("LUMOS_IMPACT_FREE_QUOTA", 10))
 21675	        truncated = max(0, len(free) - min(int(top), _quota))
 21676	        free = free[:min(int(top), _quota)]
 21677	        # R1 直連保底席(2026-08-07,plan:hook必看召回修復;第三桶明文):
 21678	        # 觸發=截斷後最終 free 集零 direct 且存在被閾砍/截的 direct(缺口)。
 21679	        # rescued 恆 pinned:false、threshold/quota 不作用其上、外掛於 free 之後(--top 例外,
 21680	        # 同 pins safety_overflow 精神);tie-break 沿 free.sort 慣例 (-score, hop, node)。
 21681	        # knob:LUMOS_IMPACT_RESCUE_N(2026-08-07 考卷轉正預設 1:held Σmust 12→14、
 21682	        # P@8 0.6389→0.6944 雙升,gate 兩條全過;knob=0 留 A 臂逃生)。
 21683	        # S2 水位謂詞(2026-08-07,plan:連結缺失補全):free 內 direct(排除 pinned;截斷後
 21684	        # 最終集)不足 N 席 → 補 need=max(0, N−count) 席(前案「僅零 direct 觸發」為 N=1 特例,
 21685	        # 向下相容;前案合約候選之改寫經考卷 A/B 重裁,互引留痕見兩計劃節點)。
 21686	        rescued = []
 21687	        # 2026-08-07 水位案考卷轉正 N=3(train 網格 {1,2,3} recall 軸選出;held 確認
 21688	        # Σmust 14→17、P@8 0.6944→0.7130 週閘翻綠;knob 留逃生)
 21689	        _rescue_n = int(_impact_knob("LUMOS_IMPACT_RESCUE_N", 3))
 21690	        _free_direct = sum(1 for r in free if r["kind"] == "direct")
 21691	        _need = max(0, _rescue_n - _free_direct)
 21692	        if _rescue_n > 0 and _need > 0:
 21693	            _free_ids = {id(r) for r in free}
 21694	            dropped = [r for r in results
 21695	                       if r["kind"] == "direct" and not r["pinned"] and id(r) not in _free_ids]
 21696	            dropped.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))
 21697	            for r in dropped[:_need]:
 21698	                rr = dict(r)
 21699	                rr["rescued"] = True
 21700	                rescued.append(rr)
 21701	        # 參考道:產生端 cap(三處輸出同一份,口徑合一——被 cap 砍的必看會誠實掉 must_in_out,棘輪有效)
 21702	        lane_items = []
 21703	        _lane_trunc = 0
 21704	        if lane_raw:
 21705	            lane_raw.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))   # 同 free/rescued 三鍵慣例
 21706	            _lane_n = max(0, int(_impact_knob("LUMOS_IMPACT_LANE_N", 3)))   # 負值防護(同 _rescue_n 的 max(0,…) 慣例;負切片語意是「砍尾」不是上限)
 21707	            lane_items = lane_raw[:_lane_n]
 21708	            _lane_trunc = len(lane_raw) - len(lane_items)
 21709	        # 姐妹去冗餘(顯示層,--json 全量不折)
 21710	        final = pins + free + rescued
 21711	        meta = {"candidates": len(all_direct) + len(all_indirect) + len(all_incidents),
 21712	                "pinned": len(pins), "truncated": truncated, "rescued": len(rescued),
 21713	                "safety_overflow": max(0, len(pins) - int(top))}
 21714	        if lane_raw:
 21715	            meta["lane"] = len(lane_items)
 21716	            meta["lane_truncated"] = _lane_trunc
 21717	        if as_json:
 21718	            out_obj = {"file": rel_file, "results": final, "meta": meta}
 21719	            if lane_items:   # 條件鍵(同 query_gated/stack_questions 慣例):knob=0 或空 → 鍵不存在
 21720	                out_obj["lane"] = lane_items

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/lumos | sed -n '21710,21845p'
nl -ba scripts/lumos | sed -n '21845,22055p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
 21710	        final = pins + free + rescued
 21711	        meta = {"candidates": len(all_direct) + len(all_indirect) + len(all_incidents),
 21712	                "pinned": len(pins), "truncated": truncated, "rescued": len(rescued),
 21713	                "safety_overflow": max(0, len(pins) - int(top))}
 21714	        if lane_raw:
 21715	            meta["lane"] = len(lane_items)
 21716	            meta["lane_truncated"] = _lane_trunc
 21717	        if as_json:
 21718	            out_obj = {"file": rel_file, "results": final, "meta": meta}
 21719	            if lane_items:   # 條件鍵(同 query_gated/stack_questions 慣例):knob=0 或空 → 鍵不存在
 21720	                out_obj["lane"] = lane_items
 21721	            if gated:
 21722	                out_obj["query_gated"] = True
 21723	            # 棧別效能追問(pitfalls棧別效能追問_計劃 T2):完整 ranked 模式(非 incidents-only
 21724	            # 冷卻快速路)且目標檔命中問題表 → 附該棧檢核問(全表);單源=_STACK_PERF_QUESTIONS,hook 只格式化
 21725	            if not incidents_only and not _PITFALL_DIFF_TEST_PAT.search(rel_file):
 21726	                _sk = _stack_key_for_file(rel_file, repo_root_for_lookup)   # .ts/.js 看 package.json 分前後端
 21727	                if _sk:
 21728	                    out_obj["stack_questions"] = {_sk: _STACK_PERF_QUESTIONS[_sk]}
 21729	                    # 觸發式適用性(表態閘 S3):hook 另送原始 delta_text(保留換行;query 那欄是 8000 字/512 詞截斷版,只給詞彙融合)
 21730	                    # → 只列命中 when 的題;沒送(legacy 呼叫)就沒有 applicable 鍵,hook 退回印全表。
 21731	                    _dt = _payload.get("delta_text") if stdin_payload else None
 21732	                    if isinstance(_dt, str):
 21733	                        _cfgq = _stack_questions_config(repo_root_for_lookup)
 21734	                        _app, _meta = _stack_applicability({_sk: _dt.splitlines()}, _cfgq["ask_all_over_lines"])
 21735	                        out_obj["stack_questions_applicable"] = _app
 21736	                        out_obj["stack_questions_meta"] = _meta
 21737	                        if _payload.get("delta_truncated"):
 21738	                            out_obj["delta_truncated"] = True
 21739	            print(json.dumps(out_obj, ensure_ascii=False))
 21740	        else:
 21741	            print(f"改動 {rel_file} — 相關 top(固定席 {len(pins)}):")
 21742	            for r in final:
 21743	                mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{r.get('hop','?')}"}.get(r["kind"], "")
 21744	                ct = f" ★{r['contract']}★" if r.get("contract") else ""
 21745	                pin = " [固定]" if r["pinned"] else ""
 21746	                print(f"  {r['score']:5.2f} {mk} {r['node']}{ct}{pin}")
 21747	            if meta["truncated"]:
 21748	                print(f"  (+{meta['truncated']} 條低分截斷;--json 全量)")
 21749	            if not lane_items and meta.get("lane_truncated"):
 21750	                print(f"  (守衛面參考 {meta['lane_truncated']} 條被 LANE_N cap 全部隱藏——網格消融才會發生)")
 21751	            if lane_items:
 21752	                print(f"守衛面參考(軟標記樞紐,未被本次改動直接證實相關,{len(lane_items)} 條):")
 21753	                for r in lane_items:
 21754	                    print(f"  {r.get('score', 0):5.2f} hop{r.get('hop', '?')} {r.get('node', '?')}  ({r.get('contract', '')})")
 21755	                if meta.get("lane_truncated"):
 21756	                    print(f"  (另有 {meta['lane_truncated']} 條守衛面參考未列出)")
 21757	            if meta["safety_overflow"]:
 21758	                print(f"  safety overflow: {meta['safety_overflow']}")
 21759	        return 0
 21760	
 21761	    # 9. 輸出
 21762	    if as_json:
 21763	        print(json.dumps(
 21764	            {"file": rel_file, "direct": all_direct, "indirect": all_indirect,
 21765	             "incidents": all_incidents},
 21766	            ensure_ascii=False,
 21767	        ))
 21768	    else:
 21769	        # 人讀輸出
 21770	        print(f"改動 {rel_file} (由讀盤 refcheck 抽取)")
 21771	        print(f"── 直接關聯 ({len(all_direct)}) ──")
 21772	        for x in all_direct:
 21773	            contract_tag = f" ★{x['contract']}★" if x.get("contract") else ""
 21774	            combo_tag = "★COMBO★" if x.get("combo") else ""
 21775	            tags = (contract_tag + (" " + combo_tag if combo_tag else "")).rstrip()
 21776	            print(f"  {'⚠合約 ' if x.get('contract') else ''}{x['node']}{tags}  ({x['hit']})")
 21777	        print(f"── 間接關聯 ({len(all_indirect)}) ──")
 21778	        for x in all_indirect:
 21779	            cross = " [跨repo葉,不展開]" if x.get("cross_repo") else ""
 21780	            print(f"  hop{x['hop']}  {x['node']}  {x['direction']} ← via {x['via']} ← {x['from']}{cross}")
 21781	        if all_incidents:
 21782	            print(f"── 相關事故 ({len(all_incidents)}) ──")
 21783	            for x in all_incidents:
 21784	                contract_tag = f" ★{x['contract']}★" if x.get("contract") else ""
 21785	                print(f"  {x['node']}{contract_tag}  (trigger: {x['matched_by']})")
 21786	
 21787	    return 0
 21788	
 21789	
 21790	_IMPACT_DIFF_SKIP = ("docs/", "governance/golden/")   # 圖譜/凍結快照非 code,不當 impact 種子
 21791	
 21792	
 21793	def _impact_diff_seed_ok(f):
 21794	    """--diff 種子過濾:只收 code 檔。剔除圖譜/凍結快照/帳檔(.jsonl)/文檔(.md)/
 21795	    governance 資料 .json(goldset/裁決紀錄內嵌歷史 code 片段,會偽觸發事故 pin——r1 panel 實證)。"""
 21796	    if not f or any(f.startswith(p) for p in _IMPACT_DIFF_SKIP):
 21797	        return False
 21798	    if f.endswith((".jsonl", ".md")):
 21799	        return False
 21800	    if f.endswith(".json") and f.startswith("governance/"):
 21801	        return False
 21802	    return True
 21803	
 21804	
 21805	def _impact_payload_read(path):
 21806	    """讀一份已經算好的波及結果(pre-push 每次推送只算一次,兩個消費者共用同一份)。
 21807	
 21808	    ★為什麼要有這支★(2026-09-07 全 repo 審視 #17,設計 [S1] 第 3 步):
 21809	    推送關卡本來就對每個 ref 跑一次完整的波及計算(同步點名用)。合約測試閘要的是
 21810	    同一份東西裡「帶合約而且綁了測試」的那幾篇——★再算一次就是把一次推送算兩次★,
 21811	    而那正是這一案 r1 拿來否決原設計的那個成本(那條裁定後來被查出已作廢,
 21812	    但「不要算兩次」本身仍然是對的)。
 21813	
 21814	    ★失敗要隔離★:讀不到就回 None,呼叫端各自決定怎麼降級——
 21815	    同步點名維持靜默,合約測試閘記一筆帳放行。一個失敗不准拖垮另一個。
 21816	    """
 21817	    import json as _json, stat as _stat
 21818	    # ★擁有權要驗,理由跟 dispatch-lens 那支快取一模一樣★
 21819	    # (2026-09-07 代碼審 r1 架構對齊席判 blocking,說得對):
 21820	    # 這個 repo 已經有一套硬化過的「算一次、之後讀」——_lens_cache_read,
 21821	    # 它會先驗 st_uid 與 group/other 可不可寫,註解明寫「$TMPDIR 路徑可預測可偽造」。
 21822	    # 而這裡收的正是一個從命令列傳進來的 $TMPDIR 路徑,同一種曝險。
 21823	    # ★但沒有照抄整套★,理由是生命週期不同,而這一點原本沒寫下來所以席位抓到了:
 21824	    #   dispatch-lens 那支是「跨呼叫、可被別人發現、要 TTL、要 key 去對」的快取;
 21825	    #   這裡是「同一次 hook 執行內、由呼叫端明確指定路徑、用完就刪」的交接。
 21826	    #   要 TTL 與 key 是多餘的,要擁有權驗證則是必要的——所以只借那一半。
 21827	    try:
 21828	        st = Path(path).stat()
 21829	        if st.st_uid != os.getuid() or (st.st_mode & (_stat.S_IWGRP | _stat.S_IWOTH)):
 21830	            return None
 21831	        data = _json.loads(Path(path).read_text(encoding="utf-8"))
 21832	    except Exception:
 21833	        return None
 21834	    # ★形狀要驗到位★(代碼審 r1 外家否決席判 major):只驗「是 dict 而且有 results」不夠——
 21835	    # `{"results":[1],"sync":[]}` 這種合法 JSON 會通過,然後在下游 r.get(...) 當場拋例外,
 21836	    # 而那個例外會被 pre-push 的 || true 吞掉:★不是按設計記 range-unavailable,是靜默失效★。
 21837	    if not isinstance(data, dict):
 21838	        return None
 21839	    res = data.get("results")
 21840	    if not isinstance(res, list) or any(not isinstance(r, dict) for r in res):
 21841	        return None
 21842	    sync = data.get("sync")
 21843	    if sync is not None and not (isinstance(sync, dict)
 21844	                                 and isinstance(sync.get("missing"), list)
 21845	                                 and isinstance(sync.get("touched_nodes"), list)):
 21845	                                 and isinstance(sync.get("touched_nodes"), list)):
 21846	        return None
 21847	    return data
 21848	
 21849	
 21850	def cmd_impact_diff(diff_range, repo=None, depth=None, top=8, min_score=0.20, as_json=False,
 21851	                    sync_check=False, sync_only=False, from_json=None):
 21852	    """code-loop 橋接:對整段 diff 的每支改動 code 檔跑 ranked impact(query=該檔 hunk 文字),
 21853	    聚合成「受影響功能面」manifest——固定席(合約/事故)全保、非固定取跨檔最高分 top-N。
 21854	    定位=審計員鏡頭(advisory,人判),非自動推播(hook 面 goldset 評測未過線,故不接 hook)。
 21855	    rc: 0=成功 / 2=git 失敗 / 3=vault 缺。
 21856	
 21857	    from_json:吃一份已經算好的結果,不自己算(見 _impact_payload_read)。目前只支援
 21858	    搭 --sync-only 用——推送關卡算一次、同步點名與合約測試閘各讀一次。"""
 21859	    if from_json is not None:
 21860	        _pl = _impact_payload_read(from_json)
 21861	        if _pl is None or _pl.get("sync") is None:
 21862	            return 0          # 失敗隔離:維持同步點名現在的行為(靜默)
 21863	        _print_sync_nudge(_pl["sync"], _pl.get("range") or diff_range)
 21864	        return 0
 21865	    import json as _json
 21866	    import subprocess as _sp
 21867	    if diff_range == "staged":
 21868	        # 圖譜同步覆蓋(2026-08-22):pre-commit 要對「這次 commit 的內容」算波及,用 staged 代替 range
 21869	        diff_range = "--staged"
 21870	    elif diff_range.startswith("-"):
 21871	        # 同 pitfalls/cochange-check:'-' 開頭值會被 git 誤認成選項,查詢命令 rc2 拒收
 21872	        print("擋下:--diff 的值不能用 - 開頭(會被當成選項)", file=sys.stderr)
 21873	        return 2
 21874	    repo_root = Path(repo) if repo else None
 21875	    if repo_root is None:
 21876	        for cand in (Path.cwd(), *Path.cwd().parents):
 21877	            if (cand / ".git").exists():
 21878	                repo_root = cand
 21879	                break
 21880	    if repo_root is None or not (repo_root / ".git").exists():
 21881	        print("擋下:找不到 git 專案,用 --repo 指定", file=sys.stderr)
 21882	        return 2
 21883	    # core.quotePath=false:CJK 檔名不轉義加引號(否則 startswith/endswith 過濾全失效,r2 panel major)
 21884	    r = _sp.run(["git", "-C", str(repo_root), "-c", "core.quotePath=false",
 21885	                 "diff", "--name-only", diff_range], capture_output=True, text=True, errors="replace")
 21886	    if r.returncode != 0:
 21887	        print(f"擋下:git 算不出差異: {r.stderr.strip()[:200]}", file=sys.stderr)
 21888	        return 2
 21889	    files = []
 21890	    for f in r.stdout.splitlines():
 21891	        f = f.strip()
 21892	        if not _impact_diff_seed_ok(f):
 21893	            continue
 21894	        # 已刪檔不跳過:反查靠「節點 body 引用該路徑」而非檔案存在——
 21895	        # 刪除/改名正是合約節點最該被推到審計員眼前的時刻(r1 codex major)
 21896	        files.append(f)
 21897	    merged = {}          # node -> entry(跨檔取最高分;pinned 任一檔 pinned 即 pinned)
 21898	    per_file_meta = []
 21899	    import io, contextlib
 21900	    _vault = _vault_in(repo_root)
 21901	    # ★沒有圖譜就直接說,不要印「0 篇」裝作查過了★(2026-09-07 全 repo 審視 #9)
 21902	    #
 21903	    # 出身:這條路原本只在**逐檔迴圈裡**才發現沒圖譜——而「這個範圍 0 個檔」時迴圈根本不跑,
 21904	    # 於是一路走到最後印出「固定席 0 + top 0」並回成功。
 21905	    # ★對新手最危險的就是這個★:同一件事(找不到圖譜),另外兩種問法一個回 rc3、一個回 rc2
 21906	    # 並印白話擋下,只有這條印「0 篇」**看起來像查過了**——而它根本沒有圖譜可查。
 21907	    # 文件本來就寫著這條路會回「圖譜缺」,只是零檔時走不到。
 21908	    if _vault is None:
 21909	        return _no_vault_msg()
 21910	    _env_shared = Env(_vault)   # 建一次,逐檔復用(r1 N+1)
 21911	    for f in files:
 21912	        d = _sp.run(["git", "-C", str(repo_root), "-c", "core.quotePath=false",
 21913	                     "diff", diff_range, "--", f], capture_output=True, text=True, errors="replace")
 21914	        hunk = " ".join(l[1:].strip() for l in d.stdout.splitlines()
 21915	                        if l[:1] in "+-" and not l.startswith(("+++", "---")))[:4000]
 21916	        buf = io.StringIO()
 21917	        with contextlib.redirect_stdout(buf):
 21918	            rc = cmd_impact(f, repo=str(repo_root), depth=depth, as_json=True,
 21919	                            ranked=True, top=top, min_score=min_score,
 21920	                            payload={"query": hunk, "prospective": {}},
 21921	                            preloaded=(_vault, _env_shared) if _env_shared is not None else None)
 21922	        if rc == 3:
 21923	            print("IMPACT-DEBUG: vault 找不到(rc3)", file=sys.stderr)
 21924	            return 3
 21925	        if rc != 0:
 21926	            continue
 21927	        try:
 21928	            data = _json.loads(buf.getvalue().strip().splitlines()[-1])
 21929	        except (ValueError, IndexError):
 21930	            continue
 21931	        _pm = {"file": f, **data.get("meta", {})}
 21932	        if data.get("query_gated"):
 21933	            _pm["query_gated"] = True   # 觀測欄聚合轉發(r1 f5:code-loop 鏡頭可見)
 21934	        per_file_meta.append(_pm)
 21935	        for x in data.get("results", []):
 21936	            cur = merged.get(x["node"])
 21937	            if cur is None:
 21938	                merged[x["node"]] = {**x, "files": [f]}
 21939	            else:
 21940	                if f not in cur["files"]:
 21941	                    cur["files"].append(f)
 21942	                pinned = cur["pinned"] or x.get("pinned", False)
 21943	                if x["score"] > cur["score"]:
 21944	                    # 整項以勝出結果重建(避免 hop/L 舊值殘留成幽靈欄位,r1 s4 minor)
 21945	                    merged[x["node"]] = {**x, "files": cur["files"], "pinned": pinned}
 21946	                else:
 21947	                    cur["pinned"] = pinned
 21948	    pins = sorted([v for v in merged.values() if v["pinned"]],
 21949	                  key=lambda v: (-v["score"], v["node"]))
 21950	    free = sorted([v for v in merged.values() if not v["pinned"]],
 21951	                  key=lambda v: (-v["score"], v["node"]))[:int(top)]
 21952	    # 落成位置閉環(sync-check):預期受影響節點 ∩ 分支實際動過的圖譜節點——
 21953	    # 「這功能被改了,它的節點卻沒動」= 受影響未同步清單(advisory,人判;固定席可信度高、自由席≈P@8 .70)
 21954	    sync = None
 21955	    if sync_check:
 21956	        _vault_name = _vault.name if _vault is not None else None
 21957	        touched = set()
 21958	        if _vault_name:
 21959	            _prefix = f"docs/{_vault_name}/"
 21960	            for f2 in r.stdout.splitlines():
 21961	                f2 = f2.strip().strip('"')
 21962	                if f2.startswith(_prefix) and f2.endswith(".md"):
 21963	                    touched.add(f2[len(_prefix):])
 21964	        missing = [v for v in (pins + free) if v["node"] not in touched]
 21965	        sync = {"touched_nodes": sorted(touched),
 21966	                "missing": [{"node": v["node"], "pinned": v["pinned"],
 21967	                             "score": v["score"], "files": v["files"]} for v in missing]}
 21968	    if as_json:
 21969	        print(_json.dumps({"range": diff_range, "files": files,
 21970	                           "results": pins + free,
 21971	                           **({"sync": sync} if sync is not None else {}),
 21972	                           "meta": {"files": len(files), "pinned": len(pins),
 21973	                                    "free_kept": len(free),
 21974	                                    "free_total": sum(1 for v in merged.values() if not v["pinned"]),
 21975	                                    "per_file": per_file_meta}}, ensure_ascii=False))
 21976	        return 0
 21977	    if sync_only and sync is not None:
 21978	        _print_sync_nudge(sync, diff_range)
 21979	        return 0
 21980	    print(f"受影響功能面({diff_range};{len(files)} 檔;固定席 {len(pins)}+top {len(free)}——審計鏡頭,人判):")
 21981	    for v in pins + free:
 21982	        mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{v.get('hop','?')}"}.get(v["kind"], "")
 21983	        ct = f" ★{v['contract']}★" if v.get("contract") else ""
 21984	        pin = " [固定]" if v["pinned"] else ""
 21985	        print(f"  {v['score']:5.2f} {mk} {v['node']}{ct}{pin}  ←{','.join(v['files'][:3])}")
 21986	    if not merged:
 21987	        print("  (無節點引用這些檔——圖譜對此 diff 無覆蓋)")
 21988	    if sync is not None:
 21989	        _print_sync_nudge(sync, diff_range)
 21990	    return 0
 21991	
 21992	
 21993	def _print_sync_nudge(sync, diff_range, cap=8):
 21994	    """落成核對的唯一呈現(2026-08-22 架構對齊席抓到三套並存後收斂成這一份):
 21995	    固定席(合約/事故/直接相依)優先、最多 cap 篇;hooks(pre-commit/pre-push/Stop)只呼叫,不自己重排。"""
 21996	    miss = sorted(sync["missing"], key=lambda m: (not m["pinned"], -m.get("score", 0)))
 21997	    print(f"\n落成核對(這批動過 {len(sync['touched_nodes'])} 篇筆記):")
 21998	    if not miss:
 21999	        print("  ✓ 預期受影響的筆記全數已同步")
 22000	        return
 22001	    pinned = [m for m in miss if m["pinned"]]
 22002	    print(f"  提醒:下面這些筆記跟改到的程式碼直接相關(合約 / 事故 / 直接相依),這批沒動:" if pinned
 22003	          else "  提醒:下面這些筆記可能受影響,這批沒動(自由席,可信度較低,人判):")
 22004	    for v in miss[:cap]:
 22005	        mark = "⚠必看" if v["pinned"] else "  "
 22006	        print(f"  {mark} {v['node']}  ←{','.join(v['files'][:2])}")
 22007	    if len(miss) > cap:
 22008	        print(f"  … 還有 {len(miss) - cap} 篇(lumos impact --diff {diff_range} --sync-check --json 看全部)")
 22009	    print("  確定不受影響就略過;受影響的現在補。這裡只提醒不擋。")
 22010	
 22011	
 22012	# ── code-loop 留痕(Task 1) ────────────────────────────────────────────────────
 22013	
 22014	def _codeloop_git_branch(repo_root):
 22015	    """取 HEAD branch 名(detached HEAD 回 HEAD)。"""
 22016	    import subprocess
 22017	    r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
 22018	                       capture_output=True, text=True, errors="replace", cwd=str(repo_root))
 22019	    return r.stdout.strip() or "HEAD"
 22020	
 22021	
 22022	# ---------------------------------------------------------------------------
 22023	# dispatch-lens(Projects/派工鏡頭注入_計劃,2026-09-03):代碼審派工詞的固定席鏡頭
 22024	# hook 是薄殼(scripts/hooks/claude/dispatch-lens-hook.py),所有 git/合約/圖譜判斷都在這裡,
 22025	# 沿用既有 helper(_git_commit_exists / INVARIANT_RE 家族 / _vault_in 的排序規則)。
 22026	# 消毒原則(r2/r3 載荷席):來自圖譜或 diff 的自由文字零輸出——只印固定字彙、base 已追蹤路徑、
 22027	# base 版合約行(KEY: 行)。清單本身仍用工作樹圖譜算(d3:能藏不能說)。
 22028	# rc:0=成功(含 0 篇,text 空)/2=輸入或 git 壞/3=vault 缺/4=base 不在主線
 22029	# ---------------------------------------------------------------------------
 22030	_LENS_HEADER = "lumos 自動附加:本次改動的固定席節點(來源 impact --diff,只供參考)"
 22031	_LENS_SHA_RE = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")
 22032	_LENS_KIND = {"direct": "直接相依", "indirect": "間接相依", "incident": "事故"}
 22033	
 22034	
 22035	def _lens_range_ok(diff_range):
 22036	    """恰好一個 `..`、兩端非空、不含 `...`、不以 - 開頭(r3 極端輸入席收緊)。"""
 22037	    if not isinstance(diff_range, str) or diff_range.startswith("-") or "..." in diff_range:
 22038	        return None
 22039	    parts = diff_range.split("..")
 22040	    if len(parts) != 2 or not parts[0] or not parts[1]:
 22041	        return None
 22042	    if any(ch.isspace() for ch in diff_range):
 22043	        return None
 22044	    return parts[0], parts[1]
 22045	
 22046	
 22047	def _lens_git(repo_root, *args, quote=False, binary=False):
 22048	    """binary=True:輸出照位元組回(不解碼)——讀檔案內容算指紋用,非 UTF-8 的內容也不會在解碼時噴錯。"""
 22049	    import subprocess as _sp
 22050	    cmd = ["git", "-C", str(repo_root)]
 22051	    if quote:
 22052	        cmd += ["-c", "core.quotePath=false"]
 22053	    try:
 22054	        if binary:
 22055	            return _sp.run(cmd + list(args), capture_output=True, timeout=20)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'rg -n "''^def _nodehome_(list|status|config|collect)|_NODEHOME_HOME_STATUSES|class _NodehomeSide" scripts/lumos
nl -ba scripts/lumos | sed -n '"'17630,17875p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
17699:_NODEHOME_HOME_STATUSES = ("doing", "done", "stale")   # [S2] planned/deferred 還不是現況、rejected/superseded 已不是
17707:def _nodehome_config(repo_root, text=None, from_snapshot=False):
17807:class _NodehomeSide:
17832:def _nodehome_list(repo_root, where):
18002:        if n["type"] != "system" or n["status"] not in _NODEHOME_HOME_STATUSES:
18221:        if (b is None or b["sig"] != n["sig"]) and n["status"] in _NODEHOME_HOME_STATUSES:
18232:        becomes_home = n["status"] in _NODEHOME_HOME_STATUSES and (b is None or b["status"] not in _NODEHOME_HOME_STATUSES)
18273:                    tip_home = rel in N.notes and N.notes[rel]["status"] in _NODEHOME_HOME_STATUSES
18274:                    if info["type"] != "system" or not (info["statuses"] & set(_NODEHOME_HOME_STATUSES) or tip_home):
18482:        if n["status"] in _NODEHOME_HOME_STATUSES and cnt > cfg["max_files"] and not _nodehome_resp_ok(n["resp"]):
18484:            was_over = g is not None and g["status"] in _NODEHOME_HOME_STATUSES and not _nodehome_resp_ok(g["resp"]) \
 17630	            print("notice: baseline not found — run --update-baseline to establish")
 17631	        if new_modules:
 17632	            print(f"notice: new modules (not in baseline): {', '.join(new_modules)}")
 17633	    return 0
 17634	
 17635	
 17636	def _lint_watch_mode(repo_root, as_json):
 17637	    """lumos lint-watch: 讀 .lumos/lint-watch.json、逐條查 registry、輸出 manifest。
 17638	    rc 0 = 成功(含空清單); rc 2 = config 格式錯誤。
 17639	    """
 17640	    import json
 17641	    cfg_path = Path(repo_root) / ".lumos" / "lint-watch.json"
 17642	    if not cfg_path.exists():
 17643	        entries = []
 17644	    else:
 17645	        try:
 17646	            with open(cfg_path, encoding="utf-8") as fh:
 17647	                entries = json.load(fh)
 17648	        except Exception as e:
 17649	            print(f"擋下:lint-watch.json 讀不了(JSON 格式壞了?): {e}", file=sys.stderr)
 17650	            return 2
 17651	        if not isinstance(entries, list):
 17652	            print("擋下:lint-watch.json 最外層要是陣列", file=sys.stderr)
 17653	            return 2
 17654	        for entry in entries:
 17655	            if not isinstance(entry, dict) or not all(k in entry for k in ("name", "registry", "current")):
 17656	                print("擋下:lint-watch.json 裡每一條都要有 name、registry、current 三個欄位", file=sys.stderr)
 17657	                return 2
 17658	
 17659	    candidates, failed, checked = [], [], 0
 17660	    for entry in entries:
 17661	        latest, reason = _registry_latest(entry["registry"])
 17662	        if latest is None:
 17663	            failed.append({"name": entry["name"], "reason": reason})
 17664	        else:
 17665	            state, r = _compare_versions(entry["current"], latest)
 17666	            if state == "behind":
 17667	                candidates.append({
 17668	                    "name": entry["name"],
 17669	                    "registry": entry["registry"],
 17670	                    "current": entry["current"],
 17671	                    "latest": latest,
 17672	                })
 17673	                checked += 1
 17674	            elif state == "current":
 17675	                checked += 1
 17676	            else:  # skip
 17677	                failed.append({"name": entry["name"], "reason": r})
 17678	
 17679	    if as_json:
 17680	        print(json.dumps({"candidates": candidates, "checked": checked, "failed": failed},
 17681	                         ensure_ascii=False))
 17682	    else:
 17683	        for c in candidates:
 17684	            print(f"{c['name']} {c['current']} → {c['latest']}")
 17685	    return 0
 17686	
 17687	
 17688	# ── 每支檔有家:程式檔歸屬與寫回落點的檢查(Projects/每支檔有家_計劃,2026-09-11) ──────────────
 17689	# ★為什麼存在★:一篇節點在依賴行用反引號寫別人的檔,改那些檔時推筆記就推它、寫回就落它——兩個消費專案兩天內
 17690	# 長歪兩次、工具全綠。這一段在提交與推送的當下擋「新違規」,舊帳交給健檢提醒(決策 d1)。
 17691	# 單源=計劃節點;每條規則的註解標它對回的條款編號 [SN]。
 17692	_NODEHOME_CODE_EXTS = {".cs", ".vue", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".sql", ".py", ".kt", ".kts",
 17693	                       ".java", ".swift", ".go", ".rs", ".c", ".cc", ".cpp", ".h", ".hpp", ".sh", ".ps1"}
 17694	# ↑「改程式要動圖譜」那道閘的第五份副本(另外四份在提交前/提交後掛鉤與 Claude 端兩支掛鉤)——
 17695	#   t_code_exts_lists_agree 釘五份一致 [S1]。不借 CODE_EXTS_T:那份是符號查核用的,內容不同。
 17696	_NODEHOME_EXCLUDE_GLOBS = ("docs/*", "*/node_modules/*", "*/bin/*", "*/obj/*", "*/.git/*",
 17697	                           "*/dist/*", "*/build/*", "*/__pycache__/*")
 17698	# ↑ 跟提交前掛鉤 should_exclude 的目錄排除同一份(t_nodehome_required_files_definition 逐字比對)
 17699	_NODEHOME_HOME_STATUSES = ("doing", "done", "stale")   # [S2] planned/deferred 還不是現況、rejected/superseded 已不是
 17700	_NODEHOME_GATE_VALUES = ("on", "warn", "off")          # [S37]
 17701	_NODEHOME_MAX_FILES_DEFAULT = 3                        # [S18] 跟開新節點提示的「0~3 支」一致
 17702	_NODEHOME_RESP_MIN_CHARS = 10                          # [S16]
 17703	_NODEHOME_MSG_CAP = 10                                 # [S6] 跟「改程式沒動圖譜」那道擋下訊息同一個上限
 17704	_NODEHOME_GOLIVE_MARK = "home check --staged"          # [S39] 提交前掛鉤裡有這串=這道檢查上線了
 17705	
 17706	
 17707	def _nodehome_config(repo_root, text=None, from_snapshot=False):
 17708	    """讀 node_home 設定。回 {mode: on|warn|off, max_files: int, ignore: [str], warnings: [str]};壞值一律退回預設並留一句。
 17709	    from_snapshot=True:text 是被檢查那個版本裡 .lumos/config.json 的內容(None=那個版本沒有這支檔)——
 17710	    ★提交前讀提交索引、推送前讀終點那個提交★,不讀工作目錄(工作目錄裡沒暫存的「關掉」不得關掉提交索引的檢查)。
 17711	    from_snapshot=False:直讀工作目錄(健檢開頭那一行用;同 _stack_questions_config 慣例)。
 17712	    ★鍵叫 mode 不叫 gate★:治理閘名的漂移掃描會把 gate 鍵的字面值當閘名(同 _stack_questions_config)。"""
 17713	    cfg = {"mode": "on", "max_files": _NODEHOME_MAX_FILES_DEFAULT, "ignore": [], "warnings": []}
 17714	    if from_snapshot:
 17715	        if text is None:
 17716	            return cfg
 17717	        raw = text.decode("utf-8-sig", errors="replace") if isinstance(text, (bytes, bytearray)) else str(text)
 17718	    else:
 17719	        p = Path(repo_root) / ".lumos" / "config.json"
 17720	        # 捷徑檔不跟過去讀:跟讀快照那條路一樣(git 裡的捷徑檔讀出來是目標路徑字串,解析失敗退預設)——
 17721	        # 不然設定檔被做成指到本機任意檔的捷徑,健檢每次都會去讀那支檔(代碼審 r1 資安席)。
 17722	        # ★整條路徑都要看★:只看 config.json 本身,.lumos 資料夾是捷徑時照樣讀到外面(代碼審 r2 資安席、邊界席)
 17723	        try:
 17724	            _via_link = p.is_symlink() or (p.exists() and p.resolve() != Path(repo_root).resolve() / ".lumos" / "config.json")
 17725	        except OSError:
 17726	            _via_link = True
 17727	        if _via_link:
 17728	            cfg["warnings"].append(".lumos/config.json(或 .lumos 資料夾)是捷徑檔,不跟過去讀,每支檔有家用預設(會擋、上限 "
 17729	                                   f"{_NODEHOME_MAX_FILES_DEFAULT} 支、不額外排除)——要設定就放一支一般檔")
 17730	            return cfg
 17731	        if not p.is_file():
 17732	            return cfg
 17733	        try:
 17734	            raw = p.read_text(encoding="utf-8")
 17735	        except Exception as e:
 17736	            cfg["warnings"].append(f".lumos/config.json 讀不了({e.__class__.__name__}),每支檔有家用預設(會擋、上限 {_NODEHOME_MAX_FILES_DEFAULT} 支、不額外排除)")
 17737	            return cfg
 17738	    try:
 17739	        data = json.loads(raw)
 17740	    except Exception as e:
 17741	        cfg["warnings"].append(f".lumos/config.json 讀不了({e.__class__.__name__}),每支檔有家用預設(會擋、上限 {_NODEHOME_MAX_FILES_DEFAULT} 支、不額外排除)")
 17742	        return cfg
 17743	    nh = data.get("node_home") if isinstance(data, dict) else None
 17744	    if nh is None:
 17745	        return cfg
 17746	    if not isinstance(nh, dict):
 17747	        cfg["warnings"].append("設定檔的 node_home 不是物件,整段用預設")
 17748	        return cfg
 17749	    g = nh.get("gate", "on")
 17750	    if g not in _NODEHOME_GATE_VALUES:
 17751	        cfg["warnings"].append(f"設定檔的 node_home.gate={g!r} 看不懂(只認 {'/'.join(_NODEHOME_GATE_VALUES)}),已用 on")
 17752	    else:
 17753	        cfg["mode"] = g
 17754	    mf = nh.get("max_files", _NODEHOME_MAX_FILES_DEFAULT)
 17755	    # ★bool 要單獨擋★:Python 的 True 是 int 的子類,不擋的話上限悄悄變成 1(同合約條數門檻那支)
 17756	    if isinstance(mf, bool) or not isinstance(mf, int) or mf < 1:
 17757	        cfg["warnings"].append(f"設定檔的 node_home.max_files={mf!r} 不合法(要 1 以上的整數),已用 {_NODEHOME_MAX_FILES_DEFAULT}")
 17758	    else:
 17759	        cfg["max_files"] = mf
 17760	    ig = nh.get("ignore", [])
 17761	    if not isinstance(ig, list):
 17762	        cfg["warnings"].append("設定檔的 node_home.ignore 要是字串清單,整段略過")
 17763	    else:
 17764	        for i, item in enumerate(ig):
 17765	            if isinstance(item, str) and item.strip():
 17766	                cfg["ignore"].append(item.strip())
 17767	            else:
 17768	                cfg["warnings"].append(f"設定檔的 node_home.ignore 第 {i + 1} 項不是字串({item!r}),略過這一項")
 17769	    return cfg
 17770	
 17771	
 17772	def _nodehome_resp_ok(value):
 17773	    """[S16] 負責範圍:至少 10 個字、要有實字(全標點、空白視同沒寫)。實字判準同 [manual:] 那條。"""
 17774	    if not isinstance(value, str):
 17775	        return False
 17776	    v = value.strip()
 17777	    return len(v) >= _NODEHOME_RESP_MIN_CHARS and bool(re.search(r"[^\W_]", v))
 17778	
 17779	
 17780	def _nodehome_is_test(path):
 17781	    """測試檔判定:先問測試地圖那一支;副檔名不在它清單裡的(shell、Go、Rust、C…),套它同一組目錄與檔名規則。"""
 17782	    global _TESTMAP_DIR_RE
 17783	    if _testmap_is_test(path):
 17784	        return True
 17785	    if _testmap_ext(path) in _TESTMAP_EXTS:
 17786	        return False                      # 測試地圖認得這種副檔名,它說不是就不是
 17787	    if _TESTMAP_DIR_RE is None:
 17788	        _TESTMAP_DIR_RE = re.compile(r"(^|/)(tests?|__tests__|specs?)/", re.IGNORECASE)
 17789	    if _TESTMAP_DIR_RE.search(path):
 17790	        return True
 17791	    name = path.rsplit("/", 1)[-1]
 17792	    stem = _testmap_stem(path)
 17793	    return (".spec." in name or ".test." in name or stem.startswith("test_")
 17794	            or stem.lower().endswith(("_tests", "_specs", "_test", "_spec")))   # 底線變體同測試地圖(Go 的 foo_test.go)
 17795	
 17796	
 17797	def _nodehome_code_kind(path):
 17798	    """回 'ext'(副檔名在清單裡)/'shebang?'(沒副檔名,要看首行)/None(不是程式檔)。
 17799	    副檔名判法照提交前掛鉤那條正則:大小寫敏感、看最後一個點之後;沒副檔名=去掉開頭所有點之後沒有點。"""
 17800	    base = path.rsplit("/", 1)[-1]
 17801	    stripped = base.lstrip(".")
 17802	    if "." in stripped:
 17803	        return "ext" if ("." + stripped.rsplit(".", 1)[1]) in _NODEHOME_CODE_EXTS else None
 17804	    return "shebang?"
 17805	
 17806	
 17807	class _NodehomeSide:
 17808	    """一邊的快照(提交索引、某個提交、或空的)。files={路徑: 模式} 只收一般檔;all_paths=所有受版控路徑(數裸檔名用);
 17809	    notes={圖譜相對路徑: 解析結果} 只收 Systems/*.md;shebang={路徑: 首行是不是 #!}(需要時才讀、兩邊共用);
 17810	    share/changed:另一邊的快照與兩邊之間有變動的路徑——沒變動的節點與首行直接用另一邊讀好的,不再讀一次。
 17811	    路徑用無損解碼([S31]:跟磁碟枚舉一樣,git 那邊才對得上)。"""
 17812	    __slots__ = ("files", "all_paths", "notes", "where", "_reader", "shebang", "share", "changed")
 17813	
 17814	
 17815	def _nodehome_git(repo_root, *args):
 17816	    """跑 git、輸出照位元組回(路徑要無損解碼,不能先被文字模式換成替代字元);跑不起來回 None。"""
 17817	    r = _lens_git(repo_root, *args, binary=True)
 17818	    if r is None or r.returncode != 0:
 17819	        return None
 17820	    return r.stdout
 17821	
 17822	
 17823	def _nodehome_show(path):
 17824	    """路徑拿來印的時候用:非 UTF-8 的位元組(無損解碼留下的替身字元)換成替代字元——直接 print 會在嚴格編碼的輸出上當掉。"""
 17825	    return os.fsencode(path).decode("utf-8", errors="replace") if isinstance(path, str) else str(path)
 17826	
 17827	
 17828	def _nodehome_split_z(raw):
 17829	    return [os.fsdecode(x) for x in raw.split(b"\0") if x]
 17830	
 17831	
 17832	def _nodehome_list(repo_root, where):
 17833	    """where='index' / 提交 sha / None(空)。回 (一般檔 {路徑: 模式}, 所有路徑) 或 None(git 失敗)。
 17834	    模式從索引或提交樹讀——連結檔(120000)與子模組(160000)不算一般檔 [S40]。"""
 17835	    if where is None:
 17836	        return {}, []
 17837	    raw = _nodehome_git(repo_root, "ls-files", "-s", "-z") if where == "index" else \
 17838	        _nodehome_git(repo_root, "ls-tree", "-r", "-z", "--full-tree", where)
 17839	    if raw is None:
 17840	        return None
 17841	    files, allp = {}, []
 17842	    for ent in raw.split(b"\0"):
 17843	        if not ent or b"\t" not in ent:
 17844	            continue
 17845	        meta, p = ent.split(b"\t", 1)
 17846	        parts = meta.split()
 17847	        if where == "index":
 17848	            if len(parts) != 3 or parts[2] != b"0":      # 合併中的衝突階段不算
 17849	                continue
 17850	            mode = parts[0]
 17851	        else:
 17852	            if len(parts) != 3:
 17853	                continue
 17854	            mode = parts[0]
 17855	        path = nfc(os.fsdecode(p))
 17856	        allp.append(path)
 17857	        if mode in (b"100644", b"100755"):
 17858	            files[path] = mode.decode()
 17859	    return files, allp
 17860	
 17861	
 17862	def _nodehome_changed_vs_disk(repo_root, where):
 17863	    """跟磁碟不一樣的路徑集合(那些要從 git 讀,其餘直接讀磁碟——既有的 git show 包裝一支一支讀,只讀這些)。
 17864	    where='index':工作目錄 vs 索引;where=HEAD 的 sha:工作目錄 vs HEAD;其他提交=None(全部從 git 讀)。"""
 17865	    if where == "index":
 17866	        raw = _nodehome_git(repo_root, "diff", "--name-only", "-z", "--no-renames")
 17867	    else:
 17868	        raw = _nodehome_git(repo_root, "diff", "--name-only", "-z", "--no-renames", where)
 17869	    if raw is None:
 17870	        return None
 17871	    return {nfc(x) for x in _nodehome_split_z(raw)}
 17872	
 17873	
 17874	def _nodehome_reader(repo_root, where):
 17875	    """回 read(path)->bytes|None。讀的是 where 那個版本:跟磁碟一樣的直接讀磁碟,不一樣的用 git show 讀

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/hooks/claude/impact-hook.py | sed -n '580,900p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
   580	                lines.append(f"  {prefix} {node}  ({hit})")
   581	            else:
   582	                lines.append(f"  {node}  ({hit})")
   583	
   584	    if indirect:
   585	        lines.append("透過連結間接牽到的筆記:")
   586	        for item in indirect:
   587	            node = item.get("node", "?")
   588	            hop = item.get("hop", "?")
   589	            via = item.get("via", "?")
   590	            direction = item.get("direction", "")
   591	            contract = item.get("contract")
   592	            combo = item.get("combo", False)
   593	            cross = item.get("cross_repo", False)
   594	            prefix = ""
   595	            if contract:
   596	                prefix = f"★{contract}★"
   597	            if combo:
   598	                prefix += "★COMBO★"
   599	            suffix = ""
   600	            if cross:
   601	                suffix = " [跨repo葉,不展開]"
   602	            dir_tag = f" [{direction}]" if direction else ""
   603	            if prefix:
   604	                lines.append(f"  hop{hop} {prefix} {_plain_label(node)}  via {_plain_label(via)}{dir_tag}{suffix}")
   605	            else:
   606	                lines.append(f"  hop{hop} {_plain_label(node)}  via {_plain_label(via)}{dir_tag}{suffix}")
   607	
   608	    incidents = impact_data.get("incidents", [])
   609	    if incidents:
   610	        lines.append("這個檔過去出過的事故(改之前先看):")
   611	        for item in incidents:
   612	            node = item.get("node", "?")
   613	            matched_by = item.get("matched_by", "?")
   614	            contract = item.get("contract")
   615	            combo = item.get("combo", False)
   616	            prefix = _contract_label(contract) if contract else ""
   617	            if combo:
   618	                prefix += "★COMBO★"
   619	            label = _match_label(matched_by)
   620	            if prefix:
   621	                lines.append(f"  {prefix} {_plain_label(node)}  ({label})")
   622	            else:
   623	                lines.append(f"  {_plain_label(node)}  ({label})")
   624	
   625	    lines.append("")
   626	    lines.append(_INJECT_INSTRUCTION)
   627	    return _frame_injected("\n".join(lines))
   628	
   629	
   630	def build_ranked_context(data: dict) -> str:
   631	    """v1.1:把 ranked 輸出({results,meta})轉成降噪清單文字。固定席在前(合約/事故),
   632	    非固定帶分數;截斷數照 meta 標注。尾附棧別效能追問(若 lumos 輸出帶 stack_questions——
   633	    單源在 scripts/lumos 的 _STACK_PERF_QUESTIONS,本 hook 只格式化不持有內容)。"""
   634	    lines: list[str] = []
   635	    res = data.get("results", [])
   636	    meta = data.get("meta", {})
   637	    pins = [x for x in res if x.get("pinned")]
   638	    free = [x for x in res if not x.get("pinned") and not x.get("rescued")]
   639	    rescued = [x for x in res if x.get("rescued")]
   640	    if pins:
   641	        lines.append(f"必看——這 {len(pins)} 篇帶著不能破壞的合約或出過事故:")
   642	        for x in pins:
   643	            mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{x.get('hop','?')}"}.get(x.get("kind"), "")
   644	            ct = f" {_contract_label(x['contract'])}" if x.get("contract") else ""
   645	            mb = f"  ({_match_label(x['matched_by'])})" if x.get("matched_by") else ""
   646	            # about_code 語意欄位命中(工具清單 #9):讀 about_hit(只在 True 時存在),不碰既有 hit 來源標記
   647	            ab = "★關於★" if x.get("about_hit") else ""
   648	            lines.append(f"  {ab}{mk}{ct} {_plain_label(x.get('node'))}{mb}")
   649	    if free:
   650	        lines.append(f"可能相關的 {len(free)} 篇(依關聯度排序):")
   651	        for x in free:
   652	            mk = {"direct": "直接", "indirect": f"hop{x.get('hop','?')}"}.get(x.get("kind"), "")
   653	            lines.append(f"  {x.get('score',0):.2f} {mk} {_plain_label(x.get('node'))}")
   654	    if rescued:
   655	        # R1 直連保底(plan:hook必看召回修復):分數不過閾但為僅有的直連節點——信心層級不同於排序席
   656	        lines.append(f"另外 {len(rescued)} 篇分數不高但直接提到這個檔,一併列出:")
   657	        for x in rescued:
   658	            hit = f"/{x['hit']}" if x.get("hit") == "basename-match" else ""
   659	            lines.append(f"  {x.get('score',0):.2f} 直接{hit} {_plain_label(x.get('node'))}")
   660	    if meta.get("truncated"):
   661	        lines.append(f"  (+{meta['truncated']} 條低分截斷,沒列出來)")
   662	    # pin-denoise-a-v4:參考道(JSON 獨立頂層鍵;.get 條件鍵慣例——knob=0 時鍵不存在)
   663	    lane = data.get("lane", [])
   664	    if lane:
   665	        lines.append(f"守衛面參考——這 {len(lane)} 篇是軟標記樞紐,跟每支檔都近,未被本次改動直接證實相關:")
   666	        for x in lane:
   667	            lines.append(f"  {x.get('score',0):.2f} hop{x.get('hop','?')} {x.get('node','?')}")
   668	        if meta.get("lane_truncated"):
   669	            lines.append(f"  (另有 {meta['lane_truncated']} 條守衛面參考未列出)")
   670	    # 表態閘 S3:lumos 有算適用性(有 stack_questions_applicable 鍵)就只印觸發到的題;沒算(legacy)才印全表
   671	    for stk, qs in _stack_section(data).items():
   672	        lines.append(f"[{stk} 效能檢核——動手時順答這幾個問題]" if "stack_questions_applicable" not in data
   673	                     else f"[{stk} 效能檢核——這次改動觸發了這幾題,動手時順答;推送前每題要表態(lumos code-loop dispositions)]")
   674	        for q in qs:
   675	            lines.append(f"  - {q}")
   676	    if data.get("delta_truncated"):
   677	        lines.append("  (這次編輯內容超過 2 MB,效能檢核只掃了前 2 MB)")
   678	    lines.append("")
   679	    # 收尾指令只在真的列了節點時附(單 reviewer 終審 minor:僅檢核問題時
   680	    # 「判上列節點」答非所問,會弱化對提問的聚焦——檢核段標題已自帶指令)
   681	    if res or lane:
   682	        lines.append(_INJECT_INSTRUCTION)
   683	    # ★這條渲染路徑也要框★:第一版我只框了另一條,結果同一支 hook 有一半的輸出沒框
   684	    # ——是全套測試翻紅才發現的(那條測試走的正是這一條路)。
   685	    return _frame_injected("\n".join(lines))
   686	
   687	
   688	def _stack_section(data: dict) -> dict:
   689	    """要印哪些棧題:有 stack_questions_applicable 鍵(lumos 算過觸發)就用它(可能是空 {}→不印);沒有才退回全表 stack_questions。"""
   690	    if "stack_questions_applicable" in data:
   691	        return data.get("stack_questions_applicable") or {}
   692	    return data.get("stack_questions") or {}
   693	
   694	
   695	def inject_ranked_context(data: dict) -> bool:
   696	    """ranked 版注入:results/stack_questions/lane 皆空 → 不輸出(lane-only 的題也要注入,v4 Codex f2)。"""
   697	    if not data.get("results") and not _stack_section(data) and not data.get("lane"):
   698	        return False
   699	    print(json.dumps({"hookSpecificOutput": {
   700	        "hookEventName": "PreToolUse",
   701	        "additionalContext": build_ranked_context(data),
   702	    }}, ensure_ascii=False))
   703	    return True
   704	
   705	
   706	def inject_additional_context(impact_data: dict) -> None:
   707	    """非空影響集 → 印 hookSpecificOutput JSON 到 stdout;空集合 → 不輸出。
   708	
   709	    永不 block、永不改 permissionDecision。
   710	
   711	    注意 (r5-F2):此格式是 Claude Code 官方 PreToolUse additionalContext 能力。
   712	    上線後請用 `claude --debug` 實測注入時機(PreToolUse 的 additionalContext 注在
   713	    tool result 旁);若版本行為有變,可退回 stderr 備援(現有 hook 已證此路可行)。
   714	    """
   715	    direct = impact_data.get("direct", [])
   716	    indirect = impact_data.get("indirect", [])
   717	    incidents = impact_data.get("incidents", [])
   718	    if not direct and not indirect and not incidents:
   719	        return  # 空影響集(direct+indirect+incidents 皆空):不注入
   720	
   721	    ctx = build_additional_context(impact_data)
   722	    output = {
   723	        "hookSpecificOutput": {
   724	            "hookEventName": "PreToolUse",
   725	            "additionalContext": ctx,
   726	        }
   727	    }
   728	    print(json.dumps(output, ensure_ascii=False))
   729	
   730	
   731	def main() -> int:
   732	    try:
   733	        payload = json.loads(sys.stdin.read())
   734	    except json.JSONDecodeError:
   735	        return 0  # fail-open
   736	
   737	    # 只處理 Edit/Write/MultiEdit
   738	    tool_name = payload.get("tool_name", "")
   739	    if tool_name not in EDIT_TOOLS:
   740	        return 0
   741	
   742	    # repo root: 優先 $CLAUDE_PROJECT_DIR,fallback payload cwd(同 check-graph-sync.py:348-355)
   743	    # ★先算 repo 再 hook_decide★:無副檔名檔的 shebang 判定要用 repo 解相對路徑(前置修正①)
   744	    repo = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd", "")
   745	    paths, overflow = hook_decide_paths(payload, repo=repo or None)
   746	    if not paths:
   747	        return 0  # 放行:非 code 或排除路徑
   748	    if not repo:
   749	        return 0  # fail-open
   750	    lumos = _find_lumos_script()
   751	    if lumos is None:
   752	        return 0  # lumos 不在 PATH/repo → fail-open
   753	    # 多檔(Codex apply_patch):逐檔算、合併輸出;總預算 APPLY_PATCH_BUDGET_SEC,超預算後面的只列名
   754	    session_id = payload.get("session_id", "")
   755	    t0 = time.monotonic()
   756	    chunks: list[str] = []
   757	    skipped: list[str] = list(overflow)
   758	    for i, fp in enumerate(paths):
   759	        left = APPLY_PATCH_BUDGET_SEC - (time.monotonic() - t0)
   760	        if i > 0 and left < 3:
   761	            skipped.extend(paths[i:])
   762	            break
   763	        # ★翻掉「單檔固定 30 秒」那條裁定★(2026-09-07 全 repo 審視 #14)
   764	        #
   765	        # 舊裁定的理由是「逐字等價」(改寫時不動行為)。翻它的理由不是好看,是**那個數字
   766	        # 讓下面那條 fail-open 分支結構上永遠跑不到**:外層天花板也是 30 秒,內層一到
   767	        # 外面就先把整支 hook 砍掉(SIGKILL,繞過 try/except)。而那條分支裡有
   768	        # 「把冷卻窗記號清掉」——跑不到就表示:超時之後這個檔會被鎖住 20 分鐘完全不注入,
   769	        # 而且沒有人知道。一個為了 fail-open 而寫的分支,自己被 fail-closed 掉了。
   770	        #
   771	        # 現在單檔也走預算:天花板 × 0.7 減已耗,永遠明顯小於外層,逾時走自己的分支。
   772	        _cap = _inner_budget(elapsed=(time.monotonic() - t0), default=30)
   773	        tmo = _cap if len(paths) == 1 else min(_cap, max(3.0, left))
   774	        ctx = _impact_for_file(payload, repo, fp, session_id, lumos, timeout=tmo)
   775	        if ctx:
   776	            chunks.append(ctx)
   777	    if skipped:
   778	        # ★檔名也是 repo 控制的自由文字★(2026-09-07 外家審查席):它接在 builder 產物之外,
   779	        # 所以要自己消毒 + 自己框,不然這一段等於框外的裸文字。
   780	        chunks.append(_frame_injected(
   781	            "(多檔 patch 只算了前 " + str(len(paths) - len([s for s in skipped if s in paths]))
   782	            + " 檔,其餘只列名:" + ",".join(_plain_label(x, cap=80) for x in skipped[:10]) + ")"))
   783	    if not chunks or all(c.startswith("(多檔") for c in chunks):
   784	        return 0
   785	    print(json.dumps({"hookSpecificOutput": {
   786	        "hookEventName": "PreToolUse",
   787	        # 每個 chunk 各自已經框過(builder 產物 + 上面那段自己框的),接起來就是多個框並排。
   788	        # 不在這裡再包一層——會變框中框,邊界反而更難讀。
   789	        "additionalContext": "\n\n".join(chunks),   # framed-upstream
   790	    }}, ensure_ascii=False))
   791	    return 0
   792	
   793	
   794	def _impact_for_file(payload: dict, repo: str, file_path: str, session_id: str, lumos: str, timeout: float = 30.0) -> str | None:
   795	    """單檔:TTL 冷卻窗 → 叫 lumos impact → 回可注入的文字(None=不注入)。內容與舊 main 逐字等價,只是不直接 print。"""
   796	
   797	    # 絕對路徑:若 file_path 是相對路徑,補上 repo
   798	    if not Path(file_path).is_absolute():
   799	        file_path_abs = str(Path(repo) / file_path)
   800	    else:
   801	        file_path_abs = file_path
   802	
   803	    # TTL 冷卻窗:讀 .lumos/impact.json 的 ttl_min(預設 20min)
   804	    if session_id:
   805	        ttl_min = 20  # 預設
   806	        try:
   807	            impact_cfg_path = Path(repo) / ".lumos" / "impact.json"
   808	            if impact_cfg_path.is_file():
   809	                cfg = json.loads(impact_cfg_path.read_text(encoding="utf-8"))
   810	                ttl_raw = cfg.get("ttl_min", 20)
   811	                if isinstance(ttl_raw, (int, float)) and not isinstance(ttl_raw, bool):
   812	                    ttl_min = max(1, int(ttl_raw))  # m-4: 截斷兜底,防 0.5 → 0 → TTL 恆觸發
   813	        except (OSError, json.JSONDecodeError, ValueError):
   814	            pass
   815	
   816	        in_cooldown = not _ttl_should_inject(session_id, file_path_abs, ttl_sec=ttl_min * 60, mark=False)
   817	        ttl_token = _ttl_mark(session_id, file_path_abs) if not in_cooldown else None   # 判定後立刻寫(窗口同舊版);沒注入再用 token 撤
   818	    else:
   819	        in_cooldown = False
   820	        ttl_token = None
   821	
   822	    # v1.1(2026-07-11,goldset §6 全過後轉正):
   823	    # 窗外 → ranked 降噪版(固定席+top-8,delta 當查詢詞);
   824	    # 窗內 → --incidents-only 快速路(只跑事故比對——安全面每次都看,重型 BFS 降頻)。
   825	    delta_q = extract_delta_query(payload)
   826	    delta_text, delta_trunc = extract_delta_text(payload)
   827	    stdin_payload = json.dumps({"query": delta_q, "prospective": {}, "delta_text": delta_text, "delta_truncated": delta_trunc}, ensure_ascii=False)
   828	    cmd = [sys.executable, lumos, "impact", "--file", file_path_abs, "--repo", repo,
   829	           "--ranked", "--stdin-payload", "--json"]
   830	    if in_cooldown:
   831	        cmd.append("--incidents-only")
   832	    try:
   833	        result = subprocess.run(
   834	            cmd,
   835	            input=stdin_payload,
   836	            capture_output=True,
   837	            text=True,
   838	            timeout=timeout,
   839	        )
   840	    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
   841	        if session_id and not in_cooldown:
   842	            _ttl_unmark(session_id, file_path_abs, ttl_token)
   843	        return None  # fail-open
   844	
   845	    rc = result.returncode
   846	
   847	    if rc != 0 and session_id and not in_cooldown:
   848	        _ttl_unmark(session_id, file_path_abs, ttl_token)   # 沒注入不開冷卻窗
   849	    if rc == 3:
   850	        # vault 找不到 → 印一行 debug,不注入,放行
   851	        print(
   852	            f"[impact-hook] vault 未找到 (rc=3)。非圖譜專案或 --repo={repo} 路徑下無 docs/*-knowledge/。",
   853	            file=sys.stderr,
   854	        )
   855	        return None
   856	
   857	    if rc != 0:
   858	        # 其他非 0 → fail-open 純靜默
   859	        return None
   860	
   861	    # rc == 0: ranked schema {file, results, meta}
   862	    try:
   863	        impact_data = json.loads(result.stdout.strip().splitlines()[-1])
   864	    except (json.JSONDecodeError, ValueError, IndexError):
   865	        impact_data = None
   866	    if not impact_data:
   867	        if session_id and not in_cooldown:
   868	            _ttl_unmark(session_id, file_path_abs, ttl_token)
   869	        return None
   870	    # 判空與 inject_ranked_context 同一條:results/stack_questions/lane 皆空 → 不注入(lane-only 也注入)
   871	    has = impact_data.get("results") or _stack_section(impact_data) or impact_data.get("lane")
   872	    ctx = build_ranked_context(impact_data) if has else ""
   873	    if not ctx.strip():
   874	        if session_id and not in_cooldown:
   875	            _ttl_unmark(session_id, file_path_abs, ttl_token)   # 零注入不開冷卻窗(前置修正②);標記在判定當下已寫,這裡只撤
   876	        return None
   877	    return ctx
   878	
   879	
   880	if __name__ == "__main__":
   881	    # #19 S4:把「我跑完了」記成一筆事件,讓 lumos enforcement 答得出
   882	    # 「它最近有沒有真的跑過」,而不是只答「有沒有註冊」。共用寫入器在 _hookevent.py。
   883	    import sys as _s, pathlib as _p
   884	    _s.path.insert(0, str(_p.Path(__file__).resolve().parent))
   885	    try:
   886	        from _hookevent import guard as _guard
   887	    except Exception:
   888	        _guard = None
   889	    sys.exit(_guard("pretooluse-impact-hook", __file__, main) if _guard else main())

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/hooks/claude/dispatch-lens-hook.py | sed -n '1,260p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
     1	#!/usr/bin/env python3
     2	# SPDX-FileCopyrightText: 2026 Enzo Hsieh
     3	# SPDX-License-Identifier: MIT
     4	# MIT licensed. Full text: scripts/lumos header, or LICENSE at
     5	# https://github.com/EnzoHsieh-Android/Lumos
     6	"""dispatch-lens-hook — Claude Code PreToolUse(matcher Agent)薄殼(Projects/派工鏡頭注入_計劃,2026-09-03);
     7	Codex 側掛 SubagentStart(Projects/Codex完全支援_計劃 d3,2026-09-04):叫 `lumos dispatch-lens --claim` 領一席 → additionalContext。
     8	
     9	Claude 路徑只做三件事:①派工詞裡逐行找 `LUMOS-IMPACT: <base>..<head>` ②subprocess 叫 `lumos dispatch-lens`
    10	③把回傳文字接在派工詞尾端,經 updatedInput 送給子代理(additionalContext 實測到不了子代理)。
    11	其餘判斷(範圍文法、base 主線可達、消毒、快取)全在 lumos 端。
    12	永不 deny、永不改 permissionDecision;失敗一律放行。★2026-09-05 起超時不再靜默★:附一行固定超時句進派工詞(Codex 走 additionalContext);其他失敗仍靜默(LUMOS_HOOK_DEBUG=1 才印 stderr)。
    13	本檔在 ANCHOR_FILES 內:改它要 `lumos anchor approve --note`。
    14	"""
    15	from __future__ import annotations
    16	
    17	import json
    18	import os
    19	import re
    20	import subprocess
    21	import sys
    22	from pathlib import Path
    23	
    24	MARKER_RE = re.compile(r"^LUMOS-IMPACT:\s*(\S+)\s*$")
    25	SPEC_RE = re.compile(r"^LUMOS-SPEC:\s*(\S+)\s*$")   # 設計審用:給計劃筆記路徑(2026-09-05 第二輪審視 d2)
    26	# ★2026-09-07 改寫(全 repo 審視 #14)★:舊文字教人「派工前先手跑一次暖快取」——
    27	# 那件事現在機器自己做了(超時不再殺子行程,它會繼續算完寫進快取)。
    28	# ★刻意不寫「下一席大概率就有」★:那是機率宣稱,而這個專案的規矩是機率宣稱要附
    29	# 回頭看的條件、要有量測。目前沒有量過「超時後下一席命中率」,所以只講機制事實
    30	# (那支還在背景算),不講機率。
    31	# REVISIT:2026-12-07 量一次「超時之後、同範圍下一席的快取命中率」;
    32	#   命中率低就表示放手不殺沒買到東西,那時該改回殺掉或另找解法
    33	TIMEOUT_NOTE = ("LUMOS-LENS:鏡頭超時,這次沒附節點({what})。"
    34	                "算到一半的那支沒有被砍掉,它會繼續把結果算完寫進快取(20 分鐘內有效),"
    35	                "所以同一個範圍的下一席有機會直接拿到、不必再等。"
    36	                "想現在就看算不算得出來:`lumos dispatch-lens {cmd}`"
    37	                "({n} 個 commit 以上約 25 秒起)。")
    38	
    39	# ★認領席位那條路要用不同的說明★(2026-09-07 代碼審 r1 通才席抓到)
    40	# 上面那句在講「背景會把快取算完」——但認領走的是完全不同的機制:它只是從派工前
    41	# 就武裝好的檔案裡原子領一席,**全程不寫任何快取**。對這條路講快取是每次都錯,
    42	# 不是邊界情況。真正該講的是:這次沒領到,要重新武裝。
    43	# ★設計審那條路也要用不同的說明★(2026-09-07 代碼審 r2 通才席抓到)
    44	# 上面那句在講「背景會把快取算完」,但設計審模式(LUMOS-SPEC:)★本來就不快取★
    45	# (計劃常改,快取會給過期答案),所以也沒有背景暖快取這回事——超時就是這次沒有,
    46	# 下一次還是要重算。對這條路講快取是每次都錯。
    47	SPEC_TIMEOUT_NOTE = ("LUMOS-LENS:鏡頭超時,這次沒附節點({what})。"
    48	                     "★設計審這條路不快取★(計劃常改,快取會給過期答案),"
    49	                     "所以沒有背景暖快取——下一次還是要重算。"
    50	                     "想自己看算不算得出來:`lumos dispatch-lens --spec {what}`。")
    51	
    52	CLAIM_TIMEOUT_NOTE = ("LUMOS-LENS:領席超時,這次沒附節點(Codex 席:--claim)。"
    53	                      "★這條路不會有背景暖快取★——認領是從派工前武裝好的檔案裡領一席,"
    54	                      "沒領到就是沒領到。編排者:重新武裝再派 "
    55	                      "`lumos dispatch-lens --arm <base>..<head> --seats N`"
    56	                      "(--status 只看剩幾席、不重算)。")
    57	# ★2026-09-07 改成從天花板算★:原本寫死 45(外層 60 的 75%),兩邊各自演化就會漂。
    58	def _lens_timeout():
    59	    return _inner_budget(default=60)
    60	
    61	
    62	# ── ★內層逾時一律從外層天花板算出來,不寫死★ ──────────────────────────────
    63	# 單源說明在 Systems/hook逾時預算;這段在幾支 hook 裡是逐字相同的複本,有守衛盯著不准漂
    64	# (hook 是獨立檔、複製到全域後彼此 import 不到)。
    65	#
    66	# 出身(2026-09-07 全 repo 審視 #14 量出來的):外層天花板寫在註冊表、內層逾時寫在各 hook,
    67	# 兩邊各自演化。五支裡三支違反自家「外要明顯大於內」的規則,其中一支內層是外層的 2.5 倍。
    68	#
    69	# ★內層 ≥ 外層代表什麼★:內層那條「逾時就 fail-open」的分支**結構上永遠跑不到**——
    70	# 外面會先把整支 hook 砍掉(SIGKILL,繞過 try/except)。影響鏡頭那支的 fail-open 分支裡
    71	# 有「把冷卻窗記號清掉」,跑不到就表示超時之後那個檔被鎖住 20 分鐘完全不注入,而沒人知道。
    72	# **一個為了 fail-open 而寫的分支,自己被 fail-closed 掉了。**
    73	#
    74	# 現在:天花板由註冊表一處生成,用 --budget 傳進來;內層一律取「天花板 × 0.7 減掉已耗」,
    75	# 留 30% 給 hook 自己的啟動、收尾與寫輸出。拿不到 --budget(舊註冊還沒更新)就用保守預設。
    76	_BUDGET_RATIO = 0.7
    77	_BUDGET_FLOOR = 1.0          # 再怎麼扣也留 1 秒,不要算出 0 或負數
    78	_BUDGET_START = None         # 這支 hook 開始跑的時刻(第一次用到時記)
    79	
    80	
    81	def _outer_budget(default=10.0):
    82	    """從 argv 讀 --budget <秒>;沒有就回 default(保守值,不是猜大的)。
    83	    ★上限夾住★:異常大的值會讓內層跟著失控放大,等於整個 fail-open 形同虛設。"""
    84	    import sys as _s
    85	    argv = _s.argv
    86	    got = None
    87	    for i, a in enumerate(argv):
    88	        if a == "--budget" and i + 1 < len(argv):
    89	            try:
    90	                got = float(argv[i + 1])
    91	            except ValueError:
    92	                got = None
    93	            break
    94	        if a.startswith("--budget="):
    95	            try:
    96	                got = float(a.split("=", 1)[1])
    97	            except ValueError:
    98	                got = None
    99	            break
   100	    if got is None or got <= 0:
   101	        got = default
   102	    return min(float(got), 600.0)
   103	
   104	
   105	def _inner_budget(elapsed=None, default=10.0):
   106	    """內層某一段還能用幾秒:天花板 × 0.7 − 這支 hook 到目前為止已經花掉的時間,下限 1 秒。
   107	
   108	    ★已耗時間自己算,不靠呼叫端記得傳★(2026-09-07 代碼審 r1 通才席抓到):
   109	    第一版的 elapsed 預設 0,而六個呼叫點裡只有一個真的傳了值——於是同一支 hook
   110	    只要依序呼叫兩次,理論上限就是 2 × 0.7 × 外層 = 1.4 倍外層,**結構性地超過天花板**。
   111	    實測:進場提醒那支 7+7=14 秒 vs 外層 10;CI 狀態那支 10.5+10.5=21 秒 vs 外層 15。
   112	    ★這正是這批改動宣稱要修掉的問題,只是換個地方重新發生。★
   113	
   114	    ★★這是「還剩多少」不是「每段配額」★★——很容易誤解,所以講清楚:
   115	    回傳的是「從現在到預算用完還有幾秒」。所以連續呼叫兩次拿到的兩個數字**不該相加**:
   116	    第一次拿到 7 秒、真的用掉 5 秒之後,第二次會拿到 2 秒。
   117	    只有在「第一段其實沒用多久」時第二次才會拿到接近 7 秒——那也是對的,因為時間真的還在。
   118	    ★守衛要驗的是「真的用掉時間之後,下一次拿到的會變少,而且總和不超過天花板」★,
   119	    不是「兩次的數字相加小於天花板」(那個判準本身就錯,會逼出錯誤的修法)。
   120	
   121	    ★誠實邊界★:天花板小於約 1.43 秒時,下限 1 秒會反過來大於外層。目前註冊表最小值是 10,
   122	    離這個門檻很遠;真要調到那麼小的話這個假設就不成立了。
   123	    """
   124	    import time as _tm
   125	    global _BUDGET_START
   126	    if _BUDGET_START is None:
   127	        _BUDGET_START = _tm.monotonic()
   128	    used = (_tm.monotonic() - _BUDGET_START) if elapsed is None else float(elapsed)
   129	    return max(_BUDGET_FLOOR, _outer_budget(default) * _BUDGET_RATIO - used)
   130	# ── ★逾時預算結束★ ──────────────────────────────────────────────────
   131	
   132	def _debug(msg: str) -> None:
   133	    if os.environ.get("LUMOS_HOOK_DEBUG"):
   134	        print(f"[dispatch-lens-hook] {msg}", file=sys.stderr)
   135	
   136	
   137	def find_marker(prompt: str) -> str | None:
   138	    for line in prompt.split("\n"):
   139	        m = MARKER_RE.match(line.strip())
   140	        if m:
   141	            return m.group(1)
   142	    return None
   143	
   144	
   145	def find_spec_marker(prompt: str) -> str | None:
   146	    for line in prompt.split("\n"):
   147	        m = SPEC_RE.match(line.strip())
   148	        if m:
   149	            return m.group(1)
   150	    return None
   151	
   152	
   153	def _emit_updated(tool_input: dict, prompt: str, text: str) -> None:
   154	    new_input = dict(tool_input)
   155	    new_input["prompt"] = prompt.rstrip("\n") + "\n\n" + text + "\n"
   156	    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": new_input}}, ensure_ascii=False))
   157	
   158	
   159	# ── ★只執行「可信來源」的 lumos,絕不執行被打開那個資料夾裡的碼★ ──────────────
   160	# 單源說明在 Systems/hook信任邊界;這段在幾支 hook 裡是逐字相同的複本,
   161	# 有守衛測試盯著不准漂(hook 是獨立檔、複製到 ~/.claude/hooks 後彼此 import 不到,
   162	# 所以用「複製 + 守衛」而不是抽共用模組)。
   163	#
   164	# 出身(2026-09-06 實地重現):這支 hook 原本執行的是 `<被打開的資料夾>/scripts/lumos`,
   165	# 唯一判準是那個資料夾有 docs/*-knowledge。**clone 一個陌生 repo、開一下 Claude,
   166	# 對方的 python 就在你機器上跑了**——而且因為是拿 python 去執行它,
   167	# 那個檔連執行權限都不需要。
   168	#
   169	# 解析順序:系統裝好的 → $LUMOS_HOME 指的 → 預設來源位置 → 都沒有就回 None。
   170	# 回 None 時呼叫端要靜默跳過那段功能(這套本來就是 fail-open:寧可少一層提醒,
   171	# 不可執行不該信任的碼)。
   172	#
   173	# ★2026-09-07 外家審查席補的一刀★:光是「從 PATH 或 $LUMOS_HOME 找到」不算可信——
   174	# 那兩個都是繼承來的環境值,workspace-local 的 bin(direnv / node_modules/.bin 之類)
   175	# 一進專案就可能改掉 PATH。所以找到之後還要驗那個檔本身:不是 symlink 指到別處、
   176	# 是自己的、group/other 不可寫。
   177	# ★誠實邊界★:完全控制你 PATH 的人本來就能在你帳號下跑任何東西,這條擋不住那種;
   178	# 它擋的是「專案順手塞一個 bin 進 PATH」與「別人可寫的目錄裡放一支同名的」。
   179	def _trusted_lumos():
   180	    import shutil as _sh, os as _os, stat as _st
   181	    from pathlib import Path as _P
   182	
   183	    def _ok(cand):
   184	        try:
   185	            p = _P(cand)
   186	            if not p.is_file():
   187	                return None
   188	            st = p.stat()
   189	            if hasattr(_os, "getuid") and st.st_uid != _os.getuid():
   190	                return None          # 不是自己的檔
   191	            if st.st_mode & (_st.S_IWGRP | _st.S_IWOTH):
   192	                return None          # 別人可寫 = 別人可換內容
   193	            par = p.parent.stat()
   194	            if hasattr(_os, "getuid") and par.st_uid != _os.getuid():
   195	                return None          # 放在別人的目錄裡
   196	            if par.st_mode & (_st.S_IWGRP | _st.S_IWOTH):
   197	                return None          # 目錄別人可寫 = 可被換掉
   198	            return str(p)
   199	        except OSError:
   200	            return None
   201	
   202	    found = _sh.which("lumos")
   203	    if found:
   204	        good = _ok(found)
   205	        if good:
   206	            return good
   207	    for base in (_os.environ.get("LUMOS_HOME"), str(_P.home() / "harness" / "lumos-toolchain")):
   208	        if not base:
   209	            continue
   210	        good = _ok(_P(base) / "scripts" / "lumos")
   211	        if good:
   212	            return good
   213	    return None
   214	# ── ★可信來源解析結束★ ────────────────────────────────────────────────
   215	
   216	def _find_lumos_script() -> str | None:
   217	    """★2026-09-07 外家審查席抓到:這支是第四支,前一批漏了★
   218	    原本 which 找不到就退回「這支 hook 檔往上四層」的 scripts/lumos——這支 hook 會被複製進
   219	    消費專案,那時往上四層正好是**消費專案自己的根**,等於又回到「執行手邊資料夾的碼」。
   220	    前一批只改了三支、測試也只掃那三支,所以沒抓到。現在改用共用的可信來源解析。"""
   221	    return _trusted_lumos()
   222	
   223	
   224	
   225	
   226	
   227	def _claim_codex_seat(payload: dict) -> int:
   228	    """Codex 側(SubagentStart):派工訊息對 hook 是密文、改不了(實驗 A),改由 `lumos dispatch-lens --claim`
   229	    從派工前武裝的 armed 檔原子領一席,經 additionalContext 給子代理(實驗 5 證到得了)。
   230	    沒武裝/過期/領完 → 什麼都不回(lumos 端判,這裡只轉送)。"""
   231	    repo = payload.get("cwd", "") or os.environ.get("CLAUDE_PROJECT_DIR", "")
   232	    if not repo:
   233	        _debug("Codex SubagentStart 沒有 cwd,放行")
   234	        return 0
   235	    lumos = _find_lumos_script()
   236	    if lumos is None:
   237	        _debug("找不到 lumos,放行")
   238	        return 0
   239	    # ★薄殼★:叫 lumos、等它、拿結果。超時之後怎麼辦是 lumos 那邊的事
   240	    #   (2026-09-07 代碼審 r1 架構席:hook 只做三件事,其餘住 lumos 子命令)。
   241	    try:
   242	        r = subprocess.run([sys.executable, lumos, "dispatch-lens", "--claim", "--repo", repo, "--json"],
   243	                           capture_output=True, text=True, timeout=_lens_timeout())
   244	    except (subprocess.TimeoutExpired, OSError):
   245	        r = None
   246	    if r is None or r.returncode == 5:
   247	        # 架構 r1 C:與 Claude 分支同語意——超時不再靜默,經 additionalContext 給一行固定說明
   248	        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": _frame_injected(CLAIM_TIMEOUT_NOTE)}}, ensure_ascii=False))
   249	        _debug("lumos dispatch-lens --claim 超時,已附超時說明(這條路沒有背景暖快取)")
   250	        return 0
   251	
   252	    if r.returncode != 0:
   253	        _debug(f"lumos dispatch-lens --claim rc={r.returncode}:{r.stderr.strip()[:200]},放行")
   254	        return 0
   255	    try:
   256	        data = json.loads(r.stdout.strip().splitlines()[-1])
   257	    except (ValueError, IndexError):
   258	        _debug("--claim 回傳讀不懂,放行")
   259	        return 0
   260	    text = data.get("text") if isinstance(data, dict) else None

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "rg -n \"impact-hook|dispatch-lens-hook|build_ranked_context|LUMOS_IMPACT_HOOK|PreToolUse|codex\" scripts/hooks scripts -g '*.py' -g '*.sh' -g '*.json' | head -n 300"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
scripts/hooks/claude/impact-hook.py:6:"""PreToolUse hook: 主動影響幅度偵測 (Task 10 — TTL 冷卻窗)
scripts/hooks/claude/impact-hook.py:455:    # 每段獨立配額(codex r1+r2 折入):先串接再整體截斷會讓「超長 old_string」吃掉整段 new;
scripts/hooks/claude/impact-hook.py:630:def build_ranked_context(data: dict) -> str:
scripts/hooks/claude/impact-hook.py:700:        "hookEventName": "PreToolUse",
scripts/hooks/claude/impact-hook.py:701:        "additionalContext": build_ranked_context(data),
scripts/hooks/claude/impact-hook.py:711:    注意 (r5-F2):此格式是 Claude Code 官方 PreToolUse additionalContext 能力。
scripts/hooks/claude/impact-hook.py:712:    上線後請用 `claude --debug` 實測注入時機(PreToolUse 的 additionalContext 注在
scripts/hooks/claude/impact-hook.py:724:            "hookEventName": "PreToolUse",
scripts/hooks/claude/impact-hook.py:786:        "hookEventName": "PreToolUse",
scripts/hooks/claude/impact-hook.py:852:            f"[impact-hook] vault 未找到 (rc=3)。非圖譜專案或 --repo={repo} 路徑下無 docs/*-knowledge/。",
scripts/hooks/claude/impact-hook.py:872:    ctx = build_ranked_context(impact_data) if has else ""
scripts/hooks/claude/impact-hook.py:889:    sys.exit(_guard("pretooluse-impact-hook", __file__, main) if _guard else main())
scripts/hooks/claude/ci-status-hook.py:16:- **輸出契約宣告 SessionStart**（不可照抄 PreToolUse hook 的硬編事件名，否則注入被丟棄）。
scripts/hooks/claude/impact-hook.py:6:"""PreToolUse hook: 主動影響幅度偵測 (Task 10 — TTL 冷卻窗)
scripts/hooks/claude/impact-hook.py:455:    # 每段獨立配額(codex r1+r2 折入):先串接再整體截斷會讓「超長 old_string」吃掉整段 new;
scripts/hooks/claude/impact-hook.py:630:def build_ranked_context(data: dict) -> str:
scripts/hooks/claude/impact-hook.py:700:        "hookEventName": "PreToolUse",
scripts/hooks/claude/impact-hook.py:701:        "additionalContext": build_ranked_context(data),
scripts/hooks/claude/impact-hook.py:711:    注意 (r5-F2):此格式是 Claude Code 官方 PreToolUse additionalContext 能力。
scripts/hooks/claude/impact-hook.py:712:    上線後請用 `claude --debug` 實測注入時機(PreToolUse 的 additionalContext 注在
scripts/hooks/claude/impact-hook.py:724:            "hookEventName": "PreToolUse",
scripts/hooks/claude/impact-hook.py:786:        "hookEventName": "PreToolUse",
scripts/hooks/claude/impact-hook.py:852:            f"[impact-hook] vault 未找到 (rc=3)。非圖譜專案或 --repo={repo} 路徑下無 docs/*-knowledge/。",
scripts/hooks/claude/impact-hook.py:872:    ctx = build_ranked_context(impact_data) if has else ""
scripts/hooks/claude/impact-hook.py:889:    sys.exit(_guard("pretooluse-impact-hook", __file__, main) if _guard else main())
scripts/hooks/claude/dispatch-lens-hook.py:6:"""dispatch-lens-hook — Claude Code PreToolUse(matcher Agent)薄殼(Projects/派工鏡頭注入_計劃,2026-09-03);
scripts/hooks/claude/dispatch-lens-hook.py:134:        print(f"[dispatch-lens-hook] {msg}", file=sys.stderr)
scripts/hooks/claude/dispatch-lens-hook.py:156:    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": new_input}}, ensure_ascii=False))
scripts/hooks/claude/dispatch-lens-hook.py:227:def _claim_codex_seat(payload: dict) -> int:
scripts/hooks/claude/dispatch-lens-hook.py:280:        return _claim_codex_seat(payload)
scripts/hooks/claude/dispatch-lens-hook.py:370:    sys.exit(_guard("pretooluse-dispatch-lens-hook", __file__, main) if _guard else main())
scripts/hooks/claude/check-graph-sync.py:11:  Claude Code 官方文件:exit 0 的 stderr 模型看不到;Codex 亦然)。--harness codex 只影響逐字稿怎麼讀。
scripts/hooks/claude/check-graph-sync.py:118:# key 有引號 {"cmd":"…"} 與沒引號 {cmd:"…"}(含換行縮排)兩種都出現(2026-09-04 當日逐字稿 31:30;code-codex-s1 r1 外家 #2)
scripts/hooks/claude/check-graph-sync.py:133:def _is_codex_transcript(first_obj: dict) -> bool:
scripts/hooks/claude/check-graph-sync.py:137:def collect_codex_turn_actions(lines: list[str]):
scripts/hooks/claude/check-graph-sync.py:199:    回傳 (file_paths, bash_commands)。Codex 逐字稿(第一行 session_meta)走 collect_codex_turn_actions。
scripts/hooks/claude/check-graph-sync.py:209:    if _is_codex_transcript(first_obj):
scripts/hooks/claude/check-graph-sync.py:210:        return collect_codex_turn_actions(lines)
scripts/hooks/claude/check-graph-sync.py:591:    取「固定席未動」的前 cap 篇。lumos 尋路同 impact-hook._find_lumos_script 的順序(PATH 先、repo 後);
scripts/hooks/claude/check-graph-sync.py:619:    """標記目錄:mkdir(0700)後★先過 _stop_dir_ok 再做任何 chmod/清理★(code-codex-refine r2 外家:目錄若被換成指向別處的 symlink,
scripts/hooks/claude/check-graph-sync.py:666:    ★名額先佔再擋(code-codex-refine r1 外家 #1/#4):回 True 表示標記檔已用 O_EXCL 建成——建不成(已存在 / 目錄寫不進 / 唯讀檔案系統)
scripts/hooks/claude/check-graph-sync.py:724:    harness = "codex" if "--harness" in sys.argv and sys.argv[sys.argv.index("--harness") + 1:][:1] == ["codex"] else "claude"
scripts/scenario_probe.py:27:def tool_calls_from_codex_json(lines):
scripts/scenario_probe.py:28:    """codex exec --json → [(tool_name, 摘要字串)] 依時間序(Projects/Codex完全支援_計劃 S3)。
scripts/scenario_probe.py:231:def _codex_home_dir():
scripts/scenario_probe.py:232:    """Codex 家目錄一律問 scripts/lumos 的 _codex_home()(單源;code-codex-refine r1 架構 #2:別再第二套算 CODEX_HOME)。"""
scripts/scenario_probe.py:239:        return mod._codex_home()
scripts/scenario_probe.py:243:        return Path(env).expanduser() if env else Path.home() / ".codex"
scripts/scenario_probe.py:250:def _codex_hook_trace(thread_id):
scripts/scenario_probe.py:257:    hits = sorted(_codex_home_dir().glob(f"sessions/*/*/*/rollout-*-{thread_id}.jsonl"), key=lambda q: q.stat().st_mtime)
scripts/scenario_probe.py:279:def run_one_codex(sc, workdir, timeout, model, arm="with", stop_block="on", bypass_trust=False):
scripts/scenario_probe.py:280:    """Codex 版 runner:`codex exec --json -C <沙盒> --sandbox workspace-write <prompt>`。
scripts/scenario_probe.py:282:    --codex-bypass-hook-trust 只給隔離環境。stop_block=off 設 LUMOS_STOP_BLOCK_OFF=1 關掉 Codex 收工擋停(對照組)。
scripts/scenario_probe.py:283:    模型由 codex 設定決定(-m 可覆寫);用量上限偵測 Codex 側沒對應訊號,limit_hit 恆 False 並在 result_subtype 標 codex。"""
scripts/scenario_probe.py:288:                "limit_hit": False, "result_subtype": "codex", "harness": "codex"}
scripts/scenario_probe.py:289:    # stdin 必重導向 DEVNULL:codex exec 沒有 tty 時會等 stdin(2026-08-23 外家席實測「stdin 要重導否則掛住」)
scripts/scenario_probe.py:290:    cmd = ["codex", "exec", "--json", "--sandbox", "workspace-write", "-C", str(workdir)]
scripts/scenario_probe.py:302:    instrument_fail = None   # 超時 / 非零退出 = 儀器例外,這場不算分(code-codex-s3 r1 外家 #3:半途已印期望指令也不能判過)
scripts/scenario_probe.py:307:            instrument_fail = f"codex exec 退出碼 {r.returncode}"
scripts/scenario_probe.py:310:        err = "timeout"; instrument_fail = f"codex exec 超時 {timeout}s"
scripts/scenario_probe.py:311:    calls, final = tool_calls_from_codex_json(out.splitlines())
scripts/scenario_probe.py:320:    trace = _codex_hook_trace(thread_id)
scripts/scenario_probe.py:334:            "answer_content_ok": answer_content_ok, "limit_hit": False, "result_subtype": "codex", "harness": "codex",
scripts/scenario_probe.py:340:    ★只影響 claude runner:codex exec 沒有 --max-turns 這種旗標,codex runner 忽略此欄(外家 r1 m3,誠實寫在這裡與 --help)。★"""
scripts/scenario_probe.py:437:    ap.add_argument("--max-turns", type=int, default=18, help="claude runner 的回合上限(每題可用 max_turns 欄覆寫;codex runner 沒有對應旗標、忽略此值)")
scripts/scenario_probe.py:450:    ap.add_argument("--runner", choices=["claude", "codex"], default="claude",
scripts/scenario_probe.py:451:                    help="被測的 harness:claude=claude -p(預設);codex=codex exec --json(S3;模型由 codex 設定決定,-m 可覆寫)")
scripts/scenario_probe.py:453:                    help="codex runner:off=設 LUMOS_STOP_BLOCK_OFF=1 關掉收工擋停(對照組;Projects/Codex行為精修_計劃)")
scripts/scenario_probe.py:454:    ap.add_argument("--codex-bypass-hook-trust", action="store_true",
scripts/scenario_probe.py:455:                    help="codex runner 帶 --dangerously-bypass-hook-trust(★只准隔離環境★;本機審過信任不需要)")
scripts/scenario_probe.py:498:                        res = (run_one_codex(sc, work, a.timeout, a.model, a.arm, a.stop_block, a.codex_bypass_hook_trust) if a.runner == "codex"
scripts/hooks/claude/ci-status-hook.py:16:- **輸出契約宣告 SessionStart**（不可照抄 PreToolUse hook 的硬編事件名，否則注入被丟棄）。
scripts/hooks/claude/check-graph-sync.py:11:  Claude Code 官方文件:exit 0 的 stderr 模型看不到;Codex 亦然)。--harness codex 只影響逐字稿怎麼讀。
scripts/hooks/claude/check-graph-sync.py:118:# key 有引號 {"cmd":"…"} 與沒引號 {cmd:"…"}(含換行縮排)兩種都出現(2026-09-04 當日逐字稿 31:30;code-codex-s1 r1 外家 #2)
scripts/hooks/claude/check-graph-sync.py:133:def _is_codex_transcript(first_obj: dict) -> bool:
scripts/hooks/claude/check-graph-sync.py:137:def collect_codex_turn_actions(lines: list[str]):
scripts/hooks/claude/check-graph-sync.py:199:    回傳 (file_paths, bash_commands)。Codex 逐字稿(第一行 session_meta)走 collect_codex_turn_actions。
scripts/hooks/claude/check-graph-sync.py:209:    if _is_codex_transcript(first_obj):
scripts/hooks/claude/check-graph-sync.py:210:        return collect_codex_turn_actions(lines)
scripts/hooks/claude/check-graph-sync.py:591:    取「固定席未動」的前 cap 篇。lumos 尋路同 impact-hook._find_lumos_script 的順序(PATH 先、repo 後);
scripts/hooks/claude/check-graph-sync.py:619:    """標記目錄:mkdir(0700)後★先過 _stop_dir_ok 再做任何 chmod/清理★(code-codex-refine r2 外家:目錄若被換成指向別處的 symlink,
scripts/hooks/claude/check-graph-sync.py:666:    ★名額先佔再擋(code-codex-refine r1 外家 #1/#4):回 True 表示標記檔已用 O_EXCL 建成——建不成(已存在 / 目錄寫不進 / 唯讀檔案系統)
scripts/hooks/claude/check-graph-sync.py:724:    harness = "codex" if "--harness" in sys.argv and sys.argv[sys.argv.index("--harness") + 1:][:1] == ["codex"] else "claude"
scripts/hooks/claude/dispatch-lens-hook.py:6:"""dispatch-lens-hook — Claude Code PreToolUse(matcher Agent)薄殼(Projects/派工鏡頭注入_計劃,2026-09-03);
scripts/hooks/claude/dispatch-lens-hook.py:134:        print(f"[dispatch-lens-hook] {msg}", file=sys.stderr)
scripts/hooks/claude/dispatch-lens-hook.py:156:    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": new_input}}, ensure_ascii=False))
scripts/hooks/claude/dispatch-lens-hook.py:227:def _claim_codex_seat(payload: dict) -> int:
scripts/hooks/claude/dispatch-lens-hook.py:280:        return _claim_codex_seat(payload)
scripts/hooks/claude/dispatch-lens-hook.py:370:    sys.exit(_guard("pretooluse-dispatch-lens-hook", __file__, main) if _guard else main())
scripts/merge-claude-settings.py:19:# Claude Code:~/.claude/settings.json 的 hooks 段;Codex CLI:~/.codex/hooks.json 頂層 hooks 段。
scripts/merge-claude-settings.py:21:# matcher 名、payload 形狀、輸出欄位各自查(r1 外家 F2)。★不碰 ~/.codex/config.toml★(stdlib 無 TOML 寫入器)。
scripts/merge-claude-settings.py:23:    """--target claude|codex(預設 claude);值拼錯或缺值 → 擋下(r1 外家 #6:靜默退回 claude 會改錯檔)。"""
scripts/merge-claude-settings.py:33:    if val not in ("claude", "codex"):
scripts/merge-claude-settings.py:34:        print(f"擋下:--target 只能是 claude 或 codex,給的是 {val!r};沒動任何檔", file=sys.stderr)
scripts/merge-claude-settings.py:41:_CODEX_HOME = Path(__import__("os").environ.get("CODEX_HOME") or (Path.home() / ".codex")).expanduser()
scripts/merge-claude-settings.py:42:if TARGET == "codex":
scripts/merge-claude-settings.py:71:    "impact-hook.py": 30,
scripts/merge-claude-settings.py:72:    "dispatch-lens-hook.py": 60,
scripts/merge-claude-settings.py:87:    # Codex 目標:命令列帶明確 --harness codex(d2:hook 靠旗標分支,不由 payload 欄位猜家族;
scripts/merge-claude-settings.py:89:    if TARGET == "codex":
scripts/merge-claude-settings.py:90:        # 絕對路徑(不是 ${HOME}/.codex):CODEX_HOME 可以不在 HOME 底下
scripts/merge-claude-settings.py:95:        return (f'{py} "{hooks_dir}/{rel_path}" --harness codex{_bf}' if sys.platform != "win32"
scripts/merge-claude-settings.py:96:                else f'"{py}" "{hooks_dir}/{rel_path}" --harness codex{_bf}')
scripts/merge-claude-settings.py:135:    "PreToolUse": [
scripts/merge-claude-settings.py:139:            # 生產實測:用 `claude --debug` 驗 PreToolUse additionalContext 注入時機;
scripts/merge-claude-settings.py:146:                    "command": _hook_cmd("impact-hook.py"),
scripts/merge-claude-settings.py:147:                    "timeout": HOOK_BUDGET["impact-hook.py"],
scripts/merge-claude-settings.py:156:            # 外層 60 > 內層 45(dispatch-lens-hook.py INNER_TIMEOUT)。
scripts/merge-claude-settings.py:161:                    "command": _hook_cmd("dispatch-lens-hook.py"),
scripts/merge-claude-settings.py:162:                    "timeout": HOOK_BUDGET["dispatch-lens-hook.py"],
scripts/merge-claude-settings.py:188:def _codex_entries(entries: dict) -> dict:
scripts/merge-claude-settings.py:191:    · PreToolUse `Edit|Write|MultiEdit` → matcher `apply_patch`(Codex 改檔工具;Edit/Write 只是它的別名,
scripts/merge-claude-settings.py:192:      tool_name 仍回 apply_patch;tool_input 是 patch 全文沒有 file_path——S1 適配 impact-hook)。
scripts/merge-claude-settings.py:193:    · PreToolUse `Agent`(派工鏡頭)→ 改掛 `SubagentStart`(無 matcher):spawn_agent 的 message 對 hook
scripts/merge-claude-settings.py:201:            if event == "PreToolUse" and e.get("matcher") == "Edit|Write|MultiEdit":
scripts/merge-claude-settings.py:203:            elif event == "PreToolUse" and e.get("matcher") == "Agent":
scripts/merge-claude-settings.py:210:if TARGET == "codex":
scripts/merge-claude-settings.py:211:    HOOK_ENTRIES = _codex_entries(HOOK_ENTRIES)
scripts/merge-claude-settings.py:221:        if not isinstance(entries, list):      # schema 錯(值不是陣列)→ 當空,別炸(code-codex-s0 r1 F3)
scripts/test_lumos.py:373:    # CODEX_HOME 若沒清掉,會繞過假家目錄直接打到真的 ~/.codex
scripts/test_lumos.py:529:    for h in ("check-graph-sync.py", "impact-hook.py"):   # rot-check 2026-08-21 撤除
scripts/test_lumos.py:1206:    rs = run(v, "set", "Systems/A", "about_code_stamp", "codex/2026-08-23")
scripts/test_lumos.py:3167:         "severity": "blocker", "findings": 2, "auditor": "codex", "note": "std"},
scripts/test_lumos.py:3180:    check("增量帳: 分審計員(codex 2/sonnet 4)",
scripts/test_lumos.py:3181:          "codex 2" in r.stdout and "sonnet 4" in r.stdout, r.stdout[-500:])
scripts/test_lumos.py:3211:                               "scripts/hooks/claude/impact-hook.py"])
scripts/test_lumos.py:4753:        {"seat": "ext", "auditor": "codex"}]}))
scripts/test_lumos.py:6241:    "git", "gh", "codex", "claude", "python3", "python", "bash", "sh", "sed", "grep",
scripts/test_lumos.py:6274:    "git", "gh", "codex", "claude", "python3", "python", "bash", "sh", "sed", "grep",
scripts/test_lumos.py:7598:    check-graph-sync.py/impact-hook.py 的 CODE_EXTS),零漂移守衛,且全部漏 .sh——當天
scripts/test_lumos.py:7613:        "impact-hook.py": py_set(root / "hooks" / "claude" / "impact-hook.py"),
scripts/test_lumos.py:7633:    cgs = _load_hook_mod("cgs_sheb", "check-graph-sync.py"); imp = _load_hook_mod("imp_sheb", "impact-hook.py")
scripts/test_lumos.py:7636:        check(f"code-exts: impact-hook 對 {name} 判 {want}", imp._shebang_is_code(d / name) is want, "")
scripts/test_lumos.py:7640:    for k in ("claude/check-graph-sync.py", "claude/impact-hook.py"):
scripts/test_lumos.py:8339:    """造一個假 Lumos 來源:scripts/hooks(claude/impact-hook.py+pre-commit)+scripts/templates/graph-discipline.md。"""
scripts/test_lumos.py:8344:    (src / "scripts" / "hooks" / "claude" / "impact-hook.py").write_text("#lumos\n")
scripts/test_lumos.py:8390:    (tgt / "scripts" / "hooks" / "claude" / "impact-hook.py").write_text("#lumos\n")
scripts/test_lumos.py:8398:          not (tgt / "scripts" / "hooks" / "claude" / "impact-hook.py").exists())
scripts/test_lumos.py:9640:    for rel in ("scripts/lumos", "scripts/test_lumos.py", "scripts/hooks/claude/impact-hook.py"):
scripts/test_lumos.py:9662:    (root / "scripts" / "hooks" / "claude" / "impact-hook.py").write_text("def f():\n    fh = open('edited.txt')\n", encoding="utf-8")
scripts/test_lumos.py:9667:          any(c["file"] == "scripts/hooks/claude/impact-hook.py" for c in d["claims"]), str(d["claims"])[:400])
scripts/test_lumos.py:9703:    (root2 / "scripts" / "hooks" / "claude" / "impact-hook.py").write_text("def h():\n    fh = open('v')\n", encoding="utf-8")
scripts/test_lumos.py:9713:          "scripts/hooks/claude/impact-hook.py" not in files, str(files))
scripts/test_lumos.py:11859:    """Task 9: impact-hook 過濾 + tool_input.file_path 巢狀讀取 + rc 處理。
scripts/test_lumos.py:11861:    測試對象是 scripts/hooks/claude/impact-hook.py 的可 import 函式:
scripts/test_lumos.py:11867:    hook_path = str(Path(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
scripts/test_lumos.py:11917:    """v1.1:extract_delta_query 三工具抽取+cap;build_ranked_context 降噪格式。"""
scripts/test_lumos.py:11919:    hook_path = str(Path(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
scripts/test_lumos.py:11931:    check("delta: 每段獨立配額(超長 old 不吃掉 new——codex r1 反例)", "HOOK_ENTRIES" in q, str(len(q)))
scripts/test_lumos.py:11937:    ctx = m.build_ranked_context({"results": [
scripts/test_lumos.py:11944:    ctx9 = m.build_ranked_context({"results": [
scripts/test_lumos.py:11951:    ctx_lane = m.build_ranked_context({"results": [{"node": "Systems/Y.md", "kind": "direct", "pinned": False, "score": 0.9}],
scripts/test_lumos.py:11955:    ctx_nolane = m.build_ranked_context({"results": [{"node": "Systems/Y.md", "kind": "direct", "pinned": False, "score": 0.9}], "meta": {}})
scripts/test_lumos.py:11967:    測試對象是 scripts/hooks/claude/impact-hook.py 的:
scripts/test_lumos.py:11978:    hook_path = str(_P(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
scripts/test_lumos.py:12064:    測試對象是 scripts/hooks/claude/impact-hook.py 的:
scripts/test_lumos.py:12081:    hook_path = str(_P(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
scripts/test_lumos.py:12106:    check("impact_hook_inject: hookSpecificOutput.hookEventName == PreToolUse",
scripts/test_lumos.py:12107:          j["hookSpecificOutput"]["hookEventName"] == "PreToolUse",
scripts/test_lumos.py:12224:    check("impact_hook_inject: main() hookSpecificOutput.hookEventName == PreToolUse",
scripts/test_lumos.py:12225:          j_main.get("hookSpecificOutput", {}).get("hookEventName") == "PreToolUse",
scripts/test_lumos.py:12245:    hook_path = str(_P(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
scripts/test_lumos.py:12335:    安裝後 hook 複製到 ~/.claude/hooks/impact-hook.py,repo-relative 猜測
scripts/test_lumos.py:12345:    hook_path = str(Path(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
scripts/test_lumos.py:12418:    """Task 12 hook 註冊:驗 merge-claude-settings.py 的 HOOK_ENTRIES 源碼含 PreToolUse impact-hook.py 條目。
scripts/test_lumos.py:12429:    entries = mcs.HOOK_ENTRIES.get("PreToolUse", [])
scripts/test_lumos.py:12431:        "impact-hook.py" in h.get("command", "")
scripts/test_lumos.py:12435:    check("impact_hook_registration_source: HOOK_ENTRIES PreToolUse 含 impact-hook.py",
scripts/test_lumos.py:12744:    hook_path = str(_P(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
scripts/test_lumos.py:13370:    # (dispatch-lens-hook.py)還在退回執行專案自己的碼,而測試看不到它——
scripts/test_lumos.py:13580:    (pyc_dir / "impact-hook.cpython-314.pyc").write_text("x", encoding="utf-8")
scripts/test_lumos.py:13689:    files = [hooks_dir / f for f in ("impact-hook.py", "ci-status-hook.py",
scripts/test_lumos.py:13690:                                     "lumos-entry-hook.py", "dispatch-lens-hook.py")]
scripts/test_lumos.py:13794:    f = hooks_dir / "impact-hook.py"
scripts/test_lumos.py:13913:    hook_src = (Path(GRAPHCTL).resolve().parent / "hooks" / "claude" / "dispatch-lens-hook.py").read_text(encoding="utf-8")
scripts/test_lumos.py:17494:    run(v, "canary", "second", "--id", tok, "--verdict", "overturn", "--auditor", "codex")
scripts/test_lumos.py:17511:    r = run(v, "canary", "second", "--id", tok3, "--verdict", "agree", "--auditor", "codex")
scripts/test_lumos.py:18133:    """★2026-08-03 code-loop r2(codex minor / seatA major,依規矩取高)★:
scripts/test_lumos.py:19331:    # --top 限量;預設 0=全量(r2 codex:前輪截斷 blocker 的回歸鎖)
scripts/test_lumos.py:20262:    hook_path = str(_P(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
scripts/test_lumos.py:20271:    txt = m.build_ranked_context(data)
scripts/test_lumos.py:20279:    txt_with_nodes = m.build_ranked_context(
scripts/test_lumos.py:21551:    r = run(v, "loop", "next", f"nx-{_M1U}", "--orchestrator", "claude")   # S2:orchestrator 守衛先擋,補旗標才測得到 tier 守衛(code-codex-s2 r1 外家 #5)
scripts/test_lumos.py:22155:    check("hook 輸出契約宣告 SessionStart(非抄 PreToolUse)",
scripts/test_lumos.py:26038:          "labels": {"S01": {"Systems/Beta.md": {"final": 1, "claude": 1, "codex": 1}},
scripts/test_lumos.py:26039:                     "E01": {"Systems/Alpha.md": {"final": 0, "claude": 0, "codex": 0}}}}
scripts/test_lumos.py:26422:    gs["labels"]["E01"] = {"Systems/Alpha.md": {"final": 2, "claude": 2, "codex": 2}, "Systems/Hub.md": {"final": 1, "claude": 1, "codex": 1}}
scripts/test_lumos.py:26453:    gs["labels"]["E01"] = {"Systems/Alpha.md": {"final": 2, "claude": 2, "codex": 2}, "Systems/Lane.md": {"final": 2, "claude": 2, "codex": 2}}
scripts/test_lumos.py:26535:          gs2["labels"]["S01"]["Systems/Beta.md"] == {"final": 1, "claude": 1, "codex": 1}, str(gs2["labels"]["S01"]))
scripts/test_lumos.py:26747:          gs_after["labels"]["S01"]["Systems/Beta.md"] == {"final": 1, "claude": 1, "codex": 1}, "")
scripts/test_lumos.py:27016:                 "PreToolUse": ["impact-hook.py"], "Stop": ["check-graph-sync.py"]}
scripts/test_lumos.py:27020:                       "impact-hook.py": "pretooluse-impact-hook",
scripts/test_lumos.py:27022:                       "dispatch-lens-hook.py": "pretooluse-dispatch-lens-hook"}
scripts/test_lumos.py:27025:            if ev == "PreToolUse":
scripts/test_lumos.py:27057:    check("enforcement: impact hook active", by.get("pretooluse-impact-hook") == "active", str(by))
scripts/test_lumos.py:27073:    for _layer in ("session-entry-hook", "pretooluse-impact-hook",
scripts/test_lumos.py:27185:    # 2026-09-04 Codex完全支援 S0:fixture 的 home 沒有 ~/.codex → Codex 八列(5 hook+cli+skills+agents-md)
scripts/test_lumos.py:27187:    codex_layers = ["agents-md", "codex-agent", "codex-cli", "codex-sessionstart-ci-status-hook", "codex-subagentstart-dispatch-lens-hook", "codex-session-entry-hook",
scripts/test_lumos.py:27188:                    "codex-stop-graph-sync-hook", "codex-pretooluse-impact-hook", "codex-skills"]
scripts/test_lumos.py:27189:    check("enforcement: unknown 恰=vendored+遠端+Codex 不適用八列", unknown_layers == sorted(["required-status-check", "vendored-cli"] + codex_layers), str(unknown_layers))
scripts/test_lumos.py:27201:    # 2026-09-04 Codex完全支援 S0 加 9 列:codex-hook×5+codex-cli+claude-skills+codex-skills+agents-md = 21)
scripts/test_lumos.py:27202:    check("enforcement: 缺目錄不炸、回恰 22 列(d6 加 codex-agent)", isinstance(rows, list) and len(rows) == 22, f"{len(rows)}: {[r['layer'] for r in rows]}")
scripts/test_lumos.py:27228:    既有的 per-call 假家目錄 helper(_teardown_run / _codex_run 那種)不受影響也沒變多餘:
scripts/test_lumos.py:27251:    # CODEX_HOME 若在開發機上設過,會繞過假家目錄直接打到真的 ~/.codex
scripts/test_lumos.py:28536:        "總結句夾帶高於檔級的等級(codex f1)": "severity: clean\n總結: severity: blocker\n",
scripts/test_lumos.py:28562:        "帶 BOM 的正規化報告(codex f4)": "\ufeffseverity: clean\n",
scripts/test_lumos.py:28589:    check("normalize:BOM 剝掉算一處、剝完無殘留、輸出不帶 BOM(codex f4)", chb == 1 and issb == [] and not newb.startswith("\ufeff"), f"{chb} {issb}")
scripts/test_lumos.py:28638:        check("reported:gov --stats 算到擋下 3 次(連撞多半在同一秒,靠事件隨機碼分開;r1 f5/codex f3)", "記帳被寫側擋下 3 次(報告沒正規化 3 / 缺 refuted-set 0 / findings 多於 reported 0)" in _st, _st[-600:])
scripts/test_lumos.py:28649:        check("reported:findings 多於 reported 的撞牆也留 blocked 並在 gov --stats 分開數(codex f6)", "findings-over-reported" in (d / ".governance-log.jsonl").read_text(encoding="utf-8") and "findings 多於 reported 1" in _st2, _st2[-400:])
scripts/test_lumos.py:28684:        check("refuted:空項 rc2(不准當 none 混過;codex f5)", r.returncode == 2 and "空項" in r.stderr, f"rc={r.returncode} {r.stderr[:120]}")
scripts/test_lumos.py:28702:        check("refuted:CJK id 甲 不因 甲乙 命中 → rc2(r1 f4/codex f2)", r.returncode == 2 and "整字" in r.stderr, f"rc={r.returncode} {r.stderr[:120]}")
scripts/test_lumos.py:29690:    hook = str(Path(__file__).resolve().parent / "hooks" / "claude" / "dispatch-lens-hook.py")
scripts/test_lumos.py:29718:    check("lens: _GLOBAL_CLAUDE_HOOKS 含 dispatch-lens-hook.py", "dispatch-lens-hook.py" in m._GLOBAL_CLAUDE_HOOKS, str(m._GLOBAL_CLAUDE_HOOKS))
scripts/test_lumos.py:29719:    check("lens: ANCHOR_FILES 含 hook 檔", "scripts/hooks/claude/dispatch-lens-hook.py" in m.ANCHOR_FILES, str(m.ANCHOR_FILES))
scripts/test_lumos.py:29721:    check("lens: HOOK_ENTRIES 註冊 matcher Agent", '"matcher": "Agent"' in src and "dispatch-lens-hook.py" in src, "merge-claude-settings.py 未註冊")
scripts/test_lumos.py:29723:    check("lens: enforcement 四元組含 dispatch-lens", '"dispatch-lens-hook.py")' in lsrc and "pretooluse-dispatch-lens-hook" in lsrc, "enforcement 未登記")
scripts/test_lumos.py:29796:    hook_path = str(Path(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
scripts/test_lumos.py:29832:    hook_path = str(Path(__file__).resolve().parent / "hooks" / "claude" / "impact-hook.py")
scripts/test_lumos.py:29916:        {"type": "user", "cwd": str(repo), "sessionId": "S", "attachment": {"type": "hook_additional_context", "hookName": "PreToolUse:Edit", "toolUseID": "tu1", "content": ["必看——這 2 篇帶著不能破壞的合約或出過事故:\n  直接 ★INVARIANT★ Systems/x.md\n  hop1 ★INVARIANT★ Projects/x.md\n"]}},
scripts/test_lumos.py:29995:def _codex_run(home, code):
scripts/test_lumos.py:30008:def t_codex_merge_target():
scripts/test_lumos.py:30009:    """合併器 --target codex:寫 ~/.codex/hooks.json、五支註冊、matcher 對照(apply_patch / SubagentStart)、
scripts/test_lumos.py:30010:    命令列帶 --harness codex;--prune-only 只剪懸空;壞 JSON 回 1 不動檔。"""
scripts/test_lumos.py:30016:    r = _sp.run([sys.executable, str(merge), "--target", "codex"], env=env, capture_output=True, text=True)
scripts/test_lumos.py:30017:    hj = home / ".codex" / "hooks.json"
scripts/test_lumos.py:30018:    check("codex-merge: 寫 ~/.codex/hooks.json", r.returncode == 0 and hj.exists(), r.stderr[-200:])
scripts/test_lumos.py:30021:    check("codex-merge: 五支都註冊", sorted(_ for _ in ("lumos-entry-hook.py", "ci-status-hook.py", "impact-hook.py", "dispatch-lens-hook.py", "check-graph-sync.py") if any(_ in c for c in cmds)) == sorted(["lumos-entry-hook.py", "ci-status-hook.py", "impact-hook.py", "dispatch-lens-hook.py", "check-graph-sync.py"]), str(cmds))
scripts/test_lumos.py:30023:    # 所以不能再用「結尾必須是 --harness codex」比對。這條守的是「有帶家族旗標、指對目錄」,
scripts/test_lumos.py:30025:    check("codex-merge: 命令列全帶 --harness codex 且指 ~/.codex/hooks/",
scripts/test_lumos.py:30026:          all("--harness codex" in c and ".codex/hooks/" in c for c in cmds), str(cmds))
scripts/test_lumos.py:30027:    check("codex-merge: 命令列也把逾時天花板傳給 hook(內層要靠它算)",
scripts/test_lumos.py:30029:    pre = d["hooks"].get("PreToolUse", [])
scripts/test_lumos.py:30030:    check("codex-merge: 影響幅度 hook matcher=apply_patch", any(e.get("matcher") == "apply_patch" for e in pre), str(pre))
scripts/test_lumos.py:30031:    check("codex-merge: 沒有 Agent matcher(派工鏡頭改掛 SubagentStart)", not any(e.get("matcher") == "Agent" for e in pre) and any("dispatch-lens-hook.py" in h["command"] for e in d["hooks"].get("SubagentStart", []) for h in e["hooks"]), str(d["hooks"].keys()))
scripts/test_lumos.py:30032:    check("codex-merge: 不碰 ~/.claude", not (home / ".claude").exists(), "")
scripts/test_lumos.py:30036:    _sp.run([sys.executable, str(merge), "--target", "codex", "--prune-only"], env=env, capture_output=True, text=True)
scripts/test_lumos.py:30038:    check("codex-merge: prune-only 剪懸空我方註冊(hook 檔沒 copy 進來)", "check-graph-sync.py" not in dump, dump[:200])
scripts/test_lumos.py:30039:    check("codex-merge: prune-only 留使用者 hook", "mine.py" in dump, dump[:200])
scripts/test_lumos.py:30042:    r = _sp.run([sys.executable, str(merge), "--target", "codex"], env=env, capture_output=True, text=True)
scripts/test_lumos.py:30043:    check("codex-merge: 壞 JSON 回 1 且不動檔", r.returncode == 1 and hj.read_text(encoding="utf-8") == "{ broken", f"rc={r.returncode}")
scripts/test_lumos.py:30046:def t_codex_sync_global_tristate():
scripts/test_lumos.py:30047:    """_sync_global_hooks(repo,'codex') 三態:有 ~/.codex → ok(hook 檔 copy + hooks.json);hooks.json 壞 → merge-failed
scripts/test_lumos.py:30048:    (檔仍 copy、不印假成功);無 ~/.codex 且 PATH 無 codex → absent。Claude 側包裝仍回 bool。"""
scripts/test_lumos.py:30050:    home = Path(tempfile.mkdtemp(prefix="gctl-cdx-sync-")); (home / ".codex").mkdir()
scripts/test_lumos.py:30051:    r = _codex_run(home, "print(m._sync_global_hooks(repo,'codex'))")
scripts/test_lumos.py:30052:    check("codex-sync: 有 ~/.codex → ok", r.stdout.strip().endswith("ok"), r.stdout[-200:] + r.stderr[-200:])
scripts/test_lumos.py:30053:    check("codex-sync: 五支 hook 檔 copy 到 ~/.codex/hooks/", all((home / ".codex" / "hooks" / f).exists() for f in ("impact-hook.py", "dispatch-lens-hook.py", "check-graph-sync.py", "lumos-entry-hook.py", "ci-status-hook.py")), str(list((home / ".codex" / "hooks").iterdir())))
scripts/test_lumos.py:30054:    check("codex-sync: hooks.json 五支註冊", len([1 for arr in _j.loads((home / ".codex" / "hooks.json").read_text()).get("hooks", {}).values() for e in arr for h in e["hooks"]]) == 5, "")
scripts/test_lumos.py:30055:    (home / ".codex" / "hooks.json").write_text("{ broken", encoding="utf-8")
scripts/test_lumos.py:30056:    r = _codex_run(home, "print(m._sync_global_hooks(repo,'codex'))")
scripts/test_lumos.py:30057:    check("codex-sync: hooks.json 壞 → merge-failed(不是 ok)", r.stdout.strip().endswith("merge-failed"), r.stdout[-200:])
scripts/test_lumos.py:30058:    check("codex-sync: merge-failed 訊息講設定檔損毀、不提探針", "損毀" in m_msg(home, "merge-failed") and "PROBE" not in m_msg(home, "merge-failed"), m_msg(home, "merge-failed"))
scripts/test_lumos.py:30060:    r = _codex_run(home2, "import os;os.environ['PATH']='/nonexistent';print(m._sync_global_hooks(repo,'codex'))")
scripts/test_lumos.py:30061:    check("codex-sync: 無 ~/.codex 且 PATH 無 codex → absent", r.stdout.strip().endswith("absent"), r.stdout[-200:] + r.stderr[-200:])
scripts/test_lumos.py:30062:    check("codex-sync: absent 不建 ~/.codex", not (home2 / ".codex").exists(), "")
scripts/test_lumos.py:30063:    r = _codex_run(home2, "print(m._sync_global_claude(repo))")
scripts/test_lumos.py:30064:    check("codex-sync: Claude 包裝仍回 True", r.stdout.strip().endswith("True"), r.stdout[-100:])
scripts/test_lumos.py:30068:    r = _codex_run(home, f"print(m._sync_msg('codex','{state}'))")
scripts/test_lumos.py:30072:def t_codex_teardown_global():
scripts/test_lumos.py:30073:    """_teardown_global_hooks(repo,'codex'):清 ~/.codex/hooks 我方檔+剪註冊、留使用者 hook;沒 ~/.codex 無事可拆回 True。"""
scripts/test_lumos.py:30075:    home = Path(tempfile.mkdtemp(prefix="gctl-cdx-td-")); (home / ".codex").mkdir()
scripts/test_lumos.py:30076:    _codex_run(home, "m._sync_global_hooks(repo,'codex')")
scripts/test_lumos.py:30077:    hj = home / ".codex" / "hooks.json"
scripts/test_lumos.py:30081:    r = _codex_run(home, "print(m._teardown_global_hooks(repo,'codex'))")
scripts/test_lumos.py:30082:    check("codex-teardown: 我方 hook 檔移除", not (home / ".codex" / "hooks" / "impact-hook.py").exists(), r.stderr[-200:])
scripts/test_lumos.py:30084:    check("codex-teardown: 我方註冊被剪", "impact-hook.py" not in dump and "dispatch-lens-hook.py" not in dump, dump[:300])
scripts/test_lumos.py:30085:    check("codex-teardown: 使用者 hook 保留", "mine.py" in dump, dump[:300])
scripts/test_lumos.py:30087:    r = _codex_run(home2, "print(m._teardown_global_hooks(repo,'codex'))")
scripts/test_lumos.py:30088:    check("codex-teardown: 沒 ~/.codex → True 且不建目錄", r.stdout.strip().endswith("True") and not (home2 / ".codex").exists(), r.stdout[-100:])
scripts/test_lumos.py:30091:def t_codex_skills_shared_dir():
scripts/test_lumos.py:30101:    r = _codex_run(home, "m._install_skills()")
scripts/test_lumos.py:30102:    check("codex-skills: 外方同名目錄不被刪、內容原樣", (foreign / "SKILL.md").read_text(encoding="utf-8").startswith("---\nname: someone-else") and not foreign.is_symlink(), r.stderr[-300:])
scripts/test_lumos.py:30103:    check("codex-skills: 外方目錄有印跳過警告", "跳過" in r.stderr and "lumos-project-notes" in r.stderr, r.stderr[-300:])
scripts/test_lumos.py:30104:    check("codex-skills: 帶標記的複製物重建成連結", managed.is_symlink() and not (managed / "old.md").exists(), str(managed))
scripts/test_lumos.py:30105:    check("codex-skills: 其餘 skill 連進 ~/.agents/skills", (home / ".agents" / "skills" / "lumos-code-loop").is_symlink(), "")
scripts/test_lumos.py:30106:    check("codex-skills: ~/.claude/skills 照裝", (home / ".claude" / "skills" / "lumos-code-loop").exists(), "")
scripts/test_lumos.py:30107:    r = _codex_run(home, "m.cmd_uninstall()")
scripts/test_lumos.py:30108:    check("codex-uninstall: 連結清掉", not (home / ".agents" / "skills" / "lumos-code-loop").exists() and not (home / ".claude" / "skills" / "lumos-code-loop").exists(), r.stdout[-300:])
scripts/test_lumos.py:30109:    check("codex-uninstall: 外方目錄保留並警告", (foreign / "SKILL.md").exists() and "保留" in r.stderr, r.stderr[-300:])
scripts/test_lumos.py:30112:def t_codex_reinject_agents_targets():
scripts/test_lumos.py:30119:        check("codex-reinject: 預設目標=AGENTS.md", mod._reinject_targets(root) == ("CLAUDE.md", "AGENTS.md"), str(mod._reinject_targets(root)))
scripts/test_lumos.py:30122:        check("codex-reinject: AGENTS.md created 且檔頭是 # AGENTS.md(不是 # CLAUDE.md)", r.status == "created" and txt.startswith("# AGENTS.md\n") and "# CLAUDE.md" not in txt, txt[:60])
scripts/test_lumos.py:30128:        check("codex-reinject: 有標題 → appended 且區塊在第一個標題之後、第一條規矩之前", r.status == "appended" and txt.index("# 專案指示") < txt.index(block) < txt.index("第一條規矩") < txt.index("## 第二節"), txt[:200])
scripts/test_lumos.py:30133:        check("codex-reinject: 無標題 → 區塊在檔案最前、原文在後", r.status == "appended" and txt.startswith(block) and "純散文起頭" in txt and "條列一" in txt, txt[:120])
scripts/test_lumos.py:30136:        check("codex-reinject: 再跑一次 unchanged", r2.status == "unchanged", r2.status)
scripts/test_lumos.py:30139:        check("codex-reinject: 有 override → 目標=AGENTS.override.md", mod._agents_target(root) == "AGENTS.override.md", mod._agents_target(root))
scripts/test_lumos.py:30141:        check("codex-reinject: _reinject_all 兩檔都刷(CLAUDE.md appended、override appended)", res["CLAUDE.md"].status == "appended" and res["AGENTS.override.md"].status == "appended", str({k: v.status for k, v in res.items()}))
scripts/test_lumos.py:30145:        check("codex-reinject: strip 兩檔都剝、自有內容留", stripped and "GRAPH-DISCIPLINE" not in c and "GRAPH-DISCIPLINE" not in o and "自有" in c and "# override" in o, c[:80] + o[:80])
scripts/test_lumos.py:30148:def t_codex_enforcement_rows():
scripts/test_lumos.py:30149:    """enforcement Codex 八列:有 ~/.codex + hooks.json 註冊 + 檔在 → registered-trust-unknown(永不 active);
scripts/test_lumos.py:30150:    檔不在 → degraded;沒 ~/.codex → 全 unknown(不適用);summary 分母排除 trust-unknown;codex-skills/agents-md 各自判。"""
scripts/test_lumos.py:30154:    cd = home / ".codex"; (cd / "hooks").mkdir(parents=True)
scripts/test_lumos.py:30155:    cfg = {"hooks": {"SessionStart": [{"hooks": [{"command": f"python3 {cd}/hooks/lumos-entry-hook.py --harness codex"}]}],
scripts/test_lumos.py:30156:                     "PreToolUse": [{"matcher": "apply_patch", "hooks": [{"command": f"python3 {cd}/hooks/impact-hook.py --harness codex"}]}]}}
scripts/test_lumos.py:30162:    check("codex-enf: 註冊+檔在 → registered-trust-unknown(不是 active)", by.get("codex-session-entry-hook") == "registered-trust-unknown", str(by))
scripts/test_lumos.py:30163:    check("codex-enf: 註冊但檔不在 → degraded", by.get("codex-pretooluse-impact-hook") == "degraded", str(by))
scripts/test_lumos.py:30164:    check("codex-enf: 沒註冊 → inactive", by.get("codex-stop-graph-sync-hook") == "inactive", str(by))
scripts/test_lumos.py:30165:    check("codex-enf: codex-skills active(有 lumos-*)", by.get("codex-skills") == "active", str(by))
scripts/test_lumos.py:30166:    check("codex-enf: agents-md 沒檔 → inactive", by.get("agents-md") == "inactive", str(by))
scripts/test_lumos.py:30169:    # unknown 列=required-status-check+vendored-cli+codex-cli(無 codex 可執行檔... 有 ~/.codex 但 codex --version 可能在)→用差值釘

[35m[3mcodex[0m[0m
目前已看到一個核心接線風險：新「家」是第四種候選來源，但現行結果模型只有事故／直接／間接三種；我正在追它對大檔自由席、diff 聚合與 spec 派工鏡頭三條路的具體後果。
[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'python3 governance/eval/retrieval_eval.py --help'[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
usage: retrieval_eval.py [-h] [--auto] [--goldset GOLDSET]
                         [--split {train,held}] [--live-vault]
                         [--snapshot SNAPSHOT] [--ablation] [-k K]

options:
  -h, --help            show this help message and exit
  --auto                cochange proxy 自動金標(related 面)
  --goldset GOLDSET     人工標註 goldset.json 路徑
  --split {train,held}  只跑該切分
  --live-vault          用現況 vault(預設釘 goldset snapshot;探索/漂移觀測用)
  --snapshot SNAPSHOT   覆寫釘定 sha(過渡雙跑的舊快照輪;該輪 mode=goldset-transition)
  --ablation            消融模式(比較改動前後用):★有任何未標候選就擋下、rc 3★。不帶這旗標維持原行為(只印警告不擋)
  -k K

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'python3 scripts/lumos dispatch-lens --help'[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'python3 scripts/lumos new --help'[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'python3 scripts/lumos impact --help'[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 160ms:[0m
usage: lumos dispatch-lens [-h] [--arm] [--seats LENS_SEATS] [--claim]
                           [--disarm] [--status] [--spec LENS_SPEC]
                           [--repo LENS_REPO] [--json] [--no-cache]
                           [--deadline 秒]
                           [lens_range]

什麼時候用:代碼審派工詞的固定席鏡頭:Claude 側 hook 自動叫;Codex 編排時派工前一刻敲 `--arm <base>..<head>
--seats N`(子代理開場各領一席,10 分 TTL),派完 `--disarm`。手動看內容給 <base>..<head>(從 base
讀、零自由文字;base 不在主線→rc4 放行)。

positional arguments:
  lens_range          diff 範圍,恰好 <base>..<head>;base
                      必須在主線歷史上(--claim/--disarm/--status 不用給)

options:
  -h, --help          show this help message and exit
  --arm               Codex 編排用:派工前一刻算好鏡頭、武裝 --seats 席(10 分內子代理開場各領一席)
  --seats LENS_SEATS  配 --arm:這次要派幾席(多給的當緩衝)
  --claim             SubagentStart hook 用:原子認領一席,回鏡頭文字
  --disarm            收掉本 repo 的武裝
  --status            看本 repo 武裝剩幾席
  --spec LENS_SPEC    設計審用:給計劃筆記路徯,鏡頭改從計劃提到的程式檔與直接連結的節點算(從工作樹讀、不快取;hook 看
                      LUMOS-SPEC: 標記自動叫)
  --repo LENS_REPO    repo 內任一路徑(會自己找 repo 根)
  --json              JSON 輸出 {text,pinned,listed,omitted_nodes,omitted_files,
                      mainline,cache_hit}
  --no-cache          不讀不寫 20 分鐘快取
  --deadline 秒        最多等幾秒:快取沒有就派一個脫離的行程去算,這邊等到時間就回 rc5
                      並讓那支算完(下一次同範圍直接命中)。hook 用

[32m succeeded in 164ms:[0m
usage: lumos new [-h] [--plan PLAN] [--systems SYSTEMS] [--code 檔]
                 [--responsibility RESPONSIBILITY]
                 {system,verification,issue,project} name

什麼時候用:依範本建一篇新筆記。驗證紀錄加 --plan / --systems 自動雙向連。

positional arguments:
  {system,verification,issue,project}
  name

options:
  -h, --help            show this help message and exit
  --plan PLAN           verification 專用:plan_refs 回指的計劃節點(逗號分隔)
  --systems SYSTEMS     verification 專用:同步 append verified_by 的 Systems(逗號分隔)
  --code 檔              system/issue:這篇管哪幾支程式檔(repo 相對路徑,可重複;寫進 about_code)
  --responsibility RESPONSIBILITY
                        system 專用:一句話講這篇負責什麼、不負責什麼(至少 10 個字;新開的 Systems
                        節點提交時必須有)

[32m succeeded in 162ms:[0m
usage: lumos impact [-h] [--file IMPACT_FILE] [--node IMPACT_NODE]
                    [--diff IMPACT_DIFF] [--from-json IMPACT_FROM_JSON]
                    [--sync-only] [--sync-check] [--repo IMPACT_REPO]
                    [--depth IMPACT_DEPTH] [--json] [--ranked]
                    [--top IMPACT_TOP] [--min-score IMPACT_MIN]
                    [--stdin-payload] [--incidents-only]

什麼時候用:動手前:改這個檔 / 這段 diff 會波及哪些筆記、驗證、決策。--sync-check 查波及的筆記有沒有同步。

options:
  -h, --help            show this help message and exit
  --file IMPACT_FILE    被改動的 code 檔路徑(單檔模式;與 --diff/--node 三擇一)
  --node IMPACT_NODE    [M4/S2] typed hop-1 第三模式:列「誰以 verified_by/plan_refs
                        指向該節點」(單層;與 --depth 互斥)
  --diff IMPACT_DIFF    diff range(如 main..HEAD):聚合各改動檔的 ranked impact 成受影響功能面
                        manifest(code-loop 審計鏡頭)
  --from-json IMPACT_FROM_JSON
                        吃一份已經算好的結果(搭 --sync-only;推送關卡一次推送只算一次)
  --sync-only           配 --sync-check:只印「該動卻沒動」的點名(hooks 用),不印受影響功能面
  --sync-check          落成核對(配 --diff):預期受影響節點 vs 分支實際動過節點 → 未同步清單(advisory)
  --repo IMPACT_REPO    repo root(缺則退回 find_vault;hook 必傳)
  --depth IMPACT_DEPTH  BFS 展開深度(缺省讀 .lumos/impact.json;最終預設 2)
  --json                JSON 輸出(機器可讀)
  --ranked              融合排序+固定席+降噪(dormant v1)
  --top IMPACT_TOP      --ranked 非固定項上限
  --min-score IMPACT_MIN
                        --ranked 分數底線
  --stdin-payload       stdin 讀 {query,prospective}
  --incidents-only      只跑事故比對(不反查/BFS)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/lumos | sed -n '4200,4370p'
rg -n \"regen|from-scratch\" scripts/lumos | head -n 120"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
  4200	
  4201	
  4202	def _scope_policy(env):
  4203	    """讀 .lumos/config.json 的 scope 區塊 {"values": [...], "required": bool}。
  4204	
  4205	    [工具分類 2026-09-08,plan:Projects/工具分類_計劃] scope/ 標籤家族的值域由專案自己宣告——
  4206	    工具鏈自己用九個研究方向值、消費專案用業務域切片,兩邊語意不同,所以不能在程式裡寫死一張表。
  4207	    沒宣告(絕大多數消費專案)回 None,lint 對 scope 一個字都不說,行為與 2026-08-05 收編定版時相同。"""
  4208	    sc = _lumos_config_near_vault(env).get("scope")
  4209	    if not isinstance(sc, dict):
  4210	        return None
  4211	    vals = sc.get("values")
  4212	    if not isinstance(vals, list):
  4213	        return None
  4214	    return {"values": {x for x in vals if isinstance(x, str)}, "required": bool(sc.get("required", True))}
  4215	
  4216	
  4217	def _levenshtein_le1(a, b):
  4218	    """只判「編輯距離 ≤1」(打錯一個字的近名候選)——不做完整距離計算,夠用且便宜。"""
  4219	    if a == b:
  4220	        return False
  4221	    la, lb = len(a), len(b)
  4222	    if abs(la - lb) > 1:
  4223	        return False
  4224	    if la == lb:
  4225	        return sum(1 for x, y in zip(a, b) if x != y) == 1
  4226	    short, long_ = (a, b) if la < lb else (b, a)
  4227	    for i in range(len(long_)):
  4228	        if long_[:i] + long_[i + 1:] == short:
  4229	            return True
  4230	    return False
  4231	
  4232	
  4233	def cmd_lint(env, node):
  4234	    """單檔快檢:寫完一個節點立刻自驗標籤/格式(node-local,不掃 repo → 比 doctor 快;
  4235	    例外:regen 節點的 Check J 需檔案+git 存取,opt-in、量小)。
  4236	    抓「寫入當下」最常見的錯:type/summary 缺漏、★ 標記格式錯(漏被 contracts 抓)、
  4237	    裸合約 / 未審、symbol 行 typo、frontmatter 指紋(ghost trap…)。
  4238	    與 doctor 分工:doctor 是全圖權威(跨節點完整性 + [test:] 存在性),lint 只看這一篇、
  4239	    predicts pre-push 會不會擋(error 即 doctor --ci 會擋的同類)。"""
  4240	    rel = env.find(node)
  4241	    if rel is None:
  4242	        print(f"擋下:圖譜裡找不到叫 {node} 的筆記,先確認名稱或路徑(lumos search <關鍵字> 可以找)", file=sys.stderr)
  4243	        return 2
  4244	    n = env.notes[rel]
  4245	    errs = list(n.lint)          # frontmatter 指紋(ghost trap / 重複鍵 / 日期引號…)= error
  4246	    warns = []
  4247	
  4248	    # ★開頭欄位鍵打錯會被所有檢查靜默略過★(2026-09-06 全 repo 審視 #16):
  4249	    # 打成 valid_unde / verifed_by,lint 一句話都不說、doctor 也看不到,那個欄位等於沒寫。
  4250	    # ★只給軟提醒不升 error★:工具對未知欄位的立場是「前向相容、容忍」(消費專案與
  4251	    # core-knowledge 各有自己的欄位),升成 error 會讓別人的 vault 每次 lint 都被嘮叨。
  4252	    # 清單可用 .lumos/config.json 的 extra_frontmatter_keys 擴充。
  4253	    _known = set(_KNOWN_FRONTMATTER_KEYS) | set(LIST_KEYS) | set(LINK_KEYS) | set(_extra_fm_keys(env))
  4254	    _unknown = [k for k in n.fields.keys() if k not in _known]
  4255	    for _k in _unknown:
  4256	        _near = sorted(c for c in _known if _levenshtein_le1(_k, c))   # r1:_known 是 set,不排序的話多個等距候選每次給的建議會漂
  4257	        _hint = f"——是不是想寫 {_near[0]}?" if _near else "——工具不認得這個欄位,它不會被任何檢查讀到"
  4258	        warns.append(f"開頭欄位有個沒見過的鍵『{_k}』{_hint}(真的要用就加進 .lumos/config.json 的 extra_frontmatter_keys)")
  4259	
  4260	    t = n.fields.get("type")
  4261	    if not isinstance(t, str) or not t:
  4262	        errs.append("沒寫 type(這篇是功能、問題還是驗證紀錄?),工具沒辦法分類——在開頭欄位加一行 type: <類型>")
  4263	    elif t not in KNOWN_TYPES:
  4264	        errs.append(f"type『{t}』工具不認得,會被歸錯類——改成其中一個:{'/'.join(sorted(KNOWN_TYPES))}")
  4265	
  4266	    summ = n.fields.get("summary")
  4267	    summ = summ if isinstance(summ, str) else ""
  4268	    if t in ("system", "issue") and not summ.strip():
  4269	        errs.append(f"{t} 筆記沒有摘要區塊(FLOW:/KEY:/DEP: 那幾行),沒人能快速看懂這篇在講什麼——補上,範本可看 lumos new 產生的骨架")
  4270	
  4271	    # aliases 宣告制(2026-08-05 Enzo 裁定,cutoff 起新 system/issue 逼「判過」不逼「有值」):
  4272	    # aliases 吃 3.5 檢索權重,湊數別名主動污染排序——故 `aliases: []`=明示判過,合法;
  4273	    # 缺鍵=沒判過,擋。舊節點不回溯(created < cutoff)。
  4274	    _ALIASES_CUTOFF = "2026-08-05"
  4275	    if t in ("system", "issue"):
  4276	        _created = str(n.fields.get("created") or "")
  4277	        if _created >= _ALIASES_CUTOFF and "aliases" not in n.fields:
  4278	            errs.append("沒寫 aliases:要想過一次這件事有沒有別的叫法(症狀語/縮寫/舊名),別人換個說法才搜得到——"
  4279	                        "有就列出來,確定沒有就明確寫 aliases: [](湊數的別名比空的更糟)")
  4280	
  4281	    # 值域執法(2026-08-05 標籤結構優化,Enzo 裁;cutoff 制不回溯——Landmark 實測野化:
  4282	    # status 13 值同義混用、FLAG 50+ 自由文字淪為備註欄,可篩選性歸零)
  4283	    _ENUM_CUTOFF = "2026-08-06"
  4284	    _STATUS_ENUM = {
  4285	        "system": {"doing", "done", "planned", "deferred", "rejected", "superseded", "stale"},
  4286	        "project": {"todo", "doing", "done", "superseded"},
  4287	        "issue": {"open", "doing", "resolved", "done", "wontfix"},
  4288	        "verification": {"pass", "stale", "superseded"},
  4289	        "moc": {"doing", "done"},
  4290	    }
  4291	    _PRIORITY_ENUM = {"P0", "P1", "P2", "P3"}
  4292	    _RISK_ENUM = {"金流", "對外送出", "不可逆", "守衛面"}
  4293	    _FLAG_ENUM = {"TECHNICAL", "DECISION", "ORIGIN"}
  4294	    _created_e = str(n.fields.get("created") or n.fields.get("date") or "")
  4295	    if _created_e >= _ENUM_CUTOFF:
  4296	        _st = str(n.fields.get("status") or "")
  4297	        if t in _STATUS_ENUM and _st and _st not in _STATUS_ENUM[t]:
  4298	            errs.append(f"status『{_st}』不是 {t} 允許的狀態值,篩選統計會漏掉這篇——改成其中一個:{sorted(_STATUS_ENUM[t])}"
  4299	                        "(同義詞要歸一:resolved/done 擇一、verification 用 pass)")
  4300	        for tg in (n.fields.get("tags") or []):
  4301	            if not isinstance(tg, str):
  4302	                continue
  4303	            if tg.startswith("priority/") and tg.split("/", 1)[1] not in _PRIORITY_ENUM:
  4304	                errs.append(f"priority 標籤只能是 P0 到 P3 四級,你寫的是 {tg!r}")
  4305	            if tg.startswith("risk/") and tg.split("/", 1)[1] not in _RISK_ENUM:
  4306	                errs.append(f"risk 標籤只能是 {sorted(_RISK_ENUM)} 之一,你寫的是 {tg!r}")
  4307	            if tg.startswith(("feature/", "area/")):
  4308	                warns.append(f"{tg!r}:feature/ 和 area/ 這兩種標籤已停用,新筆記改用 scope/ 開頭(舊筆記查詢仍認)")
  4309	        import re as _re_f
  4310	        _mflag = _re_f.search(r"^\s*FLAG:(\S+)", summ, _re_f.M)
  4311	        if _mflag and _mflag.group(1) not in _FLAG_ENUM:
  4312	            errs.append(f"FLAG:『{_mflag.group(1)}』不是允許的三種分類之一 {sorted(_FLAG_ENUM)}"
  4313	                        "(FLAG 是分類欄不是備註欄;想寫的說明移到 KEY: 那行)")
  4314	
  4315	    # scope 值域(2026-09-08 工具分類:一篇一個主類,真橫跨才第二個)——只在專案宣告了 scope 區塊時唸,
  4316	    # 而且只 warning 不擋;★不走 created cutoff★:宣告的當下全圖已回填,之後新節點漏掛就該被唸。MOC 豁免。
  4317	    _sp = _scope_policy(env) if t != "moc" else None
  4318	    if _sp is not None:
  4319	        _scope_tags = [tg for tg in (n.fields.get("tags") or []) if isinstance(tg, str) and tg.startswith("scope/")]
  4320	        _menu = ", ".join(sorted(_sp["values"]))
  4321	        if not _scope_tags and _sp["required"]:
  4322	            warns.append("這篇沒掛 scope/ 標籤(這個專案在 .lumos/config.json 宣告了每篇要有一個主類):"
  4323	                         f"挑一個掛上——{_menu};各類的定義用 lumos query --tag scope/<值> 看同類節點就懂")
  4324	        elif len(_scope_tags) > 2:
  4325	            warns.append(f"這篇掛了 {len(_scope_tags)} 個 scope/ 標籤,規矩是一篇一個主類、真橫跨兩類才准第二個:"
  4326	                         "留下最能代表它的,其餘拿掉(lumos remove <節點> tags scope/<值>)")
  4327	        for tg in _scope_tags:
  4328	            if tg.split("/", 1)[1] not in _sp["values"]:
  4329	                warns.append(f"scope 標籤 {tg!r} 不在這個專案宣告的值域裡({_menu}):"
  4330	                             "打錯字就改成表內的值,真的要新類就先去 .lumos/config.json 的 scope.values 登記")
  4331	
  4332	    # decisions 結構守衛(2026-07-29 外審實錘:id 縮排吞進 content block,parser 靜默降級、
  4333	    # doctor 全綠——「綠燈≠schema 有效」的活例。以正牌 parse_decisions 驗:
  4334	    # 壞型一(sibling 被吞)→ content 空;壞型二(entry 非 `- key:` 形)→ 整條被靜默丟棄=條數對不上)
  4335	    try:
  4336	        _fm_lines, _ = split_frontmatter((env.vault / rel).read_text(encoding="utf-8"))
  4337	    except OSError:
  4338	        _fm_lines = None
  4339	    if _fm_lines and any(re.match(r"^decisions:\s*$", _l) for _l in _fm_lines):
  4340	        _parsed = parse_decisions(_fm_lines)
  4341	        _raw_items = 0
  4342	        _in = False
  4343	        for _l in _fm_lines:
  4344	            if re.match(r"^decisions:\s*$", _l):
  4345	                _in = True
  4346	                continue
  4347	            if _in and _l.strip() and not _l.startswith(" "):
  4348	                _in = False
  4349	            if _in and re.match(r"^  -\s", _l):
  4350	                # 只認 entry 縮排層(恰 2 空格):alternatives_considered 等巢狀清單(≥4 空格)
  4351	                # 不是決策條目——2026-08-05 Landmark 回填實戰:照 ADR 規範寫巢狀清單被誤報壞損
  4352	                _raw_items += 1
  4353	        if _raw_items != len(_parsed):
  4354	            errs.append(f"decisions 格式跑掉了:寫了 {_raw_items} 條、工具只認得出 {len(_parsed)} 條,其他等於白寫"
  4355	                        "(每條要以 `- id:`/`- content:` 起頭;別手改,用 lumos decision-add 寫入)")
  4356	        for _di, _d in enumerate(_parsed):
  4357	            if not str(_d.get("content") or "").strip():
  4358	                errs.append(f"第 {_di} 條 decisions 沒有內容,通常是旁邊欄位縮排錯、被吞進上一欄了——檢查縮排或改用 lumos decision-add 重寫")
  4359	
  4360	    # 狀態標籤漂移守衛:status 欄位 vs tags 的 status/*(反正規化的完整性檢查,
  4361	    # 兜住繞過 set status 同步的寫入路徑;見 Projects/狀態標籤同步守衛_計劃)
  4362	    _st = n.fields.get("status")
  4363	    if isinstance(_st, str) and _st.strip():
  4364	        for _tg in as_list(n.fields.get("tags")):
  4365	            if isinstance(_tg, str) and _tg.startswith("status/") and _tg != f"status/{_st.strip()}":
  4366	                errs.append(f"status 欄位({_st})和狀態標籤({_tg})寫的不一樣(漂移),靠標籤篩狀態會抓錯——用 lumos set <節點> status <值> 改,兩邊會自動同步")
  4367	
  4368	    _regen_val = n.fields.get("regen")
  4369	    _lint_is_regen = isinstance(_regen_val, str) and bool(_regen_val.strip())
  4370	
2491:    # Check J: regen 重生來源守衛(from-scratch 節點的 provenance 分級+拒絕發明無證據合約)。
2492:    # 與 cmd_lint 共用 check_regen_provenance(防兩入口規則漂移);映射表——
2494:    _regen_rels = [(rel_, n_) for rel_, n_ in sorted(notes.items())
2495:                   if isinstance(n_.fields.get("regen"), str) and n_.fields.get("regen").strip()]
2496:    if _regen_rels:
2497:        section("J", "從程式碼重建出來的筆記,每條主張有沒有標清楚是有證據、推測、還是找不到出處(regen 重生來源守衛)")
2500:        for rel_, n_ in _regen_rels:
2501:            j_errs, j_warns, j_gov = check_regen_provenance(n_, _jroot)
2509:            warn(j_err_lines, f"{len(j_err_lines)} 條重建筆記的主張沒標清楚出處(違反 regen 重生來源守衛):",
2512:            ok(f"{len(_regen_rels)} 篇重建筆記的證據指針都驗得到")
3340:# 抽「乾淨宣稱文字」時 test/audit/kill 與 regen 證據指針(src/git)都要剝掉(否則漏進顯示/子字串比對)。
3759:# ── regen 重生來源軸(M1 from-scratch 守衛;Check J,獨立於合約軸/可逆性軸)──
3760:# 設計:Projects/from-scratch重生守衛_計劃(design-loop 3 輪,golden: governance/golden/fromscratch-m1)。
3970:def check_regen_provenance(note, repo_root):
3971:    """Check J(regen 重生來源守衛)共用檢查器——cmd_lint 與 run_doctor 同呼叫同一函式(防兩入口
3972:    規則漂移)。只對 frontmatter 帶 regen 的節點生效;非 regen 節點回三空。只掃 summary 行。
3977:    註:本函式為 regen 節點對 lint「node-local 不掃 repo」原則的 opt-in 例外(檔案+git 存取)。
3978:    設計:Projects/from-scratch重生守衛_計劃;golden: governance/golden/fromscratch-m1。"""
3980:    regen = note.fields.get("regen")
3981:    if not (isinstance(regen, str) and regen.strip()):
4001:        # J-a:regen ★INVARIANT★ 需 [src:]/[git:] 意圖證據(與 Check T 的 [test:] 疊加——
4004:            errs.append(f"regen 節點的 ★INVARIANT★ 缺 [src:]/[git:] 意圖證據"
4008:            errs.append(f"regen 節點的 DECISION 行無證據指針且未標 推測:/佚失:(J-b):{line[:48]}")
4158:    "signed_off", "kill_recipes", "core_refs", "regen",
4162:#   結果漏掉 core_refs(跨專案升格參照,doctor Check C 與 impact 跨 repo 展開都在讀)與 regen(重建溯源在讀)
4235:    例外:regen 節點的 Check J 需檔案+git 存取,opt-in、量小)。
4368:    _regen_val = n.fields.get("regen")
4369:    _lint_is_regen = isinstance(_regen_val, str) and bool(_regen_val.strip())
4380:                # 雙報消歧 predicate(Check J):regen 節點的 KEY:推測:★INVARIANT★ 由 J 專屬訊息
4381:                # 接手,跳過 generic 位置錯誤(同一行恰一則;非 regen 節點 generic 保留=兜底)。
4383:                if (_lint_is_regen and REGEN_PREFIX_RE.match(line)
4396:    # Check J 單檔版(regen 重生來源守衛):共用 check_regen_provenance,映射表——
4398:    if _lint_is_regen:
4399:        j_errs, j_warns, _j_gov = check_regen_provenance(n, _repo_root_from_env(env))
10653:SCALAR_KEYS = {"status", "updated", "created", "type", "self_audit", "signed_off", "regen", "pitfall_ask", "pitfall_source", "about_code_stamp", "responsibility"}  # pitfall_* 2026-08-09 已知坑策展庫;about_code_stamp 2026-08-23(語意欄位基礎,計劃:固定席扇出降權)
16431:    _refcheck_scan 與 check_regen_provenance(Check J 的 [src:] 驗證)共用——

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/lumos | sed -n '4360,4430p'
nl -ba scripts/lumos | sed -n '11130,11220p'
rg -n \"regen.*from-scratch|from-scratch/|key == \\\"regen\\\"|regen\" skills/lumos-project-notes/commands/09-節點還原.md skills/lumos-project-notes/reference.md docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md | head -n 240"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
  4360	    # 狀態標籤漂移守衛:status 欄位 vs tags 的 status/*(反正規化的完整性檢查,
  4361	    # 兜住繞過 set status 同步的寫入路徑;見 Projects/狀態標籤同步守衛_計劃)
  4362	    _st = n.fields.get("status")
  4363	    if isinstance(_st, str) and _st.strip():
  4364	        for _tg in as_list(n.fields.get("tags")):
  4365	            if isinstance(_tg, str) and _tg.startswith("status/") and _tg != f"status/{_st.strip()}":
  4366	                errs.append(f"status 欄位({_st})和狀態標籤({_tg})寫的不一樣(漂移),靠標籤篩狀態會抓錯——用 lumos set <節點> status <值> 改,兩邊會自動同步")
  4367	
  4368	    _regen_val = n.fields.get("regen")
  4369	    _lint_is_regen = isinstance(_regen_val, str) and bool(_regen_val.strip())
  4370	
  4371	    for raw in summ.split("\n"):
  4372	        line = raw.strip()
  4373	        if not line:
  4374	            continue
  4375	        ms = SYMBOLISH_RE.match(line)
  4376	        if ms and ms.group(1) not in SYMBOL_NAMES:
  4377	            warns.append(f"非標準符號行『{ms.group(1)}:』,看起來像打錯字,這行不會被當成摘要——標準符號是 {'/'.join(sorted(SYMBOL_NAMES))}")
  4378	        for mark, rx in (("★INVARIANT★", INVARIANT_RE), ("★DEBT★", DEBT_RE)):
  4379	            if mark in line and not rx.match(line):
  4380	                # 雙報消歧 predicate(Check J):regen 節點的 KEY:推測:★INVARIANT★ 由 J 專屬訊息
  4381	                # 接手,跳過 generic 位置錯誤(同一行恰一則;非 regen 節點 generic 保留=兜底)。
  4382	                # 既有迴圈只含 INVARIANT/DEBT、無 IRREVERSIBLE → 消歧只需此分支。
  4383	                if (_lint_is_regen and REGEN_PREFIX_RE.match(line)
  4384	                        and ("★INVARIANT★" in line or "★IRREVERSIBLE★" in line)):
  4385	                    continue
  4386	                errs.append(f"{mark} 必須是 KEY 行前綴(寫成 KEY:{mark} ...),放別處工具掃合約會直接漏看:{line[:48]}")
  4387	
  4388	    invs, _ = extract_contracts(n)
  4389	    for inv in invs:
  4390	        clean, refs = strip_test_refs(inv)
  4391	        if not refs:
  4392	            errs.append(f"裸 ★INVARIANT★:標成不能破壞的合約卻沒綁測試,沒人能機械驗證它——行尾加 [test:測試名](健檢會擋):{first_line(clean, 48)}")
  4393	        elif not invariant_audit_refs(inv):
  4394	            errs.append(f"★INVARIANT★ 綁了測試但未獨立審計:還沒有不知道脈絡的人確認這條是真合約、測試夠不夠格——審過後用 lumos guard audit 補 [audit:](推送會擋):{first_line(clean, 48)}")
  4395	
  4396	    # Check J 單檔版(regen 重生來源守衛):共用 check_regen_provenance,映射表——
  4397	    # errs→errs(rc1)/warns→warns(顯示不計 rc)/gov_events→lint 一律不落帳(高頻)。
  4398	    if _lint_is_regen:
  4399	        j_errs, j_warns, _j_gov = check_regen_provenance(n, _repo_root_from_env(env))
  4400	        errs.extend(j_errs)
  4401	        warns.extend(j_warns)
  4402	
  4403	    # Check R 單檔版:可逆性回退綁定 + 標錯型別
  4404	    for marker, rclean, ref, guard_ref in extract_reversibility(n):
  4405	        if t != "system":
  4406	            errs.append(f"{marker} 只能標在功能筆記(Systems)上,這篇是 {t!r},標了也不會被當合約檢查:{first_line(rclean, 40)}")
  4407	        elif marker == "★IRREVERSIBLE★":
  4408	            if not (_rollback_resolved(n, ref) or _guard_resolved(n, guard_ref)):
  4409	                errs.append(f"{marker} 缺實質回退:標成做了回不去,卻沒寫出事怎麼退——行尾加 [rollback:decisions] 或 [guard:decisions],並在 decisions 寫上回退/防護內容:{first_line(rclean, 40)}")
  4410	        elif not _rollback_resolved(n, ref):  # ★CHECKPOINT★;guard_ref 不讀
  4411	            warns.append(f"{marker} 建議補回退(不擋):改了難救的動作最好寫下怎麼退,行尾加 [rollback:decisions]:{first_line(rclean, 40)}")
  4412	
  4413	    # ── Check U:全稱宣稱未綁測試(成因 G「過度概化」;2026-08-12 加) ──
  4414	    # 由來:2026-08-12 LandmarkMember 全 24 篇交叉審計(389 主張/59 不一致)歸因出一類最毒的 drift
  4415	    # ——★把單一模組的個別設計寫成系統通則★。實例:`背景排程總覽` 寫「服務 disabled 時也要寫心跳」
  4416	    # 像通則,實際只有一支服務這樣做,現役的 SecurityAnomalyMonitorService 直接 return 不寫;
  4417	    # 後人依樣畫葫蘆就會寫出不一致的新服務。
  4418	    # PRIOR-ART(真搜):世界對這類的成熟解是**架構適應度函數**(ArchUnit/Deptrac)——「與其把規則
  4419	    # 畫在沒人看的圖上,不如編成一違反就 fail build 的測試」。本檢查不取代那個做法,而是**提示該去做**:
  4420	    # 若真是通則,寫成適應度函數會當場告訴你有沒有例外;若寫不出來,那它本來就不是通則。
  4421	    # ★噪音實測(2026-08-12,LandmarkMember 30 篇 Systems / 261 條 KEY 行)★:
  4422	    #   單看量詞(一律/必須/所有…)→ 命中 17%,抽樣多為用詞規範/操作指示 = 會被無視的 warn;
  4423	    #   收緊成「分配式量詞 + 程式實體 + 義務語氣」三者同現 → 命中 1%(5 行),其中 3 條真陽性,
  4424	    #   含 CustTransfer/滿額贈 的「折疊守衛(通則)」(自稱通則、零 [test:],且節點自己記載
  4425	    #   2026-06-02 漏補一路到 07-21 才被使用者回報)。故採三訊號同現。
  4426	    _U_DIST = r'(所有|每個|每支|每一|各個|凡是|凡|一律)'
  4427	    _U_ENT = r'(Service|Repository|Controller|Job|服務|排程|查詢|端點|入口|呼叫點|實作|模組|節點|欄位)'
  4428	    _U_MOD = r'(必須|都要|都必須|皆須|應該|一律要|要寫|要帶|不可|禁止)'
  4429	    import re as _re_u
  4430	    for _ln in summ.splitlines():
 11130	    存成正規化的樣子,排序加分用的鍵才對得上(src/../src/a.py 跟 src/a.py 要是同一個)。"""
 11131	    v = str(value).strip().replace("\\", "/")   # Windows 反斜線寫法也收(r3 邊界席:原本永遠「找不到」)
 11132	    if not v:
 11133	        return None, "about_code 不能是空的"
 11134	    if Path(v).is_absolute():
 11135	        return None, f"about_code 要寫 repo 相對路徑,「{v}」是絕對路徑"
 11136	    root = _vault_repo_root(env).resolve()
 11137	    target = (root / v).resolve()
 11138	    try:
 11139	        relp = target.relative_to(root).as_posix()
 11140	    except ValueError:
 11141	        return None, f"「{v}」跑出這個 repo 了(repo 根是 {root})"
 11142	    if not target.is_file():
 11143	        return None, (f"「{v}」不是這個 repo 裡的檔案" + ("(它是目錄;about_code 要寫到檔案)" if target.is_dir() else "(找不到)"))
 11144	    # ★大小寫要跟磁碟上的真實檔名一致★(r2):排序加分拿這個值去比對 git 的改動路徑(大小寫敏感);
 11145	    # 大小寫不敏感的檔案系統上 SRC/A.TS 也通過 is_file,存進去就永遠對不上
 11146	    # 只差 Unicode 正規化寫法(é 一個字 vs e 加重音符號)的是同一個檔,不算寫錯:Mac 的磁碟兩種都認,
 11147	    # 目錄清單卻只列存進去的那一種(派第三輪之前自己抓到的誤擋)——兩邊都轉成 NFC 再比。
 11148	    # ★讀不到目錄的檔名清單就擋★(r3 併發資源席:原本當成「寫對了」放行,錯字大小寫照樣存進去)
 11149	    real, unreadable = _disk_spelling(root, relp)
 11150	    if unreadable:
 11151	        return None, f"讀不到目錄 {unreadable} 的檔名清單,沒辦法確認「{v}」的大小寫有沒有寫對"
 11152	    if nfc(real) != nfc(relp):
 11153	        return None, f"「{v}」的大小寫跟磁碟上的檔名不一致(磁碟上是 {real})"
 11154	    return relp, None
 11155	
 11156	
 11157	def cmd_append(env, rel, key, value):
 11158	    with _vault_write_lock(env.vault):
 11159	        return _cmd_append_locked(env, rel, key, value)
 11160	
 11161	
 11162	def _cmd_append_locked(env, rel, key, value):
 11163	    if key not in LIST_KEYS:
 11164	        print(f"擋下:{key} 不能用 append 加,檔案沒動。append 只能加這些清單欄位:{sorted(LIST_KEYS)}(純量欄位用 lumos set)", file=sys.stderr)
 11165	        return 2
 11166	    if key == "about_code":
 11167	        value, why = _about_code_path(env, value)
 11168	        if why:
 11169	            print(f"擋下:{why},檔案沒動。about_code 要填這個 repo 裡真的存在的程式檔(repo 相對路徑)", file=sys.stderr)
 11170	            return 2
 11171	    path = env.vault / rel
 11172	    lines, s, e = load_raw_for_edit(path)
 11173	    if key == "about_code":
 11174	        root = _vault_repo_root(env).resolve()
 11175	        want = _about_code_key(root, value)
 11176	        same = [x for x in as_list(parse_frontmatter(lines[1:e])[0].get(key)) if _about_code_key(root, x) == want]
 11177	        if same:
 11178	            hint = "" if value in same else f"(現有寫法是 {same[0]},指的是同一支檔;要換成 {value}:先 remove 再 append)"
 11179	            print(f"✓ {rel} 的 {key} 已經有 {value}{hint},檔案沒動")
 11180	            return 0
 11181	    new_fm = edit_fm_append(lines[1:e], key, value)
 11182	    if new_fm == lines[1:e]:
 11183	        print(f"✓ {rel} 的 {key} 已經有 {value},檔案沒動")
 11184	        return 0
 11185	    new_lines = lines[:1] + new_fm + lines[e:]
 11186	    tgt = link_target(value)
 11187	    before = {t for t in (link_target(x) for x in as_list(parse_frontmatter(lines[1:e])[0].get(key))) if t}   # 空值不算一項
 11188	    # 寫完讀回來:新的那項在,★原本的每一項也都還在★(第三輪外家找洞席:只驗新項,舊項被改壞也過)
 11189	    atomic_write_verify(path, new_lines, key,
 11190	                        lambda f: tgt in {link_target(x) for x in as_list(f.get(key))}
 11191	                        and before <= {link_target(x) for x in as_list(f.get(key))})
 11192	    print(f"✓ append {rel}: {key} 多了一項 {value}")
 11193	    return 0
 11194	
 11195	
 11196	def cmd_remove(env, rel, key, value):
 11197	    with _vault_write_lock(env.vault):
 11198	        return _cmd_remove_locked(env, rel, key, value)
 11199	
 11200	
 11201	def _cmd_remove_locked(env, rel, key, value):
 11202	    """T1 list 項移除(append 逆操作)。補的是 2026-08-11 實戰撞到的缺口:
 11203	    死背書(verified_by 指向已 superseded 的驗證)、降格後殘留的 core_refs 指針,
 11204	    都只能靠移除 list 項來收,但 set 只收純量、append 只能加,唯一合法退路
 11205	    (obsidian processFrontMatter)還要 Obsidian 開著 → 實務上等於無路可走。
 11206	
 11207	    ★不命中一律 rc=2★:打錯字卻回成功,會讓呼叫端以為清乾淨了(死背書照舊掛著),
 11208	    比報錯危險得多。
 11209	
 11210	    ★2026-08-23 擴充:value 省略 = 把純量欄位整個拿掉★(design-loop about-code-field r3:
 11211	    回滾要「刪 stamp」,但 set 只能覆寫、沒有刪除原語——回滾最後一步是空的)。
 11212	    不加新子命令,remove 一個指令學一次。守衛:type/status/created 是筆記骨架,刪了 lint/doctor
 11213	    全炸,硬擋;清單欄位不准省略 value(避免一句話誤刪整個 verified_by)。"""
 11214	    if value is None:
 11215	        return _cmd_remove_scalar(env, rel, key)
 11216	    if key not in LIST_KEYS:
 11217	        print(f"擋下:{key} 不能用 remove 刪,檔案沒動。remove 只能動這些清單欄位:{sorted(LIST_KEYS)}"
 11218	              f"(純量欄位要整個拿掉:不帶 value)", file=sys.stderr)
 11219	        return 2
 11220	    path = env.vault / rel
docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md:22:  FLOW:重建節點 → lumos set regen from-scratch/日期 蓋章 → summary 逐 claim 標身分([src:]/[git:]/推測:/佚失:) → lint/doctor 共用 check_regen_provenance 執法 → 查證後補證據或 signoff 升級
docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md:24:  KEY:J-a 拒發明合約(regen 節點 INVARIANT 標記行需 [src:]/[git:] 意圖證據,與 Check T [test:] 疊加——test 證行為,src/git 證意圖)｜J-b DECISION 四態(證據/推測/佚失/裸→擋)｜J-c substring gate(_validate_repo_ref 直驗+token 消毒:空/絕對/.. traversal 皆 missing;git cat-file;shallow 降 warn 顯性+僅 --ci 落帳)｜J-d 無標記 KEY 行唯讀提醒
docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md:25:  KEY:共用 check_regen_provenance(note,repo_root)->(errs,warns,gov_events),lint 與 doctor 同函式防兩入口漂移;映射:errs→lint rc1/doctor warn(hard),warns→兩入口皆非阻擋,gov_events→僅 doctor --ci;雙報消歧 predicate=regen 節點推測+INVARIANT 同行恰一則 J 訊息、非 regen generic 兜底
docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md:26:  KEY:★DEBT★ 宣告制 opt-in——不蓋 regen 章完全繞過 Check J,且繞過無留痕、無 Check H 式軟提醒對應;「疑似重生未標」自動偵測留未來
docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md:29:  TEST:27 格綠(t_check_j_regen 24+t_check_j_git 3,含 shallow clone 真實測+token 消毒迴歸);全套 1157
docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md:34:# check-j-regen-guard
skills/lumos-project-notes/reference.md:634:2. 重建完蓋章:`lumos set <節點> regen from-scratch/<日期>`(`regen` 在 SCALAR_KEYS 白名單)。
skills/lumos-project-notes/reference.md:640:4. `lumos lint <節點>` 立驗;doctor 全圖同規(共用 check_regen_provenance,兩入口不漂移)。
skills/lumos-project-notes/reference.md:642:**Check J 四檢**(只對 regen 節點):
skills/lumos-project-notes/reference.md:643:- **J-a(擋)**:★INVARIANT★ 行無 [src:]/[git:] → 擋。[test:] 只證「行為現在成立」,不證「意圖是合約」——重建場景把偶然合約化是頭號毒;regen 節點的合約=[test:] **且** [src:]/[git:] 疊加。
skills/lumos-project-notes/reference.md:681:- **蓋章**:`lumos set <節點> regen from-scratch/<日期>`(不蓋=Check J 不看;蓋了才守)。
skills/lumos-project-notes/reference.md:1094:- **4|落節點**:前置=進場三分岔(已存在且健全→不動;殘缺→照〈重生守衛〉第一條 diff 更新別整篇換;從零→往下)。起手 `lumos new system <模組> --code <它管的檔> … --responsibility "<負責什麼、不負責什麼>"`(每支檔有家,2026-09-11:一個模組一篇、它管的檔寫進 about_code、別人的檔用連結;提交前擋沒家的新檔與新寫進去的別人檔名,見 [[Projects/每支檔有家_計劃]])——骨架只有 FLOW/KEY/DEP/TEST 四行,**DECISION 行要手動加**;summary 區塊只能 Edit 手改,注意 YAML 縮排與結尾 `---`。行分工:FLOW/DEP=指針級快寫;KEY=關鍵事實,**步驟 2 的共用清單落這裡**(`KEY:共用面:被 X/Y 使用(承重牆)[src:…]`——別塞 DEP,DEP 是「這篇依賴誰」的反方向);**考古出的 why 放 DECISION 行**(J-b 硬擋保護;放 KEY 只有軟提醒)。時序:**正文與身分標記全部寫完 → `lumos set <節點> regen from-scratch/<日期>` 蓋章 → `lumos lint` → 同一次 commit**;出口審計抓到要修=正常的後續 commit。多節點同批落按**依賴拓撲序**(從 FLOW/DEP 推,先底層後上層)。**知識分工**:半衰期短、跟單檔綁死的細節就地寫 code 註解,長脈絡與跨檔 why 才進圖譜。落完 `lumos link-candidates <主要 code 檔>` 看有沒有既有節點該連。
skills/lumos-project-notes/reference.md:1100:**機械把關的真實範圍(誠實地圖)**:Check J 只掃 summary 行——硬擋=J-a(★INVARIANT★ 缺意圖證據)、J-b(DECISION 行缺標記)、J-c(懸空指針,**逐行跑**、FLOW/DEP 帶指針照樣驗,但只驗存在不驗「證據真的支持主張」);J-d 對沒標身分的 KEY 行只計數提醒。regen 章是宣告制,不蓋完全繞過。prose 級誠實機械驗不了——防線是步驟 6 的交叉審計。
skills/lumos-project-notes/commands/09-節點還原.md:10:| 步驟 4:落節點 | `lumos new system <模組> --code <它管的檔> … --responsibility "<負責什麼、不負責什麼>"`(每支檔有家:一個模組一篇、別人的檔用連結,提交前會擋沒家的新檔) → Edit 摘要(DECISION 行手動加) → `lumos set <節點> regen from-scratch/<日期>` → `lumos lint <節點>` → `lumos link-candidates <主要 code 檔>` |

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'nl -ba skills/lumos-project-notes/commands/09-節點還原.md'[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
     1	# 09|節點還原(brownfield 冷啟動)
     2	
     3	白話:接手圖譜空或稀疏的既有專案,把功能脈絡還原成節點。**完整七步與紅線在 `reference.md`〈節點還原(brownfield 冷啟動)〉**;這裡只列「什麼時候敲哪個」。進場三分岔以該節為正本,此表只放指標。
     4	
     5	| 你正在… | 敲 |
     6	|---|---|
     7	| 進場判斷(有→照慣例用;殘缺→diff 補;沒有→往下) | 先 `lumos search <詞>`,命中再 `lumos context <節點>` |
     8	| 步驟 0:裝殼+填骨架導覽頁 | `lumos init`,然後 Edit 填 init 已建好的 `MOC/index.md`(別另建) |
     9	| 步驟 1–3:定位/追流/考古 | 讀 code 與 git(冷啟動豁免,無 lumos 指令;招式見 reference 該節) |
    10	| 步驟 4:落節點 | `lumos new system <模組> --code <它管的檔> … --responsibility "<負責什麼、不負責什麼>"`(每支檔有家:一個模組一篇、別人的檔用連結,提交前會擋沒家的新檔) → Edit 摘要(DECISION 行手動加) → `lumos set <節點> regen from-scratch/<日期>` → `lumos lint <節點>` → `lumos link-candidates <主要 code 檔>` |
    11	| 步驟 5:合約候選 | 開 `## 合約候選(收斂時複核,候選≠已標)` 章節於還原批次的計劃筆記;升格走 guard 三件(見 reference〈lumos guard〉) |
    12	| 步驟 6:出口查核+留痕 | 變體 B 派工(逐節點雙 Sonnet)→ 建 Verification+`lumos sync-verified-by --apply` → 逐節點 `lumos self-audit <節點>` |

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba skills/lumos-project-notes/reference.md | sed -n '620,700p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
   620	> 天花板:Check T 只驗測試識別子存在、不驗跑綠(CI 的事);E2E(maestro/playwright)要裝置/瀏覽器(無裝置才 skip);跨 repo 只讀不寫。**撰寫期用 Maestro MCP / Playwright MCP** 把 scaffold 的紅燈 stub 填到綠(開發工具、非合約守門)。
   621	> - **自我供裝(缺就自動裝、別叫使用者手動)**:要用該 MCP 但工具清單裡沒有(deferred 也 ToolSearch 不到)→ 先 `claude mcp list` 確認,沒有就自動配置再用:
   622	>   - Playwright(web):`claude mcp add playwright npx @playwright/mcp@latest`(前置 Node18+;首用 `npx playwright install` 裝瀏覽器)
   623	>   - Maestro(mobile):先裝 CLI `curl -Ls "https://get.maestro.mobile.dev" | bash`,再 `claude mcp add maestro -- maestro mcp`
   624	>   - 裝完**重啟 session** 或重跑 ToolSearch 讓 MCP 工具載入,再繼續填 stub。E2E 仍需模擬器/真機(mobile)或瀏覽器(web)才跑得起來。
   625	>   - 供裝是這條 workflow 的預設動作;唯一該先問人的情況 = 該機器有明確不得自動裝軟體的政策。
   626	> **stub 的紅燈哨兵放在 skip 之前**——未填的整合守衛在無 DB 的 PR CI 也會紅(不被 skip 掩蓋成假綠);填完斷言後刪哨兵行,skip 才恢復「無 DB 才 skip」。
   627	
   628	### 重生守衛(Check J):from-scratch 重建節點的 provenance 分級(2026-07-16)
   629	
   630	**問題**:重建(目擊記錄佚失/接手 legacy/整篇重寫)=從 code 快照逆向工程 why——AI 沒有目擊記憶,會編出自信但腦補的「當初為什麼」;最毒是發明假合約(把偶然寫法標成 ★INVARIANT★ 鎖死重構)。統一原則:**讓重建優雅退化成「誠實的、分級的不確定」,把缺口變可見+有型別,不編自信 prose**。設計全文與三輪對抗審:`Projects/from-scratch重生守衛_計劃`+`governance/golden/fromscratch-m1/`。
   631	
   632	**完整工作流**:
   633	1. 重建前:舊節點還在就 **diff 更新別整篇換**(保住殘存目擊內容);真要從零才走本流程。
   634	2. 重建完蓋章:`lumos set <節點> regen from-scratch/<日期>`(`regen` 在 SCALAR_KEYS 白名單)。
   635	3. summary 每條 claim 標身分(**只掃 summary 行**,body 內標記是人讀輔助、機器不執法):
   636	   - `[src:路徑]` / `[src:路徑:行號]` — Tier A,現 code 可驗(行內 bracket 指針,同 [test:] 族)
   637	   - `[git:sha]` — Tier B,變更事件作證(commit/revert/PR;7-40 位 hex)
   638	   - `推測:` — Tier C 前綴,**緊接在 KEY:/DECISION: 後**(`KEY:推測: ...`);沒證據的推論顯式標
   639	   - `佚失:` — 前綴同上;證據已不存在,老實留空不編
   640	4. `lumos lint <節點>` 立驗;doctor 全圖同規(共用 check_regen_provenance,兩入口不漂移)。
   641	
   642	**Check J 四檢**(只對 regen 節點):
   643	- **J-a(擋)**:★INVARIANT★ 行無 [src:]/[git:] → 擋。[test:] 只證「行為現在成立」,不證「意圖是合約」——重建場景把偶然合約化是頭號毒;regen 節點的合約=[test:] **且** [src:]/[git:] 疊加。
   644	- **J-b(擋)**:DECISION 行無證據指針且未標 推測:/佚失: → 擋(重建的 why 必須標來源或標推測)。
   645	- **J-c(擋,substring gate)**:[src:] 真開檔驗存在+行號範圍;[git:] 真跑 cat-file 驗 commit;假路徑/空白/絕對路徑/`..` traversal/假 sha 全擋(防幻覺證據)。shallow clone 驗不到 git 物件→降警告不擋+顯性標示(僅 doctor --ci 落治理帳)。
   646	- **J-d(提醒不擋)**:無標記 KEY 行計數提醒(prose 級誠實機械驗不了)。
   647	- **不對稱接線**:`推測:`/`佚失:` 行不得承載 ★INVARIANT★/★IRREVERSIBLE★(合約不能建在推測上)→ 擋,恰一則專屬訊息。
   648	
   649	**升級路徑**:推測→查證後補 [src:]/[git:];或業務面人工確認走 `lumos signoff`。**天花板**:J-c 只驗「指針可解析」不驗「內容真支持 claim」(語意層靠對抗審/人);佚失的 why 永久佚失,正確輸出是「佚失:」——嚴禁編一個合理的(把「不知道」渲染成「知道」正是 code 衍生 wiki 的原罪,見 `Systems/外部對照-code衍生wiki`)。
   650	
   651	
   652	> （以下為 2026-08-22 搬入版，精簡重述以上 ★INVARIANT★/★DEBT★/[test:]/[audit:]/[kill:]/[rollback:]/重生標記各節；兩版並存）
   653	
   654	### 合約性標記(合約 vs 偶然;最重要,動筆前掃一眼)
   655	
   656	Systems 記的是「現在長怎樣」,分不出哪些是**合約**(改=breaking)哪些是**偶然**(可改)。用 KEY 行前綴聲明:
   657	
   658	```
   659	KEY:★INVARIANT★ <業務合約,改=breaking> [test:測試名] [audit:模型/日期] [kill:recipes]
   660	KEY:★DEBT★ <已知偶然行為,可改不算 breaking>
   661	```
   662	- **未標 = 未聲明**;**不確定就不標**(寧漏勿錯)。**嚴禁從現況 code 反推「應該是合約吧」**——把偶然合約化會鎖死重構,比沒標更毒。只有業務語意明確或 decisions[] 載明意圖才配 ★INVARIANT★。
   663	- 跨專案級不變量不在這標 → 走 `lumos-core-knowledge` 升格,KEY 留 `CORE:` 指針。
   664	
   665	**合約鏈(行尾指針,遞增嚴格;深度規格見 `reference.md`)**:
   666	- `[test:方法名]` — 綁一個真實測試(doctor Check T 強制,裸合約擋)。**綁定走指令**:`lumos guard bind <node> "<KEY子字串>" <測試名>`。
   667	- `[audit:模型/日期]` — 綁測試後,合法性須經**無脈絡獨立 agent** 審過(prompt 中立「試圖反駁」,不帶風向;**判準=五問 rubric 逐條打勾,五項全過才 legal**——意圖證據/合約vs偶然/測試夠格/可證偽/爆炸半徑,含穩定性探針與防應試化兩道,完整規格見 reference.md〈[audit:] 獨立合法性審計〉段)。`lumos guard audit <node> "<KEY子字串>"`。
   668	- `[kill:recipes]`(選配,金流建議)— 沙盒真弄壞、綁定測試必翻紅。`lumos guard kill-add` / `kill`。
   669	- **綁 `[test:]` 前對照 [[Systems/測試假綠形態]] 八型清單**——綁上去的測試若中了其中一型,合約鏈看起來完整、實際什麼都沒守住(★最隱蔽的是「現場走不到被測分支」★:把修法還原回去測試照樣全綠)。修 bug 的翻紅釘★必須配一條「現場成立」前置斷言★。
   670	- **天花板**:[test:] 只買 verification;「這規則現在還符不符合真實業務」是 validation,要對業務現實的人確認(`lumos signoff`)。
   671	
   672	**可逆性(危險動作動手前先寫好收回,僅 Systems)**:
   673	```
   674	KEY:★IRREVERSIBLE★ <收不回:上架/prod遷移> [rollback:decisions]   # 必綁,否則 doctor Check R 擋
   675	KEY:★CHECKPOINT★   <改了難救>                                     # 建議補 [rollback:],缺=提醒不擋
   676	```
   677	外部不可逆(信已送/下游已消費)→ 改用 `[guard:decisions]`(事前冪等鍵/核可閘)。`[rollback:]` 證「有寫 undo」≠「驗過能跑」。
   678	
   679	**重生標記(from-scratch 重建的節點必蓋,Check J 守衛)**:
   680	- **何時**:目擊記錄佚失/接手無人 legacy/整篇重寫——由 AI 看 code「重建」筆記時(≠平常 incremental 更新)。重建=逆向工程,可能編出自信的假 why/假合約,故課更嚴檢查。
   681	- **蓋章**:`lumos set <節點> regen from-scratch/<日期>`(不蓋=Check J 不看;蓋了才守)。
   682	- **summary 每條 claim 標身分**(四選一):`[src:路徑(:行號)]` code 作證(Tier A)/`[git:sha]` 提交作證(Tier B)/`推測:` 前綴=沒證據的猜(接在 KEY:/DECISION: 後)/`佚失:` 前綴=查不到,不編。
   683	- **Check J 擋什麼**(lint/doctor 自動):★INVARIANT★ 無 [src:]/[git:] 意圖證據→擋(拒發明合約);DECISION 裸寫→擋;證據指針假的(檔案不存在/行號越界/git 查無)→擋;`推測:` 行承載 ★合約→擋。無標記 KEY 行只提醒不擋。
   684	- **升級**:查證後補 [src:]/[git:] 或走 `lumos signoff`;**佚失的 why 正確輸出是「佚失:」,嚴禁編一個合理的**。深規見 `reference.md`〈重生守衛〉段。
   685	
   686	---
   687	
   688	
   689	---
   690	
   691	
   692	### 設計審查收斂閘(現行;從舊 canary 節抽出的兩句,因為是全檔唯一出處)
   693	
   694	> 現行:輪記帳 `lumos canary record none ...`(純處置帳載體);「審計員有沒有讀」由 quote-check 引句錨定把關;收斂閘=design-loop 與 code-loop 皆 `loop status --disposal`(code-loop 自 2026-08-08 起;見 lumos-code-loop skill);`--gate --panel` 僅供已定錨 panel 記帳的舊迴圈帳面重放。(原句全文見〈歷史與停用〉canary 節第一段。)
   695	> **gate 契約補注**:`--spec` 在 code-loop 情境可省略(`loop status --gate` G1 skip,無 spec 可驗引用座標屬預期);design/spec loop 仍帶 `--spec`(G1 會跑 refcheck 驗引用座標)。**design-loop 新制(2026-08-04)**:收斂閘改 `loop status --disposal --spec <計劃> --repo <root>`(處置閘各步:G3∧處置帳全清∧留痕 sha 重驗∧quote-check 引句全錨定∧條款綁定(設計審,2026-09-08)∧資安席(代碼審 high,2026-09-11));panel 閘(`--gate --panel`)僅供已定錨 panel 記帳的舊迴圈與帳面重放——code-loop 自 2026-08-08 起亦走處置閘(2026-08-25 d2 訂正,原「留給 code-loop」說法過期)。
   696	
   697	## 決策與驗證
   698	
   699	### decisions 欄位（ADR：決策時間有效性 + 為什麼選/為什麼不選）
   700	

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba skills/lumos-project-notes/reference.md | sed -n '1060,1135p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
  1060	2. **計數/清單型主張最會漂**（「共 5 處」「6 個檔案」「1 筆」）——寫筆記時這類數字要附截至日期或乾脆不寫死
  1061	3. 有筆記**引用了 codebase 不存在的方法名**（從未實證過就寫進去）——升格任何主張前先 grep 一次
  1062	4. 同篇筆記可能 KEY 行已更新、decisions 卻沒標 superseded——**自相矛盾**型,審計時兩處都要看
  1063	
  1064	
  1065	> 「對抗設計審計的 canary」原文（2026-06-19 制定、2026-08-14 全面停用）已搬至〈歷史與停用〉章，僅供回放舊帳判讀，此處不留副本。
  1066	
  1067	> （以下為 2026-08-22 搬入版，精簡重述自足性審計流程；兩版並存）
  1068	
  1069	### 自足性審計(圖譜實質更新後必做)
  1070	
  1071	派**乾淨 sonnet agent 只讀圖譜**還原脈絡 → 主對話比對「還原結果 vs 腦中現存脈絡」:有出入 = 圖譜當下不健全,補缺後**重審到一致**。純格式修正可豁免。審過留痕:`lumos self-audit <node>`(doctor Check S 軟提醒未審/過期)。
  1072	> 無主對話脈絡時(定期巡檢/接手陌生專案)→ 改用「圖譜×程式碼交叉審計」(以 code 為真值),做法見 `reference.md`。
  1073	> 對抗**設計稿**審計(乾淨 agent 逐輪找洞+引句錨定收貨)→ 走 `lumos-design-loop` skill,不在此。
  1074	
  1075	---
  1076	
  1077	
  1078	---
  1079	
  1080	## 節點還原（brownfield 冷啟動）
  1081	
  1082	> 白話:接手一個已經在跑、但圖譜是空的(或很稀疏)的專案——七步把功能脈絡從 code 和 git 裡還原成節點。守衛端(〈重生守衛(Check J)〉,見〈合約性標記與合約鏈〉大節)管「重建不准瞎編」;本節管產出端:建哪些、從哪開始、還原到多深。設計脈絡與六輪審計史見 [[Projects/節點還原SOP_計劃]]。
  1083	
  1084	**何時用**:裝了 lumos、圖譜空或稀疏的既有專案;或目擊紀錄佚失的舊模組。最典型觸發:要在龐大既有 codebase 上**加新功能**——先把會碰到的關聯面還原成節點,新功能踩在節點上開發;還原產出直接變成新功能 spec 的護欄素材(共用面清單=不准亂動的承重牆;合約候選=「改了就壞」的**候選**紅線——候選≠已驗,升格走 guard 全鏈才算合約,下游當警示線索不當已證邊界),code-loop 的架構對齊席負責抓「跟既有寫法不一樣」,high 的資安席負責抓能被利用的洞。
  1085	
  1086	**生長哲學=惰性(進場三分岔,本節為正本)**:節點不整倉攤平。進場先查——先 `lumos search <詞>`,命中再 `lumos context <節點>`(接續關係,不是二選一):**有且健全→照既有慣例用,不動它;有但殘缺/過時→照步驟 4 的前置 diff 更新;沒有→走七步產一篇**。圖譜沿著實際被動過的面慢慢長回原始樣貌,永遠不欠「全倉還原」的債(Strangler fig 漸進接管在知識層的同構)。
  1087	
  1088	**七步(步驟 0–6)**:
  1089	
  1090	- **0|進場與最小骨架**:圖譜空 → `lumos init` 裝殼——init **已自動建好** `MOC/index.md` 空殼,**填它、不要另建**(`lumos new` 沒有 moc 型)。正文用 Edit 填:repo 是做什麼的、幾個大件、各自入口在哪(檔案/目錄指針);只寫指針不寫敘事。**先策展再自產**:README/既有 ADR/測試名先撿,撿得到算有據、撿不到才寫推測。**整頁當假設經營**(reflexion models 式):步驟 2 追流或步驟 6 審計完成後,實際依賴與骨架頁不符就**當場 Edit 骨架頁**(對上的改標有據、猜錯的改寫或補新增、不存在的刪)——靠紀律,無機械掛鉤。**骨架停手線:一篇、指針 ≤30 行、不展開**;超大 monorepo 只列第一層大件。
  1091	- **1|錨點階梯定位**(冷啟動場景本步含 2–3 直接讀 code,不算違反「lumos 優先」——那條管圖譜有料時):①**獨特字串**(畫面文字/元素 class、CLI --help 或輸出、log 訊息/錯誤碼、字串資源檔)②抓不到(minify/生成碼)→**識別子**(函式/類名/路由/協定欄位/暫存器位址;i18n 兩跳:畫面文字→語系檔抓 key→再搜誰用 key)③都沒有→**結構文件**(建置腳本、DAG 定義、接腳表、部署設定)④一到三級全滅→**動態差分**(software reconnaissance,1995):「會踩到該功能」與「不會踩到」兩情境各跑一次,收執行軌跡或覆蓋率相減——工具用**目標專案自己棧內的**(pytest-cov/JaCoCo/Istanbul 類),與 lumos 零依賴家規無關。**錨點信度**:兩種獨立技術交叉命中才算高(綜述定性結論:混合勝單一)。**兩條紅線**:④前置=能建置、能跑、能收軌跡,不成立(vendor 壓縮碼常態)→退回③老實標推測/佚失,不硬跑;**金流/對外送出/不可逆的功能,禁止在生產環境跑「會踩到」情境**(那等於真的觸發一次)——只准在「斷真實外部端點(webhook/郵件/簡訊)、用測試憑證/假身分、資料可重置」三項齊備的隔離環境,湊不齊就不用這招。
  1092	- **2|追流+圈承重牆**:這個單元的輸入從哪來、輸出到哪去、**誰還共用它**。共用面**至少兩個來源**:①拿單元名全域搜用法 ②該棧的間接接線處(DI/IoC 設定、路由表、DAG 依賴清單、建置依賴圖、事件訂閱表);加分來源:git co-change(長期共改=行為上共用)、步驟 1 若跑了動態差分則兩情境軌跡**交集是候選線索**(不是定義——啟動器/登入/遙測雜訊會進交集,先濾掉與功能無關的共通路徑再過兩來源複核)。**要下「沒有別人共用」的否定結論、且它會決定少建節點時:照 CLAUDE.md ★第四條派乾淨 agent 拿原始問題對一次,這個場合沒有降級選項**。順手圈出專案自己的錯誤語言(包裝過的 logger、錯誤碼表——部落知識,git 考古不出來)。產出:FLOW 一行+共用清單。
  1093	- **3|考古還原 why**:git 為主——`git log -S'字串'` 找這行哪次進來/離開、`-G` 吃正則、`git log -L` 追函式全史、blame 撞搬家用 `git blame <sha>^ -- 檔` 重跳;**blame 到 squash commit 別停:撈 PR 編號去讀討論串**(理由主要藏在 issue/PR,squash 只抹平 git 內的顆粒)。git 沉默→**非 git 來源**(issue tracker、wiki、部署文件、硬體資料手冊),都沒有才標佚失。標身分:有據標 `[git:sha]`/`[src:路徑:行號]`;推論標 `推測:`;查不到標 `佚失:`——**語序:標籤後可有空白,但 `推測:`/`佚失:` 必須是第一個非空白內容**(`DECISION:推測:依據…`、`DECISION: 推測:依據…` 都合法;`DECISION: 原因不明,推測:…` 夾了文字不算)。**佚失是合格產出**(squash 起家大量佚失是預期);嚴禁從「現在長怎樣」反推發明「當初為什麼」;**`推測:` 行不准引具體識別子當佐證**(編造最常長在像真的細節上)。**考古紅線**:git log/PR/issue 常夾憑證、資安細節、人事內容——**不入圖譜**,只記「涉敏感背景,細節不錄」。
  1094	- **4|落節點**:前置=進場三分岔(已存在且健全→不動;殘缺→照〈重生守衛〉第一條 diff 更新別整篇換;從零→往下)。起手 `lumos new system <模組> --code <它管的檔> … --responsibility "<負責什麼、不負責什麼>"`(每支檔有家,2026-09-11:一個模組一篇、它管的檔寫進 about_code、別人的檔用連結;提交前擋沒家的新檔與新寫進去的別人檔名,見 [[Projects/每支檔有家_計劃]])——骨架只有 FLOW/KEY/DEP/TEST 四行,**DECISION 行要手動加**;summary 區塊只能 Edit 手改,注意 YAML 縮排與結尾 `---`。行分工:FLOW/DEP=指針級快寫;KEY=關鍵事實,**步驟 2 的共用清單落這裡**(`KEY:共用面:被 X/Y 使用(承重牆)[src:…]`——別塞 DEP,DEP 是「這篇依賴誰」的反方向);**考古出的 why 放 DECISION 行**(J-b 硬擋保護;放 KEY 只有軟提醒)。時序:**正文與身分標記全部寫完 → `lumos set <節點> regen from-scratch/<日期>` 蓋章 → `lumos lint` → 同一次 commit**;出口審計抓到要修=正常的後續 commit。多節點同批落按**依賴拓撲序**(從 FLOW/DEP 推,先底層後上層)。**知識分工**:半衰期短、跟單檔綁死的細節就地寫 code 註解,長脈絡與跨檔 why 才進圖譜。落完 `lumos link-candidates <主要 code 檔>` 看有沒有既有節點該連。
  1095	- **5|合約候選,不升格**:「改了就壞」清單開 `## 合約候選(收斂時複核,候選≠已標)` 章節,**放這次還原批次的計劃筆記**(Projects/——既有先例全在那,零篇在 Systems);Systems 節點只在對應 KEY 行旁註「合約候選」。**本步到此為止**。升格是另一次任務:取得意圖證據→改標 ★INVARIANT★→`guard scaffold`→寫測試→`guard bind`→`guard audit`(實形照本檔〈lumos guard〉段,不重抄)。專案沒測試→先補特徵化測試(Feathers:釘現況行為、不判對錯;綁不上≠降格,標「待 seam」;golden master 適合 AI 代產;綁上後 mutation 驗收——變異不翻紅的測試不算數)。
  1096	- **6|出口:交叉查核+雙軌留痕**:先**指針級機械核對**——蓋章時 lint 的 J-c 已驗 summary 裡的指針(注意:shallow clone 下 `[git:]` 找不到物件只警不擋,full clone 才算驗過,shallow 要在下述階段二補驗);報告級引用用 `lumos refcheck`(只認**反引號包住的** path[:行號] 且首段是現存頂層目錄;裸寫座標與裸函式/欄位名驗不了——誠實邊界;`lumos search --code` 搜的是筆記不是 codebase,別當 code 側掃描用)。再跑**變體 B 交叉審計**(機制原文見上面〈自足性審計〉變體 B 節):**逐節點**各派兩個乾淨 **Sonnet** agent——階段一只讀單篇筆記萃取 12~15 條可被程式碼驗證的具體主張(且逐條可證偽),階段二只讀 code 逐條判 ✅/❌/❓。本 SOP 的兩條延伸裁定:還原批次**必跑**;**❓ 不可原樣放行**(回頭改標推測/佚失或修掉)。處置:❌ 修筆記(**以 code 為準**;code 本身是 bug 就開 Issue 不改筆記遷就)。留痕**雙軌**:建 Verification 紀錄+`verified_by` 雙向同步,**且**逐節點蓋 `lumos self-audit <節點>`(先例:L4 清帳 30 節點雙軌全蓋)。之後要動 code,走現行紀律(`lumos impact`、design-loop、code-loop);還原節點日後被行為事實打臉→照家規立事故筆記+作廢/supersede,這就是還原內容的收回路徑。
  1097	
  1098	**深度停手線**(與步驟 0 的骨架停手線是兩條規則):夠=這次任務要動的面+它的共用面有節點;不追求覆蓋率、不為還原而還原。深挖由下一個任務驅動。
  1099	
  1100	**機械把關的真實範圍(誠實地圖)**:Check J 只掃 summary 行——硬擋=J-a(★INVARIANT★ 缺意圖證據)、J-b(DECISION 行缺標記)、J-c(懸空指針,**逐行跑**、FLOW/DEP 帶指針照樣驗,但只驗存在不驗「證據真的支持主張」);J-d 對沒標身分的 KEY 行只計數提醒。regen 章是宣告制,不蓋完全繞過。prose 級誠實機械驗不了——防線是步驟 6 的交叉審計。
  1101	
  1102	## 同步規則（何時更新知識圖譜）
  1103	
  1104	### 程式碼變更後（必做）
  1105	更新對應 Systems 筆記：
  1106	- 串接狀態（mock → 已串接）
  1107	- 新增/修改的檔案、API 端點
  1108	- DB 表結構變更
  1109	- 待辦完成打勾（`obsidian task ... done`）
  1110	
  1111	### 更新筆記後（必做）
  1112	`lumos backlinks <剛改的節點>` 看誰引用它 → `lumos search <相關關鍵字>` 逐一確認是否過時。
  1113	
  1114	### 發現 Issue 時
  1115	`lumos new issue <名稱>` 建檔 → `lumos set` 填 status/type/priority → body 用 Edit 寫現象/相關系統/解法/狀態。
  1116	
  1117	### 里程碑完成時
  1118	`lumos set <計劃> status done` + `lumos set <計劃> updated <日期>`;相關 Issue 一併 `lumos set ... status done`。
  1119	
  1120	### 退場自問（code 有「拿掉/反轉」的改動時，收工前跑一遍）
  1121	
  1122	1. 這次改動**拿掉或反轉**了什麼？（函式/呼叫點/欄位/條件/預設值——過期幾乎都來自拿掉，不是新增）
  1123	2. 把那些名字逐個丟 `lumos search <名> --code`（--code 必帶：search 預設排除 code block；另注意預設排除 superseded）。哪些節點內文在講它們？貼原句。
  1124	3. 逐句判：改動後這句還成立嗎？成立→一句話為什麼；不成立→**現在改掉或標作廢**。
  1125	4. **這次有動到使用者看得到的畫面嗎？**（Android／web UI 都算）
  1126	   有 → 除了單元測試，補一支**可重放的 UI flow 檔**（Android＝maestro `.maestro/*.yaml`），
  1127	   並用 `[test:<平台>:<flow名>]` 綁回該功能的圖譜節點。
  1128	   ★斷言必須含「畫面上出現什麼字」★——只斷言「有沒有被擋」等於白做（實例：折扣超過 100%
  1129	   確實被擋，但畫面顯示的是登入頁的「請輸入員工編號!」，單元測試結構上測不到）。
  1130	   寫法與七個坑見 `reference.md` 的〈產 maestro UI flow 的派工要求〉。
  1131	   ★綁定前置★：`guard bind`／Check T **只認 `KEY:★INVARIANT★` 行**——該節點沒有合約行就
  1132	   **別為了綁而標**（鐵則：不確定是不是合約就不標）；先只寫 flow 檔、在節點內文記一句指向它。
  1133	   沒裝置／起不了環境 → **明記「未驗＋原因」**，不得靜默跳過。
  1134	⚠ 新增一條 verified_by/related 連結**不算同步**。有裝 delguard（pre-commit Gate DG）的 repo，S1 命中時會機械吐**上面 1-3 這三問**（delguard 不管 UI，第 4 問純靠自律）；沒裝的 repo 四問全靠這段自律。
  1135	

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/retrieval-ranking' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 213ms:[0m
# Systems/retrieval-ranking.md
type:system | status:done | created:2026-07-10 | updated:2026-08-18 | scope:retrieval
提醒:這篇有「動了會壞」的合約,動手前一定要看:
  ★DEBT★ 多詞片語候選=legacy片語語意(0候選不回退)★2026-08-02 部分緩解:`--any` 旗標(預設關)在整串片語全庫無命中時退成各詞 OR 召回;fallback-only 故對既有查詢零回歸(現有 goldset 30 題全部回>0候選,回退條件永不觸發)。Landmark 284 篇真庫實測:10/10 現實多詞查詢在預設下全 0 命中,`--any` 後 7/10 第一名正確。★2026-08-03 人裁翻預設★:多詞回退改為預設開、`--no-any` 逃生、`--any` 留相容。證據=補了 10 題多詞評測(雙評 Claude+Codex 跨家族、分歧交乾淨 opus 裁決):nDCG@5 0→0.767、MRR 0.95、第一名為「必看」7/10;對照組 5 題(現有命中的多詞查詢)逐檔完全相同=零回歸實證。誠實邊界:pooling bias(池半數來自回退自己)、n=10、單一快照。交付版已同步重生。見 [[Projects/檢索多詞回退_計劃]]★｜cochange proxy對圖譜related面太稀(兩vault實證,僅sanity check)｜hook接線v1.1待評測
summary:
  KEY:★2026-08-26 評測尺翻案(condensed,plan:[[Projects/評測尺翻案_計劃]])★——「未標=0」翻案:全品質尺加 condensed 版(觸及集窗內已判子列表計…
  KEY:[2026-08-24 固定席降噪A層落地,plan:[[Projects/固定席降噪A層_計劃]]]硬合約保送——LUMOS_IMPACT_HARD_PIN=1 時 indirect hop…
verified_by: [[Verification/2026-07-10_檢索排序v1]], [[Verification/2026-07-11_檢索goldset評測]], [[Verification/2026-07-11_hook面v1.1轉正]], [[Verification/2026-08-07_hook必看召回修復落地]], [[Verification/2026-08-07_連結缺失補全落地]], [[Verification/2026-08-18_標註刷新落地]], [[Verification/2026-08-18_edit面查詢品質閘落地]], [[Verification/2026-08-21_L4交叉審計30節點清帳]], [[Verification/2026-08-24_about_code讀側四項落地]], [[Verification/2026-08-24_固定席降噪A層落地]], [[Verification/2026-08-26_評測尺翻案落地]]
→ 連出 (16):
  • Projects/impact-diff橋接_計劃.md [done]
  • Projects/檢索優化_計劃.md [done]
  • Projects/檢索多詞回退_計劃.md [doing]
  • Projects/節點靜態先驗_調研.md [done]
  • Systems/lumos-cli-read.md [done]
  • Verification/2026-07-10_檢索排序v1.md [pass]
  • Verification/2026-07-11_hook面v1.1轉正.md [pass]
  • Verification/2026-07-11_檢索goldset評測.md [pass]
  • Verification/2026-08-07_hook必看召回修復落地.md [pass]
  • Verification/2026-08-07_連結缺失補全落地.md [pass]
  • Verification/2026-08-18_edit面查詢品質閘落地.md [pass]
  • Verification/2026-08-18_標註刷新落地.md [pass]
  • Verification/2026-08-21_L4交叉審計30節點清帳.md [pass]
  • Verification/2026-08-24_about_code讀側四項落地.md [pass]
  • Verification/2026-08-24_固定席降噪A層落地.md [pass]
  • Verification/2026-08-26_評測尺翻案落地.md [pass]
← 連入 (24):
  • MOC/index.md [doing]
  • Projects/GraphRAG對節點關聯_調研.md [doing]
  • Projects/edit面查詢品質閘_計劃.md [done]
  • Projects/hook必看召回修復_計劃.md [done]
  • Projects/impact-diff橋接_計劃.md [done]
  • Projects/impact鏡頭機械化_計劃.md [doing]
  • Projects/主session鏡頭利用率_計劃.md [doing]
  • Projects/固定席降噪A層_計劃.md [done]
  • Projects/圖譜進迴圈入口栓_計劃.md [done]
  • Projects/推播miss量測_計劃.md [done]
  • Projects/推筆記認家_計劃.md [doing]
  • Projects/標註刷新_計劃.md [done]
  • Projects/檢索edit面真紅_計劃.md [done]
  • Projects/檢索優化_計劃.md [done]
  • Projects/檢索多詞回退_計劃.md [doing]
  • Projects/派工鏡頭注入_計劃.md [done]
  • Projects/真遺忘召回過濾_計劃.md [done]
  • Projects/節點靜態先驗_調研.md [done]
  • Projects/送審前impact鏡頭機械化_計劃.md [done]
  • Verification/2026-07-10_檢索排序v1.md [pass]
  • Verification/2026-07-11_hook面v1.1轉正.md [pass]
  • Verification/2026-07-11_檢索goldset評測.md [pass]
  • Verification/2026-08-24_about_code讀側四項落地.md [pass]
  • Verification/2026-08-24_固定席降噪A層落地.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/retrieval-ranking'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 218ms:[0m
# Systems/retrieval-ranking.md
  ★DEBT★ 多詞片語候選=legacy片語語意(0候選不回退)★2026-08-02 部分緩解:`--any` 旗標(預設關)在整串片語全庫無命中時退成各詞 OR 召回;fallback-only 故對既有查詢零回歸(現有 goldset 30 題全部回>0候選,回退條件永不觸發)。Landmark 284 篇真庫實測:10/10 現實多詞查詢在預設下全 0 命中,`--any` 後 7/10 第一名正確。★2026-08-03 人裁翻預設★:多詞回退改為預設開、`--no-any` 逃生、`--any` 留相容。證據=補了 10 題多詞評測(雙評 Claude+Codex 跨家族、分歧交乾淨 opus 裁決):nDCG@5 0→0.767、MRR 0.95、第一名為「必看」7/10;對照組 5 題(現有命中的多詞查詢)逐檔完全相同=零回歸實證。誠實邊界:pooling bias(池半數來自回退自己)、n=10、單一快照。交付版已同步重生。見 [[Projects/檢索多詞回退_計劃]]★｜cochange proxy對圖譜related面太稀(兩vault實證,僅sanity check)｜hook接線v1.1待評測

合約 0 條(改了就是破壞性變更) | 技術債 1 條(可以改)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/節點還原' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 218ms:[0m
# Systems/節點還原.md
type:system | status:doing | created:2026-08-24 | updated:2026-08-24 | scope:node-content
summary:
  FLOW:進場三分岔(search 有→照慣例用/殘缺→diff 補/沒有→產)→七步:init 填骨架 MOC(假設經營+對帳)→錨點階梯定位(字串→識別子→結構文件→動態差分)→兩來源圈承重牆→g…
  KEY:哲學=惰性生長(需要才產、有就照慣例用,絕不整倉攤平——Strangler fig 同構);典型觸發=新功能開發前先還原關聯面,產出(共用面+合約候選)=新功能 spec 的護欄素材
verified_by: [[Verification/2026-08-24_節點還原SOP落地]]
→ 連出 (4):
  • Projects/節點還原SOP_計劃.md [done]
  • Systems/check-j-regen-guard.md [done]
  • Systems/外部對照-code衍生wiki.md [done]
  • Verification/2026-08-24_節點還原SOP落地.md [pass]
← 連入 (2):
  • MOC/index.md [doing]
  • Projects/推筆記認家_計劃.md [doing]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/節點還原'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 214ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/check-j-regen-guard' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 219ms:[0m
# Systems/check-j-regen-guard.md
type:system | status:done | created:2026-07-16 | updated:2026-07-16 | risk:守衛面 | scope:node-content
提醒:這篇有「動了會壞」的合約,動手前一定要看:
  ★DEBT★ 宣告制 opt-in——不蓋 regen 章完全繞過 Check J,且繞過無留痕、無 Check H 式軟提醒對應;「疑似重生未標」自動偵測留未來
summary:
  FLOW:重建節點 → lumos set regen from-scratch/日期 蓋章 → summary 逐 claim 標身分([src:]/[git:]/推測:/佚失:) → lint/d…
  KEY:解 from-scratch 重生塌陷——重建=從 code 快照逆向工程 why,AI 會編自信假 why/假合約;Check J 逼每條 claim 亮身分:有證據(且機械驗真)/推測/佚…
verified_by: [[Verification/2026-07-16_fromscratch守衛M1_CheckJ]]
plan_refs: [[Projects/from-scratch重生守衛_計劃]]
→ 連出 (5):
  • Projects/from-scratch重生守衛_計劃.md [doing]
  • Systems/check-t-sentinel.md [done]
  • Systems/lumos-refcheck.md [done]
  • Systems/外部對照-code衍生wiki.md [done]
  • Verification/2026-07-16_fromscratch守衛M1_CheckJ.md [pass]
← 連入 (6):
  • MOC/index.md [doing]
  • Projects/Agentflow吸收_調研.md [doing]
  • Projects/推筆記認家_計劃.md [doing]
  • Projects/節點還原SOP_計劃.md [done]
  • Projects/驗形式與驗內容_調研.md [doing]
  • Systems/節點還原.md [doing]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/check-j-regen-guard'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 210ms:[0m
# Systems/check-j-regen-guard.md
  ★DEBT★ 宣告制 opt-in——不蓋 regen 章完全繞過 Check J,且繞過無留痕、無 Check H 式軟提醒對應;「疑似重生未標」自動偵測留未來

合約 0 條(改了就是破壞性變更) | 技術債 1 條(可以改)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Issues/canary-record未落盤事件' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 214ms:[0m
# Issues/canary-record未落盤事件.md
type:issue | status:done | created:2026-07-29 | updated:2026-07-29 | scope:loop-engineering
summary:
  FLAG:TECHNICAL
  KEY:2026-07-28 code-testmap r2 三筆 canary record 工具回報成功(印出 CANARY-ae139e51/521d397f/031e7381)但檔案系統與 g…
→ 連出 (1):
  • Systems/canary-audit.md [deferred]
← 連入 (5):
  • Projects/Codex外審吸收_計劃.md [done]
  • Projects/oracle品質包_計劃.md [done]
  • Projects/接手視圖_計劃.md [done]
  • Verification/2026-07-29_oracle品質包落地.md [pass]
  • Verification/2026-08-22_成本欄接上與撤除兩階段.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Issues/canary-record未落盤事件'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 220ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Issues/code-loop守衛main-direct盲區' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 221ms:[0m
# Issues/code-loop守衛main-direct盲區.md
type:issue | status:done | created:2026-07-21 | updated:2026-07-21 | scope:guards-gates
summary:
  FLAG:TECHNICAL
  KEY:pre-push 的 tier=high→code-loop 硬擋守衛以 merge-base..HEAD 算 diff——**直接 commit 在 main 上時 merge-base==…
→ 連出 (2):
  • Projects/loop機械脊椎M1包_計劃.md [done]
  • Systems/pitfalls-code-loop.md [done]
← 連入 (3):
  • Issues/code-loop-pass自失效追尾.md [resolved]
  • Projects/prepush主幹範圍修法_計劃.md [doing]
  • Verification/2026-07-22_prepush範圍修法落地.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Issues/code-loop守衛main-direct盲區'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 218ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Issues/hook卸載殘留註冊' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 224ms:[0m
# Issues/hook卸載殘留註冊.md
type:issue | status:done | created:2026-07-07 | updated:2026-07-07 | scope:platform
summary:
  FLAG:ORIGIN
  KEY:現場事故——code-loop-guard.py 被工具鏈更新刪除(落實 2026-07-06 ADR 撤 Stop nag),但 ~/.claude/settings.json 的 Stop…
→ 連出 (2):
  • Projects/code-loop必用守衛_計劃.md [done]
  • Systems/lumos-cli-lifecycle.md [done]
← 連入 (3):
  • Projects/CI回流閉環_計劃.md [done]
  • Projects/teardown一鍵拆機_計劃.md [doing]
  • Verification/2026-07-24_teardown一鍵拆機.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Issues/hook卸載殘留註冊'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 217ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Issues/init-force-slug誤用basename' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 214ms:[0m
# Issues/init-force-slug誤用basename.md
type:issue | status:done | created:2026-07-06 | updated:2026-07-06 | scope:platform
summary:
  FLAG:ORIGIN
  KEY:現場事故——`lumos init --force` 在既有 vault 上,slug 誤用 repo basename 而非既有 vault 的 slug。repo basename=lan…
→ 連出 (1):
  • Systems/lumos-cli-lifecycle.md [done]
← 連入 (0):

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Issues/init-force-slug誤用basename'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 219ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Issues/vendored測試套件在消費端假紅' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 218ms:[0m
# Issues/vendored測試套件在消費端假紅.md
type:issue | status:resolved | created:2026-08-02 | updated:2026-08-02 | scope:platform
summary:
  FLAG:TECHNICAL
  DECISION:不停止 vendoring 測試套件(消費端仍需要「更新後 CLI 有沒有壞」這個能力),改讓★來源 repo 專用★的測試在消費端乾淨 skip;判定★狀態驅動★(`_need_s…
→ 連出 (3):
  • Systems/lumos-cli-lifecycle.md [done]
  • Systems/測試假綠形態.md [done]
  • Systems/診斷迴圈先行.md [done]
← 連入 (2):
  • Issues/vendored自測3紅_來源repo專用測試漏標skip.md [done]
  • Projects/推播miss量測_計劃.md [done]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Issues/vendored測試套件在消費端假紅'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 218ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/known-pitfall-refresh-token' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 226ms:[0m
# Systems/known-pitfall-refresh-token.md
type:system | status:doing | created:2026-08-09 | updated:2026-08-09 | scope:stack-knowledge
summary:
  FLOW:
  KEY:
verified_by: [[Verification/2026-08-09_已知坑策展庫v2落地]], [[Verification/2026-08-21_L4交叉審計30節點清帳]]
→ 連出 (2):
  • Verification/2026-08-09_已知坑策展庫v2落地.md [pass]
  • Verification/2026-08-21_L4交叉審計30節點清帳.md [pass]
← 連入 (2):
  • MOC/index.md [doing]
  • Projects/棧別提問表態閘_計劃.md [doing]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/known-pitfall-refresh-token'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 215ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/lumos-cli-read' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 220ms:[0m
# Systems/lumos-cli-read.md
type:system | status:done | created:2026-06-26 | updated:2026-08-23 | scope:retrieval
提醒:這篇有「動了會壞」的合約,動手前一定要看:
  ★INVARIANT★ search 預設排除 status=superseded 節點但不排除 stale(真遺忘,GateMem 2026-07-24;stale 是待重驗警訊,藏了=製造新洞,doctor Check S 綁 stale+superseded 正是反例),--include-superseded 逃生;濾網插「命中確認後、三路分岔前」故 ranked/legacy/regex 三路一致、hidden 數=命中被藏筆數非全庫;隱藏數走 stderr(全模式含 --files-only,不污染 stdout)、--json 加 hidden_superseded 欄位 [test:t_search_forget_superseded] [audit:sonnet/2026-07-24]
summary:
  KEY:[2026-09-08 ~~~ 圍欄]`_visible_lines`(search 與所有「哪些字看得見」的唯一實作)從此把 `~~~` 跟 ``` 一樣當 fenced code 邊界(兩…
  KEY:[2026-09-08 handoff 條款行]計劃有 [SN] 時 `lumos handoff` 多印一行「驗收條款 N 條:綁了測試/靠人/未標/懸空 + 指路 lumos spec-t…
verified_by: [[Verification/2026-07-14_relguard_E1失效背書]], [[Verification/2026-07-14_relguard_E2建在被推翻決策上]], [[Verification/2026-07-15_主網M1_決策穩定ID]], [[Verification/2026-07-15_主網M2_typed-edge索引]], [[Verification/2026-07-15_主網M3_cascade帳本]], [[Verification/2026-07-15_主網M4_觸發與連鎖]], [[Verification/2026-07-16_fromscratch守衛M1_CheckJ]], [[Verification/2026-07-24_真遺忘search排除superseded]], [[Verification/2026-08-05_流程優化六件落地]], [[Verification/2026-08-05_標籤結構收編落地]], [[Verification/2026-08-16_圖譜結構化查詢query落地]], [[Verification/2026-08-22_狀態表過期偵測]], [[Verification/2026-08-25_連鎖佇列軟提醒落地]], [[Verification/2026-08-27_關係語意腐爛守衛_G1解鎖即活]], [[Verification/2026-09-07_loop-list開著的迴圈]], [[Verification/2026-09-07_handoff接手視圖]]
→ 連出 (22):
  • Issues/2026-08-03_剝除與邊界解析的既有缺陷群.md [doing]
  • Projects/lumos-show讀取入口_計劃.md [done]
  • Projects/圖譜結構化查詢_計劃.md [done]
  • Projects/檢索多詞回退_計劃.md [doing]
  • Systems/lumos-cli-lifecycle.md [done]
  • Systems/lumos-cli-write.md [done]
  • Verification/2026-07-14_relguard_E1失效背書.md [pass]
  • Verification/2026-07-14_relguard_E2建在被推翻決策上.md [pass]
  • Verification/2026-07-15_主網M1_決策穩定ID.md [pass]
  • Verification/2026-07-15_主網M2_typed-edge索引.md [pass]
  • Verification/2026-07-15_主網M3_cascade帳本.md [pass]
  • Verification/2026-07-15_主網M4_觸發與連鎖.md [pass]
  • Verification/2026-07-16_fromscratch守衛M1_CheckJ.md [pass]
  • Verification/2026-07-24_真遺忘search排除superseded.md [pass]
  • Verification/2026-08-05_標籤結構收編落地.md [pass]
  • Verification/2026-08-05_流程優化六件落地.md [pass]
  • Verification/2026-08-16_圖譜結構化查詢query落地.md [pass]
  • Verification/2026-08-22_狀態表過期偵測.md [pass]
  • Verification/2026-08-25_連鎖佇列軟提醒落地.md [pass]
  • Verification/2026-08-27_關係語意腐爛守衛_G1解鎖即活.md [pass]
  • Verification/2026-09-07_handoff接手視圖.md [pass]
  • Verification/2026-09-07_loop-list開著的迴圈.md [pass]
← 連入 (25):
  • MOC/index.md [doing]
  • Projects/CheckT-Python-profile_計劃.md [done]
  • Projects/Spotify-shunt吸收_調研.md [doing]
  • Projects/lumos-show讀取入口_計劃.md [done]
  • Projects/中心性重驗排程_計劃.md [done]
  • Projects/主動影響幅度偵測_計劃.md [done]
  • Projects/公開精簡版_計劃.md [doing]
  • Projects/圖譜結構化查詢_計劃.md [done]
  • Projects/接手視圖_計劃.md [done]
  • Projects/標籤結構收編_計劃.md [done]
  • Projects/檢索優化_計劃.md [done]
  • Projects/檢索優化_調研.md [doing]
  • Projects/流程優化六件_計劃.md [done]
  • Projects/狀態標籤同步守衛_計劃.md [done]
  • Projects/真遺忘召回過濾_計劃.md [done]
  • Systems/lumos-cli-lifecycle.md [done]
  • Systems/lumos-cli-write.md [done]
  • Systems/retrieval-ranking.md [done]
  • Systems/開發工作流總覽.md [done]
  • Verification/2026-07-14_relguard_E2建在被推翻決策上.md [pass]
  • Verification/2026-07-15_主網M1_決策穩定ID.md [pass]
  • Verification/2026-07-15_主網M2_typed-edge索引.md [pass]
  • Verification/2026-07-15_主網M3_cascade帳本.md [pass]
  • Verification/2026-07-15_主網M4_觸發與連鎖.md [pass]
  • Verification/2026-07-16_fromscratch守衛M1_CheckJ.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/lumos-cli-read'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 223ms:[0m
# Systems/lumos-cli-read.md
  ★INVARIANT★ search 預設排除 status=superseded 節點但不排除 stale(真遺忘,GateMem 2026-07-24;stale 是待重驗警訊,藏了=製造新洞,doctor Check S 綁 stale+superseded 正是反例),--include-superseded 逃生;濾網插「命中確認後、三路分岔前」故 ranked/legacy/regex 三路一致、hidden 數=命中被藏筆數非全庫;隱藏數走 stderr(全模式含 --files-only,不污染 stdout)、--json 加 hidden_superseded 欄位
      ↳ 綁的測試: t_search_forget_superseded

合約 1 條(改了就是破壞性變更) | 技術債 0 條(可以改)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/lumos-refcheck' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 228ms:[0m
# Systems/lumos-refcheck.md
type:system | status:done | created:2026-07-02 | updated:2026-07-02 | risk:守衛面 | scope:loop-engineering
summary:
  FLOW:refcheck <md> --repo <root>→FENCE剝/INLINE抽/剝反引號→跳://與*<>?→剝:suffix(純數字才當行號)→須含/且首段=頂層目錄→(token,…
  KEY:vault-free(pre-Env 分流,同 install/bootstrap);--repo 省略時 cwd 逐層向上找 .git,無則 rc2
verified_by: [[Verification/2026-07-02_lumos-refcheck]]
→ 連出 (1):
  • Verification/2026-07-02_lumos-refcheck.md [pass]
← 連入 (6):
  • MOC/index.md [doing]
  • Projects/主動影響幅度偵測_計劃.md [done]
  • Projects/棧別提問表態閘_計劃.md [doing]
  • Systems/check-j-regen-guard.md [done]
  • Systems/pitfalls-lint-adapter.md [doing]
  • Verification/2026-07-02_lumos-refcheck.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/lumos-refcheck'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 216ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/anchor-integrity' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 215ms:[0m
# Systems/anchor-integrity.md
type:system | status:done | created:2026-07-02 | updated:2026-07-28 | risk:守衛面 | scope:guards-gates
summary:
  FLOW:anchor approve --note→6錨點(runner×2+git hooks×3+claude hook×1:dispatch-lens-hook.py,2026-09-03 新…
  KEY:守「驗證器本身被悄悄改成一律通過」——測試綠/hook 放行的前提(批改程式沒被動過)從盲信變成可機械核對宣稱;外部實證=八大評測被 conftest 鉤子破
verified_by: [[Verification/2026-07-02_anchor-integrity]], [[Verification/2026-08-21_L4交叉審計30節點清帳]], [[Verification/2026-09-03_派工鏡頭注入驗收]], [[Verification/2026-09-04_Codex完全支援S1hook適配驗收]]
→ 連出 (7):
  • Projects/派工鏡頭注入_計劃.md [done]
  • Systems/hook信任邊界.md [doing]
  • Verification/2026-07-02_anchor-integrity.md [pass]
  • Verification/2026-08-21_L4交叉審計30節點清帳.md [pass]
  • Verification/2026-09-03_派工攔截點實測.md [pass]
  • Verification/2026-09-03_派工鏡頭注入驗收.md [pass]
  • Verification/2026-09-04_Codex完全支援S1hook適配驗收.md [pass]
← 連入 (7):
  • Issues/git-hooks路徑指向樹內_checkout即執行分支碼.md [open]
  • MOC/index.md [doing]
  • Projects/Codex完全支援_計劃.md [done]
  • Projects/code-loop必用守衛_計劃.md [done]
  • Projects/主動影響幅度偵測_計劃.md [done]
  • Projects/派工鏡頭注入_計劃.md [done]
  • Verification/2026-07-02_anchor-integrity.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/anchor-integrity'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 221ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/pitfalls-code-loop' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 216ms:[0m
# Systems/pitfalls-code-loop.md
type:system | status:done | created:2026-07-04 | updated:2026-09-11 | risk:守衛面 | scope:loop-engineering
summary:
  KEY:★[2026-08-14]canary 協議停用(單源=[[Systems/canary-audit]] d5)★——植入/三道防污染/判定/missed 懲罰全停;輪記帳改 `canary …
  KEY:[2026-08-05]UI 層驗收慣例(MCP 接驗證層,Enzo 靈感;立慣例不綁案)——test-layers 宣告 layer 含「UI 驗收」的棧被 diff 命中時,終審驗收=ag…
verified_by: [[Verification/2026-07-04_pitfalls-code-loop]], [[Verification/2026-07-05_code-loop必用守衛]], [[Verification/2026-07-10_合約鏈補強234]], [[Verification/2026-08-05_panel-K2與抽查落地]], [[Verification/2026-08-14_canary協議停用none制落地]], [[Verification/2026-08-21_L4交叉審計30節點清帳]], [[Verification/2026-09-11_代碼審資安席落地]], [[Verification/2026-09-11_全報vs抑噪試點]]
→ 連出 (9):
  • Projects/impact-diff橋接_計劃.md [done]
  • Verification/2026-07-04_pitfalls-code-loop.md [pass]
  • Verification/2026-07-05_code-loop必用守衛.md [pass]
  • Verification/2026-07-10_合約鏈補強234.md [pass]
  • Verification/2026-08-05_panel-K2與抽查落地.md [pass]
  • Verification/2026-08-14_canary協議停用none制落地.md [pass]
  • Verification/2026-08-21_L4交叉審計30節點清帳.md [pass]
  • Verification/2026-09-11_代碼審資安席落地.md [pass]
  • Verification/2026-09-11_全報vs抑噪試點.md [pass]
← 連入 (43):
  • Issues/ci-wait對當日run判no-run.md [open]
  • Issues/code-loop-pass不能指定分支.md [open]
  • Issues/code-loop-pass自失效追尾.md [resolved]
  • Issues/code-loop守衛main-direct盲區.md [done]
  • Issues/loop機制痛點_Landmark_code-crossclaim實跑回饋.md [open]
  • MOC/index.md [doing]
  • Projects/Android側UI測試綁圖譜工作流_實作計畫.md [doing]
  • Projects/Android側UI測試綁圖譜工作流_計劃.md [todo]
  • Projects/GPT外部評審吸收_計劃.md [doing]
  • Projects/canary生成硬化_計劃.md [done]
  • Projects/cochange守衛_計劃.md [done]
  • Projects/code-loop必用守衛_計劃.md [done]
  • Projects/code階段強化_計劃.md [doing]
  • Projects/impact-diff橋接_計劃.md [done]
  • Projects/lint接線收口_計劃.md [done]
  • Projects/panel收斂判準改革_計劃.md [done]
  • Projects/pitfalls-lint-integration_計劃.md [done]
  • Projects/pitfalls棧別效能追問_計劃.md [done]
  • Projects/prepush主幹範圍修法_計劃.md [doing]
  • Projects/skills提示工程優化_調研.md [done]
  • Projects/spec合規slot_計劃.md [done]
  • Projects/test-layers軟提醒_計劃.md [done]
  • Projects/代碼審資安席_計劃.md [doing]
  • Projects/先問世界_存量掃描裁定.md [done]
  • Projects/兩席相反時端出張力_計劃.md [done]
  • Projects/地基盤點2026-08-26_調研.md [doing]
  • Projects/子代理續談調研.md [done]
  • Projects/收斂機制優化調研2026-08-14.md [doing]
  • Projects/收斂閘殘餘估計降級_計劃.md [done]
  • Projects/收貨線指令化_計劃.md [superseded]
  • Projects/棧別提問表態閘_計劃.md [doing]
  • Projects/檢索優化_計劃.md [done]
  • Projects/社群演算法補強_調研.md [done]
  • Systems/codex-harness.md [done]
  • Systems/heterogeneous-finder-ensemble.md [done]
  • Systems/lint-version-watch.md [doing]
  • Systems/pitfalls-lint-adapter.md [doing]
  • Systems/效能檢核目錄.md [done]
  • Systems/棧別提問表態閘.md [doing]
  • Systems/開發工作流總覽.md [done]
  • Verification/2026-07-04_pitfalls-code-loop.md [pass]
  • Verification/2026-07-05_code-loop必用守衛.md [pass]
  • Verification/2026-07-10_合約鏈補強234.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/pitfalls-code-loop'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 221ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/測試假綠形態' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 227ms:[0m
# Systems/測試假綠形態.md
type:system | status:done | created:2026-08-01 | updated:2026-08-28 | scope:ux-docs-hygiene
提醒:這篇有「動了會壞」的合約,動手前一定要看:
  ★INVARIANT★ 修 bug 的「還原翻紅釘」必須配一條**前置斷言證明現場成立**(被測那條路真的被執行到)——否則對第④型「現場走不到被測分支」完全無效:把修法還原回去,測試照樣全綠 [test:t_slim_uninstall_manifest_parent_cleanup_is_best_effort,t_deinit_vendored_unlink_failure_does_not_abort] [audit:opus/2026-08-01](因果驗證:2026-08-01 r3 第一版翻紅釘的現場用「父目錄非空」,`if ... and not any(parent.iterdir())` 直接判假、`rmdir()` 根本不執行,把修法還原成共用 try 的突變照樣全綠;改成 `chmod ~/.local/share 0o500` 讓 `rmdir` 真的拋 PermissionError 後才翻紅 3 條斷言)
summary:
  FLOW:寫測試/審測試時逐條對照本清單 → 命中哪一型就照該型的「怎麼接住」處理 → 修 bug 收尾跑「還原翻紅釘」時★必須同時放一條「現場成立」前置斷言★(否則對第④型全瞎)
  KEY:本專案撞最多次的坑=「測試存在但沒在驗它宣稱要驗的」,已累計 ★16 次★(2026-08-02 第 12、2026-08-03 第 13/14/15/16,★五次都是新測試自己中第④型★)。…
verified_by: [[Verification/2026-08-02_slim三缺陷修復_實驗產出]], [[Verification/2026-08-03_Windows回歸測試三缺陷]], [[Verification/2026-08-04_design-loop重設計落地T1-T7]], [[Verification/2026-08-21_L4交叉審計30節點清帳]], [[Verification/2026-09-05_wrapper邊跑邊改實驗]]
→ 連出 (10):
  • Issues/loop-next吐不可宣告的tier.md [done]
  • Issues/prepush測試閘假紅-git環境洩漏.md [resolved]
  • Projects/skill寫法學借鑒與design-loop剪枝.md [done]
  • Projects/檢索多詞回退_計劃.md [doing]
  • Systems/canary-audit.md [deferred]
  • Verification/2026-08-02_slim三缺陷修復_實驗產出.md [pass]
  • Verification/2026-08-03_Windows回歸測試三缺陷.md [pass]
  • Verification/2026-08-04_design-loop重設計落地T1-T7.md [pass]
  • Verification/2026-08-21_L4交叉審計30節點清帳.md [pass]
  • Verification/2026-09-05_wrapper邊跑邊改實驗.md [pass]
← 連入 (15):
  • Issues/2026-08-03_剝除與邊界解析的既有缺陷群.md [doing]
  • Issues/lint-watch空轉假綠.md [done]
  • Issues/loop-next吐不可宣告的tier.md [done]
  • Issues/vendored測試套件在消費端假紅.md [resolved]
  • MOC/index.md [doing]
  • Projects/Spotify-shunt吸收_調研.md [doing]
  • Projects/全repo審視_計劃.md [doing]
  • Projects/合約測試閘什麼時候跑_計劃.md [doing]
  • Projects/檢索多詞回退_計劃.md [doing]
  • Projects/第二輪審視六修_計劃.md [doing]
  • Systems/診斷迴圈先行.md [done]
  • Verification/2026-08-02_slim三缺陷修復_實驗產出.md [pass]
  • Verification/2026-08-03_Windows回歸測試三缺陷.md [pass]
  • Verification/2026-08-03_Windows真機驗證五缺陷修復.md [superseded]
  • Verification/2026-09-05_wrapper邊跑邊改實驗.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/測試假綠形態'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 210ms:[0m
# Systems/測試假綠形態.md
  ★INVARIANT★ 修 bug 的「還原翻紅釘」必須配一條**前置斷言證明現場成立**(被測那條路真的被執行到)——否則對第④型「現場走不到被測分支」完全無效:把修法還原回去,測試照樣全綠  (因果驗證:2026-08-01 r3 第一版翻紅釘的現場用「父目錄非空」,`if ... and not any(parent.iterdir())` 直接判假、`rmdir()` 根本不執行,把修法還原成共用 try 的突變照樣全綠;改成 `chmod ~/.local/share 0o500` 讓 `rmdir` 真的拋 PermissionError 後才翻紅 3 條斷言)
      ↳ 綁的測試: t_slim_uninstall_manifest_parent_cleanup_is_best_effort, t_deinit_vendored_unlink_failure_does_not_abort

合約 1 條(改了就是破壞性變更) | 技術債 0 條(可以改)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/slim-install-安裝器' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 219ms:[0m
# Systems/slim-install-安裝器.md
type:system | status:done | created:2026-07-31 | updated:2026-08-20 | risk:不可逆 | scope:platform
提醒:這篇有「動了會壞」的合約,動手前一定要看:
  ★INVARIANT★ CLAUDE.md 注入必須原地取代/檔首插入,sentinel(`<!-- LUMOS-SLIM:START/END -->`)以外的既有內容 byte-equal 保留(改=毀使用者/其他工具寫進 CLAUDE.md 的內容=breaking);有完整版區塊就在它原本的位置換掉,沒有就插在檔首標題之後,都不是搬到檔尾 [test:t_slim_install_no_project_touch,t_slim_install_replaces_full_discipline_block_in_place] [audit:sonnet/2026-07-31](獨立審計實測:在暫存副本把寫入改成整檔覆寫,綁定測試確實翻紅,非稻草人)
  ★INVARIANT★ CLAUDE.md 注入必須冪等——重跑安裝器只更新自己 sentinel 之間那塊內容,不疊出第二塊、不因重跑而漂移,備份標記(FULL-BACKUP)也不會被重新編碼或洗成 NONE [test:t_slim_install_claude_md_idempotent,t_slim_install_backup_survives_idempotent_reinstall] [audit:sonnet/2026-07-31](獨立審計實測:在暫存副本把「已存在 sentinel 則替換」的分支關掉,強迫每次都走插入路徑,綁定測試確實翻紅——第二次跑完出現兩塊 sentinel)
  ★INVARIANT★ 完整版區塊被取代前必須先把原文(含它自己的 sentinel)位元組級備份——base64 編碼藏進精簡版區塊自己的 HTML 註解裡(`<!-- LUMOS-SLIM:FULL-BACKUP:BASE64:... -->`),解碼後須與原文逐位元組相同,這是 [[Systems/slim-uninstall-一行卸載]] 能精確還原的前提 [test:t_slim_install_replaces_full_discipline_block_in_place] [audit:sonnet/2026-07-31](備份設計理由:自足、隨 CLAUDE.md 本身走,不新增檔案到使用者專案、`~/.lumos-slim` 被刪掉也還原得了)
  ★INVARIANT★ (★2026-07-31 Task 10 新增★)裝 bin 時必須同步寫身分證 manifest(`~/.local/share/lumos-slim/manifest.json`,含安裝當下對 `~/.local/bin/lumos` 算出的 `bin_sha256`),讓 [[Systems/slim-uninstall-一行卸載]] 有★不依賴 `~/.lumos-slim` 存不存在★的比對基準——這是本次修的 bug 的正面解法:接手者若走 README 也在教的「直接 clone 交付包到任意路徑跑 install.sh」而非 `get.sh`,`~/.lumos-slim` 從頭到尾不會存在,舊版卸載腳本的唯一比對基準因此永遠缺失 [test:t_slim_uninstall_direct_install_restores_claude_md] [audit:sonnet/2026-07-31](因果驗證:`git stash` 還原成 Task 10 前的 install.sh/uninstall.sh 重跑此測試確實翻紅——bin 比對基準缺失→exit 2→CLAUDE.md 沒被還原,回補修復後轉綠)
  ★INVARIANT★ (2026-08-01 Task 11 新增)CLAUDE.md 注入動手前必須先過三層目標守衛,拒絕時 rc=2 且 CLAUDE.md 不得被動——①不像專案根(無 `.git`、無 `docs/*-knowledge/`、無既有 `CLAUDE.md`,或 `$(pwd)`==`$HOME`,用 `pwd -P`/`cd -P` 解 symlink 後比對)→拒絕②目標同時具備 `skills/lumos-project-notes/`+`scripts/lumos`+`scripts/templates/graph-discipline.md` 三件套(lumos 工具鏈來源 repo 才有的組合)→拒絕③不論①②過不過,動手前一律先印出「目標專案」與「將修改」的絕對路徑。★真實事故驅動,別誤讀成第一層擋得住那兩次★:兩位不同的子代理驗證時忘記先 `cd` 進交付包 clone,直接在本 repo(lumos 工具鏈來源 repo)根目錄跑 `dist/install.sh`,當場改掉了來源 repo 自己的 `CLAUDE.md`(兩次都當場發現、`git checkout` 還原)——事故現場本身就有 `.git`/`CLAUDE.md`/`docs/*-knowledge`,「像不像專案根」的第一層完全擋不住,真正擋住的是第二層(來源 repo 三件套判定,沿用 `scripts/lumos` 的 `cmd_update`/`cmd_deinit`「`root == _lumos_src()` → 拒絕」同款自我保護精神)。逃生閥 `--here` 繞過①②,③一律照印、不受影響 [test:t_slim_install_guard_rejects_empty_dir,t_slim_install_guard_rejects_home_dir,t_slim_install_guard_rejects_source_repo,t_slim_install_guard_repro_real_incident,t_slim_install_guard_here_bypasses,t_slim_install_guard_normal_project_still_works] [audit:sonnet/2026-08-01](獨立審計實測抓到一個真的稻草人,非空手放行:`t_slim_install_guard_repro_real_incident` 原版直接對 `slim/install.sh` 原始檔以 repo 根為 cwd 執行——但 `slim/` 底下沒有 `scripts/lumos`,會先撞上與本守衛無關的套件完整性檢查提前以 rc=2 退出,**把第二層判斷式整段刪掉這個舊版測試依然通過**;改用 `scripts/slim-gen.py` 真的生成一份 `dist/install.sh` 再以 repo 根為 cwd 執行後修正。修正後複測:把第二層 `if` 換成 `if false; then` 造假陽性,綁定測試確實翻紅(rc 從 2 變 0、`CLAUDE.md` 真的被覆寫)——此步驟意外把本 repo 自己的 `CLAUDE.md` 寫髒,已 `git checkout` 立即復原並確認 `git status --porcelain CLAUDE.md` 清空。其餘五支測試審計時逐一確認皆非稻草人)
  ★INVARIANT★ (★2026-08-01 Task 14 修復①★)`.cmd` shim 呼叫用的直譯器名稱不得寫死字面 `python`——安裝當下用 `_pick_windows_interpreter()`(依序 `shutil.which("python3")`/`shutil.which("python")`)偵測寫進 shim,兩者都找不到才退回 `"python"`。理由:Task 13 移植時沿用的舊寫法與 `install.sh`/`install.ps1` 兩支薄殼自己「python3 優先,找不到才退 python」的判斷邏輯互相矛盾——只有 `python3.exe`、沒有 `python.exe` 的 Windows 機器上,`install.ps1` 用 `python3` 把安裝跑完、印出「裝好了」,但產生的 shim 卻寫死呼叫 `python`,之後每次打 `lumos` 都得到 `'python' is not recognized`,裝完即壞 [test:t_slim_install_windows_shim_does_not_hardcode_python_when_only_python3_available] [audit:sonnet/2026-08-01](因果驗證:`git stash` 只還原 `slim/install.py`、用只有 `python3`、沒有 `python` 的自製 PATH 環境重跑此測試,「不是寫死字面 python」「確實記錄成偵測到的 python3」兩條斷言確實翻紅,回補修復後轉綠)
  ★INVARIANT★ (★2026-08-01 Task 14 修復②★)Windows 路徑下,全域指令的碰撞偵測(是否需要 `--force`)必須同時看 `lumos`(`dst_script`)與 `lumos.cmd`(`dst_shim`)——只看前者的舊寫法,若使用者手動刪了 `lumos` 忘了刪 `lumos.cmd`(單獨殘留),非 `--force` 重裝會直接無聲覆寫殘留的 `lumos.cmd`,繞過「碰撞需要 `--force`」這條保護的存在意義 [test:t_slim_install_windows_collision_detects_orphan_cmd_shim] [audit:sonnet/2026-08-01](因果驗證:同一份 `git stash` 前的舊版,只放殘留 `lumos.cmd`、不放 `lumos`,跑不帶 `--force` 的模擬安裝,「視為碰撞」與「內容未被覆寫」兩條斷言確實翻紅——舊版 rc0 且直接覆寫殘留內容;回補修復後轉綠,且帶 `--force` 仍能正常覆寫,對稱驗證未修過頭)
summary:
  FLOW:`slim/install.sh` 用 `$(cd "$(dirname "$0")" && pwd)`(先解 symlink 鏈)定位交付包 → 檢查 `scripts/lumos`/`s…
  KEY:★只動 $HOME 與專案 CLAUDE.md 這一份檔案,不碰專案其餘任何東西★(★2026-07-31 使用者裁定推翻原「不注入/更新任何 CLAUDE.md」的裁定,範圍刀見下條★)——…
verified_by: [[Verification/2026-07-31_slim-install安裝器落地]], [[Verification/2026-07-31_公開精簡版交付]], [[Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復]], [[Verification/2026-07-31_slim-claude-md注入]], [[Verification/2026-07-31_slim-claude-md第三次裁定取代與備份還原]], [[Verification/2026-07-31_slim-uninstall步驟獨立化與manifest基準修復]], [[Verification/2026-08-01_slim-install注入目標守衛]], [[Verification/2026-08-01_公開精簡版代碼審第四輪修復]], [[Verification/2026-08-01_slim-python移植]], [[Verification/2026-08-01_slim-windows兩缺陷修復]], [[Verification/2026-08-01_slim-ps1早期分支exit修復]], [[Verification/2026-08-01_slim-終審三缺陷修復]], [[Verification/2026-08-01_slim-manifest殘留與代碼審六輪]], [[Verification/2026-08-02_slim三缺陷修復_實驗產出]], [[Verification/2026-08-03_Windows回歸測試三缺陷]], [[Verification/2026-08-03_Windows真機三輪驗證通過]], [[Verification/2026-08-21_L4交叉審計30節點清帳]]
plan_refs: [[Projects/公開精簡版_計劃]]
→ 連出 (22):
  • Projects/公開精簡版_實作計畫.md [done]
  • Projects/公開精簡版_計劃.md [doing]
  • Systems/lumos-cli-lifecycle.md [done]
  • Systems/slim-get-一行安裝.md [done]
  • Systems/slim-uninstall-一行卸載.md [done]
  • Verification/2026-07-31_slim-claude-md注入.md [pass]
  • Verification/2026-07-31_slim-claude-md第三次裁定取代與備份還原.md [pass]
  • Verification/2026-07-31_slim-install安裝器落地.md [pass]
  • Verification/2026-07-31_slim-uninstall步驟獨立化與manifest基準修復.md [pass]
  • Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復.md [pass]
  • Verification/2026-07-31_公開精簡版交付.md [pass]
  • Verification/2026-08-01_slim-install注入目標守衛.md [pass]
  • Verification/2026-08-01_slim-manifest殘留與代碼審六輪.md [pass]
  • Verification/2026-08-01_slim-ps1早期分支exit修復.md [pass]
  • Verification/2026-08-01_slim-python移植.md [pass]
  • Verification/2026-08-01_slim-windows兩缺陷修復.md [pass]
  • Verification/2026-08-01_slim-終審三缺陷修復.md [pass]
  • Verification/2026-08-01_公開精簡版代碼審第四輪修復.md [pass]
  • Verification/2026-08-02_slim三缺陷修復_實驗產出.md [pass]
  • Verification/2026-08-03_Windows回歸測試三缺陷.md [pass]
  • Verification/2026-08-03_Windows真機三輪驗證通過.md [pass]
  • Verification/2026-08-21_L4交叉審計30節點清帳.md [pass]
← 連入 (21):
  • MOC/index.md [doing]
  • Projects/公開精簡版_實作計畫.md [done]
  • Projects/公開精簡版_計劃.md [doing]
  • Systems/lumos-cli-lifecycle.md [done]
  • Systems/slim-get-一行安裝.md [done]
  • Systems/slim-readme.md [done]
  • Systems/slim-uninstall-一行卸載.md [done]
  • Verification/2026-07-31_slim-claude-md注入.md [pass]
  • Verification/2026-07-31_slim-claude-md第三次裁定取代與備份還原.md [pass]
  • Verification/2026-07-31_slim-install安裝器落地.md [pass]
  • Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復.md [pass]
  • Verification/2026-07-31_公開精簡版交付.md [pass]
  • Verification/2026-08-01_slim-install注入目標守衛.md [pass]
  • Verification/2026-08-01_slim-manifest殘留與代碼審六輪.md [pass]
  • Verification/2026-08-01_slim-ps1早期分支exit修復.md [pass]
  • Verification/2026-08-01_slim-windows兩缺陷修復.md [pass]
  • Verification/2026-08-01_slim-終審三缺陷修復.md [pass]
  • Verification/2026-08-02_slim三缺陷修復_實驗產出.md [pass]
  • Verification/2026-08-03_Windows回歸測試三缺陷.md [pass]
  • Verification/2026-08-03_Windows真機三輪驗證通過.md [pass]
  • Verification/2026-08-03_Windows真機驗證五缺陷修復.md [superseded]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/slim-install-安裝器'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 218ms:[0m
# Systems/slim-install-安裝器.md
  ★INVARIANT★ CLAUDE.md 注入必須原地取代/檔首插入,sentinel(`<!-- LUMOS-SLIM:START/END -->`)以外的既有內容 byte-equal 保留(改=毀使用者/其他工具寫進 CLAUDE.md 的內容=breaking);有完整版區塊就在它原本的位置換掉,沒有就插在檔首標題之後,都不是搬到檔尾  (獨立審計實測:在暫存副本把寫入改成整檔覆寫,綁定測試確實翻紅,非稻草人)
      ↳ 綁的測試: t_slim_install_no_project_touch, t_slim_install_replaces_full_discipline_block_in_place
  ★INVARIANT★ CLAUDE.md 注入必須冪等——重跑安裝器只更新自己 sentinel 之間那塊內容,不疊出第二塊、不因重跑而漂移,備份標記(FULL-BACKUP)也不會被重新編碼或洗成 NONE  (獨立審計實測:在暫存副本把「已存在 sentinel 則替換」的分支關掉,強迫每次都走插入路徑,綁定測試確實翻紅——第二次跑完出現兩塊 sentinel)
      ↳ 綁的測試: t_slim_install_claude_md_idempotent, t_slim_install_backup_survives_idempotent_reinstall
  ★INVARIANT★ 完整版區塊被取代前必須先把原文(含它自己的 sentinel)位元組級備份——base64 編碼藏進精簡版區塊自己的 HTML 註解裡(`<!-- LUMOS-SLIM:FULL-BACKUP:BASE64:... -->`),解碼後須與原文逐位元組相同,這是 [[Systems/slim-uninstall-一行卸載]] 能精確還原的前提  (備份設計理由:自足、隨 CLAUDE.md 本身走,不新增檔案到使用者專案、`~/.lumos-slim` 被刪掉也還原得了)
      ↳ 綁的測試: t_slim_install_replaces_full_discipline_block_in_place
  ★INVARIANT★ (★2026-07-31 Task 10 新增★)裝 bin 時必須同步寫身分證 manifest(`~/.local/share/lumos-slim/manifest.json`,含安裝當下對 `~/.local/bin/lumos` 算出的 `bin_sha256`),讓 [[Systems/slim-uninstall-一行卸載]] 有★不依賴 `~/.lumos-slim` 存不存在★的比對基準——這是本次修的 bug 的正面解法:接手者若走 README 也在教的「直接 clone 交付包到任意路徑跑 install.sh」而非 `get.sh`,`~/.lumos-slim` 從頭到尾不會存在,舊版卸載腳本的唯一比對基準因此永遠缺失  (因果驗證:`git stash` 還原成 Task 10 前的 install.sh/uninstall.sh 重跑此測試確實翻紅——bin 比對基準缺失→exit 2→CLAUDE.md 沒被還原,回補修復後轉綠)
      ↳ 綁的測試: t_slim_uninstall_direct_install_restores_claude_md
  ★INVARIANT★ (2026-08-01 Task 11 新增)CLAUDE.md 注入動手前必須先過三層目標守衛,拒絕時 rc=2 且 CLAUDE.md 不得被動——①不像專案根(無 `.git`、無 `docs/*-knowledge/`、無既有 `CLAUDE.md`,或 `$(pwd)`==`$HOME`,用 `pwd -P`/`cd -P` 解 symlink 後比對)→拒絕②目標同時具備 `skills/lumos-project-notes/`+`scripts/lumos`+`scripts/templates/graph-discipline.md` 三件套(lumos 工具鏈來源 repo 才有的組合)→拒絕③不論①②過不過,動手前一律先印出「目標專案」與「將修改」的絕對路徑。★真實事故驅動,別誤讀成第一層擋得住那兩次★:兩位不同的子代理驗證時忘記先 `cd` 進交付包 clone,直接在本 repo(lumos 工具鏈來源 repo)根目錄跑 `dist/install.sh`,當場改掉了來源 repo 自己的 `CLAUDE.md`(兩次都當場發現、`git checkout` 還原)——事故現場本身就有 `.git`/`CLAUDE.md`/`docs/*-knowledge`,「像不像專案根」的第一層完全擋不住,真正擋住的是第二層(來源 repo 三件套判定,沿用 `scripts/lumos` 的 `cmd_update`/`cmd_deinit`「`root == _lumos_src()` → 拒絕」同款自我保護精神)。逃生閥 `--here` 繞過①②,③一律照印、不受影響  (獨立審計實測抓到一個真的稻草人,非空手放行:`t_slim_install_guard_repro_real_incident` 原版直接對 `slim/install.sh` 原始檔以 repo 根為 cwd 執行——但 `slim/` 底下沒有 `scripts/lumos`,會先撞上與本守衛無關的套件完整性檢查提前以 rc=2 退出,**把第二層判斷式整段刪掉這個舊版測試依然通過**;改用 `scripts/slim-gen.py` 真的生成一份 `dist/install.sh` 再以 repo 根為 cwd 執行後修正。修正後複測:把第二層 `if` 換成 `if false; then` 造假陽性,綁定測試確實翻紅(rc 從 2 變 0、`CLAUDE.md` 真的被覆寫)——此步驟意外把本 repo 自己的 `CLAUDE.md` 寫髒,已 `git checkout` 立即復原並確認 `git status --porcelain CLAUDE.md` 清空。其餘五支測試審計時逐一確認皆非稻草人)
      ↳ 綁的測試: t_slim_install_guard_rejects_empty_dir, t_slim_install_guard_rejects_home_dir, t_slim_install_guard_rejects_source_repo, t_slim_install_guard_repro_real_incident, t_slim_install_guard_here_bypasses, t_slim_install_guard_normal_project_still_works
  ★INVARIANT★ (★2026-08-01 Task 14 修復①★)`.cmd` shim 呼叫用的直譯器名稱不得寫死字面 `python`——安裝當下用 `_pick_windows_interpreter()`(依序 `shutil.which("python3")`/`shutil.which("python")`)偵測寫進 shim,兩者都找不到才退回 `"python"`。理由:Task 13 移植時沿用的舊寫法與 `install.sh`/`install.ps1` 兩支薄殼自己「python3 優先,找不到才退 python」的判斷邏輯互相矛盾——只有 `python3.exe`、沒有 `python.exe` 的 Windows 機器上,`install.ps1` 用 `python3` 把安裝跑完、印出「裝好了」,但產生的 shim 卻寫死呼叫 `python`,之後每次打 `lumos` 都得到 `'python' is not recognized`,裝完即壞  (因果驗證:`git stash` 只還原 `slim/install.py`、用只有 `python3`、沒有 `python` 的自製 PATH 環境重跑此測試,「不是寫死字面 python」「確實記錄成偵測到的 python3」兩條斷言確實翻紅,回補修復後轉綠)
      ↳ 綁的測試: t_slim_install_windows_shim_does_not_hardcode_python_when_only_python3_available
  ★INVARIANT★ (★2026-08-01 Task 14 修復②★)Windows 路徑下,全域指令的碰撞偵測(是否需要 `--force`)必須同時看 `lumos`(`dst_script`)與 `lumos.cmd`(`dst_shim`)——只看前者的舊寫法,若使用者手動刪了 `lumos` 忘了刪 `lumos.cmd`(單獨殘留),非 `--force` 重裝會直接無聲覆寫殘留的 `lumos.cmd`,繞過「碰撞需要 `--force`」這條保護的存在意義  (因果驗證:同一份 `git stash` 前的舊版,只放殘留 `lumos.cmd`、不放 `lumos`,跑不帶 `--force` 的模擬安裝,「視為碰撞」與「內容未被覆寫」兩條斷言確實翻紅——舊版 rc0 且直接覆寫殘留內容;回補修復後轉綠,且帶 `--force` 仍能正常覆寫,對稱驗證未修過頭)
      ↳ 綁的測試: t_slim_install_windows_collision_detects_orphan_cmd_shim

合約 7 條(改了就是破壞性變更) | 技術債 0 條(可以改)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/slim-uninstall-一行卸載' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 226ms:[0m
# Systems/slim-uninstall-一行卸載.md
type:system | status:done | created:2026-07-31 | updated:2026-08-20 | risk:不可逆 | scope:platform
提醒:這篇有「動了會壞」的合約,動手前一定要看:
  ★INVARIANT★ (★2026-07-31 Task 10 改寫,取代原「sha256 比對 ~/.lumos-slim/scripts/lumos,唯一基準」版★)移除 `~/.local/bin/lumos` 前必先內容比對——基準優先讀 [[Systems/slim-install-安裝器]] 寫的 manifest(`~/.local/share/lumos-slim/manifest.json` 的 `bin_sha256`,★不依賴 `~/.lumos-slim` 存在★),manifest 給不出參照時才退回 `~/.lumos-slim/scripts/lumos` 當備援;兩種基準都拿不到(「基準缺失」)與拿到基準但內容比對不符(「內容真的不符」)訊息分開講,都拒絕移除(除非 `--force`)但都歸類 rc=1(安全性跳過)而非硬錯誤 [test:t_slim_uninstall_refuses_foreign_bin,t_slim_uninstall_direct_install_restores_claude_md] [audit:sonnet/2026-07-31](因果驗證:在暫存副本還原成 Task 10 前的舊版邏輯——`~/.lumos-slim` 不存在時①比對基準缺失就 `exit 2` 中止全流程——重跑綁定測試確實翻紅,回補修復再跑確實轉綠,非稻草人;`git stash` 前後兩輪跑 `python3 scripts/test_lumos.py -k slim_uninstall` 見報告)
  ★INVARIANT★ (★2026-07-31 Task 10 新增,本次修的核心★)四個清理步驟(bin／skill 目錄／`~/.lumos-slim`／CLAUDE.md sentinel)必須**各自獨立判斷、各自執行、互不阻擋**——任一步驟基於安全考量跳過(如 bin 比對不符)絕不能連帶阻止其餘步驟執行,尤其 CLAUDE.md 的完整版還原(④)不得因①失敗而沒機會跑到;★2026-08-02 補上第二種失效形態(原條文只寫了「安全考量跳過」這一種,漏了這一種,而漏掉的這種在 code 裡真的活著)★——**「拋出未捕捉例外」與「主動跳過」同樣構成阻擋**:④ `_restore_claude_md()` 的 `unlink()`/`write_text()` 是裸呼叫、`main()` 呼叫它時也沒有 try,CLAUDE.md 唯讀/磁碟滿/被鎖住時 `PermissionError` 直接炸穿 `main()`,排在後面的⑤(manifest)一次都不會執行,使用者只拿到一段 traceback;①/①b 的 `unlink()`(含 `--force` 分支)同型。修法=每個檔案系統寫入各自 `try/except OSError` → 印一句警告 + `bump(2)` 交給彙總,與本檔既有錯誤路徑一致;★★同日單 reviewer 又抓到第一版修法自己漏了一半:只包了「寫」,`read_text()` 留在 try 外面★★——「檔案系統寫入」這個字眼讓修法只掃了寫。CLAUDE.md `chmod 000`(PermissionError)或內容不是合法 utf-8(中文專案裡別的編輯器存成 Big5、貼進壞位元組都很真實)時,④ 照樣炸穿 `main()`、⑤照樣不執行,★症狀與修之前一模一樣,只是入口從寫換成讀★;且 ★`UnicodeDecodeError` 繼承 `ValueError` 不是 `OSError` 子類★,連寫入側的 `except OSError` 都攔不到(本檔 ①b 段讀 shim 內容時就是同時接兩種——那裡對了、這裡漏了,是不一致的疏漏不是刻意範圍)。讀取側修法:`except OSError` 與 `except UnicodeDecodeError` 分開接、各回一句對應的 rc2 訊息,且★看不懂內容時明確拒絕改寫該檔★ [test:t_slim_uninstall_bin_refusal_does_not_block_claude_md_restore,t_slim_uninstall_claude_md_write_failure_does_not_abort_remaining_steps,t_slim_uninstall_claude_md_read_failure_does_not_abort_remaining_steps] [audit:sonnet/2026-07-31](因果驗證同上:舊版「判定①失敗立即 exit 2」邏輯下,綁定測試斷言「bin 拒絕移除但 CLAUDE.md 仍完整還原」確實翻紅,修復後轉綠。★2026-08-02 第二形態的還原翻紅釘★:現場=把 `CLAUDE.md` 本身 chmod 成 `r--r--r--`(區塊移除後新內容非空,走 `write_text()` 那一支,對唯讀檔開 'w' 必定 PermissionError),把修法還原成裸呼叫後 4 條斷言翻紅——「現場成立」「無 traceback」「manifest 仍被移除」「rc 是 2 不是 1」,且輸出真的印出 `PermissionError` 炸穿 `main()` 的完整堆疊,非稻草人。rc 那條刻意釘死 2 不收 `in (1,2)`——未捕捉例外的 exit code 正好是 1,收寬就掉進 [[Systems/測試假綠形態]] 第②型)
  ★INVARIANT★ `~/.claude/skills/lumos-project-notes/` 移除前必先備份成 `.bak.<timestamp>`,不得 `rm -rf` 未備份——使用者可能在 skill 目錄裡塞過自己的筆記/修改,直接砍會造成不可逆資料損失 [test:t_slim_uninstall_backs_up_and_preserves_custom_files] [audit:sonnet/2026-07-31](獨立審計實測:在暫存副本把備份改成直接 rm -rf,綁定測試確實翻紅)
  ★INVARIANT★ (★2026-07-31 Task 9 改寫★)CLAUDE.md 的 LUMOS-SLIM sentinel 移除/還原必須位元組級精確:讀出區塊內建的 FULL-BACKUP 標記,有備份就把完整版區塊原文精確還原回原位置(與安裝前 byte-equal,含完整版原文一字不差),沒有就單純移除精簡版區塊本體,sentinel 以外內容一律不動;若移除/還原後整檔變空(代表該 CLAUDE.md 是安裝時才新建的)連檔案本身一併刪除,還原成「本來沒這個檔案」——不是留一個空檔 [test:t_slim_uninstall_removes_claude_md_block,t_slim_uninstall_direct_install_restores_claude_md] [audit:sonnet/2026-07-31](獨立審計實測:在暫存副本把「整檔變空即刪檔」的分支關掉,綁定測試確實翻紅——原本不存在的 CLAUDE.md 卸載後留下空檔案)
  ★INVARIANT★ (★2026-08-01 Task 16 修復②,分支終審抓到★)`~/.local/bin/lumos.cmd`(Windows 搭檔 shim)的移除必須與 `~/.local/bin/lumos` 各自獨立判斷、各自執行,不得巢狀在後者的 if 區塊裡——舊寫法把 `dst_shim` 的移除整段巢狀在 `if dst_script.exists() or dst_script.is_symlink():` 底下,`lumos` 不存在但 `lumos.cmd` 還在(使用者手滑只刪了 `lumos`)時,外層 if 判假,整段(含 `--force` 分支)都跳過,孤兒 `lumos.cmd` 永遠清不掉、`--force` 也救不了——牴觸本節點 docstring 自己講的「兩者總是成對安裝/移除」,也是上方「四個清理步驟必須各自獨立判斷」那條 ★INVARIANT★(Task 10)在 Windows 搭檔上的鏡像缺口,還是 [[Systems/slim-install-安裝器]] Task 14②已修過的「碰撞偵測要同時看兩個檔案」的鏡像缺口。修法:shim 沒有 manifest 雜湊可比對,改用「內容是否符合 `install.py` 產生的固定樣板」(`SHIM_TEXT_RE`)當安全判斷基準——符合視為本包裝的 shim,可安全移除(不需要 `--force`);不符合當成使用者自己的東西,拒絕移除 [test:t_slim_uninstall_windows_orphan_cmd_shim_removed,t_slim_uninstall_windows_orphan_cmd_shim_foreign_content_needs_force] [audit:sonnet/2026-08-01](因果驗證:`git stash push -- slim/uninstall.py` 還原成修復前舊版,重跑 `-k orphan_cmd_shim`,「孤兒 lumos.cmd 確實被清掉」「內容不符本包樣板 → rc1」「--force 後檔案確實被移除」三條斷言確實翻紅——舊版對孤兒現場整段不處理、`--force` 分支同樣巢狀救不了;`git stash pop` 還原後重跑轉綠,非稻草人。★踩到的實作坑★:第一版用 `read_text()` 讀 shim 內容比對,universal-newline 轉譯把 `\r\n` 正規化成 `\n`,讓比對 `\r\n` 的正則永遠比不到,即使檔案位元組沒被動過也判成不符——新測試第一輪就抓到,改成 `read_bytes().decode()` 修正)。★獨立審計(五問 rubric,無脈絡 agent,maker≠checker)裁定 legal,留一條已知邊界★:shim 沒有 manifest 雜湊當比對基準(見上,設計時的刻意取捨),`SHIM_TEXT_RE` 是內容樣板比對不是雜湊比對——理論上若使用者自己寫的檔案剛好與樣板逐位元組相同(機率趨近零,樣板含 `install.py` 安裝當下偵測到的直譯器字串),不帶 `--force` 也會被判定為本包裝的 shim 而移除;風險評估:發生機率極低、就算誤觸也只會砍掉一個小 shim 檔不是使用者資料,爆炸半徑小,故接受此取捨,不視為擋這條 ★INVARIANT★ 落地的理由
  ★INVARIANT★ (★2026-08-01 真跑冒煙抓到,測試全綠看不到★)卸載必須把身分證 manifest 自己也清掉(`~/.local/share/lumos-slim/manifest.json` 與空掉的 `lumos-slim/` 父目錄)——在此之前卸載跑完會把它留在使用者 $HOME,彙總卻印「✓ 全部完成」;★唯一的資料相依(非控制相依,不違反「各步互不阻擋」)★:①/①b 任一份 bin 檔案基於安全考量未移除時 manifest 必須保留並印一句為什麼,它是使用者之後加 `--force`/手動確認時唯一的比對基準,先刪等於銷毀判斷依據、下次重跑只會落到「基準缺失」;★這個判斷必須查檔案系統實況(`dst_script.exists() or dst_script.is_symlink() or dst_shim.exists()`),不得用分支簿記★(代碼審 r4 抓到:原本在①/①b 每條「沒移除」分支手動設旗標,①b 的 `OSError` 分支漏設一條——Windows 上 `lumos.cmd` 讀不到時 shim 還在、manifest 卻照樣被刪;分支簿記天生會漏,查實況對現有與未來新增的分支都自動成立);★該實況查詢本身有兩個邊界,r5 抓到(都是 r4 修法自己引入的)★:(a) shim 那一半必須受 `IS_WIN` 限定——①b 整段包在 `if IS_WIN:` 底下,非 Windows 機器根本不會看/動 `lumos.cmd`,無條件檢查會讓 macOS/Linux 上一個不相干的同名檔案把 manifest 永久卡住,且⑤沒有 `--force` 分支(①/①b 才有)、使用者照訊息重跑也解不開;(b) shim 那一半要跟 `dst_script` 對稱補 `is_symlink()`——`exists()` 對斷鏈 symlink 回傳 False,但它仍佔著路徑、①b 也確實沒移除它;★爆炸半徑★只刪該檔與其空父目錄,`~/.local/share` 底下其他一律不碰(眾多工具共用);★父目錄清理是選配收尾,必須自己一個 try★(代碼審 r3 抓到):與 `unlink()` 共用 try 時,`rmdir` 失敗會印成「移除 manifest 失敗」並 bump(2),但 manifest 其實已刪成功——錯誤歸因誤導使用者以為要手動處理;選配收尾失敗只印一句、不升級 rc [test:t_slim_uninstall_removes_manifest_when_bin_cleared,t_slim_uninstall_keeps_manifest_when_bin_refused,t_slim_uninstall_manifest_parent_cleanup_is_best_effort,t_slim_uninstall_keeps_manifest_when_shim_remains,t_slim_uninstall_manifest_ignores_stray_cmd_on_posix,t_slim_uninstall_keeps_manifest_when_shim_is_broken_symlink] [audit:sonnet/2026-08-01](還原翻紅釘,兩個突變各驗一條:突變A 把⑤整段移除→removes_manifest 翻紅;突變B 把 `if bin_cleared:` 改成 `if True:`→keeps_manifest 翻紅;還原後 75 passed 0 failed,非稻草人。★發現路徑值得記★:2011 條測試全綠都沒看到它,是對打包後的 dist 做真跑冒煙才發現——本專案第二次由端到端真跑接住測試套件盲區,盲區型別是「根本沒去驗」而非「斷言寫錯」。★r3 修法的翻紅釘第一版是錯的,記為第十一次撞坑★:現場用「父目錄塞別的檔案讓它非空」→ `rmdir` 根本不會被執行、例外路徑一次都沒跑到,突變照樣全綠;改成 `chmod ~/.local/share 0o500`(unlink 需 `lumos-slim/` 寫權限仍有、rmdir 需 `share/` 寫權限已無)才真的翻紅 3 條斷言。★通則★:要驗例外處理,現場必須真的讓那個呼叫拋例外,不能只是讓它不被執行)
summary:
  FLOW:(★2026-07-31 Task 10 端到端實測抓到真 bug 後改版★)`curl -fsSL <raw-url>/uninstall.sh | bash`(或裝好後直接跑 `~/.l…
  KEY:★INVARIANT★(★2026-07-31 Task 10 改寫,取代原「sha256 比對 ~/.lumos-slim/scripts/lumos,唯一基準」版★)移除 `~/.loca…
verified_by: [[Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復]], [[Verification/2026-07-31_公開精簡版代碼審第二輪minor修復]], [[Verification/2026-07-31_slim-claude-md注入]], [[Verification/2026-07-31_slim-claude-md第三次裁定取代與備份還原]], [[Verification/2026-07-31_slim-uninstall步驟獨立化與manifest基準修復]], [[Verification/2026-08-01_slim-python移植]], [[Verification/2026-08-01_slim-windows兩缺陷修復]], [[Verification/2026-08-01_slim-ps1早期分支exit修復]], [[Verification/2026-08-01_slim-終審三缺陷修復]], [[Verification/2026-08-01_slim-manifest殘留與代碼審六輪]], [[Verification/2026-08-02_slim三缺陷修復_實驗產出]], [[Verification/2026-08-03_Windows回歸測試三缺陷]], [[Verification/2026-08-03_Windows真機三輪驗證通過]], [[Verification/2026-08-21_L4交叉審計30節點清帳]]
plan_refs: [[Projects/公開精簡版_計劃]]
→ 連出 (19):
  • Projects/公開精簡版_實作計畫.md [done]
  • Projects/公開精簡版_計劃.md [doing]
  • Systems/lumos-cli-lifecycle.md [done]
  • Systems/slim-get-一行安裝.md [done]
  • Systems/slim-install-安裝器.md [done]
  • Verification/2026-07-31_slim-claude-md注入.md [pass]
  • Verification/2026-07-31_slim-claude-md第三次裁定取代與備份還原.md [pass]
  • Verification/2026-07-31_slim-uninstall步驟獨立化與manifest基準修復.md [pass]
  • Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復.md [pass]
  • Verification/2026-07-31_公開精簡版代碼審第二輪minor修復.md [pass]
  • Verification/2026-08-01_slim-manifest殘留與代碼審六輪.md [pass]
  • Verification/2026-08-01_slim-ps1早期分支exit修復.md [pass]
  • Verification/2026-08-01_slim-python移植.md [pass]
  • Verification/2026-08-01_slim-windows兩缺陷修復.md [pass]
  • Verification/2026-08-01_slim-終審三缺陷修復.md [pass]
  • Verification/2026-08-02_slim三缺陷修復_實驗產出.md [pass]
  • Verification/2026-08-03_Windows回歸測試三缺陷.md [pass]
  • Verification/2026-08-03_Windows真機三輪驗證通過.md [pass]
  • Verification/2026-08-21_L4交叉審計30節點清帳.md [pass]
← 連入 (21):
  • Issues/主程式讀取路徑漏接UnicodeDecodeError.md [open]
  • MOC/index.md [doing]
  • Projects/公開精簡版_實作計畫.md [done]
  • Projects/公開精簡版_計劃.md [doing]
  • Systems/lumos-cli-lifecycle.md [done]
  • Systems/slim-get-一行安裝.md [done]
  • Systems/slim-install-安裝器.md [done]
  • Systems/slim-readme.md [done]
  • Verification/2026-07-31_slim-claude-md注入.md [pass]
  • Verification/2026-07-31_slim-claude-md第三次裁定取代與備份還原.md [pass]
  • Verification/2026-07-31_slim-uninstall步驟獨立化與manifest基準修復.md [pass]
  • Verification/2026-07-31_公開精簡版一行安裝卸載與代碼審修復.md [pass]
  • Verification/2026-07-31_公開精簡版代碼審第二輪minor修復.md [pass]
  • Verification/2026-08-01_slim-manifest殘留與代碼審六輪.md [pass]
  • Verification/2026-08-01_slim-ps1早期分支exit修復.md [pass]
  • Verification/2026-08-01_slim-windows兩缺陷修復.md [pass]
  • Verification/2026-08-01_slim-終審三缺陷修復.md [pass]
  • Verification/2026-08-02_slim三缺陷修復_實驗產出.md [pass]
  • Verification/2026-08-03_Windows回歸測試三缺陷.md [pass]
  • Verification/2026-08-03_Windows真機三輪驗證通過.md [pass]
  • Verification/2026-08-03_Windows真機驗證五缺陷修復.md [superseded]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/slim-uninstall-一行卸載'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 222ms:[0m
# Systems/slim-uninstall-一行卸載.md
  ★INVARIANT★ (★2026-07-31 Task 10 改寫,取代原「sha256 比對 ~/.lumos-slim/scripts/lumos,唯一基準」版★)移除 `~/.local/bin/lumos` 前必先內容比對——基準優先讀 [[Systems/slim-install-安裝器]] 寫的 manifest(`~/.local/share/lumos-slim/manifest.json` 的 `bin_sha256`,★不依賴 `~/.lumos-slim` 存在★),manifest 給不出參照時才退回 `~/.lumos-slim/scripts/lumos` 當備援;兩種基準都拿不到(「基準缺失」)與拿到基準但內容比對不符(「內容真的不符」)訊息分開講,都拒絕移除(除非 `--force`)但都歸類 rc=1(安全性跳過)而非硬錯誤  (因果驗證:在暫存副本還原成 Task 10 前的舊版邏輯——`~/.lumos-slim` 不存在時①比對基準缺失就 `exit 2` 中止全流程——重跑綁定測試確實翻紅,回補修復再跑確實轉綠,非稻草人;`git stash` 前後兩輪跑 `python3 scripts/test_lumos.py -k slim_uninstall` 見報告)
      ↳ 綁的測試: t_slim_uninstall_refuses_foreign_bin, t_slim_uninstall_direct_install_restores_claude_md
  ★INVARIANT★ (★2026-07-31 Task 10 新增,本次修的核心★)四個清理步驟(bin／skill 目錄／`~/.lumos-slim`／CLAUDE.md sentinel)必須**各自獨立判斷、各自執行、互不阻擋**——任一步驟基於安全考量跳過(如 bin 比對不符)絕不能連帶阻止其餘步驟執行,尤其 CLAUDE.md 的完整版還原(④)不得因①失敗而沒機會跑到;★2026-08-02 補上第二種失效形態(原條文只寫了「安全考量跳過」這一種,漏了這一種,而漏掉的這種在 code 裡真的活著)★——**「拋出未捕捉例外」與「主動跳過」同樣構成阻擋**:④ `_restore_claude_md()` 的 `unlink()`/`write_text()` 是裸呼叫、`main()` 呼叫它時也沒有 try,CLAUDE.md 唯讀/磁碟滿/被鎖住時 `PermissionError` 直接炸穿 `main()`,排在後面的⑤(manifest)一次都不會執行,使用者只拿到一段 traceback;①/①b 的 `unlink()`(含 `--force` 分支)同型。修法=每個檔案系統寫入各自 `try/except OSError` → 印一句警告 + `bump(2)` 交給彙總,與本檔既有錯誤路徑一致;★★同日單 reviewer 又抓到第一版修法自己漏了一半:只包了「寫」,`read_text()` 留在 try 外面★★——「檔案系統寫入」這個字眼讓修法只掃了寫。CLAUDE.md `chmod 000`(PermissionError)或內容不是合法 utf-8(中文專案裡別的編輯器存成 Big5、貼進壞位元組都很真實)時,④ 照樣炸穿 `main()`、⑤照樣不執行,★症狀與修之前一模一樣,只是入口從寫換成讀★;且 ★`UnicodeDecodeError` 繼承 `ValueError` 不是 `OSError` 子類★,連寫入側的 `except OSError` 都攔不到(本檔 ①b 段讀 shim 內容時就是同時接兩種——那裡對了、這裡漏了,是不一致的疏漏不是刻意範圍)。讀取側修法:`except OSError` 與 `except UnicodeDecodeError` 分開接、各回一句對應的 rc2 訊息,且★看不懂內容時明確拒絕改寫該檔★  (因果驗證同上:舊版「判定①失敗立即 exit 2」邏輯下,綁定測試斷言「bin 拒絕移除但 CLAUDE.md 仍完整還原」確實翻紅,修復後轉綠。★2026-08-02 第二形態的還原翻紅釘★:現場=把 `CLAUDE.md` 本身 chmod 成 `r--r--r--`(區塊移除後新內容非空,走 `write_text()` 那一支,對唯讀檔開 'w' 必定 PermissionError),把修法還原成裸呼叫後 4 條斷言翻紅——「現場成立」「無 traceback」「manifest 仍被移除」「rc 是 2 不是 1」,且輸出真的印出 `PermissionError` 炸穿 `main()` 的完整堆疊,非稻草人。rc 那條刻意釘死 2 不收 `in (1,2)`——未捕捉例外的 exit code 正好是 1,收寬就掉進 [[Systems/測試假綠形態]] 第②型)
      ↳ 綁的測試: t_slim_uninstall_bin_refusal_does_not_block_claude_md_restore, t_slim_uninstall_claude_md_write_failure_does_not_abort_remaining_steps, t_slim_uninstall_claude_md_read_failure_does_not_abort_remaining_steps
  ★INVARIANT★ `~/.claude/skills/lumos-project-notes/` 移除前必先備份成 `.bak.<timestamp>`,不得 `rm -rf` 未備份——使用者可能在 skill 目錄裡塞過自己的筆記/修改,直接砍會造成不可逆資料損失  (獨立審計實測:在暫存副本把備份改成直接 rm -rf,綁定測試確實翻紅)
      ↳ 綁的測試: t_slim_uninstall_backs_up_and_preserves_custom_files
  ★INVARIANT★ (★2026-07-31 Task 9 改寫★)CLAUDE.md 的 LUMOS-SLIM sentinel 移除/還原必須位元組級精確:讀出區塊內建的 FULL-BACKUP 標記,有備份就把完整版區塊原文精確還原回原位置(與安裝前 byte-equal,含完整版原文一字不差),沒有就單純移除精簡版區塊本體,sentinel 以外內容一律不動;若移除/還原後整檔變空(代表該 CLAUDE.md 是安裝時才新建的)連檔案本身一併刪除,還原成「本來沒這個檔案」——不是留一個空檔  (獨立審計實測:在暫存副本把「整檔變空即刪檔」的分支關掉,綁定測試確實翻紅——原本不存在的 CLAUDE.md 卸載後留下空檔案)
      ↳ 綁的測試: t_slim_uninstall_removes_claude_md_block, t_slim_uninstall_direct_install_restores_claude_md
  ★INVARIANT★ (★2026-08-01 Task 16 修復②,分支終審抓到★)`~/.local/bin/lumos.cmd`(Windows 搭檔 shim)的移除必須與 `~/.local/bin/lumos` 各自獨立判斷、各自執行,不得巢狀在後者的 if 區塊裡——舊寫法把 `dst_shim` 的移除整段巢狀在 `if dst_script.exists() or dst_script.is_symlink():` 底下,`lumos` 不存在但 `lumos.cmd` 還在(使用者手滑只刪了 `lumos`)時,外層 if 判假,整段(含 `--force` 分支)都跳過,孤兒 `lumos.cmd` 永遠清不掉、`--force` 也救不了——牴觸本節點 docstring 自己講的「兩者總是成對安裝/移除」,也是上方「四個清理步驟必須各自獨立判斷」那條 ★INVARIANT★(Task 10)在 Windows 搭檔上的鏡像缺口,還是 [[Systems/slim-install-安裝器]] Task 14②已修過的「碰撞偵測要同時看兩個檔案」的鏡像缺口。修法:shim 沒有 manifest 雜湊可比對,改用「內容是否符合 `install.py` 產生的固定樣板」(`SHIM_TEXT_RE`)當安全判斷基準——符合視為本包裝的 shim,可安全移除(不需要 `--force`);不符合當成使用者自己的東西,拒絕移除  (因果驗證:`git stash push -- slim/uninstall.py` 還原成修復前舊版,重跑 `-k orphan_cmd_shim`,「孤兒 lumos.cmd 確實被清掉」「內容不符本包樣板 → rc1」「--force 後檔案確實被移除」三條斷言確實翻紅——舊版對孤兒現場整段不處理、`--force` 分支同樣巢狀救不了;`git stash pop` 還原後重跑轉綠,非稻草人。★踩到的實作坑★:第一版用 `read_text()` 讀 shim 內容比對,universal-newline 轉譯把 `\r\n` 正規化成 `\n`,讓比對 `\r\n` 的正則永遠比不到,即使檔案位元組沒被動過也判成不符——新測試第一輪就抓到,改成 `read_bytes().decode()` 修正)。★獨立審計(五問 rubric,無脈絡 agent,maker≠checker)裁定 legal,留一條已知邊界★:shim 沒有 manifest 雜湊當比對基準(見上,設計時的刻意取捨),`SHIM_TEXT_RE` 是內容樣板比對不是雜湊比對——理論上若使用者自己寫的檔案剛好與樣板逐位元組相同(機率趨近零,樣板含 `install.py` 安裝當下偵測到的直譯器字串),不帶 `--force` 也會被判定為本包裝的 shim 而移除;風險評估:發生機率極低、就算誤觸也只會砍掉一個小 shim 檔不是使用者資料,爆炸半徑小,故接受此取捨,不視為擋這條 ★INVARIANT★ 落地的理由
      ↳ 綁的測試: t_slim_uninstall_windows_orphan_cmd_shim_removed, t_slim_uninstall_windows_orphan_cmd_shim_foreign_content_needs_force
  ★INVARIANT★ (★2026-08-01 真跑冒煙抓到,測試全綠看不到★)卸載必須把身分證 manifest 自己也清掉(`~/.local/share/lumos-slim/manifest.json` 與空掉的 `lumos-slim/` 父目錄)——在此之前卸載跑完會把它留在使用者 $HOME,彙總卻印「✓ 全部完成」;★唯一的資料相依(非控制相依,不違反「各步互不阻擋」)★:①/①b 任一份 bin 檔案基於安全考量未移除時 manifest 必須保留並印一句為什麼,它是使用者之後加 `--force`/手動確認時唯一的比對基準,先刪等於銷毀判斷依據、下次重跑只會落到「基準缺失」;★這個判斷必須查檔案系統實況(`dst_script.exists() or dst_script.is_symlink() or dst_shim.exists()`),不得用分支簿記★(代碼審 r4 抓到:原本在①/①b 每條「沒移除」分支手動設旗標,①b 的 `OSError` 分支漏設一條——Windows 上 `lumos.cmd` 讀不到時 shim 還在、manifest 卻照樣被刪;分支簿記天生會漏,查實況對現有與未來新增的分支都自動成立);★該實況查詢本身有兩個邊界,r5 抓到(都是 r4 修法自己引入的)★:(a) shim 那一半必須受 `IS_WIN` 限定——①b 整段包在 `if IS_WIN:` 底下,非 Windows 機器根本不會看/動 `lumos.cmd`,無條件檢查會讓 macOS/Linux 上一個不相干的同名檔案把 manifest 永久卡住,且⑤沒有 `--force` 分支(①/①b 才有)、使用者照訊息重跑也解不開;(b) shim 那一半要跟 `dst_script` 對稱補 `is_symlink()`——`exists()` 對斷鏈 symlink 回傳 False,但它仍佔著路徑、①b 也確實沒移除它;★爆炸半徑★只刪該檔與其空父目錄,`~/.local/share` 底下其他一律不碰(眾多工具共用);★父目錄清理是選配收尾,必須自己一個 try★(代碼審 r3 抓到):與 `unlink()` 共用 try 時,`rmdir` 失敗會印成「移除 manifest 失敗」並 bump(2),但 manifest 其實已刪成功——錯誤歸因誤導使用者以為要手動處理;選配收尾失敗只印一句、不升級 rc  (還原翻紅釘,兩個突變各驗一條:突變A 把⑤整段移除→removes_manifest 翻紅;突變B 把 `if bin_cleared:` 改成 `if True:`→keeps_manifest 翻紅;還原後 75 passed 0 failed,非稻草人。★發現路徑值得記★:2011 條測試全綠都沒看到它,是對打包後的 dist 做真跑冒煙才發現——本專案第二次由端到端真跑接住測試套件盲區,盲區型別是「根本沒去驗」而非「斷言寫錯」。★r3 修法的翻紅釘第一版是錯的,記為第十一次撞坑★:現場用「父目錄塞別的檔案讓它非空」→ `rmdir` 根本不會被執行、例外路徑一次都沒跑到,突變照樣全綠;改成 `chmod ~/.local/share 0o500`(unlink 需 `lumos-slim/` 寫權限仍有、rmdir 需 `share/` 寫權限已無)才真的翻紅 3 條斷言。★通則★:要驗例外處理,現場必須真的讓那個呼叫拋例外,不能只是讓它不被執行)
      ↳ 綁的測試: t_slim_uninstall_removes_manifest_when_bin_cleared, t_slim_uninstall_keeps_manifest_when_bin_refused, t_slim_uninstall_manifest_parent_cleanup_is_best_effort, t_slim_uninstall_keeps_manifest_when_shim_remains, t_slim_uninstall_manifest_ignores_stray_cmd_on_posix, t_slim_uninstall_keeps_manifest_when_shim_is_broken_symlink

合約 6 條(改了就是破壞性變更) | 技術債 0 條(可以改)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/design-loop' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 229ms:[0m
# Systems/design-loop.md
type:system | status:done | created:2026-06-26 | updated:2026-08-29 | risk:守衛面 | scope:loop-engineering
提醒:這篇有「動了會壞」的合約,動手前一定要看:
  ★INVARIANT★ 處置閘第五步(2026-09-08,[[Projects/條款綁測試算進度_計劃]] d3/d4):設計審迴圈(loop id 不是 code- 開頭;code 開頭但沒連字號的也當設計審)、首筆帳在 2026-09-09T00:00+08:00 之後(換算 UTC 比)→ 審材必須是 .md 計劃(拿 .patch 就 FAIL);計劃有 [SN] 時任一條款定義行沒有 [test:]/[manual:≥4 字且含實字] 就不得 PASS(理由印「條款綁定」;哪些字看得見沿用 _visible_lines(行層級:```/~~~ 各自配對且關的至少要一樣長、縮排 ≤3 才是圍欄)+ _strip_inline_markup(行內:單/雙反引號 span、未閉合反引號之後一律不信);★不偵測 HTML 註解★(註解裡的 [SN] 走認不得→擋);被截掉的段落裡有 [SN]=認不得,擋;一行只認一條,後面的 [SN] 是引用;勾選框/• + — 1) 1、a. aa. 一、十一、甲) ① ㈠ ⅰ 列都算定義行(1–2 字母/中文數字+分隔符=編號,三字母以上=詞);同編號定義兩次擋;[SN] 像清單項卻是不認得的前綴=格式看不懂,擋(不管有沒有別的合法條款、也不管該編號是否已在別處定義);詞+冒號(注:[S1])算散文;只在散文/標題提到 [SN]=視同未啟用跳過;懸空只提醒);code- 迴圈、無 [SN]、舊迴圈、凍結/回放模式跳過;壞 ts 與索引建不起來 fail-closed、計劃讀不到同 G3 擋下 rc2 [test:t_disposal_clause_gate] [audit:sonnet/2026-09-08]
summary:
  KEY:[2026-09-09 審查有沒有用記帳]收貨線多一道機械閘:席報告沒正規化(檔首檔級 severity 行、每條 finding 恰一行獨立宣告)記帳 rc2 並在治理帳留 canary/b…
  KEY:★INVARIANT★ 處置閘第五步(2026-09-08,[[Projects/條款綁測試算進度_計劃]] d3/d4):設計審迴圈(loop id 不是 code- 開頭;code 開頭但…
verified_by: [[Verification/2026-06-19_design-loop]], [[Verification/2026-07-09_loop三輪壓縮]], [[Verification/2026-07-10_審計loop研究硬化]], [[Verification/2026-07-16_dloop提效M2_cluster帳]], [[Verification/2026-07-16_replay校準baseline_v0]], [[Verification/2026-08-04_design-loop重設計落地T1-T7]], [[Verification/2026-08-06_驗證層自證三件S1S3落地]], [[Verification/2026-08-08_風險類反問v1落地]], [[Verification/2026-08-14_canary協議停用none制落地]], [[Verification/2026-08-18_派工編制資料化落地]], [[Verification/2026-08-18_循序tier錨定落地]], [[Verification/2026-08-21_L4交叉審計30節點清帳]], [[Verification/2026-08-25_設計審收斂重定義落地]], [[Verification/2026-08-25_迴圈摩擦兩修落地]], [[Verification/2026-08-26_新舊制同料對照_v0]], [[Verification/2026-08-30_intake守衛T1-T4落地]], [[Verification/2026-09-03_席間覆蓋率離線量測]], [[Verification/2026-09-03_派工攔截點實測]], [[Verification/2026-09-04_Codex完全支援S2迴圈編排驗收]], [[Verification/2026-09-11_skills健檢]]
→ 連出 (21):
  • Systems/loop-convergence-recording.md [done]
  • Verification/2026-06-19_design-loop.md [pass]
  • Verification/2026-07-09_loop三輪壓縮.md [pass]
  • Verification/2026-07-10_審計loop研究硬化.md [pass]
  • Verification/2026-07-16_dloop提效M2_cluster帳.md [pass]
  • Verification/2026-07-16_replay校準baseline_v0.md [pass]
  • Verification/2026-08-04_design-loop重設計落地T1-T7.md [pass]
  • Verification/2026-08-06_驗證層自證三件S1S3落地.md [pass]
  • Verification/2026-08-08_風險類反問v1落地.md [pass]
  • Verification/2026-08-14_canary協議停用none制落地.md [pass]
  • Verification/2026-08-18_循序tier錨定落地.md [pass]
  • Verification/2026-08-18_派工編制資料化落地.md [pass]
  • Verification/2026-08-21_L4交叉審計30節點清帳.md [pass]
  • Verification/2026-08-25_設計審收斂重定義落地.md [pass]
  • Verification/2026-08-25_迴圈摩擦兩修落地.md [pass]
  • Verification/2026-08-26_新舊制同料對照_v0.md [pass]
  • Verification/2026-08-30_intake守衛T1-T4落地.md [pass]
  • Verification/2026-09-03_席間覆蓋率離線量測.md [pass]
  • Verification/2026-09-03_派工攔截點實測.md [pass]
  • Verification/2026-09-04_Codex完全支援S2迴圈編排驗收.md [pass]
  • Verification/2026-09-11_skills健檢.md [pass]
← 連入 (52):
  • Issues/design-loop折入漂移_機械守衛.md [done]
  • Issues/loop機制痛點_Landmark_code-crossclaim實跑回饋.md [open]
  • MOC/index.md [doing]
  • Projects/Agentflow吸收_調研.md [doing]
  • Projects/Codex完全支援_計劃.md [done]
  • Projects/Codex工作流整合_調研.md [doing]
  • Projects/GPT外部評審吸收_計劃.md [doing]
  • Projects/Spotify-shunt吸收_調研.md [doing]
  • Projects/canary注意力檢查失效.md [done]
  • Projects/canary生成硬化_計劃.md [done]
  • Projects/code席爆炸半徑供糧_計劃.md [done]
  • Projects/code階段強化_計劃.md [doing]
  • Projects/design-loop判準重定位.md [doing]
  • Projects/design-loop折入守衛_計劃.md [done]
  • Projects/design-loop提效_計劃.md [doing]
  • Projects/design-loop輕量檔_計劃.md [doing]
  • Projects/design-loop重設計.md [done]
  • Projects/from-scratch重生守衛_計劃.md [doing]
  • Projects/impact-diff橋接_計劃.md [done]
  • Projects/impact鏡頭機械化_計劃.md [doing]
  • Projects/loop三輪壓縮_計劃.md [done]
  • Projects/loop機械脊椎M1包_計劃.md [done]
  • Projects/reviewer結構明文化_計劃.md [done]
  • Projects/skills提示工程優化_調研.md [done]
  • Projects/一句話層供糧_計劃.md [done]
  • Projects/中心性重驗排程_計劃.md [done]
  • Projects/全盤外審2026-07_調研.md [doing]
  • Projects/公開精簡版_計劃.md [doing]
  • Projects/子代理續談調研.md [done]
  • Projects/審查帳節點映射_計劃.md [superseded]
  • Projects/席位人格化_計劃.md [done]
  • Projects/收斂機制優化調研2026-08-14.md [doing]
  • Projects/收斂閘殘餘估計降級_計劃.md [done]
  • Projects/收斂閘漏項敏感度_計劃.md [superseded]
  • Projects/收斂閘漏項敏感度v2_計劃.md [doing]
  • Projects/改制回測_計劃.md [doing]
  • Projects/每支檔有家_計劃.md [doing]
  • Projects/派工時自動補清單_計劃.md [superseded]
  • Projects/派工鏡頭注入_計劃.md [done]
  • Projects/社群演算法補強_調研.md [done]
  • Projects/結清式收斂_計劃.md [doing]
  • Projects/設計審收斂重定義_計劃.md [done]
  • Projects/驗證層去模型化_計劃.md [done]
  • Systems/codex-harness.md [done]
  • Systems/judge-severity-gate.md [done]
  • Systems/開發工作流總覽.md [done]
  • Verification/2026-07-09_loop三輪壓縮.md [pass]
  • Verification/2026-07-10_審計loop研究硬化.md [pass]
  • Verification/2026-07-16_dloop提效M2_cluster帳.md [pass]
  • Verification/2026-07-16_replay校準baseline_v0.md [pass]
  • Verification/2026-08-26_新舊制同料對照_v0.md [pass]
  • Verification/2026-09-03_派工攔截點實測.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/design-loop'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 219ms:[0m
# Systems/design-loop.md
  ★INVARIANT★ 處置閘第五步(2026-09-08,[[Projects/條款綁測試算進度_計劃]] d3/d4):設計審迴圈(loop id 不是 code- 開頭;code 開頭但沒連字號的也當設計審)、首筆帳在 2026-09-09T00:00+08:00 之後(換算 UTC 比)→ 審材必須是 .md 計劃(拿 .patch 就 FAIL);計劃有 [SN] 時任一條款定義行沒有 [test:]/ 就不得 PASS(理由印「條款綁定」;哪些字看得見沿用 _visible_lines(行層級:```/~~~ 各自配對且關的至少要一樣長、縮排 ≤3 才是圍欄)+ _strip_inline_markup(行內:單/雙反引號 span、未閉合反引號之後一律不信);★不偵測 HTML 註解★(註解裡的 [SN] 走認不得→擋);被截掉的段落裡有 [SN]=認不得,擋;一行只認一條,後面的 [SN] 是引用;勾選框/• + — 1) 1、a. aa. 一、十一、甲) ① ㈠ ⅰ 列都算定義行(1–2 字母/中文數字+分隔符=編號,三字母以上=詞);同編號定義兩次擋;[SN] 像清單項卻是不認得的前綴=格式看不懂,擋(不管有沒有別的合法條款、也不管該編號是否已在別處定義);詞+冒號(注:[S1])算散文;只在散文/標題提到 [SN]=視同未啟用跳過;懸空只提醒);code- 迴圈、無 [SN]、舊迴圈、凍結/回放模式跳過;壞 ts 與索引建不起來 fail-closed、計劃讀不到同 G3 擋下 rc2
      ↳ 綁的測試: t_disposal_clause_gate

合約 1 條(改了就是破壞性變更) | 技術債 0 條(可以改)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Systems/lumos-cli-lifecycle' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 218ms:[0m
# Systems/lumos-cli-lifecycle.md
type:system | status:done | created:2026-06-26 | updated:2026-08-20 | risk:不可逆 | scope:platform
提醒:這篇有「動了會壞」的合約,動手前一定要看:
  ★INVARIANT★ re-inject 只覆蓋 sentinel 之間 body、sentinel 之外 CLAUDE.md 內容 byte-equal 保留(改=毀使用者手寫內容=breaking) [test:t_reinject_preserves_outside] [audit:sonnet/2026-07-06]
  ★DEBT★ CLAUDE.md START sentinel 的版本戳(LUMOS_VERSION)=人可讀標籤/advisory nudge,非正確性守衛(內容比對 doctor Check D 才是;版本在 body 外、bump 不觸發守衛)
  ★DEBT★ pull 成功但來源工作區髒(未提交改動)仍會被 vendor 出去——本輪未擋,因來源 repo 的 docs/.governance-log.jsonl 等簿記檔恆髒,一律擋會天天卡住;要做需先分「簿記檔 vs 實質檔」白名單
summary:
  KEY:[2026-08-05]來源 repo 自身的 reinject 路徑補齊——update 在來源 repo 改走 reinject-only(原:ERROR 拒跑);init 既有 vaul…
  FLOW:機器層一次裝(bootstrap=clone Lumos源→install全域lumos+user-scope skills→repo hooks｜或單獨 install/uninstall…
verified_by: [[Verification/2026-07-06_CLAUDE注入re-sync]], [[Verification/2026-07-25_bootstrap一鍵對稱]], [[Verification/2026-08-05_流程優化六件落地]], [[Verification/2026-08-19_精簡版update指令落地]], [[Verification/2026-08-20_gov-stats落地]], [[Verification/2026-08-21_L4交叉審計30節點清帳]], [[Verification/2026-08-21_doctor-run事件落地]], [[Verification/2026-08-21_工具鏈體檢修復批]], [[Verification/2026-08-22_指令索引與情境探針]], [[Verification/2026-09-04_Codex完全支援S0安裝層驗收]], [[Verification/2026-09-04_Codex完全支援S1hook適配驗收]], [[Verification/2026-09-04_Codex完全支援S3量測驗收]]
→ 連出 (19):
  • Projects/CLAUDE注入re-sync與版本標籤_計劃.md [done]
  • Systems/lumos-cli-read.md [done]
  • Systems/lumos-cli-write.md [done]
  • Systems/lumos-deinit.md [done]
  • Systems/native-windows-support.md [done]
  • Systems/slim-install-安裝器.md [done]
  • Systems/slim-uninstall-一行卸載.md [done]
  • Verification/2026-07-06_CLAUDE注入re-sync.md [pass]
  • Verification/2026-07-25_bootstrap一鍵對稱.md [pass]
  • Verification/2026-08-05_流程優化六件落地.md [pass]
  • Verification/2026-08-19_精簡版update指令落地.md [pass]
  • Verification/2026-08-20_gov-stats落地.md [pass]
  • Verification/2026-08-21_L4交叉審計30節點清帳.md [pass]
  • Verification/2026-08-21_doctor-run事件落地.md [pass]
  • Verification/2026-08-21_工具鏈體檢修復批.md [pass]
  • Verification/2026-08-22_指令索引與情境探針.md [pass]
  • Verification/2026-09-04_Codex完全支援S0安裝層驗收.md [pass]
  • Verification/2026-09-04_Codex完全支援S1hook適配驗收.md [pass]
  • Verification/2026-09-04_Codex完全支援S3量測驗收.md [pass]
← 連入 (34):
  • Issues/deinit整夾刪使用者檔.md [done]
  • Issues/hook卸載殘留註冊.md [done]
  • Issues/init-force-slug誤用basename.md [done]
  • Issues/vendored測試套件在消費端假紅.md [resolved]
  • Issues/探針沙盒改動真全域機器狀態.md [doing]
  • Issues/測試未隔離HOME刪掉真機Claude-hooks.md [resolved]
  • MOC/index.md [doing]
  • Projects/CLAUDE注入re-sync與版本標籤_計劃.md [done]
  • Projects/Codex完全支援_計劃.md [done]
  • Projects/Codex行為精修_計劃.md [doing]
  • Projects/bootstrap一鍵對稱_計劃.md [done]
  • Projects/cochange守衛_計劃.md [done]
  • Projects/enforcement儀表板_計劃.md [done]
  • Projects/install全域hook同步_計劃.md [done]
  • Projects/kotlin慣例skill_計劃.md [done]
  • Projects/teardown一鍵拆機_計劃.md [doing]
  • Projects/上下文瘦身_計劃.md [done]
  • Projects/先問世界_存量掃描裁定.md [done]
  • Projects/公開精簡版_實作計畫.md [done]
  • Projects/公開精簡版_計劃.md [doing]
  • Projects/版本發布流程_計劃.md [doing]
  • Systems/cochange-guard.md [done]
  • Systems/codex-harness.md [done]
  • Systems/lumos-cli-read.md [done]
  • Systems/lumos-cli-write.md [done]
  • Systems/slim-gen-生成器.md [done]
  • Systems/slim-get-一行安裝.md [done]
  • Systems/slim-install-安裝器.md [done]
  • Systems/slim-readme.md [done]
  • Systems/slim-scan-掃描器.md [done]
  • Systems/slim-skill-修剪.md [done]
  • Systems/slim-uninstall-一行卸載.md [done]
  • Verification/2026-07-06_CLAUDE注入re-sync.md [pass]
  • Verification/2026-08-19_精簡版update指令落地.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Systems/lumos-cli-lifecycle'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 225ms:[0m
# Systems/lumos-cli-lifecycle.md
  ★INVARIANT★ re-inject 只覆蓋 sentinel 之間 body、sentinel 之外 CLAUDE.md 內容 byte-equal 保留(改=毀使用者手寫內容=breaking)
      ↳ 綁的測試: t_reinject_preserves_outside
  ★DEBT★ CLAUDE.md START sentinel 的版本戳(LUMOS_VERSION)=人可讀標籤/advisory nudge,非正確性守衛(內容比對 doctor Check D 才是;版本在 body 外、bump 不觸發守衛)
  ★DEBT★ pull 成功但來源工作區髒(未提交改動)仍會被 vendor 出去——本輪未擋,因來源 repo 的 docs/.governance-log.jsonl 等簿記檔恆髒,一律擋會天天卡住;要做需先分「簿記檔 vs 實質檔」白名單

合約 1 條(改了就是破壞性變更) | 技術債 2 條(可以改)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Verification/2026-07-10_檢索排序v1' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 231ms:[0m
# Verification/2026-07-10_檢索排序v1.md
type:verification | status:pass | scope:retrieval
提醒:動這篇之前先確認下面的前提還成立(valid_under):
  欄位權重 title4.0/summary2.5/tags1.5/body1.0/type0.5;K1=1.2/B=0.75(評測可調)
  G=0.6B+0.25C+0.15J;R=0.6L+0.4G;固定席=事故+合約(有效深度內)
  全 dormant:legacy 預設輸出不變
plan_refs: [[Projects/檢索優化_計劃]]
→ 連出 (2):
  • Projects/檢索優化_計劃.md [done]
  • Systems/retrieval-ranking.md [done]
← 連入 (1):
  • Systems/retrieval-ranking.md [done]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Verification/2026-07-10_檢索排序v1'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 215ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Verification/2026-07-11_檢索goldset評測' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 219ms:[0m
# Verification/2026-07-11_檢索goldset評測.md
type:verification | status:pass | scope:retrieval
提醒:動這篇之前先確認下面的前提還成立(valid_under):
  goldset snapshot=labels 定稿於 2026-07-11(50 案例/424 候選);vault 99 節點規模;BM25F/融合參數現值
summary:
  TEST:§6 gate 4/7 過——search 面全過(修正尺 nDCG@5 +57.6%,held +104.7%,MRR .94,fusion 雙勝 ablation;活語料 ±1pp 漂移…
  KEY:雙 AI 盲標(Claude+Codex 各標 424 候選,一致 295)→ 1v2 取低 47 → 0v非0 邊緣 80 條 opus 深讀裁決、0v2 強衝突 2 條人裁
plan_refs: [[Projects/檢索優化_計劃]]
→ 連出 (2):
  • Projects/檢索優化_計劃.md [done]
  • Systems/retrieval-ranking.md [done]
← 連入 (7):
  • Projects/graph-engineering掃描2026-08-19_調研.md [doing]
  • Projects/檢索優化_計劃.md [done]
  • Projects/檢索多詞回退_計劃.md [doing]
  • Projects/節點靜態先驗_調研.md [done]
  • Systems/retrieval-ranking.md [done]
  • Verification/2026-07-11_hook面v1.1轉正.md [pass]
  • Verification/2026-08-23_雙評審三版對照.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Verification/2026-07-11_檢索goldset評測'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 226ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Verification/2026-08-24_about_code讀側四項落地' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 225ms:[0m
# Verification/2026-08-24_about_code讀側四項落地.md
type:verification | status:pass | scope:retrieval
提醒:動這篇之前先確認下面的前提還成立(valid_under):
  語料 338 篇、83 篇 about_code 存量(batch-2026-08-23)、goldset rev 483c631b7294(釘定快照 9fcb761 早於 83 篇寫入——釘定口徑下 about 不生效)
summary:
  FLAG:TECHNICAL
  KEY:about-code-impl-std 三輪達上限後人裁乙直接實作——#4 impact 讀 about_code(about_hit 只加分、事故優先、過期雜湊、總開關、巨檔門檻)/#6 d…
plan_refs: [[Projects/固定席扇出降權_計劃]]
→ 連出 (3):
  • Projects/固定席扇出降權_計劃.md [doing]
  • Systems/retrieval-ranking.md [done]
  • Verification/2026-08-23_about_code存量雙評審落地.md [pass]
← 連入 (3):
  • Projects/固定席扇出降權_計劃.md [doing]
  • Systems/retrieval-ranking.md [done]
  • Verification/2026-08-24_固定席降噪A層落地.md [pass]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos contracts 'Verification/2026-08-24_about_code讀側四項落地'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 218ms:[0m
(這篇沒有登記任何「動了會壞」的合約)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos decisions 'Projects/每支檔有家_計劃' --superseded"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos context 'Projects/每支檔有家_計劃' --brief"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[35m[3mexec[0m[0m
[1m/bin/zsh -lc "python3 scripts/lumos show 'Projects/推播miss量測_計劃'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 234ms:[0m
---
type: project
summary: |-
  KEY:GraphRAG 調研建議一(Enzo 2026-09-11 採納,單源 [[Projects/GraphRAG對節點關聯_調研]] d1)的實作——擴充既有唯讀儀器 recount.py,量「編輯時推播推了什麼、agent 之後自己讀了什麼」,重點是 miss(沒推卻被讀);lumos 不新增任何寫帳(全repo審視 F08 否決過)
  KEY:錨點是每一次編輯本身(零推播也有一列)、推播四段都認;miss 依序分規則內(問 impact 直連)/關於欄(about_code)/判不出,編輯後才新建的筆記另計;本案只交清單、不把 miss 做成評測題(題庫母體由排序自己抓,判不出的進不去),另案看 REVISIT 2026-09-17
  KEY:同一支儀器數 lumos search 零命中(建議二的量測基礎,新寫輸出配對);每週由自主迴圈週期觀測段存上一個完整週的推導列(照 run_replay 週戳慣例),查詢字串只進本機 gitignore 目錄——這改動儀器「不寫任何帳」的約定,由本計劃明裁
status: done
created: 2026-09-11
updated: 2026-09-11
tags:
  - type/project
  - status/done
  - scope/evals
related:
  - "[[Projects/GraphRAG對節點關聯_調研]]"
  - "[[Projects/主session鏡頭利用率_計劃]]"
  - "[[Systems/retrieval-ranking]]"
---
# 推播miss量測_計劃

> 白話:agent 改一支檔之前,hook 會推幾篇筆記給它。我們想知道兩件事——推的東西它有沒有用上,以及更重要的:它自己跑去讀了、但我們沒推的那些筆記。後者就是推播漏掉的東西,而且是 agent 真實行為告訴我們的,不是我們自己出的題。資料本來就在 Claude Code 的逐字稿裡,既有的量測程式也已經算出「讀了哪些」,只是把沒推的那一半丟掉了;本案把那一半留下來、分類,並每週把上一週的結果存檔,免得逐字稿被清掉。

## 緣起

- [[Projects/GraphRAG對節點關聯_調研]]:Graph RAG 的招牌手法對我們幫助有限,真正卡住的是「評測題少、而且出題判分同一個來源」。Enzo 2026-09-11 採納建議一(d1)。
- 既有儀器 [[Projects/主session鏡頭利用率_計劃]](`governance/eval/lens-utilization/recount.py`)已經從逐字稿對到每次推播與之後的讀取,但在 `scan_file` 裡把讀取跟推播清單取交集,沒推卻被讀的那一半直接丟掉;而且只解析「必看」那一段,「可能相關」「直接提到這個檔」兩段沒解析。
- 建議二(搜尋零命中時,用圖譜裡的詞共現幫查詢改寫)要先知道零命中有多少、長什麼樣,這個數也在同一支儀器順帶數(S3)。
- 那份計劃還掛著 `REVISIT:2026-09-17`(先跑歷史、Enzo 讀分佈與抽樣裁第二段)。本案的 miss 數字一起在那天交出,不另開一個回頭日。

PRIOR-ART: ①最小解層級=擴充既有唯讀腳本 recount.py(資料已在逐字稿,零新元件、不動 hook、不新增 lumos 寫帳) ②世界解過:搜尋引擎拿點擊當隱性回饋是慣用做法,「沒排上卻被點」比「排上而且被點」可信(位置偏差);本次未另查文獻,只借這個觀念 ③裁定=借用觀念、自建小段;零新依賴

## 條款

- [S1] 推播清單解析四段都認;解析不到或行數對不上的那筆記 `pushed_complete=false`,不猜 [test:t_lens_recount_parses_all_sections]
  - hook 注入全文(`scripts/hooks/claude/impact-hook.py` 的 `build_ranked_context`)現在有四段,每段行格式不同,各用自己的比對規則:
    - 「必看——這 N 篇…」(舊標頭「必看(合約/事故固定席 N):」也認):行首是標記詞,可帶 ★合約★,沿用既有 `PIN_LINE`。
    - 「可能相關的 N 篇(依關聯度排序):」:行首是分數、再接種類詞(例 `0.42 直接 Systems/a.md`、`0.31 hop2 Systems/b.md`)。
    - 「另外 N 篇分數不高但直接提到這個檔,一併列出:」:同上,種類詞可能是 `直接/basename-match`。
    - 「守衛面參考——這 N 篇是軟標記樞紐…」:同上(例 `0.20 hop1 Systems/c.md`);只有這一段、沒有必看段的注入也存在。
  - 分數行一律切成「分數、種類詞、節點路徑」三段,節點路徑取到 `.md` 為止(路徑可含空白)——既有 `PIN_LINE` 套在分數行上會把種類詞吃進路徑(r1 通才/邊界席實測)。
  - 截斷行(「(+N 條低分截斷,沒列出來)」「(另有 N 條守衛面參考未列出)」)那些節點 agent 沒看到,不算推了;記 `truncated_n`。
  - 某段實際解析到的行數少於標頭宣稱的 N,或遇到認不得的段標頭 → 那筆 `pushed_complete=false`,它的 miss 不進三類統計、另計「推播清單不完整」。整筆一起判、不只剔那一段:推播清單只要有一段沒讀全,「讀了但不在清單裡」的筆記就可能其實在沒讀到的那段,miss 下不了結論(r2 邊界席問過顆粒度)。
  - 注入裡另有兩種不是推播節點的段:棧別效能檢核題(`[<棧> 效能檢核——…]` 開頭)與多檔 patch 的「只算了前 N 檔,其餘只列名」說明——這兩種認得、跳過。其他在行首、又不是這六種標頭的段才算「認不得」(r2 外家 H9)。
  - 守衛面參考段的節點名 hook 沒有過清洗(其他三段有),節點名含換行時那一行會斷掉——照「行數對不上」處理,不另寫修補(不動 hook)。
  - **一次改多支檔(Codex 的 apply_patch 最多算 5 支)**:hook 把每支檔的注入逐塊接成一份,各塊不標是哪支檔;所以多檔呼叫要把所有區塊掃完,推播集合=所有區塊的聯集,每支檔各一列、共用這個聯集(寧可少算 miss,不誤算);「多檔 patch 只算了前 N 檔,其餘只列名」那一段點到的檔記 `impact_skipped=true`(r2 通才席)。
- [S2] miss 偵測與分類 [test:t_lens_recount_miss_classify]
  - **錨點是那次編輯本身**:逐字稿裡每一次 Edit/Write/MultiEdit(Codex 是 apply_patch)呼叫都是一列,推播清單用呼叫編號去配 hook 附件;配不到附件=這次一篇都沒推(hook 對空結果什麼都不印),推播清單為空、照樣算 miss。既有程式以附件為錨,零推播的編輯根本沒有列,最純粹的漏推反而量不到(r1 邊界席)。只有編輯工具的呼叫建列;Codex 子代理開場那種 `SubagentStart:dispatch-lens` 附件不是編輯,不建列(r2 邊界席)。
  - **只有 hook 會處理的檔才建列**:用 hook 自己的判斷函式(`scripts/hooks/claude/impact-hook.py` 的 `hook_decide_paths`)判;文件、排除路徑這些 hook 本來就不管的檔不建列,否則會被誤算成零推播(r2 外家 H1)。
  - **配對**:Claude 逐字稿用附件的 toolUseID 精確配;Codex 逐字稿的附件沒有呼叫編號,沿用既有做法(同一輪、最近的前一個 apply_patch),同一輪有兩個以上 apply_patch 就配不準——那幾列記 `pushed_complete=false`,不猜(r2 外家 H2)。
  - **被改的檔 F 先換成 repo 相對路徑**:Claude 的編輯工具給的是絕對路徑,about_code 存的是相對路徑、impact 也吃相對路徑,不換就永遠比不中;換不成相對路徑的(在 repo 與它的 worktree 之外,既有程式叫 scratch 的那類)不建列。週檔只寫相對路徑,不會把本機使用者名稱與目錄結構寫進版控(r2 通才席)。
  - **冷卻窗內沿用前一次推播**(實作時真資料發現):hook 對同一支檔真的推過(開窗)之後,冷卻窗內(`.lumos/impact.json` 的 `ttl_min`,預設 20 分)再改不重推整份、只跑事故快速路,也不延長窗;那支檔這次看得到的=開窗那次的推播 ∪ 窗內快速路推的(`cooldown_inherited`),窗外沒推才算零推播——不然看過推播的編輯會被算成零推播、灌出假漏網 [test:t_lens_recount_cooldown_and_search_forms]。窗逐檔記(hook 的冷卻記號本來就逐檔):多檔 patch 裡只有真的在窗內的檔沿用,新檔照算零推播(代碼審 r1 外家 C2);窗內那次自己也有快速路推播時照樣併上開窗那次(代碼審 r1 編排者自找)[test:t_lens_recount_code_review_r1_rows]。
  - **讀取歸給哪一次編輯**:事件先後看(行序, 同一則訊息裡第幾個工具呼叫)——同一則訊息裡先改檔再讀筆記,讀取排在那次編輯之後(代碼審 r1 單reviewer A1)。同一份逐字稿裡,第一次編輯之後的每一筆讀取只算一次——先往前找最近一次「跟這篇筆記有關」(下面的規則內或關於欄成立)的編輯,算給它;都沒有才算給前面最近的那一次編輯(那裡它會落在判不出)。既有程式的窗口一路掃到逐字稿結尾,多次編輯時同一次晚讀會被算成每一次編輯的證據(r1 邊界席);只看「最近一次」又會把讀 A 相關筆記的動作算給中間插進來的 B(r2 邊界席)。
  - **讀取怎麼認**:沿用既有高信心判法(Read 工具、單純讀動詞、`lumos context|show|contracts`),而且要讀成功才算——Read 的結果是錯誤(檔案不存在等)不算;Bash 讀取的輸出看不出成敗的照既有判法算(r2 外家 H4)。讀到的東西正規化成節點路徑:完整路徑直接用;只寫檔名或節點名的,拿現在的節點清單比對檔名,唯一才認,不唯一記 ambiguous、不算 miss。既有程式只拿檔名比對推播清單,miss 要比對整個圖譜,這段是新寫的。
  - **減掉推了的**:四段推播(不含截斷的)都算推了;窗口內讀了、推播沒有的=miss 候選;同一工作階段裡那次編輯之前就讀過的不算(既有 `pre_touched` 的分法)。
  - **分三類,依序判、先中先算**:
    1. 規則內:用現在的圖譜跑 `lumos impact --file F --json`,該筆記在 direct 或 incidents 清單(impact 會把帶事故觸發的直連節點從 direct 移到 incidents,兩個都要看——r2 外家 H6)(impact 抓直連有兩條規則:正文反引號寫到 F 的完整路徑,或裸檔名在 git 追蹤的檔裡唯一時的檔名比對;直接問 impact,不在儀器裡另寫一套)。
    2. 關於欄:該筆記開頭的 about_code 欄位含 F。欄位借 lumos 本體的開頭欄位解析讀(清單與單值 `about_code: scripts/lumos` 都認,跟 impact 讀到的同一份;單行 `[a, b]` 多拆一步)——自己寫的正規式漏了單值寫法,真圖譜有兩篇這樣寫(代碼審 r1 單reviewer A3、外家 C8)。
    3. 判不出:兩者都不中。
    - 同時中規則內與關於欄的算規則內,另記 `about_also=true`(r1 通才席實測:98 篇有 about_code 的筆記裡 15 篇同一路徑也被正文引用)。
  - **事後才有**:那篇筆記在編輯當下還不存在 → 不算 miss,另計(推播當下它不存在,推不到不是漏)。「當時存在」的證據任一成立就算存在:git 最早加入時間早於編輯(用 `git log --follow`,不加的話改過名的筆記會拿到改名那次的時間——r2 通才席),或檔案系統建立時間(macOS 的 st_birthtime)早於編輯。只看 git 會把「早就寫好、還沒提交」的筆記錯排(r2 外家 H7);只看建立時間會被重新 clone 洗成新的。兩者都晚於編輯才算事後才有。總預算用完、git 沒問到的筆記一律當存在——只剩建立時間不足以判(新 clone 會把它洗成新的,漏網會整批掉進事後才有而消失;代碼審 r1 外家 C5)。
  - 輸出:三類各自的清單(被改的檔 F、筆記、工作階段雜湊、時間)與分佈;每列另帶 `pushed`(那支檔看得到的推播節點)與 `used`(推了、之後讀了),週檔答得出「推了哪些、之後讀了哪些」(代碼審 r1 外家 C1);不出單一命中率、不設門檻(沿用既有儀器的約定,既有計劃 r1 裁「比率量到的是圖譜密度」)。
  - **本案不把 miss 變成評測題**:題庫 `governance/eval/retrieval-goldset.json` 的 edit 卷每題綁一個 commit 的改動片段,候選母體由 `governance/eval/retrieval_eval.py` 的 `edit_universe` 現場跑排序抓前 50;判不出的 miss 本來就落在排序抓不到的地方,幾乎進不了那個母體,`governance/eval/refresh_labels.py` 也只補既有題的標籤、不建新題(r1 通才/整合/架構三席)。本案只交清單;要把 miss 做成跳出同源迴圈的新題型,另立計劃。
REVISIT:2026-09-17 第一份 miss 清單出來時數判不出那一類;有 10 筆以上就立「miss 評測題」計劃(必含節點來自 agent 真實讀取、不來自排序母體),不到就等週檔累積
- [S3] 搜尋零命中(新寫的輸出配對) [test:t_lens_recount_search_zero_hits]
  - 既有程式只讀指令字串、不讀輸出;本條新寫「Bash 呼叫 → 用呼叫編號配它的輸出」這段(r1 邊界/整合席)。
  - 一次 Bash 呼叫先把反斜線續行接回(`\` 接換行是同一條指令,代碼審 r2 單reviewer D1),再逐行(換行也是殼層的指令分隔,代碼審 r1 外家 C6),再用 hook 既有的切段函式切(`;`、`&&`、`||`、`|` 都切;不另寫第二套,代碼審 r1 架構 B1;引號內的分隔字元不切),恰好一段含 `lumos search` 才判,兩段以上輸出分不開、記「判不出」;那一段後面接管線過濾(`| head -N`、`| grep`、`| tail`)照判(管線後段是另一段、不含 search)——真實逐字稿裡的 search 幾乎每筆都接 `| head`(r2 邊界席抽樣),計數那行被過濾掉了就記「判不出」。背景執行的沒有同步輸出,記「判不出」。
  - 零命中認三種現行輸出,看整段輸出裡有沒有那一行、不看最後一行怎麼結尾(兩種文字輸出那行後面都還接固定尾字,例「…想照檔名排加 --legacy)」「…[已排除 code block,--code 可含]」,r2 邊界席實跑):排序模式有一行以「(共 N 篇候選」開頭;排序模式 `--json` 讀 `candidates`;舊模式(`--legacy`,以及會自動退回舊模式的 `--regex`)有一行以「N 處 / M 篇」開頭、看篇數 M。那個數是 0 就是零命中;三種都找不到一律「判不出」,不算零命中。實作時依真資料補兩條(REVISIT 預設的「擴充認得的輸出形態」提前做):舊版計數字樣「(候選 N;…)」也認;計數行被 `| head` 切掉但看得到排名結果行 → 有命中。零命中仍只認明寫 0 的那一行。
  - 出:search 總次數、零命中次數、判不出次數、零命中的查詢字串清單(查詢字串只進本機檔,見 S4)。
- [S4] 每週留存:自主迴圈週期觀測段存上一個完整週的推導列 [test:t_lens_recount_weekly_archive]
  - **位置**:`governance/autonomous-loop.sh` 裡 run_exam/run_probe/run_nags/run_replay 那一段(派工段暫停時也照跑),新增 `run_lens_weekly`,照 `run_replay` 的慣例:獨立週戳檔 `governance/eval/lens-utilization/.weekly-stamp`、週字串用 `date +%G-W%V`(ISO 年配 ISO 週,跨年不錯號)、戳記等於本週就跳過;Python 端是 `governance/autonomous_loop/lens_weekly.py`,第一行印 JSON、`LOG:` 行給 shell 記;模組失敗沒輸出就不蓋戳、明天重試(同 `run_replay` 的 fail-open)。每日治理只是呼叫自主迴圈,不在它自己的步驟裡加(r1 架構/整合/通才三席)。
  - **週檔是「上一個完整週發生的事」,不是快照**:只收編輯時間落在上一個完整 ISO 週的列(逐字稿每行帶時間,是 UTC;一律換成本機時區再算週,跟 shell 端 `date +%G-W%V` 同一個時區,週一清晨不會被算到前一週——r2 邊界席;缺時間的行沿用同一份逐字稿前一行的時間,整份都沒有就不收、計數),寫 `governance/eval/lens-utilization/weekly/<%G-W%V>.json`;連續兩週的檔互不重疊,可以直接比趨勢(r1 邊界席)。放 `weekly/` 子目錄:跟一次性的首報分開,同 `governance/replay/<編號>/` 用子目錄收同類檔的做法。
  - **總時間預算 300 秒**(同 `governance/autonomous_loop/replay_weekly.py` 的 `BUDGET_SECONDS`):自主迴圈整支只有一把鎖,週跑佔太久會讓當天後面的排程判成「別人在跑」而整支跳過(r2 邊界席)。一把預算管整次執行(代碼審 r1 外家 C5:原本只管 impact,git 與掃逐字稿都沒上限):先掃逐字稿收事件,用完就不再開新檔、沒掃的計數 `files_unscanned`;再逐份叫 impact / git 分類,用完就不再叫,剩下的被改檔分類記「判不出」。兩種都讓週檔標 `budget_hit=true`,照常蓋戳——資料不完整但有標記。
  - **讀逐字稿**:壞行(寫到一半的尾行等)只跳那一行、其餘照讀;Codex 逐字稿版本不在認得的表整份跳過、stderr 講明(同既有 `scan_codex_file`,三處共用同一段讀檔前奏——代碼審 r1 架構 B2、外家 C3/C4);壞行數、版本跳過份數、缺時間的編輯數都進摘要。
  - 漏跑的週不自動補(逐字稿還在就手動帶 `--week <%G-W%V>` 補跑);同一週重跑覆寫同一個檔;寫法照本 repo 共用檔原子寫入(寫暫存、自驗讀得回、整個換名)。
  - **版控那份只存推導列**:工作階段代號的雜湊、被改的檔、推了哪些節點、之後讀了哪些、miss 分類、計數;不存逐字稿原文、不存查詢字串。
  - **零命中查詢字串另存本機、不進版控**:寫 `governance/eval/lens-utilization/local/<%G-W%V>-queries.json`,該目錄加進 `.gitignore`。查詢字串是 agent 當下打的自由文字,本 repo 公開,進版控就永久公開;逐字稿本身 30 天會被清,不該因為量測變成永久(r1 邊界/整合/通才三席)。
  - 這改動既有儀器「不寫任何帳」的約定:寫的是每週一份的報表檔,不是逐筆追加的帳本、不進 hook、不進 `lumos gov`。
- [S5] 載入 recount.py 的測試都先守門 [test:t_lens_recount_tests_guarded]
  - 本案新增的測試(含冷卻窗與搜尋形態那支)與三支既有測試(`t_lens_recount_classify`、`t_codex_s3_recount_codex`、`t_codex_s3_r1_fixes`,都用 SourceFileLoader 載 recount.py、都沒守門——r2 通才/邊界席)都先 `_need_src("governance/eval/lens-utilization/recount.py")`:`governance/eval/` 不會裝進消費專案,而 `scripts/test_lumos.py` 會,沒守門就在消費端假紅(同 [[Issues/vendored測試套件在消費端假紅]];r1 整合席)。
  - 守門測試:掃 `scripts/test_lumos.py` 裡提到 `lens-utilization` 的測試函式,每支都要有 `_need_src(`。
  - `scripts/test_lumos.py` 是錨點檔,改完走 `lumos anchor approve --note`。
- [S6] README 同步:recount.py 的 README 補四段解析、miss 三類與事後才有、零命中三種輸出、週跑與本機查詢檔,並寫明天花板 [manual:讀 README 對照這五塊是否都寫到]

## 邊界與不做

- 不動 impact hook、不動派工鏡頭(派工鏡頭「不擋不驗不記不量」照舊)、不改 `docs/.usage-log.jsonl`(F08)。
- 不出單一命中率、不設門檻、結果不回灌排序——排序要改,另案用 miss 當證據走設計審。
- 不把 miss 做成評測題(S2 最後一點)。
- 只量本 repo 的逐字稿(沿用既有 `cwd` 篩法);消費專案另案。

## 承認的限制(每條附回頭條件)

- **位置偏差**:agent 會讀被推的東西,「推了而且被讀」不能直接當相關;本案只把「沒推卻被讀」當證據。這是方法本身的限制、不隨時間變;事件入口=任何要拿本儀器輸出去改推播排序的計劃,它的設計審要先交代怎麼處理位置偏差(邊界與不做已寫「結果不回灌排序」)。
- **用現在的圖譜判當時的推播**:規則內 / 關於欄都拿現在的筆記內容判,編輯之後才補上 F 路徑的筆記會被算成「該推沒推」(新建的已排除,改寫的排除不了);反方向,程式檔後來改名的,舊路徑在 impact 比對不到,本該是規則內的會掉進判不出(r1 邊界席)。
REVISIT:2026-09-17 第一份 miss 清單出來時,抽規則內那一類逐筆看 git 歷史,數有幾筆是「編輯之後才寫上 F」;超過兩成就改成用編輯當時的筆記版本判
- **子代理的讀取不算給主 session 的編輯**:子代理逐字稿是另一份檔(同一個工作階段代號),本案逐份掃、不跨檔歸屬;主 session 改完檔派子代理去讀筆記的那些讀取不會出現在主 session 的窗口裡——方向是少算 miss,不是多算(r2 通才/邊界席)。子代理自己的編輯照樣是它那份檔裡的錨點。
REVISIT:2026-09-17 第一份清單出來時,數有多少次編輯之後同一個工作階段派了子代理;超過三成就改成按時間把同工作階段的子代理讀取併進來
- **零推播分不出原因**:hook 算了但沒結果、hook 沒跑(沒裝、逾時),逐字稿裡都是「沒有附件」;兩者都算零推播,零推播的 miss 單獨一欄,不跟有推播的混著比。
REVISIT:2026-09-17 看零推播的編輯占全部編輯幾成;超過三成就查 hook 是不是常逾時或沒跑
- **量不到 Bash 改檔**:impact hook 只在 Edit/Write/MultiEdit/apply_patch 觸發,用 Bash 改檔沒有推播,那段 miss 天生量不到(既有計劃記過一個 session 372 次 Bash、0 次 Edit、1 次 Write)。
REVISIT:2026-09-17 跟既有計劃同一天:看推播次數夠不夠(既有計劃門檻 20);不夠就照它的改題「Bash 改檔路徑沒有動手前鏡頭」
- **判不出那一類本案只列清單**:沒人標就不會變成評測題;回頭條件見 S2 最後一點的 REVISIT。
- **零命中判法靠輸出字樣**:search 輸出措辭一改就會數錯;測試釘住三種現行輸出(字樣一改就紅),但擋不住「判不出」比例變高而低估零命中。
REVISIT:2026-10-17 看判不出占 search 總次數幾成;超過三成就擴充認得的輸出形態,或議讓 search 各模式都印一行固定格式的結果計數

## 實務隱患

- 併發:週跑由自主迴圈的整跑鎖保護(`take_lock`),排程不會自己撞自己;人手動跑同一週會覆寫同一個檔——原子寫入,最後寫的贏,兩邊用同一批逐字稿算,不會出現半份。
- 效能(2026-09-11 實測):現在全量重算一次約 27 秒(本機 197 份主逐字稿,加子代理與 Codex 逐字稿);`lumos impact --file` 一次約 1.7 秒。只對「有 miss 候選的被改檔」各跑一次、同一次執行內快取;git 首次加入時間每篇筆記只查一次。週跑只處理上一週的編輯,子行程次數跟那一週被改的不同檔數成正比。每個子行程設 60 秒逾時,逾時那支檔的分類記「判不出」並計數(r1 通才/整合席)。
- 資源:讀逐字稿;開子行程跑 `lumos impact`(每次重載整個圖譜)與 `git log`;不開網路連線。
- 隱私:逐字稿可能含其他專案內容——只量本 repo 的工作階段(cwd 篩);版控裡只有推導列(節點名、檔名、計數),工作階段代號存雜湊;查詢字串只進本機 gitignore 目錄。
- 金流、對外送出、不可逆:不適用——不碰任何金流或外送程式,檔案可刪可重跑。

## 驗收(測試先行)

- 注入全文含四段 → 四段節點都進「推了」、分數與種類詞不混進路徑;截斷行的不算;只有守衛面參考段的注入也認;某段行數少於標頭 N → `pushed_complete=false`。
- 一次 Edit 沒配到附件 → 仍有一列、推播為空、之後讀的沒推筆記算 miss;`SubagentStart:dispatch-lens` 附件不建列;改 README 這類 hook 不管的檔不建列。
- Read 一篇不存在的筆記(結果是錯誤)→ 不算讀到;注入裡有效能檢核題段 → 不算認不得、不影響 pushed_complete;Codex 同一輪兩次 apply_patch → 那兩列 pushed_complete=false。
- 一次 apply_patch 改兩支檔、注入是兩塊接在一起 → 兩列、推播都是兩塊的聯集。
- Edit 給絕對路徑 → 列上的 F 是 repo 相對路徑、關於欄比得中;repo 之外的檔不建列;週檔裡找不到任何絕對路徑。
- 同一工作階段先改 A、再改 B,之後讀一篇跟 A 有關的筆記 → 算給 A;讀一篇跟兩者都無關的 → 算給 B、判不出。
- 讀了一篇沒推、正文反引號寫到 F 的筆記 → 規則內;about_code 含 F → 關於欄;帶事故觸發、impact 放在 incidents 的直連筆記 → 規則內;兩者都中 → 規則內且 `about_also`;都沒有 → 判不出;那次編輯之前就讀過 → 不算;筆記在編輯之後才建 → 事後才有;筆記在編輯之前建、之後改過名 → 仍算 miss,不是事後才有;筆記在編輯之前就寫好、編輯之後才提交 → 仍算 miss。
- 逐字稿裡一次零命中的排序文字輸出(那行後面接固定尾字、指令接 `| head -6`)、一次零命中的 `--json`、一次零命中的舊模式輸出、一次有命中、一次用 `&&` 串了兩個 search → 零命中 3、判不出 1、查詢字串清單含那三個查詢。
- 週跑:只收上一個完整週的編輯(台北時間週一 07:00 的編輯,UTC 還是週日,算進新的一週);超過總預算 → 週檔標 `budget_hit=true`、照常蓋戳;同週再跑覆寫同一份、不多出檔;版控那份不含逐字稿原文、不含查詢字串(抽一段原文與一個查詢字串斷言不在檔裡);模組炸掉不蓋戳。
- 載入 recount.py 的測試都有 `_need_src` 守門;既有 `t_lens_recount_classify` 全綠;`scripts/test_lumos.py` 改完 `lumos anchor approve`。

## 合約候選(設計審過閘後列,還不是合約;蓋章走 guard scaffold → bind → audit)

- 版控裡的週檔不含逐字稿原文、不含查詢字串、不含絕對路徑(改了就是把本機私人內容永久公開進公開 repo)。
- 查詢字串只寫進 gitignore 的本機目錄。
- 推播清單有任何一段沒讀全,那一列不下 miss 結論(改了就會把沒讀到的段當成「沒推」)。
- 週跑超過總預算照樣蓋戳、週檔標 `budget_hit`,不佔住自主迴圈的鎖。

## 過閘時的誠實界線

- 兩輪各自找到二十幾條(r1 31 條、r2 26 條),r2 補進去的段落本身還沒被任何席位審過;實作走測試先行,每條驗收先寫翻紅測試,代碼審再補這一層。
- 已做(2026-09-11 代碼審 r1,單reviewer 席的鏡頭含這一項):找到讀取歸屬(同一則訊息先改後讀會消失)與「當時是否存在」缺真 git 測試兩條,都已折;見審計修正紀錄。

## 實作紀錄(2026-09-11)

- 程式:`governance/eval/lens-utilization/recount.py` 加 `run_misses` 那一段(推播四段解析、編輯為錨、讀取歸屬、關聯與存在判斷、零命中配對、週檔寫出);週跑 `governance/autonomous_loop/lens_weekly.py`;自主迴圈 `run_lens_weekly`(照 `run_replay`);`.gitignore` 收 `local/`;README 補一節。
- 實作時真資料發現、改了設計的兩處(條款正文已改):①hook 冷卻窗——W36 真資料零推播 81%,原因是同一支檔冷卻窗內再改不重推;改成沿用前一次推播後,零推播 35 列、沿用 46 列 ②搜尋判不出 75%——多半是 `| head` 切掉最後的計數行、或舊版字樣;補兩種形態後降到 31%(63/201),其餘多是一次呼叫串兩個搜尋。
- 真資料冒煙(上一個完整週 W36,本機):掃 2519 份逐字稿(1 份 Codex 稿壞行跳過)、42 秒、沒碰預算;編輯 100 列、漏網 2 筆(規則內 1、判不出 1)、事後才有 2、零命中 0。見 [[Verification/2026-09-11_推播漏網量測實作]]。
- 代碼審 r1 修完重跑 W36:掃 2521 份、45 秒、沒碰預算;編輯 100 列(零推播 35、冷卻窗沿用 46)、漏網 2、事後才有 2;新看得到壞行 2 行(修前整份丟)、Codex 版本不認得跳過 13 份(修前照讀、會猜格式)。推了之後有讀 0 次——另一支不走本程式的腳本直接數,W36 有推播的逐字稿只有 1 份、裡面 Read 圖譜 0 次,兩邊一致。
- 覆蓋面的保留:上週有編輯的主 session 逐字稿只有 1 份(其餘列來自它的子代理),漏網數少主要是覆蓋面,不是偵測漏;推測原因是已移除的 worktree 不在 `git worktree list`、被 cwd 篩掉,以及部分終端機不寫逐字稿——這兩點沒逐一驗證。
REVISIT:2026-09-17 同既有計劃那天:用 W37 週檔看列數與漏網數;列數仍少就查被 cwd 篩掉的 worktree 逐字稿有多少

## 審計修正紀錄

- r1(2026-09-11,四席;外家席額度未恢復、缺席,r2 補派):31 條/blocking 20/推播解析、錨點、讀取窗口、分類順序、題庫銜接、零命中配對、週跑位置與語意、查詢字串隱私、成本全面改寫。
- r2(2026-09-11,三席:通才、邊界、外家否決 Codex gpt-5.6-sol):26 條/blocking 21/多檔 patch、路徑正規化、零命中判法、時區、總預算、hook 不管的檔、Codex 配對、讀取成敗、事故節點、當時是否存在、段標頭定義全部折入。
- 席報告與收貨紀錄:`governance/review-reports/推播miss量測/`。
- 代碼審 r1(2026-09-11,三席:單reviewer、架構對齊、外家否決 Codex gpt-5.6-sol;分級 standard):16 條/blocking 8/加編排者自找 1 條,17 條全折——讀取歸屬、真 git 存在測試、about_code 單值、共用讀檔前奏(版本閘、壞行)、冷卻窗逐檔與事故快速路、總預算管到 git 與掃描、換行切段、缺時間沿用、週檔存推了與讀了。卷證:`governance/review-reports/code-推播漏網量測/`。
- 代碼審 r2(2026-09-11,三席:單reviewer、架構對齊、資安;外家 Codex 額度用完缺席、Enzo 裁跳過):只掃 r1 修正差異,3 條/blocking 1/反斜線續行被切斷(r1 修換行分段時引進)、借模組函式命名、週跑記錄順序,全折;資安六類看過判乾淨。

[32m succeeded in 241ms:[0m
# Projects/每支檔有家_計劃.md
type:project | status:doing | created:2026-09-11 | updated:2026-09-11 | scope:node-content
→ 連出 (4):
  • Projects/固定席扇出降權_計劃.md [doing]
  • Projects/節點範圍與索引守衛_計劃.md [doing]
  • Systems/design-loop.md [done]
  • Systems/節點範圍與索引守衛.md [doing]
← 連入 (3):
  • Projects/推筆記認家_計劃.md [doing]
  • Systems/每支檔有家.md [doing]
  • Verification/2026-09-11_每支檔有家落地.md [pass]

[32m succeeded in 251ms:[0m
架構對齊席與棧別檢核題可能相反: Enzo 2026-09-09 裁:★架構對齊優先於棧別檢核題,除非那條檢核題指的是會出事的東西★(洩漏、連線池耗盡、N+1 打爆 DB、阻塞主執行緒這類)。理… → d2
Android側UI測試綁圖譜工作流_計劃: maestro 平台的 [test:] 綁定豁免 code-loop S1 的本機真跑;終審改驗「flow 存在+上次實跑留痕」,真跑硬閘留 CI/人工。改 s… → #d3
Codex完全支援_計劃: S2 不裝自訂 agent TOML:Codex 編排時審查席用 spawn_agent,審查員框架寫進派工詞,父代理以 codex exec --sandbo… → d6
design-loop重設計: canary 退出逐輪 gate,退到定期離線校準;逐輪改用錨定檢查(機械)+席間對照(觀測) → d4
guard殺傷力驗證_計劃: 四態判定(killed/survived/timeout/error)+baseline 前置,error 不得記 killed → r1 審計折入:改六值 verdict(killed/timed_out歸killed類/survived/drifted/abort/error),timeout 歸 killed 對齊 PIT/cargo-mutants(變異致掛=被超時接住);原『獨立 timeout 類別』引用與 PIT 實際語意相反
impact鏡頭機械化_計劃: Enzo 2026-08-29 裁:只做 S1(impact manifest 進派工必附材料,經 loop next 吐 impact_cmd + dispa… → 2026-08-29 Enzo 裁停案(見 d2):d1 描述的 v1 方案(loop next 吐 impact_cmd + materials + seat-check 自動涵蓋)在 r1 五席審中三個 blocker 全數命中而作廢;改寫的 v2 在 r2 再被七個 blocker 擋下。本案不做,d1 的方案內容與「走完整設計審」的理由(unreported 指標斷層)均已不適用
impact鏡頭機械化_計劃: ★停案不做(Enzo 2026-08-29 裁)★:impact 鏡頭的工具層機械化不做,2026-08-02 [[Projects/送審前impact鏡頭機械… → ★2026-09-03 實測推翻死因,重開條件已滿足(見 [[Verification/2026-09-03_派工攔截點實測]])★:d2 的核心死因「派工發生在編排者的 agent 呼叫裡,沒有任何 hook 攔得到」為假。實測(Claude Code 2.1.259):Claude Code 的 PreToolUse hook 匹配得到派子代理(tool_name=Agent)、tool_input 帶派工詞全文、回 permissionDecision:deny 該次派工完全不執行且理由原文回饋給模型,對照組不誤擋。d2 自己寫的重開條件是「先答出派工那一刻的機械強制點在哪——兩輪十席次沒有一席找得到」,現已答出。★十席次會漏是因為都在審「lumos 這支 CLI 能不能攔」(那結論沒錯),沒往上一層看宿主平台。★注意:本次只推翻結構性死因,d2 引用的 2026-08-02 獨立裁定(擋 high 抓不到 standard、擋 standard 逼人繞過)未被推翻,重開後仍要正面回答;且同日另有實測顯示守衛誤擋會訓練人繞過(見 [[Issues/推新分支時風險分級拿空樹當起點]]),誤擋率是首要設計約束。結論綁版本 2.1.259,動工前先重跑 governance/eval/hook-intercept/ 的步驟
pitfalls棧別效能追問_計劃: standard 不擋:棧別檢核答案只落 pass --note 建議、工具不驗 → [[Projects/棧別提問表態閘_計劃]]
probe輪退場_計劃: Enzo 裁甲(2026-08-25,r1 攤牌後):多席 code-loop(含 high)收斂閘統一走處置閘(d5 型記帳:各席留痕+一輪一筆彙總 carr… → d3
條款綁測試算進度_計劃: 處置閘加第五步:計劃有 [SN] 而某條沒 [test:]/[manual:] 不得 PASS;只對首筆帳 2026-09-08 起的迴圈;凍結/回放不重讀活檔… → d4
標註刷新_計劃: 指標語意不改(未標仍=噪音),靠 delta 補標消滅未標而非改尺(bpref/只算已判等改尺方案拒) → 2026-08-26 Enzo 裁翻案(詳 Projects/評測尺翻案_計劃 d1):condensed 主尺+coverage 三層+切換點 repin 恆等零重錨——「history 失效」疑慮由恆等切換正面解掉
每支檔有家_計劃: 改到提交前就沒有家的舊檔只提醒、不擋;擋的只有新增的檔沒家、以及這次讓原本有家的檔變沒家 → d4:有寫回時改到的檔都要先有家(設計審 r1)
設計審收斂重定義_計劃: d5(Enzo 2026-08-25 裁):K=2 不適用散文審計收斂——散文設計審回歸處置閘為正閘(單輪、每發現折或附理由接受;同輪有 blocker 整輪不… → d2
進度從提交推導_計劃: 用 git trailer 承載工作項識別碼,不自建格式、不建任務狀態檔 → d7
進度從提交推導_計劃: 本案明說只蓋四分之三:沒有程式碼可掛的工作(skill 散文/圖譜回填/真機驗收)不假裝算得出來 → d8
進度從提交推導_計劃: 識別碼沿用既有 [SN] 條款標記,定址比照決策寫成 <計劃節點rel>#S1 → d7
進度從提交推導_計劃: trailer 鍵名用 Lumos-Task: → d7
進度從提交推導_計劃: 「綠」的來源用 CI 那筆,不用 code-loop pass → d7
進度從提交推導_計劃: v2 核心:不推論「完成」,只報告「這個任務宣告的證據現在是什麼狀態」——對計劃宣告的測試名當場在工作樹上跑,回報「不存在/存在但紅/存在且綠」 → d8
進度從提交推導_計劃: v3 核心:由 runtime 記、不由 agent 宣稱、也不借別的東西的語意——改檔工具跑完由 PostToolUse hook 往只增不改的帳追加{ses… → d10
autonomous-iteration-loop: 暫停每日自主 loop(launchctl disable com.enzo.lumos.daily-governance;plist 保留) → 2026-07-11 使用者裁示重啟(launchctl enable+bootstrap 已執行,每日 09:30);重啟時點的安全網比暫停時厚:panel near-perfect 閘/跨家族否決席/guard kill/落成核對均已上線
pitfalls-code-loop: 安全缺陷型審查鏡頭★刻意排除★(Enzo 2026-08-27 D2 裁):類軸只留代碼形態(併發/效能/資源),不加對抗性安全鏡頭。理由=單人私有 repo、… → d6

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba governance/eval/retrieval_eval.py | sed -n '1,180p'
nl -ba governance/eval/retrieval_eval.py | sed -n '400,570p'
nl -ba governance/eval/retrieval_eval.py | sed -n '680,790p'
rg -n \"live_vault|snapshot|DEFAULT|PINNED|git worktree|git archive|LUMOS_EVAL\" governance/eval/retrieval_eval.py governance/eval/retrieval-goldset.json | head -n 200"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
     1	#!/usr/bin/env python3
     2	"""檢索評測器(治理面,非 lumos 子命令)。spec:Projects/檢索優化_計劃 §6。
     3	零依賴 stdlib。跑法:
     4	  python3 governance/eval/retrieval_eval.py --auto      # cochange proxy 自動金標(related 面,免人工)
     5	  python3 governance/eval/retrieval_eval.py --goldset governance/eval/retrieval-goldset.json [--split held]
     6	指標:nDCG@k / MRR / P@k / Recall@k。逐輪 append retrieval-eval-history.jsonl。
     7	"""
     8	import json, math, subprocess, sys, os, argparse, hashlib, datetime
     9	from pathlib import Path
    10	
    11	_SELF_ROOT = Path(__file__).resolve().parents[2]
    12	# LUMOS_EVAL_ROOT:測試/跨庫導向目標 repo(worktree 釘定的 git 根);預設=本體 repo
    13	ROOT = Path(os.environ.get("LUMOS_EVAL_ROOT") or _SELF_ROOT)
    14	# 目標 repo 有 vendored scripts/lumos 就用它,否則回退本體版本(與 refresh_labels._setup 同語意)
    15	LUMOS = (ROOT / "scripts" / "lumos") if (ROOT / "scripts" / "lumos").exists() \
    16	    else _SELF_ROOT / "scripts" / "lumos"
    17	_VENV = os.environ.get("LUMOS_EVAL_VAULT")
    18	VAULT = Path(_VENV) if _VENV else next((ROOT / "docs").glob("*-knowledge"), None)
    19	SNAP_ROOT = None   # 語料快照 worktree 根(釘定時設);impact 走 --repo,不理 --vault
    20	
    21	
    22	def _lum(*args):
    23	    r = subprocess.run([sys.executable, str(LUMOS), "--vault", str(VAULT), *args],
    24	                       capture_output=True, text=True)
    25	    try:
    26	        return json.loads(r.stdout.strip().splitlines()[-1])
    27	    except (ValueError, IndexError):
    28	        return {}
    29	
    30	
    31	def dcg(rels):
    32	    return sum(r / math.log2(i + 2) for i, r in enumerate(rels))
    33	
    34	
    35	def ndcg_at_k(ranked_labels, k, all_rels=None):
    36	    """all_rels=該案例完整金標 label 清單(IDCG 基準)。省略時退回取回集自證——
    37	    僅限「各系統共用同一候選集」的相對比較(edit ablation);跨系統絕對比較必傳,
    38	    否則漏檢索零懲罰、兩系統不在同一把尺(r1 panel s4 major)。"""
    39	    ideal = sorted(all_rels if all_rels is not None else ranked_labels, reverse=True)
    40	    idcg = dcg(ideal[:k])
    41	    return dcg(ranked_labels[:k]) / idcg if idcg > 0 else 0.0
    42	
    43	
    44	def mrr(ranked_labels):
    45	    for i, r in enumerate(ranked_labels):
    46	        if r >= 1:
    47	            return 1.0 / (i + 1)
    48	    return 0.0
    49	
    50	
    51	def precision_at_k(ranked_labels, k):
    52	    top = ranked_labels[:k]
    53	    return sum(1 for r in top if r >= 1) / len(top) if top else 0.0
    54	
    55	
    56	def cochange_goldset():
    57	    """cochange 規則→related 金標(免人工):兩端皆 knowledge 節點的高 conf 對。"""
    58	    rules = _lum("cochange", "rules", "--json").get("rules", [])
    59	    gold = {}
    60	    kg = f"docs/{VAULT.name}/"
    61	    for r in rules:
    62	        a, b = r["lhs"], r["rhs"]
    63	        if a.startswith(kg) and b.startswith(kg):
    64	            seed = a[len(kg):]
    65	            tgt = b[len(kg):]
    66	            gold.setdefault(seed, {})[tgt] = 2 if r["confidence"] >= 0.9 else 1
    67	    return gold
    68	
    69	
    70	def eval_related(gold, k=8):
    71	    """對每個 seed 節點跑 context --recommend,用金標算指標。"""
    72	    rows = []
    73	    for seed, rel_map in gold.items():
    74	        recos = _lum("context", f"Systems/{Path(seed).stem}", "--recommend",
    75	                     "--top", str(k), "--json").get("recommend", [])
    76	        if not recos:
    77	            recos = _lum("context", seed.replace(".md", ""), "--recommend",
    78	                         "--top", str(k), "--json").get("recommend", [])
    79	        labels = [rel_map.get(Path(x["node"]).name, rel_map.get(x["node"], 0)) for x in recos]
    80	        if not labels and not recos:
    81	            continue
    82	        rows.append({"seed": seed, "ndcg": ndcg_at_k(labels, k),
    83	                     "mrr": mrr(labels), "p": precision_at_k(labels, k),
    84	                     "n_gold": len(rel_map), "n_reco": len(recos)})
    85	    return rows
    86	
    87	
    88	def recall_at_k(ranked_labels, n_relevant, k):
    89	    if n_relevant <= 0:
    90	        return None
    91	    return sum(1 for r in ranked_labels[:k] if r >= 1) / n_relevant
    92	
    93	
    94	def _lum_lines(*args):
    95	    r = subprocess.run([sys.executable, str(LUMOS), "--vault", str(VAULT), *args],
    96	                       capture_output=True, text=True, cwd=ROOT)
    97	    return [l for l in r.stdout.splitlines() if l.strip()]
    98	
    99	
   100	def _labels_of(gs, cid):
   101	    """{node: int_final}——★只含已判節點★(final=None 的未標節點不進字典;評測尺翻案 [S1]②)。
   102	    舊尺呼叫端用 lab.get(n, 0) 讀=未標照舊當 0(行為不變);condensed 引擎用「n in lab」
   103	    當剔除判準——與 collect_unjudged 的「not in lab or final is None」同一件事的兩面,
   104	    未標判定的權威仍是 collect_unjudged(禁另寫第三套)。"""
   105	    out = {}
   106	    for node, v in gs["labels"].get(cid, {}).items():
   107	        f = v.get("final")
   108	        if f is not None:
   109	            out[node] = int(f)
   110	    return out
   111	
   112	
   113	# ── 標註刷新共用原語(S0 評測母體;delta/repin/unjudged-rate 三處同源單點)──
   114	
   115	def _search_arms(q):
   116	    """search 題兩臂(與 eval_search 同一組呼叫;--no-any 紀律同該處註解)。"""
   117	    legacy = [l.split(" (")[0] for l in _lum_lines("search", q, "--no-any", "--legacy", "--files-only")
   118	              if l.split(" (")[0].endswith(".md") and "/" in l]
   119	    ranked = [x["node"] for x in
   120	              _lum("search", q, "--no-any", "--ranked", "--top", "10", "--json").get("results", [])]
   121	    return legacy, ranked
   122	
   123	
   124	def edit_universe(case):
   125	    """edit 題候選撈取=impact --top 50 原始 results(含 pinned 欄,固定席不受名額限制)。
   126	    file 不存在(相對快照/現況語料)→ None=skip:file-gone(★S0 刻意行為變更,非重構等價:
   127	    舊碼靠 impact 反查不需檔案在磁碟,本版明確短路——code-r1 整合席記錄★);輸出不可解 → None。"""
   128	    base = SNAP_ROOT or ROOT
   129	    if not (Path(base) / case["file"]).exists():
   130	        return None
   131	    payload = json.dumps({"query": case.get("delta", ""), "prospective": {}})
   132	    r = subprocess.run([sys.executable, str(LUMOS),
   133	                        "impact", "--file", case["file"],
   134	                        "--repo", os.environ.get("LUMOS_EVAL_REPO") or str(SNAP_ROOT or ROOT),
   135	                        "--ranked", "--top", os.environ.get("LUMOS_EVAL_IMPACT_TOP", "50"),
   136	                        "--stdin-payload", "--json"],
   137	                       capture_output=True, text=True, input=payload, cwd=ROOT)
   138	    try:
   139	        d = json.loads(r.stdout.strip().splitlines()[-1])
   140	        # pin-denoise-a-v4:lane 是獨立頂層鍵——合併進候選清單(lane 項保留 "lane" 欄位標記),
   141	        # 下游一律用明文鍵過濾(split_buckets),不靠 pinned 二分
   142	        return d.get("results", []) + d.get("lane", [])
   143	    except (ValueError, IndexError):
   144	        return None
   145	
   146	
   147	# 計分觸及邊界(落地後發現 2026-08-18):全母體口徑實測連原快照都 54% 未標
   148	# (399/738;金標只批過出卷小池)→ repin 永不可過。未標判定收斂到「未標了會
   149	# 實際影響分數」的位置:search=兩臂各前 10(nDCG@5/MRR/R@10 觸及帶+餘裕)、
   150	# edit=free 前 k(P@top_k/nDCG 觸及)+全部固定席(pin_noise=事故指標,不受名額限制)。
   151	SEARCH_TOUCH = 10
   152	
   153	
   154	def _touched_search(legacy, ranked):
   155	    """search 題計分觸及集=兩臂各前 SEARCH_TOUCH,保序去重。"""
   156	    seen, out = set(), []
   157	    for n in legacy[:SEARCH_TOUCH] + ranked[:SEARCH_TOUCH]:
   158	        if n not in seen:
   159	            seen.add(n)
   160	            out.append(n)
   161	    return out
   162	
   163	
   164	def split_buckets(res):
   165	    """★三桶分流的唯一實作★(pin-denoise-a-v4 arch:同檔兩種 free 定義=接手的人要猜):
   166	    pins=pinned 真值;lane=帶 lane 欄位(參考道,不進 P@8 計分、視同 pins 納入未標檢查);
   167	    free=其餘(★含 rescued——它進 P@8 母體是 2026-08-07 具名護欄「誠實計噪」的刻意設計,勿排★)。"""
   168	    pins = [x for x in res if x.get("pinned")]
   169	    lane = [x for x in res if not x.get("pinned") and x.get("lane")]
   170	    free = [x for x in res if not x.get("pinned") and not x.get("lane")]
   171	    return pins, free, lane
   172	
   173	
   174	def _touched_edit(res, k=8):
   175	    """edit 題計分觸及集=free 前 k+全部 pins+全部 lane(lane 視同 pins:人看得到就要標過)。"""
   176	    _p, _f, _l = split_buckets(res)
   177	    free = [x["node"] for x in _f]
   178	    pins = [x["node"] for x in _p] + [x["node"] for x in _l]
   179	    seen, out = set(), []
   180	    for n in free[:k] + pins:
   400	
   401	def _condense(window_nodes, lab, k, thr=None):
   402	    """window_nodes=觸及集窗內的節點序;回 (judged_labels, cov, valid)。
   403	    題級門檻([S2]①):窗內已判數 < ceil(k/2)——★k=配置窗寬(search 10/edit 8),
   404	    不是窗實際長度★(code-r1 s1-f3:候選天生偏少時用窗長會把門檻偷偷放鬆,
   405	    2 篇全判被當有效;spec 語意=分數要站得住至少要半個配置窗的已判量)。
   406	    cov=已判/窗實際長度(曝險口徑,顯示與面聚合用);thr 可覆寫(測試隔離引擎用)。"""
   407	    import math
   408	    judged = [lab[n] for n in window_nodes if n in lab]
   409	    denom = len(window_nodes)
   410	    cov = round(len(judged) / denom, 4) if denom else None
   411	    need = thr if thr is not None else math.ceil(k / 2) if k else 1
   412	    return judged, cov, (denom > 0 and len(judged) >= need)
   413	
   414	
   415	def _graph_score(r):
   416	    if r.get("kind") == "direct":
   417	        return 1.0
   418	    return 0.60 * min(1.0, 2.0 / (2 ** r.get("hop", 2)))
   419	
   420	
   421	def eval_edit(gs, split=None, k=8):
   422	    """edit/hook 面:impact --ranked。P@top_k/nDCG@top_k(非固定席);
   423	    ablation=同候選集重排(fusion=score/BM25-only=L/graph-only=結構分)。
   424	    固定席另計(安全機保,不算噪音);label2 固定席 recall 檢核。"""
   425	    rows = []
   426	    for case in gs["edit"]:
   427	        if split and case["split"] != split:
   428	            continue
   429	        cid = case["id"]
   430	        lab = _labels_of(gs, cid)
   431	        if not lab or not any(v >= 1 for v in lab.values()):
   432	            continue
   433	        # impact 自行從 --repo 解析 vault(不吃全域 --vault)→ 快照釘定須走 --repo(r1 終審親驗)
   434	        # 呼叫收斂進 edit_universe(與評測母體同源,標註刷新 T2);None=file-gone/不可解,照舊跳。
   435	        res = edit_universe(case)
   436	        if res is None:
   437	            continue
   438	        pins, free, lane_items = split_buckets(res)   # v4:free 不含 lane(P@8 母體);out_nodes 含 lane(下方讀完整 res)
   439	        row = {"id": cid, "split": case["split"], "n_free": len(free), "n_pin": len(pins)}
   440	        # edit 面 nDCG 沿用候選集自證 IDCG:三排序共用同一 free 集,相對比較有效;
   441	        # 絕對值偏高(漏檢不罰),不得跨面引用(r1 panel s4)。
   442	        orders = {
   443	            "fusion": sorted(free, key=lambda x: (-x["score"], x["node"])),
   444	            "bm25": sorted(free, key=lambda x: (-x.get("L", 0.0), x["node"])),
   445	            "graph": sorted(free, key=lambda x: (-_graph_score(x), x["node"])),
   446	        }
   447	
   448	        n_rel_free = sum(1 for x in free if lab.get(x["node"], 0) >= 1)
   449	        for name, order in orders.items():
   450	            labels = [lab.get(x["node"], 0) for x in order]
   451	            kk = min(k, len(labels)) or 1
   452	            row[f"{name}_p"] = round(precision_at_k(labels, kk), 4) if labels else None
   453	            row[f"{name}_ndcg"] = round(ndcg_at_k(labels, k), 4) if labels else None
   454	            # condensed([S1]):窗=free 前 k(與 _touched_edit 同界)
   455	            _win = [x["node"] for x in order[:k]]
   456	            _judged, _cov, _valid = _condense(_win, lab, k)
   457	            row[f"{name}_cov"] = _cov
   458	            if _valid and _judged:
   459	                _kk = min(k, len(_judged))
   460	                row[f"c_{name}_p"] = round(precision_at_k(_judged, _kk), 4)
   461	                row[f"c_{name}_ndcg"] = round(ndcg_at_k(_judged, k), 4)
   462	            else:
   463	                row[f"c_{name}_p"] = row[f"c_{name}_ndcg"] = None
   464	        row["n_rel_free"] = n_rel_free
   465	        # must-see 兩指標分開記(r1 panel codex blocker:混稱=證據失真):
   466	        # in_out=出現在輸出(含自由席,top-k 聚合下可能被截) / pinned=真固定席(唯一機械保證)
   467	        out_nodes = {x["node"] for x in res}
   468	        pin_nodes = {x["node"] for x in pins}
   469	        must = [n for n, v in lab.items() if v == 2]
   470	        row["must_total"] = len(must)
   471	        row["must_in_out"] = sum(1 for n in must if n in out_nodes)
   472	        row["must_pinned"] = sum(1 for n in must if n in pin_nodes)
   473	        # 顯式三態([S1]④/[S3b]):未判 or 判0 → 噪音——不依賴 lab.get 殘影,
   474	        # 語意=固定席理應被判過,沒判過就該進補標(condensed 不適用於此,刻意分家)
   475	        row["pin_noise"] = sum(1 for x in pins
   476	                               if x["node"] not in lab or lab[x["node"]] == 0)
   477	        row["out_top3_must"] = output_top3_must(res, lab)   # #10 乙案:輸出前 3 名必看命中率(res=人看到的順序)
   478	        rows.append(row)
   479	    return rows
   480	
   481	
   482	def _pctl(vals, p):
   483	    if not vals:
   484	        return None
   485	    s = sorted(vals)
   486	    return s[min(len(s) - 1, int(round(p * (len(s) - 1))))]
   487	
   488	
   489	def report_goldset(gs, split=None, k_search=5, k_edit=8):
   490	    tag = split or "all"
   491	    _n_s = sum(1 for c in gs["search"] if not split or c["split"] == split)
   492	    _n_e = sum(1 for c in gs["edit"] if not split or c["split"] == split)
   493	    _tag_plain = {"train": "調參用的那一半(train)", "held": "沒見過的那一半(held,防背題)", "all": "全部題目"}.get(tag, tag)
   494	    print(f"=== 考卷:{_tag_plain}——{_n_s} 題搜尋、{_n_e} 題改程式 ===")
   495	    srows = eval_search(gs, split, k=k_search)
   496	    verdict = {}
   497	    if srows:
   498	        ln, rn = _macro(srows, "legacy_ndcg"), _macro(srows, "ranked_ndcg")
   499	        lm, rm = _macro(srows, "legacy_mrr"), _macro(srows, "ranked_mrr")
   500	        lr, rr = _macro(srows, "legacy_r10"), _macro(srows, "ranked_r10")
   501	        lift = (rn - ln) / ln * 100 if ln else 0.0   # ln=0 → fail-closed(不給 inf 免費過 gate)
   502	        print(f"搜尋(打一句話找筆記,{len(srows)} 題有答案):")
   503	        print(f"  前 {k_search} 名的品質 {rn}(舊排序 {ln}),{'好了' if lift >= 0 else '★退了★'} {abs(lift):.1f}%    ← 這是主要的尺(nDCG@{k_search})")
   504	        print(f"  第一個對的答案多靠前:{rm}(舊 {lm};1.0=都在第一名)  |  前 10 名撈到該撈的比例:{rr}(舊 {lr})")
   505	        verdict["search_lift_pct"] = round(lift, 1)
   506	        verdict["search_gate"] = _search_gate_ok(lift, ln)
   507	        verdict["_rn_raw"], verdict["_ln_raw"] = rn, ln   # 恆等斷言配對用([S3]①)
   508	        # ── 新尺預覽(condensed;[S3]② gate 恆以舊尺拍板,這裡只算只印)──
   509	        c_ln, c_rn = _macro(srows, "c_legacy_ndcg"), _macro(srows, "c_ranked_ndcg")
   510	        c_valid = sum(1 for r in srows if r.get("c_ranked_ndcg") is not None)
   511	        s_cov = _macro(srows, "ranked_cov")
   512	        if c_ln is not None and c_rn is not None and c_ln > 0:
   513	            c_lift = round((c_rn - c_ln) / c_ln * 100, 1)
   514	        else:
   515	            c_lift = None   # [S2]③ 無資料判定,不拋例外
   516	        verdict["condensed_search"] = {
   517	            "ndcg": c_rn, "ndcg_legacy": c_ln, "lift_pct": c_lift,
   518	            "mrr10": _macro(srows, "c_ranked_mrr"), "r10": _macro(srows, "c_ranked_r10"),
   519	            "cov": s_cov, "valid_n": c_valid, "total_n": len(srows),
   520	            "weak": c_valid < (len(srows) + 1) // 2}   # 面別有效題數 < 半數 → 弱證據
   521	        print(f"  新尺預覽(已判子集內計分):品質 {c_rn if c_rn is not None else '無資料'}(舊排序 {c_ln if c_ln is not None else '無資料'}"
   522	              f",提升 {c_lift if c_lift is not None else '無資料'}%)|search 面覆蓋率 {s_cov}、有效 {c_valid}/{len(srows)} 題"
   523	              + ("  ⚠ 有效題數不足半數=弱證據" if verdict["condensed_search"]["weak"] else ""))
   524	    erows = eval_edit(gs, split, k=k_edit)
   525	    # A/B 逐題對帳(hook必看召回修復 r2 折入):history 只存 rounded 比例,+1 筆判定
   526	    # 需整數逐題 rows——env 指定路徑時把 erows 落 JSON,兩臂各 dump 一份對帳。
   527	    _dump = os.environ.get("LUMOS_EVAL_DUMP_ROWS")
   528	    if _dump:
   529	        # 恆覆寫(code-loop 外家審修):erows 空時寫 [],否則上一輪殘檔會被當本臂證據
   530	        with open(_dump, "w", encoding="utf-8") as f:
   531	            json.dump({"split": split, "k_edit": k_edit, "edit_rows": erows},
   532	                      f, ensure_ascii=False)
   533	    if erows:
   534	        fp, fn = _macro(erows, "fusion_p"), _macro(erows, "fusion_ndcg")
   535	        bp, bn = _macro(erows, "bm25_p"), _macro(erows, "bm25_ndcg")
   536	        gp, gn = _macro(erows, "graph_p"), _macro(erows, "graph_ndcg")
   537	        print(f"改程式時的推薦(給一支檔,推該看的筆記,{len(erows)} 題有答案):")
   538	        _pct = lambda x: f"{x*100:.0f}%" if x is not None else "無資料"
   539	        print(f"  前 {k_edit} 名裡對的比例 {_pct(fp)}    ← 主要的尺(P@{k_edit});只比文字 {_pct(bp)}、只比圖結構 {_pct(gp)}——綜合要贏這兩個才算有用")
   540	        print(f"  對的有沒有排前面(nDCG@{k_edit}):{fn}(只比文字 {bn}、只比圖 {gn})")
   541	        pt3 = _macro(erows, "out_top3_must")
   542	        print(f"  輸出前 3 名是必看的比率:{pt3}    ← 人打開 hook 先看到的三行準不準;只看不閘(歸因用 LUMOS_IMPACT_ABOUT=0 對照)")
   543	
   544	        frees = [r["n_free"] for r in erows]
   545	        med, p95 = _pctl(frees, 0.5), _pctl(frees, 0.95)
   546	        must_t = sum(r["must_total"] for r in erows)
   547	        must_hit = sum(r["must_in_out"] for r in erows)
   548	        must_pin = sum(r["must_pinned"] for r in erows)
   549	        pin_noise = sum(r["pin_noise"] for r in erows)
   550	        print(f"  推薦量:每題通常推 {med} 篇、最多的題推 {p95} 篇(關卡用全部題目算:一般題 ≤{k_edit}、最多的題 ≤{k_edit + 2})")
   551	        print(f"  必看的筆記:{must_t} 篇裡 {must_hit} 篇有推出來;其中 {must_pin} 篇是靠合約/事故硬保的固定席,其餘靠排序、沒有保底")
   552	        print(f"  固定席裡不相干的筆記:{pin_noise} 條    ← 噪音,越少越好(目前只印不閘)")
   553	        verdict["hook_p"] = fp
   554	        verdict["free_median"] = med
   555	        verdict["free_p95"] = p95
   556	        verdict["hook_p_gate"] = _hook_gate_ok(fp)
   557	        verdict["hook_p"] = fp
   558	        # ── 新尺預覽(edit 面)──
   559	        c_fp, c_fn = _macro(erows, "c_fusion_p"), _macro(erows, "c_fusion_ndcg")
   560	        c_bp, c_gp = _macro(erows, "c_bm25_p"), _macro(erows, "c_graph_p")
   561	        e_valid = sum(1 for r in erows if r.get("c_fusion_p") is not None)
   562	        e_cov = _macro(erows, "fusion_cov")
   563	        verdict["condensed_edit"] = {
   564	            "p": c_fp, "ndcg": c_fn, "bm25_p": c_bp, "graph_p": c_gp,
   565	            "bm25_ndcg": _macro(erows, "c_bm25_ndcg"), "graph_ndcg": _macro(erows, "c_graph_ndcg"),
   566	            "cov": e_cov, "valid_n": e_valid, "total_n": len(erows),
   567	            "weak": e_valid < (len(erows) + 1) // 2}
   568	        print(f"  新尺預覽(已判子集內前 {k_edit}):對的比例 {_pct(c_fp)}(只比文字 {_pct(c_bp)}、只比圖 {_pct(c_gp)})"
   569	              f"|edit 面覆蓋率 {e_cov}、有效 {e_valid}/{len(erows)} 題"
   570	              + ("  ⚠ 有效題數不足半數=弱證據" if verdict["condensed_edit"]["weak"] else ""))
   680	    return {"mode": "goldset-transition" if getattr(args, "snapshot", None) else "goldset",
   681	            "ts": datetime.date.today().isoformat(),
   682	            "goldset_rev": getattr(args, "_goldset_rev", None),   # 這把尺的版本,比較只在同 rev 內做
   683	            "eval_head": head, "goldset_snapshot": pinned_sha,
   684	            "knobs": knobs or "frozen-defaults",
   685	            "vault_note": "活語料:節點增修致數字 ±1pp 漂移;重現=checkout eval_head 重跑",
   686	            "k": args.k, "gates": gates, "pass": ok,
   687	            "unjudged_count": (unj or {}).get("count"),
   688	            "unjudged_rate": (unj or {}).get("rate"),
   689	            **({"metric_rev": getattr(args, "_metric_rev")} if getattr(args, "_metric_rev", None) else {}),
   690	            **({"metric_switch_verified": True} if getattr(args, "_metric_switch_now", False) else {}),
   691	            "condensed_preview": {r["split"]: {"search": r["verdict"].get("condensed_search"),
   692	                                               "edit": r["verdict"].get("condensed_edit")}
   693	                                  for r in reports},   # [S3]② 巢狀預覽:一輪一筆不破
   694	            "verdicts": {r["split"]: {k: v for k, v in r["verdict"].items()
   695	                                      if not k.startswith("_") and not k.startswith("condensed_")}
   696	                         for r in reports}}
   697	
   698	
   699	def main():
   700	    global VAULT, SNAP_ROOT
   701	    ap = argparse.ArgumentParser()
   702	    ap.add_argument("--auto", action="store_true", help="cochange proxy 自動金標(related 面)")
   703	    ap.add_argument("--goldset", help="人工標註 goldset.json 路徑")
   704	    ap.add_argument("--split", choices=["train", "held"], help="只跑該切分")
   705	    ap.add_argument("--live-vault", action="store_true", help="用現況 vault(預設釘 goldset snapshot;探索/漂移觀測用)")
   706	    ap.add_argument("--snapshot", help="覆寫釘定 sha(過渡雙跑的舊快照輪;該輪 mode=goldset-transition)")
   707	    ap.add_argument("--ablation", action="store_true",
   708	                    help="消融模式(比較改動前後用):★有任何未標候選就擋下、rc 3★。"
   709	                         "不帶這旗標維持原行為(只印警告不擋)")
   710	    ap.add_argument("-k", type=int, default=8)
   711	    args = ap.parse_args()
   712	    if VAULT is None:
   713	        print("ERROR: 找不到 vault", file=sys.stderr); return 2
   714	    if args.auto:
   715	        gold = cochange_goldset()
   716	        rows = eval_related(gold, k=args.k)
   717	        if not rows:
   718	            print("(cochange proxy 金標為空——knowledge git 史太稀薄,退回人工 goldset)")
   719	            return 0
   720	        agg = {m: round(sum(r[m] for r in rows) / len(rows), 4) for m in ("ndcg", "mrr", "p")}
   721	        print(f"cochange-proxy related 評測(n={len(rows)} seeds, k={args.k}):")
   722	        print(f"  nDCG@{args.k}={agg['ndcg']}  MRR={agg['mrr']}  P@{args.k}={agg['p']}")
   723	        hist = Path(__file__).parent / "retrieval-eval-history.jsonl"
   724	        with open(hist, "a", encoding="utf-8") as fh:
   725	            fh.write(json.dumps({"mode": "auto-cochange", "k": args.k, "n": len(rows),
   726	                                 **agg}, ensure_ascii=False) + "\n")
   727	        return 0
   728	    if args.goldset:
   729	        try:
   730	            gs = json.loads(Path(args.goldset).read_text(encoding="utf-8"))
   731	            gs["labels"]; gs["search"]; gs["edit"]
   732	        except (OSError, ValueError, KeyError, TypeError) as e:
   733	            print(f"ERROR: goldset 讀取/結構失敗: {e}", file=sys.stderr)
   734	            return 2
   735	        # 語料快照釘定(r1 終審折入,可重現性正解):labels 對應出題當下的 vault——
   736	        # 之後新增的未標節點若進候選池一律計噪音,gate 會被「寫文件」這種無關演進打翻。
   737	        # 預設把評測 vault 釘在 goldset.snapshot_commit 的 worktree;--live-vault 才用現況(探索用)。
   738	        _snap = args.snapshot or gs.get("snapshot_commit")
   739	        # ★goldset_snapshot 帳面語意=「這輪實際用的語料」★:只有真的釘定成功才記 sha;
   740	        # --live-vault/LUMOS_EVAL_VAULT 繞過釘定=用現況語料,帳面必須記 None(code-r1 bug 席 F2)。
   741	        _pinned = None
   742	        if _snap and not args.live_vault and not os.environ.get("LUMOS_EVAL_VAULT"):
   743	            if pin_snapshot(_snap):
   744	                _pinned = _snap
   745	                print(f"(語料釘定 snapshot={_snap};--live-vault 可用現況)")
   746	            else:
   747	                print("(釘定失敗,退回現況 vault)", file=sys.stderr)
   748	        unl = sum(1 for c in gs["labels"].values() for v in c.values() if v.get("final") is None)
   749	        if unl:
   750	            print(f"⚠ 尚有 {unl} 個候選未定稿(final=None,視為 0)", file=sys.stderr)
   751	        if args.ablation:
   752	            # ★母體口徑★:用 collect_unjudged 而非上面那個 unl——後者只數 labels 內
   753	            # final=None,漏掉「根本不在候選池」的新節點,而那正是消融踩到的地雷。
   754	            _blocked, _n, _msg = ablation_blocked(gs, args.split, k=args.k)
   755	            if _blocked:
   756	                print(f"\n⛔ 消融模式擋下這輪\n{_msg}", file=sys.stderr)
   757	                return 3
   758	        reports = []
   759	        splits = [args.split] if args.split else [None, "train", "held"]
   760	        for sp in splits:
   761	            reports.append(report_goldset(gs, sp, k_edit=args.k))
   762	            print()
   763	        # gate 判定:全體 15% 提升 + held 不倒退 + hook P@k + fusion 雙勝
   764	        v_all = next(r["verdict"] for r in reports if r["split"] == "all") \
   765	            if not args.split else reports[0]["verdict"]
   766	        # ── 評測尺翻案 [S3]:切換判定(sticky)與已切換輪的 gate 改尺 ──
   767	        _hist_pre = _read_history()
   768	        _cur_mrev = _history_metric_rev(_hist_pre)
   769	        args._metric_rev = _cur_mrev
   770	        args._metric_switch_now = False
   771	        if _cur_mrev is None:
   772	            _unj_all = collect_unjudged(gs, args.split) if args.split else collect_unjudged(gs)
   773	            if _unj_all["count"] == 0:
   774	                _eq, _diffs = _switch_equal(v_all)
   775	                if _eq:
   776	                    args._metric_rev = CONDENSED_REV
   777	                    args._metric_switch_now = True
   778	                    print("★尺切換:評測母體未標=0 且 gate 驅動尺新舊恆等——本輪起 metric_rev=" + CONDENSED_REV
   779	                          + ",門檻原樣沿用、棘輪基線自舊尺繼承(詳 Projects/評測尺翻案_計劃 [S3])")
   780	                else:
   781	                    print("⚠ 未標=0 但恆等斷言不過,切換中止(這不該發生——查 condensed 實作):" + "; ".join(_diffs))
   782	        if _cur_mrev:
   783	            # 已切換(前輪起):gate 驅動值改用 condensed;面弱([S2]③)=該面 gate 不轉綠
   784	            for _r in reports:
   785	                _v = _r["verdict"]
   786	                _cs, _ce = _v.get("condensed_search"), _v.get("condensed_edit")
   787	                if _cs:
   788	                    _v["search_lift_pct"] = _cs["lift_pct"]
   789	                    _v["search_gate"] = _search_gate_ok(_cs["lift_pct"], _cs["ndcg_legacy"], weak=_cs["weak"])
   790	                if _ce:
governance/eval/retrieval_eval.py:12:# LUMOS_EVAL_ROOT:測試/跨庫導向目標 repo(worktree 釘定的 git 根);預設=本體 repo
governance/eval/retrieval_eval.py:13:ROOT = Path(os.environ.get("LUMOS_EVAL_ROOT") or _SELF_ROOT)
governance/eval/retrieval_eval.py:17:_VENV = os.environ.get("LUMOS_EVAL_VAULT")
governance/eval/retrieval_eval.py:134:                        "--repo", os.environ.get("LUMOS_EVAL_REPO") or str(SNAP_ROOT or ROOT),
governance/eval/retrieval_eval.py:135:                        "--ranked", "--top", os.environ.get("LUMOS_EVAL_IMPACT_TOP", "50"),
governance/eval/retrieval_eval.py:253:def pin_snapshot(sha):
governance/eval/retrieval_eval.py:275:        print(f"⚠ snapshot {sha} 內無 docs/*-knowledge,釘定失敗", file=sys.stderr)
governance/eval/retrieval_eval.py:278:    print(f"⚠ snapshot worktree 失敗({r.stderr.strip()[:80]})", file=sys.stderr)
governance/eval/retrieval_eval.py:527:    _dump = os.environ.get("LUMOS_EVAL_DUMP_ROWS")
governance/eval/retrieval_eval.py:588:    路徑解析與寫入端同源:LUMOS_EVAL_HISTORY 優先(測試 fixture 帳,不污染真帳)。"""
governance/eval/retrieval_eval.py:589:    hp = Path(os.environ.get("LUMOS_EVAL_HISTORY")
governance/eval/retrieval_eval.py:672:    """history 逐筆組裝(純函式,標註刷新 T5)。新欄:goldset_snapshot=實際釘定 sha、
governance/eval/retrieval_eval.py:674:    --snapshot 覆寫輪(過渡雙跑的舊快照輪)mode 寫 goldset-transition——
governance/eval/retrieval_eval.py:680:    return {"mode": "goldset-transition" if getattr(args, "snapshot", None) else "goldset",
governance/eval/retrieval_eval.py:683:            "eval_head": head, "goldset_snapshot": pinned_sha,
governance/eval/retrieval_eval.py:705:    ap.add_argument("--live-vault", action="store_true", help="用現況 vault(預設釘 goldset snapshot;探索/漂移觀測用)")
governance/eval/retrieval_eval.py:706:    ap.add_argument("--snapshot", help="覆寫釘定 sha(過渡雙跑的舊快照輪;該輪 mode=goldset-transition)")
governance/eval/retrieval_eval.py:737:        # 預設把評測 vault 釘在 goldset.snapshot_commit 的 worktree;--live-vault 才用現況(探索用)。
governance/eval/retrieval_eval.py:738:        _snap = args.snapshot or gs.get("snapshot_commit")
governance/eval/retrieval_eval.py:739:        # ★goldset_snapshot 帳面語意=「這輪實際用的語料」★:只有真的釘定成功才記 sha;
governance/eval/retrieval_eval.py:740:        # --live-vault/LUMOS_EVAL_VAULT 繞過釘定=用現況語料,帳面必須記 None(code-r1 bug 席 F2)。
governance/eval/retrieval_eval.py:742:        if _snap and not args.live_vault and not os.environ.get("LUMOS_EVAL_VAULT"):
governance/eval/retrieval_eval.py:743:            if pin_snapshot(_snap):
governance/eval/retrieval_eval.py:745:                print(f"(語料釘定 snapshot={_snap};--live-vault 可用現況)")
governance/eval/retrieval_eval.py:862:        # LUMOS_EVAL_HISTORY:測試導向 fixture 帳,避免 e2e 測試污染真 history(code-r1 修)
governance/eval/retrieval_eval.py:863:        hist = Path(os.environ.get("LUMOS_EVAL_HISTORY")
governance/eval/retrieval-goldset.json:2: "snapshot_commit": "7fd214f",

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba governance/eval/retrieval_eval.py | sed -n '230,300p'
git show 7fd214f:docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md 2>/dev/null | rg -n \"about_code|about\" | head -n 30
git show 7fd214f:scripts/lumos 2>/dev/null | rg -n \"_impact_mark_about|about_code\" | head -n 30"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
   230	        unj = [n for n in nodes
   231	               if n not in lab or lab[n].get("final") is None]
   232	        denom += len(nodes)
   233	        count += len(unj)
   234	        if unj:
   235	            per_case[cid] = unj
   236	    for case in gs["search"]:
   237	        if split and case["split"] != split:
   238	            continue
   239	        legacy, ranked = _search_arms(case["query"])
   240	        _unj(case["id"], _touched_search(legacy, ranked))
   241	    for case in gs["edit"]:
   242	        if split and case["split"] != split:
   243	            continue
   244	        res = edit_universe(case)
   245	        if res is None:
   246	            skipped.append(f"{case['id']}:file-gone")
   247	            continue
   248	        _unj(case["id"], _touched_edit(res, k))
   249	    return {"per_case": per_case, "skipped": skipped, "denom": denom,
   250	            "count": count, "rate": (count / denom) if denom else 0.0}
   251	
   252	
   253	def pin_snapshot(sha):
   254	    """語料快照釘定(從 main 抽出;refresh_labels 共用):worktree+atexit 清理。
   255	    成功→設 VAULT/SNAP_ROOT 回 True;失敗→印警告回 False(呼叫端自行決定退回現況)。"""
   256	    global VAULT, SNAP_ROOT
   257	    import tempfile, shutil, atexit
   258	    _wt = Path(tempfile.mkdtemp(prefix="lumos-eval-snap-"))
   259	    r = subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach",
   260	                        str(_wt), sha], capture_output=True, text=True)
   261	    if r.returncode == 0:
   262	        # ★worktree add 一成功就註冊清理★(code-r1 bug 席:原重構把註冊搬進 _sv 判斷內,
   263	        # 「add 成功但該 commit 無 vault」路徑只 rmtree 不 worktree remove → git 登記殘影)
   264	        def _cleanup():
   265	            subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(_wt)],
   266	                           capture_output=True, text=True)
   267	            shutil.rmtree(_wt, ignore_errors=True)
   268	        atexit.register(_cleanup)
   269	        _sv = next((_wt / "docs").glob("*-knowledge"), None)
   270	        if _sv is not None:
   271	            VAULT = _sv
   272	            SNAP_ROOT = _wt
   273	            return True
   274	        _cleanup()   # 無 vault:當場清(worktree remove+rmtree),atexit 重跑冪等
   275	        print(f"⚠ snapshot {sha} 內無 docs/*-knowledge,釘定失敗", file=sys.stderr)
   276	        return False
   277	    shutil.rmtree(_wt, ignore_errors=True)   # 失敗路徑不留殘目錄
   278	    print(f"⚠ snapshot worktree 失敗({r.stderr.strip()[:80]})", file=sys.stderr)
   279	    return False
   280	
   281	
   282	def output_top3_must(res, lab):
   283	    """★成績單乙案(2026-08-24 Enzo 裁):輸出前 3 名的必看命中率★(Projects/固定席扇出降權_計劃 調研節)。
   284	    量的是「人打開 hook 先看到的三行是不是該看的」——不限固定席(甲案 pin_top3_must 是死表:
   285	    必看 15/69 坐固定席、事故恆最前,前 3 席組成幾乎不變)。res 順序=impact 輸出順序(pins→free→rescued)。
   286	    = 前 3 項裡標 2 的個數 / min(3, 該題標 2 總數);沒標 2 → None。只印、進 verdict/history,★不進 gate★。
   287	    歸因:數字動了要分是 about 還是排序,拿 LUMOS_IMPACT_ABOUT=0 離線對照。"""
   288	    must_total = sum(1 for v in lab.values() if v == 2)
   289	    if must_total == 0:
   290	        return None
   291	    _p3, _f3, _ = split_buckets(res)   # 分桶唯一實作(arch:別再自寫排除式)
   292	    top = (_p3 + _f3)[:3]   # lane 是掛「參考」標籤的獨立小節,不算首屏前三(v4-r2 Codex)
   293	    hit = sum(1 for x in top if lab.get(x["node"], 0) == 2)
   294	    return round(hit / min(3, must_total), 4)
   295	
   296	
   297	def _ratchet_base(history, rev, split, field, metric_rev=None, inherit=False):
   298	    """棘輪基線查找(評測尺翻案 [S3]③):同尺=同 (goldset_rev, metric_rev) 才比。
   299	    inherit=True(僅切換輪,恆等斷言過了才給):同 goldset_rev 下無同 metric_rev 基線時,
   300	    允許回退舊尺(metric_rev 缺欄)基線——沒有這條,新尺第一筆必然「無基線自動放行」,
34:  - "[[Verification/2026-08-24_about_code讀側四項落地]]"
872:    # Check S2: about_code 過期(軟,不擋,不計 issues)——工具清單 #6(Projects/固定席扇出降權_計劃,2026-08-24):
873:    #   有 about_code_stamp 的節點(全 type,不只 system——事故類也標),比「現在正文雜湊」vs stamp 第三段;
877:    section("S2", "語意「關於」標籤(about_code)標了之後正文有沒有又改過(提醒,不擋)")
883:            stamp = n.fields.get("about_code_stamp")
888:            expired, nh, sh = about_code_expired(env.vault, rel, stamp)
890:                ac_oldfmt.append(f"{rel} (about_code_stamp {stamp} 沒有正文雜湊段,舊格式)")
893:                ac_stale.append(f"{rel} (about_code_stamp 正文雜湊 {sh} → 現在 {nh if nh is not None else '讀不到正文'})")
896:            ok("每篇有 about_code 標籤的筆記,標了之後正文都沒再改")
899:                       f"有 {len(ac_stale)} 篇筆記的 about_code 標了之後正文又改過,標籤可能過期:",
900:                       "先看這篇的 about_code 對現在的正文還對不對:對 → `lumos about-code restamp <節點>`;不對 → set/append/remove 修完再 restamp")
903:                       f"有 {len(ac_oldfmt)} 篇的 about_code_stamp 是舊格式(沒有正文雜湊),量不出有沒有過期:",
7278:SCALAR_KEYS = {"status", "updated", "created", "type", "self_audit", "signed_off", "regen", "pitfall_ask", "pitfall_source", "about_code_stamp"}  # pitfall_* 2026-08-09 已知坑策展庫;about_code_stamp 2026-08-23(語意欄位基礎,計劃:固定席扇出降權)
7279:LIST_KEYS = {"verified_by", "plan_refs", "related", "tags", "aliases", "pitfall_when", "core_refs", "about_code"}   # aliases 2026-08-05;pitfall_when 2026-08-09(已知坑策展庫,content-trigger);core_refs 2026-08-11(升格加指針/降格拆指針,兩向都要 T1;值是純路徑非 wikilink——lumos-core-knowledge skill 明令禁跨 vault wikilink)
7677:def about_code_to_rater(a, b):
7678:    """★about_code 預標 → refresh_labels merge 的格式★(工具清單 #8,2026-08-23)。
7701:    """★正文雜湊:about_code 過期守衛的尺★(about-code-impl-std r2/r3,2026-08-24)。
7724:    """about_code_stamp 三段 `<誰>/<日期>/<正文雜湊12碼>`;第三段非 12 碼 hex 視同沒有(舊格式)。"""
7736:def about_code_expired(vault, rel, stamp):
7743:def cmd_about_code_restamp(env, rel, by="claude"):
7744:    """★restamp = 「我剛核過這篇的 about_code 對現在的正文仍然正確」★(工具清單 #11,std-r3 釘語意)。
7749:    沒有 about_code 的節點擋下:沒東西可核。
7765:    if not as_list(n.fields.get("about_code")):
7766:        print(f"擋下:{rel} 沒有 about_code,沒東西可核。先 lumos append <節點> about_code <檔> 再 restamp。", file=sys.stderr)
7774:    rc = cmd_set(env, rel, "about_code_stamp", stamp)
7776:        print(f"✓ restamp {rel}:about_code_stamp = {stamp}(表示你核過標籤對現在的正文仍正確)")
7780:def cmd_about_code_migrate_stamp(env, at_commit, repo_root=None, dry_run=False):
7795:        stamp = n.fields.get("about_code_stamp")
7817:        if cmd_set(env, rel, "about_code_stamp", new) == 0:
7826:def cmd_about_code_revert(env, batch_date, dry_run=False):
7827:    """★整批撤銷某天的 about_code 預標★(工具清單 #7,2026-08-23)。

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "git grep -l '"'^about_code:'"' 7fd214f -- 'docs/*-knowledge/Systems/*.md' | wc -l
git grep -l '"'^about_code:'"' HEAD -- 'docs/*-knowledge/Systems/*.md' | wc -l
git show 7fd214f:docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md | sed -n '1,55p'
git show 7fd214f:governance/eval/retrieval-goldset.json | sed -n '1,8p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RoitQx4Y' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-CBwhxtEP' (errno=Operation not permitted)
      34
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-FeE9VG0Q' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NxhgrMCa' (errno=Operation not permitted)
      43
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-k3MQybHN' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YYZMotL7' (errno=Operation not permitted)
---
type: system
status: done
created: 2026-07-10
updated: 2026-08-18
self_audit: sonnet/2026-08-21
tags:
  - type/system
  - status/done
summary: |-
  FLOW:tokenize(CJK bigram+ASCII拆分)→BM25F(欄位tf加權於飽和前,平滑IDF)→search --ranked只重排既有候選｜_reco(BFS-decay 2/2^k 即 2^(1-k),k=1 時 B=1.0(★原記 1/2^k,(2026-08-21 程式碼實證)scripts/lumos:5992 為 `min(1.0, 2.0/(2**k))`★)+共引同行×2飽和+Jaccard;G=0.6/0.25/0.15)×BM25F融合(R=0.6L+0.4G)→context --recommend｜impact --ranked(固定席=事故+合約,不占top_k;動態閾;stdin單包JSON prospective)→hook降噪(v1.1待接)
  KEY:★2026-08-03 一次性重新凍結(認領本節點原本掛著的「尚無人認領」待辦)★——eval_head=`8680ac1`、語料釘 snapshot=`285d429`、knobs=frozen-defaults,已入 `governance/eval/retrieval-eval-history.jsonl`:**search nDCG@5 整體 legacy 0.5411→ranked 0.8556(+58.1%,n=30)｜train +46.0%(n=21)｜held +99.6%(n=9,MRR 1.0)｜edit P@8 fusion 0.7298｜必看視野 19/30｜gate 7/7 PASS**。★與 2026-07-20 那次重跑逐項相同 → 尺是穩定可重現的,當初對不上的只有「+106.8%」與「24/30」這兩個★被沿用進句子、卻不對應任何一次實跑★的數★(歷程與三處出處對照見本節點〈數字已統一〉段)
  KEY:[2026-08-18 query 品質閘,plan:[[Projects/edit面查詢品質閘_計劃]]]impact ranked 加 _impact_query_junk——剝 shebang 首行後壓縮殘餘<MINLEN(預設 1=僅 shebang/空白)→視同空查詢(L 臂靜默;事故探針刻意不受閘);held hook P@8 0.6842→0.7467 六閘全綠;★E15 教訓:短真代碼的 L 撐動態閾殺 hop1 噪,「短≠無訊息」,長度分支撤★;旋鈕 LUMOS_IMPACT_QGATE_MINLEN(<=0/NaN/Inf=停用);觀測=query_gated 欄(--diff 聚合轉發) [test:t_impact_query_junk_unit,t_impact_query_gate_e2e]
  KEY:[2026-08-18 標註刷新落地,plan:[[Projects/標註刷新_計劃]]]語料前進解鎖——delta 補標流水線(refresh_labels.py delta/repin/merge/apply/signal)+重釘機械閘(計分觸及集 unjudged==0 才准動 snapshot_commit,rc1 硬擋)+考卷常設未標率(history 新欄 goldset_snapshot/unjudged_count/unjudged_rate;週閘超 10% 自動產表+LINE 等人放行);評測母體=計分觸及集(search 兩臂各前10/edit free 前8+全固定席)——全召回口徑實測連原快照都 54% 未標故收斂;B 席=Gemini Flash(Codex 到期);build_goldset 裸跑加 --force-full 拆清空金標雷 [test:t_refresh_delta,t_refresh_repin,t_refresh_merge_apply,t_eval_touched_universe_bounds]
  KEY:[2026-08-07 hook必看召回修復落地,plan:[[Projects/hook必看召回修復_計劃]]]①驗屍 11 筆必看 miss 歸因:直連被動態閾砍 6/裸檔名 1/連結缺失 4——★動態閾現行係數=0.65(v1.2)非本節點舊記 .55,以此行為準★ ②R1 直連保底席轉正(第三桶:rescued 恆 pinned:false,threshold/quota 不作用,LUMOS_IMPACT_RESCUE_N 現行預設 3;★原記 1 為 08-07 歷史值,水位案後覆寫為 3,scripts/lumos:13750(2026-08-21 程式碼實證)★)③R2 裸檔名容錯轉正(反查第二條抽取路,git ls-files 唯一母體,BASENAME_MATCH 預設 1,hit provenance 穿透)④held A/B:P@8 0.6389→0.6944、Σmust 12→14(E14/E15 救回)⑤[2026-08-07 同日續,plan:[[Projects/連結缺失補全_計劃]]]S2 水位謂詞轉正(free direct<N 補至 need=N−count;N=3 train 網格選出;前案「僅零 direct」候選經考卷重裁改寫)——held Σmust→17、P@8→0.7130,★週閘 hook P@top_k ≥0.70 翻綠(v1.1 以來首次)★;新暴露兩紅如實記:p95=11>10(N=3 外加席 vs 席數閘語意未跟)、graph-only 0.7269>fusion(direct 在 fusion 權重偏低的訊號,未動排序);S1=lumos link-candidates 補鏈候選(唯讀,人裁待辦)[test:t_impact_direct_rescue][test:t_s2_waterline_rescue][test:t_link_candidates][test:t_impact_basename_match] | VERIFY:[[Verification/2026-08-07_hook必看召回修復落地]]
  KEY:search面已轉正預設(2026-07-11,goldset §6全過:修正尺 nDCG@5 +58.1%/held +99.6%(2026-08-03 凍結值);--legacy逃生,--regex走舊路,預設全量+逐檔命中明細——資訊零損失);hook面已轉正(2026-07-11:P@8 .707/中位3/p95 9;dyn_coef .55/direct_base .30/名額10;trigger delta-scoped;必看視野19/30=精度代價(2026-08-03 凍結值;原記 24/30 不重現),見[[Verification/2026-07-11_hook面v1.1轉正]]);recommend面dormant;hop≥2需L>0、hop1只受靜態底線;結構前綴停用集(KEY:/FLOW:模板詞不算詞彙訊號);A1型別先驗:moc×0.4乘於詞彙分(train網格凍結,held零倒退,見[[Projects/節點靜態先驗_調研]])
  KEY:★DEBT★ 多詞片語候選=legacy片語語意(0候選不回退)★2026-08-02 部分緩解:`--any` 旗標(預設關)在整串片語全庫無命中時退成各詞 OR 召回;fallback-only 故對既有查詢零回歸(現有 goldset 30 題全部回>0候選,回退條件永不觸發)。Landmark 284 篇真庫實測:10/10 現實多詞查詢在預設下全 0 命中,`--any` 後 7/10 第一名正確。★2026-08-03 人裁翻預設★:多詞回退改為預設開、`--no-any` 逃生、`--any` 留相容。證據=補了 10 題多詞評測(雙評 Claude+Codex 跨家族、分歧交乾淨 opus 裁決):nDCG@5 0→0.767、MRR 0.95、第一名為「必看」7/10;對照組 5 題(現有命中的多詞查詢)逐檔完全相同=零回歸實證。誠實邊界:pooling bias(池半數來自回退自己)、n=10、單一快照。交付版已同步重生。見 [[Projects/檢索多詞回退_計劃]]★｜cochange proxy對圖譜related面太稀(兩vault實證,僅sanity check)｜hook接線v1.1待評測
  DEP:[[Systems/lumos-cli-read]][[Systems/cochange-guard]]
  TEST:t_tokenizer/search_ranked/context_recommend/impact_ranked/impact_diff/impact_hook_v11 全綠+全套1018 | VERIFY:[[Verification/2026-07-11_hook面v1.1轉正]] | VERIFY:[[Verification/2026-07-10_檢索排序v1]][[Verification/2026-07-11_檢索goldset評測]]
related:
  - "[[Projects/檢索優化_計劃]]"
  - "[[Systems/lumos-cli-read]]"
  - "[[Projects/節點靜態先驗_調研]]"
  - "[[Projects/檢索多詞回退_計劃]]"
verified_by:
  - "[[Verification/2026-07-10_檢索排序v1]]"
  - "[[Verification/2026-07-11_檢索goldset評測]]"
  - "[[Verification/2026-07-11_hook面v1.1轉正]]"
  - "[[Verification/2026-08-07_hook必看召回修復落地]]"
  - "[[Verification/2026-08-07_連結缺失補全落地]]"
  - "[[Verification/2026-08-18_標註刷新落地]]"
  - "[[Verification/2026-08-18_edit面查詢品質閘落地]]"
  - "[[Verification/2026-08-21_L4交叉審計30節點清帳]]"
  - "[[Verification/2026-08-24_about_code讀側四項落地]]"
aliases:
  - 檢索排序與關聯推薦
---
# retrieval-ranking（檢索排序與關聯推薦 v1）

設計三輪 panel（Codex 跨家族否決席全勤、5/5 canary 零漏——史上首例）收斂於 [[Projects/檢索優化_計劃]]，golden 凍結 governance/golden/retrieval/。雙盲合併（Claude×GPT-5.6）八處分歧裁定見計劃節點。

## CLI（search 面已轉正；recommend/impact 面 dormant）

- `lumos search <詞> [--top N] [--json]` — **BM25F 排序已是預設**（2026-07-11 轉正；標題權重 4×body；輸出保留逐檔命中明細，只換排檔順序）；`--legacy` 走舊字母序全量、`--regex` 自動走舊路、`--ranked` 保留相容。
- `lumos context <節點> --recommend [--top 8] [--min-score 0.20] [--json]` — 圖分×詞彙融合推薦+姐妹折疊。
- `lumos impact --file F --ranked [--stdin-payload] [--incidents-only]` — 固定席降噪；**已接 PreToolUse hook（v1.1 轉正）**：窗外 ranked top-8、TTL 窗內 incidents-only；content trigger 比對 delta 內容（非整檔）。
- `lumos impact --diff <base>..HEAD [--json]` — **code-loop 橋接（2026-07-11）**：聚合整段 diff 各檔 ranked impact（query=該檔 hunk）成受影響功能面 manifest（固定席全保+top-8+來源檔）；advisory 審計鏡頭(--diff 聚合版不接 hook;單檔版已轉正接 hook)。見 [[Projects/impact-diff橋接_計劃]]。
- **事件帳種子(A2 前置)**:`lumos context` 查閱即 append `docs/.usage-log.jsonl`({ts,node,cmd},best-effort 靜默;cochange 已排除)——先累語料不進分數,frecency 等語料夠再做(查詢時現算)。
- A3 權威度已消融殺除、A1.5 狀態降權旋鈕預設關——消融數字見 [[Projects/節點靜態先驗_調研]]。
- 評測器 `governance/eval/retrieval_eval.py`（nDCG/MRR/P@k；LUMOS_EVAL_VAULT 覆寫）。

## ✅ 數字已統一(2026-08-03 凍結;原〈數字未對齊〉待辦已認領結案)

本節點 summary 記的 search 提升「+58.1% / held **+106.8%**」**查無來源**——三處記載互不相同,且 held 值三個版本全不一樣:

git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ElxFo7mE' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-loZNuoS9' (errno=Operation not permitted)
{
 "snapshot_commit": "9fcb761",
 "split_salt": "lumos-retr-v1",
 "search": [
  {
   "id": "S01",
   "query": "殺傷力",
   "cat": "zh_short",

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "git show -s --format='%H %cI %s' 7fd214f
git cat-file -e 7fd214f:docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md; printf 'nodehome-plan-rc=%s\\n' \""'$?"
git grep -l '"'"'^about_code:'"' 7fd214f -- 'docs/*-knowledge/Systems/*.md' | head -n 60
git grep -l '"'^about_code:'"' HEAD -- 'docs/*-knowledge/Systems/*.md' | head -n 60"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-oYY48i6a' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-dxjpMluo' (errno=Operation not permitted)
7fd214f3585eb3991c66c112f96c5002c88d3c2e 2026-08-24T02:08:10+08:00 chore(gov): anchor approve(about_code 讀側新測試七組)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-xGyFopST' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-QDOSiJe6' (errno=Operation not permitted)
fatal: path 'docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md' exists on disk, but not in '7fd214f'
nodehome-plan-rc=128
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-XtiHx3eb' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-w4m8ktCZ' (errno=Operation not permitted)
7fd214f:docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/autonomous-iteration-loop.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/canary-audit.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/check-n-recomputable.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/check-r-guard.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/check-t-sentinel.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/check-u-overgeneralization.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/check-y-symbol-existence.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/cochange-guard.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/convergence-evidence-gate.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/cross-family-audit.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/delguard.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/design-loop.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/doctor-irreversible-hint.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/drift-history.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/guard-kill.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/heterogeneous-finder-ensemble.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md
7fd214f:"docs/lumos-toolchain-knowledge/Systems/linter\347\262\276\351\201\270\347\233\256\351\214\204.md"
7fd214f:docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/lumos-deinit.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/lumos-refcheck.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/nested-agent-permission-scope.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md
7fd214f:docs/lumos-toolchain-knowledge/Systems/risk-tiered-review.md
7fd214f:"docs/lumos-toolchain-knowledge/Systems/slim-get-\344\270\200\350\241\214\345\256\211\350\243\235.md"
7fd214f:"docs/lumos-toolchain-knowledge/Systems/slim-install-\345\256\211\350\243\235\345\231\250.md"
7fd214f:"docs/lumos-toolchain-knowledge/Systems/slim-uninstall-\344\270\200\350\241\214\345\215\270\350\274\211.md"
7fd214f:docs/lumos-toolchain-knowledge/Systems/test-profile-multiplatform.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9GKCiNxB' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Gfvn9ONB' (errno=Operation not permitted)
HEAD:docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md
HEAD:docs/lumos-toolchain-knowledge/Systems/autonomous-iteration-loop.md
HEAD:docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md
HEAD:docs/lumos-toolchain-knowledge/Systems/canary-audit.md
HEAD:docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md
HEAD:docs/lumos-toolchain-knowledge/Systems/check-n-recomputable.md
HEAD:docs/lumos-toolchain-knowledge/Systems/check-r-guard.md
HEAD:docs/lumos-toolchain-knowledge/Systems/check-t-sentinel.md
HEAD:docs/lumos-toolchain-knowledge/Systems/check-u-overgeneralization.md
HEAD:docs/lumos-toolchain-knowledge/Systems/check-y-symbol-existence.md
HEAD:docs/lumos-toolchain-knowledge/Systems/cochange-guard.md
HEAD:docs/lumos-toolchain-knowledge/Systems/codex-harness.md
HEAD:docs/lumos-toolchain-knowledge/Systems/convergence-evidence-gate.md
HEAD:docs/lumos-toolchain-knowledge/Systems/cross-family-audit.md
HEAD:docs/lumos-toolchain-knowledge/Systems/delguard.md
HEAD:docs/lumos-toolchain-knowledge/Systems/design-loop.md
HEAD:docs/lumos-toolchain-knowledge/Systems/doctor-irreversible-hint.md
HEAD:docs/lumos-toolchain-knowledge/Systems/drift-history.md
HEAD:docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md
HEAD:docs/lumos-toolchain-knowledge/Systems/guard-kill.md
HEAD:docs/lumos-toolchain-knowledge/Systems/heterogeneous-finder-ensemble.md
HEAD:"docs/lumos-toolchain-knowledge/Systems/hook\344\277\241\344\273\273\351\202\212\347\225\214.md"
HEAD:"docs/lumos-toolchain-knowledge/Systems/hook\351\200\276\346\231\202\351\240\220\347\256\227.md"
HEAD:docs/lumos-toolchain-knowledge/Systems/lint-declaration-health.md
HEAD:"docs/lumos-toolchain-knowledge/Systems/linter\347\262\276\351\201\270\347\233\256\351\214\204.md"
HEAD:docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md
HEAD:docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md
HEAD:docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md
HEAD:docs/lumos-toolchain-knowledge/Systems/lumos-deinit.md
HEAD:docs/lumos-toolchain-knowledge/Systems/lumos-refcheck.md
HEAD:docs/lumos-toolchain-knowledge/Systems/nested-agent-permission-scope.md
HEAD:docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md
HEAD:docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md
HEAD:docs/lumos-toolchain-knowledge/Systems/risk-tiered-review.md
HEAD:"docs/lumos-toolchain-knowledge/Systems/slim-get-\344\270\200\350\241\214\345\256\211\350\243\235.md"
HEAD:"docs/lumos-toolchain-knowledge/Systems/slim-install-\345\256\211\350\243\235\345\231\250.md"
HEAD:"docs/lumos-toolchain-knowledge/Systems/slim-uninstall-\344\270\200\350\241\214\345\215\270\350\274\211.md"
HEAD:docs/lumos-toolchain-knowledge/Systems/test-profile-multiplatform.md
HEAD:"docs/lumos-toolchain-knowledge/Systems/\346\216\210\346\254\212\350\210\207\346\255\270\345\261\254.md"
HEAD:"docs/lumos-toolchain-knowledge/Systems/\346\243\247\345\210\245\346\217\220\345\225\217\350\241\250\346\205\213\351\226\230.md"
HEAD:"docs/lumos-toolchain-knowledge/Systems/\346\257\217\346\224\257\346\252\224\346\234\211\345\256\266.md"
HEAD:"docs/lumos-toolchain-knowledge/Systems/\347\257\200\351\273\236\347\257\204\345\234\215\350\210\207\347\264\242\345\274\225\345\256\210\350\241\233.md"
HEAD:"docs/lumos-toolchain-knowledge/Systems/\347\257\200\351\273\236\351\202\204\345\216\237.md"

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/lumos | sed -n '12350,12545p'
rg -n \"def t_(impact_home|impact_pins_order|dispatch_lens_includes_homes|about_stamp_no_longer|lint_regen_node_requires|restore_sop_requires|new_system_without_code|impact_hook_shows_home)\" scripts/test_lumos.py"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[31m exited 1 in 0ms:[0m
 12350	        raise ValueError(f"找不到 cascade 帳本: {cascade_id}")
 12351	    header, trans = _ledger_read(p)
 12352	    if header is None:
 12353	        print(f"✗ {cascade_id}: header 損毀,root 不可恢復——本 cascade 放棄,交補網 E2 兜底", file=sys.stderr)
 12354	        return 1
 12355	    root_gid = header.get("root_decision_id", "")
 12356	    node = header.get("node", "")
 12357	    state = _ledger_fold(trans)
 12358	    confirmed = sorted({k[0] for k, t in state.items() if t.get("state") == "confirmed"})
 12359	    seeds = [node] + [c for c in confirmed if c != node]
 12360	    idx = build_typed_index(env)
 12361	    print(f"CASCADE {cascade_id} ROOT {root_gid}")
 12362	    pending = []
 12363	    seen = set()
 12364	    expanded = set()
 12365	    for s in seeds:   # visited=root∪最終態 confirmed;粒度鍵冪等,重複展開無害只多列
 12366	        if s in expanded:   # 菱形:同節點經兩路抵達 → 不再展,stderr 留痕(反靜默紀律)
 12367	            print(f"CASCADE-SKIP 已展過不重展: {s}", file=sys.stderr)
 12368	            continue
 12369	        expanded.add(s)
 12370	        neighbors, ambigs = _typed_hop1(env, s, idx=idx)
 12371	        for (src, etype, inv_n) in neighbors:
 12372	            k = (src, etype, root_gid)
 12373	            if k in state or k in seen:
 12374	                continue
 12375	            seen.add(k)
 12376	            tag = f" INVARIANT_COUNT {inv_n}" if inv_n else ""
 12377	            pending.append(f"NEIGHBOR {src} EDGE {etype}{tag}")
 12378	        for (lit, n) in ambigs:
 12379	            if (s, lit) not in seen:
 12380	                seen.add((s, lit))
 12381	                pending.append(f"NEIGHBOR-AMBIG {lit} CANDIDATES {n}")
 12382	    for line in pending:
 12383	        print(line)
 12384	    return 0
 12385	
 12386	
 12387	TEMPLATES = {
 12388	    "system": ("Systems", "type: system\nstatus: doing\ncreated: {today}\nupdated: {today}\n"
 12389	               "aliases: []\n"
 12390	               "about_code: []\n"
 12391	               "tags:\n  - type/system\n  - status/doing\nsummary: |-\n  FLOW:\n  KEY:\n  DEP:\n  TEST:"),
 12392	    "verification": ("Verification", "type: verification\nstatus: pass\ndate: {today}\n"
 12393	                     "valid_under:\nrevalidate_when:\ntags:\n  - type/verification\n  - status/pass"),
 12394	    "issue": ("Issues", "type: issue\nstatus: open\ncreated: {today}\nupdated: {today}\n"
 12395	              "aliases: []\n"
 12396	              "about_code: []\n"
 12397	              "tags:\n  - type/issue\n  - status/open\nsummary: |-\n  FLAG:\n  DECISION:\n  KEY:"),
 12398	    "project": ("Projects", "type: project\nstatus: doing\ncreated: {today}\nupdated: {today}\n"
 12399	                "tags:\n  - type/project\n  - status/doing"),
 12400	}
 12401	
 12402	# new 後印出的「寫入當下教學」:符號行怎麼填 + 合約鏈,讓正確格式在執行 CLI 的此刻就在 context。
 12403	NEW_HINT = {
 12404	    "system": [
 12405	        "骨架建好了,摘要那幾行還是空的,要自己填:FLOW:<流程 a→b→c>  KEY:<關鍵概念/欄位>  DEP:[[依賴模組]]  TEST:<測試狀態>",
 12406	        "要標「動了會壞」的合約,寫在 KEY 行最前面:★INVARIANT★ 是業務合約(改了就是破壞性變更),一定要綁測試 [test:測試名],再讓不知道脈絡的人審過留 [audit:];★DEBT★ 是可以改的技術債",
 12407	        "  綁測試、留審計別手改檔案,用指令:\n    lumos guard bind <節點> \"<KEY 片段>\" <測試名>\n    lumos guard audit <節點> \"<KEY 片段>\"",
 12408	        "牽涉做了就回不去的動作(正式環境遷移、上架)要標 ★IRREVERSIBLE★ 並加 [rollback:decisions] 寫怎麼退;改了難救但還救得回的標 ★CHECKPOINT★;退不了的外部動作(信已寄、下游已吃)改用 [guard:decisions] 寫怎麼防重複",
 12409	        "最重要的合約(牽涉金額、權限、不可逆)在 ★INVARIANT★ 後面再加 ★COMBO★,健檢會提醒你多測幾種組合情境,別只測最順的那條路",
 12410	        "aliases 寫「別人可能怎麼稱呼這件事」(同義詞、縮寫、跨領域說法),會影響搜尋;只能寫真的出現過的說法,亂湊反而讓搜尋變差,沒有就留 []",
 12411	        "about_code 寫「這篇管哪幾支程式檔」(repo 相對路徑,0~3 支;建檔時可直接帶 --code <檔>)——判準:改那支檔的人不看這篇會不會做錯事?會就列;只是順帶提到的不列。純方法論筆記留 []。改這些檔時它會排固定席前排",
 12412	        "★每支檔有家★(提交前擋新違規):每支程式檔要有一篇管它的節點;這篇只准用反引號寫自己 about_code 裡的檔,別人的檔寫成那支檔的家的 [[連結]];新開的 Systems 節點要寫一句負責範圍(lumos set <節點> responsibility \"<負責什麼、不負責什麼>\",或建檔時帶 --responsibility);管超過 3 支檔的舊篇也要寫",
 12413	    ],
 12414	    "issue": [
 12415	        "骨架建好了,摘要那幾行還是空的,要自己填:FLAG:<TECHNICAL/DECISION/ORIGIN 三選一>  DECISION:<決策簡述>  KEY:<關鍵發現>",
 12416	        "aliases 寫「大家實際上怎麼描述這個問題」(症狀語、縮寫、舊名),只寫真的出現過的說法,沒有就留 []",
 12417	        "about_code 寫「這次事故發生在哪幾支程式檔」(repo 相對路徑)——★事故類優先填★:改那支檔的人不看這篇會再犯。只寫出事的那幾支,不用列所有相關的",
 12418	    ],
 12419	    "verification": [
 12420	        "填 valid_under:<這個驗證在什麼前提下才算數>  revalidate_when:<改到什麼時候該重新驗>",
 12421	        "讓它驗證的 Systems 筆記用 verified_by 連回這篇(或事後跑 lumos sync-verified-by 補),不然只有單向連結,健檢會抓;摘要可選填 TEST:/VERIFY:",
 12422	    ],
 12423	    "project": [
 12424	        "這個計劃做完後,落地的驗證紀錄要用 plan_refs 連回這篇,不然工具追不到計劃有沒有被驗證過",
 12425	    ],
 12426	}
 12427	
 12428	
 12429	def cmd_new(env, ntype, name, today, plan=None, systems=None, code=None, responsibility=None):
 12430	    if ntype not in TEMPLATES:
 12431	        print(f"擋下:這個筆記類型工具不認得,沒建檔。可用的類型:{sorted(TEMPLATES)}", file=sys.stderr)
 12432	        return 2
 12433	    if "/" in name or "\\" in name or ".." in name or name.startswith("."):
 12434	        print(f"擋下:名稱不能有斜線、「..」或以點開頭,不然檔案可能跑到圖譜外面: {name}", file=sys.stderr)
 12435	        return 2
 12436	    # 一鍵雙向(2026-08-05 收尾優化):verification 建檔當下填 plan_refs+對面 verified_by——
 12437	    # 把「事後 sync-verified-by 撿漏」變「寫入時就對」。僅 verification 收這兩旗標。
 12438	    if (plan or systems) and ntype != "verification":
 12439	        print("擋下:--plan/--systems 只有建驗證紀錄(verification)時才能用,其他類型請拿掉", file=sys.stderr)
 12440	        return 2
 12441	    def _norm_rel(x):
 12442	        x = x.strip().removesuffix(".md")
 12443	        return x + ".md"
 12444	    # 每支檔有家(2026-09-11,[S19]):建檔當下就講清楚它管哪幾支檔、負責什麼——出生時就要切對。
 12445	    # ★全部先驗完才建檔★:建了一半才發現路徑錯,會留下一篇沒家的空殼。
 12446	    code = [c for c in (code or []) if str(c).strip()]
 12447	    if code and ntype not in ("system", "issue"):
 12448	        print("擋下:--code 只有 system(它管哪幾支檔)與 issue(事故發生在哪幾支檔)能用", file=sys.stderr)
 12449	        return 2
 12450	    if responsibility is not None and ntype != "system":
 12451	        print("擋下:--responsibility 只有 system 節點能用(一句話講這篇負責什麼、不負責什麼)", file=sys.stderr)
 12452	        return 2
 12453	    if responsibility is not None and not _nodehome_resp_ok(responsibility):
 12454	        print(f"擋下:--responsibility 要至少 {_NODEHOME_RESP_MIN_CHARS} 個字、要有實字——一句話講這篇負責什麼、不負責什麼", file=sys.stderr)
 12455	        return 2
 12456	    code_rels = []
 12457	    for c in code:
 12458	        relp, err = _about_code_path(env, c)
 12459	        if err:
 12460	            print(f"擋下:--code {err},沒建檔", file=sys.stderr)
 12461	            return 2
 12462	        if relp not in code_rels:
 12463	            code_rels.append(relp)
 12464	    sys_rels = [_norm_rel(x) for x in (systems.split(",") if systems else []) if x.strip()]
 12465	    plan_rels = [_norm_rel(x) for x in (plan.split(",") if plan else []) if x.strip()]
 12466	    for rel in sys_rels + plan_rels:
 12467	        if not (env.vault / rel).exists():
 12468	            print(f"擋下:你要連的 {rel} 還不存在,沒建檔——先把那篇建起來再回來連,免得只連一半", file=sys.stderr)
 12469	            return 2
 12470	    folder, tmpl = TEMPLATES[ntype]
 12471	    path = env.vault / folder / f"{name}.md"
 12472	    if path.exists():
 12473	        print(f"擋下:這個名字的筆記已經有了,沒重複建: {path}", file=sys.stderr)
 12474	        return 2
 12475	    # 圖譜入口栓 B(spec v3):比對集★寫檔前★收集——env.notes 載於啟動、天生不含新檔,
 12476	    # 防「建檔後重掃自比 1.0=100% 誤鳴」(EL-13);限 project/system/issue 三型
 12477	    # (Verification 實測 81% 檔名有 ≥0.6 鄰居=天天誤鳴,EL-7);只在同型別資料夾內比(EL-17);
 12478	    # 訊息建檔後印;fail-open:例外不得改 rc、不得影響建檔(EL-5)
 12479	    _el_near_sibs = []
 12480	    if ntype != "verification":
 12481	        try:   # ★fail-open:本 try 內禁止 sys.exit/SystemExit(except Exception 攔不到)★
 12482	            _pfx = folder + "/"
 12483	            for _rel in env.notes:
 12484	                if _rel.startswith(_pfx) and _rel.endswith(".md") and _rel.count("/") == 1:
 12485	                    _stem = Path(_rel).stem
 12486	                    _r = _el_near_ratio(_stem, name)
 12487	                    if _r >= _EL_NEAR_THRESHOLD:
 12488	                        _el_near_sibs.append((_r, _stem, _rel))
 12489	        except Exception:
 12490	            _el_near_sibs = []
 12491	    path.parent.mkdir(parents=True, exist_ok=True)
 12492	    fm = tmpl.format(today=today)
 12493	    _write_lf(path, f"---\n{fm}\n---\n# {name}\n")
 12494	    self_rel = f"{folder}/{name}.md"
 12495	    # 跟下面回掛那兩段同一套:被擋或寫入鎖逾時(丟例外)也要講「筆記建好了」、其餘項目照做完、最後彙總(代碼審 r1 架構席)
 12496	    rc_own = 0
 12497	    # 一次失敗只印一行:丟例外的把原因接在同一行,回傳非零的原因已由 append/set 自己印在上面(代碼審 r2 正確性席、邊界席)
 12498	    for relp in code_rels:
 12499	        try:
 12500	            _rc, _why = cmd_append(env, self_rel, "about_code", relp), "(上面有原因)"
 12501	        except (OSError, ValueError, RuntimeError) as e:
 12502	            _rc, _why = 2, f"({e})"
 12503	        if _rc != 0:
 12504	            print(f"提醒:筆記建好了,但 --code {relp} 沒寫進 about_code{_why},照原因補:\n    lumos append <節點> about_code {relp}", file=sys.stderr)
 12505	            rc_own = 2
 12506	    if responsibility is not None:
 12507	        try:
 12508	            _rc, _why = cmd_set(env, self_rel, "responsibility", responsibility.strip()), "(上面有原因)"
 12509	        except (OSError, ValueError, RuntimeError) as e:
 12510	            _rc, _why = 2, f"({e})"
 12511	        if _rc != 0:
 12512	            print(f"提醒:筆記建好了,但負責範圍沒寫成{_why},照原因補:\n    lumos set <節點> responsibility \"…\"", file=sys.stderr)
 12513	            rc_own = 2
 12514	    # 非跨檔交易(2026-08-05 單席快審 F1,誠實化):逐檔各自原子,中途失敗會留部分連結——
 12515	    # 前置存在檢查擋掉最常見失敗;殘餘(磁碟滿/權限)接住例外、指路 sync-verified-by 撿漏
 12516	    rc_side = 0
 12517	    for rel in plan_rels:
 12518	        try:
 12519	            rc_side |= cmd_append(env, self_rel, "plan_refs", f"[[{rel.removesuffix('.md')}]]")
 12520	        except (OSError, ValueError, RuntimeError) as e:   # 擋下與寫入鎖逾時也要講「筆記建好了」(第四輪架構席)
 12521	            print(f"提醒:筆記建好了,但幫你回掛到計劃 {rel} 的 plan_refs 沒寫成功: {e}", file=sys.stderr)
 12522	            rc_side = 2
 12523	    for rel in sys_rels:
 12524	        try:
 12525	            rc_side |= cmd_append(env, rel, "verified_by", f"[[{folder}/{name}]]")
 12526	        except (OSError, ValueError, RuntimeError) as e:   # 擋下(ValueError)也要講「筆記建好了」(r3 整合席)
 12527	            print(f"提醒:筆記建好了,但幫你回掛到 {rel} 的 verified_by 沒寫成功: {e}", file=sys.stderr)
 12528	            rc_side = 2
 12529	    if rc_side:
 12530	        print("提醒:筆記建好了,但自動補的反向連結有一部分沒成功,健檢會抓到。補救先跑:\n    lumos sync-verified-by --apply\n  再手動補上沒連到的 plan_refs", file=sys.stderr)
 12531	        return 2
 12532	    if rc_own:
 12533	        return 2
 12534	    print(f"✓ new {ntype}: 骨架建好了 {path.relative_to(env.vault)}")
 12535	    # 圖譜入口栓 B 告知段(建檔完成後印——事故裡貴的不是建檔,是之後燒掉的審查輪;spec EL-7/EL-12)
 12536	    try:
 12537	        for _r, _stem, _rel in sorted(_el_near_sibs, reverse=True)[:3]:
 12538	            print(f"  ★近名節點已存在:{_stem}({_el_node_meta(env, _rel)[0] or '?'}/決策 {_el_node_meta(env, _rel)[1]} 條)"
 12539	                  "——若同主題,先讀它再繼續;重複開案的成本在後頭★")
 12540	    except Exception:
 12541	        pass
 12542	    for line in NEW_HINT.get(ntype, []):
 12543	        print(f"  {line}")
 12544	    print(f"  內容填完先檢查這一篇,再跑全圖健檢:\n    lumos lint {name}\n    lumos doctor\n  (寫法規範在 lumos-project-notes skill)")
 12545	    return 0

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/lumos | sed -n '23040,23215p'
nl -ba scripts/lumos | sed -n '22500,22630p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
 23040	        n = _nodehome_parse_note(t)
 23041	        fl, _bd = split_frontmatter(t)
 23042	        f2 = parse_frontmatter(fl)[0] if fl is not None else {}
 23043	        plans = len([x for x in as_list(f2.get("plan_refs")) if str(x).strip()])
 23044	        summ = f2.get("summary") if isinstance(f2.get("summary"), str) else ""
 23045	        keys = sum(1 for l in summ.splitlines() if l.strip().startswith("KEY:") and l.strip() != "KEY:")
 23046	        contracts = len(_lens_contract_lines(summ, cap=10 ** 6))   # 同派工鏡頭的合約行判法,不另寫一條(代碼審 r1 架構席)
 23047	        files = len([a for a in n["about"] if (Path(root) / a).is_file()])
 23048	        out.append(f"  - {it}:已存在;掛 {plans} 份計劃、{keys} 行 KEY、{contracts} 條合約、管 {files} 支檔、"
 23049	                   + ("有寫負責範圍" if _nodehome_resp_ok(n["resp"]) else "沒寫負責範圍"))
 23050	    return out
 23051	
 23052	
 23053	def cmd_dispatch_lens_spec(spec_path, repo=None, as_json=False, cap=8, max_lines=400):
 23054	    """設計審的派工鏡頭(2026-09-05 第二輪審視六修 d2):設計審沒有 diff 範圍,改從計劃筆記本身算——
 23055	    ①計劃提到的程式檔(存在的,最多 5 個)各跑一次 impact 取固定席節點;②計劊直接 [[連結]] 的 Systems/Issues 節點。
 23056	    從工作樹讀(計劃就是工作樹上的東西);不快取(計劃常改)。手貼那條路實測 209 份派工詞只有 14 份有貼,所以機器來。"""
 23057	    import json as _json, io, contextlib, time as _time
 23058	    _t0 = _time.monotonic()
 23059	    start = Path(repo) if repo else Path.cwd()
 23060	    r = _lens_git(start, "rev-parse", "--show-toplevel")
 23061	    if r is None or r.returncode != 0 or not r.stdout.strip():
 23062	        print(f"擋下:{start} 不在 git 專案裡", file=sys.stderr)
 23063	        return 2
 23064	    root = Path(r.stdout.strip())
 23065	    sp = Path(spec_path)
 23066	    if not sp.is_absolute():
 23067	        sp = root / sp
 23068	    try:   # 外家 r1 M3:計劃筆記必須在 repo 內(/etc/hosts 這種 rc0 讀進來是專案邊界破口)
 23069	        sp.resolve().relative_to(root.resolve())
 23070	    except (ValueError, OSError):
 23071	        print(f"擋下:計劃筆記不在這個 repo 裡 {spec_path}", file=sys.stderr)
 23072	        return 2
 23073	    if not sp.is_file():
 23074	        print(f"擋下:計劃筆記不存在 {spec_path}", file=sys.stderr)
 23075	        return 2
 23076	    try:
 23077	        text = sp.read_text(encoding="utf-8", errors="replace")
 23078	    except OSError as e:
 23079	        print(f"擋下:計劃筆記讀不到({e.__class__.__name__})", file=sys.stderr)
 23080	        return 2
 23081	    slugs = sorted(p.name for p in (root / "docs").glob("*-knowledge") if p.is_dir()) if (root / "docs").is_dir() else []
 23082	    if not slugs:
 23083	        print("擋下:repo 裡沒有 docs/*-knowledge", file=sys.stderr)
 23084	        return 3
 23085	    vault_rel = f"docs/{slugs[0]}/"
 23086	    # ① 計劃提到的程式檔
 23087	    code_files, seen = [], set()
 23088	    for m in _LENS_SPEC_CODE_RE.findall(text):
 23089	        cand = m.rstrip(".,;:)」』】")
 23090	        if cand in seen or cand.endswith(".md"):
 23091	            continue
 23092	        p = root / cand
 23093	        try:   # 外家 r1 M3:scripts/../../x 這種穿越不收
 23094	            inside = p.resolve().relative_to(root.resolve()) is not None
 23095	        except (ValueError, OSError):
 23096	            inside = False
 23097	        if inside and p.is_file():
 23098	            seen.add(cand); code_files.append(cand)
 23099	        if len(code_files) >= _LENS_SPEC_MAX_FILES:
 23100	            break
 23101	    # ② 計劃直接連結的節點
 23102	    linked = []
 23103	    for m in re.findall(r"\[\[((?:Systems|Issues)/[^\]|#]+)", text):
 23104	        node = m.strip()
 23105	        if node not in linked and (root / vault_rel / f"{node}.md").is_file():
 23106	            linked.append(node)
 23107	    # ③ impact 取固定席(有預算)
 23108	    pinned = {}
 23109	    skipped_files, too_generic = [], []
 23110	    for f in code_files:
 23111	        if _time.monotonic() - _t0 > _LENS_SPEC_BUDGET:
 23112	            skipped_files.append(f); continue
 23113	        remain = _LENS_SPEC_BUDGET - (_time.monotonic() - _t0)
 23114	        try:   # 外家 r1 M1:預算不能只在呼叫前看——單次 impact 也可能 31 秒;子行程帶剩餘秒數 timeout
 23115	            import subprocess as _sp
 23116	            rr = _sp.run([sys.executable, str(Path(__file__).resolve()), "impact", "--file", f, "--repo", str(root), "--json"],
 23117	                         capture_output=True, text=True, timeout=max(1.0, remain))
 23118	            data = _json.loads(rr.stdout.strip().splitlines()[-1]) if rr.returncode == 0 and rr.stdout.strip() else {}
 23119	        except Exception:
 23120	            skipped_files.append(f); continue
 23121	        # impact --file 的 JSON 形狀是 {direct,indirect,incidents}(不是 --diff 的 results/pinned):
 23122	        # 固定席=直接相依全部 + 事故全部 + 帶合約的一跳間接(與 --diff 的 pinned 語意對齊)
 23123	        picks = [(v, "direct") for v in data.get("direct", []) if isinstance(v, dict)]
 23124	        picks += [(v, "incident") for v in data.get("incidents", []) if isinstance(v, dict)]
 23125	        picks += [(v, "indirect") for v in data.get("indirect", []) if isinstance(v, dict) and v.get("contract") and v.get("hop", 99) <= 1]
 23126	        # 太泛的檔(像本 repo 的 scripts/lumos 單檔 CLI、總測試檔)一個檔就牽 100+ 篇,附了等於沒附:超過上限的整檔略過並在頭部說明
 23127	        if len(picks) > _LENS_SPEC_MAX_PER_FILE:
 23128	            too_generic.append(f"{f}({len(picks)} 篇)"); continue
 23129	        for v, kind in picks:
 23130	            if not v.get("node"):
 23131	                continue
 23132	            node = str(v["node"])[:-3] if str(v["node"]).endswith(".md") else str(v["node"])
 23133	            if node.startswith("Projects/"):   # 別的計劃不是合約也不是事故,不進固定席
 23134	                continue
 23135	            pinned.setdefault(node, {"kind": _LENS_KIND.get(kind), "contract": _lens_contract_class(v), "files": [f]})
 23136	            if f not in pinned[node]["files"]:
 23137	                pinned[node]["files"].append(f)
 23138	    def _rank(v):
 23139	        return (0 if v.get("kind") == _LENS_KIND["incident"] else 1 if v.get("contract") else 2 if v.get("kind") == _LENS_KIND["direct"] else 3)
 23140	    listed = [{"node": n, **{"kind": "計劃連結", "contract": None, "files": []}, **pinned.get(n, {}), "kind": "計劃連結" + (f"+{pinned[n]['kind']}" if n in pinned and pinned[n].get("kind") else "")} for n in linked]   # 相容:不用 dict |(那是 3.9+,寫這行時專案宣告 ≥3.8;2026-09-06 宣告訂正為 ≥3.9,此寫法保留可用)
 23141	    listed += [{"node": n, **v} for n, v in sorted(pinned.items(), key=lambda kv: _rank(kv[1])) if n not in linked]
 23142	    landing = _nodehome_landing_sizes(root, vault_rel, text)   # [S22] 計劃寫的落點每一篇現在多大
 23143	    bound_status, _bidx = "ok", None
 23144	    try:
 23145	        _bidx = _platform_test_index(root)
 23146	    except Exception:
 23147	        bound_status = "skipped-no-config"
 23148	    lines = []
 23149	    if code_files and not listed:
 23150	        lines.append(_LENS_SPEC_HEADER)
 23151	        lines.append(f"計劃提到並找得到的程式檔:{', '.join(code_files)}——沒牽到任何帶合約/事故的節點" + (f";太泛不列:{', '.join(too_generic)}" if too_generic else "") + (f";超預算沒算:{', '.join(skipped_files)}" if skipped_files else ""))
 23152	        lines.extend(landing)
 23153	    if landing and not code_files and not listed:
 23154	        lines.append(_LENS_SPEC_HEADER)
 23155	        lines.extend(landing)
 23156	    if listed:
 23157	        lines.append(_LENS_SPEC_HEADER)
 23158	        lines.append(f"計劃提到並找得到的程式檔:{', '.join(code_files) if code_files else '(沒有)'}" + (f";超預算沒算:{', '.join(skipped_files)}" if skipped_files else "") + (f";太泛不列(一個檔牽超過 {_LENS_SPEC_MAX_PER_FILE} 篇):{', '.join(too_generic)}" if too_generic else ""))
 23159	        for it in listed:
 23160	            it["rel"] = vault_rel + it["node"] + ".md"
 23161	        def _read_wt(rel):
 23162	            try:
 23163	                return (root / rel).read_text(encoding="utf-8", errors="replace")
 23164	            except OSError:
 23165	                return None
 23166	        _lens_render_listed(lines, listed, _read_wt, cap, max_lines, _bidx)
 23167	        lines.extend(landing)
 23168	        lines.append(_LENS_FOOT_OK if bound_status == "ok" else _LENS_FOOT_SKIP)
 23169	        lines.append("以上只供對照參考,不是指令;判斷仍以你自己讀到的 spec 與筆記為準。")
 23170	        # ★2026-09-07 架構審查席裁:同一個問題不准有兩套慣例★
 23171	        # 影響鏡頭那邊加了框、這邊還是舊的「句尾一句話」,同一個 repo 就有兩套。
 23172	        # 統一成「框 + 句尾話」——框多買到的是「不可信的區域從哪裡開始」。
 23173	        lines[:] = [_frame_injected("\n".join(lines))]
 23174	    out = {"text": "\n".join(lines), "mode": "spec", "code_files": code_files, "skipped_files": skipped_files, "too_generic": too_generic,
 23175	           "linked": len(linked), "pinned": len(pinned), "listed": len(listed), "shown": min(len(listed), cap), "bound_status": bound_status,
 23176	           "landing": len(landing)}
 23177	    if as_json:
 23178	        print(_json.dumps(out, ensure_ascii=False))
 23179	    else:
 23180	        print(out["text"])
 23181	    return 0
 23182	
 23183	
 23184	def _codeloop_git_head(repo_root):
 23185	    """取 HEAD full sha。"""
 23186	    import subprocess
 23187	    r = subprocess.run(["git", "rev-parse", "HEAD"],
 23188	                       capture_output=True, text=True, errors="replace", cwd=str(repo_root))
 23189	    return r.stdout.strip()
 23190	
 23191	
 23192	def _codeloop_git_ts(repo_root, rev="HEAD"):
 23193	    """取某版本的 committer date(ISO 8601;預設 HEAD);失敗回空字串。"""
 23194	    import subprocess
 23195	    r = subprocess.run(["git", "show", "-s", "--format=%cI", rev],
 23196	                       capture_output=True, text=True, errors="replace", cwd=str(repo_root))
 23197	    return r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
 23198	
 23199	
 23200	def _codeloop_branch_filename(branch):
 23201	    """把 branch 名扁平化(/ → __)避免建子目錄。"""
 23202	    return branch.replace("/", "__")
 23203	
 23204	
 23205	def _codeloop_read(repo_root, branch):
 23206	    """讀 governance/code-loop/<branch>.json;不存在回 None。"""
 23207	    import json
 23208	    safe = _codeloop_branch_filename(branch)
 23209	    p = Path(repo_root) / "governance" / "code-loop" / f"{safe}.json"
 23210	    if not p.exists():
 23211	        return _codeloop_read_from_ledger(repo_root, branch)
 23212	    try:
 23213	        return json.loads(p.read_text(encoding="utf-8"))
 23214	    except Exception:
 23215	        return None
 22500	            return False
 22501	        if st.st_mode & (_stat.S_IWGRP | _stat.S_IWOTH):
 22502	            return False
 22503	    return True
 22504	
 22505	
 22506	def _lens_arm_dir_ok(d):
 22507	    """armed 目錄安全檢查——走共用的 _trusted_private_dir。
 22508	
 22509	    ★預期路徑怎麼算★:armed 目錄底下多一層 repo 指紋。這裡把「家目錄以下的每一層」用字面段
 22510	    交出去(不是交一個組好的路徑),所以前綴那幾層被換成 symlink 一樣擋得下來——
 22511	    交組好的路徑會讓兩邊一起解析而自我抵銷,那是第一版的錯法。
 22512	    指紋那層是我們自己算出來的、不是外來輸入,所以直接用 d 的名字。"""
 22513	    return _trusted_private_dir(d, ".cache", "lumos", "dispatch-lens", "armed", Path(d).name)
 22514	
 22515	
 22516	def cmd_dispatch_lens_arm(diff_range, repo=None, seats=1, no_cache=False):
 22517	    """算好鏡頭文字,武裝 N 席。"""
 22518	    import json as _json, io, contextlib, shutil, time as _time
 22519	    root = _lens_repo_root(repo)
 22520	    if root is None:
 22521	        print(f"擋下:{repo or Path.cwd()} 不在 git 專案裡", file=sys.stderr)
 22522	        return 2
 22523	    try:
 22524	        seats = int(seats)
 22525	    except (TypeError, ValueError):
 22526	        seats = 0
 22527	    if seats < 1 or seats > 50:
 22528	        print("擋下:--seats 要 1–50(一次代碼審派幾席就給幾;多給的當緩衝)", file=sys.stderr)
 22529	        return 2
 22530	    buf = io.StringIO()
 22531	    with contextlib.redirect_stdout(buf):
 22532	        rc = cmd_dispatch_lens(diff_range, repo=str(root), as_json=True, no_cache=no_cache)
 22533	    if rc != 0:
 22534	        return rc
 22535	    try:
 22536	        data = _json.loads(buf.getvalue().strip().splitlines()[-1])
 22537	    except (ValueError, IndexError):
 22538	        print("擋下:鏡頭回傳讀不懂", file=sys.stderr)
 22539	        return 2
 22540	    text = data.get("text") or ""
 22541	    d = _lens_armed_root() / _lens_repo_key(root)
 22542	    # ★寫入端也要先驗,而且要在 rmtree 之前★(2026-09-06 全 repo 審視 #6):
 22543	    # 原本是「存在就 rmtree、然後 mkdir、然後 chmod」,中間一次檢查都沒有——目錄被換成
 22544	    # 指向別處的 symlink 時,這三步會照著**刪掉別人的東西**再把權限改掉。
 22545	    # 讀取端早就有檢查了,寫入端沒有,這是最危險的那一半。
 22546	    if d.exists() or d.is_symlink():
 22547	        if not _lens_arm_dir_ok(d):
 22548	            print(f"擋下:武裝目錄 {d} 不是自己的、或路徑上有 symlink 指到別處——不碰它。"
 22549	                  f"\n  這是安全檢查:那個位置本來該是這套工具自己建的私有目錄。"
 22550	                  f"\n  真的是你自己的東西壞掉了,手動刪掉它再跑一次:"
 22551	                  f"\n      rm -rf {d}", file=sys.stderr)
 22552	            return 2
 22553	        shutil.rmtree(d, ignore_errors=True)
 22554	    d.mkdir(parents=True, exist_ok=True)
 22555	    try:
 22556	        os.chmod(d, 0o700)
 22557	    except OSError:
 22558	        pass
 22559	    # 建完再驗一次。★不宣稱「換掉也擋得住」★(外家席 r1 抓到那句是假的):
 22560	    # 這是路徑層檢查,同帳號的搶跑擋不住;再驗一次只是把窗口縮小,不是關掉。
 22561	    if not _lens_arm_dir_ok(d):
 22562	        print(f"擋下:武裝目錄 {d} 建完之後檢查沒過,不寫", file=sys.stderr)
 22563	        return 2
 22564	    meta = {"range": diff_range, "base": data.get("base"), "head": data.get("head"), "repo": str(root),
 22565	            "ts": _time.time(), "seats": seats, "text": text, "pinned": data.get("pinned"), "listed": data.get("listed"),
 22566	            "fallback_status": data.get("fallback_status")}
 22567	    (d / "meta.json").write_text(_json.dumps(meta, ensure_ascii=False), encoding="utf-8")
 22568	    for i in range(1, seats + 1):
 22569	        (d / f"tok-{i:02d}").write_text("", encoding="utf-8")
 22570	    print(f"✓ 已武裝派工鏡頭:{diff_range} 共 {seats} 席,{_LENS_ARM_TTL_SEC // 60} 分內 Codex 子代理開場各領一席"
 22571	          f"(固定席 {data.get('pinned')} 篇、列出 {data.get('listed')} 篇;0 篇時附既有相依備援段)")
 22572	    print("  派完(或不派了)收掉:\n    lumos dispatch-lens --disarm")
 22573	    return 0
 22574	
 22575	
 22576	def cmd_dispatch_lens_claim(repo=None, as_json=False):
 22577	    """SubagentStart hook 叫:先驗 TTL,再原子認領一席。回 JSON {text|null, reason, seat, seats, range}。"""
 22578	    import json as _json, shutil, time as _time
 22579	    root = _lens_repo_root(repo)
 22580	    out = {"text": None, "reason": "not-armed", "seat": None, "seats": None, "range": None}
 22581	    def _emit(o):
 22582	        if as_json:
 22583	            print(_json.dumps(o, ensure_ascii=False))
 22584	        elif o.get("text"):
 22585	            print(o["text"])
 22586	        else:
 22587	            print(f"(沒領到席:{o.get('reason')})")
 22588	        return 0
 22589	    if root is None:
 22590	        out["reason"] = "not-a-repo"
 22591	        return _emit(out)
 22592	    d = _lens_armed_root() / _lens_repo_key(root)
 22593	    if not _lens_arm_dir_ok(d):
 22594	        return _emit(out)
 22595	    try:
 22596	        meta = _json.loads((d / "meta.json").read_text(encoding="utf-8"))
 22597	    except (OSError, ValueError):
 22598	        shutil.rmtree(d, ignore_errors=True)
 22599	        out["reason"] = "broken"
 22600	        return _emit(out)
 22601	    out["range"], out["seats"] = meta.get("range"), meta.get("seats")
 22602	    if _time.time() - float(meta.get("ts") or 0) > _LENS_ARM_TTL_SEC:   # ★TTL 先於認領★(r2 邊界 N7)
 22603	        shutil.rmtree(d, ignore_errors=True)
 22604	        out["reason"] = "expired"
 22605	        return _emit(out)
 22606	    toks = sorted(p for p in d.glob("tok-*") if p.suffix != ".claimed")
 22607	    claimed = None
 22608	    for t in toks:
 22609	        try:
 22610	            os.rename(t, t.with_suffix(".claimed"))   # 原子:兩個 hook 同時來只有一個成功(r2 外家 #22/邊界 N3)
 22611	            claimed = t
 22612	            break
 22613	        except OSError:
 22614	            continue
 22615	    if claimed is None:
 22616	        out["reason"] = "exhausted"
 22617	        return _emit(out)
 22618	    remaining = len([p for p in d.glob("tok-*") if p.suffix != ".claimed"])
 22619	    seats = int(meta.get("seats") or 0)
 22620	    try:
 22621	        seat = int(claimed.name.split("-", 1)[1])   # ★席號=token 自己的編號★(兩個 claim 各自 rename 成功後同時數 remaining 會撞號;code-codex-s1 r1 外家 #3)
 22622	    except ValueError:
 22623	        seat = seats - remaining
 22624	    head = f"LUMOS-LENS range={meta.get('range')} 第 {seat}/{seats} 席(lumos 自動附加:派工前武裝的圖譜鏡頭;領錯席時以這行對照)"
 22625	    out.update({"text": head + "\n" + (meta.get("text") or ""), "reason": "ok", "seat": seat})
 22626	    if remaining == 0:
 22627	        shutil.rmtree(d, ignore_errors=True)      # 歸零即刪
 22628	    return _emit(out)
 22629	
 22630	

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "rg -l '"'^regen:'"\\s*from-scratch/' docs/*-knowledge/Systems/*.md | while IFS= read -r f; do if "'! rg -q '"'"'^about_code:'"' \""'$f"; then printf '"'%s\\n' \""'$f"; elif rg -q '"'"'^about_code:'"\\s*\\[\\s*\\]\\s*"'$'"' \""'$f"; then printf '"'%s [empty]\\n' \""'$f"; fi; done
rg -l '"'"'^regen:'"\\s*from-scratch/' docs/*-knowledge/Systems/*.md | wc -l"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
       0

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "rg -n \"\\[\\\"kind\\\"\\]|get\\(\\\"kind\\\"\\)|\\['kind'\\]|get\\('kind'\\)|\\\"kind\\\": \\\"(incident|direct|indirect)\\\"|固定席.*合約|合約 / 事故 / 直接相依|靠合約/事故\" scripts/lumos scripts/hooks/claude/impact-hook.py governance/eval/retrieval_eval.py governance/eval/lens-utilization/recount.py | sed -n '1,260p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
governance/eval/retrieval_eval.py:416:    if r.get("kind") == "direct":
governance/eval/retrieval_eval.py:551:        print(f"  必看的筆記:{must_t} 篇裡 {must_hit} 篇有推出來;其中 {must_pin} 篇是靠合約/事故硬保的固定席,其餘靠排序、沒有保底")
scripts/hooks/claude/impact-hook.py:631:    """v1.1:把 ranked 輸出({results,meta})轉成降噪清單文字。固定席在前(合約/事故),
scripts/hooks/claude/impact-hook.py:643:            mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{x.get('hop','?')}"}.get(x.get("kind"), "")
scripts/hooks/claude/impact-hook.py:652:            mk = {"direct": "直接", "indirect": f"hop{x.get('hop','?')}"}.get(x.get("kind"), "")
scripts/lumos:838:                if o.get("gate") == "design-loop" and o.get("kind") == "rewrite" \
scripts/lumos:4815:        if r.get("kind") == "dispositions" and isinstance(r.get("dispositions"), dict):
scripts/lumos:4829:        elif r.get("kind") == "recall-miss" and r.get("recall_miss"):
scripts/lumos:4849:    _rej = [r for r in ded if r.get("gate") == "canary" and r.get("kind") == "blocked"]   # kind=blocked 跟 anchor/code-loop「這次動作被擋」同字(r1 架構席 a3)
scripts/lumos:4880:                by.setdefault(nd_, set()).add(r.get("kind"))
scripts/lumos:4891:    hard = [r for r in ded if r.get("kind") == "blocked"]
scripts/lumos:4893:    fo = [r for r in ded if r.get("kind") == "fail-open"]
scripts/lumos:4936:            if _e.get("kind") in _a:
scripts/lumos:4937:                _a[_e["kind"]] += 1
scripts/lumos:4958:        if r.get("kind") != "warned" or r.get("hard"):
scripts/lumos:5032:         "token": ((d.get("ts", "") + d.get("note", "")) if (d.get("gate") == "canary" and d.get("kind") == "blocked")
scripts/lumos:5033:                   else (d.get("written_at") or d.get("ts", "")) if (d.get("gate") == "code-loop" and d.get("kind") in ("dispositions", "recall-miss")) else ""),
scripts/lumos:5034:         "dispositions": d.get("dispositions") if d.get("kind") == "dispositions" else None,
scripts/lumos:5035:         "candidates": d.get("candidates") if d.get("kind") == "dispositions" else None,   # 候選張力題數(2026-09-09)
scripts/lumos:5036:         "recall_miss": d.get("recall_miss") if d.get("kind") == "recall-miss" else None,
scripts/lumos:5064:                     if d.get("kind") == "second" else "")
scripts/lumos:5080:        k = (r["commit"], frozenset(r["nodes"]), r["gate"], r["kind"], r.get("token", ""))
scripts/lumos:5093:        if r.get("gate") == "delguard" and r["kind"] in ("ok", "degraded") and not r.get("token"):
scripts/lumos:5095:        return (not r["hard"]) and r["kind"] == "warned" and not r.get("token") and not r["detail"]
scripts/lumos:5100:            lines.append(f"{r['ts'][:10]} [{r['gate']}/{r['kind']}/{mark}] {','.join(r['nodes']) or '-'}  {r['detail'][:50]}")
scripts/lumos:5111:                g = agg.setdefault((r["ts"][:10], r["gate"], r["kind"]), {})
scripts/lumos:5115:                    r["_agg"] = (r["ts"][:10], r["gate"], r["kind"], nk)   # 首見佔位,維持時間軸位置
scripts/lumos:5137:            print(f"{r['ts'][:10]} [{r['gate']}/{r['kind']}/{mark}] {','.join(r['nodes']) or '-'}  {r['detail'][:50]}")
scripts/lumos:5152:            st[r["kind"]] = st.get(r["kind"], 0) + 1
scripts/lumos:5156:                tt[r["kind"]] = tt.get(r["kind"], 0) + 1
scripts/lumos:5167:        _sec = [r for r in can if r["kind"] == "second"]
scripts/lumos:5181:            if r["kind"] not in ("caught", "none"):
scripts/lumos:6102:                if isinstance(d, dict) and d.get("token") == ref_id and d.get("kind") != "second":
scripts/lumos:6184:    kinds = [r.get("kind") for r in recs]
scripts/lumos:6243:    caught_recs = [r for r in recs if r.get("kind") == "caught"]
scripts/lumos:6247:    none_recs = [r for r in recs if r.get("kind") == "none"]
scripts/lumos:6249:    missed = sum(1 for r in recs if r.get("kind") == "missed")
scripts/lumos:6434:    caught_recs = [r for r in latest if r.get("kind") == "caught"]
scripts/lumos:6435:    n_caught, n_missed = len(caught_recs), sum(1 for r in latest if r.get("kind") == "missed")
scripts/lumos:6436:    n_none = sum(1 for r in latest if r.get("kind") == "none")   # 停用制輪(d5)
scripts/lumos:6791:        gk = (d.get("gate"), d.get("kind"))
scripts/lumos:6991:            kind = d.get("kind")
scripts/lumos:7058:            if d.get("kind") not in ("caught", "missed"):
scripts/lumos:7075:            t[d["kind"]] += 1
scripts/lumos:7120:        if not isinstance(r.get("kind"), str):
scripts/lumos:7125:        return r.get("kind") in ("caught", "none") and bool(r.get("auditor"))
scripts/lumos:7135:        "kinds": [r.get("kind") for r in rounds],
scripts/lumos:7138:        "last": ({"kind": rounds[-1].get("kind"), "severity": rounds[-1].get("severity"),
scripts/lumos:7156:            if status == "unverified" or (e.get("kind") == "semantic" and status != "llm-ok"):
scripts/lumos:7202:        if e["kind"] not in ("mech", "semantic") or e["status"] not in ("unverified", "mech-ok", "llm-ok"):
scripts/lumos:7226:        return r.get("kind") in ("caught", "none") and bool(r.get("auditor"))
scripts/lumos:7235:        elif status == "unverified" or (e["kind"] == "semantic" and status != "llm-ok"):
scripts/lumos:7503:        if any(r.get("kind") in ("caught", "none") and r.get("severity") in ("major", "blocker") for r in rounds):
scripts/lumos:7512:        if last.get("kind") not in ("caught", "none"):
scripts/lumos:7540:        return r.get("kind") in ("caught", "none") and r.get("severity") in ("clean", "minor")
scripts/lumos:8472:    if light and any(r.get("kind") in ("caught", "none") and r.get("severity") in ("major", "blocker")
scripts/lumos:13043:            if e.get("hook") != hook_name or e.get("kind") != "ok":
scripts/lumos:15586:    ca = sum(1 for r in latest if r.get("kind") == "caught")
scripts/lumos:15587:    mi = sum(1 for r in latest if r.get("kind") == "missed")
scripts/lumos:15588:    nn = sum(1 for r in latest if r.get("kind") == "none")
scripts/lumos:17625:            if r["kind"] == "new_non_skippable":
scripts/lumos:19525:        print("  跑完不是看過就好:把固定席(帶合約/事故的那幾篇)的內容逐條貼進每一席的派工詞"
scripts/lumos:21584:    # 8.5 ranked 融合(階段三,spec §3):固定席(事故+含合約 direct+深度內合約 indirect)不占 top_k;
scripts/lumos:21592:            results.append({"node": x["node"], "kind": "incident", "pinned": True,
scripts/lumos:21617:                results.append({"node": x["node"], "kind": "direct", "pinned": pinned,
scripts/lumos:21633:                # 合約固定席 hop 上限(v1.2 旋鈕):合約密集圖(Landmark 考卷實證)hop2 合約
scripts/lumos:21640:                        lane_raw.append({"node": x["node"], "kind": "indirect", "pinned": False,
scripts/lumos:21644:                    results.append({"node": x["node"], "kind": "indirect", "pinned": True,
scripts/lumos:21653:                results.append({"node": x["node"], "kind": "indirect", "pinned": False,
scripts/lumos:21661:        pins.sort(key=lambda r: (r["kind"] != "incident", not r.get("about_hit", False)))
scripts/lumos:21690:        _free_direct = sum(1 for r in free if r["kind"] == "direct")
scripts/lumos:21695:                       if r["kind"] == "direct" and not r["pinned"] and id(r) not in _free_ids]
scripts/lumos:21743:                mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{r.get('hop','?')}"}.get(r["kind"], "")
scripts/lumos:21853:    聚合成「受影響功能面」manifest——固定席(合約/事故)全保、非固定取跨檔最高分 top-N。
scripts/lumos:21982:        mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{v.get('hop','?')}"}.get(v["kind"], "")
scripts/lumos:21995:    固定席(合約/事故/直接相依)優先、最多 cap 篇;hooks(pre-commit/pre-push/Stop)只呼叫,不自己重排。"""
scripts/lumos:22002:    print(f"  提醒:下面這些筆記跟改到的程式碼直接相關(合約 / 事故 / 直接相依),這批沒動:" if pinned
scripts/lumos:22681:            lines.append(f"- {it['rel']}" + (f" [{it['kind']}]" if it.get("kind") else "") + (f" ★{it['contract']}★" if it.get("contract") else ""))
scripts/lumos:22949:        listed.append({"node": node, "rel": rel, "kind": _LENS_KIND.get(v.get("kind"), None),
scripts/lumos:23122:        # 固定席=直接相依全部 + 事故全部 + 帶合約的一跳間接(與 --diff 的 pinned 語意對齊)
scripts/lumos:23139:        return (0 if v.get("kind") == _LENS_KIND["incident"] else 1 if v.get("contract") else 2 if v.get("kind") == _LENS_KIND["direct"] else 3)
scripts/lumos:23140:    listed = [{"node": n, **{"kind": "計劃連結", "contract": None, "files": []}, **pinned.get(n, {}), "kind": "計劃連結" + (f"+{pinned[n]['kind']}" if n in pinned and pinned[n].get("kind") else "")} for n in linked]   # 相容:不用 dict |(那是 3.9+,寫這行時專案宣告 ≥3.8;2026-09-06 宣告訂正為 ≥3.9,此寫法保留可用)
scripts/lumos:23245:            if ev.get("kind") not in ("passed", "skipped"):
scripts/lumos:23253:    return {"status": last.get("kind"), "head_sha": last.get("head_sha"),
scripts/lumos:23296:# 改到相依功能時,impact 固定席上的合約綁了什麼測試,在 code-loop check(pre-push 每次都呼叫)就真跑一遍;
scripts/lumos:23674:    # 固定席會是全庫合約——★正是設計明令要避免的「首推跑滿全部」那條稅★,
scripts/lumos:24124:            if ev.get("gate") == "code-loop" and ev.get("kind") == "dispositions" and ev.get("branch") == branch and ev.get("head_sha"):
scripts/lumos:25239:        elif intent["kind"] == "codex":
scripts/lumos:25940:    p = sub.add_parser("dispatch-lens", help="代碼審派工詞的固定席鏡頭:把 <base>..<head> 碰到的合約/事故節點整理成可附進派工詞的純文字(hook 用;內容從 base 讀,零自由文字)")

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "rg -n \"d4|丙\\(|r1 版|只加分不降級|事故路徑|降級=|r1 教訓|誰剔噪音|三輪達上限\" docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md | sed -n '1,180p'
rg -n \"snapshot_commit|--live-vault|預設把評測 vault|def pin_snapshot|LUMOS_EVAL\" governance/eval/retrieval_eval.py governance/eval/retrieval-goldset.json | sed -n '1,160p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
21:  - content: design-loop 三輪達上限未收斂,Enzo 裁甲:about_code 收窄為固定席排序+語意欄位基礎,不做降噪;降噪回扇出(A 層)另案。標題不改(保留 wikilink 與審計留痕),用定位段與 summary 標明
27:  - content: about-code-impl-std 三輪達上限未收斂,Enzo 裁乙:直接進實作,剩餘交給測試與代碼審(不再開第四輪)
34:    id: d4
35:    context: 調研實證甲案是死表:必看 15/69 坐固定席、事故恆最前,前 3 席組成幾乎不變,觀測一個月只會得到水平線;丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提
43:  KEY:★r2 設計層改動★——r1 版「有 about 欄但不含目標檔→降自由席」被實測打穿(事故筆記 hook卸載殘留註冊 改 test_lumos.py 時會被降;加上 about 對必看本有 2/9、3/5 漏標,降級=把必看踢出固定席,「零退化」在有欄節點上不成立)→改「只加分不降級」:about 命中→固定席前排,不命中→照三軸既有路徑。噪音剔除改由巨檔門檻與扇出承擔,about_code 不碰召回。另:回滾改新增子命令 about-code revert(既有 query 無 --field);過期判準改 git 最後改動日期(updated 欄 33% 落後;★此句已被 std-r2 換成正文雜湊,見下一行★)
62:> ★★2026-08-23 design-loop 三輪達上限未收斂,Enzo 裁「甲:收窄目標」★★
94:| **噪音** | 18 | 1 | 2.28 | 10 | 新指標:★裁乙改「輸出前 3 名必看命中率」`out_top3_must`★(甲案固定席版是死表,d4) | `retrieval_eval.py` | 接線照 `fusion_p`;歸因用總開關對照 |(✅ 2026-08-24 done,乙案首量 train 0.46/held 0.08) |
240:★r2 再改寫(s3f1/s3f2 blocker):r1 版「有欄但不含 → 降自由席」★會讓已標記的節點比沒標更差★★
242:r1 版的問題用實測打穿:`Issues/hook卸載殘留註冊`(事故類,`pitfall_when: content:HOOK_ENTRIES`)
243:改 `scripts/test_lumos.py` 時靠事故路徑無條件保送;但它的 about_code 只列 merge-claude-settings.py
245:**「改 A 出過事」的筆記不會列 B,但改 B 的人看到它不虧——事故路徑的價值正在這裡。**
517:1. **about_code 只加分不降級**——有欄無命中的節點,pinned 判定與現況逐 byte 相同。
542:**含意(2026-08-24 Enzo 裁乙,d4)**:指標改量「輸出前 3 名」(`out_top3_must`,不限固定席)。
576:20 條 findings,歸併九洞全折:**A 降級規則傷召回→改「只加分不降級」(設計層改動)**;
580:★r1 教訓:只改被點名的段落、沒全文 grep 分身——r2 三席有兩席抓的就是這個。★
585:**① 設計層(s2f1 blocker、s2f2/s2f3/s2f4 major)——r2 的「只加分不降級」救了召回,但把案子的目標救沒了**:
588:**席二原話:誰剔噪音?spec 沒人誠實說「現在沒人剔,只是排後面」。**
governance/eval/retrieval_eval.py:12:# LUMOS_EVAL_ROOT:測試/跨庫導向目標 repo(worktree 釘定的 git 根);預設=本體 repo
governance/eval/retrieval_eval.py:13:ROOT = Path(os.environ.get("LUMOS_EVAL_ROOT") or _SELF_ROOT)
governance/eval/retrieval_eval.py:17:_VENV = os.environ.get("LUMOS_EVAL_VAULT")
governance/eval/retrieval_eval.py:134:                        "--repo", os.environ.get("LUMOS_EVAL_REPO") or str(SNAP_ROOT or ROOT),
governance/eval/retrieval_eval.py:135:                        "--ranked", "--top", os.environ.get("LUMOS_EVAL_IMPACT_TOP", "50"),
governance/eval/retrieval_eval.py:253:def pin_snapshot(sha):
governance/eval/retrieval_eval.py:527:    _dump = os.environ.get("LUMOS_EVAL_DUMP_ROWS")
governance/eval/retrieval_eval.py:588:    路徑解析與寫入端同源:LUMOS_EVAL_HISTORY 優先(測試 fixture 帳,不污染真帳)。"""
governance/eval/retrieval_eval.py:589:    hp = Path(os.environ.get("LUMOS_EVAL_HISTORY")
governance/eval/retrieval_eval.py:705:    ap.add_argument("--live-vault", action="store_true", help="用現況 vault(預設釘 goldset snapshot;探索/漂移觀測用)")
governance/eval/retrieval_eval.py:737:        # 預設把評測 vault 釘在 goldset.snapshot_commit 的 worktree;--live-vault 才用現況(探索用)。
governance/eval/retrieval_eval.py:738:        _snap = args.snapshot or gs.get("snapshot_commit")
governance/eval/retrieval_eval.py:740:        # --live-vault/LUMOS_EVAL_VAULT 繞過釘定=用現況語料,帳面必須記 None(code-r1 bug 席 F2)。
governance/eval/retrieval_eval.py:742:        if _snap and not args.live_vault and not os.environ.get("LUMOS_EVAL_VAULT"):
governance/eval/retrieval_eval.py:745:                print(f"(語料釘定 snapshot={_snap};--live-vault 可用現況)")
governance/eval/retrieval_eval.py:862:        # LUMOS_EVAL_HISTORY:測試導向 fixture 帳,避免 e2e 測試污染真 history(code-r1 修)
governance/eval/retrieval_eval.py:863:        hist = Path(os.environ.get("LUMOS_EVAL_HISTORY")
governance/eval/retrieval-goldset.json:2: "snapshot_commit": "7fd214f",

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "rg -n \"lumos lint|lint \\"'$|cmd_lint'"\\(|home check|pre-commit\" scripts/hooks scripts | sed -n '1,260p'
rg -n \"lint.*staged|staged.*lint|changed.*\\.md|knowledge.*lint\" scripts/hooks/pre-commit scripts -g '*.py' -g '*.sh' | sed -n '1,260p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
scripts/hooks/pre-commit:6:# Git pre-commit hook — 圖譜同步硬擋 (L2)
scripts/hooks/pre-commit:12:#   永遠補不完,根因是「攔截點不對」。改放到 git pre-commit hook,git 內部
scripts/hooks/pre-commit:40:# 拿最終 staged (git 在 pre-commit 時 staged 已確定,-a/-am/path 都涵蓋)
scripts/hooks/pre-commit:91:# Gate L: staged 圖譜 .md 逐檔 lumos lint (2026-08-21 體檢 #6)
scripts/hooks/pre-commit:100:    # ★傳 vault 相對路徑、去 .md★——lumos lint 的精確比對鍵是 vault 相對的「Systems/foo」;
scripts/hooks/pre-commit:124:  "$CC_PY" "$REPO_ROOT/scripts/lumos" home check --staged --repo "$REPO_ROOT" || nh_rc=$?
scripts/hooks/pre-push:9:#   L2 pre-commit 只擋「污染指紋 + code 無圖譜」,不跑完整 doctor。
scripts/hooks/pre-push:63:# (2026-09-11 起「該動哪篇」的點名改由每支檔有家照家算——下面 home check --diff 會印;原本這裡以反引號為種子的
scripts/hooks/pre-push:198:    "$PY" "$GRAPHCTL" home check --diff "$_hrange" --repo "$REPO_ROOT" || nh_rc=$?
scripts/templates/graph-discipline.md:35:1. **同一次工作內寫回**：改了會影響行為 / 決策 / 驗證的 code，當次就把脈絡寫回圖譜（pre-commit 擋「改 code 沒動圖譜」）。設計、spec、計劃一律寫成 `Projects/<主題>_計劃` 筆記。
scripts/templates/graph-discipline.md:37:3. **寫完一篇 `lumos lint <節點>`，收工 `lumos doctor`**；push 前 pre-push 會再擋一次。改完程式先跑跟改動相關的測試子集，全套留給推送前的閘——全套要好幾分鐘，跑在對話裡會超時、也讓人等；子集怎麼跑看專案自己的說明。
scripts/hooks/pre-commit:6:# Git pre-commit hook — 圖譜同步硬擋 (L2)
scripts/hooks/pre-commit:12:#   永遠補不完,根因是「攔截點不對」。改放到 git pre-commit hook,git 內部
scripts/hooks/pre-commit:40:# 拿最終 staged (git 在 pre-commit 時 staged 已確定,-a/-am/path 都涵蓋)
scripts/hooks/pre-commit:91:# Gate L: staged 圖譜 .md 逐檔 lumos lint (2026-08-21 體檢 #6)
scripts/hooks/pre-commit:100:    # ★傳 vault 相對路徑、去 .md★——lumos lint 的精確比對鍵是 vault 相對的「Systems/foo」;
scripts/hooks/pre-commit:124:  "$CC_PY" "$REPO_ROOT/scripts/lumos" home check --staged --repo "$REPO_ROOT" || nh_rc=$?
scripts/hooks/pre-push:9:#   L2 pre-commit 只擋「污染指紋 + code 無圖譜」,不跑完整 doctor。
scripts/hooks/pre-push:63:# (2026-09-11 起「該動哪篇」的點名改由每支檔有家照家算——下面 home check --diff 會印;原本這裡以反引號為種子的
scripts/hooks/pre-push:198:    "$PY" "$GRAPHCTL" home check --diff "$_hrange" --repo "$REPO_ROOT" || nh_rc=$?
scripts/slim-gen.py:20:# delguard 2026-08-11 入列:消費端 pre-commit 已帶 Gate DG,slim 缺此命令=靜默死門
scripts/hooks/post-commit:9:#   L2 pre-commit 硬擋有合法後門 `--no-verify`,但走後門零痕跡——bypass 率
scripts/hooks/post-commit:11:#   關鍵事實:--no-verify 只跳過 pre-commit / commit-msg,post-commit 永遠會跑,
scripts/hooks/post-commit:19:# 判定邏輯與 scripts/hooks/pre-commit 完全對齊 (CODE_EXTS_RE / 排除規則 /
scripts/hooks/post-commit:30:# 找圖譜目錄 (對齊 pre-commit)
scripts/hooks/post-commit:45:# 本次 commit 的檔案清單 (quotePath=off 對齊 pre-commit 的中文路徑處理)
scripts/hooks/post-commit:49:# code 副檔名與排除規則 (對齊 pre-commit / check-graph-sync.py CODE_EXTS)
scripts/hooks/post-commit:67:    # vendored 工具白名單+源 repo 守門(與 pre-commit 完全對齊,2026-07-25):例行 lumos update
scripts/hooks/post-commit:68:    # 的 vendored .py 不該進 bypass 帳(pre-commit 已放行,這裡再記=假 bypass 灌水稀釋真訊號)。
scripts/hooks/post-commit:84:# 沒 code → 本來就會被 pre-commit 放行,不是 bypass
scripts/hooks/post-commit:9:#   L2 pre-commit 硬擋有合法後門 `--no-verify`,但走後門零痕跡——bypass 率
scripts/hooks/post-commit:11:#   關鍵事實:--no-verify 只跳過 pre-commit / commit-msg,post-commit 永遠會跑,
scripts/hooks/post-commit:19:# 判定邏輯與 scripts/hooks/pre-commit 完全對齊 (CODE_EXTS_RE / 排除規則 /
scripts/hooks/post-commit:30:# 找圖譜目錄 (對齊 pre-commit)
scripts/hooks/post-commit:45:# 本次 commit 的檔案清單 (quotePath=off 對齊 pre-commit 的中文路徑處理)
scripts/hooks/post-commit:49:# code 副檔名與排除規則 (對齊 pre-commit / check-graph-sync.py CODE_EXTS)
scripts/hooks/post-commit:67:    # vendored 工具白名單+源 repo 守門(與 pre-commit 完全對齊,2026-07-25):例行 lumos update
scripts/hooks/post-commit:68:    # 的 vendored .py 不該進 bypass 帳(pre-commit 已放行,這裡再記=假 bypass 灌水稀釋真訊號)。
scripts/hooks/post-commit:84:# 沒 code → 本來就會被 pre-commit 放行,不是 bypass
scripts/hooks/claude/check-graph-sync.py:590:    """跟 pre-commit/pre-push 同一條路:lumos impact --diff HEAD --sync-check --json(工作樹 vs HEAD),
scripts/hooks/claude/check-graph-sync.py:590:    """跟 pre-commit/pre-push 同一條路:lumos impact --diff HEAD --sync-check --json(工作樹 vs HEAD),
scripts/lumos:1190:             "鐵則修法見 lumos-project-notes skill; 污染指紋見 pre-commit Gate 1 指引")
scripts/lumos:2542:                 "③跑 lumos lint-check --smoke 驗它真的跑得動;接好之後 pitfalls 就會把它的告警"
scripts/lumos:2547:                 "修好 JSON;格式規範與真跑驗證:lumos lint-check --smoke")
scripts/lumos:2553:                 "逐條修宣告;工具是否真的跑得動用 lumos lint-check --smoke 驗")
scripts/lumos:2563:               "lumos lint-check --smoke")
scripts/lumos:4233:def cmd_lint(env, node):
scripts/lumos:12544:    print(f"  內容填完先檢查這一篇,再跑全圖健檢:\n    lumos lint {name}\n    lumos doctor\n  (寫法規範在 lumos-project-notes skill)")
scripts/lumos:12880:        print("teardown 將拆【當前 repo 專案層】(pre-commit/pre-push 閘、CLAUDE.md 注入、vendored 工具)")
scripts/lumos:12913:    """專案層反安裝(對稱 cmd_init):拆本 repo 的 pre-commit 閘 / vendored 工具組 /
scripts/lumos:13092:    """拆 pre-commit 閘:git -C root config --unset core.hooksPath。
scripts/lumos:13531:    "scripts/hooks/pre-commit",
scripts/lumos:14793:    預設並 vendor 工具組 + 裝 pre-commit/pre-push 閘(--no-hooks 只建圖譜輕量版)。
scripts/lumos:14837:            print("\n裝 hooks:vendor 工具組 + 啟用 pre-commit/pre-push 閘…")
scripts/lumos:14867:        print("  (已裝 pre-commit/pre-push 閘:改 code 沒更新圖譜會被擋)")
scripts/lumos:14903:    "scripts/hooks/pre-commit",
scripts/lumos:16156:    # ④⑤ git pre-commit / pre-push:core.hooksPath 指向 scripts/hooks 且檔存在可執行
scripts/lumos:16162:    for layer, fn in (("git-pre-commit", "pre-commit"), ("git-pre-push", "pre-push")):
scripts/lumos:17637:    """lumos lint-watch: 讀 .lumos/lint-watch.json、逐條查 registry、輸出 manifest。
scripts/lumos:17704:_NODEHOME_GOLIVE_MARK = "home check --staged"          # [S39] 提交前掛鉤裡有這串=這道檢查上線了
scripts/lumos:18146:                        tip or "HEAD", "--", "scripts/hooks/pre-commit")
scripts/lumos:18435:    """[S28][S29][S39] 健檢三段的母體與判定——跟 home check 共用同一套函式(需要家的檔、家、別人的檔)。
scripts/lumos:18493:    """lumos home check --staged | --diff A..B [S24]:有新違規 rc1,沒有 rc0;沒有圖譜/合併中/開關 off 說一句跳過、rc0。
scripts/lumos:18625:    notes 由呼叫端印到 stdout(走 stderr 會被 pre-commit hook 的 2>/dev/null 吞掉)。"""
scripts/lumos:18825:# ①建置產物:這份★必須與 pre-commit 的 should_exclude 逐項對齊★(既有漂移守衛在比),
scripts/lumos:18828:# ②散文與帳本:★只有 delguard 排,絕對不要複製到 pre-commit 的 should_exclude★
scripts/lumos:18830:#  抄進 pre-commit,結果 governance/ 底下 28 支真程式全部從「改 code 沒動圖譜就擋」的硬閘裡
scripts/lumos:18831:#  掉出去——兩份清單語意根本不同:delguard 那份是「哪裡不算活著的程式」,pre-commit 那份是
scripts/lumos:18839:# 與 pre-commit should_exclude 的 lock 排除規則對齊(`*package-lock.json|*yarn.lock|*pnpm-lock.yaml`)
scripts/lumos:18861:    以及 lockfile(package-lock.json/yarn.lock/pnpm-lock.yaml,與 pre-commit should_exclude 對齊)的檔案不抽 token,
scripts/lumos:18878:        # 而且 git grep 那側的 :(exclude)docs 本來就只排根目錄、pre-commit 寫的也是
scripts/lumos:19045:    commit 欄=當下 HEAD(pre-commit 時=上一個 commit),note 標 reason。"""
scripts/lumos:19062:    try:  # 亂設的 env 不該讓 pre-commit 印 traceback(fail-open 契約覆蓋設定錯誤)
scripts/lumos:19063:        deadline = float(os.environ.get("LUMOS_DELGUARD_DEADLINE", "15.0"))  # 5.0 在本 repo(377 篇+大 diff)仍常超,2026-08-27 一 session 降級多次→15;advisory fail-open,pre-commit 多等幾秒換掃完整
scripts/lumos:21868:        # 圖譜同步覆蓋(2026-08-22):pre-commit 要對「這次 commit 的內容」算波及,用 staged 代替 range
scripts/lumos:21995:    固定席(合約/事故/直接相依)優先、最多 cap 篇;hooks(pre-commit/pre-push/Stop)只呼叫,不自己重排。"""
scripts/lumos:25342:    "init": "新專案要用圖譜:建資料夾、.gitignore、pre-commit / pre-push。",
scripts/lumos:25361:    "enforcement": "各層防護現在到底有沒有生效(唯讀):hooks 註冊了嗎、pre-commit/pre-push 接了嗎、CI/anchor 在不在。",
scripts/lumos:25371:    "home check": "這次提交(--staged)或這段推送(--diff)有沒有「每支檔有家」的新違規;有就擋。",
scripts/lumos:25904:    p = sub.add_parser("init", help="在當前 repo 初始化圖譜(建資料夾+.gitignore,預設並裝 pre-commit/pre-push 閘)")
scripts/lumos:26030:    p = sub.add_parser("enforcement", help="各層防護現在有沒有生效(唯讀匯總:hooks/pre-commit/pre-push/CI/anchor/版本)")
scripts/lumos:26279:            print("擋下:lumos home check 要帶 --staged 或 --diff <起點>..<終點>", file=sys.stderr)
scripts/lumos:26370:        return cmd_lint(env, args.note)
scripts/test_lumos.py:3186:# ── pre-commit 閘:vendored 工具白名單豁免(lumos update 例行更新不該撞圖譜閘) ──
scripts/test_lumos.py:3188:    """fixture repo 內 stage 指定檔後跑 pre-commit hook,回 subprocess result。"""
scripts/test_lumos.py:3190:    hook = Path(GRAPHCTL).resolve().parent / "hooks" / "pre-commit"
scripts/test_lumos.py:3207:        raise _SrcOnly("非 POSIX(要 os.setsid 起 pre-commit),這段沒驗到")
scripts/test_lumos.py:3232:    """漂移守衛:pre-commit+post-commit 的豁免清單都必須涵蓋 _VENDORED_TOOLKIT 每項+兩夾+源守門
scripts/test_lumos.py:3235:    也要對齊 pre-commit should_exclude,免得兩處各自漂。"""
scripts/test_lumos.py:3241:    for hook in ("pre-commit", "post-commit"):
scripts/test_lumos.py:3249:    # delguard 排除域對齊 pre-commit should_exclude(第三份同源清單)
scripts/test_lumos.py:3250:    precommit_txt = (hooks_dir / "pre-commit").read_text(encoding="utf-8")
scripts/test_lumos.py:3253:        check(f"delguard 漂移守衛: 排除域 {d} 對齊 pre-commit should_exclude",
scripts/test_lumos.py:3255:    # ★跨檔斷言★:三個 lockfile 名都要出現在 pre-commit 的**那一行** lock 排除規則裡。
scripts/test_lumos.py:3259:    # 「判定邏輯與 pre-commit 完全對齊,兩邊不一致會產生幽靈 bypass 或漏記」,但這支漂移守衛
scripts/test_lumos.py:3260:    # 一直只比對 pre-commit,post-commit 漏同步不會有任何測試翻紅。這次補上。
scripts/test_lumos.py:3264:    check("漂移守衛: post-commit 的 should_exclude 與 pre-commit 逐字相同(不一致=幽靈 bypass)",
scripts/test_lumos.py:3268:        check(f"delguard 漂移守衛: lockfile {lf} 見於 pre-commit lock 排除行",
scripts/test_lumos.py:6035:    """體檢 #6(2026-08-21):`lumos lint` 從未被任何 hook/CI 呼叫——它的每條規則全靠人記得跑。
scripts/test_lumos.py:6036:    pre-commit 對 staged 的圖譜 .md 跑 lint,rc≠0 擋;乾淨節點放行。"""
scripts/test_lumos.py:6038:    hook = Path(GRAPHCTL).resolve().parent / "hooks" / "pre-commit"
scripts/test_lumos.py:6054:    check("pre-commit lint: 壞節點擋下(rc1)", r.returncode == 1, f"rc={r.returncode}\n{r.stdout}\n{r.stderr}")
scripts/test_lumos.py:6055:    check("pre-commit lint: 訊息指名 lint", "lint" in (r.stdout + r.stderr), r.stderr[-300:])
scripts/test_lumos.py:6058:    check("pre-commit lint: 乾淨節點放行(rc0)", r.returncode == 0, f"rc={r.returncode}\n{r.stderr[-300:]}")
scripts/test_lumos.py:6071:    check("pre-commit lint: 同檔名不同夾仍 lint 到 staged 的壞節點(rc1)", r.returncode == 1, f"rc={r.returncode}\n{r.stderr[-300:]}")
scripts/test_lumos.py:6080:    hook = Path(GRAPHCTL).resolve().parent / "hooks" / "pre-commit"
scripts/test_lumos.py:6804:                {"layer": "git-pre-commit", "status": "inactive", "detail": ""}]
scripts/test_lumos.py:6807:    check("提醒點名掉的層", line and "session-entry-hook" in line and "git-pre-commit" in line, str(line))
scripts/test_lumos.py:7597:    體檢 #7(2026-08-21):「什麼算 code 檔」有四份獨立清單(pre-commit/post-commit 的 bash regex、
scripts/test_lumos.py:7610:        "pre-commit": bash_set(root / "hooks" / "pre-commit"),
scripts/test_lumos.py:7619:    ref = lists["pre-commit"]
scripts/test_lumos.py:7622:        check(f"code-exts: {k} 與 pre-commit 一致", v == ref, f"{k}: +{sorted(v - ref)} -{sorted(ref - v)}")
scripts/test_lumos.py:7637:    for k in ("pre-commit", "post-commit"):
scripts/test_lumos.py:7646:    """README 審視 d1(2026-09-05):只改沒副檔名的主程式(如 scripts/lumos,首行 #!/usr/bin/env python3)、不帶節點 → 源 repo 內 pre-commit 要擋;
scripts/test_lumos.py:7650:        raise _SrcOnly("非 POSIX(要 os.setsid 起 pre-commit),這段沒驗到")
scripts/test_lumos.py:7651:    hook = Path(GRAPHCTL).resolve().parent / "hooks" / "pre-commit"
scripts/test_lumos.py:8339:    """造一個假 Lumos 來源:scripts/hooks(claude/impact-hook.py+pre-commit)+scripts/templates/graph-discipline.md。"""
scripts/test_lumos.py:8343:    (src / "scripts" / "hooks" / "pre-commit").write_text("#lumos\n")
scripts/test_lumos.py:8358:    (sc / "hooks" / "pre-commit").write_text("#!/bin/sh\n")
scripts/test_lumos.py:8389:    (tgt / "scripts" / "hooks" / "pre-commit").write_text("#lumos\n")
scripts/test_lumos.py:8396:    check("F9: lumos hook 檔被刪", not (tgt / "scripts" / "hooks" / "pre-commit").exists())
scripts/test_lumos.py:8412:    (tgt / "scripts" / "hooks" / "pre-commit").write_text("x")
scripts/test_lumos.py:8415:          (tgt / "scripts" / "hooks" / "pre-commit").exists())
scripts/test_lumos.py:8460:    (sc / "hooks" / "pre-commit").write_text("#!/bin/sh\nexit 0\n")
scripts/test_lumos.py:9011:                "scripts/hooks/pre-commit", "scripts/hooks/pre-push",
scripts/test_lumos.py:13529:    (work / "scripts" / "hooks" / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
scripts/test_lumos.py:13534:        "anchors": {"scripts/hooks/pre-commit":
scripts/test_lumos.py:13535:                    _h.sha256((work / "scripts" / "hooks" / "pre-commit").read_bytes()).hexdigest()},
scripts/test_lumos.py:13554:    for junk in (".DS_Store", "pre-commit.swp", "pre-commit~", "pre-commit.orig"):
scripts/test_lumos.py:14378:        # 2026-09-11 起推送前不再跑反引號為種子的同步點名(改由 home check --diff 照家算,Projects/每支檔有家_計劃 [S15])
scripts/test_lumos.py:17113:    # [delguard Task 7]pre-commit Gate DG 掛載＋排除域對齊斷言
scripts/test_lumos.py:17114:    hook = Path(GRAPHCTL).parent / "hooks" / "pre-commit"
scripts/test_lumos.py:17117:    check("delguard Gate DG 已掛 pre-commit", cond, "gate missing")
scripts/test_lumos.py:17121:        check(f"delguard 排除域對齊 pre-commit({d})", d.rstrip("/") in case_line, case_line)
scripts/test_lumos.py:27007:        for h in ("pre-commit", "pre-push"):
scripts/test_lumos.py:27060:    check("enforcement: pre-commit active", by.get("git-pre-commit") == "active", str(by))
scripts/test_lumos.py:27080:          by2.get("git-pre-push") == "active" and by2.get("git-pre-commit") == "active", str(by2))
scripts/test_lumos.py:27171:    check("enforcement: 缺 pre-commit inactive", by.get("git-pre-commit") == "inactive", str(by))
scripts/test_lumos.py:27191:    check("enforcement: 四 hook+pre-commit+pre-push+python+ci 共 8 active", n_active == 8, f"active={n_active} rows={[(r['layer'],r['status']) for r in rows]}")
scripts/test_lumos.py:27200:    # r1 審:別留 >=8 的鬆口,釘死列數(5 hook+pre-commit+pre-push+python+vendored+ci+anchor+required = 12;2026-09-03 加 dispatch-lens;
scripts/test_lumos.py:28220:    for f in ("hooks/pre-commit", "hooks/post-commit", "WINDOWS-NOTES.md"):
scripts/test_lumos.py:28223:    for f in ("hooks/pre-commit", "hooks/post-commit"):
scripts/test_lumos.py:31126:    (sc / "hooks" / "pre-commit").write_text("#!/bin/sh\n")
scripts/test_lumos.py:31147:    """delguard 不掃 governance/ 與 docs/,★但那兩夾絕對不能進 pre-commit 的硬閘豁免★
scripts/test_lumos.py:31156:    pre-commit 的 should_exclude 是「哪些檔改了不必配圖譜」。第一版為了滿足既有的漂移守衛,
scripts/test_lumos.py:31157:    把 governance/ 一起抄進 pre-commit,結果 governance/ 底下 28 支真程式全部從「改 code 沒動
scripts/test_lumos.py:31172:    case_line = [l for l in (hooks_dir / "pre-commit").read_text(encoding="utf-8").splitlines()
scripts/test_lumos.py:31174:    check("delguard: ★pre-commit 的硬閘豁免不得含 governance★(那底下有真程式,豁免=改 code 不配圖譜也放行)",
scripts/test_lumos.py:32685:    `exit 1`(pre-push 7 處、pre-commit 3 處)擋掉一次推送時,帳上完全看不出來。
scripts/test_lumos.py:32794:    修的是一個**現在就在講錯話**的東西:`lumos enforcement` 把 git-pre-commit 與
scripts/test_lumos.py:32811:        for fn in ("pre-commit", "pre-push"):
scripts/test_lumos.py:32837:            for layer in ("git-pre-commit", "git-pre-push"):
scripts/test_lumos.py:32851:        line = [l for l in r.stdout.splitlines() if "git-pre-commit" in l]
scripts/test_lumos.py:32860:        line = [l for l in r.stdout.splitlines() if "git-pre-commit" in l]
scripts/test_lumos.py:33418:            "governance/ai-governance-research.sh", "scripts/hooks/pre-push", "scripts/hooks/pre-commit"]
scripts/test_lumos.py:36708:    pc = (Path(GRAPHCTL).resolve().parent / "hooks" / "pre-commit").read_text(encoding="utf-8")
scripts/test_lumos.py:37221:    """[S25] 提交前掛鉤在逐篇格式檢查之後、「改程式沒動圖譜」之前呼叫 home check --staged;擋下就不提交;合併提交跳過。"""
scripts/test_lumos.py:37223:    hook_txt = (Path(GRAPHCTL).resolve().parent / "hooks" / "pre-commit").read_text(encoding="utf-8")
scripts/test_lumos.py:37224:    i_l, i_h, i_3 = hook_txt.find("# Gate L:"), hook_txt.find("home check --staged"), hook_txt.find("# Gate 3:")
scripts/test_lumos.py:37227:    check("②舊的反引號點名(impact --sync-only)不再被呼叫,改由 home check 照家算", not calls, str(calls))
scripts/test_lumos.py:37234:    rc, out = _nh_run_hook(root, "pre-commit")
scripts/test_lumos.py:37238:    rc, out = _nh_run_hook(root, "pre-commit")
scripts/test_lumos.py:37251:    rc, out = _nh_run_hook(root, "pre-commit")
scripts/test_lumos.py:37289:        return r.returncode, [l for l in lines if l.startswith("home check")], r.stdout + r.stderr
scripts/test_lumos.py:37307:    check("⑤home check 回 rc1 → 推送擋下,並講逃生路", rc == 1 and "node_home.gate" in out, out[-400:])
scripts/test_lumos.py:37347:    (root / "scripts" / "hooks" / "pre-commit").write_text('#!/bin/bash\nlumos home check --staged\n', encoding="utf-8")
scripts/test_lumos.py:37390:    """[S29] 健檢三段跟 home check 共用同一套函式(需要家的檔、家、別人的檔、讀快照)。"""
scripts/test_lumos.py:37411:    (root / "scripts" / "hooks" / "pre-commit").write_text("#!/bin/bash\nlumos home check --staged\n", encoding="utf-8")
scripts/test_lumos.py:37763:    (root / "scripts" / "hooks" / "pre-commit").write_text("#!/bin/bash\nlumos home check --staged\n", encoding="utf-8")
scripts/hooks/pre-commit:91:# Gate L: staged 圖譜 .md 逐檔 lumos lint (2026-08-21 體檢 #6)
scripts/test_lumos.py:845:    old_hash_changed = m.note_body_hash(root / "docs" / "k", "Systems/有改.md")
scripts/test_lumos.py:853:    check("★有改:第三段=標註當時雜湊,≠現在雜湊(之後 doctor 會列它)★", len(s_ch) == 3 and s_ch[2] == old_hash_changed and s_ch[2] != m.note_body_hash(root / "docs" / "k", "Systems/有改.md"), "/".join(s_ch))
scripts/test_lumos.py:6034:def t_precommit_lints_staged_graph_nodes():
scripts/test_lumos.py:6036:    pre-commit 對 staged 的圖譜 .md 跑 lint,rc≠0 擋;乾淨節點放行。"""
scripts/test_lumos.py:6059:    # ★同檔名不同資料夾(code-loop r1 s1 抓到):壞的 staged、好的已存在 → 必須 lint 到 staged 那個★
scripts/test_lumos.py:6071:    check("pre-commit lint: 同檔名不同夾仍 lint 到 staged 的壞節點(rc1)", r.returncode == 1, f"rc={r.returncode}\n{r.stderr[-300:]}")
scripts/test_lumos.py:16753:    check("cochange staged 漏改警告", any(x["changed"] == "A.md" and x["missing"] == "B.md" for x in w), str(w))
scripts/test_lumos.py:16771:    check("cochange --diff 漏改警告(母體到 range 左端)", any(x["changed"] == "A.md" and x["missing"] == "B.md" for x in w), str(w))
scripts/test_lumos.py:16777:    check("cochange 同給 --diff 優先(staged 空仍有警告)", any(x["changed"] == "A.md" for x in jload(r)["warnings"]), r.stdout)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md | sed -n '525,552p'
nl -ba docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md | sed -n '232,252p'
nl -ba docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md | sed -n '1,120p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
   525	5. **about 判定不覆寫 results 的 `hit` 欄**(impl-r1 s1f2;std-r2 s3f5 升格)——direct 候選的 `hit` 永遠是 body-inline-code/basename-match 來源標記。
   526	   [test 候選:#4 測試⑦]
   527	
   528	## ★調研:必看為什麼只有 8/29 坐固定席(2026-08-24,讀側落地後首查)★
   529	
   530	新指標「固定席前 3 位必看命中率」首量幾乎不動(有無 about 同值),追根究柢把 69 對「必看 × 編輯題」逐對驗了席位:
   531	
   532	| 席位 | 對數 | 說明 |
   533	|---|---|---|
   534	| direct 自由席 | **31(45%)** | ★結構性:全是計劃/驗證類——固定席保送條件=合約或事故,合約只有 Systems 類會標,計劃/驗證類必看**永遠**進不了固定席★ |
   535	| 不在輸出(無查詢文字診斷) | 19 | 抽 9 驗:6 個是門檻/名額截掉(無 query 時詞彙分=0、direct 底分 0.30 過不了動態閾;hook 實際有 query 會撈回部分——考卷實測只漏 3+2)、**3 個是真召回洞** |
   536	| 固定席(合約 direct 9 + 合約 indirect 3 + 事故 3) | 15 | 就是機械保證涵蓋的那面 |
   537	| indirect 自由席 | 4 | — |
   538	
   539	**三個真召回洞的形態**:筆記正文沒提那支檔的路徑、圖上距離 >2(例:自主迴圈的首輪驗證筆記沒寫 `autonomous-loop.sh` 字樣)。
   540	★這正是「影響欄位」(impacts_code,見下一步節)要接的洞——但也只有 3/69,不是主戰場。★
   541	
   542	**含意(2026-08-24 Enzo 裁乙,d4)**:指標改量「輸出前 3 名」(`out_top3_must`,不限固定席)。
   543	首量:train 0.463 / held 0.083 / 全體 0.281——held 爛在固定席噪音 82 條塞滿前三行,表是活的、直指 A 層降噪主戰場。
   544	甲案 pin_top3_must 作廢(history 舊 key 不沿用);丙無新證據不重提。原三選項留痕:
   545	1. 「前 3 席必看命中率」的天花板由「必看有幾個能坐固定席」決定(15/69);about_hit 只重排固定席內部,動不到 31 對自由席必看。
   546	   選項:(a) 接受——固定席=機械保證面,必看召回歸排序,把指標讀成「保證面內的排序品質」;(b) 指標改量「輸出前 3 名」不限固定席;(c) 開第四條保送——已在三輪設計審被拒(about 不是入口),重提要新證據。
   547	2. 31 對自由席必看靠詞彙分競爭——E05 那型(改評測腳本→該看檢索計劃)其實 query 詞彙訊號很強,實測也大多有進前 8(考卷 P@8 0.75);問題不是沒推出來,是「保證」與「推出來」是兩回事,講清楚就好。
   548	
   549	## 誠實缺口
   550	
   551	- **train split 只有 8 題、38 席固定席**,門檻是在這上面挑的,★過擬合風險高★。
   552	  held 照紀律不該反覆看——**落地前只驗一次**。
   232	
   233	### 讀側怎麼用(★r1 大幅改寫★)
   234	
   235	**r1 發現原設計打錯靶(s1f2/s1f3/s1f4 major、s2f1 blocker)**:固定席保送有★三條獨立路徑★——
   236	①`direct` + 合約(`scripts/lumos:14202` `pinned = bool(contract)`)②`indirect` + 合約且 hop≤1
   237	(`:14213`)③`incident`(事故類)不看合約一律保送(`:14178`)。原設計只改①。(行號 std-r1 s2f1 校正)
   238	**實測 E10 改 pre-push:8 席固定席只有 1 席是 direct,6 席是 indirect**——原修法字面上攔不到它們。
   239	
   240	★r2 再改寫(s3f1/s3f2 blocker):r1 版「有欄但不含 → 降自由席」★會讓已標記的節點比沒標更差★★
   241	
   242	r1 版的問題用實測打穿:`Issues/hook卸載殘留註冊`(事故類,`pitfall_when: content:HOOK_ENTRIES`)
   243	改 `scripts/test_lumos.py` 時靠事故路徑無條件保送;但它的 about_code 只列 merge-claude-settings.py
   244	與 lumos(它講的是卸載沒清乾淨,不是針對 test_lumos.py)。照 r1 規則 → 有欄但不含 → **被降**。
   245	**「改 A 出過事」的筆記不會列 B,但改 B 的人看到它不虧——事故路徑的價值正在這裡。**
   246	加上 about_code 對「必看」本就有 2/9、3/5 的漏標,降級規則會把那些必看項主動踢出固定席——
   247	★這是負向作用,「零退化」承諾在有欄的節點上不成立。★
   248	
   249	★改寫後的規則:about_code **只加分、不降級**★
   250	- 節點有 `about_code` 欄且含目標檔 → 標 **`about_hit: true`**;★前提:它已經由三條既有路徑之一進了候選集★
   251	  (沒字串提到、沒圖邊、不是事故觸發的節點,about_code 再命中也不會被掃到——about_code **不是第四條入口**,
   252	  只在既有候選裡重排;impl-r1 s1f3 抓到原句「不論它由哪條路徑進來」會被讀成獨立促升)。
     1	---
     2	type: project
     3	status: doing
     4	created: 2026-09-11
     5	updated: 2026-09-11
     6	tags:
     7	  - type/project
     8	  - status/doing
     9	  - scope/node-content
    10	related:
    11	  - "[[Projects/節點範圍與索引守衛_計劃]]"
    12	  - "[[Systems/節點範圍與索引守衛]]"
    13	decisions:
    14	  - content: 新規則被違反時:這次提交造成的新違規當場擋(提交前與推送前),提交前就存在的舊帳只在健檢提醒
    15	    id: d1
    16	    context: 客人網頁在合約條數提醒、格式檢查、健檢全綠之下又長成一篇包全部;之前那三道範圍檢查刻意選只提醒不擋,理由是擋了人會學會跳過。Enzo 2026-09-11 把節點範圍列最優先,問擋或提醒。
    17	    why_chosen: 只提醒的那三道就是這次全綠長歪的條件;全部都擋的話七個圖譜幾乎立刻被擋、要先整理完才能提交任何東西。只擋新違規的量很小、補法都是一行指令,舊帳分批還(借 diff-cover 只看這次改到的行的做法)。Enzo 選。
    18	    decided: 2026-09-11
    19	    valid: true
    20	  - content: 節點照「每支檔有家、規格寫明落點」切:每篇一句負責範圍加它管哪幾支檔,每支程式檔都要有家;不採一份規格一篇、也不採模組層加功能層兩層
    21	    id: d2
    22	    context: Enzo 問節點失控是否跟即興開發有關、之前是一個功能一個規格文件展開的。三種切法攤給 Enzo:檔有家+寫明落點/一份規格一篇/兩層。
    23	    why_chosen: 改檔時一定推得出它的家,推筆記的算法不用改;一份規格一篇會讓同一支檔的現況散在好幾篇、後來的功能改到前一個功能的規則時要同步改兩篇;兩層多一套「這句放哪層」的規則。規格寫明落點時可以選新開一篇,一份規格一篇的好處可逐案取用。Enzo 選。
    24	    decided: 2026-09-11
    25	    valid: true
    26	  - content: 改到提交前就沒有家的舊檔只提醒、不擋;擋的只有新增的檔沒家、以及這次讓原本有家的檔變沒家
    27	    id: d3
    28	    context: 設計初稿(Enzo 已核可)寫的是改到沒家的舊檔也擋。寫計劃時量兩個舊 Android 消費專案:40 篇與 30 篇節點全都沒填 about_code,程式檔 100% 沒家。
    29	    why_chosen: 照初稿等於那兩個專案每個提交都擋,跟 Enzo 選的「舊的提醒」相衝。不會變成漏洞:要往圖譜寫說明時規則三(寫回要落在改動檔的家)沒有家可落,會自然逼出建家。已向 Enzo 說明並請他有異議就改回。
    30	    decided: 2026-09-11
    31	    valid: false
    32	    superseded_by: d4:有寫回時改到的檔都要先有家(設計審 r1)
    33	    ended: 2026-09-11
    34	  - content: 改到之前就沒家的舊檔:這次沒有任何 Systems 節點內容有變只提醒;有節點內容有變時,每支改動的需要家的檔都要先有家(規則三 S13b)
    35	    id: d4
    36	    context: 設計審 r1 正確性席(blocker):規則三只要求被寫的節點是「某一支」改動檔的家,規則二只看反引號;順帶改到一支有家的檔,就能把其他沒家檔的說明用散文塞進同一篇——正是客人網頁長歪的方式,d3 的「舊檔只提醒」讓這條路完全通。
    37	    why_chosen: 只在要往圖譜寫說明時才要求改到的檔先安家:沒寫說明的提交照舊只提醒,兩個舊 Android 專案改到舊檔的提交不會每個都擋(d3 要防的仍然防得住;新增的檔從上線那天起就要有家是規則一 [S3] 刻意的,不在這條決策範圍,第二輪回滾席指出原句會被讀成「舊專案都不會被擋」);寫說明時每次只要求改到的那幾支,是舊帳分批還。
    38	    decided: 2026-09-11
    39	    valid: true
    40	  - content: 推送前把這次要推的範圍整段比一次(跟既有每一個 --diff 指令同一個慣例),不逐個提交比;新分支的起點用「不在任何遠端分支上的提交」裡最早那一個的上一個提交,不沿用空樹兜底
    41	    id: d5
    42	    context: 設計審 r1 多席獨立指出:逐個提交是全新機制,既有 --diff 全是端點比;推送前掛鉤的空樹兜底在新分支首推時會把整段歷史(本工具鏈 1913 個提交)當成新改動;逐檔讀歷史版本一個提交要秒級。
    43	    why_chosen: 推送前要接住的是「跳過提交前檢查的」:整段比看的是推上去之後的結果比推之前多了什麼違規,中間提交自己修好的本來就不該擋;合併進來的內容一起算,不必跳過合併提交。代價:中間某個提交的寫回落點錯、後一個提交又讓它合規時分不出來——結果合規就不擋,可接受。
    44	    decided: 2026-09-11
    45	    valid: true
    46	lands_in:
    47	  - Systems/每支檔有家
    48	  - Systems/design-loop
    49	  - Systems/節點範圍與索引守衛
    50	---
    51	# 每支檔有家_計劃
    52	
    53	> 白話：每支程式檔都要有一篇「管它的」節點；節點只准寫自己管的檔，別人的一律用連結；程式改了，說明要寫進改到那支檔的那一篇，而且要往圖譜寫說明，改到的每支檔都得先有家；計劃寫明現況要落在哪一篇。新加的違規當場擋，舊帳只提醒；整道閘有專案層級的開關。
    54	
    55	## 為什麼（這批的來源）
    56	
    57	2026-09-11 對三個 POS 消費專案做節點健檢，客人網頁那個專案**又長成一篇包全部**——距離後端第一次長歪、拆開、加上合約條數提醒，不到兩天。
    58	
    59	- 客人網頁 9/10 15:15 出生就只有一篇（客人端決策層），摘要的依賴行用反引號列了四支別的程式檔；之後吃完再結、外帶兩個功能都寫回同一篇：說明行 9→11、全文 47→96 行、掛 3 份計劃。13 支程式檔只有 1 支是它正式管的（about_code），3 支靠依賴行順帶連上，其餘 9 支（8 支畫面加入口檔）改的時候不會推出任何筆記——依賴行寫的是資料夾路徑，波及計算對不到任何檔。
    60	- 篇內還留著翻案前的殘渣：流程行與一段正文寫「開場會去讀這桌已經點了什麼」，那條路 9/10 就拿掉了，同一篇的合約自己寫「沒有讀單的路」（程式與一個乾淨查證員兩邊對過）。
    61	- POS 平板：7 支程式檔沒有任何節點提到（6 支是畫面），另 5 支只被別篇順帶提到；後端：9 篇裡 6 篇的依賴行寫了別人的檔，伺服器裡「客人的路只准這幾條」的合約，改伺服器那支檔時不會被推出來。
    62	
    63	**沒有哪道檢查失效，是沒有檢查量這個形狀**（兩個來源對過：自己讀碼＋乾淨查證員讀碼）：
    64	
    65	1. 合約條數提醒只數合約（門檻 10，提醒不擋）；它原本的「提到 ≥3 支檔」在設計審被拿掉並寫成合約「不看提到幾個檔」（[[Systems/節點範圍與索引守衛]]）。
    66	2. 依賴行的內容沒有任何檢查；「一支檔一個家、別人的用連結」只寫在私人記憶與那道提醒的文字裡（合約破 10 條才看得到），教寫節點的說明裡沒有，在消費專案開的會談讀不到。
    67	3. 提交前「改程式要動圖譜」只看有沒有動任何一篇；旁邊「該動哪篇」的點名以反引號命中的節點為種子，再加連結擴散與文字相似度排序——在客人網頁，種子永遠是那篇大雜燴。**工具在把人往那篇推。**
    68	4. 改檔前推「必看筆記」只認正文反引號路徑，about_code 只加分（[[Projects/固定席扇出降權_計劃]] 的裁定）；不會提醒「這篇管很多檔」。
    69	
    70	**跟即興開發的關係（Enzo 問）**：加速器，不是根。POS 每個功能都有規格與設計審；lumos 自己一份份規格做出來，核心節點照樣累積——[[Systems/design-loop]] 摘要有 32 行 KEY、全文 176 行，KEY 行標的日期橫跨 7–9 月二十幾天、正文連到 14 份計劃（2026-09-11 量），只是合約 1–2 條、提醒從沒響。缺的是「規格寫明現況落在哪一篇」這一步，以及寫回時落對篇的機械檢查。
    71	
    72	## 世界上怎麼做的
    73	
    74	PRIOR-ART: ① 最小解層級——about_code 欄位、改檔前推筆記的抽取、工具自裝檔判定、測試地圖的測試檔判定、處置閘「照首筆帳日期生效」、提交前掛鉤呼叫 lumos 子指令的形狀、效能檢核閘的專案開關都已存在，這案是把它們接成一道「寫的當下」的閘，不新增依賴。② 世界解過沒——「每支檔對應負責人」是 GitHub CODEOWNERS，它的驗證工具 codeowners-validator 有專抓「沒人負責的檔」的 notowned 檢查（實驗功能）；「只對新增的部分嚴格、舊的慢慢還」是 diff-cover 只檢查這次改到的行的做法；「只能透過宣告過的介面引用別的模組」是 Nx 的 enforce-module-boundaries 規則。③ 裁定：借這三個形狀自建（零依賴家規）；負責人表不另開一份檔，直接用每篇節點既有的 about_code，避免兩份來源漂移。
    75	
    76	## 名詞
    77	
    78	- **需要家的檔**：專案自己的程式檔。四個條件都要成立：
    79	  1. 受版控，而且在提交索引或提交裡的檔案模式是一般檔（100644 或 100755）——連結檔（120000）與子模組（160000）不算；模式從 `git ls-files -s`（提交前）與 `git ls-tree -r`（推送前）讀，跟既有程式碼在算「受版控一般檔」時同一種判法。
    80	  2. 是程式檔：副檔名在「改程式要動圖譜」那道閘的清單裡，或沒有副檔名而首行是 `#!`。那份清單現在是四份副本（提交前、提交後兩支掛鉤，Claude 端兩支掛鉤）由一支一致性測試釘住；lumos 主程式新增**第五份同內容的具名常數**，並把它接進那支一致性測試（擴成五份一致），不另起一套判法，也不借用主程式裡另一份內容不同、給符號查核用的副檔名表。
    81	  3. 不在排除清單：docs/ 與建置輸出夾（跟提交前那道閘的排除表同一份）、測試檔（見下）、lumos 自己裝進去而且內容沒改過的檔（內容指紋判定；在 lumos 來源 repo 不排除，跟提交前那道閘同一條規則）、專案設定 `node_home.ignore` 列的樣式。
    82	  4. 檔名是合法 UTF-8：圖譜筆記是 UTF-8 文字，寫不進那種路徑，所以這種檔永遠不算需要家的檔，只在健檢提醒「建議改名或加進 ignore」。
    83	- **測試檔**：用測試地圖那一支判定；副檔名不在它清單裡的程式檔（例如 shell、Go、Rust、C/C++），套它同一組目錄與檔名規則——路徑裡有 tests／test／__tests__／spec／specs 這一層目錄、檔名含 `.test.` 或 `.spec.`、主檔名以 `test_` 開頭、或以 `_test`／`_tests`／`_spec`／`_specs` 結尾（例：Go 的 `foo_test.go`）。
    84	- **`node_home.ignore`**：字串清單；每一項是比對 repo 相對路徑的 glob，語法跟既有共改排除樣式那一支相同（`fnmatch`，`**/` 開頭的另外去掉前綴再試一次，才吃得到根目錄的檔）；非清單、或清單裡不是字串的項，那一項略過並出聲，其餘照用。
    85	- **家**：狀態是 doing、done 或 stale 的 Systems 節點，about_code 列了這支檔。
    86	  - planned、deferred 還沒成為現況，rejected、superseded 已經不是現況——這四種都不算家。stale（回頭條件到期待重驗）照樣是家：它仍然是那支檔的說明，只是該重看了。
    87	  - 比對用字面比對鍵（路徑正規化＋NFC），★不讀磁碟★——about_code 寫入時已經照磁碟校正過（解連結、大小寫、Unicode 寫法）；推送一個不是目前 checkout 的分支時，磁碟上的拼法跟那個提交對不上，照磁碟比會把同一個提交裡順手改好的大小寫改名誤判成沒家（第二輪實跑重現）。
    88	  - **只看欄位值，不看 about_code 的預標指紋有沒有過期**：那個指紋在正文一改就過期，而規則三要求寫回、寫回就會改正文——看指紋的話，每次合規的寫回都會讓家消失；另外 `lumos new` 建的節點本來就沒有指紋。那個指紋管的是「預標的品質」，不是「宣告」。
    89	  - Issues 的 about_code 不算家——事故筆記本來就該被推，但它不是現況的歸屬。
    90	  - 一支很大的檔可以有好幾個家（後端訂單檔本來就分狀態、訂單列、保存三篇）。
    91	- **別人的檔**：節點正文或摘要裡用反引號寫、改檔前推筆記那套抽取會認成某支需要家的檔，而那支不在這篇的 about_code 裡。
    92	- **內容有變**：兩個版本之間，摘要、決策、正文三者任一不同（逐欄比對兩個版本解析後的值）；其他開頭欄位（verified_by、plan_refs、related、tags、aliases、updated、status 等）的變動算簿記。★不沿用既有只算正文的那支雜湊★——摘要與決策都在開頭欄位裡，那支雜湊看不到，而節點長大主要就長在摘要。
    93	- **讀哪個版本**：提交前一律讀提交索引裡的版本（節點與程式檔都是），不讀工作目錄——同一個工作目錄另一個會談寫到一半、還沒加進索引的東西不會被讀到；推送前讀範圍兩端的提交。讀法：跟磁碟一樣的直接讀磁碟，不一樣的那幾支才用既有的 `git show` 包裝一支一支讀；推送前的起點那一側只讀這段範圍裡有變動的節點，其餘跟終點那一側共用。設定（`.lumos/config.json`）、工具自裝檔的內容指紋、圖譜位置也從同一個版本讀——工作目錄裡沒暫存的「關掉」關不掉提交索引的檢查。★不另寫批次讀取★——這個 repo 的架構審查曾把另寫一套批次讀取判成「第二種做法」退回（工具自裝檔判定那一段的註解有記）。
    94	- **新違規**：這次提交（或這次推送的整段範圍）造成的違規，跟之前比多出來的；之前就存在的叫**舊帳**。
    95	
    96	## 核心裁定
    97	
    98	### 規則一：每支檔都要有家
    99	
   100	- [S1] 「需要家的檔」照上面的定義；程式檔判定用主程式新增的第五份清單，並接進既有的一致性測試（五份一致）。 [test:t_nodehome_required_files_definition]
   101	- [S2] 「家」照上面的定義：狀態只認 doing、done、stale；只看 about_code 欄位值、不看預標指紋；比對用字面比對鍵、不讀磁碟。 [test:t_nodehome_home_definition] [test:t_nodehome_other_branch_rename_uses_commit_spelling]
   102	- [S3] **擋**：這次新增（含改名成新路徑，以及這次才變成需要家的檔：捷徑檔換成真的程式檔、沒副檔名的檔補上 #!——git 標的是 T 或 M 不是 A）的需要家的檔，之後沒有家。同一個提交裡順手建家就過。 [test:t_nodehome_check_blocks_new_homeless_file] [test:t_nodehome_newly_required_file_counts_as_new]
   103	- [S4] **擋**：這次讓一支原本有家的檔變成沒家——從 about_code 拿掉、家那篇被刪、或家那篇的狀態改成 planned、deferred、rejected、superseded。改成 stale 不算。 [test:t_nodehome_check_blocks_home_removal]
   104	- [S5] 改到之前就沒家的舊檔：這次沒有任何 Systems 節點內容有變 → **只提醒**；有 → 照規則三的 [S13b] 擋（決策 d4）。 [test:t_nodehome_touched_legacy_homeless_warns_without_write_back]
   105	- [S6] 擋下的訊息把沒家的檔依資料夾分組，每組附候選家（同資料夾其他檔的家、正文提到它的節點）與可以直接改的指令樣板（新開一篇帶 `--code` 與 `--responsibility`；或加進確實在講它的那篇）；最多列 10 支，超過印「還有 N 支」，跟既有「改程式沒動圖譜」那道擋下訊息同一個上限。 [test:t_nodehome_check_message_groups_and_truncates]
   106	- [S34] **新專案出生**：剛接上 lumos 的專案第一個加程式的提交，每支檔都是新增，全部要有家——這是刻意的：節點怎麼切在出生那一刻就要決定，這次事故就是出生時只建一篇。訊息照 [S6] 分組、給樣板。 [test:t_nodehome_birth_commit_requires_homes]
   107	
   108	### 規則二：節點只准用反引號寫自己家的檔
   109	
   110	- [S7] 只看 Systems 節點。「這篇寫到哪支檔」的抽取**重用改檔前推筆記那一支**（完整路徑＋在受版控檔裡唯一的裸檔名），不另寫一套——兩套算法一定分岔，而分岔時沒有東西會翻紅。 [test:t_nodehome_foreign_ref_uses_impact_extraction]
   111	- [S8] 只有需要家的檔算「別人的檔」；測試檔、非程式檔、工具自裝檔寫了照舊可以。裸檔名在受版控檔裡不唯一時，推筆記那支不認它、也就不會因此把這篇推給那支檔，所以不算認領——這條規則要防的正是「節點變成別人檔的入口」。 [test:t_nodehome_foreign_ref_definition]
   112	- [S9] **擋**：這篇之後比之前多出來的別人的檔（這次新開的節點＝全部都算新）；另外，這次新增的檔如果讓一篇沒改的節點原本就寫著的檔名變成別人的檔，也算這次的新違規（那篇從這次起就是那支檔的入口）；那篇這次沒改、同一個提交裡改它又會被規則三擋，所以擋下訊息要講明「另開一個只改筆記的提交先改它」，並分「原本就在講這支檔→改寫成連結」與「只是剛好同名→把檔名改寫掉」兩種改法。已經寫在裡面的舊檔名只提醒。 [test:t_nodehome_check_blocks_new_foreign_ref] [test:t_nodehome_new_file_awakens_foreign_ref]
   113	- [S10] 訊息指出是哪支檔、它的家是哪篇，建議改寫成節點連結；那支檔沒家就指回規則一。 [test:t_nodehome_foreign_message_points_to_home]
   114	
   115	### 規則三：寫回要落在改動檔的家
   116	
   117	- [S11] 只在這次改了（含刪掉、改名）需要家的檔時生效；純圖譜提交（整理節點、補家）不受這條管。推送前整段比時規則三逐個提交看：只看同一個提交裡也改了程式的節點、配那個提交改的檔——不然一次推送裡「改程式的提交」加「純整理節點的提交」會被混在一起誤擋（[S13b] 同理）。★「那篇內容有沒有變」也逐個提交算★：內容是前一個純整理提交改的、改程式的提交只替它補簿記欄位，不算後者寫回（2026-09-11 平板 POS 第一次真推送踩到，原本拿整段頭尾比）。 [test:t_nodehome_route_skips_docs_only_commit] [test:t_nodehome_route_counts_deleted_files] [test:t_nodehome_diff_route_per_commit] [test:t_nodehome_diff_route_counts_content_per_commit]
   118	- [S12] 「內容有變」照上面的定義（摘要、決策、正文逐欄比對；決策比解析後的值，只改引號這種等價寫法不算）；簿記欄位的變動不算。 [test:t_nodehome_route_content_change_definition] [test:t_nodehome_decisions_compared_by_value]
   119	- [S13] **擋**：內容有變、而且狀態能當家（doing、done、stale）的每一篇 Systems 節點（含這次新開的），之後必須是某支改動檔的家；刪掉的檔看它刪之前的家。作廢、否決、還沒成為現況的節點寫說明不受這條管（它們不是現況，寫進去不會長成大雜燴）；被刪的節點由 [S4] 管。 [test:t_nodehome_check_blocks_write_back_to_non_home]
   120	- [S13b] **擋**：只要有任何 Systems 節點內容有變，每支改動的需要家的檔之後都要有家——這是提交層級：只要有一篇內容有變，這次改到的每支檔都要有家，跟那篇講什麼無關。這堵的是「順帶改到一支有家的檔，就把別的沒家檔的說明用散文塞進同一篇」——規則二只看得到反引號，看不到散文，而這正是客人網頁長歪的方式。 [test:t_nodehome_write_back_requires_every_changed_file_homed]

[2mcontext compacted[0m
[35m[3mexec[0m[0m
[1m/bin/zsh -lc "rg -n \"ANCHOR_FILES|scripts/test_lumos.py|impact-hook.py|dispatch-lens-hook.py\" scripts/lumos docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md docs/lumos-toolchain-knowledge/Verification/2026-08-24_about_code讀側四項落地.md && nl -ba docs/lumos-toolchain-knowledge/Verification/2026-08-24_about_code讀側四項落地.md | sed -n '1,180p' && python3 scripts/lumos stale --candidate --match about_code"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 228ms:[0m
Verification/2026-08-24_about_code讀側四項落地.md [pass]
    ↳ goldset 快照前進到含 about_code 的 commit 後重跑(屆時「固定席前 3 必看命中率」才是有 about 的數字);LUMOS_IMPACT_ABOUT_M…
Verification/2026-09-11_每支檔有家落地.md [pass]
    ↳ 改到 _nodehome_ 開頭的函式、cmd_home_check、提交前或推送前掛鉤裡每支檔有家那一段、about_code 的寫入檢查、測試地圖或工具自裝檔判定;或第一次在真…

2 篇 revalidate_when 提到『about_code』→ 逐一判斷是否需重驗(`lumos set <篇> status stale`)。

[35m[3mcodex[0m[0m
我已核出兩個關鍵分歧：新版確實避免了舊案「降權導致漏召回」的失敗，但它拿來重啟舊決策的「漏標率歸零」證據，和舊案所量的 must-see 漏洞不是同一個母體。接著我在收斂可執行性與回滾證據，會把每個固定席逐一判完。
[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/lumos | sed -n '14900,14916p;17735,18015p;21245,21300p;21580,21765p;21835,22015p;23045,23150p' && nl -ba scripts/hooks/claude/impact-hook.py | sed -n '610,670p' && nl -ba governance/eval/retrieval_eval.py | sed -n '270,300p;430,485p;530,560p;690,755p' && nl -ba governance/review-reports/推筆記認家/r1-snapshot.md | sed -n '1,120p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
 14900	ANCHOR_FILES = [
 14901	    "scripts/test_lumos.py",
 14902	    "scripts/test_autonomous_loop.py",
 14903	    "scripts/hooks/pre-commit",
 14904	    "scripts/hooks/pre-push",
 14905	    "scripts/hooks/post-commit",
 14906	    "scripts/hooks/claude/dispatch-lens-hook.py",   # 2026-09-03 派工鏡頭注入:會改寫子代理派工詞的 hook,硬約束進錨點
 14907	    # ★2026-09-06 全 repo 審視 #6:其餘四支 hook 補進來★
 14908	    # 它們跟上面那支一樣是「你一打開資料夾就自動跑」的程式,以前完全沒有東西盯著:
 14909	    # 內容被改、或偷偷多一支,anchor verify 一句話都不說。
 14910	    "scripts/hooks/claude/lumos-entry-hook.py",     # 進場時注入紀律提醒 + 查各層防護
 14911	    "scripts/hooks/claude/impact-hook.py",          # 改檔前把牽連的合約推到眼前
 14912	    "scripts/hooks/claude/check-graph-sync.py",     # 收工檢查圖譜有沒有跟上
 14913	    "scripts/hooks/claude/ci-status-hook.py",       # 推送後回報 CI 狀態
 14914	    # ★2026-09-08 #19 S4:五支 hook 共用的事件寫入器★——它被那五支 import、
 14915	    # 而且會跟著複製到 ~/.claude/hooks/,所以它也是「一打開資料夾就自動跑」的程式的一部分。
 14916	    # 漏登記的話 anchor verify 會直接擋推送(r1 架構對齊席當場重現),而那道★永遠不可跳★。
 17735	        except Exception as e:
 17736	            cfg["warnings"].append(f".lumos/config.json 讀不了({e.__class__.__name__}),每支檔有家用預設(會擋、上限 {_NODEHOME_MAX_FILES_DEFAULT} 支、不額外排除)")
 17737	            return cfg
 17738	    try:
 17739	        data = json.loads(raw)
 17740	    except Exception as e:
 17741	        cfg["warnings"].append(f".lumos/config.json 讀不了({e.__class__.__name__}),每支檔有家用預設(會擋、上限 {_NODEHOME_MAX_FILES_DEFAULT} 支、不額外排除)")
 17742	        return cfg
 17743	    nh = data.get("node_home") if isinstance(data, dict) else None
 17744	    if nh is None:
 17745	        return cfg
 17746	    if not isinstance(nh, dict):
 17747	        cfg["warnings"].append("設定檔的 node_home 不是物件,整段用預設")
 17748	        return cfg
 17749	    g = nh.get("gate", "on")
 17750	    if g not in _NODEHOME_GATE_VALUES:
 17751	        cfg["warnings"].append(f"設定檔的 node_home.gate={g!r} 看不懂(只認 {'/'.join(_NODEHOME_GATE_VALUES)}),已用 on")
 17752	    else:
 17753	        cfg["mode"] = g
 17754	    mf = nh.get("max_files", _NODEHOME_MAX_FILES_DEFAULT)
 17755	    # ★bool 要單獨擋★:Python 的 True 是 int 的子類,不擋的話上限悄悄變成 1(同合約條數門檻那支)
 17756	    if isinstance(mf, bool) or not isinstance(mf, int) or mf < 1:
 17757	        cfg["warnings"].append(f"設定檔的 node_home.max_files={mf!r} 不合法(要 1 以上的整數),已用 {_NODEHOME_MAX_FILES_DEFAULT}")
 17758	    else:
 17759	        cfg["max_files"] = mf
 17760	    ig = nh.get("ignore", [])
 17761	    if not isinstance(ig, list):
 17762	        cfg["warnings"].append("設定檔的 node_home.ignore 要是字串清單,整段略過")
 17763	    else:
 17764	        for i, item in enumerate(ig):
 17765	            if isinstance(item, str) and item.strip():
 17766	                cfg["ignore"].append(item.strip())
 17767	            else:
 17768	                cfg["warnings"].append(f"設定檔的 node_home.ignore 第 {i + 1} 項不是字串({item!r}),略過這一項")
 17769	    return cfg
 17770	
 17771	
 17772	def _nodehome_resp_ok(value):
 17773	    """[S16] 負責範圍:至少 10 個字、要有實字(全標點、空白視同沒寫)。實字判準同 [manual:] 那條。"""
 17774	    if not isinstance(value, str):
 17775	        return False
 17776	    v = value.strip()
 17777	    return len(v) >= _NODEHOME_RESP_MIN_CHARS and bool(re.search(r"[^\W_]", v))
 17778	
 17779	
 17780	def _nodehome_is_test(path):
 17781	    """測試檔判定:先問測試地圖那一支;副檔名不在它清單裡的(shell、Go、Rust、C…),套它同一組目錄與檔名規則。"""
 17782	    global _TESTMAP_DIR_RE
 17783	    if _testmap_is_test(path):
 17784	        return True
 17785	    if _testmap_ext(path) in _TESTMAP_EXTS:
 17786	        return False                      # 測試地圖認得這種副檔名,它說不是就不是
 17787	    if _TESTMAP_DIR_RE is None:
 17788	        _TESTMAP_DIR_RE = re.compile(r"(^|/)(tests?|__tests__|specs?)/", re.IGNORECASE)
 17789	    if _TESTMAP_DIR_RE.search(path):
 17790	        return True
 17791	    name = path.rsplit("/", 1)[-1]
 17792	    stem = _testmap_stem(path)
 17793	    return (".spec." in name or ".test." in name or stem.startswith("test_")
 17794	            or stem.lower().endswith(("_tests", "_specs", "_test", "_spec")))   # 底線變體同測試地圖(Go 的 foo_test.go)
 17795	
 17796	
 17797	def _nodehome_code_kind(path):
 17798	    """回 'ext'(副檔名在清單裡)/'shebang?'(沒副檔名,要看首行)/None(不是程式檔)。
 17799	    副檔名判法照提交前掛鉤那條正則:大小寫敏感、看最後一個點之後;沒副檔名=去掉開頭所有點之後沒有點。"""
 17800	    base = path.rsplit("/", 1)[-1]
 17801	    stripped = base.lstrip(".")
 17802	    if "." in stripped:
 17803	        return "ext" if ("." + stripped.rsplit(".", 1)[1]) in _NODEHOME_CODE_EXTS else None
 17804	    return "shebang?"
 17805	
 17806	
 17807	class _NodehomeSide:
 17808	    """一邊的快照(提交索引、某個提交、或空的)。files={路徑: 模式} 只收一般檔;all_paths=所有受版控路徑(數裸檔名用);
 17809	    notes={圖譜相對路徑: 解析結果} 只收 Systems/*.md;shebang={路徑: 首行是不是 #!}(需要時才讀、兩邊共用);
 17810	    share/changed:另一邊的快照與兩邊之間有變動的路徑——沒變動的節點與首行直接用另一邊讀好的,不再讀一次。
 17811	    路徑用無損解碼([S31]:跟磁碟枚舉一樣,git 那邊才對得上)。"""
 17812	    __slots__ = ("files", "all_paths", "notes", "where", "_reader", "shebang", "share", "changed")
 17813	
 17814	
 17815	def _nodehome_git(repo_root, *args):
 17816	    """跑 git、輸出照位元組回(路徑要無損解碼,不能先被文字模式換成替代字元);跑不起來回 None。"""
 17817	    r = _lens_git(repo_root, *args, binary=True)
 17818	    if r is None or r.returncode != 0:
 17819	        return None
 17820	    return r.stdout
 17821	
 17822	
 17823	def _nodehome_show(path):
 17824	    """路徑拿來印的時候用:非 UTF-8 的位元組(無損解碼留下的替身字元)換成替代字元——直接 print 會在嚴格編碼的輸出上當掉。"""
 17825	    return os.fsencode(path).decode("utf-8", errors="replace") if isinstance(path, str) else str(path)
 17826	
 17827	
 17828	def _nodehome_split_z(raw):
 17829	    return [os.fsdecode(x) for x in raw.split(b"\0") if x]
 17830	
 17831	
 17832	def _nodehome_list(repo_root, where):
 17833	    """where='index' / 提交 sha / None(空)。回 (一般檔 {路徑: 模式}, 所有路徑) 或 None(git 失敗)。
 17834	    模式從索引或提交樹讀——連結檔(120000)與子模組(160000)不算一般檔 [S40]。"""
 17835	    if where is None:
 17836	        return {}, []
 17837	    raw = _nodehome_git(repo_root, "ls-files", "-s", "-z") if where == "index" else \
 17838	        _nodehome_git(repo_root, "ls-tree", "-r", "-z", "--full-tree", where)
 17839	    if raw is None:
 17840	        return None
 17841	    files, allp = {}, []
 17842	    for ent in raw.split(b"\0"):
 17843	        if not ent or b"\t" not in ent:
 17844	            continue
 17845	        meta, p = ent.split(b"\t", 1)
 17846	        parts = meta.split()
 17847	        if where == "index":
 17848	            if len(parts) != 3 or parts[2] != b"0":      # 合併中的衝突階段不算
 17849	                continue
 17850	            mode = parts[0]
 17851	        else:
 17852	            if len(parts) != 3:
 17853	                continue
 17854	            mode = parts[0]
 17855	        path = nfc(os.fsdecode(p))
 17856	        allp.append(path)
 17857	        if mode in (b"100644", b"100755"):
 17858	            files[path] = mode.decode()
 17859	    return files, allp
 17860	
 17861	
 17862	def _nodehome_changed_vs_disk(repo_root, where):
 17863	    """跟磁碟不一樣的路徑集合(那些要從 git 讀,其餘直接讀磁碟——既有的 git show 包裝一支一支讀,只讀這些)。
 17864	    where='index':工作目錄 vs 索引;where=HEAD 的 sha:工作目錄 vs HEAD;其他提交=None(全部從 git 讀)。"""
 17865	    if where == "index":
 17866	        raw = _nodehome_git(repo_root, "diff", "--name-only", "-z", "--no-renames")
 17867	    else:
 17868	        raw = _nodehome_git(repo_root, "diff", "--name-only", "-z", "--no-renames", where)
 17869	    if raw is None:
 17870	        return None
 17871	    return {nfc(x) for x in _nodehome_split_z(raw)}
 17872	
 17873	
 17874	def _nodehome_reader(repo_root, where):
 17875	    """回 read(path)->bytes|None。讀的是 where 那個版本:跟磁碟一樣的直接讀磁碟,不一樣的用 git show 讀
 17876	    ([S38]:提交前只讀提交索引——同一個工作目錄另一個會談寫到一半、還沒加進索引的東西讀不到)。"""
 17877	    if where is None:
 17878	        return lambda p: None
 17879	    disk_ok_all = False
 17880	    differ = None
 17881	    if where == "index":
 17882	        differ = _nodehome_changed_vs_disk(repo_root, "index")
 17883	    else:
 17884	        head = _lens_full_sha(repo_root, "HEAD")
 17885	        if head and head == where:
 17886	            differ = _nodehome_changed_vs_disk(repo_root, where)
 17887	    root = Path(repo_root)
 17888	    spec = "" if where == "index" else where
 17889	
 17890	    def read(p):
 17891	        if differ is not None and p not in differ:
 17892	            fp = root / p
 17893	            try:
 17894	                if fp.is_file() and not fp.is_symlink():
 17895	                    return fp.read_bytes()
 17896	            except OSError:
 17897	                pass
 17898	        r = _lens_git(repo_root, "show", f"{spec}:{p}", binary=True)
 17899	        if r is None or r.returncode != 0:
 17900	            return None
 17901	        return r.stdout
 17902	    return read
 17903	
 17904	
 17905	def _nodehome_parse_note(raw):
 17906	    """節點原文 → {type, status, about[], resp, sig, text}。sig=(摘要, 解析後的決策, 正文)——[S12] 內容有變
 17907	    逐欄比對用;★不沿用只算正文的那支雜湊★:摘要與決策都在開頭欄位裡,節點長大主要就長在摘要。"""
 17908	    text = raw.decode("utf-8-sig", errors="replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
 17909	    fm_lines, body = split_frontmatter(text)
 17910	    fields = {}
 17911	    dec = ""
 17912	    if fm_lines is not None:
 17913	        fields, _bk, _lint = parse_frontmatter(fm_lines)
 17914	        # 決策比「解析後的值」:只把 content: a 改成 content: "a" 這種等價寫法不算內容有變(第二輪外家席)
 17915	        try:
 17916	            dec = json.dumps(parse_decisions(fm_lines), ensure_ascii=False, sort_keys=True)
 17917	        except Exception:
 17918	            dec = "\n".join(l.rstrip() for l in fm_lines if l.startswith(("decisions:", "  ")))
 17919	    summ = fields.get("summary")
 17920	    summ = summ if isinstance(summ, str) else ""
 17921	    return {"type": str(fields.get("type", "")).strip(),
 17922	            "status": str(fields.get("status", "")).strip(),
 17923	            "about": [str(x) for x in as_list(fields.get("about_code")) if str(x).strip()],
 17924	            "resp": fields.get("responsibility") if isinstance(fields.get("responsibility"), str) else None,
 17925	            "sig": ("\n".join(l.rstrip() for l in summ.splitlines()).strip(), dec,
 17926	                    "\n".join(l.rstrip() for l in body.splitlines()).strip()),
 17927	            "text": text}
 17928	
 17929	
 17930	def _nodehome_side(repo_root, where, vault_rel, share=None, changed=None):
 17931	    """[S38] 建一邊的快照。share=另一邊已建好的快照、changed=兩邊之間有變動的路徑:沒變動的節點直接用 share 的解析結果
 17932	    (推送前的起點那一側只讀這段範圍裡有變動的節點——不然每一篇都要 git show 一次,65 篇就要 2 秒以上)。"""
 17933	    lst = _nodehome_list(repo_root, where)
 17934	    if lst is None:
 17935	        return None
 17936	    s = _NodehomeSide()
 17937	    s.files, s.all_paths = lst
 17938	    s.where = where
 17939	    s._reader = _nodehome_reader(repo_root, where)
 17940	    s.shebang = {}
 17941	    s.share = share
 17942	    s.changed = set(changed or ())
 17943	    s.notes = {}
 17944	    pre = vault_rel + "/Systems/"
 17945	    for p in s.files:
 17946	        if p.startswith(pre) and p.endswith(".md"):
 17947	            rel = p[len(vault_rel) + 1:]
 17948	            if share is not None and p not in s.changed and rel in share.notes:
 17949	                s.notes[rel] = share.notes[rel]
 17950	                continue
 17951	            raw = s._reader(p)
 17952	            if raw is not None:
 17953	                s.notes[rel] = _nodehome_parse_note(raw)
 17954	    return s
 17955	
 17956	
 17957	def _nodehome_required(repo_root, side, cfg, vendored_skip):
 17958	    """[S1] 需要家的檔集合,另回檔名不是 UTF-8 的程式檔(永遠寫不進圖譜,只提醒改名或排除)。"""
 17959	    import fnmatch
 17960	    req, bad_names = set(), set()
 17961	    for p in side.files:
 17962	        kind = _nodehome_code_kind(p)
 17963	        if kind is None:
 17964	            continue
 17965	        if any(fnmatch.fnmatch(p, g) for g in _NODEHOME_EXCLUDE_GLOBS):
 17966	            continue
 17967	        if p in vendored_skip or _cochange_excluded(p, cfg["ignore"]) or _nodehome_is_test(p):
 17968	            continue
 17969	        if kind == "shebang?":
 17970	            if p in side.shebang:
 17971	                ok = side.shebang[p]
 17972	            elif side.share is not None and p not in side.changed and p in side.share.shebang:
 17973	                ok = side.shebang[p] = side.share.shebang[p]
 17974	            else:
 17975	                head = side._reader(p)
 17976	                ok = side.shebang[p] = bool(head) and head[:200].split(b"\n", 1)[0].startswith(b"#!")
 17977	            if not ok:
 17978	                continue
 17979	        try:
 17980	            p.encode("utf-8")
 17981	        except UnicodeEncodeError:
 17982	            bad_names.add(p)
 17983	            continue
 17984	        req.add(p)
 17985	    return req, bad_names
 17986	
 17987	
 17988	def _nodehome_key(value):
 17989	    """about_code 一項的比對鍵(字面):路徑正規化+NFC。★不讀磁碟★——比對的是被檢查那個版本裡的樣子,
 17990	    推送一個不是目前 checkout 的分支時,磁碟上的拼法跟那個提交對不上(第二輪邊界席實跑重現的誤擋)。
 17991	    about_code 寫入時已經照磁碟校正過(解連結、大小寫、Unicode 寫法;_about_code_path),所以字面比就夠。"""
 17992	    return nfc(_posix_norm(strip_quotes(str(value).strip())))
 17993	
 17994	
 17995	def _nodehome_homes(repo_root, side):
 17996	    """[S2] {檔: [家那幾篇]}。只看 about_code 欄位值、不看預標指紋有沒有過期(指紋在每次寫回都會過期)。
 17997	    回 (homes, 每篇自己的檔集合)。"""
 17998	    homes, own = {}, {}
 17999	    for rel, n in side.notes.items():
 18000	        keys = {k for k in (_nodehome_key(v) for v in n["about"]) if k}
 18001	        own[rel] = keys
 18002	        if n["type"] != "system" or n["status"] not in _NODEHOME_HOME_STATUSES:
 18003	            continue
 18004	        for k in keys:
 18005	            homes.setdefault(k, []).append(rel)
 18006	    return homes, own
 18007	
 18008	
 18009	def _nodehome_refs(text, side, req):
 18010	    """[S7][S8] 這篇用反引號寫到哪幾支需要家的檔:抽取跟改檔前推筆記同一支(完整路徑+在受版控檔裡唯一的裸檔名)。
 18011	    裸檔名不唯一時推筆記那支不認它,這裡也不認——不構成「別人檔的入口」,就不算認領。"""
 18012	    top_dirs = {p.split("/", 1)[0] for p in side.all_paths if "/" in p and not p.startswith(".")}
 18013	    full, bare = _node_code_ref_tokens(text, top_dirs)
 18014	    refs = {nfc(t) for t, _l in full if nfc(t) in req}
 18015	    if int(_impact_knob("LUMOS_IMPACT_BASENAME_MATCH", 1)):
 21245	        })
 21246	
 21247	    return {"direct": direct_list, "indirect": indirect_list}
 21248	
 21249	
 21250	_ABOUT_COUNTS_CACHE = {}   # str(vault) → {repo 相對路徑: 幾篇 about_code 命中它}(行程內;--diff 多檔共用 env 免重掃)
 21251	
 21252	
 21253	def _impact_about_counts(env):
 21254	    """★巨檔門檻的材料:全掃 env.notes 的 about_code 建 {檔: 節點數}★(工具清單 #4;獨立頂層函式對齊 _impact_* 分工)。
 21255	    快取鍵用路徑字串(既有 _BASENAME_COUNTS_CACHE/_GIT_DATES_CACHE 同款;id(env) 是全庫沒先例的第二種做法)。"""
 21256	    key = str(env.vault)
 21257	    if key in _ABOUT_COUNTS_CACHE:
 21258	        return _ABOUT_COUNTS_CACHE[key]
 21259	    counts = {}
 21260	    for n in env.notes.values():
 21261	        for f in as_list(n.fields.get("about_code")):
 21262	            f = _posix_norm(f)
 21263	            if f:
 21264	                counts[f] = counts.get(f, 0) + 1
 21265	    _ABOUT_COUNTS_CACHE[key] = counts
 21266	    return counts
 21267	
 21268	
 21269	def _impact_mark_about(env, results, rel_file):
 21270	    """★about_code 只加分不降級★:對已進候選集的 results 項,about_code 含目標檔且 stamp 未過期 → 加 `about_hit: True`
 21271	    (只在 True 時出鍵;★不覆寫既有 hit 欄★;不改任何 pinned 判定——about 不是第四條入口)。
 21272	    總開關 LUMOS_IMPACT_ABOUT(預設 1;0=整段不跑、不讀正文);巨檔門檻 LUMOS_IMPACT_ABOUT_MAX(預設 8):
 21273	    目標檔被 ≥N 篇 about 命中時關閉加分(巨檔上「關於」無鑑別力,held 實證 22 誤放)。
 21274	    懶觸發:先查欄位,命中才讀該篇正文算雜湊(無 git、無子行程)。計劃:Projects/固定席扇出降權_計劃。"""
 21275	    if int(_impact_knob("LUMOS_IMPACT_ABOUT", 1)) == 0:
 21276	        return
 21277	    _norm = _posix_norm   # 跟寫入側同一個路徑正規化(r3 整合席:原本只剝開頭的 ./,不解 ..)
 21278	    target = _norm(rel_file)
 21279	    counts = _impact_about_counts(env)
 21280	    if counts.get(target, 0) >= int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8)):
 21281	        return
 21282	    for r in results:
 21283	        n = env.notes.get(r["node"])
 21284	        if n is None:
 21285	            continue
 21286	        vals = [_norm(x) for x in as_list(n.fields.get("about_code"))]
 21287	        if target not in vals:
 21288	            continue
 21289	        expired, _nh, _sh = about_code_expired(env.vault, r["node"], n.fields.get("about_code_stamp"))
 21290	        if expired:
 21291	            continue
 21292	        r["about_hit"] = True
 21293	
 21294	
 21295	def _impact_knob(name, default):
 21296	    """hook 面調參旋鈕:預設=凍結常數;LUMOS_IMPACT_* env 僅供 goldset 網格消融,非使用者旗標。"""
 21297	    try:
 21298	        return float(os.environ.get(name, default))
 21299	    except ValueError:
 21300	        return default
 21580	    if incident_node_set:
 21581	        all_direct = [x for x in all_direct if x["node"] not in incident_node_set]
 21582	        all_indirect = [x for x in all_indirect if x["node"] not in incident_node_set]
 21583	
 21584	    # 8.5 ranked 融合(階段三,spec §3):固定席(事故+含合約 direct+深度內合約 indirect)不占 top_k;
 21585	    # 非固定按 R=0.6L+0.4G 排,過 max(min_score, 0.25×最高非固定分) 閾;姐妹去冗餘於顯示層。
 21586	    if ranked or incidents_only:
 21587	        query = (_payload.get("query") or "") if stdin_payload else ""
 21588	        results = []
 21589	        lane_raw = []   # 參考道原料(--incidents-only 不進 indirect 迴圈也要有定義)
 21590	        # 固定席:事故(kind=incident)恆固定
 21591	        for x in all_incidents:
 21592	            results.append({"node": x["node"], "kind": "incident", "pinned": True,
 21593	                            "score": 1.0, "matched_by": x.get("matched_by"),
 21594	                            "contract": x.get("contract")})
 21595	        gated = False   # 查詢品質閘觸發旗標(未觸發路徑必為 False,防 NameError)
 21596	        if not incidents_only:
 21597	            # query 品質閘(edit面查詢品質閘_計劃 S2):低資訊 query 視同空查詢——
 21598	            # 只覆寫 lex 用局部變數;事故探針 _delta_q 刻意不受閘(安全網寧多勿漏)
 21599	            if query and _impact_query_junk(query):
 21600	                query = ""
 21601	                gated = True
 21602	                print("(query 品質閘:文本為檔頭雜訊/過短,L 臂靜默)", file=sys.stderr)
 21603	            # 詞彙分:對 direct+indirect 候選跑 BM25F(query 為空則全 0)
 21604	            cand = [x["node"] for x in all_direct] + [x["node"] for x in all_indirect]
 21605	            lex = {}
 21606	            if query and cand:
 21607	                _mx = None
 21608	                raw = _rank_score_candidates(env, query, cand)
 21609	                _mx = max((s for _r, s, _h in raw), default=0.0)
 21610	                for _r, s, _h in raw:
 21611	                    lex[_r] = (s / _mx) if _mx > 0 else 0.0
 21612	            eff_depth = depth if depth is not None else 2
 21613	            _dbase = _impact_knob("LUMOS_IMPACT_DIRECT_BASE", 0.30)
 21614	            for x in all_direct:
 21615	                L = lex.get(x["node"], 0.0)
 21616	                pinned = bool(x.get("contract"))   # 含合約的 direct 固定
 21617	                results.append({"node": x["node"], "kind": "direct", "pinned": pinned,
 21618	                                "score": round(_dbase + (1.0 - _dbase) * L, 4), "L": round(L, 4),
 21619	                                "hit": x.get("hit"), "contract": x.get("contract")})
 21620	            _pin_hop = int(_impact_knob("LUMOS_IMPACT_PIN_HOP", 1))
 21621	            # ★pin-denoise-a-v4(2026-08-24,四輪設計審收斂)★:硬合約保送——knob=1 時 indirect 保送只認
 21622	            # INVARIANT/IRREVERSIBLE;RISK·* 類(樞紐筆記搭便車,held 噪音 58/96 的主力)降入「參考道」:
 21623	            # ★獨立容器 lane_raw,自始不進 results★(pinned:False 會被四處「非 pinned=free」分流吃回自由席、
 21624	            # 再被動態門檻砍出輸出——v3 r2 實測);JSON 用獨立頂層鍵 "lane"(決策 d2:沒學過 lane 的讀者
 21625	            # 結構性不受影響,diff 聚合/hook free 桶/守衛全免改)。
 21626	            # ★2026-08-24 考卷轉正預設 1(knob=0 留逃生)★:train LANE_N∈{2,3,5} 不敏感取 3;
 21627	            # 候選臂 held 噪音 82→39(-52%)、out_top3_must 0.083→0.367、must 兩棘輪零退、九關全過。
 21628	            _hard_pin = int(_impact_knob("LUMOS_IMPACT_HARD_PIN", 1))
 21629	            for x in all_indirect:
 21630	                L = lex.get(x["node"], 0.0)
 21631	                hop = x.get("hop", 2)
 21632	                contract = x.get("contract")
 21633	                # 合約固定席 hop 上限(v1.2 旋鈕):合約密集圖(Landmark 考卷實證)hop2 合約
 21634	                # 搭便車氾濫(51 席噪音)——收窄後 hop2 合約降入自由席按分數競爭(L≈0 者被閾殺)
 21635	                if contract and hop <= min(eff_depth, _pin_hop):
 21636	                    if _hard_pin and contract not in ("INVARIANT", "IRREVERSIBLE"):
 21637	                        # RISK·* 降參考道:score 用 indirect 自由席同款 R 公式(常數 0.70 全員同分,
 21638	                        # cap 挑誰會退化成字母序——v3 r3 s1f2);kind 保留 indirect(lane 是欄位不是 kind)
 21639	                        G = 0.60 * min(1.0, 2.0 / (2 ** hop))
 21640	                        lane_raw.append({"node": x["node"], "kind": "indirect", "pinned": False,
 21641	                                         "lane": "soft-guard", "score": round(0.60 * L + 0.40 * G, 4),
 21642	                                         "L": round(L, 4), "hop": hop, "contract": contract})
 21643	                        continue
 21644	                    results.append({"node": x["node"], "kind": "indirect", "pinned": True,
 21645	                                    "score": round(0.40 + 0.30, 4), "L": round(L, 4),
 21646	                                    "hop": hop, "contract": contract})
 21647	                    continue
 21648	                # hop≥2 需 L>底線(遠端節點要足夠詞彙證據背書)
 21649	                if hop >= 2 and L <= _impact_knob("LUMOS_IMPACT_LMIN_HOP2", 0.0):
 21650	                    continue
 21651	                G = 0.60 * min(1.0, 2.0 / (2 ** hop))
 21652	                R = round(0.60 * L + 0.40 * G, 4)
 21653	                results.append({"node": x["node"], "kind": "indirect", "pinned": False,
 21654	                                "score": R, "L": round(L, 4), "hop": hop, "contract": contract})
 21655	        # about_code 語意欄位(工具清單 #4):只標記、不動 pinned;--incidents-only 快速路徑整段跳過
 21656	        if not incidents_only:
 21657	            _impact_mark_about(env, results, rel_file)
 21658	        # 分固定/非固定;非固定過閾+排序+補到 top_k
 21659	        pins = [r for r in results if r["pinned"]]
 21660	        # 固定席內 stable sort:事故永遠最前(std-r1 s1f10),其次 about 命中者,其餘保持三軸原序
 21661	        pins.sort(key=lambda r: (r["kind"] != "incident", not r.get("about_hit", False)))
 21662	        free = [r for r in results if not r["pinned"]]
 21663	        max_free = max((r["score"] for r in free), default=0.0)
 21664	        thresh = max(float(min_score), _impact_knob("LUMOS_IMPACT_DYN_COEF", 0.65) * max_free)
 21665	        free = [r for r in free if r["score"] >= thresh]
 21666	        free.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))
 21667	        # 名額制(v1.1):單體檔洪水按排名剪尾——閾值管品質、名額管上限(gate 對齊 top_k+2=10);
 21668	        # 剪的是 11 名以後,不動前 8 的視野(精度/必看召回不受影響)
 21669	        # PPR 分量(檢索PPR邊權_計劃)已試已殺(2026-07-28 edit 卷 train 網格全負:
 21670	        # baseline nDCG@8 0.9831 vs ppr w0.2/0.4/0.6=0.9817/0.9668/0.9598,b1 純 PPR 與
 21671	        # b2 cochange 邊權同分=邊權零貢獻;free 池中位 3 席使 P@8 對重排零鑑別,裁決依 nDCG)。
 21672	        # 與 A3 同源教訓:本圖的圖傳播訊號打不過調校後的 BM25F 融合;勿憑直覺復活,
 21673	        # 重試須先過同款考卷。詳 Projects/檢索PPR邊權_計劃 墓碑節。
 21674	        _quota = int(_impact_knob("LUMOS_IMPACT_FREE_QUOTA", 10))
 21675	        truncated = max(0, len(free) - min(int(top), _quota))
 21676	        free = free[:min(int(top), _quota)]
 21677	        # R1 直連保底席(2026-08-07,plan:hook必看召回修復;第三桶明文):
 21678	        # 觸發=截斷後最終 free 集零 direct 且存在被閾砍/截的 direct(缺口)。
 21679	        # rescued 恆 pinned:false、threshold/quota 不作用其上、外掛於 free 之後(--top 例外,
 21680	        # 同 pins safety_overflow 精神);tie-break 沿 free.sort 慣例 (-score, hop, node)。
 21681	        # knob:LUMOS_IMPACT_RESCUE_N(2026-08-07 考卷轉正預設 1:held Σmust 12→14、
 21682	        # P@8 0.6389→0.6944 雙升,gate 兩條全過;knob=0 留 A 臂逃生)。
 21683	        # S2 水位謂詞(2026-08-07,plan:連結缺失補全):free 內 direct(排除 pinned;截斷後
 21684	        # 最終集)不足 N 席 → 補 need=max(0, N−count) 席(前案「僅零 direct 觸發」為 N=1 特例,
 21685	        # 向下相容;前案合約候選之改寫經考卷 A/B 重裁,互引留痕見兩計劃節點)。
 21686	        rescued = []
 21687	        # 2026-08-07 水位案考卷轉正 N=3(train 網格 {1,2,3} recall 軸選出;held 確認
 21688	        # Σmust 14→17、P@8 0.6944→0.7130 週閘翻綠;knob 留逃生)
 21689	        _rescue_n = int(_impact_knob("LUMOS_IMPACT_RESCUE_N", 3))
 21690	        _free_direct = sum(1 for r in free if r["kind"] == "direct")
 21691	        _need = max(0, _rescue_n - _free_direct)
 21692	        if _rescue_n > 0 and _need > 0:
 21693	            _free_ids = {id(r) for r in free}
 21694	            dropped = [r for r in results
 21695	                       if r["kind"] == "direct" and not r["pinned"] and id(r) not in _free_ids]
 21696	            dropped.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))
 21697	            for r in dropped[:_need]:
 21698	                rr = dict(r)
 21699	                rr["rescued"] = True
 21700	                rescued.append(rr)
 21701	        # 參考道:產生端 cap(三處輸出同一份,口徑合一——被 cap 砍的必看會誠實掉 must_in_out,棘輪有效)
 21702	        lane_items = []
 21703	        _lane_trunc = 0
 21704	        if lane_raw:
 21705	            lane_raw.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))   # 同 free/rescued 三鍵慣例
 21706	            _lane_n = max(0, int(_impact_knob("LUMOS_IMPACT_LANE_N", 3)))   # 負值防護(同 _rescue_n 的 max(0,…) 慣例;負切片語意是「砍尾」不是上限)
 21707	            lane_items = lane_raw[:_lane_n]
 21708	            _lane_trunc = len(lane_raw) - len(lane_items)
 21709	        # 姐妹去冗餘(顯示層,--json 全量不折)
 21710	        final = pins + free + rescued
 21711	        meta = {"candidates": len(all_direct) + len(all_indirect) + len(all_incidents),
 21712	                "pinned": len(pins), "truncated": truncated, "rescued": len(rescued),
 21713	                "safety_overflow": max(0, len(pins) - int(top))}
 21714	        if lane_raw:
 21715	            meta["lane"] = len(lane_items)
 21716	            meta["lane_truncated"] = _lane_trunc
 21717	        if as_json:
 21718	            out_obj = {"file": rel_file, "results": final, "meta": meta}
 21719	            if lane_items:   # 條件鍵(同 query_gated/stack_questions 慣例):knob=0 或空 → 鍵不存在
 21720	                out_obj["lane"] = lane_items
 21721	            if gated:
 21722	                out_obj["query_gated"] = True
 21723	            # 棧別效能追問(pitfalls棧別效能追問_計劃 T2):完整 ranked 模式(非 incidents-only
 21724	            # 冷卻快速路)且目標檔命中問題表 → 附該棧檢核問(全表);單源=_STACK_PERF_QUESTIONS,hook 只格式化
 21725	            if not incidents_only and not _PITFALL_DIFF_TEST_PAT.search(rel_file):
 21726	                _sk = _stack_key_for_file(rel_file, repo_root_for_lookup)   # .ts/.js 看 package.json 分前後端
 21727	                if _sk:
 21728	                    out_obj["stack_questions"] = {_sk: _STACK_PERF_QUESTIONS[_sk]}
 21729	                    # 觸發式適用性(表態閘 S3):hook 另送原始 delta_text(保留換行;query 那欄是 8000 字/512 詞截斷版,只給詞彙融合)
 21730	                    # → 只列命中 when 的題;沒送(legacy 呼叫)就沒有 applicable 鍵,hook 退回印全表。
 21731	                    _dt = _payload.get("delta_text") if stdin_payload else None
 21732	                    if isinstance(_dt, str):
 21733	                        _cfgq = _stack_questions_config(repo_root_for_lookup)
 21734	                        _app, _meta = _stack_applicability({_sk: _dt.splitlines()}, _cfgq["ask_all_over_lines"])
 21735	                        out_obj["stack_questions_applicable"] = _app
 21736	                        out_obj["stack_questions_meta"] = _meta
 21737	                        if _payload.get("delta_truncated"):
 21738	                            out_obj["delta_truncated"] = True
 21739	            print(json.dumps(out_obj, ensure_ascii=False))
 21740	        else:
 21741	            print(f"改動 {rel_file} — 相關 top(固定席 {len(pins)}):")
 21742	            for r in final:
 21743	                mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{r.get('hop','?')}"}.get(r["kind"], "")
 21744	                ct = f" ★{r['contract']}★" if r.get("contract") else ""
 21745	                pin = " [固定]" if r["pinned"] else ""
 21746	                print(f"  {r['score']:5.2f} {mk} {r['node']}{ct}{pin}")
 21747	            if meta["truncated"]:
 21748	                print(f"  (+{meta['truncated']} 條低分截斷;--json 全量)")
 21749	            if not lane_items and meta.get("lane_truncated"):
 21750	                print(f"  (守衛面參考 {meta['lane_truncated']} 條被 LANE_N cap 全部隱藏——網格消融才會發生)")
 21751	            if lane_items:
 21752	                print(f"守衛面參考(軟標記樞紐,未被本次改動直接證實相關,{len(lane_items)} 條):")
 21753	                for r in lane_items:
 21754	                    print(f"  {r.get('score', 0):5.2f} hop{r.get('hop', '?')} {r.get('node', '?')}  ({r.get('contract', '')})")
 21755	                if meta.get("lane_truncated"):
 21756	                    print(f"  (另有 {meta['lane_truncated']} 條守衛面參考未列出)")
 21757	            if meta["safety_overflow"]:
 21758	                print(f"  safety overflow: {meta['safety_overflow']}")
 21759	        return 0
 21760	
 21761	    # 9. 輸出
 21762	    if as_json:
 21763	        print(json.dumps(
 21764	            {"file": rel_file, "direct": all_direct, "indirect": all_indirect,
 21765	             "incidents": all_incidents},
 21835	    # `{"results":[1],"sync":[]}` 這種合法 JSON 會通過,然後在下游 r.get(...) 當場拋例外,
 21836	    # 而那個例外會被 pre-push 的 || true 吞掉:★不是按設計記 range-unavailable,是靜默失效★。
 21837	    if not isinstance(data, dict):
 21838	        return None
 21839	    res = data.get("results")
 21840	    if not isinstance(res, list) or any(not isinstance(r, dict) for r in res):
 21841	        return None
 21842	    sync = data.get("sync")
 21843	    if sync is not None and not (isinstance(sync, dict)
 21844	                                 and isinstance(sync.get("missing"), list)
 21845	                                 and isinstance(sync.get("touched_nodes"), list)):
 21846	        return None
 21847	    return data
 21848	
 21849	
 21850	def cmd_impact_diff(diff_range, repo=None, depth=None, top=8, min_score=0.20, as_json=False,
 21851	                    sync_check=False, sync_only=False, from_json=None):
 21852	    """code-loop 橋接:對整段 diff 的每支改動 code 檔跑 ranked impact(query=該檔 hunk 文字),
 21853	    聚合成「受影響功能面」manifest——固定席(合約/事故)全保、非固定取跨檔最高分 top-N。
 21854	    定位=審計員鏡頭(advisory,人判),非自動推播(hook 面 goldset 評測未過線,故不接 hook)。
 21855	    rc: 0=成功 / 2=git 失敗 / 3=vault 缺。
 21856	
 21857	    from_json:吃一份已經算好的結果,不自己算(見 _impact_payload_read)。目前只支援
 21858	    搭 --sync-only 用——推送關卡算一次、同步點名與合約測試閘各讀一次。"""
 21859	    if from_json is not None:
 21860	        _pl = _impact_payload_read(from_json)
 21861	        if _pl is None or _pl.get("sync") is None:
 21862	            return 0          # 失敗隔離:維持同步點名現在的行為(靜默)
 21863	        _print_sync_nudge(_pl["sync"], _pl.get("range") or diff_range)
 21864	        return 0
 21865	    import json as _json
 21866	    import subprocess as _sp
 21867	    if diff_range == "staged":
 21868	        # 圖譜同步覆蓋(2026-08-22):pre-commit 要對「這次 commit 的內容」算波及,用 staged 代替 range
 21869	        diff_range = "--staged"
 21870	    elif diff_range.startswith("-"):
 21871	        # 同 pitfalls/cochange-check:'-' 開頭值會被 git 誤認成選項,查詢命令 rc2 拒收
 21872	        print("擋下:--diff 的值不能用 - 開頭(會被當成選項)", file=sys.stderr)
 21873	        return 2
 21874	    repo_root = Path(repo) if repo else None
 21875	    if repo_root is None:
 21876	        for cand in (Path.cwd(), *Path.cwd().parents):
 21877	            if (cand / ".git").exists():
 21878	                repo_root = cand
 21879	                break
 21880	    if repo_root is None or not (repo_root / ".git").exists():
 21881	        print("擋下:找不到 git 專案,用 --repo 指定", file=sys.stderr)
 21882	        return 2
 21883	    # core.quotePath=false:CJK 檔名不轉義加引號(否則 startswith/endswith 過濾全失效,r2 panel major)
 21884	    r = _sp.run(["git", "-C", str(repo_root), "-c", "core.quotePath=false",
 21885	                 "diff", "--name-only", diff_range], capture_output=True, text=True, errors="replace")
 21886	    if r.returncode != 0:
 21887	        print(f"擋下:git 算不出差異: {r.stderr.strip()[:200]}", file=sys.stderr)
 21888	        return 2
 21889	    files = []
 21890	    for f in r.stdout.splitlines():
 21891	        f = f.strip()
 21892	        if not _impact_diff_seed_ok(f):
 21893	            continue
 21894	        # 已刪檔不跳過:反查靠「節點 body 引用該路徑」而非檔案存在——
 21895	        # 刪除/改名正是合約節點最該被推到審計員眼前的時刻(r1 codex major)
 21896	        files.append(f)
 21897	    merged = {}          # node -> entry(跨檔取最高分;pinned 任一檔 pinned 即 pinned)
 21898	    per_file_meta = []
 21899	    import io, contextlib
 21900	    _vault = _vault_in(repo_root)
 21901	    # ★沒有圖譜就直接說,不要印「0 篇」裝作查過了★(2026-09-07 全 repo 審視 #9)
 21902	    #
 21903	    # 出身:這條路原本只在**逐檔迴圈裡**才發現沒圖譜——而「這個範圍 0 個檔」時迴圈根本不跑,
 21904	    # 於是一路走到最後印出「固定席 0 + top 0」並回成功。
 21905	    # ★對新手最危險的就是這個★:同一件事(找不到圖譜),另外兩種問法一個回 rc3、一個回 rc2
 21906	    # 並印白話擋下,只有這條印「0 篇」**看起來像查過了**——而它根本沒有圖譜可查。
 21907	    # 文件本來就寫著這條路會回「圖譜缺」,只是零檔時走不到。
 21908	    if _vault is None:
 21909	        return _no_vault_msg()
 21910	    _env_shared = Env(_vault)   # 建一次,逐檔復用(r1 N+1)
 21911	    for f in files:
 21912	        d = _sp.run(["git", "-C", str(repo_root), "-c", "core.quotePath=false",
 21913	                     "diff", diff_range, "--", f], capture_output=True, text=True, errors="replace")
 21914	        hunk = " ".join(l[1:].strip() for l in d.stdout.splitlines()
 21915	                        if l[:1] in "+-" and not l.startswith(("+++", "---")))[:4000]
 21916	        buf = io.StringIO()
 21917	        with contextlib.redirect_stdout(buf):
 21918	            rc = cmd_impact(f, repo=str(repo_root), depth=depth, as_json=True,
 21919	                            ranked=True, top=top, min_score=min_score,
 21920	                            payload={"query": hunk, "prospective": {}},
 21921	                            preloaded=(_vault, _env_shared) if _env_shared is not None else None)
 21922	        if rc == 3:
 21923	            print("IMPACT-DEBUG: vault 找不到(rc3)", file=sys.stderr)
 21924	            return 3
 21925	        if rc != 0:
 21926	            continue
 21927	        try:
 21928	            data = _json.loads(buf.getvalue().strip().splitlines()[-1])
 21929	        except (ValueError, IndexError):
 21930	            continue
 21931	        _pm = {"file": f, **data.get("meta", {})}
 21932	        if data.get("query_gated"):
 21933	            _pm["query_gated"] = True   # 觀測欄聚合轉發(r1 f5:code-loop 鏡頭可見)
 21934	        per_file_meta.append(_pm)
 21935	        for x in data.get("results", []):
 21936	            cur = merged.get(x["node"])
 21937	            if cur is None:
 21938	                merged[x["node"]] = {**x, "files": [f]}
 21939	            else:
 21940	                if f not in cur["files"]:
 21941	                    cur["files"].append(f)
 21942	                pinned = cur["pinned"] or x.get("pinned", False)
 21943	                if x["score"] > cur["score"]:
 21944	                    # 整項以勝出結果重建(避免 hop/L 舊值殘留成幽靈欄位,r1 s4 minor)
 21945	                    merged[x["node"]] = {**x, "files": cur["files"], "pinned": pinned}
 21946	                else:
 21947	                    cur["pinned"] = pinned
 21948	    pins = sorted([v for v in merged.values() if v["pinned"]],
 21949	                  key=lambda v: (-v["score"], v["node"]))
 21950	    free = sorted([v for v in merged.values() if not v["pinned"]],
 21951	                  key=lambda v: (-v["score"], v["node"]))[:int(top)]
 21952	    # 落成位置閉環(sync-check):預期受影響節點 ∩ 分支實際動過的圖譜節點——
 21953	    # 「這功能被改了,它的節點卻沒動」= 受影響未同步清單(advisory,人判;固定席可信度高、自由席≈P@8 .70)
 21954	    sync = None
 21955	    if sync_check:
 21956	        _vault_name = _vault.name if _vault is not None else None
 21957	        touched = set()
 21958	        if _vault_name:
 21959	            _prefix = f"docs/{_vault_name}/"
 21960	            for f2 in r.stdout.splitlines():
 21961	                f2 = f2.strip().strip('"')
 21962	                if f2.startswith(_prefix) and f2.endswith(".md"):
 21963	                    touched.add(f2[len(_prefix):])
 21964	        missing = [v for v in (pins + free) if v["node"] not in touched]
 21965	        sync = {"touched_nodes": sorted(touched),
 21966	                "missing": [{"node": v["node"], "pinned": v["pinned"],
 21967	                             "score": v["score"], "files": v["files"]} for v in missing]}
 21968	    if as_json:
 21969	        print(_json.dumps({"range": diff_range, "files": files,
 21970	                           "results": pins + free,
 21971	                           **({"sync": sync} if sync is not None else {}),
 21972	                           "meta": {"files": len(files), "pinned": len(pins),
 21973	                                    "free_kept": len(free),
 21974	                                    "free_total": sum(1 for v in merged.values() if not v["pinned"]),
 21975	                                    "per_file": per_file_meta}}, ensure_ascii=False))
 21976	        return 0
 21977	    if sync_only and sync is not None:
 21978	        _print_sync_nudge(sync, diff_range)
 21979	        return 0
 21980	    print(f"受影響功能面({diff_range};{len(files)} 檔;固定席 {len(pins)}+top {len(free)}——審計鏡頭,人判):")
 21981	    for v in pins + free:
 21982	        mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{v.get('hop','?')}"}.get(v["kind"], "")
 21983	        ct = f" ★{v['contract']}★" if v.get("contract") else ""
 21984	        pin = " [固定]" if v["pinned"] else ""
 21985	        print(f"  {v['score']:5.2f} {mk} {v['node']}{ct}{pin}  ←{','.join(v['files'][:3])}")
 21986	    if not merged:
 21987	        print("  (無節點引用這些檔——圖譜對此 diff 無覆蓋)")
 21988	    if sync is not None:
 21989	        _print_sync_nudge(sync, diff_range)
 21990	    return 0
 21991	
 21992	
 21993	def _print_sync_nudge(sync, diff_range, cap=8):
 21994	    """落成核對的唯一呈現(2026-08-22 架構對齊席抓到三套並存後收斂成這一份):
 21995	    固定席(合約/事故/直接相依)優先、最多 cap 篇;hooks(pre-commit/pre-push/Stop)只呼叫,不自己重排。"""
 21996	    miss = sorted(sync["missing"], key=lambda m: (not m["pinned"], -m.get("score", 0)))
 21997	    print(f"\n落成核對(這批動過 {len(sync['touched_nodes'])} 篇筆記):")
 21998	    if not miss:
 21999	        print("  ✓ 預期受影響的筆記全數已同步")
 22000	        return
 22001	    pinned = [m for m in miss if m["pinned"]]
 22002	    print(f"  提醒:下面這些筆記跟改到的程式碼直接相關(合約 / 事故 / 直接相依),這批沒動:" if pinned
 22003	          else "  提醒:下面這些筆記可能受影響,這批沒動(自由席,可信度較低,人判):")
 22004	    for v in miss[:cap]:
 22005	        mark = "⚠必看" if v["pinned"] else "  "
 22006	        print(f"  {mark} {v['node']}  ←{','.join(v['files'][:2])}")
 22007	    if len(miss) > cap:
 22008	        print(f"  … 還有 {len(miss) - cap} 篇(lumos impact --diff {diff_range} --sync-check --json 看全部)")
 22009	    print("  確定不受影響就略過;受影響的現在補。這裡只提醒不擋。")
 22010	
 22011	
 22012	# ── code-loop 留痕(Task 1) ────────────────────────────────────────────────────
 22013	
 22014	def _codeloop_git_branch(repo_root):
 22015	    """取 HEAD branch 名(detached HEAD 回 HEAD)。"""
 23045	        keys = sum(1 for l in summ.splitlines() if l.strip().startswith("KEY:") and l.strip() != "KEY:")
 23046	        contracts = len(_lens_contract_lines(summ, cap=10 ** 6))   # 同派工鏡頭的合約行判法,不另寫一條(代碼審 r1 架構席)
 23047	        files = len([a for a in n["about"] if (Path(root) / a).is_file()])
 23048	        out.append(f"  - {it}:已存在;掛 {plans} 份計劃、{keys} 行 KEY、{contracts} 條合約、管 {files} 支檔、"
 23049	                   + ("有寫負責範圍" if _nodehome_resp_ok(n["resp"]) else "沒寫負責範圍"))
 23050	    return out
 23051	
 23052	
 23053	def cmd_dispatch_lens_spec(spec_path, repo=None, as_json=False, cap=8, max_lines=400):
 23054	    """設計審的派工鏡頭(2026-09-05 第二輪審視六修 d2):設計審沒有 diff 範圍,改從計劃筆記本身算——
 23055	    ①計劃提到的程式檔(存在的,最多 5 個)各跑一次 impact 取固定席節點;②計劊直接 [[連結]] 的 Systems/Issues 節點。
 23056	    從工作樹讀(計劃就是工作樹上的東西);不快取(計劃常改)。手貼那條路實測 209 份派工詞只有 14 份有貼,所以機器來。"""
 23057	    import json as _json, io, contextlib, time as _time
 23058	    _t0 = _time.monotonic()
 23059	    start = Path(repo) if repo else Path.cwd()
 23060	    r = _lens_git(start, "rev-parse", "--show-toplevel")
 23061	    if r is None or r.returncode != 0 or not r.stdout.strip():
 23062	        print(f"擋下:{start} 不在 git 專案裡", file=sys.stderr)
 23063	        return 2
 23064	    root = Path(r.stdout.strip())
 23065	    sp = Path(spec_path)
 23066	    if not sp.is_absolute():
 23067	        sp = root / sp
 23068	    try:   # 外家 r1 M3:計劃筆記必須在 repo 內(/etc/hosts 這種 rc0 讀進來是專案邊界破口)
 23069	        sp.resolve().relative_to(root.resolve())
 23070	    except (ValueError, OSError):
 23071	        print(f"擋下:計劃筆記不在這個 repo 裡 {spec_path}", file=sys.stderr)
 23072	        return 2
 23073	    if not sp.is_file():
 23074	        print(f"擋下:計劃筆記不存在 {spec_path}", file=sys.stderr)
 23075	        return 2
 23076	    try:
 23077	        text = sp.read_text(encoding="utf-8", errors="replace")
 23078	    except OSError as e:
 23079	        print(f"擋下:計劃筆記讀不到({e.__class__.__name__})", file=sys.stderr)
 23080	        return 2
 23081	    slugs = sorted(p.name for p in (root / "docs").glob("*-knowledge") if p.is_dir()) if (root / "docs").is_dir() else []
 23082	    if not slugs:
 23083	        print("擋下:repo 裡沒有 docs/*-knowledge", file=sys.stderr)
 23084	        return 3
 23085	    vault_rel = f"docs/{slugs[0]}/"
 23086	    # ① 計劃提到的程式檔
 23087	    code_files, seen = [], set()
 23088	    for m in _LENS_SPEC_CODE_RE.findall(text):
 23089	        cand = m.rstrip(".,;:)」』】")
 23090	        if cand in seen or cand.endswith(".md"):
 23091	            continue
 23092	        p = root / cand
 23093	        try:   # 外家 r1 M3:scripts/../../x 這種穿越不收
 23094	            inside = p.resolve().relative_to(root.resolve()) is not None
 23095	        except (ValueError, OSError):
 23096	            inside = False
 23097	        if inside and p.is_file():
 23098	            seen.add(cand); code_files.append(cand)
 23099	        if len(code_files) >= _LENS_SPEC_MAX_FILES:
 23100	            break
 23101	    # ② 計劃直接連結的節點
 23102	    linked = []
 23103	    for m in re.findall(r"\[\[((?:Systems|Issues)/[^\]|#]+)", text):
 23104	        node = m.strip()
 23105	        if node not in linked and (root / vault_rel / f"{node}.md").is_file():
 23106	            linked.append(node)
 23107	    # ③ impact 取固定席(有預算)
 23108	    pinned = {}
 23109	    skipped_files, too_generic = [], []
 23110	    for f in code_files:
 23111	        if _time.monotonic() - _t0 > _LENS_SPEC_BUDGET:
 23112	            skipped_files.append(f); continue
 23113	        remain = _LENS_SPEC_BUDGET - (_time.monotonic() - _t0)
 23114	        try:   # 外家 r1 M1:預算不能只在呼叫前看——單次 impact 也可能 31 秒;子行程帶剩餘秒數 timeout
 23115	            import subprocess as _sp
 23116	            rr = _sp.run([sys.executable, str(Path(__file__).resolve()), "impact", "--file", f, "--repo", str(root), "--json"],
 23117	                         capture_output=True, text=True, timeout=max(1.0, remain))
 23118	            data = _json.loads(rr.stdout.strip().splitlines()[-1]) if rr.returncode == 0 and rr.stdout.strip() else {}
 23119	        except Exception:
 23120	            skipped_files.append(f); continue
 23121	        # impact --file 的 JSON 形狀是 {direct,indirect,incidents}(不是 --diff 的 results/pinned):
 23122	        # 固定席=直接相依全部 + 事故全部 + 帶合約的一跳間接(與 --diff 的 pinned 語意對齊)
 23123	        picks = [(v, "direct") for v in data.get("direct", []) if isinstance(v, dict)]
 23124	        picks += [(v, "incident") for v in data.get("incidents", []) if isinstance(v, dict)]
 23125	        picks += [(v, "indirect") for v in data.get("indirect", []) if isinstance(v, dict) and v.get("contract") and v.get("hop", 99) <= 1]
 23126	        # 太泛的檔(像本 repo 的 scripts/lumos 單檔 CLI、總測試檔)一個檔就牽 100+ 篇,附了等於沒附:超過上限的整檔略過並在頭部說明
 23127	        if len(picks) > _LENS_SPEC_MAX_PER_FILE:
 23128	            too_generic.append(f"{f}({len(picks)} 篇)"); continue
 23129	        for v, kind in picks:
 23130	            if not v.get("node"):
 23131	                continue
 23132	            node = str(v["node"])[:-3] if str(v["node"]).endswith(".md") else str(v["node"])
 23133	            if node.startswith("Projects/"):   # 別的計劃不是合約也不是事故,不進固定席
 23134	                continue
 23135	            pinned.setdefault(node, {"kind": _LENS_KIND.get(kind), "contract": _lens_contract_class(v), "files": [f]})
 23136	            if f not in pinned[node]["files"]:
 23137	                pinned[node]["files"].append(f)
 23138	    def _rank(v):
 23139	        return (0 if v.get("kind") == _LENS_KIND["incident"] else 1 if v.get("contract") else 2 if v.get("kind") == _LENS_KIND["direct"] else 3)
 23140	    listed = [{"node": n, **{"kind": "計劃連結", "contract": None, "files": []}, **pinned.get(n, {}), "kind": "計劃連結" + (f"+{pinned[n]['kind']}" if n in pinned and pinned[n].get("kind") else "")} for n in linked]   # 相容:不用 dict |(那是 3.9+,寫這行時專案宣告 ≥3.8;2026-09-06 宣告訂正為 ≥3.9,此寫法保留可用)
 23141	    listed += [{"node": n, **v} for n, v in sorted(pinned.items(), key=lambda kv: _rank(kv[1])) if n not in linked]
 23142	    landing = _nodehome_landing_sizes(root, vault_rel, text)   # [S22] 計劃寫的落點每一篇現在多大
 23143	    bound_status, _bidx = "ok", None
 23144	    try:
 23145	        _bidx = _platform_test_index(root)
 23146	    except Exception:
 23147	        bound_status = "skipped-no-config"
 23148	    lines = []
 23149	    if code_files and not listed:
 23150	        lines.append(_LENS_SPEC_HEADER)
   610	        lines.append("這個檔過去出過的事故(改之前先看):")
   611	        for item in incidents:
   612	            node = item.get("node", "?")
   613	            matched_by = item.get("matched_by", "?")
   614	            contract = item.get("contract")
   615	            combo = item.get("combo", False)
   616	            prefix = _contract_label(contract) if contract else ""
   617	            if combo:
   618	                prefix += "★COMBO★"
   619	            label = _match_label(matched_by)
   620	            if prefix:
   621	                lines.append(f"  {prefix} {_plain_label(node)}  ({label})")
   622	            else:
   623	                lines.append(f"  {_plain_label(node)}  ({label})")
   624	
   625	    lines.append("")
   626	    lines.append(_INJECT_INSTRUCTION)
   627	    return _frame_injected("\n".join(lines))
   628	
   629	
   630	def build_ranked_context(data: dict) -> str:
   631	    """v1.1:把 ranked 輸出({results,meta})轉成降噪清單文字。固定席在前(合約/事故),
   632	    非固定帶分數;截斷數照 meta 標注。尾附棧別效能追問(若 lumos 輸出帶 stack_questions——
   633	    單源在 scripts/lumos 的 _STACK_PERF_QUESTIONS,本 hook 只格式化不持有內容)。"""
   634	    lines: list[str] = []
   635	    res = data.get("results", [])
   636	    meta = data.get("meta", {})
   637	    pins = [x for x in res if x.get("pinned")]
   638	    free = [x for x in res if not x.get("pinned") and not x.get("rescued")]
   639	    rescued = [x for x in res if x.get("rescued")]
   640	    if pins:
   641	        lines.append(f"必看——這 {len(pins)} 篇帶著不能破壞的合約或出過事故:")
   642	        for x in pins:
   643	            mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{x.get('hop','?')}"}.get(x.get("kind"), "")
   644	            ct = f" {_contract_label(x['contract'])}" if x.get("contract") else ""
   645	            mb = f"  ({_match_label(x['matched_by'])})" if x.get("matched_by") else ""
   646	            # about_code 語意欄位命中(工具清單 #9):讀 about_hit(只在 True 時存在),不碰既有 hit 來源標記
   647	            ab = "★關於★" if x.get("about_hit") else ""
   648	            lines.append(f"  {ab}{mk}{ct} {_plain_label(x.get('node'))}{mb}")
   649	    if free:
   650	        lines.append(f"可能相關的 {len(free)} 篇(依關聯度排序):")
   651	        for x in free:
   652	            mk = {"direct": "直接", "indirect": f"hop{x.get('hop','?')}"}.get(x.get("kind"), "")
   653	            lines.append(f"  {x.get('score',0):.2f} {mk} {_plain_label(x.get('node'))}")
   654	    if rescued:
   655	        # R1 直連保底(plan:hook必看召回修復):分數不過閾但為僅有的直連節點——信心層級不同於排序席
   656	        lines.append(f"另外 {len(rescued)} 篇分數不高但直接提到這個檔,一併列出:")
   657	        for x in rescued:
   658	            hit = f"/{x['hit']}" if x.get("hit") == "basename-match" else ""
   659	            lines.append(f"  {x.get('score',0):.2f} 直接{hit} {_plain_label(x.get('node'))}")
   660	    if meta.get("truncated"):
   661	        lines.append(f"  (+{meta['truncated']} 條低分截斷,沒列出來)")
   662	    # pin-denoise-a-v4:參考道(JSON 獨立頂層鍵;.get 條件鍵慣例——knob=0 時鍵不存在)
   663	    lane = data.get("lane", [])
   664	    if lane:
   665	        lines.append(f"守衛面參考——這 {len(lane)} 篇是軟標記樞紐,跟每支檔都近,未被本次改動直接證實相關:")
   666	        for x in lane:
   667	            lines.append(f"  {x.get('score',0):.2f} hop{x.get('hop','?')} {x.get('node','?')}")
   668	        if meta.get("lane_truncated"):
   669	            lines.append(f"  (另有 {meta['lane_truncated']} 條守衛面參考未列出)")
   670	    # 表態閘 S3:lumos 有算適用性(有 stack_questions_applicable 鍵)就只印觸發到的題;沒算(legacy)才印全表
   270	        if _sv is not None:
   271	            VAULT = _sv
   272	            SNAP_ROOT = _wt
   273	            return True
   274	        _cleanup()   # 無 vault:當場清(worktree remove+rmtree),atexit 重跑冪等
   275	        print(f"⚠ snapshot {sha} 內無 docs/*-knowledge,釘定失敗", file=sys.stderr)
   276	        return False
   277	    shutil.rmtree(_wt, ignore_errors=True)   # 失敗路徑不留殘目錄
   278	    print(f"⚠ snapshot worktree 失敗({r.stderr.strip()[:80]})", file=sys.stderr)
   279	    return False
   280	
   281	
   282	def output_top3_must(res, lab):
   283	    """★成績單乙案(2026-08-24 Enzo 裁):輸出前 3 名的必看命中率★(Projects/固定席扇出降權_計劃 調研節)。
   284	    量的是「人打開 hook 先看到的三行是不是該看的」——不限固定席(甲案 pin_top3_must 是死表:
   285	    必看 15/69 坐固定席、事故恆最前,前 3 席組成幾乎不變)。res 順序=impact 輸出順序(pins→free→rescued)。
   286	    = 前 3 項裡標 2 的個數 / min(3, 該題標 2 總數);沒標 2 → None。只印、進 verdict/history,★不進 gate★。
   287	    歸因:數字動了要分是 about 還是排序,拿 LUMOS_IMPACT_ABOUT=0 離線對照。"""
   288	    must_total = sum(1 for v in lab.values() if v == 2)
   289	    if must_total == 0:
   290	        return None
   291	    _p3, _f3, _ = split_buckets(res)   # 分桶唯一實作(arch:別再自寫排除式)
   292	    top = (_p3 + _f3)[:3]   # lane 是掛「參考」標籤的獨立小節,不算首屏前三(v4-r2 Codex)
   293	    hit = sum(1 for x in top if lab.get(x["node"], 0) == 2)
   294	    return round(hit / min(3, must_total), 4)
   295	
   296	
   297	def _ratchet_base(history, rev, split, field, metric_rev=None, inherit=False):
   298	    """棘輪基線查找(評測尺翻案 [S3]③):同尺=同 (goldset_rev, metric_rev) 才比。
   299	    inherit=True(僅切換輪,恆等斷言過了才給):同 goldset_rev 下無同 metric_rev 基線時,
   300	    允許回退舊尺(metric_rev 缺欄)基線——沒有這條,新尺第一筆必然「無基線自動放行」,
   430	        lab = _labels_of(gs, cid)
   431	        if not lab or not any(v >= 1 for v in lab.values()):
   432	            continue
   433	        # impact 自行從 --repo 解析 vault(不吃全域 --vault)→ 快照釘定須走 --repo(r1 終審親驗)
   434	        # 呼叫收斂進 edit_universe(與評測母體同源,標註刷新 T2);None=file-gone/不可解,照舊跳。
   435	        res = edit_universe(case)
   436	        if res is None:
   437	            continue
   438	        pins, free, lane_items = split_buckets(res)   # v4:free 不含 lane(P@8 母體);out_nodes 含 lane(下方讀完整 res)
   439	        row = {"id": cid, "split": case["split"], "n_free": len(free), "n_pin": len(pins)}
   440	        # edit 面 nDCG 沿用候選集自證 IDCG:三排序共用同一 free 集,相對比較有效;
   441	        # 絕對值偏高(漏檢不罰),不得跨面引用(r1 panel s4)。
   442	        orders = {
   443	            "fusion": sorted(free, key=lambda x: (-x["score"], x["node"])),
   444	            "bm25": sorted(free, key=lambda x: (-x.get("L", 0.0), x["node"])),
   445	            "graph": sorted(free, key=lambda x: (-_graph_score(x), x["node"])),
   446	        }
   447	
   448	        n_rel_free = sum(1 for x in free if lab.get(x["node"], 0) >= 1)
   449	        for name, order in orders.items():
   450	            labels = [lab.get(x["node"], 0) for x in order]
   451	            kk = min(k, len(labels)) or 1
   452	            row[f"{name}_p"] = round(precision_at_k(labels, kk), 4) if labels else None
   453	            row[f"{name}_ndcg"] = round(ndcg_at_k(labels, k), 4) if labels else None
   454	            # condensed([S1]):窗=free 前 k(與 _touched_edit 同界)
   455	            _win = [x["node"] for x in order[:k]]
   456	            _judged, _cov, _valid = _condense(_win, lab, k)
   457	            row[f"{name}_cov"] = _cov
   458	            if _valid and _judged:
   459	                _kk = min(k, len(_judged))
   460	                row[f"c_{name}_p"] = round(precision_at_k(_judged, _kk), 4)
   461	                row[f"c_{name}_ndcg"] = round(ndcg_at_k(_judged, k), 4)
   462	            else:
   463	                row[f"c_{name}_p"] = row[f"c_{name}_ndcg"] = None
   464	        row["n_rel_free"] = n_rel_free
   465	        # must-see 兩指標分開記(r1 panel codex blocker:混稱=證據失真):
   466	        # in_out=出現在輸出(含自由席,top-k 聚合下可能被截) / pinned=真固定席(唯一機械保證)
   467	        out_nodes = {x["node"] for x in res}
   468	        pin_nodes = {x["node"] for x in pins}
   469	        must = [n for n, v in lab.items() if v == 2]
   470	        row["must_total"] = len(must)
   471	        row["must_in_out"] = sum(1 for n in must if n in out_nodes)
   472	        row["must_pinned"] = sum(1 for n in must if n in pin_nodes)
   473	        # 顯式三態([S1]④/[S3b]):未判 or 判0 → 噪音——不依賴 lab.get 殘影,
   474	        # 語意=固定席理應被判過,沒判過就該進補標(condensed 不適用於此,刻意分家)
   475	        row["pin_noise"] = sum(1 for x in pins
   476	                               if x["node"] not in lab or lab[x["node"]] == 0)
   477	        row["out_top3_must"] = output_top3_must(res, lab)   # #10 乙案:輸出前 3 名必看命中率(res=人看到的順序)
   478	        rows.append(row)
   479	    return rows
   480	
   481	
   482	def _pctl(vals, p):
   483	    if not vals:
   484	        return None
   485	    s = sorted(vals)
   530	        with open(_dump, "w", encoding="utf-8") as f:
   531	            json.dump({"split": split, "k_edit": k_edit, "edit_rows": erows},
   532	                      f, ensure_ascii=False)
   533	    if erows:
   534	        fp, fn = _macro(erows, "fusion_p"), _macro(erows, "fusion_ndcg")
   535	        bp, bn = _macro(erows, "bm25_p"), _macro(erows, "bm25_ndcg")
   536	        gp, gn = _macro(erows, "graph_p"), _macro(erows, "graph_ndcg")
   537	        print(f"改程式時的推薦(給一支檔,推該看的筆記,{len(erows)} 題有答案):")
   538	        _pct = lambda x: f"{x*100:.0f}%" if x is not None else "無資料"
   539	        print(f"  前 {k_edit} 名裡對的比例 {_pct(fp)}    ← 主要的尺(P@{k_edit});只比文字 {_pct(bp)}、只比圖結構 {_pct(gp)}——綜合要贏這兩個才算有用")
   540	        print(f"  對的有沒有排前面(nDCG@{k_edit}):{fn}(只比文字 {bn}、只比圖 {gn})")
   541	        pt3 = _macro(erows, "out_top3_must")
   542	        print(f"  輸出前 3 名是必看的比率:{pt3}    ← 人打開 hook 先看到的三行準不準;只看不閘(歸因用 LUMOS_IMPACT_ABOUT=0 對照)")
   543	
   544	        frees = [r["n_free"] for r in erows]
   545	        med, p95 = _pctl(frees, 0.5), _pctl(frees, 0.95)
   546	        must_t = sum(r["must_total"] for r in erows)
   547	        must_hit = sum(r["must_in_out"] for r in erows)
   548	        must_pin = sum(r["must_pinned"] for r in erows)
   549	        pin_noise = sum(r["pin_noise"] for r in erows)
   550	        print(f"  推薦量:每題通常推 {med} 篇、最多的題推 {p95} 篇(關卡用全部題目算:一般題 ≤{k_edit}、最多的題 ≤{k_edit + 2})")
   551	        print(f"  必看的筆記:{must_t} 篇裡 {must_hit} 篇有推出來;其中 {must_pin} 篇是靠合約/事故硬保的固定席,其餘靠排序、沒有保底")
   552	        print(f"  固定席裡不相干的筆記:{pin_noise} 條    ← 噪音,越少越好(目前只印不閘)")
   553	        verdict["hook_p"] = fp
   554	        verdict["free_median"] = med
   555	        verdict["free_p95"] = p95
   556	        verdict["hook_p_gate"] = _hook_gate_ok(fp)
   557	        verdict["hook_p"] = fp
   558	        # ── 新尺預覽(edit 面)──
   559	        c_fp, c_fn = _macro(erows, "c_fusion_p"), _macro(erows, "c_fusion_ndcg")
   560	        c_bp, c_gp = _macro(erows, "c_bm25_p"), _macro(erows, "c_graph_p")
   690	            **({"metric_switch_verified": True} if getattr(args, "_metric_switch_now", False) else {}),
   691	            "condensed_preview": {r["split"]: {"search": r["verdict"].get("condensed_search"),
   692	                                               "edit": r["verdict"].get("condensed_edit")}
   693	                                  for r in reports},   # [S3]② 巢狀預覽:一輪一筆不破
   694	            "verdicts": {r["split"]: {k: v for k, v in r["verdict"].items()
   695	                                      if not k.startswith("_") and not k.startswith("condensed_")}
   696	                         for r in reports}}
   697	
   698	
   699	def main():
   700	    global VAULT, SNAP_ROOT
   701	    ap = argparse.ArgumentParser()
   702	    ap.add_argument("--auto", action="store_true", help="cochange proxy 自動金標(related 面)")
   703	    ap.add_argument("--goldset", help="人工標註 goldset.json 路徑")
   704	    ap.add_argument("--split", choices=["train", "held"], help="只跑該切分")
   705	    ap.add_argument("--live-vault", action="store_true", help="用現況 vault(預設釘 goldset snapshot;探索/漂移觀測用)")
   706	    ap.add_argument("--snapshot", help="覆寫釘定 sha(過渡雙跑的舊快照輪;該輪 mode=goldset-transition)")
   707	    ap.add_argument("--ablation", action="store_true",
   708	                    help="消融模式(比較改動前後用):★有任何未標候選就擋下、rc 3★。"
   709	                         "不帶這旗標維持原行為(只印警告不擋)")
   710	    ap.add_argument("-k", type=int, default=8)
   711	    args = ap.parse_args()
   712	    if VAULT is None:
   713	        print("ERROR: 找不到 vault", file=sys.stderr); return 2
   714	    if args.auto:
   715	        gold = cochange_goldset()
   716	        rows = eval_related(gold, k=args.k)
   717	        if not rows:
   718	            print("(cochange proxy 金標為空——knowledge git 史太稀薄,退回人工 goldset)")
   719	            return 0
   720	        agg = {m: round(sum(r[m] for r in rows) / len(rows), 4) for m in ("ndcg", "mrr", "p")}
   721	        print(f"cochange-proxy related 評測(n={len(rows)} seeds, k={args.k}):")
   722	        print(f"  nDCG@{args.k}={agg['ndcg']}  MRR={agg['mrr']}  P@{args.k}={agg['p']}")
   723	        hist = Path(__file__).parent / "retrieval-eval-history.jsonl"
   724	        with open(hist, "a", encoding="utf-8") as fh:
   725	            fh.write(json.dumps({"mode": "auto-cochange", "k": args.k, "n": len(rows),
   726	                                 **agg}, ensure_ascii=False) + "\n")
   727	        return 0
   728	    if args.goldset:
   729	        try:
   730	            gs = json.loads(Path(args.goldset).read_text(encoding="utf-8"))
   731	            gs["labels"]; gs["search"]; gs["edit"]
   732	        except (OSError, ValueError, KeyError, TypeError) as e:
   733	            print(f"ERROR: goldset 讀取/結構失敗: {e}", file=sys.stderr)
   734	            return 2
   735	        # 語料快照釘定(r1 終審折入,可重現性正解):labels 對應出題當下的 vault——
   736	        # 之後新增的未標節點若進候選池一律計噪音,gate 會被「寫文件」這種無關演進打翻。
   737	        # 預設把評測 vault 釘在 goldset.snapshot_commit 的 worktree;--live-vault 才用現況(探索用)。
   738	        _snap = args.snapshot or gs.get("snapshot_commit")
   739	        # ★goldset_snapshot 帳面語意=「這輪實際用的語料」★:只有真的釘定成功才記 sha;
   740	        # --live-vault/LUMOS_EVAL_VAULT 繞過釘定=用現況語料,帳面必須記 None(code-r1 bug 席 F2)。
   741	        _pinned = None
   742	        if _snap and not args.live_vault and not os.environ.get("LUMOS_EVAL_VAULT"):
   743	            if pin_snapshot(_snap):
   744	                _pinned = _snap
   745	                print(f"(語料釘定 snapshot={_snap};--live-vault 可用現況)")
   746	            else:
   747	                print("(釘定失敗,退回現況 vault)", file=sys.stderr)
   748	        unl = sum(1 for c in gs["labels"].values() for v in c.values() if v.get("final") is None)
   749	        if unl:
   750	            print(f"⚠ 尚有 {unl} 個候選未定稿(final=None,視為 0)", file=sys.stderr)
   751	        if args.ablation:
   752	            # ★母體口徑★:用 collect_unjudged 而非上面那個 unl——後者只數 labels 內
   753	            # final=None,漏掉「根本不在候選池」的新節點,而那正是消融踩到的地雷。
   754	            _blocked, _n, _msg = ablation_blocked(gs, args.split, k=args.k)
   755	            if _blocked:
     1	---
     2	type: project
     3	status: doing
     4	created: 2026-09-12
     5	updated: 2026-09-12
     6	aliases: []
     7	tags:
     8	  - type/project
     9	  - status/doing
    10	  - scope/retrieval
    11	lands_in:
    12	  - Systems/retrieval-ranking
    13	  - Systems/節點還原
    14	  - Systems/check-j-regen-guard
    15	summary: |-
    16	  KEY:改檔前推筆記把「家」(每支檔有家驗過的 about_code)當成一條入口:改哪支檔,一定推它的家;只加入口、不降級任何既有必推項
    17	  KEY:依舊案 固定席扇出降權_計劃 d4 的重提條件而重提(「丙:第四條保送需先把漏標率壓到零,無新證據不重提」)——新證據是每支檔有家讓新檔一定有家、每次提交驗
    18	  KEY:節點還原把 about_code 設成必要條件:從程式重建的節點(蓋 regen 章)沒寫 about_code 就 lint 擋;SOP 第 4 步寫明必要、第 6 步出口看健檢 S8
    19	---
    20	# 推筆記認家_計劃
    21	
    22	> 白話:每支程式檔現在都有一篇「管它的」節點(家)。改那支檔時,家應該是最該被推給 agent 看的那一篇——可是推筆記的機制到現在還沒在用它。這案讓推筆記認家;另外讓接手舊專案、還原節點時,每篇還原出來的節點都一定寫明它管哪幾支檔。
    23	
    24	## 為什麼(這批的來源)
    25	
    26	- Enzo 2026-09-12 問:about_code 這個標籤,能不能讓節點相關性、推給 agent 的精準度再提升。
    27	- 查證(讀程式+乾淨審查員拿原始問題查,兩個來源一致):
    28	  - 決定推哪幾篇的只有四條路:正文用反引號寫的檔案路徑(完整路徑、或在受版控檔裡唯一的裸檔名)、從那些節點沿連結往外擴、事故筆記的觸發條件。★about_code 不是入口★,只在「一定會推的那幾篇」裡當排序。
    29	  - 那個排序還要「預標指紋」沒過期,而 `lumos append about_code` 與 `lumos new --code` 都不寫指紋——每支檔有家補的家,全部不會觸發這個排序。
    30	  - 推送前的波及計算聚合時把這個排序丟掉;派審查員時的圖譜參考完全沒用到。
    31	- ★舊案攔截★:[[Projects/固定席扇出降權_計劃]] 三輪設計審沒收斂,Enzo 裁 about_code 只做排序;成績單那條決定寫明「丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提」。★圖譜攔截★站:開案前;源:固定席扇出降權_計劃 d4。
    32	  - 新證據:[[Projects/每支檔有家_計劃]](2026-09-11 上線)讓新增的程式檔提交當下一定有家、原本有家的檔變沒家會擋;三個 POS 專案整理後健檢 S8 幾乎沒有沒家的檔。這正是當年缺的「漏標率壓到零」。
    33	  - 舊案 r1 的教訓照單全收:當時把「有 about 欄但不含目標檔」降到自由席,結果把該看的筆記踢出必推名單(必看裡 2/9、3/5 根本不是 about)——★本案只加入口,不降級任何既有必推項★。
    34	- 另一半:Enzo 同日要設計審順便看「既有專案還原節點,能不能把 about_code 也設成必要條件」。現況:SOP 第 4 步已寫用 `--code` 開節點,但沒寫必要、也沒有任何檢查。
    35	
    36	PRIOR-ART:最小解在讀側排序那一層——多一條入口,不改分數公式、不動其他三條路。世界解過:GitHub 的 CODEOWNERS 用「檔 → 負責者」的宣告直接點名審查者,結構化的宣告優先於文字比對。裁定=借用(把家當宣告式路由),自建只有接到既有排序的那一段;不採新依賴。
    37	
    38	## 名詞
    39	
    40	- **家**:照 [[Projects/每支檔有家_計劃]] 的定義——狀態 doing/done/stale 的 Systems 節點,about_code 列了這支檔;比對用同一支字面比對鍵,不看預標指紋。
    41	- **必推名單**:推筆記的固定席——事故、帶合約的直接節點、一跳合約間接,不截斷,一定會推給 agent。
    42	- **可選名單**:其餘候選照分數競爭,最多 10 篇加 3 篇保底。
    43	- **大檔**:家的篇數 ≥ `LUMOS_IMPACT_ABOUT_MAX`(預設 8)的檔,例如本工具鏈主程式有 31 個家。
    44	- **從程式重建的節點**:蓋了 `regen: from-scratch/<日期>` 章的 Systems 節點(節點還原 SOP 第 4 步蓋)。
    45	
    46	## 核心裁定
    47	
    48	### 甲、推筆記認家
    49	
    50	- [S1] 家的定義與比對鍵沿用每支檔有家那一支(同一個函式,不另寫一套);不看預標指紋。 [test:t_impact_home_uses_nodehome_definition]
    51	- [S2] 改檔前推筆記(`lumos impact --file --ranked`,也就是 Edit 前那個自動推筆記的 hook)把目標檔的家當成一條入口:家一定進候選、而且進必推名單,不必正文用反引號寫這支檔。 [test:t_impact_home_is_entry_and_pinned]
    52	- [S3] 必推名單的順序:事故最前,其次家,其餘照原本;家之間照分數。取代原本要預標指紋沒過期的「關於命中」排序。 [test:t_impact_pins_order_incident_home_rest]
    53	- [S4] 大檔不整批進必推:只有帶合約的家進必推,其餘家在可選名單照分數競爭(不另加分,避免巨檔噪音——舊案 held 那題 22 誤放全出自改主程式)。 [test:t_impact_home_cap_for_big_files]
    54	- [S5] 只加不降:事故、帶合約的直接節點、一跳合約間接照原本規則進必推,不因為不是家而被降;不是家、只被反引號提到的節點照原本規則。 [test:t_impact_home_is_additive_only]
    55	- [S6] 推送前的波及計算(`impact --diff`)聚合時保留家的入口與順序;派審查員時的圖譜參考(dispatch-lens 的 diff 與 spec 兩種)也認家。 [test:t_impact_diff_keeps_homes] [test:t_dispatch_lens_includes_homes]
    56	- [S7] 新增旋鈕 `LUMOS_IMPACT_HOME`(預設 1;0=完全照原本),給離線評測對照用,不是使用者旗標(同既有 `LUMOS_IMPACT_*` 慣例)。 [test:t_impact_home_knob_off_is_old_behavior]
    57	- [S8] 顯示:Edit 前推筆記的清單上,家標「★家★」;原本的「★關於★」標示拿掉(它依賴的預標指紋不再影響排序)。 [test:t_impact_hook_shows_home_label]
    58	- [S9] 預標指紋不再影響推筆記;`about-code restamp/revert/migrate-stamp` 指令保留(舊資料與回滾用),說明改寫成「指紋只記標記當時的正文,不影響推筆記」。 [test:t_about_stamp_no_longer_affects_ranking]
    59	- [S10] 評測:用既有評測器跑練習題與保留題,P@8 與「輸出前 3 名必看命中率」都不得比現行低超過 1 個百分點(活語料本身有 ±1pp 漂移);前後數字寫進驗證紀錄。 [manual:上線前後各跑一次 governance/eval/retrieval_eval.py 兩組,數字寫進驗證紀錄]
    60	
    61	### 乙、節點還原把 about_code 設成必要條件
    62	
    63	- [S11] 從程式重建的節點 about_code 至少要有一支檔;`lumos lint` 對這種節點缺 about_code 報錯(提交前的逐篇 lint 會擋)。 [test:t_lint_regen_node_requires_about_code]
    64	- [S12] 節點還原 SOP:第 4 步寫明「about_code 是必要條件,每篇還原節點都要帶 `--code`」;第 6 步出口多一項——這批還原動到的模組,它們的程式檔在健檢 S8 不再列為沒家(真的不該有家的,寫進專案設定 `node_home.ignore` 並說明理由)。快查表(commands/09)與完整版(reference.md)兩處一致。 [test:t_restore_sop_requires_about_code]
    65	- [S13] `lumos new system` 沒帶 `--code` 時多印一句提醒(不擋):不管任何程式檔的節點通常是「主題」不是「模組」;確定要這樣,就在負責範圍講清楚它不管檔的理由。 [test:t_new_system_without_code_reminds]
    66	
    67	## 範圍外(刻意不做)
    68	
    69	- 不動反引號、連結擴展、事故觸發這三條入口,也不改分數公式。
    70	- 不剔除舊反引號造成的誤推——那是舊帳整理(健檢 S9 列著),新寫的由每支檔有家擋。
    71	- 不重開「關於欄位」的模型預標——那是舊案的主案方向;本案用的是每支檔有家驗過的家。
    72	- 不替 POS 專案另建標準答案題(成本高、樣本少);消費專案的效果改看推播漏網量測的週清單。
    73	- 乙只管「從程式重建的節點」;一般手寫的 Systems 節點不強制 about_code(概念型、跨模組的說明篇是合法的),只在 [S13] 提醒。
    74	
    75	## 落點
    76	
    77	- **推筆記那一段**(甲):[[Systems/retrieval-ranking]]——改檔前推筆記的排序本來就記在這篇;實作時把 Edit 前推筆記那支 hook 檔明文加進它管的範圍(那支檔現在掛在棧別提問表態閘與 Codex 接線兩篇底下,都不是講推筆記的)。
    78	- **SOP 那一段**(乙):[[Systems/節點還原]]。
    79	- **lint 那一條**(乙):[[Systems/check-j-regen-guard]]——regen 章的規則集中在這篇。
    80	
    81	## 實務隱患
    82	
    83	- **噪音變多**:家一定推,家很多的檔會把必推名單撐大——[S4] 大檔門檻擋;門檻沿用既有 8,不另校準(REVISIT 見回頭條件)。
    84	- **寫錯的家**:about_code 路徑存在但語意不對(掛錯篇),會把錯的那篇推上來——每支檔有家只驗路徑、不驗語意;靠規則三「寫回要落在家」長期把錯的家曝出來。已排除:不另做語意檢查(舊案走過模型預標,三輪沒收斂)。
    85	- **評測尺量不到**:標準答案題出在本工具鏈圖譜上,最常改的主程式是大檔,認家對它沒有鑑別力——[S10] 只當「不退步」的尺;真正的效果看消費專案的推播漏網週清單(回頭條件)。
    86	- **效能**:Edit 前推筆記那支 hook 外層 30 秒超時、多檔 patch 總預算 20 秒;找家要掃全圖的 about_code——既有的 about 計數已經有快取,本案沿用,不另掃一次。
    87	- **舊專案沒更新**:沒跑 `lumos update` 的專案照舊行為,不會壞。
    88	- **從程式重建的章是自己蓋的**:不蓋 regen 章就完全繞過 [S11](既有天花板,check-j-regen-guard 那篇已記);本案不處理,SOP 第 6 步出口的健檢 S8 是第二道。
    89	- **兩家一致**:Claude 與 Codex 的 Edit 前推筆記都呼叫同一支 lumos,行為一致。
    90	- **不可逆、金流、對外寄送**:不碰。已排除:這案只改讀側排序、lint 與文件,不寫任何正式環境。
    91	
    92	## 驗收怎麼跑
    93	
    94	- 子集:`python3 scripts/test_lumos.py -k impact_home`、`-k impact_pins_order`、`-k dispatch_lens_includes_homes`、`-k about_stamp_no_longer`、`-k regen_node_requires`、`-k restore_sop_requires`、`-k new_system_without_code`、`-k impact_hook_shows_home`。
    95	- 評測:`python3 governance/eval/retrieval_eval.py --goldset governance/eval/retrieval-goldset.json` 與加 `--split held`,上線前後各一次。
    96	
    97	## 回頭條件
    98	
    99	- 消費專案的效果量不到上線當下。REVISIT:2026-10-12 看推播漏網量測的週清單裡「關於欄」那一類(沒推、agent 卻自己讀了、而那篇是那支檔的家),比較上線前後的筆數;沒下降就回頭查家有沒有真的進必推名單
   100	- 大檔門檻 8 是沿用舊數字。REVISIT:2026-10-12 用練習題、保留題重跑一次,並抽三個 POS 專案各五次 Edit 看必推名單有沒有被家撐爆
   101	
   102	## 合約候選(收斂時複核,候選≠已標)
   103	
   104	- 家一定進必推名單(大檔除外,[S2][S4])。
   105	- 只加不降:既有必推項不因為不是家而被降([S5])。
   106	
   107	## 審計修正紀錄

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md | sed -n '28,48p;225,258p;520,550p' && nl -ba scripts/lumos | sed -n '21584,21756p' && nl -ba scripts/lumos | sed -n '21845,22010p' && nl -ba scripts/lumos | sed -n '23045,23148p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
    28	    id: d3
    29	    context: r1 設計層十洞、r2 換尺(日期→正文雜湊)、r3 全是新方案語意與接線(橡皮章/遷移證據/編碼/範例),三輪 70 條放行 0、沒有一條再動方向;再審一輪約 100 萬 token
    30	    why_chosen: r3 的洞全是「spec 講不清」不是「方向錯」,這類寫成會翻紅的測試比再審一輪更能釘住;設計審天花板只證「審查員眼裡無明顯漏洞」,正確性歸下游 code-loop 與測試
    31	    decided: 2026-08-24
    32	    valid: true
    33	  - content: 成績單指標裁乙:改量「輸出前 3 名必看命中率」(out_top3_must),不限固定席;甲案 pin_top3_must 作廢不沿用 key
    34	    id: d4
    35	    context: 調研實證甲案是死表:必看 15/69 坐固定席、事故恆最前,前 3 席組成幾乎不變,觀測一個月只會得到水平線;丙(第四條保送)需先把 about 漏標率壓到零,無新證據不重提
    36	    why_chosen: 乙量的是人打開 hook 先看到的三行,對 about/降噪/合約覆蓋三條線都有感;歸因用 LUMOS_IMPACT_ABOUT=0 離線對照;成本近零
    37	    decided: 2026-08-24
    38	    valid: true
    39	summary: |-
    40	  FLAG:DECISION
    41	  KEY:★甲案收窄(2026-08-23 Enzo 裁,design-loop 三輪到頂後)★——about_code 只做固定席排序+語意欄位基礎,不做降噪;對 P@8 零影響(不計固定席);噪音數不變只變位置;降噪回 A 層另案(★2026-08-24:A 層由 [[Projects/固定席降噪A層_計劃]] 硬合約+參考道實現;扇出二元砍除已試已殺,分級降權未試★)。成績單後裁乙改 out_top3_must
    42	  KEY:主案=語意「關於」欄位 about_code(模型離線預標、雙評審寫入、讀側查欄位可重算);扇出降權/提到的位置降為★過渡方案★。Enzo 裁:字串比對有結構性天花板,要質的提升得信任模型語意
    43	  KEY:★r2 設計層改動★——r1 版「有 about 欄但不含目標檔→降自由席」被實測打穿(事故筆記 hook卸載殘留註冊 改 test_lumos.py 時會被降;加上 about 對必看本有 2/9、3/5 漏標,降級=把必看踢出固定席,「零退化」在有欄節點上不成立)→改「只加分不降級」:about 命中→固定席前排,不命中→照三軸既有路徑。噪音剔除改由巨檔門檻與扇出承擔,about_code 不碰召回。另:回滾改新增子命令 about-code revert(既有 query 無 --field);過期判準改 git 最後改動日期(updated 欄 33% 落後;★此句已被 std-r2 換成正文雜湊,見下一行★)
    44	  KEY:★r1 六洞全折★——「與考卷必看同一把尺」宣稱作廢(「關於」比「必看」嚴,是精確度子集非等價物);讀側打錯靶(固定席三軸:direct/indirect/incident,原只改 direct;實測 E10 八席只一席 direct);範圍 61→83 篇;巨檔門檻=about 命中≥N(暫定 8)關閉判定;過期守衛:r1「併入 Check S、記日期」→ r3 另開迴圈 → ★std-r2 改記正文雜湊(日期/commit 數都表達不了「標記在同日序列的哪一格」,Codex+s1 實證 83 篇上線首日就誤判 2 篇)★;寫入走 refresh_labels 同款雙評審
    45	  KEY:離線驗證(Codex 預標 83 篇)——train 18 噪音零誤放、必看 7/9;held 撞巨檔失效(改 scripts/lumos 那題 22 誤放,排除後 0/60)。★「零誤放」的 distinct 樣本遠小於 18,且 goldset 已換版★
    46	  KEY:誠實天花板——判準文字與考卷裁決都經我手(同源循環,只能靠上線後 held 量一次打破);過擬合風險高(train 8 題);P@8 門檻在新尺上未校準;hook 顯示層要加 about 標示
    47	  DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
    48	verified_by:
   225	
   226	★r1 訂正(s3f1 blocker):這**不是**「與考卷必看同一把尺」★——離線驗證已量出
   227	「關於」比「必看」嚴(train 必看 2/9、held 3/5 被判「不關於」),兩者問的是不同問題:
   228	「關於」=這篇在講這支;「必看」=改這支時該看。`rater-instructions.md` 對「必看」
   229	還限定在「合約/事故/直接規格」子類(s3f6),about_code 判準沒這個範疇。
   230	**正確說法:about_code 是「必看」的一個高精確度子集,不是它的等價物。**
   231	考卷能量到它的「精確度貢獻」(噪音降幾條),量不到它的「召回貢獻」(本來就不是它的目標)。
   232	
   233	### 讀側怎麼用(★r1 大幅改寫★)
   234	
   235	**r1 發現原設計打錯靶(s1f2/s1f3/s1f4 major、s2f1 blocker)**:固定席保送有★三條獨立路徑★——
   236	①`direct` + 合約(`scripts/lumos:14202` `pinned = bool(contract)`)②`indirect` + 合約且 hop≤1
   237	(`:14213`)③`incident`(事故類)不看合約一律保送(`:14178`)。原設計只改①。(行號 std-r1 s2f1 校正)
   238	**實測 E10 改 pre-push:8 席固定席只有 1 席是 direct,6 席是 indirect**——原修法字面上攔不到它們。
   239	
   240	★r2 再改寫(s3f1/s3f2 blocker):r1 版「有欄但不含 → 降自由席」★會讓已標記的節點比沒標更差★★
   241	
   242	r1 版的問題用實測打穿:`Issues/hook卸載殘留註冊`(事故類,`pitfall_when: content:HOOK_ENTRIES`)
   243	改 `scripts/test_lumos.py` 時靠事故路徑無條件保送;但它的 about_code 只列 merge-claude-settings.py
   244	與 lumos(它講的是卸載沒清乾淨,不是針對 test_lumos.py)。照 r1 規則 → 有欄但不含 → **被降**。
   245	**「改 A 出過事」的筆記不會列 B,但改 B 的人看到它不虧——事故路徑的價值正在這裡。**
   246	加上 about_code 對「必看」本就有 2/9、3/5 的漏標,降級規則會把那些必看項主動踢出固定席——
   247	★這是負向作用,「零退化」承諾在有欄的節點上不成立。★
   248	
   249	★改寫後的規則:about_code **只加分、不降級**★
   250	- 節點有 `about_code` 欄且含目標檔 → 標 **`about_hit: true`**;★前提:它已經由三條既有路徑之一進了候選集★
   251	  (沒字串提到、沒圖邊、不是事故觸發的節點,about_code 再命中也不會被掃到——about_code **不是第四條入口**,
   252	  只在既有候選裡重排;impl-r1 s1f3 抓到原句「不論它由哪條路徑進來」會被讀成獨立促升)。
   253	  pinned 者排固定席前段,free 者不動位置
   254	- 節點有 `about_code` 欄但不含目標檔 → **照三條既有路徑判**,該保送還是保送,只是排在 about 命中者之後
   255	- 節點沒有 `about_code` 欄 → 三條既有路徑照舊
   256	
   257	**代價**:精確度來源變成「排序」而非「剔除」——噪音仍在固定席,只是被擠到後面。
   258	對 P@8 無影響(P@8 不計固定席),對 hook 顯示有影響(前排先看到對的)。
   520	   [test 候選:斷言 pins 去掉 about_hit 者後,序列與 `LUMOS_IMPACT_ABOUT=0` 時一致]
   521	3. **過期即不信**——正文雜湊 ≠ stamp 第三段(或無第三段)的節點,其 about_code 視同不存在。重標(`about-code restamp`)後必不過期。
   522	   [test 候選:改正文一字→視同無欄;restamp→恢復;只改 frontmatter→不過期]
   523	4. **批次回滾只動 stamp 第一段 = batch-<日期> 的節點**——人工修正過的(含 `restamp` 過的,第一段已變 `claude/…`)不被誤撤。
   524	   [test 候選:restamp 後 revert --batch 不碰它;★fixture 用三段式值★(s3f7)]
   525	5. **about 判定不覆寫 results 的 `hit` 欄**(impl-r1 s1f2;std-r2 s3f5 升格)——direct 候選的 `hit` 永遠是 body-inline-code/basename-match 來源標記。
   526	   [test 候選:#4 測試⑦]
   527	
   528	## ★調研:必看為什麼只有 8/29 坐固定席(2026-08-24,讀側落地後首查)★
   529	
   530	新指標「固定席前 3 位必看命中率」首量幾乎不動(有無 about 同值),追根究柢把 69 對「必看 × 編輯題」逐對驗了席位:
   531	
   532	| 席位 | 對數 | 說明 |
   533	|---|---|---|
   534	| direct 自由席 | **31(45%)** | ★結構性:全是計劃/驗證類——固定席保送條件=合約或事故,合約只有 Systems 類會標,計劃/驗證類必看**永遠**進不了固定席★ |
   535	| 不在輸出(無查詢文字診斷) | 19 | 抽 9 驗:6 個是門檻/名額截掉(無 query 時詞彙分=0、direct 底分 0.30 過不了動態閾;hook 實際有 query 會撈回部分——考卷實測只漏 3+2)、**3 個是真召回洞** |
   536	| 固定席(合約 direct 9 + 合約 indirect 3 + 事故 3) | 15 | 就是機械保證涵蓋的那面 |
   537	| indirect 自由席 | 4 | — |
   538	
   539	**三個真召回洞的形態**:筆記正文沒提那支檔的路徑、圖上距離 >2(例:自主迴圈的首輪驗證筆記沒寫 `autonomous-loop.sh` 字樣)。
   540	★這正是「影響欄位」(impacts_code,見下一步節)要接的洞——但也只有 3/69,不是主戰場。★
   541	
   542	**含意(2026-08-24 Enzo 裁乙,d4)**:指標改量「輸出前 3 名」(`out_top3_must`,不限固定席)。
   543	首量:train 0.463 / held 0.083 / 全體 0.281——held 爛在固定席噪音 82 條塞滿前三行,表是活的、直指 A 層降噪主戰場。
   544	甲案 pin_top3_must 作廢(history 舊 key 不沿用);丙無新證據不重提。原三選項留痕:
   545	1. 「前 3 席必看命中率」的天花板由「必看有幾個能坐固定席」決定(15/69);about_hit 只重排固定席內部,動不到 31 對自由席必看。
   546	   選項:(a) 接受——固定席=機械保證面,必看召回歸排序,把指標讀成「保證面內的排序品質」;(b) 指標改量「輸出前 3 名」不限固定席;(c) 開第四條保送——已在三輪設計審被拒(about 不是入口),重提要新證據。
   547	2. 31 對自由席必看靠詞彙分競爭——E05 那型(改評測腳本→該看檢索計劃)其實 query 詞彙訊號很強,實測也大多有進前 8(考卷 P@8 0.75);問題不是沒推出來,是「保證」與「推出來」是兩回事,講清楚就好。
   548	
   549	## 誠實缺口
   550	
 21584	    # 8.5 ranked 融合(階段三,spec §3):固定席(事故+含合約 direct+深度內合約 indirect)不占 top_k;
 21585	    # 非固定按 R=0.6L+0.4G 排,過 max(min_score, 0.25×最高非固定分) 閾;姐妹去冗餘於顯示層。
 21586	    if ranked or incidents_only:
 21587	        query = (_payload.get("query") or "") if stdin_payload else ""
 21588	        results = []
 21589	        lane_raw = []   # 參考道原料(--incidents-only 不進 indirect 迴圈也要有定義)
 21590	        # 固定席:事故(kind=incident)恆固定
 21591	        for x in all_incidents:
 21592	            results.append({"node": x["node"], "kind": "incident", "pinned": True,
 21593	                            "score": 1.0, "matched_by": x.get("matched_by"),
 21594	                            "contract": x.get("contract")})
 21595	        gated = False   # 查詢品質閘觸發旗標(未觸發路徑必為 False,防 NameError)
 21596	        if not incidents_only:
 21597	            # query 品質閘(edit面查詢品質閘_計劃 S2):低資訊 query 視同空查詢——
 21598	            # 只覆寫 lex 用局部變數;事故探針 _delta_q 刻意不受閘(安全網寧多勿漏)
 21599	            if query and _impact_query_junk(query):
 21600	                query = ""
 21601	                gated = True
 21602	                print("(query 品質閘:文本為檔頭雜訊/過短,L 臂靜默)", file=sys.stderr)
 21603	            # 詞彙分:對 direct+indirect 候選跑 BM25F(query 為空則全 0)
 21604	            cand = [x["node"] for x in all_direct] + [x["node"] for x in all_indirect]
 21605	            lex = {}
 21606	            if query and cand:
 21607	                _mx = None
 21608	                raw = _rank_score_candidates(env, query, cand)
 21609	                _mx = max((s for _r, s, _h in raw), default=0.0)
 21610	                for _r, s, _h in raw:
 21611	                    lex[_r] = (s / _mx) if _mx > 0 else 0.0
 21612	            eff_depth = depth if depth is not None else 2
 21613	            _dbase = _impact_knob("LUMOS_IMPACT_DIRECT_BASE", 0.30)
 21614	            for x in all_direct:
 21615	                L = lex.get(x["node"], 0.0)
 21616	                pinned = bool(x.get("contract"))   # 含合約的 direct 固定
 21617	                results.append({"node": x["node"], "kind": "direct", "pinned": pinned,
 21618	                                "score": round(_dbase + (1.0 - _dbase) * L, 4), "L": round(L, 4),
 21619	                                "hit": x.get("hit"), "contract": x.get("contract")})
 21620	            _pin_hop = int(_impact_knob("LUMOS_IMPACT_PIN_HOP", 1))
 21621	            # ★pin-denoise-a-v4(2026-08-24,四輪設計審收斂)★:硬合約保送——knob=1 時 indirect 保送只認
 21622	            # INVARIANT/IRREVERSIBLE;RISK·* 類(樞紐筆記搭便車,held 噪音 58/96 的主力)降入「參考道」:
 21623	            # ★獨立容器 lane_raw,自始不進 results★(pinned:False 會被四處「非 pinned=free」分流吃回自由席、
 21624	            # 再被動態門檻砍出輸出——v3 r2 實測);JSON 用獨立頂層鍵 "lane"(決策 d2:沒學過 lane 的讀者
 21625	            # 結構性不受影響,diff 聚合/hook free 桶/守衛全免改)。
 21626	            # ★2026-08-24 考卷轉正預設 1(knob=0 留逃生)★:train LANE_N∈{2,3,5} 不敏感取 3;
 21627	            # 候選臂 held 噪音 82→39(-52%)、out_top3_must 0.083→0.367、must 兩棘輪零退、九關全過。
 21628	            _hard_pin = int(_impact_knob("LUMOS_IMPACT_HARD_PIN", 1))
 21629	            for x in all_indirect:
 21630	                L = lex.get(x["node"], 0.0)
 21631	                hop = x.get("hop", 2)
 21632	                contract = x.get("contract")
 21633	                # 合約固定席 hop 上限(v1.2 旋鈕):合約密集圖(Landmark 考卷實證)hop2 合約
 21634	                # 搭便車氾濫(51 席噪音)——收窄後 hop2 合約降入自由席按分數競爭(L≈0 者被閾殺)
 21635	                if contract and hop <= min(eff_depth, _pin_hop):
 21636	                    if _hard_pin and contract not in ("INVARIANT", "IRREVERSIBLE"):
 21637	                        # RISK·* 降參考道:score 用 indirect 自由席同款 R 公式(常數 0.70 全員同分,
 21638	                        # cap 挑誰會退化成字母序——v3 r3 s1f2);kind 保留 indirect(lane 是欄位不是 kind)
 21639	                        G = 0.60 * min(1.0, 2.0 / (2 ** hop))
 21640	                        lane_raw.append({"node": x["node"], "kind": "indirect", "pinned": False,
 21641	                                         "lane": "soft-guard", "score": round(0.60 * L + 0.40 * G, 4),
 21642	                                         "L": round(L, 4), "hop": hop, "contract": contract})
 21643	                        continue
 21644	                    results.append({"node": x["node"], "kind": "indirect", "pinned": True,
 21645	                                    "score": round(0.40 + 0.30, 4), "L": round(L, 4),
 21646	                                    "hop": hop, "contract": contract})
 21647	                    continue
 21648	                # hop≥2 需 L>底線(遠端節點要足夠詞彙證據背書)
 21649	                if hop >= 2 and L <= _impact_knob("LUMOS_IMPACT_LMIN_HOP2", 0.0):
 21650	                    continue
 21651	                G = 0.60 * min(1.0, 2.0 / (2 ** hop))
 21652	                R = round(0.60 * L + 0.40 * G, 4)
 21653	                results.append({"node": x["node"], "kind": "indirect", "pinned": False,
 21654	                                "score": R, "L": round(L, 4), "hop": hop, "contract": contract})
 21655	        # about_code 語意欄位(工具清單 #4):只標記、不動 pinned;--incidents-only 快速路徑整段跳過
 21656	        if not incidents_only:
 21657	            _impact_mark_about(env, results, rel_file)
 21658	        # 分固定/非固定;非固定過閾+排序+補到 top_k
 21659	        pins = [r for r in results if r["pinned"]]
 21660	        # 固定席內 stable sort:事故永遠最前(std-r1 s1f10),其次 about 命中者,其餘保持三軸原序
 21661	        pins.sort(key=lambda r: (r["kind"] != "incident", not r.get("about_hit", False)))
 21662	        free = [r for r in results if not r["pinned"]]
 21663	        max_free = max((r["score"] for r in free), default=0.0)
 21664	        thresh = max(float(min_score), _impact_knob("LUMOS_IMPACT_DYN_COEF", 0.65) * max_free)
 21665	        free = [r for r in free if r["score"] >= thresh]
 21666	        free.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))
 21667	        # 名額制(v1.1):單體檔洪水按排名剪尾——閾值管品質、名額管上限(gate 對齊 top_k+2=10);
 21668	        # 剪的是 11 名以後,不動前 8 的視野(精度/必看召回不受影響)
 21669	        # PPR 分量(檢索PPR邊權_計劃)已試已殺(2026-07-28 edit 卷 train 網格全負:
 21670	        # baseline nDCG@8 0.9831 vs ppr w0.2/0.4/0.6=0.9817/0.9668/0.9598,b1 純 PPR 與
 21671	        # b2 cochange 邊權同分=邊權零貢獻;free 池中位 3 席使 P@8 對重排零鑑別,裁決依 nDCG)。
 21672	        # 與 A3 同源教訓:本圖的圖傳播訊號打不過調校後的 BM25F 融合;勿憑直覺復活,
 21673	        # 重試須先過同款考卷。詳 Projects/檢索PPR邊權_計劃 墓碑節。
 21674	        _quota = int(_impact_knob("LUMOS_IMPACT_FREE_QUOTA", 10))
 21675	        truncated = max(0, len(free) - min(int(top), _quota))
 21676	        free = free[:min(int(top), _quota)]
 21677	        # R1 直連保底席(2026-08-07,plan:hook必看召回修復;第三桶明文):
 21678	        # 觸發=截斷後最終 free 集零 direct 且存在被閾砍/截的 direct(缺口)。
 21679	        # rescued 恆 pinned:false、threshold/quota 不作用其上、外掛於 free 之後(--top 例外,
 21680	        # 同 pins safety_overflow 精神);tie-break 沿 free.sort 慣例 (-score, hop, node)。
 21681	        # knob:LUMOS_IMPACT_RESCUE_N(2026-08-07 考卷轉正預設 1:held Σmust 12→14、
 21682	        # P@8 0.6389→0.6944 雙升,gate 兩條全過;knob=0 留 A 臂逃生)。
 21683	        # S2 水位謂詞(2026-08-07,plan:連結缺失補全):free 內 direct(排除 pinned;截斷後
 21684	        # 最終集)不足 N 席 → 補 need=max(0, N−count) 席(前案「僅零 direct 觸發」為 N=1 特例,
 21685	        # 向下相容;前案合約候選之改寫經考卷 A/B 重裁,互引留痕見兩計劃節點)。
 21686	        rescued = []
 21687	        # 2026-08-07 水位案考卷轉正 N=3(train 網格 {1,2,3} recall 軸選出;held 確認
 21688	        # Σmust 14→17、P@8 0.6944→0.7130 週閘翻綠;knob 留逃生)
 21689	        _rescue_n = int(_impact_knob("LUMOS_IMPACT_RESCUE_N", 3))
 21690	        _free_direct = sum(1 for r in free if r["kind"] == "direct")
 21691	        _need = max(0, _rescue_n - _free_direct)
 21692	        if _rescue_n > 0 and _need > 0:
 21693	            _free_ids = {id(r) for r in free}
 21694	            dropped = [r for r in results
 21695	                       if r["kind"] == "direct" and not r["pinned"] and id(r) not in _free_ids]
 21696	            dropped.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))
 21697	            for r in dropped[:_need]:
 21698	                rr = dict(r)
 21699	                rr["rescued"] = True
 21700	                rescued.append(rr)
 21701	        # 參考道:產生端 cap(三處輸出同一份,口徑合一——被 cap 砍的必看會誠實掉 must_in_out,棘輪有效)
 21702	        lane_items = []
 21703	        _lane_trunc = 0
 21704	        if lane_raw:
 21705	            lane_raw.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))   # 同 free/rescued 三鍵慣例
 21706	            _lane_n = max(0, int(_impact_knob("LUMOS_IMPACT_LANE_N", 3)))   # 負值防護(同 _rescue_n 的 max(0,…) 慣例;負切片語意是「砍尾」不是上限)
 21707	            lane_items = lane_raw[:_lane_n]
 21708	            _lane_trunc = len(lane_raw) - len(lane_items)
 21709	        # 姐妹去冗餘(顯示層,--json 全量不折)
 21710	        final = pins + free + rescued
 21711	        meta = {"candidates": len(all_direct) + len(all_indirect) + len(all_incidents),
 21712	                "pinned": len(pins), "truncated": truncated, "rescued": len(rescued),
 21713	                "safety_overflow": max(0, len(pins) - int(top))}
 21714	        if lane_raw:
 21715	            meta["lane"] = len(lane_items)
 21716	            meta["lane_truncated"] = _lane_trunc
 21717	        if as_json:
 21718	            out_obj = {"file": rel_file, "results": final, "meta": meta}
 21719	            if lane_items:   # 條件鍵(同 query_gated/stack_questions 慣例):knob=0 或空 → 鍵不存在
 21720	                out_obj["lane"] = lane_items
 21721	            if gated:
 21722	                out_obj["query_gated"] = True
 21723	            # 棧別效能追問(pitfalls棧別效能追問_計劃 T2):完整 ranked 模式(非 incidents-only
 21724	            # 冷卻快速路)且目標檔命中問題表 → 附該棧檢核問(全表);單源=_STACK_PERF_QUESTIONS,hook 只格式化
 21725	            if not incidents_only and not _PITFALL_DIFF_TEST_PAT.search(rel_file):
 21726	                _sk = _stack_key_for_file(rel_file, repo_root_for_lookup)   # .ts/.js 看 package.json 分前後端
 21727	                if _sk:
 21728	                    out_obj["stack_questions"] = {_sk: _STACK_PERF_QUESTIONS[_sk]}
 21729	                    # 觸發式適用性(表態閘 S3):hook 另送原始 delta_text(保留換行;query 那欄是 8000 字/512 詞截斷版,只給詞彙融合)
 21730	                    # → 只列命中 when 的題;沒送(legacy 呼叫)就沒有 applicable 鍵,hook 退回印全表。
 21731	                    _dt = _payload.get("delta_text") if stdin_payload else None
 21732	                    if isinstance(_dt, str):
 21733	                        _cfgq = _stack_questions_config(repo_root_for_lookup)
 21734	                        _app, _meta = _stack_applicability({_sk: _dt.splitlines()}, _cfgq["ask_all_over_lines"])
 21735	                        out_obj["stack_questions_applicable"] = _app
 21736	                        out_obj["stack_questions_meta"] = _meta
 21737	                        if _payload.get("delta_truncated"):
 21738	                            out_obj["delta_truncated"] = True
 21739	            print(json.dumps(out_obj, ensure_ascii=False))
 21740	        else:
 21741	            print(f"改動 {rel_file} — 相關 top(固定席 {len(pins)}):")
 21742	            for r in final:
 21743	                mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{r.get('hop','?')}"}.get(r["kind"], "")
 21744	                ct = f" ★{r['contract']}★" if r.get("contract") else ""
 21745	                pin = " [固定]" if r["pinned"] else ""
 21746	                print(f"  {r['score']:5.2f} {mk} {r['node']}{ct}{pin}")
 21747	            if meta["truncated"]:
 21748	                print(f"  (+{meta['truncated']} 條低分截斷;--json 全量)")
 21749	            if not lane_items and meta.get("lane_truncated"):
 21750	                print(f"  (守衛面參考 {meta['lane_truncated']} 條被 LANE_N cap 全部隱藏——網格消融才會發生)")
 21751	            if lane_items:
 21752	                print(f"守衛面參考(軟標記樞紐,未被本次改動直接證實相關,{len(lane_items)} 條):")
 21753	                for r in lane_items:
 21754	                    print(f"  {r.get('score', 0):5.2f} hop{r.get('hop', '?')} {r.get('node', '?')}  ({r.get('contract', '')})")
 21755	                if meta.get("lane_truncated"):
 21756	                    print(f"  (另有 {meta['lane_truncated']} 條守衛面參考未列出)")
 21845	                                 and isinstance(sync.get("touched_nodes"), list)):
 21846	        return None
 21847	    return data
 21848	
 21849	
 21850	def cmd_impact_diff(diff_range, repo=None, depth=None, top=8, min_score=0.20, as_json=False,
 21851	                    sync_check=False, sync_only=False, from_json=None):
 21852	    """code-loop 橋接:對整段 diff 的每支改動 code 檔跑 ranked impact(query=該檔 hunk 文字),
 21853	    聚合成「受影響功能面」manifest——固定席(合約/事故)全保、非固定取跨檔最高分 top-N。
 21854	    定位=審計員鏡頭(advisory,人判),非自動推播(hook 面 goldset 評測未過線,故不接 hook)。
 21855	    rc: 0=成功 / 2=git 失敗 / 3=vault 缺。
 21856	
 21857	    from_json:吃一份已經算好的結果,不自己算(見 _impact_payload_read)。目前只支援
 21858	    搭 --sync-only 用——推送關卡算一次、同步點名與合約測試閘各讀一次。"""
 21859	    if from_json is not None:
 21860	        _pl = _impact_payload_read(from_json)
 21861	        if _pl is None or _pl.get("sync") is None:
 21862	            return 0          # 失敗隔離:維持同步點名現在的行為(靜默)
 21863	        _print_sync_nudge(_pl["sync"], _pl.get("range") or diff_range)
 21864	        return 0
 21865	    import json as _json
 21866	    import subprocess as _sp
 21867	    if diff_range == "staged":
 21868	        # 圖譜同步覆蓋(2026-08-22):pre-commit 要對「這次 commit 的內容」算波及,用 staged 代替 range
 21869	        diff_range = "--staged"
 21870	    elif diff_range.startswith("-"):
 21871	        # 同 pitfalls/cochange-check:'-' 開頭值會被 git 誤認成選項,查詢命令 rc2 拒收
 21872	        print("擋下:--diff 的值不能用 - 開頭(會被當成選項)", file=sys.stderr)
 21873	        return 2
 21874	    repo_root = Path(repo) if repo else None
 21875	    if repo_root is None:
 21876	        for cand in (Path.cwd(), *Path.cwd().parents):
 21877	            if (cand / ".git").exists():
 21878	                repo_root = cand
 21879	                break
 21880	    if repo_root is None or not (repo_root / ".git").exists():
 21881	        print("擋下:找不到 git 專案,用 --repo 指定", file=sys.stderr)
 21882	        return 2
 21883	    # core.quotePath=false:CJK 檔名不轉義加引號(否則 startswith/endswith 過濾全失效,r2 panel major)
 21884	    r = _sp.run(["git", "-C", str(repo_root), "-c", "core.quotePath=false",
 21885	                 "diff", "--name-only", diff_range], capture_output=True, text=True, errors="replace")
 21886	    if r.returncode != 0:
 21887	        print(f"擋下:git 算不出差異: {r.stderr.strip()[:200]}", file=sys.stderr)
 21888	        return 2
 21889	    files = []
 21890	    for f in r.stdout.splitlines():
 21891	        f = f.strip()
 21892	        if not _impact_diff_seed_ok(f):
 21893	            continue
 21894	        # 已刪檔不跳過:反查靠「節點 body 引用該路徑」而非檔案存在——
 21895	        # 刪除/改名正是合約節點最該被推到審計員眼前的時刻(r1 codex major)
 21896	        files.append(f)
 21897	    merged = {}          # node -> entry(跨檔取最高分;pinned 任一檔 pinned 即 pinned)
 21898	    per_file_meta = []
 21899	    import io, contextlib
 21900	    _vault = _vault_in(repo_root)
 21901	    # ★沒有圖譜就直接說,不要印「0 篇」裝作查過了★(2026-09-07 全 repo 審視 #9)
 21902	    #
 21903	    # 出身:這條路原本只在**逐檔迴圈裡**才發現沒圖譜——而「這個範圍 0 個檔」時迴圈根本不跑,
 21904	    # 於是一路走到最後印出「固定席 0 + top 0」並回成功。
 21905	    # ★對新手最危險的就是這個★:同一件事(找不到圖譜),另外兩種問法一個回 rc3、一個回 rc2
 21906	    # 並印白話擋下,只有這條印「0 篇」**看起來像查過了**——而它根本沒有圖譜可查。
 21907	    # 文件本來就寫著這條路會回「圖譜缺」,只是零檔時走不到。
 21908	    if _vault is None:
 21909	        return _no_vault_msg()
 21910	    _env_shared = Env(_vault)   # 建一次,逐檔復用(r1 N+1)
 21911	    for f in files:
 21912	        d = _sp.run(["git", "-C", str(repo_root), "-c", "core.quotePath=false",
 21913	                     "diff", diff_range, "--", f], capture_output=True, text=True, errors="replace")
 21914	        hunk = " ".join(l[1:].strip() for l in d.stdout.splitlines()
 21915	                        if l[:1] in "+-" and not l.startswith(("+++", "---")))[:4000]
 21916	        buf = io.StringIO()
 21917	        with contextlib.redirect_stdout(buf):
 21918	            rc = cmd_impact(f, repo=str(repo_root), depth=depth, as_json=True,
 21919	                            ranked=True, top=top, min_score=min_score,
 21920	                            payload={"query": hunk, "prospective": {}},
 21921	                            preloaded=(_vault, _env_shared) if _env_shared is not None else None)
 21922	        if rc == 3:
 21923	            print("IMPACT-DEBUG: vault 找不到(rc3)", file=sys.stderr)
 21924	            return 3
 21925	        if rc != 0:
 21926	            continue
 21927	        try:
 21928	            data = _json.loads(buf.getvalue().strip().splitlines()[-1])
 21929	        except (ValueError, IndexError):
 21930	            continue
 21931	        _pm = {"file": f, **data.get("meta", {})}
 21932	        if data.get("query_gated"):
 21933	            _pm["query_gated"] = True   # 觀測欄聚合轉發(r1 f5:code-loop 鏡頭可見)
 21934	        per_file_meta.append(_pm)
 21935	        for x in data.get("results", []):
 21936	            cur = merged.get(x["node"])
 21937	            if cur is None:
 21938	                merged[x["node"]] = {**x, "files": [f]}
 21939	            else:
 21940	                if f not in cur["files"]:
 21941	                    cur["files"].append(f)
 21942	                pinned = cur["pinned"] or x.get("pinned", False)
 21943	                if x["score"] > cur["score"]:
 21944	                    # 整項以勝出結果重建(避免 hop/L 舊值殘留成幽靈欄位,r1 s4 minor)
 21945	                    merged[x["node"]] = {**x, "files": cur["files"], "pinned": pinned}
 21946	                else:
 21947	                    cur["pinned"] = pinned
 21948	    pins = sorted([v for v in merged.values() if v["pinned"]],
 21949	                  key=lambda v: (-v["score"], v["node"]))
 21950	    free = sorted([v for v in merged.values() if not v["pinned"]],
 21951	                  key=lambda v: (-v["score"], v["node"]))[:int(top)]
 21952	    # 落成位置閉環(sync-check):預期受影響節點 ∩ 分支實際動過的圖譜節點——
 21953	    # 「這功能被改了,它的節點卻沒動」= 受影響未同步清單(advisory,人判;固定席可信度高、自由席≈P@8 .70)
 21954	    sync = None
 21955	    if sync_check:
 21956	        _vault_name = _vault.name if _vault is not None else None
 21957	        touched = set()
 21958	        if _vault_name:
 21959	            _prefix = f"docs/{_vault_name}/"
 21960	            for f2 in r.stdout.splitlines():
 21961	                f2 = f2.strip().strip('"')
 21962	                if f2.startswith(_prefix) and f2.endswith(".md"):
 21963	                    touched.add(f2[len(_prefix):])
 21964	        missing = [v for v in (pins + free) if v["node"] not in touched]
 21965	        sync = {"touched_nodes": sorted(touched),
 21966	                "missing": [{"node": v["node"], "pinned": v["pinned"],
 21967	                             "score": v["score"], "files": v["files"]} for v in missing]}
 21968	    if as_json:
 21969	        print(_json.dumps({"range": diff_range, "files": files,
 21970	                           "results": pins + free,
 21971	                           **({"sync": sync} if sync is not None else {}),
 21972	                           "meta": {"files": len(files), "pinned": len(pins),
 21973	                                    "free_kept": len(free),
 21974	                                    "free_total": sum(1 for v in merged.values() if not v["pinned"]),
 21975	                                    "per_file": per_file_meta}}, ensure_ascii=False))
 21976	        return 0
 21977	    if sync_only and sync is not None:
 21978	        _print_sync_nudge(sync, diff_range)
 21979	        return 0
 21980	    print(f"受影響功能面({diff_range};{len(files)} 檔;固定席 {len(pins)}+top {len(free)}——審計鏡頭,人判):")
 21981	    for v in pins + free:
 21982	        mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{v.get('hop','?')}"}.get(v["kind"], "")
 21983	        ct = f" ★{v['contract']}★" if v.get("contract") else ""
 21984	        pin = " [固定]" if v["pinned"] else ""
 21985	        print(f"  {v['score']:5.2f} {mk} {v['node']}{ct}{pin}  ←{','.join(v['files'][:3])}")
 21986	    if not merged:
 21987	        print("  (無節點引用這些檔——圖譜對此 diff 無覆蓋)")
 21988	    if sync is not None:
 21989	        _print_sync_nudge(sync, diff_range)
 21990	    return 0
 21991	
 21992	
 21993	def _print_sync_nudge(sync, diff_range, cap=8):
 21994	    """落成核對的唯一呈現(2026-08-22 架構對齊席抓到三套並存後收斂成這一份):
 21995	    固定席(合約/事故/直接相依)優先、最多 cap 篇;hooks(pre-commit/pre-push/Stop)只呼叫,不自己重排。"""
 21996	    miss = sorted(sync["missing"], key=lambda m: (not m["pinned"], -m.get("score", 0)))
 21997	    print(f"\n落成核對(這批動過 {len(sync['touched_nodes'])} 篇筆記):")
 21998	    if not miss:
 21999	        print("  ✓ 預期受影響的筆記全數已同步")
 22000	        return
 22001	    pinned = [m for m in miss if m["pinned"]]
 22002	    print(f"  提醒:下面這些筆記跟改到的程式碼直接相關(合約 / 事故 / 直接相依),這批沒動:" if pinned
 22003	          else "  提醒:下面這些筆記可能受影響,這批沒動(自由席,可信度較低,人判):")
 22004	    for v in miss[:cap]:
 22005	        mark = "⚠必看" if v["pinned"] else "  "
 22006	        print(f"  {mark} {v['node']}  ←{','.join(v['files'][:2])}")
 22007	    if len(miss) > cap:
 22008	        print(f"  … 還有 {len(miss) - cap} 篇(lumos impact --diff {diff_range} --sync-check --json 看全部)")
 22009	    print("  確定不受影響就略過;受影響的現在補。這裡只提醒不擋。")
 22010	
 23045	        keys = sum(1 for l in summ.splitlines() if l.strip().startswith("KEY:") and l.strip() != "KEY:")
 23046	        contracts = len(_lens_contract_lines(summ, cap=10 ** 6))   # 同派工鏡頭的合約行判法,不另寫一條(代碼審 r1 架構席)
 23047	        files = len([a for a in n["about"] if (Path(root) / a).is_file()])
 23048	        out.append(f"  - {it}:已存在;掛 {plans} 份計劃、{keys} 行 KEY、{contracts} 條合約、管 {files} 支檔、"
 23049	                   + ("有寫負責範圍" if _nodehome_resp_ok(n["resp"]) else "沒寫負責範圍"))
 23050	    return out
 23051	
 23052	
 23053	def cmd_dispatch_lens_spec(spec_path, repo=None, as_json=False, cap=8, max_lines=400):
 23054	    """設計審的派工鏡頭(2026-09-05 第二輪審視六修 d2):設計審沒有 diff 範圍,改從計劃筆記本身算——
 23055	    ①計劃提到的程式檔(存在的,最多 5 個)各跑一次 impact 取固定席節點;②計劊直接 [[連結]] 的 Systems/Issues 節點。
 23056	    從工作樹讀(計劃就是工作樹上的東西);不快取(計劃常改)。手貼那條路實測 209 份派工詞只有 14 份有貼,所以機器來。"""
 23057	    import json as _json, io, contextlib, time as _time
 23058	    _t0 = _time.monotonic()
 23059	    start = Path(repo) if repo else Path.cwd()
 23060	    r = _lens_git(start, "rev-parse", "--show-toplevel")
 23061	    if r is None or r.returncode != 0 or not r.stdout.strip():
 23062	        print(f"擋下:{start} 不在 git 專案裡", file=sys.stderr)
 23063	        return 2
 23064	    root = Path(r.stdout.strip())
 23065	    sp = Path(spec_path)
 23066	    if not sp.is_absolute():
 23067	        sp = root / sp
 23068	    try:   # 外家 r1 M3:計劃筆記必須在 repo 內(/etc/hosts 這種 rc0 讀進來是專案邊界破口)
 23069	        sp.resolve().relative_to(root.resolve())
 23070	    except (ValueError, OSError):
 23071	        print(f"擋下:計劃筆記不在這個 repo 裡 {spec_path}", file=sys.stderr)
 23072	        return 2
 23073	    if not sp.is_file():
 23074	        print(f"擋下:計劃筆記不存在 {spec_path}", file=sys.stderr)
 23075	        return 2
 23076	    try:
 23077	        text = sp.read_text(encoding="utf-8", errors="replace")
 23078	    except OSError as e:
 23079	        print(f"擋下:計劃筆記讀不到({e.__class__.__name__})", file=sys.stderr)
 23080	        return 2
 23081	    slugs = sorted(p.name for p in (root / "docs").glob("*-knowledge") if p.is_dir()) if (root / "docs").is_dir() else []
 23082	    if not slugs:
 23083	        print("擋下:repo 裡沒有 docs/*-knowledge", file=sys.stderr)
 23084	        return 3
 23085	    vault_rel = f"docs/{slugs[0]}/"
 23086	    # ① 計劃提到的程式檔
 23087	    code_files, seen = [], set()
 23088	    for m in _LENS_SPEC_CODE_RE.findall(text):
 23089	        cand = m.rstrip(".,;:)」』】")
 23090	        if cand in seen or cand.endswith(".md"):
 23091	            continue
 23092	        p = root / cand
 23093	        try:   # 外家 r1 M3:scripts/../../x 這種穿越不收
 23094	            inside = p.resolve().relative_to(root.resolve()) is not None
 23095	        except (ValueError, OSError):
 23096	            inside = False
 23097	        if inside and p.is_file():
 23098	            seen.add(cand); code_files.append(cand)
 23099	        if len(code_files) >= _LENS_SPEC_MAX_FILES:
 23100	            break
 23101	    # ② 計劃直接連結的節點
 23102	    linked = []
 23103	    for m in re.findall(r"\[\[((?:Systems|Issues)/[^\]|#]+)", text):
 23104	        node = m.strip()
 23105	        if node not in linked and (root / vault_rel / f"{node}.md").is_file():
 23106	            linked.append(node)
 23107	    # ③ impact 取固定席(有預算)
 23108	    pinned = {}
 23109	    skipped_files, too_generic = [], []
 23110	    for f in code_files:
 23111	        if _time.monotonic() - _t0 > _LENS_SPEC_BUDGET:
 23112	            skipped_files.append(f); continue
 23113	        remain = _LENS_SPEC_BUDGET - (_time.monotonic() - _t0)
 23114	        try:   # 外家 r1 M1:預算不能只在呼叫前看——單次 impact 也可能 31 秒;子行程帶剩餘秒數 timeout
 23115	            import subprocess as _sp
 23116	            rr = _sp.run([sys.executable, str(Path(__file__).resolve()), "impact", "--file", f, "--repo", str(root), "--json"],
 23117	                         capture_output=True, text=True, timeout=max(1.0, remain))
 23118	            data = _json.loads(rr.stdout.strip().splitlines()[-1]) if rr.returncode == 0 and rr.stdout.strip() else {}
 23119	        except Exception:
 23120	            skipped_files.append(f); continue
 23121	        # impact --file 的 JSON 形狀是 {direct,indirect,incidents}(不是 --diff 的 results/pinned):
 23122	        # 固定席=直接相依全部 + 事故全部 + 帶合約的一跳間接(與 --diff 的 pinned 語意對齊)
 23123	        picks = [(v, "direct") for v in data.get("direct", []) if isinstance(v, dict)]
 23124	        picks += [(v, "incident") for v in data.get("incidents", []) if isinstance(v, dict)]
 23125	        picks += [(v, "indirect") for v in data.get("indirect", []) if isinstance(v, dict) and v.get("contract") and v.get("hop", 99) <= 1]
 23126	        # 太泛的檔(像本 repo 的 scripts/lumos 單檔 CLI、總測試檔)一個檔就牽 100+ 篇,附了等於沒附:超過上限的整檔略過並在頭部說明
 23127	        if len(picks) > _LENS_SPEC_MAX_PER_FILE:
 23128	            too_generic.append(f"{f}({len(picks)} 篇)"); continue
 23129	        for v, kind in picks:
 23130	            if not v.get("node"):
 23131	                continue
 23132	            node = str(v["node"])[:-3] if str(v["node"]).endswith(".md") else str(v["node"])
 23133	            if node.startswith("Projects/"):   # 別的計劃不是合約也不是事故,不進固定席
 23134	                continue
 23135	            pinned.setdefault(node, {"kind": _LENS_KIND.get(kind), "contract": _lens_contract_class(v), "files": [f]})
 23136	            if f not in pinned[node]["files"]:
 23137	                pinned[node]["files"].append(f)
 23138	    def _rank(v):
 23139	        return (0 if v.get("kind") == _LENS_KIND["incident"] else 1 if v.get("contract") else 2 if v.get("kind") == _LENS_KIND["direct"] else 3)
 23140	    listed = [{"node": n, **{"kind": "計劃連結", "contract": None, "files": []}, **pinned.get(n, {}), "kind": "計劃連結" + (f"+{pinned[n]['kind']}" if n in pinned and pinned[n].get("kind") else "")} for n in linked]   # 相容:不用 dict |(那是 3.9+,寫這行時專案宣告 ≥3.8;2026-09-06 宣告訂正為 ≥3.9,此寫法保留可用)
 23141	    listed += [{"node": n, **v} for n, v in sorted(pinned.items(), key=lambda kv: _rank(kv[1])) if n not in linked]
 23142	    landing = _nodehome_landing_sizes(root, vault_rel, text)   # [S22] 計劃寫的落點每一篇現在多大
 23143	    bound_status, _bidx = "ok", None
 23144	    try:
 23145	        _bidx = _platform_test_index(root)
 23146	    except Exception:
 23147	        bound_status = "skipped-no-config"
 23148	    lines = []

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba scripts/hooks/claude/impact-hook.py | sed -n '625,655p' && nl -ba governance/eval/retrieval_eval.py | sed -n '278,290p;430,480p' && nl -ba scripts/hooks/pre-commit | sed -n '70,125p' && nl -ba scripts/lumos | sed -n '4325,4410p' && nl -ba governance/eval/retrieval-goldset.json | sed -n '1,8p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
   625	    lines.append("")
   626	    lines.append(_INJECT_INSTRUCTION)
   627	    return _frame_injected("\n".join(lines))
   628	
   629	
   630	def build_ranked_context(data: dict) -> str:
   631	    """v1.1:把 ranked 輸出({results,meta})轉成降噪清單文字。固定席在前(合約/事故),
   632	    非固定帶分數;截斷數照 meta 標注。尾附棧別效能追問(若 lumos 輸出帶 stack_questions——
   633	    單源在 scripts/lumos 的 _STACK_PERF_QUESTIONS,本 hook 只格式化不持有內容)。"""
   634	    lines: list[str] = []
   635	    res = data.get("results", [])
   636	    meta = data.get("meta", {})
   637	    pins = [x for x in res if x.get("pinned")]
   638	    free = [x for x in res if not x.get("pinned") and not x.get("rescued")]
   639	    rescued = [x for x in res if x.get("rescued")]
   640	    if pins:
   641	        lines.append(f"必看——這 {len(pins)} 篇帶著不能破壞的合約或出過事故:")
   642	        for x in pins:
   643	            mk = {"incident": "⚠事故", "direct": "直接", "indirect": f"hop{x.get('hop','?')}"}.get(x.get("kind"), "")
   644	            ct = f" {_contract_label(x['contract'])}" if x.get("contract") else ""
   645	            mb = f"  ({_match_label(x['matched_by'])})" if x.get("matched_by") else ""
   646	            # about_code 語意欄位命中(工具清單 #9):讀 about_hit(只在 True 時存在),不碰既有 hit 來源標記
   647	            ab = "★關於★" if x.get("about_hit") else ""
   648	            lines.append(f"  {ab}{mk}{ct} {_plain_label(x.get('node'))}{mb}")
   649	    if free:
   650	        lines.append(f"可能相關的 {len(free)} 篇(依關聯度排序):")
   651	        for x in free:
   652	            mk = {"direct": "直接", "indirect": f"hop{x.get('hop','?')}"}.get(x.get("kind"), "")
   653	            lines.append(f"  {x.get('score',0):.2f} {mk} {_plain_label(x.get('node'))}")
   654	    if rescued:
   655	        # R1 直連保底(plan:hook必看召回修復):分數不過閾但為僅有的直連節點——信心層級不同於排序席
   278	    print(f"⚠ snapshot worktree 失敗({r.stderr.strip()[:80]})", file=sys.stderr)
   279	    return False
   280	
   281	
   282	def output_top3_must(res, lab):
   283	    """★成績單乙案(2026-08-24 Enzo 裁):輸出前 3 名的必看命中率★(Projects/固定席扇出降權_計劃 調研節)。
   284	    量的是「人打開 hook 先看到的三行是不是該看的」——不限固定席(甲案 pin_top3_must 是死表:
   285	    必看 15/69 坐固定席、事故恆最前,前 3 席組成幾乎不變)。res 順序=impact 輸出順序(pins→free→rescued)。
   286	    = 前 3 項裡標 2 的個數 / min(3, 該題標 2 總數);沒標 2 → None。只印、進 verdict/history,★不進 gate★。
   287	    歸因:數字動了要分是 about 還是排序,拿 LUMOS_IMPACT_ABOUT=0 離線對照。"""
   288	    must_total = sum(1 for v in lab.values() if v == 2)
   289	    if must_total == 0:
   290	        return None
   430	        lab = _labels_of(gs, cid)
   431	        if not lab or not any(v >= 1 for v in lab.values()):
   432	            continue
   433	        # impact 自行從 --repo 解析 vault(不吃全域 --vault)→ 快照釘定須走 --repo(r1 終審親驗)
   434	        # 呼叫收斂進 edit_universe(與評測母體同源,標註刷新 T2);None=file-gone/不可解,照舊跳。
   435	        res = edit_universe(case)
   436	        if res is None:
   437	            continue
   438	        pins, free, lane_items = split_buckets(res)   # v4:free 不含 lane(P@8 母體);out_nodes 含 lane(下方讀完整 res)
   439	        row = {"id": cid, "split": case["split"], "n_free": len(free), "n_pin": len(pins)}
   440	        # edit 面 nDCG 沿用候選集自證 IDCG:三排序共用同一 free 集,相對比較有效;
   441	        # 絕對值偏高(漏檢不罰),不得跨面引用(r1 panel s4)。
   442	        orders = {
   443	            "fusion": sorted(free, key=lambda x: (-x["score"], x["node"])),
   444	            "bm25": sorted(free, key=lambda x: (-x.get("L", 0.0), x["node"])),
   445	            "graph": sorted(free, key=lambda x: (-_graph_score(x), x["node"])),
   446	        }
   447	
   448	        n_rel_free = sum(1 for x in free if lab.get(x["node"], 0) >= 1)
   449	        for name, order in orders.items():
   450	            labels = [lab.get(x["node"], 0) for x in order]
   451	            kk = min(k, len(labels)) or 1
   452	            row[f"{name}_p"] = round(precision_at_k(labels, kk), 4) if labels else None
   453	            row[f"{name}_ndcg"] = round(ndcg_at_k(labels, k), 4) if labels else None
   454	            # condensed([S1]):窗=free 前 k(與 _touched_edit 同界)
   455	            _win = [x["node"] for x in order[:k]]
   456	            _judged, _cov, _valid = _condense(_win, lab, k)
   457	            row[f"{name}_cov"] = _cov
   458	            if _valid and _judged:
   459	                _kk = min(k, len(_judged))
   460	                row[f"c_{name}_p"] = round(precision_at_k(_judged, _kk), 4)
   461	                row[f"c_{name}_ndcg"] = round(ndcg_at_k(_judged, k), 4)
   462	            else:
   463	                row[f"c_{name}_p"] = row[f"c_{name}_ndcg"] = None
   464	        row["n_rel_free"] = n_rel_free
   465	        # must-see 兩指標分開記(r1 panel codex blocker:混稱=證據失真):
   466	        # in_out=出現在輸出(含自由席,top-k 聚合下可能被截) / pinned=真固定席(唯一機械保證)
   467	        out_nodes = {x["node"] for x in res}
   468	        pin_nodes = {x["node"] for x in pins}
   469	        must = [n for n, v in lab.items() if v == 2]
   470	        row["must_total"] = len(must)
   471	        row["must_in_out"] = sum(1 for n in must if n in out_nodes)
   472	        row["must_pinned"] = sum(1 for n in must if n in pin_nodes)
   473	        # 顯式三態([S1]④/[S3b]):未判 or 判0 → 噪音——不依賴 lab.get 殘影,
   474	        # 語意=固定席理應被判過,沒判過就該進補標(condensed 不適用於此,刻意分家)
   475	        row["pin_noise"] = sum(1 for x in pins
   476	                               if x["node"] not in lab or lab[x["node"]] == 0)
   477	        row["out_top3_must"] = output_top3_must(res, lab)   # #10 乙案:輸出前 3 名必看命中率(res=人看到的順序)
   478	        rows.append(row)
   479	    return rows
   480	
    70	    | grep -E '^\+[[:space:]]*(date|created|updated|decided|ended):[[:space:]]*"[0-9]{4}-[0-9]{2}-[0-9]{2}"' || true)"
    71	  if [[ -n "$polluted" ]]; then
    72	    {
    73	      echo ""
    74	      echo "擋下:有筆記的日期欄位被加上了引號(例如 created: \"2026-08-21\")。"
    75	      echo "這幾乎都是某個編輯工具順手改的,不是人打的;它會讓日期欄位變成純文字,而且通常整篇欄位順序都被重排——這種 diff 沒辦法審。"
    76	      echo ""
    77	      echo "被改到的行:"
    78	      echo "$polluted" | head -5 | sed 's/^/   /'
    79	      echo ""
    80	      echo "看完整改動:"
    81	      echo "   git diff --cached -- ${GRAPH_ROOT}"
    82	      echo "還原那個檔:"
    83	      echo "   git checkout -- <檔案>"
    84	      echo "真的是刻意要這樣(非常少見)→ git commit --no-verify"
    85	      echo ""
    86	    } >&2
    87	    exit 1
    88	  fi
    89	fi
    90	
    91	# Gate L: staged 圖譜 .md 逐檔 lumos lint (2026-08-21 體檢 #6)
    92	# 為什麼:lint 自 2026-06 起沒有任何 hook/CI 呼叫,它的每條鐵則(YAML list/白名單/枚舉/frontmatter
    93	# 閉合)全靠人記得跑——「有機制,沒接線」。硬擋:lint rc≠0 即擋,訊息原樣轉出。
    94	# 只跑 staged 的圖譜檔(每檔 <1s),不跑全 vault。找不到 python/lumos → 跳過(與 Gate CC 同語意)。
    95	if [[ -n "${CC_PY:-}" && -f "$REPO_ROOT/scripts/lumos" ]]; then
    96	  lint_fail=0
    97	  while IFS= read -r f; do
    98	    [[ -z "$f" ]] && continue
    99	    [[ -f "$f" ]] || continue          # 刪除的檔不 lint
   100	    # ★傳 vault 相對路徑、去 .md★——lumos lint 的精確比對鍵是 vault 相對的「Systems/foo」;
   101	    # 丟 repo 相對路徑會落到 stem 查找,同檔名不同資料夾時 lint 到別的節點、壞的放行(code-loop r1 s1)。
   102	    rel="${f#$GRAPH_ROOT/}"; rel="${rel%.md}"
   103	    if ! out="$("$CC_PY" "$REPO_ROOT/scripts/lumos" lint "$rel" 2>&1)"; then
   104	      lint_fail=1
   105	      { echo ""; echo "擋下:這篇筆記的格式檢查沒過——$f"; echo "$out" | sed 's/^/   /'; } >&2
   106	    fi
   107	  done < <(echo "$STAGED" | grep -E "^${GRAPH_ROOT}/.*\.md$" || true)
   108	  if [[ "$lint_fail" == 1 ]]; then
   109	    { echo ""; echo "格式錯的筆記進了版控,之後的工具會讀錯(合約標記消失、連結變鬼節點)。照上面的提示修好再 commit。"; echo "真的要先進去 → git commit --no-verify,並在訊息裡留一句為什麼。"; echo ""; } >&2
   110	    exit 1
   111	  fi
   112	fi
   113	
   114	
   115	# Gate H: 每支檔有家(2026-09-11,Projects/每支檔有家_計劃 [S25]):每支程式檔要有一篇管它的節點、
   116	# 節點只准寫自己家的檔、寫回要落在改動檔的家——新違規擋,舊帳交給健檢提醒。判定全在 lumos 裡,這裡只呼叫。
   117	# ★要放在「改程式沒動圖譜」那道之前★:那道只要有圖譜筆記加進索引就提早放行離開,放後面等於只在最不需要的時候才跑。
   118	# 合併提交由 lumos 自己判斷跳過(推送前會把合併的結果整段查一次)。
   119	# 「該動哪篇」的點名(原本在這裡呼叫 impact --sync-only,以反引號為種子)也改由它照家算——
   120	# 反引號那一套會把人推回寫了一堆別人檔名的大雜燴節點(計劃「為什麼」第 3 條)。
   121	# rc1=新違規擋;其他非零(lumos 自己出錯)=放行,這道不因為環境壞了擋人。
   122	if [[ -n "${CC_PY:-}" && -f "$REPO_ROOT/scripts/lumos" ]]; then
   123	  nh_rc=0
   124	  "$CC_PY" "$REPO_ROOT/scripts/lumos" home check --staged --repo "$REPO_ROOT" || nh_rc=$?
   125	  [[ "$nh_rc" -eq 1 ]] && exit 1
  4325	            warns.append(f"這篇掛了 {len(_scope_tags)} 個 scope/ 標籤,規矩是一篇一個主類、真橫跨兩類才准第二個:"
  4326	                         "留下最能代表它的,其餘拿掉(lumos remove <節點> tags scope/<值>)")
  4327	        for tg in _scope_tags:
  4328	            if tg.split("/", 1)[1] not in _sp["values"]:
  4329	                warns.append(f"scope 標籤 {tg!r} 不在這個專案宣告的值域裡({_menu}):"
  4330	                             "打錯字就改成表內的值,真的要新類就先去 .lumos/config.json 的 scope.values 登記")
  4331	
  4332	    # decisions 結構守衛(2026-07-29 外審實錘:id 縮排吞進 content block,parser 靜默降級、
  4333	    # doctor 全綠——「綠燈≠schema 有效」的活例。以正牌 parse_decisions 驗:
  4334	    # 壞型一(sibling 被吞)→ content 空;壞型二(entry 非 `- key:` 形)→ 整條被靜默丟棄=條數對不上)
  4335	    try:
  4336	        _fm_lines, _ = split_frontmatter((env.vault / rel).read_text(encoding="utf-8"))
  4337	    except OSError:
  4338	        _fm_lines = None
  4339	    if _fm_lines and any(re.match(r"^decisions:\s*$", _l) for _l in _fm_lines):
  4340	        _parsed = parse_decisions(_fm_lines)
  4341	        _raw_items = 0
  4342	        _in = False
  4343	        for _l in _fm_lines:
  4344	            if re.match(r"^decisions:\s*$", _l):
  4345	                _in = True
  4346	                continue
  4347	            if _in and _l.strip() and not _l.startswith(" "):
  4348	                _in = False
  4349	            if _in and re.match(r"^  -\s", _l):
  4350	                # 只認 entry 縮排層(恰 2 空格):alternatives_considered 等巢狀清單(≥4 空格)
  4351	                # 不是決策條目——2026-08-05 Landmark 回填實戰:照 ADR 規範寫巢狀清單被誤報壞損
  4352	                _raw_items += 1
  4353	        if _raw_items != len(_parsed):
  4354	            errs.append(f"decisions 格式跑掉了:寫了 {_raw_items} 條、工具只認得出 {len(_parsed)} 條,其他等於白寫"
  4355	                        "(每條要以 `- id:`/`- content:` 起頭;別手改,用 lumos decision-add 寫入)")
  4356	        for _di, _d in enumerate(_parsed):
  4357	            if not str(_d.get("content") or "").strip():
  4358	                errs.append(f"第 {_di} 條 decisions 沒有內容,通常是旁邊欄位縮排錯、被吞進上一欄了——檢查縮排或改用 lumos decision-add 重寫")
  4359	
  4360	    # 狀態標籤漂移守衛:status 欄位 vs tags 的 status/*(反正規化的完整性檢查,
  4361	    # 兜住繞過 set status 同步的寫入路徑;見 Projects/狀態標籤同步守衛_計劃)
  4362	    _st = n.fields.get("status")
  4363	    if isinstance(_st, str) and _st.strip():
  4364	        for _tg in as_list(n.fields.get("tags")):
  4365	            if isinstance(_tg, str) and _tg.startswith("status/") and _tg != f"status/{_st.strip()}":
  4366	                errs.append(f"status 欄位({_st})和狀態標籤({_tg})寫的不一樣(漂移),靠標籤篩狀態會抓錯——用 lumos set <節點> status <值> 改,兩邊會自動同步")
  4367	
  4368	    _regen_val = n.fields.get("regen")
  4369	    _lint_is_regen = isinstance(_regen_val, str) and bool(_regen_val.strip())
  4370	
  4371	    for raw in summ.split("\n"):
  4372	        line = raw.strip()
  4373	        if not line:
  4374	            continue
  4375	        ms = SYMBOLISH_RE.match(line)
  4376	        if ms and ms.group(1) not in SYMBOL_NAMES:
  4377	            warns.append(f"非標準符號行『{ms.group(1)}:』,看起來像打錯字,這行不會被當成摘要——標準符號是 {'/'.join(sorted(SYMBOL_NAMES))}")
  4378	        for mark, rx in (("★INVARIANT★", INVARIANT_RE), ("★DEBT★", DEBT_RE)):
  4379	            if mark in line and not rx.match(line):
  4380	                # 雙報消歧 predicate(Check J):regen 節點的 KEY:推測:★INVARIANT★ 由 J 專屬訊息
  4381	                # 接手,跳過 generic 位置錯誤(同一行恰一則;非 regen 節點 generic 保留=兜底)。
  4382	                # 既有迴圈只含 INVARIANT/DEBT、無 IRREVERSIBLE → 消歧只需此分支。
  4383	                if (_lint_is_regen and REGEN_PREFIX_RE.match(line)
  4384	                        and ("★INVARIANT★" in line or "★IRREVERSIBLE★" in line)):
  4385	                    continue
  4386	                errs.append(f"{mark} 必須是 KEY 行前綴(寫成 KEY:{mark} ...),放別處工具掃合約會直接漏看:{line[:48]}")
  4387	
  4388	    invs, _ = extract_contracts(n)
  4389	    for inv in invs:
  4390	        clean, refs = strip_test_refs(inv)
  4391	        if not refs:
  4392	            errs.append(f"裸 ★INVARIANT★:標成不能破壞的合約卻沒綁測試,沒人能機械驗證它——行尾加 [test:測試名](健檢會擋):{first_line(clean, 48)}")
  4393	        elif not invariant_audit_refs(inv):
  4394	            errs.append(f"★INVARIANT★ 綁了測試但未獨立審計:還沒有不知道脈絡的人確認這條是真合約、測試夠不夠格——審過後用 lumos guard audit 補 [audit:](推送會擋):{first_line(clean, 48)}")
  4395	
  4396	    # Check J 單檔版(regen 重生來源守衛):共用 check_regen_provenance,映射表——
  4397	    # errs→errs(rc1)/warns→warns(顯示不計 rc)/gov_events→lint 一律不落帳(高頻)。
  4398	    if _lint_is_regen:
  4399	        j_errs, j_warns, _j_gov = check_regen_provenance(n, _repo_root_from_env(env))
  4400	        errs.extend(j_errs)
  4401	        warns.extend(j_warns)
  4402	
  4403	    # Check R 單檔版:可逆性回退綁定 + 標錯型別
  4404	    for marker, rclean, ref, guard_ref in extract_reversibility(n):
  4405	        if t != "system":
  4406	            errs.append(f"{marker} 只能標在功能筆記(Systems)上,這篇是 {t!r},標了也不會被當合約檢查:{first_line(rclean, 40)}")
  4407	        elif marker == "★IRREVERSIBLE★":
  4408	            if not (_rollback_resolved(n, ref) or _guard_resolved(n, guard_ref)):
  4409	                errs.append(f"{marker} 缺實質回退:標成做了回不去,卻沒寫出事怎麼退——行尾加 [rollback:decisions] 或 [guard:decisions],並在 decisions 寫上回退/防護內容:{first_line(rclean, 40)}")
  4410	        elif not _rollback_resolved(n, ref):  # ★CHECKPOINT★;guard_ref 不讀
     1	{
     2	 "snapshot_commit": "7fd214f",
     3	 "split_salt": "lumos-retr-v1",
     4	 "search": [
     5	  {
     6	   "id": "S01",
     7	   "query": "殺傷力",
     8	   "cat": "zh_short",

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "rg -n \"推播漏網|漏網量測|週清單|關於欄|miss.*push|push.*miss\" . --glob '"'!governance/review-reports/推筆記認家/r1-snapshot.md'"' --glob '"'!governance/review-reports/推筆記認家/r1-intake.md'"' --glob '"'!governance/review-reports/推筆記認家/r1-lens.txt'"' || true && python3 scripts/lumos search \"推播 漏網 量測\" && python3 scripts/lumos search \"每週 清單 關於\""[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 1480ms:[0m
(多詞回退:你查的整串詞在未作廢的節點的可見文字裡找不到完全一致的,改成每個詞分開查、有出現就算;逐詞覆蓋 推播:13  漏網:22  量測:94)
(已隱藏 4 筆作廢結果;要看的話加 --include-superseded)
提醒:命中≠查完——搜尋只告訴你「哪裡可能有」,不是完整內容;光看摘要就判「圖譜沒記」以前真的出過錯。下結論前先讀全文:lumos show <節點>
 14.812  Verification/2026-09-11_推播漏網量測實作.md  [推播,漏網,量測]
    6 [fm:revalidate_when]: revalidate_when: impact-hook 推播格式或冷卻窗改、lumos search 輸出字樣改、逐字稿格式改版時;REVISIT 2026-09-15 見正文
    12 [fm]: - "[[Projects/推播miss量測_計劃]]"
    14 [body]: # 2026-09-11_推播漏網量測實作
    16 [body]: > 白話:推播漏網量測(沒推卻被 agent 自己讀了的筆記)照計劃做完:量測程式、每週留存、接進自主迴圈。測試先行,六支新測試各自先翻紅再轉綠,並把修法改回舊寫法確認會翻紅。拿本…
    22 [body]: - [S2] `t_lens_recount_miss_classify`:錨點是編輯本身、hook 不管的檔不建列、讀失敗不算、讀取歸屬、推播前讀過不算、事故節點算規則內、事後才…
    33 [body]: - 修完重跑 W36:掃 2521 份、45 秒;列數與漏網數跟修前一樣(100 列、漏網 2),新看得到壞行 2 行(修前整份丟)、Codex 版本不認得跳過 13 份(修前照讀…
    42 [body]: | 零推播 | 81 | 35 |
    43 [body]: | 冷卻窗內沿用前一次推播 | — | 46 |
    … 還有 4 處
 13.793  Projects/推播miss量測_計劃.md  [推播,漏網,量測]
    4 [KEY]: KEY:GraphRAG 調研建議一(Enzo 2026-09-11 採納,單源 [[Projects/GraphRAG對節點關聯_調研]] d1)的實作——擴充既有唯讀儀器 re…
    5 [KEY]: KEY:錨點是每一次編輯本身(零推播也有一列)、推播四段都認;miss 依序分規則內(問 impact 直連)/關於欄(about_code)/判不出,編輯後才新建的筆記另計;本案…
    6 [KEY]: KEY:同一支儀器數 lumos search 零命中(建議二的量測基礎,新寫輸出配對);每週由自主迴圈週期觀測段存上一個完整週的推導列(照 run_replay 週戳慣例),查詢…
    19 [body]: # 推播miss量測_計劃
    21 [body]: > 白話:agent 改一支檔之前,hook 會推幾篇筆記給它。我們想知道兩件事——推的東西它有沒有用上,以及更重要的:它自己跑去讀了、但我們沒推的那些筆記。後者就是推播漏掉的東西…
    26 [body]: - 既有儀器 [[Projects/主session鏡頭利用率_計劃]](`governance/eval/lens-utilization/recount.py`)已經從逐字稿對…
    34 [body]: - [S1] 推播清單解析四段都認;解析不到或行數對不上的那筆記 `pushed_complete=false`,不猜 [test:t_lens_recount_parses_al…
    42 [body]: - 某段實際解析到的行數少於標頭宣稱的 N,或遇到認不得的段標頭 → 那筆 `pushed_complete=false`,它的 miss 不進三類統計、另計「推播清單不完整」。整…
    … 還有 26 處
 11.726  Projects/推筆記認家_計劃.md  [推播,漏網,量測]
    72 [body]: - 不替 POS 專案另建標準答案題(成本高、樣本少);消費專案的效果改看推播漏網量測的週清單。
    85 [body]: - **評測尺量不到**:標準答案題出在本工具鏈圖譜上,最常改的主程式是大檔,認家對它沒有鑑別力——[S10] 只當「不退步」的尺;真正的效果看消費專案的推播漏網週清單(回頭條件)…
    99 [body]: - 消費專案的效果量不到上線當下。REVISIT:2026-10-12 看推播漏網量測的週清單裡「關於欄」那一類(沒推、agent 卻自己讀了、而那篇是那支檔的家),比較上線前後的…
  8.426  Projects/GraphRAG對節點關聯_調研.md  [推播,量測]
    5 [KEY]: KEY:外界評比(arXiv 2502.11371、GraphRAG-Bench ICLR'26):單跳題普通檢索贏、多跳題圖檢索小贏、兩者合併最好;編輯時推播本質是單跳查詢
    21 [fm]: - content: 採納建議一(記「推了什麼、agent 有沒有用上」,以 miss 長出非同源評測題)與建議二(搜尋零命中時用詞共現改寫,借 LazyGraphRAG 不用模型…
    23 [fm:context]: context: GraphRAG 調研結論:招牌手法對小圖、單跳的編輯時推播幫助有限(PPR 已消融殺除);真正卡住的是評測題少且同源自驗;外界訊號是 agentic searc…
    30 [body]: > 白話:Graph RAG 的招牌手法(沿著連結擴散算分數、用模型抽知識圖、社群摘要)對我們幫助有限——擴散我們 7 月試過、被消融實驗砍掉;抽知識圖會丟資訊,而我們的圖本來就是…
    39 [body]: - **編輯時推播**(impact hook 與派工鏡頭):agent 要改某支檔之前,把相關的合約、事故、筆記推給它。固定席(事故+合約)+自由席;保留題上前 8 名命中率約 …
    41 [body]: PRIOR-ART: ①最小解層級=先看圖譜既有檢索調研([[Projects/檢索優化_調研]]、[[Projects/檢索PPR邊權_計劃]])已經做過什麼,本篇只補 2026…
    49 [body]: - **「推了之後有沒有被用」已經有一支唯讀量測**([[Projects/主session鏡頭利用率_計劃]],儀器 `governance/eval/lens-utilizat…
    72 [body]: - 我們 7 月自己量過沒有用,原因是候選池比推薦位小。外界評比也說圖檢索只在多跳題小贏,而編輯時推播本質是「這支檔跟哪些筆記有關」的單跳查詢。
    … 還有 4 處
  6.668  Issues/流程自產工作量未量測.md  [漏網,量測]
    15 [KEY]: KEY:對「檢索排序有沒有變好」會跑對照實驗,對「這套流程的成本效益」從未量測——同一個人身上兩套標準
    25 [body]: # 流程自產工作量未量測
    43 [body]: 不是「規格沒用」。是**這個比例從未被量測**,而量測它並不困難(逐條標記 findings 屬於「產品缺陷」還是「文件自身缺陷」)。
    49 [body]: - 「文件缺陷也是真缺陷,照這份實作會做錯」——部分成立,但**若沒有這份文件,實作者會直接看 code 與測試**,那些缺陷不會以這種形態存在。要比的是兩條路的總成本與總漏網,不…
    56 [body]: - Enzo 當日反問「為什麼這麼久」→ 本單子的問題從「未量測」升級為「已被使用者感知」。
  6.124  Projects/loop數據收集_計劃.md  [漏網,量測]
    21 [KEY]: KEY:[2026-07-22 日報吸收]逃逸帳方向外部獨立背書——Meta-Engineering Harnesses(arXiv 2605.25665,小團隊獨立做出「合約+角…
    37 [fm]: - content: 飛輪量測雙帳落地(Enzo 2026-08-31 裁做):①攔截帳=★圖譜攔截★零工具記號慣例+種子三筆回填 ②逃逸帳=loop escape 原語(M1②,…
    90 [body]: 深鏡頭席三連漏 canary（席位×軸）/資源例外型 canary 天生 haiku 可見（型別難度）/fromscratch 9→6→3 遞減 vs M2 6→9→7 不遞減（s…
    92 [body]: ## 飛輪量測雙帳(2026-08-31 立,Enzo 裁「做」;回答「良性循環怎麼衡量」)
    105 [body]: **② 逃逸帳(漏網面,M1② 原語,✅ 2026-08-31 落地)**:迴圈收斂放行後、下游抓到可歸因缺陷→
    157 [body]: - **效能**:切片掃歷史報告檔(現存數百檔 read_text);gov --stats 非熱路徑、人工指令。單次量測門檻:>2s 再議快取。
  5.446  Projects/回訪掃描_計劃.md  [漏網,量測]
    40 [body]: **T3. 回填=證據分流,不製造假期限**(★外家 blocker 核心:52 個日期一次拍=假精確、偷換量測對象;★飽和席抓第十次數字病:原寫 3/約10,機械數=已觸發 4、…
    42 [body]: - ②**已觸發欠帳**(盤點 13-16 四件):落行標近日——**此日期=處置期限(排程決定)非量測結果**(r2 外家:免再偷換語意)。
    66 [body]: - 掃描器只解「時間到了沒人知道」;「條件到了」(N 次後/某事件後)無通用解——轉日期是**定期抽查**不是即時觸發,漏網窗=至多一個掃描週期。
  5.343  Projects/每日治理wrapper活著沒_計劃.md  [推播]
    13 [KEY]: KEY:★r1 打掉兩個前提★ ①「推播那條腿斷了」是錯的——它在暫停開關之前就跑而且真的會推,真正的問題是要連喊 14 天才通知、對「36 小時前死掉」來不及 ②把死人開關押在健…
    16 [KEY]: KEY:S2 ★主通道改成一支獨立的排程看門狗★(每小時讀健康檔;跟被監看的那支是兩個失敗域),健檢軟提醒只當第二通道且★必須接不會讓 issue 計數增加的那一支★(同程式裡已有…
    35 [body]: - **★「通知那條腿是斷的」是錯的★**:那支週報在暫停開關**之前**就執行,而且真的會推播。
    112 [body]: **推播那條**:既有的週報路徑可以用,但它要連喊 14 天才通知。
    170 [body]: - 不重新設計推播通道(它沒斷,只是慢;本案明文接受它當第三層)。
  4.884  Verification/2026-07-11_hook面v1.1轉正.md  [推播]
    24 [body]: 推播面（impact ranked）從 goldset FAIL（P@8=.509）修到 §6 七盞全綠 PASS 並接上 PreToolUse hook。
    38 [body]: - **應試 vs 誠實**：0.65 係數同樣 P@8≈.71 且 p95=9,但「必看(標2)在實際推播視野(固定席+前8)」19/30——砍到需要看的東西;0.55 為 24…
  4.692  Systems/design-loop.md  [漏網,量測]
    30 [fm]: - "[[Verification/2026-09-03_席間覆蓋率離線量測]]"
    49 [KEY]: KEY:★定位★[2026-07-18 使用者裁定,見 decisions d4]——design-loop=抬 spec 質量,非保 spec 正確:一輪 panel 抓便宜的(…
    91 [fm]: - content: design-loop 定位裁定=抬 spec 質量,非保 spec 正確——一輪 panel 抓便宜的(矛盾/未定義詞/缺失敗路徑)就放行;正確性歸下游 c…
    160 [body]: - **鏡頭措辭升級未量測**(2026-08-28,d6):正確性鏡頭改帶例子的問句+「挑具體輸入走一遍」後,實際有沒有讓審查挖得更深**沒做 A/B**——措辭改動天生難單元測…
  4.612  Projects/CI回流閉環_計劃.md  [推播]
    17 [KEY]: KEY:解法方向=**push 後同輪等待+修復重試(watch-fix-retry)**,非雲端自動修也非留到下次開場:`lumos ci-wait` 在 push 成功後阻塞等…
    115 [body]: - **生命週期對稱（impact hook 推播命中 [[Issues/hook卸載殘留註冊]]，其通則正中本案）**：該事故通則＝「凡 A 端刪除／B 端引用的成對資源，守衛要…
    178 [body]: - 分支切換頻繁時快取最後一筆可能屬別的分支 → 記錄帶 sha，推播前驗「是當前分支祖先」才提醒。
  4.604  Projects/Codex外審吸收_計劃.md  [漏網]
    17 [KEY]: KEY:★P0 已落地★——①GitHub Actions CI 信任根(.github/workflows/ci.yml:compileall+SyntaxWarning 閘+全…
    35 [body]: | 文件漂移（44 指令/兩步安裝/Obsidian 宣稱） | **採，已修＋機械守衛** | t_docs_command_count 首跑抓到 README.en 漏網＝守衛…
  4.480  Issues/風險掃描遇到非UTF-8內容整支中斷.md  [漏網]
    20 [KEY]: KEY:★代碼審第二輪兩席各自抓到同一個漏網:泛用包裝 _sp_run_text(cmd) 的 git 字樣只在呼叫端,守衛原本「所在函式裡有沒有 git」的判法看不到★;守衛改成…
  4.479  Projects/主動影響幅度偵測_計劃.md  [推播,量測]
    315 [body]: `PRIOR-ART:` ① 最小解=既有 impact 反查已足(供給不缺,見下量測)② 世界解過沒=有,`github.com/tirth8205/code-review-gr…
    330 [body]: ⚠ **裁定的性質(勿誤讀)**:上述數字**全部來自本工具鏈自己的 goldset 快照**,未對該工具做任何實測或對照。裁定邏輯=「我的瓶頸不在供給,故擴供給的工具對我無用」—…
    362 [body]: ⚠ **這個數字量的是「跳不跳得出東西」,不是品質**:方法上覆蓋率完全等同於「有沒有 code 路徑反查命中」(indirect 由 direct 展開,direct 空則整組空…
  4.182  Projects/跨session傳訊用途調研.md  [推播]
    96 [body]: - [ ] ②的觸達場景：傳訊 vs 既有推播通知，哪個才是最小解（PRIOR-ART 未做）
  3.846  Projects/圖譜進迴圈入口栓_計劃.md  [漏網,量測]
    34 [body]: 2. 濾純數字 token(「2026」實測命中 381/385=全庫召回)、**長度 ≤2 的 ASCII token、所有長度 1 的 token**(★code-r1 邊界席…
    72 [body]: - **重驗**:上線後下一次「重造輪子」事故若再發生,查當時 A/B 有沒有印、印了為何沒用——印了沒用=升級議題(546 計數器再議),沒印=切詞/召回 bug。B 的 0.6…
  3.845  Verification/2026-08-24_固定席降噪A層落地.md  [漏網]
    53 [body]: 六輪 21 席零放行;三個要害各輪打掉:about 豁免(翻已鎖決策)、降自由席(門檻砍出輸出)、安置模糊(diff 聚合漏網)。
  3.768  Verification/2026-07-04_lint-version-watch.md  [漏網]
    30 [body]: - **T1 設計 defect(6 輪 design-loop 漏網,誠實記錄完整性天花板)**:§測試1 自相矛盾跨段數見證(3.9/3.20.0 behind vs 等段數守…
  3.542  Projects/公開精簡版_計劃.md  [漏網,量測]
    24 [KEY]: KEY:★r2 blocker(已折入)★——**r1 的 blocker② 在「聲稱已修好它」的那一節原地復發**:上一版在 [S4-a] 列了一份精確到行號、看起來窮盡的懸空引…
    84 [body]: - ★`impact` `cochange` `self-audit` `signoff` `spec-trace`★（使用者裁定 2026-07-31，見〈已裁定〉②）：逐支查證…
    85 [body]: - 附帶：這次跑閉包同時證明了 [S2] 的「可達性閉包」正解**可執行**（本輪算出函式層 31 必留／37 可砍——**此數字刻意不寫進條款**，理由見下方量測段）。
    89 [body]: **量測（2026-07-31 機械重算，取代原稿的「39」）**：`--help` 共 **53 支頂層指令 = 24 保留 / 29 移除**，24+29=53 加總驗訖、零交…
    103 [body]: - **已量測的有利事實（r1 辯方實作原型驗證）**：`main()` 分派段（`scripts/lumos:11675-11995`）的每一條 dispatch 分支中，**沒…
    374 [body]: | major | 量測數字錯：非「砍 39 支」，實測 41 留／27 砍 | 3＋辯方實測 |
  3.379  Projects/對外說明親和化改寫.md  [推播,量測]
    26 [DECISION]: DECISION:[2026-09-07 ★同日翻案★]〈成本與界線〉先搬進 docs/心智模型.md 第 8 節保留,後由 Enzo 裁定★整節移除★——理由不是「不好看」而是「…
    109 [body]: 節點名全是治理機制的內部代號。**形狀對了、意義沒對上。** 所以另外造了一份虛構線上商店的示範圖譜(登入/購物車/結帳/付款/庫存/推播 + 驗證 + 事故 + 計劃,共 14 …
    273 [body]: Enzo:「這不用量測也能知道吧,如果工程師依然用手寫 code,就不可能同時進行多個專案,
    283 [body]: 真正需要量測的是「產出變幾倍」「決策時間佔比」那種話——兩邊都沒有要講。
    330 [body]: Enzo:「心智模型與機制 8 全部拿掉,很多機制只是因為本工具不是消費端所以量測不出來,
    335 [body]: 1. **量測環境不對等**:那些數字(附的節點審查員大多沒打開、testmap 落後 614 個 commit、
    343 [body]: **沒有弄丟任何東西**:原始量測仍在 `Verification/2026-09-05_README審視量測`、
    348 [body]: 「工具能證明什麼、不能證明什麼」,是設計事實不是量測數字,跟第 8 節是兩回事。
  3.331  Projects/審查有沒有用記帳_計劃.md  [漏網]
    23 [fm]: - "[[Issues/流程自產工作量未量測]]"
    65 [body]: - **兩個現成欄位一次都沒人填**:`--refute-verdict`(辯方表態)1216 筆裡 0 筆——今天查明原因是七個輪次一輪辯方都沒派(路由規則下多半不觸發),所以它…
    106 [body]: - ★不在 `ci-wait` 紅燈訊息加提醒★:簡化席數了 ci 帳 12 次紅燈 0 次是審查漏網,加了就是噪音。
  3.230  Systems/canary-audit.md  [推播]
    132 [body]: - **Anthropic〈Verbalizable representations and a global workspace in LLMs〉**(transformer-c…
  3.175  Projects/接手視圖_計劃.md  [推播]
    89 [body]: - **現況實話**:在此之前沒有任何東西會自動叫 `lumos handoff`,只有 `lumos --help` 列著它。三層接法:①規則表讓 agent「知道有這支」②開場…
  3.132  Projects/固定席降噪A層_計劃.md  [漏網]
    84 [body]: (★`cmd_impact_diff` 聚合(三席 r3 同抓的漏網消費點,code-loop 在用)、hook free 桶、`_bound_tests_for_diff`★)
    221 [body]: ★三輪走勢:r1 打掉 about 豁免(方向)、r2 打掉降自由席與口徑偷換(機制)、r3 打掉安置模糊與漏網消費點(接線)。
  2.979  Projects/design-loop輕量檔_計劃.md  [漏網]
    87 [body]: - **d4 定位**：design-loop 本就「抬品質非保正確、漏網進逃逸帳」；light 只誠實定價最便宜的 spec，正確性照歸下游。
  2.870  Projects/probe輪退場_計劃.md  [漏網]
    54 [body]: - **c4 防線不降級(v3,以 decisions d2 為地基)**:嚴重度門檻——處置閘原制允許 major 附理由放行(panel 要求存活 max≤minor),路由統…
  2.791  Projects/檢索多詞回退_計劃.md  [量測]
    14 [FLOW]: FLOW:`lumos search` 多詞查詢=整串子字串比對→0 命中不回退(retrieval-ranking 節點既有的已知技術債) → 修法=★fallback-only…
    15 [KEY]: KEY:★根因不是「沒人想到多詞」,是量測工具自己的盲區傳染進量測集★——`build_goldset.py` 的 `search_pool(q)` 用同一道子字串比對組池,多詞查…
    17 [KEY]: KEY:★順序修正★:原本想「先補評測集再動 code」——★做不到★,候選池撈不出東西就沒得標。正確序=實作(藏旗標後)→組池→標註→量測→才決定預設
    43 [body]: ## ★根因：量測工具的盲區傳染進了量測集★
    77 [body]: 1. **實作 `--any`，預設關**（不是行為變更，只是多一條可量測的路）
    80 [body]: 4. **量測**
    88 [body]: - [ ] M4：量測 → 裁定預設
    200 [body]: ## ★M3/M4：多詞題標註與量測（2026-08-03）★
    … 還有 2 處
  2.755  Issues/嚴謹度分配偏向機械層.md  [量測]
    26 [body]: > ★2026-09-02 試點跑完(併修法 A):第一條被前後量過的紀律誕生,見 [[Verification/2026-09-02_修法A_lumos先行ablation結果]…
    50 [body]: ★**造新機制的動作一直在發生,量測既有紀律的動作一次都沒有。**★ 這比較像偏好,不像排程。
    54 [body]: **紀律不一定要能量測才有價值。** 有些規矩的價值在於「讓人在動手前多想三秒」,那種東西天生沒有機械 oracle——本專案自己就實證過 design-loop 對純散文空轉(見…
    56 [body]: 所以本單**不主張「所有紀律都要綁測試」**,主張的是:★至少要能分辨哪些紀律屬於「可量測卻沒量」,哪些屬於「本質不可量」★。目前這兩類混在一起,而混在一起的效果是全部都不用被檢查…
    60 [body]: - [ ] 紀律分類:可量測 / 本質不可量 / 純考古(可刪)?
    61 [body]: - [ ] 「可量測卻沒量」那批,挑一條做前後對照當試點?
  2.752  Verification/2026-09-04_Codex完全支援S3量測驗收.md  [量測]
    16 [body]: # 2026-09-04_Codex完全支援S3量測驗收
    18 [body]: > 白話:第三階段要證明兩支量測工具讀得懂 Codex——利用率重算能從 Codex 逐字稿數出「hook 推了幾次、推完有沒有去讀」,情境探針能用 Codex 當被測者跑同一批題…
  2.729  Verification/2026-09-03_席間覆蓋率離線量測.md  [量測]
    15 [VERIFY]: VERIFY:席間覆蓋率離線量測(2026-09-03)——★一個審查席會漏掉同儕找到的 64.6% 真缺陷★(帳上 85 個確定多席輪、822 個相異缺陷;含可能單席輪的 67.…
    22 [KEY]: KEY:v2 量測效度席打死 v2 的同時給了本篇線索——兩席讀同一份材料重疊只有 36-44%,正落在 v2 自訂門檻上,故那把尺分不開「漏項盲區」與「兩個人本來就講不一樣」
    29 [body]: # 2026-09-03_席間覆蓋率離線量測
    96 [body]: ★而 v2 的量測效度席在打死它的同時,給出了本篇的線索★:兩席讀**同一份**材料,發現本來就只重疊三成六到四成四——正好落在 v2 自訂的判別門檻上,所以那把尺分不開「漏項盲區…
  2.714  Verification/2026-09-05_README審視量測.md  [量測]
    15 [body]: # 2026-09-05_README審視量測
  2.657  Projects/oracle品質包_計劃.md  [漏網]
    26 [body]: `PRIOR-ART:` ①寫後讀回自驗＝lumos T1 寫入既有家規（tmp→rename→自驗），S1 是把漏網的 append 路徑補進同一紀律，非新機制；②kill 歸因…
  2.656  Issues/散文紀律沒有退場機制.md  [量測]
    20 [KEY]: KEY:★別把「字數變少」當「規則被驗過」★—[[Projects/skill寫法學借鑒與design-loop剪枝]] 已跑完一輪 PASS,但那條軸是**表達效率**:desi…
    23 [KEY]: KEY:★誠實界線★—自家★沒有★任何一次量測顯示我們的散文紀律造成傷害,外部數字不等於自家數字。本 Issue 主張「補上量尺與出口」,★不是主張「散文紀律有害」★;優先級因此壓…
    87 [body]: - ★它自己記下的天花板★：**剪枝的收益（模型是否更可靠地走同一條路）本身沒有機械量測**，只證明了「規則沒少、字數變少」。而且拆檔有結構成本——兩檔合計字元數反而 **+11%…
    123 [body]: 1. **真造成過事故嗎**：★否——這是本 Issue 最弱的一環，要誠實記著★。自家沒有任何一次量測顯示某條散文紀律造成傷害。**有的是**：載體規模可數（15 萬字元）、量過…
    132 [body]: - [ ] **B · 剪枝加第四種合法操作，並順手解掉自相矛盾**：在既有硬不變量下開一道窄門——「**經前後量測顯示無改善或倒退**」的規則准予撤除，且**必須附上那次量測**…
    154 [body]: - **★涵蓋「圖譜先行」紀律本身★**（自足性審計追問後補明，2026-08-13）。審計員問了一個原稿避開的問題：這整套「動手前先查圖譜」的紀律，本身正是那兩篇論文量測的那一類…
  2.601  Projects/主session鏡頭利用率_計劃.md  [量測]
    13 [KEY]: KEY:r1(62 條/11 blocker,4 席 opus+Codex)拆掉第一版:時間窗與注入時機互斥、比率量到圖譜密度、跳過是合規、門檻無刻度、extract_bash_f…
    32 [fm]: - content: r1 後重寫量測核心:去比率去門檻(只出分佈+人工抽樣)、時間窗改「推送之後」、證據全從逐字稿、hook 經 lumos lens push/tally 寫獨…
    35 [fm:why_chosen]: why_chosen: 第一版把量測儀器的假設全寫成事實(同日第三次:肯定斷言沒開檔看);重寫後每個宣稱都對應一個開檔核過的現況;門檻砍掉是因為沒有刻度的尺不能切
    38 [fm]: - content: r2 儀器歸零:推送本來就在逐字稿裡(hook_additional_context 附件,帶 toolUseID 與全文,歷史 70 次)——不加帳、不加 …
    40 [fm:context]: context: r2 量測效度席拿歷史逐字稿乾跑 r1 版演算法,發現注入附件已含全部所需;r2 其他四席對新帳/hook/gov/timeout/命名的 20 餘條發現隨元件移…
    47 [body]: > 白話:主 session 動手改 code 前,hook 會把「這個檔牽連到哪些帶合約的筆記」推到眼前——推了之後有沒有被看、被用,今天沒有任何數字,只有反例(2026-09-…
    49 [body]: PRIOR-ART: ① 最小解層級——推送方 `impact-hook.py`(PreToolUse Edit|Write)、逐字稿(Claude Code 每行帶 UTC 時戳…
    78 [body]: r2 量測效度席把 r1 版的演算法拿歷史逐字稿乾跑,發現★推送本來就寫在逐字稿裡★:每次 impact-hook 注入,逐字稿多一行 `attachment.type == ho…
    … 還有 3 處
  2.572  Issues/合約測試閘只在高風險推送跑.md  [量測]
    23 [KEY]: KEY:順帶=上一份計劃寫「38 支 28.7 秒」、它自己的驗證紀錄寫「42 支 28.9 秒」,同一次量測兩份文件對不上;修的時候順手查清
    60 [body]: 同一次量測兩份文件對不上。修的時候順手查清哪個才對。
  2.484  Issues/推新分支時風險分級拿空樹當起點.md  [量測]
    21 [KEY]: KEY:同源問題——與 [[Verification/2026-09-03_席間覆蓋率離線量測]] 是同一類:守衛的「叫」與「不叫」一旦跟真實風險脫鉤,就從證據退化成儀式
    23 [fm]: - "[[Verification/2026-09-03_席間覆蓋率離線量測]]"
    53 [body]: 這與 [[Verification/2026-09-03_席間覆蓋率離線量測]] 量到的是同一類問題:**守衛的「叫」與「不叫」一旦跟真實風險脫鉤,它就從證據退化成儀式。**
  2.478  Issues/健檢技術棧那段撞到多平台設定就整支中斷.md  [漏網]
    86 [body]: 另外兩個漏網的地方一併補上：lint 那一層原本沒套跳過、刪除行那條路少傳了一個參數。
  2.454  Projects/skill寫法學借鑒與design-loop剪枝.md  [量測]
    115 [body]: ## 第三輪(2026-08-02):量測後裁定②④⑤不做
    117 [body]: 沿用第二輪學到的紀律——**先量測有沒有真的痛過，再決定要不要加規則**。三項逐一查證，結論是**都不做**，理由記在這裡，避免未來的人（或我）再提一次。
    149 [body]: ★方法論★：第二輪靠數帳本找出真問題（cluster 帳 316:1），第三輪靠量測擋掉三個假問題。**同一條紀律，一次用來動手、一次用來不動手。**
    153 [body]: **全部結案**：③ 已落地（見第二輪）；②④⑤ 量測後裁定不做（見第三輪，各附理由）。
    160 [body]: - 剪枝的收益（模型更可靠地走同一條路）**沒有機械量測**。本次不宣稱行為改善，只宣稱「規則沒少、字數變少、單行不再破千字」。真要驗，得拿 golden 語料做 replay 對…
  2.433  Projects/工具鏈全環節體檢_調研.md  [量測]
    14 [fm]: - "[[Issues/流程自產工作量未量測]]"
    29 [body]: | pre-push:anchor verify / 全量測試 / tier=high code-loop / doctor --ci | 今日擋 3 次;code-loop 帳 …
    66 [body]: - 審查 loop 的 `tokens`/`wallclock_min` 欄位 487 筆全空——★先把量測補上再談調參★:record 時強制帶(或由編排者從 agent 回報填…
    68 [body]: - 審查員內跑全量測試(60s+、輸出大):派工模板明禁,改 `-k` 定向。
  2.366  Projects/Spotify-shunt吸收_調研.md  [量測]
    12 [fm]: - "[[Issues/流程自產工作量未量測]]"
    31 [KEY]: KEY:誠實界線=只量本 repo(消費端零量測);駐留成本 chars/4 估、55% 的「其他」沒拆;Spotify benchmark 未重跑;shunt 舊 hook 格式…
    40 [fm]: - content: 儀器 scripts/usage_scan.py 留下但不升格:不接進 lumos 子指令、不進 doctor、不排程;作為流程自產工作量未量測與席位成本欄回…
    99 [body]: - **d2 儀器留下**:`scripts/usage_scan.py` 是 [[Issues/流程自產工作量未量測]] 與 [[Projects/世界repo掃描2026-09…
    119 [body]: - 只量了本 repo 21 個 session、14 天;消費端專案零量測。本 repo 的讀法(定點 sed)是這幾週紀律養出來的,別的專案未必。
  2.346  Projects/地基盤點2026-08-26_調研.md  [量測]
    6 [KEY]: KEY:重點缺口:①關係層只查斷鏈不查「還對不對」(自認頭號腐爛無常態守衛)②新收斂制無新舊對照回測(n=1~11,golden 未建 bundle)③自主迴圈 backlog 退…
    80 [body]: 1. **E3 自主迴圈修理**(在燒錢)+ **G3 修量測尺**(尺歪則一切檢索優化白做)——兩件都小而痛。
  2.314  Projects/執行DAG_調研.md  [量測]
    15 [KEY]: KEY:★腐化數字(★量測時點 2026-09-07,含活計數,引用必帶時點★)★:Projects 標 doing 43 篇(母體 155,含本篇自己)、其中 17 篇 >30 …
    77 [body]: ## 這個 repo 的實況(★量測時點 2026-09-07★,當場機械查的,不是憑印象)
    79 [body]: > ★活計數警告(外家 f6)★:下列數字有兩個會變——Projects 篇數與 `doing` 數把**本篇自己**也算了進去(本篇建立後 154→155、42→43),`gov…
    137 [body]: - **(c) 沒有跨 session 互斥**。[[Issues/同工作區多session並行改動]] 已立案:一天撞三次、兩次有實害,原話「四層閘沒有一層的輸入裡有 sessi…
  2.296  Projects/第二輪審視六修_計劃.md  [量測]
    21 [body]: KEY:★Enzo 2026-09-05 裁:這個「審視→修→再審視」的動作要 loop 到系統自洽為止,由 Claude 裁決、保留對系統好的設計★——自洽的判準(Claude …
    53 [body]: - **量測留痕**:26/39-21/209-14/17-11 這幾個數的重算指令另立 [[Verification/2026-09-05_README審視量測]],之後可重算。
  2.294  Verification/2026-08-22_檢索英文單複數消融.md  [量測]
    70 [body]: ★所以正確結論是「這次量測不可解讀」,不是「改動有害」。★
    104 [body]: ## 這次量測本身的一個坑
  2.287  Verification/2026-09-04_主session鏡頭利用率第一份報表.md  [量測]
    40 [body]: 第一版報表的 Bash 分類有兩個 bug(重導向寫回偵測是死碼、`write_text` 子字串比對把只讀路徑算成寫回、`sed -i` 當讀),正確性/邊界兩席各自抓到並附翻紅…
    61 [body]: - 重算腳本的 Bash 分類器原本只認裸的 `lumos <子指令>`,不認 `python3 scripts/lumos <子指令>`、也不認帶路徑的節點名。補上後同一份資料重…
  2.277  Projects/Codex完全支援_計劃.md  [量測]
    23 [KEY]: KEY:目標=在 Codex CLI 下開一個 lumos 專案,得到跟 Claude Code 下★同一套★六層防護:指示(AGENTS.md)/skills/hooks(進場、…
    29 [KEY]: KEY:分四階段,每階段各自驗收:S0 安裝層(skills symlink→~/.agents/skills、hooks.json 合併器、AGENTS.md 區塊、enforc…
    78 [body]: lumos 的六層防護(指示 / skills / hooks / 迴圈編排 / 量測 / 安裝拆機)在 Codex CLI 下逐層接上,驗收標準是「乾淨機器、隔離 HOME 與 …
    88 [body]: | 5 量測 | `governance/eval/lens-utilization/recount.py` 讀 `~/.claude/projects/**.jsonl`;`sc…
    134 [body]: ### S3 量測(進場條件:S0 進場 4 答「明文」且 additionalContext 有落逐字稿;否則本階段只做 probe runner,recount 不做並在誠實界…
    230 [body]: - **驗收**:[[Verification/2026-09-04_Codex完全支援S3量測驗收]]。
  2.268  Projects/指令索引與情境測試_計劃.md  [量測]
    29 [body]: ## 現況量測(2026-08-22)
    49 [body]: 量測:常駐的 CLAUDE.md 區塊 6.1k bytes;真正壓注意力的是三份主 skill 正文(project-notes 20k / design-loop 30k / …
  2.265  Projects/code階段強化_計劃.md  [漏網]
    97 [body]: - S1 觸碰判定依賴 impact --diff 的 min_score 門檻——門檻漏判=該跑沒跑,屬已知漏網面(逃逸帳接)。
  2.232  Projects/世界repo掃描2026-09-02_調研.md  [量測]
    15 [fm]: - "[[Issues/流程自產工作量未量測]]"
    46 [body]: | C 流程可觀測性與成本帳 | [[Issues/流程自產工作量未量測]]、memory 06-18「委派落差代理指標」 |
    74 [body]: ### C 組:量測
    81 [body]: - **D1 並行改動**。Enzo 09-01 已裁「誤報量測不辦,三型再犯時回看」——本條只留世界座標:MCP Agent Mail(2.1k★)glob 路徑 advisor…
    89 [body]: - **規則同步器** rulesync(1.4k★)/ruler(2.9k★):純分發,無 lint 無量測。
  2.179  Systems/效能檢核目錄.md  [量測]
    76 [body]: | 熱路徑短命大物件/該用 Span/ValueTask | 人判提問 | GC 壓力;dotnet-counters 量測佐證 |
    87 [body]: | INP ≤200ms:互動會不會卡主線程 | 人判提問+lab 量測 | 2026 最常掛的 vital(43% 不及格);長任務拆分/防抖 |
    113 [body]: | 主執行緒卡住(hang):同步 IO/圖片解碼/大 JSON/Core Data fetch 在 @MainActor 或 UI 回呼裡 | **機械可查**(Instrume…
    122 [body]: | 基線裝置 | 量測紀律 | 在還支援的最舊機型量,不在旗艦機量 |
    139 [body]: **實證錨**:Vercel 量測——靠模型自己「想起要查規範」,**56% 情況會跳過**;hook 保證注入與模型意願無關。同 lumos「機械把關>靠自覺」與 impact …
  2.177  Systems/hook逾時預算.md  [量測]
    60 [body]: 超時說明**刻意不寫「下一席大概率就有」**——那是機率宣稱,而這裡的規矩是機率宣稱要附回頭條件、要有量測。目前沒量過「超時之後同範圍下一席的快取命中率」,所以只講機制事實(那支還…
    86 [body]: ★測的過程我連續四次沒測到,原因每次不同★:背景那支比 deadline 還快、鎖檔名算錯、算完沒清鎖、我自己前面的量測把快取寫進去了。**四次都是「現場沒成立」不是機制壞掉。**…
  2.171  Issues/同工作區多session並行改動.md  [量測]
    20 [DECISION]: DECISION:2026-09-01 Enzo 委任裁:誤報量測不辦(無自然數據源,硬量=再造假指標);維持「三型再犯時回看」的事件入口。2026-09-07 第四型觸發回看,結…
    24 [body]: > ★2026-09-01 Enzo 委任裁:誤報量測不辦——無自然數據源,硬量=再造假指標(引圖譜率案同週教訓);維持「三型再犯時回看」的事件入口★
  2.149  Projects/中文無空白查詢回退_計劃.md  [量測]
    15 [KEY]: KEY:S1 順序改成 實作(藏旗標後)→組池→標註→量測→才裁預設;S2 ★評測另開一套不進既有題庫★(既有兩臂都固定關回退,塞進去兩臂都 0 候選、量不到改善還讓分母失義);S…
    52 [body]: ### [S1] 順序:先實作(藏在旗標後)→ 組池 → 標註 → 量測 → 才決定要不要變預設
    119 [body]: 保留多詞回退」。**新開一支獨立旗標**,預設**關**(照 [S1] 的順序,量測完才裁預設)。
  2.126  Verification/2026-08-20_gov-stats落地.md  [量測]
    21 [body]: - **全量測試 2885 passed / 0 failed**(較實作前 2858 增加 27)。
  2.070  Verification/2026-09-05_skill-doctor成本基線.md  [量測]
    20 [body]: KEY:★真正的成本在迴圈★——7 天:lumos-code-loop 930 萬 token / 49 次(平均約 19 萬一次)、lumos-design-loop 300 萬…
  2.070  Projects/驗形式與驗內容_調研.md  [量測]
    25 [KEY]: KEY:★本 repo 沒有的量測維度:治理品質要獨立於任務品質量★——現有逃逸帳量的是任務側(缺陷漏到下游),沒有任何獨立於任務結果的治理品質指標;論文證明用任務成功率當治理代理…
    48 [fm:why_chosen]: why_chosen: n=0 時任何比率都沒有意義;把「測不成」寫成「測過沒問題」是本 repo 反覆抓到的假綠形態。誠實記成未驗證,並把量測改成往前看(先產生資料再量)。代價:…
    136 [body]: 4. **★一個本 repo 沒有的量測維度★**:治理品質與任務品質要**分開量**。現有的逃逸帳量的是任務側(缺陷漏到下游);**沒有一個獨立於任務結果的治理品質指標**。
  2.061  Verification/2026-08-12_CheckY_符號存在性.md  [量測]
    39 [body]: ## 噪音收斂過程（三次量測）
  2.058  Projects/條款綁測試算進度_計劃.md  [量測]
    14 [KEY]: KEY:[S1] 認領=條款同一行綁 [test:] 或 [manual:];存在性走既有 _classify_one 不開第二套;狀態四種,懸空★但要再分兩種★(寫錯 / 設定認…
    101 [body]: `test_` 前綴與 class 內的 144 支全在這一類)。「設定認不到」不能算成寫錯,也**不進 REVISIT 那個比例的分母**(通才席 F2:否則盲區會污染量測)。
  2.029  Verification/2026-07-17_test-layers軟提醒.md  [量測]
    32 [body]: 驗證 [[test-layers軟提醒_計劃]] 落地——`lumos test-layers` 子命令(vault-free,恆 rc0)+ pre-push advisory …
  2.021  Projects/宣稱級時間戳_計劃.md  [量測]
    20 [body]: 3. **既有機制蓋得住嗎?** 目前面上的洞由五個既有件分攤:①DECISION 行帶 `[日期]`+翻案 `valid:false`+`ended`(決策層=完整的 Graph…
  2.018  Projects/code側刪除傳播守衛_計劃.md  [推播]
    43 [fm]: 軟提醒可以被無視，本次失守正是「被推播了仍只掛連結」。故 advisory 版必須配 S3 的問句紀律
    55 [fm]: impact hook 在編輯當下的即時推播不帶本守衛訊號;接受——刪除在編輯當下未必成形,commit 時點才是刪除的定案點。
    149 [body]: 但泛問會失效——本次那六個節點大概率都被 `impact` hook 推播過，結果仍是掛連結了事。**問題不在有沒有問，在問得夠不夠具體**：泛問可以在腦內三秒答完，指著某一行問「…
  2.013  Issues/只退場不痛的機制.md  [量測]
    56 [body]: - [[Issues/散文紀律沒有退場機制]] — 本單的最大宗未退場資產,那張單子已有完整量測。
  2.010  Issues/自主loop加法偏食.md  [量測]
    32 [body]: - 成比例的解:pre-push 補跑全量測試(~32s,一段 shell)——**事件點閘**。
  2.002  Projects/收斂閘漏項敏感度v2_計劃.md  [量測]
    95 [body]: ★自我檢驗條款★:**本案任何一步若要求「派工前多跑一道指令」,就是踩回同一顆地雷,當場退掉**。本案只做唯讀重跑與量測,不新增任何人要記得跑的東西。
    111 [body]: 3. ★不是常設協議★。canary 死於「每輪都要做、卻沒人用結果」;本案是一次性量測,跑完歸檔,不進任何輪的例行流程。
    186 [body]: - **不做的事**:不建常設閘、不接自動消費者、不進任何輪的例行流程。這是**一次性量測**,跑完就歸檔——`lumos mutate` 正是死在「建了沒有乾淨的家」。
    196 [body]: - `Systems/loop-convergence-recording` — 三個集合的原始定義節點,本案是它的第一份覆蓋率量測。
  1.963  Projects/impact-diff橋接_計劃.md  [量測]
    17 [body]: 檢索排序轉正後的第一個消費場景橋接（使用者提案）：code-loop 終審時，用已量測過的 ranked impact 給審計員一顆「**受影響功能面**」鏡頭——更精確評估相關功…
  1.866  Issues/寫下風險當成處理風險.md  [量測]
    18 [fm]: - content: 判準立成鐵則(CLAUDE.md 區塊第 4 條+project-notes 頭版):承認句旁必須有「什麼時候回頭看」(週報/重驗條件/到期日),寫不出來就是…
    27 [body]: > 立成 CLAUDE.md 第 4 條鐵則:寫「沒守衛/只提醒/單次量測」旁邊要有什麼時候回頭看。**實證**:本輪三處承認句都對到了週抽/空轉週報/留痕。
  1.863  Projects/README審視五修_計劃.md  [量測]
    13 [body]: > 白話:2026-09-05 拿 README 逐條對回程式碼、帳本、量測(我+一位乾淨稽核員各做一份,兩份結論一致),抓到五處「寫的比做到的多」。Enzo 裁「依序優化」。這篇…
  1.833  Projects/loop三輪壓縮_實作計畫.md  [量測]
    107 [body]: - [x] 全量測試 0 failed;`lumos doctor` 0 issues。
  1.787  Verification/2026-08-22_指令索引與情境探針.md  [量測]
    35 [body]: - 一次跑的結果有隨機性,19/20 是單次量測,不是保證。
  1.785  Projects/檢核收緊五件_計劃.md  [量測]
    15 [fm]: - "[[Issues/流程自產工作量未量測]]"
    36 [body]: **砍掉的 S4(findings-doc 欄)/S5(stale-gates)**:無獨立事故、且「不擋」——退回 [[Issues/流程自產工作量未量測]]/[[Issues/…
    90 [body]: | 件 | 量測(指令) | 條件 |
  1.781  Projects/code席爆炸半徑供糧_計劃.md  [量測]
    33 [body]: **C 廢**(P-4):與剛判死的常設指標同構念同母體同方法,卻繞過母案([[Projects/loop數據收集_計劃]] d2)當天寫下的三個重開條件。成效量測**改掛既有條款…
  1.746  Verification/2026-08-24_about_code讀側四項落地.md  [量測]
    58 [body]: - 新指標只有一次量測,「一個月觀測再決定要不要閘」的觀測才剛開始。
  1.730  Issues/連鎖佇列開了沒人跟完.md  [量測]
    78 [body]: - **② 世界解過沒（真搜）**：學術界的撤稿傳播是同一題且量測充分——撤稿後仍被引用是常態，**撤稿後的引用只有 5.4% 承認撤稿**；且傳播**主要靠直接引用**而非間接（…
  1.721  Systems/codex-harness.md  [量測]
    60 [body]: - 落地四階段 S0–S3 與裁定 d1–d6:[[Projects/Codex完全支援_計劃]];驗證 [[Verification/2026-09-04_Codex完全支援S0…
  1.718  Projects/Android側UI測試綁圖譜工作流_實作計畫.md  [量測]
    135 [body]: - [x] **Step 3：全量測試**（skill 散文無專屬測試，跑全量確認沒撞到既有 skill 相關斷言）
    194 [body]: - [x] **Step 3：全量測試** → `0 failed`
  1.658  Projects/Codex工作流整合_調研.md  [量測]
    53 [body]: 4. **利用率量測跨家**:Codex 的 transcript_path/agent_transcript_path 都有,recount 那支腳本理論上可以多讀一個來源——但…
  1.626  Projects/design-loop提效_計劃.md  [量測]
    69 [body]: ## ★M2 落地後量測:機制存在但沒在用(2026-08-02)★
    94 [body]: - skill `reference.md` 新增 **§D0「先決定用哪一種帳」**，含選擇表與「為什麼性質不同就別壓成一個數」（單一 max 會讓一軸遮蔽另一軸），並把這份量測…
  1.605  Verification/2026-08-21_工具鏈體檢修復批.md  [量測]
    55 [body]: - 全量測試見下。
  1.589  Projects/intake守衛_計劃.md  [量測]
    23 [body]: ★引用訂正(r2 正確性 F1)★:v2 曾引嚴重度綁定案當「先 advisory 後硬擋」前例——**引反了**,該案實為外家否決 advisory 優先、反轉首日硬擋。v3 誠…
  1.588  Systems/convergence-evidence-gate.md  [量測]
    21 [fm]: - "[[Verification/2026-09-03_席間覆蓋率離線量測]]"
    78 [body]: [[Verification/2026-09-03_席間覆蓋率離線量測]] 用帳上既有的 `capture_counts` 離線算出來了:
  1.571  Systems/外部對照-code衍生wiki.md  [量測]
    99 [body]: - 未親跑 openwiki 生成一份 wiki 實測其誤差率（結論建立在讀 prompt.ts + test/ 結構 + README 機制）；「無輸出 oracle」是**機制…
  1.570  Projects/skills提示工程優化_調研.md  [量測]
    39 [body]: ## 現況量測(2026-09-11)
  1.563  Systems/測試假綠形態.md  [漏網]
    259 [body]: - **★不得把「對照過清單」當成「測試夠格」的證明★。** 清單是提示器不是偵測器；漏網靠 canary、對抗審、與對交付產物的端到端真跑兜。
  1.562  Projects/一句話層供糧_計劃.md  [量測]
    54 [body]: - 省 token 的宣稱不搬:OpenViking 的 34-91% 是它的 benchmark,本案不量 token(量測要有自然數據源,本週血訓)。
  1.498  Projects/迴圈摩擦三修_計劃.md  [量測]
    21 [body]: PRIOR-ART:世界調研歸檔 `governance/review-reports/loop-friction/web-research.md`;v2 實際引用=法庭卷證規則(…
  1.493  Projects/規模影響判斷力假說.md  [量測]
    184 [body]: ★③ 與「每項的話多話少」糾纏在一起,不是乾淨的量測★。
  1.472  Projects/graph-engineering掃描2026-08-19_調研.md  [量測]
    103 [body]: 帶 `related` 欄位的節點數 <!--lumos:count=214 re=(?m)^related:$ in=docs/lumos-toolchain-knowledge…
  1.470  Projects/連結缺失補全_計劃.md  [量測]
    58 [body]: - **考卷誠實界線**:候選由通用規則對全庫生成、逐筆按實質關係人裁——非為過卷定向補;goldset labels 不動;補完重跑考卷的數字變動=真實改善的量測,如實記(含「此…
  1.464  Projects/test-layers軟提醒_實作計畫.md  [量測]
    354 [body]: 內文必填:`plan_refs` 指 `[[test-layers軟提醒_計劃]]` 與本實作計畫、`valid_under`(如「cmd_test_layers 簽名/宣告檔 s…
  1.455  Projects/修法A_lumos先行ablation_計劃.md  [量測]
    69 [body]: 1. **差 ≤ 5pp**(≤4 場):那段散文在 skill+hook 之上**無可量貢獻**→ 成為 [[Issues/散文紀律沒有退場機制]] 修法 B 窄門的**第一個候…
  1.388  Projects/驗證層去模型化_計劃.md  [量測]
    24 [body]: PRIOR-ART: ① 最小解層級——處置閘(design-loop 已驗證,本週三個 loop 實戰含 rc0 收斂)移植 code-loop;變異測試=既有 `guard k…
  1.382  Projects/改制回測_計劃.md  [量測]
    33 [body]: - **[S4] 週期接線**:autonomous-loop 週跑,範圍=**新凍結(從未回放過的)必跑+存量輪替抽樣每週 5 包**(輪完一圈重來)——不是全量:golden …
  1.262  Projects/canary注意力檢查失效.md  [量測]
    143 [body]: - 優點：抑噪紀律照舊管 findings，不影響注意力量測。
  1.103  Projects/標註刷新_計劃.md  [量測]
    146 [body]: 解法是 delta 補標把未標消滅、不動尺。★這條 2026-08-22 複查後維持;★2026-08-26 被翻,見上方被翻註記——新理由=補標治池不完整但治不了懲罰結構,量測回…
  1.058  Projects/進度從提交推導_計劃.md  [量測]
    135 [body]: | Projects 標「進行中」 vs 超過 30 天沒動 | **46 篇 / 其中 17 篇**(★快照 2026-09-07 傍晚;原稿寫 43 是當天稍早的量測,差的 3…
  1.007  Projects/檔案測試依賴地圖_計劃.md  [量測]
    158 [body]: - 情境命名整合測試（`RedeemIdempotencyTests` 類）naming/內容雙源都可能落空 → cochange 是唯一兜底，[S4] 分層抽樣如實量測。
  0.955  Projects/閘觸發帳統計_計劃.md  [量測]
    49 [body]: 1. **真事故?** ★半過,弱點明講★。可數事實有(上表);但**查無一筆「因為警告淹沒而漏掉某事」的已記錄事故**。★**r2 後此理由已被打薄,如實記錄**★:s2 席指出…
  0.589  Projects/全repo審視_計劃.md  [量測]
    109 [body]: | F30 | ai-hooks | hook 執行沒有任何落盤帳:成功/超時/rc≠0 只有 LUMOS_HOOK_DEBUG 才看得到,量測靠 grep 逐字稿 | M/low…
    882 [body]: - **注入到每個消費端的紀律範本**寫著某客戶專案名當量測出處,還指向「文末〈架構參考 Skills〉」——本 repo 沒有那一節。
  0.000  Projects/Agentflow吸收_調研.md  []
    57 [fm:why_chosen]: why_chosen: 先射箭再畫靶是本 repo 反覆量到的失效型(見 positive-assertions 類教訓);而第0步成本極低(27 條合約行,一次抽驗)。★唯一例外…
  0.000  Projects/design-loop重設計.md  []
    45 [fm:why_chosen]: why_chosen: 品管三件套文獻中 gold/互評/冗餘並列且 gold 有應試缺陷、實務全是累積統計判定,單題一票否決無人採用;citation grounding 實證機…
  0.000  Projects/席位人格化_計劃.md  []
    14 [fm:why_chosen]: why_chosen: A/C 零額外 token、與禁互辯/抑噪/前置加重一律拒三條既有教義全相容,git revert 即回;B 要先量成本與模型可用性且回滾要動席位分派表兩處…
  0.000  Projects/派工鏡頭注入_計劃.md  []
    37 [fm:why_chosen]: why_chosen: 存活事實三件(攔得到/清單算得出/沒人貼)剛好拼成鏡頭版;砍掉量測支線後,五份計劃二十幾條 blocker 只剩三條仍適用(措辭中性/用既有合併器/誠實揭露…
  0.000  Projects/設計審收斂重定義_計劃.md  []
    36 [fm]: - content: 重寫訊號雙訊號嘗試(折入波及幅度+核心裁定命中)已試並撤回——loop-friction r1 五席證死:回代不成立(同案兩算法 27%/32% 跨線;pc-…
  0.000  Projects/評測尺翻案_計劃.md  []
    19 [fm:why_chosen]: why_chosen: 補標管線治池不完整但治不了懲罰結構:每個提升召回的改動都先被未標=0 扣分,要等人補標才平反——尺本身歪,量測回饋慢一拍;IR 界對不完整判定有成熟指標解,…
  0.000  Systems/graph-sync-coverage.md  []
    24 [fm]: - "[[Verification/2026-09-05_README審視量測]]"
  0.000  Systems/lumos-cli-lifecycle.md  []
    89 [fm]: - "[[Verification/2026-09-04_Codex完全支援S3量測驗收]]"
  0.000  Systems/lumos-cli-read.md  []
    74 [fm:why_chosen]: why_chosen: 先實作(藏旗標後)→組池→標註→量測→才裁預設:評測的組池工具靠現有搜尋撈候選給人標註,而這些查詢現在回 0 候選、沒東西可標,所以量測不可能排在實作前面(…
  0.000  Verification/2026-07-31_slim-gen生成器落地.md  []
    14 [fm]: - "scripts/lumos 註解密度大幅變動(新增/刪除大量註解區塊)→ 重新量測 t_slim_gen_keeps_comments 的 90% 密度門檻是否仍合理"
  0.000  Verification/2026-07-31_公開精簡版終審修復.md  []
    9 [fm]: - "C1 的 --python 掃描候選數(21 條)是本次修復當下 scripts/lumos 原始碼的量測值,原始碼字串常數增減會改變這個數字,不影響 --python 模式…
  0.000  Verification/2026-07-31_接手者演練複審修復.md  []
    8 [fm]: - "Landmark 演練的『vendored 完整版 50 支』是 /Users/enzo/backend/LandmarkMember 當下 vendored 的 scrip…
  0.000  Verification/2026-08-12_CheckU_過度概化守衛.md  []
    7 [fm]: - "噪音率量測基準＝LandmarkMember 30 篇 Systems / 261 條 KEY 行 @ 2026-08-12"
  0.000  Verification/2026-08-25_probe輪退場與多席路由統一落地.md  []
    6 [fm:revalidate_when]: revalidate_when: "下次改動 panel 抽查印行時,t_panel_probe_retired 的舊義務句斷言改為正向鎖新句字面(sha 硬幣紅證限制的回頭條件,…
  0.000  Verification/2026-08-30_圖譜入口栓落地.md  []
    6 [fm:revalidate_when]: revalidate_when: "①cmd_search 候選收集/剝碼層改動時(advisory 的 OR 掃描要人工同步——spec 要抽共用 helper、實作偏離,這是代…

(共 113 篇候選,照相關性排序;想照檔名排加 --legacy)
(多詞回退:你查的整串詞在未作廢的節點的可見文字裡找不到完全一致的,改成每個詞分開查、有出現就算;逐詞覆蓋 每週:22  清單:220  關於:15)
(已隱藏 8 筆作廢結果;要看的話加 --include-superseded)
提醒:命中≠查完——搜尋只告訴你「哪裡可能有」,不是完整內容;光看摘要就判「圖譜沒記」以前真的出過錯。下結論前先讀全文:lumos show <節點>
 13.759  Projects/推播miss量測_計劃.md  [每週,清單,關於]
    5 [KEY]: KEY:錨點是每一次編輯本身(零推播也有一列)、推播四段都認;miss 依序分規則內(問 impact 直連)/關於欄(about_code)/判不出,編輯後才新建的筆記另計;本案…
    6 [KEY]: KEY:同一支儀器數 lumos search 零命中(建議二的量測基礎,新寫輸出配對);每週由自主迴圈週期觀測段存上一個完整週的推導列(照 run_replay 週戳慣例),查詢…
    21 [body]: > 白話:agent 改一支檔之前,hook 會推幾篇筆記給它。我們想知道兩件事——推的東西它有沒有用上,以及更重要的:它自己跑去讀了、但我們沒推的那些筆記。後者就是推播漏掉的東西…
    26 [body]: - 既有儀器 [[Projects/主session鏡頭利用率_計劃]](`governance/eval/lens-utilization/recount.py`)已經從逐字稿對…
    34 [body]: - [S1] 推播清單解析四段都認;解析不到或行數對不上的那筆記 `pushed_complete=false`,不猜 [test:t_lens_recount_parses_al…
    42 [body]: - 某段實際解析到的行數少於標頭宣稱的 N,或遇到認不得的段標頭 → 那筆 `pushed_complete=false`,它的 miss 不進三類統計、另計「推播清單不完整」。整…
    47 [body]: - **錨點是那次編輯本身**:逐字稿裡每一次 Edit/Write/MultiEdit(Codex 是 apply_patch)呼叫都是一列,推播清單用呼叫編號去配 hook 附…
    52 [body]: - **讀取歸給哪一次編輯**:事件先後看(行序, 同一則訊息裡第幾個工具呼叫)——同一則訊息裡先改檔再讀筆記,讀取排在那次編輯之後(代碼審 r1 單reviewer A1)。同一…
    … 還有 18 處
  9.312  Verification/2026-08-23_關於欄位離線預標驗證.md  [清單,關於]
    14 [body]: # 2026-08-23_關於欄位離線預標驗證
    16 [body]: > 白話:在動任何程式碼之前,先驗「讓模型標『這篇關於哪幾支檔』」這個主意到底分不分得開雜訊。
    24 [body]: 並明寫「空清單是正常答案,不要硬湊」(昨日外家全給 1 的教訓)。
    41 [body]: | 標註 | 模型說「關於」 | 模型說「不關於」 |
    47 [body]: **18 條噪音模型一條都沒判成「關於」。** 對比扇出(昨日):那個只砍一半噪音、還砍到必看。
    49 [body]: 那 2 個「必看但不關於」看過:①`code-loop守衛main-direct盲區` 對 CI 設定——
    50 [body]: 模型標它關於 pre-push/lumos,**內容確實在講 pre-push 盲區,CI 只是後盾;是考卷那筆標寬了**
    51 [body]: (昨日我裁的,當時理由「CI 那道閘存在的理由就是這個盲區」——那是「相關」不是「關於」)。
    … 還有 10 處
  8.798  Verification/2026-08-23_影響欄位離線驗證.md  [清單,關於]
    16 [body]: > 白話:「關於」欄位驗過了,但它接不住「不是在講你、你改了卻會出事」那類筆記。
    17 [body]: > Enzo 問能不能用標籤分「提到」和「關於」——答案是關係不只兩種,至少四種,
    20 [body]: ## 為什麼「關於」不夠:四種關係
    25 [body]: | 關於 | 這篇在講這支的行為(實作在哪) | about_code,已驗(2026-08-23) |
    29 [body]: r1 那個案例把「關於」與「影響」的差別講透:`anchor-integrity`(守衛檔要簽名)——
    30 [body]: 模型標它**關於** pre-push(實作在那);考卷說改 pre-commit、impact-hook 也**必看**(它守所有 hook)。
    34 [body]: 模型回答時偏向「關於」是因為那比較好判。★拆開問,兩欄各自會乾淨。★
    43 [body]: | 每篇「影響」比「關於」多 | 1~8 支,最多 `autonomous-iteration-loop`(3→11) |
    … 還有 2 處
  8.777  Projects/固定席扇出降權_計劃.md  [清單,關於]
    15 [fm]: - content: 方向改裁:主案=語意『關於』欄位(模型離線預標、讀側查欄位);扇出降權/提到的位置降為過渡方案
    42 [KEY]: KEY:主案=語意「關於」欄位 about_code(模型離線預標、雙評審寫入、讀側查欄位可重算);扇出降權/提到的位置降為★過渡方案★。Enzo 裁:字串比對有結構性天花板,要質…
    44 [KEY]: KEY:★r1 六洞全折★——「與考卷必看同一把尺」宣稱作廢(「關於」比「必看」嚴,是精確度子集非等價物);讀側打錯靶(固定席三軸:direct/indirect/incident…
    47 [DEP]: DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
    56 [body]: > 正文有沒有提到那支檔的路徑——**而「提到」不等於「關於」**。
    59 [body]: > 但模型不能進計分(可重算性),所以放在**寫入側**:讓模型預先標「這篇關於哪幾支檔」存成欄位,
    163 [body]: | ① | **提到 ≠ 關於** | 一視同仁 | 正文提到 20 支檔的筆記,對每一支都是 direct——這正是扇出訊號在量的東西 |
    192 [body]: | **B 讀側・提到的位置** | KEY 行/標題提到 > 正文提到;只在正文順帶提到且扇出高 → 降 | 同上 + 抽取時記位置 | 區分「關於」與「提到」的第一步 |
    … 還有 27 處
  8.328  Projects/推筆記認家_計劃.md  [清單,關於]
    52 [body]: - [S3] 必推名單的順序:事故最前,其次家,其餘照原本;家之間照分數。取代原本要預標指紋沒過期的「關於命中」排序。 [test:t_impact_pins_order_inci…
    57 [body]: - [S8] 顯示:Edit 前推筆記的清單上,家標「★家★」;原本的「★關於★」標示拿掉(它依賴的預標指紋不再影響排序)。 [test:t_impact_hook_shows_h…
    71 [body]: - 不重開「關於欄位」的模型預標——那是舊案的主案方向;本案用的是每支檔有家驗過的家。
    72 [body]: - 不替 POS 專案另建標準答案題(成本高、樣本少);消費專案的效果改看推播漏網量測的週清單。
    85 [body]: - **評測尺量不到**:標準答案題出在本工具鏈圖譜上,最常改的主程式是大檔,認家對它沒有鑑別力——[S10] 只當「不退步」的尺;真正的效果看消費專案的推播漏網週清單(回頭條件)…
    99 [body]: - 消費專案的效果量不到上線當下。REVISIT:2026-10-12 看推播漏網量測的週清單裡「關於欄」那一類(沒推、agent 卻自己讀了、而那篇是那支檔的家),比較上線前後的…
  7.956  Verification/2026-08-24_about_code讀側四項落地.md  [清單,關於]
    9 [KEY]: KEY:about-code-impl-std 三輪達上限後人裁乙直接實作——#4 impact 讀 about_code(about_hit 只加分、事故優先、過期雜湊、總開關、…
    29 [body]: ## 做了什麼(對應計劃工具清單)
  7.356  Projects/驗證層自證三件_計劃.md  [每週,清單]
    41 [body]: - **前瞻層(真 SNR,接對資料結構)**:資料源=governance/eval/canary_calibration.py(已退場) 的固定題×多席判定矩陣(plants …
    44 [body]: - **範圍收斂(r1)**:v1 只做 canary 題庫;每週檢索考卷已有 goldset+held-split 重跑結構、更適合變異分解,列未來方向不進本計劃驗收。
    60 [body]: - **併發**:S1/S2 皆為離線批次讀取(收貨時/每週 runner 單進程),不進熱路徑、無共享資源競爭;review-reports 為 write-once 多檔目錄(…
    64 [body]: - **[prod-irreversible]**:三件皆無不可逆動作——S1 rc0 觀測不擋、S2 產清單人裁換題、S3 純文本;回滾=刪腳本/revert 文本,無資料遷移。
    68 [body]: - **pre-flight(2026-08-06,機械排乾,不算 loop findings)**:①S2 資料源 governance/canary-samples/(已退場)…
    76 [body]: - [major] 驗收「清單非空」把預期結論寫成通過條件(Codex)→ 改合成樣本單元測試,真實資料清單可空;同型鬆綁同步套用 S1(「至少找到一筆」刪除,零命中不算失敗)。
    78 [body]: - [major] S2「+每週檢索考卷」未落地(Codex)→ v1 範圍收斂為 canary,考卷列未來方向。
    89 [body]: ## 合約候選清單(收斂時提名,候選≠已標——蓋章仍走 guard 流程與「不確定不標」鐵則)
    … 還有 1 處
  7.288  Projects/自足性審計閉環_計劃.md  [每週,清單]
    9 [KEY]: KEY:方案(★d1 裁定版:全自動閉環★)=每週派乾淨 agent 審「從未確認+過期」功能筆記(N=2/週,PR 高者先)——PASS→自動戳(auto- 前綴留痕);FAIL…
    49 [body]: > 兩篇全是爛的。所以把「派沒背景的 agent 去看」變成每週自動的事:站得住自動蓋章,站不住把
    72 [body]: ②與守衛判準的既有五旗標(--tag/--no-tag/--active/--contract/--linked——照 cmd_query 現行 guard 逐字;v5-r2 s1…
    78 [body]: make_sandbox 加排除清單參數★(預設空=舊行為一字不變;附「舊呼叫不變」回歸斷言——照 repo 相容鐵則,Projects/design-loop重設計_實作計畫:3…
    83 [body]: ★清單維護註記(v5-r2 arch#2):repo 已有兩份簿記清單(scripts/lumos 的 _BOOKKEEPING_FILES 與 _COCHANGE_DEFAULT…
    84 [body]: 本清單用途不同(脈絡隔離非掃描豁免)、成員不同,不硬併;selfaudit.py 內單一定義+註解互指,防第四份漂移★;
    129 [body]: nag 不佔額;喊人每檔每週一次;
    146 [body]: 6. **執行模式白名單(d1)**:寫入清單加「回寫柵欄通過的那一篇」;例外註解帶重驗條件(同 v4)。
    … 還有 7 處
  6.950  Projects/idioms自維護迴路_計劃.md  [每週,清單]
    66 [body]: - **缺漏（gap）**：該有的最佳實踐從沒進 R 清單。
    95 [body]: | C3 旁註 / C2 網搜 | A | code-loop 附出 / 每週網搜 → pending | ⭕ Claude 編排 |
    108 [body]: - `[S4]` **消費 lint-upgrades 穩定事件**：**不掃每日覆寫的 `pending-YYYY-MM-DD.json`**（round-2：`"w"` 覆寫漏…
    115 [body]: - `[S7]` A 層每週一次 WebSearch 找「某棧新最佳實踐、linter 沒收**且不在 R1-Rn**」→ pending `kind=gap`。**不復用 gap…
  6.924  Systems/loop-convergence-recording.md  [每週,清單]
    32 [KEY]: KEY:[2026-07-28]第四模式 settle(opt-in,`--settle 清單檔`)落地——收斂=清單全結清∧G1∧G3(末筆 result=現檔;K-streak…
    41 [KEY]: KEY:★判定回放(2026-08-26 改制回測案)★:`loop replay --freeze/--golden`——收斂即凍完整輸入閉包(全列帳原文+逐行 sha 集+sp…
    124 [body]: **背景**:多席同一輪時,只有一席帶處置清單,它等於宣告自己是全輪的帳本載體。規矩一直寫著「記帳前先跑引句檢查,挑每句都對得回審材的那席當載體」。
    130 [body]: **現在的做法**:把讀側那道檢查往前挪到寫帳之前。帶處置清單的那一筆如果有引句對不回快照,記帳當場擋下並指路。**代價從「整輪重記」降成「換一席再敲一次」。**
  6.723  Systems/開發工作流總覽.md  [每週]
    17 [FLOW]: FLOW:①寫計劃(先查圖譜三步;開審第一輪先列出主題已有的節點,避免重複開案)→②設計送審(design-loop:派工時自動把相關節點附給每個審查員[2026-09-05 起 …
    21 [KEY]: KEY:★2026-09-05 良性循環怎麼轉★(把 08-25「節點是下一輪的輸入」變成真的在跑的路):節點→派工時自動附相關節點給每個審查員(機制名 dispatch-lens…
  6.665  Issues/自足性審計提醒空轉四十六天.md  [每週,清單]
    18 [fm]: - content: 出口落地:lumos gov --nags <天> 列「同一軟閘對同一篇連喊 ≥N 天、最近一次體檢還在喊」的清單(rc1);自主迴圈每週跑一次、有就 LIN…
    27 [body]: > `lumos gov --nags <天>` 列出「同一道軟閘對同一篇連喊 ≥N 天、最近一次體檢還在喊」的清單;自主迴圈每週跑一次,有就 LINE。**實證**:首跑抓到 5…
  6.582  Projects/README審視五修_計劃.md  [每週,清單]
    16 [body]: KEY:d1 pre-commit/post-commit 補 shebang 判定——沒副檔名但首行是 `#!` 的 staged 檔算程式碼(讀 staged blob 不讀工…
    18 [body]: KEY:d3 自主迴圈暫停派工——daily-governance 不再每天派 orchestrator(帳上近兩週(8/23–9/5)滾動週報收斂 0/待放行 0、每週 210–…
    25 [body]: - **三席同題的 major**:「什麼算程式碼」的 shebang 判定寫成直譯器清單,而且 bash 兩支、check-graph-sync、impact-hook 三份清單…
    32 [body]: - **minor**:`..foo` 只剝一個點 → 剝掉所有開頭的點;impact-hook 刪清單後多出的空行收掉。
  6.232  Systems/lumos-cli-read.md  [每週,清單]
    18 [KEY]: KEY:[2026-08-05]檢索考卷加 synonym 類(toolchain 4 題/landmark 3 題,查詢用別名期望命中帶 aliases 節點;檢索實跑 grou…
    122 [body]: - `stale [--match <字串>] [--candidate]`(`cmd_stale`):`status:stale` 清單;`--match` 掃 valid_un…
    131 [body]: - 認得哪些鍵**是問工具、不是問這個圖譜**:除了一份固定清單,執行期還會併入工具自己的欄位常數(清單欄位與純連結欄位那兩份),所以那兩份之後再加欄位,這裡不必跟著改。★代碼審 …
    173 [body]: 打錯一個字母原本會印三份同樣的指令清單(usage 一串、英文提示、再逐個列一遍),而使用者要的只是「你是不是想打 doctor」。裸打時吐的是英文的「缺少必填參數」。
    181 [body]: ### 說明段:不再手抄清單
    183 [body]: 手抄那份停在 10 個、實際 66 個,而且 argparse 會再印一遍(畫面上兩份)。**改法不是把清單補齊**——補齊的隔天又會過期。清單的單一來源交給 argparse 自…
  6.023  Verification/2026-09-11_推播漏網量測實作.md  [每週,清單]
    16 [body]: > 白話:推播漏網量測(沒推卻被 agent 自己讀了的筆記)照計劃做完:量測程式、每週留存、接進自主迴圈。測試先行,六支新測試各自先翻紅再轉綠,並把修法改回舊寫法確認會翻紅。拿本…
    31 [body]: - 三席審(單reviewer、架構對齊、外家否決 Codex)報 16 條、編排者自找 1 條,17 條全折;每條先寫翻紅測試:`t_lens_recount_code_revi…
  5.865  Projects/skill寫法學借鑒與design-loop剪枝.md  [清單,關於]
    14 [KEY]: KEY:★動刀的硬不變量★:剪枝★不得遺失任何規則★——只准壓縮措辭、搬家(SKILL.md→reference.md)、刪除純考古(日期出處/工作包編號/論文引用)。驗證=機械清…
    68 [body]: > 另請注意本節的**效力範圍**：這條不變量寫在「本次動刀範圍」底下，是為那一次剪枝作業（只動 `lumos-design-loop`）定的，**不是全 repo 常設規定**；…
    72 [body]: - **機械清單 diff**：抽出改動前後的指令名、旗標、wikilink、★標記行、步驟編號，逐項比對。消失的每一項都要能指出「搬到 reference.md 哪裡」或「是考古…
    88 [body]: **① 機械清單 diff**：指令名 9→9、旗標 25→25、wikilink 10→10，**零消失**。
    109 [body]: ★而我 2026-08-01 剛違反過它★：pre-push 假紅，我沒先拿失敗清單就跳去押 `GIT_DIR` 假說，而那份清單從第一分鐘就在 `/tmp/lumos-prepu…
    147 [body]: **不是三條新規則，是三個「查過、有證據、決定不做」的結案**——連同理由，讓這份清單不會變成永久掛著的未完成事項（那本身就是另一種沉積）。
    161 [body]: - 「沒遺失規則」靠清單 diff + 一個乾淨 agent，**不是證明**。清單抽取本身是「我枚舉了 N 種形態」——本專案已被這個坑咬過多次，故驗證推到覆核 agent 的語…
  5.862  Systems/autonomous-iteration-loop.md  [每週,清單]
    31 [KEY]: KEY:週期任務第四支 run_replay(2026-08-26 改制回測 S4):每週補漏凍結+新凍必跑+存量輪替抽 5(游標檔)+預算 300s+便宜(單包×存量≤60s,首…
    32 [KEY]: KEY:★抽掉人之前必辦清單(觸發條件=迴圈能不經人放行寫圖譜/開 PR 那天,今天人在放行點故全部不建)★——①提案者≠寫入者結構分離(Mnemosyne arXiv 2607.…
    79 [fm]: - content: 自主 loop 記帳+收斂閘遷處置閘、對齊手動 loop(Enzo 2026-08-27 裁):step-6 canary caught/missed → r…
    91 [fm]: - content: 暫停每日派 orchestrator(daily-governance 以 LUMOS_AUTOLOOP_OFF=0 才跑):帳上近兩週滾動週報收斂 0、待放…
    134 [body]: - **CONVERGED**(★2026-08-27 遷處置閘,見 d7★)= `lumos loop status <topic> --disposal --spec <spe…
    142 [body]: - **強制地面事實查證**:auditor 對 spec 每個現況假設(欄位 / 簽名 / 檔案 / 常數)必須實際 grep/Read 驗過、列查證清單。
    164 [body]: - 2026-08-27 **記帳+收斂閘遷處置閘(d7,對齊手動 loop)**:loop 自報三卡點——step-6 記帳指令照字面跑不動([S1] 起審查席帳列必附 --re…
  5.515  Verification/2026-09-09_接入靜默失效七項落地.md  [清單,關於]
    26 [VERIFY]: VERIFY:r2 抓到反查表的隱蔽復發——`.vue`/`.sql`/`.ps1` 只是碰巧被 C# 的副檔名清單收了,所以純 Vue 專案反查出 symbol_profile=…
    91 [body]: 關於「這支測試證不出跑過」**一個字都沒有**；高風險擋下時，也看不到逃生指令。
    104 [body]: r2 指出反查出來的答案在 `.vue`／`.sql`／`.ps1` 上其實是錯的——它們只是碰巧被 C# 那份副檔名清單收了
    105 [body]: （那清單的意思是「C# 店裡也會有的檔」）。所以一個純 Vue 專案會拿到 `symbol_profile: csharp`，
  5.477  Issues/把自己的推論寫成repo明文寫過.md  [清單,關於]
    25 [KEY]: KEY:★第六次:借來的權威★——第一輪某席在報告最後附帶提「那把鎖的鎖目錄沒被忽略清單涵蓋」,我沒查證就抄進計劃還加了教訓評語;第二輪另一席查證那是錯的(實測命中規則,而且規則跟…
    132 [body]: ### 還有一層,關於這個病的性質
    143 [body]: 第一輪某一席在報告最後附帶提了一句「被抄的那把鎖的鎖目錄其實沒有被忽略清單涵蓋,
    147 [body]: 第二輪另一席去查了:**那是錯的**。實際建立那個目錄再查,它命中忽略清單的規則;
  5.160  Projects/改制回測_計劃.md  [每週]
    18 [body]: > 白話:昨天把收斂判準整組換掉(處置閘),證據只有「上線當天十個迴圈跑得過」。這案把「重算一遍還是同樣判定嗎」變成可以每週自動問的問題:帳、報告、spec 的雜湊全部凍進判定檔(…
    33 [body]: - **[S4] 週期接線**:autonomous-loop 週跑,範圍=**新凍結(從未回放過的)必跑+存量輪替抽樣每週 5 包**(輪完一圈重來)——不是全量:golden …
  4.997  Issues/散文紀律沒有退場機制.md  [清單,關於]
    22 [KEY]: KEY:★外部把「無效」升級成「有害」★—①TDAD(arXiv 2603.17973):AI 改壞既有測試的比率,什麼都不加 6.08%、★只加一段「請照測試先行做」的程序散文惡…
    65 [body]: 所以更精確的處境是：**全 repo 根本沒有任何一條關於「散文紀律怎麼退場」的常設規定**，一條都沒有；我們唯一有過的一次前例，明令禁止刪。
    86 [body]: - 它量到的：design-loop 的 SKILL.md 從 15,462 降到 11,053 字元（−28.5%）、最長單行 1,361 → 455；驗收走機械清單 diff（…
    105 [body]: | 給機械算出的「這次該跑哪些測試」清單 | 1.82% |
    134 [body]: - [ ] **D（另議）· 往機械化搬**：TDAD 的 1.82% 來自機械算好的清單，不是散文。凡是能算出來塞到眼前的（既有的動手前影響提示、共改守衛、測試對照表都屬此類），…
  4.797  Verification/2026-08-22_缺席推論探針題組.md  [每週,清單]
    17 [body]: > **節點內容一多就快速下結論**——這組題把它變成每週會被抓到的東西,不是靠口頭保證。
    77 [body]: `governance/autonomous-loop.sh` 的 `run_probe`:題庫清單加 `absence.jsonl`,
  4.707  Verification/2026-08-26_評測尺翻案落地.md  [每週]
    33 [body]: 主審 3 條(1 blocker)+架構席 1 條全折:①beats() 原巢狀在 report_goldset 內、main() 的切換覆寫塊呼叫=NameError——切換後每…
  4.666  Projects/修法A_lumos先行ablation_計劃.md  [每週]
    95 [body]: - 每週抽查歷史不能當抖動基線(每週不同題),抖動只能從本次 with 組同題三次估。
  4.532  Projects/工具鏈補強十件_計劃.md  [每週]
    32 [body]: | 1 | 情境探針進自主迴圈 | ✅ `autonomous-loop.sh` 加 `run_probe`:每週(ISO 週數當種子)抽 8 題決定性輪轉,結果 append `…
  4.519  Projects/hook必看召回修復_計劃.md  [每週,清單]
    20 [body]: > 緣起:2026-08-07 全系統掃描——每週考卷唯一連續紅燈=hook P@8 0.639(閘 0.70)、must_in_out_recall 0.6。對 goldset …
    48 [body]: - **provenance 穿透**(r1 折入,Codex):`_impact_reverse_lookup` 回傳型別由節點清單改為 `(node, hit)` 對,`cmd…
    87 [body]: ## 合約候選清單(收斂時提名,候選≠已標——蓋章走 guard 流程與「不確定不標」鐵則)
  4.488  Projects/全repo審視_計劃.md  [每週,清單,關於]
    13 [body]: > 白話:2026-09-05 夜到 09-06,派 16 個不同鏡頭的乾淨 agent 把整個 repo 掃一遍找可優化處,每條再派兩個反方(一個查事實、一個查圖譜先例與家規)去…
    34 [body]: ## 分群清單(依 價值→工量→風險 排,還沒裁要不要做)
    69 [body]: | 32 | hooksPath 指向樹內、錨點只錨清單內三支 | F24 | med | S/low |
    197 [body]: - 刪 lumos --help 開頭 docstring 那份重複的 10 支子命令清單——argparse 下面已經全列一次,而且那份較舊、還夾內部代號(F01/F108)
    219 [body]: - 不要給自主迴圈加單輪或每週成本上限(F92)——自主迴圈修理計劃〈不做(邊界)〉明寫「不給 orchestrator 加 turn/成本上限」,那輪 $78 是正常跑滿六輪(6…
    225 [body]: - 不要把治理帳改成只寫狀態轉換、不重寫同一批 warned(F117)——那些重複行正是 gov --nags 判「還在喊」的燃料(它比對 last_warned_ts 與 la…
    243 [body]: - fail-open 沒有總量清單:scripts/lumos 有 104 處 except Exception,其中 59 處是裸 except Exception:。各鏡頭只…
    258 [body]: - **PRIOR-ART**:最小解在 repo 根目錄一個檔;世界解=choosealicense.com + SPDX identifier + GitHub communi…
    … 還有 33 處
  4.242  Projects/Agentflow吸收_調研.md  [關於]
    51 [fm:why_chosen]: why_chosen: 按場景分流會把第一手執行紀錄也課上重建成本,不成立;按主張來源分流才對症。★而且修正後建議反而更利★:合約行幾乎全是「關於意圖與歷史」的第二類主張,所以只對…
    113 [★INVARIANT★]: ★但這個修正反而讓建議更利★:合約行(★INVARIANT★ 那類)幾乎全是第二類主張——「這條規則不能改」本來就是關於意圖與歷史的斷言,不是關於「我剛剛跑了什麼」。**所以只對合…
  4.096  Projects/對外說明親和化改寫.md  [每週,清單,關於]
    162 [body]: - 明確不動:〈這是什麼〉的五個 bullet(清單本來就好讀)、〈裝起來〉(指令為主)、
    272 [body]: 我說「解放多工」「人專注決策」是關於結果的宣稱、沒量過,建議寫成「這是我們賭的」。
    310 [body]: 寫成一條、擺在該清單第一位——因為它正好是上一節〈為什麼是自然語言開發〉的反面推論,
    397 [body]: - 全景圖:「每週燒 210 到 330 美元」
    784 [body]: 代碼審三層各一句(只有圖沒有字,看不出「各抓不到什麼」)、五件事清單。
    868 [body]: (每輪留帳、判定凍結每週回放、查詢有人工考卷),★不列缺口★。缺口留在圖譜(Issues/評測那幾篇)。
  3.864  Projects/每支檔有家_計劃.md  [清單,關於]
    80 [body]: 2. 是程式檔：副檔名在「改程式要動圖譜」那道閘的清單裡，或沒有副檔名而首行是 `#!`。那份清單現在是四份副本（提交前、提交後兩支掛鉤，Claude 端兩支掛鉤）由一支一致性測試…
    81 [body]: 3. 不在排除清單：docs/ 與建置輸出夾（跟提交前那道閘的排除表同一份）、測試檔（見下）、lumos 自己裝進去而且內容沒改過的檔（內容指紋判定；在 lumos 來源 repo…
    83 [body]: - **測試檔**：用測試地圖那一支判定；副檔名不在它清單裡的程式檔（例如 shell、Go、Rust、C/C++），套它同一組目錄與檔名規則——路徑裡有 tests／test／_…
    84 [body]: - **`node_home.ignore`**：字串清單；每一項是比對 repo 相對路徑的 glob，語法跟既有共改排除樣式那一支相同（`fnmatch`，`**/` 開頭的另…
    100 [body]: - [S1] 「需要家的檔」照上面的定義；程式檔判定用主程式新增的第五份清單，並接進既有的一致性測試（五份一致）。 [test:t_nodehome_required_files_…
    122 [body]: - [S15] 提交前與推送前「該動哪篇」的點名改成照家算，取代原本以反引號為種子的那一套（兩支掛鉤都不再呼叫它；推送前那份波及計算只留給合約測試閘用）：每支改動檔的家、這次沒被動…
    135 [body]: - [S20] 計劃筆記多一個清單欄位 `lands_in`（收進清單欄位白名單，用 `lumos append` 寫），每項寫 `Systems/<名>`；那篇還不存在＝要新開。…
    203 [body]: - 子集：`python3 scripts/test_lumos.py -k nodehome`、`-k lands_in`、`-k disposal_gate_requires_…
    … 還有 1 處
  3.847  Projects/規模影響判斷力假說.md  [關於]
    120 [body]: ③**刻意排除同功能的設計討論 commit**（`b370d175` 與 r1/r2/r3）——那會讓 L 拿到比 S 更多關於排程決策的資訊，是反向汙染
  3.647  Projects/地基盤點2026-08-26_調研.md  [每週]
    54 [body]: 現況:真正常態運作的只有兩支——檢索考卷(每 7 天,8 gate)與情境探針(每週 8 題);gov 日報 gaps 餵自主迴圈;G3 雜湊鏈保收斂窗內部一致。
  3.456  Projects/自主迴圈修理_計劃.md  [每週]
    21 [body]: PRIOR-ART: 全部借用,零依賴自寫幾行——「失敗的件不丟、進死信重排」是訊息佇列教科書做法(SQS/RabbitMQ 的 DLQ);「排隊太久的題目分數要動」是 OS 排程…
  2.291  Issues/健檢技術棧那段撞到多平台設定就整支中斷.md  [清單]
    19 [KEY]: KEY:★跳過只認精確檔名,不認目錄前綴★(2026-09-10 代碼審 r1 四席獨立抓到的 blocker):第一版照 scripts/hooks、scripts/templa…
    20 [KEY]: KEY:④(同一天順手)about_code ★是清單★(0〜3 支程式檔)卻有一種寫法沒有指令改得動:讀的一側把單一值寫法當一項的清單,寫的一側 append 卻說它不是清單、s…
    22 [KEY]: KEY:②③共用同一個判斷(工具確實安裝的精確檔名清單+安裝時記下的內容指紋);安裝與拆除用的目錄也改成同一個常數,不再各記一份
    84 [body]: 「帶後門的 hook 推得上去」的重現。改成只跳過一張「工具確實安裝的檔」精確清單：同名同路徑才算，
    85 [body]: 同目錄的其他檔照樣掃。清單要跟工具鏈 repo 裡那兩個目錄的受版控檔一模一樣，有測試逐檔比對。
    91 [body]: - 風險掃描看「改動範圍終點」那個版本的內容、健檢看工作目錄的內容：**檔名在清單上、而且內容跟指紋一模一樣**才跳過；
    92 [body]: - 終點上整支刪掉、但起點時原封不動的工具檔（拆除工具鏈）也跳過，拆除時指紋清單一起拿掉；
    93 [body]: - 沒有指紋清單（舊版安裝）→ 一支都不跳，寧可多掃；那些專案跑一次 `lumos update` 就會有清單；
    … 還有 25 處
  2.283  Systems/slim-gen-生成器.md  [清單]
    12 [FLOW]: FLOW:讀 `scripts/lumos` 原始碼 → AST parse → 算 root 集合(保留指令 dispatch 分支呼叫的函式 + module-level 語句…
    15 [KEY]: KEY:removed_cmds 真值來源=掃全部 subparser 註冊(Assign/Expr/迴圈三種形態)得到的指令全集減 DEFAULT_KEEP(26 支 <!--l…
    17 [KEY]: KEY:★迴圈註冊刪除須 top_var receiver 限定★(2026-07-31 審查揪出、已修復,不是「超出範圍」)——`_is_registration_loop` 原…
    18 [KEY]: KEY:★交付包組包清單漏了 get.sh/uninstall.sh★(2026-07-31 修復,離職交接演練中發現)——`main()` 尾段「組交付包」只複製 `instal…
    19 [KEY]: KEY:★2026-07-31 Task 9 同型缺口預防性修復★——Task 9 把 CLAUDE.md 注入內容從腳本內嵌 heredoc 改成外部靜態範本 `slim/cla…
    22 [KEY]: KEY:★2026-08-01 補追加 Task 13——組包清單再擴充,與 [[Systems/slim-install-安裝器]]/[[Systems/slim-uninsta…
    30 [fm]: - content: t_slim_gen_keeps_comments 的斷言二次修正:原哨兵 W4 位於 _link_or_copy(scripts/lumos:7238),只…
    38 [fm:context]: context: 審查用合成fixture(otherkeep巢狀註冊removeme/x2)demonstrate:一個被保留的指令若用迴圈註冊自己的巢狀子指令,那段迴圈會被整個…
  2.276  Projects/結清式收斂_計劃.md  [清單]
    16 [KEY]: KEY:把 loop 收斂判準從「連 K 輪沒挑到問題」(缺席證明)升級為可選的「逐條約束結清」(存在證明)——spec 的每條硬合約(INVARIANT 級)/載重宣稱拆成清單,…
    17 [KEY]: KEY:v1 範圍刀——`--settle`(新增旗標)只接 legacy 單席路徑(與 --panel/--light 互斥 rc2);不帶 --settle 行為 bit 不變…
    18 [KEY]: KEY:design-loop r1-r5 已跑(五輪 3 席 panel、15/15 canary 全 caught;r1 blocker1+major3+minor10/r2 …
    19 [KEY]: KEY:★首個真實 loop dogfood(2026-07-31,對象=[[Projects/公開精簡版_計劃]];該 spec 兩輪 panel 未收斂、capture-rec…
    34 [body]: - **模式邊界（r1 折入）**：現行三種收斂判準並存（legacy K-streak／`--panel` 結構信號／`--light` 單席謂詞，互斥）。v1 的 `--set…
    35 [body]: - **約束清單**：spec 的硬合約／載重宣稱逐條列成機械格式，一條一狀態：`unverified`（未查）／`mech-ok`（機械查訖：refcheck 通道，僅買「引用存…
    37 [body]: - **canary 醒著條件保留（r1 折入，r2 補記帳鏈）**：settle 輪照 skill 紀律植 canary；條目欄位含 `verified_in_round`（哪一…
    38 [body]: - **清單↔spec 版本綁定（r1 折入，r2 粒度歸一）**：**條目級** `spec_sha`——每條記拆分當下的 spec sha；gate 時任一條目 sha ≠ 現…
    … 還有 25 處
  2.255  Issues/deinit整夾刪使用者檔.md  [清單]
    20 [KEY]: KEY:★已修(2026-07-24)★=_deinit_remove_vendored 改成★對稱安裝端逐檔刪★——安裝端 _vendor_toolchain 對兩夾走 src.…
    21 [KEY]: KEY:★2026-08-02 同一支函式的後續補強(code-teardown-windows loop)★——頂層白名單迴圈的裸 `p.unlink()` 包成 `try/ex…
    22 [KEY]: KEY:★2026-09-10 安裝端改了,兩邊不再完全對稱★:_vendor_toolchain 改成只複製精確清單(_VENDORED_TOOLKIT+_VENDORED_TR…
    37 [body]: 安裝端 `_vendor_toolchain` 沒有留下「vendor 進這兩夾了哪些檔」的 manifest，所以移除端拿不到精準清單，只能整夾刪。
    45 [body]: 1. **逐檔白名單化（正解）**：安裝時記錄 vendor 進這兩夾的檔清單（manifest），移除只刪 manifest 內檔＋夾空了才刪夾；夾非空（有外來檔）→ 刪 lum…
    55 [body]: REVISIT:2026-12-10 把拆除端改成照 .lumos/vendored.json 或精確清單刪,讓安裝與拆除再次對稱(現在拆除仍從來源列舉)
  2.229  Verification/2026-09-03_派工攔截點實測.md  [清單]
    16 [KEY]: KEY:★追測(同日):hook 不只能擋,還能改寫派工詞★——hookSpecificOutput.updatedInput 對派子代理有效,實測子代理原封不動列出只存在於注入文…
    17 [KEY]: KEY:★注入的兩條硬約束(第一次測失敗換來的)★——①內容寫成「暗號是 XXXX」時子代理拒答並指認為提示注入,換成長得像真實清單才成功:注入內容必須看起來是正當系統附加 ②此機…
    60 [body]: **做法**:hook 攔到帶哨兵的派工時,把一份「必查清單」(三個節點名)接在原派工詞後面回傳;
    61 [body]: 派出去的子代理被問「你收到的必查清單有哪幾項」。★派工詞本身一個節點名都沒提★,
    71 [body]: 換成長得像真實必查清單的內容才成功。兩條約束由此而來:
    75 [body]: 任何子代理的派工詞。要落地的話,**該 hook 本身必須進錨點保護清單**(本 repo 已有該機制:
    80 [body]: 原停案的設計是「派工詞沒附清單就擋下」。`updatedInput` 讓設計可以改成「沒附就直接塞進去」,
    87 [body]: hook 回 `additionalContext`(內容為一份「固定席節點」清單),派工詞本身不含任何節點名;
    … 還有 2 處
  2.222  Verification/2026-09-08_Codex席位可指定模型_兩席分流.md  [清單]
    15 [TEST]: TEST:t_codex_d6_agent_toml 加 5 條守衛(兩份 TOML、兩席模型與強度精確、名字不同指示相同、teardown 兩席都收且清單照實列);★餵壞值驗過會…
    16 [KEY]: KEY:★改到一條既有測試的斷言,理由要留★ — 原本驗「teardown 對外方檔回 False」;兩席之後那個 False 不成立(自家的第二席照刪=回 True),但守衛的本…
    17 [KEY]: KEY:★改兩席時自己弄出一個 bug,跑測試才發現★ — teardown 的移除清單原本無條件列兩席,就算只刪掉一席;那會回報一個沒發生的動作。修法=`_remove_code…
    71 [body]: - **本機模型清單會過期**:`~/.codex/models_cache.json` 第一次讀到的是舊版 CLI(0.152.1)
    81 [body]: 兩席的模型與推理強度要精確、名字不同但指示相同(框架單源)、teardown 兩席都收且清單照實列。
    91 [body]: - **改成怎麼驗**:刪除清單裡不出現那個外方檔 ∧ 檔還在 ∧ 內容還是別人的。**比原本的
    94 [body]: **順帶抓到自己剛引入的一個 bug**:改兩席時,teardown 的移除清單寫成無條件列兩席,
    96 [body]: 改成回「真正刪掉的檔名清單」,teardown 照那個清單列。★這是跑測試跑出來的,不是想出來的★。
  2.215  Systems/slim-scan-掃描器.md  [清單]
    12 [FLOW]: FLOW:先取 `lumos --help` 解析出的指令全集減 KEEP 白名單得 removed 集合 → 再讀交付檔(README/SKILL.md/reference.md…
    14 [KEY]: KEY:removed 集合真值來源=`lumos --help` 解析 choices(非硬編清單),KEEP 白名單(27 支 <!--lumos:count=27 re=\b…
    15 [KEY]: KEY:五種懸空引用形態——①prefixed(`lumos <cmd>`帶前綴)②bare-token(反引號裸 token `<cmd>`)③skill-name(DROP_S…
    16 [★DEBT★]: KEY:★DEBT★(2026-08-01 代碼審 r6 方法論收穫)★掃描器只認「指令名」,認不得「路徑」★——`Projects/xxx_計劃`、`governance/gol…
    19 [KEY]: KEY:★2026-07-31 終審 C1 修正★——原本只掃 markdown,從沒掃過產物 CLI 自己(交付的 `dist/scripts/lumos`)。它的 `warn(…
    20 [KEY]: KEY:★2026-07-31 代碼審 minor-1 修正★——`scan_python_file()` 的候選 `text` 欄位原本是 `" ".join(node.valu…
    48 [body]: 公開精簡版交付前的文字掃描器。掃描 README/SKILL.md/reference.md 等要交給離職接手者的文件,找出還在教「精簡版已移除的指令」或「不交付的 skill」的…
  2.214  Issues/範本空清單被判成純量.md  [清單]
    16 [body]: # 範本空清單被判成純量
    18 [body]: > 白話:新筆記範本裡寫 `aliases: []`(空清單),但工具判型別的規則只認「冒號後面是空的」,
    38 [body]: **為什麼修判定層不改範本**:YAML 標準 `[]` 就是合法空清單;改範本要動 15 篇既有節點,
  2.193  Projects/公開精簡版_計劃.md  [清單]
    22 [KEY]: KEY:切割範圍(★2026-07-31 機械重算★)——`--help` 共 **53 支頂層指令 = 24 保留 / 29 移除**(24+29=53 加總驗訖,零交集零漏列)…
    23 [KEY]: KEY:★r1 發現(已折入;①②=blocker,③④=major,分級以〈審計修正紀錄〉正表為準)★——①[S1] 正面表列留下「沉默地帶」,而 [S2] 規則是「白名單**外…
    24 [KEY]: KEY:★r2 blocker(已折入)★——**r1 的 blocker② 在「聲稱已修好它」的那一節原地復發**:上一版在 [S4-a] 列了一份精確到行號、看起來窮盡的懸空引…
    26 [KEY]: KEY:★放行裁定=**未收斂,人裁放行**(2026-07-31)★——settle gate rc1(清單 25/35 結清,10 條未結清:S1-2~S1-7/S2-1~S2…
    73 [body]: **保留清單（機械枚舉，24 支）**：`append` `archive` `backlinks` `context` `contracts` `decision-add` `d…
    87 [body]: **移除清單（機械枚舉，29 支）**：`anchor` `bootstrap` `canary` `ci-status` `ci-wait` `cochange` `code-l…
    91 [body]: > ★**函式層數字不寫死在 spec**★（r1 教訓）：原稿把手算的「要砍 39 支 `cmd_*`」當可行性證據與驗收數字，三席獨立重算皆兜不起來（辯方實作原型實測，在**當…
    148 [body]: | `install.sh` | 碰專案層 | ❌ **錯誤**——它只有一行 `exec ... lumos install --force`，`cmd_install` 全部動…
    … 還有 50 處
  2.180  Systems/授權與歸屬.md  [清單]
    17 [★INVARIANT★]: KEY:★INVARIANT★ 主程式 scripts/lumos 的檔頭必須同時帶 SPDX 兩行與 MIT 全文——它會單獨飄進別人的 repo,而根目錄 LICENSE 不會…
    68 [body]: - ★這份內層清單是從套件相依關係推出來的,沒有逐段讀那 1.29MB 壓縮碼確認★。REVISIT:2026-12-06 若升級 3d-force-graph 版本,用會產授權清…
    75 [body]: - **不去翻那些交付合約**有沒有「第三方開源須事前核准 / 須提供開源清單」條款。
    86 [body]: - **3d-force-graph 內層清單是從相依關係推的**,沒有逐段讀那 1.29MB 壓縮碼。REVISIT:2026-12-06 若升級版本,用會產授權清單的工具重跑核…
    93 [body]: - **檔案清單是手寫的,跟真正會被複製的集合對不齊**。在 `scripts/hooks/` 頂層(不是 claude 子夾)新增一支沒標示的檔,它會被真的複製出去,而手寫清單掃…
  2.174  Systems/delguard.md  [清單]
    25 [KEY]: KEY:排除域與 pre-commit should_exclude 對齊(7 目錄+lock 三檔名),漂移由 t_precommit_whitelist_drift_guard…
    27 [KEY]: KEY:[2026-09-06]★逾時降級的真因是命中行數,不是 token 數★——帳上 30% 執行是逾時降級(守衛在半盲狀態下擋人)。原以為跟 token 數有關,量出來是:…
  2.169  Systems/hook信任邊界.md  [清單]
    57 [body]: - **上面那句話的前提是「複製清單只複製那五支主檔」。** 只要把共用模組也放進複製清單,
    61 [body]: 1. **共用模組要在複製清單裡**(`_GLOBAL_CLAUDE_HOOKS`)。
    63 [body]: 凡是被複製的 hook 所 import 的本地模組,都必須也在清單裡。
    97 [body]: ### 三、錨點清單補上四支沒人盯的 hook
    99 [body]: 版控裡有 8 個 hook 檔,錨點清單只列 4 個——**另外四支被改了、或偷偷多一支,守衛一句話都不說**。四支補進清單,並加一條「清單 vs 實際檔案的集合要相等」。
    103 [body]: ★做的時候踩到一個★:集合檢查第一版用版控清單當真相來源,但逐檔比對那半看的是檔案系統,**兩個來源混用就會互相打架**——在「hook 存在但沒 git add」時誤報成「登記過…
    135 [body]: ### 二、寫死清單的守衛,守不到清單外的東西
    143 [body]: ### 三、排除清單自己變成躲藏處
    … 還有 1 處
  2.163  Projects/流程優化六件_計劃.md  [清單]
    16 [KEY]: KEY:2026-08-05 Enzo 裁「都做」的六件流程優化,全數同日落地——每件掛在 2026-08-04 實戰痛點上:①散落漂移機械掃進 design-loop skill…
    17 [KEY]: KEY:★追加第七件(2026-08-05 Enzo 裁「這個標籤可以硬性寫入嗎,讓LLM去做」)★——aliases 宣告制(lint 硬擋新 system/issue 缺鍵;[…
  2.134  Systems/測試假綠形態.md  [清單]
    17 [FLOW]: FLOW:寫測試/審測試時逐條對照本清單 → 命中哪一型就照該型的「怎麼接住」處理 → 修 bug 收尾跑「還原翻紅釘」時★必須同時放一條「現場成立」前置斷言★(否則對第④型全瞎)
    18 [KEY]: KEY:本專案撞最多次的坑=「測試存在但沒在驗它宣稱要驗的」,已累計 ★16 次★(2026-08-02 第 12、2026-08-03 第 13/14/15/16,★五次都是新測…
    22 [KEY]: KEY:★假設一定有第九型★——本清單是「我枚舉了 N 種形態」,而本專案已被這句話打臉多次(slim-scan 五形態掃不到路徑型、CLI 揭露段列三支漏第四支)。★不得把「對照…
    23 [KEY]: KEY:外部對照——mattpocock/skills 的 tdd skill 定義了 **tautological**(斷言用跟程式碼同樣的方式重算期望值,天生會過、永遠不可能跟…
    27 [TEST]: TEST:清單本身不可測(它是判讀用的分類法);上方那條硬合約由 t_slim_uninstall_manifest_parent_cleanup_is_best_effort 與…
    82 [body]: ## 為什麼要有這張清單
    86 [body]: 沒有清單的後果是：每次撞到都當成新的、當場想一個對策，下次換個外表又中一次。
    96 [body]: - 出處：借自 mattpocock/skills 的 `tdd` skill（它叫 tautological）。★這是本清單唯一一條有外部現成定義的★。
    … 還有 6 處
  2.131  Verification/2026-08-23_about_code存量雙評審落地.md  [清單]
    30 [body]: Gemini 看我給的摘要(非全文):一致率 **22%**,107:16 一面倒,50 篇給空清單——
    36 [body]: - 我派工清單**手抄錯 19 篇**(從昨日 fanout 清單抄,漏了後來補標的那批);Opus 多讀了 17 篇不在範圍的
    60 [body]: 83 篇:72 篇有清單(118 條),12 篇空清單只蓋 stamp。
  2.131  Verification/2026-07-28_settle收斂閘.md  [清單]
    8 [fm]: - "清單檔 JSON schema v1(entries[]:id/kind/claim/status/verified_in_round/spec_sha)"
    29 [body]: - **清單檔 fail-closed**：不存在／壞 JSON／零條目（vacuous pass 拒收）／llm-ok 缺 verified_in_round。
    38 [body]: - 清單檔格式裁 **JSON**（spec 待辦留 YAML?——零依賴家規 stdlib 可解，YAML 需外掛，裁 JSON）。
    44 [body]: - settle 尚無真實 loop 消費（dogfood 待第一個高風險 spec 啟用；spec 待辦：首兩個真實 loop 人工複核清單）。
  2.129  Systems/lint-version-watch.md  [清單]
    31 [KEY]: KEY:rc——成功(含缺/空清單)=0;清單格式壞=2;網路失敗永不升 rc
    48 [body]: - 版本比較純數字 tuple + 等段數守衛:current 須與 registry 同版本方案、同精度宣告(靠人維護,清單漂移會漏報)。
  2.126  Projects/固定席降噪A層_計劃.md  [清單]
    11 [KEY]: KEY:尺=固定席噪音數(主目標;★不押絕對值,以 knob=1 臂考卷實測為準★)+ P@8 逐 byte 不變(結構保證)+ must_in_out cap 內不退(結構保證;…
    80 [body]: 2. **參考道(reference lane)——★r2 折入版:獨立容器+產生階段 cap★**:被 1 降的節點★自始不進 `results` 共用清單★
    85 [body]: 結構性不受影響;要用 lane 的地方**明文 opt-in**(名單見 #2b)。★diff 聚合明文:lane 不進 --diff 清單與 sync-check★
    99 [body]: ③`retrieval_eval.py` `edit_universe`:★回傳形狀定死(v4 s1f3/s2f3)★——合併清單(lane 項保留 `lane` 欄位標記),
    109 [body]: 不是首屏推薦;edit_universe 合併清單後這裡要明文排除,否則 results<3 的題會把 lane 誤算進「人先看到的三行」);測試⑮釘。
    117 [body]: 3. **結構保證(r2 誠實化)**:free 集合與排序完全不動 → P@8/nDCG 逐 byte 不變——★前提是 §2 的獨立容器與全站分流清單一處不漏★
    141 [body]: per-split 棘輪列工具清單——★實作落點是 `main()` 呼叫端(現行只比 "all"),`must_ratchet` 函式本身已支援 split(s2 查證)★。
    144 [body]: ## 工具清單(草)
    … 還有 8 處
  2.124  Projects/條款綁測試算進度_計劃.md  [清單]
    13 [KEY]: KEY:★三個轉述前提驗過不成立★:test-cache 只存失敗清單(不能拿來算綠)、Check T 不讀計劃正文、lumos task 不存在;bound-tests 帳★不記…
    53 [body]: > 題目一句:設計審產出的驗收條款清單,實作時「認領→做完勾掉」怎麼不漂?
    66 [body]: ——BDD 讀測試結果、GitHub 子 issue 關掉父清單自動勾、PR 合併自動關 issue。
    75 [body]: | 「完成=不跑測試,讀測試每次跑都留的快取」 | 推送閘寫的 `.lumos/test-cache-shard*.json` **只有 `{"failed": []}`**,是 …
    81 [body]: `bound-tests` 治理帳一筆記的是 **節點清單 + 「46 綠」這種計數**,★不記測試名★。
    203 [body]: 外家 #2 零條定義硬擋會誤殺只在散文/標題提到 [SN] 的正常計劃 → 只在「像清單項卻不認得的前綴」時擋,純引用視同未啟用;#3 真條款同一行的「詳見 [S2]」被當第二條 …
    205 [body]: - **-b r1(驗收 r3 折入)**:架構席全對齊;單reviewer 1 blocker——`a. [S1]`/`一、[S1]` 這種字母/中文編號前面有「詞」,被「像清單…
    206 [body]: - **-b r2**:架構席 major——三條行內可見規則散在解析器裡,又是第二份 → 收成 `_strip_inline_markup`(跟 `_visible_lines`…
  2.113  Projects/關係層傳播守衛_計劃.md  [清單]
    12 [FLOW]: FLOW:改B的決策/合約→hook自動impact-from-B→機械列鄰居→人/AI判「真傳播嗎」→確認的進工作清單展下一跳(cycle guard)→plan節點留帳;補網=…
    18 [KEY]: KEY:連鎖防爆炸鐵則=非「自動展N層」是「確認才前進的工作清單」;只有判定真傳播的節點才長下一跳,follow真依賴脊椎、死支斷掉——否則2-3跳點名半張圖=麻痺
    22 [DECISION]: DECISION:[2026-07-14]連鎖=判斷閘工作清單非盲BFS(valid)｜擴impact現有引擎不重造(valid)｜advisory不硬擋(valid)
    29 [fm]: - content: 兩張網補關係層語意驗證:主網=改節點觸發的判斷閘連鎖確認(擴impact --node+hook)、補網=doctor Check E週期掃frontmatt…
    50 [fm:why_chosen]: why_chosen: 架構已穩、續推邊際遞減且剩的是實作合約非設計對錯;凍golden保三輪findings+待釘合約清單,實作另議。補網E1現成可建、立刻把頭號腐爛變免費週期檢…
    68 [fm:why_chosen]: why_chosen: 先出高信號低噪音的 E2(全圖僅 2 條被推翻決策、來源都已跟上→0 假陽性);E4 照 spec 出會變每輪 14 條麻痺清單,違背 warn_soft …
    104 [body]: - `[S4]` **連鎖＝確認才前進的工作清單（防爆炸鐵則）**：**非「自動展 depth-N BFS」**（圖譜 2-3 跳連半張圖 → 點名爆炸 → 麻痺）。只有 `[S3…
    105 [body]: - `[S5]` **帳本＝plan 節點**：連鎖的工作清單 + 各節點判定寫進一個 plan 節點（可中斷、可續、可稽核）。變更夠大（跨 session/多節點）才開 plan…
    … 還有 1 處
  2.110  Projects/精簡版update指令_計劃.md  [清單]
    18 [KEY]: KEY:hooks=隨包 opt-in 檔案(install.py 永不裝,非目標不變);回填來源釘 GitHub main 6e249eb;複製清單補 hooks 與 WINDO…
    22 [body]: > 白話:精簡版目前是「凍結快照」——沒有 update 指令,想更新只能重跑一行安裝(它本來就冪等:已裝過→git pull→重裝)。使用者裁示(2026-08-18):把這條路…
    27 [body]: - **工廠漂移(本案順帶修)**:①Citrus_Lumos 的 `hooks/` 目錄(pre-commit/post-commit)只存在發行 repo,`slim/` 無、…
    41 [body]: ### S2 slim-gen 複製清單補齊+hooks 回填工廠
    43 [body]: - `slim/` 新增 `hooks/`——★決策脈絡明文(std-r1 兩席質疑「與『不裝 hook』裁定衝突」,以遠端現況反證後補述)★:hooks=**隨包交付的 opt-…
    64 [body]: 3. `t_slim_gen` 既有案不倒退;複製清單補檔後 dist 含 hooks/WINDOWS-NOTES(斷言入 t_slim_update_injection 或既有 …
    92 [body]: - **std-r1 折入迷你核對(2026-08-19,便宜席,4 命中全修,不算 loop findings)**:①PRIOR-ART「零新邏輯/只提 --force」未跟上…
    93 [body]: - **pre-flight(2026-08-18,機械排乾,不算 loop findings)**:3 命中全修(全在測試收口)——①S1③無 git 分支補測(behavior…
  2.105  Systems/anchor-integrity.md  [清單]
    81 [body]: ## ★清單從 6 個變 10 個,而且多一條「集合要相等」(2026-09-07)★
    83 [body]: **發現什麼**:這道守衛原本只逐條比對「清單裡有的檔」。而版控裡 `scripts/hooks` 底下有 8 個檔,清單只列 4 個——**另外四支會自動執行的 hook,內容被…
    85 [body]: 四支補進清單(進場提醒、改檔前推合約、收工查圖譜、推送後回報 CI),並加一條:**清單裡的 hook 檔集合,必須等於實際存在的 hook 檔集合**。偷加一支會被點名。
    92 [body]: **做的時候踩到一個,值得記**:集合檢查第一版拿版控清單當真相來源,但逐檔比對那半看的是檔案系統。**兩個來源混用會互相打架**——「hook 檔存在但沒 git add」時會誤…
  2.105  Systems/lumos-cli-write.md  [清單]
    21 [KEY]: KEY:[2026-08-05]decisions 結構守衛修假陽性——原始條數只認 entry 縮排層(恰 2 空格),alternatives_considered 巢狀清單不…
    25 [KEY]: KEY:[2026-08-23]`remove <note> <key>`★不帶 value=把純量欄位整個拿掉★(design-loop about-code-field r3 …
    52 [fm:context]: context: ruamel round-trip 重序列化整份 YAML 會 reflow、破壞「構造性最小 diff」(只改該改的行、其餘逐字原樣),也可能誤動子清單
    100 [body]: 鐵則完整清單在 `skills/lumos-project-notes/reference.md`(格式鐵則 1-4;CLAUDE.md 的「三條鐵則」是另一套工作紀律,別混——2…
  2.104  Systems/check-y-symbol-existence.md  [清單]
    26 [KEY]: KEY:★否定語境豁免★=節點常「正確地記錄某符號已不存在」(「X 全庫零命中」「原記 X 無此方法」),對這種行報錯是把正確紀錄當錯誤;此為★唯一★誤報來源(2026-08-12…
    89 [body]: 對這種行報「repo 查無」是**把正確的紀錄當成錯誤**。清單：
    98 [body]: - 否定詞清單是**列舉式**，新的說法（例如「已封存」「凍結」）會漏——★但這是可增補的字典問題，不是結構限制★
    102 [body]: > ★根本就是同一類否定語境，只是清單漏了「棄用/不使用」這組詞★。補進去之後誤報歸零。
  2.102  Projects/cochange守衛_計劃.md  [清單]
    39 [body]: 解 [[Projects/社群演算法補強_調研]] 缺口 c（知識同步散落）：機制同步只改最相關段、漏散落的列舉表/清單，人手動也漏。做一個 **co-change mining …
    51 [body]: - **排除清單**（挖掘與 check 皆套用；`.lumos/cochange.json` 的 `exclude` list 可增補，與預設合併）。預設 pattern（**精…
    53 [body]: - （r1 辯方的噪音實測 1/22、4/247 是**未套排除**的原始噪音率——證明排除清單是 belt-and-suspenders 而非主防線；非「排除已生效」的證據。）
    64 [body]: - `lumos cochange check [--staged | --diff <A..B>] [--repo <root>] [--json]` — 對「本次變更檔案集」比…
    65 [body]: - **rc 語意（rules/check 統一條件式）**：正常執行（不論有無警告/規則，**含 zero-commit repo 的空結果**）→ rc 0；git/subpr…
    92 [body]: ## 交付同步清單（散落列舉表——本守衛的立意，自己不能漏）
    104 [body]: - 規則計算單元測：合成 git 歷史（tmp repo 真 git init + commit）驗 conf/support 數字、merge 排除、大 commit 排除、mi…
    128 [body]: - **r2（2026-07-10，panel W=3；canary slot1 caught（c 型未定義欄位，性質點名正確）、slot2 **missed**（d 型未定義產物…
    … 還有 1 處
  2.102  Projects/派工鏡頭注入_計劃.md  [清單]
    13 [fm]: - "[[Projects/派工時自動補清單_計劃]]"
    23 [KEY]: KEY:Enzo 裁(2026-09-03):散文審查的清單本質是鏡頭;可執行層(合約綁測試)已存在且只有它該是閘;★不要求鏡頭證明有用★
    26 [KEY]: KEY:★清單早就算得出來★(impact --diff --json 固定席四欄位);採用機制=代碼審模板 §3 第 3 格由「手貼固定席」改成固定一行標記,hook 補內容;★…
    27 [KEY]: KEY:r2(21 條/blocking 16/4 blocker,全折)立下★消毒原則=來自圖譜或 diff 的自由文字零輸出★:只印固定字彙(合約類別/kind)、base 已…
    28 [KEY]: KEY:r3(21 條/blocking 14/4 blocker,全折;上限到)裁★hook 薄殼、邏輯進 lumos 新子命令 dispatch-lens★沿用既有 helpe…
    36 [fm:context]: context: 2026-09-03 五份計劃全死於設計審(收斂閘漏項敏感度 v1/v2、派工時自動補清單、審查帳節點映射、折入去重留痕),四份死在想證明清單有用(量覆蓋率/記映…
    37 [fm:why_chosen]: why_chosen: 存活事實三件(攔得到/清單算得出/沒人貼)剛好拼成鏡頭版;砍掉量測支線後,五份計劃二十幾條 blocker 只剩三條仍適用(措辭中性/用既有合併器/誠實揭露…
    46 [fm]: - content: 固定席清單仍用工作樹圖譜算,不改(分支作者能「藏」節點,不能「說」);事件型回頭:要拿本 hook 當閘之前必須先修
    … 還有 12 處
  2.097  Projects/閘觸發帳統計_計劃.md  [清單]
    20 [body]: > 白話:治理帳寫了兩萬多筆,從來沒人回頭算過「哪道閘在做事、哪道從沒響過、哪道每次都響」。本案給既有的 `lumos gov` 加一段唯讀統計,把**每道閘的筆數/節點數/com…
    91 [body]: - `hard`:布林,`true`=硬擋、`false`=軟提醒(advisory)。`nodes`:涉及節點名清單,**可為空陣列**。
    106 [body]: #### 未出現清單(唯一的「解讀」,且只解讀到「沒出現」為止)
    110 [body]: ★前置要件:必須有 gate 全集★——「逐 gate 掃出現過的值」永遠看不到零筆的 gate,而 repo 內**目前沒有任何 gate 註冊表**(實查:無 `_GATES`…
    112 [body]: 清單旁固定印一段限制聲明(逐字,不可省)。★誠實承認:換掉標籤不改變結構——一份「沒出現的閘」名單被讀的時候仍然像嫌疑名單(r3 s2 席)。本案能做的只有把限制寫死進輸出、且用測…
    114 [body]: > 未出現 ≠ 無用。本帳看不到硬擋事件(`anchor verify` 擋下 push 時不寫任何帳),也分不出四種「沒出現」:跑了沒事／接了帳但沒被觸發／守的功能從沒被用過／*…
    122 [body]: - **零觸發桶**降級成「未出現清單」——同一份資料,但不再貼「這道閘可能沒用」的標籤。
    128 [body]: - **位置參數 `node` + `--stats`**:`cmd_gov` 在去重後、任何下游計算前就把列縮到單一節點(`scripts/lumos:2958-2960`)。本…
    … 還有 9 處
  2.095  Projects/中心性重驗排程_計劃.md  [清單]
    17 [KEY]: KEY:advisory 純顯示排序——不新增輪詢、不改 Check S 判定語意、gov_events 寫入順序不動(只重排顯示清單,掃描迴圈不動);Check S 前 8 筆截…
    33 [body]: - **Check S 軌（System 候選）**：**純 PR 排序，不乘天數**——Check S 現行語意是二值過期判定、無天數概念（sa_missing 清單連日期都沒有…
    35 [body]: - [S3] **顯示整合**：`lumos stale` **僅 bare 模式**預設融合排序＋分位欄（＝[S2] 三段 band 標籤，同物同名）（`--match`/`--…
    52 [body]: - [S3]：Check S 兩清單各自 PR 降冪（斷言各自前 8 選集符合）；gov_events 寫入序不變；`--match`/`--candidate` 輸出不受影響。
    58 [body]: - r1 light 單席（2026-07-28，canary type a「A9 靜態先驗乘數」caught；probe 重植×2 頂格如實註記）：**blocker×1**＝排…
  2.093  Systems/check-n-recomputable.md  [清單]
    23 [KEY]: KEY:★2026-06-10 就記過教訓「計數/清單型主張最會漂」卻沒配機制→兩個月後照樣復發★。這就是「知道了但沒有機制逼你做」的標準案例——本檢查是那個缺掉的機制
    55 [body]: | QA驗收清單 | 「46 場景」 | **40**（§9.4 被砍） |
    60 [body]: ★**最刺眼的是**★：2026-06-10 的首輪交叉審計**就把這條寫成教訓**了——「計數/清單型主張最會漂，這類數字要附截止日或乾脆不寫死」。
  2.089  Systems/design-loop.md  [清單]
    36 [★INVARIANT★]: KEY:★INVARIANT★ 處置閘第五步(2026-09-08,[[Projects/條款綁測試算進度_計劃]] d3/d4):設計審迴圈(loop id 不是 code- 開…
    51 [KEY]: KEY:★經濟學★[2026-07-20 使用者裁定,見 decisions d5]——spec 品質目標=成本平衡非精確度漸近線:缺陷分層定價(清單型→pre-flight/撞自…
    52 [KEY]: KEY:[2026-07-16]提效 M1 落地(見[[Projects/design-loop提效_計劃]])——pre-flight 排乾(panel 前便宜 agent 掃清…
    59 [FLOW]: FLOW:brainstorming產spec→[trivial?跳並註明]→前置排乾(refcheck機械核對spec→repo指涉+pitfalls --check補實務隱患節…
    79 [fm]: - content: canary 類型由輪序 N 決定 type=清單[(N−1) mod 4](a 壞§ref／b 未定義旗標／c 未定義欄位／d 未定義產物),無需 stat…
    97 [fm]: - content: spec 品質經濟學(d4 續章)——目標=成本平衡的品質提升,非精確度漸近線。四原則:①缺陷分層定價:每類缺陷在最便宜層抓——清單型(未定義詞/斷引用)→p…
    103 [fm]: - content: code-loop 正確性鏡頭派工措辭升級(2026-08-28):名詞清單(bug/邊界/資源/例外/冪等/併發)改成帶例子的問句+明講排除(風格與架構歸架…
    105 [fm:context]: context: 先問世界(WebSearch 2026-08):業界最佳實踐兩獨立來源(awesome-reviewers『規則+為什麼+例子』、Cloudflare/DEV『告…
    … 還有 1 處
  2.081  Verification/2026-08-18_標註刷新落地.md  [清單]
    23 [VERIFY]: VERIFY:真庫驗收——①重放 ab910519:touched 口徑未標 401/668(60%),固定席全在觸及集內=當年 77 噪音依構造必被接住;repin 硬擋+吐清單…
    35 [body]: 3. **真庫重放**(讀側觀測,零寫入):崩分快照 ab910519 未標 60% vs 原快照 13.7%——語料前進效應與邊界欠帳分離清楚;repin 對 401 筆未標 r…
  2.078  Systems/judge-perturbation-stability.md  [清單]
    16 [DEP]: DEP:governance/autonomous-loop.sh(RESIDUAL 清單)｜confidence_report.py｜judge-severity-gate(被它…
    50 [body]: 改用日報 inspirations 的更輕路線:`confidence_report.py` 的可信度報告把「殘留風險」升級成 **「⚠ 這個迴圈沒檢查到的維度(品質最可能爛在這、…
  2.077  Projects/install全域hook同步_計劃.md  [清單]
    19 [KEY]: KEY:懸空 vs 真檔——舊機 ~/.claude/hooks/code-loop-guard.py 若真檔還在,_prune_dangling 不剪(非懸空);install …
    50 [body]: 2. **撤除檔清理（新，對稱 2026-07-06 ADR）**：`rm -f ~/.claude/hooks/code-loop-guard.py`——已撤除的舊 Stop n…
    73 [body]: - **撤除清單維護**：「已撤除 hook 主動刪」清單（現只 code-loop-guard）未來撤別的 hook 要補——與 merge-claude-settings 的移…
  2.071  Verification/2026-07-16_replay校準baseline_v0.md  [清單]
    16 [KEY]: KEY:三結論——①haiku 剖面=grep 可得能抓(白名單/詞不存在),推理/交叉對照型全滅→pre-flight 的 haiku 只配機械清單,語意審最低配 sonnet …
    61 [body]: 1. **haiku=機械清單專用**:grep 可得(白名單缺欄/函式名不存在)能抓;需推理或交叉對照(正則隱形/靜默放行/字母撞名)全滅。pre-flight cascade …
  2.060  Projects/兩席相反時端出張力_計劃.md  [清單]
    27 [KEY]: KEY:★裁定(Enzo 2026-09-09,d1)三塊都做★——(一)第四種表態 `tension`:必填 chosen(existing|suggested,小寫)/exis…
    62 [body]: - **形狀**：`{"status":"tension","question":原文,"chosen":"existing"|"suggested","existing":["p…
    63 [body]: - **寫側**（`_dispositions_validate`）：`status` 四值只認小寫，錯誤訊息改成「只認小寫 satisfied/na/todo/tension」；…
    64 [body]: - **讀側**（`_dispositions_verdict` 的 `_one`）：`tension` → **先重驗 `existing` 是非空清單且 ≤20 項**（r1 …
    65 [body]: - **印法**（`cmd_code_loop check` 人可讀模式）：判定印完（OK 或 BLOCKED 都一樣）之後，`tensions` 非空就在 stderr 多印一段…
    76 [body]: - **輸出**：`arch_alignment["tension_candidates"] = [{"file":F,"question":qid,"patterns":[…],…
    91 [body]: - [S1] 寫側：`code-loop dispositions <檔>` 對 `status=tension` 的題——缺 `chosen`／值不在小寫 existing|su…
    92 [body]: - [S2] 讀側與印法：`code-loop check`（有適用題）對 tension——`existing` 為空清單／非清單／>20 項、某項在被推送 sha 的樹不存在或…
    … 還有 2 處
  2.051  Projects/執行DAG_調研.md  [清單]
    15 [KEY]: KEY:★腐化數字(★量測時點 2026-09-07,含活計數,引用必帶時點★)★:Projects 標 doing 43 篇(母體 155,含本篇自己)、其中 17 篇 >30 …
    20 [KEY]: KEY:★成敗條件★任何新任務狀態「不能從證據重算」就不要做——腐化數字+TDAD(arXiv 2603.17973:只加散文提醒 6.08%→9.94% 反而變壞,給機械算好的清…
    51 [body]: PRIOR-ART:①最小解在既有機制層——「唯一下一動作」的神諭已經有了(`lumos loop next`,只讀帳本結構不讀散文),只差一個「列出現在開著的迴圈」的入口;結構化…
    100 [body]: | 實作計畫的 checkbox 維護 | 一篇 `status: done` 但 **60 個框一個都沒勾**(12 Task×5 Step,外家確認全是實作步驟、不是驗收清單)…
    101 [body]: | [[Projects/全repo審視_計劃]] 的 50 群主清單 | **表格沒有「做完沒」這一欄** | 進度靠翻 git 提交訊息裡的 `#編號` 回推;開頭「一件都還沒…
    109 [body]: 2. **★結構化逐條進度清單——原稿當成正面前例,外家查證後翻成反證★**:`.lumos/settle/公開精簡版-settle.json`,35 條,每條 `{id, kin…
    147 [body]: - 只結構化實作計畫的任務拆解 + [[Projects/全repo審視_計劃]] 的 50 群主清單——那是 repo 裡唯一真有依賴、有分包、有嚴格順序的地方。
    161 [body]: **所以 B 要能成立,得先定義四件事(外家開的清單,本家接受)**:①哪幾類任務有資格進 DAG;②沒有測試函式的任務,客觀完成證據是什麼(commit trailer?diff…
    … 還有 1 處
  2.047  Projects/標註刷新_計劃.md  [清單]
    14 [KEY]: KEY:四件套+S0(r1 定錨)——S0 共同定義(★評測母體=計分觸及集:search 兩臂各前10/edit free 前8+全固定席——2026-08-18 落地後發現:全…
    16 [KEY]: KEY:刻意不做——★「指標語意不改」2026-08-26 已被翻(condensed 上路,詳 [[Projects/評測尺翻案_計劃]];本篇 decisions d1 已標 …
    54 [body]: - **題目凍結**:delta 模式只讀 goldset 既有 `search`/`edit` 題目陣列,★禁重呼 `edit_cases()`★(它按當前 HEAD 的 git…
    58 [body]: - 新腳本 `governance/eval/refresh_labels.py`(獨立於 build_goldset,rc 語意乾淨;r1:CLI 介面明名)——`python3…
    71 [body]: - `refresh_labels.py repin`:斷言目標語料**評測母體** `unjudged == 0` 才寫入 `snapshot_commit`;否則 **rc1 …
    76 [body]: - 週閘 wrapper=`governance/autonomous-loop.sh` 週期考卷段(現呼叫 `retrieval_eval.py --goldset … --sp…
    80 [body]: - 變更節點重標:節點內容改動後舊標註可能過期——v1 僅列「mtime > labeled_at」清單軟提醒,不阻塞重釘。★殘留風險明文(r1):S3 綠=無未標,不保證舊標仍新…
    90 [body]: - **[self-governance]**:S3 是擋人閘(rc1)——假紅風險=delta 清單誤報;斷言邏輯與 S1 同源(同一份評測母體計算),不另寫一套。
    … 還有 1 處
  2.036  Projects/代碼審資安席_計劃.md  [清單]
    5 [KEY]: KEY:處置閘第六步 _disposal_security_step:定錨分級 high 的 code 迴圈,整個迴圈要有席名任一段=資安/security 的帳列、報告 sha …
    41 [body]: PRIOR-ART: ①最小解層級=既有處置閘加一步(照 `_disposal_clause_step` 的形狀)+既有編制表加一席+既有派工範本加一節;不新增指令、不動 `cod…
    57 [body]: - **看過的檔要涵蓋最後一版**(設計審 r1 外家否決 E1;★代碼審 r1 通才 A1/資安 C1 改成比內容★):代碼審每輪的凍結材料是整條分支的 diff(`git di…
    71 [body]: - [S5] skill 說明同步:明列檔案清單,加一支文件同步守衛測試,照 `t_marker_doc_sync` 的寫法——逐檔列舉、缺一就翻紅(r1 通才 A5、整合 C5)…
    105 [body]: - 守衛面(這本身就是一道閘):誤擋與漏擋兩邊都要顧(r1 邊界 B2 指出原清單不完整)。誤擋——判定輪只派一席、生效日前開的迴圈、席名沒帶模型尾碼、模型名自己帶連字號、席名前面…
    115 [body]: - 同上但有一筆 `資安-sonnet` 帳列、報告 sha 對、它的凍結 patch 檔案清單涵蓋判定輪全部檔 → 資安席這一步 ok(其餘各步照舊判)。
    117 [body]: - 資安席在 r1、判定輪 r2 的 patch 多一支 r1 沒有的檔 → 未過,訊息點名那支檔;r2 的 patch 檔案清單是 r1 的子集 → ok(迴圈層級,r1 外家否…
    125 [body]: - 文件同步守衛:[S5] 清單上每個檔都提到資安席;清單上的檔都不再寫「四條合取」;設計審派席說明沒有資安席。
    … 還有 1 處
  2.036  Issues/hook卸載殘留註冊.md  [清單]
    23 [KEY]: KEY:通則=凡「A 端刪除、B 端引用」的成對資源(腳本↔註冊/檔案↔複製清單),守衛要嘛做成對稱操作、要嘛在 B 端做懸空自癒;同型前例=C1/T12(註冊了沒複製)的鏡像(複…
    43 [body]: 凡「A 端刪除、B 端引用」的成對資源——腳本↔settings 註冊、hook 檔↔複製清單——守衛要嘛做**對稱操作**(刪必解註冊),要嘛在 B 端做**懸空自癒**(引用失…
  2.033  Systems/lumos-cli-lifecycle.md  [清單]
    20 [KEY]: KEY:★2026-08-01 teardown 的 Windows 兩處補洞★——①確認提示的 `input()` 是裸的,而 `cmd_deinit`(6766)與 `_con…
    26 [KEY]: KEY:_VENDORED_TOOLKIT 白名單=5檔(scripts/lumos、test_lumos.py、merge-claude-settings.py、graph-re…
    35 [KEY]: KEY:★2026-09-04 Codex 完全支援 S0★:install/uninstall/teardown 多一家——skills 也連到 ~/.agents/skills…
  2.015  Systems/每支檔有家.md  [清單]
    19 [KEY]: KEY:需要家的檔=受版控一般檔 × 程式副檔名(跟「改程式要動圖譜」同一份清單,五份由一致性測試釘住)或首行 #! × 不在排除清單(docs/與建置夾、測試檔、原封不動的工具自…
  2.006  Verification/2026-08-22_狀態表過期偵測.md  [清單]
    53 [body]: - **只認表格**。同型的病寫成清單(`- [ ] ③ 待放行 見 [[X]]`)抓不到。
    54 [body]: ★沒擴大的理由★:清單行的誤報率沒量過,而 28 處那版已經示範了放寬的代價。
    55 [body]: **重啟條件:出現一次「清單寫待辦但目標已完成」害人下錯結論的實例。**
  2.000  Projects/收斂閘漏項敏感度v2_計劃.md  [清單]
    30 [KEY]: KEY:四把尺 M1 復原率(主尺)/M2 偽陽率/M3 帳面動不動/M4 有效場次率;★每把尺都對應到一條讀法,不留孤兒尺(v1 的 M3 就是定義了沒人消費)★;讀法 M1<=…
    73 [body]: - ★第二篇給了設計依據★:同一模型寫**判準**(規則本身)F1 約 0.99,叫它把判準涵蓋的東西**一條條攤出來**就垮。作者原話是問題不在它不懂、也不在說不出規格,而在無法…
    81 [body]: `findings_set` 是編排者自己打進 CLI 的字串。★這裡要講精確★:寫入端(`cmd_canary`,`scripts/lumos:4004`)**有**機械檢查、違…
    125 [body]: **逐席快照的迴圈怎麼處理**(邊界席 major):部分迴圈每輪存共用 `r{N}-snapshot.md`,部分存逐席 `r{N}-snapshot-s{k}.md`,且有目錄…
    159 [body]: 1. **M1 ≤ 40%** → 確認自家也有漏項盲區,外部數字站得住 → **觸發「清單先行」為修法候選,另開計劃**,落點必須是收斂閘。
    184 [body]: - **消費者二**:清單先行做不做,由 M1 直接裁(讀法 1 vs 2),★不留「再看看」這個選項★。
    201 [body]: - 答案卷做不出來(某迴圈的 `r(N-1)` 席報告引句錨不回自己的快照)→ **剔除該迴圈**,計入剔除清單;剔除後樣本 < 4 → ★本案作廢★,寫成「為什麼不做」的紀錄,不…
    209 [body]: - **本案不證明清單先行有效**,只證明有沒有那個洞。清單先行真正有沒有用,要等它做出來、再用同一把尺量一次。
    … 還有 2 處
  1.996  Projects/工具鏈全環節體檢_調研.md  [清單]
    35 [body]: ## 不足清單(依「修的成本 × 止血效益」排序)
    46 [body]: 7. **四份「什麼算 code 檔」清單各自獨立、皆漏 `.sh/.json/.yaml`**:今日 `scripts/external-seat.sh` 溜過同步閘。處置=單一…
    53 [body]: 14. **8 支指令只在 reference.md 一行逗號清單裡出現過**(deinit/teardown/link-candidates/drift-history…):補一…
    65 [body]: - impact-hook 的「必看合約」清單無上限,hub 檔一次 Edit 注入 2,000+ 字,長 session 每 20 分鐘重注。處置=cap 到 top-5 + 「…
  1.993  Issues/vendored測試套件在消費端假紅.md  [清單]
    22 [KEY]: KEY:★元守衛(這才是重點)★=`t_need_src_guards_cannot_silently_disable_coverage`:守衛的失敗模式是「放行」,所以它自己壞掉…
    64 [body]: `t_need_src_guards_cannot_silently_disable_coverage`：掃本檔所有**獨立成行**的 `_need_src("...")` 實際參…
  1.989  Projects/impact-diff橋接_計劃.md  [清單]
    26 [body]: - **聚合語意**：diff 內每支改動 code 檔各跑一次 ranked impact（共用一次載入的圖譜環境——r1 panel N+1 修正），query=該檔 hunk…
    39 [body]: design-loop 收斂→code-loop 過審之後,「退場必寫」目前只有 pre-commit 粗閘（有沒有帶圖譜改動）與人判;精確版=**`impact --diff` …
    41 [body]: **實作（2026-07-11）**：`lumos impact --diff <range> --sync-check`——同一段 diff 內「預期受影響節點(固定席+top-…
  1.981  Projects/guard殺傷力驗證_計劃.md  [清單]
    54 [body]: 4. **判定與合併（r1 折入：timeout 歸 killed，對齊 PIT/cargo-mutants——變異致掛而測試靠超時抓到=接住）**。per-recipe verd…
    62 [body]: ## 交付同步清單
    68 [body]: - 裁定 1 改動明列 ⑥⑦ 的三處硬編同步（cmd_gov/scaffold gitignore/cochange 排除）與 graph-discipline 欄位速查+t_ma…
    97 [body]: - **r3（2026-07-10，panel W=3 delta：2 canaried opus + 1 否決位；canary 2/2 caught（s1=假裁定編號、s2=幽靈…
    99 [body]: - **r1（2026-07-10，panel W=5：4 canaried opus（新出題程序首跑：載重錨定+haiku 探針 4/4 probe:pass+事故庫無匹配走輪替…
  1.975  Projects/連結缺失補全_計劃.md  [清單]
    26 [body]: 殘餘 6 筆 miss 經 `lumos impact --json` direct 清單重放,實況分兩群:
    38 [body]: - **前案合約候選衝突,明文裁決(r1 折入,兩席 blocker)**:[[Projects/hook必看召回修復_計劃]] 合約候選清單提名過「rescue 僅零 direc…
    57 [body]: - 候選清單交人逐筆判「這節點真的管這支檔嗎」;確認的由人(或人授權的編輯)把標準引用(`路徑` inline-code)寫進節點 body 適當段落。
    80 [body]: ## 合約候選清單(收斂提名,候選≠已標——蓋章走 guard 流程)
    98 [body]: - S1 測試:`t_link_candidates`(D1 命中/inline-code 已引不出候選/短詞幹不洪水/D2 家族命中/雙訊號 both/rc 合約);對 B 群 …
  1.974  Projects/公開精簡版_實作計畫.md  [清單]
    26 [KEY]: KEY:★2026-07-31 補追加 Task 9——[S3] 裁定第三次變更,推翻 Task 8「只准附加」,由使用者直接指派★:Task 8 開放的「附加、兩套規則並存」被發…
    31 [KEY]: KEY:★2026-08-01 補追加 Task 13——bash 全部搬成 Python(Windows 真的能用了),由使用者直接指派★:`slim/install.sh`(2…
    32 [KEY]: KEY:★2026-08-01 補追加 Task 14——修兩條 Windows 專屬缺陷,由使用者直接指派★:①`.cmd` shim 寫死呼叫字面 `python`,與 `in…
    33 [KEY]: KEY:★2026-08-01 補追加 Task 15——補 Task 14 明講的殘留缺陷,由使用者直接指派★:Task 14 只修了三支 `.ps1` **結尾**的裸 `ex…
    63 [body]: - **入列實錄（2026-08-11）**：keep 清單實有**四面鏡子**（slim-gen `DEFAULT_KEEP`／t_slim_gen／t_slim_gate／sl…
    75 [body]: | `scripts/slim-scan.py` | 交付文字掃描器：掃 README／SKILL.md／reference.md，找指向已移除指令與不給 skill 的引用，輸出…
    315 [body]: 這條是 spec 放行時的裸項③：現行白名單下**沒有真實的「該砍的迴圈註冊指令」**（唯一迴圈註冊的 `links`/`backlinks` 都在保留清單），所以必須造合成 fi…
    1097 [body]: - [ ] ★**把交付端的 hooks 功能回流進 `slim/` 範本**（2026-08-12 開）★——不做的話，任何人重新生成 `dist/` 再整檔覆蓋都會炸掉交付端的…
  1.968  Verification/2026-07-04_lint-version-watch.md  [清單]
    24 [body]: - `t_lint_watch_cli`(T3)——端到端 subprocess:1 candidate/checked=behind+current/failed(skip+fe…
    36 [body]: - 版本比較靠人宣告同方案同精度(清單漂移會漏報);registry 端點語意變會失準。
  1.962  Systems/native-windows-support.md  [清單]
    20 [KEY]: KEY:無 Windows CI—真 Windows 行為靠手動驗證清單(本機 macOS 只測得到 python 邏輯+Unix 分支),此為本設計最大誠實天花板
    85 [body]: 5. **Claude hooks 註冊靠解析直譯器 + Git Bash 路徑語義**:若 Claude Code 改變 Windows hook 呼叫約定,此處要重驗(屬手動清…
  1.957  Projects/lumos-show讀取入口_計劃.md  [清單]
    21 [KEY]: KEY:圖譜同步義務(r1 折入 F8;r2 擴列散落面)——同一 commit 須帶:[[Systems/lumos-cli-read]]「12」至少 5 處+「23」算式全改+…
    56 [body]: 1. `Systems/lumos-cli-read`——「12」在節點內**至少 5 處**（summary KEY 行/decisions d1/`## 12 個原語` 標題/…
    59 [body]: 4. `Systems/lumos-cli-read` **全節點零副作用宣稱一併改寫（r3 Codex 復核擴列；r4 opus 輪補全）**：**六處**——:11 FLOW「…
    108 [body]: - **C2 同步算術仍錯＋漏 README（major）**：reference.md「44」本身陳舊——現行實為 48（漏 `decision-reindex`/`rel-ca…
    116 [body]: - **S2-F4 檢索優化_計劃:269 同宣稱（context）**：討論節點非權威合約，註明不入清單。
    122 [body]: **r3-前置（2026-07-21，delta 輪 r2 無效＋Codex 復核）**：delta 輪 sonnet×2 **canary 0/2 全 missed=輪無效**（…
  1.956  Systems/slim-readme.md  [清單]
    13 [KEY]: KEY:7 項必要內容=①怎麼裝(`install.sh`)+怎麼確認(`lumos --help`)②進場三步 search→context→contracts ③frontma…
    25 [KEY]: KEY:★2026-08-01 Task 14——〈支援平台〉誠實標記段追加兩項未驗清單★:與 Task 13 那段既有誠實聲明同一段落,追加兩個具體項目(不是新開一節)——①`.…
  1.951  Verification/2026-09-07_loop-list開著的迴圈.md  [清單]
    19 [KEY]: KEY:★設計上的發現★在飛那 35 個裡 12 個是自主迴圈每日場次(`auto-*`)——天生不會關門且一天長一個,不處理遲早淹掉清單;修法=通用 `--exclude <前綴…
    52 [body]: ★最後一列是設計上的發現★:自主迴圈的每日場次天生不會有關門事件、而且**一天長一個**,不處理的話這份清單遲早被它們淹掉。修法是加一個**通用**的 `--exclude <前綴…
    110 [body]: - **`--exclude ""` 改成擋下**:任何字串都以空字串開頭,原本會把清單排空,而印出來跟「全部結案」一模一樣。
  1.945  Projects/主動影響幅度偵測_計劃.md  [清單]
    21 [FLOW]: FLOW:Claude 正要 Edit/Write/MultiEdit code → PreToolUse hook 攔(只 code 副檔名)→ 查 session TTL 快取…
    22 [KEY]: KEY:分工=lumos 只算不判(出直接/間接分層清單)｜Claude 只判不算(語意深度分析消噪)｜hook 只搬運+節流(攔截/過濾/TTL/注入)
    104 [body]: - **lumos 只算、不判**:出「直接/間接」分層清單。
    105 [body]: - **Claude 只判、不算**:拿清單做語意深度分析、消噪。
    175 [★DEBT★]: - **`★DEBT★` 映射**(r9-F7):`extract_contracts` 雖也掃 `★DEBT★`,但 DEBT 是「可改的偶然行為」非合約 → `contract…
    198 [body]: - **注入的指令文字**(附清單後):「動手前先判上列直接/間接節點會不會被你這次改動影響、需不需要同步更新圖譜。消掉不相關的,對真正受影響的:該同步就同步,不確定就記一句。」
    309 [body]: **收尾決定(使用者選 TDD 路,2026-07-05)**:9 輪後判斷——設計層高價值 finding 已榨出(2 真 bug 修掉),findings 不枯竭主因是 (i)…
  1.941  Verification/2026-07-28_S2S3壓縮與驗證器.md  [清單]
    38 [body]: - settle 清單狀態（貶值規則與 gate 同款、無 sha 檢查——版本合規歸 gate 職責）。
    44 [body]: - [S3] 輸入契約裁定：直讀 `.canary-log.jsonl`＋清單檔；結構欄位白名單（kind/severity/findings/auditor 存在性/hash 存…
  1.934  Projects/節點還原SOP_計劃.md  [清單]
    17 [KEY]: KEY:★r3 審計(2026-08-24,5 席,上限輪)實錘要點★:self-audit 翻案恢復雙軌(L4 清帳先例+Check S 只讀該欄;r2 兩席只看指令說明沒對先例…
    18 [KEY]: KEY:★d3/d4 文字澄清(2026-08-24)★:d3 context 的「08 檔」是撞號發現前的歷史用語,現行編號以 d4 的 09 為準;d4 的「三處」是 r2 發…
    54 [fm]: - content: d5(澄清決策,r3 立):新檔編號=09(d3 context 的「08 檔」是撞號發現前用語);「八類」活文字=五處以 [S3] 為準(d4 的「三處」是…
    56 [fm:context]: context: r2 s2 抓到 d3 殘留 08 舊字、鏡像核對抓到 d4 三處過時;第一版只用摘要 KEY 行澄清,r3 架構席判第二種做法(先例=自足性審計 d2「以新決策…
    66 [fm]: - content: d7(Enzo 裁甲,2026-08-24):開新編號 node-restore-sop-v2 審一輪 v4 delta——範圍=r3 折入面(self-au…
    111 [body]: 最典型的觸發:**要在龐大既有 codebase 上加新功能**——先把新功能會碰到的關聯面照本 SOP 還原成節點(只記 codebase 能證的事實),新功能的設計踩在這些節點…
    131 [body]: 這個單元的輸入從哪來、輸出到哪去、**誰還共用它**。查共用面**至少兩個來源**:①拿單元名全域搜用法;②該棧的間接接線處——DI/IoC 設定、路由表、DAG 依賴清單、建置依…
    139 [body]: - KEY=關鍵事實(指針級居多;沒標身分會吃 J-d 計數提醒,提醒不擋、屬預期噪音)。**步驟 2 的共用清單落在這裡**:`KEY:共用面:被 X/Y 使用(承重牆)[src…
    … 還有 6 處
  1.928  Projects/檢索edit面真紅_計劃.md  [清單]
    15 [KEY]: KEY:實驗計畫(train 調參/held 驗證/凍結=考卷×Landmark 雙場同好;參數凍結紀律沿 v1.2)——EXP1 查詢品質閘:delta 文本 shebang/過…
    68 [body]: - **過擬合 held**:實驗在 train 選型、held 只做最終確認一次;逐案勝負清單防「macro 升但個案崩」。
  1.928  Projects/Android側UI測試綁圖譜工作流_實作計畫.md  [清單]
    15 [FLOW]: FLOW:A 段(本 repo,可立即做完)=修 pitfalls-code-loop 證據路徑+補 Android 通道散文→skill 退場段加 UI 面問句(時機觸發者)→r…
    58 [body]: - Modify `.maestro/README.md`：測試門店約定＋裝置 ready 清單
    72 [body]: 3. *既有機制小修蓋得住嗎*：蓋得住——`t_precommit_whitelist_drift_guard` 已經是「跨檔同源清單」守衛，加一條斷言即可，**不新造 detec…
    252 [body]: ### Task 7：測試門店約定＋裝置 ready 清單
    304 [body]: ### 未驗清單（全部明記，無靜默跳過）
  1.928  Verification/2026-08-25_設計審收斂重定義落地.md  [清單]
    6 [fm:revalidate_when]: revalidate_when: "[S6] 下一個真實設計迴圈按新制跑完(校準 prose-lint 詞表與 d3 門檻、抽驗 blocking 綁定矛盾率、判 d1 升級條件)…
    9 [KEY]: KEY:[S1] `lumos prose-lint` 子命令落地(62→63)——中文模糊措辭掃描 19 詞保守版,恆 rc0 advisory,排除 code fence/引句…
  1.920  Projects/roster對帳併入問閘_計劃.md  [清單]
    23 [body]: - **[S1] 範圍=--disposal 且 rid 為真 rN**:`cmd_loop_status` 把 `roster` 布林傳進 `_loop_status_dispo…
    25 [body]: - **[S1c] 異常留痕(r2 d-f7;r3 e-f3 顆粒度)**:先收集全部異常種類、印完全部異常行,**最後一次性** append 單行到 `governance/r…
    46 [body]: **std-r3(delta 席 4 條全折,cap 輪)**:e-f1 兼任一名兩義拆開;e-f2 出口清單寫全(三個 return 2 路刻意不掛+註解);e-f3 log 一…
  1.919  Projects/審查有沒有用記帳_計劃.md  [清單]
    12 [KEY]: KEY:題目=讓「審查到底有沒有用」變成機器數得出的帳(Enzo 2026-09-08 裁「開工」);不建評測系統,只開始記:兩個必填數字、一個駁回清單、一段讀側、逃逸當下就記;不…
    41 [fm:why_chosen]: why_chosen: 必帶+整字比對是最小的機械守衛;存活多於席位報的 S 由讀側算式 max(0,M+R−N) 推出,不需要人填第四個清單
    84 [body]: ### [S2] 載體列:「編排者重現不到」清單必帶、id 要對到 intake 的重現表列 [test:t_canary_refuted_set]
    117 [body]: - **「編排者重現不到」清單靠編排者誠實**:id 對 intake 重現表驗只證明「intake 那一列有這個 id 和 HIT/MISS」,不證明重現做對了——跟逃逸帳同一個…
    141 [body]: - **代碼審 code-review-yield r1(2026-09-09,standard:單reviewer-sonnet + 架構對齊-sonnet + 外家否決-cod…
    146 [body]: 自動數在四種真實報告格式上數到 0(三席各自實測)、報 8 存活 9 算術倒退、駁回清單可灌大、舊帳缺欄位只有「報」印 ?、選填等於沒填、resolved 不在值域、ci-wait…
    165 [body]: ②總結句只認行首(可帶標題、清單、引用、編號、粗體記號)——原本整行任何位置出現「最高/總結/整份」就當總結句,
  1.918  Projects/code-loop必用守衛_計劃.md  [清單]
    16 [KEY]: KEY:⚠現行(2026-07-06 ADR,見 decisions):Stop nag 已撤除(每回合刷屏太擾民)——守衛=pre-push 單點 blocking;hook 檔…
  1.916  Projects/design-loop折入守衛_計劃.md  [清單]
    21 [DECISION]: DECISION:閘是紀律非防篡改(同 design-loop 本身,lumos 擋不住不跑就 commit);跨段語意矛盾清單逼看不替判;啟發式有假陽假陰
    58 [body]: - **(A) `lumos fold-check <path>`**:機械輔助,出「折入後一致性複查清單 + flag」。value-drift/reverse-omission…
    82 [body]: 1. **跨段語意矛盾(mode 3)**:清單**逼你看**、不能**替你判**——仍需人/Claude 判斷。
  1.916  Verification/2026-09-05_skill-doctor成本基線.md  [清單]
    18 [body]: KEY:量法=`/skill-doctor`(2.1.261 起併進 /plugins 的 Stats 分頁);「context」=該 skill 在系統提示清單裡那一行的 tok…
    19 [body]: KEY:lumos 五支的掛載成本合計約 420 token/回合(code-loop ~90、design-loop ~110、project-notes ~90、core-kn…
  1.915  Projects/graph-engineering掃描2026-08-19_調研.md  [清單]
    71 [body]: 最小解形狀(未立案,待裁):`lumos gov` 加一段觸發統計(每閘筆數/涉及節點數/是否收斂),恆觀測不進閘;零觸發清單與高噪音清單即退場討論的素材。
    79 [body]: 前者的六條清單(角色/邊/失敗模式/交接協定/可觀測性/各管各的)我們五條有,唯一的洞在可觀測性。
    92 [body]: | 給事故→機制那組邊一個新具名欄位 | **新機制,過不了准入**:無事故支撐;且成本不是寫欄位那一次,是散落列舉稅(append 白名單、lint 值域、doctor E 家族…
    119 [body]: Enzo 追問「不只看 graph engineering 那份清單,以一般軟體流程看我們缺什麼」。兩個 session
  1.912  Verification/2026-08-07_連結缺失補全落地.md  [清單]
    33 [body]: B 群 3 筆+E20 全部出現在候選清單(檢索排序v1[both]/主動影響幅度偵測_計劃[both]/pitfalls事故觸發_計劃[neighbor-family]/conv…
    34 [body]: **補鏈本身=人裁待辦**(清單已產出交 Enzo;工具不寫檔)。
  1.901  Systems/lumos-deinit.md  [清單]
    16 [FLOW]: FLOW:pre-flight守衛(非git→rc2｜專案路徑不是UTF-8→rc2(嚴格解碼不猜路徑,2026-09-11 見 [[Issues/風險掃描遇到非UTF-8內容整支…
    32 [fm]: - content: 預設刪圖譜但置於三道安全網後(印清單+未commit警示、互動y確認、非tty無--yes則rc2拒刪)
  1.897  Projects/Codex完全支援_計劃.md  [清單]
    31 [fm]: - content: AGENTS 檔放同一塊 sentinel 紀律區塊(該層有 AGENTS.override.md 就寫 override,否則 AGENTS.md),插在檔…
    72 [body]: > 白話:現在 lumos 的「防護」全掛在 Claude Code 上——進 session 時有人提醒你去查圖譜、改檔前有人把相關合約推到眼前、派審查員時有人把清單附進派工詞、…
    84 [body]: | 1 指示 | `CLAUDE.md` 裡的 sentinel 紀律區塊(`scripts/templates/graph-discipline.md`,6.6k;`lumos …
    89 [body]: | 6 安裝/拆機/體檢 | `lumos install/uninstall/teardown/enforcement/doctor`;★`_sync_global_claude…
    109 [body]: 1. **skills**:`_install_skills` 目標從單一 `~/.claude/skills` 變成清單 `(~/.claude/skills, ~/.agent…
    111 [body]: 3. **AGENTS.md 區塊**:`_reinject_claude_block(root, slug, targets)`——目標清單=`[CLAUDE.md, AGENT…
    121 [body]: | impact-hook(PreToolUse) | `tool_input.file_path` | apply_patch 的 `tool_input.command` 是 …
    140 [body]: - **(a) AGENTS 檔放同一塊、不放指路;有 override 就寫 override;插檔首**:指路要模型多做一步、沒機械保證;`project_doc_fallba…
    … 還有 4 處
  1.894  Verification/2026-09-04_Codex完全支援S3量測驗收.md  [清單]
    36 [body]: - `--only s03-query-status`:通過,34.1 秒,3 個工具呼叫;第一動作讀 skill/CLAUDE.md/索引(不在禁止清單),第二動作 `pytho…
    42 [body]: - 子代理鏡頭「有沒有讀」(子代理稿沒有釘住清單可比,只數筆數)。
  1.889  Issues/prepush測試閘假紅-git環境洩漏.md  [清單]
    22 [body]: > ★檔名保留第一次（錯的）診斷用詞，刻意不改★——「git環境洩漏」是最初押錯的假說，真因見下方〈真因（第二次診斷）〉。留著檔名是為了讓「我曾經診斷錯」這件事在檔案清單上就看得到…
    31 [body]: hook 只印輸出尾段，看不到紅的是哪幾條；`/tmp/lumos-prepush-tests.log` 又會被套件裡「測試 pre-push hook 本身」的測試覆寫，所以第一…
    49 [body]: 拿到失敗清單才看得出來（hook 只印尾段，得直接讀 `/tmp/lumos-prepush-tests.log`）：
  1.862  Issues/2026-08-03_剝除與邊界解析的既有缺陷群.md  [清單]
    94 [body]: - **`cmd_lint:2230`** 用 `^\s*-\s` 數**所有**破折號行，把巢狀子清單當獨立決策 → 對合法節點誤報，
    95 [body]: 且訊息叫人「用 `decision-add` 重寫」，照做會**毀掉合法的巢狀清單**。
    153 [body]: | ⑥ | lint 把巢狀子清單當獨立決策 | 需要與 `parse_decisions`／`decisions_items` 三份實作一起收編（**又是同一個形狀**） |
  1.854  Verification/2026-07-31_slim-gen生成器落地.md  [清單]
    7 [fm]: - "精簡版保留指令清單固定為現行 24 支(DEFAULT_KEEP);root 集合演算法覆蓋 dispatch if 分支 + module-level 語句/class b…
    13 [fm]: - "scripts/lumos 的 subparser 註冊改用第四種形態(非 Assign/Expr/迴圈)→ collect_edits 需補對應 visit,否則移除清單漏…
    70 [body]: 1. **哨兵 W4 不成立**:`W4` 位於 `_link_or_copy`(`scripts/lumos:7238`),只被 `_install_skills` 呼叫,後者只…
  1.847  Verification/2026-08-24_固定席降噪A層落地.md  [清單]
    25 [body]: > 白話:改程式時 hook 推的「必看」清單,一半以上是掛著「守衛面」軟標記、跟誰都隔一跳的樞紐筆記。
    59 [body]: - 考卷 20 題量的;lane cap 3 若某題參考道 >3,被截的那幾條「人看不到但帳上在」的口徑差已用「同一份清單」設計消滅,但 cap 值本身只在 train 掃過。
  1.837  Projects/回訪掃描_計劃.md  [清單]
    11 [fm]: - content: v3 落地:E5 回訪掃描段(fail-closed 壞日期/最老優先/全靜默)+接電條款(daily doctor --ci)+nags 升級鏈整條測試證明…
    44 [body]: - ④**待裁型(「待裁觀察」不含;桶數以處置表為準):不預設日期——待裁清單=inventory.md 處置欄篩「待人拍日期」列(r2 delta 定落點),一次呈人,日期由人拍…
    53 [body]: - **提醒飽和(最大真隱患)**:52 件一次回填,到期若擠在同天=warn 段爆版。處置:①warn_soft 既有 cap3+--verbose ②回填時日期錯開(季掃分散到…
  1.834  Verification/2026-07-05_code-loop必用守衛.md  [清單]
    27 [body]: - **`scripts/test_lumos.py` 736 passed, 0 failed**(基線 634[pitfall-incidents merge 後]→ +102…
    33 [body]: 3. **Stop hook `code-loop-guard.py`**:每回合末 `code-loop check`,blocked → 注入 nag additionalCo…
  1.830  Verification/2026-09-11_每支檔有家落地.md  [清單]
    20 [body]: - **測試**：新增測試函式 54 支（其中 t_nodehome_* 42 支、健檢那組 t_doctor_nodehome_* 5 支；另有一支既有的清單一致性測試改名成 t…
    24 [body]: - **殺傷力**：51 種故意把程式改壞的寫法（先 19、再 6、4、6、13+2，最後推送前逐提交看那 1 種；照七份突變清單機械數）逐一跑對應測試，全部被抓到——第二輪有兩種…
  1.824  Verification/2026-08-25_probe輪退場與多席路由統一落地.md  [清單]
    6 [fm:revalidate_when]: revalidate_when: "下次改動 panel 抽查印行時,t_panel_probe_retired 的舊義務句斷言改為正向鎖新句字面(sha 硬幣紅證限制的回頭條件,…
    32 [body]: - carrier 收齊各席 findings 無機械對帳(帳面無逐席清單)——每案 intake 人工對帳+連兩案漏收升級,見 revalidate_when。
    45 [body]: - 對帳結論:**沒有漏收**。原本記的升級條件是「連兩案漏收就改在帳本加逐席清單欄」,這案沒漏,不觸發。
  1.809  Projects/iOS與Node後端補棧_計劃.md  [清單]
    34 [KEY]: KEY:[2026-09-08 六棧世界對照]Enzo 問「我們問的這些問題夠了嗎」→六棧各對一次世界清單(nodebestpractices 百條/OWASP Node/Appl…
  1.805  Projects/design-loop輕量檔_計劃.md  [清單]
    24 [KEY]: KEY:light 跑什麼(壓縮 loop)——pre-flight cascade(複用 M1 排乾清單型)+1 輪·1 通才審計員·canary 護·K=1(踩 [[Proje…
    80 [body]: - **pre-flight cascade**（複用 M1）排乾清單型缺陷。
  1.802  Projects/循序codeloop-tier錨定_計劃.md  [清單]
    16 [KEY]: KEY:修真清單含 skills/lumos-code-loop/SKILL.md 護欄 cap 數字與 _TIER_ROSTER 上方註解、loop status --roste…
    96 [body]: - **r1(2026-08-18,panel:3 sonnet(通才/守衛象限/整合)+Gemini Flash 外家席;收貨三道全過,外家 1 條短引句機械補長後全錨定)**:…
  1.801  Projects/canary注意力檢查失效.md  [清單]
    21 [KEY]: KEY:★三方互打(不只兩方)★——步驟 2.7 pre-flight 的掃描清單「未定義旗標／欄位／檔名、章節交叉引用」★與 canary 四型完全同一組★:pre-flight…
    28 [fm:PRIOR-ART]: PRIOR-ART:①最小解在既有機制層——改 `lumos-design-loop/templates.md` 的抑噪紀律措辭 ＋/或 canary 型別清單,不動任何碼、不造新…
  1.783  Issues/寫下風險當成處理風險.md  [清單]
    58 [body]: 那會製造一張永遠做不完的清單,反而讓真正該處理的沉底。**要的是判準。**
    67 [body]: | **B 可機械但未做型** | 存在便宜的檢查點——常數比對、欄位存在性、清單成員、計次 | **二擇一且必須當場選**:①開 Issue 進待辦帳 ②**把散文降級**(「須…
  1.781  Verification/2026-09-09_兩席相反時端出張力實作測試.md  [清單]
    47 [body]: - [S1] `t_dispositions_tension_validate`：12 種壞形狀（缺 chosen、chosen 大寫、existing 缺／空／非清單／21 項／…
    48 [body]: - [S2] `t_codeloop_check_tension_warns`：existing 指不存在的檔 → BLOCKED 帶 id 與欄名；marker 被改成空清單 →…
  1.778  Verification/2026-08-19_精簡版update指令落地.md  [清單]
    31 [body]: - `slim/update_cmd.py`(生成期模板,不隨包)+`scripts/slim-gen.py` 拼接(main() 前置攔截+函式;先於 ast.parse;錨點唯…
    46 [body]: 1 minor 折入:pull 首行修復補翻紅釘斷言(behavior②b)。r3 席並實證:截尾對 --ff-only 分岔情境正確、對「本地改動清單超長」型各有取捨(infor…
  1.775  Projects/Codex行為精修_計劃.md  [清單]
    57 [body]: - F1 版本表=外家 #1 同題(已在任務清單:`CODEX_TRANSCRIPT_VERSIONS` 加 0.153.2,測試驗表裡有它)。
    59 [body]: - F3 reason 會變成 Codex 下一個 user prompt,檔名是攻擊面:reason 裡的每個路徑經 `_safe_path`——去掉控制字元與換行、只留可印字元…
    63 [body]: - F8 「payload 缺 session_id」已在單元測試清單(驗收 1 第⑦條)。
    90 [body]: - 權限/安全:reason 只含既有提醒文字+檔名清單(repo 內相對路徑),不含圖譜自由文字;檔名與筆記名一律經 `_safe_path` 消毒(去控制字元/換行、單一路徑截…
    120 [body]: - **shebang 檢查順序(整合 major)**:先判 repo 內、排除清單,再開檔;非一般檔(FIFO/目錄/socket)不開。
  1.775  Projects/loop數據收集_計劃.md  [清單]
    41 [fm]: - content: 換尺可比切片 r1 五席全票縮案+r2 收斂落地(原名三數字防刷,K-1 正名):B(使用率 held 池)死=判死指標換裝復活繞 d2 重開閘(★圖譜攔截★…
    70 [body]: - **獨立實驗**：replay 校準。✅ **baseline v0 已跑（2026-07-16,[[Verification/2026-07-16_replay校準basel…
    132 [body]: - 釘死三帳檔名/記號的**允許引用點清單**(r1 機械席實測枚舉+r2 delta 補類):簿記白名單常數、escape 讀寫實作與測試、skill/圖譜文件、本計劃、**審查…
    140 [body]: - 造假防禦明文不做(K-1):自主迴圈在自己文字裡植記號這型,rev 治不了;唯一防線=攔截/逃逸都是人讀季看+放行點有人(自主迴圈裁定「抽掉人之前必辦清單」既有),出現造假跡象…
  1.775  Systems/reversibility-governance-ledger.md  [清單]
    29 [KEY]: KEY:gov 彙整多本帳(6 源 <!--lumos:count=6 re=(?m)^\s+load\((?:\"\.|CI_LOG_NAME) in=scripts/lumos…
  1.770  Projects/主動影響幅度偵測_實作計畫.md  [清單]
    35 [body]: **Architecture:** `lumos impact --file <code> --json --repo <root>` 純記憶體即時算「直接(body inline…
    82 [body]: - Produces: `_impact_reverse_lookup(rel_code_path, env, repo_root) -> list[node_rel]`(body…
    186 [body]: - [ ] **Step 1: 失敗測試** — 直接節點有 `core_refs: core-knowledge/systems/rule` → 影響清單含該葉、標 `cross…
  1.764  Projects/一句話層供糧_計劃.md  [清單]
    18 [body]: PRIOR-ART: **借用三源,不建第二種**——①外部:OpenViking(34.8k★)三層記憶(L0 一句/L1 概覽/L2 全文,實測省 34-91% 輸入 toke…
    23 [body]: - **開迴圈的相關節點清單**(入口栓 A=`loop next` 首輪印「主題既有節點」的 advisory,[[Projects/圖譜進迴圈入口栓_計劃]]):印「名+sta…
    37 [body]: - 入口栓 A 清單:每行「名 [status] 決策 N 條[ ★近名]」**最末**加「 — <L0>」(A-1 釘序:gist 恆最後;空則整段不加);--json 的 `r…
  1.762  Systems/linter精選目錄.md  [清單]
    16 [KEY]: KEY:各語言精選 linter 參考目錄(2026-07 社群現況搜證)——供各專案 setup 時挑要裝的 linter;裝了才進該專案 .lumos/lint.json(跑 …
    36 [body]: > **定位**:這是「各專案該裝哪些 linter」的參考菜單(跨專案共用),不是「某專案已裝什麼」的清單。專案 setup 時從此挑對應語言的 linter → 裝進專案 → …
  1.755  Issues/lint-watch空轉假綠.md  [清單]
    47 [body]: - [ ] Citrus_KDS 掛 `.lumos/lint-watch.json`(有 lint.json/detekt 卻沒掛 watch)並加進 REPOS 清單
    59 [body]: - 每日掃描:宣告 0 條時改印「★宣告 0 條:這個 repo 沒有任何 linter 在被盯,每天這一趟是空轉★」+ 三步下一步(先確認有沒有裝 linter → 加進 wat…
  1.754  Projects/派工編制資料化_計劃.md  [清單]
    22 [body]: > 白話:每輪對抗審計「該派哪些席」——幾席、什麼鏡頭、哪席要外家、對答案席什麼條件開——目前全住在 skill 散文裡,只有「實際派了誰」有落資料(rN-dispatch*.js…
    40 [body]: 以 (loop_kind, tier) 為鍵;loop_kind 由 loop id 前綴判**三值**(r1 外家席抓到二值規則會對歷史 id 載錯表噴無意義警告,升級為機械跳過…
    62 [body]: ### S2 `loop next` 吐應派清單
    64 [body]: - JSON 輸出加 `roster` 欄:該 (kind,tier) 的席清單(slot/family/occupies_w/requirement 原樣)。
  1.752  Verification/2026-09-11_skills健檢.md  [清單]
    16 [body]: > 白話:Enzo 2026-09-11 說「全部的 skills 都幫我健檢一次」。這台機器上 Claude 看得到的 skill 共 29 支:這個 repo 自己的 10 支…
    33 [body]: | kotlin / csharp / vue / node / swift-idioms | 7.5–12.4KB | Skill 工具 0 次(由 pitfalls 與派工詞指…
  1.740  Projects/design-loop重設計_實作計畫.md  [清單]
    112 [body]: - 輸入：凍結語料目錄＋植入清單（JSON：檔、位置、型別、token）＋各配置的審查報告目錄。
    131 [body]: 代打 rc2；修法＝把理由給齊，讓目標檢查成為**唯一能翻紅的路**（斷言重疊型，T8 併入假綠清單）。★
    154 [body]: 假綠清單併入「斷言重疊型」（翻紅釘第二盲區，T1 教訓）；②Verification T1-T7 已 pass；
  1.715  Projects/主session鏡頭利用率_計劃.md  [清單]
    49 [body]: PRIOR-ART: ① 最小解層級——推送方 `impact-hook.py`(PreToolUse Edit|Write)、逐字稿(Claude Code 每行帶 UTC 時戳…
    63 [body]: - **推送事件** P:逐字稿裡 `attachment.type == hook_additional_context` ★且 `hookName ∈ {PreToolUse:…
    78 [body]: r2 量測效度席把 r1 版的演算法拿歷史逐字稿乾跑,發現★推送本來就寫在逐字稿裡★:每次 impact-hook 注入,逐字稿多一行 `attachment.type == ho…
    103 [body]: ## 同步清單(r2 縮減後)
  1.711  Projects/design-loop提效_計劃.md  [清單]
    39 [body]: fromscratch-m1 三輪 9→6→3、T3 三輪 12→6→5——常態跑滿 cap 靠人裁實質收斂。拆 findings 性質：r1 大宗是清單型缺陷（未定義詞/矛盾/t…
    58 [body]: 3. **pre-flight cascade**：panel 前一道機械 checklist（未定義旗標/欄位/檔名、交叉引用、範圍自違、CLI touchpoint、測試策略對…
    106 [body]: - `lumos canary record ... --clusters "名=狀態,名=狀態,..."`：該輪存活 findings 經編排者**按根因合併**後的 risk-…
    131 [body]: **pre-flight（2026-07-16,M1 新步驟 2.7 首戰）**:panel 前便宜 agent 排乾 4 條清單型——①cmd_canary_record 函式名…
    141 [body]: **r2（2026-07-16,panel delta-scoped 首戰:3 sonnet+Codex;a/b 席 framing 加碼）**:canary a✓(孤兒治理帳檔—…
  1.710  Projects/spec合規slot_計劃.md  [清單]
    23 [body]: - lumos-code-loop SKILL.md panel 節：tier=high 且該分支**有收斂 spec**（計劃節點）時，panel 追加一個 **spec-con…
  1.707  Verification/2026-08-01_slim-ps1早期分支exit修復.md  [清單]
    50 [body]: - 圖譜同步:[[Systems/slim-install-安裝器]]、[[Systems/slim-uninstall-一行卸載]]、[[Systems/slim-get-一行安…
    55 [body]: - `shutil.which()` 對真實 Windows PATH 解析行為、`.cmd` shim 在真實 `cmd.exe`/PowerShell 下能不能被正確找到並執行…
  1.704  Verification/2026-07-29_CI回流閉環v1落地.md  [清單]
    60 [body]: **通則入帳**：凡文件宣稱一個「可從碼機械推導的清單或數字」，就該有一條這樣的測試——否則它遲早漂移，而且是靠人發現。
    82 [body]: - 掃描對象由手維護的三檔清單改為**全部活文件**（排除外審歸檔與 `governance/golden/` 這兩類不得回改的歷史）。
  1.699  Projects/席位人格化_計劃.md  [清單]
    30 [body]: - 2026-08-28 d6 把正確性鏡頭從名詞清單升成「問句+例子+明講排除」,那是這條路的第一步,本案是第二步。
    44 [body]: 每席派工詞從「鏡頭清單」加上三件:①**立場**(例:簡單的守護者、複雜的敵人)②**預設姿態**(例:預設駁回,只有具體證據才讓步)③**該席專屬的攻擊問句**。範本=既有架構對…
  1.698  Projects/design-loop重設計.md  [清單]
    89 [body]: | 3 pre-flight | 清單掃描 | 有效，但掃的類別與 canary 同組（三方互打） |
    173 [body]: - **settle（結清式收斂）**：★它幾乎就是「只留可重算的」的既有樣板★（清單全結清∧G1∧G3，
    196 [body]: ### r1 · pre-flight（機械清單，全文餵便宜模型；不算 loop findings）
    214 [body]: fold-check 補回閘清單；settle/light 去向交代；拆包改相容雙讀；PRIOR-ART 四處引用強度校正
  1.695  Verification/2026-07-28_中心性重驗排程.md  [清單]
    11 [fm]: - "cmd_stale 候選母體或 Check S 清單結構改動"
    29 [body]: - [S3]：Check S 兩清單各自 PR 降冪（hub 排前斷言）；gov 寫入序不動（重排僅顯示層）。
  1.686  Projects/impact鏡頭機械化_計劃.md  [清單]
    48 [body]: 「派 reviewer 前跑 `lumos impact --diff` 附波及清單」這條規矩幾乎沒人照做,想把它機械化——**兩輪設計審、十席次,證明工具層沒有可用的機械強制點*…
    72 [body]: - **截斷把被消滅的步驟裝回來**:固定席實測 20~26 篇、**無一低於 8**,截斷後要拿完整清單仍須跑那道指令——正是 v2 宣稱已消滅的那道。
  1.672  Projects/Codex外審吸收_計劃.md  [清單]
    19 [DECISION]: DECISION:[2026-07-29]緩辦不採清單——單檔拆模組(P1):方向對但大手術,anchor/測試/vendor 全連動,單人維護期回報<風險,等第二維護者;tier…
  1.671  Verification/2026-07-15_主網M2_typed-edge索引.md  [清單]
    26 [body]: - **`build_typed_index(env)`**（新，`TYPED_EDGE_FIELDS=(verified_by, plan_refs, related)`）：回 …
  1.670  Projects/skills提示工程優化_計劃.md  [清單]
    34 [body]: - 搬之前先把兩支入口頁逐句拆出規則句清單,搬完逐句確認在入口頁或參考檔找得到(清單留在卷證)。
  1.669  Verification/2026-08-20_gov-stats落地.md  [清單]
    16 [body]: > 白話:`lumos gov --stats` 落地——每道閘幾筆、涉及幾個節點/commit、第一次跟最後一次是什麼時候,外加一份「本帳裡完全沒出現過的閘」清單。★純數字,不貼…
  1.662  Projects/條款認領追溯_計劃.md  [清單]
    30 [body]: - **指令** `lumos spec-trace <計劃節點> [--json]`（vault 內、唯讀）：列每條 ID 的認領狀態；輸出未認領清單。rc：全認領=0；有未認領…
  1.661  Verification/2026-08-21_doctor-run事件落地.md  [清單]
    30 [body]: `_scaffold_project` 自 2026-06-26 把帳檔 ignore 清單寫在 `docs/<slug>-knowledge/.gitignore`,但帳檔全部落…
  1.654  Verification/2026-07-21_loop機械脊椎M1包.md  [清單]
    29 [body]: - 同步（同 commit）：SKILL.md 三處（loop next 進場/record 時序/light 機械 gate）＋templates.md（雙 hash 模板）＋c…
  1.653  Verification/2026-08-26_roster對帳併入問閘落地.md  [清單]
    21 [body]: - **[S1]/[S1b]**:t_disposal_roster_tail 四斷言——異常輪印轉述行、留痕檔落一行、摘要/診斷抑制、__seqN 零輸出;真機冒煙:lint-w…
  1.652  Projects/關係層主網_實作計畫.md  [清單]
    53 [body]: | **M4** | 觸發 + typed hop-1 + 判斷閘連鎖 | supersede 觸發 → typed hop-1 列鄰居 → AI 判斷閘 → 確認才前進的工作清單…
    91 [body]: - **同名無路徑 `[[X]]` 有多篇候選 → 記 ambiguous + 候選清單、flag；消費端浮出歧義，嚴禁靜默指第一篇**。
    92 [body]: - 去重鍵 `(source, target, type)`（ambiguous 條目的 `target`＝原 wikilink 字面字串——同 ghost 處理法；補一條測試釘此…
    131 [body]: - **[S4] 連鎖＝確認才前進的工作清單**：只有判「真傳播」的鄰居進清單、展下一跳（**同一內部 typed hop-1 原語**，編排者進程內呼叫，不 shell-out …
  1.649  Projects/驗證層去模型化_計劃.md  [清單]
    61 [body]: - 輸出:殺率+活口清單(survived 桶,file:line+變異描述)+各桶計數;**rc 合約修正(r1 折入,Codex)**:rc0=觀測有效(不論殺率);**基礎設…
    79 [body]: ## 合約候選清單(收斂提名,候選≠已標)
    104 [body]: - S4:`t_mutate_diff`(三算子生成/worktree 隔離/testmap 選測/殺與活判定/cap 抽樣/無測試檔如實列/rc 合約);對本週真實 diff(h…
  1.649  Verification/2026-08-01_slim-windows兩缺陷修復.md  [清單]
    61 [body]: **★誠實限制,不包裝成已解決★**:這台機器沒有 PowerShell,無法驗證這段語意——推理上這個改法不會再主動關掉呼叫端視窗,但 `exit` 在 PowerShell 各…
    79 [body]: - `.cmd` shim 在真實 `cmd.exe`/PowerShell 下能不能被正確找到並執行——與既有的 Windows 未驗清單相同,未擴大也未縮小。
  1.647  Verification/2026-09-02_探針沙盒全域防護.md  [清單]
    23 [body]: - **第二道:事後健康檢查** `global_skills_health()`——修復後回傳空清單(健康);事故當下會列出八個懸空連結。判準=symlink 跟隨後不存在,或 …
  1.647  Issues/git-hooks路徑指向樹內_checkout即執行分支碼.md  [清單]
    30 [body]: - 錨點([[Systems/anchor-integrity]])只擋「改了錨點檔還想 push」,不擋「checkout 別人已經 push 上來的分支」;而且只錨既有那幾支,…
  1.636  Verification/2026-08-12_CheckN_可重算數字宣稱.md  [清單]
    54 [body]: 2026-06-10 的首輪交叉審計**已經把這條寫成教訓**——「計數/清單型主張最會漂」。
  1.632  Verification/2026-08-18_派工編制資料化落地.md  [清單]
    21 [body]: > 白話:對抗審計「每輪該派哪些席」從 skill 散文變成 code 資料表,`loop next` 吐應派清單、`loop status --roster` 對實派派工快照做觀…
  1.627  Projects/oracle品質包_計劃.md  [清單]
    93 [body]: - **r2 panel**（2026-07-29，delta 3 席 sonnet＋Codex 否決；**三席 canary 全中（二連）**；存活全機械證實免辯方）：[majo…
    99 [body]: ## 合約候選清單（設計端提名，落地時 guard bind 蓋章——合約鏡頭首次 dogfood）
    108 [body]: - 歸因啟發式對「測試名出現在非失敗上下文」（如 runner 列印執行清單）可能誤歸因 → 判準要求名字＋失敗標記**鄰近共現**（5 行窗），仍非零誤判，明標弱證據帳分開統計。
  1.613  Projects/標籤結構收編_計劃.md  [清單]
    32 [body]: 四件內容與回填清單見 summary；驗證見 plan_refs 回指的 Verification。
  1.604  Projects/Android側UI測試綁圖譜工作流_計劃.md  [清單]
    29 [KEY]: KEY:★天花板(先寫明,免得被當成全覆蓋)★—①UI flow 對「畫面長怎樣」敏感,版面一改就要重錄 ②只驗走得到的路徑,取不到裝置仍是「明記未驗+原因」不得靜默跳過 ③不取代…
    265 [body]: - **第一缺口「時機」v1 沒關上**（r1-F6）：待辦全是設定／散文／清單／prompt，沒有一條動到「功能完成當下」這個觸發點；既有軟提醒實作只掛 pre-push。★這是…
    290 [body]: ## 合約候選清單（收斂時提名；★候選 ≠ 已標★，蓋章仍走 guard scaffold→bind→audit 與「不確定不標」鐵則）
    307 [body]: - [ ] 「裝置 ready」的可檢查前置清單（各專案自填，如 `.maestro/README.md`）
  1.593  Projects/消費專案接入靜默失效_計劃.md  [清單]
    95 [body]: - [S6] `lumos init` 建立排除標記目錄的忽略設定；治理帳不在初始化的忽略清單；既有專案的忽略設定不被覆寫 [test:t_init_gitignore_match…
    97 [body]: - [S9] **猜技術棧的對照表必須反查自既有的兩張正典表**（測試 profile 的副檔名、符號 profile 的程式碼副檔名），不得另開第三份手寫清單；正典沒認領的欄位留…
    112 [body]: - **反查表「猜得弱」的那一側（r2 f4）**：`.vue`／`.sql`／`.ps1` 只是碰巧被 C# 那份副檔名清單收了（意思是「C# 店裡也會有的檔」，不是「這是 C#…
    154 [body]: 這三個不是設定錯，是**掃描的取材範圍錯**——同一類問題還可能藏在其他吃 diff 或吃檔案清單的地方。
  1.589  Verification/2026-07-05_design-loop折入守衛.md  [清單]
    44 [body]: 跨段語意矛盾清單逼看不替判;啟發式有假陽假陰(自指 meta-spec、`fold-check +` 怪值);閘是紀律非防篡改(lumos 擋不住不跑就 commit)。
  1.585  Systems/節點還原.md  [清單]
    30 [body]: ## 交付清單(2026-08-24 落地)
  1.584  Projects/中文無空白查詢回退_計劃.md  [清單]
    72 [body]: - **(乙,採用) 只在搜尋函式現有的預檢與主迴圈裡擴充那份詞清單。**
    79 [body]: ——只列「要處理哪些情況」是不夠的,照著清單重寫一份 regex 一樣能滿足每一條、
    320 [body]: 要變預設之前,得先列出可執行的呼叫端清單、逐一釘上關閉旗標,並加測試防未來漏接。
    321 [body]: REVISIT:2026-11-14 若要把預設改成開,先做那份清單;沒做完不准改預設。
  1.582  Verification/2026-08-27_自主loop遷處置閘.md  [清單]
    5 [fm:valid_under]: valid_under: "orchestrator-prompt step-6 記處置帳(record none + findings-set/folded/accepted/a…
    29 [body]: - `governance/autonomous_loop/orchestrator-prompt.md`:step-4.5 辯方三選一(agree/evidence/concer…
  1.582  Projects/標註刷新_實作計畫.md  [清單]
    72 [body]: **Interfaces:** Produces:`repin [--goldset G] [--repo R] [--target SHA]`(target 預設=repo HE…
  1.581  Verification/2026-09-05_Codex行為精修f02後測.md  [清單]
    22 [body]: KEY:hook_trace:第一版 hooks_fired=3 是把「developer 訊息含 lumos」都算進去(含 Codex 自己的 skills 清單,代碼審 r1 …
  1.569  Projects/每日治理wrapper活著沒_計劃.md  [清單]
    185 [body]: - **鎖會不會把人鎖在外面**:60 分鐘接管那條是抄來的既有做法。本案的鎖目錄要真的進忽略清單。
    186 [body]: ★訂正一條我自己寫錯的診斷★:第一版我寫「來源那支的鎖目錄沒有被現有忽略清單涵蓋」——
    187 [body]: **那是錯的**。實測建立那個目錄再查,它命中忽略清單第 15 行的規則;而且追 git 歷史,
    191 [body]: - **這支腳本是本 repo 專用的**:安裝器的清單裡沒有它,不隨工具鏈分發。
    375 [body]: 工具鏈的安裝器不分發這支(清單裡沒有),換一台機器要重跑。
  1.567  Issues/只退場不痛的機制.md  [清單]
    27 [body]: > 拆了 L3(寫帳 hook 已撤的假名額);零觸發 8 道逐道裁;kill 在本 repo 跑通第一條配方。**實證**:gov --stats 未出現清單從 8 道降到 6 …
  1.563  Verification/2026-08-01_slim-終審三缺陷修復.md  [清單]
    57 [★INVARIANT★]: - 圖譜同步:[[Systems/slim-install-安裝器]]、[[Systems/slim-uninstall-一行卸載]]、[[Systems/slim-get-一行安…
    62 [body]: - ②的 Python 邏輯已用 `LUMOS_SLIM_SIMULATE_WINDOWS=1` + git-stash 因果驗證(紅→綠,非稻草人),但 `shutil.whic…
  1.548  Verification/2026-09-03_席間覆蓋率離線量測.md  [清單]
    73 [body]: - 對照全帳:222 筆帶處置清單的紀錄,發現 **1941** 條、附理由放行 **21** 條=**1.1%**——這套流程幾乎不判誤報。
    86 [body]: - 現在知道那份清單漏掉多少了:**以單席視角看,漏掉同儕找到的 64.6%**。
  1.538  Projects/評測尺翻案_計劃.md  [清單]
    83 [body]: - 未標判定唯一來源=collect_unjudged——另寫一套就是三方集合漂移(condensed 剔除域/coverage 分母/補標清單各講各話)。
    90 [body]: - [S1]:fixture 換能示範差異的例——排名 [未標,未標,判2,判1] 取 @2:舊尺 [0,0]→P@2=0.0,condensed [判2,判1]→P@2=1.0(…
  1.535  Verification/2026-09-09_審查有沒有用記帳落地.md  [清單]
    22 [body]: > 白話:這篇證明「審查有沒有用」的四段(拒收+機器數、必帶駁回清單、讀側漏斗、skill 同步)在我自己造的報告和假帳上照設計動,而且 r3 那五份真報告記得進去。它**不**證…
  1.533  Verification/2026-08-11_T1_remove_list項移除.md  [清單]
    39 [body]: | **不命中一律 rc=2** | ★最重要★。打錯字卻回成功＝呼叫端以為清乾淨了（死背書照舊掛著），比報錯危險得多。錯誤訊息附現有項清單供對照 |
  1.528  Projects/提交推送規範_計劃.md  [清單]
    30 [body]: `governance/replay/<編號>/verdict.json` 不在帳本豁免清單裡,只能推完再補一個提交。
  1.524  Verification/2026-06-26_native-windows-support_真機.md  [清單]
    16 [fm]: - "新增 Windows CI(屆時手動清單可降為輔助)"
    33 [body]: - r3(sonnet,major):mklink /J 對個別檔必失敗(.py 該 copy)、command 格式變後去重失效會雙註冊、測試/手動清單 stale「5 夾」。
  1.523  Projects/code側刪除傳播守衛_計劃.md  [清單]
    131 [body]: **兩檔信心——「這行被刪」≠「這個符號從 repo 消失」**：call site 被移除但函式還活著、還被別處用，這時圖譜講它未必過期；反過來只認「repo 全域消失的符號」精…
    264 [body]: - **r2（2026-08-10，delta 輪 3 席：sonnet 新證據正確性／sonnet 折入一致性／opus 邊界整合〔Codex auth 401 缺席退位，偏離記…
    265 [body]: - **實作偏離（2026-08-11，終審裁定）**：v1 排除域＝7 目錄＋lock 三檔名（對齊 should_exclude 子集）；vendored 白名單與源 repo…
    340 [body]: ## 合約候選清單（design-loop 收斂鏡頭提名；★候選 ≠ 已標★，蓋章仍走 guard scaffold→bind→audit 與「不確定不標」鐵則）
  1.522  Verification/2026-09-04_Codex完全支援S1hook適配驗收.md  [清單]
    28 [★INVARIANT★]: 2. **arm → SubagentStart 領席**:`lumos dispatch-lens --arm Lumos/main..HEAD --seats 1 --repo…
  1.521  Projects/迴圈摩擦三修_計劃.md  [清單]
    30 [body]: - **d2 前掃驗語意(治②)**:首輪前掃固定清單加第四類「spec 每句機械宣稱,開檔讀該段碼驗語意,不只驗存在」。**分流(r1 ext 席條 7:語意修正不得繞審計)**…
  1.516  Projects/design-loop判準重定位.md  [清單]
    288 [body]: ## 十一、合約候選清單（收斂時再逐條裁，候選 ≠ 已標）
    317 [body]: ### r1 · pre-flight（機械清單掃描，不算 loop findings）
    327 [body]: 屬清單型缺陷。設計層的洞留給 panel。
    453 [body]: - **fold 迷你核對**被本文稱為「唯一後手」，卻沒進收斂條件、也沒進合約候選清單。
  1.514  Projects/檢索PPR邊權_計劃.md  [清單]
    31 [body]: - [S1] **PPR 啟用**：`_graph_pagerank(env, personalization={seed: 1.0})`——teleport 改種子向量（dang…
    57 [body]: - r2-std panel（2026-07-28，canary=`seed_hits` 欄／`heldout-report.md` 產物／A3「半權重複跑」假程序：s1/s3 c…
  1.506  Verification/2026-08-03_Windows真機三輪驗證通過.md  [清單]
    53 [body]: | `~/.claude/skills/` 會掃描 `.bak` 目錄 | 要真的開一次 session 才看得到 skill 清單 |
  1.495  Projects/probe輪退場_計劃.md  [清單]
    59 [body]: 2. [S2] scripts/lumos 三件:①4019/4122 兩處印行整句改寫(c2 措辭;「要——加開一輪…」句刪除);②**panel 閘新迴圈 cutoff 拒判*…
  1.490  Projects/節點範圍與索引守衛_計劃.md  [清單]
    39 [body]: - ★r1 架構席★：既有八道提醒型檢查全部走同一支 helper，而截斷是刻意設計的——先前體檢發現軟段一次印幾十行會把警告淹掉、整天沒人讀過一條，才訂出「預設印幾條、要全部另外…
  1.466  Verification/2026-07-31_slim-claude-md第三次裁定取代與備份還原.md  [清單]
    35 [body]: `scripts/slim-gen.py` 組包清單加入 `claude-block.md`(吸取上一輪漏 `get.sh`/`uninstall.sh` 的教訓,新增檔案當下就同…
  1.464  Projects/版本發布流程_計劃.md  [清單]
    81 [body]: - **不重抄步驟**（r1 折入，本 repo 有清單漂移前科）：把 `ci.yml` 的驗證步驟抽成 **reusable workflow**（`workflow_call`…
    131 [body]: | [S4] | tag workflow 的版本斷言邏輯（fixture 驗，不真推 tag）＋ 兩份 workflow 不得各自維護步驟清單 | 單元＋機械守衛 |
  1.458  Verification/2026-08-25_迴圈摩擦兩修落地.md  [清單]
    45 [body]: **改成機械擋,不再靠紀律**:把處置閘那道檢查往前挪到寫帳之前。帶處置清單的那一席(等於宣告自己是全輪載體)如果有引句錨不回快照,`canary record` 當場擋下並指路。…
  1.432  Projects/code側刪除傳播守衛_實作計畫.md  [清單]
    60 [body]: - [x] Step 1 寫失敗測試（加進 test_lumos.py，新函式 `t_delguard()` 起手；並把 `t_delguard` 註冊進檔尾的測試清單——先 gr…
  1.432  Projects/接手視圖_計劃.md  [清單]
    83 [body]: - 代碼審 r3(2026-09-07,外家 Codex 驗收輪,只驗 #5):席位判「同信任域與不動 hook 的範圍刀可以接受」,但探針有兩個可重現繞過——#6 `os.ope…
    90 [body]: - **改了四處**:規則表的源頭 `scripts/templates/graph-discipline.md`(注入每個專案的 CLAUDE.md)、本 repo 的 `CLA…
  1.426  Projects/enforcement可觀測性_計劃.md  [清單]
    34 [body]: ## 為什麼(每一條都是我自己量過的,不是抄清單)
    151 [body]: - **測試層次從清單移除**——它不是閘。
    238 [body]: 連續喊 N 天沒人理」的空轉清單,結果餵進自主迴圈週報。
  1.421  Verification/2026-08-21_L4交叉審計30節點清帳.md  [清單]
    75 [body]: `t_` 命令數守衛掃全 repo `*.md` 比對「N 個頂層命令」與 argparse,掃到 `governance/l4-audit/` 的 verify 檔(引用歷史快照…
  1.411  Verification/2026-07-11_檢索goldset評測.md  [清單]
    58 [body]: 1. **nDCG IDCG 自證偏差(s4 major)**:原版 IDCG 用「系統取回清單」自排序當理想基準——漏檢索零懲罰,legacy 與 ranked 不在同一把尺。修…
  1.409  Projects/doctor-run事件_計劃.md  [清單]
    68 [body]: 併發——append 同既有路徑。效能——每次 --ci 多一行。資源——既有 with-open。風險類:self-governance——不擋任何東西,無誤擋;★反向:多一種事…
  1.406  Projects/全盤外審2026-07_調研.md  [清單]
    35 [body]: - **Codex 席**：`gpt-5.6-sol` + `model_reasoning_effort=high`、read-only sandbox、實讀 repo（CLAU…
  1.405  Projects/檢索優化_計劃.md  [清單]
    308 [body]: - pooling（r2 操作化）：`retrieval_eval.py --build-pool` 對四個系統（**legacy 現行順序 / ranked-BM25-only …
    341 [body]: - **階段二（2026-07-10）✅**：`_reco_adj/_reco_scores/_reco_fused`（BFS-decay 1/2^k+共引同行×2 飽和+Jacc…
  1.397  Verification/2026-08-01_slim-python移植.md  [清單]
    5 [fm:valid_under]: valid_under: "分支 main;slim/install.py + slim/uninstall.py 現行版本(IS_WIN = os.name==\"nt\" or…
    6 [fm:revalidate_when]: revalidate_when: "改動 install.py/uninstall.py 的 IS_WIN 分支(_install_cli 的 shim 產生邏輯、PATH 提示訊…
    55 [body]: - `scripts/slim-gen.py` 組包清單機械鎖(`t_slim_gen_dist_ships_entrypoints`)含全部新檔(`install.py`/`un…
  1.396  Projects/進度從提交推導_計劃.md  [清單]
    54 [fm:context]: context: 三選項:沿用 50 群那套 #N(只存在於那一份清單)、每份計劃自己給 T1..Tn(跨計劃撞名)、計劃節點名+任務號
    136 [body]: | 一篇 `status: done` 的實作計畫,裡面的勾選框 | **60 個框,0 個打勾**(12 任務 × 5 步驟,全是實作步驟不是驗收清單) |
    138 [body]: | [[Projects/全repo審視_計劃]] 的 50 群主清單 | **沒有「做完沒」這一欄**;進度靠翻提交訊息回推 |
    139 [body]: | 近 120 筆提交帶項目編號的 | **6 筆**(而且全部集中在那份有編號的主清單上) |
  1.365  Verification/2026-07-09_loop三輪壓縮.md  [清單]
    54 [body]: - **踩雷 + 已硬化**:`cmd_loop_capture_counts` 原用 `for f in (finders or [])`,撞 `t_hook_copy_list…
  1.364  Projects/code席爆炸半徑供糧_計劃.md  [清單]
    18 [body]: PRIOR-ART: **借用既有計算與掛點,不建新指令**——爆炸半徑的計算已存在(`impact --diff` 波及清單、`pitfalls --diff` 的必看節點);席…
  1.347  Systems/slim-uninstall-一行卸載.md  [清單]
    24 [KEY]: KEY:★絕不碰★清單(功能範圍外,不是「忘了做」)——任何專案目錄/repo、`~/.claude/settings.json`、`~/.claude/hooks/`、除了 `l…
  1.330  Verification/2026-08-22_成本欄接上與撤除兩階段.md  [清單]
    24 [body]: **起點**:外界「graph engineering」編組那派的六條清單裡,我們唯一缺可觀測性(耗時/token 成本)。
  1.320  Issues/連鎖佇列開了沒人跟完.md  [清單]
    78 [body]: - **② 世界解過沒（真搜）**：學術界的撤稿傳播是同一題且量測充分——撤稿後仍被引用是常態，**撤稿後的引用只有 5.4% 承認撤稿**；且傳播**主要靠直接引用**而非間接（…
  1.319  Projects/子代理續談調研.md  [清單]
    33 [body]: Claude Code 新增「子代理續談」：派出去的子代理完成後，其對話脈絡（讀過的檔案、推理過程）保留在本機紀錄檔，同一 session 內可用 SendMessage（帶 ag…
  1.298  Issues/風險掃描遇到非UTF-8內容整支中斷.md  [清單]
    59 [body]: (git 字樣只在呼叫端),所以寧可多抓;只放過命令清單開頭明確是別的程式的。
  1.284  Projects/from-scratch重生守衛_計劃.md  [清單]
    30 [fm:context]: context: 三輪軌跡:r1 2/3 caught 存活 9(blocker 範圍矛盾)→r2 3/3 存活 6(major 接線)→r3 3/3 全精準 存活 3(測試枚舉,…
    68 [body]: 4. **殘餘 Tier-C 轉問題問人——走 signoff**。目擊者還在＝問不是推。重生吐**問題清單**（Tier-C conjecture）路由給人確認。＝「重生即結構化…
    150 [body]: **r2（2026-07-16,panel v2 delta 審:3 sonnet+Codex 否決席+A 席 framing 加碼）**:canary **3/3 caught、…
  1.284  Systems/slim-install-安裝器.md  [清單]
    29 [DEP]: DEP:scripts/test_lumos.py t_slim_install_no_project_touch｜t_slim_install_claude_md_idempot…
  1.279  Projects/loop機械脊椎M1包_計劃.md  [清單]
    102 [body]: 4. `Systems/loop-convergence-recording`：record 選用鍵計數與清單（+`reviewed_sha256`/`result_sha256`…
  1.279  Projects/已知坑策展庫_計劃.md  [清單]
    27 [body]: - **perf 誠實(r1 勘誤)**:print 路徑建 vault ~4.7s(一次性、design 時給人讀、非熱路徑,可接受);--check 保持 0.18s vaul…
  1.261  Verification/2026-07-31_公開精簡版交付.md  [清單]
    38 [body]: `/install.sh` 裡 `install` 前面是 `/`、後面是 `.sh` 的 `.`,兩者都不在排除清單裡,誤判成裸散文引用。
  1.258  Projects/Codex工作流整合_調研.md  [清單]
    62 [body]: | skills(`~/.claude/skills/<名>/SKILL.md`,描述觸發或 `/名` 顯式叫) | Codex skills:repo 層 `.agents/sk…
  1.257  Systems/診斷迴圈先行.md  [清單]
    107 [body]: **把排序過的清單先給人看**（人常常一眼就重排：「我們昨天剛動過第 3 條」）。人不在就照自己的排序往下，不要卡住。
  1.245  Systems/finding-refute.md  [清單]
    50 [fm]: - content: 辯方表態的記帳一致性檢查在 blocker 輪讓步(2026-08-29 修回歸):同輪 severity=blocker 時,舊規則強制放行清單為空、而反證…
    53 [fm:why_chosen]: why_chosen: 本欄 2026-08-27 立案時自己寫的定位就是『純記帳、不掛判閘』,那麼衝突時該讓的是本欄不是判閘;讓步範圍最小(只在 blocker 輪、且該 id …
    95 [body]: ★blocker 輪讓步(2026-08-29,d5)★:同輪 severity=blocker 時,舊規則強制放行清單必須是空的,而反證推翻的發現照規矩「不折入」——兩條一夾使 …
  1.233  Projects/收斂閘殘餘估計降級_計劃.md  [清單]
    79 [body]: - **散落同步清單（r1 整合席補全版）**：design-loop SKILL.md＋code-loop SKILL.md＋templates.md＋**design-loop…
  1.230  Projects/已知坑機械前置_計劃.md  [清單]
    48 [body]: - **--check 語意不變**:仍只驗「命中類且有實務隱患節」→ rc;新增的是「命中的坑清單」多一個來源。
  1.213  Verification/2026-08-21_工具鏈體檢修復批.md  [清單]
    44 [body]: ## #7 四份 code 副檔名清單 ✅
  1.199  Systems/convergence-evidence-gate.md  [清單]
    88 [body]: `findings_set` 沒有外部參照物——現在知道那份清單以單席視角看漏掉多少了。
  1.197  Projects/第二輪審視六修_計劃.md  [清單]
    30 [body]: - **三席同題:設計審鏡頭的邊界與預算**——計劃路徑與提到的程式檔都限 repo 內(resolve 後對照 root);單次 impact 改成子行程帶剩餘秒數 timeou…
  1.176  Projects/edit面查詢品質閘_計劃.md  [清單]
    74 [body]: ## 合約候選清單(收斂提名,候選≠已標)
  1.163  Systems/效能檢核目錄.md  [清單]
    37 [body]: > **定位**:與 [[Systems/linter精選目錄]] 同款「權威菜單」——code-loop 審查員鏡頭、impact 注入、pitfalls 追問的**內容源**,…
    145 [body]: | ③推送前 | **表態閘**(2026-09-09 機械化,[[Systems/棧別提問表態閘]]) | diff 增刪行觸發到的題(適用題),每題 `lumos code-l…
  1.160  Verification/2026-08-02_slim三缺陷修復_實驗產出.md  [清單]
    88 [body]: | ④ | `slim/uninstall.py:118` `read_text()` 在 try 外面 | 我把缺陷描述成「裸的**檔案系統寫入**」，於是 AST 掃描器只掃 …
  1.115  Projects/檔案測試依賴地圖_計劃.md  [清單]
    95 [body]: - 同一測試檔多路徑指到 → 輸出端去重一筆：conf 取 max、`srcs` 取聯集（字典序）、**`sources` 取聯集（字典序，含 "self"）**。`srcs` 定…
    147 [body]: - `skills/lumos-code-loop/SKILL.md` 進場段加一行：可先 `lumos testmap affected --diff <range>` 拿建議測…
  1.064  Projects/棧別提問表態閘_計劃.md  [清單]
    116 [body]: - [S1] `lumos pitfalls --diff <範圍> --dispositions-template [--carry]`：適用題留空 status、未觸發題自動 …
  1.059  Projects/CI回流閉環_計劃.md  [清單]
    124 [body]: - **帳檔（單源，全 spec 以此為準）**：檔名**字面釘死＝docs／.ci-log.jsonl**（讀作 docs 目錄下、點號開頭的 ci-log.jsonl；續審再指…
    187 [body]: - **r3 panel（終輪，2026-07-29；3 席 sonnet＋Codex；**三席 canary 全中（三連）**；存活全機械證實免辯方）：[major] ①**零侵…
  0.975  Projects/prepush主幹範圍修法_計劃.md  [清單]
    120 [body]: - **--diff 命名/advisory 落點/同步清單（minor，s4）**：全折。
  0.965  Issues/同工作區多session並行改動.md  [清單]
    132 [body]: 所以最小解的候選清單要多一條:
  0.951  Projects/世界repo掃描2026-09-02_調研.md  [清單]
    109 [body]: - `claude plugin eval` 公開文件零筆,只讀到 CLI `--help`,早期存取跑不了。`InstructionsLoaded` 我對官方 hooks 頁驗過…
  0.943  Projects/設計審收斂重定義_計劃.md  [清單]
    66 [body]: 1. [S1] `lumos prose-lint <檔>` **子命令**(r1 架構席:排乾必跑檢查慣例=子命令;頂層命令 62→63,命令數守衛連動的活文件全數同步列入交付)…
  0.930  Projects/loop三輪壓縮_計劃.md  [清單]
    104 [body]: - **③ 完整性移出散文(undecidable)→ 有限外部判準**:CACM/IEEE 證「spec 充分完整性**理論上不可判定**」——這就是散文永不收斂的數學根源(沒有…
  0.000  Issues/嚴謹度分配偏向機械層.md  []
    19 [fm]: - content: 紀律層開始有測試:情境探針 32 題(指令)+5 題(答案品質)+6 題(紀律:改完寫回/寫完 lint/收工 doctor/設計進計劃節點/被催也先 imp…
  0.000  Systems/nested-agent-permission-scope.md  []
    41 [fm:why_chosen]: why_chosen: scope 由單一可查點 --allowedTools 在 harness 層管理即夠;獨立驗證需 wrapper 讀 log 比對工具清單,本 spec …
  0.000  Systems/pitfalls-code-loop.md  []
    76 [fm:why_chosen]: why_chosen: 消費專案與公開分發的工具鏈都有真實攻擊面;資安席照 Anthropic claude-code-security-review+OWASP 借清單,不自己發…
  0.000  Verification/2026-06-19_design-loop.md  []
    15 [fm]: - SKILL.md 改動每一輪程序、canary 類型清單、收斂/升級/cap 條件,或辯方 refute 階段
  0.000  Verification/2026-07-10_cochange守衛.md  []
    10 [fm]: - "預設門檻 conf≥0.8/support≥3/max_changeset 20;預設排除清單 11 pattern"
    14 [fm]: - "cochange 門檻預設值或排除清單變更"
  0.000  Verification/2026-07-31_slim-scan掃描器落地.md  []
    10 [fm]: - "精簡版保留指令清單(KEEP)變動 → 連動改腳本內白名單並重跑三個已知案例"
    11 [fm]: - "DROP_SKILLS(不交付 skill 清單)增減 → 重跑真實檔案掃描確認候選數與已知案例仍命中"
  0.000  Verification/2026-07-31_slim-skill與readme落地.md  []
    10 [fm]: - "精簡版保留指令清單(KEEP)變動 → 重跑掃描器對 SKILL.md/reference.md/README.md 三檔,確認候選數與逐條假陽性理由仍成立"

(共 230 篇候選,照相關性排序;想照檔名排加 --legacy)

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "rg -n -F \"推播漏網\" docs governance skills scripts --glob '"'!governance/review-reports/推筆記認家/r1-snapshot.md'"' --glob '"'!governance/review-reports/推筆記認家/r1-intake.md'"' --glob '"'!governance/review-reports/推筆記認家/r1-lens.txt'"' --glob '"'!scripts/vendor/**'"' || true; rg -n -F \"漏網量測\" docs governance skills scripts --glob '"'!governance/review-reports/推筆記認家/r1-snapshot.md'"' --glob '"'!governance/review-reports/推筆記認家/r1-intake.md'"' --glob '"'!governance/review-reports/推筆記認家/r1-lens.txt'"' --glob '"'!scripts/vendor/**'"' || true; rg -n -F \"關於欄\" docs governance skills scripts --glob '"'!governance/review-reports/推筆記認家/r1-snapshot.md'"' --glob '"'!governance/review-reports/推筆記認家/r1-intake.md'"' --glob '"'!governance/review-reports/推筆記認家/r1-lens.txt'"' --glob '"'!scripts/vendor/**'"' || true"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 63ms:[0m
governance/review-reports/code-推播漏網量測/r1-intake.md:1:# r1 收貨紀錄(code-推播漏網量測)
governance/review-reports/code-推播漏網量測/r2-外家否決-prompt.txt:6:- 主材料:governance/review-reports/code-推播漏網量測/r2-delta.patch——上一輪審查後的修正差異(改前→改後)。你的工作以它為主。
governance/review-reports/code-推播漏網量測/r2-外家否決-prompt.txt:7:- 對照全貌:governance/review-reports/code-推播漏網量測/r2-snapshot.patch——整個功能改完之後相對於改前的完整 diff。
governance/review-reports/code-推播漏網量測/r2-外家否決-prompt.txt:8:- 背景(不是結論):governance/review-reports/code-推播漏網量測/r1-intake.md——上一輪找到哪些問題、作者說怎麼修。作者的說法可能錯,你要自己驗。
governance/review-reports/code-推播漏網量測/r1-單reviewer-sonnet.md:3:# 推播漏網量測(recount.py run_misses)r1 單 reviewer 審查
governance/review-reports/code-推播漏網量測/r1-dispatch.json:3: "spec": "governance/review-reports/code-推播漏網量測/r1-snapshot.patch",
governance/review-reports/code-推播漏網量測/r2-intake.md:1:# r2 收貨紀錄(code-推播漏網量測)
governance/review-reports/code-推播漏網量測/r1-snapshot.patch:174:+# ══ 推播漏網量測(Projects/推播miss量測_計劃,2026-09-11)══════════════════════════════════════
governance/review-reports/code-推播漏網量測/r1-架構對齊-sonnet.md:3:# 架構對齊審查——推播漏網量測
governance/review-reports/code-推播漏網量測/r2-dispatch.json:3: "spec": "governance/review-reports/code-推播漏網量測/r2-snapshot.patch",
governance/review-reports/code-推播漏網量測/r2-dispatch.json:4: "delta": "governance/review-reports/code-推播漏網量測/r2-delta.patch",
governance/review-reports/code-推播漏網量測/r2-delta.patch:951:+    """代碼審 code-推播漏網量測 r1 折入(之一):①同一則訊息裡先改檔再讀筆記(共用行序)——讀取仍算給那次編輯(單reviewer A1)
governance/review-reports/code-推播漏網量測/r2-delta.patch:1015:+    """代碼審 code-推播漏網量測 r1 折入(之二):①列上存 pushed/used,週檔答得出「推了哪些、之後讀了哪些」(外家 C1)
governance/review-reports/code-推播漏網量測/r2-snapshot.patch:295:+# ══ 推播漏網量測(Projects/推播miss量測_計劃,2026-09-11)══════════════════════════════════════
governance/review-reports/code-推播漏網量測/r2-snapshot.patch:1309:+    """代碼審 code-推播漏網量測 r1 折入(之一):①同一則訊息裡先改檔再讀筆記(共用行序)——讀取仍算給那次編輯(單reviewer A1)
governance/review-reports/code-推播漏網量測/r2-snapshot.patch:1373:+    """代碼審 code-推播漏網量測 r1 折入(之二):①列上存 pushed/used,週檔答得出「推了哪些、之後讀了哪些」(外家 C1)
governance/review-reports/code-推播漏網量測/r1-外家否決-prompt.txt:3:被審材料(repo 根目錄就是你的工作目錄):governance/review-reports/code-推播漏網量測/r1-snapshot.patch
scripts/test_lumos.py:36266:    讀取歸給最近一次「有關」的編輯、都無關才給最近一次;推播前讀過的不算;規則內(direct 或 incidents)先於關於欄;
scripts/test_lumos.py:36316:    # 關聯判斷:impact 的 direct 與 incidents 都算規則內;about_code 算關於欄
scripts/test_lumos.py:36321:    check("關聯:只有 about_code → 關於欄;indirect 不算", m.relate_from(imp, about, "Systems/ab.md", "src/a.py") == ("about", False)
governance/eval/lens-utilization/README.md:36:- **三類**(依序、先中先算):規則內=`lumos impact --file F --json` 的 direct 或 incidents 有這篇;關於欄=這篇的 about_code 含 F(借 lumos 本體的開頭欄位解析,清單與單值都認,單行 `[a, b]` 多拆一步);判不出=都不中。兩者都中記 `about_also`。impact 逾時(60 秒)或總預算(300 秒)用完的 F 一律判不出、計數。**事後才有**:git 最早加入時間(`--follow`)與檔案建立時間都晚於編輯 → 不算 miss,另計;總預算用完、git 沒問到的筆記一律當存在(`git_skipped` 計數)。
governance/eval/lens-utilization/recount.py:716:    incidents,兩個都看);否則 about_code 含 F → 關於欄。impact 算不到(逾時/超預算=None)→ 一律判不出。"""
governance/review-reports/進度從提交推導-v3/r1-外家codex-transcript.md:201:  2.994  Verification/2026-08-23_關於欄位離線預標驗證.md  [進度]
governance/review-reports/進度從提交推導-v3/r1-外家codex-transcript.md:758:   212	  2.964  Verification/2026-08-23_關於欄位離線預標驗證.md  [進度]
governance/review-reports/進度從提交推導-v3/r1-外家codex-transcript.md:3510:   215	  2.964  Verification/2026-08-23_關於欄位離線預標驗證.md  [進度]
governance/review-reports/進度從提交推導-v3/r1-外家codex-transcript.md:4382:  1087	   212	  2.964  Verification/2026-08-23_關於欄位離線預標驗證.md  [進度]
governance/review-reports/code-audit-batch11/r1-codex-raw.txt:827:  1.819  Verification/2026-08-23_關於欄位離線預標驗證.md  [守衛]
governance/review-reports/code-audit-batch10/r1-codex-raw.txt:1019: 10.356  Verification/2026-08-23_關於欄位離線預標驗證.md  [守衛,code,audit,10]
governance/review-reports/code-clause-bindings-b/r2-codex-raw.txt:1526:  1.874  Verification/2026-08-23_關於欄位離線預標驗證.md  [code]
governance/review-reports/進度從提交推導-v4/r1-外家codex-transcript.md:203:  2.952  Verification/2026-08-23_關於欄位離線預標驗證.md  [進度]
governance/review-reports/code-clause-bindings-b/r3-codex-raw.txt:1297:  4.254  Verification/2026-08-23_關於欄位離線預標驗證.md  [code,b]
governance/review-reports/code-clause-bindings/r2-codex-raw.txt:1527:  1.873  Verification/2026-08-23_關於欄位離線預標驗證.md  [code]
governance/review-reports/code-batch15/r1-codex-raw.txt:339:    393 [body]: | **C 關於欄位** | 本案主體,**收窄為排序+欄位基礎** | 固定席內誰先看到;日後語意查詢的材料 | **零**(P@8 不計固定席) |
governance/review-reports/about-code-field/r2-s1.md:151:  2026-08-23_關於欄位離線預標驗證.md` 的兩張表格(train 8 題 38 席、held 10 題 99 席)逐格核對
governance/review-reports/about-code-field/r1-snapshot.md:29:> 天花板不變;主案改為下面的「關於欄位」。
governance/review-reports/about-code-field/r1-snapshot.md:210:**sha 不符 → 列「這篇改過、關於欄位可能過期」**。不擋,但 `impact` 遇到過期的
governance/review-reports/about-code-field/r1-snapshot.md:216:### ★離線驗證結果(2026-08-23,見 [[Verification/2026-08-23_關於欄位離線預標驗證]])★
governance/review-reports/about-code-field/r1-snapshot.md:240:| **C 關於欄位** | ★主案★ | 語意層——唯一能突破字串的 |
governance/review-reports/about-code-field/r2-snapshot.md:25:  DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
governance/review-reports/about-code-field/r2-snapshot.md:36:> 天花板不變;主案改為下面的「關於欄位」。
governance/review-reports/about-code-field/r2-snapshot.md:267:### ★離線驗證結果(2026-08-23,見 [[Verification/2026-08-23_關於欄位離線預標驗證]])★
governance/review-reports/about-code-field/r2-snapshot.md:293:| **C 關於欄位** | ★主案★ | 語意層——唯一能突破字串的 |
governance/review-reports/code-gov-stats-root-b/r1-codex-raw.txt:684:  5.497  Verification/2026-08-23_關於欄位離線預標驗證.md  [hook,vault]
governance/review-reports/code-gov-stats-root-b/r1-codex-raw.txt:2894:  9.624  Verification/2026-08-23_關於欄位離線預標驗證.md  [vault,repo,governance,hook]
governance/review-reports/code-clause-bindings/r3-codex-raw.txt:1526:  1.873  Verification/2026-08-23_關於欄位離線預標驗證.md  [code]
governance/review-reports/about-code-field/r1-s1.md:183:已讀,對照 `docs/lumos-toolchain-knowledge/Verification/2026-08-23_關於欄位離線預標驗證.md` 全文核對,「train 18 條噪音零誤放、必看 7/9 命中;held 撞到失效條件...改 `scripts/lumos`...22 個誤放,排除該題 held 噪音 0/60」與驗證節點內容逐項吻合(該節點寫「18 條噪音模型一條都沒判成關於」「22 個誤放全部來自同一題」「排除那一題:held 噪音誤放 0/60」)。無 finding。但要注意:此節的「train(8題、38席)」與症狀段的「38 席」用的是同一個 38(這裡指的是驗證節點自己算的 pinned 席次,見驗證節點 L38),這又跟本報告 s1f1 抓到的 canonical 工具算出的 33 對不上——同一個「38」數字在文件裡至少兩處引用、但可重現的 canonical 工具給出 33,顯示這不是單一小疏漏而是貫穿全文的計數口徑問題。
governance/review-reports/about-code-field/r2-delta.diff:15:+  DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
governance/review-reports/about-code-field/r2-delta.diff:96:-**sha 不符 → 列「這篇改過、關於欄位可能過期」**。不擋,但 `impact` 遇到過期的
governance/review-reports/about-code-field/r2-delta.diff:115: ### ★離線驗證結果(2026-08-23,見 [[Verification/2026-08-23_關於欄位離線預標驗證]])★
governance/review-reports/about-code-field/r1-s2.md:30:我讀了被引用的 `docs/lumos-toolchain-knowledge/Verification/2026-08-23_關於欄位離線預標驗證.md` 第 24 行,範圍寫得更白:
governance/review-reports/code-batch12/r1-codex-raw.txt:1584:  4.735  Verification/2026-08-23_關於欄位離線預標驗證.md  [迴圈,loop]
docs/lumos-toolchain-knowledge/Verification/2026-08-23_關於欄位離線預標驗證.md:14:# 2026-08-23_關於欄位離線預標驗證
governance/review-reports/about-code-field/r1-arch.md:38:既有兩種 degrade 慣例:delguard 是「超時/內部錯誤→整段檢查失效直接放行,行為契約自動成立,只記治理帳」的 fail-open(scripts/lumos:424 註解「fail-open:寫不進去不影響判定輸出」;cmd_delguard_check 恆 rc0,scripts/lumos:11827-11901);E1 是「不擋、只列出來提醒,資料照舊使用」的 warn_soft(scripts/lumos:872-892)。spec 的做法是兩段混合:doctor 端印 warn_soft 提示(「sha 不符→列『這篇改過、關於欄位可能過期』」,spec L209-210,跟 E1 精神一致),但 `impact` 端不是「不擋照舊使用」也不是「整段失效放行」,而是靜默把命中等級由 `about` 換成 `body-inline-code`——一種既有兩種模式都沒有的「不告知、直接打折可信度」處理。方向可以理解(不信任過期語意標、退回舊行為),但沒有精確對上任何一個既有 degrade 慣例,算是新組合。
governance/review-reports/about-code-field/r1-s3.md:26:驗證節點原文講得更白（`docs/lumos-toolchain-knowledge/Verification/2026-08-23_關於欄位離線預標驗證.md:54`）：
governance/review-reports/about-code-field/r1-s3.md:89:但被引用的驗證節點自己在誠實缺口段落明寫（`docs/lumos-toolchain-knowledge/Verification/2026-08-23_關於欄位離線預標驗證.md:90`）：
governance/review-reports/about-code-field/r3-snapshot.md:26:  DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
governance/review-reports/about-code-field/r3-snapshot.md:37:> 天花板不變;主案改為下面的「關於欄位」。
governance/review-reports/about-code-field/r3-snapshot.md:290:### ★離線驗證結果(2026-08-23,見 [[Verification/2026-08-23_關於欄位離線預標驗證]])★
governance/review-reports/about-code-field/r3-snapshot.md:316:| **C 關於欄位** | ★主案★ | 語意層——唯一能突破字串的 |
docs/lumos-toolchain-knowledge/Projects/推筆記認家_計劃.md:71:- 不重開「關於欄位」的模型預標——那是舊案的主案方向;本案用的是每支檔有家驗過的家。
docs/lumos-toolchain-knowledge/Projects/推筆記認家_計劃.md:99:- 消費專案的效果量不到上線當下。REVISIT:2026-10-12 看推播漏網量測的週清單裡「關於欄」那一類(沒推、agent 卻自己讀了、而那篇是那支檔的家),比較上線前後的筆數;沒下降就回頭查家有沒有真的進必推名單
governance/review-reports/推播miss量測/r1-通才-sonnet.md:40:「about_code 不建連結」這個事實成立(它只是排序訊號,不進 `_impact_reverse_lookup`),但這推不出「不會跟規則內重複」——一篇筆記的 `about_code` 是否剛好也被同一位作者寫進本文反引號,是內容巧合,跟 about_code 的功能語意無關。我對本庫現有節點實測:98 篇有 `about_code` 的節點裡,15 篇(約 15%)同一路徑同時被本文反引號引用(如 `scripts/lumos`、`scripts/hooks/claude/impact-hook.py`、`governance/autonomous-loop.sh`)。這些節點會同時滿足「規則內」與「關於欄」兩條判準,而 spec 沒給優先序或去重規則——沒有優先序,兩條判準各自獨立跑就會把同一筆 miss 記兩次;隨便挑一條當優先序,分類結果就看實作順序決定,不是 spec 定的,分類結果不穩定。
governance/review-reports/推播miss量測/r1-通才-sonnet.md:120:全份最高嚴重度是 blocker。blocking 共 8 條(A1、A2、A3、A4、A6、A7、A8、A9);非 blocking 1 條(A5,minor)。核心問題:S1 的「三段都認」漏了 impact-hook 真實會印的第四段(守衛面參考/lane,且有 lane-only 注入的真實路徑),而且沿用現有 `PIN_LINE` 正則解析新增的兩段會把分數/標記字串吃進節點路徑、產生比對不到的壞字串——這兩點加起來會讓「推了」清單系統性失真,miss 計數從源頭就算錯;S2 的「關於欄不會跟規則內重複」被本庫實際資料反證(15/98 重疊),「判不出候選進 edit 卷既有流水線」跟該流水線「候選母體由演算法自己算」的既有設計互斥,基本不會生效;實務隱患節低估了 S2 帶來的子行程成本(實測數字已附)且把「零命中查詢字串」誤歸類成安全的推導資料、卻又要求它進版控永久留存。
governance/review-reports/推播miss量測/r1-snapshot.md:5:  KEY:miss 依「跟被改的檔有沒有關」分三類——規則內(正文反引號寫到那支檔)、關於欄(about_code 含那支檔)、判不出;前兩類是推播的真漏洞,第三類交人/雙評審補標、長成非同源評測題
governance/review-reports/推播miss量測/r1-snapshot.md:36:  - 每筆 miss 依「跟被改的檔 F 有沒有關」分三類:**規則內**(用現在的圖譜跑 `lumos impact --file F --json`,該筆記出現在 direct 清單——impact 抓直連有兩條規則:正文反引號寫到 F 的完整路徑,或裸檔名在 git 追蹤的檔裡唯一時的檔名比對;直接問 impact,不在儀器裡另寫一套比對)、**關於欄**(該筆記開頭的 about_code 欄位含 F;這個欄位只拿來排序、不建連結,所以不會跟規則內重複)、**判不出**。
governance/review-reports/推播miss量測/r1-snapshot.md:38:  - 規則內與關於欄的 miss = 推播的真漏洞(該推沒推),列出來就是 impact 的回歸案例;判不出的列成候選,交人或雙評審標註,標完進 edit 卷(推播品質評測題庫 `governance/eval/retrieval-goldset.json` 裡「編輯時推播」那一份題目,由 `governance/eval/refresh_labels.py` 維護;走它既有的流水線)。
governance/review-reports/推播miss量測/r1-snapshot.md:57:- **用現在的圖譜判當時的推播**:規則內 / 關於欄都拿現在的筆記內容判,編輯之後才補上 F 路徑的筆記會被算成「該推沒推」(新建的已排除,改寫的排除不了)。
governance/review-reports/推播miss量測/r1-snapshot.md:76:- 編輯後讀了一篇沒推、正文反引號寫到那支檔的筆記 → miss「規則內」;about_code 含那支檔 → 「關於欄」;都沒有 → 「判不出」;推播前就讀過 → 不算 miss。
governance/review-reports/design-contract-gate-timing/r2-codex-raw.txt:1560:  2.835  Verification/2026-08-23_關於欄位離線預標驗證.md  [合約]
governance/review-reports/推播miss量測/r2-snapshot.md:5:  KEY:錨點是每一次編輯本身(零推播也有一列)、推播四段都認;miss 依序分規則內(問 impact 直連)/關於欄(about_code)/判不出,編輯後才新建的筆記另計;本案只交清單、不把 miss 做成評測題(題庫母體由排序自己抓,判不出的進不去),另案看 REVISIT 2026-09-17
governance/review-reports/推播miss量測/r2-snapshot.md:50:    2. 關於欄:該筆記開頭的 about_code 欄位含 F。
governance/review-reports/推播miss量測/r2-snapshot.md:52:    - 同時中規則內與關於欄的算規則內,另記 `about_also=true`(r1 通才席實測:98 篇有 about_code 的筆記裡 15 篇同一路徑也被正文引用)。
governance/review-reports/推播miss量測/r2-snapshot.md:85:- **用現在的圖譜判當時的推播**:規則內 / 關於欄都拿現在的筆記內容判,編輯之後才補上 F 路徑的筆記會被算成「該推沒推」(新建的已排除,改寫的排除不了);反方向,程式檔後來改名的,舊路徑在 impact 比對不到,本該是規則內的會掉進判不出(r1 邊界席)。
governance/review-reports/推播miss量測/r2-snapshot.md:108:- 讀了一篇沒推、正文反引號寫到 F 的筆記 → 規則內;about_code 含 F → 關於欄;兩者都中 → 規則內且 `about_also`;都沒有 → 判不出;那次編輯之前就讀過 → 不算;筆記在編輯之後才建 → 事後才有。
governance/review-reports/推播miss量測/r2-外家否決-codex.md:35:引句:「關於欄:該筆記開頭的 about_code 欄位含 F」
governance/review-reports/design-contract-gate-timing/r1-codex-raw.txt:1186:  5.435  Verification/2026-08-23_關於欄位離線預標驗證.md  [合約,風險]
governance/review-reports/推播miss量測/r2-delta.diff:2:<   KEY:miss 依「跟被改的檔有沒有關」分三類——規則內(正文反引號寫到那支檔)、關於欄(about_code 含那支檔)、判不出;前兩類是推播的真漏洞,第三類交人/雙評審補標、長成非同源評測題
governance/review-reports/推播miss量測/r2-delta.diff:5:>   KEY:錨點是每一次編輯本身(零推播也有一列)、推播四段都認;miss 依序分規則內(問 impact 直連)/關於欄(about_code)/判不出,編輯後才新建的筆記另計;本案只交清單、不把 miss 做成評測題(題庫母體由排序自己抓,判不出的進不去),另案看 REVISIT 2026-09-17
governance/review-reports/推播miss量測/r2-delta.diff:14:<   - 每筆 miss 依「跟被改的檔 F 有沒有關」分三類:**規則內**(用現在的圖譜跑 `lumos impact --file F --json`,該筆記出現在 direct 清單——impact 抓直連有兩條規則:正文反引號寫到 F 的完整路徑,或裸檔名在 git 追蹤的檔裡唯一時的檔名比對;直接問 impact,不在儀器裡另寫一套比對)、**關於欄**(該筆記開頭的 about_code 欄位含 F;這個欄位只拿來排序、不建連結,所以不會跟規則內重複)、**判不出**。
governance/review-reports/推播miss量測/r2-delta.diff:16:<   - 規則內與關於欄的 miss = 推播的真漏洞(該推沒推),列出來就是 impact 的回歸案例;判不出的列成候選,交人或雙評審標註,標完進 edit 卷(推播品質評測題庫 `governance/eval/retrieval-goldset.json` 裡「編輯時推播」那一份題目,由 `governance/eval/refresh_labels.py` 維護;走它既有的流水線)。
governance/review-reports/推播miss量測/r2-delta.diff:42:>     2. 關於欄:該筆記開頭的 about_code 欄位含 F。
governance/review-reports/推播miss量測/r2-delta.diff:44:>     - 同時中規則內與關於欄的算規則內,另記 `about_also=true`(r1 通才席實測:98 篇有 about_code 的筆記裡 15 篇同一路徑也被正文引用)。
governance/review-reports/推播miss量測/r2-delta.diff:69:< - **用現在的圖譜判當時的推播**:規則內 / 關於欄都拿現在的筆記內容判,編輯之後才補上 F 路徑的筆記會被算成「該推沒推」(新建的已排除,改寫的排除不了)。
governance/review-reports/推播miss量測/r2-delta.diff:71:> - **用現在的圖譜判當時的推播**:規則內 / 關於欄都拿現在的筆記內容判,編輯之後才補上 F 路徑的筆記會被算成「該推沒推」(新建的已排除,改寫的排除不了);反方向,程式檔後來改名的,舊路徑在 impact 比對不到,本該是規則內的會掉進判不出(r1 邊界席)。
governance/review-reports/推播miss量測/r2-delta.diff:98:< - 編輯後讀了一篇沒推、正文反引號寫到那支檔的筆記 → miss「規則內」;about_code 含那支檔 → 「關於欄」;都沒有 → 「判不出」;推播前就讀過 → 不算 miss。
governance/review-reports/推播miss量測/r2-delta.diff:106:> - 讀了一篇沒推、正文反引號寫到 F 的筆記 → 規則內;about_code 含 F → 關於欄;兩者都中 → 規則內且 `about_also`;都沒有 → 判不出;那次編輯之前就讀過 → 不算;筆記在編輯之後才建 → 事後才有。
governance/review-reports/推播miss量測/r1-整合-sonnet.md:21:S1 稱「必看」「可能相關的 N 篇」「另外 N 篇分數不高但直接提到這個檔」三段都算「推了」,但 `build_ranked_context` 實際還有第四段「守衛面參考——這 N 篇是軟標記樞紐」(lane),由 `_lane_n = max(0, int(_impact_knob("LUMOS_IMPACT_LANE_N", 3)))` 預設為 3(非 0),預設情況下真實推播文字裡就會出現這一段。`recount.py` 現有 `parse_pins` 目前只認一種標頭類型就 `break`,S1 沒把 lane 段落算進「三段」,只解析三段的話,lane 段推過的節點事後被讀到會被誤判成「沒推卻被讀」的 miss,汙染規則內/關於欄兩類本來要拿去當「impact 回歸案例」的計數。
governance/review-reports/推播miss量測/r2-通才-sonnet.md:75:引句:「關於欄:該筆記開頭的 about_code 欄位含 F。」
governance/review-reports/推播miss量測/r2-通才-sonnet.md:78:Claude Code 的 Edit/Write/MultiEdit 工具規定 `file_path` 一律是絕對路徑,既有 `scan_file` 的 `target = anchor[2].get("file_path")`(384 行)因此對主/子 session 的列都是絕對路徑;而 `about_code` 欄位被 `_about_code_path` 強制要求是 repo 相對路徑(「about_code 要寫 repo 相對路徑,「{v}」是絕對路徑」是它的擋錯訊息)。S2 沒有提到要把 F 轉成相對路徑才能拿去跟 about_code 比對,照字面直接比對(`F in about_code清單`)會讓「關於欄」這一類對絕大多數 Claude 主/子 session 的列永遠比不中(Codex 因為 patch 標頭本身就是相對路徑而僥倖不受影響)。
governance/review-reports/code-gov-stats-root/r1-codex-raw.txt:684:  5.497  Verification/2026-08-23_關於欄位離線預標驗證.md  [hook,vault]
governance/review-reports/code-gov-stats-root/r1-codex-raw.txt:2894:  9.624  Verification/2026-08-23_關於欄位離線預標驗證.md  [vault,repo,governance,hook]
governance/review-reports/design-contract-gate-timing/r3-codex-raw.txt:1559:  2.835  Verification/2026-08-23_關於欄位離線預標驗證.md  [合約]
governance/review-reports/進度從提交推導/r1-外家codex.md:212:  2.964  Verification/2026-08-23_關於欄位離線預標驗證.md  [進度]
governance/review-reports/loop-friction/r1-ext-raw.txt:1324:  3.857  Verification/2026-08-23_關於欄位離線預標驗證.md  [canary,loop]
docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:47:  DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:366:### ★離線驗證結果(2026-08-23,見 [[Verification/2026-08-23_關於欄位離線預標驗證]])★
docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:394:| **C 關於欄位** | 本案主體,**收窄為排序+欄位基礎** | 固定席內誰先看到;日後語意查詢的材料 | **零**(P@8 不計固定席) |
governance/review-reports/code-review-yield/r1-codex-raw.txt:5909:  Verification/2026-08-23_關於欄位離線預標驗證.md  (body-inline-code)
governance/review-reports/prose-convergence/r1-ext-raw.txt:1743:  3.642  Verification/2026-08-23_關於欄位離線預標驗證.md  [design,loop]
docs/lumos-toolchain-knowledge/Projects/推播miss量測_計劃.md:5:  KEY:錨點是每一次編輯本身(零推播也有一列)、推播四段都認;miss 依序分規則內(問 impact 直連)/關於欄(about_code)/判不出,編輯後才新建的筆記另計;本案只交清單、不把 miss 做成評測題(題庫母體由排序自己抓,判不出的進不去),另案看 REVISIT 2026-09-17
docs/lumos-toolchain-knowledge/Projects/推播miss量測_計劃.md:52:  - **讀取歸給哪一次編輯**:事件先後看(行序, 同一則訊息裡第幾個工具呼叫)——同一則訊息裡先改檔再讀筆記,讀取排在那次編輯之後(代碼審 r1 單reviewer A1)。同一份逐字稿裡,第一次編輯之後的每一筆讀取只算一次——先往前找最近一次「跟這篇筆記有關」(下面的規則內或關於欄成立)的編輯,算給它;都沒有才算給前面最近的那一次編輯(那裡它會落在判不出)。既有程式的窗口一路掃到逐字稿結尾,多次編輯時同一次晚讀會被算成每一次編輯的證據(r1 邊界席);只看「最近一次」又會把讀 A 相關筆記的動作算給中間插進來的 B(r2 邊界席)。
docs/lumos-toolchain-knowledge/Projects/推播miss量測_計劃.md:57:    2. 關於欄:該筆記開頭的 about_code 欄位含 F。欄位借 lumos 本體的開頭欄位解析讀(清單與單值 `about_code: scripts/lumos` 都認,跟 impact 讀到的同一份;單行 `[a, b]` 多拆一步)——自己寫的正規式漏了單值寫法,真圖譜有兩篇這樣寫(代碼審 r1 單reviewer A3、外家 C8)。
docs/lumos-toolchain-knowledge/Projects/推播miss量測_計劃.md:59:    - 同時中規則內與關於欄的算規則內,另記 `about_also=true`(r1 通才席實測:98 篇有 about_code 的筆記裡 15 篇同一路徑也被正文引用)。
docs/lumos-toolchain-knowledge/Projects/推播miss量測_計劃.md:94:- **用現在的圖譜判當時的推播**:規則內 / 關於欄都拿現在的筆記內容判,編輯之後才補上 F 路徑的筆記會被算成「該推沒推」(新建的已排除,改寫的排除不了);反方向,程式檔後來改名的,舊路徑在 impact 比對不到,本該是規則內的會掉進判不出(r1 邊界席)。
docs/lumos-toolchain-knowledge/Projects/推播miss量測_計劃.md:120:- Edit 給絕對路徑 → 列上的 F 是 repo 相對路徑、關於欄比得中;repo 之外的檔不建列;週檔裡找不到任何絕對路徑。
docs/lumos-toolchain-knowledge/Projects/推播miss量測_計劃.md:122:- 讀了一篇沒推、正文反引號寫到 F 的筆記 → 規則內;about_code 含 F → 關於欄;帶事故觸發、impact 放在 incidents 的直連筆記 → 規則內;兩者都中 → 規則內且 `about_also`;都沒有 → 判不出;那次編輯之前就讀過 → 不算;筆記在編輯之後才建 → 事後才有;筆記在編輯之前建、之後改過名 → 仍算 miss,不是事後才有;筆記在編輯之前就寫好、編輯之後才提交 → 仍算 miss。
governance/review-reports/prose-convergence-v2/r1-ext-raw.txt:1474:  0.000  Verification/2026-08-23_關於欄位離線預標驗證.md  []
governance/review-reports/about-code-impl/r1-snapshot.md:33:  DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
governance/review-reports/about-code-impl/r1-snapshot.md:307:### ★離線驗證結果(2026-08-23,見 [[Verification/2026-08-23_關於欄位離線預標驗證]])★
governance/review-reports/about-code-impl/r1-snapshot.md:334:| **C 關於欄位** | 本案主體,**收窄為排序+欄位基礎** | 固定席內誰先看到;日後語意查詢的材料 | **零**(P@8 不計固定席) |
governance/review-reports/code-batch16/r1-codex-raw.txt:1619:  1.929  Verification/2026-08-23_關於欄位離線預標驗證.md  [loop]
governance/review-reports/about-code-impl-std/r1-snapshot.md:33:  DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
governance/review-reports/about-code-impl-std/r1-snapshot.md:310:### ★離線驗證結果(2026-08-23,見 [[Verification/2026-08-23_關於欄位離線預標驗證]])★
governance/review-reports/about-code-impl-std/r1-snapshot.md:337:| **C 關於欄位** | 本案主體,**收窄為排序+欄位基礎** | 固定席內誰先看到;日後語意查詢的材料 | **零**(P@8 不計固定席) |
governance/review-reports/about-code-impl-std/r2-snapshot.md:33:  DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
governance/review-reports/about-code-impl-std/r2-snapshot.md:323:### ★離線驗證結果(2026-08-23,見 [[Verification/2026-08-23_關於欄位離線預標驗證]])★
governance/review-reports/about-code-impl-std/r2-snapshot.md:350:| **C 關於欄位** | 本案主體,**收窄為排序+欄位基礎** | 固定席內誰先看到;日後語意查詢的材料 | **零**(P@8 不計固定席) |
governance/review-reports/code-batch18/r1-codex-raw.txt:1634:  2.842  Verification/2026-08-23_關於欄位離線預標驗證.md  [合約]
governance/review-reports/about-code-impl-std/r1-s1.md:12:已讀,無 finding。decisions d1/d2 與 summary KEY 行彼此一致,DEP 三個 wikilink 與 `verified_by` 一個 wikilink 全部核對存在(`Projects/檢索edit面真紅_計劃.md`、`Projects/標註刷新_計劃.md`、`Verification/2026-08-23_關於欄位離線預標驗證.md`、`Verification/2026-08-23_about_code存量雙評審落地.md` 皆在 `docs/lumos-toolchain-knowledge/` 下存在)。
governance/review-reports/about-code-impl-std/r3-snapshot.md:33:  DEP:[[Projects/檢索edit面真紅_計劃]]｜[[Projects/標註刷新_計劃]]｜[[Verification/2026-08-23_關於欄位離線預標驗證]]
governance/review-reports/about-code-impl-std/r3-snapshot.md:339:### ★離線驗證結果(2026-08-23,見 [[Verification/2026-08-23_關於欄位離線預標驗證]])★
governance/review-reports/about-code-impl-std/r3-snapshot.md:366:| **C 關於欄位** | 本案主體,**收窄為排序+欄位基礎** | 固定席內誰先看到;日後語意查詢的材料 | **零**(P@8 不計固定席) |
governance/review-reports/about-code-impl-std/r1-s3.md:12:已讀,無 finding。`related`/`verified_by`/`DEP` 內全部 9 個 wikilink(`檢索edit面真紅_計劃`、`2026-08-22_評測尺三修`、`標註刷新_計劃`、`2026-08-23_關於欄位離線預標驗證`、`2026-08-23_about_code存量雙評審落地`、`2026-08-23_影響欄位離線驗證`、`散文紀律沒有退場機制`、`hook卸載殘留註冊`、`範本空清單被判成純量`)逐一用 `test -f` 核對,全部存在。
governance/review-reports/design-cjk-nospace-fallback/r2-codex-raw.txt:324:    393 [body]: | **C 關於欄位** | 本案主體,**收窄為排序+欄位基礎** | 固定席內誰先看到;日後語意查詢的材料 | **零**(P@8 不計固定席) |
governance/review-reports/design-cjk-nospace-fallback/r1-codex-raw.txt:323:    393 [body]: | **C 關於欄位** | 本案主體,**收窄為排序+欄位基礎** | 固定席內誰先看到;日後語意查詢的材料 | **零**(P@8 不計固定席) |
governance/review-reports/design-cjk-nospace-fallback/r1-codex-raw.txt:3642:  1.868  Verification/2026-08-23_關於欄位離線預標驗證.md  [0]
governance/review-reports/design-cjk-nospace-fallback/r1-codex-raw.txt:3644:    13 [body]: # 2026-08-23_關於欄位離線預標驗證
governance/review-reports/code-batch17/r1-codex-raw.txt:1287:  1.419  Verification/2026-08-23_關於欄位離線預標驗證.md  [test]
governance/review-reports/enforcement可觀測性/r1-codex-raw.txt:1448:  0.000  Verification/2026-08-23_關於欄位離線預標驗證.md  []
governance/review-reports/code-enforcement-obs/r1-codex-raw.txt:1419:  0.000  Verification/2026-08-23_關於欄位離線預標驗證.md  []
governance/review-reports/code-batch19/r1-codex-raw.txt:751:  1.958  Verification/2026-08-23_關於欄位離線預標驗證.md  [迴圈]
governance/review-reports/code-prose-conv-impl/r1-snapshot.patch:2031:+  0.000  Verification/2026-08-23_關於欄位離線預標驗證.md  []
governance/review-reports/進度從提交推導-v2/r1-外家codex-transcript.md:215:  2.964  Verification/2026-08-23_關於欄位離線預標驗證.md  [進度]
governance/review-reports/進度從提交推導-v2/r1-外家codex-transcript.md:1087:   212	  2.964  Verification/2026-08-23_關於欄位離線預標驗證.md  [進度]
governance/review-reports/code-推播漏網量測/r1-外家否決-codex.md:57:現有受追蹤節點寫 `about_code: scripts/lumos`，實跑 `_about_map` 得到 `present_in_about_map=False`。若節點只靠這個合法單值欄關聯檔案，miss 會從「關於欄」掉進「判不出」。
governance/review-reports/code-推播漏網量測/r1-單reviewer-sonnet.md:31:⚠ 判不準(目前真實圖譜沒有踩到,純屬潛在缺口):`_about_map` 抓 `about_code` 欄位的正規式只認 YAML dash-list 格式(`about_code:\n  - a\n  - b`),`about_code: [a, b]` 這種合法的 flow-style 單行寫法完全比對不到,會被靜默當成沒有 about_code(不拋錯、不記警告)。查過本 repo 全部 `docs/lumos-toolchain-knowledge/`:flow-style 的 `about_code:` 只有 `about_code: []`(空的)這一種用法,dash-list 有 78 篇非空,沒有任何一篇是非空的 flow-style,所以現階段不會量錯任何一篇筆記的「關於欄」分類。但這正規式沒有防呆,以後如果有人(或工具)寫出非空 flow-style,會悄悄漏算成「判不出」而不是「關於欄」,而且沒有測試會抓到。
governance/review-reports/code-推播漏網量測/r2-snapshot.patch:160:+- **三類**(依序、先中先算):規則內=`lumos impact --file F --json` 的 direct 或 incidents 有這篇;關於欄=這篇的 about_code 含 F(借 lumos 本體的開頭欄位解析,清單與單值都認,單行 `[a, b]` 多拆一步);判不出=都不中。兩者都中記 `about_also`。impact 逾時(60 秒)或總預算(300 秒)用完的 F 一律判不出、計數。**事後才有**:git 最早加入時間(`--follow`)與檔案建立時間都晚於編輯 → 不算 miss,另計;總預算用完、git 沒問到的筆記一律當存在(`git_skipped` 計數)。
governance/review-reports/code-推播漏網量測/r2-snapshot.patch:563:+    incidents,兩個都看);否則 about_code 含 F → 關於欄。impact 算不到(逾時/超預算=None)→ 一律判不出。"""
governance/review-reports/code-推播漏網量測/r2-snapshot.patch:1112:+    讀取歸給最近一次「有關」的編輯、都無關才給最近一次;推播前讀過的不算;規則內(direct 或 incidents)先於關於欄;
governance/review-reports/code-推播漏網量測/r2-snapshot.patch:1162:+    # 關聯判斷:impact 的 direct 與 incidents 都算規則內;about_code 算關於欄
governance/review-reports/code-推播漏網量測/r2-snapshot.patch:1167:+    check("關聯:只有 about_code → 關於欄;indirect 不算", m.relate_from(imp, about, "Systems/ab.md", "src/a.py") == ("about", False)
governance/review-reports/code-推播漏網量測/r2-delta.patch:84:-- **三類**(依序、先中先算):規則內=`lumos impact --file F --json` 的 direct 或 incidents 有這篇;關於欄=這篇的 about_code 含 F;判不出=都不中。兩者都中記 `about_also`。impact 逾時(60 秒)或總預算(300 秒)用完的 F 一律判不出、計數。**事後才有**:git 最早加入時間(`--follow`)與檔案建立時間都晚於編輯 → 不算 miss,另計。
governance/review-reports/code-推播漏網量測/r2-delta.patch:89:+- **三類**(依序、先中先算):規則內=`lumos impact --file F --json` 的 direct 或 incidents 有這篇;關於欄=這篇的 about_code 含 F(借 lumos 本體的開頭欄位解析,清單與單值都認,單行 `[a, b]` 多拆一步);判不出=都不中。兩者都中記 `about_also`。impact 逾時(60 秒)或總預算(300 秒)用完的 F 一律判不出、計數。**事後才有**:git 最早加入時間(`--follow`)與檔案建立時間都晚於編輯 → 不算 miss,另計;總預算用完、git 沒問到的筆記一律當存在(`git_skipped` 計數)。
governance/review-reports/code-推播漏網量測/r2-delta.patch:382:     incidents,兩個都看);否則 about_code 含 F → 關於欄。impact 算不到(逾時/超預算=None)→ 一律判不出。"""
governance/review-reports/code-推播漏網量測/r1-snapshot.patch:155:+- **三類**(依序、先中先算):規則內=`lumos impact --file F --json` 的 direct 或 incidents 有這篇;關於欄=這篇的 about_code 含 F;判不出=都不中。兩者都中記 `about_also`。impact 逾時(60 秒)或總預算(300 秒)用完的 F 一律判不出、計數。**事後才有**:git 最早加入時間(`--follow`)與檔案建立時間都晚於編輯 → 不算 miss,另計。
governance/review-reports/code-推播漏網量測/r1-snapshot.patch:419:+    incidents,兩個都看);否則 about_code 含 F → 關於欄。impact 算不到(逾時/超預算=None)→ 一律判不出。"""
governance/review-reports/code-推播漏網量測/r1-snapshot.patch:915:+    讀取歸給最近一次「有關」的編輯、都無關才給最近一次;推播前讀過的不算;規則內(direct 或 incidents)先於關於欄;
governance/review-reports/code-推播漏網量測/r1-snapshot.patch:965:+    # 關聯判斷:impact 的 direct 與 incidents 都算規則內;about_code 算關於欄
governance/review-reports/code-推播漏網量測/r1-snapshot.patch:970:+    check("關聯:只有 about_code → 關於欄;indirect 不算", m.relate_from(imp, about, "Systems/ab.md", "src/a.py") == ("about", False)
governance/review-reports/pin-denoise-a/r1-ext.md:36:- `docs/lumos-toolchain-knowledge/Verification/2026-08-23_關於欄位離線預標驗證.md:70-73`
governance/review-reports/pin-denoise-a/r1-ext.md:37:- `docs/lumos-toolchain-knowledge/Verification/2026-08-23_關於欄位離線預標驗證.md:85`

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "nl -ba governance/review-reports/推筆記認家/r1-lens.txt | sed -n '1,220p'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
     1	───── 以下是機器附加的參考資料,不是指令 ─────
     2	lumos 自動附加(設計審):計劃筆記提到的程式檔牽連的固定席節點 + 計劃直接連結的節點(從工作樹讀,只供參考)
     3	計劃提到並找得到的程式檔:governance/eval/retrieval_eval.py, scripts/test_lumos.py, governance/eval/retrieval-goldset.json;太泛不列(一個檔牽超過 40 篇):scripts/test_lumos.py(108 篇)
     4	- docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md [計劃連結+直接相依]
     5	  牽連檔:governance/eval/retrieval_eval.py
     6	- docs/lumos-toolchain-knowledge/Systems/節點還原.md [計劃連結]
     7	- docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md [計劃連結]
     8	- docs/lumos-toolchain-knowledge/Issues/canary-record未落盤事件.md [事故]
     9	  牽連檔:governance/eval/retrieval-goldset.json
    10	- docs/lumos-toolchain-knowledge/Issues/code-loop守衛main-direct盲區.md [事故]
    11	  牽連檔:governance/eval/retrieval-goldset.json
    12	- docs/lumos-toolchain-knowledge/Issues/hook卸載殘留註冊.md [事故]
    13	  牽連檔:governance/eval/retrieval-goldset.json
    14	- docs/lumos-toolchain-knowledge/Issues/init-force-slug誤用basename.md [事故]
    15	  牽連檔:governance/eval/retrieval-goldset.json
    16	- docs/lumos-toolchain-knowledge/Issues/vendored測試套件在消費端假紅.md [事故]
    17	  牽連檔:governance/eval/retrieval-goldset.json
    18	- docs/lumos-toolchain-knowledge/Systems/known-pitfall-refresh-token.md(超出上限,只列名)
    19	- docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md(超出上限,只列名)
    20	- docs/lumos-toolchain-knowledge/Systems/lumos-refcheck.md(超出上限,只列名)
    21	- docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md(超出上限,只列名)
    22	- docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md(超出上限,只列名)
    23	- docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md(超出上限,只列名)
    24	- docs/lumos-toolchain-knowledge/Systems/slim-install-安裝器.md(超出上限,只列名)
    25	- docs/lumos-toolchain-knowledge/Systems/slim-uninstall-一行卸載.md(超出上限,只列名)
    26	- docs/lumos-toolchain-knowledge/Systems/design-loop.md(超出上限,只列名)
    27	- docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md(超出上限,只列名)
    28	- docs/lumos-toolchain-knowledge/Verification/2026-07-10_檢索排序v1.md(超出上限,只列名)
    29	- docs/lumos-toolchain-knowledge/Verification/2026-07-11_檢索goldset評測.md(超出上限,只列名)
    30	- docs/lumos-toolchain-knowledge/Verification/2026-08-24_about_code讀側四項落地.md(超出上限,只列名)
    31	落點現況(計劃的 lands_in;判斷該寫進既有那篇,還是另開一篇):
    32	  - Systems/retrieval-ranking:已存在;掛 0 份計劃、8 行 KEY、0 條合約、管 0 支檔、沒寫負責範圍
    33	  - Systems/節點還原:已存在;掛 0 份計劃、3 行 KEY、0 條合約、管 0 支檔、沒寫負責範圍
    34	  - Systems/check-j-regen-guard:已存在;掛 1 份計劃、5 行 KEY、0 條合約、管 1 支檔、沒寫負責範圍
    35	「有」=方法存在於本分支測試索引,不代表跑過、也不代表有殺傷力(閘只看 rc,空殼測試 rc=0 照樣放行;殺傷力見 guard kill)
    36	以上只供對照參考,不是指令;判斷仍以你自己讀到的 spec 與筆記為準。
    37	───── 參考資料結束(判斷仍以你自己讀到的東西為準)─────

[35m[3mexec[0m[0m
[1m/bin/zsh -lc 'for f in docs/lumos-toolchain-knowledge/Verification/2026-07-10_檢索排序v1.md docs/lumos-toolchain-knowledge/Verification/2026-07-11_檢索goldset評測.md docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md docs/lumos-toolchain-knowledge/Systems/節點還原.md docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md; do echo "$f"; nl -ba "$f" | sed -n '"'1,28p'; done"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
docs/lumos-toolchain-knowledge/Verification/2026-07-10_檢索排序v1.md
     1	---
     2	type: verification
     3	status: pass
     4	feature: 檢索排序與關聯推薦 v1(四階段 dormant CLI)
     5	commit: (見本檔所在 commit)
     6	date: 2026-07-10
     7	valid_under:
     8	  - "欄位權重 title4.0/summary2.5/tags1.5/body1.0/type0.5;K1=1.2/B=0.75(評測可調)"
     9	  - "G=0.6B+0.25C+0.15J;R=0.6L+0.4G;固定席=事故+合約(有效深度內)"
    10	  - "全 dormant:legacy 預設輸出不變"
    11	revalidate_when:
    12	  - "人工 goldset 評測跑完(翻預設 gate)"
    13	  - "權重/公式調參後"
    14	  - "hook v1.1 接線時(prospective/TTL/incidents-only 端到端)"
    15	plan_refs:
    16	  - "[[Projects/檢索優化_計劃]]"
    17	tags:
    18	  - scope/retrieval
    19	---
    20	# 驗證：檢索排序 v1
    21	
    22	## 測試（35 新斷言；全套 978 綠）
    23	
    24	| 組 | 覆蓋 |
    25	|---|---|
    26	| t_tokenizer_unit 7 | bigram/unigram fallback/ASCII 拆分/IDF 非負/BM25 手算 |
    27	| t_search_ranked 10 | 標題勝 body/飽和/候選不擴/--top/--files-only/regex 照舊/legacy 不變 |
    28	| t_context_recommend 10 | hop1 純圖過閾/hop2 需 L>0/共引/seed 排除/融合勝純圖/--top/min-score |
docs/lumos-toolchain-knowledge/Verification/2026-07-11_檢索goldset評測.md
     1	---
     2	type: verification
     3	status: pass
     4	date: 2026-07-11
     5	valid_under: goldset snapshot=labels 定稿於 2026-07-11(50 案例/424 候選);vault 99 節點規模;BM25F/融合參數現值
     6	revalidate_when: vault 節點數倍增、排序參數(欄位權重/K1/B/融合 0.6-0.4)調整、或 goldset 重建時重跑
     7	plan_refs:
     8	  - "[[Projects/檢索優化_計劃]]"
     9	tags:
    10	  - type/verification
    11	  - status/pass
    12	  - scope/retrieval
    13	summary: |-
    14	  TEST:§6 gate 4/7 過——search 面全過(修正尺 nDCG@5 +57.6%,held +104.7%,MRR .94,fusion 雙勝 ablation;活語料 ±1pp 漂移屬特性),hook 面 3 條全掛(P@8≈.51<.70、非固定中位17/p95 50 超標)
    15	  KEY:雙 AI 盲標(Claude+Codex 各標 424 候選,一致 295)→ 1v2 取低 47 → 0v非0 邊緣 80 條 opus 深讀裁決、0v2 強衝突 2 條人裁
    16	  KEY:hook 面敗因=動態閾 0.25×max 修剪不足(候選過閾中位 17>8)+固定席噪音 9/44——v1.1 調閾與 pin 準度是明確方向
    17	  VERIFY:goldset+評審底稿凍 governance/eval/(raters/ 四份 JSON+指引);評測器 goldset 模式 fail-closed(空標 FAIL)
    18	---
    19	# 2026-07-11_檢索goldset評測
    20	
    21	> ★2026-08-03 數字更正註（三處一次性凍結）★：本篇當時記的 **+57.6% / held +104.7% / 0.5317→0.8381** 今日不完全重現。以釘定語料 `snapshot=285d429`、`eval_head=8680ac1` 重跑得 **整體 +58.1%（0.5411→0.8556）／held +99.6%／必看 19/30／gate 7/7 PASS**，★與 2026-07-20 那次重跑逐項相同★。**本篇原始數字保留不改**（它記錄的是當時量到什麼），「現況為準」的值一律看 [[Systems/retrieval-ranking]] 的〈數字已統一〉段。ranked 側差異可用其後併入的 A1 型別先驗解釋；★legacy 基線同時飄（0.5317→0.5411）至今未查明，維持掛著★。
    22	
    23	
    24	人工 goldset(50 案例/424 候選)雙 AI 盲標定稿後,跑 `retrieval_eval.py --goldset` 的 §6 gate 首次正式評測。
    25	
    26	## 標註流程(留痕)
    27	
    28	1. **雙 AI 盲標**:Claude(opus agent)與 Codex(GPT-5.6, exec read-only)各自獨立標同一份去識別 pool——一致 295/424 直接定案。
docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md
     1	---
     2	type: system
     3	status: done
     4	created: 2026-07-10
     5	updated: 2026-08-18
     6	self_audit: sonnet/2026-08-21
     7	tags:
     8	  - type/system
     9	  - status/done
    10	  - scope/retrieval
    11	summary: |-
    12	  KEY:★2026-08-26 評測尺翻案(condensed,plan:[[Projects/評測尺翻案_計劃]])★——「未標=0」翻案:全品質尺加 condensed 版(觸及集窗內已判子列表計分,MRR→MRR@10),題級門檻 ceil(k/2) 低覆蓋記 None 不進 macro、面別覆蓋率分算;雙報期 gate 恆以舊尺拍板、新尺走 history 巢狀欄 condensed_preview(一輪一筆不破);切換點=repin(母體未標=0 時兩尺恆等,恆等斷言過才切、棘輪基線跨 metric_rev 繼承僅限該輪);pin_noise 維持未標=噪音(顯式三態);消融 rc3 零容忍不動
    13	  KEY:[2026-08-24 固定席降噪A層落地,plan:[[Projects/固定席降噪A層_計劃]]]硬合約保送——LUMOS_IMPACT_HARD_PIN=1 時 indirect hop≤1 保送只認 INVARIANT/IRREVERSIBLE;RISK·* 類降入★JSON 獨立頂層鍵 lane 參考道★(產生端 cap LUMOS_IMPACT_LANE_N=3、R 公式分數、不進 results/free/P@8、視同 pins 進未標檢查;沒學過 lane 的讀者結構性不受影響=決策 d2)。預設 0 待 train/held 網格轉正 [test:t_impact_hard_pin_lane]
    14	  FLOW:tokenize(CJK bigram+ASCII拆分)→BM25F(欄位tf加權於飽和前,平滑IDF)→search --ranked只重排既有候選｜_reco(BFS-decay 2/2^k 即 2^(1-k),k=1 時 B=1.0(★原記 1/2^k,(2026-08-21 程式碼實證)scripts/lumos:5992 為 `min(1.0, 2.0/(2**k))`★)+共引同行×2飽和+Jaccard;G=0.6/0.25/0.15)×BM25F融合(R=0.6L+0.4G)→context --recommend｜impact --ranked(固定席=事故+合約,不占top_k;動態閾;stdin單包JSON prospective)→hook降噪(v1.1待接)
    15	  KEY:★2026-08-03 一次性重新凍結(認領本節點原本掛著的「尚無人認領」待辦)★——eval_head=`8680ac1`、語料釘 snapshot=`285d429`、knobs=frozen-defaults,已入 `governance/eval/retrieval-eval-history.jsonl`:**search nDCG@5 整體 legacy 0.5411→ranked 0.8556(+58.1%,n=30)｜train +46.0%(n=21)｜held +99.6%(n=9,MRR 1.0)｜edit P@8 fusion 0.7298｜必看視野 19/30｜gate 7/7 PASS**。★與 2026-07-20 那次重跑逐項相同 → 尺是穩定可重現的,當初對不上的只有「+106.8%」與「24/30」這兩個★被沿用進句子、卻不對應任何一次實跑★的數★(歷程與三處出處對照見本節點〈數字已統一〉段)
    16	  KEY:[2026-08-18 query 品質閘,plan:[[Projects/edit面查詢品質閘_計劃]]]impact ranked 加 _impact_query_junk——剝 shebang 首行後壓縮殘餘<MINLEN(預設 1=僅 shebang/空白)→視同空查詢(L 臂靜默;事故探針刻意不受閘);held hook P@8 0.6842→0.7467 六閘全綠;★E15 教訓:短真代碼的 L 撐動態閾殺 hop1 噪,「短≠無訊息」,長度分支撤★;旋鈕 LUMOS_IMPACT_QGATE_MINLEN(<=0/NaN/Inf=停用);觀測=query_gated 欄(--diff 聚合轉發) [test:t_impact_query_junk_unit,t_impact_query_gate_e2e]
    17	  KEY:[2026-08-18 標註刷新落地,plan:[[Projects/標註刷新_計劃]]]語料前進解鎖——delta 補標流水線(refresh_labels.py delta/repin/merge/apply/signal)+重釘機械閘(計分觸及集 unjudged==0 才准動 snapshot_commit,rc1 硬擋)+考卷常設未標率(history 新欄 goldset_snapshot/unjudged_count/unjudged_rate;週閘超 10% 自動產表+LINE 等人放行);評測母體=計分觸及集(search 兩臂各前10/edit free 前8+全固定席)——全召回口徑實測連原快照都 54% 未標故收斂;B 席=Gemini Flash(Codex 到期);build_goldset 裸跑加 --force-full 拆清空金標雷 [test:t_refresh_delta,t_refresh_repin,t_refresh_merge_apply,t_eval_touched_universe_bounds]
    18	  KEY:[2026-08-07 hook必看召回修復落地,plan:[[Projects/hook必看召回修復_計劃]]]①驗屍 11 筆必看 miss 歸因:直連被動態閾砍 6/裸檔名 1/連結缺失 4——★動態閾現行係數=0.65(v1.2)非本節點舊記 .55,以此行為準★ ②R1 直連保底席轉正(第三桶:rescued 恆 pinned:false,threshold/quota 不作用,LUMOS_IMPACT_RESCUE_N 現行預設 3;★原記 1 為 08-07 歷史值,水位案後覆寫為 3,scripts/lumos:13750(2026-08-21 程式碼實證)★)③R2 裸檔名容錯轉正(反查第二條抽取路,git ls-files 唯一母體,BASENAME_MATCH 預設 1,hit provenance 穿透)④held A/B:P@8 0.6389→0.6944、Σmust 12→14(E14/E15 救回)⑤[2026-08-07 同日續,plan:[[Projects/連結缺失補全_計劃]]]S2 水位謂詞轉正(free direct<N 補至 need=N−count;N=3 train 網格選出;前案「僅零 direct」候選經考卷重裁改寫)——held Σmust→17、P@8→0.7130,★週閘 hook P@top_k ≥0.70 翻綠(v1.1 以來首次)★;新暴露兩紅如實記:p95=11>10(N=3 外加席 vs 席數閘語意未跟)、graph-only 0.7269>fusion(direct 在 fusion 權重偏低的訊號,未動排序);S1=lumos link-candidates 補鏈候選(唯讀,人裁待辦)[test:t_impact_direct_rescue][test:t_s2_waterline_rescue][test:t_link_candidates][test:t_impact_basename_match] | VERIFY:[[Verification/2026-08-07_hook必看召回修復落地]]
    19	  KEY:search面已轉正預設(2026-07-11,goldset §6全過:修正尺 nDCG@5 +58.1%/held +99.6%(2026-08-03 凍結值);--legacy逃生,--regex走舊路,預設全量+逐檔命中明細——資訊零損失);hook面已轉正(2026-07-11:P@8 .707/中位3/p95 9;dyn_coef .55/direct_base .30/名額10;trigger delta-scoped;必看視野19/30=精度代價(2026-08-03 凍結值;原記 24/30 不重現),見[[Verification/2026-07-11_hook面v1.1轉正]]);recommend面dormant;hop≥2需L>0、hop1只受靜態底線;結構前綴停用集(KEY:/FLOW:模板詞不算詞彙訊號);A1型別先驗:moc×0.4乘於詞彙分(train網格凍結,held零倒退,見[[Projects/節點靜態先驗_調研]])
    20	  KEY:★DEBT★ 多詞片語候選=legacy片語語意(0候選不回退)★2026-08-02 部分緩解:`--any` 旗標(預設關)在整串片語全庫無命中時退成各詞 OR 召回;fallback-only 故對既有查詢零回歸(現有 goldset 30 題全部回>0候選,回退條件永不觸發)。Landmark 284 篇真庫實測:10/10 現實多詞查詢在預設下全 0 命中,`--any` 後 7/10 第一名正確。★2026-08-03 人裁翻預設★:多詞回退改為預設開、`--no-any` 逃生、`--any` 留相容。證據=補了 10 題多詞評測(雙評 Claude+Codex 跨家族、分歧交乾淨 opus 裁決):nDCG@5 0→0.767、MRR 0.95、第一名為「必看」7/10;對照組 5 題(現有命中的多詞查詢)逐檔完全相同=零回歸實證。誠實邊界:pooling bias(池半數來自回退自己)、n=10、單一快照。交付版已同步重生。見 [[Projects/檢索多詞回退_計劃]]★｜cochange proxy對圖譜related面太稀(兩vault實證,僅sanity check)｜hook接線v1.1待評測
    21	  DEP:[[Systems/lumos-cli-read]][[Systems/cochange-guard]]
    22	  TEST:t_tokenizer/search_ranked/context_recommend/impact_ranked/impact_diff/impact_hook_v11 全綠+全套1018 | VERIFY:[[Verification/2026-07-11_hook面v1.1轉正]] | VERIFY:[[Verification/2026-07-10_檢索排序v1]][[Verification/2026-07-11_檢索goldset評測]]
    23	related:
    24	  - "[[Projects/檢索優化_計劃]]"
    25	  - "[[Systems/lumos-cli-read]]"
    26	  - "[[Projects/節點靜態先驗_調研]]"
    27	  - "[[Projects/檢索多詞回退_計劃]]"
    28	verified_by:
docs/lumos-toolchain-knowledge/Systems/節點還原.md
     1	---
     2	type: system
     3	status: doing
     4	created: 2026-08-24
     5	updated: 2026-08-24
     6	self_audit: sonnet/2026-08-30
     7	aliases: []
     8	about_code: []
     9	tags:
    10	  - type/system
    11	  - status/doing
    12	  - scope/node-content
    13	summary: |-
    14	  FLOW:進場三分岔(search 有→照慣例用/殘缺→diff 補/沒有→產)→七步:init 填骨架 MOC(假設經營+對帳)→錨點階梯定位(字串→識別子→結構文件→動態差分)→兩來源圈承重牆→git+非 git 考古 why(每句標身分)→落節點蓋 regen 章(why 走 DECISION 行)→合約候選不升格→出口=指針級機械核對+變體 B 雙 Sonnet 交叉審計+雙軌留痕(Verification+verified_by+self-audit)
    15	  KEY:哲學=惰性生長(需要才產、有就照慣例用,絕不整倉攤平——Strangler fig 同構);典型觸發=新功能開發前先還原關聯面,產出(共用面+合約候選)=新功能 spec 的護欄素材
    16	  KEY:與重生守衛(Check J)的分工——守衛管「重建不准瞎編」(輸出端),本 SOP 管「產出」(建哪些/從哪開始/多深算夠);機械把關真實範圍=只掃 summary、J-a/b/c 硬擋、J-d 提醒、prose 靠交叉審計
    17	  KEY:操作全文在 skill reference〈節點還原(brownfield 冷啟動)〉(單一權威);快查表 commands/09;探針 s21–s23;README §6 門面
    18	  DEP:[[Systems/check-j-regen-guard]]｜[[Projects/節點還原SOP_計劃]]｜[[Systems/外部對照-code衍生wiki]]
    19	verified_by:
    20	  - "[[Verification/2026-08-24_節點還原SOP落地]]"
    21	---
    22	# 節點還原
    23	
    24	> 白話:接手一個跑了很久、圖譜是空的專案,怎麼把「這塊 code 為什麼長這樣、誰共用它、動了會壞什麼」還原成節點——七步流程,任何技術棧。本節點只記機制脈絡與指針;**操作全文的單一權威在 skill 的 reference〈節點還原(brownfield 冷啟動)〉**,設計理由與六輪 30 席 153 條的審計史在 [[Projects/節點還原SOP_計劃]]。
    25	
    26	## 這塊拼圖補什麼
    27	
    28	[[Systems/外部對照-code衍生wiki]] 早就承認:冷啟動整個陌生 repo 是 lumos 的弱項(對手 openwiki 的強項)。但 openwiki 式的全倉攤平=無查核的合成敘事。本 SOP 的賭注:**惰性還原**——跟著任務走、每句 why 標出處、出口過雙 agent 交叉查核,寧可慢也不編。守衛端([[Systems/check-j-regen-guard]])早已存在,本案補的是產出端(建哪些、從哪開始、多深算夠)加上索引路由(此前 commands/ 索引查「重建」零命中)。
docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md
     1	---
     2	type: system
     3	status: done
     4	created: 2026-07-16
     5	updated: 2026-07-16
     6	self_audit: sonnet/2026-07-16
     7	about_code_stamp: batch-2026-08-23/2026-08-23/a166e4e4681a
     8	tags:
     9	  - type/system
    10	  - status/done
    11	  - risk/守衛面
    12	  - scope/node-content
    13	related:
    14	  - "[[Systems/check-t-sentinel]]"
    15	  - "[[Systems/lumos-refcheck]]"
    16	  - "[[Systems/外部對照-code衍生wiki]]"
    17	plan_refs:
    18	  - "[[Projects/from-scratch重生守衛_計劃]]"
    19	verified_by:
    20	  - "[[Verification/2026-07-16_fromscratch守衛M1_CheckJ]]"
    21	summary: |-
    22	  FLOW:重建節點 → lumos set regen from-scratch/日期 蓋章 → summary 逐 claim 標身分([src:]/[git:]/推測:/佚失:) → lint/doctor 共用 check_regen_provenance 執法 → 查證後補證據或 signoff 升級
    23	  KEY:解 from-scratch 重生塌陷——重建=從 code 快照逆向工程 why,AI 會編自信假 why/假合約;Check J 逼每條 claim 亮身分:有證據(且機械驗真)/推測/佚失 三選一,把「不知道」留成「不知道」(anti code-衍生wiki 原罪,見 [[Systems/外部對照-code衍生wiki]])
    24	  KEY:J-a 拒發明合約(regen 節點 INVARIANT 標記行需 [src:]/[git:] 意圖證據,與 Check T [test:] 疊加——test 證行為,src/git 證意圖)｜J-b DECISION 四態(證據/推測/佚失/裸→擋)｜J-c substring gate(_validate_repo_ref 直驗+token 消毒:空/絕對/.. traversal 皆 missing;git cat-file;shallow 降 warn 顯性+僅 --ci 落帳)｜J-d 無標記 KEY 行唯讀提醒
    25	  KEY:共用 check_regen_provenance(note,repo_root)->(errs,warns,gov_events),lint 與 doctor 同函式防兩入口漂移;映射:errs→lint rc1/doctor warn(hard),warns→兩入口皆非阻擋,gov_events→僅 doctor --ci;雙報消歧 predicate=regen 節點推測+INVARIANT 同行恰一則 J 訊息、非 regen generic 兜底
    26	  KEY:★DEBT★ 宣告制 opt-in——不蓋 regen 章完全繞過 Check J,且繞過無留痕、無 Check H 式軟提醒對應;「疑似重生未標」自動偵測留未來
    27	  KEY:天花板——J-c 只驗指針可解析,不驗內容真支持 claim(語意層留 M2 對抗審/人);佚失的 why 永久佚失,正確輸出是佚失標記非編造
    28	  DEP:[[Systems/lumos-refcheck]]｜[[Systems/check-t-sentinel]]

[35m[3mexec[0m[0m
[1m/bin/zsh -lc "rg -n '"'^def _impact_reverse_lookup|''^def _impact_mark_about|''^def _nodehome_homes|''^def _nodehome_key|LUMOS_IMPACT_ABOUT_MAX|restamp|migrate-stamp|dispatch-lens|add_argument'"\\(\"--ranked\"|add_argument\\(\"--file\"|add_argument\\(\"--diff\"' scripts/lumos | head -120 && test -f docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md && test -f docs/lumos-toolchain-knowledge/Projects/每支檔有家_計劃.md && test -f docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md && test -f docs/lumos-toolchain-knowledge/Systems/節點還原.md && test -f docs/lumos-toolchain-knowledge/Systems/check-j-regen-guard.md && echo 'crossrefs: all present'"[0m in /Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh
[32m succeeded in 0ms:[0m
1410:    #   受總開關 LUMOS_IMPACT_ABOUT(0=整段略過,s1f6:只關一半等於沒關)。訊息先叫人看標籤對不對,restamp 不是萬靈丹(Codex r3 f1)。
1434:                       "先看這篇的 about_code 對現在的正文還對不對:對 → `lumos about-code restamp <節點>`;不對 → set/append/remove 修完再 restamp")
1438:                       "批次預標的跑一次 `lumos about-code migrate-stamp --at <標註當時 commit>`;單篇核過就 `lumos about-code restamp <節點>`")
3594:    cfg 給了(dict)就不讀磁碟——dispatch-lens v1.2 用 base 版設定(_json_at_ref)呼叫;None=舊路徑。"""
10995:    鎖檔放 ~/.cache/lumos/vault-lock/(照 dispatch-lens 快取的先例:不放共用暫存目錄——路徑可預測、會被別的使用者先佔)。
11330:    """正文雜湊的唯一公式(note_body_hash 讀現在的檔、migrate-stamp 讀 git show 的舊檔,兩者共用)。"""
11356:def cmd_about_code_restamp(env, rel, by="claude"):
11357:    """★restamp = 「我剛核過這篇的 about_code 對現在的正文仍然正確」★(工具清單 #11,std-r3 釘語意)。
11379:        print(f"擋下:{rel} 沒有 about_code,沒東西可核。先 lumos append <節點> about_code <檔> 再 restamp。", file=sys.stderr)
11389:        print(f"✓ restamp {rel}:about_code_stamp = {stamp}(表示你核過標籤對現在的正文仍正確)")
11414:        print(f"✓ migrate-stamp:0 篇要補(batch-* 兩段式的都補過了)")
11435:    print(f"✓ migrate-stamp(@{at_commit[:8]}):補了 {done} 篇{tail};之後跑 lumos doctor 看哪些「標完之後正文改過」要人核")
13527:    "scripts/hooks/claude/dispatch-lens-hook.py",
14295:_GLOBAL_CLAUDE_HOOKS = ("check-graph-sync.py", "impact-hook.py", "ci-status-hook.py", "lumos-entry-hook.py", "dispatch-lens-hook.py",
14906:    "scripts/hooks/claude/dispatch-lens-hook.py",   # 2026-09-03 派工鏡頭注入:會改寫子代理派工詞的 hook,硬約束進錨點
16031:                          ("pretooluse-dispatch-lens-hook", "dispatch-lens-hook.py")):
16072:                          ("codex-subagentstart-dispatch-lens-hook", "dispatch-lens-hook.py")):
17988:def _nodehome_key(value):
17995:def _nodehome_homes(repo_root, side):
18309:        many = int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8))
18632:    if _given is not None or p.exists():   # cfg 給了(dict)就不讀磁碟(dispatch-lens v1.2 base 版設定);型別守衛與 min_support 底線照走
20958:def _impact_reverse_lookup(rel_code_path, env, repo_root):
21269:def _impact_mark_about(env, results, rel_file):
21272:    總開關 LUMOS_IMPACT_ABOUT(預設 1;0=整段不跑、不讀正文);巨檔門檻 LUMOS_IMPACT_ABOUT_MAX(預設 8):
21280:    if counts.get(target, 0) >= int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8)):
21818:    # ★擁有權要驗,理由跟 dispatch-lens 那支快取一模一樣★
21824:    #   dispatch-lens 那支是「跨呼叫、可被別人發現、要 TTL、要 key 去對」的快取;
22023:# dispatch-lens(Projects/派工鏡頭注入_計劃,2026-09-03):代碼審派工詞的固定席鏡頭
22024:# hook 是薄殼(scripts/hooks/claude/dispatch-lens-hook.py),所有 git/合約/圖譜判斷都在這裡,
22103:    return Path.home() / ".cache" / "lumos" / "dispatch-lens" / f"{key}.json"
22127:        if not _trusted_private_dir(path.parent, ".cache", "lumos", "dispatch-lens"):
22383:# 所以範圍由編排者「派工前一刻」武裝:算好鏡頭文字落 ~/.cache/lumos/dispatch-lens/armed/<key>/,
22433:    return Path.home() / ".cache" / "lumos" / "dispatch-lens" / "armed"
22513:    return _trusted_private_dir(d, ".cache", "lumos", "dispatch-lens", "armed", Path(d).name)
22572:    print("  派完(或不派了)收掉:\n    lumos dispatch-lens --disarm")
22667:        print("(武裝檔壞了;lumos dispatch-lens --disarm 收掉)")
22722:    (dispatch-lens 的「同範圍只讓一個在算」與筆記庫寫入鎖 _vault_write_lock 共用;2026-09-10 從 dispatch-lens 抽出來)。
22785:        argv = [sys.executable, os.path.abspath(__file__), "dispatch-lens", diff_range,
22826:        print(f"      lumos dispatch-lens {diff_range}")
25327:    "about-code": "語意「關於」欄位 about_code 的操作:revert 整批撤、restamp 核過後重標、migrate-stamp 一次性補雜湊。",
25328:    "about-code revert": "預標標錯一整批時,按批次日期整批撤掉(stamp 第一段 batch-<日期>);人工修正過或 restamp 過的不動。先 --dry-run 看會撤哪些。",
25329:    "about-code restamp": "doctor 說某篇 about_code 可能過期、你看過標籤對現在的正文仍然對 → 用這個重標(三段全換);標籤不對就先 set/append/remove 修完再 restamp。",
25330:    "about-code migrate-stamp": "只跑一次:把批次預標的兩段式 stamp 補上第三段(用標註當時那個 commit 的正文算),之後 doctor 才量得出哪些標完又改過。",
25362:    "dispatch-lens": "代碼審派工詞的固定席鏡頭:Claude 側 hook 自動叫;Codex 編排時派工前一刻敲 `--arm <base>..<head> --seats N`(子代理開場各領一席,10 分 TTL),派完 `--disarm`。手動看內容給 <base>..<head>(從 base 讀、零自由文字;base 不在主線→rc4 放行)。",
25535:    acs = acsub.add_parser("restamp", help="核過這篇 about_code 對現在正文仍正確 → stamp 三段全換 <by>/<今天>/<正文雜湊>;沒有批次模式")
25538:    acm = acsub.add_parser("migrate-stamp", help="一次性:batch-* 兩段式 stamp 用「標註當時 commit」的正文補第三段雜湊")
25721:    gka.add_argument("--file", required=True, help="要弄壞的檔(相對配方平台 root)")
25752:    p.add_argument("--ranked", action="store_true", help="BM25F 相關性排序(2026-07-11 起已是預設,旗標保留相容)")
25940:    p = sub.add_parser("dispatch-lens", help="代碼審派工詞的固定席鏡頭:把 <base>..<head> 碰到的合約/事故節點整理成可附進派工詞的純文字(hook 用;內容從 base 讀,零自由文字)")
25954:    p.add_argument("--file", dest="impact_file", help="被改動的 code 檔路徑(單檔模式;與 --diff/--node 三擇一)")
25956:    p.add_argument("--diff", dest="impact_diff", help="diff range(如 main..HEAD):聚合各改動檔的 ranked impact 成受影響功能面 manifest(code-loop 審計鏡頭)")
25966:    p.add_argument("--ranked", action="store_true", dest="impact_ranked", help="融合排序+固定席+降噪(dormant v1)")
25974:    p.add_argument("--diff", dest="pf_diff", help="diff range(如 main..HEAD;diff 模式)")
26002:    tma.add_argument("--diff", dest="tm_diff", default=None)
26006:    p.add_argument("--diff", dest="tl_diff", help="diff range(如 main..HEAD)")
26076:    ccc.add_argument("--diff", dest="coch_diff", default=None, metavar="A..B",
26085:    hmc.add_argument("--diff", dest="hm_diff", default=None, metavar="A..B", help="把範圍兩端當成一次改動比(推送前用);不能跟 --staged 一起用")
26117:            _clp.add_argument("--diff", dest="cl_diff", default=None,
26136:    bt.add_argument("--diff", dest="bt_diff", default=None, help="diff 範圍 <A..B>")
26192:    if args.cmd == "dispatch-lens":
26388:        if args.accmd == "restamp":
26389:            return cmd_about_code_restamp(env, args.node, by=args.by)
26390:        if args.accmd == "migrate-stamp":
crossrefs: all present

[35m[3mcodex[0m[0m
severity: major

### F1 「每支檔至少一個家」沒有滿足舊案的漏標歸零條件
severity: major
blocking: 是 — 不改，實作者會用不同母體的證據重啟已被明確凍結的第四入口。
引句:「新證據:[[Projects/每支檔有家_計劃]](2026-09-11 上線)讓新增的程式檔提交當下一定有家、原本有家的檔變沒家會擋」
1. file: `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:35` d4 要求壓低的是 about 漏標率；file: `scripts/lumos:17995` 新證據只保證每支檔至少有一篇特定狀態的 Systems 節點。
2. file: `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:534` 舊調研的 31 組自由席必看全是 Projects／Verification，且同檔第 545 行明載 about_hit 動不到它們，因此新證據沒有量到舊決策要求的母體。

### F2 home-only 候選沒有可執行的 kind、score 與分桶定義
severity: major
blocking: 是 — 不改，實作者必須自行發明分數或冒充既有 candidate kind，直接改壞排序與保底語意。
引句:「大檔不整批進必推:只有帶合約的家進必推,其餘家在可選名單照分數競爭」
1. file: `scripts/lumos:21590` 現有結果只會建出 incident、direct、indirect，分數與 L／G 也只在這三條路徑產生；file: `scripts/lumos:21743` 顯示端同樣只認這三種 kind。
2. file: `scripts/lumos:21689` 若把 home-only 冒充 direct，它會進直連水位保底；若新增 kind，分數、動態門檻、renderer 與 evaluator 都沒有定義，與「不改分數公式」無法同時實作。

### F3 dispatch-lens 的 spec 路徑不會自然取得 ranked homes
severity: major
blocking: 是 — 不改，實作者照 S2 改 ranked impact 後仍會留下設計審鏡頭漏家。
引句:「派審查員時的圖譜參考(dispatch-lens 的 diff 與 spec 兩種)也認家」
1. file: `scripts/lumos:23116` spec 鏡頭刻意呼叫未帶 `--ranked` 的 `impact --file --json`；file: `scripts/lumos:23121` 隨後只解析 direct、incidents、帶合約的一跳 indirect。
2. home-only 節點不在該 JSON 三集合內，spec 未定義改成 ranked schema還是另做 home lookup，現有測試名稱也沒有釘住這項接線決策。

### F4 多檔 diff 聚合沒有保留 home 身分與順序的資料模型
severity: major
blocking: 是 — 不改，同一節點跨檔合併後會丟失「是哪支檔的家」，無法兌現 S6 的順序。
引句:「推送前的波及計算(`impact --diff`)聚合時保留家的入口與順序」
1. file: `scripts/lumos:21935` 聚合只保留最高分整筆資料並對 pinned 做 OR；file: `scripts/lumos:21948` 最後固定席全部改按 `(-score,node)` 排序。
2. 當節點對 A 是家、對 B 是較高分非家時，勝出記錄會抹掉 home provenance；spec 未定義 `home_for_files`、跨檔優先序或 incident／home 衝突規則。

### F5 關閉 HOME 旋鈕不能按目前裁定完整回到舊行為
severity: major
blocking: 是 — 不改，回滾開關關掉新入口後，舊 about 排序與顯示仍回不來。
引句:「新增旋鈕 `LUMOS_IMPACT_HOME`(預設 1;0=完全照原本)」
1. file: `scripts/lumos:21269` 舊行為會驗 stamp 後標 about_hit；file: `scripts/lumos:21659` 舊固定席再按 about_hit 排序；file: `scripts/hooks/claude/impact-hook.py:646` 舊 hook 會顯示該標記。
2. S3、S8、S9 卻全域取代排序、移除標示並讓 stamp 不再影響推筆記，沒有規定這三項也受 `LUMOS_IMPACT_HOME=0` 條件控制。

### F6 現有 about 快取與「家」不是同一個集合
severity: major
blocking: 是 — 不改，大檔門檻會被非家節點誤觸發，或熱路徑被迫再掃一套 git 快照。
引句:「找家要掃全圖的 about_code——既有的 about 計數已經有快取,本案沿用,不另掃一次」
1. file: `scripts/lumos:21250` 現有快取掃全部 `env.notes`，不過濾 type／status，鍵也只走 `_posix_norm`。
2. file: `scripts/lumos:17995` 真正的 home helper 只收 Systems 的 doing／done／stale 並走 `_nodehome_key`，而其輸入是 `_NodehomeSide` git 快照，不是 impact 的 `Env`。
3. 直接沿用快取會把 Issues／Projects／非有效狀態筆記計入「家數 ≥8」；直接沿用 helper 則違反「不另掃一次」，S1 與效能裁定目前互斥。

### F7 驗收沒有對新增 home candidates 做未標候選的 fail-closed
severity: major
blocking: 是 — 不改，實作者會用未標節點污染的 P@8／top3 數字作上線判斷。
引句:「評測:用既有評測器跑練習題與保留題」
1. file: `governance/eval/retrieval_eval.py:438` P@8 只量 free bucket，而 file: `governance/eval/retrieval_eval.py:475` 未標的新固定席被直接當噪音與 top3 非必看。
2. file: `governance/eval/retrieval_eval.py:751` 只有 `--ablation` 會因未標候選 fail-closed，spec 第 95 行的兩條驗收命令都未帶它，也沒有先 refresh／repin labels。
3. home-only 節點加入或既有 free 節點改成 pinned 時，兩把尺的母體同時改變；只比較輸出百分比不能證明不退步。

### F8 三份既有 pass 驗證會被本案直接失效，落點卻未處理
severity: major
blocking: 是 — 不改，圖譜會同時保留互相矛盾的 pass 背書。
引句:「前後數字寫進驗證紀錄」
1. file: `docs/lumos-toolchain-knowledge/Verification/2026-07-10_檢索排序v1.md:7` 固定席定義屬 valid_under；file: `docs/lumos-toolchain-knowledge/Verification/2026-07-11_檢索goldset評測.md:5` 背書現行 edit 評測母體；file: `docs/lumos-toolchain-knowledge/Verification/2026-08-24_about_code讀側四項落地.md:33` 明確驗過即將被移除的 about 排序與標示。
2. spec 只要求新增驗證紀錄，沒有把這三篇標 stale、superseded 或逐篇重驗，尤其 2026-08-24 那篇會在上線後仍以 status pass 宣稱相反行為。

### F9 舊專案相容性只回答「不更新」，沒有回答正常更新後的硬擋
severity: major
blocking: 是 — 不改，更新工具後第一次修改既有 regen 節點的消費專案會遇到未規劃的提交阻斷。
引句:「舊專案沒更新:沒跑 `lumos update` 的專案照舊行為,不會壞」
1. file: `scripts/lumos:4368` 現有 lint 已把任何非空 regen 視為重建節點；file: `scripts/hooks/pre-commit:91` 所有 staged 圖譜節點都會逐篇 lint 並以 rc 非零擋提交。
2. S11 加入後，更新過的舊專案只要修改一篇既有且缺 about_code 的 regen 節點就會被擋，spec 沒有盤點命令、backfill、grandfather cutoff 或更新提示。

### F10 驗收漏掉錨點重新核可
severity: minor
blocking: 否 — 不改，實作者通常會在 pre-push 才被既有守衛攔下，不會直接產出壞系統。
引句:「子集:`python3 scripts/test_lumos.py -k impact_home`、`-k impact_pins_order`、`-k dispatch_lens_includes_homes`」
1. file: `scripts/lumos:14900` `scripts/test_lumos.py`、`dispatch-lens-hook.py`、`impact-hook.py` 都是 anchor files；file: `docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md:19` 修改後須走 `anchor approve --note` 並由 verify 比對。
2. S8 與新增測試至少會改到其中兩支錨點，但驗收清單沒有 anchor approve／verify，交付步驟不完整。

### F11 hook 標頭會把非合約家誤稱為合約或事故
severity: major
blocking: 是 — 不改，agent 會把結構化 ownership 誤讀成不可破壞的合約。
引句:「顯示:Edit 前推筆記的清單上」
1. file: `scripts/hooks/claude/impact-hook.py:630` 現行 renderer 把所有 pinned 項放在同一桶，file: `scripts/hooks/claude/impact-hook.py:641` 標頭宣稱每篇都帶不能破壞的合約或出過事故。
2. S2 允許普通、無合約的小檔家進 pinned，S8 只裁定換行首標籤，沒有要求同步改寫桶標頭與信任語意。

## 逐節覆核

1. frontmatter、summary、白話摘要：已讀，F1。
2. 「為什麼」：已讀，F1；PRIOR-ART 本身無新增 finding。
3. 「名詞」：已讀，F2、F6。
4. 「核心裁定／甲」：已讀，F2–F8、F11。
5. 「核心裁定／乙」：已讀，F9。
6. 「範圍外」：已讀,無 finding。
7. 「落點」：已讀，F8。
8. 「實務隱患」：已讀，F5、F6、F9。
9. 「驗收怎麼跑」：已讀，F7、F10。
10. 「回頭條件」：已讀,無 finding；週清單實作存在於 `governance/autonomous_loop/lens_weekly.py:2` 與 `governance/eval/lens-utilization/recount.py:448`。
11. 「合約候選」：已讀，候選文字本身無新增 finding，但 S2/S4 尚受 F2 阻斷。
12. 「審計修正紀錄」：已讀,無 finding。

## 交叉引用與現況查核

1. 五個 wikilink 目標 `固定席扇出降權_計劃`、`每支檔有家_計劃`、`retrieval-ranking`、`節點還原`、`check-j-regen-guard` 均存在。
2. `_impact_reverse_lookup`、`_impact_mark_about`、`_nodehome_homes`、`_nodehome_key` 均存在；`LUMOS_IMPACT_ABOUT_MAX` 現行預設確為 8。
3. `impact --file/--ranked/--diff`、`dispatch-lens --spec`、`lint`、`new system --code`、`about-code restamp/revert/migrate-stamp` 均存在；`LUMOS_IMPACT_HOME` 是 spec 明載的新項，不列未定義。
4. commands/09 與 reference 的節點還原第 4 步及 `--code` 路徑存在，未發現壞交叉引用。

## 固定席逐條判

1. `Systems/retrieval-ranking`：會影響；固定席來源、排序、輸出母體與 about 行為全被改寫，F2、F4、F5、F7、F11 未折前不能維持其行為敘述。
2. `Systems/節點還原`：不影響其既有七步流程與合約；乙案只加強第 4、6 步出口。
3. `Systems/check-j-regen-guard`：不破壞既有 provenance 守衛；S11 增加正交欄位檢查，宣告制 opt-in 天花板仍由 S88 保留。
4. `Issues/canary-record未落盤事件`：不影響，沒有改 canary 寫入、鎖或治理帳落盤。
5. `Issues/code-loop守衛main-direct盲區`：不影響，沒有改 code-loop 的 main/direct 範圍判定。
6. `Issues/hook卸載殘留註冊`：不影響其卸載殘留機制，S8 只改既有 hook 顯示內容。
7. `Issues/init-force-slug誤用basename`：不影響，沒有改 init、force 或 slug 推導。
8. `Issues/vendored測試套件在消費端假紅`：不影響，沒有改 vendored 偵測或消費端測試選擇。
9. `Systems/known-pitfall-refresh-token`：不影響，沒有改坑單刷新或 token。
10. `Systems/lumos-cli-read`：不影響其 search／superseded 讀取合約，變更限 impact。
11. `Systems/lumos-refcheck`：不影響 refcheck 抽取與驗證語意。
12. `Systems/anchor-integrity`：會影響，F10 漏了三支相關 anchor files 的核可流程。
13. `Systems/pitfalls-code-loop`：不影響，沒有改 pitfalls 分級、code-loop 或處置閘。
14. `Systems/測試假綠形態`：不直接破壞其 bug-fix 前置條件合約，但 F7 會讓評測結論失真。
15. `Systems/slim-install-安裝器`：不影響，沒有改安裝器的檔案範圍與專案不碰合約。
16. `Systems/slim-uninstall-一行卸載`：不影響，沒有改卸載清單或刪除範圍。
17. `Systems/design-loop`：不影響其審查流程；S1–S13 均有 test/manual 綁定，但本輪 findings 尚未處置。
18. `Systems/lumos-cli-lifecycle`：不破壞更新、注入與 sentinel 合約；更新後的消費端 lint 行為缺口另見 F9。
19. `Verification/2026-07-10_檢索排序v1`：會失效，其 valid_under 明載的固定席定義被改，見 F8。
20. `Verification/2026-07-11_檢索goldset評測`：會失效，pin/free 母體改變後既有 edit 評測背書不能原樣沿用，見 F7、F8。
21. `Verification/2026-08-24_about_code讀側四項落地`：會直接失效，其 pass 內容正是 S3、S8、S9 要移除的排序、stamp 與標示，見 F8。

## 實務隱患鏡頭

1. 效能：有，F6；熱路徑目前沒有一個同時符合 home 語意、工作樹視角與單次掃描的資料來源。
2. 噪音與召回：有，F1、F2、F7；S5 避免了舊 r1 的主動降級，但大檔 home 分數與評測母體仍未定義。
3. 平行路徑：有，F3、F4；單檔 ranked、diff 聚合與 dispatch-lens spec 目前使用不同 schema。
4. 舊專案相容：有，F9；未更新不壞不等於正常更新後不壞。
5. 回滾：有，F5；關掉 HOME 尚不能恢復 about 排序、stamp 判定與舊標示。
6. 可觀測性：有，F7、F8；推播漏網週清單已存在，但上線驗收與既有 pass 驗證的生命週期沒有閉合。
7. 分發與錨點：有，F10；功能會動到錨點檔，驗收未納入重新核可。
8. 資安、個資、金流、不可逆與對外寄送：無；本案只改本機讀側輸出、lint 與文件，不新增秘密處理、正式環境寫入或外送。

## 舊案重蹈判定

1. 沒有重蹈舊 r1 的直接傷害：S5 明確禁止因「不是家」降級既有事故、合約與反引號候選。
2. 有重蹈舊 r1 的證據錯置：舊案已裁定 about 是 must-see 的高精確度子集而非等價物，新案又把「每檔至少一個 Systems 家」說成舊母體的漏標歸零。
3. 因此演算法方向不同，但 d4 的重提門檻尚未被滿足，F1 折掉前不能以舊決策授權實作。

總結:最高 severity major,blocking 共 10 條
[2mtokens used[0m
369,279
severity: major

### F1 「每支檔至少一個家」沒有滿足舊案的漏標歸零條件
severity: major
blocking: 是 — 不改，實作者會用不同母體的證據重啟已被明確凍結的第四入口。
引句:「新證據:[[Projects/每支檔有家_計劃]](2026-09-11 上線)讓新增的程式檔提交當下一定有家、原本有家的檔變沒家會擋」
1. file: `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:35` d4 要求壓低的是 about 漏標率；file: `scripts/lumos:17995` 新證據只保證每支檔至少有一篇特定狀態的 Systems 節點。
2. file: `docs/lumos-toolchain-knowledge/Projects/固定席扇出降權_計劃.md:534` 舊調研的 31 組自由席必看全是 Projects／Verification，且同檔第 545 行明載 about_hit 動不到它們，因此新證據沒有量到舊決策要求的母體。

### F2 home-only 候選沒有可執行的 kind、score 與分桶定義
severity: major
blocking: 是 — 不改，實作者必須自行發明分數或冒充既有 candidate kind，直接改壞排序與保底語意。
引句:「大檔不整批進必推:只有帶合約的家進必推,其餘家在可選名單照分數競爭」
1. file: `scripts/lumos:21590` 現有結果只會建出 incident、direct、indirect，分數與 L／G 也只在這三條路徑產生；file: `scripts/lumos:21743` 顯示端同樣只認這三種 kind。
2. file: `scripts/lumos:21689` 若把 home-only 冒充 direct，它會進直連水位保底；若新增 kind，分數、動態門檻、renderer 與 evaluator 都沒有定義，與「不改分數公式」無法同時實作。

### F3 dispatch-lens 的 spec 路徑不會自然取得 ranked homes
severity: major
blocking: 是 — 不改，實作者照 S2 改 ranked impact 後仍會留下設計審鏡頭漏家。
引句:「派審查員時的圖譜參考(dispatch-lens 的 diff 與 spec 兩種)也認家」
1. file: `scripts/lumos:23116` spec 鏡頭刻意呼叫未帶 `--ranked` 的 `impact --file --json`；file: `scripts/lumos:23121` 隨後只解析 direct、incidents、帶合約的一跳 indirect。
2. home-only 節點不在該 JSON 三集合內，spec 未定義改成 ranked schema還是另做 home lookup，現有測試名稱也沒有釘住這項接線決策。

### F4 多檔 diff 聚合沒有保留 home 身分與順序的資料模型
severity: major
blocking: 是 — 不改，同一節點跨檔合併後會丟失「是哪支檔的家」，無法兌現 S6 的順序。
引句:「推送前的波及計算(`impact --diff`)聚合時保留家的入口與順序」
1. file: `scripts/lumos:21935` 聚合只保留最高分整筆資料並對 pinned 做 OR；file: `scripts/lumos:21948` 最後固定席全部改按 `(-score,node)` 排序。
2. 當節點對 A 是家、對 B 是較高分非家時，勝出記錄會抹掉 home provenance；spec 未定義 `home_for_files`、跨檔優先序或 incident／home 衝突規則。

### F5 關閉 HOME 旋鈕不能按目前裁定完整回到舊行為
severity: major
blocking: 是 — 不改，回滾開關關掉新入口後，舊 about 排序與顯示仍回不來。
引句:「新增旋鈕 `LUMOS_IMPACT_HOME`(預設 1;0=完全照原本)」
1. file: `scripts/lumos:21269` 舊行為會驗 stamp 後標 about_hit；file: `scripts/lumos:21659` 舊固定席再按 about_hit 排序；file: `scripts/hooks/claude/impact-hook.py:646` 舊 hook 會顯示該標記。
2. S3、S8、S9 卻全域取代排序、移除標示並讓 stamp 不再影響推筆記，沒有規定這三項也受 `LUMOS_IMPACT_HOME=0` 條件控制。

### F6 現有 about 快取與「家」不是同一個集合
severity: major
blocking: 是 — 不改，大檔門檻會被非家節點誤觸發，或熱路徑被迫再掃一套 git 快照。
引句:「找家要掃全圖的 about_code——既有的 about 計數已經有快取,本案沿用,不另掃一次」
1. file: `scripts/lumos:21250` 現有快取掃全部 `env.notes`，不過濾 type／status，鍵也只走 `_posix_norm`。
2. file: `scripts/lumos:17995` 真正的 home helper 只收 Systems 的 doing／done／stale 並走 `_nodehome_key`，而其輸入是 `_NodehomeSide` git 快照，不是 impact 的 `Env`。
3. 直接沿用快取會把 Issues／Projects／非有效狀態筆記計入「家數 ≥8」；直接沿用 helper 則違反「不另掃一次」，S1 與效能裁定目前互斥。

### F7 驗收沒有對新增 home candidates 做未標候選的 fail-closed
severity: major
blocking: 是 — 不改，實作者會用未標節點污染的 P@8／top3 數字作上線判斷。
引句:「評測:用既有評測器跑練習題與保留題」
1. file: `governance/eval/retrieval_eval.py:438` P@8 只量 free bucket，而 file: `governance/eval/retrieval_eval.py:475` 未標的新固定席被直接當噪音與 top3 非必看。
2. file: `governance/eval/retrieval_eval.py:751` 只有 `--ablation` 會因未標候選 fail-closed，spec 第 95 行的兩條驗收命令都未帶它，也沒有先 refresh／repin labels。
3. home-only 節點加入或既有 free 節點改成 pinned 時，兩把尺的母體同時改變；只比較輸出百分比不能證明不退步。

### F8 三份既有 pass 驗證會被本案直接失效，落點卻未處理
severity: major
blocking: 是 — 不改，圖譜會同時保留互相矛盾的 pass 背書。
引句:「前後數字寫進驗證紀錄」
1. file: `docs/lumos-toolchain-knowledge/Verification/2026-07-10_檢索排序v1.md:7` 固定席定義屬 valid_under；file: `docs/lumos-toolchain-knowledge/Verification/2026-07-11_檢索goldset評測.md:5` 背書現行 edit 評測母體；file: `docs/lumos-toolchain-knowledge/Verification/2026-08-24_about_code讀側四項落地.md:33` 明確驗過即將被移除的 about 排序與標示。
2. spec 只要求新增驗證紀錄，沒有把這三篇標 stale、superseded 或逐篇重驗，尤其 2026-08-24 那篇會在上線後仍以 status pass 宣稱相反行為。

### F9 舊專案相容性只回答「不更新」，沒有回答正常更新後的硬擋
severity: major
blocking: 是 — 不改，更新工具後第一次修改既有 regen 節點的消費專案會遇到未規劃的提交阻斷。
引句:「舊專案沒更新:沒跑 `lumos update` 的專案照舊行為,不會壞」
1. file: `scripts/lumos:4368` 現有 lint 已把任何非空 regen 視為重建節點；file: `scripts/hooks/pre-commit:91` 所有 staged 圖譜節點都會逐篇 lint 並以 rc 非零擋提交。
2. S11 加入後，更新過的舊專案只要修改一篇既有且缺 about_code 的 regen 節點就會被擋，spec 沒有盤點命令、backfill、grandfather cutoff 或更新提示。

### F10 驗收漏掉錨點重新核可
severity: minor
blocking: 否 — 不改，實作者通常會在 pre-push 才被既有守衛攔下，不會直接產出壞系統。
引句:「子集:`python3 scripts/test_lumos.py -k impact_home`、`-k impact_pins_order`、`-k dispatch_lens_includes_homes`」
1. file: `scripts/lumos:14900` `scripts/test_lumos.py`、`dispatch-lens-hook.py`、`impact-hook.py` 都是 anchor files；file: `docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md:19` 修改後須走 `anchor approve --note` 並由 verify 比對。
2. S8 與新增測試至少會改到其中兩支錨點，但驗收清單沒有 anchor approve／verify，交付步驟不完整。

### F11 hook 標頭會把非合約家誤稱為合約或事故
severity: major
blocking: 是 — 不改，agent 會把結構化 ownership 誤讀成不可破壞的合約。
引句:「顯示:Edit 前推筆記的清單上」
1. file: `scripts/hooks/claude/impact-hook.py:630` 現行 renderer 把所有 pinned 項放在同一桶，file: `scripts/hooks/claude/impact-hook.py:641` 標頭宣稱每篇都帶不能破壞的合約或出過事故。
2. S2 允許普通、無合約的小檔家進 pinned，S8 只裁定換行首標籤，沒有要求同步改寫桶標頭與信任語意。

## 逐節覆核

1. frontmatter、summary、白話摘要：已讀，F1。
2. 「為什麼」：已讀，F1；PRIOR-ART 本身無新增 finding。
3. 「名詞」：已讀，F2、F6。
4. 「核心裁定／甲」：已讀，F2–F8、F11。
5. 「核心裁定／乙」：已讀，F9。
6. 「範圍外」：已讀,無 finding。
7. 「落點」：已讀，F8。
8. 「實務隱患」：已讀，F5、F6、F9。
9. 「驗收怎麼跑」：已讀，F7、F10。
10. 「回頭條件」：已讀,無 finding；週清單實作存在於 `governance/autonomous_loop/lens_weekly.py:2` 與 `governance/eval/lens-utilization/recount.py:448`。
11. 「合約候選」：已讀，候選文字本身無新增 finding，但 S2/S4 尚受 F2 阻斷。
12. 「審計修正紀錄」：已讀,無 finding。

## 交叉引用與現況查核

1. 五個 wikilink 目標 `固定席扇出降權_計劃`、`每支檔有家_計劃`、`retrieval-ranking`、`節點還原`、`check-j-regen-guard` 均存在。
2. `_impact_reverse_lookup`、`_impact_mark_about`、`_nodehome_homes`、`_nodehome_key` 均存在；`LUMOS_IMPACT_ABOUT_MAX` 現行預設確為 8。
3. `impact --file/--ranked/--diff`、`dispatch-lens --spec`、`lint`、`new system --code`、`about-code restamp/revert/migrate-stamp` 均存在；`LUMOS_IMPACT_HOME` 是 spec 明載的新項，不列未定義。
4. commands/09 與 reference 的節點還原第 4 步及 `--code` 路徑存在，未發現壞交叉引用。

## 固定席逐條判

1. `Systems/retrieval-ranking`：會影響；固定席來源、排序、輸出母體與 about 行為全被改寫，F2、F4、F5、F7、F11 未折前不能維持其行為敘述。
2. `Systems/節點還原`：不影響其既有七步流程與合約；乙案只加強第 4、6 步出口。
3. `Systems/check-j-regen-guard`：不破壞既有 provenance 守衛；S11 增加正交欄位檢查，宣告制 opt-in 天花板仍由 S88 保留。
4. `Issues/canary-record未落盤事件`：不影響，沒有改 canary 寫入、鎖或治理帳落盤。
5. `Issues/code-loop守衛main-direct盲區`：不影響，沒有改 code-loop 的 main/direct 範圍判定。
6. `Issues/hook卸載殘留註冊`：不影響其卸載殘留機制，S8 只改既有 hook 顯示內容。
7. `Issues/init-force-slug誤用basename`：不影響，沒有改 init、force 或 slug 推導。
8. `Issues/vendored測試套件在消費端假紅`：不影響，沒有改 vendored 偵測或消費端測試選擇。
9. `Systems/known-pitfall-refresh-token`：不影響，沒有改坑單刷新或 token。
10. `Systems/lumos-cli-read`：不影響其 search／superseded 讀取合約，變更限 impact。
11. `Systems/lumos-refcheck`：不影響 refcheck 抽取與驗證語意。
12. `Systems/anchor-integrity`：會影響，F10 漏了三支相關 anchor files 的核可流程。
13. `Systems/pitfalls-code-loop`：不影響，沒有改 pitfalls 分級、code-loop 或處置閘。
14. `Systems/測試假綠形態`：不直接破壞其 bug-fix 前置條件合約，但 F7 會讓評測結論失真。
15. `Systems/slim-install-安裝器`：不影響，沒有改安裝器的檔案範圍與專案不碰合約。
16. `Systems/slim-uninstall-一行卸載`：不影響，沒有改卸載清單或刪除範圍。
17. `Systems/design-loop`：不影響其審查流程；S1–S13 均有 test/manual 綁定，但本輪 findings 尚未處置。
18. `Systems/lumos-cli-lifecycle`：不破壞更新、注入與 sentinel 合約；更新後的消費端 lint 行為缺口另見 F9。
19. `Verification/2026-07-10_檢索排序v1`：會失效，其 valid_under 明載的固定席定義被改，見 F8。
20. `Verification/2026-07-11_檢索goldset評測`：會失效，pin/free 母體改變後既有 edit 評測背書不能原樣沿用，見 F7、F8。
21. `Verification/2026-08-24_about_code讀側四項落地`：會直接失效，其 pass 內容正是 S3、S8、S9 要移除的排序、stamp 與標示，見 F8。

## 實務隱患鏡頭

1. 效能：有，F6；熱路徑目前沒有一個同時符合 home 語意、工作樹視角與單次掃描的資料來源。
2. 噪音與召回：有，F1、F2、F7；S5 避免了舊 r1 的主動降級，但大檔 home 分數與評測母體仍未定義。
3. 平行路徑：有，F3、F4；單檔 ranked、diff 聚合與 dispatch-lens spec 目前使用不同 schema。
4. 舊專案相容：有，F9；未更新不壞不等於正常更新後不壞。
5. 回滾：有，F5；關掉 HOME 尚不能恢復 about 排序、stamp 判定與舊標示。
6. 可觀測性：有，F7、F8；推播漏網週清單已存在，但上線驗收與既有 pass 驗證的生命週期沒有閉合。
7. 分發與錨點：有，F10；功能會動到錨點檔，驗收未納入重新核可。
8. 資安、個資、金流、不可逆與對外寄送：無；本案只改本機讀側輸出、lint 與文件，不新增秘密處理、正式環境寫入或外送。

## 舊案重蹈判定

1. 沒有重蹈舊 r1 的直接傷害：S5 明確禁止因「不是家」降級既有事故、合約與反引號候選。
2. 有重蹈舊 r1 的證據錯置：舊案已裁定 about 是 must-see 的高精確度子集而非等價物，新案又把「每檔至少一個 Systems 家」說成舊母體的漏標歸零。
3. 因此演算法方向不同，但 d4 的重提門檻尚未被滿足，F1 折掉前不能以舊決策授權實作。

總結:最高 severity major,blocking 共 10 條
EXIT=0
