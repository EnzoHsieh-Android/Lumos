---
type: issue
status: done
created: 2026-09-29
updated: 2026-09-29
aliases:
  - 3.9 推送被擋
  - 系統 Python 跑測試
about_code:
  - scripts/test_lumos.py
related:
  - "[[Systems/測試假綠形態]]"
  - "[[Projects/代碼審資料狀態鏡頭_計劃]]"
tags:
  - type/issue
  - status/done
  - scope/loop-engineering
summary: |-
  FLAG:TECHNICAL
  PITFALL:[2026-09-29 推送代碼審資料狀態鏡頭,出處見 [[Projects/代碼審資料狀態鏡頭_計劃]]]路徑上先找到蘋果內建 3.9 的環境跑推送前全套,修掉三處 3.10+ 寫法之後仍剩兩件:①`t_handoff_hook_import_is_pure` 紅——蘋果內建 3.9 載入模組時自己往 Library/Caches/com.apple.python 寫編譯暫存,測試分不出是誰在寫;②`t_escape_review_r3_fixes` 塞的二十萬層巢狀行讓 3.9 的 Python 直接當掉(SIGSEGV,macOS 跳當機報告),測試本身判綠。重現:`PATH=/usr/bin:$PATH python3 scripts/test_lumos.py -k handoff_hook_import_is_pure`
  DECISION:[2026-09-29 Enzo 選「改用新版 Python 跑推送前檢查」]那次推送讓 Homebrew 3.14 排在路徑前面照跑全套(7521 條斷言全綠),3.9 的兩件另開這篇,不為了推送硬修
---
# 蘋果內建 Python 3.9 跑全套仍紅

白話:專案宣告支援 Python 3.9,但用蘋果內建的 3.9 跑推送前的全套檢查,還有兩支測試過不去或會讓 Python 當掉。平常推送沒撞到,是因為路徑上先找到的是 Homebrew 的新版 Python。

## 經過

- 2026-09-29 推送代碼審資料狀態鏡頭時,這個會談的路徑先找到蘋果內建 3.9,推送前的閘兩次被擋。
- 第一次:測試總檔整支在 3.9 下解析不了、自主迴圈測試用了 3.11 的寫法、讀設定檔的測試用了 3.11 的解析模組。三處已修(同一次推送的修正提交),坑記在 [[Systems/測試假綠形態]]。
- 第二次:修好之後全套第一次真的在 3.9 上跑起來,冒出下面兩件。
- 第三次:照人裁改讓 Homebrew 3.14 排前面推,全綠推上去。

## 還沒處理的兩件

1. **載入 hook 不准碰檔案系統那支測試紅。** 紅的內容是一個開檔動作,路徑落在假家目錄底下的 `Library/Caches/com.apple.python/…`。推測是蘋果內建 3.9 會把編譯暫存寫到使用者快取目錄(蘋果自己的設定),不是 hook 自己在寫;★這個推測沒驗★。
2. **二十萬層巢狀那支測試讓 3.9 當掉。** 11:43–11:52 之間 macOS 記了 6 份 Python 當機報告,堆疊都是編譯字串時遞迴二十萬層撞到堆疊上限。其中 5 份的上層是 shell 或已結束的程序,1 份的上層是 Codex——★不是每一份都確定出自這次推送★;哪一段程式把那行帶進 Python 編譯器、為什麼 3.12 以上不會當,都沒查。

## 為什麼沒當場修

每修一處都要重核可指紋、重跑代碼審、再跑一次約 10 分鐘的全套;修掉三處之後又冒出兩處,看不出還有多少。人裁先推、這兩件另外處理。

## 回頭條件

已結案(2026-09-29):Enzo 裁定工具最低 Python 改成 3.14([[Projects/最低Python版本改3.14_計劃]]),這兩件 3.9 專屬的問題不再需要修。結案依據是「3.14 跑過全套綠」,不是「原因已查清」——兩件的原因本篇自己標了沒驗,現在也沒查。
