preflight-4: ran

# r2 前置留痕(lens-stage0)

只審 r1 修正 commit 6bcd0d5 的 delta(r2-snapshot.patch);r1 28 條全折後的回歸掃。測試:新加 3 支+既有 hook 10 支綠。

## 收貨三道(六席,delta=6bcd0d5)
| 席 | 條數 | 最高 | blocking | quote | 鏡頭 |
|---|---|---|---|---|---|
| s1 正確性 | 3 | major | 1 | 全錨 | 是 |
| s2 併發資源 | 2 | major | 0 | 全錨 | 是 |
| s3 邊界輸入 | 6 | major | 3 | 全錨 | 是 |
| s4 合約圖譜 | 8 | major | 1 | 全錨 | 是 |
| s5 通才 | 3 | major | 0 | 全錨 | 是 |
| arch | 1 | minor | 0 | 全錨 | — |
合計 23(3+2+6+8+3+1)/blocking 5/major 7。r1 修復驗收:六席皆「真修」。
## 處置
23 條全折(輪內有 major,accepted 必空):TTL 擁有權 token(s2-f1)、引號外才認重導向(s1-f1)、python -c 單行(s1-f3)、<<< 非 heredoc/shlex 失敗退回/子殼括號(s3-f1..f3)、變數追蹤就近判(s5-f1)、接線測試五出口(s5-f2)、scan_file 撞名測試(s5-f3)、計劃矛盾句+REVISIT 獨立行+驗證 1593/1600+docstring(s4-f3/f5/f6/f7)、try/finally 形態(arch-f1:五處守衛保留,列 minor 不改——hooks 家族無 try/finally 先例)。修正 commit 310c8f3 + 補 1 筆。
