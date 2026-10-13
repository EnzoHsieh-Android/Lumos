severity: minor

## 1. 壞設定值沒有出聲,不像其他設定讀取
severity: minor
blocking: 否
引句:「return v if isinstance(v, int) and not isinstance(v, bool) and 2 <= v <= 16 else 1」
file: `scripts/lumos:30572`(`_note_shape_config`)、`scripts/lumos:6801`(note_lint 讀取)、`scripts/lumos:29067`(`_nodehome_config`)
- 專案讀 `.lumos/config.json` 的慣例是「壞值退回預設,並留一句警告」。例如 `note_lint.gate` 看不懂時,會附上「看不懂(只認…),已用 on」。`note_shape` 的壞值和 JSON 讀不了也一樣有警告。
- `_bound_tests_parallel` 把 `"4"`、`2.5`、`17`、設定檔壞掉全部默默當成 1,沒有任何提示。使用者把值寫成 `"4"` 會以為已經並行,實際上是循序,而且看不出來。
- 計劃檔「做法」一節有寫明這是刻意的「一律當 1」,所以結構上對得上,只是少了這個專案常見的警告。
- `except (OSError, ValueError, AttributeError)` 也比相鄰的 `_config_has_top_run_cmd`(`scripts/lumos` 約 48230 行)窄,後者用 `except Exception`。

## 2. 又自己寫了一份直接讀設定檔的函式
severity: minor
blocking: 否
引句:「cfg = _json.loads((Path(repo_root) / ".lumos" / "config.json").read_text(encoding="utf-8"))」
file: `scripts/lumos:5825`(`load_platforms`,已負責解析此檔)、`scripts/lumos:48230`(`_config_has_top_run_cmd`)
- 專案裡直接讀這支設定檔的 helper 本來就多,各讀各的,例如 `_config_has_top_run_cmd`、`_nodehome_config`、`_note_shape_config`、`_lumos_config_near_vault`。這個 diff 只是再加一支,跟 `_config_has_top_run_cmd` 的形狀相同。
- 整個專案沒有共用的 config 讀取器,所以不算引入第二種做法,只是沿用既有的分散寫法。
- 兩個小差異。這支用函式內的 `import json as _json`,而 `_config_has_top_run_cmd` 直接用模組層的 `json`。它也不看捷徑檔,但 `_config_has_top_run_cmd` 同樣不看,所以不算不一致。

## 3. secs 語意改變,但相鄰欄位與日誌沒跟著對齊
severity: minor
blocking: 否
引句:「secs = _wall」
file: `scripts/lumos:47887`(`_bound_tests_log` 的 `secs`/`calc_secs` 說明)、`scripts/lumos:48385` 起各 return 的 `reason`
- `_run_bound_tests` 每個結果元組的第 6 欄仍是單項秒數,`_bound_tests_check` 的 `secs` 改成牆上時間。同一個詞在兩層意思不同。
- `_bound_tests_log` 的說明寫 `secs=跑測試那段;calc_secs=算波及那段`。改成牆上時間後其實更貼近這句話,所以日誌文字沒有衝突。
- 帳上舊紀錄的 secs 是相加值,新紀錄是牆上時間,同一個欄位前後語意不一樣。計劃檔 `REVISIT` 有註明「舊帳不拿來比」。
- 唯一遺留的問題是程式碼沒有任何標記,日後看 `secs` 的人不知道哪天之前的值是相加值。

## 三問

**1. 分層與依賴方向:對齊。**
- 改動只在 `_run_bound_tests` 內部排程,新增的 `_bound_tests_parallel` 是同層的小 helper。
- 沒有跨層直呼,仍然經過既有的 `_kill_run`(`scripts/lumos:17175`)。
- 結果順序與 `tails` 的形狀照舊。
- `_bound_tests_check` 只加了計時。

**2. 命名與錯誤處理:大致對齊,有兩點小出入。**
- 命名 `_bound_tests_parallel` 與 `_bound_tests_log`、`_bound_tests_check` 同前綴,對得上。
- 設定鍵 `bound_tests` 是獨立區塊,與 `note_lint`、`note_shape` 並列。
- 壞值回預設符合慣例,但缺少警告(見 finding 1)。
- 執行緒池用法是 `ThreadPoolExecutor` 搭配 `ex.map` 和 `with`,並用 `min(workers, len(jobs))` 限制人數,寫法標準。
- 全專案 `scripts/lumos` 只有這一處使用 `ThreadPoolExecutor`;`scripts/hooks/pre-push:682` 的切片是 shell 背景工作加 `--shard`,屬於不同層次(跨程序切測試檔),不算同一種問題的第二種做法。
- `ex.map` 裡 `_one` 若拋例外,會在組結果前中斷,不會被當成單項紅燈。循序路徑 `seen.update(_one(k) for k in jobs)` 也一樣,所以行為一致,沒有新差異。

**3. 第二種做法:沒有。**
- 我用 Grep 查過 `ThreadPoolExecutor`、`concurrent.futures`、`Pool(`,`scripts/lumos` 只有這個 diff 新增的那一處。
- 單支執行沿用 `_kill_run`。去重鍵沿用原本的 `(root, cmd)`。
- 沒有重寫並行或執行 helper。
- 設定讀取確實又加了一支(見 finding 2),但專案本來就沒有共用 helper,所以只算次要。

不對齊共 3 條,其中 major 0 條
