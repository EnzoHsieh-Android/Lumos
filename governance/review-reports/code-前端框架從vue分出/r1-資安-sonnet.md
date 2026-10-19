severity: clean

我看完整份 patch 的程式部分(`scripts/lumos`、`scripts/test_lumos.py`),也讀了新 skill 和範本文件。三類都沒找到能利用的洞,也沒有四件攻擊路徑填得出來的發現。

**①提示注入:已看,無**
- `react-idioms` 的 SKILL.md 和 `target-arch-frontend-template.md` 都是 repo 內寫死的靜態文字。裡面沒有「忽略前述指令」「執行某指令」之類的指令文字。
- 範本裡 `<採用日>`、`<回頭日>` 只是要使用者自己替換的佔位符,不會從外部讀進來。
- 消費專案的 `package.json` 只經過 `_pkg_dep_keys` 取出依賴鍵集合,拿去比對固定標記,再回傳 "react"、"vue" 或 "node"。檔案內容不會進給 AI 的派工詞。
- 消費專案的 `build.gradle(.kts)` 和 `pom.xml` 只用三條固定 regex 去比對,結果是 android 或 server 的旗標。檔案內容沒有被印出或拼進文字。
- doctor 的提醒只印固定的 eslint 設定檔名,範本是 `json.dumps` 一個固定指令字串。專案內容不流進來。

**②讀寫與執行越界:已看,無**
- `_kt_build_candidates` 的路徑來自 diff 的 repo 相對路徑,往上走到 repo 根為止,走不出 repo。git 路徑不含 `..`。
- 工作樹讀取用 `is_file()`,會跟著 repo 內的捷徑讀到 repo 外。但讀到的內容只丟給 regex 判旗標,沒有輸出或外洩,所以沒有可利用的路徑。
- 派工路徑用 `ref:rel` 形式交給 git 讀,不是自己拼 shell。
- init 給的 vitest 指令是固定字串 `npx vitest run -t {method}`,沒有拼入專案內容。`{method}` 在 `scripts/lumos` 的 `--method` 檢查(只准字母、數字、底線,不能數字開頭)已驗過。
- eslint 範本只在舊式設定時加固定前綴 `ESLINT_USE_FLAT_CONFIG=false`。
- 新程式沒有 `shell=True`、`eval`、下載網址或環境變數覆蓋來源。
- diff 內沒有密鑰,只有測試用假信箱 `t@t.t`。

**③非刻意繞過的守衛:已看,無**
- 測試檔判法加了 `\.test\.` 和 `(?:^|/)__tests__/`。要讓產品檔被誤排除,檔名得剛好帶 `.test.` 或放在 `__tests__/` 底下,這兩種本來就是測試慣例。找不到平常操作會把產品檔放進去的情境,所以不成立。
- vitest 跑過證據改成 `Tests:?\s+[^\n]{0,200}?\b[1-9]\d*\s+passed`,限制在單行內。
  - 「Tests  34 skipped (34)」沒有 `[1-9]` 開頭的 passed,仍判沒跑。
  - 「Test Files  1 passed」不符合 `Tests`,不會誤放行。
  - 測試自己 `console.log` 出同樣字樣來騙過,屬刻意偽造,範圍外。
- Kotlin 判伺服端要同時滿足兩點:
  - 全部非測試 `.kt` 檔都判成 server。
  - 離該檔最近的那層建置檔含 Spring Boot 或 Ktor 的標記,且不含 Android 標記。
  - 最近的建置檔存在但不符合就停在那層,不會再往上找,所以 Android 模組不會被根目錄的伺服端 pom 蓋過。
  - 判不出、讀不到、超過 300 支都保持照舊附 Android 題。這個方向安全。
  - 在 Android 專案裡要讓 Android 題被拿掉,得讓最近的建置檔裡出現 `ktor-server` 或 `io.ktor.plugin` 之類字串,又沒有 `com.android.` 等標記。這需要有人刻意構造,我找不到平常操作會走到的情境。

最嚴重 severity:clean,blocking 共 0 條。
