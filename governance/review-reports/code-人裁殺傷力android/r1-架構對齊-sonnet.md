severity: major

## 1. 分層與依賴方向:對齊

- 新碼的位置與依賴方向跟鄰居一致。
  - 殺傷力共用的格式檢查放在 `_kill_*` 區,緊接在 `_kill_old_issue` / `_kill_new_issue`(`scripts/lumos:26709-26721`)之後。`_kill_also_issue` 與 `_kill_also_apply` 照這兩支的先例,由 `cmd_guard_kill` 和人裁共用,沒有各寫一份。
  - 人裁新增的函式留在 `_situation_rule_*` 區,由 `cmd_situation_rule` 呼叫。呼叫方向是人裁呼叫 `_kill_*`,跟既有的 `_kill_esc`、`cmd_guard_kill(recipes_override=…)` 同向,沒有反向或跨層直呼。
  - 範圍解析經 `_kt_bj_segments`(`scripts/lumos:75518`)和 `_lens_range_ok`(`scripts/lumos:68929`),沒有改共用函式。
  - init 的 Android 判斷沿用 `_android_build_texts` 加 `_KT_BUILD_ANDROID`(`scripts/lumos:40757`、`39447`)。
- `_situation_rule_check` 內用 `import types` 加 `SimpleNamespace`,跟同區的 `scripts/lumos:75978` 寫法相同。

## 2. 命名與錯誤處理:大致對齊,有一處命名與位置不一致(見 a2)

- rc 語意對齊:拒絕走 `_situation_rule_say`(stderr 加 `擋下:`,回 2,`scripts/lumos:75758`)。guard kill 內壞配方判 `error`,不當成 `drifted`,跟 `_kill_new_issue` 的處理一致。
- 輸出跳脫對齊:所有印給人看的字串都過 `_kill_esc`,shell 字串用 `_sh_quote`(`scripts/lumos:468`)。
- 治理帳欄位 `imports` 登記進 `_GOV_FIELD_TYPES`,做法同 `clause_id` 等欄位。
- 命名偏離:新的 Gradle 工具函式用了通用的 `_gradle_*` 前綴和 `_SR_*` 常數,卻放在 situation-rule 區。鄰居的 Gradle 相關碼放在 Kotlin/detekt 區(`scripts/lumos:40610-40935`),用 `_GRADLE_*`、`_detekt_*` 命名。

## 3. 第二種做法:不對齊(a1 是 major,a2 是 minor)

- 路徑遮罩(`_kill_mask_paths`)和失敗摘錄(`_kill_fail_excerpt`)我沒找到鄰居有同功能的函式,不算第二種做法。
- `--diff` 的檢查重用 `_lens_range_ok`,沒有自寫範圍解析。
- 自寫 shell 字串切分與 Gradle 選項表(a1)、自寫讀建置檔(a2)這兩處都有鄰居已有同功能的函式。

## a1 自寫一套 Gradle 命令切詞與選項表,鄰居已有
severity: major
blocking: 是
引句:「_SR_GRADLE_VALUE_OPTS = frozenset(("-x", "--exclude-task", "-p", "--project-dir", "--tests"))」
file: `scripts/lumos:40610`
- 新增的 `_SR_GRADLE_VALUE_OPTS` 與 `_gradle_task_list` 做的是 detekt 那一組早就做過的事:用 `shlex.shlex(punctuation_chars=";&|")` 切詞,遇到 `;&|` 就停,跳過選項的值後取出任務名。
- 鄰居已有 `_GRADLE_VALUE_OPTS`(`scripts/lumos:40610`,含 `-b`、`-P`、`-D`、`--console`、`--warning-mode` 等)。
- 鄰居也已有 `_detekt_split_segments`(`scripts/lumos:40620`)、`_detekt_strip_prefix`(剝環境變數與 `env`/`time` 等包裝詞)、`_detekt_walk_segments` 與 `_detekt_gradle_codes`(取任務名的迴圈)。
- 新版的選項表是舊表的殘缺子集:
  - 缺 `--console plain`,所以 `plain` 會被當成任務名。
  - 缺 `-P`、`-D` 這類帶值的選項。
  - 不剝 `FOO=1 ./gradlew …` 這種前綴。
  - 兩邊對同一條 `run_cmd` 會看到不同的任務清單。
- 該重用鄰居的段拆分與選項表,只把 `--tests` 補進去或另外處理。

## a2 自寫逐資料夾讀建置檔,另列一份建置檔名常數
severity: minor
blocking: 否
引句:「_SR_BUILD_NAMES = ("build.gradle.kts", "build.gradle")」
file: `scripts/lumos:39445`
- `_gradle_build_android` 與 `_gradle_module_candidate` 自己迴圈開 `build.gradle(.kts)`,讀前 1MB 後 decode,再剝註解並比對 `_KT_BUILD_ANDROID`。建置檔名另列一份 `_SR_BUILD_NAMES`,而鄰居已有 `_KT_BUILD_FILES`(`scripts/lumos:39445`)。
- `_android_build_texts`(`scripts/lumos:40757`)已做過同一套讀檔流程:限制大小、剝註解、`_path_resolves_in_root` 檢查。
- 這裡的差別是新碼要按單一資料夾判斷,而 `_android_build_texts` 只回文字、沒有逐資料夾的介面。所以結構大致對得上,只多了一份常數和一份讀檔迴圈;判不準算 major 還是 minor,我取 minor。
- 建議把建置檔名改用 `_KT_BUILD_FILES`,或把讀單一資料夾的部分抽成共用函式。

不對齊共 2 條,其中 major 1 條
