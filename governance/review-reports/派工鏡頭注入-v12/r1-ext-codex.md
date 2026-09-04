### f1

引句:「三格輸出只有 base 已追蹤檔名、testmap(主線建)的測試名、base 版識別字、整數;無任何 diff 文字。」

file: `scripts/lumos:14631`

severity: blocker

blocking: 是

`testmap affected` 直接讀目前工作樹中被 `.gitignore` 排除的 `.lumos/testmap.json`，並未從 base/mainline 取資料；其中 `test` 只驗型別及當前檔案存在便原樣輸出（`scripts/lumos:14647`、`scripts/lumos:14703`）。待審分支可強制追蹤或誘導重建該檔，把分支控制的測試路徑送進審查 prompt，形成新的自由文字注入管道。

### f2

引句:「沿既有 `_cochange_mine`/`cmd_cochange_rules` 的規則」

file: `scripts/lumos:13371`

severity: major

blocking: 是

既有共改鏈會從目前工作樹讀 `.lumos/cochange.json`，讓待審分支用 `exclude`、`min_confidence` 或 `max_changeset` 改寫乃至清空備援結果；即使歷史截止於 base，規則設定仍不是 base 版。照「沿既有」字面直接呼叫現成鏈，不能得到不受待審方控制的既有相依。

### f3

引句:「`--json` 多欄位 `fallback: none|attached|skipped-no-testmap`,日後從席報告與 recount 看備援觸發率與被引率。」

file: `scripts/lumos:16731`

severity: minor

blocking: 否

缺 testmap 時規格仍要求附標頭、共改夥伴與呼叫者，但唯一狀態 `skipped-no-testmap` 會把「備援已附、僅測試格跳過」記成 skipped。依此欄位統計備援觸發率會漏算缺 map 但實際已注入的事件。

最高 severity: blocker；blocking 2 條。
