severity: minor

審查對象是固定版本 07642d8e,修補鏡頭是 84b487f2 到 23c0d065。沒有 major 或 blocker,有三條 minor。

**1. 第二段意外例外的收尾被中斷時,錄製不再有人收,cleanup 還回報已收乾淨**

severity: minor
blocking: 否。這條有兩個前提:要先出意外例外,收尾那幾秒內還要來一個訊號。錄製由 `max_record_s` 的上限自己結束,所以不會一直跑下去。

引句:「        rec = state.pop("rec", None)
        gone = abort_record(rec) if rec else True」

file: `scripts/templates/android-stability-collect.sh` 的 `native_phase`,在 `except Exception` 區塊內(快照版本 07642d8e)。

歸因:有證據的原有漏查。

- **修前**:`finally: rec = state.pop("rec", None); if rec and not abort_record(rec)` 也是先 pop 再收。
- **修後**:改成 `except Exception` 區塊,同樣先 pop 再收。

證據:
- 我用同一個測試腳本分別載入修前與修後的收集腳本。
- 設 `native_run` 丟 RuntimeError,`abort_record` 丟 Terminated。這模擬裝置呼叫卡住時收到 SIGTERM。
- 兩版結果相同:`cleanup 回傳: True ; cleanup 實際去收的錄製: [] ; state: {}`。

具體失敗場景:
- 第二段出現意外例外,`abort_record` 要送 TERM 並刪檔,最久可能 240 秒。
- 這段時間收到 SIGTERM,`Terminated` 從 except 區塊往上丟,`main` 呼叫 `cleanup(state)`。
- `state["rec"]` 已經被 pop 掉,cleanup 沒有東西可收,回傳 True。
- `main` 於是印出「裝置上的錄製已停、暫存已刪」,實際上裝置上的錄製與暫存可能還在。

正確寫法是 `abort_record` 做完再 pop。

**2. 查詢沒有自己的時間預留,正常邊緣情況下只拿到 1 秒**

severity: minor
blocking: 否。後果是第二段寫成 failed(「查詢逾時」),這一步的上限不會被超過。

引句:「        return T_LONG if deadline is None else max(1.0, min(T_LONG, deadline - time.time()))」

file: `scripts/templates/android-stability-collect.sh` 的 `native_run` 內 `left()`,以及 `deadline = None if b is None else t_start + b - NATIVE_MARGIN`。

歸因:未判定。這是 r2 新增的功能,沒有修前版本可比。我也沒在真機或真 trace_processor 上跑,只是讀碼推演。

具體失敗場景:
- 驅動與查詢共用同一個 deadline,而停錄、拉檔、讀結束紀錄發生在驅動之後、查詢之前。
- 驅動在 deadline 前 20 秒結束,停錄加讀結束紀錄花 15 秒。查詢只剩約 5 秒,真實 heapprofd 錄檔載入加遞迴查詢遠遠不夠,於是「查詢逾時」。
- 此時距離這一步的上限還有一百多秒,那段 `NATIVE_MARGIN` 沒有給查詢用。
- 反方向沒有問題:停錄在裝置卡死時可超過 180 秒,但那種情況 e2e 的 TERM 加 60 秒寬限會接手,走 cleanup。

**3. 查詢範本的遞迴走訪沒有先過濾,工作量與記憶體隨 葉子數 × 呼叫鏈深度 成長**

severity: minor
blocking: 否。工作量是線性成長,沒有二次方;逾時會被 `left()` 或 `T_LONG` 收掉,結果是 failed,不是卡死。

引句:「  select callsite_id, sum(size) from heap_profile_allocation where heap_name = 'libc.malloc' group by callsite_id」

file: `scripts/templates/android-stability-native.sql:19`,同檔的 `walk` 遞迴 CTE 與 `fr2`。

歸因:未判定。修補只動了最後的 `caller` 判斷與 `pick` 排序,走訪結構兩版一樣。

證據:
- 我把查詢原樣放進 sqlite 3.53.4,用合成資料量測。這是 sqlite 不是 trace_processor,只能當量級參考,絕對時間與記憶體會不同。
- 資料是 N 個葉子 callsite,各自接一條共用的 10 層主幹,約 60% 的葉子淨配置為 0。
- 時間與記憶體隨「葉子數 × 深度」線性成長,每個葉子 × 深度約 15 微秒、7 KB。

| 葉子數 | 深度 | 耗時 | 記憶體 |
|---|---|---|---|
| 5,000 | 40 | 2.6 秒 | 93 MB |
| 20,000 | 40 | 12.1 秒 | 207 MB |
| 100,000 | 40 | 62 秒 | 682 MB |
| 20,000 | 120 | 60 秒 | 514 MB |

具體失敗場景:
- 一個原生配置很多的 App,heapprofd 錄到 30 萬個以上不同的葉子 callsite、深度 60 以上。
- 外推約 18M 次走訪,約 5 分鐘、2 GB 以上,記憶體還沒量到 trace_processor 實機。
- 在 e2e 上限下會因 `left()` 逾時而 failed。
- 淨配置為 0 或負的葉子也被完整走訪,卻不可能讓呼叫位置累計達到 1 MiB。

**pitfalls manifest(16 條)**

| 條目 | 判定 |
|---|---|
| `test_lumos.py:18990` 的 RUF059,`d` 未使用 | 真隱患(輕):專案的 ruff 規則含 RUF,推送前閘會紅。我沒有跑 ruff 確認。這是測試檔,屬另一席的範圍,把 `d` 改成 `_` 即可 |
| `collect.sh:261`、`314` 的 `open(` 沒用 with | 誤報:CPython 引用計數離開敘述就關檔,兩處都是一次性讀寫 |
| `collect.sh:487` 的 `time.sleep` | 誤報:`fresh_launch` 裡是一次固定 `SETTLE` 秒,不在迴圈裡 |
| `native.sql` 的 13 條 N+1(行 18、21、23、52、61、75、78、81、84、88、90、92 等) | 誤報:這些是 CTE 與集合式 SELECT,沒有逐列再查。真正的效能風險是上面第 3 條的遞迴走訪 |

**三問**

- **原問題的修復效果:**
  - 逾時扣掉 `NATIVE_MARGIN` 與 `left()` 讓驅動與查詢都不超過 deadline,這部分我只讀碼,沒有真機證據。
  - 意外例外時當場收錄製有 `native_phase` 的單元測試,我讀了,沒重跑。
  - Terminated 時錄製留在 state 交給 cleanup,讀碼成立,但意外例外那條路徑有第 1 條的缺口。
  - 未驗:真機上的 heapprofd 停錄時間與拉檔時間。
- **修補處的正常、錯誤、相鄰路徑:**
  - `fresh_launch` 抽出後,第一段子程序與順序不變:force-stop、read_exits、monkey、sleep、pidof 都一樣,數量也沒變。
  - 第二段順序改成與第一段一致(read_exits 在 monkey 之前),子程序數量沒變。
  - `driver` 與 `tp_rows` 預設逾時仍是 `T_LONG`。
  - `STEP_BUDGET_S` 的 nan、inf、0、負數都在 `main` 開頭被擋下。
  - 範本缺檔在 `preflight` 就 `die`,不會白跑暖機。
  - driver 與 trace_processor 逾時走 `run()` 的整組殺掉。
  - 暫存 .sql 在 `finally` 刪除。
- **新發現的同一案例修前修後:** 第 1 條兩版結果相同(原有)。第 2、3 條沒有修前版本可比(新功能),留未判定。

LUMOS-IMPACT 固定席節點這次沒附上(鏡頭計算超時),所以我沒有對圖譜節點逐條答。

我的實驗目錄 `/private/tmp/lumos-seat-work/code-原生配置排行/資源-sonnet` 已刪除。

最嚴重 severity:minor;blocking 條數:0。
