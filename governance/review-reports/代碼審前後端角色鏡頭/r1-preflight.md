# r1 前掃:代碼審前後端角色鏡頭_計劃(r1-snapshot.md)

範圍:唯讀。repo = /Users/enzo/harness/lumos-toolchain/.claude/worktrees/fe-be-lens。程式行為以 `scripts/lumos`、`scripts/hooks/claude/dispatch-lens-hook.py`、`skills/lumos-design-loop/templates.md` 現況為準。

## ① 未定義的詞

- 「畫面觸發規則」「畫面檔」「畫面層」:計劃通篇用,但程式裡沒有這個概念,只有各題自己的 `when` 觸發字(見 ④-4)。計劃沒說「畫面檔」的判準到底是什麼(哪一題、命中幾個字才算),S3 又只寫「那幾題的觸發字」,沒列是哪幾題(推得出是 kt-compose、swift-swiftui、dart-build,但計劃沒點名)。
- 「角色」:前端/後端/判不出,有定義。「判不出」在 要做什麼 第 1 點有寫,OK。
- 「附段」「固定段」「固定席」:「固定席」在計劃裡沒解釋(範本第 3 節第 3 點才有:帶硬合約或出過事故的節點);讀者要跨文件才懂。「附段」與現有 hook 附的固定席段是不是同一段,計劃沒講清楚(見 ④-3)。
- 「卡」(前端卡/後端卡):有描述內容,算有定義。
- 「條目帶出的折入數」(REVISIT 行):「角色鏡頭條目」沒說席報告裡怎麼辨認哪一條是角色鏡頭帶出來的(沒有標記約定),撤除條件與 REVISIT 因此量不出來。
- 「第 ④ 點」「第 ① 點」「第 ⑤ 點」:範本第 3 節的審查鏡頭是阿拉伯數字 1–4,同一節「編排者派工前須知」另有一組圈圈 ①–④(意思完全不同,④=Codex 當編排者)。計劃用圈圈字指阿拉伯編號的點,有歧義(見 ④-7)。

## ② 壞引用

- `[[Projects/代碼審資料狀態鏡頭_計劃]]`、`[[Projects/派工鏡頭注入_計劃]]`、`[[Systems/棧別提問表態閘]]`、`[[Systems/效能檢核目錄]]`、`[[Systems/pitfalls-code-loop]]`、`[[Systems/codex-harness]]`、`lands_in` 的 `Systems/design-loop`:全部存在(docs/lumos-toolchain-knowledge/ 底下 .md 都在)。
- 提到的路徑:`.lumos/config.json`(消費專案設定檔,本 repo 也讀它,OK,但「角色路徑對照」那一鍵目前不存在,屬新增)。`_node_flavor` 等函式未寫路徑,沒有壞路徑。
- `[[Systems/codex-harness]]` 被寫成「管那支掛鉤」:codex-harness 的 about_code 確實列了 `scripts/hooks/claude/dispatch-lens-hook.py`,成立。
- 壞引用:無。
- 附帶:`lands_in` 有 `Systems/design-loop`(範本在 skills/lumos-design-loop/templates.md,家是否為 design-loop 我未逐一驗 about_code,僅提醒)。

## ③ 範圍自相矛盾

- 「不做」節說「不改風險分級規則」,要做第 3 點卻說「推送前的風險分級輸出多印一行」:只是多印一行,不改分級,不算矛盾,但要求「這行不改變分級結果」的守衛是 S6,一致。
- 「不改席位編制(全端改動也不拆成前端席和後端席)」與 S4「同時含前後端檔應兩張都附」:一致(同一席附兩張)。
- 決策 d1「不補推送前的前端檢核題、不擋推送」與 要做什麼 第 3 點「推送前的風險分級輸出多印一行『前端 N 檔、後端 M 檔』」:多印的那行是在推送前的 pitfalls 輸出,屬人看的統計,不是檢核題;字面上有輕微張力(「只做派工詞」vs 動 pitfalls 輸出),建議計劃明講這行算例外。
- 實務隱患寫「角色判定只看檔名、package.json 與改動行,不得多開一次全圖掃描」,但 S3 的手機畫面判定要比對改動行(見 ④-4):同一句裡「改動行」是有列入的,一致;但 要做什麼 第 1 點寫手機畫面檔 → 前端是「檔名」層級語氣,與「靠改動行觸發」不同層,建議統一。
- 「宣告優先」(S1)與「手機畫面走改動行觸發」:宣告能不能宣告手機畫面檔為前端/後端,計劃沒寫(路徑樣式對 .kt/.swift/.dart 都能宣告,應該可以,但沒說)。
- 其餘矛盾:無。

## ④ 機械宣稱驗語意

### ④-1 依副檔名與最近的 package.json 判前端或 Node 後端

計劃原句:「依副檔名與最近的 package.json 判一支檔是前端還是 Node 後端(判定函式在管 pitfalls 的那一帶,見 [[Systems/pitfalls-code-loop]]),拿來選棧別檢核題組和慣例 skill」;要做什麼 第 1 點:「沒宣告就用既有判定兜底:前端框架依賴或 .vue/.tsx/.jsx/.css/.html …→ 前端;.cs/.java/.py/.sql 與 Node 後端 → 後端」。

程式實際行為:
- file: `scripts/lumos` 函式 `_node_flavor`:只看檔案所在目錄往上「最近的 package.json」,只讀 dependencies/devDependencies/peerDependencies 的鍵,`_NODE_FRONTEND_MARKERS = ("vue","nuxt","react","next","svelte","@angular/core","solid-js","preact")` 是**整個鍵精確相等**(`m in deps`,deps 是 set),不是子字串:只有 `react-dom`、`@vue/...` 而沒有 `react`/`vue` 的 package.json 判成 node。有前端框架 → 回字串 "vue"(標籤,不是「前端」);有 package.json 沒前端框架 → "node";找不到 → None。最近的 package.json 就是最終答案,不會繼續往上找有依賴的那份:monorepo 某個子目錄放一份只有 `{"type":"module"}` 的 package.json,底下的前端 .ts 會被判 "node"。
- file: `scripts/lumos` 函式 `_stack_key_for_file`:只有 `_NODE_EXTS`(ts/tsx/js/jsx/mjs/cjs/mts/cts)才查 `_node_flavor`;其他副檔名直接回副檔名(若在 `_STACK_PERF_QUESTIONS` 裡)。因此 `.tsx/.jsx` 在**無前端依賴的 package.json 下現在判 "node"**,在找不到 package.json 時判 None,不會因副檔名就判前端。`.vue` → "vue"(有題組);`.css`、`.html` → None(沒有題組,現有機制完全沒判定)。`.cs/.java/.py/.sql` → 各自的棧鍵(cs/java/py/sql),機制上只是「有題組的副檔名」,沒有「後端」這個角色概念。
- file: `scripts/lumos` 函式 `_idiom_skill_for`:.ts/.js 家族 node → node-idioms,其餘(前端、找不到 package.json)→ vue-idioms。另外 `_ARCH_IDIOM_SKILL` 把 kt/kts/swift/dart 也各對一個 skill。

判定:**部分符合**。「.ts/.js 依最近 package.json 分 vue/node」屬實;但 (a) 沒有「前端/後端」角色概念,只有棧鍵與 "vue"/"node" 標籤,角色函式是新寫;(b) 計劃 S2 的「.tsx/.jsx/.css/.html 應判前端」不是既有行為(既有:.tsx 在後端 package.json 下判 node、.css/.html 判 None),是新規則,不是「兜底沿用既有」;(c) 「最近的 package.json」對空殼 package.json 會誤判;(d) 判「前端」標記為鍵精確相等。

### ④-2 全端改動各檔各判、取聯集

計劃原句:「全端改動各檔各判、取聯集」。

程式實際行為:
- file: `scripts/lumos` 函式 `_stack_key_for_file`(逐檔呼叫,每檔各自查最近 package.json)與 `_arch_alignment_hints`(`idiom_skills` 由逐檔的 `_idiom_skill_for` 收進 set、`sorted(skills)` 輸出);`_stack_applicability` 以 `{棧: [行]}` 逐棧各判。

判定:**符合**(逐檔各判、慣例 skill 取聯集。注意題組適用性是「逐棧」聚合行,不是逐檔,見 ④-4)。

### ④-3 派工鏡頭 hook 的通道

計劃原句:「沿用派工鏡頭 hook 的通道(派工詞有圖譜鏡頭那行時,在尾端附固定段),多附『這次改到的角色與對應的卡』」;實務隱患:「派工鏡頭附段有時間預算:附段是在派子代理那一刻由掛鉤算的,超時就附不到節點」。

程式實際行為:
- file: `scripts/hooks/claude/dispatch-lens-hook.py` 函式 `main`、`find_marker`、`_emit_updated`:派工詞逐行找 `LUMOS-IMPACT: <range>`(整行只有這個);找到就叫 `lumos dispatch-lens <range> --repo … --json --deadline <秒>`,把回傳 JSON 的 `text` 接在派工詞尾端(`updatedInput`)。**`text` 為空就什麼都不附**(`if not text: return 0`)。
- 時間預算:`_outer_budget`(從 `--budget` 讀天花板,預設 60、上限 600)、`_inner_budget`(天花板×0.7−已耗,下限 1 秒);`--deadline` = min(max(3, 內層預算), 天花板×0.9),外層 subprocess timeout = min(deadline+5, 天花板×0.9)。超時或 rc==5 → **只附一行 `TIMEOUT_NOTE` 說明,不附任何節點內容**,其餘失敗一律放行不附。
- file: `scripts/lumos` 函式 `cmd_dispatch_lens`:結果依 (base, head, 表態記錄 sha) 快取 20 分鐘(`_lens_cache_read` ttl=1200);帶 deadline 時 `_lens_wait_or_warm` 派脫離行程去算、這邊等快取;內層總預算 `_LENS_INNER_BUDGET = 45.0`、`_LENS_FALLBACK_RESERVE = 5.0`。`text` 由 impact 固定席(或固定席 0 篇時的備援段)與表態記錄行組成;角色資訊完全不在其中。
- Codex 通道:另一條,`--arm`/`--claim`(SubagentStart),派工詞沒有標記行;由 armed 檔領席、`additionalContext` 附上。設計審 `LUMOS-SPEC:` 又是第三條。
- 錨點:該 hook 在 `ANCHOR_FILES`(檔頭註明改它要 `lumos anchor approve --note`);計劃「回退」與「實務隱患」沒提這個額外步驟。

判定:**部分符合**。通道與「標記行→尾端附」屬實,有時間預算屬實。不符/風險點:(a) 超時時只附超時說明,角色卡會跟著整段消失,不是「只丟節點、卡照附」;計劃若期望角色卡不受超時影響(角色判定只看檔名與 package.json、成本很低),現有通道做不到,得另外決定;(b) `text` 空(例如非固定席為 0 且備援段也空)時 hook 整個不附,角色卡若併進 `text` 也會丟,若另附又要改 hook 的 `if not text` 邏輯;(c) 快取 key 不含角色判定,但角色只依 diff 檔名與 package.json(package.json 在 base..head 間變動時 20 分鐘內可能過期),計劃沒提;(d) Codex `--claim` 與 `LUMOS-SPEC` 兩條通道計劃沒說是否也附角色卡(S4 只寫「派工詞有圖譜鏡頭那行」= Claude 通道);(e) 改 hook 檔要 anchor approve。

### ④-4 手機畫面檔命中既有棧別題組的畫面觸發規則

計劃原句:S3「當改動裡的手機畫面檔命中既有棧別題組的畫面觸發規則(Compose、SwiftUI、Flutter 那幾題的觸發字),角色應判前端;同一種副檔名但沒命中畫面觸發的不判前端」。

程式實際行為:
- file: `scripts/lumos` 的 `_STACK_QUESTION_SPECS`:kt-compose(when 含 `@Composable`、`LaunchedEffect`、`remember`、`Lazy(Column|Row|VerticalGrid)`、`findViewById`、`RecyclerView\.Adapter`、`notifyDataSetChanged`、`.inflate(`、`ViewHolder` 等)、swift-swiftui(`var body`、`@State`、`@Observable`、`ForEach`、`List`、`AnyView`、`GeometryReader`、`.animation(`、`reloadData()`、`UICollectionView` 等)、dart-build(`Widget build(`、`setState(`、`StatefulWidget`、`ChangeNotifier`、`notifyListeners`、`Provider.of`、`context.read`、`ValueNotifier` 等)。這些是 regex,比對的是「改動的行內容」(增行與刪行,先剝字串字面、跳註解),**不是檔名**。
- file: `scripts/lumos` 函式 `_stack_applicability(lines_by_stack, threshold)`:輸入是 `{棧: [改動行…]}`——**同一棧所有檔的改動行合在一起**比,不是逐檔;輸出是「這個棧的這題適用與否」,沒有「哪支檔命中」。而且某棧改動行數 > 門檻(預設 300)→ 該棧**全部題目一律適用**(`triggered_by=["行數>門檻"]`),所以大改動時每支 .kt/.swift/.dart 檔都會被視為「命中」。
- 逐檔比對的先例只有 `_tension_candidates_into`(逐檔 `_stack_key_for_file` + 逐檔 `_STACK_TRIGGERS` 比 added_lines),可仿寫,但不是現成「一支檔是不是畫面檔」的函式。
- 這些觸發字也不專屬畫面:dart-build 的 `ChangeNotifier/notifyListeners/ValueNotifier/context.read`、swift 的 `ForEach/List/.animation(`、kt-compose 的 `remember` 都可能出現在 view-model/狀態類別;反過來,只改文案或樣式的畫面檔(沒動這些字)不命中。且 `_STACK_PERF_QUESTIONS` 只有 "kt" 鍵,`.kts` 不在內。

判定:**不符**。既有規則是「對某棧全體改動行、逐題」的適用性判斷,不是「對單一檔判是否畫面檔」;拿來做 S3 需要新寫逐檔函式,且在行數>門檻時會全數誤判為畫面。「命中畫面觸發規則」與「不命中不判前端」的語意,會漏判純文案/樣式畫面檔、誤判含狀態類別的非畫面檔。

### ④-5 推送前的風險分級輸出能不能多印一行而不改變分級

計劃原句:「推送前的風險分級輸出多印一行『前端 N 檔、後端 M 檔』。不做閘。」;S6「輸出應多一行…且這行不改變分級結果」。

程式實際行為:
- file: `scripts/lumos` 函式 `_pitfall_tier(claims, files, repo_root, diff_range)`:分級只由 claims(命中風險型樣)與 files(是否含程式檔)算出,回 (tier, 一句為什麼);與輸出文字無關。
- file: `scripts/lumos` 函式 `cmd_pitfalls`:人可讀輸出在 `print(f"tier: {data['tier']}" …)` 之後印測試範圍與 impact 提示;pre-push 走 `--json`(`cmd_pitfalls` 註解:「混進 JSON 會讓解析端壞掉」),我在 scripts 與 hooks 底下沒找到解析人可讀 `tier:` 行的程式。

判定:**符合**(多印一行純屬輸出層,不影響 `_pitfall_tier`;建議只印在人可讀分支,若也放 JSON 要確認消費者容忍新鍵)。

### ④-6 `.lumos/config.json` 宣告路徑對照:現有路徑樣式比對函式

計劃原句:「專案可以在 `.lumos/config.json` 宣告路徑對照(形狀借 Copilot 的 applyTo:路徑樣式 → 角色),宣告的優先」;回退節「`.lumos/config.json` 讀路徑對照的那段」。

程式實際行為:
- config 沒有共用讀取器:各區塊自寫讀取(`_stack_questions_config`、`_nodehome_config`、`_cochange` 設定、`load_test_profile` 等,均直讀 `<repo>/.lumos/config.json`,壞值用預設並回 warnings)。
- glob 比對現成:file: `scripts/lumos` 函式 `_cochange_excluded(path, patterns)`(fnmatch 加去掉開頭 `**/` 再試一次;`node_home.ignore` 與 cochange.exclude 都用它),另 `_is_code_file` 等直接用 `fnmatch`;`_match_incident_triggers` 有 `glob:<pattern>` 用 fnmatch/PurePath.match。fnmatch 的 `*` 可跨 `/`,只有開頭 `**/` 有特別處理,中段 `**` 無特殊語意。
- 沒有「路徑樣式 → 角色」的多值對照讀取、也沒有「多條命中誰優先」的先例。

判定:**部分符合**。glob 比對有現成(`_cochange_excluded`,但名字與語意是排除清單);config 讀取要新寫一段(照 `_stack_questions_config` 形狀);多條樣式衝突時的優先序計劃沒定。

### ④-7 派工範本第 3 節現在的點數與編號

計劃原句:「派工範本第 3 節第 ④ 點『本案特定鏡頭』是空白欄」;「兩張角色鏡頭卡,寫進派工範本第 3 節,當第 ⑤ 點」;「後端卡:不重複第 ① 點已有的」。

程式實際行為:
- file: `skills/lumos-design-loop/templates.md` 「## 3. Code-loop reviewer」派工詞的「審查鏡頭:」共 4 點,阿拉伯數字:`1. 正確性`、`2. pitfalls manifest`、`3. 圖譜鏡頭`、`4. {本案特定鏡頭：如 migration SQL 正確性…}`(空白欄,屬實)。正確性鏡頭的例子有連線/鎖/交易、對外送出或扣款重試、寫一半、時區(屬實,偏後端)。
- 同一節前面「§3 編排者派工前須知(不貼進派工詞)」另有圈圈 ①–④ 四點(④=Codex 當編排者)。計劃的「第 ④ 點=本案特定鏡頭」用的是圈圈字但指阿拉伯編號的點。
- 另:計劃「現況」說「把慣例 skill 抄進架構對齊席的派工詞…只寫在文件」——範本 7.6 確有 `{kotlin-idioms / … 依副檔名;.ts/.js 看 package.json 分前後端}` 佔位,但 `cmd_pitfalls` 也會印出 `慣例 skill:…(審查員派工時一併附上)`,不是純文件。

判定:**部分符合**。現況是 1–4(不是 ①–④),加「第 ⑤ 點」在點數上成立;但編號記法會與同節的圈圈須知混淆;且「加在 4 之後」意味著第 4 點是編排者要填的空白,卡放第 5 點是固定內容,順序上合理。

## 摘要

- ④ 共 7 條:符合 2(④-2、④-5)、部分符合 4(④-1、④-3、④-6、④-7)、不符 1(④-4)。「不符/部分符合」合計 5 條。
- 最重要:S3 的手機畫面判定拿既有觸發規則當現成機制是錯的(逐棧行聚合、行數>300 全開、非專屬畫面),需新寫逐檔函式並重訂語意;超時時角色卡會連同節點一起消失(hook 只附超時句)。
