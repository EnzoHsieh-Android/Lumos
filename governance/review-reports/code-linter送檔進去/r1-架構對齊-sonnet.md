severity: major

一句話總結:這份 diff 的主軸是「同一件事只准一種寫法」,而它自己在「怎麼演進共用函式的介面」這一點上,用了一種比較隱晦的做法(改回傳型別、靠 Python 的 dict 迭代語意剛好還跟舊行為一樣),跟這個專案一直以來「介面要變就寫一個看得出來是相容層的東西」的習慣不一樣(major)。另外抓到「唯一實作」測試守衛偏弱可繞過、以及兩處這份 diff 自己講的呼叫端數量/寫法對不上程式碼實際樣子的小落差(皆 minor)。信任檢查放的位置與失敗行為、對不齊時 linter 發現不參與分級、新測試的 fixture 寫法這三項逐一核對過,跟既有慣例一致,沒有另開一套,列在文末「沒問題的部分」。

## 逐項檢查

### 1. `_lint_stacks_for_diff` 回傳型別從 list 改成 dict——第三個呼叫端沒被這份 diff 碰到,靠 dict 迭代語意「剛好」還算對

severity: major
引句:「拿到的仍是命令清單,行為不變。」
blocking: 是

`_lint_stacks_for_diff` 原本回一個命令字串的 list,這份 diff 改成回 `{命令: [檔案, ...]}` 的 dict(`scripts/lumos:17222`)。diff 裡兩個有拿到回傳值的地方都跟著改成用 `.items()`(`scripts/lumos:20938` 附近、`scripts/test_lumos.py:9556` 起的測試),看起來很完整。

但查證所得(不在 patch 內,用 `grep -n _lint_stacks_for_diff scripts/lumos` 找到):`scripts/lumos:17930` 還有第三個呼叫端——`_lint_new_cmd_targets` 裡的 `for cmd in _lint_stacks_for_diff({("_." + ext): set()}, lint_cfg):`。這份 diff 完全沒有動它,它現在能繼續工作,純粹是因為「對 dict 做 for-in 迭代,拿到的是 key」這個 Python 語意,剛好等同舊版 list 的內容與順序(單一合成檔名時,for-in 順序 = config 裡宣告命令的 first-seen 順序)。新函式的 docstring 只用一句話帶過「只迭代它的呼叫端拿到的仍是命令清單,行為不變」,沒有為這個具體呼叫端補一條測試去釘住「拿到的清單元素、順序都跟改版前一樣」,也沒有像這個專案別處處理介面演進時那樣寫一層看得出名字的相容包裝(參見 `scripts/lumos:14601`「相容包裝:Claude 側同步,回 True=ok(既有呼叫/測試用)」、`scripts/lumos:14774`「相容外殼:兩件一起做」——這兩處都是明講「這是給舊呼叫端撐住用的殼」,不是靠語言特性剛好兜起來)。

這代表同一個回傳值現在有兩種互不相容的心智模型在專案裡並存:一種是「拿 dict,查 `.items()`/`[cmd]` 拿檔案清單」(新寫法,兩個呼叫端在用),一種是「當它是命令清單直接 for-in」(舊寫法,第三個呼叫端還在用,靠巧合成立)。以後只要有人把 `_lint_stacks_for_diff` 內部改成用別的資料結構(例如 for-in 順序不再等於命令 first-seen 順序,或改成回 `{命令: {"files": [...], "extra": ...}}` 這種巢狀結構),`_lint_new_cmd_targets` 會在沒有任何測試翻紅提示的情況下悄悄壞掉,因為現有測試(`scripts/test_lumos.py:41502` 附近)驗的是端到端行為湊巧走同一條路,不是專門釘「只迭代仍拿到命令」這個假設本身。

（附帶查證:目前跑 `python3 scripts/test_lumos.py -k lint` 295 條全線,說明現在這一刻行為正確;這條發現談的是介面演進方式跟既有慣例不一致、留下未來悄悄漂移的縫,不是說現在就壞了。）

### 2. `_lint_cmd_with_files`「唯一實作」測試:純字串比對,可以用純格式調整繞過

severity: minor
引句:「★只准有一處在替換那個佔位符★(其他地方要呼叫共用函式,不要自己再寫一份)」
blocking: 否

`t_lint_files_substitution_has_one_implementation`(`scripts/test_lumos.py:10843`)的機械保證是逐行找字面子字串 `"replace(_LINT_NEW_FILES_TOKEN"` 或 `'replace("{LINT_FILES}"'`(`scripts/test_lumos.py:10854`),命中數不等於 1 就擋。

實際試過幾種純格式改寫,都不會被這條測試抓到,而且都不需要真的多寫一套邏輯、單純把同一行拆開或換個寫法:
- 把呼叫拆成多行(`cmd.replace(\n    _LINT_NEW_FILES_TOKEN, ...)`——`(` 後面立刻換行,子字串就斷了)
- 用變數間接:`tok = _LINT_NEW_FILES_TOKEN; cmd.replace(tok, ...)`
- 用函式型寫法:`str.replace(cmd, _LINT_NEW_FILES_TOKEN, ...)`
- 改用 `re.sub(re.escape(_LINT_NEW_FILES_TOKEN), ..., cmd)`
- 甚至只是 `replace(` 後面多一個空格:`replace( _LINT_NEW_FILES_TOKEN, ...)`

這五種寫法用同一段比對邏輯實測(離線,不動 repo)全部漏網。也就是說,這條測試守住的其實是「沒有人手殘複製貼上一模一樣的那一行」,離它自己聲稱的「機械保證,擋得住未來的分裂」有落差——分裂只要換個格式或間接一層就過關,而這正是這份 diff 通篇在檢討別人(圍欄正則、副檔名比對)犯的同一類錯:自訂的守衛比它宣稱要守住的範圍窄。目前程式裡確實只有一處在替換(已用 `grep` 查證所得,只命中 `scripts/lumos:17820`),所以現在沒有真的分裂,列為 minor。

### 3. 新的測試自我宣稱裡,呼叫端數量對不上程式碼實際的呼叫端數量

severity: minor
引句:「五個呼叫端裡只有算風險這一條漏換;冒煙、規則索引、新增告警閘三條都有換。」
blocking: 否

新測試 `t_pitfalls_lint_gets_the_changed_files` 的 docstring(`scripts/test_lumos.py:10690`)說「五個呼叫端裡只有算風險這一條漏換」,但緊接著只點名了四個:冒煙、規則索引、新增告警閘(這三個「都有換」)+ 算風險(「漏換」)。而 `_lint_cmd_with_files` 自己的 docstring(`scripts/lumos:17809`,同一份 diff 寫的)講的是「三個地方各寫一次...抽成一支就不會再漏第四個地方」——也就是總共 4 個呼叫端,不是 5 個。用 `grep -n "_lint_cmd_with_files(" scripts/lumos` 查證所得,目前程式裡確實正好是 4 個呼叫端(`17303`/`17523`/`18409`/`20938`)。這是同一份 diff 兩處自我描述的數字互相矛盾,而這份 diff 的核心賣點正是「講清楚同一件事原本分散在幾個地方」,所以這個數字落差值得修正,雖然不影響行為。

### 4. `t_pitfalls_lint_integration` 內部,同一個函式、同一份 diff,JSON 擷取寫法沒有全部換成同一種

severity: minor
引句:「data6 = _json.loads([l for l in r6.stdout.splitlines() if l.strip().startswith("{")][0])」
blocking: 否

`t_pitfalls_lint_integration` 裡原本擷取 stdout 裡那行 JSON 都是 `[l for l in ... if ...][0]` 這種「先篩選成 list 再取索引 0」的寫法。這份 diff 把其中一處(`scripts/test_lumos.py:10560` 附近)改成 `next(ln for ln in ... if ...)`,但同一個函式裡幾行之後的 `data6`(`scripts/test_lumos.py:10674`)保持原樣沒有跟著換。新加的兩支測試(`t_pitfalls_lint_gets_the_changed_files`)則從頭到尾只用 `next(...)` 這個寫法。結果是這份 diff 讓「擷取那行 JSON」這件小事在同一支測試檔裡並存兩種寫法,而且切換點就落在這份 diff 自己動過的同一個函式內——跟這份 diff 通篇在講「同一件事不要分裂成兩份寫法」的立場有點自相矛盾,雖然這裡是測試工具碼、功能完全等價,影響僅止於風格一致性,列 minor。

## 沒問題的部分(逐項確認,沒有另開一套)

- **新加的信任檢查(`_vault_write_lock`,`scripts/lumos:11161`)**:呼叫的是既有共用函式 `_trusted_private_dir`,沒有另開一套判斷邏輯。跟三個既有呼叫點比對:`_lens_cache_write`(`scripts/lumos:23980` 附近,寫入端)也是「先 mkdir、再驗信任、沒過就放棄該次寫入」的順序,跟新程式碼一致,diff 自己的註解也講清楚這個選擇(「檢查排在建資料夾之後...鄰居那幾處也是同樣順序,這是共用寫法本來就有的缺口,不是這一處特有」);`cmd_dispatch_lens_arm`/`cmd_dispatch_lens_disarm`(`scripts/lumos:24369`、`24484`)失敗時是「擋下、rc=2、印 `rm -rf <path>`」——比新程式碼嚴格,但那兩處本來要做 `rmtree`,失敗有不可逆風險,擋下合理;新程式碼只是「要不要上鎖」,失敗退回「不上鎖但照常寫」,跟它正上方既有的「鎖檔資料夾建不起來」分支(`scripts/lumos:11142` 附近,OSError 分支,同樣印訊息後 `yield`)是同一種行為,屬於同函式內既有分支的延伸,不是另開一種新風格。新訊息也是「發生什麼→為何在意→指令獨立一行」三段式,跟白話三段式規範對得上。
- **對不齊時 linter 發現不參與分級**(`scripts/lumos:20950` 附近新加的 `_tier_claims`):查過專案裡「訊號可信度不足」的既有慣例——`advisory`(顯示但不進合取/不影響 rc,例：`scripts/lumos:6395` 殘餘估計降 advisory、`scripts/lumos:7954` roster 觀測段)、`unproven`(`scripts/lumos:25384` 附近 bound-filter 的第三態:不算紅但也不算綠)——這次的「照樣列出來(資訊不丟)+不參與分級」正是同一種「降級但不隱藏」的處理方式,跟既有慣例一致,不是另開一套。
- **新測試的 fixture 寫法**:`t_pitfalls_lint_gets_the_changed_files`、`t_intake_declaration_uses_shared_fence_stripping`、`t_lint_files_substitution_has_one_implementation` 各自寫的 `git()` 閉包、假 linter 腳本產生器,都是局部於單一測試函式內的寫法——查過這個檔案本來就沒有一個模組層級共用的「建 git repo」或「造假 linter」helper(`t_pitfalls_lint_integration` 自己的 `make_repo`/`make_linter` 也只是它自己函式內的區域閉包,沒有對外開放給別的測試函式用),所以新測試各自寫一份,跟既有測試檔的組織方式是一致的,沒有應該共用卻沒共用的 helper。
