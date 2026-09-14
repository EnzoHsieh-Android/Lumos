severity: minor

## F1 冒煙檔案來源擴大到未追蹤檔,降低了攻擊者取得「檔名被拼進 shell 指令」的門檻(推論)

severity: minor
blocking: 否
引句:「r = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", "*." + str(stack)],」
file: `scripts/lumos:17175`

- **誰**:能把一支檔案放進開發者本機工作目錄、但不需要(也還沒)`git add`/送 PR 的人或流程——例如惡意的範例壓縮包、`pub`/`npm` 之類套件安裝後留下的雜項檔、下載下來還沒檢視的程式碼片段。門檻比 r2 審過的「能提交檔案進這個 repo 的人(含惡意 fork/PR)」更低:r2 的模型至少要走到「檔案進了 git 索引或 PR diff 裡、有機會被看到」,r3 這個改動下,檔案只要躺在工作目錄裡沒被 `.gitignore` 擋掉就算數,連 `git status` 都不用特地去看就可能被納入。
- **從哪個入口**:`lumos lint-check --smoke`(手動指令,未接 pre-commit/pre-push/CI/daily-governance——已用 `grep` 核對 `governance/daily-governance.sh`、`.git/hooks/`、`.github/` 都沒有自動呼叫點,只有文件建議「接完宣告後手動跑一次」)。開發者在自己專案裡剛寫好 `.lumos/lint.json` 宣告、想確認冒煙時執行。
- **送什麼**:一支檔名以 `-` 開頭、副檔名對上某個已宣告棧(例如 `.dart`/`.py`/`.js`)的未追蹤檔,例如 `--rulesdir=evil.js` 這種「檔名本身長得像旗標」的名字。`shlex.quote()` 會把它安全包成單一 shell token(已核對,不構成命令注入),但**不保證下游被呼叫的分析器不會把這個 token 當成自己的命令列旗標解讀**(argument/flag injection)。
- **拿到什麼**:**推論,寫不出具體「送什麼旗標值→執行什麼」的完整鏈**——沒有在這批棧常見的分析器(dart analyze / ruff / eslint / sqlfluff / PMD / detekt / SwiftLint)裡找到「單一 `--flag=value` token 就足以觸發任意程式碼執行」且不需要額外佈局(例如另外還要一個惡意 plugin 目錄)的具體旗標;而且冒煙路徑本身不外流任何工具輸出(`cmd_lint_check` 用 `_claims, ok = _lint_run_and_parse(...)`,`_claims` 直接丟棄,失敗訊息只印被樣板化的 `cmd[:60]`,不印任何分析器的診斷內容),`_lint_run_and_parse` 也一律把子行程 stdout/stderr 導向 `DEVNULL`。所以就算真的觸發到某個危險旗標,現有程式碼路徑也沒有把結果回吐給攻擊者的通道。
- **重現(交代機制,非完整攻擊)**:在任一臨時 repo 建 `.lumos/lint.json` 宣告一個含 `{LINT_FILES}` 的 dart 棧,`touch './-Denable=x.dart'` 但不 `git add`,執行 `lumos lint-check --smoke`——比 r2(只掃 `git ls-files -z -- '*.<stack>'`,即只認已追蹤檔)多出這支「還沒被任何人看過、也還沒進 git 索引」的檔會被選進 `{LINT_FILES}`。

**判定與緩解**:跟 r2 已審過的「檔名 shlex.quote 後拼進 shell=True 指令」是同一套既有機制與既有信任邊界(r2 判 clean 時已把這條 argument-injection 疑慮列為「推論、非新增缺口」)。r3 唯一的行為差異只是把候選檔案集合從「已追蹤」擴大到「已追蹤 ∪ 未忽略的未追蹤」,沒有新增輸出通道、沒有改變执行方式、`--exclude-standard` 仍尊重 `.gitignore`。三個緩解因子同時成立時才不構成可直接利用的洞:①`--smoke` 純手動、無自動排程或 CI/hook 觸發;②沒有具體旗標可構成完整鏈;③冒煙路徑不回吐任何診斷內容。三者任一被打破(例如日後把 `--smoke` 接進自動排程,或冒煙失敗訊息開始印出更多診斷片段),這條就該重估為 major。標記為縱深防禦類的 minor,不擋這次推送。

## 逐類

1. **不可信輸入流到危險操作**:命令注入已排除——`stack` 進 `git ls-files` pathspec 是走 `subprocess.run([...])`(非 `shell=True`)的 argv 清單,且固定以 `"*."` 前綴接上,無法組出以 `:` 起首的 magic pathspec;真正進 `shell=True` 的是 `git ls-files` 選出的檔名,全部先過 `shlex.quote()` 才 `.replace()` 進宣告命令,不構成 shell 注入。剩下的 argument/flag injection 疑慮見上方 F1(推論、minor)。
2. **登入與權限**:已看,無——這批改動不涉及任何身分驗證或授權判斷。
3. **密鑰與個資**:已看,無新增揭露面。`--cached --others --exclude-standard` 的 `--exclude-standard` 會尊重 `.gitignore`,一般被忽略的 `.env`/憑證類檔名不會被撿進來;就算真有一支未被 `.gitignore` 蓋到、看起來像密鑰的檔被選中,冒煙路徑本身不印任何分析器輸出內容(見 F1 的「拿到什麼」),沒有把檔案內容回吐出去的通道,純本機、不落地到治理帳或任何會被推送的檔案。
4. **加密與傳輸**:已看,無——純本機檔案 I/O 與 subprocess,不涉及網路傳輸,沒有新增依賴。
5. **執行邊界**:已看,無新增風險——`git ls-files` 本身唯讀,不執行任何被列出的檔案;`shell=True` 插值全部先經 `shlex.quote()`;`cmd_dart_sarif` 的 `--out` 寫檔路徑沒有變(仍是 `_lint_run_and_parse` 用 `tempfile.mkstemp()` 現生的隨機路徑,攻擊者無法預先埋符號連結)。
6. **行動端**:已看,無,與行動端(iOS/Android)無關。

**新依賴**:已看,無——這次 delta 只用到既有已使用的標準庫(`shlex`/`subprocess`),沒有引入任何第三方套件,零依賴家規未被打破。
