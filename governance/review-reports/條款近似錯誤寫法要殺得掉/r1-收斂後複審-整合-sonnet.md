**severity: major**

## i1 推送前那一道要的「範圍右端」在現有程式裡不存在
severity: major
blocking: 是。照字面實作時,「同 `_spec_gate_push_check` 解析範圍的方式」找不到可抄的東西,實作者只能自己發明;發明得不同,「old 在推送版本恰好出現一次」就會誤擋或誤放。
- 位置:範圍 3。
引句:「被推送版本取範圍右端(同 `_spec_gate_push_check` 解析範圍的方式;算不出照那支既有的放行規則)」
- `_spec_gate_push_check` 只拿到範圍字串,只跑 `git diff --name-only <範圍>`,沒有任何取右端提交的步驟。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:17387`
- 既有的 `_range_base` 只取左端(起點),不取右端。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:65111`
- 計劃文字(含 `[near:]` 宣告)讀的是工作目錄,不是推送版本;預期值表那一道也是如此。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:17346`
- 於是同一次檢查會讀到兩個時間點:宣告來自工作目錄,`old` 的出現次數來自右端。
- 例:推 `A..B`,但 HEAD 比 B 新,HEAD 的計劃多了一個未推的 `[near:...]`。
  - 預期:只查 B 版本的宣告。
  - 實際:工作目錄多出的宣告被要求有紀錄,誤擋。
- 要補的規格:
  - 右端怎麼算(`a..`、`a...b`、右端為空)。
  - 計劃文字與程式檔是否都改讀同一個版本,還是明文接受兩個時間點。
  - 在天花板補一條。

## i2 型錄不在或版本不一致時,形狀檢查與推送閘的行為沒寫,字面實作會和既有先例相反
severity: major
blocking: 是。「列號不存在、識別字不在那列」一律判形狀不合,字面實作遇到型錄缺檔會把每個宣告都判不合,且報錯是誤導的「列號不存在」。
- 位置:〈用詞〉掃描、範圍 1、範圍 3。
引句:「對不上(全形冒號、大寫、空標記、列號不存在、識別字不在那列、含多餘 `]`)一律判形狀不合」
- 既有先例(2026-11-06 編排者裁定):型錄或規則包自檢程式不在,算環境不可用,只提醒、記帳、不擋;檔在但讀表失敗才擋。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:39151`
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:74610`
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:40192`
- 型錄隨工具鏈安裝,和消費專案的程式碼是兩個版本。
  - 例:作者機器的 D-4 觸發字含 `flatMapConcat`,CI 機器裝的是舊版型錄。
  - `[near:D-4:flatMapLatest→flatMapConcat]` 在 CI 變成「形狀不合」,推送被擋,專案本身一個字沒改。
- 型錄規則是「刪列只標停用、觸發字改成 `(無)`」。列一停用,舊計劃只要再被碰到,宣告就全部作廢。
  - 計劃改完仍是 done 狀態時也一樣會被擋。
- 要補的規格:
  - 型錄缺檔時,規格閘與推送閘各怎麼辦,是否照 `_KT_DT_MISSING` 先例只提醒。
  - 宣告被推送閘檢查時,是否要讀型錄。
  - 有效紀錄只比 `near` 文字,不依賴型錄。

## i3 「同一列觸發字就是兄弟寫法」的前提不成立,舊否決 d1 的比對理由站不住
severity: minor
blocking: 否。不會誤放行:無意義的配對編不過,記成弱證據;等價的配對判 survived,要走人核可。代價是摩擦,還有 〈舊否決比對〉寫的是錯的。
- 位置:〈舊否決比對〉第一條、〈用詞〉兄弟寫法宣告。
引句:「等價問題在型錄寫列時已經判過;零依賴照守」
- 型錄「觸發字」欄是偵測詞表,不是行為相異的兄弟清單。
- D-4 的觸發字是 `debounce、flatMapLatest、collectLatest、viewModelScope.launch、flatMapConcat、flatMapMerge、mapLatest、transformLatest`。
- 同列「標準寫法」欄明寫「`mapLatest`、`transformLatest` 同類:新值來時取消前一個」,也就是行為等價。
  file: `/Users/enzo/harness/lumos-near-miss/skills/kotlin-idioms/checks-catalog.md:743`
- 例 1:`[near:D-4:flatMapLatest→transformLatest]` 形狀合法。
  - 編得過就是等價變異,測試永遠不會紅,一定 survived。
  - 之後只能靠人核的 `ack-survived` 脫身。
- 例 2:`[near:D-4:debounce→flatMapLatest]` 形狀合法。
  - 換了編不過,記成弱證據,不記帳。
- 只有 `[near:D-4:flatMapLatest→flatMapConcat]` 這種真兄弟才有意義。
- 我另外數過:決策表約 60 列,觸發字不足兩個識別字的有 D-1、D-2、D-19、D-20、D-60 五列。
- 建議:
  - 把「等價問題已判過」改成「等價配對會 survived,走 ack」。
  - 或在型錄加一欄「互換組」。
  - 否則這份算部分翻了 d1,要照翻案寫法記。

## i4 條款若尚未進入進行中,設計審看不到宣告,天花板 4 的「靠設計審」落空;規格閘端的「進行中」也沒定義
severity: minor
blocking: 否。不會做出錯的判定;補救是沒有人審選哪一列,以及規格閘端缺一句狀態定義。
- 位置:〈用詞〉適用的計劃、範圍 1、天花板 4。
引句:「條款跟兄弟寫法是不是在講同一件事,機器只驗列號與識別字合法;選錯列靠設計審」
- 適用要求計劃是進行中,待辦(todo)狀態不要求宣告。設計審通常在 todo 階段跑,審材裡根本沒有 `[near:]`。
- 預期值表那道的 `_expected_requirement` 不看狀態,規格閘當場就要求表。`[near:]` 這道卻等到 status 變 doing 才要求,兩道同家族,時機卻不同。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:14595`
- 「進行中」借自 `_live`,那是 `_spec_gate_push_scan` 內的區域函式,靠推送範圍的 `touched_plans` 判「這次推送改到的 done」。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:17254`
- 規格閘指令沒有推送範圍,規格閘端「進行中」怎麼判是空白,S1、S10 沒法照寫測試。
- 建議:
  - 規格閘端只認 doing。
  - 或不看狀態,與預期值表一致。
  - 天花板 4 改寫成「靠代碼審」或明講設計審看不到。

## i5 推送前要求「每個宣告」有紀錄,但「要宣告的條款」之外的條款上寫了標記就永遠過不了
severity: minor
blocking: 否。作者拿掉標記就解了,但規格沒講,實作會各做各的。
- 位置:範圍 3、〈用詞〉要宣告的條款。
引句:「每個兄弟寫法宣告要有有效紀錄、每個免宣告要有對得上的免宣告核可、每個存活後改寫要有核可」
- 要宣告的條款已扣掉 `[manual:]`、`[keeps]`、人裁寫回的條款。
- 例:`- [S5] 當…,應… [manual:人驗] [near:D-4:a→b]`。
  - clause-kill 對「沒綁測試的條款」回 rc 2,不可能產生紀錄。
  - 若推送閘照字面對「所有宣告」要紀錄,這條推送永遠被擋。
- 同理:人裁寫回的條款即使自填 `[near:]`,是否要紀錄也沒寫。
- 要補的規格:
  - 推送閘只檢查要宣告集合裡條款上的標記。
  - 其餘條款上的標記只做形狀檢查,不要求紀錄。
  - 補一列預期值。

## i6 clause-kill 的「弱證據」只用 `weak` 旗標定義,漏了 `killed_unattributed` 與 `timed_out_weak` 兩個判定;訊息分流沒有它們
severity: minor
blocking: 否。結果是不記帳 rc 2,方向對;但引導訊息可能錯。
- 位置:範圍 2「記」、S7、〈用詞〉殺得掉。
引句:「從 `result_out` 的列讀,不看回傳碼——`cmd_guard_kill` 對弱證據的 killed 也回 0」
- 兄弟寫法漏 import、編不過是 Kotlin 上最常見的失敗。
  - 紅燈沒有歸因到指定測試,判定是 `killed_unattributed`,`weak` 旗標是 false(旗標只由 run_cmd 整套跑、flaky、筆記髒、修改時間沒錯開決定)。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:27978`
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:28009`
- 單一配方只有未歸因時,`cmd_guard_kill` 回 rc 1,和 survived 同碼。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:28064`
- 所以「對弱證據的 killed 回 0」只對 `weak` 旗標成立,對未歸因與逾時不成立。
- 規格列了「弱證據與 abort 印失敗摘錄、drifted 說換 --line、survived 才說補測試」,沒有第四種。
- 例:`flatMapConcat` 沒補 import,Gradle 編譯失敗。
  - 預期:rc 2、印失敗摘錄、說用 `--import`。
  - 若實作者只用 `weak` 旗標分流,它會落到「其他」,可能印成「補測試讓它紅」。
- 建議:S7 明列四種判定,另開一列預期值(編譯失敗 → 印摘錄、提示 `--import`、不記帳)。

## i7 `--line` 救不了「相同文字出現多次」,drifted 的建議訊息會把人帶進死路
severity: minor
blocking: 否。結果是只能走免宣告,但訊息誤導。
- 位置:〈用詞〉壞法、範圍 2 記的訊息分流、S8 的「old 恰好一次」。
引句:「drifted 說換 `--line` 或檢查原寫法」
- guard kill 套壞法是以文字比對:`src.count(old)` 必須恰為 1,否則判 drifted。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:27937`
- `old` 是整行文字,行號只決定取哪一行的文字,不傳給 guard kill。
- 例 1:同一檔有兩行完全相同的 `        .flatMapLatest { repo.search(it) }`。
  - 換 `--line` 後 `old` 文字不變,仍是 drifted。
  - 該條款只能走人核免宣告。
- 例 2:一行是另一行的子字串(縮排較少),`count(old)` 也是 2。
- 建議:
  - 在 clause-kill 先用 `src.count(old)` 預檢,rc 2 並明講「這行文字在檔裡不唯一,擴成多行 old 或改寫」。
  - 或讓壞法以「前後各帶一行」的多行片段當 `old`。
  - drifted 訊息不要再建議換 `--line`。
- 另:`old` 要從和 guard kill 相同的解碼方式取(它用 universal newline 讀,CRLF 檔不帶 `\r`),否則 `count` 為 0。

## i8 治理帳登記與讀者的接線不完整
severity: minor
blocking: 否。逐項都能在實作時補,但規格現在沒寫,S11 的預期數字會因此錯。
- 位置:範圍 4、S11、〈用詞〉免宣告核可與存活後改寫。
引句:「`clause-kill` 加進 `_KNOWN_GATES`、`LOOP_NOT_CLOSE_EVENTS`、gov 的去重 token(帶 `token` 欄,同人裁)」
- gov 去重鍵是 `(commit, nodes, gate, kind, token, check)`。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:18359`
- token 只在 `_gov_row` 裡對列舉過的閘才取值。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:18286`
- 〈用詞〉只給有效紀錄(killed/survived)列了 `token`;`waive` 與 `ack-survived` 的欄位沒有 token。
  - 同一提交、同一計劃、兩個不同條款各 `--waive`,會被折成一筆。
  - gov 的免宣告數與存活後改寫次數少算。
  - 人裁的做法是 `ts + clause_id`,這裡也要補。
- `_gov_row` 只帶少數欄位,不帶 `verdict`。
  - killed 與 survived 的 kind 都是 `clause-kill`,所以 S11 的殺掉率 3/4 算不出來。
  - 規格要寫「mapper 帶 `verdict`、`near`」。
- `LOOP_NOT_CLOSE_EVENTS` 是 `(gate, kind)` 的集合,要登記三種 kind(clause-kill、waive、ack-survived),不是一個閘名。
  - 斷言它是否完整的測試只掃 design-loop、code-loop 兩個閘,所以這一項實際上無作用。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:20643`
  file: `/Users/enzo/harness/lumos-near-miss/scripts/test_lumos.py:65789`
  - 規格要說清楚是為了誰而登記。
- `_GOV_FIELD_TYPES` 是全域表,新欄位 `near_index` 要列 `(int,)`(`bool` 也是 `int`,讀端要排除);版控帳讀者不經這張表,要自己驗型別(對照 `_spec_gate_ruled_events` 的 `isinstance` 檢查)。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:18199`
- 長時間 Gradle 跑完,治理帳寫失敗怎麼辦沒寫。
  - 人裁有補記指令(`_situation_rule_miss_text`),clause-kill 只說「沿用訊號收尾」。
  - 這一筆結果是要跑十幾分鐘才有的證據,應印出可原樣貼回帳尾的那一行。
  file: `/Users/enzo/harness/lumos-near-miss/scripts/lumos:75924`

## i9 RETIRE-IF 的三個條件,現有的記帳與 S11 量不到
severity: minor
blocking: 否。只是撤除機制空轉;全域規則要求撤除條件要量得到。
- 位置:RETIRE-IF、REVISIT、範圍 4、S11。
引句:「①宣告的兄弟寫法第一次跑就殺掉的比例超過九成五(型錄的兄弟寫法對實際測試沒有鑑別力),②推送前因缺紀錄被擋的次數裡超過一半是工具誤判,③條款裡 `[near:無 …]` 的占比超過一半」
- ① 要的是「每個宣告第一次跑」的殺掉率。S11 印的是全部紀錄的 killed 比例,存活後補測試再跑的 killed 會混進去。
  - 要在帳上或統計裡標出第幾次跑。
- ② 要的是「推送前因缺紀錄被擋」的次數與「誤判」。
  - 預期值表那道會寫 `expected-unsigned` 這類擋下事件,近似道沒有。
  - 誤判也沒有表態來源。
  - 要加一種擋下事件(例:`gate=clause-kill, kind=blocked`),還要有判誤判的方式。
- ③ 分子是已有核可的免宣告(帳上),分母是計劃裡的 `[near:` 總數(計劃文字)。
  - S11 只印「免宣告 1」這樣的個數。
  - 核可通常晚於宣告,帳上拿不到「占比」。

## i10 存活後改寫的核可綁條款編號,改編號就繞得過
severity: minor
blocking: 否。需要刻意多步,但這個洞不靠偽造帳,正常編輯就能走到。
- 位置:〈用詞〉存活後改寫、S9。
引句:「帳上有某條款某個兄弟寫法判 `survived`,而現在那一行已經沒有同一個標記原文(改寫、刪掉、改成免宣告)」
- survived 紀錄綁在 `clause_id`(例 `S2`)。
- 例:S2 對 `flatMapConcat` survived。
  - 作者把這條改編號成 `S12`、換成別的宣告,舊的 survived 在 S12 底下找不到。
  - 結果:S12 沒有任何紀錄,重跑 clause-kill 即可,不需要 `ack-survived`。
- 同理:計劃改名或搬路徑,`plan` 欄對不上,也繞過。
- 建議:存活後改寫的比對改用 `clause_sha` 或計劃內「survived 過的 (近似寫法, 原寫法)」二元組;至少把「改編號與改計劃路徑算不算改寫」寫進天花板。

## 其餘:已讀,無 finding 的節
- 範圍 1 的 S2 預期值列、S3:`_clause_body_of` 是規格閘與處置閘第五步共用的條款文法入口,加剝除只影響兩邊同一份;「同源」那條 KEY 不受影響。
  - 一個小提醒:掃描先遮反引號,剝除不遮。
  - 規格自己的 S12 把 `` `[near:D-4:...]` `` 寫在反引號內,會被剝除正規式吃掉,`_clause_sha(keep_code=True)` 因此與原文不同。
  - 建議在 S3 加一列「反引號內合法標記」的預期值,並決定要不要讓剝除也遮反引號。
- 交叉引用:範圍 N、S1 到 S12、預期值表各列對〈用詞〉的指向,逐條核對過,都存在且說法一致。

## 固定席:對節點宣稱的行為與合約的影響
- ‹Systems/guard-kill› KEY ★INVARIANT★ rc 優先序:不影響。
  - 理由:`cmd_guard_kill` 只多一個只影響殺傷力帳本 `source` 欄的選用參數;rc 優先序的判斷不改。
  - clause-kill 從 `result_out` 的列分流,不依賴 rc。
  - 注意單一未歸因時 rc 是 1(見 i6),所以讀列而不讀碼是對的。
- ‹Systems/guard-kill› KEY ★INVARIANT★ `--json` 成功時 stdout 恰一行 JSON:不影響。
  - 理由:clause-kill 不傳 `as_json`,不動 stdout 格式;`source` 只寫殺傷力帳本。
  - 但 clause-kill 本身把 `cmd_guard_kill` 的人讀輸出印到 stdout,文件上不要宣稱它有 `--json`。
- ‹Systems/規格閘›:不影響。
  - 理由:沒有合約行;「風險高只印不擋紅綠」那條講的是紅綠,預期值表已是先例,近似宣告檢查同樣是表格形的前置檢查。
  - 「條款判定與處置閘第五步同源」那條,會因 `_clause_body_of` 共用而同時套用到兩邊,S3 的測試要覆蓋兩邊。

## 實務隱患鏡頭
- 輸入與跳脫:`old`、`new` 來自程式碼行,可能含終端跳脫字元或超長字;規格只限 500 字。
  - 擋下訊息(「說過期」那類)若回印 `old`,要走 `_kill_esc`;宣告標記本身有形狀檢查,安全。
  - 規格沒寫,但屬實作細節,不另列 finding。
- 路徑:`--file` 用 `cmd_guard_kill` 的 realpath 圍欄;壓住逃逸。
- 併發:建議把多個宣告放背景並行跑。
  - 治理帳追加是單次寫入一行。
  - Gradle 同一專案目錄與 `~/.gradle` 鎖可能互相搶,但單人依序操作的前提(專案威脅模型)下可接受。
- 效能與記憶體:帳讀一次共用 `ctx["exp_gov"]`,沒有新的整帳重讀;每筆事件至多約 1.2KB,帳膨脹可忽略。
- 資安:`old` 這種程式碼行寫進版控帳。同一個 repo,不外洩;若該行含祕密,祕密早就在檔案裡。
- 相容:CRLF 檔見 i7;Windows 路徑、非 UTF-8 檔 `cmd_guard_kill` 已有處置。
- 偽造:天花板 3 已明講,範圍外。

最嚴重:major;blocking 共 2 條
