severity: minor

## F1 段落輸出沒定調用哪一種既有 bracket 標籤慣例
severity: minor
blocking: 否
引句:「文字:一個固定標題的段落,每輪一行(輪次、折入數、最高嚴重度),然後閘一行、提示一行、熔斷一行(有才印)。」
既有做法:`loop next` 每一段輸出都用 `[next] `/`[disposal] `/`[panel] ` 這種 bracket 標籤開頭(例:`print(f"[next] {loop_id}:現在狀態…")`、`print(f"[disposal] 落點: ✓ …")`),讓同一支檔案裡不同判定步驟的輸出可視覺分辨、也方便未來 grep。
file: `scripts/lumos:10426`(`[next]` 開頭)、`scripts/lumos:18582`(`[disposal] 落點:` 開頭)
問題:三稿都只講「固定標題的段落」,沒有承諾沿用 `[next]`/`[disposal]` 這套既有標籤慣例,也沒說新標題長什麼樣。不影響結構(只是文字內容細節),但留到實作時才決定,容易長出第三種措辭風格(例如不帶 bracket 前綴的自由句子)。落實時建議明講「跟進 `[disposal]`/`[next]` 同一種 bracket 標籤」。

## F2 每輪分組沒點名要不要沿用既有兩份重複的 round 分組邏輯
severity: minor
blocking: 否
引句:「對每一輪的帳列直接呼叫 `_review_yield_round`(取「折」欄)」
既有做法:目前把帳列按輪次分組(含 round-id 非連續重現的擋檢查)在 `_loop_status_panel`(`scripts/lumos:8291` 的 `groups = OrderedDict()`)與 `_loop_status_disposal`(`scripts/lumos:18293` 的 `groups = OrderedDict()`)各自重寫一份,兩份邏輯幾乎一樣但沒抽共用函式。
file: `scripts/lumos:8291`、`scripts/lumos:18293`
問題:設計只講「對每一輪的帳列直接呼叫 `_review_yield_round`」,沒有交代這「每一輪」怎麼分組出來。照現有先例(兩個既有呼叫點都各自重寫分組),`loop next`(目前完全沒有分組邏輯,只算 `rounds_count`)要生出「每輪」清單,最有可能的實作路徑是第三次重寫同一段 OrderedDict 分組。這不是設計文字本身引入的新做法(現狀本就有兩份重複),但設計沒有明講「這次要不要順手抽成共用函式,還是照舊再抄一份」,留給實作自由發揮。判不準要不要因此升級成「第二種做法」,標 ⚠:如果實作選擇抄第三份,是延續既有(不良)慣例而非新增一種;如果抽出共用函式,反而是改善,兩邊都不算違背既有架構,所以不升等 major。

## F3(⚠)cap_hint 的「折」定義與 disposal 既有「處置集合」重算不是同一件事,設計沒有點名兩者關係
severity: minor
blocking: 否
引句:「每輪折入數:對每一輪的帳列直接呼叫 `_review_yield_round`,取「折」欄。」
既有做法:`_loop_status_disposal` 的「② 處置集合」步驟(`scripts/lumos:18293` 起)是逐輪重算 `F=folded_set`/`A=accepted_set` 是否覆蓋 `findings_set` 的合取判定(過不過關的依據);`_review_yield_round` 的 `F` 欄只是單純數折入清單長度,兩者取數路徑不同但概念相鄰(都叫「折」)。
問題:設計條款([S7])只規定「沒有彙總帳」時的退化情形,沒有明講 cap_hint 印出的「折入數」跟處置閘正式判定用的「處置集合」在語意上刻意脫鉤(一個是唯讀觀測、一個是合取判準)。容易被實作誤讀成兩者該同步或互相校驗。屬命名/語意銜接的細節,判不準是否需要在文中補一句「與②處置集合互不影響」,標 ⚠,不算引入第二套判定邏輯(cap_hint 本身宣告「只印不改判定」,方向是對的)。

已看,無:機制沿用的三個宣稱都能在 `scripts/lumos` 對上號——`_review_yield_round`(`scripts/lumos:7364`)本來就被 disposal 尾端(`scripts/lumos:18548`)與 `cmd_gov` 共用,cap_hint 直接呼叫是同一函式的第三個呼叫點,不是另立一套;`_loop_anchor_tier`/`_TIER_PARAMS` 已經被 `loop next`(`scripts/lumos:10368`/`10398`)與處置閘的資安席步驟 `_gated_seats_for`(`scripts/lumos:18045`)兩處各自查表使用,新增第三處查表沒有破壞既有模式;`_panel_retired_for`(`scripts/lumos:8213`)判「2026-08-26 後新迴圈」與設計文件的判法一致。readonly 語意也對得上——`_loop_status_disposal` 已有 `readonly` 參數,既有慣例是「唯讀重驗/回放時觀測尾巴不印也不寫」(`scripts/lumos:18534`「if not readonly: _roster_tail(); _severity_tail()」,`scripts/lumos:18541` 同一模式包住「審查有沒有用」那段),cap_hint 的 [S3]「處置閘在回放或凍結中被唯讀呼叫時不印」是同一慣例的延伸,不是新規則。JSON 欄位命名刻意避開 `advisory` 是對的:`cmd_loop_next` 的 `out` dict 本來就有一個語意完全不同的 `advisory` 鍵(`scripts/lumos:10421`,講分級由編排者宣告),重名會撞義;改用 `cap_hint`/`hint` 沒有這個風險。落點 `Systems/loop-convergence-recording` 現存節點的 `about_code` 已列 `scripts/lumos`(該節點 frontmatter `about_code: [scripts/lumos]`),且內容正是收斂/loop next/disposal 閘這條線,cap_hint 這種「印給人看、不改判定」的觀測性擴充落進去符合節點既有定位,不需要新開節點。

不對齊共 3 條,其中 major 0 條。
