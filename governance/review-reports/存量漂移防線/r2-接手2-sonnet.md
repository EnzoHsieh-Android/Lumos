severity: major

鏡頭:整合與知識同步(三個月後接手視角)。逐節讀完 r2-snapshot.md,對照 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos`(34289 行)與 `scripts/test_lumos.py` 現況逐一開函式驗證借用宣稱。

## F1 `[when-test:...]` 借 `_nodehome_is_test` 沒借它要求的 layout 參數,非標準測試資料夾會被判「測試不存在」

severity: major
blocking: 是 — 消費專案用 Android/iOS/不同棧的非標準測試資料夾(androidTest、PosTerminalTests 等)寫 `[when-test:]` 條件時,工具會判「測試不存在」而永遠不觸發/永遠判錯,是靜默的錯誤判定,不是效能或風格問題。
引句:「`_nodehome_is_test` 認得的測試檔中有這個名稱(Python 找 `def <名>`,其他語言找整字)」

1. `_nodehome_is_test(path, layout=({}, {}))`(`scripts/lumos:22453`)有兩層判定:先問 `_testmap_is_test`(只認 `test/`、`tests/`、`__tests__/`、`specs/` 目錄與 `test_`/`_test` 等檔名慣例),再問 `_nodehome_in_stack_test_dir(path, layout)`(`scripts/lumos:22421`)——後者要靠 `layout` 才能認「各棧的測試資料夾」(androidTest、`PosTerminalTests/` 等,函式自己的註解點名 2026-09-12 就是為了這些才加的)。
2. `layout` 的正確算法是先對整棵樹跑 `_nodehome_layout(all_paths)`(`scripts/lumos:22402`),再把結果傳進去——全庫唯一一處這樣正確用的呼叫在 `scripts/lumos:22640`(`layout = _nodehome_layout(side.all_paths)` 接著 `scripts/lumos:22647` 才呼叫 `_nodehome_is_test(p, layout)`)。全庫另一處呼叫(`scripts/lumos:6204`)用的是預設值 `layout=({}, {})`。
3. 用預設 `({}, {})` 時,`_nodehome_in_stack_test_dir` 裡 `top_exts.get(base, ())` 與 `main_exts.get(...)` 永遠拿到空集合,函式必然回 False——等於「各棧測試資料夾」判定被靜默關掉。
4. 而且 `_nodehome_is_test` 的第三步(`scripts/lumos:22462`)是:副檔名若在 `_TESTMAP_EXTS = {"kt","java","cs","py","ts","tsx","js","jsx","vue","swift","sql"}`(`scripts/lumos:26641`)裡,就直接信「測試地圖」的判定、回 False,**不會**再落到後面「泛用 `tests?/` 目錄名」那條寬鬆規則。具體可重現的例子:`app/src/androidTest/com/foo/MyTest.kt`——`_testmap_is_test` 判 False(目錄名是 `androidTest` 不是 `test(s)/`,檔名 `MyTest.kt` 也對不上 `.spec./.test./test_/_test` 任何一種寫法),`_nodehome_in_stack_test_dir` 在沒有 layout 時也判 False,而 `.kt` 又在 `_TESTMAP_EXTS` 裡——三步都判完就直接回 False,判定「這不是測試檔」。
5. 設計文件(第 2 節第 1 點,`REVISIT:[when-file:...]` 那條上面)只寫「借 `_nodehome_is_test`(路徑規則,可對任何提交的樹用)」,完全沒提要先算 `_nodehome_layout(all_paths)` 再傳進去——照文件字面借用,自然會走 `scripts/lumos:6204` 那種「不帶 layout」的用法,直接繼承上述誤判。這正是〈誠實界線〉第二條承認的「非 Python 整字比對」以外的另一種誤判,而且方向相反:誠實界線講的是「條件提早成立、多列一次」,這裡是**條件該成立卻永遠不成立**——`[when-test:]` 用在這些測試檔上會一直判「還沒有」,drift check 永遠不會因為測試補上而放行,REVISIT 那行永遠卡著。

## F2 第一層新增的 REVISIT 格式擋,借的是 `_notelines_new`/`_notelines_regions`,跟宣稱的「跟 E5 同一套判定」不是同一套,圍欄與表格排除會落空

severity: major
blocking: 是 — 會把筆記裡示範 REVISIT 條件式寫法的圍欄範例(這種筆記本來就該有,因為這功能本身就需要文件)當成違規擋下,直接違反這條規則自己開的測試契約 [S10]。
引句:「新寫的 `REVISIT:` 行(可見行、不在圍欄與表格裡,跟 E5 同一套判定)」

1. E5(`scripts/lumos:1944-1989`)的「可見行」是 `_search_visible_lines`(`scripts/lumos:3298`),底層 `_visible_lines(keep_fenced=False)` 會把 ``` 圍欄內容整段隱形,E5 另外手動加一條 `_pr5.lstrip().startswith("|")` 排除表格行;`scripts/test_lumos.py:34570` 就是專門測這兩種排除(`"# 回訪乙\n\`\`\`\nREVISIT:2020-01-01 code區不算\n\`\`\`\n| REVISIT:2020-01-01 表格不算 |\n"`)。
2. 第一層(筆記形狀擋)現有的「這次新寫的行」機制走的是另一條路:`_note_shape_eval`(`scripts/lumos:23926`)呼叫 `_notelines_new`(`scripts/lumos:23690`),它的行篩選只靠 `_notelines_regions(text)`(`scripts/lumos:23522`)——這支函式只用開頭欄位的 `summary`/`decisions`/`body` 分區(`TOP_KEY_RE`)決定 region,**完全不解析 markdown 圍欄或表格語法**,通篇沒有任何 fence-toggle 或 `|` 開頭判斷。
3. 這不是我猜的邊界:`scripts/lumos:2697-2698` 明寫過同一種坑已經在別處踩過一次(「圍欄內是語法範例不是宣稱——Check N 自家節點的範例曾被當真標記掃,每次 doctor 都喊一條假漂移」),而且全庫有獨立的「剝圍欄唯一實作」`_strip_fences_text`/`_strip_code_text`(`scripts/lumos:161-162`),`_notelines_new` 這條路完全沒用到。
4. 設計文件把這條新規則放進「筆記形狀擋(第一層)」、緊接在既有「①這次新增的行(跟筆記內容審共用同一支)」(`_note_shape_eval` 第 1 步,`scripts/lumos:23946-23949`)旁邊,最自然的實作路徑就是掛在同一條 `_notelines_new`/`_ns_check_line` 管線上——而這條管線沒有圍欄/表格感知。要真的做到「跟 E5 同一套判定」,得另外把 `_search_visible_lines` 那套邏輯搬進這條管線,但文件的〈借用〉清單完全沒提這一步,S10 測試名字承諾的行為([test:t_note_shape_revisit_needs_date_or_probe] 要求「圍欄與表格裡的行與舊行不應管」)因此有落空的具體路徑。

## F3 第二層排除 REVISIT 行只講「以 REVISIT: 開頭」,沒提列項符號前綴,會漏掉本庫常見的「- REVISIT:」寫法,讓 r1 已經判 blocker 的互鎖風險留著

severity: major
blocking: 是 — S12 存在的目的就是避免第一層(條件式)與第二層(判成「描述程式現況」而要求刪掉)互鎖,這在 r1 被外家判過 blocker;若排除判定漏掉列項符號前綴,大多數真實 REVISIT 行仍會進第二層待審,原地重現同一個 blocker。
引句:「第二層的待審行排除以 `REVISIT:` 開頭的行」

1. E5 自己對列項符號的處理很明確:`scripts/lumos:1961-1962`——`if _l5.startswith(("- ", "* ")): _l5 = _l5[2:].lstrip()`,先剝掉 `- `/`* ` 前綴才判斷是不是 `REVISIT:` 開頭。
2. 本庫現有 REVISIT 行絕大多數就是這種列項寫法,不是裸行:`docs/lumos-toolchain-knowledge/Projects/收斂閘漏項敏感度v2_計劃.md:217`、`docs/lumos-toolchain-knowledge/Projects/工具鏈全環節體檢_調研.md:20`、`docs/lumos-toolchain-knowledge/Projects/loop數據收集_計劃.md:110-111` 等多篇都是 `- REVISIT:...`。CLAUDE.md 鐵則四本身給的範例也是「寫成獨立一行 `REVISIT:YYYY-MM-DD ...`」沒禁止列項,而本庫實務上列項寫法明顯更常見。
3. 第二層待審行的產生點在 `_note_audit_items`(`scripts/lumos:24282`)裡逐行組 `items` 那段(`scripts/lumos:24311-24326`),目前完全沒有任何「先剝列項符號」的前處理。文件第 2 節第 5 點(`scripts/lumos:74`)與條款 [S12](`scripts/lumos` 對應 `governance/review-reports/存量漂移防線/r2-snapshot.md:109`)都只寫「排除以 `REVISIT:` 開頭的行」,沒有像 S10 那樣特別點名要對齊 E5 的列項符號剝除規則。照字面實作(`ln.strip().startswith("REVISIT:")`)會讓 `- REVISIT:...` 這種本庫主流寫法繼續進 `_note_audit_items` 的待審清單,而〈審計修正紀錄〉裡 r1 外家 blocker 折入的正是「REVISIT 行從第二層待審排除,避免條件式被判成描述程式現況而要求刪掉」——這裡的實作細節缺口會讓那個已經判過 blocker 的問題,對本庫最常見的寫法原地重現。

## F4 `lands_in` 點名的 `Systems/存量漂移守衛` 不存在,全篇正文沒有任何一處描述要開這篇、它的 `responsibility`/`about_code` 該怎麼跟另外兩篇分工

severity: major
blocking: 是 — 違反 CLAUDE.md 鐵則五「每支檔有家」:落地時找不到家,要嘛新功能的大半程式碼(`lumos drift` 整個指令家族、條件語法評估、c1–c4 狀態一致檢查、考卷指令)沒有家可以寫回,要嘛實作者臨場現拍 `responsibility`,跟另外兩篇既有節點的分工邊界完全沒有設計依據。
引句:「Systems/存量漂移守衛」

1. 我在被審 repo 裡確認過:`docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md` 不存在;全庫只有這份計劃自己與 `Projects/舊句偵測實驗_計劃`、`Issues/存量筆記漂移三種機制_rtb根因回饋` 提到「存量漂移」四字,沒有第三篇 Systems 節點。
2. `lands_in`(`governance/review-reports/存量漂移防線/r2-snapshot.md:10-13`)列了三篇:`Systems/存量漂移守衛`、`Systems/筆記內容閘`、`Systems/筆記內容審`。後兩篇是既有節點,而且各自的 `responsibility` 明寫排除這份計劃的核心範圍——`Systems/筆記內容閘.md`:「不管程式檔歸屬(那是每支檔有家)、不管推送前判定者怎麼判(那是筆記內容審)」;`Systems/筆記內容審.md`:「不管新筆記行怎麼從 git 抽(那是筆記內容閘的共用函式)、不管形狀擋(第一層)」。兩篇加起來能收的只有 S10(第一層新規則)、S11(E5 一處改動)、S12(第二層排除),對應〈做法〉第 2 節第 2、2-4、2-5 點。
3. `lumos drift check/scan/ack/exam` 整個指令家族、`guard settle` 改寫、`lumos set` 連帶待辦、c1–c4 四種狀態一致檢查、doctor Z 段——這些是〈做法〉第 0、1、3 節的主體,S1–S9、S13–S17 幾乎全部條款——照上面兩篇既有節點自己劃的界線,都不屬於它們,理應落在第三篇。但全文除了 `lands_in` 那一行,沒有任何段落交代這篇要不要新開、`about_code` 該列哪些檔案、`responsibility` 一句話怎麼寫、跟另外兩篇的分工邊界在哪。三個月後接手的人照著 `lands_in` 去找,會發現指標指向一個不存在、也沒人交代過內容的節點。

## F5 接線門檻用單一外部 repo(rtb)11 正例、13 反例的小樣本,直接決定所有消費專案更新後的全域預設(block 或 warn)

severity: minor
blocking: 否 — 有 `drift_check.gate=warn|off` 的立即逃生口與兩個月後的 RETIRE-IF 回頭量測,不至於做出「壞系統」,但决策本身的統計基礎薄,值得在文件裡標注這是已知取捨而不是靠樣本量撐住的結論。⚠
引句:「就預設 block;否則先 warn,攤給 Enzo 裁」

1. 甲乙合計要考的題目是「11 題加非漂移對照」(〈範圍〉,`governance/review-reports/存量漂移防線/r2-snapshot.md:33`),我核對 `governance/eval/drift-exam/rtb-2026-09-28.json` 確認:機制②③(甲乙)共 11 題(A4–A7、B1–B4、E1–E3),非漂移對照 13 題(A8、A9、B5、D4–D6、E4、I1–I3、R1–R3)——與〈做法〉第 3 節列的題號完全對得上。
2. 〈做法〉第 4 節第 4 點的接線門檻是「非漂移零誤列、每提交要處理 ≤5」就全域預設 `block`——這個預設值一旦寫進程式碼(「設定檔沒寫時的預設值寫在程式裡」,〈做法〉第 0 節),影響的是**所有**之後執行 `lumos update` 的消費專案,不是只有 rtb 或工具鏈自己。用單一外部 repo、13 個非漂移反例「零誤列」就外推成全域預設,統計上很容易是運氣(反例基數小,10% 左右的真實誤報率也有不低機率在 13 個裡開天窗式地全過)。
3. 這一點文件本身有部分自覺(RETIRE-IF ①「推送時被 drift check 擋下的,作者表態『沒過期、照留』的比例超過一半」、REVISIT:2026-11-28),但那是上線兩個月後的事後量測,不是上線前的門檻設計依據——上線那一刻起、到 REVISIT 那天之前,全域 block 或 warn 的選擇仍然建立在這 13 個反例上。

## F6 doctor E5 印「條件式回頭條件 N 條」的承諾,在零到期、零壞損時會被既有的靜默閘擋住不印

severity: major
blocking: 是 — 違反 S11「工具應…印出條件式回頭條件的條數」的字面要求,而且恰好在最早期(還沒有任何條件式行到期或壞損,但已經有人開始寫 `[when-...]`)最容易踩到,直接讓「就算推送閘拔掉,這些行在 doctor 還看得到」這句設計動機落空。
引句:「doctor 既有的 E5 日期檢查改一處:第一格以 `[when-` 開頭的行不算」

1. E5 現有整段輸出被 `scripts/lumos:1974` 這一行閘住:`if _rv_due or _rv_bad: section("E5", ...)`——`_rv_due`(到期清單)與 `_rv_bad`(壞日期計數)都是 0 時整段連 `section()` 都不呼叫,是設計本身寫明的「全靜默:0 到期 0 壞行整段不印」(`scripts/lumos:1948` 註解)。
2. 設計文件(第 2 節第 2 點,`governance/review-reports/存量漂移防線/r2-snapshot.md:71`)只要求「第一格以 `[when-` 開頭的行不算日期格式壞損,另印條件式回頭條件 N 條」,而且明講「doctor 既有的 E5 日期檢查改一處」——用詞是「一處」,對應的自然實作是只在原本 `_rv_bad += 1` 那個分支前插入一個 `_datev.startswith("[when-")` 的例外(把它導去一個新的 `_rv_probe` 計數,不進 `_rv_bad`),而不去動最外層的 `if _rv_due or _rv_bad:` 閘。
3. 這樣一來,一個專案剛開始採用條件式 REVISIT、還沒有任何一條真的到期或寫錯格式時(`_rv_due == 0`、`_rv_bad == 0`,但 `_rv_probe > 0`),E5 整段仍然不會印,S11 承諾的「印出條件式回頭條件的條數」就在這個最常見的早期情境裡不會發生——要避開這個坑,`if _rv_due or _rv_bad:` 那一行也得跟著改成把 `_rv_probe` 算進去,但文件沒有提到這一步,而且「只改一處」的措辭反而暗示不要動它。

## 其餘節閱讀紀錄(本鏡頭範圍內,無 finding)

- 〈範圍〉、〈做法〉第 0 節共用指令家族(`_lens_push_base`、`_nodehome_clamp_base`、`_nodehome_reader`):三支函式的參數、回傳形狀與語意逐一開檔核對過(`scripts/lumos:29220`、`22967`、`22551`),跟文件描述一致,借用寫法可行,已讀無 finding。
- 〈做法〉第 1 節甲(guard settle、狀態一致檢查 c1–c4、`lumos set` 連帶待辦):`edit_fm_sync_status_tag`(`scripts/lumos:13956`)、`atomic_write_verify`(`scripts/lumos:14181`)、`_vault_write_lock`(`scripts/lumos:14251`,巢狀可重入)逐一核對過語意可用;`cmd_guard_settle` 現況(`scripts/lumos:11792`)證實了文件要修的「找不到預告行就整個擋死、半套卡住」是真實存在的問題(`_guard_planned_line` 找不到預告行時直接回錯誤訊息、settle 回 2,沒有任何補救路徑),S5 補救路徑的設計方向是對的。`guards`/`plan_refs`/`valid_under` 等欄位名稱都核對到實際程式碼裡的常數與寫入邏輯,一致。已讀,除 F1、F6 外無其他 finding。
- 〈做法〉第 3 節考卷與考法、〈條款〉、〈回退〉、〈實務隱患〉、〈誠實界線〉、〈審計修正紀錄〉:交叉引用（節號、[test:]/[manual:] 標記、r1 折入項)逐條核對過,內部一致,沒有指向不存在目標的連結。除 F4(`lands_in`)、F5(接線門檻)外無其他 finding。
- 〈考試結果〉〈修復結果〉:目前留白,符合〈審計修正紀錄〉與 S15/S16 的「還沒考/還沒做」狀態,不算缺陷。

## 總結

六條發現,最高等級 major;blocking 五條(F1、F2、F3、F4、F6),不擋一條(F5,已標 ⚠)。
