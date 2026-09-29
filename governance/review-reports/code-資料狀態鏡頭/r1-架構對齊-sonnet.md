severity: major

## F1 用正規表達式切「## 標題」到下一個「## 標題」之間的內容,跟鄰居的字串切法不同,是第二種做法
severity: major
blocking: 是
引句:「m = _re.search(r"^## 3\. Code-loop reviewer.*?(?=^## )", templates_text, _re.M | _re.S)」
說明:同一支 `scripts/test_lumos.py` 裡,「切出 templates.md 某個 `##` 小節、驗內容」這件事既有的三個既有寫法全是純字串切(`str.split`),沒有一處用 regex lookahead 做同一件事:
- `file: \`scripts/test_lumos.py:41250\`` → `sec = t.split("## 7.8", 1)[-1].split("\n## ", 1)[0] if "## 7.8" in t else ""`
- `file: \`scripts/test_lumos.py:41254\`` → `s77 = t.split("## 7.7", 1)[-1].split("\n## ", 1)[0]`
- `file: \`scripts/test_lumos.py:43770\`` → `sec = tpl.split("## 7.6", 1)[-1].split("\n## ", 1)[0]`

這份 diff 新增的 `_code_reviewer_prompt`(切「## 3. Code-loop reviewer」到下一個 `## `)與 `t_data_state_lens_doc_sync` 裡切「## 7. 平行 panel 派工」的那段,兩處都改用 `_re.search(r"^## N\. ….*?(?=^## )", text, _re.M|_re.S)`。同一支檔案、同一種任務(抓一個 `##` 小節)出現兩套做法,是本次審查標準明訂的「major=引入第二種做法」。全 repo(含 `scripts/lumos`)grep 這個 lookahead pattern 只有這份 diff 新增的兩處命中,不是既有慣例的延伸。
建議:改用鄰居的 `text.split("## 3. Code-loop reviewer", 1)[-1].split("\n## ", 1)[0]` 就能拿到同一段內容,不必引入新技巧。
判不準備註:regex 版多了「找不到就回 None」與「§7 那處用 `\Z` 收尾」兩個字串切法沒有直接對應的行為,但這兩點用 `if "## 3. Code-loop reviewer" in text else None` 與切完再 `.rstrip()`/`in text` 判斷同樣能達到,不構成非用 regex 不可的理由,故仍判 major 而非只是線索不足的 minor。

## F2 圍欄(```)擷取用了 `^`+`re.M|re.S` 的新變體,跟既有 fence 擷取寫法不同組合,但屬同技巧微調
severity: minor
blocking: 否
引句:「for body in _re.findall(r"^```[^\n]*\n(.*?)^```", m.group(0), _re.M | _re.S):」
說明:既有寫法在 `file: \`scripts/test_lumos.py:8006\`` 是 `_re.findall(r"```[a-z]*\n(.*?)```", text, _re.S)`,同樣是 regex findall 撈圍欄內容,只是新增了 `^` 錨點與 `re.M` 旗標(行首錨定,容許圍欄語言標記含中文/非 a-z 字元)。因為底層技巧(regex findall 撈 fence)跟既有做法相同,只是旗標/錨點微調,不到「第二種做法」門檻,列為 minor、不擋。

總結:不對齊共 2 條,其中 major 1 條。
