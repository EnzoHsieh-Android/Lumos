severity: major

## 入口清單與回退後痕跡去向

我讀了 `scripts/lumos` 現行讀者:`_choice_ledger_index`(:78787)、`_choice_disposition`(:78800)、`_choice_kill_pick`(:79072)、`_choice_push_judge`(:79562)、`_gov_event_types_ok`(:18478)、`_gov_choice_count_verdict`(:17959)。以下 14 個入口每個答一句「回退後怎麼辦」,同族一次掃完。

| 入口 | 回退後誰讀、讀成什麼 |
|---|---|
| reach 事件 | 舊程式不讀,留著無害。但 `none` 的結論已變成「存活帳」(見 1、2)。 |
| 壞法事件的 `via: "cov"` | 舊程式當一般 survived 讀,會被「帶過去」不重跑(見 1)。 |
| 壞法事件的 `candidate` | 舊程式忽略;`evs[-1]` 照取最後一筆,無害。 |
| invalid 事件 | 舊程式不讀。要靠回退 3 的「保留 skip 讀 invalid」才有用(見 3)。 |
| exhausted 事件 | 舊讀者看到最後一筆是 no_result,擋推送(見 3)。 |
| layer 事件與 `governance/choice-layers/` 判讀檔 | 舊程式不讀。檔留在 git 裡,卻不在簿記白名單,會連帶使代碼審留痕失效(見 4)。 |
| `.lumos/choice-layer/` 清單檔 | 未追蹤,留著沒人讀,無害。 |
| `reach-run` 事件 | 舊程式不讀,無害。 |
| run 事件多出的 `cov*` 欄位 | gov 欄位白名單不認得就略過,無害。 |
| `_choice_disposition` 新增 `"exhausted"` 回傳值 | 一旦撤掉,所有呼叫端(:78595、:79072、:79562)都得跟著改回,回退 3 沒列。 |
| `_choice_pick` 的 `skip` | 回退 3 與回退 4 對它的處置互相矛盾(見 3)。 |
| `lint-waive` 放行 | 不受影響。 |
| 推送閘子原因 | 回退 2 說「處置句改回原本那一句」,可行。 |
| gov `--stats` 新增四行 | 撤掉即可,無害。 |

## Findings

1. 回退 1 說「一切照現在」,但依覆蓋判成存活的行回不去。
   - `_choice_kill_pick` 的 :79092 規定:最新一筆是 survived,且 `tests_sha` 沒變、`only` 為 None,就「帶過去」不重跑。
   - 範圍 3 的 `via: "cov"` 存活事件根本沒跑過壞法。`--no-cov` 或拿掉 `coverage` 之後,這些行仍被當作「已判存活」永久帶過去。
   - 正式壞法永遠不會跑。除非測試檔改了(`tests_sha` 變),或手動帶 `--only`。
   - 而 `tests_sha` 只含守的測試檔的 blob,不含正式碼。有人改了正式碼、讓測試改走到那一行,也不會重跑。
   - spec 沒寫 `via: "cov"` 的事件有沒有帶 `tests_sha`。這個決定兩頭都有後果:
     - 帶了:上述永久帶過去成立。
     - 沒帶:每次 choice-kill 都走完整重跑,覆蓋加速形同失效。
   - 這也使「帳上已有的 reach 事件照印分類,不影響擋不擋」這句失真,因為存活本身就擋推送。
   - spec 沒寫回退時要怎麼處理這批 cov 存活事件,例如補一個「撤回 cov 存活」的事件,或在 `no_cov` 時讓 `via: "cov"` 不被帶過去。

severity: major
blocking: 是
引句:「帳上已有的 reach 事件照印分類,不影響擋不擋」

2. 覆蓋判錯(測試其實經過卻判沒經過)時,事後沒有發現的辦法,也沒有更正的辦法。
   - 發現:
     - 抽樣對照只涵蓋第 2、3 層的層判讀,不涵蓋 reach `none` 與 `via: "cov"` 存活。
     - 「覆蓋可信」只擋全模組 0 行、沒產出等整份問題。像 exec 資料檔對錯測試、行內函式歸屬錯這類個別測試、個別行的誤判都過得了關。
     - 唯一可能暴露的時機,是人處置時跑 `situation-rule --point` 才第一次真的跑壞法。
   - 更正:
     - 補償事件只有 `layer: 0` 的 `--withdraw`。reach 與 cov 存活沒有撤回指令。
     - `--reach-only` 只補「沒有有效 reach」的行,而且只有 `unknown` 被排除在有效之外。一筆錯的 `none` 永遠算有效、永遠不重評。
     - 範圍 4 記了 `cov_sha`,但全文沒有任何讀者用它判斷 reach 還有沒有效。第 9 節的有效表只管 layer。
   - 結果:錯的 `none` 沒有重新評估的路徑,只能由人手動 `lint-waive` 或用 `--only` 強跑。
   - 「已排除:不可逆:…分類錯了下次重算的新事件蓋過」不成立。下次根本不會重算:帳上同一行已有 `none`,而 `unknown` 以外的 reach 都算有效。

severity: major
blocking: 是
引句:「判讀準不準靠定期抽 20 條人工對照,判錯用補償事件撤回」

3. 回退 3 與回退 4 互相矛盾,而且漏了 exhausted 行的善後。
   - 回退 3 要求「保留 `_choice_pick` 讀帳上 invalid 帶 skip」,否則已處置的行會被打回。這代表 `_choice_ledger_aux` 的讀取必須留下。
   - 回退 4 卻說「整段撤掉:照 1、2、3」。照做之後 skip 仍留著,整段並沒撤乾淨。
   - 回退 2 說「`_choice_ledger_index` 照舊不收它們」,但 skip 又要讀 invalid,三處敘述互相對不上。
   - exhausted 的善後:
     - 回退 3 只說「不認 exhausted」。舊讀者看到最後一筆是 `no_result`,擋推送。
     - 若同時撤掉 skip,舊 pick 又挑回候選 1,編不過、再記 `no_result`,永遠擋住。
     - spec 沒說這批行怎麼收,可能只剩 `lint-waive`。
   - 範圍 5 說「其他讀者不動」,但 `exhausted` 要進 `_choice_disposition`,三個呼叫端都要補傳 aux 資料,與這句矛盾。
   - 對應的條款是 S17,它並沒有涵蓋回退後的行為。

severity: major
blocking: 是
引句:「4. 整段撤掉:照 1、2、3」

4. 新增的兩個目錄不在簿記白名單,提交判讀檔會讓代碼審留痕失效。
   - `_BOOKKEEPING_DIRS`(`scripts/lumos:41617`)只有 `governance/code-loop/`、`governance/review-reports/` 等幾個。
   - `governance/choice-layers/` 不在其中。`_dirty_non_bookkeeping`(:23294)與留痕有效判斷(:23520、:23653)都靠這張表。
   - 流程是「choice-kill → 判讀 → 提交治理帳」。判讀檔與帳「同一起提交」,若發生在 `code-loop pass` 之後,留痕就失效。
   - 這是 `Systems/pitfalls-code-loop` 與 `[[Projects/代碼審通過前自動跑選擇點_計劃]]` 已經出過的同一個死結。
   - 範圍 12 的文件清單沒列「補進簿記白名單」,回退段也沒列「git rm 這個資料夾」。
   - `.lumos/choice-layer/` 沒被 `.gitignore` 涵蓋。回退後它會在工作目錄裡留下未追蹤的檔,spec 沒交代清理。

severity: major
blocking: 是
引句:「每筆判讀全文存成 `governance/choice-layers/<內容雜湊>.json`(同治理帳一起提交)」

5. `via: "cov"` 事件落進 gov 統計的方式沒寫清楚,回退前後的數字口徑會不同。
   - `_gov_choice_count_verdict`(:17962)只在 `attempt == 1` 且 `via == "run"` 時才算「第一次跑殺掉率」。
   - cov 存活事件的 `via` 是 `"cov"`,所以被排除在殺掉率分母外,同時卻進入「被回報的存活」(`c["ever"]`)。
   - 母計劃的 RETIRE-IF 拿這兩個數當分母;spec 沒說 cov 事件的 `attempt` 與其他欄位,也沒說統計要不要另列。
   - 回退後的舊 gov 仍會把這批沒跑過的存活算進分母。

severity: minor
blocking: 否
引句:「(沒跑,因為沒有守的測試經過)」

6. 新欄位與新 kind 登記只寫「補上」,沒給型別;`_GOV_FIELD_TYPES` 是七本帳共用的一張表。
   - 欄位型別不對的整行,每個讀者(新舊都一樣)都會靜默跳過。
   - 型別未定的有 `judgment`(「路徑與雜湊」是 str 還是 dict)、`deps`、`tried`、`reach_clauses`、`cov_secs`、invalid 的 `row`、`blob`。
   - invalid 事件若因型別被丟掉,skip 集合就少一筆,會永遠回到編不過的候選。
   - 範圍 4 的「白名單」沒指明 `LOOP_NOT_CLOSE_EVENTS`(:21051)。`t_loop_close_kinds_classified` 會逼出這五個新 kind 的分類,spec 也沒列。

severity: minor
blocking: 否
引句:「治理帳的 (gate, kind) 白名單、gov 讀取欄位白名單與型別表補上新的 kind 與欄位(`candidate` 也要)」

## 實務隱患(風險類逐類)

- 不可逆:不成立「已排除」。治理帳只追加,而錯的 `none` 與 cov 存活事件沒有更正通道,見 1、2。
- 守衛面:spec 標「不排除」,但只列了 S9、S16、S19,沒有任何回退後行為的守衛測試,見 3、4。
- 併發與交易:無。單人、依序操作;唯一的併發例外是別的會談用舊版工具讀到新事件,這點 spec 已查過舊 index 與 gov 會略過(我核對成立)。
- 金流:無。沒有金額計算。
- 對外送出:無。覆蓋在本機跑,不對外送資料。

總結:最高等級是 major,blocking 共 4 條
