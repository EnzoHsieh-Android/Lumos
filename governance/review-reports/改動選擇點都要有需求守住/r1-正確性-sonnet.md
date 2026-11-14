severity: major

## c1 殺掉判定要從結果列認出是哪支測試,結果列沒帶測試名,配方身分也分不開
severity: major
blocking: 是——照字面實作無法產出 `killing_test` 與 `clauses`,實作者只能自己改 `result_out` 或猜配方順序。
- 位置:〈用詞〉殺掉判定、〈範圍〉2「共用」。
- spec 要一次傳入全部守的測試,再從 `result_out` 的列讀,並取「條款順序第一支殺掉它的測試」。
- 查證一:`result_out["rows"]` 只有 `recipe_id`、`short`、`verdict`、`weak`、`detail`、`weak_why`、`log_recipe_id`、`fail_excerpt`,沒有 `test` 欄。
- 查證二:`recipe_id` 由 `_kill_recipe_key(node, invariant, file, old)` 算出,不含 `test`。同一點、同一 `invariant` 的多支測試會得到同一個 `recipe_id`。spec 沒規定每個臨時配方的 `invariant` 要唯一。
- 查證三:列的順序是「按平台分組後再按配方順序」,不是條款順序。revert 失敗時 `break` 會讓後面的配方沒有列,所以也不能用位置對應。
- 查證四:`cmd_guard_kill(env, node, …)` 只收一個 `node`,spec 沒說多份進行中計劃時傳哪一份。傳錯會讓 kill-log 的 `node` 和 `recipe_id` 記到錯的計劃。
- 具體例:兩支測試 t_a、t_b 綁在計劃 P1 的 S1、S2。兩個配方的 `invariant` 都是 `cid0`,它們的 `recipe_id` 相同。t_b 判 killed、t_a 判 survived 時,工具分不出是誰殺掉,`killing_test` 無從填。
- 引句:「把它全部守的測試當 `recipes_override` 一次丟進去」
- file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:28151`
- file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:26321`

## c2 situation-rule 對同一條款文字與測試的第二個 `--point`,只換冪等鍵會被拒絕或誤判已寫過
severity: major
blocking: 是——預期值表 S10 第 3 列要「兩點各記 killed」,按 spec 描述的改法做不出來。
- 位置:〈範圍〉3「規格沒寫」、預期值表 S10 第 3 列。
- 查證一:`_situation_rule_already` 先看計劃裡有沒有相同 `_clause_sha` 且只綁該測試的定義行。第一個 `--point` 寫回後這條已經存在。
- 查證二:第二個點進來時,帳上同編號的事件的 `seg`/`row`(spec 改成 `(file,old,new)` 集合)對不上,就走 `if evs:`,回「這段條款文字與測試已由別段別列的人裁寫回…要另證就換一段條款文字」並拒絕。
- 查證三:`_situation_rule_insert` 在已存在時回 `(None, cid, msg)` 或 `(None, None, why)`,不會插第二條,也不會記第二點。
- 缺的行為:spec 只說冪等鍵換掉,沒寫「條款已存在、這個點沒被帳上記過」要走哪條路,也就是不插入、但跑殺傷力並記該點 killed 且引用既有條款。照字面只換鍵,結果不是拒絕就是 rc 0 什麼都沒記。
- 具體例:先 `--point Vm.kt:12`,再用同一段文字與測試跑 `--point Vm.kt:30`。預期兩點各記 killed;實作出來第二次被拒,或回「已寫過」而沒有第二筆 killed。
- 引句:「冪等鍵從 (seg, row) 換成 (file, old, new) 的集合」
- file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:75714`

## c3 「範圍碰到的進行中計劃」沒有定義,卻決定守的測試、無規格與生效日
severity: major
blocking: 是——這個詞決定全閘的判定,字面讀法有好幾種,實作者只能猜。
- 位置:〈用詞〉守的測試、〈範圍〉2 跑之前、〈範圍〉4 條件、S12、S14。
- 〈用詞〉只定義了「進行中計劃」(status 為 doing,或 done 且這次改到計劃檔)。「碰到」從未定義。
- 查證:現有程式的「碰到」是 `_spec_gate_push_candidates`。它取推送範圍改到的計劃檔,加上連到被改程式檔的家的 doing 計劃。spec 沒引用這支。
- 同一份 spec 又說這一圈「不論有沒有候選計劃都跑」,所以很可能不是同一個意思。
- 具體例:分支改了 Vm.kt。計劃 P(doing)的 `lands_in` 指到 Vm.kt 的家,但分支沒改 P 的檔。照「改到計劃檔」算是無規格,照候選算是有規格。S12 的 reason 因此兩種都說得通。
- 連帶問題:生效日條件寫「範圍碰到的進行中計劃的日期」,碰到多份且日期新舊混雜時,是任一份不早於生效日就適用,還是逐份算,spec 沒寫。拿一份舊計劃掛進範圍就可能整個免檢。
- 引句:「範圍碰到的進行中計劃裡,條款」
- file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:16535`

## c4 「外層函式」的定義跟被引用的切段函式互相矛盾,長函式與非函式區塊沒有退路
severity: major
blocking: 是——分組鍵 `<檔>::<函式名>`、樣式裡的函式名和多載序號,在常見 Kotlin 寫法下算不出或算錯。
- 位置:〈用詞〉需求脈絡組、樣式。
- spec 寫「往上找最近的 `fun` 宣告,沿用情境題切段找函式邊界那支」。
- 查證一:`_kt_sit_material` 找的是最近的頂層或類別層宣告,不是 `fun`。`_KT_SIT_DECL_RE` 同時收 `val`、`var`、`class`、`object`。
- 查證二:`_kt_sit_material` 在宣告超過 `_KT_SIT_MAT_MAX` 行、或宣告結束行早於命中行時回 None。spec 沒說 None 時的分組。
- 查證三:`init {}`、`constructor`、類別屬性初始化、`get()`、`by lazy`、區域 `fun` 都沒有可取的「最近 fun」。
- 字面讀「文字上最近的 `fun`」會把緊接在函式 f 之後的屬性初始化 `val x = a > b` 歸給已經結束的 f。
- 具體例:`fun search() { … }` 結束後下一行是 `val limit = if (n > 5) …`。字面實作把 `>` 組進 `::search`,跟 search 內的點合成一題,函式名也寫進樣式。
- 引句:「往上找最近的 `fun` 宣告,沿用情境題切段找函式邊界那支」
- file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:40083`
- file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:39990`

## c5 樣式推定的「不跨函式」不成立:頂層 `<top>` 與同名函式會跨檔壓掉真缺口
severity: major
blocking: 是——一次「不是需求」的判定會讓之後同樣式的存活點變成不擋,而同樣式的涵蓋範圍比 spec 宣稱的寬。
- 位置:〈用詞〉樣式、〈實務隱患〉樣式推定、預期值表 S20 第 1 列。
- 樣式是 (組號 `C-n`、成員、外層函式名) 三元組,檔與類別不在內,頂層函式名一律寫 `<top>`。
- S20 第 1 列自己就要求「另一支檔的 `toString`」被推定。
- 具體例:A 檔頂層 `val a = x > y` 被判 not-requirement,樣式是 (C-運算子,`>`→`>=`,`<top>`)。之後 B、C 檔任何頂層的 `>`(例如 `const`、`by lazy` 初始化、頂層擴充屬性)都自動「推定不是需求、不擋」。`onEvent`、`invoke`、`reduce` 等常見同名函式也一樣。
- 實務隱患寫的「樣式含外層函式名,不跨函式推廣」只在同檔同名唯一時才成立。
- 引句:「外層函式名照寫,頂層寫 `<top>`」
- 引句:「之後另一支檔的 `toString` 也有 `+`」

## c6 換行貼著運算子時算不算兩側有空白,spec 沒說,而 ktlint 風格會漏點
severity: minor
blocking: 否——spec 在天花板 2 已承認漏點,問題是它宣稱的前提(ktlint 要求兩側空白)沒有涵蓋換行。
- 位置:〈用詞〉選擇點、〈實務隱患〉運算子比對。
- 具體例:多行條件 `if (a > 0 &&\n    b < 3)`。行尾的 `&&` 右側是換行,不是空白字元。定位又是按行算的。
- 若實作逐行比對,`&&` 在行尾或行首換行都會漏掉,而這正是 ktlint 允許的寫法。這種寫法漏掉的是多行複合條件,偏偏是需求最密的地方。
- spec 沒寫換行是否算空白、運算子換行後是否仍算同一行的選擇點。
- 引句:「運算子成員只認兩側都有空白的」

## c7 識別字成員不看呼叫脈絡,屬性與具名參數會變成永遠跑不出結果的點
severity: minor
blocking: 否——不會放過缺口,但會製造只能用 `--judge` 解掉的擋下,而 `--judge` 的種類不貼切。
- 位置:〈用詞〉選擇點。
- `_kt_trigger_re` 只排除英數底線,所以任何整字的 `first`、`last`、`filter`、`take`、`all`、`none` 都算,不論是屬性、具名參數、變數還是方法。
- 具體例:
  - `pair.first` 是屬性,換成 `pair.last` 編不過,判 no_result。
  - `foo(filter = x)` 是具名參數,換成 `filterNot = x` 同樣編不過。
  - 變數 `val filter` 也一樣。
- 推送閘把 no_result 當擋。能用的出口只有 `--judge --as equivalent|not-requirement`。選 `equivalent` 是說謊,選 `not-requirement` 會順帶產生樣式推定(見 c5)。spec 沒有「不適用」這個處置。
- 引句:「識別字成員照整字比對(同 `_kt_trigger_re` 的邊界)」
- file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:39345`

## c8 「改到的行」沒套用現有的只改空白過濾,也沒套用路徑過濾
severity: minor
blocking: 否——會多擋(誤報),不會放過缺口。
- 位置:〈用詞〉選擇點、S1。
- 查證一:`_kt_sit_hits` 會把「去空白後與同一 hunk 刪行相同」的增行排除。spec 只說「改到的行」,沒沿用。
- 具體例:把 100 行邏輯包進 `withContext { … }` 而重新縮排,這 100 行全是增行,舊邏輯的每個選擇點都要重新處置。
- 查證二:路徑過濾 spec 只用 `_nodehome_is_test`,沒用情境題那支 `_kt_sit_path_ok`(它另外排除工具自裝檔與 `_stack_changed_ok`)。
- 引句:「改到的行(見〈範圍〉4 的範圍)裡」
- file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:40184`
- file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:40169`

## c9 組的第二個條件「守的測試集合相同」幾乎恆成立,S18 第 2 列造不出來
severity: minor
blocking: 否——實際分組變成只按函式,不會放過缺口。
- 位置:〈用詞〉需求脈絡組、S18。
- 〈範圍〉2 要求每點都把「全部守的測試」丟進去跑,所以同一次推送內每個點的測試集合相同。
- 紀錄欄位有 `test_blobs`(測試所在檔的 blob),沒有「跑過哪些測試」。同一檔裡的 t_a、t_b 無法分辨。
- S18 第 2 列「一點跑過 t_a、另一點跑過 t_a 與 t_b → 兩組」在上述設計下產生不出。
- 引句:「同一個外層函式(往上找最近的 `fun` 宣告,沿用情境題切段找函式邊界那支)而且守的測試集合相同」

## c10 「計劃從 B 讀」與引用的函式不一致
severity: minor
blocking: 否——工作目錄與 B 一致時看不出差異,不一致時判定可能錯。
- 位置:〈範圍〉4「讀哪一版」。
- spec 寫選擇點、計劃、治理帳都從 B 讀,但只列出讀檔的 `_kt_sit_read_many` 與讀帳的 `_gov_rows_at`。
- `_live` 讀的是 `env.notes`,也就是工作目錄的計劃狀態。`resolve_test_refs` 與平台測試索引讀的是工作目錄。
- 沒有哪個被點名的函式能讀 B 版計劃的條款與 `[test:]`。
- 具體例:工作目錄已把計劃改成 done、B 還是 doing,或工作目錄的測試已改名而 B 沒有。
- 引句:「選擇點(改到的檔)、計劃(決定守的測試)、治理帳都從 B 讀」

## c11 同身分的 `judged` 對不唯一的點會同時蓋住複製貼上的另一份
severity: minor
blocking: 否——是人裁的後果,與 c5 同源,窄得多。
- 位置:〈用詞〉選擇點身分、有效處置。
- 不唯一的點(前後各 2 行都相同,典型是複製貼上的區塊)身分是 (file, old, new),`old` 內容一樣,不含位置。
- 對其中一份 `--judge` 之後,另一份有一樣的 `old` 與 `new`,也算有效處置,而且不會被問。
- 引句:「同一點不再問」(spec 對不唯一的點沒有位置鍵,見〈用詞〉選擇點身分「還不唯一就這一點標「不唯一」」)

## c12 S15 的數字與 `attempt` 定義互相矛盾
severity: minor
blocking: 否——統計口徑錯,不影響閘。
- 位置:〈範圍〉5、S15。
- `attempt` 是「同身分第幾次」。S15 把「via situation-rule 的 killed」算在 attempt 1 的 killed 3 筆裡,又把它算進「存活後的處置分布:寫回規格 1」。
- 一個點若先 survived 再被 situation-rule 殺掉,後者是 attempt 2,不會落在 attempt 1。
- 一個點若沒有先 survived,它就不是「存活後」的處置。
- 兩個說法無法對同一筆成立,測試輸入也不知道怎麼造。
- 引句:「attempt(同身分第幾次)」

## c13 每點重跑基準,且不依相關性挑測試,成本會乘開
severity: minor
blocking: 否——spec 已用 RETIRE-IF ② 兜底,但〈實務隱患〉只講增量,沒講這個乘數。
- 位置:〈範圍〉2、〈實務隱患〉第一條。
- `cmd_guard_kill` 每次呼叫都建一個隔離工作樹,`baselines` 字典是每次呼叫自己的。
- spec 是「每點一次殺傷力呼叫」,所以同一支測試的基準每點都要重跑。run_cmd 帶 `{method}` 時,每支測試各一次 Gradle。
- 守的測試是範圍碰到的計劃的全部 `[test:]`,沒有按改動檔挑相關測試。
- 具體例:20 條款、20 支測試、30 個點,最壞要 20×30×2 次 Gradle 呼叫。
- 引句:「對還沒有有效處置的選擇點逐一跑殺掉判定(每點一個壞法、每點一次殺傷力呼叫)」

## 固定席節點判讀
- `guard-kill` INVARIANT 1(rc 優先序):不影響。spec 只新增選用參數 `source`,不傳維持原行為,rc 判定的程式區塊不動。choice-kill 的 rc 取最大是自己的另一層。
- `guard-kill` INVARIANT 2(`--json` 純度):不影響。choice-kill 呼叫 `cmd_guard_kill` 時不帶 `as_json`,不碰 JSON 輸出路徑。

## 其餘已讀、無 finding
- 〈白話〉、〈舊否決比對〉、〈PRIOR-ART〉、〈不做〉、〈回退〉、〈天花板〉:已讀,無 finding。
- 引用核對:`_KNOWN_GATES`、`LOOP_NOT_CLOSE_EVENTS`、`_GOV_FIELD_TYPES`、`_gov_row` 都存在。我掃了現有治理帳,新欄位(`file`、`old`、`new`、`group`、`reason`、`via`、`attempt`、`style`、`as`、`plans`、`clauses`、`test_blobs`)沒有與舊事件型別衝突。
- 錯字:〈用詞〉生效日提到 `_plan_effective_day(..., scope="note")`,我沒逐一核對該簽名。

## 實務隱患鏡頭
- 效能與記憶體:見 c13。另外 `_KT_SIT_READ_MAX`(4MB)超過時的行為 spec 沒寫,現有函式是 raise `_KtSitUnverifiable`,推送閘照現有慣例會擋。
- 換行與編碼:`_kt_sit_read_many` 只換 `\r\n`、用 `decode("utf-8","replace")`。`cmd_guard_kill` 用 `open(...)` 的通用換行與嚴格 UTF-8。單獨的 `\r` 或壞位元組檔會讓 `old` 恰好一次對不上,結果是 drifted 而非 killed。屬極少數。
- 併發與資安:沿用本專案單人依序操作的威脅模型,無新增面向(`old` 內容進版控帳,同現況)。
- 注入:`file`、`old`、`new` 走既有 `recipes_override` 路徑,路徑圍欄與 `_kill_*_issue` 照舊,無新增。

最嚴重:major;blocking 共 5 條
