severity: major

# 第 2 輪設計審:正確性-opus(鏡頭:第 1 輪折法本身照字面實作會不會做錯、S5 能不能一一對應)

實驗環境:`kr-r2-work-正確性-opus/repo`(--shared clone,HEAD c7024acd),腳本 `kr-r2-work-正確性-opus/exp.py`、`exp2.py`、`exp3.py`、`cfgexp.py`。參考實作照 §1 字面寫(repo 頂 = `rev-parse --show-toplevel`;realpath 圍欄;`file` 拆開後從 repo 頂往下逐層看有沒有絕對目標的符號連結;一般檔;UTF-8 文字模式;count==1),每格另建一個 repo 真跑 `lumos guard kill --json`。

S5 列出的格子實跑結果(全部對得上,S5 照字面寫得出來):

| 格子 | 新函式(字面) | 真跑 guard kill |
|---|---|---|
| 平台根是子資料夾、file 從 repo 頂算 | ok | survived(有套壞法) |
| 平台根是子資料夾、file 從平台根算 | missing | drifted(file 開不了) |
| 平台根就是 repo 頂 | ok | survived |
| repo 內相對連結 | ok | survived |
| 絕對連結(檔/資料夾那一層) | outside | error 逃逸 |
| 跑出 repo 的 `../x.py` | outside | error 逃逸 |
| 0 次 / 2 次 | hits | drifted(命中 0 / 2 次) |
| 非 UTF-8 | undecodable | 程式崩潰,丟出 UnicodeDecodeError,rc1 |
| 指到資料夾 | missing | drifted(Is a directory) |

另外查過,沒問題:`git rev-parse --show-toplevel` 回的是已經解開連結的路徑(`/tmp/x` 會回 `/private/tmp/x`),所以「路徑上任一層」就算從根目錄一路往下看,也不會把 macOS 的 `/tmp`、`/var` 誤判成絕對連結;doctor 的 `notes` 鍵跟 `env.find` 回的 rel 是同一個字串,三處算出來的短身分會一樣;工具鏈自己那一條配方(canary-audit)現在命中 1 次。

## F1 圍欄只補了「絕對路徑的符號連結」,同一類「先跑出 repo 頂再繞回來」的寫法照字面會判成 ok,guard kill 卻判逃逸;其中最常見的是 `file` 直接寫成絕對路徑
severity: major
blocking: 是
引句:「相對路徑的符號連結兩邊解析結果一樣,照常判。」
file: `scripts/lumos:13267`
1. guard kill 的圍欄是 `os.path.realpath(os.path.join(wt, file))`,而 `wt` 是暫存資料夾。路徑解析時只要有任何一步離開了 `wt`,就再也回不到 `wt` 裡面,所以一定判逃逸。新函式的基準卻是真正的 repo 頂:路徑先離開 repo 頂、再因為絕對路徑或 repo 自己的資料夾名稱繞回 repo 頂,新函式的 realpath 會落在圍欄內。第 1 輪只補了其中一種(路徑上某一層是絕對目標的連結),同一類還有三種沒補。
2. **`file` 本身是絕對路徑(最常見)**:使用者打 `lumos guard kill-add … --file "$(pwd)/prod.py"`,kill-add 不驗 `--file`,照樣寫進去。照 §1 字面算 `os.path.realpath(repo 頂/file)` 時,`os.path.join`(以及 pathlib 的 `/`)遇到絕對路徑會把前面的 repo 頂丟掉,得到的就是 repo 內那支檔,判 `ok`;往下逐層找連結時也一層都找不到。實跑 `exp2.py` 的 abs_file 格:新函式判 `ok`,guard kill 判 `error`(file 路徑逃逸 worktree,圍欄擋下)。結果是 kill-add 不提醒、P2 不列,這條配方卻永遠跑不起來。這正好是本案要抓的「配方靜靜失效」。
3. **`file` 用 `..` 爬出去再爬回來**(`../<repo 資料夾名>/prod.py`):實跑 climb_file 格,新函式判 `ok`,guard kill 判 `error` 逃逸。
4. **相對連結指向一個絕對目標的連結**(`a.py -> b.py`,`b.py -> /abs/repo/real/prod.py`):§1 說的「路徑上任一層」如果照字面只看 `file` 寫出來的那幾層,`a.py` 是相對連結,不會被抓到。實跑 chain_rel_to_abs 格,新函式判 `ok`,guard kill 判 `error`。
5. **相對連結先爬出 repo 頂再爬回來**(`c.py -> ../<repo 資料夾名>/real/prod.py`):實跑 rel_link_climb 格,新函式判 `ok`,guard kill 判 `error`。這直接推翻了引句「兩邊解析結果一樣」。
6. S5 的題目清單裡沒有上面任何一格,所以對照測試會是綠的,也就證明不到 §1 宣稱的「跟 guard kill 的『路徑逃逸』同一判法」。
7. 建議折法:把判準從「列舉哪幾種連結」改成「模擬 guard kill 的離根」。從 repo 頂開始自己一步一步解析:`file` 是絕對路徑就直接判 outside;每遇到 `..` 或連結就展開(連結目標是絕對路徑就判 outside),只要中間任何一步離開 repo 頂就判 outside,不管之後會不會繞回來。S5 再加兩格:絕對路徑的 `file`、相對連結接絕對連結。第 3 和第 5 種罕見,但跟第 2 種是同一個修法,一次補齊。

## F2 「設定先解析」只把壞 JSON 當成讀不了;`load_platforms` 遇到四種設定內容錯誤會丟 ValueError,照字面實作會讓 kill-add 直接崩潰、不寫入,比現在還退步
severity: major
blocking: 是
引句:「解析得了才呼叫 `load_platforms`,★一次判定裡只呼叫一次★,結果給每條配方共用。」
file: `scripts/lumos:4555`
1. §2 只為「解析不了、或不是物件」定義了「設定檔讀不了」,理由是「`load_platforms` 遇到壞 JSON … 不會丟錯」。這句只對壞 JSON 成立。JSON 合法、內容寫錯時,`load_platforms` 會 `raise ValueError`,我實跑 `cfgexp.py` 四種都會丟:兩個以上平台卻沒寫 default_platform、profile 名稱工具不認得、預設平台不在清單裡、`platforms` 底下某一項不是物件。
2. guard kill 自己會接住這個 ValueError,當成「設定檔讀不了」回 rc2(`scripts/lumos:13171`)。§2、§3 都沒說新程式碼要接。照字面實作的話,kill-add 在判重之後呼叫 `load_platforms`,ValueError 往外丟,整個指令以 traceback 結束,配方沒寫進去。
3. 對照現況:同一份「兩個平台、沒寫 default_platform」的設定,現在 kill-add 是 rc0 照常寫入(`exp3.py` 實跑),因為它根本不讀設定。照 spec 實作之後就寫不進去了,違反 S2「設定檔讀不了…應印『沒驗原文』的提醒並照舊寫入」的用意,也違反 §3「照舊寫入」。S2 的測試只會用壞 JSON 造題,抓不到這個退步。
4. P2 那邊會被最外層的「這一段算不出來」接住,不至於讓 doctor 崩潰,但 §5 寫好的「設定檔讀不了,這一段算不出來,先跳過」這句也走不到。
5. 建議折法:§2 把「`load_platforms` 丟 ValueError」也併進「設定檔讀不了」(原因照抄例外訊息,跟 guard kill 對齊);S2、S4 各加一格「JSON 合法但兩個平台沒寫 default_platform」。

## F3 S1 說標準錯誤「恰好多一行」,但新流程呼叫的 `load_platforms` 自己也會往標準錯誤印警告
severity: minor
blocking: 否
引句:「標準輸出跟沒有這條提醒時逐字相同、標準錯誤只多這一行、回傳碼不變」
file: `scripts/lumos:4547`
1. 以前 kill-add 不讀設定。改成要讀之後,只要設定裡某個平台的 root 不存在(第 4547 行),或單平台設定的 test_profile 名稱工具不認得(第 4479 行,這是 `load_platforms` 從磁碟重讀時印的),或 `test` 欄位不是物件,標準錯誤就會多出 `load_platforms` 自己印的警告。結果配方對得上時也不再是「不印」,失配時也不只多「恰好一行」。
2. 在乾淨的測試環境裡 S1 會是綠的,問題只會在使用者的真實設定上出現。後果是多一點雜訊,不會判錯,所以給 minor。折法有兩種:S1 的措辭改成「本功能自己的提醒恰好一行」,或呼叫 `load_platforms` 時把它印的東西收起來。doctor 的 P2 段也一樣會多印這些警告。

## F4 配方本身不是物件時,短身分沒有定義;照字面寫的 kill-rm 會讓整篇的配方都刪不掉
severity: minor
blocking: 否
引句:「在那篇的配方裡找身分以它開頭的,恰好一條就移除」
file: `scripts/lumos:13200`
1. §5 規定每條不是 `ok` 的配方都要附「修法:lumos guard kill-rm <節點> --id <短身分>」,`malformed` 也包括在內。但如果配方根本不是物件(例如陣列裡混了一個字串),它沒有 invariant、file、old 可以拿來算 `_kill_recipe_key`,短身分就沒有定義。
2. kill-rm 照字面對每條配方用 `r.get(...)` 算身分的話,遇到不是物件的那一條會丟 AttributeError,同一篇裡其他正常的配方也跟著刪不掉。kill-add 判重時有先用 `isinstance(r, dict)` 跳過,kill-rm 沒寫要不要比照。
3. 建議:kill-rm 比照 kill-add 跳過不是物件的配方;P2 列這種配方時,修法改成「手動把它從 kill_recipes 拿掉」。guard kill 跑到這篇也會崩潰(第 13200 行的 `r.get`),所以這種配方本來就只能手動修。

## 逐節
- 範圍:已讀,無 finding。
- 做法 1:F1。型別先判、讀檔方式、一般檔、count、同一支檔只讀一次,這幾項都核對過;S5 列出的各格實跑都一一對得上(見上表)。
- 做法 2:F2。
- 做法 3:F3。另外核對過:「判重之後才驗」與「只更新 covers 時用既有那條的平台」,照現在的 kill-add 結構都放得進去(驗證插在判重迴圈之後、第 12972 行 `if updated is None:` 之前、atomic_write_verify 之前),沒有發現新的錯。
- 做法 4:F4。逐行處理 `[kill:recipes]` 標記:目前讀這個標記的只有 guard list 的顯示(第 11672 行),拿掉孤兒標記不會改變任何閘的判定。如果被刪配方的 invariant 對到零行或好幾行,「那一行」沒有定義,但最壞的結果只是留下孤兒標記,不另列。
- 做法 5:已讀,無 finding。repo_root 跟 guard kill 的 `_repo_root_from_env` 在有 docs/ 的配置下一樣;`check-p2` 照既有做法寫字面閘名,能通過漂移釘。
- 條款、回退、實務隱患、誠實界線:已讀,無其他 finding。S7 綁在 S5 的測試上,只能驗說明字面沒變,驗不到「程式沒被碰到」,但這不是折法造成的問題。

最高等級:major;blocking 共 2 條
