# r1 收貨紀錄(code-選擇點存活回指第三段)

材料:r1-snapshot.patch(ce1b2bf48..d5f1970d8,3491 行)拆兩包:r1-pack-code.patch(scripts/lumos,2156 行)給正確性、資源、邊界、通才、架構對齊;r1-pack-test.patch(測試、筆記、文件,1335 行)給合約;資安拿完整一份。記帳時全輪 --reviewed 一律填整份凍結快照的指紋(第二段跑滿回顧的教訓),--snapshot 與 --scope-lines 填各席那一包。七席全數交回後才一次從逐字稿存檔,七份都已正規化;合約席有一句引句錨不到,改機械重現(見下)。另有一條編排者自己的發現(o1):在實驗專案複本用第三段版本跑 choice-layer --template,75 個存活切成 75 份,與資源席 #3 同一根因,併進那條。

## 發現與去向

| id | 席 #條 | 原報 | 一句 | 去向 |
|---|---|---|---|---|
| m1 | 正確性 #1、通才 #1、邊界 #2 | major | 計劃正文排除段用整串相等比對,帶後綴的審計修正紀錄、驗收條款標題被當正文 | 折:容節號前綴與說明後綴的標題正規式,t_choice_plan_sections_variants |
| p1 | 邊界 #3、通才 #3 | minor | 〈前言〉初始段名沒登記,出現兩個同名段 | 折:同上一支測試 |
| m2 | 合約 #1 | major | 新增頂層指令後文件仍寫 102 個,t_docs_command_count 紅 | 折:五處改成 103 |
| m3 | 邊界 #1、正確性 #2 | major | 引句只限實字數,夾大量空白過驗證、寫到一半才超過上限 | 折:引句原始長度上限、寫前整份預檢,t_choice_layer_write_preflight |
| o1 | 資源 #3(編排者實驗專案實跑同一根因) | minor | 共用的計劃條款加預期值表本身就超過份上限時,減半到 1 也縮不下來,75 個存活切成 75 份 | 折:先另存正文、共用材料超過就照存活數出,旁檔各份共用,t_choice_layer_split_shared_plan |
| b4 | 邊界 #4 | minor | 清單內層形狀不對丟堆疊 | 折:t_choice_layer_minor_r1 |
| b5 | 邊界 #5 | minor | gov 不擋範圍外層號 | 折:t_choice_layer_gov_layer_range |
| b6 | 邊界 #6 | minor | 顯示的依據不是驗過那一項,取不到印 None | 折:記錄存 cite,t_choice_layer_minor_r1 |
| g2 | 通才 #2 | minor | 待複核提示加到非存活原因 | 折:t_choice_layer_minor_r1 |
| c5 | 正確性 #5 | minor | 讀回第 1 份失敗印字面 None 回 rc0 | 折:t_choice_layer_template_parts |
| c4 | 正確性 #4、通才 #4 | minor | 存活清單用換候選前的壞法,印未分類 | 折:t_choice_kill_survivor_list_swapped |
| k2 | 合約 #2 | minor | 代碼審手冊選擇點步驟編號重複 | 折:改成連號 |
| k3 | 合約 #3 | minor | S13 沒真的驗到第 2 份 | 折:t_choice_layer_template_parts |
| k4 | 合約 #4 | minor | choice-layers 簿記資料夾沒有測試守 | 折:t_choice_layer_bookkeeping |
| a1 | 架構對齊 #1 | minor | 還原後讀回修改時間仍有手寫第二份 | 折:抽 _kill_mtime_settle,t_kill_mtime_settle_shared |
| a2 | 架構對齊 #2 | minor | 整份拒收輸出與盲判不一致、不讀 BOM | 折:t_choice_layer_minor_r1 |
| r2 | 資源 #2 | minor | 同檔嫌疑多時逐個確認吃光編譯預算 | 折:每批確認上限 8 個依距離排,t_choice_compile_suspect_cap |
| r1 | 資源 #1 | minor | 推送閘對全部有壞法的行算判讀狀態,大專案可能逾時 | 放行:不影響擋不擋,逾時只讓子原因標成未判讀;延後到 Issues/選擇點存活回指第一段末輪小問題第二段先修 |
| c3 | 正確性 #3 | minor | 多平台換候選後判定混到舊候選的列 | 放行:實作裁決 2 的取捨(總比一定落成缺結果好),合批編譯預設只在 Android 平台開 |
| s1 | 資安 #1 | minor | 判讀自由文字原文印進推送閘訊息,可能誘導下一個 AI | 放行:縱深防禦,放行仍要人敲 lint-waive;印前已跳脫控制字元並截字 |

## 機械重現

| id | 做法 | 結果 |
|---|---|---|
| m2 | 跑 -k t_docs_command_count | HIT:ARCHITECTURE.md 與 reference.md 都 claim 102、actual 103 |
| o1 | 實驗專案複本跑 choice-layer --template --diff 5679cdc5b635..HEAD | HIT:75 個存活分成 75 份,每份約 200KB |
| m1 m3 b4 b5 b6 c4 c5 k3 k4 a1 a2 r2 | 修補時各寫一支先紅的測試(實作代理回報 19 道改壞全紅) | HIT |

## 先查世界

- PRIOR-ART:材料分份——本 repo 情境題盲判每份重算、不分享共用段;reread 份清單一份一篇筆記。共用材料本身超過上限時,不靠減半縮,改把大段另存一份旁檔各份共用,沿用 note-audit 工作目錄的旁檔做法,不另找外部做法。
- PRIOR-ART:標題比對容前後綴——照本檔 _FOLD_AUDIT_RECORD_RE 的寫法(容節號前綴、說明後綴),那支只認審計修正紀錄一種且是整份文字的正規式,所以另寫一條同寫法的標題正規式。
