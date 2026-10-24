severity: major

審查席:正確性(sonnet),第 2 輪。我預設這段程式會壞,實跑後找到 3 條。我逐 hunk 讀完 `r2-pkg-templates.patch`,跑了兩版的假工具場景(做法照 `_ms_prepare` 與 `_ms_collect_env`)。兩版是從 `1e47929e` 與 `44d93aba` 用 `git archive` 取出,沒動工作樹。圖譜鏡頭(`lumos dispatch-lens` 的固定席節點)我沒逐條判:列出的節點都屬於 `scripts/lumos` 與 `scripts/test_lumos.py` 的行為合約,而這包只動 `scripts/templates/` 的範本,我讀 diff 沒看到會碰到它們的地方。

## Finding 1:SIGTERM 落在 stop_logcat 的等待期間時,日誌串流行程變孤兒,修補只收了一半

引句:「    died = stop_logcat(state.pop("lc"))」
severity: major
blocking: 是

- **場景**:宣告了 strictmode,驅動剛跑完,腳本在 `stop_logcat` 的 `time.sleep(SETTLE)` 裡收到 SIGTERM。
- **預期**:`cleanup` 殺掉 `adb logcat`,對外印「裝置上的錄製與暫存已收掉」。
- **實際**:`state.pop("lc")` 在呼叫 `stop_logcat` 之前就把串流從 `state` 拿掉。`Terminated` 在 sleep 裡拋出時,`cleanup` 的 `state.get("lc")` 已是 None,殺不到它。`adb logcat` 變孤兒,繼續把整個行程的日誌寫進 `logcat.raw`。
- 同形狀的 `rec = state.pop("rec")` 之後才進 `stop_record`。**只靠讀碼、沒實跑**:`Terminated` 若落在 `kill -TERM` 送出之前,裝置上的 perfetto 沒被 `cleanup` 收,只有 `finally` 刪檔。
- **實跑**:假 adb 的 `logcat` 睡 60 秒,`LUMOS_STABILITY_SETTLE_S=6`,等驅動跑完後送 SIGTERM。
  - 腳本是 `sh <版本>/scripts/templates/android-stability-collect.sh runB`,環境與假工具照 `_ms_collect_env`。
  - 修後 `44d93aba`:rc=2,stderr 印「擋下:收集被中斷,裝置上的錄製與暫存已收掉,沒寫結果檔」,`ps` 仍看到 `adb logcat --pid=100 -T 10-24 03:00:00.000 -v brief` 活著。實驗後已手動殺掉。
  - 修前 `1e47929e`:rc=-15,同一條孤兒行程也在,完全沒有清理。
- **歸因**:有證據的原有漏查(修前整條中斷路徑都沒收),加上修補後同形狀鄰近路徑沒修。窗口是新程式碼引入的先 pop 後等待,但最終行為沒有比修前差。

## Finding 2:日誌串流斷線時,原始日誌檔 logcat.raw 沒刪

引句:「        return {"status": "failed", "reason": "日誌串流沒開成或中途斷了"}」
severity: minor
blocking: 否

- **場景**:strictmode 已宣告,`adb logcat` 一開就結束(裝置斷線、`--pid` 無效),或中途被中斷。
- **預期**:函式說明寫「只留違規那幾行落地,原始串流刪掉」,原始檔應刪。
- **實際**:`os.unlink(raw)` 只在 ok 分支(`if not started or died` 之後)。`died` 分支提前 return,中斷路徑的 `cleanup` 也不刪,`logcat.raw` 留在 `.lumos/artifacts/android/<run-id>/`。日誌常含帳號與權杖(函式說明自己這麼寫)。`prune_old_snapshots` 只刪 `heap-*.pftrace`,所以它不會被 7 天規則清掉。
- **實跑**:假 adb 讓 `logcat` 立刻 `exit 1`(`logcat_dies`)。
  - 修後:rc=0,`strictmode` 為 `failed`,目錄內容 `['cycle.pftrace', 'logcat.raw', 'record.pbtxt', 'stability.json']`。
  - 修前:改寫 `logcat.txt`(完整原始日誌落地,更糟)。我的場景在修前反而回 `strictmode: ok`,所以兩版行為不同,修前這條不能直接對比。
- **歸因**:有證據的原有漏查。修前整份日誌都落地,修補只收了 ok 分支,同形狀的失敗分支沒修。

## Finding 3:被中斷或擋下時,同一個 run-id 的舊 stability.json 留著,看起來像這次的結果

引句:「        print("擋下:收集被中斷,裝置上的錄製與暫存已收掉,沒寫結果檔", file=sys.stderr)」
severity: minor
blocking: 否

- **場景**:同一個 run-id 重跑,中途被 SIGTERM。
- **預期**:要嘛清掉舊結果檔,要嘛結果檔帶這一次的標記,下游不會把舊資料當新資料。
- **實際**:`run_dir` 是沿用的,舊的 `stability.json` 原封不動。實跑:先放 `{"stale":1}`,SIGTERM 後兩版都還在,`record.pbtxt` 也留下。stderr 說「沒寫結果檔」,但檔案其實存在。
- **歸因**:未判定(兩版行為相同,屬原有設計)。我沒驗 macrobench 讀檔端會不會因此誤判,所以不升級。

## 資料狀態五問(逐項回答)

- **新舊格式互讀**:`heap` 欄位修後把 `"mapping": bool` 換成 `"class_names": "mapping"|"raw"`。我沒驗 `lumos macrobench` 讀端是否還認舊欄位,**未判定**。
- **寫一半**:`stability.json` 是直接 `open("w")` 再 `json.dump`,不是暫存後換名。SIGTERM 落在寫檔瞬間會留半份,窗口極小,我沒實跑。裝置暫存靠 `finally` 與 `abort_record` 刪,見 Finding 1 的缺口。
- **衍生資料**:類別名還原遞迴處理 `java.lang.Class<…>` 與陣列後綴,我讀碼沒找到錯。CSV 解析在類別名含逗號時有補救,類別名含雙引號時我沒測。
- **時間**:7 天刪除用 mtime 且只動 `heap-*.pftrace`,邏輯正確(Finding 2 提到其他檔不在清單)。日誌起點 `-T` 取到整秒(`.000`),會多收當秒量測前幾行,無害。
- **不可逆**:刪檔限於 symlink 檢查後的 `heap-*.pftrace`,我讀碼沒找到越界。

## 三問

1. **原問題的修復效果**:有行為證據的只有一條。驅動執行期間收到 SIGTERM,整組驅動被收、擋下訊息出現(本機只重現 SIGTERM 落在 logcat 等待窗口的情形,驅動執行期間的情形沒另外實跑)。其他修復(`INSTRUMENTATION_` 判定、`deobfuscate`、`STOP_WAIT` 補 KILL)我只讀碼,沒跑對應場景,**未判定**。
2. **修補處的正常、錯誤與相鄰呼叫路徑**:正常路徑我只跑了 A 場景的 rc=0 完成路徑。錯誤與相鄰路徑出現 Finding 1 與 2 兩個缺口。
3. **新發現同一案例在修前修後各是什麼結果**:已逐條寫在上面。Finding 1 兩版都留孤兒行程,Finding 2 修前是整份落地、修後是 `logcat.raw` 殘留,Finding 3 兩版相同。

## 未驗範圍

- 真實 dumpsys exit-info 格式:只用測試檔裡的 fixture。
- 真實 trace_processor 的 CSV 輸出。
- SQL 在真實追蹤檔上的行為。
- Maestro 成功判法(只有 rc,沒有 INSTRUMENTATION_ 行),我只讀碼,沒實跑。
- `rec` 先 pop 的窗口,見 Finding 1。
- 實驗臨時目錄已在實驗後用字面絕對路徑 `rm -rf` 整個刪除,孤兒行程已手動殺掉。

severity: major
blocking 共 1 條(Finding 1)
