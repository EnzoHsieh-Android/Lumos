severity: major

整份測試大致守得住。我在副本裡做了約 15 種改壞,多數會翻紅。但有一處「清理守衛」改壞後測試照綠,另有幾處小缺口。

固定席筆記(impact 附的 lumos-cli-read、guard-kill 等):這次沒有一條是針對本變更的合約,逐條判不相關。「這次新增的殘留」段與備援段都沒附上。

## 1. 第二段停錄期間被中斷的清理順序沒有測試守
severity: major
blocking: 是,S28 把 SIGTERM 時的裝置錄製清理列為驗收條款,這條路徑完全沒有測試,改壞後測試照綠。
引句:「        check("往上丟時錄製還在 state,交給 main 的 cleanup 收(這裡不先收)", state.get("rec") == rec and calls == [], str((calls, state)))」
file: `scripts/templates/android-stability-collect.sh:605-612`(`native_run` 裡 `stop_record` 之後才 `del state["rec"]`)

- 本輪補的測試只守 `native_phase` 的例外路徑,用 stub 的 `native_run` 把 rec 塞進 state。
- `native_run` 自己「停完才拿掉 state 裡的錄製槽」這個順序沒有測試。唯一的 SIGTERM 測試 `t_android_native_collect_sigterm` 把中斷落在第 4 次驅動,那時 rec 本來就還在 state。
- 最小重現:在副本把 `stop_record(...)` 前面加 `state.pop("rec", None)`,後面的 `del state["rec"]` 改成 `state.pop("rec", None)`。跑 `python3.14 scripts/test_lumos.py -k android_native`,結果 `54 passed, 0 failed`(-k android_native_query 另跑也全綠),`fails: 0`。
- 行為差異實測:用 `term_slow` 讓停錄的 `kill -TERM` 卡 3 秒,在那段送 SIGTERM。原版 `adb.log` 裡 `kill -TERM 4321` 共 3 次,cleanup 再收了一次;改壞版只有 2 次,cleanup 沒碰裝置,卻照樣印「裝置上的錄製已停、暫存已刪」。
- 補充:`stop_record` 自己的 `finally` 會刪裝置暫存檔。所以實際洩漏的是「中斷發生在送出 TERM 之前,錄製繼續跑到 `max_record_s`」這個窄窗口,加上訊息不實。
- 歸因:有證據的原有漏查。修前 07642d8 的 `native_run` 已是同一段 `stop_record` 後才 `del state["rec"]`,本輪 diff 沒動它。修前、修後兩版對該改壞都沒有測試翻紅(修前版我沒另外跑,依 diff 判斷)。

## 2. 排行裡 `.so` 與呼叫者的控制字元清除沒有測試
severity: minor
blocking: 否,S11 只點名函式名,講得出的改壞不在條款範圍內。
引句:「    sites[3]["func"] = "fn03\x1b[31m\u2028red"」
file: `scripts/lumos:40089`(`--json` 清除 `("func", "so", "caller")`)、`scripts/lumos:40103-40104`(文字輸出清除 `so` 與 `caller`)

- 三個改壞實測都是 `39 passed, 0 failed`:`--json` 清除只留 `("func",)`、文字輸出的 `caller` 不清、文字輸出的 `so` 不清。
- 控制字元只放進 `func`,`so` 與 `caller` 從沒放過。
- 程式註解說「函式名與 .so 名是被量 App 的符號(外部可控)」,但本輪補的 `--json` 清除測試只驗 `func`。
- 歸因:有證據的原有漏查(文字輸出那兩條清除 `so` 與 `caller` 是修前就有;`--json` 版是本輪新增的程式,連同它的測試都只覆蓋 `func`)。

## 3. 收集腳本裡的排序沒有測試
severity: minor
blocking: 否,SQL 本身已排序,拿掉這層不會在真實工具上改變輸出,講不出會出錯的具體場景。
引句:「        _ms_native_out(fake, sites=[(odd, "lib,x.so", 'call"er', 0, 1, 3 * _MS_MIB), ("Java_b", "libfakesdk.so", "?", 1, 0, 2 * _MS_MIB)])」
file: `scripts/templates/android-stability-collect.sh:536-543`(`native_sites` 的 `sites.sort(...)`)

- 把 `sites.sort(...)` 改成 `pass` 後,`-k android_native_collect_ok` 為 `20 passed, 0 failed`。
- 假工具輸出本來就是降冪的兩列,沒有並列、沒有亂序。
- 歸因:有證據的原有漏查(該排序行不在修補差異內)。

## 4. 時間上限 140 秒那段測試在慢機器上的餘裕變小
severity: minor
blocking: 否,實測在 3 倍 CPU 超載下仍通過,只是餘裕縮小。
引句:「        r, d, fake, _ = _ms_native_collect(td, env={"LUMOS_STABILITY_STEP_BUDGET_S": "140"},」
file: `scripts/templates/android-stability-collect.sh:583`(`2 * elapsed + NATIVE_TAIL > remaining`)

- 只要第一段超過約 6.7 秒,第二段就會被判「時間不夠」,不會進到「驅動失敗(逾時)」,這條斷言會誤紅。
- 乾淨環境量到第一段約 2 秒,餘裕約 3.3 倍。
- 3 倍 CPU 超載下,驅動上限量到約 15 秒,表示第一段約 5 秒,離誤紅只差一點。
- 歸因:有證據的修復回歸。修前用 200 秒,誤紅線約 26 秒(約 13 倍餘裕);修後改 140 秒才縮到 3.3 倍。

我沒找到其他測試弱點,也沒把下列狀況另立一條:
- SQL 的 `having sum(size) != 0` 改成 `> 0` 測試全綠,但這只是效能過濾,真實 heapprofd 不會產生負的淨量。
- 拿掉 `heap_name = 'libc.malloc'` 過濾測試全綠,但錄製設定沒指定 `heaps`,預設就只有這一個,講不出具體場景。
- `max(1.0, …)` 改 `max(0.0, …)` 全綠,屬無法觀察的邊界。
- 暖機失敗後仍繼續錄製與驅動(`if d_warm["ok"]` 改 `if True`)測試全綠,原因文字不變,只是多浪費時間;計劃沒有這條條款。

## 三問
1. **原問題的修復效果**:
   - 預估與截止共用 `NATIVE_TAIL`:改壞版(查詢誤用 `NATIVE_TAIL`)被翻紅,`剩 200 秒` 那條斷言抓到。
   - `>=` 邊界:剩 320 秒照跑、319 秒不跑,兩條斷言守著。
   - 140 秒驅動被砍:實測有跑出 `驅動失敗(逾時)`。
   - 收錄製順序:只在 `native_phase` 這層驗到;`native_run` 這層見 finding 1。
   - 允許名單與前綴補強:`libc.so` 內部框架、`libstdc++.so`、`_ZNKSt`、10 個名單函式都由 `t_android_native_query_allocator` 新斷言守著,我沒找到存活的改壞。
   - 小數位 1.5 與 1.9、`--json` 上限 200:會翻紅。
2. **修補處的正常、錯誤與相鄰呼叫路徑**:
   - 沒設上限(`end` 為 None)走 `T_LONG`,有測試。
   - 上限很遠時不超過 `T_LONG`,有測試。
   - `native_skip` 的 `remaining=None` 不限制,有測試。
   - 值為 nan、inf、0、負數、非數字會回 2,有測試。
   - 例外路徑裡 `abort_record` 被中斷、錄製留在 state 的情況有測試。
   - `_ms_collector_ns` 載入的是真實腳本本體,被換掉的只有執行環境函式(`shell`、`driver`、`start_record` 等),替換只寫進該命名空間;`sys.argv` 有還原,沒有全域訊號或環境變數殘留。
3. **新發現同一案例在修前、修後各是什麼結果**:
   - finding 1:兩版都沒有測試翻紅。
   - finding 2、3:兩版都沒有測試翻紅(依 diff 判斷,我只在修後版實跑)。
   - finding 4:修前餘裕約 13 倍,修後約 3.3 倍。這是用算式加實測第一段約 2 秒推出,沒有真的在修前版跑。

附帶:跑完後測試機的 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 底下有大量 `gctl-run-*` 現場。其中只有 `gctl-run-hopelo7_` 確認是我留下的,我已用字面路徑刪掉;其餘我無法確認是不是我的,沒動,請另行處理。實驗副本 `/tmp/lumos-seat-work/code-原生配置排行/測試-sonnet` 也已刪除。另外我為了測慢機器,臨時起了一批空轉的 python 程序,已逐一關掉,確認剩 0 個。

最嚴重 severity: major,blocking 1 條(finding 1)。
