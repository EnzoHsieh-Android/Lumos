# r2 收貨、重現與處置

## 材料與編制

- 修補鏡頭:修前 f80352f6 → 修後 5ce8115d(`r2-repair-binding.json`)。修補差異依區塊拆三段,每席必讀自己那段(lumos 382 行、測試 530 行、文件 455 行),同塊完整改動當上下文;架構對齊席讀 lumos 與測試兩段修補差異。四席皆全新 Claude Sonnet,派工詞禁止讀 r1-* 卷證。
- 完整快照 `r2-snapshot.patch` 範圍 69ac44b2..88322e46(合併最新主線之後);分支相對主線的程式改動清單與合併前相同。
- 配對案例:r1 修補前沒有先準備 repair/preserve 案例(binding 已記),由新席自選。本輪修補前,編排者在下方〈修前選例〉先列好。

## 收貨

- 四份報告從子代理逐字稿抽最後一則正式報告存檔,都不含跳脫字。都過 `report-normalize`、`refcheck`(主程式席一處 missing 是它拿來測路徑解析的輸入字串 `scripts/../scripts/hooks`,不是引用)。
- `quote-check`:文件席 #6 錨不到,見下表 D6(機械重現 HIT)。其餘全數錨定。
- **退回一次**:測試假綠席 F3 寫 `severity: major` + `blocking: 否`,兩欄矛盾,退回該席重判;它回覆改成 minor + 否(理由:現行程式本身對,缺口是回歸測試少觀察同族其他變數)。照它的回覆改那兩行,其餘一字未動。
- 測試假綠席曾在自己的 clone 跑匯出環境的全套,46 分鐘未完成、自行中止;只有 `t_command_index_complete` 紅,未匯出環境也紅。

## 重現(編排者機械重現)

finding 編號:主程式席 M1–M4;測試假綠席 T1–T6;文件席 D1–D6;架構對齊席 A1–A3。

| finding | 重現 | 說明 |
|---|---|---|
| T2 | HIT | 工作目錄(88322e46)跑 `-k t_command_index_complete` → 13 passed, 1 failed,「總目錄控制在 4.5k 字元內」值 4525 |
| T1 / M4 | HIT | `_gate_event_fit(root, "note-reread", …)` 沒傳 `head_sha`;同檔另兩個呼叫端(筆記形狀擋放寬帳、舊句檢查帳)都傳。量的事件少了寫帳時才補的 commit 與 head_sha 兩欄 |
| T3 | 採信 | 席位改壞實驗:清除範圍縮成只清一個變數,測試照綠;子行程只跑回頭重讀那支,第二個變數沒有斷言觀察 |
| T4 | 採信 | 席位改壞實驗:拿掉符號連結/非一般檔/太大守門、資料夾符號連結判斷、吞形狀錯,`-k t_reread_block` 都照綠 |
| T5 | 採信 | 席位改壞實驗:`.git/hooks` 預設改錯字,相關測試全綠;`t_hooks_path_dir_shared` 是讀原始碼字串 |
| T6 = D1 | HIT | `Systems/存量漂移守衛.md` 第 164 行仍寫「行內以子字串出現…照判不了算」 |
| M1 | 採信 | 席位附重現腳本:未提交紀錄是 125000 層巢狀陣列(<256 KB),修後 `_note_reread_uncommitted` 丟 RecursionError、prepare 崩出堆疊;修前只比檔名不讀內容 |
| M2 | HIT(讀碼) | 大小訊息兩個數字都 `// 1024`,上限加 1 到加 1023 位元組時印「256 KB,超過上限 256 KB」 |
| M3 | 採信 | 席位重現:100 列 × 3300 字,提示只點最長那行;總量由列數乘行長決定 |
| D1 | HIT | 舊句檢查計劃、存量漂移守衛、那篇 Issue 的 DECISION/症狀/REVISIT 仍把超長行子字串判法當現況 |
| D2 | HIT(讀碼) | 帳的來源改成 `_in_ci()`(CI 或 GITHUB_ACTIONS),守檔計劃〈專案開關〉附近仍寫只看 CI |
| D3 | HIT(讀碼) | 轉擋計劃寫 `_note_reread_uncommitted` 只看「工作目錄有、頂端沒有」;真碼另要求讀得懂且 provenance_ok 為真 |
| D4 | HIT(讀碼) | prepare 與 check 的「還沒提交」提示仍印 `git add governance/reread-verdicts && git commit`(整個資料夾),修前就是這樣 |
| D5 | 採信 | CHANGELOG 只寫「有舊句要處理 CI 會紅」,沒寫名稱消失檢查判不了在 CI 也紅 |
| D6 | HIT | 引句用半形逗號,原文是全形「,」;README.md 第 113 行確有「Python 函式或指令旗標刪了、改名了,或程式檔刪了、搬走了」,真碼追的是函式、類別、模組層與類別層指派、旗標 |
| A1 | HIT(讀碼) | 判不了而擋下那筆記 `state: "undecidable"`,判不了但 warn(skipped)那筆沒有 |
| A2 | HIT(讀碼) | `_note_reread_uncommitted` 與 `_drift_ack_reread_verdicts` 各有一份「走訪工作目錄紀錄資料夾、擋符號連結、非一般檔、太大」的守門 |
| A3 | 採信 | 清 `LUMOS_SKIP_*` 是新的獨立函式,沒併進已經管 lumos 相關環境的 `_isolate_environment` |

## 修補因果(regression)

- 有證據屬上一輪修補造成:T1/M4、T2、T3、T4、M1、M2、M3、D1/T6、D2、D3、D6、A1、A2、A3。
- 原有漏查:D4(修前就印整個資料夾)、D5(修補補了一半)。
- 未判定:T5(預設路徑邏輯修前修後相同,缺口在修補之前就有)。

## 修前選例(本輪修補前列)

| 組 | repair(原問題要好) | preserve(既有正常行為不能壞) |
|---|---|---|
| 帳長度 | 30 條規則類條目、條目長度 ×1 與測試原本 ×N 各一案,寫出的整行 ≤4096 位元組(含 commit 與 head_sha) | 舊句檢查帳、筆記形狀擋放寬帳照原樣截(`-k gate_event`、`-k m1`) |
| 索引長度 | `t_command_index_complete` 轉綠 | 索引仍提到 `--kind reread`(`t_command_index_complete` 其他 13 條) |
| 紀錄讀取守門 | 未提交紀錄是深層巢狀 JSON、符號連結、太大、形狀壞,prepare 不崩、不算 wip;`drift ack --kind reread` 碰到同樣的檔照原本處理 | 正常未提交且 provenance_ok 為真的紀錄照算 wip(layer1 ⑥⑦) |
| 訊息 | 上限加 1 位元組時訊息不再自相矛盾;多列超限時提示講到列數 | 剛好等於上限照寫(`t_reread_record_refuses_unreadable_size` 對照組) |
| 測試 | 清變數測試同時觀察第二個同族變數;`.git/hooks` 預設路徑有行為測試 | 原本「拿掉清變數那行就紅」照紅 |
| 帳欄位 | warn 下判不了的 skipped 帳也記 state | block 下判不了的 blocked 帳照記 state |

## 處置

- 本輪有存活 major(T1、T2),code 迴圈 major 輪 accepted 必空,所以全部折入:M1–M4、T1–T6、D1–D6、A1–A3。

## 修補提交與驗收

- 59f8f92b:八組一起修(修補代理,修前先依上表列好原問題與保留案例,每組附改壞→紅;17 種改壞全數翻紅)。
- 編排者驗收:抽看帳長度那組真碼(量長度與寫帳都帶被推頂端版本號;清單搬出說明欄後,全檔沒有別處解析回頭重讀帳的說明欄);自己重跑 `t_command_index_complete` 14、`ledger_fits` 6、`runner_drops` 3、`t_reread_block` 91、`gate_event` 5、`drift_ack` 62、`hooks_path` 17、`t_drift_m1_long` 10,全綠。

## 記帳註記

- 各席 `--scope-lines` 記該席必讀的修補差異行數(主程式 382、測試 530、文件 455、架構對齊讀前兩段共 912);同塊完整改動是上下文,只查修補碰到的函式與呼叫者,不逐行審。
- 載體席選全數錨定的主程式席。T5 修補因果未判定(見上),依共用範本 §3.1 這輪帳不帶 `--regression-set`。
