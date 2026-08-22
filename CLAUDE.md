# CLAUDE.md
<!-- LUMOS:GRAPH-DISCIPLINE:START v1.0 — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->
## 核心原則：知識圖譜是這個專案的唯一真相來源——動手前先問圖譜（必讀，優先級最高）

**`docs/lumos-toolchain-knowledge/` 裡的筆記是本專案「為什麼這樣設計、邊界在哪、哪些不能改、驗證過沒」的唯一來源。** 程式碼只告訴你現在長怎樣；這些它讀不出來。

> **界線**：圖譜管的是意圖和宣告過的合約；「現在實際跑成什麼樣」以測試、實際執行、生產觀測為準。兩邊衝突不代表圖譜對——那是有東西壞了，查清哪邊錯，立一篇事故筆記。

### 🟢 第一個工具呼叫是 `lumos`，不是 grep / Read / Explore / 查 DB

**這條最常被跳過。** 你會很自然地想 grep 或讀檔去搞懂某個東西——停一下，下面這張表左邊是你當下在想的事，右邊是該先敲的指令。查完再 grep 印證。

| 你心裡想的是… | 先敲這個 |
|---|---|
| 「這個模組 / 欄位 / 流程為什麼這樣？」 | `lumos search <詞>` → `lumos context <節點>` |
| 「動這段之前有沒有什麼不能碰的？」 | `lumos contracts <節點>` |
| 「我要改 X，會波及什麼？」 | `lumos impact --file <檔>` 或 `--diff <範圍>` |
| 「哪些是金流 / 未收案 / 連到某節點的？」 | `lumos query --tag 家族/值 [--active] [--linked <節點>]` |
| 「這個詞圖譜記過嗎？」 | `lumos search <詞>`；0 命中先換同義詞，再說沒記 |
| 「我刪掉 / 改名了一個東西，筆記還在講它嗎？」 | `lumos search <舊名> --code` 逐句判 |
| 「當初為什麼這樣決定？翻案了嗎？」 | `lumos decisions <節點> [--superseded]` |
| 「這批改動要不要過審才能推？」 | `lumos pitfalls --diff <merge-base>..HEAD` 看 `tier:` |
| 「我 push 了，CI 跑得怎樣？」 | `lumos ci-wait` / `lumos ci-status` |
| 「做完了，要留紀錄、改狀態、記決策」 | `lumos new verification <名> --plan <計劃> --systems <節點>` / `lumos set` / `lumos decision-add`（開頭欄位別手改） |

不分任務類型：開發、重構、排查、對外支援、查 DB、對帳，全都算「進場」。兩個最常見的破口：① 把任務歸成「只是查個資料」就跳過；② 使用者說「直接改、不用解釋、很急」就跳過。**不解釋可以，不查不行**——進場那一下是 `lumos impact --file <檔>` 或 `lumos contracts <節點>` 一行，幾秒鐘，省了它你改到合約都不知道。

**完整指令索引**（80 個指令按「你正在做什麼」分八類，每類一個短檔，只開需要的那一個）：`lumos-project-notes` skill 的 `commands/INDEX.md`。Edit/Write 前 hook 會自動塞一份波及清單給你，但它只推你碰到的檔，邊界仍要自己查。

### 其餘原則

- **唯一真相，分層**：圖譜和其他文件 / 記憶 / 猜測衝突，以圖譜為準；和行為事實（測試、執行、生產觀測）衝突，不自動判圖譜對，查清哪邊錯、立事故筆記。
- **同一次工作內寫回**：改了會影響行為 / 決策 / 驗證的 code，同一次工作就把脈絡寫回圖譜（pre-commit 會擋「改 code 沒動圖譜」）。做完一定寫退場：決策、驗證、合約。
- **對人回報用白話**：摘要、結論、排查回報、設計討論，一律先一句人話或比喻，再往下講。術語和 file:line 能不用就不用，非用不可就當場一句解釋。細節收進圖譜。目標是讓人少一層理解成本，不是零術語。
- **設計動筆前先問世界（PRIOR-ART 三問）**：① 最小解在哪一層（既有機制小修就別造新機制）② 世界解過沒（真的搜，不憑印象）③ 裁定 = borrow-design（預設）/ build（真沒輪子）/ adopt（例外要理由，零依賴家規下幾乎不會選）。一行 `PRIOR-ART:` 記進計劃筆記。
- **已知行為測試先行、未知行為實驗先行**：能寫成規則的走 TDD；探索性的先做最小實驗，定案後補回歸測試。嚴禁為了滿足流程寫湊數測試。「實驗先行」的完成判準：講得出一道你已經跑過、會對這個症狀翻紅的指令（貼呼叫和輸出）之前，不准開始建理論——在那之前讀 code 找原因，就是這條規則要防的事。完整紀律見 `[[Systems/診斷迴圈先行]]`。
- **計劃 / 設計也歸圖譜**：任何設計、spec、計劃一律寫成 `Projects/<主題>_計劃` 筆記（`type: project`），不寫到別的路徑；落地的驗證紀錄用 `plan_refs` 指回來。

### 寫入圖譜（規範在 `lumos-project-notes` skill——動筆前先調用，別憑記憶）

標籤符號、合約鏈（★INVARIANT★→[test:]→[audit:]→[kill:]）、可逆性（★IRREVERSIBLE★ / ★CHECKPOINT★ 加 [rollback:] / [guard:]）、重建標記（regen）、決策、驗證紀錄、條款追溯（`lumos spec-trace`）、業務簽核（`lumos signoff`）的寫法都在那份 skill。這裡只留三條最容易出事的：

1. **不確定是不是合約就不要標**——嚴禁看著現在的 code 反推「這應該是合約吧」。
2. **多個連結一定寫成一行一項的清單**——擠成一串字會長出不存在的假筆記。
3. **開頭欄位一律用 `lumos set` / `append` / `decision-add` 改**，別手改。

> 寫完一篇跑 `lumos lint <節點>`；收工跑 `lumos doctor`；push 前 pre-push 會再擋一次（doctor、錨點檢查、高風險改動沒過代碼審）。

### 遇到這些情境就調用對應 skill（別憑記憶硬幹）

| 你正在做的事 | 調用 |
|---|---|
| 排查 / 對外支援 / 查 DB / 呼叫既有 API，動手前要懂為什麼、邊界、合約 | **`lumos-project-notes`**（先 search → context → contracts） |
| 讀圖譜 / 寫筆記 / 巡檢 / 綁合約測試 / 動 `docs/lumos-toolchain-knowledge/` | **`lumos-project-notes`** |
| 跨專案共用的業務規則（升格到核心庫、`core_refs`、偏離） | **`lumos-core-knowledge`** |
| 設計 spec 寫完、要進實作前：讓幾個不知道脈絡的審查員輪流挑毛病，`lumos loop next` 派席、`lumos loop status --disposal` 判過不過；小改動可跳過但要註明 | **`lumos-design-loop`** |
| 分支要推之前：`lumos pitfalls --diff <merge-base>..HEAD` 出 `tier: high` 就要過代碼審，審完 `lumos code-loop pass --note` 留痕才推得上去 | **`lumos-code-loop`** |

> 圖譜讀寫工具是 **lumos**（`scripts/lumos`，python3 零依賴）。`lumos-*` skill 的唯一來源在 `lumos-toolchain` repo，symlink 到 `~/.claude/skills/`；每台機器裝一次：`git clone <lumos-toolchain> ~/harness/lumos-toolchain && ~/harness/lumos-toolchain/install.sh`。專案技術棧 skill（如 vue / csharp）見文末〈架構參考 Skills〉。
<!-- LUMOS:GRAPH-DISCIPLINE:END -->
