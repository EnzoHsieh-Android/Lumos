severity: major

注意:`r1-snapshot-甲丙.patch` 沒收 `scripts/test_lumos.py`。測試那幾條我讀的是提交 `cafcd3ece` 裡的測試檔,行號是該檔的現況行號。

## 問 1:分層與依賴方向

新碼放在 `scripts/lumos`,就在 `_detekt_ci_has_typed_task` 旁邊。呼叫鏈是 `cmd_lint_check` 和 `run_doctor` 呼叫 `_lint_android_ci_advisories`,它再呼叫 `_ci_config_texts`、`_android_build_texts`、`_android_plugin_paths`。這條鏈跟 `_lint_detekt_advisories` 一樣,是由上往下的純函式,沒有跨層直呼,依賴方向跟鄰居一致。

`_ci_config_texts` 把 `_detekt_ci_has_typed_task` 原本內嵌的讀檔邏輯抽出來共用。我對照過 T4 的判定,檔案範圍(`github_only=True`)和讀不了就跳過兩點都沒變,對齊。

這一問沒有發現。

## 問 2:命名與錯誤處理

**F1**
severity: minor
blocking: 否
引句:「_ANDROID_ADVICE_ORDER = ("A1", "A2", "A3")」
`_DETEKT_ADVICE_ORDER` 用來排序輸出(`scripts/lumos:38803`,用在 `scripts/lumos:39173`)。新的 `_ANDROID_ADVICE_ORDER` 定義了卻沒有任何地方用它(`grep` 只有一處),輸出順序其實寫死在 `_lint_android_ci_advisories` 的 if 順序裡。這是跟鄰居形狀一樣、卻沒接電的死常數。

**F2**
severity: minor
blocking: 否
引句:「out.append("[CI] A3:" + _ANDROID_ADVICE_TEXT["A3"].format(name=Path(pth).name[:80]))」
- 標籤不一致:鄰居的 `[CI]` 標籤只給「看整個專案、一個專案最多一則」的 T4(註解在 `scripts/lumos:38802`),逐條命令的提醒用 `[kt 第 N 條]`(`scripts/lumos:39173`)。A3 是逐條命令、可以出好幾則,卻用 `[CI]`。
- 回顯內容:`_lint_detekt_advisories` 的 docstring 寫明「不回顯命令內容」(`scripts/lumos:39158`),A3 卻把命令裡的外掛檔名原樣印出。

**F3**
severity: minor
blocking: 否
引句:「"\n        ".join(["逐條:", *_aadv,」
- 健檢那一則沒有套用鄰居的 20 條上限。鄰居有 `_dshow` 截斷再加「… 另 N 條」(`scripts/lumos:4174`-`4176`),這裡 `*_aadv` 是整串展開。
- A3 對每條命令的每支外掛各出一則,沒去重,上限對它比對 A1、A2 更需要。

**F4**
severity: minor
blocking: 否
引句:「if not any(_KT_BUILD_ANDROID.search(b) for b in builds):」
鄰居判 Android 前先剝註解:`_kt_build_verdict` 呼叫 `_kt_strip_comments`(`scripts/lumos:38161`,註解寫明「註解裡提到…不算宣告」)。新碼直接對原文跑 `_KT_BUILD_ANDROID`,所以被註解掉的 `com.android.` 在新碼會算 Android,在 pitfalls 的角色判定不算。同一支建置檔會得到兩種 Android 結論。結構對,但判定口徑跟鄰居不一樣。`_ANDROID_COMPOSE` 同理。

測試的跳過與 CI 判紅:`_detekt_compose_jar`(`scripts/test_lumos.py:126311`)和 `t_detekt_compose_rules_shared_config` 的寫法,跟 `_detekt_real_bin`(`scripts/test_lumos.py:126490`)一致。`CI` 環境變數有設且找不到時用 `check(..., False, ...)` 判紅,否則回 `None`,函式印略過原因後照樣印 `✓ 測試名`。對齊。

## 問 3:第二種做法

**F5**
severity: major
blocking: 是
引句:「words = _shlex.split(cmd)」
`_android_plugin_paths` 是第二套切 detekt 命令的做法。既有的一族是 `_detekt_split_segments`(`scripts/lumos:38838`)、`_detekt_strip_prefix`(`scripts/lumos:38877`)、`_detekt_command_codes`(`scripts/lumos:39134`)。既有那套做了這些事:
- 設 `punctuation_chars=";&|"`,並關掉註解。
- 先把 `\\\n` 換成空白並逐行處理。
- 拆段、剝環境變數與 `env`/`nice` 這類包裝詞。
- 展開 `sh -c`。

新函式用裸的 `shlex.split`,上述四件都沒做:
- `detekt ... ; echo` 這種寫法,`;` 會黏在詞上。
- `sh -c '...detekt --plugins x...'` 抓不到。
- 命令中間的 `#` 會被當註解截掉。
- 多行 `\` 接續行不處理。

同一條 `.lumos/lint.json` 命令,A3 和 T1 到 T3、P1 看到的內容可能不同。`--plugins`/`-p` 的名單在 `_DETEKT_CLI_OPTS`(`scripts/lumos:38830` 一帶)也已經有一份。

**F6**
severity: major
blocking: 是
引句:「out.append(_os.path.expanduser(part.replace("$HOME", str(Path.home())).replace("${HOME}", str(Path.home()))))」
第二套展開 `$HOME` 的做法。專案原本只有 `expanduser` 這一種(`scripts/lumos:32533`、`scripts/lumos:34394`),`$HOME` 由 shell 在跑 lint 命令時展開。新碼用字串 `replace` 手工展開,只認 `$HOME` 和 `${HOME}`,不認其他環境變數。實際執行時 shell 會展開 `$XDG_DATA_HOME` 之類,A3 卻會誤判檔案不在。

**F7**
severity: major
blocking: 是
引句:「def _android_build_texts(repo_root, max_depth=3, max_files=200, max_bytes=1 << 20):」
第二套走目錄並讀建置檔的做法。既有的有三支:
- `_kt_build_candidates`(`scripts/lumos:38136`)從檔案往上找 `_KT_BUILD_FILES`,搭配 `_kt_build_verdict` 的讀檔上限與註解剝除。
- `_stack_ext_counts`(`scripts/lumos:33929`)用 `os.walk` 原地剪枝,跳過名單用 `_STACK_SCAN_SKIP`(`scripts/lumos:33920`)。
- 全 repo 的 git 檔清單走 `_nodehome_git ... ls-files`(例如 `scripts/lumos:24718`)。

新函式自己寫了一套 `os.walk`,有自己的深度、檔數、位元組上限(3、200、1MB),另立 `_ANDROID_SCAN_SKIP_DIRS`。它的跳過名單少了 `Pods`、`vendor`、`target` 這些,卻多了「隱藏資料夾一律不進」。同一個 repo 裡,兩套掃描對「哪些目錄不算專案」的看法不一樣。

**F8**
severity: major
blocking: 是
引句:「[test:t_detekt_compose_rules_shared_config]」
測試裡另一套解析 SARIF。`_sarif_rule_lines`(`scripts/test_lumos.py:126323`)自己用 `json.loads` 走 `runs`、`results`、`locations`,拿 `ruleId` 和 `startLine`。既有的解析是 `_lint_run_and_parse`(`scripts/lumos:39724`),而且測試已有在用:`scripts/test_lumos.py:14722` 的 `m._lint_run_and_parse(cmd, root)`。

這一支還繞開了宣告到閘的路徑:它直接 `subprocess.run([det, ...])` 跑 detekt,沒走 `{LINT_SARIF_OUT}` 佔位符與 `_lint_run_and_parse`。要驗的「外掛缺檔時閘判環境不可用」其實沒經過閘,只是檢查「沒產 SARIF」。

**F9**
severity: major
blocking: 是
引句:「由測試對全表重算比對」
型錄口徑寫在測試裡,而型錄自檢本來就在 `configs/ast-grep/kotlin-android/check.py` 的 `catalog_problems`(`configs/ast-grep/kotlin-android/check.py:129`)。型錄的欄位、來源、出處檢查已經集中在那裡,並由 `--catalog-only` 觸發。`t_kt_catalog_batch4_wiring`(`scripts/test_lumos.py`,`_KT_B4_*` 一帶)又在測試檔裡另立一套:
- 用自己的正規式重算每列的「批四」標籤。
- 自己切 `## 情境決策表`、`## 來源縮寫`。
- 自己硬寫一份官方預設關規則清單。

型錄口徑因此有兩個住處,下次改型錄時一邊改了、另一邊可能不知道。

不對齊共 9 條,其中 major 5 條

其中會擋的是 F5、F6、F7、F8、F9,不擋的是 F1、F2、F3、F4。

(⚠ 給編排者:F9 我判 major,是因為題目明列「型錄口徑寫在測試裡」。若計劃把 `check.py` 定位成只管規則包與型錄格式、不管接電標籤,可降為 minor。這點我從計劃檔看不出來。)
