# code-Android測試防竄改檢查 r4 收貨紀錄

- 這是使用者在上限裁定題選「加一輪」之後的第四輪(上限裁定與跑滿回顧已記帳,回顧在同目錄 cap-retro.json)。
- 修補鏡頭:修前 22cc66758a71106cbad9cf9322ad5f689e93cd8a → 修後 fcd274397508ae886482cd39ea9e14f677bacefd(r3-dispatch.json 的 base_commit 與 r3 審材的生成範圍一致;祖先關係成立)。來源與只歸檔清單:r4-repair-binding.json。
- fix-check(r3):全部通過(171.1 秒,修正前 22cc6675 → 修正後 fb5a22f2);它點名重跑的殺傷力配方 Systems/canary-audit#259cf76bb8ae 重跑仍 killed
- 審材:完整改動 r4-snapshot.patch(047031883..fcd27439,範圍同前三輪,資安席讀這份);修補差異 r4-repair-review.patch(去掉只歸檔的卷證與帳本)拆成 r4-repair-code.patch、r4-repair-tests.patch、r4-repair-docs.patch;另附完整程式改動 r4-code.patch。

## 這一輪的做法(跑滿回顧的兩條改法先在這輪自己照做)

- 收窄或改寫判讀規則前,先把修前抓得到的同族寫法列成保留案例寫進測試;這輪修的三處回歸(點名測試任務、catch 豁免、類別本體)都回到寬判法再在外面排除明確的誤報。
- 效能修補的測試都附前置斷言證明樣本走到被改的程式;上限只量實體行這件事照實寫,另外三種乘積形狀(區塊開頭乘行數、續行邏輯行乘命中數、巢狀深度乘路徑長)各造一個最壞輸入。

## 配對案例(待驗範圍,不是已修好的證據)

| 組 | repair(原問題) | preserve(要維持的既有行為) | 兩版證據 |
|---|---|---|---|
| G1 收太窄回到寬判法 | findByName、`tasks[…]`、getByPath、`it.name ==`、withType<Test> 裡巢狀 if、換行的 matching 鏈結、同一行帶 jacoco 字樣的 tasks.test、named<Test>("jacocoTest")、測試區塊加 excludeTags 要列;try 補 fail 而 catch 只印出或空的要列;父型別換行、建構子跨行再接父型別、Java extends 換行時類別路徑在 | JaCoCo 兩種 exclude、fileTree 與依賴的 exclude、detekt(含單行、configure<DetektExtension>、內層 reports)、kotlinter、任務的 dependsOn("testX") 不列;預期例外寫法(try 結尾 fail、catch 接特定例外)、catch 斷言型別、catch 重丟不列 | r3-repro.txt(修前紅);修後 `-k tq_guard` 全綠 |
| G2 乘積形狀 | 250 行沒收尾的泛型(約 5 MB)5 秒內;2 萬字區塊開頭配 1 萬 5 千行 10 秒內、候選身分不帶整條開頭;1 MB 續行父層配 3000 個放寬鍵 10 秒內;2 萬層巢狀類別 5 秒內、記憶體峰值 200 MB 內 | 前三輪 S11 的大輸入 | 同上;編排者量測見下〈作者自驗〉 |
| G3 上限的範圍 | 正式程式檔有超長行不列太大;測試檔有超長行列太大、同檔加的跳過照樣列;CRLF 剛好 2 萬字不算 | 單行 10 萬個中綴列太大、5 秒內 | 同上 |
| G4 敘述身分 | 多行 assume 改成 false、changeThreshold 的值換行寫調高要列 | 同一個 assume 只換行重排、只改 assume 同一行的斷言不列;8 萬個 assume 30 秒內 | 同上 |
| G5 CI | -xtest、--exclude-task=test、子殼層與 $() 與轉向黏著的任務被拿掉、`|| exit 0`、`|| echo` 要列 | 檔名 build.gradle 後接 `|| echo` 不列;加 -x lint、拿掉 --tests 與 -P 參數、拿掉 -x test、非 Gradle 段的 test 不列 | 同上 |
| G6 閘與放行 | LUMOS_SKIP_LINT_NEW=0/false 不關閘;git 讀不出內容記成沒跑完;設定 off 加比對出錯留帳;自動放行原因跟說明同一句;--list 清外來文字;健檢標籤含比對出錯 | 前三輪 S12–S15 案例 | r3-repro.txt;修後 `-k lint_new`、`-k lint_waive` 全綠 |

## 作者自驗(派審前)

- 改壞檢查:這輪新寫的判斷逐道在原檔改壞一處跑對應測試(會談暫存區 mutate4.py,改前清編譯快取、跑完比對指紋還原),33 處全部翻紅;第一次有兩處沒紅(下一個停點的快取、自動放行的原因),補了 250 行泛型的計時測試與原因相等的測試後翻紅。另外三處改壞(類別路徑存祖先、Gradle 呼叫判法放寬、建置檔測試迴圈)也各自確認會紅。
- 效能與記憶體(每種輸入各自一個行程,_tg_analyze 耗時/行程峰值):8 萬行測試檔(每行一支有斷言的測試,約 4 MB) 2.71 秒/375 MB;3000 層巢狀括號的斷言 0.06 秒/39 MB;5000 層巢狀 try 0.16 秒/45 MB;接近單行上限的長行 200 行(每行 19,990 字的中綴斷言) 2.66 秒/120 MB;4.9 MB 單檔(大量同名多載) 3.21 秒/182 MB;250 行沒收尾的泛型(約 5 MB) 1.29 秒/75 MB;2 萬層巢狀類別 0.14 秒/49 MB;建置檔:2 萬字的區塊開頭配 9 萬行內層 0.55 秒/62 MB;CI:1 MB 續行父層配 4 萬個放寬鍵 0.58 秒/83 MB
- 8 萬行測試檔的行程峰值比上一輪量的高,另用 tracemalloc 只量比對本身,兩版都是 86 MB,差在行程層面的量法,不是這輪變胖。
- 考場重跑:真實歷史 776 個提交 44 條候選,跟上一輪逐條相同(中途一版多了 1 條 `build.gradle || echo` 的誤報,查出是判斷「有沒有叫 Gradle」把檔名當成呼叫,已收窄並補測試);對照表 21 筆跟上一輪相同。
- ruff(專案宣告的規則組)跟修前比沒有新增告警(中途兩條函式太複雜,已拆小函式)。

## 機械收貨

- report-normalize:7 份都已正規化。
- quote-check(對 r4-snapshot.patch):6 份全錨;邊界席 #5、#6 錨不到,機械重現見下表。
- refcheck:全部對得上。

| id | 引句 | 重現 | 結果 |
|---|---|---|---|
| b5 | (memo 只存被查過的那個節點 | `grep -c "memo 只存被查過的那個節點"` 於 r4-snapshot.patch → 1(引句開頭多一個左括號,原文在) | HIT;每層一支測試的深巢狀另由資源席、通才席獨立量到 |
| b6 | heads.append(stack[-1] if stack else "") | 引的是修前版本的程式;直接載入修後程式跑 `_tg_build_hits`:`systemProperty("json", "{")` 之後的 `lint { enabled = false }` 列 tq/build-config(誤報),`println("}")` 之後的 `enabled = false` 不列(漏報) | HIT |

## 根因分組(id = 席代碼 + 報告序號:c 正確性 6、b 邊界 10、r 資源 6、g 通才 7、k 合約 8、a 架構對齊 5、s 資安 5,共 47 條,席位標 major 18 條)

| 組 | 根因 | id | 性質 |
|---|---|---|---|
| ①點名判法改成「引號整個是任務名形狀」太窄 | 字串模板的任務名(`"test${v}UnitTest"`)不認 | c1 b1 s1 | 修補回歸(major) |
| ②區塊開頭只看第一個 `{` 之前 | 一行開兩個區塊漏判與誤判;`} else {` 被當鏈結;外層測試區塊向內傳到 reports、jacoco;flavor 名含 test | c2 c3 b9 g7 | 修補回歸(c2 major) |
| ③非線性正規式加上拿掉建置檔與 CI 的單行上限 | `|| echo`、引號任務名、`dependsOn\s*\(?\s*`、前導空白,病態行平方級回溯 | r1 r2 g1 c5 | 修補回歸(major) |
| ④每層一支測試的深巢狀 | 函式鍵本身是整串類別路徑,總長深度平方 | r3 b5 g2 | 原有漏查,只修了葉子形狀(major) |
| ⑤新加的 excludeTags 只認括號寫法 | Groovy `excludeTags 'slow'`、`+=` | k1 b3 | 修補缺口(major) |
| ⑥鏈結寫在以 `.` 開頭的下一行 | `tasks.withType<Test>()` 換行 `.configureEach {` | b2 | 原有漏查(major) |
| ⑦判斷有沒有叫 Gradle 的 lookbehind | 路徑形式 `/opt/gradle/bin/gradle` 漏;`gradle.properties`、`gradle/wrapper` 誤報 | b4 g6 | 修補回歸(b4 major) |
| ⑧敘述擷取 | 自寫括號深度(第二種做法);字串裡的括號配進深度;去掉全部空白抹平字串常值的差異 | a3 c6 b7 s2 | 修補回歸(a3 major) |
| ⑨文件 | 計劃做法一仍寫 include_local=True;catch 規則表與標準沒跟上;CI 的 -x 沒切段;太大訊息自相矛盾;「任務名形狀」實際只看 test 子字串;skip 規則表;驗證紀錄沒回寫 | k2 k3 k4 k5 k6 k7 k8 | k2 major |
| ⑩測試鑑別力 | --list 只測理由一欄;自動放行四個呼叫點只測一個;一批新分支改壞仍綠 | g3 g4 g5 | g3 major |
| ⑪其餘 minor | Kotest 中綴在 catch 裡、讀檔路徑沒有大小上限、常數命名、摘要演算法、自動放行第二寫入點、堆疊元素記憶體、catch 切片、重試讀檔、字串大括號、重試路徑引號、覆蓋面、超長行藏作弊、CR 結束註解、敘述 2000 字上限 | c4 a1 a2 a4 a5 r4 r5 r6 b6 b8 b10 s3 s4 s5 | minor |

## 修補因果核對(第三輪修補 22cc6675 → fcd27439 造成的)

依各席兩版實跑的歸因欄;架構對齊席不寫歸因,由編排者對照 r4-repair-code.patch 判(a1–a5 指的都是這輪新寫的程式)。

- 修補回歸:c1 c2 c3 c4 c5 c6 b1 b3 b4 b6 b7 b8 b9 r1 r2 r4 r6 g1 g6 g7 k3 k5 s1 s2 a1 a2 a3 a4 a5(c5、b6 只有一半是回歸:c5 的前導空白那條、b6 的字串右大括號漏報是原有;b3 是這輪新規則只補了一種寫法)。
- 原有漏查:b2 b5 b10 r3 r5 g2 g3 g4 g5 k1 k2 k4 k6 k7 s3 s4 s5(r3、b5、g2 是上一輪只修了葉子形狀)。
- 未判定:k8(驗證紀錄沒回寫重跑結果;席位沒重跑私有專案,只確認筆記沒更新)。

## 處置(使用者 2026-11-02 裁定「縮範圍再審一輪」)

建置檔與 CI 兩類規則移出這一批:程式拿掉 tq/build-config、tq/ci-config、建置檔的逾時與門檻比對,寫進計劃〈第二批〉另做。這兩類的發現以「拿掉這段程式」折入(那段程式不再存在,發現隨之解除):c1 c2 c3 c5 b1 b2 b3 b4 b6 b8 r1 r2 r4 r6 g1 g6 g7 k1 k4 k6 s1 a1。測試檔、閘與文件的發現照常修。

- 折入:除下列放行外全部,major 一律折。
- 放行(原報 minor,逐條指回席報告原條):
  - s3:測試檔超長行抹掉後另列一條太大,是使用者已接受的上限取捨;要藏作弊得刻意製造 2 萬字的行,而且還是會被擋下一條要人放行。
  - s4:用單獨的 CR 或 Java 的 \u000a 提前結束註解,屬刻意偽造語法,兩版相同;寫進抓不到清單。
  - a5:分類函式那處是「檢查命令跑不動」的另一種自動放行,語意不同,讀取端已統一只看 autopass_reason。

## 停在這裡之後

照使用者裁定,先記這一輪的帳,再縮範圍、修測試檔剩下的兩組 major,派一輪只看縮小後差異的審查。
