---
type: project
status: doing
created: 2026-07-12
updated: 2026-07-12
tags:
  - type/project
  - status/doing
summary: |-
  FLOW:訊號源(lint-watch/網搜/code-loop棄稿)→collector吐候選→共用ledger→統一refuter預篩→自主loop drain產草案→人閘(實質新R走design-loop)→改idioms文件
  KEY:治病=idioms三份(kotlin/vue/csharp)會過時(版本變)或缺漏(新實踐沒收),既有「飛輪」靠人記得回填=實質不會發生;把「該回來複查」變機械觸發
  KEY:方案C(薄collector+共用池新造;refuter借gapfill、drain借自主loop、落點仿linter-gap)——vs A全新子系統(重造輪子)/B全走既有軌(候選散兩處破壞共用池)
  KEY:共用池=governance/idioms-candidates.jsonl(唯一sink,機器可解析);候選kind=stale|gap;去重鍵(doc,kind,正規化claim);rejected留池當去重記憶
  KEY:C3棄稿側通道——桶A(有R條號→review verdict照舊)桶B(無條號但可辯護→候選池);桶B不進verdict=去「多標多對」誘因;三道防傾倒閘
  KEY:refuter預設反方(試駁不試證,駁倒即丟);gap額外執行idioms範圍紀律(框架特定→駁回,擋文件膨脹)
  KEY:drain產「照房規完整diff草案」非指針(人成本壓到y/n);實質新R走design-loop canary,機檢欄微調屬trivial
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
---
# idioms自維護迴路_計劃

**PRIOR-ART:** 最小解在既有機制小修——refuter 借 gapfill、drain 借自主 loop、落點仿 `linter-gap實務隱患`；真沒輪子的只有「共用候選池 + 三個薄 collector」。裁定 = **build（僅收集層 + 池）+ borrow-design（refuter/drain/人閘沿用既有）**。世界解：doc-freshness 常態靠 CI + human review，無現成「idioms 自維護迴路」輪子可 adopt。

## 一、問題

三份 idioms 慣例文件（kotlin R1-R18 / vue R1-R13 / csharp R1-R12）會以兩種方式腐爛：

- **過時（stale）**：條文變錯——`collectAsState` 建議變了、某條 `自訂`/`不可機檢` 現在 linter 原生支援了、綁框架 API 版本的條款（Vue 3.5 `useTemplateRef`…）隨升版失準。
- **缺漏（gap）**：該有的最佳實踐從沒進 R 清單。

文件自宣告的維護法（「飛輪：人工糾正一次就回填一條」）**沒有驅動力**——全靠人記得，實質不會發生。本計劃把「該回來複查」從「被記得」變成「被機械觸發」。

## 二、架構（方案 C）

```
              ┌─ C1 過時收集器（寄生 lint-watch）
 三 collector ┼─ C2 缺漏收集器（gapfill 網搜，指向 idioms）
 (薄,新造)    └─ C3 缺漏收集器（code-loop 棄稿側通道）
                    │ 各吐「候選」進 ↓
        共用池  governance/idioms-candidates.jsonl   ← 唯一 sink
        (新造)      │
   統一 refuter ── 借 gapfill：駁倒→rejected(留池去重)、駁不倒→screened
   (借)             │
   drain 步驟 ───── 掛每日 09:30 自主 loop：screened→產完整 diff 草案→pending
   (借 loop+新一步) │
                    └→ 人放行 → 改 idioms 文件 + 標 adopted（實質新 R 走 design-loop）
```

**元件邊界**

| 元件 | 職責 | 依賴 | 新造 |
|---|---|---|---|
| 候選池 | append-only ledger，記來源/文件/種類/狀態 | 純檔案 | ✅ 核心 |
| C1/C2/C3 | 各把一種訊號轉統一候選寫進池，**不判對錯** | lint-watch 輸出 / WebSearch / code-loop reviewer 輸出 | ✅ 薄 |
| refuter 預篩 | 每候選派 refuter 試駁 → screened/rejected | gapfill 現成 refuter | ⭕ 借 |
| drain | screened → 完整改文件草案 → pending | 自主 loop dry-run 閘 + 人放行 | ⭕ 借+一步 |

核心原則：**collector 只丟訊號、不判對錯；判對錯統一交 refuter（機器初篩）+ 人（終判）**。三源無論多吵，品質由單一道閘守。

## 三、元件規格

### 候選池
- `[S1]` ledger 路徑 `governance/idioms-candidates.jsonl`，append-only，一候選一行。
- `[S2]` 候選 schema：`{id, source: lint-watch|websearch|code-loop, doc: kotlin|vue|csharp, kind: stale|gap, claim, evidence, refuter_verdict, status: pending|screened|rejected|adopted, ts}`。
- `[S3]` 入池去重鍵 `(doc, kind, 正規化 claim)`，比對「該文件現有 R 條號」+「池內既有候選（含 rejected）」，命中即丟。

### C1 過時收集器
- `[S4]` 寄生 lint-watch：其回報某 linter 落後時，依映射（detekt→kotlin / eslint→vue / Roslyn·AsyncFixer·Meziantou→csharp）吐 `kind=stale` 候選。
- `[S5]` 候選內容是「複查指針」非具體斷言（`linter X 升 a→b，複查 <doc> 機檢欄有無條文從自訂/不可機檢變原生支援、或條號行為有變`）；版本雜訊由 refuter 翻 changelog 過濾，收集層保持薄。
- `[S6]` **不新造框架版本 watcher**；框架 API 演進（Vue/Kotlin/.NET 本身升版）由 C2 網搜吸收。

### C2 缺漏收集器
- `[S7]` `lumos-pitfalls-gapfill` 換標的：WebSearch 找「某棧新 gotcha/最佳實踐、linter 沒收**且不在該 idioms R1-Rn**」→ 產 `kind=gap`。**每週觸發一次**（非每日 drain 都跑——三棧每日網搜過重且新實踐日級不會變；每週一次足夠且省 token）。

### C3 code-loop 棄稿側通道
- `[S8]` 改 code-loop reviewer 輸出契約成兩桶：**桶 A**（有 R 條號 findings）→ review verdict 照舊、決定綠紅；**桶 B**（無條號但可辯護的最佳實踐違反）→ 進候選池 `source=code-loop`。
- `[S9]` **三道防傾倒閘**：① 桶 B 不進 verdict（移除「多標多對」誘因）② 入桶 B 門檻寫死 framing（必須可辯護通用實踐、非品味，且確認 R1-Rn 無此條）③ refuter 再篩並對 gap 執行 idioms 範圍紀律。
- `[S10]` drain 時若某 reviewer 桶 B 產量異常高 → log 提醒（framing 可能需收緊），不擋。

### refuter 預篩
- `[S11]` 每候選派乾淨 refuter，**試駁不試證**（防帶風向，沿用 canary/gapfill 哲學）。stale：翻 changelog，找不到 idioms 相關規則變動→駁倒。gap：R1-Rn 已涵蓋／純品味／**框架特定（該進專案圖譜）** 任一成立→駁倒。
- `[S12]` 駁不倒→`status=screened`；駁倒→`status=rejected`+理由，**留池當去重記憶**（同 claim 下次跳過）。留痕走既有 `lumos canary record`，gov 可查。

### drain（自主 loop 新一步 `idioms-drain`）
- `[S13]` 讀 ledger 取 `status=screened`，每筆產**照房規的完整 diff 草案**（非指針）：stale→改機檢欄/條文；gap→一條新 R 含【壞例→好例 + 機檢欄 + 依據連結】。
- `[S14]` 掛 pending（套 loop 現有 dry-run 閘），**絕不自動改文件**；LINE 通知「idioms 有 N 筆維護提案待放行」（同 lint-watch 款）。

### 人閘與落地
- `[S15]` 人放行後兩力度：機檢欄換規則名/條文微調＝trivial，直接改→標 `adopted`；**新增一條 R＝實質設計變更，走一輪 design-loop canary**（改 idioms＝改被全體專案引用的 spec）→ 落地→標 `adopted`。
- `[S16]` 改 idioms 文件觸發既有 pre-commit gate（改文件帶圖譜同步），一致。

## 四、資料流

```
lint-watch bump ─┐
websearch ───────┼→ collector 吐候選 → 去重 → refuter 預篩 ┬ 駁不倒 → ledger:screened
code-loop 棄稿 ──┘                                          └ 駁倒 → ledger:rejected+理由(去重記憶)

每日 loop drain: ledger:screened → 完整 diff 草案 → pending → 人放行 ┬ trivial → 改文件 + adopted
                                                                    └ 新 R → design-loop canary → 改文件 + adopted
```

## 五、錯誤處理與天花板

**錯誤處理**：refuter 誤駁真缺漏→rejected 全留池、人可掃 rejected 撈回（同 gapfill 天花板）；C3 濫塞→三閘 + 產量 log；同 gap 雙源撈到→去重鍵收斂；lint-watch 網路失敗→fail-open 當天無 stale；池無限長大→rejected 靠去重不重撈、adopted 可歸檔、screened 堆積＝人放行跟不上（訊號非 bug）；改文件與專案當地慣例衝突→沿用文件「當地贏、衝突記專案圖譜」。

**天花板（誠實邊界）**：
1. refuter 抓「版本沒變/已涵蓋/框架特定」，抓不到「讀了但深層判錯」——是降雜訊摩擦地板，非 oracle。
2. 「還算不算最佳實踐」無機器 oracle，終究人/乾淨模型判；本機制只保證「該複查的不漏掉」，不保證「判得對」。
3. C1 版本訊號弱（多數升版與 idioms 無關），靠 refuter 過濾；框架演進靠 C2 網搜，覆蓋不保證完整。
4. 飛輪仍需人糧：C3 要 code-loop 真在跑、真有人審 diff 才有棄稿可撿；空轉專案不產糧。

## 六、測試策略

| 單元 | 測什麼 | 型 |
|---|---|---|
| 候選池 schema | 寫入格式合法、去重鍵生效（同 claim 兩次→一筆） | 純函式 |
| C1 映射 | detekt→kotlin / eslint→vue / roslyn→csharp | 純函式 |
| C3 側通道 | 桶 A/B 分離：一有條號+一無條號 → verdict 只含 A、池只含 B | 行為 |
| refuter harness | 候選進→verdict 記錄→駁倒轉 rejected+理由（LLM 不單元測，測骨架） | 行為 |
| drain | screened→產 pending 提案、**斷言文件未被自動寫** | 行為 |
| 端到端 dogfood | 種一筆真 stale（某 detekt 規則現已原生）+ 一筆真 gap，跑到 pending | E2E |

## 七、落地順序（建議）

1. 候選池 schema + 去重（`[S1][S2][S3]`）——地基，先立。
2. C3 棄稿側通道（`[S8][S9]`）——槓桿最大、長在既有 code-loop。
3. refuter 預篩接線（`[S11][S12]`）——借 gapfill。
4. C1 寄生 lint-watch（`[S4][S5][S6]`）——接線便宜。
5. drain + 人閘（`[S13][S14][S15]`）——掛自主 loop。
6. C2 網搜（`[S7]`）——最後，跟現有 gapfill dogfood 待辦合流。
