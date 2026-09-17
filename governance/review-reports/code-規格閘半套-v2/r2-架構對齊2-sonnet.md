severity: major

## 問①:`_SHALL_COMPOUND_PREV` 一串中文字當集合,本檔有沒有先例

字元屬於某字串做 membership test(`c in "…"`)這個寫法本檔有先例(`scripts/lumos:2391`、`scripts/lumos:17415`:`any(c in raw for c in "*<>?")`;`scripts/lumos:12197`:`all(c in "0123456789abcdef" for c in h)`),所以「用字串當字元集合」這件事本身不是新做法。但這三個先例都是行內字面值,不是拉成模組層具名常數;而緊鄰 `_SHALL_COMPOUND_PREV` 的兩個同角色常數 `_TRIGGER_WORDS`、`_TRIGGER_STOPWORDS`(以及再往上的 `_CLAUSE_HANG_STATES`)全部是 tuple。同一段常數群組裡,「一組要排除/比對的詞」一律用 tuple 表示,`_SHALL_COMPOUND_PREV` 卻改用一串字元的字串當隱式集合——同角色常數在同一個常數區塊裡出現兩種表示法。
不對齊(對照 `scripts/lumos:4652` `_TRIGGER_WORDS = ("若啟用", "當", "在", "若")` 與 `scripts/lumos:4653` `_TRIGGER_STOPWORDS = (...)` 皆為 tuple)。
severity: minor
引句:「_SHALL_COMPOUND_PREV = "反效因適回對相供答感響呼"   # 這些字後面的「應」是複合詞(反應/效應/因應…),不是「主體 應 回應」的應(代碼審 v2 r1)」

## 問②:`_shall_index` 放在 `_CLAUSE_SEP_RE` 旁邊,跟鄰居 helper 擺法一致嗎

一開始懷疑「函式插在常數群組中間、函式結束後緊接下一個常數、中間零空行」是破例,但機械掃過全檔後找到同形狀的既有先例:`scripts/lumos:167` `def _version_text()` 結束後緊接 `scripts/lumos:177` `WIKILINK_RE = re.compile(...)`,中間 0 空行;另外 `scripts/lumos:15392`、`scripts/lumos:18499`、`scripts/lumos:21382`、`scripts/lumos:25032` 也都是函式後 0 空行直接接下一敘述。函式前方仍維持標準兩空行(`scripts/lumos:4659-4660`)。
對齊(對照 `scripts/lumos:167`→`177` 同形狀:小函式插在常數/規則定義之間,結束後 0 空行接下一常數)。

## 問③:`while` 找下一個「應」的寫法 vs 本檔慣用的 `re.finditer`/`re.search` 帶 lookbehind

本檔處理「找某個 token,但要排除特定上下文(例如某些字元在它前面)」這類問題時,一貫做法是編譯一個帶負向 lookbehind/lookahead 的正則常數,呼叫 `re.search`/`re.finditer` 一次到位——例如 `scripts/lumos:6404`(`(?<!\w)` 排邊界)、`scripts/lumos:7427`、`scripts/lumos:8964`、`scripts/lumos:24947`、`scripts/lumos:25705`,全部是「排除清單」直接寫進負向斷言,一次呼叫解完。`_shall_index` 要解的其實是同一類問題(找「應」但排除前一字屬於某集合這種情境),`_SHALL_COMPOUND_PREV` 又剛好是固定字元集合,完全可以寫成 `re.compile(r"(?<![反效因適回對相供答感響呼])應")` 配 `.search()`,跟鄰居同一招。這支改用手寫 `while + str.find` 迴圈自己重造一次「跳過不合格匹配、找下一個」的邏輯,是本檔既有解法之外另立的第二種做法。
不對齊(對照 `scripts/lumos:6404`、`scripts/lumos:8964`、`scripts/lumos:25705` 皆用編譯正則+lookbehind/lookahead 一次呼叫排除上下文,而非手寫迴圈)。
severity: major
引句:「i = text.find("應")
    while i != -1 and i > 0 and text[i - 1] in _SHALL_COMPOUND_PREV:」

## 問④:測試⑨的寫法

`_sg_plan(kg, "反應", [...])` → `run(kg, "spec-gate", "Projects/反應_計劃")` → `check("⑨ …", r9.returncode == 1 and "S1(" in r9.stdout and "S2(" not in r9.stdout, r9.stdout[-500:])`,跟緊鄰的⑤⑦⑧三個測試(同樣 `_sg_plan`→`run`→`check`,同樣用 `returncode`+`stdout` 子字串斷言、失敗印 `stdout[-500:]` 或 `[-400:]`)完全同構,連編號注記風格(圈碼+一句中文說明+備註代碼審輪次)都一致。
對齊(對照 `scripts/test_lumos.py` 同函式內緊鄰的⑤(`r5 = run(...)`/`check("⑤ ...")`)與⑦⑧同寫法)。

不對齊共 2 條,其中 major 1 條。
