severity: minor

## F1 英文收集框多了「per run」,中文版沒有對應
severity: minor
blocking: 否
引句:「dumpsys · Perfetto · logcat per run」
出處:file: `assets/readme-diagrams/generate.py:17`(同一行的中文是「dumpsys、Perfetto、logcat 收資料」)
說明:中英兩版工具名稱一致,但英文多了「per run」,中文版沒有。這個框的標題是「Memory & stability run」,整個框本來就是一次收集。收集腳本也不是每個 run 都三樣一起收,例如 `java_heap_dump` 只在宣告測試資料時才用。「per run」讓人讀成每一輪各跑一次,這是措辭精度問題,不是寫錯工具。
建議:英文改成「dumpsys · Perfetto · logcat to collect data」,或兩邊都拿掉「per run」。替代文字(desc)已寫成「gathers data with dumpsys, Perfetto, and logcat」,圖上改成這個說法就一致了。

## 逐句核對表
| 位置 | 圖上寫的 | 出處 | 判定 |
|---|---|---|---|
| 收集框(中/英) | dumpsys、Perfetto、logcat | `android-stability-collect.sh` 實際呼叫 `dumpsys activity exit-info`、`dumpsys meminfo`、`perfetto --background`、`adb logcat`;README 章 332–337 行同一套說法 | 一致(英文「per run」見 F1) |
| L1 副標 | Perfetto + trace_processor,照 Google skill 讀 | SKILL.md 14–15 行(官方 skill 與 `trace_processor` Perfetto v57.2)、README 326 行 | 一致 |
| L2 副標 | simpleperf(Android NDK / NDK 附)指到檔案與行號 | SKILL.md 17 行(NDK 28.2.13676358 的 simpleperf)與 95–97 行的 annotate、README 326 行 | 一致 |
| L3 副標 | heap_profile、java_heap_dump;要先同意只用測試資料 | SKILL.md 16、114、126 行,README 324、326 行;L3 要人裁、`stability.test_data` 宣告才往下 | 一致 |
| desc 英文 | L1 用 trace_processor 讀 Perfetto 錄製、照 android-profiler skill | SKILL.md 14–15 行 | 一致 |
| desc 英文 | L2 simpleperf 來自 Android NDK | SKILL.md 17 行 | 一致 |
| desc 英文 | L3 用 Perfetto 的 heap_profile 與 java_heap_dump,先經人同意只用測試資料 | SKILL.md 16 行、README 324 行 | 一致 |
| desc 英文 | 記憶體與穩定性收集用 dumpsys、Perfetto、logcat | 收集腳本 | 一致 |
| desc 中文 | 與英文逐句對應:trace_processor 讀 Perfetto、NDK 附的 simpleperf、Perfetto 附的 heap_profile 與 java_heap_dump、收集三樣工具 | 同上 | 一致,中英對應 |
| 知識筆記 2026-10-25 新增段 | L1/L2/L3 工具與收集框的說法,對上 README「各層用的工具一覽」 | README.md 326 行、README.en.md 326 行 | 一致 |

其他核對結果:
- 我跑了 `python3 assets/readme-diagrams/generate.py --check`,輸出「24 bilingual SVGs: validated, reproducible, static fallback and reveal order checked」,rc=0。
- 我用無頭 Chrome 把 `assets/android-e2e-en.svg` 與 `assets/android-e2e-zh.svg` 各截一張圖看。所有新副標、收集框文字都在框內,沒有被擠出框或和右側徽章重疊。英文 L1「Perfetto + trace_processor, read via Google's skill」最長,離徽章仍有餘裕。
- 截圖暫存在 `/tmp/lumos-seat-work/code-readme-android-diagram-tools/單審-sonnet/`,是我這個會談建的,收尾時會刪。

總結:全篇最高為 minor
