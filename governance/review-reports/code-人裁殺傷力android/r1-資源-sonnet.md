severity: clean

我逐個 hunk 用具體輸入走過一遍。資源鏡頭下沒有 finding。

## 附:圖譜鏡頭
這次派工沒有附固定席節點(LUMOS-LENS 寫「沒附固定席節點」),所以沒有逐條要答的圖譜項目。

另外,派工指定要檢查的 `.warming` 鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/3e6c2aa7f3cb792dd8196fe6df183fa162b4e4e5429f81f839e9aeb82ffdba22.json.warming` 不存在,沒有鎖要處理,我也沒刪任何東西。

以下是逐項走查的結果,每項都沒有壞處。

1. **Gradle 輸出 50MB 時的 `fail_excerpt`**
   - `_kill_run` 先把輸出過 `_kill_cap`,上限 256KB,所以 `_kill_fail_excerpt` 實際拿到的最多 256KB。
   - 我用 `_kill_fail_excerpt` 實測。256KB 全是 `e: x` 行,耗時 0.01 秒,結果 800 字。
   - 就算有人繞過上限直接給 50MB,耗時 1.3 秒,峰值記憶體約 0.8–0.95GB,但實際呼叫端不會這樣傳。
   - `* What went wrong:` 後面沒有空行的最壞輸入,也只多花 1.2 秒。
   - 兩條正規式都沒有回溯風險。`_KILL_IMPORT_RE` 的重複段用 `.` 分隔,沒有歧義;`\b{name}\b` 的名稱經過 `re.escape`。
2. **`--file` 在很深的目錄往上找建置檔**
   - `_gradle_module_candidate` 的迴圈條件是 `d.startswith(root + os.sep)`。碰到平台根或 `/` 就停,不含平台根本身。
   - 檔案在 repo 外時迴圈一圈都不跑,回傳 None。
   - 每層只做兩次 `isfile`,層數受路徑深度限制。
   - `:a:b:test` 的各段排除了 `.` 和 `..`,讀建置檔的位元組上限是 1MB,解析後不在資料夾底下的連結也不讀。
3. **多模組大 repo 讀幾次建置檔**
   - `_android_build_texts` 最多往下 3 層、200 支檔、每支 1MB,而且跳過隱藏資料夾和 `_stack_scan_skip` 的資料夾。
   - 人裁每次只在 `_gradle_blocked_tasks` 裡、任務清單含裸 `test` 時呼叫一次。
   - 模組候選用 `isfile` 往上找,不讀內容。
   - `lumos init` 用 `_init_android_probe` 記住結果,只在 kotlin/java 的 JUnit 平台才掃,多平台時整次 init 也只掃一次。
4. **`--diff` 開幾個 git 子程序**
   - `_situation_rule_diff_problem` 固定 2 個 `rev-parse`,之後走原本 `_kt_bj_segments` 的路徑,沒有迴圈。
   - 兩端都過 `--end-of-options`,不以 `-` 開頭,不能夾帶選項。
5. **`also` 套用失敗時的隔離工作樹與子程序**
   - `_situation_rule_also` 會先對 HEAD 版預套一次 `_kill_also_apply`,通常在跑 Gradle 之前就擋下。
   - 預套與 `cmd_guard_kill` 的差異不會讓預套通過、實跑卻失敗:兩邊都把換行統一成 `\n`,`_kt_sit_read_many` 的 `\r\n` 也轉成 `\n`,而 guard kill 以文字模式讀檔。
   - 萬一 guard kill 裡 `_kill_mutated` 回錯誤,走 `continue`。這發生在寫檔之前,也在壞法那次執行之前,所以沒有殘留子程序。工作樹照舊由 `finally` 清掉。
   - 預檢的幾個提早 return(run_cmd 擋下、`--import` 不合、`--diff` 不合)都發生在開工作樹與跑 Gradle 之前,沒有暫存、沒有子程序。
6. **`_KILL_ALSO_MAX` 與 `--import` 數量**
   - `_KILL_ALSO_MAX` 限的是 `also` 的筆數,`--import` 可以重複給很多次。`imports[:k]` 是 O(k²),受命令列長度上限限制,單人使用下不構成風險,所以我沒標。
7. **測試暫存**
   - 新測試都有 `_ksp_sh.rmtree(…, ignore_errors=True)` 清自己建的 `gctl-sra-*` 目錄,沒有看到留下暫存的路徑。

我的實驗腳本放在 scratchpad,跑完已用字面絕對路徑刪掉。

最嚴重 severity:clean,blocking 共 0 條。
