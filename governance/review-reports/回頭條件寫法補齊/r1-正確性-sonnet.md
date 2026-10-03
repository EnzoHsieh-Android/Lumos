severity: major

審查範圍:/tmp/回頭條件寫法補齊-r1.md 全文,對照 rw 工作樹(HEAD 60a39f02)的 `scripts/lumos`。實際查證過的既有東西:`_revisit_split`、`_revisit_lines`、`_probe_lines`、`_issue_close_revisits`、`_ns_revisit_violations`、`_ns_append_subtract`、`_notelines_regions`、`_excluded_line`、doctor E5(含 `_SOFT_CAP`)、`_drift_fix_shape_err`、CI 的 note-shape 步驟。spec 引用的既有名稱與檔案全數存在(含 `t_graph_discipline_negation_revisit`、`Systems/存量漂移守衛`、`Systems/筆記內容閘`、`Projects/舊行尾追加不算新寫_計劃` 等);標明要新寫的 `_revisit_misplaced`、`_revisit_closed`、六支新測試不算未定義。

---

**C1 結案日期「不可晚於提交當天」在 CI 用 UTC 日期,台灣時區每天凌晨 8 小時會被誤擋,而 spec 建議的寫法正是觸發條件**
severity: major
blocking: 是 — 合法寫法(結案日寫當天)在固定時段必然讓主線 CI 變紅,且 CI 這一步沒有本機那種單次跳過可用。
引句:「時區差一天可能誤擋或誤放,寫法是結案日寫當天,影響極小」

1. spec 位置:〈實務隱患〉跨環境、〈做法〉2.3(日期在提交當天之後 → 報「結案標記寫錯」)、1.2 末句(推送前與 CI 的 `note-shape --diff` 走同一支)。
2. 問題:跨環境那段只討論 doctor 的本機日期,但第一層規則會在三個地方各算一次「今天」:本機提交、本機推送前、GitHub Actions 的 CI。CI 沒設時區,跑 UTC。作者在 UTC+8 的當地時間 00:00 到 08:00 之間寫 `[closed:當地今天日期 理由]`,本機 `date.today()` 認為合法、CI 的 UTC 日期還停在前一天,判成「日期在提交當天之後」。
3. 具體例子:台灣時間 2026-10-04 07:00 提交 `REVISIT:2026-10-01 x [closed:2026-10-04 已改用新閘道]`。本機提交、推送前閘都過。推上去後 CI 在 UTC 2026-10-03 23:05 執行 `python scripts/lumos note-shape --diff "$BEFORE..$SHA"`,`2026-10-04` 大於 UTC 今天 → 報「結案標記寫錯」→ CI 紅。出口只剩改日期後重推(重寫歷史)或把專案開關設 warn;CI 那步沒有 `LUMOS_SKIP_NOTE_SHAPE` 的後門。「影響極小」的前提(只影響 doctor 提醒一天)對第一層不成立。
4. 查證:file: `scripts/lumos:27458`(`_notelines_new` 同一支被本機與 CI 共用);`.github/workflows/ci.yml:127-144`(note-shape 步驟、無 TZ 設定);`scripts/lumos` 全檔 `date.today()` 皆取執行環境本機日期。

---

**C2 「只是在講這個字不算」做不到:引號裡的範例句沒有反引號,照字面會被當成死條件,doctor 的處理建議還會誤導作者把範例搬成真的回頭條件**
severity: minor
blocking: 否 — 只多出誤報與一個誤導的建議文字,有行內程式碼可逃,不會讓功能做出不可逆的錯。
引句:「只是在講這個字(`REVISIT 行`、`寫成 REVISIT:`)不算」

1. spec 位置:〈做法〉1.1(判定)、〈驗收條款〉S3(三種不報的形狀:`寫成 REVISIT 行`、行內程式碼、圍欄)、1.3(E5 的提示「永遠不會到期——搬成獨立一行」)。
2. 問題:判定只看「`REVISIT:` 後面緊接日期或 `[when-`」,分不出「引用一個範例句」和「真的在許願」。S3 只涵蓋三種形狀,漏了最常見的第四種:用「」或引號框起來、沒包反引號的範例。
3. 具體例子:`docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md` 第 104 行寫著「REVISIT:2027-01-01 現在沒有權限檢查,之後補」這種夾帶現況的句子(是在舉例說明第二層怎麼判),沒有反引號。照字面實作:doctor E5 把它算進「N 行句中」並說「永遠不會到期——搬成獨立一行」;作者照做就憑空多出一條 2027-01-01 的真回頭條件。這類行在 spec 自己量到的 68 行裡不是少數(我用同口徑腳本重跑也是 68 行,第 104 行在內),RETIRE-IF 的量測也會因此被稀釋。第一層的訊息有寫「只是在提這個寫法就用行內程式碼包起來」,E5 的訊息沒有這句。
4. 查證:`scripts/lumos:31700`(`_revisit_split` 只看行首);唯讀掃描 `grep -rn "REVISIT:" docs/lumos-toolchain-knowledge` 後剝反引號、排除行首 REVISIT,得 68 行,第 104 行確實在內。

---

**C3 「開頭欄位其他欄的 REVISIT 永遠不會到期」對行首的 REVISIT 不成立,而 S2 與 1.1 對這個形狀互相矛盾**
severity: minor
blocking: 否 — 影響一個驗收案例的寫法與 E5 的文字準確度,不會做出危險動作。
引句:「另有 N 行 REVISIT 寫在句中、表格或開頭欄位其他欄,永遠不會到期——搬成獨立一行」

1. spec 位置:〈做法〉1.1(以 `_revisit_split` 判「不是 REVISIT 行」為前提)、1.2(三個位置含開頭欄位其他欄)、1.3、S2(列出「開頭欄位其他欄裡的 `REVISIT:2026-10-05`」應報)。
2. 問題:`_revisit_split` 不分區塊。開頭欄位裡縮排的 `  - REVISIT:2026-10-05 某事`(例如放在 `tags:`、`related:` 或 decisions 的某一欄下)去掉列表記號後以 `REVISIT:` 開頭 → 回 `date`,依 1.1「判這行不是 REVISIT 行」這個前提不成立,所以不會報。偏偏 doctor E5 是對整份文字(含開頭欄位)跑 `_revisit_lines`,這種行 E5 現在就會當真、到期就唸。所以兩件事同時錯:S2 的案例若寫成行首形狀會紅;E5 的提示說「永遠不會到期」對這種行是假的。真的死掉的只有「欄名在前」的寫法(例如 `why: 已知 REVISIT:2026-10-05 …`)。
3. 具體例子:筆記開頭欄位 `decisions:` 下某欄值換行後縮排寫 `REVISIT:2026-10-05 x` → `_revisit_split` 回 `date` → 第一層不報;E5 在 2026-10-05 照唸。
4. 查證:`scripts/lumos:2303`(E5 用 `_revisit_lines(_txt5)` 整份文字)、`scripts/lumos:31721`(`_revisit_lines` 走 `_search_visible_lines`,不分區塊)、`scripts/lumos:27214`(`_notelines_regions` 才分區塊,但只有 `_probe_lines` 與第一層用它)。

---

**C4 E5 「列前 5 個位置」與 doctor 軟提醒的 3 條上限衝突,位置擺哪裡 spec 沒指定**
severity: minor
blocking: 否 — 只會讓清單被截或擠不出來,不影響擋與否。
引句:「並列前 5 個位置(`節點:行號`,過 `_esc_clean`)」

1. spec 位置:〈做法〉1.3、S5。
2. 問題:`warn_soft` 預設每段只顯示 3 條(`_SOFT_CAP = 3`),其餘收成「另 N 條」;`--verbose` 或 `--ci` 才全列。E5 原碼明寫過教訓:壞損數放進 head 不放進 lines,否則被 cap 吞掉(H-2)。spec 說「在開頭行加一句」又說「並列前 5 個位置」,沒講位置進 head 還是 lines。
3. 具體例子:若把 5 個位置塞進 lines:有到期項目時它們排在到期項目後面,預設只看得到前 3 條,S5「並列前 5 個位置」在預設輸出下不成立;沒有到期時也只顯示 3 個加「另 2 條」。若全塞進 head,head 會變成一行很長的字。
4. 查證:`scripts/lumos:1379`(`_SOFT_CAP = 3`)、`scripts/lumos:1383-1391`(`warn_soft` 截斷)、`scripts/lumos:2326-2331`(壞損數進 head 的既有做法與註解)。

---

**C5 `[closed:]` 的讀取端(E5、`_probe_lines`、Issue 結案列出)對「寫錯的結案標記」怎麼處理沒定義,文法也沒寫成可實作的形狀**
severity: minor
blocking: 否 — 新寫的錯誤標記在第一層就擋,漏出來要靠跳過或繞過,屬邊緣情況,但規則缺口會讓實作者各猜各的。
引句:「這幾處共用一支 `_revisit_closed(probe)` → (結案標記的原文, 錯誤說明清單)」

1. spec 位置:〈做法〉2.1(寫法)、2.2(寫了之後)、2.3(第一層驗寫法)。
2. 問題:
   - `_revisit_closed` 回傳「原文」與「錯誤清單」,但 2.2 的三個消費端只說「已結案的不列/不唸/不抽」,沒說錯誤清單非空(日期在未來、理由不足 4 實字、一行兩個)的舊行算不算結案。第一層只查「新寫的」,已在主線上的行、用 `LUMOS_SKIP_NOTE_SHAPE` 或 `--no-verify` 帶進來的行,讀取端若只看到有標記就靜音,等於 `[closed:2099-01-01 好]` 能永遠關掉提醒。
   - 文法只說「`[closed:YYYY-MM-DD 理由]`」,沒定義理由能不能含 `]`。2.1 自己鼓勵「附提交或測試更好」,實務上會寫 `[[Issues/某篇]]`;`[^\]]*` 這類切法會在第一個 `]` 截斷,剩下的 `]] 處理]` 變成行尾雜訊,「一行只能有一個」的計數也取決於怎麼切。
   - 位置:2.1 說日期式「放在日期之後」又說「行內任一處都行」。日期式的日期是取到第一個空白為止,`REVISIT:2026-10-05[closed:…]`(緊貼無空白)會讓 `fromisoformat` 失敗、整行變 `bad`;條件式放在 `[when-]`/`[by:]` 之前會讓 `_probe_parse` 在遇到 `[closed:` 就停,判成「沒帶期限」。「任一處」與「之後」要擇一寫明,測試 S8 才有可驗的邊界。
3. 具體例子:舊行 `REVISIT:2026-10-01 x [closed:2026-10-03 好]`(理由 1 個實字,繞過第一層進來)→ 讀取端若以「標記存在」靜音則 E5 不唸;若以「標記合格」靜音則 E5 照唸。兩種都合理,spec 沒選,S6 又只測合格的。
4. 查證:`scripts/lumos:31700-31718`(日期取到第一個空白)、`scripts/lumos:31805-31840`(`_probe_parse` 遇到不是 `when-`/`by` 的標記就停)、`scripts/lumos:6396`(`_excluded_line` 的 4 實字算法與 spec 描述一致,此處無問題)。

---

**C6 擋「新寫」的整行規則會連帶擋住機械改寫舊行的工具(改名時的連結改寫),spec 的相容段只列了「補更正」一種**
severity: minor
blocking: 否 — 有單次跳過可用,且影響面是存量那 77 行,但會在不相干的改名提交上炸出來。
引句:「舊筆記裡的句中 REVISIT 不被擋(只擋新寫的),只在 doctor 列」

1. spec 位置:〈實務隱患〉相容、〈做法〉1.2(整行層級、不扣)。
2. 問題:`_ns_append_subtract` 只扣「程式行號引用」「釘版本不合法」兩條片段式規則,其他整行規則一律不扣,所以新規則碰到存量行就是整行報。人工補更正時「順手搬出來」合理,但 `scripts/graph-rename.sh`(notesmd-cli move)改名時會自動改寫全圖譜內含舊連結的行,若那一行同時有句中 REVISIT,改名提交就被第一層擋下,作者沒辦法也不該去搬別篇的回頭條件。
3. 具體例子:某句同時含 `[[Systems/舊名]]` 與 `…承認 X。REVISIT:2026-11-01 …`;`graph-rename.sh "Systems/舊名" "Systems/新名"` 改寫該行 → 提交時該行算新寫 → 報「回頭條件寫在句中」。出口只有 `LUMOS_SKIP_NOTE_SHAPE=1`,而每次跳過會被 RETIRE-IF ① 算進「誤擋」分子。
4. 查證:`scripts/lumos:27693`(`_NS_FRAG_KEY_RULES = ("程式行號引用", "釘版本不合法")`)、`scripts/lumos:27694-27720`(其他規則不扣)、`scripts/graph-rename.sh:1-20`(連結全 vault 改寫)。

---

**C7 同一種「寫錯的結案寫法」,第一層擋下時的改法沒提 `[closed:]`,只有 doctor 提**
severity: minor
blocking: 否 — 只是改法文字不一致,功能不受影響。
引句:「依第 1 點算句中(行首是 `~~`)」

1. spec 位置:〈做法〉1.4 與 1.2。
2. 問題:`~~REVISIT:…~~` 是作者自創的結案寫法。1.4 只規定 doctor 列出存量時多一句「要結案就改成 `[closed:…]`」;1.2 的第一層改法文字沒提。新寫 `~~REVISIT:2026-10-05 …~~` 的人在提交時只看到「搬成獨立一行」,照做會把一條本意是結案的待辦變成活的回頭條件。
3. 具體例子:作者想劃掉一條已完成的待辦,寫 `~~REVISIT:2026-10-07 …~~`,第一層擋下並建議「行首寫 `REVISIT:`」→ 照做後到期又被唸。
4. 查證:`docs/lumos-toolchain-knowledge/Projects/進度從提交推導_計劃.md:292`(存量裡就有這種結案用法);`scripts/lumos:27915-27939`(現行第一層訊息內容)。

---

**C8 文件同步漏掉兩個把舊寫法教給作者的來源**
severity: minor
blocking: 否 — 技能手冊那一份補了就能查到,但注入消費專案的規矩區塊不會提到新規則。
引句:「技能手冊 `skills/lumos-project-notes/commands/03-寫回圖譜.md` 寫回頭條件那格補兩句」

1. spec 位置:〈做法〉3(說明與同步)。
2. 問題:〈依據〉自己說存量的源頭是 `scripts/templates/graph-discipline.md` 的鐵則 4 這類指引;該檔(會被安裝進消費專案的 CLAUDE.md 區塊)與 `skills/lumos-project-notes/SKILL.md` 第 73 行都寫了「帶日期的寫 `REVISIT:YYYY-MM-DD …`(doctor 到期會唸…)」,spec 只改 `commands/03`。消費專案讀到的規矩區塊不會提「句中會被擋」與 `[closed:]`;第 3 節也沒說是否有意不改這兩處。
3. 具體例子:消費專案的 agent 只讀注入的 CLAUDE.md 區塊,不一定打開 `commands/03` → 第一次被擋才知道規則。
4. 查證:`scripts/templates/graph-discipline.md:59`、`skills/lumos-project-notes/SKILL.md:73`、`skills/lumos-project-notes/commands/03-寫回圖譜.md:49-52`。

---

**C9 先例描述與事實不符:ESLint 的 `no-warning-comments` 有「任何位置」選項**
severity: minor
blocking: 否 — 只影響〈PRIOR-ART〉論述的準確度,結論(不解析句中)不依賴它。
引句:「ESLint 的 no-warning-comments 只認固定位置的關鍵字」

1. spec 位置:開頭欄位 `PRIOR-ART:` 那行。
2. 問題:該規則的 `location` 選項預設 `start`,但可設成 `anywhere` 去找句中的關鍵字,正好是 spec 說「不做」的那條路;把它當成「只認固定位置」的同類先例,把世界上有人這樣做過的事實藏了。⚠ 我是憑對該規則設定的認識判斷,沒有在這個環境開文件驗證。
3. 具體例子:作者據此以為業界都不去抓句中的待辦註解,實際上有現成的選項可借。
4. 查證:⚠ 未在審材內查到,待外部文件核對。

---

## 已讀,無 finding 的節

- 〈範圍〉:已讀,無 finding。
- 〈回退〉:已讀,無 finding。
- 〈天花板〉:已讀,無 finding。
- 〈審計修正紀錄〉:已讀,無 finding(空節)。
- 〈驗收條款〉S1、S4–S10 的前提與對應程式現況:已讀,無 finding(S2、S3 見 C2、C3)。

## 平行路徑盤點(spec 沒列、我查過)

讀 REVISIT 的其他地方:`_ns_negation_hits`(`scripts/lumos:28051`,用 `_revisit_split` 跳過 REVISIT 行,加 `[closed:` 不影響)、筆記內容審的條件式跳過(`scripts/lumos:29854`,已結案的條件式行仍會被跳過,符合預期)、`drift fix` 的改寫考卷驗證(`scripts/lumos:35091`,只驗條件式文法,不受影響)、`_drift_fix_shape_err`(`scripts/lumos:33358`,工具自己寫的文字會過新規則;寫的是橫幅與狀態說明,不含句中 REVISIT,無衝突)、`_drift_status_probe_followups` 與 doctor Z 段(皆用 `_probe_lines`,會自然排除已結案的)。這幾處沒有漏改的證據。

## 實務隱患逐類

- 併發:無。理由:E5 與第一層只讀筆記;治理帳走既有寫入器,只多一個 note 欄位。
- 效能:無。理由:第一層只對新增行多一個正則與一次 `_revisit_split`;E5 本來逐行掃,多一個正則;`_revisit_misplaced` 的正則是線性,沒有巢狀量詞。
- 回滾:無。理由:還原提交即回原判法;寫過的 `[closed:]` 留在筆記裡無害。〈實務隱患〉回滾那句「已結案的條件若成立,推送會被擋」過度宣稱:推送判定只列「被這次推送影響」且起點沒有同一條的行,存量的已成立條件在起點本來就成立,不會被擋;不影響結論。
- 誤擋與繞過:有,見 C2(範例句誤報)、C6(機械改寫工具)、C1(CI 時區);繞過面 spec 的天花板已承認。
- 跨環境:有,見 C1。
- 金流、對外送出、不可逆:無。理由:只讀筆記、不呼叫網路、還原提交即回。

最嚴重 severity 是 major;blocking 共 1 條(C1)。
