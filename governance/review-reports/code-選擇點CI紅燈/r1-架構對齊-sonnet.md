severity: clean

我讀完整份 patch,並對照了 `scripts/lumos` 和 `scripts/test_lumos.py` 的既有寫法,沒有發現跟專案做法不一致的地方。

## 問 1 分層與依賴方向:對齊
- 測試端:`t_choice_kill_interrupt` 的 Popen 直接重用既有的 `_ppc_sigint_default`,沒有另寫還原函式。這個函式定義在 `scripts/test_lumos.py:85512`。
- 既有呼叫端也是同一個用法:`scripts/test_lumos.py:139078` 的 lint-new 中斷測試、`scripts/test_lumos.py:86336` 的 `kw = dict(start_new_session=True, preexec_fn=_ppc_sigint_default)`,以及 `scripts/test_lumos.py:85527` 和 `scripts/test_lumos.py:31137`。
- 主程式端:`_GOV_FIELD_TYPES` 只改型別登記,沒有繞過 `_gov_event_types_ok` 另做判斷。
- 引句:「stdin=subprocess.DEVNULL, preexec_fn=_ppc_sigint_default)」

## 問 2 命名與錯誤處理:對齊
- `run_id` 拆成獨立一行 `"run_id": (str, int)`,寫法跟同表 `scripts/lumos:18315` 的 `"round": (str, int, type(None))` 一樣。
- 拆出來的前置註解說明兩本帳同名不同型,寫法跟鄰近的 `# 改動選擇點(...)` 註解一樣。
- 帳本節點的 PITFALL 行有 `[出處:]`、`[根因:]`、`[修法:]`、`[test:]`,形狀跟 `Systems/測試執行器.md` 既有兩條 SIGINT PITFALL 相同。
- 那兩條既有 PITFALL 也有 `[同族:]` 欄位,而且第二條同樣只寫測試名。
- `Systems/測試執行器.md` 新增的 PITFALL 寫了 `[同族:t_runner_fanout_signal_handling、_bt_spawn_probe]`,並放在既有兩條之後。
- `INDEX.md` 把 `choice-points`、`choice-kill` 併成 `choice-*(改動選擇點)`。同一格的 `reread-*(回頭重讀)` 已經是這種寫法。
- 引句:「"run_id": (str, int),」

## 問 3 第二種做法:沒有
- 沒有新增還原 SIGINT 的函式或另一套型別判斷。
- `(str, int)` 這種多型寫法在表裡本來就有,`scripts/lumos:18315` 和 `secs` 都是。
- 引句:「preexec_fn=_ppc_sigint_default)   # 分片在背景跑時繼承」

## 小備註(不計入不對齊)
- 新程式行把註解放在行尾,鄰居 `scripts/test_lumos.py:139074` 是放在呼叫前的註解行。這只是風格,依你的規則不列。
- `_GOV_FIELD_TYPES` 上方的標頭註解寫「現有的行一筆都不會被跳過」。這是 2026-10-01 的統計,已被這次紅燈證明失準,但屬於內容正確性,不是對齊問題。

表態記錄裡 py-eventloop、py-parallel 等 na 的宣稱,我對照 diff 都成立:改動內沒有 async 或並行。

不對齊共 0 條,其中 major 0 條
最嚴重:clean;blocking 共 0 條
