severity: major

我只讀了被審材料和既有檔,沒跑任何指令改東西。以下四問逐問答。

## 問 1 分層與依賴方向

大方向對齊:`lumos` 本體只讀結果檔、不接裝置,adb 與 trace_processor 只在範本腳本裡跑。判定不跨層直呼,既有的 `_macrobench_mode` 也只讀檔(`scripts/lumos:39724`)。

有兩處對不上。

**F1:Java 堆積快照出現第二種錄法。**
- 既有的 skill 第 L3 段第 2 步,用官方 `java_heap_dump -n <套件> -o <檔>.perfetto-trace` 錄快照。這支腳本釘在 Perfetto v57.2 的 tools(`skills/lumos-android-evidence/SKILL.md:15`、`:121`)。
- 本計劃改由收集腳本用自己的 java_hprof 錄製設定來錄。
- 計劃只說了「不用 `am dumpheap`」,沒說為什麼不沿用 `java_heap_dump`。
- 計劃也沒說這兩份錄製設定怎麼保持同一份。
- ⚠ 我沒有展開 `java_heap_dump` 內部的設定,不確定它跟計劃的 java_hprof 設定實質上是不是同一份。若是,把收集腳本改成呼叫它,就不是第二種做法。

severity: major
blocking: 是
引句:「快照用 Perfetto 的 java_hprof」
佐證 file: `skills/lumos-android-evidence/SKILL.md:121`

**F2:「範本腳本才接裝置」的前提與事實不符。**
- 計劃要把家節點負責範圍改成「範本腳本(收集、重跑)才接裝置」。
- 但重跑腳本只呼叫 trace_processor,沒有 adb(`scripts/templates/android-receipt-rerun.sh:58`)。
- 既有的 adb 操作都寫在 skill 的步驟裡,由 AI 執行(`SKILL.md:30`、`:74`、`:84`)。
- 所以收集腳本是第一支會呼叫 adb 的範本,不是沿用既有做法。結構上不算跨層,但計劃用「既有做法」當依據並不成立。

severity: minor
blocking: 否
引句:「範本腳本(收集、重跑)才接裝置」
佐證 file: `scripts/templates/android-receipt-rerun.sh:58`

## 問 2 命名與錯誤處理

對齊的部分:
- 回傳碼 0 / 2 加「擋下:」,與既有一致(`scripts/lumos:39731`、`:39745`)。
- 輸出沿用 `threshold_failures`、`threshold_passed`、`threshold_skipped`,跳過原因也走 `reason`。
- 設定欄位用 snake_case,與 `results_dirs`、`tolerance_pct` 同風格。
- 範本檔名前綴 `android-`,與既有兩支一致。

不一致的有兩處。

**F3:設定檔缺失時的處理與既有流程衝突。**
- S14 要求專案沒有 `.lumos/macrobench.json` 也照判。
- 但既有 `_macrobench_config` 規定 `results_dirs` 必填(`scripts/lumos:39402`)。
- 既有 `_macrobench_mode` 在設定為 None 時直接印「沒接」並回 0,不判門檻(`:39737`)。
- 同一份 `macrobench.json` 又被計劃拿來放 `stability.test_data` 和 `stability.strictmode`。沒有設定檔時,S7 的「沒宣告 strictmode 就跳過」和 S15 的 test_data 判斷無處可讀。
- 純穩定性專案(沒有 Macrobenchmark)被 `results_dirs` 必填擋下,計劃沒交代怎麼放行。

severity: minor
blocking: 否
引句:「專案沒有 `.lumos/macrobench.json` 也照判」
佐證 file: `scripts/lumos:39737`

**F4:收集腳本的回傳碼與擋下訊息沒定。**
- 重跑腳本有明確約定:0 全符、1 不符、2 收據寫錯或環境沒準備好,且 stderr 印「擋下:」(`android-receipt-rerun.sh:5`、`:38`、`:60`)。
- 計劃只寫了逾時與刪暫存檔,沒說收集腳本的回傳碼與訊息格式。

severity: minor
blocking: 否
引句:「每個 adb 與 trace_processor 呼叫都有逾時,中途失敗也刪暫存檔」
佐證 file: `scripts/templates/android-receipt-rerun.sh:60`

## 問 3 第二種做法

對齊的部分:
- 找工具用 `${TP:-trace_processor}`,與重跑腳本同一做法(`android-receipt-rerun.sh:11`)。
- 原始檔放 `.lumos/artifacts/android/<run-id>/`,與 skill 慣例一致(`SKILL.md:23`)。
- 收據的查詢鍵是字串,與重跑腳本約定一致(`android-ui-attribution.sql:12`)。
- 沒有另開門檻檔,沿用 `macrobench-thresholds.json` 加 `check` 欄位。
- 範本登記 `_VENDORED_TREE_FILES` 並帶 SPDX,與既有一致(`scripts/lumos:31913`)。

不一致的有兩處,加上 F1:

**F5:結果檔的來源有兩條路。**
- Macrobenchmark 結果檔靠設定檔的 `results_dirs` 掃目錄找。
- 穩定性結果檔改成在命令列用 `--stability <結果檔>` 傳路徑。
- 同一個指令出現兩種供給結果的方式,計劃沒說為什麼不掃目錄。
- 這是計劃明寫的取捨,不是疏漏,所以只算 minor。

severity: minor
blocking: 否
引句:「`lumos macrobench --stability` 照門檻檔判」
佐證 file: `scripts/lumos:39402`

**F6:快照保存規則有第二套機制。**
- 既有規則是收據的 `artifact_store.keep_until` 加人裁的 `[DECISION]`(`skills/lumos-android-evidence/reference.md:32`、`SKILL.md:111`)。
- 計劃在 `macrobench.json` 放 `test_data` 宣告,再加收集腳本固定 7 天自動刪。
- 計劃有明講是取代「沒有人裁的保存規則不錄 L3」那條,所以不算偷渡。
- 但 skill 的 L3 手動流程(`heap_profile`、`java_heap_dump`)仍留著,兩條錄法各用各的保存規則,計劃沒說 L3 手動流程要不要也走 `test_data` 與 7 天。

severity: minor
blocking: 否
引句:「收集腳本每次開跑先刪掉這個專案產物目錄底下超過 7 天的快照檔」
佐證 file: `skills/lumos-android-evidence/reference.md:32`

## 問 4 落點

對齊的部分:
- `lands_in` 寫 `Systems/macrobenchmark-adapter`,與既有範本的家一致。
- 「這次要改到的地方」涵蓋了 `scripts/lumos`、`scripts/templates/`、`skills/lumos-android-evidence/`、`skills/lumos-project-notes` 的 `reference.md` 與 `commands/04-自檢與健康.md`(`reference.md:87`、`04-自檢與健康.md:21`)、`Android逐層診斷_計劃` 和 `Macrobenchmark驗收門檻_計劃`。
- 我沒找到漏列的檔案。skill 本身沒有 Systems 家節點,所以 `lands_in` 不列它是合理的。

**F7:家節點的規模與定位。**
- 家節點目前 51 行,摘要約 13 行。計劃再塞進約 14 條 WHY,加 4 支範本、一次改寫負責範圍。
- 它會從「讀 Macrobenchmark 結果」變成一個裝置端收集加判定的節點。計劃自己卻否決了 Macrobenchmark 的 `measureRepeated`,主題對不上節點名。
- 既有範本都掛這篇,有先例(`macrobenchmark-adapter.md:49`,「同屬 Android 效能證據這一塊」),所以只算 minor。
- ⚠ 是否另開一篇收集腳本的節點(例如 `android-stability-collector`),屬判斷題,我判不準。

severity: minor
blocking: 否
引句:「家節點 [[Systems/macrobenchmark-adapter]]:`about_code` 加新的四支範本」
佐證 file: `docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md:6`

不對齊共 7 條,其中 major 1 條

(相關檔案絕對路徑根:`/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability`。)
