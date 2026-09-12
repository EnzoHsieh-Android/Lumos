severity: blocker

1. `home_audit.py sample` 在沒給 `--out`、且抽樣裡有任何一對路徑跑出 repo 外(新加的 `safe_under` 擋下)時,整份報告(包含其餘全部合法配對的內容)完全不印到 stdout,退出碼仍是 0,審查員看不到任何資料也不知道資料不見了。實測:一個合法配對(`Systems/正常.md ← src/good.py`)加一個路徑穿越配對(`../../../../../../etc/passwd`),跑 `home_audit.py sample --vault … --repo …`(不帶 `--out`)結果 rc=0、stdout 是 0 bytes,只有 stderr 印出跟穿越那一對無關的警告;合法那對的抽查內容整個消失,不是被過濾掉一項,是整份不印。原因是 `if outside: ...(印警告到 stderr) else: print(text)` 這個 if/else 把「印報告」跟「outside 非空」綁在一起,只要有一對跑出 repo 外就整段跳過 `print(text)`。
引句:「print(f"⚠ 有 {len(outside)} 對的路徑跑出專案外面,沒有讀它們的內容:", file=sys.stderr)」
file: `governance/eval/home_audit.py:141-148`
severity: blocker
blocking: 是

2. `_impact_about_max()` 的「無效值退回預設」只擋住了非數字字串與 0/負數,沒擋 `nan`/`inf`——這兩個字串是合法 float,會通過 `_impact_knob` 的 `float()` 檢查,再到 `int()` 轉型時分別噴 `ValueError: cannot convert float NaN to integer` 與 `OverflowError`,而且沒有任何 try/except 接住,整支 `lumos impact --file/--diff`(含 pre-commit/pre-push 會呼叫的路徑)直接掛掉、印出完整 traceback。實測:設 `LUMOS_IMPACT_ABOUT_MAX=nan` 跑 `impact --file src/pay.py --json` 直接拋出未捕捉的 `ValueError`(呼叫鏈 `cmd_impact → _impact_confirmed_homes → _impact_about_max`),`=inf` 則是 `OverflowError`,兩者都會讓這支「防止家這條入口被靜默關掉」的旋鈕反而變成「整個工具被吵鬧地弄壞」。這支函式的 docstring 自己講「這跟旁邊「非數字退回預設」同一套處理:無效就當沒設」,但 nan/inf 恰好卡在「是數字、不是那三種被擋掉的無效值」的縫裡,沒有被這句話真正涵蓋到。
引句:「★0 與負數是無效值,退回預設★」
file: `scripts/lumos:21642-21650`
severity: major
blocking: 是

3. `_lens_kind_of` 這次改成「一篇同時是事故又是家要印成『事故·家』、兩個都不能蓋掉對方」,我實測這條邏輯本身是對的(`dispatch-lens HEAD~1..HEAD` 真的印出 `[事故·家]`,`build_ranked_context` 也印出空白分開的 `★家★ ⚠事故`),但整份 diff 與既有測試裡找不到任何一支測試餵進「同一個節點 kind=incident 又 home=True」這個組合去驗證輸出字串。既有 `t_dispatch_lens_diff_includes_homes`(只驗純家)與 `t_impact_hook_shows_home_label`(只驗純家/純直接)都不覆蓋這個此次修正真正要解決的場景,往後有人不小心把 `_lens_kind_of` 改回舊版「home 蓋過 kind」也不會有測試翻紅。
引句:「★事故不能被蓋掉★:一篇既是家、又出過事故,讀派工單的人最需要知道的是」
file: `scripts/lumos:22446-22457`
severity: minor
blocking: 否
