severity: major

# 正確性鏡頭 r3(修正差異 123aaf47..6400f52d)

## F1 樹上有一支檔名寫法特殊的程式檔,不帶路徑的條件就永久判不了,推送被擋,上一版不會
severity: major
blocking: 是 — block 模式下,正確的推送被永久擋下,而且提示沒講是哪支檔,推的人找不到原因
引句:「return None if self._unread[test] else False」
file: `scripts/lumos:22810`
file: `scripts/lumos:25922`
file: `scripts/lumos:26033`
file: `scripts/lumos:26172`

1. 讀不到的來源:`_nodehome_list` 把 ls-tree 列出的路徑一律轉成 NFC(`path = nfc(os.fsdecode(p))`),之後用「版本:NFC 路徑」讀內容;`_drift_cat_nfc` 讀不到時只多試一次「整條路徑轉 NFD」。git 裡存的寫法如果既不是 NFC 也不是 NFD,兩次都讀不到,那支檔就記成 None。實測兩種會這樣:
   - 同一條路徑裡混了兩種寫法,例如 `café/` 資料夾是組合字、裡面的 `café.py` 是分解字;
   - 檔名裡有 CJK 相容表意字(例如 U+F900「豈」;韓文漢字從 KS X 1001 轉過來常是這一段)。NFC 和 NFD 都會把它換成統一表意字,git 裡存的原字永遠對不上。
2. 情境一:新寫一條還沒成立的條件就被擋。repo 裡有 `src/豈文.py`(首字 U+F900),推送只在筆記新寫 `REVISIT:[when-symbol:not_yet_written][by:2099-12-31] 等它出現`,gate=block。
   - 這是新寫的行,old=False,一定是候選。
   - 在終點評估:語料找不到 not_yet_written,`_unread[False]` 是 True,結果是 None。
   - `_drift_probe_judge` 回 None,這一行記成判不了,判不了算要處理,rc=1。
   - 正確結果應該是「終點不成立、不列」,rc=0。上一版(123aaf47)跑同一個情境是 rc=0。
3. 情境二:只改那支檔的內容也會被擋。圖譜裡早就有一條不帶路徑的舊條件 `[when-symbol:someday_fn]`,這次推送只改 `src/豈文.py` 的內容(狀態 M,不算 code_shape)。
   - `_drift_probe_candidates` 裡的 `_tip_text` 只要改到的檔有任何一支讀出 None,就整份回 None。
   - 候選判定因此回 None,記成「git 讀不出這次改到的程式檔」,rc=1。上一版 rc=0。
   - 所以在這種 repo 裡,每次改到那支檔都擋,跟改了什麼無關。
4. 沒有出口:
   - 判不了是字串,不是發現,`drift ack` 表態不了。
   - 提示只寫「git 讀不出程式檔或筆記」,沒寫是哪支檔。
   - 推的人只能每次用 `LUMOS_SKIP_DRIFT_CHECK=1`,或把條件改成帶路徑。
   - scan 也會把圖譜裡每一條還在等的、不帶路徑的條件永久列成「判不了」。
5. ⚠ 筆記也是同一個根因:`_drift_tree_env` 這次把讀出 None 的筆記建成讀不出的筆記(diff 的 `bad.append(p[len(pre):])`)。
   - 檔名是相容表意字的筆記,每次被推送改到時,檢查都會算判不了(`scripts/lumos:25680` 只在 touched 時算)。
   - 這一點沒另外重現。
6. 修法方向:ls-tree 那一行本來就帶著 blob 的物件編號。一般檔直接用物件編號讀,就不會因為路徑寫法讀不到。另外,判不了的說明要點名是哪支檔。
7. 重現(在我自己 mktemp 的目錄,TMPDIR 也指到那裡):
   - 情境一:`/opt/homebrew/bin/python3 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/r3cor.QQ3J/repro1b.py <clone-ns>`
     輸出:`mixed= False check rc= 0` / `mixed= True check rc= 1`、`擋下:這次推送有 1 項判不了…Systems/Pay.md:16 的條件判不了(git 讀不出程式檔或筆記)`、`tree.one = None unread= {False: True}`
   - 情境二:`…/r3cor.QQ3J/repro1c.py <clone-ns>`,輸出 `check rc= 1`、`判不了(git 讀不出這次改到的程式檔)`
   - 同兩支腳本對上一版(`…/r3cor.QQ3J/prev`,123aaf47)都是 rc=0。
   - repro1.py 是混合 NFC/NFD 路徑那個版本,結果一樣(新版 rc=1,上一版 rc=0)。

## F2 規格說「不是候選的行,起點與終點結果一定一樣」,改版面分類的推送可以讓它不成立
severity: minor
blocking: 否 — 要用大寫副檔名這種少見寫法才觸發,而且這個缺口上一版就有,不是這次帶進來的
引句:「不是候選的行,起點與終點結果一定一樣,不評估。」
file: `scripts/lumos:22686`

1. 算不算測試檔,要看整棵樹的版面(`_nodehome_layout`)。版面用 `_testmap_ext` 取副檔名,會轉成小寫,而且整棵樹每條路徑都算,不管是不是程式檔。
2. 算不算程式檔,則是看 `_nodehome_code_kind`(大小寫敏感)。兩邊不一致,所以只改一支「不是程式檔」的檔,就能讓別的檔在測試與程式之間換類別。這種推送不在 code_touched 裡,也不觸發 code_shape。
3. 實例:
   - 起點有 `Foo/Main.SWIFT`(`.SWIFT` 不在程式副檔名清單裡,code_kind=None)和 `FooTests/Helper.swift`(內容 `func makeFixture() {}`)。依版面規則①,`FooTests/` 裡的 .swift 算測試檔。
   - 筆記有 `REVISIT:[when-symbol:makeFixture][by:2099-12-31] …`。
   - 推送只刪掉 `Foo/Main.SWIFT`。
4. 實測結果:
   - `is_test` 起點是 True、終點是 False;`symbol makeFixture` 起點 False、終點 True,條件從不成立翻成成立。
   - `_drift_probe_changes` 回 `code_shape: False, code_touched: []`,所以這行不是候選,check rc=0,沒列出來。
   - 同一棵樹跑 `drift scan` 會列「回頭條件成立了:1」。
5. 這次 diff 把第 0 節那句改寫了,「一定一樣」這個絕對說法還留著。要嘛把版面變動也算進 code_shape(樹上任何路徑的新增或刪除只要改到 `_nodehome_layout` 的結果就算),要嘛在〈誠實界線〉記下這個例外。
6. 重現:`…/r3cor.QQ3J/repro.py <clone-ns>` 的 R2 段,輸出 `is_test base/tip: True False`、`symbol makeFixture base/tip: False True`、`check rc= 0`、scan 印出 `[probe] 回頭條件成立了:1`。

## F3 正規化後再驗文法只補了一半:推送檢查照樣評估寫錯的行,而且 `a\..\x.py` 可以過、`a/../x.py` 卻被擋
severity: minor
blocking: 否 — 被評估的那幾行結果永遠是不成立,不會誤擋也不會漏擋;只是規則前後不一致
引句:「err = err or _probe_value_err(k, nv)」
file: `scripts/lumos:25803`
file: `scripts/lumos:26127`
file: `scripts/lumos:26280`

1. `[when-file:..\x.py]`:正規化後驗出錯,錯誤寫進 `errs`。但 `conds` 存的是原文 `..\x.py`(`conds.append((k, val if err else nv))`)。
2. 推送檢查的「寫錯的條件不評估」(`scripts/lumos:26127`)和 scan 的同一段(`scripts/lumos:26280`),都拿 `conds` 的原文重跑一次 `_probe_value_err`。原文用 `/` 切不出 `..` 段,所以回 None,這行被當成合法照樣評估。
   - 實測 `_probe_value_err('file','..\\x.py')` 回 None,symbol 的 `..\a.py::f` 也一樣。
   - 規格寫的是「條件本身寫錯的行不評估」,這裡對不上。現在結果永遠是不成立(除非樹上真有一支檔就叫 `..\x.py`),所以只是不一致,沒造成誤判。
3. `a\..\x.py` 經 normpath 收成 `x.py`,兩次驗都沒錯,會被接受。字面相同意思的 `a/../x.py` 卻因為原文有 `..` 段被擋。
   - 規格寫「不准 .. 段」,同一條路徑換個斜線方向結果就不同。
   - 實測:`file:a\..\x.py -> [] [('file', 'x.py')]`,`file:a/../x.py -> ['…不准 .. 段']`。
4. 重現:`…/r3cor.QQ3J/repro.py <clone-ns>` 的 R3 段;另外用 `/usr/bin/python3` 載入 scripts/lumos 跑 `_probe_parse('[when-file:..\\x.py][by:2099-12-31]')`,得到 errs 非空、conds 是 `('file','..\\x.py')`、`_probe_value_err` 回 `[None]`。

## 已看,無 finding
- 候選篩選(`_drift_probe_cond_candidate`):
  - 帶路徑的條件看 touched,type change(T)也算在 touched 裡。
  - 不帶路徑的條件在終點成立,表示某支語料檔有定義:那支檔如果被改到,名稱一定出現在終點全文;沒被改到,內容一樣、#! 判定一樣。唯一能讓它換類別的是版面,見 F2。
  - 子模組和連結檔不在 files 裡,texts 會濾掉,子模組更新不會造成讀不到。
  - 名稱的整字正則跟 `_defines` 的前置比對是同一個,前後一致。
- 起點判不了、終點成立:judge 回 None,記成判不了,判不了算要處理。結果跟「真的要處理」一樣是擋,只有說明不同,不算做錯事。新寫的行不問起點,不受起點讀不到影響。
- `_drift_decode`(utf-8-sig 加 replace)、`_head_is_shebang` 的語料門檻、`_shebang_line_is_python`:對沒帶 BOM 的檔,結果跟原本一樣。
- ast 多接 MemoryError、RecursionError:`ast.walk` 是迴圈不是遞迴,解析成功之後不會再丟。
- `_NotelinesNet`:
  - 第二層(keep_other=False)的 net 是 None,流程跟原本完全一樣。
  - 第一層只在「開頭欄位其他欄的行文字對上逐提交新增文字」時才呼叫 net(),而原本的判斷也是只在這種行才看 net,所以結果一樣,diff 參數也沒變。
  - git 失敗時,只要用到過就整次回 None,呼叫端照 git 失敗處理;沒用到就不回 None,這是這次刻意改的。
  - `_notelines_range_cand` 和 `_notelines_rows` 各只有一個呼叫點。
- 考試重放第③項改用改之前的圖譜(tenv0):跟 lumos set 一致,set 印連帶待辦時用的是改之前載入的圖譜。多份計劃一起重放時,每份計劃在 tenv0 裡都是自己的舊狀態,跟依序 set 的結果一樣;回傳的是路徑集合,取聯集,「另有條件」的說明不影響。
- `--budget` 擋 inf 和 nan、表態指令一種一行、`_probe_bad_path` 擋「.」、路徑提示的副檔名要字母開頭:照描述生效,沒發現做錯的輸入。

最嚴重等級 major,要擋的 1 條(F1),另有 2 條 minor。
