severity: major

## F1 「可以停」的安全警語只在散文裡,沒有任何條款/測試綁住它,照字面實作可以印出誤導的「可以停」
severity: major
blocking: 是 — 照 [S5] 字面實作(嚴重度≤minor 且折入數在降 → hint=can-stop)完全可以通過測試,卻在處置閘剛印完 FAIL 之後印「可以停」而不帶「還沒過就看閘沒過的原因」這句警語,讀的人會把「可以停」當成「這輪過了、可以收工」,而閘其實是因為 G3 hash、quote-check、條款綁定、資安席或落點這幾項非嚴重度項目失敗——這些失敗跟「嚴重度≤minor」完全無關,規則卻只看嚴重度走勢。

引句:「最後一輪最高嚴重度 ≤ minor → **可以停**(已過閘就收;還沒過就看閘沒過的原因,代碼審照舊只准放行 minor)。」

這句括號裡的警語是唯一防止「可以停」被誤讀成「閘過了」的機制,但條款 [S5] 的綁定測試只驗:

引句:「若折入數在降且最後一輪最高嚴重度不高於 minor,則提示應是可以停 [test:t_cap_hint_declining_minor_can_stop]」

`--json` 的 `hint` 欄位(見三、輸出格式)也只是一個代碼字 `can-stop`,不含這句警語;文字輸出版的警語要不要照抄,完全沒有條款約束。對照 `_loop_status_disposal` 的實際失敗來源(scripts/lumos:18265 起),FAIL 可以純粹來自跟嚴重度無關的項目:

file: `scripts/lumos:18332` — `_loop_status_disposal` 的處置集合步驟只驗 findings_set/folded_set/accepted_set 是否配平,跟嚴重度走勢無關,失敗一樣會讓 `fails.append("處置集合")`。
file: `scripts/lumos:18583` — 落點/資安席/條款綁定三項獨立失敗都會進 `fails`,跟「最後一輪最高嚴重度」無關。

也就是「折入在降、嚴重度都 minor,但因為漏帶落點/quote-check 沒過」是可以真實發生的組合(尤其是這輪本身在改「不寫帳」相關程式,若忘記把 lands_in 落到 Systems/loop-convergence-recording,就是活生生的落點失敗案例)。這種狀況下,按字面實作,`loop next`/處置閘會同時印「⛔ DISPOSAL GATE FAIL」跟提示「可以停」而不解釋為什麼還沒過——編排者如果只看提示那一行(這份計劃自己在「一句話」裡定位這段是「給人的提示」,就是設計給人快速掃過用的),會誤判成「東西已經沒事、可以收工」,實際上是漏了留痕或條款這種機械性缺口,不修就永遠過不了關。

回滾層面沒有這條的收拾成本(拔兩處呼叫照樣乾淨),但這正是本輪该盯的「提示被照做後錯了會怎樣」——修法：把「已過閘就收;還沒過就看閘沒過的原因」這句話,和其後綴的「代碼審照舊只准放行 minor」,綁進 [S5] 的條款文字本身(不是只放在做法段落的括號裡),或者拆成獨立條款配獨立測試,確保實作者不能只滿足 hint-code=can-stop 就交差。

已看,無:
- 回退段落的機械可行性:`emit()`(scripts/lumos:10556 起)是 loop next 唯一的文字/JSON 輸出收斂點(escalate/gate-pending/converged/cap-reached/plant-canary 全部經過它),`_loop_status_disposal`(scripts/lumos:18265)的 PASS/FAIL 兩個 return 前都在同一個函式作用域內,兩處都可以只插一個呼叫點——「拔掉兩處呼叫即回到現狀」這個回退宣稱在目前程式結構下站得住,不是空話。
- `loop next --spec` 對 2026-08-26 後的 panel 帳會被已退役舊閘擋下(rc=2)這件事(scripts/lumos:10664 委派 `cmd_loop_status(...panel=(panel_fmt and not light)...)`,沒帶 `disposal=True`,會落進 `_loop_status_panel` 的退役檢查,scripts/lumos:8284)——這份計劃把它列進「不在本案」延後處理是對的:因為它印的補完指令(scripts/lumos:10645 `_mode = "--disposal"`)本來就是叫人直接問 `loop status --disposal`,不是叫人對 `loop next` 補 `--spec`,所以這個已知缺口不會透過這份新功能的提示被觸發或放大,延後處理不會讓這份的提示本身失真。
- 「到上限」的判斷(`rounds_count >= cap`)是獨立算的,不依賴走到 `phase=="cap-reached"` 分支——`gate-pending`(未帶 --spec,scripts/lumos:10634 起)一樣會先印 `emit()`,所以只要輪數到了上限,不管最後停在 gate-pending 還是 cap-reached,提示都印得出來,不會因為「委派舊閘」那個已知缺口而讓上限提示整個啞掉。
- 併發/效能/金流/對外送出/不可逆/守衛面(除上述 F1 外)六類實務隱患:計劃自己的判斷(只讀帳、每輪呼叫一次 `_review_yield_round`、不碰付款、不對外、不寫帳、不改退出碼)跟現有 `_loop_status_disposal`/`cmd_loop_next` 的讀寫邊界一致,沒發現額外風險。
- 處置閘唯讀路徑(回放/凍結)不印這段:`_loop_status_disposal` 目前的 `readonly` 參數只包住 roster/severity 尾巴跟最後的 `_loop_gov_mark`(scripts/lumos:18534/18541/18583),不是整段函式都被 readonly 包住,所以計劃裡「新段落自己包一層唯讀判斷,不假設外面已經包好」(對應 [S3])是必要的正確認知,不是多餘的謹慎。

最嚴重 severity: major,blocking 共 1 條。
