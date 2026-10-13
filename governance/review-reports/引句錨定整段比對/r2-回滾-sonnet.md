severity: major

說明:我沒改任何檔,也沒在 repo 根跑 git 寫入。實驗放在 `/tmp/lumos-seat-work/引句錨定整段比對/回滾-sonnet/`,結束已刪。實作還不存在,所以「停用」走一遍是用讀碼加最小實驗代替。finding 1 到 3 是照〈回退〉兩條路走出來的後果。finding 4 到 6 是帳上多出欄位與事件對其他讀者的副作用,以及測試的空缺。

讀帳本的地方我查了 `scripts/lumos` 裡約 30 處,加上 `governance/autonomous_loop/run_ledger.py`、`confidence_report.py`、`replay_weekly.py`。它們都是逐欄 `.get`,沒有欄位白名單。`_jsonl_append_verified` 對審查帳沒有行長上限(4096 位元組的限制只在 `_ledger_append` 與治理帳)。回放的 `all_row_shas` 是整行雜湊,多一欄不影響。所以「舊版程式讀到多的欄位會忽略」成立。副作用出在 finding 4(`gov --stats`)。

## 1. 停用只管新帳,舊章指到的新判準分支關不掉;回退只考慮判太嚴,沒考慮新判準實作本身壞掉
severity: major
blocking: 是
引句:「已蓋 `full-span-v1` 的帳照章用新判準重算,判定不變,回放不漂移。寫側、處置閘、回放三者始終一致。」
file: `scripts/lumos:26373` 處置閘引句步驟的 `try` 只接 `OSError` 與 `UnicodeDecodeError`
1. 回退的起因若是新判準判太嚴,「停用」有效:寫側立刻放行,新帳蓋 `legacy`。
2. 起因若是 `full-span-v1` 那一支自己壞了,例如對某種輸入丟例外、跑太慢、或誤放編造引句,停用止不了血。
3. 已蓋章的帳會在 `loop status --disposal`、`loop replay --freeze/--golden`、週跑回放三處繼續走那個壞分支。
4. 上面 `try` 只接兩種例外,新分支丟 `IndexError` 或 `RecursionError` 會直接 traceback。誤放則是已蓋章的帳永遠被當真。
5. 規格只給兩條路:停用,或完整還原。完整還原會讓全部蓋章的帳走舊判準,後果見 finding 2。
6. 沒有「讀側暫時無視章、一律走 legacy」的隔離閥,也沒有「章不信任」的路徑。
7. 〈回退〉要補一條「新判準實作缺陷」的處置:讀側總開關,或明寫只能修新分支、修了要重凍。

## 2. 完整還原的補救步驟「逐個 `--freeze --note` 重凍」做不到回復,只會把紅燈凍進去
severity: major
blocking: 是
引句:「回放漂移的要逐個 `lumos loop replay <編號> --freeze --note` 重凍。」
file: `scripts/lumos:1139` 凍結只擋 `rc == 2`,`rc == 1` 照凍;`scripts/lumos:1268-1282` 回放比的是 rc 與 fails
1. 還原成舊版程式後,蓋 `full-span-v1` 且含巢狀引句的迴圈,處置閘判 `quote` 失敗,rc=1。
2. 照規格重凍,舊程式第二趟重算仍是 rc=1,所以 `verdict.json` 記成 `{"rc":1,"fails":["quote"]}`。
3. 實際證據:現有 305 個 golden 裡已有 5 個 rc=1 的 verdict(3 個「留痕」、2 個「處置集合」),所以凍紅燈是被允許的。
4. 之後重新升級到新版程式,同一個迴圈重算變 rc=0,與凍結的 rc=1 不同,又報邏輯漂移。
5. 補救步驟只是讓當下不報漂移,並沒有回復。這個迴圈在舊程式下仍是「沒收斂」。
6. 〈回退〉該寫的是:重凍會把紅燈凍成標準答案,升級回來要再重凍一次。處置閘轉紅的輪次要換迴圈編號重記,或乾脆不還原。

## 3. 完整還原的步驟漏了知識圖譜與決策那一半
severity: minor
blocking: 否
引句:「用 `lumos decision-add` 在本計劃記成決策,Issue 結案時註明前提失效的理由。」
file: `scripts/lumos:53479` 附近 quote-check 分派(本計劃要加的 `--rule` 與 `--compare-rules` 都落在這裡)
1. 還原提交只回程式。〈同步改的地方〉列的範本、`Systems/design-loop`、`Systems/loop-convergence-recording`、Issue 結案註記、立案清單第 18 項,都還說判準蓋章成立。
2. 依專案的 CLAUDE.md,圖譜是脈絡來源,程式碼才是現況依據。還原後這些筆記會變成會說謊的筆記,而〈回退〉沒有一步提到它們。
3. 要補一步:還原時一併把這些筆記標 superseded,或另立 Issue。

## 4. 新增的擋下事件會被 `gov --stats` 歸到「缺 refuted-set」,而且同秒同文字會被折成一次
severity: major
blocking: 是
引句:「記帳寫側因新判準擋下載體時,用 `_gate_event_or_warn` 記一筆 `canary` 閘的 blocked 事件,note 帶 `quote-rule=full-span-v1` 與不合的類別,REVISIT 到期有資料可數。」
file: `scripts/lumos:9531` 附近 `_rn`、`_rf` 兩個計數,其餘全算「缺 refuted-set」
實驗:
1. 我在 `/tmp` 的暫存 git repo 用 `_gate_event` 寫兩筆 `canary/blocked`,一筆 note 是 `quote-rule=full-span-v1 unclosed …`,一筆是 `report-not-normalized:2 …`。
2. 跑 `lumos gov --stats --since 5`,輸出:`記帳被寫側擋下 2 次(報告沒正規化 1 / 缺 refuted-set 1 / findings 多於 reported 0)`。
3. 新事件被歸成「缺 refuted-set」。這個算式是 `len(_rej) - _rn - _rf`,只認兩個字串。
4. REVISIT 要靠 `lumos gov` 數 quote-rule 擋下,但目前數不到,還會灌水另一個類別。規格〈同步改的地方〉沒列要改 `gov` 這段。
5. 另一個問題是 `scripts/lumos:9707` 附近 canary blocked 事件的去重 token 是 `ts + note`。同行 10933 的先例都在 note 加 `id=<uuid>`,註解說明「同一秒連撞兩次不能折成一次」。規格沒要求新事件帶 `id=`,同秒同類別的擋下會被折成一筆。
6. 規格要補:改 `gov --stats` 的分類,note 要帶 `id=`。
7. 還有一個沒定義的點:現行載體引句「錨不到」的擋下(`scripts/lumos:10947-10962`)沒有記事件。「因新判準擋下」是只記新判準獨有的翻轉,還是新判準下所有載體擋下都記,規格沒說。〈量測〉要的「新判不過、舊判過」只有前者數得出來。

## 5. 手動 `quote-check` 的新輸出要求與現有 `--json` 消費者衝突;新旗標與現有 parser 不相容
severity: minor
blocking: 否
引句:「手動 `lumos quote-check` 預設用 `_QUOTE_RULE_WRITE`,可加 `--rule legacy|full-span-v1` 指定;輸出第一行寫明用的是哪一版。」
file: `scripts/lumos:53141-53144` 與 `scripts/test_lumos.py:26152`
1. `--json` 模式現在只印一行 JSON,測試直接 `_j.loads(r2.stdout)`(`test_lumos.py:26152`、`26817`)。「輸出第一行寫明版本」若套用到 `--json`,這些現有測試會 `JSONDecodeError`。規格沒說 JSON 模式把版本放進物件欄位。
2. 現在的 parser 把 `qc_report` 設為必填位置參數、`--spec` 設為 `required=True`。〈量測與留痕〉的 `lumos quote-check --compare-rules [--since] [--repo]` 會被 argparse 擋成「缺少必要參數」。
3. `t_quote_full_span_compare_and_event` 照規格呼叫 `quote-check --compare-rules --repo …` 而沒帶報告。規格沒寫 parser 要怎麼改(`nargs="?"` 與互斥),實作者得猜。

## 6. 回退路徑沒有任何測試,而且目前的結構測不出來
severity: minor
blocking: 否
引句:「[S5] 當記帳寫側檢查通過時,那筆帳 應 寫 `quote_rule=full-span-v1`;處置閘重算時 應 照帳上的 `quote_rule` 選判準」
file: `scripts/test_lumos.py:26921` 起的 `t_quote_full_span_rule_stamped_on_ledger`
1. 該測試只測蓋 `full-span-v1`,以及用手改帳列(`gate_with`)測「無章、未知章」。
2. 沒有任何案例涵蓋:
   - `_QUOTE_RULE_WRITE="legacy"` 時,新帳蓋 `legacy` 章。
   - 處置閘接受 `legacy` 章。
   - `seat-check` 與手動 `quote-check` 預設隨常數變。
   - 蓋章的迴圈 `--freeze` 後 `--golden` 判定不變,且 `_REPLAY_ENGINE_REV` 沒推進。
3. 〈回退〉的核心宣稱「三者始終一致」與「回放不漂移」完全無測試把關。
4. 常數是模組變數,測試走子程序 `run(...)`,沒有環境變數或旗標可蓋掉它。要測停用,得有可注入點。
5. 這跟 finding 1 的「隔離閥」同源,一個環境變數或設定值可以同時解兩個問題。

## 已讀,無 finding
- 〈回退〉第三條「不可逆的部分」:成立,審查帳沒有欄位白名單或行長上限,舊程式忽略多的欄位。
- 「已凍結的 305 個迴圈都沒有這一欄」:查證屬實。`governance/replay/*/verdict.json` 共 305 個,帳本 `quote_rule` 出現 0 次。
- 〈回退〉第二條對「新判準判過、舊判準判不過那類」的描述:`t_quote_full_span_nested_and_multiline` 的舊判準前置斷言與現行 `_quote_rows` 一致。
- 讀 `.canary-log.jsonl` 的各處(含 `autonomous-loop.sh` 的 `run_ledger`、`confidence_report`、`replay_weekly`):逐欄 `.get`,多一欄無副作用。
- 一次停用的代碼審門檻:我在 `/tmp` 暫存分支加一行 `_QUOTE_RULE_WRITE = "legacy"`,`lumos pitfalls --diff` 判 `tier: standard`,不強制進高風險審查迴圈。但推送前的完整閘仍要跑。

總結:最高等級 major,blocking 共 3 條(finding 1、2、4)。
