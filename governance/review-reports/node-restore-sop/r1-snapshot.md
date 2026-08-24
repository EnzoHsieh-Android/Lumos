---
type: project
status: doing
created: 2026-08-24
updated: 2026-08-24
summary: |-
  FLAG:DECISION
  KEY:立案(2026-08-24 Enzo 開新任務)——「接手既有專案,把功能脈絡還原成圖譜節點」的 SOP。盤點(乾淨 agent 獨立跑)確認缺口結構性:守衛半邊有(Check J/regen 章,M1 落地),產出半邊全空——無指令、無 SOP 文件、無「建哪些/從哪開始/多深算夠」指引;commands/ 八子檔 grep regen 零命中(索引路由斷點);59 個 CLI 子指令無掃 repo 產節點者
  KEY:方案=七步 SOP(步驟 0–6,任何技術棧):骨架地圖→特徵字串定位→追流圈承重牆→git 考古還原 why→落節點蓋 regen 章逐句標身分→合約候選不升格;出口接既有 impact/design-loop/code-loop。種子=Enzo 提供的 brownfield 影片五步,通用化+補它缺的驗證層(它的 guardrail 是 maker 自律,同 openwiki 病)
  KEY:三裁定——d1 任務驅動為預設+第一天只建最小骨架,不整倉攤平;d2 產出二分:指針級快寫、why 級逐句標身分嚴禁編;d3 第一版落文件層(skill 子檔+索引+注入行),不建掃描 CLI
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
---
# 節點還原SOP_計劃

> 白話:接手一個已經在跑、但圖譜是空的(或很稀疏的)專案時,現在的工具鏈只管「重建筆記不准瞎編」(守衛),
> 沒人告訴你「該建哪些節點、從哪開始、還原到多深」(產出)。這個計劃把後半段寫成一份任何技術棧都能走的
> SOP:從看得到的行為反查 code、追資料流圈出承重牆、git 考古還原為什麼、落成蓋了重建章的節點、列出
> 合約候選但不冒充合約,最後出口接回既有的審查紀律。種子是 Enzo 給的 brownfield 教學影片五步流程,
> 這裡通用化、並補上影片沒有的驗證層。

## 症狀(會翻紅的指令)

```
grep -rl regen skills/lumos-project-notes/commands/ | wc -l
```

2026-08-24 實測輸出 0:八個指令子檔沒有任何一個提到重建/還原,照 INDEX.md 的情境分類走不到重生守衛(唯一指路的是注入範本裡一句「寫法在 skill」)。

其他由獨立盤點(乾淨 agent、不帶結論派工)確認的空白:59 個 CLI 子指令沒有掃 repo 產節點的;README/ONBOARDING/methodology 只講裝機不講建內容;「該先建哪些/建到什麼程度算夠」零指引;[[Systems/外部對照-code衍生wiki]] 明文承認冷啟動全覆蓋是對手優勢。

本案成功=①上面那條 grep ≥1 命中 ②情境探針「被丟進陌生舊專案要改功能」題能導到 SOP ③真實 brownfield repo 實跑還原 ≥2 篇節點且 Check J(重建守衛:專擋「從 code 重建的筆記瞎編」的機械檢查,見 related 節點)全綠。

## PRIOR-ART(問世界)

- **種子:brownfield 教學影片**(TikTok @one.ai186,15:50,Enzo 2026-08-24 提供逐段筆記)——五步:定位畫面是誰在管→追資料流+誰共用→spec+guardrail(給 AI 的護欄條款;forbidden 段把看懂的禁區寫死)→小步+review→回歸測試。精神對(先看懂再動手、共用面=承重牆、Brownfield 的 Clean Code=跟前人一致),兩個洞:①理解活在對話裡,session 關了蒸發,導覽圖是一次性產物 ②guardrail 是寫給 AI 看的叮嚀(maker 自律),沒有查核層,AI 逆向出的 why 可能是編的它完全沒防。
- **openwiki**([[Systems/外部對照-code衍生wiki]],已有完整對照節點)——全倉自動攤平的世界解。本 SOP 反著用:不學它攤平(無 oracle——沒有獨立查核者判對錯——的大量合成敘事),學它被記下的教訓(導覽層一分為二:指針安全、合成敘事有毒)。
- **repowise**([[Projects/from-scratch重生守衛_計劃]] 記過的最接近先行者)——從 git 歷史挖 architectural decision,佐證「git 考古還原 why」這條路世界走過。
- **內部既有零件**:Check J(重建守衛,lint/doctor 同函式,M1 已落地 27 格綠)、`lumos set <節點> regen from-scratch/<日期>` 蓋章、`lumos link-candidates`(覆蓋缺口偵測最近親)、scenario probe(驗「規則吃進去沒」的儀器)、`lumos init`(空殼六夾)。
- **裁定=借用既有設計**:SOP 是「組合現成零件+補流程文件」;第一版不建新 CLI、不採任何依賴(d3)。

## 設計:七步 SOP(任何技術棧,編號步驟 0–6)

適用場景:裝了 lumos、圖譜空或稀疏的既有專案;或本專案裡目擊紀錄佚失的舊模組。核心原則:**還原跟著任務走(d1)、還原的產出落成節點而非留在對話、每條 why 亮身分(d2)**。

**步驟 0|進場與最小骨架**
圖譜空 → `lumos init` 裝殼,然後建**一篇** MOC(Map of Content,整個 repo 的導覽頁)節點:這個 repo 是做什麼的、幾個大件、各自入口在哪(檔案/目錄指針)。只寫指針不寫敘事,每行天生可驗(路徑存在與否)。停手線:一篇、半小時內,不展開。

**步驟 1|特徵字串定位**
從可觀察行為抓一段獨特字串,全專案搜尋反查到負責的 code 單元。通用性:任何棧都有可觀察面——網頁=畫面文字/元素 class(影片的「右鍵檢查」是此步的網頁特例);CLI=--help 或輸出文字;後端=log 訊息/錯誤碼;mobile=字串資源檔。字串是最便宜的錨,比讀架構文件快且不會騙人。

**步驟 2|追流+圈承重牆**
這個單元的輸入從哪來、輸出到哪去、**誰還共用它**(拿單元名再全域搜一次用法)。共用面就是承重牆——影片「改商品頁的 hook 弄壞訂單頁」的事故根因。產出:FLOW 一行(資料怎麼流)+共用清單。已有圖譜的專案,此步先敲 `lumos impact --file <檔>` 看有沒有現成答案再自己追。

**步驟 3|git 考古還原 why**
舊專案唯一剩下的目擊者是 git 歷史:blame 找到改這段的 commit、log 讀訊息、revert/fix 紀錄、PR 描述。答得出「為什麼這樣設計/為什麼邊界在這」的,標 `[git:sha]`;code 本身能作證的標 `[src:路徑:行號]`;兩者都沒有→老實寫 `推測:` 或 `佚失:`。嚴禁從「現在長怎樣」反推發明「當初為什麼」。

**步驟 4|落節點**
把步驟 1–3 的產出寫成 `Systems/<模組>` 筆記(FLOW=流程怎麼跑/KEY=關鍵事實/DEP=依賴誰),**先蓋章**:`lumos set <節點> regen from-scratch/<日期>`(regen=重建章,宣告「這篇是從 code 重建的」;from-scratch=整篇從頭建),再逐句標身分,寫完 `lumos lint <節點>`——Check J 自動把關(合約標記 ★INVARIANT★——標了=改了就是破壞——的行,沒有 [src:]/[git:] 證據直接擋)。這步是整個 SOP 對影片最大的增量:理解不再蒸發,下個 session 直接 `lumos search` 接手。

**步驟 5|合約候選,不升格**
「改了就壞」的清單寫進筆記正文標「合約候選」,**不標 ★INVARIANT★**(不確定不標鐵則;剛還原的理解不夠格直接當合約)。升格走既有的 guard scaffold→bind→audit,綁上測試才算。專案沒測試 → 先補特徵化測試(characterization test:把現況行為釘住,不判對錯)再談升格——這也是影片「沒測試就趁現在補」的機械化版。

**步驟 6|出口:接回既有紀律**
還原完要動手改,從這裡起全走現行流程:`lumos impact` 看波及、design-loop 審設計、code-loop 審 diff、回歸=impact 清單逐一確認。SOP 到此交棒,不另立一套。收尾:派乾淨 agent 只讀新節點還原脈絡(自足性審計),對不上補到一致。

### 還原到多深算夠(停手線)

夠=**這次任務要動的面+它的共用面**有節點;不追求覆蓋率、不為還原而還原。骨架層永遠只有指針。深挖由下一個任務驅動——這是家規「圖譜只長在動過的地方」的冷啟動版,不是妥協。

## 落地件(spec-trace 對齊用)

1. `skills/lumos-project-notes/commands/08-節點還原.md`(新檔,現在還不存在,本案交付物):SOP 操作全文(本節七步的指令化版本)。
2. `skills/lumos-project-notes/commands/INDEX.md`:加「接手陌生/舊專案、圖譜是空的」情境路由一行;「grep 衝動對照表」對應行。
3. `scripts/templates/graph-discipline.md`:注入範本加一行冷啟動入口(→ 分發需重跑安裝,交付說明要註明)。
4. `skills/lumos-project-notes/SKILL.md`:進場節加一行「圖譜空或稀疏 → 走節點還原 SOP(commands/08-節點還原.md)」。
5. 情境探針 ≥3 題(口語、不帶工具字眼:「你被丟進一個沒文件的舊專案要加功能」類),過線=會照 SOP 進場。
6. 實跑驗證:真實 brownfield repo 還原 ≥2 篇節點,Check J/lint 綠,留 Verification 筆記 `plan_refs` 連回本篇。

## 實務隱患

- **編假 why**:Check J 只擋合約級(J-a),非合約 prose 靠身分標記紀律;且 regen 章是宣告制,不蓋章完全繞過(既有 ★DEBT★,非本案新增)。本案靠 SOP 文件要求「還原節點必蓋章」+探針驗——沒有機械逼。回頭條件:實跑驗證時抽查;之後任何一次發現未蓋章的重建節點,立案機械偵測(「疑似重生未標」自動偵測在 from-scratch 計劃本就留了未來項)。
- **注入面改動**:graph-discipline 範本動的是所有專案的 CLAUDE.md 受管區塊——sentinel 機制既有,只加一行;過設計審+情境探針才推。
- **骨架節點腐化**:第一天建的 MOC 沒人維護會爛。緩解:只寫指針(錯得便宜,讀者走到現場自己發現)、不寫合成敘事;既有 stale/doctor 機制兜底。
- **金流/對外送出/不可逆**:不涉及——已排除:本案交付純文件+索引路由,無 runtime 行為、不寄任何東西、可整體 revert。
- **跨 repo 通用性只在本 repo 驗過的風險**:七步的「通用」目前是設計主張;實跑驗證(落地件 6)只驗一個外部 repo,樣本=1。回頭條件:每次真實接手新專案跑 SOP 後,把踩到的棧特異問題補回 08 檔;連兩次不用補=主張站住。

## 下一步

寫完本篇 → `lumos lint` → design-loop(編號 node-restore-sop,tier standard,上限 3 輪)→ 收斂或攤人裁 → 實作落地件 1–6。
