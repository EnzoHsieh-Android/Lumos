severity: major

# 通才審查報告(r1):回頭條件消失式與生來成立_計劃

審查範圍:整份 spec 逐節讀過;所有引用的既有函式、既有測試、連結目標都已開檔核對(`_probe_parse`、`_probe_value_err`、`_probe_norm_value`、`_drift_cond_split`、`_DriftProbeTree` 的 `one` / `prefetch` / `unread_for` / `_read`、`_drift_probe_one`、`_drift_probe_line`、`_drift_probe_cond_candidate`、`_drift_probe_check`、`_drift_probe_judge`、`_drift_probe_scan`、`cmd_drift_scan`、`_retire_lines`、`_drift_split_acked`、`_drift_exam_*`,以及三篇連結的計劃、`Systems/存量漂移守衛`、技能手冊 03 都存在)。「既有測試 `t_drift_when_probes_evaluate_and_trigger` ⑨」存在且內容吻合。

**U1 「寫下時就已成立」用整行原文做 `git log -S`,跟系統其餘地方「同一條=條件標記相同」的認定不一致,改動待辦文字會讓標記說謊**
severity: major
blocking: 是 — 第 11 項的核心產出(「從沒提醒過」)在常見操作下會標錯,等於把假話印進 scan 與 `--json`。
引句:「用 `git log --format=%H --reverse -S<那一行原文> -- <筆記路徑>` 找第一次出現這一行的提交」
1. 〈做法〉2.1。`-S` 找的是「這串字的出現次數第一次變動」的提交,拿的是整行原文(含待辦說明文字)。
2. 系統其餘地方認「同一條」是看條件標記,不看說明文字:`_drift_probe_old` 比的是 `tuple(pr["conds"])`;既有測試 ⑧「只改待辦文字仍是同一條、起點早就成立:不列」就是釘這個。
3. 例子:T1 提交寫下 `REVISIT:[when-file:src/a.py][by:2027-01-01] 補測試`(當時 src/a.py 還沒有,條件不成立);T2 加了 src/a.py,推送時點名「這次推送讓條件成立了」(提醒過);T3 有人把說明文字改成 `補測試與文件`。照字面實作,scan 對這行 `git log -S` 的第一個命中是 T3(舊文字不含新整行),T3 的樹上 src/a.py 已在 → 標「寫下時就已成立(提交 T3),從沒提醒過」。這句話是錯的:T2 提醒過,條件也不是 T3 寫下的。
4. 反方向也有:說明文字改成原文的子字串(刪尾字)時,舊版含新字串,`-S` 的計數不變,命中的是更早的提交,晚改的條件(例如 T3 同時改了條件值)被算成更早寫下。
5. 查證:`scripts/lumos:32562`(`_drift_probe_old` 比條件標記不比原文)、`scripts/test_lumos.py:55867`(⑧)、`scripts/lumos:32723`(表態鍵才用整行原文)。spec 沒有說明為什麼往回查要用整行原文而不用條件標記串。

**U2 往回查的輸入沒定義完整:筆記路徑的形式、`--at`、尚未提交的行**
severity: minor
blocking: 否 — 屬於可補的定義缺口,不改變設計方向。
引句:「`lumos drift scan` 對每一條「條件已經成立」的回頭條件(含已表態的;RULE 撤除條件不查」
1. 〈做法〉2.1 的 `<筆記路徑>` 沒說是圖譜內相對路徑還是 repo 相對路徑。`_drift_probe_scan` 發現裡的 `path` 是圖譜內相對路徑(例:`Systems/x.md`),直接丟給 `git log -- ` 什麼都找不到,要補上 `vault_rel`。圖譜資料夾改過名時要用 `_drift_vault_rel(root, sha)`(`cmd_drift_scan` 已為 `--at` 這樣做)。路徑含 NFD 存檔名的 repo 還要處理 NFC/NFD(程式碼多處註解已為此踩過坑),spec 沒提。
2. `cmd_drift_scan` 有 `--at <提交>`:此時 `tenv` 是那個提交的圖譜,但 spec 的 `git log` 沒說要從 `<提交>` 起算而不是 HEAD。非 HEAD 祖先的提交(其他分支)會找到不在該快照歷史裡的提交。
3. scan 預設讀工作目錄。剛寫、還沒提交的行(依本 repo 目前 `git status` 一堆未提交筆記就是常態)`git log -S` 必然找不到 → 照 2.1 標「判不了寫下時成不成立」。這種行的「寫下時」其實就是現在,答案是「成立=生來成立」,spec 把它跟「歷史查不到」混成同一個 unknown;S6 也只列「找不到提交或超過預算」。
4. 查證:`scripts/lumos:34893`(`cmd_drift_scan` 簽名與 `--at` 處理)、`scripts/lumos:34918`(預設 `"disk"`)、`scripts/lumos:31668`(`_drift_vault_rel`)。

**U3 「不在樹上就成立」的判準沒釘死:實作基準 `self.files` 只含一般檔,連結檔、子模組、資料夾、被忽略的檔都會立刻變「已消失」**
severity: minor
blocking: 否 — 新寫的會被推送時的「已經成立」擋下;只有存量與換成連結檔的情況會誤報。
引句:「`[when-gone:<路徑>]`——那支檔不在樹上就成立」
1. 〈做法〉1.1 / 1.2:`_DriftProbeTree.one` 的 file 分支是 `v in self.files`;`self.files` 來自 `_nodehome_list`,只收模式 100644/100755,連結檔(120000)與子模組(160000)不算;disk 模式還要 `is_file() and not is_symlink()` 並排除被 gitignore 的檔。
2. 例子:`[when-gone:docs/current]`(資料夾)或指到連結檔、被忽略的產物檔 → 一寫就「已消失」;原本是一般檔、後來改成 symlink 的 → 轉成立被點名,但檔還在。`when-file` 有「指到資料夾」的提示(`_drift_probe_row_problems`),spec 沒給 `when-gone` 對應的檢查。
3. 另一個文法陷阱:`when-symbol:名稱` 可以不帶路徑,`when-gone` 沒有「不帶路徑」的寫法,所以 `[when-gone:time.time()]` 會被當成路徑 `time.time()`(合法路徑)、立刻成立,錯誤訊息只會是「條件已經成立」,不會指出寫法錯。
4. 查證:`scripts/lumos:26222`、`scripts/lumos:32132-32147`、`scripts/lumos:32349`、`scripts/lumos:32660-32670`(file 指到資料夾的提示)。

**U4 spec 宣稱「字串不能含 `]`、換行」會被擋,但在 REVISIT 行上擋不到;反引號會讓條件被靜默改寫或整行不被認得**
severity: minor
blocking: 否 — 最壞是條件被截短或整行不評估,現行四個鍵也有同樣的限制,但 spec 把它寫成已處理。
引句:「字串去頭尾空白後不能是空的,不能含 `]` 與換行(既有標記的切法)」
1. 〈做法〉1.1 / S3。`_PROBE_TOKEN_RE` 的值是 `[^\]\n]*`,遇到第一個 `]` 就停。實測:`_probe_parse("[when-file:a.py::x[0]][by:2027-01-01]")` 回 `conds=[('file','a.py::x[0')]`、`errs=[]`——值被截在 `]` 前,沒有錯誤,所以 `_probe_gone_err` 看不到 `]`,S3 無法在 REVISIT 行上驗到這條。
2. `_probe_lines` 先過 `_strip_inline_markup`:字串裡出現成對反引號會被整段剝掉(`foo`x`bar` 變 `foobar`,條件值被改寫成作者沒寫的字,幾乎必定「不再出現」→ 立即成立);單個反引號則截掉後面全部,整行變成沒有條件標記而不被評估。實測 `[when-file:a.py::`x`y][by:…]` 回 `[]`。程式碼片段(markdown、JS 樣板字串、shell)恰好是 `when-gone` 最常挑的字串。
3. 字串未做 NFC。路徑會 `nfc(_posix_norm(...))`,字串與檔案全文做字面比對:筆記是 NFD(macOS 貼上)、檔案是 NFC 的中文字串會「找不到」→ 立即成立。
4. RULE 撤除條件那邊不同:`slot_parse` 接受值內成對方括號(實測 `[retire:when-gone:src/a.py::a [0]]` 解出完整值),commit 時的撤除條件驗證走全值,可以擋 `]`;但 `_retire_lines` 重寫成 `[when-gone:…]` 再交 `_probe_parse` 時同樣會在第一個 `]` 截斷。兩條路徑結果不一致。
5. 查證:`scripts/lumos:31759`(`_PROBE_TOKEN_RE`)、`scripts/lumos:368`(`_strip_inline_markup`)、`scripts/lumos:32035`(`_retire_lines` 重寫)、`scripts/lumos:3882-3889`(撤除條件的值驗證)。

**U5 同步清單漏了讀條件鍵或列舉鍵的平行位置**
severity: minor
blocking: 否 — 屬文件與提示字串漂移,但依本專案規則會變成筆記錯句。
引句:「技能手冊 `skills/lumos-project-notes/commands/03-寫回圖譜.md` 四種鍵那句補第五種」
1. 〈做法〉1.4 / 〈做法〉3。spec 列了 `_PROBE_KEYS`、`_probe_value_err`、技能手冊 03、筆記形狀擋提醒、守衛的 WHY、路線圖。仍寫著「四種鍵」或鍵清單、spec 沒列的地方:
   - `scripts/lumos:3891`(撤除條件的「不是機器式(只收 when-file/when-symbol/when-test/when-status…)」)
   - `skills/lumos-project-notes/reference.md:404`(`[retire:]` 事件鍵清單)
   - `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:54`(「鍵只有 file、symbol、test、status 四種」,文法的出處節)
   - `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:98`
2. 不改這幾處,S3「不認得的鍵的錯誤訊息應列出五個鍵」只對 `_probe_value_err` 成立,撤除條件那條路徑的訊息仍是四個鍵。
3. `_drift_probe_row_problems` / `_drift_probe_path_warn`(scan 的「寫法問題」)也是讀條件鍵的平行路徑,spec 沒說 `when-gone` 要不要有對應的檢查(見 U3)。

**U6 「寫下時」判定的三態沒收齊:淺層 clone、歷史樹判不了、預算切換的行為前後不一**
severity: minor
blocking: 否 — 影響的是標記雜訊與 CI 行為,不改動發現本身。
引句:「淺層 clone 不往回查。」
1. 天花板 4 與〈實務隱患〉跨環境寫「不往回查」,同一節又寫「標成判不了」;S6 只列「找不到提交或超過預算」。淺層 clone(`actions/checkout` 預設深度 1,本專案 CI 文件要求 `fetch-depth: 0`,消費專案不一定)到底是「不輸出任何標記」還是「每條都標判不了」沒有定。若是後者,CI 上 scan 每條成立的條件都多一個雜訊標記。
2. spec 沒說怎麼偵測淺層(`git rev-parse --is-shallow-repository`),也沒說偵測失敗怎麼辦。
3. 往回查到的提交,在那版樹上 `_drift_probe_line` 回 None(例如 git 讀不出那版的檔)時,2.1 只列了「找不到提交、git 失敗、超過預算」,沒有把「歷史樹上判不了」明寫進去。
4. 〈PRIOR-ART〉說 `drift exam` 已在歷史上重放條件、判定沿用 `_drift_probe_line`:實際上 exam 走的是 `_drift_check_core` 的推送判定(起點與終點兩版的轉變),不是「在某個歷史提交的整棵樹上評估條件」;建歷史樹的 `_drift_probe_tree` 與 `_drift_tree_env` 才是本案要重用的。
5. 效能:`_drift_tree_env(root, sha, …)` 會讀整個圖譜所有筆記(本 repo 約 705 篇),spec 沒說只在行裡有 `when-status` 條件時才建;`_drift_list` 的記憶有上限 8 筆,超過就整個清掉(`scripts/lumos:32165`),多於 8 個不同寫下提交時「同一個提交的樹只建一次」不成立。「成立的條件通常是個位數」沒有量測。`git log -S` 本身實測很便宜(單篇 17 個提交,0.03 秒),瓶頸不在它。

## 逐節結果

- frontmatter / 白話 / 依據 / PRIOR-ART / RETIRE-IF / REVISIT:已讀。連結目標(三篇計劃、`Systems/存量漂移守衛`)都存在;PRIOR-ART 的 exam 描述見 U6-4。
- 〈範圍〉:已讀,無 finding。
- 〈做法〉1(`when-gone`):見 U3、U4、U5;其餘(`::` 從第一個切、另寫 `_drift_gone_split`、`_drift_probe_cond_candidate` 看路徑、`_retire_lines` 自動支援)已核對與程式碼現況相符。
- 〈做法〉2(寫下時就已成立):見 U1、U2、U6。
- 〈做法〉3(說明與同步):見 U5。
- 〈實務隱患〉風險類逐類:
  - 併發:無,scan 唯讀(`cmd_drift_scan` 的註解明寫不寫帳),`git log` 與建樹只讀 git 物件。
  - 效能:見 U6-5;推送判定的 `when-gone` 與 `when-symbol` 同量級,判斷成立。
  - 回滾:已讀,與程式現況相符(舊版把 `when-gone` 當未知鍵,`_probe_parse` 標 `bad`,推送與 scan 都跳過評估或列為寫錯)。
  - 誤擋:見 U3(連結檔、資料夾、被忽略的檔會立即成立而被擋)。
  - 繞過:spec 只講表態繞過;另一條路是 U4 的反引號與 `]` 讓條件不被評估,現行四個鍵同樣存在。
  - 金流、對外送出、不可逆:無,理由同 spec(只讀筆記與 git 物件)。
  - 守衛面:已讀。
- 〈驗收條款〉:S1 到 S6 的測試名皆為新測試(未存在,屬新寫)。S5 與 S6 綁同一個測試名 `t_drift_scan_born_true` 不影響可執行。S3 驗不到 `]`(U4)。
- 〈回退〉、〈天花板〉:已讀,無 finding(天花板 2 的引用「天花板 2」存在)。
- 〈審計修正紀錄〉:空節,已讀。

最嚴重 severity 是 major,blocking 共 1 條(U1)。
