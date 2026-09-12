severity: clean

判準摘要:只找「引入專案原本沒有的第二種做法」或「跨層繞過既有單一真相源」,風格偏好不列。逐項核對 java-junit profile、JAVA_TEST_RE、`_STACK_QUESTION_SPECS["java"]`、`_init_config_skeleton` 改動、新增測試寫法共五處,並反查對照組,未發現符合判準的問題。

核對紀錄(非發現,供覆核):

1. `java-junit` test profile(file: `scripts/lumos:3513`,新增)結構欄位(exts/method_re/scaffold_ext/dir_mode/rglob_under/attr_hint/fail_hint/dirs)與既有 `kotlin-junit`(對照:`scripts/lumos:3504`)逐項相同,`dirs` 三組值也是逐字複製 kotlin-junit 的 `(["test"], [])` / `(["androidTest", "test"], [])`,沒有另立一套目錄慣例。

2. `JAVA_TEST_RE`(file: `scripts/lumos:3369`)與既有 `KOTLIN_TEST_RE`(對照:`scripts/lumos:3364`)同屬「註解 → 方法名」同一套 method_re 機制,只是中段 `.*?` 取代 `[^{]*?`——patch 註解已交代原因(Java 參數化註解會帶 `{}`,Kotlin 那條在此斷裂),屬於同一機制內對不同語言語法的必要調整,不是另開一套測試發現機制。

3. `_STACK_QUESTION_SPECS["java"]`(file: `scripts/lumos:16688` 起)七題的欄位形狀(id/q/when/選用 when_raw)與既有 kt/cs/swift/node/py 組(對照:`scripts/lumos:16622` 起、`scripts/lumos:16653` 起的 py 段)一致;`when_raw` 只認雙引號字串是因為 Java 字面字串只用雙引號(對照 node 版因 JS 允許單引號而用 `['"]`,是同一機制對不同語言語法的正確變體,不是分裂出第二套)。java-data / java-android 兩題平台特有,靠各自 `when` 觸發字決定要不要出現——這正是這張表既有的設計(每題本來就各自獨立 when),不是新機制。

4. `_init_config_skeleton` 的 `ranked[:3]` → `ranked`(file: `scripts/lumos:14306`)是同一段迴圈拿掉人為截斷,函式其餘分支(單語言分支、認不出分支)寫法未變、也未被這次改動觸及,不構成另一套處理路徑。

5. 新增測試 `t_java_profile_discovery` / `t_java_stack_wiring`(file: `scripts/test_lumos.py:20411` 起)在造臨時 repo、載入 CLI(`_load_lumos()` / `_load_lumos_inproc()`)、`_disp_run` 取用、docstring 內「翻紅釘」寫法,都與既有 `t_swift_profile_discovery` / `t_python_stack_wiring`(對照:`scripts/test_lumos.py:3320`、同批新增的 py 版)同一套寫法,`_disp_run` 是既有 helper(定義於 `scripts/test_lumos.py:34402`,非本次新增)。

單一真相源檢查:`SYMBOL_PROFILES["kotlin"]["code_exts"]`(file: `scripts/lumos:3423`)在本次改動之前就已經把 `.java` 收進 kotlin 符號家族(未被此 diff 觸及),java-junit 的符號 profile 借用同一張既有表(測試 `g["symbol"] == "kotlin"` 已驗證),沒有另建一份 Java 專屬符號表;`_ARCH_IDIOM_SKILL`(file: `scripts/lumos:19246`)新增的 `"java": "java-idioms"` 仍走同一個字典查找,`_idiom_skill_for` 本身未被改成另一套判斷路徑;`_stack_key_for_file`(`scripts/lumos:16748`)完全未被此 diff 觸及,`.java` 直接落入既有的「副檔名即棧鍵」通用分支,沒有為 Java 加特判分支。

最嚴重 severity: clean、blocking 0 條。
