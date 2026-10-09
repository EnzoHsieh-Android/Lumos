severity: major

派工尾端沒有附固定席節點,所以那一條不適用。

## 逐節

- **原問題與範圍**:見 F8。
- **PRIOR-ART、RETIRE-IF**:借用的先例有一處講得不對,見 F1。
- **設計/開關**:見 F5、F11。
- **重讀:候選與兩層**:見 F2、F6、F9。
- **回傳碼與判不了**:已讀,無 finding。
  - `undecidable` 的出處成立:file: `scripts/lumos:33779` 目前記的是 `skipped`。
  - prepare 的呼叫端 file: `scripts/lumos:34755-34758` 對任何非 `error` 的原因都印出來並回 0,所以「prepare 當 skipped 處理」成立。
- **輸出**:見 F7、F10。
- **照留表態**:見 F1。
- **掛鉤與 CI**:見 F10。
- **要一起改的說法**:見 F3、F4。
- **對消費專案的影響**:見 F5 的相容性部分,以及 F3 對手冊 06 的修補。
- **驗收條款 S1-S21**:已讀,無獨立 finding。條款所指的行為問題已併入 F1、F2。
- **回退、審計修正紀錄**:已讀,無 finding。

---

## F1 照留表態拿 `_DRIFT_BOUND_KINDS` 當先例,照字面實作會讓第二層的表態永遠失效

- spec 段落:〈設計/照留表態〉第二個 bullet,以及 PRIOR-ART 的「`_DRIFT_BOUND_KINDS`、`_drift_split_acked`」。
- 撞牆場景:
  - 實作者照字面把 `reread` 加進 `_DRIFT_BOUND_KINDS`。
  - `lumos drift ack --kind reread` 會走 file: `scripts/lumos:37500` 的 `if kind in _DRIFT_BOUND_KINDS`,去呼叫 `_drift_current_finding`(file: `scripts/lumos:37548`)。
  - 那支只認 c2/c3/c6 狀態發現,所以回「第 N 行現在不是 reread」,rc 2。
  - 就算改成繞過它,`_drift_ack_buckets`(file: `scripts/lumos:37283-37285`)只收帶 `related` 且 `seq` 合法的 bound 表態。spec 記的是 `verdicts`,沒有 `related`,表態會被靜默丟掉。
  - 結果是第二層擋下後,「drift ack」這條逃生路走不通,只剩改句、`LUMOS_SKIP_REREAD_CHECK` 或改 gate。
  - 正確的先例是 m1:file: `scripts/lumos:37245` 寫著「m1 不放進 _DRIFT_BOUND_KINDS」,另走 `_drift_m1_split_acked`(file: `scripts/lumos:37306`)。
- spec 還有兩處沒交代:
  - `--kind` 的 choices 來自 `_DRIFT_KINDS`(file: `scripts/lumos:50311`)。spec 只寫「`_DRIFT_KIND_NAMES` 加名字」,沒寫 `_DRIFT_KINDS` 也要加。
  - `_DRIFT_SCAN_KINDS`(file: `scripts/lumos:35025`)只排除 m1,不改的話 scan 會多一個 reread 計數。spec 有提到要排除,但沒說改這個常數。

引句:「reread 加進 `_DRIFT_BOUND_KINDS` 那一類的比對:第二層只認 `verdicts` 含點出那一列的紀錄指紋的表態」

severity: major
blocking: 是——被擋的人拿到的逃生指令實作後會失敗,而 spec 的措辭會把實作者引向這個結果。

## F2 第一層「provenance_ok 為真」只改了 check,prepare 與現有的已提交判斷仍只比檔名,會出現死路

- spec 段落:〈重讀:候選與兩層/第一層〉、S6、〈回傳碼〉裡「prepare 把 `undecidable` 當 `skipped` 處理(行為不變)」。
- 撞牆場景:
  - `reread-record` 遇到報告開頭四行對不上時照收,但標 `provenance_ok: false`(file: `scripts/lumos:34878-34881`)。
  - 現有的 `_note_reread_committed`(file: `scripts/lumos:34697-34709`)只 `ls-tree --name-only` 比檔名,不讀內容。prepare 用同一支(file: `scripts/lumos:34772-34780`)。
  - 新規則下,check 把這篇當「沒對照」並擋下,訊息叫人跑 prepare。
  - prepare 照舊判「已對照」,印「已對照 N 篇……略過」,不產項目檔。
  - 人只有看到 `--all` 才走得出去。spec 沒要求擋下訊息講 `--all`,也沒要求 prepare 改用同一個判斷。
- 另一個缺口:第一層現在要讀「同指紋檔」的內容才知道 `provenance_ok`,但 spec 的讀檔上限與錯誤處理只在第二層那一段寫。

引句:「當候選只有 provenance_ok 為假的判定紀錄時,reread-check 應把它當成沒對照。」

severity: major
blocking: 是——擋下訊息指向的 prepare 步驟,對這類候選產不出檔,要實作者自己想到 `--all` 才解得開。

## F3 〈要一起改的說法〉漏掉會直接誤導被擋下者與消費專案的出處

- spec 段落:〈要一起改的說法〉三個 bullet。
- 撞牆場景與出處:
  - **擋下訊息裡的「改 gate 沒用」會變成假話。**
    - file: `scripts/hooks/pre-push:516` 的逃生 echo 寫「改 gate 沒用」。
    - file: `scripts/lumos:39666-39667` 寫「改 drift_check.gate 不影響這一項」。
    - file: `.github/workflows/ci.yml` drift 那步的 `::error::` 也有同一句。
    - 開關改成沒寫就照 gate 之後,這句對「沒寫 old_sentence」的專案是錯的。手冊 08 第 7 行也寫「改 gate 沒用」。
    - spec 只列「說明、help、註解」,沒列這幾條執行時印出的訊息。
  - **手冊 06 的消費專案 CI 段落會害消費專案 CI 變紅。**
    - file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:96` 寫「它在任何情況都回 0,★不需要 continue-on-error 或 || true★」。
    - 照這段加了步驟的消費專案,轉擋後遇到第二層與判不了會變紅,而手冊還叫人別加保險。
    - 同檔第 73 行的「忽略照推也可以」、第 4 步的「這一版不用表態」也都會變假。
    - spec 只點名「只提醒/恆回 0/沒寫是 warn」這幾個字樣,這幾句不在其中。
  - **手冊沒有「合併主線後本機要重判」這段。**
    - spec 只要求「訊息要講這點」(〈實務隱患〉)。
    - 手冊 06 的步驟與 08 的說明沒有任何一條要求補這段。
    - 三個月後的人看手冊不知道為什麼剛合進主線就被要求重派判定者。
  - **筆記與計劃裡的陳述也漏了。**
    - `Projects/守檔筆記對照改動_計劃.md:86` 與 `:145` 的「只列目錄、不讀內容」。程式裡 file: `scripts/lumos:34698` 的 docstring 也一樣。第二層與 S6 之後這兩處都不成立。
    - 同計劃 `:31` 的 RETIRE-IF、`:32` 的 REVISIT 2026-10-15(「再開要不要擋的另案」)、`:33` 的 REVISIT 2026-11-26、`:38` 的「不做:擋推送(另案)」、`:94`、`:146` 的「恆回 0」。
    - 10-15 的 REVISIT 六天後就會到期。
    - `Projects/CI加速_計劃.md:70` 的 [S1] 綁 `t_ci_yml_matrix_and_gates_shape`,寫著 `run:` 與 `if:` 跟拆分前逐字相同,CI 步驟一改就失真。同檔 `:33` 與 `:48` 也提到。
    - `Projects/舊句偵測實驗_計劃.md:57-59` 的 REVISIT 2026-10-26 與「達標才改擋」門檻。
    - `Projects/舊句檢查_計劃.md:38` 的 REVISIT 2026-12-14,以及 `:43`、`:231`、`:211` 的相容性說法。
    - spec 對舊句檢查計劃只列「RETIRE-IF 與 2026-10-14 那行 REVISIT」。

引句:「[[Projects/舊句檢查_計劃]] 的 RETIRE-IF 與 2026-10-14 那行 REVISIT」

severity: major
blocking: 是——使用者明確要求核對這份清單,上述幾處直接落在被擋下者要照做的訊息與手冊上。

## F4 README 圖與其產生器沒列入同步清單

- spec 段落:〈要一起改的說法〉「README 與英文版的推送前段落」。
- 撞牆場景:
  - file: `assets/drift-guard-zh.svg` 的重讀那列標著「只提醒」,文字是「程式和管它的筆記一起改:請 AI 重讀整篇舊句」。
  - 同圖另有「綁的測試名稱找不到(專案可設成擋)」和「除了兩項一定擋下的檢查、其餘可由專案改成提醒」。
  - `README.md:100` 與 `README.en.md:100` 的 alt 文字也寫提醒。
  - 圖由 `assets/readme-diagrams/generate.py` 產生,圖譜裡的家是 `Systems/README圖產生器.md:40`。
  - 直接改 SVG 會在提交時被「常一起改」的提醒抓到。lands_in 也沒有這篇。

引句:「README 與英文版的推送前段落」

severity: minor
blocking: 否——只是說明圖過期,不影響推送。

## F5 開關的「總開關 off」句有兩種讀法,相容性說明也少了一項

- spec 段落:〈設計/開關〉名稱消失檢查,以及〈對消費專案的影響〉。
- 撞牆場景:
  - 「總開關 off 時 m1 照 retire 的先例也不跑」可以讀成兩種意思:
    - 讀法 A:只有 `old_sentence` 沒寫時,m1 才跟著 gate 關掉。
    - 讀法 B:gate=off 就一律不跑 m1。
  - retire 的先例(file: `scripts/lumos:38608`)是 gate=off 就強制關,連明寫 `retire: warn` 也關。
  - 但現有 `t_drift_m1_gate_off_wording`(file: `scripts/test_lumos.py:69111`)和 `Projects/舊句檢查_計劃.md:182` [S3]、`:194` [S14] 要求「gate=off 且明寫 old_sentence=warn」時 m1 照跑。
  - 實作者讀成 B 就會踩到這兩處。⚠ 我只能指出歧義,不能判定作者的原意。
- 相容性說明也少一項:
  - 〈對消費專案的影響〉只說「不會被新擋」。
  - 實際上 gate=off 且沒寫 old_sentence 的專案,原本會跑 m1(warn 只印),現在整個關掉。
  - CHANGELOG v1.3 該寫這一點。

引句:「總開關 off 時 m1 照 retire 的先例也不跑」

severity: minor
blocking: 否——條款寫明了就能避開。

## F6 第二層讀「所有判定紀錄」的範圍與上限沒定義,卡死時沒有逃出去的線索

- spec 段落:〈重讀:候選與兩層/第二層〉與其最後一個 bullet。
- 撞牆場景:
  - 現有的讀法會用檔名正規式篩掉 `.tmp-wlf` 殘檔(file: `scripts/lumos:34324`、`34705`)。
  - spec 寫「下所有判定紀錄」,又規定「讀不成 JSON→判不了→擋」。
  - 目錄裡殘留一個非 JSON 檔,全專案所有碰到候選的推送就都被擋。訊息只會說「修好或刪掉那份紀錄」。
  - `_nodehome_cat_blobs_capped`(file: `scripts/lumos:29495-29520`)對超過上限的檔回 `None`。
  - 紀錄永不清理,目錄總量碰到 8 MB 上限後,後面的檔全回 `None`,全體進「判不了」。
  - 單檔超過 256 KB 時,刪掉重判又會產生同樣大的新紀錄。
  - 這兩條 RETIRE-IF 都量不到。
- 這個風險短期不會發生:現有 5 份紀錄約 20 KB。

引句:「判定紀錄檔用 `_nodehome_cat_blobs_capped` 讀,單檔上限 256 KB、全部上限 8 MB」

severity: minor
blocking: 否——短期不會觸發,但要在條款裡補名稱篩選與清理辦法。

## F7 擋下後用「改掉那句」逃生,會讓已過的代碼審留痕失效,spec 沒講

- spec 段落:〈輸出〉第二個 bullet。
- 撞牆場景:
  - 掛鉤裡 code-loop check 在 file: `scripts/hooks/pre-push:458`,reread-check 在 `:541`,順序上 reread 在後。
  - 手冊 06 寫「代碼審留痕之前(改筆記會讓留痕失效)」。
  - 一次 tier:high 的推送先過了代碼審留痕,才被第二層擋下。照訊息「改掉那句」,改的是筆記,留痕失效,得重跑代碼審。
  - `drift ack` 寫的是簿記檔(file: `scripts/lumos:26898` 的 `_BOOKKEEPING_FILES` 含 `governance/drift-acks.jsonl`),不會讓留痕失效。
  - 訊息該提醒「已過代碼審的推送優先用 ack」。

引句:「印逃生:第一層 → prepare 指令(派判定者、record、提交);第二層 → 改掉那句」

severity: minor
blocking: 否——有省事的 ack 路,只是訊息沒講。

## F8 動機段的帳目數字有範圍問題

- spec 段落:〈原問題與範圍〉第二個 bullet。
- 我重數的結果:
  - `docs/.governance-log.jsonl` 裡 note-reread 是 reminded 18、none 12、recorded 5,drift-check old-sentence 是 passed 35 且候選數全為 0。數字本身對得上。
  - 範圍有問題:
    - 這些事件的時間止於 2026-10-04。治理帳例行紀錄分流把 reminded/covered/none 與 drift-check passed 改寫到被忽略的本機帳(file: `scripts/lumos:1363`、`1357-1358`)。
    - spec 標「2026-10-09 數」,實際是 09-30 到 10-04 的版控帳。
    - 守檔計劃 `:32` 也提醒要兩本帳一起看。
  - 單位有問題:
    - 「提醒之後真的去跑判定並記錄的不到三成」拿 reminded(每次推送一筆)去比 recorded(每篇筆記一筆)。
    - recorded 的 5 筆中有 4 筆在同一分鐘,是同一批。
    - 方向上仍然成立,但「不到三成」不是乾淨的比例。
- 這是動機證據,不影響設計。

引句:「回頭重讀 reminded 18 次、recorded 5 次、none 12 次」

severity: minor
blocking: 否

## F9 補進來的實務隱患宣稱與現有紀錄實測不符

- spec 段落:〈實務隱患〉第二個 bullet。
- 查證:
  - 我把 5 份紀錄(共 6 列)逐列拿現行筆記對。
  - 引句仍留在筆記裡的只有兩列:`Systems/存量漂移守衛.md` 的一行 `WHY:` 和 `Systems/筆記內容閘.md` 的一行「白話:」。
  - 前者不含 `[test:`,後者是正文一般行,依 spec 的定義都不算規則類行。
  - 規則類行實際上是 0 行,所以「上線那次推送就要處理一次」不會發生。
- 後果:
  - 第二層上線時沒有任何可用的實測樣本。
  - RETIRE-IF 第一條「抽樣人工判誤報超過一半」可能很久抽不到樣。
  - spec 對 m1 承認誤報率沒有實測,對第二層沒有同等的承認。

引句:「上線前已提交的 5 份紀錄裡點出的規則類行,上線那次推送就要處理一次」

severity: minor
blocking: 否

## F10 CI 擋下訊息沒規定內容,逃生段只適用本機

- spec 段落:〈輸出〉與〈掛鉤與 CI〉。
- 撞牆場景:
  - 〈輸出〉說擋下時另印 `LUMOS_SKIP_REREAD_CHECK=1 git push`,CI 也跑同一支工具,會印出同一句。
  - 在 CI 上這句沒有用:環境變數要設在推送端,而且 CI 擋下時已經在主線。
  - CI 的 `::error::` 內容 spec 沒寫。drift 那步的先例(file: `.github/workflows/ci.yml` drift check 步驟)有寫出怎麼修。
  - 反例:判不了(逾時、讀不了)在 CI 擋下,唯一出路是改設定。
  - 另外,掛鉤不再丟 stderr 之後(spec 說要這樣),舊版工具不認得子指令時 argparse 的雜訊會印出來。現有註解 file: `scripts/hooks/pre-push:535` 就是為了避開這個雜訊才丟掉 stderr。
  - 擋下事件沒說要不要帶 `hard=True`。其他閘的 blocked 都帶(例如 file: `scripts/lumos:33233`)。

引句:「回 1 時印 `::error::` 說明後失敗、其他非零照原碼失敗」

severity: minor
blocking: 否

## F11 標 superseded 的 RULE 與被改寫的綁測條款,少了能讓 doctor 與測試保持綠的細節

- spec 段落:〈設計/開關〉最後一句與〈要一起改的說法〉第一個 bullet。
- 查證:
  - 要作廢的 RULE 在 file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:82`。
  - 專案規則(CLAUDE.md 寫作表)要求 `[status:superseded]` 另必有 `[被取代:]`。spec 沒提。
  - 新 RULE 的 `[retire:]` 只收機器式。spec 沒給可用的寫法。
  - 舊 RULE 的 `[retire:]` 是散文,不是機器式。
  - 守檔計劃 S7、S9、S13 綁的測試名是 `t_note_audit_reread_check_never_blocks`、`..._check_wired`、`..._mode_and_isolation`(file: `Projects/守檔筆記對照改動_計劃.md:120`、`122`、`126`)。
  - 改寫條款後測試改斷言但名字不改,「never_blocks」就名實不符。
  - 重命名則會讓條款裡的 `[test:]` 綁定懸空。
  - 另外 S9 要求 hook 與 CI「都不應出現連續字串 `note-audit check`」(`:122`),改寫條款時別丟掉這個限制。

引句:「落地時把它標 `[status:superseded]` 並寫新 RULE」

severity: minor
blocking: 否

---

## lands_in 三篇該寫什麼

- **`Systems/存量漂移守衛`**:
  - m1 預設改照 gate,舊 RULE 作廢並寫新 RULE。
  - `drift ack --kind reread`:表態綁判定紀錄指紋,不屬於 bound 也不屬於 expiring 那類(F1)。
  - 掛鉤與 CI 呼叫 reread-check 的那段(`:125`),把「只提醒、恆放行」改掉。
- **`Systems/筆記內容審`**:
  - reread 一節(兩層、`provenance_ok` 判法、讀紀錄內容取代「只列目錄」)。
  - 複雜度放行那節(`:98-101`):`_note_reread_check` 拆三段、`_note_audit_resolve` 的 `undecidable`、REVISIT 2026-11-01 如何結案。
- **`Systems/bound-tests-gate`**:
  - `:107-109` 那段改寫。
  - `pp_stop_if_signaled` 的行數與新的處理方式。
  - CI 步驟指紋與步驟名稱。
- 另外 F4 若要改 SVG,lands_in 還要加 `Systems/README圖產生器`。

## 實務隱患鏡頭

- **金流**:無。只動本機與 CI 的檢查回傳碼,不碰付款或計費。
- **不可逆**:無。擋下可用 warn、單次略過或 revert 恢復;`drift-acks.jsonl` 是追加檔,舊版工具讀到 `reread` 種類會略過(`_drift_load_acks`,file: `scripts/lumos:37232`)。
- **對外送出**:spec 已承認。補一點:Codex 編排時,筆記全文與 diff 要送外部服務,第一層讓這件事成為推送必經步驟,要在 CHANGELOG 特別寫。
- **守衛面**:F1(逃生失效)、F2(死路)、F7(留痕失效)。
- **併發**:無新問題。`drift ack` 寫表態檔照現有流程取庫鎖(file: `scripts/lumos:37524`)。
- **效能與資料量**:見 F6。

最嚴重的是 F1(照 spec 字面實作,第二層的 `drift ack` 逃生路徑走不通),其次是 F2(第一層對 `provenance_ok` 為假的候選產生死路)和 F3(擋下訊息與手冊的「改 gate 沒用」「不需要 || true」等漏改);blocking 共 3 條(F1、F2、F3)。
