# code-改動選擇點 r2 收貨紀錄

派 7 席(正確性、邊界、通才、資源、合約、架構對齊各看修補差異 r2-repair-code.patch 1831 行;通才另加測試差異共 2498 行;資安看整份 r2-snapshot.patch 14402 行)。7 份報告引句全數錨定(quote-check 對 r2-snapshot.patch)。派工鏡頭這輪仍算超時,固定席沒附;合約席自行對照 Systems/guard-kill 兩條合約,判不影響。
通才席回報跑測試時磁碟一度 100% 滿;編排者刪掉本迴圈本輪席位臨時目錄(5.1GB)後剩 11GB。

## 重現表
全數錨定,沒有要機械重現的錨不到條目。各條的兩版證據在席報告內;編排者另核:

| id | 核對 | 結果 |
|---|---|---|
| c1 b1 r2 k1 | 讀 `_choice_test_blobs`:`git grep -l -F -e <名> <sha> --` 不限路徑、取第一筆;計劃筆記本來就寫 `[test:<名>]`,`docs/` 排在多數模組目錄前 | HIT |
| r1 | 讀 `_choice_scan`:每支檔各開一個 ast-grep;`_choice_push_scan` 掃描與挑壞法共用同一個 30 秒 deadline | HIT |
| c2 b2 g1 a1 | 讀 `_lint_waivers_ai_pending`:拆成三份後只回 lint 與 sit,choice 兩邊都不算;`_cl_say_lint_waive_notes` 只印兩行 | HIT |

## 分組與處置

| 組 | 根因 | 條目 | 處置 |
|---|---|---|---|
| H1 | 守的測試檔用「全樹第一個含測試名的檔」,沒限在測試路徑、沒分平台;每支測試各一次全樹 grep | c1 b1 r2 k1 g2 | 折:一次 git grep 帶全部測試名,只收測試路徑(沿用既有判測試路徑的函式)裡、真的定義該測試的檔;每個平台分開;查不完時雜湊標「不完整」並當作沒變以外的狀態處理(只多跑不漏) |
| H2 | 選擇點 AI 放行拆出來後推送前小結沒有它那一行,lint-waive 的提示句也不成立 | c2 b2 g1 a1 | 折:小結加一行選擇點 AI 放行計數(照情境段那行的做法),lint-waive 的提示句對選擇點照實寫 |
| H3 | 逐檔掃描每支各開程序,大量改動用完 30 秒;掃描與挑壞法共用時限,掃完的也被丟 | r1 | 折:先整批掃一次,整批失敗才退回逐檔;掃描與挑壞法各自計時,掃完的檔不因掃描耗時被丟 |
| H4 | 新的結束碼(部分檔算不出來 rc 3、choice-kill 有檔沒跑 rc 2)計劃沒寫 | k2 | 折(文件):計劃〈範圍〉1、2 補上 |
| — | 環境變數關掉整圈時帳上不留痕 | s1 | 放行(minor,附逐條來源):跟第一輪 s2 同一件事,生效時會印一行;此變數只在測試總檔程序內設定,平常操作造不出殘留 |

## 先查世界
- PRIOR-ART:H1 Android 官方文件:儀器測試在 `src/androidTest/`、變體在 `src/androidTest<Variant>`,`sourceSets` 可改根目錄(https://developer.android.com/studio/test/advanced-test-setup 、https://developer.android.com/build/gradle-tips)。採用:找測試檔先限在測試路徑(沿用專案既有判法,它涵蓋 src/test、src/androidTest 等),不取全樹第一筆;路徑被 sourceSets 改掉的專案判不到時退回「不完整」只多跑。第一輪 Stryker 增量模式比對測試檔內容的做法照舊。
- PRIOR-ART:H3 Pants 的 lint 說明:逐檔跑快取好,但工具啟動成本高,冷快取時整批跑較便宜(https://www.pantsbuild.org/2.8/reference/goals/lint);ast-grep 單次呼叫會多核平行處理多檔(https://ast-grep.github.io/advanced/how-ast-grep-works.html)。採用:先整批,失敗才逐檔。
- 方向:對 — H1 是第一輪 G3 同一組根因連兩輪且本輪有 major;方向(依測試檔內容判重跑)本身有 Stryker 與 Android 測試路徑慣例兩個來源支持,問題在取檔方法,不換方向。
- H2、H4 是本專案自己的提醒與文件,沒有外部做法可查。

## 回歸因果(第 2 輪)
- 有證據的修復回歸:r1(修前 1400 支小檔判得到、修後全部算不出來);c2 b2 g1 a1(修前 AI 放行計數 1、修後 0);g2(修前沒有逐測試全樹查詢);c1 b1 r2 的「只改計劃筆記就重跑」那一半(修前雜湊不隨筆記變)。
- 有證據的原有漏查:k1 與 c1 b1 r2 的「補強測試不重跑」那一半(修前修後都不重跑)。
- k2 是修補新增的結束碼沒同步到文件。
- s1 是分支原本就有的行為,不是修補造成。
