# r1-s3 — autonomous-loop.sh stale-pending block + merge-claude-settings.py dedupe/retirement

審查對象：`git diff 9a95bc4..HEAD` 中 `governance/autonomous-loop.sh` 的新 stale-pending 區塊、`scripts/merge-claude-settings.py` 的自癒去重 + rot-check 撤除。方法：讀 HEAD 實檔（非僅 patch）、跑針對性單元測試、手動重現 bash/xargs/find 語意。

## 逐項覆核

### 1. `governance/autonomous-loop.sh:96-112`（stale-pending 告警區塊）

- **`$STALE` 傳遞方式**：`$STALE`（可能多行）從未被直接內插進 `python3 -c` 的原始碼字串（第 104-108 行）——只透過 `MSG=...`／`LINE_TOKEN=...` 兩個 env-var 前綴（第 102-103 行）傳給該次呼叫，python 端經 `os.environ` 讀取，不經 shell 二次展開。換行、空格、CJK 字元都不會破壞 python 語法或造成注入。實測 `python3 -c "compile(...)"` 對抽出的內層腳本語法檢查通過。
- **`find -mtime +3`（macOS/BSD vs Linux/GNU）**：實機（Darwin 25.5.0）跑 `find … -mtime +3` 驗證：剛建立的檔案不命中、5 天前 mtime 的檔案命中，語意與 GNU find 一致（本專案 launchd 只跑 macOS，不存在跨平台落差風險）。
- **`LINE_TOKEN` 來源**：不在 `daily-governance.sh`／plist `EnvironmentVariables` 匯出（已核對兩處均無 `LINE_TOKEN`），而是沿用本檔案既有慣例——每個呼叫點各自 `LINE_TOKEN="$(cat "$HOME/.config/ai-daily/line_token" 2>/dev/null)"` 現讀現傳（第 68/103/119/194/215/244/260/279 行皆同構）。新區塊與既有 8 處寫法一致，不是新引入的行為；token 檔存在（`~/.config/ai-daily/line_token`，600 權限）。若檔案缺失則 `no-token` 靜默降級——這是整份腳本既有的 fail-open 設計，不是本次改動新增的風險面。
- **`xargs -n1 basename` 對 CJK 檔名**：CJK 多位元組字元不是 IFS 空白字元，`xargs`/`basename` 對其無切字問題（實測含 CJK 檔名的路徑正確萃取 basename）。對「檔名含空格」的邊界也實測過：因 `$PENDING`（repo 內固定路徑，不含空格）恆為每行第一個 token 的前綴，`xargs -n1 basename` 逐 token 去掉目錄部分後、由 `tr '\n' ' '` 重新接回，數學上必還原成原始 basename 字串（僅第一個 token 帶路徑、其餘 token 本來就不含 `/`，basename 對它們是恆等映射）。因此在本部署路徑下不會產生錯字或錯位，只是實作手法較迂迴（用 `sed 's#.*/##'` 更直接），不到需要修的程度。
- **`exit 0` vs 非零**：新分支與同函式其餘分支（例如原本「無可展開 gap」分支）一致地用 `exit 0`；本腳本的失敗訊號通道設計上就是 LINE 推播而非 process exit code（`daily-governance.sh` 也只是 log rc、不依 rc 做分流）。與既有慣例一致，非缺陷。

**結論**：此區塊邏輯正確、與既有慣例一致，未發現 major/blocker。

### 2. `scripts/merge-claude-settings.py`（自癒去重 + rot-check 撤除）

- **去重 pass 相對 `_prune_dangling` 的順序**：讀 `main()`（第 133-181 行）確認執行序為 `_prune_dangling`（142-145 行）→ HOOK_ENTRIES merge/add（147-168 行，`--prune-only` 時跳過）→ 自癒去重（170-181 行，最後執行、且不受 `--prune-only` 影響）。這個順序對最終狀態是等冪且與交換順序無關：`_prune_dangling` 只看「檔案是否存在」、去重只看「(matcher, script 檔名) 是否等價」，兩者判準互相獨立，任一先跑都收斂到同一個最終集合（已用 `t_merge_dedupes_preexisting_duplicates` 與 `t_merge_settings_prunes_dangling` 兩條測試分別覆蓋，皆綠）。
- **rot-check 撤除的端到端路徑追蹤**（`file 刪除 → _prune_dangling 判懸空 → 註冊被剪`）：
  1. `scripts/lumos:9006-9013 _sync_global_claude`：① copy `_GLOBAL_CLAUDE_HOOKS`（已不含 `verification-rot-check.py`）② 對 `_RETIRED_CLAUDE_HOOKS`（新增了 `verification-rot-check.py`，`scripts/lumos:8994`）逐一 `unlink()` 真檔 ③ 呼叫 `merge-claude-settings.py`（不帶 `--prune-only`，走預設 merge）。
  2. `merge-claude-settings.py:_prune_dangling`：對每條 hook entry 抽出 command 內的 `*.py` 檔名，若含 `.claude/hooks/` 且該檔在磁碟不存在 → 剪掉。由於步驟 1② 已把 `verification-rot-check.py` 從磁碟刪除，此時它必然判定懸空、被剪。
  3. `HOOK_ENTRIES["PostToolUse"]` 已改為空 list（`scripts/merge-claude-settings.py:70`），merge 階段不會把它加回來。
  4. 這條「刪真檔→_prune_dangling 剪註冊」路徑本身是既有通用機制（非本次新寫），已有等價測試覆蓋（`t_install_global_hook_sync` 案例二，用 `code-loop-guard.py` 走同一段程式碼路徑；`_RETIRED_CLAUDE_HOOKS` 是 tuple 迴圈，新增一個元素即自動繼承同一驗證邏輯，不需要逐項專屬測試）。
  - 實測：單獨跑 `t_install_global_hook_sync`（8/8）、`t_merge_dedupes_preexisting_duplicates`（3/3）、`t_merge_settings_prunes_dangling`（4/4）、`t_merge_prune_only`（2/2）、`t_merge_settings_dedupe`（1/1）全綠，確認此路徑可信。
- **`PostToolUse` 非空斷言測試**：唯一提及 `PostToolUse` 的測試是 `t_merge_dedupes_preexisting_duplicates`（`scripts/test_lumos.py:3889`），斷言的是「兩份重複註冊 → 剪成一份」（`== 1`，非空），驗證的是「舊安裝器留下的、仍存在磁碟上的重複註冊」場景（測試裡自建了 stub `.py` 檔，非懸空），與「retired hook 磁碟檔案已被刪、最終應該剪成 0 份」是兩個不同場景，二者不衝突、也各自被覆蓋（後者由 `t_install_global_hook_sync` 案例二的通用機制驗證）。沒有發現遺漏的斷言缺口。

**結論**：dedupe pass 與 `_prune_dangling` 順序對最終狀態無影響（已用測試證實等冪）；rot-check 的檔案刪除→懸空判定→註冊剪除鏈路完整可信，有實際跑綠的測試支撐，非僅推論。

## 附帶查核（同一 diff 內、與 LENS 相關的周邊改動）

跑了以下針對性測試作為安全網（均綠，未列出逐條）：`code_exts_four_lists_agree`（7/7，含 .sh/.ps1 對齊）、`precommit_lints_staged_graph_nodes`（3/3，Gate L）、`gov_stats_gate_drift`（3/3，`delguard` 併入 `_KNOWN_GATES` 未破壞漂移守衛）、`delguard`（88/88，含降級落帳新斷言）。均未見紅燈。

## Severity 計數

blocker: 0, major: 0, minor: 0
