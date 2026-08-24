---
type: project
status: doing
created: 2026-08-24
updated: 2026-08-24
summary: |-
  FLAG:DECISION
  KEY:立案(2026-08-24 Enzo 開新任務)——「接手既有專案,把功能脈絡還原成圖譜節點」的 SOP。盤點確認缺口結構性:守衛半邊有(Check J/regen 章),產出半邊全空——無 SOP 文件、無「建哪些/從哪開始/多深算夠」指引;commands/ 子檔 grep regen 零命中(索引路由斷點);62 個 CLI 子指令無掃 repo 產節點者
  KEY:方案=七步 SOP(步驟 0–6,任何技術棧):填骨架導覽頁→錨點階梯定位→追流圈承重牆(grep+第二來源)→git+非 git 考古還原 why→落節點蓋 regen 章(why 走 DECISION 行接 J-b 硬擋)→合約候選不升格→出口=變體 B 交叉審計+self-audit 蓋章。種子=brownfield 影片五步,通用化+補驗證層
  KEY:四裁定——d1 任務驅動+最小骨架不攤平;d2 指針級快寫/why 級逐句標身分;d3 第一版純文件層不建 CLI;d4 放置=全文進 reference.md、commands/09 薄查表(08 已佔用,「八類」三處同步改九類)
  KEY:★r1 審計(2026-08-24,5 席)實錘要點★:Check J 只掃 summary、KEY 行只提醒不擋、FLOW/DEP 零檢查——「機械防瞎編」宣稱降級為「合約級硬擋+其餘靠交叉審計」;蓋章半成品機械全綠是已知中間態;冷啟動=code-only 重建,openwiki 節點裁的「圖譜史底料」緩解在本場景結構性缺席,補償=雙 agent 交叉審計(16.3% 不一致率教訓)
  DEP:[[Systems/check-j-regen-guard]]｜[[Systems/外部對照-code衍生wiki]]｜[[Projects/from-scratch重生守衛_計劃]]
plan_refs: []
related:
  - "[[Systems/check-j-regen-guard]]"
  - "[[Systems/外部對照-code衍生wiki]]"
  - "[[Projects/from-scratch重生守衛_計劃]]"
tags:
  - type/project
  - status/doing
decisions:
  - content: SOP 預設任務驅動:還原跟著「這次要動哪裡」走;第一天只建一篇最小骨架 MOC(純指針),不整倉攤平
    id: d1
    context: openwiki 對照節點已裁「圖譜只長在動過的地方」是家規非缺陷;全倉攤平=無 oracle 的大量合成敘事=openwiki 失效模式;影片流程本身也是任務驅動。另一選項①全倉掃描攤平:排除,理由如上;②純任務驅動零骨架:排除,第一天連錨點都找不到,一篇指針 MOC 錯得便宜
    why_chosen: 指針層便宜安全可先鋪;why 層跟著任務走才有還原品質。代價:冷啟動覆蓋率永遠輸 openwiki 式工具——接受,那是刻意不搶的地盤
    decided: 2026-08-24
    valid: true
  - content: 還原產出一律蓋 regen 章;內容二分:指針級(在哪/誰用/流向,[src:] 天生可驗)快寫,why 級(為什麼/邊界)逐句標 [git:]/推測:/佚失:,無證據老實標推測,嚴禁從現狀反推發明合約
    id: d2
    context: openwiki 對照節點「導覽層一分為二」裁定的直接應用;影片 SOP 無此區分,AI 逆向 why 會編得非常自信。另一選項①指針級免蓋章:排除,蓋章成本一行、且不蓋=Check J 全繞過;②全部當 why 級逐句考古:排除,指針錯得便宜,逐句考古讓步驟 0-2 慢十倍沒人會照做
    why_chosen: 指針錯了讀者走到現場自己修正;自信但錯的敘事比沒有敘事更毒。代價:靠紀律蓋章(宣告制),機械偵測留給 from-scratch 計劃的未來項
    decided: 2026-08-24
    valid: true
  - content: 第一版落文件層:skill 子檔+索引路由+注入範本一行;不建掃描/生成 CLI
    id: d3
    context: 最小解在哪一層的裁定。盤點顯示斷點在路由與流程文件(commands/ 索引 grep regen 零命中),不在工具;且 from-scratch 計劃 M3(git-rationale 收割/diff 重生)已排隊未做,另起工具案會撞。另一選項①寫 lumos scan/seed 指令:排除,還沒實跑過 SOP 就機械化=把沒驗過的流程焊死;②只加 INDEX 一行不寫 08 檔:排除,路由通了內容還是空的
    why_chosen: 文件層一天可交付、探針可驗、可整體 revert。代價:全靠紀律無機械逼。回頭條件:SOP 真實跑 ≥3 次後,固定出現的機械化點(如 git 考古的固定指令序列)再立工具案
    decided: 2026-08-24
    valid: true
  - content: 放置層:SOP 七步全文進 skill 的 reference.md(與既有重生守衛段相鄰),commands/09-節點還原.md 只留薄查表(何時敲哪個指令+指標);編號用 09(08 已被佔用),三處「分八類」措辭同步改九類
    id: d4
    context: r1 架構席對照 commands/05、06 慣例:多步驟流程的鄰居一律薄表+指到別處(skill 或 reference.md),敘事本體不進 commands;且 08-自動跑的.md 已存在,r1 三席獨立抓到撞號。另一選項①照原案全文塞 commands/08:排除,撞號+立第二種先例;②不建子檔只改 INDEX:d3 已排除過,路由通了內容還是空的
    why_chosen: 同層鄰居一致性——下一個要放長方法論的人不用在兩種先例間猜;reference.md 本來就是敘事型深規的家(重生守衛、自足性審計都住那)。代價:讀者多一跳(查表→reference),與 05/06 現況相同
    decided: 2026-08-24
    valid: true
---
# 節點還原SOP_計劃

> 白話:接手一個已經在跑、但圖譜是空的(或很稀疏的)專案時,現在的工具鏈只管「重建筆記不准瞎編」(守衛),
> 沒人告訴你「該建哪些節點、從哪開始、還原到多深」(產出)。這個計劃把後半段寫成一份任何技術棧都能走的
> SOP:從看得到的行為反查 code、追資料流圈出承重牆、考古還原為什麼、落成蓋了重建章的節點、列出合約候選
> 但不冒充合約,出口用兩個乾淨 agent 交叉查核(一個讀筆記、一個讀 code)。種子是 Enzo 給的 brownfield
> 教學影片五步流程,這裡通用化、並補上影片沒有的驗證層。(v2:r1 五席 39 條原始發現全數折入)

## 症狀(會翻紅的指令)

```
grep -rl regen skills/lumos-project-notes/commands/ | wc -l
```

2026-08-24 實測輸出 0:八個指令子檔沒有任何一個提到重建/還原,照 INDEX.md 的情境分類走不到重生守衛(唯一指路的是注入範本裡一句「寫法在 skill」)。

其他由獨立盤點(乾淨 agent、不帶結論派工)確認的空白:62 個 CLI 子指令(2026-08-24 實測 `--help`;r1 前誤記 59)沒有掃 repo 產節點的;README/ONBOARDING/methodology 只講裝機不講建內容;「該先建哪些/建到什麼程度算夠」零指引;[[Systems/外部對照-code衍生wiki]] 明文承認冷啟動全覆蓋是對手優勢。

本案成功=①上面那條 grep ≥1 命中 ②情境探針「被丟進陌生舊專案要改功能」題能導到 SOP ③真實 brownfield repo 實跑還原 ≥2 篇節點:`lumos lint`(含 Check J)綠,**且**變體 B 交叉審計(見步驟 6)主張不一致=0 或全數當場修正——Check J 綠只證「合約級沒瞎編+指針沒懸空」,防瞎編的主力是交叉審計,不是 lint(r1 外家+三席實錘:Check J 只掃 summary、KEY 行只提醒不擋)。

## PRIOR-ART(問世界)

- **種子:brownfield 教學影片**(TikTok @one.ai186,15:50,Enzo 2026-08-24 提供逐段筆記,存 `governance/review-reports/node-restore-sop/seed-brownfield-video-notes.md`)——五步:定位畫面是誰在管→追資料流+誰共用→spec+guardrail(給 AI 的護欄條款;forbidden 段把看懂的禁區寫死)→小步+review→回歸測試。精神對(先看懂再動手、共用面=承重牆、Brownfield 的 Clean Code=跟前人一致),兩個洞:①理解活在對話裡,session 關了蒸發 ②guardrail 是 maker 自律,沒有查核層。
  **種子取捨三項(r1 s3 抓到靜默丟棄,補明)**:①影片分「AI 輔助/純指揮」兩條路線——本 SOP **只寫純指揮路線**,刻意排除:本工具鏈的執行者就是 agent,人手貼檔案的路線不是本 SOP 的對象;②「包裝過的錯誤紀錄=部落知識」——吸收,進步驟 2(圈出專案自己的錯誤語言);③「不要在 production 裸用」警告——吸收,進步驟 6 出口警語。
- **openwiki**([[Systems/外部對照-code衍生wiki]])——全倉自動攤平的世界解。本 SOP 反著用:不學它攤平(無 oracle——沒有獨立查核者判對錯——的大量合成敘事),學它被記下的教訓(導覽層一分為二:指針安全、合成敘事有毒)。**同節點對本案最不利的半句也要引(r1 s3 抓到選擇性引用)**:lumos 唯一塌陷回 openwiki 失效模式的例外=from-scratch 重生,而它裁的緩解②「真重生對『圖譜史+code』非 code-only」在冷啟動場景**結構性不存在**(圖譜就是空的)——這不是邊角,是本 SOP 的定義場景。補償=步驟 6 的雙 agent 交叉審計+還原批次過乾淨 agent 對抗抽查;[[Projects/from-scratch重生守衛_計劃]] 的 M2(from-scratch 節點強制過對抗審)落地後,改引用那道機械閘(回頭條件)。
- **repowise**([[Projects/from-scratch重生守衛_計劃]] 記過的最接近先行者)——從 git 歷史挖 architectural decision。
- **內部既有零件**:Check J(重建守衛,只掃 summary,J-a/J-b/J-c 硬擋、J-d 提醒,詳見實務隱患第一條)、`lumos set <節點> regen from-scratch/<日期>` 蓋章、`lumos link-candidates <code檔>`(還原後查該連的既有節點,接進步驟 4)、**變體 B:圖譜×程式碼交叉審計**(reference.md〈變體 B〉,觸發詞就含「接手陌生專案」;與本 SOP 的分工:變體 B=已有筆記的事後查核,本 SOP 步驟 0–5=筆記從零到有的產出,步驟 6 出口直接採用變體 B)、scenario probe、`lumos init`。
- **裁定=借用既有設計**:SOP 是「組合現成零件+補流程文件」;第一版不建新 CLI、不採任何依賴(d3)。

## 設計:七步 SOP(任何技術棧,編號步驟 0–6)

適用場景:裝了 lumos、圖譜空或稀疏的既有專案;或本專案裡目擊紀錄佚失的舊模組。核心原則:**還原跟著任務走(d1)、產出落成節點而非留在對話、每條 why 亮身分(d2)、出口必過交叉查核**。

**步驟 0|進場與最小骨架**
圖譜空 → `lumos init` 裝殼。init **已經自動建好** `MOC/index.md` 空殼(r1 三席實錘)——**填它,不要另建**(`lumos new` 沒有 moc 型,另建也做不到;真另寫一篇會變成兩個互不知道的入口)。正文用 Edit 填:這個 repo 是做什麼的、幾個大件、各自入口在哪(檔案/目錄指針)。只寫指針不寫敘事。停手線(可數,不用牆鐘):**一篇、指針 ≤30 行、不展開**;超大 monorepo 只列第一層大件,子件留給之後的任務驅動。

**步驟 1|錨點階梯定位**
從可觀察行為抓錨,反查到負責的 code 單元。錨點按便宜到貴排:
① **獨特字串**:網頁=畫面文字/元素 class;CLI=--help 或輸出文字;後端=log 訊息/錯誤碼;mobile=字串資源檔。
② 字串抓不到(minify/混淆、生成碼)→ **識別子**:i18n 是兩跳(畫面文字→語系檔抓 key→再搜誰用 key);函式名/類名/路由字串/協定欄位名/硬體暫存器位址。
③ 都沒有(embedded 韌體、宣告式資料管線——可觀察面是波形或排程行為,不是文字)→ **結構文件**:建置腳本、DAG 定義、接腳表、部署設定,從結構往回收斂。
承認:③ 這一級最貴也最容易漏,embedded/資料管線是本 SOP 的弱區(r1 s3 實錘),實跑驗證沒覆蓋到這兩類棧之前,對它們只有「階梯方向」沒有「驗過的流程」。

**步驟 2|追流+圈承重牆**
這個單元的輸入從哪來、輸出到哪去、**誰還共用它**。查共用面**至少兩個來源**:①拿單元名全域搜用法;②該棧的間接接線處——DI/IoC 設定、路由表、DAG 依賴清單、建置依賴圖、事件訂閱表(r1 s3 blocker:純 grep 對依賴注入/反射/隱式介面會**默默漏抓**,找到一部分以為找全了,正是「改 A 壞 B」在還原階段重演)。**要下「沒有別人共用」這種否定結論、且它會決定少建節點時,照 CLAUDE.md ★第四條:派乾淨 agent 拿原始問題對一次,或至少換名/換式再搜一輪**。順手圈出**專案自己的錯誤語言**(包裝過的 logger、錯誤碼表——部落知識,git 考古不出來,種子影片點名的經典坑)。產出:FLOW 一行+共用清單。已有圖譜的專案先敲 `lumos impact --file <檔>`;冷啟動場景這條備援不存在,兩來源紀律就是唯一防線。

**步驟 3|考古還原 why(git 為主,非 git 補位)**
git 歷史是舊專案最容易拿到的目擊者:blame 找到改這段的 commit、log 讀訊息、revert/fix 紀錄、PR 描述。**git 沉默不等於 why 佚失**(r1 s3):squash 政策抹平細粒度、郵件補丁流沒有 PR、資料管線邏輯常改在外部平台、韌體 why 常在硬體資料手冊——git 挖不到時先問一圈**非 git 來源**(issue tracker、wiki、部署文件、資料手冊),都沒有才標佚失。標身分:答得出來源的標 `[git:sha]` 或 `[src:路徑:行號]`;推論標 `推測:`;查不到標 `佚失:`。**佚失是合格產出,不是步驟做壞了**——整個專案大量佚失(squash 起家)是預期結果;此刻正是最想編一個合理 why 的時刻,老實標比編漂亮重要。嚴禁從「現在長怎樣」反推發明「當初為什麼」。

**步驟 4|落節點**
把步驟 1–3 的產出寫成 `Systems/<模組>` 筆記。摘要行分工(r1 通才席實錘,接上現成硬擋):
- FLOW=流程怎麼跑、DEP=依賴誰(指針級,快寫;注意 Check J **完全不掃**這兩種行)
- KEY=關鍵事實(指針級居多;沒標身分會吃 J-d 計數提醒,提醒不擋、屬預期噪音)
- **DECISION=考古出來的 why 放這裡**——J-b 對 DECISION 行是**硬擋**(缺 [src:]/[git:]/推測:/佚失: 直接紅),把 why 放 KEY 行等於自願放棄現成的機械保護
蓋章與時序:**正文與身分標記全部寫完 → `lumos set <節點> regen from-scratch/<日期>` 蓋章 → `lumos lint <節點>` → 同一次 commit**;不留「蓋了章還沒標完」的中間態過夜(機械層分不出半成品,見實務隱患)。落完跑 `lumos link-candidates <該模組主要 code 檔>` 看有沒有既有節點該連(接線,r1 通才席抓到掛名未接)。

**步驟 5|合約候選,不升格**
「改了就壞」的清單,用既有章節慣例寫進筆記:`## 合約候選(收斂時複核,候選≠已標)`(四篇計劃同款格式,r1 s3 抓到沒指定)。**本步到此為止——標候選就是純文件動作。** 升格是**另一次任務**,走 code 側正常紀律,順序明列(r1 外家抓到缺步驟):取得意圖證據→把該行改標 ★INVARIANT★(regen 節點須附 [src:]/[git:],J-a 擋發明)→`lumos guard scaffold`→寫測試→`guard bind`→`guard audit`,全鏈走完才算合約。專案沒測試→升格前先補特徵化測試(characterization test:把現況行為釘住,不判對錯)——**這也屬升格任務,不在本 SOP 交付範圍**;且承認:embedded/資料管線補測試是基礎設施問題(要先搭 harness/模擬器),成本另計,不是「叫 AI 補幾條」就有。

**步驟 6|出口:交叉查核+接回既有紀律**
還原批次收尾**必過變體 B 交叉審計**(reference.md 既有機制,r1 s3 blocker 折入):**兩個乾淨 agent——一個只讀新節點萃取主張,一個只讀 code 逐條判真假**;單 agent 只讀筆記只能抓內部自洽,抓不到「講得通順但跟 code 對不上」,而全圖譜清帳實測過 16.3% 主張與 code 不一致,還原型節點正是高危群。不一致=0 或當場修正才算過;審完 `lumos self-audit <節點>` 蓋章留痕(不蓋 doctor 會一直軟提醒、下個 session 不知道審過)。之後要動手改 code,從這裡起全走現行流程:`lumos impact`、design-loop、code-loop。**警語(種子影片吸收)**:還原完直接動 production 級 code 前,至少讓改動走完 code-loop;還原節點內容日後被行為事實打臉→照 CLAUDE.md 既有規則立事故筆記,錯的節點標作廢或 supersede,這就是還原內容的收回路徑。

### 還原到多深算夠(停手線)

夠=**這次任務要動的面+它的共用面**有節點;不追求覆蓋率、不為還原而還原。骨架層永遠只有指針。深挖由下一個任務驅動——這是家規「圖譜只長在動過的地方」的冷啟動版,不是妥協。

## 落地件(spec-trace 對齊用;r1 通才席抓到原版零 [SN] 標記,補齊)

1. [S1] `skills/lumos-project-notes/reference.md` 新增〈節點還原七步〉深規段(放重生守衛段附近):本節七步的指令化全文(d4 放置裁定)。
2. [S2] `skills/lumos-project-notes/commands/09-節點還原.md`(新檔;08 已被佔用,r1 三席實錘):薄查表——何時敲哪個指令+一行指到 reference.md,體例照 05/06。
3. [S3] `skills/lumos-project-notes/commands/INDEX.md`:「接手陌生/舊專案、圖譜是空的」情境路由+「grep 衝動對照表」對應行;「二、八類子檔」標題改九類——**「分八類」同句散落三處**(INDEX.md:24、本 repo CLAUDE.md 受管區塊、`scripts/templates/graph-discipline.md:29`)一起改,後兩處靠重跑注入分發。
4. [S4] `skills/lumos-project-notes/SKILL.md`:進場節加一行「圖譜空或稀疏 → 走節點還原 SOP(commands/09-節點還原.md)」。
5. [S5] `scripts/templates/graph-discipline.md`:注入範本加一行冷啟動入口(分發需重跑安裝,交付說明註明)。
6. [S6] 情境探針 ≥3 題,寫進 `governance/scenarios/commands.jsonl`(scenario_probe 預設語料;r1 架構席抓到沒指名落點):口語、不帶工具字眼,過線=會照 SOP 進場。
7. [S7] 實跑驗證:真實 brownfield repo 還原 ≥2 篇節點,lint 綠+變體 B 交叉審計過,留 Verification 筆記 `plan_refs` 連回本篇。

## 實務隱患

- **編假 why——機械把關的真實範圍(r1 四席實錘後改寫)**:Check J **只掃 frontmatter 的 summary 行,正文不掃**;硬擋=J-a(★INVARIANT★ 缺意圖證據)、J-b(DECISION 行缺標記)、J-c(懸空 [src:]/[git:] 指針,只驗存在不驗「證據真的支持主張」);J-d 對沒標身分的 KEY 行**只計數提醒**;FLOW/DEP **零檢查**。所以「機械防瞎編」只對合約級成立,prose 級誠實機械驗不了(J-d 提醒文字自己就這麼寫)——prose 的防線是步驟 6 交叉審計。regen 章仍是宣告制,不蓋完全繞過(既有 ★DEBT★)。回頭條件:實跑驗證抽查;之後任何一次發現未蓋章的重建節點,立案機械偵測(from-scratch 計劃已留未來項)。
- **蓋章半成品中間態(r1 三席實錘)**:蓋了 regen 章、summary 只有 FLOW/DEP 或沒寫完的節點,check_regen_provenance 零錯誤零警告靜默全綠——機械層**分不出半成品與成品**。緩解=步驟 4 的「寫完→蓋章→lint→同 commit」時序紀律+步驟 6 交叉審計兜底。回頭條件:交叉審計若抓到半成品節點 ≥1 次,把「蓋章但無任何 DECISION/身分標記」升為 doctor 軟提醒立案。
- **併發還原(r1 兩席實錘)**:兩個 session 同時還原同一模組——`lumos new` 存在性檢查與寫檔間無鎖(TOCTOU),分頭寫同一篇=git 層 last-write-wins/merge conflict,無「哪份重建可信」的裁決機制。緩解=d1 任務驅動下同模組同時還原機率低+git 衝突是唯一柵欄;老實承認沒有機械鎖。回頭條件:真實發生一次,接到 [[Issues/同工作區多session並行改動]] 立機械案。
- **注入面改動**:graph-discipline 範本動所有專案 CLAUDE.md 受管區塊——sentinel 機制既有,改動=一行入口+「八類→九類」;過設計審+情境探針才推。
- **骨架節點腐化**:只寫指針(錯得便宜,讀者走到現場自己發現)、不寫合成敘事;既有 stale/doctor 兜底。
- **金流/對外送出/不可逆**:不涉及——已排除:本案交付(skill 檔+索引+範本行)純文件、無 runtime 行為、不寄任何東西、可整體 revert。**範圍講清(r1 通才席)**:可 revert 的是 SOP 交付物;照 SOP 還原出來的節點內容錯了,收回路徑=步驟 6 寫的事故筆記+作廢/supersede,不在「整體 revert」一句裡。
- **跨 repo 通用性只在本 repo 驗過**:七步的「通用」是設計主張;實跑驗證樣本=1,且 embedded/資料管線兩類棧(r1 s3 點名的結構性弱區)不在樣本內。回頭條件:每次真實接手新專案跑 SOP,把棧特異問題補回 reference 段;連兩次不用補=主張站住;弱區兩類遇到真實案例前,對外只稱「驗過的棧」不稱「任何棧」。

## 審計修正紀錄

- **r1(2026-08-24,5 席:s1 通才/s2 失敗模式/s3 通用性/arch 架構對齊/ext Codex 外家)**:原始 39 條(s1=11 含 1 併入、s2=9、s3=10、arch=4 含 1⚠、ext=5),去重後 22 個獨立問題,全數折入、零放行。實錘要點:08 撞號(三席)、spec-trace 零 [SN](s1)、MOC 該填不該建(三席)、Check J 覆蓋高估家族(四席:只掃 summary/KEY 只警/FLOW/DEP 零檢查/J-c 只驗存在/「只擋 J-a」低估 J-b J-c)、蓋章半成品靜默綠(三席)、承重牆 grep 靜默漏抓 DI/宣告式(s3 blocker)、自足性審計借名弱化→改用變體 B 雙 agent(s3 blocker)、選擇性引用 openwiki(s3)、步驟 5 測試碼與「純文件」自相矛盾(兩席)、升格序列缺改標步驟(ext)、併發零交代(兩席)、種子三項靜默丟棄(s3)、62≠59(兩席)、link-candidates 掛名未接線(s1)、非 git 考古來源(s3)、佚失=合格產出(s2)、停手線改可數(s2)、合約候選章節格式(s3)、放置層照 05/06 慣例(arch major,立 d4)、探針落點指名(arch)、變體 B 補進 PRIOR-ART(arch ⚠)、回滾範圍講清(s1)。
  收貨紀律:s2 兩條引句用省略號拼接錨定失敗(F5/F6),其主張分別由 s1/ext 的錨定引句與本席機械重現(scripts/lumos:2508-2576 實讀、shallow 降級 warn 實讀)獨立證實後收貨;s3 F5.2 引句 <10 字錨定失敗,主張由 grep 四篇計劃的同款章節標題獨立證實後收貨。

## 下一步

r1 折入完成 → 記帳 → `lumos loop status` 問閘;r2 派全新席掃 delta。收斂後實作 [S1]–[S7]。
