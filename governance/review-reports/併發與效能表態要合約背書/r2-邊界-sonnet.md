severity: major

**E1**
severity: major
blocking: 是,只有一部分壞法被接住也拿到 strong。
kill-add 判同一條配方的鍵是 (invariant, file, old);kill-log 新三欄沒有 old;兩條配方都涵蓋同一題,A survived、B killed,合併成一組最後一筆是 killed,算出 strong;只跑部分配方也同樣。
引句:「配方=同一 node、同一 invariant、同一 file」
file: `scripts/lumos:12862` kill-add 重複判定鍵。
file: `scripts/lumos:13214` kill-log 寫入欄位沒有 old。

**E2**
severity: major
blocking: 是,spec 給的補救路徑走不通。
kill-add 遇同 invariant、同檔、同 old 直接擋下要求先手動拿掉舊的;沒有補 covers 到既有配方的方法;所有既有配方都升級不了。
引句:「寫次數或併發測試 → `guard kill-add --covers <題目id>` → `guard kill` → 重表態」
file: `scripts/lumos:12862`

**E3**
severity: major
blocking: 是,和 v1 只提醒不擋矛盾。
背書檢查放在 `_one` 的 satisfied 分支,`_one` 例外會被接成擋下;治理帳重建的記錄不驗形狀,backing 可能是壞形狀;spec 沒要求 try/except,S11 沒測壞形狀。
引句:「放進 `out["warnings"]`(獨立於 `problems`,不改 `blocked`、不改回傳碼)」
file: `scripts/lumos:37349` `_one` 例外被接成 problems。

**E4**
severity: minor
blocking: 否,只影響統計與派工單精度。
只對被標且 satisfied 的題重算;na/todo/tension 與沒被標的題手填的 backing 會原樣留著,被 gov 統計與派工單讀到。
引句:「樣板裡若已帶 `backing`,一律丟掉重算,不信任手填或 `--carry` 帶過來的值」
file: `scripts/lumos:36970` validate 不管未知欄位。
file: `scripts/lumos:37395` carry 整包帶過來只剔除 hint。

**E5**
severity: minor
blocking: 否,可由實作補上。
--covers 邊界沒定義:不存在、沒標 contract 的 id、重複、空字串。
引句:「`lumos guard kill-add` 多一個選填參數 `--covers <題目id>[,<題目id>…]`,存進配方」
file: `scripts/lumos:21493` `_stack_spec_by_id` 可直接拿來驗。

**E6**
severity: minor
blocking: 否。
讀 kill-log 沒涵蓋:非 dict 的合法 JSON 行;covers 是字串時 in 變子字串比對;空檔的原因字串不一致;四種原因的判斷順序沒說。
引句:「逐行 `json.loads`,壞行略過」
file: `scripts/lumos:13214`

**E7**
severity: minor
blocking: 否,S3 需要這些規格才寫得出。
method 只在配方迴圈內;pentry is None 的 error 列拿不到 method 或 commit;缺 run_cmd 整個 return 2 不寫 kill-log。
引句:「`commit` 改成每筆記它那一組平台跑的當下 HEAD(現行多平台時整批只記最後一組)」
file: `scripts/lumos:13068` commit 在平台迴圈內賦值。
file: `scripts/lumos:13073` 缺 run_cmd 直接回 2。

**E8**
severity: minor
blocking: 否,補 --platform 可繞過。
多平台專案配方沒帶 --platform 而綁定測試帶前綴,kill 記預設平台,與表態拆出的平台永遠對不上。
引句:「用 `_dispositions_split_test` 把 evidence 拆成(平台, 方法名),方法名照 kill 同一套正規化」
file: `scripts/lumos:13094`
file: `scripts/lumos:4580`

**E9**
severity: minor
blocking: 否,語意與統計精度問題。
off 期間寫的表態不帶 backing,改回 warn 後原因看不出;S16 把上線前與 off 期間都算進沒有背書,污染 RETIRE-IF;note 長度與換行沒上限。
引句:「`off`:寫表態時不算背書、檢查時不提醒。」
file: `scripts/lumos:7059`

**E10**
severity: minor
blocking: 否。
`_lens_dispositions_lines` 對 tail 做 [:200] 截斷,註記接在後面會被切;多組配方只能印一個 note。
引句:「被標題目的 satisfied 行尾多印「背書:強證據(配方:<note 前 40 字>)」」
file: `scripts/lumos:34835`

**E11**
severity: minor
blocking: 否,文件精度問題。
reference.md 那句實查只有一處(另一處在 SKILL.md);S17 說六個位置但列出多於六;S4 改動前也會綠;S1 沒指明比對輸入。
引句:「逐一打開列出的六個位置,確認新說法在、舊的「只驗證據存在」句旁已補被標題目的例外、範例不含毫秒斷言」
file: `skills/lumos-code-loop/reference.md:569`
file: `skills/lumos-code-loop/SKILL.md:24`

已讀,無 finding:開關(提醒實作時 cfg 初值與 null 哨兵)、單平台正規化、上萬行、validate 對多餘欄位、過期沿用 `_codeloop_record_valid`、不做、回退、合約候選。

最嚴重 severity: major;blocking 共 3 條(E1、E2、E3)。
