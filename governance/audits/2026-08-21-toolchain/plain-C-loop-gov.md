# C 面對照表:loop / gov 家族(cmd_loop_next、cmd_loop_status 各模式閘訊息、cmd_canary_record、
# cmd_quote_check/cmd_refcheck/cmd_seat_check、cmd_gov+_render_gov_stats、cmd_search/context/contracts
# 開頭★提示句、cmd_fold_check)

本輪只出對照表,不改檔。「測試依賴」欄列出 grep scripts/test_lumos.py 找到的斷言行號與斷言用的關鍵字;
若建議白話把該關鍵字拿掉,要嘛保留關鍵字當錨點,要嘛在最後一欄註明「測試要同步改為斷言 X」。

---

## 一、cmd_loop_next(每次「問下一步」都會印;含 scope_cap / cluster_hint / canary 植入指引整段)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:4833 | .canary-log.jsonl 讀不到(權限/IO 錯誤) | `ERROR: 讀 {path} 失敗: {e}` | 擋下:讀不到審查記錄檔 {path}({e})。<br>沒有這份記錄就沒辦法算下一步該做什麼。<br>`檢查檔案是否存在、有沒有讀取權限。` | 無 |
| scripts/lumos:4837 | 同一審查編號裡,記錄一部分帶輪次、一部分不帶 | `ERROR: canary-log round 欄混用(partial-mix)——帳損壞,同 status 拒讀` | 擋下:這個審查編號的記錄格式前後不一致——有些筆記了第幾輪、有些沒有。<br>格式對不上會讓後面判斷「是不是收斂了」全部亂掉。<br>`打開 .canary-log.jsonl,把這個編號的每一筆記錄格式改一致。` | 無 |
| scripts/lumos:4846 | 同一輪號被別的輪次插隊、隔開後又出現 | `ERROR: round-id {rid!r} 非連續重現(append-only 帳次序損壞)——同 status 拒讀` | 擋下:第 {rid} 輪的記錄被其他輪次插在中間、又重新冒出來一次,代表記錄的先後順序被打亂了。<br>這本記錄只能照時間往後加,順序亂了就沒辦法判斷收斂進度。<br>`檢查並修好 .canary-log.jsonl 裡這個審查編號的寫入順序。` | 有:t_m1_codeloop_r2_fixes 附近 scripts/test_lumos.py:13626 斷言 stderr 含「非連續」——白話需保留「非連續」一詞 |
| scripts/lumos:4854 | 這次指定的分級,和記錄第一筆定下的分級不同 | `ERROR: --tier {tier} 與帳面定錨 {anchor} 衝突(定錨優先;要換 tier 開新 loop id)` | 擋下:你現在指定的分級是「{tier}」,但這個審查編號第一次記錄時就定成「{anchor}」了,兩個對不上。<br>分級一旦第一筆記錄下來就定死,不能中途換。<br>`要換分級,請開一個新的審查編號重新開始。` | 無(scripts/test_lumos.py:15134 只驗 rc==2) |
| scripts/lumos:4859 | 全新審查編號、第一次問下一步卻沒指定分級 | `ERROR: 零記錄 loop 需明示 --tier(不猜——猜錯模式撞混用守衛)` | 擋下:這是全新的審查編號,還沒有任何記錄,系統不會幫你猜要走哪個分級。<br>猜錯分級之後格式會兜不起來、反而卡住。<br>`第一次呼叫時請明確指定分級(--tier)。` | 無(scripts/test_lumos.py:15121 只驗 rc==2) |
| scripts/lumos:4874 | 分級要求每筆都帶輪次編號,但這個編號的記錄都沒帶 | `ERROR: tier={eff_tier} 要求 panel 格式(記錄帶 --round),帳面為 legacy 格式——格式衝突(補 record 帶 --round,或 tier 錯誤則開新 loop id)` | 擋下:「{eff_tier}」這個分級規定每筆記錄都要帶輪次編號,但這個審查編號目前的記錄全都沒帶。<br>分級跟記錄格式對不上,系統沒辦法往下判斷。<br>`之後記錄請補上輪次編號;如果一開始分級就設錯了,請開新的審查編號。` | 無 |
| scripts/lumos:4878 | light 分級要求單人、不分輪次,但記錄卻帶了輪次 | `ERROR: tier=light 為單席 legacy 格式,帳面卻帶 --round(panel 格式)——格式衝突` | 擋下:「light」這個分級只能用單人、不分輪次的舊格式記錄,但這裡的記錄卻帶了輪次編號。<br>格式不對,系統沒辦法判斷收斂。<br>`確認分級選對了沒有;選錯了請開新的審查編號重來。` | 無 |
| scripts/lumos:4971 | 每次問下一步、非 --json 模式時的第一行(最高頻) | `[next] {loop_id}: phase={phase} tier={eff_tier} 下一輪 N={n_next} width={width} cap={cap}` | 提醒:審查編號「{loop_id}」現在的狀態是「{phase 白話}」,分級「{eff_tier}」,接下來是第 {n_next} 輪,這輪要 {width} 人審、最多可以跑 {cap} 輪。 | 無(測試走 --json 解析 phase 欄位,不比對這行文字;scripts/test_lumos.py:15113 起) |
| scripts/lumos:4975 | 有查得到該派誰時,逐席印一行 | `應派: {slot} family={family} 佔W={是/否} requirement={requirement} note={note}` | 提醒:這一輪應該派「{slot}」這個角色(屬於{family 白話}),{是否算進人數}, 派工要求是「{requirement 白話}」。 | 有:scripts/test_lumos.py:20749 斷言 stdout 含「應派」——白話需保留「應派」一詞 |
| scripts/lumos:4979 | 查不到編制表、只有原因說明時 | `應派: —(...)` | 提醒:這一輪目前算不出「應該派誰」,原因是:{roster_note 白話}。 | 同上,保留「應派」一詞 |
| scripts/lumos:4982 | 有 canary_type / record_cmd / scope_cap / cluster_hint / note 其中一項時,逐項印 | `  {k}: {out[k]}` | (見下方對各欄位內容的個別建議——這行只是外層印法,不用單獨改) | 見下 |

### cmd_loop_next 裡真正要翻的長段提示(透過上面 4982 那行印出)

| file:line(組字處) | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:4912-4915 | phase=plant-canary 時,示範怎麼記這一輪的審查結果 | `record_cmd: lumos canary record caught\|missed --loop {id} --round rN --auditor <席> --severity <s> --findings <M> --spec <計劃節點.md> --reviewed <sha256> --tier ...` | 提醒:這一輪審完後,照下面這行指令記錄結果(把 <> 裡的內容換成實際值)。<br>沒記這一筆,系統就不知道這輪有沒有審過、有沒有問題。<br>`{record_cmd 內容}` | 有:scripts/test_lumos.py:14338 斷言 dict 含鍵 `record_cmd`(結構鍵,非文字)——只要保留鍵名與可執行指令格式即可 |
| scripts/lumos:4917-4925 | 非 light/legacy 分級時,額外印「處置閘」記錄範本 | `disposal_cmd: ... --findings-set <id串> --folded-set <id串> --accepted-set <id串> --accept-reason <id=理由> ...` + `disposal_gate: lumos loop status {id} --disposal ...` | 提醒:如果這輪要走「每個發現都要有處置結果(折掉/放行)」的嚴格收斂,改用下面這行指令記錄,並用第二行檢查有沒有真的收斂。<br>`{disposal_cmd 內容}`<br>`{disposal_gate 內容}` | 有:scripts/test_lumos.py:14338 斷言 dict 含鍵 `disposal_cmd`、`disposal_gate` | 
| scripts/lumos:4929-4934 | 分級沒定錨、判定成 legacy、且是 code 審查系列時 | `★本 loop 無 tier 定錨,正在吃 legacy 判準...★。legacy 不是可宣告值。補 --tier high 會被格式一致性當場擋掉(rc2);--tier standard 格式相容...但★既有輪數會整批計入 cap=3★...` | 提醒:這個審查編號從沒指定過分級,系統現在用最寬鬆的舊規則在跑(單人審、最多 6 輪)。<br>這規則比較鬆,之後想換嚴一點的規則要注意:已經跑過的輪數會被整批算進新規則的上限裡,可能換完馬上就到頂。<br>`要換嚴格規則,請開一個新的審查編號,並從第一筆記錄就指定分級。` | 有:scripts/test_lumos.py:14983-14989 斷言含「開新 loop id」與「cap 6」——白話需保留這兩個字串或同步改測試 |
| scripts/lumos:4936-4941 | 同上但非 code 系列(設計審查) | `★本 loop 無 tier 定錨...★這個 loop 補標不了★:帳面已是 legacy 格式...要走分級判準請★開新 loop id...★` | 提醒:這個審查編號從沒指定過分級,系統在用最寬鬆的舊規則跑,而且★沒辦法事後補分級★——記錄格式已經定型了。<br>想走嚴格一點的分級規則,只能重新開始。<br>`請開一個新的審查編號,並從第一筆記錄就指定分級。` | 有:scripts/test_lumos.py:20970 只驗 tier_hint 存在(bool);內容字串未逐字釘 |
| scripts/lumos:4944-4953 | phase=plant-canary 時一定印(每輪派工前) | `★派工前先量★ wc -l <工作副本/patch>:超過 1800 行(≈30K token)就★拆開審★...★這條門檻純粹借自外部文獻——本專案自己跑過三次對照實驗都測不出規模效應,不得引用自家資料當佐證★...` | 提醒:派這一輪審查工作之前,先算一下這次要審的東西有多少行。<br>超過 1800 行左右,建議拆開審或分給多人各審一段——材料太長時審查員容易看不完、漏東西,這是外部研究的結論,不是本專案自己量出來的(本專案跑過三次自己的對照實驗,沒量到這個效應)。<br>`wc -l <工作副本或 patch 檔>` | 有:scripts/test_lumos.py:15104 斷言 stdout 同時含「scope_cap」與「wc -l」——白話需保留「wc -l」這個指令字面 |
| scripts/lumos:4960-4965 | 第一輪(N=1)且非 light/legacy/循序模式時才印 | `★本loop第一輪——cluster 帳只有現在能選...★:若預期 findings 會散成★性質不同★的風險群...改用 --clusters '名=resolved\|accepted-minor:理由\|disputed-major' 逐群追蹤...` | 提醒:這是這個審查編號的第一輪——「要不要把發現的問題分組追蹤」只有現在能決定,之後沒辦法補選。<br>如果你預期會冒出好幾種性質完全不同的問題(例如「規格縮水」跟「邊界錯誤」),分組追蹤比較不會互相蓋掉。<br>單一主題、問題性質差不多的話用預設(不分組)就好,不用管這行。 | 有:scripts/test_lumos.py:14232-14237 斷言 dict 含鍵 `cluster_hint`,內容含「第一輪」與「開新 loop id」——白話需保留這兩個字串 |

---

## 二、cmd_loop_status 各模式的閘訊息(PANEL/LIGHT/SETTLE/DISPOSAL GATE FAIL/PASS、G1/G2/G3)

### 2.1 legacy / --gate 模式(scripts/lumos:4347-4601)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:4457-4459 | light 分級、曾經有一輪抓到 major/blocker 等級問題(永久升級) | `⛔ LIGHT GATE FAIL ({loop_id}: ratchet——已有 caught 輪 severity≥major,永久升 standard;開新 panel loop id...)` | 擋下:「{loop_id}」曾經有一輪抓到過嚴重問題(major 以上),light 這個最寬鬆的規則從此永久失效,不會再放行。<br>這是設計上的安全閥——出現過嚴重問題,就不該再用最寬鬆的規則審。<br>`開一個新的審查編號(在原編號後面加 -std),換嚴格一點的規則繼續。` | 無 |
| scripts/lumos:4461 | 這個審查編號完全沒有任何記錄 | `⏳ 無記錄 ({loop_id})` | 提醒:「{loop_id}」目前一筆記錄都還沒有。 | 無 |
| scripts/lumos:4486 | light 模式的收斂檢查沒通過 | `⛔ LIGHT GATE FAIL ({loop_id}): {fails 拼接}` | 擋下:「{loop_id}」還沒通過收斂檢查,原因:{fails 白話拼接}。 | 無 |
| scripts/lumos:4488 | light 模式通過 | `✅ LIGHT GATE PASS ({loop_id}: 單席 caught∧max≤minor∧互證∧hash 鏈驗訖 K=1)` | 提醒:「{loop_id}」通過了(單人審完、沒有中等以上問題、記錄互相對得上、內容沒被事後改過)。 | 無 |
| scripts/lumos:4503 | 一般模式,連續達標輪數已夠 | `✅ CONVERGED ({loop_id}, 連 {need} 輪 caught+乾淨;共 {len(rounds)} 輪)` | 提醒:「{loop_id}」已經連續 {need} 輪都審完且乾淨,判定收斂,總共跑了 {len(rounds)} 輪。 | 有:scripts/test_lumos.py:199,201,685 斷言 stdout 含「CONVERGED」——白話需保留「CONVERGED」或同步改測試 |
| scripts/lumos:4506 | 一般模式,還沒達標 | `⏳ 還需 {need - streak} 輪乾淨 ({loop_id}, 已 {len(rounds)} 輪)` | 提醒:「{loop_id}」還需要再連續 {need-streak} 輪乾淨才算收斂,目前已經跑了 {len(rounds)} 輪。 | 無 |
| scripts/lumos:4520/4522 | --gate 模式,檢查「連續達標輪數」這一關 | `[gate] K-streak(--need {need}): ✓` / `✗ — 還需 {need-streak} 輪...` | 提醒:第一關「連續乾淨輪數」{通過/沒通過:還需要 {need-streak} 輪}。 | 有:scripts/test_lumos.py:190,216 斷言 stdout 含「K-streak」——白話需保留「K-streak」或改測試斷言 |
| scripts/lumos:4525 | --gate 且沒帶 --spec | `[gate] G1 refcheck(引用座標): skipped(無 spec 對象,code-loop 情境)` | 提醒:第二關「文件裡的檔案/行號引用對不對」這次沒有比對對象,跳過不檢查。 | 無 |
| scripts/lumos:4535 | --gate 且 --spec 裡有引用指向不存在的檔案/行號 | `[gate] G1 refcheck(引用座標): ✗ — {len(bad)} 條壞宣稱` | 擋下:第二關沒過——文件裡有 {len(bad)} 條引用(指到檔案或行號)其實對不上真正的程式碼。 | 無(組合關鍵字「refcheck」查無獨立斷言,scripts/lumos:4532 的產出結構在別處測) |
| scripts/lumos:4541 | 同上,全部引用都對得上 | `[gate] G1 refcheck(引用座標): ✓ — {len(claims)} 條宣稱全 ok` | 提醒:第二關通過——文件裡 {len(claims)} 條引用全部對得上真正的程式碼。 | 無 |
| scripts/lumos:4564 | --gate,第三關「發現數量該遞減到 0」沒過 | `[gate] G2 發現枯竭: ✗ — {g2_fail}` | 擋下:第三關沒過——{g2_fail 白話}(這輪之前找到的問題數應該要一路遞減到 0 附近,現在還沒有)。 | 無 |
| scripts/lumos:4567 | 同上,通過 | `[gate] G2 發現枯竭: ✓ — findings={fs}` | 提醒:第三關通過——每輪找到的問題數已經遞減到 {fs}。 | 無 |
| scripts/lumos:4572 | --min-seats,審查人數不足 | `[gate] min-seats: ✗ — 窗內第 {輪次} 輪席數不足({min_seats} 席制;逐輪驗非空,空席不計)` | 擋下:規定要 {min_seats} 個不同的人審,但第 {輪次} 輪實際不夠人(重複算同一人、或沒填名字都不算數)。 | 有:scripts/test_lumos.py 多處(如 15155,20844)斷言 stdout 含「席」——白話保留「席」字 |
| scripts/lumos:4576 | 同上,人數足夠 | `[gate] min-seats: ✓ — 窗內 {len(tail)} 輪逐輪 ≥ {min_seats}` | 提醒:審查人數足夠——這 {len(tail)} 輪每一輪都有 {min_seats} 人以上不同的人審過。 | 同上 |
| scripts/lumos:4585 | --spec 帶了,雙重指紋(hash)串不起來 | `[gate] G3 hash 鏈: ✗ — {err}` | 擋下:第四關沒過——{err 白話}(用來證明「審的就是這份文件、沒被事後改過」的指紋串不起來)。 | 無 |
| scripts/lumos:4588-4589 | 收斂窗內完全沒有指紋記錄 | `[gate] G3 hash 鏈: ✗ — 收斂窗未綁 spec hash(帶 --spec 即要求驗證;請重審一輪並於 record 帶 --spec/--reviewed)` | 擋下:第四關沒過——這幾輪都沒留下「審的是哪份文件」的指紋。<br>`請重審一輪,記錄時帶上文件路徑與內容指紋。` | 無 |
| scripts/lumos:4592 | 指紋串驗證通過 | `[gate] G3 hash 鏈: ✓ — {info}` | 提醒:第四關通過——{info}(文件在整個審查過程中沒被偷改過)。 | 無 |
| scripts/lumos:4598 | --gate 有任何一關沒過 | `⛔ GATE FAIL ({loop_id}: {'/'.join(fails)})` | 擋下:「{loop_id}」沒通過收斂檢查,卡在:{fails 白話清單}。 | 無 |
| scripts/lumos:4600 | --gate 全部四關都過 | `✅ GATE PASS ({loop_id}: K-streak ∧ G1 ∧ G2 ∧ G3)` | 提醒:「{loop_id}」四關全過,判定收斂。 | 無 |

### 2.2 panel(多人)模式(scripts/lumos:3566-3879)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:3683 | 這個審查編號沒有任何 panel 格式記錄 | `⏳ 無 panel 輪記錄 ({loop_id})` | 提醒:「{loop_id}」還沒有任何一輪的多人審查記錄。 | 無 |
| scripts/lumos:3614/3617 | 這輪算「有效」(人數夠、沒漏審) | `[panel] 輪有效(no-canary 制,記帳席 {n}): ✓` / `[panel] 輪有效(canary caught {n}/{n},near-perfect): ✓` | 提醒:這輪有效——{n} 個人都記了帳、沒有人漏審。 | 有:scripts/test_lumos.py:14434 斷言 stdout 含「輪有效」——白話需保留「輪有效」一詞 |
| scripts/lumos:3620/3624/3731/3798 | 這輪判定無效(有人漏審 / 記帳人數不足) | `[panel] 輪有效: ✗ — {missed} missed(...)` 等四種變體 | 擋下:這輪無效——{原因白話:有人沒審完 / 記帳人數不夠}。這一輪的結果不能拿來當收斂證據。 | 有:scripts/test_lumos.py:14434 同上保留「輪有效」 |
| scripts/lumos:3630 | 這輪存活的問題等級太高(major/blocker) | `[panel] falsification+ODC(存活 max≤minor): ✗ — 存活 {blocker/major}` | 擋下:這輪還留著等級「{blocker/major}」的問題沒解決,等級太高不能算過關。 | 無 |
| scripts/lumos:3634 | 存活問題都在可接受等級 | `[panel] falsification+ODC(存活 max≤minor): ✓` | 提醒:這輪留下的問題等級都在可接受範圍內。 | 無 |
| scripts/lumos:3641/3646/3651 | 重疊命中估計(觀測用,不影響過不過關) | `[panel] capture-recapture 殘餘(advisory,不進合取): ...` | 提醒(僅供參考,不影響本輪過不過):估計還有 {N} 個問題可能沒被抓到——這個數字不拿來當放行依據。 | 無 |
| scripts/lumos:3743/3749 | 需要連續兩輪都乾淨,但前一輪不合格或不存在 | `[panel] K=2 前一輪: ✗ — 僅一輪(...)` / `✗ — {前一輪}: {前一輪失敗原因}` | 擋下:這個規則要連續兩輪都合格,但{只有一輪/前一輪沒過關}。 | 有:scripts/test_lumos.py 兩處斷言含「K=2 前一輪」——白話保留該詞或改測試 |
| scripts/lumos:3762 | 前一輪合格 | `[panel] K=2 前一輪({prev_rid}): ✓ ({obs})` | 提醒:前一輪({prev_rid})也合格。 | 同上 |
| scripts/lumos:3573/3576 | 判定輪加驗:不同人數是否達標 | `[panel] min-seats: ✗ — 席數不足(...)` / `✓ — {n} 相異席 ≥ {min}` | 擋下/提醒:{沒/有}達到規定的不同審查人數({n} vs 要求 {min})。 | 有:同上保留「席」字 |
| scripts/lumos:3580/3583/3586 | 判定輪的文件指紋檢查 | `[panel] G3 hash: ✗/✓ — {info}` | 擋下/提醒:文件指紋{沒/有}對上,{代表文件事後被改過/沒被改過}。 | 無 |
| scripts/lumos:3734/3769/3869 | panel 收斂檢查沒過 | `⛔ PANEL GATE FAIL ({loop_id} 輪 {rid}: {原因})` | 擋下:「{loop_id}」第 {rid} 輪沒通過:{原因白話}。 | 無 |
| scripts/lumos:3773/3776/3873/3877 | panel 收斂檢查通過 | `✅ PANEL GATE PASS ({loop_id} 輪 {rid}: ...)` | 提醒:「{loop_id}」第 {rid} 輪通過收斂檢查。 | 無 |
| scripts/lumos:3774/3875 | 通過後,決定要不要額外抽查 | `[panel] 抽查判定(e',決定性可重算): ★應抽查★... / 免抽` | 提醒:系統算出這輪{要/不用}額外抽查——這個判定任何人都能重算出一樣的結果,不是誰說了算。 | 有:scripts/test_lumos.py:12686,12690 斷言 stdout 含「抽查」且兩次呼叫結果一致——白話保留「抽查」一詞 |
| scripts/lumos:3794/3796/3798 | cluster(分組)帳,判定輪是否有效 | `[panel/cluster] 條1 輪有效(...): ✓/✗` | 提醒/擋下:這輪{有效/無效}(判斷依據同上「輪有效」)。 | 保留「輪有效」 |
| scripts/lumos:3816/3819 | 分組帳,有沒有「爭議且嚴重」的分組沒解決 | `[panel/cluster] 條2 fold 後無 disputed-major: ✗ — {N} 個: {清單}` / `✓` | 擋下/提醒:{有/沒有}分組還卡在「爭議且嚴重」狀態——{清單}。 | 無(disputed-major 多為 CLI 值,非此行文字斷言) |
| scripts/lumos:3823/3826 | 分組帳,這輪新出現了哪些分組(僅供參考) | `[panel/cluster] (advisory) 新生 cluster: {N} 個` | 提醒(僅供參考):這輪新冒出 {N} 個問題分組。 | 無 |
| scripts/lumos:3845 | 無效輪裡也帶了分組資料,列出來但不採信 | `⚠ {rid}(無效輪) clusters 已忽略: {清單}` | 提醒:第 {rid} 輪是無效輪,它帶的分組資料不採信,但列出來備查:{清單}。 | 無 |

### 2.3 settle(結清式收斂)模式(scripts/lumos:4246-4344)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:4256 | 共用記錄檔有讀不懂的壞行 | `ERROR: canary-log 含 {n} 行不可解析——settle 輪鍵=append 序,壞行使序號位移,fail-closed 及於整個共用檔` | 擋下:記錄檔裡有 {n} 行讀不懂,這會讓輪次編號全部往後歪掉,所以整個檔案都先不信。<br>`修好或搬走壞掉的那幾行,再重跑一次。` | 無 |
| scripts/lumos:4314 | 待結清清單裡還有項目沒收尾 | `[settle] 清單全結清: ✗ — {n}/{total} 條未結清` | 擋下:清單裡還有 {n}/{total} 條沒收尾,不能算收斂。 | 無 |
| scripts/lumos:4319 | 清單全部收尾 | `[settle] 清單全結清: ✓ — {total} 條(...)` | 提醒:清單裡 {total} 條全部收尾了。 | 無 |
| scripts/lumos:4323/4326 | 文件引用檢查(同 G1) | `[settle] G1 refcheck: ✗/✓ — ...` | 擋下/提醒:文件裡的引用{有壞掉的/全部對得上}。 | 無 |
| scripts/lumos:4329/4332/4335 | 最後一筆記錄的文件指紋要對上目前的文件 | `[settle] G3 末筆對齊: ✗/✓ — ...` | 擋下/提醒:最後一筆記錄的文件指紋{沒有/有}對上現在的文件版本。 | 無 |
| scripts/lumos:4341 | settle 收斂檢查沒過 | `⛔ SETTLE GATE FAIL ({loop_id}: {原因})` | 擋下:「{loop_id}」沒通過:{原因白話}。 | 無 |
| scripts/lumos:4343 | settle 收斂檢查通過 | `✅ SETTLE GATE PASS ({loop_id}: 清單全結清 ∧ G1 ∧ G3)` | 提醒:「{loop_id}」通過收斂檢查(清單收尾、引用對上、文件沒被偷改)。 | 有:scripts/test_lumos.py:3617 斷言 stdout 含「SETTLE GATE PASS」——白話需保留這個字串或同步改測試 |

### 2.4 disposal(處置閘)模式(scripts/lumos:9422-9586)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:9434 | 共用記錄檔有讀不懂的壞行 | `ERROR: canary-log 含 {n} 行不可解析——disposal 閘 fail-closed...——壞行行號: {..}` | 擋下:記錄檔裡有 {n} 行讀不懂(第 {行號} 行),所以不敢信「最後一輪」是哪一輪,先擋下。<br>`檔案有 git 版控,對照上一版找出壞的那幾行修好。` | 無 |
| scripts/lumos:9466 | 這個審查編號完全沒有記錄 | `⏳ 無記錄 ({loop_id})` | 提醒:「{loop_id}」目前一筆記錄都沒有。 | 無 |
| scripts/lumos:9481/9484/9487 | 文件指紋鏈檢查 | `[disposal] G3 hash: ✗/✓ — ...` | 擋下/提醒:文件指紋{對不上/對得上}。 | 無 |
| scripts/lumos:9495 | 這輪沒有任何「處置結果」記錄 | `[disposal] 處置集合: ✗ — 判定輪無處置帳(record 帶 --findings-set/--folded-set/--accepted-set)` | 擋下:這輪還沒記錄「找到的問題各自怎麼處置了」。<br>`記錄時要帶上發現清單與各自的處置結果(折掉/放行)。` | 無 |
| scripts/lumos:9512 | 處置結果記錄有矛盾(重複算、少算、少理由、blocker 卻放行) | `[disposal] 處置集合: ✗ — {bad}` | 擋下:這輪的處置記錄有問題——{bad 白話}。 | 無 |
| scripts/lumos:9515 | 處置記錄完整無矛盾 | `[disposal] 處置集合: ✓ — {N} 條全處置(折 {a}/放行 {b},理由齊)` | 提醒:這輪 {N} 個發現全部有處置結果,且都附了理由。 | 無 |
| scripts/lumos:9520/9533/9542/9547 | 這輪某人的審查報告/快照留痕缺失或對不上 | `[disposal] 留痕: ✗ — {原因}` | 擋下:{某人}的審查報告或凍結快照{沒留/讀不到/內容被事後改過},收貨留痕失敗。 | 無 |
| scripts/lumos:9551 | 全員留痕都在且沒被改過 | `[disposal] 留痕: ✓ — 判定輪全席 {n} 份留痕存在且 sha256 與帳面一致` | 提醒:這輪全部 {n} 份審查留痕都在,且都沒被事後改過。 | 無 |
| scripts/lumos:9557/9562/9568 | 報告裡的引句錨不進凍結快照(或報告根本沒引句) | `[disposal] quote-check: ✗ — {原因}` | 擋下:審查報告裡的引句{讀不成文字/一句都沒有/有 {n} 句在凍結快照裡找不到}——沒引句就不算驗證過。 | 無(見下方 cmd_quote_check 一節,同一套判斷邏輯的獨立命令有自己的測試) |
| scripts/lumos:9572 | 引句全部錨定成功 | `[disposal] quote-check: ✓ — {n} 條引句全數錨定` | 提醒:審查報告裡 {n} 句引言,全部都能在凍結快照裡找到原文。 | 無 |
| scripts/lumos:9583 | disposal 四條合取有任何一條沒過 | `⛔ DISPOSAL GATE FAIL ({loop_id} 輪 {rid}: {原因})` | 擋下:「{loop_id}」第 {rid} 輪沒通過處置閘:{原因白話}。 | 無 |
| scripts/lumos:9585 | 四條全過 | `✅ DISPOSAL GATE PASS ({loop_id} 輪 {rid}: ...)` | 提醒:「{loop_id}」第 {rid} 輪通過處置閘(指紋對、處置全清、留痕可重算、引句全錨定)。 | 無 |

---

## 三、cmd_canary(即 `lumos canary record` 的實作;每記一筆審查結果就印一次,repo 裡出現頻率最高的一批指令之一)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:3253 | --round 用了系統保留的內部字首 `__` | `ERROR: --round 不得以 __ 開頭(內部保留字首): {round_id!r}` | 擋下:輪次編號不能用「__」開頭,這個字首系統內部保留在用。<br>`换一個不是 __ 開頭的輪次編號。` | 無 |
| scripts/lumos:3260 | --capture-counts 格式不對(不是逗號分隔整數) | `ERROR: --capture-counts 需逗號分隔整數,收到 {capture_counts!r}` | 擋下:重疊命中的數字要用逗號分隔的整數,你給的格式不對。<br>`改成像「2,1,1」這樣的格式。` | 無 |
| scripts/lumos:3269 | --clusters 的分組字串格式錯 | `ERROR: --clusters {err}` | 擋下:分組設定寫錯了——{err 白話}。 | 無 |
| scripts/lumos:3274 | --spec 和 --reviewed 只給了其中一個 | `ERROR: hash 雙欄必須成對(--spec 與 --reviewed 同現;reviewed=派工當下真檔 sha256)` | 擋下:文件路徑(--spec)跟內容指紋(--reviewed)要嘛一起給、要嘛都不給,你只給了一個。<br>`兩個一起補上,--reviewed 填派工當下那份文件的內容指紋(sha256)。` | 無 |
| scripts/lumos:3281 | --spec 指的文件讀不到 | `ERROR: 讀不到 --spec {spec}: {e}` | 擋下:讀不到 --spec 指的檔案({e})。<br>`確認路徑對不對、檔案還在不在。` | 無 |
| scripts/lumos:3284 | --reviewed 不是合法的 64 碼指紋 | `ERROR: --reviewed 需 64 位 sha256 hex,收到 {reviewed!r}` | 擋下:--reviewed 要填 64 碼的 sha256 指紋,你給的格式不對。 | 無 |
| scripts/lumos:3301 | --tokens / --wallclock-min / --scope-lines 給了負數 | `ERROR: --{name} 需非負整數,收到 {val}` | 擋下:{欄位名} 只能填非負整數,你給的是負數。 | 無 |
| scripts/lumos:3306-3309 | 這輪被審材料超過軟性上限(1800 行) | `⚠ 本輪被審材料 {N} 行,超過軟上限 1800 行(≈30K token,...)。已在帳上標記 scope_oversize。★這一輪的 caught 是弱證據★——...` | 提醒:這輪要審的東西有 {N} 行,超過建議的 1800 行上限(外部研究認為材料太多容易看不完、漏審)。<br>這不會擋你記錄,但這輪抓到的結果會被標記成「證據力較弱」——因為審查員可能是看不完、不是真的沒問題。<br>`下一輪建議拆開來審。` | 有:scripts/test_lumos.py:15088,15099 斷言 stderr 含「軟上限」——白話需保留「軟上限」一詞 |
| scripts/lumos:3313 | --tier 給的值不在允許清單裡 | `ERROR: --tier 需 light/standard/high,收到 {tier!r}` | 擋下:分級只能是 light、standard 或 high 三選一,你給的不在裡面。 | 無 |
| scripts/lumos:3323 | --folded-set 等處置欄位給了,但沒給 --findings-set | `ERROR: --folded-set/--accepted-set/--accept-reason 須與 --findings-set 同現` | 擋下:要記處置結果(折掉/放行/理由),一定要先給「找到的問題清單」(--findings-set)。 | 無 |
| scripts/lumos:3327 | --findings-set 給了但是空的 | `ERROR: --findings-set 不得為空(沒 findings 就別帶處置欄)` | 擋下:「找到的問題清單」不能是空的——沒有問題就不用帶這些處置欄位。 | 無 |
| scripts/lumos:3330 | --findings-set 裡有重複的 id | `ERROR: --findings-set 含重複 id: {f_set}` | 擋下:問題清單裡有重複的編號:{f_set}。 | 無 |
| scripts/lumos:3335 | 折掉/放行的清單裡出現不在原始問題清單的 id | `ERROR: folded/accepted 含 findings-set 以外的 id` | 擋下:「折掉」或「放行」的清單裡,出現了不在原始問題清單裡的編號。 | 無 |
| scripts/lumos:3338 | 同一個問題同時出現在「折掉」跟「放行」 | `ERROR: folded 與 accepted 互斥,交集非空: {..}` | 擋下:同一個問題不能同時算「折掉」又算「放行」,兩邊重複了:{清單}。 | 無 |
| scripts/lumos:3341-3343 | 有問題沒被歸類到「折掉」或「放行」 | `ERROR: 未處置的 finding: {..}(folded∪accepted 必須=findings-set;每一條都要有去向)` | 擋下:有些問題還沒決定要「折掉」還是「放行」:{清單}。<br>每一條問題都要有個去向。 | 無 |
| scripts/lumos:3347 | --accept-reason 格式不對(不是 `id=理由`) | `ERROR: --accept-reason 格式須 id=理由,收到 {item!r}` | 擋下:放行理由要寫成「編號=理由」的格式,你給的格式不對。 | 無 |
| scripts/lumos:3352-3353 | 放行理由跟放行清單對不上,或理由是空的 | `ERROR: accept_reasons 鍵集合須=accepted-set 且理由非空(...)` | 擋下:放行清單裡的每一項都要有理由,而且理由不能是空的;請確認兩邊對得上。 | 無 |
| scripts/lumos:3356 | 這輪有 blocker 等級問題,卻還要放行 | `ERROR: blocker 輪 accepted 必須為空——blocker 只能折不能放行(重設計 d1)` | 擋下:這輪有嚴重到 blocker 等級的問題,規定 blocker 級問題只能折掉、不能放行,不能有放行清單。 | 有:scripts/test_lumos.py 斷言含「blocker」相關(rc2 為主,字串「輪內有 blocker 席」未逐字釘) |
| scripts/lumos:3367 | --report 或 --snapshot 指的檔案讀不到 | `ERROR: {--report/--snapshot} 讀不到: {e}` | 擋下:讀不到 {--report/--snapshot} 指的檔案({e})。 | 無 |
| scripts/lumos:3371 | --report 或 --snapshot 指的檔案是空檔 | `ERROR: {--report/--snapshot} 是空檔——留痕的最低要求是非空({_p})` | 擋下:{--report/--snapshot} 這個檔案是空的——留痕至少要有內容。 | 無 |
| scripts/lumos:3408-3409 | 這個審查編號已經定錨成「處置閘」模式,但這筆記錄沒帶報告/快照 | `ERROR: loop {loop!r} 已定錨為 disposal loop(帳面有 findings_set 記錄)——後續 record 必帶 --report 與 --snapshot(留痕強制;T6)` | 擋下:「{loop}」這個審查編號已經走上「處置閘」模式(之前記過問題清單),之後每一筆記錄都得附上審查報告和凍結快照。<br>`補上 --report 與 --snapshot 再重記。` | 無(rc2 為主,scripts/test_lumos.py:14372 只驗 rc==2) |
| scripts/lumos:3414-3415 | 記錄成功(repo 裡出現頻率最高的一行之一,每記一筆就印一次) | `✓ canary {kind} 留痕: {token} (auditor={auditor}) → {path}` | 提醒:這筆審查結果已經記下來了,審查員是「{auditor}」,存在 {path}。 | 無(scripts/test_lumos.py 對 canary record 成功案例多以 expect_rc=0 驗證,不比對這行文字) |
| scripts/lumos:3429 | 寫入記錄檔失敗(IO 層) | `ERROR: 寫入 {path} 失敗: {e}` | 擋下:寫不進記錄檔 {path}({e})。<br>`檢查磁碟空間或寫入權限。` | 無 |
| scripts/lumos:3443/3445 | 寫完後回頭讀,發現讀不回這一筆(落盤自驗失敗) | `canary record: 落盤自驗失敗({path}): 讀回失敗 {e}` / `...寫入回報成功但讀不回該筆` | 擋下:剛剛雖然回報寫入成功,但重新打開檔案卻讀不到這一筆,可能沒有真的存進去。<br>這是很嚴重的資料遺失風險,一定要查清楚。<br>`重跑一次記錄指令,若持續失敗請檢查磁碟或檔案系統。` | 有:scripts/test_lumos.py:11586 斷言 stderr 含「落盤自驗失敗」——白話需保留「落盤自驗失敗」一詞或同步改測試 |

---

## 四、cmd_quote_check / cmd_seat_check / cmd_refcheck 的輸出

### cmd_quote_check(scripts/lumos:9589-9623)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:9601 | 報告或快照檔讀不到 | `ERROR: 讀不到檔案: {e}` | 擋下:讀不到報告或快照檔案({e})。 | 無 |
| scripts/lumos:9605-9609 | 報告裡一句引言都抽不到 | `ERROR: 報告內抽不到任何「引句：「…」」——驗不了≠通過;...①②③④` | 擋下:這份報告裡完全找不到「引句：「…」」格式的引言——沒引言就沒辦法驗證,不能當作通過。<br>常見原因:格式標籤打錯、用了半形引號、引言跟標籤不同行、引號沒有成對關閉。<br>`照格式補上引句再重記。` | 無(rc2 為主) |
| scripts/lumos:9617-9620 | 逐條列出每句引言核對結果 | `  {✓/✗} #{i} 「{quote 前60字}」{過短提示}` | 提醒:第 {i} 句{對得上/對不上}原文:「{引句}」{若過短:這句太短,判定不算數}。 | 無 |
| scripts/lumos:9621-9622 | 總結行 | `{✅ 全數錨定 / ⛔ N/M 條錨不到}(正規化=NFC+剝 */`+空白摺疊;比對對象應為派工凍結快照)` | 提醒:{全部引言都對得上原文 / 有 {N}/{M} 句對不上原文,這幾句不算數}。<br>比對的應該是派工當下凍結的快照,不是現在最新的文件。 | 無 |

### cmd_seat_check(scripts/lumos:10032-10103)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:10051 | 報告或派工單讀不到/格式壞 | `ERROR: 讀 report/dispatch 失敗: {e}` | 擋下:讀不到審查報告或派工單,或格式壞了({e})。 | 無 |
| scripts/lumos:10060 | 這次派工單沒指定要查哪些材料 | `seat-check: materials 為空 → vacuous 豁免(不判 unreported/out_of_scope)` | 提醒:這次派工沒指定要查哪些材料,所以「有沒有漏查」「有沒有查超出範圍」這兩項都不檢查。 | 有:scripts/test_lumos.py:20323-20324 斷言 stdout 含「vacuous」——白話需保留「vacuous」一詞或同步改測試 |
| scripts/lumos:10091 | 寫「越界」帳失敗 | `ERROR: 越界帳寫入失敗: {e}` | 擋下:記錄「引言查超出範圍」失敗({e})。 | 無 |
| scripts/lumos:10096-10097 | 對帳結果總結行(每次跑都印) | `seat-check {報告檔名}: unreported {n1} / out_of_scope {n2}(materials {n};觀測恆 rc0)` | 提醒:對帳結果——有 {n1} 份指定要查的材料完全沒被提到,有 {n2} 句引言查超出了指定材料的範圍(這只是觀測,不會擋你)。 | 有:scripts/test_lumos.py:20301,20306,20313 逐字斷言「unreported 0/1」「out_of_scope 0/1」——白話務必保留「unreported N」「out_of_scope N」這個格式 |
| scripts/lumos:10099 | 逐條列出沒被提到的材料 | `  ⚠ unreported: {mp}(dispatch 宣告要查,報告零觸及)` | 提醒:「{mp}」這份材料,派工單說要查,但報告裡完全沒提到。 | 見上,保留「unreported」 |
| scripts/lumos:10101 | 逐條列出查超範圍的引言 | `  ⚠ out_of_scope: 「{q}」(錨不進任何 material...)` | 提醒:引言「{q}」在任何一份指定材料裡都找不到,查超出範圍了。 | 見上,保留「out_of_scope」 |
| scripts/lumos:10102 | 收尾提醒本檢查的極限 | `  ★觀測非閘:抓的是協議內一致性;lens 不判定;證據 file:line 恆合法★` | 提醒:這項檢查只是觀測、不會擋人;它抓的是「報告有沒有照派工單做」,抓不到「引言雖然對得上材料、但內容是編的」這種說謊方式。 | 無 |

### cmd_refcheck(scripts/lumos:13110-13152)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:13118 | 要檢查的文件不存在 | `ERROR: 找不到檔案: {md_path}` | 擋下:找不到要檢查的文件「{md_path}」。 | 無 |
| scripts/lumos:13123 | --repo 指的不是一個目錄 | `ERROR: --repo 不是目錄: {repo}` | 擋下:--repo 指定的路徑不是一個資料夾。 | 無 |
| scripts/lumos:13132 | 沒指定 --repo,往上找也找不到 git 專案根目錄 | `ERROR: cwd 逐層向上找不到 .git repo,請用 --repo 指定` | 擋下:從目前目錄往上找,找不到 git 專案的根目錄。<br>`用 --repo 明確指定專案根目錄。` | 無 |
| scripts/lumos:13137 | 文件讀不到 | `ERROR: 讀不到 {md_path}: {e}` | 擋下:讀不到文件「{md_path}」({e})。 | 無 |
| scripts/lumos:13145 | 人讀模式,開頭一行 | `refcheck {md} (repo={repo_root})` | 提醒:正在對照「{md}」裡的引用,專案根目錄是「{repo_root}」。 | 無 |
| scripts/lumos:13146-13150 | 逐條列出每個引用的核對結果 | `  {✓/✗} {status:<17} {loc}{摘錄}` | 提醒:「{引用位置}」{對得上/對不上}真正的檔案內容{狀態白話}。 | 無 |
| scripts/lumos:13151 | 總結行 | `統計: ok {n_ok} / missing {n_missing} / out_of_range {n_oor}` | 提醒:總共 {n_ok} 條對得上、{n_missing} 條指到不存在的東西、{n_oor} 條行號超出檔案範圍。 | 有:scripts/test_lumos.py:5191 斷言 stdout 含「missing」——白話務必保留「missing」這個字(或至少保留這行的機讀格式,同步改測試) |

---

## 五、cmd_gov 與 _render_gov_stats(含未出現清單限制聲明)

### cmd_gov 主體(scripts/lumos:2979-3169)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:3097 | 預設(非 --full)畫面,同一天同群組事件超過 6 個節點時收成一行 | `{date} [{gate}/{kind}/{mark}] {N} 節點({頭三個}…) ×{最大次數}` | 提醒:{date} 這天,「{gate 白話}/{kind 白話}」這類事件一次影響了 {N} 個節點(像是{頭三個}…),最多同一節點發生了 {次數} 次。 | 無 |
| scripts/lumos:3100 | 同上,節點數不多(≤6)時逐節點印 | `{date} [{gate}/{kind}/{mark}] {節點} ×{n}` | 提醒:{date} 這天,「{節點}」發生了「{gate 白話}/{kind 白話}」事件{,共 {n} 次}。 | 無 |
| scripts/lumos:3102 | --full 或有 detail/token 的事件(逐筆保留,repo 裡治理帳最常見的一行格式) | `{ts} [{gate}/{kind}/{mark}] {節點} {detail 前50字}` | 提醒:{ts} 這時候,「{節點}」發生了「{gate 白話}/{kind 白話}」事件({硬擋/軟性})——{detail}。 | 無 |
| scripts/lumos:3106 | 有帶 --node(縮限到單一節點)時,收尾提醒視角限制 | `(註:L2 繞過無 node、L3 以 Verification 為鍵;對 Systems 節點為部分視圖)` | 提醒:有兩類事件天生就沒有節點資訊或算法不同,所以這份清單只能看到「{node}」相關的部分事件,不是全貌。 | 無 |
| scripts/lumos:3122 | 有審查記錄時,印分帳表頭 | `canary 分帳(missed-rate 一級指標):` | 提醒:以下是各審查員的抓漏率統計(這是本專案最看重的一項指標): | 有:scripts/test_lumos.py:9243 斷言 stdout 含「canary 分帳」與「missed-rate 50%」——白話務必保留「canary 分帳」與「missed-rate」這兩個字串,或同步改測試 |
| scripts/lumos:3126 | 逐審查員印一行統計 | `  {aud}: caught {c} / missed {m} (missed-rate {rate:.0%})` | 提醒:「{aud}」抓到 {c} 次、漏掉 {m} 次,漏抓率 {rate}。 | 有:同上,保留格式 |
| scripts/lumos:3129 | 有型別線索時,印分佈 | `  型別分佈: {k}:{c}c/{m}m ...` | 提醒:各種植入類型的抓漏分佈:{清單}。 | 無 |
| scripts/lumos:3136 | 有第二判者覆核記錄時 | `  第二判者覆核: {n} 筆(agree {a} / overturn {o}{分歧率提示})` | 提醒:有人被找來覆核判定,共 {n} 次,{a} 次同意原判、{o} 次翻盤{;分歧率 {r},值得回頭看看}。 | 無 |
| scripts/lumos:3161-3162 | 收尾,印「對抗層增量帳」總結(每次跑 gov 只要有審查記錄就印) | `  對抗層增量帳(折入=測試綠後仍被抓;長期趨零=機關裝飾該砍): 折入 {N} 筆缺陷 [{依等級}] \| 依審計員: {依人}` | 提醒:測試都過了、但審查還是抓到 {N} 個真問題(這個數字若長期趨近 0,代表這套審查機制可以考慮拿掉了)。<br>依嚴重度分:{依等級};依審查員分:{依人}。 | 有:scripts/test_lumos.py:1664-1669 逐字斷言「折入 6」「blocker 2」「major 4」「codex 2」「sonnet 4」「無 findings 欄/舊輪不計」「趨零」——白話務必保留「折入」「趨零」二詞與 `{類別} {數字}` 的格式 |
| scripts/lumos:3164 | 每次跑 gov 都印的總筆數行 | `\n{_shown} 筆(近 {since_days} 天)` | 提醒:近 {since_days} 天內共 {_shown} 筆治理事件。 | 無 |

### _render_gov_stats(--stats 附加報表;scripts/lumos:2931-2977)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:2936 | --stats 表頭第一行 | `[stats] 載入源: {清單}` | 提醒:這次統計實際讀取了這幾個來源:{清單}。 | 有:scripts/test_lumos.py:3061,3188 斷言含「載入源」——保留此詞 |
| scripts/lumos:2937 | --stats 表頭第二行 | `[stats] 窗口: 近 {since_days} 天(自 {cutoff} 起)` | 提醒:統計範圍是最近 {since_days} 天(從 {cutoff} 開始算)。 | 有:scripts/test_lumos.py:3062,3188 斷言含「窗口」——保留此詞 |
| scripts/lumos:2939 | 有帶 --node 時的第三行提醒 | `[stats] ⚠ 已縮限至節點 {node},以下統計僅為該節點視角` | 提醒:以下統計只看「{node}」這個節點,不是全庫。 | 有:scripts/test_lumos.py:3194-3196 斷言第三行含「縮限」——保留此詞 |
| scripts/lumos:2941 | 這個時間窗內完全沒有資料 | `  窗口內無資料` | 提醒:這段時間裡沒有任何治理事件。 | 有:scripts/test_lumos.py:3232 斷言逐字含「窗口內無資料」——需完整保留這個字串或同步改測試 |
| scripts/lumos:2957 | 表格欄位標題行 | `  {gate}{去重後筆數}{原始行數}{不同 nodes 值數}{不同 commit 數}  {首見日} {末見日}` | 提醒:表格欄位依序是:閘名、去重後筆數、原始筆數、影響幾個不同節點、影響幾個不同提交、最早出現日、最晚出現日。 | 有:scripts/test_lumos.py:3057-3058 逐字斷言六個欄位標題——白話若要換欄名須同步改測試斷言 |
| scripts/lumos:2967 | 每個閘一行的統計數字 | `  {g}{ded}{raw}{nd}{cm}  {d1} {d2}{tag}` | 提醒:「{g 白話}」這道閘:去重後 {ded} 筆、原始 {raw} 筆,影響 {nd} 個節點、{cm} 個提交,{d1}~{d2} 之間都有出現{附加語意提示}。 | 有:scripts/test_lumos.py:3059,3076-3078,3092-3095,3115-3116 等多處對這行的欄位值做字串比對(如「n/a」「1」「2」)——動這行前務必核對這些測試 |
| scripts/lumos:2971 | 縮限到單一節點模式,不列「未出現清單」 | `  (縮限模式:不記節點的來源必然零列——結構產物非訊號,不列未出現清單)` | 提醒:因為現在只看單一節點,有些來源本來就不會記節點資訊、一定會是零,所以不列「哪些閘從沒出現過」。 | 無 |
| scripts/lumos:2973 | 全庫模式,列出從沒觸發過的閘 | `  未出現的 gate({N}):{清單}` | 提醒:以下 {N} 道閘在這段時間裡完全沒被觸發過:{清單}。 | 有:scripts/test_lumos.py:3157 斷言含「未出現」與具體閘名——保留此詞 |
| scripts/lumos:2974 | 緊接著印限制聲明(固定文字,來自單一常數) | `  未出現 ≠ 無用。本帳看不到硬擋事件...也分不出四種「沒出現」:跑了沒事／接了帳但沒被觸發／守的功能從沒被用過／本次執行根本沒載入該來源...` | 提醒:「沒出現」不代表這道閘沒用——它可能是真的沒事、可能是這次根本沒讀到它的來源,原因分不清楚。<br>想拿這份清單去判斷「這道閘能不能拿掉」之前,先確認它真的有被列進統計、而且這次有讀到它的來源。 | 有:scripts/test_lumos.py:3160-3161 斷言這段文字逐字等於常數 `_STATS_ABSENT_DISCLAIMER`,且含「硬擋」「沒載入」「從沒被用過」「跑了沒事」四個子句——改寫務必保留這四個詞,並同步改常數本身(測試直接讀常數,不是複製字串) |
| scripts/lumos:2976 | 表格收尾提醒:這裡的數字跟預設畫面的行數不是同一回事 | `  註:以上為「去重列」計數,★不等於 gov 預設畫面的行數★——預設畫面另有一層呈現折疊。` | 提醒:這張表的數字是「去重後」算的,跟不加 --stats 時看到的行數不是同一套算法——預設畫面還會把相似事件再折疊一次。 | 有:scripts/test_lumos.py:3074 斷言含「預設畫面」與「呈現折疊」——保留這兩個詞 |

---

## 六、cmd_search / cmd_context / cmd_contracts 開頭的★提示句

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:1716 | 多詞查詢整串在庫裡查無結果,自動退成各詞分別查(舊格式路徑) | `（多詞回退:整串片語在{範圍}裡無命中,改用各詞 OR 召回;逐詞覆蓋 {逐詞統計}）` | 提醒:你查的整串詞找不到完全一致的結果,系統自動改成「每個詞分開查、有出現就算」。<br>逐詞命中狀況:{逐詞統計}。 | 無(此為 stderr 附加訊息,測試多驗證 JSON/rc,scripts/test_lumos.py 對「多詞回退」關鍵字有零散引用但非此行逐字斷言) |
| scripts/lumos:1719 | 上述回退裡,有詞完全查不到任何結果 | `  ★有詞在{範圍}裡 0 命中(標 ★)——多半是查詢用詞與圖譜用語不一致,先換那個詞再查,別把結果當「圖譜沒有」★` | 提醒:上面標★的那個詞,在圖譜裡完全查不到。<br>這通常代表你用的詞跟圖譜裡的說法不一樣,不代表圖譜真的沒記這件事。<br>`換個說法再查一次。` | 無 |
| scripts/lumos:1773 | 有命中但因為節點已作廢而被隱藏 | `（已隱藏 {N} 筆作廢結果，--include-superseded 顯示）` | 提醒:另外有 {N} 筆命中結果,因為節點已經作廢所以沒顯示出來。<br>`要看被藏的結果,加 --include-superseded。` | 無 |
| scripts/lumos:1805 / 1813 | 有搜到結果、且不是 --json/--files-only 模式(每次搜尋成功都會印,repo 裡「先 search 再動手」的紀律下極高頻) | `★命中≠查完:節點內容用 lumos show <節點> 讀全文再下結論——search 只給索引,拿摘要判「圖譜沒記」是已實證的破口★` | 提醒:搜尋只給你「哪裡可能有」的索引,不是完整內容。<br>光看摘要就下結論「圖譜沒記這件事」,過去已經證實會出錯——重要判斷前要用 `lumos show <節點>` 讀全文再說。 | 無 |
| scripts/lumos:6120 | 節點有 valid_under(使用前提)條件時,context 開頭第一個提醒 | `⚠ 使用前驗證(valid_under){年久提示}:` | 提醒:動這個節點之前,要先確認以下條件現在還成立{;這個節點已經 {age} 天沒更新,條件可能已經過期}: | 無 |
| scripts/lumos:6125 | 節點有合約標記(★INVARIANT★/★DEBT★)時,context 開頭第二個提醒 | `⚠ 合約(動前必讀):` | 提醒:這個節點有動了會壞的硬規定,動手前一定要看: | 無 |
| scripts/lumos:2406 | cmd_contracts 找不到任何合約標記 | `(無合約標記)` / `(全 vault 無合約標記 — 用 ★INVARIANT★/★DEBT★ 前綴標 KEY 行)` | 提醒:{這個節點/整個圖譜}目前沒有登記任何「動了會壞」的硬規定。 | 無 |

---

## 七、cmd_fold_check(scripts/lumos:13059-13107)

| file:line | 何時印 | 原文(截80字) | 建議白話 | 測試依賴 |
|---|---|---|---|---|
| scripts/lumos:13068 | 檔案不存在 | `ERROR: 找不到檔案: {path}` | 擋下:找不到檔案「{path}」。 | 無 |
| scripts/lumos:13073 | 檔案存在但讀不到 | `ERROR: 讀不到 {path}: {e}` | 擋下:讀不到「{path}」({e})。 | 無 |
| scripts/lumos:13090 | 人讀模式,開頭一行 | `fold-check {md}` | 提醒:正在複查「{md}」裡前後對照的段落。 | 無 |
| scripts/lumos:13091-13095 | 列出需要人工確認一致性的段落 | `── 鏡像段(逐段確認與 body 一致)──` + `  ☐ 複查 {s}:與 body 一致?` / `(無鏡像段)` | 提醒:這份文件裡有 {N} 段跟正文互相對照的摘要,請人工確認內容有沒有跟正文兜起來:{逐段列出}。若沒有這類段落則不印。 | 無 |
| scripts/lumos:13096-13099 | 發現同一個數值/設定在文件裡前後寫的不一樣 | `── value-drift ──` + `  ⚠ value-drift: 「{key} {a}」vs 「{key} {b}」` | 提醒:「{key}」這項在文件裡前後寫的不一樣:一處寫「{a}」,另一處寫「{b}」——請確認哪個才對。 | 無(底層函式有直接單元測試,但這行 CLI 輸出本身無字串斷言) |
| scripts/lumos:13100-13103 | 發現只在一邊提到、另一邊沒提到的內容 | `── reverse-omission ──` + `  ⚠ reverse-omission: {A} 有「{token}」{B} 無` | 提醒:「{token}」這件事只有 {A} 那邊寫了,{B} 那邊沒提到——請確認是不是漏寫了。 | 無 |
| scripts/lumos:13105 | 兩種問題都沒有 | `✓ 無 flag` | 提醒:複查通過,沒發現前後矛盾或遺漏。 | 有:scripts/test_lumos.py:4846 驗證底層函式 `_fold_value_drift` 回傳空陣列(非此行 CLI 文字);此行本身「無」CLI 層字串依賴 |

---

## 最常被印的 5 條(依觸發頻率判斷,先改這些)

1. **scripts/lumos:3414-3415**(`cmd_canary` 成功留痕行)——每記一筆審查結果就印一次;整個 loop/canary 家族裡呼叫頻率最高的單一指令(`lumos canary record`)的唯一輸出行,幾乎每輪審查都會印好幾次。
2. **scripts/lumos:1805 / 1813**(`cmd_search` 的「★命中≠查完」提醒)——CLAUDE.md 明訂「search 是進場第一步」,只要搜尋有命中結果、非 --json 模式就會印,是全庫使用頻率最高的提醒句之一。
3. **scripts/lumos:4971**(`cmd_loop_next` 的 `[next] ...` 開頭行)——每次「問下一步該做什麼」都印,是編排者每一輪都會呼叫的入口指令。
4. **cmd_loop_status 各模式的 `✅/⛔ ... GATE PASS/FAIL` 收尾行群**(如 scripts/lumos:4503/4506/4598/4600、3769/3773/3776、4341/4343、9583/9585)——每次檢查「這一輪算不算過關」都會印其中一條,是整個治理機制裡被檢查最多次的訊息類型。
5. **scripts/lumos:3102**(`cmd_gov` 預設畫面的逐筆事件行)——只要跑 `lumos gov`(無參數,最常見用法)就會逐筆印,是查治理歷史時看到最多次的一行格式。
