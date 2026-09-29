severity: minor

# 存量漂移改法 r2 — 正確性席(opus)

對照程式碼:clone-ns @ 86a9fca6。逐節讀完;每條宣稱都對過程式碼,git -G 的行為用臨時 repo 跑過(建檔 status: pending → 原地改成 pass,`-G "^status: pass"` 只列出改成 pass 的那次,`-S status` 只列出建檔那次,跟 spec 講的一致)。

## F1 那 17 筆 c2 重新表態,會把原本表態之後才收尾的計劃一起算成「已看過」

severity: minor
blocking: 否 — 實作者照做只會讓這一小批已知案例少受一次保護,不會做出壞系統
引句:「實作收尾時,對工具鏈 2026-09-29 那 17 筆 c2 表態各重跑一次 `drift ack`(同理由)」
file: `governance/drift-acks.jsonl:12`

1. 新寫的表態記下的 `related`,是重跑那一刻那筆發現列出的已收尾計劃,不是 09-29 原本表態時看過的那一批。
2. 原本的理由有寫到當時看了幾篇,例如第 12 行寫「連著的五份計劃是各自的實驗/參考」、第 14 行寫「兩份連結計劃」。如果 09-29 到實作收尾之間又有計劃收尾、連到這篇 Issue,重跑同一個理由就會把新多出的計劃一起寫進 `related`。這正好是第 6 節要重新列出的情況,結果被這個步驟默默放過。
3. 要重現「表態當時的清單」,程式碼現成就有路:對加入那筆表態的提交跑 `lumos drift scan --at <提交> --json`,拿那時的 `related` 跟現在比。一樣才照原理由重跑;多出來的要人重新判。spec 沒寫這一步。

## F2 guard settle 走 pass 補改時,查 git 推日期的那一步會落在寫入鎖裡面

severity: minor
blocking: 否 — 只有 git 查詢超過 30 秒才會出事,機率低
引句:「還有預告句就走第 2 節同一支(日期規則、前提檢查、不疊、修復帳 `via: guard settle`)」
file: `scripts/lumos:12204`

1. 第 1 節第 1 步刻意把 c1 的 git 查詢放在鎖外。理由是寫入鎖 30 秒沒放,就會被別的程序當成死鎖接手(`_VAULT_LOCK_STALE_SEC`)。
2. `cmd_guard_settle` 一開頭就拿鎖,狀態是在鎖裡的 `_guard_settle_locked` 才讀到。照第 3 節字面「走第 2 節同一支」去做,推日期的 `git log -G` 會在鎖裡跑。要跟第 1 節一致,settle 得先在鎖外讀一次狀態、推日期,進鎖後再重判。第 3 節沒寫這個調整。
3. 同一個順序還有另一個洞(fix 也有):要不要推日期是在鎖外判的(只有 TEST、WHY、要換成已轉正的 settle 句才需要)。如果鎖外判成不用推,進鎖重讀後那一篇卻又出現要寫日期的句子(另一個會談剛改過),spec 沒說怎麼辦。字面上實作,會拿空的日期去組句子。應該寫明:鎖內發現需要日期、手上卻沒有,就回 2。

## F3 c1 推日期沒有參考筆記裡已經寫好的轉正日期,同一篇可能出現兩個不同的日子

severity: minor
blocking: 否 — 只在提交日跟人手寫的日子不同時才會發生,方向是自相矛盾,不是寫錯狀態
引句:「逐筆讀那個提交的那一篇,第一筆 status 是 pass 的,取它的日期」
file: `scripts/lumos:12032`

1. spec 的取日期順序只有兩個來源:`--date`,或 git 裡第一次變成 pass 的提交日。
2. 手補段那種情況(rtb F4–F7),下一行已經有人寫好「YYYY-MM-DD 已轉正」,spec 會把 settle 句刪掉、保留這一行。可是同一篇的 TEST、WHY 還是用 git 推出來的日期改寫。git 的日子(作者日期,可能是晚幾天才提交、或壓成一個提交)跟手寫的日子不同時,改完的筆記會同時寫著兩個轉正日。
3. WHY 行尾已經有「(X 已轉正)」的那種(程式裡叫 `why-done`,不再改寫),也是同樣的狀況。
4. 修法:取日期的順序在 `--date` 之後、git 之前,加一條「筆記裡已經有的轉正日期(手補段或 WHY 行尾)」。兩者對不上就回 2,要人給 `--date`。

## F4 手補段那句的「刪掉這一行」,照字面讀指的是人手補的那一行

severity: minor
blocking: 否 — [S2] 與下一句「因手補段而刪掉的 settle 句」已經講清楚要刪的是 settle 句,只是本句自己讀起來會導錯
引句:「下一個非空行如果符合 `^\(?\d{4}-\d{2}-\d{2}\)? ?已轉正` 就刪掉這一行(連同它後面緊接的一個空行,避免留兩個空行)」

1. 這句最近的主詞是「下一個非空行」,也就是人手補的那一行。照這句字面實作,會把人寫的已轉正說明刪掉、settle 句留著;c1 還在,人的內容卻沒了。
2. 「連同它後面緊接的一個空行」也跟著指錯對象。settle 句是樣板的最後一行,人手補段通常緊接在它後面、中間隔一個空行。空行要刪的是 settle 句後面那一個。
3. 這句應該改寫成主詞明確的「刪掉 settle 句本身,以及 settle 句後面緊接的一個空行」。

## F5 對 pending 的 guard settle 給了 `--date` 會怎樣沒寫,照字面就是默默不理

severity: minor
blocking: 否 — 影響的是使用者的預期,不會改壞既有筆記
引句:「新增 `--date YYYY-MM-DD`,給 pass 補改句用;pending 轉正照舊用今天(那一刻就是轉正日)」
file: `scripts/lumos:12300`

1. `--date` 是 settle 的參數,pending 和 pass 都能帶。spec 只說 pending 用今天,沒說帶了 `--date` 要擋還是照用。
2. 會帶 `--date` 的人通常是想補寫實際轉正的那天。默默不理的話,會寫進今天,而且沒有任何提示——這正是第 2 節要避免的「用今天改寫歷史」。
3. 應該明寫:pending 帶 `--date` 就回 2,說明 pending 的轉正日就是今天。或反過來規定照用。二擇一寫進 [S3]。

## F6 寫完之後確認「那一筆發現已經不在」,沒定義怎麼算同一筆

severity: minor
blocking: 否 — 依第 3 步用行號加種類去認,現有的寫法都走得通;只有換成路徑加種類去認才會卡死
引句:「用同一支判定確認那一筆發現已經不在」
file: `scripts/lumos:26103`

1. c4 是一篇一筆,行號是 valid_under 裡第一個含那三個詞的行。
2. valid_under 有兩項都寫「未提交」時:用 `--old` 換掉第一項,那一項不再含那三個詞,可以過;c4 還是在,只是換成指向第二項的行。
3. 用「行號加種類」認同一筆:行號變了,算已經不在,可以寫入。用「路徑加種類」認:永遠還在,每次都還原、回 2。而 `--old` 又規定全部項目合計只能出現一次,沒辦法一次換兩項,這篇就變成永遠修不掉。
4. 第 3 步用「指定的行」認,第 5 步只寫「那一筆」。應該明寫同一套鍵(種類加行號加原文),並補一條兩項都含那三個詞的測試。

## F7 c4 借用整欄重寫,「其他項目一字不動」只在解析後的值成立,檔案本身會被重排

severity: minor
blocking: 否 — 值不變,但 [S5] 的測試要是比對檔案原文會對不上,實作者會以為自己寫錯了
引句:「換掉那一段,其他項目與同一項的其他文字一字不動」
file: `scripts/lumos:14880`
file: `scripts/lumos:13524`

1. `_set_conditions_locked` 會把整欄拿掉重寫:一項就寫成單行 `valid_under: 值`,多項寫成一行一項的清單,每一項都重新過 `fmt_scalar` 加或拿掉引號。
2. 所以原本只有一項的清單會變成單行寫法,多行區塊會變成清單,不必要的引號被拿掉、單引號換成雙引號。這些都是「同一個值、不同的字」。
3. 「項」的定義也沒寫。現有程式讀取時用 `_conds`,它會把多行區塊逐行拆成好幾項;`as_list` 則是整塊算一項。拆出 `_conditions_rewrite` 時要用 `_conds` 的定義,「項數相同」才對得起來。
4. [S5] 與本句應該改成「其他項目的值不變(寫法照整欄重寫的格式)」,並寫明「項」照 `_conds` 認。

## F8 新閘名 `drift-fix` 沒登記,治理事件寫不進去,每次修完還多印一行警告

severity: minor
blocking: 否 — 寫入端自己會印出「要新增閘名請同時更新 _KNOWN_GATES」,實作時就看得到
引句:「成功後記一筆治理事件(閘名 `drift-fix`,同 `drift ack` 記事件的方式)」
file: `scripts/lumos:6904`
file: `scripts/lumos:1154`

1. `drift ack` 記的閘名是 `drift-check`,這個名字已經在 `_KNOWN_GATES` 名單上。
2. `drift-fix` 不在名單上。`_gate_event` 碰到名單外的閘名,會直接不寫、回 False;`_gate_event_or_warn` 再印一行「寫不進去」。
3. spec 要列出「`_KNOWN_GATES` 補 `drift-fix`」,並寫進第 7 節要同步改的地方;不然就改用既有的 `drift-check` 加一個新的 kind。

## F9 「多工作樹合併照既有的 JSONL 聯集合併處理」跟程式不符,而且「以最新一筆為準」讓檔內順序變得有意義

severity: minor
blocking: 否 — 帳檔合併衝突本來就存在,新規則只是讓人手解衝突時排錯順序的後果變大
引句:「照既有的 JSONL 聯集合併做法處理(`_pull_source_or_abort` 對簿記 JSONL 取聯集)」
file: `scripts/lumos:17576`

1. `_pull_source_or_abort` 只在 `lumos update` 或 bootstrap 拉工具來源 clone 時用:來源 clone 只髒了簿記帳時,它先把本機多出來的行存起來,拉完再補回去。專案 repo(工具鏈自己或 rtb)在兩個分支或工作樹之間做 git 合併時,完全不會走到它,repo 裡也沒有設 `merge=union`(`.gitattributes` 只有 ps1 那條)。
2. 兩邊都在檔尾追加 `drift-fixes.jsonl` 或 `drift-acks.jsonl`,git 合併會出現一般的衝突,要人手解。
3. 以前的表態比對是「任一筆對得上就算」,順序不重要。改成「以最新一筆為準」而且用檔內順序認最新之後,人手解衝突時如果把同一個鍵裡較舊、沒記清單的那筆放到後面,新規則就對那一鍵失效。
4. 這句要改成照實寫:沒有自動聯集,衝突要手解,手解時同一個鍵要按日期排。否則就另外規定用 `date` 加檔內順序來認最新一筆。

## F10 scan 給 c3 的修法提示少了必填的 `--status`,照抄就回 2

severity: minor
blocking: 否 — 提示文字錯了,改法本身不受影響
引句:「c1/c3/c4 每筆印 `lumos drift fix <節點> <行號> --kind <種類>`」

1. 第 4 節規定 c3 的 `--status` 必填,而這個指令格式沒有帶它。使用者照 scan 印的整行貼上跑 c3,第 1 步就會因為缺參數回 2。
2. c1 照印可以直接跑;c4 不帶改寫參數就是列證據,也說得通。只有 c3 會斷。c3 那一行應該印成 `--kind c3 --status <pass|stale|superseded|abandoned>`。
3. 另外,c5 的出路是 `guard settle`,而 pending 的 settle 仍然要 `--test`。[S1] 說「c5 指到 guard settle」,印出來的指令要帶 `--test <測試方法名>`,不然照抄也會回 2。

## 各節核對

- 開頭(白話、依據、PRIOR-ART、RETIRE-IF):已讀,無 finding。①所說的 `_guard_settle_rewrite` 目前逐行一對一輸出、只認四種句型,屬實;`_plan_first_commit` 用 `--diff-filter=A`,說明裡也寫了為什麼不信 created,屬實。
  引句:「c1 的改句邏輯現成(`_guard_settle_rewrite`,guard settle 第二步)」
- 〈範圍〉:已讀,無 finding。
  引句:「c2、c5 的自動改法(c2 要人判 Issue 解決沒;c5 已有 `guard settle` 重跑)」
- 〈做法〉第 1 節:F2、F6、F8、F9。分派「不是 scan 就當 ack」屬實(check 和 exam 在更前面另外分派);`atomic_write_verify` 的自驗只看開頭欄位,屬實。
- 〈做法〉第 2 節:F3、F4。前提檢查用 `_guard_formal_line(…, None)`:有綁任一支測試就算,跟「不限測試名」一致。`-G` 找得到轉正那次、`-S` 找不到,已經重現。
- 〈做法〉第 3 節:F2、F5。要跟著改的兩支既有測試屬實。另外,`t_guard_settle_rewrites_planned_prose` 的樣板裡 settle 句是最後一行、後面沒有手補段,新的刪行規則不會讓它變紅,要改的只是補一個手補段的情況。
- 〈做法〉第 4 節:F6、F7、F10。c3 的合法值扣掉 pending 後是 pass、stale、superseded、abandoned(lint 的值域表);`_drift_c3_hit` 本來就排除守衛紀錄,寫入不會碰到守衛機制。
- 〈做法〉第 5 節:已讀,無 finding。E5 餵 `_revisit_split` 的是原始行剝掉行內標記之後的版本,跟 spec 寫的一致;關 Issue 的路徑全 repo 只有 `lumos set`,沒有漏掉的平行入口。
  引句:「在 main 分派處 `cmd_set` 成功之後呼叫(跟計劃收尾的 `_drift_print_followups` 同一個位置」
- 〈做法〉第 6 節:F1、F9。子集語意(現在的清單是記下那份的子集才算)方向正確:計劃重新打開、從清單裡消失,仍然算已表態;多了新的就重新列出。`_drift_old_reason` 原路徑還在就跳過,屬實,所以另寫一支查找是對的。
- 〈做法〉第 7 節:F10。
- 〈條款〉:已讀。[S2] 明寫刪的是 settle 句,可以用來收 F4;其他條款跟正文一致。
  引句:「推不出日期或 repo 是 shallow 時擋下、不用今天」
- 〈回退〉:已讀,無 finding。`_drift_load_acks` 整行原樣回傳、下游只讀 path、text、kind、reason,屬實。
  引句:「已寫的欄位留在表態檔裡無害(`_drift_load_acks` 整行原樣回傳、下游只取 path、text、kind、reason)」
- 〈實務隱患〉:已讀。併發那條的「鎖內重讀重判」在 settle 那條路徑上不完整,見 F2;其他各類(不可逆、效能、金流、對外)的判斷成立。
  引句:「git 查詢放鎖外、寫入在鎖內且鎖內重讀重判」
- 〈誠實界線〉:已讀,無 finding(F3 的日期矛盾可以另補一條進界線)。
  引句:「推送前把好幾個提交壓成一個時,是壓成的那一筆的作者日期」
- 〈合約候選〉:已讀,無 finding(本節只有一句占位,設計審過閘後才填)。
- 〈審計修正紀錄〉:已讀,無 finding;r2 改寫的幾處(以最新一筆為準、鎖內重建筆記物件、拆出 `_conditions_rewrite`)都已經在正文裡對過。
  引句:「鎖內重讀要重建筆記物件(只重讀正文,開頭欄位還是舊的)」

最嚴重的等級是次要,會擋實作的共 0 條(10 條都不擋)。
