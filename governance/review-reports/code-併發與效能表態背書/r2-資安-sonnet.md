severity: clean

已看範圍:/tmp/cpe/code-r2-snapshot.patch 的 scripts/lumos 全部新增段落(kill、kill-add、背書計算、`_codeloop_record_valid_ex`、`_backing_kill_rows`),另看 r2 修正差異與上輪資安席報告。

### 1. 不可信輸入流到危險操作
已看,無。上輪 S1 已修:`_backing_kill_rows` 只收完整 40 或 64 碼小寫十六進位 head_sha,只進 git merge-base --is-ancestor 與 git diff --no-ext-diff --raw --no-renames -z 兩處,不會被當成選項。
引句:「_FULL_SHA_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")」
繞過嘗試:$ 會放過結尾換行,sha+"\n" 可以過正則,但值在 list argv、不經 shell,git 解析失敗回 unsure、整題 none,沒有注入路徑。kill-log 的 test/platform/recipe_id/covers 只做比對與分組;執行用方法名仍過 `_KILL_METHOD_OK_RE`;--raw -z 解析不對路徑做檔案操作;node_dirty 的 git status 用 list argv 並有 -- 隔開;--covers 只收已知且標 needs_backing 的 id;全程 json.loads、無 pickle/eval。

### 2. 登入與權限
已看,無。背書只進 warnings,kill-log 被偽造頂多讓提醒消失或變 strong,不能繞過任何擋下的閘。

### 3. 密鑰與個資
已看,無。

### 4. 加密與傳輸
已看,無。sha256 只當配方身分。

### 5. 執行邊界
已看,無。沒讓 hook 或 CI 執行不可信位置的檔;沙盒用本機 rev-parse 的 ghead、list argv;run_cmd 展開沿用既有;版本驗證有預算與 timeout,判不了整題 none。

### 6. 行動端
不適用,已看。

新依賴:已看,無。

最高嚴重度:clean,blocking 0 條
