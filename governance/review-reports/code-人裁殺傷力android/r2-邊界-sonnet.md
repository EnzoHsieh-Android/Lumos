severity: minor

我逐 hunk 讀完修補差異和完整改動,也用 in-process 載入真實 `scripts/lumos` 跑了實驗。實驗腳本在 `/tmp/lumos-seat-work/code-人裁殺傷力android/邊界-sonnet/`(t1 到 t6.py、proj/),沒有改 repo,也沒有用萬用字元刪檔,收貨後請編排者刪。鎖檔 `…0647f9.json.warming` 不存在,不用處理。

## b1 任務清單只取第一個 gradle 段,規格〈用詞〉寫的是每一段
severity: minor
blocking: 否
引句:「第一個呼叫詞是 gradle(_is_gradle_head)的那一段」
file: `scripts/lumos:76390`
1. 規格〈用詞〉的任務清單寫「每一段第一個檔名是 gradlew 或 gradle 的詞之後…」,實作的 `_gradle_task_list` 在第一個 gradle 段就 `return`。這是少擋,屬於規格與實作不是同一個定義。
2. 輸入:Android 專案,run_cmd 為 `./gradlew assemble && ./gradlew test --tests '*{method}'`。
3. 實測 `_gradle_task_list` 回 `['assemble']`,`_situation_rule_android_cmd_problem` 回 None,沒有擋下。同樣漏掉的還有 `./gradlew clean; ./gradlew test`(只回 `['clean']`)和 `./gradlew :app:test || ./gradlew :lib:test`。
4. 後果:壞的 run_cmd 要跑完基準才 abort,沒有在跑殺傷力之前 rc2。
5. 規格〈天花板〉第 3 點寫明基準 abort 有摘錄可看,後果有限,所以我判 minor。
6. 修法二擇一:改成對每個 gradle 段合併任務清單,或把規格改成「第一個 gradle 段」。
7. 順帶:`:test`(根專案前綴)不在清單裡擋,實測 `_gradle_blocked_tasks([':test'], 根是 Android 專案)` 回 `[]`。規格(a)寫「沒有模組前綴、剛好是 test」,對這個寫法沒有講清楚,兩邊要對齊。

## b2 run_cmd 行尾的 shell 註解被當成任務,會誤擋
severity: minor
blocking: 否
引句:「照 detekt 判定同一套拆段(_detekt_walk_segments:續行、;&| 分段、剝環境變數與」
file: `scripts/lumos:40647`(`_detekt_split_segments` 設了 `commenters = ""`,`#` 後面的字照樣切成詞)
1. 輸入:Android 專案,run_cmd 為 `./gradlew :app:testDebugUnitTest --tests '*{method}' # test only`。這條 run_cmd 在 shell 裡完全合法。
2. 實測任務清單回 `[':app:testDebugUnitTest', '#', 'test', 'only']`,裡面多了字面的 `test`。
3. 在 Android 專案實測,人裁 rc2,訊息說「任務 test 是 Android 的 test 任務」。使用者看不出是註解害的。
4. 這是改用 detekt 拆段後新帶進來的行為,舊的自寫 shlex 預設會處理 `#`。detekt 那邊刻意不當註解,但人裁這邊要的是任務名。
5. 修法:`_gradle_task_list` 遇到以 `#` 開頭的詞就停。

## b3 run_cmd 不是字串時人裁直接丟例外,不是 rc2
severity: minor
blocking: 否
引句:「cmd = pentry.get("run_cmd") or ""」
file: `scripts/lumos:76437`
1. `load_platforms` 不驗 `run_cmd` 的型別,例如設定寫成 `["./gradlew","test"]`、數字或物件。
2. 預設平台的 profile 是 kotlin-junit,`run_cmd` 不是字串但為真值時,`_situation_rule_platform` 的「有沒有 run_cmd」檢查會過。
3. 接著 `"YOUR_MODULE" in cmd` 或 `_gradle_task_list` 的 `.replace` 丟例外。我實測:數字 123 得 `TypeError`,list 和 dict 得 `AttributeError: 'list' object has no attribute 'replace'`。
4. 本案新加的呼叫點讓人裁在殺傷力之前就丟 traceback,而不是印設定錯誤並 rc2。
5. 修法:`cmd` 不是 str 就當作沒有設定並印原因。

## 查過、沒問題的項目(不必重報)
- **`--import` 邊界:** 空字串、`*`、`as`、反引號、換行、結尾換行、全形字、重複給、同名不同套件、名稱只是子字串都被擋。`\r\n` 檔、BOM、shebang、`;` 結尾、`@file:` 括號跨行、字串內的括號、區塊註解在 import 行尾開啟(插入點退回 package 行)都插得對。CRLF 時插入的行是 LF,Kotlin 不受影響。
- **`--diff`:** `-x..HEAD`、`A...HEAD`、`A..`、`..HEAD`、解析不到的提交、空字串都由入口驗擋下。完整 sha 或別名作右端,只要等於 HEAD 就收。
- **`_kill_run_dir`:** 規格 S11 與實作一致。平台根是 repo 最上層時回工作樹本身,沒提交時判 error 且基準不跑。我看不到會改壞既有「平台根等於 repo 頂」設定的路徑。
- **`_kill_mask_paths`:** 邊界用法正確。工作樹先於家目錄、長路徑先於短路徑的順序也對。在 256KB 文字上耗時趨近 0。
- **`lumos init`:** 在沒有建置檔、建置檔是資料夾、建置檔不可讀、建置檔不是 UTF-8、註解裡寫外掛名、建置檔在第 4 層這幾種情況都不丟例外。第 4 層判不到,屬規格〈天花板〉第 3 點。
- **效能:**
  - 30 萬行註解的檔頭掃描 0.21 秒,20 萬條 import 0.9 秒。
  - 5 萬個選項或 5 萬段的 run_cmd 解析在 0.2 秒內。
  - 唯一慢的是 import 行中間夾 10 萬個空白,耗時 17 秒(`re.split(r"\s+as\s+")` 的二次方回溯)。這要靠對自己 repo 的 HEAD 檔刻意造出,不屬於威脅模型,所以沒標。

## 附:圖譜鏡頭
這次派工沒附固定席節點。我自己跑 `impact --diff` 取了牽連最直接的三個節點:
- **`Systems/guard-kill`:** 這次改動不影響它的兩條 ★INVARIANT★(rc 優先序、`--json` 純度)。新增的 run_dir error 走既有的 error 判定,rc 仍是 2,沒有新增 stdout 診斷。第 14、48 行的 WHY 已經寫了「在平台根跑」,和實作一致。
- **`Systems/bound-tests-gate`:** 它的 ★INVARIANT★ 關於推送前閘逐支真跑綁定測試。`_run_bound_tests` 沒被改,殺傷力現在改成和它同一個執行目錄,不影響該合約。
- **`Systems/lumos-cli-lifecycle`:** 它的 re-inject 合約不涉及 init 的 run_cmd 骨架,不影響。

最嚴重 severity:minor,blocking 共 0 條。
