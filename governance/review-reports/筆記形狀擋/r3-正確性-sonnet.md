severity: blocker

〈frontmatter / 白話 / 依據〉已讀,無 finding。

## F1 釘版本放行寫法可被本機捏造的不可達提交物件繞過,且會連帶弱化 refcheck 的反幻覺驗證

severity: blocker
blocking: 是 —— 不改,作者能在不需要 `--no-verify`、完全不留痕的情況下讓 note-shape(以及被同一改動波及的 `lumos refcheck`/設計審引用檢查)判定一則捏造的程式引用為合法,擋不下該擋的內容。

引句:「必須是至少 12 位的十六進位提交編號、找得到、那個提交裡有這個路徑、行號在那個版本的檔長之內」

驗證(在乾淨臨時目錄用 `git -C` 做的實驗,未動 repo 任何檔):
1. 建一個全新 repo,正常 commit 一次(`main` 只有這一個提交)。
2. 不需要任何特殊權限,只用一般 git 指令捏造一個「不可達」的提交:寫一支任意內容的檔、`git hash-object -w`、`git update-index --add --cacheinfo`、`git write-tree`、`git commit-tree` 產生一個新的 commit sha——這個 sha **不是任何分支/標籤的祖先**。
3. 對這個 sha 跑 `git cat-file -e <sha>:<path>`:回 0(存在)。
4. `git merge-base --is-ancestor <sha> main`:回「NOT reachable from main」——也就是說,`git push` 絕對不會把這個物件傳給遠端(push 只送出「被推的 ref 可達」的物件)。

實測輸出(節錄):
```
PIN CHECK: ok (line-existence would validate)
NOT reachable from main — would never be transmitted by git push
```

佐證行:
file: `scripts/lumos:19820-19833` `_validate_repo_ref` 的 `at_sha` 分支只呼叫 `_git_tree_has`/`_git_tree_text`,對 sha 完全不驗可達性(reachability)、也不驗它是不是某個真實分支/標籤的祖先。
file: `scripts/lumos:29734-29737` `_git_tree_has` 的實作就是 `git cat-file -e f"{at_sha}:{path}"`——只要物件還在本機物件庫(哪怕是懸空、從沒進過任何 ref),就會判 True。
file: `scripts/lumos:29746-29757` 這支既有的 `_dispositions_check_path_line` 目前用同一個 `at_sha` 入口,但它的 `at_sha` 是呼叫端傳進來的「這次真正被推送的 sha」(工具自己算的、非使用者可自由填寫的文字)——跟本規格要新增的用法完全不同:本規格要把 `路徑@<提交>:數字` 裡「使用者自己在筆記裡寫的那段文字」直接當成 `at_sha` 餵給同一支函式。

為什麼是正確性問題:規格把「釘版本」設計成第一層唯一允許放行的合法寫法,目的是逼作者證明自己寫的行號引用「確實對應過一個真實的程式版本」,不是憑空杜撰。但驗證只查「這個 sha 在本機 git 物件庫裡找得到」,不查它是否曾經是任何分支/標籤的一部分。任何一位能提交筆記的作者,同樣有能力在本機執行三、四行 git 指令捏造一個從未進入過歷史的提交物件,把任意內容、任意行數塞進一支檔案,再把那個 sha 寫進筆記當「證據」——note-shape 會判定合法並放行(不需要 `--no-verify`,治理帳也不會留下任何繞過紀錄,因為在它眼中這是一次正常放行)。

引句:「拆成路徑、行號、釘住的提交,交給既有」

這個弱點不只影響 note-shape:規格明講「同一套拆解也讓 `lumos refcheck` 與設計審放行前的引用檢查對釘版本的引用改成對那個提交驗」——而 `_validate_repo_ref` 本身的 docstring(`scripts/lumos:19806-19811`)明白寫著它存在的理由正是「J-c 不得走 `_refcheck_scan` 抽取入口……正是 J-c 要擋的幻覺」。把使用者可自由填寫的釘版本字串直接餵給這支專門用來擋幻覺證據的函式,等於把同一個繞過管道也開給設計審的引用檢查——一個原本用來防止 AI/人捏造證據的機制,被一個從未被要求「必須可達某個真實分支」的新語法整個繞過。

需要補的驗法(給編排者/實作者的具體修法方向,不是我要求採用,只是指出缺口):至少要求 `<提交>` 是某個已知分支/標籤/HEAD 歷史的祖先(例如 `git merge-base --is-ancestor <sha> HEAD` 或對照全部本機分支),否則「釘版本」這個放行機制形同虛設。

## F2 「至少 12 位十六進位」的釘版本規則沒有排除「剛好是全十六進位的分支/標籤名」,可能放行一個仍會移動的名字

severity: major
blocking: 是 —— 規格明講「會移動的名字」一律要擋,但候選規則只檢查字元集(是否為十六進位)與長度,沒有檢查該字串是否恰好也是一個 ref 名字;若恰好撞名,擋下的判準本身就會放行一個會移動的名字。

引句:「這類會移動的名字寫成」

驗證(乾淨臨時目錄,`git -C`,未動 repo):
```
git branch deadbeefcafe        # 12 位、全十六進位字元的分支名
git cat-file -e deadbeefcafe:f.txt   # rc=0 → "resolved via branch name OK"
```
git 對這種字串的解析規則是「先當 ref 名找,找到就用」,不會因為它「看起來像 sha」就跳過 ref 解析。也就是說:只要專案裡（或作者本機)存在一個恰好是 12 位以上十六進位字元組成的分支或標籤(這類名字並不罕見,例如某些自動化工具會用短 sha 當分支名、或 cherry-pick/hotfix 分支沿用舊 commit 前綴命名),`路徑@<那個分支名>:數字` 這種寫法就會通過候選規則裡「至少 12 位十六進位」的檢查,而 `_validate_repo_ref` 的 `at_sha` 參數實際餵給 git 時,git 會把它當成該分支目前的 tip 解析(而不是固定住的某個歷史提交)——這正是規格自己列為必須擋下的「會移動的名字」,卻因為驗證只看字元形狀、不驗「這個字串是否同時也是一個 ref」而漏放行。

跟 F1 的差異:F1 不需要专案裡有任何特殊分支就能繞過(純本機捏造物件);F2 需要專案(或作者)剛好存在一個全十六進位命名的分支/標籤,觸發門檻較高、但一旦存在就是規格明文要擋卻擋不住的具體反例,屬於同一個「候選規則只驗形狀」的家族問題,建議跟 F1 一起補(例如驗證前先確認 `<提交>` 解析結果與 `git rev-parse --verify <提交>^{commit}` 對照下,不是任何本機已知 ref 的目標)。

## F3(minor,不擋)PRIOR-ART 對「放行不寫事件」援引的鄰居先例與事實不符

severity: minor
blocking: 否 —— 不影響任何判定結果,只是設計理由的事實錯誤,可能誤導後續維護者以為這是「照抄鄰居」。

引句:「★只有擋下(blocked)與環境變數跳過(skipped-env)寫事件,放行不寫★」

佐證行:file: `scripts/lumos:23347-23357` `note-shape` PRIOR-ART 宣稱借用的正主「每支檔有家」(`nodehome-check` 閘)實際上**每次跑都寫一筆事件**:`kind = "blocked" if blocked and cfg["mode"] == "on" else ("warned" if blocked else "passed")`——沒有違規時寫 `"passed"`,不是規格暗示的「照既有各閘慣例只在擋下時才寫」。這一段本身有獨立、合理的理由(rtb 回饋第 4 項),不是靠不住的設計,只是不應該說成是「照鄰居」——它其實是刻意偏離最接近的先例。實務後果很小:`lumos gov --stats` 這類統計如果日後想比較各閘的「總觸發次數」或「通過率」,note-shape 會是少數幾個永遠沒有「通過」計數的閘,可能讓人誤以為統計工具本身有 bug,而不是這個閘本來就設計成不記。建議把 PRIOR-ART 那句話改成「刻意偏離 nodehome-check 的逐次記帳,理由見下」,而不是掛在「借用既有形狀」清單裡。

〈做法 > 範圍與行〉(提交前/推送前/CI 三種範圍推導、上線點截斷、合併提交只算新行、圍欄內照查、UTF-8 讀不成整支擋下)已讀,無 finding——這些都直接對照到既有 `_nodehome_golive`/`_nodehome_clamp_base`/`_nodehome_merge_own_changes`/`_visible_lines` 的既有行為,加參數/拆函式的做法看得出來確實可行,沒發現新輸入會讓範圍算錯。

〈兩條規則〉除 F1/F2 指出的釘版本驗證缺口外,其餘部分(裸文字候選規則的前後界字元、單一檔名要求全 repo 恰好一支才算、FACT/FLOW/DEP 只看 summary 區塊新增行、`[來源:]` 五類、不用 `[src:]` 撞名的理由)已讀,無新的 finding——單一檔名判準偏「少擋」是規格自己在〈誠實界線〉承認的已知天花板,不是本輪新增的洞。

〈治理帳寫入加鎖(移出)〉已讀,無 finding——移到獨立 Issue 的理由與範圍講得清楚,沒有殘留在本計劃裡的加鎖動作。

〈紀律範本改寫〉已讀,無 finding——`scripts/templates/graph-discipline.md:44` 目前確實還是舊句(FACT/FLOW/DEP 那列只講「以程式碼為準」+ 查詢),`skills/lumos-project-notes/reference.md:410` 的 FACT 範例也確實還是舊寫法,兩處都對得上規格要改的目標。

〈消費專案的 CI〉已讀,無 finding——doctor 補檢查 CI 有沒有呼叫 `note-shape --diff`、事後掃違規兩件事分工清楚。

〈條款 S3–S8、S10、S11〉已讀,無 finding。

〈回退〉已讀,無 finding——順序合理,第 4 步已經把「釘版本解析要留」寫清楚(不然舊筆記裡的釘版本引用會被退化後的 refcheck 當成不存在的檔),第 3 步的指令空殼過渡也考慮到消費專案 CI 手貼的那一步不受 `lumos update` 管。

〈實務隱患〉已讀,無 finding——四類(守衛面/資源併發/對外送出/不可逆/金流)逐類都有具體理由,金流與對外送出的「已排除」判斷跟程式行為一致。

〈誠實界線〉已讀,無 finding——三條天花板(第二層形狀不固定、行號抽樣量小、沒接 CI 的專案擋不住 --no-verify)都是誠實的自我限制,沒有言過其實。

〈審計修正紀錄〉已讀,無 finding——r1/r2 折入清單與本次讀到的正文一一對得上,沒有發現文字寫著已折但正文其實沒改的矛盾。

最嚴重 severity 是 blocker;blocking 共 2 條(F1 blocker、F2 major)。
