severity: major

審查鏡頭:邊界與可執行。對照 /Users/enzo/harness/lumos-d3(唯讀,只在記憶體載入 scripts/lumos 跑了兩個單行驗證)。
圖譜鏡頭:派工時沒有附上合約/事故節點,無節點可逐條判;本席只能說:本案不改 kill 的跑法與任何閘的判定,對 guard-kill 既有合約「不影響」(只多 stderr 一行與 doctor 一則 warn_soft),唯一會碰到的記帳面在 F1。

## F1 新閘名沒登記,落帳靜默失敗
severity: major
blocking: 是 — 驗收條款與 RETIRE-IF 都靠這筆帳,照字面實作帳寫不出去。
spec 範圍第二條:「gov_events 記 `check-p2t`」。現況:`scripts/lumos:1486` 閘名不在 `_KNOWN_GATES`(`scripts/lumos:7993`,P2 的兩個閘登記在 `scripts/lumos:8022`、`scripts/lumos:8024`)就印一行警告、不寫帳;doctor 的 warned 要進本機帳還得列進 `_GOV_LOCAL_PAIRS`(`scripts/lumos:1329`)。spec 的「做」與 PRIOR-ART 都沒提這兩處。
具體例:照字面只在 doctor 多一段 `gov_events.append({"gate": "check-p2t", ...})` → `--ci` 時 `check-p2t` 不在名單,帳零筆。RETIRE-IF「連續 60 天這一則提醒 0 筆」永遠成立,機制在還沒被證明沒用之前就會被判該撤。
引句:「gov_events 記 `check-p2t`;自己一個例外保護。不跑 git。」
需要補:把 `check-p2t` 登記進 `_KNOWN_GATES` 與 `_GOV_LOCAL_PAIRS`,並在 S2 加一句斷言(照 `scripts/test_lumos.py:66750` 對 `check-p2s` 的寫法)。

## F2 Kotlin 反引號與前後空白:合約側不拆殼,配方側拆,同一支測試必判「不在清單」
severity: major
blocking: 是 — 對正確綁定的 Kotlin 專案每條都誤報。
spec PRIOR-ART:「兩邊比 (平台, 方法) 對,不比字串」,但合約側用 `resolve_test_refs`(`scripts/lumos:5619`)、配方側用 `_kill_method_name`(`scripts/lumos:14650`)。前者不去反引號、後者去反引號且不去空白。實測:
`resolve_test_refs("…[test:`foo bar`, kotlin: Baz]", {"kotlin":1}, "kotlin")` → `[('kotlin','`foo bar`'), ('kotlin','Baz')]`
`_kill_method_name("`foo bar`", False)` → `foo bar`;`_kill_method_name("kotlin: Baz", True)` → `' Baz'`(前面有空白;`_KILL_METHOD_OK_RE` 允許 `[\w .]+`,`scripts/lumos:14616`)。
具體例:合約 `[test:`foo bar`]`、配方 test 為 `` `foo bar` `` → 實際是同一支,比對 `('kotlin','`foo bar`')` 對 `('kotlin','foo bar')` 不等 → kill-add 誤報、doctor 誤列。配方 test 寫成 `kotlin: Baz` 同理。
引句:「配方這一側照 guard kill 實際的跑法取 (配方的 platform 欄或預設平台, `_kill_method_name(test, 多平台))`」
S1/S2 兩條條款都沒有反引號或空白的案例,測試過得了、真專案會炸。需要:兩側都先 strip 空白再 strip 反引號(同一支正規化函式),並在條款加 Kotlin 反引號、前綴後帶空白兩格。

## F3 單平台(legacy)時 resolve_test_refs 的平台參數要傳 {},spec 沒講
severity: major
blocking: 是 — 照字面傳「平台表」會在單平台專案丟 ValueError 或誤切。
`resolve_test_refs` 的說明(`scripts/lumos:5619` 起):platforms 空才是 legacy 不切分,「由呼叫端在 multiplatform=False 時傳 {}」。但 `load_platforms` 在 legacy 回的 `platforms` 是帶一個條目的 dict(`scripts/lumos:5555` 附近)。spec 寫的是 `resolve_test_refs(合約行, 平台表, 預設平台)`,沒說要看 `pdata["multiplatform"]`。
具體例:單平台專案,合約 `[test:t_a:b]`(名字含冒號的假想 ref)→ 傳整張表會按冒號切、前綴 `t_a` 不在表 → ValueError → spec 規定「不比、不提醒」,結果該提醒的靜默吞掉;反之配方側 `_kill_method_name(…, False)` 不切分,兩側解讀不一致。
需要:spec 寫明「multiplatform 為 False 時傳 {}」,條款補單平台一格。

## F4 設定檔讀不了、平台不在設定裡、配方欄位型別壞:spec 沒定義行為
severity: major
blocking: 是 — 兩條路徑都要用 `pdata`,spec 對失敗分支一字未提。
- 設定檔讀不了:`_kill_cfg_load` 回 `(None, err)`,ctx 裡 `cfg_err` 非空、`pdata` 為 None(`scripts/lumos:14715`)。第三個提醒取 `pdata["default_platform"]` 會 TypeError。P2 第一則遇到 cfg_err 的做法是整段改印「先跳過」(`scripts/lumos:3369`);第三則該照做,spec 沒說。kill-add 端 `_kill_add_warn` 本身有判斷,新提醒沒有。
- 配方 `platform` 是清單/物件:`_kill_recipe_judge` 專門防 unhashable(`scripts/lumos:14825`),spec 的「(平台,方法) 不在清單解析出的集合裡」做集合/`in` 比對會 TypeError;平台不在 `pdata["platforms"]` 時該判「判不了」還是「不在清單」也沒定。
- 配方不是 dict(例如 `["x"]`、字串):`r.get` 崩潰。spec 只說「各提醒自己一個例外保護」,整個第三則就此中斷,同一篇、同一庫其餘配方都不比對。`_kill_p2_scan` 是每條、每篇各自包保護(`scripts/lumos:15028`)。
- 沒有配方的專案:P2 刻意「沒有配方的專案完全不碰設定」(`scripts/lumos:15141`),第三則要共用 `_p2["ctx"]`,spec 沒講共用;若自己再 `_kill_check_ctx` 就多讀一次設定,且 `_p2` 為 None(第一則例外)時沒定義。
需要:列出這幾個分支各自「跳過/計入『判不了 N 條』/照列」,並每條配方各自包例外保護。

## F5 「沒帶 --test 就一定不會觸發」與同一段的「含只更新 covers 沿用的既有配方」互相矛盾,且前者不成立
severity: major
blocking: 是 — 條款 S1 的行為有兩種讀法,實作者必須猜。
範圍第一條:「沒帶 `--test` 時配方的測試一定取自清單,不會觸發」,但前一句才說含「只更新 covers」那條路徑沿用的既有配方。只更新 covers 時通常不帶 --test(`_guard_kill_add_locked` 的 `test_arg is None` 容許,`scripts/lumos:15259` 起),此時比對的是既有配方的 test,可能早就不在清單 → 每次補 covers 都重複被提醒,與 S1 開頭「`--test` 不在清單上時」的觸發條件對不上。
另外「一定取自清單」本身不成立:`test is None` 時取 `refs[0]`(含 `android:Foo` 前綴),但 `recipe` 的 platform 取 `--platform`(沒帶=預設平台)。實例:多平台、預設 `kotlin`、合約 `[test:android:Foo]`,`kill-add … --platform kotlin` 不帶 --test → 配方 (kotlin,Foo) vs 清單 (android,Foo) 不等,觸發。
引句:「沒帶 `--test` 時配方的測試一定取自清單,不會觸發。」
需要:定義觸發條件是「寫入的那條配方的 (平台,方法) 不在清單」,不看有沒有帶 --test;補「只更新 covers」與「--platform 與前綴不一致」兩格,並決定 covers-only 是否印。

## F6 kill-add 端「那條合約行」怎麼取得沒定義,鎖外重讀有競態
severity: major
blocking: 是 — 實作路徑未定,兩種實作行為不同。
PRIOR-ART 說配方對回合約行用 `extract_contracts` 加「含片段」。但 kill-add 在鎖內 `_guard_kill_add_locked` 已用 `INVARIANT_RE` 定位出唯一的 `line`(`scripts/lumos:15259` 起),而且 `warn_box` 只放 recipe、不放 line(`_kill_add_after_lock`,`scripts/lumos:15217`);提醒在放鎖後跑(spec 也這樣要求)。若在鎖外重讀筆記再比,別的會談可能剛 `guard bind` 或改了 KEY 行,比對的就不是這次寫入看的那條。再者定位規則兩邊不一樣:kill-add 的 `invariant_substr in INV_TAG_RE.sub("", line)` 比的是含 `KEY: ★INVARIANT★` 前綴的整行,`extract_contracts` 只回 `group(1)`(前綴之後)。實例:配方 invariant 填 `INVARIANT` 或 `KEY`,kill-add 時對到,doctor 對不回 → 同一條配方一邊比、一邊進「對不回」。
需要:spec 明寫「kill-add 沿用鎖內 `line`(把它放進 warn_box)」;doctor 側定位規則與 kill-add 對齊(同一支函式),別各寫一份。

## F7 doctor 對 invariant 欄位的邊界:空字串、非字串、純空白
severity: minor
blocking: 否 — 只在手改欄位時出現,後果是多/少一則提醒,不會寫壞資料。
doctor 說「恰好對到一行」。配方 `invariant` 為 `""`(空字串是任何字串的子字串)時,一篇只有一條合約就「恰好對到」,被誤歸到那條合約並拿它的清單比;非字串(數字、null)做 `in` 會 TypeError(被 F4 的保護吞掉整則)。P2 現況對 invariant 非字串是當 `""` 處理(`scripts/lumos:15141` 起的 `inv = … else ""`),不會誤對。
具體例:`kill_recipes: [{"invariant":"","test":"x",…}]` 的筆記只有一條合約 → 被判「測試不在清單上」列出。需要:空白 invariant 直接歸入「對不回」。

## F8 配方 test 缺欄/空字串/非字串:與 P2 第一則重複報,且訊息空洞
severity: minor
blocking: 否 — 只是重複噪音。
`_kill_method_name(None/"" , …)` 回 `""`(實測),不在任何清單 → 第三則列一條「配方的測試:(空)」。但這種配方在 P2 第一則已因 test 名不合法被列為 malformed(`_kill_recipe_judge`,`scripts/lumos:14846`),同一條在同一段被報兩次、第三則還叫人去 `guard bind` 一個空名字。kill-add 側 `--test ""` 同樣會寫入空 test(`test_arg is not None`),然後印出叫人綁空名字的提醒。需要:test 名不合法的配方在第三則跳過(第一則已管)。

## F9 輸出量與清單長度沒有上限
severity: minor
blocking: 否 — 不影響判定,只影響可讀。
「同一條合約綁很多測試」時 kill-add 訊息講「清單上那幾支」若逐支列出,單行可到數百字;doctor 對大量配方(rtb 一庫 73 條,見 `scripts/lumos:14815` 一帶註解的數字)逐條列且每條附 `lumos guard bind` 指令形狀,輸出隨配方線性成長。P2 第一則同樣逐條列,故不是新問題,但 spec 既然特別要求「只印一行筆數、不逐條列」給對不回的,對這一則也該說明是否截斷。具體例:一條合約綁 40 支、kill-add 帶 1 支清單外測試 → 一行列 40 個名字。建議條款明寫「清單只印前幾支加總數」或「不列清單」。

## F10 `guard bind` 的指令形狀會誤導多平台與空清單情境
severity: minor
blocking: 否 — 提醒文字不準,不影響行為。
`lumos guard bind <node> <invariant> <method> [--platform P]`(`--help` 驗過)。提醒寫「`lumos guard bind`」若沒帶 `--platform`,多平台配方在非預設平台時,照提醒原樣貼上會綁到預設平台,提醒下一次 doctor 仍判不在清單(因為綁錯平台)。spec「附 `lumos guard bind` 的指令形狀」沒說要帶 `--platform`,且配方 test 含前綴 / Kotlin 反引號時 method 要用拆殼後的名字(`guard bind` 的 method 維持識別字)。需要:指令形狀由配方的 (平台, 方法) 產生,平台非預設時帶 `--platform`。

## 逐節
- 開頭 frontmatter/summary:已讀,無 finding(`lands_in: Systems/guard-kill` 存在性屬機械前掃範圍)。
- 白話與 PRIOR-ART/RETIRE-IF:見 F1(RETIRE-IF 依賴的帳寫不出)、F2、F3、F6。
- 範圍:見 F1、F3–F6、F8、F9。
- 實務隱患:「多平台 ref」一節列了三種存法但沒列反引號/空白/legacy(F2、F3);「大圖譜」說只讀開頭欄位——已讀,無 finding(`_kill_note_skipped` 先擋掉沒 kill_recipes 的節點;但也沒說明要共用 P2 的 ctx,見 F4)。「已排除」四項:已讀,無 finding;不寫檔、不連網、不改閘判定屬實。
- 驗收條款:S1 缺反引號、單平台、--platform 與前綴不一致、covers-only、設定檔讀不了五格;S2 缺同一合約綁多支、設定檔讀不了、配方欄位壞(非 dict/空 test/空 invariant)格。見 F2–F8。
- 回退:已讀,無 finding。
- 天花板:已讀,無 finding。

實務隱患類別:
- 金流/對外送出/不可逆:無+只多 stderr 與 doctor 一則提醒、不寫檔不連網。
- 守衛面:無+不改任何閘判定;但新增的閘名要登記(F1)。
- 效能:無+只讀已解析的欄位與合約行、不跑 git;唯一規模問題是輸出長度(F9)。
- 資安/注入:無+提醒要印的人寫欄位(test、合約片段)須走 `_kill_show`/`_kill_esc`;spec 沒寫但沿用既有慣例即可,不單列。

總結:最嚴重 severity 為 major,blocking 6 條(F1–F6),非 blocking 4 條(F7–F10)。
