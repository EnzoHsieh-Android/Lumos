# r2 收貨紀錄(code-推送只跑受影響測試)

## 收貨

- 第 2 輪,分級 high,七席全 sonnet(正確性、邊界、資源、合約圖譜、通才、架構對齊、資安),外家預設不派;收斂結論照實寫成「單家族視角下」。
- 派工前:分支已換基底到主線 4cc9c425(另一個會談的 PR #160);第一輪審的 c6a14c90 換基底後是 d8134d85。修正關卡以 d8134d85 → 9918ed76 重跑全過(184.9 秒)。第一次跑(換基底前)卡在 t_prepush_docs_and_light_run_subset 超過 180 秒,已把新斷言拆成獨立測試;換基底後主線那支測試的上限是 360 秒(主線原有覆寫)。
- 修補鏡頭材料:r2-repair-review.patch(只含程式、測試、說明)、r2-repair.patch(全量)、r2-repair-binding.json(兩端提交、樹碼、指紋、歸因界線);完整快照 r2-snapshot.patch(4cc9c425..9918ed76)。
- 七席全數交回後一次存檔(從逐字稿取原文)。資源席交報告後自己開的背景測試還在我的工作樹跑,等它結束(ps 確認 0 個)才動檔。資源席報告的等級寫成粗體,用 `lumos report-normalize --write` 純格式搬移(只把等級搬成獨立行,不改值)。
- 引句:七份全錨定(對 r2-snapshot.patch)。
- 圖譜鏡頭:合約圖譜席逐篇用 `lumos contracts` 答了固定席(事故那篇沒逐條判);其他席多半自承沒逐篇讀。這輪圖譜面靠合約圖譜席。

## 重現表

| id | 來源 | 重現 | 結果 |
|---|---|---|---|
| 二通1 | 通才 #1(major) | 掛鉤 `_pf_extra=(--pushed-ref "$_rref")` 改成 `$_lref`,跑 `-k prepush_feature_branch` | HIT:席位原輸出 20 passed 0 failed(全綠,抓不到);編排者補「本機 feat 推遠端 main 照全套」「本機 main 推遠端 feat 降級」兩案後,同一改壞 `-k feature_branch_mixed_with_main` 2 passed 2 failed,還原 4 passed |
| 二合1/二正1 | 合約圖譜 #1、正確性 #1 | `grep -n "already_light" docs/lumos-toolchain-knowledge/Projects/推送只跑受影響測試_計劃.md` | HIT:0 筆,[S6] 只綁 t_prepush_feature_branch_light_ok_false |
| 二合2 | 合約圖譜 #2 | `sed -n 183p ARCHITECTURE.md` | HIT:CI 節點寫「全套測試」,沒說功能分支要開 PR 才有 |
| 二源1 | 資源 #1 | 席位實測 t_prepush_docs_and_light_run_subset 最慢 204.3 秒、上限 360 秒 | HIT(餘裕 2 倍,工具標 ⚠);上限 360 是主線原有覆寫 |

refuted: none

## 先查世界

- PRIOR-ART: 推送掛鉤判目的地(二通1)——git 官方 githooks 文件(https://git-scm.com/docs/githooks#_pre_push):pre-push 從 stdin 每行收 `<local ref> <local sha> <remote ref> <remote sha>`,被推去哪個分支看 remote ref。採用:測試補本機與遠端不同名的兩個案例(`feat:main` 照全套、`main:feat` 降級),讓「看錯欄」翻紅。
- PRIOR-ART: 測試場景回傳路徑(二架1)——同檔既有 fixture(_sc_setup 回 (d, kg, p))直接回圖譜根;採用:_ppfb_harness 多回 kg,新測試用 `kg / "Systems" / "Home.md"`,不另用搜尋。
- PRIOR-ART: 狀態變數取名(二架2)——同檔 `_suite_this` 存結果(full/light/docs),新變數存原因;採用:值改成 spec_light / feature_branch 並在註解寫明哪一個才印降級行。
- PRIOR-ART: 文件同步(二合2)——同族掃描:ARCHITECTURE.md 只有中文版,流程圖 CI 節點補「推 main 或開了 PR 才跑」。

## 歸因

- 二通1:有證據的原有漏查——c6a14c90(第一輪)與 d8134d85 的測試就都本機遠端同名,修補沒碰這段。
- 二架1、二架2、二正1、二合1:修補新增(新測試與 `_down` 都是第一輪修補帶進來的),屬修補造成的 minor。
- 二合2:有證據的原有漏查(ARCHITECTURE.md 兩版都沒變)。
- 二源1:原有負擔,上限是主線覆寫;修前耗時未量,未判定是否改善。
- 二邊1、二安1:同第一輪放行過的「主線不叫 main」族,原有設計,不是修補造成。

## 逐條去向(4 折、5 放行、0 駁回)

| id | 席報告原條 | 去向 |
|---|---|---|
| 二通1 | 通才 #1(major) | 折:t_prepush_feature_branch_mixed_with_main 補 feat:main 照全套、main:feat 降級兩案 |
| 二架1 | 架構對齊 #1 | 折:_ppfb_harness 多回 kg,新測試直接用 fixture 路徑 |
| 二架2 | 架構對齊 #2 | 折:`_down` 值改 spec_light / feature_branch,註解寫明只有 feature_branch 印降級行 |
| 二合2 | 合約圖譜 #2 | 折:ARCHITECTURE.md 流程圖 CI 節點補推 main 或開 PR 才跑 |
| 二合1 | 合約圖譜 #1 | 放行:設計判定已凍結(governance/replay/推送只跑受影響測試/verdict.json),在條款補 [test:] 要動被凍結的計劃;t_prepush_feature_branch_already_light 在全套與 PR 的 CI 照跑,改壞會紅(兩席都實測過)。計劃收尾時補綁定 |
| 二正1 | 正確性 #1 | 放行:同合1 |
| 二源1 | 資源 #1 | 放行:上限 360 秒是主線原有覆寫,這次修補把新斷言拆出去沒有加重它;耗時改善另開題 |
| 二邊1 | 邊界 #1 | 放行:同第一輪邊1(本 repo 主線是 main;這類分支本來沒有 push 事件 CI) |
| 二安1 | 資安 #1 | 放行:同邊1,席位自標推論 |
