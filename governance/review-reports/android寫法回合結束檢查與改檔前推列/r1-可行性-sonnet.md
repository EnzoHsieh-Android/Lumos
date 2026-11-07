severity: major

我在臨時 git repo(git 2.39.2)重跑了 E4、E5、E6,並用 1 萬支 kt、500 支改動的 repo 量了 `git status` 耗時。兩條 major 都有實跑結果,其餘兩條 minor 的第二條未實跑。臨時目錄已刪。

**實跑結果,多數支持計劃**
- **E4 站得住。**
  - 檔案只 touch 過時,`git --no-optional-locks status --porcelain=v1 -z --untracked-files=all` 不改寫 `.git/index`。
  - 帶 `--ignored=matching -- <檔>` 的 `status` 同樣不改寫索引。
  - `git --no-optional-locks diff-index --quiet HEAD` 不改寫索引,但會誤回 1。
  - `git --no-optional-locks diff --quiet HEAD` 和一般 `git status --porcelain` 都會改寫索引。
- **E5 站得住。** 宣告檔乾淨時 `status ... -- .lumos/lint.json .lumos/config.json` 無輸出,touch 過不誤報。
- **子模組。** 髒子模組在 v1 輸出是 ` M sub/sm`,路徑是目錄,依副檔名過濾即可排除。
- **時間預算站得住。**
  - 1 萬支檔、500 支改動時,`status` 約 0.2 秒;全部 touch 過後約 0.37 秒。
  - 500 支超過上限 50,會直接 rc3。
  - `scripts/lumos --help` 啟動約 0.77 秒。
  - 算式 30×0.7=21,`--budget` 給 19,最壞約 22 秒加啟動,與計劃一致。
- **鉤子文件。** 官方 `prompt_id` 欄位存在、鉤子並行、`timeout` 單位為秒,與計劃一致;`UserPromptSubmit` 預設逾時 30 秒。`stop_hook_active`、SIGTERM 寬限、連續八次續做上限這三項我沒讀到(頁面截斷),未驗證。

F1
引句:「`R`/`C` 用舊路徑;`??` 與 `A`(HEAD 沒有這支)基準為空」
severity: major
blocking: 是
先 `git mv` 再 `mv`、再 `git add -N` 的改名,輸出是兩筆串在一起:`R  b/Foo.kt|a/Foo.kt|` 和 ` R b/Foo2.kt|b/Foo.kt|`。第二筆的「舊路徑」`b/Foo.kt` 是索引裡的中間路徑,HEAD 沒有這支檔。
- 照字面用舊路徑去讀基準會讀不到,基準變空。`b/Foo2.kt` 裡原有的告警全被算成新增,會誤擋。
- 第一筆 `R b/Foo.kt` 在工作樹已不存在,直接讀檔會出錯或被誤判。
- 計劃只處理了「單步改名」。S1 寫的「`git add -N` 之後狀態碼 R 在第二格」測的就是單步,沒涵蓋這種鏈。
- 修法:解析時沿著舊路徑追回 HEAD 有的那一端;追不到才算基準為空,且要列出來。

F2
引句:「呼叫既有 `_kill_proc_group`——它**直接送 SIGKILL、沒有寬限**」
severity: major
blocking: 是
照字面做,SIGTERM 加 SIGKILL 的組合會留孤兒。
- `_lint_spawn` 用 `start_new_session=True`,檢查工具在自己的 session。鉤子「對它的程序群組」送的 SIGKILL 只打到 lint-new 的群組,碰不到工具。
- lint-new 的處理器只收「清單裡」的程序。`Popen` 回傳到放進清單之間,以及處理器還沒裝上之前,收到 SIGTERM 就漏掉。
- 鉤子 1 秒寬限一到就 SIGKILL lint-new,處理器沒跑完的話,工具和 `.lumos/lintbase-*` 快照都會殘留。
- 鉤子自己被 Claude Code SIGTERM 時只轉發、不再升級成 SIGKILL,處理器沒裝上時一樣漏掉。
- 修法:先登記程序再開跑(或先擋住訊號再 Popen),寬限期內由 lint-new 自己收尾,鉤子的 SIGKILL 前要確認工具群組已死。

F3
引句:「用 `commonpath` 比,實驗 E7:字串前綴擋不住 `..` 與符號連結,真實路徑擋得住」
severity: minor
blocking: 否
macOS 預設檔系統不分大小寫,`os.path.realpath` 不會校正大小寫,`commonpath` 是分大小寫比字串。使用者的目錄實際是 `~/Harness`、而宣告寫 `$HOME/harness/...` 時,合法命令會被擋,工作樹模式永遠 rc3。
- 這個方向是安全地失敗,不是被繞過。
- 但原因只有一句「工作樹模式不跑」,使用者看不出是大小寫造成的。
- 這條是照程式行為推出來的,未實跑。
- 建議:這種情況另外印一句原因。

F4
引句:「`{LINT_FILES}`、`{LINT_FILES_CSV}`、`--format`/`--json`(含 `=值`)及其值」
severity: minor
blocking: 否
白名單只驗命令模板,不驗換進 `{LINT_FILES}` 的檔名。
- 這個換入由既有程式碼 `scripts/lumos:39884` 做,只過 `shlex.quote`,擋不住開頭是 `-` 的檔名。
- 專案裡若有目錄叫 `--config=x`,工作樹模式又傳相對路徑,ast-grep 可能把它當選項。
- 本機沒有 ast-grep,未實跑,也不確定它的實際解析。
- 建議:換入前給相對路徑加 `./` 前綴,或在檔案清單前加 `--`。

總結:最嚴重是 major(改名鏈基準讀不到會誤擋、SIGKILL 只打 lint-new 群組會留工具孤兒與快照),會擋 2 條。
