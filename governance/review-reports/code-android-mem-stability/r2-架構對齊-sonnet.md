severity: minor

三問都沒有 major。我沒找到引入第二種做法或跨層直呼的地方,只有 5 條命名或錯誤處理上的 minor。我只讀了 diff 和鄰居檔,沒有實跑任何東西。

## 問 1:分層與依賴方向

**lumos 本體沒有跑 adb 或 trace_processor。**
- `_macrobench_mode` 只讀 `stability.json`,不接裝置。`_macrobench_stability_load` 只做 `read_text` 與 `json.loads`。
- 呼叫 adb、trace_processor、java_heap_dump 的全在範本 `android-stability-collect.sh`。這跟 `_macrobench_mode` 既有的「不跑 Gradle、不接裝置」同向。
- 對照:`scripts/lumos:39369`(`_macrobench_num`)、`scripts/templates/android-receipt-rerun.sh:11`(rerun 只靠 `TP` 找 trace_processor)。

**範本沒有碰 lumos 的內部函式,但多了一條反向依賴。**
- 收集腳本用相對路徑 `../lumos` 叫 `macrobench --check-config`,走的是公開子命令,不是內部符號。
- 鄰居 `android-receipt-rerun.sh` 完全不依賴 lumos,這是範本層第一次依賴 lumos 本體。
- 範本自己的 `declared_classes()` 另外解析門檻檔、挑出 `check == "instances"` 的 `class`。這等於在範本裡再知道一次 lumos 門檻檔的欄位形狀。

不對齊(minor):
severity: minor
blocking: 否
引句:「rc, out, err = run([sys.executable, lumos, "macrobench", "--repo", root, "--check-config"])」
佐證 file: `scripts/templates/android-receipt-rerun.sh:11`(鄰居範本零 lumos 依賴;收集腳本另加 `declared_classes` 重讀門檻檔)

⚠ 這條我判成 minor,因為依賴的是公開子命令,而且驗證交給 lumos 做,沒有另寫一套驗證器。要不要算「範本反向依賴 lumos」請編排者裁。

## 問 2:命名與錯誤處理

**跟鄰居一致的部分:**
- 函式前綴:`_macrobench_*`(`_macrobench_stab_*`、`_macrobench_check_*`)、常數 `MACROBENCH_*`,跟既有 `_macrobench_threshold_item_err`、`MACROBENCH_THRESHOLD_REQUIRED` 同款。
- 錯誤訊息:兩邊都回「錯誤訊息或 None」,lumos 端印 `擋下:` 後回 2,範本的 `die()` 也是印 `擋下:` 後 `sys.exit(2)`,跟 rerun 一樣印到 stderr。
- 日期:`_macrobench_date_ok` 先用 `DATE_RE` 再交 `_rule_date`,並把原本 `_macrobench_threshold_item_err` 裡自寫的日期判法(`re.fullmatch` 加 `fromisoformat`)換掉,是往專案慣例收斂。
- 整數與數字:用 `_secev_int` 與 `_macrobench_num`,沒另寫。
- 套件名:`MACROBENCH_PKG_RE` 的規則跟 `skills/lumos-android-evidence/SKILL.md:53`(英數字、底線、點)一樣。
- SQL:兩支 SQL 都用 `__PROCESS__` 佔位、只用標準 SQLite、註解不以分號結尾。我 grep 過新增的 SQL 與 sh 檔,沒有以分號結尾的註解行。第一欄當鍵(`'cycle'`、`class`)的做法也跟 `android-ui-attribution.sql` 的 `frame` 一致。

**不一致的三處:**

**(a) Python 版本下限。**
- 鄰居 rerun 的下限是 python3.7(`skills/lumos-android-evidence/reference.md:87`)。
- 收集腳本用 `python3 -P`(3.11 起才有),下限是 3.11(`reference.md:116`,有明寫)。
- 腳本沒有版本檢查。系統 python3 是 3.9 時只會噴「unknown option -P」,沒有「擋下:」訊息。
- `str.removeprefix`(3.9 起)也在同一支腳本。

severity: minor
blocking: 否
引句:「exec env PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python3 -P - "$HERE" "$(pwd)" "${1:-}" <<'PY'」
佐證 file: `scripts/templates/android-receipt-rerun.sh:11`(鄰居用 `python3 -`、下限 3.7)

**(b) 環境變數命名。**
- 新增三個變數 `LUMOS_STABILITY_LONG_S`、`LUMOS_STABILITY_SETTLE_S`、`LUMOS_STABILITY_STOP_WAIT_S` 用 `_S` 單位尾碼。
- 專案裡同類的逾時變數是 `LUMOS_TTY_TIMEOUT`、`LUMOS_TEST_TIMEOUT`,用 `_TIMEOUT` 尾碼,預設值寫在說明裡。
- 這三個也沒在腳本檔頭「外部工具」那行列出來,rerun 的檔頭至少列了 `TP`。

severity: minor
blocking: 否
引句:「T_LONG = float(os.environ.get("LUMOS_STABILITY_LONG_S", "1800"))」
佐證 file: `scripts/lumos:33578`(`LUMOS_TTY_TIMEOUT`)、`scripts/lumos:62500`(`LUMOS_TEST_TIMEOUT`)

**(c) 輸出欄位與印法。**
- 既有的 `_macrobench_print_thresholds` 只印沒達和沒判,達標的只算條數。
- 新增 `[達標]` 逐條明細,只對 `frozen`、`exits` 兩種 check 印,這是第一次有逐條印達標。
- check 條目的記錄欄位是 `scenario/check/contract`,不帶舊條目的 `metric/stat`。同一個 `threshold_*` 清單裡有兩種形狀,印的地方用 `"check" in r` 分岔。

severity: minor
blocking: 否
引句:「print(f"  [達標] {r['scenario']} {r['check']}:{_macrobench_stab_detail(r)}")」
佐證 file: `scripts/lumos:40060`(同函式既有的 `[沒達驗收門檻]`、`[沒判]` 分支)

## 問 3:第二種做法

**找工具:**
- 鄰居 rerun 是用 `TP` 直接執行,碰到 `OSError` 才印「擋下:」。
- 收集腳本在 `preflight` 先用 `shutil.which` 擋一次,`run()` 裡又有一套 `OSError` 處理,同一支腳本有兩套。
- lumos 本體還有 `_py_which`(會擋 PATH 裡的相對路徑項與 cwd 同名檔)。範本是獨立的 python 外殼,不能直接引用,所以我只列這條 minor,沒升 major。

severity: minor
blocking: 否
引句:「die(f"找不到 {tool};用環境變數 ADB=、TP= 指定")」
佐證 file: `scripts/templates/android-receipt-rerun.sh:59`(鄰居用 `except OSError` 加「擋下:」)、`scripts/lumos:117`(`_py_which`)

**沒有第二種做法的部分:**
- 日期、整數、數字驗證都共用既有函式,沒有另寫。
- 子程序收尾:範本裡的 `kill_group` 跟 `scripts/lumos:25519` 的 `_kill_proc_group` 同一套(`start_new_session` 加 `os.killpg(pid, SIGKILL)`,找不到就殺直接子程序),只是範本只攔 `OSError`。範本是 POSIX 的 sh,所以不列。
- 訊號處理(SIGTERM 轉例外)是範本專有的需求,lumos 本體沒有鄰居要比。
- 輸出解析(trace_processor 的 CSV 行、以 `"` 開頭)沿用 rerun 的作法。
- `.pbtxt` 是 `scripts/templates/` 裡第一種新檔型,佔位多了 `__DURATION_MS__`,同層沒有鄰居可比,不列。

不對齊共 5 條,其中 major 0 條
