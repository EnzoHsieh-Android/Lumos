---
type: project
status: doing
created: 2026-10-23
updated: 2026-10-23
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
related:
  - "[[Projects/Macrobenchmark退步提醒_計劃]]"
  - "[[Projects/後端工程提問與證據擴充_計劃]]"
  - "[[Projects/併發與效能表態要合約背書_計劃]]"
  - "[[Systems/guard-kill]]"
---
# Android診斷證據接入_調研

白話:想讓 AI 拿得到 Android 的效能、記憶體、ANR 與正式環境品質資料,並把「這一版功能在講清楚的測試條件下真的跑過、符合驗收條件」的證據接回 Lumos。本篇是 Enzo 2026-10-23 帶進來的調研稿整理,是接入規格草案,不代表 Lumos 已經有這些能力。落地併進 [[Projects/Macrobenchmark退步提醒_計劃]](Enzo 2026-10-23 裁「接手舊計劃一起做」)。

WHY:不由 Lumos 重做 Android Profiler,直接用 Google 官方的 android-profiler Agent Skill 與 Perfetto 工具 [出處:2026-10-23 Enzo 帶進的調研稿] [因:官方 skill 已能指引 Agent 錄 System Trace、Java/Native Heap、CPU Callstack,用 trace_processor 與 PerfettoSQL 分析,並把結論分成量測、推論、資料缺口] [不選:Lumos 自己解析 Perfetto 檔或教 AI 看 Profiler(重造輪子)]
WHY:第一版不新增通用的證據執行指令,只做轉接 skill 加手寫收據 [出處:[[Projects/後端工程提問與證據擴充_計劃]] 決策 d6] [因:核心 CLI 同時管子程序、權限、遮蔽、原始檔保存、作廢與交付判斷,兩輪設計審證實會長成第二套測試框架] [不選:lumos evidence 執行器]
WHY:毫秒數字只當驗證數據,不當推送硬閘;只有人明確裁定某裝置某情境的門檻,才算合約 [出處:[[Projects/併發與效能表態要合約背書_計劃]] 2026-10-01 裁定] [因:數字隨裝置、溫度、建置浮動]
PRIOR-ART: 官方 android-profiler skill https://developer.android.com/agents/skills/profilers/android-profiler/skill (調研時看的版本 95ea931a1ad8f9b2be132ae0cfb2aad964d71118,會更新,正式接入要釘版本重驗);Android Performance Analyzer 的 AI 分析 https://developer.android.com/android-performance-analyzer/analyze/ai ;Macrobenchmark 結果與指標 https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview#benchmark-results 、https://developer.android.com/topic/performance/benchmarking/macrobenchmark-metrics ;Trace Processor https://perfetto.dev/docs/reference/trace-processor-cli 、Batch Trace Processor https://perfetto.dev/docs/analysis/batch-trace-processor 、Trace Summary https://perfetto.dev/docs/analysis/trace-summary 。裁定:借用,Lumos 不加依賴。
RETIRE-IF: 試跑後另一個不知道對話脈絡的 Agent 只靠節點、收據、報告仍重跑不出核心查詢,或連續兩個試行案例都覺得收據比直接讀測試輸出更難用,就撤掉收據格式、回到只綁 [test:]。

## 核心定位:合約的一次 E2E 驗證收據

既有合約鏈是「功能節點的 ★INVARIANT★ 綁一支 E2E 測試」。接入後要補的是「這一次驗證」留下了什麼:

- 測試前提:App 提交與版本、裝置、資料、帳號、Feature Flag。
- 執行紀錄:跑了哪個 flow、起訖時間、結果。
- 行為證據:畫面狀態、UI tree、API 或資料狀態、Log。
- 診斷證據:Perfetto Trace、Heap、CPU、記憶體、畫格數據。
- 判定依據:合約要求跟實際結果怎麼對上。
- 檔案身分:位置、SHA-256、大小、工具版本、資料缺口。
- 重驗條件:改到什麼就要重跑。

三個角色不能合併:合約是正確答案的來源(來自需求或人裁,不能從程式或當次數字反推);E2E 負責把情境做出來;診斷工具負責留下現場。「這次量到 P95 18ms」只是一筆數據,不是新合約。

- 行為 E2E(只產生一張訂單、畫面顯示成功)可以直接決定 pass/fail。
- 診斷數據(GC 次數、P95、Native Heap)先用來留現場與比較,一次數字不能擋交付。
- 需求本身有時間或資源上限時,要同時鎖定裝置、build、fixture、操作流程、warmup 與容許誤差,否則兩次數字不能比。
- 通過與失敗都留收據;裝置斷線、Trace 掉資料、測試帳號失效這類環境失敗標「無法判定」,不算失敗也不算通過。
- 宣稱某支 E2E 守得住合約,要做故障敏感度驗證:暫時破壞它保護的行為,確認 E2E 會紅(沿用 [[Systems/guard-kill]] 的想法)。

## 拿得到哪些資料(本機或測試裝置)

| 目的 | 首選方式 | 限制 |
|---|---|---|
| 卡頓、ANR、執行緒阻塞 | Perfetto System Trace + PerfettoSQL | 看得到什麼取決於錄了哪些 data source |
| 可重複的啟動與畫面效能 | Macrobenchmark(JSON + 每輪一份 Trace) | 要實機;有量測雜訊 |
| 單段熱路徑 | Microbenchmark | 不代表完整使用者流程 |
| Java/Kotlin 物件保留 | Perfetto `android.java_hprof` | 只有引用圖,沒有欄位內容,不能給 AHAT 開 |
| 傳統洩漏分析 | `adb shell am dumpheap` 的 `.hprof` + Shark/AHAT | 可能含個資;檔案大 |
| Native 配置 | heapprofd(`heap_profile`) | 抽樣;沒 symbols 只能定位到 `.so` 與位址;跟 RSS 不是同一個數 |
| 快速分流 | `dumpsys meminfo`、`dumpsys gfxinfo <pkg> framestats` | 只有概況或近期資料 |
| Crash/ANR 現場 | Logcat、ApplicationExitInfo | 循環緩衝會覆蓋,`null` 不代表沒發生 |

- Macrobenchmark 在 debuggable、非 profileable、模擬器、低電量時會報錯,不會悄悄給出看似可信的數字。畫面驗收看 `frameOverrunMs`(正數通常是看得見的卡頓)、`frameDurationCpuMs`,看百分位分布不看平均。
- `trace_processor query <trace> --format csv "<SQL>"` 可直接出 CSV,也能開常駐 session、跑官方 metrics、批次比較多份 Trace。Lumos 不讀數百 MB 的 Trace,只保存原始檔身分、實際跑過的 SQL、查詢結果與報告。

## 正式環境(第四階段才碰,唯讀)

- ProfilingManager(API 35 起):App 請系統錄 Trace、Heap、Stack Sampling;有 rate limit、不保證每次執行,只適合抓罕見問題現場。標 `source: production-profiling-manager`、`redacted: true`、`sampling: system-rate-limited`;沒收到結果不能推論問題沒發生。
- Crashlytics 匯出 BigQuery:可按版本、裝置、Flag 分組看修正後是否下降;issue 分組只是線索,不是業務正確性判準。
- Play Developer Reporting API:crash/ANR rate、slow rendering/start、LMK 等趨勢,不是固定場景的驗收。

## 沒有低階實機時

優先序:團隊共用的代表性實機 → Firebase Test Lab 實體裝置 → 一般實機做相對比較 → 模擬器只驗功能與流程。模擬器綠燈不能寫成「低階實機已驗證」,要留「低階裝置未驗證」。

## 收據格式草案(manifest)

原始 Trace、HPROF、Logcat、正式環境匯出不進 Git;manifest 與去敏後的報告可以進版控。

```json
{
  "schema": "lumos-android-evidence/v1",
  "run_id": "android-20261023T103000Z-a1b2c3d4",
  "purpose": "compare",
  "question": "結帳頁動畫修改後是否增加可見卡頓",
  "source": "macrobenchmark",
  "project": {"git_commit": "<full-sha>", "dirty": false, "package": "com.example.app",
              "version_code": 123, "build_type": "release-profileable"},
  "device": {"model": "Pixel 6a", "api": 35, "build_fingerprint": "<fingerprint>",
             "physical": true, "battery_percent": 82, "thermal_status": "none"},
  "scenario": {"id": "checkout-scroll-v2", "iterations": 10, "preconditions": ["已登入", "固定測試資料"],
               "baseline_run_id": "android-20261022T091000Z-11223344"},
  "tooling": {"android_profiler_skill_commit": "95ea931a…", "trace_processor_version": "<version>",
              "capture_config_sha256": "<sha256>", "queries_sha256": "<sha256>"},
  "artifacts": [{"kind": "perfetto-trace", "path": ".lumos/artifacts/android/<run-id>/iteration-01.perfetto-trace",
                 "sha256": "<sha256>", "bytes": 12345678, "committed": false, "redacted": false}],
  "result": {"state": "measured", "report": "perfetto_analysis_report.md",
             "gaps": ["未涵蓋 API 29 裝置"], "symbolization": "complete"}
}
```

manifest 要答得出:哪一版程式(完整 SHA、是否 dirty)、哪個 App 建置(profileable/debuggable)、哪台裝置(實體或模擬器)、哪個情境(資料、步驟、iteration、warmup)、哪套工具與設定(版本、capture config 與 SQL 的雜湊)、哪個 baseline(不能只寫「前版」)、哪些缺口、原始檔在哪與雜湊。

報告沿用官方 skill 的證據標籤:`[SQL]` 指得回 SQL、Trace 或 JSON 的數字;`[INFERRED]` 從多筆量測推的可能原因;`[GAP]` 目前資料答不了;另加 `[DECISION]` 人裁的接受標準。(2026-10-23 訂正:原稿寫 `[MEASURED]`,官方 skill 95ea931a 實際用 `[SQL]`。)

## 寫回規則

| 實際情況 | 寫回 | 不可以寫成 |
|---|---|---|
| 相同條件重跑且達到已裁定標準 | Verification pass | 「AI 認為已優化」 |
| 指標退化或 Trace 證明有問題 | 開或更新 Issue | 為了讓驗證綠而放寬標準 |
| 缺 baseline、裝置不等價、Trace 掉資料 | Verification pending 或不寫 pass | 「沒有發現問題」 |
| 原本成立的裝置、版本、情境已變 | Verification stale | 沿用舊數字 |
| 只有 Crashlytics/Vitals 趨勢改善 | 正式環境觀測證據 | 固定場景效能驗收已通過 |
| 只有模擬器結果 | 功能或初篩證據 | 低階實機已驗證 |
| Native profile 缺 symbols | 元件層級嫌疑 + GAP | 已定位第三方 SDK 內部函式 |

可以自動檢查的:指令真的執行成功、檔案存在、雜湊相符、Trace 沒掉事件、SQL 真的跑成功、baseline 與 candidate 的裝置與情境相符、必填欄位與缺口誠實填寫。不該直接當推送硬閘的:單次 P95/P99、跨裝置數字、正式環境短期沒新事件、AI 推論的根因、沒 symbols 時的函式級判斷。

## 安全與隱私

1. HPROF 可能含 token、密碼、使用者資料,不提交、不上傳公共模型。
2. 手動錄的 Perfetto Trace 可能含其他 Process 資訊;正式環境優先用會遮蔽其他 App 的 ProfilingManager。
3. Logcat、Crashlytics 的 Custom Key 與 Breadcrumb 可能帶個資,匯入前遮蔽。
4. 連 Crashlytics BigQuery、Play Reporting API、Test Lab 用唯讀最小權限帳號。
5. 原始檔放 `.lumos/artifacts/` 並加進忽略清單;要團隊共享就用有保存期限與存取控制的物件儲存。
6. Shark 的 `strip-hprof` 降低 primitive array 外洩風險,但「已 strip」不等於已證明沒有敏感資料。
7. 原始資料的刪除、保留期限與對外上傳由專案另行裁定,不由 Agent 自己決定。

## 分階段

- **第零階段 外掛試跑,不改 Lumos 核心**:裝官方 skill;選一個可重現的卡頓情境;完成 Trace 擷取、SQL 分析與 baseline/candidate 比較;人工寫一份驗證紀錄,看 manifest 欄位夠不夠。驗收:一個不知道對話脈絡的 Agent 只靠節點、manifest、報告與原始檔,能重跑核心 SQL 並指出資料缺口。
- **第一階段 轉接 skill**(`lumos-android-evidence`):檢查 adb、裝置、建置、官方 skill 與 trace processor;依目的選工具;產 manifest、雜湊與報告骨架;導向驗證紀錄、Issue 或 pending。不自己實作 profiler、不解析 Perfetto protobuf、不把毫秒門檻寫死、不自動上傳。
- **第二階段 唯讀檢查指令**:只有試跑證明人工寫回容易出錯時才做,例如檢查 manifest、比兩份 manifest、把 manifest 連到計劃與節點;只檢查與連結,不錄製、不執行第三方指令、不替人決定標準。
- **第三階段 CI 與裝置矩陣**:固定實體裝置定期跑 Macrobenchmark;PR 只檢查基準跑得起來、檔案完整;趨勢退化先提醒。
- **第四階段 正式環境唯讀連接**:Crashlytics BigQuery、Play Reporting API、ProfilingManager(要另做產品、隱私、成本與採樣裁定)。

## 要人裁定的事與目前答案(2026-10-23)

| 題目 | 目前答案 |
|---|---|
| 第一個消費專案 | Citrus_KDS(沿用 [[Projects/Macrobenchmark退步提醒_計劃]] 決策 d2) |
| 第一個試行情境 | KDS 主頁訂單清單滑動與冷啟動,用假 POS 伺服器餵固定 60 張訂單(KDS 那邊已寫好兩支基準) |
| 原始檔只留本機或接物件儲存 | 待人裁;裁定前一律只留本機 |
| 能不能裝官方 skill 與它下載的 Perfetto 工具 | 可以(Enzo 2026-10-23),要釘版本;等評測實驗跑完、機器空出來再裝 |
| 能不能用 Firebase Test Lab、費用誰出 | 待人裁;裁定前不用 |
| HPROF、Trace、Log 的保存期限與可見人員 | 待人裁;裁定前不錄 HPROF |
| 第一版只做轉接 skill 還是加 CLI | 照第一、二階段的順序:先 skill,試跑證明需要才加指令 |

## 調研邊界

- 官方工具、格式與程式化取得路徑確認存在。
- 第零階段已在實驗室 App 與實體平板跑完(不是 KDS:KDS 的基準在 Android 16 上跑不起來,見 [[Projects/Macrobenchmark退步提醒_計劃]]〈實機端到端〉),結果見 [[Verification/2026-10-23_Android驗證收據第零階段試跑]];第一階段改成逐層診斷,見 [[Projects/Android逐層診斷_計劃]]。
- Firebase Test Lab 能不能讓所選裝置與情境完整產生 Macrobenchmark 檔案,本篇沒驗。
- 消費專案有沒有 LeakCanary、Crashlytics、Play API 或 ProfilingManager,本篇沒查。
- 本篇沒有宣稱任何 AI 分析結果可以取代產品、資安、隱私或發布的人工作業。
REVISIT:2026-12-21 KDS 實機收據試跑做了沒;沒做就判延後或撤案
