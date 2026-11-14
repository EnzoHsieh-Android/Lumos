# code-改動選擇點 r3 收貨紀錄

派 7 席(正確性、邊界、資源、合約、架構對齊各看修補差異 r3-repair-code.patch 772 行;通才另加測試差異共 1056 行;資安看整份 r3-snapshot.patch 14747 行)。派工前暖過派工鏡頭快取(算一次 150 秒),固定席這輪仍沒附上(hook 45 秒超時)。
6 份報告引句全數錨定;合約席 3 句有 1 句錨不到(見重現表 k2);資安席 clean、零條,沒有引句。資安席自述「只審修補差異」,涵蓋面不足——本輪已到上限、修補後必須對最後一版凍結快照再派資安,下一輪資安席派工詞明寫整份快照逐檔看。
通才席回報磁碟一度剩 403MB,自刪臨時副本後恢復;收齊時剩 9.8GB。

## 重現表

| id | 核對 | 結果 |
|---|---|---|
| k2 | 引句跨行:r3-snapshot.patch 第 10048–10049 行原文為「整批最多用」換行接「_CHOICE_BATCH_SHARE 那一份,剩下的留給退回的逐檔」;`scripts/lumos` `_choice_scan` 以 `* _CHOICE_BATCH_SHARE` 給整批時限,`grep -n _CHOICE_BATCH_SHARE scripts/test_lumos.py` 0 筆 | HIT |
| c1 b1 | 讀 `_choice_scan_batch`:`ast-grep scan … src` 掃目錄、不帶 `--no-ignore`;`ast-grep scan --help` 寫明目錄模式會套用 .gitignore/.ignore,`--no-ignore vcs|parent|dot|exclude|global|hidden` 可關。兩席各自用修前修後兩版探針重現(修前 1/1、修後 0/0) | HIT |
| a1 | 讀 `_choice_test_blobs`:測試名整串 `-w -F`;專案既有 `Class.Method` 取最後一段(`_test_in_tree` 一帶) | HIT |

## 分組與處置

| 組 | 根因 | 條目 | 處置 |
|---|---|---|---|
| J1 | 守的測試所在檔查找:名稱形狀沒照專案既有慣例(`類別.方法` 取最後一段),副檔名限定與輸出大小沒有釘 | a1 c2 r2 r1 | a1 折(照既有慣例取最後一段再找,同一函式內不另寫一套);c2 折(補測試路徑裡非平台副檔名的檔);r2 放行(minor,附來源:要綁的測試名剛好是 `x` 這類一兩字母識別字才觸發,28 萬行樹多吃約 200MB、0.4 秒;綁條款的測試名實務上是長名);r1 放行(minor,附來源:原有漏查、修後比修前快 8 倍以上,上限到了退成「不明 → 多跑」,不會漏也不會擋錯) |
| J2 | 整批掃描目錄時 ast-grep 套用忽略規則,暫存目錄落在忽略 `*.kt` 的 repo 裡時整批靜默零命中;整批只用一半時限沒有測試 | c1 b1 k2 | c1 b1 折(整批加 `--no-ignore` 全部種類,與逐檔點名行為一致;另加命中檔數核對不必要——旗標即根因);k2 折(補一支整批卡住、逐檔快的測試) |
| J3 | 推送前多算一個碰到計劃的時限底線,實際走快取、不起作用 | g1 | 折(拿掉死碼與文件說明) |
| J4 | 既有行為缺釘:choice-kill 有檔算不出來回 2、doctor 放行條數不含選擇點 | k1 k3 | 折(各補一支先紅的測試) |
| — | 一支超大檔讓整批失敗、其他檔連帶退逐檔 | r3 | 放行(minor,附來源:修前同輸入一樣有約 400 支超時,修後沒更壞;只提醒不擋,已列在待驗行為的未覆蓋) |

## 先查世界
- PRIOR-ART:J1 Gradle 測試篩選接受 `類別.方法` 與萬用字元的名稱形式(https://docs.gradle.org/current/userguide/java_testing.html#test_filtering);本專案綁定寫法同樣認 `Class.Method`、查找取最後一段。採用:沿用專案既有慣例,不新寫名稱剖析。
- 方向:對 — J1 是第一輪 G3、第二輪 H1 同一支函式連三輪,本輪有 major。方向(依測試檔內容判重跑)有 Stryker 增量模式比對測試檔內容(https://stryker-mutator.io/docs/stryker-js/incremental/)與 Android 測試路徑慣例(https://developer.android.com/studio/test/advanced-test-setup)兩個來源支持;本輪問題是名稱形狀沒照既有慣例,不是方向錯,不換方向。
- PRIOR-ART:J2 ast-grep `scan --help`:目錄模式預設尊重 .gitignore/.ignore/全域忽略,`--no-ignore` 逐種關掉;直接點名檔案不受影響。採用:整批加全部 `--no-ignore` 種類,讓整批與逐檔看到同一批檔。
- J3、J4 是本專案自己的死碼與缺測試,沒有外部做法可查。

## 回歸因果(第 3 輪)
- 有證據的修復回歸:a1(修前點號名雜湊穩定、修後每次重跑);c1 b1(修前逐檔 1/1、修後整批 0/0);r2(修前 `-l` 輸出不隨出現次數長,修後 `-o` 隨出現次數長)。
- 有證據的原有漏查:r1、k1、k3。
- 修補新增但未判定是否回歸(修前沒有該機制):c2、k2、g1。
- 未判定:r3。

## 上限
本輪是 high 上限第 3 輪,有 major(a1)。依手冊到頂停手、查方向(見上)。使用者 2026-11-14 交代無人值守、自行簽核、自行推進;方向判「對」、修法小而局部,編排者依該授權記 cap-decision extra-round,先寫跑滿回顧再修,修後派全新席(含整份快照的資安席)。
