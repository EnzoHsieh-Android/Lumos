severity: major

## 發現

我在 `22f6e132` 的複製版(`/tmp/lumos-seat-work/code-推送與CI提速-r2/併發資源-sonnet/repo`)上實測了四項。有兩條 finding:一條 major、一條 minor。

### Finding 1:份數沒有上限,`buckets` 仍隨 n 線性配置,記憶體與時間爆掉

severity: major
blocking: 是

引句:「loads, counts, buckets = [0.0] * live, [0] * live, [[] for _ in range(n)]」

- 輸入:耗時表存在,執行 `python3.14 scripts/test_lumos.py --shard 1/<N> -k t_write_lf_roundtrip`。`--shard` 解析只擋 `_n < 1` 與 `_i` 超出範圍,沒有份數上限。
- 路徑:`_shard_by_duration` 的 `live=min(n,len(names))` 只限制了計算迴圈,最後的 `buckets = [[] for _ in range(n)]` 仍建出 n 個空串列。
- 重現(最小重現,可當場翻紅):

| N | 耗時 | 最大常駐記憶體 |
|---|---|---|
| 1000000(測試守的上限) | 1.5s | 約 540MB |
| 100000000 | 16.2s | 約 7.7GB |
| 2000000000 | 跑了 1.5 分鐘以上、仍在長 | 約 6GB,我手動 kill |

- 對照主線:`1b83927e` 的 `shard` 是 `k % _n`,N 多大都是 O(1)。
- 影響:`--shard 1/100000000` 這類打錯字,或 `LUMOS_TEST_SHARDS` 被設成大數,過去 rc2 或安靜跑完,現在會吃掉整台機器的記憶體。
- 應該是:拒絕 `_n` 超過合理上限(例如大於測試數就 rc2),或只算第 `_i` 份、不建 n 個桶。
- 現有測試 `t_runner_shard_by_duration` 只守到 100 萬,而且只量函式、不量整支執行器。
- 歸因:有證據的原有漏查(r1 的「份數比測試多」修補只收斂了 `live`,`buckets` 沒收)。
- 查證:
  - 修前 `0cdfc7cc`:`loads/counts/buckets` 三個陣列全部是 `range(n)`,比修後更糟;修後只留下 `buckets`,記憶體線性。
  - 主線 `1b83927e`:沒有 `_shard_by_duration`,不受影響。

### Finding 2:兩個 refresh 同時跑,排序鍵的 `p.stat()` 沒包例外,另一邊已刪的檔會讓它 traceback

severity: minor
blocking: 否

引句:「runs = sorted((Path(root) / ".lumos").glob("test-durations-run*.json"), key=lambda p: (p.stat().st_mtime, p.name))」

- 輸入:同一個 repo 同時跑兩個 `lumos test-durations refresh`。
- 重現:300 個 run 檔,兩個 refresh 並行,重複 8 輪,有一輪中招。
- 輸出:`FileNotFoundError: ... test-durations-run-105of300.json`,出自 `sorted` 的 key 函式,rc1,沒有任何友善訊息。
- 沒有出現:耗時表壞掉或內容遺失(`_write_lf` 的唯一暫存名有效)。
- 應該是:在排序前把 `stat` 包進 `try`,消失的檔略過。
- 此路徑的後段 `try: p.stat()` 有包例外,這一行是漏網的。
- 歸因:有證據的原有漏查。
  - 修前 `0cdfc7cc` 的同一行 grep 數 1(同樣沒包例外)。
  - 修補沒碰這行。

### 附記(不算 finding)

- **每片跑完再讀表的比對有一個盲點,但在實際用法下不成立。**
  - 盲點:只有「某一片從開頭到結尾橫跨換表那一刻」才擋得到。
  - 實測:我先跑 `--shard 1/2`(表 `19a95d9d`,分到 1024 支),換表,再跑 `--shard 2/2`(表 `72e193d3`,分到 1026 支),兩片都 rc0。兩片加起來是 2050 支、不等於 2049 支(多跑了一支)。
  - 為什麼可接受:`pre-push` 與 CI 的各片同時啟動、各自跑幾分鐘,任何換表都會橫跨至少一片。手動依序跑各片就沒人擋。
  - 換表又換回來:原來的片結尾讀到的還是舊雜湊、判相同。這是無害的,因為它自己用的就是舊表。在窗口內才啟動的片會被擋。
- **正常推送沒人動表時不會誤擋。**
  - 我在複製版跑 `--shard 1/1 -k t_test_durations`(含 `t_test_durations_refresh`),33 支全過、rc0,表檔沒被改。
- **run 檔核對窗口 `stat→read→寫表→再 stat→unlink`。**
  - 讀的過程中被改寫:`seen` 存的是讀之前的 stat,之後兩者不同,檔保留,正確。
  - 還剩一個窗口:最後一次 `stat` 到 `unlink` 之間被 `os.replace`,新檔會被刪。實際上只有微秒級,而且執行器是在測試跑完才寫 run 檔,單人使用下可忽略。
- **大輸入與超深巢狀(執行器、refresh 都測了)。**
  - 執行器讀 100 萬筆的表:3.7s,約 840MB。
  - 執行器讀 100 萬層巢狀 `[` 的表,或 500 萬個未關的 `[`:rc2 並印出「不是合法的 JSON」,1.0s,約 500MB。這個 500MB 與正常表的基線(約 495MB)同量,是執行器自己的載入量。
  - refresh 吃 200 萬層巢狀、50 萬層巢狀物件、100 萬筆的 run 檔:前兩個被略過,第三個正常合併,2.4s,約 600MB,沒有 traceback。
  - `RecursionError` 兩邊都有接住。

## 固定席節點判讀

- `pitfalls-code-loop`(RISK):不影響。我沒動推送閘的風險分級;`pre-push` 的 `LUMOS_TEST_SHARDS` 數字檢查只擋非整數,不擋超大整數(Finding 1 的觸發面之一)。
- `測試假綠形態`(INVARIANT):不影響。這次沒有「還原翻紅釘」類改動,Finding 1 的測試缺口屬於上限沒覆蓋,不是前置斷言缺失。
- `lumos-cli-read`、`lumos-cli-lifecycle`、`guard-kill`、`design-loop`(INVARIANT):不影響。這些合約行(search 排除 superseded、reinject、rc 優先序、處置閘)我讀到的 diff 沒碰到。
- `reversibility-governance-ledger`、`loop-convergence-recording`(RISK):不影響,diff 沒動帳本寫入。
- 超出上限只列名的節點:未逐條判,主題與併發資源鏡頭無關。

## 三問

1. **原問題的修復效果有何行為證據?**
   - 邊界輸入席的「份數比測試多」:部分成立。`live` 讓計算迴圈不再隨 n 變慢,實測 N=100 萬約 1.5s,對照修前約 20 秒。但整支執行器在 N=1 億時仍要 16s 與 7.7GB(Finding 1)。
   - 併發資源席的「讀完到刪之間改寫」:成立。`seen` 對照有效,「讀完之後被改寫的留給下次」是我讀碼推出的,我沒另外造出讀寫交錯來重現。
   - 各片跑完再讀一次表:成立,但只擋得到橫跨換表的片(見附記)。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 正常:分片測試通過、沒有誤擋。
   - 錯誤:表壞、深度巢狀都回 rc2。
   - 相鄰:refresh 的排序鍵路徑沒被修補覆蓋(Finding 2)。
3. **新發現的同一案例在修前與修後各是什麼結果?**
   - Finding 1:修前記憶體更糟(三個陣列都是 n 長),修後只剩 `buckets`。
   - Finding 2:修前與修後都有這個排序鍵問題;修補沒碰到它。

未驗範圍:CI 上實機的 `concurrency` 行為、跨機器的表一致性。

總結:最嚴重等級 major;blocking 共 1 條(Finding 1)。
