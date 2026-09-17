severity: major

## 問一:`_contract_key_matches(text, with_kind=False)` 這種「加旗標改回傳形狀」有沒有先例

對齊。本檔已有同精神先例 `_lens_git(repo_root, *args, quote=False, binary=False)`(file: `scripts/lumos:24646`)——`binary=True` 就整段改變回傳型別(bytes vs 解碼字串)。而且這支本身就是把「原本三處各寫一份合約行掃描」收斂成一支(patch 內註解:「★全檔唯一的『合約行』掃描★……派工鏡頭(`_lens_contract_lines`/`_lens_contract_rows`)與規格閘的相依回歸(`_contract_texts`)都走這裡」),方向與本檔反覆出現的「別再各寫一份」慣例一致,不是新引入的做法。

## 問二:`_lens_contract_rows`/`_lens_contract_lines` 兩個消費者現在的呼叫形狀

對齊,折法本身收乾淨。`_lens_contract_lines` 走預設(2-tuple:`(s, m)`),`_lens_contract_rows` 顯式帶 `with_kind=True`(3-tuple:`(s, m, kind)`)後重組成 `(kind, s)`;規格閘那邊的 `_contract_texts`(file: `scripts/lumos:4951`)也是預設呼叫,三個消費者形狀對得上各自的用途,沒有殘留舊的手寫迴圈版本。

## 問三:`_clause_grammar` 把觸發詞硬寫成 `("若啟用", "當", "若")` 子集而不是用 `_TRIGGER_WORDS`

不對齊。`_TRIGGER_WORDS = ("若啟用", "當", "在", "若")`(file: `scripts/lumos:4655`,原意是「一條文法的觸發詞」單一來源),但這次改法在 `_clause_grammar` 內另外字面重複寫出其中三個詞、把「在」拆出去單獨判斷,而不是用集合運算(例如 `_TRIGGER_WORDS` 減去 `{"在"}`)去推導。本檔對「常數定義了卻在旁邊另寫字面子集」沒有查到既有慣例(`_TRIGGER_STOPWORDS` 旁的註解「只准增不准刪」講的是那份表自己怎麼演進,不是「別在別處抄子集」),這是把來源拆成兩份、之後 `_TRIGGER_WORDS` 改動不會連動到這裡,屬於命名/一致性層級的偏移而非另立一套解析機制。
severity: minor
引句:「any(rest.startswith(w) for w in ("若啟用", "當", "若")) or (rest.startswith("在") and _CLAUSE_SEP_RE.search(rest))」

## 問四(含 `_rollback_check_lines` 訊息三段式 + `_plan_system_links` 剝括號正則)

`_rollback_check_lines` 的擋下訊息對齊本檔同群函式的既有寫法——`P ✗ — 原因` 一行、縮排補一行講代價/怎麼做,和 `_clause_grammar` 裡其他 `return False, "trigger", f"…"` 訊息同款,不是新樣式。

`_plan_system_links` 的剝括號正則不對齊。本檔已有 `link_target(s)`(file: `scripts/lumos:216`)明確定義為抽 wikilink 完整 target 的做法(去 `[[]]`、alias、heading、引號),且該函式的 docstring 直接寫著要靠它讓寫側 dedup 精確比對。這次 r2 的修法卻另開一條 `re.sub(r"^\[\[|\]\]$", "", str(x).strip().strip('"'))` 自己剝括號,而且下面幾行仍保留原本 `lk.split("|", 1)[0].split("#", 1)[0].strip()` 自己剝 alias/heading——等於在同一支函式裡疊出「剝括號用正則、剝 alias/heading 用 split」兩段手寫解析,跟 `link_target()` 一次做完是重複實作,而不是呼叫既有的單一入口。本檔對這種「別處已有規範函式,這裡另外手刻一份局部版本」屬於同批 patch 自己在別處(`_contract_key_matches` 的折法說明)明講要避免的模式,這裡卻沒套用到自己身上。
severity: major
引句:「re.sub(r"^\[\[|\]\]$", "", str(x).strip().strip('"')) for x in as_list(note.fields.get("lands_in"))」

不對齊共 2 條,其中 major 1 條。
