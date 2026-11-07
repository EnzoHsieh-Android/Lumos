severity: minor

整體評語:API-14、TEST-31 降級的落地(型錄名稱加標記、三條規則搬到 `rules-unwired/`、S2、S3)與程式一致。
- `python3.14 scripts/test_lumos.py -k kotlin_rulepack_unwired` 跑過,11 個全過。
- `-k kt_catalog_security_lint_ids` 跑過,5 個全過。
- 三條規則確實在 `rules-unwired/`,`samples/` 的壞例與好例也還在。
- `check.py` 的 `catalog_problems` 會抓「出處不全的列被放在 `rules/`」,所以降級沒有被悄悄反悔的空間。

官方頁我用 WebFetch 抓了,確認 DataStore 的 `updateData` 原文與 spec 引的一致。DATA-12 新寫法的事實都站得住腳,剩下的是措辭與收尾問題。

### 1. DATA-12「先在外面算好」沒講例外,讀者照寫會弄丟更新
severity: minor
blocking: 否
引句:「官方允許 transform 做耗時工作,但同一個 DataStore 的寫入依序執行,transform 跑多久後面的寫入就等多久」
- 失敗場景:新寫法的建議是「能先算好的先在外面算好」,範例是 `val r = api.call(); dataStore.updateData { it.copy(x = r) }`。
- 這個範例安全,是因為 `r` 不依賴目前的值。
- 假設讀者原本寫 `updateData { cur -> cur.copy(token = api.refresh(cur.token)) }`。他為了不讓後面的寫入排隊,把它改成:
  - 先 `data.first()` 讀出目前的值。
  - 在外面呼叫 API。
  - 再 `updateData { it.copy(token = t) }`。
- 這樣原子的讀改寫就被拆開,兩個併發的更新會互相蓋掉。官方頁自己寫 `updateData` 是 atomic read-modify-write,`data` 的說明也寫 Do not layer a cache on top of this API。
- 舊列的「重試時副作用重複」被拿掉,新列的「後果」欄也沒補上這個取捨。
- 型錄的 DATA-12 列(`skills/kotlin-idioms/checks-catalog.md:543`)只在「能先算好的」這個前提裡暗示了界線。建議加一句:新值要靠目前的值算出來時,不要搬出去。
- 同樣的字眼也複製進 D-42 列(`skills/kotlin-idioms/checks-catalog.md:756`)。
- 這一列沒掛規則,靠表態對程式與盲判席,所以沒有機器把關能擋住這種誤改。

### 2. 兩種寫法推送前不再擋,但只承認了風險,沒寫回頭看的條件
severity: minor
blocking: 否
引句:「推送前不再擋這兩種寫法(見〈待人裁〉);其餘規則包等級沒動」
- 這一行承認消費專案會少擋兩種寫法,後面沒有帶回頭條件。
- 文末唯一的 `REVISIT:2026-12-07` 只看「還沒逐列查證」會不會變多,跟「什麼時候把三條規則搬回來」無關。
- 專案 CLAUDE.md 鐵則 4 要求,這種會過期的承認要附回頭條件。
- 代價是實際的:`kt-compose-test-node-by-index` 這類壞寫法,消費專案推送前不會再被擋。
- 建議補一行,例如「找到官方出處就搬回 `rules/`」,或寫成 `REVISIT:[when-file:...]`。

### 3. 範例與引用裡還有失效的 API-14 說法
severity: minor
blocking: 否
引句:「API-14、TEST-31 仍找不到,這一批不標出處不全」
- 快照這句交代 API-14 查不到官方出處,後來被標成出處不全並降為不接閘。
- 快照外查證:file: `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:199`。
  - 該行說這條帶 `{LINT_FILES}`、推送前的新增告警閘會真的跑,並用 `[API-14]` 當告警訊息開頭的範例。
  - `[API-14]` 現在是不接閘的規則,推送前不會出現這條告警,拿它當「閘會擋」的範例會誤導讀者。
- 另一個關聯點:D-2 列(file: `skills/kotlin-idioms/checks-catalog.md:716`)把 API-14 當「對應檢查」,並把「不要包 `async { }.await()`」當標準寫法。
  - 這一列的來源欄寫「同『對應檢查』各列的來源欄」,出處不全的標記不會傳到 D-2。決策表的讀者看不到這個建議其實是出處不全。
- 規則包自檢沒涵蓋這兩處,快照也沒列入收尾清單。建議把範例換成仍接閘的規則編號,並在 D-2 加註出處不全。

### 各節結論
- 〈待人裁〉的 API-14、TEST-31 部分:已讀,無 finding(只有上面第 2 點的回頭條件)。
- 條款 S2、S3 與預期值表:已讀,無 finding。測試名稱、綁定與預期值都對得上程式。
- 〈實務隱患〉裡的其他排除項:已讀,無 finding。

### 實務隱患逐類
- **金流與對外送出**:不碰,成立。
- **不可逆**:改的是型錄文件與規則目錄位置,退提交即回原狀,成立。
- **少擋什麼**:
  - 少擋的是 `async { … }.await()` 立刻等待、`onAllNodes(…)[n]`、`onNodeWithText("中文字面")` 三種寫法。
  - 這三種都只是品質問題,不是資安或崩潰,後果有限。
  - 實際風險只在第 2 點的回頭條件,而且是回頭機制不足,不是降級本身的決定。
- **DATA-12 讀者誤讀**:見第 1 點。
