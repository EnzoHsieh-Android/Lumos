severity: major

## 1. 分層與依賴方向

對齊,只有一處例外,見 a1。

- `_kill_run_dir`(`r2-code.patch` 第 30 行)放在 `_kill_plat_top` 旁邊,也呼叫它。ctx 用 `{"tops": {}}`,和 `_situation_rule_platform`(`scripts/lumos:75933`)同做法。
- `_kill_err_all`、`_kill_also_*`、`_kill_mask_paths` 都放在 `_kill_*` 家族,由 `cmd_guard_kill` 往下呼叫,方向和 `_kill_old_issue`、`_kill_new_issue`(`scripts/lumos:26717` 一帶)一致。
- `_situation_rule_*` 往下呼叫 `_kill_also_issue`、`_kill_also_apply`、`cmd_guard_kill(recipes_override=…)`,和既有人裁到殺傷力的方向相同。
- 修補把 `_gradle_task_list` 改走 `_detekt_walk_segments`、`_is_gradle_head`、`_gradle_args_tasks`(`scripts/lumos:40965`、`40960`),還把 `_gradle_build_android` 換成 `_android_build_texts(max_depth=0)`(`scripts/lumos:40794`)。重用了鄰居,也解掉上一輪的 a1、t2。
- 範圍解析走 `_kt_bj_segments` 和 `_codeloop_disp_range`,沒有自己另算。
- `_kill_run_dir` 的 `startswith(real_wt + os.sep)` 圍欄,和 `cmd_guard_kill` 裡 target 的圍欄寫法相同。
- 本輪修補沒有新增跨層直呼。

## 2. 命名與錯誤處理

大致對齊。

- 名稱延續 `_kill_*`、`_situation_rule_*`、`_gradle_*` 前綴。
- 原因字串回傳(`_kill_also_issue` 回字串或空字串),和 `_kill_old_issue` 同形。
- 人裁拒絕走 `_situation_rule_say`,rc 2,不動計劃。
- 失敗摘錄在 stderr 先印,再走 `_kill_esc`。
- guard kill 判 error 與 drifted 的分法沿用既有語意。
- 小偏差:`_situation_rule_diff_problem` 的 `subprocess.run` 沒有 timeout,也沒接 `OSError`,和 `_kill_plat_top` 與 `_lens_git` 一族的寫法不同。這條併在 a2。

## 3. 第二種做法

有兩處,見 a1、a2。其餘的路徑遮罩、shell 切詞、找建置檔、範圍解析,鄰居裡都沒有同功能函式,不算第二種做法。

- `_kill_mask_paths` 的家目錄與工作樹遮罩:`scripts/lumos` 裡沒有同功能函式。
- shlex、`_sh_quote`:修補已把自寫切詞拿掉。

## a1 檔頭掃描自寫了一套 Kotlin 註解與字串剝除
severity: major
blocking: 是
引句:「Kotlin 一行去掉註解(註解是隱藏記號)→ (程式文字, 行尾時區塊註解的巢狀層數, 這一行 ( [ 減 ) ] 的淨數)」
file: `scripts/lumos:6869`

`_strip_c_comments` 的 docstring 寫明「全庫只有這一個入口……不留兩套掃描」。它的 `kotlin=True` 分支(經 `_kt_strip_spans`,`scripts/lumos:6984`)已支援巢狀區塊註解和字串樣板。`keep_newlines`、`keep_length` 也能讓行號對得上。

新的 `_situation_rule_code_of_line`,加上 `_situation_rule_header_scan` 裡的 `depth` 與 `paren` 狀態,是手寫的第二套 Kotlin 剝註解:逐字元掃 `/* */`、`//`、引號。它處理字串的方式也和既有版不同:既有版有三引號字串(沒有跳脫)、`${…}` 樣板、反引號識別字,新版都沒有。

整檔先剝一次、再逐行掃檔頭,就能取代它。`_kt_sit_read_many` 讀進來的就是整檔文字。上一輪 c2、b1、b2、t3 的修法選了「自寫逐行狀態機」,而不是用既有入口。

## a2 `--diff` 兩端解析自己叫 git,沒用既有的 rev 解析函式
severity: major
blocking: 是
引句:「["git", "-C", str(rr), "rev-parse", "--verify", "-q", "--end-of-options", e + "^{commit}"]」
file: `scripts/lumos:69503`

`_lens_full_sha(repo_root, rev)` 做的是同一件事:`rev-parse --verify -q --end-of-options <rev>^{commit}`,再驗 sha 形狀。它走 `_lens_git`,有 timeout,也接了 `OSError`、`TimeoutExpired`。`_lens_range_ok` 已被正確重用,但 rev 解析是另抄一份裸 `subprocess.run`。

這份抄本沒有 timeout,git 不存在時會丟 `FileNotFoundError`,也不驗輸出是 sha。改成 `_lens_full_sha(rr, e)` 一行可取代,退路也會和 impact、pitfalls 一致。

不對齊共 2 條,其中 major 2 條
