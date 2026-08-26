---
type: project
status: done
created: 2026-08-04
updated: 2026-08-04
self_audit: sonnet/2026-08-04
related:
  - "[[Projects/design-loop重設計]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Systems/canary-audit]]"
  - "[[Systems/lumos-cli-write]]"
tags:
  - type/project
  - status/done
summary: |-
  FLAG:TECHNICAL
  KEY:本檔=[[Projects/design-loop重設計]](r1 已收斂、人裁放行)的 TDD 實作計畫。六包嚴格順序:★①相容雙讀→②quote-check+凍結快照→③--disposal gate(獨立路徑)→④skill 重寫(與③同批交付)→⑤收緊(留痕轉強制)→⑥離線校準★——順序鐵則=schema/產生器/skill/gate 消費端不同步的中間版本,不得存在任何強制檢查(r1 Codex 折入)
  KEY:★新 CLI 面★——record 六個選配欄(--report/--findings-set/--folded-set/--accepted-set/--accept-reason id=理由/--snapshot);新命令 `lumos quote-check <報告> --spec <快照>`(命名避開既有 anchor 子命令);gate 新旗標 `--disposal` 與 --panel/--light/--settle/--need 互斥
  KEY:★正規化規格(quote-check 核心,單一實作函式 _quote_norm)★——NFC→剝 markdown 強調記號(*/**/`)→全形半形空白摺疊為單一空格→子字串比對;引句抽取=報告內「引句：「…」」樣式逐條
  KEY:★每包完成判準★——測試先紅後綠+還原翻紅釘+現場成立前置(對照 [[Systems/測試假綠形態]] 八型);全套 test_lumos.py 綠;doctor 0 issues
  DEP:scripts/lumos cmd_canary/cmd_loop_status/cmd_loop_next｜scripts/test_lumos.py｜skills/lumos-design-loop/SKILL.md+templates.md｜governance/review-reports/｜governance/eval/
---
# design-loop 重設計・實作計畫

> **spec**：[[Projects/design-loop重設計]]（r1 panel 收斂、使用者 2026-08-04 裁「同意」）。
> **Goal**：把「閘只留可重算的＋觀測強制留痕＋預設化」落成 code 與 skill，全程不打壞現行 loop。
> **Tech**：scripts/lumos（python3 stdlib、零依賴）；測試進 scripts/test_lumos.py。

## Global Constraints（每包隱含）

- **相容鐵則**：任何中間 commit 上，現行 design-loop／code-loop 的既有呼叫（不帶新旗標）行為**一字不變**——每包附一條「舊呼叫不變」回歸斷言。
- **舊 panel 閘一行不動**（code-loop 隔離的唯一機制＝新旗標獨立路徑，spec d2/B5）。
- 寫入一律 tmp→自驗→atomic；JSONL 單行；新欄不給不寫鍵（同 `--findings` 慣例）。
- 測試對照假綠八型；修 bug 標配還原翻紅釘＋現場成立前置。

## 任務拆解

### T1（包①）record 相容雙讀：六個選配欄

**Modify**: `scripts/lumos` `cmd_canary`＋argparse；**Test**: `t_canary_record_disposal_fields_optional`

新選配參數（全部不給＝行為與今日完全相同）：

| 參數 | 存欄 | 寫側驗證（給了才驗，違反 rc2） |
|---|---|---|
| `--report <path>` | `report_path`,`report_sha256`（自算） | 檔案存在且非空 |
| `--snapshot <path>` | `snapshot_path`,`snapshot_sha256` | 檔案存在且非空 |
| `--findings-set "a,b,c"` | `findings_set`(list) | 非空、無重複 id |
| `--folded-set "a,b"` | `folded_set` | ⊆ findings_set |
| `--accepted-set "c"` | `accepted_set` | ⊆ findings_set；**與 folded 互斥；聯集＝findings_set**；`severity==blocker ⇒ 必空`（d1） |
| `--accept-reason "id=理由"`（可重複） | `accept_reasons`(dict) | 鍵集合==accepted_set；理由去空白後非空 |

步驟：紅（unrecognized arguments）→ 實作 → 綠 → **翻紅釘**：把「聯集＝findings_set」檢查註掉 → 「缺 c 未處置必 rc2」翻紅 → 還原 → commit。
斷言含：舊呼叫（零新參）rc0 且記錄無新鍵；`folded∪accepted≠findings` rc2；blocker＋accepted 非空 rc2；理由缺 rc2。

### T2（包②）`lumos quote-check`：錨定檢查＋正規化

**Modify**: `scripts/lumos`（新 `cmd_quote_check`＋`_quote_norm`）；**Test**: `t_quote_check_normalization_and_verdict`

介面：`lumos quote-check <報告.md> --spec <凍結快照.md> [--json]`
- 抽取：報告中每行 `引句：「…」`（含全形引號變體）。
- `_quote_norm(s)`：`unicodedata.normalize("NFC")` → 剝 `*` `` ` `` → 空白（含全形）摺疊單空格 → lower 不做（保留大小寫）。
- 判定：每條引句 norm 後是否為快照 norm 後的子字串 → 逐條 `ok/miss`；rc0=全 ok、rc1=有 miss、rc2=IO/參數。
- ★**單一實作**：抽取與比對只有 `_quote_norm` 一份，測試斷言兩處呼叫同函式（防兩份實作漂移——2026-08-02 教訓）。★

斷言含（現場成立前置各一）：粗體包裹的原文引句判 ok（r1 實戰重現案例）；斷行重排判 ok；**編造引句判 miss**；空報告 rc2。
翻紅釘：把剝記號步驟註掉 → 粗體案例翻紅。

### T3（包②）凍結快照留痕慣例

**Modify**: `governance/review-reports/` 慣例＋`cmd_canary`（`--snapshot` 已在 T1）；**Test**: `t_disposal_snapshot_provenance`

- 慣例：派工時快照存 `governance/review-reports/<loop-id>/<round>-snapshot.md`、席報告存 `<round>-<席>.md`。
- 斷言：record 帶 `--report`＋`--snapshot` 時，兩檔 sha256 落帳可重算；★quote-check 對**快照**跑而非現檔（防折入後引句自我成真——用「先折入再 quote-check 現檔會假 ok、對快照跑必 miss」的場景釘死）★。

### T4（包③）`loop status --disposal`：新閘獨立路徑

**Modify**: `scripts/lumos` `cmd_loop_status`（新分支→新函式 `_loop_status_disposal`）；**Test**: `t_loop_status_disposal_gate`

- 互斥：與 `--panel`/`--light`/`--settle`/`--need` 併用 rc2（比照 `--settle` 慣例）。
- 判定輪＝最後一輪；合取四條，全部讀側可重算：
  1. **G3 hash 鏈**（reuse 既有 `_hash_chain_check` 慣例）
  2. **處置集合**：判定輪記錄含 `findings_set` 且互斥／聯集／blocker 線成立（重算，不信寫側）
  3. **留痕讀側重驗**：`report_path`／`snapshot_path` 檔案存在且 sha256 與帳面一致（r1 Codex：record 完刪檔要擋）
  4. **quote-check**：對帳面 snapshot 重跑報告引句，全 ok
- canary caught/missed 欄**不進合取**（觀測；miss 不作廢——d4）。
- ★舊路徑迴歸斷言：同一帳不帶 `--disposal` 走舊 panel 閘，輸出與改動前逐字節相同。★
- 翻紅釘：刪掉報告檔 → 條 3 翻紅（現場成立前置：先驗 record 時檔案在）。

### T5（包④）skill 重寫（與 T4 同批交付，不得先後分離）

**Modify**: `skills/lumos-design-loop/SKILL.md`＋`templates.md`；`skills/lumos-code-loop/SKILL.md` 只加一段差異註記。

- SKILL 重寫面：定位段（閘便宜審不淺＋前提層職責）；流程改「pre-flight→隨機決定植入（d4 觀測）→派工（錨定紀律逐字進 prompt）→quote-check→辯方→處置帳 record→`--disposal` gate」；抑噪紀律保留但附 d4 說明；難度探針改餵全文（r1 前案已實證）；cap＝2 輪（一輪處置全清即走，第二輪只給 delta）。
- `loop next`：`record_cmd` 模板帶新欄位佔位（與 T1 同名）；**同 commit** 內模板與 schema 一致（斷言：模板填佔位後真跑 rc0——沿 `t_loop_next_legacy_emits_a_command_that_actually_runs` 的「真跑 oracle」）。
- code-loop SKILL 加註記：「design-loop 已改 disposal 判準；本 skill 沿用舊 panel 閘，**不得**因同步衝動改本檔」。
- 此包無新機械測試（散文），驗收＝T4 的模板真跑斷言＋fold-check 對兩份 skill 的 SSOT 掃描。

### T6（包⑤）收緊：`--disposal` loop 的留痕轉強制

**Modify**: `cmd_canary`；**Test**: `t_disposal_loop_requires_provenance`

- 定錨規則：loop 首筆帶 `findings_set` 的記錄定錨為 disposal loop（同 M2 cluster 定錨前例）；定錨後該 loop 後續 record **必帶** `--report`＋`--snapshot`，缺＝rc2。
- 舊 loop／未定錨 loop 完全不受影響（迴歸斷言）。
- 翻紅釘：把強制檢查註掉 → 「定錨後缺 report 必 rc2」翻紅。

### T7（包⑥）離線校準腳本

**Create**: `governance/eval/canary_calibration.py(2026-08-26 已退場,詳建了沒人跑批次裁定)`（stdlib）；**Test**: 冒煙進 test_lumos（`t_calibration_smoke`，`_need_src` 守門）

- 輸入：凍結語料目錄＋植入清單（JSON：檔、位置、型別、token）＋各配置的審查報告目錄。
- 輸出：配置 × 型別的 caught 矩陣＋JSONL 累積帳（`governance/eval/calibration-log.jsonl`）。
- 範圍刀：**不派 agent**（派工歸編排者），只做判定與記帳；判定沿 quote-check 的 `_quote_norm`（單一實作）。

### T8 收尾

- `lumos impact --diff --sync-check` 落成核對；Systems 節點同步（`loop-convergence-recording`／`canary-audit`／`design-loop` 的 FLOW/KEY 行）；建 `Verification/2026-08-XX_design-loop重設計落地`（`plan_refs` 回指本檔＋spec）；`lumos pitfalls --diff` 拿 tier → 依判準走終審。

## 實務隱患

- **T4 的「舊輸出逐字節相同」斷言可能過脆**（提示文字換行即紅）——若太脆改為「rc＋判定行集合相同」，在測試 docstring 記載取捨。
- **quote-check 的引句樣式**依賴報告遵守派工格式；席報告不照格式＝抽不到引句＝rc1——這是**紀律對機械的依賴點**，寫進 skill 派工模板並在 gate 訊息裡指路。
- **隨機植入的「隨機」**由編排者擲（skill 層），機械層只記 `planted: true/false`——誠實記載：隨機性本身不可稽核。

## 進度

- ✅ **T1（2026-08-04）**：六選配欄＋集合核對落地；`t_canary_record_disposal_fields_optional`
  10 斷言；相容鐵則驗過（零新參舊呼叫 rc0 無新鍵）；全套 2247 綠。
  ★過程教訓：第一版翻紅釘假紅——「缺 b 未處置」案例同時缺理由，拔掉聯集檢查後理由檢查
  代打 rc2；修法＝把理由給齊，讓目標檢查成為**唯一能翻紅的路**（斷言重疊型，T8 併入假綠清單）。★
- ✅ **T2（2026-08-04）**：`lumos quote-check`＋`_quote_norm`（vault-free）落地；6 斷言
  （粗體／反引號／跨行正規化、編造引句 miss、★零引句 rc2＝驗不了≠通過★、快照不存在 rc2、
  單一實作機械代理 `def _quote_norm` 恰一處）；翻紅釘實測（拔正規化→粗體案例精準翻紅）。
  附帶：新命令觸發漂移守衛（六份文件「53 個頂層命令」→54 同步）——列舉宣稱靠守衛不靠記憶的再一次實證。
- ✅ **T3（2026-08-04）**：反循環合約釘死；`t_disposal_snapshot_provenance` 3 斷言——
  前置先證明「對折入後現檔跑會假 ok」真的會發生，再釘「對凍結快照跑必 miss」；snapshot_sha256 可重算。
- ✅ **T4（2026-08-04）**：`loop status --disposal` 獨立閘落地（`_loop_status_disposal`＋
  `_quote_rows` 核心抽出共用）；`t_loop_status_disposal_gate` 10 斷言：互斥 rc2×3、缺 spec rc2、
  ★四條合取全過 rc0 且 missed 席在場照樣收斂（d4 canary=觀測非閘）★、★舊 panel 閘一行不動★、
  留痕讀側重驗（record 完竄改→FAIL）、quote-check 讀側、★blocker 在別席＋本席 accepted→輪級重算 FAIL
  （堵 r1 Codex 的寫側盲區）★；翻紅釘實測（拔 sha 重驗→竄改照樣放行,精準翻紅）。
- ✅ **T5（2026-08-04）**：`loop next` 吐 `disposal_cmd`＋`disposal_gate` 模板（record_cmd
  原樣保留給 code-loop）＋真跑 oracle 測試；skill 三檔手術改——design-loop SKILL 定位修訂＋
  處置閘流程節、templates 加★錨定紀律★與抑噪例外口、code-loop SKILL 加分流註記（刻意設計非漂移）。
- ✅ **T6（2026-08-04）**：定錨收緊——loop 首筆帶 findings_set 後，後續 record 必帶
  --report/--snapshot（rc2）；未定錨 loop 不受影響；翻紅釘實測。★T6 生效後正確地咬到 T4
  測試場景（missed 席也要留痕＝d4 判定留痕），測試已跟上。★
- ✅ **T7（2026-08-04）**：`governance/eval/canary_calibration.py`——判定 import lumos 的
  `_quote_norm`（單一實作）；caught/mentioned/missed 三態寬判＋誠實聲明「不進任何 gate」；
  累積帳 calibration-log.jsonl；冒煙測試（`_need_src` 守門）。
- ⚠️ **T8（2026-08-04）**：收尾四項全執行，終審★達 cap 未收斂→攤人裁★——
  ①sync-check 核對：slim×3／guard-kill／公開精簡版×2／test-layers／lifecycle 判不相關；
  假綠清單併入「斷言重疊型」（翻紅釘第二盲區，T1 教訓）；②Verification T1-T7 已 pass；
  ③`pitfalls --diff` tier=high → code-loop panel 三輪（W=5＋Codex 雙席＋spec 席）：
  r1＝2 missed，7 條 major 全機械 repro 後修（壞行 fail-open 寫讀兩側／判定輪取錯／巢狀引句截斷／
  引句無下限／只驗 carrier／相對路徑／UnicodeDecodeError）；r2＝1 missed，抓到 r1 修復批自己的
  回歸 3 條（__legacy 合組／全席缺欄跳過／vault.parent≠repo root）；r3＝5/5 caught 輪有效，
  又出 3 major（__ 撞鍵 3 席重疊／不成對引號靜默丟棄／git-less root 邊角）——全部修畢＋測試釘
  （新測試 5 支、全套 2302 綠），但★cap=3 到頂、無乾淨輪，發現未枯竭（capture-recapture 殘餘超門檻）★。
  ④處置：pre-push 會擋 tier=high 無 pass 留痕——放行需人明示豁免（`lumos code-loop pass --note
  "人裁豁免:達 cap,r1-r3 findings 均已修+測試釘,殘留=r3 修復批未經獨立輪"`）或加開 r4。
  ★n_badlines 全域 fail-closed 三席異議留檔：裁 accepted（誤擋方向＋git 可修＋settle 前例），
  配套＝rc2 訊息附壞行行號。★canary 生成觀察：資源類植入對 haiku 探針天生顯眼
  （r1-s2/r2-s1 皆 recraft×2-fail），該兩席 caught 記弱證據。
