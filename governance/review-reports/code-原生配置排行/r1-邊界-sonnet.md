severity: major

## Findings

### 1. 長函式名或長呼叫者會讓整行被截掉,「還留著多少」這個數字消失
severity: major
blocking: 是 — 排行最重要的數字在輸入落在規格自己允許的範圍內時就不見,屬於會做出錯誤輸出。
引句:「print(f"  {i}. {_events_clean(line, 500)}")」
file: `scripts/lumos:40109-40110` 這行先拼出 `func @ so ← caller:還留著 X MiB(N 位元組)(標籤)`,再整行交給 `_events_clean(line, 500)`。
file: `scripts/lumos:19364` `_esc_clean` 超過 limit 就 `out[:limit] + "…"`。
收集腳本允許 func、caller 各 500 字(SQL 的 `substr(...,1,500)`),lumos 卻把整行壓在 500 字。
失敗場景:
- func 長 497 字的 C++ 模板名,或 caller 長 500 字,整行超過 500。
- 尾端的「還留著 5.0 MiB(5242880 位元組)」和「(沒有符號)」「(系統函式庫)」標籤整段被截掉,只剩「…」。
- 越長的名字越會讓人看不到大小,而長的模板名正是原生配置排行常見的輸入。
重現:
```
cd /tmp/lumos-seat-work/code-原生配置排行/邊界-sonnet/ && python3.14 t3.py | cut -c1-60,480-600
```
輸出第 1 行以 `…` 結尾,沒有 MiB。第 2 行是 func=g、caller 500 字,同樣在 `ccc…` 後被截。

### 2. retained 是超大整數時,印出排行會丟 OverflowError
severity: major
blocking: 是 — 規格寫「不噴例外」,形狀檢查卻放行了會讓列印崩潰的值。
引句:「line = f"{x['func']} @ {x['so']} ← {x['caller']}:還留著 {x['retained'] / 1048576:.1f} MiB({x['retained']} 位元組){tags}"」
file: `scripts/lumos:40109`
file: `scripts/lumos:39988` 鄰近的 `_macrobench_num` 已經為「JSON 超大整數轉 float 溢位」特地接 `OverflowError`,這裡沒有。
失敗場景:
- 結果檔 `sites[0].retained` 是 1 後面接 400 個 0。
- `_macrobench_native_sites_err` 只用 `_secev_int` 加非負,放行。
- `_macrobench_native_print` 做 `int / 1048576` 時 Python 丟 OverflowError,文字模式整支 `lumos macrobench` 帶 traceback 結束,不是「整段不採用、印一行形狀不對」。
- `--json` 模式不印,所以不受影響。
重現:
```
cd /tmp/lumos-seat-work/code-原生配置排行/邊界-sonnet/ && python3.14 t4.py 2>&1 | tail -3
```
輸出最後一行是 `OverflowError: integer division result too large for a float`。
- 收集腳本不會寫出這種值,觸發條件是結果檔被人改過或損壞。
- 但規格要的就是這種輸入下不崩潰。

### 3. 回溯失敗的 ERROR 偽框架會被當成「呼叫者」印出來
severity: minor
blocking: 否 — 只影響呼叫者欄的可讀性,不影響排行與大小。
引句:「-- 呼叫者:呼叫位置往上第一個不在 libart.so 的框架;同一呼叫位置有幾個呼叫者時取結束累計加總最大的那個」
file: `scripts/templates/android-stability-native.sql:12` 與 `caller_step` 的條件只排除 `libart.so`,沒排除 ERROR 偽框架。
file: `docs/lumos-toolchain-knowledge/Projects/原生記憶體增長提示_計劃.md:139` 規格只說 ERROR 當呼叫位置時記「?」,沒說它當呼叫者時怎麼處理。
失敗場景:
- 呼叫鏈是 malloc → foo(App)→ `ERROR 1`(沒有 mapping),或 foo → libart 幾框 → `ERROR 1`。
- `ERROR 1` 的 so 是 `?`,不等於 libart.so,所以被選成 caller。
- 輸出 `('site','foo','libfoo.so','ERROR 1',...)`,lumos 印「foo @ libfoo.so ← ERROR 1」。
- 回溯被截斷時最外層正好是 ERROR 偽框架,所以這不算罕見形狀。
重現:
```
cd /tmp/lumos-seat-work/code-原生配置排行/邊界-sonnet/ && python3.14 t2.py | grep -A1 "ERROR as caller"
```

### 4. LUMOS_STABILITY_STEP_BUDGET_S 設成 nan 時,通過驗證卻等於沒有上限
severity: minor
blocking: 否 — 只有手動設成 nan 才會碰到,e2e 範本傳的是數字。
引句:「if budget and elapsed + (2 * elapsed + 120) > float(budget):」
file: `scripts/templates/android-stability-collect.sh:565` 與 `:658`,`main` 只檢查 `float(budget)` 不丟 ValueError。
失敗場景:
- budget="nan" 通過 `main` 的格式檢查,因為 `float("nan")` 合法。
- `native_skip` 裡任何數比 nan 都是 False,所以不會跳過第二段。
- 結果是一個明明設了「上限」的值,實際上完全不限制。
- 實測 `100+(2*100+120) > float('nan')` 為 False。
- "0"、負數、"inf"、空字串的行為都合理:前兩者一律跳過,後兩者視為不限制。

## 各鏡頭

1. 邊界
   - 查詢範本:mapping 名為空字串或 NULL 時 so 記 `?`,`!` 與 `a/b/` 結尾得到空字串。
   - 函式名為 NULL、空字串時歸成沒有符號,`ERROR 1234` 當呼叫位置時整列記 `?`,`ERROR`、`ERRORx` 不誤判。
   - 函式名含引號、換行、逗號、中文時,hex 往返無損。
   - rel_pc 為 NULL 寫成 `+0x?`,-1 寫成 `ffffffffffffffff`。
   - 只有 malloc 一框、整條都是配置器,都記 `?`。size 剛好 1048576 保留,少 1 或總和為負都被篩掉。
   - 同呼叫位置的兩個呼叫者各 M/2 會加總留下。heap_name 不是 `libc.malloc` 時只剩 rows 列。stats 的 value 為 NULL 或 0 的不列。
   - 效能:3.2 萬個葉、30 層約 10 秒,隨葉數線性成長。
   - 收集腳本:hex 奇數長度、retained 非數字都落入 `ValueError` 而回 failed。欄數不符的列被略過,`rows` 列不見會回「沒錄到」,都是安全方向的失敗。
   - SDK 29 與 30 的邊界、test_data、pid、驅動、時間的判斷順序都與規格一致。情境名比對是精確比對,與 `load_config` 的查表一致。
   - lumos:空清單合法,非清單、含空白字串、重複、保留字以外的名字都會擋下。名字含控制字元走 `_out_clean`。結果檔 enabled 缺、status 為 null、reason 為數字都被處理,sites 10 萬項只取 200 項。
   - 其餘見 finding 1 到 4。
2. 圖譜:已讀,對 7 個有合約的固定席節點判定不影響。
   - `lumos-cli-read` 的 search 排除 superseded、`guard-kill` 的 rc 優先序與 `--json` 純度、`design-loop` 處置閘、`測試假綠形態`、`lumos-cli-lifecycle` 的 re-inject、`bound-tests-gate`:這份 diff 只動 macrobench 區段與 `_VENDORED_TREE_FILES`,沒碰這些路徑。
   - `pitfalls-code-loop`、`loop-convergence-recording` 的風險標記:同樣沒有影響。
   - 只列名的節點沒有看到關聯。
3. 本案特定鏡頭,各分支逐一用卡線輸入對照實作:
   - `.so` 名稱:`…/base.apk!libfoo.so` 得 `libfoo.so`,`a!b!c.so` 得 `c.so`,無 `!` 取最後一段。
   - 配置器名單:`_Znw*`、`_Zna*`、`_ZNSt*`、`_ZNKSt*` 用 glob,底線不被當萬用字元。
   - 呼叫者跳過 libart.so:site 之後只有 libart 時記 `?`,libart 之後有 App 框架時取該框架。
   - 沒有符號的寫法、系統目錄、歸併鍵、篩 1 MiB、排序決勝都符合規格。
   - 截 500 字:SQL 端按字元截斷,與規格一致。長名稱在 lumos 端的後果見 finding 1。

## pitfalls manifest 15 條逐條判定

全部判誤報,沒有真隱患。
- `collect.sh` 259 與 312 的 `open(` 沒用 `with`:兩處都是一次性 `.read()`,CPython 引用計數會立刻關檔,且是從 `heap_counts`、`start_record` 原樣搬出來的既有寫法。
- `collect.sh` 577 的 `time.sleep`:只是 `native_run` 裡單次等 SETTLE,不在迴圈裡累積。
- `native.sql` 的 12 條 SELECT N+1 問題:整支是一條 WITH 語句,從沒被迴圈呼叫。

臨時實驗檔留在 `/tmp/lumos-seat-work/code-原生配置排行/邊界-sonnet/`,沒有改 repo 裡任何檔,也沒有刪除目錄,留給編排者收貨後處理。

最嚴重 severity:major;blocking 共 2 條。
