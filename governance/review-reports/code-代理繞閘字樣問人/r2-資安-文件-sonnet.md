severity: clean

文件註冊組(計劃、三篇 Systems 節點、`scripts/lumos`、`merge-claude-settings.py`)的 456 行 patch 我逐 hunk 讀完,沒有可利用的洞。除下面第 1 類的路徑引號驗證外,以下都是對 patch 內文的推論,我沒另外跑重現。

**1. 執行邊界:已看,無。**
- **指令字串組法**:新的 `bypass-ask-hook.py` 註冊是用 `HOOK_ENTRIES` 裡既有的 `_hook_cmd("bypass-ask-hook.py")` 組出來。
  - 組法沒有改動。我讀了修後版的 `_hook_cmd`,POSIX 分支把 Python 路徑用 `shlex.quote` 包好,`${HOME}/.claude/hooks/<rel>` 放在雙引號裡,所以路徑含空白不會被 shell 切開。
  - `rel_path` 是寫死的常數,不來自外部輸入。
  - `--budget 5` 來自 `HOOK_BUDGET` 常數。
  - 這條註冊沒有引入新的注入面。
- **`_codex_entries` 的跳過判法**:判法是 `event == "PreToolUse" and e.get("matcher") == "Bash"`,比對的是程式內建的 `HOOK_ENTRIES` 字典,不是讀使用者設定檔。設定檔內容繞不過它。
  - 這個跳過只影響 Codex 的註冊表產出,不涉及授權。
- **安裝、拆除名單**:`_VENDORED_TREE_FILES`、`_GLOBAL_CLAUDE_HOOKS`、`ANCHOR_FILES`、`enforcement_status` 的新增項都是字面常數檔名,沒有路徑分隔符,也沒有變數拼接。
  - 一個固定檔名被複製或刪除,無法指向別的位置。
  - 我沒有把這些名單背後的複製與刪除函式整支讀一遍,只確認新增項本身是安全的常數。
- **錨點**:`ANCHOR_FILES` 加一項,是把這支每條 Bash 都會跑的掛鉤納入完整性監控。這是收緊,不是放寬。

**2. 文件裡寫給人照抄的指令:已看,無。**
- 〈回退〉只講「拿掉 matcher、移到 `_RETIRED_STUB_CLAUDE_HOOKS`、拿掉 enforcement 列舉、重跑安裝」,沒有 `rm -rf`、`curl | sh`、`sudo`、`--force` 之類的危險指令。
- 計劃文件裡出現的 `F=--no-verify; git push $F` 等寫法,是〈範圍〉列的「攔不到寫法」範例,不是要人執行的步驟。
- 筆記裡的 `[test:…]` 只是引用測試名。

**3. 授權範圍有沒有被放寬:已看,無。**
- 新 matcher 為 `Bash`,每條 Bash 指令都會叫這支掛鉤。
- 掛鉤只會回 `ask`,也就是把原本不問的指令升級成要問人。patch 裡沒有任何路徑讓它回 `allow`,也沒有改寫 `permissionDecision` 為放行。
- 失敗時放行,等於維持沒有這支掛鉤時的原狀,不是新放寬。計劃明寫這是問人層、不是安全邊界,範圍外的繞法我不當 finding 重報。
- 逾時 5 秒。只有命中且落在暫存目錄時才會跑 git 子程序,這部分屬程式組,不在本組。

**固定席節點逐條判:**
- `Issues/code-loop守衛main-direct盲區`:不影響。本 patch 沒動 code-loop 守衛的判斷。
- `lumos-cli-read`、`lumos-cli-lifecycle` 的 ★INVARIANT★:不影響。
  - 這次對 `scripts/lumos` 的改動只有名單加一項,沒碰 search 濾網或 re-inject。
  - lifecycle 筆記只多一行 WHY,沒有動 re-inject 的 sentinel 行。
- `design-loop`、`測試假綠形態`、`guard-kill`:不影響。patch 沒有改這些合約管的邏輯。
- `pitfalls-code-loop`、`reversibility-governance-ledger` 的 ★RISK★:不影響。
  - `scripts/lumos` 的改動只是名單加字面常數檔名。
  - 這些筆記管的風險路徑沒有被碰到。
- 其餘「只列名」節點:本組 patch 內容與它們無關,不影響。

**修補鏡頭三問:**
- **原問題的修復效果**:本組只含文件和註冊,沒有行為性修復,未判定。行為修復在程式組。
- **修補處的正常、錯誤與相鄰路徑**:註冊路徑沿用既有 `_hook_cmd`,與同批其他 hook 同形,我判定仍成立。
- **新發現的修前、修後差異**:沒有新發現,不適用。

**未驗範圍:** 我沒載入 `bypass-ask-hook.py` 跑 `bypass_reasons`,因為那屬程式組。也沒實測 `merge-claude-settings.py` 在路徑含特殊字元時的實際輸出。

最嚴重等級 clean,blocking 共 0 條。
