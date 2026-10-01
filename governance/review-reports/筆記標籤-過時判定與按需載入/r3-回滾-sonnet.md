severity: major

固定席筆記:這次派工詞尾端沒有附 hook 筆記,所以沒有固定席可逐條判。

我的鏡頭是回滾:上線後要退回去,新接入專案已經被擋、欄位已經寫了一堆,關開關或還原提交退不退得乾淨。「回退」那節寫得太樂觀,有四處照字面實作後退不乾淨,另有三處措辭或順序問題。

**R3K1**
severity: major
blocking: 是 — 提醒跑在哪條路徑沒寫死,實作者順著「沿用新增行」做,預設 `gate=block` 的專案會被新提醒擋住,退路也不再只剩一個開關。
- 輸入是消費專案提交含新 H1、H2、H3 或 W4 行的筆記,走到〈結構性提醒〉。
- 現有程式有兩套「新增行」機制:
  - 第一套把結果放進 `violations`,在 `gate=block`(沒設定就是 block)時直接擋(`rc=1`)。
  - 第二套是否定現況句那條路,註解明寫「★不進 violations,回傳值照舊兩個★」。它只在 `--staged` 且開關不是 off 時才算,`--diff` 與 doctor 的事後掃描都不算。
- spec 在 PRIOR-ART 寫「沿用筆記形狀檢查的新增行與上線點」,又寫「照 `note_shape.negation` 的先例」。
  - 這兩句指向不同機制,沒有一句說「只在提交前(`--staged`)算、不進違規清單、CI 與 doctor 不算」。
  - 實作者若走第一套,H1、H2、H3 變成預設擋,和「本案不新增任何擋」矛盾。
  - 若走第一套,`--diff` 與 doctor 事後掃描會從上線點一路回掃,也違反「只看新寫的行」。
  - 退路只剩 `note_shape.tag_hints: off` 或還原提交,而 `gate=block` 的消費專案已經被擋住。
- 另外,`_note_shape_config` 的註解說它有兩個以兩個值解包的呼叫端,所以否定現況句另外寫了一支解析函式。spec 只說「照先例」,沒說 `tag_hints` 必須走獨立解析函式,實作者很可能去改前者而弄壞那兩個呼叫端。
- 引句:「照 `note_shape.negation` 的先例,壞值照 warn 並講一句」
- 佐證 file: `scripts/lumos:25593`(`_note_shape_eval` 的 hints 說明)
- 佐證 file: `scripts/lumos:24875`(`_note_shape_config`,預設 block)
- 佐證 file: `scripts/lumos:25564`(`_note_shape_negation_config` 的獨立解析註解)

**R3K2**
severity: major
blocking: 是 — doctor 的過期 RULE 清單沒有開關,也沒說算不算 issue;做成 `warn` 就會讓每個有舊 RULE 的專案 CI 變紅,而唯一的解法是回頭改舊筆記。
- 輸入是消費專案(例如 rtb 94 篇)裡有 `[until:]` 已過期或 `[confirmed:]` 超過半年的舊 RULE 行,走到〈健康檢查補一段〉,再到 S6。
- doctor 現有兩種提醒寫法:
  - `warn` 會 `issues += 1`。
  - `warn_soft` 不計入 issue。
  - CI 跑的是 `doctor --ci`(等於 strict),`issues>0` 就 `return 1`。
- spec 只寫「只提醒」,沒指定用哪一種。
- 〈結構性提醒〉的子開關列在 S4 的關閉範圍裡只有 W4、H1、H2、H3 與已作廢缺連結,不含 S6。所以 doctor 清單沒有任何設定可關。
- 〈回退〉也沒有 doctor 清單那一行,「第 0 步」只寫「doctor 清單各自還原那個提交」。
- 後果:
  - 實作者選 `warn`,所有帶舊 RULE 行的專案 CI 變紅。
  - 要消掉只能改舊行(補 `[confirmed:]`),直接違反「不回頭補」。
  - 專案端沒有關閉手段,只能等工具鏈還原提交。
- 引句:「doctor 列出所有 RULE 行裡 `[until:]` 已過期、或 `[confirmed:]` 超過半年的(舊行也列、只提醒)」
- 佐證 file: `scripts/lumos:1332`(`warn` 的 `nonlocal issues`)
- 佐證 file: `scripts/lumos:3207`(`return 1 if strict else 0`)
- 佐證 file: `.github/workflows/ci.yml:104`

**R3K3**
severity: major
blocking: 是 — 改範本會讓所有消費專案的 `doctor --ci` 變紅,第 0 步與第 1 步都這樣,「不新增任何擋」「屬既有行為」只蓋到第 1 步的還原。
- 輸入是第 0 步、第 1 步改動 `scripts/templates/graph-discipline.md`。
- 第 0 步已經改範本:RULE 效力兩處說法對齊。第 1 步再加一行指路。
- Check D 比對消費專案 CLAUDE.md 的紀律區塊與範本,內容不同就走 `warn(...)`(算 issue),CI 的 strict 隨即 exit 1。
- 消費專案要先 `lumos update` 再提交,CI 才會綠。
- 〈回退〉只在第 1 步註明「期間 doctor 提醒紀律區塊不一致,屬既有行為」。
  - 第 0 步改範本與第 0 步還原都沒提。
  - 〈實務隱患〉的「自我治理」寫「本案不新增任何擋」,這個事實不成立。
  - 本案對消費專案 CI 的實際影響是範本一改就要全體 `lumos update`。
  - 〈回退〉沒寫「還原範本後,消費專案又要再 update 一次才能轉綠」,等於退一次要再紅一次。
- 引句:「期間 doctor 提醒紀律區塊不一致,屬既有行為」
- 佐證 file: `scripts/lumos:2828`(Check D 的 `warn`)
- 佐證 file: `scripts/lumos:2790`(Check D 說明,broken 或不一致都算 issue)

**R3K4**
severity: major
blocking: 是 — 撤除條件是「8 週被照做改掉的是 0 行就撤那一條」,spec 沒說這個數怎麼量,照字面實作會留下一條永遠判不了的撤除條件。
- 輸入是上線 8 週後要判斷結構性提醒該不該撤,走到 RETIRE-IF 與 S15。
- 否定現況句的先例在 `_note_shape_negation_emit` 只記「hinted」帳,內容是幾行、幾篇兩個整數,註解寫明「沒有片段、行雜湊、路徑」。
- 該案刻意不記行雜湊和路徑,所以事後無法判斷「被提醒的行後來有沒有改」。
- 本案沒定義:
  - H1、H2、H3、已作廢缺連結要不要記帳。
  - 記哪個 `check` 名。
  - 靠什麼認出「這行被改掉」。
- 若沿用先例,被改掉的行數量不到;若新增逐行記錄,又和先例刻意不留片段的設計衝突,而 spec 完全沒碰。
- 另一個風險:H1、H2、H3 若共用 `("note-shape","hinted")` 且不分 `check`,否定現況句的量測會把它們混在一起。
- 引句:「結構性提醒單獨看:8 週被照做改掉的是 0 行就撤那一條」
- 佐證 file: `scripts/lumos:25883`(`hinted` 帳的 `extra` 只有 `check/lines/notes`)

**R3K5**
severity: minor
blocking: 否 — 回退次序有相依,但不照順序也不會直接壞系統,補一句順序即可。
- 〈回退〉說「第 3 步:`note_shape.tag_hints: off` 或還原提交」。
- 開關是第 0 步才加的,第 3 步的 H1、H2、H3 依賴它。
- 〈回退〉的各步沒有「由後往前還原」的限制。先還原第 0 步、第 3 步仍在,H1、H2、H3 會失去 off 的出口。
- 消費專案已寫進 `.lumos/config.json` 的 `tag_hints: off` 也會被靜默忽略。
- 引句:「第 3 步:`note_shape.tag_hints: off` 或還原提交。」

**R3K6**
severity: minor
blocking: 否 — 步驟順序導致中間態指令不存在,AI 會跑出參數錯誤,但可自行修復。
- 〈分期〉第 1 步寫規格、範本指路,第 4 步才做 `lumos search --about ... --prefix ...` 與 skill 查詢表那一行。
- 〈改程式時的分類檢查清單〉裡引用的取行指令要等第 4 步才存在。
- 分期沒說清單寫在哪一步。若第 1 步就落地,第 1 步到第 4 步之間消費專案的 AI 會照指引跑不存在的旗標。
- 〈回退〉第 4 步「還原提交即可」也沒包含清單與範本裡指向這支旗標的那段文字。
- 引句:「4. **搜尋行模式**:`--prefix`、`--about`、行模式、`--include-retired`、`hidden_lines`;skill 查詢表加一行。」
- 佐證 file: `scripts/lumos:40167`(目前 `search` 只有 `term` 必填、沒有 `--prefix`、`--about`、`--include-retired`)

**R3K7**
severity: minor
blocking: 否 — 派工詞升版再還原時,進行中的清單與新格式報告會被舊程式讀歪,只影響進行中的批次。
- 輸入是第 2 步升 `_NOTE_AUDIT_PROMPT_VERSION` 到 2、報告多一欄前綴,之後還原。
- 判定檔(JSON)多一個 `prefix` 鍵,舊程式的 `_note_audit_parse_verdict` 只檢查 `id` 與 `class`,所以舊程式讀得下,這點成立。
- 報告表格不一樣:`_note_audit_parse_report` 用位置切欄(`cells[2]` 是證據、`cells[3]` 是理由)。
  - spec 沒定新欄放哪。
  - 若放在 class 之後(最自然),還原後舊解析會把前綴當成證據,證據檢查和 `evidence_ok` 全錯。
- 還原版本號到 1 後,在 v2 期間 prepare 的清單,在 `record` 時 `str(lst["version"]) == str(_NOTE_AUDIT_PROMPT_VERSION)` 為假。
  - 輕的判定一律被丟掉,訊息是「來源對不上,輕的判定不收」。
  - 只有重新 prepare 能解,spec 沒寫。
- 引句:「第 2 步:派工詞與版本號還原;多一欄的新紀錄舊程式讀不到那一欄,其他欄照讀。」
- 佐證 file: `scripts/lumos:26475`(`_note_audit_parse_report` 位置切欄)
- 佐證 file: `scripts/lumos:26705`(`prov_ok` 比對版本號)
- 佐證 file: `scripts/lumos:26188`(`_note_audit_parse_verdict` 只驗 `id/class`)

**各節覆核**
- 〈分類規格〉〈分類檢查〉〈搜尋行模式〉:已讀,除上述外無回滾面 finding。
  - `--prefix` 和 `--include-retired` 是純新增旗標。
  - `term` 改成可省略不影響既有呼叫。
  - 既有的 `--include-superseded` 沒被改。
  - `--path` 的縮寫 `--p` 會變成有歧義,實務上沒人這樣打,不標。
- 〈不溯及既往〉:已讀,同 R3K1 的提醒只在 `--staged` 路徑。
- 實務隱患逐類:
  - 併發:無,新增寫入都沿用既有的治理帳與判定檔寫入點(append-only)。
  - 效能:無,只多字串比對。
  - 資源:無,不開長駐程序。
  - 回滾:有,見 R3K1 到 R3K7。
  - 相容:有,見 R3K7。
  - 注入:無,判定者讀的是筆記文字,沿用現有「筆記是資料」規則。
  - 自我治理:有,見 R3K1、R3K2、R3K3 三處「只提醒」其實會擋或變紅。
  - 金流、對外送出:已排除,理由成立。
  - 不可逆:不改資料、不刪筆記,但治理帳是 append-only,已寫進去的事件還原提交後不會消失,和 R3K4 相關。
- 前兩輪修正有沒有補上:
  - 已補上:r2 的「到期提醒送不到」(doctor 清單)、範本兩處說法、W4 開關先後、RULE 的 superseded 訊息衝突。
  - 沒補上:doctor 清單沒有關閉手段(R3K2),範本改動對消費專案 CI 的影響(R3K3)。

最高嚴重度:major,blocking 4 條
