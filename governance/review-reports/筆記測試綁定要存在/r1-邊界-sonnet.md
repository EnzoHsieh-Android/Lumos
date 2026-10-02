severity: major

# 設計審第 1 輪:邊界-sonnet 席(邊界與輸入)

實驗都在 `scratchpad/tb-r1-work-邊界-sonnet/` 下的 clone 與臨時專案跑,腳本是 exp1~exp10.py(用 importlib 載入 `scripts/lumos`,直接呼叫 `_classify_test_refs`、`_strip_inline_markup`、`_visible_lines`、`slot_parse`、`slot_check`、`_pin_commit`、`_notelines_regions`、`_platform_test_index`)。

## F1 「什麼算一個測試引用」在抽取與格子兩邊不一致,四種寫法能同時過格子又躲過存在檢查
severity: major
blocking: 是
引句:「筆記任一行裡 `[test:名稱]` 的名稱(同一個方括號可用逗號列多支」
file: `scripts/lumos:4736`(TEST_REF_RE 只認小寫半形 `[test:`、名稱至少一個非 `]` 字元)
file: `scripts/lumos:3757`(_SLOT_KEY_RE 與 _SLOT_CANON:鍵名不分大小寫、冒號收全形;格子認的比抽取多)
1. 抽取沿用 `TEST_REF_RE`(做法 1 說對一行先 `_strip_inline_markup` 再抽,規格沒另寫抽取式)時,四種寫法抽不到名稱:`[test：t_nonexist_zz]`(全形冒號)、`[Test:t_nonexist_zz]`(大小寫)、`[test:,]`(逗號連空項)、`[test:`t_nonexist_zz`]`(名稱外包反引號:剝反引號後剩 `[test:]`,正則要求至少一字)。
2. 同樣四種寫法,格子 `slot_parse` 都認成 test 欄位,`slot_check` 不報。實測(exp6/exp7):
   - `坑 [出處:x] [根因:y] [test：t_nonexist_zz]` → `slot_check('PITFALL', …)` 回 `[]`,`TEST_REF_RE.findall` 回 `[]`
   - `坑 [出處:x] [根因:y] [Test:t_nonexist_zz]` → 同上
   - `坑 [出處:x] [根因:y] [test:,]` → `slot_check` 回 `[]`,`_classify_test_refs('[test:,]')` 回 `[]`
   - `PITFALL: 坑 [出處:x] [根因:y] [test:`t_nonexist_zz`]` → 剝完是 `[test:]`,抽取 `[]`,格子的 test 值是 `` `t_nonexist_zz` ``(非空)而滿足三選一
3. 結果:PITFALL 的「三選一」靠 `[test:,]` 之類就滿足,而新規則看到的名稱集合是空,不擋。規則要擋的正是「寫了 `[test:]` 卻指不到」,這幾個寫法讓兩道閘互相認為對方有查。四選一加上 `[test-gone:]` 後同理:`[Test-Gone:x@…]`、全形冒號版格子認、本案的提交驗證抽不到。
4. 同一行 `[test:`a`,t_nonexist_zz]` 剝完是 `[test:,t_nonexist_zz]`,抽出 `,t_nonexist_zz` 一支(第一個名稱靜默消失)。
5. 規格沒有規定抽取式、也沒有規定「抽不到但格子認得」該怎麼辦(例如直接用 `slot_parse` 的結果當唯一來源,或抽取式改成同一組寬鬆規則並對空項報違規)。照字面實作會做出上述漏洞。本 repo 現有 `[test:` 加反引號的寫法有 3 處(grep 實測),表示作者真的會這樣寫。

## F2 單行寫法的摘要(`summary: "…"`)被判成「其他」區,整段不查
severity: major
blocking: 是
引句:「新寫的行用筆記內容閘既有的抽取(提交時 `_notelines_new`、推送時 `_notelines_range_added`)」
file: `scripts/lumos:27152`(_notelines_regions:頂層鍵那一行一律標 other,第 27171 行附近)
file: `scripts/lumos:27344`(_notelines_new 預設 keep_other=False,「其他」區的行不收)
1. 實測 exp2:開頭欄位寫 `summary: "PITFALL:單行寫法 [test:t_nonexist_zz]"`,`_notelines_regions` 回的區塊是 `other`;只有 `summary: |` 之後的縮排行才是 `summary`。
2. 規格說新寫的行「用既有抽取」,既有抽取預設不收 other 區。所以單行寫法的摘要裡任何 `[test:壞名]` 都不會被查,而 `extract_contracts` 與 Check T 對這種寫法是照 `\n` 切行讀得到的(讀的人以為有查)。
3. 規格沒有要求 `keep_other=True`,也沒有說明這是被接受的缺口(只說「合約行與條款定義行」不查)。補救需要明寫:用 `keep_other` 並限定 summary 單行、或在單行寫法出現時只提醒。

## F3 判定單位是實體行,而摘要、格子與作廢標記是邏輯行(續行會讓 `[test:` 沒閉合、1c 對不上)
severity: major
blocking: 是
引句:「(1c)新寫的作廢行掛著活測試 → 違規:改成 `[test-gone:]`,或把綁定移到接手的那一行」
file: `scripts/lumos:28148`(_ns_summary_logical:格子規則已把縮排更深的續行接回整條;本案沒提)
file: `scripts/lumos:28189`(_ns_superseded 對傳入的字串判)
1. `_notelines_rows` 回的是實體行。摘要裡長行折成續行很常見(格子規則專門寫了續行接回、`_ns_old_keys` 也分 logical 與 physical)。實測 exp2:`PITFALL: c [test:t_a,` 換行 `     t_b]`,第一個實體行的 `[test:` 沒閉合,正則抽不到;第二行沒有 `[test:`,也抽不到。整條逃過。
2. 1c:`RULE: …(第一個實體行,含 [test:t_live])` 與 `[status:superseded] [被取代:…]`(續行)分在兩個實體行,`_ns_superseded(第一行)` 回 False;續行本身沒有活測試。1c 對這種寫法永遠不觸發;反過來,只改續行(補上 `[status:superseded]`)時,「活測試」在沒被選進來的另一行。
3. 重排版造成的誤擋:舊的折行版本當年抽不到名稱,所以「起點版本的名稱多重集合」是空的;有人把它重排成單行,名稱第一次被抽到,舊的懸空名全成「新加的」而被擋(違反 S2 的本意)。
4. 規格應規定判定單位是接回續行後的整條(沿用 `_ns_summary_logical`),起點版本也用同一單位;現在字面寫「每一行」。

## F4 整行交給 `_classify_test_refs` 的粒度跟「新加的名稱」不同,一個壞前綴會遮住同行其他名稱、還擋到舊名
severity: major
blocking: 是
引句:「每一行(去反引號後的整段)交給 `_classify_test_refs`。平台前綴沒定義時它整段只回一筆,訊息照印它的錯誤字串。」
file: `scripts/lumos:40248`(_classify_test_refs:resolve_test_refs 丟 ValueError 就整段回一筆 `(node, "?", 錯誤字串前 60 字, "bad-name")`)
1. 實測 exp10(多平台設定 py 與 web):
   - `[test:PY:old_name,py:test_new_zz]` → 只回一筆 `('n','?',"[test:PY:old_name] 的平台前綴 'PY' 未定義…",'bad-name')`
   - `[test:py:a,PY:b,py:c]` → 一筆 `'?'`,a 與 c 都沒判
2. 規格的違規單位是「新加的名稱」(S2:舊名不擋)。那一筆沒有名稱可以對照多重集合:若當違規印,舊行原本就有的壞前綴名(舊的 12 處文件範例就是這種)在只改同行其他字時被擋,違反 S2;若當成不屬於新加而略過,同行新加的 `py:test_new_zz`(懸空)被遮住,不擋。兩條路都錯。
3. 規格要改成逐個名稱各自呼叫(或逐個名稱先 resolve),而且每筆結果要帶回名稱字串好去對多重集合;訊息 `[:60]` 截斷在前綴說明裡也截掉了名稱。

## F5 沒有平台/測試設定的專案,預設被當 C# 專案,所有新名稱都會被判指不到
severity: major
blocking: 是
引句:「索引建不起來(設定壞丟例外)→ 這組規則這次跳過、印一行原因」
file: `scripts/lumos:5111`(load_platforms legacy 分支:沒有 `platforms` 時用 `test_profile`,沒有就退 `csharp-xunit`,root=repo_root)
1. 規格只處理「索引丟例外」。實測 exp3(臨時專案,有 `test_a.py` 與 `def test_real_one()`):
   - 沒有 `.lumos/config.json`:`_platform_test_index` 不丟例外,default 是 `csharp-xunit`;`[test:test_real_one]` → `fake`,`[test:test_none]` → `dangling`
   - `{"platforms":null,"test_profile":123}`:同樣退 `csharp-xunit`(只印一行 stderr 警告),判定同上
   - `platforms` 的 `root` 目錄不存在:只印警告,不丟例外,每個名稱都是 `dangling`
2. 所以消費專案只要沒設測試設定(純文件專案、測試工具不在 profile 清單、剛 `lumos update` 還沒補設定)而筆記裡有新 `[test:]`,更新後第一次提交就全部被擋。這跟「索引建不起來」是同一種「沒有東西可查」卻走不同路。「相容」一節的說法(只有新加壞名字才擋)沒涵蓋它:這些名字不壞,是工具沒有能力判。
3. 規格需要一條「沒有可用的測試索引(沒設定、profile 退回預設、root 不存在、方法集合為空)就整組只提醒」,不然 `test_refs` 預設 block 對這類專案是誤擋。

## F6 「未提交改動落在測試檔上就只提醒」用 `git status --porcelain` 對平台根判,會讓擋在最常見情況全部降成提醒
severity: major
blocking: 是
引句:「工作目錄裡有沒提交的改動落在各平台的測試檔上時(新寫一支小函式用 `git status --porcelain` 對平台根判)」
file: `scripts/lumos:5111`(單一平台預設 root 就是 repo 根)
1. 單一平台的預設設定,平台根就是 repo 根。對 repo 根跑 `git status --porcelain`,工作目錄任何一個未提交的檔(本 repo 本身:開場 `git status` 就有 `docs/.governance-log.jsonl` 等一串 M,治理帳每次閘跑完都會被改)都算「有改動」。字面做,測試檔判斷變成「repo 裡有任何髒檔」,S9 讓整組永遠降成提醒,S1 只在工作樹全乾淨時才會擋。
2. 提交時(`--staged`)更糟:新測試與引它的筆記改在同一個提交裡是這個 repo 的標準做法;新測試檔已 `git add`,porcelain 是 `A  path`,屬於「未提交」。字面實作會把「測試和筆記一起提交」判成髒,恰好是最該擋的情境(測試名打錯字)降成提醒。
3. 規格沒說怎麼從 porcelain 輸出分出「測試檔」(依 profile 的檔案樣式)、也沒說已暫存與未暫存是否區別(`git diff --cached` 的已暫存檔在索引裡就是真的,只有工作目錄與索引不同的才有「讀工作目錄 vs 讀被檢查版本」的分歧)。未實測整段流程(規則還沒實作),依據是 `_platform_test_index` 讀工作目錄的實測(exp3/exp4)與 porcelain 的標準輸出格式。

## F7 略過條款定義行與合約行的判定,字面寫法與既有判定不一致,會把計劃裡寫在測試前的條款擋掉
severity: major
blocking: 是
引句:「與計劃裡的條款定義行(行首 `[SN]`)略過」
file: `scripts/lumos:6161`(_CLAUSE_LEAD_RE:定義行是去掉列表、標題、粗體、表格、勾選框符號後行首的 `[SN]`,且「第一次出現在行首」才算定義)
file: `scripts/lumos:4689`(INVARIANT_RE 用 `^KEY:` 錨定,不容縮排;extract_contracts 先 `strip()`)
1. 實測 exp9:`- [S1] x`、`  - [S1] x`、`**[S1]** x`、`| [S1] | x`、`### [S1] x` 的 `startswith('[S')` 都是 False,`_CLAUSE_LEAD_RE` 都命中。本計劃自己的條款寫法就是 `- [S1] …`。字面「行首」實作不會略過這些行,計劃裡的 `[test:t_尚未寫的測試]` 會被判懸空擋下;條款通常在測試寫出來之前就要先寫(spec-gate 先判門再紅綠)。
2. 合約行同理:`INVARIANT_RE.match('  KEY: ★INVARIANT★ x')` 是 False,`.match('  KEY: ★INVARIANT★ x'.strip())` 才是 True;`_notelines_rows` 回的是原始縮排行(`summary: |` 底下的行縮兩格)。規格說 `KEY:★INVARIANT★` 開頭,也沒提 `KEY:(日期) ★INVARIANT★` 的前綴變體(INVARIANT_RE 認)。
3. 規格要明寫:條款定義行用 `clause_bindings` 同一個判定(`_CLAUSE_LEAD_RE` 加「該編號第一次出現」),合約行用 `INVARIANT_RE` 對 `strip()` 後的行;否則兩種寫法各自出誤擋。

## F8 `[test-gone:名稱@提交]` 在這個 repo 的標準工作流裡常常寫不出來,或寫了馬上失效
severity: major
blocking: 是
引句:「只驗寫法與提交(至少 12 碼、在某個分支的歷史上;淺層 clone 判不了就略過那一筆)」
file: `scripts/lumos:27114`(_pin_commit:找不到提交、不在分支歷史上、淺層 clone 都回同一個 None)
file: `scripts/lumos:28586`(淺層 clone 只在 `--diff` 路徑有整道略過;`--staged` 路徑沒有)
1. 刪測試與改筆記是同一個提交(專案鐵則:程式與筆記同一個提交;「改 code 沒動圖譜」pre-commit 會擋)。提交還沒產生,作者寫不出刪掉它的那個提交編號;能寫的只有「更早的提交」,語意不是規格說的「那個提交被刪」。實務上只剩下先提交、再補一個提交的兩步。
2. 「推之前壓成一個」(專案提交規矩):在本機提交上寫的 `@sha` 壓縮後不在任何分支上,`_pin_commit` 的 `for-each-ref --contains` 找不到,推送擋下。其餘的 `路徑@提交:行號` 釘版本現在也有這個性質,但本案讓它進了測試名這條每週都會碰的路徑。
3. 淺層:實測 exp5,`git clone --depth 1` 之後 `_pin_commit(早於淺層邊界的 12 碼)` 回 None,跟「寫錯的提交」同一個回應。規格說「淺層判不了就略過那一筆」,但沒有說用什麼判(`_pin_commit` 無法區分);`--staged` 走本機掛鉤,沒有 `--diff` 那一段的整道略過,淺層 clone 裡提交含舊 `[test-gone:…@舊sha]` 的筆記會被擋。
4. 另:detached HEAD(rebase 進行中)時,新提交只被 HEAD 持有,`refs/heads` 與 `refs/remotes` 都不含它,同樣判不在分支上。
5. 規格要寫明:提交欄接受的語意(刪除前一個提交也算?)、壓縮後怎麼辦、`_git_is_shallow`(`scripts/lumos:5487`)先判後略過。

## F9 `[test-gone:]` 不驗內容,任何一個 12 碼提交加任何名稱就能放行,還滿足 PITFALL 的防回歸格
severity: major
blocking: 是
引句:「這支測試在那個提交被刪。不驗名稱存在,只驗寫法與提交」
file: `scripts/lumos:27114`(_pin_commit 只證明提交存在且在分支上)
1. 實測 exp5:`_pin_commit(最新提交前 12 碼)` 回完整 sha。也就是 `[test-gone:t_real_exists@<HEAD前12碼>]` 通過寫法與提交檢查;名稱可以是仍然存在的真測試、也可以是亂打的字。
2. S15 又規定 PITFALL 只寫 `[test-gone:]` 就滿足防回歸格。所以「PITFALL 沒有防回歸」可以靠 `[test-gone:隨便@任何提交前12碼]` 一行補齊,而且 `[test:]` 要驗存在、`[test-gone:]` 完全不驗,等於留一條比正門容易的側門。這條規格要擋的就是「指不到真測試」。
3. 規格沒說明這個口是刻意保留(說明了才有 REVISIT)。要驗得到的最小做法:那個提交的 diff 要真的刪過這個名稱(`git show <sha>` 的被刪行含該名稱);只是這一步會加 git 呼叫與合併提交的處理,屬於規格要取捨的事。

## F10 「起點版本」用同一篇筆記的路徑找,筆記改名或行搬家時,舊懸空名會被當成新加的
severity: major
blocking: 是
引句:「起點版本那篇筆記(提交時是 HEAD、推送時是範圍起點;新檔就是空)用同一支抽取得到名稱多重集合」
file: `scripts/lumos:27207`(_ns_diff 用 `-M`:改名並編輯時,diff 只給編輯過的行,檔名是新路徑)
file: `scripts/lumos:28266`(格子規則為此多讀「這次刪掉的行」並併進舊行集合,本案沒提)
1. 筆記 `git mv` 加上編輯其中含舊懸空名的行:新路徑在 HEAD 或範圍起點不存在,規格說「新檔就是空」,於是同行的舊名全被當新加,擋下。`scripts/graph-rename.sh` 就是這個repo 會做的事。格子規則已發現同題而用 `deleted + base_lines` 補,規格沒寫要不要沿用。
2. 筆記拆分、搬行(把一段從 A 篇搬到 B 篇):B 篇起點版本沒有這些名,逐名都是新加。規格「同一篇筆記」的定義就是這個結果;如果是刻意的,要在規格寫成已知取捨並給搬行的出口,現在寫的 S2 只講「同一行改字」。
3. 我標 major 的依據是「擋錯」的一條:改名加編輯屬於正常維運(`graph-rename.sh`)。搬行那條是 ⚠ 交編排者判斷是否算範圍內。

## 已查、無 finding
- 一行很長:5MB 單行 `_strip_inline_markup` 0.005 秒,反引號 50 萬對 0.02 秒(exp4),線性。
- 幾千個名稱:3000 個名稱同一個方括號,全是懸空時 `_classify_test_refs` 4.3 秒(每個名稱對 4.3MB 全文做 `in` 子字串搜尋,exp4);這是 3000 個互不相同的懸空名,實務上不會出現,也不是字面照做會出的錯,只在實作紀錄量時間時留意去重。已讀,無 finding。
- 逗號連空項:`[test:a,,b]` 判 a、b 兩個,空項略過;`[test:  ,  ]` 回 `[]`(F1 已把「空」當漏洞記)。
- 全形逗號 `[test:a，b]`:整段當一個名稱,判 bad-name(擋下),不是漏洞。
- 名稱含中文或空白:`\w` 認中文字,`有 空白` 進入 fake/dangling 判定(擋下),正常。
- 圍欄:`_visible_lines` 對沒閉合的圍欄整段隱藏之後內容、4 格縮排的 ``` 不算標記、````收三個 ```(exp8),與規格「寧可少認」一致;沒閉合反引號後的內容同樣不看(exp7)。兩者都是靜默跳過沒有提醒,規格已說「寧可少認」,不另標。
- 設定值壞:`_note_shape_slots_parse` 對大寫、非字串、null 的處理(大寫與非字串→block 加提醒、null→block 不提醒)是現成形狀;規格說照它做,字面沒有漏洞。
- 提交編號形狀:大寫 12 碼被接受(exp5)、64 碼與 11 碼與 `g` 開頭被拒;`_NS_PIN_HEX_RE` 上限 40 碼,SHA-256 專案不支援,與規格「至少 12 碼」沒衝突,不標。`@` 多個:`slot_parse` 不認 `test-gone` 之前當核心句;註冊後怎麼切 `@`(第一個或最後一個)規格沒寫,名稱本來就不驗,不標。
- 合併提交、空推送、刪分支:`--staged` 合併中整道略過、`--diff` 終點全 0 略過(`scripts/lumos:28575` 與 28594 前後),新規則掛在後面,沿用;沒有新增的邊界。

最高等級:major,blocking 共 10 條
