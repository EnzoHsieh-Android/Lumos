preflight-4: ran

# code-android-evidence r3 收貨

審材:r3-snapshot.patch(1424 行,1c6c0add..d3a17c71,排除卷證與三份帳本);修補差異 r3-repair-review.patch(398 行,49283648 → d3a17c71);來源 r3-repair-binding.json;案例 r3-behavior-cases.json。
兩席全新:單審-sonnet(2 條)、架構對齊-sonnet(4 段,第 4 段自己寫明「只是記錄,不算不對齊」)。兩席都交回後才一起存檔與處理。
這是 standard 分級的第 3 輪(上限);跑滿後攤 Enzo 裁定,選「留在範本目錄、加一輪」(cap-decision extra-round)。

## 逐條重現與去向

| id | 嚴重度 | 歸因 | 重現 | 結果 | 去向 |
|---|---|---|---|---|---|
| V1 | major | 修補回歸(r2 把範本搬進 scripts/templates/ 卻沒登記 `_VENDORED_TREE_FILES`) | `-k vendored_file_list` → 少登記 scripts/templates/android-receipt-rerun.sh,1 failed | HIT | 折:登記進 `_VENDORED_TREE_FILES` |
| V2 | major | 原有漏查(這段從 r1 的 reference.md 原樣搬來) | 收據 `trace=zzz` → rc1 KeyError 'zzz';`requires=Q7` → rc1 KeyError 'Q7' | HIT | 折:範本加兩道檢查(查詢指到 manifest 沒有的 artifact、requires 指到不存在的查詢)回 2;測試各加一案只踩那一道,各拿掉一道都紅 |
| B1 | major | 修補回歸(r2 的改法) | 讀 scripts/templates/ 既有三份都是 .md、由 lumos 以字面路徑讀;新檔是可執行 .sh、靠手動複製 | HIT(設計取捨) | 折:跑滿攤人裁,選留在範本目錄;登記進複製清單走既有分發管道(V1),錯誤輸出照 lumos 慣例(B3);計劃 WHY 寫明為什麼不做成 lumos 子指令(收據要在沒裝 Lumos 的機器上重跑、調研定了 Lumos 不執行第三方工具) |
| B2 | minor | 同 V1 | 同 V1 | HIT | 折:同 V1 |
| B3 | minor | 修補回歸(r1 起的範本寫法) | 範本收據寫錯時印到 stdout、開頭「BAD 收據本身」 | HIT | 折:改成 stderr、「擋下:」開頭,回 2;測試檢查 stderr 開頭與沒有 Traceback |

架構對齊席第 4 段(`_macrobench_num` 等對齊)席位自註「只是記錄,不算不對齊」,不列為發現。

## 修補因果

regression_set:V1、B1、B2、B3(由 r2 的修補造成)。V2 是原有漏查(席位實跑:修前 reference.md 內嵌版與修後範本版同一段程式、同樣行為),不列入。
