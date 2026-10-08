severity: major

審查範圍:/tmp/slots/r3.md 全篇。逐節已讀:格子規格、擋、lint 與擋同一張表、過期檢查表、分期、天花板、不做、實務隱患、驗收條款、回退、合約候選、審計修正紀錄。
固定席筆記:hook 沒有附在尾端,所以沒有固定席筆記可逐條判。

**R3I1**
severity: major
blocking: 是——實作者照「補連結不被擋」寫,會跟「核心一句=去掉欄位剩下的」打架,做出誤擋最常見的編輯動作。
1. 輸入:舊行 `DEP:[[A]]`,作者補上一個連結變成 `DEP:[[A]] [[B]]`。
2. 走到〈擋〉的「改到舊行不算新寫」。這一段說只差欄位的才算舊行,又說補連結不會被擋。
3. 壞在哪:`[[B]]` 不是白名單欄位,屬於核心一句。核心一句因此改變,依天花板 7 就是新寫,必有鍵全套適用。
4. 結果:補一條依賴就被迫補 `[來源:]` `[confirmed:]`,或改寫成 SEE。這跟「補連結都不會被擋」直接矛盾。S6 的條款只講欄位,沒有任何地方把連結排除在核心一句之外,實作者得自己猜。
引句:「補 `[confirmed:]` 重新確認舊 RULE、補連結都不會被擋」
佐證 file: `scripts/lumos:25906`(現行 DEP 指路行的判法是整行比對,沒有「核心一句」概念)

**R3I2**
severity: major
blocking: 是——照字面實作,每個 `lumos new system` 產的新節點第一次提交就會被擋。
1. 輸入:`lumos new system` 產的骨架,摘要是空的 `FLOW:` `KEY:` `DEP:` `TEST:`(`scripts/lumos:17347`)。
2. 走到〈格子規格〉的「核心一句空的算缺」,加上 S4(新寫的 FACT/FLOW/DEP 缺 `[來源:]` 要擋)。
3. 例外只寫「骨架留的空前綴(`DEP:`、`SEE:`)照舊不算違規」,沒有 `FLOW:`。
4. 現行 `_ns_check_line` 的 `skip = (not body) or …` 對任何前綴的空行都放行,所以 spec 說的「照舊」不成立。字面實作會收窄成只豁免 DEP 與 SEE,空 `FLOW:` 在開擋後被擋。
5. 實況:工具鏈圖譜裡有 90 條空 `DEP:`、90 條 `FLOW:`,都是骨架殘留。
6. 同時,〈格子規格〉的「核心一句空的算缺」跟 S1(WHY 核心一句是空的要擋)沒有說明空前綴例外適用哪些前綴。
引句:「骨架留的空前綴(`DEP:`、`SEE:` 什麼都沒寫)照舊不算違規」
佐證 file: `scripts/lumos:25905`

**R3I3**
severity: major
blocking: 是——SEE 的判準跟它自己的定義不一致,會讓既有的指路寫法無處可寫。
1. SEE 的定義是「只放連結的 DEP 換個名字」。
2. 現行「只放連結」判準 `_NS_POINTER_ONLY_RE` 允許連結之間夾 `｜ 、 , ; 與 和 及 見 →`(`scripts/lumos:25856`)。工具鏈圖譜實際的 DEP 指路行就是 `[[A]]｜[[B]]｜[[C]]` 這種。
3. SEE 的規則卻寫「連結以外不准有字」。依字面,`｜` 是連結以外的字。
4. 結果:`DEP:[[A]]｜[[B]]` 因為只放連結,被擋並叫人改 SEE;改成 `SEE:[[A]]｜[[B]]` 又因為有分隔字被擋。兩邊都過不了。
5. S4 沒有定義分隔符與別名 `[[A|別名]]`、`[[A#段]]` 怎麼處理。現行 regex 明確排除別名與段落,SEE 要不要照辦也沒寫。
引句:「至少一個 `[[連結]]`,連結以外不准有字」
佐證 file: `scripts/lumos:25856`

**R3I4**
severity: major
blocking: 是——日期規則會在 CI 對台灣時區的合法提交誤報,而且 CI 不能用單次跳過。
1. 輸入:台北時間 2026-10-01 06:00 提交,寫 `[since:2026-10-01]`。
2. 走到〈格子規格〉的日期規則:晚於今天算寫錯。
3. 推送後 GitHub Actions 以 UTC 跑 `note-shape --diff`,此刻 UTC 還是 2026-09-30,規則判定「晚於今天」,CI 紅。
4. 台北 00:00–08:00 的提交都有這個窗口。CI 沒有 `LUMOS_SKIP_NOTE_SHAPE`(spec 自己說 CI 照擋)。
5. spec 沒說「今天」用誰的時區、推送與 CI 是否容忍一天,也沒說套用的是提交日期還是檢查當下。既有 `rule_lifecycle_warnings` 用本機 `date.today()`,但那只是提醒,不擋。
引句:「`[since:]` `[confirmed:]` 晚於今天算寫錯」
佐證 file: `scripts/lumos:3350`(`today = today or _dt.date.today()`,本機日期、只提醒)

**R3I5**
severity: major
blocking: 是——度量式撤除條件在提交時完全沒有驗證,會寫出永遠不觸發的死條件,而這正是 spec 自己說要避免的。
1. 〈撤除條件提交時就驗寫法〉只對 `[retire:when-*]` 跑值文法檢查。
2. 〈撤除條件的機器式〉(D)為度量式訂了四條規則:`<閘>.<種類>` 白名單、比較符號、N 為 1 到 26、暖機。S2 只驗 retire「是不是機器式三類之一」,沒有任何一處在提交時驗度量的這幾條。
3. 結果:`[retire:度量 foo.bar > 3 近99週]` 能過提交,到 doctor 才發現不能判,或根本不報。
4. 白名單「從 `_gate_event_or_warn` 的呼叫點整理」只能靠人工抄:`scripts/lumos:26880` 的 `gate` 是變數,靜態掃不完。spec 沒說誰負責讓白名單不漂移,也沒有對應測試(`t_gov_stats_gate_drift` 只釘閘名,不釘種類)。
引句:「新寫(含改了 `[retire:]` 值)的 RULE 行,`[retire:when-*]` 的值跑既有的值文法檢查」

**R3I6**
severity: major
blocking: 是——spec 要 doctor 去評估條件,翻掉了既有已審定的決定,而且沒有成本說明。
1. 輸入:第 3 步的 doctor 提醒「撤除條件現在已成立」,S13 要求 doctor 對此提醒,表格寫「沿用 `drift scan` 的工作目錄判定」。
2. 既有決定相反:doctor Z 段「不評估條件、不跑 `git grep`/`ls-tree`、只讀筆記;要看哪些成立跑 `lumos drift scan`」(`scripts/lumos:31453`)。Systems/存量漂移守衛的家筆記和 `Projects/存量漂移防線_計劃` 的 S14(`t_doctor_drift_section`)都釘了這條。
3. `drift scan` 是手動指令,預算 60 秒(`_DRIFT_BUDGET_SEC`),symbol/test 條件要建整棵程式檔語料。把它搬進 doctor,每次 doctor 都吃這個成本。
4. 〈實務隱患〉效能段只講「撤除條件只看這次推送改到的路徑」,沒講 doctor 要不要預算、逾時怎麼辦。〈不做〉也沒寫翻案理由。
5. 「兜底」表列在 doctor,「沿用 scan」又可以解讀成只在 scan 輸出。要在 doctor 評估,就要明寫翻掉 S14 並訂預算;要保留 S14,就要改成「兜底在 `drift scan`」。
引句:「工作目錄裡條件現在已成立(兜底:轉變那次判不了或被跳過就再也不會被擋)」
佐證 file: `scripts/lumos:31453`、`docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md`(〈做法〉doctor Z 段「不評估條件」與 S14)

**R3I7**
severity: major
blocking: 是——回退順序會讓第 1 步被還原後,第 0 步的 lint 失去它依賴的表。
1. 第 0 步說「lint 改讀同一張表」,第 1 步又列「必有鍵表」。表到底在哪一步落地,spec 前後兩處都寫了。
2. 回退順序是:第 3 → 2 → 開擋 → 第 1 → 第 0。如果表隨第 1 步加入,第 1 步還原後,第 0 步的 lint 讀不到表。
3. 如果表在第 0 步,第 1 步清單裡的「必有鍵表」是重複列。第 0 步的驗收 S11(`t_slots_single_table`,lint 與擋讀同一張表)需要擋的程式存在,卻跨在第 0 與第 1 步之間。
4. 這是 r2「lint 併進第 0 步」補丁跟原分期的新銜接洞。
引句:「必有鍵表、`--slots` 旗標與格子上線點、舊行判定」

**R3I8**
severity: minor
blocking: 否——單源測試的守衛會變成空轉,但不會讓行為出錯。
1. `t_note_convention_single_source` 用 `| \`WHY:\` |` 這個表格列字串偵測 skill 裡有沒有第二份分類表(`scripts/test_lumos.py:19000`)。
2. spec 的新表第一欄是 `| WHY |`,沒有反引號和冒號,範本若照搬,舊測試永遠偵測不到複本。
3. spec 的 S11 只釘範本與程式的必有鍵表,沒說更新這支單源守衛的偵測字串。
引句:「測試把「紀律範本的必有鍵表」與「程式裡的必有鍵表」釘在一起」
佐證 file: `scripts/test_lumos.py:19000`

**R3I9**
severity: minor
blocking: 否——都是實作時會當場撞到的接點,但 spec 沒列,容易漏改測試或家筆記。
1. 共用抽取器:`_notelines_range_added`/`_notelines_new` 同時服務筆記形狀擋與筆記內容審(`scripts/lumos:26733`),測試以三元組解包(`scripts/test_lumos.py:49850`)。spec 的「逐提交記下掛鉤有哪幾個記號」要擴充回傳,卻只說「不為格子多跑一趟 git」,沒提回傳形狀與筆記內容審。
2. `_note_shape_config` 的註解明講兩值解包有兩個呼叫端、不能擴充(`scripts/lumos:26157`)。spec 的子開關 `note_shape.slots` 沒說要走自己的解析函式,跟否定現況句同樣處理。
3. 單次跳過:現行 `LUMOS_SKIP_NOTE_SHAPE` 檢查放在最前面,一進來就記 `skipped-env` 然後返回(`scripts/lumos:26371`)。spec 要在跳過時先算格子違規,等於重排流程,而且沒說算失敗時跳過是否仍要放行。
4. 上線點記號:掛鉤範本裡的說明註解要避免多出一份 `note-shape --staged --slots` 字串。上線點用 `git log -S` 找第一次出現,註解跟指令必須同一次提交進來。spec 沒要求。
5. 規格閘:第 0 步要改 `_plan_system_links`(`scripts/lumos:6215`)。`Systems/規格閘` 的家筆記把它記為「計劃連到誰只有一支」,是門判定訊號 2 與相依回歸的共用入口。`lands_in` 沒列這篇,改了不會被提醒回寫。
引句:「算「計劃連到哪些節點」的程式改成也讀 SEE」

**R3I10**
severity: minor
blocking: 否——新種類的登記不完整,但 `drift ack` 本身不會壞。
1. 「新種類登記進 `drift ack` 與種類名稱表」只講了兩處。`_DRIFT_KINDS` 同時決定 `drift scan` 的計數列(`scripts/lumos:31432`)和 `_drift_fix_hint` 的預設分支。
2. 新種類走預設分支會印出 `lumos drift fix <節點> <行> --kind retire`,但 `_DRIFT_FIX_KINDS` 沒有它,指令必然失敗。`probe` 在這兩處都有專屬分支(`scripts/lumos:29661`、`29740`),`retire` 也得照做。
3. 「判不了」那張清單用字串還是跟 `listed` 一樣的發現字典,spec 沒說;既有的 `unknown` 是字串、`_drift_print_findings` 需要 `kind` 與 `path`。
引句:「新種類登記進 `drift ack` 與種類名稱表」
佐證 file: `scripts/lumos:28146`、`29661`、`29740`、`31432`

**R3I11**
severity: minor
blocking: 否——不影響新寫的格子,但重建筆記的寫法在新文法下沒有出口。
1. 重建筆記(regen)現行教的是 `FLOW/DEP=指針級快寫`、`KEY=關鍵事實 [src:…]`(`skills/lumos-project-notes/reference.md:1100`)。
2. spec 說 regen 寫的行不豁免、「改成新文法」。但新文法下 FLOW 必須有程式碼答不了的 `[來源:]`,regen 的內容本來就來自程式碼;KEY 不在格子表裡。
3. 指針級的 FLOW/DEP 可以改 SEE,但 regen 的 KEY 行和流程描述改成什麼,spec 沒寫。
引句:「重建筆記(regen)寫的行不豁免:第 0 步把 skill 裡 regen 的寫法一起改成新文法」
佐證 file: `skills/lumos-project-notes/reference.md:1100`

**R3I12**
severity: minor
blocking: 否——度量的時間窗最大值跟治理帳的實際讀取上限對不上,長窗永遠不判。
1. 度量 N 可到 26 週,doctor 只讀治理帳「檔尾,上限照既有 24MB」。
2. 實測 `docs/.governance-log.jsonl` 15.9MB、10 萬行,9 月一個月就 7.5 萬筆。照這個速度,24MB 的尾巴撐不到 8 週。
3. 超過讀取上限後,「歷史不足 N 週不判(暖機)」跟「讀不到那麼遠」無法區分,N 較大的度量式撤除條件會靜默永遠不判。
4. spec 沒限制 N 與讀取上限的關係,也沒說治理帳輪替或截斷時怎麼辦。
引句:「治理帳的歷史短於 N 週、或這條 RULE 的 `[since:]` 不滿 N 週,不判(暖機)」
佐證 file: `scripts/lumos:2053`(24MB 尾巴讀取)

**實務隱患逐類**
- 併發:新增寫入只有治理帳(沿用既有),無新隱患。
- 效能:除 R3I6(doctor 評估條件)與 R3I12(帳尾讀取上限)外,其餘沿用既有一趟抽取。
- 資源:不開長駐程序,無。
- 相容:有隱患,見 R3I2、R3I3、R3I11 的舊寫法與骨架銜接。
- 注入:擋下訊息與判不了清單回填筆記內容,spec 已寫截斷與清控制字元,無新缺口。
- 自我治理:有子開關與單次跳過,缺口是 R3I9 第 3 點(跳過時要先算違規)。
- 金流、對外送出、不可逆:spec 已排除,同意——只讀筆記與程式文字,子開關可降級。

**r2 修補驗收摘要**
- `--slots` 旗標與格子記號:邏輯自洽(提交時看旗標、推送與 doctor 看歷史記號、找不到整段不跑),已對照 `_nodehome_golive`、`_notelines_range_added` 驗過。剩餘缺口是 R3I9 第 1、4 點。
- `[被取代:]` 改名與作廢不吃舊行豁免:已補上,S5 明寫「舊行這次才加上」。無新矛盾。
- 撤除條件判不了另列、預算排後:跟 `_drift_check_c`、`_drift_report_must` 的現行語意相容;剩餘缺口是 R3I10。
- 度量的 `<閘>.<種類>` 文法:文法已定,但提交時不驗,見 R3I5。
- 核心一句=去欄位剩下的:本身可行,但跟「補連結不被擋」衝突,見 R3I1。
- lint 併進第 0 步:跟分期銜接有洞,見 R3I7。

最高嚴重度:major,blocking 7 條
