severity: major

## F1 存活行的帳與畫面錯位只在 choice-kill 那一條路修掉,推送閘、choice-points、choice-layer 還是把舊存活配上新壞法
severity: major
blocking: 是(spec 自己的 WHY 要防的症狀,照〈做法〉實作後仍會在另外三條讀帳路徑發生)
引句:「不然帳上寫「存活」、畫面顯示的卻是從沒跑過的新壞法,人會對著錯的壞法補測試或放行」

1. 輸入:上線前帳上有一行,最新一筆是 survived、守的測試雜湊沒變、`new_sha` 是舊挑法的運算子壞法。上線後這行改挑到 API 壞法。這行不用特殊構造,就是 spec 想解決的那種行。
2. 我在臨時 clone 照〈做法〉只改 `_choice_kill_pick`,再用這個輸入跑,結果如下:
   - `_choice_kill_pick` 把這行排進重跑,spec 修的那條路成立。
   - `_choice_push_judge` 照樣把它歸成「存活·未判讀」,推送閘擋下並顯示新壞法(`_choice_push_show` 讀的是 `x["mutant"]["row"]`)。處置句是補測試或放行,不是「先重跑 choice-kill」。
   - `_choice_layer_survivors` 照樣把它列為存活行。choice-layer 會替這個從沒跑過的 API 壞法產判讀材料,事件寫的是 `x["mutant"]["identity"]["new_sha"]`。
   - `_choice_ledger_status` 這個 choice-points 印帳上狀態的函式只認 `_choice_disposition`,同樣印「存活」。
3. 壞在哪:`_choice_disposition`(`scripts/lumos:79774`)的 survived 判定完全不看 `new_sha`。使用者在上線後第一次推送遇到的是推送閘,不是 choice-kill。他會對著 API 壞法寫測試,或用 `lint-waive` 放行(鍵是 (檔, 行指紋),放行不帶壞法)。放行後這個 API 壞法從沒跑過就成了有效處置。這正是〈做法〉WHY 第二條要防的錯位,只是出現在另外三條讀帳路徑。
4. 缺的東西:spec 沒有一條驗收條款涵蓋這三處。S9 只驗 `_choice_kill_pick`。〈實務隱患〉只承認 killed 與 waived 行的落差,沒提 survived 行在閘上的顯示。
5. 要補的方向:把「survived 且 `new_sha` 對不上」併進 `_choice_disposition` 或各讀帳路徑(判成缺紀錄,閘叫人重跑),並補對應測試。

## F2 既有兩支測試用不帶 mutant 的合成行呼叫 _choice_kill_pick,加上 new_sha 比對後直接 KeyError,spec 沒列
severity: minor
blocking: 否(實作時跑測試就會發現,不會漏進產品,只是〈做法〉漏列要改的測試)
引句:「實作時用 `-k choice` 跑一遍找有沒有別的釘值也被帶紅。」

1. 我照〈做法〉加上 `evs[-1].get("new_sha") == x["mutant"]["identity"]["new_sha"]` 後跑了兩支既有測試,都是 `EXCEPTION: 'mutant'`:
   - `t_choice_kill_rerun_rules`(`scripts/test_lumos.py:145394`,裡面的 G3 對照「survived、守的測試沒變 → 帶過去」)。
   - `t_choice_kill_test_files_in_test_paths`(`scripts/test_lumos.py:145995`)。
2. 這兩支的合成行 `x = {"file":…, "status":"mutant"}` 沒有 `mutant` 鍵,事件也沒有 `new_sha`。spec 只提到 8 行釘值要重釘,沒說這類測試要補 `mutant.identity.new_sha` 與事件的 `new_sha`。
3. 實作端要先決定:是讓這兩支測試補欄位,還是用 `.get` 防呆。用 `.get` 防呆的話,合成行與事件兩邊都缺時會 None == None 而沿用,測試靜默綠。建議明寫成要補欄位。

## F3 S6 與 S8 的測試在改之前的程式上就是綠的,不會對症狀翻紅,只能當守衛
severity: minor
blocking: 否(兩條都是守衛性質的條款,只是違反「先紅」的慣例,不影響行為正確)
引句:「推送前挑選要跑的壞法 應 讓殺掉與放行的行照舊不重跑、過期與跑不出結果的行用新挑法重跑」

1. S6:改之前的 `_choice_kill_pick` 對 killed、waived 本來就不比 `new_sha`,對 stale、no_result 本來就重跑。五列在現行程式上全綠,它守的是「不要把 new_sha 比對擴到 killed/waived」,不是新行為。
2. S8:沒有 tiers 的現行程式,在 API 候選全被排除或全在跳過集合時本來就往下挑 ROR,所以案例一、案例二現行就綠。它守的是「別寫成只取最高級」。
3. S8 還有一處措辭問題。「回用盡」的 `exhausted` 狀態是 `_choice_line_pick`(`scripts/lumos:79431`)依 skip 與 `pick()` 算的,`_choice_pick` 本身只回 None。S8 的測試要走 `_choice_file_points` 才驗得到用盡,spec 沒寫明。
4. 這兩條如果要有翻紅的證據,得靠變異(把第 2 級以後砍掉)翻紅,spec 的預期值表沒有這樣寫。

## F4 沿用比 new_sha 會讓「檔案 blob 改變、跳過集合失效」的存活行每次不相關編輯都重跑
severity: minor
blocking: 否(只多花 choice-kill 時間,不漏判)
引句:「帳上那筆的壞法(new_sha)跟這次挑到的一樣才沿用」

1. 輸入:某存活行的第一候選曾經編不過。合批編譯檢查換成第二候選,帳上記的是第二候選的 `new_sha`。
2. 之後該檔在別處被改,blob 變了,跳過集合(要求 blob 相同)失效,`_choice_pick` 又先挑回第一候選,`new_sha` 對不上,這行重跑。
3. 同理,`_choice_identity` 的 `old` 視窗會因為檔內別處新增重複文字而往外多帶行,`new_sha` 跟著變。
4. 以前這兩種情形都沿用,現在都重跑。〈實務隱患〉與回退節沒提。

## 已驗證成立的部分
- 〈做法〉第 64 行把比對放在 survived 且守的測試雜湊沒變的 `elif` 分支(`scripts/lumos:80075`)。這個分支只在 `evs[-1].get("via") != "cov"` 時走到。覆蓋判的 survived 分支、killed、waived、stale、no_result 的條件都沒動。`--only` 路徑被 `only is None` 擋掉,不受影響。`not_unique` 在更前面就被 `nu.append` 攔走,不會對 `identity=None` 取 `new_sha`。這部分判斷成立。
- 8 行重釘的值成立。我在臨時 clone 照〈做法〉實作(`CHOICE_TIERS`、`tiers` 參數、partial 傳遞、自檢、沿用比對),跑 `-k choice_points` 後 `batch2_stable` 與 `batch3_stable` 各紅一個斷言。差集正好是 8 行,新列號與 spec 全部一致:arid.kt:18→C-18(delete),choice.kt:58→C-20、60→C-22、61→C-23、66→C-28、67→C-29、68→C-30、69→C-31。總 82 行、其餘 74 行不變。
- `choice_tables` 的 `tiers` 鍵會被 `_choice_tables` 整份傳出去,`_choice_pick` 的唯一正式呼叫端是 `_choice_file_points`,沒有別的呼叫端漏傳 `tiers`。
- 同級行與沒傳 tiers 時打亂結果跟改之前相同。S1 到 S5、S10 照字面寫都會對症狀翻紅或維持,已讀,無 finding。
- S9 的測試照字面寫會對症狀翻紅:現行程式把「測試雜湊沒變」直接沿用,加上 `new_sha` 比對後才改成重跑。
- 牽連節點 `Systems/規格閘`:這份計劃只動挑壞法的順序與沿用條件,不動殺掉與放行的鍵,沒破壞該節點宣稱的有效處置決策。但該節點若有「存活行畫面與帳一致」的宣稱,F1 的缺口會破壞它。

最嚴重:major
blocking 條數:1

殘留:`/private/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 底下還有我這次跑測試留下的 `gctl-run-*` 現場。已確認是我的三個都刪了,剩下幾個沒有 lsof 證據證明是自己的,沒動:`gctl-run-cfygc2bt`、`gctl-run-h7d6_fzy`、`gctl-run-vb6zov_b`、`gctl-run-1c3jl4hv`、`gctl-run-jo1m5v54`、`gctl-run-jr0izzeg`、`gctl-run-yuqsnc5t`、`gctl-run-1tynepz9`、`gctl-run-b7pawx8m`(其中可能有被我中途 kill 的 `-k choice` 那輪)。臨時 clone 目錄已刪。
