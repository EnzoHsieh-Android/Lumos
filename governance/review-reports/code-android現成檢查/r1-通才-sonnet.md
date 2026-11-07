severity: major

審查範圍:讀完整份 diff,並用 `_android_ci_has_lint_task` 與 `_android_plugin_paths` 實跑了上述最小重現。其他八個角度各自找過一輪,下面是去重後的結果。

**F1**
severity: major
blocking: 是
file: `scripts/lumos` 的 `_android_ci_has_lint_task`(patch 第 272–286 行)。
引句:「if not re.search(r"gradlew|\bgradle[ \t]|\barguments:", line):」
失敗場景:判斷是逐行做的,一行裡要同時有 gradlew 和 lint 詞才算。CI 常見的寫法是 `./gradlew assembleDebug \` 換行後接 `lintDebug`,lint 詞在沒有 gradlew 的下一行,所以被略過,A1 會誤報「沒接 Android Lint」。健檢會一直叫使用者去貼 CI 範本,而且 A1 沒有任何關掉或略過的方法。
重現:`_android_ci_has_lint_task(["run: |\n  ./gradlew assembleDebug \\\n    lintDebug\n"])` 回 `False`,該回 `True`。
測試只涵蓋單行與 `arguments:` 單行,沒有反斜線續行的案例。

**F2**
severity: major
blocking: 是
file: `scripts/lumos` 的 `_android_ci_has_lint_task`(patch 第 272–286 行)。
引句:「for tok in re.split(r"[\s'\"`,;&|()\[\]{}=]+", line):」
失敗場景:判斷不排除註解行,也不排除 `-x lint` 這種明確跳過 lint 的寫法。`# ./gradlew lintDebug` 這種被註解掉的行,和 `./gradlew build -x lint`,都會讓 A1 被壓掉。這個提醒的用途就是抓「其實沒在跑 lint」,所以這是漏報,而且壓掉提醒的就是它要抓的情境。
重現:`f(["# ./gradlew lintDebug\n"])` 與 `f(["run: ./gradlew build -x lint\n"])` 都回 `True`。

**F3**
severity: major
blocking: 是
file: `scripts/lumos` 的 `_android_plugin_paths`(patch 第 289–311 行),對照 `_lint_spawn`(`scripts/lumos:39714`,`shell=True, cwd=repo_root`)。
引句:「out.append(_os.path.expanduser(part.replace("$HOME", str(Path.home())).replace("${HOME}", str(Path.home()))))」
失敗場景:宣告的命令是在 shell 裡、以 `cwd=repo_root` 執行,但 A3 判斷檔案存不存在時沒照這個規則。
- 相對路徑(`--plugins tools/p.jar`)是以 lumos 當下的 cwd 解析。從別的目錄跑 `lumos lint-check --repo X`,或 doctor 在 vault 目錄跑,外掛明明在 repo 裡也會誤報 A3。
- `$RUNNER_TEMP`、`$PWD`、`$(...)` 等其他 shell 變數沒有展開,整串字面拿去查檔,必定誤報。
重現:`_android_plugin_paths("detekt --plugins $RUNNER_TEMP/x.jar")` 回 `['$RUNNER_TEMP/x.jar']`,之後 `Path(...).is_file()` 必為 False。
修法:路徑要相對 `repo_root` 解析,遇到不認得的 `$` 就略過。

**F4**
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_android_build_texts`(patch 第 244–269 行)。
引句:「for rp in sorted(cands)[:max_files]:」
失敗場景:依路徑排序後只取前 200 支。模組超過 200 個的 monorepo,排在後面的 `feature/...` 模組,甚至根目錄的 `build.gradle.kts`(排在 `app/…` 之後),都不會被讀。這時 A2 會誤報(實際有 compose-lint-checks 卻沒讀到),`_KT_BUILD_ANDROID` 的 Android 判定也可能失準。
測試 `S2 第 201 支…不算` 把這個行為寫成預期,沒有解決它。
另外,`os.walk` 在 depth<3 時會列出每個非隱藏資料夾(`venv`、`Pods`、`vendor`、`.venv` 之外的大目錄)的所有檔案,健檢每次都跑,效率上多花功夫。

**F5**
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_lint_android_ci_advisories`(patch 第 333–336 行)。
引句:「for pth in _android_plugin_paths(c):」
失敗場景:同一個外掛路徑出現在多條命令,或同一條命令裡重複,會印出重複的 A3。另外 `-p` 當成 `--plugins` 的別名,在 `detekt` 之外的命令(例如 `sh -c` 包裝)靠 `"detekt" in cmd` 這個粗判斷才進得來,不一致。
代價:輸出雜訊,doctor 又有「最多列 20 條」的限制,會被重複條目擠掉別的提醒。

**F6(重用)**
severity: minor
blocking: 否
file: `scripts/lumos` 的 `_android_plugin_paths`、`_android_build_texts`(patch 第 244–311 行)。
引句:「import shlex as _shlex」
說明:專案內已有 detekt 命令的切詞與 `sh -c` 解包設施(`_detekt_split_segments`、`_detekt_command_codes`,`scripts/lumos:39134`),這裡另寫一套 `shlex.split` 加手動展開 `$HOME`。重複實作使 `sh -c '...'` 包裝、多行續行、`;` 分段的命令不會被解析到(`shlex.split` 把整段 `sh -c '…'` 當一個字,`--plugins` 找不到),行為和 T1–T4 的判斷不一致。如果沿用 `_detekt_split_segments` 的切段結果,就不用再各自處理這些情況。

**F7(慣例)**
severity: minor
blocking: 否
file: `scripts/lumos` 的 `cmd_lint_check`(patch 第 372–391 行)。
引句:「"advisories": [*advisories, *android_adv]」
說明:`--json` 的 `advisories` 形狀沒有壞(仍是字串清單,測試用 `" T1"` 或 `" A1:"` 前綴子字串比對),但現在 `advisories` 同時混了 detekt 的 T/P 提醒和 `[CI]` 開頭的 A 提醒。依賴 `len(advisories)` 或「只有 detekt 提醒」的外部腳本會受影響。我找不到 repo 內有這種呼叫端,所以不降成問題。另外人讀輸出裡兩份提醒用兩個函式各印一段,結構重複。

**其他角度**
- 角度 2(被刪掉的行為):`_detekt_ci_has_typed_task` 原本只讀 `.github/workflows/` 底下的 .yml/.yaml,並對讀不到的檔 `continue`。新碼用 `_ci_config_texts(github_only=True)` 做同樣的事,行為等價,測試也驗過。不影響。
- 角度 3(跨檔追蹤):`advisories` 在 `scripts/lumos` 與 `scripts/test_lumos.py` 的呼叫端都檢查過。`t_lintcheck_detekt_advice_output` 的「有宣告但沒 detekt:advisories 是空清單」成立,因為那個案例沒有 Android 建置檔。
- 角度 8(慣例):沒找到能逐字引用又能指出違反行的條目,不報。

**pitfalls manifest 判定**
`scripts/lumos` line 38995 的 `open(`:誤報。對應的 `with open(root / rp, "rb") as fh:` 在 `_android_build_texts` 裡,有 `with` 管理,會確定 close。

總結:max severity = major,blocking 共 3 條(F1、F2、F3)。這三條的最小重現我都跑過,結果如上。
