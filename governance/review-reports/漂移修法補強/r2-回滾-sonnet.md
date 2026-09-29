severity: major

# 設計審 r2 回滾-sonnet 席報告(漂移修法補強_計劃 r2 凍結稿)

對照的 repo:`scratchpad/clone-ns`(唯讀,未改任何檔)。以下 file 路徑都相對該 repo。

## F1 c1/settle 回退清單漏了「回傳個數」往上傳的三層,照清單退會讓 settle 與 c1、c5 當場解包失敗
severity: major
blocking: 是
引句:「`_guard_settle_rewrite` 多回的集合與組字函式拿掉,兩處訊息改回原字串」
file: `scripts/lumos:12134`
file: `scripts/lumos:12274`
file: `scripts/lumos:12537`
1. 現況 `_guard_settle_rewrite` 回 `(out, missing)`;它被 `_guard_pass_rewrite`(12290,再回 4 元組給 12425 的 `_guard_settle_pass` 與 27836 的 `_drift_fix_c1`)和 `_guard_settle_record_lines`(12537,3 元組,給 settle 的 pending 路徑與 c5)呼叫。
2. spec 第 3 節要讓它「另外回傳已是轉正後說法的種類集合」,元數變了,上面三層一定要跟著改才接得到集合。
3. 回退只寫拿掉 `_guard_settle_rewrite` 的集合與兩處「訊息」,沒列 `_guard_pass_rewrite`、`_guard_settle_record_lines`、`_drift_fix_c5`、`_guard_settle_locked` 也要改回。照字面只退第一支:`_guard_settle_rewrite` 回 2 元組,`_guard_pass_rewrite` 仍解 3 個,`lumos guard settle` 對每一篇已 pass 的守衛紀錄與 `drift fix --kind c1/c5` 都會 ValueError。
4. 我另外驗了:多認的三種「已轉正」說法只進 `seen`,而 `seen` 只決定回傳的 `missing`(12134 起的函式體),不影響寫出去的行,所以「退只影響訊息」這半句是對的,缺的只是元數傳遞那一串。
5. 建議:回退寫成「`_guard_settle_rewrite` 與所有解它回傳值的呼叫端(列出 4 支)一起改回」,並要求先用 `grep -n "_guard_settle_rewrite\|_guard_pass_rewrite\|_guard_settle_record_lines"` 對一次。

## F2 `_vendored_intact` 的三處既有內嵌清單點錯,回退說「留著、三處行為不變」的前提不成立
severity: major
blocking: 是
引句:「這個內嵌寫法已有三處(推送前小改動判定、筆記形狀擋兩處),一起改成呼叫它,行為不變」
file: `scripts/lumos:18365`
file: `scripts/lumos:24477`
file: `scripts/lumos:24609`
file: `scripts/lumos:17833`
1. 我 grep `frozenset() if _is_toolchain_repo(root) else _vendored_state(` 得到的三處是:18365(`_stack_ext_counts` 一帶的技術棧掃描,`ref` 省略=讀工作目錄)、24477(筆記形狀擋,`ref=""`)、24609(筆記形狀擋,`ref="" if staged else tip_where`)。「推送前小改動判定」不在其中。
2. 推送前小改動判定走的是 `_vendored_skip`(17833):它呼叫 `_vendored_state` 兩次(終點、起點),還有 `_intact_end | (_intact_start - _present_end)` 的拆除工具鏈邏輯,不是那個一行內嵌。照 spec 字面「把三處收成 `_vendored_intact(root, ref)`」,實作者會去改 `_vendored_skip`,拆除跳過那段會被抹掉或要另外偷渡;而真正的第三處(18365,ref 是 `None`)會被漏改或被誤傳成 `""`,從「讀工作目錄」變成「讀索引」,行為變了。
3. 回退因此也不成立:回退段寫「`_vendored_intact` 可以留著(三處既有呼叫行為不變)」;若實作時已把 `_vendored_skip` 或 18365 的 ref 語意動過,「留著」就把行為變更一起留下。要真退乾淨,得知道每一處原本的 ref(`None` / `""` / `"" if staged else tip_where`),spec 沒記。
4. 建議:第 5 節改寫成明列三個真實位置與各自 ref,`_vendored_skip` 標明不動;`_vendored_intact` 的 ref 不給預設值。

## F3 卷證目錄的「撤掉」路徑與 c4 寫入互鎖:只撤第 1 節、留第 2 節時修復帳與測試會壞
severity: major
blocking: 是
引句:「`_drift_c4_evidence` 改回只用計劃名比對;修復帳多出的 `reports_same`、`reports_name` 舊版會忽略」
file: `scripts/lumos:27935`
file: `scripts/lumos:28125`
1. 第 2 節「過了才組 `res`」的 `extra` 明寫 `reports_same`、`reports_name` 由證據函式產出,S2 條款與測試 `t_drift_fix_c4_values_writes_via_set_rewrite` 把這兩欄釘進修復帳。現況 `_drift_c4_evidence` 只回 `first`、`reports`、`template` 三鍵(27950)。
2. RETIRE-IF ① 的處置是「同提交找法沒帶來計劃名以外的東西,撤掉」——也就是單獨撤第 1 節、保留 `--values`。回退段只給整包退的說法,沒講單撤第 1 節時:`extra` 那兩欄怎麼辦(拿掉?寫空清單?)、S2 測試釘的兩欄怎麼改、`RETIRE-IF`/REVISIT 的一行量測指令(靠這兩欄)撤後就失效。
3. 結果:觸發 RETIRE-IF ① 的那一天,照現有文字只能整包退(連好的 `--values` 一起退),或自己臨時發明「只退一半」的做法;而第一個實作 c4 寫入的人不知道這一欄未來會被撤,可能把它耦合進 S2 的判定。
4. 舊版工具讀新修復帳:我查了 `_drift_jsonl_rows`(27554)、`_drift_fix_last_sha`(27755)、`_drift_next_seq`(27565),舊版只取 `path`、`seq`、`after_sha256`,多出的鍵不會出錯——回退段這句「舊版會忽略」是對的,已驗;缺的是單撤第 1 節的說法。
5. 建議:回退段補一條「只撤卷證目錄」:`extra` 兩欄改成什麼、S2 測試哪一行改、REVISIT 指令改量什麼。

## F4 翻案決策與「被取代的 PITFALL」沒有機械上的還原路徑,回退寫的做法做不到
severity: major
blocking: 是
引句:「翻案決策用 `lumos decision-supersede` 撤」
file: `scripts/lumos:15603`
file: `scripts/lumos:3300`
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:44`
1. 被翻掉的舊決定住在存量漂移守衛的 PITFALL 行(該篇第 44 行「c4 不自己寫開頭欄位的原始文字…Enzo 2026-09-30 裁改走既有的 lumos set」),那一篇根本沒有 `decisions:` 欄位(grep 無)。所以「用 `lumos decision-add` 記翻案」記的是一條全新的決策,沒有任何舊決策可以被 `decision-supersede` 指向。
2. 「把那條 PITFALL 標成被取代」沒有機制:`[status:superseded]` 只有 RULE 行認(`scripts/lumos:3300` 一帶的 RULE 檢查,且訊息要求「確定撤掉就把整行刪掉」),PITFALL 沒有這個標記。實作者只能手寫一句散文,之後沒人機械讀得出。
3. 回退時:`decision-supersede` 撤的是新那條——把新決策標 `valid:false`、補 `superseded_by`,並開一本連鎖帳(15603 起,函式說明寫「開一本連鎖帳」,連鎖帳要 confirm/prune),可是沒有任何步驟把舊裁決「復活」;`cmd_decision_supersede` 也拒絕重複翻案,已翻過就不能取消。推上去之後 `decision-amend` 又不准動結構欄。所以回退後圖譜狀態是:新決策失效、舊裁決只剩一句被標「被取代」的 PITFALL,兩邊都沒有一條有效的當前裁決。
4. 回退段說「一起改回」,沒說改回成什麼、用哪個 commit 當基準。
5. 建議:實作時把舊裁決的 PITFALL 前面加一句可 grep 的固定標記(例如 `[已被〈決策編號〉取代]`),決策以 `--supersede` 的新決策指回它;回退寫成「`git revert` 那個提交」為主要路徑(單一提交含程式、筆記、決策),而不是靠 supersede。

## F5 delguard 跳過紀錄寫進「detail」,但實際只有 `note` 欄;RETIRE-IF ② 的量測沒有可 grep 的標記
severity: major
blocking: 是
引句:「記在既有的 delguard 治理事件的 detail 裡(RETIRE-IF ② 要抽樣這些名稱)」
file: `scripts/lumos:29401`
file: `scripts/lumos:7256`
file: `scripts/lumos:7321`
1. `_delguard_log_result`(29401)寫的事件只有 `gate、kind、hard、nodes、note`,note 是 `tokens=… hits=… secs=…`;`detail` 是 `lumos gov` 讀取時從 `note` 映射出來的名字(7256),不是磁碟上的欄位。照字面在事件裡加 `detail` 鍵,`gov` 讀不到(它只讀 `note`)。
2. 跳過資訊要能被 RETIRE-IF ②「累計 ≥20 次因工具檔跳過」數到,spec 沒定義固定字樣(不像既有的 `reason=slow`)。REVISIT 的指令只 grep `"gate": "delguard"`(我驗過 923 筆命中,格式對),數不出哪些是「因工具檔跳過」。
3. 逾時降級走 `_delguard_log_degraded`(29411),事件也沒有這個資訊;spec 只說在既有剩餘時間判定內做,沒說降級路徑要不要帶跳過數,累計會少算。
4. `lumos gov` 顯示層把 delguard ok/degraded 折成 ×N(7321,`_is_advisory`),note 內容不出現,抽樣 5 次名稱只能讀原始 jsonl。REVISIT 那行沒寫這一點。
5. 建議:寫進 `note`(不是 `detail`),固定前綴如 `vendored-skip=<n> names=<最多 20 個>`,降級路徑也帶;REVISIT 指令改成 `grep 'vendored-skip='`。

## F6 混版機器:全域 skill 文件比專案自己的工具新時,文件叫人用 `--values`,舊版工具只回 argparse 用法錯誤
severity: minor
blocking: 否
引句:「筆記不乾淨或另一台是舊版工具:也可以用 `lumos set <節點> valid_under …`(不記修復帳)」
file: `skills/lumos-project-notes/commands/04-自檢與健康.md:11`
1. 這句提示是新版工具印出的,舊版根本不會印。而 spec 第 6 節要同步改的 commands/04 那一列是 skill 文件,skill 走 symlink 隨 repo 更新(記憶:lumos 更新分發),消費專案裡 vendored 的 `scripts/lumos` 要 `lumos update` 才換。
2. 場景:機器 A 已拉新 skill(commands/04 寫 `--kind c4 --values`)、專案 vendored 工具還是舊的 → 模型照文件下 `--values`,舊版 argparse 報 `unrecognized arguments: --values`,沒有任何指到 `lumos set` 的退路。反向(退回工具、skill 還沒退)同樣。
3. 回退段沒提「文件先退還是工具先退」的順序,也沒提消費專案要重跑 vendored 更新。
4. 建議:commands/04 那一列同時寫「舊版沒有 `--values` 時用 `lumos set`」,回退順序寫成先退文件、後退工具。

## F7 RETIRE-IF ① 在資料量不足時沒有預設動作,機制可能永遠留著
severity: minor
blocking: 否
引句:「上線兩個月後(以 REVISIT 那天為準):①工具鏈與 rtb 合計 c4 修復帳 ≥5 筆,而」
1. 修復帳只在走 `drift fix --kind c4 --values` 時才有 c4 筆;走 `lumos set` 不記帳(spec 誠實界線自己承認)。rtb 這輪 26 筆漂移是用 set 修的、帳上沒 c4 紀錄,新增 c4 漂移是否一天 5 筆都難說。
2. 2026-11-30 那天若總數 <5,①條件不成立也不成立反面,REVISIT 那行沒說「資料不足就延期一次並寫出下一個日期」還是「視為維持」。實務上就是沒人回頭、機制無限期留著。
3. 建議補一句:不足 5 筆就把 REVISIT 順延並記為單次量測。

## 逐項勾對「回退」清單(對第 2 到第 6 節新加物)
- 第 1 節:改 `_drift_c4_evidence`、列提交檔案、來源標記、排序、`_esc_clean` 與 `_drift_sh` 用法。回退只講了 evidence 函式,無 finding(見 F3 對 `extra` 的耦合)。
- 第 2 節:`--values` 接線七處都列了;`_conditions_vals_err`、`_conditions_rewrite` 留著合理(set 行為由 S3 釘住)。未提的「證據頁 `_conds` 展開、2000 字限、逐項列出」屬於同一支 `_drift_c4_print`,「指令改回 lumos set」若被讀成只改指令那一行,展開與限長會殘留,但殘留無害,不算 finding。
- 第 3 節:見 F1。
- 第 4 節:c3 `--reason` 三處都列了,已讀,無 finding。
- 第 5 節:`skip` 預設空集合可讓呼叫端不傳即回原行為,已讀,無 finding;`_vendored_intact` 見 F2;治理事件欄位見 F5。
- 第 6 節:文件與測試同步見 F4、F6。

## 合約行(★INVARIANT★)判定
- Systems/guard-kill 兩條 INVARIANT(guard kill 的 rc 優先序、`--json` 成功時 stdout 恰一行 JSON):只管 `guard kill`,這份設計動的是 `guard settle` 的「找不到」訊息與回傳集合,不碰 kill 的 rc 與 JSON 輸出,不影響。
- Systems/lumos-cli-write、Systems/delguard、Systems/存量漂移守衛:我 grep `INVARIANT|IRREVERSIBLE` 在這三篇沒有命中(guard-kill 之外沒有),沒有可判的合約行。

## 舊版讀新修復帳、混版補充
- 舊版讀新帳:已驗證安全(見 F3 第 4 點);「乾淨檢查」用 `_drift_fix_last_sha` 比最後一筆 `after_sha256`,c4 新筆有這欄,舊版反而能把 `--values` 留下的未提交改動當成工具自己的,不會誤擋。
- 已用 `--values` 改過的筆記在回退後:舊版乾淨檢查認得那筆指紋,同一篇繼續修不受影響;只有「先 revert 筆記、帳留著」時最後一筆指紋與檔案不符,但那時檔案等於 HEAD,乾淨檢查第一條就放行,無 finding。

最高等級:major;blocking 共 5 條
