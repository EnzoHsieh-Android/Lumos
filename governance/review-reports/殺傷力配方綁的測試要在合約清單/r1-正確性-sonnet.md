severity: major

審查鏡頭:正確性/邏輯。對照 /Users/enzo/harness/lumos-d3 的 scripts/lumos。圖譜鏡頭:派工沒有附上牽連的合約/事故節點,無節點可逐條判。

## F1 「沒帶 --test 一定不會觸發」不成立:清單寫非預設平台前綴時 kill-add 自己寫的配方會被自己提醒
severity: major
blocking: 是(S1 條款與實際行為對不上,實作照 spec 會對剛寫入的配方誤報,且提醒的修法指示是錯的)
spec 段落:範圍第一條。
引句:「沒帶 `--test` 時配方的測試一定取自清單,不會觸發。」
問題:沒帶 --test 時,`_guard_kill_add_locked` 取 `refs[0]` 的原始字串(含平台前綴)當配方的 test,而且只在使用者傳 --platform 時才寫 platform 欄;前綴不會被轉成 platform 欄(`scripts/lumos:15289-15303` 一帶的 recipe 組裝)。實際跑法是 `scripts/lumos:15877` 分組用 `r.get("platform") or platform_override or default_plat`,方法名用 `_kill_method_name`(`scripts/lumos:14650`)去掉前綴。
具體例:多平台設定,default_platform=csharp;合約行 `[test:kotlin:FooTest]`;跑 `guard kill-add 節點 片段 --file … --old … --new …`(不帶 --test、不帶 --platform)。配方 test 為 "kotlin:FooTest"、無 platform 欄。spec 的比對把配方側算成 (csharp, FooTest),清單側算成 (kotlin, FooTest) → 不相等 → 印「這條合約還沒綁…/要 lumos guard bind」類提醒。預期:不提醒(測試明明取自清單);實際:誤報,而且建議的修法(guard bind)是錯的,真正的問題是配方沒帶 platform=kotlin、kill 會在 csharp 平台跑 FooTest。doctor 同理會把這條逐條列出,每次 doctor 都唸。
S1 的測試條款沒有涵蓋「清單寫非預設平台前綴 + 不帶 --test」這個組合,守不到。要嘛 spec 承認這是另一個真問題(配方平台沒跟前綴)並寫專用訊息,要嘛 kill-add 在取自清單時順手補 platform 欄,spec 現在兩者都沒說。

## F2 清單解析沒寫「單平台(legacy)要傳空平台表」,照 PRIOR-ART 字面實作會在單平台專案吞掉提醒或誤判
severity: major
blocking: 是
spec 段落:PRIOR-ART。
引句:「用既有 `resolve_test_refs(合約行, 平台表, 預設平台)` 解析成 (平台, 方法) 對」
問題:`load_platforms` 在單平台時回的 platforms 是非空的單一條目(`scripts/lumos:5551-5560`),multiplatform=False;`resolve_test_refs` 的 docstring(`scripts/lumos:5619-5626`)明寫 legacy 要由呼叫端傳 {} 才不切冒號。既有呼叫點都這樣閘(如 `scripts/lumos:36056` 的 `pd["platforms"] if pd["multiplatform"] else {}`)。spec 對配方側寫了「`_kill_method_name(test, 多平台)`」帶 multiplatform,清單側卻寫「平台表」沒閘,兩邊不對稱。
具體例:單平台專案、清單 `[test:tests/test_a.py::test_x]` 或任何含冒號的方法名。若傳 `pdata["platforms"]`(非空)→ 切出前綴 "tests/test_a.py" 不在平台表 → 丟 ValueError → 依 spec「不比、不提醒」靜默略過,該提醒在 legacy 專案對含冒號的測試名永遠不會出。配方側(multiplatform False 不去前綴)是整串,與清單側若兩邊閘法不一致就比不起來。
修:spec 要寫死「清單側 platforms=pdata['platforms'] if multiplatform else {};配方側 mp=pdata['multiplatform']」,S1/S2 加單平台含冒號案例。

## F3 doctor 側沒定義「清單解析丟 ValueError」與「單一配方格式壞」怎麼處理,一支壞配方可能吞掉整則提醒
severity: major
blocking: 是
spec 段落:範圍第二條、第三條。
引句:「自己一個例外保護;不跑 git。」
問題:只有 kill-add 側寫了「未定義平台前綴時不比、不提醒、不讓 kill-add 失敗」。doctor 側沒寫:(a) 某合約行有未定義平台前綴 → 丟 ValueError:該行的配方要計入「另有 N 條對不回」、還是略過、還是整則提醒死掉?(b) 配方欄位型別壞(`platform` 是 list、`test` 是數字、元素不是 dict):配方側 (平台, 方法) 若放進 set 比對會 TypeError(list 不可雜湊)。既有 `_kill_p2_scan` 是逐篇、逐條各包例外(`scripts/lumos:15033-15056`),spec 只要求「各提醒自己一個例外保護」(整則一個 try)。
具體例:rtb 這類 73 條配方的庫,其中一篇有一條 `"platform": ["a"]`。照 spec 整則一個 try → 整則提醒只剩一行「判不了」,其餘 72 條真失配全被吞;預期:壞的那條單獨處理,其他照列。
修:spec 要寫成逐篇逐條保護,並規定 ValueError 的歸屬(建議算進 N 並在 N 行註明原因)。

## F4 「另有 N 條」那行的出現條件與 S2「都在清單上時不列」互相矛盾
severity: minor
blocking: 否(實作者要猜,但猜哪邊都不致誤報提醒本身)
spec 段落:範圍第三條與驗收條款 S2。
引句:「在同一則提醒的開頭另印一行筆數(「另有 N 條配方對不回合約行,沒比對」),不逐條列」
問題:提醒是「有失配才列」的一則。全部配方都在清單上、但有 3 條對不回合約行時:S2 說「都在清單上時 應 不列」,範圍卻說 N 行印在「同一則提醒的開頭」。沒有失配就沒有這則提醒、N 就不會印,與「目前沒有任何檢查管這種情況,至少讓人看得到」的目的相反;有失配才附帶 N 則只在最糟的組合下才看得到。S2 的測試只說「對不回合約行的配方 應 只算進另有 N 條那一行」沒有寫單獨出現的情形。
具體例:圖譜只有一條配方、其片段在合約行被改字後對不到 → 期望(依目的)印 N=1;實際(依 S2 前半)什麼都不印。

## F5 kill-add 的提醒要拿合約行,但 warn_box 只裝配方,傳遞方式沒寫(可執行性缺口,附帶 race)
severity: minor
blocking: 否
spec 段落:範圍第一條與 PRIOR-ART「接在既有的鎖外提醒旁」。
問題:`_kill_add_after_lock` 迴圈 `for rec in warn_box` 把元素當配方傳給 `_kill_add_warn`,又用 `warn_box[0]` 算 `_kill_recipe_id`(`scripts/lumos:15217-15230`);合約行(`line`)只存在於 `_guard_kill_add_locked` 內部。spec 沒說行文字怎麼帶出鎖外:改 warn_box 形狀會牽動這兩處與既有測試;鎖外重讀筆記則會在放鎖後被別的會談改過清單(kill-add 本來就把 git 判斷放鎖外的理由),比到的可能不是「這次寫入時」的清單。
具體例:放鎖後另一個會談 `guard bind` 把該測試綁上、或把清單改掉 → 鎖外重讀比出與寫入時相反的結論。

## F6 去標記後「含片段」與 kill-add 的定位不是同一把尺,doctor 會與 kill-add 對到不同行
severity: minor
blocking: 否
spec 段落:PRIOR-ART 末句與範圍第二條。
引句:「對回合約行用 `extract_contracts` 加去標記後「含片段」。」
問題:kill-add 的定位是對整條 KEY 行(含 `KEY: ★INVARIANT★` 前綴與括號日期)去標記後比片段(`scripts/lumos:15276-15281`);`extract_contracts` 回的是 `INVARIANT_RE` 的 group(1),已去掉前綴。片段若含前綴或日期括號(例:`INVARIANT`、或日期字樣),kill-add 當時對得上、doctor 對不上(進 N)。另 kill-add 掃的是 frontmatter 全部行,`extract_contracts` 只掃 summary 欄位。實務上片段多為宣稱正文,這個差異罕見,故 minor。
具體例:片段寫 `2026-09-01` 這種只出現在 `KEY: (2026-09-01) ★INVARIANT★ …` 括號裡的字 → kill-add 命中、doctor 判對不回。

## 逐節
- 檔頭 frontmatter / summary:已讀,無 finding。`_kill_note_skipped` 等引用的函式都存在(`scripts/lumos:15020`、`14619`、`14650`、`5169`、`5619`)。
- 範圍 第一條:F1、F5。「只更新 covers」路徑:`recipe = r` 取既有配方,先前用它自己的 platform 驗原文(`scripts/lumos:15316` 一帶),提醒比的是既有配方(沿用 spec 的做法正確),但每次補 covers 都會重唸同一條既有失配,屬 spec 明示的取捨,不報。
- 範圍 第二條、第三條:F3、F4、F6。
- 範圍 不做:已讀,無 finding。
- 實務隱患(多平台 ref):三種存法已查——(1) 方法名+platform 欄:正確。(2) 帶前綴沒有 platform 欄:spec 的規則(前綴被 `_kill_method_name` 去掉、平台取預設)忠於 kill 實際跑法,但「前綴被忽略」本身 spec 沒講,是 F1 的根因。(3) 只有方法名:正確。清單側有前綴/沒前綴:預設平台兩種寫法互相等價,正確。Kotlin 反引號:配方側 `_kill_method_name` 去掉、清單側探測時也去掉(`scripts/lumos:5889`),合約寫的是裸名,無問題。
- 實務隱患(大圖譜):已讀,無 finding。只讀 frontmatter,不跑 git;但 `_kill_cfg_load` 讀設定失敗(cfg_err)時這則提醒怎麼辦 spec 沒寫(併入 F3 修法一起規定)。
- 其他風險類:金流/對外送出/不可逆/守衛面——只多 stderr 與 doctor 行,不改判定,無 finding。
- 驗收條款 S1/S2:已讀;S1 缺「非預設平台前綴+不帶 --test」(F1)、「單平台含冒號」(F2);S2 缺「ValueError 合約」與「壞配方不拖累其他條」(F3)、「只有對不回、無失配」(F4)。
- 回退、天花板:已讀,無 finding。

最高 severity:major,blocking 共 3 條(F1、F2、F3)。
