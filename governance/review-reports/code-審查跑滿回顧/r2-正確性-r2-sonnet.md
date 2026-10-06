severity: minor

席名:正確性-r2-sonnet。逐 hunk 走過的範圍與結論(其餘無發現):
- `_loop_records` 改走 `_canary_ledger_scan`:非物件行、loop 非字串列改成跳過(舊碼會 AttributeError),UnicodeDecodeError 與 OSError 行為保持;3039 列真帳掃描 0.03 秒、約 22MB,無效能問題。
- `_ledger_tail_needs_newline`:不存在/空檔/非一般檔回 False;半行結尾補一個換行;本機帳照樣走 `_regular_own_fd`;讀側都跳空行,補換行不改既有呼叫端行為。整行多 1 位元組(最多 4097)只影響版控帳的 `open("a")` 路徑,該路徑本來沒有 4096 上限檢查。
- `_retro_read_bytes`:O_NOFOLLOW/O_NONBLOCK/fstat 一般檔、256KB 整好放行、256KB+1 在第五次 read 取到 1 位元組判超過,邊界正確;管線、目錄、捷徑都回錯誤不卡住。
- `_cap_retro_check` 深層巢狀(深度 100000 的 JSON,Python 3.14.6 實跑)與孤立代理字元:不丟堆疊。
- `--template --write`:O_EXCL|O_NOFOLLOW 已存在(含懸空捷徑)回 2 不動檔;目錄不存在在更前面被卷證檢查擋成 2;見 F2 的寫一半殘檔。
- 同編號多筆人裁/回顧:`_cap_retro_status` 與 `cmd_loop_retro` 都取最後一筆人裁、其後最後一筆 recorded/skipped,兩處一致。
- 固定席圖譜(impact 27 席):`Issues/canary-record未落盤事件`、`design-loop`、`loop-convergence-recording`、`lumos-cli-lifecycle/read` 等,diff 沒動寫帳的落盤順序(擋點在寫帳之前,新換行補在寫帳字串上);沒看出破壞其宣稱的合約。`loop-convergence-recording` 的「各讀者對輪數認定一致」這個面向見 F1。

### F1 切行只修了一半:`loop status` 與 `canary record` 的重複檢查仍用 splitlines,輪數認定跟新讀法分歧(修補引起)
severity: minor
blocking: 否 — 只在帳列內含 U+2028/U+2029/U+0085 時發生;錯認的是「輪數/壞行數」,不是放行判定本身,且該分歧在舊碼就存在,只是這輪修補讓一半讀者對、一半不對
- 輸入:審查帳一列 `{"loop":"x","round":"r1","auditor":"a b",...}`(寫入端 `json.dumps(ensure_ascii=False)` 不跳脫 U+2028)。
- 走到:`_loop_records`/`_loop_records_checked`/`cap-decision`/`canary record` 擋點都走新的 `text.split("\n")`,認這列為 1 筆;但 `cmd_loop_status`(`loop status`、`--disposal`、`loop next` 的主讀取迴圈)與 `canary record` 的「找同座標列」仍用 `read_text(...).splitlines()`,把這列劈成兩半、兩半都是壞 JSON。
- 壞在哪:同一份帳,人裁/回顧一族算「1 輪」,處置閘算「0 列、2 條壞行」。cap-decision 記進治理帳的 `rounds` 會含處置閘看不到的輪次;第八步與第一步對同一迴圈的輪數不同。修補只改了 helper,沒有把其它 `.canary-log.jsonl` 讀者一併收斂。
- 引句:「    for line in text.split("\n"):」
- 佐證行:file: `scripts/lumos:11558`(`cmd_loop_status` 的 splitlines)、file: `scripts/lumos:9116`(同座標列查找的 splitlines)、file: `scripts/lumos:11354`(escape 統計的 splitlines)
- 重現(部分重現,未跑到端到端閘):
  ```
  python3 - <<'X'  # 載入 scripts/lumos 為模組,vault=<tmp>/vault,帳=上述一列
  print(len(_loop_records(env,"x")))      # 1
  # 等同 cmd_loop_status 的讀法:
  [json.loads(l) for l in text.splitlines() if l.strip()]   # 第一列即 ValueError → rows 0、badlines 2
  X
  ```
  輸出:`_loop_records: 1` / `loop status 讀法: rows 0 badlines 2`

### F2 狀態「沒有」時一律提示 `--template --write`,回顧檔已存在(手寫未 record、或寫一半殘檔)時照做回 2 走進死路
severity: minor
blocking: 否 — 只是提示指到會被拒的指令,沒有資料損失;拒絕訊息本身有講「先自己刪掉」
- 輸入:人裁已記、回顧檔 `cap-retro.json` 已存在但還沒 `--record`(例:代理剛寫好;或 `--template --write` 在 O_EXCL 建檔後、`os.write` 前被殺/磁碟滿,留下 0 位元組或半截檔)。狀態是 `none`。
- 走到:`_cap_retro_fix_cmd(root, loop_id, "none")` 不看檔在不在,固定回 `lumos loop retro <id> --template --write`;doctor [I2]、處置閘第八步、`canary record` 擋下、`loop next`、`retro-stats` 都印它。照貼 → `cmd_loop_retro` 的 `os.open(..., O_EXCL)` 丟 FileExistsError → 回 2「回顧檔已經存在…先自己刪掉再 --template --write」。
- 壞在哪:使用者該做的是 `--check`/`--record`(檔在)或先刪殘檔(半截檔),提示卻只給一條必被拒的指令;`stale` 才有分辨「改現有檔」的提示。寫一半的殘檔也沒有清理(`ok_w` 為假時直接 return 2,不 unlink 自己剛建的檔),`--check` 對它只會說不是合法 JSON。
- 引句:「def _cap_retro_fix_cmd(root, loop_id, state):」
- 佐證行:file: `scripts/lumos:13540`(_cap_retro_fix_cmd 的來源,新版位置見 diff)、file: `scripts/lumos:13595`(--write 的 FileExistsError 分支)
- 重現:`lumos loop retro <id> --template --write` 之後再執行一次同指令(模擬殘檔/手寫檔),rc=2;此時 `lumos doctor` 的 I2 仍印同一條指令。

總結:最嚴重 minor,blocking 0 條
