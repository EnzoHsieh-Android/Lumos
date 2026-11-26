severity: minor

**1. 分層與依賴方向**

兩處上一輪的點,修法本身都對齊既有做法,沒有新的跨層。
- `store` 改成呼叫 `_write_bytes_atomic(Path(dst), data)`,對照 `scripts/lumos:32277`。該函式的 docstring 明講「不另寫一份原子寫入」。`except OSError` 照舊,函式內的 BaseException 清暫存檔也不用 `store` 自己處理。
- `_kill_measure_singles` 的呼叫端原本要檢查 `len(got) > 4`,現在改成固定 `after` 回 6 項、沒給 `after` 時走 else 分支補同形的 `spent, cut`。`scripts/lumos:29122` 是 `cb.after` 唯一的傳入處,沒有別的呼叫端要跟著改。
- 新增的 `robo_zero` 只呼叫同檔既有的 `_choice_cov_proj_hits` 和 `_choice_cov_exec_robo`(`scripts/lumos:79750`、`79759`)。`store(keep=…)` 的 `keep` 只換掉 `_cache_path` 的結果。方向都是類別方法往下用模組級輔助函式,同 `take`、`cached` 的寫法。

**2. 命名與錯誤處理**

結構對,但有一處說明文字沒跟著修法改。

severity: minor
blocking: 否
引句:「紅記基準不綠;連續 _CHOICE_COV_RED_BREAKER 支掛覆蓋才紅就斷路(代碼審 r1 F3)。回傳 5 項:第 5 項是兩趟加起來的秒數,_kill_measure_singles 拿它估剩下的。」

這句 docstring 這輪沒被修補差異改到,留在 `scripts/lumos:29294`。但同一個函式現在每條 return 都是 6 項(`return (*res, res[2], True)` 等)。同類的 `after` docstring(`scripts/lumos:29263`)只寫「回傳寫進基準快取的那一份」,沒寫項數,所以只有這一處對不上。同一輪已經把 `_kill_measure_singles` 的 docstring 改成 6 項,鄰居的寫法是說明跟協議同步改。

其餘:
- 新方法 `robo_zero` 的命名是動詞或名詞短語,跟 `take`、`cached`、`breaker`、`settle` 沒有衝突。
- 例外處理沒有新增 bare except。
- 測試名 `t_choice_cov_*` 與同檔同族一致。
- check 訊息前綴 `r2 c1`、`F8` 跟既有的 `F9`、`F8` 慣例相同。

**3. 第二種做法**

本輪沒有引入第二種結構性做法。兩處值得標出的差異都屬測試側、風險低,所以只列 minor。

severity: minor
blocking: 否
引句:「cb = object.__new__(m._KillCovBase)」

`_ckc_cb_stub` 用 `object.__new__` 繞過 `__init__`,再逐一手設 `prep`、`c`、`names`、`meth`、`pkgs`、`why`、`got`、`seen`、`wrapped`、`tripped`、`trip_why`、`red_streak`、`full`、`_cmd`。這是整個測試檔裡唯一用 `object.__new__` 造樣板的地方(grep 僅此一處)。同族鄰居都是用真建構子加 SimpleNamespace 造替身,例如 `m._ChoiceKillRun(types.SimpleNamespace(find=…), Path(…), …)`(`scripts/test_lumos.py:146830`、`146864`)與 `m._KillMerge(_ckm_time.monotonic() + 600)`(`146619`)。`_KillCovBase.__init__(prep, c, names, pkgs, shape, ep, variant, init)` 在 `scripts/lumos:29170`,其中 `shape`、`ep`、`variant`、`init` 能直接給假值。手設內部欄位有一個隱憂:往後 `__init__` 多加欄位時,這個樣板不會跟著紅。

severity: minor
blocking: 否
引句:「gh = Path(_os_mod.environ.get("GRADLE_USER_HOME") or Path(pwd.getpwuid(_os_mod.getuid()).pw_dir) / ".gradle")」

這支測試用 `pwd.getpwuid` 取真實家目錄,去讀真的 Gradle 快取找 Groovy jar,繞過測試檔開頭的 HOME 隔離。我 grep 過,測試檔沒有其他地方用 `pwd.getpwuid` 或找 `~/.gradle/wrapper/dists`。隔離是這個專案的硬規矩(`scripts/test_lumos.py:545-560` 的機制測試明講,隔離被拆掉會紅)。
- 方向性對齊的部分:這支測試找不到工具時印「本機沒有…只做靜態檢查」並 return,跟 `scripts/test_lumos.py:38452`、`127116`、`129791` 的 detekt、ast-grep 作法一致。`java` 用 `which`,跟 `113851` 相同。
- 唯讀,風險低,所以只列 minor。

沒有發現的部分:
- `t_choice_cov_prune_keep` 與 `t_choice_cov_robo_zero_cache` 走既有的 `_ckc_repo`、`_ck_run`、`_ck_cleanup`、`_ckm_gov_ck`,沒有另寫一套。
- `_CKC_ANALYZE` 假腳本改成寫三個鍵並加 `omit_keys` 旋鈕,是沿用既有 `cov` 字典的選項(`drop_hits`、`noclasses`)的形狀,沒有新增另一條假腳本分支。

不對齊共 3 條,其中 major 0 條
