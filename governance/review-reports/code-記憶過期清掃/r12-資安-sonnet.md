severity: minor

## 發現1

severity: minor

引句:「子行程開在自己的行程群組裡,停整個群組。」

觀察到什麼:

這一輪把清掃子行程(以下稱 L2)改成用 `start_new_session=True` 開,逾時時 `_kill_tree()` 對 L2 的 pgid 做 `os.killpg()`,確實解掉了 r11 minor(L2 底下的 `git fetch` 孫行程變孤兒)。但這個做法有一個副作用:L2 現在跟最外層那支真正被 Claude Code 登記、掛著「12 秒外層逾時」的行程(以下稱 L1,也就是 `python3 memory-sweep.py --budget 12 --quiet` 這支本尊)**不再同一個行程群組**。

常見的 supervisor 慣例(包括這份程式碼自己這一輪剛採用的手法)是:啟動一支要限時的行程時就順手幫它開一個新 session/pgid,逾時了直接 `killpg` 整組收乾淨,不用一個一個追子孫。如果 Claude Code 自己的「外層 12 秒逾時」也是用這種常見手法實作(對它登記、啟動的 hook 行程做群組級收尾),那麼在**這一輪修好之前**,L2 沒有自己的 session,會跟著 L1 同一個 pgid——外層真的出手時會連 L2 一起清掉,是無意間被外層的收尾模式接住;**這一輪修好之後**,L2 被特意隔到自己的 session/pgid,外層對 L1 做群組級 `killpg` 就再也碰不到 L2(以及 L2 底下還在跑的 `git fetch`)。

實測(模擬「外層對 L1 的整個 process group 做 killpg」這個常見收尾動作,拿掉 sleep 换成貼近真實的兩層行程結構——L1 用 `start_new_session=True` 啟動、L1 內部再照 `_watchdog()` 現在的真正寫法用 `start_new_session=True` 開出 L2):

```
python3 /tmp/r12_review/sim_outer_kill.py
```
輸出:
```
L1 pid=2249 pgid=2249, L2 pid=2250 pgid=2250
killpg 呼叫沒有丟例外
waitpid 嘗試 (非阻塞): (2249, 9)
```
```
ps aux | grep "time.sleep(20)"
enzo  2250  ...  SNs  ...  Python -c import time; time.sleep(20)
```
L1(pid 2249)被 SIGKILL 收掉(`waitpid` 回傳訊號 9),但 L2(pid 2250)在 `killpg(L1 的 pgid, SIGKILL)` 之後仍然活著(`ps` 還看得到,狀態 `SNs`)。

會造成什麼:這個路徑要真正發生,前提是「這支 hook 自己的內層自律(`_watchdog_limit()` 算出來、正常態約 10.2 秒的自我逾時)先失守」——目前測過的阻塞手法(FIFO/裝置檔)在這一輪修完後已經在 lstat 那一步就被擋掉,不會拖到真的靠外層 12 秒兜底(見下面「已確認」的計時)。也就是說,這一輪把「行程群組收尾」這件事做對了一半:確實讓自己的 `_watchdog()` 逾時分支能連根拔起清掃子行程,但同時也讓自己**脫離了外層原本可能提供的那張安全網**——如果未來又冒出一種目前想不到、繞得過內層自律的卡法(這份程式碼自己的註解也承認「前四輪每封一種變形就冒出下一種」),外層真的要出手時反而撈不到已經被隔離出去的 L2/L3,殘留的 `git fetch` 之類行程會在「Claude Code 認為這支 hook 已經死了」之後繼續跑。屬於防禦縱深層面的取捨副作用,不是靠現有 .md 內容就能單獨打穿的洞。

建議怎麼修:如果要兩邊都要(自己能連根拔起,又不喪失外層可能提供的群組級收尾),可以讓 L1 自己也主動加入 L2 的 session,或者反過來讓 L1 保留在外層那個 pgid 裡、L2 才獨立,並讓 `_kill_tree` 在收到訊號(例如自己被 SIGTERM)時也轉手 `killpg` 給 L2;比較簡單的做法是在 L1 的最上層(`__main__` 或 `guard()` 外面)裝一個訊號處理器,收到終止訊號時先幫忙 `killpg(L2 的 pgid)` 再讓自己死掉。

## 已確認

- 看門時間從程式一啟動就算(`_PROC_START`)+ 下限 0.5 秒:正常情境下(空記憶目錄、`--budget 12`)整支 CLI 實跑僅 0.8 秒,沒有誤判超時;`_watchdog_limit()` 在真實呼叫路徑下離下限很遠(git rev-parse 正常態遠低於它自己設的 3 秒上限),下限只在「已經耗掉接近整個外層預算」的極端情境才會介入,不受記憶檔內容影響。
- 具名管道(FIFO)不再讓讀檔卡住:`mkfifo` 放進記憶目錄後,用真實呼叫方式(`--budget 12 --quiet --dir <含 FIFO 目錄>`)實跑僅 0.134 秒完成,直接報「不是一般檔(具名管道、裝置檔之類),不當成記憶檔讀」——比 r11 當時「靠 12 秒逾時兜底」更好,`lstat` 加 `O_NONBLOCK` 讓這條路徑根本不會走到會卡住的那一步。
- 逾時分支整支 CLI 端到端驗證:用 `--budget 0.05` 逼真的逾時路徑,0.585 秒內看門層正確印出「超時沒跑完」且帶完整安全框,退出碼 0,行為符合設計宣稱。
- 逾時後連根拔起孫行程:`python3 scripts/test_lumos.py -k memory_sweep` 66 項全過(含 ㉘㉙㉚㉛ 這一輪新增的測項),㉚ 驗證看門逾時後,子行程開出的孫行程(`sleep 30`)確實跟著一起被清掉,不再變孤兒。
- 子行程 `--budget` 參數改寫(`_child_argv`)只讀取 L1 自己的 `sys.argv`(來自 hook 註冊的固定呼叫方式),不觸碰記憶檔內容,沒有被記憶檔影響的路徑。
