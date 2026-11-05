severity: minor

我讀了 r2-snapshot.patch 裡 `.github/workflows/ci.yml`、`.lumos/config.json`、`configs/ast-grep/kotlin-android/check.py` 全文,以及 `scripts/lumos`、`scripts/test_lumos.py` 的 diff。規則 YAML、Kotlin 樣本、型錄和筆記只用檔名清單加 grep 掃過(網址、密鑰樣式、信箱)。我沒有實際執行任何東西。

**逐類結果**

- ① 提示注入:已看,無。
  - `_LINT_MSG_SHOW` 從 70 字放寬到 120 字,印進給 AI 的擋下訊息。內容來自 repo 內自寫的規則 YAML `message:`。
  - `check.py` 的 `message_problems` 還強制 message 不含 `$`、不超過 120 字,並要以型錄編號開頭。
  - 型錄裡抄自網頁的網址只出現在來源欄,沒有進派工詞或 hook 附加段。
- ② 讀寫與執行越界:已看,只有兩條 minor,見下。
  - `check.py` 的 `subprocess.run` 全是 list 參數,沒有 `shell=True`。
  - r1 的 `shutil.which("sg")` 退路已移除,現在只認 `ast-grep`(`sg = sg or shutil.which("ast-grep")   # 不退去找 sg:Linux 上 sg 是切換群組的系統工具`)。
  - `_ktpack(copy=True)` 只寫 `tempfile.mkdtemp` 做的複本。
  - CI 只新增 `pip install ast-grep-cli==0.51.1`,版號已釘,沒有插值。
  - 新增的程式、範本、公開文件裡沒有密鑰或信箱。我 grep 了 AKIA、sk-、ghp_、`@gmail.com`、PRIVATE KEY,命中全在審查卷證。
- ③ 一步繞過:已看。r1 的 `_RULEPACK_SAMPLE_RE` 過寬已修,現在只認 `.kt`、`.kts`。還有一條殘留,見下。
  - `include_test_paths` 預設空集合,等於照舊排除測試路徑。設定值經過型別檢查,壞值只告警並當沒設。
  - `review-fp-` 檔名豁免只在 `check.py` 自檢裡生效,而且要規則本身在 `rules-review` 才算。它不進推送閘,所以不會讓產品碼的告警被略過。

**發現**

severity: minor
blocking: 否
1. 這條屬推論,因為我沒實測。r1 的樣本排除修在 `scripts/lumos`,但 `.lumos/config.json` 的 `node_home.ignore` 仍是不分副檔名的萬用字元。
   - 誰:照常操作的使用者或 AI。
   - 從哪:在 `configs/ast-grep/<任何包>/samples/` 底下放或改非樣本檔,例如 `.py` 或 `.sh`。
   - 送什麼:符合 `configs/ast-grep/*/samples/*` 的任何檔。
   - 拿到什麼:該檔不受「每支檔有家」那一道檢查約束。這只是漏掉一道檢查,不是漏掉安全閘,因為風險分級那邊已經收窄到 `.kt`、`.kts`。
   - 縮小點:改成 `configs/ast-grep/*/samples/**/*.kt` 之類,並順便加 `*.kts`。
   引句:「"configs/ast-grep/*/samples/*"」
   file: `.lumos/config.json` 的 `node_home.ignore`。

severity: minor
blocking: 否
2. 測試輔助把 `sg` 路徑直接接進 shell 腳本和 shell 命令字串,沒有加引號。
   - 誰:使用者在路徑含空白或 shell 特殊字元的位置安裝 ast-grep。
   - 從哪:`LUMOS_AST_GREP` 環境變數,或 PATH 上找到的 `ast-grep`。
   - 送什麼:含 `;`、`$(…)` 或空白的路徑。
   - 拿到什麼:`#!/bin/sh` 包裝腳本的 `exec <sg> "$@"` 和新增告警閘的命令字串 `<sg> scan --config … > …` 會被拆開,或執行路徑裡夾帶的指令。
   - 縮小點:這個值要由使用者自己設或自己安裝,屬於刻意設環境變數,所以只算縱深防禦;一般情況最多是路徑含空白時測試失敗。可改用 `shlex.quote(sg)` 包起來。
   引句:「wrap.write_text("#!/bin/sh\ncase \"$*\" in *ancestor-named-test*) exit 2;; esac\nexec " + sg + " \"$@\"\n", encoding="utf-8")」
   file: `scripts/test_lumos.py` 的 `t_kotlin_rulepack_samples`。
   另一處同樣的插值:「cmd = f"{sg} scan --config {pack} --format sarif {{LINT_FILES}} > {{LINT_SARIF_OUT}}"」,在 `t_lint_new_astgrep_kotlin_two_files`。`pack` 是 repo 路徑,也沒引號,所以 repo 路徑含空白時整條命令會斷。

**總結**:沒有可直接利用的洞。r1 的兩條都已處理(`sg` 退路移除、樣本排除收窄到 Kotlin 檔),只剩設定檔排除範圍過寬和測試輔助 shell 插值兩條縱深防禦的 minor,都不擋。
