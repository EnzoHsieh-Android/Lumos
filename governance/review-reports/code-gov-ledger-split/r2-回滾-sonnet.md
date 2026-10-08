severity: minor

## F1 整份替換會把使用者的 docs/.gitignore 捷徑換成一般檔,revert 不會還原
severity: minor
blocking: 否
引句:「        _write_lf(gi, (raw + chunk).decode("utf-8"))」
file: `/home/user/Lumos/scripts/lumos:21072`(_ensure_docs_gitignore,_write_lf 在 17727)
失敗場景:消費專案的 docs/.gitignore 被提交成捷徑(例如指向 ../.gitignore 或共用設定檔)。跑 lumos update 或 init 時,_write_lf 先寫暫存檔再 os.replace,捷徑本身被換成一般檔。實測(臨時目錄):docs/.gitignore -> ../other/g,補行後 is_symlink 為 False,目標檔內容原樣、沒有那兩行。結果:
1. 該檔在 git 裡是 typechange(模式 120000 變 100644),工作目錄變髒,正是本案要消除的狀態。
2. 還原本案提交不會把捷徑接回去。〈回退〉只說「多出的兩行無害」,沒提這個。
3. 目標檔被別的專案共用時,本專案和共用來源從此分岔。
同一種不可逆也出現在硬連結:實測 os.link 後補行,docs/.gitignore 的 nlink 變 1,另一個連結仍是舊內容,兩邊分家。
補充:讀(read_bytes)到替換(os.replace)之間沒有鎖,這段時間使用者在編輯器存檔的改動會被整份蓋掉;改版前的就地追加不會丟這種寫入。這條沒實跑,只列為併發面,不單獨計分。
測試 ④「docs/.gitignore 是捷徑」把這個行為當成預期寫死,所以不會翻紅。
重現(minor,可重現):mkdir docs other; echo node_modules > other/g; ln -s ../other/g docs/.gitignore; 呼叫 _ensure_docs_gitignore(Path("docs")); 再看 test -L docs/.gitignore,得 1(不是捷徑),other/g 無新增行。

## F2 度量撤除條件在新舊版並存時兩邊判定相反,〈回退〉沒寫到
severity: minor
blocking: 否
引句:「        first = oldest_local if (gate, kind) in _GOV_LOCAL_PAIRS else oldest」
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:94`(〈實務隱患〉回滾段)
佐證:新版把 check-s.warned 這類觀察寫進本機帳,版控帳不再增加。舊版的 _doctor_metric_lines 只讀版控帳,暖機護欄看版控帳最舊一筆。
失敗場景:RULE 寫 [retire:度量 check-s.warned == 0 近4週],團隊一台升級、一台沒升級,或整體回滾後仍有人用新版寫出的版控帳。
1. 升級那台:新版自己讀本機帳,有事件就不判,結果正確。
2. 沒升級、或回滾後的舊版機器:版控帳最舊一筆早於 4 週,暖機放行,版控帳近 4 週 check-s.warned 為 0(新版機器的事件都在各自本機帳),判成「該撤」。
3. 新版在新 clone 或 CI 的機器:本機帳不在,不判。
同一條規則兩台機器一台喊該撤、一台沉默,而且喊的那台是誤報。這不是版本偏差,是版控帳不再增加事件造成的。
〈回退〉只寫「舊版的 --nags 只看版控帳會少報」,沒提度量撤除條件會多報。因為 doctor --ci 不跑 S18,所以只影響本機 doctor 的軟提醒,不擋推送,故判 minor。
重現(未能重現舊版,沒有舊版副本可跑):推論來自舊版只讀版控帳這一點,新版回歸測試 ① 只涵蓋新版自己的行為。

## F3 計劃〈做法〉5 還寫「不整檔改寫、二進位追加」,與程式現況相反
severity: minor
blocking: 否
引句:「      整份經 _write_lf 原子替換,不就地追加(代碼審 r1:兩個程序同時補,追加會補兩份;替換時兩邊寫的是同一份內容。」
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:73`
失敗場景:計劃〈做法〉5 仍寫「缺的用二進位追加到尾端……不整檔改寫」,程式已改成整份原子替換。下一個依計劃做回退或排查的人,會以為 docs/.gitignore 的捷徑、硬連結、擁有者不受影響(F1)。驗收條款 [S5] 也沒寫捷徑被換成一般檔的行為。〈實作紀錄〉最後一條有講,但它是流水帳,規則段沒改。

## 已走過沒問題的範圍
- 權限與 CRLF:_write_lf 用 copymode 沿用原檔權限,位元組往返(decode 後 encode)保留 CRLF 和 BOM;實測一般檔路徑沒壞。
- 本機帳是捷徑:_gate_event 與 _append_governance_log 都在開檔前判 is_symlink 並略過。_gate_event 回 False,走 _gate_event_or_warn 只印警告、不改判定;被提交的捷徑不會讓閘改判。
- 本機帳寫入失敗不連累版控帳:兩本各自 try。
- 回退時的未追蹤檔問題:〈回退〉要求先刪本機帳、每個 worktree 各一份,與程式現況一致(根 .gitignore 兩行跟著還原消失;_BOOKKEEPING_FILES 含新檔名,新版內部帶進提交也不會讓留痕失效,舊版沒有)。
- 度量暖機護欄的新版內部判定:本機帳不在時略過,不再誤報;合讀時間排序與壞行處理讀檔尾、只跳壞行。
- 不是 UTF-8 的 .gitignore:decode 失敗被接住,不動。

只有文件與邊角的小問題,沒有擋回退的缺陷。
