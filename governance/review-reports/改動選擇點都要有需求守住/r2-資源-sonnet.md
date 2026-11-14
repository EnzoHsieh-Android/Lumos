severity: major

## z1 批次只省了工作樹與基準,壞法 × 守的測試的 Gradle 次數仍是 N×T,沒有提前停、總量上限與預估
severity: major
blocking: 是——照字面實作,耗時隨「壞法數 × 守的測試數」線性增加且沒有上限,首次呼叫與每次補測試重跑都可能超過 RETIRE-IF ② 的十分鐘,而推送閘要求全部處置完才放行。

- spec 段落:〈用詞〉殺掉判定、〈範圍〉2、〈實務隱患〉第一條、天花板 3。
- 引句:「每個壞法對每支守的測試各一個臨時配方」
- 查證 `cmd_guard_kill`:
  - 迴圈對每條配方各開一次 `_kill_run`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28092`),沒有「這個壞法已被殺就跳過其餘測試」的路徑。
  - 基準按展開後的指令各跑一次(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28043`)。run_cmd 帶 `{method}` 時,T 支測試就是 T 次基準,不論壞法數。
  - 所以「一次呼叫」只省掉工作樹與重複基準,壞法 × 測試的次數一次都沒省。
- 論文對照:
  - 2.1 節寫明覆蓋率「determines the minimal set of tests that need to be run in an attempt to kill a mutant」,論文一個壞法只跑覆蓋那一行的最小測試集。
  - 2.3 節對每個壞法準備一份版本狀態、平行執行。
  - spec 引論文 2.3 的「一次產生、批次執行」,實際是單棵樹串行,且每個壞法跑全部守的測試。
  - 引句:「②論文只變異有覆蓋的行,我們沒有 Kotlin 覆蓋率,改成只用條款綁的測試、沒覆蓋的行存活時照樣要處置(天花板 3)」
  - 這條差異的後果只寫了存活語意,沒寫成本。
- 數字例:
  - 派工詞情境:10 個壞法 × 3 支測試 = 30 次壞法跑 + 3 次基準,Android 冷編譯。
  - 單次壞法跑含專案設定、增量編譯、測試,估 40–150 秒(我沒有 Android 專案可量,是估值)。
  - 合計約 25–90 分鐘。
  - spec 自己的實測是小型實驗副本「約 10 秒判 killed」,那是下界。
  - 這份計劃自己就有 20 條 `[test:]`。若它是守的測試,30 個壞法就是 600 次壞法跑。
  - `--only <定位>` 重跑單一壞法(補測試之後驗證用)仍要跑 T 次基準加 T 次壞法跑,而且新建一棵冷樹。
  - `situation-rule --point` 也是每次新建工作樹、冷編譯一次(只跑 1 個壞法 × 1 支測試)。
  - 14 個存活逐一處置,就是 14 次冷樹。
- 現有緩解:`--diff` 與 `--only` 能縮範圍。但 `--only` 縮的是壞法,不是測試。
- 建議(不改 rc 計算與 `--json` 單行合約):
  - `cmd_guard_kill` 的配方加選用的分組鍵,同組已有強 killed 就略過其餘配方。這樣批次與提前停不衝突,r1 z3 的「互相牽制」是假二選一。
  - `choice-kill` 加 `--test <名>` 窄化守的測試。
  - 每次呼叫加壞法數上限(例如 `--max-mutants`),剩下的下次再跑,並在開跑前印「N 壞法 × T 測試 ≈ 次數」。
  - `_CHOICE_SINCE` 等實測耗時寫進報告、確認可接受再生效,不要上線第一天就踩 RETIRE-IF ②。

## z2 中斷時「已有結果的壞法照記、印留下的工作樹路徑」照 spec 只加 `source` 參數做不到;r1 z5 沒折到位
severity: major
blocking: 是——字面實作要嘛中斷後所有結果全丟,要嘛「等這次殺傷力收尾」就是中斷不了。Claude Code 的對話指令上限最長 10 分鐘,逾時送 SIGTERM,長批次會「跑 10 分鐘 → 全丟 → 重跑」無限循環。

- spec 段落:〈範圍〉2「共用」「記」。
- 引句:「第一個訊號 → 等這次殺傷力收尾、已有結果的壞法照記、rc 2;第二個 → 強制結束,印留下的工作樹路徑」
- 引句:「`cmd_guard_kill` 多一個選用參數 `source`(不傳維持原行為)」
- 查證:
  - 結果只在呼叫內的區域變數 `results`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27958`)。
  - `result_out["rows"]` 與 kill-log 都在迴圈結束後才寫(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28149`、`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28156`)。
  - `_situation_rule_signals` 在 `defer` 為假時第一個訊號直接丟 `KeyboardInterrupt`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:76015` 起)。
  - `_kill_run` 收完程序群組後重新往上丟(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27794`)。
  - `cmd_guard_kill` 沒有任何 `except KeyboardInterrupt`,所以前面已跑完的壞法全部消失。現有 `_situation_rule_kill` 的訊息也明寫「計劃與治理帳都沒寫」(單一壞法時沒差)。
  - 另一種讀法:`defer=True` 時只記下訊號、不中斷。那「等這次殺傷力收尾」就是等剩下全部壞法跑完,第一個訊號失去中斷的意義。
- 「印留下的工作樹路徑」做不到:
  - `_situation_rule_force_exit` 印的是事先設好的固定字串,然後 `os._exit`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:75999`)。
  - 工作樹路徑是 `cmd_guard_kill` 內 `_isolated_worktree` 的區域值,外層拿不到。
  - 第二個訊號之後樹留給清殘骸。清殘骸的時限是 `_LINT_NEW_STALE_SEC = 86400`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:42800`),只在「下一次」帶 `sweep_repo` 的呼叫開頭才跑(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27727`)。
  - Android 一棵樹連 `build/` 估 1–3GB,每次強殺留一棵,正是全域規則記的暫存累積那一類。
- 驗收條款裡沒有任何 `[S]` 綁「中斷」「interrupted: true」,這整段沒有測試守。
- 建議:
  - `cmd_guard_kill` 加每條配方跑完的回呼(或檢查「要不要停」旗標),`choice-kill` 在回呼裡逐壞法寫治理帳。
  - `_isolated_worktree` 把活著的樹登記進模組層字典(仿 `_KILL_RUN_LIVE`),強制結束時能印出路徑或直接移除。
  - 補一條 `[S]` 條款綁中斷。
  - 新增的印出一律走標準錯誤,不破壞 `--json` 純度。

## z3 基準 abort 與 killed 的優先序自相矛盾,而且 `abort` 不在 no_result 清單裡
severity: major
blocking: 是——字面實作有兩個互斥的答案;而每個壞法都用到每支守的測試,一支測試的基準壞掉就等於整批作廢。

- spec 段落:〈用詞〉殺掉判定、S7。
- 引句:「某條測試指令的基準 abort → 這次呼叫裡用到它的壞法全部 no_result(原因 abort),不重跑」
- 查證:
  - 同一段前面的規則是任一支 `killed` 且非弱證據就判 killed。
  - 後面 no_result 的枚舉是 `killed_unattributed`、`timed_out_weak`、`weak`、`drifted`、`error`,沒有 `abort`。
  - `cmd_guard_kill` 確實產生 `verdict: "abort"`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28049`)。
- 輸入 → 預期:t_a 基準因環境壞紅、t_b 強 killed 某壞法。
  - 依第一條規則是 killed。
  - 依 abort 句,「用到它的壞法」= 每個壞法,全部 no_result。
  - 若 t_a 紅、t_b 綠(survived),枚舉沒有 `abort`,「其餘全部 survived」不成立,判定未定義。
- 後果:一支不相干、環境不穩的測試被列入守的測試,整批數小時的成果全成 no_result、rc 2,重跑再來一次。
- 建議:基準紅的測試從該呼叫的集合中排除並記「沒跑」。剩下的測試仍可判 killed。沒有強 killed 時才判 no_result(原因寫明哪支基準紅),並補一條 `[S]` 條款釘優先序。

## z4 帳的每筆大小:`test_blobs` 物件無法被 `_gate_event_fit` 縮短,而且每個壞法都重複存一份
severity: major
blocking: 是——spec 要求「保持在 `_gate_event_fit` 的上限內」,而它最大的欄位用 `_gate_event_fit` 照現況縮不了;若真把物件欄位傳給它,會直接丟例外。

- spec 段落:〈範圍〉2 記、〈範圍〉5 帳量。
- 引句:「實作量一筆的位元組數並保持在 `_gate_event_fit` 的上限內」
- 引句:「`test_blobs` 是物件」
- 實測(在我的暫存目錄對 repo 載入函式,沒改 repo):
  - 25 支守的測試、24 條條款、`reason` 帶 8 行失敗摘錄,一筆 `choice-kill` 事件 = 4877 位元組。
  - 其中 `test_blobs` 約 3.3KB,去掉後 1596 位元組。
  - 最小事件(1 條條款、無 reason)748 位元組。
  - 把 `test_blobs` 當 `list_key` 丟給 `_gate_event_fit`:丟 `TypeError: keys must be str, int, float, bool or None, not slice`。
  - 原因是 `_gate_event_fit_drop` 對字典做切片賦值(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:1921`)。
  - 不傳的話整行 >4096 也照寫(那個函式的註解就說寫入端沒有硬上限),spec 的「上限內」落空。
- 規模:同一次呼叫的 150 個壞法事件帶同一份 `test_blobs`,約 150 × 3.3KB ≈ 500KB 重複寫入。版控治理帳目前約 22.5MB,一次大呼叫就占約 2–3%。
- 讀帳成本不是問題:`_gov_rows_at` 讀 22MB 版控帳實測 0.09 秒、行程記憶體 127MB。
- 建議:
  - 每筆事件只放 `tests_sha`(守的測試集合的短雜湊);完整對照只在 `run` 那筆放一次(靠 `run_id` 連回)。
  - `reason` 的失敗摘錄限短。
  - 在 S 條款裡釘「單筆事件 ≤ 4096」,用 T=30 的輸入。

## z5 kill-log:choice-kill 每個「壞法 × 測試」一列進版控的殺傷力帳本,spec 沒提大小
severity: minor
blocking: 否——只是帳本快速變大,不影響判定。

- spec 段落:〈範圍〉5。
- 引句:「`gov` 讀殺傷力帳本那支 loader 照舊不分來源」
- 查證:
  - `cmd_guard_kill` 迴圈後對每筆結果寫一列 `docs/.kill-log.jsonl`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28156`)。
  - 這支檔進版控(`git ls-files` 有它),現況 138 列 67KB,平均約 490 位元組。
  - `abort`、`timed_out_weak`、`killed_unattributed` 的列另帶最多 800 字的 `fail_excerpt`。
  - 基準 abort 時,該測試 × 每個壞法每列都帶同一份摘錄。
- 數字:30 個配方約 15–40KB;150 壞法 × 10 測試約 1500 列,數百 KB 到 1MB 以上。
- `no_result` 重跑還會再加一次。
- 帳量那節只算了治理帳。
- 建議:`source` 是 `choice-kill` 時不寫 kill-log,因為治理帳已有判定;或只寫非 killed 的列。

## z6 冷編譯的基準會同時決定「逾時上限」與「壞法逾時下限」,spec 沒處理
severity: minor
blocking: 否——只在冷編譯慢或壞法無窮迴圈時放大成本,有環境變數可調。

- spec 段落:〈實務隱患〉第一條。
- 引句:「Android 新工作樹冷編譯仍貴,實作時量一次 20 行改動的實際耗時寫進報告」
- 查證:
  - 基準上限固定為 `max(600.0, floor)`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28043`)。
  - 壞法逾時是 `max(b_elapsed * 5, floor)`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:28091`)。
  - 新樹的第一支測試基準含全專案冷編譯。
  - 冷編譯超過 10 分鐘 → 整批 abort、無任何訊息指向 `LUMOS_KILL_TIMEOUT_FLOOR`,而重跑又是一棵新冷樹。
  - 冷基準 8 分鐘 → 該測試每個無窮迴圈壞法(例:`while (a && b)` 的 LCR 換 `true`)要等 40 分鐘才判 `timed_out_weak`。
- 現有的 `_situation_rule_kill` 有開跑前印出上限的訊息(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:76076` 起),choice-kill 的 spec 沒寫沿用。
- 建議:
  - 逾時倍數改用熱的基準,或加絕對上限。
  - 基準逾時的訊息指向環境變數。
  - 開跑前印上限。

## z7 「同一份計劃」與「碰到的計劃(複數)」對不上,一次呼叫的粒度沒定(r1 z6 第一點沒折完)
severity: minor
blocking: 否——判定語意不會錯,只是成本倍數與 `plans` 欄的歸屬要靠實作者猜。

- spec 段落:〈用詞〉守的測試、殺掉判定。
- 引句:「同一平台、同一份計劃的所有壞法,在一次 `cmd_guard_kill` 呼叫裡跑」
- 引句:「碰到的計劃的〈驗收條款〉裡,`[test:]` 綁的測試」
- 問題:
  - 範圍碰到兩份進行中計劃時,守的測試是兩份的聯集。
  - 一次呼叫只有一個 `node`(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:27902`),而 `node_dirty` 弱證據是按那份計劃的 git 狀態算的。
  - 若實作成每個壞法 × 每份計劃各一輪,冷樹與基準翻倍。
  - 「killing_test 取條款順序第一支」在跨計劃時也沒有順序定義。
- 建議:寫明「聯集、node 取哪一份、跨計劃順序」,或規定一份計劃一輪。

## z8 推送閘「算不出來」的補救建議 `--diff` 在 pre-push 用不上,超大檔會永久擋(r1 z4 折入不完整)
severity: minor
blocking: 否——只影響罕見情境(單支 .kt 超過 4MB)。

- spec 段落:〈範圍〉4「預算與讀不到」。
- 引句:「訊息列哪支檔、建議 `--diff` 縮範圍(同情境題那道的處理)」
- 查證:
  - `_kt_sit_read_many` 對單支 >4MB 的檔拋 `_KtSitUnverifiable`,整個範圍都算不出來(`/Users/enzo/harness/lumos-near-miss/scripts/lumos:40111` 起)。
  - 推送閘的範圍由掛鉤與分岔點決定,使用者無法在 pre-push 帶 `--diff`。
  - 那支檔沒有定位,也無法 `--judge`。
  - 結果:範圍內只要有一支生成碼 >4MB 就永遠擋,唯一出口是關掉整道閘的環境變數。
- 成本面無問題:實測 4MB 的 Kotlin 剝註解與字串只要 0.19 秒,30 秒預算在正常情況下不會被碰到。
- 另外,新的一圈在算不出來時「擋」,跟 `_spec_gate_push_check` 現有註解(算不出範圍或索引 fail-open,「推送閘不能因為工具壞而擋所有人」)不同。這是 spec 有意的選擇,但要在 Systems/規格閘寫明。
- 建議:超大檔改成列出、請人判該檔不適用或排除(例如加進跳過清單),別建議 `--diff`。

## z9 回報上限只是錯開批次、不減總量,而且 B 當種子可被作者重擲;跟論文 2.3 的口徑也不同
severity: minor
blocking: 否——不影響正確性,影響這道閘的設計意圖(降低認知負擔)有沒有達到。

- spec 段落:〈用詞〉回報上限、天花板 7。
- 引句:「回報上限之外的存活不擋;同一批存活要到 B 變了才可能抽到別的」
- 論文 2.3 節:上限是「7 times the number of total files in the changelist」(整份改動的所有檔)、從存活中隨機挑報告,未報的就不處理。spec 只數 `.kt` 正式碼檔,口徑較窄。
- 輸入 → 預期:20 個存活、上限 14。
  - 處理 14 個、提交帳,B 因此改變。
  - 剩 6 個,低於上限,全部變成擋下。
  - 總共仍要處理 20 個。論文是未抽到的就此丟掉,這裡只是分批。
- 因為提交治理帳(spec 要求的下一步)本身就會改變 B,抽樣結果每次推送必變。
- 作者也可用空提交重擲,挑到較好處理的子集。
- 「固定種子穩定回報」引的 3.2.4 節:論文那節談的是壓掉冗餘壞法(例:`x != nullptr` 的 `false` 與 `nullptr` 等價),沒有規定固定種子。spec 的雜湊種子是自己的機制,達成同一目標但不是論文做法。
- 建議:
  - 在 spec 明寫「分批不減量」。
  - 或以不受作者控制的量(例如範圍起點加改到的行雜湊)當抽樣種子。

## z10 乾節點規則第一版漏了論文明講的條件(複合節點遞迴規則與 A.1.11/A.1.17/A.1.20/A.1.22),spec 自己的 PRIOR-ART 還列了「提早 return、旗標」卻沒進表
severity: minor
blocking: 否——先天雜訊較高,但不改變機制;RETIRE-IF ① 會接住。

- spec 段落:PRIOR-ART、〈用詞〉乾節點規則。
- 引句:「附錄 A:log、斷言、時間、監控、容量、樣板方法、提早 return、旗標」
- 引句:「第一版照論文附錄 A 譯成 Kotlin:log(`Log.*`、`Timber.*`、`println`、`logger.*`)」
- 論文對照:
  - 第 5 頁公式 (1) 規定複合節點「只有所有部分都是乾的才算乾」。spec 的規則只比對「那一行」或「整個函式本體」,沒有這條遞迴。
    - 輸入:`if (BuildConfig.DEBUG) { Log.d(TAG, "x") }`,spec 規則下會在 `if` 那一行產生壞法並存活;論文下整個 if 都是乾的。
  - A.1.20:`list.size > 0` 換成 `>=` 或 `<` 是等價或不可達壞法(Kotlin 的 `.size`、`.length`、`isEmpty()` 同理)。
  - A.1.22:提早 return 優化(`if (xs.isEmpty()) return emptyList()`)被刪掉不改行為。
  - A.1.11:浮點 `>` 換 `>=` 無意義(`score > 0.95`)。
  - A.1.17:快取查詢的 `if` 被刪不改行為。
  - A.1.13 與 A.1.16 的旗標、閘道設定也沒進表。
- 論文表 2 顯示規則起步時 85% 的壞法被判沒用。spec 的 RETIRE-IF ① 用同一個八成線,卻從上線第一天就擋推送。
- 建議:第一版補上述各條,或在計劃寫明為什麼先不收,並在 RETIRE-IF 加暖機期。

## z11 選擇點表引論文表 1 時漏了 `<=`;「一行一個壞法」的挑法跟論文 Listing 2 不同卻不在差異清單裡
severity: minor
blocking: 否——都是雜訊與分布問題,不影響機制。

- spec 段落:〈用詞〉選擇點表 ROR、一行一個壞法、PRIOR-ART 差異清單。
- 引句:「ROR(論文表 1):`a > b` → `a >= b`、`a < b`、`true`、`false`」
- 論文表 1 的 ROR:`a > b → {a < b, a <= b, a >= b, true, false}`。spec 標著「論文表 1」卻少了 `<=`。
- spec 〈用詞〉一行一個壞法的做法:
  - 把整行的「選擇點 × 候選壞法」配對全部排成一串,用行雜湊種子打亂。
  - 論文 Listing 2 是只打亂運算子(五個),逐個運算子嘗試,第一個能產生的就用,運算子被選中機率均等。
- 後果:
  - 候選多的運算子(LCR 5 個、ROR 4 個、API)被選中的機率遠高於只有 1 個候選的(UOI)。
  - 與論文的運算子分布不同。
- 引句:「跟論文不同的地方:①論文用語法樹判節點,我們沒有 Kotlin 語法樹」
- 差異清單 ①–④ 沒列這一項。
- 建議:補進差異清單,或改成先挑運算子再挑候選。

## 其餘節與固定席

- 已讀,無 finding:
  - 〈白話〉。
  - 〈舊否決比對〉。
  - 〈不做〉。
  - 〈回退〉。
  - 預期值表與驗收條款交叉引用(S1–S21 都有對應列;範圍 1/4/5、天花板 2/3/4/6/7 的引用都存在且說法一致)。
  - 推送閘重算壞法的 CPU 成本(實測見 z8、z4)、治理帳讀取成本(0.09 秒)。
  - 整段 `_KT_SIT_BUDGET` 時限沿用。
- 實務隱患鏡頭逐類:
  - 時間:見 z1、z6。
  - 磁碟與暫存:單次呼叫一棵樹可接受;中斷殘留見 z2;每個 `--only`、`--point` 重跑各一棵冷樹見 z1。
  - 記憶體:`_kill_cap` 每次輸出上限 256KB,配方結果只留摘錄,無問題。
  - 帳量:見 z4、z5。
  - 程序與訊號:見 z2。
  - 網路:無,本功能不連外。
  - 並行:使用者排除。
- r1 資源席折入驗收:
  - z1(每點一棵樹)在樹與基準的層面已折到位。
  - z2(基準紅每點重付)已折到位:`baselines[cmd]` 在呼叫內快取了紅的結果,後續配方直接判 abort。
  - z3(殺掉後不停)被刻意放棄,但 z1 說明可兩全。
  - z4(推送閘預算)大部分折入,補救建議殘留見 z8。
  - z5(中斷)沒到位,見 z2。
  - z6 沒到位:kill-log 見 z5,計劃粒度見 z7。其餘兩點(blocked 同 B 不重記、提醒提交帳)已折入。
- 固定席(`Systems/guard-kill`)逐條判:
  - INVARIANT「guard kill rc 優先序」:不影響。spec 只加選用 `source`,不碰 rc 計算。我在 z1、z2 建議的回呼、分組提前停也只會減少列、不改 `abort`、`error` 與 `survived` 的優先序。
  - INVARIANT「`--json` 成功時 stdout 恰一行」:不影響。choice-kill 不帶 `as_json`。若採 z1、z2 的建議,預估與進度訊息要走標準錯誤。
  - `Systems/規格閘`:節點沒有合約行,新增一圈不破壞既有合約。唯一要留意是 z8 說的「算不出來擋」跟該函式註解的 fail-open 方針相反,需在節點補一句 WHY。
- 暫存:我的實驗腳本在 `/tmp/lumos-seat-work/改動選擇點都要有需求守住/資源-sonnet/`(t1.py、t2.py),由編排者收貨後刪。實驗中建的系統暫存資料夾都已逐一用字面路徑刪除。repo 沒有被改動。

最嚴重:major;blocking 共 4 條
