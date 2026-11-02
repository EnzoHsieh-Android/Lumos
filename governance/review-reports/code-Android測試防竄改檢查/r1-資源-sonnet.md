severity: major

## 圖譜鏡頭

以 `lumos show` 讀了 `Systems/test-guard` 和計劃筆記。`Systems/pitfalls-lint-adapter` 和 `Systems/bound-tests-gate` 沒細讀,以下只涉及 test-guard 與計劃的宣稱。

- 計劃〈效能〉寫「300 支檔 0.4 秒、每支檔開始前看一次截止時間」。S11 又寫「一次改 300 支檔應在 30 秒內」。F1 的輸入同樣是 300 支檔,實測 196 到 199 秒,和這個宣稱不符。
- 計劃寫「比對算在同一個 300 秒預算裡」,但沒提這會讓既有檢查命令的單條保底(30 秒)提前不成立。F2 實跑證明,調小 `budget_sec` 的專案會被誤擋。
- `Systems/test-guard` 有一條 WHY:「off 的專案仍付比對成本」。實際成本沒有上限,見 F1。截止時間只在 `_tg_analyze` 的逐檔迴圈裡檢查。迴圈之後的 `_tg_test_rules` 完全不檢查。
- 沒有發現 diff 破壞 `bound-tests-gate` 的語意。
- off 模式有傳截止時間給比對,這點符合圖譜宣稱。
- lint-waive 在沒有終端時不會卡住推送流程,也不會卡住 CI(見 F5 的條件)。

### F1 命中候選一多,`_tg_hit_cands` 變成「命中數 × 檔數 × 行數」,截止時間管不到
severity: major
blocking: 是 — 一次正常的大批量改動讓推送卡幾分鐘,而且超過預算也不會被中斷
引句:「path, ln = next(((p, _tg_line_of(h, line)) for p, _b, h, _fb, _fh, _kt in test_files if _tg_line_of(h, line)),」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:49080`,以及 `_tg_line_of` 在 `:48916`

**走到哪一行。** 每個命中(`tq/skip-added` 或 `tq/snapshot-changed`)都從第一支測試檔開始找。對每支檔先 `split("\n")`,再逐行呼叫 `_tg_norm`(一次 `re.sub`),直到找到那行文字為止。`_tg_line_of` 在 generator 的條件裡被呼叫一次,又在 tuple 的取值裡再呼叫一次,所以成功的那支檔掃兩遍。

`_tg_analyze` 的逐檔迴圈檢查了 `deadline`,但 `_tg_test_rules` 在迴圈之後呼叫(`:48955`),完全沒有截止檢查。

**輸入與實測。**
- 300 支測試檔,每支 20 個 `@Test` 函式,每個函式新加一行不同的 `@Ignore("flaky i_k")`,共 6000 個命中。每支檔約 260 行、13KB,遠低於單檔上限。
- `lumos test-guard`:196 秒。
- 走閘門 `_lint_new_verdict(deadline=monotonic()+60)`:199.5 秒,輸出 `status blocked ... 6000 條作弊候選`。`guard["error"]` 是 None,沒有出現「超過截止時間」。預算 60 秒,實際跑了 199 秒。
- 80 支檔、1600 個命中,cProfile 顯示 31 秒中有 28 秒在 `_tg_norm`(1730 萬次呼叫)。
- 耗時大致隨命中數乘檔數成長,檔案或命中再多一倍,耗時會再翻好幾倍。

**為什麼這是作弊比對最常遇到的情境。** 「一口氣把一堆測試加上 `@Ignore`」正是它要抓的事。這時整個推送會卡在比對裡,時間沒有上限。計劃的 S11 把 300 支檔寫成 30 秒內,但沒涵蓋「300 支檔都有命中」。

**off 模式。** `_lint_new_off` 照樣跑比對,同一段無上限的時間照付,而且 off 專案的人就是不想付這筆成本。

**修法方向。** 收集命中時就把 `(path, line)` 一起記下來,不用事後反查。這也能同時修掉 F4 的錯檔問題。

### F2 比對先吃掉共用預算,正常推送被判成「時間預算沒跑到」而擋下
severity: major
blocking: 是 — 沒有任何候選、檢查命令本身 0.1 秒就跑完,推送卻被擋
引句:「budget_end = deadline if deadline else (_time.monotonic() + cfg["budget_sec"])」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:39105`(`out["guard"] = _lint_new_guard(repo_root, start, tip, deadline)` 在 `:38959`,在檢查工具之前先跑)

**走到哪一行。** `_lint_new_verdict` 先呼叫 `_lint_new_guard`,它用掉共用的 `deadline`。`_lint_new_tools` 再用同一個 `deadline` 當 `budget_end`。`_lint_new_run_cmds` 裡,`left < per_cmd_floor_sec` 就記一筆 `kind:"budget"` 的 undone,於是 `hard_undone` 非空,閘門 block。

`_LINT_NEW_DEFAULTS` 的註解明說,慢工具的專案應該自己把 `budget_sec` 和 `per_cmd_floor_sec` 調小。調小之後,比對吃掉的比例就更大。

**重現。**
- 建一個 Kotlin repo,`.lumos/config.json` 寫 `{"lint_new":{"gate":"block","budget_sec":60}}`,`.lumos/lint.json` 宣告一條瞬間跑完的 `kt` 命令。
- 改動 10 支測試檔,每支約 4.9MB、9 萬行,是上限內的合法輸入。再加一支 `src/main` 的 `.kt`。測試檔的改動不構成任何候選。
- 實跑 `_lint_new_verdict(repo, A..B, deadline=monotonic()+60)`:

```
elapsed 38.0 status blocked blocked True reason 1 條命令因為時間預算沒跑到
undone [{'kind':'budget', ..., 'detail':'時間預算剩 22 秒,不足單條保底 30 秒'}] ran 0 guard err None
```

- 對照組:用 base 版本 `047031883` 的 `scripts/lumos` 跑同一個範圍和同一份設定,`elapsed 0.1 status clean blocked False ran 1`。
- 預算改 300 時新版是 clean,可見只有調小預算的專案受影響。
- 修法方向:比對用自己的截止時間或預算比例,不要吃掉檢查命令的保底時間。

### F3 `_TG_LIT` 和 `_TG_CONST` 對長字串常值造成約 100 倍的記憶體放大
severity: minor
blocking: 否 — 受 5MB 單檔上限約束,實測 4.5MB 常值的峰值約 1.06GB,不是無限成長
引句:「_TG_LIT = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)\'')」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:48496`(`_TG_CONST` 在 `:48456`,結構相同)

**走到哪一行。** `[^"\\\n]` 和 `\\.` 兩個分支放在 `(?:…)*` 裡,不是佔有式。既有的 `_C_STRIP_PAT` 刻意用 `*+`,就是為了避開這個問題。

**重現。**
- 一支測試檔,內含 `assertEquals("<4.5MB 單行字串>", a)`,改動前後只差一個字元。
- `lumos test-guard`:8.2 秒,峰值 1,061,537,064 位元組。
- 單獨跑 `_TG_LIT.fullmatch('"'+'a'*4500000+'"')`:峰值約 540MB。

**影響。** 這個峰值會疊在 F6 的 1.5GB 上。

### F4 命中的檔案和行號歸給第一個含同一行文字的檔,另有誤報
severity: minor
blocking: 否 — 候選位置錯,但推送結果(擋或不擋)沒變
引句:「(test_files[0][0] if test_files else "", 0))」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:49080`

**走到哪一行。** 檔案和行號是事後用文字內容去所有已變更測試檔裡反查,第一個含該行的檔就是答案。

**重現。**
- `ATest.kt` 本來就有一行 `@Ignore`,這次只改了函式內的其他地方。
- `BTest.kt` 這次新加一行 `@Ignore`。

實跑輸出的兩條候選都是 `ATest.kt:3`。一條是 B 新加的,檔案歸錯了。另一條是 A 原本就有的 `@Ignore`,只因為函式簽名變了,擁有者雜湊跟著變,被算成新增。

這個問題和 F1 同一個函式,修法一起解決。

### F5 `_ci` 區塊的放寬鍵偵測是平方級
severity: minor
blocking: 否 — 需要單一 CI 檔內有數千個同層放寬鍵,正常 CI 檔不會有
引句:「while q < len(indent) and (indent[q] is None or indent[q] > indent[p]):」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:48775`

**走到哪一行。** 每個 `continue-on-error: true` 這類放寬鍵,都會往回掃到比它縮排淺的標頭,再往前掃整個區塊,最後 `any(gradle[p:q])` 再切一份片段。

**實測。** 一個 job 底下 n 行同層的 `continue-on-error: true`:n=2000 要 0.29 秒,n=4000 要 1.15 秒,n=8000 要 4.73 秒,隨 n² 成長。單檔上限是 10 萬行,照這個趨勢會跑到十幾分鐘。這在單一檔案內部發生,逐檔迴圈的截止檢查打斷不了。

### F6 單檔上限之內的合法輸入,記憶體約是輸入的 7.6 倍,超過計劃的 30 秒目標
severity: minor
blocking: 否 — 沒有超出計劃寫的檔案數與總量上限,但計劃沒寫這個倍率,也沒寫對應的時間
引句:「_TG_MAX_TOTAL = 200_000_000          # 一次推送讀進來的內容總量上限;超過的那幾支列 tq/too-large」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:48383` 附近(常數定義);`_tg_read` 在 `:48893` 附近

**實測。** 20 支各約 4.9MB、9.1 萬行的測試檔,兩端合計 196MB,在 5MB / 10 萬行 / 200MB 的上限之內。結果:
- 耗時 75.8 秒。
- 峰值記憶體 1,503,119,016 位元組。

**倍率偏高的原因。** `text` 字典一直活到 `_tg_analyze` 結束。`test_files` 又為每個函式各存 `raw` 和 `mbody` 兩份複本。

**其他數字,供對照。** 4000 支共 180MB 的 `src/main` 檔:16.6 秒、786MB。上限內的 1 個 96,245 行測試檔:24.8 秒,主要耗在 difflib 的重複斷言。

**值得再看的兩處。**
- 分岔點起算:`_tg_start` 讓每次推送都重付整條分支的成本,即使只改一行。
- `cat-file --batch` 逾時:`_nodehome_cat_blobs_capped` 在 60 秒上限逾時,回傳 `None`,所有檔都被標成 `UNREADABLE`。模擬這個回傳值,300 支檔變成 300 條 `tq/unreadable`。這是工具逾時被記成每個檔案各一條候選,不是檔案本身有問題。這一點是模擬結果,真實逾時未重現,標 ⚠。

### F7 每個建置檔都獨立跑一次 `git grep`
severity: minor
blocking: 否 — 每次 0.05 秒,只有一次推送改很多建置檔時才累積
引句:「retry_ok = _tg_retry_ok(root, head) if retry_ok is None else retry_ok」
file: `/Users/enzo/harness/lumos-tq-android/scripts/lumos:49002`

**走到哪一行。** `retry_ok` 是 `_tg_build_cands` 的區域變數,每個檔案各算一次,同一個 `head` 的結果沒有快取。

**重現。** 300 個模組的 `build.gradle.kts` 都新加 `maxRetries`,整個 repo 3 萬支檔。`lumos test-guard` 耗時 19.9 秒,其中約 15 秒是 300 次 `git grep`。單次約 0.05 秒,repo 越大每次越慢。

### 其他確認過、沒有問題的

- 逾時和 Ctrl-C 時沒有 git 子程序殘留。`_nodehome_cat_*` 與 `_lens_git` 都用 `subprocess.run(timeout=)`,逾時會殺掉子程序。比對本身不建暫存目錄。`_lint_new_tools` 的 `mkdtemp` 仍有 `finally: rmtree`。
- off 模式的比對有傳截止時間,且 `LUMOS_SKIP_LINT_NEW` 也走同一條路。唯一例外是 `_tg_start` 裡的 `_lens_default_base`,它沒傳截止時間,只靠單次 20 秒上限。
- lint-waive 沒有終端時:沒有 `/dev/tty` 會立刻回 `None`,CI 不會卡。stdin 是 TTY 的情況會等 `LUMOS_TTY_TIMEOUT`(預設 30 秒)。阻擋訊息一次印出最多 50 條 waive 指令,如果由接了虛擬終端卻沒人答的代理逐條呼叫,每條最多等 30 秒。只有 `stdin.isatty()` 為真且 `readline()` 回空字串(isatty 撒謊)時才會連等兩次。推送流程本身不呼叫 lint-waive,所以不會卡住推送。
- `_lint_new_kind_counts` 讀整本治理帳(本機 21MB / 12.4 萬行),但只有健檢呼叫,而且既有的 `_lint_new_autopass_count` 本來就整本讀,不是新增的成本。
- 大檔 `_C_STRIP_PAT` 剝註解、`_rg_methods` 的 600 字元宣告上限、`_rg_expr_end` 的運算式本體切法,在我試的輸入(4 萬行 `a<a<a<…`)沒有退化,6.7 秒。
- 實跑中發現一個與資源無關的正確性缺口:重複的相同斷言行讓 difflib 只產出 insert 加 delete,不是 replace,`tq/expected-changed` 漏報。這不屬資源席,供參考。

最嚴重等級 major,blocking 共 2 條(F1、F2)。
