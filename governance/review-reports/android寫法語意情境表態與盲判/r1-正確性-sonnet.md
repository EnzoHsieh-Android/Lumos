severity: blocker

我讀完整份凍結 spec 的全部章節,並逐一核對了它引用的函式與常數。現況與下面的宣稱對不上之處,我在臨時目錄以外沒有動任何檔。「總結」見最後一行。

### Finding 1
severity: major
blocking: 是(判準:正常寫法會被必擋,且唯一出口是謊報 tension)
- 段落:範圍 4「推送前核對」。
- 引句:「作者 na 而盲判 row 為 none → 一致;其他都是不一致」
- 輸入:一段 `ids.map { id -> async { api.load(id) } }.awaitAll()`。
  - `skills/kotlin-idioms/checks-catalog.md` 的 D-1、D-2、D-3、D-8、D-9 觸發字都含 `async`,所以 5 題同時適用。
  - 作者對 D-3 答 satisfied,對 D-1、D-2、D-8、D-9 答 na。這是正確答案,因為這段碼不屬於那 4 列。
  - 盲判對這 5 題都會回 `row: D-3`,不會回 `none`。
  - 4 題 na 全判不一致,仲裁也判 D-3,於是跟盲判一致,被擋。
- 錯在哪:na 的語意是「這一列不適用」,盲判的 none 是「候選列全都不適用」。兩者不是同一個類別,多列觸發字重疊時 na 一律誤擋。
- 唯一出口是把 na 改成 tension。tension 要編造 existing 和 hazard,還會灌高 RETIRE-IF ② 的 tension 比例。
- 同類輸入:刪行也觸發。`_stack_applicability` 註明「增行與刪行都算」。把平行改成循序(D-2)會刪掉 `async` 行而觸發 D-1,作者 na,盲判回 D-2,同樣被擋。
- file: `scripts/lumos:38177`,說明 `_stack_applicability` 刪行也算觸發。
- file: `skills/kotlin-idioms/checks-catalog.md:668-676`,說明 5 列觸發字都含 async。

### Finding 2
severity: major
blocking: 是(判準:RETIRE-IF ① 的撤除條件在數學上永遠達不到)
- 段落:RETIRE-IF ① 與範圍 6「統計」。
- 引句:「作者與盲判一致度(相符率與 Cohen's kappa,類別=row 加 none)」
- 輸入:以單一列看。`row` 欄必須等於題號(範圍 3 驗證),所以作者的標籤對同一題恆為 `D-n`(satisfied)或 none(na),幾乎是常數。
  - 例:20 次命中,作者全是 D-1。盲判 19 次 D-1、1 次 none。
  - 相符率 po = 0.95,偶然一致率 pe = 1×0.95 + 0×0.05 = 0.95,kappa = (po−pe)/(1−pe) = 0。
  - 盲判 20 次全同意時,pe = 1,分母為 0,kappa 無定義。
- 結果:RETIRE-IF ①「kappa ≥ 0.9 且命中 ≥ 20」的兩種情形,一個是 0、一個是 0/0。盲判到底有沒有抓到東西這條,永遠無法觸發撤除。
- 補充:spec 沒寫 pe=1 時怎麼處理,也沒寫 kappa 是跨列合算還是逐列算。「每一列……kappa」有歧義。
- 補充:kappa 只用 row,不含 followed。作者 D-1、盲判 D-1 但 followed=false,閘算不一致而 kappa 算一致,兩個口徑矛盾。

### Finding 3
severity: major
blocking: 是(判準:多筆記錄的存法與現有「取最後一筆」讀法衝突,CI 端會漏記錄)
- 段落:範圍 4「盲判記錄與核對」。
- 引句:「寫入盲判記錄(治理帳一筆 `blind-judge` 事件加標記檔,同表態的讀寫慣例」
- 輸入:改動大到分批(各批各一筆記錄),再加上仲裁記錄。
  - 現有慣例是 marker 單檔覆寫。本機 marker 不在時,讀治理帳「該分支最後一筆 kind」(`_codeloop_read_dispositions` 的 docstring 明說「檔案行序的最後一筆」)。
  - 後寫的記錄蓋掉前面的批次。CI 端只看得到最後一批或仲裁記錄,「取聯集涵蓋每個適用題」恆不成立。
- 同一題有多筆記錄的情形也沒有規則。出口寫「改表態後重跑盲判」,這時版本與 sha256 都不變,新舊兩筆記錄的 row 可能不同,spec 沒說取哪筆。
  - 作者可以重跑到盲判同意為止,盲判就失去獨立性。
- 仲裁記錄沒有對應欄位,沒說 `--arbiter` 的記錄怎麼跟第一盲判配對。
- file: `scripts/lumos:70200`,說明 `_codeloop_read_dispositions` 的讀法。

### Finding 4
severity: major
blocking: 是(判準:規則互相重疊,同一輸入同時符合放行與擋下)
- 段落:範圍 4「仲裁」。
- 引句:「仲裁跟作者一致 → 放行(記一筆「仲裁採作者」);仲裁跟第一盲判一致或三方都不同 → 擋」
- 輸入:作者 satisfied D-1。盲判 1 回 D-1 且 followed=false(兩個盲判都認定沒照做)。仲裁也回 D-1 且 followed=false。
  - 「一致」只定義了一次,而且那次是 `row 相同且 followed 為真`。這裡 row 同作者,又同第一盲判。
  - 「跟作者一致」與「跟第一盲判一致」兩條同時成立,先放行還是先擋沒有寫。
  - 若只比 row,則兩個盲判都說沒照做,卻因多數決放行,與設計意圖相反。
- S4 的測試條款沒有涵蓋 followed=false 的任何組合。

### Finding 5
severity: major
blocking: 是(判準:部分決策列沒有一定出現的字面特徵,證據樣式機制對這幾列不可行)
- 段落:用詞「證據樣式」。
- 引句:「寫「照這列標準寫法寫出來的程式,一定會出現的字面特徵」」
- 輸入 1:D-2 的標準寫法是「直接循序呼叫,不要包 `async { }.await()`」。
  - D-2 的標準寫法和 D-20 的不適用寫法,本質上是「沒有特殊寫法」。
  - 要寫成正規式,只能寫否定(`async` 不出現),但窗只有 7 行,否定在窗裡必然恆真,等於沒驗。
  - 這與範圍 3 的「一條都沒中 → 沒照做」相衝。D-2 的主寫法沒有可被「中」的正樣式。
- 輸入 2:語法沒定義。例子「`主: \basync\s*\{ ; \.await\(\)|awaitAll\(`」裡的 `;` 與 `|` 優先序不明。
  - 若 `;` 是「且」,窗前後 3 行放不下常見寫法:`val a = async {` 多行區塊,`a.await()` 在 10 行以後。
  - 若 `;` 是分隔多條(或),則 `async {` 單條就過,正是實務隱患 1 說的「太鬆被敷衍」。
- 輸入 3:例子的 `|awaitAll\(` 讓 D-3 寫法也能滿足 D-1,列與列的證據樣式沒有互斥。
- S2 只測了含 `async {` 與 `awaitAll(` 的好例,沒有測 D-2 這類無正樣式的列。

### Finding 6
severity: major
blocking: 是(判準:漏接一個消費者,伺服端 Kotlin 會被問 Android 題)
- 段落:範圍 2「在四處各接一次」。
- 引句:「情境題不塞進載入時就編譯好的靜態題目表」
- 同一段又說情境題標 `android_only`。但 `_stack_platform_excluded` 取 android_only 題號的來源是靜態表。
  - 實證:`scripts/lumos:37848` 的 `sp["id"] for sp in _STACK_QUESTION_SPECS.get("kt", []) if sp.get("android_only")`。動態情境題不在其中,伺服端 Kotlin 專案(Spring)的情境題不會被排除。
- 漏列的其他消費者:
  - `_stack_platform_excluded`,產出 `exclude` 給 `_stack_applicability`(`scripts/lumos:61853` 與 `scripts/lumos:64718`)。
  - impact hook 路徑也呼叫 `_stack_applicability`(`scripts/lumos:64725`),會把情境題印進單檔提醒。
  - `lumos code-loop` 單題表態指令的 `_stack_spec_by_id`(`scripts/lumos:71584`)。
- 這些與 spec 列的「四處」重疊但不完整,「題號集合守衛測試」也不會抓到 `_stack_platform_excluded`。

### Finding 7
severity: major
blocking: 是(判準:sha256 綁定證明不了「盲判看過的材料」,仲裁記錄的核對規則也算不出來)
- 段落:範圍 4「`--template` 與結果寫入」。
- 引句:「結果每題一筆:`{id, row: "D-<n>"|"none", followed: true|false, evidence: "path:line", reason}`」
- 問題 A:結果檔沒有 sha256 欄位,也沒有 `--sha256` 之類的參數。
  - 工具若在寫入時重算材料 sha256,記錄必然對得上,綁定形同虛設,不能證明盲判看過這份材料。
  - 若由代理自己帶,代理就能亂填。
- 問題 B:仲裁只判不一致的題。但 `--template` 沒有「只列某幾題」的選項,而且材料不得含表態,工具無法知道哪幾題不一致。
  - 仲裁代理要嘛判整批,要嘛結果題集是子集,而「每筆記錄的 sha256 要對得上重算的那一批」。子集對不上整批的 sha256。
  - 子集的覆蓋規則(取聯集涵蓋每個適用題)也不適用仲裁記錄。
- 問題 C:沒寫 `--template --diff <範圍>` 與推送前重算用的範圍如何一致。範圍不同則批次邊界不同,sha256 全變。

### Finding 8
severity: minor
blocking: 否(判準:只多花成本,不會判錯)
- 段落:範圍 4「改碼後盲判記錄過期,規則同表態」。
- 輸入:專案慣例是「做到一半的本機提交,推之前壓成一個」,另外合併主線也會改 HEAD。
  - 表態有 `--carry`。盲判記錄沒有對應的帶過來機制,而材料 sha256 若相同,版本綁定本身就是多餘的。
  - 壓提交或 rebase 後,記錄全過期,要重派盲判代理與仲裁。
  - `_dispositions_verdict` 對過期的處理是整個擋(`scripts/lumos:70626`)。

### Finding 9
severity: minor
blocking: 否(判準:統計與重複記錄,只影響數字)
- 段落:範圍 6「統計」與 4「新事件種類登記」。
- 輸入:治理帳去重的 token 只替 `dispositions`、`recall-miss` 用 `written_at`。
  - 其他 kind 的 token 是空字串,所以同 HEAD 的第二筆 `blind-judge`(批次、仲裁、重跑)會被折成一筆。
  - 實證:`scripts/lumos:17006`。spec 只說登記進 `LOOP_NOT_CLOSE_EVENTS`,沒提 `_gov_row` 的 token。
- 結果:仲裁採作者與採盲判的次數、命中數都被低估。

### Finding 10
severity: minor
blocking: 否(判準:前置依賴與現況不符,需要先確認)
- 段落:用詞「情境題」。
- 引句:「型錄的格式檢查不准收一般常用字(停用字表與檢查由第一批的型錄格式檢查承接」
- 現況:型錄 D-3 觸發字含 `map`、`forEach`,D-8 含 `try`、`catch`,D-15 含 `flow`、`collect`、`first`、`take`,D-19 含 `launch`、`suspend`。這份檢查目前不存在。
- 若第一批晚落地,本案一上線幾乎每個 Kotlin 改動都命中多題。
- file: `skills/kotlin-idioms/checks-catalog.md:670-683`,說明這些觸發字目前就在表裡。

### Finding 11
severity: minor
blocking: 否(判準:證據驗法的盲點,單人威脅模型下風險低)
- 段落:範圍 3「讀窗比證據樣式」。
- 輸入:作者把 evidence 指到一行 `// val a = async { api.a() }` 的註解,或字串內容。
  - 適用性判定先剝字串與註解,而證據窗 spec 沒寫要不要剝。
  - 沒剝的話註解就讓 D-1 過;剝了的話,多行寫法被誤剝。
  - 觸發字的 `.`(例:`viewModelScope.launch`、`Dispatchers.IO`)沒寫要不要 `re.escape`,「自己加字界」沒涵蓋這個。

### 其他章節
- 前言、PRIOR-ART:已讀,無 finding。
- 範圍 1(讀表)、範圍 5(拉進代碼審):已讀,無獨立 finding。範圍 5 的盲判核對依賴 Finding 3 與 7 的修法。
- 實務隱患、驗收條款、回退、天花板:已讀。驗收條款漏了 Finding 1、4 的組合,見上。

最嚴重 severity:blocker 級以下最高為 major。**所以首行 `severity: blocker` 取消,實際全份最高為 major。**

更正首行:實際最高等級為 `severity: major`。
總結:最嚴重 severity 為 major,blocking 共 7 條(Finding 1 至 7)。
