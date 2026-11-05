severity: blocker

我讀完整份 spec,並對照 `scripts/lumos`、`checks-catalog.md`、`棧別提問表態閘.md`、`.github/workflows/ci.yml` 與第一批計劃查證。16 處前掃已修的我沒重報。共 13 條 finding:1 條 blocker、8 條 major、4 條 minor。其中 `kotlin規則包` 那個落點是 lands_in 新開節點,不算壞引用。

### finding 1(範圍 4「推送前核對」)
severity: blocker
blocking: 是。作者與盲判逐題比對的規則,在多列同時命中時沒有任何一種誠實答案能過,閘會卡死。

引句:「或作者 na 而盲判 row 為 none → 一致;其他都是不一致」

- **問題:**
  - 觸發字高度重疊。D-1、D-2、D-8、D-9 都收 `async`,D-1、D-2 也都收 `await`、`suspend`。
  - 一段 `val a = async{…}; val b = async{…}; Ui(a.await(), b.await())` 會同時讓 D-1、D-2、D-8、D-9 適用。
  - 誠實的作者答案是 `kt-sit-D-1` satisfied、`kt-sit-D-2` na。
  - 盲判是逐題出 `row`,候選列是全部命中列。對 `kt-sit-D-2` 這一題,盲判會答 `row: D-1`。
  - 作者是 na 而盲判不是 none,依這條規則判為不一致。
  - 再派仲裁,仲裁同樣答 D-1,「仲裁跟第一盲判一致」,結果擋。
  - 作者要過只剩兩條路:把 D-2 的 na 說謊成 satisfied,但證據樣式對不上,過不了;或改成自填 tension。
  - 即「同一段程式對應 N 個適用題」這個常態,比對單位(逐題的 `row`)與作者答案的語意(這題是不是這列)對不上。
- **佐證:**
  - `docs/lumos-toolchain-knowledge/Projects/Android寫法語意情境表態與盲判_計劃.md` 的「候選列」定義(命中觸發字的所有列,不只題目自己那一列)。
  - file: `skills/kotlin-idioms/checks-catalog.md:668` D-1 觸發字含 async、await、suspend。
  - file: `skills/kotlin-idioms/checks-catalog.md:669` D-2 觸發字同樣含 async、await、suspend。
  - file: `skills/kotlin-idioms/checks-catalog.md:675` D-8 觸發字含 async、await。
  - S4 的測試案例只列單題單列,沒有多列共現。

### finding 2(範圍 2、用詞「並標 `android_only`」)
severity: major
blocking: 是。server 端 Kotlin 改動會被問 Android 情境題,打破表態閘「改後端的檔不會被問 Android」的既有承諾。

引句:「在四處各接一次:適用性判定(`_stack_applicability`)、表態樣板(`_dispositions_template`)」

- **問題:**
  - `android_only` 的排除是 `_stack_platform_excluded` 從靜態 `_STACK_QUESTION_SPECS["kt"]` 撈出 `android_only` 題號,算出 `exclude` 再傳進 `_stack_applicability`。
  - 情境題放在另一張延遲讀入的表,不在 `_STACK_QUESTION_SPECS` 裡,所以它們永遠不會進 `exclude`。
  - 這個函式不在 spec 列的四處接點裡。
  - 排除面也沒說清:`_stack_applicability` 的情境分支要不要讀 `exclude`、`--carry` 要不要處理。
- **佐證:**
  - file: `scripts/lumos:37841` 到 `scripts/lumos:37848`,`_stack_platform_excluded` 只讀 `_STACK_QUESTION_SPECS.get("kt", [])`。
  - file: `scripts/lumos:61877` 把 `exclude` 傳進 `_stack_applicability`。
  - file: `scripts/lumos:38177` 是 `_stack_applicability` 簽名。
  - 表態閘筆記 KEY:`2026-09-12` 的「改後端的檔不會被問 Android」承諾。

### finding 3(範圍 4「治理帳一筆 `blind-judge` 事件」、範圍 6 統計)
severity: major
blocking: 是。S7 的統計與任何靠治理帳重建的讀取,都拿不到 `blind-judge` 事件的內容。

引句:「治理帳一筆 `blind-judge` 事件加標記檔,同表態的讀寫慣例」

- **問題:**
  - 治理帳讀入是白名單欄位對映。`_gov_row` 只保留既有幾個欄位,`dispositions` 這個欄位還限定 `kind == "dispositions"` 才帶。
  - 盲判的結果、材料 sha256、`arbiter` 旗標若不加進去,到 `_render_gov_stats` 時全部消失,S7 的 kappa、仲裁採作者與採盲判次數不可能算出來。
  - 去重鍵 `token` 只有 `dispositions`、`recall-miss` 用 `written_at`。
  - 同一個 commit 的第一盲判、仲裁、分批的多筆 `blind-judge` 會折成一筆,仲裁記錄因此不見。
  - 這些位置 spec 一個都沒列,只說「同表態的讀寫慣例」。
  - 該段註解明寫「新增 mapper 用到的欄位時一起補進來」。
- **佐證:**
  - file: `scripts/lumos:16925` 附近的 `_GOV_FIELD_TYPES` 註解。
  - file: `scripts/lumos:17001` 到 `scripts/lumos:17016`,`_gov_row` 與 `token` 欄。

### finding 4(用詞「常用字當觸發字」、實務隱患「常用字當觸發字」)
severity: major
blocking: 是。spec 把成本爆炸的防線押在一個不存在的檢查上,而型錄現況已經收了常用字。

引句:「停用字表與檢查由第一批的型錄格式檢查承接」

- **問題:**
  - 第一批計劃全文沒有停用字表。「停用」只出現兩次,都是 Tricorder 的「壓不下就停用」,與觸發字無關。
  - S3 對觸發字只驗「有列編號與觸發字」。
  - 型錄現況的觸發字已含 `map`、`forEach`、`launch`、`try`、`catch`、`first`、`take`、`collect`、`suspend`、`delay`、`cancel`、`remember`、`Flow`、`flow`。
  - 任何一次 `.kt` 改動幾乎必中某幾列。
  - 於是每個 Android 推送都要跑盲判,而且作者每次要答十來個情境題。
  - 實務隱患那一條寫「本案依賴那一道」,依賴落空。
- **佐證:**
  - file: `docs/lumos-toolchain-knowledge/Projects/Android協程與API寫法機械檢查標準_計劃.md:105` 的 S3 全文。
  - file: `skills/kotlin-idioms/checks-catalog.md:668` 到 `skills/kotlin-idioms/checks-catalog.md:687` 的觸發字欄。
  - D-3 同時含 `map`、`forEach`,D-4 含 `cancel`、`Job`。

### finding 5(用詞「證據樣式」、實務隱患「證據樣式太嚴誤擋」)
severity: major
blocking: 是。有些列的標準寫法是「不寫某物」,正向正規式無法表達,spec 對這些列沒有出路。

引句:「每列至少兩條正規式,窗前後 3 行」

- **問題:**
  - D-2 標準寫法是「直接循序呼叫……不要包 `async { }.await()`」,D-20 的 alt 是「不切換,也不要在呼叫端多包一層」,D-14 的 alt 是「不需要共享卻共享 → 用畫面自己的 `viewModels()`」。
  - 它們的正確形態沒有字面特徵,「必出現的字面特徵」寫不出來。
  - 作者回報 satisfied 又沒有可核對的樣式,於是只能 na,又掉進 finding 1 的不一致。
  - 證據樣式的欄內語法也沒定義:
    - 多條之間用 ` ; `,與 Kotlin 常見的分號和 regex 的 `|` 衝突。
    - 多條是 AND 還是 OR 不明。S2 的敘述「窗裡要有一條符合」讀成 OR,範例卻是「async 加 await」成對。
    - 大小寫旗標、跳脫沒說。
  - 以 OR 讀,S2 窗內只有 `async {` 沒有任何 await 也會放行 D-1 main。
  - 型錄格式檢查(第一批 S3)沒有驗這一欄。
- **佐證:**
  - file: `skills/kotlin-idioms/checks-catalog.md:669` D-2 列。
  - file: `skills/kotlin-idioms/checks-catalog.md:687` D-20 列。
  - 現行型錄尚無「證據樣式」欄。

### finding 6(範圍 4、S4)
severity: major
blocking: 是。仲裁的「一致」比的是整組 `(row, followed)` 還是只比 `row`,兩種讀法放行結果相反。

引句:「仲裁跟第一盲判一致或三方都不同 → 擋,訊息印各方的 row 與理由」

- **問題:**
  - 「仲裁跟作者一致」、「跟第一盲判一致」沒有定義比對欄。
  - 只比 `row` 時,第一盲判答 D-1 但 `followed:false`、仲裁答 D-1 且 `followed:false`,對作者是「row 相同」,會被放行。
  - 兩個獨立盲判都說沒照做,作者卻過了。
  - S4 案例「仲裁判 D-1 應放行」也只寫 row。
  - 也沒有定義作者 na、第一盲判 D-1 `followed:false`、仲裁 none 這類組合。

### finding 7(範圍 4「盲判記錄與核對」)
severity: major
blocking: 是。記錄的儲存、數量與 sha 綁定都沒定義,多筆記錄(第一盲判、仲裁、分批)無處放。

引句:「推送前把這一版所有盲判記錄的題目取聯集」

- **問題:**
  - 表態的 marker 是每分支單一 JSON,寫入時整份原子覆蓋;治理帳回退讀「該分支最後一筆事件」。
  - 盲判卻要同一版本存在第一盲判、`--arbiter`、多批,需要「全部記錄的聯集」。
  - 照表態慣例,仲裁會覆蓋第一盲判,後到的一批會蓋掉先前一批。
  - 指令 `blind-judge <盲判結果.json> [--arbiter]` 沒有告訴工具這份結果對應哪一批、哪個 sha256。
  - 結果每題 `{id,row,followed,evidence,reason}` 也沒有 sha 欄。
  - 若寫入時重算 sha,綁定等於沒綁,不能證明盲判席看的是那份材料。
  - 範圍 5「一題一份材料」與這裡「每批各自的 sha256」單位互相衝突。
- **佐證:**
  - file: `scripts/lumos:70162` 到 `scripts/lumos:70185`,`_codeloop_write_dispositions` 單檔覆蓋。
  - file: `scripts/lumos:70195` 到 `scripts/lumos:70210`,`_codeloop_read_dispositions` 取最後一筆。

### finding 8(範圍 1 讀表、實務隱患「型錄格式壞掉」)
severity: major
blocking: 是。CI 這個「獨立信任根」對情境題會整個失效。⚠ 消費專案 CI 是否有型錄副本未實地驗證。

引句:「讀不到或格式壞 → 情境題整組不出題、印一行提醒,不擋、不記帳」

- **問題:**
  - 型錄在 lumos-toolchain 的 `skills/` 底下,spec 規定「從自己的安裝位置讀這張表」。
  - CI 工作流用的是 repo 內的 `scripts/lumos`。消費專案的 runner 上沒有裝使用者層 skills 時,CI 讀不到型錄,情境題整組不出題。
  - 本機 pre-push 讀得到而擋人,CI 讀不到而放行。
  - 「讀不到→不擋」把原本設計成不能被繞過的後盾,對這一組題變成 fail-open。
  - 盲判材料含候選列三欄,所以本機與 CI 的型錄版本只要差一字,`sha256` 就對不上。
  - D-n 編號沒有穩定性規則(插列、刪列、改號)。題號變了,`--carry`、八週統計與歷史帳都斷。
  - spec 對這些都沒有交代。
- **佐證:**
  - file: `.github/workflows/ci.yml:1` 到 `.github/workflows/ci.yml:3`,獨立信任根說明。
  - file: `.github/workflows/ci.yml:42`,CI 跑 `python scripts/lumos code-loop check`。
  - file: `scripts/lumos:34419` 附近,安裝位置判別沿用 `skills/lumos-project-notes/SKILL.md`。

### finding 9(用詞「盲判」、範圍 4 `--template`)
severity: major
blocking: 是。盲判材料「程式段」要怎麼從現有適用性結果算出來,spec 沒有定義,現有程式也給不出。

引句:「拿工具產生的材料(這次改動裡觸發情境題的程式段、前後文、候選列」

- **問題:**
  - `_stack_applicability` 收的是「棧 → 增刪行文字」,同一棧所有改動檔的行混在一起,不帶檔名與行號。
  - 要產生材料,得另外反查觸發行在哪個檔哪一段,還要決定前後文行數、超長函式怎麼截。
  - 適用性還含「刪行」。一次純刪除 `async` 的改動會讓 D-1 適用,但沒有被推版本的程式段可供盲判,作者也找不到可引的證據。
  - 這種案例該 na 還是怎樣,spec 沒寫。
  - 8 萬字分批的切分單位(依題?依檔?)也沒定義,而 sha 與涵蓋檢查都綁在批上。
- **佐證:**
  - file: `scripts/lumos:38177` 的簽名與 `scripts/lumos:61861` 到 `scripts/lumos:61877` 的呼叫端。
  - file: `scripts/lumos:61157`,`_tension_candidates_into` 也直接讀 `_STACK_TRIGGERS`,情境題不在內,與範圍 2 的接點清單不一致。

### finding 10(範圍 3「表態對程式」)
severity: minor
blocking: 否。證據行不必落在這次改動內,機械這一道有繞法,但盲判看的是實際改動,仍會抓到。

引句:「`evidence` 照既有規則寫單一個 `path:line`」

- **問題:**
  - 讀窗只對被推版本的那一行,沒要求那一行屬於這次改動的增行。
  - 作者可以指向 repo 裡原本就存在的任一行 `async {` 過機械這一道,「完全沒參考」的擔憂原封不動留在機械側。
  - 要抓得靠盲判補位。

### finding 11(範圍 4 出口)
severity: minor
blocking: 否。逃生口本身是既有機制,但這份設計的目標正是防敷衍。

引句:「或作者把那題改表態成既有的 tension」

- **問題:**
  - tension 不跟盲判比、不查樣式。
  - 作者碰到任何不一致,補三個欄位就能放行,盲判核對的實質約束力因此打折。
  - 唯一牽制是 RETIRE-IF ② 的事後計數,沒有任何當場擋。

### finding 12(RETIRE-IF ①、範圍 6)
severity: minor
blocking: 否。回頭條件的量測單位與統計輸出對不上。

引句:「①某一列情境題的盲判與作者一致度 kappa ≥ 0.9 且命中 ≥ 20 次」

- **問題:**
  - 範圍 6 的 kappa 是「類別=row 加 none」的單一多類別值,算不出「某一列」的 kappa。
  - 另外,第一批計劃的批三條件寫「以 light 等級拉進代碼審查迴圈、固定多一席盲判席」。
  - 本計劃改成「分級不動」加提示加推送擋,與它的承諾不一致。第一批要同步改寫。
- **佐證:**
  - file: `docs/lumos-toolchain-knowledge/Projects/Android協程與API寫法機械檢查標準_計劃.md:79`。

### finding 13(範圍 4「記錄綁目標版本與材料 sha256」)
severity: minor
blocking: 否。成本與可用性問題,不是正確性。

引句:「記錄綁目標版本與材料 sha256」

- **問題:**
  - 盲判記錄沒有 `--carry` 的對應。
  - 專案常規是推前 rebase,rebase 後 head sha 變了、材料沒變,記錄也要整批重派。
  - 每次要再花一輪模型成本。
  - 表態有 `--carry`,盲判沒有。

### 實務隱患鏡頭
- **併發:** 同分支的 marker 單檔覆蓋,多會談同時跑盲判會互蓋(finding 7)。
- **效能與記憶體:**
  - 材料 8 萬字分批已有處理。
  - 觸發字過寬造成的題目數與盲判成本在 finding 4。
  - 反查觸發行位置的成本沒有量測。
- **安全:**
  - 盲判材料只含改動程式段,沒有新增執行命令的地方,無新增風險。
  - 派工詞夾帶答案的問題,spec 已依威脅模型明確排除。
- **回退與資料遷移:** 回退段合理;治理帳讀側略過未知種類,我在 `_gov_row` 看到的是白名單,與「略過」一致。已讀,無額外 finding。
- **金流、不可逆、對外送出:** 無,理由同 spec 的「已排除」三條。

最嚴重 severity:blocker;blocking 共 9 條(1 條 blocker、8 條 major)。
