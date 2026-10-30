# r4 收貨與修補紀錄(code-Android目標架構產生器)

三席:正確性A-sonnet(程式包 r4-packA.patch)、正確性B-sonnet(測試文件包 r4-packB.patch)、架構對齊-sonnet(程式包)。報告從逐字稿原樣存檔。
收貨時架構對齊席 A41 的引句用反引號包(quote-check 抽不到),請原席只改那一行重交;重交後三份都正規化、全錨。
ID:A 席 F41–F43;B 席 F51–F53;架構對齊席 A41。

第四輪是使用者加開的一輪,仍有 major(F41、F51,同一件事兩席獨立報)。2026-10-30 使用者裁「全修後接受風險進推送」(cap-decision accept-risk),不再派第五輪。

處置:全折,沒有放行、沒有駁回。

## 修補因果(--regression-set)
- F41 / F51(同一件事):r3 把 Konsist 判法改成「第一個 /src/ 之後那段」,程式改對了(兩席都用同一個輸入跑過修前漏收、修後收),但測試資料沒有一筆能分辨新舊寫法,改回舊寫法照綠。產品行為不是退化,是 r3 修補沒補到分辨力。判:原有漏查。
- F42:沒有 /src/ 的路徑,r3 的函式取第一段,Konsist 實際是空字串(A 席反組譯 KoSourceSetProviderCore 查證);修前的正規式在這種路徑判不是測試,修後判成測試、從清單掉出。判:有證據的修復回歸。
- F43:r3 新加的 Java 實跑用了 Java 17 才有的 HexFormat,JDK 11 上修前全綠、修後紅一條(A 席實跑)。判:有證據的修復回歸(測試基礎設施)。
- F52:r3 新加的 Java 實跑在 java 存根上紅、逾時被當成沒有 java(B 席用假 java 實跑)。判:有證據的修復回歸(測試基礎設施)。
- F53:技能文件那句修前就有;判原有漏查。A41:r3 新寫的提示格式;判原有漏查(格式,不是行為)。

## 依根因分組與出處清單(修前先列)
### K1 Konsist 判法沒照它的實際算法、測試沒有分辨力(F41、F51、F42)
出處:`_arch_tpl_konsist_test` 與它的說明;測試 S3 的檔案清單與 `konsist_scans`;`Systems/android-arch-template` 舊檔清單那段。
修法:沒有 /src/ 時名稱是空字串、冒號取第一個之後;測試清單補 `src/main/java/x/src/test/Z.kt`(新算法收、舊正規式漏);直接問判斷函式六個案例(兩個 src/ 段、沒有 src/、兩種冒號位置、androidTest、src/ 後面的 test 段);對照判準同步改。
### K2 Java 實跑的環境判斷(F43、F52、A41)
出處:測試的 `_ARCH_TPL_JAVA_READER`、`_arch_tpl_java_legacy_read` 與 S8 跳過提示。
修法:Java 程式改用 Java 11 就有的 API;先跑 `java -version`,跑不起來才算沒有能用的 java(印「這次沒驗到」);之後編譯、執行失敗或逾時都回失敗讓斷言紅;提示照專案既有「⚠ … 沒驗到」的格式。
### K3 文件(F53)
出處:技能文件〈Konsist 那一半〉最後一條。修法:改成純 Kotlin 模組時 Android 部分由編譯器擋,但這支測試還擋 Retrofit 與序列化框架,不要拿掉。
