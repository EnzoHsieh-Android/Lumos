1. **severity: major**

   引句:「★flock 只鎖「讀配額→append started」與終局 append 兩小段」

   問題：終局 append 也使用 `LOCK_EX|LOCK_NB`，但規格只定義「搶不到就跳過 selfaudit 段」。若派工已完成後終局鎖碰撞，該輪已不能安全「跳過」：`done/fail/abort/stale` 會遺失。尤其遺失 `stale` 會錯誤占用週配額；下次又會把仍在帳上的 `started` 誤補成 `orphan`。規格沒有 retry、阻塞補寫或 durable deferred append，故 NB 快速失敗與終局必須耐久兩者不相容。

   查證：`/tmp/selfaudit-loop-v5-r3.md:113-121`；既有先例只將 NB 失敗用於「尚未寫入前整批退出」，不是已完成外部工作後丟棄結果：`governance/eval/refresh_labels.py:52-73`。

   能翻紅的最小重現：

   ```python
   # python3 /tmp/repro_terminal_nb.py
   import fcntl, json, multiprocessing as mp, os, tempfile, time

   ledger = tempfile.mktemp()
   lockfile = ledger + ".lock"
   open(ledger, "w").write(
       json.dumps({"week":"2026-W35","stem":"A","kind":"started","ts":"t0"}) + "\n"
   )

   def holder():
       with open(lockfile, "w") as f:
           fcntl.flock(f, fcntl.LOCK_EX)
           time.sleep(1)

   p = mp.Process(target=holder)
   p.start()
   time.sleep(.2)

   # 模擬派工已完成，現在依 spec 用 NB append 終局。
   with open(lockfile, "w") as f:
       try:
           fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
           with open(ledger, "a") as out:
               out.write(json.dumps(
                   {"week":"2026-W35","stem":"A","kind":"stale","ts":"t1"}
               ) + "\n")
       except BlockingIOError:
           pass  # spec 的快速失敗路徑沒有補寫機制

   p.join()
   rows = [json.loads(x) for x in open(ledger)]
   assert any(x["kind"] == "stale" for x in rows), rows
   ```

2. **severity: major**

   引句:「有 started 無終局=下次進場補記 kind=orphan」

   問題：窄鎖釋放後派工可運行最長 900 秒，但下一個並行進場看見「started 無終局」時，無法區分「前一行程被殺」與「前一行程仍在正常派工」。帳目沒有 attempt/run id、PID/lease、存活探測或 orphan 最小年齡。因此正常在途派工會被補成 `orphan`；稍後原行程再 append `done/stale`，同一筆 `started` 便具有兩個終局。此時同 stem 多列無法可靠配對，也直接推翻 orphan 的語意及「耐久預約已提供跨程序已佔用信號」的宣稱。

   查證：`/tmp/selfaudit-loop-v5-r3.md:110-121`；派工 timeout 見 `/tmp/selfaudit-loop-v5-r3.md:85`。

   能翻紅的最小重現：

   ```python
   # python3 /tmp/repro_false_orphan.py
   import json, multiprocessing as mp, tempfile, time

   ledger = tempfile.mktemp()

   def append(kind):
       with open(ledger, "a") as f:
           f.write(json.dumps({
               "week":"2026-W35", "stem":"A", "kind":kind, "ts":time.time()
           }) + "\n")

   def live_dispatch():
       append("started")
       time.sleep(1)       # 正常且仍在 900 秒 timeout 內
       append("done")

   p = mp.Process(target=live_dispatch)
   p.start()
   time.sleep(.2)

   rows = [json.loads(x) for x in open(ledger)]
   if sum(x["kind"] == "started" for x in rows) > sum(
       x["kind"] in {"done","fail","abort","stale","orphan"} for x in rows
   ):
       append("orphan")    # 「下次進場補記」會誤判正常在途工作

   p.join()
   rows = [json.loads(x) for x in open(ledger)]
   terminals = [x for x in rows if x["kind"] != "started"]
   assert len(terminals) == 1, rows
   ```

附帶驗證：五路徑 `rsync --exclude` 後再 `git add -A && commit` 的實跑因唯讀沙盒禁止 `mktemp`，未能重現；命令在建立暫存目錄時即以 `Operation not permitted` 結束。就 Git 語意而言，排除檔會被 snapshot commit 收成基線刪除，提交後 `status`/`diff` 應為乾淨，未發現否決級反例。

最嚴重 severity：major
