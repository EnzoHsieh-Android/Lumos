severity: minor

## c1 整批掃描對「被 .gitignore 蓋住的暫存目錄」靜默得到零命中(逐檔掃不會)
severity: minor
blocking: 否 因為觸發要求 TMPDIR 落在一個忽略規則蓋得到 `*.kt` 或 `*` 的 git 工作樹裡,是罕見環境;但發生時判定會從算得出變成靜默放行。

- 輸入:TMPDIR 指到某 git repo 底下的目錄,該 repo 的 `.gitignore` 內容是 `*` 或 `*.kt`;改動含兩支各有一個比較運算選擇點的 .kt。
- 路徑:`_choice_scan` 對多於一支檔的改動先走 `_choice_scan_batch`,對 `src` 整個目錄跑 `ast-grep scan`。ast-grep 掃目錄時會套用 `.gitignore`,直接點名檔案則不套用。整批 rc 為 0,輸出為空,所以不退回逐檔,每支檔被判成「沒有選擇點」。
- 預期:兩支檔各 1 個命中。實際:修後兩支都是 0 個,`bad` 為空,沒有任何提醒,推送端當作不需要處置。
- 命令:`TMPDIR=<該 repo>/tmp python3.14 probe1.py <版本>/scripts/lumos`,其中 probe1.py 載入 lumos 後呼叫 `_choice_scan(cwd, {"a/A.kt": T, "b/B.kt": T}, 60)`。
  - 修前 f1be3141:`{'a/A.kt': 1, 'b/B.kt': 1} {}`
  - 修後 8e521300:`{'a/A.kt': 0, 'b/B.kt': 0} {}`
  - 修後、TMPDIR 在 `/var/folders`(正常環境):`{'a/A.kt': 1, 'b/B.kt': 1} {}`
- 補充:`.gitignore` 內容是 `tmp/` 或 `lumos-choice-*` 時沒有重現,只有 `*`、`*.kt` 這類蓋得到暫存檔本身的規則會。我另用 ast-grep 直接驗過:同一目錄整批 0 行輸出、單檔 1 行輸出。
- 修法方向:整批改成逐檔呼叫那種不套忽略規則的行為(加 ast-grep 的 `--no-ignore` 一類旗標),或整批結果的命中檔數對不上時退回逐檔。
引句:「rc = _choice_sg_run([exe, "scan", "--config", cfg, "--json=stream", "src"], tmp, str(out_path), timeout)」
file: `scripts/lumos:77045`(修補差異 `_choice_scan_batch`)
歸因:有證據的修復回歸(修前逐檔點名檔案,兩版輸出如上)。

## c2 守的測試雜湊的「副檔名限定」拿掉後測試照綠
severity: minor
blocking: 否 因為改壞只會多重跑(多算進測試資料夾裡的非程式檔),不會漏掉該重跑的行。

- 改壞:把 `git grep` 的路徑樣式 `*{e}` 整段拿掉(`_lens_git_dl(rr, *args, at_sha, "--", deadline=deadline)`)。
- 我在副本做了這個改動,清 `__pycache__` 後跑 `python3.14 scripts/test_lumos.py -k choice_kill_test_files_in_test_paths`,結果 `19 passed, 0 failed`。
- 缺口:測試只放了 `.kt`,沒有任何「測試路徑裡、含測試名、但不是該平台副檔名」的檔,例如 `feature/src/test/resources/cases.md`。此時改它會讓雜湊變、存活的行重跑,而 `_choice_test_blobs` 的說明寫的是「副檔名屬於那個平台」。
- 歸因:有證據的原有漏查(這段是修補新寫的,所以也算修補自帶的測試缺口)。修前沒有這個限定,無兩版可比。
引句:「副檔名由 git grep 的路徑樣式限定」
file: `scripts/lumos:77929`(`_choice_test_blobs`)

## 三問回答

**① 原問題的修復效果**
- H1(取到計劃筆記、子字串誤收、兩平台同名、查不到記不明標記):
  - 修後跑 `-k choice_kill_test_files_in_test_paths` 19 項全過。
  - `-k choice_kill_rerun_rules` 11 項過,`-k choice_kill_incremental` 6 項過(我跑到 99.5 秒,餘裕 2 倍)。
  - 我另對真 git 驗了 `git grep -z -o -w -F` 的輸出:格式是 `HEAD:路徑\0命中字`,`-o` 取最長命中,所以 `loads` 與 `loads data` 兩支各自找得到自己的行。
  - 修前:第一個含測試名的檔會是計劃筆記,作者的測試註解說明了這個翻紅釘。我沒另外在修前版本重跑這條。
- H2(推送前小結多選擇點那行):`-k lint_waive_choice` 4 項過,`-k gov_stats_choice_dedup` 4 項過,doctor 計數不含 `choice:`。
- H3(整批先掃、掃描與挑壞法分計時):`-k choice_scan` 9 項過,包含 1400 支小檔在時限內全判得到、掃描用光時限後掃完的檔仍判。批次與逐檔在正常暫存目錄下結果一致,見 c1 的第三行輸出。
- H4(文件的回 3、回 2):`cmd_choice_points` 有檔算不出來時回 3、`_choice_kill_report` 在 `res.get("unverified")` 時回 2,與計劃相符。

**② 修補處的正常、錯誤與相鄰路徑**
- 逐檔退路:輸出超過 64MB 或逾時時改逐檔,`t_choice_scan_per_file` 通過。
- `_choice_tests_sha` 的新舊互讀:修前帳裡的雜湊若只含找到的檔,修後算出相同或不同,最壞多重跑一次;帶「?」的新雜湊與舊雜湊不等,所以也重跑。
- 推送端 `_choice_push_stale_tests` 遇到任一邊帶「?」就不誤報。
- `_choice_test_blobs` 的兩個呼叫端(choice-kill、推送前判定)都已換成新簽名,`_choice_tests_sha` 只有這兩處呼叫。
- 以下是設計上的取捨,不算 finding:
  - 測試放在 `_choice_is_test` 認不出的路徑(例如 `src/e2e/`)時,每次都標「?」、存活行每次重跑。
  - 測試名含中文時 git 的 `-w` 不擋子字串,只會多收檔、多重跑。

**③ 新發現在修前、修後各是什麼**
- c1:修前 1/1、修後 0/0(見上)。
- c2:修前沒有這個限定、無可比;修後變異存活。

**未驗範圍**
- 真 Android 專案的端到端耗時。
- 整批輸出超過 64MB 退逐檔時,大量大檔的耗時。
- 條款 S1–S26 逐條對照:這輪只看了與修補相關的 S11、S13、S19、S22 與文件回報碼。

## 圖譜鏡頭
這次沒附固定席節點。依 diff 自己判:
- 改動只動 `scripts/lumos` 的選擇點掃描與測試雜湊、`lint-waive` 提示句、推送小結一行,以及對應文件與測試。
- 對 `Systems/規格閘`、`Projects/改動選擇點都要有需求守住_計劃` 的合約沒有破壞:S11 的雜湊語意更嚴(只多跑不漏),S19 的退逐檔語意保留。

## 角色鏡頭(後端卡)
- be-api-compat:對外 API 無改動。治理帳事件的 `tests` 欄由 `[名, 物件編號]` 改成 `[平台, 名, 物件編號]`,但沒有讀取端拆這個欄位,`tests` 也不在 `_GOV_FIELD_TYPES` 型別表裡。
- be-authz:沒有新增或改動端點,不適用。

最嚴重:minor;blocking 共 0 條
