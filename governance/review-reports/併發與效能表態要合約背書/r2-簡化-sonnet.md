severity: major

核心機制(寫表態時算一次、存進記錄、推送前只讀)夠小,不挑;挑四周多出來的東西。緣起與現況(數字屬實)、推送前檢查、過期、天花板、不做:已讀,無 finding。實務隱患:併發、效能、資源、相容、輸出純度皆無新增。

**F1**
severity: minor
blocking: 否。method 欄只是重複記錄 test 已存的值。
引句:「`method`:實際跑的測試方法名,照 `cmd_guard_kill` 現行的正規化(有平台時去掉平台前綴、去掉 Kotlin 反引號)」
file: `scripts/lumos:13214` 已寫入 test 欄;`scripts/lumos:13119` 正規化三行;讀取端本來就要正規化,讀時對 test 正規化即可。

**F2**
severity: minor
blocking: 否。file 欄只為分組,可延後。
引句:「按配方分組(配方=同一 node、同一 invariant、同一 file)」
file: `scripts/lumos:13214` 目前不記 file;沒有同 node 同 invariant 不同 file 的實例,先用 node+invariant 分組。

**F3**
severity: major
blocking: 是。順手修的 commit 問題不屬於本案範圍,背書判定也用不到它。
引句:「同時修一個既有小問題:`commit` 改成每筆記它那一組平台跑的當下 HEAD(現行多平台時整批只記最後一組)」
file: `scripts/lumos:13070` 註解寫明多平台時記最後一組 HEAD(各 row 的 platform 欄可辨),是刻意設計;背書不讀 commit;改的是 gov 也會讀的既有欄位語意(`scripts/lumos:7291`)。應另立 Issue,從本案與 S3 拿掉。

**F4**
severity: minor
blocking: 否。_DISP_BUDGET 那段過度防禦,可縮成一句。
引句:「這一步不讀治理帳、不讀破壞測試紀錄、不跑 git,所以不增加推送前的時間,也碰不到 `_DISP_BUDGET` 超時放行的問題。」
file: `scripts/lumos:36926`

**F5**
severity: major
blocking: 是。一次標八題是基數未驗證就全標,複合題的背書會讓審查席以為整題已答完。
引句:「本 repo 是 Python,八題永遠不會在這裡觸發,效用要在消費專案量。」
file: `scripts/lumos:20971` `_STACK_QUESTION_SPECS`。建議 v1 只標單一面向、最能寫成最終狀態斷言的題(如 sql-nplus1、fe-race),複合題待有人寫出配方再加。⚠ 交編排者確認消費專案分布。

**F6**
severity: major
blocking: 是。off|warn 開關加三條驗收,與只提醒不擋自相矛盾。
引句:「`.lumos/config.json` 的 `stack_questions.contract_evidence`:`off` / `warn`,預設 `warn`;只認這兩個小寫字串」
file: `scripts/lumos:21417`。stack_questions.gate 已可整個關;嫌吵可不理或關 gate;S12、S13、S14 可整組延後到第 8 週評估。

**F7**
severity: minor
blocking: 否。派工鏡頭註記可延後。
引句:「每筆被標題目的 satisfied 行尾多印「背書:強證據(配方:<note 前 40 字>)」或「背書:沒有(<原因>)」。」
file: `scripts/lumos:34822` `_lens_dispositions_lines` 每題只印前 200 字,尾端註記會擠掉 evidence;推送前提醒已達成核心目的。

**F8**
severity: minor
blocking: 否。文件更新清單範圍大,S17 人工六處。
引句:「逐一打開列出的六個位置,確認新說法在、舊的「只驗證據存在」句旁已補被標題目的例外、範例不含毫秒斷言」
file: `skills/lumos-code-loop/SKILL.md` 等。寫測試教學是一段新內容,功能被撤就成孤兒;建議只補 kill-add --covers 說明。

**F9**
severity: major
blocking: 是。S5 到 S10 六條只是同一判定函式的分支,應合併成一個表格驅動測試。
引句:「[S6] 當 kill-log 裡對得上的紀錄都沒宣告涵蓋這一題,寫表態 應 記背書為 none [test:t_contract_backing_needs_covers]」
file: `scripts/test_lumos.py`。17 條可縮到約 8 條。

**F10**
severity: major
blocking: 是。RETIRE-IF 在消費專案量不出來,量法沒有人、沒有頻率。
引句:「量法:在各消費專案跑 `lumos gov --stats` 看表態段按題目 id 的狀態分布(本案在該段多印「有背書/沒有背書」兩個數)。」
file: `scripts/lumos:7054` 表態段只讀本機治理帳;消費專案的帳不會回傳本 repo;沒寫誰跑、多久、怎麼彙整;REVISIT 沒指定專案——回頭條件沒接電。

**F11**
severity: minor
blocking: 否。covers 參數值沒驗證。
引句:「`lumos guard kill-add` 多一個選填參數 `--covers <題目id>[,<題目id>…]`,存進配方」
file: `scripts/lumos:12809`。打錯字的 covers 永遠無法背書;用 _stack_spec_by_id 驗一次即可。

最嚴重 severity: major,blocking 共 5 條(F3、F5、F6、F9、F10)。
