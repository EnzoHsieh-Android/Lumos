severity: minor

結論:沒有引入第二種做法,也沒有跨層直呼,所以沒有 major。r2 我那一席報的 A 到 G 七條,結構上都修好了:路徑篩選改成共用、`rules` 改成傳進去、目錄改名並加取路徑函式、兩張新表各有一支讀表函式、掃描結果重用、`_fence_body` 建在 `_fence_regions` 上、新節放在〈統計〉之前。這一版剩下 6 條 minor,多半是 r2 修法只修了一半。

## 1. 分層與依賴方向

對齊的部分:
- check.py 向 scripts/lumos 借函式,方向跟既有做法一樣。`situation_sample_problems` 就是這樣接:`configs/ast-grep/kotlin-android/check.py:662-680` 的 `load_lumos`,加上 `:696-707` 的 `lumos=None` 再載入、載入失敗回 `("<situation>", …)`。
- 新自檢另外在 `check()` 與 `--catalog-only` 串接,不放進 `catalog_problems`。這跟 `:1017-1018` 與 `:1103` 一致。
- `_kt_sit_path_ok` 放在 scripts/lumos,由 check.py 呼叫。這比 r2 的「check.py 自己組一份」好,也沒有另抄一份。

不對齊 1:`_kt_sit_path_ok(rel)` 少了 `skip`,同一組條件在 scripts/lumos 還有一份內聯的沒收
- 推送端現在的寫法是 `_PITFALL_DIFF_TEST_PAT.search(rel)` 和 `_stack_changed_ok(rel, skip)` 一起判:`scripts/lumos:39961-39962`。`skip` 是消費專案裡原封不動的工具檔,由 `_vendored_skip(...)` 傳進來(`scripts/lumos:74296`、`:74779`)。
- 計劃把函式定成單參數 `_kt_sit_path_ok(rel)`,又說「行為不變」。這兩句無法同時成立:`skip` 要嘛丟掉,推送端行為就變;要嘛要加成可選參數,計劃卻沒寫。
- 同一組條件在 `scripts/lumos:69400` 還有一份(`not cur or _PITFALL_DIFF_TEST_PAT.search(cur) or not _stack_changed_ok(cur, vend)`)。計劃只改 `_kt_situation_segments`,這份沒提。
- 專案有先例要把這種內聯收成同一支:`scripts/lumos:65082` 的註解寫著「原本這裡內聯一份、那邊再抄一份」。

severity: minor
blocking: 否
引句:「抽成 scripts/lumos 的一支小函式 `_kt_sit_path_ok(rel)`(新增)」
file: `scripts/lumos:39961-39962`(完整條件含 `skip`)、`scripts/lumos:69400`(同一組條件的另一份)、`scripts/lumos:65082`(「原本內聯一份」的收斂先例)

## 2. 命名與錯誤處理

對齊的部分:
- `_api_table`、`_unreach_table` 加底線,對應 `_pending_table`(`check.py:536`)。
- `coroutines_api_dir()` 不加底線,對應 `situation_dir`(`:642`)、`wiring_dir`(`:376`)。
- `*_problems` 回 `[(鍵, 原因)]`。
- 目錄名不再跟 `API` 主題前綴(`:100`)撞。
- `rules` 改成傳進去,跟 `stats_problems(text, rows, rules=None)`(`:616`)一致。

不對齊 2:參數名 `main_rows` 遮住模組層的同名函式,跟鄰居的 `rows`、`text` 也不同
- 兩支新函式都用 `main_rows`、`catalog_text` 當參數名。
- check.py 有模組層函式 `def main_rows(text=None, problems=None)`(`:766`),參數名會把它遮住。
- 鄰居一律叫 `rows`、`text`:`wiring_problems(text, rows)`(`:401`)、`pending_problems(text, rows)`(`:556`)、`stats_problems(text, rows, rules=None)`(`:616`)。
- 這些鄰居的 `rules` 都有預設值 `None`;新函式的 `rules` 是必傳。

severity: minor
blocking: 否
引句:「bad_snippet_reach_problems(lumos, catalog_text, main_rows, rules, samples_dir, templates_text, scan_index=None)」
file: `configs/ast-grep/kotlin-android/check.py:766`(`def main_rows`)、`:401`、`:556`、`:616`

不對齊 3 ⚠:lumos 載入失敗的訊息由誰產生,計劃前後矛盾
- 計劃一邊寫 `api_decision_problems(lumos, …)` 收「已載入的模組」,由 `main` 與 `check()` 各載入一次再傳進去。另一邊又寫「lumos 載入不到 → 回 `[("<api>", "要載入 scripts/lumos:<原因>")]`,同 `situation_sample_problems`」。
- 函式收到的已經是模組,不可能自己回報載入失敗。
- 既有做法是 `lumos=None` 時在函式裡 `load_lumos()`,失敗才回那一句(`check.py:703-707`)。要照這個做,新函式就該是 `lumos=None`。要由呼叫端載入,就要寫明失敗訊息由 `main`、`check()` 產生。
- `check()` 已經呼叫 `situation_sample_problems()`,它自己會再載入一份(`:1018`)。載入 `scripts/lumos` 是整份執行,所以第二份是浪費。計劃沒說要把 `lumos` 也傳給它(它已經支援 `lumos=`)。

severity: minor
blocking: 否
引句:「lumos 載入不到 → 回 `[("<api>", "要載入 scripts/lumos:<原因>")]`」
file: `configs/ast-grep/kotlin-android/check.py:696-707`、`:1018`、`:1103`

## 3. 第二種做法

沒有「同一件事兩套做法」的 major。剩下 2 條是補洞。

不對齊 4 ⚠:`scan()` 回傳形狀改了,但呼叫端與索引的鍵沒交代;`scan_index=None` 也有兩個意思
- `scan()` 現在回 `(ruleId, file, 起始行)` 三元組,docstring 也這樣寫:`check.py:915-945`。
- 解構三元組的地方有 `:1048-1052`(`for rule_id, f, _line in got`)、`:1091`(`(i, f, _line)`),以及測試 `scripts/test_lumos.py:127382` 的 `m.scan(...)`。多回起訖行就會讓這幾處全部解構失敗。計劃沒列要改這些呼叫端。
- 索引怎麼鍵、涵蓋哪一份設定,計劃沒寫。`check()` 是在 `CONFIGS` 乘 `bad/good` 的迴圈裡掃(`:1046-1048`),只有 `rules/` 那份設定、`bad` 那一類才是改由要查的。
- `scan_index=None` 同時代表「沒有 ast-grep(`--catalog-only`,只做靜態核對)」。計劃又寫「`scan()` 回 None 時這道判問題」。函式分不出這兩種 None。既有做法是掃描失敗在 `check()` 就記一筆 `("<pack>", f"{cfg} 掃 … 跑不起來")`(`:1049-1050`)。

severity: minor
blocking: 否
引句:「`scan()` 改成多回每筆的起訖行(`--json=stream` 本來就有)」
file: `configs/ast-grep/kotlin-android/check.py:915-945`、`:1048-1052`、`:1091`、`scripts/test_lumos.py:127382`

不對齊 5 ⚠:`_fence_body` 只說建在 `_fence_regions` 上,圍欄的寬嚴退讓與小節標題判定可能長出第二套
- 專案的寫法是 `_visible_lines` 先用嚴格口徑,圍欄沒關就整份退回寬鬆口徑:`check.py:836-848`。`_fence_regions` 本身不含這個退讓。
- `Systems/kotlin規則包.md:40` 的 WHY 規定「範本標題只有 `TEMPLATE_HEADING_RE` 與 `template_sections` 一套」。
- 現有標題判定 `TEMPLATE_HEADING_RE` 只認 `## T\d+`:`check.py:756`。「壞寫法」小節是 `### 壞寫法:<編號> …`(`skills/kotlin-idioms/test-templates.md:430`、`:1445`)。
- 計劃沒說「`### 壞寫法` 標題」「小節的結尾」「同一組裡同編號出現兩次」(`test-templates.md:1464` 與 `:1482` 的 API-10)怎麼認。
- 讀小節要找標題、找結尾、讀圍欄,等於新增一套標題與圍欄判定。
- 既有的對齊測試 `t_kotlin_template_fence_parity`(`scripts/test_lumos.py:127623`)只比 `_visible_lines`,不比新的圍欄內文讀法。
- 這條是 ⚠:計劃可能打算沿用 `template_sections` 找組、`_visible_lines` 的退讓邏輯,只是沒寫。

severity: minor
blocking: 否
引句:「讀圍欄內文用 `check.py` 的 `_fence_body`(新增,建在既有的 `_fence_regions` 上)」
file: `configs/ast-grep/kotlin-android/check.py:756`、`:811-848`;`skills/kotlin-idioms/test-templates.md:1445-1482`;`scripts/test_lumos.py:127623`

## 4. 落點合不合理

落在 `Systems/kotlin規則包` 合理:新節、新自檢函式、母體目錄都在它的負責範圍內。`_kt_sit_path_ok` 放在 scripts/lumos、家是 `Systems/棧別提問表態閘`,也對:該篇的 about_code 列了 `scripts/lumos`,`_kt_situation_segments` 的 WHY 也在那篇(第 54、58 至 61 行)。新節放在〈接電證據〉(`checks-catalog.md:809`)與〈統計〉(`:1072`)之間,r2 的位置問題已解。

不對齊 6:改到棧別提問表態閘的程式,計劃的 `lands_in` 卻沒列它
- 計劃前置欄位 `lands_in` 只列 `Systems/kotlin規則包`,`related` 也沒有 `[[Systems/棧別提問表態閘]]`。
- 〈範圍〉6 卻要求在棧別提問表態閘補一句,而且 scripts/lumos 的改動(`_kt_sit_path_ok`)是在那篇的家。
- 專案規則(CLAUDE.md 鐵則 5):計劃要寫 `lands_in`(現況落在哪幾篇),改到的每支檔的家要同批更新。
- 同類先例:`Projects/Android寫法語意情境表態與盲判_計劃.md` 的 `lands_in` 列了棧別提問表態閘、pitfalls-code-loop、kotlin規則包三篇。

severity: minor
blocking: 否
引句:「`_kt_sit_path_ok` 的家是 [[Systems/棧別提問表態閘]],那篇補一句」
file: `docs/lumos-toolchain-knowledge/Projects/Android寫法語意情境表態與盲判_計劃.md:17-20`(`lands_in` 列三篇的先例)、`docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:12-15`(about_code 含 scripts/lumos)

不對齊共 6 條,其中 major 0 條。

審查的檔案
- 被審材料:`/Users/enzo/harness/lumos-d4-triggers/governance/review-reports/情境決策點窮舉與壞寫法要叫得出/r3-snapshot.md`
- 對照程式:`/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py`、`/Users/enzo/harness/lumos-d4-triggers/scripts/lumos`、`/Users/enzo/harness/lumos-d4-triggers/scripts/test_lumos.py`
- 對照筆記與型錄:`/Users/enzo/harness/lumos-d4-triggers/docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md`、`/Users/enzo/harness/lumos-d4-triggers/docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md`、`/Users/enzo/harness/lumos-d4-triggers/skills/kotlin-idioms/checks-catalog.md`、`/Users/enzo/harness/lumos-d4-triggers/skills/kotlin-idioms/test-templates.md`
