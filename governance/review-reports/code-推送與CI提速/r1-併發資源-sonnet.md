severity: minor

審查範圍:併發、資源與效能鏡頭,實驗都在 `/tmp/lumos-seat-work/code-推送與CI提速/併發資源-sonnet/`。以下三條 finding 都是小問題,不擋推送。

## 實測結果(沒出問題的部分)

- **分片函式的耗時:** `_shard_by_duration` 在 2000 支、16 份下,連叫 16 次共 0.06 秒。各份權重最大與最小差 0.1 秒,最重那份是平均的 1.0002 倍,平衡得很好。
- **讀耗時表:** `governance/test-durations.json` 有 2029 支,`json.load` 花 0.56 毫秒,加上 sha256 也可忽略。
- **run 檔被半寫讀到:** 寫 run 檔是「寫暫存檔再 `os.replace`」,暫存檔名是 `.json.lumos-tmp`,不會被 `test-durations-run*.json` 這個 glob 撈到。refresh 讀不到半寫檔,最差是整檔被略過。
- **各片 run 檔名互不衝突:** 各片寫 `test-durations-run-iofN.json`,檔名分開,不會互相蓋掉。沒有分片的子集跑寫 `test-durations-run.json`,合併時每支取最新,也不衝突。
- **CI concurrency:**
  - 主線推送的群組鍵是 `ci-push-<sha>`,每個提交各自一組,且 `cancel-in-progress` 是 false,所以主線不會互相取代或取消。
  - PR 用編號分組並取消舊的,符合設計。被取消的 run 在 `ci-wait` 裡走「未定」,不會被當成綠。
  - shards 那段的子殼 `( … rc=$?; echo …; exit $rc )` 保留了離開碼,`wait` 照樣收得到。
- **一個 runner 兩份並行:** 照耗時分的演算法本身是確定性的,沒有可以放大差距的路徑。

## Finding

severity: minor
blocking: 否
1. 各片各自讀耗時表,中途換表時聯集不再等於全部,而且全綠不報。
   - **場景:** 推送前掛鉤用 `&` 一片一片起 4 個行程,每片自己在 `main()` 裡呼叫 `_load_durations_table()` 再算分法。這時另一個行程跑 `lumos test-durations refresh`(`os.replace` 換表),或 `git pull` / `checkout` 換掉表,各片就會用不同版本的表。
   - **重現:** 我用兩份差一個權重的表,分別算出第 1 片和第 2 到 4 片,拼起來漏了 344 支、重複了 364 支。三片拼起來的結果沒有人檢查。
   - **為什麼沒被抓到:** 每片都印了表雜湊,但掛鉤和執行器都不比對各片的雜湊,各片離開碼照樣 0。
   - **應該是:** 掛鉤先讀一次表再把雜湊傳給各片,各片發現自己的表雜湊對不上就 rc2;或至少讓掛鉤比對各片 log 裡的雜湊。
   - **機率:** 窗口只有各片啟動相差的幾毫秒,實際很低。但後果是漏跑測試還判綠,正好是這條線最忌諱的一種,所以仍然列出。
   - 判不準的部分標 ⚠:本機掛鉤是否真的有可能與 refresh 並行,取決於使用習慣。
引句:「同一個提交的每一份讀到的是同一個檔,所以格式不對時每一份都會擋——不各自退回輪流分,免得混用兩種分法、聯集出錯。」

severity: minor
blocking: 否
2. 兩個 `refresh` 同時跑時,固定的暫存檔名會讓其中一個失敗。
   - **走到哪:** `cmd_test_durations_refresh` 的 `tmp = table_path.with_suffix(...)` 是固定檔名,沒有帶 pid。
   - **重現:** 3 個 refresh 同時跑,各讀 3 個 run 檔,共 20 輪。結果是 40 次 rc0、15 次 rc2(run 檔已被別人刪光)、5 次 rc1。rc1 的訊息是 `FileNotFoundError: …test-durations.json.lumos-tmp' -> '…test-durations.json'`。
   - **後果:** 兩個行程寫同一個暫存檔,一個 `replace` 走了暫存檔,另一個就找不到。失敗那個的 run 檔不會被刪。每輪結束時耗時表本身都還是合法 JSON,沒有壞表。
   - **應該是:** 暫存檔名帶 pid 或用 `tempfile`。
引句:「        tmp = table_path.with_suffix(table_path.suffix + ".lumos-tmp")」

severity: minor
blocking: 否
3. `refresh` 讀完才刪 run 檔,中間有一片剛好寫完新檔,新檔會被刪掉。
   - **場景:** refresh 在 `for p in runs:` 讀完,最後 `for p in runs: p.unlink()` 刪的是同一批路徑。讀到刪之間如果某片剛好用 `os.replace` 換了新內容,新內容沒進表就被刪了。
   - **後果:** 只是少一份計時資料,耗時表不會壞。同一個 run 檔路徑被覆蓋才會發生,實際影響很小。
   - **應該是:** 用「讀到的當下的 mtime / 內容」確認沒變再刪,或改成讀完就改名(`rename`)成私有檔名再處理。
引句:「讀完刪掉 {len(runs)} 個 run 檔」

## 其他觀察(不構成 finding)

- **耗時表只增不減:** refresh 規定「沒跑到的保留舊值」,改名或刪掉的測試名會永遠留在表裡。表會慢慢長、中位數也會被舊名拉動。目前 2029 支沒有實際壞處,等表明顯大於實際測試數再處理就好。
- **耗時是在什麼負載下量的:** 本機 4 片並行與 CI 單機 2 片並行量到的秒數不同。「取最新」會讓表隨最後一次刷新的環境擺動。這只影響平衡度,不影響完整性,表格式壞掉的處理也已經每片一致擋 rc2。

## 固定席節點逐條判

- **測試假綠形態 ★INVARIANT★:** 這條要求修 bug 的還原翻紅釘要有前置斷言證明現場成立。這次新測試有加 `★前置★`(例如照名字輪流分確實不平均、子集真的跑了)。條款本身沒被動到,不影響。finding 1 是另一類假綠,但屬於新增分片機制自己的風險,不違反這條。
- **lumos-cli-lifecycle:** 這條管 re-inject 保留 sentinel 之外的內容,改動沒碰到。不影響。
- **lumos-cli-read:** 這條管 search 預設排除 superseded,改動沒碰到。不影響。
- **pitfalls-code-loop、loop-convergence-recording、reversibility-governance-ledger(★RISK★):** 只牽連 `scripts/lumos`。新增的 `_TEST_DURATIONS_REL` 進了 `_BOOKKEEPING_FILES`,語意是「只改耗時表不讓代碼審留痕失效」,我沒發現併發面的副作用。
- **guard-kill 兩條 INVARIANT:** rc 優先序和 `--json` 純度,改動沒碰到。不影響。
- **design-loop 處置閘第五步:** 改動沒碰到。不影響。
- **超出上限只列名的節點:** 沒逐篇讀,從這鏡頭看沒有關聯。

最嚴重等級:minor。blocking 共 0 條。
