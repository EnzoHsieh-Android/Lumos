severity: major

# 代碼審 r3 資安-opus(回頭重讀守檔筆記:試著繞過第 2 輪的修法)

實驗都在 `hcc-r3-work-資安-opus/repo` 裡跑。這個目錄是對 negguard 做的 `git clone --shared`,HEAD 是 80a8bb90。腳本 `exp1.py`–`exp6.py` 直接載入 clone 裡的 `scripts/test_lumos.py`,借它的 `_nh_repo`、`_rr_repo`、`_rr_index_add`、`_stats_fixture` 造小專案,用 `/opt/homebrew/bin/python3` 跑。本機 git 版本是 2.39.2。

## F1 檔名結尾是 CR 的 #! 腳本,首行會讀成同目錄另一支檔的首行,留痕照樣判有效(第 2 輪 a1 的修法被繞過)
severity: major
blocking: 是
引句:「blobs = _nodehome_cat_blobs(repo_root, [f"{sha}:{f}" for f in ask for sha in (marker_sha, rec_sha)],」
file: `scripts/lumos:37992`(`_codeloop_bookkeeping_code` 用「版本:路徑」批次讀首行)
file: `scripts/lumos:24062`(`_nodehome_cat_blobs` 只在路徑有 `\n` 時整批當判不了,沒管 `\r`)

1. 為什麼會出錯:`_nodehome_cat_blobs` 把每一項接成 `sha:路徑\n` 餵給 `git cat-file --batch`。git 讀每一行時,如果行尾是 `\r\n`,會把 `\r` 一起去掉。所以查 `sha:governance/replay/run\r` 時,git 實際查的是 `sha:governance/replay/run`。那個版本裡如果真有一支不帶 CR 的 `run`,拿回來的就是它的內容;這是別支檔,而且不會報錯。
2. 先直接證明 git 會這樣做:在一個 repo 裡同時提交 `run`(內容 `2026`)和 `run\r`(內容 `#!/bin/sh`),再查 `run\r`:
   ```
   $ printf 'HEAD:run\r\n' | git cat-file --batch
   485052d512a02b83e9342bcf73dededa325ab881 blob 5
   2026
   ```
   ls-tree 列得出這兩個是不同的 blob,但查 `run\r` 回的是 `run` 的內容。
3. 攻擊做法:代碼審留痕記下之後,另開一個提交,在簿記資料夾放兩支檔:
   - 誘餌 `governance/replay/run`,內容是一行戳記 `2026-10-01`;
   - 真腳本 `governance/replay/run\r`,內容是 `#!/bin/sh\necho pwn\n`,權限 755。
   
   `_nodehome_code_kind("…/run\r")` 回 `shebang?`,接著去讀首行,讀到的卻是誘餌的 `2026-10-01`,於是判成不是程式、整批算簿記,留痕照樣有效(exp1.py):
   ```
   control: #! script (no decoy)            valid=False files=b'governance/replay/run\x00'
   CR-suffix script only                    valid=False files=b'governance/replay/run\r\x00'
   CR-suffix script + decoy stamp 'run'     valid=True  files=b'governance/replay/run\x00governance/replay/run\r\x00'  why=祖先 37c2cce1+簿記豁免(其後 2 檔皆簿記)
   ```
   第二列是對照組:只放 CR 那支、沒有誘餌時兩邊都讀不到,會照設計保守判成程式。只要加上誘餌,結果就翻成放行。
4. 這一條是修法本身的錯,不是「判準不夠寬」:註解與測試③④寫的保證是「首行讀目標提交裡**那一版**」,這個情境讀到的是另一支檔。每支檔有家的 `_is_code_file` 從磁碟開 `run\r`,讀得正確,所以這裡也跟「同一套判法」的說法對不上。後果跟第 2 輪 a1(major)完全一樣:簿記資料夾裡多了一支 #! 腳本,代碼審留痕卻還算有效、推送不擋。要真的被利用,得有人去執行 `run$'\r'` 這支檔;這個前提跟 a1 當時相同。
5. 修法:在 `_nodehome_cat_blobs` 裡,路徑以 `\r` 結尾的也整批當判不了(跟 `\n` 同一句,例如 `any("\n" in s_ or s_.endswith("\r") for s_ in specs)`),這樣就會走「讀不到 → 保守當程式」。另一種做法是先用 ls-tree 拿 blob 編號,再用編號讀。這支函式大約有 15 個呼叫端用「版本:路徑」的寫法(例如 24006 行的合併新行判定、24869 行的 hook 讀取),都是同一族問題,可以一起修;這裡只要求這一輪新加的這個消費者。

## F2 簿記資料夾裡「看起來不像 #!」但一樣能跑的腳本仍然算簿記(BOM、前置空白、#! 在第二行、有執行位元但沒有 #!)
severity: minor
blocking: 否
引句:「副檔名在清單裡=是;沒副檔名看首行是不是 #!」
file: `scripts/lumos:6528`(`_head_is_shebang` 只看位元組開頭是不是 `#!`)

1. 實測(exp1.py),以下四種都判留痕有效:
   ```
   BOM #!                  valid=True   (\xef\xbb\xbf#!/bin/sh)
   leading space #!        valid=True   ( #!/bin/sh)
   #! on line 2            valid=True
   no #!, +x shell body    valid=True   (mode 755、內容 echo pwn)
   CRLF #!                 valid=False  (#!/bin/sh\r\n 照樣抓到)
   ```
2. 這幾種都真的跑得起來:bash 執行一支沒有可用 #! 的可執行檔時,execve 會回 ENOEXEC,bash 就改用 sh 直接跑它的內容。實測 `bash -c ./nx` 印出 `pwn-noshebang`;`bash -c ./bom` 先報 `line 1: #!/bin/sh: No such file or directory`,接著印出 `pwn-bom`。
3. 放行的理由:這是計劃刻意選的判準(跟每支檔有家共用 `_head_is_shebang`),每支檔有家對這幾種也一樣不要求有家。另外,repo 裡沒有東西會執行簿記資料夾裡的檔;要讓它被執行,就得改簿記資料夾外的檔,而那樣留痕本來就會失效。如果要收緊,最便宜的訊號是 git 記的檔案權限:改用 `git diff --raw` 取 mode,簿記資料夾裡 mode 是 100755 的一律當程式檔。這不會動到每支檔有家的判準。

## F3 `lumos gov` 只跳過「不是物件」的行;欄位型別不對的物件行照樣讓它當掉,而這本帳可以直接提交
severity: minor
blocking: 否
引句:「if not isinstance(d, dict):」
file: `scripts/lumos:7273`(mapper 外層只接 ValueError、KeyError)
file: `scripts/lumos:7281`(`[stem(x) for x in d.get("nodes", [])]`:nodes 是 null 時,對 None 迭代會丟 TypeError)
file: `scripts/lumos:21538`(`docs/.governance-log.jsonl` 在簿記白名單裡,提交它不會讓留痕失效)

1. 實測(exp2.py,用 `_stats_fixture` 造一本帳,裡面一行正常事件加一行下面列的內容):
   ```
   fragment-dict  rc=0 traceback=False        ({", ":1})
   {}             rc=0 traceback=False
   nodes null     rc=1 traceback=True TypeError: 'NoneType' object is not iterable
   ts int         rc=1 traceback=True TypeError: 'int' object is not subscriptable
   note int       rc=1 traceback=True TypeError: can only concatenate str (not "int") to str
   ```
2. 就第 2 輪想擋的那個攻擊來說,這次修法是完整的。我另外驗證過 U+2028 切出來的碎片能不能拼成物件:引號在 JSON 字串裡一定寫成 `\"`,所以碎片頂多拼出 `{", ":1}` 這種鍵名固定是 `", "` 的物件,拼不出 ts、nodes、note 這些鍵,mapper 只會拿到預設值,不會當掉(上面第一列)。
3. 放行的理由:要做出第 1 點那幾行,得有人直接手寫帳本再提交。這是第 1 輪就已經存在的問題,不是這次修法新開的;gov 是唯讀報表,也不在推送路徑上。要修的話,load 的 mapper 外層多接 TypeError、AttributeError 就夠了。

## 查過、沒有洞的部分(不算 finding)
- **共用路徑守衛 `_repo_path_unsafe`**(exp5.py):測了四種情況。①在大小寫不分的 APFS 上提交 `.LUMOS`、`GOVERNANCE` 符號連結,結果是 lstat 把大小寫不同的名字當成同一層,判 symlink 擋下;②`governance/Reread-Verdicts` 是連結,擋下;③相對路徑帶 `..`,判 outside;④筆記內容審與存量漂移兩邊的訊息都照舊。repo 外的目錄最後是空的。抽成共用函式之後,「建立前、建立後各查一次」與硬連結數檢查都還在,沒看到新開的洞。
- **gitlink 與符號連結放在簿記資料夾**(exp6.py):gitlink 沒有副檔名時,cat-file 讀不到內容,現在保守判程式、留痕失效(第 2 輪是有效,這次更嚴);gitlink 取名 `sub.md` 判有效,但它不能執行。符號連結指向 `../../src/auth.py` 判有效,可是執行它跑的是那支沒改過的檔,沒有新程式溜進來;連結目標文字剛好是 `#!/bin/sh` 時會判成程式,這個方向是誤擋、不是漏擋。
- **CRLF 的 #!** 照樣抓得到。**大寫副檔名 `.PY`** 在第 2 輪的收貨紀錄已經處置過,這裡不再報。
- **項目檔頭偽造**:要偽造一行檔頭一定得有 `\n`,而 `\n` 屬於 Cc、已被過濾;全形冒號、同形字的鍵名都對不上 `^(欄位): ` 這個樣式;同一個欄位出現兩次會整份拒收。
- **同形字、全形、組合字元、不斷行空白與其他空白類字元**(exp4.py):`А.md`(西里爾字母)、`Ａ.md`(全形)、`A̶.md`、`A　.md`、`A .md`、`Aᅟ.md`、`A⠀.md` 每篇都有自己的對照指紋,各自被列出、各自要對照,不能用來把真的 `A.md` 算成已對照。它們的效果只停在終端上「看起來像同一篇」。帳本每一行照 `splitlines()` 切開後都還是物件,`lumos gov` 回 0。
- **NFC 與 NFD 撞名**(exp3.py):同時提交 `Café.md`(NFC)與 `Café.md`(NFD)兩篇,候選只剩一篇,而項目檔裡放的是 NFD 那篇(誘餌)的內容。這來自第 1 輪就有的「以 NFC 為鍵」設計,不是這次修法造成的;能提交的人本來就可以直接提交一個假的對照紀錄檔名(第 2 輪已經列為信任提交者的設計),撞名沒有給攻擊者更多能力;而且在 macOS 上這兩篇也沒辦法同時 checkout。所以不列。
- **`_note_reread_uncommitted`**(這一輪新加):目錄是符號連結時會跟著連結去列檔名,但它只讀檔名、只拿來決定 prepare 要不要略過;check 照舊只認已提交的紀錄,沒有寫檔或刪檔的路徑。

最高等級:major
