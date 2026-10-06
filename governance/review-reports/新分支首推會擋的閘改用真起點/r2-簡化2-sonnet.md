severity: major

## F1 範圍列了 9 個吃 `_brange` 的呼叫點,其中至少 3 個不擋,不需要換
severity: major
blocking: 是——範圍過大,多出的呼叫點沒有「不換就誤擋」的失敗場景,卻都要寫測試和承擔回退面。
spec 段落:「範圍」第三條(吃 `pp_block_range_for` 的清單)與「做法」3。
引句:「兩處 `loop escape --range`。」
問題:`loop escape --auto --range` 只把範圍字串寫進逃逸帳的描述,不是閘。`file: scripts/hooks/pre-push:432`、`file: scripts/hooks/pre-push:438` 在 `code-loop check` rc1 之後才呼叫,而 `cmd_loop_escape` 的 `git_range` 只當紀錄欄位。它不會誤擋,換了反而讓帳上的範圍跟閘實際看的範圍不一致,所以換 `_brange` 是必要的只有「帳要跟閘一致」這一個理由。這一條是低價值,可併成「escape 跟 code-loop check 用同一個變數」一行,但 spec 把它當獨立的受影響呼叫點列進驗收面,多了測試負擔。
更大的問題在「真正會擋」的清單本身:
- `spec-gate --push-check`:本身擋不擋要看計劃筆記,沒有證據顯示 rtb 的 715 條來自它。spec 沒給失敗場景(哪個輸入走到這步被空樹誤擋)。
- `pitfalls --diff --json`(決定分級)與 `impact_once`:這兩個是 rtb 重現的真因(分級被拉高、受波及合約測試被餵進 code-loop check),保留。
- `doctor --touched-from`:會擋,但只在有逾期預告合約時。保留。
具體例:新分支首推、只改一份 README。今天 `spec-gate --push-check` 拿空樹範圍,spec 沒說它在這個輸入下會擋;若它擋,spec 該寫出來,不寫就不該動。
更小的改法:只換「會因範圍大而誤擋、且 rtb 已重現」的三條(pitfalls 分級、impact_once→code-loop check、doctor touched),spec-gate 與 escape 視為跟著 `$_range` 的別名變數、不另列。至少要把 spec-gate 的失敗場景補進 spec。

## F2 開新指令 `lumos push-range` 的必要性只成立一半:新指令能被「既有指令在內部吃空樹」取代
severity: major
blocking: 是——存在更小且已有先例的改法,spec 的「不選」只否決了掛鉤層算起點,沒比較過「在 lumos 端統一處理」。
spec 段落:「範圍」第一條、「做法」1;「不選」。
引句:「新指令 `lumos push-range --diff <遠端舊值>..<頂端> --push-remote <遠端名> --pushed-ref <遠端 ref>`」
事實:`_lens_push_base`(`file: scripts/lumos:41772`)已經把「全零起點或本機找不到的起點」解成跟主線的分岔點,每支檔有家(`file: scripts/lumos:27922`)與筆記形狀擋(`file: scripts/lumos:30318`)就是這樣用的;`code-loop check` 在 CI 對全零同樣走它。也就是說 lumos 端已經有「看到全零/找不到就自己算真起點」的機制,而掛鉤層是把全零先換成空樹才傳,把這個機制關掉。
更小的改法 A:掛鉤的 `pp_range_for` 對新分支/找不到舊值時改傳 `全零..頂端`(不再換空樹),讓 pitfalls、impact、spec-gate、code-loop check、doctor 各自在 lumos 端呼叫既有的 `_lens_push_base`(幾個已經在用)。不需要新指令、不需要掛鉤端的 40~64 位十六進位格式驗證、不需要「舊版 lumos 沒有指令」的退回分支。代價:`_lens_push_base` 在合過主線時多算,r1 已指出,所以 A 不是免費的,但那個缺點本案的天花板第 1 條本來就接受了一般增量的同類多算。
更小的改法 B:讓既有指令吃 `--push-remote/--pushed-ref`(`drift check`、`note-audit reread-check` 已有同一組參數,`file: scripts/lumos:47182`),只對 pitfalls(分級)、impact、code-loop check 三個加。spec 要說明為什麼 A、B 都不採:現在「不選」欄只比較了掛鉤層算起點與只改訊息,沒有這兩個。
為什麼 spec 的選擇可能仍成立:六個消費者各自加旗標是 6 份參數解析,一支印範圍指令只維護一處;這是新指令的唯一站得住的理由,spec 沒寫出這一句,應補。補上並對 A 說明為何不行(`_lens_push_base` 合過主線會錯、`--no-verify` 推別的遠端分支能繞過,這兩個是 r1 實測的,可直接引),F2 可降為 minor。

## F3 S7(舊值本機找不到)與標籤路徑是範圍蔓延,且彼此矛盾
severity: minor
blocking: 否——可砍可留,但標籤那段的後果已自己寫成「推送前不跑全套測試」的退步。
spec 段落:「實務隱患」標籤推送、驗收 S7。
引句:「標籤的頂端通常已在主線上 → 範圍是空的 → 分級判成只動文件、推送前不跑全套測試。」
問題:修的目標是「新分支首推誤擋」。標籤推送遠端 ref 是 `refs/tags/*`,不是分支,舊值通常全零。spec 因為把新範圍也餵給「分支與標籤共用的那次 pitfalls」,等於新增一個放鬆(發版標籤不跑全套)。這不是被要求的修法,是副作用被接受。最小做法:`pp_block_range_for` 只在 `$_rref == refs/heads/*` 時呼叫 `push-range`,標籤維持空樹範圍。多一個 `if` 換掉整條天花板與接受的退步,比寫進天花板簡單。S7 同理:舊值找不到走同一個分支,零額外成本,可留。

## F4 RETIRE-IF 與範圍自相矛盾,且「收斂」不是撤除條件
severity: minor
blocking: 否——但不能撤除的機制條件等於沒寫撤除條件。
spec 段落:RETIRE-IF 與天花板第 2 條。
引句:「本案「只在新分支首推時呼叫」這個分支判斷撤掉,一律呼叫。」
問題:撤掉的是 `pp_block_range_for` 裡的 if,不是新指令;新指令在收斂後反而變成唯一入口。所以撤除條件沒有說「看到什麼就把 `lumos push-range` 與 `_brange` 拿掉」。若採 F2 的 A,撤除條件才自然(`_lens_push_base` 被 `_push_range_start` 吸收即一併消失)。要寫成機器可判的:例如「`Issues/推送前其他閘的範圍在合過主線時會多算` 結案後,hook 內 `_hrange` 與 `pp_range_for` 全被刪掉」。

## F5 `頂端..頂端` 與退回空樹兩種輸出形狀是多餘的分支
severity: minor
blocking: 否
spec 段落:「範圍」第一條、驗收 S6。
引句:「頂端已在主線上(沒有新東西)印 `頂端..頂端`」
問題:`_push_range_start` 回 None 時,下游 `git diff A..A` 為空,各閘各自處理空範圍的行為沒被驗過(pitfalls 空範圍判分級、code-loop check 對空範圍是跳過還是報錯、spec-gate 空範圍)。這是新輸入形狀。更簡單:None 時讓指令 rc1 或印空,掛鉤把非 0 一律退回空樹(多擋、同今天),就少一個要驗的形狀;但那會讓「頂端已在主線」的新分支被誤擋,正是要修的。所以不能砍,只能要求:S6 裡補「各下游吃 `頂端..頂端` 不崩、不誤擋」一條,否則三種輸出裡這一種沒有端到端驗證(S1~S3 沒有任何一條的輸入是頂端已在主線)。⚠ 判不準下游 pitfalls 空範圍的實際行為,未實跑。

## 逐節
- 開頭 summary/白話/依據/PRIOR-ART:已讀,無 finding(PRIOR-ART 引的 `_push_range_start` 與 `--push-remote/--pushed-ref` 已開檔驗存在)。
- 做法 4(註解改寫)、5(舊單結案)、6(寫回):已讀,無 finding。
- 回退:已讀,無 finding。
- 驗收條款:見 F5;S1~S5、S7 共用同一個測試名 `t_prepush_new_branch_block_range`,一條測試綁六條款,紅了無法定位,但屬寫法偏好,不標。

## 實務隱患(簡化鏡頭,逐類)
- 複雜度/維護面:新增 1 個指令、1 個掛鉤函式、1 個格式正規式、1 個退回分支、1 個新變數 `_brange`(掛鉤變成三個範圍名),見 F2、F4。
- 效能:每個新分支多一次 lumos 啟動,spec 已列,無額外。
- 金流/對外送出/不可逆:無,因為只動掛鉤範圍推導與唯讀指令。

## 圖譜鏡頭
派工時沒有附上計劃牽連的合約/事故節點,固定席判斷:無可逐條判的節點,無 finding。

總結:最嚴重 major,blocking 2 條(F1、F2)。
