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
- **T3 AI 語意填補（背包，AI-auto-liberal，2026-07-15 拍板）**：**Claude 編排的「suggest 流程」**（非單一 lumos 命令——lumos 不派 AI，r1 折入）：`backlog` 列該跑節點 → `candidates` 列候選決策 → **Claude 讀內容判實作哪條** → `add-ai` 寫 `decision_refs_ai`（標 by:ai）→ 人 `decision-refs list --by ai` 抽查、`prune` 剪錯／`promote` 蓋章升級。覆蓋背包大宗。詳見 §T3 詳細規格。
- **T2 結構缺口（零頭）**：那 9 條「邊指到決策節點卻無 ref」折進 T3 的候選選取（決定對哪些驗證派 AI），**不做獨立 doctor 檢查**（低召回、不值得一道常設檢查）。

## 釘死的合約

- **不對稱信任（核心安全）**：AI 誤指決策（V 實作 d3、AI 填 d2）的緩解——`by:ai` 的 ref **對 E3 firing 生效**（加法、advisory warn、錯了人一刪、低 harm），但**對 E2 suppression 不生效**。因為誤 ref 拿去抑制 E2 ＝把真落後邊靜默藏掉 ＝本守衛要防的頭號腐爛（危險方向）。**E2 帳本抑制只認 by:human 或 cascade-confirmed 的 ref**；ai-ref 升級成可抑制需人抽查蓋章。這是把主網「auto-confirm 放寬 / auto-prune 保守」的不對稱，套到 ref 的「firing 放寬 / suppression 保守」。
- **provenance 格式（定案 ③，2026-07-15）**：ai 填的進獨立欄位 **`decision_refs_ai`**、human 確認/cascade-confirmed 的進 **`decision_refs`**。**這個雙欄結構本身就是不對稱信任的機械實現**：E3 firing 讀「兩欄聯集」（放寬）、E2 suppression 只讀 `decision_refs`（保守，ai 欄結構上碰不到抑制）。人抽查蓋章＝把某條從 `decision_refs_ai` 搬進 `decision_refs`（升級成可抑制）。比平行 by 欄（易漂移）與富格式行內 `by:ai`（改動既有解析）都乾淨。E2/E3 讀側各自明確吃哪欄，無隱式合併歧義。
- **回寫的節點範圍**：confirm 可 confirm 任何鄰居（含 Systems）；decision_refs 寫到被 confirm 的節點上（與 E2 首判精化讀任何鄰居 decision_refs 一致，非只 Verification）。
- **reindex 前置**：add-ai/回寫前目標決策必須有 id；無 id 的候選 candidates 直接跳該條（同節點其他有 id 決策照列），不自動 reindex（避免隱式改別的節點）。
- **audit surface**：`lumos decision-refs [--by ai] <節點>` 列 ref + 來源；剪錯的走既有寫入原語（或補 `decision-refs prune`）。

## 天花板
- **T3 是 AI GIGO**：AI 判實作哪條決策，判錯 = 填錯 ref。緩解靠不對稱信任（firing 可容錯、suppression 不容錯）+ by:ai 可抽查，非靠準度。
- **不追求高召回的機械偵測**：機器只保證「翻案掃過的（T1）」+「AI 讀過的（T3）」長出 ref；沒人碰的驗證背包靠增量清。
- decision_refs 對就對、錯了 advisory 級提醒，不污染業務邏輯——這是敢放手 auto-fill 的前提。

## 落地順序
> **進度（2026-07-15）**：P ✅ + T1 ✅（[[Verification/2026-07-15_decision_refs養成_P前置_T1回寫]]）+ code-loop 硬化 ✅（異質 panel 5 修，[[Verification/2026-07-15_decision_refs養成_codeloop硬化]]，1130 tests 綠）→ **T3 待 design-loop**。

1. **前置 P**：套 `decision-reindex` 到決策節點（機械，可先在 lumos-toolchain 自身跑、再 LandmarkMember）。
2. **T1 confirm 回寫**（機械、地面真相、現成可建）——主網從「需要 ref」翻成「一邊動一邊長 ref」。
3. **T3 AI suggest**（含不對稱信任、provenance、audit）——覆蓋背包；design-loop 重點審這塊。

## T3 詳細規格（design-loop v2；r1 四席+Codex 折入）

**分工（同 lumos 家規「Claude 編排、lumos 出原語」）**：lumos 出**機械原語**，語意判斷（V 實作哪條決策）是 **Claude 編排步驟**（如判斷閘），lumos 不派 AI、不讀語意。**`suggest` 不是 lumos 命令**（r1 A/C/Codex）——它是 Claude 編排流程 `backlog→candidates→讀判→add-ai` 的**合稱**；下文一律用「suggest 流程」，CLI 只有下列五個真原語。**目標一律 `<節點>` 非 `<驗證>`**（r1 A#5：decision_refs 適用任何鄰居含 Systems，與 T1 一致；suggest 流程對背包節點跑、不限 Verification）。

**lumos 機械原語（Codex 驗過底層零件足夠）**
- `decision-refs backlog [--json]`（**新，r1 C#F2/A#3 補**）：機械列「suggest 流程該跑哪些節點」——有 `verified_by`/`plan_refs`/`related` typed 邊指向「帶決策節點」、但 `decision_refs`+`decision_refs_ai` **皆空**的節點。走 `build_typed_index`（Codex 確認可建、已處理 ghost/歧義）。**這是「typed 邊」的唯一定義＝三具名邊**，與 candidates 來源同集合（消 r1 A#3 口徑落差）。
- `decision-refs candidates <節點> [--json]`：機械列候選決策——來源＝該節點 `plan_refs`/`verified_by`/`related`（typed index fwd）解析到的節點的**所有決策，含已翻案的**（V 可能實作一條後被推翻的意圖，正是 E3 要抓的）；**只列有 id 的決策**，無 id 的**跳過該條**（仍列同節點其他有 id 決策，非整體 rc=2，r1 Codex）。輸出＝節點 `summary`+body 前 N 字（**機械摘要、非語意**，r1 Codex）+ 每候選 `<rel>#dN` + 決策 content。空候選集 → 空輸出 rc=0（Claude 端 no-op）。
- `decision-refs add-ai <節點> <ref>`：寫 ref 到 `decision_refs_ai`。**自帶存在性驗證（r1 Codex#1/A#2/B#2：`_append_decision_ref` 不驗這個，add-ai 要自己驗）**：ref 格式 `<rel>#dN`、目標節點存在、決策 id 真存在 → 否則 rc=2 拒。**不做 candidate-membership 檢查**（那靠協議約定，非機械強制——措辭改「存在性強制 + 協議約定只填 candidates」，不再宣稱「機械上只能從 candidates 選」）。
- `decision-refs <節點> [--by ai|human]`：audit 列 ref + 來源欄位（裸節點名易與子命令撞名 → **改要求顯式子命令 `decision-refs list <節點>`**，r1 A#8/C#F6）。
- `decision-refs prune <節點> <ref> [--by ai|human]`：移除 ref。**兩欄處置釘死（r1 A#6/B#5/Codex）**：`--by` 指定則只移該欄；不帶 `--by` **兩欄都移**（清乾淨、消「兩欄殘留只清一欄」的假清除）。移正欄＝解除 E2 抑制，屬顯式動作（有 `--by human` 即人明示）。冪等：移不存在 → no-op rc=0。
- `decision-refs promote <節點> <ref>`（**抽查蓋章**）：ref 從 `decision_refs_ai` 搬到 `decision_refs`（升級可抑制 E2）。**新雙欄原語（r1 Codex#2/B#1：不可先 prune 再 add，要單次）**：讀一份 fm → 同時 remove `_ai` + add 正欄 → 一次 `atomic_write_verify`，`expected_check` 斷言「正欄恰一份、`_ai` 無」，失敗全不動。**promote 前重跑存在性驗證（r1 B#4：曾合法後失效的 ref 不得經蓋章洗白進正欄繞過不對稱信任）**：目標已 dangling → rc=2 拒、提示走 prune。**冪等（r1 A#7/B#7）**：`_ai` 已無但正欄已有該 ref → no-op rc=0；兩欄都無 → rc=2。

**Claude 編排協議（＝「suggest 流程」）**：① `backlog` 列該跑的節點 → ② 對每節點 `candidates` → ③ Claude 讀節點摘要+候選 content、判「實作哪條」（放寬：似是就填；一個都不像 → 跳過該節點不 add）→ ④ `add-ai`。

**釘死的合約（design-loop 重點）**
- **不對稱信任（核心，T1 已建、四席+Codex 行號驗過）**：ai-ref（`decision_refs_ai`）對 E3 firing 生效、**結構上抑制不了 E2**；唯一升級路徑＝人 `promote`（重驗存在性、原子搬移）。
- **backlog/candidates 同集合**：typed 邊＝`verified_by`/`plan_refs`/`related` 三具名邊，兩原語同定義（不再有「選了卻吐空 / 該選沒選」落差）。
- **add-ai 存在性自驗**、**promote 重驗+原子雙欄**、**prune 兩欄語意**、**candidates 無 id 跳該條**：如上各原語條款。
- **AI GIGO 天花板**：填哪條靠 Claude、判錯＝ai-ref 誤填；不對稱信任兜住（誤 ai-ref 只誤觸發 E3 advisory、人 prune）。suggest 流程不追求準度、追求覆蓋 + 可抽查。

**測試策略（逐條對齊合約，補 r1 C#F3 漏的）**：backlog 只列兩欄皆空+有 typed 邊到決策節點的、candidates 含已翻案決策+**無 id 決策跳該條仍列其他**+**空候選集空輸出**、add-ai **自驗存在性（拒不存在節點/id）**、prune 冪等+**兩欄都移 vs --by 單欄**、promote **原子雙欄搬移+重驗 dangling 拒蓋章+冪等**、list --by 分欄；**單元層釘不對稱**（只有 `_ai` 有值 → E2 suppression 不觸發，r1 C#F7 建議）；E2E＝背包節點跑 suggest 流程 → ai-ref 落 `_ai` → E3 對翻案觸發、E2 不受影響、promote 後才可抑制。

## T3 審計修正紀錄

**r1（2026-07-15，panel：3 sonnet 異鏡頭 + Codex 否決席讀 repo）**：canary a✓（candidates 只列 valid vs 測試矛盾）b✓（promote 兩步 vs atomic）c✗（--force，C 席漏抓但挖出更深真 blocker）。Codex 驗證**核心成立**（candidates 用 build_typed_index+parse_decisions 可建、E2/E3 不對稱信任接線行號全對）。約 12 條真 findings 全折 v2：
- **suggest 非 lumos 命令**（A/C/Codex）：改為 Claude 編排「suggest 流程」合稱；CLI 只有五真原語；信心階梯/reindex 前置行同步。
- **批次選取補 `backlog` 原語**（C#F2/A#3）：typed 邊＝三具名邊、與 candidates 同集合（消口徑落差）。
- **add-ai 自驗存在性**（Codex#1/A#2/B#2）：`_append_decision_ref` 不驗目標存在，add-ai 自己驗；措辭撤「機械上只能從 candidates 選」→「存在性強制＋協議約定」。
- **promote 雙欄原子原語 + 重驗 dangling**（Codex#2/B#1/B#4）：單次 read-modify-write（remove _ai+add 正欄同份 fm，expected_check 斷言正欄一份/ _ai 無）；promote 前重驗存在性（防失效 ref 蓋章洗白繞過不對稱信任）；冪等。
- **原語目標 `<驗證>`→`<節點>`**（A#5，與 T1「含 Systems」一致）、**prune 兩欄語意**（A#6/B#5：不帶 --by 兩欄都移）、**candidates 無 id 跳該條非整體 rc=2**（Codex）、**audit 改顯式 `list` 子命令**（A#8/C#F6）、**候選摘要機械化**（Codex）、**測試補漏兩合約**（C#F3）。

## 進實作前（紀律）
本 spec 完成 → 交 **lumos-design-loop**（碰寫入路徑 + AI 派工 + E2 靜默抑制風險，建議 `--need 3`）到 `loop status --gate --panel` 收斂才實作。落地 Verification 以 `plan_refs` 回指本節點。
