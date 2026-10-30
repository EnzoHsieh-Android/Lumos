# r3 收貨與修補紀錄(code-Android目標架構產生器)

三席:正確性A-sonnet(程式包 r3-packA.patch)、正確性B-sonnet(測試文件包 r3-packB.patch)、架構對齊-sonnet(程式包)。報告從逐字稿原樣存檔。
收貨時 B 席 F33 的引句把兩行接成一行(quote-check 錨不到),請原席只改那一處重交。
ID:A 席 F21–F24;B 席 F31–F33;架構對齊席 A21、A22。

第三輪是 standard 上限,本輪仍有 major(F21、F31),2026-10-30 使用者裁「加開第四輪」(cap-decision extra-round)。

## 編排者機械重現
- F21:本機 JDK 17(`java R.java`,原始碼與輸出在 r3-repro.txt)把資料檔 legacyDoc 原文抽出來跑一行一條的清單:1000 條 true、3000 條與 50000 條 StackOverflowError。HIT。同一條正規式把外層重複群組改成佔有式 `*+`:三種條數都 true。
- F22 / F32(同一件事、兩席獨立報):Java 的 `$` 在非 MULTILINE 下會停在最後一個行終止符(含 U+0085、U+2028、U+2029)之前,Python 的 `$` 只認 `\n`;兩席各自用 JDK 17 實跑過。修法改用 `\A`、`\z`(Python 3.14 起支援 `\z`,工具鏈最低版本就是 3.14)。
- F31:測試的必拒清單沒有「開頭有雜字」的輸入,巢狀那條被結尾的 `}` 擋掉,開頭的 `^` 拿掉照綠。照讀報告可直接確認。HIT。

## 修補因果(--regression-set)
- F21:r2 的修補把逐字元讀法換成整份一條帶重複群組的正規式,Java 引擎對重複群組逐層遞迴;修前逐字元讀法沒有條數上限(A 席用 Java 移植版跑 5 萬條成功)。判:有證據的修復回歸。
- F22 / F32:正規式是 r2 新寫的,但修前的逐字元讀法更寬(讀到第一個 ] 就返回)。保證文字(只會比 lumos 嚴)是 r2 新寫的。判:F32 有證據的修復回歸(保證不成立),F22 原有漏查。
- F31、F33、F23:r2 新寫的測試覆蓋不完整,修前沒有行為測試可比。判:原有漏查。
- F24、A21、A22:跟 r2 修補無關的原有程式。判:原有漏查。

## 依根因分組與出處清單(修前先列)
### J1 Kotlin 讀清單的正規式:Java 與 Python 只做到語法同義,資源行為與錨點語意不同(F21、F22、F32、F31、F33)
出處:資料檔 `readLegacyFiles` 的兩條正規式與 BOM 處理;測試 `_arch_tpl_kotlin_legacy_reader` 與 S8 的必讀、必拒清單;資料檔註解;`Systems/android-arch-template` 讀清單那段;驗證紀錄。
修法:外層重複群組改佔有式 `*+`;錨點改 `\A`、`\z`;BOM 放進正規式(`\A﻿?`),Kotlin 不另外剝;測試照 Kotlin 原樣跑(不在測試端剝 BOM);必拒清單補開頭雜字、檔尾 U+0085/U+2028/U+2029;本機或 CI 有 java 時,另用 Java 實跑同一條正規式(大清單 5 萬條、各種必讀必拒),沒有 java 就印一行跳過。
repair:3000 與 5 萬條讀得進去;`x{"files": [...]}`、檔尾 U+2028 不認;帶 BOM 讀得進去。preserve:空陣列、CRLF、方括號星號、NFD 讀得進去;尾逗號等既有必拒照拒;產生器寫出的清單讀得進去。
### J2 清單收檔的 Konsist 判法沒照它的實際算法、測試資料少一型(F23)
出處:`_ARCH_TPL_KONSIST_TEST_RE`、`_arch_tpl_legacy_file`;測試 `konsist_scans`。
修法:照 Konsist 0.17.3 的算法(取路徑第一個 `/src/` 之後到下一個 `/` 的那段當原始碼集名稱,轉小寫含 test 就是測試)改寫;測試的對照判準改用不同寫法(切段)獨立寫;測試資料補 `src/androidTest/java/x/test/H.kt`(兩邊都不看,不收)。
### J3 規則跟綁的測試範圍不一致(F24)
出處:資料檔 domain 純 Kotlin 那條 RULE 與 `domainHasNoAndroidImports`。修法:測試另擋 retrofit2、kotlinx.serialization、Moshi、Gson、Jackson 的 import;測試釘這幾個前綴。
### J4 重複寫法(A21;A22 放行)
A21:`cmd_arch_template` 找 repo 根改呼叫既有的 `_lens_repo_root`。
A22 放行理由:Konsist 判測試原始碼集的規則跟既有兩套(`_rg_is_test_path`、`_e2e_default_excluded`)本來就不同,這條是照 Konsist 本身的算法鏡像,併進既有任一套都會改到那邊的判定。
