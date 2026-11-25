severity: minor

## 1. 分層與依賴方向:對齊
- 新邏輯放的層跟既有合併快篩一致。
  - 重排放在 `_kill_merge_iter` 交出配方那一步(file: `scripts/lumos:29097`)。現行 `yield from chunk` 就在那裡,docstring 也寫明逐支迴圈本體一字不改。
  - 名單由 `_choice_merge_classify` 從已讀的 facts 算出(file: `scripts/lumos:28851`),`_kill_merge_screen` 往上帶(file: `scripts/lumos:29064`)。呼叫方向沒變:iter 呼叫 screen,screen 呼叫 classify。
  - `unclean` 計數字典掛在 `_KillMerge` 上,跟既有 `streak`、`tripped`、`survived` 同一條通道(file: `scripts/lumos:28877`)。計數點在 `_kill_merge_breaker`(file: `scripts/lumos:29033`)。
  - 沒有跨層直呼。
- ⚠ 判不準:`_kill_merge_screen` 目前只回字串 "pass"、"single" 或 "break"。計劃說「回 single 時一併帶出名單」,等於回傳形狀混用字串與帶名單的值。既有通道是掛在 `mg` 或 `c` 的屬性,例如 `mg.survived`。帶名單走回傳值還是掛屬性,交編排者決定。不計入條數。

## 2. 命名與錯誤處理:大部分對齊,3 條不對齊

**欄位與計數命名**
- 對齊:`merge_unclean`、`merge_base_why` 的 `merge_` 前綴跟 `merge_tripped` 同族(file: `scripts/lumos:18469`)。
- 對齊:型別登記進 `_GOV_FIELD_TYPES`,`(dict,)` 有 `counts` 的前例,`(str,)` 也有前例。
- 對齊:加進 `ck` 子字典鍵清單的做法,跟前案 `merged`、`single`、`merge_tripped` 同(file: `scripts/lumos:18558`)。
- 對齊:`rx.update(...)` 的寫法也沿用前案(file: `scripts/lumos:79021`)。

**不對齊 A:印字規則反轉了,同步清單漏列**
- 前案白紙黑字規定時限不夠量齊「不印字」,出現在三處:做法 5〈印字〉、做法 1 的條件句、程式 docstring。
- 本案要在 `_kill_merge_ready` 時限門與 `_kill_merge_singles` 重估收手時印一行,等於反轉這條。
- 本案「同一提交改的既有句子」清單只列了做法 1「少於 2 個」、做法 3、舊否決第三條。沒列做法 5〈印字〉,也沒列做法 1 的「不印字」半句。
- 照前案路徑,同提交不改這兩句,筆記會自相矛盾。
- 另外要改 `_kill_merge_ready` 的 docstring「不印字」(file: `scripts/lumos:28901`)。
- 前案對照:`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:64` 與 `:124`。
- 引句:「`_kill_merge_ready` 因時限門(剩下的總時限 < 支數 × 10 秒 × 1.5)回 None 時,印一行到標準錯誤」
severity: minor
- blocking: 否(結構對,只是同步與日誌慣例沒對齊)

**不對齊 B:新印字沒指定既有前綴格式**
- 既有標準錯誤印字一律是 `⚠ {_kill_esc(plat)}:<原因>,這個平台組…`(file: `scripts/lumos:28965`、`scripts/lumos:29044`)。
- 本案的時限提示與改過的斷路器行,文字都沒寫「⚠ 平台:」前綴和 `_kill_esc`。
- 時限門在 ready 裡、`c.plat` 拿得到,也是每平台組各印一次。
- 斷路器那行本來就帶前綴,所以只有時限提示是真缺。
- 引句:「守的測試 N 支,合併要先量齊基準,約需 M 秒,這次剩 R 秒,不合併、改逐支;要合併請帶 --max-seconds <M 無條件進位到百>」
severity: minor
- blocking: 否

**不對齊 C:`unclean` 的鍵多了一層折疊字串**
- 現行 classify 回給斷路器的原因字串有:「逾時」、「被系統收掉」、「找不到 JUnit 結果檔」、「結果檔讀不出來」、「結果檔超過大小上限」(file: `scripts/lumos:28826`、`scripts/lumos:28851`)。
- 本案要把後兩種折成新字串「結果檔讀不出或過大」,等於在 classify 的原因字串之外多一份對照。
- 前案「原因字串」只有一張表 `_CHOICE_MERGE_BASE_WHY`(file: `scripts/lumos:28735`),快篩那一側直接用 classify 的字串。
- 這是新增一份折疊對照,不是沿用既有原因表;不到「第二種做法」(沒有新通道),但字串口徑不一致。
- 簡單對齊法:鍵直接用 classify 的 why,或把折疊寫成跟 `_CHOICE_MERGE_BASE_WHY` 同一張表。
- 引句:「後者一律記成「結果檔讀不出或過大」」
severity: minor
- blocking: 否

## 3. 第二種做法:沒有 major
- 沒引入新通道:資料仍走 `_KillMerge` 屬性,再由 `_choice_kill_report` 的 `rx.update` 寫進 run 事件。
- 沒引入新時限估算:沿用 `_CHOICE_MERGE_UNIT_SECS × _CHOICE_MERGE_BUDGET_K`,只多印一行。
- 沒引入新原因表,見上面不對齊 C。
- ⚠ 判不準:`merge_base_why` 另存一個字串,而 `mg.plats[plat]` 已經存「基準」這種不啟用原因(file: `scripts/lumos:28975`)。兩處各存一份原因,是重複還是刻意分工,交編排者。run 事件是單欄位,多平台組時要取哪一個,計劃也沒寫。不計入條數。
- ⚠ 判不準:`n_mutants` 拿掉判斷後變成程式裡沒人讀的參數,只為「既有測試位置參數建構」保留(file: `scripts/lumos:28877`、`scripts/lumos:78991`)。專案慣例通常連呼叫端一起改,留死參數算不算偏離,交編排者。不計入條數。

## 4. 落點:對齊
- `lands_in` 的 `Systems/guard-kill` 與 `Systems/規格閘` 跟前案相同,而且內容就是這兩篇現有的句子。
  - guard-kill 現有 `_KillMerge`、`_kill_merge_iter` 的 WHY 在 `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:55`。
  - 規格閘現有 run 事件欄位的 WHY 在 `docs/lumos-toolchain-knowledge/Systems/規格閘.md:97`。
- 新增的 `merge_unclean`、`merge_base_why` 寫進規格閘,對照前案 `merged`、`single`、`merge_tripped` 的落點,一致。
- 覆蓋選測試另開一篇計劃合理:它要改被測專案的測試執行引擎、會改判定口徑,跟「只改順序」性質不同。該檔已存在於 `Projects/選擇點變異覆蓋選測試_計劃.md`,本案的〈不做〉也有連結。
- 參考資料裡 Systems/guard-kill 掛 0 份計劃,屬現況,不算不對齊。

不對齊共 3 條,其中 major 0 條(另有 3 個 ⚠ 交編排者,不計入)。
