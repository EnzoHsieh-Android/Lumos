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
  - Systems/codex-harness
  - Systems/派工鏡頭
  - Systems/每輪修補差異派工
  - Systems/design-loop
related:
  - "[[Projects/派工鏡頭跨repo不再靜默_計劃]]"
decisions:
  - content: 設計審的 LUMOS-SPEC 多收「完整提交編號:計劃路徑」,lumos 在會談 repo 從共用物件庫讀那個提交裡的計劃;編號由 lumos spec-freeze 產生;不讓派工詞指定任何目錄或別的 repo
    id: d1
    context: 計劃常只存在別的 git 工作樹,掛鉤在會談目錄找不到計劃,一晚十幾席設計審都沒拿到固定席節點。第一輪設計審試讓派工詞指定任意路徑、用權限位元判信不信,第二輪改成登記清單,兩輪共 51 條發現幾乎全出在「派工詞的文字決定去哪裡跑 git」這一層;第三輪改成讀提交裡的計劃,46 條發現集中在提交編號的形狀、只讀一般檔、文法由誰判、快照與提交沒綁在一起、回退漏掉全域 lumos
    why_chosen: 同一個 repo 的工作樹共用物件庫,讀提交只在會談 repo 跑 git,不碰派工詞指到的目錄,跟代碼審寫完整提交編號同一個道理;只收完整編號才沒有被同名分支搶走的歧義;spec-freeze 用暫存 index 建不掛分支的提交,快照與提交一定一致,也不用先正式提交草稿
    alternatives_considered:
      - "派工詞指定任意路徑,用權限位元判信不信:擋不住 .git 檔裡指到別處的 commondir、權限放寬的設定檔、從沒用過的下載 repo,又會在 /tmp 底下誤殺"
      - "派工詞指定路徑,再比對一份登記清單:清單放哪、誰能寫說不清,拒絕說明本身會誘導人去登記,會談本身是工作樹時怎麼列工作樹也要另判"
      - "讀 git worktree list 的工作樹清單,比對派工詞的路徑後去那裡讀檔:仍是派工詞的文字決定去哪個目錄讀,而且讀的是沒凍結的工作樹內容,快照與鏡頭對不上"
      - "把凍結快照放進會談目錄、派工詞貼工作樹路徑(不用新子命令與新寫法):會在會談目錄留未追蹤檔,撞全域規則「不碰別的會談的工作目錄」;而且工作樹路徑那條的 vault 取 slugs[0],repo 有兩個 vault 時會選錯 vault"
    trade_offs: "完全不同的 repo 照舊不支援,只附說明行、手動貼固定席;每輪派工前要多敲一次 lumos spec-freeze;只收完整提交編號,手打不方便;spec-freeze 是 lumos 第一個寫 git 物件的子命令,刻意落兩週後會被 gc 的懸空物件;成功不記事件,用量只能數派工單"
    decided: 2026-10-14
    valid: true
---
# 派工鏡頭可指定目標repo_計劃

> 白話:派審查席時,掛鉤會自動把「這次改動牽連到的圖譜筆記」貼進派工詞。它一律在「會談開在哪個資料夾」那裡算。全域規則要求每份工作開獨立的 git 工作樹,於是計劃常常只存在別的工作樹裡,掛鉤在會談目錄找不到,只附一行「沒附」。同一個 repo 的工作樹共用同一份 git 物件庫:在計劃所在的工作樹跑 `lumos spec-freeze`,把計劃凍成一個不掛分支的提交,在會談目錄就能用「完整提交編號:計劃路徑」把它讀出來,凍結快照也在會談目錄用同一個寫法寫出。改成:設計審的 `LUMOS-SPEC:` 可以寫成 `<完整提交編號>:<計劃路徑>`,lumos 在會談 repo 裡從那個提交讀計劃;程式檔與節點存不存在照會談目錄判,只在提交裡有的另外列名。不去別的目錄跑 git,不新增信任機制;完全不同的 repo 照舊不支援,附說明行。

## 緣起

- 2026-10-13 後端示範:會談開在 lumos 工具鏈,審的是示範 repo `order-demo` 的分支,派工鏡頭算不出牽連筆記(只附了說明行)。2026-10-14 夜裡更普遍:全域規則要求每個工作開獨立的 git 工作樹,我在三個工作樹各開一份計劃、派了十幾席設計審,計劃只存在那些工作樹裡,掛鉤在會談目錄找不到,所有席都沒拿到固定席節點。出處:使用者 2026-10-14 列的示範改進第 4 條;當晚的席報告都寫「派工尾端沒有附固定席節點」。
- 舊裁定:[[Projects/派工鏡頭跨repo不再靜默_計劃]] 的 WHY 行寫「不選:標記行加 repo 路徑讓掛鉤改去那裡算(標記行文法要改、派工詞的自由文字會變成掛鉤去跑 git 的路徑,先不開這個口;說明行給繞法即可)」。**本計劃不推翻它**:第一、二輪設計審試過讓 `LUMOS-REPO:` 指定任意路徑,再用權限位元(r1)或登記清單(r2)判信不信,兩輪共 51 條發現,幾乎全出在「讓派工詞的文字決定去哪裡跑 git」這一層(`commondir` 指到別處、登記清單誰能寫、拒絕說明本身誘導登記、圍欄裡的標記被靜默忽略、被拒時取角色卡會用錯的樹、會談本身是工作樹時怎麼列工作樹)。這正是舊裁定擔心的口。
  - 改走的路:痛的是「同一個 repo 的另一個工作樹」(當晚十幾席都是這種),而工作樹共用物件庫,讀提交裡的計劃只要在會談 repo 跑 git,不碰派工詞指到的任何目錄。示範 repo 那種完全不同的 repo 一晚只出現一次,照舊附說明行、手動貼。

PRIOR-ART: 代碼審那條路已經是這樣:`LUMOS-IMPACT:` 寫完整提交編號,工作樹共用物件庫,在會談目錄就算得出別的工作樹的提交(派工範本已要求寫完整提交編號、不寫 HEAD)。設計審照同一個道理,把計劃路徑換成 git 原生的 `<rev>:<path>` 寫法(`git show` 本來就收這種寫法),不自創文法、不新增信任機制。提交編號的解法照抄 `_lens_full_sha`,讀提交裡的檔照抄 `_nodehome_cat_blobs_capped`。凍結提交借 git 原生的做法:`GIT_INDEX_FILE` 指一份暫存 index,`write-tree` 加 `commit-tree` 建不掛 ref 的提交(`git stash create` 就是這樣建提交、不動分支)。借用,不自建。
RETIRE-IF: Claude Code 在派工事件帶出子代理的工作目錄(會談目錄與工作目錄不再可能錯開),或連續 8 週沒有新的派工單帶 `spec_commit`(`git log --since=8.weeks --name-only --format= -- 'governance/review-reports/*/r*-dispatch.json'` 列出的檔裡,`grep -l spec_commit` 是 0 筆)——拿掉這個寫法與 `lumos spec-freeze`。
REVISIT:2026-12-15 數一次 `grep -l spec_commit governance/review-reports/*/r*-dispatch.json` 的筆數(用了幾輪),再數掛鉤事件裡 `spec_commit `、`spec_worktree ` 字首失敗 note 的代碼分布(成功不記事件,逾時那筆不帶字首),照 RETIRE-IF 判。

## 做法

1. **`LUMOS-SPEC:` 多收提交寫法,只收完整提交編號**:值以**第一個冒號**切開(檔名可以再含冒號)。冒號前全是十六進位、至少 7 碼時,當成「提交寫法」;其他值一律照現在當工作樹路徑。
   - 提交寫法裡,`<提交>` 必須是 40 或 64 碼十六進位(不分大小寫,內部轉小寫),用既有 `_lens_full_sha` 的解法(`rev-parse --verify -q --end-of-options <提交>^{commit}`),而且解出的完整編號必須等於轉小寫後的輸入;不合任一條都回 `spec_rev_missing`。
   - 所以短編號(7–39 碼、41–63 碼)、被同名分支或標籤導到別的提交、縮寫撞號,一律不成立:git 對不足完整長度的字串會先當 ref 名解析,同名分支會搶走(第三輪兩席實測);縮寫隨提交增加也會從解得到變成模稜兩可。只收完整編號,跟代碼審 `LUMOS-IMPACT:` 用的 `_LENS_SHA_RE` 同一個形狀。`_lens_git` 逾時或 git 跑不起來回 None,也歸 `spec_rev_missing`。
   - 分界:冒號前恰好 6 碼十六進位照工作樹路徑;恰好 7 碼起(含超過 64 碼)都是提交寫法,長度不是 40 或 64 就回 `spec_rev_missing`。大小寫混用的 40 碼照常成功。
   - 為什麼「至少 7 碼十六進位加冒號」就算提交寫法:寫短編號的人拿得到 `spec_rev_missing` 的說明,不會被當成工作樹路徑、拿到「先凍結」的繞法。工作樹路徑剛好以 7 碼以上十六進位的目錄名加冒號開頭,在 docs 底下實務上不會有。
2. **路徑規則(提交那條路新增,工作樹那條路不變)**:提交寫法冒號後的路徑必須是正規的 posix 相對路徑:不得空、不得以 `/` 開頭、不得有 `.`、`..` 或空段(連續兩個 `/`、結尾 `/`)、不得含反斜線或空白;至少三段,第一段必須正好是 `docs`、第二段必須是 `<slug>-knowledge`(slug 至少一個字元,大小寫照字面比,`Docs/`、`x-Knowledge` 都不合)。不合就回 `spec_outside_repo`。
   - 「空白」是 Python `str.isspace()` 為真的任何字元(含 tab、換行、U+3000 全形空白、NBSP)。
   - 只做字串檢查,不先正規化:`./docs/…` 這種 git 認得的寫法也擋,條款只收一種寫法。不復用 `_posix_norm`:正規化會把 `a/./b`、`a//b` 改寫成合法路徑,這裡要拒絕而不是改寫。
   - vault 用路徑自己的 slug,不取會談工作樹的 `slugs[0]`:repo 有兩個 `*-knowledge` 時,連結節點、落點、目標架構段都到計劃所在的那個 vault 找。會談工作樹的 `docs/` 底下沒有名字正好相同的 `<slug>-knowledge` 目錄時回 `no_knowledge`(比對 `docs/` 的目錄清單,不用 `is_dir()`:macOS 不分大小寫會讓同一份輸入在兩個平台回不同代碼)。
   - 檔名的 Unicode 正規化不處理:路徑不是 NFC(`unicodedata.is_normalized("NFC", 路徑)` 為假)就直接回 `spec_missing`,不交給 git——macOS 的 `core.precomposeunicode` 會把參數轉成 NFC,交給 git 判就平台相依。夾具檔名只用 NFC,NFD 只出現在輸入字串。
   - **檢查順序(同時違反時回第一個違反的代碼)**:①會談目錄在 git 專案裡,否則 `not_git`;②提交編號的長度與解析,否則 `spec_rev_missing`;③路徑字串規則,否則 `spec_outside_repo`;④路徑是 NFC,否則 `spec_missing`;⑤vault 在會談目錄存在,否則 `no_knowledge`;⑥`ls-tree` 是一般檔,否則 `spec_missing`;⑦大小,否則 `spec_too_large`;⑧讀內容,讀不到 `spec_missing`。
   - **工作樹那條路的檢查一律不動**:照現在接受絕對路徑、只看解析後在 repo 內與是檔案、沒有大小上限、`vault_rel` 照現在取 `slugs[0]`。唯一的差別是失敗時 `--json` 多印失敗代碼(見 6)。
3. **只讀一般檔**:提交寫法先用 `_lens_git(..., quote=True)`(帶 `core.quotePath=false`)跑 `ls-tree -z -l <完整編號> -- <路徑>`,結果必須正好一筆(以 NUL 切)、路徑欄等於輸入路徑、mode 是 100644 或 100755、type 是 blob;沒有這一筆,或是目錄(040000)、符號連結(120000)、子模組(160000),都回 `spec_missing`(目錄會印出檔名清單、符號連結會印出連結目標字串,不擋就會被當成計劃內容掃)。
   - 大小用 `ls-tree -l` 的 size 欄判:大於 1048576 回新代碼 `spec_too_large`;剛好 1MB(1048576 位元組)照讀。
   - 內容用既有 `_nodehome_cat_blobs_capped(root, ["<完整編號>:<路徑>"], 1MB)` 讀,不另組 `cat-file -s` 加 `show`:專案已經有「讀提交裡的檔、先問大小、超過上限不讀進記憶體」這一套,它的註解寫明上限放在批次讀取這一層、不另起查法(角色鏡頭代碼審架構席裁過)。大小已在上一步判過,所以單項回 None 一律當讀不到(物件被清或 missing),回 `spec_missing`、不回 `spec_too_large`;整批回 None(逾時或 git 失敗)也回 `spec_missing`。解碼照工作樹那條用 `utf-8` 加 `errors="replace"`,含 NUL 或非 UTF-8 的二進位計劃照常讀、不報錯。
   - 它內部直接起子行程、不走 `_lens_git`,所以「只在會談 repo 跑 git」改用 PATH 上的假 `git` 驗(S9),不靠替換 `_lens_git`。
4. **讀計劃收斂成一支**:新增共用的讀計劃函式(暫名 `_dispatch_lens_read_spec`),收 repo 根與標記值,回計劃文字、`spec_source`(`commit` 或 `worktree`)、完整提交編號、blob 編號、vault 路徑,或失敗代碼與 rc。`cmd_dispatch_lens_spec` 與 `_dispatch_lens_spec_with_arch` 都呼叫它,文法只在這一處判。
   - `_dispatch_lens_spec_with_arch` 不再自己 `Path(spec_path)` 讀檔(現在遇到提交寫法會讀檔失敗、目標架構段靜默消失):外層先呼叫一次,把結果交給 `cmd_dispatch_lens_spec`(新增選填參數),同一份計劃只讀一次、git 只跑一輪。
   - 目標架構段(`_dispatch_lens_spec_arch_text`)吃的計劃文字就是這一份。vault 也用這支回的那個(提交寫法是路徑得出的 vault),由外層傳進目標架構段,不再在裡面呼叫 `_arch_target_vault_rel(root, "HEAD")` 取排序第一個;工作樹寫法傳的是 `slugs[0]`,跟現在相同。宣告照現在從會談 repo 的 `.lumos/config.json` 讀,宣告裡的節點從會談 repo 的 HEAD、在傳進來的那個 vault 底下讀。
5. **程式檔存在照會談目錄判**:跟 impact 一致(impact 子行程用 `--repo <會談 repo 根>` 讀會談目錄)。計劃提到的程式檔照現在用會談目錄的 `is_file()` 判、照現在跑 impact。
   - 提交寫法時,會談目錄沒有、只在那個提交裡有的檔,另列一行「只在提交 <12碼> 裡、會談目錄沒有,沒算牽連:<檔>」,最多 5 個(同 `_LENS_SPEC_MAX_FILES`),不再落到「沒牽到任何家、合約或事故的節點」那句,讓席位以為已經算過。
   - 判法(2026-10-14 代碼審 r2/r3 起取代原寫的逐檔呼叫——每個候選各跑一次 `ls-tree`):候選一次交給既有的批次查大小 `_nodehome_cat_sizes`(`<完整編號>:<路徑>` 一行一個,壞候選只讓那一行沒有大小、不拖垮整批),有大小的再用只帶這些路徑的 `ls-tree -z`(一批最多 200 個路徑)看 mode,只有一般檔算數;候選最多 5000 個(見實作紀錄)。列滿 5 個就停;`scripts/../../x` 這種穿越不收。
   - 這一行抓得到的是「計劃所在分支已提交、會談目錄分支還沒有」的檔。工作樹裡還沒提交的新檔不進凍結提交(tree 只比 HEAD 多計劃),兩邊都沒有,照現在不列。
   - 反方向(會談目錄有、提交裡已刪)照會談目錄算、照附。
6. **連結節點與落點分三種(提交寫法)**:計劃直接連結的 Systems/Issues 節點:
   - 會談目錄有:照現在附,內容讀會談目錄那份。附加段頭寫明「節點內容是會談目錄的版本」(提交裡改過的版本不附)。
   - 只在那個提交裡有:用 `cat-file -e <完整編號>:<vault>/<節點>.md` 確認存在才列名,標「只在那個提交裡,會談目錄還沒有這篇」,內容不附;最多列 `_LENS_SPEC_MAX_NAMED`(20)篇,其餘只印「另有 M 篇連結的節點只在那個提交裡,沒列名」。名字含換行或 NUL 的算寫法不合(git 一行一筆的批次查詢問不到),兩種寫法都只計數。(2026-10-14 代碼審 r5 起取代原寫的「名字整段符合嚴格字元集才列名、不合只計數」:字元集分不出名字與指令,見下面「名字一律以資料形式印」。)
   - 兩邊都沒有:不印名字,只印筆數「N 個連結在會談目錄與凍結提交裡都找不到(可能是還沒提交的新節點或錯字)」。
   - **名字一律以資料形式印**(2026-10-14 代碼審 r5 起取代 r1–r4 的字元白名單與「不合印固定字樣」):計劃路徑、節點名、計劃提到的程式檔名、目標架構宣告的節點名、規則原文與命中檔名(代碼審與設計審兩條路)都經同一個出口 `_lens_author_name_show`——包在固定的一對標記 ‹ › 裡;控制、格式、行段分隔、替身、私用、未指派碼位,會撐破標記或框的 ‹ ›、反斜線、框線字元 ─ 與反引號,以及畫面上看不見的字(代碼審 r6 補變體選擇符與填充字,r7 起全照輸出跳脫用的同一份判定 `_lens_hidden_char`,正文最後一道 `_lens_visible` 也用它;r8 起 `_lens_visible` 對正常表情符號序列裡的單一 U+FE0F、U+200D 照印,名字出口照舊全跳),跳脫成看得見的 `\uXXXX`(同 `_kill_esc` 那套;超出基本平面的跳成 8 碼 `\UXXXXXXXX`);其他字(標點、韓文 NFD、整句英文)照印;節點名超過 80 字、路徑超過 300 字截斷並在標記後標明原長;空字串與只由空白、隱形字組成的名字印「(空名字)」(不加標記,分得出跟真叫這個名字的檔)。讀不讀節點只看路徑安全(`_vault_node_check`),程式檔照跑 impact。**整句英文或中文指令仍印得出**:防線不是字元集,而是「作者可控的文字一律在注入框內、包在標記裡、以資料出現」——有輸出就加框(工作樹寫法只有落點時也框),目標架構段由 `_arch_target_text` 自己加框(工具寫死的段首與尾句在框外,規則原文的反引號與反斜線照原字;代碼審 r7);附加段整體不超過 `_LENS_SPEC_TEXT_MAX`(12000)字——先按節點分配每篇合約行的字數(保住後面節點的標題、小計與殘留徽章),最後才在行界截斷並講明原本多少字,`--json` 的 `listed` 是文字裡實際印出的節點標題行數(含只列名的)、`shown` 是其中貼了內容的標題數,另給 `text_truncated`;目標架構段套同一個字數上限。
   - 為什麼只列確認存在的:現在設計審只列會談目錄裡 `is_file()` 為真的節點(提交寫法另列提交裡確認存在的),印出來的名字一定對應真實存在的檔;連結的抓法 `\[\[((?:Systems|Issues)/[^\]|#]+)` 會吃換行與任意長度,沒驗過存在就列名,等於讓計劃作者把任意文字塞進派工詞(違反 [[Systems/派工鏡頭]] 的零自由文字規矩)。名字怎麼印由上一條的出口管,所以 lumos 端不另抄 `_clean_field`。
   - 落點段(`_nodehome_landing_sizes`)套同一條規則:會談目錄有就照印大小;只在提交裡有就列名並標「只在那個提交裡,會談目錄還沒有這篇」;兩邊都沒有只印筆數「N 個落點在會談目錄與凍結提交裡都找不到(可能是要新開的節點或錯字)」;最多列 20 行,其餘「另有 M 篇落點沒列」。工作樹寫法的落點照現在印「還不存在(要新開)」。
   - 用詞一律是「會談目錄」,不寫「主線」(會談目錄不一定在 main 上)。工作樹寫法照現在只認會談目錄有的節點。
   - rc 照樣是 0。
7. **lumos 的輸出欄位與失敗代碼**:`--json` 的成功列與失敗列都帶 `spec_source`;提交寫法另帶 `spec_commit`(完整編號)與 `spec_blob`(blob 編號)。提交寫法成功時,附加段開頭加印「計劃來源:提交 <12碼> 的 <路徑>(blob <12碼>)」,席位拿得到跟 spec-freeze 那行對照的值。計劃沒提到程式檔、沒連結節點、也沒寫 `lands_in`(沒有任何固定席內容)時,照樣印這一行、rc 0,不印空輸出。
   - 計劃類失敗代碼共六個:新增五個 `spec_rev_missing`、`spec_missing`、`spec_outside_repo`、`spec_too_large`、`no_knowledge`(現在的工作樹那條路失敗只印 stderr、不印代碼),加上沿用範圍類既有的 `not_git`(會談目錄不在 git 專案裡;現在 `cmd_dispatch_lens_spec` 在這裡回 rc 2、不印代碼,跟舊裁定要消除的靜默同一族)。rc:`no_knowledge` 3,其餘 2,跟現在工作樹那條路的 rc 對齊。工作樹那條路對應:不在 git 專案 `not_git`、不在 repo 裡 `spec_outside_repo`、不存在或讀不到 `spec_missing`、沒有圖譜 `no_knowledge`;stderr 原文與 rc 不變。
   - 提交寫法不帶 `--json` 時,stderr 印一行「dispatch-lens:計劃讀不到(<代碼>)」,rc 同上。
   - lumos 端新增一份常數 `_LENS_FAIL_CODES`(十一個代碼:範圍六個、計劃新增五個,`not_git` 兩邊共用),`_dispatch_lens_fail` 只收這份裡的代碼,S11 拿它跟掛鉤比,不掃原始碼。`_dispatch_lens_fail` 加選填的附帶欄位(帶 `spec_source` 等),說明裡的種數從「六種」改成「十一種(範圍六種、計劃新增五種,`not_git` 兩邊共用)」;掛鉤的 `LENS_FAIL_REASONS` 加這五個代碼。
8. **掛鉤不判文法**:標記的找法照舊(`find_spec_marker`,`SPEC_RE` 不改),值原樣交給 lumos;掛鉤不依值的形狀分流、不跑 git(顯示時只切冒號前的十六進位,見 S35)。說明行與 note 只讀 lumos 回的 `spec_source`、`spec_commit`、`lens_fail`。
   - `_fail_note(r, rng, repo)` 改成 `_fail_note(r, rng, repo, spec=None)`:`rng` 有值照現在走範圍版(`FAIL_NOTE` 不動);`spec` 有值且 `lens_fail` 是計劃類代碼時,用新寫的計劃版 `SPEC_FAIL_NOTE`:「LUMOS-LENS:這次沒附固定席節點(計劃 {what} 在會談專案 {repo} 讀不到:{why})。……照派工詞審查即可。」`{what}` 原寫用 `_clean_field(spec)`——**2026-10-14 代碼審 r4 起被 `_spec_what` 取代**(冒號前是 7–64 碼十六進位時照印、冒號後過名字顯示規則,其他整段過名字顯示規則;r5 起顯示規則是 lumos 名字出口的抄本,帶值的那一句加注入框、工具寫死的指示放框外,見 S35);不用範圍專用的 `_SAFE_RANGE_RE`(計劃路徑一定不合它,會整句顯示成 `<範圍>`)。
   - `spec_source` 是 `worktree`、代碼是 `spec_missing` 或 `spec_outside_repo` 時加繞法(`SPEC_FREEZE_HINT`):「計劃在別的工作樹時,在那個工作樹跑 `lumos spec-freeze <計劃>`(不帶 --out,不在那裡留檔),把它印的那行 `LUMOS-SPEC:` 貼進派工詞」,快照回會談目錄用提交寫法凍(見 9)。兩個代碼都加:把別的工作樹裡的計劃寫成絕對路徑是最自然的寫法,它落在 `spec_outside_repo`。
   - `lens_fail` 是 `not_git` 且帶 `spec_source` 時也走計劃版,`{why}` 用 `LENS_FAIL_REASONS` 裡既有的那句。
   - **成功不記事件**:提交寫法與工作樹寫法成功都不呼叫 `_hookevent.mark`。只在失敗時照既有慣例記(`_hookevent.mark`「只在吞掉逾時或失敗時呼叫」),所以不碰 [[Projects/派工鏡頭注入_計劃]]「不擋不驗不記不量」那筆決策,`_hookevent.py` 檔頭不改。用量改數派工單(見 RETIRE-IF)。
   - 失敗的 note 一律是 `spec_<spec_source> <代碼>`(`spec_commit spec_rev_missing`、`spec_worktree spec_missing`…)。kind:提交寫法的所有計劃類代碼(含 `no_knowledge`:提交寫法下多半是 slug 打錯或分支錯位)與工作樹寫法的 `spec_missing`、`spec_outside_repo` 記 `ok`——使用者輸入錯不是掛鉤壞掉,記成 `error` 會拉高 enforcement 的錯誤數、蓋過真的掛鉤錯誤;工作樹寫法的 `no_knowledge` 與兩種寫法的 `not_git` 照現在記 `error`。逾時照現在記 `timeout` 與逾時句,這筆不帶字首。
   - note 字首是固定字彙,不當成讀端可解析的欄位(回退第 5 步 grep 確認沒有讀端解析)。
   - 掛鉤檔頭「其餘判斷全在 lumos 端」照舊成立,補一句「計劃寫法也由 lumos 判,掛鉤只讀 `spec_source`」。
9. **新子命令 `lumos spec-freeze <計劃> [--out governance/review-reports/<編號>/rN-snapshot.md]`**:在工作目錄(計劃所在的工作樹)建一個不掛分支的提交,有給 `--out` 就從這個提交寫出凍結快照,印出要貼的一行 `LUMOS-SPEC: <完整提交編號>:<路徑>`(`--json` 另給 `spec_commit`、`spec_blob`、路徑)。快照與提交因此一定一致,也不必先正式提交草稿(正式提交會撞上提交前檢查、錨點簽名,還會多出要壓掉的半成品提交)。
   - **兩種寫法**:計劃在會談目錄時,一次 `lumos spec-freeze <計劃> --out governance/review-reports/<編號>/rN-snapshot.md`。計劃在別的工作樹時分兩步:在那個工作樹跑 `lumos spec-freeze <計劃>`(不帶 `--out`:只建提交、印那一行,不在那個工作樹留任何檔——它可能是別的會談的工作目錄);再回會談目錄跑 `lumos spec-freeze <完整提交編號>:<路徑> --out governance/review-reports/<編號>/rN-snapshot.md`,從共用物件庫讀那個提交裡的計劃寫出快照、印同一行,不建新提交。提交寫法的檢查跟 dispatch-lens 的提交寫法同一套(編號只收完整 40/64 碼而且解出等於輸入,否則 `spec_rev_missing`;路徑字串 `spec_outside_repo`;非 NFC、不是一般檔或讀不到 `spec_missing`;超過 1MB `spec_too_large`),之後才驗 `--out`。
   - **`--out` 只收執行所在 repo 的 `governance/review-reports/` 底下**(底下至少還有一段):照字面接成絕對路徑、去掉 `.` 與 `..` 後找出等於 repo 根的那一段,它底下要以 `governance/review-reports/` 開頭、不准有 `.git` 段(大小寫不拘)、已存在的每一段上層都要是資料夾而且不是符號連結;不合回 `out_outside_repo`(`.lumos/`、`.claude/settings.json`、repo 外、`.git` 底下都在這裡擋)。逐段檢查跟第 3 步計劃路徑的逐段 lstat 共用一支。卷證、收貨與記帳都在會談目錄,快照就直接寫在那裡,不用再複製。
   - **檢查順序(照編號做,同時違反時回第一個違反的代碼;全部 rc 2,`--json` 印 `{"freeze_fail": <代碼>}`,stderr 印一行說明)**:
     1. 形狀:工作目錄在 git 專案裡(否則 `not_git`);HEAD 解得到提交(否則 `no_head`)。
     2. 路徑字串:輸入先轉成相對於 repo 根——絕對路徑必須以 `rev-parse --show-toplevel` 的字串加 `/` 開頭,去掉這段前綴;相對路徑接在 `rev-parse --show-prefix`(目前目錄相對於 repo 根的前綴)後面。兩種都不做正規化,轉完再套第 2 條的路徑規則與空白規則;前綴不合或規則不合回 `spec_outside_repo`(macOS `/tmp` 對 `/private/tmp` 這類連結前綴會不合,stderr 提示改用相對路徑)。
     3. lstat:從 repo 根往下,路徑的每一段都用 `os.lstat` 判,任何一段是符號連結就拒絕;最終檔用 lstat 判是一般檔(`stat.S_ISREG`);`resolve()` 之後必須在 repo 根(也 `resolve()`)底下。不合都回 `spec_missing`。不用 `Path.is_file()`:它與 `hash-object` 都會跟著符號連結走,會把 repo 外的檔凍進物件庫與快照(第四輪兩席實測讀到 `/etc/hosts`)。
     4. 大小:lstat 的大小大於 1048576 回 `spec_too_large`。在建任何物件之前判,不留懸空物件,也不會印出一行貼了之後每席都回 `spec_too_large` 的 `LUMOS-SPEC:`。
     5. `--out`(有給才驗):位置不合回 `out_outside_repo`(規則見上);已存在而且位元組與工作樹上的計劃不同(或不是一般檔)就拒絕,回 `out_conflict`;位元組相同視為重建同一份,照常做下去、照常印那一行。理由:重派或 gc 後重跑時,工作樹上的計劃常已折進修正,覆寫會讓同一輪出現兩個 blob、兩份快照,先前各席的 quote-check 全對不上。要凍新的一輪就換新的 `--out`。
     6. 建提交:見下一點。任何一步的 git 回 None 或 rc 非 0 回 `git_failed`(可能已留下懸空物件,gc 會清)。
   - 建提交的步驟:在暫存目錄開一份 index,用 `GIT_INDEX_FILE` 指向它:`read-tree HEAD` 起、`hash-object -w --no-filters <計劃>` 放進這份計劃的工作樹內容(不跑過濾器,內容與工作樹位元組相同)、`update-index --add --cacheinfo <mode>,<blob>,<路徑>`(`<mode>`:lstat 的擁有者執行位元有設是 100755,沒設是 100644)、`write-tree`、`commit-tree <tree> -p HEAD -m "lumos spec-freeze"`;作者與提交者用固定的環境變數(`GIT_AUTHOR_NAME`/`GIT_COMMITTER_NAME` 等設成 `lumos spec-freeze`),不讀使用者設定。最後用第 3 條同一支讀法從這個提交讀出計劃,原子寫進 `--out`(暫存→`os.replace`),刪掉暫存 index。
   - **每個 git 呼叫都加 `-c core.hooksPath=/dev/null -c core.fsmonitor=false`**:指向暫存 index 時 `read-tree` 與 `update-index` 會跑 `post-index-change` 掛鉤(第四輪邊界席實測記號寫了三次),`core.fsmonitor` 也會執行外部程式;`commit-tree` 本身不跑提交掛鉤、不吃 `commit.gpgsign`(第四輪三席實測)。git 呼叫一律走 `_lens_git`:擴充它加 `env=None` 參數(跟 `os.environ` 合併後傳給子行程),用來傳 `GIT_INDEX_FILE` 與固定作者;兩個 `-c` 放在 args 最前面。不另寫 `subprocess.run`,也不另開一支寫入用的包裝。
   - **這是 lumos 第一個寫 git 物件的子命令**,而且刻意落懸空物件,跟 `_replay_git_blob`「只引用已被 tree 引用的物件(取 HEAD 的 blob),不用 `hash-object -w` 落兩週會被 gc 的懸空 blob」取向相反。理由:replay 的凍結要長期回放,設計迴圈只活一晚;要長期回放的東西不用 spec-freeze。
   - 不動任何 ref、真的 index 與分支;工作樹裡其他沒提交的改動不進這個提交(tree 只比 HEAD 多這份計劃)。
   - 拒絕時不建提交、不寫 `--out`(第 1–5 步都在建物件之前)。失敗代碼登記在 `_SPEC_FREEZE_FAIL_CODES`(九個:`not_git`、`no_head`、`spec_rev_missing`、`spec_outside_repo`、`spec_missing`、`spec_too_large`、`out_outside_repo`、`out_conflict`、`git_failed`)。路徑含空白要擋,是因為標記文法 `\S+` 不收空白,產出的那行會被掛鉤整行略過。
   - 全域 lumos 不同支就警告:跑時用掛鉤 `_trusted_lumos` 同一套找法(PATH 上的 `lumos`、其次 `$LUMOS_HOME`、其次 `~/harness/lumos-toolchain`,同樣的擁有者與權限檢查)找出全域那支,`resolve()` 後跟自己這支檔不是同一支,就在 stderr 印一行「這支 lumos 不是掛鉤會叫的那支(<路徑>),那支若是舊版,貼上的提交寫法會被當成工作樹路徑、靜默不附」,照常完成、rc 0。專案的 CLAUDE.md 教人敲 `python3.14 scripts/lumos`,最容易踩到這條。
   - 不掛 ref 的物件在預設 gc 兩週後才會清(`gc.pruneExpire` 預設 2.weeks.ago),設計迴圈一晚跑完,窗口夠用。
   - 派工單 rN-dispatch.json 多記 `spec_commit`(編排者照範本寫);RETIRE-IF 與 REVISIT 數的就是這個。
10. **範本只叫人用 spec-freeze,以及版本錯開**:三份手冊(SKILL.md、templates.md、reference.md)統一寫「設計審派工前先 spec-freeze;席位材料、rN-snapshot、--reviewed 都用它產生的那份;派工單記 spec_commit」,怎麼凍照 9 的兩種寫法;不另外複製工作副本、不對計劃真檔算指紋(第 2 步修過真檔後副本就舊了)。不叫人手寫提交編號。
   - spec-freeze 與掛鉤叫的都是全域那支 lumos(掛鉤用 `_trusted_lumos`:PATH 上的 `lumos`、其次 `$LUMOS_HOME`、其次 `~/harness/lumos-toolchain`;編排者在終端敲的 `lumos` 也是 PATH 那支),所以產得出那一行,就代表全域 lumos 認得這個寫法。範本寫 `lumos spec-freeze`,不寫 `python3.14 scripts/lumos`。
   - 舊掛鉤配新 lumos:提交寫法照常能用,只少失敗說明行與 note(舊 `_fail_note` 在沒有範圍時直接回空,`LENS_FAIL_REASONS` 也不認新代碼),不報錯(S19 守)。
   - 新掛鉤或新範本配舊 lumos:舊 lumos 沒有 `spec-freeze`,編排者敲下去當場看到錯誤,照舊寫工作樹路徑;新掛鉤收到舊 lumos 的失敗(stdout 空、rc 2)不附說明行、不丟例外(S20 守)。
   - Codex 編排時派工訊息對掛鉤是密文,設計審本來就拿不到鏡頭(`--arm` 只收代碼審範圍);範本那一行標明「提交編號寫法只對 Claude 編排有效」,[[Systems/codex-harness]] 的天生限制那段補一句。
11. **要一起改的說法(列全)**:
   - `skills/lumos-design-loop/SKILL.md` 派工步驟裡 `LUMOS-SPEC: <計劃筆記.md>` 那句;
   - `skills/lumos-design-loop/reference.md` 講設計審鏡頭從工作樹讀的那段;
   - `skills/lumos-design-loop/templates.md` 兩處:§1 審計員那行與 §7.6 架構席那格;
   - `skills/lumos-project-notes/reference.md` 的指令表裡 dispatch-lens 那格;
   - `skills/lumos-project-notes/commands/05-設計審查迴圈.md` 的指令表;
   - [[Systems/design-loop]] 講 `LUMOS-SPEC` 落點那段;
   - `scripts/lumos` 的 `--spec` 參數說明(現在寫「從工作樹讀」)與 `cmd_dispatch_lens_spec` 的 docstring;新子命令要通過 `t_every_subcommand_has_when`(`lumos spec-freeze --help` 第一段要有「什麼時候用:」),在說明對照 `HELP_WHEN` 補一筆 `spec-freeze`;
   - `spec-freeze` 的說明寫進 [[Systems/派工鏡頭]](它管 `scripts/lumos` 的派工鏡頭那段),實作時用 `lumos set Systems/派工鏡頭 responsibility "…"` 把負責範圍擴寫成也管「設計審用的凍結提交與快照(`spec-freeze`)」,不手改開頭欄位;
   - 掛鉤 `dispatch-lens-hook.py` 的檔頭與新的 `SPEC_FAIL_NOTE`;
   - [[Systems/codex-harness]] 逐一列舉 `lens_fail` 代碼的那行 WHY(六個改成十一個)。
   - `skills/lumos-project-notes/commands/06-代碼審與推送.md` 只講代碼審,不用改。
12. **不做**:不讓派工詞指定任意路徑或別的 repo(舊裁定照舊成立);不改 `LUMOS-IMPACT:` 的寫法;不收短編號、分支名或 `HEAD~1` 這類寫法;不讀工作樹裡沒凍結的改動;不改 `SPEC_RE`(路徑不可含空白,spec-freeze 先擋)。Codex 編排的 `--arm` 不在範圍內。

## 驗收條款

lumos 層(直接跑被測 repo 的 `scripts/lumos dispatch-lens --spec`;S2–S4、S10 一律帶 `--json`,同時斷言 `lens_fail` 與 rc):

- [S1] 當 `--spec` 是 `<完整提交編號>:docs/x-knowledge/Projects/a_計劃.md`、那份計劃只在另一個工作樹的那個提交裡、計劃提到的程式檔與連結節點在會談目錄都有時,lumos 應回 rc 0、附上那些固定席節點,`--json` 應帶 `spec_source: commit`、`spec_commit`(等於輸入)與 `spec_blob`,附加段開頭應印提交與 blob 的前 12 碼;計劃沒有任何固定席內容(沒提程式檔、沒連結、沒 `lands_in`)時,仍應 rc 0 並印「計劃來源:提交 <12碼>」那一行。[test:t_dispatch_lens_spec_commit_from_other_worktree]
- [S2] 當提交寫法的編號不是 40 或 64 碼(例如 7 碼短編號,即使 git 解得到;超過 64 碼的十六進位)、是不存在的 40 碼、或在 SHA-1 repo 寫 64 碼時,lumos 應回 `spec_rev_missing`、rc 2、不附任何節點;冒號前恰好 6 碼十六進位時應照工作樹路徑處理(`spec_source: worktree`),恰好 7 碼時應是提交寫法;全大寫與大小寫混用的 40 碼應照常成功;git 支援 `--object-format=sha256` 時,在 SHA-256 repo 寫 64 碼完整編號應照常成功,不支援就跳過並印跳過原因。[test:t_dispatch_lens_spec_commit_shape]
- [S3] 當提交寫法的路徑是空字串、以 `/` 開頭、含 `.` 段、`..` 段、空段、結尾 `/`(`docs/x-knowledge/`)、反斜線、任一種 `str.isspace()` 為真的字元(半形空白、tab、U+3000、NBSP 各一筆)、只有兩段(`docs/x-knowledge`)、空 slug(`docs/-knowledge/…`)、大小寫不合(`Docs/…`、`docs/x-Knowledge/…`)時,lumos 應回 `spec_outside_repo`;slug 在會談工作樹的 `docs/` 沒有名字正好相同的目錄時應回 `no_knowledge`、rc 3;路徑是 NFD 時應回 `spec_missing`;檔名含第二個冒號時應以第一個冒號切開照常讀到;同時違反兩條時應回做法 2 檢查順序裡較前的代碼(短編號加壞路徑回 `spec_rev_missing`;合規路徑、slug 不存在、提交裡也沒有這個檔回 `no_knowledge`)。[test:t_dispatch_lens_spec_commit_path_rules]
- [S4] 當提交寫法的路徑在那個提交裡是目錄、符號連結或子模組時,lumos 應回 `spec_missing`;大小是 1048577 位元組時應回 `spec_too_large`;剛好 1048576 位元組時應照常讀;計劃含 NUL 與非 UTF-8 位元組時應照常讀、rc 0。[test:t_dispatch_lens_spec_commit_regular_blob_only]
- [S5] 當 repo 有 `a-knowledge` 與 `b-knowledge` 兩個 vault、提交寫法的計劃在 `b-knowledge` 時,連結節點、落點與 `--arch-target` 目標架構段的節點都應到 `b-knowledge` 找,不到 `a-knowledge`。[test:t_dispatch_lens_spec_commit_vault_from_path]
- [S6] 當計劃提到的程式檔只在那個提交裡、會談目錄沒有時,輸出應列「只在提交 <12碼> 裡、會談目錄沒有,沒算牽連」那一行,不應對它跑 impact,也不應出現「沒牽到任何家、合約或事故的節點」;計劃同時提到 `scripts/../../x` 與一個中文檔名的只在提交裡的檔時,那一行仍應列出中文檔名那個。[test:t_dispatch_lens_spec_commit_file_only_in_commit]
- [S7] 當計劃連到五篇節點(會談目錄有、只在那個提交裡有、只在那個提交裡有而名字含反引號、名字含換行、兩邊都沒有)時,第一篇應附內容,第二篇應只列名並標「只在那個提交裡,會談目錄還沒有這篇」,第三篇應照列、反引號跳脫成 `\u0060`,第四篇不應出現名字、只計入「連結寫法不合或指到圖譜外面」,第五篇不應出現名字、只出現「1 個連結在會談目錄與凍結提交裡都找不到」那句,rc 應是 0;`lands_in` 寫同樣的節點時落點段應照同一條規則分開。[test:t_dispatch_lens_spec_commit_linked_three_kinds]
- [S8] 當提交寫法帶 `--arch-target`、計劃提到一個只在那個提交裡寫到的路徑時,目標架構段應照提交裡的計劃文字算出、不應靜默變空。[test:t_dispatch_lens_spec_commit_arch_text]
- [S9] 讀提交裡的計劃時,lumos(含 impact 子行程與目標架構段)應只在會談 repo 跑 git。搭法:先用 `shutil.which("git")` 取真 git 的絕對路徑,在暫存目錄寫一支 `#!/bin/sh` 的假 `git`(把 `-C` 值、目前工作目錄與 `GIT_DIR` 記一行到紀錄檔,再 `exec` 真 git 的絕對路徑),把暫存目錄前置進 PATH,並把這份 PATH 傳給子行程(用子行程跑 `scripts/lumos dispatch-lens`,不在行程內呼叫,impact 子行程才會繼承)。斷言:rc 0、輸出含預期的固定席節點、紀錄至少有 `rev-parse`、`ls-tree`、`cat-file` 各一筆,而且每一筆以 `-C`、工作目錄、`GIT_DIR` 解析後的位置都在會談 repo 根底下,沒有一筆落在計劃所在的另一個工作樹(只斷言「零筆違規」在實作前就是綠的)。[test:t_dispatch_lens_spec_commit_git_only_in_session]
- [S10] 當值是工作樹路徑時,檢查應與現在相同(絕對路徑、不在 `docs/*-knowledge/` 底下的計劃、超過 1MB 的計劃都照讀,rc 與 stderr 不變),失敗時 `--json` 應多印 `lens_fail`(`spec_missing`、`spec_outside_repo`、`no_knowledge` 或 `not_git`)與 `spec_source: worktree`;會談目錄不在 git 專案時,兩種寫法都應回 `not_git`、rc 2。[test:t_dispatch_lens_spec_worktree_unchanged_plus_code]
- [S11] lumos 的 `_LENS_FAIL_CODES` 應等於掛鉤 `LENS_FAIL_REASONS` 的鍵集合(十一個)。[test:t_dispatch_lens_fail_codes_match_hook]

掛鉤層(照既有 `fire()` 替換 `subprocess.run`,回假的 lumos JSON;夾具的計劃路徑不含「範圍」兩字):

- [S12] 當 lumos 回提交寫法成功列時,掛鉤不應呼叫 `_hookevent.mark`(成功不記事件);掛鉤應只呼叫一次 lumos、把標記值原樣傳過去,不應呼叫 git。[test:t_dispatch_lens_hook_spec_commit_event]
- [S13] 當 lumos 回 `spec_source: worktree` 與 `spec_missing` 或 `spec_outside_repo` 時,說明行應用計劃版措辭、帶 spec-freeze 繞法:別的工作樹那一步寫 `lumos spec-freeze <計劃>` 而且寫明不帶 `--out`,快照回會談目錄用 `lumos spec-freeze <完整提交編號>:<路徑> --out governance/review-reports/<編號>/rN-snapshot.md` 寫,不應有舊的單步帶 `--out` 寫法,也不應出現「範圍」或 `<範圍>`;事件應記 kind `ok`、note `spec_worktree <代碼>`;回 `spec_source: worktree` 與 `no_knowledge` 時應記 kind `error`、note `spec_worktree no_knowledge`。[test:t_dispatch_lens_hook_spec_worktree_fail_notice]
- [S14] 當 lumos 回 `spec_source: commit` 與 `spec_rev_missing`、`spec_missing`、`spec_outside_repo`、`spec_too_large`、`no_knowledge` 任一個時,說明行應用計劃版措辭、不帶繞法,事件應記 kind `ok`、note `spec_commit <代碼>`;回 `not_git` 時應記 kind `error`;逾時那筆應記 `timeout`、note 不帶 `spec_` 字首。[test:t_dispatch_lens_hook_spec_commit_fail_notice]
- [S19] 拿本計劃實作前的掛鉤(`git show <實作前的提交>:scripts/hooks/claude/dispatch-lens-hook.py` 寫進暫存檔)收新 lumos 的提交寫法成功列與每一種計劃類失敗列時,掛鉤應 rc 0、成功列照附內容、失敗列不附說明行、不丟例外。[test:t_dispatch_lens_hook_old_with_new_lumos]
- [S20] 新掛鉤收到舊 lumos 的回應(stdout 空、rc 2,沒有 `spec_source`)時,應 rc 0、不附說明行、不記 `spec_` 字首的 note、不丟例外。[test:t_dispatch_lens_hook_new_with_old_lumos]

`lumos spec-freeze`:

- [S15] 跑完之後,`--out` 的內容應與那個提交裡那份計劃的 blob 位元組相同,也與工作樹上的計劃位元組相同;印出的那一行應等於 `LUMOS-SPEC: <提交>:<路徑>`;那個提交的父提交應是 HEAD;把那一行餵給 dispatch-lens 時回的 `spec_blob` 應等於快照的 blob 編號;計劃路徑用絕對路徑或在子目錄用相對於目前目錄的路徑給時,結果應與用相對於 repo 根的路徑給時相同。[test:t_spec_freeze_snapshot_matches_commit]
- [S16] 跑前跑後,`for-each-ref` 的輸出、真的 index 檔位元組(路徑用 `rev-parse --git-path index` 取,工作樹裡是 `.git/worktrees/<名>/index`)、HEAD 與目前分支都應不變;前後兩次量之間只准跑唯讀、不刷新 index 的指令(不跑 `git status`);工作樹裡另一個沒提交的改動不應進那個提交(tree 只比 HEAD 多這份計劃)。[test:t_spec_freeze_leaves_refs_and_index]
- [S17] 當 repo 裝了會留記號的 pre-commit、commit-msg、post-commit、post-index-change 掛鉤與會留記號的 clean 過濾器時,跑完之後記號都不應存在。[test:t_spec_freeze_runs_no_hooks_or_filters]
- [S18] 當計劃路徑含空白、不合路徑規則、本身是符號連結、中間某段目錄是符號連結、是目錄、大小 1048577 位元組,或 repo 沒有 HEAD 時,spec-freeze 應回 rc 2 與做法 9 檢查順序裡對應的代碼、不寫 `--out`,而且 `git cat-file --batch-all-objects --batch-check` 列出的物件清單前後相同(不數 `rev-list --all`:不掛 ref 的提交不在裡面,數了永遠綠)。[test:t_spec_freeze_rejects_bad_path]
- [S21] 當 `--out` 已存在而且內容跟工作樹上的計劃不同時,spec-freeze 應回 rc 2、`out_conflict`、`--out` 位元組不變、物件清單前後相同;內容相同時應 rc 0、照常印那一行。[test:t_spec_freeze_refuses_overwrite_frozen_snapshot]
- [S22] 當 PATH 上的 `lumos` 指到另一支檔時,spec-freeze 應在 stderr 印「不是掛鉤會叫的那支」那一行、仍 rc 0;指到自己時不印。[test:t_spec_freeze_warns_untrusted_self]
- [S23] 當 `--out` 在 repo 外、上層某段是符號連結、用 `..` 繞出 repo,或在 `.git` 底下時,spec-freeze 應回 rc 2 與 `out_outside_repo`、目標位置不出現新檔、物件清單前後相同;`governance/review-reports/` 底下還不存在的多層目錄應照建、rc 0。[test:t_spec_freeze_out_must_stay_in_repo]
- [S24] 當計劃在另一個工作樹時,在那裡不帶 `--out` 跑 spec-freeze 應 rc 0、印 `LUMOS-SPEC:` 那一行、那個工作樹 `git status` 不多檔;在會談目錄用那一行的 `<完整提交編號>:<路徑>` 帶 `--out governance/review-reports/x/r1-snapshot.md` 跑應 rc 0、快照位元組等於草稿、印同一行;短編號回 `spec_rev_missing`、路徑不合規則回 `spec_outside_repo`、提交裡沒有這個檔回 `spec_missing`。`--out` 是 `.lumos/evil.json`、`.claude/settings.json`、`.GIT/info/attributes`、`governance/review-reports/a/.Git/x` 時兩種寫法都應回 `out_outside_repo`;`--out` 是 `governance/review-reports-x/…` 或 `Governance/Review-Reports/…`(前綴照整段、照字面比)時也一樣。[test:t_spec_freeze_commit_form_from_session] [test:t_spec_freeze_out_only_review_reports] [test:t_spec_freeze_out_prefix_exact_segments]

代碼審 r3–r8 補的條款(這幾輪新加的行為與守衛;之前只在 Systems/派工鏡頭 的 PITFALL 綁測試):

- [S25] 當提交寫法的編號是物件庫沒有的 40 碼、40 碼的附註標籤物件(解出的提交編號不等於輸入),或 git 那邊把縮寫原樣解回來時,dispatch-lens 與 spec-freeze 都應回 `spec_rev_missing`。[test:t_spec_freeze_commit_rev_full_and_resolves]
- [S26] 五份手冊(設計迴圈的 SKILL.md、templates.md、reference.md,project-notes 的 commands/05、reference.md)都應寫「設計審派工前先 spec-freeze;……派工單記 spec_commit」那句、`--out` 放 `governance/review-reports/` 與會談目錄的提交寫法,「別的工作樹」那一步不帶 `--out`;這五份加上 `lumos --help` 的 spec-freeze 說明,都不應有舊的單步寫法(spec-freeze 帶 `--out` 指到快照、計劃不是提交寫法、那一句不是講計劃在會談目錄時),不論佔位寫成角括號、大括號或直接檔名。[test:t_design_loop_manuals_spec_freeze_wording] [test:t_design_loop_manuals_spec_freeze_old_step_any_placeholder]
- [S27] 文件守衛檢查這幾項,拿掉任一項應紅:計劃做法 9 寫了 `out_outside_repo` 與 `--out` 放哪、有條款綁 `t_spec_freeze_out_must_stay_in_repo`;計劃與 [[Systems/派工鏡頭]] 沒有「代碼審 rN 修正」這類輪次標題(守衛只認三個寫死的字樣,清單在 `_lr2_notes_problems`;其他輪次敘述不在檢查範圍);[[Systems/lumos-cli-lifecycle]] 有入口清 git 環境那行(帶代價、綁測試);[[Systems/派工鏡頭]] 有 `_vault_node_path`、`_vault_node_read`、`_lens_author_name_show`、讀不讀只看路徑安全、端到端守衛、無標點整句仍印得出、每類上限、目標架構段兩條路都經出口、字數上限先按節點分配、看不見只有一份判定、目標架構段分配含標題行、反引號路徑不回溯、整段總量上限、正文保留表情符號序列、必答指示一定附各一條守則行(帶指定的綁定測試)與名字防線的 REVISIT 行;[[Systems/codex-harness]] 有 `spec_source` 與 `_spec_what` 兩條守則行;S25 起的條款綁齊這幾輪新加的每支測試(清單 `_LR4_CLAUSE_TESTS` 寫在測試裡);S13 寫齊三個關鍵寫法;做法 5 寫批次並標明取代;做法 6 寫「名字一律以資料形式印」與「整句英文或中文指令仍印得出」;做法 8 標明被 `_spec_what` 取代;計劃有名字防線的 REVISIT 行。變異照實是這些:清單裡每支測試各拿掉一次綁它的條款、S13 三個寫法各改一次、三個輪次字樣各加回一次、lifecycle 那行拿掉代價、做法 5/6/8 各改一次、兩條 REVISIT 與 codex-harness 的 `_spec_what` 那行各拿掉一次、`_LR5_LENS_WANT` 列的每條派工鏡頭守則行各拿掉一次、加回承認句(`t_lens_repo_notes_r4_clauses_and_limits`);做法 9 的 `out_outside_repo` 改掉一次、拿掉綁 `t_spec_freeze_out_must_stay_in_repo` 的條款、派工鏡頭的 `_vault_node_path`、`_vault_node_read`、`_lens_author_name_show` 三條守則行各拿掉一次、codex-harness 拿掉 `spec_source` 那行(`t_lens_repo_notes_spec_freeze_and_entry`)。只看這些字樣與綁定在不在,不檢查條款文字與測試斷言對不對得上(那由各條綁的測試自己守)。[test:t_lens_repo_notes_spec_freeze_and_entry] [test:t_lens_repo_notes_r4_clauses_and_limits]
- [S28] 當提交寫法的計劃提到超過 5000 個程式檔與節點時,「提交裡有沒有」應只問前 5000 個(連結與落點排前面),印「只算到一半」、`--json` 的 `scan_truncated` 與 `cands_truncated` 為真,沒問到的不應算成找不到;剛好 5000 個不截斷、5001 個才截斷,重複與 NFC/NFD 兩種寫法的同一個名字不佔名額。[test:t_dispatch_lens_spec_commit_cands_capped] [test:t_dispatch_lens_spec_commit_cands_cap_exact]
- [S29] 當提交本身把檔名存成 NFD 時,計劃寫 NFC 或 NFD 都應查得到;計劃同時用 NFC 與 NFD 兩種寫法連同一篇節點、提同一支程式檔時,都只應列一次。[test:t_dispatch_lens_spec_commit_stored_nfd_found] [test:t_dispatch_lens_spec_nfc_nfd_listed_once]
- [S30] 當固定席節點是指到圖譜外的捷徑檔,或整個圖譜資料夾是符號連結時,外面那篇的內容不應進派工詞,只計數;圖譜資料夾本身或上層是符號連結時,附加段應另印「圖譜資料夾本身或上層是符號連結」那一行(不是只寫「指到圖譜外面」);工作樹寫法的計劃所在 repo 唯一的 `*-knowledge` 是符號連結時,應回 `no_knowledge`、stderr 講明是符號連結。[test:t_dispatch_lens_spec_pinned_node_symlink_not_read] [test:t_dispatch_lens_spec_vault_dir_symlink_pinned_not_read]
- [S31] 作者寫得到的名字(計劃路徑、連結與落點的節點名、計劃提到的程式檔名——含「只在提交裡」那行、找得到那行、太泛與超預算、固定席的牽連檔——與目標架構宣告的節點名和檔名)印進派工詞時,每一次出現都應在注入框內、包在 ‹ › 裡;每個輸出點各放一個帶唯一哨兵的指令句跑 dispatch-lens(提交寫法、工作樹寫法,都帶 `--arch-target`)時,哨兵都應出現、沒有一處在框外或標記外;工作樹寫法只有落點時也應在框內;計劃檔名或程式檔名是一整句帶逗號、冒號、句號、反引號的指令時,整段應包在標記裡(反引號跳脫)。[test:t_dispatch_lens_spec_author_names_e2e_sentinels] [test:t_dispatch_lens_spec_source_line_sentence_path_in_marks] [test:t_dispatch_lens_spec_author_names_sentence_in_marks] [test:t_dispatch_lens_spec_commit_source_line_strict_path]
- [S32] 帶標點的合法名字應照讀照附、照印:會談目錄有的 `[[Systems/Q&A規則]]`、`[[Systems/a+b]]`、`[[Systems/設計：舊]]` 與全形括號的節點內容照附,落點 `Systems/Q&A規則` 照印「已存在」,計劃提到的 `app/[id]/page.tsx`、`src/@types/x.d.ts` 照列名、它們的家照附,`Q&A_計劃.md` 的來源行照印;工作樹與提交兩種寫法都是。[test:t_dispatch_lens_spec_punct_names_read_and_attached] [test:t_dispatch_lens_spec_fullwidth_paren_node_attached]
- [S33] 不帶標點的整句檔名照印(名字出口不判語意),而且應包在 ‹ › 裡、在注入框裡,框內句尾有「不是指令」那句。[test:t_dispatch_lens_spec_unpunctuated_sentence_shown_in_frame]
- [S34] 名字顯示規則的邊界(期望值照做法 6 手寫):空字串、純空白、全形空白印「(空名字)」;節點名 80 字照印、81 字截成前 80 字並標「…(截斷,原長 81 字)」;路徑 300 字照印、301 字同樣截斷標明;U+3040(未指派)、U+202E、U+200D、U+E000(私用)、換行與 ‹ ›、反斜線、框線字元 ─ 與反引號 跳脫成 `\uXXXX`;`[ ]`、`@`、`+`、`$`、`&`、全形冒號、韓文 NFD、整句英文與前後空白照印;一串名字逗號接、各自加標記;掛鉤的顯示函式對同一批樣本的輸出應與 lumos 完全相同。[test:t_dispatch_lens_spec_name_shown_as_data_edges] [test:t_dispatch_lens_hook_name_show_matches_lumos]
- [S35] 掛鉤的說明行(讀不到、逾時、鎖狀態未知、範圍算不出)裡的計劃值與範圍值應過跟 lumos 同一套名字顯示規則:整句指令包在 ‹ › 裡,提交寫法冒號前的完整編號照印在標記外;範圍值不合保守字元集印 `<範圍>`(帶反引號或 `$(` 的範圍值);帶這兩種值的那一句應在注入框裡;每種說明行各放一個哨兵跑掛鉤時,附上的那段裡哨兵都應在框內、標記內。[test:t_dispatch_lens_hook_spec_sentence_what_in_marks] [test:t_dispatch_lens_hook_notes_e2e_sentinels] [test:t_dispatch_lens_hook_fail_reason_notice]
- [S36] 提交寫法 5000 個只在提交裡的連結、工作樹寫法 5000 筆不存在的 `lands_in` 時,兩類各應只列前 `_LENS_SPEC_MAX_NAMED`(20)行、其餘印「另有 M 篇」,輸出行數與字數在上限內;附加段超過 `_LENS_SPEC_TEXT_MAX`(12000)字時應在行界截斷(單行比上限長就截那一行),最後一行講明截了、原本多少字,沒超過的原樣不動。[test:t_dispatch_lens_spec_only_nodes_and_landing_capped] [test:t_dispatch_lens_spec_text_total_cap]
- [S37] 計劃先寫 NFD、後寫 NFC,磁碟上是 NFC 時(用「位元組完全相同才算存在」模擬正規化敏感的檔案系統),連結節點與程式檔都應找到、各只列一次;真的跑一次工作樹寫法時,韓文 NFD 先出現的連結節點內容照附。[test:t_dispatch_lens_spec_nfd_first_nfc_on_disk_found]
- [S38] 代碼審那條路(`dispatch-lens <範圍> --arch-target`)的目標架構段跟設計審那條同一套:被審分支改到的檔名、分叉點版宣告的節點名與規則原文經名字出口、整段在注入框裡;四種行(讀不到規則照鄰居審、貼規則的標題、…另有幾條、節點太多只列名)各放一個哨兵跑真的子行程時,`arch_text` 與併進 `text` 的那段裡哨兵都應在框內、配好的標記內。[test:t_dispatch_lens_arch_target_code_path_e2e_sentinels] [test:t_arch_target_dispatch_lens_attaches_rules]
- [S39] 設計審的 7 處輸出點(找得到的程式檔那行兩個分支的「超預算沒算」、第一個分支的「太泛不列」、「(超出上限,只列名)」、目標架構段的「…另有 N 條」、「節點太多,規則沒貼」、「讀不到規則…照鄰居審」)各放一個哨兵時,都應在框內、配好的標記內;標記照順序配對,同一行兩個名字之間的裸印、落單的 ‹ 或 ›、跨行的 ‹ 都算問題。[test:t_dispatch_lens_spec_sentinels_every_output_point] [test:t_dispatch_lens_sentinel_marks_paired]
- [S40] 目標架構段有總量上限:3000 個目標節點時「節點太多」列名行只列 `_ARCH_TARGET_LENS_NAMED`(20)行、其餘「另有 M 個」;名字長到放不下時,放不下的列名行併進「另有 M 個目標節點沒列名」、整段仍在 `_LENS_SPEC_TEXT_MAX` 字內;規則原文每條截在 `_ARCH_TARGET_RULE_SHOW`(200)字並標原長,每篇照分配(分配含標題行,見 S47)、三個節點的標題都在;比對最多拿 `_ARCH_TARGET_LENS_FILES_MAX`(2000)支檔、用前 `_ARCH_TARGET_LENS_DECLS_MAX`(500)條宣告、吃 `_ARCH_TARGET_LENS_BUDGET`(5)秒預算,超過照實印「只算到一半」(沒有命中也印);推送前分級那條不帶上限、照舊全算。[test:t_arch_target_text_total_capped] [test:t_arch_target_lens_split_budget_and_caps]
- [S41] 名字出口與掛鉤抄本另跳脫看不見的字(代碼審 r7 起照 S45 的同一份判定;r6 原本手列的變體選擇符 U+FE00–FE0F、U+E0100–E01EF、U+034F、U+17B4–17B5、U+180B–180F 與填充字 U+115F、U+1160、U+3164、U+FFA0、U+2800 都在那份判定裡),超出基本平面的跳成 8 碼 `\UXXXXXXXX`(跟「U+E004 加 1」分得開),只由隱形字與空白組成的名字印「(空名字)」;兩邊對同一批樣本(含 Zl、Zp、Cs、NEL)輸出相同、都等於規格值;`_kill_esc` 不帶新參數時照舊。[test:t_dispatch_lens_name_show_invisible_and_wide]
- [S42] spec-freeze 印的那行與 `--json` 的 `line`、`spec_path`:計劃路徑含要跳脫的字元時照名字出口顯示(標準輸出沒有原樣的 ESC、U+202E、反引號),stderr 講明那行不能直接貼;一般路徑照印、不提醒;寫法判斷照用原值。[test:t_spec_freeze_line_shown_through_name_exit]
- [S43] 設計審計劃連 8 篇、每篇 40 條各約 160 字的合約時,8 篇的標題都在、超出分配的印「另有 N 條沒顯示」(帶殘留的另計)、落點與句尾照印、不整段截,`--json` 的 `listed`、`shown` 是 8、`text_truncated` 是 false;撐過上限時 `listed` 等於文字裡實際印出的節點標題行數(含「只列名」的行)、`shown` 等於其中貼了內容的標題數(不含「只列名」)、`text_truncated` 是 true。[test:t_dispatch_lens_spec_cap_by_node_and_json_counts]
- [S44] 掛鉤說明行帶計劃值或範圍值的那一句在注入框裡,工具寫死的指示(照派工詞審查即可、spec-freeze 提示、檢查鎖、手動補跑的指令)在框外;範圍算不出時手動指令寫 `lumos impact --diff <範圍>` 並講明 `<範圍>` 是派工詞 `LUMOS-IMPACT:` 那行冒號後面的值,不再寫「上面那段範圍」。[test:t_dispatch_lens_hook_fixed_hints_outside_frame]
- [S45] 輸出跳脫用的「看不見或會改顯示」只有一份判定 `_lens_hidden_char`:Unicode 類別 Cc、Cf、Zl、Zp、Cs、Co、Cn,Unicode 16 Default_Ignorable 全表,與畫面上像空白的 U+2800、U+FFFC、U+1D159、U+303F、U+16FE4、U+13441、U+13442;名字出口、正文最後一道 `_lens_visible` 與掛鉤抄本對全部 0x110000 個碼位的判定都等於測試獨立組的判準,只由這些字與空白組成的名字印「(空名字)」;合約行後面附一串變體選擇符與填充字時,`dispatch-lens main..HEAD` 的派工詞裡看得到每個字的跳脫;`_kill_esc` 不帶新參數時照舊。[test:t_dispatch_lens_hidden_chars_every_codepoint] [test:t_dispatch_lens_name_show_blank_lookalikes] [test:t_dispatch_lens_visible_hidden_after_contract]
- [S46] 掛鉤說明行的會談專案路徑走名字顯示規則(包在 ‹ › 裡、看不見的字跳脫),跟計劃值、範圍值同一套。[test:t_dispatch_lens_hook_repo_field_name_show]
- [S47] 目標架構段的字數分配含標題行:整段先留列名行的字數、其餘照前 3 個節點平分;標題行的命中檔清單最多 `_ARCH_TARGET_LENS_FILES_CHARS`(1000)字、也不超過那篇分配的四分之一,放不下的印「另有 N 支」;連第一條規則都放不下時先把檔名清單縮成「另有 N 支」;還是放不下的那篇寫「規則沒附」,框後講明幾篇規則沒附,一條規則都沒附時尾句改成「一條目標規則都沒附」、不再說「違反一條規則=major」。20 支 200 個反引號的檔名、20 支 300 個 U+F0000 的檔名、三節點各 20 支 250 字檔名與 30 條規則三種情境,每個節點的標題與至少一條規則都在。[test:t_arch_target_text_long_filenames_keep_rules] [test:t_arch_target_text_rules_not_attached_said]
- [S48] 目標架構段工具寫死的段首說明在注入框前、尾句在框後,框裡只放帶值的內容(節點名、檔名、規則、警告與只算到一半);代碼審與設計審兩條路都照這樣。宣告整份不用(規則清單是空的)時不印「只算到一半」。[test:t_arch_target_text_fixed_lines_outside_frame] [test:t_arch_target_split_no_rules_no_cut]
- [S49] 規則原文照原字印:冒號後面只留共用欄位解析 `slot_parse` 的核心句(欄位拿掉)再套每條 200 字上限,反引號與反斜線不跳脫,看不見的字、‹ ›、框線字元照樣跳脫、整條包在 ‹ › 裡;派工範本 §7.6 講明引「目標規則」時引 ‹ › 之間的字、不含 ‹ ›,跳脫序列照印出來的字抄。[test:t_arch_target_rule_show_code_text_kept] [test:t_design_loop_manuals_target_rule_quote]
- [S50] 設計審目標架構段找計劃裡反引號路徑不回溯:4 萬段沒收尾的 `a/a/…` 1 秒內掃完(舊正規式 13 秒),形狀照舊;計劃超過 `_ARCH_TARGET_SPEC_SCAN_MAX`(20 萬)字只掃前面,段裡講明只掃了前多少字。[test:t_dispatch_lens_spec_backtick_paths_linear]
- [S51] 新增殘留段每條合約最多列 `_LENS_RESIDUAL_REFS_MAX`(12)筆殘留指標(有原因的先列、決策內容只讀列出的),其餘印「另有 N 筆殘留指標未列」;代碼審派工鏡頭整段 `text` 超過 `_LENS_TEXT_MAX`(r8 起 24000)字時在行界截(走 `_lens_spec_cap_lines`)、截點在框裡先補框尾、講明截了與原本多少字(同一個上限重跑拿到的一樣,不叫人手動重跑),`--json` 帶 `text_truncated`。[test:t_dispatch_lens_residual_refs_capped] [test:t_dispatch_lens_diff_text_total_cap]
- [S52] 規則原文的核心句照 `slot_parse` 的文法:欄位的值帶 `[[連結]]` 或含方括號的行內程式碼時整個欄位拿掉,欄位後面還有字時欄位拿掉、後面的字照留,不在白名單的 `[a:b]` 是正文照留;尾端接 20 萬個欄位時 1 秒內(或耗時不到 5 萬個的 8 倍)。[test:t_arch_target_rule_show_shared_slot_parse] [test:t_arch_target_rule_show_many_fields_linear]
- [S53] 正文最後一道 `_lens_visible` 對緊跟在看得見的字後面的單一 U+FE0F(❤️)、前後都是看得見的字(或照印的 U+FE0F)的單一 U+200D(👨‍👩、❤️‍🔥)照印;孤立的、連續的、貼著空白或其他看不見的字的照舊跳脫;名字出口照舊全跳;合約行含 ❤️ 與 👨‍👩 時 `dispatch-lens main..HEAD` 的派工詞裡是原字。[test:t_dispatch_lens_visible_emoji_sequences_kept]
- [S54] 代碼審派工鏡頭整段截斷時,工具寫死的必答指示(表態記錄那句、殘留必答題)接在截斷說明之後、一定附,整段(含必答指示)在上限內、框頭尾數相等;整段上限不超過設計審 `_LENS_SPEC_TEXT_MAX` 的 4 倍。[test:t_dispatch_lens_text_cap_keeps_fixed_asks]
- [S55] 目標架構段標題行的命中檔清單遇到放不下的檔名跳過、再試後面的,「另有 N 支」照實數(含清單上限之外的)。[test:t_arch_target_files_show_skips_long_name]
- [S56] 設計審目標架構段的反引號路徑候選不收含 NUL 的;`_kill_esc` 沒有 `extra_cats` 參數,私用與未指派碼位照樣由 `hidden=True` 跳脫。[test:t_arch_target_spec_bt_paths_drop_nul] [test:t_kill_esc_params_no_extra_cats]

- 測試怎麼搭:S1、S5–S9 用 `git worktree add` 造真的第二個工作樹,在那裡用 spec-freeze 或提交放計劃;會談目錄留在主工作樹,而且停在不含那個提交的分支上(在同一棵樹上跑,不論實作照哪種解讀都會綠)。lumos 層與掛鉤層分開測,不跑端到端:掛鉤找的是全域 lumos,端到端會依機器上裝的版本紅綠不定。不換 `HOME`(S22 只改 PATH)。夾具檔名只用 NFC,NFD 只出現在輸入字串。

## 實務隱患

- 守衛面:掛鉤會改寫子代理的派工詞,也是錨點清單裡的檔。這次不新增去別的目錄跑 git 的路:dispatch-lens 讀計劃只在會談 repo 跑 `rev-parse`、`ls-tree`、`cat-file`(含 `_nodehome_cat_blobs_capped` 的批次讀),都用 `<編號>:<路徑>` 讀物件,不讀 index、不跑過濾器(第三輪正確性席實測 textconv 不執行),跟代碼審那條路(在會談 repo 算別的工作樹的提交)同一個風險面。
- 提交編號是派工詞給的:只收完整編號、解出必須等於輸入,最壞是指到會談 repo 裡別的完整提交、附上那份計劃的節點——附加段開頭印提交與 blob 的前 12 碼,席位對得上 spec-freeze 印的那一行與 rN-dispatch.json 記的 `spec_commit`。
- spec-freeze 會寫物件庫:`hash-object -w --no-filters` 與 `commit-tree` 只新增物件,不動 ref、真的 index 與分支;每個 git 呼叫關掉掛鉤與 fsmonitor,不跑過濾器。有人把 `gc.pruneExpire` 設成 now 或手動 `git gc --prune=now`,當輪的提交會被清掉,鏡頭回 `spec_rev_missing`、有說明行看得見。計劃沒改過就重跑 spec-freeze 寫回同一份 `--out`;已折進修正就會被 `out_conflict` 擋下,這一輪剩下的席改成在計劃所在工作樹跑 `lumos dispatch-lens --spec <rN-snapshot.md>` 手動貼固定席,不換掉已凍的快照。
- 節點內容讀會談目錄的版本:計劃所在分支改過的 Systems 節點,席位看到的是會談目錄那份;附加段頭寫明是哪個版本。
- 過渡期多一次呼叫:舊 lumos 的設計審失敗是 stdout 空加 rc 2,掛鉤會當成舊版、拿掉選配旗標再叫一次;新 lumos 失敗印 JSON 列,不再白跑。只吃預算,不影響結果。
- 已排除:金流:不碰。
- 已排除:對外送出:只在本機跑 git 與 lumos。
- 已排除:不可逆:還原提交即回到只認工作樹路徑;spec-freeze 建的提交不掛 ref,gc 會清;派工詞多出的提交寫法,舊版會當成工作樹路徑找不到、照舊不附。
- 改了錨點清單裡的掛鉤與測試檔,提交前要 `lumos anchor approve`。

REVISIT:2026-11-15 查事件帳與席報告,spec-freeze 印過「不是掛鉤會叫的那支」警告之後,仍有提交寫法被舊的全域 lumos 當成工作樹路徑、靜默不附的;有就把警告改成拒絕。
REVISIT:2026-12-15 翻一次這段期間的席報告與材料,看有沒有席位照著框內名字(帶 ‹ › 的計劃路徑、節點名、檔名、規則原文)裡的句子做事:`rN-dispatch.json` 只記材料與席位、沒存派工詞,所以逐輪看該輪材料——設計審看 `rN-snapshot.md`(凍結的計劃)有沒有連結、落點、反引號程式路徑,代碼審看 `rN-*.patch` 有沒有改到節點名、檔名或目標架構宣告與規則;有的輪次,把席報告結論(clean、跳過審查、照檔名回報)跟該輪實際改動對照——照做的席位多半不會引名字,所以不能只靠 grep;`grep -rlF '‹' governance/review-reports/*/r*-*.md` 只當輔助(一個連字號的舊檔名也涵蓋,結果自己剔掉 `r*-intake.md` 與 `r*-snapshot.md`);有就把名字改成只印雜湊與長度,或跟圖譜實際節點名表比對
REVISIT:2026-12-15 數附加段裡「只在那個提交裡,會談目錄還沒有這篇」與「節點內容是會談目錄的版本」出現的次數,多到席位常拿不到該審的版本,就改成附提交裡那份內容。

## 回退

照順序:
1. 還原程式、掛鉤、範本與手冊的提交(範本與掛鉤一起退,免得範本還叫人跑 spec-freeze、掛鉤卻不認)。
2. **全域 lumos 也要退並核對**:掛鉤與編排者敲的都是 `_trusted_lumos` 找到的那支(PATH 上的 `lumos`,本機是 `~/.local/bin/lumos` 指到 `~/harness/lumos-toolchain`;沒有才用 `$LUMOS_HOME`)。把那個來源拉到還原後的提交,核對 `lumos spec-freeze --help` 回「沒有這個子命令」(舊 lumos 實際印「擋下:沒有「spec-freeze」這個指令」)。只退掛鉤不退這支,會留下舊掛鉤配新 lumos,指紋核對卻顯示已回原狀。
3. 每個消費專案跑 `lumos update`,再 `lumos anchor approve --note "<為什麼>"` 並提交簽名檔。`_sync_global_hooks` 用 `copy2` 無條件覆寫 `~/.claude/hooks/`、不比版本,**最後一個跑 update 的專案會把它的掛鉤寫回 `~/.claude/hooks/`**:所以第 2 步先做,各專案拉到的來源就已經是退過的版本;`_sync_global_hooks` 也把同一批掛鉤 copy2 到 `~/.codex/hooks/`。全部跑完再核對 `~/.claude/hooks/dispatch-lens-hook.py` 與 `~/.codex/hooks/dispatch-lens-hook.py` 的指紋都等於還原後的版本。之後有人從還沒退的分支或舊工作樹跑 `lumos install`、`lumos update --no-pull`,會把新版寫回去;核對不相等就從已退的專案再跑一次 `lumos update`。
   - 機器上沒有可成功 pull 的消費專案時(`cmd_update` 在專案根就是來源 repo 時只重刷紀律區塊、不同步全域掛鉤),改在已退的來源跑 `lumos install` 同步全域掛鉤,再照上面核對兩個目錄的指紋。
4. 還有派工詞帶著提交寫法的進行中迴圈:先跑 `grep -l spec_commit governance/review-reports/*/r*-dispatch.json` 列出來(每個消費專案各跑一次),清單裡還沒收尾的迴圈就是要處理的。舊版 lumos 把提交寫法當成工作樹路徑找不到、不印失敗代碼,不會有說明行;編排者在回退當下手動 `lumos dispatch-lens --spec <工作樹路徑>` 貼固定席,之後照退回的範本寫工作樹路徑。手動貼的固定席讀的是工作樹現況,跟 `rN-snapshot.md` 可能不同版本,在該輪收貨紀錄寫明。
5. 撤掉本計劃的 REVISIT 與 RETIRE-IF 行,或在行尾標 `[closed:<日期> 已回退不做]`(結案理由至少 4 個實字,只寫「已回退」三個字會被判成結案標記寫錯),免得 doctor 到期叫人去數一個已不存在的欄位。事件帳裡已記的 `spec_commit`、`spec_worktree` note 留著;回退前 grep 一次確認沒有讀端把這兩個字首當固定格式解析。
6. spec-freeze 建的不掛 ref 提交不用手動清,gc 會清。

## 實作紀錄

2026-10-14 照本文實作,S1–S56 各綁測試(名字照條款的 `[test:]`;S25 起是代碼審 r3–r8 補的)。跟本文字面不同、或本文沒寫到而實作時補定的地方:

- **程式檔候選多收反引號裡的路徑**:`_LENS_SPEC_CODE_RE` 只收 ASCII,中文檔名(S6 要列的那種)永遠抓不到。另加一條只收反引號裡、開頭是同一組目錄的路徑(`_LENS_SPEC_CODE_BT_RE`),兩種寫法共用,所以工作樹寫法也多認得反引號裡的中文檔名;原本那條的結果與順序不變。
- **spec-freeze 也擋非 NFC 路徑**(回 `spec_missing`,併在第 3 步):dispatch-lens 對非 NFC 路徑一律回 `spec_missing`,不擋的話會印出一行每席都讀不到的 `LUMOS-SPEC:`,跟第 4 步擋大小同一個理由。
- **讀回那一步的批次讀取沒帶兩個 `-c`**:spec-freeze 讀回用的是 dispatch-lens 同一支讀法,`ls-tree` 有帶 `core.hooksPath=/dev/null` 與 `core.fsmonitor=false`,但內容走既有 `_nodehome_cat_blobs_capped`,它自己起 `git cat-file --batch`、沒有傳全域選項的參數。`cat-file` 只讀物件、不碰 index,不會觸發掛鉤或 fsmonitor(S17 有裝 post-index-change 與 fsmonitor 記號驗過);為了這一點改那支共用函式的簽名不划算。
- **`--out` 選填**:不給就只建提交、印那一行(計劃在別的工作樹時用,見做法 9)。位置合格(在 `governance/review-reports/` 底下)、上層不存在時才建;寫入失敗、上層是檔案或 `--out` 本身是符號連結都回 `out_conflict`。
- **`_dispatch_lens_fail` 收到不在 `_LENS_FAIL_CODES` 的代碼會丟 `ValueError`**,不讓沒登記的代碼漏到掛鉤(S11 一併驗)。
- **全域 lumos 警告直接載入掛鉤檔的 `_trusted_lumos`**:先找這支 lumos 旁邊的 `hooks/claude/dispatch-lens-hook.py`,沒有再找 `~/.claude/hooks/` 那支,不另抄一份找法(那段在掛鉤之間是逐字複本、有守衛盯著)。兩個都找不到就不印警告。
- **有輸出就加注入框**,包括提交寫法沒有任何節點、只印來源行的情況,以及工作樹寫法只有落點的情況(代碼審 r5:原本工作樹寫法只有列出節點時才框,落點名在框外)。`--json` 另帶 `only_in_commit`(只在提交裡的程式檔清單)。
- **git 呼叫多兩個保險**:`ls-tree` 加 `--literal-pathspecs`(檔名裡的 `*` 不當萬用字元),`commit-tree` 加 `--no-gpg-sign`。
- **S19 的「實作前的掛鉤」釘 `30238fbd`**:那是本計劃實作前最後一次改掛鉤的提交、已在主線上,掛鉤 blob 跟本計劃開工時(`82cea578`)相同;分支壓成一個提交合進主線後 `82cea578` 可能不在主線歷史上。新 lumos 的成功列與每種計劃類失敗列由測試當場跑被測 lumos 產生,不手寫。
- **先紅再綠的例外**:S12(成功不記事件)與 S20(新掛鉤配舊 lumos)守的是實作前就成立的行為,實作前跑就是綠的;改用變異實驗證明抓得到錯(成功也記事件 → S12 紅;把空回應當成 `spec_missing` → S20 紅)。
- **目標架構段的 vault**:做法 4 寫工作樹寫法「跟現在相同」不精確——原本取 HEAD 樹裡排序第一個 vault,現在傳工作樹 glob 的 `slugs[0]`。只有工作樹有 HEAD 沒有、而且排序更前的 `docs/*-knowledge` 時兩邊不同;那時節點仍從 HEAD 讀,目標架構段會找不到節點、只附說明。影響小,沒改回。
- **掛鉤記事件只有一支 `_mark_event`、寬接 Exception**:逾時、鎖錯誤、背景未啟動、範圍與計劃讀不到五處都走它;列舉例外型別時 RuntimeError 會跑出掛鉤。
- **讀節點內容收成一支 `_vault_node_read`**:固定席(impact 找到的家)、計劃連結與落點三處都先過同一套圖譜內檢查(`_vault_node_check`:節點名寫法正規——代碼審 r5 起只看路徑安全(不准絕對路徑、. .. 空段、NUL、換行),不再看字元集——、圖譜資料夾本身與上層每一段都不是符號連結、節點檔解析後仍在圖譜資料夾裡)才讀;沒過的不列、不讀、只計數。固定席的節點名來自 impact 的 JSON,原本直接 `root / rel` 讀,同一篇捷徑檔在落點判「指到圖譜外」、在固定席照讀。圖譜資料夾本身或上層是符號連結時另印一行講明原因;工作樹寫法 glob 找 `*-knowledge` 時跳過符號連結,只剩符號連結時 `no_knowledge` 的訊息也講明。
- **作者寫得到的名字一律以資料形式印、同一個出口**(`_lens_author_name_show`;代碼審 r5 起取代 r1–r4 的字元白名單):包在 ‹ › 裡、控制格式私用未指派類與 ‹ ›、反斜線、框線字元 ─ 與反引號 跳脫(`_kill_esc` 加 `extra_chars` 參數,預設不帶時既有呼叫端不變;原本另有 `extra_cats`,r7 改由 `hidden` 涵蓋後沒人傳,r8 拿掉)、截斷標明原長、空名字固定字樣;讀不讀節點只看路徑安全。原本計劃路徑另用只擋反引號與控制類字元的黑名單,程式檔名的幾行只去控制字元;r1–r4 改成白名單後,合法名字整支消失、整句英文照印,判準本身選錯。掛鉤說明行用同一套規則的最小抄本,測試比對兩邊對同一批樣本的輸出。目標架構段的節點名、規則原文與檔名也走這個出口,出口、加框與上限都收在 `_arch_target_text`,代碼審與設計審兩條路都經它(代碼審 r6:r5 只讓設計審那條傳出口、自己加框,代碼審那條印被審分支的檔名不走出口、在框外);守衛改成端到端哨兵測試,拿掉原本掃寫法的 AST 守衛。
- **提交寫法「提交裡有沒有」只查候選**:候選(連結與落點排前面、程式檔在後)交給既有的批次查大小 `_nodehome_cat_sizes`,有大小的再用只帶這些路徑的 `ls-tree` 看 mode(符號連結與目錄不算);不列整棵樹、不另寫 cat-file 解析。每個候選的 NFC 與 NFD 兩種寫法都問,`ls-tree` 關掉 `core.precomposeunicode`(提交本身存 NFD 時才查得到)。候選最多 5000 個(`_LENS_SPEC_COMMIT_CANDS_MAX`;r3 併發席實測 5000 個約 1.1 秒,r1 的 3300 個候選要照實數完),超過的不問、印「只算到一半」、JSON 的 `cands_truncated` 為真,沒問到的不算成找不到。落點與連結先算,impact 最後用剩的預算;落點段只有標題時不印。
- **提交寫法的編號檢查收成一支 `_spec_commit_rev_ok`**:dispatch-lens 與 spec-freeze 共用(只收 40/64 碼、解出等於輸入)。
- **lumos 入口清 git 環境**:`main()` 一進來設 `GIT_NO_REPLACE_OBJECTS=1`、`GIT_GRAFT_FILE` 指到不存在的路徑、拿掉 `GIT_DIFF_OPTS` 與 `GIT_EXTERNAL_DIFF`,所有子命令與子行程都繼承;理由與影響面寫在 [[Systems/lumos-cli-lifecycle]]。測試在行程內呼叫 `main()` 時,執行器每支測試前後把這四個變數存回。
- **掛鉤判計劃類失敗照 lumos 回的 `spec_source`**,不另抄一份「只屬範圍」的代碼清單;`lens_fail` 不是字串時不附說明行。

- 設計審固定席模式的基本測試改名 `t_dispatch_lens_spec_mode_core`:舊名是 `t_arch_target_dispatch_lens_spec_mode` 的子字串,修正關卡用 `-k` 篩測試時會同時選到兩支、判名字不唯一。

## 審計修正紀錄

- r1 前掃(2026-10-14):9 條(語意命中 5、③ 2、② 1、存在命中 1)直接修進本文:Codex 跨 repo 認領領不到,改寫成不做;重複標記的處理前後矛盾,統一成不算;信任檢查要先讀 `.git` 檔、不能先跑 git,另寫資料夾版不改逐字複本;更正「跟會談目錄受到的保護相同」(會談目錄現在沒有檢查);設計審失敗沒有說明行,補三個代碼;原因代碼拆成六個並與 lumos 的表分開;舊裁定兩處加會談 codex-harness 標作廢;路徑可以有空白。前掃紀錄在 `governance/review-reports/派工鏡頭可指定目標repo/r1-intake.md`。
- r1(2026-10-14,6 席):32 條/blocking 11/信任靠權限位元擋不住 `.git` 裡的 `commondir`、權限放寬的設定檔、從沒用過的下載 repo,又會在 `/tmp` 底下誤殺;標記寫歪會退回會談目錄附上錯的樹;成功時看不出用的是哪個 repo;被拒時連角色卡一起丟;記帳量不到撤除條件;舊裁定照字面作廢會把還有效的決策一起作廢;回退「無害」不成立;全數折入:改成登記制(會談 repo 的工作樹加裝過 lumos 的專案)、寫歪與重複都不算也不退回、成功印來源行、被拒照附角色卡、掛鉤自己不再跑 git、事件 note 固定字首、只作廢被推翻的那一格、手冊要改的地方列全、回退改成清單。席報告在 `governance/review-reports/派工鏡頭可指定目標repo/`。
- r2(2026-10-14,3 席):19 條/blocking 14/登記清單放哪、誰能寫、拒絕說明本身誘導登記、圍欄裡的標記被靜默忽略、被拒時取角色卡會用錯的樹、會談本身是工作樹時怎麼列工作樹、測試換 `HOME` 會讓掛鉤找不到 lumos;全數折入:整類拿掉——不再讓派工詞指定路徑,改成設計審標記收 git 原生的 `<提交>:<路徑>` 寫法,在會談 repo 從物件庫讀計劃(同一個 repo 的工作樹共用物件庫);跨 repo 照舊裁定不做。席報告在 `governance/review-reports/派工鏡頭可指定目標repo/`。
- 註:前兩輪寫的標作廢、登記清單等做法已整類撤回,舊裁定照舊成立。
- r3(2026-10-14,6 席):46 條/blocking 16/短編號會被同名分支搶走、路徑只做字串檢查會把目錄與符號連結讀成計劃、掛鉤說不解析卻要分辨寫法、程式檔存在用提交判而牽連用會談目錄算、快照與提交沒綁在一起、回退漏掉全域 lumos;全數折入:只收完整提交編號、提交那條路新增路徑規則並只讀一般檔、讀計劃收斂成一支、存在照會談目錄判並另列只在提交裡的、lumos 回 `spec_source` 給掛鉤讀、新增 `lumos spec-freeze` 同時產生提交與快照、回退加全域 lumos。收貨紀錄在 `governance/review-reports/派工鏡頭可指定目標repo/r3-intake.md`。
- r4(2026-10-14,6 席):36 條/blocking 10/符號連結會把 repo 外的檔凍進快照、大小上限與檢查順序在建提交之後才判、暫存 index 仍會跑 post-index-change 掛鉤、重跑 spec-freeze 會覆寫已凍結的快照、成功記事件違反「不擋不驗不記不量」、只在提交裡與不存在的節點名會把作者的自由文字印進派工詞、「不建提交」與「只在會談 repo 跑」的量法照字面永遠綠;全數折入:spec-freeze 改成編號檢查順序(形狀→路徑字串→逐段 lstat→大小→`--out` 比對→建提交)、所有 git 呼叫關掉掛鉤、`--out` 內容不同就拒絕、成功不記事件改數派工單、節點名過嚴格字元集與存在檢查才列名、`ls-tree` 逐檔加 `-z`、驗收條款補量法與邊界、回退補 Codex 掛鉤目錄與進行中迴圈清單。這是跑滿後破例加開的第四輪,折完直接進實作,不再派審。收貨紀錄在 `governance/review-reports/派工鏡頭可指定目標repo/r4-intake.md`。
