severity: major

# 架構對齊審查 r3(回頭條件消失式與生來成立,第 3 版修訂稿)

對照基準:`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/63d8e989-6977-4097-93eb-6b1c206d9484/scratchpad/rw` 的 `scripts/lumos`(下面行號都是這份)。

## 四問的總結

1. 分層與依賴方向:大致對。條件評估照舊進 `_DriftProbeTree.one`(`scripts/lumos:32377`),`_drift_probe_one`、`_drift_probe_line`(`:32388`)不動,推送判定走 `_drift_probe_cond_candidate`(`:32430`),born 在 `cmd_drift_scan`(`:34893`)拿到 `_drift_probe_scan`(`:32650`)的發現之後才算。這跟既有 REVISIT 處理同一條路。有兩處沒講清楚落在哪一層,見 Z7、Z8。
2. 命名與錯誤處理:規則名「條件寫錯」、`_probe_gone_err` 對 `_probe_named_err`、`_drift_born_line` 對 `_drift_prev_ack_line` 都跟鄰居一致。不一致處見 Z4、Z5、Z6。
3. 第二種做法:有一個,是往回查歷史的走訪器(Z1),另有路徑來源引用錯(Z2)、拆值又多一處(Z3)。
4. 落點:`Systems/存量漂移守衛` 加 `Systems/筆記內容閘` 對。`回頭條件寫法補齊_計劃` 同樣落這兩篇,「條件式回頭條件(乙)」那節在守衛裡(`docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:96`),筆記內容閘有 REVISIT 的 WHY 鄰居(`Systems/筆記內容閘.md:29-30`)。不需要另開。無 finding。

---

**Z1 往回查歷史另寫了一支走訪器,沒有用也沒有說明為什麼不用既有的單篇歷史走訪**
severity: major
blocking: 否 — 照字面做不會錯,但會多養一套跟 `_note_status_seq` 平行、規矩又不同的「一篇筆記的逐版歷史」
引句:「提交清單:`_lens_git(root, "-c", "core.quotePath=false", "log", "--first-parent", "--format=%H", <起點>, "--", ":(literal)<路徑>", binary=True, timeout=<剩餘預算與 20 秒的較小值>)`」
說明:專案裡已經有「讀一篇筆記的逐版歷史」的做法,是 `_note_status_seq`:`_ns_git(... "log", "--follow", "--format=%H", "--name-only", "-z", rng, "--", p)`,再用 `_git_log_sha_paths` 解成(提交, 當時的路徑),組成 `提交:路徑` 用 `_nodehome_cat_blobs` 批次讀,嚴格模式用 `_utf8_ok` 驗編碼,讀不到就回 None 當判不了,每次 git 呼叫前看 deadline。spec 的 PRIOR-ART 只拿 `drift scan --at` 與 `drift exam` 比,沒提這一支。差別:本案自己手寫一個 `_lens_git` 呼叫(自己拼 `-c core.quotePath=false`,而專案的做法是 `_ns_git` 或 `_lens_git(quote=True)`),只回 `%H`、不帶 `--name-only`,也不 `--follow`(把改名丟進天花板 2)。`--first-parent` 與 `:(literal)` 是本案有理由的新需求,但可以加在既有那支的旁邊或參數,沒有理由整支另寫、連改名跟隨都放掉。要嘛抽出共用(例如把 `_note_status_seq` 的「log 加批次讀加嚴格解碼」那一段拆成取版本清單的函式,status 與條件抽取各自吃),要嘛在 PRIOR-ART 寫明為什麼 `--follow` 在這裡不能用。
對照 file:`scripts/lumos:29789`(`_note_status_seq`)、`scripts/lumos:29804`(`log --follow ... --name-only -z`)、`scripts/lumos:29843`(`_git_log_sha_paths`)、`scripts/lumos:29813`(`_note_history_states` 的 `_utf8_ok` 嚴格判斷)、`scripts/lumos:27351`(`_ns_git` 的 quotePath 說明)、`scripts/lumos:39854`(`_lens_git(quote=True)`)、`scripts/lumos:35303`(drift exam 歷史用 `rev-list --first-parent`)

**Z2 「`_nodehome_list` 的原樣那份」這個東西不存在,規格指的路徑來源要不到**
severity: minor
blocking: 是 — 照字面實作拿不到「git 列樹時的原樣路徑」,實作者只能拿到 NFC 路徑,在 NFD 或混用檔名的 repo 會讀不到筆記或 `:(literal)` 對不上
引句:「路徑用 git 列樹時的原樣路徑(`_nodehome_list` 的原樣那份,不是 NFC 後的)」
說明:`_nodehome_list` 回的 `files` 與 `allp` 兩份都已經 `nfc(os.fsdecode(p))`,沒有原樣那份;它順便填的 `oids` 也是以 NFC 路徑為鍵。專案拿到原樣路徑的做法是 `git log --name-only -z` 的輸出(`_git_log_sha_paths` 配出「提交與當時的路徑」),或 `_notes_touched_in_range` 回的「git 原樣路徑」。`_drift_cat` 的說明就是在講「用路徑讀」在 NFD、混用、相容表意字時永遠讀不到,所以才用列檔時記的內容編號。本案往回查的是歷史提交,拿不到那個提交的 oids 時應照 Z1 的做法讓 log 一併吐出當時的路徑。
對照 file:`scripts/lumos:26196`(`_nodehome_list`,`:26217` 的 `nfc(os.fsdecode(p))`)、`scripts/lumos:32186`(`_drift_cat` 的說明)、`scripts/lumos:29755`(`_notes_touched_in_range`)、`scripts/lumos:29843`

**Z3 拆值還是會多出一份:`_probe_gone_err` 與 `_probe_norm_value` 的 gone 分支沒有說要呼叫 `_drift_cond_split(v, k)`**
severity: minor
blocking: 否 — 結構上還是同層,但違反程式裡明寫的「拆值只留一支」的決定
引句:「`_probe_value_err`:`gone` 走新寫的 `_probe_gone_err`(路徑規矩、字串非空、`..` 與 `/` 開頭照 file);」
說明:`_drift_cond_split` 的說明(代碼審 r5 架構對齊席)就是因為各處自己 `rsplit` 造成「點名的範圍跟判定的範圍連三輪對不上」才收成一支。spec 第 2 點開頭說 `_drift_cond_split(v, k)` 加鍵參數,但列到 `_probe_value_err`、`_probe_norm_value` 時只說「走新寫的」「只正規化路徑那段」,沒要求它們也呼叫那一支,實作者很容易在這兩處再寫一次「切第一個 `::`」。要在這兩行明寫「拆值一律呼叫 `_drift_cond_split(v, "gone")`」,守衛測試再掃一次(spec 的漂移守衛測試現在只掃訊息與文件)。順帶:現有 `_probe_norm_value`、`_probe_named_err`、`_drift_probe_path_warn` 本來就各自 `rsplit`,本案不必清,但不要讓 gone 變成第四個。
對照 file:`scripts/lumos:32195`(`_drift_cond_split`)、`scripts/lumos:31929`(`_probe_norm_value` 自己 `rsplit`)、`scripts/lumos:31945`(`_probe_named_err` 自己 `rsplit`)、`scripts/lumos:32620`(`_drift_probe_path_warn` 自己 `rsplit`)

**Z4 逐一列出的十處漏了 `_probe_parse` 裡依鍵名做反斜線轉換的那一行**
severity: minor
blocking: 否 — S3 的「字串裡的反斜線 應 原樣保留」測試會抓到,但規格沒有告訴實作者要擋住這一處
引句:「反斜線轉斜線與 NFC 正規化**只做在路徑那段**(先切再正規化)。」
說明:`_probe_parse` 在第一次驗值之前對整個值做 `val.replace("\\", "/") if k in ("file", "symbol", "test") else val`,是另一處「列舉鍵」的地方,也是反斜線處理的第一關(接著 `_probe_norm_value` 再驗第二次)。spec 的清單與〈做法〉1.5 列舉鍵的地方都沒提它。`gone` 不能被加進那個 tuple(會把字串裡的反斜線改掉),但也不能漏想:第二次驗證要靠 `_probe_norm_value` 把 `..\x` 轉成 `../x`,spec 應該明寫「`_probe_parse` 這行不加 gone,靠 `_probe_norm_value` 的第二次驗證抓 `..\x`」。
對照 file:`scripts/lumos:31982`(`_probe_parse` 的 tuple)、`scripts/lumos:31985-31987`(第二次驗證)

**Z5 `born` 的 `--json` 形狀裡 `unknown` 跟輸出頂層的 `unknown` 同名不同義,判不了也不走既有的 `problems`**
severity: minor
blocking: 否 — 名稱與欄位位置不一致,結構沒壞
引句:「`--json` 的發現多一個欄位 `born`,形狀固定是物件:`{"commit": 短碼}` 或 `{"unknown": 原因}`,不標就沒有這欄;判不了留在發現自己的欄位裡、不搬進 `problems`。」
說明:`cmd_drift_scan` 的 `--json` 頂層已有 `"unknown": bad`(讀不出的筆記路徑清單)與 `"problems"`(條件的判不了都記在這裡:`_drift_probe_scan` 的「判不了(超過預算)」「判不了(git 讀不出…)」)。`born.unknown` 是同一個詞第三種意思,下游讀的人要靠位置分辨。「不搬進 problems」的理由(發現已經在、不能因為判不了 born 就丟掉)成立,但欄名可以跟鄰居的形狀一致(例如 `{"commit": 短碼}` 對 `{"undecided": 原因}`,或沿用 `why` 這個既有發現欄的詞)。文字版的「判不了寫下時成不成立(原因)」也跟既有「判不了(原因)」不是同一個句型。
對照 file:`scripts/lumos:34925-34928`(`--json` 的 `unknown`、`problems`)、`scripts/lumos:32680-32685`(`problems` 裡的判不了句型)

**Z6 `_drift_born_line` 說「照 `_drift_prev_ack_line` 的呈現」,但那一行在已表態的發現底下根本不印,spec 又要求已表態的照標**
severity: minor
blocking: 否 — 實作時會發現,但會被迫把 born 行放到跟被引用的鄰居不同的位置
引句:「照既有「先前表態」那行的呈現(`_drift_prev_ack_line`),另起一支 `_drift_born_line` 印在那條發現底下」
說明:`_drift_scan_print` 對每個發現,只有 `if not acked:` 底下才印 `why` 與 `_drift_prev_ack_line`;已表態的只印那一行加「(已表態)」。〈做法〉2.5 與 [S5] 又要求已表態的照標,所以 born 行要放在 `if not acked:` 之外。這是照鄰居不了的地方,spec 應該明講「born 行不受 `if not acked` 管」,並說清楚已表態那行的字樣是否改成「(已表態)」加 born 一句,還是另起一行。
對照 file:`scripts/lumos:34938`(`_drift_scan_print`)、`scripts/lumos:34955-34960`(`if not acked:` 底下才印 why 與 prev_ack)、`scripts/lumos:32806`(`_drift_prev_ack_line`)

**Z7 推送點名多一句「路徑在這一版就找不到」沒說加在哪一層,最自然的位置會讓 key-agnostic 的判定函式懂 `when-gone`**
severity: minor
blocking: 否 — ⚠ 判不準是否算跨層,留給作者決定
引句:「`when-gone` 的路徑在終點版本就找不到時,點名訊息後面多一句「路徑在這一版就找不到——打錯字、全形符號,或是被 gitignore 的檔?」」
說明:原因字串是 `_drift_probe_judge(now_of, was_of, pr, old)` 組的,它只拿兩個回呼與解析結果,不認得鍵也沒有樹。能看到終點樹的是 `_drift_probe_check`(它有 `_tree(tip)`)。spec 沒指定放哪:放進 judge 就要給它樹或鍵(讓一個目前不認識任何鍵的函式認識 `gone`),放在 check 的 `must.append` 前補字才合現有分層。另外 `drift scan`(`_drift_probe_scan`)的「條件已經成立,該處理了」是另一套原因字串,spec 沒說 scan 要不要同樣的提示;存量裡的打錯字舊行恰好是 scan 最容易遇到的。
對照 file:`scripts/lumos:32589`(`_drift_probe_judge`)、`scripts/lumos:32485`(`_drift_probe_check` 呼叫 judge 與 `must.append`)、`scripts/lumos:32690`(scan 自己的 why 字串)

**Z8 反引號的原文檢查分在兩個呼叫端、各寫一份,沒有點名共用的函式**
severity: minor
blocking: 否 — 兩條路的規矩可能日後漂移(「RULE 撤除條件與 REVISIT 兩條路的寫法要求一致」是 spec 自己的目標)
引句:「在筆記形狀擋的回頭條件檢查(`_ns_revisit_violations`)與格子撤除條件檢查(`_slot_retire_err` 的呼叫端)看**原文**報「條件寫錯」」
說明:REVISIT 這條路的位置有現成的:`_ns_revisit_cond_viol(ln, rest)` 同時拿到原文 `ln` 與剝過的 `rest`。撤除條件那條路在 `_slot_retire_err` 的呼叫端,另一個地方。依專案慣例(「判定跟 E5、第二層共用同一支」,見 `Systems/筆記內容閘.md:29`)應該寫一支只看原文的 `_probe_raw_marker_err(原文)`,兩個呼叫端各呼叫一次,而不是各寫一份。另外 [S4] 的「照 REVISIT 那條路報錯」要靠這一支才保證一致。
對照 file:`scripts/lumos:27982`(`_ns_revisit_cond_viol`)、`scripts/lumos:3866`(`_slot_retire_err`)

**Z9 往回查每個歷史提交的圖譜位置沒有提 `_drift_vault_rel(root, sha)`**
severity: minor
blocking: 否 — 圖譜資料夾改過名的 repo 才會踩到,會被判成讀不到而標「判不了」,不會錯標
引句:「找到這一世的第一版後,在那個提交的樹與圖譜上用同一支 `_drift_probe_line` 判一次(圖譜用 `_drift_tree_env`,同 `drift scan --at` 讀某提交圖譜的做法)。」
說明:`drift scan --at` 與 `drift exam` 讀某提交的圖譜時都先用 `_drift_vault_rel(root, 該提交)` 取那個提交自己的圖譜位置(`scan --at` 那行的註解寫明「圖譜資料夾改過名時,拿現在的位置讀舊提交會讀到空樹」)。spec 說「同 `drift scan --at` 的做法」但沒把這一步寫出來,往回走到舊提交最容易遇到的就是這種情況;也牽動 Z1 的筆記路徑要不要隨提交換成當時的 `vault_rel` 加相對路徑。
對照 file:`scripts/lumos:34909-34914`(`scan --at` 取提交自己的圖譜位置)、`scripts/lumos:35104`、`scripts/lumos:35146`(`drift exam` 同樣做法)、`scripts/lumos:31668`(`_drift_vault_rel`)

---

不對齊共 9 條,其中 major 1 條
