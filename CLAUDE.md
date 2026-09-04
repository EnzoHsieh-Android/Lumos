# CLAUDE.md
<!-- LUMOS:GRAPH-DISCIPLINE:START v1.0 — 自動注入/更新,勿手改本區塊;改範本 scripts/templates/graph-discipline.md -->
## 知識圖譜先行（必讀，優先級最高）

**`docs/lumos-toolchain-knowledge/` 是本專案「為什麼這樣設計、邊界在哪、哪些不能改、驗證過沒」的唯一來源；程式碼只告訴你現在長怎樣。** 它主要的讀者是下一個 session 的 AI（偶爾是人），所以寫的時候以「沒有脈絡的人讀得懂」為準。 行為事實（測試、實際執行、生產觀測）和圖譜衝突時，不自動判圖譜對——查清哪邊錯，立一篇事故筆記。

### 第一個工具呼叫是 `lumos`，不是 grep / Read / Explore / 查 DB

| 你心裡想的是… | 先敲這個 |
|---|---|
| 「這個模組 / 欄位 / 流程為什麼這樣？」 | `lumos search <詞>` → `lumos context <節點>` |
| **中文查詢：概念之間加空白** | `lumos search "作廢 收回 點數"`，不是 `作廢訂單點數怎麼收回`——整串當片語比對，黏成一串幾乎必定 0 筆（Landmark 實測 8 句 3 句 0 筆） |
| 「動這段之前有什麼不能碰的？」 | `lumos contracts <節點>` |
| 「我要改 X，會波及什麼？」 | `lumos impact --file <檔>` 或 `--diff <範圍>` |
| 「哪些是金流 / 未收案 / 連到某節點的？」 | `lumos query --tag 家族/值 [--active] [--linked <節點>]` |
| 「我刪掉 / 改名了一個東西，筆記還在講它嗎？」 | `lumos search <舊名> --code` |
| 「當初為什麼這樣決定？翻案了嗎？」 | `lumos decisions <節點> [--superseded]` |
| 「這批改動要不要過審才能推？」 | `lumos pitfalls --diff <merge-base>..HEAD` |
| 「我改了某個流程 / 環境，哪些驗證該重驗？」 | `lumos stale --candidate --match <關鍵字>` |
| 「我 push 了，CI 怎樣？」 | `lumos ci-wait` / `lumos ci-status`（不要 `gh run list`：結果要進治理帳） |
| 「做完了，要留紀錄 / 改狀態 / 記決策」 | `lumos new verification … --plan … --systems …` / `lumos set` / `lumos decision-add` |

查得到才算先行（Landmark 2026-08-11 實測出來的三條）：① 0 筆不是沒記——看「逐詞覆蓋」裡標 ★ 的那個詞是 0，換同義詞再查，換三次還不到再問人，**不要轉頭去 grep**；② 大節點先 `lumos context <節點> --brief`（合約行照樣在頭部），要全文再 `lumos show`；③ 單篇筆記內部可能新舊打架，doctor 驗不出——摘要裡有日期的 KEY 行比正文段落新，衝突又影響決策就去 code 裁，再回頭修圖譜。

★第四條（2026-08-22 Enzo 裁，成本理由：判斷錯本來就要重查一次，這兩分鐘是提前付）★：**要說「沒有／缺／不存在／沒人做過」之前，如果那句話會決定要不要動手做東西——先派一個乾淨 agent 用「原始問題」去對一次，不要把你的結論丟給它**（丟結論它會順著你講，就失去意義）。同日實測：一天內六次判斷失準，**全部是「只信一個來源、沒去對第二個」**——搜錯詞、自己腳本有 bug、讀錯欄位名、用錯工具、看了張過期的表；其中四次是另一個 session 拿它自己的數字打臉才發現。**只有這個場合要派，其他查詢照常**（實測「帶否定斷言」的回覆一天 31 次太多，加上「會決定動不動手」這一刀才降到個位數）。

兩個最常見的破口：① 把任務歸成「只是查個資料」就跳過；② 使用者說「直接改、不用解釋」就跳過。**不解釋可以，不查不行**——進場那一下是一行指令、幾秒鐘。

Edit / Write 之前 hook 會自動塞一份「必看合約 / 事故 + 相關筆記」給你——但它只推你碰到的檔，看到它不等於查過圖譜，合約邊界仍要自己 `lumos contracts` / `context`。

**接手圖譜還是空的專案 → 先走節點還原 SOP**（`lumos-project-notes` 的 `commands/09-節點還原.md`：七步把脈絡還原成節點；需要才產、有就照慣例用）。
**不確定該敲哪個指令 → 讀索引**：`lumos-project-notes` skill 的 `commands/INDEX.md`（4k，按你正在做的事分九類，只開需要的子檔）。

### 鐵則

1. **同一次工作內寫回**：改了會影響行為 / 決策 / 驗證的 code，當次就把脈絡寫回圖譜（pre-commit 擋「改 code 沒動圖譜」）。設計、spec、計劃一律寫成 `Projects/<主題>_計劃` 筆記。
2. **開頭欄位用指令改**（`lumos set` / `append` / `decision-add`），別手改；多個連結一行一項；不確定是不是合約就不要標。重建筆記（regen）與決策四欄的寫法在 skill。
3. **寫完一篇 `lumos lint <節點>`，收工 `lumos doctor`**；push 前 pre-push 會再擋一次。改完程式先跑跟改動相關的測試子集，全套留給推送前的閘——全套要好幾分鐘，跑在對話裡會超時、也讓人等；子集怎麼跑看專案自己的說明。
4. **承認風險要附回頭看的條件**：寫「沒機械守衛 / 只提醒不擋 / 單次量測」這種話，旁邊必須有什麼時候重驗；寫不出來就是該處理不該承認。回頭條件要接電：帶日期的寫成獨立一行 `REVISIT:YYYY-MM-DD 一句要做什麼`（緊鄰原句；doctor 到期會唸）；綁事件的明寫事件入口在哪——純散文的回頭條件＝沒人會回頭（2026-08-31 全圖盤點 52 件實證）。

### 給人看的回報用白話
先一句人話或比喻，再往下講；術語和 file:line 能不用就不用，非用不可就當場一句解釋。設計動筆前先問世界（最小解在哪一層、世界解過沒、裁定＝借用既有設計為預設 / 真沒輪子才自建 / 採用新依賴在零依賴家規下幾乎不選），一行 `PRIOR-ART:` 記進計劃筆記。能寫成規則的走測試先行；探索性的先做最小實驗——講不出一道會對症狀翻紅的指令之前，不准開始建理論（見 `[[Systems/診斷迴圈先行]]`）。

### 遇到這些情境就調用對應 skill

| 你正在做的事 | 調用 |
|---|---|
| 理解既有系統、排查、對外支援、查 DB、寫筆記、巡檢、綁合約測試（含 ★INVARIANT★ / ★IRREVERSIBLE★ / ★CHECKPOINT★ 與 [test:] [audit:] [kill:] [rollback:] [guard:] 的寫法、`lumos spec-trace`、`lumos signoff`） | **`lumos-project-notes`** |
| 跨專案共用的業務規則（升格核心、`core_refs`、偏離） | **`lumos-core-knowledge`** |
| 設計 spec 寫完、要進實作前的審查迴圈 | **`lumos-design-loop`** |
| 分支要推之前，`pitfalls` 出 `tier: high` 的代碼審 | **`lumos-code-loop`** |

> lumos 在 `scripts/lumos`（python3 零依賴）；`lumos-*` skill 唯一來源是 `lumos-toolchain` repo，每台機器裝一次：`git clone <lumos-toolchain> ~/harness/lumos-toolchain && ~/harness/lumos-toolchain/install.sh`。專案技術棧 skill 見文末〈架構參考 Skills〉。
<!-- LUMOS:GRAPH-DISCIPLINE:END -->

## 本 repo 的測試子集怎麼跑(紀律區塊鐵則三說的「看專案自己的說明」就是這裡)

改完程式先跑跟改動相關的子集,全套(約 8 分鐘、3700+ 案例)留給推送前的閘:

```
python3 scripts/test_lumos.py -k <關鍵字>
```

關鍵字比對測試函式名(例:`-k stop_block`、`-k codex`);對照組 Codex 曾因在對話裡跑全套而超時([[Projects/Codex行為精修_計劃]] 基線)。
