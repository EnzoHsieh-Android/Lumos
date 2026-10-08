severity: major

# r3 通才-opus 席報告(代碼審修正關卡第0步,第 3 輪)

實驗都在 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/f0-r3-work-通才-opus/` 底下做(`repo` 是 `--shared` clone,版本 7f57df4a;腳本 `plat.py`、`e2e5.py`、`cfgbad.py`、`names.py`、`tree_node.py` 都留在那裡,可以重跑)。派工點名要驗的三件事,結論先講:
- ①拿掉驗不了的平台:第 3、4、5 項讀同一份改過的設定,但三項對「被拿掉的平台」反應不一樣。拿掉的如果正好是 `default_platform`,三項全倒;子模組的平台根也漏判(F1、F2、F4)。這一版還把「`load_platforms(樹)` 丟例外就回 2」那條先決條件刪了(F3)。
- ②依賴資料夾預設連回主工作目錄:本 repo 跟最小 Node 專案在樹裡都跑得起來,實測見〈樹的準備〉一節,沒有 finding。
- ③測試名格式:`web:t_x`、Kotlin 拆掉反引號後的名字、`a]b`、`a,b` 的判法都跟設計一致,沒有 finding。

## F1 被拿掉平台的測試如果綁在受波及合約上,第 5 項會一直判紅,同一行裡其他平台的測試也跟著不跑
severity: major
blocking: 是
引句:「這樣只有那個平台不驗,同一專案別的平台照驗」
file: `scripts/lumos:4908`
file: `scripts/lumos:38431`
file: `scripts/lumos:38624`
1. 〈樹的準備〉把驗不了的平台從樹裡那份設定刪掉。第 5 項 `_bound_tests_check(樹, …)` 讀的就是這份設定,所以合約行裡 `[test:被拿掉的平台:名]` 交給 `resolve_test_refs` 時,會因為「平台前綴未定義」丟 `ValueError`。
2. `_bound_tests_for_diff` 接到這個例外,把**整條合約行**記成一筆 `bad-name`(`scripts/lumos:38431-38432`)。`_run_bound_tests` 再把 `bad-name` 直接判成 `red`,原因寫「測試名不合法或平台前綴未定義」。所以第 5 項回 `red`,整次判不過。
3. 端到端重現(`e2e5.py`):用測試總檔的 `_mk_bound_tests_repo` 造一個 repo,合約寫成 `[test:t_pay_ok, maestro:flow_login]`,設定成兩個平台:`api` 的平台根是 `.`,`maestro` 的平台根是 `.maestro/`(沒進版控)。照字面把 maestro 從設定拿掉,再跑 `_bound_tests_check(dd,"HEAD~1..HEAD")`,輸出:
   `第5項 status: red`
   `reason: 受波及合約的測試沒過:Systems/Pay.md [[test:maestro:flow_login] 的平台前綴 'maestro' 未定義於 platforms(api] 測試名不合法或平台前綴未定義`
   `api` 平台的 `t_pay_ok` 明明是綠的,卻完全沒跑。同一份設定在主工作目錄跑推送前那道閘,maestro 只會記成「沒設 run_cmd、沒跑」,不會判紅。
4. 結果是:只要 `base..修正後` 改到的檔牽連到綁了被拿掉平台測試的合約,第 5 項每次都判不過,原因還寫成「測試名不合法」,這跟〈樹的準備〉保證的「平台 X 這次不驗」和「其他平台照驗」都對不上。修正關卡沒有能修好它的辦法,只能用 `LUMOS_SKIP_FIX_CHECK` 跳過,`loop next` 會一直提醒。第 3 項有特別寫「附『平台 X 這次不驗』的原因」,第 5 項完全沒有對應的處理,三項的行為不一致。
5. pos-ios 現在的 `[test:maestro:menu_main_visual]` 寫在一般的 `KEY:` 行、不是 ★INVARIANT★,所以今天還不會撞到。但 pos-ios 設定裡的說明已經寫了之後要綁 `[test:maestro:…]`,一綁上就會撞。
6. 要補兩件事:第 5 項裡,解析時遇到被拿掉的平台前綴,要當成「這個平台這次不驗」,跳過那一支、印說明,不能判紅;同一行裡其他平台的測試照跑。要嘛在共用的「測試名解析」函式加一個參數,傳入被拿掉的平台清單;要嘛第 5 項不改設定,改成在結果裡把這些平台濾掉。條款 S2 或 S5 也要補一個情境:「合約同一行綁兩個平台、其中一個被拿掉」。

## F2 被拿掉的平台如果正好是 `default_platform`,第 3、4、5 項全倒,「其他平台照驗」不成立
severity: major
blocking: 是
引句:「拿掉之後一個平台都不剩 → 回 2」
file: `scripts/lumos:4864`
1. 設計只規定「一個平台都不剩就回 2」,沒有規定被拿掉的是 `default_platform` 時怎麼辦。`load_platforms` 遇到「預設平台不在清單裡」會丟 `ValueError`(`scripts/lumos:4864-4865`)。
2. 實測(`plat.py` 的 A 段):設定是 `default_platform: web`,`web` 的平台根不存在,另有一個正常的 `api` 平台。照字面拿掉 web 之後:
   `load_platforms: ValueError 預設平台 'web' 不在平台清單裡(有的是: api)`
   `_platform_test_index: ValueError …`(第 3 項的索引)
   `_run_bound_tests: (None, "config platforms 壞: 預設平台 'web' 不在平台清單裡(有的是: api)")`(第 4 項)
   第 5 項 `_bound_tests_for_diff` 會把這個例外接成 `no-config`,判不過。第 3 項的設計只寫了「接住 `resolve_test_refs` 丟的 `ValueError`」,`_platform_test_index` 丟的例外沒人接,照字面實作就直接印出 Python 錯誤堆疊。
3. 如果實作者順手把 `default_platform` 這個鍵也刪掉,剩一個平台時 `load_platforms` 會改用剩下那個當預設。實測:沒寫前綴的 `[test:t_web_x]` 會被歸到 `('api', 't_web_x')`,本來屬於 web 的測試會拿到 api 的索引去找,判成「找不到」,不會附「平台 web 這次不驗」的原因。剩兩個以上平台時,則改丟「沒說預設是哪個」的 `ValueError`。
4. 不管走哪條路,api 這個能驗的平台都沒驗到,跟引句同一段承諾的「其他平台照驗」相反。要明訂:預設平台被拿掉時,不改 `default_platform`;沒寫前綴的測試名都當成「平台 <預設> 這次不驗」;第 3 項呼叫 `_platform_test_index(樹)` 也要包例外處理。或者乾脆規定預設平台驗不了就整次回 2,並寫進 S2。

## F3 這一版把「`load_platforms(樹)` 丟例外就回 2」改成只檢查 JSON 語法,語法對但內容不合法的設定會讓後面的步驟當掉
severity: major
blocking: 是
引句:「樹裡的設定讀得懂:樹裡的 `.lumos/config.json` 先自己用 JSON 讀一次,讀不懂回 2」
file: `scripts/lumos:4830`
file: `scripts/lumos:4852`
file: `scripts/lumos:38615`
1. r3-delta 第 99 行:舊稿是「`load_platforms(樹)` 讀得懂(丟例外就回 2)」,新稿只剩「先自己用 JSON 讀一次」。新稿說的理由(壞 JSON 不會丟例外,所以要自己先判)本身沒錯,但它把原本那條判斷整個換掉,沒有保留。
2. JSON 語法對、內容卻讓 `load_platforms` 丟例外的設定,現在都能通過先決條件。實測(`plat.py` 的 C 段、`cfgbad.py`):
   - 設了兩個平台卻沒寫 `default_platform` → `ValueError 設定了 2 個平台,但沒說預設是哪個`
   - profile 名稱寫錯 → `ValueError 設定檔 platforms['a'].profile 填了 'nosuch'`
   - 整份設定是 `[]` → `AttributeError 'list' object has no attribute 'get'`(`scripts/lumos:4830`)
   - 平台根寫成 `"root": null` → `TypeError unsupported operand type(s) for /: 'PosixPath' and 'NoneType'`(`scripts/lumos:4852`)
3. 這幾種設定都通過先決條件,接著:〈樹的準備〉要取每個平台的平台根,用 `load_platforms` 取就丟例外,自己讀 JSON 的話遇到 `[]` 也一樣當掉;第 3 項的 `_platform_test_index` 丟出去沒人接;第 4 項的 `_run_bound_tests` 只接 `ValueError`(`scripts/lumos:38615`),`AttributeError` 和 `TypeError` 會直接穿出共用函式。最後整支程式當掉印出錯誤堆疊,退出碼是 1,跟「驗了但不過」分不出來,而且不寫治理帳事件,`loop next` 會一直提醒。
4. 修法:把先決條件改回「先自己讀 JSON,讀不懂回 2;再呼叫 `load_platforms(樹)`,丟任何例外都回 2」,而且這一步要放在〈樹的準備〉拿掉平台之前。S2 加一個情境:「JSON 合法但兩個平台沒寫預設」。

## F4 平台根是 git 子模組時,樹裡會有一個空資料夾,「要是存在的資料夾」這條判不出它驗不了
severity: major
blocking: 是
引句:「每個平台的平台根取實際路徑後,要在樹的實際路徑底下、而且是存在的資料夾」
1. `git worktree add` 不會把子模組的內容抓下來,只會在子模組的位置留一個空資料夾。這個平台根在樹的實際路徑底下、也是存在的資料夾,所以照字面不會被拿掉。
2. 重現指令(在工作目錄下):建 `sub` repo(含 `test_a.py`)→ 在 `sm` 用 `git submodule add <sub> ios` 加成子模組 → `git -C sm worktree add --detach <暫存>/wt HEAD`。輸出 `樹裡 ios 是資料夾嗎: yes`、`內容: 0`。
3. 照字面:這個平台留著,紀錄裡寫到它的測試在第 3 項全部判「找不到」,而且不會附「這次不驗」的原因;第 5 項綁它的合約判 `dangling`,也就是紅。主工作目錄的子模組有內容,推送前那道閘在那裡照常是綠的。這正是這一版要修的「驗不了的平台讓整次判不過」那一類,只是換了形狀,沒修到。本機消費專案目前沒有用子模組(查過 `~/harness/*/.gitmodules`,一個都沒有),所以今天碰不到。
4. 修法:改用一條統一的規則,不只看「是不是存在的資料夾」:平台根在修正後的提交裡要是資料夾物件(`git ls-tree` 的模式是 040000),平台根是 `.` 的除外。子模組(160000)、符號連結(120000)、沒進版控的資料夾都歸進「這次不驗」。這條規則也可以換掉現在「實際路徑在不在樹底下」那段判斷,而且跟 `at` 欄位驗檔案模式的寫法一致。

## F5 派工單在手冊的第幾步寫 `base_commit`,文件前後講法不一
severity: minor
blocking: 否
引句:「手冊第 2 步寫派工單時一起寫」
file: `skills/lumos-code-loop/SKILL.md:34`
1. 〈修正紀錄〉說在「手冊第 2 步」寫。〈要同步的文件〉這一版改成「第 1 步(凍結材料時先提交,派工單寫 `base_commit`)」。〈實務隱患〉又說「手冊第 2 步寫『派工前先提交』」。
2. 手冊裡第 1 步是「凍結材料」,派工單是在第 2 步的最後一行「派工單落 `rN-dispatch.json`」寫出來的。所以〈要同步的文件〉那句要改回第 2 步。「先提交」放在第 1 步凍結材料的時候做沒問題,但寫 `base_commit` 要跟著派工單一起放在第 2 步。

## F6 預設連依賴資料夾之後,「跑的期間別的會談改檔不影響這次結果」這句不成立
severity: minor
blocking: 否
引句:「跑的期間別的會談改檔、提交都不影響這次結果」
1. 依賴資料夾預設連回主工作目錄。Node 多套件專案的其他套件、Python 可編輯安裝(`pip install -e`),在樹裡載到的是主工作目錄**當下**的檔案,〈依賴資料夾〉自己也承認這一點。
2. 「有沒提交的改動」那句警告只在開跑時檢查一次。跑的五分鐘裡,別的會談再改主工作目錄,這些專案的結果就會受影響。〈建樹〉那句話要加一個但書:「連了依賴資料夾的專案除外」。

## 逐節核對
- 前言、依據、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding。
- 〈名詞〉:已讀。「樹先取實際路徑」實測 git 本來就會把路徑轉成實際路徑,用 `/private/tmp/...` 去收 `/tmp/...` 建的樹,`worktree remove` 回 0,沒問題。「樹裡那份設定可以改寫」引出 F1、F2。
- 〈範圍〉:已讀,無 finding。
- 〈修正紀錄〉測試名格式(派工點名的③):`names.py` 實測,用「解析前擋 `]` 和 `,`,拆出平台後方法名過 `_KILL_METHOD_OK_RE`」的規則,結果是:多平台下 `web:t_x` 解析成 `(web,'t_x')`,過;單平台下整串 `web:t_x` 被擋,這跟推送前那道閘一致。`should return empty list` 過。帶反引號的版本被擋,因為 `discover_test_methods` 對 Kotlin 是拆掉反引號才存名字,紀錄也要寫拆掉後的名字,這跟推送前那道閘一致。`a]b`、`a,b` 在解析前就被擋。`a[b`、`t-x`、`web:t:x` 被白名單擋。`...` 跟 `.` 會過白名單,但第 3 項在索引裡找不到,最後還是判不過,不會放錯。無 finding。base_commit 的步驟編號見 F5。
- 〈fix-check〉先決條件:F3。清殘骸:「`worktree remove` 失敗就直接刪資料夾」這段,Python 的 `rmtree` 碰到符號連結是刪連結本身、不會進去刪主工作目錄的 `node_modules`,實測收樹之後主工作目錄的 `node_modules/.bin/jest` 還在。無 finding。
- 〈樹的準備〉:拿掉平台見 F1、F2、F4。依賴資料夾(派工點名的②):①本 repo 是單平台設定,repo 頂沒有 `node_modules`、`.venv`、`venv`,所以連依賴什麼都不做;在取過實際路徑的樹裡跑 `-k t_platform_index_consumers_drift_guard`,7.8 秒、3 passed。②最小 Node 專案(`--shared` clone pos-api,`node_modules` 連到本機已裝好的那份):樹建好後呼叫 `_lint_link_deps(主, 樹)`,在樹裡跑 `npx jest -t checkoutWorksDirectlyFromOpen`,回 0,`Tests: 115 skipped, 1 passed`,`_ran_evidence_check` 判 True,用的是樹裡的 `jest.config.cjs` 跟 ts-jest。跑得起來,沒有上網抓套件。F6 是這段順帶的措辭問題。
- 〈逐項驗〉第 1、2 項:已讀;`_loop_records`、`_disposal_round_groups` 的語意跟設計描述一致。第 3、4、5 項:F1、F2、F3。
- 〈記帳與跳過〉、〈共用函式〉、〈loop next〉、〈canary record〉、〈上線〉:已讀,無 finding(這幾節本版沒改,只核對了引用的函式和測試名都存在)。
- 〈條款〉S1–S12:S1 的格式情境跟③的實測一致;S2 缺 F1、F2、F3 的情境,已分別寫在各條的修法裡。
- 〈回退〉:已讀,無 finding。
- 〈實務隱患〉:〈跨 repo 或沒進版控的平台〉一段要把子模組也算進去(F4);〈要同步的文件〉見 F5。
- 〈審計修正紀錄〉:已讀;r2 那條寫的「驗不了的平台只拿掉那個」,F1、F2、F4 指出這個修法還沒修到的形狀。
- 交叉引用:`_LINT_NEW_STALE_SEC`、`_lint_new_clean_stale`、`_escape_reason_ok`、`_MANUAL_MIN_CHARS`、`_codeloop_record_valid_ex`、`_drift_jsonl_parse`、`_drift_m1_code_kind`、`_GOV_FIELD_TYPES`、`_KNOWN_GATES`、規格閘四支函式、`_roster_dispatch_entries`、`cmd_seat_check`、`_gate_event_or_warn`、四支點名的測試、七篇 Systems 節點、兩篇 Projects 節點,都查得到。

## 實務隱患鏡頭
- 路徑處理:有命中,F4(子模組)、F1(改寫設定之後解析路徑跟著變)。
- 設定與相容性:有命中,F2、F3。
- 並行與交易邊界:有命中但輕微,F6。樹本身是隔離的,但連了依賴資料夾就破了這個隔離。
- 跳脫與清洗:測試名用 `shlex.quote` 展開進指令,`]` 和 `,` 在解析前就擋掉,實測沒有洞。
- 巢狀與遞迴、名稱碰撞、效能與記憶體:這一版改的段落沒有新增這類行為。撞名的判法沿用規格閘,沒有新的 finding。
- 金流、對外送出、不可逆:無。不碰付款;依賴資料夾連好之後 Node 實測沒有上網抓套件;樹跟連結都在收樹時清掉,實測主工作目錄的依賴沒被刪。

最高等級:major,blocking 共 4 條
