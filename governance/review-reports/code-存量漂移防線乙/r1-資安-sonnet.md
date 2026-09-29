severity: clean

## 審查範圍與角色
以攻擊者視角看這份 diff(存量漂移防線「乙」:條件式回頭條件 `REVISIT:[when-*:...][by:...]`)。核心風險假設是:條件標記的值(`when-file`/`when-symbol`/`when-test`/`when-status`)來自筆記內容,筆記可由任何有提交權限但未必受信任的協作者寫入,屬外來輸入。逐類檢查如下,均已看,無 finding。

## 1) 不可信輸入流到危險操作
已看,無 finding。

- `when-file`/`when-symbol`/`when-test` 的值最終只用在兩種地方:(a) 集合成員判斷 `v in self.files`;(b) 字典查找 `corpus.get(path)`。兩者都不會拿筆記裡的字串直接組路徑去讀磁碟或當 git ref 用。
  引句:「paths = sorted(p for p in self.files if _nodehome_code_kind(p) == "ext"」
  引句:「out[p] = (Path(self.root) / p).read_bytes()」
  第二句的 `p` 來自第一句過濾後的 `paths`,而 `paths` 的來源是 `self.files`——建構於 `_nodehome_list`(`git ls-files -s -z` / `git ls-tree -r -z`),只收 mode 為 `100644`/`100755` 的一般檔(連結檔 120000、子模組 160000 都被排除),也就是 git 自己認得的追蹤檔清單,不是筆記字串直接餵給檔案系統。實測:
  file: `scripts/lumos:22786`(`_nodehome_list`:`files[path] = mode.decode()` 只收 `100644`/`100755`)
  file: `scripts/lumos:25787`(`self.files = set(lst[0]) if lst else set()`)
- 就算 `when-file`/`when-symbol`/`when-test` 寫成 `../../etc/passwd` 這種穿越字串,也在讀之前先被擋:
  引句:「p.startswith("/") or ".." in p.split("/")」
  這段 `_probe_bad_path` 在 `_probe_value_err`/`_probe_named_err` 裡對 `file`/`symbol`/`test` 三種鍵都會呼叫,而 `_drift_probe_check`、`_drift_probe_scan` 在真的呼叫 `.one()`/`.line()` 評估條件之前,都先用 `_probe_value_err` 篩過一輪(壞值的行整條不評估):
  引句:「lines = [x for x in lines if x[3]["conds"] and all(_probe_value_err(k, v) is None for k, v in x[3]["conds"])]」
  引句:「if not pr["conds"] or any(_probe_value_err(k, v) for k, v in pr["conds"]):」
  即使假設 `_probe_bad_path` 漏放了某個穿越字串,實際讀取仍必須先出現在 `self.files`(git 追蹤清單)裡才會被讀進 `corpus`;筆記字串本身從未被當成檔案系統路徑直接組合讀取,只當 dict key 查表,查不到就是 `None`,不會旁落讀到 repo 外的檔。屬雙重防線,沒有可重現的繞過路徑。
- git 呼叫全部用參數列表(`subprocess.run(cmd + list(args), ...)`),沒有 `shell=True`,`re.escape()` 用於把 `symbol`/`test` 的名稱組進正則,沒有把筆記字串直接編譯成不受控的正則語法:
  引句:「word = re.compile(rf"(?<![\w]){re.escape(name)}(?![\w])")」
  file: `scripts/lumos:30923`(`_lens_git`:`cmd = ["git", "-C", str(repo_root)]` + `list(args)`,無 shell 字串拼接)
- `--probes` 改寫檔用 `json.loads` 讀,不是 `pickle`/`eval`,且 `_drift_exam_probe` 明確只在記憶體換字串,不寫回被考 repo:
  引句:「不改被考 repo(只在記憶體裡換)。」

## 2) 登入與權限
已看,無 finding。這份 diff 不涉及任何登入態、token 或權限判斷邏輯;`_drift_probe_check`/`_drift_probe_scan` 能讀到的程式檔範圍,就是呼叫者本來就能用 `git show` 讀到的同一份 repo 樹狀態,沒有新增讀取範圍或繞過既有存取控制的路徑。

## 3) 密鑰與個資
已看,無 finding。新增程式碼沒有讀寫任何憑證、token 或個資欄位;`corpus()` 讀進來的內容只拿去做名稱字串比對(`.search`),比對結果只回 True/False/None,不會把檔案內容印進發現訊息或治理帳(`why` 欄位只組裝固定文案與筆記自身文字,例如「這次推送讓條件成立了」)。

## 4) 加密與傳輸
已看,無 finding。此 diff 不涉及網路傳輸或加解密邏輯。

## 5) 執行邊界(推送前掛鉤、CI、`exam --repo` 指向陌生 repo)
已看,無 finding(含一項已於筆記記載、非本次新增的既有限制)。

- `lumos drift exam --repo <repo> --probes <改寫檔>` 對 `--repo` 只做唯讀 git 操作(`git rev-parse`/`ls-tree`/`diff`/`cat-file`),沒有對該 repo 執行其內容、沒有 checkout 或跑其掛鉤腳本,跟既有 exam 機制(`invalidating_commits`)同一信任等級,乙沒有擴大這個邊界。
- `_drift_check_core` 新增呼叫 `_drift_probe_check` 後,乙的評估邏輯現在無條件掛在每次 `drift check`(推送閘)裡跑,但 `override`/`override_base` 兩個參數只在 `_drift_exam_probe`(exam 專用路徑)手動傳入,`cmd_drift_check` 呼叫鏈沒有接這兩個參數,CLI 也沒有對應旗標,乙沒有幫「推送時偽造條件式判定結果」開一條路:
  file: `scripts/lumos:1067`~附近(`main()`:`cmd_drift_check(repo=args.dr_repo, diff_range=args.dr_diff)`,未傳 override)
- diff 裡新增一則 WHY 筆記記載既有的 `.lumos/config.json` gate 自我繞過限制(推的人可在同一提交把 `drift_check.gate` 改成 `off`),但這是文件補記既有已知限制、附了 `retire:` 條件,且明寫是「代碼審 r1 資安席」上一輪已經抓到並裁定為「只防疏忽、不防存心繞過」的設計取捨,不是本次「乙」新增的程式碼路徑,乙的 diff hunk(`scripts/lumos`)裡也沒有改動讀 `.lumos/config.json` 的邏輯,故不在本輪重報:
  引句:「推的人可以在同一個提交把 drift_check.gate 改成 off 放過自己(代碼審 r1 資安席)」

## 6) 行動端
不適用,已看,無 finding。此 diff 純屬工具鏈 CLI(Python)與圖譜筆記,不涉及行動端程式碼。

## 新依賴
已看,無。新增函式全部使用 Python 標準庫(`re`、`datetime`、`json`、`time`、`pathlib`),沒有引入新的第三方套件。

## 總結
最高等級 clean,blocking 0 條。
