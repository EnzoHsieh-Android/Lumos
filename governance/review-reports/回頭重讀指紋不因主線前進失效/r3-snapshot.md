---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/guards-gates
  - risk/守衛面
lands_in:
  - Systems/筆記內容審
  - Systems/pitfalls-code-loop
related:
  - "[[Projects/守檔筆記對照改動_計劃]]"
  - "[[Projects/舊句兩道轉擋_計劃]]"
  - "[[Issues/推送前其他閘的範圍在合過主線時會多算]]"
  - "[[Issues/預設起點與名冊人數收尾小問題]]"
---
# 回頭重讀指紋不因主線前進失效_計劃

> 白話:推送前的「回頭重讀」會記住「這篇筆記對照過這一版程式」。現在它認的是程式檔在分支頂端的整份內容,所以只要主線有人改了同一支檔、你 rebase 上去,你自己的改動一個字沒變,所有對照過的筆記也全部要重讀一遍。改成認「你這條分支對那支檔做的改動本身」:主線前進、rebase 之後,只要你的改動沒變,對照紀錄照樣算數。

## 緣起

- 2026-10-13 一條分支因主線連續前進兩次而 rebase 兩次,回頭重讀也跟著重派兩次;自己的改動沒變,判定者讀的是同一段改動。`scripts/lumos` 被大約 49 篇筆記的 about_code 管著,主線上任何人改到它,所有管它的筆記在每條進行中的分支上都會失效。出處:使用者 2026-10-14 問「這次示範有什麼 lumos 可以改進」時列的第 3 條。
- 詞彙:**候選**=這次推送要對照的家筆記(改到的檔的家 ∩ 這次被改過的筆記);**主線候選**=算分岔點用的主線分支(遠端 HEAD、main/master 的上游等);**頂端**=被推送(或被 prepare)的那個提交;**對照紀錄**=`governance/reread-verdicts/` 裡以對照指紋開頭的判定紀錄。
- 原設計 [[Projects/守檔筆記對照改動_計劃]] 的對照指紋是雜湊(筆記路徑、那篇頂端 about_code 每支檔的頂端 blob、範本版本),刻意不含範圍與 diff。理由寫在它的〈做法〉第 1、2 節:「手動 prepare 與推送前 check 的起點算法可能不同,含 diff 的指紋對不上、提醒永遠消不掉」(設計審 r1 四席)。本計劃要推翻「不含 diff」這一半,所以必須正面回應那條理由(見〈做法〉3)。

PRIOR-ART: git 自己的 `git patch-id --stable` 就是為了「rebase 之後認出同一個改動」而設計(`git cherry`、`git rebase` 判斷哪些提交已經在上游都靠它):把 diff 去掉行號後雜湊。借它「去掉行號、`index` 行」的想法,但不借它「忽略所有空白」那一半——本 repo 以 Python 為主,縮排就是語意,忽略空白會把縮排不同的改動當成同一個(前掃實測:把 `return y` 搬進迴圈與只縮成兩格,patch-id 相同);正規化重用本 repo 既有的逐檔改動指紋函式 `_patch_file_changes`(資安席用來認「rebase 之後同一版改動」),不另跑 `git patch-id`、不另寫第二套。主線分岔點借本 repo 既有的手動代碼審預設起點算法(主線候選與推送閘共用);同一次 check 裡候選範圍與指紋用不同的起點函式,理由見〈做法〉3。
RETIRE-IF: 上線 8 週內,`note-reread` 事件裡「靠 `v2` 命中」的篇數是 0(新指紋沒有省下任何一次重讀),或從「靠 `v2` 命中、`v1` 不會命中」那一群抽查到一次該重讀卻被當成已對照——撤回成只認 `v1`。
REVISIT:2026-12-15 照 RETIRE-IF 數一次 `note-reread` 事件的 `covered_by` 與 `fp` 欄位,並從「靠 `v2` 命中」那一群抽 5 篇,人工比對判定者當時讀的 diff 與頂端的程式,看舊句有沒有該點出卻沒點出的。

## 做法

1. **新指紋(`v2`)認「這條分支對每支檔的改動」**:雜湊(筆記路徑、範本版本、一行 `指紋算法 v2`、那篇 about_code 每一項配上「它在分岔點..頂端的改動指紋」)。舊指紋(`v1`)= 現在的頂端 blob 指紋,雜湊輸入一字不改、不加版本字樣。
   - **先拿清單、不靠路徑比對**:跑一次 `git diff --raw -z --no-renames <分岔點> <頂端>`(不帶 pathspec),得到這條分支改過的每支檔(git 原樣路徑的位元組、兩邊的物件編號與 mode、狀態)。原樣路徑經 `_nodehome_key` 換成 NFC 鍵,跟 about_code 的鍵比;「未改」的意思是「不在這份清單裡」,不是「diff 沒有輸出」——樹裡存的是 NFD 檔名、或 about_code 的鍵當成 pathspec 比不到,都不會被誤記成未改(r1 正確性席、邊界席實測過這個洞)。about_code 的某一項在分岔點與頂端兩邊的樹裡都找不到(拼錯、是資料夾),整篇退回 `v1`。
   - **文字檔**:對清單裡的每一支,單獨跑一次 diff(全域開 `--literal-pathspecs`,路徑用 git 原樣路徑、前面加 `--` 分隔,**不加** `:(literal)` 前綴——兩者併用時 git 會把前綴當成檔名的一部分、輸出變空,r2 三席實測);清單裡有這支檔、diff 卻是空的,那篇退回 `v1`。輸出交給既有的逐檔改動指紋函式 `_patch_file_changes`——它本來就是「rebase 之後還認得同一版改動」的指紋(資安席在用),會去掉行號與文字檔的 `index` 行、處理引號路徑、mode 與新增刪除。它現在連 `@@` 後面的函式名標頭一起算;本計劃給它加兩個參數,預設都不變(資安席照舊),回頭重讀這邊都打開:「不算函式名標頭」;「只用 `\n` 切行」——它現在用 `splitlines()`,會在換頁符號(`\x0c`)、U+2028 等字元處多切一刀,切出來的後半段不以 `+`、`-`、空白開頭而被丟掉,同一行換頁符號之後的改動就不進指紋(r2 兩席實測)——函式名標頭取自 hunk 之前最近一行頂格的行,主線改了封閉函式的簽名、或在上方新增頂格的一行,作者的改動一字未變它也會變(r1 三席實測)。
   - **二進位檔、被設成 `-diff` 的檔、子模組**:diff 帶 `--full-index`;`_patch_file_changes` 本來就對「Binary files … differ」改記 `index` 行裡改後那一邊的物件編號(帶 `--full-index` 才是完整編號),子模組的「Subproject commit」行是一般增刪行,照算。所以不另外判二進位。這些檔主線改了也會讓指紋變,方向是多列。型別變更(`--raw` 狀態 `T`,例如一般檔變符號連結)那篇退回 `v1`。
   - **選項的來源**:「釘住 hunk 切法」的兩個旗標(`--inter-hunk-context=0 --diff-algorithm=myers`)抽成一個常數,筆記形狀閘那兩份既有的 diff 選項與這裡共用;指紋用的這組在現有給判定者組 diff 的 `_NOTE_REREAD_DIFF_ARGS` 旁定義、由它延伸;git 呼叫用 `_lens_git`(它有逾時參數,`_ns_git` 沒有)。全域選項放在 `diff` 之前(`--literal-pathspecs`、`-c core.quotePath=false`、`-c diff.suppressBlankEmpty=false`、`-c diff.indentHeuristic=true`——放在 `diff` 之後 git 會回 129,r1 兩席實測),diff 選項是 `--no-ext-diff --no-textconv --no-color --no-renames --diff-algorithm=myers --inter-hunk-context=0 -U3` 加已釘的前綴。`core.attributesFile`、`.git/info/attributes` 讓某支檔在一台機器上變成 `-diff` 的情形照樣會讓兩台機器算出不同指紋,只會多列,不另處理。
   - **位元組原樣**:git 輸出以位元組讀、用 `surrogateescape` 解碼再編碼回去雜湊,不用 `errors="replace"`(那會把不同的非 UTF-8 位元組變成同一個字)。
   - **大小上限**:跑 diff 之前,用 `git cat-file -s` 看清單裡那支檔兩邊的物件大小,任一邊超過 4 MB 那篇退回 `v1`、不跑 diff(避免一支大檔先整份讀進記憶體;`scripts/lumos` 約 3 MB,在上限內)。`--raw` 加 `--no-abbrev`,物件編號是完整的。
   - **快取**:逐檔結果放進那一次掃描的 `scan` 裡,鍵是(分岔點、頂端、原樣路徑);一次推送多個 ref、測試在同一個程序裡跑很多暫存 repo,都不會互相污染。
2. **全部「未改」就退回 `v1`**:候選是用範圍起點算的,指紋是用分岔點算的,兩者可能不同,會有「是候選、但 about_code 每一項在分岔點..頂端都未改」的筆記(這次把某檔移出 about_code、分支先改又改回、手動給的範圍很寬)。這種筆記的 `v2` 會是一個跟程式版本無關的常數,一旦記過一次,之後任何同形狀的分支都會被當成已對照——所以整篇改用 `v1`(r1 邊界席)。
3. **分岔點只有一種算法,跟推送參數無關**(回應舊否決理由):手動代碼審的預設起點那支函式 `_codeloop_default_base`(主線候選照推送閘的 `_push_mainlines`,外加本機 main/master;多個共同祖先照 `_push_pick_base` 取歷史最長的)的本體,搬到推送起點那一區成為共用函式 `_lens_default_base(repo_root, tip=None, include_local=True)`,`_codeloop_default_base(repo_root)` 留成呼叫它的薄包裝(行為不變,代碼審判定唯一的呼叫點與 7 支既有測試照舊):
   - `tip=None`:跟現在一樣看 HEAD 與目前簽出的分支;
   - **回頭重讀傳 `include_local=False`**:主線候選只收遠端那幾個,不加本機 main/master。本機 main 上還沒推出去的提交沒有任何一次推送替它重讀過,把它算進主線,那段改動就沒人對照(r2 正確性席);只有本機主線、沒有遠端主線時,算不出分岔點,退回 `v1`;
   - `tip` 是一個提交編號時,「這條分支的上游遠端」改成看「指向這個提交的本機分支」:恰好一條就用它登記的上游遠端;零條或多條就跟現在沒有分支時一樣(有 origin 用 origin、只有一個遠端用它)——不看目前簽出的是哪條,這樣結果只取決於 refs 與頂端,跟在哪個工作樹、簽出什麼無關。`merge-base --all` 也改對 `tip` 算。
   - 回頭重讀一律傳解析好的提交編號。所以手動 prepare 與推送前 check 在同一份 refs 狀態、同一個頂端下算出的分岔點必然相同。舊理由說的「起點算法可能不同」是指範圍起點:兩個子指令都經 `_note_audit_start` 取起點,不帶推送參數走 `_lens_push_base`(給定的起點在本機找得到就原樣用),帶推送參數走 `_push_range_start`;那個起點照舊只決定「誰是候選」,不進指紋。
   - 為什麼不用 `_push_range_start`:它吃 `--push-remote`、`--pushed-ref`,手動 prepare 沒有這兩個值,正是舊理由說的分歧來源。這個新消費者登記進 [[Issues/推送前其他閘的範圍在合過主線時會多算]] 的收斂清單;那篇 Issue 與 [[Issues/預設起點與名冊人數收尾小問題]] 講的是同一支函式,`--short` 與分支、標籤同名的問題照那篇 Issue 的條件另修,本計劃不併入,在兩篇 Issue 互相連結。
   - 已知會變的情形(都是多列方向,不擋正確性):另一個工作樹把本機 main 快轉到含頂端時,分岔點變成頂端本身,退回 `v1`;fetch 之後沒 rebase,分岔點不變;交叉合併有多個共同祖先時照歷史最長取。
   - CI:CI 的 reread-check 不擋、只印(見 [[Systems/筆記內容審]] 的 WHY 行)。CI 沒有本機 main/master、也可能是淺層 clone,算出的分岔點可能不同或算不出而退回 `v1`;結果只會多列。
4. **新舊兩種指紋都認**:check 判一篇「已對照」照這個順序:先看 `v1`——有一筆已提交、來源核對過的紀錄,檔名開頭是這篇的 `v1` 指紋,或紀錄內容的 `contrast_fp_v1` 欄位等於它;`v1` 不中,再看 `v2`——有一筆這樣的紀錄,檔名開頭是這篇的 `v2` 指紋,**而且那支紀錄檔是這條分支自己新增的**(分岔點的樹裡沒有它)。`v1` 相符代表 about_code 每支檔在頂端逐位元組相同,比 `v2` 嚴格,認它不會漏判。
   - **為什麼 `v2` 只認分支自己的紀錄**:`v2` 只含改動本文與前後三行,不綁檔案其他部分。紀錄合進主線後永遠留著,之後別的分支只要做出逐字相同的改動(例:有人把預設值改回去、之後又有人再改一次),就會命中多年前那筆紀錄,筆記卻已經不是當時那樣(r2 正確性席)。分支自己的紀錄在 rebase 之後仍是分支自己新增的,所以 rebase 的好處照樣拿得到。
   - prepare 能算 `v2` 時,紀錄檔名用 `v2`,內容同時記 `contrast_fp_v1`;算不出時檔名用 `v1`。這樣分支本機快轉進 main 再推 main(分岔點等於頂端、只算 `v1`)時,只要程式沒再動,分支上記的那筆照樣命中(r2 正確性席)。
   - 好處:升級那天進行中分支的舊紀錄照舊算數,不用重派判定者、不用重新表態;回退時 `v2` 紀錄只是不再命中的檔,`v1` 紀錄照舊可用。
   - 第二層(規則類條目要表態)按筆記路徑讀紀錄、表態以判定紀錄的指紋為鍵;因為不必重新 prepare,升級本身不會產生要重新表態的條目。
5. **算不出就退回 `v1`**:分岔點算不出(沒有主線候選、沒有共同祖先、git 失敗)、分岔點就是頂端本身(推的是主線、或頂端已在主線上)、about_code 有一項兩邊的樹都找不到、全部未改(第 2 點)、單檔 diff 超過上限、或 git 呼叫逾時——那一篇用 `v1`。退回只會讓已對照的被多列,不會漏判。
   - **逾時吃剩餘預算**:reread-check 有約 30 秒的軟上限。指紋這一步的每次 git 呼叫,逾時取「20 秒」與「整體剩餘預算減 3 秒」的較小者;剩不到 3 秒就不跑,剩下的候選直接用 `v1`。所以這一步不會把後面第二層的預算吃光、變成整次判不了。這跟掃描那一段既有的做法(在呼叫點之間看截止時間、過了就停下判不了)刻意不同:指紋這一步有安全的退路(`v1`),所以降級、不停。prepare 沒有整體預算,可能算出 `v2`、而 check 退回 `v1`——那篇會被多列一次,事件會記下退回原因(第 7 點),可量。
6. **判定者讀的範圍跟指紋同一個基準**:用 `v2` 時,prepare 給判定者的 diff 改成「分岔點..頂端、只含那篇 about_code 裡出現在 `--raw` 清單上的檔」(不是用推送範圍改到的檔取交集),跟指紋證明的範圍一致;給判定者的 diff 因超過字數上限被縮短時,那篇改用 `v1`(判定者沒讀完整,不能替整份改動背書)(r1 邊界席:原本手動 `--diff HEAD~1..HEAD` 只讓判定者讀最後一個提交,記下的紀錄卻讓整條分支都算已對照)。退回 `v1` 時照現在用範圍 diff。材料指紋的算法不變(仍含給判定者的 diff 全文)。
7. **事件記得到要量的東西**:`note-reread` 事件(reminded、blocked、covered、none 都算)在 `extra` 裡多四個欄位(不用 `ref` 欄,免得被代碼審留痕的讀者誤讀):`branch`(推送前 check 用被推的 ref,手動用目前簽出的分支,detached 寫空)、`fp_counts`(這次候選裡 `v2`、`v1` 各幾篇,`v1` 的再按退回原因分:無遠端主線、在主線上、樹裡找不到、全部未改、太大、型別變更、diff 空、判定者材料被縮短、逾時)、`covered_by`(已對照的篇數裡,靠 `v1` 命中、靠 `v2` 命中各幾篇——先判 `v1`,所以「靠 `v2`」就是新指紋放寬的那一群)、`v2_only`(靠 `v2` 命中的那幾篇的筆記路徑與兩種指紋,最多 20 篇)。既有的 `layer1_fps` 每筆多一個 `ver`。RETIRE-IF 的漏判抽查從 `v2_only` 抽。
8. **呼叫點與函式**:現在的 `_note_reread_contrast_fp` 保留原名原簽名當 `v1`(直接呼叫它的兩支既有測試不用改);新增 `v2` 那一支;`_note_reread_fps` 與 prepare 單篇那個呼叫改成先算 `v2`、算不出用 `v1`,`_note_reread_covered` 收兩種指紋。

## 要一起改的說法

照 [[Projects/舊句兩道轉擋_計劃]]〈要一起改的說法〉的先例,現況句就地改成新事實,舊理由留一行帶日期的歷史(「2026-10-14 前不含 diff,理由是……,由 [[Projects/回頭重讀指紋不因主線前進失效_計劃]]〈做法〉3 取代」):
- 程式:回頭重讀第一層擋下時印的那句「對照指紋含這篇 about_code 列的程式在頂端的版本——合併主線帶進別人對同一支程式的改動、筆記改名、about_code 增減都算」改成新說法(主線帶進的改動不再算,作者自己的改動、筆記改名、about_code 增減照算);`_note_reread_contrast_fp` 的 docstring 標成 `v1` 並說明何時用。
- 手冊 `skills/lumos-project-notes/commands/06-代碼審與推送.md` 講「程式改了(含合併主線帶進別人對同一支程式的改動、rebase……)就要重判」那句,與消費專案 CI 那段。
- [[Systems/筆記內容審]] 講「不含範圍與 diff」那段與 CI 的 WHY 行;[[Systems/pitfalls-code-loop]] 講 `_codeloop_default_base` 的 WHY 行與它的 REVISIT(多一個消費者)。
- [[Projects/守檔筆記對照改動_計劃]] 講「兩邊起點可能不同,但對照指紋不含範圍」「只用 `git ls-tree` 就能算」、誠實界線的盲區、設計審 r1 紀錄、S6;[[Projects/舊句兩道轉擋_計劃]] 講「不改對照指紋的組成」「對照指紋照舊含筆記路徑與程式 blob」的兩句。
- 測試 `t_note_audit_reread_check_reminds` 裡「翻紅釘:把範圍或 diff 算進去 → 紅」那段:改成釘 `v1` 那支函式(`v1` 仍不准含 diff),另加 `v2` 的釘。不改的話,下一個人會把它當守衛、把 `v2` 修回不含 diff。
- `t_reread_block_layer1` 釘的那句子字串跟著改。
- CHANGELOG 照現有格式加一筆;版號不升——這次沒有改掛鉤、紀律區塊或範本,消費專案 `lumos update` 就拿得到。
- 改了 `scripts/test_lumos.py`,提交前 `lumos anchor approve`。

## 驗收條款

- [S1] 當分支改了 `a.py`、對照紀錄已記,接著主線也改了 `a.py`(不在作者改動的前後三行內)、作者 rebase 到新主線時,reread-check 應認得那篇已對照(靠 `v2` 命中)、不再列出。[test: t_reread_fp_survives_mainline_advance]
- [S2] 當 rebase 時解衝突改到了作者對 `a.py` 的那一段時,reread-check 應重新列出那篇。[test: t_reread_fp_changes_with_own_patch]
- [S3] 同一份 refs 狀態、同一個頂端,手動 `reread-prepare --diff <任一起點>..<頂端>` 與推送前 `reread-check --push-remote … --pushed-ref …` 算出的對照指紋應相同(起點不同、有兩條本機分支指向同一頂端、從不同工作樹跑,也一樣)。[test: t_reread_fp_same_for_prepare_and_check]
- [S4] 推主線(頂端在主線上)或算不出分岔點時,指紋應等於現行頂端 blob 指紋算法算出的值(測試寫死那個十六進位字面值,不在測試裡重算)。[test: t_reread_fp_falls_back_to_blob]
- [S5] 作者本機設了 `diff.algorithm=patience`、`diff.noprefix=true`、`diff.interHunkContext=10`、`diff.mnemonicPrefix=true`、`diff.suppressBlankEmpty=true`、`diff.indentHeuristic=false`、外部 diff 工具時,`v2` 指紋應與沒設時相同。[test: t_reread_fp_ignores_local_diff_config]
- [S6] 分支沒改、但主線改了某篇的第二支 about_code 檔時,那篇的指紋不應改變。[test: t_reread_fp_untouched_file_ignored]
- [S7] 兩條分支對同一支 Python 檔的改動只差縮排(例:一條把 `return y` 搬進迴圈、一條只把它縮成兩格)時,兩者的指紋應不同。[test: t_reread_fp_keeps_whitespace]
- [S8] 主線只改了作者那段所在函式的 `def` 那一行(離作者改動超過三行)、作者 rebase 後,指紋不應改變。[test: t_reread_fp_ignores_function_header]
- [S9] 分支先後把同一支二進位檔(或設成 `-diff` 的檔)改成兩種不同內容時,兩次的指紋應不同。[test: t_reread_fp_binary_by_object]
- [S10] about_code 用 NFC 寫、樹裡存的是 NFD 檔名、分支改了那支檔時,那一項不應被記成未改。[test: t_reread_fp_nfd_path_not_unchanged]
- [S11] 候選筆記的 about_code 每一項在分岔點..頂端都未改時,應用 `v1`。[test: t_reread_fp_all_unchanged_uses_v1]
- [S12] 升級前用 `v1` 記的紀錄,升級後同一頂端的 check 應照舊認得已對照;只有 `v2` 紀錄、改用 `v1` 判的情形(回退)不應被當成已對照。[test: t_reread_fp_accepts_v1_records]
- [S13] reread-check 的 `note-reread` 事件應帶 `branch`、`fp_counts`、`covered_by`、`v2_only`,`layer1_fps` 每筆帶 `ver`。[test: t_reread_fp_event_fields]
- [S14] 整體預算剩不到 3 秒時,指紋這一步不應再跑 git,剩下的候選應用 `v1`,check 不應因此判成「判不了」。[test: t_reread_fp_respects_budget]
- [S15] 用 `v2` 時,prepare 給判定者的 diff 應是分岔點..頂端、只含那篇 about_code 裡分支改過的檔,即使手動給的 `--diff` 範圍只有最後一個提交;給判定者的 diff 被縮短時,那篇應用 `v1`。[test: t_reread_prepare_material_matches_fp]
- [S16] 同一行在換頁符號之後的內容不同的兩種改動,`v2` 指紋應不同;清單裡有某支檔、diff 卻是空的,那篇應用 `v1`。[test: t_reread_fp_split_and_empty_diff]
- [S17] 主線上已有一筆 `v2` 紀錄,另一條分支做出逐字相同的改動時,不應被那筆紀錄判成已對照;同一條分支 rebase 之後,自己的 `v2` 紀錄應照樣命中。[test: t_reread_fp_v2_only_own_records]
- [S18] 本機 main 有還沒推出去、改到 about_code 檔的提交,分支從它開出時,那支檔不應被記成未改(分岔點只看遠端主線)。[test: t_reread_fp_ignores_local_mainline]
- [S19] 分支記了 `v2` 紀錄、本機快轉進 main 後推 main(只算 `v1`)且程式沒再動時,應照樣判已對照。[test: t_reread_fp_ff_main_uses_v1_field]

- 測試怎麼搭:現有的回頭重讀測試夾具只有一個沒有遠端的 repo,分岔點等於頂端,一律走 `v1`;S1–S3、S5–S11、S13–S19 要另搭「有遠端、遠端 main 在頂端之前、分支在上面」的夾具(`remote add` 加 `update-ref refs/remotes/origin/main`,照 `t_codeloop_default_base_prefers_newest_mainline` 的搭法)。S10 的 NFD 檔名要用 `-c core.precomposeunicode=false` 加 `hash-object`、`update-index --cacheinfo` 這類底層指令造;S2 用 `commit-tree` 手造兩個提交,不跑真的 rebase 衝突;S9 要提交一支 `.gitattributes`(`*.dat -diff`);S14 用既有的 `deadline` 參數注入;S3 的「不同工作樹」用 `git worktree add`。S1 要斷言命中的是 `v2`(不是碰巧 `v1` 也相同)。S4、S7、S12 對現行程式本來就是綠的,是守衛,要用變異驗證(例如把空白正規化掉、把 `v1` 的雙認拿掉)證明會紅。
- 既有測試:`t_codeloop_default_base_prefers_newest_mainline` 照舊呼叫單參數、要照舊綠;`t_note_audit_reread_check_reminds` 與 `t_reread_block_layer1` 照〈要一起改的說法〉改。

## 實務隱患

- 守衛面:這是推送前會擋的閘(`note_reread.gate` 是 block 時)。風險是「該重讀的被當成已對照」。新指紋比舊指紋寬的地方只有兩種:主線改了作者沒碰的檔(第 1 點「未改」)、主線改了作者碰過的檔但不在作者那段的前後三行內且不是那段的內容。這兩種在舊指紋下會重派,但重派時判定者讀的也只是作者自己的 diff(rebase 後範圍起點是新主線),舊指紋並沒有讓判定者看到主線的改動——所以新指紋沒有拿掉任何真的審查。主線那邊的改動照常由它自己那次推送(以它自己的候選)處理;那條推送走 `--no-verify` 或閘設成不擋時沒有人重讀,這在舊指紋下也一樣。全部未改、樹裡找不到、二進位檔、NFD 路徑四個洞由第 1、2 點與 S9–S11 守。
- 已排除:金流:不碰。
- 已排除:對外送出:只跑本機 git。
- 已排除:不可逆:紀錄檔格式不變;新舊兩種指紋都認,升級與回退都不會讓既有紀錄失效(回退後 `v2` 紀錄只是不再命中)。
- 時間:check 多一次 `git diff --raw` 與每支改到的 about_code 檔一次 diff(只對分支改過的檔,通常幾支),在剩餘預算內跑(第 5 點);耗時實作時在本 repo 量一次寫進實作紀錄。

## 回退

- 還原提交即回到只認 `v1`;升級期間記的 `v2` 紀錄不再命中,那幾篇在進行中的分支上要重 prepare 一次(只限升級後才 prepare 的那幾篇)。事件多出的欄位舊讀者不讀,無害。消費專案 `lumos update` 取回舊版。

## 審計修正紀錄

- r1(2026-10-14,6 席):35 條/blocking 12/改動指紋有四個會漏判的洞(函式名標頭、二進位檔、NFC/NFD 路徑、全部未改成常數)、選項位置照字面做會整個失效、升級會讓所有紀錄一次失效、撤除條件量不到、要一起改的說法沒列、跟既有逐檔改動指紋另寫一套;全數折入:先用 `--raw -z` 拿清單、文字檔重用 `_patch_file_changes` 並關掉函式名標頭、二進位改記物件編號、全部未改退回 `v1`、新舊兩種指紋都認、事件加欄位、判定者讀的 diff 跟指紋同基準、新增〈要一起改的說法〉與 S8–S15。席報告在 `governance/review-reports/回頭重讀指紋不因主線前進失效/`。
- r2(2026-10-14,3 席:正確性、邊界、架構對齊,只看 r1 折入後的改動):18 條/blocking 6/`:(literal)` 前綴與全域旗標併用會讓 diff 變空、重用的函式在換頁符號處切錯、`v2` 不綁檔案版本使主線上的舊紀錄能替之後相同的改動背書、本機 main 上沒推的提交被當成主線、快轉進 main 後推 main 用不到分支紀錄、事件量不出放寬那一群;全數折入:只留全域旗標、`_patch_file_changes` 加只用換行切行的參數、`v2` 只認分支自己新增的紀錄、分岔點只看遠端主線、紀錄同時記 `v1`、先判 `v1` 再判 `v2` 並記 `v2_only`、共用起點函式搬到推送起點區。新增 S16–S19。
