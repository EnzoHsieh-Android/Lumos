severity: major

# 代碼審修正關卡第0步 設計審 r1:正確性-opus

鏡頭:正確性與邏輯。立場:假設照字面實作會在某個輸入上判錯,找出那個輸入。
實驗環境:`git clone --shared` 到 `f0-r1-work-正確性-opus/repo`,在 clone 上 `git worktree add --detach .../tree HEAD` 建樹,用 SourceFileLoader 載入 `scripts/lumos` 直接呼叫函式。

## 先記已實測、行為跟計劃描述相符的部分(不是 finding)

- 第 3 項:`_platform_test_index(Path(樹))` 在本 repo(單平台)回 `default=python`、平台根就是樹、方法集 1412 支,`t_spec_gate_zero_ran_is_weak`、`t_loop_next_disposal_cmd_actually_runs` 都在。
- 第 4 項:`_run_bound_tests(Path(樹), items, tails)` 跑兩支,8.6 秒。`t_spec_gate_zero_ran_is_weak` 判 green、n=1;`t_spec_gate_needs`(撞到 `t_spec_gate_needs_rollback`、`t_spec_gate_needs_method_filter`)n=2、宣告 2,`_spec_gate_verdict` 判 weak「篩選匹配到 2 支,測試名要唯一…(程式裡有 2 支名字對得上)」,跟 S4 寫的字樣一致。
- 第 5 項:`_bound_tests_check(Path(樹), "a5877e38~1..HEAD")` 回 `green`、59 支、跑 247.1 秒、算 58.4 秒,總共 281 秒。`bound-tests` 事件寫在樹的 `docs/.governance-log.jsonl`(樹多 1 行),clone 主目錄的 `git status` 沒變,跟計劃描述一致。
- 規格閘共用函式:`_spec_gate_run_clauses` 與 `_spec_gate_regress` 兩處都可以改成「共用函式回逐支 (編號, 平台, 方法, 紅綠弱, 原因, detail) 加跑不起來原因,聚合、印出、略過或記失敗留在呼叫端」,字面保得住(措辭問題見 F7)。
- `_codeloop_record_valid_ex` 在玩具 repo 上的結果:事件之後只提交 `docs/.canary-log.jsonl` 判有效;只提交 `governance/review-reports/…/r1-fix.json` 判有效;提交圖譜筆記判無效;壓提交判無效(「不是目標的祖先」);空字串、`zz` 判無效;8 碼短 sha 會判有效,所以計劃先驗 40 碼十六進位是必要的。

## F1 平台根寫絕對路徑時,先決條件照樣通過,但樹裡的第 3、4、5 項都跑在主工作目錄
severity: major
blocking: 是
引句:「每個平台的平台根(`load_platforms` 解析後)都在 repo 頂底下」
file: `scripts/lumos:4852`
file: `scripts/lumos:38635`

1. 輸入:`.lumos/config.json` 的某個平台寫 `"root": "/Users/x/proj/ios"`,也就是指向主工作目錄底下的絕對路徑。`load_platforms` 不擋絕對路徑:`repo_root / root_str` 碰到絕對路徑時會把基底整個換掉。
2. 先決條件是在建樹之前(①)用主工作目錄的設定算的。這個根在 repo 頂底下,所以通過。
3. 進到樹以後,`load_platforms(樹)` 解析出來的還是同一條主工作目錄路徑。實測:
   `tree -> …/f0-r1-work-正確性-opus/repo/scripts | under main: True | under tree: False`
   結果有三處受影響:
   - 第 3 項的 `methods_for` 掃的是主工作目錄。
   - 第 4 項 `_run_bound_tests` 的 `cwd=pentry["root"]` 也是主工作目錄。
   - 第 5 項經 `_bound_tests_for_diff` 一樣跑在主工作目錄。
   於是「已提交的版本是紅的、沒提交的修正讓它變綠」也會判過,「跑的期間別的會談改檔、提交都不影響這次結果」不成立。這是該擋的被放過。
4. 同一個根因還有一條路徑:設定檔有進版控、但主工作目錄有沒提交的設定改動時,先決條件驗的是主工作目錄那一版,樹用的是提交那一版。
   - 主工作目錄那一版把 `../x` 改成 `ios` 但沒提交:先決條件放行,樹裡的根解析到暫存資料夾外、不存在,第 3 項全部判「找不到」。
   - 反過來,提交那一版有 `default_platform` 之類的錯:`_platform_test_index(樹)` 丟 `ValueError`,計劃沒寫這時第 3 項怎麼處理。
5. 改法方向:先決條件改成在樹準備好之後用 `load_platforms(樹)` 判,要求每個平台根解析後都在樹底下(兩邊都先取實際路徑)。不在樹底下的回 2,跟 `../` 走同一條路。
6. 本機 4 個多平台專案目前都寫相對路徑(`.`、`.maestro/`),沒有人實際撞到。不過設定檔允許這種寫法,計劃自己也把「平台路徑在樹裡解析不到」列成要擋的情況。

## F2 依賴資料夾連回主工作目錄後,工作區套件與可編輯安裝會載入主工作目錄的原始碼,不是樹裡的
severity: major
blocking: 是
引句:「依賴資料夾:repo 頂與每個平台根各用 `_lint_link_deps` 把 `node_modules`、`.venv`、`venv` 連回主工作目錄的同一位置」
file: `scripts/lumos:23636`

1. 輸入:Node 多套件專案(npm/pnpm workspaces)。`node_modules/ws -> ../packages/ws` 是相對連結,而 `node_modules` 整個被連回主工作目錄。從樹裡解析 `node_modules/ws` 時,相對連結以真實位置為基準,結果落到主工作目錄的 `packages/ws`。
2. 最小實驗:在 main 底下建 `packages/ws/index.js`(內容「main 未提交版」)和 `node_modules/ws -> ../packages/ws`;在 tree 底下建 `packages/ws/index.js`(內容「樹裡提交版」);再呼叫 `_lint_link_deps(main, tree)`。輸出:
   `樹裡 require("ws") 讀到: main 未提交版 | 實際路徑: …/nodedemo/main/packages/ws/index.js`
   Node 預設不保留符號連結(`preserveSymlinks` 預設 false),實際 `require` 也是載入這支。
3. Python 也一樣:用 src 版型、`pip install -e .` 裝進 `.venv`,而 `run_cmd` 用 `.venv/bin/python -m pytest -k {method}`。`.venv` 裡的 `__editable__…pth` 寫的是主工作目錄 `src/` 的絕對路徑,樹裡的測試 `import mypkg` 會載入主工作目錄的程式。
4. 後果:修正還沒提交、或提交的那版是壞的時,第 4、5 項測的其實是主工作目錄的程式,紅的會被判成綠。〈實務隱患〉只承認「依賴版本跟提交不一致」這個天花板,沒有寫到「專案自己的原始碼被換成主工作目錄那一份」。S4 驗「主工作目錄 git status 不變」也抓不到這件事。
5. 這跟新增告警閘的天花板不一樣:lint 只讀檔案,不會 import 專案自己的套件。至少要在〈實務隱患〉寫明,並在「只印提醒」那段的判斷裡加一條:工作目錄有沒提交的改動,而且專案用工作區或可編輯安裝時,提醒的措辭要改成「結果可能測到沒提交的版本」。或者改成只連第三方依賴,工作區連結在樹裡重建。

## F3 S1–S12 沒有一條在多平台設定下跑第 3–5 項與樹的準備;照字面傳字串路徑,多平台專案會直接當掉
severity: major
blocking: 是
引句:「而且在樹的測試索引裡找得到(`_platform_test_index(樹)`,`Class.Method` 寫法照那段的處理)」
file: `scripts/lumos:14203`
file: `scripts/lumos:4852`

1. 共用工作樹函式是從 guard kill 抽出來的,guard kill 的樹路徑是 `os.path.join(tmp_parent, "wt")`,是字串。計劃只在第 5 項寫了 `Path(樹)`,第 3 項、第 4 項(`load_platforms(樹)`、`_platform_test_index(樹)`)和樹的準備(`_lint_link_deps`)都直接寫「樹」。
2. 實測傳字串的結果:
   - 多平台設定下 `load_platforms(str)` 丟 `TypeError: unsupported operand type(s) for /: 'str' and 'str'`。
   - `_lint_link_deps(str, str)` 不管單平台還是多平台都丟同一個 `TypeError`。
   - 單平台(legacy)的 `load_platforms(str)` 不會當,因為 root 直接等於傳進去的值。
3. 本 repo 是單平台,S3/S4/S12 的測試 fixture 照現有規格閘 fixture 的寫法也是單平台。S2 唯一一條多平台情境(平台根在 repo 外)在建樹之前就回 2 了,S11 的多平台情境測的是 guard kill,不是 fix-check。
   所以「第 3、4 項在多平台當掉」以及 F1 的絕對路徑,S1–S12 全綠也照樣過得去。本機 4 個用 lumos 的消費專案(mOrangePos、pos-ios、pos-guest-flutter、lumos-stack-verify)全是多平台設定,也就是說真正要用的專案都落在沒測到的那條路徑上。
4. 當掉的後果:沒有寫事件、沒有回 1 或 2,只印例外;`loop next` 會一直提醒,而照提醒去跑 fix-check 也永遠跑不過。
5. 要補的有兩件:
   - 計劃寫明共用函式回 `Path`,或者每個呼叫點都包 `Path(樹)`。
   - 加一條條款,在兩個平台(其中一個平台根在子資料夾)的 fixture 上跑通第 3、4、5 項與依賴連結,斷言測試是在「樹/子資料夾」裡跑。

## F4 「other」類跟「other」類也算同類連兩輪,兩件不相干的修正會被要求寫「上次修法為什麼沒守住」
severity: minor
blocking: 否
引句:「審查帳上這一輪的前一輪(照帳上輪次出現的順序)有修正紀錄、其中有一組跟這組同類別」

1. 輸入:r1 的修正紀錄有一組 `category: other, note: 文件連結失效`;r2 有一組 `category: other, note: 時區換算`,收的發現 `finding_severities` 記 major。
2. 照第 2 項字面,這兩組同類別,r2 這組要寫 `prior.why_failed`、`prior.new_approach` 各十個字,沒寫就回 1。
3. `other` 是「不在清單裡的雜項」,兩個 `other` 不代表同一個根因。編排者只能寫一段湊字數的理由才過得去,REVISIT 那天數「擋在哪一項」時,第 2 項的擋下次數會被這種情況灌水。改法:`other` 不參加同類比對,或者改比 `note`。

## F5 改名一律判不過,而且沒有能過的路;經由 rebase 帶進來的上游改名也算進去
severity: minor
blocking: 否
引句:「`base..修正後` 有程式檔被改名時(`git diff -M --name-status -z` 的改名條目,判程式檔用 `_nodehome_code_kind`)這項也判不過」
file: `scripts/lumos:24804`

1. 輸入 A:修正本身把 `scripts/a.py` 改名成 `scripts/b.py`,重構常見這種做法。之後不管修正紀錄怎麼改、測試怎麼修,第 5 項都判不過,只剩 `LUMOS_SKIP_FIX_CHECK` 一條路。
2. 輸入 B:派工之後 `git pull --rebase`,主線上別人改了某支檔的名字。計劃不要求 `base` 是修正後的祖先,`base..修正後` 是兩個端點直接比對,會把上游的改名也算進來,這輪同樣永遠判不過。
3. `_nodehome_code_kind` 對沒有副檔名的檔一律回 `shebang?`,所以 `LICENSE`、`.gitkeep`、`Dockerfile` 改名也算程式檔改名。
4. 後果是這一輪的 `loop next` 一直提醒,編排者只能選擇跳過。RETIRE-IF 的「跳過比例」和「擋下的項目裡沒有一條是真的有缺」都會被這種擋法灌水。計劃至少要寫明這是接受的代價,並在提醒裡指路;或者改成把改名條目的舊路徑也餵給 impact,至於那是不是另開的 Issue,交給編排者判斷。

## F6 壓提交或 amend 之後內容一模一樣,提醒還是會再響
severity: minor
blocking: 否
引句:「同一個提交,或是祖先而且中間只動了簿記檔——跟代碼審留痕失不失效同一套;判不了也當作無效」
file: `scripts/lumos:39244`

1. 輸入:在 X fix-check 判過,接著照專案慣例「推之前壓成一個」做 `git reset --soft <merge-base> && git commit`,得到 Y,兩邊的樹完全相同。
2. 玩具 repo 實測:`_codeloop_record_valid_ex(X, Y)` 回 `False`,原因是「不是目標的祖先——多半是壓過提交或 rebase」。`loop next` 因此再提醒一次,得重跑大約 5 分鐘。
3. 計劃在〈實務隱患〉講的是「提交了簿記檔以外的檔就再提醒」,沒講到「內容沒變、只是改寫歷史」也會再提醒。這不會讓壞的修正被放過,只是多一次假提醒。可以在 `_codeloop_record_valid_ex` 判無效之前,先比較 `git diff --quiet X Y -- . ':!<簿記檔>'`;不改的話,至少把這種情況寫進〈實務隱患〉。

## F7 「原始失敗尾巴」指的是 `_run_bound_tests` 結果裡的 detail,不是 tails;寫錯的話相依回歸的紅字面會變
severity: minor
blocking: 否
引句:「相依回歸的紅字面用的是原始失敗尾巴,不是原因,所以兩個都要回」
file: `scripts/lumos:6676`
file: `scripts/lumos:38622`
file: `scripts/lumos:38644`

1. 相依回歸印的是 `紅({str(detail)[:80]})`,這個 `detail` 是 `_run_bound_tests` 結果元組的第 5 欄,紅的時候是 `rc=N <最後 120 字>`,懸空的時候是「綁的測試在程式碼裡找不到(懸空)」。
2. `_run_bound_tests` 另外還有一個 `tails` 輸出(原始輸出的尾巴,最多 256KB),而且非 `real` 的項目(相依回歸會送 `dangling` 進去)根本不會寫進 `tails`。
3. 計劃說的「`_run_bound_tests` 給的原始失敗尾巴」兩種讀法都說得通。如果實作拿的是 `tails`:懸空那條會印成 `紅()`,真紅的那條會印出輸出最前面的 80 個字,字面就變了。S12 要抓得到這件事,fixture 裡得有一條懸空、一條真紅的相依回歸。建議把措辭改成「結果裡的 detail」,或者在 S12 寫明這兩種情況。

## F8 幾條會判錯的分支沒有條款釘住
severity: minor
blocking: 否
引句:「`green`、`no-pins`、`no-bound`、`no-vault` 過,後三種印說明」

下面這些行為,實作寫反的話 S1–S12 全綠也照樣過:
1. 第 5 項的狀態對應:S5 只測了 red、green、skipped、沒設 run_cmd、改名。`unfilterable`、`no-config`、`diff-unavailable`、`range-unavailable` 判不過,`no-pins`、`no-bound`、`no-vault` 判過,這兩組都沒有條款。實作把 `no-config` 歸到「過」不會有任何一條紅。
2. `skipped-env` 事件之後又提交了程式:照計劃要回到提醒,而不是印「已跳過」。S8 只測「有同輪 skipped-env 就印已跳過」。
3. `unaffected` 的檔在修正後已經不存在要判不過:S1 只列了「函式段是空的或找不到」。
4. `canary record --regression-set` 沒帶 `--loop` 要回 2:做法裡寫了,S9 沒列。
5. 同類連兩輪的「前一輪照帳上出現的順序」:S6 沒有 r1、r3、r2 這種亂序的 fixture,不過 `cmd_loop_next` 本身會擋非連續重現,所以實際影響只在「輪次字串不照數字排」這一種情況。

## 各節逐節核對

- 名詞:已讀,無 finding。核對過 `_MANUAL_MIN_CHARS`(4)、`_nodehome_code_kind` 回 `shebang?` 或 `ext` 或 `None`、`finding_kinds` 與 `finding_severities` 在 `cmd_canary` 都強制全集(`set(kinds) != F` 回 2),所以「給就要給全」屬實,「沒記類別」只會是整筆沒帶。
- 範圍:已讀,無 finding。
- 修正紀錄:F4。`base` 用 `rev-parse --verify --end-of-options` 轉換、`--no-renames -z` 比對改名與中文檔名、刪掉的檔不驗函式段,這幾段已讀,沒找到判錯的輸入。
- `lumos loop fix-check` 執行順序、先決條件、清殘骸、樹的準備:F1、F2、F3。
- 逐項驗 1–5:F1、F3、F5、F8。第 3 項不過的不送第 4 項、第 4 項沒有 `{method}` 判不過,這兩點已讀,無 finding。
- 記帳與跳過:已讀,無 finding。`_gate_event` 沒拿到 `head_sha` 時會自己補 `rev-parse HEAD`,所以 `skipped-env` 事件也有 40 碼,`loop next` 判得了。三本帳既有的 `head_sha` 全是字串(1784 筆)、`secs` 全是浮點(254 筆)、`record_sha256` 與 `failed_items` 是 0 筆,加型別不會讓既有行被丟。
- 共用函式:F7。guard kill 在 `worktree add` 失敗、保留樹、清理順序這幾條路徑上的現況已讀,計劃的契約跟現況一致。
- `lumos loop next` 的提醒與記帳範本:F6。`disposal_cmd` 只在 `plant-canary` 而且不是 light 或 legacy 時才吐,計劃寫「第 2 輪起」跟 `n_next` 對得上。代碼審的 315 筆載體席全都帶 `round`(實數),不會有循序帳沒有輪次、提醒卻永遠滿足不了的情況。
- `canary record --regression-set`:F8 第 4 點,其餘已讀,無 finding。
- 上線、回退:已讀,無 finding。
- 實務隱患:F2(漏列的風險類)。逐類檢查:
  - 時間:實測 281 秒,跟計劃估的約 5 分鐘相符。
  - 並行:清殘骸只清超過一天的,同時跑的另一次 fix-check 不會被清,無。
  - 殘骸:另一個 repo 留下的同前綴殘骸,`worktree remove` 會失敗,接著 `rmtree` 照刪,那個 repo 的 `.git/worktrees` 管理紀錄要等它自己 prune 才清掉,不影響判定,無。
  - 金流、對外送出:無。

最高等級:major,blocking 共 3 條
