---
type: project
status: doing
created: 2026-07-29
updated: 2026-07-29
tags:
  - type/project
  - status/doing
related:
  - "[[Projects/Codex外審吸收_計劃]]"
  - "[[Issues/canary-record未落盤事件]]"
  - "[[Systems/guard-kill]]"
  - "[[Systems/canary-audit]]"
summary: |-
  FLAG:TECHNICAL
  KEY:P1-1 oracle 品質包(外審對話收斂的最高投資序)——讓每盞綠燈答得出兩問:證據真的落盤了嗎(S1 record 寫後讀回自驗)/紅燈真的是那條規則咬住的嗎(S3 guard-kill 歸因);加 S2 canary 第二判者抽查(植入者≠判定者的抽樣分權)
  KEY:出身——2026-07-29 Codex 外審對話三輪:它抓到 record 回報成功未落盤真事故([[Issues/canary-record未落盤事件]])+「guard-kill 只知紅不知為何紅」+「caught/missed 無第二判者」;與我方圖譜舊結論「驗證層天花板=oracle 品質」合流
  DEP:[[Systems/canary-audit]]
  DEP:[[Systems/guard-kill]]
---
# oracle 品質包_計劃（P1-1）

`PRIOR-ART:` ①寫後讀回自驗＝lumos T1 寫入既有家規（tmp→rename→自驗），S1 是把漏網的 append 路徑補進同一紀律，非新機制；②kill 歸因＝mutation testing 生態的 killing-test attribution（PItest 報告殺死變異的具體測試、Stryker 分 Survived/NoCoverage）——borrow-design：解析 runner 輸出歸因到綁定測試名，不引依賴；③第二判者抽查＝評分者間信度（inter-rater）抽樣慣例，取抽樣不取全量（成本）。裁定＝borrow-design。

## 範圍刀（明確不做）

- **不做**帳本上雲／不可竄改儲存（合規面，超出本包；見外審 P1-0/組織級路線）。
- **不做** canary caught/missed 判定自動化（判定仍是編排者，S2 只加抽樣分權）。
- **不改** `loop status` 收斂邏輯（second 行由既有 loop 欄過濾天然隔離，只加回歸釘不加代碼）——S2 純 telemetry，**不進 gate**。
- **不做**全量第二判——抽樣（成本與價值的取捨，明文）。
- guard-kill 歸因**不 parse 各框架結構化報告**（JUnit XML 等＝依賴/耦合面大）——文字輸出啟發式＋明標弱證據級別。

## 條款

### [S1] `canary record` 落盤自驗（修 [[Issues/canary-record未落盤事件]] 的機械面）

- 成功輸出改為：`✓ canary <kind> 留痕: CANARY-<id> [(auditor=<a>)] → <log 檔絕對路徑>`（auditor 段沿現行慣例**有給才印**；新增＝行尾落盤絕對路徑，消「成功了但不知寫哪」盲區）。
- **append 後讀回驗證**：重新開檔、確認含該 `CANARY-<id>` 的行存在且 `json.loads` 可解、其 `id` 欄等於該 ID；任一不成立 → stderr `canary record: 落盤自驗失敗(<絕對路徑>)` ＋ **rc 2**，且**不印 ✓ 行**（成功宣稱與證據綁死）。
- vault 解析失敗（cwd 無 vault 且未給 --vault）→ 維持現行 rc2 路徑，但 [S1] 測試釘住「絕不靜默成功」。
- `canary second`（[S2] 新指令）與既有 record 共用同一寫入＋自驗 helper（單源，不雙寫）。

### [S2] canary 第二判定者（抽樣分權，telemetry-only）

- 新子指令：`lumos canary second --id CANARY-<id> --verdict agree|overturn --auditor <模型/人> [--note "<一句>"]`
  - 追加一行 `{kind:"second", ref:"CANARY-<id>", verdict, auditor, note, ts}` 到同一 canary log（走 [S1] 同一自驗 helper）。
  - `--id` 在 log 中不存在 → rc 2；`verdict` 僅收 `agree`/`overturn`（overturn 語意＝第二判者不同意原 caught/missed 判定；細節寫 note）。
  - `loop status` 忽略 second 行——**機制＝天然成立**（second 行不帶 `loop` 欄，現行 `loop==loop_id` 過濾天生濾掉，pre-flight 已實查現碼證實）；**不要為此新寫判斷（死代碼）**，[S3′] 第 5 項是回歸釘（防未來 filter 鬆動），非新邏輯。
- **抽樣紀律（skill 層，非機械閘）**：design-loop 與 code-loop 判讀段各加一條——每累計 5 個 caught 輪抽 1 輪，把「審計員原始報告全文＋植入描述（型別/位置/性質）」交乾淨第二判者判 caught/missed；抽中輪的審計員報告存 `governance/canary-samples/CANARY-<id>.md`（**寫入者＝編排者人工存檔，本條即其定義，[S3′] 不驗**；僅抽中輪保留——全量成本不值）。分歧（overturn）→ 記 `canary second --verdict overturn` ＋該 loop 下一輪 framing 復核。
- 誠實天花板：抽樣頻率 1/5 是先驗值；第二判者仍是 LLM（同門盲點靠換家族緩解，skill 建議第二判者優先跨家族）。

### [S3] guard-kill 歸因升級（「準殺」）

**現況更正（pre-flight 實查）**：現行 verdict 已六值（killed/timed_out/survived/drifted/abort/error）、`.kill-log` 已有 verdict 欄、且 **timed_out 現行計入 killed**（PIT 心智模型註解在案）。本條款＝**取值語意升級＋一項刻意行為變更**，非新增欄位：`killed` 拆歸因/未歸因兩級；`timed_out` **改不計 killed**（刻意變更——採外審「timeout 降弱證據」；理由：掛掉可能是環境非變異）。**rc 影響明文**：無 survived 時 rc 維持 0（弱證據不阻放行），摘要必印 `弱證據 N 筆`；有 survived 仍 rc1。其餘取值（drifted/abort/error）不動。

`lumos guard kill` 跑完 recipe 後，對 runner stdout＋stderr 做文字歸因：

| verdict | 判準 | 語意 |
|---|---|---|
| `killed`（歸因） | rc≠0 **且** 綁定測試方法名出現於輸出、且其行起往後 5 行內有失敗標記（`FAIL`/`FAILED`/`✗`/`AssertionError`/`Exception`，大小寫不敏感） | 強證據：那條測試真的咬住了 |
| `killed-unattributed` | rc≠0 但綁定測試名未命中上述判準 | 弱證據：可能只是 compile error/環境 crash——印警告「建議 recipe 加 filter 鎖定該測試」；**與 killed 分開計數**（摘要行分列） |
| `timed_out-weak` | runner 逾時 | 弱證據、**不計 killed**（刻意變更，見上） |
| `survived` | rc 0 | 不變（稻草人證據） |

- 歸因輸出：命中行前後各 1 行摘錄（截 200 字）印於 verdict 之後——「紅燈是誰咬的」可讀。
- 綁定測試名比對：以 `[test:]` 的方法名（含多平台 `P:方法` 的方法段）做**大小寫敏感子字串**比對（測試方法名是識別字）。
- 既有 kill 測試：**timed_out 相關斷言依刻意變更同步調整**（其餘不倒退）；`.kill-log` verdict 欄既存——只擴值域，舊值讀取不變。

### [S3′] 測試（TDD，`t_canary_record_persist`／`t_canary_second`／`t_guard_kill_attribution`）

1. record 正常 → 輸出含絕對路徑；該行讀回可解、id 相符；`--auditor` 未給時無 auditor 段（沿現行）；
2. record 落盤失敗（log 路徑被同名**目錄**佔用）→ rc2、stderr 含「落盤自驗失敗」、**無 ✓ 行**；
3. record 於 vault 外 cwd（明給 --vault）→ 寫進正確 log（cwd 漂移回歸釘）；cwd 無 vault 且未給 --vault → rc2 非靜默成功；
4. second 正常 agree → log 追加 kind=second 行（含 note 落盤讀回）；`--id` 不存在 → rc2；verdict 亂值 → rc2；缺 `--auditor` → rc2（分權紀錄無名則失義）；
5. second 行存在時 `loop status --gate` 輸出與 rc 與無 second 時**逐字節相同**（telemetry 不滲入 gate）;
6. kill 歸因四型（fake run_cmd 各產：具名失敗／匿名 crash／逾時／全綠）→ killed／killed-unattributed（含警告）／timed_out-weak／survived；**timeout-only 情境 rc0＋摘要印弱證據筆數**；摘要 killed 與 unattributed **分開計數**可見；
7. killed 歸因輸出含命中行摘錄；**超長命中行截 200 字**（構造長行驗截斷）；
8. 舊 .kill-log 行（無 verdict 欄）讀取不炸、視為 killed；
9. 綁定名比對大小寫敏感（`Foo_test` 不命中 `foo_test`）；**多平台綁定（`[test:P:方法]`）取方法段歸因**命中案。

### [S4] 文件/skill touchpoints

- `skills/lumos-code-loop/SKILL.md` §4「修進真碼」補一句：**修 bug 標配「還原翻紅釘」**（把 bug 還原、綁定測試必翻紅的回歸測試；testmap 實戰教訓——存在且綠的測試可空轉）。
- design-loop 與 code-loop 判讀段各加 [S2] 抽樣條（一句＋樣本保留路徑）。
- [S1] 落地後：`Issues/canary-record未落盤事件` status → resolved，回填根因調查結果（重現或「無法重現，readback 防線已閉」如實記）。

## 實務隱患

- 歸因啟發式對「測試名出現在非失敗上下文」（如 runner 列印執行清單）可能誤歸因 → 判準要求名字＋失敗標記**鄰近共現**（5 行窗），仍非零誤判，明標弱證據帳分開統計。
- readback 在 NFS/延遲寫檔系統上理論上可 false-fail → append 後同 fd flush 再讀，本機 POSIX 語意下穩定；異常檔案系統列明文限制。
- 第二判者樣本檔（canary-samples/）含審計員報告全文 → 可能夾敏感碼段；保留於 repo 內 gitignore 或入版控？**裁定：入版控**（它就是稽核證據，遮掩即失義）——但列入 pitfalls 提醒別貼密鑰。

## 審計修正紀錄

- **pre-flight**（2026-07-29，機械 checklist＋現碼實查，不計 loop findings）：①[S3] 三處現況誤述更正——現行 verdict 已六值/.kill-log 已有 verdict 欄/timed_out 現行計 killed（「timeout→skipped 既有語意」是我方誤寫）→ 改述為「取值語意升級＋timeout 降級屬刻意變更」並明文 rc 影響；②[S2] loop status 忽略 second＝天然成立（second 行無 loop 欄,現有過濾天生濾掉）→ 明文防死代碼,測試改回歸釘定位;③範圍刀與 [S2] 措辭衝突消解;④auditor 段沿現行有給才印;⑤[S3′] 補 6 項測試縫(note 落盤/缺 auditor rc2/多平台方法段/分開計數/200 字截斷/timeout-only rc 邊界);⑥canary-samples 寫入者=編排者人工,明文不驗。
