severity: major

邊界可執行鏡頭。程式現況我實際查過:`_node_flavor_of`、`_RAN_EVIDENCE`、`_stack_applicability`、`_review_role_for`、`_tension_candidates_into`、`_init_config_skeleton`、`_lintcheck_validate`。前掃已修的不重報。

## 逐條 finding

### F1 B10 伺服端訊號 `io.ktor` 會把 Android 模組判成伺服端
- 位置:〈做法〉B10「判伺服端的訊號」
- 問題:規則寫成「建置檔寫了 `com.android.application`/`com.android.library` → Android;寫了 `org.springframework.boot` 或 `io.ktor` → 伺服端」。`io.ktor` 是子字串比對,沒限定在 plugins 區塊。Android 與 KMP 模組常見的依賴是 `implementation("io.ktor:ktor-client-okhttp:2.3.0")`,字串裡也有 `io.ktor`。現代 Android 專案的外掛多半寫 `alias(libs.plugins.android.application)`(版本目錄形式),檔裡沒有 `com.android.application` 這串字,「先判 Android」的優先序救不了它。
- 具例:`app/build.gradle.kts` 內容為 `plugins { alias(libs.plugins.android.application) }` 加 `dependencies { implementation("io.ktor:ktor-client-okhttp:2.3.0") }`,檔案 `app/src/main/.../Home.kt` 沒有 `import android.`(純 ViewModel)。照 spec:判伺服端 → kt-compose、kt-leaks、kt-startup 全部不列、角色判後端。實際是 Android,表態閘少問三題,這正是計劃〈實務隱患〉②自己說要防的「判錯平台讓 Android 專案漏問」。S24、S25 都沒涵蓋這個輸入。
- 照字面能不能寫成測試:能,而且該寫。現在的條款只測得到「建置檔有 `org.springframework.boot`」。
- 佐證:`file: scripts/lumos:26300` 一帶的骨架與 `_ROLE_UI_IMPORT` 都沒有建置檔解析可借,這支是全新字串比對。
引句:「寫了 `org.springframework.boot` 或 `io.ktor` → 伺服端」
severity: major
blocking: 是 — 照字面實作會讓版本目錄寫法加 ktor 客戶端的 Android 專案被判伺服端,守衛放寬、漏問題目。

### F2 B10「三條路都不列」漏了 pitfalls --diff 的舊語意整組清單
- 位置:〈做法〉B10「接線」
- 問題:spec 只改 `_stack_applicability`(加排除集合參數)和改檔前推播的整組清單。pitfalls --diff 另有一條平行路徑:`stack_qs[sk] = _STACK_PERF_QUESTIONS[sk]`,不經 `_stack_applicability`。它輸出在 JSON 的 `stack_questions` 欄,也進人讀輸出。這裡仍整組含 Android 三題。
- 具例:只改 Spring 的 `.kt` 檔 → `stack_questions_applicable` 沒有 Android 題,但 `stack_questions.kt` 仍列出 Compose、洩漏、冷啟動三題給派工與人看。B10 的目的是「Spring 專案不再看到」,這個欄位沒收到。S22–S27 只釘 applicable/meta 與改檔前推播,pitfalls 的 `stack_questions` 欄沒有條款。
- 佐證:`file: scripts/lumos:47270-47276`(`stack_qs`)與 `file: scripts/lumos:47315`、`file: scripts/lumos:47383`(輸出欄)。
引句:「pitfalls --diff 由改動檔的判定結果算出集合傳進去」
severity: major
blocking: 是 — 照字面只改 `_stack_applicability`,pitfalls 輸出的整組欄位仍列 Android 題,又缺條款釘它,實作者會以為做完了。

### F3 B10 沒處理 `_tension_candidates_into`,候選會指向被排除的題
- 位置:〈做法〉B10「接線」「表態閘讀的題表跟著少這三題,不用另外改」
- 問題:`_tension_candidates_into` 直接走 `_STACK_TRIGGERS[sk]` 全部題目,不經 `_stack_applicability`。它的 docstring 寫「候選的題必在 stack_questions_applicable」,排除之後不成立。
- 具例:伺服端 `.kt` 新增一行 `val view = ...`,對照檔都沒有 → 產出 `kt-leaks` 的「可能撞」候選。pitfalls 人讀輸出會印出,但 kt-leaks 已不在表態表裡,沒人能表態它。
- 佐證:`file: scripts/lumos:46612-46636`(迴圈沒有排除參數)、`file: scripts/lumos:47428`(照印候選)。
引句:「表態閘讀的題表跟著少這三題,不用另外改」
severity: minor
blocking: 否 — 只多出一條無處可答的提示,不影響擋與放。

### F4 B10 角色判定要讀建置檔,spec 沒說讀哪個版本、算不算進讀檔上限
- 位置:〈做法〉B10「判伺服端的訊號」「角色」
- 問題:`.kt` 的角色判定現在走「批次讀 git 某版本的檔內容」(`_review_role_changed_files` 的 want 清單,`_ROLE_READ_CAP=300`,另有時間預算)。這份清單目前只列 `.kt` 檔本身,以及 `.ts/.js` 的 package.json 候選。`.kt` 的建置檔候選(`build.gradle(.kts)`、`pom.xml` 往上每一層)沒進清單。spec 說「跟 `_node_flavor` 同形狀、結果快取」,但快取鍵是工作樹路徑。
- 具例:審查範圍是 `base..head` 的某個舊版本,工作樹已 checkout 到別的內容。實作者照 spec 寫成讀工作樹,會拿到錯的建置檔。批次讀取表的 cap 與預算也沒算進建置檔的讀取。`t_review_role_file_cap_and_budget`、`t_review_role_skips_huge_blobs` 這組現有測試的語意會被這支改動碰到,spec 沒提。
- 佐證:`file: scripts/lumos:30420-30440`(want 清單只對 `_NODE_EXTS` 加 package.json 候選)。
引句:「新增一支跟 `_node_flavor` 同形狀的小函式,結果快取」
severity: minor
blocking: 否 — 多半在 HEAD 上跑,錯版本只在審舊範圍時出現,且判不出時照舊。

### F5 react 觸發字清單的跳脫混用,照抄會讓整支 lumos 載入即崩
- 位置:〈做法〉F2 + W2 七題的「觸發」
- 問題:同一份清單裡有的寫成 regex 原文(`\.then\(`、`\.map\(`、`import\(`、`\bawait\b`),有的沒跳脫(`fetch(`、`setInterval(`、`setTimeout(`、`subscribe(`)。`_STACK_TRIGGERS` 載入時就 `re.compile`,「壞 regex=啟動即錯」。
- 實測:`python3.14 -c "import re; re.compile('fetch(')"` 回 `missing ), unterminated subpattern`,`setInterval(`、`subscribe(` 同樣報錯。
- 另一處不可寫成測試:react-key 的 `when_raw` 寫「`Math\.random\(\)` 出現在 key 的寫法」,沒給具體 regex。S17 的命中樣本與不命中樣本沒辦法逐字釘。
- 補充:`key=\{\s*(?:i|idx|index)\s*\}` 沒有要看字串內容,放 `when_raw` 與前文「`when_raw` 只放要看字串才判得出的樣式」自相矛盾,但不影響行為。
引句:「觸發:`fetch(`、`axios`、`\bawait\b`、`\.then\(`、`AbortController`、`XMLHttpRequest`、`useSWR`、`useQuery`」
severity: minor
blocking: 否 — 載入即崩會被第一次跑測試抓到,但 `Math.random` 那條要實作者自己發明樣式。

### F6 「跑過的證據」新樣式沒說要加多行旗標,fix_hint 也沒分家
- 位置:〈做法〉F1「`_RAN_EVIDENCE`(統一一條樣式)」
- 問題:判定函式是 `re.search(spec["re"], 去色輸出)`,不帶任何旗標。spec 要的「行首(前面可有空白)的 `Tests`」需要 `(?m)^`。實作者若寫 `^\s*Tests` 卻沒加 `(?m)`,只比對整串開頭,vitest 摘要永遠對不到。S4 會翻紅,所以是擋得住的 minor。
- 另一處:`fix_hint` 現在寫「換了自訂 reporter…」,對 vitest 使用者(`--reporter=dot` 或 `json` 沒有 Tests 摘要行)沒指到 vitest 的做法。spec 沒說這句要不要改。
引句:「行首(前面可有空白,vitest 的摘要行是縮排的)的 `Tests` 後面可有可無冒號」
severity: minor
blocking: 否 — 測試先紅就會發現。

### F7 W7 init 的 eslint 提示在 lint.json 已存在時仍會印
- 位置:〈做法〉W7「init」、S11
- 問題:spec 寫「跑完設定骨架之後查同一張表,命中就印一行」,沒有「lint.json 已存在就不印」的條件。doctor 那邊明確寫了「`.lumos/lint.json` 不存在時」才查表。
- 具例:專案已接好 `.lumos/lint.json`,每次重跑 `lumos init` 仍印「要讓代碼審看得到它的告警,照 doctor 範本建」,是錯的催促。S11 只測有 eslint 設定且沒有 lint.json 的情況。
- 同段另一處:根目錄同時有 `eslint.config.js` 與 `.eslintrc.json` 時,印哪個檔名沒定義(S8、S9 各測單一檔)。
引句:「命中就印一行「看到 eslint 設定 `<檔名>`;要讓代碼審看得到它的告警」
severity: minor
blocking: 否 — 只是誤導提示,不改守衛。

### F8 前端優先序:svelte、angular、solid 與 react 並存時會判成 react
- 位置:〈做法〉F2 + W2「改 `_node_flavor_of`」
- 問題:規則是「有 vue/nuxt → vue;沒有但有 react/next/preact → react;只有 svelte/angular/solid → vue」。`@angular/core` 加 `react`(例如 Angular 專案為了 Storybook 或某元件庫宣告了 react),或 svelte 專案的 devDependencies 有 react,會判成 react,拿到 React 題組與 react-idioms,問偏。條款只有 S12–S14,沒有涵蓋混合依賴。〈不做〉聲明 Svelte/Angular 照舊歸 vue,混合輸入與它矛盾。
引句:「沒有 vue/nuxt、但有 react、next、preact 任一 → `react`」
severity: minor
blocking: 否 — 少見混合,且方向是「問偏」不是「漏擋」。

### F9 S29 無法在 CI 重現,也不是機械可查
- 位置:S29
- 問題:`[manual:]` 要在 `/Users/enzo/orca/workspaces/order-web` 裝好的 node_modules 上實跑 eslint。那是 repo 外的目錄,其他機器與 CI 沒有。可以機械化的那一半沒做:react-idioms 機檢欄寫到的規則代號,是否只出現在一份固定名單(`rules-of-hooks`、`exhaustive-deps`,加標「未實跑」的 `jsx-key`、`no-array-index-key`)裡。現在改規則代號不會有任何東西紅。
引句:「每條機檢欄的 eslint 規則代號應在 order-web 已裝的 eslint 與 eslint-plugin-react-hooks 上實跑核對過」
severity: minor
blocking: 否 — 是一次性實作期核對,但「未實跑」標記沒有機械守衛。

## 風險類(逐類)
- 守衛面:會碰。F1 讓 Android 漏問(放寬),F2 與 F3 是 B10 沒收乾淨。跑過證據樣式放寬那段,我讀得到的邊界(jest 的 `✓ 測試名` 列不在行首、`Test Files` 不是 `Tests`)沒找到假綠輸入,已讀,無 finding。
- 舊資料與舊帳相容:已讀,無 finding。排除參數預設空,既有 `_stack_applicability` 測試呼叫不變。現有 `t_review_role_fallback_by_stack_key` 用 `{"react": "18"}` 期待前端,新規則下仍判前端。
- 在途分支:已讀,無 finding。〈實務隱患〉③已承認 vue 題換 react 題要重新表態,order-web 是唯一受影響專案。
- 跟其他計劃的交界:已讀,無 finding。vitest 吸收《逾期回頭條件立案清單》第 10 節兩邊都寫明。

## 已讀無 finding 的節
〈現況〉、〈八格盤點〉、符號 profile 收 `.jsx`(`_stack_ext_counts` 已計入 `.jsx`,反查路徑成立)、F7 前端範本、〈回退〉、〈不做〉。

最嚴重 severity:major;blocking 共 2 條(F1、F2)。
