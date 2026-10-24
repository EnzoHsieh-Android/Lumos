severity: minor

整體判斷:diff 新增的工具名稱都有出處,沒有寫錯工具,也沒有誇大。中英兩版逐句對應。只剩兩處措辭精度問題。

## F1 「開關前後各掃/各拍」的「前」其實是暖機之後
severity: minor
blocking: 否
引句:「用 Android 內建的 `dumpsys meminfo --unreachable`，開關前後各掃一次」
出處:``scripts/templates/android-stability-collect.sh: `scripts/templates/android-stability-collect.sh:471-475` ``(先跑暖機驅動,再掃「前」那次與拍「前」那份快照)。計劃第 70-73 行也寫「暖機後」。
問題:這句同時出現在第一、二項:第一項掃描與第二項快照的「前」,都是暖機 W 輪之後、量測 N 輪之前。中文「開關前後」容易讓人以為是第一次開畫面之前。英文版 "before and after" 有同樣問題。
建議改法:改成「暖機之後、量測 N 輪之後各掃一次」,第二項的快照同樣改。中英兩版一起改。

## F2 驅動工具寫成只有 UI Automator,漏了驅動是設定檔指令這件事
severity: minor
blocking: 否
引句:「專案自己寫的操作測試（現在用 Android 的 UI Automator，之後換成 Maestro）」
出處:``docs/lumos-toolchain-knowledge/Projects/Android記憶體與穩定性驗收_計劃.md: `docs/lumos-toolchain-knowledge/Projects/Android記憶體與穩定性驗收_計劃.md:21` ``與第 67 行,設定檔 `stability.driver` 是任意指令。``scripts/templates/android-stability-collect.sh: `scripts/templates/android-stability-collect.sh:214-226` ``,只對 UI Automator 的 `INSTRUMENTATION_` 輸出做特別檢查。
問題:
1. 「現在是 UI Automator、子案二換 Maestro」與計劃第 21 行一致,不算錯。
2. 但「之後換成 Maestro」是計劃中的未來事項,且 REVISIT:2027-01-31 還沒實測 Maestro 的 repeat 變數。README 把它寫成既定事實,略有承諾過頭。
3. 驅動本身只是設定檔裡的一條指令。
建議改法:改成「現在支援 Android 的 UI Automator,Maestro 規劃之後接」,或加一句「驅動指令由專案設定檔指定」。

## 逐句核對表

| # | 新增描述(摘要) | 出處 | 判定 |
|---|---|---|---|
| 1 | L3:`heap_profile` 看誰在大量配置 | SKILL.md:114,L3 第 1 步 | 一致 |
| 2 | L3:`java_heap_dump` 拍快照找誰抓著 | SKILL.md:126,L3 第 2 步 | 一致 |
| 3 | L0 是 Macrobenchmark 加 `lumos macrobench` 判定 | SKILL.md L0 | 一致 |
| 4 | L1 是 Perfetto 紀錄,用 `trace_processor` 照官方 skill 讀 | SKILL.md:15,description | 一致 |
| 5 | L2 是 NDK 附的 simpleperf | SKILL.md:17 | 一致 |
| 6 | L3 是 Perfetto 的 `heap_profile` 與 `java_heap_dump` | SKILL.md:16 | 一致 |
| 7 | 操作測試現在用 UI Automator | 計劃:21,collect.sh:222-225 | 一致 |
| 8 | 之後換成 Maestro | 計劃:21 | 一致,但是未來規劃(見 F2) |
| 9 | 原生記憶體用 `dumpsys meminfo --unreachable`,前後各掃一次 | collect.sh:191-192,473 | 工具一致,「前」的措辭見 F1 |
| 10 | 物件增長用 `java_heap_dump` 兩份快照,再用 `trace_processor` 數類別 | collect.sh:275,248;heap-classes.sql | 工具一致,「前」的措辭見 F1 |
| 11 | 只在宣告測試資料後才拍快照 | collect.sh:379-381,475;計劃:29 | 一致 |
| 12 | 指定物件剩幾個,來自第二份快照 | collect.sh 的 after 快照、計劃 `instances` 檢查 | 一致 |
| 13 | 最高記憶體:Perfetto 全程錄製,`trace_processor` 算最大值 | collect.sh:303-306,cycle.sql 的 `peak_anon_swap_kb` | 一致 |
| 14 | 閃退:`dumpsys activity exit-info` 讀前後兩次 | collect.sh:185,467,477 | 一致 |
| 15 | 閃退:並比對行程有沒有換過 | collect.sh 的 `pids` 讀三次,計劃:31 | 一致 |
| 16 | StrictMode:`adb logcat` 收這個 App 的日誌,只留違規行 | collect.sh:406-411,443(`--pid`、`StrictMode policy violation`) | 一致 |
| 17 | 凍結:同一份 Perfetto 錄製的每幀時間 | cycle.sql(`actual_frame_timeline_slice` 或 `Choreographer#doFrame`) | 一致 |
| 18 | 中英兩版 | 逐句對照 | 對應,無遺漏、無多寫 |

總結:全篇最高為 minor
