severity: clean

已看,無:

改動範圍是 `scripts/lumos` 裡 `cmd_loop_replay` 內層函式 `_load_rows()` 的一行過濾條件,從
`if d.get("loop") == loop_id:` 改成 `if isinstance(d, dict) and d.get("loop") == loop_id and d.get("kind") != "spec-gate":`,
外加一支新測試與一行圖譜 PITFALL。逐項核對如下:

1) 凍結與回放兩側是否同一支讀帳函式——是。`_load_rows()` 定義在 `cmd_loop_replay` 內,`--freeze` 分支與
`--golden` 分支都呼叫它(分別在 `raw, parsed = _load_rows()` 與 `raw, _parsed_live = _load_rows()`),兩側用的過濾
邏輯完全同一份程式碼,不會出現「凍結當下」與「回放當下」用不同判斷而閉包雜湊對不起來的問題。凍結時寫進 golden 的
`all_row_shas` 本來就是過濾後的 `raw`,回放時重新載入的 `raw` 用同一過濾條件比對,兩邊自洽。

2) 已凍過的舊 golden 回放會不會被這次改動變紅——實測不會。掃了 repo 現有 154 份 `governance/replay/*/verdict.json`,
沒有一份的 rows 裡含 `kind=spec-gate`;帳本裡帶 spec-gate 留痕的 9 個 loop 編號裡,只有「審查跑滿上限提示」
「逃逸帳對得起來」兩個曾被凍結,而它們的 verdict.json 是這次同一個提交(8cdfef63)裡用已修好的程式碼重新凍的
(frozen_at 2026-09-26 21:02),重新確認過裡面 24 列都不含 spec-gate 那筆。也就是說沒有「舊 golden 用未修版凍、
新程式碼讀出來變少從而誤報帳被動」的情形。

3) `isinstance(d, dict)` 這個新判斷不是行為倒退,是順帶補了一個既有的洞:改動前若帳本裡出現合法 JSON 但非物件的
一行(例如純字串或陣列——`json.loads` 不會丟 ValueError,但後面 `d.get(...)` 對非 dict 會丟 AttributeError),
`_load_rows()` 會直接整個指令炸掉未捕捉的例外。這支檔案裡至少 3 個既有函式(`_loop_close_stamps`、
`cmd_loop_status`、`_loop_records`)都已經對同一類壞行加了 `isinstance(d, dict)` 防呆,這次是把
`cmd_loop_replay` 補齊到同一慣例,不是新引入的副作用。

4) 同族缺陷排查——`grep` 全檔案 `get("loop")` 相關的讀帳位置,凡是會餵進 `_loop_status_disposal`(判定「帶輪次/
不帶輪次一致性」的那支函式)的呼叫點只有 4 處:`cmd_loop_replay` 的兩處(636、650 行,這次修的)、golden 回放
重算那處(798 行,吃的是凍結時已過濆的 `g.get("rows")`,天然一致)、以及 `cmd_loop_status`(9631 行叫用,9606
行已有 `d.get("kind") != "spec-gate"`)。另外 `cmd_loop_verify_progress`(9090 行)、`_loop_records`(9914 行)
也都已經有同樣的過濾。其餘讀 `.canary-log.jsonl` 按 loop 分組的地方(`_escape_rows_for`、`cmd_severity_check`、
`cmd_canary` 的定錨檢查、`cmd_loop_list`、`cmd_loop_canary_stats`、`_auto_escape`、`cmd_loop_escape`)用途都不是
「判斷輪次是否一致」,spec-gate 列混進去不影響它們的邏輯(例如 canary_stats 本來就先篩 `kind in ("caught","missed")`
才會用到 loop)。沒有找到還缺這個過濾、會被同一症狀打到的地方。

5) 測試載重宣稱——實跑驗證。在乾淨拷貝上先跑新測試 `t_loop_replay_ignores_spec_gate_rows` 全綠(凍結 rc0、
回放 rc0);接著把 `_load_rows()` 裡的過濾條件手動改回舊版(拿掉 `isinstance` 與 `kind != "spec-gate"`),清掉
`__pycache__` 後重跑,兩個斷言都翻紅,錯誤訊息正是「這個審查編號的記錄有的帶輪次、有的不帶」——與這個 bug 真實
症狀的敘述一致,確認測試會對修法翻紅、不是空氣測試。之後還原檔案、再跑 `-k loop_replay`(21 案例全過,含既有
的「凍結列被改=帳被動紅」等竄改偵測測試沒被這次改動弱化)、`-k spec_gate`(101 過)、`-k disposal`(172 過),
均無回歸。

6) 圖譜筆記位置——`design-loop.md` 的 `about_code: scripts/lumos`,是這支檔的登記的家,PITFALL 落點正確;
新增的 `[test:t_loop_replay_ignores_spec_gate_rows]` 與實際測試函式名一致。

引句:「不然整個迴圈被判成「有的帶輪次有的不帶」而拒凍」
