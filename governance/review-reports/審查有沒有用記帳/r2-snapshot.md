---
type: project
status: doing
created: 2026-09-08
updated: 2026-09-08
tags:
  - type/project
  - status/doing
  - scope/evals
summary: |-
  FLAG:TECHNICAL
  KEY:題目=讓「審查到底有沒有用」變成機器數得出的帳(Enzo 2026-09-08 裁「開工」);不建評測系統,只開始記:兩個必填數字、一個駁回清單、一段讀側、逃逸當下就記;不回填 853 份舊卷證、不做模型
  KEY:★不從報告自動數★(r1 五席用四種真實格式證明會數到 0;專案只准一份 severity 解析):S1 席位列必填 --reported,`_report_severities` 只當下限守衛;--findings 語意與 light/gate 舊閘依賴不動
  KEY:S2 載體列必帶 --refuted-set(none 可)、id 對 intake 驗、理由含實字;--self-found-set 讓漏斗算得通(報 8 → 存活 9 的真帳)
  KEY:S3 讀側只印★問閘的這一輪★一行 + gov --stats 一段;缺欄位五格各印 ?;★段首固定兩句★不混算、不印比率;「駁回」一律寫「編排者重現不到」;逃逸 E 是迴圈累計
  KEY:S4 只改 skill(design-loop 步驟 10 後補逃逸段、範本加三旗標、驗收輪舊項不留 severity 行),不動 ci-wait;S5 範圍刀
  KEY:r1(2026-09-08,5 席):通才 2 blocker、接手 1 blocker、簡化 1 blocker、Codex 2 major、架構 1 major;去重 16 條全折、0 放行
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
- **席報告「看起來」數得出「報了幾條」,r1 五席證明不行。** 收貨 SOP 要求每條 finding 一行 `severity: <值>`,寫側早就擋「讀不到任何 severity: 獨立宣告行」(code-loop reference)。對今天下午 18 份席報告(code-clause-bindings 兩個編號)實算,行首 `severity: minor|major|blocker` 的行數有 16 份跟手填的 `--findings` 一致;不一致的 2 份是驗收輪的架構席報告——它把前輪已折平的舊發現連同舊 severity 標籤原樣留著。今天早上的 8 份(嚴重度嵌在標題破折號後,如「## F1 — BLOCKER」)機器數到 0。★所以自動數不是萬靈丹:報告格式至少三種,驗收輪的舊項要有辦法排除★——這正是 [S1] 演算法要先講清楚的。
- **兩本帳可信度不同級**(同事 session 抄走的那句):閘擋了誰是機器寫的、賴不掉;人漏了什麼、人駁回了什麼只能靠人誠實。讀側必須分開印、不可拿人工帳的數字去算機器帳的比率。

## 做什麼(r1 折入後;r1 之前的寫法見卷證 r1-snapshot.md——那版想「從席報告自動數」,五席用四種真實報告格式證明會數到 0)

### [S1] 席位列必填「報了幾條」,解析只當下限守衛 [test:t_canary_reported_required]

- `canary record` 帶 `--report` 的席位列★必帶 `--reported N`★(席報告自己數的條數,含 minor;不帶 rc2)——跟 `--severity`、`--report` 同一種「必填、寫側擋」的慣例;選填就是 refute_verdicts 0/1216 那條路。
- ★不從報告自動數★(r1 五席:標題內嵌、`- [major]` 列表、驗收輪留舊項三種格式今天都在用,自動數會得 0;而且專案只准一份 severity 解析 `_report_severities`,不得另寫寬鬆版)。解析只拿來當**下限守衛**:`_report_severities` 數到的非 clean 宣告行(扣掉檔序第一個宣告=檔級)若 > `--reported`,rc2「報告裡的宣告行比你填的多,對正再記」;少於不擋(格式沒正規化的報告本來就數不全)。
- 寫側再一條:`--findings`(存活)不得大於 `--reported`(存活不會多於報的)。`--findings` 既有語意與必填規則一律不動——`--light`/`--gate` 兩條舊閘仍 fail-closed 依賴它(通才席、簡化席各自核過)。

### [S2] 載體列:駁回清單必帶、id 對得上 intake、理由要有實字 [test:t_canary_refuted_set]

- 有 `--findings-set` 就★必帶 `--refuted-set`★(跟 folded/accepted 同一種硬擋慣例),值 `none` 表示這輪 0 條駁回;`id=理由` 逗號串,理由 ≥4 字且含實字。
- ★寫側對 intake 驗★:帶非 none 的 refuted-set 時必帶 `--intake`,每個駁回 id 要在 intake 檔文字裡出現(子字串),沒有就 rc2——這樣「駁回」才不是 CLI 打進去的任意字串(Codex/通才/接手三席同判)。id 用 intake 機械重現表裡的編號(同一套)。
- 駁回 id 不得與 findings-set 重疊。閘仍不驗駁回的對錯(那是人工判斷,intake 留重現指令);讀側把 R 標成「編排者重現不到(人填,已對 intake)」。
- 載體列再加 `--self-found-set`(選填,⊆ findings-set):編排者自己踩到、沒有任何一席報過的發現——不然「報 8 → 存活 9」算術倒退(通才席拿今天 -b r1 的真帳證明:i9 是我折 i4 時自己踩到的)。

### [S3] 讀側:問閘那一輪印一行、全庫一段,缺欄位五格都印「?」 [test:t_gov_stats_review_yield]

- `lumos loop status <編號> --disposal` 尾端(觀測,不進合取;凍結/回放模式照既有慣例不印觀測尾)印★問閘的這一輪★一行:「席位報 N(+編排者自找 S)→ 存活 M / 重現不到 R → 折 F / 放行 A;這條迴圈累計逃逸 E」。N=該輪席位列 `reported` 加總;任何欄位缺(2026-09-09 前的帳)就★該格印「?」,五格各自判★,不拿散文 note 猜數字(Codex 席 blocker)。N+S < M+R 時印「⚠ 算術不通」,不修數字。逃逸帳沒有輪次欄位,E 是整條迴圈累計(簡化席)。
- `lumos gov --stats` 新段「審查有沒有用(只算有 `reported` 的 K 輪,2026-09-09 起)」:K、Σ報、Σ自找、Σ存活、Σ重現不到、Σ折、Σ放行、逃逸筆數與最重等級;K < 5 時多印一句「樣本太少,別下結論」(接手席:全庫 227 個迴圈 45% 兩週內沒新帳,舊帳永遠是 ?)。
- ★段首固定兩句★:①「人記的帳(這段)跟機器擋的帳(『閘的動作』那段)可信度不同級,不要拿這裡的數字去算那裡的比率」②「這段內部也不印比率、也別自己算 Σ折/Σ報 當『審查有用率』——Σ報是人填的、各席口徑不一」(接手席 F6)。
- 「駁回」在所有輸出裡一律寫「編排者重現不到」,不寫「駁回」(接手席:不知道流程的人會讀成審查員錯)。

### [S4] 逃逸的當下就記:只改 skill,不動 ci-wait [manual:對照 skill diff 人看]

- design-loop skill 步驟 10 之後補一段獨立散文(跟 code-loop skill 第 8 步後那段同款):設計審放行後、實作階段抓到的設計期漏洞也是逃逸 → `lumos loop escape`。
- 兩個 skill 的 record 範本加 `--reported`、`--refuted-set`、`--self-found-set`;收貨 SOP 補:驗收輪留前輪已折平的舊項時★不要留 `severity:` 行★(嵌在標題或散文裡),不引入新值 `resolved`(架構席/Codex:值域單一來源是 `_SEV_ORDER`)。
- ★不在 `ci-wait` 紅燈訊息加提醒★:簡化席數了 ci 帳 12 次紅燈 0 次是審查漏網,加了就是噪音。

### [S5] 範圍刀 [manual:對照實作 diff 人看:沒新帳本、沒回填、沒模型、沒自動數]

不新開帳本(全部加在既有 canary 列與 gov --stats 上)、不回填舊卷證(全 repo 席報告 853 份——`governance/review-reports/**/r*-*.md` 去掉 intake/snapshot/roster/dispatch——帳上 783 個相異報告路徑;跨四五代協議,混池=體溫計加溫度計)、不做統計模型/不自動調參、不改處置閘的判定(讀側是觀測)、不動 `--findings` 語意、不從報告自動數、不另寫 severity 解析。

## 實務隱患(r1 折入後)

- **必填會讓別的 session 記帳被擋**:`--reported`、`--refuted-set` 一上線,沒讀新 skill 的 session 記帳 rc2。對策:擋下訊息直接印該帶什麼、怎麼數;兩個 skill 範本同步改;這正是「有東西逼」的那一半,選填就會重演 0/1216。
- **下限守衛的邊界**:`_report_severities` 只認獨立行,標題內嵌/列表格式的報告數到 0 → 守衛形同虛設(不擋),但不會誤擋;獨立行格式的報告若宣告行比填的多才擋。
- REVISIT:2026-10-08 抽 20 份席報告人工對一次「填的 reported」與報告自數,看口徑漂不漂
- **駁回清單靠編排者誠實**:id 對 intake 驗只證明「intake 提過這個 id」,不證明重現做對了——跟逃逸帳同一個天花板,段首寫明;讀側永遠不印比率。
- **選填欄位沒人填的老病**:refute_verdicts 就是前科,所以 S1/S2 都改必填;剩 `--self-found-set` 選填(不填=沒有自找,讀側「算術不通」會把漏填印出來)。
- REVISIT:2026-11-08 量兩件事——有 findings-set 的輪裡 refuted-set 非 none 的比例(0% 也是答案:代表沒人駁回或沒人記),以及「算術不通」出現的輪數
- **自我治理(self-governance)這一類**:這本帳量的是治理工具自己的審查流程,記帳的人(編排者)同時是被量的人。對策:①報幾條由必填+下限守衛雙向夾(填少於報告宣告會擋);②駁回要有 id、對 intake、理由有實字;③讀側不印比率、不進任何閘,沒有「把數字做好看就能過關」的誘因。已排除:自動調參、把這段當閘。
- **兩本帳混算**:段首固定兩句;讀側不印任何比率。
- **併發**:兩個 session 記同一輪只會多幾筆 append-only 的列,讀側加總會重複——這是既有 canary 帳的既有邊界(記帳前查 `loop next`),不在本案。
- **不涵蓋**:「白擋了什麼」(閘誤擋)這一軸——機器帳那邊 `gov --stats` 已有 fail-open/blocked 計數,誤擋要人判,不在本案。
- **效能**:讀側多掃一次 canary 帳(1216 筆、約 1 MB),`gov --stats` 已經在讀它,不另開檔。

PRIOR-ART: 世界=code review analytics 的「finding acceptance rate / review yield」與 DORA(DevOps Research and Assessment,四個交付指標那套)式的「逃逸缺陷率」(都是事後從既有紀錄算,不另建系統);自家=`finding_kinds`、`refute_verdicts`、逃逸帳、`gov --stats` 各段都已存在,缺的只是「報幾條」與「駁回」兩個欄位;裁定=borrow-design(全加在既有 record/stats 上,不新帳本、不新指令)

## 審計修正紀錄

- r1(2026-09-08,5 席:通才/接手的人/簡化守護者 算人數,＋架構對齊、外家否決 Codex):去重 16 條/blocking 11/最高 blocker——
  自動數在四種真實報告格式上數到 0(三席各自實測)、報 8 存活 9 算術倒退、駁回清單可灌大、舊帳缺欄位只有「報」印 ?、選填等於沒填、resolved 不在值域、ci-wait 提醒 0/12 是噪音;
  全折、0 放行。行為斷言配例:「席報告獨立宣告 5 行、--reported 填 3 → rc2;填 6 → 過」。
- 卷證:`governance/review-reports/審查有沒有用記帳/`。
