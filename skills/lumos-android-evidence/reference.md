# lumos-android-evidence 收據格式

收據目錄 `.lumos/receipts/<run-id>/` 進版控,放 `manifest.json`、`report.md`、`queries.sql`、`rerun.sh`;原始檔在 `.lumos/artifacts/android/<run-id>/`,不進版控。草案來源與欄位理由見 [[Projects/Android診斷證據接入_調研]]〈收據格式草案〉與 [[Projects/Android逐層診斷_計劃]]〈收據格式補強〉。

## manifest.json(schema lumos-android-evidence/v1.1)

```json
{
  "schema": "lumos-android-evidence/v1.1",
  "run_id": "android-<日期>-<情境>",
  "purpose": "compare",
  "question": "一句話:要回答什麼",
  "project": {"git_commit": "<40 碼>", "dirty": false, "package": "<套件>", "version_code": 1,
              "build_type": "<建置類型;是否 debuggable / profileable>",
              "built_apk_sha256": {"app": "…", "benchmark": "…"},
              "installed_apk_sha256": {"app": "…", "benchmark": "…"}},
  "device": {"model": "…", "api": 36, "build_fingerprint": "…", "physical": true,
             "battery_percent_before": 100, "battery_percent_after": 100,
             "thermal_status_before": "0", "thermal_status_after": "0",
             "cpu_locked": false, "cpu_locked_note": "照抄結果檔 context.cpuLocked;未 root 時是猜的,兩邊不同列 gaps"},
  "scenario": {"id": "…", "benchmark": "<類別#方法>", "iterations": 20, "compilation_mode": "None",
               "instrument_args": {"<鍵>": "<值>"}, "baseline_instrument_args": {}, "steps": ["沒有 Macrobenchmark 時寫 adb shell input 步驟"],
               "valid_iterations": {"frame_count_runs": [1033, 1014], "confirmed_in_trace": [0, 1, 2, 3, 4]},
               "started_utc": "…", "ended_utc": "…", "baseline_run_id": "…"},
  "tooling": {"android_profiler_skill_commit": "95ea931a1ad8f9b2be132ae0cfb2aad964d71118",
              "trace_processor_version": "Perfetto v57.2-…", "trace_processor_sha256": "<平台二進位雜湊>",
              "perfetto_tools_ref": "v57.2", "simpleperf_ndk": "28.2.13676358",
              "trace_processor_platform": "mac-arm64", "trace_processor_sha256_note": "平台二進位的雜湊,不是 skill 裡那支包裝腳本", "simpleperf_version": "<simpleperf --version 輸出>",
              "python_deps": ["texttable", "protobuf"],
              "benchmark_macro_version": "1.4.1", "queries": "queries.sql", "queries_sha256": "…"},
  "contract_refs": [{"contract": "Systems/結帳流程 ★INVARIANT★ 從主頁進結帳…", "threshold": "frameOverrunMs P90 ≤ 0", "result": "沒達(3.6)"}],
  "artifact_store": {"where": "本機 <專案>/.lumos/artifacts/android/<run-id>/", "keep_until": "<日期或人裁>", "how_to_get": "找 <誰> 或 <儲存位置>"},
  "layers": [
    {"layer": "L0", "why_escalated": null, "tool": "lumos macrobench", "result": "3 項變慢", "artifacts": ["macrobench-compare"],
     "native_retained": [{"func": "<照抄 --json 的 sites 前 5 筆,L0 通過而排行有內容時才有這欄>", "so": "…", "caller": "…", "retained": 0}]},
    {"layer": "L1", "why_escalated": "L0 退步:frameOverrunMs P90 跨零", "tool": "android-profiler perfetto-trace-analysis",
     "result": "主嫌 obtainView,Running 99.9%,無子 slice", "queries": ["Q17", "Q26"]},
    {"layer": "L2", "why_escalated": "Q26:obtainView cpu≈wall 且無子 slice", "tool": "simpleperf --call-graph fp",
     "compile": "speed+debug-info(數字不可跟 L0 比)", "result": "MainActivity.kt:36 佔 86.6%",
     "replay": {"artifact": "replay-script", "seconds": 30, "record_delay_s": 4},
     "commands": ["<錄製、annotate、還原的完整指令,照實際跑的抄>"],
     "source_snapshot": "pre-fix-source(修前原始碼快照的 artifact id;行號指的是這一版)",
     "annotate": {"source_root": "<絕對路徑>", "filters": "--include-tid 1030"},
     "device_state_before": "<Dexopt state 與 getprop>", "device_state_after": "<同上>", "restored": true,
     "artifacts": ["perf-data", "debug-odex", "annotate-summary", "replay-script"]}
  ],
  "artifacts": [
    {"id": "macrobench-compare", "kind": "lumos-macrobench-json", "path": ".lumos/artifacts/android/<run-id>/macrobench.json",
     "sha256": "…", "bytes": 0, "committed": false, "redacted": false}
  ],
  "result": {"state": "measured | inconclusive | not-run", "report": "report.md", "gaps": ["…"]}
}
```

- 每個 artifact 都要有 `id`、`sha256`、`bytes`;查詢標頭用 `id` 指 Trace,不要寫路徑。
- `contract_refs`:這次驗證對到的功能節點合約;從 `lumos macrobench --json` 的門檻判定照抄 `contract`,沒有門檻檔時寫空清單。
- `instrument_args` 基準與候選都要寫;APK 雜湊相同時,報告要明講差異只在輸入,不能寫成「程式退步」。
- 結論只靠一輪 Trace 時,報告要寫明是哪一輪;要說「5 輪都這樣」,queries.sql 就要有逐輪的查詢。
- L0 的結論(`lumos macrobench` 比對)與 L2 的行號不在 `rerun.sh` 裡,報告的〈重跑〉一節要寫可直接貼上執行的指令:L0 寫比對用的設定與 `lumos macrobench --json`,L2 寫 `annotate.py` 的完整參數。
- 被排除不用的檔不列,或列了並寫 `excluded_reason`。
- `result.state`:環境失敗(裝置斷線、Trace 掉資料、帳號失效)寫 `inconclusive`,不算失敗也不算通過。

## queries.sql 標頭

每條查詢前一行,欄位用空白分開,值不含空白:

```
-- [Q17] session=cand trace=cand-iter000 requires=Q15 expect=obtainView:n=148,total_ms=1151.14
select ...;
```

- `session`:同一個 trace_processor session 的名字;同名的查詢依序在同一個 session 跑。
- `trace`:artifact `id`。同一個 session 只能對一份 Trace。
- `requires`:要先跑過的查詢(建暫存表、`include perfetto module`);沒有寫 `-`。
- `expect`:`<列的第一欄值>:<欄>=<值>,…`,比對時數值取到小數兩位;只建表不出結果的寫 `expect=-`。第一欄的值不能有空白、冒號、逗號,也要是字串(輸出裡帶引號那種);名稱不合(例如 `Heap size (KB)`、`HWC:validate`)或第一欄是數字時,SQL 裡另取一個字串別名當第一欄(`'heap_kb' as k`)。
- `rerun.sh` 遇到標頭數跟解析到的條數不一樣、一條 expect 都沒有、或 manifest 列的 Q 不在檔裡,會回 2 並說原因;這是收據本身寫錯,不是量測結果不符。
- 下一行起到第一個以 `;` 結尾的行是 SQL 本體,一條一個語句;註解行不要以 `;` 結尾,不然查詢會被截在那一行。
- 查詢有兩種來源:固定的分析查詢(每次都一樣、只換參數,例:分 XML / Compose 的 `scripts/templates/android-ui-attribution.sql`)放工具鏈的範本目錄、整份貼進來;其餘一次性、照這次症狀寫的查詢照舊手寫在這裡。範本裡的佔位字(例:`__PROCESS__`)貼進來時就換掉,不要留在收據裡。佔位字有兩種寫法:`{{NAME}}` 是 lumos 程式自己替換的(例:回頭重讀的派工詞範本),`__NAME__` 是給 AI 照 skill 手動替換的(例:這支查詢範本,而且它在 SQL 的字串引號裡)。

## rerun.sh

範本是工具鏈的 `scripts/templates/android-receipt-rerun.sh`(接上 Lumos 的專案裡同一個路徑也有一份),寫收據時原樣複製進收據目錄,不要改:

```
cp scripts/templates/android-receipt-rerun.sh .lumos/receipts/<run-id>/rerun.sh
```

跑前把 `$SKILL_ROOT/references/perfetto/bin` 放進 PATH(或用 `TP=<trace_processor 路徑> ./rerun.sh` 指定)。需要 python3.7 以上(標準庫;腳本用 UTF-8 模式跑,收據裡有中文也不受系統語系影響,檔頭帶 BOM 也讀得到)。回傳碼:0 全部相符、1 有比對不符、2 收據本身寫錯或環境沒準備好(標頭沒被解析到、一條 expect 都沒有、manifest 列的查詢不在檔裡、查詢指到 manifest 沒有的 artifact、requires 指到不存在的查詢、分析工具執行不了),回 2 時在 stderr 印「擋下:」開頭的原因。

- 每條查詢只重放它 `requires` 鏈上的語句,不重放同 session 其他查詢:trace_processor v57.2 的 `-q` 一個檔裡有兩條回傳列的語句會直接報錯(2026-10-23 實測)。所以 `requires` 只能指 INCLUDE / CREATE 這類不回傳列的語句。
- 不靠常駐 session 的狀態,別人重跑得出一樣的結果;查詢多時會慢。
- 停在 L0 的收據也要有幾條 Trace 查詢(每輪 App 畫格數、超時格數),驗 `valid_iterations.confirmed_in_trace`;L0 本身的重跑指令寫在 report.md(見 SKILL.md L0 第 5 步)。

## 記憶體與穩定性收集

規則單源 `Projects/Android記憶體與穩定性驗收_計劃`;這裡只放照抄用的寫法。

`.lumos/macrobench.json` 加 `stability` 段(有這段時 `results_dirs` 可以不填):

```json
{"stability": {
  "package": "com.example.app",
  "scenario": "com.example.bench.PlayerLeak#cycle",
  "driver": "adb shell am instrument -w -e class com.example.bench.PlayerLeak#cycle -e cycles {{CYCLES}} com.example.bench/androidx.test.runner.AndroidJUnitRunner",
  "warmup": 2, "cycles": 5,
  "test_data": {"value": true, "decided_by": "<裁定的人>", "decided_at": "<YYYY-MM-DD>"},
  "strictmode": true, "category": "app"}}
```

- `driver` 跑兩次(暖機、量測),`{{CYCLES}}` 換成輪數,環境變數 `CYCLES` 與 `ANDROID_SERIAL`(設了 `adb_serial` 時)也會給;打開原生配置排行的情境再多跑兩次(第二段的暖機與量測)。
- `native_retained`(選填,預設不寫=全部不跑):要列原生配置排行的情境名清單,`"@default"` 代表沒指定情境的 stability 段本身,其他名字要是 `stability_scenarios` 裡的情境。打開的情境在既有量測讀完之後另跑一段 W+N 輪只錄 heapprofd(要 `test_data` 的 value 是 true、Android 11 以上、App 是 profileable 或 debuggable),驗收多花約一段量測的時間;情境含下單這類後端副作用時,第二段會再多下 W+N 次。結果寫在 `stability.json` 的 `native_retained` 段,`lumos macrobench --stability` 印前 20 個,只提醒不擋。
- `test_data` 不寫就不錄 Java 快照,java_growth 與 instances 列成跳過。範例的裁定人與日期是佔位,不能照抄:要先問人「這個專案是不是只在測試帳號與假資料下跑」,照對方的回答填真的人名與日期(--check-config 只擋得住 <裁定的人>、<YYYY-MM-DD> 這種原樣照抄的佔位,改成別的假名字它分不出來;真正的防線是先問人)。
- `strictmode` 寫 true 的前提是測試建置真的打開了 StrictMode 的 VM 規則並 `penaltyLog()`;宣告了卻沒開,零筆照樣判通過。
- release 建置開 R8 時加 `"mapping": "app/build/outputs/mapping/benchmark/mapping.txt"`,類別名才還原得回來。

跑:`sh scripts/templates/android-stability-collect.sh [run-id]`(在專案根目錄;`ADB`、`TP`、`JAVA_HEAP_DUMP` 指外部工具),再 `lumos macrobench --stability .lumos/artifacts/android/<run-id>/stability.json`。

- 主機的 `python3` 要 3.11 以上(腳本用 `python3 -P`;工具鏈本身要求 3.14)。
- run-id 只收英數字、點、底線與連字號,也不能只有點(它會用在裝置上的路徑);不給就用 `stability-<日期時間>`。
- 專案是 git repo 時,`.lumos/artifacts/` 要先在 `.gitignore` 裡,不然腳本回 2、不碰裝置。
- 保留:每次開跑時只自動刪超過 7 天的 `heap-*.pftrace`(含原生配置排行那段的 `heap-native.pftrace`;不再跑就不會刪);`cycle.pftrace`(量測那段的追蹤檔)、`record.pbtxt` 與 `record-native.pbtxt`(錄製設定)、`logcat.txt`(只有違規行)、`stability.json` 不自動刪;原始日誌 `logcat.raw` 不管成不成都在收集結束前刪掉。整個 run 目錄不進版控,用完自己刪。
- `java_heap_dump` 逾時或被中斷時,它在裝置 `/data/misc/perfetto-traces/` 底下的暫存快照(`java-profile-*`)可能留著;收集腳本只清自己的 `lumos-stability-<run-id>.*` 與 `lumos-native-<run-id>.*`,那份要自己 `adb shell ls` 看過再刪;主機當掉或 adb 斷線時這兩種也可能留著,先 `adb shell ls /data/misc/perfetto-traces/ /data/misc/perfetto-configs/` 列出來,只挑 `lumos-stability-<這次的 run-id>.` 與 `lumos-native-<這次的 run-id>.` 開頭的,對每一個寫完整路徑刪(同目錄別的檔可能是別人正在錄的)。
- 測試縮短用的環境變數:`LUMOS_STABILITY_SETTLE`(預設 2 秒)、`LUMOS_STABILITY_STOP_TIMEOUT`(30 秒)、`LUMOS_STABILITY_LONG_TIMEOUT`(1800 秒),平常不用設。`LUMOS_STABILITY_STEP_BUDGET_S` 由端到端範本傳(這一步的上限秒數),預估原生配置排行那段跑不完就不跑、寫 failed「時間不夠」;手動跑不用設。

門檻檔 `.lumos/macrobench-thresholds.json` 的寫了 `check` 的條目(`scenario` 要等於 stability 段的 scenario;另加 `contract`、`decided_by`、`decided_at`):

| check | 自己的欄位 |
|---|---|
| native_unreachable | `max_bytes`(預設 0) |
| java_growth | `min_per_cycle`(預設 1)、`exclude_prefixes`(蓋掉預設排除的 java.、javax.、kotlin.、android.、androidx.、dalvik.、libcore.、sun.) |
| instances | `class`、`max` |
| peak_vitals、exits、strictmode | 無 |
| frozen | `max_block_ms`(選填) |

每一種都另外可以寫 `device_model`(選填,指定裝置型號;結果檔換了裝置時那條跳過)。

寫了表格以外的欄位會被當成寫錯、回 2。例:

```json
{"version": 1, "thresholds": [
  {"scenario": "com.example.bench.PlayerLeak#cycle", "check": "java_growth", "min_per_cycle": 1,
   "contract": "Systems/播放器釋放:畫面關掉時 SDK 都要 release", "decided_by": "<裁定的人>", "decided_at": "<YYYY-MM-DD>"},
  {"scenario": "com.example.bench.PlayerLeak#cycle", "check": "instances", "class": "com.example.app.PlayerActivity", "max": 1,
   "contract": "Systems/播放器釋放:畫面關掉時 SDK 都要 release", "decided_by": "<裁定的人>", "decided_at": "<YYYY-MM-DD>"},
  {"scenario": "com.example.bench.PlayerLeak#cycle", "check": "exits",
   "contract": "Systems/播放器釋放:畫面關掉時 SDK 都要 release", "decided_by": "<裁定的人>", "decided_at": "<YYYY-MM-DD>"}]}
```

UI Automator 驅動要「自己測自己」(測試模組的 `targetPackage` 是測試套件本身,Macrobenchmark 模組就是這種),否則每次 `am instrument` 會重啟被測 App,記憶體累積不起來:

```kotlin
@RunWith(AndroidJUnit4::class)
class PlayerLeak {
    @Test fun cycle() {
        val n = InstrumentationRegistry.getArguments().getString("cycles")!!.toInt()
        val device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
        repeat(n) {
            device.findObject(By.res("com.example.app", "open_player")).click()   // 開畫面
            device.wait(Until.hasObject(By.res("com.example.app", "player")), 5_000)
            device.pressBack()                                                     // 關畫面
            device.wait(Until.hasObject(By.res("com.example.app", "open_player")), 5_000)
        }
    }
}
```

Maestro 驅動:flow 不能用會先停 App 的 `launchApp`(要嘛不啟動,要嘛 `stopApp: false`),兩次呼叫都從同一個起點畫面開始,輪數用 `-e` 傳(`"driver": "maestro test -e CYCLES={{CYCLES}} .maestro/player-cycle.yaml"`):

```yaml
appId: com.example.app
---
- repeat:
    times: ${CYCLES}
    commands:
      - tapOn:
          id: "open_player"
      - assertVisible:
          id: "player"
      - back
```

`repeat` 的 `times` 吃不吃 `${CYCLES}` 這種變數,官方文件沒寫、這裡也沒實測過;子案二接 Maestro 時先驗,不行就改用 `while` 加計數。
