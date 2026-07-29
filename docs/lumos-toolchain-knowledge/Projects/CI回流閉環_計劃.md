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
  KEY:解法方向=**push 後同輪等待+修復重試(watch-fix-retry)**,非雲端自動修也非留到下次開場:`lumos ci-wait` 在 push 成功後阻塞等 CI 結論→紅則印失敗步驟+log 尾段→在場 session 當輪修→重推→再等(最多 2 次自動重試,之後攤人);SessionStart 推播降為**後備網**(session 中斷/機器關機才用),不是主路徑
  KEY:★不採雲端 autofix(明文裁定)★——世界主流(Copilot cloud agent 一鍵修/Codex workflow_run autofix/GH Agentic Workflows)是 CI 失敗觸發 agent 在雲端改碼開 PR;與 2026-07-29 剛裁定的「autonomous 非 dry-run 停用」同源風險(無人看顧 agent 握寫入權=confused-deputy),且需把金鑰放進 CI → 本案明文排除,解禁條件同 [[Systems/nested-agent-permission-scope]] d4
  DEP:[[Systems/gov治理帳]]
---
# CI 回流閉環_計劃

`PRIOR-ART:` ① 最小層：`gh run list --json` 已能查狀態、`lumos gov` 已是多帳彙整器、SessionStart hook 已存在——本案是**接線**不是造新機制。② 世界解過：Copilot cloud agent 一鍵修復、Codex `workflow_run` autofix、GH Agentic Workflows self-healing CI——全屬「雲端 agent 自動改碼開 PR」型。③ 裁定＝**borrow-design 但反向取捨**：借「CI 失敗要有下游接手」的問題定義，**拒絕**其雲端無人值守實作（見上方 ★ 裁定），改為本機拉取＋人在場修復。

## 範圍刀（明確不做）

- **不做**雲端自動修復／自動開 PR（見 ★ 裁定；解禁＝子 agent 唯讀隔離落地）。
- **不做** webhook／常駐監聽（要開埠、要密鑰；pull 模式夠用）。
- **不擋** push／commit：CI 狀態不新增本機硬閘（`ci-wait` 的 rc1 是給 skill 判讀用的訊號，不是閘）。
- **不做**無限重試：修復重試上限 2 次，之後攤人＋寫 Issue（防燒錢與掩蓋真 bug）。
- **不做**跨 repo 聚合：只查當前 repo 當前分支。
- **不解析** CI log 全文做根因判讀（v1 只取失敗步驟名＋log 尾段；判讀交在場的人／session）。

## 條款

### [S1] `lumos ci-wait [--timeout 600] [--repo R] [--json]`——push 後同輪等結論（主路徑）

- **時機**：`git push` 成功之後**立刻**在同一輪跑（CI 於 push 完成即觸發，~3 分鐘出結論）。
- 行為：先解析當前 HEAD sha → 輪詢 `gh run list --branch <分支> --json databaseId,headSha,status,conclusion,displayTitle,url`（間隔 15s，`--timeout` 預設 600s）直到**該 sha 的 run** 出現且 `status=completed`。
- **綠**：印一行綠燈訊息、寫帳、rc0。
- **紅**：印 `conclusion`＋**失敗步驟名**＋該步驟 log 尾段 40 行（`gh run view <id> --log-failed`，截 4000 字）＋run URL；寫帳；**rc 1**（讓呼叫端/skill 知道要進修復路徑）。
- 逾時未出結論：印已知狀態＋提示手動查，寫帳（`conclusion=timeout-waiting`），**rc 0**（不把等待逾時當失敗）。
- `gh` 不存在／未登入／非 GitHub remote → stderr 一行說明＋**rc0** fail-open（不因缺工具卡住任何流程）。
- 快取：結果寫 docs 下的 ci-log JSONL 帳檔（本案新建產物，append，欄位 `{ts, run_id, sha, conclusion, title, url, checked_at}`）；同 `run_id` 且 `conclusion` 未變 → 不重複 append（去重鍵＝`(run_id, conclusion)`）。走 [S3] 的自驗 helper（`_jsonl_append_verified`，唯一鍵＝`run_id`＋`conclusion` 合成字串）。
- 輸出：文字模式一行 `CI <conclusion> <sha 前7> <title> → <url>`；`--json` 單行純 JSON。
- rc：**恆 0**（advisory；查詢工具不擋事）。唯一 rc2＝`--repo` 指非目錄。
- `--refresh` 才打網路；不帶則讀快取最後一筆（離線可用、不拖慢 hook）。

### [S2] 修復重試迴圈（skill 紀律，機械原語由 [S1] 出）

`lumos-project-notes` skill 的收尾段與 code-loop 收斂後段各加一條——**push 成功後必跑 `lumos ci-wait`**：

- rc0（綠）→ 收工。
- rc1（紅）→ **當輪修**：讀 [S1] 印出的失敗步驟＋log 尾段 → 定位 → 修 → commit → push → **再跑一次 `ci-wait`**。
- **重試上限 2 次**（＝最多推三次）。仍紅 → **停、攤給人**，並把失敗步驟／log 尾段／已試修法寫成 Issue 節點（`Issues/CI-<sha7>-紅燈`，帶 `pitfall_when`），不無限燒。
- **flaky 判別（誠實，不自動化）**：同一 sha 重跑一次就綠 → 記為疑似 flaky 進 Issue，不當修好（避免「重跑到綠」變成掩蓋真 bug 的慣性）。
- **紅燈不過夜**：修不完就寫 Issue 並在收尾報告明講「main 上有紅燈未解」，不得靜默收工。

### [S2b] 後備網（主路徑失效時才用，都只提醒不擋）

1. **SessionStart hook**：session 中斷／機器關機導致 [S2] 沒跑完時的兜底——讀帳最後一筆，紅且 sha 仍是祖先 → 開場注入一行提醒。綠或無資料靜默。
2. **pre-push**：帳上最後一筆為紅且 sha 仍是祖先 → stderr 一行提醒（不改 rc，不新增擋點）。
3. **`lumos gov` 第 7 源**：CI 事件併入治理時間軸（`gate="ci"`, `hard=False`），使「紅過幾次／紅了多久沒解」可查。

### [S3] 帳與離線查詢

- `lumos ci-status`（唯讀、不打網路）：印帳上最後一筆＋`(檢查於 <ts>)`；超過 24 小時加註可能過期。供 hook 與離線用。
- 帳檔欄位 `{ts, run_id, sha, conclusion, title, url, failed_step}`；去重鍵＝`(run_id, conclusion)`（同 run 狀態變化才 append）。寫入走 `_jsonl_append_verified`（寫後讀回自驗，唯一鍵＝run_id+conclusion）。
- **SessionStart hook 與 `ci-status` 皆不打網路**（避免拖慢開場）；只有 `ci-wait` 會連線。

### [S4] 測試（TDD，`t_ci_status`）

1. `gh` 不存在（PATH 隔離）→ ci-wait rc0＋stderr 說明＋不寫帳；
2. 假 `gh` fixture（第一次回 in_progress、第二次回 success）→ 輪詢後 rc0、寫帳一筆（狀態變化各一筆）；
3. 假 `gh` 回 failure ＋ `--log-failed` 吐固定文字 → **rc1**、輸出含失敗步驟名與 log 尾段（截 4000 字）；
4. 只認**當前 HEAD sha 的 run**：fixture 回別的 sha 的 run → 不當結論、繼續等到逾時；
5. 逾時（`--timeout 1` ＋ 恆 in_progress fixture）→ rc0＋提示，帳記 `timeout-waiting`；
6. `--json` 單行純 JSON（含 conclusion/url/failed_step）；
7. `ci-status` 唯讀不呼叫 `gh`（fixture 設成呼叫即失敗，仍 rc0、讀帳輸出）；帳 >24h 加註過期；
8. gov 第 7 源顯示 CI 事件；
9. SessionStart hook：紅且為祖先 → 注入；綠 → 靜默；紅但 sha 非祖先（已 rebase 掉）→ 靜默。

### [S5] 文件

- README 指令參考加 `ci-wait`／`ci-status` 兩行＋工作流圖加「push → ci-wait → 紅則當輪修」一步；ARCHITECTURE 治理帳段落更新為七帳。
- 本節點記「為什麼不做雲端 autofix」，供未來重議時看得到取捨。

## 實務隱患

- `gh` 未登入時 `gh run list` 會回錯誤而非空結果 → fail-open 需吃 rc≠0 與空輸出兩型。
- 同一 sha 可能有多個 workflow（未來擴充）→ v1 只取最近一次 run，明文限制。
- 分支切換頻繁時快取最後一筆可能屬別的分支 → 記錄帶 sha，推播前驗「是當前分支祖先」才提醒。

## 審計修正紀錄

（loop 折入區）
