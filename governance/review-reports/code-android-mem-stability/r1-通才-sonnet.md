severity: major

通才席(測試品質)報告,範圍為 r1-snapshot-tests-docs.patch。能實跑的都做了翻紅檢查。

方法:把 scripts/ 複製到 `/tmp/lumos-seat-work/code-android-mem-stability/通才-sonnet/`,各改壞一處,清 `__pycache__` 後跑 `python3.14 scripts/test_lumos.py -k <關鍵字>`。結果:

- 全套 `-k android_memstab` 基準 164 案例全綠。
- 改壞後仍全綠的有 7 處:拿掉 `lc_died`、拿掉 `-T t0`、拿掉 `islink(base)`、`abort_record` 改成 pass、java_growth 的 `n` 寫死 5、vitals 後兩級與 game 第三級改成 9.99、exit_diff 只比 pid。
- 改壞後仍全綠的另有 2 處:拿掉 `block is not None`、`perfetto_alive` 不比 pid。
- 拿掉 `time.sleep(2)` 有翻紅,所以「日誌串流等兩秒」那條有守住。
- 我留下一份紅的現場 `gctl-run-epxfrs92`,已用字面路徑刪掉。臨時目錄 `/tmp/lumos-seat-work/code-android-mem-stability/通才-sonnet/` 留給編排者收貨後刪。

### 1. 收集腳本「日誌串流中途斷了」的分支沒有任何測試走得到,實機斷線時 strictmode 會假通過
severity: major
blocking: 是
引句:「if a[0] == "logcat":」
假 adb 的 logcat 寫完內容就 `time.sleep(60)`,從不提早結束,所以收集腳本的 `lc_died` 判斷在測試裡永遠是 False。
- 情境:`adb logcat` 一啟動就退出(裝置斷線、`--pid` 無效)。
- 預期:`strictmode.status` 為 `failed`,門檻判成跳過。
- 實際:`lc_died` 的判斷不被任何測試覆蓋,若壞了會得到 `{"status": "ok", "violations": []}`,門檻判成通過,等於漏抓違規卻放行。
- 翻紅檢查:把 `lc_died = lc is not None and lc.poll() is not None` 改成 `lc_died = False`,164 案例全綠。
- 計劃 S7 寫「日誌串流中斷使 status 為 failed 時列成跳過」,綁的 `t_android_memstab_strictmode` 只測 lumos 端吃一個手寫的 failed,收集端從沒產生過 failed。
- 修法:假 adb 加一個旗標讓 logcat 立刻 exit 1,斷言 `strictmode.status == "failed"`。
- file: `scripts/templates/android-stability-collect.sh:301` 附近(程式包第 14 區塊的 `elif lc is None or lc_died:`)。

### 2. 「只收量測開始之後的日誌」沒有任何斷言,拿掉 `-T t0` 測試照綠
severity: major
blocking: 是
引句:「收集腳本只收量測開始之後的日誌、一筆違規只算一次」
S7 條款綁在 `t_android_memstab_strictmode`,那支測試只測 lumos 端。收集端的 `-T t0` 在假 adb 裡被整個忽略,`t_android_memstab_collect_driver_status` 也沒檢查 adb.log 有帶 `-T`。
- 翻紅檢查:把 `"-T", t0, ` 從 logcat 指令移除,`-k collect_driver_status` 11 案例全綠。
- 實機情境:暖機輪與量測輪是同一個 pid。拿掉 `-T` 後 logcat 會倒出暖機期間的 StrictMode 違規,被算進量測期,洩漏門檻誤判沒過。
- 修法:在 adb.log 斷言有 `logcat --pid=100 -T 03:00:00.000`;並讓假 logcat 依 `-T` 過濾,放一筆更早的違規,斷言不被計入。

### 3. 「產物目錄本身是捷徑就不刪」的守衛沒有測試,拿掉照綠
severity: major
blocking: 是
引句:「(base / "linked").symlink_to(elsewhere, target_is_directory=True)」
測試只造了「`android/` 底下的子項是捷徑」,而 `prune_old_snapshots` 有兩道不同的守衛。
- 子項守衛 `os.path.islink(p)`:測試有覆蓋。
- 根守衛 `if os.path.islink(base): return`:沒有覆蓋。
- 翻紅檢查:拿掉根守衛,`-k android_memstab` 164 案例全綠。
- 情境:`.lumos/artifacts/android` 本身是指向專案外的捷徑,裡面有超過 7 天的 `<run>/heap-*.pftrace`。預期不刪,守衛壞了會刪到專案外。
- 知識圖譜把這條當 WHY 綁定 `t_android_memstab_collect_test_data_gate`(「遇到捷徑(symlink)的目錄或檔就跳過」),綁定測試只守到一半。
- 修法:加一組 `base` 自己是捷徑的案例,斷言外面的舊檔還在。

### 4. peak_vitals 只驗了前三級與 game 第一二級,後兩級與分級上界沒有預期值
severity: minor
blocking: 否
引句:「(6799, "app", 2.25 * GB, "threshold_passed"),」
- app 的 3.25、4.25 GB 與 game 的 3.50、4.00、5.00 GB 從未被斷言;9216、14336、18432 的邊界也沒有案例。
- 翻紅檢查:把 `MACROBENCH_VITALS_FG` 改成 `(2.00, 2.25, 2.25, 9.99, 9.99)` 與 `(2.25, 2.75, 9.99, 9.99, 9.99)`,全綠。
- 6799、6800 這一對對 app 有部分失效:兩邊上限都是 2.25,只擋得住「下界含」,擋不住「上界不含」被改成含。
- 情境:12 GB 平板(如 12288 MB)的 app 峰值 3.3 GB,預期沒過,表若被抄錯就判通過。
- 修法:每一級各補一個剛好等於、與一個超過 1 KB 的案例,game 的 6800 與 9216 邊界也補上。

### 5. S11 迴圈裡有一個被 `continue` 掉的死條目,max_main_block_ms 缺值的情境根本沒測
severity: minor
blocking: 否
引句:「("cycle_trace", {"status": "ok", "frozen_frames": 0, "frames": 600}, "frozen_trace_missing_block_ok"),」
該條目緊接著被 `if chk == "frozen_trace_missing_block_ok":` 的 `continue` 跳過,什麼都沒驗。
- 它想守的情境是:追蹤檔沒有主執行緒區段時,SQL 會輸出 -1,`_ms_val` 變 None,設了 `max_block_ms` 時必須靠 `block is not None` 才不炸。
- 翻紅檢查:拿掉 `block is not None and`,`-k frozen_frame` 4 案例全綠。實際會拋 TypeError 並丟 traceback,而不是印判定。
- S11 文字寫「值是 -1 …… 跳過不通過」,frozen 這條沒有 -1 的案例。
- 修法:刪掉死條目,改成 frozen 的真案例(`max_main_block_ms: -1` 加 `max_block_ms=500`,預期通過且不出例外)。

### 6. exit-info 前後比對「pid 加 timestamp」的複合鍵沒有被任何案例區分
severity: minor
blocking: 否
引句:「應只留下後一份多出來的那幾筆(用 pid 加 timestamp 比)」
`t_android_memstab_exit_info_diff` 的新舊紀錄 pid 都不同(90 對 100 到 105)。
- 翻紅檢查:把比對鍵改成只看 pid,`-k exit_info_diff` 7 案例全綠。
- 情境:裝置對同一 pid 先後留下兩筆紀錄(pid 重用),後一筆被誤判成舊的,量測期的崩潰漏報。
- 修法:舊紀錄放 pid=100 加舊 timestamp,新紀錄放同 pid 加新 timestamp,斷言要算進去。

### 7. 假 adb 的 `ps` 不看 pid,收集腳本「用 ps 判斷錄製還活著」的 pid 比對沒被驗
severity: minor
blocking: 否
引句:「elif c.startswith("ps -A"):」
假 adb 對任何 `ps -A ...` 都印 `4321 perfetto`,真實指令是 `ps -A -o PID,NAME | grep -w <pid>`。
- 翻紅檢查:把 `perfetto_alive` 的 `any(line.split()[:1] == [pid] ...)` 換成 `bool(out.strip())`,`-k collect_record_alive` 4 案例全綠。
- 情境:實機上別的行程出現在 `ps` 輸出時,錄製早已結束卻被判成還活著。
- 修法:假 ps 依指令裡的 pid 過濾輸出,並加一個 pid 不符、輸出有別的行的案例。

### 8. 新增測試子集約 2 分鐘,主因是收集腳本的固定睡眠與每案重複跑兩次 lumos
severity: minor
blocking: 否
引句:「return root, r, d, _mb_run(root, "--stability", str(sp))」
- `_ms_collect` 在腳本裡有 `time.sleep(2)`(monkey 之後)加 `time.sleep(2)`(logcat 收尾),每次至少 4 秒。測試呼叫它 16 次。
- 實測最慢的四支:collect_driver_status 35.9 秒、collect_test_data_gate 31.2 秒、exit_info_diff 23.8 秒、collect_record_alive 17.3 秒。
- `_ms_root` 每案固定跑兩次 lumos(`--json` 與文字),多數測試只用第一次的結果;`peak_vitals_floor` 因此要 12.9 秒。
- 代價:`-k android_memstab` 一次約 2 分鐘,而全套約 8 分鐘,推送前閘約多了 25%。
- 修法:收集腳本的兩段睡眠改成可用環境變數縮短(測試設 0.1 秒);`_ms_root` 的文字輸出改成按需才跑。
- file: `scripts/templates/android-stability-collect.sh:261` 附近(`time.sleep(2)` 兩處)。

### 9. run-id 測試的環境變數拼錯,且為了拿假工具目錄多跑了一次完整收集
severity: minor
blocking: 否
引句:「JAVA_HEAD_DUMP=str(fake0 / "jhd")」
- 腳本讀的是 `JAVA_HEAP_DUMP`,測試寫成 `JAVA_HEAD_DUMP`,拼錯。目前不出事,因為 run-id 檢查在最前面就 `die`、測試也沒宣告 test_data,所以這個變數根本用不到。
- 但要是有人把檢查順序挪後,測試會改打到真的 `java_heap_dump`。
- 為了拿到 `fake0` 還多跑一次完整 `_ms_collect(...)`(約 4 秒)。
- 修法:改正拼字;直接在 `td` 下建假工具,不用先跑一次收集。

最嚴重 severity: major,blocking 共 3 條。
