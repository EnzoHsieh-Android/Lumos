severity: major

先說實驗環境:臨時 repo 放在 scratchpad 的 `rfp-r2-邊界/`,實驗完我還沒刪(收尾時要刪)。第二輪新寫的內容裡有 2 個會讓守衛失效的洞,另有 3 個實作時要猜的缺口。

severity: major
blocking: 是 — 照字面做,每一支文字檔的逐檔 diff 都是空輸出,指紋退化成常數,守衛靜默失效
引句:「單獨跑一次 diff(路徑用 git 原樣路徑、加 `:(literal)` 前綴)」
問題:同一份計劃的「選項只有一組」要求全域放 `--literal-pathspecs`,這一條又要求路徑加 `:(literal)` 前綴。兩者併用時,git 把整串 `:(literal)a.py` 當字面檔名,比對不到任何檔。
具體失敗情境:
- 我在臨時 repo 跑 `git --literal-pathspecs diff --no-renames <B> <T> -- ':(literal)a.py'`,輸出是空的,rc=0,沒有報錯。
- 實作者只要兩條都照做,`_patch_file_changes('')` 回 `{}`。這時要嘛每支檔都變成「無輸出」,指紋是跟內容無關的常數(正是第 2 點要防的洞);要嘛實作者得再猜怎麼處理。
- 單獨用其中一個都正確:只有全域旗標時 `-- '[a]*.py'` 能命中,只有前綴時 `:(literal)[a]*.py` 也能命中。
- 計劃必須二選一。另外路徑可能以 `-` 開頭,也沒寫要加 `--` 分隔。
- S5、S10 都不會抓到這個洞,因為它們不比對 diff 是否為空。要加一條「單支檔 diff 不得為空」的驗收條款,或明寫哪一個旗標取代哪一個。
程式佐證:`_note_reread_scan` 用全域旗標的寫法是 ``file: `scripts/lumos:36095` ``。

severity: major
blocking: 是 — 作者在行內分頁符之後改了內容,指紋不變,卻被當成已對照
引句:「輸出交給既有的逐檔改動指紋函式 `_patch_file_changes`」
問題:計劃說重用這支函式就等於繼承它的正確性。但它用 `text.splitlines()` 切行,而 Python 的 `splitlines` 除了 `\n` 之外還會在 `\x0c`、`\x1c-\x1e`、U+0085、U+2028、U+2029 切行。切出來的後半段沒有 `+`、`-`、空白這類前綴,會被 hunk 內的分支(`if ln[:1] in ("+","-"," ","\\")`)直接丟掉。計劃的「位元組原樣」條款用 `surrogateescape`,只管編碼,管不到這個。
具體失敗情境:
- 實測:同一支 `a.py`,新增一行 `y="a<FF>b"` 與 `y="a<FF>ZZZ"`(FF 是分頁符 `\x0c`),`_patch_file_changes` 兩次都回同一個 sha256(`32c1c17d…`)。
- Python 原始碼裡有 `\x0c`(Emacs 與舊式原始碼常用的分頁符),或字串內含 U+2028,都能觸發。
- 結果:作者改掉分頁符之後的邏輯,指紋不變,舊的對照紀錄繼續算數,「該重讀卻被當成已對照」。
- 這正是 RETIRE-IF 要抓的失敗類型。
- 資安席用同一支函式,所以以前就有這個洞。現在把它搬到「放寬就是漏判」的用途上,後果變重。
- 修法是給 `_patch_file_changes` 一個參數改用 `split("\n")`,或在重用前先處理。計劃第 1 點已經要給它加「不算函式名標頭」的參數,可以一併處理,並加一條驗收條款(例如 S16:`\x0c` 之後內容不同,指紋不同)。
程式佐證:``file: `scripts/lumos:25905` ``(`for ln in text.splitlines():`)。

severity: minor
blocking: 否 — 只會造成多列或換機器後算出不同指紋,不會漏判
引句:「得到這條分支改過的每支檔(git 原樣路徑的位元組、兩邊的物件編號與 mode、狀態)」
問題:`--raw` 預設輸出縮寫的物件編號。實測只有 7 個字元(`587be6b`),長度還受 `core.abbrev` 影響。
具體失敗情境:
- 二進位檔那條路徑記的是「改後那一邊的物件編號」。若直接取 `--raw` 的欄位,縮寫長度因機器設定而不同,兩台機器對同一份改動算出不同指紋。
- 縮寫還有極小的碰撞可能。
- 計劃要明寫 `--raw --no-abbrev`,或改用 `rev-parse` 取完整編號。
- 另外,`_patch_file_changes` 本身處理 Binary 時取的是 diff 內 `index` 行(縮寫),這一點也要順手釘 `--full-index`。

severity: minor
blocking: 否 — 沒寫清楚,實作者得猜,但猜錯多半只是多列
引句:「(`--raw` 的 mode 是 160000,或 `--numstat` 印 `-	-`)」
問題:
- 流程只說了 `--raw` 一次,沒說要多跑一次 `--numstat` 才判得出二進位。而逐檔 diff 的輸出本身就有 `Binary files … differ`,而且 `_patch_file_changes` 已經處理它。兩條路誰為準沒寫。
- 型別變更(檔案變符號連結,`--raw` 狀態為 T)時,逐檔 diff 會印兩段同名的 `diff --git`。該函式以檔名為鍵,後一段蓋掉前一段。結果沒錯,但計劃沒提,也沒有驗收條款。
- 單檔超過 4 MB 就退回 `v1`,但現有的 `_lens_git` 用 `subprocess.run(capture_output=True)`,整份輸出先全部進記憶體才能比大小。「避免一支大檔把記憶體吃滿」這個目的達不到。要嘛改用串流讀取並設上限,要嘛先跑 `--numstat` 看行數。
- 預算條款要求每次 git 逾時取「20 秒與剩餘預算減 3 秒的較小者」,但 `_ns_git` 簽名沒有 `timeout` 參數,只有 `_lens_git` 有。計劃沒說要加參數轉傳,實作者要自己發現。
程式佐證:``file: `scripts/lumos:32100` ``(`_ns_git`)、``file: `scripts/lumos:47386` ``(`_lens_git`)。

severity: minor
blocking: 否 — 夾具缺步驟,會讓第一版測試跑不出預期的先紅
引句:「S1–S3、S5–S11、S13–S15 要另搭「有遠端、遠端 main 在頂端之前、分支在上面」的夾具」
問題:搭法的方向對,現有慣例也可用:`remote add` 加 `update-ref refs/remotes/origin/main`,見 ``file: `scripts/test_lumos.py:37263` ``。但有幾個地方沒寫,實作者要猜:
- S10:macOS 的 git 預設 `core.precomposeunicode=true`,會把 NFD 檔名在 `git add` 時改成 NFC,APFS 本身也不區分。要造出「樹裡存的是 NFD」的夾具,得用 `-c core.precomposeunicode=false` 加底層指令(`hash-object`、`update-index --cacheinfo`、`mktree`),計劃沒提。在 Linux 的 CI 上行為又不同。
- S2:要在夾具裡「rebase 時解衝突改到作者那段」,真的跑 rebase 衝突很脆弱。建議直接用 `commit-tree` 手造兩個提交。
- S9:要在夾具提交 `.gitattributes`(`*.dat -diff`)才能造出被設成 `-diff` 的檔。
- S14:要能注入假的時鐘或截止時間,才能模擬「剩餘預算不到 3 秒」。現有 `deadline` 參數可用,但計劃沒指明。
- S3「從不同工作樹跑」要用 `git worktree add`。工作樹與 `.git/refs` 共用,夾具的 `g()` 輔助函式要能指定 `-C`。

已讀,無 finding 的節:
- 〈做法〉第 2 點(全部「未改」退回 `v1`)。
- 〈做法〉第 3 點(`_codeloop_default_base(repo_root, tip="HEAD")` 的簽名與行為)。
- 〈做法〉第 4 點(新舊兩種指紋都認)。
- 〈做法〉第 5 點的退回清單與預算邏輯(實作面見上面第四條 finding)。
- 〈做法〉第 6、7、8 點。
- 〈要一起改的說法〉。
- 〈實務隱患〉、〈回退〉。

另外,「全域選項放在 `diff` 之前」這點我實測確認正確:`git diff -c core.quotePath=false` 會回 `fatal: ambiguous argument`。`--raw -z --no-renames` 的輸出格式是 `:mode mode oid oid 狀態\0路徑\0`,與計劃描述一致。

最高等級 major,共 2 條 blocking(分別是 `--literal-pathspecs` 與 `:(literal)` 衝突、`splitlines` 吃掉分頁符之後的內容)。
