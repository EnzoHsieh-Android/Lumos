severity: minor

我看了 diff 全部 812 行,其中 `scripts/lumos` 的改動逐段對過。呼叫端追蹤的結果:

- `_repo_path_unsafe` 抽出 `_path_resolves_in_root` 後,正常路徑的判定不變。只有一點差別:原本 `resolve()` 丟 OSError 或 RuntimeError 會直接往上拋,現在改回傳 "outside"。這是改善,不算退步。
- `_detekt_segment_codes`、`_detekt_cli_args`、`_detekt_walk_segments` 改呼叫 `_cmd_basename` 後,語意只多認反斜線。在 posix 路徑上沒有差別。
- `_ci_workflow_texts` 的其他呼叫者(行 48684、59820、59927、60354、60417)餵的都是 `.github/workflows` 的 yml,檔名不會是 Jenkinsfile。所以 Jenkinsfile 搬家對它們沒影響。
- `_strip_c_comments(..., keep_newlines=True)` 這個參數存在,簽名對得上。

F1(Jenkinsfile 改走新分支後少了 `#` 註解剝除)
severity: minor
blocking: 否
引句:「檔名是 Jenkinsfile 的照 Groovy 剝 `/* */` 與 `//`(沿用 `_strip_c_comments`,字串裡的 `//` 不算;換行照留,行數不變),不套 `#` 規則。」
- 搬家前,Jenkinsfile 先經過 `_ci_workflow_texts` 剝 `#` 整行註解,再由 A1 剝 Groovy 註解。搬家後 Jenkinsfile 直接 `continue` 跳過 `#` 剝除。
- 場景:Jenkinsfile 裡 `sh '''` 區塊含 shell 註解 `# ./gradlew lint (TODO later)`,實際只跑 `assembleDebug`。
- 重現:我在臨時目錄寫了這份 Jenkinsfile,執行 `_android_ci_lint_evidence(_ci_workflow_texts(_ci_config_paths(d)))`,得到 True。搬家前這行會被剝掉,應該回 False 並印 A1。
- 影響:只造成 A1 少印,不會誤報。文件的天花板節沒提這個新增的少印來源,語料和測試也沒有涵蓋。
- 因為重現得出,所以列入。已刪除臨時目錄。

F2(四個欄位名過寬,`command:` 影響最大)
severity: minor
blocking: 否
引句:「_CI_GRADLE_TASK_FIELD = re.compile(r"^([ \t]*(?:-[ \t]+)?)(?:tasks|arguments|command|gradle_task)[ \t]*:」
- 這個正規式不分 CI 種類,也不要求上下文有 gradle 或 orb。
- 場景:GitHub 或 GitLab 設定檔裡出現 `command: npm run build`,或 docker compose 風格的 `command: build`。這時 `build` 會被當成 gradle 任務列的證據,A1 因此被靜默。
- 文件天花板節只舉了 CircleCI 的 `command: make build`,沒說 `tasks:`、`arguments:` 在其他 CI 也會中。這是少印,不是誤報。
- 同樣的偏差也進了 `_ANDROID_CI_CORPUS`,語料只有 Azure 一例,沒有 `command: npm run build` 這種反例。
- 我沒有實跑,是從正規式推的。

F3(語料測試不清臨時目錄)
severity: minor
blocking: 否
引句:「root = Path(tempfile.mkdtemp(prefix="gctl-andcorp-"))」
- `t_lint_android_ci_corpus` 每次建立 23 個臨時目錄,都沒有刪。
- 同一批 diff 裡的 `outside = Path(tempfile.mkdtemp(prefix="gctl-andci-out-"))` 和 `odir = Path(tempfile.mkdtemp(prefix="gctl-andci-odir-"))` 也是同樣情況。
- 違反的規則是 `/Users/enzo/.claude/CLAUDE.md` 的「自己跑的測試或實驗:跑完…刪掉它留下的暫存」。不過測試執行器是否會隔離 TMPDIR 我沒有確認,所以只列 minor。

沒有找到會弄壞呼叫端或拿掉守衛的問題。

總結:最嚴重是 minor(F1 Jenkinsfile 少剝 `#` 註解,已重現),會擋 0 條
