---
type: project
status: doing
created: 2026-07-15
updated: 2026-07-15
summary: |-
  FLAG:DECISION
  KEY:解決 decision_refs 的雞生蛋——工作流沒東西產生它,故 E3 與主網 Systems 牙口全睡著(真圖 259 節點/39 有決策/0 reindex/0 decision_refs)。目標=讓系統自我養成 decision_refs,讓 [[關係層主網_實作計畫]] 賺回工
  KEY:實測揭露「補哪條」大部分機器判不了——驗證→決策的連結無結構替身(308 方向邊只 9 條巧合指到決策節點,低召回);故自動判斷=T1 帳本地面真相(機械)+T3 AI 語意填補(讀內容),純機械只是零頭
  KEY:信心階梯 前置P reindex決策節點 → T1 confirm回寫(地面真相,機械) → T3 AI自動填背包(2026-07-15拍板放手:AI自動填+by:ai+人抽查翻案,同主網auto-confirm不對稱安全)
  KEY:核心安全風險=AI誤指決策 → 不對稱信任:ai-ref 對 E3 firing 生效(加法/advisory/一刪),但對 E2 suppression 不生效(誤ref抑制真落後邊=靜默漏傳播=頭號腐爛;suppression 只認 by:human/cascade-confirmed)
  DEP:[[關係層主網_實作計畫]]｜[[Systems/lumos-cli-write]]｜[[Systems/lumos-cli-read]]
  DECISION:進實作前過 lumos-design-loop(碰寫入路徑+AI派工+靜默抑制風險);本節點 spec 完成即交 loop
tags:
  - type/project
  - status/doing
plan_refs:
  - "[[關係層主網_實作計畫]]"
---
# decision_refs自動養成_實作計畫

## 問題（緣起）

主網（[[關係層主網_實作計畫]]）實測揭露：它的真實牙口卡在 `decision_refs` 採用，而**工作流裡沒有任何環節產生 decision_refs**——雞生蛋死鎖。E3（意圖鏈斷義）與主網對 Systems 節點的直接點名都因此永久睡著。

**真圖數據（LandmarkMember 259 節點，2026-07-15 實測）**：39 節點有決策、**0 reindex 過**、**0 decision_refs**。方向邊 308 條，只 **9 條**指向「有決策的節點」。

**關鍵誠實發現**：「哪些節點缺 decision_refs」**大部分機器偵測不到**——因為缺的那個「實作了哪條決策」是語意連結、無結構替身（一篇驗證實作 `POS-API#d3`、卻只有 `plan_refs→某計劃`，跟 POS-API 之間沒有邊）。機械只看得到 9 條巧合對齊的（低召回）。故「自動判斷需要補」＝ **T1 地面真相（機械）＋ T3 AI 語意填補（讀內容）**，純機械只是零頭。

## 信心階梯（三層 + 前置）

- **前置 P：`decision-reindex` 決策節點** — decision_refs 需 `<節點rel>#dN`、目標決策先要有 id。機械、一次性、每個決策節點跑一次（39 個，現 0 個）。M1 已交付 reindex 指令，此處是套用。
- **T1 帳本回寫（地面真相，機械）**：`rel-cascade confirm` 成功 → 把 `from_decision_id` append 到被 confirm 鄰居的 `decision_refs`，provenance 沿 `--by`（ai/human）。**`prune` 不回寫**（判無關＝不記依賴）。走 `atomic_write_verify`。往前自我養成。
- **T3 AI 語意填補（背包，AI-auto-liberal，2026-07-15 拍板）**：**Claude 編排的「suggest 流程」**（非單一 lumos 命令——lumos 不派 AI，r1 折入）：`backlog` 列該跑節點 → `candidates` 列候選決策 → **Claude 讀內容判實作哪條** → `add-ai` 寫 `decision_refs_ai`（標 by:ai）→ 人 `decision-refs list --by ai` 抽查、`prune` 剪錯／`promote` 蓋章升級。**覆蓋範圍＝「V 有 typed 邊直達的決策節點」的結構可達子集**（r2 誠實降級：candidates 是 1-hop 邊解析、surface 不出「無結構邊的語意連結」——那批留人工/future，非 T3 能碰）。詳見 §T3 詳細規格。
- **T2 結構缺口（零頭）**：那 9 條「邊指到決策節點卻無 ref」折進 T3 的候選選取（決定對哪些驗證派 AI），**不做獨立 doctor 檢查**（低召回、不值得一道常設檢查）。

## 釘死的合約

- **不對稱信任（核心安全）**：AI 誤指決策（V 實作 d3、AI 填 d2）的緩解——`by:ai` 的 ref **對 E3 firing 生效**（加法、advisory warn、錯了人一刪、低 harm），但**對 E2 suppression 不生效**。因為誤 ref 拿去抑制 E2 ＝把真落後邊靜默藏掉 ＝本守衛要防的頭號腐爛（危險方向）。**E2 帳本抑制只認 by:human 或 cascade-confirmed 的 ref**；ai-ref 升級成可抑制需人抽查蓋章。這是把主網「auto-confirm 放寬 / auto-prune 保守」的不對稱，套到 ref 的「firing 放寬 / suppression 保守」。
- **provenance 格式（定案 ③，2026-07-15）**：ai 填的進獨立欄位 **`decision_refs_ai`**、human 確認/cascade-confirmed 的進 **`decision_refs`**。**這個雙欄結構本身就是不對稱信任的機械實現**：E3 firing 讀「兩欄聯集」（放寬）、E2 suppression 只讀 `decision_refs`（保守，ai 欄結構上碰不到抑制）。人抽查蓋章＝把某條從 `decision_refs_ai` 搬進 `decision_refs`（升級成可抑制）。比平行 by 欄（易漂移）與富格式行內 `by:ai`（改動既有解析）都乾淨。E2/E3 讀側各自明確吃哪欄，無隱式合併歧義。
- **回寫的節點範圍**：confirm 可 confirm 任何鄰居（含 Systems）；decision_refs 寫到被 confirm 的節點上（與 E2 首判精化讀任何鄰居 decision_refs 一致，非只 Verification）。
- **reindex 前置**：add-ai/回寫前目標決策必須有 id；無 id 的候選 candidates 直接跳該條（同節點其他有 id 決策照列），不自動 reindex（避免隱式改別的節點）。
- **audit surface**：`lumos decision-refs list <節點> [--by ai|human]` 分欄列 ref（顯式 `list` 子命令）；剪錯走 `decision-refs prune`（`--reject` 記否決記憶）。

## 天花板
- **T3 是 AI GIGO**：AI 判實作哪條決策，判錯 = 填錯 ref。緩解靠不對稱信任（firing 可容錯、suppression 不容錯）+ by:ai 可抽查，非靠準度。
- **T3 覆蓋是結構可達子集（r2 誠實降級）**：candidates/backlog 只做 1-hop typed 邊解析——只碰得到「V 直接連到的節點」的決策。**無結構邊的語意連結（V 實作某決策、卻跟它沒有邊）T3 機械上 surface 不出來**，那批留人工/未來 content-based。機器只保證「翻案掃過的（T1）」+「AI 讀過結構可達候選的（T3）」長出 ref。
- decision_refs 對就對、錯了 advisory 級提醒，不污染業務邏輯——這是敢放手 auto-fill 的前提。

## 落地順序
> **進度（2026-07-15）**：P ✅ + T1 ✅（[[Verification/2026-07-15_decision_refs養成_P前置_T1回寫]]）+ code-loop 硬化 ✅（異質 panel 5 修，[[Verification/2026-07-15_decision_refs養成_codeloop硬化]]，1130 tests 綠）→ **T3 待 design-loop**。

1. **前置 P**：套 `decision-reindex` 到決策節點（機械，可先在 lumos-toolchain 自身跑、再 LandmarkMember）。
2. **T1 confirm 回寫**（機械、地面真相、現成可建）——主網從「需要 ref」翻成「一邊動一邊長 ref」。
3. **T3 AI suggest**（含不對稱信任、provenance、audit）——覆蓋背包；design-loop 重點審這塊。

## T3 詳細規格（design-loop v3；r1+r2 四席+Codex 折入）

**分工（lumos 家規「Claude 編排、lumos 出原語」）**：lumos 出**機械原語**，語意判斷是 **Claude 編排步驟**，lumos 不派 AI、不讀語意。**`suggest` 不是 lumos 命令**——它是 Claude 編排流程 `backlog→candidates→讀判→add-ai` 的**合稱**；CLI 是下列 **六個真原語**（Codex r2 更正：五→六）。目標一律 `<節點>`（decision_refs 適用任何鄰居含 Systems，與 T1 一致）。

**覆蓋範圍誠實邊界（r2 B#1 降級）**：candidates/backlog 是 **1-hop typed 邊解析**——只碰得到「節點直接連到的節點」的決策。**無結構邊的語意連結 T3 摸不到**（那批留人工/future）。T3 覆蓋＝結構可達子集，非「背包大宗」。

**lumos 機械原語（六個；Codex r2 驗過讀側/解析/writer 足夠，唯 promote/prune 需新雙欄 edit helper）**
1. `decision-refs backlog [--json]`：列「該跑 suggest 流程的節點」＝有三具名邊指向「**帶≥1 有 id 決策的節點**」、且 `decision_refs`+`decision_refs_ai`+`decision_refs_rejected` **三欄皆空**的節點。走 `build_typed_index`。**「帶決策」鎖有 id 決策**（Codex r2：否則 backlog 選了 candidates 卻空轉）。**兩欄→三欄**：加 `decision_refs_rejected`（見否決記憶）——被人剪過的節點不再重入背包。**收窄語意（r2 B#2/C#4）**：backlog＝「從未碰過」的節點；補一條就退出（部分覆蓋、非窮盡——收窄版接受，多候選漏補靠人手動再 candidates）。
2. `decision-refs candidates <節點> [--json]`：列候選決策——三具名邊 fwd 解析到的節點的**所有決策含已翻案的**（E3 要抓的）；只列有 id 決策，無 id 跳該條（仍列其他）。`--json` 附 **`skipped_no_id` 計數**（Codex r2/C#5：區分「真沒候選」vs「候選都缺 id 待 reindex」）。輸出＝節點 `summary`+body 前 N 字（機械摘要）+ 每候選 `<rel>#dN`+content。空候選→空輸出 rc=0。
3. `decision-refs add-ai <節點> <ref>`：寫 `decision_refs_ai`。**自帶存在性驗證**（ref 格式、目標節點存在、決策 id 真存在 → 否則 rc=2）；**拒 rejected**（該 ref 在 `decision_refs_rejected` → rc=2，否決記憶）。**冪等（r2 C#3）**：`_append_decision_ref` exact-dedup，重複 add 同 ref no-op。不做 candidate-membership 機械檢查（靠協議約定 + 存在性強制）。
4. `decision-refs list <節點> [--by ai|human]`：audit 分欄列 ref（顯式 `list` 子命令，避裸節點名撞子命令）。
5. `decision-refs prune <節點> <ref> [--by ai|human] [--reject]`：移除 ref。`--by` 指定移該欄、不帶 `--by` **兩欄都移**（消假清除）。**`--reject`（否決記憶，r2 B#4）**：把該 ref 記進 `decision_refs_rejected`——防下一輪 backlog 重列+AI 原樣加回的振盪；`decision-refs list` 顯示 rejected 供翻案（人可 prune rejected 解除）。移正欄＝解除 E2 抑制（顯式）。冪等：移不存在 no-op rc=0。
6. `decision-refs promote <節點> <ref>`（**抽查蓋章**）：ref 從 `_ai` 搬到 `decision_refs`（升級可抑制 E2）。**新雙欄 edit helper（Codex#2/B#1，promote+prune 共用）**：讀一份 fm → remove/add 各欄 → 一次 `atomic_write_verify`，**count-based `expected_check`「正欄恰一份、`_ai` 無」**（Codex r2：`_append_decision_ref` 自驗只查「至少一份」，promote 要另寫計數檢查）。**promote 前重驗存在性**：目標 **dangling → rc=2 拒**（非 warn；防失效 ref 蓋章洗白繞過不對稱信任，r2 A#1）。**冪等**：`_ai` 無但正欄已有 → no-op rc=0；兩欄都無 → rc=2；**兩欄都有（異常態，r2 C#2）→ dedup 後正欄一份、清 `_ai`、rc=0**（fail-safe 收斂）。
   - **註（r2 A#2）**：promote 只驗**存在性非權威性**——指向「已翻案決策」的 ref 允許 promote（那正是 E3 要抓的；且 E2 精化對「指到那條翻案決策」的 ref **不抑制**，故不構成洗白）。id 穩定性靠 M1 保證（`decision-reindex` 只補缺、既有 id 永不重用/位移）——promote 存在性檢查建立其上。

**Claude 編排協議（＝suggest 流程）**：① `backlog` 列節點 → ② 逐節點 `candidates` → ③ Claude 讀摘要+候選 content 判「實作哪條」（放寬；一個都不像→跳過不 add）→ ④ `add-ai`。

**釘死的合約**
- **不對稱信任（核心，T1 已建、五席行號驗過）**：ai-ref 對 E3 firing 生效、**結構上抑制不了 E2**；唯一升級＝人 `promote`（重驗存在性+dangling rc=2 拒+原子搬移）。
- **否決記憶（r2 B#4）**：`prune --reject` 記 `decision_refs_rejected`，backlog/add-ai 尊重——人剪的有持久效力、不被 AI 原樣加回振盪。
- **backlog/candidates 同集合**：三具名邊 + 帶 id 決策，兩原語同口徑（消 Codex r2「backlog 選了 candidates 空轉」）。
- **AI GIGO 天花板**：填哪條靠 Claude；誤 ai-ref 只誤觸發 E3 advisory（人 prune），不對稱信任兜住。

**測試策略（逐條對齊合約）**：backlog 三欄皆空+邊到帶 id 決策節點+補一條就退出+rejected 不再入列、candidates 含已翻案+無 id 跳該條+skipped_no_id 計數+空輸出、add-ai 自驗存在性+拒 rejected+重複冪等、prune 兩欄都移 vs --by 單欄+--reject 記憶+冪等、promote 原子雙欄+**dangling rc=2 拒**+冪等+兩欄都有 dedup 收斂、list 分欄+顯示 rejected；**單元層釘不對稱**（只 `_ai` 有值→E2 不抑制）+**反向**（prune 正欄→E2 停止抑制，r2 C#6）；E2E＝背包跑 suggest→ai-ref 落 `_ai`→E3 對翻案觸發/E2 不受影響→promote 後可抑制→prune --reject 後不復發。

## T3 審計修正紀錄

**r1（2026-07-15，panel：3 sonnet 異鏡頭 + Codex 否決席讀 repo）**：canary a✓（candidates 只列 valid vs 測試矛盾）b✓（promote 兩步 vs atomic）c✗（--force，C 席漏抓但挖出更深真 blocker）。Codex 驗證**核心成立**（candidates 用 build_typed_index+parse_decisions 可建、E2/E3 不對稱信任接線行號全對）。約 12 條真 findings 全折 v2：
- **suggest 非 lumos 命令**（A/C/Codex）：改為 Claude 編排「suggest 流程」合稱；CLI 只有五真原語；信心階梯/reindex 前置行同步。
- **批次選取補 `backlog` 原語**（C#F2/A#3）：typed 邊＝三具名邊、與 candidates 同集合（消口徑落差）。
- **add-ai 自驗存在性**（Codex#1/A#2/B#2）：`_append_decision_ref` 不驗目標存在，add-ai 自己驗；措辭撤「機械上只能從 candidates 選」→「存在性強制＋協議約定」。
- **promote 雙欄原子原語 + 重驗 dangling**（Codex#2/B#1/B#4）：單次 read-modify-write（remove _ai+add 正欄同份 fm，expected_check 斷言正欄一份/ _ai 無）；promote 前重驗存在性（防失效 ref 蓋章洗白繞過不對稱信任）；冪等。
- **原語目標 `<驗證>`→`<節點>`**（A#5，與 T1「含 Systems」一致）、**prune 兩欄語意**（A#6/B#5：不帶 --by 兩欄都移）、**candidates 無 id 跳該條非整體 rc=2**（Codex）、**audit 改顯式 `list` 子命令**（A#8/C#F6）、**候選摘要機械化**（Codex）、**測試補漏兩合約**（C#F3）。

**r2（2026-07-15，panel v2）**：canary a✓b✓c✗→實為 3/3（a promote-warn/b backlog-單欄/c prune-單欄 都被抓）。Codex 驗 v2 底層零件足夠（六原語 argparse 無衝突、讀側/writer 夠），唯 promote/prune 需**新雙欄 edit helper**、promote 需 **count-based expected_check**（`_append_decision_ref` 自驗只查「至少一份」）。存活真 findings 折 v3：
- **T3 覆蓋誠實降級（B#1 blocker→人裁「收窄」）**：candidates/backlog 是 1-hop 邊解析、只碰結構可達子集；「覆蓋背包大宗」宣稱撤，改「結構可達子集」+ 天花板明記無結構邊摸不到。
- **否決記憶（B#4 major）**：加 `decision_refs_rejected` 欄 + `prune --reject`；backlog/add-ai 尊重——防人剪錯被下一輪 AI 原樣加回振盪。
- **promote dangling rc=2 拒非 warn**（A#1，canary a 同向——真 spec 本就 rc=2，v2 已對；v3 再強調）、**backlog 鎖有 id 決策**（Codex：消「選了卻空轉」）、**candidates skipped_no_id 計數**（C#5）、**兩欄都有異常態 dedup 收斂**（C#2）、**add-ai 冪等明文**（C#3）、**存在性≠權威性註**（A#2：翻案決策可 promote、E2 精化不抑制、非洗白）、**reindex id 穩定性交叉引用 M1**（A#3）、**反向測試 prune 正欄→E2 停抑制**（C#6）。

## 進實作前（紀律）
本 spec 完成 → 交 **lumos-design-loop**（碰寫入路徑 + AI 派工 + E2 靜默抑制風險，建議 `--need 3`）到 `loop status --gate --panel` 收斂才實作。落地 Verification 以 `plan_refs` 回指本節點。
