# r1 收貨紀錄(code-選擇點存活回指第一段補修)

材料:r1-snapshot.patch(20ac8f996..a8c4c069c,-U10,925 行,sha256 90c85110b02ed9e515562592488520b291c1e06bbae79daf3bd6fad8be8f04a6)。七席(正確性、資源、邊界、合約、通才、架構對齊、資安)全數交回後才一次從逐字稿存檔;report-normalize 七份都已正規化、quote-check 七份全錨。架構對齊席第一次交的第 1 條寫 severity major、blocking 否,退回該席自己重判,重交後維持 major、blocking 是,存的是重交版。

## 發現與去向

| id | 席 #條 | 原報 | 一句 | 去向 |
|---|---|---|---|---|
| c1 | 正確性 #1 | major | 舊快取只有 .exec、沒有 .base.json 的退路沒有測試;拒收分支也沒測 | 折:新增 t_choice_cov_resume_old_cache、t_choice_cov_base_read_rejects |
| c2 | 正確性 #2 | minor | 規格閘 WHY「覆蓋可信看專案類別有紀錄數」還寫舊判法 | 折:summary-line 改寫 |
| c3 | 正確性 #3 | minor | Robolectric 環境類別在 includeNoLocationClasses 沒生效時可能也記不到 | 放行:延後到 Issues/選擇點存活回指第一段末輪小問題第二段先修 第 9 條 |
| r1 | 資源 #1 | minor | 走訪不限非原始碼檔、每個平台組重走一次 | 折:_KillPrep._src_pkgs 一個平台根只掃一次、另加 _CHOICE_COV_SRC_ENTRIES 上限 |
| r2 | 資源 #2 | minor | 超過 20000 支靜默截斷 | 折:看滿上限印一行提醒 |
| r3 | 資源 #3 | minor | 具名管道 x.kt 會讓 open 卡住 | 折:islink 與 isfile 檢查後才開 |
| b1 | 邊界 #1 | minor | BOM、反引號 package 讀不到 | 折:正規式收 ﻿ 與反引號、去掉反引號 |
| b2 | 邊界 #2 | minor | 跳過清單任何深度比對 test,主程式 test 套件被跳;上限靜默 | 折:_choice_cov_test_srcset 只認 src 底下的測試資料夾 |
| b3 | 邊界 #3 | minor | el 超大整數 OverflowError、NaN;基準寫失敗連帶丟掉覆蓋資料 | 折:接 OverflowError、math.isfinite、非負;store 基準另包 try |
| k1 | 合約 #1 | minor | take 說明字串還寫舊 Robolectric 判法 | 折 |
| k2 | 合約 #2 | minor | 議題 summary 還把第 1 條寫成未修、updated 沒跟 | 折:summary-line、什麼條件算修好、四篇 updated |
| g1 | 通才 #1 | minor | rc 與逾時拒收條件沒有測試 | 折:t_choice_cov_base_read_rejects |
| g2 | 通才 #2 | minor | SdkEnvironment 沒有測試 | 折:t_choice_cov_robo_exec 加 a3 |
| g3 | 通才 #3 | minor | 同 c2 | 折(同一處修改) |
| g4 | 通才 #4 | minor | 續跑快取 WHY 沒提 .base.json | 折:summary-line 改寫並綁 t_choice_cov_resume_old_cache |
| a1 | 架構對齊 #1 | major | 走訪另立跳過清單,不用共用 CODE_SKIP_DIRS | 折:_CHOICE_COV_SRC_SKIP = CODE_SKIP_DIRS 加 .gradle,測試資料夾改結構判 |
| a2 | 架構對齊 #2 | minor | 空殼判定另用 ElementTree 重剖,跟 test_quality.junit 兩套 | 放行:延後到同議題第 10 條 |
| a3 | 架構對齊 #3 | minor | 基準檔讀取自寫一套、65536 魔術數 | 折:改走 _choice_cov_read,上限取名 _CHOICE_COV_BASE_MAX |

資安席 clean,沒有條目。

## 機械重現

| id | 做法 | 結果 |
|---|---|---|
| c1 | 拿掉 cached() 的 `and base is not None`,跑 -k choice_cov_resume_old_cache | HIT:0 passed, 1 failed |
| g1 | 拿掉 `or doc["rc"] != 0 or doc["to"]`,跑 -k choice_cov_base_read_rejects | HIT:3 passed, 1 failed |
| b3 | 不接 OverflowError;拿掉 isfinite;基準寫失敗改回 None,各跑 -k choice_cov_base_read_rejects | HIT:三者各 1 failed |
| a1 b2 | 測試資料夾改回任何深度比對字面名;不認變體資料夾,跑 -k choice_cov_src_pkgs_edges | HIT:各 1 failed |
| b1 | 正規式拿掉 ﻿;不去反引號,同上 | HIT:各 1 failed |
| r2 | 拿掉上限提醒,同上 | HIT:1 failed |
| g2 | SdkEnvironment 改名,跑 -k choice_cov_robo_exec | HIT:4 passed, 1 failed |
| c3 | 推論,席自己標未能重現 | MISS:沒在實驗專案關設定實測,延後到議題第 9 條 |

## 先查世界

- PRIOR-ART:套件宣告前可以有什麼——Kotlin 文法 kotlinFile 是「可選 shebang → 檔案註解 @file: → packageHeader」,所以 package 不一定在第一行;正規式用多行模式找行首 package 就涵蓋檔案註解,另補檔首 BOM 與反引號名稱。來源 https://kotlinlang.org/docs/reference/grammar.html 、 https://kotlinlang.org/spec/packages-and-imports.html 。採用。
- PRIOR-ART:測試原始碼資料夾的慣例——Android 官方〈Advanced test setup〉:單元測試在 src/test、儀器測試在 src/androidTest,變體專屬的放 src/test<變體>、src/androidTest<變體>;所以「名字等於 test」漏掉變體資料夾,改成 src 底下 test、androidTest 開頭(加多平台慣例的 Test 結尾)。來源 https://developer.android.com/studio/test/advanced-test-setup 、 https://developer.android.com/studio/preview/test-suites 。採用。
- PRIOR-ART:走訪的跳過清單——專案內已有 CODE_SKIP_DIRS 與 _walk_test_files「走檔只有這一份」的規矩,直接疊用;不另找外部做法。
- PRIOR-ART:JUnit 空殼檔(a2)——不在這輪改;test_quality.junit 是邊讀邊數的串流讀法,要讓它回空殼旗標得改它的回傳形狀,牽動其他呼叫者,延後到第二段。
