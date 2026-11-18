severity: clean

我沒有在被審材料裡找到可被利用的洞,三類資安面向都沒有 finding。

**三類逐項**
- ①提示注入:已看,無。新增程式碼沒有把筆記內容、檔名、分支名、帳本欄位或席報告放進派工詞、hook 附加段或指令。`gov --stats` 的「依列號」小節輸出前,列號一律先經 `_kill_esc` 並截到 20 字,排序鍵也只認 `C-` 加最多 9 位 ASCII 數字。
- ②讀寫與執行越界:已看,無。新增的程式碼是 `check.py` 的撤列與樣本標記檢查、`scripts/lumos` 的錨點與編輯邏輯、統計小節。三者只讀工具鏈自己的 `kotlin-choice/` 目錄,沒有新的 subprocess、環境變數、下載網址或 shell 插值。測試裡新增的 `subprocess.run` 是以清單參數呼叫 `sg scan`,工作目錄是測試自建的暫存目錄。我用 grep 掃過全部新增行,沒有新寫入的密鑰、信箱或可用憑證;出現的網址都是論文與官方文件引用。`docs/.bypass-log.jsonl` 只多了一行,是這條分支自己的 wip 記錄,`governance/anchor-baseline.json` 只換了測試總檔的雜湊與簽核備註。
- ③非刻意一步繞過的守衛:已看,無。撤列守衛的格式不符時是回報錯誤,不會當成沒有撤列而靜默放行。樣本標記指向表裡沒有的列號時,新函式 `choice_sample_mark_problems` 會單獨報出來。這兩條都不依賴 `LUMOS_SKIP_*` 或 `PYTHONPATH` 之類的環境。

**修補鏡頭三問**
- 原問題的修復效果:修補範圍包含撤列行格式檢查與大數字列號排序。我在修後版本的臨時副本跑 `python3.14 scripts/test_lumos.py -k retired`,17 個測試全過。這只證明這批測試在修後版本通過,我沒有跑修前版本對照,所以歸因未判定。
- 修補處的正常、錯誤與相鄰呼叫路徑:`_choice_retired` 讀到沒有撤列、寫「(無)」、列號合法、格式不符這幾種輸入,程式碼上各走各的分支。`rules_dir` 為 False 時不看規則檔,這條分支也沒有對外的讀寫。我沒有逐一造這些輸入實際執行。
- 新發現:零條,所以沒有修前、修後的對照案例。

**已驗的正向主張**
- claim:撤列檢查對「資安三類」不開新口子。input:`_choice_retired`、`_choice_retired_problems`、`choice_sample_mark_problems` 的全部新增程式碼。expected:沒有外部可控字串進入指令或寫檔路徑。before:未跑,修前的撤列守衛本來就不存在。after:程式碼檢視加 `-k retired` 17 個測試全過。comparison:未判定,修前沒有對應行為可比。
- 未驗範圍:沒有執行 ast-grep 對 Kotlin 樣本的實掃。第二批的 `_choice_anchor_edits` 與 `_choice_anchor` 只做靜態閱讀,沒有逐條跑案例;它們處理的是被變異測試的 Kotlin 原始碼,我沒看到對應的資安攻擊路徑。
- 通知裡要求檢查的鎖檔(`/Users/enzo/.cache/lumos/dispatch-lens/807e5435….json.warming`),我沒有檢查也沒有刪。

最嚴重:clean;blocking 共 0 條
