severity: major

審查範圍:第 2 輪凍結版(r2-snapshot.md)全文,鏡頭「接手」。做過的核對:實跑參考實作 revisit 子命令(對 clone 的 HEAD~3..HEAD,5 秒、能跑、輸出四樣)、讀 `_gate_event`、`cmd_drift_check`、`_drift_print_hints`、`cmd_drift_ack`、`_drift_split_acked`、`_drift_config`、參考實作的 `Push.disappeared`、`_assigns`、`Note._mid_retire`、`_clause_has_hist`;54 個字眼逐項對過(26 + 25 + 3,前 26 與 `NEG_LEXICONS["zh"]` 逐字一致)。條款 S1–S13 每條可測性見文末表。

## F1 判不了發生在「候選名稱還不知道」的階段時,記不記帳兩句話打架
severity: major
blocking: 是
引句:「有候選名稱、或沒有起點時才記;這次沒改到程式檔、或有起點但沒有任何名稱消失 → 不印、不記」
file: `scripts/lumos:1147`(`_gate_event` 的 docstring:擋人時一定要有帳,寫不進去也不得改判定)
敘述:
1. 〈做法〉3 把「候選名稱」定義成過了形狀過濾與「消失」判定之後的名稱。「消失」要先有終點語料(所有 Python 檔的定義聯集),而 state 五種裡的 `git-failed`(列檔、diff、批次讀失敗)與 `timeout`(冷快取剖終點語料時最容易發生)都可能發生在候選名稱算出來之前。
2. 這時候選名稱數是未知(或當成 0)。照上面那句,「有候選名稱才記」不成立 → 不記帳;但同一節後面寫「git-failed、unreadable 在 warn 記 warned、在 block 記 blocked」,block 又要 rc 1。兩句不能同時照做:實作者要嘛 block 擋了人卻沒帳(違反 `_gate_event` 的「擋人時一定有帳」),要嘛自己加例外,計劃沒寫例外。
3. 連帶影響 REVISIT:RETIRE-IF ③ 的分子是 timeout 帳數。CI 永遠冷快取,最容易 timeout 的就是「剖終點語料階段」,那一類若不記帳,③ 會低估,「時間到的比例」量出來偏好看,轉擋的判斷偏樂觀。
4. 計劃沒說終點語料要不要先看「起點有終點沒有」的粗候選再決定要不要剖整個語料(沒有粗候選就不必剖、不會 timeout)。這個順序決定 1 到 3 發生的機率,也要寫死。
建議:寫明 git-failed 與剖語料階段的 timeout 在候選名稱未知時也記(候選數記 0 或 null),`no-candidates` 只用在「跑完、確定沒有」。

## F2 兩週帳資料太少或沒有時,「四條都不成立」會變成轉擋
severity: major
blocking: 是
引句:「任一條成立就不把預設改成擋、留在提醒」
敘述:
1. RETIRE-IF 四條全是「壞才留提醒」的寫法:①準度 < 60%、②單次 > 30 筆、③時間到 > 5%、④放過的真舊句 >= 1/3。沒有任何一條是「證據不足就不轉」。
2. 實驗數字顯示工具鏈 300 個提交只有 1 筆列出、要處理 0;兩週的工具鏈帳很可能要處理層 0 到 3 筆,rtb 那份靠跨會談訊息請對方回報(可能沒回、也可能 rtb 端還沒接上 drift check)。①的分母是 0 時準度 0/0 無定義,不「低於 60%」;②③④在沒資料時都不成立。照字面 REVISIT 那天的結論是「轉擋」,而且是根據零筆或幾筆(一筆假就 0%,一筆真就 100%)。
3. 〈做法〉4 的抽判寫了「30 筆以內全判」,但沒寫最少要幾筆去重後的要處理才准下結論;REVISIT 那行只有「前置沒接上就順延」一種順延理由。
建議:加一條「去重後要處理層 rows 少於 N 筆(或 rtb 帳缺)就順延兩週、不轉擋」,N 由編排者定(例:20)。

## F3 帳的欄位在計劃裡叫 `extra.*`,實際 JSON 沒有 extra 這一層
severity: minor
blocking: 否
引句:「從帳的 `extra.base_sha` 與 `head_sha` 抽」
file: `scripts/lumos:1217`(`ev.update(extra)`:extra 的鍵直接併進事件最上層)
敘述:
1. `_gate_event(..., extra={...})` 是把鍵合併到事件頂層,治理帳一行長得像 `{"ts":…,"gate":"drift-check","kind":"warned","check":"old-sentence","state":"done","base_sha":…,"rows":[…]}`,沒有 `"extra": {…}`。
2. 條款 S6 的「`extra.check` 是 old-sentence」與〈做法〉4 的「`extra.base_sha`」都可以被讀成巢狀:照 S6 寫測試的人會寫 `ev["extra"]["check"]` 而翻紅;REVISIT 的人用 `jq '.extra.base_sha'` 會全部拿到 null,抽不出 `--pairs`。`grep '"check": "old-sentence"'` 兩種讀法都比得到,所以沒被發現。
3. 計劃也沒給「從帳抽 `--pairs`」的指令(要 jq 或 python 一行),REVISIT 的人得自己猜欄名。
建議:S6 與〈做法〉4 改寫成「事件頂層的 `check`、`state`、`base_sha`(用 `_gate_event` 的 extra 參數傳入)」,並附一行抽 pairs 的 jq。

## F4 rows 上限讓單筆帳可達約 90 KB,比帳裡現有最長一行大約 20 倍
severity: minor
blocking: 否
引句:「rows 是要處理全部(最多 200)加只列出前 50」
file: `scripts/lumos:15826`(`_ledger_append` 的並行合約寫著單行 4KB 上限;`_gate_event` 沒擋,但現有帳最長一行約 4.8KB)
敘述:
1. 每筆 row 帶 path、line、layer、names、text(200 字),中文一字 3 位元組,最多 250 筆 ≈ 60–90 KB。工具鏈 `docs/.governance-log.jsonl` 現在 14.7 MB(超過 `_LEDGER_MB_CAP = 5` 的提醒線)、93590 行、最長 4816 位元組。
2. 每次有候選名稱的推送都寫,而且這個檔是追蹤的(每次多一大段未提交改動,下一個提交帶走)。rtb 大提交那種 20 筆要處理的推送不會撞上限,但每次推送都重複記同一批未改的 rows(〈做法〉4 自己說「同一句沒改、每次推送都會再列」),兩週內帳的體積成長主要來自這裡。
3. 計劃〈實務隱患〉的效能與併發兩項沒提帳體積。
建議:rows 只記要處理層與只列出前 10,或整批 rows 超過 4 KB 就只記筆數加前 N 筆;至少在〈實務隱患〉寫明取捨與回頭條件。

## F5 標題的 N 與 block 模式標題沒定義,S13 沒辦法寫死輸入輸出
severity: minor
blocking: 否
引句:「舊句檢查:這次推送消失了 N 個名稱,筆記裡還在講的——要處理 A 筆、只列出 B 筆」
敘述:
1. N 是「候選名稱數」(筆記先篩之前,例:200 個名稱消失、3 行還在講)、還是「有出現在發現裡的不同名稱數」?兩種讀法對同一輸入印出不同數字。〈做法〉3 定義了「候選名稱數」這個字,但標題那句沒有指過去。
2. 標題只寫了 warn 版括號「(drift_check.old_sentence=warn,不擋)」;S13 寫成「(drift_check.old_sentence=<值>…)」。block 版括號與 off 版(不印)沒寫,block 模式該印「擋下」還是沿用同一句?既有 `_drift_report_must` 的 warn 與 block 是兩個開頭(「擋下」與「提醒(…不擋)」)。
3. 輸出走 stderr 還是 stdout 沒寫(既有 drift check 全部走 stderr,`drift scan` 走 stdout);S13 測試要接哪個串流。
4. 要處理層與只列出層是印成一段還是兩段、只列出層有沒有改法提示,沒寫(既有 drift check 對只列出也印改法)。
建議:S13 加一個固定輸入與逐字期望輸出(含 block 版、含 N 的算法)。

## F6 改法或發現超過 20 筆時,既有的「還有 N 條(lumos drift scan 看全部)」會指到看不到 m1 的地方
severity: minor
blocking: 否
引句:「`drift scan` 與健檢(doctor)跑舊句檢查(只有一棵樹,判不了消失)」
file: `scripts/lumos:27674`(`_drift_print_hints` 超過 20 條時印「還有 N 條(lumos drift scan 看全部)」)
敘述:
1. `_drift_print_findings` 只印前 20 筆、`_drift_print_hints` 只印前 20 條;〈做法〉3 明說 `m1` 重用這兩支,只改去重鍵與長度上限,沒改 20 筆上限與那句結尾提示。
2. RETIRE-IF ② 自己允許「單次要處理超過 30 筆」發生。那次 block 模式下使用者只看得到 20 筆,想看剩下的,提示叫他跑 `drift scan`,而 S12 規定 scan 不含 `m1`,得到的是零筆。
3. block 模式修完 20 筆再推才看得到下一批,可行但不會知道還有幾筆該去哪看;也沒有 `m1` 專用的全列指令。
建議:`m1` 超過 20 筆時改印「其餘 N 筆改完再推會再列」,或提高 `m1` 的顯示上限。

## F7 被提示的人只知道「改寫或刪掉」,不知道怎樣的改寫才會過關
severity: minor
blocking: 否
引句:「改寫或刪掉這句;確定照留就」
敘述:
1. 使用者看到的是:標題、`路徑:行  原文`、消失的名稱與原本在哪支檔、一條改法。照貼 ack 指令是通的(`--name=--restore` 我核對過 argparse 接受、`_drift_sh` 對 `;` 與空白會加引號),ack 後 `cmd_drift_ack` 會另印「要提交表態檔」。
2. 但「改寫」到什麼程度才算修好,得知道 54 個歷史字眼與括號、切句規則(例:改成「原本叫 foo_bar,已移除」才會不列;只把「現在」改成別的詞還是會列)。這些只在程式常數 `_DRIFT_M1_HIST_WORDS`,提示與輸出都沒講;人改寫後再推,仍被列出來,只能猜。
3. 另外提示沒講「表態要提交進去再推,而且現在推送檢查只認提交進去的表態檔」;這句在 ack 指令輸出裡有,但先照「改寫」路走的人不會看到,不影響正確性。
建議:改法那行多一句範例,例如「改成歷史說法(例:原本叫 <名稱>,已移除)」。

## F8 「以 P4r3 為準」與計劃刻意加的擴充直接衝突
severity: minor
blocking: 否
引句:「凡是本計劃的字面跟 P4r3 不一樣,以 P4r3 為準、並回頭改計劃」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:521`(`tip_all_defs`:剖不動的終點檔用 `if info:` 直接略過,沒有文字比對退路)
敘述:
1. 〈做法〉1「剖不動」那條規定終點語料剖不動的檔要用 `_drift_py_def_re` 與引號包住的 `--旗標` 做文字比對;參考實作 P4r3 沒有這一步(略過,等於這些檔貢獻零個名稱)。4 MB 上限、`_drift_decode`、快取也是計劃加的、參考實作沒有。
2. 開頭那句說字面不一樣一律以 P4r3 為準,拿著它的實作者會把文字比對退路拿掉,再被 S11 的「不縮排的 `old_name: Callable = h` 找得到就當還在」翻紅;反過來照 S11 做就違反開頭那句。驗收數字不受影響(兩份語料剖不動都是 0 支),但規則本身自相矛盾。
建議:開頭那句改成「判定規則以 P4r3 為準,以下項目是正式工具刻意多的:文字比對退路、4 MB 上限、快取、讀不出的筆記」。

## F9 S5 的「git 行程數一樣」與 S10 的「批與批之間停下」沒點名測試接縫
severity: minor
blocking: 否
引句:「一次推送 `m1` 的 git 行程數不隨檔數成長:列檔 0–2、diff 1、程式檔批次讀 1–2、讀筆記 2」
敘述:
1. S5 要斷言改到 3 支與 30 支 `.py` 時行程數相同;〈做法〉1 寫「程式檔批次讀 1–2」,沒說什麼時候是 1、什麼時候是 2(沒副檔名檔另一批?),測試若在兩種輸入下剛好落在不同批數就翻紅。要寫死:批次讀數只由「有沒有沒副檔名檔」與「有沒有快取未命中」決定。
2. S5 要把 Python 版本函式「測試換掉它」,計劃沒給這支函式的名字(只在〈回退〉出現「取 Python 版本的小函式」);S10 要「把時間調到第 2 批前用完」,判定函式收 `deadline`(單調時鐘絕對值),測試沒法用調常數的方式落在第 2 批之前,要換掉時鐘或給批次鉤子,計劃沒說。實作者自己取名可以做,但條款「一條一支測試」的輸入沒寫死。

## F10 REVISIT 的人拿到的欄位與參數形式有三處要猜
severity: minor
blocking: 否
引句:「`--pairs` 每行一組 `<base_sha>..<head_sha>`」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:1254`(`cmd_revisit`;`--vault` 預設 `docs/lumos-toolchain-knowledge`,是 repo 相對路徑)
敘述:
1. 我實跑過:`old_sentence_exp.py revisit --repo <clone> --vault docs/lumos-toolchain-knowledge --pairs <檔> --out <json>` 能跑、5 秒,輸出「命中、字眼過濾放過、形狀過濾放過、撤除節②豁免行、否定撤除行」五個數。指令本身可用。
2. 計劃寫 `--vault <圖譜>`,沒說要給 repo 相對路徑(rtb 是 `docs/rtb-production-agent-demo-knowledge`);給成圖譜名會讀到空樹、命中 0,看起來像「沒有漏報」。
3. ledger 的 rows `path` 是圖譜相對路徑還是 repo 相對路徑,計劃沒說(〈做法〉4 的 `git show <head_sha>:<圖譜>/<path>` 暗示圖譜相對,但〈做法〉3 只寫 `{path, line, layer, names, text}`)。
4. RETIRE-IF ④ 的樣本是 `clause_released`,它同時含要處理與只列出兩層、也沒去重;〈做法〉4 的「去重」與「30 筆抽判」只寫給要處理層,④ 的分母口徑要照哪個沒說。

## F11 revisit 的「撤除節②豁免行數」數的是行,不是被藏起來的舊句
severity: minor
blocking: 否
引句:「兩週帳看不到被豁免的句子,REVISIT 用 revisit 子命令數」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:1276`(`cnt` 是被豁免節裡所有非空行)
敘述:
1. 我實跑的輸出「撤除節②豁免 163 行」是那兩篇被豁免節裡所有非空行數,不管那些行有沒有提到消失的名稱。要回答的問題「②有沒有把真舊句藏起來」,需要的是「關掉 ② 之後多出來的命中」(像 P4r3c、P4r3s 那樣多跑一個 P4r3 不含 ② 的版本再相減)。子命令沒有。
2. 計劃只說「記進計劃」、沒有任何 RETIRE-IF 條件用它,所以不擋轉擋;但〈誠實界線〉那句寫成「REVISIT 用 revisit 子命令數」,會讓人以為這個數回答了漏報問題。
建議:〈誠實界線〉改寫成「只數被豁免的行數,不知道其中有沒有真舊句」,或子命令補一個關掉 ② 的版本。

## F12 時間到時已找到的部分結果怎麼處理沒寫
severity: minor
blocking: 否
引句:「時間到時 warn 模式印明、不算要處理,block 模式算要處理」
敘述:
1. `timeout` 發生在掃到一半(第 2 批正則前用完),此時已經有要處理的命中。warn 模式是「印那一句沒跑完」加已找到的、還是只印那一句?這些命中要不要進 rows(進了會被算進 RETIRE-IF ① 的分母)、算不算進 `handle` 筆數?
2. block 模式:已找到的命中要不要印、要不要提供 ack 指令;只印「判不了」的話使用者連已知的舊句都看不到。
3. 〈做法〉4 只說 `timeout` 進完成率,沒說 timeout 那筆的 rows 怎麼算。
建議:寫死「timeout 時不記 rows、handle/listed 記 0」或「記已找到的、準度分母略過 timeout」。

## F13 gate=off 那句「這道檢查關掉了」之後,舊句檢查照跑
severity: minor
blocking: 否
引句:「gate=off → 印原來那句、不跑 c1–c5/probe,`rc_core` = 0」
file: `scripts/lumos:28258`(那句是「存量漂移檢查:這個專案把這道檢查關掉了(drift_check.gate=off),跳過」)
敘述:
1. 已經在設定檔寫 `drift_check.gate=off` 的專案,升級後預設 old_sentence=warn 會照跑:先印「這個專案把這道檢查關掉了…跳過」,緊接著印一大段舊句檢查、最多多 30 秒。使用者看到的是自相矛盾的兩句。
2. 「互不牽連」是刻意的(〈做法〉3 與 S3 都寫了),但輸出那句沒跟著改。
建議:gate=off 那句在 old_sentence 不是 off 時改成「c1–c5 與回頭條件關掉了(drift_check.gate=off);舊句檢查另有開關 drift_check.old_sentence」。

## F14 「拆包的每個名稱」比參考實作寬,P4r3 驗收數字不保證同
severity: minor
blocking: 否
引句:「tuple/list 拆包的每個名稱」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:201`(`_assigns` 只收 `elts` 裡直接是 `ast.Name` 的一層,不收 `*rest`、巢狀 tuple)
敘述:
1. 輸入 `first, *rest = f()`:參考實作收 `first`,不收 `rest`(`Starred`);輸入 `(a, (b, c)) = x` 只收 `a`。計劃寫「每個名稱」,照字面的實作者會收 `rest`、`b`、`c`,S8 的三個例子都測不出差別。
2. `try: … except* E:` 在 Python 3.14 是 `ast.TryStar`,不是 `ast.Try` 的子類別,參考實作與計劃都會漏掉裡面的指派;計劃寫「模組層 `if`/`try`」沒排除也沒收。
3. 影響:多收會讓候選「消失」判定少列(方向是漏報,而且只在 tuple 有星號時),不影響驗收數字的量級,但「驗收以 P4r3 為準」與字面「每個名稱」之間有縫。
建議:寫「拆包只收一層、只收直接是名稱的元素(照參考實作),`*rest` 與巢狀不收」,S8 加 `first, *rest = f()` 一例。

## 條款可測性逐條(輸入輸出寫清楚沒)
- S1:可測。輸入(a.py、b.py、tests/test_x.py、governance/eval/x.py、build/x.py 各種擺法)與輸出(算/不算)都寫了。
- S2:可測。逐字眼可對 54 個;例子含括號與切句。缺:撤除節在「第一個標題之前」的行為(參考實作的 `_mid_retire` 以層級 0 處理,標記會一路撐到全篇尾;計劃寫「一級標題底下就是到整篇尾」,沒寫標題之前)。
- S3:可測,四種組合寫得清楚。
- S4:可測。
- S5:大致可測,見 F9。
- S6:欄位名見 F3、記帳條件見 F1、rows 大小見 F4。
- S7:可測(名稱含分號、空白、`$()`);我核對 `_drift_sh` 的正則會對這些加引號。
- S8:可測,見 F14。
- S9:可測。
- S10:除「第 2 批前用完」的接縫外可測(F9)。
- S11:六個子情境擠在一條、一支測試;可測但失敗時不好定位(建議拆,不擋)。
- S12:可測。`drift fix … --kind m1` 走既有 `_drift_fix_args_err` 的「--kind 只能是 c1/…」,我核對 argparse 的 `--kind` 沒設 choices,會走到那句。
- S13:見 F5。

## 已讀,無 finding
〈範圍〉〈回退〉〈實務隱患〉〈合約候選〉:已讀,除已在上面各條裡提到的之外沒有另外的 finding。
〈做法〉1 的起點三種情況、程式檔範圍、路徑類、形狀過濾、快取位置與鍵:已讀,與參考實作與既有函式(`_note_audit_resolve`、`_drift_oids`、`_drift_list`、`_nodehome_code_kind`)核對一致。
〈做法〉2 的整字、名稱先篩(ASCII 切詞)、54 個字眼、分層:已讀,與參考實作 `_mk_rx`、`_clause_has_hist`、`HIST_WORDS2`、`homes_any` 一致。
合約行(★INVARIANT★)本輪我這個鏡頭沒有另外判。

最高等級:major;blocking 共 2 條
