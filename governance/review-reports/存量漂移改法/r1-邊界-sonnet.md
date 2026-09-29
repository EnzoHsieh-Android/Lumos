severity: major

(鏡頭:邊界與可執行。程式碼佐證檔:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos,下稱 lumos。)

## F1 `git log -S` 找不到「轉正那次提交」,日期推算照字面永遠落空
severity: major
blocking: 是 — 不改,c1 的日期推算在正常情況下一律「推不出來」而擋下,或誤取到別的提交,[S2] 的測試綠不起來
引句:「所以做法是:取 `git log -S` 列出的提交(舊到新),逐一讀那個提交的家節點」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:11754`
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:12280`
1. `-S` 只列「字串出現次數變了」的提交。settle 第一步(`_guard_settle_home`,lumos:12280 附近)是把同一行的預告行 `KEY:★INVARIANT-PLANNED★ <合約> [watch:..][due:..]` 換成正式行 `KEY:★INVARIANT★ <合約> [test:..]`——合約文字出現次數 1→1,轉正那次提交不在 `-S` 清單裡。
2. 我在臨時 repo 重現:提交 A(2026-09-01)寫預告行、提交 B(2026-09-23)換成正式行,`git log -S"退款要冪等" -- 系統/家.md` 只回 A;`-G` 與不加過濾的 `git log -- 路徑` 才會回 A、B 兩筆。
3. 後果:spec 的演算法「逐一讀清單裡的提交、第一個有正式行的就是轉正日」在清單裡只有 A(沒有正式行)→ 推不出來 → 擋下要人給 `--date`。rtb 的 F1–F3 情境(預告 → 轉正分兩次提交)正是這種,工具在它要解的案例上永遠要求 `--date`,等於日期推算這條路沒做出來。若清單裡恰好有第三個提交讓次數變動(例如之後改寫合約文字),則會誤取到那次而不是轉正日,而且不會擋下。
4. 〈誠實界線〉只承認「行被改寫過推出來的是改寫那天」,沒發現連正常轉正都推不到。改法要走的是「列出家節點檔的所有提交(舊到新)逐一判正式行在不在」(或 `-G`,並限定路徑),spec 沒寫。
5. 同時未定義:路徑是中文,查詢用的路徑要跟 git 樹裡存的拼法一致(NFC/NFD;repo 若在別台以 `core.precomposeunicode=false` 提交過,NFC 查不到 NFD 的樹),輸出解析要用 `-z` 或處理 quotepath 的八進位轉義;只寫了「限定家節點一支檔」。
6. 日期取「提交日期」沒說取 author date 還是 committer date、哪個時區;本 repo 規則是推前把本機提交壓成一個,committer date 會是壓縮那天,不是轉正那天。⚠ 影響哪個日期較合理要看 rtb 實際流程,spec 應明寫。

## F2 同一筆發現有好幾筆表態時,舊表態會永遠遮住新的「連著計劃變了」
severity: major
blocking: 是 — 不改,[S8] 對已經有舊表態的那批筆記(2026-09-29 已寫的 17 筆)完全失效,而且失效是靜默的
引句:「表態帶 `related` 的,要現在的清單是它的子集才算對得上」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:27079`
1. 表態檔是只增不改的 jsonl,同一個 (路徑, 原文, 種類) 可以有多筆(重新表態就是再 append 一筆)。現行 `_drift_split_acked`(lumos:27079)把全部表態收成鍵集合,「任一筆對上」就算已表態。
2. spec 只寫「帶 related 的要子集」「沒帶 related 的舊表態照舊只比路徑、原文、種類」,沒說同鍵多筆時怎麼合成。照字面逐筆判、任一筆過就放行的話:舊的沒帶 related 那筆永遠對得上 → 新增的收尾計劃永遠不會重新列出,即使人之後又用新指令表態了一筆帶 related 的也一樣(舊那筆仍在檔裡、仍會放行)。
3. 要能寫成測試,得定:同鍵多筆時以「最新一筆」為準(舊的沒 related、新的有 → 用新的),或「有 related 的優先於沒有的」。[S8] 的測試只列「沒記清單的舊表態照舊對得上」,沒列這個組合。
4. `related` 欄位的形狀也沒定:`_drift_load_acks` 對欄位原樣回傳(只驗 path、kind),手改成字串或 null 時,集合運算會把字串拆成字元;要規定「不是清單一律當沒帶」。兩邊路徑比對要不要 NFC 也沒寫(既有鍵比對用 `nfc()`,清單比對若漏掉,中文計劃名在 NFD/NFC 兩種寫法間會被誤判成「多了新計劃」)。⚠ 後者依賴 Mac 與 git 樹的正規化差異,頻率未實測。

## F3 c4 的「多行區塊整欄換」會靜默丟掉區塊裡其他前提
severity: major
blocking: 是 — 不改,照字面實作會把人寫的其他前提整段抹掉,而清單寫法卻小心地只換一項,兩種形狀的保護不對等
引句:「清單只換含那三個詞的那一項(有好幾項含就擋下,要人指定),單行與多行區塊整欄換」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:14863`
1. `valid_under` 三種寫法:單行純量(整欄就是一句,整欄換沒問題)、清單(逐項)、多行區塊(`|`/`>` 之後好幾行)。發現物的行號指到區塊裡含關鍵詞的那一行(`_drift_field_line` 的 pred)。
2. 多行區塊可以是好幾句前提、只有一行含「未提交」。spec 對它整欄換成「一句新前提」,其餘各行的前提內容消失,`--replace` 只給了一句。改前內容只在修復帳裡。
3. 而 `_set_conditions_locked`(lumos:14863)只接受單行的值,多行區塊換成一行也改變了欄位形狀。要的不是「整欄換」,而是只換含關鍵詞的那一行(或要求新句子承接整段並擋下少於原行數的替換);spec 沒定,測試 [S5] 也沒有「區塊內含多句」的案例。

## F4 c4 清單「好幾項都含就擋下、要人指定」沒有可用的指定方式
severity: major
blocking: 是 — 不改,這條路又是一個工具沒路可走的死巷(正是這份計劃要補的缺口),而且 [S5] 的那半句寫不成測試
引句:「比對發現物的 line 與 kind;c1 的 line 是檔案行號,c3、c4 是 `_drift_field_line` 找到的欄位行」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:26095`
1. c4 每篇最多出一筆發現(`_drift_state_findings` 對每篇只 append 一次),它的行號是「第一個含關鍵詞的那一行」(`_drift_field_line` 的 pred 只回第一個)。
2. 〈做法〉§1 要求 `<行號>` 必須等於發現物的行號,否則擋下回 2 → 使用者要「指定」第二個含關鍵詞的項,只能給第二項的行號,但那在 §1 就被擋掉;spec 也沒有 `--item`/`--index` 之類參數。結果:好幾項含關鍵詞的清單永遠修不了,只能表態。
3. 另一種可行走法是「一次換掉第一個,換完第二個自然成為下一筆發現」,那就不用擋下;spec 兩邊都沒選。要在 [S5] 寫明是哪一種。
4. `--replace ""`、只有空白、含換行的新句子,行為沒定(`_set_conditions_locked` 對空與換行各有擋,新寫的「只換一項」路徑要不要沿用同一套擋法沒寫)。

## F5 參數組合與 `--date` 的定義不完整
severity: minor
blocking: 否 — 實作者可自行補,但補的方式不同會讓測試與行為不一致,不會做出壞系統
引句:「轉正日期:`--date YYYY-MM-DD` 有給就用;沒給就從 git 推」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:12195`
1. 日期格式錯(`2026-9-23`、`2026-02-30`)、未來日期、早於守衛紀錄 `created` 的日期:沒定要不要擋(同類指令 `cmd_self_audit` 用 `date.fromisoformat` 擋,可照抄,但 spec 沒寫)。
2. 參數對種類不合時:`--kind c3` 卻給 `--replace`、`--kind c4` 給 `--status`、`--kind c1` 給 `--by`、c3 沒給必填的 `--status`(argparse 那層擋不到,因為 `--status` 只對 c3 必填)——沒有一條寫「回 2 且訊息是什麼」。
3. `--dry-run` 搭 c4 不帶 `--replace`(本來就不寫)、搭 c4 帶 `--replace`、搭 c1 日期推不出來:各是什麼輸出沒寫。
4. `guard settle` 補改 pass 節點時「日期規則同上」暗示要有 `--date`,但〈做法〉§2 沒寫 `guard settle` 增加 `--date` 參數;shallow clone(CI)上推不出日期時,這個入口就沒有給日期的辦法,矛盾於「要人給 `--date`」。pending 轉正時有沒有給 `--date` 也沒定(現行永遠用今天)。
5. c1 的合約文字取自守衛紀錄裡的 `預告的合約:` 行,手改掉時、或家節點連結解不到(`env.find(home)` 失敗)時,fix 沒寫擋下的訊息(`_guard_settle_locked` 有,fix 是新路徑要複製)。

## F6 「寫完驗證」失敗與「鎖內重讀」的順序沒定義
severity: minor
blocking: 否 — 主要規則([S9])方向對,只是失敗分支與順序留給實作者猜,一個實作會留下改了一半的筆記
引句:「所以寫完另外重讀整篇,再跑一次同一支判定,確認那一筆發現已經不在」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:14695`
1. `atomic_write_verify` 是「驗完才換名」;spec 的「寫完再判定」是換名之後才驗。若發現仍在(例如 c1 有句型沒改到、c4 新句仍含關鍵詞),檔案已經改了。是回退、還是只報錯?回傳碼?要不要還寫修復帳?spec 沒寫。可以改成「在記憶體算出新文字、跑判定、通過才寫」,但 spec 選的是寫後驗。
2. 〈做法〉§1 先寫「用 `_drift_state_findings` 確認這一行現在是這一種發現」,鎖在後面一句;`_drift_state_findings(env)` 吃的是指令開頭載入的 env(main 在分派前已載入),不是磁碟現況。〈實務隱患〉寫「鎖內重讀狀態(同 settle)」,但〈做法〉沒寫「拿鎖之後重建 env 再判定」;c3 在兩個會談同時修時會各追加一行狀態說明。
3. `--dry-run` 要不要拿鎖沒寫([S9] 的測試名含 lock,怎麼在測試裡觀察「有拿鎖」也沒定;可用 `_VAULT_LOCK_HELD`,但要在條款裡點名)。
4. 寫入順序(筆記先、修復帳後,還是相反)與帳寫失敗時的處理沒定;帳寫失敗但筆記已改,就違反「改一筆就有一行帳」。

## F7 c2 表態記 `related` 時,寫入端的邊界沒定義
severity: minor
blocking: 否 — 寫入端的空分支由實作者決定,測試可能各寫各的,不會壞掉既有資料
引句:「當時那筆發現列出的已收尾計劃清單(排序後,跟發現物一樣存圖譜內相對路徑,不加 vault 前綴)」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:27101`
1. `cmd_drift_ack` 現在完全不算發現物,只讀指定那一行原文就寫(lumos:27101 起);它允許表態任何一行、任何種類,即使那一行現在根本不是發現。spec 要它「記當時那筆發現列出的清單」,得先跑 `_drift_state_findings`,而沒有對應的發現時(`--kind c2` 但那篇沒連著已收尾的計劃、或行號指到別行)寫入什麼?`[]` 與「不帶欄位」在比對規則下是相反的行為(`[]` 之後任何收尾計劃都算新增;不帶欄位則永遠對得上),spec 沒選。
2. ack 每次現算全圖譜的發現物(`build_typed_index` 全庫),表態指令的耗時變重;同時 [S8] 條款沒有「找不到發現物」的分支。

## F8 c4 證據查詢的空結果、shallow、未提交筆記行為沒定
severity: minor
blocking: 否 — 證據本來就標示為「猜」,但空輸出時的行為要定,否則會印出壞掉的範本句
引句:「①那篇驗證紀錄第一次被提交的提交編號與日期(`git log --diff-filter=A`)」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:4861`
1. c4 的前提字面就是「還沒提交」,那篇驗證紀錄本身很可能還沒提交(或 git 不在、vault 不在 repo 內):`git log --diff-filter=A` 沒輸出。範本句「提交 <sha>;代碼審見 <卷證>」的 sha 從哪來?spec 沒寫「沒有提交」的輸出。
2. shallow clone 只在 c1 那節被擋(用 `_git_is_shallow`);c4 的證據在 shallow 上會把邊界提交當成「第一次被提交」,而且是錯的,卻沒有任何提示。
3. 檔案被改名過,`--diff-filter=A` 不追改名(要 `--follow`,且 `--follow` 與 `--diff-filter=A` 的組合行為不穩),回的是改名那次。
4. 卷證目錄的「名字含計劃或 feature 關鍵字」用什麼比對(子字串、NFC、大小寫)沒定;〈誠實界線〉只說可能漏或多。

## F9 手補「已轉正」段的判準與刪行後的版面沒定
severity: minor
blocking: 否 — 影響單一情境的比對細節,寫成測試前要先補齊
引句:「`_guard_settle_rewrite` 現在是逐行一對一輸出,要改成可以刪行;settle 與 fix 共用這一支」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:12086`
1. 「下一段以『<日期> 已轉正』開頭」:日期格式沒定(`2026-09-23`、`2026/09/23`、`(2026-09-23 已轉正)` 帶括號、日期後有冒號);「一段」是到下一個空行還是下一行;跳過空行後遇到標題行算不算。
2. 刪掉那句後,前後各一個空行會變成連續兩個空行;若那句是最後一行,「下一段」不存在,走「換成(日期 已轉正)」——這條分支需要在 [S2] 的測試裡明列。
3. 呼叫端 `_guard_settle_record` 用 `missing` 判斷提醒;改成可刪行後,「已被手補而刪除」的句型要不要出現在 `missing`(它其實是「處理過了」),沒寫,會多印一行誤導的提醒。

## F10 E5 標記對驗證紀錄的語意、顯示上限與 Issue 結案集合
severity: minor
blocking: 否 — 只影響顯示文字與 [S6]/[S7] 的邊界
引句:「標記對所有類型都做(計劃、驗證紀錄也會標),不只 Issue」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:2245`
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:5247`
1. `QUERY_CLOSED_STATUSES` 含 `pass`。status: pass 的驗證紀錄是最常見的正常狀態,它帶的「幾天後重驗」REVISIT 到期就是要它被唸,標成「(這篇已結案)」等於對每筆通過的驗證紀錄都貼上「已結案」,跟〈做法〉§5 的用意(過時提醒)反了。應明說對 pass 的驗證紀錄要不要標。
2. E5 用 `warn_soft`,清單顯示只列前幾行,其餘折成「另 N 條」;標記加在行尾,第 4 筆起看不到。[S6] 的測試應只斷言在可見範圍內。
3. [S7] 寫「結案狀態=QUERY_CLOSED_STATUSES」,但 Issue 合法狀態值(lumos:5247)是 open/doing/resolved/done/wontfix,交集只有 resolved/done/wontfix;其餘(pass、superseded、abandoned)對 Issue 本來就被 `lumos lint` 擋。要寫明「取交集」。
4. 「Issue 已是結案狀態,又 set 成另一個結案狀態(resolved→wontfix)」算不算「改成」(每次都列?還是只在跨進結案時列?)沒定。

## F11 「怎麼修」的提示訊息有平行入口沒列進範圍,改完會說謊
severity: minor
blocking: 否 — 純訊息與說明表,行為無誤,但使用者照舊提示會走回舊路
引句:「其他種類說明沒有改法、指到 `drift ack`」
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:27236`
file: `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/scripts/lumos:35690`
1. 推送閘擋下的訊息(`_drift_report_must`,lumos:27236 附近)寫「已經 pass 的紀錄 settle 直接回『已轉正』,不會改寫」與「預告句那幾筆:把預告句手改成歷史說法」。[S3] 讓 settle 對 pass 補改之後前半句變成假的;新增 `drift fix` 之後這裡也該指到 `lumos drift fix`。spec 的〈範圍〉沒列這處。
2. 指令說明表 `_CMD_HELP`(lumos:35690 一帶)要新增 `drift fix` 一條,否則若有「每個子命令都要有說明」的測試會紅;doctor Z 段的 advice(lumos:2273)、`drift scan` 每筆輸出也沒指到新指令。spec 沒列。
3. `drift` 的分派(lumos:37020 附近)目前是「不是 scan 就當 ack」,新增 fix 時要改成明確判斷,否則 fix 會被當成 ack 執行(這是實作陷阱,spec 沒提)。

## F12 〈實務隱患〉與〈做法〉互相矛盾、還留著舊說法
severity: minor
blocking: 否 — 文件精度,以〈做法〉為準即可
引句:「不可逆(碰到,可還原):改的是版控裡的筆記,git 還原得回來;照 fixed.txt 可整批找出」
1. 〈做法〉§1 已經改成 `governance/drift-fixes.jsonl` 修復帳、且〈前掃〉明說「不靠人記得留 fixed.txt」;〈實務隱患〉不可逆那一行還寫「照 fixed.txt 可整批找出」。
2. 〈實務隱患〉歷史日期一條寫「`git log -S` 取最早一筆,shallow clone 推不準時也擋(提交數不足判不出「最早」)」;〈做法〉§2 是「逐一讀提交、第一個有正式行的」、且「repo 是 shallow 就擋」(無條件擋,不是推不準才擋)。兩處演算法與擋的條件不同。
3. 〈實務隱患〉「向後相容」寫「下游只取 path、text、kind、reason」,加上 `related` 之後 `_drift_split_acked` 也會用它,「下游只取四個鍵」不再成立(舊版 lumos 讀新檔不受影響這個結論仍成立,因為它會忽略多的鍵)。

已讀,無 finding:〈範圍〉
引句:「rtb 那 24 筆由 rtb 會談用新指令修(本計劃只負責工具)」

已讀,無 finding:〈回退〉
引句:「`drift fix` 是新指令:回退就是拿掉子命令與三支改法函式,既有指令不受影響」

已讀,無 finding:〈誠實界線〉(F1 的第 4 點是它沒涵蓋到的邊界,該節自己的宣稱在字面上成立)
引句:「c4 的證據是「猜」:卷證目錄用名字比對,可能漏或多;所以只提議不寫入」

已讀,無 finding:〈c3 驗證紀錄改狀態加一行〉的狀態集合(pass/stale/superseded/abandoned 與 lumos:5247 的驗證紀錄值域一致)。追加一行的落點(檔案結尾沒有換行、最後一節是表格或未關閉的程式碼圍欄)只有細節,沒有影響行為的 finding。
引句:「不改正文原本那段(例如「記 pending,因為…紅」):歷史說法保留,新加的一行說明後來怎樣了」

實務隱患逐類檢查:守衛面誤擋/漏擋——見 F2(漏擋:舊表態遮蔽)、F1(誤取日期);不可逆——git 可還原且有修復帳,見 F6 第 1 點的失敗分支;併發——見 F6 第 2 點;效能——見 F7 第 2 點,只有全圖譜索引一次,無風險;向後相容——見 F12 第 3 點與 F2 第 4 點;金流、對外送出——spec 已排除,同意。

總結:最嚴重等級為重大;blocking 共 4 條(F1、F2、F3、F4),全部共 12 條 finding。
