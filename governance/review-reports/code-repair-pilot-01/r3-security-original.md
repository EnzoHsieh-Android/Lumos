severity: blocker

本輪不能放行：找到 1 個已重現的 blocker、1 個因唯讀限制降級為 major 的真實隔離缺口。以下可直接交父代理存檔；本席未修改 repo、圖譜或暫存檔，也未執行模型探針、push 或網路寫入。

## Finding 1：Git command-scope config 可同時補回遠端並停用 pre-push

severity: blocker  
blocking: 是

引句:「指令會落到別的 repo 上(2026-09-21 審查席在完全正常的來源上重現過本體遠端被拔光)。」

材料: `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-code.patch:174`

file: scripts/scenario_probe.py:385  
file: scripts/scenario_probe.py:505  
file: scripts/scenario_probe.py:617  
file: scripts/scenario_probe.py:692  
file: scripts/test_lumos.py:36964

`_git_env()` 只移除六個 Git 路徑環境變數，仍保留：

- `GIT_CONFIG_COUNT`
- `GIT_CONFIG_KEY_*`
- `GIT_CONFIG_VALUE_*`
- `GIT_CONFIG_PARAMETERS`
- `GIT_CONFIG_GLOBAL`
- `GIT_CONFIG_SYSTEM`

具體輸入：

```text
GIT_CONFIG_COUNT=2
GIT_CONFIG_KEY_0=remote.r3escape.url
GIT_CONFIG_VALUE_0=https://example.invalid/r.git
GIT_CONFIG_KEY_1=core.hooksPath
GIT_CONFIG_VALUE_1=/dev/null
```

已用目前真程式 in-process 呼叫 `_git_env()`，再作唯讀 Git 查詢。可重現輸出：

```text
preserved: 2 remote.r3escape.url core.hooksPath
effective hooksPath: /dev/null
effective remotes:
Lumos      https://github.com/EnzoHsieh-Android/Lumos.git (fetch)
Lumos      https://github.com/EnzoHsieh-Android/Lumos.git (push)
r3escape   https://example.invalid/r.git (fetch)
r3escape   https://example.invalid/r.git (push)
```

執行路徑：

```text
父程序環境
→ _git_env 原樣保留 GIT_CONFIG_*
→ git remote 看見環境注入的遠端
→ remote remove 無法刪除 command-scope 設定，且回傳碼未檢查
→ git config core.hooksPath 寫入的副本設定被環境值 /dev/null 蓋過
→ Claude/Codex runner 繼承同一環境
→ 一般 git push r3escape HEAD 已有有效目標且不會執行防推 hook
```

我已重現到外部寫入前的全部決定性條件；依禁令沒有真的 push。這不是要求重造整個模型環境，而是本輪新加 `_git_env()` 與「pre-push 硬擋」的直接漏網輸入。

現有測試只注入 `GIT_DIR`、`GIT_WORK_TREE`，斷言也只檢查這兩個鍵，因此會假綠。

最小修復門檻：清除 Git config 注入入口，並用兩個 runner 都會繼承的環境驗證「有效遠端為空」及「有效 hooksPath 正是臨時 hooks 目錄」；測試要包含環境注入遠端及 hooksPath 覆寫。

## Finding 2：來源內部的 absolute separate-git-dir 會在複製後仍指回本體

severity: major  
blocking: 是

引句:「沙盒的隔離動作會寫進那個 git 目錄所屬的 repo——拔掉真遠端、改掉真 hooksPath,防護會靜默失效。」

材料: `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-code.patch:266`

file: scripts/scenario_probe.py:481  
file: scripts/scenario_probe.py:487  
file: scripts/scenario_probe.py:495  
file: scripts/scenario_probe.py:505  
file: scripts/scenario_probe.py:529

目前只確認「來源的實際 gitdir 位於來源目錄內」。以下合法形狀會通過：

```text
src/.git            → gitdir: /tmp/.../src/.hidden-git
src/.hidden-git/    → 真 Git 資料
```

`rsync -a` 會原樣複製 `.git` 裡的絕對路徑。副本的 `.git` 因此仍指回來源 `.hidden-git`；接下來的 `remote remove`、`git config`、`git add`、`git commit` 會改來源 Git 資料。

因唯讀沙盒不能建立 fixture，本席未執行，按要求由 blocker 自降為 major。父代理可在臨時目錄重現：

```sh
set -eu

repo=/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone
scratch=$(mktemp -d)
src="$scratch/src"
mkdir -p "$src"

git -C "$src" init -q --separate-git-dir "$src/.hidden-git" .
git -C "$src" config user.name fixture
git -C "$src" config user.email fixture@example.invalid
printf 'fixture\n' > "$src/x"
git -C "$src" add x
git -C "$src" commit -qm base
git -C "$src" remote add sentinel "$scratch/sentinel.git"

python3 -c '
import importlib.util, sys
spec = importlib.util.spec_from_file_location("scenario_probe", sys.argv[1])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print(mod.make_sandbox(sys.argv[2]))
' "$repo/scripts/scenario_probe.py" "$src"

printf 'after-remotes:\n'
git -C "$src" remote
printf 'after-hooks:\n'
git -C "$src" config --get core.hooksPath
```

預期重現輸出是 `sentinel` 已從來源消失，且來源 `core.hooksPath` 被改成 `/tmp/lumos-probe-.../hooks`。這不同於已處置的「gitdir 在來源外部」案例：本例的 gitdir 確實在來源內，但複製後的絕對 indirection 仍指回本體。

最小修復門檻：複製完成後重新解析「副本」的 absolute gitdir，要求它位於副本內且不與來源 gitdir 相同；否則在任何 Git 寫入前停手。加入 inside-source separate-git-dir 反例。

## 原問題驗收

- 成功工具內容才證明取得目標片段：通過。`source_evidence()` 只從成功且完成的工具結果接受 marker。
- 缺紀錄為 `unknown`、完整但未讀到為 `absent`：通過。
- v04 每個 attempt 使用獨立乾淨副本：通過；每次迴圈都進 `_run_source_attempt()`，重新產生 token 及 sandbox，finally 清理。
- 不污染真 repo：一般 clone 形狀通過；Finding 2 的 Git indirection 形狀不通過。
- C2：Claude 非零退出排除仍保留。
- C3：逐題有效分母仍保留。
- 卷證 `r3-regression.txt` 記載 `157 passed, 0 failed`；這是既有卷證，本席沒有在唯讀沙盒重跑。

## 固定席與圖譜影響

直接受影響：

- `Systems/codex-harness`：兩個 finding 都落在 sandbox、Git 環境及 runner 邊界。
- `Systems/測試假綠形態`：Git 環境測試只覆蓋 `GIT_DIR/GIT_WORK_TREE`；缺少上述兩條反事實輸入。
- `Issues/探針以工作樹為來源會改到本體`：外部 gitdir 舊案例已處置，但 Finding 2 顯示正面條件仍漏掉來源內 absolute gitfile。
- `Issues/探針讀碼證據不足`：本輪 marker/result 修補符合問題要求，沒有新增 finding。

已逐項核對、未見合約語意影響，可分組列為無影響：

- `Systems/lumos-cli-read`
- `Systems/lumos-cli-lifecycle`
- `Systems/bound-tests-gate`
- `Systems/canary-audit`
- `Systems/design-loop`
- `Systems/guard-kill`
- `Systems/slim-get-一行安裝`
- `Systems/slim-install-安裝器`
- `Systems/slim-uninstall-一行卸載`
- `Projects/規格落成可驗收條件_計劃`
- `Systems/lumos-deinit`
- `Projects/逃逸自動記_計劃`
- `Systems/節點範圍與索引守衛`
- `Systems/cochange-guard`
- `Systems/check-r-guard`

`py-eventloop`: na。本程式是同步 CLI，沒有 async event loop；`subprocess.run` 和 JSON 解析的文字命中不足以使事件迴圈題適用。`r3-pitfalls.json` 的 C901/E702 等樣式告警不構成本輪缺陷。`r3-test-layers.txt` 為空檔，且本改動沒有 UI/device 層。

## Seat-check 材料

正式全分支凍結檔：

`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-snapshot.patch`

逐 hunk 讀完的三份分工材料：

`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-code.patch`

`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-context.patch`

`/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone/governance/review-reports/code-repair-pilot-01/r3-archive-security.patch`

一致性核對：`r3-code.patch` 與 `r3-archive-security.patch` 都是正式 snapshot 的 byte-exact 連續片段；`r3-context.patch` 的 11 個 diff section 均 byte-exact 存在於 snapshot。歷史卷證只作一致性核對，沒有重開已處置舊發現。

程序揭露：本席沒有主動開啟其他 r3 席報告；但一次為找測試行號而執行的遞迴 `rg` 超出預定範圍，輸出曾帶出 `r3-boundary.md` 的數行命中。本席未再開該檔、未採用其內容；Finding 1 在該次誤命中前已由目前程式與唯讀 in-process 輸出獨立重現。父代理若採絕對隔離的 seat-check，應把這項程序污染一併記帳。