# r3 收貨紀錄(code-android資安與崩潰靜態檢查補齊)

兩席新席(審查三、架構對齊三)全數交回後才寫進卷證;報告從逐字稿取最後一則。架構對齊三的三行 severity 前面有縮排,用 `report-normalize --write` 純格式搬移(只動縮排、不改等級與引句)。兩份 quote-check 全數錨定。

編號:審查三 S1、S2(major)、S3、S4(minor);架構對齊三 A6(共用機制兩種並存)、A7(共用判斷 id 帶 kt- 前綴)、A8(節點目錄說明沒跟上),都是 minor。

歸因(照審查三兩版實跑):S1、S2 有證據的修復回歸(r2 修補新增的正規式與分支);S4 的 when 主詞寫法對 API-19 是修復回歸、帶套件名是原有漏查;S3 原有漏查。

## 先查世界

- PRIOR-ART:S1 S2:同一個「是不是只在除錯版走到」的判讀,r2 用字面正規式補「且」、r3 又被 `!=`、`!x && DEBUG` 打穿——同類第二次,照手冊換形狀,改看語法節點種類:ast-grep 的 Kotlin 語法把 `a && b` 解成 `conjunction_expression`、`a || b` 解成 `disjunction_expression`、`!x` 解成 `prefix_expression`(暫存區 `--debug-query=cst` 實測),只認「條件節點本身是除錯旗標」或「`conjunction_expression` 的直接子節點是除錯旗標」,括號、`||`、否定自然不算。同類工具做法:MobSF mobsfscan 不分析外層判斷(計劃 PRIOR-ART ③),本包選擇保留結構判斷以免 API-19、DATA-16 對除錯版寫法誤擋。排除:任何靠字串比對條件文字的做法。
- A6:ast-grep 規則檔內的 `utils:` 只在同一檔可用(官方 utility-rule 文件 https://ast-grep.github.io/guide/rule-config/utility-rule.html ),跨檔要 `utilDirs`;compose.yml 那幾組只在同一檔共用,不搬,理由寫進規則包節點。

## 出處清單

- 共用判斷的引用:`grep -rn in-debug-only-branch configs/ast-grep/kotlin-android/` → API-19、API-40、DATA-16(`rules/`)、API-41(`rules-unwired/`)四處。
- 舊版 TLS 的 enabledProtocols 寫法:方法呼叫(`.`、`?.`、`arrayOf<String>`)、屬性賦值(改成賦值節點種類比對,認多層、`!!`、`apply` 區塊)。

## 重現(修前紅、修後綠)

| id | 驗法 | 結果 |
|---|---|---|
| S1 | 新增 C36–C38(`x != null && DEBUG`、`!a && DEBUG`、`DEBUG && (a \|\| b)`)| HIT:r2 版報,r3 版不報 |
| S2 | 新增 C39(`a \|\| b && DEBUG`,照報)、C47(`a && (b \|\| DEBUG)`,照報);共用判斷的「且」分支拿掉 → C27、C36–C38 紅;改成往下找 → C47 紅 | HIT |
| S3 | 新增 C44(多層)、C45(apply)、C46(`?.` 加 `arrayOf<String>`)| HIT:修前不報,修後報 |
| S4 | 新增 C40(帶套件名,不報)、C42(when 主詞 true 分支,不報)、C43(false 分支,報);拿掉套件名 → C40 紅、when 主詞放寬到 false → C43 紅 | HIT |
| A6 A7 A8 | 讀碼 | HIT;改短名、節點補目錄說明與不搬 compose.yml 的理由 |

改壞驗證另含:拿掉 !DEBUG 的 else → C41 紅;拿掉一般 else 排除 → C07、C25、C32 紅。修後 `check.py --sg` 規則 211 條、0 個問題;`-k kotlin_rulepack` 111 passed、`-k kt_catalog` 48 passed。

## 上限

r3 是 standard 代碼審的上限。這輪修補沒有再派新席看;把關靠審查三列出的每個寫法都進了逐例案例、加上每個分支的改壞驗證。收尾報告照實寫這一點。
