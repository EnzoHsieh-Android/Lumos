severity: minor

F1 A3 對陌生 repo 的 `--plugins` 值做環境變數展開,只會多一次檔案存在檢查
- 誰:陌生 repo 的作者,`.lumos/lint.json` 由他控制。
- 從哪裡:使用者在該 repo 跑 `lumos lint-check` 或 `lumos doctor`。
- 送什麼:`--plugins $SOME_SECRET/x.jar` 或 `~/...` 這種展開後會指到使用者環境或家目錄的值。
- 拿到什麼:程式只對展開後的路徑做 `is_file()`,輸出裡只有「第 N 條 A3」這句固定文字,不印路徑也不印展開值。攻擊者看不到輸出,秘密值不會離開本機,所以沒有可用的外洩路徑。AI 讀到「有 A3」只拿到一個存在與否的位元。沒設的變數展開後仍含 `$`,會被略過。這條寫不出完整攻擊路徑,屬推論,只算縱深防禦。
- 要不要改:可以不改。要收緊就只展開 `$HOME`、`~`、`$LUMOS_*`,或展開後不在 repo 與 `$HOME` 內就不判。
- 佐證:`_android_plugin_missing` 與 `_detekt_plugin_values` 都沒有把路徑或值放進回傳字串,A3 輸出只含 `idx`。
引句:「pth = _os.path.expanduser(_os.path.expandvars(raw))」
severity: minor
blocking: 否

F2 建置檔與 CI 設定檔掃描會跟著符號連結的檔案走,但內容只影響布林判斷
- 誰:陌生 repo 作者。
- 從哪裡:repo 裡放 `build.gradle -> ~/.ssh/xxx` 或 `.github/workflows/a.yml -> /etc/...` 這類符號連結。
- 送什麼:指向 repo 外檔案的符號連結。
- 拿到什麼:`os.walk(followlinks=False)` 擋住了資料夾的連結。檔案連結則因 `os.path.isfile` 和 `open` 都會跟過去,所以會讀到 repo 外的檔。不過內容只拿去比對 `compose=true`、`lint` 這類字,結果只影響要不要印 A1 或 A2 的固定提醒。不回顯內容,也不執行。這條也寫不出完整攻擊路徑,屬推論,只算縱深防禦。
- 要不要改:可以不改。要收緊就在 `isfile` 之外加 `not os.path.islink`,或把真實路徑限制在 repo 內。
引句:「if (fn in _ANDROID_SCAN_NAMES or rp == "gradle/libs.versions.toml") and _os.path.isfile(_os.path.join(dirpath, fn)):」
severity: minor
blocking: 否

已看,無:
- ①提示注入:A1 和 A2 是固定常數字串。A3 只插入條號 `idx`,命令內容不回顯。型錄檢查的 `problems` 訊息只含規則編號和固定文字。對方可控文字沒有進到輸出或派工詞。
- ②CI 新步驟:下載、比對 sha256(`sha256sum -c`,失敗時 `set -eu` 中止)、寫入 `GITHUB_ENV`,順序正確。網址版本寫死在 `env`,沒有 `${{ }}` 展開外來輸入,jar 不會在比對前被載入。`$RUNNER_TEMP` 不是攻擊者可控的路徑。
- ②本機下載範本:先存成 `.part`,用 `shasum -a 256 -c` 比對,通過才 `mv`,失敗就 `rm -f`。範本的網址和雜湊都寫死,沒有環境變數可以覆蓋下載來源。`lumos` 本身不自動下載也不執行。
- ②`LUMOS_DETEKT_COMPOSE_JAR` 只在測試裡讀,用來找 jar,不會在 hook 或安裝流程中執行不可信位置的檔。這是使用者自己設的,屬系統天花板範圍。
- ②密鑰與信箱:新增內容裡沒有。
- ③非刻意繞過:這輪沒看到會讓守衛被一個指令或一次編輯意外走過的新路徑。A 系列只是提醒,不改退出碼,也不新增守衛。
- 子程序與 shell 插值:`_detekt_plugin_values` 只做字串解析,沒有 `shell=True` 或執行命令。

總結:最嚴重是 minor(F1、F2 兩條,都是推論的縱深防禦),會擋 0 條
