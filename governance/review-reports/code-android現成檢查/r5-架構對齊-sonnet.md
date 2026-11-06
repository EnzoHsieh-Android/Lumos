severity: major

先講結論。上一輪兩項宣稱屬實:
- 取檔名已統一。`scripts/lumos` 裡不再有拿 posixpath 取命令詞檔名的寫法,`os.path.basename` 只剩無關的兩處(29650、41264)。
- Jenkinsfile 的註解判斷已收進 `_ci_workflow_texts`(`scripts/lumos:60330`)。

但新抽的 `_path_resolves_in_root` 留下了舊的內嵌寫法,另有一處錯誤處理語意改了。

**① 分層與依賴方向**

呼叫方向是對的。`_ci_config_paths` 與 `_android_build_texts` 這兩個 Android 掃描函式往下呼叫共用的路徑 helper,`_repo_path_unsafe` 也呼叫它,沒有反向或跨層直呼。Jenkinsfile 剝註解下沉到 CI 讀取層,消費端 A1 不再自己補剝,方向正確。

F1 `_detekt_segment_codes` 內部有兩種問法
引句:「head = _cmd_basename(seg[0])」
引句:「if head in _GRADLE_HEADS:」
- 同一個函式先自己算 basename 再比對 `_GRADLE_HEADS`,而同一份補丁新增的 `_is_gradle_head` 就是做這件事。
- `_detekt_plugin_values` 呼叫 `_is_gradle_head(seg[0])`(`scripts/lumos:39067`),判定函式卻直接比對,「是不是 gradle 詞」有兩種問法。
- 結構上屬分層小瑕疵。
severity: minor
blocking: 否

**② 命名與錯誤處理**

`_cmd_basename` 的命名跟 `_is_gradle_head` 一致,中文 docstring 的出處寫法也跟既有函式同款。

F2 `_path_resolves_in_root` 吞掉 OSError,改了 `_repo_path_unsafe` 原有的契約
引句:「解析不了(OSError、連結迴圈)當不在。」
- `_repo_path_unsafe` 的 docstring 寫明「OSError 往上拋、呼叫端自己講」(`scripts/lumos:52515`)。
- 呼叫端 `_secinv_vault_problem` 就接這個:`except (OSError, ValueError)`,回「檢查圖譜路徑時讀不了」(`scripts/lumos:7147`)。
- 抽出之後,解析失敗不會再往上拋,而是變成 "outside" 回報,呼叫端那條錯誤訊息就走不到了。
- 同族錯誤處理在兩處不一致。helper 自己的決定(連結迴圈當不在)合理,但 `_repo_path_unsafe` 沒有跟著更新 docstring 與呼叫端。
severity: minor
blocking: 否

**③ 第二種做法**

F3 `_path_resolves_in_root` 自稱唯一一份,但舊的內嵌寫法還在
引句:「★「解析後要在 repo 內」只有這一份★」
- 同一個判法至少還有兩處自寫,沒有改走新 helper:
  - `scripts/lumos:36768`:`Path(base).resolve().is_relative_to(Path(root).resolve())`,在 `_events_path_safe`。
  - `scripts/lumos:72252`:`p.resolve().is_relative_to(vroot)`。
- `_events_path_safe` 的前面還手寫逐層 `is_symlink` 迴圈,跟 `_repo_path_unsafe` 重疊。
- 這份補丁一邊宣稱統一、一邊新增 helper,舊寫法原封不動,等於又多了一份。
- 建議的處理:要嘛把這兩處改走新 helper,要嘛把「只有這一份」那句拿掉或限縮成「Android 掃描與 `_repo_path_unsafe` 共用」。
severity: major
blocking: 是

F4 `_CI_GRADLE_TASK_FIELD` 的縮排掃描跟既有 YAML 讀法同族,但縮排量法不同
引句:「ind = len(ln) - len(ln.lstrip())」
- 專案沒有 YAML 套件(零依賴)。既有讀法是逐行縮排掃描,例如 `_ci_jobs_calling_without_full_history`,它也吃 `_ci_workflow_texts` 的輸出(`scripts/lumos:60375` 附近)。
- 兩邊都是手寫縮排狀態機,但既有的量縮排是 `len(ln) - len(ln.lstrip(" "))`,只算空格;新的 `lstrip()` 連 tab 都算。
- 沒有共用的縮排或區塊判斷 helper,等於各寫一套。
- 結構方向跟既有做法一致,只有細節不一致,所以不算新引入的第二種機制。
severity: minor
blocking: 否

不對齊共 4 條,其中會擋的 1 條。
