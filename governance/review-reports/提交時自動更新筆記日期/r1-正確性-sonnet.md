severity: major

說明:spec 實際位置是 /tmp/更新日期-r1.md(圖譜路徑 docs/lumos-toolchain-knowledge/Projects/提交時自動更新筆記日期_計劃.md 在主 repo 不存在)。以下情境都在 mktemp 臨時 repo(scratchpad/t1、t1wt)用真 git 與假掛鉤實跑。派工單沒有附牽連的合約/事故節點,所以固定席那條記「無附帶節點可判」。

## F1 「GIT_INDEX_FILE 不是預設索引就整個跳過」沒有定義何謂預設,照字面做會在 worktree 裡整個失效
severity: major
blocking: 是 (使用者規則要求每個會談用獨立 git worktree,這是主要使用情境,功能等於沒上線)
段落:範圍第 3 條「GIT_INDEX_FILE 指的不是預設索引」;做法第 1 步。
引句:「GIT_INDEX_FILE 指的不是預設索引(`git commit <路徑>` 只提交指定檔時 git 用臨時索引」
問題:spec 沒寫「預設索引」怎麼判。實測掛鉤收到的值:
- 主工作目錄一般 `git commit`:GIT_INDEX_FILE=.git/index(相對路徑,而且一定有設)。
- linked worktree 一般 `git commit`:GIT_INDEX_FILE=<絕對路徑>/.git/worktrees/t1wt/index。
具體例:實作者寫「變數有設就跳過」→ 所有提交都跳過;寫「不等於 <root>/.git/index」→ worktree 裡每個一般提交都被當成指定路徑提交,印「這次是指定路徑提交」並不改日期。預期:一般提交要改;實際:全跳。
同理 `rebase-merge`/`rebase-apply` 資料夾在 worktree 裡位於 .git/worktrees/<名>/(`.git` 是檔案不是資料夾),spec 只說「資料夾」,沒說用 `git rev-parse --git-path` 解析;照字面拼 <root>/.git/rebase-merge 在 worktree 偵測不到 rebase,rebase 的 reword/edit 停下時 `commit --amend` 會被誤改。

## F2 `git commit -a` / `-p` 也被「非預設索引」誤跳過,而且訊息說謊
severity: major
blocking: 是 (-a/-am 是最常見的提交形態,掛鉤檔頭註解自己寫「-a/-am/<path>/--amend 都涵蓋」)
段落:範圍第 3 條;實務隱患「指定路徑提交」。
引句:「這種印一句「這次是指定路徑提交,日期沒自動改」」
問題:實測 `git commit -a`、`-am`、`-p` 掛鉤看到 GIT_INDEX_FILE=.git/index.lock(就是真正的索引,git 在 lock 裡 add -u);只有 `git commit <路徑>` / `--only` 才是 next-index-NNN.lock(臨時索引,在裡面 add 會讓提交帶進去但事後真索引沒有,實測 status 出現 MM,spec 這個判斷是對的)。我另外驗證:`-a` 下掛鉤 sed 改檔再 `git add`,提交內容含改動、索引與提交一致,完全安全。所以 spec 的「不是預設索引」把 -a 一起跳過,且對 -a 使用者印「指定路徑提交」是錯訊息。
具體例:`echo X >> note.md; git commit -am msg`(updated 是舊日期)→ 預期改成今天;實際跳過、印指定路徑提交。要區分只能認 `next-index-*` 或 `index.lock` 之外的臨時名,spec 沒給判準。
另:`-p` 時 `git diff --quiet` 回 1(索引與工作目錄本來就不同),若改成放行 index.lock,-p 的人會被「部分暫存」擋下且教他 `git add <檔>`,正好抵銷 -p 的意圖;spec 沒說 -p 要擋還是跳。

## F3 純改名(內容沒動)會被當成「HEAD 沒有的」而改日期
severity: major
blocking: 是 (「不該改的改了」)
段落:範圍第 1 條、做法第 1-2 步(`--no-renames --diff-filter=AM`)。
引句:「HEAD 沒有的(新檔、改名過來的)一律照同一規則」
問題:`--no-renames` 讓純 `git mv a.md c.md` 在暫存清單裡是新增 c.md;HEAD 沒有 c.md,「正文有差」成立,於是改 updated。實測 `git mv d/a.md d/c.md` 後暫存清單只剩 c.md,diff --cached --name-only 不含舊名。S6 只覆蓋「改名又改正文」,沒有「純改名不改」的條款。
具體例:把 50 篇筆記搬進子資料夾(內容零改動)→ 預期日期不動;實際 50 篇 updated 全變今天,而 updated 正是 spec 說「過期判斷與排序都看這一欄」的欄位,被整批洗成假新。要嘛 HEAD 側用 `-M` 找出改名來源比對,要嘛明寫純改名視為新增並接受,spec 兩邊都沒寫,還與「只改開頭其他欄位不動」的精神矛盾。

## F4 `--amend` 的比對基準是 HEAD(被修改的那個提交),不是它的父提交
severity: minor
blocking: 否 (邊角,結果只是日期偏新或偏舊,不污染內容)
段落:範圍第 1 條末句「`--amend` 時 HEAD 是被修改的那個提交,照同一規則」。
問題:amend 後的最終提交是「父提交→新內容」,spec 卻拿被修改的舊提交當比對。例 A:舊提交(用 --no-verify 或指定路徑提交)改了筆記正文但 updated 沒改;amend 只多加別的檔 → 該筆記與 HEAD 相同,不改,最終提交的正文改了而日期仍舊(漏改)。例 B:舊提交改了正文,amend 把正文還原成與父提交一樣 → 與 HEAD 有差就改日期,最終提交對父提交其實沒有正文差(誤改)。
(未提到 unborn HEAD:第一個提交沒有 HEAD 可讀,spec 沒寫行為;工具出錯放行,所以不致命。)

## F5 擋下訊息沒提 LUMOS_SKIP_UPDATED_BUMP,部分暫存的人被導向「整篇加入」
severity: minor
blocking: 否 (訊息措辭,有別的出口)
段落:範圍第 2 條;S3。
引句:「點名那一篇,教 `git add <檔>` 後再提交」
問題:用 `git add -p` 刻意只提交部分改動的人,被教 `git add <檔>` 等於叫他放棄意圖;跳過用的環境變數只在「實務隱患」寫,S3 驗收沒要求訊息帶它。實測 `git commit -p`(F2)與 `git add -p` 後的一般提交都會 diff --quiet 回 1。

## 逐節
- 範圍:F1-F4。已讀;「部分暫存」判定(`git diff --quiet -- <檔>` 回 1)本身我實測正確(含已暫存又被別處改、暫存後工作目錄被刪都回 1);未暫存的別人改動不會被帶進提交,因為只在回 0 才改、只換一行。
- 做法:F1、F3;步驟 5「暫存檔名清單不會過期」成立(這道只重加清單內已有的檔);但 Gate 1(日期引號污染)在 UB 之前跑,若實作換行時保留原引號寫成 `updated: "2026-10-06"`,下一次提交的 `+` 行會被 Gate 1 擋;spec 沒寫「換成無引號的 YYYY-MM-DD」,建議寫進 S1 的位元組比對(此條屬 F3 同級的未定義,但我給不出一個在現有資料上必發生的例子,不另立 finding)。
- 實務隱患:「提交被後面的檢查擋下」成立(重提交時 updated 已是今天就跳過)。「提交前掛鉤改了工作目錄……不會把沒暫存的改動帶進提交」成立。指定路徑提交的敘述正確,但誤把 -a/-p 一起算進去(F2)。
- 驗收條款:S4 的「指定路徑提交(臨時索引)」測試若用 `git commit -a` 或手設 GIT_INDEX_FILE 造情境,會鎖死 F2 的錯行為;沒有任何條款覆蓋 worktree(F1)、純改名(F3)、-a(F2)。
- 回退/天花板:已讀,無 finding(天花板第 1 條沒列 -a 被跳過,但那是 F2 的錯誤,不是天花板)。
- PRIOR-ART / RETIRE-IF / 白話 / 依據:已讀,無 finding。

## 實務隱患逐類
- 部分暫存/暫存區與提交對不上:指定路徑提交已正確排除;-a/-p 見 F2;worktree 見 F1。
- 並行會談寫同一檔:會被當部分暫存擋下,行為正確(擋而不吞)。
- 金流、對外送出、不可逆:無;只改本地筆記一行日期,可 git 還原。
- 效能:無(單次批次讀 HEAD,spec 已有 REVISIT)。
- 編碼:CRLF/BOM 的「其他位元組不動」spec 沒講行尾保留,但本 repo 筆記皆 LF,給不出具體現有檔案,不標。

最嚴重 severity: major;blocking 條數:3(F1、F2、F3)
