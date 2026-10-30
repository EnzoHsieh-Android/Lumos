# r1 收貨與修補紀錄(code-Android目標架構產生器)

兩席(正確性-sonnet、架構對齊-sonnet)報告從逐字稿原樣存檔;report-normalize 不用改;quote-check 兩份全錨;refcheck 全對得上;seat-check 只提醒「報告沒提到 patch 檔名」(觀測不擋)。
架構對齊席的兩個 ⚠(目標架構範本家族兩種機制、佔位字替換另疊一層)判不成 finding:前者是計劃〈做法〉1 明定 Android 用產生器、其他兩份照抄;後者行為需求不同(表外佔位字要拒絕)。

處置:F1–F6、A1 全折,沒有放行、沒有駁回。

## 依根因分組與出處清單(修前先列)

### G1 lumos、產出的 Kotlin 與架構對齊審查三方判法分岔(F1、F4;F2、F3 同族另列)
出處:
- 舊檔清單收哪些檔:`scripts/lumos` 的 `_arch_tpl_legacy`(原本自訂排除三種測試目錄)↔ 架構對齊分目標節點的 `_arch_code_file`、`_arch_target_rule_index`。
- 範圍判斷:資料檔 `inScope`(new-only、all 兩塊)、`relPath`、`scopeDirs` 的 NFC。
- 說法:計劃〈做法〉4、條款 S3、`Systems/android-arch-template` 舊檔清單那段、技能文件〈舊檔清單與 none 的分工〉、計劃審計紀錄第二部分實作那條的解讀①。
repair:範圍內 androidTest、testFixtures 的舊檔要進清單(`t_arch_template_android_legacy_modes` 逐支期望+「在清單上⇔架構對齊會命中」對照);Kotlin 判範圍那幾行釘原文(`t_arch_template_android_konsist_legacy_shape`)。
preserve:鄰目錄 cartx 不進清單、NFD 檔名轉 NFC、方括號星號照字面、legacy=all 不產清單(同一支 S3 測試);macrobench-lab 實跑 new-only 舊檔照舊、新檔紅、刪行畢業(驗證紀錄)。

### G2 Kotlin 字串樣板(F2)
出處:資料檔裡唯一把外部字串塞進 Kotlin 字串的是 `{{SCOPE_LIST}}`;`{{ROOT}}` 已由 `--root` 的套件名正則擋掉 `$`;節點那邊是 Markdown 不受影響。
repair:`--scope feature/$gen` 產出 `listOf("feature/\$gen")`。preserve:一般範圍原樣(S8 的 scopeDirs 常數檢查)。

### G3 舊檔清單讀法寬鬆(F3)
出處:資料檔 `readLegacyFiles`;lumos 端 `_arch_legacy_at` 走嚴格 JSON;技能文件〈改主意怎麼做〉的「舊檔重構完」。
repair:尾逗號在 Kotlin 那邊也紅(macrobench-lab 實測,見驗證紀錄);測試釘「兩字串之間要逗號」與 skipSpace 不吃逗號。preserve:正常清單照讀(macrobench-lab 重跑紅綠跟原本第 3 步一致)。

### G4 開關語意(F5)
出處:資料檔 usecase=required 與 optional 兩支 ViewModel 測試。repair:required 版也擋 RepositoryImpl、DataSource、Dao、Api(`t_arch_template_android_switch_effects`)。preserve:optional 版不擋 Repository 結尾。

### G5 重複與沒用到的程式(F6、A1)
出處:`_arch_tpl_scope_error` 與共用的 `_config_glob_error`;`_ARCH_TPL_TEST_TAG_RE` 全檔只有定義。repair:改先呼叫共用檢查,刪掉沒用到的正規式。preserve:S4 逐案拒絕原因(空、空白、./、/、反斜線改成同一句;其餘各自一句)。

## 修補驗證(修前紅、修後綠)
原始輸出另存 `r1-repro.txt`。逐條拿掉修正跑對應測試:F4、A1、F5、F1(斜線邊界)、F1(NFC)、F3、F2 七種改回修前寫法各自紅,還原後綠。修補與拆函式沒有混在一起:拆函式(過新增告警閘)在第一輪派審前就已併進功能提交。
效能:一萬支檔的範圍跑 `--print legacy` 0.96 秒、常駐記憶體約 350MB(大多是載入主程式)。
