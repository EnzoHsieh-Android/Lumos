severity: major

1. 做法第 5 點最後一項「CHANGELOG 寫一條」照字面做不了,會撞上版本單源守衛。
引句:「CHANGELOG 寫一條(回顧檔第 2 版、跑滿查方向)」
severity: major
blocking: 是——實作者照這句做,不是推送閘變紅,就是被迫替人決定要不要發版;spec 對這兩條路都沒交代。
- file: `CHANGELOG.md:3-8`。這份只記對外發版,標題固定為 `## vMAJOR.MINOR — YYYY-MM-DD`,而且明寫「不留常駐的未發布區塊」。
- file: `scripts/test_lumos.py:11451`。`t_version_single_source` 要求 `LUMOS_VERSION` 與 CHANGELOG 第一筆一致。
- file: `scripts/lumos:277`。目前版本常數是 v1.4。
- file: `RELEASING.md:14-19`。升版是人工的、不可逆的發版步驟。
- 加一條新標題而不升常數,守衛紅。把條目塞進 v1.4,等於改寫已發版的紀錄。升版要走 RELEASING.md,要人裁。
- 這次改動不動掛鉤或注入格式,本機安裝又是符號連結,v1.4 以來的升版理由(提示跑 `lumos update`)用不上。
- 相容二寫「CHANGELOG 寫明」,同樣沒交代。
- 要寫明這次不發版而只靠圖譜與手冊,或寫明發 v1.5 的人裁與 `LUMOS_VERSION` 一起改。

2. 同步點清單漏了 `docs/心智模型.md` 的到頂描述,也沒有寫為什麼不用改。
引句:「同步點逐處列(措辭各不同,不靠搜同一句):」
severity: minor
blocking: 否——那句仍然成立,只是做法第 5 點說「每一處都改成」,清單卻沒涵蓋它。
- file: `docs/心智模型.md:130`。流程圖邊標籤寫「沒過:再開一輪(最多 3 輪,到頂交給人裁)」。
- 我 grep「到頂」「跑滿」「cap-decision」「retro」,範圍是 `skills/`、`docs/`、`README*`。清單其餘各處都對得上實際行號:design-loop `reference.md:332,542`、code-loop `reference.md:245,620`、`05` 第 22、23、33 行、`06:134`、README 兩份、指令參考兩份。
- 只漏這一處。

3. 網址去重的鍵含 port,但規格只把 `urlsplit` 的 ValueError 算成該項的錯。
引句:「用 `urllib.parse.urlsplit` 解(解不開、丟 ValueError,算這一項的錯,不丟例外)」
severity: minor
blocking: 否——補一個 try 範圍就好,但字面實作會在 `--check` 丟堆疊,違反 S2「不丟例外」。
- 我用 Python 3.14 驗過:`urlsplit('http://a.com:abc/x')` 解得開,取 `.port` 才丟 ValueError;`:99999` 同樣。
- file: `scripts/lumos:10359-10362`。repo 既有的 `_secev_target_host` 把 `u.port` 放進同一個 try,spec 的 PRIOR-ART 說借用它的取法,卻沒寫這一點。
- 要寫明「取 port 的存取也算進同一個 try」,S2 補一個壞 port 的案例。
- 天花板一另外沒列兩個同頁寫法:`:443` 與不帶 port 算不同鍵、主機名結尾的點。

4. 跑滿提示新加的句子寫成無條件,但這一支也會在 converged 的迴圈印出來。
引句:「先上網查這條路的方向(至少兩個來源),結論附在請人裁的訊息裡」
severity: minor
blocking: 否——只是多餘工作與措辭,不會做錯事。
- file: `scripts/lumos:17659-17662`。`ask` 在 hint 不是 can-stop 時為真,這幾行會加上 `[cap-hint] 人裁:` 前綴。
- file: `scripts/lumos:22780-22782`。現有那句是有條件的「要破例再開一輪或接受剩下的風險,先記人裁」。
- file: `scripts/test_lumos.py:104840`。既有測試明說 converged 到上限也印這段。
- 代碼審多半折完就過(spec 名詞自己也這樣說)。新句無條件,會變成每次過關都被叫去上網查,前面還掛著「人裁:」的標籤。
- 把新句併進「要破例再開一輪…」那個條件子句裡。
- 「已有人裁」那一支對 accept-risk 也印「寫進 world_check」,和「不在 accept-risk 時強制」互相打架,要限定 extra-round。

5. S5 的措辭比做法第 3 點的三分法寬,而且「不論 version 是幾」與「version 收 1 或 2」矛盾。
引句:「人裁 ts 早於生效時間時,不論 version 是幾、world_check 填了什麼(含型別不對),應照舊過而且不寫 world_verdict」
severity: minor
blocking: 否——只影響測試怎麼寫;accept-risk 早於生效時間的情況實務上不會有 world_check。
- 做法第 3 點的「不管」只涵蓋 extra-round 且 ts 早於生效。accept-risk 不論 ts 都是「選填」,有填就驗。
- 照 S5 寫測試,拿 accept-risk 加舊 ts 加型別錯的 world_check,會預期通過,實作卻判錯。
- version 是 3 或 `"2"` 仍會被 `version 收 1 或 2` 擋掉,「不論 version 是幾」也講過頭了。
- file: `scripts/lumos:22418-22420`。現行 version 檢查。

6. 「照舊擋」的 version 型別檢查沒有任何既有或新增的測試守著。
引句:「既有的 int 型別判斷照留,`"2"`、`2.0`、`true` 照舊擋」
severity: minor
blocking: 否——把 `== 1` 改成 `in (1, 2)` 時,最容易弄丟的就是排除 bool 這一步,現在沒有任何一支測試會紅。
- 我查了 `scripts/test_lumos.py` 的回顧測試區,檔內 `version` 只出現在產生器(`:103446`)和骨架測試(`:103881`)。
- 沒有哪一支驗過 `"1"`、`1.0`、`true`。`True == 1`,漏掉 bool 排除就會放行 `true`。
- 做法第 7 點和 S2/S5 都沒補這組案例。

7. retro-stats 的「沒填」口徑沒定義,會混進不該算的迴圈。
引句:「印一段「世界查證結論(加開的迴圈):方向對 N、要換方向 M、判不準 K、沒填 L」」
severity: minor
blocking: 否——只是觀測數字,但 RETIRE-IF 與 REVISIT 要人工拿它判斷。
- file: `scripts/lumos:22998-23004`。`data` 只有 state 為 recorded 時才有。
- file: `scripts/lumos:22990`。none、stale、skipped、not_applicable、error 都沒有 `data`。
- 「只數最新人裁是 extra-round 的」之後,這些狀態和「不管」的舊迴圈(world_check 整段不讀)都落在「沒填」。
- 要寫明「沒填」只算已記回顧、需要世界查證卻沒填的,其餘另列或不算。
- 「不管」的迴圈不能直接讀未驗的 `world_check.verdict`,非字串會丟例外。

8. 第 7 點的既有測試讓 36 處產生器呼叫在生效日前完全不經過 world_check 的驗法,日期一到才一起露出問題。
引句:「產生器改成預設 version 2 並帶一份合格的 world_check」
severity: minor
blocking: 否——S2 到 S6 另外有明確 ts 的案例,產生器那份文件在「要求」路徑上是否真的合格,卻只能在生效日之後才被既有測試驗到。
- file: `scripts/test_lumos.py:103441-103454`。`_cr_decide` 用真實時間,生效常數是實作日隔天零點,在那之前所有案例都屬於「不管」。
- 到日期之後,這 36 支會同時從「不管」切換成「要求」。
- 補一個明確 ts 的案例,把產生器那份 world_check 走一次「要求」路徑。

9. 回頭條件用「方向:」當機械線索,這個詞太常見。
引句:「主觸發有沒有在 intake 的〈先查世界〉留下「方向:」那一行」
severity: minor
blocking: 否——只影響之後的人工統計準不準。
- `PRIOR-ART:` 有獨特前綴,「方向:」沒有。intake 散文裡本來就會出現「方向:」這種寫法。
- 2027-02-04 與 2026-12-15 那兩行 REVISIT 靠 grep 判斷,會有假命中。
- 手冊那行改成 `方向:對|要換|判不準 — …` 的整串固定前綴(或另取獨特記號),REVISIT 就拿它當檢索詞。

10. 起因段指的計劃與迴圈,這個 repo 找不到,接手的人查不到證據。
引句:「起因:風險高測試證據加嚴那份計劃的設計審,第一、二輪各自在紙上換了一次機制形狀」
severity: minor
blocking: 否——不影響設計成立,只影響可核對性。
- `docs/lumos-toolchain-knowledge/Projects/` 沒有這份計劃。
- 它在 `/Users/enzo/harness/lumos-highrisk-evidence`(分支 `highrisk-test-evidence`),名稱是「高風險測試證據加嚴_計劃」,與 spec 的用詞順序不同。
- spec 沒寫迴圈編號或卷證路徑,三個月後那條分支若還沒合併,這段起因無從核對。
- 補上計劃節點與卷證路徑,或寫明那條分支合併前這段無法在本 repo 核對。

### 逐項核對與實務隱患

- **上一版問題**:r2 的 G1 到 G10 在正文都有落實。三種情況的分法、統計讀已驗內容、不新增狀態、測試直接寫帶 ts 的事件、d1 與白話段一致、手冊同步點逐處列,現行程式與手冊的引用行都對得上。
- **第 0 點接口**:design-loop `SKILL.md:41` 與 code-loop `SKILL.md:50` 的原句都存在,接在整句保留的後面可行。code-loop 的第 4 步在 `SKILL.md:45`,第 5 步的〈先查世界〉在 `:50`,步驟編號與 spec 一致。
- **第 6 點寫回**:`Systems/每輪修補差異派工.md` 的 `[不選]` 在第 20 行,REVISIT 2026-12-15 在第 21 行,都在。`Projects/審查跑滿回顧_計劃.md` 的第 98 行與第 134 行也對得上。`Systems/loop-convergence-recording` 確實是 `[cap-hint]` 的家(第 34、35、37 行)。
- **釘既有字面的測試**:`t_cap_retro_next_hint_scope_only`(`:104263`)與 `_cr_ask_count`(只數 `lumos loop cap-decision`)不受新句影響,「範圍外反向斷言照綠」成立。`_CR_MANUALS` 只要求出現 `--template --write` 和「多席帶輪次」,新句不碰這兩個。需要改的只有 `:103446` 和 `:103881`,spec 都有列。
- **併發**:沒有新的共享狀態。帳是追加寫入,事件讀取不嚴格比對欄位,舊工具讀到多出的 `world_verdict` 會忽略。
- **效能與資源**:回顧檔已有 256KB 上限(`scripts/lumos:22123`),網址去重用集合,狀態判定對每個迴圈多解幾個網址,量級可忽略。
- **回滾**:回退段沒提到 retro-stats 新增的世界查證統計段,要補。

最嚴重等級:major,blocking 1 條(第 1 條)。
