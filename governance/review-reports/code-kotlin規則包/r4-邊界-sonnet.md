severity: minor

邊界輸入實跑找到三個小問題,都不會讓合法規則包出錯行為,沒有會擋的問題。

**finding 1:files 區塊只去整行註解,清單項目後面的行內註解不處理**
severity: minor
blocking: 否
引句:「doc = "\n".join(ln for ln in doc.splitlines() if not ln.lstrip().startswith("#"))」
`configs/ast-grep/kotlin-android/check.py:31`
- 輸入:`files:\n  - '**/src/test*/**'  # 不含 src/main\nrule:…`
- 結果:`_files_block_is_test_only` 回 False。行內註解裡的 `src/main` 被當成區塊內容,規則被誤判成不是只掃測試碼。
- 後果:`check()` 對 `samples/ancestor-named-test` 的祖先目錄守衛會跳過這條規則,守衛靜默變弱。
- 現有規則包都用單行 `files: [...]` 的寫法,目前沒有規則踩到,所以只算 minor。
- 同一輪其他寫法我都跑過,結果正確:
  - 縮排註解、頂格註解、CRLF、tab、檔尾沒換行。
  - 引號裡的 `#`(`'**/src/main#x/**'` 照常認得 `src/main`)。
  - 單行與多行 `[...]` 寫法。
- 歸因:有證據的原有漏查。修前沒有任何註解處理,行內註解同樣會誤判;這次修補只補了整行註解。我只讀了兩版程式的邏輯,沒另外取出修前版本跑。

**finding 2:決策表觸發字的 regex 裡兩個逗號都是半形,全形逗號「,」切不開,「(無)」並列檢查可被繞過**
severity: minor
blocking: 否
引句:「trig = [t.strip().strip("`") for t in re.split(r"[、,,]", norm) if t.strip()]」
`configs/ast-grep/kotlin-android/check.py:105`
- 實跑確認 regex 內容是 `[\u3001,,]`(頓號加兩個半形逗號),看起來本意是頓號、半形逗號、全形逗號。
- 輸入 `(無),foo`(全形逗號)的結果:
  - 輸出 `(['(無),foo'], None)`。
  - 沒有報「不能跟其他觸發字並列」,整串被當成一個永遠比對不到的觸發字。
- 輸入 `collectAsState,stateIn`(全形逗號)同樣整串不切。
- 這條新規則本來要擋「(無)」跟其他觸發字並列,全形逗號寫法等於繞過它。
- 型錄現有列是否有人用全形逗號,我沒逐列查。
- 歸因:有證據的原有漏查。這個 regex 在修前的行也一樣(diff 裡被刪掉的那行同款),新的 `dt_triggers` 只是原樣搬過來,但新增的並列檢查因此有了洞。

**finding 3:ast-grep 輸出不是 JSON 時,自我檢查直接 traceback**
severity: minor
blocking: 否
引句:「d = json.loads(ln)」
`configs/ast-grep/kotlin-android/check.py` 的 `scan()` 裡。這段不在本輪 diff 內,diff 只動了 `scan` 外圍的逾時處理。
- 重現:我造了假的 `sg`,`--inspect` 時回 `effectiveRuleCount=1,skippedRuleCount=0`,掃描時印 `not json` 並以 exit 1 結束。
- 指令:`python3.14 check.py --sg <假 sg>`。
- 結果:`json.decoder.JSONDecodeError` 一路噴出去,沒有走 `problems`。
- 後果:自我檢查本來就以非零結束,不會放行錯誤;只是輸出不是「<pack> 跑不起來」那種可讀訊息。
- 歸因:有證據的原有漏查。這個解析不是本輪修補引入的。

**已驗的正常路徑,結果正確**
- 缺〈來源縮寫〉節:`catalog_problems` 記一筆後往下檢查,`abbrs` 設成空集合,不會 NameError。節名相近(例如「出處簡稱」)同樣走缺節分支。
- 逾時旗標:
  - `check()` 開頭 `_TIMED_OUT[0] = False`(第 284 行)。
  - `scan` 與 `loaded_count` 共用這個旗標。
  - 逾時後兩邊都回 None,新的 `got is None` 分支會印「讀不到載入條數」,不會印「載入 None 條」。
- `dt_triggers` 的輸入結果:
  - `(無)` 的全形半形括號四種組合、反引號包住的 `` `(無)` ``、`(無)、`、`(無) ` 都解析成 `([], None)`。
  - 空字串、空白、只有 `、` 會報「觸發字不准空」。
  - `(無)、foo` 會報並列。
  - `(無)(無)` 和 `( 無 )` 被當成普通觸發字,不報錯;後者是空格造成,不算誤判。

**未驗範圍**
- 沒有取出修前版本逐字重跑。
- 沒有跑 repo 的 `-k` 測試子集。
- 沒有測 CRLF 版型錄檔。
- 沒有圖譜鏡頭的固定席,因為鏡頭計算逾時沒附節點。

臨時目錄 `/tmp/lumos-seat-work/code-kotlin規則包/邊界-sonnet` 已刪。
