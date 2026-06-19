# core-content-baseline — 核心節點合約語意的下毒絆線(doctor Check C2)(設計)

> 狀態:**設計打磨完成、擱置實作**(2026-06-19)。canary-loop 4 輪(R1–R4,含 2 輪 opus)深度修補,**未達形式 K=2 收斂**(canary 在此 spec 反覆失靈,見下〈擱置決定〉);待全域核心合約節點 >1 再進實作。
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
          "valid_under": [{"text": "...", "hash": "..."}, {"text": "...", "hash": "..."}],
          "decisions":   [{"key": "2026-04-20", "text": "<content>", "hash": "..."}]
        },
        "approved_at": "...", "approved_by": "..."
      }
    }
  }
  ```
  - **節點路徑 key(解 R1-M3)**:相對 `core_base` 的 posix 路徑、NFC(`nfc()`),不含 repo 名前綴。
  - **decisions 穩定 key(解 R1-B4 + R2-B2 + R3-M2,改採唯一 decided、棄 #index)**:key = 該條 `decided` 日期。**`approve` 強制 `decided` 在該節點內唯一**——碰撞或缺 `decided` → `approve` **報錯要人補/區別**,不自動編 `#index`(R3-M2:`#index` 在 mid-list 刪除會位移、級聯假 diff)。改 `content` → 同 key、hash 變 → 「被動過」;增/刪一條 → key 增/減。
  - **valid_under(解 R3-M3,改內容集合、棄位置 i)**:逐條存 `{text, hash}`,**比對用 hash 集合(set)diff,不靠位置**——mid-list 刪一條 = 一個 hash 消失,不會級聯位移後續(位置 index 會)。
  - **hash**:`sha256(normalize(text))[:16]`(截斷 16 碼,實作為 module 常數 `BASELINE_HASH_LEN = 16`)。**存 text 本體**供報文顯示「舊→新」。
  - **`normalize(text)` 是本功能新增的 helper(解 R3-M1/M4,非 `load_vault` 的 `nfc`)**:`nfc` 只做 Unicode NFC、且只用在 path/stem,**不去空白**。本 `normalize` = strip 前後空白 + 全形空白(U+3000)轉半形/去除 + NFC。**且須對三類欄位一致**:`decisions[].content` 來自 `parse_decisions`(已 per-line strip + `\n`.join),`summary`/`valid_under` 來自 `note.fields`(未 strip)——`normalize` 要設計成對「已 strip 的 content」idempotent,使三類欄位走同一把正規化、hash 才可比。

### 單元 2 — `lumos baseline {approve,status}`

- **`lumos baseline approve [<node>]`**
  - **載入(解 R1-B2/M4 + R3-B3)**:對核心節點做解析**需要第二個 vault**——`approve`/Check C2 都先用 Check C 的定位邏輯(`CORE_KNOWLEDGE_ROOT` env 優先、否則 sibling 慣例)找到 `core_base`,再 **`Env(core_base)` / `load_vault(core_base)` 直建** transient Env。**(R3-B3 關鍵:core repo 沒有 `docs/*-knowledge` 結構(root 直接放 `Business/` 等),所以絕不可走 `find_vault`/`--vault` 解析(會回 `None`);必須 `Env(core_base)` 直建。)** **「重用既有解析」只成立在這個第二 vault 上**:Check C 本身只 `target.exists()`、不 parse 內容,內容解析是新 code path。
  - **不可重用的 helper(R3-B3)**:任何「從 vault root 推 `docs/` 父層」的 helper 對 core repo 會 misfire——`find_vault`(要 `docs/*-knowledge`)、`_append_governance_log`(寫 `vault.parent`,對 core repo = `backend/` 非 repo)、Check C 的 `repo_root` 找 `docs`。這些**不重用**;只重用 `core_base` 定位 + `load_vault`。
  - **欄位抽取的正確函式(解 R2-B1,地面事實已查證)**:`summary` / `valid_under` 走 `note.fields`(parse_frontmatter 對單值/字串 list 正確);**但 `decisions` 不可用 `note.fields["decisions"]`**——`parse_frontmatter` 的 `LIST_ITEM_RE` 對 nested dict 只抓每個 `-` 後首行,產出 garbage 字串 list。`decisions` **必須走專用的 `parse_decisions(note.fm_lines)`**(lumos line 1674,回傳含 `content`/`decided`/`valid` 的 dict list)。
  - **枚舉(解 R1-M1/M2 + R4-MAJOR1,按 type 過濾、非「欄位非空」)**:不給 node = 掃 `core_base` 的 `*.md`,**但只收 `type` 在核心合約集的節點(`core-business`;未來可加白名單)**。**(R4-MAJOR1:core repo 實際有 5 個 md,含一個 `type: verification` 的 DB 驗證節點、它有自己 verification-scope 的 `valid_under`;若按「欄位非空」收,Check C2 會擋到非合約的 Verification 節點,違反「只守核心」。必須按節點身份(type)過濾,不是欄位空否。)** 給 `<node>` = 只更那個(仍須通過 type 過濾)。
  - **寫入**:寫 `core_base/.lumos/core-content-baseline.json`,tmp-write + atomic rename(比照 guard bind 慣例)。記 `approved_at`、`approved_by`(解 R1-N2 + R3-m2,本功能**新**邏輯:`git config user.name`+`user.email`、**cwd 指定 consumer repo**(`env.vault`)以取對的作者,fallback `$USER`)。
  - **decided 唯一檢查(解 R3-M2)**:approve 前驗該節點 `decisions` 的 `decided` 兩兩相異且非空;違反 → 報錯中止,不寫 baseline。
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
- **比對**:`Env(core_base)`,對每個核心節點:
  - `summary`:單值比 hash(異 → 被動過,報舊→新)。
  - `decisions`:按 `decided` key 配對——同 key hash 異 → 被動過;key 只在當前 → 新增;只在 baseline → 刪除。
  - `valid_under`:**hash 集合 diff(R3-M3)**——當前有 baseline 無 → 新增;baseline 有當前無 → 刪除;改一條 = 一刪一增。不靠位置。
  - 任一未 approve 的差異 → block;全相符 → 過。報文舊文取自 baseline 存的 `text`。
- **硬度(解 R3「issues 註記」)**:差異計入 `issues`。但 lumos `doctor` 的退出碼**只在 `--ci`/`strict` 時隨 issues 非 0**;bare `lumos doctor` 即使 issues>0 仍 exit 0。**pre-push 走 `--ci` → 硬擋成立**。故文件只宣稱「pre-push / `--ci` 擋」,不宣稱「bare doctor 非 0」。approve 後重算相符 → 綠。

## 跟既有 Check 的分工

| Check | 守什麼 |
|---|---|
| Check C(既有) | core_refs 指針「**檔案在不在**」(連結完整) |
| **Check C2(新)** | core_refs 指到的核心節點「**合約語意欄位有沒有被靜默改**」(內容完整) |
| Check T(既有) | ★INVARIANT★ 有沒有綁可執行測試 |
| Check R(既有) | 不可逆動作有沒有寫回退 |

**`baseline approve` 留痕的正確位置(解 R3-B2/M5,推翻 R1-N6 的含糊版)**:approve 寫到**執行端 consumer vault 的 `<env.vault>/../.governance-log.jsonl`**(即 `lumos gov` 讀得到的那份),**不是** core_base——因為 ① core repo 無 `docs/` 層、`_append_governance_log` 的 `vault.parent` 會落在 `backend/`(非 repo),② `lumos gov` 只讀 consumer vault 的那份、看不到 core repo 的。approve **自寫 append**,**event schema 須對齊既有 gov reader(R4-MAJOR2)**——reader(lumos:1130)讀 `{gate, kind, nodes[](list), hard}`,故寫 `{"ts":..., "commit":..., "gate":"baseline", "kind":"approved", "hard":false, "nodes":[<node>], "approved_by":...}`;**不可**用 `{event, node}`(單數 `node` + 鍵名 `event` → reader 解成 `?/?/空 nodes`、`gov <node>` 篩不到)。**不重用** `_append_governance_log`(它 ① gate 在 doctor 的 `--ci` call site、② 無 git commit 時早退——正是 CI-checkout 情境會吞掉留痕)。`ts` 用 `datetime.now().astimezone().isoformat(timespec="seconds")`(**非** `time.time()` epoch,R4-MINOR1:reader 以 `ts[:10]` 比日期,epoch 會被 90 天窗濾掉)。如此 approve 史才真進 `gov` ledger、可追蹤(對齊 loop engineering)。

## 誠實天花板

- **只證沒被靜默改,不證語意對不對**:baseline 只證「這欄字自上次 approve 沒變」,**不證那條規則本身對不對**(同 Check T 的 verification≠validation 邊界)。
- **擋靜默改,擋不了明知故改**:hash tripwire 只擋「沒人注意的改」;擋不了「明知故改 + 隨手 `approve` 過」。它抬的是「核心改動必須經過一次**顯式停頓 + 留痕**」的地板,不是 oracle。
- **守備靠標記、且現在對象極少**:範圍靠節點 `type`(核心合約集);目前全域**僅 1 個核心合約節點**,守備價值隨核心知識成長才放大(對齊 lumos_計劃「等 core_refs 變多再做」——v2 因「立刻守得到那 1 個 + 隨成長擴大」而仍值得現在做,但不誇大覆蓋)。
- **留痕不對稱(R4-MINOR2)**:baseline 住**共用的 core repo**,但 approve 留痕寫**執行端 consumer vault 的 governance-log** → consumer A 的 approve 對 consumer B 的 `lumos gov` 不可見(B 卻已吃到 A 改的 baseline)。approve provenance 不像 baseline 那樣全域可見;升格時可考慮在 core repo 旁也留一份 provenance。

## 測試策略

合成 core-knowledge repo + baseline:
- 改一條 `decisions[].content` → Check C2 block;`approve` 後 → 綠。
- 改 `summary` → block。
- 新增一條 `valid_under` 未 approve → block;刪一條 → block。
- **刪「中間」一條 decision / valid_under(解 R3-M2/M3)→ 只報該條刪除,不級聯誤報後續條目「被動過」**(驗證集合/唯一-key 比對沒退化成位置比對)。
- **decided 碰撞/缺失 → `approve` 報錯中止**(R3-M2);approve 留痕後 **`lumos gov` 從 consumer vault 讀得回該 `baseline-approve` 事件**(R3-B2 落點正確性)。
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

### R3(2026-06-19,canary 類型 c=未定義常數,**opus**(連2 missed 升級),caught)
**升 opus 奏效**:canary(`BASELINE_HASH_LEN` 未定義常數)被**正確抓到**——opus 在 finding B1 點明「named-but-never-defined」並附完整識別符清查表標其為「the defect」,還順手揪出兩輪 sonnet 沒碰的深層真錯。worst real = blocker。全部折入:
- **blocker**:**B2** approve 留痕落點錯——`_append_governance_log` 寫 `vault.parent`,對 core repo = `backend/`(非 repo)、`gov` 讀不到、無 commit 早退 → 改寫 **consumer vault 的 governance-log**、自寫 append 不重用該 helper;**B3** core repo 無 `docs/*-knowledge` 結構 → transient Env 須 `Env(core_base)` 直建、不走 `find_vault`;列不可重用的 docs/-假設 helper。
- **major**:**M1** `normalize` 是新 helper(非 `load_vault` 的 `nfc`,後者不去空白);**M2** decisions `#index` mid-list 刪除級聯 → 改「decided 唯一、碰撞報錯」;**M3** `valid_under` 位置 index 同樣級聯 → 改 hash 集合 diff;**M4** content(parse_decisions 已 strip/join)vs summary/valid_under(note.fields 未 strip)正規化不一致 → normalize 三欄一致;**M5** `--ci` gating 與 `_append_governance_log` call site 矛盾 → approve 自寫。
- **near-blocker 註記**:bare `lumos doctor` 即使 issues>0 exit 仍 0(只 `--ci`/`strict` 非 0)→ 文件只宣稱「pre-push/`--ci` 擋」。
- **minor**:m1 core_refs 不驅動枚舉(枚舉=掃 core_base,core_refs 只證哪 repo 是 core);m2 approved_by 標為新邏輯 + cwd=consumer;m3 測試補 mid-list 刪除 / gov 讀回 / decided 碰撞。

## 擱置決定(2026-06-19,user 選 A)

設計經 4 輪 canary-loop(含 2 輪 opus)深度打磨,從 v1「守空集合」的致命前提錯,修到欄位級、整合層全對齊現實(枚舉按 type 過濾、event schema 對齊 gov reader、core repo 無 docs 結構、normalize 三欄一致、decided 唯一 key、valid_under 集合 diff…)。**但決定先擱置實作**,理由:
1. **守備對象現在只有 1 個**核心合約節點(`custtransfer-semantics`)——對齊 lumos_計劃 既有判斷「等 core_refs/核心節點變多再做」。
2. **此 loop 揭發 canary 機制的限制**:4 輪 3 次 canary 出問題(R1/R2 漏抓——審計員注意力被密集真問題吃滿;R4 不公平——type d「憑空產物」對合理 self-contained 新功能不適用)。真正接住設計缺陷的是「真 findings + 手動查證」,非 canary。此 spec 的形式 K=2 收斂,canary 提供的保證很弱,硬刷投報率低。

**meta 留作 loop-engineering 反饋**:canary missed 率該當可追蹤指標;canary 類型需分 spec 性質校準;「真 findings 數」可能比「canary caught」更可靠反映審計品質。對比同日 rot-eval loop(canary 5/5、5 輪乾淨收斂)——同一機制在不同 spec 上可信度差異巨大。

> 重啟條件:核心合約節點 >1(或新增 core_refs 消費端)時,本 spec 已 ready,接 writing-plans 即可。
