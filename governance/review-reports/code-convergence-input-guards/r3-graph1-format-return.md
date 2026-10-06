severity: minor

## Findings

graph1-F1
severity: minor
blocking: 否

引句:「PITFALL:[來源:2026-07-23 Systems/guard-kill 舊摘要]手寫態名把 survived 誤當綁定測試翻紅；重現與固定版本結果見 Verification/2026-10-07_合併前最新主線整合，不外推其他配方。」

- 觀察：新增 PITFALL 以未定義的 `[來源:]` 代替必填 `[出處:]`，且摘要缺 `[根因:]` 與 `[test:]`／`[repro:]`／`[防回歸:]` 任一項。正文雖有說明，結構化摘要仍違反新筆記格式。
- 判準：`AGENTS.md:46` 明定 PITFALL 必須有 `[出處:]`、`[根因:]`，並附三種驗證鍵之一。
- 具體失敗場景：新 session 或工具只取摘要欄位時，無法結構化辨認根因及重現入口；現行 lint 又會把它判成零問題，使錯形狀繼續流入圖譜。
- 受影響位置：file: `docs/lumos-toolchain-knowledge/Issues/殺傷力舊摘要態名誤寫.md:16`
- 修補候選：改用規範鍵，將正文已有的根因及固定案例入口填回摘要。
- 保留候選：保留「只修態名、不外推其他配方」、原 decision、正文及 Verification 連結，避免把筆記修正升格成產品效力。
- 命令與原輸出：

```text
$ python3 scripts/lumos lint 'Issues/殺傷力舊摘要態名誤寫'
✓ lint Issues/殺傷力舊摘要態名誤寫.md — 0 問題
```

- 結果：缺口仍在；本席唯讀未修 repo。因正文尚能提供脈絡、未改 CLI 行為，評為 minor。

## 三問

1. 原問題是否修復：未判定。圖譜記載負數計數、測試家路由、guard-kill 態名及 AST 測試界線等修補，但未提供同案例兩版實跑材料；不能以筆記的 green／done 宣稱修復成功。
2. 原正常路徑是否保留：未判定。`r3-test-layers.txt` 為 0 bytes，本席未取得同輸入、同預期、相同 fixture、實際載入版本及兩版原始輸出。
3. 新發現：有，graph1-F1；屬本輪新增圖譜摘要形狀缺口，不主張它是產品修補造成的執行回歸。

各真碼根因的獨立選例如下，結果均未跑、未判定：

| 根因 | repair 候選 | preserve 候選 | 獨立推導 |
|---|---|---|---|
| 負數 findings 太晚拒收 | `--findings -1` 應在追加前 rc2 | `--findings 0` 仍合法；格式錯誤仍留既有 blocked telemetry | 函式守衛 file: `scripts/lumos:9319`；治理留痕合約來自計劃正文 |
| 測試家路由證據漏收／跨提交借證 | 同提交修改已宣告測試並寫回其家應通過 | 未修改該測試仍拒收；測試仍免強制安家；純測試不得借給 production 家 | 分類器 file: `scripts/lumos:29114`；路由 helper file: `scripts/lumos:29454`；逐提交消費 file: `scripts/lumos:29663` |
| staged index 讀取競態 | 檢查期間 index 改變時撤回額外證據 | index 穩定的合法路由仍可採信；原正式程式退路不放寬 | 呼叫者 file: `scripts/lumos:30028` |
| guard-kill 舊摘要態名誤植 | 固定配方須核對實際 verdict、weak 與真正斷言 | `survived` 仍為 rc1；drift／abort／error 優先級及 JSON 純度不得改 | 函式／合約 file: `scripts/lumos:17077`；未讀完整結果分支、未實跑 |
| AST 寫入點測試誤受函式長度影響 | 真正 `cmd_home_check` 寫入點應被定位 | 函式外同文字不得誤算；真正 writer 仍須被抓到 | 本席未在額外行數內完整讀該測試，要求另拆席 |
| 修補／保留、同類／根因、修補／重構混稱 | 手冊須分開記錄及判讀 | 完整改動、新席獨立核對、三輪上限與未判定語意保留 | 手冊文字存在；屬人工指引，未量實輪效果，不宣稱收斂改善 |

## 固定合約逐條判讀

| 固定合約 | 本片段判讀 | 理由 |
|---|---|---|
| design-loop 第五步 `.md` 計劃及條款綁測試 | 不影響 | 本片段只更新相關計劃狀態／敘述，未改 KEY、CLI 或測試綁定 |
| search 預設排除 superseded、不排 stale | 不影響 | 無 search 過濾或節點狀態查詢 hunk |
| bound-tests 對固定席綁定測試真跑 | 不影響 | 無 bound-tests 閘、run_cmd 或合約綁定 hunk |
| guard-kill rc 優先序 | 不影響 | 新增的是舊摘要態名事故說明；未改 runtime 或 KEY |
| guard-kill JSON 成功路徑 stdout 純度 | 不影響 | 無 JSON 輸出路徑 hunk |
| 授權檔不得進 `_VENDORED_TOOLKIT` | 不影響 | 無 vendoring／deinit 檔案清單變更 |
| 飄移檔 SPDX 與主程式 MIT 全文 | 不影響 | 無被複製程式或授權檔 hunk |
| 還原翻紅釘必須有現場前置斷言 | 不影響 | 圖譜文字反覆保留前置成立及真斷言要求；但本席未實跑其測試 |

上述「不影響」只限分配的 graph part 1，不代表整個 `c4f2b0cf..HEAD` 無回歸。

## 實跑與效力

- 固定 HEAD：

```text
95735eff7f3e17c930d43eecde5dd9d7c4fe9eff
```

- 12 個本片段節點逐一 `lumos lint` 均輸出 `0 問題`；graph1-F1 證明 lint 綠不等於格式符合人工合約。
- 所列治理／研究引用均存在。
- 未跑全套。
- 未跑兩版本行為案例；檔案系統唯讀，首次 shell here-document 也因不能建立暫存檔而拒絕，因此不把任何筆記收據重新宣稱為本席實跑證據。
- 手冊已靜態包含 repair／preserve、同類與根因分離、分段驗證、完整改動及未判定規則；是否降低輪數、漏報率或修補副作用尚未量測。

## 閱讀帳

指定材料已逐段完整讀取：

- `r3-graph-part-1.patch`：832 行
- `r3-scope-binding.txt`：15 行
- `r3-graph-lens.txt`：57 個邏輯行
- `r3-pitfalls.json`：198 行
- `r3-test-layers.txt`：0 bytes
- `/Users/enzo/.agents/skills/python-idioms/SKILL.md`：233 行
- 合計：1335 個邏輯行

額外上下文：

- `AGENTS.md`：97 行
- `CLAUDE.md`：101 行
- 兩次定點 `rg`：74 個輸出行
- CLI 定點函式片段：216 行
- 顯示總數 488 行；去除重複定位後 472 個唯一行，仍超過 445 上限。

依派工規則，超額涉及的 AST 測試、完整 guard-kill 結果分支及更深呼叫鏈一律列未判定；若要裁定其兩版行為，需另拆唯讀席，不由本席續讀。

最高級：minor  
阻擋數：0  
三問未判定範圍：所有未具同案例兩版來源與本席實跑原輸出的產品修復／保留主張，以及超額未完整讀取的 AST、guard-kill 結果分支與更深呼叫鏈。