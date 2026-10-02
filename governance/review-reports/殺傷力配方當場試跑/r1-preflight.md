# 殺傷力配方當場試跑_計劃 設計審前置掃描

(行號對照 negguard 工作副本的 scripts/lumos,為大約值。全程只讀程式碼,沒跑任何指令實驗。)

## ① 未定義的詞

命中 4 處(只列會讓接手的人卡住的):

1. 「短身分」:計劃沒說 `--id` 是「整串相等」還是「前綴比對」。程式裡的實況:印出來的是 `_kill_recipe_id(...)[:12]`(12 字元),kill-rm 收的是 8~64 個十六進位字元、用 `startswith` 比對、對到多條不同身分就擋(`_guard_kill_rm_locked` 約 14527)。guard kill 的 `--id` 若只做「在清單裡」(相等),使用者貼 kill-rm 認得的 8 字元前綴會對不到;若做前綴,又要不要擋 <8 字元、對到多條怎麼辦,計劃都沒寫。接手的人會各自發明一套。
2. 「弱證據」:計劃〈做法〉③ 與 S3 用它指 `killed_unattributed`、`timed_out_weak` 這類「判定」,但 kill-log 另有一個布林欄位 `weak`(整套一起跑、flaky 平台、筆記有未提交改動、修改時間沒錯開都會設成 true)。兩件事不同。一筆 `verdict=survived` 而 `weak=true` 的紀錄,要不要列?計劃沒說(見 ④ 第 7 項)。
3. 「最近一次真跑」「ts 最新」:沒說同秒、`ts` 缺失或型別不對時怎麼辦(見 ④ 第 4 項)。
4. 「這幾條配方指著這次改過的檔」:配方 `file` 是相對「配方平台所在 repo 最上層」的路徑(kill-add 的 `--file` 說明、`_kill_plat_top`),不是相對 vault 所在 repo 根。計劃沒定義「指著」要不要先確認平台根就是 fix-check 的 repo(見 ④ 第 8 項)。

## ② 壞引用

未命中壞引用。逐一 grep 確認都存在:

- 函式:`_kill_recipe_id`(13859)、`_guard_kill_rm_list`(14477)、`_backing_kill_rows`(41079)、`_codeloop_record_valid_ex`(40384)、`_kill_p2_scan`(14181)、`_kill_p2_one`(14213)、`cmd_guard_kill`(14823)、`cmd_guard_kill_add`(14241)、`cmd_guard_kill_rm`(14455)、`cmd_loop_fix_check`(11929)、事件名 `check-p2`(doctor 約 2960,白名單約 7303)。
- 筆記節點:`Systems/guard-kill`、`Systems/代碼審修正關卡`、`Projects/殺傷力配方修補體驗_計劃`、`Projects/殺傷力配方失配提醒_計劃`、`Projects/漂移防治路線圖_計劃`、`Projects/代碼審修正關卡_計劃` 都在。
- 指令速查檔:`skills/lumos-project-notes/commands/06-代碼審與推送.md` 在,且含 guard kill。
- 外部引用(rtb 提交 c531ac7、rtb 的 `Issues/存量筆記漂移等工具修復`)在本 repo 查不到,屬外部,不算壞引用。
- 計劃說「kill-add 的『下一步』字面有測試釘著的話要同步」:grep `scripts/test_lumos.py` 沒有任何斷言釘「跑殺傷力驗證」或那行「下一步」,所以目前沒有要同步的測試。該句可改成「已查過,沒有測試釘它」。
- 新測試名 `t_guard_kill_only_ids`、`t_guard_kill_add_try`、`t_doctor_p2_lists_survived`、`t_fix_check_recipe_rerun_note`:現在都不存在,是新的,不算壞引用。

## ③ 範圍自相矛盾

命中 3 處:

1. 〈做法〉② 說回傳碼「killed 系列 0、survived 1、跑不起來 2」,但 `cmd_guard_kill`(約 14985~15003)的實際規則是:任一 survived=1;drifted/abort/error 且無 survived=2;**全部都是弱證據(`killed_unattributed`/`timed_out_weak`)=1**;有強 killed 且無錯誤=0。所以「killed 系列 0」不成立,全弱證據也回 1。這跟 S2「殺不掉時回 1、印出判定與 kill-rm 指令」會打架:rc=1 不等於 survived(見 ④ 第 2 項)。
2. 〈範圍〉不做「不改 guard kill 的判法、回傳碼語意」,但 `--try` 要「判 survived 時另印一行」,而 `cmd_guard_kill` 只回 rc、不回逐條判定,呼叫端分不出 survived 與全弱證據。要做就得動 `cmd_guard_kill`(加一個回傳結果的參數)或讀 kill-log 尾巴,範圍要明說。
3. RETIRE-IF 說「看 kill-log 每次真跑的配方條數:一次只跑一條的紀錄為零」。kill-log 每行沒有「這次是 --id 還是 --try 跑的」欄位,而計劃自己又說不改 kill-log 欄位;只能靠同一個 `ts` 的行數反推,而且單配方的筆記跑整篇也是一條。這個撤除條件量不出來。要嘛撤除條件改成別的可量測訊號,要嘛承認量不到、改成問 rtb(10-15 的 REVISIT 已涵蓋)。

〈回退〉〈實務隱患〉〈條款〉之間沒有發現其他互相打架。

## ④ 機械宣稱驗語意

格式:原句 → 程式實際行為 → 判定 → 建議。

### 1. guard kill 的配方過濾與 `--id` 要掛哪、`_kill_recipe_id`

- 原句:「新旗標 `--id`(可重複,也收逗號分隔),值是 kill-rm 與 guard kill 結果行印的那個短身分(`_kill_recipe_id`)。給了就只留短身分在清單裡的配方;跟既有的『合約片段』過濾可以一起用」
- 實際:合約片段過濾在 `cmd_guard_kill` 約 14841~14842(`recipes = [r for r in recipes if invariant_substr in r.get("invariant", "")]`),緊接著判空回 2。`_rid` 在約 14865 之後才算:`{**r, "_rid": _kill_recipe_id(str(rel), r)}`,用的是原配方 `r`、節點是 `str(rel)`,跟 kill-rm(`_guard_kill_rm_locked`:`_kill_recipe_id(str(rel), r)`)與 `_guard_kill_rm_list` 是同一個函式、同一組參數。結果行印 `id=` 取 `[:12]`(約 14975)。**成立**:同一個值。
- 掛法:`--id` 要加在 argparse 的 `gk`(約 42430~42436)並在 dispatch(約 43367)傳進 `cmd_guard_kill` 的新參數;過濾要放在合約片段過濾之後、`if not recipes` 之前,且要在 `_rid` 轉換之前用原配方算身分(之後 `{**r}` 的 dict 也能算,但原配方最直接)。
- 注意兩點:(a) 現有合約片段過濾用 `r.get(...)`,清單裡有非物件元素會崩(已有 Issue「guard kill遇到格式壞的配方整支崩潰」,不在本計劃範圍)。`--id` 過濾若放在它前面、且用 `_kill_recipe_id`(它本來就處理非物件),則給了 `--id` 時格式壞的元素會先被濾掉,不會崩,但這是副作用,測試要知道。(b) 比對語意見 ① 第 1 項,要寫死。
- 建議(語意類):「給了就只留短身分在清單裡的配方」→「給了就只留完整身分以該串開頭的配方;每個給的串要是 8 個以上十六進位字元(同 kill-rm,不合就回 2),對到零條回 2,對到兩條以上不同完整身分也回 2 並列出;同一完整身分的重複配方(手改造成)會一起跑,S1 的『結果只有一筆』只在無重複時成立」。

### 2. 找不到時「共用 `_guard_kill_rm_list` 的列法」

- 原句:「給的短身分有任何一個在這篇找不到 → 回 2,印『找不到』的是哪幾個,並照 kill-rm 不帶 --id 時的樣子列出這篇每條配方的短身分(共用 `_guard_kill_rm_list` 的列法)」
- 實際:`_guard_kill_rm_list(env, node)`(14477~14507):參數只有 `(env, node)`;自己再做一次 `env.find` 與 `_kill_read_recipes`;列表**印到標準輸出**;最後一行固定印「移除:lumos guard kill-rm <節點> --id <短身分>」(約 14505)。**部分成立**:可以呼叫,但 (a) 結尾那行是 kill-rm 的移除提示,放在 guard kill 的「找不到」訊息後面會誤導(叫人去移除而不是重跑);(b) 它印 stdout,`--json` 模式下會污染 stdout(合約 `t_guard_kill_json_purity` 明文只收窄「成功跑完 rc 0/1」,rc2 早退不印 JSON 算範圍外,所以不違約,但 --json 呼叫端會在 stdout 看到非 JSON);(c) 重複 find 與讀檔一次,無害。
- 建議:把列行迴圈(14485~14504)抽成 `_guard_kill_rm_rows(rel, recipes)` 之類共用小函式,`_guard_kill_rm_list` 與 guard kill 的找不到分支共用;找不到訊息走 stderr,結尾提示依呼叫端換成「重跑:lumos guard kill <節點> --id <短身分>」。計劃那句「共用列法」改成「共用逐行格式、結尾提示由呼叫端給、輸出到標準錯誤」。

### 3. `cmd_guard_kill_add` 寫完後:「下一步」那行、新配方短身分、同行程呼叫 guard kill

- 原句:「寫入成功時,原本那行『下一步: lumos guard kill 跑殺傷力驗證』改成印出只跑這一條的指令」
- 實際:該行在 `cmd_guard_kill_add` → `_guard_kill_add_locked` 末尾約 14410,**在寫入鎖裡**印。同一函式在約 14320 已算 `key = _kill_recipe_key(str(rel), invariant_substr, file, old)`(判重用),對字串欄位齊全的新配方就等於 `_kill_recipe_id(str(rel), recipe)`,所以手上有資料可算 `key[:12]`。**成立**。只更新 covers 那條路(約 14405~14407)另有一行「下一步」,計劃說照舊,與程式一致。
- 「`--try`:寫入成功後,在同一個行程裡呼叫 guard kill」:`cmd_guard_kill_add` 約 14283~14287 在鎖外迴圈 `_kill_add_warn`,之後 `return rc`。`--try` 該掛在這裡(鎖外、`_kill_add_warn` 之後)。`_guard_kill_add_locked` 回傳只有 rc,要把新配方帶出來:`warn_box[0]` 就是這次寫入(或只更新 covers)的那條 recipe,可直接在外層算 `_kill_recipe_id(str(rel), warn_box[0])[:12]`。**成立,但計劃沒說怎麼把短身分帶出鎖外**,建議明寫「用 warn_box 帶出,在鎖外算」。
- 同行程呼叫 `cmd_guard_kill(env, node, ids=[sid])` 的副作用:不拿筆記庫寫入鎖(它不讀寫鎖),所以放掉鎖後呼叫沒有鎖衝突;它會:印結果行與總結到 stdout、`survived` 時印一行到 stderr、寫 kill-log(約 14926~14945,是預期的)、讀工作目錄的筆記(`env.vault / rel`,見下)。沒有全域狀態需重置。**成立**。
- 但有兩個計劃漏掉的後果:(a) kill-add 剛把筆記改成未提交,guard kill 約 14902 `dirty` 判的是**平台 repo 整個 `git status --porcelain`**,筆記在同一個 repo 時必定非空,所以 `--try` 每次都會先印「⚠ … repo 有未提交變更——不會進沙盒(kill 以 HEAD 為基準),配方/測試需先 commit」(stdout),且 `node_dirty` 一定為 true,這次 kill-log 每一行 `weak=true`。這不是 bug,但 `--try` 的使用者每次都會看到這行警告,文件要先講。(b) 這次的程式是 HEAD,不是工作目錄:若使用者剛改了程式還沒提交(rtb 重寫配方的典型情境:先改程式、再重寫配方),`--try` 會判 drifted(rc 2)。〈做法〉② 已提「對 HEAD 跑」,但建議 rc 2 且工作目錄有未提交改動時多印一句「程式改動沒提交,先提交再試」。
- guard kill 讀配方:`_kill_read_recipes(env.vault / rel)` 約 14837,讀**工作目錄**的筆記,不是 HEAD;所以 kill-add 剛寫完、尚未提交的新配方,guard kill 看得到。**成立**(計劃那句「筆記剛寫還沒提交時…弱證據」與程式一致)。
- 原句:「寫入成功時用 guard kill 的回傳碼(killed 系列 0、survived 1、跑不起來 2)」→ 見 ③ 第 1 項:全弱證據也是 1。**不成立(部分)**。
- 原句:「判 survived 時另印一行:配方已寫進筆記,換位置重寫就 kill-rm 再重加」→ `cmd_guard_kill` 不回逐條判定。★動到核心★(`--try` 的判 survived 靠這個):
  - 修改前:「判 survived 時另印一行」(由呼叫端 `cmd_guard_kill_add` 推斷)。
  - 修改後:二選一寫進計劃——(甲)`cmd_guard_kill` 加一個選用參數 `_out=None`(傳入 list,把 `results` 的 verdict 放進去),不改判法與回傳碼;(乙)`--try` 結束後讀 kill-log 尾端、取 `recipe_id` 等於新配方、`ts` 等於本次的那行。甲簡單且不依賴檔案寫成功(kill-log 寫失敗時只會印警告,乙就讀不到)。並把〈範圍〉的「不改 guard kill」改成「不改判法與回傳碼,只多一個回傳結果的選用參數」。另外「換位置重寫」的提示只在 verdict 為 survived 時印;全弱證據(rc 1)要另一句(「紅燈沒歸因到綁定測試,不是殺不掉」)。
- S2 條款「殺不掉時應回 1」:若測試用的是 survived 配方,成立;但條款文字應限定「判定是 survived 時」,否則和全弱證據 rc 1 混在一起。
- 另一個漏洞:`--try` 搭配「只更新 covers」那條路(同一配方已存在、只改 covers)時要不要試跑?計劃沒說。程式裡該路也把 recipe 放進 `warn_box`,所以技術上可跑;但沒新配方,建議明寫「`--try` 在只更新 covers 時照樣跑那一條」或「不跑、印一行說明」。

### 4. `_backing_kill_rows`:欄位、`ts`、對回配方、壞行、「取 ts 最新一筆」

- 原句:「另讀殺傷力帳本(`_backing_kill_rows`:型別不對、`head_sha` 不是完整 sha、對不回筆記現有配方的行都略過),每條配方取帳上 `ts` 最新的那一筆」
- 實際(41079~41133):讀的是 `<repo_root>/docs/.kill-log.jsonl`(寫入端 `cmd_guard_kill` 約 14931 寫 `env.vault.parent/.kill-log.jsonl`;兩者在標準 `docs/<x>-knowledge` 佈局下同一檔)。逐行 `_drift_jsonl_parse` 壞行(非 JSON、非物件)直接略過。過濾:`test/platform/verdict/head_sha/recipe_id` 要是字串、`weak` 要是布林、`head_sha` 要是 40 或 64 位十六進位、`recipe_id` 非空。再經 `_backing_note_recipes` 用 `recipe_id` 對回該 `node` 筆記**工作目錄**裡的配方(身分算法同 `_kill_recipe_key`),對不到就丟;對得到的行,**只把 `covers` 與 `note` 改成筆記那條的值**。回傳行 = 原 kill-log 的整個 dict:有 `ts`(未驗證型別)、`node`、`commit`、`invariant`(**取自帳檔,不是筆記**)、`test`、`platform`、`verdict`、`tail`、`flaky_risk`、`covers`、`recipe_id`、`head_sha`、`weak`、`note`。**部分成立**:「型別不對、head_sha 不是完整 sha、對不回現有配方的略過」成立;但是——
  - (a) 計劃〈做法〉③ 要列「合約前段」。回傳的 `invariant` 是帳檔的值,而 `_backing_note_recipes` 的註解(41101 附近)明講不信帳檔那一行(kill-log 在提交裡誰都能改)。**要用筆記那條配方的 invariant**,不要用 row 的;且要經 `_kill_show` 才印。`ts` 沒驗型別、也不是 sha 那種被正則擋過的字串,印進 doctor 前要先驗是字串並去控制字元(取日期前 10 字元)。只有 `head_sha` 被正則擋過,可直接 `[:8]`。
  - (b) 該函式不篩筆記的 `type`/`status`:P2 `_kill_p2_scan` 會跳過 verification 型與 superseded/stale 的筆記,`_backing_note_recipes` 不會。若直接拿它的結果列 survived,會多列這些該跳過的筆記。要在列的時候照 `_kill_p2_scan` 同一組跳過規則(見第 6 項建議抽共用)。
  - (c) 「取 ts 最新」:`ts` 是 `datetime.now().isoformat(timespec="seconds")`(約 14822),本機時間、無時區、精度到秒。同一次 guard kill 的所有行共用同一個 `ts`;同一個配方在同一次裡只會一行(除非手改造成重複),所以同一配方同秒兩行幾乎只發生在兩次執行同秒(`--try` 之前才跑完一次,每次至少 1.4 秒,實際不太可能)。但 `ts` 沒型別驗證、舊紀錄可能缺。既有的 `_backing_judge_groups` 取「最後一筆」是用**檔內順序**(`groups[rid][-1]`),只有跨配方比 `latest` 才用 `ts`。**建議**:改成「取檔內順序最後一筆」,不要比 `ts`(同秒平手、型別不明、改系統時鐘都會錯);跟既有背書算法一致。
- 另:`_backing_kill_rows` 另外讀每個被引用節點的筆記一次,doctor 的 P2 迴圈本來也讀一次,多一輪檔案讀取,可接受,但別在每條配方裡重呼叫它,要呼叫一次、自己分組。
- 〈做法〉③ 說「判定是 `survived` 的列出來」:帳上的 `weak` 為 true 的 survived(例如筆記未提交、整套一起跑、flaky 平台、**`_mtime_unsure`:編譯快取吃到舊檔,這種 survived 有可能是假的**)也會被列。S3 條款「只有弱證據的配方應不列」沒釐清是 verdict 還是 `weak` 欄。建議(語意類):「判定是 survived 的列出來」→「最新一筆 verdict 是 survived 的列出來;`weak` 為 true 的 survived 照列但行尾加『(證據弱:筆記當時未提交或有修改時間沒錯開,先重跑)』;其他 verdict(killed、killed_unattributed、timed_out_weak、drifted、abort、error)最新一筆時不列」。並注意 drifted/abort/error 若是最新一筆,會蓋掉更早的 survived(該配方已另有原文對不上的提醒,這樣合理,但要寫進條款)。
- 另一個與既有算法的差別:既有背書算法是「同版本上任何一次 survived 就判 none」;本計劃是「只看最新一筆」。同一版本先 survived 後 killed(例如 flaky 平台)時兩邊結論不同。這是設計取捨,建議在〈做法〉③ 一句話說明為什麼不同(P2 是提醒、背書是閘)。

### 5. `_codeloop_record_valid_ex` 用 head_sha 對現在 HEAD 判「之後動過程式」

- 原句:「那次跑的版本跟現在的 HEAD 之間動過程式(`_codeloop_record_valid_ex` 判無效或判不了)時,這行尾端加『(之後程式改過,先重跑)』。每個版本只判一次(快取),整段最多判 50 個不同版本」
- 實際(40384~40445):簽名 `(repo_root, rec_sha, marker_sha, timeout=None)` 回 `(ok, why, unsure)`。`rec_sha == marker_sha` → `(True, "同版本", False)`;不是祖先 → 無效;其他非零 → 找不到(淺 clone → unsure=True;完整歷史 → 無效);`git diff --raw` 的檔案**全是簿記檔或簿記資料夾**才算有效,**任何其他變更(含 `docs/*.md` 筆記、其他程式)都回 `(False, "之後動了代碼(非純簿記增量)", False)`**。判不了(逾時、讀不懂)回 `unsure=True`。**部分成立**:它判的是「之後有沒有動過任何非簿記的檔」,不是「配方指著的那支程式改了沒」。
- 後果:`_BOOKKEEPING_FILES` 只含 `docs/.kill-log.jsonl` 等帳檔、`_BOOKKEEPING_DIRS` 只含卷證資料夾。筆記 .md 不是簿記。所以只要那次真跑之後有**任何一個**提交動了任何非簿記檔(包括不相干的文件、別的功能),所有 survived 行都會帶「(之後程式改過,先重跑)」。在一個天天有提交的 repo 裡,幾乎每一行都會帶這句,訊息等於零資訊,只有「剛跑完還沒再提交」的那一行不帶。
- 另一個坑:kill-log 的 `head_sha` 是**平台根所在 repo** 的 HEAD(`marks[-1].update(head=ghead)`,ghead 取自 `proot`),而本函式用 `repo_root`(vault 所在的 repo)。多平台、平台根在另一個 repo 時,`merge-base --is-ancestor` 非 0/1 → 找不到 → 一律判無效或判不了,加註變成噪音。
- 逾時:單次 git 上限 `_disp_git_timeout()` 預設 8 秒、每個版本最多 3~4 支 git;計劃只有「最多判 50 個版本」,沒有總時間預算。最壞情況 50 × 數支 × 8 秒會讓 doctor 卡數分鐘。既有的背書算法有 `_BACKING_BUDGET`(20 秒)與 deadline 可抄。
- 建議(語意類,不動核心):
  - 修改前:「那次跑的版本跟現在的 HEAD 之間動過程式(`_codeloop_record_valid_ex` 判無效或判不了)時,加『(之後程式改過,先重跑)』」。
  - 修改後:「那次跑的版本到現在的 HEAD 之間,這條配方指著的 `file` 變過(`git diff --quiet <head_sha> HEAD -- <file>` 非 0)、或判不了(版本找不到、逾時)時,加『(配方指的檔之後改過,先重跑)』」。這更貼近使用者真正要知道的事、每個 (版本, 檔) 一支 git、更便宜,且不受不相干提交與簿記判法影響。若堅持沿用 `_codeloop_record_valid_ex`,至少把標示改成「(之後有提交,先重跑)」並加總時間預算(沿用 `_BACKING_BUDGET` 與 deadline),且只拿平台根與 vault 同一個 repo 的行判,其餘直接標「先重跑」。
  - 「判不了」時它回 `unsure=True`;計劃把「無效」與「判不了」併成同一個標示,這個併法可以,但要在條款寫清楚。

### 6. doctor P2 段:新清單併法、軟提醒計數、`check-p2` 事件、「原文已對不上的不重複列」

- 實際:doctor P2 在約 2943~2970。`_kill_p2_scan(env.vault, notes, repo_root)` 回 `{"cfg_err", "items":[(stem 清單, 文字)], "total"}`。顯示分三支:`cfg_err` → 一個 `warn_soft`;`items` 非空 → 一個 `warn_soft` 並對每個涉及的 stem 各記一筆 `check-p2`(`kind="warned"`);否則 `ok(...)`。`warn_soft`(1354)每呼叫一次 `segs+1`、`lines+=len(lines)`,**預設每段最多印 3 條**(`_SOFT_CAP`),其餘要 `--verbose`。
- 影響:(a) 若 survived 清單併進同一個 `items`,列表過 3 條就被收成「另 N 條」,且與原文對不上混在同一個標題「…的原文對不上程式(guard kill 跑到會判 drifted 或擋下)」下,標題語意就錯了(survived 不是對不上)。**建議另開一個 `warn_soft` 呼叫,標題獨立**(例如「有 N 條殺傷力配方最近一次真跑判 survived」),軟提醒段數+1、行數照實累加;`check-p2` 事件另加 `kind` 或在 `nodes` 外加一個區別欄(例如 `kind="survived"`),不然事件消費者分不出兩種。
  (b) 「原文已經對不上的那條不重複列」要靠什麼判:`_kill_p2_one` **回傳判定狀態 code**(ok/hits/missing/path/malformed/noplat/noroot/cfg…),但 `_kill_p2_scan` 約 14199 丟掉了回傳值,`st` 裡也沒存。要在 `_kill_p2_one` 呼叫處把「code 不是 ok 的配方的 `(rel, 完整身分)`」收進 `st["bad_ids"]`,再回傳給 doctor。這是動 `_kill_p2_scan`/`_kill_p2_one` 的回傳形狀(目前只回 dict 三鍵,測試可能釘著,要查 `t_doctor_p2*` 之類),計劃沒寫。另外 `code in ("noplat","noroot","cfg")` 這幾種是「判不了」而非「對不上」,也要決定要不要跳過;最簡單是「只要 P2 本次對這條有列任何一行就不列 survived」。
  (c) `cfg_err` 分支:設定檔讀不了時,P2 整段 skip;survived 清單不依賴設定檔,但用到 `_backing_note_recipes`→`_kill_read_recipes`,與設定無關,可獨立顯示;計劃沒說這分支要不要列,建議列。
  (d) 跳過規則:`_kill_p2_scan` 的 verification 型 / superseded/stale / `kill_recipes` 欄缺失 的判斷是**內嵌在迴圈裡**(14187~14192),沒有獨立函式。③ 與 ④ 都需要同一組規則。**建議**:把這三行抽成 `_kill_p2_skips(note)`(純重構,行為不變),三處共用,並用一支測試釘住三處同口徑。
  (e) 吞吐:doctor 整段已有例外兜底;新清單也要包 try,失敗只加一行「survived 清單算不出來」,不要讓它拖垮原文對不上的結果。

### 7. `cmd_loop_fix_check` 的 `changed` 與 `notes` 輸出、掃配方用哪支函式

- 原句:「`lumos loop fix-check` 算出 `base..修正後` 改到的檔之後,掃筆記裡每條殺傷力配方的 `file`(照 P2 的跳過規則…),有指到改過的檔的,在輸出的提醒段加一行…接每條一行 `lumos guard kill … --id …`(最多列 10 條…)」
- 實際:`changed` 在約 12010:`set(_fix_git_z(rr, "diff", "--no-renames", "--name-only", "-z", base, head))`,`rr` 是 `_vault_repo_root(env)`(從 vault 往上找 `.git` 的那層),所以路徑是相對 repo 最上層;`--no-renames` 讓刪除與改名的舊路徑也在集合裡。`notes` 是一個字串 list,人讀輸出時每項印成一行 `  · {n}`(約 12185),`--json` 時整個 `notes` 陣列原樣進 JSON。**成立**(`changed` 可用)。
- 但:(a) `notes` 是「一項一行」,計劃的「一行提示接 10 行指令」若塞成一個多行字串,第二行起沒有「  · 」前綴;若分 11 個 notes,`--json` 的 `notes` 多 11 項(計劃說不寫事件欄位,但 `--json` 的 `notes` 是輸出的一部分,會變)。要寫明:一條說明 + 每條指令各一個 note(最多 10 + 一條「還有 N 條」)。 (b) fix-check 在「這輪沒有要修正紀錄的折入」時約 11978 就早退(`need` 為假),此時不印提醒。計劃說「修正關卡在修正改到配方指著的檔時」,實際只在 `need` 為真的輪次才會跑到,要在條款寫清楚(S4 的測試輪要是有要修正紀錄的輪次)。 (c) `file` 是相對**配方平台所在 repo 最上層**,`changed` 是相對 `rr`。只有「平台 repo 最上層 == rr」時能直接比。平台根在另一個 repo、或同名檔碰巧存在時會誤報。**建議**:用 `_kill_check_ctx(rr)` + `_kill_plat_top(ctx, pentry["root"])` 取平台 repo 頂,與 `rr`(都 `realpath`)不等的配方不比。這比 `_kill_recipe_judge` 輕(不讀 blob、不判原文),**掃配方不要用 `_kill_p2_scan`**(它回的是「有問題的」文字、不回配方清單,且每條都讀 HEAD 檔並判原文,多餘);要新寫一個小迭代器(用第 6(d) 項抽出的跳過規則 + `_kill_read_recipes`),輸出 `(節點 rel, 完整身分, file, 平台)`。 (d) 讀的是工作目錄筆記;fix-check 驗的是提交(`head`)那一版。工作目錄筆記有未提交改動時,提醒的配方與提交裡的不同,行為上是提醒,可接受,但可在已有的「工作目錄沒提交的改動不算」那條 `notes` 旁不另處理。 (e) `env.notes` 在 fix-check 可用(`Env.notes = load_vault(vault)`,約 654),不需另載。
- 「最多列 10 條」「只印、不影響過不過」:`passed = not items_fail` 與 `notes` 無關,**成立**。

### 8. kill-log 的 `recipe_id` 怎麼算、含不含 `new`

- 原句(〈實務隱患〉):「kill-log 的 `recipe_id` 由節點、合約、檔、原文算出,不含 `new`」
- 實際:`recipe_id = _kill_recipe_key(str(rel), invariant, file, old)`(約 14917),`_kill_recipe_key` 是 `sha256(json.dumps([node, invariant, file, old]))`(13833~13841)。**不含 `new`、不含 test、platform、note**。**成立**。連帶:同一完整身分 = 同一條「在同一處的配方」,重寫壞法(只改 `new`)身分不變。kill-add 判重也用同一把(約 14320),所以重寫壞法一定要先 kill-rm 才能 kill-add(已有的規則);重加後身分不變,舊的 survived 帳會繼續在最新那一筆,直到重跑。與計劃說法一致。
- 精確一點:`_kill_recipe_id`(給 kill-rm 與短身分用)對「字串欄位齊全的 dict」回 `_kill_recipe_key`;對格式壞的元素回 `sha256(["malformed", node, 元素])`。kill-log 對壞 dict 仍會算 `_kill_recipe_key(…None…)`。兩者只在「配方格式壞」時不同,而格式壞的配方 guard kill 本來就會出錯、不會有可用的 survived 行,不影響本計劃。

## 其他小處(非必修)

- 〈做法〉② 的「(節點與短身分照 shell 規則加引號)」:程式已有 `_kill_node_arg(rel)`(13873,去 `.md`、含控制字元時印佔位字、其餘 `shlex.quote`),直接沿用;短身分是十六進位,不用引號。計劃可直接寫「節點寫法用 `_kill_node_arg`」。
- PRIOR-ART 說「`_kill_recipe_id`(kill-rm 與 guard kill 結果行已在用)」:成立。
- doctor 在 CI 或別台機器上讀不到 kill-log(本專案外的消費專案 kill-log 不進版控,見 `_cmd_codeloop_dispositions` 註解),③ 只在本機有帳時有東西可列。可在〈實務隱患〉補一句。
- 〈實務隱患〉「P2 多讀一次 kill-log」:`_backing_kill_rows` 會讀整個 kill-log 並對回每個被引用節點;帳檔大時不是常數時間。建議 doctor 只讀一次、自己分組。

## 結論

必修(照影響大小排):

1. ★動到核心★ `--try` 判 survived 靠 `cmd_guard_kill` 回逐條判定,但現在只回 rc;而 rc 1 也包含「全弱證據」。要在計劃裡二選一:給 `cmd_guard_kill` 一個選用的結果輸出參數(不改判法、不改 rc),或讀 kill-log 尾巴;並把〈範圍〉的「不改 guard kill」收窄、把 rc 描述改成「killed 有強證據 0、survived 或全弱證據 1、drifted/abort/error 2」、S2 條款限定「判定是 survived 時」。
2. ★動到核心★ ③ 的「(之後程式改過,先重跑)」靠 `_codeloop_record_valid_ex`:它判的是「之後有沒有動過任何非簿記檔」,筆記 .md 與不相干提交都算,實務上每行都會帶,等於無資訊;且 kill-log 的 `head_sha` 是平台根 repo 的 HEAD、可能與 vault repo 不同;且沒有總時間預算。改成「配方指著的 `file` 在 head_sha..HEAD 之間改過」(`git diff --quiet <head_sha> HEAD -- <file>`),或至少改措辭加總預算並限同 repo。
3. ③「原文已對不上的不重複列」目前無從判:`_kill_p2_scan` 丟掉了 `_kill_p2_one` 的回傳 code。計劃要寫明改 `_kill_p2_scan` 的回傳(多回「有列問題的配方身分」),並查既有測試是否釘著它的回傳形狀。
4. ③ 要另開一個 `warn_soft`(預設每段只印 3 條、標題語意不同),`check-p2` 事件要能分兩種;跳過規則(verification/superseded/stale)抽成共用函式給 ③ 與 ④ 用,`_backing_kill_rows` 不篩這些、要在列的時候補篩。
5. ③ 取最新一筆改為「檔內順序最後一筆」(跟 `_backing_judge_groups` 一致),不要比 `ts`(同秒、型別未驗);印出的合約前段取筆記那條配方的、不取帳檔的 `invariant`,`ts` 驗型別去控制字元;並定義 `weak=true` 的 survived 怎麼列(建議照列、加「證據弱」註記;`_mtime_unsure` 的 survived 可能是假的)。
6. ① 定義 `--id` 比對語意:前綴、8 個以上十六進位、對到零或多條不同身分都回 2(同 kill-rm);「找不到」改用共用逐行格式、輸出到 stderr、結尾提示不用 kill-rm 的「移除」那句(`_guard_kill_rm_list` 不能直接呼叫)。
7. ④ 比對 `file` 與 `changed` 前要確認配方平台的 repo 頂(`_kill_plat_top`)與 fix-check 的 `rr` 相同,否則誤報;掃配方不要用 `_kill_p2_scan`,另寫小迭代器;提醒要「一說明 + 每條指令一個 note」,且只在 fix-check 沒早退(這輪需要修正紀錄)時印,S4 測試要照這個條件造輪次。
8. `kill-add --try` 的其他未定義情境寫進計劃:只更新 covers 時要不要試跑、`--try` 必定先印「repo 有未提交變更」警告且當次行 `weak=true`、程式未提交時 rc 2 的提示。
9. RETIRE-IF 的「一次只跑一條的紀錄為零」現在量不到(kill-log 沒有執行 id 欄、計劃又不加欄位);改成可量測的訊號或承認只靠 10-15 問 rtb。
