# 舊句檢查_計劃 前掃報告(設計審首輪前)

只讀。讀過 `scripts/lumos`(clone-ns)的 `_drift_check_core`、`_drift_probe_check`、`_drift_probe_changes`、`_drift_config`、`cmd_drift_check`、`_drift_report_must`、`_drift_print_findings`、`_drift_fix_hint`、`_drift_print_hints`、`_drift_split_acked`、`_drift_ack_key`、`_drift_ack_args_err`、`cmd_drift_ack`、`_drift_load_acks`、`_drift_old_reason`、`_gate_event` / `_gate_event_or_warn`、`_esc_clean`、`_note_audit_resolve`、`_lens_push_base`、`load_symbol_profile` / `NEG_LEXICONS`、`_notelines_regions`、`_visible_lines`、`_drift_py_names`、`_drift_probe_is_py`、`_shebang_line_is_python`、`_drift_gate_doctor_lines`、`cmd_drift_scan`、exam/history 三處呼叫點,以及實驗程式 `old_sentence_exp.py` 的字眼表、撤除節、分層段與報告。

## ① 未定義的詞

**①-1**
- 計劃原句:「`m1` 的模式獨立一個開關 `drift_check.old_sentence`(warn/block/off,沒寫=warn),跟既有 c1–c5 的 gate 分開」與〈範圍〉「(與 scan 的推送範圍模式)」
- 問題:「scan 的推送範圍模式」不存在。`drift scan` 的參數只有 `--at/--json/--budget`(argparse `drs`),沒有 `--diff`,也不呼叫 `_drift_check_core`。讀者查不到這個「模式」是什麼。
- 建議:刪掉「與 scan 的推送範圍模式」;m1 只接 `drift check --diff`(與 exam/history,見④)。同時把〈做法〉3 的「scan 不帶範圍時不跑」改寫成「scan 不跑 m1」。

**①-2**
- 計劃原句:「要處理」「只列出」層(〈範圍〉〈做法〉〈條款〉大量使用)
- 問題:這兩個詞在 `_drift_check_core` 的回傳 `(must, listed, unknown)` 有意義,但計劃沒說 m1 的「要處理」與既有 c1(範圍內轉正)/probe 的「要處理」是同一個 `must` 清單。這會影響模式與回 1 的行為(見③-1、④-1)。
- 建議:〈做法〉3 加一句「m1 的要處理層進 `must`、只列出層進 `listed`」,或明說不進(另立回傳)。

**①-3**
- 計劃原句:「起點」「終點」「推送範圍照 `drift check` 既有的起點判法」
- 問題:既有起點判法是 `_lens_push_base` 再經 `_nodehome_clamp_base` 截到「上線點」,而且空樹起點時 `base=None`。計劃沒講「起點被截到上線點」與「base=None(新分支、找不到主線)時 m1 怎麼算」。起點沒有定義集合時,「起點有、終點無」恆為空,等於整次不判;讀者不知道。
- 建議:〈做法〉1 補一句「base 為 None(空樹)時 m1 不判,印一行說明」;〈誠實界線〉補「起點被截到 drift check 的上線點,上線點之前刪的名稱看不到」。

**①-4**
- 計劃原句:「字眼表=既有否定詞表+『撤、刪、拔掉、不帶、沒有、改成、原本、當時、叫、擴成、前身是、改名為』」
- 問題:「既有否定詞表」有兩個候選:`NEG_LEXICONS["zh"]` 常數,或 `load_symbol_profile` 依專案 `.lumos/config.json` 的 `neg_lexicon` / `neg_extra` 給的那份(en 專案會拿到英文表)。計劃沒指定用哪個。實驗程式用的是常數 `NEG_LEXICONS["zh"]`(`HIST_WORDS = tuple(LM.NEG_LEXICONS["zh"]) + ...`)。
- 建議:寫明「用 `NEG_LEXICONS["zh"]` 常數,不讀專案的 neg_lexicon」或「讀專案設定」二擇一;後者要補測試。

## ② 壞引用

逐一驗過:
- `[[Projects/舊句偵測實驗_計劃]]`、`[[Projects/存量漂移防線_計劃]]`、`[[Issues/存量筆記漂移三種機制_rtb根因回饋]]`、`[[Projects/先問世界_存量掃描裁定]]`、`[[Projects/漂移修法補強_計劃]]`、`lands_in: Systems/存量漂移守衛` 都存在。
- `old_sentence_exp.py`、`report-2026-09-30.md`、`_drift_check_core`、`_drift_fix_hint`、`_esc_clean`、`_drift_config` 前身概念的 `drift_check.gate`、`scripts/lumos`(無副檔名、shebang python)都存在。
- 條款裡的 `t_drift_m1_*` 六個測試名目前都不存在(`grep` 0 筆),屬待寫,不算壞引用,但要提醒:S1–S6 綁的是尚未存在的測試。

**②-1**
- 計劃原句:「〈回退〉…(同 [[Projects/漂移修法補強_計劃]]〈回退〉的做法)」
- 問題:連結存在、〈回退〉節也存在(第 78 行起),主要路徑段落確實是 `git revert --no-commit` 後帳本檔留現況。這一條通過,列在此只為說明已驗。
- 建議:無。

**②-2**
- 計劃原句:「REVISIT:2026-10-14 …(`grep '"m1"' docs/.governance-log.jsonl` …)」
- 問題:(a)目前該帳 `"m1"` 命中 0 筆,而治理事件的 `kind` 欄在 `_gate_event` 裡是「結果」(blocked/warned/acked/skipped-env/fix),不是發現種類;計劃要記 `kind m1` 是新用法,`grep` 可行但會與其他帳的 `"m1"` 字串(如 canary 帳)混,判準不穩。(b)更重要:本 clone 的 `scripts/hooks/pre-push` 與 `.github/` 都沒有 `drift check`(grep 0 筆),存量漂移守衛節也寫「還沒接線」。工具鏈自己不跑 drift check,兩週提醒帳就是空的,REVISIT 那天無數可看。
- 建議:REVISIT 的指令改成 `grep '"gate": "drift-check"' … | grep '"m1"'` 之類同時比 gate;〈做法〉補「先把 drift check 接進本 repo 的 pre-push 與 CI」為前置(或明說兩週帳只來自 rtb)。

**②-3**
- 計劃原句:〈範圍〉「既有 c1–c5 的 gate」
- 問題:`_DRIFT_KINDS = ("probe","c1",...,"c5")`,還有 probe;計劃沒提 probe 也共用 `drift_check.gate`。無關緊要,但「既有 gate 不管 m1」的說明應涵蓋 probe。
- 建議:寫成「c1–c5 與 probe」。

## ③ 範圍自相矛盾

**③-1(核心:模式開關)**
- 計劃原句:〈做法〉3「既有 `drift_check.gate` 不管 `m1`」「off 不跑」與〈條款〉S3「既有 gate 開關不影響 `m1`」
- 問題:`cmd_drift_check` 在讀到 `gate=off` 時直接 `return 0`,先於 `_drift_check_core`。所以 `gate=off` 且 `old_sentence=block` 時 m1 根本不跑,「gate 不影響 m1」為假。反向也有問題:`gate=block`、`old_sentence=warn` 時,m1 的要處理若進 `must`,`_drift_report_must(root, mode, must, ...)` 只吃一個 mode,會被 gate=block 擋(rc1),違反 S3「warn 時 m1 要處理不讓 check 回 1」。
- 建議:〈做法〉3 明寫控制流:m1 從 `must` 拆出來另走一條(自己的 mode、自己的印與記帳),`gate=off` 提前返回要改成「只跳過 c1–c5/probe」,並加測試(gate/old_sentence 四種組合)。

**③-2(核心:表態綁名稱)**
- 計劃原句:〈做法〉2「同一行提到好幾個消失的名稱只算一筆」對上〈做法〉3「表態:…路徑+原文+種類+名稱都要一樣才算已表態」與 S4「換一個名稱觸發同一行時照列」
- 問題:一行一筆、但表態綁一個名稱:那筆發現到底帶哪個名稱?兩個名稱同行時,ack 綁其中一個,另一個名稱是否算「換一個名稱觸發」而照列?若照列就不是「只算一筆」;若一筆帶名稱集合,則 ack 的 `--name` 只給一個就不夠。`_drift_split_acked` / `_drift_ack_key` 目前 key 是 `(path, text, kind)`,`_drift_print_hints` 去重 key 是 `(kind,path,line)`,都沒有名稱維度。
- 建議:二擇一寫死:(a) 一筆發現帶「名稱集合」,表態 `--name` 可重複、集合被涵蓋才算已表態(仿 c2/c3 的 related 涵蓋);(b) 一行×名稱各算一筆(改〈做法〉2 的計數)。

**③-3**
- 計劃原句:〈做法〉3「限時:…超過預算就停、印『舊句檢查這次沒跑完(時間到)』,不算要處理」
- 問題:既有預算機制是「判不了(unknown)算要處理」:`cmd_drift_check` 中 `if not must and not unknown: return 0`,`_drift_report_must` 在 unknown 存在時 block 會回 1,而且明寫「判不了就放行等於一條繞過的路」。計劃要 m1 例外,但沒說出走 `unknown` 以外的通道;若照 core 慣例把「超時」塞 `unknown`,在 gate=block 下會擋人,與「只提醒期間不讓它擋人」矛盾。
- 建議:〈做法〉3 明寫「m1 超時只印 stderr、不進 unknown」,並在〈誠實界線〉說明這是刻意與既有「判不了算要處理」相反的選擇及轉 block 時要不要改回。

**③-4**
- 計劃原句:〈條款〉S1「剖不動的檔不判並印出支數」與〈做法〉1「某一版剖不動…那支檔這次不判」對上〈做法〉1 「起點有、終點整個 repo 找不到」
- 問題:「終點」剖不動的檔,它的定義在終點集合中缺席,那些名稱在別處也存在時就會被誤判為「消失」;計劃只說「那支檔這次不判」,但沒說終點剖不動的檔所定義的名稱、被其他檔判為消失的情形怎麼處理(整個 repo 比法下,終點任何一支剖不動,都可能讓名稱看似消失)。
- 建議:〈做法〉1 明寫:終點只要有任何 Python 檔剖不動,涉及該檔在起點也定義過的名稱一律不判;或整次 m1 不判。

**③-5**
- 計劃原句:〈範圍〉做 ①「改到的 Python 檔在起點定義、終點整個 repo 都找不到的名稱」與 〈範圍〉不做「全歷史定義索引」及〈誠實界線〉「先加後刪…那種名稱看不到」
- 問題:輕微:〈做法〉「被刪或改名的舊路徑與它的檔名也算一個名稱」,但「消失」定義只說「同名定義」;路徑與 `--旗標` 要怎麼比「終點都找不到」沒寫(路徑=樹上不存在?旗標=終點任一 Python 檔的 `add_argument` 都沒有?)。
- 建議:〈做法〉1 補三類名稱各自的「消失」判準。

**③-6**
- 計劃原句:〈做法〉2「字眼表=…(列了 12 詞)」與 依據句「9 題擋到 7 題…13 題非漂移誤列 0 題」
- 問題:見④-6。字眼表與實驗量出數字的表不同,計劃拿實驗數字當現表的成績依據。

## ④ 機械宣稱驗語意

**④-1(核心:`_drift_check_core` 內加分支、判法/分層/模式)**
- 計劃宣稱:「`_drift_check_core` 在既有 c1–c5 與條件式之後跑;只在有範圍時跑」「〈回退〉m1 整段在 `_drift_check_core` 裡一個分支」
- 實際行為:`_drift_check_core` 回 `(must, listed, unknown)` 三個清單,無 mode 概念,且被四處呼叫:`cmd_drift_check`、`_drift_exam_probe`(約 28482)、`_drift_exam_one`(28513)、`--history`(28672)。exam 的 `noise` 直接取 `must` 筆數與 `unknown`(`noise = ... + len(unknown)`),在 core 加 m1 會讓考試與歷史重放的噪音數與「誤報要處理」計數都變,既有 exam 成績與 `存量漂移守衛` 的「預設改 block 三條門檻」量測基準被改動;m1 也不在考卷題型內。另外「有範圍時才跑」在 core 沒有現成參數(`base` 可為 None、`tip` 恆有),「有範圍」要另定義。
- 落差:計劃把 core 當「c1–c5+probe 的單一出口」,實際是共用給考試與健檢的純判定,且不知道 mode/名稱維度。
- 建議:m1 不放進 `_drift_check_core`,另立 `_drift_old_sentence_check(root, base, tip, vault_rel, deadline)`,由 `cmd_drift_check` 呼叫並自己分層、自己 mode;`exam --history` 要不要跑 m1 另寫。〈回退〉措辭跟著改。

**④-2(`_drift_fix_hint`)**
- 計劃宣稱:「`_drift_fix_hint` 對 `m1` 印…`lumos drift ack <節點> <行號> --kind m1 --name <名稱> --reason "…"`」「提示單一產生處」
- 實際行為:`_drift_fix_hint(kind, path, line)` 只有三個參數,沒有名稱;`kind=="probe"` 有專屬分支、其餘落到 `base = "lumos drift fix … --kind {kind}"`(預設分支會替 m1 印出 `drift fix --kind m1`,而 `drift fix` 的 `--kind` 只認 c1–c5、`_DRIFT_FIX_ALLOWED` 沒有 m1)。所以必須加分支、改簽名(拿到名稱)。同時 `_drift_report_must` 在提示後還有一段獨立印出的通用句「`lumos drift ack <節點> <行號> --kind {k} --reason "<為什麼照留>"`」(每個 kind 一行),對 m1 缺 `--name`,與單一產生處的宣稱衝突;`_drift_print_hints` 的去重鍵 `(kind,path,line)` 也吃不下同行多名稱。
- 建議:計劃列出要改的三個點:`_drift_fix_hint` 簽名、`_drift_report_must` 的通用 ack 行對 m1 用同一產生處、`_drift_print_hints` 去重鍵。

**④-3(drift ack 的比對)**
- 計劃宣稱:「表態:m1 的表態多記觸發的名稱(name),比對時路徑+原文+種類+名稱都要一樣」
- 實際行為:`_drift_ack_key(path, text, kind)` 三元組;`_drift_split_acked` 對非 c2/c3(`_DRIFT_BOUND_KINDS`)直接 `k in keys`;`_drift_old_reason` 用「原文+種類」找舊理由;`_drift_load_acks` 以 `kind in _DRIFT_KINDS` 過濾;`drift ack` 的 `--kind` 是 argparse `choices=_DRIFT_KINDS`;`cmd_drift_ack` 對非 c2/c3 不驗「那一行現在真的是這種發現」(`_drift_current_finding` 只給 c2/c3 用)。計劃沒列的連帶修改:`_DRIFT_KINDS` 與 `_DRIFT_KIND_NAMES` 都要加 m1(`_drift_print_findings` 用 `_DRIFT_KIND_NAMES[f['kind']]`,缺會 KeyError);`_DRIFT_KINDS` 加 m1 後 `drift scan` / doctor 的 `for k in _DRIFT_KINDS` 迴圈與計數(28357–28401)會多出 `m1 0`;m1 的 ack 因為判定要範圍,無法像 c2/c3 在 ack 當下驗證那一行真的是 m1(可 ack 任何一行);`_drift_old_reason` 沒有名稱維度。
- 建議:〈做法〉3 補「`_DRIFT_KINDS`/`_DRIFT_KIND_NAMES` 加 m1、scan/doctor 迴圈排除 m1、`--name` 在 m1 必填/其他 kind 禁用、m1 ack 不驗行當下狀態(誠實界線寫明)」。
- 〈回退〉的「舊版會忽略不認得的種類」:對表態檔屬實(`_drift_load_acks` 過濾 kind),對治理事件也屬實(`kind` 是自由字串);此句通過。

**④-4(drift check 的時間預算)**
- 計劃宣稱:「`m1` 共用 drift check 既有的時間預算;剖檔與比對超過預算就停…」
- 實際行為:`cmd_drift_check` 建 `deadline = monotonic() + _DRIFT_BUDGET_SEC(60)` 傳給 core;core 內每一步前都檢查;`_DRIFT_BUDGET_SEC` 是 60 秒。m1 在 c1–c5 與 probe 之後跑,可用的是「剩下的預算」,前面用掉多少 m1 就少多少;冷快取實測 3.6–7.4 秒,通常沒問題,但 rtb 新分支首推曾實測 67 秒(見存量漂移守衛 PITFALL)時,m1 幾乎必超時。「共用」是屬實的,但「停下不算要處理」與既有預算語意相反(見③-3)。單次 git 呼叫上限 20 秒、不會被打斷,這點對「剖檔」不適用(ast.parse 在 Python 內不可中斷)。
- 建議:寫明 m1 的預算檢查點(每支檔剖之前)與「in-process 剖檔不可打斷,最壞多出一支檔的時間」。

**④-5(`.lumos/config.json` 讀被推送頂端那份)**
- 計劃宣稱:「`drift_check.old_sentence`(`.lumos/config.json`,讀被推送頂端提交的那份,同既有 gate 的讀法)」
- 實際行為:屬實:`cmd_drift_check` 用 `_drift_config(_nodehome_reader(root, tip)(".lumos/config.json"))`。但 `_drift_config` 只回 `(gate, warnings, explicit)`,只認 `gate` 鍵,`drift_check` 不是物件或 gate 非法時整組退回預設;要讀 `old_sentence` 需擴充這支(否則第二支自己讀同一個鍵,存量漂移守衛節明寫過「不另開第二支讀同一個鍵」的決定,代碼審 r4)。另外「同一個提交把開關改 off 放過自己」的既有 RULE(2026-09-29,開關讀頂端)對新開關同樣成立,計劃〈實務隱患〉沒提。`_drift_gate_doctor_lines` 也只唸 gate,不唸 old_sentence。
- 建議:〈做法〉3 寫明「擴 `_drift_config` 回傳 old_sentence」與 doctor 提醒是否要補;〈實務隱患〉引用該 RULE。

**④-6(既有否定詞表、字眼表)**(核心:判法本身)
- 計劃宣稱:「字眼表=既有否定詞表+『撤、刪、拔掉、不帶、沒有、改成、原本、當時、叫、擴成、前身是、改名為』;英文字整字比」;「借 `scripts/lumos` 既有的」
- 實際行為:(a)既有否定詞表是 `NEG_LEXICONS["zh"]`(22 詞,含 ascii 的 dead/removed/deleted/…),Check Y 用**子字串**比(`any(k in _ln for k in _NEG)`),不是整字;整字比是實驗程式自己的 `HIST_RX`。(b)實驗量成績用的字眼表 `HIST_WORDS` 是 zh 表 + 「撤除、撤掉、拿掉、原寫、原本、原先、不再、舊版、舊的、刪除、刪掉、取代、搬到、搬去、改為、改叫、改成、曾、前身、撤、刪、拔掉、去掉、不帶、沒有」,**不含**「當時、叫、擴成、前身是、改名為」,而且含計劃沒列的十餘詞(不再、舊版、取代、曾…)。也就是說計劃的表與實驗量過的表**兩邊都對不上**:少了 12 詞中的 5 詞未量、多了實驗用的 ~14 詞沒抄進來。(c)「叫」單字是危險詞:知識庫 `.md` 內含「呼叫」的行有 748 行、含「叫」984 行(全庫 6 萬行);而 `HIST_RX` 對非 ascii 詞是子字串,「呼叫 `foo()`」這類句子會整句被當歷史句豁免,直接讓 m1 大量漏報(如 「呼叫 `_drift_fix_hint`」提到已刪名稱的句子)。同理「沒有」「刪」「撤」單字在一般敘述中常見(「沒有…」多半是現況描述)。上一份計劃〈實驗結果〉寫的是「當時叫」「擴成」這類**詞組**,計劃卻拆成「當時、叫」。
- 落差:準度數字(7/9、16 筆、0 誤列)是另一張表的成績;計劃實作字眼表後這些數字不保證成立,「叫」可能把漏報推高。
- 建議:字眼表改用「當時叫」而非「叫」;把實驗程式的 HIST_WORDS 全表(含未列的詞)直接搬進模組常數並逐項列在計劃裡;上線前用實驗程式換成新表重跑 9 題+13 題+16 筆,把新成績寫進計劃;子字串/整字規則寫明只對 ascii 詞整字比。

**④-7(治理事件)**
- 計劃宣稱:「每次 check 對 `m1` 記一筆(gate `drift-check`,kind `m1`),note 帶要處理 N、只列出 M、剖不動 K」;〈範圍〉「沿用它的…治理事件」
- 實際行為:`drift-check` 在 `_KNOWN_GATES`;`_gate_event_or_warn` 寫得進去。但目前 drift check **只在有要處理或判不了時**記帳(`_drift_report_must` 內的 `blocked` / `warned`),列出全部零筆時不記任何事件,也沒有「每次 check 記一筆」的既有路徑;「kind」欄現在只放結果字串(blocked/warned/acked/fix/skipped-env),沒有放發現種類的先例。m1 記帳是新寫入點、新 kind 值。另有既有守衛:`LOOP_NOT_CLOSE_EVENTS` 對 code-loop/design-loop 的新 kind 要分類,drift-check 目前不受此限,但要確認 `lumos gov` 的統計不會把未知 kind 誤算(未讀 gov 統計碼,標為待驗)。`nodes` 欄現在放筆記名(最多 50),計劃的「每筆 `路徑:行 名稱` 最多 30 筆」塞 note,note 長度沒有上限說明。
- 建議:〈做法〉3 說明這是新寫入點(不是沿用),寫明 gate 與 kind 的取值及 warn 模式下要記帳的時機(零發現也記?);REVISIT 的 grep 指令對應改。

**④-8(`_esc_clean`)**
- 計劃宣稱:「筆記路徑與名稱印到終端前過 `_esc_clean`」
- 實際行為:`_esc_clean(v, limit=200)` 把控制字元(含 C1 8 位元控制碼、換行、ESC)換成空格並截到 limit;`_drift_print_findings` 已對 path、text、why 用它。屬實。註:治理事件 note 與 `--name`/`--reason` 內容是否過濾,計劃沒說(`_drift_placeholder_err` 與 `_drift_one_line` 是既有 ack 的擋法,ack 的 `--name` 需同樣一行檢查)。
- 建議:〈做法〉3 補「`--name` 走 `_drift_one_line` 檢查」。

**④-9(筆記分區與圍欄判定)**
- 計劃宣稱:「掃正文、摘要(summary)、決策欄;圍欄內不掃;`about_code`、`related` 這類開頭欄位不掃」;「分層:…摘要行 → 要處理」
- 實際行為:屬實:`_notelines_regions` 回 body/summary/decisions/other,decisions 內結構鍵行算 other;`_visible_lines` 剝圍欄(含未閉合圍欄後全視為 code)。實驗 `Note.scan_lines` 取 body/summary/decisions 且行在 `vis` 內。沒有落差。「行內程式碼內外都算」也與實驗一致(用整行)。
- 注意:decisions 區的行也走「摘要行 → 要處理」嗎?實驗只對 `regs=="summary"` 給要處理層(第 664 行),決策欄的句子只按「家」分層;計劃寫「或摘要行」,一致。

**④-10(抽定義用 `ast`、沿用既有)**
- 計劃宣稱:「抽定義用標準庫 `ast`」「shebang 是 python(例 `scripts/lumos`)」
- 實際行為:`scripts/lumos` 已有 `_drift_py_names`(函式/類別任何層、模組層指定,語法/記憶體錯回 None)、`_drift_probe_is_py`(.py 或 shebang 含 python 的判定,`_shebang_line_is_python` 只看首行含 `python`)。計劃要抽的集合比它多(巢狀指定名之外的類別層指定、`add_argument` 旗標、路徑),所以不能直接用 `_drift_py_names`;但語法錯處理(SyntaxError/ValueError/MemoryError/RecursionError)、BOM(讀檔用 utf-8-sig,存量漂移守衛 PITFALL)、`_drift_probe_is_py` 判定都是既有踩過的坑,計劃〈做法〉1 沒有引用。實驗程式是否處理 BOM 我沒逐行驗。
- 建議:PRIOR-ART ① 補「抽定義比照 `_drift_py_names` 與 `_drift_probe_is_py`(同一組 ast 例外、utf-8-sig、shebang 判定),不另寫第二份」,〈條款〉S1 加 BOM 與 MemoryError 的邊界測試。

**④-11(推送前掛鉤與 CI 接線)**
- 計劃宣稱:〈PRIOR-ART〉「沿用它的範圍、推送前掛鉤與 CI 接線」
- 實際行為:`drift check` 的接線是消費專案自己貼(doctor 的 `_drift_gate_doctor_lines` 提示「CI 在 note-audit 那步後面加…」);本 clone 的 `scripts/hooks/pre-push` 與 `.github/` 都沒有 `drift check`(grep 0 筆),`存量漂移守衛` 節寫「還沒接線」。所以「沿用它的接線」對工具鏈自己是空的(見②-2)。
- 建議:如②-2。

**④-12(定義快取、`<git 目錄>/lumos/`)**
- 計劃宣稱:「存在 `<git 目錄>/lumos/defs-cache.json`(不進版控;讀寫失敗當沒有快取)」「寫入走暫存檔再原子替換」
- 實際行為:`scripts/lumos` 有 `rev-parse --git-dir` 的用法(僅 `_cochange_transactions` 做 unborn 判斷),沒有把 `<git 目錄>/lumos/` 當快取目錄的既有慣例可沿用(我沒找到;若有請審查員指出)。多工作樹下 `--git-dir` 是各自的 `worktrees/<名>` 子目錄,`--git-common-dir` 才共用;計劃沒選。記憶「共用檔原子寫入:暫存→自驗→copymode→replace」是既有方法。
- 建議:寫明用 `--git-common-dir` 或 `--git-dir`,以及快取大小上限/淘汰(整個 repo 每個 blob 一筆,長期會膨脹)。

## 總結

| 類別 | 命中條數 |
|---|---|
| ① 未定義的詞 | 4(①-1 到 ①-4) |
| ② 壞引用 | 2 個實質(②-2、②-3),另 1 條「通過」不計;連結與檔名 0 條壞 |
| ③ 範圍自相矛盾 | 6(③-1 到 ③-6,其中 ③-6 併到④-6) |
| ④ 機械宣稱驗語意 | 12 條查驗,其中 9 條有落差(④-1、④-2、④-3、④-4、④-5、④-6、④-7、④-10、④-11/④-12 屬補充);④-8、④-9 屬實 |

**動到「核心裁定」的條(建議首輪審查優先處理)**
- 判法本身:④-6(字眼表與實驗量過的表不同,「叫」會吃掉含「呼叫」的整句,實驗成績不能直接套)、③-4(終點剖不動時的「消失」誤判)、③-5(路徑/旗標的消失判準未寫)。
- 分層:④-1(m1 放進 `_drift_check_core` 會被考試/歷史重放共用,改變既有 exam 噪音基準)、①-2。
- 模式開關:③-1(`gate=off` 提前返回讓「gate 不影響 m1」為假;單一 mode 傳給 `_drift_report_must` 使 gate=block/old_sentence=warn 仍會擋)、③-3(超時不算要處理與既有「判不了算要處理」相反)、④-5(`_drift_config` 要擴充)。
- 表態綁名稱:③-2(一行一筆 vs 綁單一名稱)、④-3(key、`_drift_split_acked`、`_DRIFT_KINDS`、`_DRIFT_KIND_NAMES`、ack 不驗行)、④-2(通用 ack 提示缺 `--name`)。
- 其他非核心但會讓兩週提醒期落空:②-2 / ④-11(工具鏈自己沒接 drift check)、④-7(治理事件是新寫入點)。
