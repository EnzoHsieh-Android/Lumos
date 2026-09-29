severity: major

架構對齊審查(只看「跟既有做法一不一致」)。對照碼在 clone-ns 的 scripts/lumos。三問結論先列:
- 問1 分層與依賴方向:新指令走 cmd_* → 私有 helper 的既有分層(`cmd_drift_ack` scripts/lumos:27101 → `_jsonl_append_verified` :8511、`_vault_write_lock` :14714 一帶),沒有看到跨層直呼;唯一要注意的是 F2(E5 內聯迴圈與新函式各自組一套判定)。
- 問2 命名與錯誤處理:常數名 `_DRIFT_FIXES`、id 前綴 `DFIX-` 跟 `_DRIFT_ACKS`(:25983)、`DACK-`(:27127)一致;治理事件與例外處理有落差,見 F1、F4。
- 問3 第二種做法:見 F2(第二份 REVISIT 行判定)、F3(狀態表仍有兩份手寫)、F7(帳上存整篇原文)。
- 問4 落點:見 F6。

## F1 新閘名 drift-fix 沒登記進 _KNOWN_GATES,「記一筆治理事件」照字面實作會靜默不寫
severity: major
blocking: 是 — 不改,實作者照字面寫完,治理事件根本沒落帳、gov 統計看不到,還會讓漂移釘測試翻紅
引句:「成功後記一筆治理事件(閘名 `drift-fix`,同 `drift ack` 記事件的方式)」
file: `scripts/lumos:1154`
1. `drift ack` 記事件用的是既有閘名 `drift-check`(kind=acked,scripts/lumos:27141),不是新閘名;spec 說「同 drift ack 的方式」卻換了新閘名 `drift-fix`,兩句對不上。
2. 通用落帳器 `_gate_event` 在寫之前檢查 `gate not in _KNOWN_GATES`,不在就不寫、只在 stderr 喊一句(:1154-1158);名單在 :6904,`drift-check` 是 2026-09-28 為存量漂移守衛補進去的(:6924)。
3. spec 的〈同步改的筆記與文件〉、〈做法〉都沒提要改 `_KNOWN_GATES`。照字面做:呼叫走 `_gate_event_or_warn`,結果是每次 fix 都印「不在 _KNOWN_GATES 名單上——沒有寫」,事件從沒落帳。
4. 修法二選一要在 spec 寫死:沿用 `drift-check` 加新 kind(如 `fixed`,跟 ack 的 `acked` 同閘),或把 `drift-fix` 明列進 `_KNOWN_GATES` 並註記日期(鄰居都是這樣註記)。

## F2 「跟 E5 同一套判定」只靠散文,新函式 _issue_close_revisits 會是第二份 REVISIT 行判定
severity: major
blocking: 是 — 同一件事(哪些行算回頭條件)兩處各寫一份、沒有機械守一致,之後 E5 改判定 set 側會靜默漂開
引句:「用跟 E5 同一套判定(`_search_visible_lines` 剝程式碼區,餵 `_strip_inline_markup` 之後的 `_revisit_split`」
file: `scripts/lumos:2205`
1. E5 的判定是內聯在 doctor 大函式裡的迴圈(:2205-2245:`_search_visible_lines` → `_strip_inline_markup` → `_revisit_split` → 日期解析),沒有可呼叫的 helper。
2. spec 要新寫 `_issue_close_revisits`,把這三個原語再組一遍;§5 的 E5 標記也要在 E5 迴圈裡另加「來源是已結案 Issue」判斷。結果:同一套「哪些行算回頭條件」存在 E5 迴圈、`_issue_close_revisits`、`_ns_revisit_violations`(:24851)、筆記內容審(:25398)幾處各自組裝。
3. 專案既有的收斂做法是把判定抽成單一支讓各處共用(`_revisit_split` 就是這樣來的,:26331 的註解寫「E5、第一層、第二層共用這一支」)。本 spec 只收斂到 `_revisit_split` 這一層,「逐行迭代與剝碼」這一層沒有收斂,也沒有一致性測試;[S7] 只測 set 側,[S6] 只測 E5 側,沒有一條釘「兩邊對同一份文字列出同一批行」。
4. 修法:抽一支「一篇筆記 → [(行號, 種類, 剩餘文字)]」供 E5 迴圈與 `_issue_close_revisits` 共用,或至少補一條同輸入兩側輸出一致的條款。

## F3 「不另寫一份」的狀態表位置與現況不符,而且還有一份手寫表沒被收
severity: minor
blocking: 否 — 結構方向對(抽常數共用),只是位置說錯、漏收一份既有重複,實作者看程式就能修
引句:「把 `cmd_lint` 裡的類型狀態表抽成模組層常數(`_TYPE_STATUSES`),lint 與 fix 共用,不另寫一份」
file: `scripts/lumos:5244`
1. 這張表叫 `_STATUS_ENUM`,是 `_lint_collect`(:5173)裡的區域變數,不在 `cmd_lint`(:5136);且只在 `_created_e >= _ENUM_CUTOFF` 的分支內定義。抽到模組層時要連 cutoff 判斷一起想,不是搬一行。
2. 同一件事另有一份手寫字串表:`_nl_rule_status` 裡的 `allowed = {"verification": "pass/stale/superseded/pending/abandoned", ...}`(:5493)。spec 說抽出來後「不另寫一份」,但這份既有重複沒列進要收的範圍,抽完仍是兩份(常數 + 字串表),且沒有機械守一致。⚠ 鄰居本身已經有兩份,專案沒有單一源可對;建議一併把 :5493 改成由常數組字串。

## F4 自驗失敗「檔案已經落盤」的前提與程式現況相反,錯誤處理也沒對齊鄰居的例外接法
severity: minor
blocking: 否 — 結構(鎖內、原子寫、失敗回 2)對,只是前提描述錯、例外接法沒寫,不會做出壞系統
引句:「自驗失敗時檔案已經落盤,不能只報錯」
file: `scripts/lumos:14695`
1. `atomic_write_verify` 是「解析新內容 → `expected_check` → lint 無新指紋 → 才 `_write_lf`」,任何一步失敗都 `raise RuntimeError`,此時檔案還沒寫(:14695-14710)。spec 第 5 步說自驗失敗檔案已落盤,跟程式相反。
2. 鄰居的做法:例外由呼叫端接住印「擋下:…」回 2(`cmd_set` 在 main 分派處 `except (ValueError, RuntimeError)`,:37048 一帶;`_guard_settle_record` 在 :12313 附近局部接)。spec 的 drift fix 分派沒寫要接 `ValueError/RuntimeError/OSError`(`_write_lf` 也可能丟 OSError),照字面實作會讓例外直接噴堆疊。
3. spec 加的「寫完從磁碟重讀、確認發現已不在、還在就寫回改前原文」是專案裡沒有先例的補救路(全檔搜「還原/寫回原」找不到筆記寫入的先例)。它處理的是「改後內容寫進去了但發現沒消掉」,這件事合理,但應改寫成正確前提(改後內容通過 fm 自驗、卻沒消掉發現),並明寫例外接法。⚠ 鄰居沒有先例可對。

## F5 鎖內重判沒用既有的 only= 參數
severity: minor
blocking: 否 — 只是慢一點,結果不會錯
引句:「再用 `_drift_state_findings` 重判,確認指定的行現在確實是這一種發現」
file: `scripts/lumos:26078`
1. `_drift_state_findings(env, only=None)` 已提供 `only=` 路徑集合,docstring 寫明「要算的路徑集合」;spec 的第 1 節第 3 步、第 6 節 `drift ack` 都沒用它,照字面會在鎖內對全圖譜每篇跑一遍。
2. 這個函式仍會先 `build_typed_index(env)` 全圖(:26083),`only` 只省逐篇檢查,不解決整體耗時;而 spec 自己把「鎖 30 秒被接手」當設計理由(第 1 節第 1 步)。要嘛用 `only={rel}` 對齊既有介面,要嘛在 spec 講明為什麼不用。

## F6 lands_in 少列了實際會改到的另外幾處的家
severity: minor
blocking: 否 — 文件落點問題,不影響行為;實作時 pre-commit 的「每支檔有家/改 code 要動圖譜」會再提醒
引句:「  - Systems/lumos-cli-write」
1. 會動到的碼與家:`_KNOWN_GATES`(若採 F1 的登記做法)、`_STATUS_ENUM` 抽常數(lint 一側)、doctor E5、`_BOOKKEEPING_FILES` 加一項。這幾處 spec 只在〈同步改的筆記〉列出 4 篇 Systems,lands_in 只有 3 篇,且 `_BOOKKEEPING_FILES` 的歷史記在 `Systems/pitfalls-code-loop`(該篇有專段記白名單沿革)。
2. 對照先例:上一次加 `drift-acks.jsonl` 進白名單是記在存量漂移守衛那篇,不是 pitfalls-code-loop(該篇 grep 不到 drift)。所以「白名單那一項寫進存量漂移守衛」有先例,這一點對齊;剩下的 lint 狀態表、E5 標記要說明落在哪一篇。⚠ 判不準 E5 的家:E5 只在 `Systems/存量漂移守衛` 與 `Systems/筆記內容閘` 被提到,專案沒有一篇專管 doctor E5 的節點。

## F7 修復帳存「改前整篇原文」是專案帳檔沒有的第二種可逆做法
severity: minor
blocking: 否 — 有明確理由(不靠 git 也找得回來)且回退節有交代,只是成為新做法,接手者要知道
引句:「`before`(改前整篇原文)、`after_sha256`(改後整篇的指紋)」
file: `scripts/lumos:27127`
1. 鄰居 `drift-acks.jsonl` 每筆只存 `text`(單行)、`reason`、`line` 等小欄位(:27127-27128);治理帳、簽核帳同樣不存筆記本體。改筆記類指令(`cmd_set`、settle)的可逆靠 git,沒有先例把整篇筆記塞進帳。
2. 影響:每筆最多一整篇筆記進版控的帳檔,帳會隨修復筆數快速變大;spec 的 RETIRE-IF 只量筆數,沒量帳檔大小。回退節寫了「能逐筆寫回」,但 scope 沒有對應的還原指令,只有人工照帳寫回。⚠ 專案沒有既有的「帳內存快照」可對照,判不準是否該引入。

## 已看,無 finding
- 〈做法〉第 1 節分派:「`drift` 子命令現在不是 scan 就當 ack」屬實(scripts/lumos:37029-37033;check、exam 另在 :36761 更早分派),要拆三支的說法對。
引句:「加 fix 要改成明確分三支,不然 fix 會被當成 ack 執行」
- 〈做法〉第 2、3 節 c1 與 settle 共用同一支 `_guard_settle_rewrite`(:12086):與現況一致,呼叫者確實只有 `_guard_settle_record`(:12303)。
引句:「`_guard_settle_rewrite` 改整篇(同一篇的四種預告句是一組」
- 〈做法〉第 4 節 c4:`_set_conditions_locked`(:14863)確實自讀自寫並印「✓ set」,拆 `_conditions_rewrite` 共用符合專案「同一支寫入邏輯共用」的既有做法。
引句:「拆出「給舊的行、回新的行」那一段(`_conditions_rewrite`),set 與 fix 共用」
- 〈做法〉第 6 節:`_drift_split_acked`(:27079)現行是集合聯集(任一筆對上就算),spec 改成最新一筆為準是刻意的行為變更,且已說明不借 `_drift_old_reason`(:27089,其邏輯確為「原路徑還在就跳過」)。
引句:「不借 `_drift_old_reason`(它為了分辨改名,原路徑還在就跳過)」
- 〈條款〉〈回退〉〈實務隱患〉〈誠實界線〉:已讀,與本席只管的一致性無關。

不對齊共 7 條;要擋的共 2 條
