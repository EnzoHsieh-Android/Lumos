severity: minor

整體看下來:這份 diff 沒有能被利用的洞。三類各有結論,兩條 minor 附在最後。

**① 提示注入:已看,無。**
- 新增的 linter 提示(`_linter_config_hits`、`_init_lint_hint`)印出的工具名和檔名全是常數表(`_LINTER_CONFIG_MARKERS`)裡的字串。
- package.json 的內容只被拿去解析依賴名,不會被貼進給 AI 的文字。
- react 題組、`react-idioms` skill 和前端範本是靜態文字。我用 grep 找過 curl、wget、`npx`、eval、`| sh`,沒有可執行的外來字串。

**② 讀寫與執行越界:已看,無。**
- `_worktree_text` 用 `Path.is_file()`,會跟著捷徑讀到 repo 外(例如 package.json 或 `build.gradle.kts` 是指向 repo 外檔案的捷徑)。
- 讀到的文字只進 `_pkg_dep_keys` 和 `_KT_BUILD_*` 正規式,輸出只剩 "react/vue/node" 或 "android/server" 這類判定,內容不外露。
- 管線、裝置檔這類 `is_file()` 為假的目標不會被讀。讀取量有 `head` 與 `max_bytes` 上限。
- `_ROLE_CLOCK` 預設是 `None`,從來不讀環境變數或設定,只有測試程式碼會換它。
- 這份 diff 裡沒有安裝腳本、下載網址、密鑰或信箱。我查過 `http(s)://`、`@xxx.com`、`api_key`、`sk-`,命中的只有測試用的假信箱 `t@t.t`。
- 測試檔裡的 `subprocess` 呼叫都是固定的 argv 串列,沒有 `shell=True`,也沒有外部輸入拼接。暫存目錄用 `tempfile.mkdtemp`,範圍在自己建的目錄內。
- `node-vitest` 的 `npx vitest run -t {method}` 沿用既有 `{method}` 的 shell 引號處理,和 jest、pytest 同一條路,這輪沒有新增插值面。

**③ 非刻意走過守衛:已看,有兩條 minor。**
- Kotlin 判伺服端:我沒找到把 Android 判成伺服端的路徑。
  - 伺服端只認建置檔裡的 spring boot 或 ktor 外掛宣告,Android 跡象優先。
  - 找到最近一份建置檔就停下判定,不會越過它往上層找。
  - Android 專案常見的 convention plugin 寫法會判成「判不出」,仍然照舊附 Android 題。
- `lint-waive`:`.lumos/lint-waivers.json` 在審查範圍外。這份 diff 沒改放行的比對邏輯。

**1. 測試檔判法擴大,會把名叫 `spec.*`、`test.*` 的正式檔當成測試檔**

引句:「_PITFALL_DIFF_TEST_PAT = re.compile(r"(test_|_test\.|\.spec\.|\.test\.|/tests?/|(?:^|/)__tests__/|(?:^|/)(?:test|spec)\.[^/]*$)", re.I)」

severity: minor
blocking: 否

- 誰:使用者本人或照常操作的 AI。
- 從哪裡:編輯並提交名叫 `src/auth/spec.ts`、`src/payments/test.py`、`scripts/test.sh` 這類的正式程式檔。
- 送什麼:帶 `DELETE FROM` 這類不可逆操作的改動。
- 拿到什麼:這個變數在 `scripts/lumos` 約有十處引用(不可逆提示、棧別題出題、角色鏡頭、緊張候選),這類檔會被一併略過,該問的題少問。
- 我用 python 跑過這條樣式:`src/auth/spec.ts`、`scripts/test.sh`、`src/payments/test.py` 都判為測試檔。
- 影響面窄:舊樣式的 `test_` 本來就吃得到 `contest_runner`、`attest_user`,這次新增只多了「檔名恰為 test 或 spec」和 `.test.`。

**2. 跑過證據的樣式放寬,同一行文字就能湊出「有跑過」**

引句:「"re": r"Tests\b[^\n]{0,200}?(?<![0-9])[1-9]\d*[^\S\n]+passed",」

severity: minor
blocking: 否(推論,不是已證實的繞過)

- 誰:使用者本人或照常操作的 AI。
- 從哪裡:合約測試閘跑 `npx vitest run -t {method}`。
- 送什麼:`-t` 沒篩到任何測試,但輸出另有一行以 `Tests` 開頭或帶 `Tests` 字樣、同一行 200 字內接著 `N passed`。例如詳細列表印出某個測試的標題。
- 拿到什麼:`_ran_evidence_check` 判成「跑過」,沒跑的測試被判綠。
- 新樣式不再錨在 `Tests:` 或行首,命中面比舊樣式大。
- 我沒能構造出自然發生的輸出,所以標推論。

最嚴重 severity: minor,blocking 共 0 條。
