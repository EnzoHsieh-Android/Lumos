severity: minor

我逐 hunk 讀完整份 diff,設定值、項目數、平台、逾時、新測試這幾組極端輸入都走過一遍,只找到一個有重現的缺陷,另有一處計劃與測試不一致。

**1. 主流程等待迴圈在 threads[0] 結束後變成空轉**
severity: minor
blocking: 否
引句:「            threads[0].join(0.1)」
file: `scripts/lumos:48212`(此行號是我讀工作樹時估的,錨點以上面引句為準)
1. 輸入:`parallel=4`,而去重後的工作長短不一。這是本 repo 的實際情況:51 支裡有 41 秒、23 秒、18.5 秒各一支,其餘約 1 秒。另一個等價情況是 `workers=16`、`jobs=2`,其中一支很慢。
2. 路徑:佇列取空後,`_worker` 在 `except _queue.Empty: return` 離開。`threads[0]` 通常最先取到短工作,也最先結束。
3. 之後 `while any(th.is_alive() ...)` 仍為真,因為還有別的執行緒在跑慢測試。但 `threads[0].join(0.1)` 對已結束的執行緒會立刻返回,並不會等 0.1 秒,迴圈變成滿速空轉。
4. 最小重現是我用同樣結構寫的獨立程式(三個 0.01 秒的工作加一個 3 秒的工作,4 個 daemon 執行緒):
   - 輸出 `iterations 3871302 cpu 2.98`,也就是約 3 秒內空轉 387 萬圈、吃滿一顆核心。
   - 對應到真實情況,尾端那支 41 秒的測試跑完前,主執行緒會一直佔一顆核心。這會跟尾端的測試搶 CPU,逼近 180 秒逾時的測試更容易轉紅,與計劃「實務隱患」那段的假設相反。
5. 此問題不影響結果正確性;可以改成對所有執行緒輪流 `join`,或在迴圈裡 `time.sleep(0.1)`。

**2. S4 條款與測試的秒數不一致**
severity: minor
blocking: 否
引句:「兩篇筆記綁同一支約 1 秒的測試時,閘回報的 secs 應是跑測試那段的牆上時間(約 1 秒)」
1. 計劃 S4 寫「約 1 秒」。測試 docstring 也寫「約 1 秒」,但實際在 `run.py` 注入 `time.sleep(2.0)`,斷言區間是 `1.8 <= secs < 3.5`。
2. 這是計劃、docstring 與斷言三處自相矛盾。斷言本身沒問題,2 秒對上相加值約 4 秒。
3. 在慢速的 CI 上,若牆上時間超過 3.5 秒,測試會變成假紅。上界只留 1.5 秒餘裕,而單支測試要重載 4 萬行以上的模組。

**邊界逐項判定(沒有 finding)**
- **`parallel` 的各種值:**
  - 2、16 回傳原值,17、1、0、-1、2.0、True、"4"、`[]`、`{}`、NaN 都回 1。
  - `v != 1 or isinstance(v, bool)` 讓 `1`、`1.0` 不出聲,`True` 出聲,與計劃一致。
  - 巨大整數落在 `<= 16` 之外,回 1 並出聲,沒有溢位問題。
- **`bound_tests` 與 config.json 的壞形狀:**
  - `bound_tests` 為 null 回 1 且不出聲,為 `[]`、"x"、4 時出聲並回 1,這條也有測到。
  - config.json 不存在、空檔、編碼壞掉都被 `except Exception` 吞掉回 1,不出聲。「設定讀不了」和「沒寫」在使用者看來無差別,其他讀設定的地方也是同一慣例。
  - config.json 是 `[]` 或 "x" 時,`isinstance(cfg, dict)` 擋住,回 1。
- **項目數與執行緒數:**
  - 0 項或 1 項時 `len(jobs) > 1` 為假,走循序路徑。`workers=16`、`jobs=2` 時 `min(workers, len(jobs))` 只開 2 條執行緒,結果正確。
  - 同一指令被 50 項共用時,`jobs` 只有 1 個鍵,走循序並照舊去重。
- **多平台與整套跑:**
  - 一個平台的 root 不存在時,該支 `_kill_run` 丟 OSError,`_worker` 以 `BaseException` 收下,主流程在 0.1 秒內往外丟。
  - 沒有 `{method}` 的整套跑(逾時 600 秒)與可過濾的混在一起時,兩者各自用自己的 `timeout`,互不影響。
  - 同一批裡的整套跑會與其他測試同時跑。這是計劃已寫明的取捨,消費專案自行決定要不要打開。
- **逾時與 `LUMOS_TEST_TIMEOUT=0`:**
  - `per_test=None` 時,可過濾的測試用 `10**6` 秒。結果段的 `int(timeout)` 只在 `to` 為真時執行,而 `10**6` 的逾時實際走不到,所以沒有新增的 `TypeError` 路徑。這段與改動前一致。
  - 逾時極小時,每支各自計時,行為與改動前一致。
- **secs 與記帳:**
  - `_wall` 在 `_run_bound_tests` 前後各量一次,前面的 `whole-suite-deferred`、`no-config` 路徑 secs 是 0 或沒帶,不受影響。
  - `_bound_tests_log` 只在 `secs is not None` 時加 `secs_kind`。呼叫端中帶 `secs=` 的只有 red 與 green 兩處,都傳牆上時間,沒有混到逐項相加的值。
- **新測試在 CI 與 root 下:**
  - 以 root 執行時,root 不存在仍是 OSError(root 權限不影響目錄是否存在),S5 照樣成立。
  - S5 用 `pgrep -f` 收尾殺程序,在沒有 `pgrep` 的最小容器會丟 FileNotFoundError。這是環境假設,不算 finding。
  - S2 的「同時跑」判斷靠 2 秒內互相看到標記,而不是計時重疊,在慢機器上不易假紅。

**圖譜鏡頭**
- **`bound-tests-gate`(★INVARIANT★):**
  - 這份 diff 沒破壞它宣稱的行為。任一支紅、懸空、方法名不合法或證不出跑過,仍回 `blocked=True` 且 rc1;沒 `run_cmd`、算不出 diff、無固定席、沒綁定時,仍不擋但寫帳。
  - 判紅綠的 `results.append` 分支只是搬位置,三種判定(紅、no-cmd、unproven/green)與去重鍵都沒變。
  - 在 `bound_tests` 區塊不合法的臨界情況下,閘會退回循序執行,不會放行。
- **`guard-kill`、`lumos-cli-read`、`測試假綠形態`、`lumos-cli-lifecycle`、`design-loop`:** 牽連檔只是 `scripts/lumos` 與 `scripts/test_lumos.py`,diff 沒碰到它們各自的合約行為。
  - 唯一接觸點是 `_spec_gate_judge_items` 共用 `_run_bound_tests`,但它丟掉第 6 個欄位(`_secs`),不受 secs 語意變更影響。
- **`loop-convergence-recording`、`pitfalls-code-loop`(★RISK★):** 沒有具體受影響的 file:line,不臆測。

總結:最高等級 minor
