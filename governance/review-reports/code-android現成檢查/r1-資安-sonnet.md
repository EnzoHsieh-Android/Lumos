severity: minor

**已看,無**
- 提示注入:這份 diff 沒有新增把筆記內容、檔名或席報告塞進派工詞的路徑。唯一的外來字串進輸出是 F1。
- 讀寫越界:新函式只讀不寫,沒有 `eval`、沒有 shell 插值。
  - `_android_plugin_paths` 用 `shlex.split` 切字串,只對 `Path(pth).is_file()` 做存在判斷,不會讀到檔案內容。
  - `_android_build_texts` 與 `_ci_config_texts` 讀到的文字只拿去跑 regex,不印出。
  - `os.walk` 設了 `followlinks=False`,不會跟著符號連結進資料夾。建置檔本身若是指向 repo 外的捷徑,會被讀進來比對,但內容不外流。
- CI 新步驟:
  - 下載網址是寫死的 `github.com/mrmans0n/compose-rules/releases/download/v${COMPOSE_RULES_VERSION}/…`,沒有可被環境變數覆蓋的位置。
  - `set -eu` 加上 `echo … | sha256sum -c -`,雜湊不符時步驟會失敗。
  - `LUMOS_DETEKT_COMPOSE_JAR` 在驗證通過之後才寫進 `GITHUB_ENV`。
  - `$j` 由 `RUNNER_TEMP` 組成,沒有外部輸入。
- 新增的密鑰與信箱:無。
- 測試檔:`_detekt_compose_jar` 讀環境變數 `LUMOS_DETEKT_COMPOSE_JAR`。這是測試自己的設定,屬刻意環境,不報。

**F1(A3 把對方 lint.json 的字串印進 AI 上下文)**
severity: minor
blocking: 否
- 攻擊路徑:
  - 誰:提供陌生 repo 的人。
  - 從哪:對方 repo 的 `.lumos/lint.json` 裡 `kt` 命令的 `--plugins <任意文字>`,再由使用者跑 `lumos lint-check` 或 `lumos doctor` 觸發。
  - 送什麼:一個不存在的路徑,最後一段檔名帶最多 80 字的指令式文字。
  - 拿到什麼:`_lint_android_ci_advisories` 把 `Path(pth).name[:80]` 原樣印在 `[CI] A3:` 那行,同樣的字串也進 `--json` 的 `advisories`。對方可控的文字因此進到 AI 的上下文。
- 限縮:這條只能多印 80 字。對方的 lint.json 本來就能放要被推送閘執行的命令,所以威脅沒有變大,屬縱深防禦。
引句:「out.append("[CI] A3:" + _ANDROID_ADVICE_TEXT["A3"].format(name=Path(pth).name[:80]))」

**F2(範本下載雜湊不符時,jar 留在固定目錄,之後每次推送都載入且不再驗)**
severity: minor
blocking: 否
- 攻擊路徑:
  - 誰:照 linter 目錄範本操作的使用者。
  - 從哪:範本那條 `gh release download … && echo "<sha>  …" | shasum -a 256 -c -`。
  - 送什麼:被換掉或下載到一半壞掉的 jar,雜湊不符。
  - 拿到什麼:`&&` 只擋住後面的指令,不符的 jar 仍留在 `$HOME/.local/share/lumos/detekt-plugins/`。
- 後續:
  - 推送前的 `--plugins $HOME/.local/share/lumos/detekt-plugins/detekt-compose-0.4.28-all.jar` 命令不會比對雜湊就直接載入,等於執行該 jar。
  - A3 只做 `Path(pth).is_file()`,所以這支不符的 jar 在健檢眼裡是正常的。
- 其他:
  - 範本裡「不符就不要用」只是散文,沒有機器擋。範本沒有在失敗時刪檔。
  - `gh release download` 遇到已存在的檔會拒絕覆蓋,所以壞檔也不會被下一次下載蓋掉。
- 限縮:需要上游 release 被竄改或下載損壞,而且使用者忽略失敗訊息,所以只列縱深防禦。
引句:「mkdir -p "$HOME/.local/share/lumos/detekt-plugins" && cd "$HOME/.local/share/lumos/detekt-plugins" && gh release download v0.4.28 -R mrmans0n/compose-rules」

**F3(提一句,不算守衛漏洞)**
severity: minor
blocking: 否
- 範圍外,屬刻意設定環境變數:shell 裡殘留的 `LUMOS_DETEKT_COMPOSE_JAR` 會讓測試改載入那個路徑的 jar。這是測試的行為,不是產品路徑,只是順手提一下。
引句:「p = _os.environ.get("LUMOS_DETEKT_COMPOSE_JAR") or str(」

總結:最高嚴重度 minor,共 3 條發現,blocking 為是的有 0 條。
