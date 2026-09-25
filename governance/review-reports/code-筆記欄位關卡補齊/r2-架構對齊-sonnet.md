severity: clean

## 問 1:分層與依賴方向

新碼都留在 `scripts/lumos` 同一層(doctor/lint 這批函式),沒有新開模組、沒有跨層直呼。

最關鍵的一處是把 `_note_lint_config(_repo_root_from_env(env))` 改成 `_note_lint_config(_vault_repo_root(env))`(`scripts/lumos:1210`、`scripts/lumos:4835-4837`)。查了全檔,`_vault_repo_root` 已是本 repo 找 repo 根的主流做法(30+ 處呼叫,含 `_nodehome_config`、`_lint_load_and_validate` 等同層鄰居都用它),`_repo_root_from_env` 反而是舊的少數用法、且 `scripts/lumos:2770-2775` 留的註解已經記過兩者語意不同(standalone 時 `_repo_root_from_env` 回 parent,跟 `.git` 在 vault 內的定義互斥)。這處改動是把原本的離群用法收回主流,不是引入新依賴方向。

`run_doctor` 的 L 段迴圈裡新增 `try/except Exception as _ex`(`scripts/lumos:1223-1226`)包住 `_lint_collect`/`_lint_new_rules` 呼叫,是本檔 18 處 `for rel, n in sorted(notes.items())` 迴圈裡唯一一處這樣包的。但這是唯一一處「整個圖譜跑、輸入是任意人寫的 frontmatter」的新迴圈(其他迴圈原本就只讀 `n.fields`/`n.targets` 這種已經正規化過的欄位,不會踩到 lint 內部對 `type` 做集合查找的地雷),沒有既有鄰居做同一件事卻用別的寫法,所以不算「引入專案裡原本沒有的第二種做法」。

引句:「_nlc = _note_lint_config(_vault_repo_root(env))」(`scripts/lumos:1210`)

## 問 2:命名與錯誤處理

`_note_lint_config` 把回傳值從 `(mode, warns)` 元組改成 `{"mode":…, "warnings":…}` 字典,鍵名、預設值處理順序(捷徑檔→檔案不存在→JSON 壞掉→整份不是物件→鍵不是物件→值看不懂)完全比照 `_nodehome_config`(`scripts/lumos:21573-21631`)的既有形狀,連文件字串都明寫「結構照 _nodehome_config」。錯誤訊息句式(`f".lumos/config.json 讀不了({e.__class__.__name__})…"`、"看不懂(只認 …),已用 on")跟 `_nodehome_config` 逐字同款。

`_lint_collect` 對 `type` 非字串的新分支訊息「type 要是一個字串(一篇只有一種類型),你寫的是 {type(t).__name__}——改成 type: <類型>」,跟同函式既有的 `type『{t}』工具不認得…` 及 `_nodehome_config` 的 `bool` 單獨擋寫法(`scripts/lumos:21618`「★bool 要單獨擋★」同一種「先擋型別再擋值」節奏)一致。

異常訊息「lint 讀這篇時出錯({_ex.__class__.__name__}),開頭欄位可能寫成工具讀不懂的形狀——跑 lumos lint <節點> 看」跟既有「逐篇跑 lumos lint <節點> 看完整訊息;每條都講了怎麼修」(`scripts/lumos:1235`附近)同樣把使用者導去下一步指令,語氣一致。

引句:「cfg = {"mode": "warn", "warnings": []}」(`scripts/lumos:5108`)

## 問 3:第二種做法

沒找到自創工具函式取代既有同功能實作的情況——找根改用既有的 `_vault_repo_root`(沒有另開一支)、回傳形狀套用既有的 `_nodehome_config` 字典樣板(沒有自己發明新形狀)、`type`/日期防呆沿用本函式與 `_nodehome_config` 已經在用的「isinstance 先擋型別」節奏。測試也沿用 r1 就有的 `_nl_vault`/`_nl_note`/`_NL_OK_SYS` 輔助函式,沒有另開一組。

引句:「結構照 _nodehome_config:設定檔不存在 → 用預設、不警告」(`scripts/lumos:5103`)

不對齊共 0 條,其中 major 0 條。
