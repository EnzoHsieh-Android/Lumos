severity: major

## F1 新增的 `--graph` 旗標沒有比照 `--suite`/`--shard` 做「runner 認不認得這個旗標」探測,舊版 runner 配新 hook 會把合法的文件推送誤判成「測試有紅」而擋下

severity: major
blocking: yes

引句:「    [[ "$_SUITE_GRAPH" -eq 1 ]] && _suite_args+=(--graph)   # 碰到圖譜筆記:加跑讀真圖譜的測試(檢索品質、評測)」

觀察到什麼:`scripts/hooks/pre-push` 對 `--suite`(file: `scripts/hooks/pre-push:401`)與 `--shard`(file: `scripts/hooks/pre-push:395`)都先 `grep -q -- '"--suite"' ...test_lumos.py` 探一次「這支 runner 認不認得這個旗標」,認不到就退回舊行為(不帶該旗標/退串行)。這個探測的存在理由,pre-push 自己的註解寫得很白:「★先探這支 runner 支不支援分片★:新 hook 配到舊的(或別人自己寫的)runner 時,硬塞它不認得的旗標會讓它整個報錯 → 人被莫名其妙擋下。探不到就乖乖退回串行,行為跟以前一模一樣。(2026-09-06 實際踩到:假 runner 不認得新旗標,當場被判紅。)」(file: `scripts/hooks/pre-push:385-388`)。

但這次新增的 `--graph`(file: `scripts/hooks/pre-push:407`)完全沒有同款探測——`_SUITE_GRAPH` 一旦被任何一個 ref 標成真,就直接把 `--graph` 塞進 `_suite_args`,不管當下這份 `scripts/test_lumos.py` 認不認得這個字。

怎麼重現(端到端真跑,不是猜):
1. 建一個乾淨假 repo,裝上這次 fold 之後的真 `scripts/hooks/pre-push` 與真 `scripts/lumos`,但 `scripts/test_lumos.py` 用「本輪 fold 之前」的版本(`git show cf3dfa84:scripts/test_lumos.py`——那個版本已經有 `--suite docs`,但還沒有 `--graph`)。
2. 建一篇 `docs/lumos-toolchain-knowledge/Systems/Home.md`,commit 一次當基準,`git push --no-verify` 建好遠端起點。
3. 只改這篇圖譜筆記(加一句話)再 commit 一次,這次用真的 `git push`(掛鉤生效)。
4. 結果:`lumos doctor` 先過(0 issues),接著印出「擋下:test_lumos.py 有紅,有測試沒過。紅的是這幾支:」,`git push` 回 `error: failed to push some refs`,rc=1。
5. 但把掛鉤存的完整輸出攤開看,四片全部是同一段:
   ```
   usage: test_lumos.py [-h] [-k KEYWORD] [--list] [--keep-tmp] [-x] [--ff]
                        [--seed N] [--shard 第幾片/共幾片] [--json-summary 檔案]
                        [--suite {docs,keys}] [--keys 名字,名字]
                        [關鍵字]
   test_lumos.py: error: unrecognized arguments: --graph
   ```
   四片全是 argparse 因為不認得 `--graph`直接報錯(rc=2),一支測試都沒真的跑,卻被 `run_group()` 的判準(`_r -ne 0 && _r -ne 3` → `_bad=1` → 整組判「有紅」)當成「測試失敗」,擋下一次完全合法、只改圖譜筆記的推送。

為什麼是 bug 不是風格:這正是 pre-push 自己註解裡點名、2026-09-06 已經真的發生過一次、後來特地為 `--suite`/`--shard` 補上探測旗標避免的同一種故障模式——這次替 `--graph` 加邏輯時沒有比照辦理,在同一支檔案裡留下不一致的防禦深度。可觸發場景不是憑空想像:這支工具鏈設計上就是要被 vendor 進消費專案、靠 `lumos update` 同步(`_vendor_toolchain`/`_sync_global_from_project` 一帶到處在處理「vendored 檔案更新順序」的問題),任何一次 `scripts/hooks/pre-push` 先於 `scripts/test_lumos.py` 落地的中間狀態(更新沒跑完、消費端只拉了部分檔、或是本地暫存/合併衝突留下舊版 test_lumos.py),都會讓一次單純的圖譜筆記推送被誤擋,而且錯誤訊息完全誤導(講「有測試沒過」,不是「這支 runner 太舊」)。

## F2 `--graph` 挑測試靠原始碼裡有沒有出現「-knowledge」字樣,這個字樣同時是全檔案上百支測試通用的假 vault 命名慣例(`x-knowledge`/`demo-knowledge`/`kg-knowledge`…),導致挑進來的 46 支裡約四分之三根本沒讀真圖譜,跟這條新機制自己宣稱的目的矛盾,且讓「碰到圖譜筆記」情境下的子集執行時間翻倍以上

severity: major
blocking: yes

引句:「    # graph=True(推送碰到圖譜筆記):讀真圖譜的測試也算——檢索品質、評測、goldset 這些圖譜健檢驗不到(r1 通才席)
    rx_graph = _re.compile(r"-knowledge")」

觀察到什麼:`rx_graph` 是對測試原始碼(含一跳輔助函式)做「有沒有出現子字串 -knowledge」的裸比對,沒有要求它連到「真的這個 repo 的 `docs/lumos-toolchain-knowledge`」。但這個字樣在 `scripts/test_lumos.py` 裡是通用假 vault 命名慣例,一路撒在 `x-knowledge`、`demo-knowledge`、`z-knowledge`、`t-knowledge`、`kg-knowledge`、`proj-knowledge` 這些跟真圖譜無關的臨時目錄名上(隨手 grep 就有幾十處,不是特例)。

怎麼重現:實跑 `python3 scripts/test_lumos.py --list --suite docs` 得 63 支、`--list --suite docs --graph` 得 109 支,`--graph` 多拉進來的 46 支逐一核對原始碼(含一跳輔助函式):
- 只有 12 支真的碰真圖譜 `docs/lumos-toolchain-knowledge`(例:`t_slim_gate_search_equivalence_counterfactual`、`t_impact_end_to_end`、`t_precommit_whitelist_drift_guard`)。
- 25 支是共用 `_mk_eval_fixture()`/`_load_retrieval_eval()` 的評測邏輯測試(`t_eval_*`、`t_refresh_*`、`t_must_see_ratchet`、`t_pin_noise_ratchet`…)——這兩支輔助函式建的是 tempdir 底下的假 vault `docs/kg-knowledge`(file: `scripts/test_lumos.py:27484`),`_load_retrieval_eval` 雖然用 `Path(GRAPHCTL).resolve().parent.parent` 定位真 repo 根(所以會命中 `rx_real`),但那只是拿來找 `governance/eval/retrieval_eval.py` 這支*程式*的路徑,載入後立刻把 `m.ROOT`/`m.VAULT` 全部改指回假的 tempdir vault(file: `scripts/test_lumos.py:27518-27519`)——這批測試從頭到尾沒讀過一個字的真圖譜筆記。
- 其餘 9 支(`t_lens_recount_*`、`t_codex_s3_*`、`t_update_*`、`t_goldset_force_full_guard`)也都是拿 Codex 逐字稿/假 clone/假 goldset fixture 在測程式邏輯,同樣沒碰真圖譜內容。

實測時間:單機四片同時跑,`--suite docs`(63 支)28 秒;`--suite docs --graph`(109 支)66 秒——多一倍以上,而多出來的 46 支裡四分之三對「圖譜筆記改了要不要重驗」這個問題完全答不出東西,純粹陪跑。

為什麼是 bug 不是風格:這條機制的存在理由是它自己的註解寫的「讀真圖譜的測試也算——檢索品質、評測、goldset 這些圖譜健檢驗不到」,但實測只有約四分之一名副其實。更諷刺的是,同一輪 fold 裡另一半修的正是「只在假環境裡寫一份 CLAUDE.md 的整合測試跟這次改的真文件無關」這個同構問題(`_docs_suite_select` 的 docstring 自己講的),`rx_graph` 卻用最鬆的裸子字串比對把同一種假環境誤命中問題原封不動地在 `--graph` 這邊重新種回去——沒有像 `rx_doc` 那樣要求路徑錨定或跟 `_DOCS_ONLY_PATHS` 對齊。目前唯一的把關 `t_runner_suite_flags` 只斷言「有加、有 t_slim_gate、沒有 t_ci_wait」,沒有像文件子集那樣訂一個上限(file: `scripts/test_lumos.py` 的 `check("docs 子集不超過全套一成…")` 只驗 `names` 不驗 `--graph` 之後的 `gnames`),所以這個精度回退完全沒有測試守著,以後只會更鬆不會變緊。

## 驗過的路徑(沒發現額外問題)

- CI 的 `sed -n 1p/2p/3p` 在「lumos 出錯走 `printf 'full\nlumos 算不出來\n'` fallback」時的行為:實測 `sed -n 3p` 在這個只有兩行的字串上回空字串,而此路徑下 `suite` 本來就會停在 `full`,所以 `graph` 是否為空不影響最終判定,沒有第三行漂移問題。
- `re.match(r"docs/[^/]+-knowledge/", f)`:逐一手算過 `docs/lumos-toolchain-knowledge/...`(命中)、`docs/x-knowledge-old/...`(不命中,因為 `-knowledge` 後面接的是 `-old` 不是 `/`)、大寫 `docs/Foo-Knowledge/...`(不命中,regex 沒有 `re.IGNORECASE`,但專案慣例本來就是全小寫,非真實風險)。
- 掛鉤多 ref、一個碰圖譜一個不碰:`_SUITE_GRAPH` 是單純跨 ref 的 OR 累加(同一支檔案裡 `_SUITE_FULL`/`_SUITE_LIGHT` 也是同款寫法),且 `_test_suite_for_range` 保證 `graph` 欄位只在 `suite=="docs"` 時才可能為真(full 分支兩個回傳點都明寫 `"graph": False`),沒有交叉污染。
- `--graph` 沒配 `--suite docs`、配 `--suite keys`:實跑 `--suite keys --keys foo --graph` 與單獨 `--graph`,都印「擋下:--graph 只配 --suite docs 用」、rc2,符合預期。
- `suite_graph` 在 `_pitfall_diff_collect` 的兩個 JSON 回傳點(no_lint fallback 與有 lint config 兩條路)都有帶,實跑 `lumos pitfalls --diff ... --json` 確認欄位存在。
- 假執行器記錄檔搬到 repo 外(`argl = d.parent / "runner-args.log"`):確認 `_sg_commit` 真的用 `git add -A`,搬出去之前若留在 `d` 內,下一次 `_sg_commit` 會把上一輪掛鉤跑完留下的 log 檔一併吃進提交、多一支非文件檔進推送範圍,判定會跟著漂——這個修法是對的,且用兩個場景(純文件放行 / 只改圖譜筆記帶 `--graph`)的完整組合都實跑過 `t_prepush_docs_and_light_run_subset` 確認通過。
- 這次 delta 動到、新增或改斷言的測試(`t_test_suite_docs_only_judgement`、`t_runner_suite_flags`、`t_prepush_docs_and_light_run_subset`、`t_prepush_and_ci_wired_for_docs_suite`)四支都在乾淨 worktree 裡單獨真跑過,全部通過,沒有發現斷言本身失真或漏測的地方(除了上面 F2 指出的「有加但沒訂上限」這個結構性缺口)。
