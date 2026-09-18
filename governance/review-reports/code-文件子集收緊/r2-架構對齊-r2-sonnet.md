severity: major

審材:governance/review-reports/code-文件子集收緊/r2-snapshot.patch(509 行,sha256 d4acdc57…已核對相符)。判準只看「這批寫法跟專案既有的一不一樣」,不列風格。

## 三問逐答(先給結論,細節見對應 F<n> / 驗過的路徑)

1. `_SUITE_GRAPH` 累積寫法 / `_suite_args+=(--graph)` 陣列寫法 / CI `graph` output 與 `sed -n Np`:**大致對齊**,但緊貼著 `_suite_args+=(--graph)` 這行、只隔兩行context 的 `--suite` 既有探測寫入口(`grep -q -- '"--suite"'`)沒有被沿用到 `--graph` 身上 → 見 **F1(major)**。
2. `_test_suite_for_range` 回 dict 多 `graph` 鍵、JSON 多 `suite_graph` 欄與既有欄位命名:**對齊**,見「驗過的路徑」。
3a. 執行器 `--graph` 旗標配對檢查(rc2)跟既有 `--keys` 配對檢查寫法:**對齊**,見「驗過的路徑」。
3b. `re.match(r"docs/[^/]+-knowledge/", f)` 認圖譜目錄跟 lumos 既有判定寫法:**不對齊**,lumos 裡已有兩處認「路徑是不是圖譜」的既有寫法沒被沿用 → 見 **F2(major)**。

不對齊共 2 條,其中 major 2 條。

## F1 `--graph` 沒沿用同一段裡緊鄰的「探測執行器認不認得旗標」既有寫入口

severity: major
blocking: yes

引句:「[[ "$_SUITE_GRAPH" -eq 1 ]] && _suite_args+=(--graph)   # 碰到圖譜筆記:加跑讀真圖譜的測試(檢索品質、評測)」

觀察到什麼:這行的正上方兩行,就是同一個 if 區塊決定 `_suite_mode` 用的既有寫法——「grep -q -- '"--suite"' "$REPO_ROOT/scripts/test_lumos.py" 2>/dev/null; then」——這是專案自己訂出來的寫入口:任何要塞進 `_suite_args`/呼叫執行器的新旗標,都要先讀執行器的原始碼探它認不認得,認不得就退全套,理由寫在同檔上面(hook 探 `--shard`/`--suite` 那段的既有註解就講過這件事:硬塞執行器不認得的旗標會讓它整個報錯,被誤判成「測試有紅」)。`--graph` 是這批新加的旗標,卻繞過這個既有寫入口,直接無條件 `_suite_args+=(--graph)`,沒有任何「執行器認不認得 --graph」的探測或退回。

怎麼重現(已在唯讀 worktree 裡實際跑過,未動到正式 repo):
1. `git worktree add --detach /tmp/seat-架構對齊-r2-sonnet 7cff4ef2`(這批凍結的提交)
2. 取一份還沒有 `--graph` 支援的舊版執行器:`git show c064ccad:scripts/test_lumos.py > /tmp/old-runner.py`(c064ccad 是這批之前的提交,代表「掛鉤版本比執行器新」或「執行器版本落後掛鉤」這種現實會發生的版本落差)
3. 模擬 hook 會下的指令:`python3 /tmp/old-runner.py --list --suite docs --graph`
4. 實際結果:`test_lumos.py: error: unrecognized arguments: --graph`,離開碼 `rc=2`。

為什麼是 bug 不是風格:pre-push 掛鉤自己的 `run_group()` 把「不是 0、也不是 3」的離開碼一律當 `_bad=1`(`file: \`scripts/hooks/pre-push:443\``:「[[ "$_r" -ne 0 && "$_r" -ne 3 ]] && _bad=1」),最終 `exit 1` 印出「擋下:test_lumos.py 有紅,有測試沒過」——把純粹的旗標版本不合擋成「測試沒過」,擋下合法推送。這正是 `--shard`/`--suite` 探測寫入口存在的理由(同檔既有註解:「新 hook 配到舊的(或別人自己寫的)runner 時,硬塞它不認得的旗標會讓它整個報錯 → 人被莫名其妙擋下」),`--graph` 沒有同等保護,踩得到一模一樣的假紅。CI 端(`.github/workflows/ci.yml` 的 `extra="$extra --graph"`)風險小一些(單一提交內 hook 腳本與 runner 一起改、版本自洽),但同樣沒有任何探測或退回。

## F2 圖譜目錄判定改寫成第三種寫法,沒沿用 lumos 裡已出現兩次的既有判定寫法

severity: major
blocking: yes

引句:「graph = any(re.match(r"docs/[^/]+-knowledge/", f) for f in files)」

觀察到什麼:這批在 `_test_suite_for_range` 裡新增「這批改動有沒有碰到圖譜筆記」的判定,寫成一段全新的正則式 `re.match(r"docs/[^/]+-knowledge/", f)`。但同一支 `scripts/lumos` 裡,對「一個 git 算出來的相對路徑字串,判斷它在不在 docs/*-knowledge 圖譜底下」這件事,已經有寫法完全一致、逐字重複兩次的既有慣例(都不是走檔案系統的 `_vault_in`/`find_vault`——那兩支要吃真正存在的目錄,對「範圍可能不是目前 checkout 的分支」這種情境不適用,所以不算既有判定函式;真正對得上的是下面這兩處):
- `file: \`scripts/lumos:21478-21479\``:「p.startswith("docs/") and p.count("/") >= 2」+「and p.split("/", 2)[1].endswith("-knowledge")」
- `file: \`scripts/lumos:26510\``:「p.startswith("docs/") and p.count("/") >= 2 and p.split("/", 2)[1].endswith("-knowledge")」

這兩處吃的輸入跟新增的 `graph` 判定完全同型——都是「git 算出來、不保證目前有 checkout 出來的相對路徑字串清單」(`_nodehome_list`/`git ls-tree` 的結果,對照這批的 `git diff --name-only` 結果),不是檔案系統路徑,所以是真正可比、該直接沿用的既有寫法,不是 `find_vault` 那種要求路徑實際存在磁碟上的函式。

怎麼重現:直接比對三段程式碼(引句 vs 上面兩個 `file:` 位置)即可看出是三種不同寫法在做同一件事——兩處用 `str.split("/", 2)[1].endswith(...)`,這批改用 `re.match`。

為什麼是 bug 不是風格:席名詞明列「引入第二種做法…才 major」,這裡是同一支檔案裡第三次寫「這個路徑是不是圖譜」,規則本身沒變(都是「docs/ 下第一層資料夾名結尾是 -knowledge」),純粹是又刻了一份既有判定邏輯,而不是呼叫或抽出既有寫法共用;往後兩邊各自被改動(例如未來圖譜目錄規則要加一種例外)時,容易只改到其中一處、另外兩處(含這批新加的)沒跟著改,形成行為分岔的坑。

## 驗過的路徑(已看,無發現)

- `_SUITE_GRAPH` 的累積寫法(`_SUITE_SEEN=0; _SUITE_FULL=0; _SUITE_LIGHT=0; _SUITE_KEYS=""; _SUITE_GRAPH=0` 起手、迴圈裡 `grep -q '"suite_graph": *true' && _SUITE_GRAPH=1`)跟既有 `_SUITE_FULL`/`_SUITE_LIGHT`(`case "$_suite_this" in full) _SUITE_FULL=1 ;; light) _SUITE_LIGHT=1 ;; esac`)是同一種「起始 0、命中就設 1、逐 ref 只加不減」寫法,對齊。
- `_suite_args+=(--graph)` 用的 `+=(...)` 陣列累加寫法,在 `scripts/hooks/pre-push`(`_PP_LINES+=("$_line")`)與 `scripts/hooks/pre-commit`(`src_files+=("$f")`)裡本來就是既有慣例,不是這批新引入的寫法;跟 `_keys_args` 用整段重新賦值(`_keys_args=(--suite keys --keys "$_SUITE_KEYS")`)不同,是因為 `_keys_args` 是獨立分支、`_suite_args` 是在已賦值的陣列上疊加,情境不同,不算另一種做法。
- CI 新 step output:python 一行式從印兩行(`suite`/`suite_reason`)擴成印三行(多 `suite_graph`)、`sed -n Np` 跟著從 `1p`/`2p` 擴到 `3p`、`echo "graph=$graph" >> "$GITHUB_OUTPUT"` 跟既有 `echo "suite=$suite" >> "$GITHUB_OUTPUT"` 同一種寫法,連錯誤時的預設字串都跟著補上第三行的換行(`'full\nlumos 算不出來\n'`),看得出是照既有兩行的樣子直接延伸成三行,對齊。
- `_test_suite_for_range` 回傳 dict 多的 `"graph"` 鍵,跟既有 `"light_ok"` 鍵一樣是布林、full 分支給 `False`;JSON 輸出把它改名成 `"suite_graph"` 而不是原樣的 `graph`,這跟既有 `reason` 鍵在 JSON 裡改名成 `suite_reason`(而不是保留 `reason`)是同一個既有規則——沒有已經是 `suite_` 前綴或已經全域唯一的鍵名,輸出時一律補 `suite_` 前綴避免跟別的欄位撞名,對齊,不是另立命名法。
- 執行器 `--graph` 的配對檢查——「if _args.graph and _args.suite != "docs": ... return 2」——跟既有「if _args.keys and _args.suite != "keys": ... return 2」逐字同構(旗標有給但 --suite 不是要求的值 → 印訊息 → return 2),插入位置也緊貼在既有 `--keys` 配對檢查正上方,對齊。
- `t_runner_suite_flags` 裡新增的 `r = run_r("--graph"); check("--graph 沒配 --suite docs 擋 rc2", ...)` 也是照抄既有 `--keys` 那條配對測試的寫法,沒有另立一套。

已核對材料範圍:`.github/workflows/ci.yml`、`scripts/hooks/pre-push`、`scripts/lumos`(`_test_suite_for_range`/`_pitfall_diff_collect` 兩處輸出)、`scripts/test_lumos.py`(`_docs_suite_select`/argparse/`t_test_suite_docs_only_judgement`/`t_runner_suite_flags`/`t_prepush_docs_and_light_run_subset`/`t_prepush_and_ci_wired_for_docs_suite`)全部四檔的差異段落;審材外核對過 `scripts/lumos` 裡 `_vault_in`/`find_vault`(檔案系統版,不適用)與兩處 `-knowledge` 路徑判定既有寫法(21478-21479、26510)。未派子代理,未跑全套測試,實驗只在 `/tmp/seat-架構對齊-r2-sonnet` 唯讀 worktree 跑過一次讀檔驗證後已 `git worktree remove --force` 清掉。
