# r2 收貨、重現與處置

## 材料與編制

- 修補鏡頭:修前 0221bd2e → 修後 b53500e2(`r2-repair-binding.json`,祖先關係 rc0;區間兩個修補提交 082a5d7d、b53500e2)。修補差異 515 行;完整快照 `r2-snapshot.patch` 範圍 8e648f3d..2494971e。
- 兩席全新 Claude Sonnet:正確性席讀修補差異加案例,架構對齊席讀修補差異。派工詞禁止讀 r1-* 與輕量迴圈卷證。
- 上一輪記帳後,架構對齊席報告第 3 行總結句寫「所以沒有 major」被判高於檔級宣告,退回該席,它交回的替代句照原文換上(r1 帳記的是換上之後的版本)。

## 收貨

- 兩份報告從子代理逐字稿抽最後一則存檔,都是正規化格式。
- **退回一次**:正確性席的引句寫成 `引句:原文` 沒有用「」包住,機器抽不到;退回該席,它交回五行 `引句:「…」`,照原文逐行換上,其餘一字未動。換上後全數錨定。
- 架構對齊席 12 句引句有 3 句錨不到(#3、#4、#6):引的是本分支沒改到的 `scripts/test_lumos.py` 的 `_lumos_parser_tree` 說明與規格閘筆記修前版本的摘要行,不在凍結快照裡;下表機械重現 HIT。

## 重現(編排者機械重現)

finding 編號:正確性席 F1–F5;架構對齊席 A1–A5。

| finding | 重現 | 說明 |
|---|---|---|
| A1 | HIT | `COLUMNS=40 python3.14 scripts/lumos spec-gate --help` 找不到「風險低時紅綠是放行條件」(被斷行),`COLUMNS=100` 找得到;`scripts/test_lumos.py` 的 `_lumos_parser_tree` 說明寫明讀說明文字只走 parser 這一條(原文 grep 命中 1)。新測試起子行程剖 --help |
| A2 | HIT | 規格閘筆記正文新增 `- 2026-10-10:` 流水帳條目,同篇其他帶日期紀錄都是摘要前綴行;摘要那行修前版本 grep 命中 1 |
| A3 | HIT | 指令參考「只列出、不擋」區塊有一行 `git commit`,其他區塊每行都是 `lumos`;`lumos doctor` 已有一列 |
| A4 | HIT | 開關表新列把四個開關併成一格、後三個省略 `note_shape.` 前綴 |
| A5 | HIT | 英文 README 新連結標籤寫 `10/7–10/10`,同檔既有連結寫 `October 7–10` 並標 (Chinese) |
| F1 | 採信 | 席位 grep:lint_new、note_lint、tag_hints、close_summary 在 skill 手冊零命中 |
| F2 | 採信 | 席位附 `note_shape.gate` 為 off 時提前 return,四個提醒排在其後 |
| F3 | HIT | README 兩版已無「用量帳」,清點處置欄仍寫 README 註明預設不開 |
| F4 | 採信 | 席位附 `replay_weekly.py` 的補凍結失敗、逾時、游標寫入失敗都進同一個 errors 清單 |
| F5 | HIT | 規格閘筆記摘要「半套只印不擋紅綠、不寫審查帳」;`_spec_gate_record` 寫 `.canary-log.jsonl`,在兩種門都會跑 |

## 修補因果(regression)

- 有證據屬上一輪修補造成:A1(新測試是上一輪補的)、A2、A3、A4、A5、F1、F2、F3(都是上一輪新加或改寫的文字)。
- 原有漏查:F5(摘要那行兩版都在)。
- 未判定:F4(修前寫「執行出錯也會通知」範圍較廣,修後收窄成「逐案回放出錯」;沒有證據證明是修補讓它不準)。依共用範本 §3.1 這輪帳不帶 `--regression-set`。

## 修前選例

| 組 | repair | preserve |
|---|---|---|
| 規格閘說明測試 | 改走 parser 與說明表;終端寬度 40、200 都綠;放回修前說明 3 條紅;語意寫反(風險高也擋)1 條紅 | `-k spec_gate` 既有測試照綠 |
| 文件說法 | 開關表、只列出區塊、回放通知、清點處置欄、英文連結、規格閘摘要與程式一致 | `--suite docs` 照綠;`generate.py --check` 照綠 |

## 處置

- 本輪有存活 major(A1),全部折入:F1–F5、A1–A5。修補提交 cbb854a0。
- 編排者驗收:`-k spec_gate` 104、`-k help` 11、`--suite docs` 736,全綠;新測試在 COLUMNS=40、200 都綠,兩種改壞都紅(改壞在 scratchpad 的 shared clone 做,做完刪掉)。
