severity: minor

審查範圍:`r3-snapshot.patch` 的程式部分(`ci.yml`、`scripts/lumos` 的 A1 到 A3、`check.py`、測試)和 `r3-repair.patch`。我只讀碼,沒有實跑。

**F1 建置檔與 CI 設定檔掃描會跟著符號連結的「檔案」讀到 repo 外(縱深防禦,攻擊路徑為推論)**
severity: minor
blocking: 否
引句:「_os.path.isfile(_os.path.join(dirpath, fn))」
- 位置:`_android_build_texts` 在進資料夾時不跟符號連結(`followlinks=False`),但檔案層只用 `isfile` 判斷。`isfile` 會跟連結,所以名為 `build.gradle` 的連結可指向 repo 外的檔案。`_ci_config_paths` 的 `p.is_file()` 同理。
- 誰:使用者本人或照常操作的 AI,對一個陌生 repo 跑 `lumos doctor` 或 `lumos lint-check`。
- 從哪:該 repo 裡名為 `build.gradle` 或 `.github/workflows/x.yml` 的符號連結。
- 送什麼:連結指向 `~/.ssh/config` 之類的檔案。
- 拿到什麼:該檔最多前 1MB 被讀進記憶體,但只用來判 A1、A2 的是與否。輸出是固定文字,不帶檔案內容。對方看不到使用者本機的輸出,所以沒有洩漏通道。
- 建議:要補的話,對這兩處的檔案加 `not os.path.islink`。

**其餘各類已逐一檢視:**
- 提示注入:已看,無。A1 到 A3 的提醒文字全是固定字串,只帶條數索引 `[kt 第 N 條]`,不回顯命令、路徑或建置檔內容。對方可控的文字沒有進到給 AI 的輸出。
- A3 對 `--plugins` 值做 `expandvars` 與 `expanduser`:已看,無可利用的洞。
  - 展開結果只用在 `is_file()`,輸出只有「有或沒有 A3」。環境秘密的值不會被印出,也不會被寫進任何地方。
  - 對方想靠「在不在」洩漏資訊,得看到使用者本機的輸出,沒有回傳通道。
  - 路徑跑到 repo 外只做存在檢查,不讀內容。
  - 反引號和萬用字元已排除。展開後仍含 `$` 的也排除。
  - 含 NUL 的路徑不會讓 `is_file` 丟例外。
  - 這個 `lint.json` 的命令本來就會被新增告警閘用 shell 執行,A3 沒有增加執行面。
- CI 下載 compose-rules jar:已看,無繞過點。
  - 步驟開頭有 `set -eu`,下載後立刻用寫死的 sha256 比對。`sha256sum -c` 失敗時整步失敗,不會走到寫 `GITHUB_ENV` 那行。
  - 檔案在 `$RUNNER_TEMP/detekt/` 下,路徑只來自 runner 變數與固定版本號。
  - 版本號放在步驟的 `env`,不是 `${{ }}` 插值,沒有注入點。
  - `curl -L` 沒加 `--proto =https`,但起點是 https,雜湊會兜底。這點與上一步 detekt 的既有做法一致,不報。
  - 測試端只在 `LUMOS_DETEKT_COMPOSE_JAR` 或本機固定目錄存在時才用,`CI` 為真且找不到時判紅,不會安靜略過。
- 讀寫與執行越界:已看,無。新程式只讀檔,不寫檔、不執行外來檔。測試裡的 `subprocess` 參數都是 `shlex.quote` 過的自造路徑。新寫的內容沒有密鑰或信箱。
- 非刻意一步繞過守衛:已看,無。A1 到 A3 只是提醒,不改退出碼,不是守衛。`_detekt_walk_segments` 把 detekt 判定和外掛路徑提醒共用同一套切段,沒有出現兩邊看法不一致、可被一個指令走過去的缺口。

總結:最嚴重是 minor(符號連結檔案只做布林判斷、無洩漏通道),會擋 0 條
