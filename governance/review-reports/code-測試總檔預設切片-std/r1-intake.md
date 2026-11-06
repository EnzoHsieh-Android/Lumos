# r1 收貨紀錄(code-測試總檔預設切片-std)

## 為什麼有這個編號

- 原編號 code-測試總檔預設切片 判 light(工具把 scripts/test_lumos.py 當測試檔、不算程式檔),編排者多派一席正確性;正確性席報 blocker 1、major 2,light 誤判,照規則升級開本編號走 standard。light 那輪兩份報告與帳在 governance/review-reports/code-測試總檔預設切片/。

## light 輪(升級前)發現的去向(全數折入,修補提交 4efa74fb6)

| 來源 | 發現 | 去向 |
|---|---|---|
| light 正確性 #1(blocker) | 中斷測試在背景環境 SIGINT 被忽略,必紅留孤兒 | 折:沙盒母程序開頭把 SIGINT 裝回預設;背景環境 `bash -c '… & wait $!'` 重跑全綠 |
| light 正確性 #2(major) | 只收領頭、測試驗不到孫程序 | 折:每組都送 KILL 不看領頭死活;假測試開忽略 TERM 的孫程序並驗它被收 |
| light 正確性 #3(major) | 開片途中非 Ctrl-C 例外留孤兒、片數無上限、HUP 沒接 | 折:BaseException 也先收片;片數上限 16;接 HUP |
| light 正確性 #4 | 片數判法跟推送前閘不一致、「²」崩潰 | 折:只認半形數字,沒設或空是 4 |
| light 正確性 #5 | -x 切片後只停紅那一片 | 折:帶 -x 照舊單一程序 |
| light 正確性 #6 | 合併摘要沒記當掉的片、空清單照印 | 折:摘要加 bad_shards、skip_over;空清單不印 |
| light 架構對齊 #1 | 暫存前綴與清理 | 本輪 a2 一起折 |
| light 架構對齊 #2 | TERM 回 130 跟推送前閘 143 不一致 | 折:回 128+訊號編號 |
| light 架構對齊 #3 | 收子程序又一份寫法 | 本輪 a1 一起處理 |

## 本輪重現表

| id | 來源 | 重現 | 判定 |
|---|---|---|---|
| c1 | 正確性 #1 | 同程序先設 HUP 為 SIG_IGN 再呼叫 _fanout_trap,getsignal 變成處理器(席位實跑) | HIT,折入:原本忽略的不接;t_runner_fanout_signal_handling ①,改壞(N11)翻紅 |
| c2 | 正確性 #2 | 席位實測 -k t_runner_default_fanout_green 單支峰值約 5.3GB | HIT,折入:不需驗預設 4 片的測試改開 2 片;計劃隱患記實測並開 REVISIT 2026-12-05 看推送前閘與 CI |
| c3 | 正確性 #3 | 讀碼:Popen 回傳到 append 之間收到 TERM 會漏記 | HIT,折入:開片到記下之間擋訊號,子程序開頭還原遮罩;signal_handling ③,改壞(N14)翻紅 |
| c4 | 正確性 #4 | 讀碼:except 區塊內處理器仍裝著 | HIT,折入:開始收片先忽略三個訊號、收完還原;signal_handling ④ 與 spawn_error,改壞(N12、N13)翻紅 |
| c5 | 正確性 #5 | 讀碼:lumos-fanout- 不在修剪範圍 | HIT,折入:前綴改 gctl-run-fanout-,超過一天由既有修剪收;紅燈測試驗前綴,改壞(N15)翻紅 |
| a1 | 架構對齊 #1 | 讀碼:收法 TERM→等→KILL 跟 _kill_proc_group 只送 KILL 不同 | 折入(文件):計劃做法 2 寫明為什麼不借 _kill_proc_group(測試總檔零依賴不 import lumos、先 TERM 讓暫存收尾跑得到) |
| a2 | 架構對齊 #2 | 同 c5 | HIT,折入(同 c5) |
| a3 | 架構對齊 #3 | 同檔已有 _ppc_sigint_default | HIT,折入:中斷測試改用它 |

## 折入後驗證

- 背景環境(`env -u LUMOS_FANOUT_CHILD -u LUMOS_TEST_SHARDS bash -c '… --serial -k t_runner_ … & wait $!'`)197 過 0 紅;新增同程序訊號測試 9 過、開片出錯 3 過。
- 本輪新守衛 N11–N15 各改壞一次都翻紅(N13 第一次沒紅,補 spawn_error 的收尾檢查後翻紅);變異副本加程序數上限 40 的看門狗,沒碰 _fanout_wanted。
- 規格閘在實作前版本重跑:11 條紅 10、綠 1(keeps),放行留痕已更新。
