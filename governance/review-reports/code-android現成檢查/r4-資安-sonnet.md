severity: minor

已看三類(提示注入、讀寫與執行越界、非刻意繞過守衛),只有 F1、F2 兩條 minor。

**F1 資料夾是符號連結時,CI 設定檔仍會跟到 repo 外去讀**
severity: minor
blocking: 否
引句:「檔案本身是符號連結的略過(不跟著讀到 repo 外,代碼審 r3 資安席)」
`scripts/lumos` 的 `_ci_config_paths` 只擋「檔案本身」是連結(`p.is_symlink()`),`wf.is_dir()` 與 `wf.iterdir()` 照樣跟過資料夾連結。`.circleci/config.yml` 的路徑檢查也只看最後一段。
- 攻擊路徑:
  - 誰:使用者本人或照常操作的 AI,對一個別人給的 repo 跑 `lumos lint-check` 或 `lumos doctor`。
  - 從哪:該 repo 帶 `.github/workflows` 或 `.circleci` 資料夾連結,指到 repo 外的目錄。
  - 送什麼:連結目標目錄裡的 `ci.yml` 或 `config.yml`。
  - 拿到什麼:實測 `_ci_config_paths` 回傳了連結目標裡的檔案,所以 repo 外的檔案被讀進來。但讀到的內容只決定 A1 與 T4 的真假,不回顯、不執行,所以沒有資料外洩。
- 我只看得出兩個影響:
  - 外部檔案裡寫了 `detektDebug` 或 `lintDebug`,A1 與 T4 的提醒就被壓掉。
  - 本輪宣稱的「不跟連結讀到 repo 外」只對檔案連結成立,對資料夾連結不成立。
- 建議:判斷路徑要不要略過時,往上檢查每一層父資料夾是否為連結。`_android_build_texts` 用 `os.walk(followlinks=False)` 並對檔案做 `islink` 檢查,這個我已看過,是乾淨的。
- 連結指向連結:檔案層會被 `is_symlink` 擋掉。資料夾層同上,不擋。
- file: `scripts/lumos:60295`

**F2 A3 用 `os.path.expandvars` 展開環境變數後去判斷檔案存不存在,可當成存在與否的探測**
severity: minor
blocking: 否
引句:「照 shell 的規則展開環境變數與 `~`(`os.path.expandvars`、`expanduser`)」
- 攻擊路徑:推論。
  - 誰:使用者本人或照常操作的 AI。
  - 從哪:對一個 `.lumos/lint.json` 由別人寫的 repo 跑 `lumos doctor`。
  - 送什麼:`--plugins $SOME_SECRET/x.jar` 這類字串。
  - 拿到什麼:只多一個「路徑存不存在」的布林提醒。
- A3 的提醒文字是固定字串,不回顯命令或展開後的值,環境秘密也不會被寫進輸出或帳本,所以不構成秘密外露。展開後含 `$`、`{`、`}` 就不判,這道檢查我也確認有擋住,沒有找到會展開到環境秘密並外流的路徑。

**逐類結論**
- 提示注入:已看,無。A1 到 A3 的提醒都是固定文字,不帶命令、檔名或 CI 內容。
- `_is_gradle_head` 換進 detekt 判定:已看,無。
  - `_detekt_walk_segments` 與舊邏輯等價。
  - 新增 `.\gradlew` 與 `tools\gradle` 會被認成 gradle,只會多報,不會讓原本會擋的命令被一步走過。
  - 一個含反斜線的 detekt CLI 路徑被誤認成 gradle 是不實際的構造,頂多算刻意多步。
- 密鑰與信箱:已看,無。CI 範本新增的 sha256 是公開檔案的雜湊。
- 下載來源:已看,無。URL 由版本變數組出,在 `env` 裡寫死,不接受外部覆蓋,下載後有比對 sha256。

總結:最嚴重是 minor(資料夾符號連結仍會被跟到 repo 外讀取,但內容不外流),會擋 0 條。
