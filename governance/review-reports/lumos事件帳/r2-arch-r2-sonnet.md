severity: minor

本輪沒有第二種做法達到 major。r1 的兩條 major(帳格式與保留、`which("claude")` 與 HOME 隔離)都修掉了。剩下是命名、錯誤處理與落點上的小偏離。

## 1. 分層與依賴方向
大致對齊。
- 安裝改接 `_sync_global_hooks(src, "claude")`、移除改接 `_teardown_global_claude`,跟 Codex 席位走同一條路:`scripts/lumos:18608`、`scripts/lumos:18776`、`scripts/lumos:18712`。
- `lumos events` 放 `cmd_*` 並唯讀,對照 `cmd_handoff`:`scripts/lumos:36512`。
- enforcement 只看檔案系統,對照 `enforcement_status` 的 `home`/`root` 注入:`scripts/lumos:20281`。
- 新頂層 `mods/`、`.claude-plugin/` 只屬來源 repo,沒有跨層直呼。
- 有一處:`lumos events` 底下掛了會刪檔的 `--prune`,見 F3。

## 2. 命名與錯誤處理
大致對齊。
- `ev` 取代 `kind`,避開 `_hookevent.py:37` 的同名異義。
- 三態狀態值只用 `active/stale/unknown`,對照 `scripts/lumos:17261`。
- 失敗不改 install 回傳碼,保留 `cmd_install` 對 hook 註冊失敗回 2 的規則:`scripts/lumos:16955-16961`。
- 外掛步驟自己在函式內印訊息有先例:`_install_codex_agent` 內 `print(..., file=sys.stderr)`,`scripts/lumos:18717`。
- 偏離:新增一套狀態字,見 F2。

## 3. 第二種做法
- 狀態回報通道:新增 ok/skipped/failed,見 F2。
- git 呼叫與逾時:見 F1。
- 找指令:改用 `_py_which`,已對齊。
- 開關命名:`LUMOS_SKIP_CLAUDE_PLUGIN` 沿用 `LUMOS_SKIP_*` 前綴,測試執行器清環境變數也有 `CODEX_HOME` 的先例(`scripts/test_lumos.py:463`)。語意的差別見 F5。
- 刪檔做法:見 F3。
- 主 checkout 解法:repo 內沒有任何 `git-common-dir` 或 `common_dir` 用法,所以不是重複實作。但跟鄰居位置規則不同,見 F6。

## 4. 落點
- 新開 `Systems/lumos事件帳` 管 mod 與市集檔,合理。
- 安裝與移除進 `lumos-cli-lifecycle`,對得上它的責任(`lumos-cli-lifecycle.md:8`)。
- `lumos events` 進 `lumos-cli-read` 合理,但 `--prune` 會刪檔,見 F3。
- enforcement 那一列進 `hook信任邊界` 的理由站不住,見 F4。
- 登記處(`HELP_WHEN`、指令說明字典、argparse、`INDEX.md`)寫得齊:`HELP_WHEN` 在 `scripts/lumos:36618`。

### F1 `_events_root` 的 git 呼叫沒說用既有包裝,逾時寫了第三種值
severity: minor
blocking: 否 — 結構正確,只是同一件事(對 repo 問 git)repo 內已有包裝卻另寫一份逾時
引句:「所以在 worktree 裡跑」
file: `scripts/lumos:33068`
- 鄰居:`_lens_git`(`scripts/lumos:33068`,固定 20 秒、吞 OSError 與逾時、回 None)和 `_testmap_git`(`scripts/lumos:30546`,可傳 timeout)。
- 鄰居:`_hookevent.py:101-102` 另用 3 秒。
- 計劃要的是裸 `git -C <root> rev-parse` 加 3 秒,沒說要重用哪支。
- 建議:Python 側的 `_events_root` 用 `_testmap_git(root, [...], timeout=3)`,或註明為何不用。

### F2 外掛步驟新增 ok/skipped/failed,跟既有三態字串並行且不走 `_sync_msg`
severity: minor
blocking: 否 — 計劃有理由不併進回傳字串(`cmd_install` 與 `_sync_global_claude` 會誤判),這點成立;偏的是詞彙與輸出方式
引句:「成功與略過印到標準輸出,失敗印到標準錯誤。」
file: `scripts/lumos:18758`
- 既有「本機沒這家」叫 `absent`(`scripts/lumos:18770`),新的叫 `skipped`。
- 既有狀態集中由 `_sync_msg` 轉成給人看的一行(`_sync_msg`,`scripts/lumos:18758`),新的在函式裡直接印。
- 建議:沿用 `absent` 一詞,或在 `_sync_msg` 旁補一個 plugin 專用的轉譯函式,讓輸出格式與兩個 ✓ / ⚠ 前綴一致。

### F3 `--prune` 掛在唯讀指令底下,且跟鄰居的自動到期清理不同做法
severity: minor
blocking: 否 — 計劃已誠實列為會刪檔、不跟符號連結,並有 REVISIT:2026-11-05,不是靜默第二套
引句:「保留期限靠人或排程跑」
file: `scripts/lumos:25975`
- 鄰居清理:`_note_audit_work_dir` 在每次使用時順手刪超過 14 天的檔,靜默、失敗吞掉(`scripts/lumos:25975-25987`)。
- 鄰居刪資料夾:先判符號連結再 `unlink`,否則才 `rmtree`(`scripts/lumos:16993-17002`)。
- repo 內沒有既有的獨立 `--prune` 指令(grep 只找到 `merge-claude-settings` 的 `--prune-only`)。
- 計劃把破壞性旗標放進讀取類節點 `Systems/lumos-cli-read` 的 `lumos events`,而該節點的指令都是唯讀。
- 建議:一併寫明為何不照 `_note_audit_work_dir` 在寫入端自動清,或把 `--prune` 的說明記到有寫入語意的家。

### F4 把 enforcement 列放進 `hook信任邊界`,理由「既有 hook 事件帳活著沒的判法住在那篇」查不到
severity: minor
blocking: 否 — 兩篇都能找到,但計劃寫的前提圖譜裡驗不出來(⚠ 判不準哪篇才是家)
引句:「enforcement 那一列進」
file: `docs/lumos-toolchain-knowledge/Systems/hook信任邊界.md:28`
- `hook-events` 在 `Systems/` 底下沒有任何筆記提到,只出現在 `Projects/enforcement可觀測性_計劃.md`、新計劃與 `Verification/` 實測裡。
- `hook信任邊界` 只有一處 enforcement,是連到那篇計劃的連結。
- `codex-harness` 的 DEP 行直接寫了「enforcement Codex 列」(`codex-harness.md:37`),是唯一在 Systems 層明寫 enforcement 列的家。
- 我判不準哪篇才是 `enforcement_status` 的家。計劃應先機械查證(`about_code` 與正文提到的函式),不要憑「同族」推。

### F5 偵測 `claude` 用 PATH,鄰居 Codex 側用「家目錄在不在」
severity: minor
blocking: 否 — 計劃有自己的隔離辦法(開關加清 `CLAUDE_CONFIG_DIR`),只是跟 `_codex_present` 路線不同(⚠)
引句:「測試執行器在建立拋棄式家目錄的同一處設定它」
file: `scripts/lumos:18596`
- Codex 側:`_codex_present()` 看 `~/.codex` 是否存在,回 `absent`,不依賴 PATH。
- 新做法:`_py_which("claude")` 找得到才動。
- 既有 `LUMOS_SKIP_*` 多半是單次繞過某道閘並留帳,例如 `LUMOS_SKIP_NOTE_SHAPE`(`scripts/lumos:25344`)。這顆是測試隔離用的整段略過,語意不同。
- 不是錯,只是第二種判斷「這台有沒有這家 CLI」的方式。建議在計劃寫一行為什麼不用家目錄判定。

### F6 事件帳寫主 checkout,hook 事件帳寫會談所在的 worktree 頂層
severity: minor
blocking: 否 — 計劃有理由(worktree 會被刪),`_events_root` 也讓讀取端一致;只是兩本帳在 worktree 會分家
引句:「所以在 worktree 裡跑」
file: `scripts/hooks/claude/_hookevent.py:101`
- 鄰居 `_hookevent._root_from_cwd` 用 `git rev-parse --show-toplevel`,在 worktree 裡寫進 worktree 自己的 `governance/runtime/hook-events.jsonl`。
- 新帳在同一個 worktree 會寫進主 checkout。
- 同一個 `governance/runtime/` 概念下,兩本帳在 worktree 會位置不同。
- 計劃的 Systems 節點應把這個差別寫明。

## 前輪修復驗收(r1 本鏡頭)
- F1(第二套事件帳格式、同名異義、無保留):修一半。`ev` 取代 `kind` 修好;保留只做手動 `--prune`,沒有鄰居式自動到期,見本輪 F3。
- F2(裸 `which`、繞過 HOME 隔離):已修好。改用 `_py_which`,enforcement 不呼叫外部指令、只看檔案系統。
- F3(安裝移除沒走 `_sync_global_hooks`/`_teardown_global_claude`):已修好,但新增一套並行狀態字,見本輪 F2。
- F4(自帶 `*` 的 `.gitignore`):已修好。S9 釘兩邊內容一致。
- F5(`lumos events` 錯誤輸出慣例):已修好。三段式、沒帳回 0、`--session` 不存在回 2 都寫明。
- F6(enforcement 列落點):修出新問題。改進 `hook信任邊界`,但該篇是否為 hook 事件帳判法的家查不到,見本輪 F4。

不對齊共 6 條,其中 major 0 條
