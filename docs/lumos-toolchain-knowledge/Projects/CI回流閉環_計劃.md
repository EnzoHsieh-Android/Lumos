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

`PRIOR-ART:` ① 最小層：`gh run list --json` 已能查狀態、`lumos gov` 已是多帳彙整器、Claude hook 註冊機制（`merge-claude-settings.py` 的 `HOOK_ENTRIES`）已存在——主路徑 [S1][S2] 屬接線；**但 [S2b]-① 的 SessionStart hook 是新建**（實查現有僅註冊 PreToolUse/PostToolUse/Stop 三事件，無 SessionStart），需新增 hook 檔＋新事件登記，pre-flight 已更正原「已存在」的誤述。② 世界解過：Copilot cloud agent 一鍵修復、Codex `workflow_run` autofix、GH Agentic Workflows self-healing CI——全屬「雲端 agent 自動改碼開 PR」型。③ 裁定＝**borrow-design 但反向取捨**：借「CI 失敗要有下游接手」的問題定義，**拒絕**其雲端無人值守實作（見上方 ★ 裁定），改為本機拉取＋人在場修復。

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
- 帳檔：`docs/.ci-log.jsonl`（本案新建；欄位單源定義見 [S3]，此處不重述）。
- 輸出：文字模式一行 `CI <conclusion> <sha 前7> <title> → <url>`；`--json` 單行純 JSON。
- **rc 明定（pre-flight 修矛盾：原文「恆 0」與紅燈 rc1 互斥，會讓 [S2] 主路徑失去觸發訊號）**：綠 rc0／**紅 rc1**（skill 判讀訊號，非閘）／逾時 rc0／工具缺席 rc0 fail-open／`--repo` 指非目錄 rc2。無 `--refresh` 旗標（`ci-wait` 恆打網路——它的存在意義就是等本次 push 的結論；讀快取那條是 `ci-status` 的語意，見 [S3]）。

### [S2] 修復重試迴圈（skill 紀律，機械原語由 [S1] 出）

`lumos-project-notes` skill 的收尾段與 code-loop 收斂後段各加一條——**push 成功後必跑 `lumos ci-wait`**：

- rc0（綠）→ 收工。
- rc1（紅）→ **當輪修**：讀 [S1] 印出的失敗步驟＋log 尾段 → 定位 → 修 → commit → push → **再跑一次 `ci-wait`**。
- **重試上限 2 次**（＝最多推三次）。仍紅 → **停、攤給人**，並把失敗步驟／log 尾段／已試修法寫成 Issue 節點（`Issues/CI-<sha7>-紅燈`，帶 `pitfall_when`），不無限燒。
- **flaky 判別（誠實，不自動化）**：同一 sha 重跑一次就綠 → 記為疑似 flaky 進 Issue，不當修好（避免「重跑到綠」變成掩蓋真 bug 的慣性）。
- **[S2] 全段屬 skill 紀律層（同誠實天花板一類），非機械閘**：重試上限、flaky 判別、Issue 產出都靠自覺遵守＋收尾報告留痕；工具端只出 rc1 訊號與失敗證據（[S1]）。明文記此邊界，勿誤以為有機械保證。
- **紅燈不過夜**：修不完就寫 Issue 並在收尾報告明講「main 上有紅燈未解」，不得靜默收工。

### [S2b] 後備網（主路徑失效時才用，都只提醒不擋）

1. **SessionStart hook**：session 中斷／機器關機導致 [S2] 沒跑完時的兜底——讀帳最後一筆，紅且 sha 仍是祖先 → 開場注入一行提醒。綠或無資料靜默。
2. **pre-push**：帳上最後一筆為紅且 sha 仍是祖先 → stderr 一行提醒（不改 rc，不新增擋點）。
3. **`lumos gov` 第 7 源**：CI 事件併入治理時間軸。**mapper 欄位明定**（對齊既有 load() 契約）：`ts=d.ts`／`commit=d.sha`／`gate="ci"`／`kind=d.conclusion`（success/failure/…）／`hard=False`／`nodes=[]`／`token=d.dedup_key`（第 5 去重鑑別子）／`detail=f"{d.title} {d.failed_step}".strip()`。

### [S3] 帳與離線查詢

- `lumos ci-status`（唯讀、不打網路）：印帳上最後一筆＋`(檢查於 <ts>)`；超過 24 小時加註可能過期。供 hook 與離線用。
- **帳檔欄位（單源，全 spec 以此為準）**：`{ts, run_id, sha, conclusion, title, url, failed_step}`——`failed_step` 僅紅燈時非空；無 `checked_at`（`ts` 即檢查時刻）。
- 去重鍵＝`(run_id, conclusion)`：同 run 同結論重跑不重複 append；狀態變化（如 `in_progress`→`failure`）各記一筆。
- 寫入走既有 `_jsonl_append_verified(path, rec, key_field, key_value)`（**實查簽名：caller 給欄名與值**）——本案傳 `key_field="dedup_key"`、值＝`f"{run_id}:{conclusion}"`，故記錄多帶一個 `dedup_key` 欄供自驗與去重共用。
- **SessionStart hook 與 `ci-status` 皆不打網路**（避免拖慢開場）；只有 `ci-wait` 會連線。

### [S4] 測試（TDD，依現有一函式一主題慣例拆：`t_ci_wait`／`t_ci_status_and_gov`／`t_ci_hooks`）

1. `gh` 不存在（PATH 隔離）→ ci-wait rc0＋stderr 說明＋不寫帳；
2. 假 `gh` fixture（第一次回 in_progress、第二次回 success）→ 輪詢後 rc0、寫帳一筆（狀態變化各一筆）；
3. 假 `gh` 回 failure ＋ `--log-failed` 吐固定文字 → **rc1**、輸出含失敗步驟名與 log 尾段（截 4000 字）；
4. 只認**當前 HEAD sha 的 run**：fixture 回別的 sha 的 run → 不當結論、繼續等到逾時；
5. 逾時（`--timeout 1` ＋ 恆 in_progress fixture）→ rc0＋提示，帳記 `timeout-waiting`；
6. `--json` 單行純 JSON（含 conclusion/url/failed_step）；
7. `ci-status` 唯讀不呼叫 `gh`（fixture 設成呼叫即失敗，仍 rc0、讀帳輸出）；帳 >24h 加註過期；
8. gov 第 7 源顯示 CI 事件；
9. SessionStart hook：紅且為祖先 → 注入；綠 → 靜默；紅但 sha 非祖先（已 rebase 掉）→ 靜默；
10. pre-push 提醒：帳最後一筆紅且為祖先 → stderr 有提醒且 **rc 不變**（不新增擋點）；綠 → 無提醒；
11. 去重：同 run 同 conclusion 連跑兩次 → 帳只一筆；
12. 寫後自驗失敗（帳檔 symlink→/dev/null）→ ci-wait 印落盤自驗失敗、rc2（沿 `_jsonl_append_verified` 既有語意，優先於紅燈 rc1）；
13. `--repo` 指非目錄 → rc2；`gh` 未登入（fixture 吐鑑權錯誤 rc≠0）→ rc0 fail-open＋stderr；非 GitHub remote → rc0 fail-open；
14. **重試上限機械面**：`ci-wait` 不含重試邏輯（重試是 [S2] skill 紀律）——測項僅釘「rc1 時輸出含可據以修復的失敗步驟＋log 尾段」，重試次數不由工具強制（明文取捨：紀律面不機械化，防工具替人決定何時放棄）。

### [S5] 文件

- README 指令參考加 `ci-wait`／`ci-status` 兩行＋工作流圖加「push → ci-wait → 紅則當輪修」一步；ARCHITECTURE 治理帳段落更新為七帳。
- 本節點記「為什麼不做雲端 autofix」，供未來重議時看得到取捨。

## 實務隱患

- `gh` 未登入時 `gh run list` 會回錯誤而非空結果 → fail-open 需吃 rc≠0 與空輸出兩型。
- 同一 sha 可能有多個 workflow（未來擴充）→ v1 只取最近一次 run，明文限制。
- 分支切換頻繁時快取最後一筆可能屬別的分支 → 記錄帶 sha，推播前驗「是當前分支祖先」才提醒。

## 審計修正紀錄

- **pre-flight**（2026-07-29，機械 checklist＋現碼實查，不計 loop findings）：①rc 規格自相矛盾（「恆 0」vs 紅燈 rc1，會讓主路徑失去觸發訊號）→ rc 明定五態；②`--refresh` 誤植（`ci-wait` 恆打網路，讀快取是 `ci-status` 語意）→ 刪；③帳檔欄位兩處打架＋檔名未定 → 單源定義於 [S3]＋補 `dedup_key` 欄（對齊 `_jsonl_append_verified` 實查簽名）；④PRIOR-ART 誤述「SessionStart hook 已存在」→ 實查僅 PreToolUse/PostToolUse/Stop 三事件，更正為新建；⑤gov mapper 欄位未定 → 對齊既有 load() 契約逐欄明定；⑥[S4] 測試名與慣例不符＋漏 6 型 → 拆三函式＋補測項 10-14；⑦重試/flaky/Issue 屬紀律層非機械閘 → 邊界明文（防誤以為有機械保證）。
