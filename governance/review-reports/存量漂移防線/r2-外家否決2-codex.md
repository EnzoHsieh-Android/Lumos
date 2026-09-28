severity: major

## F1 表態命令無法兌現種類綁定與失效理由回顯

severity: major

blocking: 是 — 不補表態鍵與失效配對規則，實作者無法判斷該豁免哪個發現，也無法穩定找回舊理由。

引句:「綁①那一行的內容編號(借 `_notelines_content_id`:路徑、區塊、小標題、行文字)②**發現種類**(`probe` 或 `c1`…`c4`)」

file: `scripts/lumos:23822`

1. 指令只有 `<節點> <內容編號> --reason`，沒有 `--kind`。同一行可同時是 c4 與 probe，例如 `valid_under` 同時含「未提交」與 `[when-status:…]`；命令無從選擇要豁免哪一種。
2. `_notelines_content_id` 還綁區塊與小標題。只改標題、行文字不變時，內容編號仍會改，違反 S3「那行沒改、同一種原因時不再擋」。
3. 行文字或路徑改掉後，新編號跟舊編號沒有可逆關係。規格沒有要求表態紀錄保存原路徑、區塊、標題、原文，也沒有定義改名或改句後的配對算法，因此「印出舊理由」無法可靠實作。

## F2 六十秒後放行讓閘的涵蓋率由掃描順序決定

severity: major

blocking: 是 — 大圖譜或刻意堆疊探針可耗盡預算，使真正由本次推送觸發的條件未評估而放行。

引句:「總預算用完,剩下沒判的行數印出來、記 `degraded`、不擋。」

1. 規格沒有要求先評估本次 diff 直接相關的探針、快取相同查詢、批次 grep，或保留預算給新增及可能轉真的條件。
2. 只要前面的條件耗完六十秒，後面的 false→true 條件就不會進入「要處理」，block 模式仍回 0。
3. `degraded` 只留下觀測，沒有讓 CI 或推送失敗；因此這不只是健檢少列，而是可重現的閘繞過路徑。

## F3 c1 漏掉 settle 明列要修的摘要 WHY

severity: major

blocking: 是 — 部分轉正或舊資料只殘留摘要 WHY 時，scan 與推送閘會判成一致。

引句:「驗證紀錄 status 是 pass、有 `guards` 欄,而且還有 `guard plan` 寫的固定句」

file: `scripts/lumos:11568`

1. `guard plan` 實際固定產生三句：摘要 WHY、摘要 TEST、正文「為什麼還不做」。
2. settle 的修訂要求三句全改，但 c1 只檢查摘要 TEST 與正文，沒有檢查摘要 `WHY:[日期]預告這條合約但還沒做:`。
3. 輸入一篇 `status: pass`、TEST 與正文已修、只剩摘要 WHY 的守衛紀錄，c1 會漏掉唯一仍在講「還沒做」的舊句。

## F4 條件語法的合法輸入集合與掃描邊界未定義一致

severity: major

blocking: 是 — 照不同合理解讀實作，會在壞條件漏擋與把範例誤當探針之間分叉。

引句:「條件鍵不認得或值是空的也擋。舊行不管。」

file: `scripts/lumos:29249`

1. 條件被允許放在任何筆記行，但形狀擋只驗新寫的 `REVISIT:`；非 REVISIT 行的 `[when-status:節點]`、`[when-symbol:路徑::]` 可直接落地。
2. 「鍵存在、值非空」不足以驗四種值：`when-status` 是否必須有 `=`、空 symbol、非法 repo 路徑，以及值中的 `]`、`::`、`=`、`|` 如何跳脫都沒定義。
3. 第一層排除圍欄與表格，條件掃描卻宣稱任何行都可放，沒有說 inline code、圍欄、表格中的語法範例算不算真探針。本 spec 自己就含多個字面條件範例。
4. `_lens_git` 只把引數原樣交給 git；規格沒有要求 `git grep -e <值> … -- <路徑>` 這類 option terminator。以 `-` 開頭的值可被合理但不安全的實作解讀成 git 選項。

## F5 全面排除 REVISIT 讓新現況宣稱繞過內容審

severity: major

blocking: 是 — 作者只要在現況句前加合法日期，就同時通過第一層並消失於第二層。

引句:「第二層的待審行排除以 `REVISIT:` 開頭的行」

file: `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md:42`

1. `REVISIT:2027-01-01 現在沒有權限檢查，之後補` 的第一格是合法日期，所以第一層放行。
2. 新規則又讓整行退出第二層；其中「現在沒有權限檢查」正是範圍章節交給筆記內容審處理的程式現況宣稱。
3. 第二層目前尚未接入 hook/CI；即使日後接線，按本設計仍永久跳過此類行。排除應只涵蓋機械條件部分或純待辦形狀，不能按行首全面豁免。

## F6 when-test 沒有帶入函式必需的提交版面資料

severity: major

blocking: 是 — Swift、Kotlin、Android 等棧的合法測試檔會被判成非測試，條件永遠不成立。

引句:「在被檢查的樹裡,`_nodehome_is_test` 認得的測試檔中有這個名稱」

file: `scripts/lumos:22402`

file: `scripts/lumos:22453`

1. `_nodehome_is_test(path, layout=({}, {}))` 的預設 layout 是空的；`AppTests/Support.swift`、`app/src/androidTest/.../Support.kt` 這類棧別測試目錄要靠 `_nodehome_layout(all_paths)` 才能認出。
2. spec 只寫借 `_nodehome_is_test`，沒有要求先對被檢查提交的整棵樹算 layout 並傳入。
3. 現有考卷沒有 `when-test` probe，這個錯法也不會被驗收門檻抓到。

## F7 非 Python 粗比對會漏掉真正的定義事件

severity: major

blocking: 是 — 誠實界線把 false positive 錯寫成只會多列一次，實際會吞掉後續真事件。

引句:「條件可能提早成立(多列一次,不會漏)。消費專案(Swift、Kotlin、Dart…)用這種條件時」

1. 若註解或字串先出現名稱，條件會在那個提交提前變成 true。
2. 真正定義稍後加入時，起點與終點都是 true；check 只擋 false→true，因此真正事件不再列出。
3. 帶路徑不能修正同一檔內的註解、字串與定義重名。這是確定的漏抓，不是單純多擋一次。

## F8 B3 有兩套互斥的失效提交

severity: major

blocking: 是 — `drift exam` 沒有權威事件來源，依 JSON 或 probes 實作會得出相反成績。

引句:「每題:編號、分類、判定、機制、筆記路徑、行號、原文、小標題、失效提交」

file: `governance/eval/drift-exam/rtb-2026-09-28.json:186`

file: `governance/eval/drift-exam/rtb-2026-09-28-probes.json:14`

1. 主考卷 B3 的 `invalidating_commits` 是 `b9c7496`、`8ff8c95`；改寫檔的 `event_commit` 是 `f183cd8`。
2. 唯讀重驗顯示 `f183cd8^` 尚無 Phase 12 計劃，`f183cd8` 建立計劃且 `status: doing`，正是 false→true。
3. `b9c7496` 與 `8ff8c95` 的父版、終版都已是 `doing`，用主考卷欄位跑只會得到 true→true，不會擋到。
4. spec 說乙對「失效提交」跑，卻未定義 JSON 與 probe 衝突時以誰為準。

## F9 B2 宣稱拆兩行，改寫檔實際只考一半

severity: minor

blocking: 否 — 現有 probe 仍能考到檔案條件，但不能證明 spec 宣稱的任一條件拆行行為。

引句:「對 A7、B1、B2(拆兩行)、B3、B4 與非漂移的 B5」

file: `governance/eval/drift-exam/rtb-2026-09-28-probes.json:10`

1. probes 只有一筆 B2，內容只覆蓋「分析行程有正式啟動程式」。
2. 誠實界線又明寫後半「改接外部模型」沒有可寫的檔或名稱，考試只考前半。
3. 因此「B2 拆兩行」是錯誤宣稱；兩行任一成立的接受測試實際不存在。

## F10 考卷更正紀錄與 D6 證據仍有事實錯誤

severity: minor

blocking: 否 — 分類結果未因此翻轉，但卷證無法支持其自稱的更正完整性。

引句:「設計審 r1 查出 4 題失效提交寫錯,已更正並留紀錄」

file: `governance/eval/drift-exam/README.md:15`

file: `governance/eval/drift-exam/rtb-2026-09-28.json:359`

file: `governance/audits/2026-09-28-rtb-drift-rootcause/rootcause.md:62`

1. README 只列 A5、A6、E1 三題的失效提交更正；A4、A5 的另一次修正是 `note_at_event` 路徑，不是第四題失效提交。
2. D6 的 `code_evidence` 宣稱短名 `test_restart_recovery_requires_the_held_keys` 在 `b8c6ccc` 建立。
3. 唯讀 git 重驗顯示 `b8c6ccc` 與 HEAD 都只有 `test_restart_recovery_requires_the_held_keys_and_the_age_cutoff`。根因報告也明載短名從一開始就寫錯。
4. D6 仍屬 true-not-drift，但考卷給出的證據方向相反。

## F11 回退指令列不出所有會被舊 E5 判壞的條件

severity: major

blocking: 是 — 照回退章節操作後，遺漏的節點會讓 doctor 重新報格式損毀。

引句:「得先把條件式改寫成日期(`lumos search "[when-"` 列出全部)」

file: `scripts/lumos:3428`

file: `scripts/lumos:3647`

file: `scripts/lumos:1954`

1. `lumos search` 預設 `include_superseded=False`，會隱藏 superseded 節點。
2. doctor E5 直接遍歷 `env.notes`，沒有排除 superseded 節點。
3. 因此 superseded 筆記中的條件式 REVISIT 不會被回退搜尋列出，E5 還原舊解析器後卻會把它們算成壞格式。回退命令至少缺 `--include-superseded`。

## F12 併發段落處理的是 Git 合併，不是已知的同檔競寫

severity: major

blocking: 是 — 新增的表態與事件寫入者仍會產生被讀端靜默捨棄的壞 JSONL。

引句:「表態檔是只追加的 jsonl,兩條分支各自追加合併會有衝突行」

file: `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md:23`

file: `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md:31`

1. 既有 Issue 指的是兩個程序同時 append 同一實體檔，資料可黏成壞行，讀端解析失敗後靜默略過。
2. spec 回答的是兩條 Git 分支合併衝突；「手動保留兩邊」無法修復執行時已互相穿插或已被略過的資料。
3. 新增 `drift ack` 與 drift-check 事件會增加同類寫入者。ack 遺失會重新擋人，event 遺失會讓 RETIRE-IF 的統計失真。
4. 已知 Issue 要求所有寫入者共用同一把鎖；本 spec 只替 settle 加鎖，沒有替新增帳本寫入定義鎖與失敗語意。

## F13 lands_in 漏列實際被改的系統家

severity: minor

blocking: 否 — 程式仍可實作，但守衛與治理帳的系統節點會少掉本次行為變更脈絡。

引句:「整個 settle 包在 `_vault_write_lock` 裡;先改家筆記的預告行」

file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:14`

file: `docs/lumos-toolchain-knowledge/Issues/治理帳多個寫入者都沒上鎖.md:39`

1. frontmatter 的 `lands_in` 只有存量漂移守衛、筆記內容閘、筆記內容審。
2. `guard settle` 的現有機制家是 `Systems/guard-kill`；本設計改寫入順序、鎖與補救路徑，卻沒把它列入落點。
3. 新增 governance event 與表態帳也波及 `Systems/reversibility-governance-ledger`，至少應明定是否寫回該家或另立帳本之家。

## F14 三分支最長時間少算了一次完整 scan

severity: minor

blocking: 否 — 不會判錯，但推送與 CI 的最壞時間、逾時配置會被低估。

引句:「三個分支一起推最多約 3 分鐘,實際條件少時遠低於此。」

file: `scripts/hooks/pre-push:171`

file: `scripts/hooks/pre-push:206`

file: `.github/workflows/ci.yml:96`

1. doctor 在逐分支迴圈前先跑一次；規格又令 doctor Z 執行一次最多六十秒的 scan。
2. 之後三個分支各有一個六十秒 check，明列上限應是約四分鐘，不是三分鐘。
3. CI 也會先跑 doctor、再跑 drift check，單次最壞新增約兩分鐘。

## F15 c3 沒定義空或壞 plan_refs 的真值

severity: minor

blocking: 否 — c3 只列不擋，但不同實作者會對同一筆記產生不同清單。

引句:「驗證紀錄 status 是 pending,`plan_refs` 列的計劃全都已收尾。」

1. `plan_refs: []` 可被解成「列出的計劃全都已收尾」的空集合真，也可被解成根本沒有適用計劃。
2. 引用不存在、引用到非 project、或部分引用無法解析時，規格也沒有定義是 c3、寫錯條件、判不了，還是略過。
3. S7 要求 c3 成立與不成立都判對，卻沒有足夠條件成為測試 oracle。

## F16 set 的連帶待辦沒有定義要印哪種指令

severity: minor

blocking: 否 — 功能只多印不自動寫入，但輸出契約與測試預期仍不確定。

引句:「每項給一行要敲的指令。不是計劃、或不是改成 done/superseded 就不印」

1. c2 同段承認連結有時只是參考，SIGTERM Issue 就是刻意保持 open。
2. 若輸出 `lumos set <Issue> status done`，使用者照敲會錯關合法 Issue；若輸出 `lumos context`，則只是檢視，不是處理待辦。
3. spec 與 S6 都未列各類待辦的確切指令及何時只能檢視，實作者無法形成唯一輸出。

### 逐節覆蓋

- frontmatter、白話、依據、PRIOR-ART、RETIRE-IF、範圍：已讀；除 F13 外無 finding。移出的丙、符號及測試存在性機制沒有被重新要求實作。
- 共用指令家族：F1、F2、F12、F14。
- 甲／狀態連帶：F3、F15、F16；settle 的鎖、原子寫入、補救順序本身已讀,無其他 finding。
- 乙／條件語法：F4、F5、F6、F7。
- 考卷與考法：F8、F9、F10；其餘 probe 的唯讀前後驗證成立：A7/B4 在 `0ffba7d`、B1/B2/B5 在 `8ff8c95`、B3 在 `f183cd8`。
- 掃全圖譜、修復與接線：已讀,無獨立 finding。
- S1–S17：已讀；缺口已分別錨定上述 finding，無額外 finding。
- 回退：F11；settle 補救與三態關閉路徑已讀,無其他 finding。
- 誠實界線與審計修正紀錄：F7、F9、F10。
- 考試結果、修復結果：目前是明示待實作占位，已讀,無 finding。

### 既有節點影響判定

- `Projects/舊句偵測實驗_計劃`：不影響；本 spec 沒有重新實作機制①，D4–D6 僅作非漂移對照。
- `Projects/code側刪除傳播守衛_計劃`：不影響；沒有更動 delguard 的 token、時限或提醒語意，新閘是平行路徑。
- `Projects/筆記形狀擋_計劃`、`Systems/筆記內容閘`：有影響；新增 REVISIT 形狀規則，但 F4 尚未把適用行與完整值語法定死。
- `Projects/筆記內容審_計劃`、`Systems/筆記內容審`：有影響；`_note_audit_items` 的整行排除形成 F5；原系統目前尚未接入 hook/CI。
- `Systems/guard-kill`：有影響；settle 行為被改，補救方向合理，但落點漏列見 F13。
- `Issues/存量筆記漂移三種機制_rtb根因回饋`：部分解決機制②③；F3、F5–F8 仍會留下漏抓。
- `Issues/治理帳多個寫入者都沒上鎖`：會惡化；新增寫入者但沒有解掉同檔競寫，見 F12。

### 實務隱患覆蓋

- 判錯與漏抓：有，F3–F8。
- 表態完整性：有，F1、F12。
- 效能與降級：有，F2、F14。
- 併發與資料完整性：有，F12。
- 回退與可恢復性：有，F11；settle 的半套補救已讀,無其他 finding。
- 多語言相容性：有，F6、F7。
- 輸入與命令安全：有，F4；值的字元域及 git option 隔離沒有合約。
- 驗收可信度：有，F8–F10。
- 金流：無；不讀寫付款、金額或帳務資料。
- 對外送出：無；設計只操作本機 repo 與 git 物件。
- 不可逆：無；計劃中的內容改寫與新增檔均受 git 管理，且主要寫入採原子替換。
- 新依賴與供應鏈：無；設計沿用 Python 標準庫及既有單檔 CLI。

最高 major，blocking 共 10 條。