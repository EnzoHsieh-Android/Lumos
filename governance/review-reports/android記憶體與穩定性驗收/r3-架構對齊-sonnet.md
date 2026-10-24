severity: minor

**1. 分層與依賴方向**

整體對齊。判定留在 `lumos macrobench`(只讀檔、不接裝置),接裝置的事放進範本腳本。這跟既有分工一致:`scripts/templates/android-receipt-rerun.sh` 是獨立腳本,不 import lumos,靠 `TP` 找外部工具。收集腳本用 `JAVA_HEAP_DUMP` 找快照腳本,是同一種依賴方向。範本到 skill 腳本是外部工具依賴,不是跨層直呼。

我沒找到 major 的跨層直呼,只有一處 ⚠:設定檔 `.lumos/macrobench.json` 的 `stability` 段同時被收集腳本和 `lumos macrobench` 讀。`_macrobench_config` 目前在 `scripts/lumos:39402-39404` 強制要求 `results_dirs`,並用 `_macrobench_config_fields`(`scripts/lumos:39375`)驗每個欄位。計劃只寫了「有 stability 段時 results_dirs 可以不填」,沒寫誰驗 `stability` 段的欄位型別:lumos 這邊驗,還是只有收集腳本驗?
⚠ 判不準:`stability` 段的欄位驗證歸屬沒寫,可能變成兩邊各驗一套。

**2. 命名與錯誤處理**

回傳碼與擋下訊息對齊。壞設定和壞輸入回 2 並印「擋下:」,與 `scripts/lumos:39731` 和 `scripts/templates/android-receipt-rerun.sh:60` 一致。輸出沿用 `threshold_failures`、`threshold_passed`、`threshold_skipped`,與 `scripts/lumos:39708` 一致。數字走 `_macrobench_num`,與 `scripts/lumos:39365` 一致。環境變數 `JAVA_HEAP_DUMP` 與 `TP` 同型。有三條命名不一致:

severity: minor
blocking: 否
引句:「`exits`(新增的每筆 reason、kind、pid、timestamp、desc)」
佐證 file: `scripts/lumos:39460`
說明:`kind` 在 macrobench 已用在 `failed` 清單,值是 missing_dir、unreadable、duplicate。計劃自己的 WHY 也寫了「`kind` 這個名字在 macrobench 已有兩種意思」,並否決拿它當門檻欄位名。結果檔的 exits 卻又新增第三種意思。

severity: minor
blocking: 否
引句:「`device`(選填,多台裝置時的 adb 序號)」
佐證 file: `scripts/lumos:39650`
說明:既有門檻檔的 `device_model` 是「裝置型號,用來篩裝置」。設定檔新欄位 `device` 指 adb 序號,兩個詞容易混淆。結果檔的 `device_model` 又是型號。

severity: minor
blocking: 否
引句:「驅動指令裡的 `{cycles}` 換成輪數」
佐證 file: `skills/lumos-android-evidence/reference.md:77`
說明:專案現有兩種佔位字寫法,`{{NAME}}` 由 lumos 程式替換,`__NAME__` 由 AI 手動替換。`{cycles}` 單層花括號是第三種,由腳本替換。
另外,兩支 sql 範本需要的行程名由誰替換、套件名要不要驗字元,計劃沒寫。既有做法是 `skills/lumos-android-evidence/SKILL.md:53` 先驗套件名只含英數字、底線與點,再替換 `__PROCESS__`。

門檻欄位的單位後綴也不一致:`max_bytes`、`max_block_ms`、`min_per_cycle`,還有 instances 條目裡沒單位的 `max`。這屬風格,不列。

**3. 第二種做法**

我沒找到 major。門檻檔、輸出欄位、收據格式、找工具、設定檔都沿用既有做法。

- 門檻格式:沿用同一個 `.lumos/macrobench-thresholds.json`,加選填 `check` 欄位。計劃明確否決另開一個門檻檔、另開一個指令。
- 設定檔:`stability` 段加進同一份 `macrobench.json`,沒另開檔。
- 結果檔:`--stability` 吃單一路徑,不掃目錄,與 `_macrobench_collect`(`scripts/lumos:39452`)掃 `*-benchmarkData.json` 是兩條讀入路徑。計劃有寫理由(每次一個 run-id 目錄),且輸出沿用同一組 threshold_* 欄位,我判為有交代的差異。結果檔放 `.lumos/artifacts/android/<run-id>/`,與 skill 既有的原始檔位置一致。
- 找工具:`TP`、`JAVA_HEAP_DUMP` 兩個環境變數加 PATH 後備,與 `scripts/templates/android-receipt-rerun.sh:11` 一致。
- 收據:查詢第一欄為字串鍵、COALESCE 換 -1、註解不以分號結尾,都照 `reference.md` 的 expect 規則。
- 錄快照:沿用 skill 既有的 `java_heap_dump`,不另寫錄製設定。

有一處 ⚠:收據重跑的 manifest 只有 `artifacts[].path` 這個欄位(`scripts/templates/android-receipt-rerun.sh:19`)。計劃寫「快照 7 天後刪,刪了之後收據裡跟快照有關的數字標成不能重跑」,但「不能重跑」這個狀態在現有收據格式裡沒有對應欄位。
⚠ 判不準:標示怎麼表達沒寫,可能長出第二種收據狀態。

**4. 落點**

落點合理。`macrobenchmark-adapter` 目前的 `about_code`(`docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md:8`)已經管著兩支 android 範本,所以兩支新 sql 範本也放進去會更一致。不過這份計劃把它們連同收集腳本歸給新家 `android-stability-collector`,理由站得住:收集腳本是第一支會接裝置的範本,而 adapter 的 responsibility(同檔第 6 行)寫明「不接裝置」。新節點的負責範圍寫成「…;不判過不過」,與既有「負責…;不負責…」的寫法同型。

〈這次要改到的地方〉列了 `_VENDORED_TREE_FILES` 登記、SPDX 檔頭、註解不以分號結尾,與既有 PITFALL(`scripts/lumos:31913`)和 `android-ui-attribution.sql` 檔頭的做法對得上。新範本的登記清單在 `_VENDORED_TREE_FILES` 一處維護,有現成逐檔比對測試守著。

這一問沒有不對齊條目,只有上面兩個 ⚠。

不對齊共 3 條,其中 major 0 條
