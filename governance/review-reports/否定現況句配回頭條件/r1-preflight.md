# 否定現況句配回頭條件_計劃 前掃報告

被審:`negguard/docs/lumos-toolchain-knowledge/Projects/否定現況句配回頭條件_計劃.md`
讀過的程式:`negguard/scripts/lumos`、`scripts/hooks/pre-commit`、`governance/eval/negation-revisit/neg_revisit_measure.py` 與 `report-2026-09-30.md`。
只讀;S1 例句用參考實作 `classify_text` 在暫存目錄外跑過(沒寫任何 repo 檔)。

## ① 未定義的詞(4)

**①-1**
- 計劃原句:「只看這次新寫的行、截到上線點」(〈與參考實作的刻意差異〉6);「上線 8 週後…用量測程式把上線後的提交重跑一次」(〈做法〉7);「實作上線了:記下上線提交」(REVISIT)
- 問題:「上線點」在現有程式是 `_NOTE_SHAPE_GOLIVE_MARK = "note-shape --staged"`(用 `_nodehome_golive` 對 `scripts/hooks/pre-commit` 做 `git log -S`),那是 2026-09-27 筆記形狀擋自己的上線點。這個提醒沒有自己的標記字串,計劃也沒說要不要加。「截到上線點」與「上線後的提交」到底指哪個沒定義。
- 建議:寫明「沿用筆記形狀擋的上線點,不另設」或「另設標記字串 X」;〈做法〉7 的「上線後」改成一個可機械取得的日期或提交(REVISIT 那行記下的那個提交)。

**①-2**
- 計劃原句:「同一區塊(正文、摘要、決策)裡、這一行前後 3 行內」
- 問題:「行」有沒有算空行沒說。參考實作 `_revisit_near` 是原始行號 ±3(空行照算),計劃的例子「隔 4 行 → 提醒」沒講空行。「區塊」對到程式的 body/summary/decisions(`_notelines_regions`),但條款與做法混用「區塊」「區」,而且不含 other。
- 建議:寫「原始行號 ±3,空行算一行」;區塊名照 `_notelines_regions` 的英文名寫。

**①-3**
- 計劃原句:「寬表(沒、沒有、未、缺、無、不會、不存在…)」;「A3」「A7」「考卷 B4」
- 問題:寬表清單以「…」收尾,實際是 `BROAD_ZH` 7 詞加 `BROAD_EN` 7 詞(missing、no、lack…)。A3、A7、B4 是舊計劃的考卷編號,這篇沒有定義。
- 建議:寬表寫「見量測程式 `BROAD_ZH/BROAD_EN`」;A3/A7/B4 第一次出現時附一句是哪句。

**①-4**
- 計劃原句:「英文整字 `not yet`、`yet to`(不分大小寫)、`TODO`、`TBD`(分大小寫…)」
- 問題:「整字」的邊界沒定義。參考實作 `_rx` 用 `(?<![A-Za-z0-9_-])…(?![A-Za-z0-9_-])`,連字號與底線算字內,所以 `TODO-list`、`TODO_x` 不中。做正式工具的人只看計劃會用 `\b`,結果會跟參考實作不同(`\b` 把 `-` `_` 之外當邊界,且 `_` 算字元但 `-` 不算)。
- 建議:寫明邊界規則等於量測程式 `_rx` 的那條。

## ② 壞引用(2)

**②-1**
- 計劃原句:「rtb 2026-09-30 把 33 條散文回頭條件改寫成條件式,掃描全部點名、其中 11 條待辦真的漏了([[Issues/存量筆記漂移三種機制_rtb根因回饋]]〈工具覆蓋率比對〉)」
- 問題:grep 驗過。〈工具覆蓋率比對〉那段講的是 20 處真漂移(存量抓到 7/20、抓不到 6.5/20,其中「回頭條件是散文」3 處),沒有 33、沒有 11、也沒有「全部點名」。「33 條改寫」只出現在 `Issues/rtb接上漂移檢查後回報的四個小改進` 第 6 條,而且那裡只講「至少 2 條條件綁錯事件」。「11 條漏」在本 repo 的兩篇 Issue 都找不到,原始出處大概在 rtb repo。
- 建議:「11 條」改成指到 rtb 的實際筆記(節點或提交),或刪掉;33 的出處改指四個小改進第 6 條。這句是本計劃的動機依據之一。

**②-2**
- 計劃原句:「字眼表誤觸:只中寬表、沒中窄表的 3398 行抽 30 行 1 行真」
- 問題:報告表 2 的母體是「只中寬表、沒中窄表、**沒配的**」3398;若照計劃表的數字算,寬或窄命中 2900+1353=4253,窄 274+179=453,只中寬表是 3800,不是 3398(差的約 400 行是旁邊已有 REVISIT 的)。計劃漏了「沒配的」。
- 建議:補上「且旁邊沒配回頭條件的」。

## ③ 範圍自相矛盾(7)

**③-1(掛點)**
- 計劃原句:〈範圍〉不做②「推送前與 CI(`--diff`)印提醒」;〈與參考實作的刻意差異〉6「範圍照 note-shape:只看提交前這一次、截到上線點(參考實作逐提交看、不截)」;S8「逐提交呼叫 `_ns_negation_hints` 跟 hits 檔逐行比」
- 問題:讀 `_notelines_new`:`staged=True` 走 `git diff --cached -U0`,完全不做上線點截斷;截斷只發生在 `staged=False` 的範圍模式(`_notelines_range_cand` → `_notelines_range_added(mark=live_mark)`)。提醒只在 `--staged` 印,所以「截到上線點」對這個功能是空話。S8 若用範圍模式逐提交重放,工具鏈 300 個提交多半早於 2026-09-27 的上線點,會被截成空,S8 就比不出 100 行。
- 建議:刻意差異 6 刪「截到上線點」,只留「只看提交前這一次的新行」;S8 明寫重放怎麼取 rows(傳一個永遠找不到的 `mark` 讓 `_nodehome_golive` 回 None,或自己餵 rows)。

**③-2(否定字眼表與過濾規則)**
- 計劃原句:〈做法〉1 第 3 點「一行裡每一處都不算才整行不算」、第 4 點「用句號…切出窄表那一處所在的句子,裡面沒有歷史字眼…也沒有規則字眼」;「字眼表與過濾一字不差照量測程式的常數」
- 問題:計劃的語意是「每一處各自判,有一處留下整行算」。參考實作 `classify_text` 是 `hist = any(...)`、`rule = any(...)`,對所有 live 命中的子句取 any,任何一句有歷史或規則字眼整行就丟。我實跑:`設計還沒做。當時還沒有模型段` → 參考實作不算;`不准還沒審;設計還沒做` → 不算;照計劃的每處各判會算。S1 的例句「還沒提交的檔;設計還沒做」兩種語意都算,測不出差別。刻意差異 1–6 沒列這條,S8 要求「差的每一筆都要落在刻意差異裡」會撞到未宣告的差異。
- 建議:二選一寫死。(a) 照參考實作 any 語意,第 3、4 點改寫;(b) 保留每處各判,列進刻意差異第 7 條並用同一份 hits 重估差幾行,S1 補一條「歷史句與現況句同行」的例子。

**③-3(哪些句子算已配)**
- 計劃原句:〈做法〉2「而且它的條件標記解析得過、帶 `[by:]`(`_probe_parse` 沒有錯)——就不提醒」;刻意差異 4 只列「只有日期式」與「行內夾 REVISIT」
- 問題:參考實作 `_revisit_near` 只要 `_revisit_split` 判 cond 就算配,不管 parse 與 `[by:]`。計劃多加了「parse 過、有 by」這個條件,但刻意差異沒列。資料上 cond 命中 0 行所以數字不動,不過規則在實作與重放間分歧。另 `_probe_parse` 回的是 `errs` 清單與 `by` 欄,「沒有錯」要看 `errs==[]` 且 `by is not None`,「沒帶 by」本身不在 errs 裡(`_ns_revisit_violations` 另外補)。
- 建議:刻意差異補第 7/8 條;〈做法〉2 明寫判法是 `not pr["errs"] and pr["by"]`。

**③-4(哪些句子算已配、提醒會不會變成擋)**
- 計劃原句:〈做法〉2「同一區塊(正文、摘要、決策)裡…有一行條件式回頭條件…就不提醒」;S2「摘要與決策裡的新行照算」
- 問題:條件式回頭條件只在 body/summary 生效。`_probe_lines` 只收 `regs in ("body","summary")` 且非表格;`_ns_revisit_violations` 對其他區塊(含 decisions)裡的 `[when-…]` 直接回「條件寫在不評估的地方」——那是**擋**(note-shape 第一層,存量漂移防線 [S10])。所以決策區塊裡的否定現況句永遠配不成;照提醒字樣在決策區塊旁邊加 REVISIT,反而被擋下。〈做法〉2「決策」列為可配的區塊是錯的。
- 建議:決策區塊的句子要嘛不納入(S2 改成 body/summary 才算),要嘛提醒字樣分流,講「決策裡的句子把 REVISIT 加在正文或摘要」,而且「3 行內」對決策不成立,得改成「同一篇」或不提醒。

**③-5(升級門檻)**
- 計劃原句:〈範圍〉不做③「寫治理帳」;〈回退〉「不寫帳、不寫檔」;〈做法〉7 第 2、4 條與 RETIRE-IF ①③「因為這個提醒而寫的條件式」
- 問題:提醒不留任何紀錄,事後只能拿量測程式對提交重跑規則。「同一次推送或兩週內配上」可以重放算出,但「因提醒而寫」無法判定:重放看不出寫的人有沒有被提醒過、有沒有 `--no-verify`、有沒有裝掛鉤。門檻 4、RETIRE-IF ③ 又依賴 drift 表態紀錄裡「綁錯事件」,而表態欄位沒有標記這條 REVISIT 是不是提醒引來的。
- 建議:門檻與撤除條件的分母改成「提醒之後兩週內在同一行附近新寫的條件式」(用重放可算的口徑),並承認歸因不了;或提醒印出時在提交訊息無關的地方留一個可數的標記(與「不寫帳」的取捨要 Enzo 裁)。

**③-6(掛點、提醒不進違規清單)**
- 計劃原句:〈做法〉3「在 `_note_shape_eval` … 多呼叫一次 `_ns_negation_hints(text, rows)`,回提醒清單…放進回傳的第三個值」;〈做法〉「效能」「正式工具只看一次提交的新行」;不做②「--diff 不印」
- 問題:`_note_shape_eval` 有三個呼叫端:`cmd_note_shape --staged`、`--diff`、`_note_shape_doctor_lines` 的事後掃描(最多 `_NS_DOCTOR_SCAN_CAP=200` 個提交,逐提交呼叫,且 `viol, _errs = res` 兩值解包)。放在 `_note_shape_eval` 裡等於 `--diff` 與 doctor 掃描也白算提醒(效能與「不做②」矛盾),回傳改三值也會讓那兩處解包炸掉。〈回退〉知道要一起還原,〈做法〉3 沒講怎麼避免。
- 建議:加參數 `hints=False`(預設關,只有 `--staged` 開),或把 `_ns_negation_hints` 從 eval 抽出來由 `cmd_note_shape` 在 `staged` 時自己呼叫(它已有 `_notelines_new` 的結果要重取的問題,得選一種);明寫兩個舊呼叫端不改。

**③-7(低)**
- 計劃原句:REVISIT 第 49 行「[when-symbol:…::_ns_negation_hints][by:2026-12-31] 實作上線了:記下上線提交,補一行上線後第 8 週的日期式 REVISIT…」與〈做法〉7 末的「[when-symbol:…][by:2026-12-31] 上線時把本節的『8 週後』換成實際日期…」;`Systems/筆記內容閘` 第 52 行還有第三條同條件
- 問題:同一個條件三處各一條,做同一件事(上線後補日期)。函式一出現三條同時被 drift check 要處理(而且是擋,見④-4)。另外這篇計劃自己有新寫的否定句(例:「擋還沒有設計(〈做法〉7)」),旁邊 3 行內沒有條件式,照本計劃規則會被自己提醒。
- 建議:合成一條;自己那句改成歷史說法或配條件。

## ④ 機械宣稱驗語意(6 條有問題;另列驗過屬實的)

**④-1(掛點)**
- 計劃宣稱:「逐行看 note-shape 已經算出的『這次新寫的行』(`_notelines_new` 回的 body/summary/decisions 三塊;開頭欄位其他欄不看)」
- 我讀的:`_note_shape_eval` 呼叫 `_notelines_new(..., keep_other=True)`(給 REVISIT 條件寫錯規則用),所以回來的 rows 含 `other` 區塊的行;`_notelines_new` 只有 `keep_other=False` 才只收三塊。
- 問題:`_ns_negation_hints(text, rows)` 收到的 rows 含開頭欄位其他欄,S2 的「開頭欄位其他欄不算」要靠自己濾 `reg != "other"`。參考實作 `scan_note` 有濾(`regions[i-1]=="other"` 跳過)。
- 建議:〈做法〉1 寫明「rows 進來後先濾掉 reg=="other"」。

**④-2(提醒不進違規清單)**
- 計劃宣稱:「提醒不進 violations,所以 rc、擋不擋、治理帳的違規條數都跟現在一樣」;S4「只有提醒、沒有別的違規,note-shape 應回 0 而且不寫治理帳」並且要印
- 我讀的:`cmd_note_shape` 在 `_note_shape_eval` 之後是 `viol, errs = res; if not viol and not errs: return 0`,在印任何東西之前就返回。warn 模式有違規才寫 `warned`、block 才回 1(那段 `return 1` 在印違規之後)。
- 問題:提醒放第三個值也不會被印,除非把那句早退改掉;改的時候要保證只有提醒時不走到 `_gate_event_or_warn(...,"warned",…)`(現有寫法只要走到那段就寫帳)。提醒段要插在 block 的 `return 1` 之前才會與違規同時出現。「違規條數不含提醒」這一句本身成立(`len(viol)+len(errs)`)。
- 建議:〈做法〉3 明寫「早退改成 `if not viol and not errs and not hints`;只有提醒時印完直接 `return 0`,不進 `_gate_event_or_warn`」;S4 那條測試涵蓋「只有提醒不寫帳」(現在的寫法很容易漏)。

**④-3**
- 計劃宣稱:「`.lumos/config.json` 的 `note_shape.negation`:warn/off,預設 warn…照 `_note_shape_config` 的讀法從被檢查的版本讀」;PRIOR-ART「子開關照 `drift_check.old_sentence` 的先例」
- 我讀的:`_note_shape_config(text)` 回 `(mode, warnings)`,只解析 `note_shape.gate`,預設 block;設定檔壞 JSON、`note_shape` 不是物件都回 block 加提醒。被檢查版本的讀法(`_nodehome_reader(root, tip_where)(".lumos/config.json")`)沿用沒問題(staged 時 tip_where="index")。`_drift_old_sentence_config` 先例是「預設 warn、認 block/warn/off、壞 JSON/非物件/壞值都照 warn 並提醒」。
- 問題:(a) 讀 `negation` 要另寫或擴充讀取函式,計劃只說「照讀法」。(b) 壞 JSON、`note_shape` 非物件時 negation 該怎樣沒寫(gate 那邊是 block+提醒;先例是 warn+提醒)。(c) 計劃刻意不收 `block`(「看不懂,照 warn」),跟 old_sentence 先例(收 block)不同,PRIOR-ART 卻寫「照先例」。
- 建議:補這三點;PRIOR-ART 註明「除了不收 block」。

**④-4(核心:條件式之後會發生什麼、升級門檻)**
- 計劃宣稱:「之後東西真的出現,既有的漂移檢查(推送時)與漂移掃描就會點名那一行」(〈白話〉);「漂移檢查與掃描:…點名、表態全是既有的」(〈做法〉6);「只提醒、不擋」
- 我讀的:`cmd_drift_check`/`_drift_check_c`:`_DRIFT_DEFAULT_GATE = "block"`(2026-09-30 起預設 block);`_drift_probe_check` 對候選行「終點成立而起點沒有同一條或還不成立 → 要處理」,`_drift_probe_judge` 對「這次新寫、終點已成立」也回要處理;`要處理` 在 block 模式 rc1 擋推送(`_drift_print...`「擋下」)。`_drift_probe_scan` 才是「該處理了」的列出。`when-symbol` 用 `_DriftProbeTree.one`→`_defines`:只認函式/類別/模組層指定的**定義**,不是「出現過名字」;`when-file` 是「檔在樹上」。
- 問題:(a) 「點名」低估——預設是擋推送。提醒字樣教人寫條件式,條件一成立(或一寫就已成立)那次推送會被 drift check 擋下,要 `drift ack`/`fix` 才能推。這是提醒的下游成本,計劃只在〈做法〉8 講「綁錯事件」。(b) 「條件優先綁那個東西本身」的 `when-symbol` 只判定義;句子講的是「某個流程/計劃」時綁 symbol 常永遠不成立或誤成立。(c) RETIRE-IF ③ 與門檻 4 以「被點名後表態還不是時候」量綁錯,但預設是擋,人可能直接 `ack`(理由怎麼寫影響判讀)。
- 建議:〈白話〉與〈做法〉6 把「點名」改成「新寫或條件成立那次推送,預設 block 會擋,可 `drift ack`」;提醒字樣加一句「條件已成立的話推送會被擋」;〈做法〉7 第 4 條註明表態欄位怎麼分「綁錯」與「就是該做」。

**④-5**
- 計劃宣稱:〈做法〉5「範本會注入每個專案的 CLAUDE.md,改完照既有流程重注入…(既有的範本同步測試會釘)」
- 我讀的:`scripts/templates/graph-discipline.md` 現在 11337 bytes;doctor Check D 的基線 `_DISCIPLINE_SLIM_BASELINE_BYTES = 5256`,超過 150%(7884)就 `warn_soft`「常駐的紀律範本長回五成以上了」,現況已是約 216%。同步驗證在 `_expected_claude_body` 與 doctor Check D。
- 問題:計劃往常駐範本加句子,沒提已經超過提示工程計劃設的體積線,也沒說這句要不要搬進 skill。
- 建議:〈做法〉5 記一筆「範本已超基線,這次加約 N bytes」,或改成範本只放一句指路、細節放 skill。

**④-6(掛點)**
- 計劃宣稱:「提醒…只在提交前印」;PRIOR-ART「提交前掛鉤與 CI 共用一支」
- 我讀的:`scripts/hooks/pre-commit` Gate NS:`if [[ -n "${CC_PY:-}" && -f "$REPO_ROOT/scripts/lumos" ]]`,而 `CC_PY` 只在 `$REPO_ROOT/scripts/lumos` 存在且 `_lumos_py314` 時才設。也就是只有 repo 裡有 `scripts/lumos`、且有 Python 3.14 時才跑;rc 不是 1 一律放行。
- 問題:提醒的觸及範圍(哪些專案、哪些機器)沒寫;RETIRE-IF ① 的「沒人理」可能只是沒看到。此外提醒只在提交前印,而寫的人常在 agent 對話裡執行 `git commit`,stderr 是否被 agent 讀到不確定。
- 建議:〈誠實界線〉補一條「沒裝掛鉤、沒 Python 3.14、`--no-verify` 的提交完全沒提醒」;RETIRE-IF ① 的分母排除這些。

### 驗過屬實(不算違規,供審查員省時間)
- `_visible_lines`(回 行號從1起+原始行,圍欄逐行 toggle)、`_strip_inline_markup`(回 (文字, 是否截斷),未閉合反引號之後不信)、`_revisit_split`(去一層列表/引用記號、表格行回 None、`cond/date/bad`)、`_probe_parse`、`_notelines_regions`、`_notelines_new`、`_note_shape_eval`、`cmd_note_shape`、`_note_shape_config`、`_note_shape_doctor_lines` 都存在,行為如計劃描述(除上列例外)。
- 表格行不能寫 REVISIT:`_revisit_split` 對 `|` 開頭回 None,`_ns_revisit_violations` 對表格內條件標記擋——屬實。
- 筆記內容審排除條件式 REVISIT:程式 `reg in ("body","summary") and _revisit_split(...)[0]=="cond"` 跳過,日期式照審——屬實(仍只限 body/summary,與 ③-4 同源)。
- 工具預告樣板:`guard plan` 寫 `TEST:還沒有測試在守這條…`、`WHY:[日期]預告這條合約但還沒做:…`、`為什麼還不做:…`(第三句在正文第 0 欄、沒有列表記號,計劃說「去掉列表記號後以…開頭」多餘但無害);`_guard_planned_prose` 用 `strip().startswith`,`_GUARD_WHY_MID = "]預告這條合約但還沒做:"`——屬實。
- 未完全等價處在 ③-2、③-3。S1 例句用參考實作 `classify_text` 逐句實跑,除 `satisfied/tension/todo 合計`(參考實作因 `re.I` 會提醒,計劃靠分大小寫排除,屬已宣告的差異 2)外都與條款一致。
- E5:條件式的 `[by:]` 到期由 doctor E5 唸(`_revisit_lines` 取 by 當日期)——屬實。
- `docs` 引用:`Projects/存量漂移防線_計劃`〈做法〉第 0、2 節與第 2 節第 5 點、[S10],`Projects/新增名稱否定句檢查_計劃`、`Projects/筆記形狀擋_計劃`、`Projects/筆記內容審_計劃`、`Systems/筆記內容閘`(含帳本雜訊的 WHY)、三篇 Issue、報告第 5、6 節與 `neg_revisit_measure.py`、`labels-2026-09-30.json`——都存在。
- 表 1 數字自洽:55/174=31.6%、44/173=25.4%(門檻 3 的「25%–32%」);100=93+7+1−1、78=84+8−14(差異 1–4 加總)成立;13/30 的 95% 區間約 27%–61%;22 行拆 12/7/3 成立。

## 總結

| 類別 | 條數 |
|---|---|
| ① 未定義的詞 | 4 |
| ② 壞引用 | 2 |
| ③ 範圍自相矛盾 | 7 |
| ④ 機械宣稱驗語意 | 6 |
| 合計 | 19 |

**動到核心裁定的條目**
- 掛點(note-shape 哪一層、哪個模式印):③-1、③-6、④-1、④-6,以及 ①-1(上線點)
- 提醒不進違規清單(rc、治理帳不變):④-2、③-6(三值回傳會弄壞 doctor 掃描的兩值解包)
- 否定字眼表與過濾規則:③-2(any 對每處各判,與「一字不差照參考實作」矛盾,S8 會撞未宣告差異)、①-4(英文整字邊界)、③-3(已配判法與參考實作不同)
- 哪些句子算已配:③-4(決策區塊配不成,照提醒做反而被擋)、③-3、①-2(前後 3 行是否含空行)
- 升級門檻(擋的前提與撤除條件):③-5(「因提醒而寫」無法歸因,又不寫帳)、④-4(下游 drift check 預設是擋不是點名,影響門檻 4 與 RETIRE-IF ③ 的解讀)、②-1(動機依據的 33/11 找不到出處)
