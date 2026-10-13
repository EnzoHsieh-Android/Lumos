severity: major

我沒改 repo,也沒建任何暫存目錄,所以不需要清理。實驗都是內嵌的 python 小腳本,只讀帳本與快照。

## 1. 連續未閉合的引句讓抽取變成平方時間,與「總成本約為報告長度」不符
severity: major
blocking: 是(判準:第 3 版自己寫的效能宣稱被具體輸入推翻,而且會讓收貨閘卡死)
引句:「掃到報告結尾還沒回到零:這條判格式不合,`kind="unclosed"`;從它之後的下一個標籤繼續抽,後面的引句不受影響。」
引句:「效能:每個標籤掃到它的引句結束與下一個標籤為止,一份報告總成本約為報告長度;比較指令對同一份快照只正規化一次。」
1. 輸入:`引句:「` 重複 N 次,中間沒有任何閉引號。這就是「報告極長未閉合」的最壞形狀。
2. 第一個標籤的深度一路增加到報告結尾,沒有回到零,判 `unclosed`。
3. 步驟 3 要求「從它之後的下一個標籤繼續抽」,第二個標籤同樣掃到結尾,如此重複。總成本是 N 的平方,不是線性。
4. 我照字面寫了一支樸素實作來量。N=500 約 50 萬步、0.03 秒,N=1000 約 200 萬步、0.13 秒,N=2000(報告 8KB)約 800 萬步、0.52 秒,每翻倍約 4 倍。
5. 外推到帳上現有最大報告 228,777 位元組,標籤數約 5 萬,約 12 億步,在 Python 裡是數分鐘。
6. 這個平方成本落在處置閘、寫側 `cmd_canary` 和 `--compare-rules` 全帳掃描上。席位或手改的報告就能把閘拖住。
7. 預期:一次掃描時記住「某深度已到結尾仍未回零」,後續標籤直接判 `unclosed`;或明寫「第一個 unclosed 之後的標籤全判 unclosed」。
8. 測試 `t_quote_full_span_unclosed_and_trailing_note` 只測少量標籤,抓不到平方。要補一條 N=5000 個 `引句:「` 的限時測試。

## 2. 設定區塊的壞值:rollback 開關打錯字時會往嚴的那邊失守
severity: major
blocking: 是(判準:回退章節的兩個止血開關,在最常見的人為錯誤下失效,spec 沒有規定)
引句:「讀法照 `_bound_tests_parallel`:區塊不是物件、值不在認得的集合,印一句提醒並當沒寫。」
1. 輸入:第二階段上線後,急著止血的人把 `quote_check.write_rule` 寫成 `"Legacy"`、`"legacy "`,或把 `read_override` 寫成 `"Legacy"`。
2. 兩個鍵都「不在認得的集合」,被當沒寫。
3. `write_rule` 退回程式預設,第二階段預設是 `full-span-v1`。回退被靜默換成最嚴的判準,只剩一行 stderr。
4. `read_override` 被當沒寫,隔離閥根本沒開。這正好發生在「新判準實作有缺陷、丟例外」的緊急時刻,警告只有一行,混在處置閘長輸出裡。
5. 值是 list 或 dict 時還有實作陷阱。我實測 `['a'] in {'legacy','full-span-v1'}` 與 `{'a':1} in 同一個 set` 都丟 `TypeError: unhashable`。照 spec「值不在集合」,如果實作用 set 比對,config 寫 `"write_rule": ["legacy"]` 會 traceback,而不是「提醒並當沒寫」。
6. 對照的 `_bound_tests_parallel` 是用 `isinstance(v, int)` 判斷,不是 set 成員測試。
7. 預期:
   - 比對先判 `type(v) is str`,再比對集合。
   - 無法辨識的值要和「沒寫」分開處理。
   - `read_override` 有寫但不認得時,要擋下或明顯警告,而不是靜默當沒寫。
   - 補測試:`write_rule` 是 list、`true`、`"Legacy"`、`null`;`quote_check` 是字串、陣列、`null`;兩鍵都缺。
8. 現有測試只有 `t_quote_full_span_rule_stamped_on_ledger` 用合法值設定(`legacy` 與 `read_override`),沒有任何壞值案例。
9. 還有兩個 spec 沒寫的情形:
   - `.lumos/config.json` 本身是壞 JSON:`_bound_tests_parallel` 是靜默 `return 1`,spec 沒說這裡要不要出聲。
   - `read_override` 已設且 `write_rule` 缺:第二階段預設會寫新章,同時讀側強制舊判準。兩者矛盾沒被點出。

## 3. read_override 與壞章誰優先,以及診斷指令在隔離閥下會印錯
severity: major
blocking: 是(判準:兩條相鄰規則的優先序未定,且診斷指令在隔離閥下與實際判準不符)
引句:「`read_override`:讀側隔離閥,只認 `"legacy"`;設了之後處置閘與回放對所有帳一律用 `legacy` 重算並印一行警告」
引句:「處置閘判失敗時印的診斷指令帶上該列的 `--rule <章>`。」
1. 輸入:`read_override=legacy`,載體列 `"quote_rule": ""` 或 `["x"]`。
2. 〈讀章的規則〉說空字串或非字串「判失敗」。隔離閥說「一律用 legacy」。兩邊都可以照字面成立,spec 沒排順序。
3. 實作若先驗章,隔離閥擋不住壞章帳,止血失效。實作若先看隔離閥,壞章被吞,與 S5 的「章的值不合判失敗」互相衝突,測試也沒釘。
4. 另一個問題:隔離閥開著時,處置閘用 `legacy` 判。但同一段會印「診斷指令帶 `--rule <章>`」,章是 `full-span-v1`,人照貼會得到與閘不同的結果,而且得到的是被隔離閥想避開的新判準分支。
5. 章是無法辨識的字串時,`--rule <章>` 會被 argparse 的 `choices` 拒絕,那條診斷指令根本跑不起來。
6. 預期:
   - 明文規定「隔離閥優先」或「壞章優先」。
   - 隔離閥下診斷指令印 `--rule legacy`。
   - 判失敗的列不印 `--rule`。

## 4. `--compare-rules --since` 的 0、負數、極大值與非整數都沒定義
severity: major
blocking: 是(判準:spec 說「跟 gov --since 同義」,但 gov 的行為本身在極端值會 traceback,spec 沒另行規定)
引句:「`--since N`:近 N 天(整數,跟 `gov --since` 同義),用 `_loop_ts_key` 比;`ts` 解析不動的列算進「略過」。不給就掃全帳。」
我實測 `gov --since` 的實作(`datetime.date.today() - timedelta(days=N)`):
- N=0 得今天,N=-5 得未來日期 2026-10-18,N=100000 得 1752-12-28,N=10**10 丟 `OverflowError: Python int too large to convert to C int`。
- N=999999999 的 `date - timedelta` 也會超出 date 範圍丟 OverflowError。
- `gov` 的 `--since` 是 `type=int`,所以 `1.5`、`1e3` 由 argparse 擋成 rc2。

拿這些輸入對照 spec:
1. `--since 0` 在秒數比較下 cutoff 是「現在」,所有舊帳都在窗外,得到全 0 的表。窗外的列不在「略過」任何一格,表的總和與帳本列數對不上,也沒有「窗外」計數。
2. `--since -5` cutoff 在未來,同樣全 0,而且靜默 rc0。預期:拒絕非正整數,rc2。
3. `--since 99999999999`:實作若照 gov 用 `timedelta`,traceback。預期:給上限或改用秒數運算,並明講上限。
4. `--since 1.5`、`abc`:行為靠 argparse `type=int`,但「位置參數與 `--spec` 改成不必填」的子 parser 重構可能把 `type` 丟掉。spec 要求寫明。
5. `ts` 不是字串時,`_loop_ts_key` 會丟例外,不是回 None。我實測 `_loop_ts_key(123)`、`_loop_ts_key(['x'])` 都是 `AttributeError`(`not ts` 只擋 None、空字串、0,`123.replace` 會爆),spec 卻說解析不動算進「略過」。
6. 帳上 `ts` 現況 4124 筆帶時區字串、95 筆是沒帶時區的字串,沒有非字串。非字串 `ts` 只可能來自手改,但「壞行」的定義(是否含「合法 JSON 但非物件」如 `[]`、`123`、`null`)也沒寫。我實測帳本現在有 0 壞行、4219 列全是 dict。
7. 預期:`ts` 不是 str 時視為略過;JSON 非物件的行歸「壞行」。補測試:`ts: 123`、行是 `[]`、`--since 0`、`--since -1`、`--since 99999999999`。

## 5. `_QUOTE_RULE_STAMP_SINCE` 在剛好相等與無時區時行為不明
severity: minor
blocking: 否(判準:只影響警告行,不影響判準,spec 已說只警告不擋)
引句:「帳列沒有章但 `ts` 不早於它 → 處置閘多印一行警告」
1. `ts` 剛好等於常數時,「不早於」成立,所以印警告。邊界方向有寫,但沒有測試釘住。
2. 帳上有 95 筆 `ts` 是沒帶時區的字串。`_loop_ts_key` 對它回 None。spec 只說 `_loop_ts_key` 比,沒說 None 時怎麼辦。
3. 若退回 `_loop_ts_newer` 的字串比對,`"2026-10-13T10:00:00"` 比 `"...+08:00"` 短,字串較小,會判成早於,漏警告。若解不動就不印,同樣漏警告。
4. 預期:規定「ts 解不動或無時區 → 不警告」或「→ 警告」二選一,並加兩個測試(相等、無時區)。
5. 缺 `ts` 的無章列、`ts` 在未來(時鐘偏移)的舊列同理:未來時間會誤印警告。

## 6. 比較指令的記憶體宣稱自相矛盾,實際用量約 286MB 以上
severity: major
blocking: 是(判準:兩句宣稱不能同時成立,實測數字讓「快取」一句直接變成記憶體風險)
引句:「讀不到檔、不是 UTF-8、帳本壞行都略過並各自計數;同一份快照只正規化一次(快取),不把全部文字留在記憶體。」
1. 「同一份快照只正規化一次」需要保留每份快照的正規化結果。「不把全部文字留在記憶體」要求不保留全部。兩句同時要求,沒有說明快取策略(LRU 容量?或先按快照分組再逐組處理?)。
2. 我統計目前帳本:952 份不同快照、3286 組(報告, 快照)配對,快照總計約 286,620,506 位元組(約 286MB)。
3. `_quote_rows` 每次呼叫還會再建 `hay` 與去空白的 `hay_ns` 兩份副本,所以全快取約 3 倍,接近 1GB。
4. 預期:規定「按快照分組、組內共用一份、處理完就丟」,或給快取上限,並加壓力測試(造 1000 份 300KB 快照的帳本跑,量峰值)。
5. 另一個相關問題:`_quote_rows` 的簽名是 `(rtext, stext)`,每次都重新 `_quote_norm(stext)`。「只正規化一次」要求拆出新介面,但 spec 說「四個呼叫點各自明確傳 `rule`」,沒有講新介面。

## 7. gov --stats 新分類與舊事件混合時,計數可能重複或變負
severity: minor
blocking: 否(判準:要特殊席名才觸發,現有分類是子字串比對,spec 沒要求更嚴)
引句:「`lumos gov --stats` 的「記帳被寫側擋下」分類多一格「引句判準」,以 note 開頭 `quote-rule:` 計數,不再落進「缺 refuted-set」。」
1. 現行程式 9530 到 9532 行:`_rn` 和 `_rf` 用 `"report-not-normalized" in _d(r)` 的子字串比對,「缺 refuted-set」是 `len(_rej) - _rn - _rf` 的剩餘值。
2. 新事件 note 帶 `auditor=<席>`,席名是自由文字。若席名含 `findings-over-reported` 這串,同一筆事件會同時被 `_rf` 與新分類計一次。
3. 若實作只是新增 `_rq` 計數而沒有互斥,「缺 refuted-set」可能變成負數。
4. 舊事件(不含 `quote-rule:`)與新事件混在同一個窗口時,舊事件仍照剩餘值算進「缺 refuted-set」,新事件必須排除,否則舊 18 筆 + 新 N 筆全落入剩餘格。spec 只有「不再落進」一句。
5. 預期:四個分類改成互斥的 `startswith` 優先序,並在測試中混入舊事件與席名含這些子字串的新事件,驗證四格相加等於總數。
6. 現有 `t_quote_full_span_compare_and_event` 的混合案例有沒有涵蓋,我只能看到名稱,沒有逐行驗證。

## 其餘節
- 〈抽取規則〉步驟 1 到 2、4 到 6:已讀,除 finding 1 外無 finding。
- 〈兩階段上線〉、〈回退〉、〈實務隱患〉:除 finding 2、3 的連帶影響外,已讀,無 finding。
- 實務隱患的風險類:
  - 效能:有,見 finding 1、6。
  - 自我治理:spec 已列。
  - 不可逆、金流、對外送出:spec 已寫,我也核對過這次改動沒有新路徑。

總結:最高等級 major,blocking 共 4 條(findings 1、2、3、6 與 4 合計為 5 條 blocking 標示,其中 finding 4 同為 blocking: 是)。更正:blocking 為 1、2、3、4、6,共 5 條。

總結:最高等級 major,blocking 共 5 條
