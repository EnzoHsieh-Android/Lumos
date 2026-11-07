# r1 收貨紀錄(code-android情境題與表態對程式)

## 收貨

- 第 1 輪,high(`pitfalls --diff 87c825676..0ea5f2e2d`:複雜度告警數字變動被新增告警閘認成新增;本案改推送前表態判定,屬守衛面)。整份凍結 r1-snapshot.patch 2102 行(sha256 1795a915…,不含卷證),拆甲(scripts/lumos 988 行)、乙(測試 608 行)、丙(型錄、check.py、筆記 506 行);正確性、資源、邊界、通才看甲乙(1596 行),接手、架構對齊看甲丙(1494 行),資安看整份。七席全 sonnet;外家預設不派,結論寫成「單家族視角下」。
- 七份從逐字稿存檔,正規化格式;quote-check:接手那份有引句錨不到(引的是型錄列文字,佐證走實跑重現,照採);其餘全錨。refcheck 全 ok。席位沒改 repo,審查席臨時目錄已刪。

## 重現表(席位多已實跑,以下為編排者抽驗與席位原輸出)

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 一接1 | 接手 F1 | `Box(Modifier.clickable { onClick() }.padding(8.dp))` 以 D-34 main 答 | HIT(席位原輸出):被擋;型錄 D-52 自己的標準寫法就是尾隨 lambda |
| 一接4 | 接手 F4 | CO-8 壞寫法(try 包在 coroutineScope 裡)以 D-8 main 答 | HIT:放行 |
| 一正1 | 正確性 F1 | 檔內函式前有 `data class Item(val id: Int)` | HIT:段材料縮成兩行、標準寫法被擋 |
| 一正2 | 正確性 F2、通才 F3 | 把 scripts/lumos 複製進消費專案跑 pitfalls | HIT:型錄讀不到、情境題整題消失 |
| 一通1 | 通才 F1、正確性 F3、邊界 F5、資安 F2 | `_kt_sit_verdict_one(".", "nonexistent..HEAD", None, ent, {})` | HIT:回 None(放行) |
| 一安1 | 資安 F1、通才 F2 | 殘留 `LUMOS_KT_CATALOG` 指到小型錄 | HIT:推送前情境題整題消失、不印提醒 |
| 一邊1 | 邊界 F1、架構 F2 | `git config diff.interHunkContext 10`、`diff.noprefix=true` | HIT:段被吃掉或全部消失 |
| 一架1 | 架構 F1 | lumos `_kt_dt_*` 與 check.py `dt_*` 對讀 | HIT:兩套讀表,必有欄數不同(6 對 8) |
| 一資1 | 資源 F1 | 300 支 kt 檔各 300 行 | HIT(席位原輸出):pitfalls 多 39 秒,一次推送重算多遍 |

refuted: none

## 先查世界

- PRIOR-ART: 證據樣式(作者自寫的正規式)既擋掉型錄自己的標準寫法(D-34、D-23、D-47、D-21、D-1、D-20)又放過壞寫法(D-8、D-10、D-16)——同一類字面判斷打穿。業界寫規則一律附正反範例自測:ast-grep `test` 把每條規則的 valid/invalid 範例分成 validated、noisy(誤報)、missing(漏報)、reported 四類(https://ast-grep.github.io/guide/test-rule.html );Semgrep 用 `ruleid:` 防漏報、`ok:` 防誤報(https://docs.semgrep.dev/writing-rules/testing-rules )。採用:每列證據樣式要附正例(該列標準寫法、例外寫法的範例程式)與反例(對應檢查列的壞寫法範例),由型錄自檢經真實的切段與核對程式跑過——正例要放行、反例要擋;做不到的那條改 `(無)` 交盲判,不留「可能擋掉標準寫法」的樣式。排除:靠人逐列看樣式(這輪 56 列裡 9 列出錯)。
- PRIOR-ART: 誤擋沒出口——計劃範圍 5 的段放行原定下一次做;本輪證實誤擋確實會發生,把範圍 5 段放行(照新增告警閘 `lint-waive` 的形狀:理由、origin、ack)提前到這一次。
- PRIOR-ART: 算不出段時放行——Systems/棧別提問表態閘 既有 KEY「核對每題包例外→無法驗證擋下不 fail-open」;照它,任何計算失敗都判無法驗證擋下。
- PRIOR-ART: 型錄位置與覆寫——lumos 既有 `_lumos_src()`(LUMOS_HOME 或 ~/harness/lumos-toolchain)找工具鏈檔;測試專用覆寫只在測試執行器的隔離標記下生效(找既有標記)。
- PRIOR-ART: diff 解析——既有 `_notelines_parse_hunks` 與釘住 diff 參數的做法(`_DIFF_PIN_HUNK_ARGS`),不另寫。
- PRIOR-ART: 型錄讀表——lumos 以 importlib 借用 check.py 的讀表(既有先例:lumos 在別處 import 工具鏈其他檔),讀表只住一處。
- PRIOR-ART: 效能——字面子字串預篩後才跑逐列正規式(資源席實測 15 秒→0.8 秒)、`git cat-file --batch` 取代逐檔 git show、同一範圍與版本只算一次、核對迴圈檢查期限。

## 歸因

- 第一輪,沒有上一輪修補可回歸。

## 逐條去向(全折;實作依下列裁決,完成後逐條補實際修法)

裁決(編排者):D1 證據樣式附正反範例自測、做不到的改 `(無)`;D2 段放行提前上線;D3 計算失敗一律無法驗證擋下;D4 `LUMOS_KT_CATALOG` 只在測試隔離標記下生效,其他情況照預設並在用到時印出用哪份型錄;D5 型錄路徑走 `_lumos_src()`;D6 diff 解析沿用既有;D7 讀表只留 check.py 一套;D8 宣告頭視窗修正;D9 效能四項;D10 文件與計劃對齊、換列列改成型錄明確標記並由自檢驗;D11 問題句裡的檔名照既有消毒。

## 修補後實際去向(實作完成後補)

- 折:除下面四條外全部折入(提交 89623c4ba、e659fabf6、41a5537e7;逐條修法見提交說明與計劃〈審計修正紀錄〉)。
- 放行(原報 minor):一架4(驗證主幹寫死題號:目前只有一題形狀特別,等第三種題型出現再改題表旗標)、一架6(詞界寫法重複:庫裡沒有共用工具,抽出要動三處無關程式)、一正4(產生碼段數沒有上限:已有時間預算,超時判無法驗證且可段放行)、一資3(兩支舊測試 40–50 秒:既有狀態,非本次引入)。
- 型錄讀不到的處置:編排者依使用者授權改裁為「環境不可用、只提醒並記帳、不擋」(照新增告警閘既有 `_gate_failopen` 先例);型錄在但讀表失敗照舊擋。
