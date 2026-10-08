severity: minor

## F1 _drift_config 擴充沒寫非法值與非物件時 old_sentence 的退回值,也沒寫回傳形狀
severity: minor
blocking: 否
引句:「`_drift_config` 擴充,多回 `old_sentence` 的值(同一支讀同一個鍵,不另開第二支;讀被推送頂端提交的 `.lumos/config.json`,同既有 gate)。」
file: `scripts/lumos:28196-28223`
1. 現況 `_drift_config` 回三元組,兩個呼叫端(`cmd_drift_check` 的 `mode, warns, _explicit = …`、`_drift_gate_doctor_lines` 的 `mode, cfg_warns, explicit = …`)和測試(`scripts/test_lumos.py:51580` 的三變數解包)都照三個接。spec 只說「多回」,沒說追加在尾端、也沒說三處要同步改;實作者若改成四元組,漏改一處就是 ValueError,doctor 或推送閘整段炸掉。
2. 各輸入的 old_sentence 退回值 spec 一個都沒寫,實作者得自己猜:(a) 沒有設定檔或 JSON 壞掉:現況 gate 退 warn,old_sentence 該退 warn(spec 說「沒寫=warn」,對得上)。(b) `drift_check` 不是物件(例 `"block"` 字串):gate 現況退 warn 並印提醒,old_sentence 也該退 warn,但要不要各印一句提醒沒定。(c) `old_sentence` 是 null 或 "Block"、"blocked" 這類非法值:必須退 warn 而不是 off 或 block(退 off 會靜默關掉檢查、退 block 會擋人),spec 沒寫。(d) `gate` 非法而 `old_sentence` 合法(或反過來):兩個開關是否互不牽連(一個壞了另一個照讀),spec 只在 S3 驗「四種合法組合」,沒驗壞值組合。
3. 現況 `explicit`(專案有沒有自己寫 `drift_check`)在只寫 `old_sentence`、沒寫 gate 時會是 True 且 gate 退 warn 且無提醒;doctor 因此會印「存量漂移檢查是 warn(.lumos/config.json 的 drift_check)」,把 gate 的提醒掛在其實是在設 old_sentence 的專案上。spec 沒說 doctor 的開關提醒要不要也講 old_sentence 的值(專案設 block 卻被 gate 的提醒講成 warn,會誤導)。
4. 舊版工具讀到有 `old_sentence` 鍵的設定檔:現況只取 `gate`,多的鍵忽略,回退安全(已驗)。

## F2 名稱欄的舊表態與缺欄相容沒定義,既有的通用比對分支會把它當作整行涵蓋
severity: minor
blocking: 否
引句:「一筆發現的名稱集合**全部**被同路徑同原文的 `m1` 表態涵蓋才算已表態(仿 c2/c3 的 related 涵蓋);新名稱觸發同一行 → 照列。」
file: `scripts/lumos:27404-27431`
1. `_drift_split_acked` 對非綁定種類(`_DRIFT_BOUND_KINDS` 只有 c2、c3)走 `keys` 集合,以 (路徑, 原文, 種類) 比對、完全不看名稱。spec 說「仿 c2/c3」,但沒寫要把 `m1` 加進 `_DRIFT_BOUND_KINDS` 還是另開分支。只加 `_DRIFT_KINDS` 而不動這裡(spec 種類登記一節只列了兩個常數),m1 就落進通用分支,任何同路徑同原文的 m1 表態不論名稱一律涵蓋,S4 的「新名稱觸發同一行時照列」失效。
2. 缺名稱欄的 m1 表態(手改帳檔、`--name` 寫入前的半成品、被截斷的一行)新版讀到怎麼算,spec 沒寫。c2/c3 的先例是「沒記 related 的不算數」,m1 應比照:缺欄或空集合一律不涵蓋任何名稱。`_drift_load_acks` 只驗 `path` 與 `kind`,不會替它擋。
3. `_drift_old_reason`(表態失效時借舊理由)只比 text 與 kind,不比路徑也不比名稱;m1 的樣板句在不同筆記間會一字不差,會把 A 表態的理由印給另一組名稱的發現,誤導「以前表態過」。spec 沒提。
4. 回退方向:舊版 `_drift_load_acks` 以 `kind in _DRIFT_KINDS` 濾掉 m1 行(已驗 `scripts/lumos:27397`),不會出錯;spec 〈回退〉這句成立。但〈回退〉清單漏列 `_drift_split_acked` 的 m1 分支、`_drift_ack_args_err` 的簽名(現在只有 kind 與 reason 兩參數)、`cmd_drift_ack` 與 argparse 的 `--name`、`_drift_print_hints` 的去重鍵、`_drift_report_must` 的通用 ack 行;照字面只拿掉清單上的項目,會留下引用不存在名稱參數的死碼或 NameError。

## F3 治理帳 old-sentence-blocked 沒帶 hard 旗標,現有消費端數不到;每次推送零筆也寫帳讓追蹤檔常髒
severity: minor
blocking: 否
引句:「每次 drift check 有跑 `m1` 就記一筆,gate `drift-check`,kind 依結果 `old-sentence-clean` / `old-sentence-warned` / `old-sentence-blocked` / `old-sentence-incomplete`」
file: `scripts/lumos:7119`
1. 「閘的動作」統計只認 `kind == "blocked"`(`scripts/lumos:7119`)與 `skipped` 開頭;spec 的 `old-sentence-blocked` 沒說要不要 `hard=True`,也不是統計認得的 kind,真的擋過人在該報表裡看不到。spec 自己的 REVISIT 用 grep 讀 kind 前綴,不受影響,但「閘的動作」報表對 m1 的擋下是盲的;spec 應寫明接受這點或改帶 hard。
2. 舊版工具讀到這些新 kind:治理帳 kind 是自由字串,舊版讀取端只在 kind 上做等值或前綴判斷,不會例外(回退句成立)。gate 名 `drift-check` 已在白名單(`scripts/lumos:6947`),不用新增。
3. 「零筆也記」意味著每次有範圍的推送都在追蹤的 `docs/.governance-log.jsonl` 多一行(工作樹現況已顯示它是 modified 狀態,別的事件也在寫,不是新性質);但 clean 是最常見結果,此後這檔在任何有 drift check 的專案都是每次推送後必髒。這對 rtb 更新工具後的第一次推送:所有推送前掛鉤跑完後工作樹多一個未提交改動,spec 沒提醒要不要一併提交,也沒說重複推送同秒同 note 的 clean 帳是否靠讀時去重折掉。

## F4 rtb 更新工具後第一次推送的行為沒交代:新分支首推常沒起點或預算用完,帳滿是 incomplete
severity: minor
blocking: 否
引句:「時間到:warn 模式印「舊句檢查這次沒跑完(時間到)」、不算要處理;block 模式照既有「判不了算要處理」」
file: `scripts/lumos:28250-28262`
1. 設定沒寫 `old_sentence` 時預設 warn,rtb 更新後第一次推送不會被擋(合乎預期),但 spec 自己承認 rtb 新分支首推曾在前段就用掉 67 秒,那類推送 m1 沒跑完,record 是 incomplete;起點是空樹也是 incomplete。這兩類在 rtb 兩週帳裡可能佔大宗,REVISIT 準度統計的分母沒說要不要排除 incomplete,否則「零筆」被誤讀成乾淨。
2. block 模式下「沒有起點版可比,不判」是放行,但同一節時間到卻是「判不了算要處理」,兩種 incomplete 在 block 下待遇不同、且 spec 引的理由(放行等於繞過)對空樹起點同樣成立;新分支首推就能繞過 block。這是誠實界線該寫的取捨,現在沒寫。
3. `LUMOS_SKIP_DRIFT_CHECK=1` 與 `_note_audit_resolve` 回非法時,現況整個 drift check 直接回,m1 也就不跑;spec 沒明講 m1 跟隨這個跳過(推薦跟隨)。

## F5 _DRIFT_KINDS 加 m1 的連帶逐處核對(判「不影響」或需要顯式排除)
severity: minor
blocking: 否
引句:「`drift scan` 與 doctor 逐種類計數的迴圈排除 `m1`;`drift fix` 不收 `m1`(`_DRIFT_FIX_ALLOWED` 不動),提示不會指到它。」
file: `scripts/lumos:28357-28363`
1. 用到 `_DRIFT_KINDS` 的地方共五處:(a) `_drift_load_acks` 濾種類(m1 需要進來,對);(b) `_drift_ack_args_err` 與 argparse `choices=_DRIFT_KINDS`(ack 可選 m1,對,但 `--name` 驗證要進 `_drift_ack_args_err`,它現在收不到 name);(c) `_drift_scan_print` 的計數字典、標頭 `if k != "probe"` 與逐種類迴圈:標頭要排除的是 m1 也是 probe 那個條件,spec 只說「排除」,實作要同時改標頭條件與 `counts`(不排除會印「m1 0」);(d) `_drift_doctor_lines` 寫死 `("c1"…"c5")`,不吃 `_DRIFT_KINDS`,不影響(已驗);(e) 考試(`drift exam`)按考卷題目的 kind 走,不迭代 `_DRIFT_KINDS`,不影響。
2. `_DRIFT_FIX_KINDS` 是獨立寫死的元組(`scripts/lumos:26257`),`_drift_fix_args_err` 用它擋,m1 傳進去得到「--kind 只能是 c1/…」而不是 KeyError,安全。但 `_drift_fix_hint` 末行 `return [base]` 是通用回退,不加 m1 分支就會對 m1 印出會被拒絕的 `drift fix … --kind m1`;spec 已要求加 m1 分支,此項只是確認一個漏做就翻車的位置,測試應釘。
3. `_drift_state_findings`(scan、ack 的 c2/c3、fix 共用)不會產出 m1,所以 `drift ack --kind m1` 若比照 c2/c3 走 `_drift_current_finding` 會恆回「現在不是 m1」;spec 已寫「ack 當下不驗」,一致,對。
4. 舊版讀新版的表態檔:m1 行被 (a) 濾掉;舊版 `drift ack --kind m1` 被 argparse 拒絕,exit 2,回退後不會殘留半功能。新版讀舊版表態檔(沒有名稱欄):舊檔本來就沒有 m1 行,無影響。

## 已讀,無 finding
- 〈回退〉的快取檔一句:舊版完全不讀 `defs-cache.json`,刪不刪都不影響;放 `--git-common-dir` 內不進版控,已成立。
- 〈實務隱患〉守衛面一句(同提交把 old_sentence 改 off 放過自己):跟 gate 同一取捨,設定被推送頂端讀取,已成立。
- 合約 ★INVARIANT★:本席只走回滾與相容鏡頭,未逐條展開 Systems/guard-kill 與 Systems/lumos-cli-write;判斷是 m1 只讀程式與筆記、寫的是表態檔與治理帳與快取(都是既有 `_drift_ledger_append` 與 `_gate_event_or_warn` 這兩個既有寫入路徑),若實作另開新寫入函式才需要重新對 lumos-cli-write 的鎖與原子寫合約。

最高等級:minor;blocking 共 0 條
