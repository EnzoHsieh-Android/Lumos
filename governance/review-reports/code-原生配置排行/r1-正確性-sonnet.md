severity: minor

我沒有找到 blocker 或 major。逐 hunk 走完之後,只有三條 minor。repo 沒被我改過(`git status` 只有開工前就有的兩項)。本機跑 `python3.14 scripts/test_lumos.py -k native` 為 165 passed、0 failed。

## Findings

### 1. 結果檔的 retained 是超大整數時,文字輸出會丟 OverflowError
severity: minor
blocking: 否 輸入要手改或損壞的 stability.json 才會出現,收集腳本寫的是 SQLite 64 位元整數,走不到。
引句:「line = f"{x['func']} @ {x['so']} ← {x['caller']}:還留著 {x['retained'] / 1048576:.1f} MiB({x['retained']} 位元組){tags}"」
file: `scripts/lumos:40109` 與 `scripts/lumos:8578`。`_secev_int` 只擋 bool,`_macrobench_native_sites_err` 只擋負數,所以 `10**400` 這種非負整數會通過驗形狀。
- 失敗場景:`sites[0].retained` 是 401 位數的整數。走到 `_macrobench_native_print` 的 `x['retained'] / 1048576`,整數除法結果超過 float 上限,拋 OverflowError。
- 結果:`lumos macrobench` 非 `--json` 時整支帶 traceback 崩掉,違反規格第 6 步「形狀不對不噴例外」。`--json` 路徑不受影響。
- 重現:在 `/tmp/lumos-seat-work/code-原生配置排行/正確性-sonnet/` 放 `s2.json`,內容是 `{"native_retained":{"enabled":true,"status":"ok","sites":[{...,"retained":1<400 個 0>}]}}`,再跑 `python3.14 scripts/lumos macrobench --repo <含 stability.native_retained 的專案> --stability s2.json`。輸出:`OverflowError: integer division result too large for a float`。

### 2. 第二段的結束紀錄讀不到,就把整份排行判 failed,規格沒有這個原因
severity: minor
blocking: 否 這是比規格保守的行為,不產生錯誤排行。⚠ 規格對這一格沉默,我判不準算不算缺陷。
引句:「why = "讀不到第二段的結束紀錄"」
file: `scripts/templates/android-stability-collect.sh:493`。`read_exits` 在 rc 非 0 或沒有全域標頭時回 `("failed", 原因字串)`。
- 規格〈打算怎麼做〉第 2、3 步的失敗原因只列:驅動失敗、App 結束、行程換了、錄製失敗、查詢各項。
- 失敗場景:第二段前後任一次 `dumpsys activity exit-info` 偶發 rc≠0。`ex_status` 或 `ex_status2` 不是 ok,`new` 變 None,走進這個 elif,排行 failed。
- 此時 pid 前後相同、heap-native.pftrace 也完整。第一段碰到同樣狀況只把 `exits` 這個 check 記成 unjudged,不連累別的資料。
- 另一個影響:輸出沒有全域標頭的裝置,這段永遠 failed。

### 3. 「呼叫者」會取到回溯失敗的 ERROR 偽框架,並列時還勝過真呼叫者
severity: minor
blocking: 否 只影響「呼叫者」那一欄的可讀性,排行的數字和呼叫位置不受影響。
引句:「where not s.unknown and f.so != 'libart.so' group by s.leaf」
file: `scripts/templates/android-stability-native.sql:60`。規格〈排行怎麼算〉第 1 條說 ERROR 偽框架「記成 ?」,但 SQL 只在選呼叫位置時排除它,選呼叫者時沒排除。
- 重現:`/tmp/lumos-seat-work/code-原生配置排行/正確性-sonnet/t4.py`,對 sqlite 3.53.4 的假表跑。
- 假呼叫鏈 1:`malloc ← foo(libfoo.so) ← ERROR 2`,1 MiB。假呼叫鏈 2:`malloc ← foo ← bar(libfoo.so)`,1 MiB。
- 輸出 `['site','foo','libfoo.so','ERROR 2',1,0,2097152]`。兩個呼叫者各 1 MiB 並列,依名字升冪(BINARY 排序,大寫 E 排在小寫 b 前面)選到 `ERROR 2`,真呼叫者 `bar` 被擠掉。
- 印出來是 `foo @ libfoo.so ← ERROR 2`。

## 各鏡頭

**1. 正確性。** 用 `/tmp/lumos-seat-work/code-原生配置排行/正確性-sonnet/t3.py` 對 SQL 做了 400 組隨機鏈的對照:Python 參考實作照規格寫,涵蓋 NULL 名稱、空名、無 mapping、`!` 與 `/` 路徑、六個系統目錄、並列、1 MiB 卡線、非 libc.malloc 的 heap。差異 0 筆。其餘走過且沒問題的項目:
- **邊界。** 空 site 列、`rows`=0、全是配置器的鏈(記為 `?`)、M-1 排除而 M 納入、取前 200 的 SQL 與 Python 排序鍵一致。
- **資源與例外。**
  - 暫存 .sql 有 finally 刪除。
  - 錄製槽:`start_record` 先登記、`stop_record` 後才 `del`,`native_phase` 的 finally 一律 `pop` 並 `abort_record`。
  - `Terminated` 先放行;`KeyboardInterrupt` 不是 Exception,同樣穿過。
  - `pidof` 回 None 由 pid 比對接住。
  - `start_record` 回 `(None, 原因, None)` 時 `abort_record` 直接當作已收。
  - `tp_rows` 的 rc 為 None 時,逾時走「查詢逾時」,其他走「算不了」。
- **冪等與寫一半。** 中斷不寫結果檔,下次只擋已有 stability.json 的 run-id;殘留的 heap-native.pftrace 符合既有 7 天刪除的樣式;`adb pull` 要 rc=0 才採用,舊檔不會被誤用。
- **新舊互讀。**
  - 舊腳本寫的結果檔沒有這段,新 lumos 判 unsupported 且不印。
  - 實測舊 lumos(faecd422)讀含 `stability.native_retained` 的設定,`--check-config` 通過;讀新結果檔的 `--json` 也正常。
- **時間預算。** 走一遍:預算 3600、第一段 1000 秒,1000+(2000+120)=3120 不超過,會跑;第一段 1200 秒則 3720 超過,不跑。算式與規格一致。
- **SQL 效能。** 30000 個 leaf、深度 61,約 24 秒、約 200 MB,遠低於 T_LONG 1800 秒。
- **不可逆。** 只刪自己的 `lumos-native-<run-id>.*` 與暫存檔;`pkill -f` 的樣式沿用第一段既有寫法,沒有新增風險。

**4. 本案鏡頭。**
- ① `native_skip` 的順序與規格第 2 步逐項吻合。`native_run` 的原因順序是驅動失敗、結束紀錄、App 結束、pid 換了、錄製失敗,最後是查詢(逾時、stat、rows)。唯一多出來的是第 2 點。
- ② 呼叫鏈走查:`malloc(libc.so) ← _Znwm(libc++.so) ← foo_alloc(libfoo.so) ← art_jni(libart.so) ← java_frame`,結果是呼叫位置 `foo_alloc`、呼叫者 `java_frame`,符合規格。另見第 3 點。
- ③ `except Terminated: raise` 在 `except Exception` 之前,離開前 finally 收掉錄製;`device_dirty` 讓 `cleanup` 能照實回報裝置沒回應。已讀,無 finding。

## manifest(15 條)

- collect.sh 259 行與 312 行的 `open(...).read()`:誤報。都是單一運算式、讀完立刻被回收,沒有 handle 活著;這個寫法是第一段既有的。
- collect.sh 577 行的 `time.sleep(SETTLE)`:誤報。它不在迴圈裡。
- native.sql 的 12 條 N+1(17、20、22、51、60、74、77、80、83、87、89、91 行):誤報。這支範本是一條 WITH RECURSIVE 的複合語句,trace_processor 只執行一次,沒有外層迴圈逐筆發查詢。

## 圖譜鏡頭(固定席)

- `lumos-cli-read` 的 search 合約、`guard-kill` 的 rc 優先序與 JSON 純度:不影響。diff 只在 macrobench 區新增函式,沒碰 search 或 guard kill。
- `design-loop` 的處置閘、`測試假綠形態`、`lumos-cli-lifecycle` 的 re-inject、`bound-tests-gate`:不影響。這些合約管的是別的子命令與測試簽章,diff 沒動它們的程式路徑。
- `_VENDORED_TREE_FILES` 新增的兩支範本檔在 repo 內都存在,並且已列在 `Systems/android-stability-collector.md` 的 `about_code`。
- 其餘 `pitfalls-code-loop`、`loop-convergence-recording` 與只列名的節點:不影響。diff 沒有改它們管的審查迴圈與記帳邏輯。

## 角色卡

- be-api-compat:`macrobench --json` 與 `stability.json` 都是新增欄位(`native_retained`),沒有改名、刪除或改預設值。e2e judge 用 `.get` 讀,舊 lumos 讀新檔不報錯(已實測)。
- be-authz:這個變更沒有新增或改動任何端點,不適用。

最嚴重 severity 是 minor,blocking 共 0 條。
