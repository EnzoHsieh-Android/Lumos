severity: major

審查對象:/tmp/slots/r1.md,逐節讀完,鏡頭是資源與時序。未附固定席筆記(派工詞尾端沒有 hook 附件),所以「破壞既有節點行為或合約」這一項無從逐條判。凡寫「程式碼:行」的都是對照 repo `scripts/lumos`(rw 副本)開檔驗過語意的結果。

**R1 推送時過期檢查:判不了就擋,預算耗盡後輸出爆量**
severity: major
blocking: 是——照字面實作,大型 repo 上跟這次改動無關的推送會被擋,終端被刷滿。
- 輸入:大 repo(上萬支程式檔、上千篇筆記),一次推送新增或刪除任何一支程式檔,而且筆記裡有許多 `RULE ... [retire:事件 …符號出現]`。
- 走到哪:〈格子欄位的過期檢查〉把 `[by:]`、`[retire:事件]` 掛在存量漂移檢查的候選篩選與預算上,只寫「沿用」。
- 壞在哪:
  1. 候選篩選對不帶路徑的符號條件有一條硬規則。只要這次推送有程式檔被新增、刪除或改名(`code_shape`),所有符號條件都算候選(`scripts/lumos:29078`)。
  2. 判定時,不帶路徑的符號要讀終點與起點兩棵樹的全部程式檔(`_DriftProbeTree.corpus`,`scripts/lumos:28959`)。
  3. 既有的 REVISIT 條件是短命的,通常只有幾條。RULE 的撤除條件是長命的,可以有上千條,規模差一個量級。
  4. 全域預算是 `_DRIFT_BUDGET_SEC = 60`(`scripts/lumos:28164`),整個存量漂移檢查共用,包含頂端樹的批次讀取。
  5. 預算用完後,候選迴圈會把每個剩下的候選行各記成一條「判不了」(`scripts/lumos:29148` 起的迴圈)。
  6. 報告階段對每條「判不了」各印一段提示,沒有上限(`scripts/lumos:30433`)。
  7. 「判不了」算要處理,block 模式 rc=1(`scripts/lumos:31169` 的提示文字明講「判不了就放行等於一條繞過的路」)。
- 結果:最壞時序下,一次無關的加檔推送被擋,終端被數百到數千行「判不了」刷滿,唯一出路是 `LUMOS_SKIP_DRIFT_CHECK=1`。
- spec 缺的:對「`[retire:事件]` 判不了」的處理沒定義,也沒有輸出上限。它的原則是「只有這次改動有關的才擋」,與此衝突。
- 此項不涉及解析成本:我在 610 篇、約 6.3 萬行上實測 `_probe_lines` 全跑一遍只要 0.09 秒,所以掃描量不是問題,問題在讀程式檔語料的 I/O 和預算。
引句:「過期檢查沿用存量漂移檢查的候選篩選與預算」
佐證:`scripts/lumos:29078`、`scripts/lumos:28959`、`scripts/lumos:29148`、`scripts/lumos:30433`

**R2 擋下訊息把整行內容再印一遍:無上限、無控制字元清理**
severity: major
blocking: 是——照字面做出來的輸出路徑沒有上限,也沒有清理。
- 輸入:一次提交或推送新增大量違規行,例如整批匯入或改名沒被認成改名的筆記,每行缺好幾格。
- 走到哪:〈擋〉的「擋下訊息」要求印三樣:缺哪幾格、範本、把這一行已有內容填進範本。
- 壞在哪:
  - 現行 `_note_shape_report` 對每條違規印一行,片段只取前 60 字(`text.strip()[:60]`),違規清單與 errs 沒有筆數上限(`scripts/lumos:26481`)。
  - spec 把每條變成三段,且要回填「已有的內容」,等於放掉 60 字截斷。
  - 筆記單行可到一萬字以上(`_DRIFT_M1_LINE_MAX` 的註解說兩份圖譜最長一行 10003 字)。違規行數乘上行長,輸出量沒有上限。
  - 同檔存量漂移的列印明確做了兩件事:取前 20 筆,並對來自被推送筆記的文字做 `_esc_clean`(`scripts/lumos:30333` 之後的 `_drift_print_findings`)。筆記形狀擋沒有這兩道,回填整行內容會把未清理的筆記文字原樣印到 CI 日誌與終端。
- spec 缺的:輸出筆數上限、回填內容的長度上限與控制字元清理。
引句:「印出這一行缺哪幾格、該前綴的一行範本、把這一行已有的內容填進範本的樣子」
佐證:`scripts/lumos:26481`、`scripts/lumos:30333`

**R3 「上線點」沿用舊的,新格子規則會溯及既往**
severity: major
blocking: 是——照字面實作會讓舊行被當成新違規,並把 doctor 填滿。
- 輸入:已經裝過筆記形狀擋的消費專案,更新到有格子規則的版本。
- 走到哪:〈擋〉的「舊行」一條,以及〈擋〉第一條「掛在筆記形狀檢查」。
- 壞在哪:
  - 上線點是「提交前掛鉤含 `note-shape --staged`」那一刻(`_NOTE_SHAPE_GOLIVE_MARK`,`scripts/lumos:25443`)。這個點在舊規則上線時就定了,可能是幾個月前。
  - 格子規則若直接掛進同一支 `_note_shape_eval`,doctor 的事後掃描會從這個舊上線點到遠端頂端(最多 200 個提交,`_NS_DOCTOR_SCAN_CAP`)重算。
  - 這段期間照舊寫法寫的 WHY、PITFALL 行都會被報成「已推上遠端卻違反筆記形狀擋(多半是 --no-verify 繞過)」(`scripts/lumos:26338` 起)。
  - 推送範圍也一樣:範圍是從舊上線點截斷的,不是從新規則上線點算的。
- spec 缺的:格子規則自己的上線點(新的掛鉤標記或日期)。S1 的「舊行不查」沒有可機械判定的「舊」。
引句:「上線點之前寫好的行一律不查,也不轉換」
佐證:`scripts/lumos:25443`、`scripts/lumos:26338`

**R4 改動舊行就變成新行,「舊筆記不動」做不到**
severity: major
blocking: 是——spec 的核心承諾和偵測機制對不上,實作者會做出逼人亂填的系統。
- 輸入:只想修一個錯字或補一個連結的舊 WHY、PITFALL 行,或 `[status:superseded]` 要加在舊行上(E)。
- 走到哪:「新寫的行」的判定(`_notelines_rows`,`scripts/lumos:25730`)。
- 壞在哪:
  - 推送範圍的判法是「這行去頭尾空白後出現在逐提交新增文字集合裡」。任何字元的改動都讓整行算新行。
  - 舊行改一個字就要補齊 `[出處:]`、`[因:]` 等必有鍵;標作廢的舊行還得補 `[by:]`。
  - 舊行沒有出處的實值,作者只能填空殼,正好是 RETIRE-IF 要抽查的「為過關硬填空殼」。
  - 〈回退〉與逃生口只列單次跳過、降級開關,沒有「碰到舊行」這條。
  - 此項只涉及這道檢查的行判定;我查過 `drift fix` 各種類(c1 到 c5)寫的是正文行和 status 欄位,不改摘要行,所以修復工具本身不受影響。
- spec 缺的:碰到舊行時的豁免規則,例如「核心句沒變、只是同行搬動」或「改動只在鍵之外」。
引句:「舊寫法在舊行 應 照認、不查」
佐證:`scripts/lumos:25730`

**R5 `[retire:事件 …]` 的形狀與既有探針文法對不上,且自己的例子不合格**
severity: major
blocking: 是——S2、S8 無法按字面寫出可通過的實作與測試。
- 輸入:任何 `RULE ... [retire:事件 …]`。
- 走到哪:〈格子規格〉D 一條、RULE 例子、〈格子欄位的過期檢查〉`[retire:事件 …]` 一列。
- 壞在哪(五處):
  1. spec 自己說「值裡不能有 `]`」,事件形狀卻含 `<[[節點]] 狀態=值>`。`RETIRE_REF_RE` 是 `[^\]]*`(`scripts/lumos:3314`),會在第一個 `]` 截斷。`rule_field_truncated`(`scripts/lumos:3331`)就是為這個坑寫的。
  2. 既有探針文法沒有「`[[節點]] 狀態=值`」,只有 `when-status:<節點>=<值>`(`_probe_value_err`,`scripts/lumos:28568`)。
  3. 既有探針是 AND(全部成立才算),`_drift_probe_line` 在 `scripts/lumos:29026`。spec 的「或」沒有對應。
  4. 「檔或符號出現」對應的是 `when-file`、`when-symbol` 的存在判定,spec 沒說清是哪個鍵、是否可帶路徑。
  5. 既有探針只解析 `REVISIT:[when-…]` 開頭的行(`_probe_lines`,`scripts/lumos:28654`)。RULE 行內的 `[retire:…]` 沒有解析器,「沿用轉變判定」只是沿用 `_drift_probe_judge` 語意,解析要新寫。
- 自相矛盾:RULE 例子是 `[retire:事件 分析行程改由沙箱隔離]`,既不是節點狀態也不是檔或符號出現,照 S2 的「形狀合格」會被自己擋。
- spec 缺的:一份明確的值文法(怎麼寫節點、怎麼表達多條件)和一個解析入口。
引句:「`[retire:事件 <[[節點]] 狀態=值> 或 <檔或符號出現>]`」
佐證:`scripts/lumos:3314`、`scripts/lumos:3331`、`scripts/lumos:28568`、`scripts/lumos:28654`

**R6 `[by:]` 沒有值文法,取代鏈可能成環**
severity: major
blocking: 是——S5、S8 的判定對象沒有定義。
- 輸入:`WHY ... [status:superseded] [by:X]`。
- 走到哪:E 列、〈格子欄位的過期檢查〉`[by:…]` 列。
- 壞在哪:
  - `[by:取代者]` 的值是節點、決策編號、還是日期,都沒寫。
  - 若是節點連結,會撞上同一個 `]` 截斷問題(同 R5.1)。
  - 判定「它自己也作廢了」需要沿鏈往下走。A by B、B by A(或自指)會成環。spec 沒有環的處理,也沒有深度上限。實作者各猜各的:無限遞迴,或把環當作「沒作廢」。
  - 取代者在這次推送被刪或改名時,要靠反向索引找出所有指向它的行。spec 只寫「沿用候選篩選」。既有候選篩選是針對 REVISIT 條件寫的,沒有這個反向查找。
- spec 缺的:值文法、環與深度上限、改名時怎麼算。
引句:「指到的決策或節點不存在、或它自己也作廢了」
佐證:`scripts/lumos:28654`(既有候選機制只認 REVISIT 行)

**R7 `note_shape.slots` 與既有 `note_shape.gate` 的優先序沒定**
severity: major
blocking: 是——同一份設定會依實作者猜法有兩種行為。
- 輸入:專案設 `note_shape.gate=off` 或 `warn`,`slots` 沒寫(預設 block)。
- 壞在哪:
  - `cmd_note_shape` 在 `mode == "off"` 時直接 return,連 eval 都不跑(`scripts/lumos:26422` 一帶)。照這個順序實作,gate=off 會讓 slots 連帶失效,與「預設 block」及「所有專案」衝突。
  - spec 引的先例 `drift_check.old_sentence` 是兩個開關各管各的,gate=off 時舊句檢查照跑。照這個先例,gate=off 的專案會被新的 block 擋。
  - gate=warn 加 slots=block 的組合也沒說。
  - 既有 doctor 在 gate 不是 block 時會提醒(`_note_shape_doctor_lines`,`scripts/lumos:26268`)。slots 被關或降級沒有對應提醒。
- spec 缺的:優先序、組合表,以及 slots 降級時的 doctor 提醒。
引句:「照 `drift_check.old_sentence` 那種」
佐證:`scripts/lumos:26351`、`scripts/lumos:26422`、`scripts/lumos:26268`

**R8 分期第 0 步先於第 2 步:骨架一產出就被 lint 唸成打錯字**
severity: major
blocking: 是——照分期順序實作,中間狀態每個新筆記都有警告。
- 輸入:第 0 步上線後(`lumos new` 骨架提示已用 SEE),第 2 步還沒上。
- 壞在哪:`SYMBOL_NAMES` 沒有 SEE、LOG(`scripts/lumos:3264` 一帶)。lint 對沒收錄的符號行唸「非標準符號行……看起來像打錯字,這行不會被當成摘要」(`scripts/lumos:5415` 起)。
- 結果:第 0 步到第 2 步之間,骨架裡的 SEE 行每篇新筆記都被唸。第 1 步 S4 的「只放連結的 DEP/FLOW 應提醒改用 SEE」同樣叫人寫一個系統還不認的前綴。
- 修法方向:把 LOG、SEE 進前綴表放在第 0 步之前,或至少同步。
引句:「`lumos new` 骨架提示改用新範本與 SEE」
佐證:`scripts/lumos:5415`、`scripts/lumos:3264`

**R9 淺複製 CI:新增的檢查全部靜默跳過,spec 卻寫「CI 照擋」**
severity: minor
blocking: 否——spec 的事實錯誤,但既有 doctor 會提醒,不會做出壞系統。
- 輸入:CI 淺複製(`fetch-depth` 預設 1)。
- 壞在哪:
  - `note-shape --diff` 遇淺複製直接 `skipped-env` 並 `return 0`(`scripts/lumos:26384`)。
  - 同一檔的 `_note_audit_resolve`(`scripts/lumos:26874`)也是同樣處理。
  - 所以新的必有鍵檢查、`[by:]` 與 `[retire:事件]` 推送檢查,在淺複製 CI 都不會跑。
  - 〈實務隱患〉對 CI 淺複製與兩個同時推送都沒提。
- 缺的:在隱患節加一句「淺複製 CI 跳過,由既有 doctor 提醒補」。
引句:「`LUMOS_SKIP_NOTE_SHAPE=1` 單次跳過留帳、CI 照擋」
佐證:`scripts/lumos:26384`、`scripts/lumos:26874`

**R10 RETIRE-IF 的繞過比例量不出來;`[retire:度量]` 沒有時間窗**
severity: minor
blocking: 否——退場判準本身寫得出來,只是屆時算不出;度量那條已標「先做兩種指標」,指標怎麼定義留給實作。
- 輸入:上線 8 週後想算「被擋下後用單次跳過繞過的比例」。
- 壞在哪:
  - 跳過帳在評估之前就寫了(`scripts/lumos:26369` 起,`skipped-env`),帳上不知道這次本來會不會被格子規則擋。
  - 擋下帳的 note 欄只有「新違規 N 條」,不分是格子規則還是舊規則(`scripts/lumos:26481` 起)。
  - 所以「格子規則被繞過的比例」的分子和分母都得另外記。
  - `[retire:度量 <指標> <比較> <數字>]` 沒有時間窗。治理帳在本 repo 已有 100302 行、16 MB(`docs/.governance-log.jsonl`),整檔讀進 doctor 的成本和「累計還是近 N 週」都沒定。
- 缺的:格子規則自己的帳事件種類(例如 `slots-blocked`、`slots-skipped`),和度量的視窗定義。
引句:「擋下後用單次跳過繞過的比例超過三成」
佐證:`scripts/lumos:26369`、`scripts/lumos:26481`

**R11 `[recheck:]` 的範例不是週期;doctor 提醒沒有彙總與靜音方式**
severity: minor
blocking: 否——只影響提醒的品質,不擋。
- 輸入:範例 `[recheck:辦大型活動前]`,和一年後有幾百條 FACT 的專案。
- 壞在哪:
  - 表格寫「超過週期」,範例寫的是事件字串。非週期值怎麼處理沒定義(忽略、用來源預設、還是壞值)。
  - 沒有彙總上限,也沒有確認後的靜音方式。唯一的辦法是改日期,而改日期又觸發 R4。
  - 此項不涉及掃描量:掃摘要行是字串比對。
引句:「FACT:點數商城兌換約十幾 TPS、零競爭 [來源:生產] [觀測:2026-08-13] [recheck:辦大型活動前]」

**R12 `[test:]` 存在性檢查:spec 引的「既有」只管合約行,對應的計劃還在排隊**
severity: minor
blocking: 否——spec 已點名由路線圖 1b 負責,只是分期沒列依賴。
- 輸入:PITFALL 行 `[test:t_不存在]`。
- 壞在哪:
  - `[test:]` 解析目前只用在 ★INVARIANT★ 合約行(`invariant_test_refs`,`scripts/lumos:4600` 一帶)。
  - 漂移防治路線圖 1b「所有筆記的 `[test:]` 驗存在」狀態是「排隊」(`docs/lumos-toolchain-knowledge/Projects/漂移防治路線圖_計劃.md:36`)。
  - 在 1b 做完之前,S3 的「防回歸三選一」用一個不存在的測試名就能過。
- 缺的:在〈分期〉列出對 1b 的依賴,或在第 1 步的天花板註明。
引句:「既有綁定測試存在性檢查;路線圖 1b 那案負責所有筆記」
佐證:`scripts/lumos:4600`、`docs/lumos-toolchain-knowledge/Projects/漂移防治路線圖_計劃.md:36`

**R13 `by` 鍵同時有兩種意思,違反 spec 自己的統一原則**
severity: minor
blocking: 否——命名衝突,不影響行為。
- 壞在哪:
  - spec 原則是「同一個意思跨前綴只有一種鍵」,但 `by` 同時指取代者(`[by:取代者]`)、撤除的期限(`[retire:人裁 by:日期]`)。
  - 既有 REVISIT 的 `[by:YYYY-MM-DD]` 又是第三種意思(期限),且 `_PROBE_TOKEN_RE` 專門吃它(`scripts/lumos:28505`)。
  - 目前解析範圍不同(REVISIT 行 vs 摘要前綴行),不會撞,但 grep 或日後共用解析器時會混。
引句:「`[by:取代者]`、`[applies:路徑]`、`[test:名]`」
佐證:`scripts/lumos:28505`

**各節查證結果**
- 〈格子規格〉:已讀,有 R4(舊行)、R5、R6、R7、R13。內部交叉引用(〈待解問題〉、〈分期〉第 4 步、related 各節點、第三欄)目標都存在。
- 〈擋〉:已讀,有 R2、R3、R7、R9。
- 〈格子欄位的過期檢查〉:已讀,有 R1、R5、R6、R10、R11、R12。「時間到期只提醒」與表格一致。
- 〈分期〉:已讀,有 R8。
- 〈天花板〉、〈不做〉、〈驗收條款〉、〈回退〉、〈合約候選〉:已讀,無 finding。

**實務隱患(逐類)**
- 併發(兩個同時推送):無新增問題。spec 只新增治理帳寫入,帳是追加式的(既有行為),不寫其他共享狀態;兩個推送各自對遠端舊值算範圍,互不影響。
- 推送中途失敗:無新增問題。檢查是唯讀的,失敗後重推即可。
- CI 淺複製:見 R9。
- 大型 repo:見 R1(最壞點)。提交時的必有鍵檢查只是字串比對;我實測 610 篇約 6.3 萬行的 `_probe_lines` 全跑只要 0.09 秒,所以這部分無問題。
- doctor 掃描量:掃摘要行本身無問題,輸出量見 R11。
- 擋下訊息輸出量:見 R2、R1。
- 資源(長駐程序):無,spec 沒有開長駐程序。
- 金流、對外送出、不可逆:spec 已排除,我同意,因為只讀筆記與程式文字。

最高嚴重度:major,blocking 8 條
