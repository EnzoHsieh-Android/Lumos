---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/lumos-cli-write
related:
  - "[[Projects/交接2026-10-03_計劃]]"
summary: |-
  WHY:提交前掛鉤自動把這次提交裡正文或摘要真的改過的圖譜筆記,開頭的 updated 改成今天再一起提交(新指令 `lumos updated-bump --staged`);同一篇只暫存了一部分就擋下請整篇加入 [出處:2026-10-06 消費專案 rtb 第三輪回饋的 D4 項;Enzo 2026-10-06 裁「提交時自動改」] [因:updated 靠人記得 lumos set,實測抽 15 篇有 5 篇落後 git 實際改動日期(`git_last_change_dates` 的說明),rtb 這輪手改了幾十次;讀筆記的人與排序、過期判斷都看這一欄] [不選:健檢列出加一鍵修(要有人看到提醒才會修,存量會一直長);提交後另做一個提交補日期(多一個提交、推送前要壓)]
---
# 提交時自動更新筆記日期_計劃

白話:每篇筆記開頭有一欄 `updated`(最後更新日期),靠人改完內容記得用 `lumos set` 改它;常常忘,實測抽 15 篇有 5 篇落後。這次讓提交前的掛鉤自動做:這次提交裡,正文或摘要真的改過的筆記,把 `updated` 改成今天,再一起提交。只改開頭其他欄位(例如狀態)的不動。同一篇只暫存了一部分時,掛鉤沒辦法只改暫存的那份而不把沒暫存的也帶進去,所以擋下請整篇加入。

依據:Enzo 2026-10-06 裁定「提交時自動改」(三選一:提交時自動改 / 健檢列出加一鍵修 / 兩個都做)。

PRIOR-ART: 提交前掛鉤已經逐篇對暫存的圖譜筆記跑 `lumos lint`(Gate L)、`home check --staged`、`note-shape --staged`;讀暫存清單與內容沿用 note-shape 的 `_nodehome_list(root, "index")` 與 `_nodehome_reader`(索引與磁碟相同直接讀磁碟),HEAD 版本用 `_nodehome_cat_blobs` 一次批次讀;合併中的判斷照 note-shape 的 `rev-parse -q --verify MERGE_HEAD`;改 `updated` 那一行自寫一支只換那一行的小函式;本機日期照專案慣例 `datetime.now(timezone.utc).astimezone().date()`。lint-staged、pre-commit 框架的「hook 改檔後重新 git add」是業界常見做法,它們同樣遇到「部分暫存」的問題,常見處理是暫存區與工作區不一致就擋或先 stash——本案選擋。
RETIRE-IF: 2027-01-06 抽 20 篇最近三個月改過的筆記,`updated` 落後 git 實際改動日期的仍超過 2 篇(表示掛鉤沒在跑或被繞過),或使用者回報部分暫存被擋造成的困擾多過省下的手改,就撤掉改回健檢提醒。

## 範圍

- 做:新指令 `lumos updated-bump --staged [--repo <根>]`:對暫存區裡圖譜資料夾底下新增或修改的 `.md`(改名視為新增),比對暫存版本與 HEAD 版本——正文(開頭欄位之後)或 `summary` 欄位有差,而且暫存版本的 `updated` 不是今天 → 把工作目錄那篇的 `updated:` 行改成今天,再 `git add` 那一篇。HEAD 沒有的(新檔、改名過來的)一律照同一規則。印改了哪幾篇。`--amend` 時 HEAD 是被修改的那個提交,照同一規則。
- 做:「部分暫存」= 那一篇工作目錄的內容跟暫存區不一樣(`git diff --quiet -- <檔>` 回 1)→ 不改、rc1 擋下,點名那一篇,教 `git add <檔>` 後再提交;`git diff` 自己出錯(回 2 以上)當工具出錯、那篇跳過。
- 做:以下情形整個跳過、rc0:沒有 `updated:` 欄的那篇不加;合併、cherry-pick、revert、rebase 進行中、`merge --squash` 之後的提交(有 MERGE_HEAD、CHERRY_PICK_HEAD、REVERT_HEAD、`rebase-merge`/`rebase-apply` 資料夾、SQUASH_MSG 任一);`GIT_INDEX_FILE` 指的不是預設索引(`git commit <路徑>` 只提交指定檔時 git 用臨時索引,在裡面 `git add` 會讓真正的暫存區跟提交對不上)——這種印一句「這次是指定路徑提交,日期沒自動改」;`LUMOS_SKIP_UPDATED_BUMP=1`(只認 1)。
- 做:提交前掛鉤新增一道「Gate UB」(Gate PY 之後、Gate L 之前):照 home check 的回傳碼規矩——rc1 擋,其他非零(工具出錯)放行。
- 做:指令說明字典、skill 總目錄、指令總數同步;`commands/08-自動跑的.md` 提交前那列補這一道;`commands/03-寫回圖譜.md`「改狀態/日期/類型」那列補一句「updated 提交時會自動改」。
- 不做:推送前或 CI 再檢查一次;存量的落後。

## 做法

1. `cmd_updated_bump(repo, staged)`:專案根與圖譜資料夾照 `note-shape --staged`;`git diff --cached --name-only --no-renames --diff-filter=AM -z` 取暫存清單,只留圖譜資料夾底下的 `.md`;先判範圍第 3 條的跳過情形。
2. 內容:暫存版本用 `_nodehome_reader`(索引與磁碟相同直接讀磁碟),HEAD 版本用 `_nodehome_cat_blobs` 一次讀完;`split_frontmatter` 拆開、`parse_frontmatter` 取 `summary` 與 `updated`;正文或摘要相同 → 跳過;暫存版本 `updated` 已是今天 → 跳過;沒有 `updated:` 行 → 跳過。
3. 要改的那篇:部分暫存 → 收進清單;否則把工作目錄那篇開頭欄位裡唯一一行 `updated:` 換成今天(只動那一行,其他位元組不動),`git add -- <檔>`。
4. 有部分暫存的 → 印清單與教法、rc1(已改的那幾篇保持已改、已加入;重跑會跳過已是今天的)。
5. 提交前掛鉤加 Gate UB(見範圍第 4 條);掛鉤一開頭算好的暫存檔名清單不會因此過期(這道只重新加入清單裡已有的檔)。
6. 寫回 [[Systems/lumos-cli-write]];兩份 skill 速查照範圍第 5 條。

## 實務隱患

- **部分暫存**:會擋;用 `git add -p` 只提交部分改動的人要先整篇加入或 `LUMOS_SKIP_UPDATED_BUMP=1`。
- **指定路徑提交**:`git commit <路徑>` 不自動改日期(臨時索引的限制),會印一句;這種提交的 updated 照舊可能落後。
- **提交被後面的檢查擋下**:這道已經把日期改好、加進暫存區;修好後重提交會跳過已是今天的,不重複改。
- **時區**:本機日期;跨午夜提交的那篇記成提交當下的本機日期,接受。
- **提交前掛鉤改了工作目錄**:改的只有 `updated:` 那一行,而且那篇工作目錄與暫存一致才改,不會把沒暫存的改動帶進提交。
- 已排除:金流:只改筆記的日期欄,不碰任何金流
- 已排除:對外送出:不連網、不送任何東西出去
- 已排除:不可逆:改的是要提交的筆記,提交前後都可 git 還原
- 守衛面:新增一道會擋的提交前檢查(部分暫存時擋),不放寬任何既有檢查;擋的情況有單次跳過的環境變數

REVISIT:2026-11-06 在本工具鏈量一次:一次提交 100 篇筆記時這道花幾秒;超過 5 秒就查是哪一步慢

## 驗收條款

- [S1] 當暫存的筆記正文或摘要改過、updated 不是今天時,updated-bump 應 把它改成今天並加入暫存,其他位元組不動 [test:t_updated_bump_bumps]
- [S2] 當暫存的筆記只改了開頭其他欄位(例如 status)、或 updated 已是今天、或沒有 updated 欄時,updated-bump 應 不動它 [test:t_updated_bump_skips]
- [S3] 當要改的筆記工作目錄跟暫存不一樣(部分暫存)時,updated-bump 應 rc1、不改那一篇、點名並教 git add [test:t_updated_bump_partial]
- [S4] 當是合併、cherry-pick、rebase 進行中、指定路徑提交(臨時索引),或 LUMOS_SKIP_UPDATED_BUMP=1 時,updated-bump 應 什麼都不改、rc0 [test:t_updated_bump_skip_switches]
- [S6] 當筆記被 git mv 改名又改了正文時,updated-bump 應 照樣改它的 updated [test:t_updated_bump_bumps]
- [S5] 當透過提交前掛鉤提交一篇改過正文的筆記時,提交進去的版本 updated 應 是今天;部分暫存時掛鉤 應 擋下 [test:t_precommit_updated_bump]

## 回退

退回本案的提交即可:只新增一個指令與掛鉤裡一段呼叫;退回後 updated 回到靠人改。消費專案要 `lumos update` 才拿到新掛鉤。

## 天花板

1. `--no-verify` 繞過提交前掛鉤、`git commit <路徑>` 指定路徑提交時不會改。
2. 只管這次提交碰到的筆記,存量的落後不處理。
