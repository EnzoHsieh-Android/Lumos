severity: minor

## x1 失敗摘錄原樣帶進給 AI 看的訊息(推論)
severity: minor
blocking: 否
引句:「return [_kill_esc(ln) for ln in (ex or "").split("\n")[:_KILL_EXCERPT_SHOW]]」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:26825`
1. 誰:照常操作 `lumos situation-rule` 的 AI。人裁被拒時,它會讀到終端的輸出。
2. 從哪裡:人裁殺傷力判成 killed_unattributed、timed_out_weak 或 abort 的那條拒絕路徑,印 `殺傷力那一次的失敗摘錄`。
3. 送什麼:Gradle 或測試輸出裡以 `e: `、`error:`、`E  `、`FAILED ` 開頭或以 ` FAILED` 結尾的行,加上 `* What went wrong:` 到下一個空行之間的行。這些文字可能來自第三方依賴的錯誤訊息,或別人提交的測試斷言訊息。
4. 拿到什麼:最多 12 行、約 800 字的外來文字進到 AI 的上下文。`_kill_esc` 只換控制字元和零寬字元,一般自然語言的指令句不會被攔。
5. 為什麼只有 minor:這個 repo 是單人自用,輸出來自使用者自己的建置。每行 ≤200 字、總長 ≤800,且有 `_kill_esc`。我沒有構造出實際可用的注入,所以標推論。

## x2 失敗摘錄寫進受版控的 kill-log,路徑遮罩只涵蓋工作樹與家目錄(推論)
severity: minor
blocking: 否
引句:「for p, tag in ((wt, "<worktree>"), (home, "~")):」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:26788`
1. 誰:照常跑 `guard kill` 或人裁的使用者或 AI。
2. 從哪裡:`cmd_guard_kill` 把 `fail_excerpt` 寫進 `docs/.kill-log.jsonl`。這個檔在 repo 的 `docs/` 底下,會被一起提交推送。
3. 送什麼:Gradle 錯誤行。這些行可能含家目錄與工作樹以外的路徑(例如 `/opt`、外接磁碟、內部 Maven 主機名),或帶憑證的倉庫 URL。
4. 拿到什麼:這些內容進了會推上遠端的帳本。
5. 為什麼只有 minor:既有的 `tail` 欄(200 字,不遮罩)已經有同樣的暴露面,`fail_excerpt` 只是多了遮罩,沒有讓情況更糟。Gradle 通常會隱藏 URL 裡的憑證,我也沒有實證會漏。

## 附:逐類結論
- **①提示注入**:已看,只有 x1。`--import` 與 `note` 只收過形狀檢查的 ASCII 字串。run_cmd 擋下訊息只印固定文字、`_kill_esc` 過的任務名、受正規式限制的模組候選與 `_sh_quote` 過的相對路徑。它沒有印 `--file` 或建置檔的內容。
- **②讀寫與執行越界**:已看,只有 x2,其餘無。
  - `--import` 每行用 `_KILL_IMPORT_RE` 做 `fullmatch`。ASCII 識別字不含換行、分號、註解、反引號或 `*`,所以寫不出 import 以外的程式。
  - `_kill_also_issue` 限定 `new` 只能在 `old` 那一整行之後多出 import 行,`also` 最多一筆,只在記憶體裡替換,並要求目標行恰好出現一次,所以改不到 import 以外的行。
  - `also` 只經 `cmd_guard_kill` 在隔離工作樹寫入,原本的 `realpath` 圍欄沒動。筆記宣告的配方帶 `also` 也不理。
  - `--diff` 兩端先用 `_lens_range_ok` 擋 `-` 開頭、三點與空白,再用 `rev-parse --end-of-options` 驗證,右端必須等於 HEAD,不會被當成 git 選項。
  - 模組路徑逐段用 `[A-Za-z0-9_.-]+` 檢查並排除 `.` 與 `..`,讀建置檔前有 `_path_resolves_in_root`。
  - 命令拼接:`{method}` 的 shell 注入(`--test 'x;cmd'` 配 `'*{method}'`)我實測成立。但 `cmd_guard_kill` 在展開前先用 `_test_name_ok` 擋,所以走不通。
  - 這次沒有新增密鑰或信箱。
- **③非刻意、一步就能繞過的守衛**:已看,無。
  - run_cmd 檢查用 shlex 切詞,多空白、換用 gradle(`_is_gradle_head`)、`&&` 前置的 `cd` 都擋得到。
  - 檢查漏掉 `bash -c "./gradlew test"` 與沒有前導冒號的 `app:test`。這是提前提示,不是真正的守衛。這兩種寫法在 Gradle 的 Android 模組上不收 `--tests`,基準會非綠,判 abort。真正的把關是「只認沒有弱證據的 killed」,沒有被走過去。
  - `--diff` 找得到主線分岔點時不生效,有印一行說明,不是靜默。

最嚴重 severity:minor。blocking 共 0 條。
