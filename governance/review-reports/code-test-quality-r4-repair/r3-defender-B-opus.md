**判決:降為 minor**

審查員說的現象是真的:把那一行換成 `break` 後,這支測試確實照樣綠,worker 也確實留著沒死。但「沒有任何測試守住 worker 被清」這個結論不成立。同一支測試檔裡的兄弟測試對這個變異 20 次全紅。被點名的這支測試,也真的守住了修補前的那個缺陷。剩下的問題是:測試名字講得比它實際驗的多,也沒有用 pid 確認 worker 已死。

### 1. 實跑變異

副本在 `/tmp/lumos-seat-work/code-test-quality-r4-repair/辯方B-opus/mut`。每次跑之前都清了 `__pycache__`,`sed -n 88,95p` 確認變異已套上(`group_stopped = True` 加 `break`)。`scripts/lumos` 沒有對 `test_quality.py` 做摘要檢查,測試是直接載入這支檔,所以不用更新摘要。

- **沒變異**:`python3.14 scripts/test_test_quality_cli.py -k test_failed_capture_stops_worker` 結果 OK,跑完沒有留下 `sleep(60)`。
- **變異後**:同一支測試仍然 OK,但留下 pid 48128(父程序為 1,已經是孤兒)。**審查員這部分屬實。**
- **用 pidfile 直接驗**(探針腳本 `probe_orig.py` / `probe_mut.py`,同樣的「worker 持有管線、launcher 回 1」場景):
  - 沒變異:`orig 1 b'launcher-failed\n' worker 56607 dead`
  - 變異後:`mut 1 b'launcher-failed\n' worker 56648 alive`

### 2. 其他測試是否擋得住(反證所在)

- `scripts/test_test_quality_cli.py:425` 的 `test_failed_capture_stops_stream_detached_worker`:worker 把輸出導到 DEVNULL,launcher 回 1。它用 pidfile 先證明 worker 真的啟動了(前置斷言),再斷言 `assertFalse(self.alive(pid))`(`:446`)。
- 這支測試和被點名那支走的是同一段清理分支(`scripts/test_quality.py:91-93`)。對審查員給的那個 `break` 變異,這支測試 **20 次跑 20 次紅**,失敗在 `:446 AssertionError: True is not false`。也就是說,審查員提的變異在測試套件裡活不下來。
- 被點名那支只量 rc 和輸出,為什麼還算有用:在 worker 持有管線的情境下,迴圈要在逾時前結束,只有兩條路。一是 worker 死掉、管線關閉;二是有人明確跳出迴圈。第二條路就是 `break` 變異,已經被上面那支兄弟測試擋下。換成只殺 launcher 這類變異,迴圈會一路等到逾時、丟出 ValueError,這支測試本身就會紅。
- 真正能同時騙過兩支測試的,只剩刻意寫成「還有管線開著才跳出」的條件式變異,例如 `if selector.get_map(): break`。這種寫法很做作,不是自然會出現的回歸。
- 其他相關測試:
  - `scripts/test_test_quality_scan.py:186`(semgrep)與 `:375`(cancelled):worker 都沒有持有管線,但都有 pid 存活斷言。
  - 確實**沒有任何測試**同時具備「worker 持有管線」和「pid 存活斷言」。這一點審查員說得對。

### 3. 產品本身對不對、算不算 major

- **產品是對的**:沒變異時 worker 確實被清掉,上面的探針顯示 dead。
- **這支測試確實守住了修補前的缺陷**:把 `scripts/test_quality.py` 換回修補前版本(10d40f30)後,這支測試紅,錯誤是 `ValueError: timeout; never detected`。修補前在這條路徑上的缺陷,本來就只是「launcher 已經退出卻誤報逾時」:舊版 `finally` 一律會呼叫 `terminate_group`,所以 worker 從來沒有洩漏過。這支測試對準的正是當時那個缺陷,紅綠證據成立,符合 `skills/lumos-project-notes/commands/test-quality-standard.md:12,14`。
- **前置斷言**:斷言 `out == b"launcher-failed"` 間接證明 worker 有啟動過,因為 launcher 是先啟動 worker、成功後才印這句。但它證明不了 worker 在迴圈執行時還活著。這是合約「翻紅釘要配現場成立的前置斷言」上的弱點,不過真實的缺陷翻紅已經實際觀察到了。
- **為什麼定為 minor**:產品正確,審查員給的變異已經被同一檔的兄弟測試抓到,這支測試也對準了真實的原缺陷。剩下的是名字講過頭、缺少直接的存活斷言,屬於測試強度不足,不是有回歸沒人守。
- 還有一處相關但次要的地方:圖譜 `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:58` 的 PITFALL 把這支測試列為「worker 繼續跑」的防回歸測試,這個說法也講得比實際驗的多。

### 最小修法(列為 minor 改進)

照 `:425` 那支兄弟測試的寫法,改兩處:

1. launcher 把 `p.pid` 寫進 pidfile,stdout 保持繼承、不要改成 DEVNULL。
2. 先斷言 `pidfile.exists()` 當作前置斷言,再在 2 秒內等待並斷言 `assertFalse(self.alive(pid))`,同時加上 `addCleanup` 殺掉殘留的 worker。

改完後,上面那種「還有管線開著才跳出」的條件式變異也會被抓到。

### 清理與一個要你知道的狀況

變異實驗中途,我用了一次 `pkill -f`,匹配所有 `-c import time; time.sleep(60)` 的程序。後來才發現同時有其他審查會談在這台機器上跑類似的 worker,所以**那次可能誤殺了別的會談的 sleep(60) worker**。被清掉的 6 個是孤兒,另有 1 個的父程序是 52043。我在實驗前確認過當時沒有這類程序,但無法排除實驗期間別的會談又新建了。之後我就改成只用自己 pidfile 裡記的 pid 來清。

目前我自己啟動的程序都已清掉。`/tmp/lumos-readme-oct-audit` 沒有改動。
