severity: minor

## x1 run_cmd 檢查被 `bash -lc` 或帶引號的 `#` 一步走過
severity: minor
blocking: 否
引句:「if depth == 0 and len(body) >= 3 and body[1] == "-c":」
file: `/Users/enzo/harness/lumos-srl-android/scripts/lumos:40986`
攻擊路徑:
1. 誰:使用者本人,或照常改 `.lumos/config.json` 的 AI。
2. 從哪:`lumos situation-rule` 跑殺傷力前的 `_situation_rule_android_cmd_problem`,它呼叫 `_gradle_task_list`,再呼叫 `comments=True` 的 `_detekt_walk_segments`。
3. 送什麼:run_cmd 寫成 `bash -lc './gradlew test --tests "*{method}"'`(登入 shell 很常見),或 `./gradlew '#x' test`。
4. 拿到什麼:我在 r3 的 scripts/lumos 上實跑確認,這兩種寫法的 `_gradle_task_list` 都回空清單或 `[('', [])]`。Android 頂層 `test` 因此不會被擋,檢查在使用者沒有刻意繞的情況下被走過去。
- 第一種的原因是 `sh -c` 只認 `body[1] == "-c"`,認不得 `-lc`、`-ec`。這個判法本來就在,但人裁的任務清單現在也走它。
- 第二種的原因是 `comments=True` 切詞後分不出引號,`'#x'` 被當成註解,後面的詞全被截掉。程式的 docstring 已把這點寫成「已知限制」。
- 後果只是殺傷力真的去跑一次,得到弱證據後被拒,不會寫進計劃,也沒有程式執行或資料外洩。所以只算縱深防禦。
- 建議(任選):`-lc`、`-ec` 這類合併旗標也當 `-c` 處理;或者 run_cmd 有 gradle 字樣、任務清單卻是空的,就印一行「檢查沒看懂這條命令」。

## 附:逐類結論
- **①提示注入:已看,無。**
  - run_cmd 擋下訊息只印 `_kill_esc(t)[:60]` 的任務名、設定鍵與從 `--file` 推的模組候選。候選要通過 `_SR_MODULE_PART` fullmatch,建置檔內容不會原樣印出。
  - fail_excerpt 先遮工作樹與家目錄路徑,再逐行經 `_kill_esc`(`_kill_excerpt_show`)、最多 12 行,每行 ≤200 字、總長 ≤800 字。
  - `--diff` 的錯誤訊息一律經 `_kill_esc` 且截斷。
- **②讀寫與執行越界:已看,無。**
  - `--import` 要過 `_KILL_IMPORT_RE` 的 `re.fullmatch`(ASCII 識別字),放不進換行、分號、反引號或註解。
  - also 套用只改「整行相等且恰好出現一次」的那一行。檔頭掃描的 `\x00` 標記,在註解與字串內會被剝成空白,無法偽造「行尾乾淨」。
  - `-p` 指到平台根之外,只會唯讀走 `_android_build_texts`。那支函式有層數、檔數與位元組上限,也不跟符號連結,內容不外洩。
  - `--diff` 兩端走 `_lens_full_sha`,帶 `--end-of-options`,不會被當成 git 選項。
  - 修補沒有新增密鑰或信箱。
- **③非刻意、一步就能繞過的守衛:有 x1(minor)。**
  - 另外看了 `-p "$VAR"` 的情況。它會當成不存在的目錄,檢查靜默放行,和 x1 同一類,同樣不致命。
  - r2 修補本身的邏輯(每段合併、`:test`、`_lens_full_sha`、run_cmd 非字串回 rc 2)我沒找到新的可利用洞。

最嚴重 severity:minor,blocking 共 0 條。
