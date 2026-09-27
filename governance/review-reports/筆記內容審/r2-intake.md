# r2 收貨紀錄(筆記內容審)

凍結材料:r2-snapshot.md(r1 折入後整份)、r2-delta.patch。6 席全新(正確性 opus;邊界、接手、併發、架構對齊 sonnet;外家否決 Codex,從 clone 目錄啟動);收齊前沒動被審材料。

## 收貨三道

- report-normalize:6 份皆已正規化。
- quote-check:4 份首交即全錨定;邊界席 1 句(用了省略號又包「」)、併發席 2 句(一句其實出自程式碼)對不上,請該席自己改(只改那幾行,程式碼那句改成 file: 佐證),重收後 6 份全錨定。
- refcheck:每份各 1 個 missing,都是還沒建立的判定檔資料夾。

## 編排者重現

| 發現 | 重現 | 結果 |
|---|---|---|
| r2h-F1 簿記豁免常數有四個消費者 | 讀碼:`_BOOKKEEPING_DIRS` 定義處註解「三個消費者共用」,另有 `_codeloop_record_valid` 使用 | HIT(讀碼確認) |
| r2h-F2 / r2g-F6 `code-loop pass` 沒有範圍輸入 | 讀碼:pass/skip 子命令只有 --note 與 --repo | HIT(讀碼確認) |
| r2a-F7 `_write_lf` 暫存檔留在同資料夾 | 讀碼:暫存檔名 `<檔名>.<pid>-<亂數>.tmp-wlf`,與目標同資料夾 | HIT(讀碼確認) |
| r2b-F5 全新 clone 沒有 FETCH_HEAD | 席位附的可重跑指令;另讀碼確認全檔沒有量 fetch 時間的函式 | HIT |
| r2g-F3 Codex 判定者模型沒定義 | 讀碼:`_CODEX_SEAT_MODEL` 是既有常數,計劃原稿沒指它 | HIT(讀碼確認) |
| 其餘條目 | 設計層論證,附 file:line、引句全錨定 | 採信 |

## 處置

39 條全折(輪內有 blocker,不得放行);refuted 無。Enzo 2026-09-28 裁「收窄成防疏忽」:防作者自己作弊那幾層整個拿掉,對應的發現以「機制不存在」處置,算折;逐條去向見計劃〈審計修正紀錄〉r2 與 r2-mirror.md。

鏡像核對:39 條未處理 0、部分 1、相反 0;新矛盾 2 處,已改。見 r2-mirror.md。
