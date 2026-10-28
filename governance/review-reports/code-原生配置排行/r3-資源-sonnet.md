severity: minor

我只用合成資料在 SQLite CLI 3.53.4 上量查詢,沒有在真機或真 trace_processor 上跑。收集腳本的時間預算和收錄製順序,我是逐行讀程式判斷的,沒有實際執行。

## Findings

1. 查詢加了 having 後,留著的呼叫點仍然「葉數 × 呼叫深度」地展開,大錄檔下記憶體近 GB 級
severity: minor
blocking: 否 判準:後果是 trace_processor 被系統殺掉或被 T_LONG 砍掉,整段寫成 failed(只提醒,不擋推送),不會做出錯的排行。
引句:「  having sum(size) != 0   -- 淨留量是 0 的呼叫點不影響任何加總,不往上走呼叫鏈(大錄檔省工)」
file: `scripts/templates/android-stability-native.sql:21`(遞迴 `walk` 在 `:24-27`,被 `fr2` 多處引用而整份物化)
歸因:有證據的原有漏查。`walk`/`fr2` 在修補前就存在,修補只擋掉淨留量為 0 的葉。
- 查證:我造了 10 萬個葉呼叫點、鏈深 60,每個葉配一筆分配和一筆釋放,用 SQLite CLI 量,指令是 `/usr/bin/time -l sqlite3 t.db < X.sql`。

| 情境 | 修前(無 having) | 修後(有 having) |
|---|---|---|
| 90% 的葉淨留量為 0 | 47.2 秒、最大常駐 2.17 GB | 4.5 秒、223 MB |
| 0% 的葉淨留量為 0 | 47.4 秒、2.18 GB | 47.3 秒、2.18 GB |

- 失敗場景:App 在量測結束時還有大量「活著」的原生配置呼叫點(沒被釋放的,不是配了又還的)。having 篩不掉它們,每個葉照樣沿呼叫鏈往上走到根。10 萬葉 × 深度 64 約 640 萬列,約 2.2 GB。外推到 30 萬葉 × 深度 100,約 3000 萬列,估計超過 10 GB,這是外推,我沒有實測。
- 後果:程式碼註解寫的「大錄檔省工」只對「大多被釋放」的錄檔成立。T_LONG 只管時間,不管記憶體,所以主機有被 OOM 殺掉的風險。⚠ 真實 heapprofd 錄檔的活著葉數與深度分布,我沒有實測資料。

## Manifest 15 條判定
- `collect.sh:263`(`open(...).read()`):誤報。CPython 立刻回收 handle,且沒有迴圈。
- `collect.sh:316`(`open(...).read()`):誤報,理由同上。
- `collect.sh:489`(`time.sleep(SETTLE)`):誤報。它在 `fresh_launch` 裡只睡一次,不是迴圈累積。
- `native.sql` 的 18、22、24、53、62、76、79、82、85、89、91、93 行共 12 條 N+1:全是誤報。它們是同一個查詢內的 CTE 和子查詢,不會在迴圈裡重複呼叫。真正的效能問題在上面第 1 條的遞迴展開,不是 N+1。

## 已驗主張與證據
- **收錄製順序**(`native_phase`):
  - `except Terminated: raise` 排在 `except Exception` 前面(`Terminated` 是 `Exception` 的子類,順序正確)。
  - 意外例外時改成先 `abort_record` 再 `state.pop`。收的那幾秒如果被 Terminated 打斷,`rec` 還留在 state,由 main 的 `cleanup` 重收。
  - 修補前先 `pop` 再收,在那個窗口被打斷時會漏收,修補後這個洞已補上。
  - `start_record` 一開頭就登記 state,`native_run` 在 `del state["rec"]` 之前,停錄與 `finally` 的 `rm` 都有涵蓋。
- **整組殺掉**:`run()` 用 `start_new_session` 開子程序,逾時和 `BaseException` 時整組 `kill_group`,並限制 `reap` 最多等 `REAP` 秒。driver 與 trace_processor 走同一條路。
- **截止時間**:
  - `end` 只在 main 讀一次。
  - 跑不跑的預估是 `2*elapsed+NATIVE_TAIL`,驅動截止是 `end-NATIVE_TAIL`,查詢截止是 `end-NATIVE_FINISH`,都以 `T_LONG` 封頂,下限 1 秒。
  - e2e 傳的是 `T_LONG`(預設 3600),與 e2e 自己的步驟逾時同值。查詢逾時後 kill 加 reap(最多 10 秒)仍落在 `end` 之前,約 5 秒餘裕。
  - 正常裝置下 `NATIVE_TAIL=120` 夠用。停錄(最多 30 秒加 `ps`)加拉檔(`T_SHORT`=120)最壞約 150 秒,超過 120 秒,此時查詢只剩 1 秒的下限、寫成 failed「逾時」。這要驅動剛好跑到截止才會發生,是邊角,我給不出具體場景,所以不單獨列為 finding。
- **查詢逾時訊息**:`native_query` 拿掉特例分支後,逾時的原因變成「trace_processor 算不了原生配置記帳:逾時(N 秒)」。我 grep 過,除了測試字串 `"逾時("`(`scripts/test_lumos.py:18834`)之外,沒有消費端比對舊字樣「查詢逾時」。
- **`scripts/lumos` 的 hunk**:`_macrobench_native_sites_err` 保證 `func`、`so`、`caller` 都是字串,所以新的 `_events_clean` 包裝不會 KeyError。

## 對照案例(repair / preserve)
- G1 時間上限、G2 收錄製順序:只做了上面的程式讀法核對,沒有實跑,結論是未判定。
- G4 查詢省工:
  - repair:量測如第 1 條表格。
  - preserve:`rows` 計的是 `heap_profile_allocation` 全表(`native.sql` 的 `select 'rows'`),不經過 `leaf`,所以「全部淨留量為零」不會誤判成「沒錄到」。
- G3、G5、G6、G7:未驗。這幾組屬測試與文件,不在我的鏡頭。

## 三問
1. **原問題的修復效果有何行為證據?**
   - 淨留量為零的葉:90% 為零時,時間從 47 秒降到 4.5 秒,記憶體從 2.17 GB 降到 223 MB。
   - 錄製收尾順序:程式讀法正確。
   - 其餘:沒有真機或實跑證據。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 成立。`Terminated` 繼續往上丟;意外例外照樣收掉錄製再寫 failed;沒設上限時 `left()` 回 `T_LONG`;`having` 不影響 `rows` 與 `stat` 兩種輸出。
3. **新發現的同一案例在修前、修後各是什麼結果?**
   - 第 1 條:0% 為零的葉時,修前修後都是 47 秒、2.18 GB,沒有惡化也沒有改善。
   - 90% 為零時,修前 47 秒、2.17 GB,修後 4.5 秒、223 MB,修補有效但不完整。

## 未驗範圍
- 沒有用真機、真的 heapprofd 錄檔和真 trace_processor 執行。
- 停錄與拉檔在慢 USB 下的實際耗時沒量。
- 測試檔的內容,以及固定席筆記(未附逐條的備援段)的逐條對應,都沒查。

最嚴重:minor,blocking 0 條。
