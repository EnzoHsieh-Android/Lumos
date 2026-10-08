severity: minor

我找到 3 條,都不影響回傳碼。

## 驗證做了什麼

- 在 `/tmp/lumos-seat-work/code-新寫句子寫法提醒/正確性-sonnet/w` clone 了一份(已含此 diff),跑 `python3.14 scripts/test_lumos.py -k note_wording`,22 passed、0 failed。
- 中文數字解析:十=10、十三=13、三十五=35、兩=2、二十=20、九十九=99,十十和二三回 None,都符合預期。
- 定義段切法:用差分對照 `scripts/lumos`、`scripts/test_lumos.py` 與 `scripts/*.py` 裡 932 個「恰好一處行首定義」的名稱。快速切法的成員數與整檔 ast 的成員數沒有任何不一致。
- 我造的容易切錯的寫法(段內頂格註解、反斜線續行、多行字串、`+` 串接、頂格鍵的字典、CRLF、非 UTF-8、150 層巢狀括號),結果都是回 None 或數對,沒有印出錯的數字。
- 效能:本 repo 全部 git 檔案建索引約 0.09 秒、峰值約 81 MB。餵 3000 個不同名稱,只算前 50 個有定義的,之後設 `py_capped`,上限擋得住。

## manifest 命中

這次 diff 新增的行(`scripts/lumos` 的 31291–31571、31975、31984、32034、32108、32756、32761、32777,以及測試檔新增段)上,2693 條裡沒有任何一條落在其中。沒有需要判真隱患或誤報的條目。

## 固定席

這次派工附的是「圖譜沒有釘到節點」備援段,沒有固定席筆記,不必逐條答。

## 本案隔離鏡頭(只提醒不擋)

- 讀設定:`_ns_wording_prepare` 自己有 try。
- 判定:`_ns_wording_collect` 包住 `_ns_wording_hints`。`pairs.table()` 失敗時只設旗標並回空表,不會丟例外。
- 印出和記帳:`_ns_wording_emit` 整段包 try。
- 呼叫位置:`_ns_wording_prepare` 和 `_ns_wording_emit` 都在 `cmd_note_shape` 的 rc 算完之後或不影響 rc 的位置。
- 我沒找到會改 rc 或影響另兩組提醒的漏網例外。唯一漏出去的是 F2 的 `SyntaxWarning` 雜訊,它是警告,不是例外。

## 新舊互讀

- 舊設定檔沒有 `note_shape.wording`:預設走 warn,測試有覆蓋。
- 帳面多一種 `check=wording`:`tag-hints` 與 `close-summary` 早就用同樣形狀寫 `check` 欄,而且 `("note-shape","hinted")` 本來就在本機帳白名單裡。讀帳端不會因此出錯。

## 位置規則的取捨

- 位置規則對 `(更正:第三項)` 和 `(更正:第 十 項)` 都會提醒。
- 「第 2 行」「第 3 節」「第 3 步」這類在更正括號裡的字樣也會被當成位置提醒。
- 這兩點是設計取捨,警語已寫明「不是在指清單項目就不用理」,所以不列為 finding。

### F1 更正括號只看最外層,外層不是更正括號時,裡面的更正會被漏掉
severity: minor
blocking: 否 — 只是漏提醒,不影響判定與回傳碼。
引句:「最外層的括號群 → [(起, 迄)];半形與全形混用、可巢狀,沒收尾的不算。」
失敗場景:
- 輸入 `說明(見 `KINDS`(更正:第 3 項))`。
  - `_ns_wd_paren_groups` 只吐最外層的 `(見 …)`。
  - `_NS_WD_FIX_RE.match` 在最外層那一組開頭比對不到「更正」,內層的更正括號永遠沒被看到。
  - 實測 `_ns_wd_line_hit` 回 `None`。
- 輸入 `說明 :-( 然後 (更正:第 3 項)`。前面有一個沒收尾的左括號,`depth` 一直大於 0,後面的更正括號永遠不收尾。實測同樣回 `None`。

### F2 解析定義段會把 SyntaxWarning 印到 stderr,打破「只印一句」的承諾
severity: minor
blocking: 否 — 只是雜訊。
引句:「mod = ast.parse("\n".join(seg))」
失敗場景:
- 被點名的名稱定義成 `PATTERNS = ("\d+", "\w+")` 這種含無效跳脫的字串常數。
- 走到 `_ns_wd_def_count` 的 `ast.parse`。
- Python 3.14 預設會對每個無效跳脫印 `<unknown>:1: SyntaxWarning: "\d" is an invalid escape sequence...`。
- 整支檔裡沒有 `catch_warnings` 或 `simplefilter`。
- 最小重現(結果照樣回 2,提醒照常印,多兩行警告):
  `python3.14 -c "…m._ns_wd_def_count('K = (\"\\\\d\", \"\\\\w\")\n',0,'K')"`
  輸出兩行 SyntaxWarning 後回 2。
- 提交每次只要點名這類名稱就會多出這種雜訊。

### F3 「行首定義」的正規式連三引號字串裡頂格的假定義也算,會印出指向不存在定義的標記
severity: minor
blocking: 否 — 只是提醒,貼上去後 drift scan 會自己判出來。
引句:「_NS_WD_DEF_RE = re.compile(r"^(?:([A-Za-z_][A-Za-z0-9_]*)\s*(?::[^=\n]*)?=(?!=)|class\s+([A-Za-z_][A-Za-z0-9_]*))", re.M)」
失敗場景:
- 名稱唯一的「行首定義」在三引號字串或測試夾具裡。
- 輸入:`test_x.py` 內 `src = """\nDENYLIST = ["a", "b", "c"]\n"""`,筆記寫 `` `DENYLIST` 有 3 種 ``。
- 索引用正則而不是 ast,把它當成唯一定義,`_ns_wd_def_count` 也數得出 3。
- 實測印出 `[count:test_x.py::DENYLIST=3]`。
- 真實樣本:`scripts/test_lumos.py` 裡的 `DENY` 就是這種,快速數法回 39,但整檔 ast 的模組層根本沒有 `DENY`。

佐證行:
file: `scripts/test_lumos.py`(`DENY` 在夾具字串內頂格定義,我用差分腳本 `../t3.py` 印出 `NOT-TOPLEVEL scripts/test_lumos.py DENY 39`)

總結:共 3 條,最高 minor
