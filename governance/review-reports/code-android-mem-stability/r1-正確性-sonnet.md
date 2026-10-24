severity: major

本席預設程式會壞,找到 3 個 major、3 個 minor。每條都用假 adb、trace_processor 和驅動(照 `_ms_collect` 的做法,檔案在 `/tmp/lumos-seat-work/code-android-mem-stability/正確性-sonnet/`)或直接餵結果檔實跑過。表態記錄裡 py-* 的 na 與本席判定無關,沒有追。後端卡 be-api-compat、be-authz 對不上:這份改動只有命令列工具、收集腳本和 SQL 範本,沒有對外端點和 API 欄位,所以沒有對應發現。

## 發現

### 1. App 崩潰後沒被重啟時,exits 檢查被列成「沒判」,崩潰記錄等於被丟掉(計劃 S5、S19)
severity: major
blocking: 是
引句:「p, why = _ms_src(stab, "pids")」

`_ms_exits` 要求 pids 來源是 ok 才肯判。收集腳本的 pids 只要有一次 `pidof` 沒讀到,就整個記成 failed。App 在量測輪中崩潰且沒被重啟,是最常見的崩潰形態,這時第三次 pid 讀不到,exits 其實已經記到 crash,卻不會被判。第一次 pid 在 `monkey` 啟動後只等固定 2 秒,冷啟動慢的裝置會讀到空,同樣讓 exits 永遠「沒判」。S11 寫的是 exits 與 strictmode 在 driver 失敗時照判,理由正是「崩潰時驅動一定失敗,這時正是 exits 該判不過的時候」。S19 實驗室只測到「崩潰後被重啟、pid 變了」這一種,沒測到不重啟。

重現:
- 命令:`python3.14 t1.py`,接著用只有 exits 一條的門檻檔跑 `lumos macrobench --repo <暫存專案> --stability .../stability.json`。
- 輸入:`exit_after` 帶一筆 `reason=4 (APP CRASH(EXCEPTION))`,`pids=("100","100","")`。
- 預期:`[沒達驗收門檻] pkg.Leak#cycle exits:crash`。
- 實際:結果檔 exits 是 `{"status":"ok","new":[{"type":"crash",...}]}`,但 pids 是 failed。判定輸出是「0 條沒達、0 條達標、1 條沒判」,以及 `[沒判] pkg.Leak#cycle exits:pids 沒收到(failed):有一次讀不到 pid(App 不在了)`。

修法方向:`_ms_exits` 在 pids 不是 ok 時,仍要判 exits 裡的壞類型,只把 pid 變化這一項當作無法判;或收集腳本不要因為單次讀不到就整個丟掉已讀到的 pid。

### 2. 驅動沒有成功結束的幾種輸出會被記成 ok,量測輪沒跑完其他數字照樣全綠(計劃 S16)
severity: major
blocking: 是
引句:「if "INSTRUMENTATION_CODE" in text and ("INSTRUMENTATION_CODE: -1" not in text or "FAILURES!!!" in text):」

S16 的字面是「UI Automator 輸出沒有 `INSTRUMENTATION_CODE: -1` 就記 failed」。程式只在輸出裡已經有 `INSTRUMENTATION_CODE` 時才檢查,完全沒有這個字就當成功。計劃自己寫了「`am instrument -w` 失敗時回傳碼照樣可能是 0」,所以只靠 rc 擋不住。

重現:`python3.14 t4.py`,驅動 rc 0,輸出分別是下列三種,結果檔 `driver.status` 全是 `ok`:
- `INSTRUMENTATION_FAILED: com.lab.test/androidx.test.runner.AndroidJUnitRunner`
- `INSTRUMENTATION_RESULT: shortMsg=Process crashed.`
- `INSTRUMENTATION_ABORTED: System has crashed.`

預期這三種都是 `failed`,需要完整 N 輪的五種檢查全部跳過。實際全部被當成跑完 N 輪。這正是設計審 r2 想堵的「UI 沒跑完、其他數字全綠」。程式分不出驅動是 UI Automator 還是 Maestro,修法方向是輸出裡出現任何 `INSTRUMENTATION_` 開頭的行,就要求有 `INSTRUMENTATION_CODE: -1`,或把驅動種類寫進設定。

### 3. 快照是空的也被當成有資料,java_growth 空轉判「通過」(計劃 S11)
severity: major
blocking: 是
引句:「if not all(_ms_val(v) is not None for v in [*b.values(), *a.values()]):」

收集腳本的 `heap_counts` 對 trace_processor 回 0 列(例如快照檔存在但沒有 Java 堆積圖,或行程名對不上)不報錯,回傳 `{}`。結果檔因此是 `heap: ok, before: {}, after: {}`。`_ms_heap` 的檢查是對空集合取 `all()`,恆為真,空資料就過關了。S11 要求「欄位缺或值不可用時不得列成通過」。

重現:`python3.14 t2.py`,`test_data` 已宣告,`heap=({}, {})`,門檻檔有 java_growth 和 instances 各一條。
- 預期:兩條都是「沒判」,理由是快照沒有任何物件。
- 實際:`0 條沒達、1 條達標、1 條沒判`,java_growth 通過。instances 剛好因為類別物件也找不到而跳過,但 java_growth 沒有同樣的保護。

修法方向:收集腳本在任一份快照的 counts 為空時把 heap 記成 failed,判定端也要拒絕空的 before 或 after。

### 4. 有 R8 mapping 時 `java.lang.Class<混淆名>` 沒有被還原,「類別物件佐證」失效(計劃 S3)
severity: minor
blocking: 否
引句:「name = mapping.get(base, base) + arr」

`heap_counts` 用 `mapping.get(base, base)` 只還原整個名字。類別物件在快照裡叫 `java.lang.Class<a.b>`,尖括號裡的混淆名沒有還原。收集腳本又用原名拼出 `java.lang.Class<com.sdk.Player>` 當「宣告類別」去保留,兩邊對不上,這筆被當成沒變動的類別丟掉。結果是有 mapping 的專案,SDK 物件被全部釋放(0 個實例)時,instances 永遠進不了「0 個、通過」,只會「沒判」,而且訊息說「可能拼錯或被混淆」,方向是錯的。

重現:`python3.14 t3.py`。
- 輸入:`mapping.txt` 寫 `com.sdk.Player -> a.b:`,兩份快照都只有 `java.lang.Class<a.b>` 與 `a.c`,門檻檔 instances 類別寫 `com.sdk.Player`、max 0。
- 預期:算 0 個、通過。
- 實際:結果檔 `heap.before` 與 `after` 都是 `{}`,判定是 `[沒判] ... 兩份快照都沒有它的實例也沒有它的類別物件(類別名拼錯或被混淆?)`。

### 5. 結果檔欄位缺時,exits 與 strictmode 判成通過(計劃 S11)
severity: minor
blocking: 否
引句:「new = [e for e in s.get("new", []) if isinstance(e, dict)]」

`_ms_exits` 的 `new`、`_ms_strictmode` 的 `violations`、pids 的 `values` 都用 `.get(…, 預設空)`。來源 status 是 ok 但欄位缺時,等於「零筆」,直接通過。S11 要求欄位缺要「跳過並說原因,不得列成通過」。收集腳本自己一定會寫這些欄位,所以只有手改或舊版格式的結果檔會碰到。

重現:結果檔 `{"scenario":"s","exits":{"status":"ok"},"pids":{"status":"ok"},"strictmode":{"status":"ok"}}`,門檻檔有 exits 與 strictmode 各一條。
- 預期:兩條都是沒判。
- 實際:`2 條達標`,並印 `[達標] s exits:只有 0 筆其他原因的結束紀錄`。

### 6. 兩個設定錯誤走出 traceback 與 rc 1,不是計劃寫的 rc 2「擋下」
severity: minor
blocking: 否
引句:「if st.get("category", "app") not in MACROBENCH_VITALS_FG:」

- `category` 寫成清單時,`list in dict` 丟 TypeError。命令 `lumos macrobench --repo e --check-config` 實際印 `TypeError: cannot use 'list' as a dict key (unhashable type: 'list')`,應該是 rc 2 加驗證訊息。
- 同形狀的鄰近路徑 `_ms_peak_vitals` 對 `stab.get("category")` 也一樣不防,結果檔寫壞時會丟例外。
- 計劃 S14 的設定檢查與收集腳本註解都寫「設定讀不了回 2 並印擋下:」。收集腳本的 `load_mapping` 對不存在的 mapping 路徑沒有攔,重現:`python3.14 t3.py` 後半段,收集腳本以 rc 1 結束,印 `FileNotFoundError ... nope.txt`,沒寫結果檔。
- 這個錯誤發生在動裝置之前,所以不會留下裝置暫存。

## 資料狀態五問
- **新舊格式互讀**:沒寫 check 的舊門檻條目維持舊判定。結果檔缺欄位的問題見第 5 條。
- **寫一半**:中途出例外時,`abort_record` 會停掉裝置上的 perfetto 並刪暫存。出例外時舊的同名 `stability.json` 會原樣留著,這只在手動指定重複 run-id 時才碰得到,我沒當成發現。
- **時間**:7 天刪除只動 `heap-*.pftrace`,符號連結的處理和測試相符。`logcat -T` 的起點截到整秒,最多多收量測前不到 1 秒的日誌,我判成不值得列。
- **不可逆**:沒找到可以刪到別處的路徑。
- **StrictMode 日誌解析**:照 AOSP 的 `sLogger` 格式(執行緒與 VM 兩種都含 `StrictMode policy violation`),沒有發現算錯。

## 其他
本席的臨時目錄 `/tmp/lumos-seat-work/code-android-mem-stability/正確性-sonnet/`(含 `src/`、`memseat-*`、`e/`、`h.py`、`t1.py` 到 `t4.py`)留給編排者收貨後刪。我沒有動 adb 連著的裝置,也沒有在 android-mem-stability 工作樹動手。

最嚴重 major,blocking 共 3 條。
