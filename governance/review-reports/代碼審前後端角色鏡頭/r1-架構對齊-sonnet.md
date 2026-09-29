severity: major

## F1 角色卡另開一條派工附段通道,掛鉤不再是薄殼
severity: major
blocking: 是
引句:「角色卡另走一次快速計算,只看改動檔清單、檔案匯入與 package.json,不跟圖譜那段共用預算與快取」
說明:既有派工附段只有一條通道:掛鉤只叫一次 `lumos dispatch-lens`,文字(含框)全在 lumos 端組,超時只附一行固定說明、不附任何內容;Codex 那條是武裝時把 text 存進 meta.json、領席時原樣吐出。本計劃要求「圖譜那段超時或算出空白時,角色卡照附」,而且「不共用預算與快取」,等於在 lumos 端或掛鉤端多一段獨立計算與獨立超時處理;回退節又寫「掛鉤檔改回後要重核可指紋」,表示要動掛鉤。掛鉤檔頭明寫「掛鉤只做三件事,其餘住 lumos 子命令」,第二次呼叫或超時分支塞內容都違反。Codex 通道的文字是武裝時就算好的,計劃沒說角色卡在哪一刻算、怎麼進 meta.text。建議把角色卡併進 `cmd_dispatch_lens`/`cmd_dispatch_lens_arm` 輸出的同一段文字,內部各自計時,掛鉤與領席碼不動。
對照的既有寫法:file: `scripts/hooks/claude/dispatch-lens-hook.py:298`、file: `scripts/hooks/claude/dispatch-lens-hook.py:317`(超時只附 TIMEOUT_NOTE)、file: `scripts/lumos:31045`(cmd_dispatch_lens_claim 原樣吐 meta.text)

## F2 新增第二套「這支檔是什麼棧」判定,且開始讀檔案內容
severity: major
blocking: 是
引句:「手機與 Android 畫面:看檔案本身的匯入」
說明:既有判棧只有一條路:`_stack_key_for_file`(副檔名為鍵,.ts/.js 走 `_node_flavor`),其 docstring 明說「兩個消費者都走這一支,別各自抄副檔名邏輯」,`_idiom_skill_for` 也是同一條。本計劃另造一個「角色」判定,優先序自成一套(宣告→匯入→副檔名表→package.json),第 (c) 步重列一份副檔名表,第 (b) 步讀檔案內容嗅匯入。`_node_flavor` 註明「只看 dependencies 的鍵,不猜檔案內容」,理由是猜錯會把問題塞給錯的檔;本案的匯入嗅探正好走相反方向,還要處理刪除檔看改動前版本。同一支檔於是有「題組鍵」「慣例 skill」「角色」三個各自判定的答案,可能互相矛盾(例:同一支 .kt 被判成角色前端,卻還在 kt 題組)。建議角色從 `_stack_key_for_file` 的結果映射(kt/dart/swift 之類的鍵加一張鍵到角色小表),需要的內容嗅探只當該映射的補充,並在同一個函式裡。
對照的既有寫法:file: `scripts/lumos:20488`(_stack_key_for_file)、file: `scripts/lumos:20448`(_node_flavor,不猜檔案內容)、file: `scripts/lumos:26921`(_idiom_skill_for)

## F3 設定檔新鍵沒交代壞值處理,既有兩種做法不一致
severity: minor
blocking: 否
引句:「第一條命中的算數;樣式比對沿用專案既有的路徑樣式比對寫法」
說明:路徑樣式比對沿用 `_cochange_excluded`(fnmatch 加去掉 `**/` 再試一次)是對齊的,不列問題。但計劃沒寫 `.lumos/config.json` 的鍵名、壞格式(非清單、角色值不是前端/後端、樣式非字串、JSON 壞掉)怎麼辦。既有兩種:`_ci_config` 壞了回關閉並印 stderr 警告;`_stack_questions_config` 回預設並把警告收進 warnings 由呼叫端印。專案自己沒有統一做法,見末尾 ⚠。派工掛鉤是靜默執行的環境,warnings 印去哪也要交代。
對照的既有寫法:file: `scripts/lumos:20505`(_stack_questions_config)、file: `scripts/lumos:28241`(_ci_config)、file: `scripts/lumos:26394`(_cochange_excluded)

## F4 卡片單源的形狀跟既有題庫不同,審查方向內容散在兩處
severity: minor
blocking: 否
引句:「內容單源放在 lumos 本體(跟棧別題庫同處,消費專案拿得到)」
說明:計劃說跟棧別題庫同處,但形狀不同:既有題庫每題是 `{id, q, when}`,id 是語意代號(kt-compose、dart-platform),靠 `when` 觸發;角色卡題號是流水號 fe-1、be-1,整張附、沒有觸發條件、沒有表態統計。另一方面,上一份同型計劃把審查鏡頭內容放在 design-loop skill 的派工範本第 3 節,並以文件內容守衛測試釘;本案正確性鏡頭主體仍在範本、角色卡在 lumos 本體,同樣是「審查員該往哪看」的內容分住兩處,只靠第 5 點一句指路連起來。結構本身站得住(範本不複製卡片、只指單源),但命名(流水號 vs 語意 id)與「為何不進範本」沒有交代。兩份先例都存在,見末尾 ⚠。
對照的既有寫法:file: `scripts/lumos:20285`(_STACK_QUESTION_SPECS 的 id/q/when 形狀)、file: `skills/lumos-design-loop/templates.md`(第 3 節審查鏡頭,資料狀態鏡頭放這裡)、file: `docs/lumos-toolchain-knowledge/Projects/代碼審資料狀態鏡頭_計劃.md`(範本內容守衛做法)

## F5 lands_in 漏掉判定與設定讀取的既有家
severity: minor
blocking: 否
引句:「[[Systems/棧別提問表態閘]]」
說明:計劃只把棧別提問表態閘放在 related,lands_in 卻列 design-loop、pitfalls-code-loop、codex-harness。`_node_flavor`、`_stack_key_for_file`、`_stack_questions_config` 這一帶(以及 .lumos/config.json 讀法)的家是棧別提問表態閘與 pitfalls-code-loop;新的角色判定與設定鍵就放在它們旁邊,卻沒歸到那篇。另外派工範本檔 `skills/lumos-design-loop/templates.md` 目前沒有登記在任何 Systems 節點的 about_code(既有欠帳,上一份計劃也這樣處理),本案要改它,先確認是否被每支檔有家擋下。

## 四問

1. 分層與依賴方向:不對齊(F1、F2)。lumos 本體放判定與卡片、範本只指路、掛鉤不讀 skill 檔,這幾點對齊,也沒有派工範本與 lumos 各存一份卡片內容(範本第 5 點只指路);問題在掛鉤/領席那一層多出第二段獨立計算(F1),以及判定層多一套平行的檔案分類(F2)。
2. 命名與錯誤處理:大致對齊但有缺口(F3、F4)。壞設定值處理沒寫、warnings 與 stderr 兩種既有做法沒選;題號 fe-1/be-1 與語意 id 慣例不同。
3. 第二種做法:有(F1 另一段派工附段通道與獨立超時處理;F2 另一套判棧且讀檔案內容)。路徑樣式比對沿用既有的 `_cochange_excluded`,設定讀取沿用直讀 `.lumos/config.json`,這兩項沒有第二種。
4. 落點合不合理:寫進既有幾篇大致合理,不需另開新節點;但判定與設定鍵應歸棧別提問表態閘(F5),掛鉤相關歸 codex-harness(dispatch-lens-hook.py 的家),範本相關歸 design-loop。scripts/lumos 已由四篇共同登記,不影響。

## ⚠ 交編排者
- ⚠ 設定壞值處理:`_ci_config`(關閉加 stderr)與 `_stack_questions_config`(預設加 warnings 清單)兩種既有做法並存,專案沒有單一慣例;請編排者裁本案跟哪一種。
- ⚠ 卡片單源位置:資料狀態鏡頭放範本(文件守衛)、棧別題庫放 lumos 本體(內容守衛);兩份先例都在,本案選 lumos 本體有機械附上的理由,但範本正確性鏡頭與角色卡分屬兩處是否可接受,請編排者裁。

總結:不對齊共 5 條,其中 major 2 條。
