severity: major

已讀,無 finding:補換行與批次寫入交錯——兩行程各 40 筆約 1KB、晚起 90ms 跑 30 輪 0 行壞掉,單行不到 8KB 不會被切開(`scripts/lumos:13201`);兩行程同時補換行最多多一個空行,第 3 步已略過;推送前檢查只讀已載入記錄,本來就有 deadline 與每題 try(`scripts/lumos:37261`)。

**RR1**
severity: major
blocking: 是 — git 逾時會讓 survived 紀錄被靜默丟掉,把 strong 發給實際上有過 survived 的配方。
`_codeloop_record_valid` 吞掉 TimeoutExpired 回 (False, "git 超過…"),與真的不是祖先共用 False;第 4 步只留有效紀錄,逾時的 survived 被丟掉,第 6 步只看到 killed 判 strong;逾時是暫態,同一份程式與 kill-log 會得到不同背書,違反合約候選第二條;第 4 步丟掉 why,講不出是逾時。改法:對得上名字的紀錄只要有一筆驗不了(逾時或 git 失敗),整題判 none,原因「版本驗證逾時」。
引句:「留下「platform 對得上、`test` 正規化後的方法名對得上、`head_sha` 經 `_codeloop_record_valid` 對這次表態的版本有效」的紀錄」
file: `scripts/lumos:37158`

**RR2**
severity: major
blocking: 是 — 沒有任何上限或上限退場,耗時上限沒有定義。
單個 sha 最壞兩次 git 各 8 秒;快取範圍是全呼叫還是每題沒說;kill-log 只增不減,不同 sha 數會一直長;寫表態這條路沒有總預算(`scripts/lumos:37664`)。要明講快取全呼叫共用,並設總預算或只驗最近 K 個 sha(超過判 none,原因「紀錄太多驗不完」)。
引句:「並對每一筆對得上名字的紀錄跑一次 `_codeloop_record_valid`(同一個 head_sha 只跑一次)」
file: `scripts/lumos:37165`

**RR3**
severity: minor
blocking: 否 — 〈實務隱患〉併發段說法不精確。
背書在寫表態那一刻就凍結,之後那批寫進來也不會讓舊 strong 失效,要重表態才重算;視窗是整段破壞測試執行時間(可能數分鐘);殘行的真正成因是 kill -9 或磁碟滿,要寫成具體成因。
引句:「寫表態當下看不到正在跑的那一批——可能讀到同版程式上較早的 killed 而判 strong;這跟天花板第 1 條同源」
file: `scripts/lumos:13199`

**RR4**
severity: minor
blocking: 否 — try 邊界有歧義。
文字較接近 try 不包寫帳;`_codeloop_dispositions_gov_log` 把 OSError 轉 (ok, why),呼叫端回 rc2(`scripts/lumos:37070`);S9 沒有反向案例鎖住寫帳失敗仍 rc2;第 2 題才例外時第 1 題已算的 strong 保留還是全部重置沒寫,應全部重置為 none。
引句:「整段包在 try 裡:任何例外都記 `backing={"status":"none","reason":"讀取失敗"}`,照常寫帳」

**RR5**
severity: minor
blocking: 否 — 既有行為,但新功能依賴組內每一筆都落帳。
後一個平台沒設 run_cmd 直接 return 2,前面平台結果沒落帳(`scripts/lumos:13084`);配方 revert 失敗 break,其後配方不出現在 results;某條 survived 可能從沒進 kill-log。天花板要加一條「整批提前結束時已算出的結果不落帳」,或讓 guard kill 提前結束前先落帳。
引句:「組內**每一筆**都要是 `killed` 且 `weak` 不是 true;任一筆不是 → none,原因「有一次不是強證據」」

最嚴重 severity: major,blocking 共 2 條(RR1、RR2)。
