severity: major

## F1 小改動閘的簿記目錄過濾是內容無關的路徑前綴判斷——把程式檔改名進這三個目錄可讓四維度全部看不到
severity: major
blocking: yes

觀察:`_small_change_check` 在建 `files` 清單時,任何路徑只要落在 `_BOOKKEEPING_DIRS` 底下就直接 `continue` 跳過,完全不進入後面的擴散/相對量/歷史/目的四道檢查。而這批把 `_BOOKKEEPING_DIRS` 從單一個 `governance/code-loop/` 擴成三個目錄的 tuple,且同一組常數被 `_small_change_check`(新的推送閘)、pitfalls 掃描 `_stack_changed_ok`、`_codeloop_record_valid` 三處共用。

引句:「_BOOKKEEPING_DIRS = ("governance/code-loop/", "governance/review-reports/", "governance/replay/")   # 2026-09-17 小改動閘 r2:卷證目錄也是紀錄不是碼(三個消費者共用這一組)」

引句:「if path in _BOOKKEEPING_FILES or path.startswith(_BOOKKEEPING_DIRS) or (vrel and path.startswith(vrel + "/")):」
引句:「continue   # 帳本/卷證/筆記不算程式改動;其他副檔名一律算(JSON/HTML 在前端專案就是碼)」

重現:一份全靠人驗的雙向門計劃,推送前把落點內任一支程式檔用 `git mv` 搬進 `governance/review-reports/<隨便一個名字>` 或 `governance/replay/<隨便一個名字>`(不管內容有沒有改)。`_numstat_new_path` 解析出的新路徑會落在 `_BOOKKEEPING_DIRS` 前綴內 → 這支檔完全不會進 `files` 清單 → 不算進擴散的檔數/目錄數、不算進相對量、不查歷史裁判檔/風險標籤、也不影響目的判斷。若這是這次改動裡唯一被碰到的檔,`files` 會是空清單,函式在 `if not files: return []` 直接放行,四維度全過。

為什麼是 bug:這份 patch 自己在同一段落寫了「★不按副檔名排除★(r2 通才席 blocker:借 _PITFALL_DIFF_SKIP_EXT 會讓 .json/.html/.svg 整支量不到,前端專案的大改動 fail-open)」——也就是作者已經意識到「內容無關的路徑判斷會 fail-open」這個坑,並且針對副檔名修掉了。但同一支函式仍然保留另一個內容無關的判斷維度:路徑前綴。凡是路徑字串命中 `_BOOKKEEPING_DIRS` 三個目錄之一,不管檔案實際內容是不是程式碼、也不管它是不是剛被改名進來的真程式檔,一律視而不見。這是同一類漏洞(content-blind filter → fail-open)換了一個維度重新出現,而且這批把可豁免的目錄從 1 個擴成 3 個,攻擊面反而變大了。小改動閘存在的目的正是要在「全靠人驗、沒有任何自動化紅綠可判」的情況下擋住偷渡的大改動,這個缺口直接讓它可以被繞過。

## F2 改名+大量編輯時,相對量的「原本行數」查詢用新路徑去查改名前的舊樹,幾乎必定查不到、原本行數靜默算成 0
severity: minor
blocking: no

觀察:相對量檢查對每個非二進位檔案算 `churn = la + ld`,超過 300 行絕對值門檻時才會去查「原本行數」`lt`,查法是 `git show {base}:{path}`,其中 `path` 是**改名後**的新路徑,`base` 是改動前的舊提交。

引句:「lt = len(g.stdout.splitlines()) if g.returncode == 0 else 0」

重現:一支檔案在同一次改動裡「改名+大幅編輯」(新增/刪除總行數超過 300 行),舊提交樹裡只有舊路徑下的檔案,新路徑在舊提交裡不存在,`git show {base}:{新路徑}` 一定回非 0(找不到檔案),於是 `lt` 被設成 0,印出來的訊息會寫「原本 0 行」,而 `churn > lt * max_rel_churn` 恆真(0 * 0.2 = 0),不管實際改動量占原檔比例多少都會被判「相對量」擋下。

為什麼是 bug:這不是安全性漏洞(結果是保守地擋、不是放行),但「相對量」這個維度存在的意義是要跟真實原始檔案大小比,查詢卻系統性地查不到原始檔案(用錯了 commit 端的路徑),導致這條分支形同虛設、訊息還會誤導成「這個檔案原本是空的」。上一輪的測試 ⑦(複核)只驗了「改名+一行小編輯」,改動量遠低於 300 行絕對門檻,根本不會走進這段查 `lt` 的程式碼,所以這個邊界從沒被驗證過。

## 複核

① `--no-renames` 純改名算整支重寫:已修好。`_numstat_new_path` 用正則解析 `dir/{old => new}/f` 與 `old => new` 兩種格式,實際用 `git diff --numstat <commit>..<commit>` 這種提交對提交的範圍(而非未暫存 worktree diff)跑過,確認 git 對改名確實印出 `{old => new}` 括號格式,函式能正確還原成新路徑。純改名(無內容變動)時 la/ld 都是 0,不會被算進相對量。
引句:「r = subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "diff", "--numstat", git_range, "--"], capture_output=True, text=True, errors="replace")」

② 借副檔名排除讓 .json/.html 量不到:已修好。過濾只看 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS`/vault 相對路徑三個條件,完全不看副檔名,JSON/HTML 檔會正常被算進 `files` 清單(測試 ⑪ 也驗了 data.json 超過 300 行會被擋)。但如上面 F1 所述,目錄前綴本身仍是內容無關的判斷,問題換了個維度存在。

③ `_loop_ts_key` 回 None 直接跳過改成退回字串比對:已修好。`cutoff_str` 用 `.astimezone()` 產生一定帶時區,`_loop_ts_key(cutoff_str)` 恆不為 None;只有逃逸帳自己的 `ts` 解析不動(沒帶時區或格式錯)時才會退回字串比對,行為符合文件所寫。測試 ⑨ 驗了 UTC 寫入的時間戳換算後仍判「近期」,不會因為時區位移被字串比對誤判成不是。
引句:「if k is None or cutoff_key is None:   # 解析不動(沒帶時區)照 _loop_ts_key 文件退回字串比對(r2 複核②)」
