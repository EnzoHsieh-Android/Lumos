severity: clean

**①提示注入**
已看,無。型錄、壞例樣本和範本文字只進 `check.py` 的比對,輸出是給人讀的自檢問題訊息。這份修補沒有把這些文字寫進派工詞、hook 附加段或指令。

**②讀寫與執行越界**
已看,無。
- `check.py` 這輪新增的程式只做讀檔、`split`、正規式比對和字串比對。沒有 `subprocess`、`os.system`、`eval` 或 shell 插值,沒有讀 repo 外的路徑,也沒有環境變數覆蓋下載來源。
- `_bad_lines` 讀的是 `samples_dir/bad/<rule_id>/` 底下的 `*.kt*`。`rule_id` 來自規則 yml 的 id,不是外部輸入。
- 新測試用 `tempfile.mkdtemp(prefix="gctl-badlines-")` 建目錄(權限 0700),只寫固定內容的假壞例檔。測試在 `finally` 用 `rmtree` 清掉,沒有拼接命令或外部輸入。
- 樣本和型錄文字進正規式的路徑是既有的 `_kt_trigger_re`,這輪沒動。檔案都是 repo 內自己維護的。
- `mutate2.py.txt` 已確認:`r3-repair-binding.json` 的 `archive_only` 列了它,檔案也已追蹤在 git 裡,副檔名是 `.txt`,不會被執行。這份修補差異裡沒有它的內容。
- 差異裡沒有新的密鑰或信箱。`gen_tables.py.txt` 只改了理由字串,而且是 `.txt`,不執行。

**③非刻意、一步就能繞過的守衛**
已看,無。逐項推演如下。
- **// BAD 新判讀會不會讓壞例檔寫錯也被當成有標記:沒有,反而更嚴。**
  - 新判讀是:這行原文裡 `// BAD` 的出現次數,要多於「只去註解、保留字串」版本裡的次數,才算標記。
  - 這樣字串裡的 `"see // BAD"` 不再被當標記,以前用原文直接比對時會誤認。
  - 誰=照常編輯壞例檔的人或 AI,從哪=多寫或少寫一行字串或註解,送什麼=字串裡含 `// BAD` 的行,拿到什麼=規則改由的核對意外通過。這條路徑在這輪修補後已被關上。
  - 殘餘情況:`/* … // BAD … */` 區塊註解裡的字樣仍算標記。這是修補前就有的行為,會把後面的語句認成被標的行。這屬於寬鬆,但要先在註解裡寫出 `// BAD` 才會發生,不是單步意外。我只提這一句,不列為發現。
- **三份行對不上時失敗關閉:** 原文、去註解版、保留字串版三份行數不一致時,`_bad_lines` 會回報「去註解後行數對不上」的問題並 `continue`,不會靜默放行。
- **換頁字元與 U+2028:** 三份一律只照 `\n` 切,不再用 `splitlines()`。這讓行號與 ast-grep 的行號一致,關掉了「前一行有換頁字元就把標記對到別行」的偏移。
- **只有註記的行跳過:** `_ANNOTATION_ONLY_RE` 比舊的 `startswith("@")` 嚴。`@Composable fun A(...)` 這種註記後面接程式的行不再被跳過,所以標記不會漂到下下行去。
- **`_unreach_table` 片段格:** 改成整格恰好一段反引號才取內文,否則用整格原文。對不上反查單位就會被報,方向是失敗關閉。
- **`_visible_lines`:** 未閉合圍欄在 `keep_fenced` 時,內文一路算到檔尾,與 CommonMark 一致。這修掉最後一行被丟掉的洞,對守衛只有加強。
- **環境殘留:** 這輪新增的程式不讀 `LUMOS_SKIP_*` 或 `PYTHONPATH`。

**看過的檔(9 支)**
- `configs/ast-grep/kotlin-android/check.py`
- `configs/ast-grep/kotlin-android/coroutines-api/jvm-only.txt`
- `configs/ast-grep/kotlin-android/samples/situation/D-4.kt.txt`
- `docs/lumos-toolchain-knowledge/Projects/情境決策點窮舉與壞寫法要叫得出_計劃.md`
- `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md`
- `docs/lumos-toolchain-knowledge/Verification/2026-11-12_情境決策點窮舉實作驗證.md`
- `governance/review-reports/情境決策點窮舉與壞寫法要叫得出/sweep/gen_tables.py.txt`
- `scripts/test_lumos.py`
- `skills/kotlin-idioms/checks-catalog.md`

總結:最高等級 clean,共 0 條
