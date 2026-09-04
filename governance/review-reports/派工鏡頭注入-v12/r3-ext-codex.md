### f1

引句:「共用 deadline:備援段開始時取單調時鐘 30 秒 deadline」

file: `scripts/lumos:13422`

severity: blocker

blocking: 是

deadline 只規定在每次 `git show` 前檢查，但 `_cochange_mine` 內的 `git rev-parse`、`git log` 均無 timeout，單次即可無限卡住；即使 `git show` 沿用 `_lens_git` 的 20 秒 timeout，最後一次呼叫也可越過 30 秒才返回。因此照字面做無法兌現整段超時降級。

### f2

引句:「沿 `cmd_testmap_build` 既有的檔↔測試比對邏輯」

file: `scripts/lumos:14446`

severity: major

blocking: 是

此宣稱與 repo 現況不符：既有 testmap 用 `_testmap_is_test`、固定 `_TESTMAP_EXTS` 和檔名／目錄規則分類，完全不讀 test profile 的 `file_name_match`，也不抽取測試方法。第三版實際要求的是拼接 testmap 與 `discover_test_methods` 的新演算法，不能稱為沿用既有檔↔測試邏輯。

### f3

引句:「輸出只有 base 已追蹤檔名、base 版測試方法名與識別字、整數、固定字串」

file: `scripts/lumos:2455`

severity: blocker

blocking: 是

「測試方法名」不是安全 token：Kotlin 既有 regex 接受反引號內任意非反引號文字，包含空白、換行及完整派工指令；base profile 的自訂 `method_regex` 也能把任意內容捕獲為 group 1。若不另加單行識別字白名單與長度限制，新增輸出會成為自由文字注入管道。

最高 severity: blocker；共 3 條 finding，blocking 2 條；r2 四條中 3 已解、1 未解。
