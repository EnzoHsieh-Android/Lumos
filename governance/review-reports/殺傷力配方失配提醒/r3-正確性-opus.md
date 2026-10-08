severity: minor

# 第 3 輪設計審:正確性-opus(鏡頭:第 2 輪折法——模擬 guard kill 工作樹的解析器、設定交給 load_platforms(cfg=)、配方身分共用函式、kill-rm)

實驗環境:`kr-r3-work-正確性-opus/repo`(--shared clone,HEAD 339923e1);腳本 `kr-r3-work-正確性-opus/exp/run.py`、`exp/run2.py`。每一格各建一個 repo,用 kill-add 宣告後真跑 `lumos guard kill`,看實際判定。

真跑 guard kill 的結果(只列跟 spec 寫法有關的格):

| 輸入 | 真跑 guard kill | spec 照字面的解析器 |
|---|---|---|
| `a -> b`、`b -> a` 的連結迴圈,file=`a` | drifted(file 開不了:Too many levels of symbolic links),rc2 | outside(spec 對應到 error) |
| file=`""` 或 `.` | error(file 路徑逃逸 worktree),rc2 | 會走到 repo 頂本身,「還在根內」有歧義;照字面會判 missing(不是一般檔) |
| file=`../wt/prod.py` | 套用了壞法(工作樹資料夾固定叫 `wt`,爬出去再爬回來還在工作樹裡) | outside |
| file=`../myrepo/prod.py` | error 逃逸 | outside(一致) |
| 非 UTF-8 | 程式崩潰丟 UnicodeDecodeError,rc1(spec 寫對了) | undecodable |
| 相對資料夾連結 `lnk -> src`,file=`lnk/x.py` | 套用了壞法,接著 `git checkout -- lnk/x.py` 失敗 → error「revert 失敗——後續同組配方作廢」 | ok |
| 相對檔案連結 `p.py -> prod.py` 的配方,同組再接一條 `prod.py` 的配方 | 第一條 survived;第二條 drifted「old 命中 0 次」(還原只還原了連結,目標檔留在被改壞的狀態) | 兩條都是 ok |
| 子模組裡的檔 `vendor/lib.py`(工作目錄裡存在) | drifted(file 開不了:No such file) | ok |

另外查過,沒問題:`load_platforms(repo_root, cfg=dict)` 走的分支跟從磁碟讀同一份設定完全一樣(單平台分支也把同一份 cfg 傳給 `load_test_profile`);pre-push 掛鉤的環境裡沒有 `GIT_DIR`,doctor 在掛鉤裡跑 `git -C <平台根> rev-parse` 不會解析錯 repo;doctor 的 `repo_root` 從定義到 P 段之間沒有被重新指定,跟 `_repo_root_from_env` 在有 docs/ 時是同一個值;精簡版產生器靠呼叫可達性保留函式,P2 呼叫到的新函式會一起保留;本 repo 唯一一條配方(canary-audit)現在命中 1 次;`check-p2` 用字面閘名寫,可以通過閘名漂移掃描。整份沒有找到照字面實作會做錯主要行為的 blocking 項;以下全是 minor。

## F1 解析器有三種輸入跟真跑 guard kill 判得不一樣:迴圈、解析到 repo 頂本身、`../wt/`
severity: minor
blocking: 否
引句:「跟隨連結超過 40 次 → `outside`(迴圈)」
file: `scripts/lumos:13267`
1. **迴圈**:guard kill 用 `os.path.realpath`(非 strict)。遇到迴圈時它不會丟錯,而是回傳一條還在工作樹裡的路徑,所以會通過圍欄;接著 `open` 丟 ELOOP,這是 OSError,判成 drifted「file 開不了」(`scripts/lumos:13277`)。實跑 `a -> b`、`b -> a` 的結果確實是 drifted。spec 卻把迴圈歸成 `outside`,kill-add 的提醒字面會說「guard kill 會擋在圍欄外(判 error)」,跟實際不符。這條是第 2 輪折法新加的,沒有實跑驗過。應改成 `missing`,細節帶「連結迴圈」。
2. **解析到 repo 頂本身**(file 是 `""`、`.`、`sub/..`):guard kill 的圍欄要求 `startswith(wt_real + os.sep)`(`scripts/lumos:13268`),剛好等於工作樹根本身不算在裡面,所以判 error 逃逸(實跑 `""`、`.` 都是這樣)。spec 寫「走完還在根內才算解析成功」,沒講等於根算不算在內;照字面最可能判成在內,接著被「不是一般檔」歸成 `missing`,跟 S5 的 `outside ↔ error` 對應不上。應寫明「解析結果等於 repo 頂本身 → `outside`」。
3. **`../wt/<x>`**:第 2 輪的理由是「guard kill 的工作樹資料夾名跟 repo 不同」,但工作樹資料夾名是固定字面 `wt`(`scripts/lumos:13237`),跟 repo 叫什麼名字無關。實跑 `../wt/prod.py` 時 guard kill 真的套用了壞法,解析器卻判 `outside`(誤報)。現實裡沒人會這樣寫,所以只建議把理由改正確(「爬到工作樹上一層之後,除非剛好走回名叫 `wt` 的資料夾,否則回不來」),或在誠實界線裡註明這個例外。
4. 這三格都不在 S5 的題目清單裡,所以對照測試會綠,但「判法逐項對齊」的宣稱不成立。第 1、2 點兩邊都是「不是 ok」,不會漏報,所以給 minor。

## F2 S5 的對照題要逐格各自隔離,而且有一格的 guard kill 結果要另外定義;不然對照測試會因為 guard kill 自己的還原行為被污染
severity: minor
blocking: 否
引句:「讓新函式與真跑 `lumos guard kill` 各判一次,斷言兩邊的對應」
file: `scripts/lumos:13288`
1. guard kill 把同一篇、同一平台的配方放進同一個工作樹依序跑。套完壞法後用 `git checkout -- <file>` 還原(`scripts/lumos:13288`)。
2. 「repo 內相對符號連結」這格如果是**檔案連結**(`p.py -> prod.py`):還原只還原連結本身,目標檔 `prod.py` 留在被改壞的狀態。實跑時同組下一條 `prod.py` 的配方被判 drifted「old 命中 0 次」,但解析器讀的是工作目錄,判 ok。如果對照測試把這格放在其他以 `prod.py` 為目標的格子前面,會紅得莫名其妙,實作者可能因此去「修」解析器。
3. 如果是**資料夾連結**(`lnk/x.py`):壞法套上了,但還原失敗,結果是 error「revert 失敗」,然後 `break`(`scripts/lumos:13292`),同組後面的格子全部拿不到判定。
4. 非 UTF-8 那格會讓整個 guard kill 崩潰(rc1),同一次執行的其他格也全部拿不到判定。
5. 建議在對照測試的說明裡寫明:每格各用一篇筆記(或各建一個 repo)、各跑一次 guard kill;連結那格的「套用了壞法」包含 error「revert 失敗」這種結果(它不是逃逸,符合 spec 寫的「沒判 error 逃逸」,但要明寫,免得實作者拿 verdict 是不是 error 來判)。

## F3 誠實界線只講了「沒提交的改動」,漏了兩種工作目錄跟隔離工作樹永遠不一樣的情況:子模組、被忽略的檔
severity: minor
blocking: 否
引句:「讀的是工作目錄的檔(包含沒提交的改動)」
file: `scripts/lumos:13277`
1. `git worktree add` 不會把子模組檢出,也不會帶進 .gitignore 掉的檔(例如產生出來的程式碼)。實跑:配方指向子模組裡的 `vendor/lib.py`,工作目錄裡有這支檔,guard kill 判 drifted「No such file」;解析器讀工作目錄,判 ok。
2. 這種配方 guard kill 永遠跑不起來,P2 卻永遠說對得上,而且就算「先提交再跑」也不會轉綠。這正是本案要抓的「配方靜靜失效」,只是發生頻率低。
3. 建議至少在誠實界線補一句(子模組裡的檔、被忽略的檔:P2 會說對得上,guard kill 會判 drifted);要補機械判斷的話,可以用 `git -C <repo 頂> ls-files --error-unmatch -- <file>` 判它是不是被追蹤的檔。不建議這一輪擴範圍。

## F4 S4 沒把「load_platforms 丟例外」這格放進去;而且它要斷言的字面跟最外層例外保護印的字一樣,分不出「正確判成設定讀不了」和「整段崩掉被兜住」
severity: minor
blocking: 否
引句:「設定檔是壞 JSON 時應印」
file: `scripts/lumos:4555`
1. 第 2 輪正確性席 F2 的折法建議「S2、S4 各加一格:JSON 合法但兩個平台沒寫 default_platform」。這版 S2 加了(「內容讓 `load_platforms` 丟例外」),S4 沒加。
2. 做法 5 規定設定讀不了要印「設定檔讀不了,這一段算不出來,先跳過」,整段外層的例外保護則印「這一段算不出來」。S4 只斷言後面這個子字串。如果實作在 P2 裡沒接住 `load_platforms` 的 ValueError,讓它往外丟、被最外層兜住,S4 照樣會綠。
3. 建議把 S4 的斷言改成「設定檔讀不了」,並加一格「兩個平台沒寫 default_platform」。

## F5 目標檔被刪掉(重構後最常見的失配)時,「不是一般檔」那一步怎麼判沒寫清楚;kill-add 那邊也沒有像 P2 一樣包例外保護
severity: minor
blocking: 否
引句:「不是一般檔(目錄、具名管線、裝置檔)→ `missing`,細節寫」
file: `scripts/lumos:13277`
1. 照順序,解析成功之後先判「是不是一般檔」,再開檔;只有開檔那一步寫了「`OSError` → `missing`」。路徑不存在時:用 `os.path.isfile` 判,細節會寫成「不是一般檔」,但檔其實是被刪了,使用者會被誤導;用 `os.stat` 判,會丟 FileNotFoundError,而 spec 沒說這一步的 OSError 要怎麼處理。
2. P2 有逐條的例外保護,會兜成「這條判不了」(也沒附 kill-rm 修法)。kill-add(做法 3)只對讀設定包了例外保護,判斷函式本身沒包。照字面實作,只要判斷函式丟出未預期的例外(上面那個 stat、權限不足的 `readlink` 等等),kill-add 就會在寫入前崩潰。第 2 輪才剛為了「kill-add 不能比現在退步成崩潰不寫入」折過一次,這裡是同一類問題還沒折到的地方。
3. 建議:「不是一般檔」那一步的 OSError 一樣歸 `missing`,細節帶原因(例如「不存在」);kill-add 對判斷函式整個包一層,任何例外都印「⚠ 提醒:<原因>,沒驗原文」,然後照舊寫入。

## F6 PRIOR-ART 還寫著舊的「realpath 前綴判法」,跟做法 1 改成的模擬解析器對不上
severity: minor
blocking: 否
引句:「同一種基準與圍欄(平台根所在 repo 的最上層、realpath 前綴判法)」
file: `scripts/lumos:13268`
1. 第 2 輪把路徑判斷改成「模擬 guard kill 工作樹的小解析器」,原因正是工作目錄裡做 realpath 前綴判斷會跟 guard kill 判得不一樣。PRIOR-ART 還說新判斷用「同一種……realpath 前綴判法」,兩處互相矛盾。下一個 session 只讀 PRIOR-ART 的話,會照舊寫法做。
2. 建議改成「同一種基準(平台根所在 repo 的最上層);圍欄改成模擬工作樹的解析器,理由見做法 1」。

## F7 kill-rm 一次移除多條同身分配方時,只講了印「那條」;同身分但內容不同的多條,會丟掉其他條的設定
severity: minor
blocking: 否
引句:「移除前在標準輸出印出被移除那條的完整內容」
file: `scripts/lumos:12870`
1. 身分只看節點、invariant、file、old(`_kill_recipe_key`),不看 new、test、platform、covers。手改出來的「同身分」不一定是逐字重複,可能 new 或 covers 不一樣。
2. 做法 4 說對到的全是同一完整身分時「一起移除」,但印內容與範本只講「那條」(單數)。照字面只印一條的話,其他條的 new 或 covers 就這樣沒了,這違反這個步驟本身「讓修法不會丟掉舊配方的設定」的目的。
3. 建議寫明:每一條被移除的都印完整內容;內容不完全相同時,另外印一句「這幾條身分相同但內容不同」。

## 逐節
- 前言、依據、PRIOR-ART、RETIRE-IF、REVISIT:F6;其餘已讀,無 finding。
- 範圍:已讀,無 finding。
- 做法 1:F1、F2、F3、F5。型別先判、身分共用函式(格式壞的用 `["malformed", 節點, 原始元素]` 雜湊,JSON 解析出來的值一定序列化得回去)、同檔只讀一次、文字模式讀檔(跟 guard kill 一樣會把換行正規化)都核對過。
- 做法 2:F4。`load_platforms(cfg=)` 跟從磁碟讀同一份設定走同一條路,實際查證過;接走警告、例外當讀不了,這兩點的折法正確。
- 做法 3:F5。插入點(判重之後、`if updated is None:` 與原子寫入之前)放得進現在的結構;既有 24 處 kill-add 呼叫都沒有逐字比對標準錯誤。
- 做法 4:F7。最短 8 字元、多條不同身分擋下、標記逐 KEY 行處理:目前讀 `[kill:recipes]` 標記的只有 guard list 的顯示,拿掉標記不會改變任何閘的判定。
- 做法 5:F4。事件只在 `--ci` 時寫治理帳,pre-push 跟每日治理也都是用 `--ci` 跑,符合「有列出就記帳」;軟提醒不動回傳碼。
- 條款:S4 見 F4;S5 見 F1、F2;其餘已讀,無 finding。
- 回退、實務隱患、誠實界線:F3;其餘已讀,無 finding。

最高等級:minor;blocking 共 0 條
