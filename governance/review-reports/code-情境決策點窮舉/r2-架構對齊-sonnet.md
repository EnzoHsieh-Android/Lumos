severity: minor

先說結論:這次修補多數真的收斂成一套。去註解走 `lumos._strip_c_comments`,`_norm_colon` 已刪、全改用 `_norm`,反引號切片段都走 `_snippets`,路徑正規化走 `_sample_abs`。剩下三處小地方不一致,沒有引入需要在兩套之間猜的第二種做法。

**第 1 問:分層與依賴方向。大致對齊,有一個舊遺留的並存。**
- `_bad_lines` 多收一個 `lumos` 參數,在 `_rule_route_problems` 用 `env["lumos"]` 傳入。`_parts_in_order`、`_word_in`、`_reachable` 都是同一個「載入後呼叫」寫法,沒有出現第二種借法。
- 對照:`configs/ast-grep/kotlin-android/check.py:1092`、`:959`。去註解呼叫在 `check.py:1125`,對應 `scripts/lumos:6869` 的全庫唯一入口。
- 並存處:`_fence_body` 改走 check.py 本地的 `_visible_lines(keep_fenced=True)`(`check.py:1155`),不走 `lumos._visible_lines`。同一檔裡,去註解是借 lumos,圍欄判讀卻是本地複本。
- 本地複本是修前就有的(`check.py:1314`、`:1339`)。這次補丁是替複本加了 `keep_fenced`,而 `scripts/lumos:5375` 早有同名旗標、語意相同。見發現 1。

**第 2 問:命名與錯誤處理。大致對齊,有一個行為小分歧。**
- 讀檔失敗用 `except (OSError, UnicodeDecodeError) as e` 加 `e.__class__.__name__`,跟 `_api_names`(`check.py:874`)同形。問題清單是 `(名稱, 訊息)` 形狀。
- `_bad_lines` 回 `(out, probs)` 二元組,跟 `_api_names` 的 `(names, probs)` 同形。
- `_HOMONYM_REASON` 加 `_norm(reason).startswith(...)`,跟 `_STOPWORD_REASON` 的寫法一字不差,對齊。
- `check()` 把 `why` 改名 `lumos_why`,命名較清楚,沒有衝突。
- 不一致處見發現 2、3。

**第 3 問:第二種做法。**
- 去註解、正規化(`_norm_colon` 併入 `_norm`)、`\|` 還原、路徑正規化都沒有新增第二套。
- 新舊並存:圍欄判讀的本地複本(發現 1)。表格片段格的切欄是 `_snippets` 加一個條件式回退,新舊兩種形狀並存(發現 2)。

**修補鏡頭對照(修前→修後)**
- 圍欄:修前 `_fence_body` 自己呼叫 `_fence_regions` 再組 `fenced` 集合;修後改走 `_visible_lines`。`_fence_body` 內只剩一條路,但 `_visible_lines` 本地複本仍和 lumos 版並存。
- `_norm_colon`:修前 `check.py` 自有;修後刪除、改 `_norm`,只剩一套。
- `_unreach_table`:修前 `c[2][1:-1]` 手剝反引號再 `.replace`;修後 `_snippets(c[2])`,但外面多一個條件回退。
- `_bad_lines` 去註解:修前 `ln.find("// BAD")` 加 `.split("//")[0]`(字串內的 `//` 會被截斷);修後走 `lumos._strip_c_comments`,只剩一套。
- 路徑:修前兩處各寫一遍 `str(f.resolve())` 與 `str(Path(f) if ... resolve())`;修後 `_sample_abs` 單一入口。

**發現 1:給本地圍欄複本加旗標,而不是呼叫已有同功能的 lumos 版**
severity: minor
blocking: 否
引句:「keep_fenced=True 時也留圍欄★內★的行(圍欄標記行本身照樣不留),同 scripts/lumos 的 keep_fenced。」
file: `scripts/lumos:5375`(`_visible_lines(lines, keep_fenced=False)`,有 `keep_fenced` 且只有這一個圍欄判定入口);`configs/ast-grep/kotlin-android/check.py:1339`(本地複本)。
代價:`_fence_body` 本來已拿得到 `env["lumos"]`,可以直接呼叫 lumos 版,卻去擴充本地複本。以後 lumos 改圍欄規則時,本地複本得手動同步,docstring 要寫「同…」這種人工對齊。這是修前就有的複本,所以只列 minor。此點⚠交編排者判斷:專案是否刻意讓 check.py 的圍欄判定脫離 lumos 載入(`_visible_lines` 也被不載入 lumos 的 `template_sections` 用,`check.py:1359`),若是則屬刻意取捨。

**發現 2:`_unreach_table` 用 `_snippets` 但保留條件回退,行為與主表不同**
severity: minor
blocking: 否
引句:「rows.append((c[0], c[1], sn[0] if len(sn) == 1 and c[2].startswith("`") else c[2], c[3], c[4]))」
file: `check.py:1079`;對照 `check.py:922` 的 `_snippets`(`\|` 還原是無條件的)。
代價:單一反引號片段走 `_snippets`,其餘(多片段、無反引號)回退成原始 `c[2]`,而且**不做 `\|` 還原**,修前是一律還原。同一個格子在主表是「全部切片、全部還原」,在這張表變成「兩種形狀」,接手的人要猜。比對用的 `_parts_in_order` 吃的是字串,回退分支會讓帶 `\|` 的多片段格比不到。

**發現 3:新增的函式前少一個空行,跟檔內其他頂層定義不一致**
severity: minor
blocking: 否
引句:「return out, probs」
file: 同一個 patch 區段裡的 `def _fence_body` 前只剩一個空行;`check.py:1141` 對照其他頂層定義之間一律兩個空行,例如 `check.py:1084` 的 `_norm_code` 前。
代價:純排版。修補時刪掉了 `_bad_lines` 後和 `_reach_unit_problems` 前的空行,ruff 預設規則不報,但跟鄰居的版面不同。

總結:不對齊共 3 條,其中 major 0 條,最高等級 minor
