---
type: project
status: doing
created: 2026-07-10
updated: 2026-07-10
tags:
  - type/project
  - status/doing
decisions:
  - content: 壞法人宣告(kill 配方進 decisions)+config 宣告 run_cmd,不做自動變異生成
    context: 零依賴跨語言(C#/Kotlin/E2E/python)工具不內建語言知識;自動生成變異有等價變異不可判定問題(實務 4-39% 誤報)
    why_chosen: 人宣告的壞法保證語意有變(繞開等價變異,pytest-mutagen/ISO 26262 先例);run_cmd 沿 .lumos/lint.json 既有信任模型(專案自己宣告的指令);universalmutator ICSE 2018 實證文字層+外部指令 rc 跨語言可行
    decided: 2026-07-10
    valid: true
  - content: 四態判定(killed/survived/timeout/error)+baseline 前置,error 不得記 killed
    context: 紅燈≠殺傷:本來就紅的測試會假殺、編譯錯的紅是最常見假殺來源
    why_chosen: cargo-mutants baseline 流程+timeout=baseline×5下限20s 整套照搬;PIT/cosmic-ray 的獨立 timeout 類別;survived 才 rc1(稻草人)、環境問題 rc2 分開
    decided: 2026-07-10
    valid: true
related:
  - "[[Projects/社群演算法補強_調研]]"
  - "[[Systems/check-t-sentinel]]"
---
# guard殺傷力驗證_計劃

## 目標

補 ★INVARIANT★→`[test:]` 合約鏈的最後一哩：Check T 只驗「綁的測試存在」、`[audit:]` 靠 agent 讀判「夠不夠格」——都沒有**真的打一拳**。新增 `lumos guard kill`：對綁定的測試，在隔離環境故意弄壞被守護的行為，測試必須翻紅；全綠＝綁定是稻草人（假證據），機械可證。

PRIOR-ART: ① 最小解層級：既有 guard 家族加子命令 + config 加欄位，無新物種。② 世界解過（2026-07-10 專項調查，來源見文末）：pytest-mutagen（人宣告壞法、逐 mutant 期望翻紅——概念完全對口但綁死 python/pytest）、ISO 26262 fault injection（安全領域制度化的「宣告故障+期望防護翻紅」）、StrykerJS command runner / cosmic-ray test-command / universalmutator（「config 宣告任意測試指令、rc 判紅綠、工具不內建語言知識」的跨語言介面，ICSE 2018 實證）、cargo-mutants（baseline 前置 + timeout=baseline×5 下限 20s）、PIT/Stryker（四態判定 killed/survived/timeout/error 與增量失效）。③ 裁定 = **borrow-design**：「宣告式 kill 配方 × command-runner × 圖譜綁定」組合世界無既成品，各構件皆有先例背書；零依賴 stdlib 原生實作。

## 設計裁定（四條）

1. **壞法由人宣告，不自動生成**：kill 配方記在該 ★INVARIANT★ 對應 decision 的 `kill` 欄位（block scalar 內 JSON array；`parse_decisions` 通用解析零改動），KEY 行尾標 `[kill:decisions]`（同 `[rollback:decisions]` 樣板）。每條配方 = `{"file","old","new","note"}`（純文字替換、跨語言；old 必須唯一命中）。**配方從業務行為推導、不從實作反轉**（DO-178C 教訓——照抄實作行反轉會把配方也變套套邏輯）；一條 INVARIANT 可綁多條配方（N=1 證據力弱，mutation 社群共識）。宣告走 `lumos guard kill-add`（寫後自驗），同 scaffold 的防帶風向鐵則：壞法描述「業務上什麼壞了」須經人確認。
2. **跑測試靠 config 宣告指令（沿 lint.json 先例）**：`.lumos/config.json` 的 platform 加選填 `run_cmd`（含 `{method}` 佔位，如 `dotnet test --filter FullyQualifiedName~{method}`）。lumos 已有執行專案宣告指令的先例（`.lumos/lint.json` 的 lint pipeline，`scripts/lumos:4613`）——信任模型相同：專案自己宣告的指令。無 `run_cmd` 的平台 → kill 明確報「未宣告不可用」（rc 2），不猜。
3. **隔離 + baseline 前置（cargo-mutants 整套照搬）**：`git worktree add` 臨時樹（用畢移除；detached、不污染工作區）→ 先跑**未變異** baseline，綁定測試必須綠（本來就紅 → `abort`，防假殺）→ 套配方（old 找不到/多重命中 → `stale`，即配方漂移需重寫，同 PIT「hash 變了作廢歷史」）→ 重跑同一指令 → 判四態。
4. **四態判定 + 留痕**：`killed`（紅，配方被接住）✓ / `survived`（綠，**稻草人證據，rc 1**）/ `timeout`（baseline×5、下限 20s，獨立類別不算 killed 也不算 survived）/ `error`（套用後編譯錯等 harness 失敗——**不得記 killed**，編譯錯的紅是最常見假殺）。結果 append governance/kill-log.jsonl（本功能新建的留痕檔，尚不存在故不用 inline-code 標）（{ts,node,invariant摘要,recipe_note,verdict,platform}），`--json` 出 manifest。

## CLI 面

- `lumos guard kill-add <node> "<KEY子字串>" --file F --old X --new Y [--note "業務上壞了什麼"]` — 寫配方進對應 decision 的 `kill` 欄位 + KEY 行尾補 `[kill:decisions]`（merge 不重複）；寫後自驗（重 parse 讀得回）。
- `lumos guard kill <node> ["<KEY子字串>"] [--platform P] [--json] [--keep-worktree]` — 跑該節點（或指定合約）的全部配方。rc：全 killed=0；任一 survived=1；stale/abort/error/timeout 存在但無 survived=2（配方或環境要修，非稻草人證據）；config 缺 run_cmd=2。
- doctor 不加硬檢（v1）：kill 是主動體檢不是 gate——`guard list` 順帶顯示各 INVARIANT 有無 `[kill:]`（資訊不擋）。

## 邊界與誠實天花板

- **E2E（maestro/playwright）**：世界查無 E2E mutation 實踐（成本）；本設計 N=1 配方 × 只跑綁定 flow 是唯一可行形態，但 flaky 紅≠殺傷——E2E 平台的 verdict 註記 `flaky-risk`，建議跑 2 次 survived 才定罪（v1 只註記不重跑）。
- **配方等價風險**：人宣告的壞法可能改到 dead code → 永遠 survived；工具誠實報 survived 由人判——fail-safe 方向（誤報稻草人 → 人查發現配方壞，比漏報安全）。
- **宣告的壞法可能自己是稻草人**（挑個 smoke test 都抓得到的壞法）：機械驗不了，靠 `[audit:]` 獨立審計順帶審配方合理性（審計 prompt 補一問）。
- kill 證「這個測試接得住這個壞法」，不證「接得住所有壞法」——是存在證明不是覆蓋證明。

## 測試計畫（scripts/test_lumos.py，合成 repo + 假 run_cmd）

- 合成 python 平台（run_cmd=`python3 -m pytest ...` 或更簡單：`python3 <test.py>` rc 判定）：killed happy path、survived（測試不斷言）、stale（old 漂移/多重命中）、abort（baseline 紅）、timeout（sleep 配方）、error（套壞語法）、無 run_cmd rc2。
- kill-add 寫後自驗：decision kill 欄位讀得回、KEY 行 `[kill:decisions]` merge 不重複、多配方 append。
- worktree 清理：跑完無殘留（`git worktree list` 乾淨）。

## 驗收（真機）

- 本 repo：對一條現有機制造一個示範 INVARIANT+配方跑通四態。
- **Landmark（C# xunit）**：挑一條已綁 `[test:]` 的真實 ★INVARIANT★，宣告 run_cmd（dotnet test --filter）與一條業務壞法配方，真跑 kill——這是跨 repo、跨語言、真 DB 守衛的端到端驗收（使用者的「每條 invariant 綁端點驗證」規範在此閉環）。

## 相關模組

- [[Projects/社群演算法補強_調研]]
- [[Systems/check-t-sentinel]]
- [[Systems/check-r-guard]]
- [[Systems/test-profile-multiplatform]]

## PRIOR-ART 來源

- pytest-mutagen：github.com/timpaquatte/pytest-mutagen（宣告式 mutant、期望翻紅）
- StrykerJS command runner：stryker-mutator.io/docs/stryker-js/configuration
- cosmic-ray：cosmic-ray.readthedocs.io（test-command+timeout→incompetent 三態）
- cargo-mutants：mutants.rs/baseline.html（baseline 前置、timeout 公式）
- universalmutator：github.com/agroce/universalmutator（ICSE 2018，文字層跨語言+外部指令 rc）
- PIT：pitest.org/faq（KILLED/SURVIVED/TIMED_OUT/NO_COVERAGE、targetTests、withHistory）
- ISO 26262 fault injection、DO-178C requirements-based coverage（需求推導壞法、人審把關）
