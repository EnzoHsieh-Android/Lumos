severity: minor

已看範圍:
- /tmp/cpe/code-r3-snapshot.patch 中 `scripts/lumos` 的全部 hunk:gov 讀帳、kill-add 的 covers、guard kill 的沙盒與 kill-log 新欄位、背書算法(`_backing_*`、`_contract_backing_*`)、`_codeloop_record_valid_ex`、`_codeloop_bookkeeping_code`、`_dispositions_verdict` 的 `_backing_warn`、argparse。
- 文件與 SVG 的 diff,以及 `scripts/test_lumos.py` 的新增測試(只掃過,不報測試假資料)。
- repo 內佐證:`_drift_jsonl_parse`、`_drift_jsonl_rows`、`_stack_spec_by_id`、.gitignore 注入段、`git ls-files` 的 kill-log 追蹤狀態。
- 沒看 /tmp/cpe/code-r3-fold.patch:它只是參考,而且不是引句來源。

**R3S1**
severity: minor
blocking: 否。只是縱深防禦:偽造的背書只能壓掉一行「只提醒」的警告,而且這支 diff 沒有任何地方靠背書放行或擋推送。
- 誰:對本 repo(kill-log 是被追蹤的檔)投稿的外部第三方。
- 入口:PR 裡改 `docs/.kill-log.jsonl`。
- 送什麼:幾行偽造的 JSON。
  - `head_sha` 填一個真實存在、是當前提交祖先的完整 sha。
  - `test` 與 `platform` 對上要背書的測試。
  - `verdict` 填 `killed`,`weak` 填 `false`,`covers` 填目標題號,`recipe_id` 隨便填。
- 原因:`_backing_kill_rows` 只驗欄位型別和 sha 格式,沒有跟筆記裡真正的 `kill_recipes` 對帳,也沒驗這行是不是 `guard kill` 真的寫出來的。
- 拿到什麼:維護者在本機跑 `lumos code-loop dispositions` 時,這題被記成 `backing.strong`。
  - `_backing_warn` 不再印「沒有破壞測試背書」。
  - 派工鏡頭對審查席印「背書:強證據」。
  - 偽造行的 `note` 欄(取前 40 字)會原樣進審查席的提示,等於給審查席一條低頻寬的提示注入通道。
- 緩解(已確認):
  - 消費專案的 .gitignore 會忽略 kill-log,所以這條只在 kill-log 被追蹤的 repo 成立(例如本 repo)。
  - 讀檔不跟符號連結,偽造的檔無法借此讀別處的檔。
  - 手填或 `--carry` 帶來的 `backing` 已被 `_backing_mark` 先全部拿掉,表態檔本身偽造不了背書。
- 建議:在算背書時,把 `recipe_id` 對回筆記現有的 `kill_recipes`,並用 `covers` 取自筆記而不是取自 kill-log 這一行;審查席提示裡的 `first_note` 只取自筆記。
引句:「for r in _drift_jsonl_rows(Path(repo_root) / "docs" / ".kill-log.jsonl"):」
file: `scripts/lumos:28954`

逐類結論:
1. 不可信輸入流到危險操作:已看,無可利用。
   - kill-log 的 `head_sha` 先過 `^(?:[0-9a-f]{40}|[0-9a-f]{64})$` 才進 `git merge-base --is-ancestor` 和 `git diff` 的 argv,不可能以 `-` 開頭,也不是 shell 插值(argv 列表,無 `shell=True`)。
   - `$` 會放行結尾多一個換行的字串,但那只會讓 git 回 128、判成無效,不構成注入。
   - `--covers` 的值用 `_stack_spec_by_id` 白名單驗過才寫進 frontmatter。
   - 表態檔的 `evidence` 只做字串比對,不進路徑或命令。
   - `worktree add` 的 sha 來自 `rev-parse HEAD`,不是帳檔。
   - 沒有反序列化和 eval,只有 `json.loads`。
2. 登入與權限:已看,繞不過會擋推送的閘。背書只進 `warnings`,不進 `problems`,不改 `blocked`;`_backing_warn` 自己吞掉所有例外,也沒有 fail-open 路徑。偽造的影響只有 R3S1 那一條。
3. 密鑰與個資:已看,無。新增的訊息只有例外類名和截斷後的 `reason`,沒有環境變數或 token。kill-log 的 `tail` 是既有欄位。
4. 加密與傳輸:已看,無。`recipe_id` 用 sha256,僅作分組鍵,不是安全用途。沒有隨機數。
5. 執行邊界:已看,無新增。
   - 沙盒仍然執行消費專案 config 的 `run_cmd`,但這是既有行為,這支 diff 沒有放大。
   - 沙盒路徑用 `mkdtemp`;沒有寫使用者全域設定。
   - gov 改成逐行容錯讀,解碼用 replace,是縮小攻擊面的修法。
6. 行動端:不適用。
7. 新增依賴:無。只有 stdlib 的 hashlib 與 time。

最高嚴重度:minor,blocking 0 條
