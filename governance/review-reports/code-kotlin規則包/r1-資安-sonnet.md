severity: minor

我讀了 `.github/workflows/ci.yml`、`.lumos/config.json`、`scripts/lumos`、`scripts/test_lumos.py` 的 diff 和 `configs/ast-grep/kotlin-android/check.py` 全文。其餘檔案(YAML 規則、Kotlin 樣本、型錄 markdown、卷證)我用檔名清單和 grep 掃過。

**逐類結果**

- ①提示注入:已看,無。`_cl_say_lint_block` 印給 AI 的告警訊息來自 repo 內作者自寫的規則 YAML,不是外來文字。我也沒找到網頁抄來的內容或網址被組進派工詞或 hook 附加段。
- ②讀寫與執行越界:
  - CI 新增 `pip install ast-grep-cli==0.51.1`,版號已釘,沒有 shell 插值。它沒鎖雜湊,但依賴與供應鏈依家規不另審。
  - `check.py` 的 `subprocess.run` 全是 list 參數,沒有 `shell=True`,執行檔來源是 `--sg`、PATH 或 `LUMOS_AST_GREP`。
  - `_ktpack(copy=True)` 用 `tempfile.mkdtemp` 做複本,只寫暫存區。測試寫入的是複本,不碰真檔。
  - 新程式、範本、公開文件裡我沒找到密鑰或信箱,grep 的命中只在審查卷證裡。
  - 未見 hook 或安裝腳本去執行不可信位置的檔。
- ③非刻意的守衛繞過:有兩條 minor,見下。

**發現**

severity: minor
blocking: 否
1. 樣本目錄排除正規式吃掉 `configs/ast-grep/<任何名>/samples/` 下的所有檔案,不分副檔名。
   - 誰:照常操作的使用者或 AI。
   - 從哪:在該目錄放入或修改非樣本的程式檔,例如 `.py` 或 `.sh`。
   - 送什麼:路徑符合 `configs/ast-grep/*/samples/*` 的任何檔。
   - 拿到什麼:`_stack_changed_ok` 回 False,那支檔不進風險分級、棧別題、新增告警閘的掃描,守衛被一次編輯意外走過。
   - 縮小點:排除可以限定在 `.kt` 與 `.kts` 副檔名,或用 `scripts/lumos` 現有的路徑白名單。這個風險不大,因為這類路徑正常只放壞例樣本。
   引句:「_RULEPACK_SAMPLE_RE = re.compile(r"configs/ast-grep/[^/]+/samples/")」
   file: `scripts/lumos` 的 `_stack_changed_ok`。
   補充:`.lumos/config.json` 的 `node_home.ignore` 加了 `"configs/ast-grep/*/samples/*"`,同樣不分副檔名。

severity: minor
blocking: 否
2. 這條屬推論,因為我沒實測。`check.py` 的 `main` 找不到 `ast-grep` 時退回 `shutil.which("sg")`。
   - 誰:沒裝 ast-grep 的使用者或 CI 環境。
   - 從哪:直接跑 `python3 check.py`。
   - 送什麼:PATH 上的 `sg`,在 Linux 與部分 macOS 上是 shadow-utils 的 `sg`(切換群組的 setgid 工具),不是 ast-grep。
   - 拿到什麼:會以 `sg scan ...` 之名執行這支無關的系統工具,可能卡在群組密碼提示。
   - 縮小點:本機沒裝時只認 `ast-grep`。CI 已釘裝 `ast-grep-cli`,它兩個名字都有裝,所以 CI 不受影響。
   引句:「sg = sg or shutil.which("ast-grep") or shutil.which("sg")」
   file: `configs/ast-grep/kotlin-android/check.py`(`main`)。

**順手提一句**

測試用的 `LUMOS_AST_GREP` 環境變數可以讓測試去執行任意執行檔。這屬於刻意設定環境變數的範圍外情況,標 minor、blocking: 否。

**總結**:沒有可直接利用的洞,只有兩條縱深防禦類的 minor,都不擋。
