severity: major

(方法:在 --shared clone 對 scripts/lumos 做 19 個單點突變加 14 個組合突變,每次前清 __pycache__,跑 `-k guard_kill_no_` 與 `-k mtime_unsure`;另拿 d8b02331 的舊 scripts/lumos 配新測試當對照。)

## F1 「測試跑完那一秒」不記也照綠:S2 的跑完記帳沒有測試守住
severity: major
blocking: 是
引句:「                mstate["r"] = int(time.time())」
佐證行:file: `scripts/lumos:13987`(套壞法後測試跑完的記帳,patch 內該行出現兩次:baseline 後與壞法跑完後;這裡指壞法跑完那一處)
1. 突變:拿掉壞法跑完後那一行 `mstate["r"] = int(time.time())`(其餘不動),清快取後跑 `-k guard_kill_no_` 與 `-k mtime_unsure` → 全綠(GREEN)。
2. 它不是等效突變。最小重現(能當場翻紅):同上突變,再把 `t_guard_kill_no_stale_build_cache` ③ 的 test_guard.py 在寫紀錄檔前加一行 `time.sleep(1.3)`(讓一次測試跨過秒界,真實測試工具常超過 1 秒),跑 `-k guard_kill_no_stale` → ③ 翻紅:`✗ ③[S2] 每次寫檔…晚於上一次跑測試結束的秒`,「2 passed, 1 failed」。對照組:未突變的程式碼加同一行 sleep → 3 passed,所以紅是這個突變造成的,不是我改的測試太苛。
3. 原因:出貨的 ③ 測試只跑得很快(<1 秒),`mstate["w"]` 的秒恰好等於測試結束的秒,別處的等待與確認用 w 就補上了;一旦測試跑超過 1 秒,w 與 r 分開,漏記 r 會讓還原寫檔跟測試結束同一秒(正是 S2 要擋的狀況)。測試沒有任何一條讓「跑測試」耗時超過 1 秒,所以 r 這個欄位在條款層面等於沒人驗。
4. 建議:③ 的 test_guard.py 加 `time.sleep(1.1)`(或 ① 用慢測試),讓 r 與 w 不同秒。

## F2 `_kill_after_write` 的重試分支(utime、睡 1 秒、3 次、回 False)與 `_kill_wait_new_second` 的 3 秒上限完全沒有測試守住
severity: minor
blocking: 否
引句:「        time.sleep(1.0)\n        try:\n            os.utime(path)」
佐證行:file: `scripts/lumos:13751`(`_kill_after_write` 整個函式)
1. 突變 m7(utime 改設未來時間)、m18(拿掉睡 1 秒)、m19(utime 改成不做)、m12(3 秒上限拿掉)、m13(等待整個變空操作)單獨套都 GREEN。m7 尤其要注意:S3「不設未來時間」只被 `t_guard_kill_no_future_mtime` 守在「正常路徑」,而那條路徑(`mt > floor`)在真檔案系統上根本不會走到 utime;唯一碰到 utime 的 S4 測試把整個 `_kill_after_write` 換成 `lambda: False`,所以重試分支(也是設計審說「設到未來會造出假 killed」的那個分支)零測試。
2. m1、m2、m3、m4、m13 單獨 GREEN 是兩層互補(等待與寫後確認各自足以讓修改時間錯開)——這部分是等效,不算洞;但組合起來(例如 m13+m3+m4、m1+m3、m2+m4)都能被 ①②③ 翻紅,所以兩層同時拿掉有守住。
3. 缺口:真正走 utime 的分支沒有直接單元測試。建議直接呼叫 `m._kill_after_write(path, {"w": 現在秒+1, "r": 0})`,斷言回 False、且檔的 mtime 不晚於現在(守 S3 的重試分支),也一併守「3 次後放棄」。上限(m12)只在時鐘往回撥時才有差,要驗得 mock time,可接受不測。

## F3 Linux CI 檢查:不致恆綠恆紅,①偶爾不在修前翻紅(不影響修後)
severity: minor
blocking: 否
引句:「    e.pop("PYTHONDONTWRITEBYTECODE", None)」
佐證行:file: `scripts/test_lumos.py`(`_kgk_run`,patch 內該行)
1. 以舊 scripts/lumos(d8b02331)配新測試連跑 3 次:② ③ 三次全紅,① 三次中有 1 次沒紅(`1 passed, 3 failed` 與 `2 passed, 1 failed` 的差異),所以 ① 在舊碼下是時序依賴的,不是穩定的回歸守衛;修後 4 次皆綠,沒有偶發失敗。② ③ 才是穩定守衛,① 靠 ② ③ 補位,可接受。
2. Linux:Python 的 pyc 同樣用「原始檔 mtime 取整秒 + 大小」判定,所以 ①②③ 的重現原理在 Linux 成立(不是 macOS 專屬),不會恆綠。`_kgk_run` 清掉 PYTHONDONTWRITEBYTECODE 有效;但若 CI 設了 `PYTHONPYCACHEPREFIX` 或唯讀 cwd,pyc 不會寫在 worktree,① ② 會恆綠(舊碼也綠)——這是推測,未在 Linux 實跑,且沒看到 CI 這樣設,故只提醒。
3. 核心時鐘粗粒度(Linux 檔案時間戳取自快取時鐘,可能比牆鐘慢幾毫秒):`mt > floor` 在秒界附近可能偶爾判不過,走重試(睡 1 秒、utime),不會失敗,只多 1 秒;③ 的斷言用整秒比較且重試後成立,不會偶發紅。測試最慢 13 秒(超時上限 180 秒、餘裕 14x),不致在 CI 逾時。

## 其他核對(無缺口)
引句:「                    res["_mtime_unsure"] = True」
佐證行:file: `scripts/lumos:13999`(旁路欄設值處)
- S4:m9(weak 不算)、m10(--json 不濾)、m11(提醒每條印)都被 `t_guard_kill_mtime_unsure_is_weak` 翻紅;m8(任何情況都設未來時間)被 `t_guard_kill_no_future_mtime` 翻紅;m5(baseline 不記)被 ② ③ 翻紅。
- 注意:S4 測試把 `_kill_after_write` 換成恆 False 後,不會驗到「還原那一半」的 `and mt_ok` 單獨拿掉(m4 為 `pass` 的版本也 GREEN,因為套壞法那一半的 False 已經讓 weak 成立);這屬於 F2 的同類缺口,不另立。

最高等級:major
