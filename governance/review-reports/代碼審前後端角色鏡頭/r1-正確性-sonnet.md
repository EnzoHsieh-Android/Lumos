severity: major

審查鏡頭:正確性/邏輯。已讀全文各節(frontmatter、現況、要做什麼 1-5、已裁、已知限制、驗收條款 S1-S9、回退、實務隱患、撤除條件、不做)。
交叉引用核對:related 四篇([[Projects/代碼審資料狀態鏡頭_計劃]]、[[Projects/派工鏡頭注入_計劃]]、[[Systems/棧別提問表態閘]]、[[Systems/效能檢核目錄]])、正文提到的 [[Projects/前端框架從vue分出_計劃]]、lands_in 三篇(design-loop、pitfalls-code-loop、codex-harness)在 worktree 的 docs/lumos-toolchain-knowledge 下都存在;範本第 3 節存在,第 4 點確為空白欄、尚無第 5 點。無壞交叉引用。

## F1 手機端「匯入 android/androidx」判前端過寬,與「資料層判不出」的已知限制自相矛盾
severity: major
blocking: 是
判準:照字面實作會把 Room DAO、Repository 這類資料層檔判成前端並附無障礙/載入錯誤空卡,違反 spec 自己的「寧可不附也不附錯」,實作者無法從 spec 得知該照哪一句做。
spec 段落:「要做什麼」1(b)、S3、「已知限制」第二條。
引句:「.kt/.java 匯入 android 或 androidx、.swift 匯入 SwiftUI 或 UIKit、.dart 匯入 flutter 套件 → 前端」
引句:「不匯入畫面框架的手機端檔(例如純資料層)判不出、不附卡;這是刻意的,寧可不附也不附錯。」
問題:輸入=一支 Android 的 `UserDao.kt`(`import androidx.room.Dao`)或 `AuthRepository.kt`(`import android.content.Context`、`android.util.Log`)。走 1(b):匯入含 android/androidx → 前端 → 附前端卡(fe-x 載入/錯誤/空、無障礙、卸載後更新)。這正是「已知限制」聲稱會判不出的純資料層檔。androidx 涵蓋 room、work、datastore、lifecycle、security-crypto,android.* 涵蓋 Context/Log/Build,大部分非畫面檔都會 import 其中之一。Flutter 的 `package:flutter/foundation.dart`(純邏輯常用)、Swift 的 UIKit(UIImage 處理類)同理。S3 的測試只驗「有這些匯入→前端」與「沒這些匯入→判不出」,兩端都過,抓不到這個中間地帶。
佐證:
file: `scripts/lumos:20285` `_STACK_QUESTION_SPECS` 的 kt 題組 `kt-leaks` 的觸發詞本來就含 `\bContext\b`,說明 Context 在後端/資料層檔也常出現,既有專案並不把它當畫面訊號。

## F2 .java 與 .kt 規則不對稱:沒有 android 匯入的 Android Java 檔被判後端
severity: minor
blocking: 否
判準:不改,實作者會讓 Android 專案的純 Java 模型/工具類收到「每個端點授權、分頁」後端卡,但這是提示雜訊不是壞系統。
spec 段落:1(c)「.cs/.java/.py/.sql → 後端(.java 已先過 b)」、S3「.java 應判後端」。
引句:「同副檔名但沒這些匯入的 .kt/.swift/.dart 應判「判不出」、.java 應判後端」
問題:輸入=舊 Android 專案的 `Money.java`(POJO,無任何 import)。1(b) 沒命中 → 1(c) → 後端 → 附後端卡。同樣的 `Money.kt` 卻判不出。專案有 java-idioms 明講涵蓋「Android 舊碼」,所以這是既有目標客群。另 .cs 在 Unity/MAUI 專案同理判後端。
佐證:file: `scripts/lumos:26921` `_ARCH_IDIOM_SKILL` 把 java 對到 java-idioms,其 description 寫「JVM 後端服務、Android 舊碼、批次與排程程式」,即 .java 副檔名本身分不出前後端。

## F3 專案宣告的路徑樣式沿用 fnmatch,`dir/**/*.ts` 比不到 `dir/index.ts`;而這是已知限制唯一的出路
severity: minor
blocking: 否
判準:不改,宣告了 `frontend/**/*.ts` 的專案裡直接放在 frontend 底下的檔會靜默落回 package.json 判定,而空殼 package.json 情境下判成後端,正是宣告想修的那個錯。
spec 段落:1(a)、「已知限制」第一條。
引句:「樣式比對沿用專案既有的路徑樣式比對寫法(開頭 `**/` 的處理跟既有排除清單一致)」
問題:既有寫法是 stdlib fnmatch 加「開頭 `**/` 去掉再試一次」。實跑 `fnmatch("frontend/index.ts","frontend/**/*.ts")` 得 False,`fnmatch("frontend/a/index.ts","frontend/**/*.ts")` 得 True;同時 `apps/*/a.ts` 會比到 `apps/web/x/a.ts`(星號跨斜線)。spec 沒寫這兩個行為,也沒要求測試涵蓋(S1 只測兩條都命中取第一條)。
佐證:file: `scripts/lumos:26394` `_cochange_excluded` 只處理開頭 `**/`,docstring 自述是「雙試補 stdlib fnmatch 的坑」,中段 `**/` 沒補。

## F4 `.lumos/config.json` 宣告清單的鍵名、項目形狀、角色詞彙、錯誤處理全未定義,S1 無法寫成測試,且無法宣告「不附」
severity: major
blocking: 是
判準:實作者必須自己發明 schema(鍵名、是物件陣列還是二元組、角色值叫 frontend 還是 前端、壞值怎麼辦),兩個實作者會做出互不相容的設定格式,且消費專案一旦寫進設定就是對外合約。
spec 段落:1(a)、S1、「回退」。
引句:「`.lumos/config.json` 裡一份有序清單,每條是「路徑樣式 → 角色」(形狀借 Copilot 的 applyTo),第一條命中的算數」
問題:(1)沒有鍵名(回退段說「設定檔裡那一鍵」但從未給名字);(2)角色值只列「前端/後端/判不出」三詞,但清單能不能寫「判不出/略過」沒說——若不能,就無法把 `tools/`、`scripts/`、測試目錄這類 .py 排除出後端卡(見 F5),1(c) 副檔名一律判後端;(3)壞值處理未定:既有同類設定有「不合法→用預設並留一句警告」的慣例,spec 沒要求沿用;(4)整個清單非陣列、樣式為空字串或 `*` 全匹配時的行為未定。
佐證:file: `scripts/lumos:20505` `_stack_questions_config` 是既有慣例(讀 `.lumos/config.json`、值不合法用預設並回 warnings、鍵名與合法值集合寫成常數),本 spec 沒說是否同構。

## F5 「改動檔清單」的來源與排除規則未定,與既有 pitfalls/派工路徑的排除口徑衝突;刪檔那條在既有結構下走不到
severity: major
blocking: 是
判準:實作者不知道測試檔、vendored 檔、純刪除檔、改名檔算不算,S4/S8 的計數與「附哪張卡」會因來源不同而不同;照既有 `added` 結構做會讓 S3「刪除的檔看改動前版本」永遠不觸發。
spec 段落:「要做什麼」3、4、1(b)、S3、S8。
引句:「角色卡另走一次快速計算,只看改動檔清單、檔案匯入與 package.json」
引句:「不看改動行、不受改動行數門檻影響;刪掉的檔看改動前的版本。」
問題:
(a)清單來源沒定。既有 pitfalls `--diff` 走的是以「新增行」為鍵的 `added` 字典,純刪除檔不在其中(只有 `changed_lines` 記刪行);vendored 檔被 `vend_skip` 濾掉;測試檔被 `_PITFALL_DIFF_TEST_PAT` 濾掉;`.html/.json/.md` 等在 `_PITFALL_DIFF_SKIP_EXT`。spec 1(c) 卻把 `.html` 明列前端。若重用既有清單,`.html` 永遠進不來、刪檔永遠沒有,S3 的刪檔案例無從實作;若另寫清單,測試檔(如 `test_x.py` 判後端)與 vendored `node_modules`、產生檔會計入,一個只改測試的變更也會附後端卡,違反自己的注意力稀釋條款「只附改動真的碰到的那張卡」。
(b)判定時讀哪棵樹沒定。既有 `_node_flavor` 讀工作樹的 package.json;派工鏡頭整體刻意「只信 base 樹」(`--arm/--claim` 與 `_read_base`)。輸入=同一個 diff 同時新增前端套件的 package.json(含 react)與其底下的 .ts:讀工作樹判前端、讀 base 判不出;刪除的 .ts 其 package.json 也可能已被同 diff 刪掉。spec 只規範「刪掉的檔看改動前版本」,對 package.json 與 `.lumos/config.json` 讀哪個版本沒寫;若讀工作樹,被審的分支自己就能改 `.lumos/config.json` 決定自己收到哪張卡。
佐證:
file: `scripts/lumos:27234` `added.setdefault(cur_file, set()).add(new_ln)` 只在新增行收檔,`+++ /dev/null` 分支(同區 27238 起)只把刪行放進 `changed_lines`。
file: `scripts/lumos:20599` `_PITFALL_DIFF_SKIP_EXT` 含 `.html`。
file: `scripts/lumos:20632` `_PITFALL_DIFF_TEST_PAT` 排除測試檔。
file: `scripts/lumos:20448` `_node_flavor` 以 `Path(repo_root)/file_rel` 讀工作樹,不接受 rev 參數。

## F6 派工通道接線只涵蓋「超時」「算出空白」兩種情況,其他早退分支與 arm 失敗路徑仍會讓角色卡整個掉光
severity: major
blocking: 是
判準:不改,實作者會把角色卡掛在既有的 lens 成功路徑後面,結果 base 不在主線(rc 4)、無主線(rc 4)、無 docs/*-knowledge(rc 3)、回傳讀不懂等早退時角色卡消失,而 S5 的紅綠測試仍會全綠。
spec 段落:「要做什麼」3、S5、「回退」。
引句:「圖譜那段超時或算出空白時,角色卡照附。」
引句:「當圖譜那段超時或算出空白,派工附段應仍含角色卡」
問題:
(a)Claude 通道:hook 對 `dispatch-lens` 的處理是 rc==5 附超時說明、rc!=0 直接 `return 0` 放行、JSON 讀不懂放行、`text` 空放行。spec 只點名「超時」與「空白」兩個分支要補卡;rc 2/3/4(base 非主線、無圖譜、鏡頭擋下)的分支沒點名,因此「角色另走一次快速計算,不共用預算與快取」是否也在這些分支照附,實作者無從判斷。
(b)Codex 通道:`--arm` 是 `rc = cmd_dispatch_lens(...); if rc != 0: return rc`,鏡頭一擋下(非主線 base、無圖譜)就在寫 meta/tokens 之前整個離開——不只角色卡,連席位都不武裝。spec 說 Codex 通道「派子代理那一刻領取」,但領取只是 `rename` token 並回 arm 時存好的 `meta["text"]`,角色卡若要在領取時才算就違反現有「claim 只做原子領一席」設計;若在 arm 時算,就得在 rc!=0 路徑上也繼續武裝。spec 兩者都沒選。
(c)Hook 是薄殼、且受指紋保護,「另走一次快速計算」意味第二次 subprocess(或 lumos 端新旗標)。若做在 hook,消費專案全域已安裝的舊 hook 不會有這段,得重跑安裝才生效;spec 的「回退」只提重核可指紋,沒提分發。超時預算:lens 那次子行程 deadline 最多約天花板的 0.9 倍,超時後同一次 hook 呼叫仍受同一個外層天花板,「不跟圖譜那段共用預算」在單一 hook 行程內做不到(只能共用外層的剩餘時間),spec 沒給角色計算自己的上限數字。
佐證:
file: `scripts/hooks/claude/dispatch-lens-hook.py:288` rc==5 才附說明;其後 `if r.returncode != 0: … return 0`、`if not text: … return 0`。
file: `scripts/lumos:30991` `cmd_dispatch_lens_arm` 內 `rc = cmd_dispatch_lens(...)` 之後 `if rc != 0: return rc`,早於寫 `meta.json`。
file: `scripts/lumos:31045` `cmd_dispatch_lens_claim` 只 rename token 並回 `meta.get("text")`。
file: `scripts/hooks/claude/dispatch-lens-hook.py:12` 檔頭聲明本檔在 ANCHOR_FILES 且 hook 只做三件事。

## F7 角色卡會附給每一席,與範本已定的「資料狀態五問只留給正確性席」差異化紀律衝突;後端卡還與資安席重疊
severity: minor
blocking: 否
判準:不改,審查員拿到每席相同的兩張卡,重演 spec 自己引用的「注意力稀釋」與範本第 361-362 行剛規定要避免的「每席做同一份題」;是效果問題不是壞系統。
spec 段落:「要做什麼」2、3、「實務隱患」最後一條。
引句:「注意力稀釋:派工詞變長,審查員可能被新題帶離原本會看的地方」
問題:hook 只看派工詞裡有沒有 `LUMOS-IMPACT:` 行,不知道是哪一席;範本 §7.x 各席(架構對齊、資安、邊界、回滾)都留這一行,所以每席都會被接上前端/後端卡。be 卡「每個端點的授權檢查」與範本 §7.8 資安席的攻擊面重疊;fe 卡的效能/無障礙對回滾席、整合知識同步席無關。spec 唯一的稀釋對策是「判不出就不附」,沒處理「附給哪幾席」。
佐證:
file: `skills/lumos-design-loop/templates.md:362` 已規定資料狀態五問只留給正確性/邏輯席,其他席刪掉,理由是避免差異化被稀釋。
file: `skills/lumos-design-loop/templates.md:266` §7 派工範本同樣要求留 `LUMOS-IMPACT` 行。

## F8 spec 稱後端卡只補「現在沒涵蓋的」,但外呼逾時與大量資料分頁在既有棧別題與慣例 skill 已存在
severity: minor
blocking: 否
判準:不改,實作者不會去核對重複,be-3、be-4 會與作者/架構席已看到的題重複;不壞系統,只是宣稱與現況不符。
spec 段落:「要做什麼」2 後端卡。
引句:「不重複第 1 點正確性鏡頭已有的。只補 API 對外相容(欄位改名、刪欄位、預設值改變)、每個端點的授權檢查、大量資料要分頁、外呼逾時。」
問題:「不重複」只對照了範本第 3 節第 1 點,沒對照棧別題與慣例 skill。實查 `cs-data`(大結果集分頁)、`node-data`(stream/分頁)、`java-data`(分頁或串流)、`node-external`/`py-external`/`java-external`(每個外呼有無逾時)已存在,csharp/java-idioms 另有「大結果集分頁」條款。真正沒有的只有 API 相容與授權兩題(授權在 lumos 全部題庫與範本中 0 命中)。
佐證:file: `scripts/lumos:20285` `_STACK_QUESTION_SPECS` 內 `cs-data`、`node-data`、`node-external`、`py-external`、`java-data`、`java-external` 題文含「分頁」與「逾時/timeout」。
file: `skills/csharp-idioms/SKILL.md:91` R11 大結果集分頁;`skills/java-idioms/SKILL.md:213` R23 大結果集要分頁或串流。

## F9 .ts/.js 判定沿用 `next`/`nuxt` 為前端框架標記,全端框架內的伺服端檔(路由處理、server action)只拿前端卡、拿不到後端卡
severity: minor
blocking: 否
判準:不改,Next/Nuxt 專案裡 API 路由的授權與分頁問題不會被提醒,而前端卡的「只限網頁」題(伺服端渲染、把使用者內容當 HTML 插入)反而會附在後端處理檔上。
spec 段落:「要做什麼」1(d)、「已知限制」(只列空殼 package.json 一種)。
引句:「.ts/.js 家族:照既有 package.json 判定,前端框架 → 前端、Node → 後端、找不到 → 判不出。」
問題:輸入=`app/api/orders/route.ts`(Next.js 路由處理,同 package.json 含 `next`)。1(d) → 前端 → 附前端卡、不附後端卡;它是伺服端授權/分頁的主要載體。spec 已知限制只承認空殼 package.json,未承認這型;出路(宣告路徑對照)雖存在,但受 F3/F4 影響。monorepo 根 package.json 含 react 而 backend 子目錄自己沒有 package.json 時同樣被判前端(最近的 package.json 就是答案)。
佐證:file: `scripts/lumos:20450` `_NODE_FRONTEND_MARKERS = ("vue", "nuxt", "react", "next", "svelte", "@angular/core", "solid-js", "preact")`;file: `scripts/lumos:20448` `_node_flavor` 只取最近一份 package.json、以整份依賴集判定。

## 實務隱患鏡頭
- 併發:派工通道並行 N 席時,Claude 側每席各叫一次角色計算(無快取、無鎖),互不干擾但重複;Codex 側由 arm 一次算好、claim 只 rename,無新競態。已讀,無 finding(前提是角色卡如 F6 所述在 arm 時算)。
- 效能(派工掛鉤時間預算):角色計算只 git 讀改動檔清單與匯入,量級小;唯一隱患是 F6(c)的單一 hook 內預算上限沒給數字。
- 回滾路徑:spec「回退」列全;缺分發面(F6 c),不影響帳本。
- 消費專案(vendored lumos)拿不拿得到:卡片單源放 lumos 本體,消費專案透過安裝拿到;hook 若改動須重跑安裝才生效,spec 未提(F6 c)。

最嚴重 severity 是 major;blocking 共 4 條(F1、F4、F5、F6)。
