severity: major

# 邊界可執行席報告:回頭重讀指紋不因主線前進失效_計劃

我用 Apple Git 2.39.2 在臨時倉庫做了實驗。實驗倉庫已刪,下面各條的輸出都是當時實跑所得。

## 〈做法〉1:每支檔的改動指紋

severity: minor
blocking: 否 — 照字面做第一次跑 S1 就會紅,抓得到;但抓到之前會是靜默退回 v1
引句:「再加 `--literal-pathspecs --no-renames --diff-algorithm=myers --inter-hunk-context=0 -U3`」
問題:`--literal-pathspecs` 是 git 的全域選項,要放在 `diff` 前面,不是 diff 的選項。現有程式也是這樣放的:`file: `scripts/lumos:36216`` 是 `_ns_git(root, "--literal-pathspecs", "diff", …)`。材料寫成「跑 `git diff …` 再加 `--literal-pathspecs`」,沒說放哪。
失敗情境:實作者把它塞進 diff 參數串,git 回 usage(實測 `git diff --literal-pathspecs HEAD HEAD` 印出 usage)。`_ns_git` 對非零回傳碼回 None(`scripts/lumos:32100`),這正好符合〈做法〉3 的「git 失敗退回 v1」。結果所有指紋靜默退回 v1,功能整個不生效,只有 S1 會紅。
建議:材料寫明全域選項放 `diff` 前,並加一條「diff 呼叫失敗時退回 v1 要留一筆可查的事件」。

severity: major
blocking: 是 — 材料說的主線前進後指紋不變,在最常見的情形不成立
引句:「把 `@@ -a,b +c,d @@` 的數字換成固定字樣,其餘每一行(含空白、含上下文行、含檔頭的路徑)原樣雜湊」
問題:`@@ … @@` 後面還有一段 git 附的「所在函式標題」,例如 `@@ -31,7 +31,7 @@ def foo(a):`。材料只換數字,「其餘原樣」就把這段標題算進雜湊。標題取自 hunk 之前最近一行頂格的字母開頭行,不受 -U3 限制。
失敗情境:實測。分支改 `a.py` 第 31 行附近,主線把封閉函式簽名改成 `def foo(a, b=1):`,離分支的 hunk 還有 27 行。rebase 後 hunk 的數字和三行上下文都一樣,標題卻從 `def foo(a):` 變成 `def foo(a, b=1):`,指紋改變。`scripts/lumos` 約五萬行,多數 hunk 在長函式內,主線改了該函式簽名就失效,正好打在緣起要解的情形。S1 的測試夾具若不動封閉函式標題,測試會綠、實務會漏。
建議:正規化時把 `@@ … @@` 整行(含後面的標題)換成固定字樣。再加一條驗收:主線只改封閉 `def` 行,指紋不變。

severity: major
blocking: 是 — 該重讀的會被當成已對照
引句:「每檔去掉 `index` 行」
問題:二進位檔的 diff 去掉 `index` 行後只剩 `Binary files a/x and b/x differ`,內容完全沒進雜湊。判成二進位的不只副檔名是圖檔的:含 NUL 的檔(例如 UTF-16)、`.gitattributes` 設 `-diff` 的檔也算。`_about_code_path` 只擋非檔案(`scripts/lumos:21082`),不擋二進位。
失敗情境:實測。同一支 `bin.dat`,分支先改成 `00 01 02` 再改成 `09 09 09`,去掉 `index` 行後兩份文字完全相同。about_code 列了這支檔的筆記,第一次記過對照紀錄,日後這支檔換成別的內容,筆記仍被當成已對照。
建議:diff 加 `--binary`(含 base85 內容,仍可去掉 `index` 行),或二進位檔改把兩邊 blob 編號放進指紋。

severity: major
blocking: 是 — 全「未改」的指紋是一個跟程式版本無關的常數
引句:「主線怎麼改它都不影響指紋」
問題:候選用審查範圍起點算(`_note_reread_scan`,含 `homes_b` 起點那邊的家,以及整段範圍裡碰過的筆記)。指紋改用分岔點算。兩個範圍不同,於是會有「是候選,但 about_code 每一項在分岔點..頂端都是『未改』」的筆記:
- 這次把某檔從 about_code 移出,且該檔有改。
- 分支自己先改又改回(淨改動為空)。
- 手動 `--diff` 給很寬的範圍,範圍內有合進來的主線改動。

這種筆記的指紋 = 雜湊(筆記路徑、各項皆未改、v2),是一個永遠不變的常數。紀錄是跟著 repo 提交的(`governance/reread-verdicts/`),所以一旦記過一次,之後任何一條分支遇到同樣形狀,都被當成已對照。判定者當時讀的是範圍起點的 diff,不是分岔點的。v1 的 blob 指紋至少跟程式版本綁著,v2 的常數沒有。
建議:每一項都是「未改」(含空 diff)時,整篇退回 v1。這跟 S6(只有部分未改)不衝突,再加一條驗收。

severity: major
blocking: 是 — 材料沒說怎麼從 about_code 的鍵找到 git 路徑,照現有程式的做法會讓路徑不符時變成「未改」
引句:「跑一次 `git diff <分岔點> <頂端> -- <那幾支檔>`」
問題:`_nodehome_key` 回 NFC。`_nodehome_list` 填的 `oids` 也是 NFC 鍵,git 原樣路徑已丟掉(`scripts/lumos:30724`)。現有的 diff 路徑靠 `scan["changed"][f]` 才拿得到原樣路徑,但 `changed` 只涵蓋審查範圍。分岔點..頂端裡、不在 `changed` 的檔沒有原樣路徑可查。
失敗情境:樹裡存的是 NFD 檔名(舊 macOS 建的倉庫),about_code 的 NFC 鍵放進 `--literal-pathspecs`,git 比不到,回空 diff,該檔被記成「未改」,而作者其實改了它。這是漏判方向。程式裡已有多處註解提到這個坑(`scripts/lumos:36055` 一帶)。材料另外沒定義「切成逐檔」怎麼把 `diff --git a/x b/x` 區段對回 about 鍵。含空格和 ` b/` 的路徑會切錯,而 `_lens_git` 預設 quotePath 為真,中文路徑會被加引號。
建議:材料寫明用 `ls-tree -z` 之類建「NFC 鍵 → 原樣路徑」表,對兩邊樹都建;切檔用 `--raw -z` 或 `--name-status -z` 配對,不靠解析標題行。

severity: minor
blocking: 否 — 只會多列、不會漏判,但 S5 列的設定不全
引句:「作者本機設了 `diff.algorithm=patience`、`diff.noprefix=true`、`diff.interHunkContext=10`、`diff.mnemonicPrefix=true`、外部 diff 工具時,指紋應與沒設時相同」
問題:
- `diff.suppressBlankEmpty=true` 會把空白上下文行從 `" "` 變成空字串(實測),而空白是「照算」的。
- `core.quotePath` 材料沒提,只有走 `_ns_git`(`quote=True`)才釘死。
- 材料說「沿用 `_NOTE_REREAD_DIFF_ARGS`」,這組參數裡沒有 quotePath。

失敗情境:兩台機器設定不同,同一份改動算出不同指紋,只是多列。
建議:S5 補 `diff.suppressBlankEmpty`,並寫明走 `_ns_git`。

severity: minor
blocking: 否 — 沿用 v1 的口徑,但 v2 把宣稱變強了
引句:「手動 `reread-prepare --diff <任一起點>..<頂端>` 與推送前 `reread-check --push-remote … --pushed-ref …` 算出的對照指紋應相同」
問題:指紋蓋住整條分支的改動,判定者讀的卻是 `--diff` 範圍的那一段。手動 `reread-prepare --diff HEAD~1..HEAD` 只讀最後一個提交,記的對照紀錄卻讓整條分支的指紋都算已對照。v1 也有這個口徑,但 v1 宣稱的是「對照過這一版程式」,v2 宣稱的是「對照過分支的改動」,語意更強。
建議:材料明說這是接受的風險,並寫出回頭看的條件。

severity: minor
blocking: 否 — 邊界行為沒寫,但都是多列方向
引句:「零條或多條退回目前簽出的分支」
問題:幾個邊界材料沒寫:
- detached HEAD 沒有「目前簽出的分支」(實測 detached 時 `for-each-ref --points-at` 回 `feat`)。
- detached 且恰好一條分支指向頂端時,行為從「用 origin」變成「用該分支的上游」,與「呼叫點傳 HEAD、行為不變」不完全一致。
- 頂端被合進本機 main(`_codeloop_default_base` 一定加入 `refs/heads/main`)時,merge-base 等於頂端,整批退回 v1,卻沒寫。
- criss-cross 多個 merge-base 取歷史最長(`_push_pick_base`,`scripts/lumos:47361`),選哪個會讓分岔點跳動,此時分岔點可能夾進另一側的改動。
- 合併提交當頂端:這種情形材料沒有講。
- 全部候選的 about_code 聯集塞進同一條 argv,沒分批,大圖譜可能超過 ARG_MAX。

建議:每種情形補一條驗收,或寫明「一律退回 v1」。

## 驗收條款能否寫成先紅的測試

severity: minor
blocking: 否 — 條款本身可測,但紅綠分布與夾具要求沒寫
引句:「兩條分支對同一支 Python 檔的改動只差縮排」
問題:
- 現有測試夾具 `_rr_repo`(`scripts/test_lumos.py:69047` 一帶)沒有 main 或 origin,新指紋在那裡一律退回 v1。S1、S6 要建 main、origin、feature 三方。
- 先紅(對現行程式):S1、S6 會紅。S7 在 v1 下兩條分支 blob 不同,指紋本來就不同,不是先紅,也抓不到「忽略空白」的實作,得靠變異實驗(把縮排正規化掉要紅)。S2、S3、S4、S5 在 v1 下都已經綠,不能當先紅,只能當守護測試,要靠變異驗證。
- S4 的期望值要寫成 v1 的字面十六進位(v1 指紋只由 blob 編號決定,所以固定),不要在測試裡重算一次,否則是把實作重寫一遍。
- S1 和 S6 共用同一個測試名 `t_reread_fp_survives_mainline_advance`,拆成兩支,不然一支紅了分不出哪條。
- 缺的條款:標題函式名、二進位檔、全「未改」常數、NFD 路徑、分批、逾時退回 v1、v1 紀錄在升級後仍算數、v2 與 v1 不撞、合併提交與 detached 與多分支與 criss-cross。
- 現有 `t_codeloop_default_base_prefers_newest_mainline`(`scripts/test_lumos.py:37263`)要隨簽名改。

其他節(緣起、〈做法〉3 到 5、實務隱患、回退):已讀,無 finding。

最高等級 major,共 4 條 blocking(hunk 標題、二進位檔、全「未改」常數、NFC 與原樣路徑對應)。

相關檔案:
- 材料:`/tmp/回頭重讀指紋不因主線前進失效-r1.md`
- 程式:`/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos`
- 測試:`/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/test_lumos.py`
