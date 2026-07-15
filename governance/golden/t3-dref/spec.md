# t3-dref — 凍結 spec 快照（design-loop 達 cap、人裁凍結、待實作）

> **狀態**：達 3 輪 panel cap 未 clean 收斂 → 人裁「凍 golden、暫停實作」（2026-07-15）。
> 核心（六原語 + 不對稱信任雙欄）穩、Codex + 四席行號驗過；非收斂集中在 **v3 晚加的 `decision_refs_rejected`（否決記憶）+ backlog 判準**這塊。
> 本檔＝凍結當下的 v3 spec + 收斂到的 **v4 方向**（簡化，待日後真需要再實作）。
> 權威計劃節點：`Projects/decision_refs自動養成_實作計畫`（decisions#d1 記凍結裁定）。

---

## 目的（一句話）

派 AI 回頭替舊驗證補「我背書哪條決策」的便條（`decision_refs`）——解主網 `decision_refs` 的雞生蛋：工作流沒東西產生它，故 E2 suppression / E3 firing / 主網對 Systems 直接點名全睡著。

**T1 已交付**（confirm 回寫、地面真相、機械）＝一邊 confirm 一邊長 ref；**T3＝AI 語意填補**，補 T1 碰不到的存量。

---

## 誠實覆蓋邊界（r2 B#1 降級，凍結時已定案）

candidates/backlog 是 **1-hop typed 邊解析**——只碰得到「節點直接連到的節點」的決策。**無結構邊的語意連結（V 實作某決策、卻跟它沒有邊）T3 機械上摸不到**（那批留人工/future content-based）。

**T3 覆蓋＝結構可達子集，非「背包大宗」**（真圖 308 方向邊只 9 條巧合指向有決策節點）。這是凍結的關鍵 ROI 信號：T3 是窄覆蓋小加分，不是它立項時以為的「補大宗」。

---

## v3 spec（凍結當下；六機械原語 + Claude 編排）

**分工（lumos 家規）**：lumos 出**機械原語**，語意判斷是 **Claude 編排步驟**，lumos 不派 AI、不讀語意。`suggest` 不是命令，是 `backlog→candidates→讀判→add-ai` 的合稱。目標一律 `<節點>`（含 Systems，與 T1 一致）。

**六機械原語**
1. `decision-refs backlog [--json]`：列「該跑 suggest 的節點」＝有三具名邊指向「帶≥1 有 id 決策的節點」、且 `decision_refs`+`decision_refs_ai`+`decision_refs_rejected` **三欄皆空**。走 `build_typed_index`。
2. `decision-refs candidates <節點> [--json]`：列候選決策——三具名邊 fwd 解析到的節點的**所有決策含已翻案的**；只列有 id，無 id 跳（仍列其他），`--json` 附 `skipped_no_id`。輸出＝summary+body 前 N 字+每候選 `<rel>#dN`+content。
3. `decision-refs add-ai <節點> <ref>`：寫 `decision_refs_ai`。自帶存在性驗證（格式/目標存在/id 真存在→否則 rc=2）；拒 rejected；冪等 exact-dedup。
4. `decision-refs list <節點> [--by ai|human]`：分欄列 ref（顯式子命令，避裸節點名撞子命令）。
5. `decision-refs prune <節點> <ref> [--by ai|human] [--reject]`：移除。`--by` 移該欄、無 `--by` 兩欄都移。`--reject` 記 `decision_refs_rejected`（否決記憶）。冪等。
6. `decision-refs promote <節點> <ref>`（抽查蓋章）：`_ai`→`decision_refs`（升級可抑制 E2）。新雙欄 edit helper（讀一份 fm→remove/add→一次 atomic_write_verify，count-based expected_check「正欄恰一份、`_ai` 無」）。promote 前重驗存在性，dangling→rc=2 拒。冪等：兩欄都有→dedup 收斂 rc=0。只驗存在性非權威性（翻案決策允許 promote）。

**釘死的合約**
- **不對稱信任（核心，T1 已建、五席行號驗過）**：ai-ref 對 E3 firing 生效、**結構上抑制不了 E2**（雙欄機械實現：E3 讀聯集、E2 只讀 `decision_refs`）；唯一升級＝人 `promote`。
- **否決記憶**：`prune --reject` 記 `decision_refs_rejected`，backlog/add-ai 尊重。
- **backlog/candidates 同集合**：三具名邊 + 帶 id 決策。
- **AI GIGO 天花板**：填哪條靠 Claude；誤 ai-ref 只誤觸發 E3 advisory，不對稱信任兜住。

---

## v4 收斂方向（r3 三席匯聚；簡化，凍結為「待實作」）

r3 三席三輪皆 caught canary、收斂到同一根因：**v3 晚加的 `decision_refs_rejected`（否決記憶）是半成品**——無解除原語（永久鎖死）、不在 candidates/promote 各層強制（繞道洗白）、backlog 判準也錯。三席匯聚的 v4 方向：

1. **backlog 判準改集合差**（B 席深洞）：正確判準＝「**候選集 − 已填 ≠ 空**」，**不是「N 欄皆空」**。三欄皆空只是「從未碰過」，會漏「補了一條但還有候選」的節點。
2. **rejected 過濾移到讀側**（candidates 標/濾 rejected），**不靠 add-ai 晚拒**——否決記憶要在 candidates 就生效，否則 backlog 重列→AI 原樣算回→靠 add-ai 才擋＝振盪窗口還在。
3. **考慮砍掉 `decision_refs_rejected` 回雙欄**：否決記憶是為擋「AI 重加回振盪」，但 design-loop 顯示它引入的洞（無解除/繞道）比它擋的振盪更貴。v4 傾向**砍第三欄**、用「集合差 backlog + candidates 讀側去重」達成同等防振盪，回乾淨雙欄（`decision_refs` / `decision_refs_ai`）。
4. **count-check 精確化**（r3-c）：promote 的 expected_check「`_ai` 無」語意＝「**此 ref 不在 `_ai`**」非「整欄空」；add-ai 補「已在正欄」檢查；T1 回寫也認 rejected（一致性）。

**凍結裁定的元信號**（design-loop 不只抓 bug，也體檢功能值不值得）：連兩輪暗示「別再堆小功能大機械」——T3 是窄覆蓋小加分（結構子集），為它加的保險機械（rejected-memory）反覆引入漏洞。T1 已交付真價值。故凍 v4 方向、暫停實作；日後真需要 T3 時，撿 v4 簡化設計（雙欄 + 集合差 backlog）直接實作。
