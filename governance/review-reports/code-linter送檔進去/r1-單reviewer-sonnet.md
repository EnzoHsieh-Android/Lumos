severity: major

## 發現 1:`_lint_run_and_parse` 新加的 fail-closed guard,把 `lint-check --smoke` 的「零檔案」冒煙路徑變成保證失敗

`_lint_run_and_parse`(`scripts/lumos:17670`)新增:

引句:「if _LINT_NEW_FILES_TOKEN in cmd:」

這段 guard 的用意(給 `_pitfall_diff_collect`/`_lint_new_verdict` 用):佔位符沒被換成真檔名就不要跑,回 `ok=False`,避免「找不到檔」的錯誤被當成一條真發現撐高分級。這個意圖本身是對的。

但 `_lint_run_and_parse` 是全域共用函式,還有第三個呼叫端沒被作者考慮到:`_lintcheck_smoke_cmd`(`scripts/lumos:17289`)。它的既有設計(這次沒改,docstring 原文明寫):

引句:「這個棧在專案裡一支檔都沒有時原樣送出(冒煙只驗得到「命令本身」)。」

也就是說:當一個剛宣告的棧(例如剛裝 `.lumos/lint.json` 加了 `"rs": [...]`,但整個 repo 還沒有任何 `.rs` 檔)在跑 `lumos lint-check --smoke` 時,`_lintcheck_smoke_cmd` 會刻意把命令原樣送出(佔位符不換),目的是至少驗一下「這條命令語法對不對、工具裝了沒」。這條路徑在這次 diff 之前是可以通過的——只要工具本身沒問題。

新加的 guard 讓這條路徑★保證失敗★,不管底層工具是不是完全正常,因為 `_lint_run_and_parse` 一看到 cmd 裡還有 `{LINT_FILES}` 就直接 `return [], False`,連 subprocess 都不會跑。`cmd_lint_check` 把 `ok=False` 一律解讀成:

引句:「冒煙失敗:命令跑不出可解析 SARIF(task 不存在/工具沒裝?)」

——這句診斷是錯的,工具其實是好的,只是專案裡還沒有那個副檔名的檔案。

### 重現(在 `/tmp` 臨時 repo 裡做的,沒有動這個 repo 本身)

```bash
TMPD=$(mktemp -d /tmp/lumos-lint-smoke-XXXX)
cd "$TMPD"
git init -q && git config user.email t@t && git config user.name t
mkdir -p .lumos
cat > .lumos/lint.json <<'EOF'
{"rs": ["python3 -c \"import json,sys; json.dump({'runs':[{'tool':{'driver':{'name':'Fake'}},'originalUriBaseIds':{},'results':[]}]}, open(sys.argv[1],'w'))\" {LINT_SARIF_OUT} {LINT_FILES}"]}
EOF
echo hello > README.md
git add -A && git commit -q -m init
python3 <這次 diff 後的 scripts/lumos> lint-check --smoke --repo "$TMPD" --json
```

現在(HEAD `5c1b6cce`)的輸出:
```
{"problems": [{"stack": "rs", "issue": "冒煙失敗:命令跑不出可解析 SARIF(task 不存在/工具沒裝?)｜..."}], "declared": true}
rc=1
```

同一段腳本、同一份宣告,還原到這次 diff 的上一個版本(`8d6d5ce2`)跑:
```
{"problems": [], "declared": true}
rc=0
```

命令本身(一支永遠成功、輸出合法空 SARIF 的 python 腳本)完全沒變、環境沒變、宣告沒變——差別只在有沒有這次 diff。這是這次改動直接造成的回歸,不是既有問題。

### 為什麼測試沒抓到

新增的 `t_lintcheck_smoke_fills_lint_files`(既有測試,這次沒改)和這次新加的 `t_pitfalls_lint_gets_the_changed_files` 全部只覆蓋「棧裡★至少有一支檔★」的情境。整份 diff 沒有任何測試對應 `_lintcheck_smoke_cmd` docstring 自己講的「這個棧在專案裡一支檔都沒有」分支——我實際跑過 `scripts/test_lumos.py -k lintcheck`,14 案例全線通過,證實現有測試看不到這個洞。

### 影響

`lumos lint-check --smoke` 是這個工具鏈自己文件裡教人「裝好新棧的宣告後拿來驗證」的指令(`scripts/lumos:2564` 附近的引導文字:「跑 lumos lint-check --smoke 驗它真的跑得動」)。剛幫一個新語言/新棧寫好宣告、還沒來得及加第一支該語言的檔案時,這個驗證動作現在★保證回報「跑不動」★,不管工具裝得多好。對照這次要修的原始問題(「linter 那隻手從來沒真的檢查過」),這是同一個症狀家族的新變種:又一個「明明環境是好的,卻被判定為壞」的假陰性,而且是這次改動自己新引進的。

severity: major
blocking: 是

---

## 查證所得(供對照,非發現)

- 針對本輪最該挑戰的問題(「對不齊時 linter 發現不參與分級,會不會讓真正該擋的東西溜過去」):讀了 `_codeloop_guard_verdict`(`scripts/lumos:26388-26406`)確認 `_lint_new_verdict`(新增告警閘)是在 tier 判斷★之前★獨立執行、獨立可以 `blocked:True` 擋下推送,而且它是靠 `_lint_new_extract` 直接從 base_ref/head_ref 兩個 git 版本抓檔案內容來跑,不依賴 `_lint_aligned` 的對齊判斷。也就是說,即使 `pitfalls --diff` 因為工作區髒或範圍不對齊而把 tier 降回 standard,真正新帶進來的告警仍會被 lint-new 閘擋下——作者「真正擋新帶進來的告警的是推送前那道閘,跟對齊無關」這句話,讀程式碼與追蹤呼叫順序後查證屬實,沒發現反例。
- `_intake_declared` 改用 `_visible_lines` 之後,對「四個反引號外、三個反引號內」與「波浪號圍欄」兩種形狀实際 trace 過状态機邏輯,結果與新測試期望一致,沒有讓「原本該擋的模板照抄」重新被判定為算數。
- `_vault_write_lock` 新增的 `_trusted_private_dir(lock.parent, ".cache", "lumos", "vault-lock")` 檢查,傳入的字面段與 `lock.parent`(`Path.home()/".cache"/"lumos"/"vault-lock"`)完全對得上,不會因為段落打錯而誤判;檢查排在 `mkdir` 之後導致的「殘留空資料夾」風險,patch 自己的註解已經誠實揭露、且與既有的 `_lens_arm_dir_ok` 等站點共享同一個既有缺口,不是這次新引入的獨有問題。
- `_lint_stacks_for_diff` 回傳型別從 list 改成 dict 後,逐一查了三個呼叫端(`_pitfall_diff_collect`、`_lint_new_cmd_targets` 內的 for-in、以及測試檔),沒發現還把它當 list 做索引或集合運算的殘留用法;`for cmd in _lint_stacks_for_diff(...)` 這種只迭代鍵的舊寫法在 dict 上行為不變,是安全的。
- `_lint_cmd_with_files` 對含空白/含單引號檔名用 `shlex.quote` 各自跳脫再拼接,人工核對邏輯正確;中文檔名、絕對路徑不受影響。極長檔案清單撐爆命令列長度的理論風險存在,但這是「把檔案清單接進 shell 命令」這個既有共用寫法本身的性質(`_lint_new_verdict` 原本就有一樣的接法),不是這次重構新引入的獨有缺陷,故未單獨列為發現。
