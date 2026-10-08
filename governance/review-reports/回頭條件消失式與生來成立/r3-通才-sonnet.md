severity: major

# r3 通才席報告(無鏡頭,逐節全讀)

審材:`/tmp/回頭條件消失式與生來成立-r3.md`。程式碼對照:rw 工作樹(下稱 rw)`scripts/lumos`、`scripts/test_lumos.py`、`skills/`、`scripts/templates/`。
本輪重點放在「r2 的修法有沒有真的解決原問題」與「補丁銜接處的新不一致」。下列 U1、U2、U3、U6 是 r2 已點出、但 r3 修法仍然做不到或接錯的;U4 是 r2 B8 的修法和驗收條款 S2 打架;U5 是 r2 補的列鍵文件清單有一份對不上現況。

## 逐節結論

- 檔頭、範圍、PRIOR-ART/RETIRE-IF/REVISIT、依據:已讀,無 finding(`t_drift_when_probes_evaluate_and_trigger` ⑨、〈做法〉第 0、2 節、各 `[[…]]` 連結對象在 rw 都存在)。
- 做法 1(條件鍵 `when-gone`):見 U3、U4、U5、U6、U7、U9。
- 做法 2(寫下時就已成立):見 U1、U2、U8。
- 做法 3(說明與同步):已讀,無 finding(`Systems/存量漂移守衛`、`Systems/筆記內容閘`、`Projects/漂移防治路線圖_計劃` 第 6、11 項「另案待開」字樣在 rw 都找得到)。
- 實務隱患、回退、天花板:逐類答覆放在檔末;內容本身除上列各條牽連處外,已讀,無 finding。
- 審計修正紀錄:已讀,無 finding。

---

**U1 往回查「三種 None」的分辨,r3 點名的函式做不到;總量上限也沒有可呼叫的地方**
severity: major
blocking: 是 — 照字面實作會把「超過單篇上限」或「讀不出」的舊版當成「那篇不存在,這一世從下一版開始」,標出錯的提交
引句:「每一版的筆記內容:`_nodehome_cat_blobs_capped` 批次讀,單篇上限照既有、總量上限 32 MiB(超過就判不了)」

1. 位置:〈做法〉2.3 第二個子點,和 2.2 第二個子點「往回的某一版:那篇不存在 → 這一世的開頭就是它的下一版(正常停);讀不出、超過單篇大小上限、不是嚴格 UTF-8 → 判不了(…原稿把三種 None 混在一起)」。
2. 問題:r2(C4、B2)抓到的就是「三種 None 混在一起」,r3 的修法是在 2.2 把三種寫成三種處置,但 2.3 實際要呼叫的 `_nodehome_cat_blobs_capped` 只回 `bytes|None`:該版沒有這個路徑、超過 `max_bytes`、物件不是一般檔,三者都是同一個 `None`,而且它只有單一 `max_bytes` 參數,沒有「總量」概念。所以 2.2 的三分法在 2.3 指名的函式上無法實作;「總量上限 32 MiB」也沒有地方累計。
3. 例子:某篇舊版筆記 3 MB(超過單篇上限),它之前的版本還有同一條 → 實作者拿到 `None`,只能二選一:全當「不存在」→ 這一世的開頭停在較新的版本,標出一個比實際晚的提交(誤標,而且 `--json` 的 `born.commit` 是錯的);全當「判不了」→ 「刪掉再重寫」這種正常歷史(中間有一版真的沒有那篇)也被判成判不了,S5「刪掉又重新寫 應 以重新寫的那一版為準」的測試紅。
4. 查證佐證:file: `scripts/lumos:26527`(`_nodehome_cat_blobs_capped` 過大者 `res[i]` 保持 None)、file: `scripts/lumos:26508`(`_nodehome_cat_sizes` 才分得出「沒有這個物件」,回 None)、file: `scripts/lumos:26541`(`_nodehome_cat_blobs` 對 missing 與非 blob 都 append None)。要分三種必須自己先問 `_nodehome_cat_sizes` 再讀,spec 沒這樣寫。

---

**U2 「原樣路徑」在 `_nodehome_list` 裡不存在;log 回空的處置也沒定義**
severity: major
blocking: 是 — 照字面實作拿不到「原樣」,NFD 存的筆記路徑會查到空歷史,而 spec 沒說空歷史怎麼辦
引句:「路徑用 git 列樹時的原樣路徑(`_nodehome_list` 的原樣那份,不是 NFC 後的)」

1. 位置:〈做法〉2.3 第二個子點(提交清單)。
2. 問題:`_nodehome_list` 回的 `(files, allp)` 兩份路徑都已經 `nfc(os.fsdecode(p))`,沒有任何一份是原樣。r2 Z2 的本意是「NFC 過的路徑對 NFD 樹查不到」,r3 修法引用了一個不存在的設施。程式裡真正保留原樣的是 `_nodehome_name_status(raw, norm=False)`(給 diff 輸出用),列樹沒有。
3. 例子:Linux CI 上、git 裡以 NFD 存的筆記(含日文濁音或韓文的檔名)→ 照字面用 NFC 路徑下 `:(literal)` 的 `git log` → 結果空;再用 `commit:NFC路徑` 讀 → 全是 missing。spec 的 2.2 沒有「log 回空」這一條(只列了未提交的行、淺層、partial clone、git 失敗),實作者可能把它當「這一世的開頭不明」不標、或當「不存在 → 正常停」。同一個空結果也會發生在:筆記在工作目錄是新檔、還沒有任何提交(沒被「工作目錄裡還沒提交的行」涵蓋到:那句講的是行,不是整篇)。
4. 查證佐證:file: `scripts/lumos:26196-26230`(`_nodehome_list`,`allp.append(nfc(...))`)、file: `scripts/lumos:32186-32192`(`_drift_cat` 註解:「樹清單把路徑轉成 NFC 了」)、file: `scripts/lumos:26438`(`norm=False` 只在 name-status)。需要補:原樣路徑從哪取(新寫一支 ls-tree 解析,或 `git log --name-only -z` 對回),以及 log 回空要判成什麼。

---

**U3 撤除條件的 `..\x` 在提交時擋不住,S4 照 spec 設計實作會紅**
severity: major
blocking: 是 — S4 要求撤除條件 `..\x` 報錯,但 spec 指定的驗證路徑(`_slot_retire_err` → `_probe_value_err`)收到的是未轉斜線的原文,放行
引句:「撤除條件的 `when-gone` 標記內有反引號或 `..\x` 應 照 REVISIT 那條路報錯」

1. 位置:〈做法〉1.2 最後一條(`_slot_retire_err` 值驗證走 `_probe_value_err` 同一支)與 〈驗收條款〉S4、S3。
2. 問題:REVISIT 那條路能擋 `..\x`,靠的是 `_probe_parse` 先把 file/symbol/test 的反斜線換成斜線再驗,並在正規化之後再驗第二遍。`_slot_retire_err` 沒有這兩步,直接把 `v[5:].partition(":")` 切出來的原文丟給 `_probe_value_err`。spec 為 `gone` 新寫的 `_probe_gone_err` 只說「`..` 與 `/` 開頭照 file」,沒說自己要處理反斜線;而且 `_probe_parse` 那行 `k in ("file", "symbol", "test")` 的換斜線正好不能加 `gone`(字串段反斜線要原樣),所以靠 `_probe_parse` 的第一遍救不了 retire 路。
3. 例子(已在 rw 實跑):`m._slot_retire_err("when-file:..\\x.py")` → `None`(放行);同一值走 `m._probe_parse("[when-file:..\\x.py][by:2026-12-01]")` → errs 有「../x.py 不合法」。對 `gone` 照字面實作,`[retire:when-gone:..\x]` 提交時同樣放行,S4 該條的測試紅;更糟的是這條撤除條件之後在 scan 才被 `_retire_lines → _probe_parse` 列成寫錯,提交閘沒擋。
4. 查證佐證:file: `scripts/lumos:3866-3891`(`_slot_retire_err`)、file: `scripts/lumos:31982-31986`(`_probe_parse` 的換斜線與二次驗證)、file: `scripts/lumos:31910`(`_probe_value_err` 無反斜線處理)。修法要在 `_probe_gone_err` 內部對路徑段自己轉斜線再驗,並在 〈做法〉1.2 寫明。

---

**U4 「路徑找不到」的追加提示句沒限定「新寫」,把真的刪檔的轉變也加上錯誤提示;S2 內部互相矛盾**
severity: major
blocking: 是 — 照字面實作,「推送刪掉檔」這個最主要的使用情境,點名訊息會被附上「打錯字、全形符號,或是被 gitignore 的檔?」
引句:「`when-gone` 的路徑在終點版本就找不到時,點名訊息後面多一句」

1. 位置:〈做法〉1.4 末段與 S2 第三、四個分句。
2. 問題:r2 B8 的本意是「新寫就已成立」那個原因句(「這次新寫(或改了條件)的回頭條件,條件已經成立」)會讓人以為東西剛被刪,所以要補一句。r3 寫成了「終點版本就找不到」這個純狀態條件,沒綁「起點沒有同一條」。但「這次推送刪了那支檔」(S2 第一句、`[when-gone:src/a.py]` 的典型使用)的終點同樣找不到那個路徑,同一句也會附上去,而且那種情況原因句是「這次推送讓條件成立了」,附「打錯字?」是錯的。S2 第一句要求點名「這次推送讓條件成立了」,第三句要求「終點找不到就多一句」,對「刪檔」這個輸入兩句同時成立,測試 `t_drift_when_gone_push` 無法同時寫出兩個斷言。
3. 另一個銜接處:附加句要用到終點的樹(判斷路徑在不在),但產生原因字串的是 `_drift_probe_judge(now_of, was_of, pr, old)`,簽章裡沒有樹也沒有鍵,spec 沒說這句在哪一層加(判完後在 `_drift_probe_check` 的 `elif verdict:` 分支加,或改 judge 簽章)。
4. 例子:`[when-gone:src/a.py]` 存在已久,這次推送刪掉 `src/a.py` → 判定「這次推送讓條件成立了」+ 「路徑在這一版就找不到——打錯字…?」→ 作者被誤導去檢查拼字。
5. 查證佐證:file: `scripts/lumos:32589-32604`(`_drift_probe_judge`,`old` 為真才是「這次推送讓條件成立了」)、file: `scripts/lumos:32476-32497`(`_drift_probe_check` 組 `must` 的位置)。

---

**U5 列鍵文件清單裡的 `SKILL.md` 根本沒列鍵,S7 與〈做法〉1.5 的守衛測試一開始就紅**
severity: major
blocking: 是 — 守衛測試要求四份文件都提到 `_PROBE_KEYS` 的每個鍵,但 SKILL.md 只出現 `when-file`,symbol/test/status 都不在;照字面寫測試等於一建好就紅
引句:「漂移守衛測試掃這兩句程式訊息、提醒那段、上面四份文件,都要提到 `_PROBE_KEYS` 的每個鍵」

1. 位置:〈做法〉1.5 與 〈驗收條款〉S7(S7 只列三則訊息,沒列文件,兩處範圍不一致)。
2. 問題:r2(C8、B7、U4)要求補 reference.md、範本、SKILL.md。rw 現況:`skills/lumos-project-notes/SKILL.md` 只有第 73 行一段,提到 `[when-file:路徑]` 之後寫「四種鍵怎麼選見 commands/03-寫回圖譜.md」,並沒有列 symbol/test/status;`reference.md` 第 404 行是 RULE 的 retire 清單;`03-寫回圖譜.md` 第 50 行才是 REVISIT 的完整列鍵。要滿足「每份都提到每個鍵」,不是「列鍵那句補一個」,而是得把 SKILL.md(常駐、有大小壓力)灌進四個鍵的清單。另外「四種鍵」字樣在 03 與 SKILL.md 各一處(`grep "四種鍵"`),spec 沒要求改成五種。
3. 例子:實作者照 S7 寫 `for doc in (...四份...): for key in _PROBE_KEYS: assert f"when-{key}" in text`,SKILL.md 對 `symbol/test/status` 三個既有鍵就紅,和 `gone` 無關。
4. 查證佐證:file: `skills/lumos-project-notes/SKILL.md:73`、file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:50`、file: `skills/lumos-project-notes/reference.md:404`、file: `scripts/templates/graph-discipline.md:50`(retire 清單)與 `:59`(鐵則 4 只有 when-file,被 `t_graph_discipline_negation_revisit` 逐字釘住)。要改的是:守衛的文件範圍按「真的列鍵的地方」重定,或明說 SKILL.md 改列鍵。

---

**U6 範本一改,本 repo 自己的 CLAUDE.md、AGENTS.md 注入區塊必須重注入;spec 沒列,而且「升範本版本」沒有對象**
severity: major
blocking: 是 — 只改範本不重注入,`t_graph_discipline_negation_revisit_source` ①與 doctor Check D 都紅,spec 的步驟會漏
引句:「範本有改就照既有規矩升範本版本」

1. 位置:〈做法〉1.5 末段。
2. 問題:範本 `graph-discipline.md` 刻意無版本戳(`_START_TEMPLATE` 註解:「範本保持無版本戳…版本由 reinject 當下插值」),所以沒有「範本版本」可升;既有規矩其實是「範本改了,CLAUDE.md/AGENTS.md 的注入區塊要重注入」(本 repo 的 `CLAUDE.md:52`、`AGENTS.md:53` 都是範本第 50 行 retire 清單的拷貝)。spec 的檔案清單列了 `scripts/templates/graph-discipline.md`,沒列這兩份注入拷貝,也沒說重注入,「升版本」一詞會讓實作者去找不存在的版本欄。
3. 例子:實作者只改 `scripts/templates/graph-discipline.md` 第 50 行加 `when-gone:路徑::字串` → `t_graph_discipline_negation_revisit_source` ①(「注入區塊跟範本一致」)紅;doctor Check D 對本 repo 也報漂移。
4. 查證佐證:file: `scripts/lumos:335-352`(`_START_TEMPLATE` 與「無版本戳」註解)、file: `scripts/test_lumos.py:62416-62432`(`_source` 測試比對 `span.body == body`)、file: `CLAUDE.md:52`、file: `AGENTS.md:53`。

---

**U7 「判不了」時 spec 承諾「點名那支檔、講原因」,既有機制只在「樹上有、讀不出」時才點名,其餘四種判不了點名不到**
severity: minor
blocking: 否 — 只影響判不了時訊息的準確度,不影響成立/不成立的判定
引句:「內容含 NUL、是 Git LFS 指標檔(開頭 `version https://git-lfs.github.com/spec/`)、或不能用嚴格 UTF-8 解碼」

1. 位置:〈做法〉1.3「帶字串」子點、1.2 的 `_drift_row_unread` 一項、天花板 7 與審計紀錄 r2 例(「點名時講原因」)。
2. 問題:`_DriftProbeTree.unread_for` 只在 `self._text[path] is None` 時才回該路徑;資料夾(根本沒讀)、NUL、LFS、Big5(`_text` 存的是替代字元解碼過的非 None 字串)都回 `[]`。於是這五種判不了的訊息只會是固定句「判不了(git 讀不出程式檔或筆記)」,既沒點名那支檔,字面原因也不對(檔其實讀得出)。spec 在 1.3 說「scan 的『判不了』照既有的 `_drift_bad_note` 點名那支檔」,但沒給「原因」的載體(例如 `one` 回第三種值)。
3. 例子:`[when-gone:legacy.c::時間]`,legacy.c 是 Big5 → 推送時被點名「判不了(git 讀不出程式檔或筆記)」,作者不知道是編碼問題,也沒看到 legacy.c 的名字。
4. 查證佐證:file: `scripts/lumos:32310-32320`(`unread_for`)、file: `scripts/lumos:32555`(`_drift_bad_note`)、file: `scripts/lumos:32676`、`:32489`(固定的「git 讀不出…」文字)。

---

**U8 born 的接線有兩個沒寫到的缺口:發現沒有帶條件;已表態的列在文字輸出裡沒有「底下」可印**
severity: minor
blocking: 否 — 實作者看程式一定會發現,補起來不影響設計方向
引句:「呼叫點在 `cmd_drift_scan` 拿到 `_drift_probe_scan` 的發現之後」

1. 位置:〈做法〉2.5。
2. 問題:(a) `_drift_probe_scan` 回的發現 dict 只有 `kind/path/line/text/related/why`,沒有解析過的 `conds`;`cmd_drift_scan` 拿到發現之後要查寫下時,得再用 `_probe_lines` 或 `_probe_parse` 重抽一次,或改 `_drift_probe_scan` 回傳。spec 沒指定。(b) 「照既有『先前表態』那行的呈現(`_drift_prev_ack_line`)…已表態的照樣標」:`_drift_scan_print` 對已表態的列只印一行 `(已表態)`,`why` 與 `prev_ack` 兩行都包在 `if not acked:` 裡;照樣抄 `_drift_prev_ack_line` 的位置,已表態的就印不出 born——而第 11 項要解的正是「表態後就看不出」。
3. 例子:一條已表態、生來成立的行,文字輸出只有 `  path:12  REVISIT…  (已表態)`,沒有「寫下時就已成立」;`--json` 有。S5 的「已表態的 應 照標」只對 json 成立。
4. 查證佐證:file: `scripts/lumos:32676-32680`(發現 dict 欄位)、file: `scripts/lumos:34968-34978`(`_drift_scan_print` 的 `if not acked:`)、file: `scripts/lumos:32806`(`_drift_prev_ack_line` 只吃未表態的 `prev_ack`)。

---

**U9 嚴格 UTF-8 解碼沒說 BOM;字串去不去頭尾空白也沒說**
severity: minor
blocking: 否 — 影響罕見輸入,最壞是提早判成立、可表態
引句:「能解碼就在文字裡找字串,找不到 → 成立」

1. 位置:〈做法〉1.3 與 1.1 字串規則(「去頭尾空白後不能是空的」)。
2. 問題:(a) 全庫讀取器一律 `utf-8-sig`(`_drift_decode` 的說明有專門講 BOM);spec 說「嚴格 UTF-8」沒講 BOM。用 `bytes.decode("utf-8")` 的話,BOM 留在第一個字元前,字串剛好在檔案開頭(例如 `#!/usr/bin/env` 或 `<?php`)就找不到 → 誤判成立。(b) 字串是「去空白後非空」只是驗證,比對用的字串有沒有去空白沒寫;`_drift_cond_split` 現行共用尾段是 `.strip()` 名稱,而 `_probe_norm_value` 說「字串原樣」,兩個說法會得到不同的比對字串(`[when-gone:a.py:: foo ]`)。
3. 例子:帶 BOM 的 `index.php`、`[when-gone:index.php::<?php]` → 檔案開頭是 U+FEFF 後接 `<?php`,但全檔只有這一處出現,嚴格 `utf-8` 解碼後仍可比對成功(BOM 在字串前面不影響子字串),所以只在「字串必須從第一個字元開始」才出問題——實務上是罕見輸入,記為 minor。
4. 查證佐證:file: `scripts/lumos:32180-32183`(`_drift_decode`)、file: `scripts/lumos:32195-32199`(`_drift_cond_split` 的 `.strip()`)。⚠ BOM 一項我沒有實跑「字串貼在檔首」的反例,只確認了程式慣例。

---

**U10 〈做法〉1.5 與 S7 的守衛範圍不一致;路徑裡有 `::` 的檔名被當成字串**
severity: minor
blocking: 否 — 文字不一致與罕見輸入
引句:「`::` 從**第一個**切(字串裡可以有 `::`,路徑裡不會有)」

1. 位置:〈做法〉1.1 第二個子點、1.5 與 S7。
2. 問題:(a) 「路徑裡不會有 `::`」是未查證宣稱:POSIX 檔名可以含冒號(例如 `docs/a::b.md`),不禁止;`[when-gone:docs/a::b.md]` 會被切成路徑 `docs/a`、字串 `b.md`,而 `docs/a` 在樹上不存在 → 立刻成立,推送被點名(帶「找不到路徑」那句,剛好給對提示)。spec 把它當不變量,沒列天花板。(b) 1.5 的守衛掃「兩句程式訊息、提醒那段、四份文件」,S7 驗收條款只寫「三則訊息」(沒有文件),測試名同一個 `t_drift_when_gone_grammar`;兩邊該一致。
3. 查證佐證:spec 內部(1.5 對 S7);file: `scripts/lumos:32195`(現行切法同樣不處理檔名含 `::`)。

---

## 實務隱患逐類

- 併發:無。scan 與推送判定只讀 git 物件與工作目錄,不寫帳(`cmd_drift_scan` 註解載明不寫治理帳);往回查多一個 `git log` 子行程,沒有共用可寫狀態。
- 效能:spec 的估算漏了一項。往回查每個不同提交要 `_drift_list`(整個 repo 的 `ls-tree -r`)加圖譜讀入,spec 實量的 0.19 秒是這一段;但判斷「不帶路徑的 symbol/test」時 `_DriftProbeTree.corpus` 每個提交還要讀整份程式碼,並對命中的檔跑 `ast.parse`。在 rw 實測:`scripts/lumos` 約 1.6 秒、`scripts/test_lumos.py` 約 2.5 秒,每個不同提交各一次。最多 20 條、20 個不同提交的最壞情況就是數十秒,已經碰到 60 秒預算;spec 靠預算耗盡改標「判不了(超過預算)」兜底,所以不會當機,但「成立的條件通常是個位數」只對一般情況成立。這是 spec 已用預算處理的 ⚠ 邊角,不另算 finding。`_DRIFT_LS_CACHE` 滿 8 筆就整個清空,20 個提交會反覆清空連目前 scan 用的樹,只多花時間、不影響正確。
- 回滾:spec 的敘述成立(還原後 `when-gone` 變不認得的鍵);補一個 spec 沒提的相容點:消費專案本機新版、CI 舊版時,新寫的 `when-gone` 會被舊版 CI 擋成「不認得的條件鍵」(〈相容〉已寫「更新前寫了會被舊版擋」,但沒提團隊內版本不一的情況),屬已知相容代價,不另報。
- 誤擋與繞過:誤擋來源主要是打錯字或被 gitignore 的路徑,spec 已設提示句並可表態;提示句的限定錯誤見 U4。繞過:寫本來就不存在的字串然後表態,spec 已明寫為留痕動作。大小寫不敏感檔案系統上寫錯大小寫的路徑,在工作目錄模式因 `allp` 來自 git 名稱仍判消失,同樣是打錯字的一類,可由提示句涵蓋。
- 安全/外送/金流/不可逆:無。只讀筆記與 git 物件;partial clone 已排除不呼叫網路。

最嚴重 severity 是 major,blocking 共 6 條(U1、U2、U3、U4、U5、U6)。
