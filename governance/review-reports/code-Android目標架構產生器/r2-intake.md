# r2 收貨與修補紀錄(code-Android目標架構產生器)

三席:正確性A-sonnet(程式包 r2-packA.patch)、正確性B-sonnet(測試文件包 r2-packB.patch)、架構對齊-sonnet(程式包)。報告從逐字稿原樣存檔。
收貨時兩處格式問題請原席只改那一處重交、其他一字不動:A 的總結行寫了「blocker 0、major 0」(report-normalize 判總結藏更高等級);B 的 F14 引句把半形逗號分號轉成全形(quote-check 錨不到)。重交後三份都正規化、全錨;refcheck 全對得上。
ID:A 席 F1、F2;B 席 F11–F15;架構對齊席 A11。同一輪內不撞號(F1、F2 跟 r1 的同名 ID 是不同輪)。

處置:折 F1、F2、F11、F12、F13、F14、F15;放行 A11。
- A11 放行理由:`_arch_tpl_fill` 跟 `_note_template_fill` 的行為需求不同(表外佔位字要拒絕,不能原樣漏進產出),載入與佔位字正規式都共用同一份,沒有另一套讀範本或另一個正規式;席位自己也標判不準。

## 修補因果(--regression-set)
- F1(A)與 F13(B)是同一件事、兩席獨立報:r1 修補把清單改成只照 `_arch_code_file`,`src/main` 底下路徑有 test/ 段的正式 .kt 從清單掉出去,Konsist 照掃。兩席都用同一個輸入跑過修前(8a601700,清單收)與修後(2f1b1840,清單不收)。判:有證據的修復回歸。
- F11:修前根本沒有逗號檢查,修後的文字比對擋不住兩種改壞(B 席兩版實跑)。判:原有漏查(r1 的修補沒補到行為證據)。
- F2、F12、F14、F15:兩版都有,判原有漏查。

## 依根因分組與出處清單(修前先列)
### H1 Kotlin 讀清單沒有行為證據、而且比 lumos 寬(F11、F2)
出處:資料檔 `readLegacyFiles`;lumos 端 `_arch_legacy_at`(標準 JSON);技能文件〈舊檔清單與 none 的分工〉、〈改主意〉;`Systems/android-arch-template` 讀清單那段。
修法:改兩條只用 Java 與 Python 同義語法的正規式;測試把原文從產出抽出來在 Python 實際跑。repair:尾逗號、前逗號、少逗號、少括號、多欄位、巢狀、跳脫、控制字元、非字串、不換行空白、尾巴多字一律不認;Kotlin 讀得進去的,json.loads 一定讀得進去而且同一份。preserve:空陣列、CRLF、BOM、方括號星號、NFD 讀得進去(t_arch_template_android_konsist_legacy_shape);產生器寫出的清單讀得進去(t_arch_template_android_legacy_modes);macrobench-lab 正常清單、空陣列照讀,尾逗號紅。
### H2 清單收檔跟架構測試掃描範圍分岔(F1、F13)
出處:`_arch_tpl_legacy`;Konsist 0.17.3 `KoScopeCreatorCore.isTestSourceSet`(反組譯:原始碼集名稱轉小寫含 test);計劃〈做法〉4 與 S3、`Systems/android-arch-template`、技能文件。
repair:`src/main/java/mysrc/test/Q.kt` 回到清單、`src/integrationTest/...` 收。preserve:`src/test` 與 `.md` 不收、androidTest 與 testFixtures 照收、cartx 不收(同一支 S3 測試;「在清單上」⇔「架構對齊會審或架構測試會掃」逐檔對照)。
### H3 測試只看名字(F12)
出處:switch_effects 的 required 那條斷言。repair:釘 `dataSuffixes.any { type.endsWith(it) }`。preserve:五個結尾名照查。
### H4 文件(F14、F15)
出處:技能文件〈改主意怎麼做〉;舊計劃 S1、S3 條款句與補註。repair:補 all 改 new-only;條款句改寫成產生器那組的產出。preserve:綁定測試名不變(t_arch_target_android_template_valid、t_arch_target_android_template_konsist_names_match)。

## 修補驗證(修前紅、修後綠)
原始輸出另存 `r2-repro.txt`。
