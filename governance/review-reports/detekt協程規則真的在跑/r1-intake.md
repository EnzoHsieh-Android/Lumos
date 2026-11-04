preflight-4: ran

# r1 收貨紀錄(detekt協程規則真的在跑)

## 前掃(2026-11-04,sonnet 一席,固定四項清單)

①未定義詞、②壞引用、③範圍矛盾、存在類命中:直接修真檔,不算 findings。
- ①白話名沒對上規則名(吞取消訊號、補開兩條、型別參數、探針放哪):計劃新增〈用詞〉節逐一對上。
- ②所有連結與指令都在;測試名找不到是實作前的正常狀態。
- ③共用設定補開會影響新增告警閘、S4 觸發條件比探針寬、探針不驗 collectAsState、S3 與實務隱患語氣:範圍、不做、實務隱患各補一句講明。

## 語意類命中(修真檔,修改前→後)

1. 回退節對健檢的描述錯了(健檢 F 段只做格式驗證,從不執行 linter)。
   - 前:「冒煙與健檢回到只驗『有沒有產出 SARIF』」
   - 後:「冒煙回到只驗『有沒有產出可解析的 SARIF』,lint-check 與健檢 F 段不再印型別資訊提醒(健檢本來就不跑 linter,只驗宣告格式)」
2. PRIOR-ART ③說「照抄」既有提醒形狀,但那個形狀只用在「沒宣告」那一支,已宣告且健康那一支只有 ok 訊息。
   - 前:「照抄健檢 F 段既有的『有 eslint 設定但沒接』提醒形狀」
   - 後:「用同一個形狀(提醒函式帶空清單)…本案是在 F 段新加一個判斷,不是改既有分支」;範圍另寫明放在 F 段既有分支之後、宣告讀得出來就判。
3. 換 `--input` 被說得像小改動,實際既有冒煙只換 `{LINT_FILES}` 佔位符,沒有處理 `--input` 的程式。
   - 前:範圍只寫「把輸入換成內建探針檔再跑一次」
   - 後:「把那個參數的值(連同外面的引號)整段換成探針暫存目錄…這段換參數的程式是新寫的」

沒有動到核心裁定,不升級為正式 finding。

## 先查世界

PRIOR-ART: 規則有沒有在跑用正樣本驗——查 detekt 官方型別解析文件(https://detekt.dev/docs/gettingstarted/type-resolution)明寫沒有型別解析時要型別的規則「不會跑」、沒說會警告;本機實驗也沒有警告。所以只能從外面用已知會中的樣本驗,不能靠工具自己報。採用。

## r1 收貨(四席:正確性、邊界、接手、架構對齊;全為 sonnet,同一家模型)

機械三道:四份報告引句全數錨定凍結快照;refcheck 引用全部存在(ok 21/17/30/30,missing 0);seat-check 派工單材料格式未被讀到(vacuous)。正規化:三份報告把列表式等級搬成獨立行(只搬格式)。

## 編排者重現(命令 → 結果 → HIT/MISS)

| 發現 | 重現方式 | 結果 |
|---|---|---|
| 邊界F1/接手F4:沒帶佔位符的 detekt 宣告在新增告警閘只記錄不擋 | 讀 `_lint_new_run` 一帶:`if _LINT_NEW_FILES_TOKEN not in cmd: out["report_only"].append(cmd); continue` | HIT |
| 邊界F1:帶佔位符時多檔用空白分隔,detekt 1.23.8 拒跑 | `detekt --input 'src/Probe.kt' 'src/Probe2.kt' --report sarif:m.sarif` → rc=1 `Was passed main parameter 'src/Probe2.kt'`;逗號分隔 `--input 'src/Probe.kt,src/Probe2.kt'` → 有 SARIF | HIT |
| 正確性F1/接手F8/邊界F10:SARIF ruleId 帶前綴 | 先前實驗輸出 `detekt.coroutines.InjectDispatcher` 等 | HIT |
| 接手F3:`./gradlew detekt` 任務沒有型別解析 | detekt 官方型別解析頁 | 未本機重現(沒有 Android 專案可跑),採信官方文件 |
| 接手F1/正確性F11:Android 專案沒有可抄的 classpath 取得法 | 計劃與調研筆記確實沒寫 | HIT |

## 依根因分組

- **A 方向類(改變第 1 步該做什麼)**:①推送閘對 Android detekt 實際上從不擋(邊界F1、接手F4);②CLI 帶 classpath 對 Android 專案走不通、Gradle 純 detekt 任務也沒型別(接手F1、F3,正確性F11)。這兩條讓「只補冒煙探針」修不到真正的洞。
- **B 判定細節類**:規則 ID 前綴比對(正確性F1 等)、探針沒產出 SARIF 的第三態(正確性F2、邊界F2)、沒依賴協程函式庫的專案誤判(正確性F3)、detekt 指令列判法(正確性F4、邊界F3、接手F7)、健檢遇畸形宣告崩潰(正確性F5、邊界F8、接手F9)、`--json` 與問題分支的提醒去向(架構、正確性F6)、探針換參數成為第二種做法(架構 major)、暫存目錄與報告檔副作用(邊界F7、F9,架構)。
- **C 知識同步類**:圖譜與 kotlin-idioms 多處「已開/預設開」會被讀成「有在擋」(接手F5、F10)。

## 判讀

單輪 blocking 約 15 條、計劃約 3,000 字,超過手冊「>1 條 blocking/300 字」的重寫建議訊號;A 類兩條改變範圍本身,不是折幾句能修。攤給使用者裁方向(縮範圍重寫或改做推送閘),本輪暫不折、不記帳。
