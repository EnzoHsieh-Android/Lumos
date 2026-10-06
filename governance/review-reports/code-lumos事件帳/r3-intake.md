# code-lumos事件帳 r3 收貨紀錄

- 六席全新報告(r3-snapshot.patch,HEAD 51f3a76e;外家兩席依 Enzo 指示缺席)格式正規化、引句全數錨定;架構對齊席 clean、沒有引句可對。
- 末輪(high 上限 3 輪)仍有一族 major(深巢狀讀得進、印不出),兩席從兩個出口獨立抓到。Enzo 2026-10-05 裁「全修、不開第四輪」:依根因四組折入,各組先紅測試,修完請報 major 的兩席續談只驗收自己那條(兩席都回「已修」,沒發現修補帶出新問題)。
- 編號:r3 各席用 r3 加席位字母加條號(c 正確性、p 併發資源、e 邊界輸入、k 合約圖譜、s 資安)。

## 編排者重現表

| id | 宣稱 | 重現 | 結果 | 處置 |
|---|---|---|---|---|
| r3c1 / r3e1 | 七萬到十一萬層巢狀讀得進、印的時候 RecursionError(文字、--json、列表) | t_events_r3_hostile_output 先紅:one 與 one_json 都 Traceback,壞行 0 | HIT | 折(讀取端深度 32、單行 64KB) |
| r3e2 | 超長工具名把 ✓/✗ 截掉 | 同上先紅:找不到以 ✗ 結尾的行 | HIT | 折(欄位各自截斷) |
| r3e3 | 讀取端沒有大小上限 | 同上先紅:沒有 _EVENTS_MAX_FILE | HIT | 折(塊檔 16MB 略過計數) |
| r3c2 / r3e5 / r3s1 | 讀取端沒過上層連結檢查,讀到 repo 外 | t_events_r3_path_trust 先紅:四種讀法都 rc0 印出 OUTSIDE | HIT | 折 |
| r3s2 | 兩處路徑原樣印出控制字元 | 同上先紅:輸出含 ESC 與 BEL | HIT | 折 |
| r3e4 / r3c3 | gitdir 相對路徑誤擋、壞位元組丟 Traceback | 同上先紅:相對路徑印不可信;壞位元組 UnicodeDecodeError | HIT | 折 |
| r3c3 | --repo 給子目錄被擋且原因講錯 | 同上先紅:子目錄 prune 沒清掉 | HIT | 折 |
| r3e6 | 信任判斷沒有正向案例 | 補正向案例(絕對路徑 worktree 清得到);改壞相對路徑解讀後翻紅 | HIT | 折 |
| r3p1 | 掃描就失敗卻說刪了一部分 | t_events_r3_honest_messages 先紅:failed=[('A', True)] | HIT | 折 |
| r3p2 | 等待沒有總預算、逾時不重查 | 同上先紅:_ledger_wait 不收 budget | HIT | 折 |
| r3p3 | 卸載做一半仍給兩條手動指令 | 同上先紅;另改 t_teardown_removes_ledger_plugin 的舊期望 | HIT | 折 |
| r3k5 | 沒附外掛時提示叫人跑 install | 同上先紅:輸出含 lumos install | HIT | 折 |
| r3k1 | 計劃 S6 S7 S8 與做法段跟程式不符 | 讀計劃第 94、109、128 行與程式比對,屬實 | HIT | 折(改條款與做法段) |
| r3k2 | 規則綁的測試守不住宣稱的三件中兩件;enforcement 的連結檢查沒測試 | 新增 t_enforcement_ledger_row_symlinks;拿掉上層連結檢查後翻紅;規則補綁兩支測試 | HIT | 折 |
| r3k3 | 24 小時保護只靠天數下限、筆記沒寫 | 讀系統筆記屬實 | HIT | 折(寫進規則行與讀取指令說明) |
| r3k4 | 3 秒逾時只寫在計劃 | 讀系統筆記屬實 | HIT | 折(寫進規則行、綁 git_hang 測試) |

## 改壞驗證(修後)

深度上限、單行長度、塊檔大小、讀取端連結、相對 gitdir、子目錄 repo、掃描與刪除分開、等待總預算、enforcement 連結九處逐一拿掉,對應測試全部翻紅;還原後與修好版本逐位元組一致。

## 效能(修後,本機單次)

15MB 塊檔(15 萬筆事件夾 200 行三萬層巢狀):三種輸出都在 2.5 秒內,記憶體峰值約 450MB。
