severity: major

## 逐節結果

- 前言、frontmatter、問題與範圍、最小實驗、實驗結果、接線前三洞:已讀,無 finding。
  - 交叉引用的 5 個節點都存在:`Projects/設計審後端失敗與未知狀態_計劃`、`Verification/2026-10-02_代碼審完成路徑一句小實驗`、`Verification/2026-10-03_外部碼表推播小實驗`、`Systems/pitfalls-code-loop`、`Systems/design-loop`。
  - 「印不出來」那一洞與程式碼相符:`_lens_render_listed` 只印 `_contract_key_matches` 認的 KEY 合約行。
- 共用形狀、第一項、第二項、第三項、條款、實務隱患、回退、撤除條件:見下列 finding。

## Findings

### 1
severity: major
blocking: 是——補選的筆記在常見情況下根本不會被渲染,第二項的價值落空。
- 段落:第二項。
- 引句:「補進列出清單,種類標「外部碼表」,最多補 3 篇,已在清單的不重複。」
- 問題:補選的筆記接在固定席後面,而 `_lens_render_listed` 只對前 `cap=8` 篇印內文,其餘只印名字。
  - 固定席(家、事故、合約、直接相依)在多檔 diff 裡常常 ≥8 篇,補進來的筆記就落在 cap 之後,只剩一行檔名,審查員看不到官方原文。
  - spec 沒說補選的筆記要排在哪、要不要保證一定渲染。
- file: `scripts/lumos:40007`——`if i < cap:` 以外的分支只印「(超出上限,只列名)」。
- file: `scripts/lumos:40361`——`cap` 由 `_dispatch_lens_graph` 傳入,預設 8。

### 2
severity: major
blocking: 是——spec 的併發與快取宣稱與自己新增的行為互相矛盾。
- 段落:實務隱患「併發」與第二項時間上限。
- 引句:「快取鍵不變(輸出內容依 base 與 head 決定)。」
- 引句:「不夠就停止補選,並在輸出多印一行「外部碼表補選因時間上限中止」。」
- 問題:輸出一旦受牆鐘時間影響,就不再只由 base 與 head 決定。
  - 「因時間上限中止」的截斷版會被寫進以 base、head、表態 key 為鍵的快取。
  - 之後同範圍的每個派工都命中這份截斷結果,補選再也不會重跑。
  - 背景暖機行程和前景的負載不同,結果也可能不同。
  - spec 沒說截斷結果要不要寫快取、要不要帶標記重算。
- file: `scripts/lumos:40564` 之前的 `_dispatch_lens_graph` 尾段,`_lens_cache_write(cpath, out)` 無條件寫入。
- file: `scripts/lumos:40253`——`cached` 命中就直接 print。

### 3
severity: major
blocking: 是——spec 說「不新增閘門」,實際上新增了會擋推送的觸發面,卻沒有誤擋率的量測或逃生說明。
- 段落:第三項與實務隱患「守衛面」。
- 引句:「沿用棧別提問表態閘既有流程(作者表態、審查員看得到表態記錄),不新增閘門。」
- 問題:`_dispositions_verdict` 對每個「適用」的題,只要缺表態、表態過期,或 `na` 理由太短,就 `blocked=True`。
  - 所以每多一個觸發形狀,就多一條可能擋推送的路。
  - 形狀「引號 3 到 5 位數字比較」的誤傷面很廣:`version == "2024"`、`zip != "10001"`、`case "100"`、`in ("1","2")`、PIN 或年份比對。這些都不是外部回應碼。
  - spec 只用單元測試釘「不命中樣本」,沒有拿真實 repo 的 diff 量過命中率。
  - 閾值 `_STACK_ASK_ALL_DEFAULT=300`:單一棧改動行超過 300,整個題組全部適用。大重構會被迫替 8 個棧各答一次 extcode,即使完全沒碰外部碼。spec 的守衛面段落沒提這條路徑。
- file: `scripts/lumos:41849`——`out["blocked"] = bool(out["problems"])`。
- file: `scripts/lumos:23884`——`over = len(raw_lines) > threshold` 令全表適用。
- file: `scripts/lumos:23838`——`_STACK_ASK_ALL_DEFAULT = 300`。

### 4
severity: major
blocking: 是——第一項把 FACT 行抬成「以原文為準」,與專案的證據規則抵觸,且沒有新鮮度把關。
- 段落:第一項。
- 引句:「這段標題固定寫「外部事實(官方或第三方來源,程式碼看不到;以原文為準)」」
- 問題:專案規則寫明 `FACT:` 行只是線索,要有 `[confirmed:]`、近期確認才有挑戰程式碼的效力。外部碼表是廠商會改版的東西。
  - 現行 `_CTX_SOURCE_RE` 只驗「有來源標記」,不驗日期、不驗網址、不驗是否被標 `superseded`。
  - 任何一行帶 `[來源:外部]` 的 FACT 都會被渲染成權威原文。
  - 實驗 B 組 7/8 就是審查員照信推播;過期或寫錯的碼表因此會被同樣照信,而且是被標題背書的。
  - spec 沒有要求印 `[confirmed:]` 日期、跳過已 `superseded` 的行,或在標題註明可能過期。
- file: `scripts/lumos:3373`——`_CTX_SOURCE_RE` 只比對來源類別。

### 5
severity: major
blocking: 是——「每篇 10 行」的截斷沒有相關性選擇,真實碼表會把要看的碼擠掉。
- 段落:第一項。
- 引句:「每篇最多 10 行、每行截 200 字;沒有這類行就不印標題。」
- 問題:實驗用的碼表只有 4 到 5 行,通過門檻不代表真實碼表也行。
  - 真實的 2C2P 或其他金流碼表往往幾十個碼,照檔案順序取前 10 行,2000 或 1005 可能根本不在裡面。
  - spec 沒說依據這次 diff 命中的碼字面(例如 `"2000"`)優先挑出含該碼的行。
  - 每行截 200 字也可能把原文後半句截掉,而實驗 B 組的關鍵提示正是原文後半句「please do payment inquiry request」。

### 6
severity: major
blocking: 是——第二項的「改動行」從哪來、用哪套過濾,spec 沒定義,照現有函式做會誤觸發。
- 段落:共用形狀末句與第二項。
- 引句:「刻意不認:沒有引號的數字比較(`== 200`,HTTP 狀態碼語意公開周知,認了會誤傷大量程式);測試檔(沿用既有的測試檔判斷)。」
- 問題:`cmd_impact_diff` 的輸出只有 `files` 與 `results`,不含改動行文字;hunk 是函式內部組好、截 4000 字、只用來當查詢。鏡頭要自己再跑一輪 `git diff` 才有改動行。
  - spec 只說「沿用既有的測試檔判斷」,沒指名 `_stack_changed_ok`。
  - 那支還排除非代碼副檔名、`governance/review-reports/`(審計證物,刻意埋 bug 與引號碼)、簿記檔與工具自裝檔。
  - 只用測試檔判斷的話,審查卷證 `.patch`、`.md` 筆記或 vendored 檔裡的 `== "2000"` 會命中。
  - 這份 spec 自己和碼表筆記就大量含有 `"2000"` 字面。
  - 第三項走 `pitfalls --diff` 那套,第二項走鏡頭自己的 git diff,「單一來源」只釘了正規式,沒釘取行與過濾。
- file: `scripts/lumos:35692`——`_stack_changed_ok` 的排除清單。
- file: `scripts/lumos:38862` 附近——impact 的 hunk 只拿去當 query,不回傳。

### 7
severity: minor
blocking: 否——補選讓列出清單由空變非空時,v1.2 備援段會被跳過,與「行為完全一樣」的說法有出入。
- 段落:第二項。
- 引句:「沒命中形狀時鏡頭行為與現在完全一樣。」
- 問題:沒命中時確實一樣。但命中、固定席為 0 篇、補選到 1 篇時,`if not listed:` 的備援段(code 層既有相依)不再附上。
  - 命中形狀的 diff 反而少了備援資訊。
  - spec 沒說補選應該在備援判斷之前還是之後,以及兩者能否並存。
- file: `scripts/lumos:40346`——`if not listed:` 才進 `_lens_fallback`。

### 8
severity: minor
blocking: 否——第一項改動共用渲染函式,波及 spec 模式鏡頭,spec 範圍與測試沒涵蓋。
- 段落:設計 PRIOR-ART 與範圍。
- 引句:「派工鏡頭的節點渲染(兩種鏡頭共用一支)」
- 問題:`_lens_render_listed` 同時服務 diff 模式與 spec 模式(讀工作樹)。第一項上線後,設計審的鏡頭也會印外部事實行。
  - 範圍段卻寫「代碼審派工時推給審查員的參考筆記;不在範圍:設計審」,自相矛盾。
  - S2 只測渲染函式本身,沒有測 spec 模式是否要印。
- file: `scripts/lumos:40564`——spec 模式也呼叫 `_lens_render_listed`。

### 9
severity: minor
blocking: 否——共用形狀的一般欄比對的是被剝字串的行,spec 沒交代,第三組形狀會寫錯。
- 段落:共用形狀。
- 引句:「欄位名那組放一般那一欄(題目表要求一般欄不能空)。」
- 問題:一般欄(`when`)比對前會把字串字面換成 `""`。第三組「`respCode ==` 後接引號字串」放一般欄,實際比對的是 `respCode == ""`,必須寫成配 `""` 的正規式,而且會連空字串比較 `x == ""` 也命中。
  - 另外 `na` 自動樣板的理由只拼 `when`,不含 `when_raw`,第一組(全在 `when_raw`)未觸發時的說明會不完整。
  - spec 與 S1 都沒針對這點設樣本。
- file: `scripts/lumos:23942`——`_strip_string_literals` 把字串換成 `""`。
- file: `scripts/lumos:42015`——樣板理由只讀 `s["when"]`。

### 10
severity: minor
blocking: 否——現有測試把題數寫死,spec 的測試清單沒涵蓋,實作時會一片紅。
- 段落:條款 S5。
- 引句:「題目表除 sql 外的八個棧應各多一題 `<棧>-extcode`,id 集合應釘住」
- 問題:S5 只提 `t_stack_question_triggers`,但另有題數釘死的斷言。
  - `len(...["py"]) == 5`、`dart == 6`、`java == 7`。
  - kt 的 `len(data["stack_questions_meta"]["kt"]) == 7`。
  - 加題後這些全紅,而且「純新增也動邊界」。
  - `t_stack_question_triggers` 的 id 集合(`set(ids) == {...}`)與 `_samples` 也要同步。
- file: `scripts/test_lumos.py:23285`、`scripts/test_lumos.py:23455`、`scripts/test_lumos.py:23512`、`scripts/test_lumos.py:41319`。

### 11
severity: minor
blocking: 否——`[查:]` 欄在程式碼裡沒有定義,也沒有任何檢查。
- 段落:第一項末句與第三項題目文字。
- 引句:「網址寫在標記外面的 `[查:]` 欄(例:`FACT:2000 原文「…」 [來源:外部] [查:https://…]`)」
- 問題:全 repo 找不到 `[查:` 的定義或 lint。它只是約定,工具不會驗網址存在、不會禁止寫進來源標記。
  - 「[來源:外部 網址] 不會被認得」的後果是該行被當成沒帶來源,會被 note-shape 擋下,但作者看到的訊息是「缺來源」,指不到原因。
  - 題目文字括號也不平衡(「…附官方網址)網址寫在 [查:] 欄,不要寫進來源標記)」多一個右括號)。
- file: `scripts/lumos:3373`——只認五種來源類別。

### 12
severity: minor
blocking: 否——補選逾時機制沒有夾住單次讀檔的 timeout,最壞會超出內層預算。
- 段落:第二項與實務隱患「效能」。
- 引句:「每讀一篇前先看剩餘時間,不夠就停止補選」
- 問題:「讀前看剩餘」只擋下一篇。`_lens_git` 預設 `timeout=20`,剩 1 秒時發出的讀取仍可阻塞 20 秒,超過 hook 內層(外層 × 0.7)的設計前提。
  - `_lens_git` 有 `timeout` 參數可以夾,spec 沒說要夾。
- file: `scripts/lumos:39244`——`_lens_git(..., timeout=20)`。
- file: `docs/lumos-toolchain-knowledge/Systems/hook逾時預算.md`——內層必須明顯小於外層的規則。

### 13
severity: minor
blocking: 否——同一題在多棧 diff 會問 8 次,且 `lands_in` 漏了管題目表的筆記。
- 段落:第三項與 frontmatter 的 `lands_in`。
- 引句:「id 為 `<棧>-extcode`,題目文字與觸發形狀全部引用同一組常數(單一來源)。」
- 問題一:題目 id 按棧各一個,kt+node+py 混合 diff 會要求三份內容相同的表態。
  - spec 沒說要不要跨棧去重。
  - `.go`、`.php`、`.rb` 與無 `package.json` 的 `.ts` 不在題目表裡,完全沒覆蓋。這是已知邊界,但 spec 沒寫進限制。
- 問題二:`lands_in` 只有 `Systems/pitfalls-code-loop` 與 `Systems/design-loop`,而題目表有專屬說明節點 `Systems/棧別提問表態閘` 與 `Systems/效能檢核目錄`。
  - 程式碼註解要求「目錄改動須同步此表」。
  - 現有測試 `t_tension_doc_sync` 也在核對這兩篇。
  - 漏掉的話,改完題目表就違反「每支檔有家、改到要寫進家」的鐵則。
- file: `scripts/lumos:23390`——題目表與效能檢核目錄的同步註解。
- file: `scripts/test_lumos.py:42148`——兩篇節點被漂移守衛點名。

### 實務隱患逐類
- 併發:finding 2。spec 說「已排除」,但新增的時間截斷輸出會被寫進快取,前提不成立。
- 效能:finding 12。補選最多讀 8 篇,量不大,但逾時沒夾住。取改動行還要多跑一輪 `git diff`(finding 6),spec 沒計入。
- 資源:無。不新增連線、檔案控制代碼或鎖,沿用 `_lens_git`。
- 回滾:無。已核對 `_dispositions_validate` 會擋對不到題目表的 id,spec 回退節的描述屬實。
- 守衛面誤觸發:finding 3、6、9。

## 對固定席節點的判定
- `Systems/pitfalls-code-loop`:已讀。這份設計新增的鏡頭補選與外部事實行渲染,不破壞該節點的合約行為。
  - 「合約行」仍由 `_contract_key_matches` 掃描,第一項只在其後追加。
  - 不影響的前提是 finding 1、2、7 修掉,否則補選會污染列出清單與快取語意。
- `Systems/design-loop`:判「有影響」。第一項改的 `_lens_render_listed` 也服務 spec 模式(finding 8)。設計審的鏡頭輸出會變,而 spec 範圍聲明「不在範圍:設計審」。

最嚴重等級:major;blocking 共 6 條(finding 1 到 6)。