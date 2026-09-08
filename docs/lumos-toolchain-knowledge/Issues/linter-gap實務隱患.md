---
type: issue
status: open
created: 2026-07-05
updated: 2026-07-05
tags:
  - type/issue
  - status/open
  - scope/stack-knowledge
related:
  - "[[pitfalls網搜補漏_計劃]]"
summary: |-
  FLAG:TECHNICAL
  KEY:lumos-toolchain(python3 stdlib)的 linter 實務隱患尚未留痕(進實務隱患紀錄)——lumos-pitfalls-gapfill skill 網搜補漏的落點;兩段〈已採納〉(放行的坑,可被 pitfalls 進場餵)〈已評估駁回〉(駁回的坑+反證,供 skill 去重跳過)
  KEY:〈已採納〉目前空(2026-07-05 首次 dogfood 唯一候選被反證預篩駁倒)
  DECISION:isinstance(True,int) bool 穿 int 守衛=真通則隱患但 lumos 已全修(唯二 config int 守衛皆加 not isinstance bool)→ 駁回(無未修實例),記此避免重找
---
# linter-gap 實務隱患(lumos-toolchain / python3 stdlib)

`lumos-pitfalls-gapfill` skill 的落點:linter(ruff/pylint 等)未收錄、經網搜+反證預篩+人放行的殘餘新坑。skill 進場先讀本節點兩段去重。

## 〈已採納〉(放行的坑 — 可被 pitfalls 進場當隱患鏡頭餵)
*(2026-09-08 六棧世界對照:13 條候選,反證席駁倒 8、存活 4 條半——存活的在下表;席報告全文見治理帳與各消費端 grep 證據,反證席去 LM/KDS/mOrangePos 實查)*

| 坑 | 觸發條件 | 來源 |
|----|----------|------|
| **[kt] 副作用 key 選錯**:LaunchedEffect/DisposableEffect 讀了會變的輸入卻用 `Unit` 當 key(永不重跑)/key 太寬(每次重組重跑) | .kt 改動;反證席實查 KDS 18 處 LaunchedEffect 有 9 處 Unit key、2 處讀可變輸入 | [Compose side-effects](https://developer.android.com/develop/ui/compose/side-effects);折入 kt Q1+kotlin-idioms R15(2026-09-08 世界對照) |
| **[sql] 隔離等級/鎖順序/parameter sniffing** | 交易碼;LM 38 處交易僅 1 處明寫隔離、DeadlockRetry 4 處止血、0 處 OPTION(RECOMPILE),compat 150 無 PSP 優化 | [SQL Server deadlocks](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide);折入 sql Q3(2026-09-08) |
| **[swift] 型別抹除與 layout 反覆**:AnyView/條件換型別、GeometryReader/深層堆疊/preference 鏈、大樹隱式動畫;貴子樹 equatable() | .swift 改動(尚無消費端) | [WWDC25 306](https://developer.apple.com/videos/play/wwdc2025/306/);折入 swift Q2+swift-idioms R15 |
| **[swift] 耗電:背景定位/輪詢、網路零散請求** | .swift 改動(尚無消費端);MetricKit 那半歸 ops 不收 | [Energy Efficiency Guide](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/EnergyGuide-iOS/);新增 swift Q6+swift-idioms R16 |
| **[node] 入口速率限制** | Node 後端(尚無消費端);反證席判為 ops/安全防線而非效能題→只進 node-idioms R15+目錄列,不進追問表 | [OWASP Node cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html) |

## 〈已評估駁回〉(駁回的坑 + 反證 — skill 去重跳過,別重找)

- **[2026-09-08 六棧世界對照,反證席駁回 8 條——下次跳過]**
  - **[kt] 背景工作改 WorkManager 帶 constraints**:idioms 家規不點名框架(kotlin-idioms:10);兩消費端(KDS/mOrangePos)是插電 kiosk/POS,0 Service/0 WorkManager,唯一的「timer」是 viewModelScope 內 while(true) 輪詢,已歸 kt Q2 scope 題。
  - **[kt] LazyColumn contentType**:2026-07-27 已駁回一次(兩消費端無混排列表),今日重查 KDS 0 處 contentType。
  - **[cs] new HttpClient 每請求 socket 耗盡**:csharp-idioms R6 已寫;2026-07-27 gapfill 已駁回(LM 0 處 new HttpClient、工廠慣例 13 處),今日重查同。
  - **[cs] EF AsNoTracking / 大回應 stream**:LM 只用 Dapper(0 EF);stream 那半=csharp-idioms R11 原句+cs Q2 分頁。
  - **[vue] 長列表虛擬化/v-memo/active-item props**:vue-idioms R11 逐字相同+vue Q4 已問。
  - **[sql] SELECT * / DISTINCT 掩蓋 join 重複 / OR 串改 IN**:SELECT * 已在 cs Q2 且 sqlfluff AM04 機檢;同欄 IN 與 OR 串在 SQL Server 是同一個 predicate 無索引差(MS Learn IN 範例 A);DISTINCT 是正確性氣味非效能題,LM 11 處皆單欄查找。
  - **[swift] 大圖不下採樣/主線程解碼**:swift Q4「預先縮圖、非同步解碼」+目錄 iOS 段已問。
  - **[node] body 大小上限/單核 cluster**:R4 已有 body 上限,且 Express/Fastify 預設就有 100kb/1MiB;多實例部署已是 R6/R11 前提。
  - **[node] prototype pollution / ReDoS / 隱藏錯誤細節**:R12 邊界 schema=正解、R4+security:detect-unsafe-regex、R13 已寫。
  - **[node] 每行 log 帶請求 id / AsyncLocalStorage 累積洩漏**:R10 已規定 ALS;「ALS store 累積」前提錯(store 隨 async resource GC,Node 24 AsyncContextFrame 預設),只有違反 R10 才漏;請求 id 是觀測慣例,不在效能目錄範圍。

- **`isinstance(x, int)` 誤收 bool**(python `bool` 是 `int` 子類,`isinstance(True,int)==True`;config 讀 JSON 整數欄位用 `isinstance(v,int)` 守衛時 `{"depth":true}` 會穿透)。**真通則隱患、ruff/pylint 一般不 flag**,但**對 lumos 駁回=無未修實例**:反證者 grep 全 codebase,唯二讀 JSON config 整數守衛的地方(`_impact_load_config` `scripts/lumos:5573-5576`、`impact-hook.py:335`)**皆已加 `not isinstance(v,bool)`**,其餘 json.load 讀 str/dict/list 無整數守衛場景。來源:[Real Python isinstance](https://realpython.com/ref/builtin-functions/isinstance/)、[TIL bool subtype of int](https://www.linkedin.com/pulse/til-python-bool-subtype-int-wouter-donders)。(2026-07-05 dogfood)
