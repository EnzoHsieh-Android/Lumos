severity: minor

## r1 C-38、C-39 新排除條件讓長方法鏈在作用域大括號裡的掃描時間變成三次方成長
severity: minor
blocking: 否

最壞輸入是在作用域大括號裡放一條很長的方法鏈,旁邊再有一個 `launch`。我用真規則 `configs/ast-grep/kotlin-choice/sgconfig.yml`,在修前 763081c0d 與修後 926c72056 各掃一次,量到的時間如下。

| 輸入 | 修前 | 修後 |
|---|---|---|
| `supervisorScope { launch{a()}` 後接 100 個 `.join()` | 0.03s | 0.11s |
| 同上,200 個 | 0.04s | 0.62s |
| 同上,300 個 | 0.07s | 1.94s |
| 同上,500 個 | 0.15s | 8.2s |
| 同上,1000 個 | 0.52s | 61s |
| `coroutineScope { val r = x` 後接 600 個 `.add(1)`,再兩個 `launch` | 0.86s | 14.2s |
| `coroutineScope` 裡 300 個 `.map { it }` | 0.19s | 2.15s |

- **成因:** 走到 `api.yml` 的 C-38、C-39 `utils.child-co` 新加的 `not: inside: navigation_expression … inside: call_expression`,每個後代呼叫節點都要多算一次。這一層被 `has-co` 與 `many-co` 的後代掃描重複評估,所以三次方成長。
- **輸出與命中:** 輸出位元組沒有變大,反而變小,因為鏈上被排除的呼叫不再命中。
- **時限:** 一個作用域裡有 1000 個鏈節的檔案(61s)會超過推送前掃描共用的 `_KT_SIT_BUDGET = 30.0`,300 個鏈節以內都不到 2 秒。現實程式碼很少有這麼長的鏈,所以只標 minor。
- **覆蓋缺口:** S9 沒有覆蓋這個形狀。
- **未判定:** 我沒有做把新排除條件拿掉的反證,成因是用修前、修後對照推出來的。

引句:「    not:      inside:        kind: navigation_expression        has: {kind: navigation_suffix, regex: '^(\?\.|\.)\s*(await|join)$'}        inside: {kind: call_expression}」

歸因:有證據的修復回歸。修前 500 個鏈節 0.15s,修後 8.2s;其他輸入在兩版的時間與輸出位元組一致,只有這個形狀變慢。

## 已驗主張與未驗範圍(不計為 finding)

**已驗,結果良好:**
- C-38 在單一作用域平鋪 2000 與 6000 個 `launch`:修前、修後都是 2.3s 與 21.6s,輸出 1.0MB 與 3.1MB,命中 1 處。這是 `many-co` 的 `precedes: stopBy: end` 既有的二次方,修補沒動它,是上輪沒人看的角落。
- 平鋪 2000 與 6000 個 `async{}.await()`:0.22s 與 0.65s,零輸出,排除條件在平鋪輸入上沒有讓規則變慢。
- 3000 組作用域檔:修前 12.3MB、修後 10.2MB,輸出沒有放大。
- 作用域巢狀 50、100、200 層:最慢 0.53s,輸出約 0.25MB 以內。
- C-48 巢狀 200 與 600 層:修前、修後完全相同(0.36s 與 3.1s,194KB 與 1.07MB)。
- C-48 兩萬個 `extraBufferCapacity` 具名引數:修前、修後都約 49s。這是既有的寬引數二次方,修補沒動,不計為修復回歸。
- C-48 兩萬行 `extraBufferCapacity = 0x0`:修後零命中、輸出 13.6MB,修前 26.5MB,零判斷運作正常。
- C-53 巢狀 400 層:修前、修後都是 0.5s、557KB。
- `zero-int` 的 `prefix_expression` regex 是線性,沒有回溯風險。
- 我實跑 `python3.14 scripts/test_lumos.py -k t_choice_scope_rule_output`,14 個檢查全過,總共 1.5s,逾時上限 180s。這支測試是在目前的 HEAD 860d97e 上跑的,不是 926c720,但是檢查內容與 patch 相同。
  - **雙重否定的檢查有咬力:** 拿掉雙重否定時,C-48 巢狀 200 層輸出 73MB(有雙重否定時 194KB),C-53 輸出 90MB(有雙重否定時 197KB),作用域 100 層輸出 46MB(有雙重否定時 77KB)。1MB 上限與 10 倍門檻都抓得到。
  - **慢機器:** 每次 `ast-grep` 呼叫的 `timeout=120` 約有 80 倍餘裕。
  - **記憶體:** `capture_output` 會暫存 73 到 90MB,屬於短暫峰值。
- `_cb_points` 與 S9 都改用 `TemporaryDirectory`,例外路徑會刪暫存。修前 `_cb2_points` 與 `_cb3_points` 的 `mkdtemp` 從不刪,這是修補帶來的改善。

**未驗範圍:**
- `_cb_points` 內的 `subprocess.run` 沒有 `timeout`,修前就沒有;在沒有 ast-grep 卡住的證據下,不算 finding。
- 測試 `t_choice_samples_batch2` 的 `mkdtemp(prefix="gctl-cb2rules-")` 沒刪。測試執行器把 `TMPDIR` 隔離進 `gctl-run-*`,綠燈時整個清掉,所以不算洩漏。
- 沒有檢查 `scripts/lumos` 裡 `_choice_err_start` 與 `_CHOICE_CALL_NAME_RE` 的重構,除了讀 patch 外沒有實跑。兩者都是 O(1) 的 regex match,沒有新的子程序或大量讀入。
- 沒有跑任何不帶 `-k` 的全套測試。

總結:最高嚴重度 minor,blocking 共 0 條
