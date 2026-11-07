severity: minor

審查範圍是 r4-repair.patch 對照 `scripts/lumos`(已套上這輪修補的工作樹)。上一輪點的第一處(第二次走訪)和第二處(gradle 詞表兩份)確實處理了,我沒找到新的第二種做法,只有兩條小的不一致。第三處(CI 檔兩條讀法)這輪沒宣稱處理,現況仍在,下面一併交代。

**問一:分層與依賴方向**
- 第二次走訪已消失。`_android_lint_config_evidence` 整支刪掉,`_lint_android_ci_advisories` 只剩 `_android_build_texts(repo_root)` 這一次 `os.walk`(`scripts/lumos:39092`)。
- gradle 詞表已歸一。`_GRADLE_HEADS`(`scripts/lumos:39014`)由 `_is_gradle_head` 在三處共用:A1 的 check/build 判定(`scripts/lumos:39042`)、`_detekt_plugin_values`(`scripts/lumos:39055`)、`_detekt_segment_codes`(`scripts/lumos:39145`)。
- 方向有點雙向,見 F1。
  - detekt 區的判定函式現在依賴放在 Android 區塊裡的 helper。
  - Android 區塊本來就依賴 detekt 區的 `_detekt_walk_segments`、`_detekt_cli_args`。

F1
severity: minor
blocking: 否
引句:「if _is_gradle_head(seg[0]):」
- 同一個函式 `_detekt_segment_codes` 裡,`head = _pp.basename(seg[0])` 沒動(`scripts/lumos:39143` 附近),旁邊又多一種用 `re.split(r"[/\\]")` 的判法。
- `_detekt_plugin_values` 也一樣,`_detekt_cli_args(seg, _pp.basename(seg[0]))` 還在。
- 結果是一個函式裡有兩種取檔名的做法,而且 `\` 現在只在 gradle 判定上被認得,detekt 其他判定仍不認。
- helper 放的位置也讓 detekt 區反過來依賴 Android 區。
- 對照:`scripts/lumos:39017`、`scripts/lumos:39143`。

**問二:命名與錯誤處理**
- `_GRADLE_HEADS` 對得上既有的 `_*_NAMES` 常數寫法,例如 `_ANDROID_SCAN_NAMES`(`scripts/lumos:38967`)。
- `_is_gradle_head` 對得上既有的 `_is_*` 函式,例如 `_is_dep_manifest`(`scripts/lumos:40028`)。
- 兩者沒帶 `_detekt_` 或 `_android_` 前綴,但因為跨區共用,這樣合理,不算不一致。
- 符號連結略過有兩種寫法:
  - `_ci_config_paths` 用 `p.is_file() and not p.is_symlink()`(`scripts/lumos:38934`),跟既有的 `scripts/lumos:45346` 同款。
  - `_android_build_texts` 用 `_os.path.islink(fp)`(`scripts/lumos:38993`),跟該函式本來就用 `_os` 的寫法一致。
- 各自貼合所在函式的 Path 或 os 風格。repo 裡沒有共用的「不是符號連結的一般檔」helper,所以不算新增的第二種做法,不列。

**問三:第二種做法**
- 續行合併:`text.replace("\\\n", " ")` 是 `scripts/lumos` 裡唯一一份。我查過沒有既有的續行合併 helper,所以不是又一份。
- 符號連結判斷:見問二,沒有可共用的既有 helper,不算又一份。
- Jenkinsfile 剝註解:
  - 剝註解沿用 `_strip_c_comments`(`scripts/lumos:6826`),沒有另寫一套,這點是對的。
  - 但「Jenkinsfile 要用 `//` 剝」的判斷放在消費端,見 F2。
- CI 檔兩條讀法仍在。
  - `_detekt_ci_has_typed_task` 的 T4 直接 `p.read_text(...)` 讀原文(`scripts/lumos:38945`)。
  - A1 則經 `_ci_workflow_texts`(`scripts/lumos:60295`)去註解。
  - `_ci_config_paths` 已讓兩者共用路徑清單和符號連結略過,讀取與剝註解沒有統一。
  - 這輪沒宣稱處理,不另列發現。

F2
severity: minor
blocking: 否
引句:「if Path(path).name == "Jenkinsfile":」
- `_ci_workflow_texts` 的 docstring 寫「容錯跟哪些算註解只有一份」(`scripts/lumos:60296`)。
- 現在 Jenkinsfile 的 `//` 與 `/* */` 由 `_android_ci_lint_evidence` 這個消費端按檔名自行補剝,哪些算註解變成兩處在定。
- 同時 `_ci_workflow_texts` 對 Jenkinsfile 仍先照 YAML 的 `#` 規則剝一次。
- 把這個檔名分支放進 `_ci_workflow_texts` 才符合既有「只有一份」的原則;現狀只會影響之後第二個讀 Jenkinsfile 的消費端。
- 對照:`scripts/lumos:39035`、`scripts/lumos:60295`。

不對齊共 2 條,其中會擋的 0 條
