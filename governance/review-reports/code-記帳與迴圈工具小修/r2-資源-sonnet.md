severity: major

這輪沒有發現子程序問題。有兩條資源發現:修補宣稱的「帳讀一次」在預設記帳路徑上沒有成立,而且改完之後記帳的尖峰記憶體變高、被拒絕的呼叫也多讀一次整本帳。測試環境:臨時 repo,10 萬列帳,python3.14,修前 `d2da0e8c` 對修後 `f791d8ba`。

測量方法:對 `.canary-log.jsonl` 掛 `sys.addaudithook` 的 open 事件,數讀取次數並印呼叫堆疊;掛的是 `sys.addaudithook`,所以走 `io.open` 的 `_canary_ledger_rows` 也算得到。另外用 `/usr/bin/time -l` 量尖峰記憶體,用 `/usr/bin/time -p` 量牆鐘時間。

1. 預設記帳路徑整本帳還是讀 3 次,跟修前一樣;只有帶 `--orchestrator` 或 `--regression-set` 的路徑少讀 1 次
severity: major
   - blocking: 是
   - 輸入:`canary record none --loop dsg-5 --round r99 --tier standard --auditor a --report … --snapshot …`,帳 10 萬列。
   - 修前讀 3 次:`_cap_retro_record_block`、`cmd_canary` 的 `_loop_records_checked`、`_jsonl_append_verified` 讀回自驗。
   - 修後也是 3 次:開頭的 `_canary_ledger_scan`、`_cap_retro_record_block`(內部又 `_loop_records_checked(env, loop_id)` 沒帶 `scan=`)、讀回自驗。
   - 牆鐘時間約 3.5 秒對 3.5 秒,沒有省。
   - 加 `--orchestrator` 時修前 4 次、修後 3 次,這條路徑有收到。
   - 正式的代碼審記帳一定帶 `--report`、`--snapshot`、`--round`,走的是預設路徑,這條路徑沒變快。
   - 沒帶 `--report` 與 `--snapshot` 時,`cmd_canary` 尾端的 T6 段另有一次 `path.read_text` 整檔讀,這條沒被收。
   - 引句:「讀帳一次,後面 --orchestrator、--regression-set、輪次規則、載體最後記共用(代碼審 r1 資源 1:原本一筆最多讀三次整本帳)」
   - 歸因:未判定,這是修補沒達成宣稱的效果。修前修後同一指令都是 3 次,見上面的測量。
   - 只見次數相同,不能說有倒退;但「收成開頭一次」的註解與實測不符。

2. 開頭的 `_lscan` 一直活到函式結束,記帳時同時有兩份整本帳在記憶體
severity: minor
   - blocking: 否
   - 輸入同上,多個編號(10 萬列分在 1 萬個編號):尖峰記憶體修前 353MB、修後 456MB。
   - 單一編號 10 萬列:修前 351MB、修後 449MB。
   - 原因:`_lscan` 沒有釋放,`_cap_retro_record_block` 又掃出第二份。
   - 在 `_lrows, _lerr = _loop_records_checked(...)` 之後加 `del _lscan`:多編號的情形降回 355MB;單一編號的情形仍是 449MB,因為 `_lrows` 本身就是整本帳。
   - 這是複製產生的 `lumos_after_del` 的實驗,不是 repo 的改動。
   - 引句:「_lscan = _canary_ledger_scan(env)」
   - 歸因:有證據的修復回歸。修前 351 到 353MB,修後 449 到 456MB,同一指令。

3. 被拒絕的呼叫現在也先讀整本帳
severity: minor
   - blocking: 否
   - 輸入:`canary record none --loop dsg-5 --round r99 --tier standard --auditor a`,故意不帶 `--report`,會被擋成 rc2。
   - 修前讀 1 次,修後讀 2 次,牆鐘 2.96 秒對 3.31 秒(10 萬列)。
   - 原因:開頭的 `_canary_ledger_scan` 在後面各個「擋下」判斷之前就做了,而 `--report`、`--snapshot` 的缺漏檢查排在它後面。
   - 引句:「if loop:\n        try:\n            _lscan = _canary_ledger_scan(env)」
   - 歸因:有證據的修復回歸。修前 1 次、修後 2 次,同一指令。

已驗、無問題的部分:
- **讀側新增 `_review_rows` 沒有變成多掃。** `loop next` 與 `loop status --disposal` 在單一編號 10 萬列的帳上,修前修後都約 1.55 秒與 1.75 秒。尖峰記憶體約 456 到 462MB,前後相同。
- **擴大到 30 萬列是線性的。** `loop next` 3.59 秒,`loop status --disposal` 4.43 秒。
- **沒有二次方工作。** 單一編號 10 萬列的 `_round_format_write_block` 也沒有。
- **子程序沒有新增。** 修補差異裡沒有新增 `subprocess`。`_git_head` 與 `_plans_in_range` 的 `subprocess.run` 沒帶 `timeout`,但那是修補之前就有的,不在差異內。
- **未測:** `--regression-set` 路徑沒有實測,這條只靠看程式判斷會用 `_lrows`。`--panel` 在我的測試帳上因混用守衛 rc2,讀取次數沒有量到有意義的數字。

三問的回答:
- **原問題的修復效果:** 部分成立。帶 `--orchestrator` 或 `--regression-set` 的路徑少讀 1 次,預設路徑沒有減少。
- **修補處的相鄰路徑:** 拒絕路徑多讀 1 次,記憶體多一份帳,見 2、3 兩條。
- **同一案例的修前修後結果:** 見各條的數字。

最嚴重 severity:major,blocking 共 1 條。
