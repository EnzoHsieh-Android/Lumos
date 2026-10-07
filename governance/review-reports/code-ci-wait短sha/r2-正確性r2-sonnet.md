severity: minor

## F1 尾端換行的完整 sha 會被當成已是完整碼直接放行
severity: minor
blocking: 否 — 只有 --sha 帶尾端換行(例如 shell 變數沒修剪)才觸發,結果跟修正前一樣查不到、判 no-run,不比原本更糟;沒有資料損壞或誤判綠
引句:「    if _LENS_SHA_RE.match(sha):」
重現:`python3.14 -c "import re;R=re.compile(r'^[0-9a-f]{40}$|^[0-9a-f]{64}$');print(bool(R.match('a'*40+'\n')))"` 印 True(Python 的 `$` 會匹配尾端換行前)。所以 `--sha "<40碼>\n"` 不走 _lens_full_sha、原樣交給 run list。file: `scripts/lumos:43926`、`scripts/lumos:41835`。這是既有 _LENS_SHA_RE 的特性(其他呼叫點多用 fullmatch,本處用 match);可改 fullmatch 或先 strip。

## 已讀無 finding 的項目
- 大寫完整 sha:不符小寫正規式,轉交 _lens_full_sha;git rev-parse 接受大寫並回小寫完整碼,結果是被換成小寫(比原本只會查不到好)。引句:「    full = _lens_full_sha(root, sha)」
- 帶空白或其他字元:rev-parse 失敗 → None → rc2 並列三種可能,不會 traceback;與 cmd_ci_wait 既有的 stderr-only rc2 路徑一致(見 `scripts/lumos:41877` 一帶 --repo-dir 錯誤)。引句:「        print(sha_err, file=sys.stderr)」
- 逾時 20 秒對 30 秒:本機 rev-parse --verify 毫秒級,逾時回 None 走「git 跑不起來」分支而非崩潰;沒人依賴到 20~30 秒區間。引句:「    if r is None or r.returncode != 0:」(`scripts/lumos:44181`)
- _LENS_SHA_RE 定義位置:第 43926 行是模組層級,執行時 cmd_ci_wait 由 main 分派(`scripts/lumos:50032`)才呼叫,模組已完整載入,無 NameError。引句:「_LENS_SHA_RE = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")」(不在 diff 內,僅供佐證)
- 完整 40 碼但本機沒有的提交(只在遠端):直接放行不換,維持原行為,不誤擋。引句:「        return sha, None」
- 副作用:--sha 也接受 HEAD~1、分支名並被換成完整 sha(以 `^{commit}` 解析),屬可接受的放寬。
- 測試:帶 --grace 0 且驗 d["sha"]==full;第二案 deadbeef 本機不存在 → rc2。引句:「    r = _ci_run(root, v, env, "ci-wait", "--json", "--sha", "deadbeef")」

資料狀態五問:
1. 空/缺值:--sha 空字串走 HEAD 分支,取不到維持 unavailable。
2. 大小寫/格式:大寫被 rev-parse 正規化;尾端換行見 F1。
3. 重複/歧義:短碼對到多個 → rev-parse 失敗 → rc2 並提示(原因文字涵蓋)。
4. 缺席:本機沒有提交 → rc2 提示 git fetch。
5. 逾時/外部失敗:git 逾時回 None → rc2 訊息涵蓋「git 跑不起來」。

總結:只找到一處可忽略的小瑕疵(尾端換行匹配),其餘路徑行為正確。
