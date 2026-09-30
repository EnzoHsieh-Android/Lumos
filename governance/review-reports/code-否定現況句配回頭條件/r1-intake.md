# r1 收貨紀錄(code-否定現況句配回頭條件)

凍結材料:e6213559..1ca70d4f 的 git diff -U10(不含治理帳與錨點基準),1260 行;`r1-snapshot.patch`。分級:pitfalls 判 standard;因為動到筆記形狀擋與全域紀律範本,編排者在單審查員與架構對齊之外加派外家否決席。
3 席:正確性 opus、架構對齊 sonnet 5.5、外家否決 Codex(gpt-5.6-sol xhigh,唯讀沙盒)。

## 席位收貨

- 3 席全交;report-normalize 都已正規化;quote-check 全數錨定。
- 被審的複製在 17:42 被切成分離狀態(`checkout: moving from main to 1ca70d4f`),時間落在三席審查期間,實作者說不是它;三席都沒自報。切到的就是被審的那個提交,內容沒被動到;編排者之後把 main 快轉到修正提交並切回。主 repo reflog 沒有新動作。
- 發現 5 條(機器數):正確性 3、架構對齊 1、外家否決 1;major 1 條(外家否決 F1)。

## 判讀

- 外家否決 F1:新測試讀 skills/ 底下的檔,消費專案沒有這些檔,更新後全套測試必紅、推送與 CI 被擋。席位用實際 vendored 檔案集合做了等價重現,採信。修:照既有 `_need_src` 慣例拆成來源專用測試,另加一支模擬消費專案的測試。
- 正確性三條都是「行為對、測試沒守到」;架構對齊一條是 doctor 那行靠訊息字樣判斷。同輪有 major,全部折。

## 機械重現(在審的那一版 1ca70d4f 上;方法:折入後的新測試格,把修法還原就翻紅,先證明現場成立)

| 發現 | 做法 | 結果 |
|---|---|---|
| 外家否決-F1 | 改前的測試檔放進模擬消費專案跑 / 拿掉 `_need_src` | HIT:讀檔失敗紅;`t_negation_hint_consumer_sim` 翻紅 |
| 正確性-F1 | 修飾語視窗改 8 字 | HIT:原說明宣稱會紅、實際照綠(說明與實作紀錄改成實際會紅的寫法) |
| 正確性-F2 | 四個分支各改壞一處 | HIT:改前照綠;加例句後各自只紅那一句 |
| 正確性-F3 | 設定寫錯的提醒改成每次都印 | HIT:`t_note_shape_negation_never_blocks` ⑬ 翻紅 |
| 架構對齊-F1 | doctor 那行改回比對文字 | HIT:`t_note_shape_negation_doctor_line` ⓪ 翻紅 |

## 處置

- 5 條全折(folded),accepted 空、refuted 空。修正在 0984c966。
