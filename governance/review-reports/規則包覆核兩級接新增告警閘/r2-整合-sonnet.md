severity: minor

回報語言:繁體中文。我沒有改 repo 裡任何檔,也沒有跑不帶 `-k` 的測試。實驗用的目錄(ast-grep 0.51.1、主線規則包副本、臨時 git repo `e2e/`)都在 `/tmp/lumos-seat-work/規則包覆核兩級接新增告警閘/整合-sonnet/` 底下,交給編排者收貨後刪。

## 端到端走一遍的結果

我在臨時 repo 照新範本宣告三條 ast-grep(`sgconfig.yml`、`sgconfig-review.yml`、`sgconfig-hints.yml`),用主線的 `lumos lint-new` 實跑:

- **推送前新增告警閘:** 一筆覆核級命中(`kt-livedata-setvalue-background`)和一筆提示級命中(`kt-value-assign-background`)都被擋。SARIF 的 level 是 note,閘照收。擋下訊息會印出可直接貼的 `lint-waive` 指令。
- **放行:** `--note` 少於 10 字會被拒;寫夠後放行,重跑變 clean。`lint-waive --list` 會標出「AI 放的、還沒人看過」。
- **零命中輸出:** 三份設定掃乾淨的檔都吐出合法 SARIF(`results: []`),不會被當成「跑不出可解析結果」。
- **lint-check:** 三條宣告都顯示健康,沒有重複或多餘宣告的檢查。
- **doctor / 治理帳:** 本席沒有單獨跑 doctor。放行清單與 AI 待看提醒在 `lint-waive --list` 看到。
- **註冊面:**
  - 安裝器沒有複製 `configs/ast-grep`:`install.sh` 裡完全沒提到它。
  - 工具自裝檔清單也不含它:`_VENDORED_TOOLKIT` 不列。
  - 消費專案走 `$HOME/harness/lumos-toolchain/configs/...` 直接讀工具鏈 clone。
  - 所以 `rules-unwired/` 和 `sgconfig-unwired.yml` 不需要在安裝器或自裝檔清單登記。
  - 規則包測試的複本 `_ktpack(copy=True)` 是整個 `copytree`,會自動帶到新目錄。
  - 型錄自檢不會把 `rules-unwired/` 裡的 (b) 類規則當問題,只要它們是 hint 或 info。

## F1 做 6 的前提講過頭:推送前掛鉤、CI、代碼審的分級都已經是 --no-lint
severity: minor
blocking: 否 判準:改動本身正確且無害,只是理由與「守衛面」定位寫得比實況重,屬文字層缺陷。
spec 段落:範圍做 6、實務隱患末條「三處都是守衛面」。
問題:`pitfalls --diff` 帶 lint 只出現在人手動跑(代碼審手冊第一步)與 `capture-counts --from-pitfalls` 兩條路。真正決定要不要過審的路徑都帶 `--no-lint`,所以「被逼代碼審」並不是強制發生。做 6 因此是讓手動輸出對得上,不屬守衛面,「放行後少審」的風險也不成立。
佐證:
- 我實測:同一範圍 `pitfalls --diff` 帶 lint 時,放行並提交後仍是 `tier: high`(閘是 clean);加 `--no-lint` 是 `tier: standard`。
- file: `scripts/hooks/pre-push:567` 的分級呼叫帶 `--no-lint`。
- file: `.github/workflows/ci.yml:93` 同樣帶 `--no-lint`。
- file: `scripts/lumos:75201` 的 `_codeloop_pitfalls_tier` 同樣帶 `--no-lint`。
- ⚠ 另有窄缺口:`pitfalls` 的 claims 沒有指紋欄,指紋沒變的命中(例如整段搬移)若起始行落在新增行上,手動分級會是 high,但閘是 clean、沒有東西可放行。我沒實測搬移情境。
引句:「`pitfalls --diff` 也逐條跑 lint 宣告,不看放行檔,任何一筆新命中就判高風險,作者已放行仍被逼代碼審」

## F2 做 5 用「禁兩個檔名」去補一份「放行整個目錄」的白名單
severity: minor
blocking: 否 判準:只會讓收工多跑檢查,沒有安全影響,屬設計脆弱點。
spec 段落:範圍做 5。
問題:`_lint_wt_allow` 現在的白名單是「`--config` 真實路徑在 `configs/ast-grep/` 底下就行」。spec 只加兩個檔名的排除。
- 若有人把 `sgconfig-unwired.yml` 誤宣告,或日後出現別的 `sgconfig-*.yml`,收工仍會每回合跑。
- spec 沒寫比對方式。既有程式對目錄比對特地處理了 macOS 大小寫不分與符號連結(用 `os.path.samefile`),單用字串檔名比對會被大小寫變體繞過。
- 較穩的寫法是只准真實路徑指到 `kotlin-android/sgconfig.yml`。
佐證:file: `scripts/lumos:41184` 起的 `_lint_wt_allow`;其 `inside` 判斷與 `samefile` 那段只防「是否落在工具鏈目錄」。
引句:「`_lint_wt_allow` 對 `--config` 值是規則包 `sgconfig-review.yml` 或 `sgconfig-hints.yml` 的命令回」

## F3 做 7 的文字同步清單沒列齊
severity: minor
blocking: 否 判準:殘留的只是過時說明文字,不影響行為,但與 S 條款綁測試的那句會與新行為不符。
spec 段落:範圍做 7。
問題:我在主線 `git grep` 出下列地方仍在講「預設不接」「接上前不擋」「要靠盲判」,spec 沒列:
- `rules-review/` 五支 yml 的檔頭與內文註解,共 7 處。例:`rules-review/api.yml:1`、`data.yml:13`、`state.yml:124`。
- 兩支 `review-fp-*.kt` 樣本第一行註解。
- `check.py:777` 的「給盲判對照」註解。spec 只列 `check.py` 開頭三級說明與 `REVIEW_FP_PREFIX` 兩處。
- [[Systems/kotlin規則包]] 檔案節:
  - 「`rules/`、`rules-review/`、`rules-hints/` 底下的 yml 依型錄主題分檔」那行沒補第四個目錄。
  - `sgconfig-review.yml` 那行的「要靠盲判排除」只列了「接上前範本不接」那半。
- Projects/Android協程與API寫法機械檢查標準_計劃:
  - 第 73 行「hint 級規則預設不接推送閘」。
  - 第 126 行「只准提示級」。
  - [S2] 條款(綁 `t_kotlin_rulepack_messages_cite_catalog`)寫「引用(出處不全)列的規則 應 是提示級」,與新規則「只准放 rules-unwired/」不符。
  - spec 只說「兩句改指本計劃」。
- Projects/Android寫法型錄逐列查證_計劃 第 36、48 行:仍寫「應降到 `rules-hints/`」。
- 型錄格子數我核對過,正確:「批一(只有提示級規則,預設不接)」表內 40 格(全文 41 次,多的 1 次是第 11 行定義);「接上前不擋」7 格;覆核級卻標「批一」3 格。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/Android協程與API寫法機械檢查標準_計劃.md:47,73,104,126`(`git show Lumos/main:` 讀出);file: `configs/ast-grep/kotlin-android/check.py:777`。
引句:「[[Systems/kotlin規則包]]:`about_code` 補 `sgconfig-unwired.yml` 與 `rules-unwired/`(用 `lumos append`)」

## F4 既有測試「一條規則都沒讀到要報」在第四個目錄加入後會翻紅
severity: minor
blocking: 否 判準:實作時必然被測試抓到,不會漏進主線,但 spec 沒預告要改測試。
spec 段落:範圍做 2。
問題:`CONFIGS` 變四組後,那個測試的迴圈只清空 `rules`、`rules-review`、`rules-hints` 三個目錄的 yml。`rules-unwired/` 仍有規則,`load_rules()` 讀得到,就不會報「一條規則都沒讀到」,測試翻紅。spec 要改的是訊息文字,沒提這個測試的迴圈。改 `test_lumos.py` 還要走簽名流程,應預先寫進實作步驟。
佐證:file: `scripts/test_lumos.py:126457`(`for d in ("rules", "rules-review", "rules-hints")`)。
引句:「`CONFIGS` 加第四組;`_DIR_SEVERITY` 讓 `rules-unwired` 收 hint 與 info(試水溫的覆核級規則也放這裡)」

## F5 (b) 類「還沒量過的新規則」沒有型錄標法,也沒有升級路徑
severity: minor
blocking: 否 判準:現在 (b) 類是零條,風險在日後;但標法與升級路徑不寫,試水溫流程會再次變成口頭。
spec 段落:範圍做 1、做 2、做 7。
問題:
- 型錄通電批次欄的值定義(第 11 行)只有「批一=會擋的規則已上線」「批一(只有提示級規則,預設不接)」等。spec 只說 8 列保留「預設不接」,沒定義「規則在 `rules-unwired/` 的 (b) 類列」該寫什麼。
- 型錄自檢沒有「該列的規則都在 unwired 時標籤不能寫批一」這類對照,標籤與規則位置會漂移。
- `rules-unwired/` 只收 hint 與 info。打算最終升成 warning 或 error 的新規則,試水溫時得先改嚴重度,搬出去時再改一次。
- 32 格要改寫、7 格「接上前不擋」要「照新接法改」,新文字長什麼樣沒給。我核對過這 7 格裡 STATE-16 同列另有提示級規則 `kt-value-assign-background`,所以格子要同時講覆核級與提示級。
佐證:
- 第 11 行定義與 `awk` 逐格核對:API-17、STATE-1、STATE-7、STATE-16、CO-44、DATA-10、DATA-36 這 7 格寫「語意覆核級(…接上前不擋)」。
- file: `configs/ast-grep/kotlin-android/check.py:664-665`、`check.py:392-394`。
引句:「(b) 還沒在真專案量過誤報的新規則。」

## F6 預算不夠時 ast-grep 命令是「擋下」,不是「略過」
severity: minor
blocking: 否 判準:邊角情形(同一專案有慢工具先吃預算),但範本旁的說明會讓人以為會安靜略過。
spec 段落:範圍做 4。
問題:閘的總預算預設 300 秒,單條保底 30 秒。剩餘預算不足保底的命令記成 `undone kind=budget`,而 `_lint_new_classify` 把非環境類的未跑到判為硬擋。範本排序只決定誰先被餓死,不會讓提示級「讓出」。已宣告 detekt 的 Kotlin 專案,若 detekt 先吃光預算,排在後面的覆核或提示級 ast-grep 會讓推送被擋,逃生門只有人工放行。
佐證:file: `scripts/lumos:43275-43293`(`left < cfg["per_cmd_floor_sec"]` 分支)、file: `scripts/lumos:43012-43030`(`hard_undone` 判擋)、file: `scripts/lumos:42400-42406`(預設值)。
引句:「`sgconfig.yml` 那條排第一,預算不夠時先跑會擋的那份」

## F7 舊專案怎麼到新範本:沒有消費端看得到的入口,重複宣告也沒人偵測
severity: minor
blocking: 否 判準:spec 已明說不自動改消費專案,缺的是可偵測性,不影響已接專案的行為。
spec 段落:範圍做 4、不做末條。
問題:
- 新範本只存在於 [[Systems/linter精選目錄]] 這篇工具鏈圖譜。`skills/`、`lumos doctor`、`lint-check` 都沒有 Kotlin ast-grep 範本或提醒:`scripts/lumos` 裡只有 detekt 與 Android Lint 的 advisory,沒有 ast-grep 的。舊範本的消費專案不會被告知有三條,也查不出自己停在單條。
- 「同一筆命中會列兩次」我實測屬實,但只在兩條命令字串不同時發生(例:`$HOME` 與絕對路徑,或多一段 `../`)。字串完全相同時,閘會去重,只列一次。我實跑兩條字串不同的重複宣告,同一命中列兩次、擋下數字膨脹成「2 條」。
- `lint-check` 只驗格式,沒有重複宣告檢查,所以這句只能靠人讀。
佐證:file: `scripts/lumos:41655`(`cmd_lint_check` 只有 detekt、Android advisory);臨時 repo `.lumos/lint.json` 四條宣告實測。
引句:「以前照舊範本另加過 `sgconfig-hints.yml` 宣告的,刪掉舊那條,不然同一筆命中會列兩次」

## F8 誤擋量量測與撤除條件的輸入沒定義清楚
severity: minor
blocking: 否 判準:屬量測與撤除條件的完整度,不影響機制行為。
spec 段落:實務隱患第 1 項、RETIRE-IF。
問題:
- 型錄 TEST 主題的規則(覆核與提示級裡至少 8 條,如 `kt-test-no-assertion`、`kt-test-verify-only`)在 `include_test_paths` 預設為空時不會掃測試檔、永遠不響。「54 條共量到幾筆」要寫明有開沒開。
- 「單次推送新增命中」的推送內容沒定義,不同推送可差一個數量級。
- RETIRE-IF 用 `lint-waive --list` 數「新增命中少於 10 筆」,但該指令只列被放行的,被擋後直接修掉的不在裡面。「八成理由是誤報」也是自由文字,不是機器可算的度量。
佐證:file: `scripts/lumos:42409-42415`(`include_test_paths` 預設 `frozenset()`)、`Systems/linter精選目錄.md` 的「測試檔也要掃」條;我實跑 `lint-waive --list` 只輸出放行紀錄。
引句:「任一專案單次推送新增命中超過 20 筆,先只接覆核級、提示級那條宣告延後」

## 固定席:對 [[Systems/kotlin規則包]]、[[Systems/linter精選目錄]] 的行為與合約

- 兩篇節點都是 0 行 KEY、0 條合約(派工附錄寫「0 條合約」),所以沒有 ★INVARIANT★ 類條款會被破壞。
- [[Systems/kotlin規則包]] 的 `WHY`(出處不全只准提示級,綁 `t_kotlin_catalog_rows_wired`)與 `RULE`(誤報超過一成降提示級,`[retire:人裁]`):spec 明講要改字。我確認改後語意仍成立,但 `RULE` 行改字後需要重新確認 `[confirmed:]`,spec 沒寫。判:不破壞,有此手續缺漏。
- [[Systems/linter精選目錄]] 的「提示級規則預設不接」:spec 明改。判:會被推翻,是設計意圖。
- 提到的 `t_kotlin_rulepack_messages_cite_catalog` 與 `t_kotlin_catalog_rows_wired`:我核對過測試主體(假規則帶 `dir` 與不帶 `dir` 兩種寫法),做 2 的「缺鍵照不在 unwired 算」與它們相容。判:不影響測試意圖。

總結:最高等級為 minor,blocking 共 0 條
