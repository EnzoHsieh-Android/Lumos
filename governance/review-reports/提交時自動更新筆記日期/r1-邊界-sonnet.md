severity: major

審查鏡頭:邊界與可執行。spec 檔案 /tmp/更新日期-r1.md(圖譜裡尚無 `docs/lumos-toolchain-knowledge/Projects/提交時自動更新筆記日期_計劃.md` 這個檔,以投稿檔為準)。實驗都在 mktemp 臨時 repo 跑(路徑記在 scratchpad/d4tmp),沒動 lumos-d4。
圖譜牽連節點:派工時沒有附上合約/事故節點,所以沒有固定席逐條判;我自己核對的引用:`docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md`、`docs/lumos-toolchain-knowledge/Projects/交接2026-10-03_計劃.md`、`skills/lumos-project-notes/commands/08-自動跑的.md`、`skills/lumos-project-notes/commands/03-寫回圖譜.md` 都存在,`git_last_change_dates` 在 `scripts/lumos:40798`。

## F1 「GIT_INDEX_FILE 不是預設索引就跳過」沒定義怎麼判,照字面實作會整個功能不運作或誤判
severity: major
blocking: 是 判準:最常見的提交方式會被誤歸類,功能在主場景不作用(major)。

段落:範圍第 3 條、做法第 1 步。
引句:「`GIT_INDEX_FILE` 指的不是預設索引(`git commit <路徑>` 只提交指定檔時 git 用臨時索引」
問題:spec 沒說「預設索引」怎麼比。我在臨時 repo 的 pre-commit 裡印 GIT_INDEX_FILE,實測值:
- 一般 `git commit`:相對路徑 `.git/index`(不是絕對路徑)。
- `git commit -a`(含 `-a --amend`):絕對路徑 `<repo>/.git/index.lock`,這個是真的暫存區的鎖檔,在裡面 `git add` 會進提交(實測 hook 裡改 a.md 再 add,a.md 進了該次提交)。
- `git commit <路徑>`:絕對路徑 `<repo>/.git/next-index-<PID>.lock`,臨時索引。
- 連結工作樹(worktree)的一般提交:絕對路徑 `<主repo>/.git/worktrees/wt/index`,而且是 realpath(`/private/var/...`,不是 `/var/...`),同時 GIT_DIR 也被設。
具體例:(a)實作者用「GIT_INDEX_FILE 非空且不等於 `<根>/.git/index`」判,一般提交的相對 `.git/index` 就被判成非預設,整個功能永遠不跑(S5 紅);(b)改成「非空就跳」更糟,同上;(c)用字串比絕對路徑,worktree 提交(CLAUDE.md 全域規則要求開 worktree 工作)全被跳過;(d)`git commit -a` 看起來像臨時索引被跳過,但實際上是可以安全 add 的,等於 `-am` 這個最常見用法被誤判成「指定路徑提交」,還印出錯誤訊息「這次是指定路徑提交」。
修正方向:判準寫成「`git rev-parse --git-path index` 解成 realpath 後,與 GIT_INDEX_FILE 解成 realpath 後相同」,且把 `index.lock` 結尾視為可寫(-a),`next-index-*.lock`才是臨時索引;S4 要補 -a、worktree、相對路徑三個案例。

## F2 部分暫存與 add 用的 pathspec 會被檔名裡的萬用字元騙
severity: major
blocking: 是 判準:會把沒暫存的別篇改動悄悄帶進提交,直接違反 spec 自己「不會把沒暫存的改動帶進提交」的宣稱(major)。

段落:範圍第 2 條、做法第 3 步。
引句:「改的只有 `updated:` 那一行,而且那篇工作目錄與暫存一致才改,不會把沒暫存的改動帶進提交。」
問題:spec 寫的是 `git diff --quiet -- <檔>` 與 `git add -- <檔>`,`--` 只擋旗標,不擋 pathspec 的萬用字元與魔法前綴。實測(臨時 repo):
- 筆記 `g/a[1].md` 已暫存且與工作目錄一致,同資料夾另一篇 `g/a1.md` 有未暫存改動 → `git diff --quiet -- 'g/a[1].md'` 回 1,被誤判成部分暫存,擋下整個提交,且訊息教人 `git add` 那篇,人照做也沒用(重提交仍然回 1)。
- 筆記 `g/s*.md` 與 `g/sb.md` 都有改,只暫存 `s*.md` 之後 `git add -- 'g/s*.md'` → `git status` 變成兩篇都 `M ` 已暫存,`sb.md` 沒暫存的改動被帶進提交。
檔名含 `[`、`*`、`?` 在筆記標題裡不罕見(例如「方案[v2]」)。
修正方向:所有 git 呼叫加 `--literal-pathspecs`(或 `GIT_LITERAL_PATHSPECS=1`)或路徑前綴 `:(literal)`;S3 加一個檔名含 `[` 的案例。

## F3 core.autocrlf 或 CRLF 工作目錄會讓「正文有沒有改」恆為有改,S2 失效
severity: major
blocking: 是 判準:Windows 消費專案(repo 有 get.ps1)每次碰筆記都誤判為正文改過,規則的核心判準失效(major)。

段落:做法第 2 步。
引句:「暫存版本用 `_nodehome_reader`(索引與磁碟相同直接讀磁碟),HEAD 版本用 `_nodehome_cat_blobs` 一次讀完」
問題:`_nodehome_reader`(`scripts/lumos:27409`)判「索引與磁碟相同」靠 `git diff --name-only`,而 `core.autocrlf=true` 時索引存 LF、工作目錄是 CRLF,git diff 回報「相同」(我實測:`git diff --name-only` 空、`git diff --quiet` rc=0,`git show :n.md` 是 `\n`,磁碟是 `\r\n`)。所以暫存版本讀到的是 CRLF 位元組,HEAD 那份用 cat-file 讀到的是 LF 位元組。`split_frontmatter` 用 `"\n".join` 還原,body 一邊是 `body\r\n`、一邊 `body\n`,必然「有差」。
具體例:autocrlf=true 的使用者只改 `status:`(S2 情境),body 逐行都被判為不同 → updated 被改成今天,違反「只改開頭其他欄位的不動」。反方向:summary 是用 `.strip()` 取的所以不受影響,但正文不是。
另外改 `updated:` 那一行也要保留該行的 `\r`:spec 寫「只動那一行,其他位元組不動」但沒說行尾;實作者用文字模式讀寫(Python 預設)會把整篇 CRLF 轉成 LF,動到所有位元組。
修正方向:比對前兩邊都先把 `\r\n` 正規化成 `\n`;換行用 bytes 方式讀寫並保留原行尾;S2 加 CRLF 案例。

## F4 --amend 的說明與機制自相矛盾:掛鉤認不出 amend,也拿錯比對基準
severity: major
blocking: 是 判準:spec 宣稱的行為沒有任何可執行的偵測手段,且照宣稱的基準會算錯(major)。

段落:範圍第 1 條。
引句:「`--amend` 時 HEAD 是被修改的那個提交,照同一規則。」
問題:(1)pre-commit 拿不到 amend 資訊:我實測 `git commit --amend` 的 pre-commit 環境裡 GIT_INDEX_FILE 是 `.git/index`、GIT_REFLOG_ACTION 是空,跟一般提交一模一樣,只能從父行程參數猜(ps),spec 沒寫怎麼偵測,所以實際上「照同一規則」= 拿 HEAD(被改的提交)當基準。(2)這個基準是錯的:amend 之後的提交是以 HEAD^ 為父,筆記該不該 bump 看的是跟 HEAD^ 比。
具體例:昨天提交 C1 用 `--no-verify` 改了某篇正文、updated 仍舊;今天 `git commit --amend` 只改訊息或別的檔 → 暫存版本正文跟 HEAD(C1)相同 → 跳過,C1 這篇 updated 永遠落後(spec 目標就是消除這種落後)。反例:C1 改了某篇正文且 updated 正確,amend 把正文改回 HEAD^ 的樣子只剩 status 變動 → 跟 HEAD(C1)比正文有差 → 被 bump,但淨改動沒有正文差異。
另:第一個提交(沒有 HEAD)被 amend 時,HEAD 就是該提交,HEAD^ 不存在,spec 對根提交 amend 沒講;根提交本身(無 HEAD)走「HEAD 沒有的一律照同一規則」會把每一篇有 updated 的筆記都當新檔 bump,這是合理的但 S1–S6 沒有案例。
修正方向:要嘛把 amend 從範圍移除寫進天花板(跟 `--no-verify` 並列「amend 不處理」),要嘛寫明偵測方式與以 HEAD^(根提交以空樹)為基準。

## F5 rebase 偵測寫成裸資料夾名,在 worktree 與子目錄呼叫會漏
severity: major
blocking: 是 判準:CLAUDE.md 全域規則要求每個會談開 worktree,rebase 進行中的提交會被自動 bump,污染 rebase 重寫的歷史(major)。

段落:範圍第 3 條。
引句:「有 MERGE_HEAD、CHERRY_PICK_HEAD、REVERT_HEAD、`rebase-merge`/`rebase-apply` 資料夾、SQUASH_MSG 任一」
問題:這些檔都在 git 目錄(`rev-parse --git-dir`),不是 `<根>/.git`。連結工作樹的 `.git` 是一個檔案,git 目錄是 `.git/worktrees/<名>/`(我實測 GIT_DIR 在 worktree 掛鉤裡就是那裡)。`scripts/lumos` 目前只有 MERGE_HEAD 用 `rev-parse -q --verify` 判(`scripts/lumos:30753` 起的 cmd_note_shape),沒有 CHERRY_PICK_HEAD、rebase-merge 等任何現成寫法可沿用(grep 無結果),spec 的 PRIOR-ART 說「照 note-shape 的」只涵蓋 MERGE_HEAD 這一個。
具體例:實作者寫 `os.path.exists(root/".git"/"rebase-merge")`,在 worktree 裡 rebase 衝突解完 `git commit`(或 rebase 停在 edit 時 amend)時目錄不在那個路徑,判成沒在 rebase,對重寫中的歷史改 updated;submodule 內的 repo 同理(`.git` 也是檔案)。
修正方向:一律用 `git rev-parse --git-path <名>` 取路徑再判存在,並補 S4 的 worktree 案例。

## F6 效能:逐篇 git 行程,100 篇就超過 spec 自己的 5 秒門檻
severity: major
blocking: 是 判準:spec 的 REVISIT 門檻在其 §做法 的設計下必然觸發,且一次暫存數百篇是真實情境(rtb 一輪手改幾十次、批次重寫)(major,判準:每次提交都付的成本)。

段落:做法第 3 步、REVISIT。
引句:「REVISIT:2026-11-06 在本工具鏈量一次:一次提交 100 篇筆記時這道花幾秒;超過 5 秒就查是哪一步慢」
問題:做法第 3 步對每篇各跑一次 `git diff --quiet -- <檔>` 與 `git add -- <檔>`。我在臨時 repo(400 個小檔、全部有改)實測這兩個指令逐檔迴圈 29 秒(約 7 秒/100 篇,repo 越大每次索引刷新越慢,這是最輕的情況)。而 PRIOR-ART 說讀內容已改批次(`_nodehome_cat_blobs` 一個行程),只有這段仍是逐篇。
修正方向:一次 `git diff --name-only -z --no-renames`(`_nodehome_changed_vs_disk` 已有)得到部分暫存集合,一次 `git add --pathspec-from-file=- --pathspec-file-nul`(搭配 literal pathspecs,見 F2)。

## F7 改寫 updated 那一行的規格不涵蓋實際會碰到的欄位寫法
severity: minor
blocking: 否 判準:都有 Gate L 或後續檢查兜底,最壞是被擋或不 bump,不會壞檔(minor)。

段落:做法第 2、3 步。
引句:「沒有 `updated:` 行 → 跳過」
實測 `parse_frontmatter`(`scripts/lumos:514`)對各寫法的結果,spec 都沒覆蓋:
- 帶引號 `updated: "2026-10-01"`:解析值去掉引號、lint 另報「日期加了引號」;spec 沒說改寫時引號要不要拿掉。整行換成 `updated: 2026-10-06` 才會讓 Gate L 過;若實作者保留引號,則 Gate UB 改完、Gate L 照擋。已是今天但帶引號的:判「已是今天」跳過,Gate L 擋(符合預期但 spec 沒說)。
- 兩個 `updated:` 行:`parse_frontmatter` 取最後一個,同時 lint 報重複;做法第 3 步寫「唯一一行」,沒說有兩行時怎麼辦。只換第一個的話,解析值還是後一個的舊日期,提交被 Gate L 擋,但 UB 已把半改的檔 `git add`。
- `updated:` 在 summary 區塊之後或之前:位置無差,解析都行;但 summary 內縮區塊裡的 `  updated: 2020-01-01` 這種縮排行不是頂層欄位(實測 `in_block_only` 解析得 None),實作者用 regex `^updated:` 不加縮排判斷會誤換區塊內的行 —— spec 要明寫「只認頂層、不縮排」。
- 行尾註解 `updated: 2026-10-01 # c`:解析值是整串含註解,永遠不等於今天字串,每次提交都 bump 並把註解整行吃掉。
- 空值 `updated:` 後面接清單項:只換那一行會留下孤兒清單項,開頭欄位壞掉。
- BOM 開頭的筆記:`split_frontmatter`(`scripts/lumos:503`)要求 `text.startswith("---")`,BOM 時回 None,等同「沒有開頭欄位」被靜默跳過,updated 永遠不會自動更新,也沒有任何提示。
- 沒有開頭欄位、frontmatter 沒閉合:同上跳過,合理。
修正方向:在做法第 3 步寫一條明確的取代規則(只認頂層未縮排的 `updated:`、整行換成 `updated: YYYY-MM-DD` 並保留行尾、有 0 或 >1 行就跳過並印一句),並補 S2 的案例。

## F8 檔名的 NFC 正規化與 `git cat-file --batch` 對換行檔名整批失效
severity: minor
blocking: 否 判準:前者只影響 Linux 上以 NFD 存檔名的 repo、後者要檔名含換行,觸發面小,且結果是跳過或誤 bump 而非壞檔(minor)。

段落:做法第 1、2 步。
引句:「HEAD 版本用 `_nodehome_cat_blobs` 一次讀完」
問題:(1)`_nodehome_cat_blobs`(`scripts/lumos:27821`)文件寫明路徑含 `\n` 時整批回 None;spec 沒定義 None 時怎麼做,而 HEAD 沒有該檔的單筆也是 None —— 實作者若不分辨,整批失敗會讓「所有筆記都被當新檔」全部 bump(包括只改 status 的)。(2)`_nodehome_list` 回傳的路徑經過 `nfc()`(`scripts/lumos:27364` 起),spec 做法第 1 步卻是自己用 `git diff --cached --name-only -z` 取原始清單,第 2 步又拿 `_nodehome_reader`(吃 NFC 鍵)讀;兩邊檔名寫法不一致時 `git show :<NFC路徑>` 讀不到、`git add -- <NFC路徑>` 對不上 NFD 存的檔名。macOS 預設 precomposeunicode 會掩蓋這點,中文檔名(本專案幾乎全是中文)在 Linux CI 或用 NFD 提交的 repo 才會出事,我沒法在 mac 重現,標 ⚠。
修正方向:做法第 2 步註明 None 的處理(整批 None = 工具出錯、rc 非 1 放行;單筆 None = HEAD 沒有),路徑一律沿用 git 原樣的 bytes 做 add、NFC 只當查表鍵。

## F9 工作目錄改寫沒有並行與 GUI 寫入的保護
severity: minor
blocking: 否 判準:需要有人在毫秒窗內同時寫同一篇,機率低,結果是丟掉一次編輯,git 內容與暫存區不受影響(minor)。

段落:做法第 3 步。
引句:「把工作目錄那篇開頭欄位裡唯一一行 `updated:` 換成今天(只動那一行,其他位元組不動)」
問題:`git diff --quiet` 檢查與改寫之間、以及「讀取—取代—寫回」之間都不是原子的;使用者的全域規則允許同一個 repo 有別的 Claude 會談,GUI 工具(從 GUI 觸發 hook 時編輯器開著那篇)也可能同時寫。spec 沒寫原子寫入(暫存檔、檢查、replace)、也沒寫改寫前後再驗一次內容沒變(記憶「共用檔原子寫入」記載的做法)。改寫的結果是檔案被外部程式重新載入或讓編輯器跳「檔案已被修改」。
修正方向:寫入前記下讀到的 bytes,寫入前再讀一次比對,不同就放棄並當部分暫存處理;用暫存檔 + `os.replace` 且複製原檔 mode。

## F10 Gate UB 之後被擋的提交會留下已改工作目錄 + 已 add 的半成品,spec 只說「重提交會跳過」,漏了 `git commit -a` 與 reset 的後果
severity: minor
blocking: 否 判準:spec 已承認此行為並給了重提交會跳過的理由,只差邊角說明(minor)。

段落:實務隱患「提交被後面的檢查擋下」。
引句:「這道已經把日期改好、加進暫存區;修好後重提交會跳過已是今天的,不重複改。」
具體例:使用者被 Gate L 擋下後放棄這次提交、`git restore --staged <檔>`,工作目錄那篇仍留著被改成今天的 updated(使用者沒改過那天的內容時也是)—— 一篇只是「加了 status 以外的暫存」又被取消的筆記,updated 已被動過且不會復原。另外 Gate UB 已 add 後若 Gate 1(污染指紋)或 Gate H 擋下,同樣留下。這是 spec 已接受的類型,只要補一句承認「取消提交不會回復 updated」即可。

## 逐節結果
- 白話段/依據/PRIOR-ART/RETIRE-IF:已讀。PRIOR-ART 說 note-shape 的 `rev-parse -q --verify MERGE_HEAD` 可沿用,只涵蓋 MERGE_HEAD(見 F5);`git_last_change_dates` 存在(`scripts/lumos:40798`),`_nodehome_list`/`_nodehome_reader`/`_nodehome_cat_blobs`/`split_frontmatter`/`parse_frontmatter` 都存在。壞引用:無(related 的 `交接2026-10-03_計劃`、`Systems/lumos-cli-write`、兩份 commands 檔都存在)。
- 範圍:F1、F4、F5(跳過條件的偵測)、F2(部分暫存)。
- 做法:F2、F3、F6、F7、F8、F9。
- 實務隱患:F2(「提交前掛鉤改了工作目錄」那句宣稱被推翻)、F10。「已排除」三條(金流、對外送出、不可逆)我同意:只改本地筆記一行,不連網;不可逆那句「提交前後都可 git 還原」對沒進版控的未暫存改動不成立,但 F2 的部分暫存擋與 F9 已涵蓋,所以不另立 finding。
- 驗收條款:缺案例 —— `-a`(F1)、worktree(F1/F5)、CRLF(F3)、檔名含 `[`(F2)、amend(F4)、帶引號/兩個 updated/BOM(F7)、首個提交(無 HEAD)。S6 排在 S5 前面的編號順序無妨。另 S4 寫「rc0」但指定路徑那種要「印一句」,測試條款沒要求驗那句。
- 回退、天花板:已讀,無 finding。(天花板第 1 條只列 `git commit <路徑>`,但依 F1 實測,`-a` 在字面實作下也會被跳過或誤判,應一併寫明。)

## 實務隱患清單(風險類逐類)
- 並行寫入:有,F9。
- 路徑與跳脫(萬用字元、換行、NFC):有,F2、F8。
- 換行與編碼(CRLF、BOM):有,F3、F7。
- 部分暫存與 git 內部狀態(臨時索引、worktree、amend、rebase):有,F1、F4、F5。
- 效能與規模(數百篇):有,F6。
- 金流:無,只改筆記日期欄。
- 對外送出:無,不連網。
- 不可逆:無,改的是要提交的筆記(F9 的丟失編輯屬並行寫入類)。
- 資安:無新增面;`git add` 的檔案清單來自 git 自己的暫存清單,不來自使用者輸入字串拼接(但 F2 的 pathspec 解讀要用 literal)。

severity 最高:major;blocking 條數:6(F1–F6),non-blocking 4(F7–F10)。
