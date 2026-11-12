severity: clean

這輪修補差異裡沒有能被利用的洞。下面三類都已逐項看過。

**①提示注入:已看,無。**
- 修補差異裡,型錄片段、理由、壞例樣本的文字只流進 Python 內部的字串比對和正規式比對。
- 沒有任何一處把這些文字寫進給 AI 的派工詞、hook 附加段或指令。
- `_bad_lines` 讀到的樣本文字只拿去和型錄片段比對。
- 比對失敗時,錯誤訊息只回到 `check()` 的問題清單,不進 AI 指令。

**②讀寫與執行越界:已看,無。**
- `check.py` 呼叫 ast-grep 的方式沒變:`subprocess.run([sg, "scan", "--config", ..., target])`,用清單、不經 shell。
  - 這次修補沒有碰這段。
  - 型錄、樣本的文字沒有進到這條指令列的任何位置。
  - `sg` 來自呼叫端的 `--sg` 參數;`LUMOS_AST_GREP` 環境變數只在 `scripts/test_lumos.py` 的 `_ktpack_sg` 讀取,而且被當作整個執行檔路徑,不是被拼接的字串。
- 這次修補沒有碰 `load_lumos`:路徑固定是 `HERE.parents[2]/scripts/lumos`,`HERE` 取自 `__file__` 的 resolve 結果,型錄內容換不掉它。
  - 修補在 `_bad_lines` 新增的 `lumos._strip_c_comments` 呼叫,用的是同一個已載入的模組。
- `_bad_lines` 只對 `samples/bad/<rule_id>/` 做 `rglob("*.kt*")` 並讀檔。
  - `rule_id` 來自型錄〈叫不出的壞寫法〉的「規則 kt-…」,先經 `_ROUTE_RE` 限成 `[\w-]+`,再要在 `by_rule` 裡找得到才會走到。
  - 不會因此讀到 `samples` 目錄之外。
  - 壞例檔讀不了時會捕捉 `OSError` 和 `UnicodeDecodeError`,轉成問題訊息,不崩。
- 新增的測試 `rmtree(mc.HERE.parents[2])` 刪的是 `_ktpack(copy=True)` 用 `tempfile.mkdtemp(prefix="gctl-ktpack-")` 建的複本根目錄。
  - `HERE` 被改指向複本,`parents[2]` 就是那個暫存根目錄,不是真 repo。
  - 新測試 `_reach_route_guards` 另建的 `gctl-badlines-` 暫存目錄也由 `finally` 刪掉。
- `shutil.copy(GRAPHCTL, 複本/scripts/lumos)` 複製的是測試自己的主程式,目的地在暫存複本內。
- `mutate.py.txt` 是副檔名 `.txt` 的卷證。
  - 我在 repo 內搜過,沒有任何設定或腳本會執行它;`r2-repair-binding.json` 也把它列為 `archive_only`,只記錄不重讀。
  - 檔案裡確實寫了本機 scratchpad 的 ast-grep 路徑,屬卷證裡本機絕對路徑的既有慣例,不報。
- 這次差異沒有新寫進程式、範本或公開文件的密鑰與信箱。
- `jvm-only.txt` 和 `api-curated.py.txt` 只是名稱清單與理由文字,沒有可執行內容。

**③非刻意、一步就能繞過的守衛:已看,無。**
- 新的守衛各有一條會翻紅的測試:
  - 壞例標記要整字認(`//BAD`、`// BAD-NEXT` 算,`// BADGE` 不算)。
  - 只有 `…` 的片段不算比到。
  - 同一個(情境列, 對應檢查, 片段)出現兩列要報。
  - 壞例檔讀不了要報。
  - 規則的起訖行要涵蓋片段所在的 `// BAD` 行。
- 我沒找到「照平常操作就意外走過去」的路徑,也沒有新增依賴環境變數才生效的跳過旗標。
- 本機沒有 `PYTHONPATH` 或 `LUMOS_SKIP_*` 殘留就會讓這些守衛失效的情況。
- `import sys` 的 `dont_write_bytecode` 切換有 `finally` 還原。

**看過的檔(10 支):**
1. `configs/ast-grep/kotlin-android/check.py`
2. `configs/ast-grep/kotlin-android/coroutines-api/jvm-only.txt`
3. `configs/ast-grep/kotlin-android/samples/situation/D-4.kt.txt`
4. `docs/lumos-toolchain-knowledge/Projects/情境決策點窮舉與壞寫法要叫得出_計劃.md`
5. `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md`
6. `docs/lumos-toolchain-knowledge/Verification/2026-11-12_情境決策點窮舉實作驗證.md`
7. `governance/review-reports/情境決策點窮舉與壞寫法要叫得出/sweep/api-curated.py.txt`
8. `governance/review-reports/情境決策點窮舉與壞寫法要叫得出/sweep/gen_tables.py.txt`
9. `scripts/test_lumos.py`
10. `skills/kotlin-idioms/checks-catalog.md`

第 4、5、6、10 支是文件與型錄,只掃過有沒有密鑰、信箱或可執行片段,沒有。

總結:最高等級 clean,共 0 條
