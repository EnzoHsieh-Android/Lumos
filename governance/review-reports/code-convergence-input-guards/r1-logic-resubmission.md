severity: major

格式退回重送：本報告只修正引句格式與已讀材料清單，不增刪 finding、不變更 severity、blocking、判準或原證據。`r1-logic-raw.md` 原報仍保留，未覆寫。

## correctness-F1

severity: major  
blocking: 是

引句:「result.returncode == expected, result.stdout + result.stderr」

觀察：N 的 18 組控制全部只核對最終 rc。`ignored-test`、`symlink-test`、`json-home`、`diff-split`、`shebang-index-negative` 等負控制沒有先斷言目標測試確實位於該版本的改動集合、確實由目標節點持有，也沒有核對 stderr 的具體拒收種類與路徑。這違反固定席正式合約「還原翻紅釘必須配前置斷言證明現場成立」。舊碼紅燈及兩個 mutant 收據能證明目前 fixture 有殺傷力，但不能取代測試內的持續前置守衛。

判準：若 `ignored-test` 同時出現另一支新增無家的程式檔，即使路由錯誤地接受 ignored 測試，CLI 仍會因 `new-homeless` 回 rc1；目前測試會把這個錯結果當成預期成功，形成假綠。

具體輸入 → 錯結果 → 可執行證據：

- 在 `ignored-test` fixture 額外加入未安家的普通程式檔，並建立只移除 route 分類之 ignore 排除的 mutant。
- 正確結果應顯示 ignored 測試不能成為路由證據；目前 oracle 只看 rc1，會被另一個 `new-homeless` 擋項遮蔽。
- 應先斷言索引／提交的實際 `g_paths`、TestHome 的 `about_code` 與啟動用 production 變更，再核對唯一預期的 route 診斷、節點及路徑；shebang 兩案另應直接斷言索引與工作目錄首行相反。

file: `scripts/test_lumos.py:48062`  
file: `docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md:25`

本席為唯讀且沒有可寫的自有 tmp，因此未實跑上述 mutant；這是依正式合約及測試 oracle 的靜態重現，不冒稱實跑。

## 資料狀態五問

- 新舊互讀：H 的引句與初次 SHA 來自同一份 bytes，之後再雜湊核對；N 對每個 group 讀該提交與所有父版，未見端點借證據。
- 半寫：H 的解碼或首次 I/O 失敗立即 rc2；N 的版本清單讀取失敗會清空 `route_tests`，回到原拒收路徑。
- 衍生資料：H 的 `_quote_rows` 與 `_validated_sha` 同源；N 沿用既有 regular-file、測試分類、ignore、vendor、UTF-8 與 shebang 判定，未建立第二套 owner/classifier。唯一缺口是 F1 的測試證據本身可能被其他 rc1 遮蔽。
- 時間：H 明確拒絕一次性讀取失敗後再成功；N 的提交清單與 shebang 快取按版本 SHA 隔離，未見跨版本污染。
- 不可逆：H 在首次讀取、解碼、引句核對及第二次雜湊一致前不追加成功 canary；既有 Governance blocked 事件未被錯誤擴成禁止。N 僅改路由判定，不寫資料帳。

## 固定席節點判定

- `Systems/design-loop.md`：不影響處置閘第五步的計劃格式、條款綁定或回退規則。
- `Systems/pitfalls-code-loop.md`：未改風險分級入口；無附加正式硬合約。
- `Systems/bound-tests-gate.md`：未改合約測試選取、實跑或 blocked 判定。
- `Systems/guard-kill.md`：未改 rc 優先序或 JSON stdout 純度。
- `Systems/授權與歸屬.md`：未動 vendored toolkit 清單、授權檔刪除或程式檔頭。
- `Systems/測試假綠形態.md`：被 correctness-F1 破壞。
- `Systems/lumos-cli-read.md`：未改 search 的 superseded/stale 濾網。
- `Systems/lumos-cli-lifecycle.md`：未改 re-inject sentinel 外內容。
- 其餘只列名節點依派工規則未展讀，也未拿歷史 scope 冒充正式合約。

## 本次格式接收席實際已讀材料

以下只陳述本次格式接收席的實際讀取，不聲稱原正確性席讀過：

- 原始報告：`governance/review-reports/code-convergence-input-guards/r1-logic-raw.md`
- 派工：`governance/review-reports/code-convergence-input-guards/r1-dispatch.json`
- source：`governance/review-reports/code-convergence-input-guards/r1-source.patch`
- graph：`governance/review-reports/code-convergence-input-guards/r1-graph.patch`
- source lens：`scripts/lumos`、`scripts/test_lumos.py` 的本案變更相關區段
- graph lens：`governance/review-reports/code-convergence-input-guards/r1-graph-lens.txt`
- full-index：`governance/review-reports/code-convergence-input-guards/r1-file-index.txt`
- pitfalls：`governance/review-reports/code-convergence-input-guards/r1-pitfalls.json`
- dispositions：`governance/review-reports/code-convergence-input-guards/r1-dispositions.json`
- test layers：`governance/review-reports/code-convergence-input-guards/r1-test-layers.txt`（空檔）
- 入口：`CLAUDE.md`、`docs/lumos-toolchain-knowledge/MOC/index.md`
- full snapshot：未重審卷證；只核對 `r1-file-index.txt` 索引及 `r1-snapshot.patch` SHA-256，實際值 `c137531fdc524a6ef2e788cee5bde9661b82891eaba6dd4ff4ad8bdcbc3d7afd`，與派工 `reviewed` 相符

替代引句已用同一凍結 snapshot 執行 quote-check，結果全數錨定。

最高級：major  
blocking 數：1