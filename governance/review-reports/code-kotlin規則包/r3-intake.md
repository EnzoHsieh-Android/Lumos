# r3 收貨紀錄(code-kotlin規則包)

## 收貨

- 七席全數交回後一次存檔(從各席逐字稿抽最後一則),報告格式、引句、檔案引用三道都過;通才、架構對齊兩席 clean。
- 條數:正確性 6、邊界 2、規則 5、合約圖譜 2、資安 1,共 16。規則席 Finding 1、2 是 major,其餘 minor。
- 本輪派工詞寫明「不准改 repo 工作樹」,各席報告與 `git status` 都確認沒動工作樹。
- 修補因果:16 條裡 14 條是 r2 修補引入或沒修到位(「(無)」分支沒作用、files 區塊新讀法的小退步、缺〈來源縮寫〉早退、逾時測試只鎖一條路、多餘條件、錯位註解、全形半形混寫、規則放寬或名單擴大造成的誤報、型錄搬級後補註沒跟上);規則 Finding 5(Ktor 存變數後 use)與資安 1(樣本目錄範圍)是修補前就有的。

## 先查世界

- PRIOR-ART: OkHttp 5 的 `Response.body` 改成非空(5.0.0-alpha.7 起,https://square.github.io/okhttp/changelogs/changelog 、https://square.github.io/okhttp/5.x/okhttp/okhttp3/-response/body.html ),所以 `r.body.use { }`、`r.body.string()` 是正確的關閉寫法,規則席的觀察屬實。光看語法樹分不出呼叫端用的是 OkHttp 4 還是 5,也分不出 body 有沒有被關,改形狀只會再放寬一次;採用:整條搬語意覆核級,正確寫法放成 review-fp- 好例給盲判對照。
- PRIOR-ART: Semgrep 把「多嚴重」(severity)與「多確定不誤報」(confidence)分成兩個欄位,型別判不準的規則降確定度、不靠一直放寬形狀(https://semgrep.dev/docs/kb/rules/understand-severities );本規則包的對應做法就是第三級語意覆核級(info,不擋,命中交盲判),延續 r1、r2 收貨引用的 Semgrep AI 雜訊過濾做法。DataStore 的 try/runCatching 放行同理搬級。
- PRIOR-ART: 自我檢查的小修(註解行、全形半形括號、缺節照樣報齊、逾時旗標)是本檔內部判讀,查的是 YAML 規格(整行 `#` 是註解、不屬於任何鍵,https://yaml.org/spec/1.2.2/#comments );照它先去掉整行註解再找區塊邊界,不另寫 YAML 解析器(零依賴家規)。

## 修後改壞驗證

把 check.py 逐處改壞,跑規則包與型錄兩支測試,九處都各自翻紅:files 區塊不剝註解、「(無)」並列不報、全形不正規化、「(無)」不回空清單、缺〈來源縮寫〉早退、讀載入條數不守逾時旗標、掃描逾時不設旗標、自我檢查開頭不重設旗標、讀不到條數印 None。

## 逐條去向(15 折、1 放行、0 駁回)

| id | 席報告原條 | 去向 |
|---|---|---|
| 正1 | 正確性 #1 | 「(無)」解析抽成 `dt_triggers`,回空清單;跟其他觸發字並列要報;測試直接斷言解析結果 |
| 正2 | 正確性 #2 | files 區塊判斷前去掉整行註解;補頂格清單、頂格註解兩條改壞與一條對照 |
| 正3 | 正確性 #3 | 缺〈來源縮寫〉節改成記一筆、縮寫當空集合照跑;測試斷言同時報出其他問題 |
| 正4 | 正確性 #4 | 補「讀條數立刻回、掃描才卡住」的假工具;門檻收到 2.5 秒;補下一次自我檢查不沿用旗標 |
| 正5 | 正確性 #5 | 刪掉多餘的 `owner == rule_id`(只讀自己目錄的命中,行為不變) |
| 正6 | 正確性 #6 | 註解移回 `MSG_MAX` |
| 邊1 | 邊界 #1 | 同正1:全形半形先統一再比 |
| 邊2 | 邊界 #2 | 同正3 |
| 規1 | 規則 #1(major) | `kt-okhttp-response-not-closed` 搬 rules-review/;OkHttp 5 寫法放 review-fp- 好例 |
| 規2 | 規則 #2(major) | `kt-datastore-read-no-catch` 搬 rules-review/;try/runCatching 裡的終端操作放 review-fp- 好例 |
| 規3 | 規則 #3 | `CoroutineScope(…) + 屬性` 的屬性是 SupervisorJob 時放行;補反向壞例(普通 Job 照報) |
| 規4 | 規則 #4 | 名單拿掉泛用的 `state`;Map 片段補進好例 |
| 規5 | 規則 #5 | 同一個變數接 `.use { }` 算關掉;補反向壞例(use 別的資源照報) |
| 合1 | 合約圖譜 #1 | 型錄 STATE-4 實測欄註明 Eagerly 那條在語意覆核級、同列另兩條才擋 |
| 合2 | 合約圖譜 #2 | 型錄 CO-44、DATA-36 實測欄補語意覆核級與 review-fp- 說明;API-17、DATA-10 因規1、規2 改通電批次;統計重算(info 12、warning 115;守到列數口徑寫死成程式算得出的定義,129) |
| 資1 | 資安 #1 | 放行:樣本目錄排除範圍是明說的取捨(Systems/kotlin規則包 檔案節);利用要把產品碼刻意放進工具鏈教材樣本目錄,屬專案威脅模型不防的刻意偽造(單人自用、AI 依序操作),加鎖定會多一個要維護的規則包名單 |

refuted: none
