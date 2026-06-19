# core-content-baseline — 核心節點合約語意的下毒絆線(doctor Check C2)(設計)

> 狀態:草稿 v2(R1 canary-loop 揭發前提錯誤後 pivot;canary-護審計 loop 待續跑 R2+)｜日期:2026-06-19
> 觸發:2026-06-19 治理日報 gap 2 ——「共通節點是多人共編的共享記憶,卻沒有『退回上一版良好狀態』的機制,一筆寫錯會沿連結擴散給全部 agent」。
> 區分:**不是** Check R(撤「世界動作」);守的是「**記憶狀態**」——核心節點的合約語意被靜默改寫。

## v2 pivot 說明(必讀)

v1 設計「守核心節點的 `★INVARIANT★` 行」**前提是錯的**:R1 審計 + 獨立 grep 證實 `citrus-core-knowledge` 全 repo **0 條 ★INVARIANT★**、全 vault **1 條 core_refs**——核心節點承載合約語意的是 `summary` / `decisions[].content` / `valid_under`,**不是** ★INVARIANT★ KEY 行。v2 把守備對象改成這些**實際承載語意的欄位**,tripwire / hard-block+approve 概念全照舊,且立刻守得到唯一的核心節點 `citrus-core-knowledge/Business/member/custtransfer-semantics.md`,並隨核心知識成長自動擴大。

## 目標(一句話)

給**跨專案核心知識**(`core_refs` 指到、住在 core-knowledge repo 的節點)的**合約語意欄位**算 hash、存進**人工 approve 的 baseline**;doctor 新增 **Check C2** 比對「當前 vs baseline」,語意欄位被靜默改/增/刪且未 approve → **hard block**,放行只能靠顯式 `lumos baseline approve`(留痕)。

## 為什麼需要(現況缺口)

改一條核心節點的 `summary` 或某條 `decisions[].content`:不會破連結、不會讓 doctor 變紅(現有 Check C/T/R 都不看「核心語意文字有沒有被動過」)、grep 也搜不出異常。於是一筆改錯**靜默變成所有下游 session 的真值**,沿 `core_refs`/wikilink 擴散。git 本來就留歷史(revert 是 git 的事),**缺的不是 revert,是「偵測 + 顯式 approve 閘」**。

## 守備欄位(明確列舉,對齊真實 schema)

守核心節點這三類**承載「規則是什麼 / 邊界在哪」**的欄位:
- `summary`(一句話核心語意)
- `decisions[].content`(每條 ADR 的決策本體)
- `valid_under`(list,合約成立條件,逐條)

**v1 不守**(留升格):`context` / `why_chosen` / `trade_offs` / `alternatives_considered`(決策*理由*,改寫風險較低、變動較頻繁,守了假陽多);`revalidate_when` / `verified_by`(流程性,非合約本體)。

## 邊界 / 非目標(YAGNI)

- **只守上列三類欄位**,不守節點全文、不守理由欄。
- **只守核心節點**(core-knowledge repo 內 / core_refs 指到),不守一般 repo(user 選定:最高槓桿、基線維護成本最低)。
- **只 hard block**,不做軟硬分級(user 選定)。
- **不自動 revert**(git 的事);**不自動更新 baseline**(關鍵:不能「doctor 綠就更新」,本場景正是「改壞但 doctor 照綠」,自動更新=自動吞下下毒)。

## 三個單元

### 單元 1 — baseline 檔

- **位置(確認 a)**:存在**被守的 core-knowledge repo** 的 `.lumos/core-content-baseline.json`(不是各使用端 repo)——多專案共用同一份。
- **結構(解 R1-B3「報文要舊文」+ B4「行身份/有序」:存 text 與 hash,decisions 有序帶穩定 key)**:
  ```json
  {
    "version": 1,
    "nodes": {
      "Business/member/custtransfer-semantics.md": {
        "fields": {
          "summary":     {"text": "...", "hash": "<sha256前16>"},
          "valid_under": [{"i": 0, "text": "...", "hash": "..."}, {"i": 1, "...": "..."}],
          "decisions":   [{"key": "2026-04-20", "text": "<content>", "hash": "..."}]
        },
        "approved_at": "...", "approved_by": "..."
      }
    }
  }
  ```
  - **節點路徑 key(解 R1-M3)**:相對 `core_base` 的 posix 路徑、NFC 正規化(比照 `load_vault` 的正規化),不含 repo 名前綴。
  - **decisions 穩定 key(解 R1-B4 + R2-B2)**:用該條的 `decided` 日期;同日多條則 `decided#<index>`,**index = `parse_decisions` 的 append(原始行)順序**(已查證 `parse_decisions` 依 raw line order;假設新決策附加在尾端,故既有 key 穩定)。**缺 `decided` 的決策** → key 用 `noDate#<index>`(同樣 append 序)。改 `content` → 同 key、hash 變 → 「被動過」;新增/刪一條 → key 增/減。此順序假設寫進測試。
  - **valid_under**:list 逐條存 `{i, text, hash}`(有序),逐條比對能定位哪條被改。
  - **hash**:`sha256(normalize(text))[:16]`;normalize = 去前後/全形空白 + NFC。**存 text 本體**供報文顯示「舊→新」。

### 單元 2 — `lumos baseline {approve,status}`

- **`lumos baseline approve [<node>]`**
  - **載入(解 R1-B2/M4)**:對核心節點做解析**需要第二個 vault**——`approve`/Check C2 都先用 Check C 的定位邏輯(`CORE_KNOWLEDGE_ROOT` env 優先、否則 sibling 慣例)找到 `core_base`,再 `load_vault(core_base)` 建一個 transient Env。**「重用既有解析」只成立在這個第二 vault 上**:Check C 本身只 `target.exists()`、不 parse 內容,內容解析是新 code path(這點 v1 含糊,v2 明確)。
  - **欄位抽取的正確函式(解 R2-B1,地面事實已查證)**:`summary` / `valid_under` 走 `note.fields`(parse_frontmatter 對單值/字串 list 正確);**但 `decisions` 不可用 `note.fields["decisions"]`**——`parse_frontmatter` 的 `LIST_ITEM_RE` 對 nested dict 只抓每個 `-` 後首行,產出 garbage 字串 list。`decisions` **必須走專用的 `parse_decisions(note.fm_lines)`**(lumos line 1674,回傳含 `content`/`decided`/`valid` 的 dict list)。
  - **枚舉(解 R1-M1/M2)**:不給 node = **掃描整個 core_base 的 `*.md`**(經 `load_vault`),不是只取 consumer 的 core_refs union(後者會漏掉沒人指的核心節點)。給 `<node>` = 只更那個。
  - **寫入**:寫 `core_base/.lumos/core-content-baseline.json`,tmp-write + atomic rename(比照 guard bind 慣例)。記 `approved_at`、`approved_by`(解 R1-N2:取 `git config user.name`+`user.email`,fallback `$USER`)。
  - **寫後自驗(解 R1-M5)**:重讀 baseline、對同節點重算 hash,assert 與寫入值相符。
  - **空欄位(解 R1-N3)**:節點三類欄位全空 → 警告並跳過、**不寫空 entry**(空節點不是「守得到的」節點)。
  - **`<node>` 參數格式(解 R1-N5)**:相對 `core_base` 的 posix 路徑(= baseline key),或 stem;給例子。
- **`lumos baseline status`**:列當前 vs baseline 的 diff,唯讀。輸出四類(解 R1-N4):
  ```
  Business/member/custtransfer-semantics.md
    ✓ summary               一致
    ⚠ decisions[2026-04-20] 被動過  舊「會員點數異動採…」→ 新「…」
    + valid_under[2]        新增(未 approve)
    - decisions[2026-04-22] 刪除(baseline 有、當前無)
  ```

### 單元 3 — doctor Check C2

- **命名(解 R1-N1)**:叫 **Check C2**(緊鄰既有 Check C、表達「C 守指針存在、C2 守指到的內容」),在 `run_doctor` 中**接在 Check C 之後**插入(同一個 `core_base` 定位,順著用)。
- **何時跑(確認 b)**:能定位 `core_base` 且其 `.lumos/core-content-baseline.json` 存在時跑;**核心 repo 不在環境(CI 未 checkout)→ 跳過不誤判**(比照 Check C);baseline 不存在 → 提示「首次需 `lumos baseline approve` 建基線」,不當 block。
- **比對**:`load_vault(core_base)`,對每個核心節點逐欄位/逐 decision/逐 valid_under 條目比 hash:
  - 當前有、baseline 無 → 新增(未 approve → block)
  - baseline 有、當前無 → 刪除 → block
  - 同 key 但 hash 異 → 被動過(報舊→新,舊文取自 baseline 存的 text)→ block
  - 全相符 → 過
- **硬度**:任一被動過/增/刪未 approve → 計入 `issues`(hard block),doctor 非 0、pre-push 擋。approve 後重算相符 → 綠。

## 跟既有 Check 的分工

| Check | 守什麼 |
|---|---|
| Check C(既有) | core_refs 指針「**檔案在不在**」(連結完整) |
| **Check C2(新)** | core_refs 指到的核心節點「**合約語意欄位有沒有被靜默改**」(內容完整) |
| Check T(既有) | ★INVARIANT★ 有沒有綁可執行測試 |
| Check R(既有) | 不可逆動作有沒有寫回退 |

`baseline approve` 一律 append `.governance-log.jsonl`(**不** gate 在 `--ci`,解 R1-N6):`{event:"baseline-approve", node, approved_by, ts}` → 進 `gov` ledger,核心改動的 approve 史變可追蹤(對齊 loop engineering)。

## 誠實天花板

- **只證沒被靜默改,不證語意對不對**:baseline 只證「這欄字自上次 approve 沒變」,**不證那條規則本身對不對**(同 Check T 的 verification≠validation 邊界)。
- **擋靜默改,擋不了明知故改**:hash tripwire 只擋「沒人注意的改」;擋不了「明知故改 + 隨手 `approve` 過」。它抬的是「核心改動必須經過一次**顯式停頓 + 留痕**」的地板,不是 oracle。
- **守備靠標記、且現在對象極少**:範圍靠 `core_refs`/core-knowledge 歸屬;目前全域**僅 1 個核心節點**,守備價值隨核心知識成長才放大(對齊 lumos_計劃「等 core_refs 變多再做」——v2 因「立刻守得到那 1 個 + 隨成長擴大」而仍值得現在做,但不誇大覆蓋)。

## 測試策略

合成 core-knowledge repo + baseline:
- 改一條 `decisions[].content` → Check C2 block;`approve` 後 → 綠。
- 改 `summary` → block。
- 新增一條 `valid_under` 未 approve → block;刪一條 → block。
- **只動 `context`/`why_chosen` 等理由欄** → **不**觸發(不在守備欄)。
- **只動空白/全形空白** → normalize 後**不**假陽。
- 核心 repo 不在環境 → Check C2 跳過(不誤判)。
- baseline 不存在 → 提示建基線、不 block。
- 節點三類欄位全空 → `approve` 警告跳過、不寫空 entry。
- `baseline status` 四類 diff 各一例。

## 落地形態

**直接進 lumos**(要接 doctor/pre-push 硬閘)。實作順序:① `core_base` 定位 + `load_vault` 第二 vault + 欄位抽取/hash → ② `baseline approve`(寫 + 自驗 + 枚舉)→ ③ `baseline status` diff → ④ doctor Check C2 比對 + hard block → ⑤ approve 留痕進 gov。

## 審計修正紀錄

### R1(2026-06-19,canary 類型 a=壞§ref,sonnet,**MISSED**)
canary(植入〈附錄 A — Check B 狀態機〉壞引用)**漏抓**——審計員太投入找真問題、沒點出該植入瑕疵 → 按 loop 紀律該輪判決不採信、不機械折入。**但** R1 揭發的 **B1**(核心節點 0 條 ★INVARIANT★、設計守空集合)經**獨立 grep 查證為地面事實**,推翻 v1 前提 → 觸發本次 v2 pivot(守備對象改 summary/decisions/valid_under)。重寫時一併主動採納我獨立判斷為真的 R1 findings:B2(第二 vault load)、B3(baseline 存 text 供報舊文)、B4(decisions 有序+穩定 key)、M1/M2(approve 枚舉=掃 core_base)、M3(路徑 key 相對 core_base+NFC)、M4(reuse 只指定位、解析是新 path)、M5(寫後自驗)、N1(命名 Check C2)、N2(approved_by 來源)、N3(空欄位跳過)、N4(status 輸出格式)、N5(node 參數格式)、N6(gov 不 gate --ci)。
> 教訓記:寫 spec 前未先 grep 核心節點實際 schema 就假設有 ★INVARIANT★——接住的是手動查證,非 canary。canary 漏抓示範其「地板非 oracle」的限制。

### R2(2026-06-19,canary 類型 b=未定義旗標,sonnet,**MISSED**)
canary(植入未定義旗標 `--strict`)**漏抓**——審計員注意到 `--strict`(N3 當它冗餘真 flag)與 canary 註解(M4 當殘留垃圾),但**未正確點出「`--strict` 是憑空未定義旗標」的瑕疵性質** → 按「光 token 不算、要點性質」判 missed,該輪判決不採信、不機械折入。**連 2 輪 missed → 護欄觸發:R3 升 opus。** 兩輪 sonnet 都因 spec 技術細節密集、注意力被真問題吃滿而漏 canary。
> 但 R2 揭發、經**獨立查證為地面事實**者先修:**B1**(`decisions` 須走 `parse_decisions(note.fm_lines)`,非 `note.fields["decisions"]`——後者對 nested dict 產 garbage)、**B2**(`decided#index` 用 append 序、缺日期用 `noDate#index`)。其餘(M2 gov-log 位置/git context、M3 approve 的 --vault context、N1-N5)未折,留 opus R3 重審。
