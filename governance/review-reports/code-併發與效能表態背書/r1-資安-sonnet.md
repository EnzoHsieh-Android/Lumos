severity: minor

已看範圍:/tmp/cpe/code-r1-snapshot.patch 全文;重點 scripts/lumos 的 kill、kill-add、背書計算與 `_codeloop_record_valid`。

### 1. 不可信輸入流到危險操作

**S1(縱深防禦,推論)**
severity: minor
blocking: 否
- 誰:能往 PR 提交 docs/.kill-log.jsonl 的攻擊者。
- 入口:`_backing_kill_rows` 讀進的 head_sha 沒有格式驗證,直接交給 `_codeloop_record_valid`,進 git merge-base --is-ancestor 與 git diff --name-only。
- 送什麼:head_sha 寫成 --output=/path 這類以 - 開頭的字串。
- 拿到什麼:若一路走到 git diff,理論上可用 --output 覆寫任意檔。
- 實測:--output=/tmp/x、--all、--octopus、--independent、--fork-point 餵給 git merge-base --is-ancestor 全部 rc=129,程式在 rc 不是 0 或 1 時提早 return,git diff 碰不到。現況無法利用。
- 建議:對 head_sha 加 ^[0-9a-f]{7,64}$ 檢查,或 git 參數前加 --end-of-options,不靠 merge-base 錯誤碼當唯一屏障。
引句:「if not r["head_sha"] or not r["recipe_id"]:」
file: `scripts/lumos`(patch 內 `_backing_kill_rows`)

其他已看,無:沙盒的 ghead 來自本機 rev-parse;配方方法名仍過 `_KILL_METHOD_OK_RE` 白名單;--covers 只接受已知 id;covers 寫入前過濾成字串;`_kill_recipe_key` 用 json.dumps 再 sha256;node_dirty 的 git status 是 list argv;全程 json.loads、無 pickle/eval。

### 2. 登入與權限
已看,無。

### 3. 密鑰與個資
已看,無。新欄位與 backing 只含狀態、原因短句、截斷的 first_note(人寫的業務說明)。

### 4. 加密與傳輸
已看,無問題。sha256 只用於配方身分,不是安全邊界。

### 5. 執行邊界
已看,無。run_cmd 展開沿用既有 `_run_cmd_expand`;補換行路徑固定;沒寫全域設定;背書只進 warnings,kill-log 被偽造最多讓提醒消失,不能繞過任何擋下的閘。

### 6. 行動端
不適用,已看。

新依賴:已看,無,只用標準庫。

最高嚴重度 minor,blocking 0 條。
