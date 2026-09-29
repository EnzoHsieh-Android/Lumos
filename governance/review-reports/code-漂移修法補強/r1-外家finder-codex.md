severity: major

## F1 改名離開工具自裝路徑時，刪除守衛仍抽出舊檔符號

severity: major
blocking: 是
引句:「+            cur, is_vault, is_excl = _delguard_path_flags(ln, graph_root)」
file: `scripts/lumos:29356`

1. `cmd_delguard_check` 使用 `git diff -M`，改名 diff 的檔頭同時包含舊路徑與新路徑；但 `_delguard_path_flags` 只讀 `b/` 新路徑。當 `scripts/lumos` 改名到非白名單路徑時，屬於舊工具檔的 `-` 行因此不會命中 `vendored_skip`。
2. 唯讀最小重現：

   ```text
   diff --git a/scripts/lumos b/src/old-lumos
   rename from scripts/lumos
   rename to src/old-lumos
   --- a/scripts/lumos
   +++ b/src/old-lumos
   @@ -1,2 +1 @@
   -def zzVendoredGone():
    x = 1
   ```

   執行：

   ```python
   _delguard_parse_diff(diff, "docs/x-knowledge",
                        frozenset({"scripts/lumos"}))
   ```

   實際輸出：

   ```text
   {'tokens': ['zzVendoredGone'], 'vault_diffs': {}, 'vendored_skipped': []}
   ```

   預期 `tokens` 為空，且 `vendored_skipped` 記下 `scripts/lumos`。目前會繼續產生本功能原本要消除的誤報，治理事件也漏記 `vendored-skip=`，違反 S5。
3. 新測試只覆蓋同路徑修改，沒有覆蓋 `rename from` 與 `rename to` 不同的分支。解析時應分別保存 `a/`、`b/` 路徑：`-` 行依來源路徑判斷，`+` 行依目的路徑判斷。

## 圖譜鏡頭逐條判定

- `Systems/存量漂移守衛`：c1、c3、c4 的改動與 S1–S4 一致；未另見錯誤分支。
- `Systems/bound-tests-gate`：未改動合約測試的發現、執行或阻擋判定。
- `Systems/guard-kill`：只改 settle 缺句訊息；kill 回傳碼優先序與 JSON 純度未受影響。
- `Systems/授權與歸屬`：未修改 `_VENDORED_ALL` 的內容或 deinit 刪除流程，兩條授權合約未受影響。
- `Systems/測試假綠形態`：新增測試均有現場前置斷言，但 S5 測試未進入改名分支，因而漏掉 F1。
- `Systems/lumos-cli-read`：搜尋與 superseded/stale 過濾路徑未改。
- `Systems/lumos-cli-lifecycle`：re-inject 與 sentinel 外內容保留邏輯未改。
- `Systems/design-loop`：處置閘與審材類型判定未改。

## 驗證

- 已用唯讀、記憶體內載入方式重現 F1。
- delguard 無跳過參數時，舊版與新版解析器對 1,000 組合成 diff 的輸出一致，未發現拆函式造成的其他行為漂移。
- 專案測試子集未能執行：唯讀沙盒沒有可寫暫存目錄，測試入口在建立隔離目錄時回報 `FileNotFoundError: No usable temporary directory found`。

最高等級:major