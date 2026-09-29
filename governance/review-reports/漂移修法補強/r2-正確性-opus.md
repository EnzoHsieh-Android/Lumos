severity: major

# 設計審 r2:正確性-opus

審材:`governance/review-reports/漂移修法補強/r2-snapshot.md`(凍結稿)。對照 repo:clone-ns @ 9c240a56(實驗在自己的 `git clone --shared` 副本裡做,沒動 repo)。

## F1 第④道只擋「原有的項不見」,擋不到「別人刪掉的項被照貼的舊指令加回來」和「別人新加、含關鍵詞的項被蓋掉」,併發那一段說的保護不成立
severity: major
blocking: 是
引句:「證據頁到寫入之間有人改過 valid_under,由做法第 2 節第④道擋下」
file: `scripts/lumos:27769`
file: `scripts/lumos:27820`
file: `scripts/lumos:26376`

1. 第④道只查一個方向:現在的項(不含關鍵詞的)要全部出現在 `--values` 裡,也就是「現在的項 ⊆ `--values`」。反方向(`--values` 裡多出來、現在已經沒有的項)不查。
2. 情境一,刪掉的項被加回來:甲會談印出證據頁,valid_under 是〔「舊前提 X」、「乙 未提交」〕,預填指令是 `--values "舊前提 X" "<整項新內容>"`。乙會談發現 X 過期,用 `lumos set` 整欄改成〔「乙 未提交」〕並提交。甲把證據頁的指令填好照貼:乾淨檢查過(已提交,跟 HEAD 一樣,見 `_drift_fix_clean_err`);`_drift_current_finding` 過(c4 還在);①②③過;④ 現在不含關鍵詞的項是空集合,過;⑤過 → 寫成〔「舊前提 X」、「乙 已提交…」〕,c4 消失,修復帳也記了一筆。乙刻意刪掉的條件沒有任何提示就回來了。
3. 情境二,新加的項被蓋掉:乙會談在同一欄多加了一項「丙 未提交的 Windows 分支」並提交。甲照貼的指令沒有這一項;④ 把含關鍵詞的項整個排除(第④道寫明只查「不含那三個詞的每一項」),③ 又不准 `--values` 含這三個詞 → 寫成功,丙整項消失,寫後驗證(`_drift_no_kind("c4")`)反而因為丙不見了而判「已處理」。
4. 同一個人也會踩到,不需要兩個會談:看完證據頁 → 先用 set 刪掉一項並提交 → 回頭貼舊指令。
5. 鎖內的指紋比對(`_drift_fix_write`)只保護「判定到寫入」這一段;證據頁是另一次執行,兩次執行之間沒有任何綁定。所以〈實務隱患〉併發那一句寫的「由做法第 2 節第④道擋下」只對「有人新加了不含關鍵詞的項」成立。
6. 修法二擇一:(a) 證據頁把目前 valid_under 各項算一個短指紋,印進預填指令(例 `--expect <指紋>`),寫入前指紋對不上就擋,叫人重跑證據頁;(b) 第④道改成兩個方向都查:含關鍵詞的項數要跟證據頁一樣,而且 `--values` 裡「不在現在各項裡」的值不能多過含關鍵詞的項數。(a) 比較簡單,也不會擋到把一項拆成兩句的正常用法。條款 [S2] 要一起補。

## F2 第④道的「每一項」沒寫清楚怎麼展開;另外,讀的一側看不到的內容照樣會被整欄覆蓋悄悄刪掉,也有「②不准、④又要求」卡死的情況
severity: minor
blocking: 否
引句:「現在 valid_under 裡不含那三個詞的每一項,都要原文一字不差出現在 `--values` 裡」
file: `scripts/lumos:27958`
file: `scripts/lumos:13775`
file: `scripts/lumos:15153`

1. 「項」有兩種讀法,結果不一樣。現行 `_drift_c4_print` 用 `as_list(...)` 取各項;第 2 節只把證據頁改成 `_conds`,第④道沒講用哪一種。實測:`valid_under: |` 底下兩行〔「甲條件 A」、「乙 未提交 工作樹」〕,`as_list` 得到一項(含換行,也含「未提交」),`_conds` 得到兩項。照 `as_list` 做的話,整個區塊因為含關鍵詞被第④道排除 →「甲條件 A」不在 `--values` 裡也不會擋 → 被悄悄刪掉。這正是第④道括號裡說要防的「區塊寫法被拆開的項目靜默刪掉」。要寫明「用 `_conds` 展開,跟證據頁同一份清單」。
2. 讀的一側看不到的東西,第④道也保護不到。實測清單項下一行的接續行(`  - 甲` 下面接 `    接續同一項`,標準 YAML 裡算甲的一部分)與清單裡的 `# 註解`:本工具讀出來只有〔甲、乙 未提交〕。用 `_set_conditions_locked`(也就是拆出來的 `_conditions_rewrite` 那套算法)整欄改成〔甲、乙 在提交 abc 驗過〕之後,接續行與註解都不見了,沒有任何提示。drift fix 還會替這次寫入記一筆修復帳,看起來像審過。〈誠實界線〉要補一句「本工具讀不到的內容(清單項的接續行、註解)整欄改寫時會消失」;或者在整欄範圍內只要有不是 `- ` 開頭的非空行就擋,叫人用 set。
3. ② 和 ④ 會互相卡死。現有某一項(不含關鍵詞)含 `<sha>`、`<卷證>` 或 U+2028,這很可能發生:舊流程用 `lumos set` 貼範本句,set 不擋 `<sha>`、`<卷證>`。④ 要求它原文出現,② 又擋它。訊息只說「換成真的內容再跑」,換掉之後換成 ④ 擋。最後只能走 set,但沒有一則訊息講清楚這條路。
4. 重複項:現有〔A、A、乙 未提交〕,給〔A、新句〕就過 ④(只看有沒有出現),一個 A 被刪掉。影響小,寫明「重複項按次數算」或「重複項合併」其中一種就好。

## F3 乾淨檢查排在五道擋之後還是之前,前後文互相矛盾
severity: minor
blocking: 否
引句:「之後照 drift fix 原流程:乾淨檢查(帶 `--dry-run` 時不做,同既有慣例)」
file: `scripts/lumos:27779`
file: `scripts/lumos:28168`

1. 第 2 節的帶 `--values` 那段和 [S2](「過了才做乾淨檢查、鎖內寫入、寫後驗證」)都說:①到⑤擋完才做乾淨檢查。
2. 同一節的接線清單卻寫「`_drift_fix_load` 的條件改成 c4 且沒帶 `--values`」。乾淨檢查在 `_drift_fix_load` 裡(第 27820 行附近),而 `cmd_drift_fix` 先跑 `_drift_fix_load`,再跑 `_DRIFT_FIX_COMPUTE[kind]`,也就是 `_drift_fix_c4` 與五道擋。照接線做,實際順序是乾淨檢查 → 五道擋,跟文字與 [S2] 相反。
3. 會出錯的輸入:筆記有別人留下的未提交改動,同時 `--values` 還含「未提交」。照接線做印的是乾淨檢查的訊息,照 [S2] 做印的是第③道的訊息。兩種都回 2、不寫檔,但依 [S2] 寫的測試若斷言訊息,會跟照接線寫的實作對不上。二擇一寫死;照接線的順序改 [S2] 最省事,因為其他種類的既有慣例也是這個順序。

## F4 `--values=-x` 只在只有一項時有用;證據頁預填的指令遇到 `-` 開頭的項會直接被 argparse 退掉
severity: minor
blocking: 否
引句:「的單一項以 `-` 開頭時要寫成 `--values=-x`(argparse 的限制)」
file: `scripts/lumos:27630`

1. 實測(argparse,`--values` 設 `nargs="+"`):`--values=-x b` → `unrecognized arguments: b`。也就是用了 `=` 寫法,`--values` 就只收那一個值。c4 是整欄重寫,多半有好幾項,這個退路在最常見的情況下根本用不上。
2. `--values a -x` → `unrecognized arguments: -x`;`--values a -- -x` 也一樣失敗。`-1`(像負數)和 `-O2 編譯`(含空白)反而收得進去。所以真正收不進去的是「`-` 開頭、不含空白、不像數字」的項。
3. 證據頁的預填指令:`_drift_sh` 的白名單包含 `-`,所以 `-x` 這種項原樣印出、不加引號(就算加了引號,shell 也會拿掉)。人照貼 → argparse 回 2,訊息也講不到原因。
4. 修法:〈誠實界線〉改成照實寫(「有 `-` 開頭又不含空白的項時,drift fix 收不了,改用 set」,而且要先確認 set 的位置參數收不收得了);證據頁遇到這種項時,不印可照貼的指令(比照「含控制字元」那一條逐項列出)。

## F5 `_drift_fix_hint` 的 c4 提示沒規定佔位字長什麼樣;萬一印成 `--values "<各項…>"`,①②都擋不到
severity: minor
blocking: 否
引句:「`_drift_fix_hint` 的 c4 說明改成指到 `--values`」
file: `scripts/lumos:27622`
file: `scripts/lumos:27653`

1. drift check、scan、doctor、計劃收尾的連帶待辦,都從 `_drift_fix_hint` 拿 c4 的提示。〈範圍〉自己把指令寫成 `drift fix --kind c4 --values <各項…>`。
2. 佔位字的防線只有兩道:① `_SET_COND_SLOT`(`<整項新內容>`),② `_DRIFT_PLACEHOLDER_RE`(只認 `<為什麼…>`、`<sha>`、`<卷證>`)。`<各項…>`、`<新內容>` 都不在裡面。
3. ⚠ 情境(前提:提示照〈範圍〉那種寫法印):valid_under 只有一項「在未提交的工作樹上驗」,照貼 `lumos drift fix X 5 --kind c4 --values "<各項…>"`。①②都沒擋;③沒有關鍵詞;④ 沒有不含關鍵詞的現有項要比;⑤過 → 寫成 `valid_under: "<各項…>"`,c4 消失,修復帳記一筆。
4. 修法:寫明 c4 提示只印「不帶 `--values` 的證據指令」加上說明;或者規定提示裡的佔位字一定用 `<整項新內容>`(① 擋得到)。

## F6 列出「同一個提交加進來的檔」時沒處理改名,跟它自稱照抄的既有寫法不同,結果還會隨使用者的 git 設定變
severity: minor
blocking: 否
引句:「_nodehome_git(root, "show", "-z", "--name-only", "--diff-filter=A", "--format=", <提交>)」
file: `scripts/lumos:24485`
file: `scripts/lumos:24486`

1. 第 1 節說照抄「每支檔有家」那一段既有的寫法。既有的是 `("show", "-M", "--diff-filter=AR", "--name-only", "--format=", "-z", gl)`,改名也算;spec 只取 `A`。
2. 實測:前一個提交把卷證放在 `tmp/r1.md`,功能提交把它 `git mv` 進 `governance/review-reports/X_plan/r1.md`,同時加驗證紀錄。預設設定下 `git show -z --name-only --diff-filter=A --format= HEAD` 只列出 `docs/ver.md`,X_plan 不在「同提交」清單裡;加了 `-c diff.renames=false` 又列出來了。同一個 repo、同一個提交,只因為使用者的 `~/.gitconfig` 不同,就得到不同的「兩者」集合與範本句。
3. 修法:照既有寫法用 `-M --diff-filter=AR`,或者明確加 `--no-renames`,把結果固定下來。二擇一寫進 spec。

## F7 擴充 `_guard_settle_rewrite` 的回傳值:該跟著改的呼叫端沒列全,「已是轉正後說法」的集合什麼時候算也沒定義
severity: minor
blocking: 否
引句:「兩處用同一支組字函式」
file: `scripts/lumos:12290`
file: `scripts/lumos:12537`
file: `scripts/lumos:28010`
file: `scripts/lumos:12556`

1. `_guard_settle_rewrite` 有兩個直接呼叫端,都照兩個值解包:`_guard_pass_rewrite` 的 `new, missing = …`,以及 `_guard_settle_record_lines` 的 `new, missing = …`。改成回三個值而不同步改,這兩處會丟 ValueError(解包數量不對)。往下再傳一層還牽連三處:guard settle 已 pass 那一路(`_guard_settle_pass`)與 c1 解包 `_guard_pass_rewrite` 的四個值;pending 轉正那一路(`_guard_settle_record`)與 c5 解包 `_guard_settle_record_lines` 的三個值(`_drift_fix_c5` 在第 28010 行)。spec 的做法和〈回退〉都只提 `_guard_settle_rewrite` 本身、`_drift_fix_c1`、`guard settle`,沒提 `_guard_pass_rewrite`、`_guard_settle_record_lines` 的回傳形狀要跟著改,也沒提 c5 要不要跟著改。既有測試在第 54201 行攔 `_guard_settle_record_lines`,會把回傳值原樣傳下去,不受影響。
2. 印「找不到」的地方其實有三處,不是兩處:`_guard_settle_pass`、`_guard_settle_record`(兩者都走 `_guard_settle_missing_say`),以及 `_drift_fix_c1` 的 msg。
3. 集合的語意有歧義。settle 那一種的認法是「正文任一行符合 `_GUARD_MANUAL_SETTLED_RE`」,但 settle-del 的情境(settle 句下一行就是手補的已轉正段)兩個條件同時成立:工具刪掉了 settle 句,又被算進「已是轉正後說法」→ 印出「已經是轉正後的說法,不用改」,跟實際做的事(刪了一行)相反。TEST 預告句和已轉正的 TEST 行同時存在時也一樣。要寫明:集合只收「沒有預告句可改、但有轉正後說法」的種類,也就是從原本會落進 missing 的種類裡分出來。
4. `_GUARD_MANUAL_SETTLED_RE` 會命中任何以「日期 已轉正」開頭的正文行(例「2026-09-30 已轉正的合約還有三條沒審」)。只影響訊息措辭,不另立一條。

## F8 第 5 節點名的三處內嵌寫法位置寫錯;照名字去找的話,會找到一支不能換的函式
severity: minor
blocking: 否
引句:「這個內嵌寫法已有三處(推送前小改動判定、筆記形狀擋兩處)」
file: `scripts/lumos:18365`
file: `scripts/lumos:24477`
file: `scripts/lumos:24609`
file: `scripts/lumos:17833`

1. `frozenset() if _is_toolchain_repo(root) else _vendored_state(root, …)[0]` 實際出現在:`_stack_ext_counts`(健檢的技術棧統計,`ref=None` 看工作目錄)、`_nodehome_ledger`(`ref=""`)、`cmd_home_check`(`ref="" if staged else tip_where`)。後兩處是「每支檔有家」,不是「筆記形狀擋」;筆記形狀擋(`_ns_*`)一處都沒有呼叫 `_vendored_state`。PRIOR-ART ③ 的「同筆記形狀擋的用法」也是同一個錯。
2. 「推送前小改動判定」用的是 `_vendored_skip`(起點、終點兩個版本都看,起點原封不動、終點刪掉的也跳)。那不是這個內嵌寫法;照 spec 改成呼叫 `_vendored_intact` 會少掉拆除工具鏈那一路的跳過,行為會變。
3. 三個真正的呼叫處改成 `_vendored_intact(root, ref)` 是等價的:短路順序相同,`ref=None` 與 `ref=""` 照傳就好。我判這一步本身沒問題,只要把點名改對、寫明 `_vendored_skip` 不動。

## F9 delguard 的治理事件沒有 detail 欄;逾時降級那一路也不會記跳過數
severity: minor
blocking: 否
引句:「記在既有的 delguard 治理事件的 detail 裡」
file: `scripts/lumos:29404`
file: `scripts/lumos:29417`

1. `_delguard_log_result` 與 `_delguard_log_degraded` 寫的事件欄位是 `gate`、`kind`、`hard`、`nodes`、`note`,沒有 `detail`(本 repo 的治理帳 922 筆 delguard 事件全是這個形狀)。`detail` 是別的閘在用的欄位。要寫明是新加 `detail` 欄,還是接在 `note` 後面。RETIRE-IF ② 的量法要照著抓得到才算數。
2. 跳過判定做完之後才逾時的話,走的是 `_delguard_log_degraded`,這一路不會記「跳過幾支、少抽哪些名稱」。RETIRE-IF ② 的「累計 ≥20 次」會少算。要寫明降級事件也帶,或者寫明只有跑完的才算。

## 各節核對(沒有 finding 的部分)

- 第 2 節拆 `_set_conditions_locked`(照重點逐項對過):現行的順序是佔位字 → 空值 → 多行 → `load_raw_for_edit`(BOM、CRLF 丟 ValueError)→ `fmt_scalar`(`_yaml_quote` 丟 ValueError)→ `atomic_write_verify`(RuntimeError)。後三種例外都由 main 的 `except (ValueError, RuntimeError)` 印成「擋下:{e}」、回 2(第 38117 行附近)。拆開後:值檢查、`_conditions_rewrite` 的錯誤改由 `_set_conditions_locked` 自己印「擋下:<訊息>」、回 2;讀檔錯與寫入錯照舊往外丟。stderr 的字、先後順序、回傳碼都一樣;set 之後只有 `args.key == "status"` 才有後續動作,valid_under 不受影響。多行那句的 `how`:set 傳 `lumos set <筆記> {key}` 就能一字不差還原。判定:等價,無 finding。唯一的小瑕疵是 drift fix 那邊的 `how` 字樣「drift fix … --kind c4 --values」少了開頭的 `lumos `,是措辭問題,不另立。
- 第 2 節 ②③⑤、`check`、`handled`、`texts=[]`:c4 的判定(第 26376 行)是把 `as_list` 各項用空白接起來、區分大小寫地找子字串。③ 逐項用同一組詞擋,接起來的空白也不會拼出關鍵詞 → 寫後「c4 消失」在 ③ 過了之後一定成立。開頭欄位在筆記形狀擋裡屬於 other 區,不做逐行檢查(第 25199 行附近),所以 `texts=[]` 跟提交時的閘一致。`_drift_fix_args_err` 的 `o.get(k) not in (None, False)` 遇到 list 值也判得對。無 finding。
- 第 1 節其餘:`_plan_first_commit` 不跟改名(`git log --diff-filter=A` 限定新路徑,改名那次會被當成新增),spec 的描述正確;`_nodehome_split_z` 拆 `-z` 輸出實測正確;shallow 由既有檢查擋。除 F6 外無 finding。
- 第 4 節 c3 的理由:`_drift_fix_args_err` 已經對所有種類套用 `_drift_fix_reason_ok`;`_drift_placeholder_err` 現在在 c2(`_drift_fix_c2_args`)與 `_drift_ack_args_err` 用,屬實;補的那一行會進 `texts`,照樣過筆記形狀擋。已讀,無 finding。
- 第 5 節其餘:工具自裝檔共 17 支,讀索引 `git show :<檔>` 17 次,在 15 秒的剩餘時間內沒問題;`skip` 只影響被跳過那支檔自己的回收表(回收表本來就是逐檔算的),不牽連別的檔。除 F8、F9 外無 finding。
- 第 6 節、條款、回退:除上面各條牽連到的部分外,已讀,無 finding。

## ★INVARIANT★ 合約逐條

- guard-kill「guard kill 回傳碼的優先順序」:這份設計只改 guard settle 與 c1 的訊息,沒碰 `guard kill` 的執行與回傳碼 → 不影響。
- guard-kill「guard kill --json 成功時 stdout 恰一行 JSON」:同上,沒碰 guard kill 的輸出 → 不影響。
- 存量漂移守衛、lumos-cli-write、delguard 沒有 ★INVARIANT★ 行。lumos-cli-write 的 WHY「set 擋 `<整項新內容>`」綁 `t_drift_fix_c4_evidence_then_replace`;spec 保留那一段,① 也照舊由 set 共用 → 不破壞。

## 實務隱患(逐類)

- 資料遺失:碰到。整欄覆蓋會刪掉讀的一側看不到的內容,第④道也只查一個方向(F1、F2)。
- 併發:碰到。鎖與指紋只涵蓋一次執行裡面;證據頁與寫入之間沒有任何綁定(F1)。
- 守衛面:碰到。delguard 跳過紀錄的欄位和降級路徑(F9);`_vendored_intact` 點名的位置(F8)。
- 資安:照 spec 走 `_drift_sh` 與 `_esc_clean`,無新洞。`-` 開頭的項屬於能不能用的問題,不是資安問題(F4)。
- 相容與混版:修復帳多出的欄位舊版會忽略;`_guard_settle_rewrite` 回傳形狀要同步改(F7)。
- 效能:git 查詢兩次,另讀索引 17 次,都有逾時,無問題。
- 不可逆、金流、對外送出:無。只寫本機筆記與帳,乾淨檢查保證 git 退得回來。

最高等級:major;blocking 共 1 條
