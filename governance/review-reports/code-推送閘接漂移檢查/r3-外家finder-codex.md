severity: minor

## F1 單獨傳入 `--push-remote` 會漏查主線推送

severity: minor

blocking: 否

引句:「push = None if (push_remote is None and pushed_ref is None) else (push_remote or "", pushed_ref or "")」

file: `scripts/lumos:28247`  
file: `scripts/lumos:28258`  
file: `scripts/lumos:33127`  
file: `scripts/test_lumos.py:51227`

1. CLI 文件宣稱帶 `--push-remote`「或」`--pushed-ref` 就進入推送範圍模式，parser 也允許只給其中一個。
2. 只給 `--push-remote origin` 時，`pushed_ref` 被轉成空字串，`_push_mainline()` 無法知道目前推的是 `main`，因此不會跳過 `origin/HEAD`／`origin/main`。
3. GitHub Actions checkout 後，這些 ref 可以已指向本次頂端；接著 `_push_range_start()` 判定「頂端已在主線」，回傳 `None`，整道漂移檢查放行。本次 `OLD..TIP` 內即使有應擋的轉正事件也不會檢查。
4. 內建 pre-push、CI 與現有測試都同時傳兩個旗標，所以正式接線不受影響；問題落在 CLI 公開允許的單旗標路徑。應要求兩個旗標同時出現，缺一時回參數錯誤，或讓缺少 `pushed_ref` 時不得使用「頂端已在主線」的捷徑。

唯讀重放把遠端主線 refs 模擬成 Actions checkout 後都指向 `HEAD`，其餘使用真 `_push_range_start()` 與 Git 祖先判定：

```text
only --push-remote: (None, '頂端已在主線(refs/remotes/origin/HEAD)上——沒有新東西')
both flags: ('fc25e1e45db3295ae235bc2b4714b8bfb6d0108d', '找不到主線(遠端預設分支、main/master 的 upstream、遠端 main/master 都沒有,或就是這次推的分支),用遠端舊值 fc25e1e45db3 當起點')
```

## 圖譜鏡頭逐條判定

- `Issues/code-loop守衛main-direct盲區`：不影響；code-loop 仍使用逐 ref 的遠端舊值至本地新值，沒有退回 merge-base==HEAD 的舊盲區。
- `Systems/存量漂移守衛`：正式 pre-push／CI 接線同時傳兩個旗標，符合 [S1]；公開 CLI 的單旗標路徑有 F1。
- `Systems/每支檔有家`：不破壞判定；只新增訊號回傳碼的停下處理。
- `Systems/筆記內容閘`：不改 note-shape 範圍與判定；訊號中斷不再被當成放行。
- `Systems/測試假綠形態`：新增測試有現場前置斷言及舊算法對照，但只測兩個推送旗標一起傳，未覆蓋 F1。
- `Systems/anchor-integrity`：`lumos anchor verify` 實跑通過，12 個驗證器檔案與基準線一致。
- `Systems/lumos-cli-lifecycle`：未碰 re-inject 與 sentinel 外內容，合約不受影響。
- `Systems/lumos-cli-read`：未改 search／superseded 過濾，合約不受影響。
- `Systems/bound-tests-gate`：code-loop、合約測試及 drift check 的相對順序維持；沒有改其判定。
- `Systems/canary-audit`、`Systems/design-loop`、`Systems/guard-kill`：無相關執行路徑變更。
- `Systems/slim-get-一行安裝`、`Systems/slim-install-安裝器`、`Systems/slim-uninstall-一行卸載`：未改安裝或卸載內容。
- `Projects/規格落成可驗收條件_計劃`、`Projects/雙向門放行_計劃`、`Projects/逃逸自動記_計劃`：spec-gate、逃逸記帳與其判定未變；只在訊號退出時停止後續執行。
- `Systems/lumos-deinit`、`Systems/cochange-guard`、`Systems/節點範圍與索引守衛`、`Systems/check-r-guard`：未見受改動分支影響。

唯讀檢查另確認：`git diff --check`、hook 的 `bash -n`、兩支 Python 檔的記憶體編譯均通過。完整測試會建立暫存 repo，依唯讀限制未執行。

最高等級:minor