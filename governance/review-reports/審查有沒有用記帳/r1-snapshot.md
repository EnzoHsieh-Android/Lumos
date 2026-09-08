---
type: project
status: doing
created: 2026-09-08
updated: 2026-09-08
tags:
  - type/project
  - status/doing
  - scope/evals
related:
  - "[[Projects/loop數據收集_計劃]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Issues/流程自產工作量未量測]]"
  - "[[Projects/enforcement可觀測性_計劃]]"
---
# 審查有沒有用記帳_計劃

> 題目一句:讓「審查到底有沒有用」變成機器數得出來的帳,不是散文。Enzo 2026-09-08 裁「開工」;起因見同事 session 的盤點(回報在 [[Projects/loop數據收集_計劃]] 那條線)。
> 這不是「建一套評測系統」,是「開始記」——三個數字、一個逃逸帳、一段讀側;不回填舊卷證、不做統計模型。

## 為什麼(2026-09-08 我自己量的)

- **審查帳有 1216 筆,但答不出「報了幾條、站得住幾條」。** 席位列的 `--findings` 在 skill 裡寫「存活條數」,實務上有人填席位報的總數、有人填存活的,語意早就混了;被編排者機械重現駁回的發現★根本沒有 id★(只寫在 intake 散文),機器數不出。
- **兩個現成欄位一次都沒人填**:`--refute-verdict`(辯方表態)1216 筆裡 0 筆——今天查明原因是七個輪次一輪辯方都沒派(路由規則下多半不觸發),所以它不是主力;`lumos loop escape` 逃逸帳 0 筆到今天才補第 1 筆(#19 那條線的隔離缺陷被推送閘抓到,審查放行後的漏網)。
- **席報告本身數得出「報了幾條」——但只對照 SOP 寫的報告成立。** 收貨 SOP 要求每條 finding 一行 `severity: <值>`,寫側早就擋「讀不到任何 severity: 獨立宣告行」(code-loop reference)。對今天下午 18 份席報告(code-clause-bindings 兩個編號)實算,行首 `severity: minor|major|blocker` 的行數有 16 份跟手填的 `--findings` 一致;不一致的 2 份是驗收輪的架構席報告——它把前輪已折平的舊發現連同舊 severity 標籤原樣留著。今天早上的 8 份(嚴重度嵌在標題破折號後,如「## F1 — BLOCKER」)機器數到 0。★所以自動數不是萬靈丹:報告格式至少三種,驗收輪的舊項要有辦法排除★——這正是 [S1] 演算法要先講清楚的。
- **兩本帳可信度不同級**(同事 session 抄走的那句):閘擋了誰是機器寫的、賴不掉;人漏了什麼、人駁回了什麼只能靠人誠實。讀側必須分開印、不可拿人工帳的數字去算機器帳的比率。

## 做什麼

### [S1] 席位列自動數「報了幾條」,存進帳 [test:t_canary_reported_auto]

- `canary record` 帶 `--report` 時,機器數報告裡行首 `severity: minor|major|blocker` 的行數(去列表符號與粗體;排除 clean;排除第一行的檔級 severity;★排除值為 `resolved` 的行★),寫成新鍵 `reported`,並記 `reported_by: auto`。★不靠人填★——refute_verdicts 0/1216 證明選填欄位沒人填。
- ★SOP 補一條(進兩個 skill 的收貨段)★:驗收輪報告裡留下的前輪已折平項,嚴重度行寫 `severity: resolved`(不是留舊值)——不然機器會把已解決的當成這輪報的。嵌在標題裡的寫法早就被寫側擋(讀不到獨立 severity 行 rc2),不必另處理。
- 席報告格式對不上時(自動數與席位總結句明顯不符)可 `--reported N` 覆蓋,覆蓋要帶 `--reported-note` 一句為什麼;沒帶理由 rc2;帳上記 `reported_by: manual`,讀側分開印。
- 既有 `--findings` 語意不動(歷史帳不回溯),新讀側只用 `reported`。

### [S2] 載體列多一組「駁回清單」,駁回要有 id 和理由 [test:t_canary_refuted_set]

- `--refuted-set id=理由`:編排者機械重現後判 MISS、沒折也沒放行的發現。寫側驗證:id 不得與 `--findings-set` 重疊、理由不得為空;有 `--findings-set` 而沒帶 `--refuted-set` 視同 0 條駁回(不擋——擋會逼人亂填,但讀側印「未填」跟「0」分開)。
- 這樣一輪的帳才閉合:報(席位總和)→ 去重後 存活(findings-set)+ 駁回(refuted-set)→ 存活裡 折(folded)/ 放行(accepted)。
- ★閘不驗駁回的對錯★(那是人工判斷,intake 留重現指令);這裡只讓它有 id、有理由、數得出來。

### [S3] 讀側:每輪一行、全庫一段,兩本帳分開 [test:t_gov_stats_review_yield]

- `lumos loop status <編號> --disposal` 尾端(觀測,不進合取)每輪印一行:「報 N → 存活 M / 駁回 R → 折 F / 放行 A;逃逸 E」;`reported` 缺的印「報 ?(2026-09-09 前的帳沒數)」。
- `lumos gov --stats` 新段「審查有沒有用(2026-09-09 起才有帳)」:有 `reported` 的輪數、Σ報/Σ存活/Σ駁回/Σ折/Σ放行、逃逸帳筆數與最重等級;辯方表態那段照舊。
- ★段首一句固定★:「人記的帳(這段)跟機器擋的帳(上面『閘的動作』)可信度不同級,不要拿這裡的數字去算那裡的比率」。

### [S4] 逃逸的當下就記:兩個提醒點 [manual:對照 skill 與 ci-wait 訊息的 diff 人看,不改行為]

- `lumos ci-wait` 紅燈的收尾訊息加一句:修完若可歸因到某次已放行的審查 → `lumos loop escape <編號> --stage ci --severity … --desc …`。
- code-loop skill 第 8 步之後那個獨立段落已有 escape 那句;design-loop skill 步驟 10 補同一句(設計審放行後、實作階段抓到的設計期漏洞也是逃逸)。
- 記帳模板(兩個 skill 的 record 範本)加 `--refuted-set`。

### [S5] 範圍刀 [manual:對照實作 diff 人看:沒新帳本、沒回填、沒模型]

不新開帳本(全部加在既有 canary 列與 gov --stats 上)、不回填舊卷證(全 repo 席報告 853 份——`governance/review-reports/**/r*-*.md` 去掉 intake/snapshot/roster/dispatch——帳上 783 個相異報告路徑——跨四五代協議,混池=體溫計加溫度計)、不做統計模型/不自動調參、不改處置閘的判定(讀側是觀測)、不動 `--findings` 語意。

## 實務隱患

- **自動數會數錯的地方**:席報告格式不照 SOP(嚴重度寫在表格裡、寫成 `**severity**`、一條 finding 兩行 severity)。對策:數法固定且公開(行首、去列表符號與粗體、只算 minor/major/blocker、排除第一行),數錯用 `--reported` 帶理由覆蓋;讀側印「自動數」還是「人覆蓋」。REVISIT:2026-10-08 拿一個月的席報告抽 20 份人工對一次自動數
- **駁回清單靠編排者誠實**:不想承認自己駁錯就不記——跟逃逸帳同一個天花板,寫在段首。對策只有一個:intake 的機械重現表已經是留痕,`--refuted-set` 的 id 要對得上 intake 才算數(讀側不驗,人抽查)。
- **選填欄位沒人填的老病**:refute_verdicts 就是前科。所以 [S1] 不靠人填、[S2] 靠「有 findings-set 就會想到」加模板;仍要量:
- REVISIT:2026-11-08 量「有 findings-set 的輪裡 refuted-set 有填(含明填 0)的比例」,低於五成就把它改成寫側必填
- **兩本帳混算**:段首固定句;讀側不印任何跨帳比率。
- **自我治理(self-governance)這一類**:這本帳量的是治理工具自己的審查流程,記帳的人(編排者)同時是被量的人——利益衝突擋不住。對策:①「報幾條」由機器從席報告數,編排者改不了席報告(留痕 sha 綁帳);②駁回要有 id 與理由、intake 有重現指令,人可抽查;③讀側不印跨帳比率、不進任何閘(觀測),所以沒有「把數字做好看就能過關」的誘因。已排除的:自動調參、把這段當閘——兩者都會把量測變成目標。
- **不涵蓋**:「白擋了什麼」(閘誤擋)這一軸——機器帳那邊 `gov --stats` 已有 fail-open/blocked 計數,誤擋要人判,不在本案。
- **併發/效能**:讀側多掃一次 canary 帳(1216 筆、約 1 MB),`gov --stats` 已經在讀它,不另開檔。

PRIOR-ART: 世界=code review analytics 的「finding acceptance rate / review yield」與 DORA(DevOps Research and Assessment,四個交付指標那套)式的「逃逸缺陷率」(都是事後從既有紀錄算,不另建系統);自家=`finding_kinds`、`refute_verdicts`、逃逸帳、`gov --stats` 各段都已存在,缺的只是「報幾條」與「駁回」兩個欄位;裁定=borrow-design(全加在既有 record/stats 上,不新帳本、不新指令)
