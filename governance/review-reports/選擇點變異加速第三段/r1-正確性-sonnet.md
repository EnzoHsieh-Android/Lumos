severity: minor

審查範圍:spec 全文逐節讀完,並對照 `scripts/lumos` 的現行程式。程式現況跟 spec 的假設相符之處如下,不列為 finding。
- 單支基準估算的三個案例(30/2/2/2、30/9/9/9、5.99 秒)逐步代入都成立。
- `_secev_junit_facts` 的 8 個代碼與 `test_quality.JUnitRejected` 的代碼一致。
- 治理帳沒有讀者依賴「結果檔讀不出來」這個確切字串。
- `cmd_guard_kill` 對每個平台只呼叫一次 `_kill_merge_iter`,所以 `mg.plats[c.plat] = (True, "")` 不會在跑到一半時重設已跳開的平台。

## Findings

1. 恢復條件把「編不過」也算乾淨,而且實務隱患節低估了恢復後又跳開的成本
severity: minor
   blocking: 否,這只會多付有上限的試探成本,不會判錯任何壞法
   - spec 段落:〈白話〉第 2 點、〈用詞〉「恢復」、〈做法〉2 的 `_kill_merge_breaker` 入口、〈實務隱患〉第一條。
   - 引句:「試探結果乾淨(通過、有失敗、編不過)就恢復合併」
   - 引句:「最壞多付 5 次快篩逾時,之後每 10 個試一次」
   - 會壞的順序:
     - 斷路器因 `report_malformed` 或 `zero_cases` 這類「讀結果檔失敗」跳開。
     - 下一個被拿來試探的壞法剛好編不過,`_choice_merge_classify` 回 `compile`。
     - `compile` 的條件是結果資料夾沒有任何 `TEST-*.xml` 且輸出符合編譯錯誤樣式。這一路根本沒讀過結果檔,不能證明「讀結果檔」那條路恢復了。
     - 斷路器仍照 spec 恢復:`streak` 歸零、`reopen` 加一。
     - 若沒跑乾淨集中在存活的壞法(完整跑完才寫大結果檔,見下),接下來要再吃滿 5 次沒跑乾淨才重新跳開。
     - 之後每個周期是 10 個壞法走逐支,加 1 次試探,再加 5 次白跑快篩,而不是 spec 寫的「之後每 10 個試一次」。
   - 程式佐證:
     - file: `/Users/enzo/harness/lumos-choice-speed3/scripts/lumos:28873-28876`。`compile` 只在「結果資料夾沒檔案、rc≠0、輸出符合編譯錯誤樣式」時回,不經 `_choice_merge_facts` 的讀檔判讀。
     - file: `/Users/enzo/harness/lumos-choice-speed3/scripts/lumos:29095-29108`。啟用狀態下 `compile` 本來就「不計不歸零」,代表它跟斷路器要守的故障無關。
   - 判準:恢復只該由證明結果檔讀得動的結果觸發(`pass`、`fail`)。`compile` 沒有這個證明,又被拿來歸零 `streak`。
   - 補充(spec 沒測到的路徑):
     - 〈驗收條款〉S2 只測「有失敗恢復」與「逾時維持停用」。
     - 沒有任何條款釘「恢復後再跳開」時 `trips` 2、`reopen` 1、`streak` 重新數 5 次。
     - 沒有條款釘 `compile` 的恢復行為。
     - 沒有條款釘試探結果是 `rc 不是 0`、`對不到名字` 這種不計斷路器的 `unclean` 時既不恢復也不再計數。

2. RETIRE-IF ① 的判準量到的是「結尾還停用」,不是「恢復後又跳開」
severity: minor
   blocking: 否,這是撤除條件的量法問題,不影響執行期行為
   - spec 段落:RETIRE-IF ①、〈做法〉2 最後一條(run 那筆記 `merge_trips`、`merge_reopen`)。
   - 引句:「恢復後大多又跳開,半開只是多付試探,拿掉半開回到跳開即停用」
   - 會壞的順序:
     - 一個平台上,每次跳開要嘛尚未恢復,要嘛已恢復。所以 `trips - reopen` 只可能是 0 或 1。
     - 判準寫的「`merge_trips` 大於 `merge_reopen`」只表示「這次呼叫結束時還停用」,跟「恢復後又跳開」無關。
     - 在 trips=3、reopen=2 的呼叫中,恢復後確實又跳開了兩次,但被判成跟「trips=1、reopen=0」同一類,而且 `merge_reopen` 非空的篩選又把後者排除了。
     - 反過來,trips=2、reopen=2(跳開、恢復、再跳開、再恢復)是半開反覆失靈,卻被判成健康。
     - 5 次呼叫累計到「超過一半」的門檻,可能純粹反映「當次呼叫結束時剛好還停用」的機率。
   - 程式佐證:file: `/Users/enzo/harness/lumos-choice-speed3/scripts/lumos:79122-79126`。run 那筆目前只有 `merge_tripped`(布林)與 `merge_off`,新欄位要照 spec 另加。判準因此只能用 spec 加的兩個欄位算。
   - 判準:要量「恢復後又跳開」,應直接記恢復後再跳開的次數(例如 `trips - 1`)。或者把判準改成「`merge_trips` 加總大於 `merge_reopen` 加總的 2 倍」。

## 逐節

- 白話:已讀,除上述兩條外無 finding。
- 實測(來源):已讀,無 finding(FACT 都帶來源與日期)。
- 用詞:「恢復」那條歸入 finding 1。其餘「能跑快篩的壞法」「斷路器停用」兩個定義跟 `_kill_merge_iter` 迴圈現況一致。
- 做法 1(量單支基準):已讀,無 finding。
  - 對照 `_kill_merge_singles`(`scripts/lumos:29030`)。
  - 兩支以內不收手,第三支起用 `measured[1:]`,S1、S7 逐步代入都成立。
  - 第一支被剩下時限截斷而逾時,仍走 `b_to and cap < full` 回 False。
  - 提示的 `c.merge_need` 在 measured 少於 2 支時用單價。這只影響第二支被截斷時提示的數字,不影響收手判斷。
- 做法 2(半開):除 finding 1 外無 finding。
  - `cool` 計數:第 11 個試探、試探後歸零、第 22 個再試,三處一致。
  - `streak`:啟用時才會更新,停用時不動,恢復時歸零,所以不會殘留舊計數。
  - `trips` 與 `reopen`:跳開時 trips 加一、恢復時 reopen 加一。
  - 沒產生快篩結果的路徑:`_kill_merge_apply` 回 `single` 的路徑在 `_kill_merge_screen` 進入 `_kill_merge_breaker` 之前就返回,spec 已寫明視同沒恢復。
  - `break`:還原失敗的 `break` 同樣在進入斷路器之前返回。
- 做法 3(拒收代碼):已讀,無 finding。
  - 代碼清單與 `JUnitRejected` 相符。
  - 斷路器鍵數上限 9 成立(8 個代碼加 `OSError`,另有大小上限一種)。
  - 計數與 `merge_unclean` 的鍵會變細。
  - 計數路徑讀 `why`,不依賴確切字串。
  - `_CHOICE_MERGE_BASE_WHY.get(why, why)` 沒有該鍵時照原字串帶出。
  - 基準那條路的 `why.endswith("對不到結果檔裡的名字")` 不受影響。
- 做法 4(`merge_why`):已讀,無 finding。
  - `kinds` 與 `whys` 的鍵都是 `(平台, group)`,跟 `finish` 讀 `kinds` 的鍵一致。
  - 型別登記與缺欄讀成空字典照 `merge_kind` 的既有型式即可。
- 預期效益、不做、回退、實務隱患:除 finding 1、2 外無 finding。
- 驗收條款與預期值表:S2 缺口已併入 finding 1。其餘案例可執行。

## 實務隱患鏡頭

| 風險類 | 判定 | 理由 |
|---|---|---|
| 併發與交易 | 無 | 一次呼叫、一棵工作樹、一條執行緒;`cool`、`trips`、`reopen`、`whys` 都是呼叫內的記憶體狀態。 |
| 不可逆 | 無 | 帳上只新增欄位。半開失靈的最壞結果是多跑快篩,不會誤判存活;存活判定仍來自「通過」的快篩。 |
| 資料外洩、金流、對外送出 | 無 | 只在本機跑測試。 |
| 時間與時限 | 有,見 finding 1 | 試探快篩沿用既有上限。 |
| 效能 | 有,見 finding 1 | 持續失靈時每個周期的白跑次數比 spec 寫的多。 |

## 固定席(guard-kill)

- `t_guard_kill_rc_precedence`:不影響。設計只改合併快篩的斷路器與估算,不碰 `cmd_guard_kill` 的 rc 判定。
- `t_guard_kill_json_purity`:不影響。
  - 合併只由 `choice-kill` 啟用,它用 `contextlib.redirect_stdout` 吞掉 `cmd_guard_kill` 的 stdout,見 `scripts/lumos:28470`。
  - 新增的「恢復合併」那行 spec 沒寫輸出到哪一路。依現有斷路器提示都走 stderr,實作應照做;若誤印 stdout 只會被吞掉,不會破壞 JSON 純度。

最嚴重 severity:minor;blocking 共 0 條。
