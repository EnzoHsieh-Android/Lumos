severity: blocker

## Finding 1:送給模型的擋停訊息,在「shell 寫檔」這個本案要修的核心場景下,退化成不列檔名——實測重現

severity: blocker
blocking: 是

`main()` 新增的擋停分支裡,`turn_rel` 仍是拿 `collect_turn_actions` + `extract_bash_file_paths`（也就是舊的「認名字」列舉法：`EDIT_TOOLS` 三個工具 + `BASH_FILE_OPS_PATH_BEARING={"rm","mv","cp","git rm","git mv"}`）算出來的 `file_paths` 建的，`model_rel = [r for r in rel if r in turn_rel]` 對 shell 改的檔（`sed -i`/`echo >`/heredoc）永遠交集不到，於是送給模型的 `reason` 掉進 fallback 分支、變成「這一輪動到的檔算不出來,所以不列檔名」——這正是本案宣稱修好的那個場景。
引句:「model_rel = [r for r in rel if r in turn_rel]」
引句:「這一輪動到的檔算不出來,所以不列檔名」

**實測重現**（本機直接跑該 hook，不經測試套件）：造一個只用 `sed -i` 改 `scripts/keep.py`（未提交）的假逐字稿，餵給 `scripts/hooks/claude/check-graph-sync.py`（session 首次 Stop，未關閉擋停），實際輸出：
```
{"decision": "block", "reason": "LUMOS-STOP:改了程式碼但知識筆記沒跟著動\n工作樹上有 1 個程式碼檔還沒提交、筆記沒跟著動;這一輪動到的檔算不出來,所以不列檔名。"}
```
同一現場改用 `Edit` 工具（模擬編輯工具改檔），輸出正確列出 `scripts/keep.py`。對照組證明差異只來自「怎麼改的檔」，跟 S1 測試的翻紅釘同一個場景。

file: `scripts/hooks/claude/check-graph-sync.py:1027-1035`（實作）

七支新測試（`t_sync_nudge_*`）全部經由 `_run_stop` 呼叫、而 `_run_stop` 固定帶 `LUMOS_STOP_BLOCK_OFF=1`（見 `scripts/test_lumos.py:44065-44078` 註解「擋停關掉,只看提醒本身」），也就是**唯一會觸發上面這段 `model_rel` 邏輯的路徑（session 首次 Stop、未設關閉旗標）從未被任何一支新測試跑過**。這與驗證紀錄宣稱「每一條守衛都證明過『拆掉會翻紅』」不符——這段新增邏輯連正常路徑都沒驗過，遑論翻紅。
file: `docs/lumos-toolchain-knowledge/Verification/2026-09-18_收工點名改問版本控制.md:5`（summary 那句「七支新測試全綠,而且每一條守衛都證明過「拆掉會翻紅」」）

驗證紀錄第 82 行還寫「主流程不再拿它們（`collect_turn_actions` 等）算清單」，但上面的 `model_rel` 正是拿 `collect_turn_actions` 的輸出（經 `file_paths`）在「算清單」——決定送進模型那條訊息裡有沒有檔名，這句話對主流程整體而言不準確。
file: `docs/lumos-toolchain-knowledge/Verification/2026-09-18_收工點名改問版本控制.md:82`

計劃書驗收條件 12「擋停那條送給模型的訊息…確認只列這輪對話紀錄裡出現過的路徑」在驗證紀錄裡完全沒有對應段落被交代（沒有任何測試、任何手動記錄提到這條），而它實際的行為是本案要修的病换個位置重演。
file: `docs/lumos-toolchain-knowledge/Projects/收工點名問版本控制_計劃.md:272`（驗收條件 12）

## Finding 2:graph-sync-coverage.md「三個時機」表第一列仍寫舊語意（這輪動過圖譜/這輪沒動），跟同一篇緊接著的新增段落、跟改後的程式碼直接矛盾——而且計劃自己的驗收條件明講要同步這張表

severity: major
blocking: 是

`docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:51`（三個時機表第一列，本次 diff 未改動這一行，是既有文字原封不動留著）仍寫「即使這輪動過圖譜,仍點名「直接相關、這輪沒動」的篇」，用的是「這一輪」語意；但同一篇緊接在下面新增的 `## ★2026-09-18 起…` 一節明白寫「核心代價:清單是「工作樹上未提交的」,★不再宣稱切得出這一輪★」（`docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:74`），而程式碼裡閘門 3 的判準（`graph_touched = any(is_graph_file(...) for _, r in entries)`，`scripts/hooks/claude/check-graph-sync.py:950-953`）確實已經是拿 `git status` 全部未提交項目判斷，不再是「這一輪」。
file: `docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:51`
file: `docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:74`

計劃節點自己的驗收條件第 13 條寫明「落點那篇節點裡的『三個時機』表要同步更新成新的算法」，但這張表的第一列並沒有真的更新——同一次改動裡宣稱要做的事沒做到。
file: `docs/lumos-toolchain-knowledge/Projects/收工點名問版本控制_計劃.md:274`

## Finding 3:`touched_graph_via_cli` 變成死碼,沒人在文件或程式頭註解裡交代

severity: minor
blocking: 否

閘門 3 原本的判準 `graph_touched_via_edit or touched_graph_via_cli(bash_commands)` 被整段換成只問版本控制（`scripts/hooks/claude/check-graph-sync.py:950-953`），但 `touched_graph_via_cli()` 這個函式本體（`scripts/hooks/claude/check-graph-sync.py:414`）沒有被刪除、也不再被 `main()` 任何地方呼叫，檔頭的新註解與計劃筆記都沒提到這個函式已經是殘跡。功能上不算回歸（版本控制查詢本來就會涵蓋 CLI 寫入造成的檔案異動），但留著一段沒人指名是死碼的函式,下一個 session 讀到容易誤以為它還在生效。

## 總結

最嚴重等級:blocker(Finding 1)。blocking 共 2 條(Finding 1、Finding 2)。
