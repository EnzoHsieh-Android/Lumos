# code-收證認得Truth與裝置字串比較 r2 收貨紀錄

材料:修補差異拆兩包(A 包程式、標準與筆記 678 行給通才席與架構對齊席;B 包公開卷證與三本帳 947 行給卷證席);修前 c08dc36 → 修後 d5e8f27,修前不是修後的祖先(歸因界線見 r2-repair-binding.json)。

收貨:三份報告從逐字稿存檔,從檔級等級那行起存;卷證席報告經 report-normalize --write 搬了 6 處。quote-check:卷證席、架構對齊席全數錨定;通才席第 5 條引句錨不到(引的是驗證紀錄,不在 A 包),由編排者重現 HIT 後撈回。卷證席報告有 3 處 `/Users/enzo`,是工具鏈 repo 自己的路徑與搜尋樣式,沒有考場程式識別字。

卷證席第 1 條之後,編排者另查出第二輪的整份快照與修補差異也嵌著同樣內容(修後版本樹裡的舊版整份 patch),一併排除重產;見 r1-記帳更正-2.md 與 r2-repair-binding.json 的 excluded_from_patches。

| id | 席與原條 | 原報 | 編排者重現 | 歸因 | 去向 |
|---|---|---|---|---|---|
| S1 | 通才 #1 | major | HIT:首個堆疊行是建構子、連字號、lambda、含空白方法名時,Caused by 內的 Assert 堆疊被認(修前 False、修後 True) | 有證據的修復回歸(席位三版對照) | 折:堆疊行改成 `at ` 到左括號前都算;四種形狀反例,改回窄規則會紅(已實測);兩種刻意大輸入 0.03 秒內 |
| S2 | 通才 #2 | minor | HIT:陣列型別放寬時測試照綠 | 原有漏查 | 折:補 `com.example.ArrayComparisonFailure`、`…ArrayComparisonFailureX` 反例 |
| S3 | 通才 #3 | minor | HIT | 有證據的修復回歸 | 折:計劃與測試說明改指「收證工具的家那條 PITFALL 防回歸列的十支」 |
| S4 | 通才 #4 | minor | HIT | 有證據的修復回歸 | 折:四處改成「從第一個堆疊行起(含這一行)」 |
| S5 | 通才 #5 | minor | HIT | 原有漏查 | 折:驗證紀錄與計劃補 REVISIT |
| K1 | 卷證 #1 | major | HIT:舊版整份 patch 命中 5 行 | 原有漏查(席位判) | 折:排除撤回目錄重產第一輪整份 patch(零識別字),帳上指紋更正(未推送);第二輪兩份 patch 同樣重產 |
| K2 | 卷證 #2 | minor | HIT | 有證據的修復回歸 | 折:說明檔改寫子套件那句 |
| K3 | 卷證 #3 | minor | HIT | 原有漏查 | 折:說明檔改成「公開檔不放本機路徑」 |
| K4 | 卷證 #4 | minor | HIT:fix-check 與 converged 帳行記的是推送前重建的中間提交 | 未判定 | 折:這裡註明——推送的只有最後那個提交,帳上記的中間提交只在本機物件庫,gc 後取不回;要重放以帳上的檔案指紋為準 |
| K5 | 卷證 #5 | minor | HIT:規格閘帳行記了改名前的測試名 | 未判定 | 折:這裡註明——`t_test_quality_cli_drill_cases_present` 先改名成 `t_drill_quality_cli_cases_present`(避開子字串誤選),第二輪後再改成 `t_test_quality_drill_cli_cases_present`;帳只能追加,舊名留在那幾行 |
| K6 | 卷證 #6 | minor | HIT | 原有漏查 | 放行:席報告入帳後不能改;同類工具鏈本機路徑在 repo 舊檔已大量存在,不是考場識別字 |
| R1 | 架構 #1 | minor | HIT | 有證據的修復回歸 | 折:改成 `t_secev_tq_*` 與 `t_test_quality_drill_cli_cases_present` |
| R2 | 架構 #2 | minor | HIT | 有證據的修復回歸 | 折:程式註解補陣列比較 |
| R3 | 架構 #3 | minor | HIT | 有證據的修復回歸 | 折:REVISIT 搬到做法節末尾,承認風險的散文改成 REVISIT |
| R4 | 架構 #4 | major | 判讀成立(席位標 ⚠) | 原有(這輪補了 WHY) | 折:把決定提升寫進收證工具的家(WHY 帶適用條件),成為有明文的變體 |

修補三問(編排者彙整席位證據):①原問題——近似型別名不認、二次方消除、Hamcrest 與訊息內 Caused by 已認(通才席兩版計時與案例);②正常路徑——本機型別、一般斷言、安全證據閘兩條路成立,真實 XML 86 份三版歸因零差異(通才席);帳只追加、指紋一致、數字對得上(卷證席);③新發現的修前修後見上表歸因欄。
