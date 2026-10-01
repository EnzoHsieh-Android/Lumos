severity: major

固定席筆記:這次沒有 hook 附在尾端的固定席筆記,無法逐條判。我自己的判斷:這份設計沒有改動既有的 `note-shape` 判定契約。它在舊規則旁邊加新規則,舊記號 `note-shape --staged` 仍被新記號包含。唯一動到既有行為的點是 R3K1。

驗證過、補得對的上輪修補(開檔對過,無 finding):
- `git log -S` 找上線點的語意,和「新記號包含舊記號」吻合。
- 每個提交各自判定掛鉤有沒有記號(per-commit liveness)的機制已存在,在 `scripts/lumos` 的 `_notelines_range_added` 內。
- `[被取代:節點#dN]` 的來源 `decision-add` 確實印 `<rel>#d<N>`。
- `drift ack` 載入時濾掉未知種類,見 `scripts/lumos:29331`,所以第 2 步回退「留在檔裡無害」成立。
- `[retire:when-file:…]` 不會誤觸既有的 `_PROBE_ANY_RE`(它要求 `[when-` 緊接在方括號後),`_PROBE_KEYS` 四種鍵與 `_probe_value_err` 都存在。
- 「判不了」是 `_drift_check_core` 回傳的第三個清單,可以另列。

---

**R3K1**
severity: major
blocking: 是——照 spec 的回退順序,可能讓提交時的整道筆記形狀擋靜默失效,實作者會做出壞系統。
1. 輸入:已把 `--slots` 加進掛鉤的消費專案,之後工具鏈只還原第 1 步程式。
2. 第 1 步的回退只寫「先 `note_shape.slots: off`,再還原」,沒有要求先把掛鉤範本的 `--slots` 拿掉。
3. 還原後,掛鉤仍執行 `note-shape --staged --slots …`。`scripts/lumos:41284` 的 `ap.parse_args()` 是嚴格解析,未知旗標會讓 argparse 以 rc 2 結束。
4. `scripts/hooks/pre-commit:227-232` 只在 rc 等於 1 時才擋,其他非零一律放行。結果是提交時的行號引用、FACT 來源、REVISIT 格式、否定現況句整套檢查都靜默跳過,也不寫治理帳。
5. 只有推送時的 `--diff` 還能補上,但那條路沒帶 `--slots`。
6. 前提也要更正:「程式全機即時生效,但掛鉤要各專案更新」不成立。`scripts/lumos` 與 `scripts/hooks/*` 都在 `_VENDORED_TOOLKIT`/`_VENDORED_TREE_FILES`(`scripts/lumos:18500-18520`)裡,掛鉤呼叫的是 `$REPO_ROOT/scripts/lumos`。程式與掛鉤是同一輪 `lumos update` 一起到的,不是程式先全機生效。
7. 建議:第 1 步要求永久保留 `--slots` 當被接受的旗標(還原後也留,可為空操作)。或者把「先拿掉掛鉤的 `--slots`」列為第 1 步回退的前置條件。
引句:「第 1 步:`note_shape.slots: off` 先停,再還原。」
佐證行 file: `scripts/hooks/pre-commit:227`、`scripts/lumos:41284`、`scripts/lumos:18500`

**R3K2**
severity: major
blocking: 是——必有鍵表同時被歸在第 0 步和第 1 步,實作順序與回退順序都會出錯。
1. 第 0 步寫「lint 改讀同一張表」,第 0 步要自己能跑,表必須在第 0 步就存在於程式裡。
2. 第 1 步又把「必有鍵表」列為擋的程式的一部分。
3. 若實作者照第 1 步把表放在那裡,第 0 步的 lint 讀不到表(NameError)。
4. 若放在第 0 步,第 1 步的清單就是錯的。
5. 回退順序是「第 1 步先、第 0 步最後」。照字面還原第 1 步會連表一起拿掉,第 0 步的 lint 就壞。
6. 建議:明寫表屬於第 0 步,第 1 步只引用它。
引句:「**擋的程式**:必有鍵表、`--slots` 旗標與格子上線點」
佐證 file: `scripts/lumos:5428`(lint 呼叫 `context_marker_warnings`)

**R3K3**
severity: major
blocking: 是——回退承諾要的是部分還原,但步驟定義成同一個提交,「還原提交」做不到。
1. 第 0 步是規範、前綴、lint、解析器、範本、skill、骨架提示的合併,還要跟分類計劃第 0 步併成同一次。
2. 回退卻承諾「只還原範本、skill 與骨架提示;SEE 留在前綴表與算計劃連結的程式裡」,同一段又說「lint 回到舊判準」。
3. 前一句沒列 lint 與解析器,後一句又要還原 lint,兩句互相矛盾。
4. 若實作者照字面做成一個提交,`git revert` 會把 SEE 一起拿掉:
   - `SYMBOL_NAMES`(`scripts/lumos:3261`)少了 SEE,所有已寫的 `SEE:` 行會被 lint 唸成「非標準符號行」(`scripts/lumos:5416`)。
   - `_plan_system_links`(`scripts/lumos:6215`)只認 `DEP:`,SEE 的連結會漏算,影響計劃連到哪些節點的判定。
5. 這正是 spec 自己承諾不會發生的事。
6. 建議:第 0 步明寫拆成至少兩個提交,SEE 註冊加讀連結為「惰性前綴」一個,範本、skill、骨架、lint 另一個。並說明 lint 與解析器那部分到底還不還原。
引句:「第 0 步:最後還原,而且只還原範本、skill 與骨架提示;SEE 留在前綴表與算計劃連結的程式裡」
佐證 file: `scripts/lumos:3261`、`scripts/lumos:6215`

**R3K4**
severity: major
blocking: 是——lint 改讀同一張表,會對舊筆記的 FLOW/DEP 大量新增警告,跟「舊筆記不檢查」矛盾。
1. 「怎麼分新舊」只認兩種舊寫法:冒號後第一個是 `[日期`,或 RULE 的 `[retire:]` 非機器式。
2. 舊的 FLOW/DEP 行都不屬於這兩種。
3. 表裡 FACT/FLOW/DEP 必有 `[來源:]` 與 `[confirmed:]`。「其他都算新文法、用新表」,這些舊行就全被當新文法唸缺鍵。
4. 現有程式刻意避開這件事:`scripts/lumos:3268` 的註解寫明 FLOW/DEP 接進 lint 會對舊帳一次噴警告,所以 lint 只套 FACT。
5. 我在 `docs/lumos-toolchain-knowledge` 數了摘要裡有內容的行:DEP 184 行、FLOW 87 行,全沒有 `[來源:]`。FACT 11 行,只有 3 行有。
6. 消費專案更新後的警告量更大,規模取決於它們的舊筆記。
7. 建議:明寫 lint 讀表時只套 WHY/RULE/PITFALL/FACT,或加一個「舊式 FLOW/DEP」豁免判準;不然要把這道警告量列進第 0 步的預期,並寫回頭撤除條件。
引句:「其他都算新文法、用新表」
佐證 file: `scripts/lumos:3266`、`scripts/lumos:25907`

**R3K5**
severity: major
blocking: 是——處理過的 RULE 會永遠被 doctor 重複提醒,而且沒有出口。
1. 第 123 行把 RULE 的 superseded 訊息從「整行刪掉」改成「留著並寫 `[被取代:]`」,作廢的 RULE 會留在檔裡。
2. 推送時的抽取只在第 130 列寫了「已標 `[status:superseded]` 的行不抽」。
3. doctor 列(第 131 列)的「工作目錄裡條件現在已成立」沒有同樣的排除,「沿用 `drift scan` 的工作目錄判定」也不會自帶排除。
4. 撤除條件成立 → 作者依指示標 superseded 並留著 → 條件永遠成立 → doctor 每次都再提醒這一行。
5. 唯一的出口是刪掉那行,卻與第 123 行的指示相反。
6. 建議:第 131 列也寫明略過 `[status:superseded]` 的行。S13 加一條對應案例。
引句:「工作目錄裡條件現在已成立(兜底:轉變那次判不了或被跳過就再也不會被擋)」
佐證 file: `scripts/lumos:3375`(現行訊息叫人刪行)

**R3K6**
severity: minor
blocking: 否——只是兩句規則互相打架,實作者能先裁定,不會做出壞系統。
1. 第 107 行說「補連結都不會被擋」。
2. 核心一句定義為「整行去掉前綴與所有欄位之後剩下的文字」,`[[連結]]` 不是欄位。
3. 所以 `DEP:[[A]]` 補成 `DEP:[[A]]、[[B]]`,核心一句變了,算新寫,會被 S4「只放連結的新寫 DEP 應被擋並提示改用 SEE」擋下。
4. 既有的 `_ns_check_line`(`scripts/lumos:25907`)對只放連結的 DEP 是整個豁免,新規則反過來要擋。
5. 建議:要嘛刪掉「補連結」,要嘛明寫補連結的 DEP 行怎麼算。
引句:「補 `[confirmed:]` 重新確認舊 RULE、補連結都不會被擋」
佐證 file: `scripts/lumos:25907`

**R3K7**
severity: minor
blocking: 否——只在上線前開分支、上線後才合進來這個罕見情境才誤擋,有單次跳過可用。
1. 情境:feature 分支在掛鉤帶 `--slots` 之前從 main 切出。
2. 分支上的 A 提交(掛鉤無記號,不查)寫了舊式 PITFALL 行。
3. 之後合進 main 的新掛鉤,B 提交(掛鉤有記號)只補了該行的 `[test:x]`。
4. 推送時「上一版」是範圍起點那一版,裡面沒有 A 寫的那行,B 補的行被當新行,缺 `[出處:]` 與 `[根因:]` 被擋。
5. 既有的 `_notelines_range_added`(`scripts/lumos:25573`)把「還沒上線的提交寫的行」另收進 `old_by`,正是為了這種情況。spec 沒說格子規則要不要照用。
6. 這違反 S7「不溯及既往」的承諾。
7. 建議:舊行判定把非上線提交寫的行也算進「上一版」。
引句:「推送時是推送範圍的起點那一版(不是逐提交的上一個提交」
佐證 file: `scripts/lumos:25573`

**R3K8**
severity: minor
blocking: 否——只影響 RETIRE-IF 抽查的準度,不影響擋與放行。
1. 擋下事件:現有 `_note_shape_report`(`scripts/lumos:26481-26497`)一次提交只記一筆 `blocked`。spec 想標 `check:"slots"`,但格子違規與行號、FACT 來源違規可能同一次出現。要標成哪一種沒寫。
2. 單次跳過事件:`LUMOS_SKIP_NOTE_SHAPE` 在 `cmd_note_shape` 最開頭(`scripts/lumos:26370`)就 return,commit 與 `--diff` 兩條路都會。pre-push(`scripts/hooks/pre-push:359`)也是同一支。
3. 若使用者在提交時跳過、推送時又設同一個環境變數,會記兩筆帶 `slots_lines` 的跳過事件,同一批筆記路徑、同一個 30 分鐘窗口,RETIRE-IF 的分子會被灌水。
4. 「單次跳過時先算一次格子違規」還要求把跳過判斷移到取得 vault、設定、範圍之後,spec 沒提。
5. 建議:寫明哪個階段才記 `slots_lines`,或在配對時依 `attempt_id` 去重。
引句:「單次跳過時先算一次格子違規(只是新增行的字串比對)」
佐證 file: `scripts/lumos:26370`、`scripts/lumos:26481`

**R3K9**
severity: minor
blocking: 否——度量那段是 doctor 提醒,錯了只是誤報或漏報。
1. 度量的 N 允許到 26 週,檔尾只讀 24MB。
2. 目前 `docs/.governance-log.jsonl` 是 15.9MB、涵蓋 89 天、約 10 萬行,也就是約 180KB/天,24MB 大約只裝得下 130 天。再過約 45 天,N 大於約 18 週的度量就看不到完整窗口。
3. 既有 A2 讀法(`scripts/lumos:2053-2090`)有 `_from`/`_oldest` 判斷檔尾是否截斷。spec 只寫「歷史短於 N 週不判」,沒說「歷史」是整份檔還是被截斷的檔尾。
4. 若實作者漏掉截斷判斷,`<`/`==` 比較(例如「近 26 週事件數 < 1」)會被誤判成立。
5. 白名單「從 `_gate_event_or_warn` 的呼叫點整理」靜態整理不全:`scripts/lumos:25433`、`26880`、`26905`、`31328`、`38471` 的閘名或種類是變數。白名單與呼叫點之間也沒有釘住的測試。
6. 建議:把 N 上限降到檔尾能蓋住的範圍,或明寫截斷時不判;白名單加漂移測試。
引句:「doctor;一次 doctor 只讀一遍治理帳檔尾(上限照既有 24MB),所有度量共用」
佐證 file: `scripts/lumos:2053`、`scripts/lumos:25433`

**R3K10**
severity: minor
blocking: 否——只是回退流程少一步,補上即可。
1. 開擋步與它的回退都要改 `scripts/hooks/pre-commit`,這支在 `ANCHOR_FILES`(`scripts/lumos:19931-19938`)。
2. 工具鏈自己的 `pre-push`(`scripts/hooks/pre-push:239`)有 `anchor verify`,內容和基準線不符就擋推送。
3. 開擋與回退都需要 `lumos anchor approve --note …`,spec 兩處都沒寫。
4. 急迫回退時這是會卡住推送的一步。
5. 建議:兩處補上這一步。
引句:「開擋步:把 `--slots` 從掛鉤範本拿掉;已更新的專案再一輪 `lumos update`」
佐證 file: `scripts/hooks/pre-push:239`、`scripts/lumos:19931`

**R3K11**
severity: minor
blocking: 否——是成本與既有提醒的惡化,不是錯誤行為。
1. spec 把整段格子規格(約 6.4KB 文字,含五行例子)放進紀律範本,而範本每回合注入每個消費專案的 CLAUDE.md/AGENTS.md。
2. `scripts/templates/graph-discipline.md` 已是 11485 bytes。doctor Check D 的瘦身提醒門檻是 5256 的 150%,也就是 7884 bytes(`scripts/lumos:2856`),已經超標,屬既有提醒。
3. Codex 的 AGENTS.md 有 32KiB 靜默截斷上限,doctor 在單層超過 75% 才提醒(`scripts/lumos:2866`)。範本再變大,對那些 AGENTS.md 已經偏大的專案是實際風險。
4. 「實務隱患」的資源段沒提範本體積。
5. 建議:範本只放前綴表、必有鍵表、一個例子,其餘細節放 skill 子檔。
引句:「紀律範本的前綴表改成格子規格(單一來源)」
佐證 file: `scripts/lumos:2856`、`scripts/templates/graph-discipline.md`

**R3K12**
severity: minor
blocking: 否——是釘住測試的投影規則不夠具體,實作者可以自己補定義。
1. S11 要比對「前綴 → 必有鍵集合」,拆表格後去掉反引號與 `\|` 轉義。
2. PITFALL 格寫成「`[出處:]` `[根因:]`,再加 `[test:]`、`[repro:指令]`、`[防回歸:無 理由]` 三選一」。
3. 照「只去反引號與轉義」投影出來,`test`/`repro`/`防回歸` 三個都是必有。程式裡卻是三選一。
4. RULE 格的 `[依據:人\|外部\|審計\|法規\|相容]` 還有「`[retire:人裁]` 另必有 `[until:]`」兩層條件。
5. 照字面做,要嘛測試永遠紅,要嘛投影把條件式擠平而失去釘住的意義。
6. 建議:規定範本表裡一律「全必有」與「三選一/條件必有」兩種寫法,並說明各自如何投影。
引句:「再加 `[test:]`、`[repro:指令]`、`[防回歸:無 理由]` 三選一」
佐證:無(純 spec 內部)

---

各節:
- 格子規格(文法、欄位、值、重複鍵、作廢):已讀,除 R3K6、R3K12 外無 finding。
- 擋:R3K1、R3K7、R3K8。
- lint 與擋同一張表:R3K2、R3K3、R3K4、R3K12。
- 格子欄位的過期檢查:R3K5、R3K9。
- 分期:R3K2、R3K3。
- 天花板、不做:已讀,無 finding。
- 驗收條款:S4 中「只放連結的 DEP/FLOW 要擋」與既有豁免相反,見 R3K6。其餘已讀,無 finding。
- 回退:R3K1、R3K3、R3K10。
- 合約候選、審計修正紀錄:已讀,無 finding。

實務隱患逐類:
- 併發:無。新增寫入只有治理帳,沿用既有的 append。
- 效能:無。必有鍵是字串比對。新增的舊版文字比對讀的是 HEAD 與範圍起點兩版,和既有批次讀同階。
- 資源:有,範本體積,見 R3K11。治理帳檔尾讀取上限,見 R3K9。
- 相容:有,見 R3K1(旗標孤兒)、R3K3(SEE 惰性前綴)、R3K4(lint 對舊筆記)。
- 注入:無新洞。擋下訊息已有截斷與清控制字元。
- 自我治理:有,見 R3K8(跳過帳)、R3K10(錨點核可)。
- 金流、對外送出:無,只讀筆記與程式文字。
- 不可逆:無。不改資料、不刪筆記。但回退 R3K1、R3K3 要先定義清楚才退得乾淨。

最高嚴重度:major,blocking 5 條
