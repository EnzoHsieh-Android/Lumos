severity: major

## F1 五支既有程式檔仍沒有家

severity: major  
blocking: 是 — 不改，實作者把程式變更與圖譜說明放進同一提交時，既有「每支檔有家」守衛會擋下，或只能留下沒有歸屬的程式改動。  
引句:「在範圍內:`scripts/lumos` 與 `scripts/hooks/**`(git 掛鉤會被複製進消費專案)、Claude/Codex 掛鉤註冊」  
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:29`, `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:92`

1. `install.sh`、`get.ps1`、`scripts/install-hooks.sh`、`scripts/install-graph-toolchain.sh`、`scripts/hooks/post-commit` 都在實作範圍內，但沒有任何 Systems 節點以 `about_code` 收養；`lumos impact --file <檔> --json` 的 `homes` 均為空。
2. spec 第 10 點只替「新的共用檔」開系統節點，沒有替上述五支既有檔補家。固定席明定「改到之前就沒家的舊檔，有寫說明就擋」，因此 `lands_in` 列出 `Systems/每支檔有家` 並不能代替逐檔歸屬。
3. 實作前必須先把五支檔分配到適當 Systems 節點，再將行為說明寫回各自的家。

## F2 新 resolver 漏進錨點信任清單

severity: major  
blocking: 是 — 不改，新增檔會讓既有錨點覆蓋測試與全套 CI 直接翻紅；若繞過測試，三支掛鉤的直譯器選擇又成為未受錨點監看的執行入口。  
引句:「新共用檔要登記進工具自裝檔的精確名單」  
file: `scripts/test_lumos.py:15937`, `scripts/lumos:18573`

1. 現有測試要求 `git ls-files scripts/hooks` 的全部掛鉤檔與 `ANCHOR_FILES` 完全相等；spec 只要求把新共用檔加入 vendored 精確名單，沒有要求加入 `ANCHOR_FILES` 與 `governance/anchor-baseline.json`。
2. 新檔位於 `scripts/hooks/`，且會在 `anchor verify`、`code-loop check`、bound tests 之前被 source；它能改掉 `PY`、候選順序或失敗語意，屬於掛鉤實際執行鏈的一部分。
3. 依 spec 字面只更新 vendored 名單後，`t_anchor_covers_every_hook` 類檢查會列出新檔為「沒被盯著」；必須同步更新錨點清單、baseline 及其覆蓋測試。

## F3 外層啟動器無法進入宣稱的 resolver

severity: major  
blocking: 是 — 不改，機器明明已有合格直譯器，安裝器或全域命令仍會在 resolver 執行前報找不到 Python。  
引句:「Windows 的 `lumos.cmd` 包裝照舊寫指令名不寫死路徑,版本同樣交給 lumos 開頭」  
file: `install.sh:5`, `get.ps1:35`, `scripts/lumos:16394`

1. POSIX 的 `install.sh`、`get.sh` 與兩支薄殼只直接執行 `python3`；全域 Unix `lumos` 又以 `#!/usr/bin/env python3` 啟動。環境只有 `python3.14` 或只有 `$LUMOS_PYTHON` 指定路徑時，殼層先失敗，`scripts/lumos` 的候選清單永遠跑不到。
2. Windows `get.ps1` 只試 `python3`、`python`；`lumos.cmd` 同樣只從這兩個名稱選一個。標準的 launcher-only 環境只有 `py -3.14` 時，安裝器先回「沒有 Python」，即使 spec 的 Python resolver 列了 `py -3.14` 也無法進入。
3. Git for Windows 的掛鉤走 shell 共用檔；spec 只把 `py -3.14` 說成 Python 實作的 Windows 額外候選，因此 py-only 機器上的 pre-commit/pre-push 仍會誤擋。
4. 啟動殼層必須能使用 `$LUMOS_PYTHON`、版本化命令及 Windows launcher，或另設一個先於 Python 主程式的完整 bootstrap resolver。

## F4 POSIX 註冊命令沒有引用 `sys.executable`

severity: major  
blocking: 是 — 不改，直譯器絕對路徑含空白時，Claude 與 Codex 的全部 Python hooks 都無法啟動。  
引句:「當註冊 Claude/Codex 掛鉤,工具應寫入目前執行的那一支直譯器的路徑」  
file: `scripts/merge-claude-settings.py:107`, `scripts/merge-claude-settings.py:118`

1. spec 要把 `_PY` 改成 `sys.executable`，但 `_hook_cmd` 在非 Windows 的 Claude 與 Codex 分支都把 `_PY` 直接串入 shell 命令，沒有引用或 shell escaping。
2. 以 `/opt/Python 3.14/bin/python3.14` 執行合併器時，註冊值會成為 `/opt/Python 3.14/bin/python3.14 "...hook.py"`；shell 將 `/opt/Python` 當成命令，六支 hooks 全部失效。
3. Windows 分支已對 Python 路徑加雙引號，POSIX 分支也必須以可靠的 shell quoting 產生命令；測試要用含空白的 `sys.executable` 路徑實際解析命令，而不只比對字串包含路徑。

## F5 `uv python find` 會把探測變成自動安裝

severity: major  
blocking: 是 — 不改，找不到 3.14 時掛鉤不會依裁定擋下，而會連網下載並修改使用者機器。  
引句:「有 uv 時再試 `uv python find '>=3.14'`」  
file: `docs/lumos-toolchain-knowledge/Projects/最低Python版本改3.14_計劃.md:41`

1. 本機 `uv 0.11.19` 的 `uv python find --help` 明列 `--no-python-downloads — Disable automatic downloads of Python`；spec 的命令沒有這個旗標。
2. 在 uv 已安裝、但沒有任何 ≥3.14 直譯器的環境，resolver 會要求 uv 自動下載 Python，而不是列完候選、印安裝方式並讓 pre-commit/pre-push 擋下。
3. 這同時引入未列出的網路外呼、共享 uv cache 寫入、併發下載及不受掛鉤預算限制的等待；候選探測必須加 `--no-python-downloads`，並測試「uv 存在但沒有相符安裝」仍走找不到分支。

## F6 正向部署步驟漏掉兩家已安裝設定

severity: major  
blocking: 是 — 不改，repo 裡的註冊程式改對後，現有 `~/.claude/settings.json` 與 `~/.codex/hooks.json` 仍會繼續呼叫舊直譯器。  
引句:「回退程式碼之後,設定檔裡寫進去的直譯器路徑不會自己變回來,要重跑一次安裝」  
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:131`, `scripts/lumos:17487`

1. spec 只在回退節要求重跑安裝，正向落地與驗收沒有相同操作。
2. 來源 repo 中執行 `lumos update` 只走 reinject-only，不會執行 `_sync_global_hooks`；修改 `merge-claude-settings.py` 不會自行重寫家目錄下兩家的設定。
3. 固定席已明定：改 hook 的計劃必須把「跑一次安裝指令，並對 Claude/Codex 兩個部署位置各比一次 sha256」寫入驗收。本 spec 沒有這一步，故本機實際 hooks 仍保持舊狀態。

## F7 CHANGELOG 的裁定在兩節互相衝突

severity: minor  
blocking: 否 — 一處要求不寫、另一處又把寫 CHANGELOG 當成防法，只造成實作範圍與驗收文字互相打架，不直接決定執行期行為。  
引句:「防法:CHANGELOG 寫升級說明,擋下訊息附三種平台的安裝指令」  
file: `docs/lumos-toolchain-knowledge/Projects/最低Python版本改3.14_計劃.md:47`, `docs/lumos-toolchain-knowledge/Projects/最低Python版本改3.14_計劃.md:72`

1. 做法第 7 點明定「不寫 CHANGELOG」，實務隱患的對外送出段卻明定「CHANGELOG 寫升級說明」。
2. intake 宣稱前掃已把 CHANGELOG 改成 README，但只修了做法節，實務隱患仍保留舊處置。
3. 兩節須統一成 README 承接本次升級注意、下次發版再移入 CHANGELOG。

### 逐節覆核

1. 開頭欄位、白話、依據、暫停事項、RETIRE-IF：已讀；除 F5 的 uv 行為外，無 finding。
2. 範圍：F1；其餘列出的檔案與現況均能在 repo 找到。
3. 做法第 1–10 點：F1–F6。
4. 條款 [S1]–[S7]：七個標號都存在；第 2 點、3 點與 [S7] 的交叉引用目標均存在。F3–F5 使 [S1]–[S5] 在指定環境下無法成立。
5. 回退：F6；其餘回退沒有資料格式變更，已讀、無 finding。
6. 實務隱患：F7；守衛誤擋由 F3/F4 覆蓋，對外連網與效能由 F5 覆蓋，併發風險也收斂在 uv 下載這一條；金流無，因改動不接觸付款或計費。
7. 誠實界線：已讀；[S7] 與日期型 REVISIT 均存在，無額外 finding。

### 固定席逐條判

1. `Systems/lumos-cli-lifecycle`：會受 F1、F3、F6 影響；其 sentinel 外內容 byte-equal 的正式合約不受本設計影響。
2. `Systems/bound-tests-gate`：會受 F2、F3 影響；resolver 在 pre-push 的 `code-loop check` 前失效或未被錨定時，固定席測試真跑流程到不了。
3. `Systems/每支檔有家`：會被 F1 直接違反，因五支修改檔仍無 `about_code` 歸屬。
4. `Systems/codex-harness`：會受 F4、F6 影響；註冊命令在含空白路徑失效，且來源 repo 改完不會自動部署到 Codex/Claude 設定。
5. `Systems/測試假綠形態`：已讀，無 finding；本設計沒有移除既有還原翻紅釘，F2 反而會由現有覆蓋測試直接翻紅。

最嚴重等級 major，blocking 共 6 條。