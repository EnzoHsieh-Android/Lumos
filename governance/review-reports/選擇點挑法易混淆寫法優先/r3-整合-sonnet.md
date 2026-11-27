severity: major

## I1 新增的存活沿用比對只接在 choice-kill,推送閘與判讀入口還是對著新挑到的壞法處置存活
severity: major
blocking: 是(照第二條 WHY 自己寫的目的,存活的帳與畫面錯位這件事沒有被解掉)
引句:「沿用存活的那個分支(守的測試雜湊沒變的存活)多比一項」

1. 輸入:上線後帳上有一行,最新一筆是 survived,守的測試雜湊沒變,帳上 new_sha 是舊挑法的運算子壞法;新挑法挑到 API 壞法。
2. 計劃只改 `_choice_kill_pick`。
   - 我查了呼叫端:`_choice_kill_pick` 只被 choice-kill 的規劃函式用,`scripts/lumos:80164`。
   - 推送閘走的是 `_choice_push_judge`,`scripts/lumos:82366`。它對 `disp == "survived"` 直接把那行當存活,不比 new_sha。
   - 所以推送閘仍把這行列為存活。示例行(`_choice_push_show`)印的是現行挑法的壞法列,帳上卻是舊壞法的判定。第二條 WHY 的 [因] 要消除的錯位原樣存在。
3. 推送閘給的處置句也沒有導向重跑。`_choice_push_sub` 把這行歸「存活·未判讀」(判讀檔以 new_sha 對不上而作廢,`scripts/lumos:81263`),處置句是 `_CHOICE_PUSH_FIX`(`scripts/lumos:82261`)裡的「跑 lumos choice-layer --template,派全新代理判讀」。
   - 判讀材料與判讀事件取的是現行挑法的 new_sha(`scripts/lumos:81878`),也就是對一個從沒跑過的壞法做判讀。
   - 這行如果沒被回報上限抽中(`_choice_cap_pick`),連擋都不擋,choice-kill 也不會被叫去重跑。
4. 〈實務隱患〉寫「上線後第一次推送:多類同行的存活行要重跑、判讀要重做」,第二條 WHY 的 [代價] 同樣這麼寫。實際上推送閘只會要求「判讀要重做」,「重跑」要使用者自己想到去跑 choice-kill 才發生。文件講的第一次推送行為,跟程式路徑不符。
5. 驗收的缺口:S9 的測試名叫 `t_choice_pick_tier_survived_rerun_on_new_pick`,標題寫「推送前挑選要跑的壞法」,但預期值只描述 `_choice_kill_pick` 的輸出,沒有任何一條驗收覆蓋推送閘的存活列示,也沒覆蓋 `choice-points` 與 choice-layer 的材料。
6. 接手的人照〈做法〉只改 `_choice_kill_pick`,測試會綠,錯位在推送閘照舊。計劃要嘛把推送閘與判讀入口一併納入(例如帳上 new_sha 對不上時 `_choice_push_judge` 改判「過期」類,走重跑),要嘛承認推送閘不處理,並把〈實務隱患〉與 [代價] 改成實際行為。

## I2 兩份舊計劃與一條既有條款仍寫「存活照算給新壞法」「已 survived 而守的測試沒變應不重跑」,落點沒列
severity: minor
blocking: 否(這是文字漂移,不影響程式行為,但三個月後的人會讀到互相矛盾的敘述)
引句:「是當時的歷史描述,不改,補一句指到本計劃」

1. 〈落點〉對第二批計劃只補一句。但 `docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md:111` 同一句還寫「既有的殺掉、存活或放行照算給新挑到的壞法」,〈天花板〉第 5 條也是。這幾句在本計劃下對「存活」已經不成立。
2. `docs/lumos-toolchain-knowledge/Projects/改動選擇點都要有需求守住_計劃.md:212` 的 S11 是已綁測試的條款:「已 survived 而守的測試沒變的行 應 不重跑」。本計劃改成「壞法不同就重跑」,S11 沒列入〈落點〉。
3. `Systems/規格閘.md:87` 那條 WHY 也寫「沿用」規則,同樣沒列。
4. 與有效處置那條既有 WHY 的衝突:
   - 原文 [因:型錄改了、挑到的壞法換了,同一行的需求證據不該作廢;測試沒變重跑結果一樣] 與 [不選:鍵帶列號或壞法雜湊],我讀過,和第二條 WHY 沒有字面衝突。
   - 理由一:存活不是需求證據;理由二:new_sha 是值的比對,不是處置鍵;理由三:「測試沒變重跑結果一樣」在壞法相同的前提下仍成立。
   - 兩條 WHY 能並存,但前一條的 [因] 前半句會讓人以為存活也不作廢,建議在補的句子裡明寫「存活不算需求證據,所以不適用前半句」。
5. 〈落點〉所列四處原文我逐一核對,和計劃描述相符:
   - `Systems/規格閘.md:67` 的「類別用行指紋當種子洗牌」。
   - `Systems/規格閘.md:68` 的「論文整次呼叫洗一次類別」。
   - `Systems/規格閘.md:72` 的 survived 句。
   - `Projects/改動選擇點都要有需求守住_計劃.md:95` 的「把那一行有選擇點的類別…打亂」。

## I3 S10 只綁第二批那支釘值測試,第三批那支也要重釘卻沒綁
severity: minor
blocking: 否(全套測試會在推送前紅,不會漏過)
引句:「既有釘值測試 應 照新挑法重釘那 8 行、其餘行照舊 [test:t_choice_points_batch2_stable]」

1. 〈做法〉寫「兩支」釘值測試都要重釘。核對:`scripts/test_lumos.py:148731` 的 `_CB2_S7_PIN` 與 `scripts/test_lumos.py:149129` 的 `_CB3_S7_PIN` 各 82 筆,8 行都在兩邊。82 減 8 等於「其餘 74 行」,數字對。
2. S10 的 [test:] 只有 `t_choice_points_batch2_stable`,`t_choice_points_batch3_stable` 沒綁在條款上。

## I4 消費專案規則包與 lumos 版本錯位是「靜默、不提醒」,沒有回頭條件
severity: minor
blocking: 否
引句:「消費專案的規則包複本是舊 check.py、lumos 是新版時,表裡沒有 tiers,靜默退回舊挑法、不提醒」

1. 全域規則要求承認的風險要附 `REVISIT:` 回頭條件。這一條沒有。
2. 錯位期間存的帳是舊挑法;規則包升級的那一次,I1 說的存活重跑又會再發生一次。這是文件沒寫的第二次衝擊。

## 其他檢查項

- 論文 2102.11378(我用 pdftotext 讀原文核對):
  - 引言寫開發者起初把 85% 的回報壞法歸為沒用,文件寫法對。
  - 3.2.5 寫「progressively improved productivity to 89%」,同篇另有「from 15% to 89%」,文件寫法對。
  - Listing 2 的 `ops = shuffle(...)` 在逐行迴圈之外,所以「整次呼叫洗一次」成立;原文沒有提種子,文件「沒規定種子」也對。
  - 4.2 Listing 3 的 `order_by_historic_productivity(line, ops)` 依歷史存活率與開發者回饋排序,文件寫法對。
  - 「沒用約 11% 是本計劃換算」的說明合理。
- 釘版本的樣本引用 `configs/ast-grep/kotlin-choice/samples/arid.kt@f618b62cde0b:18` 與 `choice.kt@f618b62cde0b:58`:
  - 提交存在,樣本檔自該提交起至 HEAD 沒有改動。
  - 寫法符合「路徑@提交編號:行號」。
  - 逐行核對:arid.kt 第 18 行 `validator.require(x > 0)` 是直接子陳述的呼叫,所以會由 C-1 改成 C-18;choice.kt 第 58、60、61、66 到 69 行對應的 API 列號(C-20、C-22、C-23、C-28 到 C-31)正確。
  - 型錄各類列數(API 35、NUL 2、SBR 1、AOR 5、ROR 8、LCR 2、UOI 2,合計 55)與型錄實數一致。
  - C-31、C-37、C-43 到 C-45、C-54、C-55 都是 API 類。
- 〈做法〉的挑壞法、自檢、等級表與回退各節,與 `_choice_pick_iter` 現行寫法(`scripts/lumos:79358`)相容,已讀,無 finding。
- 牽連節點 `Systems/規格閘`:本計劃要改的是 WHY 文字與 choice-kill 的沿用條件。殺掉與放行的鍵不變,所以不破壞該節點宣稱的有效處置合約。破壞點只有 I1 那條存活路徑。
- 第一次推送的文件交代:見 I1 第 4 點,與程式實際行為不符,屬 I1 的一部分。

最嚴重:major
blocking 條數:1
