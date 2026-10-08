severity: major

LUMOS-SPEC: docs/lumos-toolchain-knowledge/Projects/Lumos事件帳_計劃.md

（已知並依指示不報：決策 d1 的 TypeScript、d2 的「用 claude plugin 指令列安裝」本身。以下只報 d1、d2 沒蓋到的部分。）

## 1. 分層與依賴方向:大致對齊,有兩處偏離
- **對齊**:
  - 讀取指令 `lumos events` 比照唯讀指令放在 `scripts/lumos` 的 `cmd_*`,只讀檔、不造帳。對照 `cmd_handoff`:`scripts/lumos:36512`、`cmd_enforcement`:`scripts/lumos:20544`。
  - 安裝放在 `_refuse_if_probe` 之後,對照 `scripts/lumos:16871` 與 `cmd_install`:`scripts/lumos:16908`。
  - 事件檔放 repo 樹內 `governance/runtime/`、fail-open、只在成功點寫,跟 `_hookevent.py:35`(`REL`)與 `:58` 起的 `record()` 一致。
- **不對齊(偏離一)**:既有「安裝時順便裝 Codex 席位設定」不放在 `cmd_install` 本體,而是走 `_sync_global_hooks`(`scripts/lumos:18608`,內含 `_install_codex_agent`:`scripts/lumos:18712`)。`cmd_install` 與 `lumos update`(`scripts/lumos:18841`)共用這條路,所以 update 也會自癒。拆除端走 `_teardown_global_claude`(`scripts/lumos:18776`,呼叫 `_remove_codex_agent`:`scripts/lumos:18742`),不在 `cmd_uninstall`(`scripts/lumos:16969`)。計劃把外掛安裝直接塞進 `cmd_install` 開頭、移除塞進 `cmd_uninstall`,並明說 update、bootstrap 不碰外掛。見 F3。
- **不對齊(偏離二)**:`enforcement_status` 為了讓測試能隔離 HOME,所有判斷都只讀注入的 `home`(`scripts/lumos:20281`、`_codex_present(home)`:`scripts/lumos:18596`)。計劃改成在 enforcement 裡執行真的 `claude plugin list --json`,這條路徑繞過 `home` 注入。見 F2。

## 2. 命名與錯誤處理:部分不對齊
- **對齊**:
  - 狀態值只用 `active/stale/unknown`。這與 `enforcement_summary` 把 `stale` 跟 `unknown` 同族排除的處理一致(`scripts/lumos:20531`)。
  - 「近期事件先便宜判、再貴判」的順序,跟 hook 的 liveness 判法同型(`_HOOK_LIVENESS_WINDOW_DAYS = 7`,`scripts/lumos:17202`)。
- **不對齊**:
  - 失敗處理:鄰居的 `cmd_install` 在 hook 註冊寫不進去時回 2(`scripts/lumos:16959-16961`),並用 `_sync_msg` 的三態字串(`scripts/lumos:18847` 附近)。計劃寫「任一步失敗只印一行、不改回傳碼」,沒說印到 stdout 還是 stderr,也沒有狀態字串。見 F3。
  - 欄位語意:`kind` 在既有帳是結果值 `ok|timeout|error`(`_hookevent.py:37`),在新帳是事件類型。見 F1。

## 3. 第二種做法:有(F1、F2、F4)
- **事件帳格式**:既有是單檔 `hook-events.jsonl` 加上限修剪(`_hookevent.py:36`);新帳是每會談資料夾加分塊檔。
- **外部指令呼叫**:既有 `_py_which`(`scripts/lumos:115`)刻意拒絕 PATH 相對項與 cwd 內的檔,一律用絕對路徑執行。計劃寫的是裸 `shutil.which("claude")`。
- **逾時**:既有 3 秒(`_hookevent.py:102`)、10 秒(`scripts/lumos:20385` 的 `codex --version`)。計劃用 3 秒和 60 秒兩個新值,沒說明為什麼不沿用。
- **.gitignore 處理**:鄰居有兩種,`init` 寫 `governance/.gitignore` 的 `runtime/`(`scripts/lumos:18210-18224`),以及 `_note_audit_work_dir` 的自我忽略(`scripts/lumos:25975`)。計劃選第二種,理由充分。

## 4. 落點:大致合理,有一處該調
- 新開 `Systems/lumos事件帳` 管 mod 與市集檔是對的,因為這是全新語言、全新目錄。
- 既有 `hook-events` 那套(`_hookevent.py` 與它的 liveness 判法)的家是 `Systems/hook信任邊界`。
- enforcement 的 Claude 事件帳列是「hook 事件帳活著沒」的同族,計劃卻寫進 `Systems/codex-harness`。見 F6。
- `lumos-cli-lifecycle`(26 KB)、`lumos-cli-read`(38 KB)、`codex-harness`(17 KB)都不算過大,不需要另開。

### F1 第二套事件帳格式,與既有 hook 事件帳並存、欄位同名異義、無保留上限
severity: major
blocking: 是 — 同一個 `governance/runtime/` 會並存兩套 `kind` 語意不同的事件帳,而且新帳沒有保留期限或大小上限(鄰居 `_hookevent.py:36` 有 `MAX_BYTES`、`scripts/lumos:25975` 有 14 天清理);分塊檔本身有平台理由可保留,但實作前要補上兩帳關係與清理規則。(r1 重判:原報 blocking 否,與 major 矛盾,經編排者退回該席,該席維持 major 改判 blocking 是)
引句:「分段塊檔則是新做法,只借位置與 fail-open 慣例。」
對照:
- `_hookevent.py:35-37`:單檔、`MAX_BYTES` 上限修剪、`kind` 是 ok/timeout/error。
- `scripts/lumos:25975`:`_note_audit_work_dir` 帶 14 天到期清理。
- 新帳的 `kind` 是 `turn_start/tool/spawn` 等事件類型,同一個 `governance/runtime/` 底下會有兩種同名欄位、不同語意的帳。
- 計劃沒有任何保留期限或大小上限。實作時應補:到期清理,或明寫「無上限且為什麼可以」。

### F2 enforcement 與安裝用裸 `which("claude")` 加真指令呼叫,繞過既有的找指令慣例與 HOME 隔離
severity: major
blocking: 是 — enforcement 的既有測試靠注入 `home` 隔離,這條路徑會在 CI 或沒有 claude 的機器上變成不穩定的判定,而且要被每次開場的 hook 呼叫
引句:「沒有 → 才跑 `claude plugin list --json`(逾時 3 秒),有 `lumos-ledger@lumos-toolchain` 且 enabled → 已安裝但近期沒有」
對照:
- `scripts/lumos:115-135`(`_py_which` 的絕對路徑加防 cwd 內檔)。
- `scripts/lumos:18587-18600`(`_codex_home` / `_codex_present`:只看家目錄、不看 PATH,理由寫明「結果跟 HOME 隔離的測試一致」)。
- Claude 側既有判法是讀 `home/.claude/settings.json`(`scripts/lumos:20300` 起)。
- 建議改成讀 `home/.claude` 底下外掛的安裝紀錄檔;若 `claude plugin list` 是唯一可靠來源,就套 `_py_which` 並讓 `home` 可注入。
- 這一條也涵蓋 `cmd_install` 裡的 `shutil.which("claude")`(那是 d2 之外、找指令的做法)。

### F3 外掛安裝與移除沒走既有的 `_sync_global_hooks` / `_teardown_global_claude` 路徑,失敗語意也不同
severity: minor
blocking: 否 — 結構上能運作,屬於慣例偏離
引句:「`lumos update`、`bootstrap` 走的 `_sync_global_hooks` 不碰外掛(要新版就重跑 `lumos install`)。」
對照:
- `scripts/lumos:18608`(`_sync_global_hooks`)、`scripts/lumos:18712`(`_install_codex_agent`,三態回傳)。
- `scripts/lumos:18776-18811`(`_teardown_global_claude` → `_remove_codex_agent`)。
- `scripts/lumos:16955-16961`(失敗時 `cmd_install` 回 2)。
- 計劃的失敗只印一行、不改回傳碼、也沒有三態字串。
- 後果:`update` 不會升級 mod,這與既有「update 自癒」不同。

### F4 事件帳資料夾自帶 `*` 的 .gitignore,與 init 的 `runtime/` 忽略並存
severity: minor
blocking: 否 — 計劃已寫明理由(既有 `governance/.gitignore` 不補寫,calc-ios 因此提交過 hook 事件帳),且借的是既有的 `_note_audit_work_dir` 做法
引句:「第一次寫入時在事件帳資料夾放一個內容只有 `*` 的 `.gitignore`,讓它自己忽略自己。」
對照:
- `scripts/lumos:25975-25980`。
- `scripts/lumos:18210-18224`。
- 差別在這份是用 TypeScript 重寫一次那段邏輯,Python 側沒有共用函式,實作時需要一條測試釘住兩邊內容一致(計劃的 S9 只檢查寫檔路徑)。

### F5 lumos events 的錯誤輸出與使用者面慣例未寫明
severity: minor
blocking: 否 — 屬於細節缺漏
引句:「沒有事件帳時回 0,印「沒有事件帳」與可能原因(mod 沒裝、這不是 Claude 會談、repo 沒有圖譜)。」
對照:
- `scripts/lumos:36512-36525`(`cmd_handoff`:用法錯誤才回 2,訊息用「擋下:…」加「為什麼在意」再加獨立一行指令)。
- 計劃沒寫 `--session` 給了不存在編號時怎麼回。
- 計劃沒寫「可能原因」要不要用三段式。

### F6 enforcement 的 Claude 事件帳列寫進 `Systems/codex-harness`,同族的 hook liveness 住在 `Systems/hook信任邊界`
severity: minor
blocking: 否 — 兩篇都提到 enforcement,放哪篇都能找到,但新節點與 hook-events 的關係應該互相連結
引句:「enforcement 那一列進 `Systems/codex-harness`。」
對照:
- `scripts/hooks/claude/_hookevent.py` 的家是 `docs/lumos-toolchain-knowledge/Systems/hook信任邊界.md`。
- `codex-harness` 的負責範圍是 Claude 與 Codex 兩家 hook 與探針。
- 建議 Claude 事件帳那一列寫進 `hook信任邊界`(或兩篇各寫自己那半),`Systems/lumos事件帳` 與 `hook信任邊界` 互連。

不對齊共 6 條,其中 major 2 條
