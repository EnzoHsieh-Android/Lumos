severity: minor

我看到的是:LUMOS-IMPACT 把 `Systems/測試假綠形態` 列為這支檔的家,並有一條 ★INVARIANT★(翻紅釘要配「現場成立」前置斷言)。這份 diff 動了 `scripts/test_lumos.py` 的 `main()`、新增守衛測試,並在那篇筆記摘要加一行 PITFALL。沒有表態紀錄要查。

**問 1:分層與依賴方向——對齊。**
- 新增兩行放在 `main()` 裡、緊接清 GIT_* 那段之後(`scripts/test_lumos.py:35490` 是 GIT_* 的 `environ.pop`,新增行接在它後面)。
- 兩者同樣用 `_os_env` 這個別名改 `os.environ`,不是在每支測試各自帶 env。
- 註解的寫法也一樣:`★標題★`、日期、症狀、「為什麼修在唯一進入點」。
- 沒有跨層直呼。

**問 2:命名與錯誤處理——大致對齊,有一處小落差。**
- 命名對齊:`t_runner_disables_child_colors` 和鄰居 `t_runner_isolates_real_home_and_tmp`(`scripts/test_lumos.py:520`)同屬 `t_runner_*`。
- docstring 對齊:都寫出身與日期,並寫明翻紅條件。
- 落差在 check 訊息。鄰居的訊息一律帶「隔離:」前綴。同檔還有「現場成立」前置斷言,例如 `scripts/test_lumos.py:585`、`scripts/test_lumos.py:591`、`scripts/test_lumos.py:630`。新測試用裸的「①②③」,沒有前綴,也沒有「★前置★ 現場成立」那種斷言。見 A1。
- PITFALL 行的鍵是齊的:有 `[出處:]`、`[根因:]`、`[test:]`,另有選填的 `[修法:]`。形狀和同節點其他 PITFALL 行一致。

**問 3:第二種做法——有並存,但不算結構分叉。**
- 這個 repo 已經有一處測試自己帶 NO_COLOR 給子程序:`scripts/test_lumos.py:50888`,`search -h` 那支,寫的是 `env=dict(_os.environ, NO_COLOR="1")`。
- 現在進入點統一設 `PYTHON_COLORS=0`。新註解自己寫「PYTHON_COLORS 優先於 FORCE_COLOR 與 NO_COLOR(Python 3.13 起)」,所以舊那支的 NO_COLOR 已經是冗餘。
- 讀的人會猜:那支為什麼還要帶 NO_COLOR,是另有原因,還是漏改。
- 兩者控制的現象不同(argparse 說明文字的色彩,對 traceback 色彩),也沒有衝突,所以不判重大。是否真的冗餘我沒有實跑驗證,標 ⚠。見 A2。

## A1 新守衛測試的 check 訊息少了鄰居慣用的前綴與前置斷言
severity: minor
blocking: 否
引句:「    check("②沒有 FORCE_COLOR", "FORCE_COLOR" not in os.environ, repr(os.environ.get("FORCE_COLOR")))」
佐證:file: `scripts/test_lumos.py:520`
佐證:file: `scripts/test_lumos.py:585`
失敗場景:鄰居守衛的訊息都帶領域前綴「隔離:」,並放「★前置★ 現場成立」。新測試只有「①②③」。另外 ③ 的子程序本來就繼承進程環境,所以 ③ 只靠 ① 已成立的環境變數,沒有獨立證明現場。FORCE_COLOR 走不到假紅路徑時,② 照綠,和鄰居用前置斷言防的盲區相同。

## A2 進入點統一設色彩變數,但 `search -h` 那支仍自帶 NO_COLOR
severity: minor
⚠
blocking: 否
引句:「    # 修在唯一進入點、理由同上面清 GIT_*:對現有與未來起子程序比對輸出的測試都自動成立,不用每支各自帶 env。」
佐證:file: `scripts/test_lumos.py:50888`
失敗場景:註解宣稱「不用每支各自帶 env」,但 `scripts/test_lumos.py:50888` 還留著自帶 NO_COLOR 的做法。兩套並存,下一個要寫「比對子程序輸出」測試的人不知道該學哪一套。

不對齊共 2 條,其中重大 0 條
總結:這次修法的位置和寫法跟清 GIT_* 那段幾乎一樣,沒有另立一套架構,只是新測試的訊息格式比鄰居少了前綴與前置檢查,而且舊的 NO_COLOR 做法沒順手收掉。
