severity: major

**1. 分層與依賴方向**
- 結構沒有新的不一致。
  - `_KillPrep` 的建構、傳入 `cmd_guard_kill`、`remaining()` 與 `on_signal()` 都跟 `_KillMerge` 同形(`scripts/lumos:29010`)。
  - `_kill_signal_marked` 抽成 `_KillMerge` 與 `_KillPrep` 共用,合 r1 的建議。
  - `_choice_merge_init_path(c, name=_CHOICE_MERGE_INIT_NAME)` 與新抽的 `_choice_init_file_write` 都是一處改兩處用,事件腳本寫入也改走它。
  - `_KillCovBase` 的 `_Kill` 前綴與位置(`_KillPrep` 之後,`scripts/lumos:29165`)合鄰居慣例。
  - `_KillCovBase.start` 拿不到初始化腳本會印原因,r1 那條已修好。
- 依賴方向正常:`_kill_measure_singles` 仍是共用函式,準備物件經 `wrap`、`after` 掛進去,沒有跨層直呼。

**2. 命名與錯誤處理**
- 一處 minor:`_kill_measure_singles` 讓 `after` 回傳 4 項或 5 項,靠 `len(got) > 4` 判斷。
  - 對照:`_kill_run` 與合併快篩那條路都固定回 4 項(`scripts/lumos:28224` 起的 `_kill_run` 文件寫「回傳形狀不變」)。
  - 這是隱性的變長協議,但只限這一個呼叫點,結構還是對的。

severity: minor
blocking: 否
引句:「spent = got[4] if len(got) > 4 else got[2]   # after 回 5 項時第 5 項是這支實際花的秒數」

- 其餘錯誤處理(`except OSError` 回 `None` 或「分析失敗」、`print(... file=sys.stderr)` 配 `_kill_esc`)與鄰居一致。

**3. 第二種做法**
- 一處 major:`_KillCovBase.store` 自己手寫了一份「暫存檔再換名」的原子寫入。
  - 既有的 `_write_bytes_atomic(path, data)`(`scripts/lumos:32267`)已經做了這件事:暫存檔名帶 pid 與 uuid、O_EXCL 建檔、copymode、os.replace,丟例外會刪暫存檔。
  - 它的文件明寫「不另寫一份原子寫入」,別處也都用它(`scripts/lumos:15552`、`scripts/lumos:73945`、`scripts/lumos:77444`)。
  - 手寫版用固定的 `dst + ".tmp"` 當暫存名,正是 `_write_bytes_atomic` 文件裡記過的「兩個程序同時寫就互搶」那種做法,失敗時也不清暫存檔。
  - 續跑快取資料夾是跨 run 共用的,所以這不只是風格問題。
  - 修法:`store` 改呼叫 `_write_bytes_atomic(Path(dst), data)`,保留 `except OSError` 回 `None`。

severity: major
blocking: 是
引句:「with open(dst + ".tmp", "wb") as fh:」

不對齊共 2 條,其中 major 1 條

注意:派工詞要我檢查的鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/e66c46f232ba45926460402ae71cc97b4218b4c132a2860b2ad8075c5539647b.json.warming`,我沒有動它。派工詞也說照審查做即可,我也沒有刪。
