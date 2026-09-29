severity: major

審查範圍:逐節讀完整份 spec(frontmatter、現況、要做什麼 1-5、已裁、已知限制、驗收 S1-S9、回退、實務隱患、撤除條件、不做)。交叉引用 [[Projects/代碼審資料狀態鏡頭_計劃]]、[[Projects/派工鏡頭注入_計劃]]、[[Projects/前端框架從vue分出_計劃]]、[[Systems/棧別提問表態閘]]、[[Systems/效能檢核目錄]]、lands_in 三篇(design-loop、pitfalls-code-loop、codex-harness)目標節點都存在。現況第 53、54、62 行的散文宣稱(_node_flavor 取最近 package.json、整個套件名相等、掛鉤有時間預算與快取、超時只附一行)經查與程式相符。派工範本第 4 點是空白欄,屬實。派工那一刻沒有附固定席節點,故不需逐條判固定席。

## F1 角色卡的「快速計算」沒有預算、沒有順序,掛鉤外層 60 秒被內層吃光時整個派工詞會被連帶殺掉
severity: major
blocking: 是
判準:照字面實作,實作者會把第二次子行程接在圖譜那次之後,超時路徑下掛鉤被外層 SIGKILL,連「已算好的圖譜段」和超時說明都一起丟,是壞系統。

- spec 段落:要做什麼第 3 點、實務隱患「派工附段有時間預算」。
- 引句:「角色卡另走一次快速計算,只看改動檔清單、檔案匯入與 package.json,不跟圖譜那段共用預算與快取」
- 引句:「角色卡的計算不得多開一次全圖掃描,只讀改動檔的匯入與 package.json;要跟圖譜那段分開算,才不會一起超時」
- 問題:輸入=大範圍改動(上千支檔,含數百支 .kt/.java/.swift/.dart 要讀匯入),圖譜那段走到超時。掛鉤現況是外層 60 秒、圖譜那次 subprocess 上限 `_run_tmo`=min(deadline+5, 0.9×60)=47 秒;超時分支立刻 `_emit_updated` 再 return。spec 要求「超時時角色卡照附」,就必須在超時分支之後(或之前)再跑一次角色計算並把兩段合成一個 updatedInput(現況每條路徑只 print 一次 JSON)。spec 沒給角色計算的逾時秒數、沒說先算還是後算、沒說要不要扣「內層預算是還剩多少、不是每段配額」那條(掛鉤檔頭註解寫得很清楚,且這個專案就是為這個病修過)。角色計算若含每檔一次 `git show`(`_lens_git` 單次逾時 20 秒),1000 檔不封頂,47+X 秒超過 60 秒,整支 hook 被砍,派工詞什麼都沒附,連超時句都沒有。
- 同一段的另一洞:spec 只講「超時或算出空白」,沒講圖譜那段回 rc 2/3/4(範圍不合法、無 docs/*-knowledge、base 不在主線)時角色卡附不附。掛鉤現況 rc!=0 直接 return 0、什麼都不附;若角色卡照 S5 字面只掛在「超時/空白」兩個分支,rc 3/4 時角色卡不附,而消費專案無圖譜正是 rc 3。
- 佐證:
  - file: `scripts/hooks/claude/dispatch-lens-hook.py:300-330` 超時分支只 `_emit_updated` 一次即 return,`_run_tmo`、`_dl` 夾在 0.9×外層。
  - file: `scripts/hooks/claude/dispatch-lens-hook.py:351-353` `r.returncode != 0` 直接放行不附。
  - file: `scripts/merge-claude-settings.py:72` dispatch-lens-hook.py 外層 60 秒。
  - file: `scripts/lumos:31329-31341` rc 4(base 不在主線)、rc 3(base 樹無圖譜)、rc 2 都在算任何東西之前就回。
  - file: `scripts/lumos:30426-30437` `_lens_git` 每次呼叫逾時 20 秒,無總量上限。
- 需補:角色計算的總秒數上限與先後順序(建議在圖譜 subprocess 之前算、用同一份 `_inner_budget`)、檔案數上限(超過就只算前 N 支或整段判不出並印一句)、圖譜段 rc≠0 時角色卡的去留。

## F2 角色判定讀哪棵樹沒講:工作樹、base、head 三種讀法在派工那一刻結果不同
severity: major
blocking: 是
判準:實作者會直接抄 `_node_flavor`(只讀工作樹磁碟),而派工掛鉤的既有紀律是「只讀 base/head 的 git 物件、不信工作樹」,兩者衝突時實作者會做錯決定,且不出錯訊息、只是靜默不附卡。

- spec 段落:要做什麼第 1 點(b)(d)。
- 引句:「不看改動行、不受改動行數門檻影響;刪掉的檔看改動前的版本。」
- 引句:「照既有 package.json 判定,前端框架 → 前端、Node → 後端、找不到 → 判不出。」
- 問題:輸入=代碼審派工範圍 `base..head`,head 是另一條分支上的提交、目前工作樹停在 main(派工鏡頭本來就支援,cmd_dispatch_lens 全程用 `git show <sha>:path`、`ls-tree base_sha`,刻意不讀工作樹)。新增的 `Foo.kt` 在工作樹不存在 → 讀匯入失敗 → 判不出 → 不附卡,而使用者以為有附。同理:
  - 新增一整個 `web/` 套件連同它的 package.json(base 沒有、head 才有):用 base 讀是「找不到」,用工作樹讀也是找不到。
  - 已刪的 `web/src/gone.ts`:`_node_flavor` 對不存在的檔照樣往上找父目錄,實測 `_node_flavor("src/gone/deleted.ts", ...)` 會回 node/vue 而不是判不出;但 package.json 若也在同一範圍被刪,工作樹已無,回 None。spec 只規定「刪掉的檔看改動前的版本」,只講到手機匯入,沒講 package.json 也要跟著看改動前。
  - 改名(`git diff --name-only` 預設偵測改名、只列新名):後端目錄搬進前端目錄,舊路徑不出現,沒定義用哪個路徑判。
- Codex 那條:armed 的 meta 是 arm 那一刻存好的文字,claim 只吐字串;spec 說「領取」時附角色卡,沒說是 arm 時算好塞進 meta.text 還是 claim 時算(claim 那時沒有檔案清單、只有 range)。
- 佐證:
  - file: `scripts/lumos:20448-20486` `_node_flavor` 用 `Path(repo_root)/file_rel` 從磁碟讀,不接受 git 樹。
  - file: `scripts/lumos:31353-31366` dispatch-lens 用 `ls-tree -r base_sha` 與 `git show base_sha:rel` 讀圖譜,註明「圖譜根從 base 樹解析(工作樹版…分支加一個空目錄就能熄燈)」。
  - file: `scripts/lumos:31045-31097` claim 只讀 meta.json 的 range 與 text,不算任何檔案清單。
  - file: `scripts/lumos:30199` 檔案清單用 `git diff --name-only`(未加 `--no-renames`)。
- 需補:明訂「檔案內容與 package.json 一律讀 head 的 git 物件(刪除/被刪的 package.json 讀 base)」或明訂「讀工作樹、且範圍終點不等於工作樹時降級成什麼」,並寫進 S3 的測資;Codex 路徑寫明 arm 時算。

## F3 專案宣告(`.lumos/config.json`)的鍵名、角色值、壞值處理、比對語意全沒定義,S1 無法寫成測試
severity: major
blocking: 是
判準:S1 的測試名綁在這份宣告上,鍵名與角色值不定義,實作者必須自己發明 schema,兩個實作者會做出不相容的設定檔。

- spec 段落:要做什麼第 1 點(a)、S1、回退。
- 引句:「專案宣告:`.lumos/config.json` 裡一份有序清單」
- 引句:「樣式比對沿用專案既有的路徑樣式比對寫法(開頭 `**/` 的處理跟既有排除清單一致)」
- 問題:
  1. 頂層鍵叫什麼沒寫(回退節說「設定檔裡那一鍵」),角色值寫中文「前端/後端」還是 fe/be 也沒寫。
  2. 壞輸入全無規定:清單不是陣列、某條缺角色、角色值拼錯、樣式不是字串、設定檔 JSON 壞掉、`.lumos` 是捷徑檔。既有兩個讀取器(`_stack_questions_config`、`_nodehome_config`)都有「壞值退預設+留一句警告」與「捷徑檔不跟過去讀」的慣例,spec 沒說沿用,實作者照字面會走出丟例外或靜默吞掉。
  3. 比對語意:既有 `_cochange_excluded` 回布林,不回「第幾條命中」,「第一條命中算數」要新寫一個回索引的函式,不是「沿用」。實測 fnmatch 下 `web/*` 命中 `web/src/a.ts`(`*` 會跨斜線),`./web/a.ts` 與前導 `/`、反斜線寫法永遠不命中且無任何警告,「路徑樣式寫錯」會讓整份宣告靜默失效,而已知限制節把宣告當成空殼 package.json 的唯一出路。
  4. 讀哪個版本的設定檔(工作樹或範圍終點)沒寫;`_nodehome_config` 明確處理過「工作目錄裡沒暫存的關掉不得關掉索引的檢查」這型問題。
- 佐證:
  - file: `scripts/lumos:26394-26403` `_cochange_excluded` 回 True/False 且 `**/` 只在樣式開頭剝一次。
  - file: `scripts/lumos:20505-20536` `_stack_questions_config` 壞值→預設+warnings。
  - file: `scripts/lumos:22542-22572` `_nodehome_config` 對捷徑檔與讀不了的處理。
  - 實測(在本審稿的暫存目錄,fnmatch 直呼):`_cochange_excluded("web/src/a.ts", ["web/*"])` 回 True;`_cochange_excluded("./web/a.ts", ["web/*"])` 回 False。
- 需補:鍵名、角色值、壞值一律「退回不宣告+印一句」、比對函式(回第一個命中索引)、讀哪個版本;S1 加一條壞宣告的案例。

## F4 壞掉或帶 BOM 的 package.json 被判成「後端」,不是「判不出」,前端專案會被附後端卡
severity: minor
blocking: 否
判準:結果是附錯卡(而 spec 自己說「寧可不附也不附錯」),但只影響審查員看哪裡、不擋推送,實作者不會因此做出壞系統。

- spec 段落:要做什麼第 1 點(d)、S2。
- 引句:「照既有 package.json 判定,前端框架 → 前端、Node → 後端、找不到 → 判不出。」
- 問題:輸入=前端專案的 package.json 帶 UTF-8 BOM(Windows 編輯器常見)或有多餘逗號。`_node_flavor` 用 `read_text(encoding="utf-8")` 再 `json.loads`,BOM 會丟 JSONDecodeError,被 `except` 吞成 `data = {}`,deps 為空,結果回 "node"。實測:`{"dependencies":{"vue":"3"}}` 加 BOM 的 package.json 底下的 `src/a.ts`,`_node_flavor` 回 `node`。S2 只驗「有 package.json 沒前端框架 → 後端」,把這個錯誤行為當成規格編進測試。
- 佐證:
  - file: `scripts/lumos:20462-20467` 解析失敗 `data = {}` 後仍走到 `fl = ... else "node"`。
  - 實測:見上,暫存目錄建 BOM package.json 後呼叫 `_node_flavor("src/a.ts","nf")` 輸出 `node`。
- 需補:S2 加一條「package.json 讀不了或解析失敗 → 判不出」,實作時不要直接複用 `_node_flavor` 的 node 分支,或先改它用 `utf-8-sig`。

## F5 「這次改動含哪些檔」的母體沒定義,兩個消費者會算出不同的檔集合;附卡門檻是 1 支檔
severity: minor
blocking: 否
判準:不會做出壞系統,但 S4 與 S8 的「前端 N 支」會各算各的,審查員被單一 .css 或 vendored 的 .py 帶偏。

- spec 段落:要做什麼第 3、4 點、實務隱患「注意力稀釋」。
- 引句:「全端改動兩張都附;全部判不出一張都不附。」
- 引句:「所以只附改動真的碰到的那張卡,判不出就不附」
- 問題:
  1. 派工通道的檔集合來自 `impact --diff` 的種子(`_impact_diff_seed_ok`:只剔 docs/、.md、.jsonl、governance 的 .json,測試檔、lock、圖片、無副檔名檔全在);推送前分級的檔集合來自 `added`/`changed_lines`(`_PITFALL_DIFF_SKIP_EXT` 先剔 .html、.svg、.json 等,再剔測試檔與 vendored)。S4 與 S8 引用同一個判定函式,卻餵不同母體:`.html` 在 (c) 判前端,但走推送前那條路根本不會被算到,兩處數字對不上。
  2. 門檻是 1 支:一次 400 支後端檔的改動夾一個 .css,依「全端兩張都附」就附前端卡;測試檔(`.spec.ts`、`tests/`)算不算、消費專案裡安裝進去且未改過的工具檔(`scripts/hooks/*.py` 會被判後端)算不算,都沒寫。消費專案的第一次提交或重跑安裝就會把這些 .py 帶進範圍,前端專案於是每次都被附後端卡;pitfalls 那條路有 `vend_skip` 專門處理過同一種事故(2026-09-10),派工路徑沒有。
  3. 二進位檔與無副檔名檔(圖片、`Makefile`、`scripts/lumos`)落在「判不出」沒問題,但 S8 的 K 會被它們墊高,行文沒說 K 是否含非程式檔。
- 佐證:
  - file: `scripts/lumos:30107-30116` `_impact_diff_seed_ok` 的剔除清單。
  - file: `scripts/lumos:20599-20602` `_PITFALL_DIFF_SKIP_EXT` 含 `.html`、`.svg`、`.json`。
  - file: `scripts/lumos:27030-27044` `_stack_changed_ok` 與 `vend_skip` 的存在理由(2026-09-10)。
  - file: `scripts/lumos:27253-27262` 推送前的棧別題只掃非測試檔。
- 需補:指定唯一的檔集合來源(建議一律「範圍內改動檔,剔測試、vendored、bookkeeping」),兩處共用;寫明門檻(至少 1 支還是達某比例)。

## F6 判定表的盲點:全端框架單一 package.json、Kotlin/Swift 後端、非 Android 的 Java 都會判錯邊
severity: minor
blocking: 否
判準:已知限制節只講了「空殼 package.json」,其餘這幾類是同一機制的常見輸入,實作者照表做會附錯卡;有宣告可補救所以不阻擋。

- spec 段落:要做什麼第 1 點(b)(c)(d)、已知限制。
- 引句:「.cs/.java/.py/.sql → 後端(.java 已先過 b)。」
- 問題:
  1. Next.js/Nuxt 這類全端單一套件:`_node_flavor` 的前端標記含 `next`、`nuxt`,整個套件的 `app/api/**/route.ts`、server action、DB 存取層全被判前端,後端卡(端點授權、分頁、外呼逾時)永遠附不到最需要它的檔上。已知限制只列空殼一種,這一種才是常見輸入。
  2. 對稱性斷裂:.java 不匯入 android → 後端(Android 的純資料類、工具類 Java 會被附「API 對外相容、端點授權」),而 Kotlin/Swift/Dart 後端(Ktor、Spring Boot Kotlin、Vapor、Dart server)無匯入 → 判不出。同一個「沒匯入畫面框架」在 .java 是後端、在 .kt 是判不出,S3 把這條寫進測試。
  3. `.tsx/.jsx` 在 (c) 直接判前端,先於 (d);後端套件裡的 email 樣板 .tsx 也被判前端。
- 佐證:
  - file: `scripts/lumos:20443` `_NODE_FRONTEND_MARKERS` 含 next、nuxt、react、preact、svelte、@angular/core、solid-js。
  - file: `scripts/lumos:20488-20502` `_stack_key_for_file` 對 .ts/.js 只有 node/vue/None 三種結果,沒有「這個目錄是伺服端」的概念。
- 需補:已知限制節補上全端框架與 Java/Kotlin 不對稱兩條;或 S3 把「.java 不匯入 android」也判不出,與 .kt 對稱。

## F7 派工詞沒有標記行時角色卡整個不出現,但範本第 5 點寫成「自動附上」
severity: minor
blocking: 否
判準:實作者不會做壞系統,但審查員與編排者會誤以為每次代碼審都有卡。

- spec 段落:要做什麼第 2、3 點、實務隱患。
- 引句:「角色鏡頭卡由派工時自動附上,對上卡片題的發現在標題附題號」
- 引句:「代碼審的兩條派工通道(Claude 派工詞有圖譜鏡頭那行、Codex 派子代理那一刻領取)都附;設計審那條不附。」
- 問題:輸入=編排者派代碼審席但派工詞沒有 `LUMOS-IMPACT:` 那行(範本第 3 點是「可省」的鏡頭欄位、light 單席通才也常省)。掛鉤 `find_marker` 找不到就 return 0,角色卡不附;Codex 路徑沒 `--arm` 也是 `not-armed`。範本第 5 點卻寫成無條件「自動附上」,審查員讀了會期待有卡。另外同一派工被重送(編排者重派同一份詞)在 Claude 路徑是重算重附、無副作用;Codex 路徑重送會多領走一個 token,`exhausted` 時該席沒卡,spec 沒提。
- 佐證:
  - file: `scripts/hooks/claude/dispatch-lens-hook.py:106-119` `find_marker` 逐行比對,無標記回 None,main 直接 return 0。
  - file: `scripts/lumos:31066-31083` claim 逐一 rename token,用完回 `exhausted`。
  - file: `skills/lumos-design-loop/templates.md:145-153` 第 3 點的標記行是範本內容,不是強制。
- 需補:範本第 5 點寫成「派工詞有 LUMOS-IMPACT 行、且改動含前端/後端檔時才附」,與 S4 的前提一致。

## 各節已讀,無 finding
- frontmatter、decisions d1-d3、現況、已裁、撤除條件、不做:已讀,無 finding。
- 回退節:已讀,無 finding(掛鉤檔改回要重核可指紋已寫明;`.lumos/config.json` 變死鍵屬實不影響其他功能)。

## 實務隱患逐類
- 併發:Claude 路徑每次派工獨立子行程,無共享寫入;Codex claim 用原子 rename,重送多耗 token 見 F7。角色卡不進快取所以無快取競態,但也因此每席重算一次,見 F1 的預算。
- 效能:F1(無預算、無檔案數上限、每檔一次 git show)。
- 回滾路徑:回退節完整;唯一缺口是掛鉤檔改動要重核可指紋(spec 已寫)。
- 消費專案(被 vendored 的 lumos)拿不拿得到:卡片單源在 lumos 本體,消費專案跟著裝;風險在 vendored 工具檔被算進後端(F5)與無圖譜專案的 rc 3(F1)。
- 金流、對外送出、不可逆:同意 spec 的「已排除」理由(純文字與判定函式)。
- 守衛面:同意標命中;S7 與資料狀態鏡頭同形狀,無新增疑慮。

最嚴重 severity 是 major,blocking 共 3 條(F1、F2、F3)。
