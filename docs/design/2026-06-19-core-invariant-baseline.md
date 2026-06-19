# core-invariant-baseline — 核心鐵則行的下毒絆線(doctor Check B)(設計)

> 狀態:草稿(canary-護審計 loop 待跑)｜日期:2026-06-19
> 觸發:2026-06-19 治理日報 gap 2 ——「共通節點是多人共編的共享記憶,卻沒有『退回上一版良好狀態』的機制,一筆寫錯會沿連結擴散給全部 agent」。
> 外部依據:多 agent 記憶污染研究 / OWASP Agent Memory(已知良好快照 + 完整性校驗)。
> 區分:**不是** Check R(那撤的是「世界動作」:上架/prod 遷移);這守的是「**記憶狀態**」——核心鐵則行被靜默改寫。

## 目標(一句話)

給**跨專案核心知識**(`core_refs` 指到的核心節點)的每條 `★INVARIANT★` 行算 hash、存進**人工 approve 的 baseline**;doctor 新增 **Check B** 比對「當前 vs baseline」,核心鐵則行被靜默改/增/刪且未 approve → **hard block**,放行只能靠顯式 `lumos baseline approve`(留痕)。

## 為什麼需要(現況缺口)

改一條核心 `★INVARIANT★` 的**合約宣稱文字**:不會破連結、不會讓 `lumos doctor` 變紅(doctor 現有的 Check C/T/R 都不看「鐵則文字本身有沒有被動過」)、grep 也搜不出異常。於是一筆改錯的核心鐵則**靜默變成所有下游 session 的真值**,沿 `core_refs` / wikilink 擴散,沒人會發現它被動過。git 本來就留歷史(revert 是 git 的事),**缺的不是 revert,是「偵測 + 顯式 approve 閘」**。

## 邊界 / 非目標(YAGNI)

- **只比 `★INVARIANT★` 行**,不比節點全文。
- **只守核心節點**(`core_refs` 指到的 / core-knowledge repo 內),不守一般 repo 的 ★INVARIANT★(2026-06-19 user 選定:最高槓桿、基線維護成本最低)。
- **只 hard block**,不做軟硬分級(user 選定)。
- **不自動 revert**(git 的事);**不自動更新 baseline**(關鍵:不能用「doctor 綠就更新」,因為本場景正是「改壞但 doctor 照樣綠」,自動更新=自動吞下下毒)。

## 三個單元

### 單元 1 — baseline 檔

- **位置(2026-06-19 確認 a)**:存在**被守的 core-knowledge repo** 的 `.lumos/invariant-baseline.json`(不是各使用端 repo)——多專案共用同一份基線。
- **結構**:
  ```json
  {
    "version": 1,
    "nodes": {
      "<節點相對路徑>": {
        "hashes": ["<sha256 前16碼>", "..."],
        "approved_at": "2026-06-19T..","approved_by": "<人或 agent 標記>"
      }
    }
  }
  ```
- **hash 算什麼(設計定法,留 loop 戳)**:只 hash 該 `★INVARIANT★` 行的**合約宣稱本體**——**剝掉**行尾的 `[test:...]` / `[audit:...]` 指針再 normalize(去前後/全形空白)。理由:`[test:]`/`[audit:]` 的變動是 Check T / audit 流程的正常更新,不該觸發 Check B 假陽;Check B 只盯「合約這句話本身」有沒有被動。
- 重用 lumos 既有的 ★INVARIANT★ 解析(Check T / `contracts` / guard 用的同一套),不另寫 parser。

### 單元 2 — `lumos baseline {approve,status}`

- `lumos baseline approve [<node>]`:把當前核心節點的 ★INVARIANT★ 行 hash 寫進 baseline(不給 node = 全部核心節點;給 node = 只更那個),記 `approved_at`/`approved_by`。**寫後自驗**(對齊 guard bind/set 的慣例)。
- `lumos baseline status`:列當前 vs baseline 的 diff(被動過 / 新增 / 刪除 / 一致),唯讀。
- 二層命令,對齊既有 `guard bind` / `canary record` / `loop status`。

### 單元 3 — doctor Check B

- **何時跑(2026-06-19 確認 b)**:能定位到 core-knowledge repo 且其 `.lumos/invariant-baseline.json` 存在時跑;**核心 repo 不在此環境(CI 未 checkout)→ 跳過不誤判**(完全比照既有 Check C 的 repo 定位邏輯:`CORE_KNOWLEDGE_ROOT` env 優先,否則 sibling 慣例)。baseline 檔不存在(從沒 approve 過)→ 提示「首次需 `lumos baseline approve` 建基線」,不當 block。
- **比對演算法(「被改一條」怎麼識別)**:baseline 存「節點 → 核心 ★INVARIANT★ 行 hash 集合」。doctor 算當前集合,對比:
  - 當前有、baseline 沒有 → **新增**鐵則行(未 approve → block)
  - baseline 有、當前沒有 → **被刪或被改**(改 = 舊 hash 消失 + 新 hash 出現)→ block
  - 兩集合相等 → 過
  - 報文:`節點 X:1 條核心鐵則被動過(舊「<48字>」→ 新「<48字>」);確認對的話跑 lumos baseline approve X`
- **硬度**:被動過且未 approve → 計入 `issues`(hard block),doctor 非 0、pre-push 擋。approve 後重算 hash 相符 → 綠。

## 跟既有 Check 的分工

| Check | 守什麼 |
|---|---|
| Check C(既有) | core_refs 指針「**檔案在不在**」(連結完整) |
| **Check B(新)** | core_refs 指到的核心節點「**★INVARIANT★ 行內容有沒有被靜默改**」(內容完整) |
| Check T(既有) | ★INVARIANT★ 有沒有綁可執行測試 |
| Check R(既有) | 不可逆動作有沒有寫回退 |

Check C 守連結、Check B 守內容,互補。`baseline approve` 留痕(誰/何時)可進 `gov` ledger → 可觀測(對齊 loop engineering:核心改動的 approve 史變可追蹤的率)。

## 誠實天花板(寫進報文/文件)

- **只證沒被靜默改,不證鐵則對不對**:baseline 只證「這條鐵則行的字自上次 approve 沒變」,**不證那條鐵則本身對不對**(同 Check T 的 verification≠validation 邊界)。
- **擋靜默改,擋不了明知故改**:hash tripwire 只擋「沒人注意的改」;擋不了「明知故改 + 隨手 `approve` 過」。它抬的是「核心改動必須經過一次**顯式停頓 + 留痕**」的地板,不是 oracle。
- **守備靠標記**:範圍靠 `core_refs` / core-knowledge 歸屬;沒被標成核心的高槓桿節點不在守備內。

## 測試策略

- 合成 core-knowledge repo + baseline:
  - 改一條核心 ★INVARIANT★ 的合約宣稱 → Check B 報 block;`approve` 後 → 綠。
  - 新增一條核心 ★INVARIANT★ 未 approve → block。
  - 刪一條 → block。
  - **只動行尾 `[test:]`/`[audit:]` 指針** → **不**觸發(hash 剝指針)。
  - **只動空白/全形空白** → normalize 後**不**假陽。
  - 核心 repo 不在環境 → Check B 跳過(不誤判)。
  - baseline 檔不存在 → 提示建基線、不 block。
- `lumos baseline status` 的 diff 分類(被動過/新增/刪除/一致)各一例。

## 落地形態

**直接進 lumos**(不像 rot-eval 是離線評測)——因為要接 doctor/pre-push 的硬閘。實作順序:① baseline 檔讀寫 + `approve` → ② `status` diff → ③ doctor Check B 比對 + hard block → ④(次要)approve 留痕進 gov。

## 審計修正紀錄

(canary-護審計 loop 跑完後補)
