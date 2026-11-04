severity: minor

我沒有開啟 r1-、r2- 開頭的席報告,以下都是自己讀 r3-snapshot.patch、r3-repair.patch 和 repo 原始碼判的。

## 問 1:分層與依賴方向

沒有跨層直呼,也沒有新增依賴方向。

- `scripts/lumos` 只改了 `_STACK_QUESTION_SPECS` 裡 `kt-flow`、`kt-leaks` 兩題的 `q` 文字。題目 id 沒動,`when` 觸發字也沒動,跟 `scripts/lumos:36707` 的其他棧題目同一層。
- 新測試都是讀文件或讀 `scripts/lumos` 的守衛測試,放在 `scripts/test_lumos.py`,依賴方向跟 `t_tension_doc_sync`、`t_test_quality_standard_android_room_section` 一樣。
- 守門都用 `_need_src`(`scripts/test_lumos.py:146`)。`GRAPHCTL` 本身已經 `resolve()` 過(`scripts/test_lumos.py:30`),所以 `_kotlin_idioms_text` 讀檔不帶 `.resolve()` 沒有路徑分歧。
- 手冊新增的「五、Android 特有(只有 Android 專案適用)」節,位置和標題寫法都跟 `skills/java-idioms/SKILL.md:174` 的「六、Android 特有」一致,而且在接線節之前。
- 修補差異(r3-repair.patch)只動 `governance/anchor-baseline.json`。我算過,各提交的 `scripts/test_lumos.py` 雜湊和當下基準檔一致:
  - `1f9a03359`:`d44a9eada24617b2`
  - `98a346717`:`46c64b8e6007a2f0`

## 問 2:命名與錯誤處理

結構對,有兩處跟鄰居不一致,都是 minor。

**C1 兩個審查題同在一個提交內,只同步了一個到效能檢核目錄**

- 既有 X:效能檢核目錄跟 `_STACK_QUESTION_SPECS` 雙向同步。題目語意改了,目錄的對應列也要改。依據是 `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:29` 摘要寫的「本目錄『人判提問』欄改動須同步 scripts/lumos _STACK_QUESTION_SPECS」。
- 隱患 Y:`kt-leaks` 題文多問了 ViewModel 收 Context 或繼承 `AndroidViewModel`,但目錄第 66 行「記憶體洩漏(Context 持有)」那一列沒提 ViewModel。我 grep 這個檔,`AndroidViewModel` 只出現在 Flow 列和 `kt-flow` 對照列的 `ViewModel`(第 70、233 行),洩漏列沒有。
- 這次 Z:`kt-flow` 的題和目錄列兩邊都改了,`kt-leaks` 只改題。
- 不一致 1 檔。
- 計劃做法 5 的清單本來就沒列洩漏列,所以這是「計劃自己漏列」,不是「漏做」。
- 引句:「ViewModel 有沒有收 Context/Activity 或繼承 AndroidViewModel(官方建議不要;要資源就移到畫面層或資料層,idioms R20)?」
- 對照鄰居:`docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:66`
severity: minor
- blocking: no

**C2 新測試的暫存目錄前綴不是專案慣用的 `gctl-`**

- 既有 X:`scripts/test_lumos.py` 裡 `mkdtemp(prefix=...)` 約 780 處,756 處用 `gctl-` 開頭。同區塊的 `t_tension_lens_and_gov` 也是(`scripts/test_lumos.py:65311`、`65465`,`gctl-tens-`、`gctl-tens-gov-`)。
- 隱患 Y:專案的暫存清理、`gctl-run-*` 殘骸辨識、runner 的 `iso_tmp` 檢查(`scripts/test_lumos.py:625`)都以 `gctl-` 為辨識前綴。
- 這次 Z:`t_kotlin_idioms_detekt_snippet_runs` 用 `lumos-kt-idioms-detekt-`,全檔只有這一處。
- 不一致 1 檔。
- 實際影響小:runner 把 TMPDIR 隔離在 `gctl-run-` 底下,`finally` 也會 `rmtree`。
- 引句:`root = Path(_tf.mkdtemp(prefix="lumos-kt-idioms-detekt-"))`
- 對照鄰居:`scripts/test_lumos.py:65311`
severity: minor
- blocking: no

錯誤處理和日誌我看了,沒有不一致:
- 缺外部工具時印 `⚠ … 沒驗到` 後 return,跟 dart 段(`scripts/test_lumos.py:25583-25585`)一樣。
- 全檔缺工具的處理本來就混用(pwsh 走 `check(True)` 加 return、`watchdog_notifier_bundle` 印 `✓` 後 return),不是這次新引入。
- 新測試的 `print("  ✓ t_...")` 收尾,跟 `print("t_...")` 開頭兩種寫法在檔內都有(約 425 對 634),不算不一致。

## 問 3:第二種做法

沒有引入第二種做法。測試形狀、`_need_src`、手冊的依據行和機檢行、計劃筆記的「審計修正紀錄」段、驗證紀錄的 frontmatter(`valid_under`、`revalidate_when`、`plan_refs`)都沿用既有格式。Verification 目錄 327 份裡 320 份有 `valid_under`。

## 修訂輪:壓提交與重簽有沒有引入新不一致

重簽本身沒問題。基準檔備註的寫法跟主線前一次(`77317a880`)一致,各提交內的雜湊也對得上。壓提交的切法有一處跟主線慣例不一致。

**C3 提交切法:一個計劃拆兩個提交,審查卷證只在最後一個提交**

- 既有 X:專案規定「一個功能一個提交,程式、圖譜筆記、審查卷證放同一個提交」。主線最近的功能提交都是這樣:
  - `77317a880`:程式、筆記、卷證和兩份日誌帳在同一個提交
  - `23c34f843`:同上
  - `9c6d7a81e`:同一個 detekt 標準接法,設定檔和 linter 目錄在同一個提交
- 隱患 Y:Kotlin 慣例計劃是一個功能,卻切成 `1f9a03359`(手冊、審查題、測試、效能檢核目錄)和 `3e62aa422`(`configs/detekt/android.yml` 加 linter 目錄)兩個提交。
- 計劃 `lands_in` 寫了「Systems/linter精選目錄」,但第一個提交沒有改它。
- 第一個提交的 Verification 筆記寫「回頭條件記在 [[Systems/linter精選目錄]]」,那條 REVISIT 要到第二個提交才出現。
- 這一批的審查卷證(r1、r2 席報告)、兩份日誌帳、`.canary-log` 全在第三個提交 `98a346717`。第一個提交沒有自己的卷證。
- 這次 Z:三個提交對兩個功能,把一個功能切成兩段,卷證只掛在另一個功能的提交上。
- 不一致 3 個提交。
- 兩個計劃共用一個審查迴圈,卷證掛在最後一個提交可以辯護,所以我不判 major。
- ⚠ 交編排者:要不要把 `3e62aa422` 併回 `1f9a03359`(變成兩個功能提交),我只能說這跟主線不同,不能替人裁。
- 引句:「linter 精選目錄的 detekt 標準接法補型別資訊的實測事實(它管共用設定那支檔)」
- 對照鄰居:`git show --stat 77317a880`、`git show --stat 9c6d7a81e`
severity: minor
- blocking: no

## 小備註,不列為 finding

- 兩份計劃的「審計修正紀錄」只寫了 r1,沒有 r2 的修補(例如 S3 加每條「依據」行檢查),Verification 筆記的「代碼審 r1 之後」同樣沒有 r2。Room 計劃(`Room資料庫測試守衛_計劃.md:175` 起)是每輪各記一條。這可能是等迴圈收尾才補,我不判。
- 第三個提交類型寫 `docs:`,主線上同類(`19f7e4029`)是 `feat:`。主線類型本來就混用,所以不列。

不對齊共 3 條,其中 major 0 條
