severity: minor

兩個 minor 都是寫法跟鄰居不一致、結構是對的,沒有引入第二種做法。⚠ 項是鄰居本身不一致,交編排者判斷。

## 1. 分層與依賴方向

對照結果:放的位置與連結方式跟鄰居一致。

- 驗證紀錄用 `plan_refs` 指計劃、`system_refs` 指 Systems 節點。
  - 引句:「plan_refs:  - "[[Projects/Android的detekt推送前真的擋_計劃]]"system_refs:  - "[[Systems/linter精選目錄]]"」
  - 對照:`docs/lumos-toolchain-knowledge/Verification/2026-10-07_審查回顧eval補強.md:13`(有 `system_refs`)。335 篇驗證紀錄中 47 篇有 `system_refs`,所以有沒有它都是既有做法。
  - 對照:`docs/lumos-toolchain-knowledge/Verification/2026-11-06_Android儀器測試範本與架構測試實跑.md:11` 只有 `plan_refs`,這篇多一個 `system_refs` 不算違例。
- 被驗的 Systems 節點補 `verified_by`。
  - 引句:「+  - "[[Verification/2026-11-08_detekt的CI型別檢查範本實跑]]"」
  - 對照:`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md` 同欄已有三筆 `[[Verification/…]]`,寫法相同。
- 結案橫幅放在 H1 之後、白話引言之前,引用計劃與驗證都用 `[[連結]]`,沒有手寫路徑。
  - 引句:「> **已結案(2026-11-08)**:[[Projects/Android的detekt推送前真的擋_計劃]] 做完」
  - 對照:`docs/lumos-toolchain-knowledge/Issues/worktree裡改檔推不出筆記.md:23`,位置相同。

## 2. 命名與寫法

對照結果:大部分一致,有兩條不一致(finding 1、2),另有一條 ⚠。

- 檔名 `2026-11-08_detekt的CI型別檢查範本實跑.md` 是「日期_主題」,H1 同檔名,`type`、`status: pass`、`date`、`valid_under`、`revalidate_when`、`tags` 順序都跟鄰居一樣。
  - 對照:`docs/lumos-toolchain-knowledge/Verification/2026-11-01_Kotlin慣例對齊官方與detekt實測.md:2-14`。
- 結案橫幅句式「**已結案(日期)**:…以下是當時的排查紀錄,不是現況。」跟鄰居逐字一致。
  - 對照:`docs/lumos-toolchain-knowledge/Issues/worktree裡改檔推不出筆記.md:23`。

1. 狀態改了、`updated` 沒跟上。
severity: minor
blocking: 否
   - 引句:「-status: open+status: done」
   - 問題單 `docs/lumos-toolchain-knowledge/Issues/推送閘對Android的detekt只記錄不擋.md:5` 的 `updated` 仍是 2026-11-04。
   - 計劃 `docs/lumos-toolchain-knowledge/Projects/Android的detekt推送前真的擋_計劃.md:5` 的 `updated` 仍是 2026-11-05。
   - 對照:同批的 `docs/lumos-toolchain-knowledge/Projects/Android資安靜態檢查補齊第二批_計劃.md:5` 已改成 2026-11-08。
   - 對照:`docs/lumos-toolchain-knowledge/Issues/worktree裡改檔推不出筆記.md:5` 的 `updated`(2026-10-02)跟結案日一致。
   - 規範:`lumos updated-sync` 在 `/Users/enzo/.claude/skills/lumos-project-notes/commands/03-寫回圖譜.md:13`。

2. 問題單結案後 `related` 沒有指向新驗證紀錄。
severity: minor
blocking: 否
   - 引句:「S9 實跑見 [[Verification/2026-11-08_detekt的CI型別檢查範本實跑]]」
   - 橫幅正文引用了這篇驗證紀錄,但開頭欄位 `related` 沒補。
   - 這條證據偏弱:我沒找到「橫幅裡引用就要進 `related`」的明文規範,`Issues/` 底下也沒有以 `verified_by` 連驗證紀錄的先例。判成 minor 的理由是計劃檔是否補連結,patch 也看不出來。

⚠ 交編排者:`[closed:]` 的理由裡放了 `[[連結]]`。
- 引句:「[closed:2026-11-08 已在 macrobench-lab 複本實跑(AGP 8.13.2、detekt 1.23.8),範本改成實測檔名,紀錄見 [[Verification/2026-11-08_detekt的CI型別檢查範本實跑]]]」
- 規範寫「理由至少 4 個字、不放 `[[連結]]`」:`/Users/enzo/.claude/skills/lumos-project-notes/commands/03-寫回圖譜.md:110`。
- 鄰居也這樣寫:`docs/lumos-toolchain-knowledge/Projects/Android單元測試標準實機演練_計劃.md:82`。
- 其他 `[closed:]` 行(例 `docs/lumos-toolchain-knowledge/Projects/收斂閘漏項敏感度v2_計劃.md:220`)都不放連結。
- 規範與鄰居互相衝突,我不裁。不過這條已經違反規範字面,是否算第二種做法由你判。doctor 或 lint 是否擋它,我沒跑,也沒驗。

## 3. 第二種做法

對照結果:沒有引入專案原本沒有的寫法。

- 引句:「REVISIT:2026-12-15 在一個裝了 detekt Gradle 外掛的 Android 專案照 CI 型別檢查範本實跑 … [closed:2026-11-08」
  - `[closed:日期 理由]` 放行尾,跟 `docs/lumos-toolchain-knowledge/Projects/detekt協程規則真的在跑_計劃.md:70` 等一致。
  - 原 REVISIT 文字保留,沒有刪。
- 範本句改成「2026-11-08 實測 detekt 1.23.8:…」,帶日期與版本的現況註記,這種寫法在 `Systems/linter精選目錄.md` 內本來就常見(例:「2026-11-01 用 detekt 1.23.8 實測」)。
- 驗證紀錄末句「實驗複本與各步驟輸出在會談暫存區…收尾已刪」跟全域暫存清理規則的做法一致。

不對齊共 2 條,其中 major 0 條。另有 1 項 ⚠ 交編排者。
