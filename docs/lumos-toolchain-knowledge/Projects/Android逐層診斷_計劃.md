---
type: project
status: doing
created: 2026-10-23
updated: 2026-10-23
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
lands_in:
  - Systems/macrobenchmark-adapter
related:
  - "[[Projects/Android診斷證據接入_調研]]"
  - "[[Projects/Macrobenchmark退步提醒_計劃]]"
---
# Android逐層診斷_計劃

白話:Android 效能問題不靠一次把所有工具開滿,而是一層一層往下查:先看基準結果有沒有變慢或沒達門檻,有才看 Trace 找卡在哪,Trace 指到 App 自己的程式在 CPU 上算很久、又沒有更細的打點,才錄 CPU 取樣指到檔案與行號;熱點落在記憶體配置或回收才往記憶體那層。每往下一層都寫進同一份驗證收據,並記下為什麼往下。落地成調研第一階段的轉接 skill `lumos-android-evidence`:skill 教 Agent 怎麼跑、怎麼判斷要不要往下;Lumos 核心不呼叫 adb、不跑工具。Enzo 2026-10-23 裁:「我需要能看到哪一行程式的評測結果……層遞式的,當這份 trace 實際錄出異常,或是不達驗收門檻時,就往下一個工具執行」。

WHY:分層往下、每層有觸發條件,不一次全錄 [出處:2026-10-23 Enzo 裁] [因:CPU 取樣要重新編譯 App 並帶除錯資訊,會改變被量的對象;記憶體快照可能含個資;沒有異常就全錄等於每次都付最貴的代價] [不選:每次都錄 Trace+CPU 取樣+記憶體(慢、改變被量對象、留下不必要的敏感檔)]
WHY:指到行號用 simpleperf 加帶除錯資訊的完整編譯,先錄回程位址堆疊(`--call-graph fp`)、對不到行號再補錄 DWARF,不用 Perfetto 的 traced_perf [出處:2026-10-23 SM-X710 實測,見〈第零階段試跑〉與〈四組驗證〉] [因:traced_perf 與 simpleperf 預設的 DWARF 堆疊都在系統讀時鐘那段核心提供的程式(vdso)斷掉,1654 個樣本全部解不出上一層;改回程位址堆疊後 2215 個樣本接回 `getView`,官方 `annotate.py` 標出第 36 行佔 86.6%] [代價:熱點在配置記憶體時 fp 會斷在 ART 配置慢路徑(s05 主執行緒 651 樣本只有 16 個看得到 App 框架),要多錄一次 DWARF] [不選:traced_perf callstack_sampling(本機實測斷在 vdso);Java method tracing(只到函式、沒有行號,且開銷大);只用 DWARF(熱點在讀時鐘時斷在 vdso)]
WHY:量速度的那一層與指行號的那一層分開記,行號層的數字不拿來比快慢 [出處:2026-10-23 實測] [因:指行號要 `cmd package compile -f -m speed` 並開 `debug.generate-debug-info`,跟 Macrobenchmark 的 CompilationMode 不同,執行速度不可互比] [代價:要多跑一次情境]
WHY:執行與判斷放在 skill,不加 Lumos 指令 [出處:[[Projects/Android診斷證據接入_調研]] 第一階段、[[Projects/後端工程提問與證據擴充_計劃]] 決策 d6] [因:Lumos 零依賴、不碰裝置;要不要往下一層要讀 Trace 判斷,是 Agent 的工作] [不選:lumos android-evidence 執行器]
WHY:收據的重跑腳本是工具鏈 `scripts/templates/` 裡的一支範本檔,登記在工具組複製清單、跟其他範本一起進消費專案,寫收據時再複製進收據目錄;它是獨立腳本、不呼叫 lumos,錯誤照 lumos 慣例回 2 並在 stderr 印「擋下:」;skill 目錄本身只放 .md、不放可執行檔 [出處:2026-10-23 代碼審 code-android-evidence r1 架構對齊席 A3、r2 架構對齊席(原本把腳本寫在 reference.md 的程式碼區塊,測試得從 markdown 抽出來執行,是專案沒有的第二種做法)、r3 架構對齊席(範本目錄原本只放文字範本);跑滿 3 輪,Enzo 同日裁「留在範本目錄、加一輪」] [因:收據要能讓沒脈絡的人一鍵重跑([[Projects/Android診斷證據接入_調研]]〈收據格式草案〉),腳本得跟著收據進消費專案的版控;其他 skill 都沒有可執行檔,安裝器整個目錄 symlink,放執行檔要另外處理權限與更新] [不選:做成 lumos 子指令(收據要在沒裝 Lumos 的機器上也重跑得了,而且調研第二階段定了 Lumos 不執行第三方工具,重跑要叫 trace_processor);skill 目錄附一支 rerun.sh 讓消費專案直接呼叫(收據會依賴工具鏈的安裝位置,換機器就重跑不了);腳本寫在 reference.md 的程式碼區塊(測試只能從 markdown 抽出來跑,範本文字一改被測物就跟著變)] [test:t_android_evidence_rerun_refuses_empty]
PRIOR-ART: Google 官方 android-profiler skill(釘 95ea931a1ad8f9b2be132ae0cfb2aad964d71118)的 recording/analysis 流程與 [SQL]/[INFERRED]/[GAP] 標籤;Perfetto v57.2 的 trace_processor 與錄製腳本(`cpu_profile`、`heap_profile`、`java_heap_dump`,https://raw.githubusercontent.com/google/perfetto/v57.2/tools/);NDK 28.2.13676358 附的 simpleperf(`app_profiler.py`、`annotate.py`、`report_sample.py`,文件 android_application_profiling.md「Java 要完整編譯才標得出原始碼行」)。裁定:全借用,skill 只串流程與收據,Lumos 不加依賴。
RETIRE-IF: 連續兩個真實消費專案的退步案例,走完分層仍停在 [GAP]、指不到函式;或 Android Studio / 官方 skill 內建同樣的逐層與收據,就撤掉這個 skill 改指向官方。
REVISIT:2026-12-21 收據的 queries.sql 標頭多了沒有 = 的字、expect 少等號、manifest 缺 artifacts 或 queries 是 null 時,rerun.sh 噴 Traceback 回 1(只會報失敗、不會誤判通過);真實收據遇到過就改成回 2 並說原因(代碼審 code-android-evidence r4 F1 放行)
REVISIT:2026-12-21 KDS 或另一個真實專案跑過一次完整分層(不是注入的退步)了沒;沒有就判延後或撤案

## 四層與往下的條件

| 層 | 工具 | 回答 | 往下一層的條件 |
|---|---|---|---|
| L0 | Macrobenchmark 結果檔 + `lumos macrobench`(或人裁的門檻檔) | 有沒有變慢、有沒有達門檻 | 報出退步,或任一指標沒達人裁的門檻;都沒有就停,收據記 L0 通過 |
| L1 | 同一次執行每輪附帶的 Perfetto Trace + 官方 perfetto-trace-analysis(triage → per-candidate) | 卡在哪個執行緒、哪段框架 slice、是在算(Running)還是在等 | 主嫌是 App 自己行程的主執行緒或 RenderThread,在 CPU 上跑(Running 佔多數),且那段 slice 底下沒有更細的打點 → L2;主嫌是等待(binder、鎖、I/O)→ 留在 L1 順著喚醒鏈追;主嫌是 GC、配置或 LMK → L3 |
| L2 | simpleperf `--call-graph fp`,App 先 `cmd package compile -f -m speed` 且 `setprop debug.generate-debug-info true`;`annotate.py -s <原始碼目錄>` | 哪個函式、哪個檔、哪一行 | 熱點行落在配置記憶體(new、集合擴容)或 GC → L3;否則停 |
| L3 | heapprofd(原生配置)、java_hprof(Java 物件保留) | 誰配置、誰留住 | 最後一層 |

- L3 預設關閉:要錄 Java 記憶體快照或原生配置前,專案要先有人裁的保存規則(調研〈要人裁定的事〉三題),沒裁就在收據記 `[GAP] L3 未授權` 停在 L2。
- 每層開始前寫下「為什麼往下」一行(引上一層的 [SQL] 或結果檔數字),寫不出就不往下。
- 情境重跑:L2、L3 要重新操作同一個情境。有 Macrobenchmark 測試就用同一支測試加 `-e` 參數重跑;沒有就照收據裡寫的手勢或步驟,用 `adb shell input` 重現,步驟寫進收據。

## 收據格式補強(第零階段稽核發現)

沿用 [[Projects/Android診斷證據接入_調研]] 的 manifest 草案;欄位的現行寫法以 skill 的 reference.md 為準,這裡只記為什麼要補。第一次稽核補的:

- `device.cpu_locked`:照抄結果檔 `context.cpuLocked`。未 root 的裝置上它是 benchmark-common 依各核目前最低頻率猜的(`CpuInfo.isCpuLocked`),同一台會自己翻,兩邊不同時列進 gaps,不判成條件不等價。
- `scenario.valid_iterations`:每輪畫格數(結果檔 `frameCount.runs`)與 L1 確認有真的操作到的輪次;百分位要註明含哪幾輪。
- `project.installed_apk_sha256`:從裝置 `pm path` 拉的實際 APK 雜湊。同一份原始碼重建出的 APK 雜湊會不同(2026-10-23 實測),只記建置產物不夠。
- `tooling.trace_processor_sha256`、`tooling.simpleperf_ndk`:分析工具二進位的雜湊與 NDK 版本。
- `layers[]`:每層一筆 `{layer, why_escalated, tool, config, artifacts, result}`;L2 另記 `compile: speed+debug-info`,並標明數字不可跟 L0 比。
- 查詢檔每條一行機器可讀標頭 `-- [Qn] session=<名> trace=<artifact id> requires=<Qm,…> expect=<關鍵值>`,另附 `rerun.sh` 一次跑完並比對 expect。
- 比對輸出(例如 `lumos macrobench --json`)存成 artifact 帶雜湊,結論引它。
- 第二次稽核(四組收據的 s05)再補:基準與候選兩邊的啟動參數(同一個 APK 只換參數時,沒記就證明不了差在哪;這次是盲測時刻意拿掉才缺)、L2 重現腳本與參數存成 artifact、帶除錯資訊的 `base.odex` 列進 artifacts(沒有它 annotate 只剩函式名)、annotate 的篩選參數、L0 與 L2 的重跑指令寫進報告、逐輪查詢、原始檔保存位置。
- 證據標籤改用官方的 `[SQL]`/`[INFERRED]`/`[GAP]`,加 `[DECISION]`;調研草案寫的 `[MEASURED]` 是誤記。

## 條款

- [S1] 當 L0 比對沒有退步、也沒有不達門檻時,skill 應指示停在 L0、收據記 L0 通過,不得錄 L2、L3 [manual:無退步的結果檔走一次 skill,收據只有 L0;2026-10-23 s04 通過]
- [S2] 當 L0 報出退步時,skill 應指示用同一次執行的每輪 Trace 跑官方 triage,收據的 L1 那筆要引 L0 的退步項 [manual:注入 bindDelayMs 那次走一次,L1 的 why_escalated 指到 L0 退步項;2026-10-23 s02、s03、s05 通過]
- [S3] 當 L1 主嫌是 App 主執行緒的 Running 時間、且 slice 底下沒有子 slice 時,skill 應指示往 L2 錄 simpleperf,並在收據寫出 L1 的根據 [manual:注入 bindDelayMs 那次走到 L2,why_escalated 引 obtainView 的 cpu/wall 查詢;2026-10-23 s02 通過]
- [S4] 當走到 L2 時,收據應指出熱點所在的原始碼檔與行號,且標明這層的編譯模式與 L0 不同、數字不可互比 [manual:注入 bindDelayMs 那次指到忙等那一行;2026-10-23 s02 指到第 41 行(加開關後行號下移)通過]
- [S5] 當 L1 主嫌是等待 binder 或鎖時,skill 應指示留在 L1 追喚醒鏈,不得往 L2 [manual:注入等鎖那次走一次;2026-10-23 s03 通過]
- [S6] 當專案沒有 L3 的保存裁定時,skill 應指示停在 L2 並記 `[GAP] L3 未授權`,不得錄記憶體快照 [manual:注入配置型退步走一次,收據停在 L2 並有該 GAP;2026-10-23 s05 通過]
- [S9] 當專案有人裁的 L3 授權、L2 熱點落在配置記憶體時,收據應指出配置經手最多的 App 函式,以及留住記憶體的類別與欄位 [manual:注入配置型退步、授權後走一次;2026-10-23 s05 指到 churn 與 MainActivity.retained 通過]
- [S7] 收據應能讓沒脈絡的 Agent 只靠收據與原始檔,用 `rerun.sh` 重跑 L1 的核心查詢並得到 expect 值 [manual:派乾淨 Agent 只給收據目錄重跑]
- [S10] 收據的重跑腳本(scripts/templates/android-receipt-rerun.sh)在收據本身寫錯時應回 2 並在 stderr 說原因,格式全對、比對相符時應回 0,不得空轉 [test:t_android_evidence_rerun_refuses_empty]
- [S8] 當派一個沒脈絡的 Agent 只拿 Trace 與 skill(目錄改中性名)分析注入退步時,它應走到 L2 並指出注入的那一行 [manual:盲測一次,比對答案]

## 四組驗證(2026-10-23,SM-X710、Android 16)

小測試 App 加了兩種注入(macrobench-lab 138ae62),五組結果目錄用中性名稱 s01–s05,哪組注入什麼只記在答案檔。派一個沒參與這段對話的 Agent 只照 skill 做,四組的 L0、L1 判斷寫完才准讀 App 原始碼:

| 組 | 注入 | 預期 | Agent 的結果 |
|---|---|---|---|
| s02 | 每列忙等 8ms | L2 指到忙等那行 | L2:`MainActivity.kt:41` `busyWait(bindDelayMs)` 85.72% |
| s03 | 每列等背景執行緒抓著的鎖 | 停在 L1、追到持鎖者 | 停在 L1:obtainView 期間只有 10.5% 在跑,鎖等待 122 次 481.8ms,持鎖的 `lab-lock-holder` 等鎖時在睡 |
| s04 | 每列配置 64KB | L0 沒退步就停 | 停在 L0:0 項變慢 |
| s05 | 每列配置 1MB | 往 L3、未授權停在 L2 | L2(DWARF 補錄)指到 `churn` 與第 72 行 `retained.add(ByteArray(128))`;記 `[GAP] L3 未授權` |

- 四份收據的 `rerun.sh` 全部回 0(新範本重跑 45 項比對全相符)。
- Agent 回報 13 條 skill 摩擦,全部改進 skill;最重要的兩條:舊 `rerun.sh` 範本把同 session 的 SELECT 一起重放會被 trace_processor 拒絕(改成只重放 `requires` 鏈),以及 fp/DWARF 要依熱點切換。
- 一條留給人裁,見下一行。
- 同日 Enzo 裁「記憶體先試查一下」(只限實驗室 App、檔案留本機),s05 補跑 L3:Java 配置取樣 10 秒約 267MB、99.9% 經 `churn`;物件快照指到 `MainActivity.retained` 留住約 25MB。只到函式與欄位,沒有行號。

REVISIT:2026-11-06 frameOverrunMs P50 在 SM-X710 120Hz 因緩衝深度兩群跳動(s05 只因它報退步,基準各輪本來就在 -1 與 -3.5 間跳),請 Enzo 裁 lumos macrobench 要不要把 frameOverrunMs P50 降成只列出;macrobench 分支推上去之後再改

## 端到端演練:測試專案接上 Lumos(2026-10-23)

macrobench-lab 用這條分支的工具組接上 Lumos(`LUMOS_HOME` 指工作樹、`--no-pull`;接完要把全域設定重同步回正式安裝,見下方坑),走完一次「合約綁流程測試 → 埋錯 → 系統點名要重測 → 照 skill 排查 → 修 → 重測 → 更新驗收」:

- 綁定:清單滑動寫成 `★INVARIANT★` 綁 `bench:scrollList`;綁定測試閘從改動範圍找到合約、在平板上真跑(約 120 秒,預設 180 秒上限沒多少餘裕)。兩輪獨立審計抓到測試只滑不查,補成「每次滑完最大列號要變大」並實機改壞驗紅;文字透明這型記成殘留。
- 觸發:加識別碼的新功能讓 CPU P90 4.2→9.3ms;綁定測試閘重量(流程綠、兩條門檻沒達並印合約)、回頭重讀點名「效能達標」那行、`lumos stale --candidate --match getView` 列出驗收紀錄。
- 排查:沒脈絡的 Agent 照 skill L0→L1→L2,指到 `MainActivity.kt:49`(呼叫識別碼那行)84%;修成查預先算好的表,重測兩條門檻達標;舊驗收紀錄標 superseded、新開一篇。它違反一次禁讀(提交被擋後看了 HEAD 標題),已在根因定位之後。
- 坑:`lumos init` 會把全域 Claude 外掛來源與 hooks 指到 `LUMOS_HOME`,影響這台機器所有會談,試完要用正式安裝 `lumos install --force` 重同步。
- 坑:綁定測試閘在平台的 root 底下執行 `run_cmd`,腳本路徑要相對平台目錄。
- 排查 Agent 回報 12 條 skill 摩擦,10 條已改進 skill;兩條要改程式,見下面兩行。

- 同日已處理:基準檔改成記下每個情境的來源結果檔與雜湊(見 [[Projects/Macrobenchmark驗收門檻_計劃]] S9),L1 照來源去 artifacts 找那次的 Trace。
- 同日已處理:「每支檔有家」本來就有專案層忽略清單(`.lumos/config.json` 的 `node_home.ignore`),收據目錄加一行 `.lumos/receipts/*` 就不需要家;skill〈收尾〉改成指示這一步,不另加程式。

## 第零階段試跑(2026-10-23,SM-X710、Android 16)

細節與數字在 [[Verification/2026-10-23_Android驗證收據第零階段試跑]];這裡只留影響設計的結論。

- 官方 triage 能從 Trace 定位到注入的瓶頸(主執行緒 `obtainView` 每次多約 7.8ms、全在 CPU 上)。
- 盲測:沒脈絡的 Agent 只拿 Trace 與官方 skill,判出「`obtainView` 裡、`calculateBounds` 之前一段約 8ms 的 Java 迴圈,在等時鐘走滿而不是在做事」;函式內哪一行標 [GAP](沒有呼叫堆疊)。它注意到目錄名 `bind8` 與答案吻合,自稱沒當證據,但排除不了。
- 收據稽核:沒脈絡的 Agent 只靠收據重現了全部核心數字,但要自己補腳本;缺口見上一節。
- 實驗室 App 的滑動基準原本第二輪起清單停在底部、沒有真的捲(Trace 證實),已修(macrobench-lab a9848d3)。
- 行號層實測見第二條 WHY。

## 不做

- Lumos 核心不加指令、不呼叫 adb 或任何分析工具。
- 不自動上傳任何 Trace、perf.data 或記憶體檔;原始檔只放消費專案的 `.lumos/artifacts/`(已在忽略清單)。
- 不把任何一層的毫秒數字當推送閘。

## 實務隱患

已排除:金流:只讀本機量測資料,不碰交易
已排除:對外送出:工具下載只從釘版本的官方網址;不上傳資料
已排除:不可逆:`setprop debug.generate-debug-info` 與 `cmd package compile` 只動測試裝置上的 App 編譯狀態,`setprop` 用空值或重開機還原,編譯狀態用 `cmd package compile --reset <套件>` 還原(2026-10-23 在 SM-X710 的 help 確認有這個旗標);skill 要在 L2 結束時還原
已排除:守衛面:不改任何推送前檢查或閘

## 回退

拿掉 `skills/lumos-android-evidence/`;消費專案的收據目錄留著也不影響其他指令。
