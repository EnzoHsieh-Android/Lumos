severity: major

審查對象:/tmp/tags/r1.md,鏡頭是回滾。hook 沒有附固定席筆記,所以「逐條判不影響」那項沒有對象可判。

**K1 回退節說「欄位留著無害」,但新欄位會取代舊欄位,退回去後舊工具會把已取代的 RULE 當成有效**
severity: major
blocking: 是——照字面實作並退回後,已被取代的 RULE 會恢復挑戰程式碼的效力,實作者會做出壞系統。
1. 輸入是新寫的 RULE 行,只帶 `[superseded-by:]`(按〈欄位不重複〉不再寫 `[status:superseded]`),或只帶 `[retire-when-*]`(不再寫 `[retire:]`)。
2. 把 `note_tags.gate` 改 `off` 或還原提交後,舊的 `rule_lifecycle_warnings` 只認 `[status:]`。沒有 `status:superseded` 就視為 active,見 `scripts/lumos:3334-3338`。只有 `retire-when` 就報缺 retire,見 `scripts/lumos:3328`。
3. 紀律範本把「沒被標 `[status:superseded]` 的 RULE」定義為可挑戰程式碼,見 `scripts/templates/graph-discipline.md:28`。被取代的 RULE 因此復活。
4. 即使不退回,spec 也只用 S21 讓 lint 認 retire-when,沒有任何條款讓 lint 或範本認 `superseded-by`。
5. 回退節只談「沒有消費者時只是文字」,沒有反向遷移,也沒要求保留舊欄位。
引句:「已經寫進筆記的欄位留著也無害(沒有消費者時只是文字),不必清。」

**K2 單一 `gate` 開關關不掉單一檢查,而 W6 的機械擋沒定義比對邊界,誤擋只能整包降級**
severity: major
blocking: 是——RETIRE-IF 承諾「撤掉對應那一半」,但回退只提供整包開關或還原提交,實作出來局部撤不掉。
1. W6 在 block 專案「同一行欄位值在欄位外又出現」就擋,沒說是子字串還是詞界。WHY 行依規定都帶出處日期,例如 `2026-10-01`;`=1` 或 `=4`、中文「一」都會誤中。
2. 誤擋的出口只有兩個:環境變數單次跳過,但 CI 照擋(〈自我治理〉);或把 `gate` 改 `warn`/`off`,這會同時關掉①到⑥和 W1 到 W6 全部檢查。
3. 先例 `note_shape.negation` 有獨立子開關,見 `scripts/lumos:25537-25560`,本案沒有。
4. ⚠ 交編排者:W6 的實際誤報率我沒實測,上面是由 spec 字面推出的場景。
引句:「欄位的值(數量、字面值、日期)在欄位外又出現一次——阿拉伯數字或中文數字都算——就擋」

**K3 搜尋過濾不受開關管,預設靜默隱藏行,回退節卻說第 1 到 4 步改 off 就能停**
severity: major
blocking: 是——第 4 步沒有開關,撤條件求值錯了也只能還原程式。
1. S16 讓 `lumos search` 預設不輸出帶 `[superseded-by:]` 或撤除條件已成立的行。
2. 這道過濾「不受開關影響」,但回退節把第 1 到 4 步都列為改 `off` 就停。
3. 撤除條件求值錯誤時(例如 `[retire-when-file:]` 被無關檔案滿足),仍有效的 RULE 會從預設搜尋消失。
4. 既有的 `--include-superseded` 是節點層級,並且會在 stderr 印「已隱藏 N 筆」,見 `scripts/lumos:4013`、`scripts/lumos:40186`。S16 把同名旗標改成行層級,又沒要求印隱藏筆數,agent 看不出被藏了東西。
5. 入口範例 `lumos search --about <檔> --prefix …` 沒給 term,但 `scripts/lumos:40168` 的 `term` 是必填位置參數。
引句:「載入那半(search 的新過濾)是唯讀的,所有專案都能用,不受開關影響。」

**K4 設定的讀取來源、壞值方向、init 寫入範圍和預設值收回都沒定**
severity: major
blocking: 是——這四點決定「關開關」到底退不退得乾淨,實作者只能猜。
1. 讀取來源:先例 `note_shape.gate` 讀被檢查的版本(提交前讀暫存區,推送與 CI 讀頂端提交),設定不是 block 時 doctor 每次印一行,見 `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md:48` 和 `scripts/lumos:25691`。spec 都沒提。若讀工作樹,本機未提交的 off 會繞過 CI。
2. 壞值方向:先例壞設定一律退回 block,見 `scripts/lumos:24877-24892`。照抄的話,JSON 壞掉的既有專案會被擋,違反 S1;反過來退 off,則 block 專案的設定壞掉時會悄悄停擋。spec 沒定。
3. init 範圍:`_init_config_skeleton` 在已有 config 時直接返回,見 `scripts/lumos:18678-18680`。已有 config.json 的新接入專案不會得到 `block`,S2 只測乾淨情形。
4. 收不回:`block` 寫進消費專案後沒有版本。撤案後它留著無作用,日後以不同語意重新引入同名鍵,所有舊專案立刻生效。spec 沒有 doctor 清單或遷移提示。
引句:「`lumos init` 對新接入的專案寫入 `block`(六類欄位的機械判準擋、寫法規則提醒)。」

**K5 「欄位只出現在新行」的假設不成立,判過時的掃描範圍和觸發時機沒定**
severity: major
blocking: 是——字面實作要嘛漏掉真過時,要嘛每次無關的程式推送都被舊行擋住。
1. 欄位行寫進去之後,是別的提交改了程式才讓它過時。判過時必須對庫內所有帶欄位的舊行讀現在的程式,不是只看新增行,上線點截斷也管不到它。
2. 既有的 drift check 是「推送讓條件從不成立變成成立」才擋一次,見 `scripts/lumos:27911`。③「成立 → 擋」沒有轉態語意,成立後之後每次推送都被擋,直到有人改那一行。
3. ④「兩端成對」同理。對端筆記被改名或重建後,無關推送也會被擋。
4. 從 `off` 或 `warn` 升到 `block` 時,關閉期間寫的欄位行會一次全部受檢,spec 沒講。
引句:「欄位判過時只看帶欄位的行,而欄位只會出現在新行上。」

**K6 治理帳:新閘名沒登記,誤報比例量不到**
severity: minor
blocking: 否——測試會在實作時抓到未登記的閘名,不會做出錯行為,只是退場條件沒有資料來源。
1. `_gate_event` 對不在 `_KNOWN_GATES` 的閘名直接不寫,只印警告,見 `scripts/lumos:1220-1224`。名單在 `scripts/lumos:6951`。spec 沒要求登記新閘名。
2. 跳過用的環境變數名也沒定,而 `LUMOS_SKIP_NOTE_SHAPE` 只管 note-shape。
3. 帳裡只有 blocked、warned、skipped-env。「誤報多過真報」沒有對應的事件種類,誤報是改欄位、降級還是跳過,帳都分不出來。
4. 退回後,帳裡留下不在名單的 `note-tags` 事件,無害,但 spec 沒提。
引句:「每次擋下與跳過都寫治理帳,`lumos gov --stats` 看得到次數,RETIRE-IF 的誤報比例就從這裡量。」

**K7 第 0 步的 RULE 提醒對所有專案生效,沒有開關,只能靠還原提交收回**
severity: minor
blocking: 否——只是多印提醒,不擋推送。
1. S11 沒有任何 gate 條件,而 S1 只管「新欄位」的擋與提醒,所以 W4 對 rtb 和所有消費專案都生效。〈相容〉節卻說「舊筆記沒有新欄位,行為完全不變」。
2. 回退節對第 0 步只說「各自還原那個提交」。lumos 是 symlink 分發,還原等於全域一次退。
3. 先例 `note_shape.negation` 有獨立 off,見 `scripts/lumos:25537-25560`。
引句:「當新寫的 RULE 行缺 since 或 retire,提交時 應 印出提醒(目前不印)」

**K8 紀律範本、skill、改檔前提示的速查表沒有列入回退,而且會灌進 gate=off 的專案**
severity: minor
blocking: 否——只造成多餘提示與 doctor 漂移訊息,不會破壞擋的行為。
1. 範本加一行會注入每個消費專案的 CLAUDE.md,gate 為 off 的也有,等於教 AI 寫沒人檢查的欄位。
2. 每次增刪這一行,doctor Check D 在所有消費專案都報「紀律區塊漂移」,直到它們重跑 `lumos update`,見 `scripts/lumos:2828-2838`。回退節沒列這些還原項。
3. 「範本有大小上限」只是 soft 提醒。現在 `scripts/templates/graph-discipline.md` 已有 11485 bytes,超過基線 5256 的 1.5 倍,見 `scripts/lumos:2851-2862`。
4. S17 說速查表依 `note_tags.gate` 決定附不附。impact-hook 不讀專案設定,它只吃 lumos 輸出的欄位,見 `scripts/hooks/claude/impact-hook.py:693-697`。這個開關要落在 lumos 的輸出上,spec 沒說。
引句:「紀律範本只加一行指路(範本有大小上限,而且所有專案都會注入,不放整張表)」

**K9 ④取代鏈跟既有的 `decision-supersede` 並行,對決策錨點的成對規則沒定**
severity: minor
blocking: 否——spec 沒說決策錨點的處理,最壞是實作者自己選一邊,不是 spec 字面會直接做錯。
1. 既有的 `decision-supersede` 只在決策本身寫單端的 `superseded_by`、`ended`,見 `scripts/lumos:15844-15883`。
2. ④允許錨是決策編號,但沒說另一端怎麼回指。照「只有一端 → 擋」,所有既有的決策翻案都會被當成單端。
3. 回退時兩條取代機制各自殘留,語意分岔。
引句:「錨可以是合約編號、決策編號或 `[id:]`」

**K10 行內 `[count:N re=… in=…]` 的語法會被 `]` 截斷,而且定型後很難改**
severity: major
blocking: 是——S4 要求它跟 doctor N 用同一個重算器,但正則常含字元組 `[0-9]`,欄位當場被截斷。
1. 既有行內欄位解析一律用 `[^\]]*`,例如 `scripts/lumos:3271-3276`。連既有 `[retire:]` 都被截斷過,所以才有 `rule_field_truncated`,見 `scripts/lumos:3292-3303`。
2. doctor N 用 HTML 註解 `<!--lumos:count=… re=(.+?)\s+in=… -->`,可以含 `]`,見 `scripts/lumos:3017`。兩種語法不等價。
3. 一旦使用者寫了含 `]` 的正則,事後要改語法就得掃回所有已寫的欄位行。〈寫法規則〉沒有轉義規則,也沒有版本標記。
4. ⚠ 交編排者:這取決於實作的解析器,spec 沒指定。若採括號配對解析,此條會降級。
引句:「找不到具名集合時用 `[count:N re=… in=…]`」

各節核對:
- 〈frontmatter 與 related〉:`Projects/標籤系統盤點_調研` 等 6 篇都存在,`Projects/Lumos定位_程式碼為主脈絡為輔_計劃` 和 `Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋` 存在。`Systems/筆記標籤` 是新建,不算壞引用。已讀,無 finding。
- 〈現況〉、〈設計原則〉、〈前綴表〉:已讀,無獨立 finding(相關問題併在 K2、K7)。
- 〈欄位 v1〉:K1、K5、K9、K10。
- 〈寫法規則〉:K2、K7。
- 〈一個事實只寫一處〉:K1、K2。
- 〈讓 AI 知道該寫什麼〉:K8。
- 〈按需載入〉:K3。
- 〈不溯及既往〉:K4、K5。
- 〈分期〉、〈已裁〉、〈天花板〉、〈不做〉、〈驗收條款〉、〈合約候選〉:已讀,無獨立 finding。

實務隱患逐類:
- 併發:無。spec 說不新增寫入點,但治理帳 append 本來就有,見 K6。
- 效能:無具體失敗場景。〈實務隱患〉說 search 新過濾「多一道篩」,但撤除條件求值要讀並解析目標檔,量級我沒量。
- 回滾:有,見 K1、K2、K3、K4、K7、K8。
- 相容:有,見 K1、K7。
- 自我治理的逃生口:有,見 K2、K4。
- 注入、資源、金流、對外送出:無,spec 的理由成立。
- 不可逆:「所有擋都能用設定關掉,欄位留著無害」不成立,見 K1。

最高嚴重度:major,blocking 6 條
