preflight-4: ran

# code-android-evidence r4 收貨

審材:r4-snapshot.patch(1459 行,1c6c0add..bb0f8261,排除卷證與三份帳本);修補差異 r4-repair-review.patch(202 行,d3a17c71 → bb0f8261);來源 r4-repair-binding.json;案例 r4-behavior-cases.json。
跑滿 3 輪後 Enzo 裁 extra-round,這是加的那一輪。兩席全新:單審-sonnet(2 條)、架構對齊-sonnet(1 條)。兩席都交回後才一起存檔與處理。本輪最高 minor。

## 逐條重現與去向

| id | 嚴重度 | 歸因 | 重現 | 結果 | 去向 |
|---|---|---|---|---|---|
| F1 | minor | 原有漏查(標頭解析、expect 拆值、manifest 取 artifacts 那幾行兩版相同) | 席位實跑:標頭多一個無 = 的字、expect=a:n、manifest 缺 artifacts、queries 為 null,各回 1 並噴 Traceback | HIT(採席位實跑輸出) | 放行:只會報失敗、不會誤判通過;計劃加 REVISIT 2026-12-21,真實收據遇到就改成回 2 |
| F2 | minor | 修補引入(r3 新寫的 PITFALL 文字) | 讀 scripts/lumos `_vendor_toolchain`:安裝只照 `_VENDORED_TREE_FILES` 精確清單複製,沒登記的檔不會被裝進消費專案 | HIT | 折:改正 Systems/macrobenchmark-adapter 那條 PITFALL 的現象與根因,以及內文同一句 |
| C1 | minor | 修補引入(r2 新增的範本檔頭) | 讀 scripts/ 既有 .sh:都是 #!/usr/bin/env bash + set -euo pipefail,檔頭另有兩行 MIT 說明 | HIT | 放行:用 /bin/sh 是刻意的,收據要能在沒裝 bash 的機器上重跑(席位自己也註明判不準是否刻意);SPDX 兩行已齊,授權檢查測試綠 |

## 修補因果

regression_set:F2、C1(由 r2、r3 的修補新增的文字與檔頭);F1 是原有漏查,不列入。
