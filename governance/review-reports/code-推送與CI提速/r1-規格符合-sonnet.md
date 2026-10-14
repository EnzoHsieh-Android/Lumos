severity: minor

**逐條裁定**

〈做法〉
- 耗時表:已實作。`governance/test-durations.json` 已進版控,`version` 為 1,2029 筆,全是非負數。`_BOOKKEEPING_FILES` 已加入它。
- 記錄實測秒數:已實作。每支測試跑完都記秒數,過、紅、逾時、例外都記,跳過的(`SKIPPED_NAMES`)不記。寫入在 `if _is_src:` 底下,先寫 `.lumos-tmp` 再 `os.replace`。`.gitignore` 已加 `.lumos/test-durations-run*.json`。
- 刷新耗時表(`lumos test-durations refresh`):已實作。我另跑了 `t_test_durations_refresh`,11 項全過。取最新、保留舊值、刪 run 檔三項都對。多做的部分見 finding 1。
- 分片:
  - 執行順序維持 suite、分片、ff/seed、`-k`:已實作。
  - 檔案不存在時印「沒有耗時表,照名字輪流分」:已實作。
  - 格式不對時每一份 rc 2:已實作。測試涵蓋 6 種壞法,三份都是 rc 2。
  - 分法(權重、下限 0.05、中位數、同權重照名字、平手比支數再比編號):已實作,與 `_shard_by_duration` 逐字相符。
  - 雜湊行(表雜湊前 8 碼、總支數、這份支數):已實作。
  - 空片照舊擋(rc 1),帶 `--suite` 的空片算過:已實作。
- 取消過期 CI(`concurrency`):已實作。群組鍵為 `ci-事件名-PR 編號 || sha`,`cancel-in-progress` 只對 `pull_request` 為真。
- CI 印每份耗時:縮水,見 finding 2。

〈範圍〉
- 第二階段、「不做」各項:都沒有實作,符合預期。沒有多做主線略過全套、合併佇列或快取。

驗收條款
- S1:已實作。`t_runner_shard_by_duration` 17 項全過。
- S2:已實作,同一支測試涵蓋。
- S3:已實作。
- S4:已實作,`t_ci_yml_speed_shape` 4 項全過。但測試只查「份耗時」這個字串,查不到開頭有沒有印時間。
- S5:已實作。`pitfalls --diff` 對只改耗時表的提交判成 `docs`。

〈回退〉
- 已實作。刪掉耗時表就退回輪流分,不用改程式。ci.yml 兩段是獨立的,可以單獨還原。

**Findings**

severity: minor
blocking: 否
縮水:CI 每份日誌只在結尾印耗時,開頭沒有印時間。spec〈做法〉要求「shards 工作在每一份的日誌開頭與結尾印時間,結尾印『第 i 份耗時 N 秒』」。實作只在結尾 `echo "第 $i 份耗時 …"`,開頭只有 `s=$(date +%s)` 這個變數,沒有輸出。結尾的耗時行足以量出撤除條件要的數字,所以不影響行為。照 spec 字面,每份日誌缺一行起始時間。
引句:「( s=$(date +%s); python scripts/test_lumos.py --shard "$i/$SHARD_TOTAL"; rc=$?; echo "第 $i 份耗時 $(( $(date +%s) - s )) 秒"; exit $rc ) > "/tmp/shard-$i.log" 2>&1 &」

severity: minor
blocking: 否
多做 ⚠:`refresh` 對舊表的處理超出 spec。spec 只說「沒跑到的保留舊值」。實作在舊表格式不對時改成從空表開始(靜默,不印提示)。舊表格式對、但個別秒數不合法時,也悄悄丟掉那幾筆。另外把新值 `round(…, 3)`。spec 沒有這些行為。照 spec 字面,合法的舊值應該全留。
引句:「table = {k: v for k, v in old["tests"].items()」

縮水+未實作共 1 條
