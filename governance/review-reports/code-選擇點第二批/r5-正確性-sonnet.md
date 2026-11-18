severity: major

## c1 規則裡方法名與識別字的比對頭尾錨點拿掉,樣本核對照綠
severity: major
blocking: 是——能指出具體合理的改壞而樣本核對全綠,被保護的是「只收這個名字」的必要行為。
引句:「LaunchedEffectCompat(k) { load() } // MISS C-36」
- 作者只驗了拿掉整個 `regex`,以及 `LaunchedEffect`、`remember` 的結尾 `$`(`LaunchedEffectCompat`、`rememberSaveable` 兩行翻紅)。其餘錨點沒有任何一行守著。
- 我把 api.yml 的錨點逐一改掉,每次跑 `choice_sample_problems`,結果都是 `[]`,等於全綠:
  - C-34 的 `let$` 改成 `let`。輸入 `x.letX { it }` 會多命中(實測 `val d = x.letX { it }`,多命中一行)。
  - C-35 的 `combine$` 改成 `combine`。輸入 `a.combineLatest(b)` 會多命中。
  - C-36 的 `^LaunchedEffect$` 改成 `LaunchedEffect$`。輸入 `MyLaunchedEffect(k) { load() }` 會多命中。
  - C-37 的 `^remember$` 改成 `remember$`。輸入 `myremember(k) { 3 }` 會多命中。
  - `Unit` 那條的 `^`、`$` 拿掉。輸入 `LaunchedEffect(distanceUnit)`、`LaunchedEffect(UnitX)` 的 key 會被當成字面值 `Unit`,命中消失,是靜默漏殺。
- 這四個方法名各自缺一個 MISS 樣本,`Unit` 那條缺一個 HIT 樣本,補上就會翻紅。
- 歸因:有證據的原有漏查。修前版本跑同樣的改壞,同樣全綠;這輪補的樣本沒有補到這幾個錨點。
- 對照證據:拿掉 `[CA]` 型的 `regex` 整個,修前 `noOfRule`、`let|also`、`combine|zip`、`LaunchedEffect` 結尾 `$` 都是存活,修後都翻紅。這輪補的樣本確實有效,只是漏了錨點。
- file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml:188-189`(let 的 regex)、`:205`(combine)、`:256`(LaunchedEffect)、`:301`(remember)、`:227`(Unit)

## c2 最後一個陳述的註解排除只守了 lambda 那一處,if/when/try 區塊內的那一處拿掉照綠
severity: major
blocking: 是——同一條「註解不算陳述」條款有兩處用到,只有一處有樣本守著,另一處拿掉改壞而樣本全綠。
引句:「val lc = list.map {」
- 規則裡 `ofRule: {matches: code}` 出現兩次:value-pos 一次,value-used 最後一個 `all` 分支一次。
- 新樣本 `lc`、`mc` 的註解都在 lambda 內,只能翻紅第一處。我只把第二處拿掉(`- nthChild: {position: 1, reverse: true}` 取代 `ofRule` 版本),`choice_sample_problems` 回 `[]`。
- 最小輸入:`val r = if (c) { go(); x.let { it + 1 } // c` 換行 `} else 0`。原規則命中 `.let`(C-34,行 18);改壞後這一行不再命中,是值被用到的 `.let` 被漏掉。
- 歸因:有證據的原有漏查。修前同樣存活;作者補樣本時只涵蓋 lambda 那一處。
- file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml:178-179`

## c3 作者判等價不補的「父節點種類限定」不等價:拿掉 `kind: prefix_expression` 後 `-k + 1` 的行為不同
severity: major
blocking: 是——作者的等價判斷有可執行的反例,而且改壞後樣本全綠。
引句:「- {kind: prefix_expression, regex: '^[-+]'}」
- 把這一行改成 `{regex: '^[-+]'}`(拿掉種類限定、留 regex),樣本核對照綠。
- 輸入 `LaunchedEffect(-k + 1) { load() }` 與 `LaunchedEffect(+k * 2) { load() }`:兩行的文字以 `-`、`+` 開頭,節點是二元運算而非前綴運算,最後一個子節點是整數字面值。
  - 原規則:不是字面值,所以命中 C-36。
  - 改壞後:當成字面值,兩行都不命中。實測 added `[]`,removed 兩行(各 C-36 一筆)。
- 歸因:有證據的原有漏查。修前同樣存活,這輪沒碰這一行。
- 補一行 `LaunchedEffect(-k + 1) { load() } // HIT C-36` 就會翻紅。
- 其餘作者判等價的類別我造不出行為不同的合理 Kotlin:
  - `stopBy: end`:原始字串、巢狀插值、`"${id}"` 都在直接子節點,拿掉後 added、removed 都是空。
  - 內層 `nthChild reverse`:拿掉後 added、removed 都是空。
  - `regex: '^[-+]'`:唯一差異是 `LaunchedEffect(@Suppress("X") 1)`,原規則命中、拿掉後不命中。這是註解加常數,拿掉反而更對,不當缺陷。
  - 外層 `nthChild reverse`:只有具名引數標籤是 `Unit` 時才不同,不合法。
- file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml:239`

## c4 C-35 的 `?.combine` 與完整套件名比對的空白容忍沒有樣本
severity: minor
blocking: 否——差別只出現在較少見的寫法,造出的是漏殺或多殺一行,不影響其他規則。
引句:「val f = a.combine(b) { x, y -> x + y } // HIT C-35」
- 把 C-35 regex 的 `(\?\.|\.)` 改成只認 `\.`:`val g = a?.combine(b) { p, q -> p }` 的兩種寫法(同行與 `?.` 換行)都不再命中,樣本照綠。樣本沒有 `a?.combine` 的 HIT。
- 把完整套件名的 `\s*` 都拿掉(`'^kotlinx\.coroutines\.flow\.combine$'`):`kotlinx.coroutines` 換行 `.flow.combine(a, b) {…}` 原本不命中,改壞後多命中一行,樣本照綠。樣本沒有跨行完整套件名的 MISS。
- 歸因:有證據的原有漏查(修前同樣存活)。
- file: `configs/ast-grep/kotlin-choice/rules-choice/api.yml:205,210`

## 表列號新判法的逐項回答
- 實測在修前與修後都跑過。環境是合成型錄,`rules_dir=False`。
- 修後的結果:
  - `C-0`、`A-0`:報「列號要寫成…」。修前被接受,這是新增的行為。
  - `C-01`、`A-01`、`C-１`、`C-٤０`:報「列號要寫成…」。修前全部被接受。
  - `C-1a`、`C- 40`、`c-40`、`C-4 0`:列沒有被讀成列,什麼問題都沒報,行為跟修前一樣。`_CHOICE_ROW_RE` 與 `_ARID_ROW_RE` 的 `^\|\s*C-\d+\s*\|` 先把這幾行濾掉,新判法看不到它們。
  - 列號前後有全形空白(`\u3000C-40`、`C-40\u3000`):`_cells` 的 strip 先去掉空白,當成 `C-40` 收進表,沒有報。
- 同列的規則 id、樣本標記與撤號檢查有沒有漏報或連鎖報錯:
  - 沒有漏報。列號被跳過後,`rules-choice` 裡 id 同名的規則報「在型錄沒有對應的列」,撤號檢查照樣看規則 id 擋住,樣本標記指向那個號時被 `choice_sample_mark_problems` 報。
  - 有連鎖:同一個壞列號除了「列號要寫成…」之外,還會多報規則沒有對應列、樣本標記指向不存在的列。這是額外的訊息,不是漏報。
  - 被濾掉的那幾種寫法(`C-1a`、`c-40` 等)只有在有同名規則檔或樣本標記時才會被間接報出,單獨寫成表列沒有任何訊息,是原有行為。
- 兩版對照:`before` 是 59c41038、`after` 是 c261a154,同一份合成型錄各列對照如上。
- 測試:`python3.14 scripts/test_lumos.py -k choice_table_batch2` 20 passed、`-k choice_samples_batch2` 33 passed(在我的臨時副本)。

## 作者新補樣本的 HIT/MISS 核對
- 在 c261a154 用 ast-grep 0.51.2 實跑,`choice_sample_problems` 回 `[]`,每行 HIT/MISS 標記都跟規則現在的行為對得上。
- 每一行有沒有真的測到上方註解說的那個子句,我拿掉對應子句逐一驗:
  - `lc` 與 `mc`:拿掉 `line_comment`、`multiline_comment` 排除,翻紅行 46 與 49。
  - 行 51 `ys`:拿掉 value-pos 的 `nthChild` 翻紅。
  - 行 52 `v2`:拿掉第二處 `nthChild` 翻紅。
  - 行 53 的 if 底下 when:拿掉 `inside lambda` 或 `control_structure_body` 翻紅。
  - 行 54 `x.also`:regex 加上 `also` 翻紅。
  - 行 62 `a.zip`:regex 加上 `zip` 翻紅。
  - 行 64 `a.combine` 無呼叫:拿掉 `inside call_expression` 翻紅。
  - 行 95/106(插值寫法)、96/107(方法名結尾)、97(`k + 1`,拿掉整行 prefix 子句才翻)、98(`run`,regex 加上 `run`、`rememberSaveable` 翻紅)都各有對應。
  - 每行都測到註解寫的子句,沒有「被別的子句命中、拿掉目標子句照綠」的情況。
- 我自己挑的子句裡,拿掉後樣本核對沒翻紅的見 c1–c4。等價存活(無可造出的輸入差別):`kind: navigation_expression` 的雙重否定、`kind: statements`、call 前綴 `nthChild: 1`、`^` 在 `let` 的 regex 前端。

## 修補鏡頭三問
- ① 原問題的修復效果:修前跟修後各跑同樣的改壞。
  - 拿掉 `ofRule: {matches: code}`、`LaunchedEffect` 結尾 `$`、`remember` 結尾 `$`、字串插值種類只留一種、`let|also`、`combine|zip`:修前都存活,修後都翻紅(對應新樣本行)。
  - 表列號 `C-040`、`C-４０`、`C-4０`、`A-01`:修前接受、修後報「列號要寫成…」。
  - 證據來自 `choice_sample_problems` 與 `choice_tables` 的實跑輸出。
- ② 修補處的正常、錯誤與相鄰路徑:
  - 正常列號 `C-1`、`C-40`、`A-1` 照認,測試的 20 條與 33 條都綠。
  - 撤號那一行的判法沒動。
  - 規則 id 要等於列號的檢查照舊,真實型錄 `check.py` 0 問題。
  - 已存在的樣本結果不變(基準 `choice_sample_problems` 回 `[]`)。
  - 沒有發現修補造成的回歸。
- ③ 新發現的同一案例修前、修後:c1–c4 的改壞都是修前與修後同樣存活,歸因都是有證據的原有漏查,不是修復造成。
- 圖譜鏡頭(固定席)沒有附,只讀到 `lens-r5.txt`:
  - `Systems/kotlin規則包.md`:這次改 `check.py`、`api.yml`、`test_lumos.py`,沒有改它宣稱的行為,不影響。
  - bound-tests-gate、guard-kill、lumos-cli-lifecycle、測試假綠形態、lumos-cli-read 的 INVARIANT:改動沒碰那幾條對應的程式路徑,不影響。
  - `pitfalls-code-loop`、`loop-convergence-recording` 的 RISK:只有 `scripts/lumos` 在本輪修補外改過(`_CHOICE_BASE_RED`、依列號統計),沒有改到它們的程式路徑,不影響。
- 未驗範圍:沒有重跑 scripts/lumos 的依列號統計時間打平路徑,也沒有跑含 ast-grep 的真實推送前閘。依列號統計與引數錨點只做了程式碼讀法核對,沒有找到具體出錯輸入。我另外測了安全呼叫符前有註解的情況:規則本身就不命中,沒有進到編輯那一步。

最嚴重:major;blocking 共 3 條
