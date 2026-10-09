severity: major

## Finding 1
severity: major
blocking: 是(CI 在 main 合併後會用另一個範圍重算候選,擋下的是沒人判過的筆記,屬於會誤擋)
- spec 段落:〈設計〉重讀第一層、〈設計〉掛鉤與 CI、〈不做〉。
- 引句:「對照指紋照舊不含筆記自己的內容:筆記改了不必重判,程式改了才要。」
- 引句:「CI 那一步拿掉 `|| true` 與 `continue-on-error`。」
- 時序:
  1. PR 分支第一次推送 P1 改了程式 C1 和管它的筆記 N,N 的候選在當次範圍內,於是補了判定紀錄,對照指紋是 fp1。
  2. 第二次推送 P2 只改了 N 同樣管的另一支程式 C2,沒碰 N。
  3. 掛鉤的範圍是遠端舊值到新頂端,只含 P2。候選要求筆記在範圍內被碰過,所以 N 不是候選,本機放行。
  4. PR 以 merge commit 併進 main。CI 只在推 main 時跑(`on: push: branches: [main]`),範圍是 `BEFORE..SHA`,涵蓋整個 PR。
  5. 這次 N 是候選,頂端的對照指紋變成 fp2(C2 的 blob 變了),已提交紀錄只有 fp1。第一層判定為沒對照,CI 回 1。
- 壞在哪:
  - main 事後才紅,而且 PR 階段沒有任何閘看過這個狀態,因為 `pull_request` 事件不跑那一步(它帶 `if: github.event_name == 'push'`)。
  - 作者當時沒有任何失誤,也沒有訊號能預防。
  - RETIRE-IF 把「CI 在這兩步擋下的次數」當繞過證據,這類誤擋會灌水,導致提前撤回。
  - 在分支上合併 main 後再推,或 force-push 後再推,範圍會退到跟主線的分岔點(整支分支),同樣會重算候選。
- 查證:
  - file: `.github/workflows/ci.yml:5-8` 只在 main 推送時觸發。
  - file: `.github/workflows/ci.yml:247-264` 是現有的 reread 那一步。
  - file: `scripts/lumos:34429` 的 `_note_reread_contrast_fp` 讓指紋取決於頂端 about_code 的 blob。
  - file: `scripts/lumos:33340` 的 `_notes_touched_in_range` 用逐提交碰過算候選。
  - file: `scripts/lumos:44705` 的 `_push_range_start` 對推 main 本身會跳過所有主線候選,範圍就是 `BEFORE..SHA`。
- 我實測過:在 /tmp 的 clone 做兩個提交,c1 改程式和筆記,c2 只改程式。`c1..c2` 的候選是「沒有要對照的家筆記」,`base..c2` 的候選有 N,指紋為 552485fb05af509e,與 `base..c1` 的 5ea2acd85daa0970 不同。
- 建議:要嘛 spec 明寫「CI 重算範圍時只擋該範圍起點之後、本機推送看得到的指紋」,要嘛第一層在 CI 的 main 推送上不擋(只留推送前),要嘛推送前候選改成「分支相對主線分岔點」的累計範圍。

## Finding 2
severity: major
blocking: 是(「環境沒東西回 0」與「判不了要擋」在程式裡共用同一個原因種類,spec 沒說怎麼拆,照現況實作會自己牴觸或留繞過路)
- spec 段落:〈設計〉判不了的分法、驗收 S8、S9。
- 引句:「環境沒有可判的東西(不是 git 專案、沒有圖譜、淺層 clone、範圍沒有新東西、頂端已在主線):照舊回 0、記 `skipped` 或 `none`。」
- 時序與壞處:
  - `_note_audit_resolve` 的 `reasons` 只有 none、skipped、error 三種。
  - 淺層 clone、沒有圖譜、「讀不到頂端提交的檔案清單(git 失敗)」都記成 `skipped`。
  - spec 把前兩者歸為環境回 0,把第三者歸為判不了回 1。
  - 現在的呼叫端是 `if kind != "none": raise _NoteRereadStop(why)`。
  - 如果實作者依 spec 把 `skipped` 全當環境回 0,那 `git ls-tree` 失敗就變成靜默放行,這正是你要防的「讓某一步失敗被歸成環境沒東西」。
  - 如果全當判不了,S9 的淺層 clone 就回 1。
  - spec 只說「`_NoteRereadStop` 帶一個種類」,沒有說 `_note_audit_resolve` 的 reasons 要怎麼改。
- 另一個繞過路:「沒有圖譜」是從被推頂端的檔案清單算出來的(`vaults` 為空)。頂端提交拿掉或改名圖譜目錄就整道回 0,兩層都不跑。這要在 spec 寫明由別的閘(每支檔有家)接住,或判成要擋。
- 查證:
  - file: `scripts/lumos:33721` 淺層 clone 記為 skipped。
  - file: `scripts/lumos:33759` 讀不到檔案清單記為 skipped。
  - file: `scripts/lumos:33764` 沒有圖譜記為 skipped。
  - file: `scripts/lumos:34953` 呼叫端只分 none 與其他。
- 建議:spec 要點名 reasons 增加第四種(例如 `undecidable`),並列出每個原因字串歸哪類。

## Finding 3
severity: major
blocking: 是(表態一次就永久豁免,之後同一行因新程式變不成立,判定紀錄再點出來也不會擋)
- spec 段落:〈設計〉照留表態。
- 引句:「筆記那一行之後被改,原文對不上,表態自然失效。」
- 時序:
  1. 程式改動 A 後,判定者點出 `RULE:` 行 L,作者判斷仍成立,執行 `drift ack … --kind reread`。
  2. 數月後程式改動 B 讓 L 真的不成立,判定者再次點出 L,這次的指紋是 fp2。
  3. 第二層只用路徑、原文、種類比對表態。L 沒改,表態仍有效,於是靜默放行。
- 壞在哪:
  - reread 不收 `--tracked-in`,也不在會到期的種類裡,所以沒有任何失效機制。
  - 同族的 c2、c3、c6 綁了 related 與 seq,m1 綁了名稱,reread 沒綁任何東西。
  - 還有一個副作用:`drift ack --kind reread` 只檢查「是結構行」,不要求任何判定紀錄點過它,可以事先對整篇筆記的結構行全部表態,第二層就永久失效。
- 查證:
  - file: `scripts/lumos:37278` 的 `_drift_ack_buckets` 把非 bound、非 expiring 的種類都丟進通用 `keys` 集合。
  - file: `scripts/lumos:35039` 的 `_DRIFT_EXPIRING_KINDS` 只有 probe 與 retire。
  - file: `scripts/lumos:37453` 的 `_drift_ack_line_err` 只檢查行存在與否。
- 建議:表態記下點出它的 `contrast_fp`,或記下當時管它的 about_code blob 集合,新指紋的判定紀錄再點出同一行就要重新表態。

## Finding 4
severity: minor
blocking: 否(規格內部矛盾,不改變是否安全,但會讓驗收條款互相衝突)
- spec 段落:〈設計〉重讀第二層。
- 引句:「候選全部對照過之後才跑。」
- 引句:「第一層與第二層同時成立時兩層都印,記一筆 `blocked`。」
- 時序:第一層成立代表有候選沒對照過,第二層又規定要候選全部對照過才跑,兩句不能同時成立。實作者要嘛第二層只對已對照的子集跑,要嘛永遠兩階段擋。後者代表作者先補紀錄推一次、再被第二層擋一次,多一輪往返。
- 查證:spec 通篇沒有這個子集的定義,S7 與 S3 也沒有覆蓋「同時成立」。

## Finding 5
severity: minor
blocking: 否(CI 還是會擋,只是本機落差與失敗時看不到原因)
- spec 段落:〈設計〉掛鉤與 CI、S13。
- 引句:「推送前掛鉤的 reread-check 段應在回傳 1 或 2 時擋下推送、130 時交給中斷處理」
- 問題一:
  - 其他非零回傳碼(例如 137 被記憶體不足殺掉、143、127)規格沒講。現行掛鉤是一律印一句放行。如果只加 1、2 兩條擋,工具被外部砍掉就繞過。
  - 本機這邊的判不了「全擋」原則,在這一層破功,只剩 CI 接住。
- 問題二:
  - 掛鉤仍把標準錯誤丟掉(`scripts/hooks/pre-push:538` 的 `2>/dev/null`)。工具在 `cmd_note_audit_reread_check` 外丟出的例外,表現是 rc 1 加上看不到理由,有人會被「擋下」卻不知原因。
- 問題三:
  - `core.hooksPath` 是絕對路徑 `/Users/enzo/harness/lumos-toolchain/scripts/hooks`,所有工作樹共用主工作目錄的掛鉤。
  - 在合併前,主工作目錄掛鉤還是舊的,新分支的工具會回 1,但舊掛鉤把它吞掉(`scripts/hooks/pre-push:538-545` 現行寫法),本機不擋,等 CI 擋。
  - 反過來,新掛鉤搭舊分支的 `scripts/lumos`,若舊到沒有 reread-check 子指令,argparse 回 2 就會整支擋住,且 `LUMOS_SKIP_REREAD_CHECK` 對不認得子指令的舊工具無效。
- 建議:spec 要寫明其他非零怎麼處理,並規定掛鉤在 rc 1、2 擋下時把標準輸出轉出。

## Finding 6
severity: minor
blocking: 否(設計上是刻意取捨,但「改一個字就過」值得在 spec 寫明)
- spec 段落:〈設計〉重讀第二層。
- 引句:「那一行改掉或刪掉了就算處理過。」
- 時序:判定者點出 `RULE:` 行,作者在行內改一個字(甚至把開頭 `RULE:` 改成 `RULE :`),第二層就放行,內容仍然不成立。
- 後果:被改的行若不再以 `RULE:` 開頭,還會同時失去合約行的身分,第二層之後也不會再擋它。
- 查證:行的比對是整行去頭尾空白後精確比對。

## Finding 7
severity: minor
blocking: 否(需要作者刻意,但新的預設擋讓最省事的路就是它)
- spec 段落:〈不做〉、〈設計〉重讀第一層。
- 引句:「判定仍由編排者派,閘只讀已提交的紀錄,所以 CI 也判得出」
- 時序:第一層只要檔名前綴有已提交紀錄就算對照過。`reread-record` 收 `[]` 的報告,來源錨點不符也照收,只標 `provenance_ok: false`。被擋下時,最省事的出口是用 `reread-prepare` 產項目檔後,手寫一份空陣列報告記錄。兩道指令就能清掉整批候選。
- 查證:
  - file: `scripts/lumos:34868` 附近有 `prov_ok` 為假時仍照收的寫法。
  - file: `scripts/lumos:34697` 的 `_note_reread_committed` 只列檔名、不讀內容。
- 建議:至少讓第一層只認 `provenance_ok` 為真、或 `model-actual` 有值的紀錄;不做的話,在 RETIRE-IF 的抽樣裡納入「空紀錄占比」。

## Finding 8
severity: minor
blocking: 否(與同族閘一致,但 spec 的 RETIRE-IF 計量有盲點)
- spec 段落:〈對消費專案的影響〉、RETIRE-IF。
- 引句:「要暫緩的專案在 `.lumos/config.json` 寫 `drift_check.old_sentence` 或 `note_reread.gate` 為 warn。」
- 引句:「本機 `--no-verify` 繞過只有 CI 看得到」
- 時序:開關從被推頂端提交讀(`scripts/lumos:34467` 一帶的 `_nodehome_reader(root, tip0)`)。推送者把設定改成 warn 和觸發改動放進同一個提交,本機與 CI 都讀到 warn;`off` 還不寫帳。
- 壞處:RETIRE-IF 的三個計量(skipped-env、CI 擋下、誤報抽樣)都看不到這條路,與「繞過只有 CI 看得到」的說法不符。
- 建議:改設定的提交本身要被點名,或把這條補進計量。

## Finding 9
severity: minor
blocking: 否(目前只是 spec 缺一句規範)
- spec 段落:〈設計〉重讀第二層。
- 引句:「印每一行(路徑、頂端版行號、原文節錄、判定理由、照留指令)」
- 問題:`text` 與 `why` 來自已提交的判定紀錄 JSON,是推送者可控的內容。spec 沒有說要過 `_esc_clean` 或 `_note_reread_show`。現行第一層對路徑有這個處理(`scripts/lumos:34891` 附近),代碼審 r2 就曾因此修過。CI 日誌也會原樣印出。
- 建議:spec 加一句「所有從紀錄與筆記來的字串一律清控制字元」。

## 逐節結果
- 〈原問題與範圍〉:已讀,無 finding。治理帳數字我核對過(名稱消失 passed 35、reread reminded 18、recorded 5、none 12 吻合)。
- PRIOR-ART 與 RETIRE-IF:已讀,見 Finding 8。
- 〈設計〉名稱消失檢查開關、重讀開關:已讀,無 finding。
  - 實測 `drift check` 對 300 個提交的範圍約 18 秒(其中舊句檢查部分約 2.2 秒)。
  - `reread-check` 對整個 repo 空樹起點約 3 秒。
  - 30 秒預算在這個 repo 沒問題,逾時改擋不會讓大推送永遠推不出去。
- 〈設計〉輸出:已讀,無 finding。
- 〈驗收條款〉:見 Finding 2、4。S3、S5 到 S7、S13 沒覆蓋 Finding 1 的多次推送序列,需要補一條「兩次推送加合併」的條款。
- 〈回退〉:已讀,無 finding。

## 實務隱患鏡頭
- 守衛面:有影響,Finding 2、3、5。
- 併發與多工作樹:有影響,Finding 1、5(共用 `core.hooksPath`)。
- 不可逆:無。擋下只讓推送失敗,表態檔只追加。
- 金流:無。只動回傳碼。
- 對外送出:無。閘只讀本機版控內容。
- 資安:有影響,Finding 9。
- 效能與記憶體:無。紀錄檔目前 5 份約 20KB,實測成本低。
- 跨平台編碼:無。比對用 `strip()` 與 `\n` 切行,和紀錄產生方一致。

## 固定席節點
派工尾端沒有附固定席節點,無需逐條判。

最嚴重的是 Finding 1:CI 只在 main 推送時跑 reread-check,用整個 PR 的累計範圍重算候選,多次推送的 PR 合併後會被誤擋成紅燈;blocking 共 3 條(Finding 1、2、3)。
