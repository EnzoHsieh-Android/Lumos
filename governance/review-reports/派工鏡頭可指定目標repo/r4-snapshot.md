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
    trade_offs: "完全不同的 repo 照舊不支援,只附說明行、手動貼固定席;每輪派工前要多敲一次 lumos spec-freeze;只收完整提交編號,手打不方便"
    decided: 2026-10-14
    valid: true
---
# 派工鏡頭可指定目標repo_計劃

> 白話:派審查席時,掛鉤會自動把「這次改動牽連到的圖譜筆記」貼進派工詞。它一律在「會談開在哪個資料夾」那裡算。全域規則要求每份工作開獨立的 git 工作樹,於是計劃常常只存在別的工作樹裡,掛鉤在會談目錄找不到,只附一行「沒附」。同一個 repo 的工作樹共用同一份 git 物件庫:在計劃所在的工作樹跑 `lumos spec-freeze`,把計劃凍成一個不掛分支的提交、同時寫出凍結快照,在會談目錄就能用「完整提交編號:計劃路徑」把它讀出來。改成:設計審的 `LUMOS-SPEC:` 可以寫成 `<完整提交編號>:<計劃路徑>`,lumos 在會談 repo 裡從那個提交讀計劃;程式檔與節點存不存在照會談目錄判,只在提交裡有的另外列名。不去別的目錄跑 git,不新增信任機制;完全不同的 repo 照舊不支援,附說明行。

## 緣起

- 2026-10-13 後端示範:會談開在 lumos 工具鏈,審的是示範 repo `order-demo` 的分支,派工鏡頭算不出牽連筆記(只附了說明行)。2026-10-14 夜裡更普遍:全域規則要求每個工作開獨立的 git 工作樹,我在三個工作樹各開一份計劃、派了十幾席設計審,計劃只存在那些工作樹裡,掛鉤在會談目錄找不到,所有席都沒拿到固定席節點。出處:使用者 2026-10-14 列的示範改進第 4 條;當晚的席報告都寫「派工尾端沒有附固定席節點」。
- 舊裁定:[[Projects/派工鏡頭跨repo不再靜默_計劃]] 的 WHY 行寫「不選:標記行加 repo 路徑讓掛鉤改去那裡算(標記行文法要改、派工詞的自由文字會變成掛鉤去跑 git 的路徑,先不開這個口;說明行給繞法即可)」。**本計劃不推翻它**:第一、二輪設計審試過讓 `LUMOS-REPO:` 指定任意路徑,再用權限位元(r1)或登記清單(r2)判信不信,兩輪共 51 條發現,幾乎全出在「讓派工詞的文字決定去哪裡跑 git」這一層(`commondir` 指到別處、登記清單誰能寫、拒絕說明本身誘導登記、圍欄裡的標記被靜默忽略、被拒時取角色卡會用錯的樹、會談本身是工作樹時怎麼列工作樹)。這正是舊裁定擔心的口。
  - 改走的路:痛的是「同一個 repo 的另一個工作樹」(當晚十幾席都是這種),而工作樹共用物件庫,讀提交裡的計劃只要在會談 repo 跑 git,不碰派工詞指到的任何目錄。示範 repo 那種完全不同的 repo 一晚只出現一次,照舊附說明行、手動貼。

PRIOR-ART: 代碼審那條路已經是這樣:`LUMOS-IMPACT:` 寫完整提交編號,工作樹共用物件庫,在會談目錄就算得出別的工作樹的提交(派工範本已要求寫完整提交編號、不寫 HEAD)。設計審照同一個道理,把計劃路徑換成 git 原生的 `<rev>:<path>` 寫法(`git show` 本來就收這種寫法),不自創文法、不新增信任機制。提交編號的解法照抄 `_lens_full_sha`,讀提交裡的檔照抄 `_nodehome_cat_blobs_capped`。凍結提交借 git 原生的做法:`GIT_INDEX_FILE` 指一份暫存 index,`write-tree` 加 `commit-tree` 建不掛 ref 的提交(`git stash create` 就是這樣建提交、不動分支)。借用,不自建。
RETIRE-IF: Claude Code 在派工事件帶出子代理的工作目錄(會談目錄與工作目錄不再可能錯開),或連續 8 週掛鉤事件裡都沒有 `spec_commit` 字首的 note——拿掉這個寫法與 `lumos spec-freeze`。
REVISIT:2026-12-15 數一次掛鉤事件裡 `spec_commit` 字首 note 的次數與失敗代碼分布(逾時那幾筆 kind 是 timeout、不帶這個字首,不計),照 RETIRE-IF 判。

## 做法

1. **`LUMOS-SPEC:` 多收提交寫法,只收完整提交編號**:值以**第一個冒號**切開(檔名可以再含冒號)。冒號前全是十六進位、至少 7 碼時,當成「提交寫法」;其他值一律照現在當工作樹路徑。
   - 提交寫法裡,`<提交>` 必須是 40 或 64 碼十六進位(不分大小寫,內部轉小寫),用既有 `_lens_full_sha` 的解法(`rev-parse --verify -q --end-of-options <提交>^{commit}`),而且解出的完整編號必須等於轉小寫後的輸入;不合任一條都回 `spec_rev_missing`。
   - 所以短編號(7–39 碼、41–63 碼)、被同名分支或標籤導到別的提交、縮寫撞號,一律不成立:git 對不足完整長度的字串會先當 ref 名解析,同名分支會搶走(第三輪兩席實測);縮寫隨提交增加也會從解得到變成模稜兩可。只收完整編號,跟代碼審 `LUMOS-IMPACT:` 用的 `_LENS_SHA_RE` 同一個形狀。`_lens_git` 逾時或 git 跑不起來回 None,也歸 `spec_rev_missing`。
   - 為什麼「至少 7 碼十六進位加冒號」就算提交寫法:寫短編號的人拿得到 `spec_rev_missing` 的說明,不會被當成工作樹路徑、拿到「先凍結」的繞法。工作樹路徑剛好以 7 碼以上十六進位的目錄名加冒號開頭,在 docs 底下實務上不會有。
2. **路徑規則(提交那條路新增,工作樹那條路不變)**:提交寫法冒號後的路徑必須是正規的 posix 相對路徑:不得空、不得以 `/` 開頭、不得有 `.`、`..` 或空段(連續兩個 `/`、結尾 `/`)、不得含反斜線或空白;前兩段必須是 `docs/<slug>-knowledge/`。不合就回 `spec_outside_repo`。
   - 只做字串檢查,不先正規化:`./docs/…` 這種 git 認得的寫法也擋,條款只收一種寫法。
   - vault 用路徑自己的 slug,不取會談工作樹的 `slugs[0]`:repo 有兩個 `*-knowledge` 時,連結節點、落點、目標架構段都到計劃所在的那個 vault 找。會談工作樹沒有同名的 `docs/<slug>-knowledge/` 目錄時回 `no_knowledge`。
   - 檔名的 Unicode 正規化不處理:macOS 預設 `core.precomposeunicode=true`,用 NFD 檔名寫的測試會變成平台相依,夾具只用 NFC 檔名。
   - **工作樹那條路的檢查一律不動**:照現在接受絕對路徑、只看解析後在 repo 內與是檔案、沒有大小上限、`vault_rel` 照現在取 `slugs[0]`。唯一的差別是失敗時 `--json` 多印失敗代碼(見 6)。
3. **只讀一般檔**:提交寫法先用 `_lens_git` 跑 `ls-tree <完整編號> -- <路徑>`,結果必須正好一列、mode 是 100644 或 100755、type 是 blob;沒有這一列,或是目錄(040000)、符號連結(120000)、子模組(160000),都回 `spec_missing`(目錄會印出檔名清單、符號連結會印出連結目標字串,不擋就會被當成計劃內容掃)。
   - 內容用既有 `_nodehome_cat_blobs_capped(root, ["<完整編號>:<路徑>"], 1MB)` 讀,不另組 `cat-file -s` 加 `show`:專案已經有「讀提交裡的檔、先問大小、超過上限不讀進記憶體」這一套,它的註解寫明上限放在批次讀取這一層、不另起查法(角色鏡頭代碼審架構席裁過)。單項回 None(超過上限)回新代碼 `spec_too_large`;整批回 None(逾時或 git 失敗)回 `spec_missing`。上限照它的比較:剛好 1MB(1048576 位元組)照讀,多一個位元組就擋。解碼照工作樹那條用 `utf-8` 加 `errors="replace"`。
   - 它內部直接起子行程、不走 `_lens_git`,所以「只在會談 repo 跑 git」改用 PATH 上的假 `git` 驗(S9),不靠替換 `_lens_git`。
4. **讀計劃收斂成一支**:新增共用的讀計劃函式(暫名 `_dispatch_lens_read_spec`),收 repo 根與標記值,回計劃文字、`spec_source`(`commit` 或 `worktree`)、完整提交編號、blob 編號、vault 路徑,或失敗代碼與 rc。`cmd_dispatch_lens_spec` 與 `_dispatch_lens_spec_with_arch` 都呼叫它,文法只在這一處判。
   - `_dispatch_lens_spec_with_arch` 不再自己 `Path(spec_path)` 讀檔(現在遇到提交寫法會讀檔失敗、目標架構段靜默消失):外層先呼叫一次,把結果交給 `cmd_dispatch_lens_spec`(新增選填參數),同一份計劃只讀一次、git 只跑一輪。
   - 目標架構段(`_dispatch_lens_spec_arch_text`)吃的計劃文字就是這一份;宣告與節點照現在從會談 repo 的 HEAD 讀。
5. **程式檔存在照會談目錄判**:跟 impact 一致(impact 子行程用 `--repo <會談 repo 根>` 讀會談目錄)。計劃提到的程式檔照現在用會談目錄的 `is_file()` 判、照現在跑 impact。
   - 提交寫法時,會談目錄沒有、只在那個提交裡有的檔(一次 `ls-tree` 帶多個路徑判,要是一般檔),另列一行「只在提交 <12碼> 裡、會談目錄沒有,沒算牽連:<檔>」,最多 5 個(同 `_LENS_SPEC_MAX_FILES`)。計劃要新增或改名的檔就是這種,不再落到「沒牽到任何家、合約或事故的節點」那句,讓席位以為已經算過。
   - 反方向(會談目錄有、提交裡已刪)照會談目錄算、照附。
6. **連結節點與落點分三種(提交寫法)**:計劃直接連結的 Systems/Issues 節點:
   - 會談目錄有:照現在附,內容讀會談目錄那份。附加段頭寫明「節點內容是會談目錄的版本」(提交裡改過的版本不附)。
   - 只在那個提交裡有:列名並標「只在那個提交裡,會談目錄還沒有這篇」,內容不附。
   - 兩邊都沒有:列名並標「連結指到不存在的節點」(分得出是錯字連結)。
   - 落點段(`_nodehome_landing_sizes`)同樣分:會談目錄有就照印大小;只在提交裡有就標「只在那個提交裡,會談目錄還沒有這篇」;兩邊都沒有照現在印「還不存在(要新開)」。
   - 用詞一律是「會談目錄」,不寫「主線」(會談目錄不一定在 main 上)。工作樹寫法照現在只認會談目錄有的節點。
   - rc 照樣是 0。
7. **lumos 的輸出欄位與失敗代碼**:`--json` 的成功列與失敗列都帶 `spec_source`;提交寫法另帶 `spec_commit`(完整編號)與 `spec_blob`(blob 編號)。提交寫法成功時,附加段開頭加印「計劃來源:提交 <12碼> 的 <路徑>(blob <12碼>)」,席位拿得到跟 spec-freeze 那行對照的值。
   - 失敗代碼共五個,**都是新增**(現在的工作樹那條路失敗只印 stderr、不印代碼):`spec_rev_missing`、`spec_missing`、`spec_outside_repo`、`spec_too_large`、`no_knowledge`。rc:前四個 2,`no_knowledge` 3,跟現在工作樹那條路的 rc 對齊。工作樹那條路對應:不在 repo 裡 `spec_outside_repo`、不存在或讀不到 `spec_missing`、沒有圖譜 `no_knowledge`;stderr 原文與 rc 不變。
   - `_dispatch_lens_fail` 加選填的附帶欄位(帶 `spec_source` 等),說明裡的種數從「六種」改成「十一種(範圍六種、計劃五種)」;掛鉤的 `LENS_FAIL_REASONS` 加這五個代碼。
8. **掛鉤不判文法**:標記的找法照舊(`find_spec_marker`,`SPEC_RE` 不改),值原樣交給 lumos;掛鉤不解析值的形狀、不跑 git。說明行與 note 只讀 lumos 回的 `spec_source`、`spec_commit`、`lens_fail`。
   - `_fail_note(r, rng, repo)` 改成 `_fail_note(r, rng, repo, spec=None)`:`rng` 有值照現在走範圍版(`FAIL_NOTE` 不動);`spec` 有值且 `lens_fail` 是計劃類代碼時,用新寫的計劃版 `SPEC_FAIL_NOTE`:「LUMOS-LENS:這次沒附固定席節點(計劃 {what} 在會談專案 {repo} 讀不到:{why})。……照派工詞審查即可。」`{what}` 用 `_clean_field(spec)`,不用範圍專用的 `_SAFE_RANGE_RE`(計劃路徑一定不合它,會整句顯示成 `<範圍>`)。
   - `spec_source` 是 `worktree`、代碼是 `spec_missing` 或 `spec_outside_repo` 時加繞法:「計劃在別的工作樹時,在那個工作樹跑 `lumos spec-freeze <計劃> --out <快照>`,把它印的那行 `LUMOS-SPEC:` 貼進派工詞」。兩個代碼都加:把別的工作樹裡的計劃寫成絕對路徑是最自然的寫法,它落在 `spec_outside_repo`。
   - 事件 kind:計劃類 spec_* 代碼(使用者輸入錯)記 `ok` 加 note,不記 `error`:錯的提交編號、打錯的路徑不是掛鉤壞掉,記成 `error` 會拉高 enforcement 的錯誤數、蓋過真的掛鉤錯誤。`no_knowledge` 與範圍類代碼照現在記 `error`。
   - 這是對 `_hookevent.mark`「只在吞掉逾時或失敗時呼叫」慣例的有限破例:只用在提交寫法成功與這幾個代碼,note 用固定字首——提交寫法成功 `spec_commit`、失敗 `spec_commit <代碼>`、工作樹寫法失敗 `spec_worktree <代碼>`;工作樹寫法成功不記(跟現在一樣)。逾時時照現在記 `timeout` 與逾時句,這筆不帶字首。也是對 [[Projects/派工鏡頭注入_計劃]]「不擋不驗不記不量」的有限鬆綁——只記這個寫法的結果,不記注入次數。
   - 掛鉤檔頭「其餘判斷全在 lumos 端」照舊成立,補一句「計劃寫法也由 lumos 判,掛鉤只讀 `spec_source`」。
9. **新子命令 `lumos spec-freeze <計劃> --out <rN-snapshot.md>`**:在工作目錄(計劃所在的工作樹)建一個不掛分支的提交,再從這個提交寫出凍結快照,印出要貼的一行 `LUMOS-SPEC: <完整提交編號>:<路徑>`(`--json` 另給 `spec_commit`、`spec_blob`、路徑)。快照與提交因此一定一致,也不必先正式提交草稿(正式提交會撞上提交前檢查、錨點簽名,還會多出要壓掉的半成品提交)。
   - 步驟:取工作目錄的 repo 根;`<計劃>` 先套第 2 條的路徑規則(相對於 repo 根),而且要是工作樹上的一般檔;在暫存目錄開一份 index,用 `GIT_INDEX_FILE` 指向它:`read-tree HEAD` 起、`hash-object -w --no-filters <計劃>` 放進這份計劃的工作樹內容(不跑過濾器,內容與工作樹位元組相同)、`update-index --add --cacheinfo <mode>,<blob>,<路徑>`、`write-tree`、`commit-tree <tree> -p HEAD`;作者與提交者用固定的環境變數(`lumos spec-freeze`),不讀使用者設定。最後用第 3 條同一支讀法從這個提交讀出計劃,原子寫進 `--out`,刪掉暫存 index。
   - 不跑提交掛鉤(`commit-tree` 不觸發掛鉤),不動任何 ref、真的 index 與分支;工作樹裡其他沒提交的改動不進這個提交(tree 只比 HEAD 多這份計劃)。
   - 拒絕(rc 非 0、不建提交、不寫 `--out`):計劃路徑含空白(標記文法 `\S+` 不收空白,產出的那行會被掛鉤整行略過)、不合路徑規則、不是一般檔、HEAD 不存在。
   - 不掛 ref 的物件在預設 gc 兩週後才會清(`gc.pruneExpire` 預設 2.weeks.ago),設計迴圈一晚跑完,窗口夠用。
   - 派工單 rN-dispatch.json 多記 `spec_commit`(編排者照範本寫)。
10. **範本只叫人用 spec-freeze,以及版本錯開**:`templates.md` 的 `LUMOS-SPEC:` 那一行改成:在計劃所在的工作樹跑 `lumos spec-freeze <計劃> --out <rN-snapshot.md>`,貼它印的那一行;rN-snapshot 就用它寫出的那份。不叫人手寫提交編號。
   - spec-freeze 與掛鉤叫的都是全域那支 lumos(掛鉤用 `_trusted_lumos`:PATH 上的 `lumos`、其次 `$LUMOS_HOME`、其次 `~/harness/lumos-toolchain`;編排者在終端敲的 `lumos` 也是 PATH 那支),所以產得出那一行,就代表全域 lumos 認得這個寫法。範本寫 `lumos spec-freeze`,不寫 `python3.14 scripts/lumos`。
   - 舊掛鉤配新 lumos:提交寫法照常能用,只少 note 與失敗說明行(舊 `_fail_note` 在沒有範圍時直接回空,`LENS_FAIL_REASONS` 也不認新代碼),不報錯。
   - 新掛鉤或新範本配舊 lumos:舊 lumos 沒有 `spec-freeze`,編排者敲下去當場看到錯誤,照舊寫工作樹路徑。
   - Codex 編排時派工訊息對掛鉤是密文,設計審本來就拿不到鏡頭(`--arm` 只收代碼審範圍);範本那一行標明「提交編號寫法只對 Claude 編排有效」,[[Systems/codex-harness]] 的天生限制那段補一句。
11. **要一起改的說法(列全)**:
   - `skills/lumos-design-loop/SKILL.md` 派工步驟裡 `LUMOS-SPEC: <計劃筆記.md>` 那句;
   - `skills/lumos-design-loop/reference.md` 講設計審鏡頭從工作樹讀的那段;
   - `skills/lumos-design-loop/templates.md` 兩處:§1 審計員那行與 §7.6 架構席那格;
   - `skills/lumos-project-notes/reference.md` 的指令表裡 dispatch-lens 那格;
   - `skills/lumos-project-notes/commands/05-設計審查迴圈.md` 的指令表;
   - [[Systems/design-loop]] 講 `LUMOS-SPEC` 落點那段;
   - `scripts/lumos` 的 `--spec` 參數說明(現在寫「從工作樹讀」)與 `cmd_dispatch_lens_spec` 的 docstring,以及新子命令的 `--help` 與指令總數(`lumos --help` 的 choices 有漂移守衛);
   - 掛鉤 `dispatch-lens-hook.py` 的檔頭與新的 `SPEC_FAIL_NOTE`;
   - [[Systems/codex-harness]] 逐一列舉 `lens_fail` 代碼的那行 WHY(六個改成十一個)。
   - `skills/lumos-project-notes/commands/06-代碼審與推送.md` 只講代碼審,不用改。
12. **不做**:不讓派工詞指定任意路徑或別的 repo(舊裁定照舊成立);不改 `LUMOS-IMPACT:` 的寫法;不收短編號、分支名或 `HEAD~1` 這類寫法;不讀工作樹裡沒凍結的改動;不改 `SPEC_RE`(路徑不可含空白,spec-freeze 先擋)。Codex 編排的 `--arm` 不在範圍內。

## 驗收條款

lumos 層(直接跑被測 repo 的 `scripts/lumos dispatch-lens --spec`):

- [S1] 當 `--spec` 是 `<完整提交編號>:docs/x-knowledge/Projects/a_計劃.md`、那份計劃只在另一個工作樹的那個提交裡、計劃提到的程式檔與連結節點在會談目錄都有時,lumos 應回 rc 0、附上那些固定席節點,`--json` 應帶 `spec_source: commit`、`spec_commit`(等於輸入)與 `spec_blob`,附加段開頭應印提交與 blob 的前 12 碼。[test:t_dispatch_lens_spec_commit_from_other_worktree]
- [S2] 當提交寫法的編號不是 40 或 64 碼(例如 7 碼短編號,即使 git 解得到)、是不存在的 40 碼、或在 SHA-1 repo 寫 64 碼時,lumos 應回 `spec_rev_missing`、rc 2、不附任何節點;大寫的完整編號應照常成功。[test:t_dispatch_lens_spec_commit_shape]
- [S3] 當提交寫法的路徑是空字串、以 `/` 開頭、含 `.` 段、`..` 段、空段、反斜線、空白,或前兩段不是 `docs/<slug>-knowledge/` 時,lumos 應回 `spec_outside_repo`;slug 在會談工作樹沒有對應目錄時應回 `no_knowledge`、rc 3;檔名含第二個冒號時應以第一個冒號切開照常讀到。[test:t_dispatch_lens_spec_commit_path_rules]
- [S4] 當提交寫法的路徑在那個提交裡是目錄、符號連結或子模組時,lumos 應回 `spec_missing`;大小是 1048577 位元組時應回 `spec_too_large`;剛好 1048576 位元組時應照常讀。[test:t_dispatch_lens_spec_commit_regular_blob_only]
- [S5] 當 repo 有 `a-knowledge` 與 `b-knowledge` 兩個 vault、提交寫法的計劃在 `b-knowledge` 時,連結節點與落點應到 `b-knowledge` 找,不到 `a-knowledge`。[test:t_dispatch_lens_spec_commit_vault_from_path]
- [S6] 當計劃提到的程式檔只在那個提交裡、會談目錄沒有時,輸出應列「只在提交 <12碼> 裡、會談目錄沒有,沒算牽連」那一行,不應對它跑 impact,也不應出現「沒牽到任何家、合約或事故的節點」。[test:t_dispatch_lens_spec_commit_file_only_in_commit]
- [S7] 當計劃連到三篇節點(會談目錄有、只在那個提交裡有、兩邊都沒有)時,第一篇應附內容,第二篇應只列名並標「只在那個提交裡,會談目錄還沒有這篇」,第三篇應列名並標「連結指到不存在的節點」,rc 應是 0;`lands_in` 寫同樣三篇時落點段應照同樣三種分開。[test:t_dispatch_lens_spec_commit_linked_three_kinds]
- [S8] 當提交寫法帶 `--arch-target`、計劃提到一個只在那個提交裡寫到的路徑時,目標架構段應照提交裡的計劃文字算出、不應靜默變空。[test:t_dispatch_lens_spec_commit_arch_text]
- [S9] 讀提交裡的計劃時,lumos(含 impact 子行程與目標架構段)應只在會談 repo 跑 git:PATH 前置一支假 `git` 外包腳本,記下每次呼叫的 `-C` 值與工作目錄後轉給真的 git,每一筆解析後都應在會談 repo 根底下,沒有一筆落在計劃所在的另一個工作樹。[test:t_dispatch_lens_spec_commit_git_only_in_session]
- [S10] 當值是工作樹路徑時,檢查應與現在相同(絕對路徑、不在 `docs/*-knowledge/` 底下的計劃、超過 1MB 的計劃都照讀,rc 與 stderr 不變),失敗時 `--json` 應多印 `lens_fail`(`spec_missing`、`spec_outside_repo` 或 `no_knowledge`)與 `spec_source: worktree`。[test:t_dispatch_lens_spec_worktree_unchanged_plus_code]
- [S11] lumos 印得出的 `lens_fail` 代碼集合應等於掛鉤 `LENS_FAIL_REASONS` 的鍵集合(十一個)。[test:t_dispatch_lens_fail_codes_match_hook]

掛鉤層(照既有 `fire()` 替換 `subprocess.run`,回假的 lumos JSON):

- [S12] 當 lumos 回提交寫法成功列時,掛鉤應記 kind `ok`、note `spec_commit`;掛鉤應只呼叫一次 lumos、把標記值原樣傳過去,不應呼叫 git。[test:t_dispatch_lens_hook_spec_commit_event]
- [S13] 當 lumos 回 `spec_source: worktree` 與 `spec_missing` 或 `spec_outside_repo` 時,說明行應用計劃版措辭、帶 spec-freeze 繞法,不應出現「範圍」或 `<範圍>`;事件應記 kind `ok`、note `spec_worktree <代碼>`。[test:t_dispatch_lens_hook_spec_worktree_fail_notice]
- [S14] 當 lumos 回 `spec_source: commit` 與 `spec_rev_missing` 時,說明行應用計劃版措辭、不帶繞法,事件應記 kind `ok`、note `spec_commit spec_rev_missing`;回 `no_knowledge` 時應記 kind `error`。[test:t_dispatch_lens_hook_spec_commit_fail_notice]

`lumos spec-freeze`:

- [S15] 跑完之後,`--out` 的內容應與那個提交裡那份計劃的 blob 位元組相同,也與工作樹上的計劃位元組相同;印出的那一行應等於 `LUMOS-SPEC: <提交>:<路徑>`;那個提交的父提交應是 HEAD;把那一行餵給 dispatch-lens 時回的 `spec_blob` 應等於快照的 blob 編號。[test:t_spec_freeze_snapshot_matches_commit]
- [S16] 跑前跑後,`for-each-ref` 的輸出、真的 index 檔位元組、HEAD 與目前分支都應不變;工作樹裡另一個沒提交的改動不應進那個提交(tree 只比 HEAD 多這份計劃)。[test:t_spec_freeze_leaves_refs_and_index]
- [S17] 當 repo 裝了會留記號的 pre-commit、commit-msg、post-commit 掛鉤與會留記號的 clean 過濾器時,跑完之後記號都不應存在。[test:t_spec_freeze_runs_no_hooks_or_filters]
- [S18] 當計劃路徑含空白、不合路徑規則、不是一般檔,或 repo 沒有 HEAD 時,spec-freeze 應回 rc 非 0、不建提交(物件庫的提交數不變)、不寫 `--out`。[test:t_spec_freeze_rejects_bad_path]

- 測試怎麼搭:S1、S5–S9 用 `git worktree add` 造真的第二個工作樹,在那裡用 spec-freeze 或提交放計劃;會談目錄留在主工作樹,而且停在不含那個提交的分支上(在同一棵樹上跑,不論實作照哪種解讀都會綠)。lumos 層與掛鉤層分開測,不跑端到端:掛鉤找的是全域 lumos,端到端會依機器上裝的版本紅綠不定。不換 `HOME`。檔名只用 NFC。

## 實務隱患

- 守衛面:掛鉤會改寫子代理的派工詞,也是錨點清單裡的檔。這次不新增去別的目錄跑 git 的路:dispatch-lens 讀計劃只在會談 repo 跑 `rev-parse`、`ls-tree`、`cat-file`(含 `_nodehome_cat_blobs_capped` 的批次讀),都用 `<編號>:<路徑>` 讀物件,不讀 index、不跑過濾器(第三輪正確性席實測 textconv 不執行),跟代碼審那條路(在會談 repo 算別的工作樹的提交)同一個風險面。
- 提交編號是派工詞給的:只收完整編號、解出必須等於輸入,最壞是指到會談 repo 裡別的完整提交、附上那份計劃的節點——附加段開頭印提交與 blob 的前 12 碼,席位對得上 spec-freeze 印的那一行與 rN-dispatch.json 記的 `spec_commit`。
- spec-freeze 會寫物件庫:`hash-object -w --no-filters` 與 `commit-tree` 只新增物件,不動 ref、真的 index 與分支,不跑提交掛鉤與過濾器。有人把 `gc.pruneExpire` 設成 now 或手動 `git gc --prune=now`,當輪的提交會被清掉,鏡頭回 `spec_rev_missing`、有說明行看得見;重跑 spec-freeze 即可。
- 節點內容讀會談目錄的版本:計劃所在分支改過的 Systems 節點,席位看到的是會談目錄那份;附加段頭寫明是哪個版本。
- 過渡期多一次呼叫:舊 lumos 的設計審失敗是 stdout 空加 rc 2,掛鉤會當成舊版、拿掉選配旗標再叫一次;新 lumos 失敗印 JSON 列,不再白跑。只吃預算,不影響結果。
- 已排除:金流:不碰。
- 已排除:對外送出:只在本機跑 git 與 lumos。
- 已排除:不可逆:還原提交即回到只認工作樹路徑;spec-freeze 建的提交不掛 ref,gc 會清;派工詞多出的提交寫法,舊版會當成工作樹路徑找不到、照舊不附。
- 改了錨點清單裡的掛鉤與測試檔,提交前要 `lumos anchor approve`。

REVISIT:2026-11-15 查事件帳與席報告,有沒有用專案內 `scripts/lumos` 跑 spec-freeze、全域 lumos 還是舊版,以致提交寫法被舊 lumos 當成工作樹路徑、靜默不附;有就讓 spec-freeze 比對自己與 `_trusted_lumos` 找到的那支是不是同一份、不同就拒絕。
REVISIT:2026-12-15 數附加段裡「只在那個提交裡,會談目錄還沒有這篇」與「節點內容是會談目錄的版本」出現的次數,多到席位常拿不到該審的版本,就改成附提交裡那份內容。

## 回退

照順序:
1. 還原程式、掛鉤、範本與手冊的提交(範本與掛鉤一起退,免得範本還叫人跑 spec-freeze、掛鉤卻不認)。
2. **全域 lumos 也要退並核對**:掛鉤與編排者敲的都是 `_trusted_lumos` 找到的那支(PATH 上的 `lumos`,本機是 `~/.local/bin/lumos` 指到 `~/harness/lumos-toolchain`;沒有才用 `$LUMOS_HOME`)。把那個來源拉到還原後的提交,核對 `lumos spec-freeze --help` 回「沒有這個子命令」。只退掛鉤不退這支,會留下舊掛鉤配新 lumos,指紋核對卻顯示已回原狀。
3. 每個消費專案跑 `lumos update`,再 `lumos anchor approve --note "<為什麼>"` 並提交簽名檔。`_sync_global_hooks` 用 `copy2` 無條件覆寫 `~/.claude/hooks/`、不比版本,**最後一個跑 update 的專案會把它的掛鉤寫回 `~/.claude/hooks/`**:所以第 2 步先做,各專案拉到的來源就已經是退過的版本;全部跑完再核對 `~/.claude/hooks/dispatch-lens-hook.py` 的指紋等於還原後的版本。之後有人從還沒退的分支或舊工作樹跑 `lumos install`、`lumos update --no-pull`,會把新版寫回去;核對不相等就從已退的專案再跑一次 `lumos update`。
4. 還有派工詞帶著提交寫法的進行中迴圈:舊版 lumos 當成工作樹路徑找不到、不印失敗代碼,不會有說明行;編排者在回退當下手動 `lumos dispatch-lens --spec <工作樹路徑>` 貼固定席,之後照退回的範本寫工作樹路徑。
5. 撤掉本計劃的 REVISIT 與 RETIRE-IF 行,或在行尾標 `[closed:<日期> 已回退]`,免得 doctor 到期叫人去數一個已不存在的欄位。事件帳裡已記的 `spec_commit`、`spec_worktree` note 留著;回退前 grep 一次確認沒有讀端把這兩個字首當固定格式解析。
6. spec-freeze 建的不掛 ref 提交不用手動清,gc 會清。

## 審計修正紀錄

- r1 前掃(2026-10-14):9 條(語意命中 5、③ 2、② 1、存在命中 1)直接修進本文:Codex 跨 repo 認領領不到,改寫成不做;重複標記的處理前後矛盾,統一成不算;信任檢查要先讀 `.git` 檔、不能先跑 git,另寫資料夾版不改逐字複本;更正「跟會談目錄受到的保護相同」(會談目錄現在沒有檢查);設計審失敗沒有說明行,補三個代碼;原因代碼拆成六個並與 lumos 的表分開;舊裁定兩處加會談 codex-harness 標作廢;路徑可以有空白。前掃紀錄在 `governance/review-reports/派工鏡頭可指定目標repo/r1-intake.md`。
- r1(2026-10-14,6 席):32 條/blocking 11/信任靠權限位元擋不住 `.git` 裡的 `commondir`、權限放寬的設定檔、從沒用過的下載 repo,又會在 `/tmp` 底下誤殺;標記寫歪會退回會談目錄附上錯的樹;成功時看不出用的是哪個 repo;被拒時連角色卡一起丟;記帳量不到撤除條件;舊裁定照字面作廢會把還有效的決策一起作廢;回退「無害」不成立;全數折入:改成登記制(會談 repo 的工作樹加裝過 lumos 的專案)、寫歪與重複都不算也不退回、成功印來源行、被拒照附角色卡、掛鉤自己不再跑 git、事件 note 固定字首、只作廢被推翻的那一格、手冊要改的地方列全、回退改成清單。席報告在 `governance/review-reports/派工鏡頭可指定目標repo/`。
- r2(2026-10-14,3 席):19 條/blocking 14/登記清單放哪、誰能寫、拒絕說明本身誘導登記、圍欄裡的標記被靜默忽略、被拒時取角色卡會用錯的樹、會談本身是工作樹時怎麼列工作樹、測試換 `HOME` 會讓掛鉤找不到 lumos;全數折入:整類拿掉——不再讓派工詞指定路徑,改成設計審標記收 git 原生的 `<提交>:<路徑>` 寫法,在會談 repo 從物件庫讀計劃(同一個 repo 的工作樹共用物件庫);跨 repo 照舊裁定不做。席報告在 `governance/review-reports/派工鏡頭可指定目標repo/`。
- 註:前兩輪寫的標作廢、登記清單等做法已整類撤回,舊裁定照舊成立。
- r3(2026-10-14,6 席):46 條/blocking 16/短編號會被同名分支搶走、路徑只做字串檢查會把目錄與符號連結讀成計劃、掛鉤說不解析卻要分辨寫法、程式檔存在用提交判而牽連用會談目錄算、快照與提交沒綁在一起、回退漏掉全域 lumos;全數折入:只收完整提交編號、提交那條路新增路徑規則並只讀一般檔、讀計劃收斂成一支、存在照會談目錄判並另列只在提交裡的、lumos 回 `spec_source` 給掛鉤讀、新增 `lumos spec-freeze` 同時產生提交與快照、回退加全域 lumos。收貨紀錄在 `governance/review-reports/派工鏡頭可指定目標repo/r3-intake.md`。
