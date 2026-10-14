severity: minor

我在固定版本 22f6e132 的複本上審查,沒有找到會判錯的輸入,只有一條 minor。複本在 `/tmp/lumos-seat-work/code-推送與CI提速-r2/正確性-sonnet/repo`。

## Finding

severity: minor
blocking: 否

`_shard_by_duration` 的份數上限只收了計算量,沒收配置量。`live = min(n, len(names))` 讓迴圈不隨 n 變慢,但 `buckets` 仍配置 n 個空 list。有耗時表時,把 `--shard` 打成很大的份數會吃掉大量記憶體。
- 輸入:`--shard 1/10000000 --list`,repo 內有 `governance/test-durations.json`。
- 實測修後 22f6e132:3.0 秒、最大常駐記憶體 1.2GB。
- 主線 1b83927e 同一輸入(沒有耗時表):1.0 秒、0.49GB。
- 每千萬份約多 0.7GB,打成 1e9 約 70GB,會把機器拖死。
- 原本打錯份數會很快回「一支都沒分到」rc1。
- 應該是只回傳要的第 `_i-1` 份,或在 `_n > len(tests)` 時直接走空片路徑。這是單人輸入錯誤,所以只標 minor。

引句:「    loads, counts, buckets = [0.0] * live, [0] * live, [[] for _ in range(n)]」

歸因:有證據的原有漏查。上輪修補(r1 邊界輸入席)只收了計算量,配置量沒收到。修前 0cdfc7cc 我沒有實際跑,只讀了程式,所以修前的結果未驗。

## 逐項結論(已驗,有跑)

- **`_duration_ok` 兩份**:逐字相同,同一條規則。`t_test_durations_refresh` 的探針含 NaN、Inf、`10**400`、布林、字串、`-0.0`,兩邊判法一致。
- **`_load_durations_table` 各種壞法**:不是 JSON、不是物件、`tests` 空或不是物件、秒數為字串、負數、NaN、Infinity、超大整數、巢狀過深,都丟 `ValueError`。每一片回 rc2,連 `--suite docs --list` 也是。BOM 兩邊都吃(`json.loads(bytes)`)。沒有表則三片聯集等於全部、不重複。
- **`_shard_by_duration` 分法**:浮點累加順序固定,各片獨立算結果一致。中位數、權重下限 0.05、平手比支數三條規則,各有一組拿掉就會翻紅的輸入。份數 100 萬在 2 秒內算完。
- **`_thash_end`**:
  - 開頭沒表、結尾有表,以及開頭有表、結尾沒表或壞掉,都回 rc2。
  - 表沒換則 rc0。
  - `--list` 是查詢,提早離開不比對,合理。
  - `--suite` 的空片 `return 0` 也提早離開,那片沒跑測試,合理。
  - `-k` 是分片之後才篩,比對仍會做。
  - `-x` 中斷後仍會做結尾比對。
- **`cmd_test_durations_refresh`**:
  - 舊表壞掉(含 `tests` 的值不合法)時 rc2、不覆蓋、run 檔留著。
  - run 檔形狀不對時略過,其他檔照合併。
  - 取最新靠排序 `(mtime, name)` 加後蓋前。
  - 讀之前先記錄 stat,刪之前比對 `mtime_ns` 與大小。竄改測試是在 `_write_lf` 插入改寫,被改的 run 檔確實留著。
  - 暫存檔 `*.lumos-tmp` 不會被 `*.json` 的 glob 掃到。
- **`cmd_push_summary`**:函式結尾的 `return 0` 本來就在,這輪只補了行程內回傳值的測試。拿掉 `return 0` 會回 `None`,`rv == 0` 會翻紅,測試有牙。
- **ci.yml**:
  - 子殼層 `set +e` 正確。紅的那片也印得出耗時,`rc` 由子殼層的 `exit $rc` 傳出。
  - 新增的開始、耗時兩行不會誤觸日誌的 `, [1-9][0-9]* failed` 紅燈判斷。
  - `concurrency` 群組:PR 用編號,其餘事件用 sha,`cancel-in-progress` 只對 PR 開。
- **新測試**:`t_runner_shard_by_duration`、`t_test_durations_refresh`、`t_ci_yml_speed_shape`、`t_push_summary_anchor_note_and_separators` 在複本上全綠。
- **資料狀態五問**:
  - 新舊互讀:無問題。
  - 寫一半:靠 `_write_lf` 原子換名。
  - 衍生資料:表只增不修剪,現況 2029 筆對 2049 支,有 1 筆孤兒。這是設計(沒跑到的保留舊值),不標。
  - 時間:無問題。
  - 不可逆:刪 run 檔前核對過。

## 三問

1. **原問題的修復效果**:
   - 竄改表的情境(開頭沒表、結尾被寫出一張)修後 rc2、「耗時表換了」。
   - 同一支執行器在表沒換時 rc0。
   - 超大整數、巢狀過深、BOM、tests 形狀不對,現在都不崩、不清表。
   - 這些證據都在上面兩支測試的輸出裡。
2. **修補處的相鄰路徑**:空片、`--list`、`-k`、`--suite` 都仍成立。只有份數很大的相鄰路徑,是上面那條 minor。
3. **新發現的同一案例**:修前 0cdfc7cc 沒有實際跑,修前結果標「未驗」。主線 1b83927e 的結果在上面。

## 未驗範圍

- 沒有在真實 GitHub Actions 上跑 `concurrency` 與每片耗時的實況。
- `t_runner_shard_by_duration` 本機要 56 秒(上限 180 秒,餘裕約 3.2 倍),CI 並行下是否逼近上限沒有實測。這條沒有具體失敗場景,所以沒列為 finding。
- 沒有逐點跑 mutation。
- 以下兩處只讀程式,沒跑,也沒有可用的失敗場景:
  - `sorted(... p.stat() ...)` 遇到懸空符號連結或併發刪檔會未捕捉。
  - run 檔 key 含孤立代理字元時,`_write_lf` 的 `UnicodeEncodeError` 不屬於 `OSError`,會未捕捉。

## 固定席節點

- **測試假綠形態**:這輪新增的前置斷言(`★前置★ 現場成立`)都有放,不影響。
- **其餘節點**(`pitfalls-code-loop`、`lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle`、`reversibility-governance-ledger`、`loop-convergence-recording`、`design-loop`):不影響。
  - 這輪沒動它們的 INVARIANT 所涵蓋的行為。
  - `_BOOKKEEPING_FILES` 只多收一個資料檔路徑。
  - `pitfalls --diff` 把只改耗時表的提交判成 docs,有測試覆蓋。
- 其餘「只列名」的節點未逐一展開,沒有發現牽連。

最嚴重等級 minor;blocking 共 0 條。
