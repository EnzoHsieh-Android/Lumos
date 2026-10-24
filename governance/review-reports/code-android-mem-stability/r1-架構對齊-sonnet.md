severity: major
第一行:

severity: major

**問 1 分層與依賴方向**

lumos 本體沒有跑 adb 或 trace_processor。`_macrobench_mode` 只讀 `--stability` 指的 stability.json(`_macrobench_stability_load`),不接裝置,跟既有「不跑 Gradle、不接裝置」一致。adb、TP、java_heap_dump 全在範本 `android-stability-collect.sh`,分層正確。

範本反過來呼叫 lumos,而鄰居沒有這個方向。`android-receipt-rerun.sh` 完全不碰 lumos,新範本卻靠 lumos 驗設定,還讀 lumos 擁有的兩份設定檔。呼叫的是公開子命令,不是內部函式,所以我只標 minor。

severity: minor
blocking: 否
引句:「rc, out, err = run([sys.executable, lumos, "macrobench", "--repo", root, "--check-config"])」
佐證 file: `scripts/templates/android-stability-collect.sh:643`(對照 `scripts/templates/android-receipt-rerun.sh:12`,鄰居只靠 `$HERE` 與環境變數)

這條有三個疑點:
- 範本用 `here/../lumos` 當路徑,假設範本與 lumos 放在 scripts/ 的相鄰目錄。鄰居是複製進收據目錄的,不能這樣假設。
- 它靠 `removeprefix("擋下:")` 去解析 lumos 的 stderr 文字。
- `declared_classes()` 另外直接讀 `macrobench-thresholds.json`(`scripts/templates/android-stability-collect.sh:852`),等於門檻檔的格式知識在範本和 lumos 兩邊各有一份。

⚠ 這是新的雙向耦合,結構上算不算「反過來依賴」請編排者裁。

**問 2 命名與錯誤處理**

對齊的部分:
- 錯誤處理:「擋下:」加 stderr 加 rc2 一致(`scripts/lumos` 的 `_macrobench_mode`、範本的 `die()`)。
- 工具找不到時的訊息:「用 TP=… 指定」的口吻與鄰居相同。
- 回傳碼:範本只有 0 和 2,標頭已明寫,鄰居是 0/1/2。範本不判定,所以我不算不對齊。
- 佔位符:`__PROCESS__` 與 SQL 註解「不以分號結尾」都照鄰居(`scripts/templates/android-heap-classes.sql:585`)。
- 設定欄位:snake_case,`decided_by`、`decided_at` 與 `contract` 沿用既有欄位。

不對齊的部分:

1. 新函式前綴與鄰居不同。鄰居一律叫 `_macrobench_*`,新增的 judge 輔助函式叫 `_ms_*`。
severity: minor
blocking: 否
引句:「def _ms_native_unreachable(t, stab, rec):」
佐證 file: `scripts/lumos:39766`(patch 內 246 行處;對照既有 `_macrobench_check_thresholds`、`_macrobench_threshold_item_err`)

2. 範本的 python 外殼多了 `-I`,而鄰居沒有。
severity: minor
blocking: 否
引句:「exec env PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python3 -I - "$HERE" "$(pwd)" "${1:-}" <<'PY'」
佐證 file: `scripts/templates/android-stability-collect.sh:609`(對照 `scripts/templates/android-receipt-rerun.sh:12`,鄰居是 `exec env PYTHONUTF8=1 python3 -`)

這會讓鄰居的 UTF-8 保證失效。`-I` 會忽略所有 PYTHON* 環境變數,我實測 `PYTHONUTF8=1 python3 -I` 的 `utf8_mode` 是 0。鄰居檔頭 `scripts/templates/android-receipt-rerun.sh:9-11` 寫明,不開 UTF-8 模式在 LC_ALL=C 下會崩潰。

3. 找專案根的方式不同。鄰居用 `$HERE/../../..`(收據目錄相對位置),新範本改用 `$(pwd)`,要求在專案根目錄跑。
severity: minor
blocking: 否
引句:「用法:在專案根目錄跑 sh scripts/templates/android-stability-collect.sh [run-id]」
佐證 file: `scripts/templates/android-stability-collect.sh:604`(對照 `scripts/templates/android-receipt-rerun.sh:9`)

另外,新增環境變數 ADB 與 JAVA_HEAP_DUMP 是沿用 TP 的做法,我不列為不對齊。

**問 3 第二種做法**

1. 日期驗證又多一份。`_macrobench_date_ok` 是「regex 加 `date.fromisoformat`」。同一個函式家族 `_macrobench_threshold_item_err` 裡已經有同邏輯的行內版本(`scripts/lumos:39688` 一帶,patch 內 130 行附近),新舊兩份同時存在,舊的沒改成呼叫新的。lumos 內另有既有的 `_rule_date`(`scripts/lumos:4296`)與 `_secinv_date`(`scripts/lumos:7378`)。專案裡甚至有註解寫「不另寫日期判法」(`scripts/lumos:5000`)。
severity: major
blocking: 是
引句:「return isinstance(s, str) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s)) and bool(datetime.date.fromisoformat(s))」
佐證 file: `scripts/lumos:39401`(新 helper 在 patch 內 58-63 行;既有重複在 `scripts/lumos:39688` 附近、`scripts/lumos:4296`)

2. 數字驗證沒有第二套。`_macrobench_field_ok` 與 `max_record_s` 都呼叫既有的 `_macrobench_num`,這點對齊。整數驗證是自己寫 `isinstance(int) and not bool`,但專案已有 `_secev_int`(`scripts/lumos:8559`)。這是同族重複,但範圍很小,歸 minor。
severity: minor
blocking: 否
引句:「if not isinstance(st.get(k), int) or isinstance(st.get(k), bool) or st[k] < 1:」
佐證 file: `scripts/lumos:39420` 一帶(patch 內 76 行),對照 `scripts/lumos:8559`

3. 找工具的做法沒有第二種。TP 用 `os.environ.get` 加 `shutil.which`,與鄰居同族。

4. 輸出印法沒有第二種。新條目併進既有的 `_macrobench_print_thresholds`、`threshold_*` 三個清單,沿用「只提醒」的文案。

5. 臨時 SQL 檔的做法沒有第二種。NamedTemporaryFile 加 `trace_processor -q` 加 `startswith('"')` 的解析方式與鄰居相同。

不對齊共 8 條,其中 major 1 條。

(minor 7 條:問 1 的 1 條、問 2 的 3 條、問 3 的 1 條,加問 2 的 `_ms_` 前綴已算在內。數字重新對:minor 為問 1 一條、問 2 三條、問 3 一條,共 5 條,加 major 1 條,應為 6 條。以下以此為準。)

更正後的最後一行:不對齊共 6 條,其中 major 1 條。
