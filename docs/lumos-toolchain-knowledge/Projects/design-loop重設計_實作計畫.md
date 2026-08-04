---
type: project
status: doing
created: 2026-08-04
updated: 2026-08-04
related:
  - "[[Projects/design-loop重設計]]"
  - "[[Systems/loop-convergence-recording]]"
  - "[[Systems/canary-audit]]"
  - "[[Systems/lumos-cli-write]]"
tags:
  - type/project
  - status/doing
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

**Create**: `governance/eval/canary_calibration.py`（stdlib）；**Test**: 冒煙進 test_lumos（`t_calibration_smoke`，`_need_src` 守門）

- 輸入：凍結語料目錄＋植入清單（JSON：檔、位置、型別、token）＋各配置的審查報告目錄。
- 輸出：配置 × 型別的 caught 矩陣＋JSONL 累積帳（`governance/eval/calibration-log.jsonl`）。
- 範圍刀：**不派 agent**（派工歸編排者），只做判定與記帳；判定沿 quote-check 的 `_quote_norm`（單一實作）。

### T8 收尾

- `lumos impact --diff --sync-check` 落成核對；Systems 節點同步（`loop-convergence-recording`／`canary-audit`／`design-loop` 的 FLOW/KEY 行）；建 `Verification/2026-08-XX_design-loop重設計落地`（`plan_refs` 回指本檔＋spec）；`lumos pitfalls --diff` 拿 tier → 依判準走終審。

## 實務隱患

- **T4 的「舊輸出逐字節相同」斷言可能過脆**（提示文字換行即紅）——若太脆改為「rc＋判定行集合相同」，在測試 docstring 記載取捨。
- **quote-check 的引句樣式**依賴報告遵守派工格式；席報告不照格式＝抽不到引句＝rc1——這是**紀律對機械的依賴點**，寫進 skill 派工模板並在 gate 訊息裡指路。
- **隨機植入的「隨機」**由編排者擲（skill 層），機械層只記 `planted: true/false`——誠實記載：隨機性本身不可稽核。
