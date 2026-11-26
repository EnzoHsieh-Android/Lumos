severity: minor

我只跑了三支綁定測試,三支都綠:`t_choice_kill_merge_events_cmd` 17、`t_choice_kill_merge_events_order` 15、`t_choice_kill_merge_hang_breaker` 21。我另外把審查用的 repo 暫時切到固定版本(detached HEAD),已切回 `choice-kill-speed4`,HEAD 仍是 ac80263d,沒有留下改動。

### Finding 1
severity: minor
blocking: 否
歸因:有證據的修復回歸(修補新增了行為與測試,但驗收條款與預期值表沒跟上)
引句:「- [S6] 當帶腳本的合併基準 rc 1 而且沒寫結果檔、不帶腳本那次通過時,choice-kill 應 印「帶事件初始化腳本的合併基準不通過」」
- 修補新增「重試的上限照剩下的總時限重算」(`_kill_merge_base` 的 `min(cap, max(mg.remaining(), 1.0))`),測試也加了斷言(重試上限 ≤ 30)。
- 但計劃的 S6 條款、預期值表、〈做法〉第 1 條都沒寫這個行為。
- 三個月後的接手者從條款讀不到這條要求,有人把 `min(...)` 改回 `cap`,條款與預期值表都不會告訴他錯了。
- 同樣的缺口還有 S3:新增了「跳開、恢復後從頭數」兩個案例,條款與預期值表沒對應。
- S2 也有缺口:新增了長行不回溯、行尾 `\r` 兩個案例,條款沒對應。
- 守檔筆記 `guard-kill.md` 的 WHY 已寫「上限照剩下的總時限重算」「兩個連續計數都歸零」,只有計劃的條款落後。
- 重試上限的測試因此沒有 S 條款可綁。
- 最小重現:`grep -n 'S6\]' 計劃.md` 看不到「剩下的總時限」。

### Finding 2
severity: minor
blocking: 否
歸因:有證據的修復回歸
引句:「elif why == _CHOICE_MERGE_HANG_WHY:   # 另外數,不動 streak;到 _CHOICE_MERGE_HANG_BREAKER 照跳開的寫法跳開」
- 程式現在到的是 `mg.hang_breaker`,不再是常數 `_CHOICE_MERGE_HANG_BREAKER`。
- 這行註解和 `_kill_merge_breaker` docstring 的「恢復(啟用、streak 歸零、…)」都沒更新。
- docstring 只提 `streak`,實際恢復與跳開時 `hang_streak` 也歸零。
- 照註解做的人會去改常數,而測試用 `hang_breaker=3` 帶入的路徑不會受影響。
- file: `scripts/lumos:29226` 與 `scripts/lumos:29243`

### Finding 3
severity: minor
blocking: 否
歸因:有證據的修復回歸
引句:「前面是類別、後面去掉事件字樣是測試名(所以測試名可以含 ` > `)」
- 計劃〈用詞〉寫「後面只准有行尾空白」,舊正規式只吃 `[ \t\r]`。
- 新的 `_choice_merge_event_line` 用 `line.rstrip()`,會多吃 `\f`、`\v`、全形空白等。
- 只影響順序,不影響結果判定,但「用詞」與程式不再逐字相同。
- 我沒有跑案例,是從程式與計劃用詞對照得出的差異。

### Finding 4
severity: minor
blocking: 否
歸因:未判定
引句:「- Kotlin 反引號測試名含 `(`:身分照既有 `_choice_merge_fullname` 從第一個 `(` 截掉,事件對不到那支、落未知層」
- 這條實務隱患寫在計劃裡,但 `guard-kill.md` 沒有對應的 PITFALL 或 RULE。
- 它是已知的順序降級,沒有 `[test:]` 或 `[repro:]` 綁定。
- 接手者在筆記圖譜裡查不到,只能從計劃裡找。

### 已驗主張與證據
- **原問題的修復效果**
  - 斷路器:`_kill_merge_trip` 兩種計數共用,跳開與恢復時 `streak`、`hang_streak` 都歸零。程式比對如此,新增的兩個 S3 案例(15 次跳開、恢復、再 1 次不跳開;3 次掛住加 5 次逾時、恢復後 14 次不跳開)在三支測試裡綠。
  - 事件行解析:改字串切分,線性。新增的六萬個 ` > ` 長行測試在一秒內通過。
  - 重試上限:重算 `min(cap, 剩下總時限)`,假 `_kill_run` 案例斷言兩次上限是 100.0 與 ≤ 30。
- **相鄰路徑**
  - `_cmd_arg_quote` 由 `_run_cmd_expand` 與 `--init-script` 共用,Windows 與 POSIX 的分支搬移前後相同。
  - 事件行 `A > B > C FAILED`、`Foo >  STARTED`、`A > FAILED`、`B\tFAILED` 等邊界,我逐條比對舊正規式與新函式,結論相同。
  - `_kill_merge_trip` 把 `streak` 也歸零:全檔 grep 沒有其他讀 `streak` 的呼叫端,跳開後被停用,所以不影響。
- **同一案例修前與修後**
  - 15 次跳開、恢復、再 1 次掛住:修前恢復只清 `streak`,`hang_streak` 還是 15,下一次掛住就又跳開;修後歸零、不跳開。這是從程式 diff 推得的,我沒有在修前版本上實際跑過。
- **未驗範圍**
  - 沒有對新增斷言做變異驗證:嘗試把重試上限改回 `cap` 時,複製出來的 repo 缺環境、只得到無關的 `NoneType` 例外,沒有得到可用的紅結果。
  - 沒有跑全套測試。
  - 沒有核對 `規格閘.md` 與前三段計劃的「部分被取代」註記,這次修補沒改到它們。

### 三問
- **文件現在對得上程式嗎?**
  - 守檔筆記 WHY 對得上。
  - 計劃〈做法〉3、〈落點〉、〈回退〉、〈用詞〉事件行已更新,對得上。
  - 驗收條款與預期值表落後(finding 1),另有兩條註解過期(finding 2、3)。
- **修補有沒有引入新問題?**
  - 沒有行為上的回歸。程式與測試一致,只有文件與註解的同步缺口。
- **接手者最可能撞牆的地方?**
  - 重試上限與恢復後重算這兩條行為只存在測試與 WHY,不在條款。
  - 註解指向常數而實際走 `mg.hang_breaker`。

最高 minor,blocking 0 條
