# code-選擇點存活回指條款第一段 r2 收貨

- 派七席(正確性、資源、邊界、合約、通才、架構對齊、資安,sonnet)。前六席主看 r2-repair.patch(上輪修補差異,1693 行),另附 r2-snapshot.patch 對照;資安席看完整的 r2-snapshot.patch(2854 行)。記帳 --spec 與 --reviewed 一律填整份快照。
- 七席全部交回後一次從逐字稿存檔;格式都過 report-normalize。架構對齊席第一版檔級寫 minor、內文有 major,退回原席只改檔級行後重交(內容一字未動)。資安席判 clean、零引句(非載體,同 r1)。
- 編號:正確性 c1–c3、資源 s1–s2、邊界 b1–b4、合約 k1–k2、通才 g1–g5、架構對齊 a1–a2,共 18 條;major 7 條(c1 b1 同一條、k1、g1 g2 g3、a2)。輪內有 major,原報 major 全折;原報 minor 除 c2 外全折,c2 放行(帶 --finding-source)。

## 依根因分組(修正提交見 r2-fix.json)

| 組 | 根因 | 發現 | 折法 |
|---|---|---|---|
| G1 | 分析任務「依賴編譯」用 GString 清單做 in 比對,恆不等(上輪 F4 修補無效) | c1 b1 g4 | 名單先 `*.toString()`;新增 t_choice_cov_groovy_dep:靜態擋 `in [ … ${ … ]`,本機有 Gradle 附的 Groovy 時真跑那一行比對 |
| G2 | 上輪修補沒寫專屬測試(名稱檢查、清快取、分析時間門) | g1 g2 g3 | 新增 t_choice_cov_name_check、t_choice_cov_prune_keep、t_choice_cov_analyze_budget,各自改壞翻紅 |
| G3 | 清快取在建這次資料夾之前、保留數沒算這次 | c3 b3 | 這次的 at_sha 一定留、其餘留 KEEP−1 個;t_choice_cov_prune_keep 釘「清完共 2 個」與符號連結不刪 |
| G4 | 存快取手寫原子寫入(固定 .tmp 名、失敗不清) | a2 g5 | 改呼叫既有 `_write_bytes_atomic` |
| G5 | 計劃與 gov 讀端沒跟上新原因與新欄位 | k1 k2 | 計劃〈範圍〉4 補「名稱檢查沒過」(非暫時性)與 `cov_judged`;gov ck 欄位清單補 `cov_judged` |
| G6 | 掛覆蓋逾時與重跑截斷的處理 | s1 s2 a1 | 掛覆蓋跑滿單支上限當場斷路(原因沿用「掛覆蓋才紅」,不加新原因);不掛的重跑被剩下時限截斷記時間不夠、不寫基準;after 固定回 6 項(多實際秒數與被截斷);新增 t_choice_cov_rerun_edges |
| G7 | 分析輸出缺 nolines、noclasses 照收 | b2 | 三個鍵都要在、型別對才收;假 Gradle 改成跟真腳本一樣三鍵都寫;新增 t_choice_cov_parse_keys |
| G8 | Robolectric 0 的覆蓋資料進續跑快取,重補永遠讀回同一份 | b4 | 這種不進快取(放 scratch),快取裡讀到這種也刪掉重量;新增 t_choice_cov_robo_zero_cache |

放行:c2(minor)——續跑全命中時分析要冷編譯,上限 max(60, 支數×0.5) 秒對大專案可能不夠。不加長的理由:分析前的時間門會跟著加長、更常整段不做;失敗方向安全(記暫時性分析失敗、壞法跑全部守的測試、`--reach-only` 可重補)。實驗專案那次 169 支是全部重量、不是全命中,沒量到這個情境;第二段實測時特意跑一次全命中續跑,逾時就依實測改上限。

## 重現表

| 發現 | 怎麼試 | 結果 |
|---|---|---|
| c1 b1 | 本機 Gradle 8.13 附的 groovy-3.0.22.jar 跑 `'compileDebugKotlin' in ["compile${v}Kotlin"]` | HIT(印 false;加 toString 印 true) |
| g1 g2 g3 | 讀測試檔與程式,確認三處沒有專屬測試;席位各自把條件改成 False 跑 -k choice_cov 全綠 | HIT |
| c3 b3 | 讀 `_choice_cov_prune` 與呼叫順序 | HIT |
| a2 g5 | 讀 store 與既有 `_write_bytes_atomic` | HIT |
| k1 k2 | `grep -c 名稱檢查沒過`、`grep -c cov_judged` 計劃為 0;讀 gov ck 欄位清單 | HIT |
| s1 s2 a1 | 讀 red_rerun 與 `_kill_measure_singles` 的截斷判斷 | HIT |
| b2 | 讀 `_choice_cov_parse` | HIT |
| b4 | 讀 store 與 cached | HIT |
| c2 | 沒有大型 Android 專案可量冷編譯 | 讀程式確認上限算法 HIT;實際逾時未重現 |

## 修補因果(對上輪修補)

上輪修補造成或修補本身沒修到的:c1 b1(F4 修法無效)、c2(F4)、c3 b3(F14)、s1 s2 a1(F3)、k1(F12 新原因)、k2(F8 新欄位)、g1 g2 g3(F12、F14、F6 修補缺測試)、g4(F9 測試只比字串)。上輪之前就在的:a2 g5(store 首版就手寫)、b2(nolines 寬鬆讀首版就有)、b4(store 首版就存)。

## 改壞翻紅(修後逐條把修補拿掉)

groovy_dep 拿掉 toString → 2 紅;name_check 條件改 False → 紅;rerun_edges 逾時不斷路、重跑截斷照寫各 → 紅;parse_keys 缺鍵照收 → 紅;prune_keep 不呼叫清快取、保留數改回 KEEP 各 → 紅;analyze_budget 拿掉時間門 → 紅;robo_zero_cache 照樣存 → 紅。九處全紅,還原後全綠。

## 先查世界

PRIOR-ART: G1 Groovy 的 GString 跟 String:`==` 相等但 `equals` 不相等,Java 集合的 contains(Groovy 的 in 走它)用 equals,所以 String 清單找 GString 或反過來都會漏;Groovy 官方把這列為不修,建議比對前 toString(https://issues.apache.org/jira/browse/GROOVY-2332 、https://nofluffjuststuff.com/blog/scott_leberknight/2008/03/wackiness_with_string_gstring_and_equality_in_groovy )。採用:名單先 `*.toString()`。排除:只靠字串包含的測試(Groovy 不執行就驗不出)。
方向:對 — 分析任務依賴變體的編譯任務是 Gradle 表達「先編譯再分析」的標準做法(依賴寫在任務上,不靠呼叫順序;https://docs.gradle.org/current/userguide/task_configuration_avoidance.html 、https://docs.gradle.org/userguide/best_practices_tasks.html ),這次錯在 Groovy 字串比對,不是方向;`tasks.matching` 會把所有任務實體化,但這是只跑一次的初始化腳本,成本可接受。
PRIOR-ART: G2 修補缺專屬測試——照本 repo 既有紀律(代碼審手冊「首輪派審前先自己變異」),修補後逐條改壞確認翻紅;這輪九處都做了,紀錄在上一節。
方向:對 — 修後逐條變異確認測試會紅,是變異測試的基本用法(https://pitest.org/ 、https://stryker-mutator.io/docs/ ),本 repo guard-kill 本身也是這套;上輪漏在「修補沒逐條變異」,不是方向問題。
PRIOR-ART: G4 原子寫入——沿用本 repo 既有 `_write_bytes_atomic`(暫存名帶 pid 與 uuid、O_EXCL、失敗清暫存),不另寫。
PRIOR-ART: G3 快取保留——LRU 保留「這次一定在用的那份」再依時間留其餘,同一般快取清理把正在用的條目標成 pinned 的做法;不另查。
PRIOR-ART: G6 逾時當場斷路——沿用合併快篩既有的「逾時算紅、當場收手」形狀;不加新原因字串,避免下一輪多一個讀寫面。
