severity: minor

# 邊界與輸入席報告(code-android-mem-stability r2,邊界-sonnet)

做法:我在臨時目錄各取出修前 1e47929e 與修後 44d93aba 的完整工作樹,把 `scripts/lumos` 當模組載入,對判定函式與設定檢查逐欄位灌極端值。極端值包括缺欄位、null、0、-1、-5、1.5、true/false、字串、空字串、空清單、空物件、NaN、Infinity 和 10**400。另外用 `python3.14 -I <版本>/scripts/lumos macrobench --repo <臨時 repo> [--stability …] [--check-config] [--json]` 各跑一次。跑完已用字面絕對路徑刪除臨時工作樹與目錄,沒碰 adb 與裝置。

## Findings

### 1. unreachable 的 before 或 after 不是物件時,判定噴 AttributeError 而不是列成跳過(rc=1、整份輸出丟失)
severity: minor
blocking: 否

引句:「b, a = s.get("before") or {}, s.get("after") or {}」

- 輸入:stability.json 的 `unreachable.before` 設成 `[1]`、`"x"`、`1.5`、`true` 或 `-1`(任何非空且不是物件的值),門檻檔有 `native_unreachable` 條目。
- 預期:列成跳過並說原因。計劃 S11 與 WHY「結果不是有限數列成跳過」都說讀不到不得噴例外。
- 實際:`AttributeError: 'list' object has no attribute 'get'`,rc=1,整份判定沒印出來。
- 同族對照:同一個修補把 heap 補成「缺 before 或 after(或不是物件)」,但 unreachable 沒套同一條。
- 命令:`lumos macrobench --repo <只有 stability 段的 repo> --stability stab_unr.json`。修前與修後都是 traceback、rc=1。
- 歸因:有證據的原有漏查。修前修後行為一樣,不是修補造成。
- 現實面:收集腳本只寫 dict 或 None,正常路徑碰不到。只有手改或外來格式的檔會觸發。

### 2. 違規與結束紀錄的清單裡有非物件元素時被靜默丟掉,列成達標;型別不是字串時文字輸出噴 TypeError
severity: minor
blocking: 否

引句:「v = [x.get("type") for x in s["violations"] if isinstance(x, dict)]」

- 輸入 A:`strictmode.violations = ["DiskReadViolation"]` 或 `[1]`。
- 預期 A:格式不對,列成跳過。
- 實際 A:非物件元素被丟掉,判成 `[達標]`。`exits.new = ["crash"]` 或 `[1]` 同樣判成達標(pid 都一樣時)。
- 輸入 B:`violations = [{}]` 或 `[{"type":5}]`。
- 預期 B:判沒過並印出明細。
- 實際 B:判定本身是沒過,但文字輸出時 `"、".join(r.get("violations", []))` 噴 `TypeError: sequence item 0: expected str instance, NoneType found`。rc=1,「沒達」的結果沒印出來。`--json` 輸出不噴,JSON 裡是 `violations:[null]`。
- 命令:`lumos macrobench --repo <repo> --stability stab_bad.json`,修前修後都是 rc=1 與 traceback。
- 同族對照:本輪修補只加了「violations、new 要是清單」,沒擋元素型別。
- 歸因:有證據的原有漏查,修前修後一樣。
- 現實面:收集腳本的 violations 一定是 `{"type": 字串}`,正常路徑不觸發。

### 3. 設定檢查對 warmup、cycles 沒有上界;修補把結果檔 cycles 的超大整數從「跳過」變成「通過」
severity: minor
blocking: 否

引句:「n = stab.get("cycles")」

- 輸入 1:設定 `warmup=10**18, cycles=10**400`。
- 預期 1:`--check-config` 擋下。同一函式對 max_record_s 已經加了 1 到 86400 的上界,這裡卻沒有。
- 實際 1:修前修後都回 None,合格。收集腳本會拿它當驅動輪數去跑,實際上跑不完。
- 輸入 2:結果檔 `cycles=10**400`,heap 的 Foo 從 1 增加到 100,門檻檔有 `java_growth`。
- 預期 2:判沒過,或列成跳過。
- 實際 2:
  - 修前 1e47929e:跳過「結果檔的 cycles 缺了或小於 1」。原因是 `_macrobench_num` 遇到 OverflowError 回 False。
  - 修後 44d93aba:判 **通過**。`_secev_int` 取代了 `_ms_val`,不再擋超大整數,`need = n * 1` 大到永遠不會有類別達標。
  - 對照:`cycles=5` 同一份 heap 兩版都判沒過。
- 歸因:
  - 結果 2 是有證據的修復回歸,觸發值只有超過約 1e308 的整數(修前會跳過、修後會通過),因此是 minor。
  - 結果 1 是有證據的原有漏查。
- 現實面:收集腳本寫入的 cycles 等於設定值。真正的缺口是設定檢查沒有上界。

### 4. 只有 stability 段、沒有門檻檔(或門檻檔為空清單)時,`lumos macrobench` 整份無輸出、rc=0
severity: minor
blocking: 否

引句:「if cfg is None and not any(res[k] for k in ("threshold_failures", "threshold_passed", "threshold_skipped")):」

- 輸入:`.lumos/macrobench.json` 只有 stability 段(合格),沒有 `macrobench-thresholds.json`,或門檻檔是 `{"thresholds":[]}`,再給 `--stability` 一份結果檔。
- 預期:至少說「沒有門檻可判」。這條警告只在 `cfg is None` 時才印。
- 實際:什麼都不印,rc=0。使用者忘了寫門檻檔,看起來就像全部通過。
- 命令:`lumos macrobench --repo <repo> --stability stab_ok.json`,修前修後都是空輸出、rc=0。
- 歸因:有證據的原有漏查,這段函式修前就是這樣。
- 這不是判定被列成通過,只是靜默無操作,所以只列 minor。

## 已驗主張(兩版證據)

**官方分級區間邊界(post 版,app 與 game 各一次)**
- 區間含下界、不含上界:3199.99 與 18432 跳過;3200、4800、6800、9216、14336 各進下一級;每個上界 -0.01 還在前一級。
- 每級限額都是「峰值剛好等於上限判通過、+1 KB 判沒過」,與計劃 WHY(低於 3200 或至少 18432 沒有官方數字)一致。
- total_mem_mb 為 -1、0、缺、NaN 一律跳過。這項我只跑了後版(未對修前逐格重跑),邊界與計劃一致。

**設定檢查**
- 只有 stability 段且 `results_dirs` 不寫或給 `[]`:兩版 `--check-config` 的結果是修前 rc=2、修後 rc=0,這是預期的修復。
- 兩者都有:兩版皆 rc=0。
- 沒有 stability 段而 `results_dirs=[]`:兩版皆 rc=2。
- `results_dirs=null` 加 stability:兩版皆 rc=2。這與計劃「不填或空清單」一致,屬正常行為。
- stability 為 null、`{}`、`[]` 或 `"x"`:兩版皆 rc=2 並給出訊息。

**欄位矩陣**
- `max_record_s` 的 0、負數、NaN、Infinity、布林、字串、0.5、86401、1e15:後版全擋。修前 `1e15`、86401、0.5 會通過。
- `category=[]` 或 `{}`:修前 TypeError,修後正常回錯誤。
- 門檻 check 條目的 max_bytes、min_per_cycle、exclude_prefixes、class、max、max_block_ms 對 0、負數、NaN、Infinity、布林、字串、空清單、`[""]`、`["a",1]`、10**400:兩版都沒有例外,型別錯誤都擋下。
- 未知欄位(例如 exits 條目寫 `max`、peak_vitals 條目寫任意鍵)只有後版擋下。
- decided_at 的全形數字、`2026-10-24\n`、`2026-02-30`、`20261024` 兩版都擋。

**pids**
- 欄位矩陣的結果,後版 pids 的所有壞形狀(缺、null、0、負數、小數、布林、字串、空清單、單元素、物件)都跳過。需要完整輪數的五種條目跳過,理由是 pid 讀不到。
- 修前版對 `values=-1`、1.5、true、NaN 會噴 `TypeError: int object is not iterable`。這一點是修復有效。

**exits 崩潰類例外**
- 有 `{"type":"crash"}` 或 `native_crash` 或 `anr`:pid 全相同判沒過,pid 讀不到時修前跳過、修後判沒過。這是計劃要的行為。
- 大寫 `CRASH` 或 type 缺漏或 type 為清單:不算崩潰類,以 pid 判。
- 沒有崩潰類紀錄時 `new` 為空且 pid 讀不到:跳過。
- 結果檔 scenario 或 device_model 不符:跳過,優先於 exits 判定。
- 我沒找到在不該判的時候判沒過的路徑。崩潰類型只來自收集腳本的 EXIT_TYPES 或 MemoryLimiter,而且是用前後差集算出的 new。
- 沒有證據的部分:`new` 本身是否可能混入前一輪的舊紀錄,取決於收集腳本在裝置上的行為,我沒去驗。

**其他**
- frozen 在 max_block_ms 已設而阻塞量為 -1、缺、布林、字串或 NaN 時,後版跳過。修前會當成沒超限而通過,這是修復有效。
- heap 的 classes_seen 缺、為 0、不是整數時,兩版都跳過。這項我只對後版驗了擋下,修前沒有這個檢查。
- stability.json 為陣列、空檔、NaN、目錄或不存在:兩版皆 rc=2。

## 三問回答

1. **原問題修復效果:** 上述有對照的改動,pid 壞形狀、`max_record_s`、`category` 清單、frozen 的 max_block_ms、`results_dirs` 空清單、未知欄位、崩潰紀錄不靠 pid,這幾項我都實測到「修前出事、修後正確」。
2. **修補處的正常、錯誤與相鄰路徑:** 正常路徑(7 種全過)兩版輸出一致。相鄰路徑裡 finding 1、2 是同族但沒補到的點,finding 3 的結果 2 是修補引入的小回歸。
3. **新發現的同一案例在兩版的結果:** 已逐條附在每個 finding 裡(修前 1e47929e 與修後 44d93aba)。

## 未驗範圍
- 沒對真實 trace_processor 與 adb 輸出做驗證,只對 stability.json 的形狀做了邊界測試。
- 收集腳本本身的邊界(例如 `cycle_numbers` 遇到 `int("nan")`)不在本席被審的那一包裡,只讀過,沒跑過。

最嚴重 severity:minor,blocking 共 0 條。
