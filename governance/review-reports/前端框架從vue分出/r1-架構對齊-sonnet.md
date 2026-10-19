severity: minor

整體判斷:這份計劃大多沿用既有的機制,沒有自創第二套判棧、第二套解析器或第二套設定讀法。我找到 9 條小的不對齊,都是 minor,沒有 major。每條 finding 的引句都已用 grep 逐字比對過凍結審材 r1-snapshot.md,都找得到。

## 1. 分層與依賴方向

對得上的地方:
- 判前端值的唯一源頭仍是 `_node_flavor_of`,下游全跟著走。這跟 `_stack_key_for_file` 在 `scripts/lumos:30232` 的做法一樣。
- 新增題組的位置、題目表形狀、`react-extcode` 的附加方式都照 `_STACK_QUESTION_SPECS`、`_EXTCODE_STACKS` 走。
- `node-vitest` 在 `_RAN_EVIDENCE` 當別名,跟 `TEST_PROFILES["node-vitest"]` 的別名寫法一樣(`scripts/lumos:5877`)。
- 題組鍵加 `react` 後,角色判定可以仿 `_ROLE_BACK_KEYS` 的集合寫法。計劃沒寫這點,但不衝突。

不對齊:

severity: minor
blocking: 否
引句:「只看檔案頭的匯入與建置檔的外掛宣告,不猜程式內容。」
file: `scripts/lumos:30316`
file: `scripts/lumos:30413`
說明:判伺服端的訊號有兩條讀取路。
- 角色路是用 `reader` 讀基準版,內容靠批次讀取先挑好。`_review_role_wanted` 目前只認 package.json 候選和手機檔本身。
- pitfalls 路則讀工作樹。
- 計劃只說「跟 `_node_flavor` 同形狀、結果快取」,沒寫新函式要不要收 `reader`、建置檔要不要加進 `_review_role_wanted` 的批次讀取與 `_ROLE_READ_CAP`。
- 漏掉的話,角色路會繞過「只信起點版」的設計,把 Gradle 檔當工作樹直讀;或根本讀不到建置檔,B10 的角色判定落空。
- 建議計劃明寫這兩處接線。

## 2. 命名與錯誤處理

severity: minor
blocking: 否
引句:「這三題一律不列——觸發詞命中、行數超過門檻、改檔前推播印整組,三條路都不列」
file: `scripts/lumos:30004`
file: `scripts/lumos:30158`
說明:
- 題目旗標的既有形狀是布林(`shape_only`、`needs_backing`,角色卡還有 `web_only`)。計劃的 `"platform": "android"` 是字串值,在這張表裡是新形狀。
- 排除要在三個地方落實:`_stack_applicability` 的參數、`stack_qs` 整組(`scripts/lumos:47276`)、impact 整組(`scripts/lumos:50089`)。`_STACK_PERF_QUESTIONS` 只存題目原文、沒有 id,要濾掉三題就得另外對回 spec。
- 建議改成 `android_only: True` 這類布林,並用一支共用的「某棧濾掉某平台題」小函式,不要在三處各濾一次。

severity: minor
blocking: 否
引句:「跑完設定骨架之後查同一張表,命中就印一行」
file: `scripts/lumos:26040`
說明:
- init 的輸出慣例是帶前綴的單行(`  ✓ …` 完成、`  ⚠ …` 提醒)。
- 計劃要印的那行把「發生什麼、為何在意、指令」擠在同一句,指令沒有獨立一行。
- doctor [F] 用的 `warn(lines, head, advice)` 已是分段形狀(`scripts/lumos:3789`),可照它的段落排。
- 建議 init 那行用 `⚠` 前綴,指令另起一行。

severity: minor
blocking: 否
引句:「node → node-idioms、react → react-idioms、其他或找不到 package.json → vue-idioms」
file: `scripts/lumos:46124`
file: `scripts/lumos:46129`
說明:
- 既有的 `_ARCH_IDIOM_SKILL` 是「副檔名或棧鍵 → skill」的表,鍵就是 `vue`、`py` 這類棧鍵,跟 `_stack_key_for_file` 的回傳值同一套。
- 計劃另造一張「前端值 → skill」的小表,等於同樣的對應寫了兩張。
- 建議 .ts/.js 家族改成用 `_stack_key_for_file` 的結果去查 `_ARCH_IDIOM_SKILL`,表裡補 `node`、`react` 兩列即可。

## 3. 第二種做法

沒有 major。有兩處重複,都是已有共用寫法的同功能:

severity: minor
blocking: 否
引句:「或根 package.json 的 dependencies/devDependencies 有」
file: `scripts/lumos:30198`
file: `scripts/lumos:30171`
說明:
- 「這個 repo 用不用 vitest」要再讀一次 package.json 並收集依賴鍵。
- 既有的 `_node_pkg_text`(讀一次就快取)和 `_node_flavor_of`(收 dependencies、devDependencies、peerDependencies)已經做了同件事。
- 計劃只收兩類依賴,跟既有的三類不一致。
- 建議把「收依賴鍵」抽成共用小函式,兩邊都呼叫它。

severity: minor
blocking: 否
引句:「只看 repo 根。表的每一列附一份」
file: `scripts/lumos:31526`
說明:
- 新增 `_LINTER_CONFIG_MARKERS` 列 eslint 設定檔名。
- 既有的 `_LINT_CONFIG_GLOBS` 已經列了 `*.config.js/mjs/cjs/ts` 和 `.eslintrc*`。兩份名單已經不一樣:計劃列了 mts/cts,既有的沒列。
- 用途不同(偵測 vs 搬設定檔),所以我不算 major。
- 建議計劃寫明兩份的關係:共用同一個常數,或互相註明、補進同步守衛。

## 4. 落點

severity: minor
blocking: 否
引句:「各寫自己那段)+本篇+驗證紀錄+react-idioms+範本與使用說明」
說明:
- frontmatter 的 `lands_in` 列了 9 篇,commit ① 點名 6 篇家節點、commit ② 點名 2 篇目錄,`Systems/pitfalls-code-loop` 沒有對到任何一段。
- 角色鏡頭(`_review_role_for` 與 B10 的角色改動)有寫在 pitfalls-code-loop 裡(該篇有 7 處提到「角色」)。
- 要嘛把它補進 commit ① 的清單,要嘛從 `lands_in` 拿掉並說明角色改動寫進哪一篇。

severity: minor
blocking: 否
引句:「②只有兩份目錄筆記([[Systems/效能檢核目錄]]、[[Systems/linter精選目錄]] 的 React 段)」
file: `docs/lumos-toolchain-knowledge/Systems/補新語言SOP.md:122`
file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md`
說明:
- 這個拆法照 SOP 第 10 步,對齊。
- 但 SOP 的理由是「兩份目錄不是主程式的家」,這句已經不全對:效能檢核目錄的 `about_code` 列了 `scripts/lumos`。
- 同一個提交裡還塞了與前端無關的 Kotlin 伺服端判定(B10)、init 的 vitest 骨架、doctor 的 eslint 偵測。專案規矩是「一個功能一個提交」。
- 建議計劃註明這個取捨,或把 B10 另拆一個提交。
- 另外 `skills/react-idioms` 與前端範本檔沒有指定家,但既有 vue-idioms、DDD 範本也沒有,這點算對齊。

severity: minor
blocking: 否
引句:「①互不依賴的等待要並行(同 vue R1)」
file: `scripts/lumos:30032`
file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:4`
說明:
- 目錄的規矩是「idioms 裡標『⚠ 不可機檢』的條目優先入問」。
- vue 有 `vue-parallel`,kt 的協程題也涵蓋同一件事。
- react-idioms 的 ① 是不可機檢的頭號條款,但六題 react 專屬題裡沒有對應的「並行等待」題。
- 這是題組內容的取捨,不是結構問題,所以只標 minor。若刻意不收,建議寫進決策 d1 的「不選」。

不對齊共 9 條,其中 major 0 條

⚠ 交編排者判斷:`.java` 用「沒有 android 匯入就判後端」(`scripts/lumos:30335`),`.kt` 則改看建置檔外掛宣告。計劃已用 d2 解釋 Kotlin 為何不能只看匯入,所以我沒計入。但兄弟語言對同一件事有兩套判法,值得確認是刻意的。
