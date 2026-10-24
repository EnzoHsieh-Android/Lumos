severity: major

# 資源席報告:android-stability-collect.sh 與相關查詢

先講結論:收集腳本一被 SIGTERM 就丟下孤兒,這是主要問題。查詢裡的二次方工作和幾個時間預算是次要的。

我用測試裡的假 adb、假 trace_processor 和假 java_heap_dump,在 `/tmp/lumos-seat-work/code-android-mem-stability/資源-sonnet/` 實跑。沒碰任何 adb 連著的裝置。實驗用的臨時目錄、孤兒程序都已自己清掉。

## 收集腳本被 SIGTERM 終止時,裝置上的錄製、logcat 串流與驅動都沒收掉
severity: major
blocking: 是

引句:「        if not finished:」

- **場景**:AI 全權依序操作,外層逾時或 `kill` 預設送 SIGTERM。收集腳本進入量測區(`start_record`、logcat Popen、`driver(n)` 之後)時收到 SIGTERM,Python 預設直接結束,`finally` 不會跑。
- **預期**:`abort_record` 把裝置上的 perfetto 收掉並刪暫存,logcat 串流也停掉。
- **實際**(命令:用 `kill -TERM` 對收集腳本主程序送訊號,量測中,驅動為 `sleep 25`):
  - `adb.log` 最後一行停在 `logcat --pid=100 ...`。沒有 `kill -TERM`,也沒有 `rm -f`。
  - 裝置上的 perfetto 沒被通知停,設定檔與追蹤檔留在 `/data/misc/perfetto-*`。它會一直錄到 `duration_ms`(預設 600 秒)才自己結束。
  - 主機端 `ps` 顯示 `adb logcat` 與驅動的 `sleep 25` 兩個孤兒,ppid 都是 1,各存活 15 秒以上,之後我手動殺掉。
- **相關位置**:`except`/`finally` 只防得了 KeyboardInterrupt 與一般例外。`abort_record` 的觸發條件是 `finished` 為假,而 `finally` 本身就不會被 SIGTERM 觸發。
- **另一個窗口**:`start_record` 之後、進 `try` 之前,有 `open(log_path)` 和 `subprocess.Popen([ADB,"logcat"...])`。這段若拋例外(例如 adb 在這一刻消失),`rec` 也沒人收。
- **另一個窗口**:`stop_record` 的 30 秒等待迴圈中被中斷,perfetto 已被 TERM,但 `rm -f remote_cfg remote_trace` 在迴圈之後,所以裝置暫存檔會留下。
- **建議**:
  - 註冊 `signal.signal(SIGTERM, ...)` 轉成例外,或把整段包進單一 try/finally。
  - Popen 與 start_record 放進同一個 try。
  - 把 `rm -f` 放進 `finally`。

## 驅動逾時只殺 `sh -c` 本身,驅動底下的子程序變孤兒,裝置上的 instrumentation 也沒停
severity: minor
blocking: 否

引句:「    rc, out, err = run(["sh", "-c", cmd.replace("{{CYCLES}}", str(n))], timeout=T_LONG, env=env)」

- **實跑**:把 `T_LONG` 在副本改成 3 秒,驅動設成 `(sleep 20 &) ; sleep 20`。
  - 腳本約 11.6 秒結束,沒有卡住。`subprocess.run` 在 Python 3.14 不會無限等管線。
  - 結果檔正確寫出 `driver failed:逾時(3 秒)`。
  - 但四個 `sleep 20` 孤兒留在主機上,手動殺掉。
- **後果**:真實驅動(`adb shell am instrument ...`、多指令腳本)逾時後,`subprocess.run` 只殺了 sh 或 adb 客戶端。裝置上的 instrumentation 仍在跑,逾時之後還會跟後續的 `unreachable` 與快照搶同一個 App。
- **建議**:`Popen(start_new_session=True)`,逾時時 `os.killpg`。

## `max_record_s` 調大時,cycle.sql 的 peak 子查詢是二次方
severity: minor
blocking: 否

引句:「  SELECT MAX(a.value + COALESCE((SELECT s.value FROM swp s WHERE s.ts <= a.ts ORDER BY s.ts DESC LIMIT 1), 0)) AS v FROM anon a」

- **實跑**:用 Python 內建 sqlite3 建同名表(`counter` 沒索引,取樣間隔 250ms,anon 與 swap 各 N 點),直接跑這支檔。

| N(約等於錄製長度) | 耗時 |
|---|---|
| 2400(10 分鐘,預設上限) | 0.52 秒 |
| 7200(30 分鐘) | 4.6 秒 |
| 14400(60 分鐘) | 18.7 秒 |
| 28800(2 小時) | 73.8 秒 |

- **判斷**:預設 600 秒沒問題。時間成長明顯是二次方(N 加倍、耗時約四倍)。
- **風險**:真的 trace_processor 比 sqlite3 慢數倍,`stability.max_record_s` 調到 1 小時以上時可能撞到 `T_LONG`(1800 秒)。撞到之後 `cycle_trace` 變 failed,peak_vitals 與 frozen 兩條門檻會被列成跳過。
- **建議**:改成對 `ts` 排序後的 asof join,或加註「max_record_s 不要超過 N」。

## `stop_record` 等錄製結束的 30 秒到了沒有強制收掉,還會刪掉仍在寫的檔
severity: minor
blocking: 否

引句:「    shell(f"rm -f {remote_cfg} {remote_trace}")」

- **場景**:裝置慢、64 MB 緩衝要沖寫,`perfetto_alive` 30 秒內還是真。
- **現況**:迴圈結束後直接 `adb pull`,拉到半截檔。隨後 `rm -f` 刪掉仍被寫入的檔(檔案描述符還開著,空間不釋放),但沒有 `kill -KILL`。
- **後果**:perfetto 繼續活到 `duration_ms`,最後回報「拉不回追蹤檔」之類。`alive` 變數是進迴圈前量的,這種情況會誤判成「錄製有跑完」。
- **建議**:迴圈逾時要補強制結束,並明確寫出原因。

## 次要觀察(未列為 finding)
- `adb pull` 用 `T_SHORT`(120 秒)。慢速無線 adb 拉 72 MB(兩個緩衝合計)可能逾時,拉失敗後 `rm -f` 把證據一併刪掉。
- 磁碟累積:`cycle.pftrace`、`logcat.txt`、`record.pbtxt` 不在 7 天清理範圍(只清 `heap-*.pftrace`)。
- 大檔記憶體:`heap_counts`、`load_mapping`、logcat 檢查都是逐行或只留聚合結果,沒有發現把整份大檔讀進記憶體的路徑。`heap_counts` 的 `capture_output` 只收 trace_processor 的 CSV 輸出,上萬個類別約數 MB。
- 表態記錄的 py-memory 與 py-hotpath 寫 na。這些是 `lumos` 內的聲明,收集腳本是另一個程序,不在這兩題範圍內,我未去反駁。

最嚴重 severity:major,blocking 共 1 條。
