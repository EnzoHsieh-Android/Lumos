severity: major

鏡頭:整合與知識同步。查證環境:凍結審材 r1-snapshot.md(115 行)對照 clone-ns 的 scripts/lumos 與 skills/、docs/lumos-toolchain-knowledge/。實務隱患逐類結論放在最後一節。

## F1 新的修復帳沒進簿記檔白名單,提交後會被當成程式改動
severity: major
blocking: 是 — 不改,實作者照字面新增 governance/drift-fixes.jsonl 就會讓小改動閘、code-loop 留痕失效判定把它當程式改動,壞了「通過後只准再提交帳本」的流程
引句:「修復帳:每改一筆,往 `governance/drift-fixes.jsonl` 追加一行(借 `_jsonl_append_verified`,跟表態檔同一種寫法)」
file: `scripts/lumos:21205`
1. 現況:`_BOOKKEEPING_FILES` 是單一源,pitfalls 掃描排除、code-loop 留痕失效豁免、小改動閘(`_sc_changed_files` 的 `_bk`,約 6542 行)、更新時只髒簿記檔的聯集合併(約 17632 行)都讀它。表態檔 `governance/drift-acks.jsonl` 就是專為這個原因在 21210 行補進去的(註解寫「存量漂移防線 [S3]」)。
2. spec 說「跟表態檔同一種寫法」,只借了寫入函式,沒提白名單。〈範圍〉〈做法〉〈回退〉〈lands_in〉都沒有這一項。
3. 後果(可重現):在 lumos-toolchain 這類走 code-loop 的 repo,代碼審 pass 之後提交修復帳,`.jsonl` 不在白名單會讓留痕失效(小改動閘的行數統計也會把新增的帳行算進去);來源 clone 只髒這本帳時,更新流程照原路擋下、不做聯集合併。
4. 該補的:spec 加一條,把 `governance/drift-fixes.jsonl` 加進 `_BOOKKEEPING_FILES` 並綁一條測試(仿 drift-acks 的先例),同時寫明這本帳是否提交進版控(現在沒寫,「事後找得回來」靠的就是它被提交)。

## F2 診斷輸出與 `drift ack` 提示仍教人手改,新指令沒有任何入口指到它
severity: major
blocking: 是 — 不改,照 spec 實作出來的 `drift fix` 沒人找得到,而且現有輸出還會叫人走反方向(rtb 會談就是照輸出走才「沒路可走」)
引句:「一個指令 `lumos drift fix`,依發現的種類給現成的改法」
file: `scripts/lumos:27237`
1. `_drift_report_must`(推送閘輸出)對 c1 印「預告句那幾筆:把預告句手改成歷史說法」,上一行註解還寫「★不叫人重跑 guard settle★:已經 pass 的紀錄 settle 直接回已轉正,不會改寫」。[S3] 之後這句註解與訊息都變成錯的:settle 會補改句,drift fix 也能改。
2. `drift scan` 的文字輸出(`_drift_scan_print`)完全沒有下一步指令;doctor Z 段的 advice 是 `lumos drift scan · lumos drift ack …`(`scripts/lumos:2273`),沒有 fix。
3. skills 端根本沒有 drift 的列:`skills/lumos-project-notes/commands/04-自檢與健康.md`、`INDEX.md` 只有 `drift-history`;`reference.md:117` 的子命令全覽寫「drift check·scan·ack·exam」;頂層說明字典 `"drift"`(`scripts/lumos:35687`)也只列四個子命令。AI 會談進場查的是這些表,不是 spec。
4. `skills/lumos-project-notes/commands/06-代碼審與推送.md:19` 的 guard settle 列寫死 `--test <測試方法名>` 為必填,[S3] 改成 pending 才必填後這列要改。
5. 先例:同 repo 的[[Projects/兩席相反時端出張力_計劃]]有一整段「其餘文字同步」逐項列出 reference.md、commands/06、Systems 表格;本 spec 的 lands_in 只有兩篇 Systems,沒有這一段。
6. 該補的:〈做法〉加「輸出與文件同步」小節,列:`_drift_report_must` 的 c1/c3/c4 提示、doctor Z advice、`_drift_scan_print` 每種類的下一步、`"drift"` 說明字典、reference.md:117、04 與 06 的表、Systems/存量漂移守衛的 responsibility 行(現寫「check、scan、ack、exam」)。

## F3 S8 沒說 `drift ack` 怎麼拿到「當時那筆發現」,拿不到時的行為決定了放寬缺口是否留著
severity: major
blocking: 是 — 不改,實作者會自己選(查不到就不記 related),而「舊表態照舊對得上」的放寬會被新表態繼續複製,自我治理隱患的防法失效
引句:「`drift ack --kind c2` 寫入時多記 `related`:當時那筆發現列出的已收尾計劃清單」
file: `scripts/lumos:27101`
1. `cmd_drift_ack(env, node, line, kind, reason)` 現在只驗「那一行非空」,不知道有沒有對應的發現(可以對任何行、任何 kind 表態)。要記 related,必須新跑一次 `_drift_state_findings(env, only={rel})` 再用 path+line+kind 對到那一筆。
2. spec 沒寫:對不到時(行號給錯、kind 給錯、狀態剛好變了)是擋下、記一筆不帶 related、還是照舊。若選「不帶 related」,任何人多打一個錯行就得到一筆永遠只比路徑原文的鬆表態,且與〈實務隱患〉「新寫的一律帶清單」矛盾。
3. spec 也沒寫 c3 的 related 從哪來(`_drift_c3_hit` 回傳的 plans,c3 發現物的 `related` 欄有,見 `_drift_state_findings`)——與 c2 是同一個對應步驟,寫一處就夠,但要寫。
4. 表態失效條件:related 存的是計劃路徑,計劃改名後現在的清單裡是新路徑,不在舊 related 子集內,會誤判成「多了新的收尾計劃」重新列出(表態本來就不綁行號,但綁了路徑);spec 沒提這個誤報邊,也沒提怎麼退場(重新表態即可,但要寫進提示)。

## F4 `drift fix` 先用啟動時載入的 env 判定再上鎖,鎖內沒有重讀,與〈實務隱患〉的宣稱不符
severity: major
blocking: 是 — 不改,兩個會談同時修同一篇時,後寫的會用舊全文蓋掉先寫的
引句:「防法:寫入鎖、鎖內重讀狀態(同 settle)」
file: `scripts/lumos:12208`
1. 〈做法〉§1 的順序是:先用 `_drift_state_findings` 確認這一行是那一種發現,「寫入一律拿筆記庫寫入鎖」,寫完再重讀驗證。判定用的 env 是指令開頭載入的(`env_text(env, rel)` 讀的是載入時的內容)。
2. `guard settle` 之所以叫「鎖內重讀」,是因為 `_guard_settle_locked` 拿到鎖之後用 `load_raw_for_edit` 從磁碟重讀、再判狀態(註解「★狀態從磁碟重讀★」)。spec 的 c1/c3/c4 三支寫函式沒寫這一步;c1 是整篇改寫,若用載入時的行陣列改寫再 `atomic_write_verify`,期間別的會談在同一篇加的行會被蓋掉。
3. 該補的:明寫「拿到鎖之後從磁碟重讀那一篇、在重讀的內容上再判一次是不是那種發現、再改」;寫完驗證要用的新 Env 怎麼建也一併指出(現有 env 不會自己更新)。

## F5 S3 的 `--date` 與 `--test` 接縫沒定義,settle 端遇到「推不出日期」是死路
severity: minor
blocking: 否 — `drift fix --date` 這條路仍走得通,settle 端只是訊息指向不存在的旗標,實作者補一個旗標或改訊息即可
引句:「或推不出來就擋下、要人給 `--date`,不拿今天充數」
file: `scripts/lumos:36071`
1. `guard settle` 的 argparse 沒有 `--date`;[S3] 只說「同 [S2] 的日期與不疊規則」。照字面 settle 在 shallow clone 或推不出時擋下並叫人給 `--date`,但 settle 收不了這個旗標。
2. [S3]「`--test`…給了也不檢查」:`cmd_guard_settle` 開頭就先 `IDENT_RE.match(method)` 驗名字(在讀狀態之前,`scripts/lumos:12201`),spec 沒說要挪到 pending 分支之後;method 為 None 時現在的成功訊息還會印「綁上 [test:None]」與「下一步 guard audit」(`_guard_settle_record`)。
3. 半做完的 pending(家筆記已是正式行、守衛紀錄還 pending)補第二步時用今天還是提交日期,spec 沒定;因為這種情況正式行可能已提交好幾天。
4. 〈範圍〉的「做」①–⑦沒有列 settle 行為改動與 `--test` 選填,只有〈做法〉§2 與 [S3] 寫了;lands_in 列 guard-kill 的理由在範圍裡看不到。

## F6 c1 一篇多句預告、一次改整篇,之後逐行 `drift fix` 會撞行號位移
severity: minor
blocking: 否 — 失敗方向是安全的(回 2、沒寫檔),但 rtb 那批「20 筆 c1 在 7 篇」照 scan 清單逐行跑會連續報錯
引句:「改整篇(不是只改指定那一行:同一篇的四種預告句是一組,只改一句會留下自相矛盾的半套)」
file: `scripts/lumos:26122`
1. c1 是「一句一筆」發現(`_drift_guard_findings` 對每個預告句各出一筆,行號是檔案行號)。整篇改完後,同一篇其餘 3 筆已不存在,再用它們的行號呼叫會被 [S1] 擋成「現在不是那一種發現」;而 [S2] 刪掉 settle 句還會讓其他行號位移。
2. 訊息「這一行不是 c1」會誤導人以為 scan 清單錯了。spec 沒定義:同一篇 c1 已全部清掉時回 0 印「已修」、或允許指定同篇任一 c1 行都算。
3. c4 證據那一支同理:spec 沒寫 shallow 時 `git log --diff-filter=A` 的「第一次被提交」會是嫁接點提交(與 [S2] 不同,只有 c1 有 shallow 擋),也沒寫檔案改過名時的行為;卷證目錄的「名字含計劃名」只適用 `governance/review-reports/` 這個版面,別的專案未必有,沒有時要印「找不到」而不是空清單。

## F7 E5 標記與 S7 列出的判準細節沒對齊 E5 現有判定,列出範圍會漂
severity: minor
blocking: 否 — 只多印,列錯不會壞資料;但列出的行與 E5 之後唸的行可能對不上
引句:「改完之後,這篇正文與摘要裡還有日期式或條件式回頭條件就逐行列出(行號加原文)」
file: `scripts/lumos:2224`
1. E5 是靠 `_search_visible_lines`(剝掉圍欄與行內程式碼)加 `_revisit_split(_strip_inline_markup(...))` 認 REVISIT 行;[S7] 沒寫要走同一支,自己寫正則會把圍欄裡的範例也列出來(存量漂移守衛節點記過這個坑:「這行是不是 REVISIT」全庫只有一支判定)。
2. 「結案狀態=`QUERY_CLOSED_STATUSES`」含 pass、superseded、abandoned,這些不是 Issue 的合法狀態(Issue 是 open/doing/resolved/done/wontfix);`_cmd_set_locked` 不驗狀態值屬於哪種類型,所以 `lumos set <Issue> status pass` 也會觸發列出。要嘛限定 Issue 的三個結案值,要嘛明說「不驗」。
3. E5 標記「這篇已結案」要讀狀態:E5 迴圈拿到的是 `_n5`(Note),狀態要用 `_drift_str(_n5, "status")`;直接 `_n5.fields["status"]` 遇到清單或非字串值會壞。spec 沒提,測試 [S6] 只驗一般值。

## F8 舊筆記與回頭點沒列進同步:存量漂移防線的 REVISIT 與缺口段、guard-kill 的 pass 行為描述都會變成錯的
severity: minor
blocking: 否 — 只是筆記內容過期;但到期日一到 doctor E5 會唸一條已被裁定的待辦
引句:「缺口清單出自 rtb 會談實測回報,記在 [[Projects/存量漂移防線_計劃]]〈修復結果〉」
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:247`
1. 該檔 247 行 `REVISIT:2026-10-13 決定這五項開不開新計劃…` 與〈修復結果〉標題「未做,要另走設計」:本 spec 的依據已裁定現在開始,這條 REVISIT 到 10-13 會被 E5 唸,內容卻已過期。spec 沒寫「這條改成指向本計劃、或刪掉」。
2. `Systems/guard-kill.md:19` 的 PITFALL 寫「守衛紀錄已是 pass 就回 0」並綁 [test:t_guard_settle_recovers_half_done];[S3] 之後「有預告句時補改、沒有才回 0」,這行與它對應測試的第③格(已 pass 印已轉正,該測試已寫沒有預告句的情境,可保留)要在筆記裡改成新說法。
3. `Systems/存量漂移守衛.md` 的 responsibility 寫「不負責 guard settle 本身(guard-kill)」,但 c1 與 settle 現在共用並改動 `_guard_settle_rewrite`(可刪行);責任邊界句要調整,否則 lumos home 檢查會指到錯的家。

## F9 RETIRE-IF 的三個數目前沒有機械來源,REVISIT 到期時量不出來
severity: minor
blocking: 否 — 屬撤除條件的可執行性,不影響工具行為
引句:「①`drift fix` 在工具鏈與 rtb 合計被用不到 5 次(大家寧可手改,入口沒價值)」
file: `docs/lumos-toolchain-knowledge/Projects/存量漂移改法_計劃.md:23`
1. 修復帳 `governance/drift-fixes.jsonl` 各 repo 一本,「工具鏈與 rtb 合計」沒有彙整路徑(`lumos gov` 也不讀這本);`docs/.usage-log.jsonl` 的指令使用統計是否記到子命令層級沒查證。
2. ②「被人手改回或再改」要比對修復帳的「改後」與之後的 git 歷史,spec 沒有這支比對;③「c4 證據提議被人照抄」在不帶 `--replace` 時不寫任何東西(S5),之後帶 `--replace` 的句子也沒記提議內容,兩者無法對照。要嘛在修復帳的 c4 紀錄記提議句,要嘛把這條撤除條件改成量得到的。

## 各節結論

## 範圍
已讀,只有 F5 第 4 點(settle 改動不在「做」清單)。
引句:「`drift fix` 每改一筆寫一行修復帳(改前改後),事後找得回來」

## 做法 §1–§6
F1–F7 已列。§3 c3 的狀態集合已與程式碼核對:`scripts/lumos:5248` 驗證紀錄合法狀態為 pass/stale/superseded/pending/abandoned,spec 扣掉 pending 正確;`--by` 用 `env.find` 解析與既有節點查找一致,無 finding。
引句:「`--status pass|stale|superseded|abandoned`(必填,驗證紀錄的合法狀態扣掉 pending,見 `lumos lint` 的類型狀態表)」

## 條款
已讀,無獨立 finding(綁定測試名與 F1–F7 相關處已在各條列出:[S3] 併入 F5、[S8] 併入 F3、[S9] 併入 F1、F4)。[S1]–[S9] 交叉引用與〈做法〉章節一致。
引句:「所有寫入應在筆記庫寫入鎖內、原子寫入,寫完重讀並確認那一筆發現已不在」

## 回退
已讀,無 finding。回退說明與程式碼現況相符(表態檔讀取整行原樣回傳、只驗 path 與 kind,已於 `scripts/lumos:27070` 核對)。
引句:「c2/c3 表態的 `related`:回退時比對忽略這個欄位即可(舊行為);已寫的欄位留在表態檔裡無害」

## 誠實界線
已讀,無 finding(E5 不跳過已結案回頭條件的取捨自洽,S7 是安靜的唯一出口)。
引句:「E5 不跳過已結案的回頭條件:結案 Issue 的過時提醒照樣會唸,只是多了標記;要安靜得靠 [S7] 在結案當下處理。」

## 實務隱患逐類
- 守衛面誤擋或漏擋:F3(表態鬆綁的放寬缺口)、F2(提示過時);推送閘的 c1 判定本身不動,無其他新增。
- 不可逆:c1/c3/c4 改的是版控筆記,git 可還原;但〈實務隱患〉引用的「fixed.txt」已被修復帳取代,〈不可逆〉那一行還寫「照 fixed.txt 可整批找出」是舊文字(minor,併入 F8 一併改)。
- 併發:F4。
- 效能:無。`git log -S` 限定家節點單檔;c4 的 `git log --diff-filter=A` 也是單檔;不在迴圈裡跑。
- 向後相容:無 finding。表態多欄位舊版忽略(已核對);`guard settle --test` 由必填改選填,舊呼叫方式不變。

整份最嚴重的是會做出錯行為的一級,擋下實作的共 4 條(F1–F4)。
