severity: major

先講結論:這份投稿的主線(覆蓋掛在單支基準上、四層判讀、無效壞法記憶)可行。但照字面實作,會撞到簿記白名單、基準快取的鍵、gov 的第一次判定口徑、推送閘讀帳的形狀這幾處,另有一處與自己的說法互相矛盾。以下對程式現況都查過。

## 白話、用詞、不做:逐節讀

1. 判讀有效條件(範圍 9 的表)與「處置一條不會讓別條作廢」互相矛盾。
   - 第 1、4 層綁「碰到的每份計劃的條款全文加正文雜湊」。第 1 層的處置本來就是 `situation-rule` 往計劃 P 加一條條款,P 的條款全文一變,同一份 P 底下所有第 1、4 層判讀全部作廢。
   - 第 3 層「補了測試就重判」,同一條條款底下的存活也互相作廢。
   - 這正是 r1 要消掉的 n² 重判,只是換了形狀;白話、WHY 4、實務隱患「判讀成本」三處都寫了反話。
   - 該改成:表的第 1、4 層改綁「那個壞法行本身加引到的條款或段落」,或者把這句承諾收窄成「只對第 2、3 層成立」。

severity: major
blocking: 是
引句:「依據沒變就一直有效,處置一條不會讓別條作廢」

## 範圍 1 到 3:覆蓋基準與依覆蓋選測試

2. `none` 的行不跑壞法就記存活,而壞法從沒被編譯過,等於把「編不過」又放回存活裡。
   - 白話自己的例子顯示 17 條等價裡有 4 條其實編不過,約兩成。
   - 這條路徑一旦跳過執行,這類壞法永遠記成存活而不是無效。
   - 照〈不做〉第一條,第 4 層只是建議,人要用 `lint-waive` 放行,所以每個這樣的行都要人工放行才能推。
   - 第三道的無效壞法記憶因此救不到最需要它的那批行。
   - 缺的是:`none` 的行至少要先編譯檢查一次(例如併進覆蓋基準那一輪),或在材料與第 4 層標明「未編譯」。

severity: major
blocking: 是
引句:「覆蓋分類是 `none` 的行不跑、直接記存活」

3. `baselines` 交接缺三個定義,另有一個回歸風險。
   - **鍵怎麼定。** `cmd_guard_kill` 的基準快取以展開後的完整指令字串為鍵(`scripts/lumos:28498`、`scripts/lumos:29168`)。覆蓋基準的指令多了 init script,壞法指令沒有,spec 沒說存進哪個鍵。鍵對不上就會再量一次,S5 的「不再量」會紅。
   - **多平台。** 快取是每個平台一份(`scripts/lumos:28474`),spec 給的是單一扁平 dict。兩個 kotlin-junit 平台若指令字串相同會撞鍵。
   - **「不確定」欄位。** 第五欄來自 `mstate["unsure"]`,也就是修改時間沒錯開的弱證據(`scripts/lumos:28502`、`scripts/lumos:29185`)。spec 沒說覆蓋基準怎麼算它,寫成固定 False 會讓弱證據判定靜默失效。
   - **掛覆蓋後基準變紅。** 掛 JaCoCo 後單支基準可能變紅(例如 Robolectric 加 instrumentation 失敗),但不掛時是綠的。交進去後 `cmd_guard_kill` 會判「基準非綠 abort」(`scripts/lumos:28506`),所有壞法變 `no_result`。這違反「覆蓋關掉或失敗時一切照現在」。斷路器只管覆蓋不可信,不管基準本身變紅。
   - ⚠ 另外,壞法改在 `cmd_guard_kill` 自己的工作樹跑,而基準預熱的是 choice-kill 的隔離樹。壞法樹第一次編譯是冷的,「多約 4 分鐘」的估算沒算進去,交編排者實測。

severity: major
blocking: 是
引句:「這些基準交給 `cmd_guard_kill` 的新選用參數 `baselines`」

## 範圍 4 到 6:記帳、讀者、換候選

4. gov「第一次判定」的口徑與現況不符。
   - spec 說「照舊數 `attempt == 1`」。實際條件是 `attempt == 1` 而且 `via == "run"`(`scripts/lumos:17962`)。
   - `via: "cov"` 的存活因此不進第一次判定,殺掉率被灌高,RETIRE-IF 的分母也被吃掉。
   - `attempt` 由 `self.attempts[key]` 逐筆累加(`scripts/lumos:79231`)。候選 1 編不過的那筆 `no_result` 是 attempt 1,候選 2 變成 attempt 2。結果是第一次判定記成 `no_result`,真正的判定被漏掉。
   - 同一筆 `no_result` 也會進原因統計,而 spec 只說 `invalid` 與 `exhausted` 不進分母。
   - spec 沒定義 `via: "cov"` 與候選 2 的 `attempt` 怎麼算,S10 也沒有案例。

severity: major
blocking: 是
引句:「換候選的壞法事件帶 `candidate`,統計另列」

5. 推送閘讀帳的形狀與「其他讀者不動」不符。
   - `_choice_push_read` 只回 `_choice_ledger_index(evs)` 與放行集合(`scripts/lumos:79758`)。
   - exhausted、skip、layer 判讀都要從 B 版(被推版本)帳讀到,`_choice_disposition` 也得多收 blob 與 aux 事件。
   - 呼叫端至少有 `_choice_points_lines` 一帶(`scripts/lumos:78605`)、`_choice_kill_pick`、`_choice_push_judge`、`situation-rule --point`。
   - 「判讀有效」第 2 層要比對引句,引句只在 `governance/choice-layers/<雜湊>.json` 裡,不在帳上。推送閘要從 B 版樹讀這些檔,spec 沒寫缺檔、壞檔怎麼處理。

severity: major
blocking: 是
引句:「新增一支 `_choice_ledger_aux(evs)` 收 reach、layer、invalid、exhausted,其他讀者不動」

6. 判讀檔與清單檔的新位置不在簿記白名單。
   - `_BOOKKEEPING_DIRS` 沒有 `governance/choice-layers/`,也沒有 `.lumos/choice-layer/`(`scripts/lumos:41617`)。
   - choice-kill 的 `_choice_kill_base` 在工作目錄不乾淨時直接 rc2(`scripts/lumos:79117`)。
   - 提交判讀檔會讓代碼審留痕失效,「通過後只准再提交帳本」被打破,`pass` 預判也受影響。
   - 範圍 12 的文件清單沒列這個改動點,範圍 9 也沒提。

severity: major
blocking: 是
引句:「每筆判讀全文存成 `governance/choice-layers/<內容雜湊>.json`(同治理帳一起提交)」

7. 無效壞法只綁「那支檔的 blob」,依賴別支檔的編譯結果會被永久凍住。
   - 型別推論、別支檔的宣告變了,同一支檔 blob 不變,壞法其實已經能編譯,卻照樣被跳過。
   - `exhausted` 又被當有效處置、不擋推送,真缺口因此靜默消失,而且不會重試。
   - 範圍 6 要求錯誤指到被改的檔,擋不掉這種:錯誤可以指到被改的檔,但成因在別支檔。
   - 至少要把整體樹(`at_sha` 或相關檔集合)的指紋也納入鍵,或給 `exhausted` 一個到期重試的條件。

severity: major
blocking: 是
引句:「在那支檔的內容(git blob)下編不過;記在帳上,之後同一支檔同一個 blob 挑壞法時跳過它」

8. `via: "cov"` 的存活事件欄位沒定義。
   - 現有讀者靠 `judged`(缺值讀成 single)、`tests_sha`(用來判「守的測試沒變就不重跑」,`scripts/lumos:79072`)、`plans`、`clauses`。
   - 沒填這些,gov 的 single 計數被灌水,`tests_sha` 缺會讓這些行每次都重跑。

severity: minor
blocking: 否
引句:「沒跑,因為沒有守的測試經過」

9. `cov_sha` 沒有任何讀者。
   - `--reach-only`「沒有有效 reach」的「有效」沒定義。〈用詞〉只說 `unknown` 無效,測試或檔變了的 reach 算不算有效沒寫。
   - 結果是補了測試後,`choice-points` 仍印舊分類。

severity: minor
blocking: 否
引句:「對帳上目前是存活、而且沒有有效 reach 的行補 reach 事件」

10. 範圍 9 的 `deps`「見下表」,但那張表是有效條件,不是欄位形狀。
    - 單筆 4096 位元組上限下,第 1、4 層碰到多份計劃時,逐份雜湊塞不塞得下沒有估。

severity: minor
blocking: 否
引句:「`deps`(見下表)、`token`),單筆不超過 4096 位元組」

## 其他節:REVISIT、預期值表、驗收條款、回退、天花板

11. REVISIT 2027-02-15 的事件名與實際不符。
    - 寫的是「reach、layer、invalid、cov 事件」,但 `cov` 是 run 事件上的欄位,不是 kind。
    - 漏了 `exhausted` 與 `reach-run`。

severity: minor
blocking: 否
引句:「讀治理帳 gate choice-kill 的 reach、layer、invalid、cov 事件」

預期值表、驗收條款、回退:已讀,與正文互相對得上,無額外 finding。唯一需要補的是回退 3 前半句與後半句的互相引用,請在正文改寫時一併整理。

## 實務隱患

- 守衛面(推送閘提示、`_choice_disposition`、`skip`)連動範圍 5 與 6,finding 5 到 7 與此有關。
- 併發與交易:無。單人單機依序操作,威脅模型成立。
- 金流:無。只讀測試覆蓋。
- 對外送出:無。覆蓋在本機跑。
- 不可逆:治理帳只追加,補償事件可撤回。這一點成立,但 `exhausted` 沒有到期條件(見 finding 7),等於把「撤回」的責任丟給人。

總結:最高等級是 major,blocking 共 8 條
