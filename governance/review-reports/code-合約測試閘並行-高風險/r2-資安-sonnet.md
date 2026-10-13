severity: clean

沒有可利用的洞,沒有 finding。

## 逐類檢查

1. **不可信輸入流到危險操作:已看,無。**
   - `bound_tests.parallel` 只有「2 到 16 的 int(排除 bool)」才會被採用。
   - 這個值只用來決定 `range(min(workers, len(jobs)))` 的執行緒數量。它不進 shell、不進路徑,也不進模板或 eval。
   - 組出 shell 指令的路徑沒動:`_run_cmd_expand(run_cmd, method)` 和 `_kill_run(..., shell=True)` 都是既有程式。
   - 這次新增的 `plan`、`jobs`、`seen` 只重排「誰先跑」,命令字串、`root` 和 `cwd` 的來源跟原本循序版完全一致。
   - 提醒訊息會把設定值原樣印出,但用的是 `{v!r}` 和 `{bt!r}`。str 的 repr 會把 ESC、控制字元和 bidi 覆寫字元(都不可列印)轉成跳脫序列,list 和 dict 內層字串也一樣。所以惡意設定檔無法靠它往終端注入控制碼,頂多讓提醒變長。
   - 訊息輸出到 stderr,不進 JSON 或治理帳。
   - 治理帳新增的 `secs_kind` 是固定字串 `"wall"`,不是外部輸入。

2. **登入與權限:已看,無。** 這次改動沒有認證或授權邏輯。

3. **密鑰與個資:已看,無。** 設定值和提醒訊息裡沒有密鑰類欄位,新增的 log 欄位也不帶個資。

4. **加密與傳輸:已看,無。** 沒有網路或加密程式碼。

5. **執行邊界:已看,無新增攻擊面。**
   - 陌生 repo 的 `.lumos/config.json` 能讓推送閘同時開最多 16 個程序。但能寫這份設定的人本來就能寫 `run_cmd`(`shell=True`),讓閘執行任意指令。所以並行數沒有提升權限,只是資源用量,屬於其他席(DoS)的範圍。計劃筆記和手冊也都誠實寫了這個信任邊界。
   - 工作執行緒是 daemon,取工作用 `queue.get_nowait()`,結果寫入 `seen[key]` 時有鎖保護。沒有共用的可預測暫存檔:`_kill_run` 每次用 `tempfile.TemporaryFile`(匿名檔)和 `start_new_session=True`,沒有符號連結競爭的機會。
   - 測試檔裡會被 CI 真的執行的命令也看過。
     - `t_bound_tests_parallel_error_stops_fast` 和 `t_bound_tests_parallel_interrupt_stops_dispatch` 的 `finally` 用 `pgrep -f str(d)` 加 `SIGKILL`。`d` 是 `tempfile.mkdtemp(prefix="gctl-btpar-")` 產生的隨機目錄,正則特殊字元只有 `.` 和 `-`,不會殺到別人的程序。
     - 它也殺不到「測試總檔自己」,因為測試總檔的 cmdline 不含 `d`。
     - `probe` 的參數都用 argv 傳遞(`sys.argv[1..3]` 加 `json.loads`),沒有字串拼進 `-c` 的程式碼,所以沒有注入。
     - `pgrep -f` 只比對 cmdline,不比對 cwd。慢測試子程序(`python run.py t_slow*`)的 cmdline 不含 `d`,可能殺不到,會殘留最多 12 秒。這是清理不完全,不是漏洞,也不會殺到無關程序。⚠ 未實測,純讀碼推論。
   - 子程序成為孤兒(例外或 Ctrl-C 後繼續跑到逾時)是 `_kill_run` 既有的行為,循序版按 Ctrl-C 一樣會這樣。它不跨越信任邊界,所以不算洞。

6. **行動端:已看,無。**

## 新加依賴

已看,無。只用標準庫的 `threading` 和 `queue`,檔內 import 就在函式裡。

## 修補鏡頭(資安範圍內的結論)

- 修補是把 ThreadPoolExecutor 換成自建 daemon 執行緒。我獨立讀了 `_worker` 和 `errs` 的使用,沒有新增資料外洩或注入路徑。
- 例外收集 `except BaseException` 之後由主流程重新 raise,沒有吞掉 `KeyboardInterrupt`。
- 歸因:無 finding,不適用。
- 未驗範圍:沒有實際執行測試,所以並行行為的正確性、競態和效能不在我的範圍,留給其他席。

總結:最高等級 clean
