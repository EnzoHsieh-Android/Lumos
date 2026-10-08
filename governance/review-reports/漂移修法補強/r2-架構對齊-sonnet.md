severity: minor

# 設計審 r2 架構對齊席(sonnet)

## 四問

**問 1 分層與依賴方向:對齊。**
- drift 往下呼叫 guard、guard 不呼叫 drift:spec 把 c1/settle 的「已轉正」辨認與組字函式放在 guard 區段,`_drift_fix_c1` 呼叫它,方向與既有一致。file: `scripts/lumos:12274`(`_guard_pass_rewrite` 說明明寫「drift 往下呼叫 guard,guard 不呼叫 drift」)、`scripts/lumos:27834`(`_drift_fix_c1` 呼叫 guard)。
- c4 寫入:drift 區(27969)呼叫 set 區拆出來的 `_conditions_vals_err`、`_conditions_rewrite`(原在 `scripts/lumos:15128`),drift 往下用寫入層的函式;set 不呼叫 drift(`_SET_COND_SLOT` 在 14620 只是常數與註解提到 drift,是既有事實)。方向沒有反。file: `scripts/lumos:15128`、`scripts/lumos:27969`。
- delguard:`cmd_delguard_check`(29423)往下呼叫 `_vendored_state`(17765)、`_is_toolchain_repo`(17822),同樣是往下。無跨層直呼。

**問 2 命名與錯誤處理:大致對齊,有三處細節不一致(F3、F4、F6)。**
- `_conditions_vals_err(key, vals, how) → (vals, err)`、`_conditions_rewrite → (行, err)`:鄰居慣例是「回 (值, 錯誤訊息)、訊息不帶『擋下:』前綴、由呼叫端印」——`_guard_date_arg`、`_drift_fix_by`、`_drift_append_note`、`_guard_pass_rewrite`、`_drift_placeholder_err` 都是這樣。`how` 參數雖是新形狀,但同族的 `_drift_placeholder_err(text, what)` 已經用「帶一個描述字串進去組訊息」的寫法,不算第二種做法。file: `scripts/lumos:27622`、`scripts/lumos:12256`(`_guard_date_arg`)、`scripts/lumos:27881`。
- `_conditions_rewrite` 把 `fmt_scalar` 的 ValueError 轉成回傳的錯誤訊息:set 原本讓 ValueError 一路飛到主程式 `except (ValueError, RuntimeError)` 印「擋下:…」rc 2(`scripts/lumos:38121`),轉成回傳後由 `_set_conditions_locked` 印同樣的「擋下:<訊息>」回 2,對使用者看到的字與 rc 一致,[S3] 站得住。

**問 3 第二種做法:沒有 major;有兩處「近似第二份」(F1、F5)。**
- 第④道(現有不含三個詞的項要原文保留)在既有程式裡沒有鄰居可比,是新增的擋,不是拿另一套機制做同一件事;它用既有的 `_conds` 展開與 `_DRIFT_UNCOMMITTED_WORDS`,不算第二種。
- c4 寫入流程借 `_DRIFT_FIX_COMPUTE`、`res` 的 `check/handled/extra/texts` 形狀,與 c1、c2、c3、c5 一致;`_drift_fix_c5` 的 `extra={"test":...}` 是同款(`scripts/lumos:28010`附近)。
- `_vendored_intact` 抽出:見 F5(三處描述有誤,且旁邊已有另一支同族的 `_vendored_skip`)。
- c4 的 `check=lambda f: _conds(f.get("valid_under")) == vals` 與 `_set_conditions_locked` 裡的 `lambda f: _conds(f.get(key)) == vals`(`scripts/lumos:15170` 附近)是同一個判斷寫兩份;拆函式時沒有一起抽,屬小重複,不另立 finding(維護時漂移風險低,測試 S3、S8 會各自釘)。

**問 4 落點:合理。**
- lands_in 四篇都存在且 about_code 都列了 `scripts/lumos`(delguard 另列 `scripts/hooks/pre-commit`),對應:c4 卷證/寫入/c3 理由 → 存量漂移守衛;`_conditions_*` 拆函式 → lumos-cli-write;settle 訊息 → guard-kill(它的 WHY 已寫「改句、前提、轉正日期推導放 guard 這邊」,`docs/lumos-toolchain-knowledge/Systems/guard-kill.md:30`);刪除守衛 → delguard。存量漂移守衛的 responsibility 明寫「不負責 guard settle 本身與改句」,spec 把 settle 訊息落在 guard-kill 與該界線一致。
- 第 6 節文件清單只小缺兩點(F8)。

## Findings

## F1 c1 的「已轉正」辨認說成擴充既有 seen 判定,實際結構做不到;且會讓同一族辨認散成多處
severity: minor
blocking: 否
引句:「不另設第二支判定:辨認式跟寫入端(`_guard_settle_rewrite` 寫出的轉正後字樣)用同一組字樣常數、放在同一段」
file: `scripts/lumos:12134`
file: `scripts/lumos:12178`
1. `_guard_settle_rewrite` 的 `seen` 只在迴圈裡對「`_guard_prose_ops` 回的預告句行」累加(`ops` 只含預告句與 why-done、settle-del)。已經改成「TEST:[日期] 預告已轉正」或「預告當時為什麼還不做:」的行不是預告句,永遠不會進 `ops`,所以「在 seen 判定上多認三種」不是加幾個分支,而是要另掃一遍輸入行——那就是一支新的辨認,跟 spec 標榜的「不另設第二支」相反。
2. 同一族「已轉正」字樣目前已經散在三處:`_guard_planned_prose(settled_ok)` 認 WHY 行尾、`_guard_written_settled_dates`(12178)用 `_GUARD_MANUAL_SETTLED_RE` 與 `_GUARD_WHY_SETTLED_DATE_RE` 認日期、`_GUARD_SETTLED_TAIL_RE`。新增的辨認若各寫各的,會是第四處。
3. spec 說「同一組字樣常數」,但寫入端現況是把「TEST:[…] 預告已轉正,合約改由…」、「預告當時」、「(… 已轉正)」直接內嵌在 f-string(`scripts/lumos:12152-12160`),沒有常數可共用;要真的共用就得改寫入端四個分支,spec 的做法段與回退段都沒列這一步。
4. 建議(不改 spec 結論,只補做法):明寫「把三種轉正後字樣抽成常數,寫入端與辨認端都改用;辨認放進 `_guard_written_settled_dates` 同一段」,並在回退段補上寫入端改回內嵌。

## F2 `_guard_settle_rewrite` 多回傳一個集合,牽動的呼叫點只列了兩處
severity: minor
blocking: 否
引句:「`_drift_fix_c1` 與 `guard settle` 印訊息時」
file: `scripts/lumos:12290`
file: `scripts/lumos:12532`
file: `scripts/lumos:28010`
1. `_guard_settle_rewrite` 的回傳形狀改了(2 個值變 3 個),它的呼叫者有 `_guard_pass_rewrite`(12290,再被 guard settle 補改與 `_drift_fix_c1` 用)與 `_guard_settle_record_lines`(12532,再被 `_guard_settle_record` 與 `_drift_fix_c5` 用,28010 行 `_drift_fix_c5` 把 `_missing` 丟掉)。spec 只講 `_drift_fix_c1` 與 guard settle 兩處印訊息,沒講 `_guard_pass_rewrite`、`_guard_settle_record_lines` 兩層轉手要跟著改回傳形狀,也沒說 c5 與 pending 轉正那條路徑的訊息要不要一起換成「已轉正/找不到」分開講(現況 `_guard_settle_missing_say` 在 12556 是這兩條路的唯一出口)。
2. 結果:照 spec 字面做,補改路徑講「已經是轉正後的說法」、pending 轉正路徑仍講「找不到」,同一句型因入口不同而說法不同——正好是 guard-kill 那條 WHY 說要避免的(`docs/lumos-toolchain-knowledge/Systems/guard-kill.md:30`「同一種句子不因入口不同而結果不同」)。⚠ 判不準是不是有意只改兩處;若有意,回退段與 [S4] 要明講 c5/pending 路徑不動。

## F3 c3 理由的佔位字檢查與 c4 的檔案無關擋,沒放進既有的「各種類參數檢查表」
severity: minor
blocking: 否
引句:「佔位字由既有 `_drift_placeholder_err`(現在 c2 與 drift ack 在用),c3 也呼叫,不另包函式。」
file: `scripts/lumos:27693`
file: `scripts/lumos:27714`
1. 既有做法:各種類「不用讀檔就能判的參數錯誤」放在 `_DRIFT_FIX_KIND_ARGS[kind]`(c2 的佔位字檢查在 `_drift_fix_c2_args`,27699 行,`_drift_fix_args_err` 統一先跑)。c3 對應的是 `_drift_fix_c3_args`(27708)。
2. spec 把 c3 的佔位字呼叫放進 `_drift_fix_c3`(回退段也寫「`_drift_fix_c3` 的接法與佔位字呼叫」),那是讀檔與乾淨檢查之後的階段;c4 的前三道(值檢查、佔位字與單行、關鍵詞)同樣是不讀檔的檢查,spec 放進 `_drift_fix_c4`,`_DRIFT_FIX_KIND_ARGS["c4"]` 仍是 `lambda o: None`。
3. 後果:同一條規則(S5 說「與 c2 相同」)在 c2 是參數階段擋、在 c3 是讀檔後才擋,髒檔時 c3 會先報「有未提交的改動」而不是報理由不合格;結構不會壞,但這是同一個專案裡兩處放法。建議 c3 的佔位字放 `_drift_fix_c3_args`,c4 的 ①②③ 放 `_DRIFT_FIX_KIND_ARGS["c4"]`(要不要仍是 `--dry-run` 也擋,放在參數階段自然成立)。

## F4 治理事件欄位名寫成 detail,現況欄位是 note,且是 key=value 一串
severity: minor
blocking: 否
引句:「記在既有的 delguard 治理事件的 detail 裡」
file: `scripts/lumos:29401`
1. `_delguard_log_result` 寫的欄位是 `nodes` 與 `note`,`note` 的格式是空白分隔的 `tokens=… hits=… secs=…(+ reason=…)`(29406);沒有 `detail` 欄。RETIRE-IF ② 與 REVISIT 要 grep/抽樣的就是這筆事件,欄位名寫錯會讓量測那步照字面找不到。
2. 跳過資訊也應沿用同一個 `key=value` 寫法(例:`vendored_skip=N`、被跳過的名稱清單),不要另開一個欄位;另外 `_delguard_log_degraded`(29411)的事件走另一個 `note` 字串,超時或內部錯誤時的事件不會帶跳過數,spec 也該講一句「降級事件不記」。

## F5 `_vendored_intact` 抽出:三處內嵌寫法的描述與現況對不上,旁邊已有同族的 `_vendored_skip`
severity: minor
blocking: 否
引句:「這個內嵌寫法已有三處(推送前小改動判定、筆記形狀擋兩處),一起改成呼叫它,行為不變。」
file: `scripts/lumos:18365`
file: `scripts/lumos:24477`
file: `scripts/lumos:24609`
file: `scripts/lumos:17833`
1. 三處內嵌寫法實際在:`_stack_ext_counts`(18365,風險掃描的副檔名統計,ref 用預設的 None=看工作目錄)、`_nodehome_ledger`(24477,ref="")、`cmd_home_check`(24609,ref 依 `staged` 在 "" 與 `tip_where` 之間切)。「推送前小改動判定」不在這三處;推送前分級用的是 `_vendored_skip(root, diff_range)`(17833,呼叫在 21261、29863),那支自己也以 `_is_toolchain_repo` 開頭、要算起點終點兩個狀態,是同一個慣用寫法的第四種變體,spec 沒提、也不併。
2. `_vendored_intact(root, ref)` 必須讓「不傳 ref(None,看工作目錄)」與 `""`(看索引)是兩種不同語意原樣通過,否則 18365 那處「行為不變」會被打破;spec 的簽名沒寫預設值。⚠ 實作時若把 None 當 "" 處理會改變風險掃描讀工作目錄還是讀索引。
3. 新增 `_vendored_intact` 後,`_vendored_state`/`_vendored_skip`/`_vendored_intact` 三支名字相近、各回不同集合;建議 spec 註明 `_vendored_skip` 為何不改用它(範圍語意不同),避免下一個人把它當第二種做法。
4. 這不是引入新做法(三處收成一處是收斂),所以只算 minor;描述錯誤會讓審代碼審的人找不到「推送前小改動判定」那處。

## F6 delguard 的工具檔判定沒有把剩餘時間傳下去,鄰居都是往下傳 timeout
severity: minor
blocking: 否
引句:「超時或出錯照既有的降級路徑,不跳。」
file: `scripts/lumos:29423`
file: `scripts/lumos:33068`
file: `scripts/lumos:29380`
1. `cmd_delguard_check` 的既有慣例是每個子程序都拿「剩餘時間」當 timeout 往下傳(`git diff` 的 `timeout=max(0.1, deadline - …)`、`_delguard_confidence(..., timeout=rem)`),超時以 `subprocess.TimeoutExpired` 落進既有降級路徑。
2. `_vendored_state(root, "")` 走 `_lens_git`,對 `_VENDORED_ALL` 的約 17 支檔各跑一次 `git show`,每次固定 20 秒 timeout(`scripts/lumos:33068`),不吃 delguard 的 deadline。spec 說「在既有的剩餘時間判定(`_over()`)內」只是取完之後再看一次 `_over()`,最壞情況(git 卡住)會比 deadline 多出很多。這與「advisory、恆 rc0、寧可降級」的既有設計取向不同調,也不是 delguard 內任何一處的寫法。
3. 判不準是否要在 spec 層處理:若沿用 `_vendored_state` 原樣,至少在誠實界線註明「工具檔判定的 git 讀取不受 delguard 15 秒預算限制」,並在做法段說明「只在 diff 碰到工具檔時才付這個成本」是唯一的界限。

## F7 「diff 碰到工具檔」的判定沒說由誰、從哪取路徑
severity: minor
blocking: 否
引句:「`cmd_delguard_check` 在取得 staged diff 之後、而且 diff 至少碰到一支 `_VENDORED_ALL` 裡的路徑時才做」
file: `scripts/lumos:29222`
1. 既有的 diff 檔頭解析(`_delguard_parse_diff` 內的 `_flags`,抽 ` b/(.+)$`)是這一支的內部函式,回傳只有 `tokens`、`vault_diffs`,沒有「碰到的路徑清單」。spec 要求 `cmd_delguard_check` 先判「至少碰到一支 `_VENDORED_ALL`」再決定要不要取 `skip`,但 `skip` 又得傳進 `_delguard_parse_diff`——順序是「先判碰到→取 skip→再 parse」,所以碰到的判定必須在 parse 之前另抽一次路徑,等於在 `cmd_delguard_check` 裡寫第二套 `diff --git … b/` 解析。
2. 建議明說做法:要嘛 `_delguard_parse_diff` 多回 `paths` 由呼叫端二次呼叫(parse 兩次),要嘛用 `git diff --cached --name-only -z` 另跑一次(多一次 git 呼叫,要算進剩餘時間)。現在兩種都沒寫,實作者會各自發明。

## F8 第 6 節文件清單漏兩處落點
severity: minor
blocking: 否
引句:「文件:[[Systems/存量漂移守衛]] 的 c4 用法與那條「c4 不寫檔、改走 lumos set」的 PITFALL(標成被取代,補新說法)」
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:8`
1. 存量漂移守衛除了 c4 用法,還會多出「c3 收 `--reason`」與「c4 修復帳多 `reports_same`、`reports_name`」兩件使用者看得到的行為,清單只點 c4 用法與 PITFALL;c3 那件在 lands_in 已對應該篇,但第 6 節沒列,實作時容易漏寫。
2. `_vendored_intact` 收斂三處既有呼叫(每支檔有家、風險掃描)行為不變,可不寫;但新的「刪除守衛跳過工具檔」與 `_vendored_state` 的既有說明散在 `Systems/lumos-deinit`、`Systems/每支檔有家` 等篇(grep 得到),spec 只寫 delguard 一篇。若要讓下個 session 不漏,需在 delguard 那篇補一條指到 `_vendored_state` 說明所在的節點連結(不要在 delguard 內用反引號寫別人的檔)。

## 結尾

不對齊共 8 條,其中 major 0 條。
最高等級:minor;blocking 共 0 條
