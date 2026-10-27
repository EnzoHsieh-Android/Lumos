severity: major

三問都有對照到 file:line。結論先講:指路層的做法對齊,但 `rN-repro.txt` 是第二種卷證做法。

### A1 `rN-repro.txt` 是第二種原始輸出落點,跟第 6 步的證據紀錄重疊且沒有講清關係
severity: major
blocking: 是
引句:「重現與改壞驗證的原始輸出另存 `rN-repro.txt` 進卷證，intake 只寫結論與指向」
- 專案已有一套「重現與改壞驗證的原始輸出」的記法。同一檔第 6 步 `before`/`after` 要記「實際命令、退出碼…行為觀測，連到原始輸出」,且明說「可引用同一個原始紀錄，無需複製內容」(file: `skills/lumos-design-loop/templates.md:242-245`)。第0步的 `guard kill` 子項也要求「真正失敗內容取既有 runner 原始報告」(file: `skills/lumos-design-loop/templates.md:232`)。
- 既有卷證檔名慣例是「一種用途一個檔」,而且都列在範本裡:`rN-intake.md`、`rN-dispatch.json`、`rN-fix.json`、`rN-behavior-cases.json`、`rN-repair.patch`、`rN-repair-binding.json`(file: `skills/lumos-design-loop/templates.md:222,236-237`)。`rN-repro` 在此之前不存在,全範本只有新增的這一處出現。命名形狀不衝突。
- 問題在新檔沒說跟第 6 步的 `before`/`after` 指標是什麼關係:是它取代原始輸出的落點,還是另一份?第6步說「連到原始輸出」,新句說「另存 rN-repro.txt」,兩句沒接起來。接手的人要猜原始輸出該放 `rN-repro.txt`,還是第 6 步指標指到的別處。
- 這條沒有機械守衛。`rN-repro.txt` 不在任何驗收檔清單,`scripts/test_lumos.py` 也沒有對應的檔名測試,卷證裡有沒有這個檔,收貨時沒人檢查。
- 建議:改成「原始輸出另存卷證,檔名沿第 6 步 before/after 的指標指到的那份」,或明講 `rN-repro.txt` 就是第 6 步 `before`/`after` 指標的落點。

### A2 WHY 行的出處/因/不選格式對齊,但一行裝了三件事,而且是這篇裡罕見的「指路型 WHY」
severity: minor
blocking: 否
引句:「寫在 `skills/lumos-design-loop/templates.md` §3.1 第0步〈先列出處清單再修〉,`skills/lumos-code-loop/SKILL.md` 第 5 步與」
- 欄位對齊:`[出處:]`、`[因:]`、`[不選:]` 都有,跟同篇的 WHY 行一樣(file: `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:45-57`,以及同篇的「派工詞範本寫明刪檔」「工具鏈本 repo 的代碼審鏡頭範圍」兩條)。
- 全形/半形不一致:新 WHY 行核心句用半形逗號、分號(「intake 再修,修補與拆小分開提交,重現…」)。三條對照裡,同篇的 WHY 核心句用全形「，」(「保留案例核對真正診斷與落帳，不只核對退出碼」),`SKILL.md` 第5步新增句也用全形「，」。不過同篇另有半形的 WHY(「派工詞範本寫明刪檔…」),所以鄰居本身不統一,只列 minor。
- 一行同時寫了「做法」「哪一層是單源」「指路處」。這跟鄰居「工具鏈本 repo…不複製第二份派工詞」那條是同一形狀,所以對齊,但沒有 `[test:]`、`[applies:]`。CLAUDE.md 的 WHY 表把這兩欄列為選填,所以不算缺。
- 新增的 WHY 行跟後面那條 WHY 之間多了一個空行(patch 顯示新行末尾 `+` 空行),同篇其餘 WHY 之間都是單一空行,沒有不一致。

### A3 單源指路:手冊層沒有抄第二份定義,跟鄰居一致
severity: clean
blocking: 否
引句:「動手修前先列同一問題的全部出處（同族函式、各處說法、新守衛的反向案例）、修補與拆小分開提交、重現輸出另存，見§3.1第0步〈先列出處清單再修〉。」
- `06-代碼審與推送.md` 新增一段,形狀跟〈修訂輪核對修補副作用〉既有的指路行一致:一句摘要,加「見§3.1第0步」。既有鄰居是「動手修前的根因組配對…同見§3.1第0步」「…亦見§3.1第0步」「同類提醒…同見§3.1第0步」(file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:124-130` 附近)。
- 新段的括號摘要列了三個要點,比鄰居的指路句稍長,但沒有重述定義:沒有「最少列哪些」「反向案例怎麼寫」。
- `SKILL.md` 第5步新增半句「先把每個根因組同一條規則、同一種說法的全部出處列進 intake 再修，修補與拆小分開提交、重現輸出另存 `rN-repro.txt`」,與該步原有「按共用範本§3.1第0步，替每個程式根因組先選…」同構,仍指向 §3.1 第0步為單源(file: `skills/lumos-code-loop/SKILL.md:50`)。
- ⚠ 輕微重述風險:`SKILL.md` 第5步直接寫出檔名 `rN-repro.txt`,而這是手冊層。若 A1 改了檔名,這裡得跟著改。此重複的程度跟第5步既有的 `rN-fix.json` 同級(file: `skills/lumos-code-loop/SKILL.md:51`),判 clean,提醒編排者一併改。

### 三問
1. 分層與依賴方向:對齊。單源在範本 §3.1 第0步子項,手冊(`06`、`SKILL.md`)只留指路,圖譜節點用 WHY 行記脈絡,層次跟鄰居一致,沒有抄第二份完整定義(對照 `templates.md:222-223`、`06-代碼審與推送.md:124-130`)。唯一的層級瑕疵是 A1 的 `rN-repro.txt` 檔名被複製到手冊層。
2. 命名與錯誤處理:大致對齊,見 A2。WHY 欄位齊全;範本新子項沿用 `**粗體標題**：` 加「（括號補充）」的子項形狀,跟 `同類提醒與根因關係分開` 等鄰居同形;全形/半形只在 WHY 核心句有小偏差。
3. 第二種做法:不對齊。`rN-repro.txt` 與第 6 步的「連到原始輸出」落點沒有說清楚分工,見 A1。另外,「修補和拆小分開提交」這條沒有引入新做法,它直接引用既有〈分開驗修補與重構〉(file: `skills/lumos-design-loop/templates.md:228`)。

不對齊共 2 條,其中 major 1 條。
