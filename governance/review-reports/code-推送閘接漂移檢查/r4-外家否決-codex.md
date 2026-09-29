severity: minor

## F1 分岔點計數逾時後仍任選起點，可能漏掉漂移
severity: minor
blocking: 否
引句:「n = int(r.stdout.strip()) if (r is not None and r.returncode == 0 and r.stdout.strip().isdigit()) else -1」
file: `scripts/lumos:33258`

1. 新增邏輯用 `git rev-list --count` 選歷史最長的分岔點，但查詢逾時或無法執行時只把計數設成 `-1`，沒有回傳 `_PUSH_START_UNKNOWN`。
2. 具體輸入：新分支首推，同時合入兩條互不包含的主線，`merge-base --all` 得到 `B_short`、`B_long`；`B_long` 歷史較長，但它的計數查詢逾時。程式會選計數成功的 `B_short`，違反本輪宣稱的「取歷史最長」與「git 逾時算判不了」。
3. 若 `B_short` 的筆記狀態已與頂端相同，而 `B_long..頂端` 才包含應攔截的狀態轉換，錯誤起點會讓 block 模式回 0；CI 和 pre-push 都可能漏擋。應讓任何分岔點計數失敗直接進入「判不了」分流。
4. 未能重現：唯讀沙盒禁止建立規則要求的臨時 clone；因此依規則下調一級。

## 圖譜鏡頭逐條判定

- `Issues/code-loop守衛main-direct盲區`：不影響；本次沒有改動 code-loop 的逐 ref 範圍或 main-direct 判定。
- `Systems/存量漂移守衛`：受 F1 影響；分岔點計數逾時沒有依其 fail-closed 規則轉成「判不了」。
- `Systems/每支檔有家`：不影響；home check 仍使用原本的範圍算法。
- `Systems/筆記內容閘`：不影響；note-shape 的判定與接線沒有變更。
- `Systems/測試假綠形態`：既有新增測試均有現場前置斷言，但沒有涵蓋 `rev-list --count` 逾時後的分流。
- `Systems/anchor-integrity`：不影響；`scripts/test_lumos.py` 的雜湊與基準一致，`anchor verify` 顯示 12 個驗證器全部通過。
- `Systems/lumos-cli-lifecycle`：不影響；未碰 re-inject 或 CLAUDE.md sentinel 行為。
- `Systems/lumos-cli-read`：不影響；未碰 search 對 superseded／stale 的過濾合約。

最高等級:minor