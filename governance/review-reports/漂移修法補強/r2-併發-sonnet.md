severity: major

## F1 第④道只擋「少了現有項」,擋不住證據頁之後被刪掉的項,還對含關鍵詞的項整批放行
severity: major
blocking: 是
引句:「現在 valid_under 裡不含那三個詞的每一項,都要原文一字不差出現在 `--values` 裡」
file: `scripts/lumos:28086`(`_drift_fix_write` 只比判定當下讀的位元組與鎖內磁碟是否相同)
file: `scripts/lumos:27935`(`_drift_c4_evidence` / `_drift_c4_print` 印證據頁時沒有留任何快照或指紋)
敘述:
1. 併發區把「證據頁到寫入之間有人改過 valid_under」全交給第④道。但第④道讀的是 `drift fix --values` 那一刻的磁碟(`cx["lines"]`),不是印證據頁那一刻的;兩個程序之間沒有任何憑證(沒有指紋、沒有 `--expect`)。鎖內比指紋只保證「這支 drift fix 自己讀檔到寫檔之間沒人動」,管不到「證據頁到這支 drift fix 之間」。
2. 復活被刪的項:valid_under 原有 X、Y、Z(含「還沒提交」)。A 印證據頁、照預填指令拿到 X Y `Z'`。B 在這時用 `lumos set` 把 Y 刪了(Y 已過時)。A 跑 `--values X Y Z'`:第④道只檢查「現有不含三詞的項(X)都在 values 裡」,X 在,通過;values 多出來的 Y 沒人檢查,整欄覆蓋後 Y 被靜默加回去。方向性只擋一邊,「別人剛做的刪除被復活」等同於「別人剛加的項被刪除」,合約意圖(避免靜默覆蓋)只做了一半。
3. 含關鍵詞的項整批豁免:valid_under 有兩項都含「未提交」(Z1、Z2),或 B 在證據頁之後另加了一項含「還沒提交」的條件 W。第④道只要求「不含三詞的項」原文在,含三詞的項全部豁免;第③道又要求 values 每一項都不能含三詞。所以 `--values X Z1'`(沒寫 Z2)通過①到⑤:Z2 被靜默刪掉,`handled=_drift_no_kind("c4")` 因為 Z2 已不在而判定成功,修復帳的 `changed` 雖然有記,但沒有任何訊息叫人知道「這項是被刪、不是被改寫」。證據頁只標「← 要改的這項」,沒有把「刪掉」與「改寫」分開。
4. 建議(判斷不確定的部分標 ⚠):證據頁預填指令附上 valid_under 欄位的指紋(例如 `--expect <sha>`),`--values` 帶了就在判定時比、不符回 2;或把含關鍵詞的項也納入對照,要求每個含關鍵詞的現有項在 values 裡「有一個對應的改寫」而不是直接消失(⚠ 對應的判法要另想,不能讓工具自己判讀語意)。

## F2 「受既有剩餘時間限制」只做了進場前一次檢查,`_vendored_state` 本身沒有時間上限
severity: minor
blocking: 否
引句:「在既有的剩餘時間判定(`_over()`)內取 `_vendored_intact(root, "")`」
file: `scripts/lumos:17765`(`_vendored_state` 對 `_VENDORED_ALL` 每一支各跑一次 `git show`,再一次讀 `.lumos/vendored.json`)
file: `scripts/lumos:33068`(`_lens_git` 每次呼叫固定 `timeout=20`,不吃呼叫端的剩餘時間)
file: `scripts/lumos:29423`(`cmd_delguard_check` 的 `git diff` 用的是 `max(0.1, deadline - 已用)`,兩者做法不一致)
敘述:
1. `_VENDORED_ALL` 有 17 支檔,加清單共 18 次 git 呼叫,每次上限 20 秒;預設整支 delguard 只有 15 秒。`_over()` 只在呼叫「前」看一次,呼叫「中」沒有任何截斷。git 卡住(網路磁碟、超大 repo、防毒掃描)時,pre-commit 最壞會多等到約 360 秒才輪到下一個 `_over()` 檢查,而這道守衛的設計契約是「恆 rc0、超時降級」。
2. 「超時或出錯照既有的降級路徑,不跳」也對不上:`_vendored_state` 遇到 `_lens_git` 逾時(回 None)不會拋例外,而是把該檔記成「在、但沒對上」再繼續下一支,所以根本不會進到降級路徑,只是慢。三個既有呼叫端(推送前判定、筆記形狀擋)不在 15 秒契約底下,不能拿它們「行為不變」當這裡安全的理由。
3. 附帶的時序:staged diff 在一個 git 呼叫裡讀,索引裡的工具檔與清單在之後 18 次呼叫裡讀。中間若有別的程序(編輯器、另一個 shell 的 `git add`)重新暫存,跳過集合來自比 diff 新的索引:diff 裡是被改過的工具檔內容、索引卻已是原封不動,結果該檔被跳過、被刪名稱漏抽,違反本節自己說的「寧可誤報不漏」。窗口很窄,單靠 `git diff --cached --raw` 拿到同一時刻的 blob id 可以避開(⚠ 沒實驗過,只是方向)。
4. 建議:給 `_vendored_state` 一個總時限參數(或只查 diff 真的碰到的那幾支,不要全表 17 支),把逾時明確回成「不跳」並記進治理事件的降級原因。

## F3 c4 的 git 查詢失敗會被記成「同提交清單為空」,而 RETIRE-IF 正是靠這個欄位決定撤不撤機制
severity: minor
blocking: 否
引句:「git 失敗或逾時,同提交清單當空。」
file: `scripts/lumos:5865`(`_plan_first_commit` 逾時回 None,與「沒進歷史」同一個回值)
file: `scripts/lumos:23621`(`_nodehome_git` 失敗回 None,與「那個提交沒加任何卷證」同一個結果)
敘述:
1. `--values` 寫入路徑要組 `extra` 的 `reports_same`,所以在鎖外、判定之後、寫入之前跑 `_plan_first_commit`(最長 20 秒)加 `_nodehome_git`(20 秒逾時)。這段最長約 40 秒以上的時間裡,`cx["raw"]` 是更早讀的:期間任何程序碰過這一篇(例如另一個 `lumos set`),鎖內指紋比對就回「判定之後這一篇被改過,沒寫;重跑一次」;重跑又是同樣長的窗口,機器忙、git 慢時很難通過。
2. 逾時、失敗、shallow 全部收成 `reports_same: []`,寫進帳的欄位與「真的沒有同提交卷證目錄」長得一模一樣。RETIRE-IF ① 的量法是「同提交找到、計劃名找不到」的筆數要 ≥1,否則撤掉同提交找法;git 在負載下逾時越多,帳上 `reports_same` 空清單越多,量出來的結果會系統性偏向「同提交找法沒帶來東西、該撤」。2026-11-30 REVISIT 的一行 python 沒辦法區分這兩種。
3. 建議:帳上加一個欄位記「同提交查詢有沒有成功」(例如 `reports_same_ok`,失敗寫 false 或整個欄位寫 null),REVISIT 指令只統計成功的筆。

## F4 「過了才組 res」列的鍵不夠,照字面組出來的 res 會在寫入流程裡 KeyError
severity: minor
blocking: 否
引句:「過了才組 `res`:`check=lambda f: _conds(f.get("valid_under")) == vals`(用去空白後的 vals)」
file: `scripts/lumos:28086`(`_drift_fix_write` 讀 `res["new"]`、`res["key"]`、`res["check"]`)
file: `scripts/lumos:28060`(`_drift_fix_preview` 讀 `res["msg"]`)
file: `scripts/lumos:28157`(`cmd_drift_fix` 成功時印 `res['msg']`;`_drift_fix_record` 讀 `res["extra"]`、`res["new"]`)
敘述:
1. spec 列了 `check`、`handled`、`extra`、`texts`,沒列 `new`(改後行)、`key`(`"valid_under"`)、`msg`(預覽與成功訊息用)。照字面實作,`--dry-run` 印預覽、鎖內寫入、成功訊息三處都會 `KeyError`。
2. 更容易漏的一個:`key` 要是 `valid_under`,`atomic_write_verify` 才會用對的鍵報錯;`check` 用的是 `f.get("valid_under")` 這個寫死的鍵,兩處不同步時,錯誤訊息會指到別的欄位。這不是併發問題,但在同一段補進來的文字,就一併寫出。

## 已讀,無 finding
- set 拆函式後鎖的位置:`cmd_set` 在 `_vault_write_lock` 裡呼叫 `_cmd_set_locked` 再呼叫 `_set_conditions_locked`,拆後它仍在鎖內先驗值、再讀檔、再 `_conditions_rewrite`、再寫。drift fix 呼叫兩支不寫檔函式是純運算,不需要鎖;真正的寫入仍走 `_drift_fix_write` 的鎖與位元組比對,所以拆函式沒有新增「鎖外讀、鎖內寫」的洞。鎖可重入(`_VAULT_LOCK_HELD`),不會自己卡自己。
- 兩個 `drift fix --kind c4 --values` 同時跑同一篇:兩邊 `cx["raw"]` 相同,先寫的贏,後寫的在鎖內比對發現磁碟已變回「判定之後這一篇被改過」,不會兩邊都寫。A 寫完到記帳之間 B 進來:B 的乾淨檢查看到未提交改動、帳上最後指紋還不是 A 的,被擋,不會兩筆帳互蓋。
- 修復帳新欄位的追加本身:`_drift_ledger_append` 在 `_drift_fix_record` 的 `_vault_write_lock` 內取序號並追加;`_drift_jsonl_parse` 只在 `\n` 切行、只要求是 JSON 物件,不驗欄位,舊版工具讀到多出的 `reports_same`、`reports_name`、`template_used` 會忽略,新欄位不會讓行被丟掉。序號同號的合併情形是既有行為,本設計沒有惡化。
- ★INVARIANT★ 逐條:Systems/guard-kill 兩條(`guard kill` 的 rc 優先序、`--json` 成功時 stdout 只有一行 JSON)——本設計只改 `guard settle` 與 `_drift_fix_c1` 的「找不到」訊息與 `_guard_settle_rewrite` 的回傳,`guard kill` 的路徑與輸出都不碰,不影響。Systems/lumos-cli-write、存量漂移守衛、delguard 三篇在這份 repo 的摘要裡沒有 ★INVARIANT★ 行(只查到存量漂移守衛的兩條 RULE:預設 warn 的門檻、開關讀頂端提交,都與這份設計無關),不影響。
- 刪除守衛的 `_vendored_state(root, "")` 讀索引:`f"{ref}:{p}"` 在 ref 為空字串時是 `:path`,git 解讀成索引第 0 階段,`_json_at_ref` 同理;沒暫存清單時索引裡的清單是舊的,和新暫存的工具檔指紋對不上、不跳,和誠實界線的說法一致。

最高等級:major;blocking 共 1 條
