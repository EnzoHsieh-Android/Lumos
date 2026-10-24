severity: minor

白話:這份設計大體走在既有的路上,沒有跨層直呼,也沒有另開指令或另開門檻檔。對不上的地方都不是結構性的,只是新做法有幾處沒講清楚。

**1. 分層與依賴方向:對齊**
- 計劃寫明「Lumos 不跑第三方工具,trace_processor 與 adb 只在範本腳本與 skill 裡用」。這跟既有規則一致:`Projects/Android逐層診斷_計劃.md:23` 寫「Lumos 零依賴、不碰裝置」,`Systems/macrobenchmark-adapter.md:6` 寫「不接裝置」。
- 判定只加在 `lumos macrobench`,延伸 `_macrobench_mode`(`scripts/lumos:39724`)。它讀檔、不跑 Gradle、不接裝置,所以沒有跨層。
- 範本放 `scripts/templates/` 並登記進 `_VENDORED_TREE_FILES`(`scripts/lumos:31913-31930`),跟 `android-receipt-rerun.sh`、`android-ui-attribution.sql` 一樣。
- 有一點要留意(⚠ 交編排者):既有兩支範本只跑 trace_processor,沒有跑 adb 的。新收集腳本是第一支在範本裡跑 adb 的,計劃把它當成既有規則的延伸。
- 另外,家節點 responsibility 寫「不接裝置」(`Systems/macrobenchmark-adapter.md:6`),新收集腳本要接裝置。計劃只把負責範圍改成「讀結果檔與收集結果檔」,沒講這句「不接裝置」怎麼辦,見問題 4 的 finding。

**2. 命名與錯誤處理:大致對齊,有兩處不一致**
- 對齊的部分:
  - 輸出沿用 `threshold_failures`、`threshold_passed`、`threshold_skipped`,跟 `scripts/lumos:39678` 同名。
  - 缺欄位列成跳過並說原因,跟 `:39685-39700` 的 `reason` 寫法一致。
  - 不認得的 `kind` 或缺必填欄位走「擋下並說原因」(計劃 S13),對應既有「擋下:…」加回傳 2(`:39732`),只提醒的判定回 0。
  - `round` 用字串,跟 `android-ui-attribution.sql` 檔頭「第一欄是字串鍵」同一規則。
- 不一致的地方:
  - `kind` 這個欄位名已經有兩種意思:`failed[].kind == "duplicate"`(`scripts/lumos:39594`)和收據 manifest 的 `"kind": "lumos-macrobench-json"`(`skills/lumos-android-evidence/reference.md:47`)。再加一個門檻條目的 `kind`,同一個詞在同一個子系統裡指三種東西。
  - 既有門檻條目必填 `scenario/metric/stat/contract/decided_by/decided_at`(`:39629`),輸出和印字也都用 `r['metric']`、`r['stat']`、`max/min/current`(`:39716-39718`)。計劃說有 `kind` 的條目只必填 `scenario/contract/decided_by/decided_at`,沒有 metric/stat,也沒有單一上限或下限。計劃沒說這種條目在 `threshold_failures` 裡長什麼樣、怎麼印。這個形狀不定,既有印字會直接壞掉。
  - `--stability <結果檔>` 讀不了、不是 JSON、或欄位型別不對時的回傳碼沒寫。S13 只管 `kind` 的錯,而既有慣例是壞檔回 2(`:39732`)。

finding A(`kind` 同名多義):
severity: minor
blocking: 否
引句:「門檻檔的每一條加一個選填的 `kind` 欄位(leak、instances、peak、exits、strictmode、frozen)」
佐證 file: `scripts/lumos:39594`

finding B(有 `kind` 的條目輸出形狀沒定,既有印字依賴 metric/stat/max/min):
severity: minor
blocking: 否
引句:「`scenario`、`contract`、`decided_by`、`decided_at` 照舊必填」
佐證 file: `scripts/lumos:39716`

finding C(`--stability` 結果檔壞掉時的回傳碼沒寫):
severity: minor
blocking: 否
引句:「判定(`lumos macrobench --stability <結果檔>`):門檻檔裡寫了 `kind` 的條目對結果檔判」
佐證 file: `scripts/lumos:39732`

**3. 第二種做法:整體對齊,有一處輸入通道要留意**
- 對齊的部分:
  - 計劃明說不另開門檻檔、不另開指令,沿用 `.lumos/macrobench-thresholds.json` 與 `lumos macrobench`。
  - 收據照用現有的重跑腳本和 queries.sql 規格。
  - 判定「只提醒、回 0」,跟 `Systems/macrobenchmark-adapter.md` 的 WHY「有退步也回 0」一致。
  - 快照路徑 `.lumos/artifacts/android/<run-id>/` 跟 `skills/lumos-android-evidence/reference.md:3` 一致。
- 要留意的地方:既有的結果檔都是靠 `.lumos/macrobench.json` 的 `results_dirs` 發現(`_macrobench_collect`)。新的 `stability.json` 改成用旗標傳路徑,是第二種「結果檔怎麼找」的做法。
  - 這是 Macrobenchmark 結果檔之外的另一種資料,不是同功能重做,所以我只標 ⚠ 交編排者,不列 major。
  - 沒說的事:沒有 `.lumos/macrobench.json` 時,`_macrobench_mode` 會在 `cfg is None` 直接回「沒接 Macrobenchmark」(`scripts/lumos:39741`)。`--stability` 在沒接 Macrobenchmark 的專案會不會走到,計劃沒交代。
- 另外,計劃沒說收集腳本怎麼找 trace_processor。既有重跑腳本用環境變數 `${TP:-trace_processor}`(`scripts/templates/android-receipt-rerun.sh:11`),skill 用 `$SKILL_ROOT/references/perfetto/bin/trace_processor`(`skills/lumos-android-evidence/SKILL.md:15`)。若新腳本自己再發明一種找法,就是第二種做法,最好寫明沿用 `TP`。

finding D(收集腳本找 trace_processor 的方式沒寫,有分岔風險):
severity: minor
blocking: 否
引句:「收集腳本放工具鏈範本目錄、照抄進消費專案,判定加在 `lumos macrobench` 與既有門檻檔」
佐證 file: `scripts/templates/android-receipt-rerun.sh:11`

**4. 落點合不合理:大致對齊,一處責任描述自相矛盾**
- 既有慣例:兩支 Android 範本都掛在 `Systems/macrobenchmark-adapter` 的 `about_code`(`docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md:8-10`),理由是「同屬 Android 效能證據這一塊」。
- 新的查詢範本和收集腳本掛同一篇,跟既有做法一致。`lands_in` 只列這一篇也合理,不必另開。
- 計劃有列要把 S6 記成被取代,以及 skill 的兩處改動,這幾處落點完整。
- 矛盾點:家節點 responsibility 明寫「不接裝置」,而收集腳本要跑 adb。計劃只把負責範圍改成「讀 Macrobenchmark 結果檔與收集結果檔」。收集腳本接裝置這件事,以及「不接裝置」這句要不要改成「Lumos 本體不接裝置,範本腳本才接」,計劃都沒說,改完會讓節點自己前後打架。
- 還有一點:這篇節點已經掛了兩支範本,再加一支腳本和一支查詢,份量變大。這不算不一致,只是提醒。

finding E(家節點「不接裝置」與新收集腳本接裝置衝突,計劃沒處理):
severity: minor
blocking: 否
引句:「家節點 [[Systems/macrobenchmark-adapter]] 的負責範圍改成「讀 Macrobenchmark 結果檔與收集結果檔」」
佐證 file: `docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md:6`

不對齊共 5 條,其中 major 0 條
