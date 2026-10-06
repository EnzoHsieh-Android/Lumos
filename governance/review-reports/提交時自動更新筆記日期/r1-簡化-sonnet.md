severity: major

# 簡化鏡頭審稿:提交時自動更新筆記日期

說明:spec 實際讀的是 `/tmp/更新日期-r1.md`。派工單寫的 repo 內路徑 `docs/lumos-toolchain-knowledge/Projects/提交時自動更新筆記日期_計劃.md` 在主工作目錄不存在。d4 repo 的程式碼已對照。這次派工沒有附上牽連的合約或事故節點,所以固定席逐條判斷這一項是「無可判」,不是「不影響」。

## 前言 / 範圍(做)

## F1 「GIT_INDEX_FILE 不是預設索引就跳過」判不出來,而且會誤跳過每一次 git commit -a
severity: major
blocking: 是——spec 照寫會讓一條最常見的提交路徑整個失效,而且印出的訊息是錯的(判準:行為與宣稱相反)。

spec 段落:範圍「做」第 3 條(跳過情形)與實務隱患「指定路徑提交」。

引句:「`GIT_INDEX_FILE` 指的不是預設索引」

問題:spec 沒有定義「預設索引」怎麼比。我用 hook 實測,各種提交方式在 pre-commit 裡看到的 `GIT_INDEX_FILE` 值如下:
- 普通 `git commit`:相對路徑 `.git/index`。
- `git commit -am`:絕對路徑 `<repo>/.git/index.lock`。
- `git commit <路徑>`:`<repo>/.git/next-index-NNNN.lock`。
- `--amend`、`merge --squash` 後的提交:相對路徑 `.git/index`。

具體例:
- 輸入:改了一篇筆記正文,執行 `git commit -am x`。
- 預期:updated 被改成今天。`-a` 的臨時索引就是之後會變成真索引的那一份,掛鉤在裡面 `git add` 是安全的。
- 實際:若實作照字面比「等於 `$GIT_DIR/index`」,普通提交的相對路徑 `.git/index` 就比不等於絕對路徑。`-a` 的 `index.lock` 也不等。結果是兩者都被當成指定路徑提交而跳過。
- 印出的那句「這次是指定路徑提交,日期沒自動改」對 `-a` 是錯話。

更小的改法:判準改成只認 `next-index-*` 這個形狀,也就是真正指定路徑提交時才有的檔名。其餘(含 `index.lock`)照常做。這樣跳過條件從「不是預設」(開集合,要窮舉)縮成一個可測的字串比對。S4 也要加一個 `commit -a` 的反例。

驗證:臨時 repo 加 `.git/hooks/pre-commit` 印 `$GIT_INDEX_FILE`,依序跑 `commit`、`commit -am`、`commit <path>`、`commit --amend`、`merge --squash` 後 `commit`。

## F2 「部分暫存就 rc1 擋下」是整套設計裡最大的一塊額外機制,更小的做法是跳過那一篇、不擋
severity: minor
blocking: 否——現在的設計能運作,只是可以省掉一個擋下分支與它的整串周邊。

spec 段落:白話段、範圍「做」第 2 條、做法第 3 與 4 條、實務隱患「部分暫存」。

引句:「同一篇只暫存了一部分時,掛鉤沒辦法只改暫存的那份而不把沒暫存的也帶進去,所以擋下請整篇加入。」

問題:這一條帶出以下這些零件。
- `git diff --quiet` 的回傳碼 1 與 2 以上要分開判。
- 部分暫存清單與教學文字。
- 「已改的保持已改、重跑會跳過」的時序說明。
- Gate UB 的 rc1 擋下分支。
- S3 一條驗收。
- RETIRE-IF 的第二個撤除條件(使用者抱怨部分暫存被擋)。
- `LUMOS_SKIP_UPDATED_BUMP` 這個逃生口(見 F4)。

這個功能本來就只是便利的自動化。spec 的天花板已經承認 `--no-verify` 和指定路徑提交會漏。多一種「部分暫存的那篇這次不自動改」不改變性質。

更小的改法:部分暫存的那篇印一行「這篇只暫存一部分,updated 沒自動改」就跳過,整個 Gate UB 不擋(像 Gate CC 那樣恆 rc0)。這樣:
- 不需要擋下/重跑時序。
- 不需要跳過環境變數。
- 也不再有「擋人」帶來的使用者抱怨風險。

代價:`git add -p` 的人偶爾會留下落後的日期。這跟 spec 已接受的指定路徑提交缺口是同一類。

⚠ 判不準:專案偏好「寧可機械擋」,見記憶 prefer-mechanical-block。這條是使用者的取捨,不是工程對錯。但裁定 D4 的只有「提交時自動改」,沒有裁「部分暫存要擋」。擋不擋是 spec 自己加的設計,值得讓使用者再看一眼。

## F3 跳過條件裡 cherry-pick、revert、rebase 三項多餘,只有 MERGE_HEAD 與 SQUASH_MSG 有真實危害
severity: minor
blocking: 否——多寫的是死碼與不必要的白名單,不會壞事。

spec 段落:範圍「做」第 3 條,做法第 1 條。

引句:「合併、cherry-pick、revert、rebase 進行中、`merge --squash` 之後的提交」

問題:跳過的理由要是「暫存對 HEAD 的差異會包含別人的改動」。
- 合併:暫存差異含被合進來的全部筆記,每篇都會被改成今天。這個危害成立。
- `merge --squash`:同理成立。
- cherry-pick 與 revert:差異就是被摘的那一筆。改成今天是合理且想要的,跳過反而讓 updated 落後。
- rebase:同理。

實測:沒有衝突的 cherry-pick、revert 與 rebase 的每一步根本不觸發 pre-commit。只有衝突解完後手動 `git commit` 才會進掛鉤,這是很窄的情境。

更小的改法:跳過 `MERGE_HEAD` 與 `SQUASH_MSG` 兩項,沿用 note-shape 的 MERGE_HEAD 判斷。刪掉 `CHERRY_PICK_HEAD`、`REVERT_HEAD`、`rebase-merge`/`rebase-apply`。S4 的測試案例也少三組。這些條件是前掃加的,不是 Enzo 的裁定,可以改。

## F4 `LUMOS_SKIP_UPDATED_BUMP` 新環境變數:不擋人就不需要
severity: minor
blocking: 否——多一個開關多一份維護,不影響正確性。

spec 段落:範圍「做」第 3 條、實務隱患「部分暫存」、守衛面。

引句:「`LUMOS_SKIP_UPDATED_BUMP=1`(只認 1)」

問題:逃生口只在 Gate 會擋人時才有存在理由。依 F2,若部分暫存改成跳過,這條就只剩「不想要自動改」一種用途。現有的 `--no-verify` 已是通用逃生口。鄰居 `LUMOS_SKIP_NOTE_SHAPE` 會寫治理帳(`_gate_event_or_warn`),spec 沒說這個新開關要不要記帳。要是記,又多一段;要是不記,跟鄰居不一致,而且前面有人驗證過的「跳過要留帳」的慣例也沒對齊。

更小的改法:若保留 F2 的擋下設計,逃生口留著,但要寫明記不記帳。若採 F2 的跳過設計,整個刪除。

## F5 REVISIT 2026-11-06 的「100 篇花幾秒」量測是多餘的待辦
severity: minor
blocking: 否——是多一條要追的待辦,不是設計缺陷。

spec 段落:實務隱患後的 REVISIT 行。

引句:「REVISIT:2026-11-06 在本工具鏈量一次:一次提交 100 篇筆記時這道花幾秒;超過 5 秒就查是哪一步慢」

問題:Gate L 對每篇暫存筆記各起一個 python 跑 `lumos lint`(`scripts/hooks/pre-commit` Gate L 的 while 迴圈),註解寫每檔 <1s。100 篇的既有成本本來就是百秒等級。新指令只起一個 python、讀一次批次 blob,相對可忽略,瓶頸不在它。這條量測不會改變任何決定。

更小的改法:刪掉這行 REVISIT。要留就改成 RETIRE-IF 之外的真觸發條件,例如「單次提交總時間超過 X 秒」。

## F6 新頂層指令 `updated-bump` 的連帶同步成本,以及 `--staged` 旗標沒有第二個模式
severity: minor
blocking: 否——是同步清單與旗標的重量,功能不受影響。

spec 段落:範圍「做」第 1 與第 5 條。

引句:「新指令 `lumos updated-bump --staged [--repo <根>]`」

問題:
1. 多一個頂層指令,要同步:指令說明字典、skill 總目錄、指令總數,外加兩份速查。這些是 spec 自己列出的 5 處同步。
2. 這個指令只有 `--staged` 一個模式,沒有 `--diff` 之類的兄弟。note-shape 才有 `--staged | --diff`,所以那個旗標是在分辨模式。這裡的旗標是死的。

更小的改法:
- 不開新頂層指令,把「改日期」做成 note-shape 或 home 旁的一個動作。例如 `note-shape --staged --bump-updated`:但這會讓檢查指令開始改檔,職責混了,我不推。
- 比較乾淨的小改:指令照開,但去掉必填的 `--staged` 旗標,預設就是暫存區。

⚠ 判不準:`home check --staged`、`note-shape --staged` 兩個鄰居都帶 `--staged`,保持一致有價值。要是為了對稱留著,就不算問題。這條降為提醒。

## 做法(1–6)

已讀,無 finding(除上述各條)。

補充核對:
- 做法第 2 條要同時比對 `summary` 與正文。若把規則簡化成「暫存版本跟 HEAD 比,除了 `updated:` 那一行之外有任何差異就改」,可以不用 `parse_frontmatter` 取 summary,也不用「只改 status 就不動」的特例。
- 但這會改變使用者看得到的行為:改 status 也會改日期。Enzo 沒裁這一點,所以這裡只列為選項,不當 finding。
- 做法第 5 條說「掛鉤一開頭算好的暫存檔名清單不會因此過期」。這句成立:Gate UB 只重新 add 清單裡已有的檔。

## 回退 / 天花板

已讀,無 finding。「退回本案的提交即可」與簡化立場一致。

## 實務隱患(逐類)

- 金流、對外送出、不可逆:已讀,spec 的「已排除」三項理由成立。
- 時區:已讀,本機日期、接受跨午夜的記法。無新 finding。
- 部分暫存、指定路徑提交、被後面檢查擋下:見 F1 與 F2。
- 效能:見 F5。
- 守衛面:新增一道會擋的檢查。若採 F2 的較小做法就變成不擋,守衛面改成「不新增擋點」。

總結:最嚴重 severity 為 major,blocking 共 1 條(F1)。其餘 5 條 minor,blocking 否。
