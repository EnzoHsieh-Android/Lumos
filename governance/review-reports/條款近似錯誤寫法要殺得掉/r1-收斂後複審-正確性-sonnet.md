severity: major

## c1 `--line` 選定的那一行,在整支檔裡可能不是「恰好出現一次」,殺傷力判 drifted、永遠過不去
severity: major
blocking: 是——照字面實作,同內容的行或縮排較少的同文行會讓 `--line` 失效,clause-kill 與推送前那一道都卡死。
- spec 段落:〈用詞〉壞法、〈用詞〉有效紀錄、〈範圍〉2。
- 問題:spec 用「含原寫法整字的『行』」計數(恰好一行,多行給 `--line`),但 `old` 交給 `cmd_guard_kill` 與推送前新鮮度檢查時是整支檔的「子字串」計數。兩種單位不同,`--line` 只能消除「行數」的歧義,消不掉「子字串」的歧義。
- 具體例:檔內有兩行 `    .flatMapLatest { repo.search(it) }`(縮排 4 格)與 `        .flatMapLatest { repo.search(it) }`(縮排 8 格)。工具先報多行,使用者給 `--line 12`。此時 `old` 是 4 格那行,但它是 8 格那行的子字串,整檔 `count` 等於 2。
- 預期:`--line` 指定的行被視為唯一。實際:`cmd_guard_kill` 判 drifted(「old 命中 2 次」),spec 的 drifted 訊息只叫人「換 `--line`」,換哪一行都一樣。兩行文字完全相同時更是無解。
- 推送前那一道的「`old` 在推送版本恰好出現一次」是同一個子字串計數,同樣會誤擋,只能走免宣告。
- 佐證:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27935` 是 `cnt = src.count(r.get("old", ""))`,`cnt != 1` 判 drifted。人裁那邊也是用 `src.count(old)`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:75721`),但人裁的 `--old` 由人多寫幾個字,本案由工具取整行,沒有這個出口。
- 修法方向:`old` 要帶換行與縮排,並在建帳前用同一個子字串計數檢查;或把 `--line` 改成可以帶前後文。

## c2 〈用詞〉兄弟寫法宣告的合法集合是型錄「觸發字欄」,不是兄弟寫法;其中有非識別字,`\b…\b` 字面實作會當掉或對不到
severity: major
blocking: 是——spec 字面把「型錄觸發字」當成「識別字」,D-58 與 D-60 的觸發字不是識別字,實作會出錯。
- spec 段落:〈用詞〉兄弟寫法宣告(「原寫法與兄弟寫法都要是那一列『觸發字』欄裡的識別字」)、〈用詞〉壞法(`\b<原寫法>\b`)。
- 問題 1:觸發字欄混了與「兄弟寫法」無關的詞。D-4 列 `debounce`、`viewModelScope.launch` 也在觸發字裡,`debounce→flatMapLatest` 形狀合法,但它不是兩個互相替代的寫法。型錄列的「(換列)/例外」欄才是兄弟寫法的來源。〈實務隱患〉第一條「壞法限型錄同一列,列本身就是『選哪個要看需求』」對這種配對不成立。
- 問題 2:觸發字不全是識別字。實測 `_KT_DT_ROWS` 有 `Color(`(D-58)、`contains(`、`indexOf(`(D-60)、`proguard-rules`(D-48)、`viewModelScope.launch`、`Result.retry`、`chain.proceed` 等。
  - 照 spec 字面 `\b<原寫法>\b` 且沒做跳脫:`\bcontains(\b` 會丟 `re.error: missing )`,整個指令崩潰。
  - 做了跳脫:`\bcontains\(\b` 對 `names.contains(x)` 命中,對 `names.contains("a")` 不命中,因為 `(` 和 `"` 之間沒有字界,結果是零行 rc 2。
- 現有 `_kt_trigger_re`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:39183`)已經處理這件事:只在邊界是英數字時才加前後斷言,並且跳脫。spec 沒說沿用,卻另寫了 `\b…\b`。
- 修法方向:比對與換字一律沿用 `_kt_trigger_re`,並限定哪些列的哪些觸發字可當 `[near:]` 的兩端,或型錄新增「兄弟寫法」欄。

## c3 Kotlin 的 flatMapLatest 必有 import 行,「恰好一行」在旗艦例子 D-4 上幾乎一定不成立,且整字比對連註解與字串都算
severity: minor
blocking: 否——可用 `--line` 迴避,但 spec 預期值表的情境(S4 與 S12 都假設只有一行)與真實專案不符。
- spec 段落:〈用詞〉壞法、預期值表 S4、S12。
- 問題:`kotlinx.coroutines.flow.flatMapLatest` 是要明確 import 的擴充函式(除非用 `flow.*`)。真實檔案至少有 `import …flatMapLatest` 加一行呼叫共兩行,工具永遠回「多行,請給 `--line`」。
  - 實測:`re.search(r"\bflatMapLatest\b","import kotlinx.coroutines.flow.flatMapLatest")` 命中。
  - 壞法的搜尋沒有排除註解與字串。若實作改用別的寫法,檔內只剩一行註解提到 `flatMapLatest`,工具會唯一命中並把註解改掉,必然 survived。
  - 這個 survived 會被記帳,之後要改宣告就得人核可(存活後改寫)。
- 修法方向:找行時用 Kotlin 剝註解與字串的那套(型錄已有),並排除 import 行。

## c4 有效紀錄取「最後一筆」的篩選沒有 `test_name`,結果依執行順序而定
severity: minor
blocking: 否——只會誤擋,重跑被誤擋那支測試即可。
- spec 段落:〈用詞〉有效紀錄(「先篩出計劃、條款編號、第幾個、標記原文、條款雜湊都對得上的,再取檔內最後一筆」)。
- 具體例:條款綁 `t_a`(強)與 `t_b`(弱)。
  - 先 `--test t_a` 判 killed,再 `--test t_b` 判 survived。最後一筆是 survived,整條宣告被擋,即使 `t_a` 已經咬住。
  - 反過來,先 `t_b` survived、再 `t_a` killed,就放行。
  - 判定因此取決於使用者跑指令的順序,不是取決於「有沒有任何一支綁的測試咬得住」。
- 修法方向:篩選加上 `test_name`,或改成「現綁清單內任一支最新一筆為 killed」。同一道理也適用 `file` 與 `old` 不同的紀錄。

## c5 「存活後改寫」判法只看歷史上有過 survived,不看最新一筆;刪除或改寫已翻成 killed 的宣告也要人核可
severity: minor
blocking: 否——是多要一次人核可,不放行錯的。
- spec 段落:〈用詞〉存活後改寫、S9。
- 具體例:`[near:A]` 先 survived,補強測試後重跑判 killed。之後條款改字、把 A 換成 B,B 也判 killed。
  - 帳上仍有一筆 A survived,現在那行沒有 A,於是要求 `ack-survived`。
  - A 最新一筆是 killed,不該算「存活後改寫」。
- 另外:survived 紀錄與核可都綁 `clause_id`(S\<n\>)。計劃中途刪掉或插入條款造成重新編號時,S1 變成另一條條款,也會被誤要求核可。spec 沒說條款不存在或編號挪動時怎麼處理。

## c6 第幾個(`near_index`)寫進比對條件,刪除或重排任一個標記會讓其他標記的 Gradle 紀錄全部作廢
severity: minor
blocking: 否——放行不會錯,只是代價很高。
- spec 段落:〈用詞〉第幾個、有效紀錄。
- 具體例:一行有 `[near:M1] [near:M2]`,兩者都 killed(各要十幾分鐘 Gradle)。刪掉 M1,M2 的位置變成 1,帳上 `near_index=2`、`near` 相同,仍判缺紀錄。兩個標記對調位置也一樣。
- 標記原文已經是身分的一部分,`near_index` 只在「兩個一模一樣的標記」時才有用。
- 修法方向:索引只用來區分文字完全相同的標記,否則不納入比對。

## c7 `[near:]` 剝除規則沒說是否跳過反引號,與掃描的遮罩規則不一致
severity: minor
blocking: 否——只影響條款雜湊與引句比對,不影響放行判定。
- spec 段落:〈用詞〉掃描、S3、預期值表 S2 反引號那列。
- 問題:掃描先用 `_inline_visible_mask` 遮反引號,但剝除是「條款專用的正規式,只在 `_clause_body_of`」,spec 沒說這支正規式要不要遮反引號。
  - 若不遮,反引號裡的 `` `[near:D-4:…]` `` 被當標記剝掉。凍結審材 S12 本身就有這種句子。
  - 影響:`_clause_body_of(keep_code=True)` 的結果少一段引用文字。人裁引句與 `_clause_sha`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:13913`)用這份,改動那段說明文字不會改雜湊。
- 修法方向:剝除也先遮反引號,與掃描共用同一支遮罩。

## c8 「被推送版本取範圍右端,同 `_spec_gate_push_check` 解析範圍的方式」——該函式並不解析右端
severity: minor
blocking: 否——規格有「算不出就放行」的退路,但被引用的現成零件不存在。
- spec 段落:〈範圍〉3。
- 查證:`_spec_gate_push_check` 把 `git_range` 整串交給 `git diff`,沒有拆端點。現有的拆法只有 `_range_base`(只回左端點,`/Users/enzo/harness/lumos-near-miss/scripts/lumos:65111`)。
- 未規定的輸入:`A..`(右端為空)、`..B`、單一版本號(`git diff X` 其實是比對工作樹)。
- 更重要的是:治理帳 `_gov_vc_gate_events` 讀的是工作目錄的帳(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:23577`),不是「被推送版本」那一版。工作目錄有帳、但推送的提交沒帶到帳時,本機閘放行,CI 只讀提交內容會擋。
- 修法方向:另寫右端解析並規定空右端取 `HEAD`,帳也改從該版本讀。

## c9 殺傷力帳本讀者清單不完整
severity: minor
blocking: 否——只影響統計口徑。
- spec 段落:〈範圍〉4。
- 問題:spec 只提到 `_backing_kill_rows`「等」。`gov` 的 `load(".kill-log.jsonl")`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:18324`)沒有任何 `source` 過濾,人裁與 clause-kill 的 kill-log 列都會被算進 `gate: kill` 的統計。
- 現況:人裁那份已有同樣行為,但 S11 另外在治理帳算殺掉率,兩套口徑會並存。
- 修法方向:spec 明寫哪些讀者要跳過、哪些要保留。

## 固定席逐條判(Systems/guard-kill)
- ★INVARIANT★ rc 優先序:不影響。clause-kill 只新增選用參數 `source`,`cmd_guard_kill` 的 rc 判定不動,rc 優先序也不動。
- ★INVARIANT★ `--json` 純度:不影響。clause-kill 不走 `--json` 路徑,也沒改 `cmd_guard_kill` 的輸出。
- 附帶提醒:`source` 取代現行 `recipes_override is not None` 的條件(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28041`)時,不傳 `source` 的舊呼叫端行為要維持不變,否則 `lumos situation-rule` 的帳本欄位會漂移。

## 實務隱患逐類
- 注入與跳脫:有,見 c2(正規式沒跳脫會崩潰);其餘單人本地,不做加強。
- 檔案與路徑:`--file` 受平台根與非測試檔限制,沒找到新洞;`old` 與 `new` 超 500 字會 rc 2,真實的長單行 Kotlin 表達式會讓人只能走免宣告,算已知代價。
- 資源與效能:無新增。推送前只讀帳與讀檔,同 (提交, 檔) 有快取,不重跑 Gradle。
- 併發與交易:無,與 spec 自陳一致(單人單機依序)。
- 帳與一致性:見 c4、c5、c6、c8。

## 已讀無 finding
- 〈白話〉、〈舊否決比對〉、〈不做〉、〈依據來源〉、〈回退〉、〈天花板〉。
- 〈範圍〉1、5。
- 預期值表 S1、S3、S5 至 S7、S10 至 S12:引用的範圍與用詞章節都存在,說法一致。
- 補充:`[near:]` 剝除後 `_clause_sha` 對既有人裁紀錄的影響,在標記後接逗號或行尾兩種情境下推演一致,結論是雜湊不變(只有 c7 的反引號例外)。

最嚴重:major;blocking 共 2 條
