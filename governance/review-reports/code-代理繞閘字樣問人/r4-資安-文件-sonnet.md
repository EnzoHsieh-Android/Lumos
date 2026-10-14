severity: clean

我讀完了測試文件組的七個檔案,沒有可利用的洞。

## 逐類判斷

**1. 執行邊界:已看,無**
- **暫存目錄與子程序**:新測試的暫存目錄都用 `mkdtemp` 建,收尾用 `rmtree(..., ignore_errors=True)` 且只刪自己建的路徑。
  - 子程序全用 list 形式的 `_sp.run([...])`,沒有 `shell=True`,也沒有字串拼接成指令。
  - `git init`、`worktree add`、`commit` 的路徑都來自測試自建的 `base`,不吃外部輸入。
- **符號連結**:`os.symlink(real/"sub" → tmp_root/"lnk")` 和 `os.symlink(R → tmp_root/"realln")` 的連結檔都建在自己的暫存根底下,目標是自建的 repo。沒有寫到暫存目錄外,也沒有對連結目標做刪除。
- **假 git**:`fake/git`(`sleep 30`)放在專屬的 `mkdtemp` 目錄。`PATH` 只塞進 `env=dict(...)` 傳給那一個子程序,不動全域環境,收尾整個目錄刪掉。
  - 這個 `sleep` 可能在逾時殺掉後變孤兒,但只是資源耗盡,不在範圍內,不報。
- **權限還原**:`_os.chmod(rt, 0o555)` 被 `try/finally` 包住,必定還原成 `0o755`,測試中途失敗也不會留下唯讀目錄。`chmod(f, 0o644)` 用在自建檔。
- **HOME 隔離**:`t_bypass_ask_registered` 把 `HOME` 與 `USERPROFILE` 指到暫存家目錄再跑 `merge-claude-settings.py`,所以新的 Bash matcher 註冊不會寫進使用者真正的 `~/.claude/settings.json`。Codex 目標另帶 `CODEX_HOME` 指到暫存目錄。
- **`merge-claude-settings.py`**:新註冊只有 `matcher: Bash`、固定 `_hook_cmd("bypass-ask-hook.py")`、timeout 5,命令字串沒有外部可控的輸入。`_codex_entries` 對 Codex 用 `continue` 跳過,等於不註冊(測試也斷言 `hooks.json` 內不含 `bypass-ask-hook.py`)。
- **`scripts/lumos` 的名單**:`_VENDORED_TREE_FILES`、`_GLOBAL_CLAUDE_HOOKS`、`ANCHOR_FILES`、`enforcement_status` 各加一行字面常數,沒有路徑拼接。
  - `ANCHOR_FILES` 把新掛鉤納入錨點,是收緊而不是放寬。
  - 安裝副本若被改,錨點只盯來源樹,和其他既有掛鉤相同,不是這次新增的缺口。
- **存活事件修剪測試**:`mkstemp` 加 `copymode` 的行為由測試鎖住(權限維持 0644、殘留暫存檔清理、換入失敗不留殘檔)。
  - 那些測試對 `m.os.replace` 的 mock 只作用在 `with` 範圍內。
  - 殘檔清理只清自己目錄下 `*.trim` 且超過一分鐘的檔。這是被測程式的行為,屬程式組範圍。

**2. 文件裡給人照抄的回退步驟:已看,無**
- 計劃的〈回退〉要人拿掉 matcher、把檔名搬到 `_RETIRED_STUB_CLAUDE_HOOKS`、拿掉 `enforcement_status` 那一列、`lumos anchor approve` 重簽、重跑安裝。
- 沒有 `rm -rf`、`sudo`、`curl | sh` 這類指令,都是改檔和重跑自家安裝。文件還明說「只拿掉 matcher 不夠」,不會誤導人留下已註冊但行為不明的狀態。
- S6 手冊寫「使用者要跳過時自己在提示列用驚嘆號前綴執行」,這是使用者自己的 shell,屬設計決定,文件已明列。

**3. 授權範圍:已看,無**
- 掛鉤只回 `ask`,不回 `allow`,也不改指令。
- Codex 刻意不註冊。
- 失敗一律放行,這是明寫的威脅模型:問人層,不是安全邊界。
- `_codex_entries` 的 `continue` 只針對 `PreToolUse` 加 matcher `Bash` 這一條,不影響其他事件。

## 固定席節點

- **`Issues/code-loop守衛main-direct盲區`**:不影響。這次沒有碰 code-loop 守衛的 main-direct 邏輯,只動 `test_lumos.py`,新增的是新測試。
- **`lumos-cli-read` 的 INVARIANT(search 預設排除 superseded)**:不影響。diff 沒有動 search 路徑。
- **`lumos-cli-lifecycle` 的 INVARIANT(re-inject 只覆蓋 sentinel 之間)**:不影響。diff 只在筆記裡新增一行 WHY,沒有動 re-inject 程式碼。
- **`design-loop` 的 INVARIANT(處置閘第五步)**:不影響。這次沒有改處置閘邏輯。
- **`測試假綠形態` 的 INVARIANT(還原翻紅釘要配前置斷言)**:不影響資安面。
- **`guard-kill` 的 INVARIANT(rc 優先序、`--json` 純度)**:不影響,沒有碰 guard kill。
- **`pitfalls-code-loop` 和 `reversibility-governance-ledger`(`★RISK★`)**:不影響。
- **只列名的節點**:沒有看出與資安面相關的牽連。

## 附帶觀察

以下兩點沒有可描述的攻擊路徑,不計入 finding。
- 新掛鉤檔在安裝後放在 `~/.claude/hooks/`,錨點只驗來源樹。這和既有的六支掛鉤相同,屬原有的信任邊界,不是這次新增的缺口。
- 不少測試會真的呼叫 `git init`、`git commit`。它們依賴整輪測試前的 `_isolate_environment` 隔離使用者全域 git 設定。

最嚴重等級 clean,blocking 共 0 條。
