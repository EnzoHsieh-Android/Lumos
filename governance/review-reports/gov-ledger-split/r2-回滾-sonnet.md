severity: major

# r2 回滾席(sonnet)審查報告

立場:收拾殘局的人。查證方式:逐節讀 spec,對照 scripts/lumos,並在暫存目錄用真的 git 重現「停止追蹤、別台機器拉取、還原提交」三步(結果見 finding 1)。

## 逐節

- 開頭 summary、盤點、範圍:已讀,無 finding(寫入器清單與判定類讀者清單抽查屬實:`scripts/lumos:1310`、`scripts/lumos:1410`、`scripts/lumos:42313`)。
- 做法 1(分流規則):已讀,無 finding。
- 做法 2(本機帳路徑):已讀,無 finding。
- 做法 3(寫入器):已讀,無 finding。
- 做法 4(忽略規則):finding 3。
- 做法 5(讀者):finding 2。
- 做法 6、驗收條款:finding 4。
- 實務隱患、回退、天花板:finding 1(回滾與已排除),另見 finding 3。

## Findings

1. 「停止追蹤不刪磁碟上的檔、還原提交即回到原行為」兩句不成立;回滾段的 `git add -f` 也是錯方向
severity: major
blocking: 是(〈已排除:不可逆〉與〈回滾〉兩段明講的安全宣稱為假,依此操作的人會丟資料或走錯步驟)
引句:「兩本帳都只追加,停止追蹤不刪磁碟上的檔,還原提交即回到原行為」
引句:「使用紀錄帳要恢復追蹤得手動 `git add -f`」
file: `scripts/lumos:16186`(`_usage_log` 每次 show/context 寫 `docs/.usage-log.jsonl`)、`scripts/lumos:20548-20600`(`_pull_source_or_abort`,source clone 的簿記帳聯集合併)
實測(暫存 repo,標準 git 行為):
- 停止追蹤那台機器本身確實不刪檔;但其他任何 clone(別台機器、別的 worktree 之外的 clone、CI 副本)`git pull` 到該提交後,磁碟上的 `docs/.usage-log.jsonl` 被 git 刪掉(實測 b 端 `ls` 只剩 `.gitignore`)。上線前的整本使用歷史在那些機器的磁碟上消失,只剩 git 歷史裡可撈。`_pull_source_or_abort` 的聯集合併路徑也一樣:拉完後只把「本機比 HEAD 多出的行」補回(`scripts/lumos:20620` 一帶 `need = _C(old_lines) - _C(base...)`),HEAD 裡的舊行不補,重建出來的是一個只有近期行的檔。
- 還原提交(`git revert`)不需要 `git add -f`:還原會自動把檔重新放回索引。實測還原後,原機器磁碟上被忽略的本機新增行(`local2`)被還原寫回的舊內容覆蓋,別台機器本機的 `mine` 也被覆蓋(git 對被忽略的檔視為可覆蓋,不報錯)。也就是回滾時「上線期間累積的使用紀錄」被靜默吃掉,而不是「得手動 add -f」。
- 兩個宣稱只對「執行 `git rm --cached` 的那一台」成立,對其餘機器不成立。
spec 該補:停止追蹤的影響是「所有人拉到後磁碟檔被刪」;回滾步驟是「先備份磁碟上的 `docs/.usage-log.jsonl` 再還原,還原後把備份的新行補回」,並刪掉 `git add -f` 那句。

2. 兩本帳合併讀時,「最近一次」類讀者的順序沒定義,混版本時會讀到舊的
severity: minor
blocking: 否(只影響 doctor 的軟提醒顯示,不影響任何判定)
引句:「doctor 的 spec-gate 比例段與 S18 度量改成讀兩本(抽一支模組層級的小函式給它們共用」
file: `scripts/lumos:2866-2878`(spec-gate-run 以「檔內最後一筆勝出」存 `_latest[節點]`)
場景:spec-gate-run 屬觀察型閘,新版寫本機帳、舊版機器(或上線前)寫版控帳。共用小函式若先讀本機帳、後讀版控帳,版控帳裡較舊的 spec-gate-run 會蓋掉本機帳較新的;反過來,舊版機器於上線後才補進版控帳的事件會蓋掉本機帳更新的。spec 只寫「兩本合起來算」「計數相同」,S3 只驗計數,沒定義「合併後按 ts 排序」。同函式給 S18(`scripts/lumos:3822` `_gov_metric_events` 回傳 oldest 與事件清單)時也要明講 oldest 取兩本的最小值,否則「讀到的最舊一筆不早於 N 週前就不判」的暖機保護會被本機帳(較新)的 oldest 錯當成整體。spec 該補:合併後依 ts 排序;S3 加一條「最近一次」與 oldest 的斷言。

3. 本機帳忽略規則「靠 init 補、沒補到只是偏吵」低估了:全域工具一更新,所有消費專案立刻開始寫本機帳,而忽略規則要等各專案跑 `lumos update`;`docs/.gitignore` 不存在的專案永遠補不到
severity: minor
blocking: 否(不影響判定,但目標「工作目錄乾淨」在這些專案達不到,且有被順手提交的路徑)
引句:「既有 vault 由 `_init_additive_setup` 補——`docs/.gitignore` 存在而缺這一行就在尾端追加,不存在就不建」
file: `scripts/lumos:20693`(`_init_additive_setup` 只在 `lumos update`/init 跑)、`scripts/lumos:20877-20881`(scaffold 的 docs/.gitignore 內容)
場景:
- 工具是每台機器一份全域安裝,hook 呼叫的是它;拉新版後第一次提交就寫本機帳,該專案的 `docs/.gitignore` 還沒補,檔案成為未追蹤檔。有人 `git add docs`/`git add -A` 就把它提交進版控,之後它是一本被追蹤、兩台機器各自追加、沒有聯集合併保護的帳(`_BOOKKEEPING_FILES` 沒有它,`scripts/lumos:24193`,`_pull_source_or_abort` 的聯集路徑也不認它)。
- 「尾端追加」沒定義檔尾沒有換行時怎麼辦:手改過的 `docs/.gitignore` 最後一行若不以換行結尾,直接接上會變成 `.ci-log.jsonl.governance-local.jsonl`,連原本的 .ci-log 忽略規則一起壞掉。
- 回滾:工具退回舊版後,上述已補進消費專案 `docs/.gitignore` 的那一行留著,無害;但若新版期間有人把本機帳提交進版控,回滾後它變成一本沒人讀、沒人忽略的追蹤檔。
spec 該補:追加前檢查檔尾換行;說明 `docs/.gitignore` 不存在的專案的處理(至少 doctor 唸一句,或寫入器在忽略規則不存在時退回版控帳);考慮把 `docs/.governance-local.jsonl` 也放進 `_BOOKKEEPING_FILES` 以免被提交時各處把它當程式改動。

4. 驗收條款沒有任何一條覆蓋回滾與混版本
severity: minor
blocking: 否
引句:「還原本案的單一功能提交(〈實務隱患〉回滾)。本機帳留在磁碟不影響任何判定;要清就刪 `docs/.governance-local.jsonl`」
file: `scripts/test_lumos.py`(S1-S5 的測試名 t_gov_split_* 對應條款,無回滾對應)
〈回退〉說「不影響任何判定」,但沒有一條條款驗:舊版讀者對「版控帳混有新版寫入的資料」不出錯(本案沒改版控帳格式,這點成立,但沒被釘住);停止追蹤的步驟與還原的行為(finding 1)沒有任何驗證。REVISIT 量的是提交數,不量回滾演練。spec 該補一條只驗檔案系統行為的條款(拉取後磁碟檔的去留),或把回滾步驟寫成可跑的指令。

## 逐類實務隱患

- 本機帳裡的紀錄(回滾後):留在磁碟、舊版不讀;上線期間的觀察型事件在舊版統計看不到(spec 已寫),判定類讀者只讀 code-loop、fix-check、design-loop 三個閘,抽查 `scripts/lumos:1250`、`10198`、`11146`、`42313`、`43295` 屬實,判定不受影響。唯一例外見 finding 2 的軟提醒顯示。
- 停止追蹤的使用紀錄帳:見 finding 1。
- 已被 init 補過 .gitignore 的消費專案:回滾後多一行無害規則,見 finding 3。
- 一台新版、一台舊版、CI 新版本機舊版:判定面一致(版控帳的內容與格式沒變,判定類讀者三個閘都不分流);統計面分歧是預期的跨機器限制(〈天花板〉2 已承認),新增的是 finding 2 的順序問題。
- 〈回退〉與〈回滾〉做得到嗎:還原提交做得到,但兩段對使用紀錄帳的描述錯誤(finding 1)。

總結:判定面的回滾安全成立,但〈已排除:不可逆〉與〈回滾〉對使用紀錄帳「不刪檔、還原即復原、需 `git add -f`」三個說法經實測為假(其他機器拉取會刪檔、還原會覆蓋磁碟上被忽略的檔),最嚴重為 major。
