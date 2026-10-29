severity: major

## 三問

**問 1 分層:對齊。**
- 判法第 1、2 條寫在收集腳本,第 3、4 條寫在 lumos。這個切法跟鄰居一樣。
- 算 L1/L2 算縮減,不算判定。它跟 `android-stability-cycle.sql` 在 SQL 裡算出 `peak_anon_swap_kb`、`frozen_frames` 同性質,都是把原始資料壓成幾個數字,沒有說過不過。`heap_result` 只留前後有變的類別(`scripts/templates/android-stability-collect.sh:460-466`),也是縮減。
- 分類、下限、排序放 lumos,跟 `_macrobench_stab_java_growth` 的 `need`、`grown` 判定同層(`scripts/lumos:40054-40066`)。
- 提示不進 `MACROBENCH_CHECK_JUDGES`(`scripts/lumos:40156`),而是放在初始字典的固定鍵,跟 `stability_unjudged`、`low_iterations` 同處(`scripts/lumos:40312`)。這也對齊。
- 只有一處不乾淨,見 F5:1 MiB 這個數字兩層各有一份。

**問 2 命名與錯誤處理:大致對齊,有三處小差異。**
- 狀態只用 ok / failed / unsupported,並沿用 `src()`,對齊 `collect.sh:376`。
- 讀結果檔、印出前清字元,沿用 `_macrobench_stab_val` 和 `_events_clean(…, 500)`,對齊 `scripts/lumos:40020`、`40242`。
- 不對齊的三處是命名(F2)、樣本不足的狀態與時機(F3)、整數檢查(F4)。

**問 3 第二種做法:有一處。**
- 查詢放範本檔、用 `WITH RECURSIVE`、測試用 Python 內建 sqlite 對假表跑,都跟 `android-ui-attribution.sql:20` 和 `android-heap-classes.sql` 一樣。
- `csv.reader` 是第二種解析做法(F1)。
- 整數比和驗數字沒有另起一套。

### F1 同一支收集腳本裡出現第二種 csv 解析
severity: major
blocking: 是
引句:「整個輸出交給 csv.reader 解析(函式簽名會帶逗號與引號;第一段的 split 寫法不回頭改)」
file: `scripts/templates/android-stability-collect.sh:263`
1. `heap_counts` 用 `[c.strip('"') for c in line.split(",")]`,`cycle_numbers` 用 `rows[0].split(",")`(`collect.sh:300`)。第 4 步另用 `csv.reader`。
2. 這支檔目前沒有 `import csv`(`collect.sh:19`)。改完同一份 trace_processor 輸出會有兩種讀法。計劃自己寫了「第一段的 split 寫法不回頭改」,等於明講並存。
3. 計劃也沒說新增的 TP 呼叫要共用現有的「讀範本、換佔位、寫暫存檔、跑 TP」流程。`heap_counts` 和 `cycle_numbers` 各抄了一份(`collect.sh:251-258`、`289-297`),新函式會是第三份。
4. 接手的人會不知道該學哪一種。逗號是真問題:`heap_counts` 靠「只有最後一欄是數字」把逗號接回去,新查詢有多個文字欄,接不回去,所以才要 `csv.reader`。對應的處理是抽一支共用的「跑範本並解析成列」,三處都用它,或明確把舊兩支一起改。

### F2 L1/L2 與 skill 的診斷層撞名,且正文、JSON、鄰居三套命名
severity: minor
blocking: 否
引句:「每一項有 `func`、`so`、`caller`、`symbol`(true/false)、`system`(true/false)、`low1`、`low2`、`end`(位元組整數)」
file: `scripts/templates/android-stability-collect.sh:460`
1. 判法與條款用 `L1`、`L2`,結果檔欄位用 `low1`、`low2`,同一個量兩個名字。
2. 同一份計劃第 7 步要改 skill 的「L0 往下條件」和「L3」。在 lumos-android-evidence 裡,L1、L2 本來是診斷層(Perfetto、simpleperf),L1/L2 的意思會被讀混。
3. 鄰居的快照量一律用 `before`/`after`(`collect.sh:460-466`、`scripts/lumos:40010-40040`)。`end` 是窗口最小值之外的結尾累計,語意不同,但字面上沒有跟 `after` 對應的說明。

### F3 「樣本不足」寫 failed,而且在整段跑完之後才寫
severity: minor
blocking: 否
引句:「時段短於 4 個傾印間隔時寫 failed「樣本不足」」
file: `scripts/templates/android-stability-collect.sh:462`
1. 「N 小於 4」在第 2 步的前置檢查就已經知道(`st["cycles"]`)。第 2 步把條件不成立一律寫 unsupported 並在動手前停下,跟 `heap_result` 的 `unsupported if not test_data` 一樣(`collect.sh:448`、`462`)。
2. 這條卻讓第二段先錄完再回 failed。這樣會多錄一段、多留一個錄檔,結果檔上也分不出「設定本來就不夠」和「跑壞了」。
3. 鄰居對輪數不足的處理是 lumos 側的提醒(`scripts/lumos:39808-39832` 的 `low_iterations`),或判定函式的範圍檢查(`scripts/lumos:40058`)。沒有一個是跑完才寫 failed。
4. 「時段短於 4 個傾印間隔」要看資料才知道,寫 failed 合理。N 小於 4 該搬進第 2 步的判斷順序。

### F4 數字驗證只用 `_macrobench_stab_val`,宣告的整數沒有用整數檢查
severity: minor
blocking: 否
引句:「數字照 `_macrobench_stab_val` 擋負數與非數字」
file: `scripts/lumos:40020`
1. 第 5 步把 `low1`、`low2`、`end` 定為位元組整數,第 3 條又強調用整數比 `3 ×(L2 − L1)≥ L2`。
2. `_macrobench_stab_val` 只擋負數與非有限數,小數會通過(`scripts/lumos:39450`、`40020`)。
3. 鄰居對必須是整數的欄位另用 `_secev_int`(`scripts/lumos:8578`、`40058` 的 `cycles`、`40086` 的 `classes_seen`)。
4. 同樣,第 6 步「結果檔沒有這段 → unsupported」「status 不是 ok 就印原因」是自己寫的讀法,沒說要沿用 `_macrobench_stab_src`(`scripts/lumos:40010`)。接手的人要猜新鍵讀來源段用哪一套。

### F5 1 MiB 這個數字在兩層各有一份
severity: minor
blocking: 否
引句:「收集腳本不分類、不套 1 MiB 下限以外的門檻」
file: `scripts/templates/android-stability-collect.sh:460`
1. 收集腳本用「最後累計至少 1 MiB」篩輸出量(第 4 步),lumos 用「L2 小於 1 MiB → 不增長」分類(第 3 條)。兩邊篩的欄位不同(`end` 對 `L2`),沒有共用來源。
2. 鄰居的收集腳本只留「有變的類別」,不帶門檻常數。門檻只在 lumos 的判定函式裡(`need`、`min_per_cycle`,`scripts/lumos:40054-40066`)。
3. 改下限時要同時記得改兩處。因為 `L2 ≤ end`,收集端的篩選是 lumos 端的超集,現在不會出錯。

不對齊共 5 條,其中 major 1 條
