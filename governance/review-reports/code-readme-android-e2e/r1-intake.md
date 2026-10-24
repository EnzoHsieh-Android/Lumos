preflight-4: ran

# code-readme-android-e2e r1 收貨

審材:主線 17a0d393 到 29deb0ef 的完整改動(README 中英兩版、圖產生器、家節點;產出的兩份 SVG 不放審材,由產生器 --check 驗可重現),r1-snapshot.patch 262 行。
兩席:單審(sonnet)、架構對齊(sonnet),都交回後才一起存檔;席報告從各席對話紀錄取最後一則回答原文。單審席最後一行寫成「max severity: major」被格式檢查擋,請該席只改那一行重出,存成 r1-單審-sonnet-格式更正.md(原檔保留)。
id:F 單審、A 架構對齊;編號照報告。引句兩席全錨。

## 機械重現

| id | 嚴重度 | 重現 | 結果 | 去向 |
|---|---|---|---|---|
| F1 | major | 讀碼:收集腳本 prune_old_snapshots 只在開跑時刪超過 7 天的 heap-*.pftrace;skill L3 原文寫「不再跑就不會刪,用完自己刪」;README 寫「快照只留在本機 7 天」 | HIT | 折:中英兩版改成「之後每次跑收集腳本會順手刪掉超過 7 天的,不再跑就不會自動刪,用完要自己刪」 |
| F2 | minor | grep 全 repo:Tab S9 只出現在兩份 README,驗收紀錄寫 SM-X710 | HIT | 折:改成「Samsung 平板(型號 SM-X710)」 |
| A1 | minor | 讀產生器:data-kind 值是 android-evidence record(作者把 receipt 整批換詞時誤換) | HIT | 折:改成 android-record |
| A2 | minor | 讀 assets/readme-diagrams/README.md:寫 Eleven scenes、22 assets,場景清單沒有 Android | HIT | 折:改 Twelve、24,清單補 Android 一條 |

全折 4、放行 0、駁回 0。
