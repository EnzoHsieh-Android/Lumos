severity: major

## z1 單次呼叫的 Gradle 成本沒有上限:存活與編不過的壞法都要跑完全部守的測試
severity: major
blocking: 是——照字面實作,一次 `choice-kill` 在第一次使用的功能上可能跑好幾個小時,而且 spec 沒有任何旋鈕能擋住。

- spec 位置:〈用詞〉守的測試、殺掉判定,〈範圍〉2 的 `--max-mutants`,〈實務隱患〉跑太久。
- 引句:「碰到的計劃(聯集)〈驗收條款〉裡 `[test:]` 綁的測試」
- 引句:「同一 `group` 已有一支強 killed 就略過其餘配方」
- 引句:「(預設 30):一次最多跑幾個壞法」
- 問題:實際 Gradle 次數是基準 B 加壞法 R。B 是實際輪到的不同測試數,每支基準最長 600 秒。R 是每個壞法跑到的測試數之和。
  - 只有「強 killed」會提前停。
  - survived、killed_unattributed、timed_out_weak、編不過全都要把 T 支測試各跑一遍。T 是所有碰到的進行中計劃的聯集。
  - spec 沒有覆蓋率(論文 2.1 用覆蓋率縮小測試集),沒被守的行一定存活。第一次跑一個新功能時,多數壞法會是 survived。
  - spec 自己承認沒有型別資訊(天花板 2),所以「編不過」是常態。每個編不過的壞法會在每支測試上各失敗一次。第一個失敗的輸出就能看出是編譯錯誤,但 spec 沒寫「編不過就停這個壞法」。
  - 會掛住的壞法(spec 自己舉 `flatMapLatest`→`flatMapConcat`)每支測試都要等到逾時。逾時是 `max(基準耗時×5, 20)` 秒(`scripts/lumos:28091`)。
  - 具體算法:預設 N=30、T=25(本計劃自己就有 25 條各綁一支測試)。最壞 R=750 次加 25 次基準,以暖機 45 秒計約 9.7 小時。
  - `--max-mutants` 只限壞法數,不限總時間。開跑前印「N × T」只是告知。
  - 唯一的量測被推到實作時(「實作時量一次 20 行改動的實際耗時」),RETIRE-IF ② 兩個月後才看。
- 論文差異:論文 2.3 是每個壞法各自一份版控暫存狀態、平行跑。spec 是單一工作樹、序列「改檔、跑、還原」。這點沒列在「跟論文不同的地方」,也沒寫在天花板 3。
- 建議:加每次呼叫的總時限(例如 `--max-seconds`)或每壞法測試數上限。編不過或第一支就逾時就停該壞法。
- file:`scripts/lumos:28029`(逐配方跑,只有迴圈外才有停止條件)
- file:`scripts/lumos:28113`(`timed_out_weak` 不算強證據,不會停)

## z2 `--max-mutants` 與「沒有有效處置就重跑」合起來會餓死沒跑過的壞法
severity: major
blocking: 是——照字面實作,「再跑一次」會把同一批 30 個存活壞法又跑一遍。

- spec 位置:〈範圍〉2、S11。
- 引句:「對還沒有有效處置的行,依〈用詞〉殺掉判定批次跑、逐筆寫帳」
- 引句:「(預設 30):一次最多跑幾個壞法」
- 問題:存活、no_result、不唯一都不是有效處置(只有 killed 且 killing_test 還在,或 judged 才算),所以每次呼叫都會再被選進來。
  - spec 沒定義挑哪 30 個:沒跑過的優先,還是檔案順序。
  - 例:40 個壞法,第一次按檔案順序跑前 30 個,其中 25 個存活,印「還有 10 個沒跑,再跑一次」。
  - 第二次呼叫時,那 25 個存活仍無有效處置。依自然順序它們排在前面,又吃掉 25 個名額,後 10 個要等人把存活處置掉才輪得到。
  - 每個存活又是 z1 的 T 次 Gradle。
  - S11 的預期值列只測了第一次(40 個跑 30 個),沒測第二次。
- 建議:挑選次序寫明為「帳上沒有任何 choice-kill 紀錄的行 > 其他」,並釘一條第二次呼叫的案例。

## z3 有效處置以 (file, line_sha) 為鍵,內容相同的兩行會互相遮蔽(第二輪改成「以行為單位」造成的退步)
severity: major
blocking: 是——照字面實作,一行真的存活的選擇點會因為別處同文字的行被殺掉而放行。

- spec 位置:〈用詞〉有效處置、壞法身分,對應第二輪分組 H4。
- 引句:「帳上同一個 (`file`, `line_sha`) 最新一筆是 `killed` 而且 `killing_test` 還在現在守的測試裡」
- 引句:「`file`、`line_sha`(那一行原文的 sha256 前 16 碼)、`row`(列號)、`new_sha`」
- 問題:壞法身分有 `row`,但有效處置的鍵沒有。同一檔裡文字相同的行很常見,例如 `if (page > limit)`、`.filter { it.isActive }`。
  - 帶上下文後它們各自唯一,所以兩行都會被各自跑一次(S3 只擋上下文也相同的)。
  - 例:Vm.kt 第 12 行被 t1 殺掉,第 80 行同文字、沒測試守著、存活。
  - 若殺掉的那行在帳上較晚(第 80 行先跑、第 12 行後跑),「最新一筆」是 killed,第 80 行的存活被當成已處置,推送放行。
  - 反過來,存活的那行較晚時,第 12 行被誤判成未處置。
  - 狀態取決於處理順序,`--only <定位>` 重跑單行也會翻轉另一行。
  - `choice-judge` 判一行,另一行同文字的也跟著被判。
  - 回報上限的種子用「曾經存活的行」身分集合,同文字的行會被併成一個,抽樣數也被扭曲。
- 建議:鍵加上能分出同文字行的欄位,例如 `old` 的雜湊或含上下文的行指紋。

## z4 「治理帳讀不到就擋」在預算耗盡時會把逾時當成讀不到,擋下本該放行的推送
severity: major
blocking: 是——照字面實作,逾時路徑會產生硬擋,和 spec 自己寫的「逾時只提醒」相反。

- spec 位置:〈範圍〉4 算不出來、S20。
- 引句:「整體逾時或讀不到 → 這一圈只提醒不擋並記一筆 kind `unverified`」
- 引句:「治理帳在 B 不存在或讀不到 → 擋」
- 問題:兩句都用「讀不到」,分界沒寫。
  - spec 指定的 `_gov_rows_at` 帶 `deadline` 時,剩餘不足 1 秒就回 `"unreadable"`(`scripts/lumos:64923`),跟 git 真的讀不出分不開。
  - 若 ast-grep 掃描或讀檔先把 `_KT_SIT_BUDGET` 吃掉,帳才被讀,結果是硬擋、reason「帳讀不了」,而不是 `unverified`。
  - 原註解寫這個期限是「推送前核對跟表態那一道共用期限」(`scripts/lumos:39986`)。spec 沒說新一圈是獨立 30 秒還是共用剩餘。若共用,大推送(最需要檢查的)會系統性落到這條路。
  - `_kt_sit_read_many` 對任何超過 4MB 的單檔會整批 raise(`scripts/lumos:40130`),不是「那支檔跳過」。字面實作會讓整圈 unverified,等於推一個大檔就繞過整道閘。
- 建議:帳讀不到要區分「預算用完」(算 unverified)和「git 回錯」(擋)。大檔要先用 `_nodehome_cat_sizes` 篩掉再讀。

## z5 第一個中斷訊號「讓配方收尾」跟現有處理與 `cmd_guard_kill` 介面對不上
severity: minor
blocking: 否——兩種實作都會留下完整判定的壞法,只有行為跟 spec 描述不同。

- spec 位置:〈範圍〉2 中斷、S12。
- 引句:「第一個訊號:讓正在跑的那條配方收尾,已經由 `on_row` 交出結果而且判定完整的壞法照記」
- 問題:「沿用」的 `_situation_rule_signals` 預設第一個訊號就丟 `KeyboardInterrupt`,`_kill_run` 當場收掉程序群組(`scripts/lumos:27794`)。沒有「讓它收尾」。
  - 要做到「收尾」得用 `defer=True`,並讓迴圈在配方之間檢查停止旗標。
  - spec 的新參數只有 `source`、`stop_group_on_kill`、`on_row`,沒有停止檢查點。若 `defer=True` 又沒檢查點,第一個 Ctrl-C 會被吞到整次呼叫結束。
  - S12 的預期「前 2 到 3 個記帳」太鬆,抓不出這兩種實作的差別。
  - 另外 `on_row` 的例外(例如帳寫失敗)沒說要不要中止整次。
- 工作樹登記與強制結束:強制結束只印路徑,留到一天後被下一次帶 `recipes_override` 的呼叫清掉(`_isolated_worktree_sweep`),不會憑空堆積。Android 工作樹含 build 目錄可能數 GB,殘留可達一天。測試程序群組能收,但 Gradle daemon 自己另開 session,收不掉。這是現有「誠實邊界」,不是新問題。

## z6 `stop_group_on_kill` 要判「強」、`on_row` 要交完整列,但這兩個值現在在迴圈結束後才算
severity: minor
blocking: 否——實作者補上就是了,只是 spec 沒講。

- spec 位置:〈用詞〉殺掉判定。
- 引句:「`on_row` 回呼在每條配方跑完時交出那一列」
- 問題:`weak`、`recipe_id`、`covers` 在迴圈外才蓋章(`scripts/lumos:28139-28148`)。
  - 迴圈中途交出的列沒有 `weak`。
  - 要判強 killed 得在迴圈內重算 `ws`(run_cmd 沒有 `{method}`)、`flaky`、`node_dirty`、`_mtime_unsure`。
  - 對 kotlin-junit 加乾淨工作目錄,只剩 `_mtime_unsure` 會變動。若實作者把缺的 `weak` 當 False,mtime 沒錯開的弱證據會被當強殺而提前停。
- 「略過」列的 verdict 字串與 icon、rc 對應也沒定義。預設路徑要確保它不影響 rc 優先序(見固定席)。

## z7 推送前的暫存檔:怎麼建、怎麼清、跑幾次 ast-grep 都沒寫
severity: minor
blocking: 否——不照字面做也能對,但容易寫出殘留與逾時。

- spec 位置:〈用詞〉語法樹掃描、〈範圍〉4 讀哪一版。
- 引句:「改到的檔用 `_kt_sit_read_many` 讀 B 版(交 ast-grep 的是暫存檔,掃完刪)」
- 引句:「`ast-grep scan --config <那份設定> --json=stream <檔>`」
- 問題:
  - 單檔寫法暗示每檔開一次程序。300 個 `.kt` 就是 300 次規則載入,容易吃光 30 秒預算而落到 unverified(放行)。應該一次掃一個暫存目錄。
  - 「掃完刪」沒講逾時、例外、被中斷時要不要刪。暫存檔該放在 `tempfile.TemporaryDirectory`(finally 清),逾時要連 ast-grep 子程序一起收。使用者全域規則特別提過暫存累積推高 fseventsd。
  - 現成零件沒提:`_lint_new_extract`、`_lint_new_run_cmds`、`_lint_new_clean_stale`、`pgid_file`(`scripts/lumos:43165`、`scripts/lumos:43653`、`scripts/lumos:43306`)。
  - ast-grep `--json` 的行號是 0 起算(我對照記憶,沒在這台機器驗,它沒裝),而「改到的行」是 diff 的 1 起算。spec 沒寫換算。

## z8 帳量 ≤4096:做得到,但 S20 量的不是會長大的欄位
severity: minor
blocking: 否——做得到,但驗收條款量的是不會隨 T 變大的欄位。

- spec 位置:〈範圍〉5、S20。
- 引句:「實作量一筆 `choice-kill` 事件在守的測試 30 支時的位元組數,要在 4096 以內(S20)」
- 引句:「`reason` 的失敗摘錄限 300 字」
- 問題:
  - choice-kill 事件只存 `tests_sha`,事件大小跟「30 支測試」無關,S20 的「30 支」是空的。真正會長的是 `plans`、`clauses`、`file` 路徑。
  - `_gate_event_build` 會把 `note` 又複製成 `detail`,再加 `nodes`、`head_sha`、`attempt_id`(`scripts/lumos:1595`)。
  - 300「字」以 UTF-8 計約 900 位元組。摘錄若同時進 `note` 與 `detail` 就是 1800。
  - 估算:5 份計劃名稱各約 100 位元組、`nodes` 與 `plans` 各一份,合計接近 4096。
  - 既有 `_gate_event_fit`(`scripts/lumos:1885`)正是量整行並從尾端丟清單鍵的零件,spec 沒提它。
  - `run` 那筆的測試對照隨 T 線性長大,走 `_gate_event_fit` 會被截,「對照」就不完整,而紀錄的守的測試所在檔物件編號要靠它做新鮮度提醒。
- 另:`_GOV_FIELD_TYPES` 已有 `row: (str, None)`(情境題用)。spec 的 `row` 一邊寫「列號」(`C-<n>`,字串),一邊又用「行號」,若寫成整數,`cmd_gov` 會整行丟棄。

## z9 對照論文:`delay` 陳述本身該是乾的;其餘差異的後果
severity: minor
blocking: 否——多一些噪音存活,可以靠人判處置。

- spec 位置:〈用詞〉乾節點規則「時間」。
- 引句:「時間(`delay`、`withTimeout`、`withTimeoutOrNull` 呼叫的引數節點;A.1.4)」
- 論文 A.1.4 的第一個例子就是刪掉整個 `SleepFor(...)` 陳述(第 15 頁),內文講的是「statements invoking sleep-like functionality」。spec 只讓引數乾。
  - SBR 仍會把 `delay(x)` 陳述刪掉。
  - `runTest` 的虛擬時間下刪 `delay` 多半存活,這是論文明講會造成的無用壞法。
- 論文核對其餘幾處:
  - 表 1 候選正確。
  - Listing 2 的類別洗牌正確。
  - 2.3 的「檔數 × 7」正確(論文是「total files in the changelist」,spec 的「所有種類」忠於原文)。
  - 公式 1 正確。
  - A.1.23 `==` 只換 `!=` 正確。
  - spec 沒處理 `===`/`!==`(Kotlin 文法兩者都是 `equality_expression`,`scripts/lumos` 無關,見 grammar.js:1651)。
  - 差異①(無覆蓋率)的後果見 z1。
  - 差異②(擋推送)的代價:噪音由人吃,論文是不強制的提示。

## z10 公式 1「複合節點全子節點乾才乾」在 ast-grep 輸出裡算不出來,也其實用不到
severity: minor
blocking: 否——候選種類只有六類,改用「候選的祖先或自己落在乾節點範圍內就扣掉」即可。

- spec 位置:〈用詞〉乾節點規則結尾。
- 引句:「乾節點範圍內的節點不產生壞法;複合節點照公式 1:只有所有子節點都乾才整個乾。」
- 語法樹驗證:節點名都存在於 grammar.js。
  - 存在的節點:`comparison_expression`、`equality_expression`、`conjunction_expression`、`disjunction_expression`、`additive_expression`、`multiplicative_expression`、`prefix_expression`、`call_expression`、`navigation_expression`、`statements`、`lambda_literal`、`call_suffix`、`value_arguments`、`real_literal`。
  - `if_expression` 有 `condition` 欄位。
  - `while`、`when` 沒有欄位,只能用 pattern。
  - 二元運算子沒有欄位名,運算元靠 pattern 的 `$A`/`$B`,運算子 token 不是具名節點。
  - 我讀 grammar.js 與記憶判斷,`kind` 選不到運算子,得靠 pattern。
- 問題:ast-grep 只輸出命中節點,拿不到「所有子節點」,lumos 沒法算公式 1。
  - 「乾範圍包含候選」這條簡單規則就覆蓋 S4 的全部列。
  - 例:`if (BuildConfig.DEBUG) { Log.d(TAG, "x") }` 裡的 `Log.d(...)` 被 log 規則扣掉。
  - 例:`BuildConfig.DEBUG && x > 1` 的 `x > 1` 不在乾範圍,照挑。
  - `if` 本身不是六類候選,所以不需要整個標乾。
- 補充:SBR 的「`lambda_literal` 最後一個陳述不刪」會把 `launch { repo.load() }` 這種 Android 最常見的單句 lambda 全排除。這是保守側的天花板,不是錯。
- 補充:規則 `if (x) foo()` 這種無大括號本體,`control_structure_body` 直接掛 `_statement`,不在 `statements` 下,「statements 的直接子節點」本來就排除了它,第二條多餘但無害。

## 固定席逐條判
- `Systems/guard-kill` INVARIANT「rc 優先序:survived→rc1、drifted/abort/error→rc2、弱證據不放行執行錯誤」——不影響。
  - 三個新參數預設不傳,行為不變。
  - 基準 abort 拿掉是 choice-kill 自己判,不改 `cmd_guard_kill` 的 rc 規則。
  - 要守住:`choice-kill` 不要拿 `cmd_guard_kill` 的 rc 當判定,只用 `rows`。「略過」列不可被記成上述任一 verdict(z6)。
- `Systems/guard-kill` INVARIANT「--json 成功跑完時 stdout 恰一行合法 JSON」——不影響。
  - `choice-kill` 不走 `as_json`。
  - 新增的「略過」列、強制結束印路徑、`on_row` 進度若寫到 stdout,要照 `_keep_out` 在 `as_json` 時走 stderr,否則會破壞純度。
- `Systems/規格閘`(0 條合約,有 PITFALL「審查帳讀不到就擋」)——帳讀不到擋,spec 與它一致。
  - 但 spec 〈舊否決比對〉寫「只有治理帳讀不到才擋」(`scripts/lumos` 無關),而〈範圍〉4 與 S6 又新增「沒有 ast-grep 就擋」。這是自己的前後矛盾:前者的「照它」不成立,新機器與 CI 缺工具時被擋。
  - 見 z4 的 deadline 衝突。
- `Systems/kotlin規則包`——不影響。
  - 新增 `configs/ast-grep/kotlin-choice/` 與型錄兩節。
  - `check.py` 一般化讀表要保留情境決策表行為不變,spec 已寫。

## 第二輪折入核對
- 已到位:
  - H1:語法樹節點名與欄位核對通過(z10)。
  - H7:API 兄弟寫法的不收清單。
  - H8:choice-kill 不寫殺傷力帳本。
  - H9:論文表 1、Listing 2、A.1.23 引用已正確。
- 折入有退步或沒到位:
  - H4 的「有效處置以行為單位」引入 z3。
  - H3 的 `--max-mutants` 沒定次序,引入 z2。
  - H5 的「算不出來放行」與帳讀不到擋沒分清,見 z4。
  - H3 的 `stop_group_on_kill` 只擋強殺,見 z1。

## 實務隱患逐類
- 跑太久:z1、z2。
- 記憶體:無。22MB 帳以 `git show` 整檔讀入,`needle` 預篩後只保留相關行,估計峰值在百 MB 內。
- 磁碟與暫存:z7、z5 的工作樹殘留。
- 程序殘留:Gradle daemon 逃出程序群組是既有邊界(z5)。
- 帳成長:每次呼叫約 30 筆事件(各 ≤4KB)加一筆 `run`,以 22MB 現帳估計是每個功能約 1% 成長,可接受,但 `run` 的對照隨 T 長大(z8)。
- 逾時與 fail-open:z4。
- 並行:依立場不考慮。

最嚴重:major;blocking 共 4 條
