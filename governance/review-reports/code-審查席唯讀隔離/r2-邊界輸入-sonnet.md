severity: major

### F1 寫壞標記的判準對常見 markdown 寫法仍靜默放行(整個審查席失去防護)
severity: major
blocking: 是 — 派工第一行明明是 LUMOS-SEAT 標記,卻判成 none 而不是 bad。這一席完全不套白名單,也沒有任何提示,是 fail-open。r1 的 r1e3「標記加 markdown 修飾靜默不認」只補了一部分。
引句:「const SEAT_LOOSE_RE = /^[#>*_`\s]*lumos-seats?\s*[:：]/i」
重現(`node --experimental-strip-types`,直接 import register.ts 的 `parseMarker`):
```
**LUMOS-SEAT**: a/r1/b   -> {"kind":"none"}   // 粗體包住名字,冒號在外面
- LUMOS-SEAT: a/r1/b     -> {"kind":"none"}   // 項目符號(- + 數字.)沒在剝除集合裡
1. LUMOS-SEAT: a/r1/b    -> {"kind":"none"}
[LUMOS-SEAT: a/r1/b]     -> {"kind":"none"}
"LUMOS-SEAT: a/r1/b"     -> {"kind":"none"}
LUMOS-SEAT a/r1/b        -> {"kind":"none"}   // 忘了冒號;r1 之前的 ^lumos-seat 會擋,新判準反而放行
​LUMOS-SEAT: a/r1/b -> {"kind":"none"}   // 零寬空白;JS 的 trim 不剝它
```
對照:`**LUMOS-SEAT:** a/r1/b`、`## `、`> `、反引號包住的寫法都會回 bad,所以只有「冒號在修飾符之外」和「剝除集合以外的前綴」這兩類會漏。
建議:判準改成「去掉非字母數字前綴後,以大寫 `LUMOS-SEAT` 開頭(不管有沒有冒號)」,或剝除集合擴大到 `-+[<"'` 與數字加點。沒冒號的一般提及用大小寫與整詞區分(`LUMOS-SEAT` 後面接空白或冒號,不是 `-seating`)。

### F2 `claude` 當路徑最後一段時,本 repo 的 `mods/claude` 目錄被當成執行檔誤擋
severity: minor
blocking: 否 — 只是誤擋,審查員改寫成相對路徑加結尾斜線就能做同一件事。
引句:「const last = /^(\/|\.\.?\/|~\/)/.test(t) ? t.slice(t.lastIndexOf('/') + 1) : t」
重現(`bashBlock`):
```
ls ./mods/claude                                      -> 擋「claude」
find /Users/…/lumos-toolchain-seat-guard/mods/claude -name "*.ts"  -> 擋
cd /Users/x/repo/mods/claude && ls                    -> 擋
ls ~/harness/x/mods/claude                            -> 擋
ls /Users/x/repo/skills/gh                            -> 擋
ls mods/claude/   或   git -C /Users/x/repo ls-files mods/claude   -> 放行
```
本 repo 的目錄就叫 `mods/claude`。審查員拿絕對路徑去 `find`、`ls`、`cd` 是很常見的下法。絕對路徑與相對路徑的結果不一致,計劃條款 S3 只列了 `cat mods/claude/x.ts` 放行,沒列目錄當參數。擋下提示也沒說「目錄名剛好叫 claude 時,結尾加 `/` 或改用相對路徑」。
建議:最後一段是 claude、gh 等,且該詞是這個 token 的結尾(沒有結尾斜線)時才擋,並在擋下提示補一句目錄的繞法;或把條款補一條目錄參數的案例,明說這是接受的誤擋。

### F3 擋下提示把 `grep -rn push`、`git grep push` 的出路講丟了
severity: minor
blocking: 否 — 純提示品質,不影響擋或放行。
引句:「'檔案內容用 Read 工具讀;要搜的字避開這幾個詞,或把 git 與 push 分成兩條指令;報告內容直接寫在回答裡。')」
重現:`git grep push`、`git log -S push`、`git log --grep push` 都被擋。要找的字就是 push 時,「避開這幾個詞」做不到。而且 `echo push; git status` 同一條指令字串裡分開寫仍然擋。「分成兩條指令」只有拆成兩次 Bash 呼叫才有效,提示沒講清楚。Grep 工具在白名單裡,可以直接搜 push,但提示沒提。
建議:提示補「搜字請用 Grep 工具」與「git 與 push 要分成兩次 Bash 呼叫,不是同一行」。

### 前輪修復驗收
- r1e4 路徑上限:4096 字與 256 段的邊界測過。`/tmp/` 加 255 段(共 256 個非空段)與 4096 字都放行,257 段與 4097 字都擋,邊界正確。macOS 的 PATH_MAX 是 1024,真實路徑到不了上限,不會誤擋。
- r1s2 大小寫:`GH pr`、`GIT PUSH`、`CAT /tmp/LUMOS-SEAT-STAGING` 都擋。制表符、全形空白、`$'gh'`、`\gh`、`$(gh pr)`、反引號包住的 gh 都擋。
- r1e2 切詞:`cat mods/claude/x.ts`、`git log --grep=push`、`python3 test.py -k push`、`node test_push_tool.js`、`cat scripts/hooks/pre-push` 都放行,沒有誤擋。
- 不擋但屬於「不防有心繞」範圍,不算新洞:`'g'h`、`g\h`、`g""h`、`${a}h`、`git pu\sh`、`git -c alias.p=push p`、`--exec=gh`、`X=gh`(等號不切詞)。Unicode 折小寫(土耳其 İ、ﬀ 連字)沒有造成能執行的新寫法。
- r1e5 市集檔:`utf-8-sig` 讀 BOM 正常。無效位元組丟 UnicodeDecodeError,屬於 ValueError,有被接住。`plugins` 不是清單、`name` 不是字串都回空集合。
- 讀檔看不懂的提示:`~`、Windows 路徑、URL、相對路徑都擋,提示「改用乾淨的絕對路徑」合理。空字串與 undefined 會印成 `()` 或 `undefined`,可讀。
- r1e3 標記:`LUMOS-SEAT：`(全形冒號)、`lumos-seat:`(小寫)、`LUMOS-SEATS:` 擋下派工,`請依 lumos-seat: 規則`、`lumos-seat-guard: x` 照常。F1 是這項修法留下的缺口。
- 圖譜鏡頭:牽連清單裡沒有跟輸入處理相關、需要另外回報的項目。

總結:最嚴重 major,blocking 1 條
