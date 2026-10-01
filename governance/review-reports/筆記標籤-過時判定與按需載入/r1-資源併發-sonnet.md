severity: major

固定席筆記:這次沒有 hook 附在尾端的固定席筆記,所以沒有「不影響」可判。

## 逐節讀完的結果

- 已讀,無 finding:前言與 frontmatter、依據、PRIOR-ART/RETIRE-IF、現況、設計原則、前綴表、不做、已裁、回退、合約候選。
- 〈驗收條款〉:S1 到 S21 都有 `[test:]` 或 `[manual:]`,沒有懸空編號。S19 排在 S20、S21 之後,只是順序問題。
- 內部交叉引用:`〈欄位 v1〉`、`〈一個事實只寫一處〉`、`〈回退〉`、`〈分期〉`、`〈讓 AI 知道該寫什麼〉` 都找得到對應小節。
- 有 finding 的節:欄位 v1、寫法規則、一個事實只寫一處、讓 AI 知道該寫什麼、按需載入、不溯及既往、實務隱患、驗收條款。見下。

**R1 擋的範圍自相矛盾:只看新行,還是前提一變就擋**
severity: major
blocking: 是——實作者得在「抓不到後來改程式造成的過時」和「每次推送掃全部筆記」之間猜,選哪個都是壞系統。
- 〈不溯及既往怎麼做〉說欄位只看新行。〈欄位 v1〉的 ①②⑥ 說「依賴欄位變了 → 擋」,意思是之後有人改程式,舊筆記上的欄位才算過時。兩句不能同時成立。
- 只看新行:那條脈絡要等到下次有人改這一行才會被檢查。防過期這個主要目的完全落空。
- 前提變了就擋:改程式的那次推送,範圍裡根本沒有筆記行。實作得在每次碰到程式的推送掃全部帶欄位的筆記,拿欄位指到的檔去比對。千篇筆記的 repo 每次推送都要整批讀圖譜。
- 現有的 `_note_shape_eval` 只看新增行。條件式回頭條件的探針則先用 `_drift_probe_is_candidate` 篩出「這次推送改到的才評估」,再有 `_DRIFT_BUDGET_SEC` 預算與起點對照。spec 兩樣都沒講要不要沿用。
- 沒有「起點對照」會造成誤擋:`_drift_probe_judge` 的做法是起點早就成立就不列。spec 的「成立 → 擋」是絕對值判定。某個欄位違規一旦進了主線(例如 `LUMOS_SKIP_NOTE_SHAPE=1` 跳過),之後每個人、每一次無關的推送都會被擋,直到有人去改那一行。
- 兩個推送的時序:A 把 `MODEL_VARS` 改成 5,B 在另一條分支新增 `=4` 的欄位,各自對自己的 tip 都綠。誰後推要靠 rebase 後重算才抓得到。若只看新行,先推 B、後推 A 時抓不到。④ 取代鏈的兩端分在兩個推送時也是同樣的狀況:只有一端的那次推送會被 S7 擋住,兩端沒法分開落地。
- 引句:「欄位判過時只看帶欄位的行,而欄位只會出現在新行上。」
- 佐證行 file: `scripts/lumos:25593`(`_note_shape_eval` 只處理新增行)、`scripts/lumos:28460`(`_drift_probe_is_candidate` 候選篩選)、`scripts/lumos:28630`(`_drift_probe_judge` 起點對照)

**R2 「同一個重算器」不存在,而且它讀工作目錄、沒有預算、上限超過後的結果沒定義**
severity: major
blocking: 是——S4 與 〈實務隱患·效能〉都建立在一個不可重用、也不吻合推送閘語意的函式上。
- doctor N 的重算不是函式,是 `cmd_doctor` 裡一段內嵌迴圈。S4 要的「同一個重算器」得先抽出來,spec 沒把這件事排進任何一期。
- 它用 `os.walk(repo_root)` 掃工作目錄,不是被推送的那個提交。note-shape 刻意從 tip 版本讀(`cmd_note_shape` docstring:「設定與內容都從被檢查的版本讀」)。推送的不是 HEAD、或 CI 不是 checkout 到該提交時,兩邊重算的數字不同。
- 它沒有 deadline。每一個標記都從頭 `os.walk` 整個 repo。上限 4000 檔 / 40MB 一碰到就 `RuntimeError`,只是列成「標記本身有問題」的軟提醒(doctor N 標題寫「提醒,不擋」)。spec 沒說這個狀況在 block 模式是擋、放還是報錯。
- 使用者寫的 `re=` 直接 `re.findall` 掃至多 40MB,沒有逾時。catastrophic 的正則(例如 `(a+)+$`)會讓 pre-push 卡住。程式內另一處註解(`scripts/lumos:4191`)就記過「兩萬個註解要 11 秒,每次健檢與推送前都跑」。spec 把這條路升成硬擋,卻沒帶預算。
- 引句:「正則寫法跟 doctor N 段的 HTML 註解標記同一個重算器」
- 佐證行 file: `scripts/lumos:3017`(內嵌迴圈與 `_MAX_FILES, _MAX_BYTES`)、`scripts/lumos:3024`(沒有 deadline,逐標記 `os.walk`)、`scripts/lumos:3060`(`RuntimeError` 只進軟提醒)

**R3 `[count:N re=… in=…]` 的行內寫法放不進多數正則**
severity: major
blocking: 是——天花板 3 與 S4 把這個形式當成「找不到具名集合」的退路,它卻無法承載含 `]` 的正則。
- 行內欄位的現有解析一律排除 `]`:`_PROBE_TOKEN_RE` 的值是 `[^\]\n]*`,`_NS_NEG_FIELD_RE` 是 `[^\]]*`,RULE 欄位也有 `rule_field_truncated` 專門抓「值裡含 `]` 被截斷」。
- 實際例子:`[count:3 re=^\s*[A-Z]+: in=docs/**]` 在 `[A-Z` 就被截掉,`re=` 變成殘缺的正則。doctor N 用 HTML 註解(`<!--lumos:count=… re=(.+?) in=-->`)正是為了避開這點。S4 要求兩種寫法「得到同一個數」,但行內寫法解析不出同一個 `re`。
- `in=` 的 glob 同樣不能含 `]`(例如 `[ab]*.py`)。spec 沒給跳脫或改寫規則。
- 引句:「找不到具名集合時用 `[count:N re=… in=…]`」
- 佐證行 file: `scripts/lumos:27913`(`_PROBE_TOKEN_RE`)、`scripts/lumos:3017`(HTML 註解形式)

**R4 ② 與 ⑥ 要的「寫下當時」基準沒有地方存,在淺複製與大歷史上也算不出**
severity: major
blocking: 是——兩個欄位的判準都以「寫下那一刻」為參考點,但欄位語法、「一個事實只寫一處」與驗收條款都沒給它的存放處。
- ② 的「寫欄位時記下當時的成員清單」:欄位只有 `[enum:路徑::列舉]`,沒有清單。若寫進欄位,就違反〈一個事實只寫一處〉。若用「句中反引號名稱」,句子常常只點名幾個而非全部成員(例如「每種付款方式都要走風控」),「少」會恆成立而恆擋。
- ⑥ 的「名稱本體自這行寫下後變了」:要找到這一行的寫入提交(`git log -S` 或 `git blame`),再讀那版的符號內容。對每一個帶 `lives` 的行都這樣做,大 repo、深歷史下是逐行的 git 呼叫。CI 淺複製下根本找不到。spec 沒說這樣判不了時怎麼辦。
- 對照:⑤ 有 `[snapshot:日期@提交]`,能存參考點。⑥ 沒有。S9 只驗證「列進回頭重讀候選」,沒驗基準來源。
- 引句:「寫欄位時記下當時的成員清單(或句中反引號名稱),跟現在的列舉成員兩邊比,多或少 → 擋」
- 引句:「名稱本體自這行寫下後變了 → 列進回頭重讀候選、只提醒」
- 佐證行 file: `scripts/lumos:24333`(現有「上線點」只用 `git log -S` 對一支掛鉤檔,不是逐行回溯)

**R5 「沿用回頭條件探針」被高估:探針只認 REVISIT 行,而且新鍵名根本不會被辨識**
severity: major
blocking: 是——spec 以為 ③ 是「接上既有求值器」,實際要新增一條行蒐集路徑和一整套時序語意。
- `_probe_lines` 只收 `_revisit_split` 判定為 REVISIT 條件式的可見行。③ 把 `[retire-when-file:…]` 掛在 RULE 或 WHY 行上,不會被收進來。
- `_PROBE_TOKEN_RE` 與 `_PROBE_ANY_RE` 的字首是 `[when-`。`[retire-when-file:` 開頭是 `[retire-`,兩者都不匹配。
- 更糟的是,note-shape 對「條件標記寫在 REVISIT 行以外」目前報違規「條件寫在不評估的地方」(`_ns_revisit_violations`)。新鍵名即使被辨識,也會與這條規則打架。
- 探針的 `_drift_probe_row_problems` 要求 `[by:]` 期限。spec 的 ③ 沒帶期限,S6 也沒驗。
- 探針是「這次推送讓條件從不成立變成成立」才擋(見 R1 的起點對照)。S6 寫「條件成立,推送應被擋」,沒說是否要求轉變。
- 引句:「沿用回頭條件探針求值;成立 → 擋;」
- 佐證行 file: `scripts/lumos:28062`(`_probe_lines`)、`scripts/lumos:27913`(`_PROBE_TOKEN_RE`)、`scripts/lumos:25323`(`_ns_revisit_violations` 的「不評估的地方」)、`scripts/lumos:28434`(`_drift_probe_line`)

**R6 `lumos search` 的預設排除不是「多一道篩」,要對每個命中行評估條件,而且影響所有專案**
severity: major
blocking: 是——spec 說這半邊不受開關影響、不用索引,實作者照字面做會讓每次 `lumos search` 多出 git 評估,且判不了時是顯示還是藏沒有規定。
- `cmd_search` 的主迴圈已經對每個筆記 `read_text` 並逐行過濾。`[superseded-by:]` 是純字串判斷,確實只是一道篩。
- 「撤除條件已成立」不是字串判斷。它要建 `_drift_probe_tree`(`git ls-tree -r`,上萬支檔)、讀被指到的程式檔、做 AST 或文字比對。
- 這要在每次預設 `search` 發生,而不是只在 `--about` 時發生,因為 S16 寫的是「search 應預設不輸出」。每次查詢都付一次列樹成本,逾時或 git 讀不出時要藏還是顯示,spec 也沒說。藏起來的話,agent 會看不到還有效的規則。
- 引句:「預設排除帶 `[superseded-by:]` 與撤除條件已成立的行」
- 佐證行 file: `scripts/lumos:3769`(`cmd_search`)、`scripts/lumos:28370`(`_DriftProbeTree.one`、`corpus` 的列樹與讀檔)

**R7 速查表的主要管道對筆記編輯根本不會觸發**
severity: major
blocking: 是——S17 與〈讓 AI 知道該寫什麼〉第 1 層寫的「改筆記前 hook 附速查表」,現有 hook 做不到。
- `impact-hook.py` 只對 `CODE_EXTS` 副檔名的檔觸發,`.md` 不在清單。`EXCLUDE_PATH_CONTAINS` 還明排除 `/docs/`。筆記路徑兩條都不過,連 `lumos impact` 都不會被叫。
- hook 只掛編輯類工具(`Edit/Write/MultiEdit/apply_patch`)。`check-graph-sync.py` 的註解實測近 12 份逐字稿裡改檔動作有 286 次走 shell(`sed -i`、heredoc)、31 次走編輯工具。多數筆記寫入不會經過這個 hook。
- 若要新增「筆記編輯」分支,要連 TTL 冷卻一起處理:同一檔 20 分鐘內改走 `--incidents-only` 快路,速查表是否重送沒有定義。
- 結果:「主要管道」實際涵蓋很少,第 2 層的提醒才是實際能送到的。spec 的 RETIRE-IF 與 S19 都沒有量這個管道的觸達率。
- 引句:「AI 要改一篇筆記時,既有的改檔前提示 hook(impact-hook,現在已經會附棧別檢核題)多附一張六行的速查表」
- 佐證行 file: `scripts/hooks/claude/impact-hook.py:31`(`CODE_EXTS`)、`scripts/hooks/claude/impact-hook.py:47`(`EXCLUDE_PATH_CONTAINS` 含 `/docs/`)、`scripts/hooks/claude/impact-hook.py:147`(`_decide_one`)、`scripts/hooks/claude/check-graph-sync.py:27`(shell 編輯 286 次的註解)

**R8 W6 的「中文數字也算」會讓小數值的欄位幾乎必擋**
severity: major
blocking: 是——block 模式下,`[count:…=1]` 或 `=2` 的行幾乎寫不出來,逃生口只有環境變數。
- 欄位的值是 1,散文裡的「一」(「一律」「一個」「同一」「唯一」)全部算重複。這些字在中文句子裡出現的頻率接近每行。值為 2 到 9 也有類似問題。
- 日期也算:WHY 規定要帶出處,常寫成 `[2026-10-01 …]`。若同一行有 `[confirmed:2026-10-01]` 或 `[until:…]`,一寫就擋。
- 「只比同一行」也沒有辦法排除欄位自己。例如 `[count:app/config.py::MODEL_VARS=4]` 裡的 `4`,要明講欄位內不算。
- 引句:「同一行裡,欄位的值(數量、字面值、日期)在欄位外又出現一次——阿拉伯數字或中文數字都算——就擋,訊息印出改法」

**R9 「不新增寫入點」與自己的逃生口設計互相矛盾**
severity: minor
blocking: 否——不改的話實作會照既有慣例寫帳,行為正確,只是併發那一行的聲明不準。
- 〈實務隱患·自我治理〉要求每次擋下與跳過都寫治理帳。治理帳 `docs/.governance-log.jsonl` 是被 git 追蹤的檔(開場 git status 就顯示它被改了)。推送時寫它會讓工作目錄變髒,兩個同時進行的推送會各寫一筆。
- 〈實務隱患·併發〉卻寫「全部是推送前或查詢時的唯讀計算,不新增寫入點」。
- 引句:「不碰。全部是推送前或查詢時的唯讀計算,不新增寫入點;設定檔由人或 `lumos init` 寫。」
- 佐證行 file: `scripts/lumos:1234`(`_gate_event_or_warn`)、`scripts/lumos:1260`(`_append_governance_log` 寫 `docs/.governance-log.jsonl`)

**R10 ⑤ 快照的擋點只寫在「轉狀態」,推送閘與平行寫入路徑沒交代**
severity: minor
blocking: 否——最差是手改 frontmatter 繞過,可由後續把檢查移到推送時補。
- S8 寫「轉狀態 應 被擋」,指 `lumos set status done`(`cmd_set`)。直接手改 frontmatter、重建筆記(regen)、`drift fix` 這些寫入路徑不經過它。〈實務隱患〉卻把 ⑤ 列在「新的推送閘」。推送時要比對 base 和 tip 的 `status` 才知道有沒有轉 done,spec 沒寫這一段。
- 「現況類小節」的識別沒定義。是靠標題文字、還是靠專用標記,實作者得猜。
- 引句:「當計劃轉 done 而現況類小節沒有 `[snapshot:]`,而專案開 block,轉狀態 應 被擋」
- 佐證行 file: `scripts/lumos:15266`(`cmd_set`)

## 實務隱患逐類

- **併發/時序:有隱患。** 見 R1(兩個推送、取代鏈兩端分兩次推)與 R9(治理帳寫入)。
- **效能/大 repo:有隱患。** 見 R1(全掃筆記 vs 候選篩選)、R2(重算器沒預算)、R4(⑥ 逐行 git 回溯)、R6(search 預設評估)。
- **判不了該擋還是放:有隱患。** spec 全篇沒有任何一條寫「判不了」的處理,見 R2、R4、R6。
  - 先例互相不一致:note-shape 在淺複製與 git 失敗時 fail-open(`cmd_note_shape`),drift check 則判不了算「要處理」(`scripts/lumos:28630` 附近的 strict 語意)。
  - 影響到的具體情境:CI 淺複製、git 讀檔逾時、超過 4MB 的程式檔、剖不動的 Python、非 Python 語言(天花板 5)、重算超上限。
- **淺複製 CI:有隱患。** note-shape 的 `--diff` 在淺複製下印一句就 rc 0 跳過(`scripts/lumos:25792`),不是硬擋。
  - spec 的逃生口寫「CI 照擋」。預設 `fetch-depth: 1` 的 CI 上,所有掛在這個入口的新檢查會靜默不生效。
  - 現有先例有提醒機制:`_note_shape_doctor_lines` 會告訴使用者 CI 沒抓完整歷史。spec 沒說 `note_tags` 要不要接同一套提醒。
- **資源/長駐:無。** 不開長駐程序、不加連線。
- **注入:無新增。** `lumos search` 輸出的片段與現況相同,推播 hook 維持只印篇名,這點與程式一致(hook 只印篇名與合約類別,見 `scripts/hooks/claude/impact-hook.py:629`)。
- **回滾:無新增。** 關掉 `note_tags.gate` 即可;欄位留著無害,這個宣稱成立。

最高嚴重度:major,blocking 8 條
