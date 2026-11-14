severity: major

## t1 節點起始行規則讓接在鏈後面的 `.flatMapLatest` 這一行永遠不是選擇點
severity: major
blocking: 是——照字面實作,Kotlin 慣用的多行鏈式寫法(行首是 `.`)在這版完全沒有壞法,推送閘靜默放行。
- 位置:〈用詞〉選擇點、API 列、預期值表 S1 第一列。
- 引句:「語法樹掃描在改到的行上命中的選擇點規則節點(節點起始行是改到的行)」
- 引句:「`.flatMapLatest { repo.search(it) }`(檔頭逐一 import flatMapLatest)」
- 問題:API 列只認 `navigation_expression` 後接 `call_suffix`,也就是 `call_expression`。tree-sitter 的 `call_expression` 與 `navigation_expression` 都是左遞迴(`seq($._expression, $.call_suffix)`、`seq($._expression, $.navigation_suffix)`)。節點起點是整條鏈的接收者,不是 `.flatMapLatest` 那一行。
  - 輸入:`val r = query` 換行 `    .debounce(300)` 換行 `    .flatMapLatest { repo.search(it) }`,只改第三行。
  - 預期:API 壞法 flatMapConcat。
  - 字面實作:節點起點在第一行,第三行沒有選擇點,S21 判「改到的行沒有壞法 → 不要求」,放行。
- S1 自己的範例就是行首 `.` 的續行,跟〈用詞〉的起始行定義互相矛盾。面試題要在多行鏈上才會原樣重現。
- 同一根因也影響:
  - 跨行布林,例如 `a > 0` 換行 `&& b`,只改第二行時 `&&` 節點起點在第一行。
  - `a && b && c` 這類左遞迴二元鏈。
- 修法方向:選擇點的位置改用「運算子記號/選擇器 `simple_identifier` 所在行」,不用節點起始行。`old` 的取法仍可照節點整段。
- 查證:grammar.js 第 1204、1218 行是左遞迴結構;`navigation_suffix` 另帶 `type_arguments` 與 `_member_access_operator`。

## t2 同類別多節點用「最左邊」挑,左遞迴鏈上起點全部相同
severity: minor
blocking: 否——挑到的仍是合法壞法,只是不確定是哪一個。
- 位置:〈用詞〉一行一個壞法。
- 引句:「在那個類別的節點中取最左邊的一個」
- 問題:`x.distinctUntilChanged().flatMapLatest {…}` 的外層與內層 `call_expression` 起點同欄。`a + b + c` 的兩層 additive 也是。
  - 沒有第二排序鍵,挑哪個取決於 ast-grep 輸出順序與版本。
  - S3「同一行內容不變挑同一個」只有在輸出順序固定時成立。
- 修法方向:用運算子記號的欄位當排序鍵,並寫明同欄時取外層或內層。

## t3 有效處置只認 (file, line_sha),同檔內容相同的兩行共用一筆處置
severity: major
blocking: 是——照字面實作,複製貼上的第二處選擇點從沒跑過壞法也算有處置,正是這份計劃要堵的洞。
- 位置:〈用詞〉有效處置、壞法身分。
- 引句:「帳上同一個 (`file`, `line_sha`) 最新一筆是 `killed` 而且 `killing_test` 還在現在守的測試裡」
- 問題:壞法身分有 `row`、`new_sha`,但有效處置只看 `line_sha`(單行原文雜湊)。
  - 輸入:同檔兩個 ViewModel 各有一行 `.flatMapLatest { repo.search(it) }`,兩行的前後各兩行不同。
  - S3「不唯一」只在連前後各 2 行都相同才觸發,所以兩行各自「唯一」。
  - 第一行被 `choice-kill` 殺掉,第二行(沒有測試守)查帳時 `line_sha` 相同,直接視為已處置。
  - 反向也成立:第一處被判 `judged equivalent`,第二處真正的選擇也跟著免死。
- 兩行都在改到的範圍內時,同一份種子還會讓它們挑到同一類別。
- 修法方向:有效處置的鍵加入 `old` 帶上下文後的雜湊,或加 `occurrence` 序號。

## t4 有效處置綁著「現在守的測試」,計劃一轉 done 前面殺掉的行全變過期,而且指令跑不回來
severity: major
blocking: 是——照字面實作,先把計劃標 done、之後再推一次,所有 killed 行都被擋,擋下後 `choice-kill` 也跑不動。
- 位置:〈用詞〉進行中計劃、守的測試、過期,〈範圍〉2 跑之前、〈範圍〉4 判定。
- 引句:「status 是 doing,或這次推送改到計劃檔本身而 status 是 done」
- 問題:`_live` 的語意是「done 且推送範圍改到計劃檔本身」才算進行中(已讀 `_spec_gate_push_scan` 的 `_live`)。
  - 流程:第一次推送計劃 doing。第二次推送把計劃改 done(算進行中)。CI 失敗或審查意見後第三次推送只改程式碼,計劃不在範圍內,於是沒有進行中計劃。
  - 此時守的測試集合為空,所有 `killing_test` 都「不在現在守的測試裡」,整批判成過期,或被判「無規格」。
  - `choice-kill` 同樣算不出進行中計劃,回 rc 2「沒規格就判不了」,作者只能把計劃改回 doing 或逐行 `choice-judge`。
- 另一個缺口:「碰到的計劃」交給 `_spec_gate_push_candidates` 時,輸入範圍是推送範圍 A..B 還是改到的行範圍(主線分岔點..B),〈用詞〉沒講。前者會漏掉,後者會誤抓。
- 修法方向:
  - 已有 `killed` 紀錄且測試仍存在於 B 版樹的行,不要求計劃仍在進行中。
  - 或把「進行中」沿用到整個分支的生命週期(同一範圍起點)。
  - 並明講計劃候選用哪個範圍。

## t5 乾節點的「複合節點全乾才乾」無法由 ast-grep 命中結果算出,「旗標」列的字面又跟 S4 的例子互相矛盾
severity: major
blocking: 是——照字面實作,S4 要求的「複合節點只有所有子節點都乾才算乾」做不出來,旗標列有兩種讀法且其中一種違反 S4。
- 位置:〈用詞〉乾節點規則、〈用詞〉語法樹掃描、S4、預期值表 S4 後兩列。
- 引句:「複合節點照公式 1:只有所有子節點都乾才整個乾」
- 引句:「旗標(含 `BuildConfig.DEBUG` 的條件節點;A.1.13、A.1.16)」
- 問題 1:語法樹掃描只回「規則命中的節點」。判斷「所有子節點都乾」要走完整棵樹,並對每個葉子定義「乾」(關鍵字、括號、識別字算不算?)。ast-grep 的規則 YAML 只能手寫逐案的 `all`/`has`,不是遞迴,spec 沒有第二個機制。
- 問題 2:旗標列字面是「含 `BuildConfig.DEBUG` 的條件節點」乾。
  - 讀法一:乾的是整個 `if_expression`。那 `if (BuildConfig.DEBUG && x > 1)` 整個乾,跟 S4 最後一列「`x > 1` 照常可挑」衝突。
  - 讀法二:乾的只是 `BuildConfig.DEBUG` 子節點。那「整個 if 沒有壞法」(S4 第四列)靠的是公式 1 遞迴,回到問題 1。
- 修法方向:把規則寫成單一 ast-grep 規則並附反例樣本,不靠通用遞迴,在〈乾節點規則〉列「乾的範圍」欄逐列寫死是哪個節點。

## t6 跟論文不同的差異清單還缺幾處,後果沒寫
severity: minor
blocking: 否
- 位置:PRIOR-ART 的「跟論文不同的地方」①–⑥、天花板 3。
- 引句:「論文有覆蓋率挑最小測試集,我們沒有,每個壞法跑全部守的測試」
- 對照論文原文(PDF 第 3 頁 2.2 節、第 7 頁 Listing 2)缺的幾處:
  1. 論文只對「被覆蓋的改動行」產生壞法(Listing 2 的 `covered_lines`)。論文用覆蓋率同時決定「哪些行要變異」。差異①只講了「挑最小測試集」。後果是沒有任何測試跑到的行一律存活,這點只在天花板 3 一句帶過。
  2. Listing 2 的 `shuffle` 在整次呼叫只洗一次,同一份改動的每一行共用同一個類別順序。spec 的「每行用各自種子洗」是不同做法,沒列在差異裡。
  3. 3.2.4 的冗餘壞法抑制沒做。論文舉的 LCR 與 null 比較、`x != null` → `false` 在 Kotlin 很常見。spec 的 LCR 給 `true`/`false`/`$A`/`$B`,沒有排除它們。
  4. 附錄 A 乾節點只收了一部分。依據來源表寫「A.1.1–A.1.24」,實際沒收 A.1.7(靠覆蓋率)、A.1.8(加 0)、A.1.9/A.1.10(null 與零比較)、A.1.17(快取查詢)、A.1.18、A.1.19、A.1.14。
- 已核對正確:表 1 的 AOR/LCR/ROR/UOI/SBR 候選、`2.3 節 7×檔數` 上限、A.1.23 的 `==`→`!=` 單向、公式 1 以節點為單位。
- file: `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-shearwater/abe4deee-64ee-43ea-85c3-2a647e0b825a/scratchpad/paper/google-practical-mutation-testing.pdf:7`

## t7 ast-grep JSON 的細節與解析錯誤沒處理
severity: minor
blocking: 否
- 位置:〈用詞〉語法樹掃描。
- 引句:「讀每個命中的規則編號、節點範圍(起訖行列)、節點原文與後設變數(運算元)」
- 問題:
  - ast-grep 的 `--json` 行號是 0 起算,行號對照的差一會錯位。
  - 欄位單位在含中文的 Kotlin 字串或註解行上容易錯位,應改用 `range.byteOffset` 切字串。spec 都沒寫。
  - tree-sitter-kotlin 遇到不認得的語法(Kotlin 2.x 新語法)會產生 ERROR 節點並照樣回命中。spec 沒有「節點含 ERROR 就略過」的規則。落成「壞法編不過 → no_result」,而 no_result 會擋推送。
- 修法方向:規則樣本加一份含 ERROR 的檔,掃描時排除祖先或子孫含 ERROR 的節點。

## t8 SBR 的排除規則有兩處不準
severity: minor
blocking: 否
- 位置:〈用詞〉選擇點表 SBR 列、S5。
- 引句:「`statements` 的直接子節點、而且是 `call_expression` 的陳述 → 刪掉」
- 問題 1:「不在 `value_arguments` 裡」是空話。`statements` 的直接子節點不可能是 `value_argument`,實作者可能誤讀成「祖先任何一層」而把 `foo(bar { a(); b() })` 這種引數內 lambda 的陳述全排掉。
- 問題 2:「不是 `lambda_literal` 的最後一個陳述」把 `launch { repo.save(x) }`、`onClick = { vm.onTap() }` 這類 Unit lambda 的唯一呼叫陳述全排除,過度排除。
- 問題 3:漏排值語意的區塊。`val x = if (c) { a() } else { b() }`、`when` 分支、`try` 區塊的最後陳述也是值。刪掉會編不過,落成 no_result。
- 修法方向:排除規則改寫成 ast-grep 的 `inside` 加 `nthChild`,並附對照樣本。

## t9 ceiling 4 對面試題的機率只講了一半,而且最關鍵的驗收是手動的
severity: minor
blocking: 否
- 位置:天花板 4、S25。
- 引句:「面試題那種 `flatMapLatest` 若跟條件式同一行,有一半以上的機會挑到別的類別」
- 問題:
  - 「一半以上」數學上成立(K≥2 時 1-1/K ≥ 1/2),但沒講更大的來源:t1 的行首 `.` 問題與類別內同欄的並列(t2)。
  - 一條鏈上同時有 `distinctUntilChanged`(API「拿掉」)與 `flatMapLatest` 時,一旦挑到 API 類,「在那個類別取最左邊」可能先挑到 `distinctUntilChanged`,而不是 `flatMapLatest`。
  - 這份計劃要證明的核心,也就是面試題能被抓到,唯一的驗收 S25 是 `[manual:]`,沒有任何綁定測試。
- 修法方向:把 S25 的那一行(多行鏈、單行兩種寫法)各做成 `choice-points` 的 fixture 測試,至少驗「選擇點存在、類別是 API」。

## t10 RETIRE-IF 的樣本下限量得到,但門檻可能永遠達不到
severity: minor
blocking: 否
- 位置:RETIRE-IF、S22。
- 引句:「上線兩個月、被回報的存活累計至少 30 個之後」
- 問題:
  - 分母「被回報的存活」在 `--stats` 沒有獨立數字。S22 只印第一次跑殺掉率與處置分布,沒有「被上限抽中的存活數」。
  - 條件③「被擋筆數過半是過期」的筆數與 `blocked` 事件的去重規則(同 B 同組 reason 不重記)互相作用,會低估。
  - 單人專案兩個月是否累積 30 個存活沒有依據。累積不到,三個撤除條件全部不會觸發,沒量到,條件等於沒有。
- 修法方向:`--stats` 加印「被回報的存活」總數,並寫明未達樣本時的處理(延長觀察期或看 REVISIT)。

## t11 作者照常操作可以怎麼繞
severity: minor
blocking: 否
- 位置:〈用詞〉乾節點規則。
- 引句:「斷言與前置條件(裸呼叫 `require`、`check`、`assert`、`requireNotNull`、`checkNotNull`、`error`,沒有接收者;A.1.5)」
- 繞法:
  1. 行首 `.` 續行(t1)。這是最常見的。
  2. 把邏輯放進整個節點都乾的引數裡:`check(items.filter { … }.any())`、`maxOf(a, if (x > y) b else c)`、`delay(retry * 1000L)`。乾的範圍是「那個節點整個,含跨行引數」,裡面所有選擇點全被擋掉。
  3. 靠 `@Module` 類別本體、`@Provides` 函式本體整段乾。
  4. 用表沒列的寫法換:elvis `?:`、`in` 範圍、`isEmpty`↔`isNotEmpty`、`when` 分支、數字常數。這些屬天花板 1,算已承認。
  5. 同檔複製貼上的相同行(t3)。
- 以上都在使用者承認的威脅模型(單人、AI 依序操作、不防刻意偽造)之內,只列出供作者看是否要收窄。

## t12 壞法套回原文沒說明是否加括號
severity: minor
blocking: 否
- 位置:〈用詞〉壞法身分、選擇點表 AOR/LCR。
- 引句:「`new` 是 `old` 套上壞法。」
- 問題:`new` 由後設變數直接拼文字。
  - 輸入:`x + a * b` 把 `a * b` 換成 `$A + $B` 得到 `x + a + b`,結構變了。
  - 輸入:`p && a && b` 的內層 `p && a` 換成 `$A || $B` 得到 `p || a && b`,結構也變了。
  - 這仍是有差異的壞法,但不是 spec 說的那個壞法,`new_sha` 與 `old` 對不上預期值表的列。
- 修法方向:規則樣本加這類巢狀案例,並寫明何時加括號。

## 折入檢查(r2 的 73 條)
已讀 r2-intake.md,抽查以下幾組,到位:
- H1:節點名 `comparison_expression`、`equality_expression`、`conjunction_expression`、`disjunction_expression`、`additive_expression`、`multiplicative_expression`、`prefix_expression`、`call_expression`、`navigation_expression`、`statements`、`lambda_literal`、`value_arguments`、`function_body`、`call_suffix` 在 grammar.js 都存在。
- H3 的 `stop_group_on_kill`、`on_row`、`source`。
- H4 的「曾經存活」集合當種子。
- H7 已拿掉 `first/last`、`take/takeLast`、`drop/dropLast`、`collectLatest/collect`、`coroutineScope/supervisorScope`。
- H9 的表 1 候選。
- 未到位的只有 t1(起始行)、t3(身分鍵),分別是 H1 與 H4 折入後新產生的洞。

## 圖譜節點逐條判
- `Systems/guard-kill`:兩條 ★INVARIANT★ 不受影響。
  - `cmd_guard_kill` 新增的 `source`、`stop_group_on_kill`、`on_row` 都是選用,不傳時行為不變,rc 優先序(survived→1、drifted/abort/error→2)不動。
  - `choice-kill` 自己的 rc「取最大」是另一條指令的規則,不改 `cmd_guard_kill` 本身。
  - JSON 純度限定 rc 0/1 成功路徑。計劃新增的「強制結束時印出工作樹路徑」不在成功路徑,但實作須走 stderr,不然在 `--json` 的 rc 2 路徑仍會污染。這一句建議寫進計劃。
- `Systems/規格閘`:節點沒有合約行(0 條),無 ★INVARIANT★ 可破。計劃另起一圈放在 `_spec_gate_push_check`,「算不出來就放行」的既有裁定被保留。
  - 但「ast-grep 不在而範圍有 .kt 正式碼改動 → 擋」跟舊否決比對裡引的「工具壞不能擋所有人」互相衝突。這點計劃是明講的,但 S6 與原則矛盾,算 minor。
- `Systems/kotlin規則包`:沒有合約。計劃是新增兩節與 `configs/ast-grep/kotlin-choice/`,不動既有 `kotlin-android` 規則,不影響。

最嚴重:major;blocking 共 4 條
