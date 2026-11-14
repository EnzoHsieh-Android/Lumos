severity: major

## z1 推送前讀帳的次數沒有規定,照字面逐條讀會把治理帳讀上百次
severity: major
blocking: 是——〈範圍〉3 的判法是「每個非『無』的 `[near:]` 要有一筆有效紀錄」,沒寫整輪只讀一次。照字面逐條、逐計劃讀帳,會做出上一輪審查剛修掉的那種效能問題。

- 位置:〈範圍〉3、〈用詞〉有效紀錄。
- 引句:「裡 gate 與 kind 都是 `clause-kill` 的一筆」
- 本席重點的試算:10 份計劃、每份 10 條條款、每條 2 個 near,共 200 個 near。
- `_gov_vc_gate_events` 每呼叫一次,就把整本治理帳 `limit=None` 全讀進記憶體再切行。
- 帳 5 萬行時,逐 near 讀會做 200 次整本讀取、200 次切行,記憶體峰值各約 50MB(`_ledger_lines_having` 的註解記錄 12 萬行約 50MB)。
- 現有先例是預期值表那圈把帳讀一次,存進 `ctx["exp_gov"]`:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:14591`。
- `_expected_requirement` 的註解寫明,這是為了修「每份計劃都整本重讀一次治理帳」(代碼審 r1 資源 z2)。
- 推送閘本來就已經讀兩次:`ctx["sg_gov"]` 讀 `spec-gate`(`:17243` 一帶),`ctx["exp_gov"]` 讀 `signoff` 加 `situation-rule`。
- 直接加一個 `clause-kill` 專用的讀法,就是第三次整本讀。
- 具體例:輸入是 200 個 near、帳 5 萬行;預期是整輪推送前只讀一次帳,建一張 `(計劃, clause_id, near_index)` 對最新一筆紀錄的索引。
- 建議:spec 明寫「把 `clause-kill` 併進 `_expected_gov` 的閘名 tuple、共用 `ctx`」,並加一條呼叫次數的測試。`_spec_gate_ruled_events` 和 `_expected_push_one` 的 hits 都已經按 kind 過濾,所以併入不會影響它們。

## z2 近似錯誤的檢查會套到「連結候選」計劃,不相干的推送被擋,要補的 Gradle 跑數沒有上限
severity: major
blocking: 是——〈範圍〉3 說「接在 `_spec_gate_push_check` 現有的計劃清單上」。照字面做,會連作者自己沒碰的計劃一起擋。

- 位置:〈範圍〉3。
- 引句:「接在 `_spec_gate_push_check` 現有的計劃清單上」
- `_spec_gate_push_candidates` 的清單包含 doing 的計劃,只要它的 `lands_in`、`related` 或正文連到被碰到的 Systems 節點或被改程式檔的家:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:16535`。
- 本計劃自己的 `lands_in` 就是 `Systems/規格閘` 和 `Systems/guard-kill`,而 `Systems/規格閘` 管的是 `scripts/lumos`。任何人推一個動 `scripts/lumos` 的提交,都會把所有連到這兩個家的風險高 doing 計劃拉進來。
- 對照 `_spec_gate_push_sources`:它刻意只看範圍裡被改到的計劃,註解寫「別人的計劃不擋你」(`:17340` 一帶)。
- 具體例:輸入是 10 份風險高計劃、各 10 條條款、各 2 個 near,帳上都沒紀錄。
- 預期是只擋推送範圍自己的計劃。
- 照字面做,這 200 個 near 都會被列為缺紀錄,每個要跑一次 Android 的 Gradle 殺傷力。以十幾分鐘一次算,約 30 小時才能解除擋下。
- 建議:spec 限定近似錯誤檢查只看 `_spec_gate_touched_plans` 這一圈,或只看 `_live` 的計劃。同時說明 done 的計劃是否算。`_expected_push_one` 的 `_live` 過濾目前是 doing,或這次推送改到本檔的 done。
- 補充:做不到的話,要有一條逃生口,例如被連結候選拉進來的計劃只提醒、不擋。

## z3 clause-kill 的中斷與錯誤路徑沒規定收尾,沿用人裁那套的承諾沒寫成條款
severity: major
blocking: 是——spec 只寫「沿用 guard kill 的隔離工作樹」,S1–S10 沒有任何一條綁中斷收尾。照字面做的實作,收尾會比人裁那套少一半。

- 位置:〈實務隱患〉併發與交易那行、〈範圍〉2、〈驗收條款〉。
- 引句:「單人單機依序操作,沿用 guard kill 的隔離工作樹」
- 已查證的現況:`_isolated_worktree` 的 finally 只在例外或 `KeyboardInterrupt` 走得到。
- SIGTERM 和 SIGHUP 預設直接結束程序。工作樹放在 `/tmp/lumos-kill-*`,Gradle 的 build 目錄可能有數 GB,而且 `git worktree` 的登記還在。這些都留給「超過一天」才清:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27594`、`:42613`。
- 殘骸只在下一次帶 `recipes_override` 的 guard kill 開跑前才清,clause-kill 剛好有這個條件。
- 人裁分支另有 `_situation_rule_signals`(兩段式:第一個訊號走 finally 收尾,第二個訊號 `os._exit` 並收掉測試程序群組):`/Users/enzo/harness/lumos-srl-android/scripts/lumos:75946`、`:75970`。
- 它是 spec 所稱的「前置」才有的東西。clause-kill 不寫計劃、不拿寫入鎖,只要照那套把 `st.defer` 保持為假就能用。spec 沒說要套,也沒說中斷時的 rc 與帳。
- 具體例:clause-kill 跑 Gradle 時收到 SIGTERM(對話工具逾時、關終端)。預期是 rc 2、工作樹與暫存資料夾移除、治理帳不寫。spec 沒有規定,實作者很可能漏掉。
- 建議:加一條 S 條款,綁 SIGTERM 後工作樹與暫存資料夾被收掉、治理帳零事件、rc 2。再加一句「套用 `_situation_rule_signals`」。
- 誠實邊界:Gradle daemon 自己另開 session,收不到。人裁那套已有同樣的邊界,spec 應照抄那一句。

## z4 `<推送提交>` 沒有定義,也沒說 `git show` 只讀幾次
severity: major
blocking: 是——spec 要讀「被推送版本」的檔,卻沒說那是哪個提交。照字面實作要自己發明規則。

- 位置:〈用詞〉有效紀錄、〈範圍〉3。
- 引句:「`old` 在被推送版本(`git show <推送提交>:<file>`)的整份檔恰好出現一次」
- `_spec_gate_push_check(env, git_range, repo)` 拿到的是範圍字串,可能是 `a..b` 或三點。`:17387` 一帶。
- pre-push 是逐 ref 迴圈,被推的 sha 不一定是 HEAD。作者的工作目錄也可能不是被推版本。
- spec 沒說怎麼從範圍取右端點,也沒說取不到時怎麼辦。同一個函式對無法解析的範圍是放行,這邊卻是 fail-closed 的讀帳。
- 資源面:200 個 near 若各 `git show` 一次,會對同一支檔(例如同一個 ViewModel)反覆取 blob 並計數。
- 建議:整輪按 `(提交, file)` 快取檔案內容,只讀一次。再加一個上限:blob 超過數 MB 時當讀不到而擋,免得一個巨大的生成檔把記憶體吃光。spec 還要寫明右端點怎麼取,以及取不到時的行為。
- 具體例:兩個 near 都指向 `SearchViewModel.kt`。預期是 `git show` 只跑一次。

## z5 計劃檔有未提交改動時,殺傷力一律算弱證據,「殺得掉」永遠成立不了
severity: minor
blocking: 否——只是訊息誤導,補提交就能解;spec 沒寫但不會讓實作做錯。

- 位置:〈範圍〉2 驗證的「工作目錄除簿記檔外乾淨」、〈用詞〉殺得掉。
- `cmd_guard_kill` 在節點(也就是這份計劃)有未提交改動時,把 `weak` 設成 true:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27832`、`:28009`。
- 〈用詞〉要求「沒有弱證據」。所以計劃檔是 dirty 的話,無論測試有沒有紅都不算殺得掉。
- 這和〈範圍〉2 的「簿記檔」是否含計劃檔互相牽動。spec 沒定義簿記檔,若計劃檔算簿記而被放行,結果會是 rc 1,卻寫著「補測試讓它紅」。
- 具體例:剛在計劃加了 `[near:]` 還沒提交就跑 clause-kill。預期是 rc 2,並說「先提交計劃」。
- 建議:驗證階段明確要求計劃檔乾淨,不乾淨 rc 2。

## z6 新閘名 `clause-kill` 沒登記進 `_KNOWN_GATES`,事件會被靜默丟掉
severity: minor
blocking: 否——S4 的測試一寫就紅,實作時會被抓到。

- 位置:〈用詞〉有效紀錄、〈範圍〉2 記帳。
- `_gate_event` 對不在 `_KNOWN_GATES` 名單的閘名,只印警告、不寫、回 False:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:1839`。
- 目前名單有 `situation-rule`(`:17760`),沒有 `clause-kill`。
- 沒登記的話,所有 clause-kill 的記帳都失敗,推送前那道會永遠擋。
- 建議:在〈範圍〉2 列出登記 `_KNOWN_GATES` 與 gov 統計名單,並補一條同步的漂移守衛(名單新增要有對應測試)。

## z7 治理帳事件含整段 `old`,沒有長度上限
severity: minor
blocking: 否——只影響帳長得多快。

- 位置:〈用詞〉有效紀錄欄位(`old`、`near_text`)。
- 現有政策是事件上限 4096 位元組,`_gate_event_fit` 靠丟清單欄位來守:`/Users/enzo/harness/lumos-near-miss/scripts/lumos:1862`。
- `old` 是字串,不是清單,`_gate_event_fit` 管不到。多行 Kotlin 原文可能很長,而且每次重跑(含 survived 的重跑)都追加一行,帳就長得快。
- 讀帳成本與行數、位元組數成正比,和 z1 疊加。
- 建議:`clause-kill` 在驗證階段規定 `old` 的長度上限(超過就 rc 2),或帳上改記雜湊加長度,推送版本再算雜湊比對。

## z8 每個 near 都開一個新工作樹、冷跑兩次 Gradle,沒有批次入口
severity: minor
blocking: 否——是成本問題,不影響正確性。

- 位置:〈範圍〉2、〈實務隱患〉。
- `cmd_guard_kill` 本身支援多條配方共用一個工作樹,且同一個測試指令的 baseline 只跑一次(`baselines[cmd]`)。
- 但 `lumos clause-kill` 一次只收一個 `--near`。同一份計劃的 20 個 near 就是 20 個冷工作樹、40 次 Gradle 建置,沒有 baseline 共用。
- 建議:允許同一條指令帶多個 `--near`,或 `--all <計劃>` 批次,共用一個工作樹與 baseline。寫成「建議放背景跑」也至少要在 spec 提一句。

## 其餘各節
- 已讀〈白話〉、〈舊否決比對〉、〈用詞〉、〈不做〉、〈依據來源〉、〈回退〉、〈天花板〉,對照程式後無 finding。
- 交叉引用核對過:〈用詞〉的「見範圍 2」、〈實務隱患〉的「天花板 2」、預期值表 S1–S10 對應〈驗收條款〉,目標都存在、說法一致。
- 「同一個條款同一個第幾個有多筆時取最新一筆」:以檔內順序為準,與 `_spec_gate_pick` 的規則一致,不需改。

## 固定席節點(Systems/guard-kill)逐條判
- ★INVARIANT★ rc 優先序(survived 是 rc 1,drifted/abort/error 是 rc 2):不影響。`source` 是新增的選用參數,只改寫帳欄位,不動 rc。
- 但實作 clause-kill 時,不能只看 `cmd_guard_kill` 的 rc。弱證據的 killed(`killed_unattributed`)在 `cmd_guard_kill` 是 rc 0,要靠 `result_out` 的 `weak` 欄位判定。spec 的「沒有弱證據」已隱含這點,但沒有明講。
- ★INVARIANT★ `--json` 模式成功時 stdout 恰一行 JSON:不影響。clause-kill 不傳 `as_json`,新增的 `source` 也不碰輸出。

最嚴重:major;blocking 共 4 條
