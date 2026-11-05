severity: minor

整份只有一條會讓讀型錄的人被誤導的小問題。型錄數字、各列的級別、知識筆記的句子和測試名都對得上程式,兩篇筆記的 lint 都是 0 問題。

## finding

severity: minor
blocking: 否

**DATA-10 的實測狀態欄抄了 API-17 的理由,「OkHttp 5 寫法」跟 DataStore 無關。**

引句:「代碼審 r3 實測形狀分不出對錯(OkHttp 5 寫法、try 裡的終端操作)改放語意覆核級;這列有規則在語意覆核級(info)」

- 位置:`skills/kotlin-idioms/checks-catalog.md` 的 DATA-10 列,對照 `configs/ast-grep/kotlin-android/rules-review/data.yml` 的 `kt-datastore-read-no-catch`。
- 規則檔的搬移註解只寫了「try/runCatching 區塊裡接的終端操作(collect、toList、single…)列舉不完」,沒有 OkHttp。「OkHttp 5 寫法」是 API-17 的原因,DATA-10 這列把整句貼了過去。
- 失敗場景:下一個人看 DATA-10 會去找一個不存在的 OkHttp 5 誤報。理由欄跟規則實際的搬移原因對不上。
- 修法:把括號改成「try/runCatching 裡的終端操作」。
- 歸因:有證據的修復回歸。修前 DATA-10 該欄沒有這句,是這輪新寫的。查證是 `git diff` 比對這一列,加上讀規則檔註解。

## 已驗項目

1. **規則包條數**:`rules/` 有 30 error + 115 warning,`rules-review/` 有 12 info,`rules-hints/` 有 50 hint,合計 207,跟〈統計〉的「207(30/115/12/50)」完全一致。
2. **「被會擋的規則守到的列數」**:我照字面口徑寫程式數了一次。條件是通電批次欄含「告警帶寫法=批一」,而且現成規則欄或實測狀態欄提到至少一個 `rules/` 底下的規則 id。結果 129,跟型錄寫的 129 一致。總列數也是 473。
3. **改動的五列級別註記**:API-17、DATA-10、STATE-4、CO-44、DATA-36 寫的規則所在級別都跟實際目錄一致。
   - 前四列的規則實際在 `rules-review/`。
   - STATE-4 寫「kt-statein-eagerly(語意覆核級 info,不擋;同列另兩條才擋)」,另兩條 `kt-statein-lazily-or-no-timeout`、`kt-statein-lazily-in-viewmodel` 確實在 `rules/state.yml`。
   - CO-44 的 `kt-bg-dispatcher-touches-view`、DATA-36 的 `kt-worker-retry-unbounded` 也在 `rules-review/`。
4. **有沒有別的列漏註**:`rules-review/` 的 12 條規則,每一條在型錄中出現的列都帶「語意覆核級」註記,沒有漏的。這 12 條涵蓋 API-11、API-17、TEST-5、STATE-16、STATE-7、STATE-1、STATE-4、CO-44、DATA-36、DATA-10。
5. **`kotlin規則包.md` 的 `dt_triggers` 說法**:跟 `check.py` 一致。
   - 「(無)」全形半形括號都認(先正規化再比對)。
   - 「(無)」單獨出現時回空清單。
   - 跟其他觸發字並列會報「不能跟其他觸發字並列」。
   - 格子空白會報「觸發字不准空」。
   - `test_lumos.py` 第 125176 到 125179 行有對應的檢查。
   - `dt_triggers` 目前只有 `check.py` 自己用。筆記說「第二、三批要走 `dt_triggers`」是寫給日後的人,不是現況描述。
6. **測試名**:`pitfalls-code-loop.md` 的 `t_rulepack_sample_dir_skips_risk_scan` 在 `test_lumos.py` 第 125247 行存在。舊名 `t_kotlin_rulepack_samples_not_scanned_as_code` 在 `docs`、`scripts`、`skills`、`configs` 都沒有殘留。`kotlin規則包.md` 引用的 `t_kotlin_catalog_rows_wired`、`t_kotlin_rulepack_messages_cite_catalog`、`t_kotlin_rulepack_samples` 也都存在。`-k rulepack` 的 38 個測試全過。
7. **筆記的檔案引用**:`governance/review-reports/code-kotlin規則包/cap-retro.json` 存在。

## 三問(修補鏡頭)

- **原問題的修復效果**:「統計數字重算」和「搬到覆核級的列補註」這兩項,修後我重算都對得上。修前證據我沒另外取出來比,所以歸因只限修後狀態成立,未判定修前是否錯過。
- **相鄰路徑**:別列(STATE-1、STATE-7、STATE-16、API-11、TEST-5)原本就帶覆核級註記,沒被破壞。
- **新發現的修前修後**:DATA-10 那句理由是這輪新增,修前沒有,見上方 finding。

未驗範圍:我沒有重跑修前版本的 `check.py`,也沒對真專案重跑規則。
