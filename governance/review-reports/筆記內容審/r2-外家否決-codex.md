severity: blocker

## F1 刪除治理帳事件即可洗掉較重判定

severity: blocker  
blocking: 是 —— 核心防線可被單一帳本刪除繞過，`check` 會錯誤放行。

引句:「對不上的判定檔當作不存在並列出來」

1. Spec〈做法〉第 0、2、3 節與 [S10] 只對 `governance/note-verdicts/` 做 append-only 檢查；治理帳沒有同等的刪改守衛。
2. 重現：同一內容編號已有「推得出」判定 A 與「脈絡」判定 B，兩者原本都有匹配事件。新提交只刪除治理帳中 A 的事件，不動任何判定檔。判定檔 append-only 檢查通過；A 被視為不存在；B 使內容成為已涵蓋；`check` 回 rc0。
3. 這不是〈誠實界線〉排除的「偽造判定檔並補造匹配事件」，只刪一行既有事件，卻直接兌現了稿內明稱要防的「刪掉不喜歡的判定」。
4. 現有寫入器只是向普通、受版控的 JSONL 追加資料，沒有不可刪保證。file: `scripts/lumos:928`。治理帳還被列為代碼審簿記豁免，單改這本帳不會使既有留痕失效。file: `scripts/lumos:20336`、file: `scripts/lumos:20340`。

## F2 無鎖的並行申訴會突破一生一次上限

severity: major  
blocking: 是 —— 申訴上限與折疊規則在合法並行操作下失效。

引句:「同一個內容編號一生只准申訴一次」

1. Spec〈做法〉第 2 節、第 3 節第 5 點、[S8] 與〈實務隱患〉同時要求「先確認從未申訴」及「各寫亂數檔、不用鎖」。
2. 重現：兩個 `record --dispute` 同時處理同一內容編號、指向同一原判定。兩者都在任一申訴落檔前讀到零筆，遂各自通過檢查並原子寫入不同亂數檔。
3. 結果是同一內容有兩筆申訴；第 70 行的「被某個申訴檔指名就換成申訴結果」沒有定義兩筆申訴衝突時取哪一筆。
4. `_write_lf` 明載原子換名不解決 read-modify-write 競態，呼叫端必須上鎖。file: `scripts/lumos:14149`、file: `scripts/lumos:14150`。現有「檢查不存在再新增」實作也確實用 `_vault_write_lock` 包住。file: `scripts/lumos:21446`、file: `scripts/lumos:21452`、file: `scripts/lumos:21456`。
5. [S9] 只測兩個普通判定檔能同時落地，[S8] 只測循序第二次申訴，沒有覆蓋這個交叉競態。

## F3 Codex 判定者的模型來源沒有定義

severity: major  
blocking: 是 —— Codex 編排路徑無法產生可重現且可校準的 `model` 值。

引句:「codex 派 Codex 那邊審查席的既有模型」

1. Spec〈做法〉第 3 節第 1、2、5 點要求 prepare 寫入工具模型常數、報告逐字照抄、record 精確比對；[S14] 又把模型變更綁到重新校準。
2. Claude 路徑明定 `opus`，Codex 路徑只寫「既有模型」，沒有常數名稱、值或取得介面。實作者無法判斷要寫產品預設模型、當前會談模型，還是某個 review role 模型。
3. 現有 `_TIER_ROSTER` 只宣告席名與相對家族，不宣告具體模型。file: `scripts/lumos:10316`、file: `scripts/lumos:10325`。`loop next` 的機讀輸出也只輸出席位與家族。file: `scripts/lumos:10897`、file: `scripts/lumos:10906`；CLI 只有 `--orchestrator`，沒有模型旗標。file: `scripts/lumos:31960`、file: `scripts/lumos:31964`。
4. 兩個照稿實作者可選出不同字串，造成報告互相拒收；既有模型被產品側替換時，也無從判定是否觸發 [S14]。

## F4 decision-amend 的可寫欄位與旗標缺失

severity: major  
blocking: 是 —— 作者處理流程依賴一支無法按 spec 實作或驗收的命令。

引句:「`decision-amend <節點> <決策編號> …`」

1. Spec〈做法〉第 3 節第 4 點只以省略號表示修改內容，沒有定義新值從哪個位置參數或旗標傳入，也沒有列出哪些欄位可改。
2. 現有決策至少有 `content`、`context`、`why_chosen`、`decided`、`valid` 與 `id`。file: `scripts/lumos:14928`、file: `scripts/lumos:14931`、file: `scripts/lumos:14933`、file: `scripts/lumos:14934`。
3. 重現：未推送決策的 `why_chosen` 含一個被判為「推得出」的子句。稿內要求用 `decision-amend` 修，但沒有任何語法能指定 `why_chosen`。只實作 `content` 修改會卡住；整項覆寫則會破壞日期、編號或有效狀態。
4. 現有相鄰命令把介面逐項定死：`decision-supersede` 有 `--by/--ended`，`decision-add` 有 `--decided/--context/--why`。file: `scripts/lumos:32199`、file: `scripts/lumos:32218`、file: `scripts/lumos:32221`。新稿的 [S12] 只驗遠端分類，沒有驗修改後欄位與保留不變量。

## F5 單一上次 fetch 無法證明所有遠端都夠新

severity: major  
blocking: 是 —— 多遠端 repo 可把已推送決策誤判成尚未推送並原地修改。

引句:「先要求遠端追蹤參照夠新」

1. Spec〈做法〉第 3 節第 4 點要求掃描「每一個遠端追蹤參照」，卻只定義單一「上次 fetch 超過 10 分鐘」條件，沒有逐遠端時間或強制 `fetch --all`。
2. 重現：repo 有 `origin` 與 `upstream`；`upstream` 實際已新增決策 d7，但本地追蹤參照尚未刷新。使用者剛 fetch `origin`，全域「上次 fetch」仍在十分鐘內。命令掃描本地快取時看不到 upstream 的 d7，遂准許原地修改已推送決策。
3. 現有可引用的 fetch 範本明確只刷新 `origin`。file: `scripts/lumos:23885`。現有遠端掃描則會枚舉所有 `refs/remotes/*`。file: `scripts/lumos:23908`。稿內沒有新增一個把這兩種範圍對齊的來源或契約。
4. 〈誠實界線〉只承認 fetch 完成後到修改前的競態，沒有承認「另一個遠端根本沒 fetch」這條路。

## F6 code-loop pass 沒有可對應的範圍輸入

severity: minor  
blocking: 否 —— 遺漏的只是非阻擋提醒，後續 pre-push `check` 仍會擋住待審內容。

引句:「`code-loop pass` 發現這個範圍還有待審筆記行時印一行提醒」

1. Spec〈做法〉第 3 節第 8 點與 [S17] 使用「這個範圍」，但沒有定義它從哪裡取得或替 `pass` 增加旗標。
2. 現有 `code-loop pass` 只綁 checkout 分支與 HEAD。file: `scripts/lumos:30967`、file: `scripts/lumos:30992`。其 parser 只有 `--note` 與 `--repo`；`--diff`、`--at-sha`、`--branch` 只存在於其他子命令。file: `scripts/lumos:32490`、file: `scripts/lumos:32495`、file: `scripts/lumos:32497`。
3. 重現：checkout 分支有自己的 upstream，但實際要推 `HEAD:release`。`pass` 當下不知道 release 的遠端舊 SHA，無法重建 pre-push 使用的 `_hrange`；提醒會掃錯範圍或不印。真正推送時 hook 才從 remote/local SHA 算出範圍。file: `scripts/hooks/pre-push:221`、file: `scripts/hooks/pre-push:233`。

### 逐節覆核

1. 文件頭、白話、依據、重寫稿、PRIOR-ART、RETIRE-IF、REVISIT：已讀,無 finding。
2. 〈判定者能不能用〉：已讀,無 finding。
3. 〈做法〉第 0 節：見 F1。
4. 〈做法〉第 1 節：已讀,無 finding；`_ns_range_added`、`_ns_regions`、`_note_shape_eval`、上線截斷函式及掛鉤現況均已核對。
5. 〈做法〉第 2 節：見 F1、F2。
6. 〈做法〉第 3 節：見 F3–F6。
7. 〈做法〉第 4 節：除 F3 的模型定義外，已讀,無 finding。
8. 〈做法〉第 5 節：已讀,無 finding。
9. 〈條款〉：S8–S10、S12、S17 的缺口分別見 F1、F2、F4–F6；其餘已讀,無 finding。
10. 〈回退〉：已讀,無 finding。
11. 〈實務隱患〉：並行宣稱的缺口見 F2；其餘已讀,無 finding。
12. 〈誠實界線〉：未涵蓋 F1 與 F5；其餘已讀,無 finding。
13. 〈前身 r3 發現怎麼處理〉與〈審計修正紀錄〉：已讀；修補銜接產生的 F1、F2 已列，其餘無 finding。
14. 凍結稿內章節引用、允許查閱的圖譜節點、`judge_prompt.md`、指定函式、旗標、掛鉤與 CI 路徑均已核對存在；前身審查卷證依本輪材料禁令未讀。

### 實務隱患鏡頭

1. 守衛面：F1；帳本一側缺少 append-only 對稱守衛。
2. 資源併發：F2；跨檔案的唯一性判定不能只靠原子換名。
3. 多遠端狀態：F5；單一 fetch 新鮮度不足以證明全部追蹤參照新鮮。
4. 對外送出：無——限定使用編排會談同一家供應商，沒有新增第二家資料接收者。
5. 可用性：無——限流與中斷有帶理由的 skip、warn/off 與治理帳路徑。
6. 容量：無——批次上限、搜尋檔數上限及定期檔數／容量複查均已寫明。
7. 不可逆：無——守衛位於推送前，回退順序與永久 no-op 相容入口已定義。
8. 金流：無——此功能不讀寫付款、扣款或計費狀態。

總結: 最嚴重 severity blocker；blocking 5 條。