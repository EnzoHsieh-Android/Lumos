severity: major

(接手席視角:只拿 spec 與 repo 動手。已確認可行的部分:`cmd_guard_kill` 的順序確實是 讀檔→`open(target,"w")` 寫壞法→`_kill_run`→`git checkout --`→判定,utime 放寫入後、`_kill_run` 前與還原成功後都接得上;行程內呼叫可用 `_load_lumos_inproc()` 載入再 `m.cmd_guard_kill(m.Env(v), "Systems/Limit")`,`sys.stderr` 在呼叫時才取,可用 redirect_stderr 接;`import os` 在函式內拿到的是同一個 os 模組,換掉 `os.utime` 會生效。以下是照 spec 做會卡住或漏掉的地方。)

## F1 S2「不靠時序」只講到寫入那一側,還原那一側與「判定不受影響」沒有寫得出會翻紅的斷言
severity: major
blocking: 是
引句:「第一條改 a、第二條改 b、測試同時 import a 與 b 時,第二條的判定不應受第一條影響」
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力驗證編譯快取誤判_計劃.md:46`
1. 要在不靠時序下驗修改時間,只能讓 run_cmd 的測試腳本(得先 commit 進 worktree 的 HEAD)自己 `os.stat` 後寫到工作樹外的絕對路徑檔,事後由測試讀。spec 沒寫這個做法(前置掃描只提過,沒進 spec)。實作者得自己猜。
2. 還原之後設的時間,只有「下一條配方的那次測試執行」看得到(a 的 mtime 在第二次執行時才被記錄);最後一條配方的還原時間在 worktree 刪掉後量不到(除非 `--keep-worktree`,spec 也沒提)。所以 S2「還原之後」子句只有在 a/b 兩條以上時才可驗。
3. 更關鍵:把「還原後 utime」整段拿掉,S2 的寫入側 mtime 斷言仍全綠。會讓它翻紅的條件是「測試執行 ≥1 秒,使還原寫回的 mtime 等於剛設的未來時間 M」(前置掃描 BUG-1),這需要測試腳本刻意 sleep ≥1.1 秒;spec 只說「不靠時序」,沒說要用 sleep 來把這個時序變成確定的。照字面寫的 S2 測試抓不到這次前置掃描才補進來的缺口,補丁沒有回歸守衛。
4. 「第二條判定不受影響」這句在未修版本要翻紅,需要:第一條壞法與原檔同大小、同秒內、a 被還原後再被 b 條的測試 import。這同樣靠時序(假綠只會在慢機器出現),不屬於「不靠時序」的那一半。spec 沒區分哪句話是確定性斷言、哪句是時序斷言。
建議:在〈做法〉或 S2 寫明 (a) 用 run_cmd 腳本記 mtime 到工作樹外檔;(b) 還原側用「測試腳本 sleep 1.1 秒」製造確定的紅;(c) 最後一條的還原不在驗證範圍或明講用 `--keep-worktree`。

## F2 S3 的提醒「一行」語意不清,測試斷言與還原失敗時的狀態會被迫猜
severity: minor
blocking: 否
引句:「設時間失敗(`os.utime` 丟出 OSError)不擋:印一行提醒到標準錯誤」
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力驗證編譯快取誤判_計劃.md:41`
1. utime 在每條配方有兩個位置(寫入後、還原後),替身讓 `os.utime` 一律丟錯時,一條配方會印 1 行還是 2 行?每條各一行還是整個指令只印一次?S3 測試要斷言行數或字樣,spec 沒定。
2. 設時間失敗時「同一組上一次設的時間」要不要更新?下一條若 utime 恢復正常,`max(現在+1, 上一次+1)` 用哪個「上一次」沒寫。
3. 提醒字樣沒給;spec 另要求別在 `cmd_guard_kill` 原始碼新增 `"verdict": "…"` 字面(文件守衛 `test_lumos.py:25180` 以該函式原始碼切片抽值域),實作者要自己避開,可在 S3 一併寫「提醒文字不含 verdict 字面」。
4. S3 與 S1/S2 共用同一個 `[test:t_guard_kill_no_stale_build_cache]`;S3 需要行程內載入加換掉全域 `os.utime`,S1 需要真的 subprocess 跑兩條,放在同一個測試函式內任一段紅都難定位。前置掃描已建議拆名,spec 沒採納也沒說理由。

## F3 S1 的「本機實測 5/5」只在 macOS 內建 3.9 的快取位置下成立,測試用哪個直譯器沒寫
severity: minor
blocking: 否
引句:「S1 的測試要在一秒內連跑兩條才會重現,本機實測 5/5」
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力驗證編譯快取誤判_計劃.md:57`
1. `_mk_kill_env` 的 run_cmd 寫死 `python3 test_guard.py`(`scripts/test_lumos.py:20339` 起),在本機是 3.9(快取在 `~/Library/Caches/com.apple.python/<絕對路徑>`),CI 與 CLAUDE.md 規定的 3.14 則寫工作樹 `__pycache__`。spec 的 5/5 只量了 3.9,沒說 3.14 下 S1 也會重現,也沒說實作者該用 `python3` 還是 `sys.executable`。
2. 若用 `sys.executable`(3.14)而 pyc 判準相同,理論上可重現,但 spec 沒寫、實作者得自己試;試不出來時無從判斷是測試造得不對還是環境不同。

## F4 要同步的文件沒列齊:Issue 的 REVISIT 與狀態、guard-kill 節點要改哪幾處,spec 只寫了「補一句」
severity: minor
blocking: 否
引句:「Issue 原本建議甲(或清快取),這裡改選乙,Issue 跟著補一句。」
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力驗證編譯快取誤判_計劃.md:27`
1. 現況:Issue 摘要裡仍有「REVISIT:2026-11-01 …跑測試前設 `PYTHONDONTWRITEBYTECODE=1`,或每條還原後清掉工作樹裡的 `__pycache__`」(`docs/lumos-toolchain-knowledge/Issues/guard kill在Python專案會沿用編譯快取誤判殺得掉.md` summary),與本計劃選乙矛盾,而且日期(11-01)跟本計劃 REVISIT(10-15)不同天;spec 沒說這行要撤掉或改寫,也沒說實作完 Issue 的 status 要改 resolved(用 `lumos set`)。
2. Issue 內文與摘要把快取寫成工作樹的 `__pycache__`,本計劃自己說 3.9 在 `~/Library/Caches`,兩邊說法不同,spec 沒列為要修。
3. `Systems/guard-kill` 是 lands_in,但 spec 沒寫要在哪裡寫什麼:概述/FLOW 一行(壞法與還原後設嚴格遞增未來 mtime)、〈實作位置〉、TEST 行加新測試名、「誠實界線」要不要提未來時間副作用。實作紀錄節只留「(實作後補)」。改了 `scripts/lumos` 與 `scripts/test_lumos.py` 的家也要確認都有 about_code(CLAUDE.md 鐵則 5)。
4. 〈回退〉說 revert 後 `[test:]` 懸空時才處理,但沒說 revert 時 guard-kill 節點新增的那段也要一起撤。

## F5 REVISIT 與 PRIOR-ART 裡的一句未驗宣稱沒有可執行的判準
severity: minor
blocking: 否
引句:「REVISIT:2026-10-15 跟 rtb 回報同一天,看 rtb 那邊 guard kill 有沒有因為修改時間在未來而冒出新的警告或錯誤」
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力驗證編譯快取誤判_計劃.md:29`
1. 判準取決於 rtb 人工回報:`.kill-log.jsonl` 不記 stderr,S3 的提醒、make 的時鐘偏差警告都不會進帳;沒有指令或檔案可在 10-15 查。到期當天接手的人只能問人。可寫成:指定看哪個欄位(如 kill-log 裡 `error`/`abort` 比例相對改動前)或明寫「沒收到 rtb 回報就算無事並關掉」。
2. RETIRE-IF 可執行(讀 `cmd_guard_kill` 是否仍共用單一 worktree),不需改。
3. 〈實務隱患〉另有一句:「make 會印『時鐘偏差』警告(Python、Gradle、jest、go 不會)」(同檔第 56 行),前置掃描已標未驗,spec 仍原樣寫成肯定句;實作者無從知道是誰驗的。建議標「未驗」或刪括號。

已讀,無 finding 的節:〈範圍〉(核對「不改合約測試閘與其他呼叫 `_kill_run` 的地方」:`_kill_run` 實有 4 處呼叫 `scripts/lumos:13922/13950/38139/38192`,本案不改它,範圍成立);〈回退〉主句;〈實務隱患〉「既有測試」句(核對 `scripts/test_lumos.py:25180` 的 verdict 值域抽取,屬實)。

最高等級:major;blocking 共 1 條
