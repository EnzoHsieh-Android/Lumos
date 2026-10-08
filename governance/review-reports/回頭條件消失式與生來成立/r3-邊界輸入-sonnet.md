severity: major

# 第 3 輪(最終輪)邊界輸入席審查

審查對象:`/tmp/回頭條件消失式與生來成立-r3.md`。程式碼對照:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw`(唯讀)。下文程式引用的 file 都指這個 repo 的 `scripts/lumos`。前兩輪已修好的項目(`-S` 找錯提交、資料夾判消失、Big5 經替代字元誤判、合併提交交錯、`_nodehome_git` 無逾時等)不重報。我另外在自己的臨時目錄 `/tmp/revB3-PIvL` 造了 NFD 檔名與 `log.follow` 的小 repo 做實驗。

## 各節掃描

- 檔頭(frontmatter、summary、PRIOR-ART、RETIRE-IF、REVISIT):已讀,無 finding。`_drift_tree_env`、`_drift_probe_line`、`drift scan --at` 皆存在;`lands_in` 兩篇與 related 三篇存在於圖譜。
- 範圍:已讀,無 finding。
- 做法 1(`when-gone`):見 B3、B6、B7、B8、B11、B12。
- 做法 2(寫下時就已成立):見 B1、B2、B4、B5、B9、B10。
- 做法 3(說明與同步):見 B12。
- 實務隱患:風險類逐類答覆見文末。
- 驗收條款:見 B3(S5 與現行輸出結構衝突)、B6(S3 缺 `a\..\x` 與字串兩端空白的案例)、B12。
- 回退、天花板:已讀,無 finding(天花板 5 與 B7 的補充有關,不重報)。
- 審計修正紀錄:已讀,無 finding。

---

**B1 往回查用的「原樣路徑」在程式裡不存在,NFD 檔名的筆記整段查歪**
severity: major
blocking: 是 — 照字面實作時,規格指名的資料來源不存在;自行改用 NFC 路徑,git 讀不到,而且失敗被當成「那篇不存在」的正常停
引句:「路徑用 git 列樹時的原樣路徑(`_nodehome_list` 的原樣那份,不是 NFC 後的)」
1. 位置:做法 2.3「提交清單」。
2. 問題:`_nodehome_list` 只回兩份東西,`files` 與 `allp`,兩份的鍵都是 `nfc(os.fsdecode(p))`;`oids` 的鍵也是 NFC。程式裡沒有「原樣那份」。規格要靠它讓 `:(literal)<路徑>` 對得上 git 裡存的位元組,這個前提不成立。「每一版的筆記內容」那步也一樣:`<提交>:<路徑>` 只能用 NFC 組,沒有該提交的內容編號可用。`_drift_cat` 的註解寫過這個坑,現有補法是列整棵樹取編號,而規格要往回走 N 個提交,每個提交列一次樹的成本不在規格裡(`_drift_list` 快取上限 8)。
3. 例子:筆記檔名是 NFD(Linux 上 `café.md` 存成 `cafe` 加組合重音)。`git log --first-parent --format=%H <起點> -- ":(literal)café.md"`(NFC 路徑)輸出空字串;`git cat-file -s HEAD:café.md`(NFC)回 128 `exists on disk, but not in 'HEAD'`。規格沒定義「提交清單是空的」怎麼辦。若實作者把讀不到的版本一律當「那篇不存在 → 這一世的開頭就是它的下一版」(2.2 第二點),那整條往回查就停在起點,標出「寫下時就已成立(提交 <起點短碼>)」:一個錯的肯定句,不是「判不了」。
4. 查證佐證:file: `scripts/lumos:26196-26233`(`_nodehome_list`,26220 行 `path = nfc(os.fsdecode(p))`);file: `scripts/lumos:32186-32193`(`_drift_cat` 註解:樹清單把路徑轉成 NFC,用路徑讀永遠讀不到);實驗 `/tmp/revB3-PIvL/r`(`core.precomposeunicode=false` 下的 NFD `café.md`)。
5. 修法方向:往回查的路徑與讀取要明講怎麼取 git 的原始位元組路徑(例如另跑 `ls-tree -z` 取原樣路徑,或對每個提交用 `git log --raw -z` 帶出編號),並規定「提交清單為空、或起點版本讀不到這篇」一律判不了,不准落進「那篇不存在」。

**B2 規格要區分「那篇不存在」與「超過上限」,但指定的讀取函式把兩者都回成 None**
severity: major
blocking: 是 — 超過單篇上限的舊版本被當成「那一版沒有這篇」,這一世開頭被標在錯的提交
引句:「讀不出、超過單篇大小上限、不是嚴格 UTF-8 → 判不了」
1. 位置:做法 2.2 第二點與做法 2.3「每一版的筆記內容」(`_nodehome_cat_blobs_capped` 批次讀,總量上限 32 MiB)。
2. 問題:`_nodehome_cat_blobs_capped` 對「超過 max_bytes」寫 `res[i]=None`;`_nodehome_cat_blobs` 對「該提交沒有這個路徑」(`missing`)也回 None。同順序的 list 裡兩種 None 無法分辨。整批失敗才回整個 None,跟 list 裡的 None 又是另一回事。r2 修正紀錄寫「原稿把三種 None 混在一起」,r3 的呼叫法仍然是混的。規格要的「總量上限 32 MiB」也要先拿到全部大小再加總,`_nodehome_cat_blobs_capped` 內部只做單篇上限,規格沒說要另外呼叫 `_nodehome_cat_sizes`。
3. 例子:某篇筆記有一版被貼了 3 MB 的 log,超過單篇上限(假設上限 1 MB)。往回走到那一版,函式回 None。規格 2.2 說「不存在 → 這一世的開頭就是它的下一版」,實作者拿到 None 沒法判斷是哪一種。若當成不存在,這一世開頭被誤標在那一版的下一版,後面照常標「寫下時就已成立(提交 <短碼>)」。
4. 查證佐證:file: `scripts/lumos:26527-26540`(`_nodehome_cat_blobs_capped`);file: `scripts/lumos:26578-26591`(`_nodehome_cat_blobs` 的 `missing / ambiguous` 回 None);file: `scripts/lumos:26508-26524`(`_nodehome_cat_sizes` 才分得出「有沒有物件」與大小)。
5. 修法方向:規格改成先呼叫 `_nodehome_cat_sizes`(None=不存在、數字=大小)再自行決定讀不讀,總量也在那一步加總;或明寫新函式。

**B3 已表態的發現照現行輸出結構根本不會印出 born 那一行**
severity: major
blocking: 是 — 整份計劃要解的情境(表態後看不出生來就成立)在文字輸出上不會被解到
引句:「呼叫點在 `cmd_drift_scan` 拿到 `_drift_probe_scan` 的發現之後」
1. 位置:做法 2.5(另起 `_drift_born_line`,照 `_drift_prev_ack_line` 的呈現,印在那條發現底下)、S5「已表態的 應 照標」、WHY「表態後就再也看不出」。
2. 問題:`_drift_scan_print` 對每一列先印路徑與原文(已表態的後面加 `(已表態)`),然後 `if not acked:` 才印 why 與 prev_ack 那行。規格說「照既有先前表態那行的呈現」,照字面把 `_drift_born_line` 印在 prev_ack 旁邊,就落在 `if not acked:` 裡面,已表態的一律不印。而已表態正是本案動機(WHY 第一句、白話第二段)。JSON 輸出沒這問題(`dict(f, acked=...)` 會帶 born),只有文字模式。
3. 例子:一條生來成立的舊行已表態照留。`lumos drift scan` 文字輸出只有一行 `path:12  REVISIT:[when-file:...]  (已表態)`,沒有任何「寫下時就已成立」。S5 的測試若只驗 `--json` 會是綠的,文字模式的缺口沒人守。
4. 查證佐證:file: `scripts/lumos:34950-34955`(`print(... + ("  (已表態)" if acked else ""))`、`if not acked:`);file: `scripts/lumos:34893-34925`(`cmd_drift_scan` 先 `_drift_split_acked` 再印)。
5. 修法方向:規格要明寫 born 行印在 `if not acked:` 之外(或已表態的另一條印法),並讓 S5 同時驗文字與 `--json`。

**B4 `_probe_parse` 沒列進「逐一列出」的名單,`a\..\x.py` 會在 `when-gone` 重新通過**
severity: major
blocking: 是 — 已修過一次的路徑規矩洞,在新鍵上以另一種寫法重現,而且 S3 的測試案例碰不到
引句:「`_probe_value_err`:`gone` 走新寫的 `_probe_gone_err`(路徑規矩、字串非空、`..` 與 `/` 開頭照 file)」
1. 位置:做法 1.2 的函式清單(號稱 r2 補齊「逐一列出」)與 S3。
2. 問題:`_probe_parse` 先做 `val.replace("\\", "/") if k in ("file","symbol","test") else val` 再第一次驗,這是代碼審 r3 為了 `a\..\x.py` 加的(註解寫得明白)。清單沒列 `_probe_parse`,`gone` 不在那個 tuple 裡,第一次驗拿到的是沒轉過斜線的原文。`_probe_bad_path` 用 `/` 切段,`a\..\x.py` 切不出 `..` 段 → 第一層放行。接著 `_probe_norm_value` 會 `_posix_norm` 轉斜線並 `normpath`,結果 `x.py`;第二次驗(驗的是 `x.py`)也放行。同樣的路徑寫成 `a/../x.py` 會被擋。規格說「反斜線轉斜線與 NFC 正規化只做在路徑那段」,但整套反斜線預處理在 `_probe_parse`,沒人被指派去改。
3. 例子:`REVISIT:[when-gone:src/a\..\x.py][by:2027-01-01] ...` → 提交時不報「條件寫錯」,實際評估的路徑變成 `src/x.py`(`posixpath.normpath('src/a/../x.py')` 是 `src/x.py`;我實跑確認 `a\..\x.py` 的 `..` 檢查為 False、正規化為 `x.py`)。S3 只寫了 `..\x` 這種開頭就變成 `../x` 的案例,測試綠但洞還在。
4. 查證佐證:file: `scripts/lumos:31979-31986`(`_probe_parse` 的 replace 與兩次驗);file: `scripts/lumos:428-434`(`_posix_norm`);file: `scripts/lumos:31945-31954` 與 `scripts/lumos:31910-31926`。
5. 修法方向:清單加上 `_probe_parse`(把 `gone` 的路徑那段先轉斜線再驗),S3 補 `a\..\x.py` 與 `a\b\..\..\x.py` 兩個案例。

**B5 重複條件標記只在被掃的那一版檢查,歷史版本裡複製出來的第二行會被當成同一條,誤標到更早的提交**
severity: major
blocking: 是 — 會輸出一個肯定的錯誤歸因(提交 <短碼>),不是判不了
引句:「被掃的那一版裡這篇有兩行以上條件標記一樣 → 判不了(分不出是哪一行;設計審 r2 正確性席)」
1. 位置:做法 2.2 第一點與 2.1(「連續都還有這一條」)。
2. 問題:「兩行標記一樣」的防呆只看被掃的那一版。往回走的每一版只問「有沒有這一條」,沒定義「有兩行時算有」或「有兩行時停」。複製貼上同條件的第二行是常見寫法(同一支檔多個待辦)。
3. 例子:v1 寫了行 A,標記 X(條件已成立)。v5 複製一行 B,標記同樣 X。v7 刪掉 A。HEAD(v8)只剩 B,被掃那一版沒有重複,不觸發判不了。往回走:v7 有 X(B)、v6 有 X(A 與 B)、…、v1 有 X(A)→ 連續有,一路走到 v1 → 對 B 標「寫下時就已成立(提交 v1)」。B 實際寫在 v5。反過來 A、B 同在 v1–v4、v5 刪 A 也一樣。
4. 查證佐證:file: `scripts/lumos:32565-32570`(`_drift_probe_old` 的「同一條」是對標記取 tuple 集合比對,只回有沒有,沒有計次);既有先例也是「有沒有」,所以規格才必須自己加計次規則。
5. 修法方向:往回走的每一版都數同標記的行數,數量變化(0→1、1→2、2→1 都算)一律停並標判不了,不要跨過去。

**B6 字串兩端空白的處理有兩種讀法,S3 沒釘**
severity: minor
blocking: 否 — 兩種讀法都能實作,但會得到不同的評估結果,而且要靠作者猜
引句:「字串:照字面、分大小寫,去頭尾空白後不能是空的(帶了 `::` 就要有字串)」
1. 位置:做法 1.1 的「字串」規則與 `_probe_norm_value` 的「字串原樣」。
2. 問題:「去頭尾空白後不能是空」只規定驗證用的 strip;「字串原樣」、「照字面」又說比對不動。沒說比對時是否 strip。現有 `symbol` 的 `_drift_cond_split` 會 `name.strip()`。整個值已被 `_probe_parse` 的 `.strip()` 去了最外端,但 `::` 後的前導空白不會被去掉。
3. 例子:`[when-gone:src/a.py:: time.time()]`(冒號後有一格空白,很自然的寫法)。照「字面」比對的是 `" time.time()"`,檔裡 `x=(time.time())` 找不到 → 推送時立刻判成立,被點名「條件已經成立」。照 strip 比對的是 `time.time()`,找得到,不成立。
4. 查證佐證:file: `scripts/lumos:32195-32199`(`_drift_cond_split` 對路徑與名稱都 `strip()`);file: `scripts/lumos:31935-31939`(`_probe_norm_value` 現有 symbol 分支 `name.strip()`)。
5. 規格要明寫比對是否 strip,並在 S3 補 `:: x` 與 `::x  ` 兩個案例。

**B7 磁碟模式列檔對 NFD 與 gitignore 的失敗方向,在 `when-gone` 上從「不響」翻成「誤響」**
severity: minor
blocking: 否 — 既有列檔行為,但新鍵把後果從靜默變成誤報,規格天花板沒寫
引句:「工作目錄模式的 scan 照工作目錄看「在不在」:sparse-checkout 沒拉下來的檔、還沒暫存的刪除都算消失」
1. 位置:做法 1.3「工作目錄模式」與天花板 5。
2. 問題:`_drift_disk_list` 用 `os.path.lexists(base / nfc路徑)` 過濾。在檔名位元組保留 NFD 的檔案系統(Linux ext4,git 沒開 `precomposeunicode`),`lexists(NFC)` 是 False → 該檔從 `files` 與 `allp` 都被丟掉。另外 `ls-files --others --exclude-standard` 不含 gitignore 的檔,磁碟上存在的 build 產物或生成檔也不在清單裡。
3. 例子:`[when-gone:docs/生成/café.json]`,檔實際在磁碟上(NFD 位元組)。對 `when-file` 這種錯誤是永遠不響(靜默);對 `when-gone` 是立刻成立,scan 列成「條件已經成立,該處理了」,born 還會一路往回查標「寫下時就已成立」。字串部分也一樣:字串用 NFC 打、檔內容是 NFD,`in` 比對找不到 → 成立。規格只對路徑做 NFC,對字串與檔內容都沒有一句話。
4. 查證佐證:file: `scripts/lumos:32132-32147`(`_drift_disk_list`);file: `scripts/lumos:391-398`(`_nfc_child` 說明「磁碟上可能是 NFD(Linux 不幫忙正規化)」);file: `scripts/lumos:32187-32192`。
5. 天花板補一條:磁碟模式遇 NFD 檔名與 gitignore 檔,`when-gone` 會誤判成立;字串不做 NFC 正規化,檔內容與字串的正規化形式不同時永遠找不到。

**B8 帶字串判不了的新原因(NUL、LFS、非嚴格 UTF-8、不是一般檔),三處固定訊息仍說「git 讀不出程式檔或筆記」**
severity: minor
blocking: 否 — 推送被擋時說明講錯原因,但不影響判定結果
引句:「現在不是嚴格 UTF-8、判不了(推送判不了算要處理,點名時講原因)」
1. 位置:審計修正紀錄 r2 的例子與做法 1.3(帶字串)、做法 1.2 的函式清單。
2. 問題:清單只改 `_drift_row_unread`(點名哪支檔),沒列任何一處改訊息文字。三處訊息是寫死的 `"git 讀不出程式檔或筆記" + _drift_bad_note(...)`:`_drift_probe_check` 的判不了、`_drift_probe_candidates` 的判不了、`_drift_probe_scan` 的判不了。新原因不是 git 讀不出,是內容被判定不可比對。r2 的例子承諾了「講原因」,r3 的改動清單沒兌現。
3. 例子:`[when-gone:legacy.c::時間]`,legacy.c 是 Big5 → 推送時顯示 `legacy.c`、「git 讀不出程式檔或筆記: legacy.c」。作者去查 git 權限,實際該做的是換字串或改檔案編碼。
4. 查證佐證:file: `scripts/lumos:32489`、`scripts/lumos:32531`、`scripts/lumos:32676`(三處同一句固定文字)。
5. 清單加上「判不了的原因欄」要沿著 `unread_for` 往上傳到這三處,並在 S1 或 S2 驗訊息。

**B9 born 步驟需要的條件鍵與解析結果,發現(finding)字典裡沒有,規格沒說怎麼取得**
severity: minor
blocking: 否 — 可以實作,但規格留了一個介面缺口,實作者會各自發明
引句:「呼叫點在 `cmd_drift_scan` 拿到 `_drift_probe_scan` 的發現之後。」
1. 位置:做法 2.5。
2. 問題:`_drift_probe_scan` 回的發現只有 `kind、path、line、text、related、why`,沒有 `conds`。`text` 是 `ln.strip()` 的原文,但解析用的是 `_strip_inline_markup(ln)[0]` 之後的字串。born 要的是「條件標記」才能在歷史版本裡找同一條,得回頭重走 `_revisit_split` 加 `_probe_parse`,或是改 `_drift_probe_scan` 讓發現帶上 `conds`。規格兩者都沒說,而 `_drift_split_acked` 以後的 `done` 與 `left` 兩個清單是同一批物件(物件身分在 `_DRIFT_BOUND_KINDS` 以外不複製),如果走加欄位路線,`--json` 會把 `conds` 一併印出去,跟「`born` 欄形狀固定」沒對上。
3. 例子:實作者從 `text` 直接 regex 抽 `[when-...]`,就會抽到帶反引號 span 的原文,跟 `_probe_lines` 認的標記不一致(`` `x` `` 被剝掉),找不到「同一條」→ 全部誤判成寫下時是起點版本。
4. 查證佐證:file: `scripts/lumos:32671-32680`(`found.append({...})` 沒有 conds);file: `scripts/lumos:32010-32015`(`_probe_lines` 用剝過行內程式碼的字串解析)。
5. 規格補一句:born 用 `_probe_lines` 重抽,或發現多帶不輸出的內部欄位。

**B10 資源段與 2.4 對「每個提交建一次樹」與「判完就丟」互相矛盾,且同一篇的 N 條重複查同一段歷史**
severity: minor
blocking: 否 — 只影響效能與預算,結果不變
引句:「每個不同的寫下時提交建一次樹與圖譜,判完那一條就丟掉、不留快取」
1. 位置:做法 2.4 與實務隱患「效能」(「每個不同提交建一次樹與圖譜」)。
2. 問題:「每個不同提交建一次」與「判完那一條就丟掉」不能同時成立。同一批次建的筆記常有多條回頭條件,生在同一個提交;丟掉再建就是每條一次。`git log` 與整段歷史版本也是「每條成立的條件一次」,同一篇筆記上 10 條成立的條件會把同一段歷史讀 10 遍。`_nodehome_cat_blobs_capped` 與 `_nodehome_cat_sizes` 的逾時預設 60 秒,規格只把 `git log` 的逾時夾進預算,其餘批次讀不受預算約束,最壞一條就多出 `20 + 2×60` 秒,20 條就不是「吃 scan 既有預算」。
3. 例子:一篇筆記 10 條 `when-gone` 都已成立,歷史 60 版:`git log` 10 次、每次讀 60 個版本。建一個 0.19 秒的圖譜環境 10 次,不大;但在一個大 repo 上 `git log -- 路徑` 若逼近 20 秒上限,10 次就是整個預算。
4. 查證佐證:file: `scripts/lumos:26527`(`timeout=60` 預設)、file: `scripts/lumos:26508`;file: `scripts/lumos:32155-32170`(`_drift_list` 快取上限 8,也會被這個流程洗掉)。
5. 規格要選:按筆記路徑記憶 log 結果與版本內容(這一輪呼叫內),樹與圖譜按提交記憶、數量有上限,並把每次批次讀的 timeout 也夾進剩餘預算。

**B11 帶字串的目標檔沒有大小上限,且位元組快取疊在文字快取上會多佔一份記憶體**
severity: minor
blocking: 否 — 現有 symbol 條件也有同一個特性,但規格明講新增第二份快取,資源面沒提
引句:「所以 `_DriftProbeTree` 加一份位元組快取、走同一次批次讀」
1. 位置:做法 1.3 與實務隱患「效能」(「讀一支檔(同帶路徑的 symbol,有預讀)」)。
2. 問題:`_read` 對每支檔先讀整份 bytes、`_drift_decode` 成文字存進 `_text`。新增位元組快取後,同一支檔 bytes、解碼後的文字(含替代字元)兩份都駐留,目標檔幾百 MB(vendored 資料、舊的資料庫匯出)時是 2 到 3 倍。NUL、LFS 這些判不了的檢查其實只要頭一小段位元組。`_nodehome_cat_blobs`(非 capped)沒有大小上限。
3. 例子:`[when-gone:data/dump.sql::CREATE TABLE old_table]`,dump.sql 800 MB。scan 與推送判定都會整份讀進記憶體、解碼、再存位元組,尖峰約 2.4 GB,而一般 symbol 條件的路徑目標是程式檔,沒有這個量級。
4. 查證佐證:file: `scripts/lumos:32270-32290`(`_read` 內 `_drift_decode(...)`);file: `scripts/lumos:26543-26580`(`_nodehome_cat_blobs`)。
5. 規格補:帶字串的 `gone` 目標檔單檔上限(超過判不了),且位元組讀到後用完就轉成「結果」,不與解碼文字雙份留存。

**B12 同步清單漏列倉庫根目錄的 CLAUDE.md、AGENTS.md,以及文法的家**
severity: minor
blocking: 否 — 漂移守衛測試只掃規格列的四份文件,漏掉的兩份靠既有的範本同步機制補;但文件清單宣稱是「逐一」
引句:「文件裡列鍵的地方逐一改:`skills/lumos-project-notes/commands/03-寫回圖譜.md`」
1. 位置:做法 1.5。
2. 問題:`grep` 整個 repo 出現「when-symbol」且列鍵的位置還有 `CLAUDE.md` 第 52 行與 `AGENTS.md` 第 53 行(RULE 的效力一行,文字與範本 `scripts/templates/graph-discipline.md` 第 50 行相同),以及文法的家 `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md`〈做法〉第 0 節(規格自己在依據段說條件文法在那裡)。規格只寫「範本有改就照既有規矩升範本版本」,沒說根目錄這兩份是靠重新注入還是手改。守衛測試掃的「上面四份文件」也就不包含它們。
3. 例子:實作後只改了範本,根目錄 CLAUDE.md、AGENTS.md 仍寫「只收機器式:when-file、when-symbol、when-test、when-status」,下一個讀這個 repo 的 AI 照它寫 `[retire:when-gone:...]` 時會以為不可以。
4. 查證佐證:file: `CLAUDE.md:52`、`AGENTS.md:53`、`scripts/templates/graph-discipline.md:50`(都在 rw repo 根下);file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md`。
5. 規格補:根目錄兩份是否由注入更新(若是,測試要驗注入後相同),以及文法更新寫回哪一篇。

**B13 跨環境宣稱「本機與 CI 同一支判定」對 `log.follow` 設定不成立**
severity: minor
blocking: 否 — 我實驗後結果恰好相同(舊路徑不存在 → 停),但宣稱本身錯,設定一改就會有人誤以為是 bug
引句:「本機的外部差異與文字轉換設定不影響;本機與 CI 同一支判定。」
1. 位置:實務隱患「跨環境」。
2. 問題:`git config log.follow true` 時,`git log -- :(literal)y.md`(單一路徑)會跟著改名往回走:在 `/tmp/revB3-PIvL/r` 實測同一個路徑 follow=true 輸出 5 筆提交,follow=false 輸出 2 筆。提交清單長度因本機設定而不同。目前的流程碰到舊路徑會判「不存在 → 停」,所以結果碰巧一致;但「不受本機設定影響」的說法要靠這個巧合,規格沒寫出來,也沒加 `--no-follow` 或明確的旗標。
3. 例子:有人在本機設了 `log.follow=true`,debug 時看到「提交清單比預期長」。
4. 查證佐證:實驗 `/tmp/revB3-PIvL/r`;file: `scripts/lumos:39854-39868`(`_lens_git` 不清理 git 設定)。
5. 規格改成明說「提交清單含改名前的提交也沒關係,因為舊路徑讀不到會停」,或加 `--no-follow`。

---

## 實務隱患鏡頭逐類答覆(邊界輸入立場)

- 併發:無新 finding。只讀 git 物件與工作目錄檔,不寫帳(`cmd_drift_scan` 讀指令不寫帳是既有決定)。例外:掃描當中有人 commit 或 `git gc`,`git log` 與後續 `cat-file` 之間對不上 → 讀不到會回 None,又會撞 B2 的「不存在」誤判,B2 修了就一併解。
- 效能與記憶體:見 B10、B11。往回查的最壞成本(大 repo 上 `git log -- 路徑`)由 `min(剩餘預算, 20)` 夾住,方向是對的;批次讀取的逾時沒夾,見 B10。
- 回滾:無 finding。還原提交後 `when-gone` 變成「不認得的條件鍵」,與規格描述相符(`_probe_value_err` 的第一支檢查就是 `k not in _PROBE_KEYS`)。
- 誤擋與繞過:誤擋見 B6、B7(新寫的 `when-gone` 在字串兩端空白與 NFD 檔名下被判成立而擋推送);繞過沿用表態,規格已寫明。B1、B2、B5 是「標錯」,不是擋,但會讓表態者以為已確認過歷史。
- 相容:新鍵只在新版認得;`lumos update` 之前舊版不認得是規格已寫的事。B12 說的是文件漏同步。
- 跨環境:見 B13、B7。
- 金流、對外送出、不可逆:無+只讀筆記與 git 物件,不呼叫網路(partial clone 不往回查已寫);同意規格原判。
- 守衛面:推送判定是會擋的閘,B6 與 B7 會讓新鍵多擋;B8 只影響說明。讀不準就判不了的設計原則是對的,但 B1、B2、B5 三條在規格自己定義的路徑上把「讀不準」寫成了「肯定」,違反這個原則。

## 極端輸入對照表(各案的結論)

- 字串含 `::`:規格已定第一個切,與現有 `symbol` 最後一個切方向相反,測試 S3 有案例;已讀,無 finding。
- 全形冒號、全形空白:沒有 `::` 則整串當路徑;推送時被點名並附打錯字提示,規格已寫;無 finding。
- 資料夾、符號連結、子模組:規格已定,在=不成立;帶字串時判不了;無 finding。
- NFD 檔名:見 B1(筆記路徑)與 B7(目標檔)。
- 二進位與超大檔:NUL、LFS 已定;大小上限見 B11。
- 字串跨行:regex 與規格都擋換行;無 finding。
- 筆記改名:天花板 2 已寫「找到改名後那一版」;但 B1 的 NFD 情況會讓改名之外也發生同樣效果,不重報。
- 歷史上寫過又刪又寫:見 B5(重複行計次)。
- 淺層 clone、partial clone:規格已定整段不往回查;無 finding。
- scan 預算剛好用完:`git log` 的逾時是 `min(剩餘, 20)`,剩餘為 0 或負時 `subprocess.run(timeout<=0)` 會立即逾時 → `_lens_git` 回 None → 判不了,方向正確;其餘批次讀見 B10。

最嚴重 severity:major;blocking 共 5 條(B1、B2、B3、B4、B5)。
