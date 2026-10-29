severity: major

我在副本(`07642d8e`)逐一改壞正式程式後跑對應測試,拿到 2 條 major 和 4 條 minor。副本已用字面絕對路徑刪除。

整批基線是 `-k android_native` 184 passed。S1–S29 的 `[test:]` 名稱共 27 支,每支都在 `scripts/test_lumos.py` 有定義,沒有未綁定的 `t_android_native_*`。

## 1. 配置器跳過規則的 .so 清單與多數函式名,拿掉後測試照綠
severity: major
blocking: 是——S3 明文綁定這支測試,改壞後驗收條款的測試照綠。
引句:「(8 * _MS_MIB, [("calloc", _MS_LIBC, 1), ("_ZnwmRKSt9nothrow_t", "/system/lib64/libc++.so", 2), _MS_MALLOC]),」
file: `scripts/templates/android-stability-native.sql:40-43`(`coalesce(so in (...) or fname in (...) or fname glob ...)`);規格 S3 在 `docs/lumos-toolchain-knowledge/Projects/原生記憶體增長提示_計劃.md:191`。
歸因:有證據的原有漏查。這支測試沒在修補差異裡改動,SQL 也不在修補差異裡。
失敗場景:S3 要求 `libc.so`、`libc++.so`、`libc++_shared.so`、`libstdc++.so` 裡的「全部框架」都跳過,但測試給的每個 libc 或 libc++ 框架,名字剛好也被函式名清單或 `_Znw*` 前綴擋掉,所以 .so 規則從沒被單獨驗到。
- 實測:把 `so in ('libc.so', 'libc++.so', 'libc++_shared.so', 'libstdc++.so') or ` 整段拿掉,`-k android_native_query` 結果是 `41 passed, 0 failed`。
- 實機後果:SDK 呼叫 libc 內部名字不在清單的框架(例如 scudo 內部函式)時,這些框架會被誤當成「呼叫位置」而不是歸給 SDK。
- 清單裡的名字也沒個別驗過。只有 `__wrap_malloc` 一項被抓到:把整份名單拿掉會紅,但單拿掉 `je_malloc`、`tc_malloc`、`realloc`、`posix_memalign`、`memalign`、`__libc_malloc`、`calloc` 各自仍全綠,因為這些函式在測試裡都放在 libc.so 路徑下,被 .so 規則擋住了。
- `_ZNKSt*` 前綴整段拿掉也是 41 passed;測試只用了 `_ZNSt`、`_Znw`、`_Zna`。

修前修後:修前 84b487f 加新測試,這支測試是綠的;修後也是綠的。兩版都抓不到,不是修補造成。

## 2. 第二段改用 `fresh_launch` 的重構沒有行為證據,拿掉停 App 與啟動全綠
severity: major
blocking: 是——規格〈打算怎麼做〉第 3 步與 G8 重構的核心行為(第二段從乾淨行程開始、停完才讀結束紀錄)沒有任何測試守,還原修補也不紅。
引句:「(fake / "driver").write_text(f"#!/bin/sh\necho \"$@\" >> \"$FAKE_DIR/driver.log\"\n[ -f \"$FAKE_DIR/driver_sleeps\" ] && [ \"$1\" = 5 ] && \"$FAKE_DIR/sleeper\"\n"」
file: `scripts/templates/android-stability-collect.sh:481-488`(`fresh_launch`)和 `:595`(`native_run` 呼叫處);規格 `原生記憶體增長提示_計劃.md:150`。
歸因:有證據的修復回歸性缺口。修補把第二段的「停 App、啟動、延遲、讀結束紀錄」換成共用函式,但沒有新增任何斷言能區分新舊順序或有無此步驟。
失敗場景與兩個實測改壞,都跑 `-k android_native`:
- 把第二段改回修前順序(force-stop → monkey → sleep → `read_exits`)是 `184 passed, 0 failed`。修前是先啟動後讀結束紀錄,修後是先讀再啟動,測試分不出來。
- 把第二段改成完全不停 App、不啟動(只剩 `read_exits` 與 `pidof`)同樣是 `184 passed, 0 failed`。後果是 `no_startup` 的錄製接在上一輪留下的行程上,第一段殘留會算進排行,這正是 `fresh_launch` 註解寫的 2026-10-24 實驗室事故。
- 假 adb 的 `am force-stop` 與 `monkey` 都有記進 `adb.log`,但 `t_android_native_collect_ok` 只數了 `kill -TERM`,沒數 `force-stop` 次數或順序。第一段那條 `fs < ex < st` 的順序守衛(`t_android_memstab_collect_driver_status`)也只看第一段。

修前修後:修前版本(新測試對舊程式)與修後版本都是綠,兩邊都不紅,所以「重構沒壞第二段」缺乏行為證據。

## 3. 原生錄製設定的 `duration_ms` 佔位、`sampling_interval_bytes`、多餘的 `process_cmdline` 都沒被斷言
severity: minor
blocking: 否——只是覆蓋面可以更完整,沒有條款直接綁這幾個欄位。
引句:「check("錄製設定是 heapprofd、只接已在跑的主行程、沒有連續傾印", 'name: "android.heapprofd"' in cfg and 'process_cmdline: "com.lab"' in cfg」
file: `scripts/templates/android-stability-heapprofd.pbtxt:14-19`。
歸因:有證據的原有漏查。這份範本在修補差異外。
場景:`-k android_native` 全套改這份範本,三種改壞都是 `184 passed, 0 failed`。
- `duration_ms: __DURATION_MS__` 換成 `duration_ms: 1000`。`max_record_s` 對第二段失效,錄 1 秒就停。
- `sampling_interval_bytes: 4096` 換成 `0`。規格 PRIOR-ART 寫明 Perfetto 不接受 0。
- 多加一行 `process_cmdline: "other"`。這會同時錄第二個行程,違反 `main_process_only`;測試只用 `in cfg` 子字串比對。

## 4. lumos 印出一位小數 MiB 的算法沒被驗
severity: minor
blocking: 否——正確的位元組數仍有斷言(`5242880 位元組`),只有一位小數的 MiB 沒被驗。
引句:「check("每行有函式、.so、呼叫者、還留著多少", "fn00 @ libfakesdk.so ← com.lab.C.c00:還留著 30.0 MiB" in out, out[-800:])」
file: `scripts/lumos:40108-40109`(`tenth = x["retained"] * 10 // 1048576`,以及 `f"還留著 {tenth // 10}.{tenth % 10} MiB`)。
歸因:有證據的原有漏查。
場景:測試的 retained 全是 MiB 的整數倍,小數位恆為 0。
- 把 `{tenth % 10}` 換成固定 `0`,`-k android_native_lumos` 是 `36 passed`。
- 把 `//` 換成進位版(`+ 1048575`),也是 `36 passed`。
- 1.5 MiB 會印成 `1.0 MiB`,但同一行的位元組數不錯。

## 5. 查詢輸出看不懂的分支、`rc != 0` 的 stderr 尾端、`sec["sites"][:200]` 沒被驗
severity: minor
blocking: 否——都有別條路徑兜底(統一落成 failed),只是原因文字不同。
引句:「        ("查詢跑不起來", {}, files(native_fails="1"), None, "算不了原生配置記帳"),」
file: `scripts/templates/android-stability-collect.sh:553-560`(`except ValueError` 分支)、`scripts/lumos:40089`(`[:200]`)。
歸因:有證據的原有漏查。
場景:`-k android_native` 全套,三種改壞全是 `184 passed`。
- 把 `except ValueError` 改成 `except ZeroDivisionError`:hex 或數字格式錯會逃到外層,寫成「第二段出了意外(ValueError…)」,原因文字不同但測試不分。
- 把 `err.strip()[-200:] or rc` 換成固定字串。
- 把 `sec["sites"][:200]` 換成 `sec["sites"]`。

## 6. `left()` 的 `min(T_LONG, …)` 上限沒被驗
severity: minor
blocking: 否——現有測試只驗了「不超過剩下的秒數」這一半。
引句:「check("有 deadline:兩次驅動與查詢的上限都不超過剩下的 50 秒", len(seen) == 3 and all(0 < t <= 50 for _, t in seen), str(seen))」
file: `scripts/templates/android-stability-collect.sh:592-593`。
歸因:有證據的原有漏查(`left()` 在修補差異裡,但新測試沒覆蓋 T_LONG 這一邊)。
場景:`max(1.0, min(T_LONG, deadline - time.time()))` 拿掉 `min(T_LONG, …)`,`-k android_native_budget_rule` 是 `7 passed, 0 failed`。
- 測試的 deadline 固定是 +50 秒,從不超過 `T_LONG`。
- 設了大的步驟上限時,卡住的查詢可以等到 deadline,而不是 `T_LONG`。

## 已驗主張

- **修補前後行為**:把新測試檔放在修前 84b487f 上跑 `-k android_native`,是 24 項斷言紅(`150 passed, 24 failed`),涵蓋:
  - `budget_values`(nan/inf/0/-5 沒擋)。
  - `budget_rule` 與 `phase_exception`(函式簽名)。
  - `collect_budget`(驅動沒被砍,33.1 秒)。
  - `lumos_print`(長名字、超大整數 Traceback)。
  - `lumos_shape`(10 條形狀)。
  - `query_caller`(ERROR 偽框架當呼叫者)。
  - `templates_present`。

  修後 184 passed。修復選例 G1、G2、G3、G6、G7 都有「修前紅、修後綠」的證據。
- **G5**(第二段 pid 讀不到、結束紀錄讀不到):`not pids[0] or` 在修前就存在,這輪只加測試。拿掉 `not pids[0] or` 會紅,拿掉 `new is None` 分支也會紅。
- **G4**(Android 11 邊界):程式沒變,只加邊界測試。`NATIVE_MIN_SDK` 改 31 或 29 都會紅。
- **查詢本身會紅的改壞**:
  - 門檻 `>=` 改 `>`、`limit 200` 改 199 或 201、`substr` 500 改 501 或 499、排序 `a.func` 改 desc。
  - 呼叫者的 `caller = '?'` 排序、`f.step > s.step` 改 `>=`、`group by` 與 `partition` 拿掉 sys。
  - stat 的 `severity` 與 `value != 0`、`rows` 的 `count(*)`。
  - ERROR 偽框架判斷、系統目錄 glob(拿掉 `/odm/*`)、`path = ''` 改回 `''`。
- **腳本與流程會紅的改壞**:
  - budget 公式(`>=`、119、拿掉 `2*`)、`deadline = None`、`except Terminated: raise` 拿掉。
  - `abort_record` 拿掉、`state.pop("rec")` 沒清、`NATIVE_MIN_SDK` 邊界、`no_startup: true` 改 false。
  - 查詢逾時、`stats`、`rows` 0 的判斷順序。
  - lumos 這邊的 `MACROBENCH_NATIVE_SHOW`、`status` 驗證、`retained` 負數驗證。
- **時間與全域狀態**:
  - 預算測試的「沒有等滿 30 秒」實測 20.2 秒(deadline 20 秒加約 0.2 秒收尾),餘裕足夠,不是慢機器上的不穩來源。
  - `os.environ` 與 `sys.argv` 都在 `finally` 還原,沒看到洩漏。
  - `_ms_orphans` 只殺命令列帶自己假工具目錄的程序。
  - 最慢是 `t_android_native_collect_failures` 41.7 秒,對測試框架 180 秒上限的餘裕只有 4 倍。這不是我能指出具體失敗的場景,所以不列 finding。
- **`_ms_collector_ns`**:`exec` 載入的是真的 `native_phase`、`native_run`、`native_skip`,只替換 `shell`、`driver`、`abort_record` 等外部依賴,測到的是真函式。但 `main` 把例外交給 `native_phase` 這一接線只有 SIGTERM 子程序測試守,意外例外那條路徑沒有端到端測試(未判定其重要性)。
- **假輸入形狀**:真 `trace_processor`(v58.2)對空追蹤跑 `android-stability-native.sql`,輸出 `"kind","a","b","c","d","e","f"` 加 `"rows","","","",0,0,0`,與假 tp 的表頭和引號風格一致,查詢在真實 schema 下可解析。沒有真實 heapprofd 追蹤可驗證 `stack_profile_frame.name` 是否真為 mangle 名,規格宣稱是,未驗。
- **固定席節點**:`lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle`、`design-loop` 的 INVARIANT 與本改動無涉(沒動 search、guard kill、re-inject、處置閘)。`測試假綠形態` 的 INVARIANT(還原翻紅釘要有前置斷言證明現場成立)對修補的釘有效:G1、G2、G3 在修前都紅。`bound-tests-gate` 的綁定測試存在性成立。`loop-convergence-recording` 與 `pitfalls-code-loop` 沒有 test 層面的牽連。

## 三問

1. **原問題的修復效果有何行為證據?** G1(長名字與超大整數)、G2(ERROR 偽框架當呼叫者)、G3(預算值與逾時被砍)、G6(意外例外先收錄製)、G7(缺範本開跑前擋下)都有修前紅、修後綠的證據。G5 與 G4 的程式沒有改,只補測試,改壞程式都會紅。G8(第二段改用 `fresh_launch`)沒有行為證據,見 finding 2。G9(`e2e_preflight_stability_tools` 只一處讀 `test_data`)不在這份測試差異裡,未驗。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 第一段的 `measure` 呼叫 `fresh_launch` 後的順序,由原有的 `t_android_memstab_collect_driver_status` 守住。第二段相鄰路徑(暖機失敗不開錄、開錄失敗)的改壞,在 `collect_failures` 的 `-k` 範圍內仍是綠;暖機失敗那條改成無條件開錄也是 `27 passed`,未驗證「不開錄」,只驗了 failed。
3. **新發現的同一案例在修前、修後各是什麼結果?** finding 1:修前加新測試是綠,修後也綠,拿掉 .so 規則兩邊都綠。finding 2:修前版本(舊順序)的第二段在新測試下是綠,修後新順序也綠,兩邊都分不出,所以不是修補造成,而是修補沒補到行為證據。finding 3 到 6 是修補外的原有覆蓋缺口,修前修後行為相同。

最嚴重 severity: major,blocking 2 條。
