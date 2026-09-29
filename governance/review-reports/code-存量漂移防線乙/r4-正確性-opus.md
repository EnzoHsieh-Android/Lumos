severity: major

# r4 正確性鏡頭(opus)

範圍:6400f52d..5ea8659c 的修正差異(凍結 diff r4-snapshot.patch)。實驗全在自己 mktemp 的目錄 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/r4c.rGS8 裡跑,git 一律 -C 到那裡的臨時 repo;系統 python 是 /usr/bin/python3 = 3.9.6。

## F1 太深判定只量「最長邏輯行」,elif 長鏈這種跨行的深巢狀照樣讓 3.9 的 ast.parse SIGSEGV,drift check 整支崩潰

severity: major
blocking: 是 — 這段修正宣稱要擋掉的程序崩潰,換一個形狀就原樣重現,而且是端到端的 check 指令直接被訊號殺掉

引句:「run = 0 if t.type == _tok.NEWLINE else run + 1」

1. 計數器每遇到 NEWLINE 就歸零,所以只看得到「單一邏輯行」的長度。但 `if a:pass` 後面接一長串 `elif a:pass`,每個 elif 是自己的一個邏輯行(每行 4、5 個詞),在語法樹裡卻是一層套一層的 If 節點——3.9 的解析器與 ast 轉 Python 物件都是遞迴,深度跟著 elif 數長。
2. 實測(系統 python 3.9.6,直接呼叫 _drift_py_names):`'"""def example_only(): pass"""\nif a:pass\n' + 'elif a:pass\n' * N`
   - N=110000(1.32MB)、130000(1.56MB):`_drift_py_too_deep` 回 False、解析成功;
   - N=160000(1.92MB):`_drift_py_too_deep` 回 False,接著 `ast.parse` → 程序 rc=139(Segmentation fault)。
3. 端到端重現(翻紅指令,腳本在上面臨時目錄的 e2e.py):用測試的 `_dr_repo(cfg={"drift_check": {"gate": "block"}})` 建專案,加 `src/gen.py`(上面 N=160000 的內容)與一行 `REVISIT:[when-symbol:example_only][by:2099-12-31] 等範例變真的`,提交後跑
   `/usr/bin/python3 scripts/lumos drift check --diff <起點>..HEAD --repo <臨時 repo>`
   輸出:`check rc -11`(被 SIGSEGV 殺掉,沒有任何判定或治理帳)。直接呼叫 `_drift_probe_tree(repo, sha).one('symbol','example_only')` 同樣 rc=139。
4. 觸發條件:3.12 以前、該 Python 檔含條件的名稱(`_defines` 先用正則預篩,名稱要出現在檔裡才會走到 ast)、檔裡有約 14 萬層以上的 elif 鏈(產生器生出的分派表/狀態機屬這類)。單行長運算式那一型在 15 萬字元以下我逐一試過(`**` 鏈、呼叫鏈 `f()()()`、屬性鏈、下標鏈、not 鏈、三元鏈、lambda 鏈、加法、比較)都不崩,所以「不到 15 萬字元不量」那條門檻本身沒問題;漏的是「深度不等於單行長度」這個形狀。
5. 對照:CI 用 3.12 以上不受影響,所以同一次推送在本機推送前檢查崩潰、在 CI 正常,兩邊結果不一致。
file: `scripts/lumos:25905`
file: `scripts/lumos:25867`

## F2 2 萬詞門檻會把「平的大資料字面值」誤判成太深:3.9 退回正則,docstring 範例又被當定義、只用 CR 換行的檔則一個定義都找不到

severity: minor
blocking: 否 — 只影響 3.9 上 15 萬字元以上、含一行 2 萬詞以上字面值的檔,結果偏差但不崩

引句:「_DRIFT_PY_MAX_LINE_TOKENS = 20000」

1. 一個 5200 筆的 dict 字面值(`"name_00000": "\U0001f000",` 一行 4 個詞加換行)就是一個 2 萬多詞的邏輯行;這種產生出來的資料表(emoji 對照、Unicode 表)在一般專案常見,3.9 的 ast.parse 解析它毫無問題(平的,不深)。實際會崩的單行要約 21.6 萬個負號、13 萬詞的 lambda 鏈,2 萬離崩潰線差一個數量級。
2. 重現(腳本 t1 同目錄 data.py,166455 字元,開頭 docstring 裡有一行 `def example_only():`,後面是 5200 筆的 EMOJI dict):
   - 3.9.6:`too_deep True names True regex-hit True` → `_drift_py_names` 回 None、退回 `_drift_py_def_re`,docstring 裡的範例被當成定義,`[when-symbol:example_only]` 判成立;
   - 3.14.6:`too_deep False names False` → ast 判,不成立。
   同一個條件在本機推送前(3.9)與 CI(3.12+)判出相反結果;r1 用 ast 修掉的「文件範例被當定義」在這類檔上回來了。
3. 第二種輸入:只用 `\r` 換行(舊 Mac 換行)的 Python 檔。`io.StringIO(txt).readline` 只認 `\n`,整支檔變成一個「行」,8000 個函式、229780 字元就超過 2 萬詞 → 判太深 → 退回正則;而正則用 `re.M` 的 `^`,在只有 `\r` 的文字裡只對得到檔首,結果 `f5` 這種真的定義判成不存在(實測 `ast.parse` 在 3.9 解析成功、`regex f5 False`)。
file: `scripts/lumos:26072`

## F3 SHA-256 的 repo 讀檔退回「版本:路徑」,拿掉 NFD 重讀後,NFD 檔名的程式檔與筆記變成每次都判不了(r2 的版本讀得到)

severity: minor
blocking: 否 — 只在 SHA-256 物件格式的 repo 出現,這種 repo 很少(GitHub 目前不收)

引句:「return _nodehome_cat_blobs(root, [oids.get(p) or f"{where}:{p}" for p in paths], timeout=timeout)」

1. `_drift_list` 只快取 40 位的提交編號(`re.fullmatch(r"[0-9a-f]{40}", where)`),但 `_lens_full_sha` 的 `_LENS_SHA_RE` 也收 64 位。SHA-256 repo 的起點/終點是 64 位 → `_drift_list` 不進快取、`_DRIFT_OID_CACHE` 沒有 → `_drift_oids` 回 {} → `_drift_cat` 全部退回 `<提交>:<NFC 路徑>`。這份差異同時拿掉了 r2 的 NFD 重讀,所以 git 裡存 NFD 的路徑在這種 repo 一律讀不到。
2. 重現:`git init --object-format=sha256`,用 `git -c core.precomposeunicode=false update-index --add --cacheinfo 100644,<blob>,<NFD 的 src/café.py>` 放一支 `def cafe_fn()` 再提交,對 HEAD 建 `_drift_probe_tree`:
   - 這份差異(5ea8659c):`noPath None withPath None bad ['src/café.py']` → 不帶路徑與帶路徑的條件都判不了,block 模式每次推送擋;
   - 上一版(6400f52d 的 scripts/lumos):`noPath True withPath True`。
   同一條路也用在 `_drift_tree_env` 讀筆記,NFD 檔名的筆記一樣變成讀不出的筆記。
3. 附帶:where 不在快取時,`_drift_oids` 每次都呼叫 `_drift_list` → `_nodehome_list` 重新 ls-tree 一次,結果還丟掉;SHA-256 repo 每次 `_drift_cat` 多一次整棵樹的列檔。
file: `scripts/lumos:25942`
file: `scripts/lumos:25980`

## F4 判不了的說明點名的是「整棵樹讀過而讀不出的檔」,不是這一行碰到的檔:status 條件判不了的行會點名一支無關的程式檔

severity: minor
blocking: 否 — 只影響訊息,判定(判不了→要處理)本身對

引句:「_drift_bad_note(trees.get(tip), trees.get(base))」

1. `bad_paths()` 回的是該樹 `_text` 裡所有讀出 None 的檔(prefetch 與語料讀過的全部),`_drift_bad_note` 每一行判不了都拿同一份清單接在後面,跟那一行的條件無關;status 條件判不了(指到的筆記不是 UTF-8)時,那篇筆記反而不會被點名。
2. 重現(腳本在臨時目錄 misattr.py,3.14 程序內跑):同一篇 Pay 寫兩行——第 16 行 `REVISIT:[when-symbol:src/b.py::xfn][by:2099-12-31] 甲`、第 18 行 `REVISIT:[when-status:Projects/壞=done][by:2099-12-31] 乙`;`Projects/壞.md` 內容是非 UTF-8,`src/b.py` 的內容編號讀取換成回 None。`cmd_drift_check` 輸出:
   `判不了:Systems/Pay.md:18 的條件判不了(git 讀不出程式檔或筆記:src/b.py)`
   第 18 行只有 status 條件,從沒碰 src/b.py,真正的原因 Projects/壞.md 沒被點名。scan 的 `_drift_bad_note(tree)` 同一種形狀。
file: `scripts/lumos:26217`
file: `scripts/lumos:26046`

## 已看,無 finding

- 用內容編號讀:`_nodehome_list` 的欄位位置——索引模式 `ls-files -s` 是「模式 編號 階段」取 parts[1]、提交樹 `ls-tree` 是「模式 種類 編號」取 parts[2],都對;衝突階段在前面就被濾掉。目前只有 `_drift_list` 傳 oids、只對 40 位提交編號傳,索引模式沒有呼叫端。
- `_DRIFT_OID_CACHE` 與 `_DRIFT_LS_CACHE`:滿 8 筆兩個一起清、再補回目前這筆,`_drift_oids` 先呼叫 `_drift_list`(被逐出時會重列並重填)再取編號,兩個 dict 對得上;repo 裡沒有別處(含測試)直接寫這兩個快取。
- disk 模式讀檔沒走 `_drift_cat`,這份差異沒動它的行為。
- `_drift_py_too_deep` 對 scripts/lumos 本身(1688485 字元,3.9 回 False,0.57 秒)與 scripts/test_lumos.py(2802073 字元,回 False)都不誤判;tab 縮排、反斜線續行、CRLF、form feed 混著的 26–29 萬字元合法檔,3.9 也回 False。
- `_DriftNames` 查集合 vs 原本的 `(?<![\w])name(?![\w])`:名稱整串符合 `\w+` 時,兩者都等於「文字裡有一段最長的 \w 連續串恰好等於名稱」;兩邊都是 Unicode 的 \w、都分大小寫,含數字、數字開頭、CJK 名稱結果一樣;不是整串 \w 的名稱(含 `.`、`$`、組合附加符號、`·`)照舊對原文跑正則。等價。
- 「任一確定受影響就是候選」:任一條 True 就評估整行,判不了的條件在評估時照樣回判不了,不會因此漏成不擋;全是 False 或 None 的行為跟原本一樣。
- `_drift_with_layout`:起點是空樹(`base` 為空)時不看版面,但那時起點沒有「同一條」,每一行本來就是候選;讀不到樹當成版面有變,只會多評估、最後落到判不了,方向是保守的。版面(`_nodehome_layout`)是檔屬於測試或程式的唯一非路徑依據,補上後形狀改變的覆蓋是完整的。
- bad 旗標:check(`not x[3]["bad"]`)、scan(`pr["bad"]`)不評估;scan 的問題清單、第一層(`_ns_revisit_violations`)、doctor Z 段計數都看 `errs`,而 `bad` 為真時 `errs` 一定有東西;只有期限寫錯時 `bad` 為假、`errs` 有東西,四處一致是「列成寫錯、照評估」。exam 手寫的 dict 補了 `"bad": True`,沒有別處自己拼解析結果。
- 反斜線先轉斜線再驗:只對 file/symbol/test,status 值不動;名稱那段裡的反斜線轉了也不影響 `_probe_named_err`(它只驗路徑那段)。

總結:最高 major,需要擋下的 1 條(F1),另有 3 條 minor。
