找到 2 條 blocking finding。

1. blocking: 是  
判準句：照字面把 disposal 寫成「blocker 折掉後，其餘 major 可附理由接受」，會被目前實作拒絕；只要同輪曾有 blocker，整輪 `accepted` 必須為空。  
群標：structural  
逐字引句：「disposal=發現全折或附理由接受、major 可 accepted、blocker 必折」  
查證：

- `/tmp/prose-convergence-v2-r1.md:30`
- `scripts/lumos:10021-10033`

問題：稿件描述的是逐 finding 規則；實作卻是輪級規則：`AC and any(... severity == "blocker")` 即失敗。因此同輪 `blocker B1` 已 folded、`major M1` 有理由 accepted，集合雖全處置，仍不能過閘。[S2] 若照稿件寫判詞，會直接教出被 CLI 擋下的記帳行為。應明寫：「同輪有 blocker 時，所有 findings 都只能 folded；該輪不得有任何 accepted。」

2. blocking: 是  
判準句：照字面以「單輪 blocking >1／300 字」判整份重寫，會把歸檔的殘餘 major 密度／inspection page 起步線，改造成沒有來源的單輪發現密度與自行定義頁長，實際觸發行為不同。  
群標：evidence  
逐字引句：「單輪 blocking 密度極高(暫用門檻:>1 條/邏輯頁,1 頁≈300 字;Gilb 起步線」  
查證：

- `/tmp/prose-convergence-v2-r1.md:36`
- `/tmp/prose-convergence-v2-r1.md:53`
- `governance/review-reports/prose-convergence/web-research.md:6`
- `governance/review-reports/prose-convergence/web-research.md:14-15`

問題：歸檔記的是「殘餘 major 密度」退出線，數字為 0.1、0.25、最寬 1 條／頁；另只定性說密度太高時重寫。歸檔沒有：

- 把「殘餘 major」改成「單輪新發現 blocking」
- 把 inspection page 定義成 300 中文字
- 證明 `>1/頁` 就是 Gilb 的重寫門檻

所以「Gilb 起步線」是不忠實的來源標示；標成暫用、待 S6 校準，仍不能消除首次實作會錯觸發重寫的問題。應改稱「本案自行提出的暫用 heuristic」，或另補可核來源與單位換算。

其餘指定核點：

- panel 分寫正確：無 cluster 路徑確為每輪 `max severity ≤ minor`，K=2 要最後兩輪各自通過，見 `scripts/lumos:3759-3794`、`3897-3923`。
- d2 與 K=2 沒找到 blocking 級矛盾：稿件保留全量材料，新 minor 仍報告、記帳並標 non-blocking；機械閘本來允許 minor。它是審查火力政策，不是新增第三道 gate。
- 「六處機械依賴全不動」完整涵蓋 r1 指控：fold-check 鏡像段、排除 regex、pitfalls blacklist、中斷恢復、G3 單檔保護、quote-check 快照材料六項皆有對應；未發現漏項。

最嚴重是否 blocking：是。最嚴重為第 1 條，因為它會讓文件明教的合法 disposal 記帳被現行 CLI 必然拒絕。
