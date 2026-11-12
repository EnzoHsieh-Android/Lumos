severity: minor

**第 1 問,分層與依賴方向:對齊。**
- 新碼都放在原本的層。check.py 的 `_bad_lines`、`_unreach_table`、`_visible_lines` 是原地改,沒有新增跨層呼叫。
- 向 scripts/lumos 借函式的方式只有一種:呼叫端傳進來的 `lumos` 參數。新加的 `kept = lumos._strip_c_comments(...)` 跟它上一行 `code = lumos._strip_c_comments(...)` 同形。
- file: `configs/ast-grep/kotlin-android/check.py:1129`(修後版本,`code` 那行)、`:1130`(新加的 `kept`)。
- 修前 `git show 594f97e95b:…/check.py` 的 `_bad_lines` 只借同一支函式一次,修後借兩次,方式沒變。
- `_visible_lines` 沒有再添一條平行路徑。修前修後都是 `_scan(strict)` 先嚴格、再退回寬鬆,只改了 `keep_fenced` 時沒關圍欄的 hidden 集合。
- 它跟 scripts/lumos 的 `_visible_lines`(`scripts/lumos:5375`)是既有的兩份,修補還補了 `keep_fenced=True` 的對拍測試(測試檔 `t_kotlin_template_fence_parity`)。

**第 2 問,命名與錯誤處理:大致對齊,有一處小出入(見 2)。**
- 新常數 `_ANNOTATION_ONLY_RE` 放在模組層,緊鄰 `_BAD_MARK_RE`(`check.py:1106`、`:1107`),命名跟 `_BAD_MARK_RE`、`_ROUTE_RE`(`:782`)、`_SINGLE_IDENT_RE`(`:783`)同一套,行尾註解也同寫法。
- 讀檔失敗仍是 `probs.append(f"壞例檔 {f.name} 讀不了(...)")`。新增的行數對不上也是同樣形狀:`probs.append(f"壞例檔 {f.name} 去註解後行數對不上,…")`,沒有另外拋例外。
- `_unreach_table` 裡的 `re.fullmatch(r"`[^`]*`", c[2])` 用行內正規式。鄰居 `check.py:353` 和 `:832` 的 `re.fullmatch` 也是行內寫法,所以不算偏離。

**第 3 問,第二種做法:測試端有一處重疊,check.py 沒有新的第二種做法。**
- 修補鏡頭核對:`raw` 從 `splitlines()` 改成 `split("\n")`,沒有並存。`.startswith("@")` 被 `_ANNOTATION_ONLY_RE` 取代,舊寫法已刪。`_visible_lines` 只剩一套。
- 型錄 `.md` 的 D-4 列是資料,不是做法。

### 1. 測試裡又手切了一次型錄〈情境決策表〉一節,而且同一支測試內有兩種切法

severity: minor
blocking: 否
引句:「    _dt1 = _txt.find("\n## ", _dt0 + 5)」
- file: `configs/ast-grep/kotlin-android/check.py:295`(`_section(text, title)`,「從 `## <title>` 到下一個 `## `;找不到回 None」,檔內 8 處共用)。
- 修前版本:`git show 594f97e95b:scripts/test_lumos.py` 的 `t_kt_catalog_evidence_patterns` 對全檔數 `| D-n |` 列。修後版本(`scripts/test_lumos.py` 約 131161~131181 行)同一支測試裡有兩種切法。
  - 數列數:`_txt.find("\n## 情境決策表")` 加 `_txt.find("\n## ", _dt0 + 5)`。
  - 取列索引:`next(i for i, ln in enumerate(lines) if ln.startswith("## 情境決策表"))` 加 `next((i for i in range(_i_dt + 1, len(lines)) if lines[i].startswith("## ")), len(lines))`。
- 第一種跟 `_section` 的邏輯一樣,只是多了魔術數字 `+ 5`(`_section` 用 `+ 1`)和 `>= 0` 的退路。同一支測試後面就拿得到 `kp = _ktpack()`,可以直接用 `kp._section(_txt, "情境決策表")`。
- 代價:切節的邊界規則在測試端有第三種寫法。日後〈情境決策表〉標題改名或加內層標題,要改 check.py、這支測試的兩處,加上同檔其他 `find("\n## ")`,漏改一處就會靜默數錯。
- ⚠ 交編排者:測試檔裡原本就有兩派。
  - `find` 派:測試檔 `_apidp_set`(約 131791 行)和約 122974 行。
  - `next(startswith)` 派:約 127429 行。
  - 所以「測試切節」這件事專案本身沒有統一做法。我只把「check.py 已有 `_section` 卻沒用」和「同函式內兩種並存」判為小問題,沒有判重大。

### 2. `\|` 還原在 `_unreach_table` 內聯重寫,沒有走 `_snippets` 的共用出口

severity: minor
blocking: 否
引句:「        rows.append((c[0], c[1], sn[0] if whole else c[2].replace("\\|", "|"), c[3], c[4]))」
- file: `configs/ast-grep/kotlin-android/check.py:922`。`_snippets` 的 docstring 寫「主表壞寫法欄、決策表證據樣式、〈叫不出的壞寫法〉片段格都走這一支」,而 `:924` 的 `s.replace("\\|", "|")` 就是還原的唯一出口。
- 修前版本:修前 `sn[0] if len(sn)==1 and c[2].startswith("`") else c[2]`,不是整格的分支沒做 `\|` 還原。修後版本在非整格分支另寫一次 `.replace("\\|", "|")`,所以同一個格子在「整格是一段反引號」和「其他」兩條路徑各用一份還原邏輯。
- 代價:`\|` 的還原規則(例如日後要多處理 `\\`)要改兩處。docstring 也明寫「兩種都做 `\|` 還原」,說明作者知道這是並行兩份。
- 結構上沒有走偏:兩分支的結果型態一致,也沒有第二套切格子。

總結:不對齊共 2 條,其中重大 0 條,最高等級 minor
