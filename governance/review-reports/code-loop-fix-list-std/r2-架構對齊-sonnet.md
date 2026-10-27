severity: minor

**1. 分層與依賴方向**

單源和指路的結構跟鄰居一致,沒有第二份定義。

- 完整做法只在 `templates.md` §3.1 第 0 步〈先列出處清單再修〉。
- `SKILL.md` 第 5 步只加一句「先照〈先列出處清單再修〉列齊同一問題的出處」。
- 06 手冊只加一行「見§3.1第0步〈先列出處清單再修〉」。
- 06 這行的寫法和同節既有五行指路(「同見/亦見§3.1第0步」)一樣,只指路、不抄內容。
- 上一輪修補把 06 原本括號裡的「同族函式、各處說法…」「拆小分開提交、重現輸出另存」整串拿掉,等於把抄在手冊的第二份定義收回。這一步讓它更對齊。
- 對照:`skills/lumos-project-notes/commands/06-代碼審與推送.md:111-123`、`skills/lumos-code-loop/SKILL.md:60`。

圖譜節點的 WHY 行比鄰居長,還複述了「暫時本機提交」「壓成一個」「rN-repro.txt」這些做法細節。鄰居的 WHY 多半只寫結論。這是漂移風險,不是結構錯,所以不列 finding。節點的家與 `about_code` 沒變,對照 `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:63-69`。

有一處在同節內重複定義,見 A3。

**2. 命名與格式**

- `[出處:] [因:] [不選:]` 欄位、`〈…〉` 節名引用、粗體小標,都和鄰居一樣。
- 新 WHY 行沒有 `[test:]`,但鄰居的同類 WHY(保留案例、同類提醒等)也沒有,對齊。
- 兩處不齊,見 A1、A2。

### A1 第 2 步的交叉引用指到錯的步驟
severity: minor
blocking: 否
引句:「兩端提交碼照本節第2步存進下一輪的 `rN-repair-binding.json`」
- 本節第 2 步是產生 `rN-repair.patch`,第 3 步「留來源」才建 `rN-repair-binding.json`。第 1 步是固定兩端。
- 鄰居(第 0 步與 06 手冊)的交叉引用都指對步驟。
- 對照:``file: `skills/lumos-design-loop/templates.md:236-237` ``。

### A2 同一條 bullet 裡 rN 的輪次口徑不一致
severity: minor
blocking: 否
引句:「修補這一輪重現與改壞驗證的完整原始輸出另存同輪的 `rN-repro.txt` 進卷證」
- 既有卷證檔 `rN-repair.patch` 和 `rN-repair-binding.json` 都以「下一輪」編號(第 2、3 步寫「存到下一輪的 rN-…」)。
- 新的 `rN-repro.txt` 和 `rN-intake.md` 改用「同輪」編號,同一條 bullet 裡 rN 的口徑不一致。
- 讀者容易搞不清 r1 修補產生的是 `r1-repro.txt` 還是 `r2-repro.txt`。
- 對照:``file: `skills/lumos-design-loop/templates.md:236-237` ``。

### A3 暫時本機提交與推前壓成一個,在同節重複定義
severity: minor
blocking: 否
引句:「先各用一個暫時本機提交分開」
- 同節後面已有一條單源規則:「中間點可用暫時本機提交；推前仍按一功能一提交整理…壓提交或換基底後按原規則重新固定派工版本」。
- 新 bullet 又寫了一遍「暫時本機提交…推前壓成一個」,同一節內有兩處說這件事,違反「同一條規則只准一份定義」。
- 新 bullet 只需指向〈分開驗修補與重構〉那條,不必再寫提交處置。
- 對照:``file: `skills/lumos-design-loop/templates.md:77` ``。

**3. 第二種做法**

沒有判到第二種做法。

- 卷證裡本來就有原始輸出的 `.txt`(例如 `ablation-green.txt`、`baseline-before-fix.txt`),`rN-repro.txt` 不是新種類的檔。
- `rN-intake.md` 本來就是編排者的機械重現留痕,範本註明「前掃語意類修正也逐條記這裡」。把出處清單放進去,是沿用同一個落點。
- 三個檔分工清楚:
  - `rN-repro.txt` 放完整原始輸出。
  - `rN-intake.md` 放命令、摘錄與 HIT/MISS。
  - `rN-repair-binding.json` 放兩端提交碼、樹碼與指紋。
- 上一輪修補把 repro 改成「下一輪新席按第6步填 `before`／`after` 時可以連到它,但第6步的證據紀錄仍由新席自己查證,不以這份代替」。這讓 repro 不取代第 6 步的證據紀錄。
- 因此 repro 不是第二個落點。第 6 步原本只寫「連到原始輸出」而沒指定位置,repro 是它的連結目標之一。

**修補鏡頭**:這次修補沒有讓原本對齊的地方變得不對齊,反而讓 06 手冊的指路更對齊。它新帶進兩個小瑕疵,就是 A1 的步驟編號錯和 A3 的同節重複,都是 minor。

不對齊共 3 條,其中 major 0 條
