severity: major

# r3 正確性席審查報告(回頭條件消失式與生來成立,第 3 版修訂稿)

審查方式:逐節讀完整份 spec,對照 `scripts/lumos`、`scripts/test_lumos.py` 與文件實際內容;凡能實驗的都在臨時行程裡載入 `scripts/lumos` 實跑(沒有改 repo)。以下 finding 都帶可重現的查證。

## 實務隱患鏡頭:碰到的風險類(逐類答)

- 併發:無 + 只讀 git 物件、scan 不寫帳;唯一的共用狀態是 `_DRIFT_LS_CACHE`(上限 8,滿了整個清掉),往回查建 20 個樹會把 scan 自己終點的快取沖掉,但終點的 `files` 與 `ptree` 已在手上,重列一次即可,不會算錯。
- 效能:有 + 見 C8(實測每個提交建樹加讀語料約 2 秒,不是 0.19 秒)。
- 回滾:無 + 還原提交後 `when-gone` 變「不認得的條件鍵」,`_probe_parse` 會把整行標 `bad`,check 與 scan 都不評估,與〈實務隱患〉的描述一致。
- 誤擋與繞過:有 + 見 C3(刪檔這個主要觸發會印打錯字提示)、C2(反斜線寫法)。
- 記憶體:有 + 見 C1 的總量上限,規格沒有寫怎麼先問大小。

## C1 至 C9 如下

**C1 §2.2/§2.3 的三種「讀不到」用 `_nodehome_cat_blobs_capped` 分不出來,r2 修法照字面做不出來**
severity: major
blocking: 是 — 刪除提交(正常停)與超過單篇上限(判不了)在該函式回傳裡都是 None,照字面實作會把其中一種做錯
引句:「讀不出、超過單篇大小上限、不是嚴格 UTF-8 → 判不了(設計審 r2 正確性席、邊界席:原稿把三種 None 混在一起)」

1. 位置:〈做法〉2.2 第二個子項與 2.3「每一版的筆記內容:`_nodehome_cat_blobs_capped` 批次讀」。
2. 問題:r2 的修法要求「不存在 → 正常停」「超過上限 → 判不了」「讀不出 → 判不了」三種分開。但規格指定的函式把三種都回成同一個 None。該函式先用 `_nodehome_cat_sizes` 問大小,`n is None`(物件不存在)與 `n > max_bytes`(太大)都不進 `ok`,`res` 預設 `None`;git 讀取失敗則整批回 None。規格沒有說要自己另外呼叫 `_nodehome_cat_sizes` 去分。
3. 例子:筆記在提交 D 被刪掉、提交 R 重新建立(帶同一條條件)。提交清單含 D 與 R。若實作者把 None 一律當「不存在 → 正常停」,則一個 600KB(超過上限)的中間版本也會被當成「刪掉過」,這一世的開頭被錯切到它的下一版,scan 就會對錯的提交印「寫下時就已成立(提交 xxxx)」。反過來若把 None 一律當判不了,則 D 這種刪除提交永遠讓整段判不了,「刪掉又重新寫 應以重新寫的那一版為準」(S5)永遠做不到。
4. 查證:file: `scripts/lumos:26527`(`_nodehome_cat_blobs_capped`:`ok = [i ... if n is not None and n <= max_bytes]`、`res = [None] * len(specs)`)、`scripts/lumos:26494`(`_nodehome_cat_sizes`:缺物件回 None)。規格的 32 MiB 總量上限也沒有機制:`_nodehome_cat_blobs_capped` 只管單篇、讀完才回;同類先例 `scripts/lumos:27689` 是先問 sizes 加總再讀,規格沒有指向它。「單篇上限照既有」也沒有單一既有常數(`_ROLE_MAX_BYTES` 512KB、`_NS_APPEND_BASE_MAX_BYTES` 524288、`_CODELOOP_BOOKKEEPING_HEAD_CAP` 各自不同)。

**C2 §1.2 號稱逐一列出「拆值與讀鍵的地方」,漏了 `_probe_parse` 裡依鍵名先轉反斜線的那一行,兩種實作方式都會做錯**
severity: major
blocking: 是 — 不改那行,`..\x` 會被收成 `x`;直覺地把 gone 加進那行,又會把字串裡的反斜線改掉,違反 S3
引句:「拆值與讀鍵的地方逐一列出(設計審 r2 三席:原稿說「全部呼叫同一支」不是現況)」

1. 位置:〈做法〉1.2 清單(8 個子項、10 個函式),S3「`..\x` 這種反斜線寫法 應 報條件寫錯、字串裡的反斜線 應 原樣保留」。
2. 問題:`_probe_parse` 在呼叫 `_probe_value_err` 之前有一行 `val.replace("\\", "/") if k in ("file", "symbol", "test") else val`,這是依鍵名分派的另一個點,清單沒列。該行存在的理由寫在註解裡:`a\..\x.py` 若不先轉成斜線,第一次驗證看不到 `..` 段,隨後 `_probe_norm_value` 內的 `_posix_norm` 會把它正規化成 `x.py`,第二次驗證就過關了。
3. 例子:
   - 照清單字面實作(不動那行):`[when-gone:a\..\x.py][by:2026-12-31]` 第一次驗證 `"a\\..\\x.py".split("/")` 只有一段,不含 `..`;`_probe_norm_value` 對路徑段做 `nfc(_posix_norm(path))` 得到 `x.py`(已實跑:`_posix_norm('a\\..\\x.py')` 回 `'x.py'`,`_probe_bad_path('a\\..\\x.py')` 回 False);第二次驗證 `x.py` 合法。結果提交時不擋,條件被默默改成 `x.py`,S3 與 S4 的 `..\x` 案例紅。
   - 直覺地把 `"gone"` 加進那個元組:整個值(含字串段)的反斜線全被轉成斜線,`[when-gone:src/a.py::C:\temp]` 比對的字串變成 `C:/temp`,違反 S3「字串裡的反斜線 應 原樣保留」。規格要求的是「先切再正規化」,但這行是先正規化整個值再切。
4. 查證:file: `scripts/lumos:31982`、`scripts/lumos:31983-31986`;註解 `scripts/lumos:31980-31981`。

**C3 §1.4 的「路徑在這一版就找不到」提示,字面上也會套在刪檔這個主要觸發上**
severity: major
blocking: 是 — gone 最常見的合法觸發是檔被刪,S2 的字面讀法會對它印「打錯字、全形符號、gitignore」
引句:「`when-gone` 的路徑在終點版本就找不到時,點名訊息後面多一句「路徑在這一版就找不到——打錯字、全形符號,或是被 gitignore 的檔?」」

1. 位置:〈做法〉1.4、S2 第四個子句「路徑在終點版本就找不到時點名 應 多一句」。
2. 問題:條件文字沒有限定「起點也找不到」或「屬於新寫的那條分支」。`[when-gone:src/a.py]` 的正規成立方式是這次推送把 `src/a.py` 刪掉,此時「終點版本就找不到」為真。S4 也明寫「推送刪掉那支檔 應點名撤除條件成立」。理由句自己說「原本的原因句會讓人以為東西剛被刪」,表示意圖只限制在「不是剛被刪」的情形,但驗收句沒有這個限定。
3. 例子:推送刪掉 `src/a.py`,筆記早就有 `[when-gone:src/a.py]`(`old` 為真)。`_drift_probe_judge` 回 `這次推送讓條件成立了`,依 S2 字面再接上「路徑在這一版就找不到——打錯字、全形符號,或是被 gitignore 的檔?」,作者看到的是個誤導的提示。反方向:新寫的行與刪檔在同一次推送,同樣會誤印。
4. 附帶的未定義:提示要在哪裡接,規格沒說。`_drift_probe_judge(now_of, was_of, pr, old)` 沒有樹的參數,拿不到「終點路徑在不在」;`_drift_probe_check` 收集 `must` 時才有 `_tree(tip)`。實作者得自己決定位置,而理由字串同時被 kind="retire" 共用。
5. 查證:file: `scripts/lumos:32589-32604`(`_drift_probe_judge`)、`scripts/lumos:32496-32502`(`must.append(... "why": verdict)`)。

**C4 §2.3 引用的「`_nodehome_list` 的原樣那份」不存在,而且原樣路徑拿不到時整段行為沒定義**
severity: minor
blocking: 否 — 只影響以 NFD 儲存檔名的庫,而且結果是判不了或查不到,不會寫出錯的標記
引句:「路徑用 git 列樹時的原樣路徑(`_nodehome_list` 的原樣那份,不是 NFC 後的)」

1. 位置:〈做法〉2.3 第二個子項。
2. 問題:`_nodehome_list` 一律 `path = nfc(os.fsdecode(p))`,`allp` 與 `files`、oids 全是 NFC,沒有保留原樣的第二份。`tenv.notes` 的鍵、`_drift_list` 快取也都是 NFC。規格把它寫成既有物件,不是「要新寫」。要原樣路徑得改 `_nodehome_list` 或另外列樹(precedent:`_nodehome_name_status(norm=False)`)。
3. 例子:Linux 上的 CI,筆記檔名在 git 裡是 NFD。`git log -- ":(literal)<NFC 路徑>"` 不匹配,提交清單為空。清單為空時規格沒有說算「工作目錄裡還沒提交」(判不了)還是「那篇不存在」(正常停);兩種讀法的後果不同。
4. 查證:file: `scripts/lumos:26196-26230`(尤其 `path = nfc(os.fsdecode(p))`)、`scripts/lumos:26438`(`norm=False` 的 precedent 在別的函式)。

**C5 §2.5/天花板 2:改名與拆篇時「寫下時就已成立」的標記說得比查到的強**
severity: minor
blocking: 否 — 規格在天花板 2 已承認,但輸出文字沒有保留這個不確定,屬 UI 層的過度宣稱
引句:「筆記改過名或拆過篇,找到的是改名後那一版;在側分支寫下再合併的,算成合併那一版」

1. 位置:〈做法〉2.1、2.5、S5,天花板 2。
2. 問題:r2 把標記裡的「從沒提醒過」拿掉,理由是「側分支、改名、拆篇時這句話說得比查到的強」。但保留下來的「寫下時就已成立(提交 xxxx)」在同一批情境下一樣說得比查到的強,而且在改名時是可偵測的:`git log -- 路徑` 的最舊一筆在 `git diff-tree -M` 下是 R 狀態。
3. 例子:提交 1 建 `Projects/X.md`,內含 `[when-file:src/a.py]`(a.py 還沒有,條件不成立);提交 2 加 `src/a.py`;提交 3 把筆記 `git mv` 成 `Projects/Y.md`。`git log --first-parent HEAD -- Projects/Y.md` 只回提交 3(新增),該版條件已成立 → scan 標「寫下時就已成立(提交 3)」,事實是寫下時(提交 1)不成立。S5 還特地用「寫下時還不成立、後來才成立的 應 不標」當驗收,這個情境恰好繞過它。
4. 查證:實驗未跑 git 歷史(規格 §2.3 描述的演算法本身決定結果);`git log --first-parent` 加字面路徑不跟隨改名是 git 的行為。

**C6 §2.5 說「照 `_drift_prev_ack_line` 的呈現」,而那段呈現只印在未表態的列底下,與「已表態的照樣標」矛盾**
severity: minor
blocking: 否 — S5 有「已表態的 應照標」這條驗收,測試會抓到,但照模型抄會先做錯
引句:「照既有「先前表態」那行的呈現(`_drift_prev_ack_line`),另起一支 `_drift_born_line` 印在那條發現底下」

1. 位置:〈做法〉2.5。
2. 問題:`_drift_scan_print` 裡 `_drift_prev_ack_line` 只在 `if not acked:` 區塊內印。本案的核心動機正是「表態把它藏起來」,所以 born 行必須在已表態的列也印。若照 `prev_ack` 的位置抄(印在 `why` 之後、同一個 `if not acked` 內),已表態的就看不到。
3. 例子:一條已表態的生來成立回頭條件,文字輸出是 `src/x.md:12  REVISIT:...  (已表態)` 後面沒有下一行,而 `--json` 卻有 `born`,兩個輸出不一致。
4. 查證:file: `scripts/lumos:34990-34999`(`_drift_scan_print`,`(已表態)` 後只有 `if not acked:` 內才印 `why` 與 prev_ack)。

**C7 RETIRE-IF 的計數標準會被本案自己的文字污染,永遠數不到零**
severity: minor
blocking: 否 — 只影響撤除條件能不能觸發,不影響功能對錯
引句:「`when-gone` 兩個月零使用(數圖譜裡 `[when-gone:` 出現幾次),拿掉這個鍵」

1. 位置:稿首 RETIRE-IF ①、REVISIT:2026-12-03 那行。
2. 問題:〈做法〉3 要求在 `Systems/存量漂移守衛`、`Systems/筆記內容閘` 補 WHY 行,這兩行與本計劃筆記本身都含字面 `[when-gone:`(文件、範例、行內程式碼都算)。用字面子串計數,下限永遠是這幾處,「零使用」不可能成立。要的應是「行首 `REVISIT:[when-gone:` 或 `[retire:when-gone:` 且在可見文字裡的」那種計法,規格沒有定義。
3. 例子:2026-12-03 有人跑 `grep -r '\[when-gone:' docs/` 得到數十筆,RETIRE-IF ① 因而不會被判成立,即使真正的使用是 0。
4. 查證:file: `docs/lumos-toolchain-knowledge/Projects/回頭條件消失式與生來成立_計劃.md`(本檔 §1、§3、審計修正紀錄皆出現)。

**C8 效能數字低估:每個往回查的提交建樹加讀語料實測約 2 秒,20 條約 40 秒,吃掉 60 秒預算的大半;而且「每個不同提交建一次」與「判完那一條就丟」互相牴觸**
severity: minor
blocking: 否 — 有預算與 20 條上限擋住,最壞是標「判不了(超過預算)」
引句:「每個不同的寫下時提交建一次樹與圖譜,判完那一條就丟掉、不留快取」

1. 位置:〈做法〉2.4、〈實務隱患〉效能。
2. 問題:規格引用「建一次圖譜約 0.19 秒」,但判定要的 `_drift_probe_tree` 加不帶路徑的 symbol/test 要讀整份程式語料。我在這個 repo(約 600 篇筆記)對最近 10 個提交各做一次 `_drift_tree_env` + `_drift_probe_tree` + `tree.one("symbol", "cmd_drift_scan")`,每個 1.74 至 2.16 秒(合計 19.4 秒)。另外「每個不同提交建一次」暗示按提交去重,「判完那一條就丟掉」又說每一條各建;兩條共用同一個寫下時提交時,是建一次還是建兩次,規格沒定。
3. 例子:同一篇有 20 條成立的條件、各自生在不同提交且帶不帶路徑的 symbol,約 40 秒,且排在原本評估之後,前面若已花掉 30 秒,後段全標「超過預算」。
4. 查證:實跑的指令是載入 `scripts/lumos` 後呼叫 `_drift_tree_env`、`_drift_probe_tree`、`tree.one`,輸出見上;file: `scripts/lumos:32150-32170`(`_drift_list` 快取上限 8,超過就整個清)。

**C9 §1.5 對「列鍵的文件」的盤點不準:SKILL.md 沒有列鍵,CLAUDE.md 與 AGENTS.md 的注入區塊沒提,「四種鍵」的數目字會過期**
severity: minor
blocking: 否 — 守衛測試與 `t_graph_discipline_negation_revisit_source` 會紅,照訊息可修
引句:「`skills/lumos-project-notes/commands/03-寫回圖譜.md`、`skills/lumos-project-notes/reference.md`、`skills/lumos-project-notes/SKILL.md`、注入消費專案紀律區塊的範本 `scripts/templates/graph-discipline.md`」

1. 位置:〈做法〉1.5。
2. 問題:
   - `SKILL.md` 只在第 73 行用 `[when-file:路徑]` 當範例,並說「四種鍵怎麼選見 commands/03」,沒有列出四個鍵。規格卻要求漂移守衛測試掃它並「都要提到 `_PROBE_KEYS` 的每個鍵」,等於逼它新增一份列表,與現況「指向 03」的分工不一致。
   - 範本 `graph-discipline.md` 第 50 行的列鍵句也同時存在於本 repo 的 `CLAUDE.md` 第 52 行與 `AGENTS.md` 第 53 行(注入區塊)。`t_graph_discipline_negation_revisit_source` 的 ① 要求兩份注入區塊與範本一致,改範本後必須重新注入,規格只說「照既有規矩升範本版本」,沒提重新注入這兩個檔。
   - `03-寫回圖譜.md` 第 50 行寫「四種鍵」,加 `gone` 後變五種,該數目字沒列在要改的地方。
3. 例子:實作者改了範本與 03、reference,沒重注入 CLAUDE.md、AGENTS.md → `t_graph_discipline_negation_revisit_source` ① 紅;或照字面去改 SKILL.md 卻找不到可改的列鍵句。
4. 查證:file: `skills/lumos-project-notes/SKILL.md:73`、`scripts/templates/graph-discipline.md:50`、`CLAUDE.md:52`、`AGENTS.md:53`、`skills/lumos-project-notes/commands/03-寫回圖譜.md:50`、`scripts/test_lumos.py:62416`。

**C10 §1.2 末段關於 RULE 撤除條件路徑的前提不成立,而且 RULE 與 REVISIT 兩條路對字串的可寫範圍其實不一致**
severity: minor
blocking: 否 — 多出的檢查是多餘而非錯誤,不可寫的字串屬於極少數
引句:「在筆記形狀擋的回頭條件檢查(`_ns_revisit_violations`)與格子撤除條件檢查(`_slot_retire_err` 的呼叫端)看**原文**報「條件寫錯」」

1. 位置:〈做法〉1.2 末段、S4、天花板 4。
2. 問題:
   - 前提錯:RULE 的 `[retire:]` 值經 `slot_parse` 取出時保留原樣反引號(`slot_parse` 不剝反引號,只是括號計數時把反引號段當字面)。所以 `_slot_retire_err` 與 `_retire_lines` 的 `_probe_parse("[" + 值 + "]")` 拿到的就是含反引號的原文,只要 `_probe_gone_err` 檢查反引號就會觸發;只有 REVISIT 那條路(`_probe_lines`/`_ns_revisit_cond_viol` 用 `_strip_inline_markup` 後的文字)才被剝。S4 說撤除條件「照 REVISIT 那條路報錯」的描述會讓實作者在不需要的地方多加一支原文檢查。
   - 不一致:`slot_parse` 對值裡不成對的 `[` 報「值裡的方括號要成對,或把值用反引號包起來」,而 gone 又禁止反引號。字串含單獨的 `[`(如 `foo[`)在 REVISIT 能寫(`_PROBE_TOKEN_RE` 只排除 `]` 與換行),在 RULE 撤除條件完全寫不出來。這與同一段「RULE 撤除條件與 REVISIT 兩條路的寫法要求一致」矛盾,天花板 4 也沒列 `[`。
3. 例子:`[retire:when-gone:a.py::foo[]` → 實跑 `slot_parse` 回 `('retire', 'when-gone:a.py::foo[]', '值裡的方括號要成對,或把值用反引號包起來')`;而 `REVISIT:[when-gone:a.py::foo[][by:2026-12-31] x` 的 `_PROBE_TOKEN_RE` 可以收下 `foo[`。
4. 查證:file: `scripts/lumos:3812-3836`(`slot_parse`)、`scripts/lumos:3866-3891`(`_slot_retire_err`)、`scripts/lumos:32030-32036`(`_retire_lines`)、`scripts/lumos:368-379`(`_strip_inline_markup` 只剝反引號)。

## 已讀,無 finding 的節

- 稿首摘要、白話、依據、PRIOR-ART 的現況引用(`_drift_tree_env`、`_drift_probe_line`、`t_drift_when_probes_evaluate_and_trigger` ⑨、`_nodehome_cat_blobs_capped`、`_git_is_shallow`、`_lens_git` 的 `binary`/`timeout`、`_drift_bad_note`、`_drift_prev_ack_line` 皆存在,簽名與規格用法相符)。
- 〈範圍〉。
- 〈做法〉1.1 寫法(`::` 切第一個、字串規矩;`_posix_norm` 已去尾斜線,`src/lib/` 不會變成永遠成立)。
- 〈做法〉1.3 評估(「在」的算法與 `_drift_disk_list`/`_nodehome_list` 的 `allp` 對得上:`allp` 含連結檔與子模組、工作目錄模式 `lexists` 濾掉 sparse 未拉下與未暫存刪除;`_read` 先解碼確實會把 Big5 變亂碼,另存位元組快取的理由成立)。
- 〈做法〉1.4 的候選篩選(`touched` 含改名兩端、刪除路徑,前綴判斷可行;`_drift_probe_judge` 的 old/was 轉變邏輯對 gone 照舊成立)。
- 〈做法〉2.1、2.2 的規則本身(連續一世、只沿主幹、兩行同標記判不了、淺層與 partial clone 不往回查)。
- 〈實務隱患〉的併發、回滾、相容、跨環境、已排除項;〈回退〉;〈天花板〉1、3、5、6、7;〈審計修正紀錄〉。
- 驗收條款 S1、S6、S7 的敘述與做法一致。

最嚴重 severity 是 major,blocking 共 3 條(C1、C2、C3)。
