severity: major

# r2 架構對齊-sonnet(對照 repo 根:scratchpad/negguard,下文 `scripts/lumos` 皆指它)

四問總答(各問後面是細節,finding 在下方):
- 問 1 分層與依賴方向:fix-check 當 `_bound_tests_check` 的新呼叫端、借 `_lint_link_deps`、`_kill_run` 跨段使用,方向跟鄰居一樣(file: `scripts/lumos:38923`、`scripts/lumos:39659`、`scripts/lumos:39697` 是現有三個呼叫端;file: `scripts/lumos:38641` 是合約測試閘跨段用 guard kill 區的 `_kill_run`,同一種先例)。不一致處在「逐支真跑那層」另起一套(F1)與「共用函式放哪、環境變數穿幾層」沒寫(F2、F5)。
- 問 2 命名與錯誤處理:閘名 `fix-check`、kind `passed`/`blocked`/`skipped-env`、`LUMOS_SKIP_FIX_CHECK`、`--repo`、`--round`、欄位 `secs`/`round`/`loop` 跟鄰居一致(file: `scripts/lumos:25830` note-shape 用 `blocked`/`warned`/`passed`;file: `scripts/lumos:31835` drift-check 同;file: `scripts/lumos:41109` `loop status` 的 `--repo`;file: `scripts/lumos:41051` `canary record` 的 `--round`;file: `scripts/lumos:38373` bound-tests 的 `secs`)。不一致:`--template`(F4)、`fix_check.max_minutes` 的單位與讀取函式(F3)。
- 問 3 第二種做法:殘骸標記檔+行程編號、SIGTERM 轉例外,專案裡沒有既有做法(`grep -n 'signal.signal\|KeyboardInterrupt\|atexit\|os.kill(' scripts/lumos` 對這些全 0 筆;`worktree prune` 只出現在 guard kill 的 finally,file: `scripts/lumos:14320`),不算另起爐灶。樣板產生沿用「印到標準輸出不寫檔」的先例(file: `scripts/lumos:33928`)。設定讀取:見 F3。真正的第二種做法是逐支紅綠判定(F1)。
- 問 4 落點:見 F6。新開 `Systems/代碼審修正關卡`、guard-kill 補共用函式合理;`regression_set` 落點有疑問。

## F1 先紅後綠的「跑一支、讀支數、判紅綠」自己重寫一套,沒沿用規格閘與合約測試閘已有的那條
severity: major
blocking: 是
引句:「每支測試(去重)先在綠樹跑、再在紅樹跑。支數用 `_ran_count` 讀:」
file: `scripts/lumos:6584`
file: `scripts/lumos:6628`
file: `scripts/lumos:38606`
file: `scripts/lumos:38498`
1. 既有做法:`_run_bound_tests(repo_root, items, tails=tails)` 逐支真跑(依完整指令去重、逾時讀 `LUMOS_TEST_TIMEOUT`、非 0 判 red、0 但證不出跑過判 unproven、`{method}` 缺判 no-cmd),`tails` 帶回輸出尾巴;規格閘接著用 `_ran_count` 讀「篩到幾支」,交 `_spec_gate_verdict`(file: `scripts/lumos:6584`)判 red/green/weak(支數 ≥2 判「篩選匹配到 N 支,測試名要唯一」、n==1 且被跳過判弱證據、n==0 或 unproven 判弱證據、讀不出支數則「只印有沒有跑過」)。規格閘的雙向門(`door == "low"`)本身就是「每條各自紅、keeps 的綠」的先紅後綠判法(file: `scripts/lumos:6748`、`scripts/lumos:6779`)。
2. 這份設計的第 4 項把同一組判定逐條重寫:綠=0 結束且支數 ≥1;紅=非 0 且支數恰好 1、沒被跳過;支數 ≥2 → 「名字選中 N 支」;支數 0 → 「選不到這支測試」;讀不出支數 → 標「讀不出跑了幾支」;逾時、無 `{method}` 各一條。這跟 `_spec_gate_verdict` 的規則幾乎逐條對得上,只差「紅樹要的是 red、綠樹要的是 green」這個外殼。
3. 〈PRIOR-ART〉寫「全部沿用,不另想一套」,但名字只點到 `cmd_guard_kill`、`_lint_link_deps`、`_bound_tests_check`;`_run_bound_tests`、`_spec_gate_verdict` 整份計劃沒出現。〈做法〉第 4 項也沒說這層是呼叫它們還是自己迴圈跑 `_kill_run`。字面實作會得到第三份(`_run_bound_tests`、規格閘判定、fix-check 自己的)「跑一支測試判紅綠」邏輯,三份各自演進:例如日後改 `_ran_count` 的跳過判法、`_RAN_EVIDENCE` 的樣式或逾時變數,fix-check 那份得另外同步。
4. 要處理的差異是真的:`_run_bound_tests` 沒有環境變數參數(TMPDIR)與總時間預算,規格閘的判定也只在綠樹跑一次。但鄰居的處理方式是「在共用函式上加選填參數」(如 `tails=`、`keep_re=`、`advisory=`),不是另寫迴圈;這份設計只對 `_kill_run` 加 env 參數,沒打算對 `_run_bound_tests` / `_spec_gate_verdict` 做同樣的事。
5. 判成 major 的依據:嚴重度錨「引入了第二種做法」。⚠ 設計沒寫死是不是自寫迴圈(只描述判定規則、沒有函式名),若編排者確認第 4 項實作會經 `_run_bound_tests`(items 用平台+方法、在紅/綠樹各呼叫一次、`tails` 取支數)再把紅樹的判定抽成與 `_spec_gate_verdict` 共用的一支,本條可降為 minor「措辭沒點名」;無論哪種,都要把沿用的函式名寫進〈做法〉第 4 項與 PRIOR-ART。未實測,依據是讀碼。

## F2 共用隔離工作樹函式放哪、殘骸標記與 SIGTERM 歸誰,沒寫清楚;同一支共用函式會有兩種生命週期
severity: minor
blocking: 否
引句:「每個工作樹建立時在暫存資料夾放一個寫著行程編號的標記檔;每次 `fix-check` 一開始,掃 `git worktree list --porcelain` 裡路徑帶修正關卡前綴、標記檔的行程已經不在的」
file: `scripts/lumos:14202`
file: `scripts/lumos:14310`
file: `scripts/lumos:23630`
1. 〈共用的隔離工作樹〉把 guard kill 的「mkdtemp(`lumos-kill-` 前綴)+ `worktree add --detach` + finally 收」抽成共用函式,guard kill 與修正關卡都用;但標記檔、殘骸掃描、SIGTERM 轉例外三樣只寫在〈中斷與殘骸〉、只對「修正關卡前綴」與 `fix-check` 生效。
2. 結果:同一支共用函式建出兩種樹,一種(修正關卡)有標記檔+下次清+SIGTERM 收,一種(guard kill)被 SIGTERM/SIGKILL 時照舊留殘骸(現行 finally 同樣收不到 SIGKILL,file: `scripts/lumos:14310`)。這不是第二種做法(專案沒有既有的標記檔先例,見問 3 的 grep),但標記檔寫在共用函式裡還是 fix-check 自己寫、共用函式放在哪一段(鄰居:`_lint_link_deps` 在 lint-new 段、`_kill_run` 在 guard kill 段,各被別的閘跨段借用),設計都沒指名,實作者會各自決定。
3. ⚠ 判成 minor:結構上沒有跨層直呼;要編排者決定標記檔是否進共用函式(讓 guard kill 一併受益,前綴參數就是清理的鍵),並在〈共用的隔離工作樹〉寫出函式名與位置。

## F3 `fix_check.max_minutes` 單位與鄰居不同;第 1 步用到的設定沒有指名讀取函式;所指的 `_ci_config` 失敗語意與敘述相反
severity: minor
blocking: 否
引句:「新增設定讀取函式(照 `_ci_config` 那類的寫法:沒設定用預設、讀不懂用預設並警告)」
file: `scripts/lumos:34517`
file: `scripts/lumos:23507`
file: `scripts/lumos:22554`
1. `_ci_config` 讀不懂時是「功能全關(fail-safe)」(file: `scripts/lumos:34517`),不是「用預設並警告」;敘述的行為其實是 `_lint_new_config` / `_stack_questions_config` 那一類(回帶 `warnings` 的 cfg dict、不合法的鍵退預設並記警告,file: `scripts/lumos:23507`)。引用的鄰居跟描述的行為對不上,照字面找 `_ci_config` 來抄會得到相反的失敗方向。
2. 鄰居的時間類設定一律是秒:`lint_new.budget_sec`、`per_cmd_floor_sec`(file: `scripts/lumos:23531`)。這份設計同一個 `fix_check` 區塊裡 `max_minutes` 是分鐘、`stress[].timeout` 是秒,區塊內單位混用。
3. 第 1 步就讀 `fix_check.max_minutes`(項目 6),但〈做法〉裡「設定讀取函式」只出現在〈第 2 步〉的壓力指令;第 1 步沒指名讀取函式,第 2 步又「新增」一支,容易長成兩處各讀一次 `.lumos/config.json` 的 `fix_check` 區塊。
4. minor:結構(讀 `.lumos/config.json` 的一個區塊、回帶警告的 cfg)對,錯在引用對象、單位、與第 1 步沒有讀取函式。

## F4 `--template` 在 guard-scaffold 已是「帶路徑的選項」,樣板旗標的既有寫法是 `--dispositions-template`
severity: minor
blocking: 否
引句:「`lumos loop fix-check <迴圈編號> --round <輪> --template` 印出骨架到標準輸出(照表態樣板的做法,不寫檔)」
file: `scripts/lumos:41207`
file: `scripts/lumos:41525`
1. 設計宣稱照表態樣板的做法;表態樣板的旗標是不帶值的 `--dispositions-template`(file: `scripts/lumos:41525`),印到標準輸出不寫檔(file: `scripts/lumos:33928`)這一點相同。
2. 但 `--template` 在 `guard-scaffold` 上是「範本路徑」(`gs.add_argument("--template", help="範本路徑…")`,file: `scripts/lumos:41207`),同一個旗標名在兩個指令上一個要值、一個是開關。
3. minor:不影響結構,只是命名;可改 `--fix-template` 之類帶指令名的寫法,或在〈做法〉明講接受這個差異。

## F5 TMPDIR 只加在 `_kill_run`,但第 5 項經 `_bound_tests_check` → `_run_bound_tests` → `_kill_run` 三層才到它,環境變數穿不過去;`_kill_run` 變更的落點也沒涵蓋 bound-tests-gate
severity: minor
blocking: 否
引句:「跑測試時 `TMPDIR` 指到修正關卡自己的暫存資料夾,跟工作樹一起刪(本 repo 的測試工具紅的時候會在 `TMPDIR` 留暫存現場)。」
file: `scripts/lumos:38641`
file: `scripts/lumos:38725`
file: `scripts/lumos:38787`
1. 〈中斷與殘骸〉只說對 `_kill_run` 加「選填參數帶環境變數」。第 4 項若自己呼叫 `_kill_run` 才拿得到;第 5 項呼叫 `_bound_tests_check(綠樹, …)`,它內部走 `_run_bound_tests` 再到 `_kill_run`(file: `scripts/lumos:38787`、`scripts/lumos:38641`),兩層簽名都沒有環境變數參數,設計也沒說要加。受波及合約測試紅的時候,暫存現場會留在系統 TMPDIR、不跟工作樹一起刪。
2. 鄰居的做法是把選填參數一層層傳下去(`payload=`、`advisory=` 就是這樣穿過 `_bound_tests_check`),這份設計沒寫要穿幾層。
3. `_kill_run` 被合約測試閘使用(file: `scripts/lumos:38641`),〈要同步的文件〉只列 guard-kill 補共用函式、沒列 bound-tests-gate;「被中斷時收乾淨」的行為改動落在 `_kill_run` 的家(依專案鐵則 5 要寫進改到那支檔的家)與 bound-tests-gate 的描述都沒指名。
4. ⚠ minor:這是補丁與原文銜接處的缺口;要編排者決定是否把環境變數參數穿過 `_run_bound_tests`/`_bound_tests_check`,並在〈要同步的文件〉補 bound-tests-gate。

## F6 `regression_set` 欄位的落點:同族欄位(`folded_set`、`finding_kinds`)的說明在 finding-refute,不在 loop-convergence-recording
severity: minor
blocking: 否
引句:「[[Systems/loop-convergence-recording]] 補 `regression_set` 欄與 `loop next` 提醒」
file: `docs/lumos-toolchain-knowledge/Systems/finding-refute.md:94`
file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:31`
1. `loop-convergence-recording`(174 行)對 `folded_set`、`finding_kinds`、`--finding-kind` 的提及是 0 次(`grep -c` 實測);這幾個欄位與「記帳一致性契約」寫在 `finding-refute`(105 行)(file: `docs/lumos-toolchain-knowledge/Systems/finding-refute.md:94`)。`--regression-set` 的解析「照 `--folded-set`」、語意還拿 `--finding-kind` 當對照,寫在同族那篇比較順。
2. 反過來,`loop next` 的提醒/提示放 `loop-convergence-recording` 有先例(`[cap-hint]` 段就在那裡,file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:31`),所以那一半落點合理。
3. 其餘兩個落點合理:新開 `Systems/代碼審修正關卡` 管指令本體(命名中英混用在 Systems 下有先例:`guard-kill`、`bound-tests-gate`、`棧別提問表態閘`);`guard-kill`(116 行)補共用工作樹函式是它原本的責任範圍(隔離工作樹+跑測試)。
4. minor:`canary record` 欄位拆兩篇寫(`regression_set` 在 loop-convergence-recording、其兄弟欄位在 finding-refute)會讓下一個讀者找不到全貌;可在 finding-refute 補一行指到新欄位,或把 `regression_set` 放 finding-refute。⚠ 交編排者判。

不對齊共 6 條,其中 major 1 條。
最高等級:major,blocking 共 1 條
