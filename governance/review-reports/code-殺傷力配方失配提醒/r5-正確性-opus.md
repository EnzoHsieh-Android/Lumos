severity: major

# 代碼審第 5 輪 正確性席(正確性-opus)

審材:r5-delta.patch(0f1e68ea..7a510e53)。實驗都在 `git clone --shared` 出來的副本裡跑(副本與實驗腳本在 `kcc-r5-work-正確性-opus/`),對照方式跟 `t_kill_recipe_check_matches_guard_kill` 一樣:每一格自己一個 repo,同一條配方讓判斷函式判一次、真跑 `lumos guard kill --json` 一次,再用測試裡的 `_krc_match` 對照。`-k kill_recipe_check` 兩支照綠(80 passed)。

先講結論:**「正式路徑」這條規定本身站得住**。底下這些寫法我都造了、真跑兩邊對照,全部對得上,還原也都還原到同一支檔:檔名含萬用字元(`x?.py`、`x[ab].py` 而且旁邊有 `xa.py`、`x*.py`)、反斜線 `a\b.py`(有和沒有 `ab.py` 兩種)、`-` 開頭、`!` 開頭、中間有冒號、結尾空白、空白加引號、執行檔模式 100755、深層子資料夾、平台根是子資料夾、提交裡只差大小寫的兩支一般檔(配方寫哪一支都試過)。git 還原時會先照字面比對,再當萬用字元比對,所以萬用字元不會讓還原失敗。拿掉模擬之後,程式與測試裡已經沒有任何地方還在呼叫被刪掉的函式。

有問題的是下面四條,只有 F1 是 major。

## F1 正式路徑的檔在工作目錄讀不到時判 missing,kill-add 提醒卻說「guard kill 跑到它會判 drifted」;實跑 guard kill 是 killed、rc 0
severity: major
blocking: 是
引句:「msg = f"{f} 讀不到({res['detail']});guard kill 跑到它會判 drifted。{fix}"」
file: `scripts/lumos:13206`
file: `scripts/lumos:13066`
file: `scripts/lumos:13822`
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:89`

1. 這一輪改動之後,正式路徑一定在 HEAD 裡,而且是一般檔。guard kill 的工作樹是從 HEAD 檢出來的,所以它一定開得到這支檔。判斷函式卻是去工作目錄讀這支檔(`_kill_read_text(str(Path(top) / file))`)。因此只要判出 `missing`,原因一定是工作目錄跟 HEAD 不一樣:檔案被刪了、被改成資料夾、還沒提交的 `git mv`,或是工作目錄的絕對路徑太長。這些情況 guard kill 都照樣套得上壞法。也就是說,這一輪之後 kill-add 只要印出「guard kill 跑到它會判 drifted」,這句話幾乎每次都是錯的。改動前 `missing` 涵蓋「不在提交裡」,那時這句話是對的;這一輪把那部分搬到 `path`,這句提醒卻沒跟著改。
2. 同一輪自己的說明文件也已經不認這條對應了:docstring 改寫成「對應 guard kill:ok=套上壞法而且還原得回去、hits=drifted、undecodable=讀檔出錯…」,裡面沒有 missing。`_krc_match` 也把 `"missing": verdict == "drifted"` 拿掉了。Systems/guard-kill 的對照表同樣沒有 missing 那一列。可是程式還是會判出 missing,提醒也還在預測 drifted,兩邊說法互相矛盾。S5 對照測試裡沒有任何一格會判出 missing,所以拿掉這個狀態或改它的字面,測試都照綠。
3. 計劃〈誠實界線〉承認的是「已追蹤的檔有未提交的改動時,兩邊**讀到的內容**仍可能不同」。它沒有授權提醒去斷言 guard kill 會怎麼判。工作目錄內容被改、判斷函式判 hits 的情況(下面 B、C 兩格),我歸在已承認的範圍裡,不另外報。
4. 重現 1(kill-add 的字面跟真跑對不上;`exp5.py`:`_mk_kill_env()` 建好之後刪掉工作目錄的 prod.py,HEAD 裡還有):
```
$ /opt/homebrew/bin/python3 exp5.py <副本>
kill-add rc 0
stderr: ⚠ 提醒:"prod.py" 讀不到(工作目錄裡沒有這支檔(No such file or directory));guard kill 跑到它會判 drifted。修法:lumos guard kill-rm Systems/Limit --id e78d76f5fc38,照現在的程式改寫後再 kill-add
guard kill rc 0 {"results": [{... "file": "prod.py", ... "verdict": "killed", ...
```
提醒預測 drifted,還附了「kill-rm 移掉」的修法;實際上這條配方在 guard kill 裡是 killed、rc 0,是一條有效的配方。
5. 重現 2(對照格;`exp.py` 與 `exp4.py`,用 `_krc_cell` 加 `after` 改工作目錄):
```
A 工作目錄刪掉(未提交)  判斷=missing '工作目錄裡沒有這支檔(No such file or directory)'  guard kill rc=1 verdict=survived  對得上=False
D 工作目錄換成資料夾    判斷=missing '不是一般檔'                                    guard kill rc=1 verdict=survived  對得上=False
長路徑(repo 頂+file=1060 位元組 > 1024,工作樹前綴較短)
                        判斷=missing '工作目錄裡沒有這支檔(File name too long)'      guard kill rc=1 verdict=survived  對得上=False
```
(survived 的意思是壞法套上了、還原也成功,在 `_krc_match` 裡算作 ok。)
6. 修法建議:正式路徑判 missing 時,提醒不要預測 guard kill 的結果,改寫成「工作目錄裡讀不到(提交裡有這支檔;guard kill 用提交的版本)——先確認是不是還沒提交的刪除或改名」;P2 同一段也帶這句。S5 加一格「正式路徑、工作目錄刪掉 → missing、提醒不寫 drifted」,Systems/guard-kill 的對照表補上 missing 一列。另一種做法是讓正式路徑直接讀 HEAD 的內容(`git cat-file`),這樣就跟 guard kill 讀同一份,但會改變「讀工作目錄」這個設計取捨,要人裁定。

## F2 提交裡有只差大小寫的「資料夾+連結」或「一般檔+連結」時,正式路徑判 ok 或 hits(還讀到 repo 外的檔),guard kill 判 error 逃逸;計劃寫的已知限制把後果講輕了
severity: minor
blocking: 否
引句:「開檔、數原文、還原都照字面走,判得準,其他寫法一律請人改寫、不預測結果。」
file: `scripts/lumos:13822`
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md:169`

1. 計劃〈實作紀錄〉承認的限制是:「提交裡同時有只差大小寫的兩支檔時,guard kill 工作樹裡只會有其中一支;沒處理」。兩支都是一般檔時我實跑過,兩邊對得上(L、L1 兩格)。可是如果其中一支是連結,在大小寫不分的檔案系統上,工作樹裡最後留下的是那個連結。這時 guard kill 的 realpath 會跟著連結走出 repo、被圍欄擋下,判 error。判斷函式在 clone 下來的工作目錄裡,會經過同一個連結讀到 repo 外面的檔、數那裡的原文,前幾輪的圍欄到這裡已經沒有了。所以後果不只是「讀到另一支檔的內容」,而是兩邊判出不同狀態,判斷函式還讀了 repo 外的檔。
2. 重現(`exp2.py`、`exp3.py`,在 macOS 預設的 APFS 上用 git 管線指令造提交):
```
L2 提交裡 A.py=一般檔、a.py=連結→repo 外   判斷=ok                guard kill rc=2 verdict=error detail='file 路徑逃逸 worktree(圍欄擋下)'  對得上=False
資料夾版:提交裡 SRC/x.py=一般檔、src=連結→repo 外,另外 clone 一份
  clone: warning: the following paths have collided ... 'src'
  判斷=hits '原文出現 2 次'(數的是 repo 外 evil/x.py 的內容)    guard kill rc=2 verdict=error detail='file 路徑逃逸 worktree(圍欄擋下)'  對得上=False
```
3. 定成 minor 的理由:這是計劃已經點名的同一個根因,而且得有人刻意造只差大小寫的連結才會發生。不過要補起來很便宜,也不必回頭量檔案系統:在 `_kill_path_issue` 裡建 canon 時,不分模式把每個路徑**和它的每一層上層資料夾**都按 `nfc().casefold()` 收起來。如果正式路徑本身或它任何一層上層資料夾,折疊後同時對到兩個以上不同的寫法,就判 path「提交裡有只差大小寫或寫法的另一個路徑」。這樣在保守的方向把洞補上,同時把〈實作紀錄〉那句限制的後果寫準。

## F3 被判 path 時給的建議有三種會誤導:拆開寫法的檔永遠在兩種寫法之間來回跳;`連結/..` 會被建議成另一支檔;提交裡真實存在、檔名含零寬字元的檔永遠判 path,卻沒說要怎麼辦
severity: minor
blocking: 否
引句:「hits = ctx["canon"][key].get(nfc(posixpath.normpath(file)).casefold(), ())」
file: `scripts/lumos:13139`
file: `scripts/lumos:13154`
file: `scripts/lumos:13134`

1. **來回跳**:如果提交裡存的就是拆開寫法(NFD;在 Linux 或 `core.precomposeunicode=false` 的情況下提交進來的),配方寫 NFD 會得到「寫成 "café.py"」(組合寫法)。照建議改成 NFC 之後,又得到「提交裡沒有這個路徑,是不是 "café.py"」(拆開寫法)。這兩個字串印在終端上一模一樣,使用者照著建議改,永遠改不完。實跑(`exp7.py`):
```
配方寫 NFD → path '...檔名是拆開的 Unicode 寫法,寫成 "caf\xe9.py"'
配方寫 NFC → path '...提交裡沒有這個路徑,是不是 "café.py"'
```
照規定,這種檔本來就不能當配方目標(S5 已經有一格判 path),但提醒應該直接講「這支檔在提交裡是拆開寫法,不能當配方目標(改檔名或換一支檔)」,而不是叫人改寫。
2. **`連結/..` 被建議成另一支檔**:`posixpath.normpath` 是照字面消掉 `..`,不會跟著連結走。提交裡 `lnk` 是指向 `sub/deep` 的連結時,`lnk/../prod.py` 照字面解析其實是 `sub/prod.py`,guard kill 改的也是那支;建議卻寫「是不是 "prod.py"」。實跑(`exp6.py`,原文只在 sub/prod.py 裡出現):
```
判斷: path 不是提交裡的正式路徑:提交裡沒有這個路徑,是不是 "prod.py"
guard kill: 1 survived  whole-suite          ← 壞法套在 sub/prod.py 上
照建議改寫成 prod.py 後判斷: hits 原文出現 0 次
```
在這個例子裡,下一次檢查會把錯抓出來。但如果兩支檔裡原文都剛好出現一次,照建議改寫就會在沒有任何提示的情況下換掉配方要改的檔。修法:路徑裡有任何一段 `..` 時不給建議(或是 `..` 前面那一段在 modes 裡是 120000 時不給)。
3. **檔名含零寬字元的檔永遠判 path**:`_path_special_chars` 連 Cf 類也算進去,所以零寬連接字元(U+200D,emoji 組合裡就有)、零寬不連接字元(U+200C,波斯文常用)、軟連字號這些都會被擋。這種檔在提交裡真實存在,guard kill 跑起來完全正常(`exp.py` 的 O 格:判斷=path「含控制字元或無效字元」,guard kill survived),可是提醒說「含控制字元」不是事實,也沒有任何寫法能讓它轉成正式路徑。這是規格的取捨(S5 寫的是「不含控制字元」),只要求提醒字面講清楚:「檔名含格式字元(如零寬字元),這支檔不能當配方目標」。
4. 順帶一提:Windows 使用者習慣寫的 `src\x.py`,在提交裡有 `src/x.py` 時也不會給建議(實跑:「提交裡沒有這個路徑(沒提交、被忽略…)」)。canon 查詢前把 `\` 換成 `/` 就能點名正確寫法。

## F4 模擬拿掉了,計劃〈做法〉與 Systems/guard-kill 還在用現在式描述舊做法,同一篇裡前後矛盾
severity: minor
blocking: 否
引句:「★規定正式路徑、不模擬★(Enzo 2026-10-01 裁,代碼審第 4 輪後)」
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md:26`
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md:42`
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md:49`
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md:59`
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md:123`
file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:95`

1. 計劃的 PRIOR-ART(第 26 行)還寫「用一支小解析器重演 guard kill 在隔離工作樹裡的路徑解析與圍欄」。〈做法〉第 42 行寫「路徑解析照 guard kill…模擬」,第 49 行寫對照測試的對應是「`outside` ↔ error(逃逸)」,第 60 行寫 kill-add 印 `outside` 的字面;這些都是被拿掉的做法,卻用現在式寫成規格。〈實作紀錄〉第 123–124 行(「解析器走的是 HEAD 裡有什麼」「跟隨連結超過 40 次沒有照寫」)講的是已經刪掉的程式,也沒標註已經撤掉。條款 S1、S3、S5 已經改了,所以同一篇裡規格本文和條款互相打架。下一個接手的人照〈做法〉讀,會以為現在還在模擬。
2. 計劃第 59 行與 Systems/guard-kill 第 95 行都寫「判重之後、**寫入之前**驗」。同一段後半句、以及這一輪改過的 docstring(「kill-add 寫入成功、放掉寫入鎖之後」)寫的都是寫入之後才驗,所以這兩處自己內部就矛盾(第 4 輪 F4 只修了 docstring)。
3. 修法:〈做法〉第 1 節的路徑那幾點換成「規定正式路徑」的說法,或在那一節開頭加一行「本節的路徑解析已在代碼審第 4 輪後撤掉,以〈條款〉與〈實作紀錄〉第 4 輪那段為準」;第 123–124 行標「已撤」;兩處「寫入之前」改成「寫入成功、鎖放掉之後」。

最高等級:major
