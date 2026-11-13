severity: minor

結論:沒有引入第二種做法(沒有 major)。新加的 `route_rule_hits_problems`、`api/` 目錄、共用核對、新節位置,結構方向都對得上。差異有 7 條,都是跟鄰居寫法不一致或計劃沒講清楚的地方。

## 1. 分層與依賴方向

**對齊的部分**
- check.py 向 scripts/lumos 借函式的方向沒變。`situation_sample_problems` 已經這樣做:`check.py:696-705`。
- 不放進 `catalog_problems`、另外在 `check()` 與 `--catalog-only` 串接,同樣照既有做法。
- `route_rule_hits_problems` 放在 `--sg` 完整模式,對應既有的分工:不需要 ast-grep 的靜態核對在 `catalog_problems`,要實跑 ast-grep 的在 `check()`。SARIF 探針也是這樣放:`check.py:1030-1037` 一帶。

**不對齊 A:路徑篩選在 check.py 組出一份新的**

「叫得出」要複製推送前「被問到」的篩選,但計劃同時規定不改 scripts/lumos。結果是 check.py 自己把 `_PITFALL_DIFF_TEST_PAT` 和 `_stack_changed_ok` 再組合一次。

真正的推送端篩選是 `_kt_situation_segments` 裡的一串條件,多一道 `_kt_sit_may_hit`:`scripts/lumos:39961-39962`。

日後推送端再加一道條件,check.py 的「叫得出」就會悄悄跟它分家。

專案對這種刻意的另一份有先例,做法是寫 WHY 加一支雙向比對的測試。例如 `_fence_regions`,綁了 `t_kotlin_template_fence_parity`。計劃沒有對應的 WHY,也沒有比對測試。

severity: minor
blocking: 否
引句:「先過推送前同一套路徑篩選」
file: `scripts/lumos:39961-39962`(完整的篩選串)與 `configs/ast-grep/kotlin-android/check.py:811-815`(「刻意的另一份」的先例註解)

**不對齊 B:新函式的簽名沒有照鄰居的注入方式**
- 計劃的 `api_decision_problems(lumos, catalog_text, api_dir, samples_dir, templates_text)` 沒收 `rules` 或主表 `rows`。
- 鄰居都是從外面傳進來:`wiring_problems(text, rows)`(`check.py:401`)、`stats_problems(text, rows, rules=None)`(`:616`)、`catalog_problems(rules)`(`:468`)。
- 「規則 <id>」要核規則在 `rules/` 底下、訊息開頭的編號對不對。這些資料只有 `load_rules()` 讀得到,所以新函式會自己再讀一次。
- lumos 載入失敗時怎麼回報,計劃沒寫。`situation_sample_problems` 的做法是回 `("<situation>", "…要載入 scripts/lumos:…")`(`check.py:703-707`)。三支新函式的 `lumos` 又是必傳的位置參數。
- 這個 ⚠ 不影響結構。`main` 和 `check()` 要載入一次再分別傳給三支,但計劃沒說。

severity: minor
blocking: 否
引句:「api_decision_problems(lumos, catalog_text, api_dir, samples_dir, templates_text)」
file: `configs/ast-grep/kotlin-android/check.py:401`、`:616`、`:696-707`

## 2. 命名與錯誤處理

**對齊**
- `*_problems` 的命名、回 `[(鍵, 原因)]` 的形狀、`_api_names` 加底線,都跟 r1 之後的鄰居一致。

**不對齊 C:`api/` 這個名字和既有的「API」撞了**
- 這個規則包裡的 `API` 已經是型錄主題前綴,指「API 一次性呼叫與網路」(`check.py:100`),也是規則檔名 `rules/api.yml`。
- 計劃再拿 `API 決策點`、`API 母體`、目錄 `api/` 去指另一件事,也就是協程函式庫的公開 API。同一個規則包裡,這個字有兩個意思。
- 鄰居的做法是這類資料放在 `samples/` 底下,例如 `samples/situation`、`samples/lint-wiring`,並用 `situation_dir()`、`wiring_dir()` 這種小函式回傳路徑。
- 計劃把 `api/` 放在規則包頂層,也沒有對應的取路徑函式。測試要換成暫存母體,只能靠參數傳 `api_dir`,預設值從哪裡來沒寫。

severity: minor
blocking: 否
引句:「`configs/ast-grep/kotlin-android/api/kotlinx-coroutines-core-1.10.2.klib.api`(新增)」
file: `configs/ast-grep/kotlin-android/check.py:376-377`(`wiring_dir`)、`:642-643`(`situation_dir`)、`:100`(`API` 主題前綴)

## 3. 第二種做法

專案原本沒有的只有「第三方釘版母體檔」這一種資料。這是新種類,不是跟既有功能重複。有三處「兩節共用」的接法要點名:

**不對齊 D:共用核對沒有單一入口,而且 API 那一節沒有「對應檢查」可以餵進去**
- 計劃說兩節「共用同一組值與同一套核對」,但沒有指名哪一支函式。
- 〈API 決策點〉的表只有「名稱 | 歸屬 | 理由」三欄,沒有「對應檢查」欄。
- 「規則 <id>」要核「訊息開頭引的編號等於對應檢查」,「範本 T<n>」要核「n 等於對應檢查列通電批次欄的值」。這兩個核對在 API 那一邊沒有對應檢查可以拿來比。
- 計劃沒說 API 那一邊的「對應檢查」從哪來。可能的來源是規則訊息開頭的編號,範本那邊則沒有來源。照現在寫法,兩邊最後多半是各寫一份,會漂。
- 同樣沒有指名的還有表的讀法。〈API 決策點〉、〈叫不出的壞寫法〉這兩張表,有四個消費者要讀:`api_decision_problems`、`bad_snippet_reach_problems`、`route_rule_hits_problems`、`stats_problems`。
- 既有的慣例是每張手寫表只有一支讀表函式,例如 `_pending_table`(`check.py:536`)和 `wiring_table`(`:380`)。計劃沒有命名這兩張新表的讀法。

severity: minor
blocking: 否
引句:「兩節共用同一組值與同一套核對」
file: `configs/ast-grep/kotlin-android/check.py:380-386`、`:536`(單一讀表函式的先例)

**不對齊 E:`route_rule_hits_problems` 另掃一遍壞例樣本**
- `check()` 本來就掃過一遍 `samples/bad`。迴圈 `for rule_id, f, _line in got` 拿到了行號,卻把 `_line` 丟掉(`check.py:1048-1052`)。
- 計劃的新函式自己用 `sg` 重掃一遍,等於同一份資料算兩次。
- 掃描逾時時怎麼辦,計劃也沒寫。`check()` 的做法是掃描回 None 就記一筆「跑不起來」,並用 `_TIMED_OUT` 旗標(`:1006`、`:1048-1050`)。
- SARIF 探針也是獨立再掃,所以有先例。但那是因為輸出格式不同;這裡是同一份資料,不同於那個理由。

severity: minor
blocking: 否
引句:「route_rule_hits_problems(sg, catalog_text, samples_dir)」
file: `configs/ast-grep/kotlin-android/check.py:1006`、`:1048-1052`

**不對齊 F:範本「壞寫法」小節要讀的是圍欄裡的程式碼,但既有讀法會把圍欄藏掉**
- 「範本 T<n>」核對要找 `### 壞寫法:<對應檢查>` 小節,API 那一邊還要看那一組小節的程式碼含不含這個名稱。
- 既有的 `template_sections` 走 `_visible_lines`,刻意把圍欄裡的內容全部藏掉:`check.py:851-858`、`:836-848`。程式碼正好都在圍欄裡。
- 要讀圍欄裡的內容,就得在 `_fence_regions`(`:811-833`)的基礎上另寫一支「取圍欄內文」的函式。計劃沒提。
- 沒有統一用這個基礎,就會出現第二套標題與圍欄判定,和 `Systems/kotlin規則包.md:40` 那條 WHY 的精神相反。

severity: minor
blocking: 否
引句:「範本那一組有 `### 壞寫法:<對應檢查>` 小節」
file: `configs/ast-grep/kotlin-android/check.py:811-858`;`skills/kotlin-idioms/test-templates.md:430`(`### 壞寫法:` 小節的實際長相)

## 4. 落點合不合理

落在 `Systems/kotlin規則包` 合理:新節、新自檢函式、母體檔都在它的負責範圍內。

⚠ 有一處位置沒講清楚。計劃只說新節放在「〈接電證據〉之後」,沒說在〈統計〉之前還是之後。
- 〈統計〉是型錄最後一節,`stats_problems` 取的是 `text[i:]` 一路到檔尾(`check.py:621`),不像 `_section` 會在下一個 `## ` 截斷。
- 新節若放在〈統計〉之後,統計的正規式會把新表當成統計範圍的一部分。
- 其他手寫節都排在決策表切片之外,新節放在〈統計〉之前才算跟鄰居一致。

severity: minor
blocking: 否
引句:「型錄在〈接電證據〉之後新增〈API 決策點〉節」
file: `configs/ast-grep/kotlin-android/check.py:616-626`(`stats_problems`);`skills/kotlin-idioms/checks-catalog.md:1072`(〈統計〉是最後一節)

不對齊共 7 條,其中 major 0 條。

審查的檔案
- 被審材料:`/Users/enzo/harness/lumos-d4-triggers/governance/review-reports/情境決策點窮舉與壞寫法要叫得出/r2-snapshot.md`
- 對照程式:`/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py`、`/Users/enzo/harness/lumos-d4-triggers/scripts/lumos`
- 對照型錄與筆記:`/Users/enzo/harness/lumos-d4-triggers/skills/kotlin-idioms/checks-catalog.md`、`/Users/enzo/harness/lumos-d4-triggers/docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md`
