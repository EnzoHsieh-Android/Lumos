severity: major

# 存量漂移改法 r3 邊界與可執行審查(sonnet)

審查範圍:凍結審材 r3-snapshot.md 全文;對照 clone-ns 的 scripts/lumos。已用臨時腳本在 mktemp 目錄驗證 git 對 untracked 檔的行為,並用 python 載入 scripts/lumos 驗證 `parse_frontmatter`、`_visible_lines` 的實際輸出(未改任何 repo 檔)。

## F1 --dry-run 在「重判這一行是不是這一種發現」與 c1 前提之前就結束,預覽的東西真跑會被擋
severity: major
blocking: 是 — 不改,實作者會讓 dry-run 對「其實不是這種發現」的行印出改後內容並回 0,而 spec 明說要拿 dry-run 取代 settle 沒有的預覽
引句:「不拿鎖,用第 1 步讀到的內容照第 4 步算出改後內容,印改前改後,回 0」
file: `scripts/lumos:26078`(`_drift_state_findings` 只在 spec 的第 3 步才被呼叫)
1. 第 1 節的步驟順序是 1 鎖外準備、2 dry-run 結束、3 拿鎖並用 `_drift_state_findings(env, only=…)` 重判「指定的行要還是這一種發現」。所以 dry-run 從頭到尾沒有任何一步確認 `<行號>` 真的是 `--kind` 指的那種發現。
2. c1 的「前提(鎖內)」(家節點有綁測試的正式行)也在第 3 步之後,dry-run 同樣跳過。第 3 節又寫「settle 沒有 `--dry-run`,要先看改法就用 `drift fix --kind c1 --dry-run`」。重現:對一篇 pending 守衛紀錄,或家節點沒有正式行的守衛紀錄跑 `drift fix --kind c1 <行號> --dry-run`,依字面會印出改前改後、回 0;拿掉 `--dry-run` 真跑卻回 2。「預覽跟實寫才會一致」這個目標(第 1 步自己寫的)被打破。
3. c3(`--by` 要查 `env.by_stem`)、c5(要從家節點正式行讀測試名)、c2(要看連結)的預覽都需要一份圖譜物件,spec 沒說 dry-run 用哪一份、要不要現建。
4. 行號越界、不是該種發現、`--kind` 與那一篇的 type 對不上,在 dry-run 下都沒有定義的行為(只有拿鎖後的第 3 步有「回 2 並講『這一行現在不是 <種類>』」)。
5. 修法方向(不是建議措辭,是要補的條款):dry-run 也要跑第 3 步的重判與 c1 前提(只是不拿鎖、用當下讀到的 Env),寫進 S9 或 S1。

## F2 第 4 步拿哪一份文字算改後內容沒有規定,字面讀法是鎖外讀的舊內容,會蓋掉鎖等待期間別人的改動
severity: major
blocking: 是 — 實作者若照第 1 步讀到的 lines 算改後內容,「鎖內重判通過」不保證寫進去的檔是最新的,等於用舊版整篇覆蓋
引句:「用 `load_raw_for_edit` 讀一次(它對 BOM、CRLF 直接拒絕」
file: `scripts/lumos:14695`(`atomic_write_verify` 只用磁碟上的原檔做 lint 指紋比對,不擋寫進去的內容是舊的)
1. 第 1 步是「鎖外只讀準備」,`load_raw_for_edit` 讀一次;dry-run 明寫「用第 1 步讀到的內容照第 4 步算出改後內容」,顯示第 4 步吃的是第 1 步的內容。第 3 步「鎖內」只重建圖譜物件並重判發現,沒有說「重讀那一篇原文」。第 2、3 節反而明寫 c1 與 settle 是「鎖內重讀重判」,只有這兩處提到鎖內重讀,更加證明其他種類沒有。
2. 重現(⚠ 依字面推演,未實跑):A 在鎖外讀完 c3 那篇 → B 用 `lumos set` 改了同一篇別的欄位並釋放鎖 → A 拿到鎖,重判仍是 c3(status 還是 pending)→ 用舊 lines 算出改後內容 → `atomic_write_verify` 通過(它只比 lint 指紋)→ 寫入,B 的改動被整篇蓋掉。第 5 步的「還原前比指紋」只保護「我們寫完到驗證之間」,保護不到「讀取到寫入之間」。
3. 還原也一樣:第 5 步要還原的「改前原文」若是第 1 步的舊內容,會把 B 的改動也回退掉。
4. 要補的條款:第 3 步拿到鎖之後,必須再用 `load_raw_for_edit` 讀一次,第 4 步只用這份;c1 的「鎖內內容需要日期」那句才有意義。

## F3 「沒有未提交的改動」沒涵蓋 untracked 與被忽略的筆記,「git 一定退得回去」的前提不成立
severity: major
blocking: 是 — 這是整份計劃「不可逆(碰到,可還原)」與修復帳定位的唯一退路,漏掉的情況下改壞的筆記沒有任何退路
引句:「先確認那一篇在 git 裡沒有未提交的改動(工作目錄與暫存區都乾淨」
file: `scripts/lumos:5843`(`_plan_first_commit` 對從沒進歷史的檔回 None,說明它確實會遇到這種檔)
1. 實測(臨時 repo):對一個 untracked 的 `v/new.md`,`git diff --quiet -- v/new.md` 與 `git diff --cached --quiet -- v/new.md` 都回 0(乾淨);只有 `git status --porcelain` 才顯示 `??`。被 `.gitignore` 的筆記連 `git status --porcelain` 也是空的。
2. spec 只寫「工作目錄與暫存區都乾淨」,實作者最自然的寫法是這兩支 `git diff --quiet`,於是新建還沒 `git add` 的 Issue(c2)、驗證紀錄(c3、c4)會被放行,改壞了沒有任何提交可以還原,而第 1 步、修復帳、回退節都寫成「git 一定退得回去」。
3. 要補的條款:判準明寫成「該路徑必須是已追蹤(`git ls-files --error-unmatch`)且 `git status --porcelain -- <路徑>` 為空」;untracked、ignored、intent-to-add 都回 2 並說明。
4. 不在 git repo、git 不在 PATH:spec 第 1 步後半有「不在 git repo 都回 2」,但寫在 c1/c4 的 git 查詢那句裡;c2、c3、c5 的「不在 git repo」是否也擋,要靠讀者推論這道乾淨檢查本身需要 git。建議條款把這一點單獨寫明(此點單獨看是 minor,併入本條)。

## F4 S1「有未提交改動就擋」與 S5「同一欄兩項可一項一項修」互相打架
severity: major
blocking: 是 — 兩條條款都要寫成測試,照 S5 的說法連續兩次 fix 同一篇,第二次會被 S1 擋下
引句:「同一欄兩項都含時可以一項一項修」
file: `scripts/lumos:26078`(`_drift_state_findings` 每篇最多產生一筆 c4,所以「一項一項修」必然是對同一篇連續 fix)
1. S1 與第 1 步:那一篇有未提交的改動(含暫存區)一律回 2。第一次 c4 fix 寫完後那一篇就是「未提交的改動」。
2. 第 5 節與 S5 允許同一欄有兩項含關鍵詞時「一次修一項」,第 1 節第 5 步還專門為此寫了 c4 判準。但 c4 只有一筆發現/篇,第二項只能在同一篇再跑一次 fix,此時工作目錄是髒的,依 S1 會被擋。
3. 同樣的衝突出現在「同一篇同時有 c3 與 c4」(兩者都是驗證紀錄,c3 看 `plan_refs`、c4 看 `valid_under`,可以並存):先修 c3 再修 c4 必須中間先 commit。
4. spec 完全沒說「中間要先提交」,也沒說同篇連續修的例外。實作者得自己決定放寬 S1(削弱不可逆的保證)或讓 S5 那句不可達(測試寫不出來)。要補:明寫同篇連續修需先 commit,並把 S5 的測試寫成含 commit 的序列,或定義「髒但只被本工具上一筆 fix 弄髒(指紋等於修復帳的 after_sha256)可續修」。

## F5 c4 的 `--new` 只擋換行與關鍵詞,替換進去的片段可以是壞 YAML,現有自驗抓不到
severity: major
blocking: 是 — 會寫出 Obsidian 或標準 YAML 讀不了、或型別變了的開頭欄位,而 spec 的驗證與 lint 都不會攔
引句:「`--new` 不得含換行、不得含那三個詞(會立刻再被列出,回 2,提示改用 drift ack)」
file: `scripts/lumos:14444`(`fmt_list_item` 有 `_yaml_plain_ok` 守衛,c4 的原始文字替換繞過了它)
1. 實測(python 載入 scripts/lumos 跑 `parse_frontmatter`):`valid_under:` 底下 `  - 提交 abc123: 見卷證` 讀成字串、lint 指紋為空;`  - 提交 abc #見` 同樣無指紋;`  - "提交 abc 見`(引號沒閉合)無指紋;`valid_under: 提交 abc: 見` 無指紋。工具自己的解析器全放行。
2. 但標準 YAML 下:`- 提交 abc123: 見卷證` 會變成單鍵物件而不是字串(型別變了,c4 之後的 `_conds` 讀取會壞);` #` 之後整段被當註解截掉(資訊遺失);未閉合引號與 `key: value` 混在純量裡是語法錯誤。
3. 第 1 節第 5 步的 `atomic_write_verify` 檢查的是 `expected_check(fields)` 與「lint 沒有新指紋」,c4 的 `expected_check` spec 沒定義;即使定義成「被換的那一段不再含那三個詞」,對 YAML 合法性也沒有任何約束。
4. `--old` 若落在有引號的項目裡(`- "還沒提交…"`),`--new` 含雙引號也會破壞引號配對。
5. 要補:`--new` 進入原始文字之前,對「替換後那一整行」做與 `fmt_list_item`/`_yaml_plain_ok` 同標準的檢查(或重新用 YAML 規則解析那一項,確認仍是單一字串),不合就回 2 並提示加引號的寫法。

## F6 c4 的「處理到」判準對 `--old` 不含關鍵詞的替換也會成立,回報修好了但發現還在
severity: minor
blocking: 否 — 不改,操作者用不含關鍵詞的片段當 `--old` 時會得到成功訊息與修復帳一筆、但 scan 仍列出同一筆 c4;是誤導而不是壞資料
引句:「c4 被換的那一段不再含那三個詞(同一欄別項還含是別筆)」
file: `scripts/lumos:25978`(`_DRIFT_UNCOMMITTED_WORDS` 三個詞)
1. 「被換的那一段」指 `--new`(必然不含,因為前面已擋)還是指替換後那一整項,spec 沒有說。若指 `--new`,則 `--old "工作樹"` 換成別的字,判準恆成立,但那一項的「未提交」還在,scan 仍會列出。
2. `--old` 是關鍵詞的一部分(例:`--old "提交"` 從「未提交」中切出)也合法,結果是把詞拆壞而不是把前提改對。
3. 要補:判準寫成「替換後,包含 `--old` 那一處的那一項不再含三個詞之一」,或要求 `--old` 必須至少含一個關鍵詞。

## F7 c2 `--close --why` 沒有長度與換行規則,而同一份 spec 對 `--new` 明擋換行
severity: minor
blocking: 否 — 不改,`--why` 帶換行會把一行變多行,且後面那行可以是任何行首格式;是操作者輸入,影響範圍限於那一篇的結尾
引句:「結案(存量漂移 c2):<why>」
file: `scripts/lumos:27101`(`cmd_drift_ack` 對 `--reason` 有至少 4 字的規則;`--keep` 走它,`--why` 沒有對應)
1. `--keep --reason` 等同 `drift ack`,有「至少 4 個字」與 JSON 逸出;`--close --why` 是直接寫進正文的一行,沒有最小長度、沒有換行檢查、沒有前後空白處理。
2. `--why $'…\nREVISIT:2026-01-01 …'` 會在正文末尾造出一條真的回頭條件行(行首標記合法),或造出別的行首格式;第 6 節緊接著要「列出這篇還留著的回頭條件」,行為被污染。
3. 要補:`--why` 不得含換行/控制字元、至少 4 字,與 `--reason` 對齊;S11 的測試加一格。

## F8 參數與種類的組合表不完整:`--keep`、c4 只列證據、c5/c1 的 `--date`、settle 的 `--date` 驗證
severity: minor
blocking: 否 — 不改,每個缺口的實作者都能猜出合理做法,但不同實作者會猜不同,測試對不上
引句:「等同 `drift ack --kind c2`(同第 8 節記 related 與時間戳記),不改筆記、只寫表態檔」
file: `scripts/lumos:37033`(main 分派目前「不是 scan 就當 ack」)
1. `--keep` 走第 1 節的哪幾步?第 1 步的乾淨檢查與 BOM/CRLF 檢查若套用,則 CRLF 的 c2 筆記連表態都做不到(scan 會列、fix 拒絕、`--close` 也拒絕);既有 `drift ack` 對這種筆記是可用的。「等同」兩個字不足以決定。
2. c4 不帶改寫參數(只列證據、不寫檔)是否受第 1 步乾淨檢查限制?spec 只說 `--dry-run` 不受限,所以髒的筆記連看證據都要加 `--dry-run`。
3. 第 1 步的例子「pending 的 settle 給 `--date`」是 `guard settle` 的規則,不是 `drift fix` 的參數;c5(日期用今天)給 `--date`、c1 給 `--test`/`--status`/`--close` 等是否一律回 2,沒有一張「每種 kind 收哪些旗標」的表。
4. `guard settle --date` 的格式錯誤與晚於今天是否也回 2:第 1 步寫在 fix 的準備段,第 3 節的 settle 沒有重述,`--dry-run` 對 `--keep` 是否也不寫表態檔也沒說。
5. 要補:一張 kind × 旗標的收/拒表,並在 S1 用它。

## F9 「每一步失敗都回 2」與寫入例外的接法不一致,OSError 會直接噴 traceback
severity: minor
blocking: 否 — 不改,磁碟滿或權限問題時是 rc 1 加堆疊而不是 rc 2;不寫壞資料
引句:「順序(每一步失敗都回 2、印原因)」
file: `scripts/lumos:12314`(鄰居 settle 只接 `(ValueError, RuntimeError)`)
1. 第 5 步寫「例外照鄰居 settle 的接法轉成回 2」。鄰居的接法是 `except (ValueError, RuntimeError)`,而 `_write_lf` 的失敗(權限、磁碟滿、目錄被換成檔案)是 `OSError`,不在其中;`edit_fm_scalar` 遇到 `status` 是清單型欄位也是丟 `ValueError`,位置在 `atomic_write_verify` 之前,也不在 spec 描述的接法範圍內。
2. 結果:照字面實作,`OSError` 沒被接住,回 1 並印堆疊,違反開頭那句。還原本身失敗有「回 2」的規定,但第一次寫入失敗沒有。
3. 要補:第 4、5 步的所有 `OSError` 一併轉 2,並在 S9 加一個注入寫入失敗的案例(現有故障注入只有 verify 與 ledger)。

## F10 c2/c3 加行時「結尾停在未閉合圍欄」用什麼判斷沒指定,最自然的做法會誤判一般以圍欄結尾的筆記
severity: minor
blocking: 否 — 不改,實作者用 `_visible_lines` 判會把「以已閉合程式碼區塊結尾」的筆記整批擋下,測試沒覆蓋就上線
引句:「正文結尾停在沒閉合的程式碼圍欄裡就回 2(加進去會變成程式碼的一部分)」
file: `scripts/lumos:3531`(`_visible_lines` 不回傳「結尾是否還在圍欄裡」,`_scan` 的 unterminated 旗標是內部區域變數)
1. 實測:文字 `正文\n\n```\ncode\n```\n` 經 `_visible_lines` 回傳的可見行是 `['---','type: issue','---','正文','','']`;最後一個非空行「```」(已閉合的收尾標記)不在可見行裡,標記行本身一律被跳過。
2. 若實作者以「最後一個非空行不在可見行內」判斷未閉合,已閉合的圍欄結尾也會被判成未閉合而擋下。`_visible_lines` 還有「規格讀法讀不完就退回寬鬆讀法」的分支,所以要用哪一種讀法判斷,spec 也沒說。
3. 要補:指定新增一支回傳「結尾是否仍在圍欄內」的共用函式(從 `_visible_lines` 的 `_scan` 抽出),並在 S4 或 S11 加兩格:以已閉合圍欄結尾(放行)、以未閉合圍欄結尾(擋下)。

## F11 「本身與上層目錄都不是符號連結」沒說到哪一層為止,照字面在 macOS 暫存目錄裡整批被擋
severity: minor
blocking: 否 — 不改,測試與很多開發機(路徑含 /tmp、/var 的符號連結)會全被擋,實作者會自己發現並補上界線
引句:「本身與上層目錄都不是符號連結(是就回 2)」
file: `scripts/lumos:8511`(`_jsonl_append_verified` 現在完全不檢查符號連結,這是新增的共用檢查)
1. 「上層目錄」若指到檔案系統根,則 repo 放在 `/tmp/...`(macOS 上是 `/private/tmp` 的符號連結)、`/var/folders/...`、家目錄本身是符號連結的機器上,任何帳檔都被擋,S9 的測試在 tempfile 目錄裡也會紅。
2. 合理的意思是「repo 根(不含)以下,到帳檔為止」逐層都不是符號連結,且解析後的真實路徑落在 repo 根的真實路徑之下。spec 沒寫界線,「repo 根」本身是符號連結時的行為也沒寫。
3. 另外,spec 要求「表態檔的寫入也做同一個檢查」,而 `_drift_load_acks` 讀取端已有 `is_symlink()` 檢查;若 `governance/` 目錄合法地是符號連結(共用治理目錄的常見做法),既有使用者從此不能表態,向後相容也沒寫。

## F12 E5 的「顯示上限」在 `warn_soft` 裡面,呼叫端事先不知道哪幾行會顯示
severity: minor
blocking: 否 — 不改,實作者要嘛全標(違反條款文字)要嘛改 `warn_soft` 或複製上限常數
引句:「照樣列、照樣計數;只標在顯示上限內的行」
file: `scripts/lumos:1311`(`shown = list(lines) if _verbose else list(lines)[:_SOFT_CAP]`,`_SOFT_CAP = 3`,`--verbose`/`--ci` 時全列)
1. 上限由 `warn_soft` 依 `_verbose` 與 `_SOFT_CAP`(3)在內部截,E5 事先組 `_lines5` 時不知道。`--ci` 視同 verbose(第 1298 行),所以「顯示上限」在 CI 是無上限,互動是 3。
2. S6 寫「在顯示上限內的那幾行應標」,測試得知道用哪個模式跑。要補:標記在組 `_lines5` 時對「排序後的前 `_SOFT_CAP` 條(或 verbose 時全部)」做,或讓 `warn_soft` 收一個逐行加註的回呼。

## F13 c2/c3 表態的 `ts` 精度、時區與相同時間的平手沒有定義,「最新一筆」在邊界會誤判
severity: minor
blocking: 否 — 不改,同一秒內連續表態、或跨時區/跨機器合併後,可能取到錯的那一筆,方向是可能多擋或少擋一次,可由重新表態自癒
引句:「取 `ts` 最新的那一筆,它的 `related` 涵蓋現在的清單」
file: `scripts/lumos:27079`(`_drift_split_acked` 現在用集合比對,新邏輯要新寫)
1. `ts` 寫成「ISO 時間到秒」:沒寫是 UTC 還是本地、有無時區位移。兩台不同時區的機器各自追加後 git 合併,字串比大小會排錯順序。
2. 同一秒內兩筆同鍵表態(腳本連跑 `--keep` 兩次、或 `fix --keep` 之後緊接 `drift ack`)平手時取哪一筆沒規定;`related` 不同時結果不同。
3. 舊筆記錄只有 `date` 沒有 `ts`,spec 有「只看記了 related 的」擋掉,但 `related` 有而 `ts` 缺或格式壞(手改)的紀錄怎麼排沒有寫。
4. 要補:`ts` 一律 UTC 帶 Z、平手取檔案中較後者、`ts` 缺或不合法視為最舊;寫進 S8 的測試。

## F14 追加前補換行只說「最後一個位元組不是換行」,空檔與不存在的檔沒有定義
severity: minor
blocking: 否 — 不改,一個空的或新建的帳檔第一行前面會多一個空行,`wc -l` 對 RETIRE-IF 第①項的機械量法多算 1;其他讀取端會跳過空行
引句:「改成追加前檢查最後一個位元組,不是換行就先補一個換行」
file: `scripts/lumos:8511`(`_jsonl_append_verified` 以 `open(path, "a")` 直接追加,不管檔是否存在)
1. 檔不存在或大小為 0 時沒有「最後一個位元組」;`data[-1:] != b"\n"` 這種寫法對空檔為真,會先寫一個換行。
2. 這支共用函式被表態檔、治理帳、canary 等多個帳共用,spec 寫「一起受益」,但沒有要求既有各帳的測試全跑一次,也沒有說補換行是否要記一筆(悄悄改了別人的檔尾)。
3. 要補:空檔與不存在不補;另外補換行本身要在同一次 `open(..., "a")` 內完成(先讀最後一個位元組再一次寫兩段),避免兩個程序同時追加時互相插入。

## F15 `<節點>` 用 `env.find` 解析,同名多篇時只印警告取第一篇,而 fix 是會改檔的指令
severity: minor
blocking: 否 — 不改,同名時可能改到別篇;第 3 步的重判只在那個行號恰好不是該種發現時才擋
引句:「語法:`lumos drift fix <節點> <行號> --kind <種類> [--dry-run] [種類專屬參數]`」
file: `scripts/lumos:667`(`Env.find` 遇同名 `print` 警告後回 `hits[0]`)
1. spec 對 `--by` 特別寫了「先查 `env.by_stem` 看同名有幾篇,找不到或同名好幾篇回 2」,但 fix 自己的 `<節點>` 沒有同樣規則。c2/c3/c5 的發現行都是 `status:` 那一行,行號常常相同(第 3 至 5 行),同名兩篇又剛好都有同一種發現時,重判不會擋。
2. `drift ack` 現有就是這個行為,但它只寫表態檔;fix 會改筆記本文。要補:與 `--by` 同一條規則(同名好幾篇回 2、要求路徑寫法)。此庫目前無同名筆記(實測 0 組),所以是預防性條款。

## F16 c5 遇到「家節點還留著預告行」一律指到 `guard settle`,但 settle 對「好幾條」也是擋下、指回手動處理
severity: minor
blocking: 否 — 不改,c5 在「家節點有兩條以上同文預告行」時會給一條走不通的出路
引句:「家節點還留著重複的預告行」
file: `scripts/lumos:12262`(`_guard_settle_home`:idxs 為 1 條時拿掉重複預告行,超過 1 條時回 False 並印「先手動把重複的那行處理掉」)
1. `_guard_settle_home` 有兩種情況:正式行已在且預告行剛好 1 條(settle 幫你拿掉)、正式行已在且預告行 2 條以上(settle 擋下要你手動處理)。spec 的 c5 條款把「指到 guard settle」說成一律的出路,第二種情況指過去只會再被擋一次。
2. 另外 c5 的偵測(`_drift_guard_findings`)只要求正式行綁了測試,不看預告行殘留與否;所以 scan 會列出 c5,fix 又要回 2,循環提示。
3. 要補:c5 的擋下訊息依預告行條數分兩句(1 條指到 settle;2 條以上直接說手動拿掉重複行);S12 測試兩種各一格。

## F17 修復帳 `changed` 的行號是改前還是改後、插入行的改前寫什麼沒定義
severity: minor
blocking: 否 — 不改,帳的讀者(稽核者)無法確定要對哪個版本的行號,「c1 事後被再改」的量法(RETIRE-IF 第②項)要用它
引句:「`changed`(改到的每一行:行號、改前、改後;刪掉的行改後記 null)」
file: `scripts/lumos:12086`(`_guard_settle_rewrite`,c1 整篇改寫加上刪行後,行號會位移)
1. c1 整篇重寫加上「刪 settle 句與後面一個空行」,刪行之後所有後續行號位移;c3、c2 是在檔尾插入新行。「行號」記改前的還是改後的、插入行的「改前」是否記 null,只寫了刪除那一個方向。
2. RETIRE-IF 第②項要對修復帳每筆 c1 的路徑跑 `git log -p` 看「改句那幾行有沒有再動」,行號語意不定就沒法機械比對。
3. 要補:`changed` 每筆給 `{old_line, new_line, before, after}`(缺的一邊是 null),並釘在 S9 或另一格測試。

## F18 S9 的「磁碟已被別人改過就不還原」那一支沒有測試接縫
severity: minor
blocking: 否 — 不改,這是整份計劃最重要的一段安全邏輯,卻只有一半有測試路徑
引句:「環境變數 `LUMOS_DRIFT_FIX_FAULT=verify|ledger` 讓第 5 步的驗證或第 6 步的寫帳假裝失敗」
file: `scripts/lumos:14714`(`_VAULT_LOCK_STALE_SEC`;鎖檔與寫入的順序在測試裡要靠額外接縫才能製造插手者)
1. S9 寫「驗證失敗或帳寫不進去時,磁碟內容仍是剛寫的那一版才還原,否則回 2 不還原」。故障注入只能讓驗證或寫帳「假裝失敗」,製造不出「失敗後、還原前磁碟被別人改了」這個狀態,「否則」那一支無法寫成測試,除非用 monkeypatch 測試內部函式。
2. 要補:`verify|ledger` 之外多一個接縫值(例如 `ledger-tamper`:寫帳前在檔尾追加一行再假裝失敗),或明寫這一支用什麼方式在測試裡製造。

## F19 `guard settle` 對 pass 節點的回傳碼從「一律 0」變成「前提不符回 2」,重跑式的呼叫方會壞
severity: minor
blocking: 否 — 不改,只影響在腳本或掛鉤裡把 `guard settle` 當冪等指令重跑的呼叫方;是相容性的邊界,不是資料
引句:「還有預告句就走第 2 節同一支(前提、日期、不疊、修復帳 `via: guard settle`)」
file: `scripts/lumos:12222`(現況:pass 直接印已轉正、回 0,註解寫「另一個程序剛做完、或重跑:當成成功」)
1. 現行的註解是刻意設計:重跑或併發時 pass 一律成功。新行為在 pass 且留有預告句時,如果家節點沒有綁測試的正式行、需要日期又推不出來,依第 2 節都回 2。原本回 0 的呼叫現在可能回 2。
2. spec 的回退節與實務隱患的向後相容都只寫了「舊版讀表態檔不會壞」,沒寫這個回傳碼的變化。要補:寫進向後相容,或把「pass 但前提不符」定成印提醒回 0,只有 fix 入口回 2。

## 已讀無 finding 的節

## 回退
已讀,無 finding
引句:「`drift fix` 是新指令:拿掉子命令、各種類的改法函式、drift 分派改回兩支」

## 誠實界線
已讀,無 finding(F19、F13 的補充屬於這裡的向後相容與時間戳記,不在本節重複)
引句:「c4 的卷證目錄是用名字比對猜的,可能漏或多;所以只提議、不寫入。」

## 合約候選
已讀,無 finding
引句:「(設計審過閘後填。)」

## 審計修正紀錄
已讀,無 finding
引句:「折入(全數):轉正日期改看守衛紀錄第一次變成 pass 的提交」

## 實務隱患逐類
1. 守衛面誤擋/漏擋:見 F3(漏擋 untracked)、F11(誤擋符號連結上層目錄)。
2. 不可逆:見 F2、F3、F4。
3. 併發:見 F2、F13、F18;鎖內重建圖譜約一秒對 30 秒的接手上限沒有問題(工具鏈 590 篇),但 spec 沒寫兩次重建(重判一次、寫後驗證一次)加起來的上限,大型消費專案的鎖時間是 ⚠ 未量測。
4. 效能:無。fix 一次一篇、git 查詢限定單檔;`_drift_state_findings` 每次仍會 `build_typed_index(env)` 全庫,鎖內兩次,量級與現有 `drift ack` 同。
5. 向後相容:見 F11、F14、F19。

總結:最嚴重等級為高,需先改再實作的共 5 條(F1 至 F5),其餘 14 條為文字或條款精度。
