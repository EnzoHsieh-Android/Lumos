severity: major

固定席筆記:派工詞與 hook 都沒附,所以「固定席逐條判」沒有對象,不適用。

已讀,無 finding 的節:frontmatter 與 WHY 摘要、依據、PRIOR-ART/RETIRE-IF/REVISIT、現況、設計原則、前綴表、不收清單、讓 AI 知道該寫什麼(第 1 到 5 點)、不溯及既往怎麼做、已裁、天花板、不做、實務隱患、合約候選、審計修正紀錄。

這些節內的交叉引用我逐個核對過,目標都存在:〈天花板〉第 2 條、〈分期〉、〈回退〉、〈讓 AI 知道該寫什麼〉第 4 點、已裁第 6 題、S1/S3/S7。

另外查證了 r1 的舊洞:
- 判過時的時機已接上 `_drift_probe_check` 的候選篩選,補上。
- 值內 `]` 已有切法規則,補上。
- `init` 預設值已移除,補上。
- 「`::` 切法」只補了文字規則,沒跟共用函式對上,見 R2B2。
- 「求值器」補成了表格,但邊界沒定義,見 R2B4。

---

**R2B1 「判不了」一詞同時指兩件相反處理的事**
severity: major
blocking: 是——照字面實作會讓非 Python 專案的欄位被擋,或讓基礎設施失敗被放行,兩種都是壞行為。
1. 輸入:Kotlin、Swift、TypeScript、Dart 專案寫了 `[count:app/Models.kt::X=4]`。
2. 〈欄位 v1〉求值欄和 S5 說:讀不出來的「起點終點都判不了就不擋」。
3. 〈欄位 v1〉最後一條「判不了」卻說「照存量漂移檢查既有的處理」。既有處理是:判不了算要處理,`block` 模式下擋推送。`cmd_drift_check` 的 docstring 寫明「放行等於一條繞過的路」。`_drift_probe_judge` 回 `None` 就進 `unknown`,`_drift_check_c` 裡 `not must and not unknown` 不成立就走 `_drift_report_must`,最後 `return 1`。
4. 照字面實作這兩句,實作者會把「語意上讀不出來」也塞進同一個 `None` 通道,結果是所有非 Python 欄位在每次推送都被擋。
5. 反過來,為了讓 S5 成立,實作者可能把「git 讀不出、預算用完」也當成放行。
6. spec 沒把「語意判不了(求值器不認)」和「基礎設施判不了(git、預算)」分成兩個詞。
引句:「照存量漂移檢查既有的處理(git 逾時、淺複製、預算用完時的嚴格判定沿用它的設定),不另訂。」
佐證:`scripts/lumos:29777`、`scripts/lumos:28630`、`scripts/lumos:29779`

**R2B2 欄位路徑「不帶副檔名」被判寫壞,和本 repo 自己的無副檔名主程式、共用切法衝突**
severity: major
blocking: 是——工具鏈自己的主程式 `scripts/lumos` 沒有副檔名,「工具鏈也擋」的欄位,對它既不能切、又被提醒寫壞。
1. 輸入:`[lives:scripts/lumos::cmd_search]`,或 `Makefile`、`Dockerfile`、shebang 腳本。
2. 〈欄位 v1〉的切法規則是「第一個帶副檔名的路徑之後的 `::`」。無副檔名時規則不成立。
3. 〈寫法提醒〉又把「路徑不帶副檔名」列入欄位寫壞。
4. 既有探針明確支援這類檔:`_drift_probe_code_path` 收「沒副檔名但開頭是 `#!`」的檔,`_drift_probe_path_warn` 還為 Makefile 寫了豁免。
5. 共用的 `_DriftProbeTree.one` 走 `_drift_cond_split`,用 `rsplit("::", 1)` 從最後一個切。
6. S6 要求 `src/net.rs::Client::connect` 照「副檔名之後」切。這要嘛改共用切法,連帶改變既有 `when-symbol` 的語意與其寫壞警告;要嘛有兩支切法。
7. spec 兩條都沒說。
引句:「路徑不帶副檔名、寫在不評估的地方 → 提醒。」
佐證:`scripts/lumos:28241`、`scripts/lumos:28085`、`scripts/lumos:28649`

**R2B3 `[lives:]` 在非 Python 檔判的是「名稱出現過」,帶 `::` 的限定名永遠起點不成立**
severity: major
blocking: 是——非 Python 的錨點判成「還活著」的條件過寬,S6 的 Rust 例子根本無法成立。
1. 輸入一:TypeScript 檔刪掉 `function dispatch`,同檔註解、呼叫點或 import 還留著 `dispatch`。
   - `_defines` 對非 Python 只做 `(?<![\w])dispatch(?![\w])` 全文比對,所以 `lives` 仍成立,不擋。
   - 〈天花板〉第 5 條只承認「名稱還在、行為變了」,沒承認「定義沒了、字還在」。
2. 輸入二:Rust 的 `src/net.rs::Client::connect`。
   - Rust 定義寫成 `impl Client { fn connect }`,檔內不會出現字串 `Client::connect`,只有呼叫端才會。
   - 所以寫在定義檔裡的錨點,起點就判「沒有」,是死條件,又不提醒。
3. Kotlin 反引號名稱含空白、Ruby 的 `Foo#bar` 同理。
引句:「沿用回頭條件探針的符號判定(同一支 `_DriftProbeTree`;Python 用語法樹、其他語言用文字)」
佐證:`scripts/lumos:28379`(`_defines`)、`scripts/lumos:28392`(`one`)

**R2B4 數量與值的求值器邊界沒定義,照字面做會誤判**
severity: major
blocking: 是——S4「新寫的在終點不吻合就擋」會把寫對的欄位擋掉,而且找不到可修的寫法。
1. 輸入:`MAX = -1`。
   - 負數在語法樹裡是 `UnaryOp`,不是 `Constant`,規則寫的「整數、浮點、字串、布林」沒包含它。
2. 輸入:`TIMEOUT = 60 * 5`、`X = [*BASE, "a"]`、`{**A, "b": 1}`、`{1, 1}`。
   - 只做 `len(elts)` 會算出錯的成員數。
   - 規則只說「程式組出來的」判不了,沒說含展開或重複成員的字面值。
3. 輸入:`[value:app/c.py::NAME=...]` 的值怎麼寫。字串帶不帶引號?`True` 還是 `true`?`0.1` 和 `0.10`?`1_000` 和 `1000`?規則只說「值是字面值」,沒說比對的是字串化的值還是 `literal_eval` 之後的值。
4. 輸入:名稱定義在 `if sys.platform == ...:` 或 `try/except` 裡。
   - 既有的 `_drift_py_names` 只收 `tree.body` 直接的指派,所以名稱「不見了」。
   - 規則「終點那個名稱不見了 → 擋」加上 S4,會把新欄位永遠擋掉。這種寫法在程式裡明明存在,只是不在模組頂層。
5. 輸入:同名清單先 `X = [a, b]` 再 `X += [c]` 或 `X.append(...)`。
   - 求值器讀到 2,實際是 3。
6. 輸入:Enum 的成員數。
   - 靜態語法樹分不出別名、`_ignore_`、`auto()`,也認不得「繼承自自訂 Enum 基底」的類別。
引句:「Python 用語法樹讀模組層的指派——清單、元組、集合、字典字面值的成員數,Enum 類別的成員數,常數字面值(整數、浮點、字串、布林)」
佐證:`scripts/lumos:28098`(`_drift_py_names` 只收 `tree.body`)

**R2B5 既有的 HTML 數量標記一夕變成推送閘,跟 S1 和「舊筆記完全不受影響」矛盾**
severity: major
blocking: 是——spec 自己承諾的「不溯及既往」被這一條打破,而且重算用的檔案宇宙和 doctor 不同。
1. 輸入:本 repo 已有的 `<!--lumos:count=… re=… in=…-->`,在 `Projects/兩席相反時端出張力_計劃.md`、`Projects/棧別提問表態閘_計劃.md`、`Projects/graph-engineering掃描2026-08-19_調研.md` 等舊筆記裡。
2. 〈欄位 v1〉說存量漂移檢查「也呼叫」重算函式,起點吻合、終點不吻合就擋。
3. 但 S1 和〈不溯及既往〉都說「沒寫欄位的筆記完全不受影響」。這些標記不是 `[count:]` 欄位,卻會被新閘評估。舊標記裡仍吻合的,下次有人改到 `in=` 範圍的檔,推送就被擋。
4. doctor N 用 `os.walk` 掃工作目錄,含未追蹤與被忽略的檔,跳過 `CODE_SKIP_DIRS`,以 `errors="ignore"` 解碼。
5. 存量漂移檢查讀的是起點與終點兩個提交的 git 樹。同一個標記可能 doctor 說對、推送說錯。
6. doctor 的上限(4000 檔、40MB)在 doctor 裡只出提醒。到了推送閘,依 R2B1 的「判不了」處理,是擋。
7. 一個含 `in=**/*.cs` 的標記在大 repo 會讓每次碰到 `.cs` 的推送都被擋。
8. 還有一個小處:S7 說「doctor N 與存量漂移檢查 應 呼叫同一個重算函式」,但doctor 現在是內嵌在 run_doctor 的區塊,不是函式,沒有檔案來源抽象就無法在兩個提交上跑。
引句:「本案把 doctor N 段裡內嵌的重算抽成共用函式,存量漂移檢查也呼叫它」
佐證:`scripts/lumos:3017`、`scripts/lumos:3018`、`docs/lumos-toolchain-knowledge/Projects/兩席相反時端出張力_計劃.md:49`

**R2B6 「受總時間預算管」對正規式與語法樹解析是假的**
severity: major
blocking: 是——一條壞正規式或一支大檔,可在推送閘與 CI 上掛住。
1. 輸入:標記 `re=(a+)+$ in=**/*.py`,或欄位指向超過 4MB 的 Python 檔。
2. 〈欄位 v1〉說重算「受存量漂移檢查的總時間預算管」。
3. 預算只在檔與檔之間、步驟之間檢查。單次 `re.findall` 無法中斷,災難性回溯可以跑任意久。
4. 新求值器沿用 `_DriftProbeTree._py`,對檔案大小沒有上限。同一支檔 m1 有 `_DRIFT_M1_PARSE_MAX_BYTES`,理由寫著「尖峰記憶體約原始碼 100 到 280 倍」。
5. 這個標記由筆記作者寫,推送閘和 CI 都會替所有人執行它。
引句:「重算受存量漂移檢查的總時間預算管,不再每個標記各自無上限地掃整個 repo。」
佐證:`scripts/lumos:29868`、`scripts/lumos:3017`

**R2B7 正文範例把欄位包在反引號裡,依 spec 自己的規則是死的**
severity: major
blocking: 是——規範單源要寫進 skill 的範例,照抄會讓每條欄位都不被評估。
1. 〈一個事實只寫一處〉的範例行寫成「WHY:[2026-10-01 討論]……`[count:app/config.py::MODEL_VARS=4]`」,PITFALL 例也包了 `` `[lives:app/router.py::dispatch]` ``。
2. 〈欄位 v1〉的「寫在哪裡才算」說:行內程式碼裡的欄位不評估,並要提醒「寫在不評估的地方」。
3. AI 照這個範例逐字寫,欄位落在不評估區,S9 提醒一定出現,過時判定永不觸發。
4. 〈寫法提醒〉的 W1 範本和〈讓 AI 知道該寫什麼〉的速查表都會沿用這個形態。
引句:「加變數前先量記憶體 `[count:app/config.py::MODEL_VARS=4]`」

**R2B8 非 Python 專案:W1 的範本推薦 `count`,但求值器不認,「寫的當下提醒」沒有擁有者**
severity: major
blocking: 是——對 Kotlin、Swift、TypeScript、Dart 專案,W1 會推出永遠不生效的欄位,又沒有任何一處告訴作者。
1. 〈欄位 v1〉求值欄承諾「寫的當下提醒改用正規式數量」。
2. 〈欄位寫壞〉的清單(鍵名、`=值`、`]`、副檔名、不評估處)和 S9 到 S14 都沒有這一項。
3. 提醒在提交時跑,而「判不了」要靠讀程式碼,提交前的筆記形狀檢查現在沒有任何地方讀程式碼。
4. W1 的範本固定寫 `[count:…]`。非 Python 的專案收到這條提醒、照填,欄位在推送時兩端都判不了,依 S5 靜默放行,沒有任何訊息。
5. 〈天花板〉第 3 條承認不懂別的語言,但沒講 W1 對這些專案該推薦什麼。
引句:「其他語言或讀不出來的(例:程式組出來的集合)→ 起點終點都「判不了」就不擋,寫的當下提醒改用正規式數量」

**R2B9 W1 的觸發與範本填值沒有可執行的定義**
severity: major
blocking: 是——S10 要求「印出填好名稱的範本」,但範本要的路徑與值,實作者拿不到。
1. 輸入:WHY 行用反引號寫了 `main`、`config`、`Client`,或 `scripts/lumos`、`--top`、`LUMOS_SKIP_DRIFT_CHECK`、`drift_check.fields`。
2. 「程式符號」沒有判準。既有 Check Y 的 `_is_symbol_shaped` 就是為此寫的一整套 profile 與啟發式,spec 沒說是否沿用。
3. 範例輸出是「`[count:app/config.py::MODEL_VARS=4]`」,含路徑與值。
4. 路徑要在 repo 裡找定義:同名符號出現在多個檔時選哪個?沒有定義時印什麼?
5. 值要求值:函式與類別沒有成員數,該推 `count`、`value` 還是 `lives`,spec 沒規則。
6. 〈寫法提醒〉只說「把那個名稱填進範本」,和範例不一致。
引句:「新寫的 WHY、RULE、PITFALL 行用反引號提到程式符號,又沒帶任何依賴欄位 → 提醒」
佐證:`scripts/lumos:2973`(Check Y 的符號形狀判準)

**R2B10 「寫在不評估的地方」的偵測現況不存在,而且會對說明欄位語法的文件本身誤報**
severity: minor
blocking: 否——只是提醒,不擋推送。
1. 輸入:新寫在圍欄、行內程式碼、表格裡的 `[count:…]`。
2. 既有 `_probe_lines` 對圍欄和行內程式碼是靜默跳過,只有表格行與 summary 以外的開頭欄位才進 `dead`。S9 要求圍欄和行內程式碼也提醒,這是新寫。
3. 這份 spec 自己的〈欄位 v1〉表格與〈寫法提醒〉就有 `[count:路徑::名稱=N]` 寫在表格與反引號裡。照 S9 實作,這篇計劃一提交就吃到好幾條「寫在不評估的地方」。
4. 說明欄位語法的筆記(skill 子檔、這份計劃)是最常寫這種範例的地方,提醒會變成雜訊。
引句:「行內程式碼、表格、圍欄、frontmatter 非摘要欄位裡的欄位不評估(文件範例才不會被當真),寫在那裡的提醒「寫在不評估的地方」。」
佐證:`scripts/lumos:28062`

**R2B11 W2 的排除清單和前綴表不一致,而且漏掉常見前綴**
severity: minor
blocking: 否——只是提醒。
1. 前綴表把 FACT、FLOW、DEP 當同一類「只寫程式答不了的現況」。W2 只排除 FACT,FLOW 與 DEP 的摘要行含「3 個 pod」也會被唸「程式推得出的事實不寫」。
2. 我在本 repo 的 Systems 摘要行實測,1053 行裡含「只有/唯一/恰好」或「N 個/N 支」的行有 120 行不在 WHY/RULE/PITFALL/FACT 之內。分布是 KEY 106 行、TEST 7 行、FLOW 5 行、DEP 2 行。
3. TEST 行記的是驗證結果,例如「2 個測試通過」,不是程式事實。
4. 〈一個事實只寫一處〉自己舉的壞例「模型變數有四個」用的是中文數字,W2 的「N」只比阿拉伯數字,抓不到。
引句:「而且前綴不是 WHY、RULE、PITFALL、FACT → 提醒」

**R2B12 W6 的「整個數字」比對在單位數的值上會誤報**
severity: minor
blocking: 否——降級成提醒了。
1. 輸入:`[count:x.py::A=1]` 搭配同行「第 1 步」或「10 月 1 日」。
2. 「前後不是數字或英文字母」的規則放過 `日 1 `、`.`、`-`,所以 `1`、`0`、`2` 這類值幾乎每行都命中。
3. 日期跳過只認 `YYYY-MM-DD`,不認其他寫法。
引句:「在方括號外又以整個數字出現(前後不是數字或英文字母;日期 `YYYY-MM-DD` 整串跳過;中文數字不比)」

**R2B13 分期第 0 步放 W4,但控制它的開關 `tag_hints` 要到第 2 步才有**
severity: minor
blocking: 否——只影響第 0 步到第 2 步之間的過渡期。
1. S14 要求 `note_shape.tag_hints` 為 off 時「W1 到 W6」都不出現,〈相容〉也說 W4 要關就設它。
2. 分期把 W4 放在第 0 步,`note_shape.tag_hints` 與其他 W 項放在第 2 步。第 0 步出貨的 W4 沒有開關。
3. 〈回退〉第 0 步只說還原提交,和 S14 對不上。
引句:「0. **先修文件矛盾、讓既有提醒送得到**:四處文件矛盾裡,RULE 效力那處改程式註解去對齊紀律範本(範本是政策來源),其餘照程式行為改;RETIRE-IF 加進摘要前綴表;W4。」

**R2B14 「範本是政策來源」,但範本自己有兩句互相不一致**
severity: minor
blocking: 否——是文件修補的範圍問題,不改變程式行為。
1. `scripts/templates/graph-discipline.md:28` 寫「同時寫齊 `[since:]` `[retire:]` `[confirmed:]` 且最近半年確認過」。
2. 同檔 `scripts/templates/graph-discipline.md:42` 的表格寫 `[confirmed:]` 選填、「寫齊才有挑戰程式碼的效力」,可讀成只要 since 加 retire。
3. 第 0 步只說改程式註解,沒說範本表格那行也要對齊;S15 只釘程式註解。
4. W4 只提醒缺 since、retire、until 過期,不提醒缺 `[confirmed:]`,所以工具引導出的 RULE 沒有挑戰效力。這個差距沒被說明。
引句:「RULE 效力那處改程式註解去對齊紀律範本(範本是政策來源)」
佐證:`scripts/templates/graph-discipline.md:28`、`scripts/templates/graph-discipline.md:42`、`scripts/lumos:3268`

**R2B15 搜尋行模式:`--about` 的範圍、排序與預設上限不夠定義**
severity: minor
blocking: 否——截斷數有印在 stderr,不是靜默。
1. 輸入:`lumos search --about scripts/lumos --prefix RULE,PITFALL,WHY`。
2. 實測本 repo,管 `scripts/lumos` 的家筆記有 80 篇,摘要裡 WHY、RULE、PITFALL 共 168 行。行模式預設 80 行,會截掉一半以上。
3. 保留哪 80 行沒有排序規則。
4. 既有 `--top` 預設 0 代表全量,註解寫著「圖譜先行不靜默截斷」。行模式預設改成 80,argparse 需要新的預設哨兵值,spec 沒提。
5. S16 說輸出是「這兩種摘要行」,而〈欄位 v1〉的欄位可寫在正文行,正文行沒有前綴可以篩。`--about` 單獨給時,是否輸出家筆記全部摘要行,沒有定義。
6. `--about` 的檔參數怎麼正規化(`./`、絕對路徑、相對 cwd、NFC),沒寫。沒有家的檔印什麼也沒寫。
引句:「行模式預設 80 行,`--top 0` 全給」
佐證:`scripts/lumos:40184`、`scripts/lumos:34533`

**R2B16 `drift ack` 的種類沒定義;`fields` 開關和 `drift_check.gate` 的交互沒定義**
severity: minor
blocking: 否——實作者要自己決定,但選哪個都有合理說法。
1. 擋下訊息要印 `drift ack`。`_DRIFT_KINDS` 是固定元組 `("probe","c1",…,"m1")`,`_drift_ack_args_err` 對不在內的種類回錯。新增發現種類要改這個元組,或沿用 `probe`,spec 沒說。
2. 沿用 `probe` 會跟同一行的 REVISIT 表態混在一起。表態以(路徑、原文、種類)為鍵、沒有期限,等於永久關掉那一行。
3. 專案若把 `drift_check.gate` 設成 `warn`,`fields` 預設 block 是否仍然擋?既有 `old_sentence` 是「兩個開關各管各的」。spec 只借它的壞值處理,沒借這一點。
4. 「起點就不吻合的舊帳由 doctor 列出」(S3)沒有出現在分期的任何一步,也沒有對應 S 條款。
引句:「當起點就已經不吻合、終點仍不吻合,推送 應 不被擋(舊帳由 doctor 列出)」
佐證:`scripts/lumos:27554`、`scripts/lumos:28860`

---

實務隱患:這份設計碰到的風險類,逐類回答如下。
- **資源**:有隱患,見 R2B6。預算管不到單次正規式與語法樹解析。
- **相容**:有隱患,見 R2B5。舊 HTML 標記會被新閘評估。
- **注入**:有。標記裡的 `re=` 由筆記作者寫、由所有人的推送與 CI 執行。沒有逃逸或提權風險,但可以癱瘓推送(R2B6)。
- **回滾**:無新問題,`fields: off` 與還原提交足夠。唯一的小洞是第 0 步的 W4 沒有開關(R2B13)。
- **併發、金流、對外送出、不可逆**:無。新增的寫入只有既有的治理帳,spec 的「已排除」三項理由成立。

最高嚴重度:major,blocking 9 條
