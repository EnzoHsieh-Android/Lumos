# code-pass選擇點預判 r3 收貨(上限輪)

席位:正確性-sonnet、架構對齊-sonnet(全新代理,沒讀上輪報告)。材料:r3-snapshot.patch、r3-repair.patch、r3-repair-binding.json、r3-behavior-cases.md;派工單 r3-dispatch.json(base_commit 4fa287474)。
收貨三道:兩份都已是正規化格式、refcheck 全 ok;正確性席引句全數錨定。架構對齊席 a1 的引句跨兩行,quote-check 錨不到,編排者機械重現 HIT(見重現表),照收;載體因此掛全錨的正確性席。
reflog 只有編排者自己的提交;`git worktree list` 沒有審查席留下的工作目錄;兩席收齊後整個迴圈的臨時目錄已刪(這是最後一輪)。

發現編號:正確性 c1;架構對齊 a1、a2(共 3 條,全 minor)。

## 重現表

| id | 席 | 等級 | 編排者重現 | 處置 |
|---|---|---|---|---|
| c1 | 正確性 | minor | HIT(現象):席位兩版各跑一次,修前最慢 50.7 秒、修後 72.8 秒,工具印「餘裕不足 3 倍」;多出的時間對得上 r2 新增的兩次 pass 子程序 | 放行:離 180 秒上限還有 2 倍,上限輪不再改程式;計劃寫了 REVISIT:2026-12-21 看耗時,超過 120 秒就拆 |
| a1 | 架構對齊 | minor | HIT:引句跨兩行錨不到;`grep -n -A1` 在 r3-snapshot.patch 第 363、364 行找到相鄰的兩行原文 | 放行:同 r2 a2,結構與鄰居相同,只差輸出通道;席位自己也標推送路徑本來就印 stdout、鄰居有分歧 |
| a2 | 架構對齊 | minor | HIT(現象):同 r2 a1 | 放行:同 r2 a1,範圍照推送前掛鉤輸入模擬是設計審 r2 定的做法 |

另:架構對齊席說它沒驗 `t_prepush_cl_reason_table_matches_lumos` 要不要補 `choice`——編排者查過,那張表管的是 `code-loop check` 的 reason_kind,這次只在 `code-loop pass` 擋下事件的 blocks 帶 `choice`,沒有新增 reason_kind;該測試在 r1 變異驗證時跑過 5 條全綠。

## 修補因果(regression-set)

- c1:耗時增加來自 r2 修補新增的兩次 pass 呼叫,兩版量測有差 → 上一輪修補造成,列入 regression-set。
- a1、a2:修補差異沒動那幾行,修前就有 → 原有,不列。
結論:`--regression-set c1`。

## 先查世界

本輪全數放行、不改程式,不適用修前查世界;c1 的回頭條件照專案既有的測試耗時帳(`governance/test-durations.json`)與 180 秒上限判。
