severity: minor

## s1 ast-grep 在推送閘的 PATH 上找不到時,選擇點那一道整道放行
severity: minor
blocking: 否 — 屬縱深防禦,設計上本來就「算不出來就放行」,但使用者照常操作也會踩到,只靠一行提醒。

- **誰**:使用者本人,或照常操作的 AI。
- **從哪**:用 GUI git 用戶端(Xcode、Tower 這類)或 PATH 精簡的環境執行 `git push`,pre-push 掛鉤跑到 `spec-gate --push-check`。這些環境的 PATH 通常沒有 `/opt/homebrew/bin`。
- **送什麼**:一份改到 Kotlin 正式碼、有存活選擇點的推送。
- **拿到什麼**:`_choice_push_scan` 收到 `_ChoiceNoTool`,回 `"unverified"` 並只印一行提醒。擋下清單是空的,選擇點守衛被意外走過。GUI 用戶端常不顯示掛鉤輸出,提醒可能沒人看到。

引句:「return "unverified", _choice_push_unverified(rr, at_sha, f"ast-grep 不在({e})", hint=f"裝 ast-grep 後再推:{_CHOICE_INSTALL}")」

file: `scripts/lumos`(snapshot 的 `_choice_push_scan`)

我沒有實際跑過 GUI 用戶端,所以這條走到的路徑是讀程式推出來的。

## s2 殘留的 `LUMOS_CHOICE_SINCE` 會讓推送前選擇點整圈關掉
severity: minor
blocking: 否 — 關掉時會印一行「被環境變數關掉」,不是靜默,而且這個變數是測試用的覆寫。

- **誰**:使用者本人。
- **從哪**:shell 裡殘留 `export LUMOS_CHOICE_SINCE=9999-12-31`,例如手動重現測試總檔的預設值後沒清掉。
- **送什麼**:之後任何一次 `git push`。
- **拿到什麼**:`_choice_round` 一開頭 `since > today` 就 `return []`,整道選擇點閘放行。

引句:「if os.environ.get("LUMOS_CHOICE_SINCE", "").strip() == since and _choice_push_has_kotlin(rr):」

file: `scripts/lumos`(snapshot 的 `_choice_push_round`)

沒找到哪個正常流程會自己把這個變數留在 shell 裡。測試總檔裡是 `os.environ.setdefault`,只影響測試自己的程序。

## 已看,無
- **①提示注入**:`choice-points`、`choice-kill`、`situation-rule --point` 印出的檔名、壞法原文、宣告行、原因摘錄都有包 `_kill_esc`。`--consent` 的原話在 `situation-rule` 路徑裡標成資料,這是既有設計。
  - 備註:`choice-kill` 印的建議指令是 `lumos lint-waive choice:{_kill_esc(file)}:{line}`,檔名沒有 shell 引號。檔名帶空白時複製貼上會因參數被拆開而失敗,不是守衛被繞過,也沒有越界寫入,所以不報。
- **②讀寫與執行越界**:
  - ast-grep 掃描用 `_lint_wt_resolve_tool` 解成 PATH 上的絕對路徑,設定檔經 `_lint_wt_cfg_inside` 限定在 `configs/ast-grep/` 底下。參數是清單、不開 shell,也不帶 `-U` 或 `-i`。
  - 暫存檔名用序號加 `.kt`,不用 repo 路徑,收尾刪除。
  - `cmd_guard_kill` 套壞法前有 realpath 圍欄。我讀了程式,圍欄會擋掉指向 worktree 外的符號連結,沒有另跑重現。
  - `.kt` 內容從 git blob 讀,不跟隨工作目錄捷徑。
  - 規則 yml 沒有 `fix:` 或 `transform:`。
  - `check.py` 新增的 `shutil.which("ast-grep")` 跟同檔既有寫法一致,不是新缺口。
  - pre-push 掛鉤新加的探測只用 `grep -q` 讀 `$GRAPHCTL` 檔案,不執行它。
  - 新增內容沒有密鑰、信箱或可用憑證。
- **③非刻意繞過**:除 s1、s2 外沒有其他。放行檔和治理帳讀不出來時是擋下,不是放行,所以讀失敗不會被當成全放行。

## 圖譜鏡頭固定席
這次沒附固定席節點(鏡頭計算超時),沒有可逐條判的項目。

最嚴重:minor;blocking 共 0 條
