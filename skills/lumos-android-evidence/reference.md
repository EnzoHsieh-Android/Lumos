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
  "scenario": {"id": "…", "benchmark": "<類別#方法>", "iterations": 5, "compilation_mode": "None",
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
    {"layer": "L0", "why_escalated": null, "tool": "lumos macrobench", "result": "3 項變慢", "artifacts": ["macrobench-compare"]},
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
- 下一行起到 `;` 結束是 SQL 本體,一條一個語句。

## rerun.sh

範本是工具鏈的 `scripts/templates/android-receipt-rerun.sh`(接上 Lumos 的專案裡同一個路徑也有一份),寫收據時原樣複製進收據目錄,不要改:

```
cp scripts/templates/android-receipt-rerun.sh .lumos/receipts/<run-id>/rerun.sh
```

跑前把 `$SKILL_ROOT/references/perfetto/bin` 放進 PATH(或用 `TP=<trace_processor 路徑> ./rerun.sh` 指定)。需要 python3(標準庫)。回傳碼:0 全部相符、1 有比對不符、2 收據本身寫錯(標頭沒被解析到、一條 expect 都沒有、manifest 列的查詢不在檔裡、查詢指到 manifest 沒有的 artifact、requires 指到不存在的查詢),回 2 時在 stderr 印「擋下:」開頭的原因。

- 每條查詢只重放它 `requires` 鏈上的語句,不重放同 session 其他查詢:trace_processor v57.2 的 `-q` 一個檔裡有兩條回傳列的語句會直接報錯(2026-10-23 實測)。所以 `requires` 只能指 INCLUDE / CREATE 這類不回傳列的語句。
- 不靠常駐 session 的狀態,別人重跑得出一樣的結果;查詢多時會慢。
- 停在 L0 的收據也要有幾條 Trace 查詢(每輪 App 畫格數、超時格數),驗 `valid_iterations.confirmed_in_trace`;L0 本身的重跑指令寫在 report.md(見 SKILL.md L0 第 5 步)。
