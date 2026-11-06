severity: minor

審查範圍:r5-snapshot.patch 全文與 r5-repair.patch,也對照了 repo 內 `_repo_path_unsafe` 的所有呼叫端。除一條縱深防禦的 minor 外,三類都已看,沒有可直接利用的洞。

**驗證 `_path_resolves_in_root` 真的擋住**

引句:「return Path(p).resolve().is_relative_to(Path(root).resolve())」

- **資料夾連結(上輪的洞)**:`resolve()` 會跟完路徑上每一層連結,包含資料夾那層。`.github/workflows` 若是指到 repo 外的連結,底下的檔解析後就落在 root 外,會被略過。這個洞已補上。
- **`..` 與連結鏈**:`resolve()` 先正規化 `..` 並跟完整條連結鏈,再比較,繞不過。
- **`/private` 前綴(macOS 的 /tmp、/var)**:root 與 p 兩邊都 `resolve()`,前綴一致,不會誤擋也不會誤放。
- **大小寫不敏感檔系統**:p 是由 root 拼出來的,前綴字串相同,大小寫差異無法讓外部路徑通過前綴比對。
- **解析失敗**:`except (OSError, RuntimeError)` 回傳 False,連結迴圈或不可讀都當成不在 repo 內,方向是封閉的。
- **`_android_build_texts` 的檢查與讀取**:檢查用的是 `os.path.join(dirpath, fn)`,讀取用 `root / rp`,兩者是同一個檔,沒有檢查一個、讀另一個的錯位。`os.walk` 設 `followlinks=False`,連結資料夾不會被走進去。

**抽出共用後,原守衛有沒有變鬆**

引句:「if not _path_resolves_in_root(rootp, fp):」

- 判定式本身與抽出前的 `fp.resolve().is_relative_to(rootp.resolve())` 逐字同義。
- 唯一差別是解析時遇到 OSError 或 RuntimeError,舊版會直接拋例外,新版回傳 `"outside"`。這只會更嚴。
- `_repo_path_unsafe` 的 symlink、notdir 兩個逐層檢查沒動。
- 我查了 `scripts/lumos` 的所有呼叫端:7148、11905、11926、14854、22686、43243、43608、52567、54053、57486、69557、69633。它們都只看回傳值真假或 kind,沒有任何一處依賴「拋例外」,所以沒有變鬆的地方。

**提示注入**

引句:「"A1": "專案是 Android,但 CI 設定檔(.github/workflows/、.gitlab-ci.yml 等)裡都找不到 Android Lint 的跡象"」

- A1、A2、A3 的提醒文字都是固定字串。
- 被掃的 CI 檔內容只被用來判斷有沒有 lint 跡象(布林值)。檔名與檔案內容沒有進入給 AI 的輸出。
- 新增的程式碼沒有 subprocess、shell 插值、eval 或下載行為,只是讀檔與印固定字串。

**F1 解析與開檔之間有時間差(TOCTOU)**

severity: minor
blocking: 否
引句:「if (fn in _ANDROID_SCAN_NAMES or rp == "gradle/libs.versions.toml") and _os.path.isfile(fp) \」
審材外佐證 file: `scripts/lumos:52515`

- **誰**:使用者本人或照常操作的 AI,在同一台電腦上掃一個陌生專案。
- **從哪**:`lumos lint-check` 掃描期間。
- **送什麼**:在 `_path_resolves_in_root` 通過之後、`open` 之前,把 repo 內的建置檔換成指向 repo 外的連結。
- **拿到什麼**:讀取只被用來判斷有沒有 compose、lint 之類的字面跡象,內容不會回顯,所以不會外洩。這條是推論,而且需要刻意搶時序,屬於範圍外的系統天花板。

總結:最嚴重是一條 minor 的檢查與開檔時間差(推論,不外洩內容),會擋 0 條。
