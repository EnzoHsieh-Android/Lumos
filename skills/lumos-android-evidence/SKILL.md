---
name: lumos-android-evidence
description: Android 效能問題逐層查到哪一行,並留一份別人重跑得出來的驗證收據。L0 看 Macrobenchmark 結果有沒有變慢或沒達門檻,有才 L1 用每輪的 Perfetto Trace 跑官方分析找卡在哪,指到 App 自己的程式在 CPU 上算才 L2 用 simpleperf 指到檔案與行號,熱點是記憶體才 L3(要人裁)。觸發:Android 滑動卡、啟動慢、lumos macrobench 報退步、要查「哪一行讓它變慢」、要留效能驗證證據。
---

# lumos-android-evidence:Android 效能逐層診斷與驗證收據

白話:不一次把工具開滿,上一層真的看到異常才往下一層;每一層的資料、查詢與「為什麼往下」都寫進同一份收據。執行全由你(Agent)照這頁做,Lumos 只負責 L0 的比對(`lumos macrobench`),不碰裝置。設計與取捨單源在 [[Projects/Android逐層診斷_計劃]];收據格式在本目錄 `reference.md`。

## 先準備(每台機器一次,版本要釘)

| 工具 | 釘的版本 | 取法 |
|---|---|---|
| 官方 android-profiler skill | `95ea931a1ad8f9b2be132ae0cfb2aad964d71118` | `git clone https://github.com/android/skills` 後 checkout 這個 commit;`SKILL_ROOT=<clone>/profilers/android-profiler` |
| trace_processor | Perfetto v57.2 | `$SKILL_ROOT/references/perfetto/bin/trace_processor`(包裝腳本,第一次會下載並驗雜湊;不要另找別的版本) |
| 錄製腳本 | Perfetto v57.2 | `https://raw.githubusercontent.com/google/perfetto/v57.2/tools/` 底下的 `cpu_profile`、`heap_profile`、`java_heap_dump`,不要抓 `main` |
| simpleperf | NDK 28.2.13676358 | `$ANDROID_HOME/ndk/28.2.13676358/simpleperf`;`annotate.py` 要 `texttable`、`protobuf`,裝在獨立 venv,不動系統 Python |

換版要重驗,並在收據 `tooling` 記新版本。

## 不准做的事

- 不上傳 Trace、perf.data、記憶體檔到任何外部服務或公共模型。原始檔只放專案 `.lumos/artifacts/android/<run-id>/`(確認在 `.gitignore`);進版控的只有收據目錄 `.lumos/receipts/<run-id>/`。
- 不把任何一層的毫秒數字當推送閘,也不從這次的數字反推出「合約」。門檻只能來自人裁,寫在專案的 `.lumos/macrobench-thresholds.json`(格式與節點寫法見 [[Projects/Macrobenchmark驗收門檻_計劃]]);沒有門檻檔就只跟基準比。
- 沒有人裁的保存規則,不錄 L3(記憶體快照可能含個資)。
- 模擬器的結果只能寫「流程驗證」,不能寫成效能通過。

## L0:有沒有變慢、有沒有達門檻

1. 跑專案的 Macrobenchmark(實體裝置、USB、先 `adb shell svc power stayon usb`;跑前刪掉裝置上 `/sdcard/Android/media/<benchmark 套件>/` 舊檔)。
2. 記下這次的輸入:啟動參數(`am instrument -e …`、intent extras)、測試資料、Feature Flag。基準與候選兩邊都記;同一個 APK 只換參數時,這是兩邊唯一的差異,沒記就證明不了差在哪。
3. 跑前跑後各記一次裝置狀態(L0 是推送前的綁定測試閘代跑、你拿到時已經跑完的話,當下補量一次,收據 gaps 寫明是事後量的):型號、`ro.build.fingerprint`、電量、`dumpsys thermalservice` 的 Thermal Status;從裝置 `pm path` 拉實際安裝的 APK 算 sha256(同一份原始碼重建的 APK 雜湊會不同,只記建置產物不夠)。
4. 拉回結果 JSON 與每輪 `.perfetto-trace` 到 artifacts 目錄,算 sha256 與大小。
5. `lumos macrobench --json` 比對基準,輸出存成 artifact,並把比對用的設定與指令寫進 report.md(L0 的重跑方式)。
   - 基準是專案自己存的 `.lumos/macrobench-baseline.json`:在專案根直接跑。
   - 基準是另一次執行(例如同一天先跑的正常版):不要覆蓋專案的基準檔。另建一個暫存目錄,放 `.lumos/macrobench.json`(`results_dirs` 寫基準那次的絕對路徑),並把專案的 `.lumos/macrobench-thresholds.json` 複製進暫存目錄的 `.lumos/`(門檻是從 `--repo` 指的目錄讀的,沒複製就一條門檻都不判),`lumos macrobench --repo <暫存目錄> --update-baseline`,再把 `results_dirs` 改成候選那次的路徑跑 `--json`;收據 `scenario.baseline_run_id` 旁寫明基準是這樣產生的。
6. 找 L1 要對照的基準 Trace:專案基準檔(`.lumos/macrobench-baseline.json`)只有統計值,但每個情境的 `source` 記了它來自哪個結果檔與 sha256;去 artifacts 找雜湊對得上的那次執行,用同一次留下的 Trace。基準是舊版工具存的(沒有 `source`)或那次的 artifacts 已經不在,就用同裝置、同情境、最近一次正常版執行代替,收據寫明它不是基準的來源;都沒有就先用目前正常版的程式重跑一次。
7. 檢查有效輪:讀結果檔每輪 `frameCount.runs`(滑動)或每輪啟動時間;某幾輪畫格數明顯少一截,先懷疑量測腳本沒真的操作到(例:清單已停在底部),在收據 `valid_iterations` 記下來,L1 時用 Trace 確認。
8. **往下條件**:`--json` 的 `regressions` 不是空的(比基準變慢),或 `threshold_failures` 不是空的(沒達人裁的驗收門檻)。都沒有 → 收據記 `L0 通過` 後停,不錄 L2、L3。`threshold_skipped` 裡的門檻(換了裝置、情境沒跑到)要寫進收據 gaps,不能當成達標。
9. 沒達門檻的那幾條各帶 `contract`(功能節點的合約行):照抄進收據 `contract_refs`,寫回時對到那個功能節點。

## L1:卡在哪、在算還是在等

照官方 `$SKILL_ROOT/analysis/workflows/perfetto-trace-analysis/perfetto_trace_analysis.md` 的 Step 1–4 做,含 Step 2 triage 與 Step 3 每個候選的 per_candidate_analysis(skill 要你派子代理的地方就派)。

- 用 L0 那次執行留下的 Trace,不另錄。主要對象挑「有效輪裡超時格最多」的那一輪:超時格數用結果檔 `sampledMetrics.frameOverrunMs.runs[i]` 裡大於 0 的個數(不要用 Trace 的 jank_type,Samsung 上幾乎每格都標 Buffer Stuffing);基準取同一輪次。
- triage(Step 2)的派工也附基準 Trace 路徑,要求每個候選附基準同名 slice 的次數與耗時;基準也有同樣量的(例如每格都在的無障礙 binder 呼叫),是本來就有的成本,不算這次的退步。
- 官方流程要你寫的 `perfetto_analysis_report.md` 不另寫檔,內容併進收據的 report.md(子代理只在回報裡給結果)。
- 派 triage 與 per_candidate 子代理時,要求它們回報的每條 SQL 照 reference.md 的 queries.sql 標頭格式寫:第一欄是可當 key 的名稱、用行程或執行緒名稱篩,不要寫死 utid/upid;收據才接得上 rerun.sh。
- 官方流程要問使用者的地方(症狀、要深挖哪些候選),用 L0 的退步項當症狀,triage 嚴重度前 1–3 名全部深挖。
- 每一條 SQL 照 `reference.md` 的標頭格式寫進收據的 `queries.sql`,附 `expect`。
- **往下條件**(寫進收據 `layers[1].why_escalated`,引用 Q 編號):
  - 主嫌是 App 自己行程的主執行緒或 RenderThread,那段時間多數是 Running,而且那個 slice 底下沒有能解釋時間的子 slice → **L2**。
  - 主嫌是等待(S/D 狀態、binder、鎖、I/O)→ **留在 L1**,照官方 per_candidate 順著喚醒鏈追到源頭;源頭在別的行程就記成共同嫌疑,不往 L2。
  - 主嫌是 GC、配置記憶體、LMK → **L3**(沒授權就停,記 `[GAP] L3 未授權`)。
  - L1 證實 L0 報的那一項是平台雜訊(例如 frameOverrunMs P50 在 120Hz 面板因緩衝深度兩群跳動,基準各輪本來就在跳),但 A/B 比對另外找到 App 自己的 CPU 退步 → 照那個退步的性質往下,`why_escalated` 兩件事都寫。

## L2:哪個函式、哪一行

這一層會改變 App 的編譯狀態,**數字不能跟 L0 比快慢**,只拿來定位。

1. 先記原狀(寫進收據,還原後再比一次):
   ```
   adb shell dumpsys package <套件> | grep -A3 'Dexopt state'
   adb shell getprop debug.generate-debug-info
   ```
   再開除錯資訊並完整編譯:
   ```
   adb shell setprop debug.generate-debug-info true
   adb shell am force-stop <套件>
   adb shell cmd package compile -f -m speed <套件>
   ```
2. 重現 L0 的同一個情境並同時錄。順序固定:先在背景開始重現(用同一支 Macrobenchmark 測試、或收據寫好的 `adb shell input` 步驟),重現時間要比錄製長(例:重現 30 秒、錄 10 秒);等 `adb shell pidof <套件>` 有值再開錄:
   ```
   python3 <simpleperf>/app_profiler.py -p <套件> -r "-e task-clock:u -f 1000 --call-graph fp --duration 10"
   ```
   用 `adb shell input swipe` 重現前,先看 `adb shell dumpsys window | grep mCurrentRotation`:平板常是橫向,`wm size` 給的是直向的實體尺寸,座標要照旋轉後的方向算。
   收據記重現秒數與開錄延遲;重現用的腳本或步驟連同參數存成 artifact,讓人確認 L2 跟 L1 是同一個條件。
   - 先用 `--call-graph fp`:熱點在讀時鐘時(vdso),DWARF 堆疊與 Perfetto 的 traced_perf 在 Samsung SM-X710 / Android 16 都會斷在 vdso,只有 fp 上得去(2026-10-23 實測)。
   - fp 錄完,annotate 的 Function/Line 表是空的,或主執行緒樣本裡看得到 App 自己框架的不到一成 → 趁裝置還在除錯編譯狀態,用同一個重現補錄一次 `--call-graph dwarf`。熱點在配置記憶體時 fp 會斷在 ART 的配置慢路徑,dwarf 反而接得上(同日實測)。兩份都放進收據,報告寫明行號來自哪一份。
3. 標行號:
   ```
   <venv>/bin/python <simpleperf>/annotate.py -i perf.data -s <App 原始碼根> --comm <主執行緒名或套件> --ndk_path <NDK>
   ```
   看 `annotated_files/summary` 的「Function/Line」表與標註後的原始碼。只看主執行緒時用 `--include-tid <主執行緒 tid>`(tid 從 `report_sample.py` 的輸出看;`--comm` 要填 simpleperf 看到的行程名,跟 Perfetto 截成 15 字的執行緒名不一樣,容易篩錯,不建議用),佔比的分母會變;實際用的篩選參數與原始碼路徑寫進收據。
   熱點函式沒出現在 Function/Line 表(常見於被呼叫的同檔小函式):用 `report_sample.py --show_art_frames` 數主執行緒堆疊含那個函式的樣本比例,函式內的行號標 [INFERRED],或用 `report_html.py --add_source_code` 看逐行。
   行號靠 `binary_cache/` 裡帶除錯資訊的 `base.odex`,沒有它只剩函式名:把那支 odex 列進 artifacts(帶 sha256),整個 binary_cache 目錄留在本機 artifacts。要看完整堆疊或函式彙總用 `report_sample.py --show_art_frames` 或 `report_html.py`;不要用 `report.py`(要 tkinter,終端機跑不起來)。
4. 還原裝置(一定要做,寫進收據):
   ```
   adb shell setprop debug.generate-debug-info "''"
   adb shell cmd package compile --reset <套件>
   ```
   原狀是 `status=verify reason=cmdline`(Macrobenchmark 用 CompilationMode.None 跑過後的狀態)時,`--reset` 只回到 `reason=install`,再補 `adb shell cmd package compile -f -m verify <套件>`。
5. 還原後再跑一次第 1 步的兩條指令,跟原狀比對;收據 `restored` 只在兩者相符時寫 true。
6. 收據 `layers[2]` 記 `compile: speed+debug-info`、熱點檔案與行號、佔比;perf.data 與 annotate 輸出放 artifacts。
7. **往下條件**:熱點行在配置記憶體(new、集合擴容、字串串接)或 GC → L3;否則停。

## L3:誰配置、誰留住(預設關)

只有專案有人裁的保存規則(保存多久、誰看得到、能不能離開本機)才做;收據 `[DECISION]` 記是誰、哪天裁的。HPROF 類檔案不進版控、不外傳。重現情境照 L2 第 2 步的順序(背景重現、等 `pidof` 有值再開錄)。

1. 誰在配置(Java):`heap_profile -n <套件> --heaps com.android.art -d 10000 -o <目錄>`。`-o` 的目錄要先建好,不存在時它只印一行就結束、什麼都沒錄。原生配置把 `--heaps` 換成 `libc.malloc`。
   查 App 自己的函式各經手多少配置(對 `raw-trace`):
   ```
   with recursive anc(alloc_id, callsite_id) as (
     select a.id, a.callsite_id from heap_profile_allocation a where a.size > 0
     union all select anc.alloc_id, c.parent_id from anc join stack_profile_callsite c on c.id = anc.callsite_id where c.parent_id is not null)
   select f.name, sum(a.size) bytes from anc
     join stack_profile_callsite c on c.id = anc.callsite_id join stack_profile_frame f on f.id = c.frame_id
     join heap_profile_allocation a on a.id = anc.alloc_id
   where f.name like '%<套件片段>%' group by 1 order by bytes desc;
   ```
   只到函式,沒有行號;函式很長時再對照 L2 的行號。
2. 誰留住(Java):重現跑完、App 還活著時 `java_heap_dump -n <套件> -o <檔>.perfetto-trace`。查支配樹最大的幾個,再查是哪個欄位指到它:
   ```
   include perfetto module android.memory.heap_graph.dominator_tree;
   select c.name, d.dominated_size_bytes, d.dominated_obj_count from heap_graph_dominator_tree d
     join heap_graph_object o on o.id = d.id join heap_graph_class c on o.type_id = c.id
   order by d.dominated_size_bytes desc limit 10;
   ```
   `heap_graph_reference` 以 `owned_id` 找回 `owner_id` 與 `field_name`,就是程式裡的變數名。
3. 收據 `layers[3]` 記兩份檔的雜湊、查詢 Q 編號與結果;快照可能含個資,`redacted` 照實填。

## 收尾

1. 收據的 `report.md` 是收據檔,不是給編排者的報告;子代理環境擋 Write 寫報告檔時,用 Bash 寫入。報告用官方標籤:`[SQL]`(指得回 Q 編號或結果檔)、`[INFERRED]`、`[GAP]`,另加 `[DECISION]`(人裁的接受標準)。
2. 把 `scripts/templates/android-receipt-rerun.sh` 複製成收據目錄的 `rerun.sh`(不用改),自己跑一次確認回 0;回 2 是收據本身寫錯,照它印的原因修。
   收據進版控時,`queries.sql`、`rerun.sh` 會被「每支檔有家」當程式檔擋下:第一次在專案的 `.lumos/config.json` 加 `"node_home": {"ignore": [".lumos/receipts/*"]}`(已有 node_home 就只加進 ignore 清單),收據是驗證留下的紀錄,不需要家。
3. 依調研〈寫回規則〉決定寫回:相同條件達標 → Verification pass;退步或證實有問題 → 開或更新 Issue;條件不等價、缺基準、Trace 掉資料 → pending,不寫 pass。
4. 要證明收據夠用(提交前必做):派一個沒脈絡的 Agent,只給收據目錄與原始檔,跑 `rerun.sh` 並判每條結論;它抓到的問題改完、重跑 `rerun.sh` 回 0 才提交。要盲測分析能力時,artifacts 目錄名改成中性的(不要叫 `bind8` 這種會洩露答案的名字)。
