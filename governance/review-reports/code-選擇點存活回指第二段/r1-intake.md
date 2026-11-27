# r1 收貨紀錄(code-選擇點存活回指第二段)

材料:r1-snapshot.patch(37510bf04..73939824e,3447 行,sha256 2a4adc7b…)拆兩包:r1-pack-code.patch(scripts/lumos、scripts/test_quality.py,2225 行)給正確性、資源、邊界、通才、架構對齊;r1-pack-test.patch(測試、筆記、文件,1222 行)給合約;資安拿完整一份。七席全數交回後才一次從逐字稿存檔。架構對齊席報告檔首少檔級行,用 report-normalize --write 純格式補(不改內容);資安席總結句帶了更高等級字樣,退回原席只改那一行重交。正確性 #1、邊界 #2 各有一句引句是 diff 外的程式(`_situation_rule_point_target`),錨不到,改機械重現(見下)。

## 發現與去向

| id | 席 #條 | 原報 | 一句 | 去向 |
|---|---|---|---|---|
| c1 | 正確性 #1、邊界 #2、通才 #1 | major | exhausted 行讓 situation-rule --point 丟 KeyError;lint-waive 把它說成沒有壞法 | 折:補鍵與字樣,t_choice_exhausted_status_readers |
| c2 | 正確性 #2 | major | 探針整批全綠才補償,一個永久紅的舊候選讓同批能編的都補不到 | 折:整批紅改逐個單獨編,t_choice_compile_probe_split |
| c3 | 正確性 #3 | minor | --reach-only 也做合批編譯並寫 invalid | 放行:計劃〈範圍〉7 明寫 reach-only 準備物件做完合批編譯與覆蓋才結束 |
| c4 | 正確性 #4 | minor | 多平台時換候選清掉前一平台組已跑的列 | 放行:合批編譯預設只在 Android 平台開,多平台同一行同時開編譯才會碰到;延後到 Issues/選擇點存活回指第一段末輪小問題第二段先修 |
| r1 | 資源 #1 | minor | 壞法行讀整份檔做註解處理,大檔白花秒數 | 折:兩邊都只取檔頭 _CHOICE_COV_SRC_HEAD,t_choice_cov_pkg_comments |
| r2 | 資源 #2 | minor | 編譯輸出超過 256KB 截斷時整批抓不到無效 | 放行:失效開放(照現在交測試、不判錯);延後到同議題 |
| b1 | 邊界 #1 | major | 修改時間沒錯開時探針沒編就記補償 | 折:新增「這次沒驗」值,三處都認,t_choice_compile_probe_split |
| b3 | 邊界 #3 | minor | 只編測試所在模組,跨模組的壞法編不到 | 放行:實作裁決 2,失效開放(照現在交測試) |
| k1 | 合約 #1 | minor | 計劃 cov-audit 欄位與判錯條件跟程式不一致 | 折:計劃範圍 4、5、6 與〈用詞〉改寫 |
| k2 | 合約 #2 | minor | Groovy 真跑改成手動打開,沒寫回頭條件 | 折:規格閘補 REVISIT when-symbol |
| g2 | 通才 #2 | minor | 行註解裡的 /* 讓區塊註解正規式蓋到檔尾 | 折:改用既有 _strip_c_comments,t_choice_cov_pkg_comments |
| g3 | 通才 #3 | minor | 抽查跑出 no_result 被當成判對 | 折:no_result 不算抽查完成,其餘改照跑,t_choice_cov_audit_noresult |
| a1 | 架構對齊 #1 #2 | major | _platform_compile_flag 另寫 Android 單元測試判法 | 折:預設改成 _choice_compile_cmd 組得出指令,刪掉自寫正規式,t_choice_compile_flag_same_source |
| a2 | 架構對齊 #3 | major | 合批套壞法前沒過 _kill_old_issue、_kill_new_issue | 折:units() 補兩道,t_choice_compile_units_guards |
| a3 | 架構對齊 #4 | minor | 還原是第三份「等新一秒、checkout、讀回修改時間」 | 放行:多檔、內容比對、丟中止例外,語意跟既有兩份不同;延後到同議題 |
| a4 | 架構對齊 #5 | minor | _choice_compile_cmd 抄了一份取模組與變體 | 折:抽 _choice_unit_variant、_choice_task_swap,三處共用 |
| s1 | 資安 #1 | minor | 套壞法目標可能是指向 .git 的捷徑 | 折:units() 擋真實路徑在 .git 底下,t_choice_compile_units_guards |
| s2 | 資安 #2 | minor | 只改別支檔時舊無效候選要等下一次探針 | 放行:計劃〈用詞〉跳過集合明載的設計(推送閘不跑探針) |

架構對齊報告 #1 是席位寫在引言段後的檔級宣告(report-normalize 把它算成一條),內容即 #2,同指給 a1。

## 機械重現

| id | 做法 | 結果 |
|---|---|---|
| c1 | 載入 scripts/lumos、替身 _choice_range 與 _choice_kill_scan 回一行 status exhausted,呼叫 _situation_rule_point_target(None,"a.kt:3",None,None) | HIT:KeyError 'exhausted' |
| c2 b1 a1 a2 g2 g3 s1 | 修補時各寫一支先紅的測試(實作代理回報 12 組改壞全紅) | HIT |
| c3 | 讀計劃〈範圍〉7:「準備物件做完合批編譯與覆蓋就結束」 | 現象 HIT,判準 MISS(規格就是這樣) |

## 先查世界

- PRIOR-ART:變異測試對編不過的變異——Stryker 把 CompileError 與 RuntimeError 歸成 invalid,不進分數的分母,報表另列筆數。來源 https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ 、 https://stryker-mutator.io/docs/General/faq 。採用:無效壞法不計分、換候選、另列筆數;探針逐個單獨確認才補償(Stryker 文件沒講重驗,這一半是本計劃自己的規則)。
- PRIOR-ART:套件宣告讀法沿用檔裡既有 _strip_c_comments(Kotlin 模式),不另寫正規式。
