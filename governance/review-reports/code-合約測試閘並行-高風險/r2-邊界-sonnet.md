severity: major

## 1. S7 中斷測試把「0.6 秒後送 SIGINT」當成「閘已進入等待迴圈」,載入模組超過 0.6 秒就紅
severity: major
blocking: 是
引句:「_time.sleep(0.6)
        pr.send_signal(_sig.SIGINT)」
file: `scripts/test_lumos.py`(t_bound_tests_parallel_interrupt_stops_dispatch,上述兩行)

1. 子程序用 `SourceFileLoader('m', 'scripts/lumos').exec_module` 載入 5 萬行的 `scripts/lumos`。沒有 `__pycache__` 時,這一步要編譯。我實測冷載入約 1.9 秒,有快取時約 0.08 秒。測試沒有任何「閘已開始跑」的握手,0.6 秒一到就送 SIGINT。
2. 冷載入時,KeyboardInterrupt 落在 `exec_module` 內部,在 probe 的 `try` 之外。probe 的 stdout 沒有 `INTERRUPTED`,`並行 S7 前置:中斷有送到、閘照樣往外丟` 轉紅。
3. 重現:在 `3daa00a8` 的乾淨 clone 跑 `python3.14 scripts/test_lumos.py -k t_bound_tests_parallel_interrupt_stops_dispatch`,在沒有可用 `__pycache__` 的環境下,連跑 3 次都是 `1 passed, 1 failed`(另外一次加了 `PYTHONDONTWRITEBYTECODE=1`)。錯誤輸出是 `importlib._bootstrap_external get_code ... KeyboardInterrupt`。同時 `started` 為 0 支,所以「最多 2 支」那條斷言空過。
4. 影響:CI 乾淨 checkout、4 個 shard 同時搶 CPU、禁寫 bytecode 的容器、慢機器,這支都會紅。推送閘與 CI 會擋下無關的推送。
5. 這次看到的是紅,不是假綠。同一根因也讓「中斷後不再派新的」在中斷落在派工前的情況下沒被驗到。
6. 歸因:有證據的修復回歸。這支測試出現在修補差異裡(修前 `d3ac862` 沒有)。修前的行為證據:無。

## 2. S5 與 S7 的 finally 清掃是空操作,而且依賴 pgrep
severity: minor
blocking: 否
引句:「for pid in _sp.run(["pgrep", "-f", str(d)], capture_output=True, text=True).stdout.split():」
file: `scripts/test_lumos.py`(t_bound_tests_parallel_error_stops_fast 與 t_bound_tests_parallel_interrupt_stops_dispatch 的 finally)

1. 慢測試的指令是 `{python} run.py t_slowN`,`d` 只是 cwd,不在命令列裡。實測起一個 cwd 在某目錄、命令列是 `python3.14 run.py t_slow0` 的程序,`pgrep -f <該目錄>` 沒有任何輸出,`pgrep -f "run.py t_slow0"` 才找到。所以 pgrep 永遠不會命中這些孤兒,殺不掉任何東西。S5 的 `t_slow` 會在測試結束後繼續睡到 12 秒,孤兒不會被收掉。這違反全域規則「結束前刪掉自己建的程序」。
2. 沒有 `pgrep` 的環境(最小容器、alpine/busybox)裡,`_sp.run(["pgrep", ...])` 在 finally 內丟 `FileNotFoundError`。它跳過後面的 `rmtree`,測試因例外而紅,並蓋掉原本的斷言結果。
3. 歸因:S5 與 S7 的 pgrep 都在修補差異裡(差異第 328 行與第 386 行),所以是有證據的修復回歸。修前的行為證據:無。

## 3. 丟例外路徑上,在跑的測試不會停,而 fix-check 呼叫端接住例外後會繼續往下走
severity: minor
blocking: 否
引句:「except BaseException as e:   # 開不了程序之類;交給主流程往外丟」
file: `scripts/lumos:13317`(`except Exception as e: bt = {"status": "error", ...}`)

1. 輸入:`bound_tests.parallel` 為 2 以上,其中一個平台的 `root` 不存在,另一個平台有慢測試(最長 600 秒)。
2. 走法:不存在的 root 讓 `_kill_run` 的 `Popen` 丟 `FileNotFoundError`,worker 把它記進 `errs`,主流程往外丟。13317 行把它轉成 `status: error`,程序繼續做修正關卡的後續步驟。
3. 其他 worker 已開跑的 `_kill_run` 仍在 daemon 執行緒裡執行,測試子程序在自己的 session,最多繼續跑到各自的逾時。這是新的行為:循序模式丟例外時沒有任何測試同時在跑。計劃文字只承認 Ctrl-C 孤兒,沒有承認這條路徑。
4. 我沒有實測 13317 行之後會不會有衝突寫入,所以這條只定為 minor。
5. 歸因:未判定。修前同樣是 ThreadPoolExecutor,它在 `__exit__` 時 join、不留孤兒,但 r1 版本的行為我沒有在這份材料裡逐版實測。

## 邊界輸入逐項(`_bound_tests_parallel`、`_run_bound_tests`、`_bound_tests_check`)

這些我讀碼逐項走過,沒有發現錯誤。

- **設定值**:
  - 2、16:接受,回傳原值。
  - 17、0、-1、`True`、`"4"`、`[]`、`{}`、`NaN`:一律警告後回 1。`True != 1` 為 False,但有 `isinstance(v, bool)` 補上,仍會警告。
  - `null` 或沒有 `parallel` 鍵:靜默回 1。
  - `1`:靜默回 1。
  - `1.0`:`1.0 != 1` 為 False 且不是 bool,所以靜默回 1。這和 docstring 寫的「小數一律 1、有寫但不合法會出聲」略有出入,但結果等同 1,不構成錯誤。
- **區塊與檔案**:`bound_tests` 是 `null` 以外的非物件(`4`、`[]`、`false`、`"x"`)會警告。`bound_tests = {}` 靜默回 1。`config.json` 不存在、空檔、頂層不是物件、編碼壞、JSON 壞,都落入 `except Exception` 或 `isinstance` 判斷,靜默回 1(不警告,和其他設定讀不到時的慣例一致)。
- **巨大整數**:超過 4300 位數的整數在 Python 3.11 以上 `json.loads` 就丟 `ValueError`,被吞掉,靜默回 1。4300 位以內的整數會把整串 `repr` 印進 stderr,訊息很長但不出錯。
- **提醒去重**:鍵是 `(resolve 後的路徑, "value:"+repr(v))` 或 `"block:"+repr(bt)`。同專案不同值會各提醒一次,不同專案同值也會各提醒一次,不會漏提醒。路徑不存在時 `resolve()` 不丟例外。
- **項目數量**:
  - 0 項:`jobs` 為空,走循序分支,`seen.update(空)` 無事發生。
  - 1 個去重後的 job:`len(jobs) > 1` 不成立,走循序分支。
  - 50 個項目共用同一指令:`jobs` 為 1,走循序分支,只跑一次。
  - workers 大於 jobs:`min(workers, len(jobs))`,正確。
- **逾時**:`LUMOS_TEST_TIMEOUT=0` 得到 `None`,逾時退為 `10**6`,整套跑仍取 `max(600, 0)=600`。極小的逾時值每支都逾時,和循序一致。
- **`_wall`**:`_t_run` 在 `_time.monotonic()` 取得,`round(…, 1)`。`secs_kind` 只在 `secs is not None` 時寫入,所有呼叫 `_bound_tests_log(..., secs=...)` 的路徑(red、unfilterable、green)都符合。
- **S6 與 S2 的時序**:S2 的「2 秒內看到別支標記」在機器極忙(兩支啟動相差超過 2 秒)時可能判成循序而紅。這是推測,我沒有重現,不當 finding 報。

## 修補鏡頭三問

**① 原問題的修復效果有何行為證據?**
- 等待安靜:`t_bound_tests_parallel_wait_is_quiet`,我讀碼確認逐條 `join(0.1)` 的設計成立,沒有重跑。
- 中斷後不再派新的:`t_bound_tests_parallel_interrupt_stops_dispatch`。這支在我的環境重現為紅(見 finding 1),所以目前拿不到有效的行為證據。
- 出錯馬上結束:`t_bound_tests_parallel_error_stops_fast`,我跑了 `-k t_bound_tests_parallel_error_stops_fast`,結果是 `4 passed, 0 failed`(含同名前綴的幾支),這支本身綠。
- 單調時鐘:`t_bound_tests_secs_monotonic` 讀碼成立。
- 提醒去重:`t_bound_tests_parallel_config_values` 讀碼成立。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
- 正常路徑(jobs 大於 1、parallel 為 2 到 16)的結果組裝照原順序,`tails` 與去重鍵都沿用。
- 錯誤路徑會往外丟,但見 finding 3 的孤兒行為。
- 規格閘的 `_spec_gate_judge_items` 與修正關卡都吃同一個 `_run_bound_tests`,回傳形狀沒變,`secs` 欄位在這兩條路徑沒有被消費。

**③ 新發現的同一案例在修前、修後各是什麼結果?**
- finding 1 的案例在修前版沒有這支測試,所以修前結果為「無對應測試」,修後在冷載入下紅。
- finding 2 的 `pgrep` 清掃在修前版也有(差異第 328 行是修前),修後新增 S7 的同一寫法,屬沿用錯誤。
- finding 3 沒有在修前版逐版實測,標未判定。

**案例證據**
- claim:S7 在沒有 bytecode 快取時紅。
- input:`3daa00a8` 的乾淨 clone 上跑 `python3.14 scripts/test_lumos.py -k t_bound_tests_parallel_interrupt_stops_dispatch`。
- expected:`INTERRUPTED` 出現、`started` 不超過 2 支。
- case_source:binding 的 GA/repair 案例 `t_bound_tests_parallel_interrupt_stops_dispatch`。
- before:`d3ac862`,無此測試,未驗。
- after:3 次都是 `1 passed, 1 failed`,第一個失敗斷言是 `並行 S7 前置`。
- attribution:有證據的修復回歸。

**未驗範圍**:我沒有跑全套測試,沒有在 Linux 或 root 身分下實跑,沒有驗證 `parallel` 為 4 時本 repo 測試在同一個 repo 根下並行互相踩踏的可能性。

## 圖譜鏡頭

- **bound-tests-gate(★INVARIANT★ 綁定測試逐支真跑、任一紅/懸空/fake/bad-name/unproven/unfilterable 就擋)**:行為保留。`plan` 對懸空、偽證據、不合法名稱照樣產 `red`,`no-cmd` 照舊,`unproven` 與 `unfilterable` 的後段判定程式沒動。`secs` 改成牆上時間,筆記已同步改。這個節點的行為仍成立,我沒有發現合約被破壞。
- **guard-kill**:`_kill_run` 本體沒改,rc 優先序與 `--json` 純度合約不受影響。
- **測試假綠形態(還原翻紅釘要配前置斷言)**:新測試 S5(`RAISED`)、S6(兩支都綠且牆上時間)、S7(`INTERRUPTED`)、secs_monotonic(`status == green`)都有前置斷言,形狀符合。S7 的前置斷言在冷載入時正是那條翻紅的斷言,也就是前置有效,但觸發條件不穩定(finding 1)。
- **design-loop、lumos-cli-read、lumos-cli-lifecycle、loop-convergence-recording、pitfalls-code-loop**:diff 沒碰它們的行為路徑,不受影響。
- 其餘「超出上限只列名」的節點,我沒有逐一讀,不下結論。

總結:最高等級 major
