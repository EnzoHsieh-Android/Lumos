---
type: issue
status: open
created: 2026-10-24
updated: 2026-10-24
aliases: []
about_code:
  - scripts/templates/android-receipt-rerun.sh
tags:
  - type/issue
  - status/open
  - priority/P2
  - scope/stack-knowledge
summary: |-
  FLAG:TECHNICAL
  PITFALL:使用者環境設了 PYTHONIOENCODING=ascii 時,比對完全相符的收據重跑會崩潰回 1 [出處:2026-10-24 代碼審 code-android-ui-kind r4 三席各自重現] [根因:UTF-8 模式管不到 PYTHONIOENCODING,r3 拿掉 stdout 重設後沒有東西壓過它] [修法:env 那行加 PYTHONIOENCODING=utf-8] [repro:PYTHONIOENCODING=ascii TP=印中文鍵的假工具 sh rerun.sh]
  PITFALL:收據寫歪(expect 缺等號、標頭多一個沒等號的詞、缺 manifest、UTF-16 檔)時 Traceback 回 1,跟比對不符同碼,不是文件寫的 2 [出處:2026-10-24 代碼審 code-android-ui-kind r4 邊界與通才席] [根因:解析收據的幾行沒包錯誤處理,修前就如此] [repro:queries.sql 寫 expect=甲 後跑 rerun.sh]
  REVISIT:2026-11-07 照正文〈什麼條件算修好〉開一個小修補把各項收掉,收完把這篇結案
---
# Android收據重跑第四輪放行的小缺口

2026-10-24 代碼審 code-android-ui-kind 第四輪(三輪跑滿後加開)七席都只報小問題,十五條全部附理由放行、沒有折進這次推送;這篇集中記下後續該收的。席報告與重現紀錄在 `governance/review-reports/code-android-ui-kind/` 的 r4 檔。家節點是 [[Systems/macrobenchmark-adapter]],寫法分流的規則在 [[Projects/Android介面寫法分流_計劃]]。

## 症狀

- 使用者環境設了 `PYTHONIOENCODING=ascii`(或 latin-1),比對完全相符的收據重跑印結果時 `UnicodeEncodeError`、回 1;修前那版回 0。
- 收據寫歪(expect 缺等號、標頭多一個沒等號的詞、缺 manifest、UTF-16 的檔)時 Traceback 回 1,呼叫端分不出「收據寫錯」和「量測不符」。
- 回傳碼 2 這一輪多了「分析工具執行不了」的意思,但 skill 主檔、腳本檔頭、家節點第一段、逐層診斷計劃的 S10 還寫「2 = 收據本身寫錯」。
- 計劃與家節點把崩潰根因寫成「LC_ALL=C」;實測 Python 3.7 以上遇到 C 語系會自動開 UTF-8 模式,光設 LC_ALL=C 不會崩,要 UTF-8 模式被關掉(`PYTHONUTF8=0`)或語系編碼不是 UTF-8 才會。測試本身是對的(它強制關掉 UTF-8 模式),錯的是說明。
- 測試抓不到拿掉 `errors='replace'`:分析工具輸出含非法 UTF-8 時會 Traceback。
- `python3 -` 讀 stdin 時模組搜尋路徑第一項是目前目錄,在放了 `json.py` 的目錄裡執行會先載入它(縱深防禦,不是這輪引入的)。
- 分析工具沒有逾時;腳本被 SIGTERM 殺掉時暫存查詢檔與子程序會留下。
- L1 分流用的「跨幀四類總和」是 AI 手動加總,重跑腳本只釘單一幀,驗不到分流依據。
- 架構對齊席另記:UTF-8 模式是專案裡第二種編碼做法、reference 寫的 3.7 下限跟專案的 3.14 不一致、授權守衛依副檔名分兩套註解符號。

## 根因

- 前三項:r3 為了 Linux 的編碼問題改成「整支腳本開 UTF-8 模式」,拿掉了 stdout 重設;UTF-8 模式管不到 `PYTHONIOENCODING`,而新增的回傳碼語意只改了 reference 與家節點第二段。
- 收據解析與讀檔的幾行從一開始就沒包錯誤處理;逾時、SIGTERM、`-I` 也是原本就沒做。
- 四類總和:查詢範本輸出是每幀一列,沒有一條查詢直接輸出跨幀總和。

## 現在怎麼繞

- 跑重跑腳本前不要設 `PYTHONIOENCODING`;回 1 先看 stderr 有沒有 Traceback,有就是收據寫錯或環境問題,不是量測不符。
- 回 2 照 stderr 印的原因處理(「執行不了分析工具」那則會提示用 `TP=` 指定)。
- 在收據目錄或自己的專案目錄執行,不要在放了外來 .py 檔的目錄執行。

## 什麼條件算修好

- env 那行加 `PYTHONIOENCODING=utf-8`,測試多一組 `PYTHONIOENCODING=ascii` 的環境,拿掉這個變數會紅。
- 收據解析與讀檔失敗一律回 2 並說原因,測試各放一個寫歪案例(缺等號、多等號、缺 manifest、UTF-16)。
- 回傳碼 2 的意思在 skill 主檔、腳本檔頭、家節點、逐層診斷計劃四處寫成同一句。
- 計劃與家節點的根因改成「UTF-8 模式被關掉或語系編碼不是 UTF-8」,測試註解同步。
- 測試多一支輸出含 `\xff` 的假分析工具,拿掉 `errors='replace'` 會紅。
- 啟動改 `python3 -I -`;逾時與 SIGTERM 是否收、四類總和要不要多一條彙總查詢,做那次修補時一起判。
