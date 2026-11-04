preflight-4: ran

# r1 收貨紀錄(Android的detekt規則說實話)

前案 detekt協程規則真的在跑 r1 判重寫(使用者 2026-11-04 裁),本案是接手的新編號;前案卷證在同層 detekt協程規則真的在跑 資料夾。

## 前掃(sonnet 一席,固定四項)

①②③與存在類:直接修真檔,不算 findings。
- ①共用設定沒寫檔名 → 〈用詞〉補「共用設定」一條;「要型別資訊的規則」改成「預設開、共用設定開、或本案補開」;吞取消訊號版本限制前後說法不一致 → 〈判定依據〉補一行講清楚 2.0.21 響、2.3.21 不響。
- ③補開兩條講不清楚是新增還是改 → 範圍與回退改寫;格式部分壞掉時合法項照判 → 判定表〈宣告格式壞掉時〉改寫;`--json` 未宣告路徑沒有新欄位 → 範圍寫明。

## 語意類命中(修改前→後)

1. PRIOR-ART② 誇大 shlex 先例。前:「本 repo 處理使用者指令字串的既有做法也是 shlex」;後:「本 repo 拆掛鉤命令時用過 shlex 拆詞,lint 命令本身照舊交給 shell 執行,這裡只拆來判讀、不改命令」。
2. Gradle 任務判定把自訂任務(如 detektAll)誤判成有型別。前:「名字是 detekt 接一個大寫字母開頭的後綴…判成有型別任務」;後:只認 detektMain、detektTest 與以 Debug/Release/UnitTest/AndroidTest 結尾的變體任務,baseline 與產設定任務不判,其餘判成「認不得」並新增提醒 G2。
3. T3 只列長參數的等號寫法,實測短參數 `-i=`、`-cp=` 也拒跑。前:列五個長參數;後:「detekt 參數表裡任一個長或短參數名,緊接 =」。
4. 健檢提醒段數:warn 帶空清單會讓結尾提醒段數多一,補註「這是預期」。

沒有動到核心裁定。

## r1 收貨(四席,全為 sonnet,同一家模型)

機械三道:引句——正確性、邊界、架構全數錨定;接手 9 句有 1 句錨不到(#4「推送前的新增告警閘會真的執行它們」,它引的是程式訊息不是計劃,已機械重現,見下表)。refcheck 全部存在(ok 7/11/13/29)。正規化:接手 9 處、架構 3 處把等級搬成獨立行。

## 編排者重現(HIT/MISS)

| 發現 | 重現 | 結果 |
|---|---|---|
| c1/b1/a2 佔位符守衛白名單 | 讀守衛測試的白名單與斷言;正確性席另在副本實跑翻紅 | HIT |
| b2/c3 看不到完整參數 | shlex(posix、只拆 `;&|`、whitespace_split、commenters 空)拆 `detekt --classpath $(cat cp.txt) --input a` → `$(cat` 留在同一詞;`detekt @args.txt` → `@args.txt` 獨立一詞 | HIT |
| c2/b3 shlex 設定 | 同上設定拆中文路徑、`html:r#1.html`、`:app:detekt` 都保持完整 | HIT |
| h3 健檢舊訊息打架 | 健檢 F 段印「推送前的新增告警閘會真的執行它們」(程式訊息原文) | HIT |
| h5/c8 ForbiddenMethodCall 要全名 | 兩席各自實跑,裸名不響、全名響 | 採信(兩席獨立一致) |
| c7 版本邊界 2.2.0 | 編排者先前實測 2.0.21 響、2.3.21 不響,與正確性席逐版結果一致 | HIT(兩點) |
| h8 相對路徑 classpath 位置 | 未重現,接手席單席實測 | 採信(只進天花板,不影響判定) |
| 其餘 | 規格缺漏類,讀凍結快照即可確認缺 | HIT |

## 先查世界

PRIOR-ART: 拆詞——Python 官方 shlex 文件:`whitespace_split=True` 時 wordchars 無效、`punctuation_chars` 只能建構時給、`shlex.split()` 會把 commenters 設成空(https://docs.python.org/3/library/shlex.html);本機實測照此設定拆十種寫法。採用。
PRIOR-ART: Gradle 帶值選項——Gradle 命令列說明(man page:https://manpages.ubuntu.com/manpages/jammy/man1/gradle.1.html)列 -x、-I、-p、-P、-c、-D 等帶值選項;清單照它與現行 Gradle 文件列舉。採用。
PRIOR-ART: 看不到完整參數就不判缺——跟 react-doctor、Vercel 那類「保守、寧漏不誤報」的判準同方向(見調研筆記);沒有找到專門判 shell 字串裡工具參數的現成函式庫(bashlex 不是標準庫,零依賴家規不採)。

## 依根因分組與去向(全折,無放行、無駁回)

1. 佔位符守衛:c1、b1、a2 → 範圍改成抽共用小函式進白名單。
2. 看不到完整參數:b2、c3 → 判定表第 6 步。
3. 拆詞設定與退化寫法:c2、b3、c4、b5 → 判定表拆詞 1–5 步、取值越界、S1 案例清單。
4. Gradle:c5、b6 → 帶值選項清單、任務名優先序;P2 改看段。
5. 輸出形狀:b4、a1 → 提醒文字單一張表、不回顯命令、三段式、健檢合成一段最多 20 條。
6. 知識同步:h1、h2、h3、h4、h6、h7、h9、a3 → 清單逐處重寫、健檢舊訊息改、REVISIT 綁另案狀態、lands_in 補兩篇。
7. 共用設定可靠性:h5、c8 → 新條款 S4 自動檢查、全名與規則集寫死。
8. 事實修正:c6、c7、h8 → 判定依據、T1 文字、天花板。

## 鏡像核對(折入後,sonnet 一席只看本輪 diff)

找到 5 處段落沒跟上,已修真檔:不做與範圍對新增告警檢查的說法、回退漏列新項目、RedundantSuspendModifier 的分類前後相反、PRIOR-ART「不新建機制」過頭與出處、自寫腳本同時在表外與表內;另把實務隱患的 RETIRE-IF 與 REVISIT 條件對齊。
