severity: minor

整體判斷：規則、樣本、型錄、測試、圖譜節點、卷證放的位置都跟前幾批一樣，沒有引入第二種做法或跨層直呼，也沒有 major。不對齊的有 6 條，全是 minor。

repo 根：`/Users/enzo/orca/workspaces/lumos-toolchain/unwired-remeasure`。下面的 file: 路徑都相對這個根。

### 1. 分層與依賴方向

對齊，只有兩處小偏差（見第 D、F 條）。
- 規則檔仍在 `configs/ast-grep/kotlin-android/rules-unwired/`，樣本在 `samples/bad|good/&lt;規則名&gt;/`，型錄在 `skills/kotlin-idioms/checks-catalog.md`，測試仍是 `scripts/test_lumos.py` 的 `t_kotlin_rulepack_unwired_dir`。
- lands_in 寫 `Systems/kotlin規則包`，跟第二、三批計劃一樣。
- 整條規則連樣本一起刪、`rules-unwired/compose.yml` 整支刪掉，之前就有先例。對照：`git show b9a64e9b4` 刪了 `kt-register-pair-missing` 的 bad/good 樣本。
- 卷證形狀沿用 `governance/review-reports/&lt;slug&gt;/experiment/` 加 `r1-*.md`、`r1-intake.md`、`r1-dispatch.json`。對照：`governance/review-reports/android資安靜態檢查補齊第三批/` 有同樣的 `experiment/` 與 r1 檔案組。
- 決策翻案用 frontmatter 的 `valid:false`、`superseded_by`、`ended`，跟 `Projects/棧別提問表態閘_計劃` 那類寫法同一套。跨計劃用 `[[…]]#d1` 的寫法，同類例子只找到「`[[…]]` 不帶 `#d`」那一筆。

### 2. 命名與錯誤處理

- 規則訊息對齊。我量過 7 條改寫後的訊息，都是 `[型錄編號]錯在哪;改用…`，長度 69 到 109 字，在 120 字上限內。
- 型錄〔查證 2026-11-08:網址〕跟 `〔查證 2026-11-05:…〕` 同格式。
- 重量數字寫進實測狀態欄，沿用「樣本內…、樣本外…；日期 換一批語料重量…，見 [[計劃]]」的句型。對照：`skills/kotlin-idioms/checks-catalog.md` 的 DATA-87 列。
- 不對齊 A：樣本裡「不報」例子的註解寫法。
- 不對齊 B：兩列「通電批次」欄的用詞。

A. 樣本註解用了新前綴「// 不報:」，鄰居慣用 `// 容易誤報:`、`// GOOD:` 或 `// case: &lt;名稱&gt;`。
- 全樣本有 138 處「容易誤報:」、105 處「// case:」。
- 新的「不報:」前綴只出現在這次的兩個檔案。
- file: `configs/ast-grep/kotlin-android/samples/good/kt-async-await-immediately/src/main/kotlin/kt-async-await-immediately.kt:11`（同檔第 5 行用的是「容易誤報:」）
- file: `configs/ast-grep/kotlin-android/samples/good/kt-click-navigate-unguarded/src/main/kotlin/kt-click-navigate-unguarded.kt:25`（同檔其他三個案例都用 `// case:`，這個沒有）

severity: minor
blocking: 否
引句:「別的 scope 的 async、View 的點擊導航在好例裡」

B. 型錄 API-36、UI-103 兩列的通電批次欄寫成 `告警帶寫法=未接(型錄這列出處不全,規則已移除)`，是新句子。
- 原本只有三種：`規則在 rules-unwired/:…`、`登記的現成檢查擋不到這列壞寫法…`、`還沒有規則`。
- 型錄第 11 行的「通電批次欄的值」說明沒列這種寫法。
- 計劃卻寫「通電批次改寫成跟其他不接閘規則同一句」，這兩列沒照辦。
- file: `skills/kotlin-idioms/checks-catalog.md:188`、`skills/kotlin-idioms/checks-catalog.md:430`、`skills/kotlin-idioms/checks-catalog.md:11`

severity: minor
blocking: 否
引句:「通電批次改寫成跟其他不接閘規則同一句」

C. 回頭條件沒有照鄰居的慣例收掉。
- 第二批計劃關掉回頭條件時，在行尾加 `[closed:日期 [[計劃]] 結果]`，這次對第二批的 REVISIT 也這樣做了。
- 但逐列查證計劃的 REVISIT 2027-02-08「重查 API-14 與 TEST-31 的官方出處…找到就把那一列的(出處不全)拿掉、規則搬回 `rules/`」沒有加 `[closed:…]`。
- 這件事這次已經查完了，結論是找到原文但規則留在 `rules-unwired/`，這條卻還開著，寫法也跟實際結果相反。
- file: `docs/lumos-toolchain-knowledge/Projects/Android寫法型錄逐列查證_計劃.md:104`
- 對照：`docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:95`

severity: minor
blocking: 否
引句:「逐列查證計劃 d1 的翻案與正文補註」

### 3. 第二種做法

整體沒有 major 等級的第二種做法。
- 移除規則：沿用「整條連樣本刪」的先例。
- 翻案：沿用 frontmatter 的 `valid:false` 和 `superseded_by`。
- 卷證：沿用既有形狀。
- 出處補查的證據放 `experiment/source-recheck-a|b.md`，跟逐列查證計劃的「12 批結果＋二次深查」同類。
- 逐列查證計劃的正文多了一段粗體括號「以下是當時的裁定紀錄,不是現況」。這是在 frontmatter 之外多一種標示法，但沒有取代 frontmatter，我只算輕微，不單獨列。
- 有一處接近「第二種做法」：出處不全的規則，原本一律搬到 `rules-unwired/` 停放，這次對查不到的規則改成刪掉。這條放在下面第 E 條。

### 4. 落點合不合理

- 不對齊 D：規則包節點沒寫完整。
- 不對齊 E：規則包節點的原則句跟新做法打架。
- 不對齊 F：計劃是否該拆開。

D. `Systems/kotlin規則包` 只改了兩處，其他過時句子還在。
- 只改了：WHY 資安那行補了重量結果，以及第 76 行把條數改成 27 並列出移除的三條。
- 第 51 行的 WHY 仍寫「2026-11-08 使用者裁定標出處不全、三條規則搬 rules-unwired/」，沒標已被取代。
- 第 76 行仍保留「同日 API-14、TEST-31 人裁標出處不全，再從 rules/ 搬 2 條」。現在這兩列已拿掉出處不全。
- 「引用型錄出處不全列的規則放這裡」這個條件，在 `rules-unwired/` 內已經沒有規則符合。
- 只靠一句「見 [[計劃]]」把現況推給計劃，節點本身會誤導下一個讀的人。
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:51`、`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:76`

severity: minor
blocking: 否
引句:「[[Systems/kotlin規則包]] 不接閘目錄那行改成 27 條並寫明移除的三條」

E. 原則句跟新做法沒對上，節點也沒補新的 WHY。
- 節點第 52 行有測試綁定的 WHY：「引用型錄出處不全列的規則只准放不接閘的 rules-unwired/」。意思是出處不全就停放，不是刪。
- 這次的新做法是「查不到或跟官方相反就移出規則包」。API-36、UI-103 兩列仍標出處不全，卻沒有規則掛著。
- 這個「停放或刪除」的取捨寫在計劃裡，沒有進節點的 WHY。
- 刪規則本身有先例、使用者也明講要移掉，所以我只判 minor。
- file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:52`

severity: minor
blocking: 否
引句:「規則與壞例好例樣本一起刪;`rules-unwired/compose.yml` 只剩這一條,整支刪掉」

F. 一份計劃同時做「重量」與「出處補查」，建議拆開。
- 標題只講「資安規則重量」，但出處補查的 11 條規則裡 8 條是協程、測試等非資安規則（FLOW-14、CO-37、TEST-16、STATE-9、TEST-33、ARCH-3、API-14、TEST-31）。
- 補查的主體是翻案逐列查證計劃的 d1，實際該住在那一條線上。
- 兩件事的依據、卷證、驗收條款（S2 對 S3、S4）都各自獨立。
- 計劃自己的審計紀錄寫「同輪加進出處補查」，是 r1 才併進來的。
- 先例是第二批計劃把新規則與重量放同一篇，所以不算 major。
- 但之後想找「出處補查」的人，很難從標題找到這篇。
- 建議二選一：拆成獨立計劃，或至少把標題與 lands_in 說明改成兩件事都涵蓋。
- file: `docs/lumos-toolchain-knowledge/Projects/Android不接閘資安規則重量_計劃.md:25`
- 我沒有核實這個標題在 repo 內被別處當關鍵詞引用的情況，這點請編排者視需要確認。

severity: minor
blocking: 否
引句:「盤點後只登記那一級有 11 條規則掛在型錄出處不全的列上」

不對齊共 6 條，其中 major 0 條

我在 `/tmp/lumos-seat-work/android不接閘資安規則重量/架構對齊二-sonnet/` 下沒有建任何東西，也沒改 repo 內任何檔案。
