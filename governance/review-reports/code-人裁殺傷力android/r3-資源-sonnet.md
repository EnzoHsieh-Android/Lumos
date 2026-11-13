severity: clean

我讀完 r2 修補的三個重點(`_strip_c_comments`、每段合併的任務清單、`_lens_full_sha`)和它們的呼叫端,沒找到會做出錯行為的資源問題。以下是實測走過的輸入。

先交代鎖:`bfbdd1dd…json.warming` 這個檔不存在,沒有東西要處理,我也沒刪任何鎖。

## 實測(用 `scripts/lumos` 在記憶體載入,實驗檔放臨時目錄,結束後已刪)

1. **檔頭掃描加 `_strip_c_comments(kotlin=True)`**:對 `_situation_rule_imports_problem` 餵 4MB 的八種壞輸入,都在時間預算內完成。
   - 輸入包含:4MB 空行、4MB 的 `import x.Y` 行、`@file:Suppress(` 後接 4MB 空行、4MB 的 `` `\n ``、4MB 的 `"\n`、4MB 的 `"${`、4MB 的單引號、4MB 的 `/*` 巢狀。
   - 耗時是線性的:1MB 約 0.5 秒、4MB 約 2 秒(最慢的 `"\n`、單引號、`"${` 三種)。其餘輸入 4MB 都在 0.7 秒內。
   - 沒有正規式回溯爆炸,也沒有二次方成長。
   - 未收尾的 `@file:(` 回「沒有插入點」,不丟例外。
2. **記憶體**:4MB 空行檔增量約 41MB,沒超出測試的 40 倍界線。
   - 病態輸入會更高:4MB 的 `"\n` 實際增量 314MB(RSS),4MB 的 `// c\n` 增量 214MB。來源是共用剝法 `_kt_strip_spans` 每個區段記一筆。
   - 這是手造的 4MB 病態檔,沒有造成失敗,所以不標 finding。測試 ⑥ 的 40 倍界線只覆蓋空行這一種形狀。
3. **任務清單改成每段合併、`comments=True`**:
   - `_gradle_task_list` 只做一次拆段,沒有子程序。`sh -c` 只展開一層。
   - 沒有多讀建置檔:`_gradle_blocked_tasks` 只有在任務清單裡有頂層 `test` 或 `:test` 時,才對專案目錄讀一次 `_android_build_texts`。模組任務只讀 `max_depth=0`,即只讀那個模組資料夾。
   - `-p`、`-p=`、`-p ''`、`-p test` 這幾種寫法都不丟例外,也沒有卡住。
4. **`-p /` 與 `-p /Users`**:`_under_root` 對絕對路徑照用,所以 `_android_build_texts` 會從 `/` 走最多 3 層。實測 0.35 秒,而且讀到系統上別的 Android 專案,誤判成「test 是 Android 的 test 任務」。
   - 有界(`max_depth=3`、`max_files=200`、不跟符號連結),`_under_root` 的文件也寫明單人威脅模型下不擋,所以不標。
5. **`--diff` 改用 `_lens_full_sha`**:每端 1 個 git 子程序,共 2 個,有逾時,git 不在 PATH 回 None。沒有自叫 `subprocess`,不會留孤兒。`_situation_rule_target` 的 HEAD 解析改成同一支,多 0 個。
6. **新增的提早 return 路徑**:`run_cmd` 不是字串、`-p` 檢查擋下、`--import` 的 also 錯誤,這幾條都發生在殺傷力開隔離工作樹之前,或是純記憶體運算。我沒看到它們留下暫存或子程序。
   - 殺傷力開工作樹之後 also 套用失敗的收尾,屬 r1、r2 已處理的範圍。

## 附:圖譜鏡頭

這次派工沒附固定席筆記,我只看這個範圍牽連到的兩篇。

- **`Systems/棧別提問表態閘`**(情境題人裁那條 WHY):修補後的文字(剝註解走 `_strip_c_comments`、`run_cmd` 每個 gradle 段都查、`#` 註解不算、`-p` 換專案目錄、`:test` 照頂層 test 判)和程式碼行為一致,我用實測驗過。不影響該節點宣稱的合約。
- **計劃筆記**(〈用詞〉檔頭區與任務清單):描述和 `_detekt_walk_segments(comments=True)` 的行為一致。
  - 唯一落差是記憶體界線:筆記寫「4MB 空行檔記憶體回到修補前量級」,實測只對空行成立,病態輸入約 75 倍。
  - 不影響決策,不用改筆記。

最嚴重 severity:clean,blocking 共 0 條。
