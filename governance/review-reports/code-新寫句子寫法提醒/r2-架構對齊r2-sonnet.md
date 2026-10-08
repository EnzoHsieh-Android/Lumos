severity: major

**1. 分層與依賴方向**

對齊。新碼還是放在 `_ns_wording_*` 這一組,位置在 `_ns_tag_hints_*` 和 `_ns_negation_*` 之後。呼叫方向也一樣:`cmd_note_shape` 呼叫 `_ns_wording_collected`,再呼叫 `_ns_wording_emit`。這和 `_ns_tag_hints_collected` 接 `_ns_tag_hints_emit`(`scripts/lumos:31238`、`31249`)、`_ns_negation_collected`(`scripts/lumos:32932`)是同一形狀。

修補把原本混在 emit 裡的「印設定提醒、取 error」搬進 collected,和鄰居分工一致。我沒有看到跨層直呼。`_ns_wd_def_count` 現在整段交給 `_count_eval`(`scripts/lumos:36681`),這是往鄰居的唯一一份判法收斂,是改善。

小差異:`_ns_wording_collected` 回傳三元組 `(items, capped, fail)`,鄰居回兩元組。多出的 `capped` 是這組特有的需求,結構沒問題。

**2. 命名與錯誤處理**

大致對齊。
- 命名:`_ns_wd_*` 前綴和第 1 輪相同,`_ns_wording_collected` 對上 `_ns_tag_hints_collected`。
- 例外處理:`fail` 先印「沒跑完(類別名)」再 return,和 `scripts/lumos:31251` 同形。
- 記帳:hinted 帳走原有路徑。
- `_ns_wd_in_string` 接的例外清單,和 `_drift_py_names`(`scripts/lumos:35757`)、`_count_eval`(`scripts/lumos:36687`)那組 `SyntaxError, ValueError, MemoryError, RecursionError` 一致,另外加了 `tokenize.TokenError`。

不對齊的一處是 `_COUNT_NUM_EDGE` 那一行,見 F2。

**3. 第二種做法**

- `_ns_wd_in_string` 引入了第二種判法。專案裡「這行是不是落在字串裡」的既有做法是 `_drift_py_names` 用 `ast` 判:它的 docstring(`scripts/lumos:35747`)明寫「三引號字串裡的 def 被當成定義……改用 ast」,而且 `_py_declared_methods` 早就為同一個坑改用 ast。新函式改用 `tokenize` 自己建跨行字串的行區間表,還為 3.12 以前的 f-string token 寫了 `getattr(tokenize, "FSTRING_START", -1)` 的分支。我 grep 過整支 `scripts/lumos`,`tokenize` 只在這裡出現(其餘都是 `_rank_tokenize`,是別的東西)。計劃筆記給的理由是效能:整支 ast 解析在 3 MB 的檔上要 1.8 秒、350 MB,tokenize 約 0.25 秒。
- `_ns_wd_paren_groups` 改寫成 stack 版,吐每一層括號群。它和 `_ns_paren_groups_only`(`scripts/lumos:30493`,只回布林、只算深度)用途不同,不是重複實作,只是又多了一份括號配對。我判不算第二種做法。
- `_COUNT_NUM_EDGE` 是好的收斂。`_count_rewrite`(`scripts/lumos:36733`)原本寫死在 regex 裡的字集抽成共用常數,`_ns_wd_numbers` 改用它,兩邊同一組字,正是把第二份拿掉。
- `_ns_wording_collected` 沒問題,見第 1 問。

### F1 `_ns_wd_in_string` 用 tokenize 另寫了一套「定義在不在字串裡」的判法,既有的是 ast
severity: major
blocking: 是 — 判法一旦分成 ast 與 tokenize 兩套,drift 那邊的 `_drift_py_names` 和提交提醒這邊遇到「斷不了的檔」「新語法」「f-string」時會各說各話。⚠ 效能理由(0.25 秒對 1.8 秒)確實存在,是否接受交編排者裁。要是不想另開一套,可以讓 `_ns_wd_in_string` 也走既有的 ast 路徑,或在 `_drift_py_names` 旁邊補一個共用的「跨行字串行區間」工具。
引句:「用標準庫 tokenize 斷詞,一支檔只斷一次、只在有名稱要找它時才斷(3 MB 約 0.25 秒);斷不了的檔整支當作不能信、回 True。」
佐證行 file: `scripts/lumos:31386`
佐證行 file: `scripts/lumos:35747`

### F2 `_COUNT_NUM_RE` 的原註解被併到 `_COUNT_NUM_EDGE` 那一行末尾
severity: minor
blocking: 否 — 只影響讀的人:`_COUNT_NUM_RE` 失去「九位數以內」的說明,而同一行末尾多出一段和 `_COUNT_NUM_EDGE` 無關的舊註解,兩個 `#` 疊在同一行。這和鄰居「一個常數一段註解」的寫法不一致。
引句:「drift fix 與新寫句子的數量提醒共用     # 九位數以內:超長的數字轉整數會丟例外、整個 scan 停掉」
佐證行 file: `scripts/lumos:36513`
佐證行 file: `scripts/lumos:36514`

總結:不對齊共 2 條,其中 major 1 條
