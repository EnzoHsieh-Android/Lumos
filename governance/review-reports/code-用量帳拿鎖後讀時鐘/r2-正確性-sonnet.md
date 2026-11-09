severity: minor

**F1 新建帳時,拿鎖後才讀到壞時鐘,會留下 0 位元組帳檔,之後每次都停在「版本或結構不可判」**
severity: minor
blocking: 否
引句:「            # 拿到寫鎖之後才讀時鐘:記帳時間照拿鎖先後排,同時搶名額的一方不會被誤判成時鐘回撥」
失敗場景:
- 帳檔不存在,鎖前那次讀時鐘正常、拿鎖後那次是 NaN 或負數(我用 `side_effect=[1.8e9, nan]` 模擬)。
- `sqlite3.connect` 加 `BEGIN IMMEDIATE` 已經建出空檔,這時才拋「時鐘不可判」,空檔留下。
- 之後 `fresh=False` 且 `user_version=0`,每次都拋「用量帳版本或結構不可判」,要手動刪檔才能恢復。
- 這正是鎖前驗證想避免的症狀,所以「時鐘壞時不碰帳檔」只在鎖前那次讀就壞時成立。

證據:`exp.py` E1,在 `/tmp/lumos-seat-work/code-用量帳拿鎖後讀時鐘/正確性-sonnet/`。
- 修後 `50d731ca`:`E1 exists True 0`,再呼叫得到「用量帳版本或結構不可判」。
- 修前 `cbb265c6`:同一個 `side_effect` 只會讀一次時鐘,修前沒有「鎖前正常、鎖後才壞」這種情境,無法拿來做同案例對照。
- 修前的 E2(單次壞時鐘)也留下了空帳檔,那正是修補要解的問題。

歸因:有證據的修復回歸,指修補新增的第二次讀時鐘所開出的新窗口。實務機率極低,因為兩次讀取只隔幾微秒。

測試缺口:`test_attempt_ledger_bad_clock_after_lock_stops` 先用 `now=t0-20000` 建好帳,沒涵蓋新建帳的情況,所以抓不到這個案例。

最小重現:
```
python3.14 -I exp.py after
```
看 E1 那幾行。

修法建議(非必要):鎖後壞時鐘若是新建帳,就刪掉剛建的空檔;或把鎖後驗證放在取得 `fresh` 判斷之前。

**修補鏡頭三問**
1. 原問題的修復效果:
   - 我重做了搶輸的情境 E4:另一方在連線時插入 `t0+0.5`,牆上時間跳到 `t0+1`。修前和修後都得到 `False`,沒有拋時鐘回撥例外。
   - 修後拿鎖前讀的值只用於 `clock_ok`,記帳用的 `now` 在鎖內重讀。`float(now)`、`INSERT` 和 `now < max(initialized, latest)` 都用鎖後的值,沒有地方誤用鎖前的值。
   - 因為 `time.time()` 是在鎖內讀的,記帳時間照拿鎖先後排。
   - 修前版本的搶輸情境要靠 E4 的模擬才看得出來,我沒另外還原舊版去跑 E4 的紅燈。
   - 變異檢查(在 `--shared` clone 上做):
     - 拿掉「鎖後重讀」:3 條測試出現 1 failure、1 error。
     - 拿掉「鎖前驗證」:2 條紅。
     - 兩道檢查各自都有測試會紅。
   - 包裝測試 `t_probe_attempt_ledger_clock` 檢查 `returncode==0` 且輸出含 `Ran 3 tests`;子測試紅時 `returncode` 非零,不會假綠。
2. 相鄰路徑:
   - 傳了 `now` 的路徑沒變:`read_clock_after_lock=False`,E3 在兩版都是「時鐘不可判」且不建檔。
   - `limit=0` 提前返回,仍在 `clock_ok` 之前。
   - 兩個呼叫端沒改:`run_one_codex` 兩處呼叫 `claim_model_attempt` 都沒傳 `now`,另有一處呼叫 `attempt_ledger_remaining` 也沒傳,三處都走新路徑。
   - 錯誤路徑上,`finally` 會 rollback 並關閉連線,檔案還是由 F1 那條路徑留下。
3. 新發現 F1 的同一案例在兩版的結果:修後會留下 0 位元組空帳檔並卡死帳本;修前沒有這個情境,但同類的單次壞時鐘在修前也會留空檔。

**待驗行為**
- 行為①(沒指定時間、時鐘壞、帳檔不存在時不留空檔):成立。NaN 和 -1.0 兩種壞值,修前 `exists True`,修後 `exists False`。僅限「鎖前那次讀就壞」,鎖後才壞見 F1。
- 行為②(拿鎖前正常、拿鎖後才壞時照樣停):成立。已有帳時拋「時鐘不可判」且不記帳,測試覆蓋;新建帳時雖然停了,卻會留空檔(F1)。
- 行為③(搶最後一個名額,搶輸方得到 False):成立。E4 在修前和修後都得到 `False`。
- 行為④(時鐘真的倒退照樣停止):成立。`now=t0` 早於 `latest` 時拋 `ProbeAttemptLedgerError`,測試有覆蓋。
- 行為⑤(呼叫端傳了 `now` 時行為跟修前一樣):成立。`now` 不為 None 時,不讀牆上時鐘,檢查位置與修前相同。

**圖譜鏡頭**:固定席節點(`codex-harness`、`測試假綠形態`、`授權與歸屬`、`autonomous-iteration-loop`、`lumos-cli-read`、`bound-tests-gate` 等)都沒被破壞。
- 本次只動一個交易函式、兩條測試和一個包裝測試。
- 沒有新增授權檔,沒有改 SPDX 檔頭或 `_VENDORED_TOOLKIT`。
- 「還原翻紅釘需前置斷言」那條,test 1 靠 `racing_connect` 保證現場成立,test 2 靠 `assertFalse(ledger.exists())` 斷言。

**角色卡**:`be-api-compat` 不影響,因為函式簽章不變、帳檔格式不變,新舊版可互讀。`be-authz` 不適用,因為沒有端點。

總結:最高嚴重度 minor。

相關檔案:`/Users/enzo/orca/workspaces/lumos-toolchain/flaky-race/scripts/scenario_probe.py`(`_attempt_ledger_transaction`)、`/Users/enzo/orca/workspaces/lumos-toolchain/flaky-race/scripts/test_autonomous_loop.py`。實驗腳本在 `/tmp/lumos-seat-work/code-用量帳拿鎖後讀時鐘/正確性-sonnet/exp.py`。
