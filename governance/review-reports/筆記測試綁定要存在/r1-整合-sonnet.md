severity: major

# r1 整合-sonnet(整合與接手鏡頭)

我照「要照這份計劃實作的人」讀,逐項對過 `scripts/lumos` 與 `scripts/test_lumos.py`(凍結 repo 的 shared clone 在我的臨時目錄,只讀、做了兩個小實驗)。

## F1 「沒提交的改動就只提醒」照字面做,會讓提交時這組規則在最常見的流程下整個失效
severity: major
blocking: 是
引句:「新寫一支小函式用 `git status --porcelain` 對平台根判」
file: `scripts/lumos:28578`(`cmd_note_shape` 只提交時用 `--staged`,讀的內容是提交索引)
file: `/Users/enzo/harness/lumos-toolchain/.lumos/config.json:2`(本 repo 是 legacy 設定,平台根就是 repo 根)
1. 計劃 S9 與做法 6 寫「落在各平台的測試檔上」,實作那一句卻是「對平台根判」。兩個讀法選錯,結果天差地別。
2. 讀法甲:`git status --porcelain` 在平台根底下有任何一條就降成只提醒。提交時筆記自己就是已暫存的改動,平台根是 repo 根(本 repo、rtb 都是)時,每一次提交都會降成只提醒,規則在提交時永遠擋不下。
3. 讀法乙:只算測試檔、而且只算「暫存」與「工作目錄」不一致的(未暫存的修改與未追蹤)。這才是做法 6 想收斂的情況。
4. 就算選了「只算測試檔」,porcelain 的 `A `/`M `(已暫存、跟工作目錄一致)也會被算進去。本 repo 的家規是「程式、測試、筆記放同一個提交」,測試檔與筆記一起暫存正是主流程,讀法甲的降級會讓它也失效。
5. 計劃沒寫:用哪個 porcelain 欄位判、「測試檔」怎麼從平台根認出來(profile 的檔名樣式?)、推送時要不要也判。S9 的測試夾具因此無從決定:夾具只放一個未暫存的測試檔,兩種讀法都綠;夾具放已暫存的測試檔,兩種讀法才分岔。
6. 修補方向:計劃要明寫「只比暫存區與工作目錄不一致的測試檔」,並加一條「已暫存且一致的測試檔不降級」的條款。未實測,依據是讀碼。

## F2 整行丟給 `_classify_test_refs` 再扣「新加的名字」,壞前綴會讓同行其他名字(含舊名字)一起被吞成一筆,S2 在這種輸入下不成立
severity: major
blocking: 是
引句:「平台前綴沒定義時它整段只回一筆,訊息照印它的錯誤字串。」
file: `scripts/lumos:40248`(`_classify_test_refs`:`resolve_test_refs` 丟 `ValueError` 就整段回一筆 `("?", 訊息, "bad-name")`)
file: `scripts/lumos:5169`(`resolve_test_refs`:逗號切完逐段檢查前綴)
實驗(設定檔有 `platforms` 且有 `py`,測試檔有 `test_real_one`):
```
WHY:x [test:test_real_one, 古怪:abc] -> [('n','?',"[test:古怪:abc] 的平台前綴 '古怪' 未定義於 platforms(py)…",'bad-name')]
WHY:x [test:test_real_one, nope_name] -> [real, dangling]   (正常:每個名字各一筆)
```
1. 做法 3 寫「每一行(去反引號後的整段)交給 `_classify_test_refs`」,做法 2 寫「新寫行裡的名稱扣掉起點版本的多重集合,剩下的才查」。兩句接不起來:丟整行進去,回傳要拿來「扣舊名字」,可是壞前綴那一筆的方法欄是錯誤字串、不是名字,對不回任何一個原名字。
2. 場景:舊行 `[test:舊名, 古怪:abc]` 本來就有,只改了行上別的字。整行進 `_classify_test_refs` → 一筆 `bad-name` → 對不上多重集合 → 被當成新違規擋下。這正好違反 S2「舊行原本就有、只改了其他字時應不擋」。
3. 反過來,新加名字旁邊有一個壞前綴名字時,好名字完全沒被判到(只出一筆),要等使用者改完再炸第二次。
4. 能讓 S2 在所有輸入下成立的做法是:只把「扣完剩下的新名字」重組成一段合成文字(例如 `[test:新1,新2]`)再交給分類。計劃要把這步寫出來,否則實作者各自選,選整行的那種實作會讓 S2 只在沒有壞前綴時成立。
5. 另外 legacy(沒設 `platforms`)時整串含冒號的名字不切分,走 `dangling` 而不是 `bad-name`,計劃的「判定」欄位措辭(只講 bad-name)與此不符,訊息改法要兩種都給。

## F3 「一行」在摘要裡不是實體行:作廢標記、`[test:]` 與合約行跨續行時,1c、合約行略過、S8 都會判錯
severity: major
blocking: 是
引句:「(1c)新寫的作廢行掛著活測試 → 違規:改成 `[test-gone:]`,或把綁定移到接手的那一行」
file: `scripts/lumos:27344`(`_notelines_new` / `_notelines_rows` 回的是實體行 `(行號, 行文字, 區塊)`)
file: `scripts/lumos:28189`(`_ns_superseded` 吃單一字串;格子規則為了續行另寫了 `_ns_summary_logical`,`scripts/lumos:28000` 以下)
1. 摘要常把一條長 RULE/WHY 用縮排折成多個實體行(格子那邊已經為此有 `_ns_summary_logical` 接回續行)。`[status:superseded]` 在首行、`[test:x]` 在續行,逐實體行判 `_ns_superseded` 與 `[test:]` 就湊不到同一行:S8 判不出。
2. 只改了續行(例如新加 `[test:x]` 在續行)時,新行集合裡只有續行,首行的作廢標記不在 rows 裡,1c 同樣漏判。
3. 同一個問題在合約行略過:做法 1 用 `INVARIANT_RE` 判行首,續行上的 `[test:合約測試]` 不是以 `KEY:★INVARIANT★` 開頭,會被當成一般行重判一次,與 Check T 重複報告(又因為是新加的、而擋下)。
4. 計劃沒說「行」指實體行還是接回續行的整條;`[test:a,` 換行 `b]` 這種跨行方括號 `TEST_REF_RE`(`scripts/lumos:4736`)本來就抓不到,也沒說明。
5. 選錯的後果:選實體行,S8/合約行略過在折行輸入下失效;選整條,計劃要明寫要重用 `_ns_summary_logical` 並解決「行號報哪一行」。判不準屬於 ⚠ 交編排者決定,但必須在計劃裡定下來。
6. 1c 另有一個沒寫明的問題:它是不是也套「新加的名字」多重集合?S8 的字面是「新寫的行 … 又掛著指得到的 `[test:]`」(不套),而名詞段「活測試」只定義了名字層。實作者如果順手沿用規則 1 的扣除,在舊行上加 `[status:superseded]` 收回舊限制(最典型的 1c 場景,名字是舊的)就會被放過。這句要明寫「1c 不扣舊名字」。
未實測,依據是讀碼。

## F4 測試索引「建得起來但是空的」不在 fail-open 範圍,缺平台根或沒設平台的專案會被每個新名字擋下
severity: major
blocking: 是
引句:「索引建不起來(設定壞丟例外)→ 這組規則這次跳過、印一行原因(note-shape 本來就 fail-open)」
file: `scripts/lumos:5084`(`load_platforms`:根目錄不存在只印警告不丟例外;沒設 `platforms` 時 legacy 預設 profile 是 `csharp-xunit`)
file: `scripts/lumos:12856`(`_platform_test_index`)
實驗(兩個空專案,測試方法集合與 haystack 都是空):
```
proj2  platforms.be.root = ../no-such-sibling  -> ⚠ 平台 'be' 的 root 不存在… ; [('n','be','test_real_one','dangling')]
proj3  沒有 .lumos/config.json                  -> default=csharp-xunit ; [('n','csharp-xunit','test_real_one','dangling')]
```
1. 計劃的 fail-open 只接「設定壞丟例外」。上面兩種都不丟例外,索引成功建起來、只是空的,所有名字判成 `dangling`,全部擋下。
2. 現實場景:平台根指到 sibling repo(後端、前端分兩個 repo 的消費專案)。本機有 sibling 時一切正常,CI 或別台機器沒 checkout sibling,提交與推送時「每個新加的 `[test:]` 都指不到」,而且 CI 擋下沒有出口(單次跳過只在本機)。
3. 沒設測試設定的專案(docs 專案、還沒配好 `platforms`)寫 `[test:…]`,也全部擋下,而訊息講的是「改成真的測試名」,誤導。
4. 計劃的 RETIRE-IF 靠「索引沒認出」的名字比例,但索引整個空的情況不會被歸成「索引沒認出」,而是正常的 dangling,抽查時算進擋對的一邊,低估誤擋。
5. 修補方向:計劃要定一個「索引是否可用」的判準(平台根不存在、方法集合與 haystack 都空、legacy 且沒有設定),不可用就整組跳過並印原因;S10 的夾具要涵蓋這兩種,不只設定壞。

## F5 「三選一寫死的字三處」數少了:實際要動的位置與會紅的既有測試更多,而且動紀律範本要連動升版
severity: minor
blocking: 否
引句:「三處一起改成照組員數寫:程式組必有鍵說明那行、測試裡解析範本表的 helper」
file: `scripts/lumos:3898`(`_slot_check_required` 組訊息的 `" 三選一"`)
file: `scripts/lumos:27999`(`_NS_SLOT_TEMPLATE["PITFALL"]` 的提示寫法,只列 test、repro、防回歸)
file: `scripts/test_lumos.py:30420`(`"三選一" in x`)、`scripts/test_lumos.py:30641`(`"三選一" in out`)、`scripts/test_lumos.py:31505`(治理帳 key `"test/repro/防回歸"`)
file: `CLAUDE.md:45`、`AGENTS.md:46`(紀律區塊的拷貝,跟 `scripts/templates/graph-discipline.md:43` 同一列)
file: `scripts/lumos:338`(`_START_TEMPLATE` 版本由 `LUMOS_VERSION` 插值)、`CHANGELOG.md:10`(v1.1 先例:範本改一條就升版、寫對外說明)
file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:37`(「`PITFALL:` 沒有測試就寫 `[repro:指令]`…」)
1. 訊息文字:組員變四個後訊息若改成「四選一」,`t_slots_*` 兩處 `"三選一"` 子字串斷言與 `slots_missing` 的 key(由組員 `"/".join(grp)` 組出,會變成 `test/test-gone/repro/防回歸`)會紅;計劃沒列這些測試要跟著改,也沒說訊息是否保持「三選一」字樣。
2. 紀律範本改一列,這個 repo 自己的 `CLAUDE.md`、`AGENTS.md` 的紀律區塊要重新注入(Check D 比對),消費專案要 `lumos update`;依 v1.1 先例要升版並寫 `CHANGELOG.md`。計劃的「同步哪些文件」沒有這一串。
3. 新增的 `_NS_SLOT_TEMPLATE["PITFALL"]` 提示與 skill 指令速查(commands/03)也提到防回歸三種寫法,計劃沒列。
4. 這些都是會被推送前閘或全套測試抓到的,屬於漏列、不是邏輯洞,所以標 minor。

## F6 單次跳過時「也記 `test_refs`」的接法限制很多,照抄 `_ns_skip_slot_extra` 會在多數跳過情境下不帶欄位,S14 不成立
severity: major
blocking: 是
引句:「單次跳過時也先算一次記進去(照格子的 `_ns_skip_slot_extra`)」
file: `scripts/lumos:28089`(`_ns_skip_slot_extra`:合併中、無圖譜、格子子開關 off 時回 None)
file: `scripts/lumos:28573`(只有 `staged and slots_flag` 才呼叫它,推送時的跳過不算)
1. `_ns_skip_slot_extra` 一上來就以「格子開關是 off 就 return None」、呼叫端又只在 `--staged --slots` 才叫它。`test_refs` 規則的開關與 `--slots` 無關(提交時不需要掛鉤改動就會跑),所以:格子關著、或掛鉤沒帶 `--slots`、或推送/CI 時跳過,都記不到 `test_refs`。S14 寫的是「這組規則…被單次跳過時」,沒限定情境。
2. 它回傳的是單一 `extra` 字典,里面已經有 `check`("slots" 或 "shape+slots",`scripts/lumos:28375`,既有測試 `30960`、`31500` 釘這兩個值)。計劃沒定義 `test_refs` 存在時 `check` 怎麼寫,混合三種時尤其無解。
3. 「條數與前 20 個名稱、各自判定」是單一欄位還是 `test_refs_count` 與清單兩個欄位也沒寫;REVISIT 要「數擋下次數與名稱」,S14 的測試要把形狀釘死。
4. 跳過前算一次,表示逃生口自己要先建索引(F4、時間隱患);計劃沒說跳過時索引建不起來的行為,雖然 `_ns_skip_slot_extra` 的慣例是整段包例外、回 None。
5. 修補方向:計劃要明定:`test_refs` 欄位形狀、`check` 組合規則、跳過在提交與推送兩路都算(或明說推送不記)、不依賴格子開關。

## F7 `_note_shape_report` 與 `cmd_note_shape` 的接線點沒寫,字面實作會漏掉「只有這組違規」的情況並印錯誤的標題與收尾句
severity: minor
blocking: 否
引句:「(提交與推送都跑);認得 `[test-gone:]` 並登記成格子鍵」
file: `scripts/lumos:28635`(`rc = _note_shape_report(...) if (viol or errs or sviol) else 0`)
file: `scripts/lumos:28685`(`_note_shape_report`:標題固定「有新寫的、程式碼推得出來的形狀」,收尾句固定「為什麼擋:筆記只留程式碼推不出來的東西」)
1. 呼叫條件只認 `viol or errs or sviol`;實作者若只新增違規清單卻忘了加進這個條件,只有 `test_refs` 違規時 rc 會是 0、什麼都不印。
2. 報告函式的標題與收尾句講的是「程式碼推得出來」,跟「測試名指不到」是兩回事,套同一個標題會誤導;格子那組已經示範過「只因格子擋時不印筆記形狀擋的收尾句」(`scripts/lumos:28701`)。計劃要說這組自己印一段、自己的收尾句。
3. `warn` 時 `blocked` 的判定與記帳的 `warned` 分支要加進 test_refs 的 mode,計劃只寫「照 `note_shape.slots` 的形狀」,沒寫三組(違規、格子、test_refs)的混合規則。

## F8 「起點版本那篇筆記」遇到改名會當成新檔,同篇舊名字被誤判新加
severity: minor
blocking: 否
引句:「起點版本那篇筆記(提交時是 HEAD、推送時是範圍起點;新檔就是空)」
file: `scripts/lumos:27250`(`_notelines_range_added` 的 `_carry` 已經照提交逐個把改名帶到終點路徑)
1. 做法 2 用「同一路徑」讀起點版本。範圍內改名過的筆記,起點路徑讀不到內容,被當成「新檔就是空」,於是同篇所有被編輯到的行上的舊名字都算新加。
2. 場景:一個推送裡有 `git mv A.md B.md` 並改了裡面一行 `[test:舊懸空名]` 以外的字;該行進 rows,舊名字不在空集合裡 → 被擋,違反 S2 精神。
3. 修補:起點版本的讀取要沿用 `_carry` 的改名映射(新路徑 → 舊路徑)。計劃要寫。

## F9 doctor 新段:段 id、位置、「下一層子項」沒有可實作的定義
severity: minor
blocking: 否
引句:「另列散文撤除的候選:計劃裡條款定義行仍有 `[test:]`,而它下一層子項含」
file: `scripts/lumos:2513`(S17 到 S19 的寫法與位置)
file: `scripts/test_lumos.py:7545`(`t_doctor_soft_sections_truncate_by_default` 切 `[S]` 到 `[E1]` 窗口)
file: `scripts/test_lumos.py:40578`(`t_doctor_advisory_sections_do_not_block`:標題含「不擋」的段不得用 `warn(`)
1. 沒給段 id 與擺放位置。S16 到 S19 的註解特別說明要避開 `[S]`~`[E1]` 軟段截斷測試的窗口;新段放進去會被那支測試數到。計劃只說「照 S17–S19」,沒寫位置紀律。
2. 標題一定要含「不擋」並只用 `warn_soft`/`_soft_list`,否則上面第二支測試會紅;計劃沒提。
3. 「下一層子項」在資料模型裡沒有:筆記是行,沒有子項樹。實作者只能自己用縮排猜;rtb 那 12 條的樣子計劃也沒給範例。S11 的夾具因此各人造各人的,條款綠不代表抓得到 rtb 的真實寫法。
4. 全庫掃描要不要略過 `status: superseded|stale` 的計劃(S5 有這樣的略過,`scripts/lumos:2380`)也沒寫。

## F10 要掃哪些區塊、條款定義行怎麼認,計劃只給字面
severity: minor
blocking: 否
引句:「合約行(摘要裡、`INVARIANT_RE`)與計劃裡的條款定義行(行首 `[SN]`)略過」
file: `scripts/lumos:6161`(`_CLAUSE_LEAD_RE`:去掉列表符號、勾選框、粗體後才是 `[SN]`)
file: `scripts/lumos:27152`(`_notelines_regions`:body/summary/decisions/other)
1. 條款行實際長 `- [S1] …`,字面「行首」不會命中;要重用 `_CLAUSE_LEAD_RE`(S5 與 spec-trace 同一支),計劃沒點名。
2. 區塊:名詞段寫「筆記任一行」,但 `_note_shape_eval` 現有迴圈對 `other`(開頭欄位其他欄)是特別處理的(`keep_other=True` 才收)。這組規則要不要查開頭欄位其他欄、decisions 的 `content/context` 文字,沒定。
3. 合約行在摘要裡是縮排兩格(YAML 區塊純量),`INVARIANT_RE` 要先 `strip`,舊代碼已這樣,但計劃不提。

## F11 `[test-gone:]` 形狀檢查在兩處各做一次,同一個寫壞會雙報
severity: minor
blocking: 否
引句:「新寫行裡的 `[test-gone:]` 寫法不對(沒有 `@`、提交不到 12 碼、不在任何分支歷史上)→ 違規。」
file: `scripts/lumos:3855`(`slot_check`,已作廢的行跳過;提交時 `--slots` 與 lint 都用)
file: `scripts/lumos:27114`(`_pin_commit`:至少 12 碼、不超過 40 碼 `_NS_PIN_HEX_RE`)
1. 做法 4 的「沒有 `@`、不到 12 碼」與做法 8 的 `slot_check` 形狀檢查(名稱非空、`@` 後至少 12 碼十六進位)是同一件事,同一個壞寫法在提交時會同時出現一筆格子缺漏與一筆 `test_refs` 違規,兩筆帳、兩個訊息。
2. 兩邊對作廢行的處理不同(`slot_check` 跳過、本案不跳過),同一行 `[status:superseded] [test-gone:壞]` 只有一邊報。
3. 上限也不一致:`_pin_commit` 擋超過 40 碼,計劃寫「至少 12 碼十六進位」。
4. 修補:形狀只放 `slot_check` 或只放本案,另一邊只做「在歷史上」的 git 判斷。

## 其他節核對
- 〈回退〉:已讀,無 finding。格子規則回退後不認 `test-gone` 鍵的描述,跟 `_SLOT_CANON` 只收白名單鍵(`scripts/lumos:3746`)一致。
- 〈範圍〉〈名詞〉:使用者已裁的範圍(擋新加的、全庫只提醒、佔位字不准)不重報。`[test-gone:` 不被 `TEST_REF_RE`(`\[test:\s*…`,`scripts/lumos:4736`)誤抓,已核對,沒有問題。
- `_KNOWN_GATES` 與文件列舉守衛:本案沿用 `note-shape` 閘名、沒新增閘,所以 `_KNOWN_GATES`(`scripts/lumos:7537`)不受影響,無 finding。

## 施工對照(接手者視角,供編排者核對計劃缺哪些)
- 新函式放 `_note_shape_eval` 旁(`scripts/lumos:28378` 一帶):`_note_test_refs`、`_note_shape_test_refs_parse`(照 `_note_shape_slots_parse`,`scripts/lumos:28113`)、`_ns_test_refs_mode`(照 `_ns_slots_mode`)、違規收集函式(拿 `notes` 與起點版本)。資料流要新增一個容器(像 `slots`),因為 `_note_shape_eval` 回的是 `(viol, errs)` 兩個值、有多個以兩值解包的呼叫端(doctor `scripts/lumos:2058` 一帶、`_ns_skip_slot_extra`)。
- `cmd_note_shape` 在 `_ns_slots_collected` 之後接;`_note_shape_report` 要多一個參數(F7);單次跳過在 `scripts/lumos:28569` 之後接(F6)。
- 會紅的既有測試:`t_slots_single_table`(`scripts/test_lumos.py:30332`,範本與程式兩邊一致,動範本與 `_SLOT_ONE_OF` 要同步)、`t_slots_*` 兩處 `"三選一"` 斷言與 `test/repro/防回歸` key(F5)、`t_command_index_complete`(沒新指令,不受影響)、`t_doctor_soft_sections_truncate_by_default` 與 `t_doctor_advisory_sections_do_not_block`(F9)。note-shape 現有 `_ns_repo`(`scripts/test_lumos.py:50110`)沒有平台設定與測試檔,S1 到 S10、S12 到 S14 的夾具要自己加:`.lumos/config.json` 的 `platforms`(python profile)、一個含 `def test_x` 的測試檔、已提交的起點(S2)、真實 commit 與 `git commit-tree` 捏造的孤兒提交(S5、S6)、一個未暫存的測試檔(S9,依 F1 的定義)、一個缺 `default_platform` 的雙平台設定(S10)、`_ns_gov` 讀帳(S14,已有)、doctor 用 `mkvault`(S11)。S15 是純函式,`slot_check("PITFALL", …)` 一行就能測。
- 消費專案升級後 CI 才會碰到的行為(F4)在 repo 內的夾具造不出來,要用不存在的平台根目錄模擬。

最高等級:major,blocking 共 5 條
