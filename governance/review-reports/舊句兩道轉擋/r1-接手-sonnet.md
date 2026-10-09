severity: major

固定席節點:派工尾端沒有附,不適用。

我讀了整份 spec。程式對照用的是 aspidochelone-reread-block 這個 repo(路徑省略前綴)。下面 1 到 4 是 major,5 到 12 是 minor。

## 1
severity: major
blocking: 是(major 就要在實作前修)

- **spec 段落**:〈原問題與範圍〉第一條,以及〈設計〉的預設翻轉。
- **引句**:
  引句:「Enzo 2026-10-09 裁:不等兩週量測,直接擋」
- **撞牆場景**:
  - 三個月後的接手者讀 `Systems/存量漂移守衛.md`,會讀到一條四個欄位都齊的 RULE。RULE 說舊句檢查開關沒寫時是 warn。
  - 這條 RULE 的 `[confirmed:2026-09-30]` 在半年內,依 CLAUDE.md 有挑戰程式碼的效力。新程式把預設翻成 block,就違反了這條 RULE。接手者會照 RULE 把程式改回 warn。
  - spec 沒說這條 RULE 要撤除、作廢或改寫。
  - `Projects/舊句檢查_計劃.md` 的 RETIRE-IF 寫「樣本不足一律延長…不能因為沒有壞訊號就轉擋」。它的 REVISIT 是 2026-10-14 和 2026-12-14。人裁翻案之後這些日期還會跳出來要求量測。
  - `Projects/守檔筆記對照改動_計劃.md` 還有三條會變謊的條款,都綁了測試。S7 寫「回 0…記恰好一筆 skipped」,S9 寫「continue-on-error: true」,S13 寫「是 block…應照 warn」。做法段落(第 88、89、91、107 行與〈實務隱患〉第 146 行)也還寫著「任何情況都回 0」「只提醒」。
  - spec 只把這份計劃放在 `related`,沒要求這些條款作廢或改寫。
- **查證**:
  - file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:82`(RULE),`:125`(「★那段只提醒、恆放行★」),`:129`
  - file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:36`、`:37`、`:38`、`:43`
  - file: `docs/lumos-toolchain-knowledge/Projects/守檔筆記對照改動_計劃.md:88`、`:89`、`:91`、`:107`、`:120`、`:122`、`:126`、`:146`
  - file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:109`(「恆回 0」、pp_stop_if_signaled 的行數描述)
- **lands_in 三篇該寫什麼**:
  - 存量漂移守衛:RULE 第 82 行以人裁撤除並寫新 RULE;第 125 行和第 129 行的行為句;`drift ack` 多一種 reread。
  - 筆記內容審:第二層讀判定紀錄內容、判不了的分法、第 74 行「對照指紋不含筆記」的註記、第 78 行的輸出說明。
  - bound-tests-gate:第 109 行、第 17 行 WHY 裡的 CI 步驟指紋、掛鉤 rc 處理。
  - 另外要列出需要 amend 或 supersede 的舊條款:守檔筆記對照改動_計劃的 S7、S9、S13,以及舊句檢查_計劃的 RETIRE-IF 和兩條 REVISIT。

## 2
severity: major
blocking: 是

- **spec 段落**:〈設計〉的「照留表態」。
- **引句**:
  引句:「不收 `--tracked-in`(reread 不在會到期的種類裡)」
- **撞牆場景**:
  - 表態只綁路徑加原文加 kind,沒綁對照指紋或判定紀錄。
  - 有人今天為某次程式改動寫了 `--reason "誤判"`,之後那條 RULE 行因為別的程式改動真的過期。新判定紀錄再點出它時,舊表態仍然命中,第二層永遠不擋。
  - 一條 RULE 行可以被預先表態,在判定者還沒判之前就先永久豁免。
  - repo 有明文原則反對這種永久豁免:`_DRIFT_EXPIRING_KINDS` 讓 probe 和 retire 的表態有期限或綁去處。c2、c3 的表態綁 related 和 seq,註解寫「不然會永久豁免之後才收尾的計劃」。
  - spec 把「筆記那一行之後被改」當成唯一失效條件。這個條件對「程式變了但行沒變」的情況無效,而這正是第二層要抓的情況。
- **查證**:
  - file: `scripts/lumos:35035`(`_DRIFT_BOUND_KINDS`)、`:35039`(`_DRIFT_EXPIRING_KINDS`)
  - file: `scripts/lumos:37235`(`_drift_ack_key` 只有 path、text、kind)
  - file: `scripts/lumos:37245-37260`(`_drift_split_acked` 的綁定註解)
- **建議**:表態要記判定紀錄的 contrast_fp 或 material_fp,新指紋出現就失效。

## 3
severity: major
blocking: 是

- **spec 段落**:〈原問題與範圍〉的 ⑥「說明文字一起改」。
- **引句**:
  引句:「的說明文字、doctor 提示行、`--help`、CHANGELOG 一起改」
- **撞牆場景**:
  - spec 沒列清單,落地後這些處所會說謊或誤導。
  - **被擋下的人照訊息走會走錯**:`reread-record` 收尾印「確認是誤判就不動——這一版不需要表態」。手冊第 4 步同樣寫「這一版不用表態」。照做之後結構行沒處理,推送被第二層擋下。
  - 第一層和第二層的擋下訊息,spec 只規定印清單、prepare 指令、照留指令,沒規定印逃生寫法(`LUMOS_SKIP_REREAD_CHECK` 和 `gate=warn`)。逃生寫法只出現在「判不了」那一支。
  - 手冊的先後順序:手冊寫重讀在代碼審留痕之前,因為「改筆記會讓留痕失效」。掛鉤實際是先跑 code-loop,再跑 reread-check。tier-high 分支過了代碼審才被第二層擋下,改筆記就得重審。走表態那條路不用重審,但 spec 沒告訴人優先走哪條。
  - 會變謊的處所如下:
    - 手冊 `06-代碼審與推送.md` 第 73 行「只提醒、不擋」,第 94 行,第 96 行(「它在任何情況都回 0,不需要 continue-on-error 或 || true」)。
    - 手冊 `08-自動跑的.md` 第 7 行(「★reread-check 例外★:只提醒…恆回 0」和「舊句檢查…沒寫是 warn」)。
    - 手冊 `04-自檢與健康.md` 第 14 行(「沒寫是 warn」)。
    - README.md 第 90 行(「函式刪了…只提醒」),第 92 行(「只提醒的檢查」)。
    - `scripts/lumos` 第 49364 行、第 50288 行、第 49367 行(命令表說明)。
    - 掛鉤第 543 行「照推——這道只提醒、不擋」,以及掛鉤和 CI 步驟的註解。
    - `scripts/lumos:34899` 的收尾句。
- **查證**:file: `scripts/lumos:34899`;file: `scripts/hooks/pre-push:543`;file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:73`、`:94`、`:96`。

## 4
severity: major
blocking: 是

- **spec 段落**:〈設計〉最後的「對消費專案的影響」,以及「名稱消失檢查開關」。
- **引句**:
  引句:「要暫緩的專案在 `.lumos/config.json` 寫 `drift_check.old_sentence` 或 `note_reread.gate` 為 warn」
- **撞牆場景**:
  - **old_sentence 不看 gate**:
    - 已設 `drift_check.gate=warn` 或 `off` 的專案,升級後第一次推送會被 old_sentence 擋下。
    - repo 的先例相反:`_drift_retire_config` 沒寫時照總開關 gate,理由是「專案設 gate=warn 只提醒的,升級後不會被新檢查擋」。
    - 掛鉤現有的逃生句也寫「整個專案先只提醒 → drift_check.gate 設成 warn」。
    - spec 沒說這個差異是刻意的,也沒說升級說明怎麼寫。
  - **消費專案的 CI 會變紅**:
    - 手冊第 96 行教消費專案接 CI 時不加 `|| true`,並說這個命令恆回 0。rtb 已照此接線。
    - 這些 CI 在 `lumos update` 之後沒人改任何東西,第一次 rc1 就紅。spec 沒提 CI 是 `lumos update` 帶不到的。
  - **等於每次改程式的推送都要派判定者**:
    - 每支檔有家規則加上提交前「改 code 沒動圖譜」,幾乎每次改程式的推送都有候選。
    - 沒有 claude 或 codex 環境的貢獻者,唯一出路是 SKIP 或改 warn。
    - spec 對這種人沒有交代。
  - **版本號**:CHANGELOG 沒有「未發布」區塊,守衛要求頂部版號等於 `LUMOS_VERSION`(現為 v1.2)。spec 的「同版」沒說要升 v1.3,也沒說會不會觸發 `lumos update` 提示。
- **查證**:
  - file: `scripts/lumos:38510-38522`(retire 沿用 gate)
  - file: `scripts/hooks/pre-push:515`(逃生句)
  - file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:43`(gate=off 的相容性說明)
  - file: `scripts/lumos:270`(`LUMOS_VERSION`)

## 5
severity: minor
blocking: 否(掛鉤回傳碼規則補一句即可)

- **spec 段落**:〈設計〉的「掛鉤與 CI」。
- **引句**:
  引句:「130 交給中斷處理、2 也擋並講參數錯」
- **撞牆場景**:
  - rc 3 到 129 以及 131 以上(例如 OOM 殺掉的 137)沒規定。
  - 現行掛鉤的理由是「被外部砍掉不該擋只提醒的檢查」。改成擋之後這個理由翻轉,spec 又用「不然把閘弄慢或弄壞就能繞過」去擋判不了。
  - 掛鉤丟掉 stderr(`2>/dev/null`)。rc 2 除了參數錯,還可能是 argparse 或 Python 版本過舊,這時掛鉤講「參數錯」會誤導。
  - 工具外未捕捉的例外(rc 1)會變成沒有任何訊息的擋下。
- **查證**:file: `scripts/hooks/pre-push:537-543`;file: `scripts/hooks/pre-push:70-75`(`pp_stop_if_signaled` 是 128 以上才停)。

## 6
severity: minor
blocking: 否

- **spec 段落**:〈設計〉第二層與第一層。
- **引句**:
  引句:「候選全部對照過之後才跑。」
  引句:「第一層與第二層同時成立時兩層都印,記一筆 `blocked`。」
- **撞牆場景**:
  - 兩句互相矛盾。第一層有 `left` 時,第二層是不跑,還是只對已對照的那幾篇跑?
  - 現行 `_note_reread_check` 在 `left` 為空時就記 `covered` 並回 0,實作者必須重構這條路徑。
  - 兩個選項的使用者體驗不同。前者逼出多輪付費判定,後者一次攤開。
- **查證**:file: `scripts/lumos:34990-34995`(`if not left:` 提早返回)。

## 7
severity: minor
blocking: 否

- **spec 段落**:〈設計〉的「判不了的分法」。
- **引句**:
  引句:「環境沒有可判的東西(不是 git 專案、沒有圖譜、淺層 clone、範圍沒有新東西、頂端已在主線)」
- **撞牆場景**:
  - `_note_audit_resolve` 的 `reasons` 只有 `none`、`skipped`、`error` 三種。
  - 淺層 clone 和沒有圖譜的 `skipped`,與「讀不到頂端提交的檔案清單(git 失敗)」的 `skipped` 混在同一種。spec 要求前者回 0,後者算判不了而擋下。
  - 實作者若按 `skipped` 一律擋,所有 CI 沒設 `fetch-depth: 0` 的消費專案都會紅。若一律放,git 失敗就能繞過。
  - spec 沒說要拆開。
- **查證**:file: `scripts/lumos:33738-33741`(shallow),`:33761-33768`(沒有圖譜),`:33773-33775`(git 失敗,三者同為 skipped);file: `scripts/lumos:34953-34955`(目前對 `kind != "none"` 一律丟 `_NoteRereadStop`)。

## 8
severity: minor
blocking: 否

- **spec 段落**:〈實務隱患〉列既有測試、〈驗收條款〉。
- **引句**:
  引句:「以及斷言舊句檢查預設 warn 的測試;改的是斷言、不是刪測試。」
- **撞牆場景**:
  - 清單不全。
  - `_DR_CI_GATE_STEP_FP` 用步驟名稱「note reread reminder (回頭重讀守檔筆記;只提醒、不擋)」當鍵,連同 `|| true` 和 `continue-on-error` 一起算指紋。spec 要拿掉這兩行,指紋和名稱都得改,`t_ci_yml_matrix_and_gates_shape` 會紅。
  - `t_prepush_gates_stop_on_signal` 斷言掛鉤有恰好 8 行 `pp_stop_if_signaled`,掛鉤改寫會動到。
  - 舊句檢查的預設 warn 斷言散在許多測試,例如 ⑦ 的 `got[4][3]` 與 `got[2][3] == "warn"`,spec 只用一句話概括。
  - 條款缺口:
    - 沒有 warn 模式下判不了回 0 並記 skipped 的條款。
    - 沒有 rc 2(參數錯)的掛鉤條款。
    - 沒有兩層同時成立的條款。
    - 沒有 `drift scan` 排除 reread 的條款。
    - 沒有 doctor 提示行的條款。
- **查證**:file: `scripts/test_lumos.py:62205-62212`;file: `scripts/test_lumos.py:60276`;file: `scripts/test_lumos.py:68384-68386`。

## 9
severity: minor
⚠
blocking: 否

- **spec 段落**:〈設計〉第一層。
- **引句**:
  引句:「對照指紋照舊不含筆記自己的內容:筆記改了不必重判,程式改了才要。」
- **撞牆場景**:
  - 對照指紋含筆記路徑和筆記頂端 `about_code` 各項的 blob。
  - 筆記改名、`about_code` 增減(每支檔有家規則常逼人在同一支線上加 `about_code`),或把主線併進分支而主線動過同一支程式,指紋都會變。已經付費判完的紀錄就失效,第一層再擋,要重判。
  - 這在 spec〈不做〉範圍內,但訊息和手冊都沒提醒,「筆記改了不必重判」是過度簡化。
  - 這個重判成本也沒進 RETIRE-IF。
- **查證**:file: `scripts/lumos:34459-34471`(指紋組成);file: `scripts/lumos:34449-34456`(`_note_reread_about`)。

## 10
severity: minor
⚠
blocking: 否

- **spec 段落**:〈設計〉第二層的輸出。
- **引句**:
  引句:「印每一行(路徑、頂端版行號、原文節錄、判定理由、照留指令)」
- **撞牆場景**:
  - 這是第一次把筆記內文(不只路徑)和判定者的 `why` 印進終端,並要使用者照貼指令。
  - 現有的 `drift ack` 貼上指令為了防控制字元,有「帶特殊字元就不印、請手動表態」的處理(m1 的 PITFALL)。spec 沒說第二層沿用。
  - `drift ack` 讀工作目錄的筆記,行號卻是頂端版的行號。推非 HEAD 的 ref 或工作目錄有未提交修改時,行號會對不上,可能被 S11 誤擋,甚至表態到錯行。
- **查證**:file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:89`(貼上守衛 PITFALL);file: `scripts/lumos:37427-37433`(`cmd_drift_ack` 讀 `env_text`)。

## 11
severity: minor
blocking: 否

- **spec 段落**:〈做法〉RETIRE-IF、REVISIT。
- **引句**:
  引句:「`skipped-env`(用 `LUMOS_SKIP_DRIFT_CHECK`/`LUMOS_SKIP_REREAD_CHECK` 單次略過)」
- **撞牆場景**:
  - `LUMOS_SKIP_DRIFT_CHECK` 整道 drift check 一起略過,帳上只有 `drift-check` 加 `skipped-env`,沒有 `check` 欄,分不出是舊句檢查的人還是 c1 到 c5 的人。這會誤觸發 RETIRE-IF。
  - 第二層擋下的結構行要抽樣判誤報,但 spec 沒說 `blocked` 事件要記哪些行。
  - CI 擋下沒有治理帳事件,無法計次。
  - REVISIT 日期 2026-12-04 是以 spec 建立日起算,不是上線日。
  - 還有一個與「CI 也判得出」有關的限制:`_push_range_start` 對已在主線的頂端回 `none`,主線推送在 CI 上是跳過的。CI 只補分支推送,直推主線加 `--no-verify` 兩邊都看不到。
- **查證**:file: `scripts/lumos:38597-38599`;file: `scripts/lumos:44705-44731`(頂端已在主線則回 None)。

## 12
severity: minor
⚠
blocking: 否

- **spec 段落**:〈實務隱患〉的已排除項。
- **引句**:
  引句:「已排除:對外送出:閘只讀本機版控裡已提交的判定紀錄與表態檔,推送當下不呼叫模型、不送資料到外部」
- **撞牆場景**:
  - 閘本身確實不外送。但改擋之後,要讓閘過就必須把筆記全文加程式 diff 交給判定者(Codex 編排時是外部服務)。原本可忽略的外送,變成推送的必經步驟。
  - 對有程式碼保密要求的消費專案,出路只剩 warn 或 off,spec 沒提。
  - 排除理由的字面成立,但實質風險沒被答到。
- **查證**:file: `scripts/lumos:34868-34876`(prepare 輸出的派法含 `codex exec`)。

## 實務隱患鏡頭逐類

- **金流**:無,只動本機與 CI 的回傳碼。
- **對外送出**:見 12 ⚠。
- **不可逆**:無。擋下可靠改設定或還原恢復。但設定檔從被推頂端讀取,同一次推送可以順手把 gate 改成 warn 自我解除。這是所有閘共有的既有性質,spec 也把 warn 當逃生,不算新洞。
- **效能與資源**:
  - 30 秒軟上限逾時現在會擋。大型單一庫或 CI 冷機器風險較高,出口只有 SKIP。
  - 判定紀錄內容的讀取沒有大小上限。任何貢獻者都能提交一個超大的 `<對照指紋>-….json`,讀取逾時就成了判不了。
  - spec 只說「各數 KB」。⚠
- **並行**:
  - 同一個 repo 的兩個會談各自記判定紀錄,檔名有時間加亂數,不衝突。
  - 表態檔用既有鎖。
  - 另一個會談未提交的紀錄會被 `wip` 提醒,但不算數。
  - 無新風險。
- **資料一致與相容**:見 4 和 9。
- **安全**:見 10。
- **觀測**:見 11。

## 已讀無 finding 的節

- 〈原問題與範圍〉的基線數字:我在 `docs/.governance-log.jsonl` 實數,舊句 passed 為 35,重讀 reminded 為 18、recorded 為 5、none 為 12,與 spec 相符。
- PRIOR-ART:已讀,無 finding。其中「實驗二這類行 6 行裡 5 行是真問題」在來源計劃(第 102 行)標明是「不是本案承諾」的起點建議,樣本只有 6 行。這一點沒新增 finding。
- 〈回退〉:已讀,無 finding。我查了 `drift scan` 讀到不認得的 kind 確實會略過(`_drift_load_acks` 過濾 `_DRIFT_KINDS`),回退成立。
- 〈設計〉的「重讀開關」:已讀,無 finding。我核對了 `_note_reread_config` 的四種壞設定,現況是 warn,spec 描述正確。

最嚴重的是第 1 項:翻預設會直接違反一條仍有效的 RULE 與多條綁測試的舊條款,spec 沒有處置它們。blocking 共 4 條(第 1 到 4 項)。
