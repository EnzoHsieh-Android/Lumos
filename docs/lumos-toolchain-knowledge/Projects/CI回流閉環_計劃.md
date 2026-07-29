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
  - "[[Systems/nested-agent-permission-scope]]"
summary: |-
  FLAG:DECISION
  KEY:問題——CI(GitHub Actions)紅了只存在 GitHub 網頁,本機 lumos/圖譜/治理帳全不知情;下個 session 開場也讀不到 → 自動開發迴圈在「推出去之後」斷掉
  KEY:解法方向=**本機拉取(pull)**非雲端自動修:`lumos ci-status` 查最近一次 run→記 .ci-log.jsonl→gov 第 7 源+SessionStart hook 推播+pre-push 軟提醒;「接手」=下個 session 開場即知紅、拿得到失敗步驟與摘要、由在場的人監督下開修
  KEY:★不採雲端 autofix(明文裁定)★——世界主流(Copilot cloud agent 一鍵修/Codex workflow_run autofix/GH Agentic Workflows)是 CI 失敗觸發 agent 在雲端改碼開 PR;與 2026-07-29 剛裁定的「autonomous 非 dry-run 停用」同源風險(無人看顧 agent 握寫入權=confused-deputy),且需把金鑰放進 CI → 本案明文排除,解禁條件同 [[Systems/nested-agent-permission-scope]] d4
  DEP:[[Systems/gov治理帳]]
---
# CI 回流閉環_計劃

`PRIOR-ART:` ① 最小層：`gh run list --json` 已能查狀態、`lumos gov` 已是多帳彙整器、SessionStart hook 已存在——本案是**接線**不是造新機制。② 世界解過：Copilot cloud agent 一鍵修復、Codex `workflow_run` autofix、GH Agentic Workflows self-healing CI——全屬「雲端 agent 自動改碼開 PR」型。③ 裁定＝**borrow-design 但反向取捨**：借「CI 失敗要有下游接手」的問題定義，**拒絕**其雲端無人值守實作（見上方 ★ 裁定），改為本機拉取＋人在場修復。

## 範圍刀（明確不做）

- **不做**雲端自動修復／自動開 PR（見 ★ 裁定；解禁＝子 agent 唯讀隔離落地）。
- **不做** webhook／常駐監聽（要開埠、要密鑰；pull 模式夠用）。
- **不擋** push／commit：CI 狀態是**軟提醒**，不新增硬閘（避免「CI 暫時紅就工作癱瘓」）。
- **不做**跨 repo 聚合：只查當前 repo 當前分支。
- **不解析** CI log 全文做根因判讀（v1 只取失敗步驟名＋log 尾段；判讀交在場的人／session）。

## 條款

### [S1] `lumos ci-status [--repo R] [--json] [--refresh]`

- 資料源：`gh run list --limit 1 --branch <當前分支> --json databaseId,conclusion,status,displayTitle,headSha,createdAt,url`（`gh` 不存在／未登入／非 GitHub remote → **stderr 一行說明＋rc0**，fail-open，不因缺工具卡住任何流程）。
- 快取：結果寫 docs 下的 ci-log JSONL 帳檔（本案新建產物，append，欄位 `{ts, run_id, sha, conclusion, title, url, checked_at}`）；同 `run_id` 且 `conclusion` 未變 → 不重複 append（去重鍵＝`(run_id, conclusion)`）。走 [S3] 的自驗 helper（`_jsonl_append_verified`，唯一鍵＝`run_id`＋`conclusion` 合成字串）。
- 輸出：文字模式一行 `CI <conclusion> <sha 前7> <title> → <url>`；`--json` 單行純 JSON。
- rc：**恆 0**（advisory；查詢工具不擋事）。唯一 rc2＝`--repo` 指非目錄。
- `--refresh` 才打網路；不帶則讀快取最後一筆（離線可用、不拖慢 hook）。

### [S2] 推播三處（都只提醒、不擋）

1. **SessionStart hook**（`scripts/hooks/claude/`）：讀 `.ci-log.jsonl` 最後一筆，若 `conclusion` ∈ `{failure, cancelled, timed_out}` **且**該 `sha` 是當前分支祖先 → 注入一行：`⚠ 上次 push 的 CI 紅了(<sha7> <title>) → <url>；本輪開工前先處理或明確跳過`。綠或無資料則靜默（零噪音）。
2. **pre-push**：push 前若快取最後一筆為紅且 sha 仍是祖先 → stderr 一行提醒（**不改 rc**，不新增擋點）。
3. **`lumos gov` 第 7 源**：`.ci-log.jsonl` 併入時間軸（`gate="ci"`, `kind=conclusion`, `hard=False`），使「CI 紅過幾次／紅了多久沒修」可查。

### [S3] 誰去刷新（避免「快取永遠是舊的」）

- **pre-push 之後不自動查**（push 當下 CI 還沒跑完，查了也是舊的）。
- **SessionStart hook 不打網路**（會拖慢每次開場）——只讀快取。
- **刷新點＝兩處**：① 每日治理腳本（`governance/daily-governance.sh`）加一行 `lumos ci-status --refresh`；② 人／session 手動跑 `lumos ci-status --refresh`（例如剛 push 完等三分鐘後）。
- **陳舊誠實**：文字輸出附 `(檢查於 <checked_at>)`；快取超過 24 小時 → 加註 `⚠ 資料可能過期,--refresh 更新`。

### [S4] 測試（TDD，`t_ci_status`）

1. `gh` 不存在（PATH 隔離）→ rc0＋stderr 說明＋不寫帳；
2. 假 `gh`（fixture 腳本吐固定 JSON）→ 寫入 `.ci-log.jsonl` 一筆、欄位齊；
3. 同 run 同 conclusion 重跑 → 不重複 append（去重）；同 run 但 conclusion 由 `in_progress`→`failure` → append 新筆；
4. 不帶 `--refresh` → 不呼叫 `gh`（fixture 設成呼叫即失敗仍 rc0 且輸出讀自快取）；
5. `--json` 單行純 JSON；
6. 快取 >24h → 輸出含過期註記；
7. gov 第 7 源顯示 CI 事件；
8. SessionStart hook：紅且為祖先 → 有注入；綠 → 靜默；紅但 sha 非祖先（已被 rebase 掉）→ 靜默。

### [S5] 文件

- README 指令參考加兩行（`ci-status`）；ARCHITECTURE 治理帳段落更新為七帳。
- 本節點記「為什麼不做雲端 autofix」，供未來重議時看得到取捨。

## 實務隱患

- `gh` 未登入時 `gh run list` 會回錯誤而非空結果 → fail-open 需吃 rc≠0 與空輸出兩型。
- 同一 sha 可能有多個 workflow（未來擴充）→ v1 只取最近一次 run，明文限制。
- 分支切換頻繁時快取最後一筆可能屬別的分支 → 記錄帶 sha，推播前驗「是當前分支祖先」才提醒。

## 審計修正紀錄

（loop 折入區）
