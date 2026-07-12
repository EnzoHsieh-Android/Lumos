---
type: project
status: doing
created: 2026-07-12
updated: 2026-07-12
tags:
  - type/project
  - status/doing
summary: |-
  FLOW:訊號源(C1a-lint演進/C1b-框架版本/C2-網搜每週/C3-code-loop旁註)→collector吐候選(帶target_rule)→共用池(lock去重)→refuter預篩(自造留痕)→governance-drain產草案→人閘三力度(微調/新R走design-loop/刪R)→改idioms文件
  KEY:治病=idioms三份(kotlin/vue/csharp)會過時(版本變)或缺漏(新實踐沒收),既有「飛輪」靠人記得回填=實質不會發生;把「該回來複查」變機械觸發
  KEY:方案C'(round-1 Codex跨家族審計修正版)——借「設計教訓」(gapfill反證預篩哲學/lint-watch的staging+LINE+人放行形態),但refuter留痕·drain·框架監測各造薄專用新原語,不硬借canary-record/自主loop-N=1(現契約不容)
  KEY:共用池=idioms-candidates(可變狀態儲存,atomic-rewrite+advisory-lock,非append-only;待建);schema含結構化target_rule;候選kind=stale|gap;stale身分=(doc,tool/框架,from→to,target_rule)含版本以利重驗
  KEY:C3改「加法旁註」——reviewer照常產完整verdict(所有真bug照計,不動verdict/pre-push),額外旁註「反覆樣式值得升R」;修正round-1 blocker(舊桶B會讓無R真bug逃收斂閘)
  KEY:refuter預設反方(試駁不試證);框架特定判準=可替換第三方庫選擇(Hilt/Koin·Pinia/Vuex)→駁回進專案圖譜,核心語言/官方框架通用慣例→收(對齊idioms分層原則)
  KEY:drain=獨立governance步驟(仿lint-watch:staging+LINE+人放行,非自主loop插槽);C2網搜每週;人閘三力度(微調trivial/新R走design-loop/刪R);與linter-gap分池(通用idioms vs 專案gotcha)
  DEP:[[pitfalls網搜補漏_計劃]][[lint-version-watch]][[自主loop加法偏食]][[linter-gap實務隱患]]
  DECISION:[2026-07-12]走方案C(薄collector+池新造,篩選/清池借既有)(valid)
  DECISION:[2026-07-12]drain掛每日09:30自主loop(valid)｜統一refuter預篩三源(valid)｜C3桶B不進verdict去誘因(valid)
related:
  - "[[pitfalls網搜補漏_計劃]]"
  - "[[Systems/lint-version-watch]]"
  - "[[Issues/自主loop加法偏食]]"
  - "[[Issues/linter-gap實務隱患]]"
decisions:
  - content: 走方案C：薄 collector + 共用候選池為新造，refuter 借 gapfill、drain 借自主 loop、落點仿 linter-gap
    context: 三份 idioms 文件會過時/缺漏，既有『飛輪』靠人記得回填=實質不會發生；需把『該複查』機械觸發。三源(lint-watch/網搜/code-loop棄稿)產出需匯流
    why_chosen: 唯一同時滿足『共用 sink』又不重造 gapfill/loop 的方案；A 全新子系統重造已 dogfood 的 refuter/drain/落點(違零依賴家規)，B 全走既有軌會讓候選散在 lint-watch staging 與 linter-gap 兩處(破壞共用池、人要看兩地)
    alternatives_considered:
      - "A 全新 lumos idioms-watch 子系統：概念最乾淨、邊界清楚，但重造 gapfill refuter/自主 loop drain/linter-gap 落點——零依賴家規下的重造輪子"
      - "B 全走既有軌、不造新東西：新代碼幾乎為零且全部已驗證，但候選散在 lint-watch staging 與 linter-gap 節點兩處，破壞『共用 sink』、人要看兩地"
      - "C 薄 collector + 共用池新造，refuter/drain 借既有：選此"
    trade_offs: "需明確定義三個 collector 與既有 refuter/loop 的介面(新增邊界的維護成本)；換得共用池不散落 + screening/draining 不重造已 dogfood 的機制"
    decided: 2026-07-12
    valid: true
  - content: round-1 修正:方案C→C'——borrow-design(gapfill反證哲學+lint-watch的staging形態)但refuter留痕/drain/框架監測各造薄新原語,不硬借canary-record(收斂專用)/自主loop(N=1單工)
    context: round-1 design-loop 跨家族Codex否決席揭露:C3兩桶會讓無R真bug逃code-loop收斂閘(blocker)、canary-record無候選語意、自主loop N=1單工不容drain插槽、gapfill反證綁單專案與idioms跨專案通用相斥、lint-watch輸出已被治理層消費
    why_chosen: 保住三源完整迴路又修正blocker:C3改加法旁註(不動verdict/pre-push)、refuter/drain各造薄專用原語(仿形態不硬借)、C1b加回框架watcher補框架rot分類洞、明定框架特定判準(可替換庫選擇→駁/核心框架慣例→收)
    decided: 2026-07-12
    valid: true
---
# idioms自維護迴路_計劃

**PRIOR-ART:** round-1 對抗審計（Codex 跨家族否決席）證實「只借不造」的假設半數與現契約不符（canary-record 是收斂專用、自主 loop 是 N=1 單工、gapfill 是互動式 skill 且反證邏輯綁單專案、lint-watch 輸出已被治理層消費）。修正為**方案 C'**：借「設計教訓」（gapfill 的反證預篩哲學、lint-watch 的 staging+LINE+人放行**形態**），但 refuter 留痕 / drain / 框架版本監測各造**薄的專用新原語**，不硬借。裁定 = **borrow-design（哲學與形態）+ build（薄新原語：`idioms-candidates` CLI + 框架 watcher + drain 步驟）**。

## 一、問題

三份 idioms 慣例文件（kotlin R1-R18 / vue R1-R13 / csharp R1-R12）會以兩種方式腐爛：

- **過時（stale）**：條文變錯——① `collectAsState` 建議變了、某條 `自訂`/`不可機檢` 現在 linter 原生支援了（**linter 演進**）；② 綁框架 API 版本的條款（Vue 3.5 `useTemplateRef`…）隨升版失準（**框架 API 演進**）。兩子型各有專屬 collector（C1a/C1b）。
- **缺漏（gap）**：該有的最佳實踐從沒進 R 清單。

文件自宣告的維護法（「飛輪：人工糾正一次就回填一條」）**沒有驅動力**——全靠人記得，實質不會發生。本計劃把「該回來複查」從「被記得」變成「被機械觸發」。

## 二、架構（方案 C'）

```
  C1a 寄生 lint-watch（消費治理層 lint-upgrades 輸出）─┐  linter 原生化 → stale
  C1b 框架版本 watcher（新薄原語:Vue/Kotlin/.NET 版本）┤  框架 API 演進 → stale
  C2  網搜收集器（獨立 refuter，非借 gapfill 專案反證）─┤  新最佳實踐 → gap（每週）
  C3  code-loop reviewer 加法旁註（不動 verdict）──────┘  反覆樣式 → gap
                    │ 各吐「候選」進 ↓
     共用池  idioms-candidates（可變狀態儲存，atomic rewrite + advisory lock；待建）
     (新造核心)     │  結構化 target_rule；stale 身分含版本
   refuter 預篩 ─── 專用留痕（記在候選記錄內，非 canary-record）：駁倒→rejected、駁不倒→screened
   (薄新原語)       │
   drain 步驟 ───── 獨立 governance 步驟（仿 lint-watch 形態:staging+LINE+人放行；非自主 loop 插槽）
   (薄新原語)       │  screened → 照房規完整 diff 草案 → idioms-proposals（governance/ 下待建）
                    └→ 人放行 → 改 idioms 文件 + 標 adopted（微調 trivial / 新 R 走 design-loop / 刪 R）
```

**元件邊界**

| 元件 | 職責 | 依賴 | 新造 |
|---|---|---|---|
| 候選池 | 可變狀態儲存（atomic rewrite），記來源/文件/種類/**target_rule**/狀態 | 純檔案 + fcntl advisory lock | ✅ 核心 |
| C1a/C1b/C2/C3 | 各把一種訊號轉統一候選寫進池，**只丟訊號不判對錯** | lint-upgrades 輸出 / 框架 registry / WebSearch / code-loop 旁註 | ✅ 薄 |
| refuter 預篩 | 每候選派 refuter 試駁 → screened/rejected（留痕記在候選內） | 借 gapfill **哲學**、自造留痕 | ⭕ 薄新原語 |
| drain | screened → 完整改文件草案 → governance staging | 仿 lint-watch **形態**、人放行 | ⭕ 薄新原語 |

核心原則：**collector 只丟訊號、不判對錯；判對錯統一交 refuter（機器初篩）+ 人（終判）**。三源無論多吵，品質由單一道閘守。（C3 的粗門檻是「訊號整形」不是「判涵蓋」——權威判斷仍在 refuter+人。）

## 三、元件規格

### 候選池
- `[S1]` 候選儲存 `idioms-candidates.json`（待建，置於 `governance/` 下），**可變狀態儲存**（非 append-only）：狀態轉移（pending→screened/rejected→adopted）以 **tmp 寫入 → 自驗 → atomic rename** 就地更新，避免 append-only 與可變 status 的矛盾。
- `[S2]` 候選 schema：`{id, source: lint-linter|framework|websearch|code-loop, doc: kotlin|vue|csharp, kind: stale|gap, target_rule, claim, evidence, refuter_verdict, status: pending|screened|rejected|adopted, ts, revised_from_to}`。**`target_rule` 為結構化欄位**（stale 指某條 R 號、gap 為 null 待分配），供去重與 drain 精確定位，不靠自然語言解析。
- `[S3]` 入池**單寫入者 + fcntl advisory lock** 防 check-then-act race。去重身分：**stale = `(doc, target_rule, tool/框架, from→to)`**（含版本——同版本重複則丟、新版本重新入池以利重驗）；**gap = `(doc, 正規化 claim)`**（正規化＝Unicode NFC + trim + lowercase，**只做機械近似**；跨源語意重複靠 drain 時人眼收，不宣稱機械收斂——見天花板）。比對現有 R 清單（讀三份 idioms 的 `R\d+` 標號）+ 池內既有候選（含 rejected/adopted）。

### C1a linter 演進收集器（寄生 lint-watch）
- `[S4]` **消費治理層 `lint-watch` 已去重的新候選輸出**（`governance/lint-upgrades/`，非原始 lint-watch JSON——避開重複通知/漏 seen 歷史）。依映射（detekt→kotlin / eslint→vue / NuGet analyzers[Roslyn·AsyncFixer·Meziantou]→csharp）吐 `kind=stale`。
- `[S5]` 候選是「複查指針」（`linter X 升 a→b，複查 <doc> 機檢欄有無條文從自訂/不可機檢變原生支援`）。**但指針本身不是可反駁 claim**——refuter 對 C1a 候選的差事是「翻該版 changelog 找具體 idioms 相關規則變動」，**找不到＝擱置（deferred）非駁倒**（避免把「檢索失敗」誤判成「無變動」的系統性假陰性）。

### C1b 框架版本 watcher（新薄原語）
- `[S6]` **新造薄 watcher**（round-1 決策加回）：讀 `.lumos/idioms-framework-watch.json`（`[{doc, framework, registry, current}]`，registry 用既有 lint-watch 的 `npm:vue` / `maven:org.jetbrains.kotlin:kotlin-stdlib` / `nuget:` 機制），機械查框架本身最新穩定版 vs 鎖定版，落後→吐 `kind=stale`（target_rule=null，claim 標「框架 X 升 a→b，複查綁該版 API 的條款」）。fail-open（網路失敗不升 rc）。**讓「框架 rot」有正確的 stale 來源**（補 §一 Vue 3.5 例的分類洞）。

### C2 缺漏收集器（獨立網搜，非借 gapfill 反證）
- `[S7]` WebSearch 找「某棧新最佳實踐、linter 沒收**且不在該 idioms R1-Rn**」→ 產 `kind=gap`。**每週觸發一次**。**不復用 gapfill 的「本專案不會踩→反證」邏輯**（那綁單一 repo，idioms 是跨專案通用，會錯殺通用候選）——C2 用**自己的 refuter 判準**（見 [S11]）。**與 `linter-gap實務隱患` 明確分池**：後者記專案級 gotcha、前者記跨專案通用 idioms 規則，職責不重疊、各自 refuter 判準不同。

### C3 code-loop reviewer 加法旁註（修正 round-1 blocker）
- `[S8]` **reviewer 照常產出完整 verdict**——所有真 bug（含無 idioms R 條號的 correctness/邊界/資源/例外/並發/impact 合約 finding）**全數照舊計入 verdict 與 severity**，verdict 解析、pre-push 硬擋邏輯**一字不動**（消除 round-1「無 R 真 bug 逃收斂閘」blocker 與相容性風險）。
- `[S9]` reviewer **額外**產一個**加法旁註區塊**（與 verdict 分離、不影響綠紅）：標記「本次審查中，哪些真 finding 反映了一個**反覆出現、值得升成一條 idioms 規則**的通用樣式」→ 該旁註條目進候選池 `source=code-loop, kind=gap`。旁註是 reviewer verdict 的**附加輸出**，不是把 finding 從 verdict 抽走。
- `[S10]` 旁註門檻寫死 framing（可辯護通用實踐、非品味）；產量異常高→log 提醒（framing 需收緊），不擋。**因旁註不 gate，即使誤標已存在的 R，refuter+人閘會接住，風險低。**

### refuter 預篩（薄新原語，自造留痕）
- `[S11]` 每候選派乾淨 refuter，**試駁不試證**（沿用 gapfill/canary 哲學）。判準依 kind：
  - **stale（C1a/C1b）**：翻 changelog 找具體 idioms 相關規則變動——找到→screened；**找不到→deferred（擱置重試），非 rejected**。
  - **gap（C2/C3）**：① R1-Rn 已涵蓋 ② 純品味非可辯護實踐 ③ **框架特定** 任一成立→駁倒。**「框架特定」判準明定**（消除 round-1 自相矛盾）：**可替換的第三方庫選擇**（Hilt/Koin、Pinia/Vuex、EF/Dapper）→ 駁回、進專案圖譜；**核心語言/官方框架的通用慣例**（Coroutines/Flow/Compose、Composition API、ASP.NET Core async）→ 收。對齊三份文件既有的「分層原則：不裁框架庫選擇」。
- `[S12]` 駁不倒→`status=screened`；駁倒→`status=rejected`+理由，**留在候選記錄內**（本池即去重記憶，同身分下次跳過）。**留痕自造**（記在候選 json 的 `refuter_verdict`），**不借 `lumos canary record`**（那是 loop 收斂專用、無候選語意，硬借會污染 `.canary-log`）。refuter 逾時/失敗→狀態留 `pending` + 記 `retry_after`，不卡死。

### drain（薄新原語，獨立 governance 步驟）
- `[S13]` **獨立 governance 步驟 `lumos idioms-drain`**（**非**自主 loop 的 N=1 gap 插槽——那是單工、有 pending 就不開新工，塞不進；改**仿 lint-watch 形態**掛 governance daily 排程，位置在 lint-watch 步驟**之後**以看到其 staged 輸出）。讀池取 `status=screened`，每筆產**照房規的完整 diff 草案**（固定用「已載入三份 idioms 房規」的 prompt 範本產出，防走鐘）：stale→改機檢欄/條文**或標刪除**；gap→一條新 R 含【壞例→好例 + 機檢欄 + 依據連結】。
- `[S14]` 草案 stage 到 `idioms-proposals（governance/ 下待建）`（**絕不自動改文件**）；LINE 通知「idioms 有 N 筆提案待放行」（N=0 靜默、不發空通知）。

### 人閘與落地
- `[S15]` 人放行後**三力度**：① 機檢欄換規則名/條文微調＝trivial，直接改→`adopted`；② **新增一條 R＝實質設計變更，走一輪 design-loop canary**（改 idioms＝改被全體專案引用的 spec）→ `adopted`；③ **整條 R 已不適用＝刪除**（stale 可導向刪除非只修改），走輕量人確認→`adopted`（補 round-1 缺的刪除路徑）。
- `[S16]` **自引用斷路**：design-loop 審 idioms 提案（力度②）期間，**C3 旁註收集器對該次審查關閉**（不回收自身產生的候選）；候選記 `provenance` 世代，禁止「桶 B 入池→採納成 R→同 finding 再影響原型別 verdict」的回授環。人閘 + 此斷路共同保證有限終止。
- `[S17]` `adopted` 候選**留池標記、不搬離**（搬離會讓 [S3] 去重讀不到、同 claim 再入池）；池增長靠「rejected/adopted 標記後可壓縮但恆保留身分鍵」控制。改 idioms 文件是否觸發既有 pre-commit gate、要求同步哪個節點——**列為實作期需 hook 實測確認項**（不假設）。

## 四、資料流

```
C1a lint-upgrades ─┐
C1b 框架 registry ─┼→ collector 吐候選(帶 target_rule) → lock+去重 → refuter 預篩 ┬ 駁不倒 → screened
C2  網搜(每週) ────┤                                                              ├ 駁倒 → rejected+理由(留池)
C3  reviewer 旁註 ─┘                                                              └ 檢索失敗 → deferred(重試)

governance daily(lint-watch 後): screened → 房規範本產完整 diff 草案 → idioms-proposals（governance/ 下待建） → LINE
   人放行 ┬ trivial 微調 → 改文件 + adopted
         ├ 新 R → design-loop canary(C3 旁註對本審查關閉) → 改文件 + adopted
         └ 刪 R → 輕量確認 → 改文件 + adopted
```

## 五、錯誤處理與天花板

**錯誤處理**：refuter 誤駁真缺漏→rejected 全留池、人可用 `lumos idioms-candidates list --rejected` 掃並 `--revive <id>` 撈回（附新 evidence 才重轉 screened）；併發→單寫入者 + fcntl advisory lock，check-then-act 全程持鎖；C1a/C1b 網路失敗→fail-open（deferred，不升 rc）；changelog 檢索失敗→deferred 重試非駁倒（避免系統性假陰性）；stale 版本識別含 from→to→同版本不重掃、新版本重驗；drain N=0→靜默；改文件與專案當地慣例衝突→沿用文件「當地贏、衝突記專案圖譜」。

**天花板（誠實邊界）**：
1. refuter 抓「版本沒變/已涵蓋/框架庫選擇」，抓不到「讀了但深層判錯」——是降雜訊摩擦地板，非 oracle。
2. 「還算不算最佳實踐」無機器 oracle，終究人/乾淨模型判；本機制只保證「該複查的不漏掉」，不保證「判得對」。
3. **去重只機械近似**：gap 跨源（C2 網搜散文 vs C3 旁註）語意等價無法純機械判，殘餘重複靠 drain 時人眼收——不宣稱機械收斂。
4. 飛輪仍需人糧：C3 要 code-loop 真在跑、真有人審 diff 才有旁註可撿；空轉專案不產糧。

## 實務隱患

- **C3 相容性（已解）**：改為加法旁註後 verdict 解析一字不動，無相容風險——但需測「旁註區塊缺失時 verdict 解析仍正常」。
- **併發寫入**：單寫入者 + fcntl advisory lock 選定；仍需定義崩潰恢復（半寫的 tmp 檔清理）與非 POSIX 平台（本工具鏈僅 macOS/Linux，Windows 不支援）。
- **框架 watcher 的 registry 覆蓋**：Vue（npm）清楚，Kotlin「框架」指什麼（語言？stdlib？Compose？）、.NET 指 SDK 還是 runtime——`.lumos/idioms-framework-watch.json` 要人工宣告清楚，覆蓋不保證完整。
- **drain 排程競跑**：需明訂 drain 在 daily-governance 腳本的**確切步序**（lint-watch 之後），避免與 lint-watch 同次產出的可見性競賽。
- **自引用終止**：[S16] 的斷路靠 provenance 世代 + 審查期關閉 C3——需測「design-loop 審 idioms 提案時不產生回授候選」。
- **與 gapfill/linter-gap 邊界**：C2 與 `linter-gap實務隱患` 已明定分池（[S7]）；但兩者都做網搜，需確認不重複燒 WebSearch（可共用一次搜尋、分流結果）。

## 六、測試策略

| 單元 | 測什麼 | 型 |
|---|---|---|
| 候選池 | atomic rewrite 狀態轉移正確；去重身分（stale 含版本／gap 正規化）生效；併發 lock 下無重複/半寫 | 純函式 + 併發 |
| C1a/C1b 映射 | linter→doc、框架 registry→doc 對；版本落後判定；fail-open | 純函式 |
| C3 旁註 | **verdict 不受旁註影響**（有無旁註，verdict/severity 相同）；旁註缺失 verdict 仍解析 | 行為 |
| refuter harness | 候選進→verdict 記候選內；駁倒→rejected+理由；stale 檢索失敗→deferred 非 rejected；框架庫選擇→駁回 | 行為 |
| drain | screened→產 idioms-proposals（governance/ 下待建） 草案、**斷言 idioms 文件未被自動寫**；N=0 靜默 | 行為 |
| 自引用斷路 | design-loop 審 idioms 提案期間 C3 不產回授候選 | 行為 |
| 端到端 dogfood | 種一筆真 stale（某 detekt 規則已原生）+ 一筆真框架 rot（Vue 3.5）+ 一筆真 gap，跑到 staging | E2E |

## 七、落地順序（建議）

1. 候選池 `idioms-candidates` CLI + schema + lock + 去重（`[S1][S2][S3]`）——地基。
2. C3 加法旁註（`[S8][S9][S10]`）——槓桿最大、不動既有 verdict/pre-push，風險低。
3. refuter 預篩薄原語 + 自造留痕（`[S11][S12]`）——借哲學不借 canary-record。
4. C1a 寄生 lint-upgrades（`[S4][S5]`）+ C1b 框架 watcher（`[S6]`）。
5. drain 薄原語 + governance 排程 + 人閘三力度 + 自引用斷路（`[S13][S14][S15][S16][S17]`）。
6. C2 網搜（`[S7]`）——與 linter-gap 分池、共用搜尋分流。
