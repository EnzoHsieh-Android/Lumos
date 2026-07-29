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
  KEY:★彈性宣告(2026-07-29 使用者裁定,零侵入預設)★——推送路徑由專案 `.lumos/config.json` 的 `ci.flow` 宣告:**無宣告=direct(現況,裝了新功能行為不變)**／`pr`(一律分支+PR,紅燈碰不到 main)／`tier`(混合:pitfalls tier=high 才走 PR);GitHub 端 branch protection/ruleset **完全不必動**(工具端行為,隨時改 config 切換,不影響其他人與消費專案)
  KEY:解法方向=**push 後同輪等待+修復重試(watch-fix-retry)**,非雲端自動修也非留到下次開場:`lumos ci-wait` 在 push 成功後阻塞等 CI 結論→紅則印失敗步驟+log 尾段→在場 session 當輪修→重推→再等(最多 2 次自動重試,之後攤人);SessionStart 推播降為**後備網**(session 中斷/機器關機才用),不是主路徑
  KEY:★不採雲端 autofix(明文裁定)★——世界主流(Copilot cloud agent 一鍵修/Codex workflow_run autofix/GH Agentic Workflows)是 CI 失敗觸發 agent 在雲端改碼開 PR;與 2026-07-29 剛裁定的「autonomous 非 dry-run 停用」同源風險(無人看顧 agent 握寫入權=confused-deputy),且需把金鑰放進 CI → 本案明文排除,解禁條件同 [[Systems/nested-agent-permission-scope]] d4
  DEP:[[Systems/reversibility-governance-ledger]]
---
# CI 回流閉環_計劃

`PRIOR-ART:` ① 最小層：`gh run list --json` 已能查狀態、`lumos gov` 已是多帳彙整器、Claude hook 註冊機制（`merge-claude-settings.py` 的 `HOOK_ENTRIES`）已存在——主路徑 [S1][S2] 屬接線；**但 [S2b]-① 的 SessionStart hook 是新建**（實查現有僅註冊 PreToolUse/PostToolUse/Stop 三事件，無 SessionStart），需新增 hook 檔＋新事件登記，pre-flight 已更正原「已存在」的誤述。② 世界解過：Copilot cloud agent 一鍵修復、Codex `workflow_run` autofix、GH Agentic Workflows self-healing CI——全屬「雲端 agent 自動改碼開 PR」型。③ 裁定＝**borrow-design 但反向取捨**：借「CI 失敗要有下游接手」的問題定義，**拒絕**其雲端無人值守實作（見上方 ★ 裁定），改為本機拉取＋人在場修復。

## 範圍刀（明確不做）

- **不做**雲端自動修復／自動開 PR（見 ★ 裁定；解禁＝子 agent 唯讀隔離落地）。
- **不做** webhook／常駐監聽（要開埠、要密鑰；pull 模式夠用）。
- **不擋** push／commit：CI 狀態不新增本機硬閘（`ci-wait` 的 rc1 是給 skill 判讀用的訊號，不是閘）。
- **不做**無限重試：修復重試上限 2 次，之後攤人＋寫 Issue（防燒錢與掩蓋真 bug）。
- **不做**跨 repo 聚合：只查當前 repo 當前分支。
- **不動 GitHub 設定**：不要求也不代設 branch protection／ruleset／auto-merge repo 選項（那是人的決定，且會全域影響消費專案）——工具端在有無保護下都能運作。
- **不改預設行為**：未宣告 `ci.flow` 的專案（含所有既有消費 repo）行為與現在**逐字相同**（直推、無 PR、無新閘）。
- **不解析** CI log 全文做根因判讀（v1 只取失敗步驟名＋log 尾段；判讀交在場的人／session）。

## 條款

### [S1] `lumos ci-wait [--timeout 600] [--repo-dir D] [--json]`——push 後同輪等結論（主路徑）

**旗標更名（r1 四方同報）**：原 `--repo` 與 `gh` 原生 `-R/--repo`（吃 `OWNER/REPO` 字串）語意相反、直傳會被 gh 拒收 → 改名 `--repo-dir`（本機目錄，沿 lumos 家族語意）；**owner/repo 由本案自行從 `git -C D remote get-url origin` 解析後餵 `gh -R`，不轉發使用者輸入**。

- **時機**：`git push` 成功之後**立刻**在同一輪跑（CI 於 push 完成即觸發，~3 分鐘出結論）。
- 行為：先解析當前 HEAD sha → 輪詢 `gh run list --branch <分支> --json databaseId,headSha,status,conclusion,displayTitle,url`（間隔 15s，`--timeout` 預設 600s）直到**該 sha 的 run** 出現且 `status=completed`。
- **綠**：印一行綠燈訊息、寫帳、rc0。
- **conclusion 九值分三類（r1：原紅/綠二分不窮盡；gh 實有 success/failure/cancelled/skipped/timed_out/action_required/neutral/stale/startup_failure）**：
  - **綠**＝`success`／`neutral`／`skipped` → rc0。
  - **紅**＝`failure`／`timed_out`／`startup_failure` → rc1＋失敗證據（下行）。
  - **未定**＝`cancelled`／`action_required`／`stale` → rc0＋印「非成功但無失敗步驟可歸因」＋寫帳，**不進修復路徑**。
- **紅燈證據取得（r1+Codex：`--log-failed` 是純文字 log 非結構化 step API，多 job 平行時輸出交錯，且可能只標 UNKNOWN STEP）**：步驟名走 **`gh run view <id> --json jobs`** 取 `jobs[].steps[]` 中 `conclusion=="failure"` 者——**多個失敗步驟全列**（`job/step` 成對，`failed_step` 欄以 `;` 串接）；log 證據才用 `--log-failed`，**先取尾 40 行、再截 4000 字**（兩上限依序，r1 定序）；＋run URL；寫帳；**rc 1**。
- 逾時未出結論：印已知狀態＋提示手動查，寫帳（`conclusion=timeout-waiting`），**rc 0**（不把等待逾時當失敗）。
- `gh` 不存在／未登入／非 GitHub remote → stderr 一行說明＋**rc0** fail-open（不因缺工具卡住任何流程）。
- 帳檔：docs 下的 ci-log JSONL（本案新建產物，檔名比照既有六帳的 dot-log 慣例；欄位單源定義見 [S3]）。
- 輸出：文字模式一行 `CI <conclusion> <sha 前7> <title> → <url>`；`--json` 單行純 JSON。
- **rc 單源（全 spec 以此為準，含優先序）**：`--repo-dir` 非目錄 rc2 ＞ **帳檔寫入/自驗失敗 rc2**（沿 `_jsonl_append_verified` 語意，優先於紅燈——r1 抓到原 rc 表與 [S4] 測項打架）＞ 紅 rc1 ＞ 綠/未定/逾時/工具缺席 rc0（fail-open）。無 `--refresh` 旗標（`ci-wait` 恆打網路——它的存在意義就是等本次 push 的結論；讀快取那條是 `ci-status` 的語意，見 [S3]）。

### [S1b] 推送路徑分派（`.lumos/config.json` 的 `ci.flow`，彈性宣告）

```json
{"ci": {"flow": "direct|pr|tier", "auto_merge": true}}
```

- **`direct`（預設，無宣告即此）**：現況——直接 push 目標分支 → `ci-wait` → 紅則當輪修（[S2]）。**裝了本功能不改變任何既有專案的行為**。
- **`pr`**：改動一律走 feature 分支——`lumos ship` 幫忙串：建/推分支 → `gh pr create --fill` → （`auto_merge` 為真時）`gh pr merge --auto --squash` → `ci-wait` 等該分支的 run → 綠則由 GitHub 自動合併進 main、紅則在分支上修（main 全程乾淨）。
- **`tier`（混合，推薦）**：跑 `lumos pitfalls --diff <base>..HEAD` 取尾行 tier——`high` 走 `pr` 路徑、`standard` 走 `direct`。**沿用既有風險分級器，不新造判準**。
- **config 讀取**：沿既有 `.lumos/config.json` 慣例（同 cochange/test-layers/lint 宣告）；未知 `flow` 值 → stderr 警告＋**退回 `direct`**（fail-safe：不因設定打錯就改變推送行為）。
- **`auto_merge` 前提誠實**：GitHub 端未開「Allow auto-merge」或無必要檢查時，`gh pr merge --auto` 會失敗 → 捕捉後降級為「PR 已開、請人工合併」＋stderr 說明，**不視為錯誤**（rc 不變）。
- **GitHub 端硬保護（選配、與本案解耦）**：若日後要機械強制「紅燈不准進 main」，走 GitHub **Rulesets**（支援 evaluate 只記錄不擋的試跑模式、支援 bypass 名單保留緊急直推並留痕）——本 spec 不代設、不依賴其存在。

### [S2] 修復重試迴圈（skill 紀律，機械原語由 [S1] 出）

`lumos-project-notes` skill 的收尾段與 code-loop 收斂後段各加一條——**push（或 `lumos ship`）成功後必跑 `lumos ci-wait`**（[S1b] 三種 flow 共用同一套修復迴圈；差別只在「紅燈修在 main 上還是分支上」）：

- rc0（綠）→ 收工。
- rc1（紅）→ **當輪修**：讀 [S1] 印出的失敗步驟＋log 尾段 → 定位 → 修 → commit → push → **再跑一次 `ci-wait`**。
- **重試上限 2 次**（＝最多推三次）。仍紅 → **停、攤給人**，並把失敗步驟／log 尾段／已試修法寫成 Issue 節點（`Issues/CI-<sha7>-紅燈`，帶 `pitfall_when`），不無限燒。
- **flaky 判別（誠實，不自動化）**：同一 sha 重跑一次就綠 → 記為疑似 flaky 進 Issue，不當修好（避免「重跑到綠」變成掩蓋真 bug 的慣性）。
- **[S2] 全段屬 skill 紀律層（同誠實天花板一類），非機械閘**：重試上限、flaky 判別、Issue 產出都靠自覺遵守＋收尾報告留痕；工具端只出 rc1 訊號與失敗證據（[S1]）。明文記此邊界，勿誤以為有機械保證。
- **紅燈不過夜**：修不完就寫 Issue 並在收尾報告明講「main 上有紅燈未解」，不得靜默收工。

### [S2b] 後備網（主路徑失效時才用，都只提醒不擋）

1. **SessionStart hook（新建）**：讀帳最後一筆，紅則開場注入提醒；綠／無資料靜默。
   - **落地三處必改（r1 實查，缺一即靜默失效）**：① 新 hook 檔進 `scripts/hooks/claude/`；② 登記進 `merge-claude-settings.py` 的 `HOOK_ENTRIES`（新事件 SessionStart）；③ **檔名加進 `scripts/lumos` 的 `_GLOBAL_CLAUDE_HOOKS` 白名單**——否則檔案不被複製到 `~/.claude/hooks/`，下次 init/bootstrap 時 `_prune_dangling` 會把註冊剪掉。
   - **生命週期對稱（impact hook 推播命中 [[Issues/hook卸載殘留註冊]]，其通則正中本案）**：該事故通則＝「凡 A 端刪除／B 端引用的成對資源，守衛要嘛對稱操作、要嘛 B 端懸空自癒」；本案是同一面鏡子的另一面「註冊了沒複製＝silent no-op」——故三處必改缺一不可，且 [S4] 須有測項釘住「註冊存在 ⟺ 檔案存在」（沿既有 `t_merge_settings_prunes_dangling` 的守衛精神）。
   - **輸出契約**：沿 PreToolUse hook 的 stdout JSON 形式（`hookSpecificOutput.additionalContext`），不用 Stop hook 的 stderr+exit2（事件語意不同）。
   - **提醒精準度（r1+Codex）**：帳檔加 `branch` 欄；觸發條件＝最後一筆為紅 ∧ 其 sha 是當前 HEAD 祖先 ∧ 其 branch＝當前分支——防「從紅 sha 開的新分支被永久提醒」。
2. **pre-push**：同上三條件 → stderr 一行提醒（不改 rc、不新增擋點）。**插入點明定（r1 實查）**：須放在 `have_vault` 早退之前——否則無 vault 的 repo 永遠看不到提醒。
3. **`lumos gov` 第 7 源**：CI 事件併入治理時間軸。**mapper 欄位明定（一律 `d.get(...)` dict 存取，對齊既有六源——r1 指正屬性存取會讓 `lumos gov` 全源炸掉）**：ts／commit（取 sha）／gate＝ci／kind（取 conclusion，缺則 ?）／hard＝False／nodes＝[]／token（取 dedup_key，第 5 去重鑑別子）／detail（title＋failed_step 串接後 strip）。**無 severity 欄**（CI 事件無嚴重度語意；原文的 tier 欄是幽靈欄位，帳檔從未寫入）。

### [S3] 帳與離線查詢

- `lumos ci-status`（唯讀、不打網路）：印帳上最後一筆＋`(檢查於 <ts>)`；超過 24 小時加註可能過期。供 hook 與離線用。
- **帳檔欄位（單源，全 spec 以此為準）**：`{ts, run_id, sha, conclusion, title, url, failed_step}`——`failed_step` 僅紅燈時非空；無 `checked_at`（`ts` 即檢查時刻）。
- **只在終局寫帳（r1 修矛盾：原文暗示 in_progress 也記，與 [S1] 終局寫帳打架）**：`ci-wait` 只在**綠／紅／未定／逾時**四種終局各寫一筆；輪詢中的 `in_progress` 不寫帳。
- **去重是應用層責任（r1 實查：`_jsonl_append_verified` 是「無條件寫入再讀回自驗」，不是 upsert，擋不了重複）**：寫入前先掃帳檔，已存在同 `dedup_key`（＝`run_id:conclusion`）→ 跳過寫入直接輸出（不算失敗）；否則才呼叫 helper（`key_field` 傳 `dedup_key`）。
- **逾時且該 sha 的 run 從未出現**：`run_id` 記 null、`dedup_key` 改用 `nosha:<sha>:timeout-waiting`（避免此型互相去重吞掉）。
- **SessionStart hook 與 `ci-status` 皆不打網路**（避免拖慢開場）；只有 `ci-wait` 會連線。

### [S4] 測試（TDD，拆三函式：`t_ci_wait`／`t_ci_status_and_gov`／`t_ci_hooks`；gh 一律 fixture 腳本，**不打真 API**）

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
14. conclusion 九值分類：neutral／skipped → rc0 綠；cancelled／action_required／stale → rc0 未定且不取失敗步驟；timed_out／startup_failure → rc1 紅；
15. 多 job 平行失敗 fixture（兩 job 各有失敗 step）→ failed_step 含兩者（`;` 串接）且取自 jobs JSON 非 log 解析；
16. log 兩上限依序：先 40 行後 4000 字（構造 100 行超長 log 驗）；
17. 逾時且 run 從未出現 → run_id null、dedup_key 走 nosha 形式；兩個不同 sha 的逾時各記一筆（不互吞）；
18. branch 欄與提醒精準度：紅 sha 是祖先但 branch 不同 → hook 靜默；
18b. hook 生命週期對稱：新 hook 同時在 `HOOK_ENTRIES` 與 `_GLOBAL_CLAUDE_HOOKS` 白名單中（缺一即紅），且 merge 後註冊不被 `_prune_dangling` 剪掉；
19. **flow 分派**：無宣告 → 走 direct（不呼叫 gh pr，行為與現況逐字相同）；`flow=pr` → 呼叫 pr create/merge（fixture 攔截）；`flow=tier` ＋ pitfalls 吐 `tier: high` → 走 pr 路徑，吐 `standard` → 走 direct；未知 flow 值 → 警告＋退 direct；
20. **auto_merge 降級**：`gh pr merge --auto` fixture 回失敗 → 印「PR 已開、請人工合併」、rc 不變（非錯誤）；
21. **重試上限機械面**：`ci-wait` 不含重試邏輯（重試是 [S2] skill 紀律）——測項僅釘「rc1 時輸出含可據以修復的失敗步驟＋log 尾段」，重試次數不由工具強制（明文取捨：紀律面不機械化，防工具替人決定何時放棄）。

### [S5] 文件

- README 指令參考加 `ci-wait`／`ci-status`／`ship` 三行＋`.lumos/config.json` 的 `ci.flow` 宣告一段（含「無宣告＝現況不變」的醒目說明）＋工作流圖加「push → ci-wait → 紅則當輪修」一步；ARCHITECTURE 治理帳段落更新為七帳；**`cmd_gov` docstring「六帳」改七帳**（in-code 文件同步）；**新帳檔補進 vault `.gitignore` 樣板與 `_COCHANGE_DEFAULT_EXCLUDE`**（比照既有六帳，防誤入版控與假共改警訊）。
- 本節點記「為什麼不做雲端 autofix」，供未來重議時看得到取捨。

## 實務隱患

- `gh` 未登入時 `gh run list` 會回錯誤而非空結果 → fail-open 需吃 rc≠0 與空輸出兩型。
- 同一 sha 可能有多個 workflow（未來擴充）→ v1 只取最近一次 run，明文限制。
- 分支切換頻繁時快取最後一筆可能屬別的分支 → 記錄帶 sha，推播前驗「是當前分支祖先」才提醒。

## 審計修正紀錄

- **pre-flight**（2026-07-29，機械 checklist＋現碼實查，不計 loop findings）：①rc 規格自相矛盾（「恆 0」vs 紅燈 rc1，會讓主路徑失去觸發訊號）→ rc 明定五態；②`--refresh` 誤植（`ci-wait` 恆打網路，讀快取是 `ci-status` 語意）→ 刪；③帳檔欄位兩處打架＋檔名未定 → 單源定義於 [S3]＋補 `dedup_key` 欄（對齊 `_jsonl_append_verified` 實查簽名）；④PRIOR-ART 誤述「SessionStart hook 已存在」→ 實查僅 PreToolUse/PostToolUse/Stop 三事件，更正為新建；⑤gov mapper 欄位未定 → 對齊既有 load() 契約逐欄明定；⑥[S4] 測試名與慣例不符＋漏 6 型 → 拆三函式＋補測項 10-14；⑦重試/flaky/Issue 屬紀律層非機械閘 → 邊界明文（防誤以為有機械保證）。
- **r1 panel**（2026-07-29，3 席 sonnet＋Codex 否決；**三席 canary 全中**；存活全機械證實免辯方）：[major] ①`--repo` 與 gh 原生 `-R` 語意相反、直傳被拒 → 更名 `--repo-dir`＋自行解析 owner/repo（四方同報）；②conclusion 當紅綠二分、實有九值 → 三類明定（席2）；③`--log-failed` 非結構化 step API＋多 job 交錯 → 步驟名改走 `--json jobs` 且全列（席1+Codex）；④gov mapper 用屬性存取會讓 `lumos gov` 全源炸、且 severity 欄是幽靈 → 改 dict 存取＋刪欄（席2）；⑤`_jsonl_append_verified` 不是 upsert、去重須應用層自己擋 → 明文（席3）；⑥SessionStart hook 漏 `_GLOBAL_CLAUDE_HOOKS` 白名單 → 註冊會被 `_prune_dangling` 剪掉而靜默失效 → 三處必改＋輸出契約明定（席3+Codex）；⑦pre-push 提醒若放 `have_vault` 早退之後永不觸發 → 插入點明定（席3+Codex）；⑧rc 表與測項 12 打架（自驗失敗 rc2 未入表）→ rc 單源含優先序；⑨in_progress 是否寫帳自相矛盾 → 只在四終局寫帳；⑩`DEP` 指向不存在的節點（ghost）→ 改指真實治理帳節點（席2）。[minor] 逾時無 run_id 的 dedup 形式；log 兩上限定序；branch 欄防跨分支誤提醒；`cmd_gov` docstring 六→七帳；新帳檔補 gitignore 與 cochange exclude。測項補 14-18。
  canary 帳：席1 caught（b 型幽靈旗標）、席2 caught（c 型幽靈欄位，並點出屬性存取致命）、席3 caught（d 型幽靈產物）。
