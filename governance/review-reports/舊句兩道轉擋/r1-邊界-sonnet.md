severity: major

派工尾端沒有附固定席節點,所以沒有節點可逐條判。以下 13 條是對照 `scripts/lumos` 與測試檔實際讀碼後的結果。

## finding

### 1. 結構行定義把大半摘要行都納進來,「波動最少的一類」不成立
severity: major
blocking: 是(會讓第二層擋下範圍遠大於設計宣稱)
- 位置:〈設計〉重讀第二層第一個子項、〈實務隱患〉第一條。
- 輸入:判定者點出任何一行含 `[test:` 的 WHY、PITFALL 摘要行,或正文裡只是提到 `[test:` 這個語法的說明句。
- 壞在哪:這些行全部算結構行,頂端版還留著就擋。
- 數字:在 `docs/lumos-toolchain-knowledge` 數,行首是 `RULE:` 的有 23 行,含 `[test:` 的有 1735 行,含 `★INVARIANT★` 的有 205 行,有前綴的摘要行共 2891 行。所以真正擋的是約六成的摘要行,不是 RULE 那一小類。
- 真實樣本:`governance/reread-verdicts/` 五份裡唯一一列被判成結構行的,是 WHY 行靠 `[test:` 才中。
- 依據不足:spec 的 PRIOR-ART 引的是 `Projects/守檔筆記對照改動_計劃.md:102`「實驗二這類行 6 行裡 5 行是真問題」。同篇第 102 行明寫「不是本案承諾」,第 155 行寫「準度只在 rtb 驗過一次」,複判一致率約三分之二。
引句:「以 `RULE:` 開頭、或含 `★INVARIANT★`、或含 `[test:`」
引句:「只擋結構行把波動限制在最少的那一類」

### 2. 第二層何時跑,spec 前後矛盾
severity: major
blocking: 是(核心演算法有兩種互斥讀法)
- 位置:〈設計〉重讀第二層。
- 矛盾:第 39 行說第二層在「候選全部對照過之後」才跑,也就是 `left` 為空。第 44 行又說第一、二層「同時成立」時兩層都印。`left` 非空時第二層根本不跑,同時成立不可能發生。
- 沒講清的行為:若要同時成立,第二層就得對「有紀錄的那幾篇」先跑。這時候選一半有紀錄一半沒有,結構行掃描要不要做、用哪個 `done` 集合,spec 都沒說。
- 驗收條款:S3、S5 各測一層,沒有任何一條涵蓋同時成立。
引句:「候選全部對照過之後才跑」
引句:「第一層與第二層同時成立時兩層都印」

### 3. 「判不了」與「環境沒東西」的分法,現有介面分不出來,而且判不了時用哪種模式也沒交代
severity: major
blocking: 是(照 spec 寫會把兩類混在一起)
- 現況:`_note_audit_resolve` 回報的 reasons 只有 none、skipped、error 三種。
  - 淺層 clone(`scripts/lumos:33721`)、「讀不到頂端提交的檔案清單(git 失敗)」(`scripts/lumos:33759`)、「這個專案沒有圖譜」(`scripts/lumos:33764`)全是 skipped。
  - `_note_reread_check` 對 skipped 一律 `raise _NoteRereadStop`(`scripts/lumos:34953`)。
- spec 要的:淺層 clone 與沒有圖譜回 0,讀不到檔案清單的 git 失敗要 block 回 1。要做就得改這個共用函式的契約,或比對字串,spec 沒提。
- 模式取得:外層 `cmd_note_audit_reread_check` 的 except 要依 gate 決定回 1 或 0,但 `mode` 是在 `_note_reread_check` 裡讀的(`scripts/lumos:34940-34946`)。例外若發生在讀設定之前,外層拿不到模式,spec 沒說預設走哪邊。
- 附帶:`_nodehome_reader(root, tip0)(".lumos/config.json")` 在 git 失敗與檔案不存在時都回 None,新預設下 git 偶發失敗會讓設 warn 的專案被當成沒設而擋下。
引句:「環境沒有可判的東西(不是 git 專案、沒有圖譜、淺層 clone、範圍沒有新東西、頂端已在主線)」
引句:「`_NoteRereadStop` 帶一個種類」

### 4. 照留表態只綁路徑加原文,一次表態永久免疫之後所有判定
severity: major
blocking: 是(讓第二層擋下可被一次性永久靜音)
- 輸入:甲推送時判定者點出 RULE 行 L,作者表態「照留」。之後程式又改,產生新對照指紋,新判定者再次點出同一行 L(這次可能真的不成立)。
- 壞在哪:`_drift_ack_key`(`scripts/lumos:37235`)的 key 是路徑、原文、種類,沒有指紋或範圍終點。這行表態對每一次新判定都有效,只要原文不變,第二層永遠不再擋它。
- 對照:c2、c3、c6 綁了當時的 related(`_DRIFT_BOUND_KINDS`,`scripts/lumos:35035`),probe 與 retire 有 until(`_DRIFT_EXPIRING_KINDS`,`scripts/lumos:35039`),只有這個新種類既不綁也不過期。
- 說法不實:spec 把「原文對不上才失效」當成足夠。它漏了「原文不變但程式換了」這個最常見情況。
引句:「筆記那一行之後被改,原文對不上,表態自然失效」
引句:「reread 不在會到期的種類裡」

### 5. 對照指紋含 about_code 的 blob,合併或 rebase 一動就失效,CI 在 main 上會紅 ⚠
severity: major
blocking: 是(轉擋後 CI 上不可修的紅燈與重複的判定成本)
- 指紋組成:`_note_reread_contrast_fp`(`scripts/lumos:34459-34469`)含頂端每個 about_code 檔的 blob 編號。`scripts/lumos` 是 90 篇筆記的 about_code。
- 輸入:判定者在分支頂端記錄了紀錄。PR 合併到 main 時,main 已因別的合併改過 `scripts/lumos`,合併後 blob 不同,指紋跟著變。
- 壞在哪:`ci.yml:5-7` 的 CI 在 push 到 main 時跑這一步,是 `BEFORE..SHA` 範圍。候選的指紋在合併提交上算出來沒有對應紀錄,第一層回 1。拿掉 `|| true` 與 `continue-on-error` 後,main 的 CI 就紅。
- 修不掉:補一個紀錄提交到 main,下一次 push 的範圍已不含該程式變動,等於紅燈留在合併提交上。本機 rebase 後同樣得重派判定者。
- 缺口:spec 只寫「改對照指紋的組成」不做,沒討論這個後果,RETIRE-IF 也只計次數。
- 標 ⚠ 的理由:實際會不會發生,取決於 PR 合併前有沒有強制更新到最新 main,我看不到分支保護設定。
引句:「改對照指紋的組成」
引句:「CI 那一步拿掉 `|| true` 與 `continue-on-error`」

### 6. 掛鉤與 CI 的回傳碼處理沒涵蓋崩潰、被殺、舊工具,也沒印逃生說明
severity: minor
blocking: 否(窄情境,有 CI 後盾)
- 掛鉤現況:`scripts/hooks/pre-push:538` 把標準錯誤丟掉。
- 崩潰誤判:Python 例外跳出 `cmd_note_audit_reread_check` 時回傳碼就是 1(例如 `_note_audit_root` 內的非預期例外)。掛鉤會把它當成擋下,訊息卻已被丟掉,使用者看不到原因。
- 其他非零沒交代:spec 只規定 1 擋、130 中斷、2 擋。被 OOM 殺掉(137)、逾時這類其他非零,掛鉤的舊文字是「印一句放行」。spec 的理由是「弄壞就能繞過」,這個漏洞自己卻沒補。
- 舊版衝突:第 539-541 行舊註解寫舊版 argparse 回 2 要放行,spec 把 2 改擋。
- 逃生說明:`drift check` 擋下時掛鉤會印逃生說明,reread 這邊 spec 只在「判不了」時印 `LUMOS_SKIP_REREAD_CHECK`,第一、二層擋下沒有。
- CI 面:`LUMOS_SKIP_REREAD_CHECK` 只管本機,CI 的判不了沒有略過手段,只能把設定改 warn 重推,這句 spec 沒講。
- 消費專案:`lumos update` 帶不到消費專案的 CI(`Projects/守檔筆記對照改動_計劃.md:94`)。〈對消費專案的影響〉沒提 CI 後盾對它們是缺席的,也就是本機繞過沒有後盾。
引句:「回傳 1 就擋、130 交給中斷處理、2 也擋並講參數錯」

### 7. 同一行在筆記出現兩次時的行為沒定義
severity: minor
blocking: 否(罕見,有表態出口)
- 輸入:筆記中兩處有一模一樣的結構行,例如範本句,判定者只點出第 10 行。
- 壞在哪:spec 用原文比對,作者改掉第 10 行,第 50 行的同文仍被當成留著的結構行,於是擋下。
- 沒定義的事:輸出印的是哪一個行號,表態的原文鍵是否同時蓋住兩處(`_drift_ack_key` 是原文,會蓋住),第 50 行判定者根本沒審過卻被擋,這是否合理。
- 其他:結構行若放在 fenced code block 或以 `>` 引用,`>` 不會被當列表符號去掉,開頭判斷失效,只剩「含 `[test:`」可中,規則不一致。
引句:「只看頂端版筆記裡**還一字不差留著**的結構行(逐行去頭尾空白後比對)」

### 8. 讀判定紀錄的方式沒規定,壞檔、大檔、形狀不明都會變成永久擋
severity: minor
blocking: 否(需要手改過的檔案才會觸發)
- 現況:`_note_reread_committed`(`scripts/lumos:34697-34709`)只列檔名,沒讀內容。第二層要新增讀內容的路徑,spec 沒說用哪個函式。
- 大小:現有 `_nodehome_cat_blobs`(`scripts/lumos:29527`)沒有大小上限,另有 `_nodehome_cat_blobs_capped`(`scripts/lumos:29495`)。`reread-record` 的 `text` 沒截斷(只截 `quote` 與 `why`),手改或很長的筆記行會很大。spec 以「各數 KB」帶過。
- 形狀:`rows` 不是清單、某列不是物件、`text` 缺少或不是字串、非 UTF-8、JSON 壞,spec 都只歸入「讀不懂判定紀錄」。
- 同指紋取聯集時:只要有一份壞檔,即使另一份完好,整篇都判不了,block 時只能靠 `LUMOS_SKIP_REREAD_CHECK`(CI 不認)或刪掉那個檔。這個補救步驟 spec 沒要求印出來。
- 同類:表態檔壞行會被 `_drift_jsonl_parse` 靜默略過(`scripts/lumos:37198`),表態悄悄失效,輸出只會再擋一次,沒有提示原因。
引句:「讀頂端提交裡、檔名前綴等於它對照指紋的**所有**判定紀錄」
引句:「每篇候選多讀幾個小 json(各數 KB),在 30 秒預算內」

### 9. 輸出沒寫逃脫與引用處理,也沒有上限
severity: minor
blocking: 否(實作時可補,但 spec 該寫明)
- 資安:判定紀錄的 `text`、`why` 與筆記路徑都來自已提交內容。現有程式輸出一律過 `_note_reread_show`(`scripts/lumos:34360`),註解標明是為了擋控制字元與雙向覆寫。新增的「原文節錄、判定理由、照留指令」若漏過這道,會回到已修過的問題。
- 照留指令:筆記名可含空白或引號,要像 `_note_reread_cmdline` 那樣 `shlex.quote`,spec 沒提。
- 上限:`drift check` 列出上限是 20 條(`_drift_print_findings`,`scripts/lumos:38565-38577`),第一層列清單上限是 `_NOTE_REREAD_LIST_MAX`(10)。第二層「印每一行」沒有上限,而每一行要一個指令表態,每次指令要讀整個 vault 並取寫鎖。
- 行號:照留指令是用行號,若被推的頂端不是目前工作目錄的 HEAD,行號可能指到別的結構行,`_drift_ack_line_err` 只驗「是不是結構行」,會記成表態。
引句:「block 時印每一行(路徑、頂端版行號、原文節錄、判定理由、照留指令)」

### 10. 設定解析:警告與既有「跟總開關」的先例不一致
severity: minor
blocking: 否(行為差異小,可以在實作時補)
- 缺警告:第 36 行把「寫 null」「整份設定不是物件」列為壞設定、各講一句,但現碼對這兩種不給任何警告。`old_sentence: null` 走 `v is None`(`scripts/lumos:38542-38544`),頂層不是物件也回預設而不講話。S1 的測試描述也沒涵蓋這兩種。
- 與先例相反:`_drift_retire_config`(`scripts/lumos:38503-38505`)明寫「沒寫照總開關 gate」,理由是「專案設 gate=warn 只提醒的,升級後不會被新檢查擋」。新規定讓 `old_sentence` 預設 block 而不看總開關,`gate=warn` 或 `off` 的專案升級後就會被擋。`_drift_check_c` 的訊息(`scripts/lumos:38712`)本來就說「舊句檢查另有開關」,可見是刻意分開,但 spec 沒討論為何與 retire 不同。
引句:「`_drift_old_sentence_config` 沒寫、寫 null、讀不成 JSON、`drift_check` 不是物件、整份設定不是物件、值看不懂時一律回 block」

### 11. 要改的既有測試清單不完整
severity: minor
blocking: 否(實作時測試會紅,但 spec 稱清單是完整的)
- 漏列 `t_ci_yml_matrix_and_gates_shape`(`scripts/test_lumos.py:62244`)。它以指紋釘死後盾每一步的 run、if、continue-on-error、env(`scripts/test_lumos.py:62205-62211`),包括步驟名稱「note reread reminder (回頭重讀守檔筆記;只提醒、不擋)」。拿掉 `continue-on-error` 與 `|| true` 或改步驟名都會紅。`Systems/bound-tests-gate.md` 的 WHY 還寫「後盾步驟的指令逐字照搬」。
- 漏列 `t_drift_m1_layers_and_mode`(`scripts/test_lumos.py:68325`),其中 `scripts/test_lumos.py:68384-68386` 釘「old_sentence 照它的預設 warn」。
- 漏列 `t_drift_m1_review_r2_doctor_old_sentence`(`scripts/test_lumos.py:69717`),釘 doctor 行「預設 warn 不唸」。
- 還有 `scripts/test_lumos.py:64677` 釘「轉擋還沒做」。
- 驗證:S13 的測試 `t_reread_block_hook_and_ci_wiring` 與其餘新測試名目前都不存在(grep 為 0),屬預期,不算缺陷。
引句:「會被新行為弄紅、要一起改的既有測試:`t_note_audit_reread_check_never_blocks`」

### 12. 判定紀錄的真偽與來源沒驗,轉擋的決定被默默落在「不驗」
severity: minor
blocking: 否(守衛立場是防疏忽不防存心)
- `Projects/守檔筆記對照改動_計劃.md:77` 寫「轉擋另案再決定要不要驗」`provenance_ok`。spec 只講讀 `text`,沒說 `provenance_ok: false` 的紀錄是否算數。
- 第一層只看檔名符合正規式(`_NOTE_REREAD_VERDICT_NAME_RE`),手寫一個 `{"rows": []}` 就能滿足。程式本身標明這個閘只防疏忽,所以不嚴重,但這個決定該寫進 spec。
- 真實樣本裡有兩份 `rows: []` 是合法的,所以不能把空 rows 當可疑。
引句:「閘只讀已提交的紀錄,所以 CI 也判得出」

### 13. 「提醒形同虛設」只對重讀成立,名稱消失檢查沒有任何命中樣本
severity: minor
blocking: 否(這是裁量,Enzo 已裁,只是依據要寫準)
- 查帳:`docs/.governance-log.jsonl` 裡 `check: old-sentence` 共 35 筆,35 筆全是 `candidates: 0`、`handle: 0`、`listed: 0`。它從沒真的命中過一個候選。
- 後果:「提醒後去處理不到三成」只對重讀(18 次提醒、5 次記錄)成立。名稱消失檢查預設改 block 的誤報率沒有任何實測,RETIRE-IF 的抽樣因此要等上線後才有分母。spec 該說明這是無資料的轉擋。
引句:「名稱消失檢查 35 次跑完、全是 passed,沒有 warned 或 blocked」

## 逐節
- 〈原問題與範圍〉:數字核對屬實,見第 13 條。
- 〈設計〉:名稱消失檢查開關見第 10 條,重讀開關只有「預設改 block」的小改動,已讀,無 finding。
- 〈設計〉重讀第一層:已讀,無 finding(「對照指紋不含筆記內容」與 `scripts/lumos:34459` 相符)。
- 〈設計〉重讀第二層:第 1、2、4、7、8、9 條。
- 〈設計〉判不了的分法:第 3 條。
- 〈設計〉輸出、照留表態、掛鉤與 CI、對消費專案的影響:第 4、6、9、11 條。
- 〈驗收條款〉:沒有涵蓋同時成立(第 2 條)、重複行(第 7 條)、壞檔(第 8 條)、`null` 與頂層非物件(第 10 條)。
- 〈實務隱患〉:第 1 條駁斥其第一句,第 11 條補其測試清單。
- 〈回退〉:`drift scan` 讀不到未知種類時略過,與 `_drift_load_acks` 的過濾(`scripts/lumos:37232`)相符,已讀,無 finding。
- 交叉引用:`lands_in` 與 `related` 的六個節點都存在。`scripts/hooks/pre-push` 與 `.github/workflows/ci.yml` 屬 `Systems/bound-tests-gate.md` 的 about_code,歸屬合理。

## 實務隱患鏡頭
- 金流:無,只動檢查回傳碼。
- 對外送出:閘本身不送,但轉擋後每次候選都得先派判定者,diff 與筆記全文必然送給外部模型。頻率因此大增,spec 的「已排除」只講閘本身,沒講這個。
- 不可逆:擋下可逆,但表態檔只追加且對指紋不過期(第 4 條),實質上變成不可撤回的永久豁免。
- 守衛面:有,第 1 到 5 條都在這一類。
- 併發與資源:30 秒軟上限加上逾時 block(第 3 條),慢機器與首次推送(空樹起點)會被擋。
- 資安:第 9 條。
- 成本:一次推送最多有候選 n 篇,每篇都要判定者一次。`scripts/lumos` 是 90 篇筆記的 about_code,實際上通常 1 到 5 篇,最壞可到數十篇,spec 沒給上限或分批做法。

最嚴重的是第 5 條(合併或 rebase 讓對照指紋失效,CI 在 main 上變成修不掉的紅燈,⚠ 取決於合併流程)與第 4 條(一次表態永久蓋過之後所有判定);blocking 共 5 條(第 1 到 5 條)。
