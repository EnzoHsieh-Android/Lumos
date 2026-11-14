severity: major

## z1 每點新建一棵工作樹、基準重跑一遍,50 點的總耗時與磁碟放大 50 倍以上
severity: major
blocking: 是——照字面實作,Gradle 基準 2 分鐘時,首次推送的補跑要幾小時,而且 spec 沒有降成本的辦法。

- spec 段落:〈用詞〉殺掉判定、〈範圍〉2 共用、〈實務隱患〉第一條、RETIRE-IF ②。
- 引句:「一個選擇點只呼叫一次 `cmd_guard_kill`,把它全部守的測試當 `recipes_override` 一次丟進去(同一支測試指令的基準只跑一次)」
- 「基準只跑一次」只在單一點的呼叫之內成立。
  - `cmd_guard_kill` 每次呼叫都新建隔離工作樹,`_isolated_worktree` 裡是 `git worktree add --detach`,結束時 `worktree remove --force`。
  - `baselines = {}` 是呼叫內的區域變數。
  - 檔案:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28026`、`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28046`
  - 所以 50 個點就是 50 次基準。
- 基準快取的 key 是展開後的測試指令 `cmd`。
  - Android 的 `run_cmd` 通常帶 `{method}`(例:`--tests {method}`)。
  - 每支守的測試各有一條 `cmd`,所以每點基準 = T 次。
  - spec 預期值表 S4 的「基準只跑一次」只在 `run_cmd` 不帶 `{method}`(整套跑)時才成立。
- 每棵工作樹都是新的,沒有 `build/` 和 `<樹>/.gradle`。
  - 每點都付一次冷編譯(Gradle daemon 與 `~/.gradle` 快取還在,但專案層沒有)。
  - 「基準 2 分鐘」是熱的數字,這裡會更慢。
- 數字例(輸入 → 預期)。
  - 50 點、T=1、基準 2 分鐘、壞法跑 ≥2 分鐘,約 200 分鐘。
  - T=3 約 10 小時。
  - RETIRE-IF ② 的十分鐘上限,第一次大分支就超 20 倍。
- 磁碟與檔案事件:Android 工作樹連同 `build/` 約 1 到 3GB,每點建了就刪,峰值只有一棵。
  - 但總寫入量約 50×GB 的檔案大量進出。
  - 這正是全域 CLAUDE.md 記的 fseventsd 漲到 11GB 的那一類負載,spec 沒提。
- 現成的解法已在 `cmd_guard_kill` 裡:同一次呼叫、同一棵工作樹內可跑多條配方,用 `mstate` 管還原與修改時間,基準按 `cmd` 共用。
  - spec 卻把「一次呼叫」的粒度定在單點,這是最貴的粒度。
- 建議:
  - 同一平台、同一個 HEAD 的所有點,放進一次 `cmd_guard_kill` 的 `recipes_override`,基準每個 `cmd` 只跑一次;或
  - 在 spec 寫明跨點基準快取(key 為 HEAD、`cmd`、平台)。
- 另補一條:RETIRE-IF ② 寫的是「每次推送前要補跑的選擇點中位數」,但推送閘不跑殺傷力。
  - 這個量只能從 `choice-kill` 的耗時統計取,措辭要對齊。

## z2 基準本身就紅或逾時時,每個點都重付一次最長 600 秒
severity: major
blocking: 是——照字面實作,壞掉的基準會被 N 個點各付一次,失敗模式的成本最高、卻最不需要。

- spec 段落:S6「假平台:基準就紅 → no_result(abort)、rc 2」、〈範圍〉2 rc 取最大。
- 基準的逾時上限是 `max(600.0, floor)`。
  - 檔案:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28047`
  - 逾時或 rc≠0 時,該點得到 `abort`,下一個點又新建工作樹、再跑一次同樣的基準。
- 同一個 HEAD、同一條測試指令,基準結果是確定的。
  - 輸入:50 點、基準因測試環境壞掉每次逾時 → 預期是跑完第一點就停。
  - 字面實作是 50×10 分鐘 = 約 8.3 小時,然後 50 筆 `no_result` 寫進帳。
- 建議:
  - 某平台、某 `cmd` 的基準 abort 時,當輪對這個 `cmd` 的所有後續點直接記同一個原因、不再重跑;
  - 或整輪 rc 2 就停。

## z3 一點的全部守的測試都跑,殺掉後不停
severity: minor
blocking: 否——結果正確,只是白花 T 倍的時間。

- spec 段落:〈用詞〉殺掉判定、S4。
- 判定規則是「任有一支 killed 且 weak 為否 → killed,killing_test 取條款順序第一支」。
  - 這個結果等同於「按條款順序跑、第一支強 killed 就停」。
- 但 `cmd_guard_kill` 沒有提早結束的路徑,`recipes_override` 的每一條都會跑(基準加壞法)。
  - 通常大多數點是 killed(spec 引的 Google 數字也是如此),T 支測試全跑是純浪費。
- 建議:
  - 按條款順序逐支呼叫,第一個強 killed 就停;或
  - 在 spec 明寫 `cmd_guard_kill` 要加「第一個強 killed 就停」的選用參數。
- 取捨:逐支呼叫和 z1 的合併呼叫互相牽制,spec 要選定一個。

## z4 推送閘的時間預算與逾時結果沒寫,而且擋下後的補救辦法對不上
severity: major
blocking: 是——超時或讀不到時是放行還是擋,字面實作沒有答案;「治理帳讀不到 → 擋」又會讓補救指令無效。

- spec 段落:〈範圍〉4「讀哪一版」、〈實務隱患〉倒數第二條「大分支(改 5000 行)要量,實作時寫進報告」。
- 現有的先例有預算:`_KT_SIT_BUDGET = 30.0`,超過就「算不出來」。
  - 檔案:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:39986`
  - `_kt_sit_read_many` 會 raise `_KtSitUnverifiable`(單支檔超過 4MB 或讀不到)與 `_KtSitOverBudget`。
  - 檔案:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:40114`
- spec 要重用這支函式,卻沒寫:
  - 選擇點掃描的 deadline 取多少;
  - 兩種例外在這道閘是放行、擋、還是只提醒。
  - 現有情境題那一道是「提醒不擋」,而這道閘的基調是「沒紀錄就擋」。
- 輸入:改 5000 行、其中有一支超過 4MB 的 `.kt`(例如產生碼),預期要有明確結果。
  - spec 沒給,實作者隨手選,而且那個點也無法定位、無法 `--judge`。
- 「治理帳在 B 讀不到 → 擋」把兩件事混在一起。
  - `_gov_rows_at` 回 `missing` 與 `unreadable`。
  - `unreadable` 包含 `git show` 逾時(`_residual_blob_at` 預設 `timeout=60`)。
  - 檔案:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:64917`、`/Users/enzo/harness/lumos-near-miss/scripts/lumos:65061`
  - 5 萬行的帳讀逾時就擋。
  - 訊息指向的 `lumos choice-kill` 是補不了這個的,`--judge` 也不行。
- 讀帳的成本:`_gov_rows_at` 整個 blob 進記憶體,逐行做位元組子字串篩選。
  - 5 萬行約數十 MB,可以接受。
  - 但 spec 的快取只說「(提交, 檔)」,沒說 `choice-kill` 跑 50 點時是否每點重讀帳。
  - 只要寫「開始讀一次、新增的列併進記憶體」就夠。
- 建議:
  - 寫明閘的 deadline 與超時、超限、讀不到各自的結果(擋或放行,配一句訊息);
  - 把 `unreadable` 和 `missing` 分開處理。

## z5 中斷與錯誤路徑:點與點之間沒有訊號處理,第二個訊號會留下整棵工作樹
severity: minor
blocking: 否——spec 已有兩段式收尾可沿用,缺的是迴圈層的幾句規定。

- spec 段落:〈範圍〉2 共用(「保留 Ctrl-C/SIGTERM/SIGHUP 兩段式收尾」)、記(「中斷 → 已跑完的點照記、跑到一半的那點不記、rc 2」)。
- 處理器裝在 `_situation_rule_kill` 的 `with _situation_rule_signals()` 裡,一次呼叫一裝一卸。
  - 檔案:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:76076`
  - 若 spec 的「改成只回 (列, 狀態)」把處理器維持在這支函式內,點與點之間(寫帳、算下一點)沒有處理器。
  - 預設的 SIGTERM 會直接終止程序。
  - Ctrl-C 變成沒收尾的 `KeyboardInterrupt`,可能發生在追加帳的那一下。
- spec 只說狀態 `interrupted`,沒寫收到後要停整個迴圈。
  - 字面實作可能繼續跑下一點。
- 第二個訊號走 `_situation_rule_force_exit`,工作樹留給清殘骸。
  - 清殘骸的時限是 `_LINT_NEW_STALE_SEC = 86400`(一天)。
  - 檔案:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:42800`
  - 每次強殺留一棵 1 到 3GB 的 Android 工作樹,加上 `git worktree` 登記,連續中斷會累積幾 GB。
- `_kill_run` 用 `start_new_session=True` 開 shell。
  - 收的是程序群組。
  - `./gradlew` 啟動的 daemon 若脫離群組,逾時或中斷後還會在被刪的樹上繼續建置。
  - 下一點又開新的 daemon,這是現有的盡力而為邊界。
  - 50 點的迴圈把這個邊界放大,spec 沒提 `--no-daemon` 之類的處理。
- 建議:
  - 處理器包住整個迴圈;
  - 第一個訊號收到後寫明停整輪、rc 2;
  - 寫明強殺的殘骸處理,並在最終訊息列出殘留路徑。

## z6 `cmd_guard_kill` 只吃單一 node,而守的測試取自多份計劃;帳要先提交,spec 沒寫
severity: minor
blocking: 否——都是接線細節,不影響設計方向。

- spec 段落:〈用詞〉守的測試、〈範圍〉2 記、〈範圍〉4 讀哪一版、〈範圍〉5。
- `cmd_guard_kill(env, node, …)` 第一個參數是單一筆記。
  - 檔案:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27902`
  - 〈用詞〉說守的測試取範圍碰到的「所有進行中計劃」。
  - 選哪個 `node` 傳進去、kill-log 的 `node` 欄記哪份計劃,spec 沒寫。
- 殺傷力記帳是在整次呼叫結束後才寫 kill-log,中斷的點不寫。
  - 檔案:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28155`
  - 這和 spec「跑到一半的不記」一致,已核對。
  - 但每個 choice-kill 的點都會往 `docs/.kill-log.jsonl` 追加(帶 `tail`、`fail_excerpt`)。
  - 它在版控裡,spec 沒提大小成長。
- 推送閘讀的是 B 的版控治理帳(`_gov_rows_at(B)`)。
  - 治理帳有「例行紀錄分流」白名單,不在白名單的事件進版控帳。
  - spec 沒說 `choice-kill` 的五種事件進哪一本。
  - 若進版控帳,作者每次 `choice-kill` 之後必須先提交帳才推,否則閘讀 B 找不到紀錄。
  - 這點要寫進〈範圍〉6 的手冊補充。
- 每次擋下都記一筆 `blocked` 進帳,帳會因為重試而膨脹。可沿用現有「同內容不重記」的做法。

## 其他已核對的節
- 交叉引用:S1 到 S20 都有定義,每條也都有預期值表列。
  - 〈範圍〉3 的「來源互斥」、〈實務隱患〉的「紀錄過期」存在。
  - 唯一偏差:S15 的預期值表來源寫「〈範圍〉5 RETIRE-IF」,但 RETIRE-IF 在檔頭,〈範圍〉5 裡沒有。不影響實作。
- 程式碼假設查證存在:`_isolated_worktree`、`_kt_sit_read_many`、`_gov_rows_at`、`_situation_rule_kill`、`_backing_kill_rows`、`_codeloop_disp_range`、`_waive_origin_tty`。
- 小偏差:`_kt_catalog_missing` 實際上除了型錄不存在,也把「`_KT_PACK_CHECK_REL` 規則包自檢檔不在」判成缺檔。
  - 檔案:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:40087`(約略位置,以 grep 為準)
  - spec 〈用詞〉寫「型錄不存在」,範圍較窄,要對齊。
- 掃描本身的成本:選擇點掃描是文字比對加 `_strip_c_comments`,每檔上限 4MB,約線性。
  - 唯一性檢查是每點對全檔做 `count`,5000 行改動估計幾百點,是百分之一秒到秒級,不構成瓶頸。

## 設計審固定席(`guard-kill`)逐條判
- INVARIANT「guard kill rc 優先序:survived→rc1、drifted/abort/error→rc2」:不影響。
  - spec 只新增選用參數 `source`,`choice-kill` 從 `result_out` 讀列、自己判 killed、survived、no_result。
  - 不改 `cmd_guard_kill` 的 rc 計算。
- INVARIANT「`--json` 成功時 stdout 恰一行 JSON」:不影響。
  - `choice-kill` 呼叫時不帶 `as_json`;`source` 只是記帳欄位,不新增 stdout 輸出。
  - 實作時要注意 `source` 不能讓 `--json` 路徑多印診斷。
- 唯一要留意:`_backing_kill_rows` 改成「`source` 非空就跳過」,現行是只認 `_SITUATION_RULE_SOURCE`。
  - 這樣會連手寫進帳、帶別的 `source` 的列一起跳過,應是預期,但要在 Systems/guard-kill 的口徑裡寫明。

最嚴重:major;blocking 共 3 條
