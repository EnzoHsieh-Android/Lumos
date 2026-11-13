severity: minor

（總結：四問都沒有引入「第二種做法」，所以沒有 major。有 4 條 minor，都是接法或位置跟鄰居不同。）

## 1. 分層與依賴方向：大致對齊，有兩處接法跟鄰居不同

**對齊的部分。**
- check.py 呼叫 scripts/lumos 的方向沒變。
- 計劃要借 `_kt_trigger_re` 與 `_kt_sit_text_segments`，既有的 `situation_sample_problems` 也是這樣借，並且用同一個切段函式：`check.py:705`、`check.py:662`（`load_lumos`）、`check.py:727`。
- 型錄手寫節由 check.py 核對的模式，跟〈待查證〉〈接電證據〉〈統計〉一樣：`check.py:559`（`pending_problems`）、`check.py:401`（`wiring_problems`）、`check.py:616`（`stats_problems`）。
- 「規則 <id>」「範本 T<n>」兩種改由，重用既有的 `behavior_value` 與 `_TEMPLATE_VALUE_RE`（`check.py:759`）。
- 規則訊息的 `[型錄編號]` 比對，也跟 `catalog_problems` 同一套。
- 計劃拿「統計核對」守新增的數字，走的是 `_stats_expected` 的既有路（`check.py:578`）。

**不對齊 A：需要 scripts/lumos 的檢查，接的位置不同。**
- 計劃把 `api_decision_problems`（用到 `_kt_trigger_re`）與 `bad_snippet_reach_problems`（用到 `_kt_sit_text_segments`）都接進 `catalog_problems`。
- 既有的同類檢查 `situation_sample_problems` 同樣要載入 scripts/lumos，卻刻意不放進 `catalog_problems`。它在 `check()` 與 `--catalog-only` 另外串接：`check.py:1018`、`check.py:1103`。
- `catalog_problems` 的 docstring 寫「不需要 ast-grep」，現行內容也沒載入 scripts/lumos（`check.py:469`）。
- 照計劃做，每次呼叫 `catalog_problems` 都會多載入一次 scripts/lumos。test_lumos.py 有很多測試用假型錄多次呼叫它，例如 `scripts/test_lumos.py:126907`、`:127431`、`:127456`。
- 計劃沒說 `rules=None` 時，「規則 <id>」那條怎麼處理。`catalog_problems` 的 `rules` 參數預設就是 None。
- 計劃也沒說要不要像 `situation_sample_problems(lumos=None)` 那樣開放注入已載入的模組。

severity: minor
blocking: 否
引句：「`check.py` 的 `bad_snippet_reach_problems`(新增,接進 `catalog_problems`)」
file: `configs/ast-grep/kotlin-android/check.py:1018` 與 `:1103`（需要 lumos 的自檢另串，不在 catalog_problems 裡）

**不對齊 B：新節的位置會落進 `catalog_problems` 的決策表切片。**
- 計劃的新節放在〈情境決策表〉之後。
- `catalog_problems` 把〈情境決策表〉到〈待查證〉之間整段當決策表（`dt = text[i_dt:i_pend]`，`check.py:472-475`），並用 `^\|\s*D-\d+\s*\|` 逐行認列。
- 〈叫不出的壞寫法〉表的第一欄是「列編號」，內容是 `D-n`。它會被這個迴圈當成決策表的列。
- 目前只因為欄數不是 8（計劃寫的是 5 欄）才被 `continue` 跳過。那行註解「已在 dt_table 報過」在這種情況下並不成立，因為 `dt_table` 在下一個 `## ` 就截斷了。
- 既有的手寫節（〈待查證〉〈接電證據〉〈統計〉）都排在這個切片之外。

severity: minor
blocking: 否
引句：「型錄在〈情境決策表〉之後新增〈API 決策點〉節」
file: `configs/ast-grep/kotlin-android/check.py:472-475`（切片範圍）；`skills/kotlin-idioms/checks-catalog.md:732` 與 `:801`（決策表與〈待查證〉的位置）

## 2. 命名與錯誤處理：命名對齊，回報形狀有細節沒寫（⚠）

**對齊。**
- 函式名 `*_problems` 與既有一致。
- 計劃說問題訊息「印列編號、對應檢查與片段」，跟既有回 `[(列編號, 原因)]` 的方向一致。
- 「問題帶 `<catalog>` 之類的佔位鍵」是既有慣例，例如 `check.py:559` 的 `pending_problems`、`check.py:616` 的 `stats_problems`。

**不對齊 ⚠：**
- 計劃沒有說這兩支自檢的回報形狀。
- 〈API 決策點〉表是以「名稱」為鍵，不是列編號。回的 tuple 第一格該放名稱還是 `<catalog>`，沒定。
- 計劃新增的 `api_names` 沒加底線。它是提取輔助，不是測試要讀的資料位置。
- 既有的公開例外有寫理由：`situation_dir` 與 `wiring_dir` 給測試讀樣本目錄，知識筆記裡有 WHY。計劃沒寫 `api_names` 為什麼要公開。

severity: minor
blocking: 否
引句：「叫不出、表上又沒有 → 問題,訊息印列編號、對應檢查與片段。」
file: `configs/ast-grep/kotlin-android/check.py:401`、`:559`（回報形狀範例）；`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:62`（公開例外要寫 WHY 的先例）

## 3. 第二種做法：沒有，但 `.api` 是新的存放類型（⚠）

**沒有第二種做法。**
- 觸發字比對、切段、讀型錄表，都沿用既有函式。沒有另寫一套讀表，也沒有另寫一套觸發字比對。
- 頻率門檻 8% 沿用 `STOP_TRIGGERS` 的 E9 口徑（`check.py:150`、`:160`）。
- 「從語料統計常見寫法」已被計劃自己否決。

**不對齊 ⚠：**
- 「原檔逐位元組放進 repo 的第三方檔」在這個規則包裡沒有先例。
  - 既有的規則包資料，樣本是自己寫的 `.kt.txt`，規則是自己寫的 yml。
  - 外部來源則是在型錄寫網址，不把檔案放進 repo。
- 這不算「第二種做法」，因為原本沒有同功能的東西；只是 `configs/ast-grep/kotlin-android/api/` 是新種類的目錄。
- 計劃只說「逐位元組放」，沒有任何機制驗證放進去的是官方原檔，例如雜湊或版本行比對。
  - 對照〈接電證據〉：樣本檔名與存在性有檢查，`check.py:456`。
  - 沒有驗證的話，手改過的 `.api` 檔會被當成官方母體。
- 樣本檔的副檔名特意用 `.kt.txt`，是為了不讓推送閘把它當產品碼（知識筆記有 WHY，`Systems/kotlin規則包.md:33`）。計劃沒說 `.api` 會不會被判成程式。
- 計劃要把 `.api` 加進 `about_code`。但這個筆記的 `about_code` 現在連 rules 與 samples 都沒逐一列，只列 check.py、型錄、sgconfig、utils yml 等，所以這個寫法跟現有 `about_code` 的列法不同。

severity: minor
blocking: 否
引句：「照官方該版標籤的原檔逐位元組放」
file: `configs/ast-grep/kotlin-android/check.py:984-995`（`_sample_owner`、`good_cases`，樣本目錄的既有處理）；`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:8-17`（`about_code` 現況）

## 4. 落點合不合理：合理

- 計劃寫進 Systems/kotlin規則包，是對的。
- 這個節點的負責範圍是「Kotlin/Android 寫法的 ast-grep 規則包（規則、樣本、自我檢查）與型錄 checks-catalog.md 的格式」。新增的兩節型錄與兩支自檢都落在這個範圍內。
- 同類的先例都寫在這一篇：`stats_problems`、`pending_problems`、`wiring_problems`、`template_problems` 的 WHY 都在這裡，例如 `Systems/kotlin規則包.md:57`、`:60`。
- 該筆記現在 112 行、約 41.9KB，有 60 多條 WHY。再塞 2 條 WHY 與一個新檔的家，塞得進去，不需要另開。
- 計劃一併說會改 scripts/lumos 的測試（`t_kt_situation_api_family_e2e`）。scripts/lumos 的 `_kt_*` 本身屬於 [[Systems/棧別提問表態閘]]，計劃不改它的判定，所以沒有越界。

不對齊共 4 條，其中 major 0 條。

審查的檔案：
- 被審材料：`/Users/enzo/harness/lumos-d4-triggers/governance/review-reports/情境決策點窮舉與壞寫法要叫得出/r1-snapshot.md`
- 對照程式：`/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py`
- 對照程式：`/Users/enzo/harness/lumos-d4-triggers/scripts/lumos`
- 對照型錄：`/Users/enzo/harness/lumos-d4-triggers/skills/kotlin-idioms/checks-catalog.md`
- 對照筆記：`/Users/enzo/harness/lumos-d4-triggers/docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md`
