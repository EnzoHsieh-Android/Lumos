severity: blocker

1. `.port` 非法會丟例外,spec 的 try 範圍只框住 `urlsplit`,沒框住 `.port`。上一版 G5 只修了一半。
引句:「解不開、丟 ValueError,算這一項的錯,不丟例外」
severity: blocker
blocking: 是,照字面實作會讓 S2 的「不丟例外」落空,而且崩的是所有 `_cap_retro_status` 的呼叫端。
- `urlsplit` 對 `http://a.com:99999/`、`http://a.com:abc/`、`http://[::1]:x/` 都解得開、不丟例外。丟 `ValueError` 的是取 `u.port` 那一步。
- spec 的比對鍵含 `port`。照寫實作時,`u.port` 多半落在 try 外面。我用同樣的鍵函式實測,這三個網址都崩 `ValueError`(Port out of range / could not be cast to integer)。
- `_cap_retro_check` 每次讀回顧狀態都重跑(doctor、canary record、loop next、retro-stats 都經過 `_cap_retro_status`)。所以一個壞埠號會讓這幾個指令都崩,不只 `--check`。
- repo 既有的主機名取法已經在 try 內讀 `_port = u.port`,spec 說要借它,卻只抄了 `urlsplit` 的 ValueError。
- file: `scripts/lumos:10360-10363`(`urlsplit` 與 `u.port` 同在一個 try)、`scripts/lumos:22573`(狀態重驗的呼叫點)
- 修法:規則改寫成「`urlsplit`、讀 `port`、`hostname` 都在同一個 try,任一丟 ValueError 就算這一項的錯」。S2 的測試加 port 99999、`abc`、`:80:80` 三種。

2. 「不管」這一類在 `retro-stats` 與 `--record` 的銜接沒寫。r2 的 G1 只在 `--check` 這側修好。
引句:「world_check 整段不讀、不驗、不寫帳,不論 version 是幾、裡面填了什麼」
severity: major
blocking: 否,不會讓 S5 的檢查結果出錯,但這條規則在統計和記帳兩端沒有落實。
- `_cap_retro_check` 只回 `(probs, data)`,`data` 是整份 JSON 原樣(`scripts/lumos:22506`)。`_cap_retro_status` 把它原樣放進 `res["data"]`(`scripts/lumos:22573`)。
- spec 規定 `retro-stats` 讀這份「已驗內容」,並數「最新人裁是 extra-round 的」迴圈。生效前的舊 extra-round 迴圈屬於「不管」,world_check 沒驗過,卻會被數進去。
- 兩種後果:要嘛把舊迴圈全算進「沒填 L」,灌水;要嘛讀到沒驗過的 `world_check`。後者在內容是 `5`、`verdict` 不是字串時,`.strip()` 會讓 `retro-stats` 崩。
- `--record` 也得知道這次是哪一類才能決定帶不帶 `world_verdict`,但 `_cap_retro_check` 沒回這個訊息。實作者只能在記帳處把三分法重寫一次,這正是 G1 想消掉的雙份判斷。
- 修法:讓 `_cap_retro_check` 回第三個值(`required`、`optional`、`ignored`),stats 與記帳都只讀它;並寫明 `retro-stats` 是排除「不管」的迴圈,還是把它們算進「沒填」。

3. 比對鍵的邊界沒講清楚,「路徑全是斜線」會因實作而分歧。
引句:「去掉結尾斜線的 path」
severity: minor
blocking: 否,影響的是重複判定的一致性,不影響放行與否。
- `rstrip('/')` 會讓 `http://a.com//`、`/`、空路徑三者同鍵,也會讓 `/x//` 與 `/x` 同鍵。「只去一個」的寫法(`[:-1]`)則讓 `//` 變成 `/`,與空路徑不同鍵。spec 兩種都能讀出來。
- 我實測了 `rstrip('/')` 的結果:`//` 和 `/` 都得到空字串。
- 修法:寫死是「去掉全部結尾斜線」,並在 S2 補 `http://a.com`、`http://a.com/`、`http://a.com//` 三者判重複的案例。

4. 天花板一列得不全,幾個便宜的湊兩來源寫法沒列。
引句:「鍵相同算重複(不管 `#` 之後、帳密;`www.` 與不帶 `www.`、追蹤參數不同算不同來源——天花板一)」
severity: minor
blocking: 否,這份 spec 本來就不防刻意偽造(信任原則),只是天花板該寫全。
以下各組在鍵上都不同,實測確認:
- 預設埠:`http://a.com:80/x` 的 port 是 80,`http://a.com/x` 是 None。
- 主機尾點:`a.com.` 與 `a.com`。
- `http` 與 `https` 同頁,因為鍵含 scheme。
- 百分比編碼大小寫:`%2F` 與 `%2f`。
- IPv6 寫法:`::1` 與 `0::1`。
- 全形主機名。
- 查詢參數順序。
修法是把這些補進天花板一的列舉,不必機械擋。

5. `hostname` 只要求非空,比既有取法鬆。
引句:「scheme 不分大小寫是 http 或 https,`hostname` 不是空的」
severity: minor
blocking: 否,格式檢查本來就不保證真的查過。
- `http://exa mple.com/`(含空白)、`http://%41.com/`、`http://./`、含 NUL 的主機名,`hostname` 都非空,會過。
- 既有 `_secev_target_host` 在 netloc 含 `\`、`%`、空白時一律判不出來(`scripts/lumos:10364`)。spec 說借它的主機名取法,卻沒借這一道。
- 補充:`urlsplit` 會悄悄吃掉網址中間的 tab 和換行,所以 `ex\tample.com` 與 `example.com` 同鍵。這是無害的,但值得寫進說明。
- 修法:沿用同一條 netloc 字元檢查,或把「主機名不含空白、`%`、`\`」寫進規則。

6. 空骨架和 null 的邊界沒窮舉,實作者容易用真值判斷放過錯誤型別。
引句:「`world_check` 省略、`null`、`{}`、或空骨架(每格去空白後都是空字串、清單可以是空的)都算沒填、照過」
severity: minor
blocking: 否,spec 另有「不是物件算型別錯」一句,但 S4 沒把反例列進去。
- 實作若寫 `if not wc: return`,`[]`、`""`、`false`、`0` 會被當沒填而過。spec 要的是型別錯。
- 空骨架的「每格」沒說明:格子缺鍵或是 `null` 算不算空?`{"foo":1}` 算空還是填一半?
- 沒說的組合:accept-risk、version 1、而且 world_check 填了完整內容,要驗嗎?會寫 `world_verdict` 嗎?
- 修法:S4 補 `[]`、`""`、`false`、`0` 為判不過,以及 `{"queries":[], "sources":[], "verdict":null, "note":""}` 的歸類。

7. 生效常數與 `ts` 的邊界,測試沒釘住。
引句:「不早於生效常數 `_CAP_WORLD_CHECK_SINCE`(帶時區的完整時間戳」
severity: minor
blocking: 否,判斷的主幹(`ts` 解不開就算要求)是對的,而且偏嚴。
- `_loop_ts_key` 對沒帶時區的字串回 `None`。如果常數寫成沒時區的 `2026-11-05T00:00:00`,`None` 對數字做比較會丟 `TypeError`,或被實作者包成靜默全部「要求」。
- 既有做法在 `scripts/lumos:3517` 與 `scripts/lumos:14999` 直接拿常數呼叫 `_loop_ts_key`,同樣沒有自檢。
- S5 只測「早於」和「不早於」,沒測 `ts` 正好等於常數的那一刻。也沒測同一時刻但不同時區的寫法(`+08:00` 與 `Z`)。
- 我實測過幾個 `ts` 字串:`2026-11-05` 與沒帶時區的時間戳回 `None`(算要求,偏嚴);空字串和尾端有換行的字串會讓 `fromisoformat` 丟 `ValueError`,被 `_loop_ts_key` 吃掉回 `None`。這些都是 fail-closed,沒問題。
- 修法:加一支斷言常數可解析的測試,並在 S5 補等於常數與跨時區同一時刻兩例。

實務隱患逐類(已實測的沒有新 finding)

- **效能與資源**:`urlsplit` 對 5MB 的單一網址只要約 8 ms。我試了長路徑、括號、`@`、冒號、斜線這幾種病態輸入。回顧檔有 256KB 上限(`scripts/lumos:22123`),sources 數量因此有界。最壞是幾千條壞網址各印一行錯誤,這跟既有 `families` 一樣,沒有新增問題。
- **併發**:「最新一筆人裁」是治理帳的檔內順序。`--check` 和 `--record` 在同一次呼叫裡用同一份位元組與同一個 `dec`,沒有新的競態。兩次呼叫之間有人追加 cap-decision,屬既有行為。
- **回滾**:spec 的回退保留「version 收 1 或 2」,留在帳上的 `world_verdict` 欄沒有讀取端會被它弄壞。沒發現問題。

總結:最嚴重等級 blocker,blocking 1 條。
