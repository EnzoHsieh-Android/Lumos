preflight-4: ran

# android記憶體與穩定性驗收 r1 前掃(派席之前)

前掃由一個 sonnet 代理做(固定清單四項加舊否決比對);命中的已修進計劃真檔,不算 findings。

## 舊否決比對
- 撞到 Projects/Android逐層診斷_計劃 否決的「每次都錄 Trace、CPU 取樣與記憶體」:計劃的實例數檢查要錄 Java 堆積快照。2026-10-24 問 Enzo「上次的理由現在還成立嗎」,選「照調和做:N 輪後錄一次」;計劃改成只在洩漏情境、門檻檔宣告了類別時,N 輪量完才錄一份,舊否決照留、這條記成例外並寫理由。
- 撞到 Projects/Android逐層診斷_計劃 的 S6(沒有保存裁定時停在 L2):Enzo 2026-10-24 已選保存規則,這是翻案;計劃加一節〈這次要改到的地方〉列出 S6 與 skill 兩處要改。

## 核心裁定改動(問人後才改)
- 成對方法靜態提醒(原 S13):前掃讀程式發現代碼審題目是寫死的表,沒有「讀專案設定出題」的路,等於新機制;它也是動到守衛面的唯一來源。2026-10-24 問 Enzo,選「移到後續另案」;原 S13 拿掉、改成 REVISIT 2027-01-31,實務隱患的守衛面改回已排除。

## 語意類命中(改前 → 改後)
- 「判定沿用 lumos macrobench 與門檻檔」→ 現行門檻每條只收一個有限的 max 或 min(scripts/lumos 的 MACROBENCH_THRESHOLD_REQUIRED 與其後檢查),趨勢、實例數、官方底線套不上;改成「門檻加選填 kind 欄位,沒寫 kind 照舊」,並加 S13 釘相容性。
- 「收據重跑腳本能從追蹤檔重算」→ 重跑腳本拿輸出第一欄的字串當比對鍵;改成查詢第一欄是輪次字串(S10 寫明)。
- 「原始檔本機保留 7 天後刪」與「收據重跑讀追蹤檔」互相打架 → 改成只有快照 7 天後刪,追蹤檔不受限;收據裡的實例數只留結果不重算。
- 「沒過就接 L3」→ 逐層診斷的 L3 原本是 L0→L1→L2 之後;改成明寫記憶體檢查沒過直接進 L3、凍結幀照原本 L1。

## 其他前掃命中(直接修)
- 未定義的詞:做法丙、支配樹、匿名常駐記憶體、Java 堆積怎麼取樣、實驗室是哪個專案、收集結果的格式 → 加〈用到的詞〉段與結果檔欄位清單。
- 範圍自相矛盾:「四種」與「六種」、資料流判定步驟漏了 StrictMode、快照何時錄兩處講法不同 → 統一。
- 容差規則沒沿用家節點既有的「百分比與絕對值取大」→ 寫明沿用,S3 補「第一輪接近 0」的案例。
- 新範本要帶 SPDX 檔頭 → S12 寫明。

# r1 收貨(四席交回之後)

審材 r1-snapshot.md(106 行,sha256 6fd5e31a…,LUMOS-SPEC 3fcb762d);四席全新 sonnet:通才、邊界可執行、整合、架構對齊。四席交回後才一起從逐字稿存檔。
格式:通才席檔級寫 major、內文有 blocker,另有兩行總結;退回該席自己改檔級與總結,之後再退回補引句行(原報告沒有引句行)。整合席原報告沒有引句行,退回補;`severity: major ⚠` 用 report-normalize --write 純格式拆行。四份 quote-check 全錨。

## 編排者重現(收貨後做,實驗與調研)

- 每輪結束值抖動(B1、I9、G4):實驗室 ui-c1-unstable-ft-v3 五份追蹤檔,只看 com.example.mblab 的 Heap size (KB) 最後一筆:15584、13084、28292、21400、12368 → HIT。
- 冷啟動殺行程(G1、I6、B11):讀 macrobench-lab 的 LabBenchmarks.kt,滑動基準註解寫 COLD 會在量測前殺 App → HIT。
- 快照時機(G2、I6):SM-X710 對 profileable 的基準建置下 `am dumpheap -g` → SecurityException: Process not debuggable;Perfetto java_hprof 同一個 App 錄得到 15 MB、trace_processor 數得出類別實例數 → HIT(原設計做不出來,改用 java_hprof)。
- 原生減法(G3、I4):實驗室暫時分支加假 SDK(關畫面沒呼叫 release 時漏 2 MB 原生記憶體),同一行程開關 5 輪:沒 release 時 `dumpsys meminfo --unreachable` 回 10485760 位元組 5 塊、Native Heap 7036→16104 KB;有 release 時 0 位元組、Native Heap 4660–9448 KB 有升有降 → HIT(改用 unreachable 當主判定,Native Heap 只回報)。暫時分支做完已刪。
- 結束紀錄時鐘與全機(G9、B4):`dumpsys activity exit-info com.example.mblab` 只列這個套件、timestamp 是本地時間不帶時區;`am crash` 兩秒後新紀錄已在第一筆 → HIT(改成前後比對)。
- 業界做法調研(Enzo 2026-10-24「也可以上網搜業界做法」):LeakCanary 3.0 堆積增長偵測、libmemunreachable、AppExitInfoTracker 原始碼;結果寫進計劃 PRIOR-ART 與 WHY。

## 逐條去向

全部 42 條折入計劃(r2 版),沒有放行、沒有不成立。

| id | 席 | 嚴重度 | 一句 | 去向 |
|---|---|---|---|---|
| G1 | 通才 | blocker | 沒規定不殺行程 | 折:驅動同一行程、收集腳本排順序,不用 measureRepeated |
| G2 | 通才 | blocker | N 輪後快照跑不起來 | 折:收集腳本從主機錄 java_hprof(實測可錄) |
| G3 | 通才 | major | 原生減法會算錯 | 折:改 unreachable 主判定 |
| G4 | 通才 | major | 容差單位錯置 | 折:趨勢判定拿掉,改增長比對與 unreachable,不用毫秒容差 |
| G5 | 通才 | major | 峰值基準沒定義 | 折:基準那層移到統計化計劃,這裡只做官方底線 |
| G6 | 通才 | major | 分級表矛盾、MB 對應沒定 | 折:寫官方 MB 區間、含下界不含上界 |
| G7 | 通才 | minor | 輸出形狀與印字不相容 | 折:輸出每筆帶 check 與明細,印字照 check 分支 |
| G8 | 通才 | minor | 沒 macrobench.json 早退 | 折:S14 |
| G9 | 通才 | major | 時間過濾的時鐘 | 折:前後比對 |
| G10 | 通才 | major | 收不到與沒事分不出 | 折:每個來源帶 status,S11 |
| G11 | 通才 | major | 7 天刪沒有執行者 | 折:收集腳本每次開跑先刪,S15 |
| G12 | 通才 | minor | 凍結幀與阻塞來源 | 折:幀時間線或 doFrame、最上層區段、暖機不錄 |
| G13 | 通才 | minor | 輪次鍵從哪來 | 折:追蹤檔一份、鍵 cycle;空值 -1 |
| G14 | 通才 | minor | R8 混淆與 +1 | 折:代價寫 keep 規則;沒有類別算 0;門檻可設 1 |
| B1 | 邊界可執行 | major | 嚴格單調抓不到抖動中的洩漏 | 折:同 G4 |
| B2 | 邊界可執行 | major | 毫秒容差套到 KB | 折:同 G4 |
| B3 | 邊界可執行 | major | 輪數少、缺輪、null | 折:不再逐輪判;兩份快照與一次掃描,缺了 status 不是 ok 就跳過 |
| B4 | 邊界可執行 | major | 時區與全機紀錄 | 折:同 G9,限套件 |
| B5 | 邊界可執行 | major | 空當成沒事、StrictMode 沒開、MemoryLimiter 版本 | 折:status、strictmode 宣告;MemoryLimiter 只是四種之一 |
| B6 | 邊界可執行 | major | 缺席算 0 還是沒量到、混淆 | 折:S3 沒有類別算 0;快照 status 另判;keep 規則 |
| B7 | 邊界可執行 | major | 七種必填欄位、阻塞、峰值 | 折:check 欄位與各自欄位;阻塞併進 frozen |
| B8 | 邊界可執行 | major | 分級表與 MB 區間 | 折:同 G6 |
| B9 | 邊界可執行 | minor | 單位、swap 取樣對齊、0 值 | 折:S9 寫 swap 取之前最近一次;量不到 -1 |
| B10 | 邊界可執行 | minor | 輪次排序 | 折:不再逐輪輸出 |
| B11 | 邊界可執行 | minor | 啟動模式 | 折:同 G1 |
| I1 | 整合 | major | 必填欄位、舊驗證會擋、早退、驗收門檻 S5 | 折:check 欄位只對有寫的條目;S13、S14;改驗收門檻計劃 S5 |
| I2 | 整合 | major | 峰值基準與容差 | 折:同 G5 |
| I3 | 整合 | major | 收據重跑一條查詢一份追蹤檔、NULL | 折:追蹤檔只一份、COALESCE -1 |
| I4 | 整合 | major | 原生減法口徑 | 折:同 G3 |
| I5 | 整合 | major | 分級邊界 | 折:同 G6 |
| I6 | 整合 | major | 量測到收集的交接沒人認領 | 折:收集腳本在主機排全部順序 |
| I7 | 整合 | major | 子案二要重做錄製 | 折:錄製設定做成範本;驅動指令寫在設定 |
| I8 | 整合 | major | 測試資料無法機械判、7 天無執行者 | 折:test_data 宣告、收集腳本刪 |
| I9 | 整合 | major | 嚴格單調太脆 | 折:同 G4 |
| I10 | 整合 | minor | 要改到的地方漏項 | 折:〈這次要改到的地方〉補 about_code、skill 各處、兩份計劃 |
| I11 | 整合 | minor | MemoryUsageMetric 進結果檔被毫秒容差誤報 | 折:不用 MemoryUsageMetric |
| I12 | 整合 | minor | L3 結論不能重跑沒標 | 折:收據標明快照刪除後哪些數字不能重跑 |
| A1 | 架構對齊 | minor | kind 同名多義 | 折:改名 check |
| A2 | 架構對齊 | minor | 有 kind 條目的輸出形狀 | 折:同 G7 |
| A3 | 架構對齊 | minor | --stability 壞檔回傳碼 | 折:S14 回 2 |
| A4 | 架構對齊 | minor | trace_processor 找法 | 折:沿用 TP 環境變數 |
| A5 | 架構對齊 | minor | 家節點「不接裝置」衝突 | 折:負責範圍改寫 |

## 修補因果

r1 首輪,不適用。
