severity: major

## F1 「下一站接住」排除規則會把自動記逃逸的整批 design 類資料歸零

severity: major
blocking: 是——照 spec 字面實作,`design` 類的逃逸率會被結構性低估到接近 0,量尺量到的不是它宣稱要量的東西,拿去做決定會判斷錯。

spec 第一節定義 `loop_kind=design` 的其中一種來源是代碼審自動記逃逸,而且明講這樣分類的用意就是要記下「設計審放過、代碼審接住」這件事:

引句:「代碼審記到 major 時自動記的逃逸,loop 欄故意寫成去掉 code- 的計劃名」

spec 第四節「下一站接住」規則卻是:

引句:「站名是 `實作`、`code-loop`、`push-gate` 的,代表往下一站就被接住,另列一欄,不算漏網。」

問題:代碼審自動記逃逸寫進帳的那一列,`stage` 欄位就是字面上的 `"code-loop"`(見 `scripts/lumos:8008-8011`,`_auto_escape(env, "code-loop", severity, ..., source="code-loop", ...)`)。所以「代碼審放過的」用 `loop_kind=design` 分類進 design 那一類統計,但因為它的站名剛好也叫 `code-loop`,同一列在第四節被「下一站接住」規則排除、不算進分子。結果是:凡是靠這個自動機制記下的 design 逃逸,一律不算漏網——不是因為它真的被下一站接住免責,而是站名字串剛好撞上排除清單。這跟 spec 自己在第一節寫的「歸給設計審迴圈」的意圖直接矛盾:歸給 design 是想讓它算進 design 的逃逸率,但下一站接住規則會讓它永遠不算。

拿真實帳驗證(`docs/.escape-log.jsonl`,25 列):17 列是自動記的,其中 7 列 `stage=="code-loop"`(即代碼審自動記逃逸那批),例如:

file: `docs/.escape-log.jsonl`(第 25 列附近,loop=`雙向門放行`/`收工點名問版本控制`/`筆記欄位關卡補齊`/`驗收前提欄位可改`,共 7 筆,`auto:true, stage:"code-loop", source:"code-loop"`)——這 7 筆依第一節規則全部會被推成 `loop_kind=design`,但依第四節規則又全部落進「下一站接住」而不進分子。這是目前逃逸帳裡「設計審放過、代碼審接住」語意的全部資料,7/25 = 28% 的既有列。照 spec 字面實作,design 類逃逸率永遠測不到這整條路徑帶來的訊號,而這恰好是 spec frontmatter WHY 段落點名要記下的東西。

## F2 「放行了的迴圈」定義沒有指明治理帳哪個 kind 才算過閘,現有機制把三種不同結果混記

severity: major
blocking: 是——分母若誤收未過閘的迴圈,率會系統性偏低,而且偏低的方向與幅度不可預期(取決於 cap-reached/rewrite 事件多寡),使用者會拿一個算錯的率去下結論。

spec 第四節對分母的定義:

引句:「分母:放行了的迴圈數。放行 = 治理帳裡有這個迴圈的收斂紀錄(處置閘過關時寫的),而且審查帳裡有它的列」

PRIOR-ART 段落也說機制層要沿用既有的「收斂紀錄」:

引句:「處置閘過關時寫進治理帳的收斂紀錄」

但治理帳裡 `gate=design-loop` 的收斂事件其實有三種 `kind`,語意完全不同(`scripts/lumos:551`):

file: `scripts/lumos:551` — `kind=converged(閘過了)| cap-reached(跑滿上限沒過)| rewrite(人裁判整份重寫、開新編號收尾)`

只有 `converged` 是「處置閘過關」;`cap-reached` 明寫是「沒過」,`rewrite` 是人工裁定整份打掉重寫(不是通過)。現有程式碼(`scripts/lumos:8660-8661` `LOOP_CLOSE_EVENTS = {("design-loop","converged"),("design-loop","cap-reached"),("design-loop","rewrite")}`)把三者一起當「關門」用,但那是為了判斷「迴圈還開不開著」這個不同的問題,不是「有沒有放行」。spec 沒有指明分母只該收 `converged`,也沒有提醒現成的「收斂紀錄」判定(`_loop_close_stamps`/`LOOP_CLOSE_EVENTS`)三種混記,任何字面實作(不管是重用既有函式還是照 spec 文字重寫)都會撞到同一個模糊點:到底算不算 `cap-reached`/`rewrite`?

拿真實帳驗證,治理帳裡 `design-loop` 的分布(`docs/.governance-log.jsonl`):converged 257、rewrite 9、cap-reached 3。9 筆 rewrite 裡例如 `loop-friction`:

file: `docs/.governance-log.jsonl`(2026-08-25T17:04:17,`gate=design-loop kind=rewrite nodes=["loop-friction"]`)note 寫「r1 五席 25 審項/blocking 21」——這個迴圈是被判定不過關才整份重寫,不是「處置閘過關」。若字面實作把它算進分母(因為它確實是治理帳裡「這個迴圈的收斂紀錄」),分母會多算至少 12 個(design 類)從未真正放行的迴圈,拉低所有 design 類別的率,而且拉低幅度不透明。

## 已看,無:

- 條款 S1–S9 與做法一~四逐條對照過現有函式(`_escape_rows_for` scripts/lumos:7397、`_plan_for_loop` scripts/lumos:9293、`cmd_loop_escape` scripts/lumos:9404、`_auto_escape` scripts/lumos:9319):撤回機制(S3)描述與現況相符——`cmd_loop_escape --list`(scripts/lumos:9438 起)與 `rule-gap`(scripts/lumos:20215)確實各自開檔讀、沒走 `_escape_rows_for`,spec 第三節要改這兩處的描述屬實,不影響本次找到的兩條。
- S2(手動記帳要 sha 或 defect_ref)與現況程式碼相容:`cmd_loop_escape` 目前已有 `defect_ref` 參數與寫入邏輯(scripts/lumos:9514-9515),補一道擋下檢查即可,沒有結構性衝突。
- S4「率不得大於 1」:只要分子集合是分母集合的子集,結構上成立,本身沒有邏輯錯——問題出在分母/分子定義本身(見 F1/F2),不是這條款式子。
- S6 歸因不明(同一 sha/defect_ref 出現在兩個以上迴圈):現有帳本資料裡沒有找到違反此假設的實例,判準本身可執行,沒有另立疑慮。
- S7 分級(tier)取值:`docs/.canary-log.jsonl` 確認欄名是 `tier`,值域 standard/high/light,與 spec 假設相符;範圍類（`scope/<類>`）標籤機制沿用 `_plan_for_loop`,查得到對應計劃檔案。
- S8 樣本太少門檻(<20)與 S9(治理帳有收斂紀錄但審查帳沒有列,不算分母)本身是可執行的獨立規則,不受 F1/F2 影響(F1/F2 影響的是「哪些列/迴圈進得了分子分母」,不是這兩條款式子本身)。
- 效能與併發段落(逃逸帳/審查帳/治理帳檔案大小 1.7MB/13MB)與磁碟實測相符(`docs/.canary-log.jsonl` 1,747,009 bytes、`docs/.governance-log.jsonl` 13,291,056 bytes),唯讀指令不進閘的宣稱與 `lumos escape-stats` 尚未存在的事實一致(現有 `--help` 沒有這個子指令,屬於本案要新增,非矛盾)。
- 回退段落與誠實界線段落純屬文字宣告,沒有可執行性缺口可查。

最嚴重 severity: major;blocking 共 2 條。
