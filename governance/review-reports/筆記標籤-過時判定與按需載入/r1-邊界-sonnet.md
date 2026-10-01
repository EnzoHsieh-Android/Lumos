severity: major

這份是外部投稿,我當第三方稿審。固定席筆記:派工詞和 hook 都沒有附,所以「固定席逐條判」這一項沒有對象可判。

「已讀,無 finding」的節:frontmatter、依據、PRIOR-ART/RETIRE-IF、現況(四處文件矛盾的宣稱屬實)、設計原則、不做、回退。內部交叉引用(〈欄位 v1〉〈分期〉〈回退〉〈一個事實只寫一處〉〈讓 AI 知道該寫什麼〉〈前綴怎麼寫、怎麼判過時〉、已裁第 2 題)目標都存在。

---

**B1 init 預設寫 block 會讓沒有設定檔的既有專案被改成擋,有設定檔的新專案反而拿不到**
severity: major
blocking: 是——照字面做會破壞「既有專案一律不受影響」的承諾(S1 合約),或讓 S2 在多數情況下不成立。
1. 輸入:既有專案沒有 `.lumos/config.json`,跑 `lumos update`。`update` 會呼叫 `_init_additive_setup`,再呼叫 `_init_config_skeleton`。這個函式的設計意圖是「既有專案也拿得到骨架」,而且只要檔案不存在就整份寫。
2. 把 `note_tags.gate: block` 放進骨架,這個既有專案下次 update 就悄悄變成 block。這和「既有專案一律不受影響」正面衝突。
3. 反方向:新接入的專案若先有 `config.json`,骨架函式直接 return(「既有設定一律不覆寫」),`note_tags` 不會被寫進去,等於 off。S2 的「新接入一個專案」在這條路上不成立。
4. spec 沒有定義怎麼分辨「新接入」和「既有專案」。
引句:「`lumos init` 對新接入的專案寫入 `block`」
佐證:`scripts/lumos:18204`、`scripts/lumos:18396`、`scripts/lumos:18670`

**B2 「只看新增行」判不出「程式變了、筆記沒動」,執行時機整段沒定義**
severity: major
blocking: 是——count、value、enum、lives 要抓的就是這種情況,照字面只看新行就抓不到。
1. 輸入:一行帶 `[count:app/config.py::MODEL_VARS=4]` 的 WHY 已提交。之後有人只改程式,把 MODEL_VARS 改成 5,筆記一個字沒動。
2. note-shape 的機制只評估 `_notelines_new` 回傳的新增行,這次推送沒有新增行,所以不會判。
3. 「欄位只會出現在新行上」只在寫入那一刻成立,之後它就是舊行。
4. 要抓得到,得用存量漂移乙那種「這次改到的程式檔是不是候選」的篩選,或每次推送全掃帶欄位的行。spec 兩條都沒選,也沒說由哪個閘(pre-commit、pre-push、CI)負責。
5. 若選全掃,一個人改程式後,別人所有不相干的推送都會被擋到筆記更新為止,這個後果 spec 沒提。
引句:「欄位判過時只看帶欄位的行,而欄位只會出現在新行上。」
佐證:`scripts/lumos:25618`(`_notelines_new` 只取新增行)、`scripts/lumos:28470`(`_drift_probe_is_candidate` 才是「程式變了」的篩法)

**B3 ①②要「讀名稱的成員數、常數值、列舉成員」,程式裡沒有這個求值器,PRIOR-ART 說「接在既有零件上」不實**
severity: major
blocking: 是——最核心的兩類欄位要新寫求值器,但分期和工作量都當作沿用既有零件。
1. 回頭條件探針只認 file、symbol、test、status 四種條件,其中 symbol 只判「名稱是否定義」。
2. doctor N 是 `re=` 加 `in=` 的全 repo 正則計數,不會讀具名集合,而且是寫死在 cmd_doctor 裡的內嵌程式碼,不是可共用的函式。S4 要求的「同一個重算器」得先抽出來。
3. 全 repo 掃描有 4000 檔和 40MB 的上限。超限時 doctor 只出提醒,spec 沒說 block 模式下超限算擋還是放行。
4. 天花板 5 說非 Python「認不出來就提示改用正則寫法」,同樣沒說認不出來時 block 要不要擋。
引句:「讀那個名稱的成員數或常數值,跟 N 或字面值不同 → 擋」
佐證:`scripts/lumos:2924`、`scripts/lumos:3017`(`_CNT_RE`)、`scripts/lumos:28297`(`_DriftProbeTree.one` 只有定義判定)

**B4 欄位語法沒定義值裡的 `]`、`=`、`::`、空白**
severity: major
blocking: 是——同族的欄位解析都是 `\[key:\s*([^\]]*)\]`,值一遇到 `]` 就截斷;照這個做法 spec 自己舉的欄位寫法就會壞。
1. 輸入:`[count:N re=[A-Z]\w+ in=**/*.cs]`。字元集 `[A-Z]` 的 `]` 把欄位截在 `re=[A-Z`。doctor N 改用 HTML 註解,正是為了避開這個問題。
2. 輸入:`[value:app/c.py::URL=http://x:80/a=b]`。字面值裡有 `:`、`=`,甚至 `::`(例如 `a::b`)。該用哪個 `=` 切、`::` 從最後一個還是第一個切,spec 都沒說。
3. 欄位寫壞(少 `=N`、鍵打錯、全形冒號)是靜默忽略還是擋,沒有驗收條款。回頭條件那邊會列「不認得的條件鍵」。
4. S4 要求行內寫法和 HTML 註解寫法算出同一個數,但行內寫法本身裝不下 doctor N 允許的正則。
引句:「找不到具名集合時用 `[count:N re=… in=…]`」
佐證:`scripts/lumos:3270`(`SINCE_REF_RE` 等同族 `[^\]]*`)、`scripts/lumos:3003`(`rule_field_truncated` 專門唸被 `]` 截斷)、`scripts/lumos:3017`(doctor N 的註解式語法)

**B5 `路徑::名稱` 對 Rust、C++、PHP 的限定名一律切錯,⑥ lives 會永久誤擋**
severity: major
blocking: 是——在 block 模式下這是無法靠修筆記解掉的誤擋,只能把欄位拿掉。
1. 輸入:`[lives:src/net.rs::Client::connect]`,Rust 的限定名;C++ 的 `Foo::bar` 同理。
2. 沿用既有切法 `rsplit("::", 1)`,得到路徑 `src/net.rs::Client`、名稱 `connect`。這個路徑不在樹上,`one()` 回 False。
3. ⑥ 規則「名稱不在那支檔 → 擋」於是每次都擋。
4. 既有程式已知這個坑,只對 when-symbol 印警告「寫成 型別::方法 了?」。spec 的語法選擇和天花板 5 都沒涵蓋。
5. 另外 Kotlin 反引號名稱(含空白)、Ruby 的 `Foo#bar` 也落在同一個語法空洞。
引句:「符號一律寫 `路徑::名稱`(跟既有的 `[when-symbol:路徑::名稱]` 同一個寫法)」
佐證:`scripts/lumos:28244`(`_drift_cond_split`)、`scripts/lumos:28649`(`_drift_probe_path_warn`)、`scripts/lumos:28418`(path 不在 files 回 False)

**B6 欄位在行內程式碼、表格、圍欄、frontmatter 非 summary 區能不能算,整份沒定義**
severity: major
blocking: 是——記載這些欄位的筆記(Systems/筆記標籤、skill 速查表)自己的範例會被當真。
1. 既有條件探針剝掉行內程式碼、表格行、圍欄,以及 frontmatter 的非 summary 欄,命中只算「寫在不評估的地方」。
2. RULE 欄位卻是對原始文字跑 regex,不剝反引號。
3. 這份 spec 的欄位語法大量出現在表格和反引號裡(例如 `[count:路徑::名稱=N]`)。實作者若直接重用 RULE 那套 regex,landing 的 Systems/筆記標籤 一寫文件範例就會被評估成不存在的路徑而擋。
4. 若重用探針那套,spec 自己的表格範例又不算數。
5. 兩條路擇一,spec 要寫明。
引句:「寫法沿用 rtb 原提案的標準寫法。欄位都掛在脈絡行上」
佐證:`scripts/lumos:28062`(`_probe_lines` 的剝除與 dead 分類)、`scripts/lumos:3281`(`parse_rule_fields` 不剝反引號)

**B7 W6「欄位外又出現同數字就擋」會跟 WHY 必填的出處打架,中文數字比對規則也沒定義**
severity: major
blocking: 是——W6 規定「擋」,誤擋沒有合法的改法。
1. 輸入:`WHY:[2026-10-01 ...]要跟 GPU 記憶體對齊 [count:app/c.py::X=10]`。WHY 必須帶出處,出處就是日期、`#dN` 或 sha,這些都含數字。
2. 值 10、1、2026 在日期裡出現;值 3 撞上 `#d3`。W6 要求「把散文那份拿掉」,但出處不能拿掉。
3. 比對粒度(子字串還是整數 token)沒定義。以「整 token」比,`2026-10-01` 的 `10` 仍是獨立 token。
4. 中文數字:`[count:…=1]` 對上「統一」「一致」「唯一」裡的「一」,這些都不是數量。「兩」「十二」對 12 的換算也沒寫。
引句:「在欄位外又出現一次——阿拉伯數字或中文數字都算——就擋」
佐證:`scripts/lumos:3236`(`_CTX_SRC_RE` 出處規則)、`scripts/lumos:3243`(WHY 缺出處的規則)

**B8 S17 假設 impact-hook 會在改筆記時觸發,實際它完全不碰筆記**
severity: major
blocking: 是——「寫的當下(主要管道)」整條教學通路在現有 hook 上不存在,而且 spec 把它當既有機制「多附」一張表。
1. `_decide_one` 只放行 `CODE_EXTS` 副檔名,`.md` 回 None。
2. `EXCLUDE_PATH_CONTAINS` 另外明排 `/docs/`。
3. hook 全檔不讀 `.lumos/config.json`,沒有地方判斷 `note_tags.gate`。
4. 要做就得新增筆記路徑的觸發分支、讀設定、決定框和防注入包裝。
5. 另外,AI 用 `lumos set` / `append` 改檔時不經 Edit 工具,hook 根本不會觸發。
引句:「AI 要改一篇筆記時,既有的改檔前提示 hook(impact-hook,現在已經會附棧別檢核題)多附一張六行的速查表」
佐證:`scripts/hooks/claude/impact-hook.py:31`(`CODE_EXTS`)、`scripts/hooks/claude/impact-hook.py:45`(`/docs/` 排除)、`scripts/hooks/claude/impact-hook.py:147`

**B9 給 agent 的入口指令照字面會直接報錯,`--include-superseded` 又已被佔用**
severity: major
blocking: 是——spec 要放進 skill 的就是這條指令,放進去 agent 一跑就失敗。
1. `search` 的 `term` 是必填位置參數。我實跑 `python3 scripts/lumos search --path Systems`,輸出「擋下:少了必須要給的 term」。
2. `lumos search --about <檔> --prefix RULE,PITFALL,WHY` 沒有 term,必失敗。要改成 `term` 可選,spec 沒提,也沒說無 term 時的排序走哪條。
3. `--include-superseded` 在現有 search 是「含已作廢節點」(節點層,`_is_forgotten`)。S16 把它改成「行層」,同一旗標兩個語意,沒說兩層怎麼並存。
引句:「`lumos search --about <檔> --prefix RULE,PITFALL,WHY`」
佐證:`scripts/lumos:40168`、`scripts/lumos:40186`

**B10 「預設只給還有效的」的排除條件不齊,會把已作廢的 RULE 當有效載入**
severity: major
blocking: 是——按需載入要擋掉已失效內容,漏掉的恰是最常見的舊寫法。
1. 規則表寫 RULE「預設只給還有效的」。
2. 實際排除只有兩項:帶 `[superseded-by:]`,以及撤除條件已成立。
3. ④ 說舊的 `[status:superseded]` 寫法照認,但載入端沒有排除它。
4. `[until:]` 已過期的 RULE 也沒排除。表格說這種 RULE 過期要擋,載入端卻照給。
5. 輸入:一條 `RULE:[since:...][status:superseded]...`,`--prefix RULE` 照樣把它當有效規則吐給 agent。
引句:「預設排除帶 `[superseded-by:]` 與撤除條件已成立的行」

**B11 第 0 步先上線 W4,與「沒有 gate 一律不觸發」的 S1 衝突**
severity: major
blocking: 是——分期和合約候選互相矛盾,實作者必須猜哪邊算數。
1. 第 0 步標明「不等本案其他部分」,內容包含 W4:提交時對新寫的 RULE 行印缺 since/retire 的提醒。
2. `note_tags.gate` 要到第 1 步才出現。第 0 步上線時沒有開關可看,所有專案(含工具鏈與 rtb)都會多出這個提示。
3. 這與 S1(沒有 gate 時所有新欄位的擋與提醒一律不觸發)和〈實務隱患〉相容條「舊筆記…行為完全不變」互相矛盾。S1 被列為合約候選。
4. 二選一:W4 拿掉第 0 步,或明講 W4 不受 gate 管並放寬 S1。
引句:「提交時對新寫的 RULE 行印出缺 since/retire、until 過期這類提醒」

**B12 ⑥ 的「名稱本體自這行寫下後變了」沒有基準,S9 後半無法實作或驗證**
severity: major
blocking: 是——欄位 `[lives:路徑::名稱]` 不帶指紋,工具沒有「寫下當時的內容」可比。
1. 要比就得對每個帶欄位的行做 `git blame` 或 `git log -S`,再取出當時的符號本體,成本和失敗模式(行被重排、改名、換行)都沒交代。
2. spec 說借 Fiberplane 的錨點加指紋,但欄位裡沒有指紋。
3. 「本體」在非 Python 沒有語法樹可切邊界,怎麼取也沒說。
4. 沒有基準的話,「列進回頭重讀候選」要麼永遠不觸發,要麼每次推送都觸發。
引句:「名稱不在那支檔 → 擋;名稱本體自這行寫下後變了 → 列進回頭重讀候選、只提醒」

**B13 `--about <檔>` 在「一支大檔多篇共用家」時不收斂**
severity: minor
blocking: 否——不是會做出壞系統,但按需載入的目標「少塞不相關」在這裡失效。
1. 輸入:`--about scripts/lumos`。本 repo 有 40 篇 Systems 筆記在 about_code 列了它。
2. 這 40 篇的 WHY/RULE/PITFALL/FACT/FLOW/DEP/KEY 摘要行合計約 627 行(我用 grep 數的,口徑是 Systems 內以這些前綴開頭的行)。
3. `--top` 預設 0(全量),照字面一次吐出 600 多行,沒有按函式或欄位指向縮小的方法。
引句:「那支檔的家筆記的摘要行,加上 `lives`/`count`/`value`/`enum` 指到那支檔的行」

**B14 `note_tags` 設定壞掉時的行為沒定義**
severity: minor
blocking: 否——這是一般邊界,多數人不會踩到,但手滑的後果是靜默沒開。
1. 輸入:`"gate": "blcok"`、`"note_tags": "block"`(不是物件)、JSON 壞掉、`gate: null`。
2. 同族的設定都有明確處理並印警告:note_shape 壞值走 block、note_reread 走 warn、node_home 走 on。
3. 本 spec 只寫「沒有這個鍵 = off」,沒說壞值是 off、block 還是 warn,也沒說要不要警告。壞值靜默變 off,正好是「設了擋卻沒擋」。
引句:「設定裡沒有這個鍵 = off」
佐證:`scripts/lumos:24875`(`_note_shape_config`)、`scripts/lumos:5456`(`_note_lint_config`)

**B15 規則表兩處不一致或沒定義**
severity: minor
blocking: 否——都屬小處的決定,選哪邊都不會做出壞系統。
1. RULE 列寫 `[until:]` 過期 → 擋,但 W4 與 S11 只說「提醒」。`[until:]` 也不在〈欄位 v1〉六類裡,沒有驗收條款。
2. 同一行有多個 `[retire-when-*]` 時是「全部成立」還是「任一成立」沒說。既有 REVISIT 是全部成立。`[expect:]` 在多條件時管哪一個也沒說。
引句:「機器式撤除條件成立 → 擋;`[until:]` 過期 → 擋;`[confirmed:]` 超過半年 → 提醒;依賴欄位變了 → 擋」

**B16 S8 的「現況類小節」沒有判定法**
severity: minor
blocking: 否——可靠標題慣例補上,但要先寫出來。
1. 輸入:計劃轉 done,小節叫「現況」「背景」「盤點結論」「現在長怎樣」。
2. 照字面要擋「現況類小節」,但哪些標題算沒定義。靠標題字樣會漏掉換標題的、誤擋把「現況」當標題用的別的小節。
3. `[snapshot:日期@提交]` 的 `@提交` 是否要驗證(例如沿用 `_pin_commit` 的至少 12 位十六進位加在分支歷史上)也沒說。
引句:「計劃轉 done 時,現況類小節沒有 snapshot → 擋」

---

## 實務隱患(逐類)
- 併發:spec 說不新增寫入點。唯一的寫入是 init 寫設定,衝突見 B1。其餘無,因為全是唯讀計算。
- 效能:數量重算沿用 doctor N 的上限。這個上限內的行為(超限擋或放行)沒定義,見 B3。若選 B2 的全掃,每次推送的成本會多出一次。
- 資源:無,沒有長駐程序或連線。
- 回滾:設 off 即可,spec 的說法成立。前提是 B14 的壞值處理明確。
- 相容:有破口,見 B1 與 B11。
- 注入:search 輸出的是筆記原文片段,風險同現況。hook 的指令行裡檔名要沿用 `_plain_label` 消毒,spec 沒提,但現有程式已有。
- 自我治理的逃生口:`LUMOS_SKIP_*` 加設定降級沿用 note-shape 的套路,可行。但 B5 的誤擋只能靠移除欄位解,逃生口要寫進訊息。

最高嚴重度:major,blocking 12 條
