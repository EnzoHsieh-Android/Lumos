# code-簡報審查抓到的機制缺口-std r4 收貨

破例第 4 輪(使用者 2026-11-10 裁 extra-round,跑滿回顧已記)。兩位全新席審修補後整包 r4-pack.patch(560 行)加修補差異 r4-repair-review.patch(135 行);修補來源 r4-repair-binding.json(修前 771f6c11 → 修後 57dd3cb2,r3 fix-check 全部通過,結果在 r3-fix-check.log)。兩席都沒讀前幾輪報告、收貨紀錄與回顧。

## 機械收貨

- 架構對齊席報告原本就是正規化格式。正確性席報告最後一行寫成「max severity: minor」,report-normalize 判成不合格的等級宣告;編排者沒改報告,退回該席原樣重交、只改那一行為「最高等級:minor」,重交版正規化通過。兩份都從逐字稿存檔。
- quote-check 對 r4-snapshot.patch 兩份全數錨定;refcheck 正確性 1 處、架構對齊 3 處全對。
- 正確性席只在自己的臨時目錄做複本實驗,沒動 repo;兩席臨時目錄與編排者重現目錄收齊後用字面路徑刪除(lsof 確認沒有程序在用)。

## 判讀(id:正確性席 i、架構對齊席 j)

| id | 席位等級 | 觀察重現 | 歸因 | 去向 |
|---|---|---|---|---|
| i1 | minor | HIT:Fragment 裡 `object : LifecycleService()` 匿名物件內的 `lifecycleScope.launch { vm.state.collect {} }`,ast-grep 0.51.1 對 state.yml 報第 5 行;同檔具名 `class S : LifecycleService()` 不報 | 原有漏查(state.yml 在修前 771f6c11 與修後 57dd3cb2 相同,修補差異沒動規則) | 放行:匿名物件寫 Service 實務上不會出現,而且結果是多報一處、不會漏報;天花板節已寫例外只認類別宣告,不另補一句 |
| j1 | minor | HIT:計劃〈驗收條款〉與〈預期值表〉順序是 S1、S5、S4;修前 771f6c11 的計劃沒有 [S5](grep 0 處),S5 是 r3 折入時插在 S4 前面 | 有證據的修復回歸(r3 修補新增 S5 時排錯位置) | 放行:只是條款排列順序,編號、綁定、預期值表對應都正確,spec-trace 照編號認條款不受順序影響;再折會多一輪只為排序 |

編排者機械重現不到的:無(refuted none)。修復回歸集合:j1。

## 三問(取自正確性席,編排者核對)

- 原問題修復效果:正確性席在複本上逐個拿掉規則 14 個比對樣式或排除,14 次全部翻紅(其中 `$F.collect { $$$ }` 由既有 C231 等列守著);修前「拿掉偵測段照綠」該席沒重跑,記未判定,以 r3 收貨的翻紅釘為作者側紀錄。
- 修補處正常路徑:`-k kotlin_rulepack` 511 passed, 0 failed;Service 例外的跨行宣告、主建構子、同檔 Fragment、Fragment 內部 Service 都符合預期。
- 新發現兩版:i1 兩版相同(規則檔沒變);j1 修前沒有 S5、修後順序錯,屬修補帶進。

## 先查世界

本輪沒有要折的組,不另查。破例前查方向的結論記在 cap-retro.json 的 world_check(ast-grep valid/invalid、Semgrep ruleid/ok,方向不變)。
