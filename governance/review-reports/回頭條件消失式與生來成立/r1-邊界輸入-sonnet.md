severity: major

審稿範圍:整份 spec 逐節讀完,對照 rw 工作樹的 scripts/lumos 與 scripts/test_lumos.py。交叉引用目標(Systems/存量漂移守衛、三篇相關計劃、skills/lumos-project-notes/commands/03-寫回圖譜.md、`t_drift_when_probes_evaluate_and_trigger` 的 ⑨、〈天花板〉第 2 條、`_drift_probe_line`、`_drift_split_acked` 等)都存在。下面只列邊界輸入找出的洞。

**B1 「第一次出現這一行」不等於「寫下時」,改過、搬過、刪了又寫的行會被誤標「從沒提醒過」**
severity: major
blocking: 是 — 輸出的是一句肯定的事實宣稱(「寫下時就已成立,從沒提醒過」),照字面實作會對一批合法的舊行說錯,而且表態過的也照標,使用者會據此改決定。
引句:「找第一次出現這一行的提交(只看這一篇的歷史;筆記改過名就在改名後的第一個提交找到,天花板 2)」

1. 位置:〈做法〉2.1,連動〈天花板〉2。
2. 問題:`git log -S<整行原文>` 找的是「這一串字第一次出現」,不是「這個條件第一次被寫下」。以下輸入都會把「第一次出現」落在後來的提交:
   - 行被改過字(追加 `[by:]`、改期限、改說明、`lumos drift fix` 或 regen 重寫整行):新字串的第一次出現是改動那一版。
   - 筆記搬到別的資料夾、圖譜資料夾改名:`git log` 預設不追改名,改名那個提交對這個路徑就是整篇新增。
   - 同一行寫過、刪掉、很久以後貼回來(使用者問的「又刪又寫」):`--reverse` 取到最早那一次,判的是舊的那次寫入,跟現在這一行無關。
3. 例子:二〇二六年三月寫下 `REVISIT:[when-file:src/x.py][by:2026-12-31] 補測試`,條件等了半年,九月 src/x.py 出現(條件成立)。十月有人把期限改成 2027-03-31。照字面實作,scan 找到十月那個提交,在它的樹上 src/x.py 已在 → 標「寫下時就已成立(提交 abc1234),從沒提醒過」。實際上它等了半年、正常運作。〈天花板〉2 自己承認「會標成那個提交時的判定」,但標記文字是肯定句,不是「判不準」。
4. 查證:`_probe_lines` 回的 `tx` 是 `ln.strip()`(`scripts/lumos:32638` 附近的 `out.append((i, ln.strip(), _probe_parse(rest)))`);改字後的整行與舊行是不同字串。`git log` 預設不加 `-M`/`--follow`,路徑改名在 `-S` 下就是新增。⚠ 搬資料夾在本 repo 是常態(Projects 歸檔),不是罕見事。
5. 缺口:spec 沒有「這一行是從哪個舊版本演變來的」的判定,也沒有把標記降級成「最早在這一版看到的字串」的措辭。

**B2 `when-gone` 指到資料夾、符號連結、子模組時,寫下當下就永遠成立,而且沒有「指到資料夾」的警告**
severity: major
blocking: 是 — 新鍵最基本的路徑輸入(資料夾)讓條件永遠為真;scan 會把它列成「條件已經成立」,推送雖會擋但要等到推送,而且警告機制漏掉這個鍵。
引句:「`[when-gone:<路徑>]`——那支檔不在樹上就成立」

1. 位置:〈做法〉1.1、1.2。
2. 問題:`_DriftProbeTree.one` 的 file 分支是 `v in self.files`,而 `self.files` 只收一般檔:提交樹用 `_nodehome_list`,模式只收 100644/100755(連結 120000 與子模組 160000 明確排除);工作目錄用 `_drift_disk_list`,`is_file() and not is_symlink()`。所以「路徑不在 files 裡」包含資料夾、符號連結、子模組、拼錯的路徑——spec 把它們全部讀成「那支檔不在了」。
3. 例子:`[when-gone:src/legacy]`(`src/legacy/` 是資料夾,裡面還有三支檔)→ `src/legacy` 不在 files → 成立。`[when-gone:scripts/run.sh]` 而 `scripts/run.sh` 是符號連結(還在用)→ 同樣成立。
4. 查證:file: `scripts/lumos:26222`(`if mode in (b"100644", b"100755")`)、file: `scripts/lumos:32141`(`not (base / p).is_symlink()`)。既有 `when-file` 已經為此有「指到資料夾」警告:file: `scripts/lumos:32642`(`any(f.startswith(v.rstrip("/") + "/") ...)`),spec 的 `_probe_gone_err` 與〈做法〉都沒提要不要加同一種警告;而 `when-file` 的另一半(路徑不存在永遠不成立)在 `when-gone` 上翻成「永遠成立」,後果比 `when-file` 嚴重(正向鍵寫錯是靜默不提醒,消失鍵寫錯是立刻提醒錯)。
5. 缺口:要定義「樹上有沒有這條路徑」包含資料夾與連結,還是只認一般檔;`_drift_probe_row_problems` 要不要也對 gone 報資料夾。

**B3 反斜線正規化在 `when-gone` 上沒交代:不加會重開已修過的 `..` 繞過,加了會把字串部分的反斜線改成斜線**
severity: major
blocking: 是 — 兩種實作都出錯,而 spec 沒說選哪一種;字串帶反斜線(Windows 路徑、跳脫序列)是消失條件的典型內容。
引句:「`_probe_norm_value` 多一個 `gone` 分支呼叫它;字串去頭尾空白後不能是空的」

1. 位置:〈做法〉1.1、1.4。
2. 問題:`_probe_parse` 在驗值之前先對 `k in ("file", "symbol", "test")` 做 `val.replace("\\", "/")`,原因是代碼審 r3 發現 `a\..\x.py` 繞過 `..` 檢查。`gone` 的值是「路徑::字串」一整串,spec 沒說這行要不要加 `gone`:
   - 不加:`[when-gone:a\..\x.py]` 原文用 `/` 切不出 `..` 段,過關;之後 `_posix_norm` 把它轉成 `a/../x.py`,正規化後再驗一次會擋,但若 `_probe_norm_value` 的 gone 分支只對路徑做 `_posix_norm` 而第二次驗是對整串做,行為取決於寫法——spec 沒定。
   - 加:`[when-gone:src/a.py::C:\temp\x]` 的字串變成 `C:/temp/x`,檔裡的是 `C:\temp\x`,永遠對不上,條件寫下當下就成立。
3. 例子:`REVISIT:[when-gone:src/a.py::path\to\old][by:2027-01-31] ...`。照「統一加進 tuple」的最順手寫法,字串被改成 `path/to/old`,條件立刻成立,推送被點名「條件已經成立」,作者以為是 spec 的保險功能而表態照留(〈實務隱患〉繞過那一條)——條件從此永遠是死的。
4. 查證:file: `scripts/lumos:31982`(`val.replace("\\", "/") if k in ("file", "symbol", "test") else val`),file: `scripts/lumos:31975-31981` 的 r3 註解。
5. 缺口:要寫明反斜線轉換只套在路徑段(`_drift_gone_split` 之後),字串段原樣保留。

**B4 往回查沒有釘 git 的 rev 範圍與「沒進過提交的行」:`--at`、未提交的新行都會得到無意義的結果**
severity: minor
blocking: 否 — 結果是「判不了」或次要誤標,不改變發現本身。
引句:「找不到提交、git 失敗、超過預算 → 標「判不了寫下時成不成立」」

1. 位置:〈做法〉2.1。
2. 問題:`cmd_drift_scan` 有 `--at <提交>`(tenv 是那個提交的圖譜)。spec 的 `git log` 沒有帶終點 rev,預設走 HEAD:
   - `--at` 指到不在 HEAD 祖先裡的提交(別的分支):找不到,全部標判不了。
   - scan 預設看工作目錄,筆記裡剛寫還沒提交的行:也「找不到提交」,被標成「判不了」——其實是最明確的「還沒寫進歷史」,不是判不了。
3. 查證:file: `scripts/lumos:34912-34921`(`--at` 取 `sha`、`vault_rel` 以那個提交為準)。
4. 缺口:`git log` 要接 `sha or HEAD`;未提交的行要有自己的標示(或明講歸「判不了」)。

**B5 一行含 NUL 字元時,往回查會丟 ValueError 讓整個 scan 崩掉,spec 只處理「git 失敗」**
severity: minor
blocking: 否 — 要求輸入含 NUL 的筆記行;影響是 scan 整支中止而非誤判。
引句:「找不到提交、git 失敗、超過預算 → 標「判不了寫下時成不成立」」

1. 位置:〈做法〉2.1。
2. 問題:`-S<原文>` 把整行放進 argv。條件值的正則是 `[^\]\n]*`,NUL 能進來,`_probe_parse` 不拒收。實測 `_probe_parse("[when-file:a\x00b][by:2027-01-01]")` 回 `{'conds': [('file', 'a\x00b')], 'errs': [], 'bad': False}`;`subprocess.run(["git", ..., "-S\x00x"])` 丟 `ValueError: embedded null byte`。`_lens_git` 只 catch `(OSError, TimeoutExpired)`,ValueError 不在裡面。
3. 例子:某篇筆記有 `REVISIT:[when-file:src/a\x00.py]...`(貼上時夾到的控制字元),它的條件成立 → 進往回查 → 整個 `lumos drift scan` 以 traceback 結束,其他所有發現都出不來。
4. 查證:file: `scripts/lumos:39865`(`except (OSError, _sp.TimeoutExpired)`)。同一種輸入在既有路徑不會觸發,因為既有路徑沒把行原文放進 argv。
5. 缺口:往回查前要先檢查原文可當 argv(無 NUL),或 catch ValueError 並標判不了。

**B6 往回查的 git 指令沒有釘 textconv / 外部 diff / `-diff` 屬性,本機與 CI 會得到不同結果**
severity: minor
blocking: 否 — 結果是整批標「判不了」或不同環境不一致,不改變發現本身。
引句:「本機與 CI 同一支判定」

1. 位置:〈實務隱患〉跨環境。
2. 問題:pickaxe 受 `.gitattributes` 的 `-diff`/`binary`、`diff.<driver>.textconv`、`diff.external` 影響:筆記被標成 binary 時 `-S` 不比對(要加 `-a`),設了 textconv 的比對的是轉換後的文字。本機設定與 CI 不同,同一行得到不同的「第一次出現」。repo 已經為同類問題在 `_ns_diff` 釘過參數。
3. 例子:消費專案的 `.gitattributes` 有 `*.md -diff`(避免 PR 顯示雜訊),`git log -S` 對每篇都沒有命中 → 每一條成立的條件都標「判不了寫下時成不成立」,功能等於沒上線,也沒有警示。
4. 查證:file: `scripts/lumos:27360-27364`(`_ns_diff` 釘 `--no-ext-diff --no-textconv`,註解寫「本機與 CI 結果就不一樣」);同檔 `scripts/lumos:32396` 一帶的 diff 也有「標了 -diff 屬性的檔看不見新增行的坑」的註解(`_drift_probe_is_candidate` 說明)。
5. 缺口:要寫明加 `--no-ext-diff --no-textconv -a`(或等價)與 `-c` 關掉會影響輸出的設定。

**B7 淺層 clone 的偵測方式沒寫,而且〈實務隱患〉與〈做法〉對「淺層時怎麼辦」說了兩種話**
severity: minor
blocking: 否 — 意圖清楚(標判不了),缺的是偵測手段;repo 已有現成的偵測可借。
引句:「找到的「第一次出現」可能是淺層邊界,標成判不了寫下時成不成立(淺層時不往回查)」

1. 位置:〈實務隱患〉跨環境、〈天花板〉4、〈做法〉2.1。
2. 問題:同一句裡兩種動作——「找到後標判不了」與「不往回查」;〈做法〉2.1 的失敗清單(找不到提交、git 失敗、超過預算)也沒有「淺層」這一項。沒說怎麼知道是淺層:只靠「找到的提交是不是邊界」沒法判斷,因為淺層邊界提交在 `-S` 眼裡就是「整篇新增」,回傳一個完全正常的 sha。
3. 例子:GitHub Actions `actions/checkout` 預設 depth=1。CI 跑 `drift scan` 時 `git log -S` 唯一能回的就是那一個提交,在它的樹上所有現在成立的條件當然都已成立 → 每一條都被標「寫下時就已成立」。
4. 查證:file: `scripts/lumos:29473`、file: `scripts/lumos:30106`(兩處已用 `git rev-parse --is-shallow-repository`),spec 沒引用。
5. 缺口:要明寫用 `--is-shallow-repository`,並把「淺層」加進 2.1 的判不了清單。

**B8 工作目錄模式的檔案清單對 sparse-checkout 與未 stage 的刪除會讓 `when-gone` 當下成立,而往回查那一邊用完整提交樹**
severity: minor
blocking: 否 — 只影響特定 checkout 型態的 scan,且與既有 `when-file` 設計一致的方向(但對消失鍵是反向風險)。
引句:「路徑不在樹上就成立」

1. 位置:〈做法〉1.1 / 1.2、〈做法〉2.1。
2. 問題:scan 預設 `where="disk"`。`_drift_disk_list` 把「索引裡有但磁碟上不在」的路徑剃掉(`os.path.lexists`),所以 sparse-checkout 沒展開的目錄、或手動刪掉還沒 stage 的檔,在 disk 模式都算「不在」→ `when-gone` 成立;同一條在往回查那邊用完整提交樹看,檔在。結果:發現「條件已經成立」但「寫下時」那一版也看似成立或不成立,兩邊用的是不同口徑的樹。
3. 例子:巨型專案用 sparse-checkout 只展開 `app/`,筆記寫 `[when-gone:legacy/old.py]`:scan 說成立,實際上檔還在。
4. 查證:file: `scripts/lumos:32141`(`allp = [p for p in allp if os.path.lexists(base / p)]`)。⚠ 沒實跑 sparse-checkout。

**B9 往回查的 git 指令沿用 `_lens_git` 預設逾時 20 秒,不受 scan 剩餘預算約束**
severity: minor
blocking: 否 — 超出幅度有限(每條最多 20 秒),功能仍可用。
引句:「往回查吃 scan 既有的時間預算(`--budget`,預設照舊),排在本來的評估之後」

1. 位置:〈做法〉2.2。
2. 問題:`_DriftProbeTree._read` 讀檔時有把逾時夾進剩餘預算(`left = max(1, deadline - now)`),`_lens_git` 預設 `timeout=20` 不看預算。預算剩 1 秒時,下一條 `git log -S` 仍可跑 20 秒;N 條成立的條件各 20 秒。「超過預算就標判不了」的承諾因此是軟的。
3. 查證:file: `scripts/lumos:39854`(`timeout=20`)、file: `scripts/lumos:32279` 一帶 `_read` 的 `left` 計算。
4. 缺口:要寫明每次 `git log` 的 timeout 夾剩餘預算,並在每條前檢查是否已超過。

**B10 `when-gone` 字串的表達力邊界沒進〈天花板〉:`]`、跨行、反引號、NFC/NFD**
severity: minor
blocking: 否 — 都是寫的時候會被擋或提早成立,作者看得到;缺的是文件化。
引句:「不能含 `]` 與換行(既有標記的切法)」

1. 位置:〈做法〉1.1、〈天花板〉3。
2. 問題:
   - 字串含 `]`(`items[0]`、正規式字元類)寫不出來;〈天花板〉只列了「同義寫法」一種限制。
   - 一行回頭條件是單行,所以多行程式碼片段無法當條件字串。
   - `_probe_lines` 先用 `_strip_inline_markup` 剝掉反引號行內程式碼再解析;條件字串若被作者習慣性包在反引號裡,整個標記消失(整行變成「沒有條件標記」)。
   - 比對是 `_drift_decode(...)` 之後的原字串,沒有 NFC:筆記字串(macOS 貼上可能是 NFD)與檔案內容(NFC)對不上時,字串「不再出現」→ 條件寫下當下成立;路徑段有 `nfc`,字串段沒有。
3. 查證:file: `scripts/lumos:31759`(`[^\]\n]*`)、file: `scripts/lumos:32180-32183`(`_drift_decode` 只去 BOM)。

**B11 其他讀條件鍵/訊息的舊位置:`_slot_retire_err` 的錯誤訊息仍列四個鍵,與 S3「列出五個鍵」不一致**
severity: minor
blocking: 否 — 訊息文字過時,不影響判定。
引句:「RULE 的撤除條件 `[retire:when-gone:…]` 走同一支解析(`_retire_lines` 改寫成回頭條件標記再交給 `_probe_parse`),自動支援,不另寫。」

1. 位置:〈做法〉1.4。
2. 問題:撤除條件的值驗證還有另一支 `_slot_retire_err`(file: `scripts/lumos:3891`),末尾的「不是機器式(只收 when-file/when-symbol/when-test/when-status、度量、人裁)」是第二份鍵清單,spec 沒列進要改的地方,也不在 S3/S4 的守衛範圍;`_retire_lines` 已經是「改寫成條件標記再交給 `_probe_parse`」的現狀,不是這個案子新做的。同一檔的 file: `scripts/lumos:28371` 的 RULE 格式範例只舉 `when-file`,不用改。
3. 例子:把 `[retire:when-gone:x]` 寫成別的壞形狀,使用者看到的訊息還是舊四鍵。
4. 缺口:把該訊息納入要改的清單並加進 S3。

## 實務隱患鏡頭(逐類)

- 併發:無+為什麼——只讀 git 物件與工作目錄,不寫帳;scan 同時有人改檔,結果是「掃描當下」的快照,與既有 scan 相同。
- 效能:無(量過)——`git log -S` 限單一筆記路徑,本 repo 最熱的一篇(Systems/存量漂移守衛,17 個提交)毫秒級;`_drift_tree_env` 加 `_drift_probe_tree` 對 400 個提交之前的一版約 0.15 秒;成立的條件是個位數時沒有問題。唯一缺口是 B9 的逾時沒夾預算。
- 回滾:無+為什麼——「還原後 `when-gone` 變成不認得的鍵」的行為與 `_probe_parse` 的 `bad` 旗標一致(寫錯的條件不評估、scan 列成寫錯);已查 `_drift_probe_check` 的 `lines = [x for x in lines if x[3]["conds"] and not x[3]["bad"]]`。
- 誤擋與繞過:見 B2(資料夾/連結立即成立→推送被擋)、B3(字串帶反斜線立即成立→被擋後只能表態繞過)。
- 跨環境:見 B6、B7、B8。

最嚴重 severity 是 major,blocking 共 3 條(B1、B2、B3)。
