severity: clean

審查範圍:r2 修補差異,對照 `scripts/lumos` 合併快篩一帶與 `scripts/test_lumos.py`。我沒有跑測試,只讀程式與 grep。

**問 1 分層與依賴方向**

- 三個新抽出的函式都放在對的地方,沒有跨層直呼。
- `_cmd_arg_quote` 放在 `_run_cmd_expand` 正上方(`scripts/lumos:28072`),和它同層、同一個平台判斷(`_IS_WIN`)。呼叫端是 `_run_cmd_expand` 的 `{python}`、`{method}` 兩處和 `_choice_merge_cmd` 的 `--init-script`,都在同一段程式裡。依賴方向是合併指令組裝 → 代換函式 → 引號小工具,鄰居 `_choice_merge_cmd` 本來就經 `_run_cmd_expand` 這一支,沒有新增跨層呼叫。
- `_kill_merge_trip`(`scripts/lumos:29259`)定義在唯一呼叫端 `_kill_merge_breaker`(`:29222`)之後。鄰居也有「呼叫端在前、被呼叫的在後」的寫法,例如 `_kill_merge_base`(`:29096`)呼叫在它之後的 `_kill_merge_base_run`(`:29133`)。簽章 `(mg, plat, ...)` 跟 `_kill_merge_off(mg, plat, why, ...)`(`:29006`)同形,只動 `mg`、不碰 `c`,層次一致。
- `_choice_merge_event_line`(`:28887`)放在 `_choice_merge_events`(`:28901`)之前,和 `_choice_merge_facts` 在 `_choice_merge_classify` 之前一樣,是被呼叫的先定義。
- 這一問沒有不對齊。

**問 2 命名與錯誤處理**

- `_cmd_arg_quote` 的 `_cmd_` 開頭不是新慣例。`_cmd_basename`(`scripts/lumos:42127`)也是「指令字串的詞」這類小工具。`_cmd_*_locked` 那批是子命令實作,但它們帶 `_locked` 尾巴,不會混淆。
- `_kill_merge_trip` 和 `_choice_merge_event_line` 都沿用本區的 `_kill_merge_*` 與 `_choice_merge_*` 前綴。
- 印字方式一致。`_kill_merge_trip` 的警告跟原本跳開那兩處逐字相同:`print(f"⚠ {_kill_esc(plat)}:…", file=sys.stderr)`,平台名先過 `_kill_esc`。重試時間上限那處的 `print("⚠ …")` 沒動格式。
- 事件行不合就回 `None`,不丟例外,跟鄰居 `_choice_merge_shape` 回 `None` 的做法一致。
- 新增常數 `_CHOICE_MERGE_EVENTS` 沿用 `_CHOICE_MERGE_*` 命名與「一行註解帶計劃出處」的註解習慣。
- `_KillMerge.__init__` 新增 `hang_breaker=_CHOICE_MERGE_HANG_BREAKER`,跟既有的 `breaker=_CHOICE_MERGE_BREAKER`、`probe_every=` 是同一種形狀。
- 這一問沒有不對齊。

**問 3 第二種做法**

- 單參數加引號工具:專案裡已有的 `_sh_quote`(`scripts/lumos:468`)只是 `shlex.quote` 的包裝,文件寫明是「印給人照貼的指令」用,不管 Windows。在可執行指令字串這條路上,只有 `_run_cmd_expand` 做過 `_sp.list2cmdline([x]) if _IS_WIN else _shlex.quote(x)`。grep `list2cmdline` 全檔,除了新函式之外只有 `:28090` 的註解,表示沒有第二個 Windows 感知的引號工具。這輪是把原本在 `_run_cmd_expand` 內重複兩次、`_choice_merge_cmd` 再寫第三次的同一個三元式收成一支,是收斂,不是新增第二套。
- 這一問沒有不對齊。有一點可以順手補,不是對不齊:`_cmd_arg_quote` 的 docstring 沒提它跟 `_sh_quote`、`_drift_sh`(印給人用)的分工,下一個讀的人可能會誤以為重複。這屬於純風格,不列為不對齊。
- 事件行改用字串切:鄰居本來就有兩種做法並存。`_choice_merge_fullname`(`:28838`)用 `partition("::")`,`_choice_merge_shape`(`:28775`)用 `rpartition(":")`,這些是切自己組出來或結構固定的字串。`_CHOICE_MERGE_SYSKILL_RE`(`:28766`)和 `_KILL_COMPILE_RE`(`:28191`)是用 `search` 找固定字樣,沒有可變長度的兩側貪婪段,不會有回溯問題。舊的 `_CHOICE_MERGE_EVENT_RE` 是兩側可變長度,在長行上會變二次方。專案裡有先例把「避免回溯」當理由改寫:`scripts/lumos:4566` 的 `_RREF_LINK` 註解寫「不回溯成平方」,`:6821` 用佔有式量詞。這輪改成字串切、註解寫了理由,可以當作有依據的例外,不算第二種做法。
- 測試裡替換 `m._kill_run`:這是既有慣例。`scripts/test_lumos.py:147286`、`:147293`、`:147406`、`:148024` 都是 `m._kill_run = …` 加上 `try/finally` 還原,新測試的 `saved_run` 寫法跟它們一致。
- 兩種測試風格都有沿用:直接呼叫函式(`_kill_merge_breaker`、`_choice_merge_events`)和經 `_ckm_repo` 真跑假 Gradle,跟既有 `t_choice_kill_merge_*` 一樣。
- 這一問沒有不對齊。

**表態記錄的宣稱**:`py-eventloop`、`py-parallel` 等標「na」,跟 diff 一致,沒有 `async` 或並行的改動,我不反駁。

不對齊共 0 條,其中 major 0 條
