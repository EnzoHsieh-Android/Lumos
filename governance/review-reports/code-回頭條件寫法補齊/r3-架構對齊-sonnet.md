severity: clean

# 第 3 輪 架構對齊審查(只看第 2 輪修正:半形引號整類不認)

## 三問

1. 分層與依賴方向:沒有新依賴,也沒有跨層直呼。`_revisit_quote_states` 仍只被 `_revisit_misplaced` 一處呼叫,引號表 `_REVISIT_QUOTES` 仍是唯一來源。
   對照:scripts/lumos 的 `_revisit_misplaced`(約 31790 行)與 `_revisit_quote_states`(約 31796 行)。
2. 命名與錯誤處理:這份 diff 沒有新增或改名任何函式與常數。刪掉 `straight` 與 `last['"']` 後,迴圈形狀和原本一致。
   錯誤訊息(`_REVISIT_MISPLACED_FIX`)、skill 說明 `03-寫回圖譜.md`、計劃〈做法〉1.2 都同步改成「全形引號「」」,三處用字一致。
   我另外 grep 了 scripts、skills、README、docs 裡其他「引號包起來」的說法,沒有漏改的 REVISIT 相關處。
   scripts/lumos 約 22462 行寫「引號用半形 "…"」,但那是代碼審引句抽取(`_quote_rows`)的錯誤訊息,與本案無關。
3. 第二種做法:沒有新增。引號判定只剩一套,而且比上一版少一個分支。

## 實測

- 在 rw 工作樹跑 `python3.14 scripts/test_lumos.py -k revisit_misplaced`,結果 24 passed、0 failed。
- 手動餵 `_revisit_misplaced` 三個輸入:
  - `「a REVISIT:2026-10-05 x」 後 REVISIT:2026-10-06 y` 只報第二處。
  - `“a REVISIT:2026-10-05 x” 與 ”REVISIT:2026-10-05 y“` 只報第二處,反向引號 `”…“` 不被當成開引號。
  - `「a『b』 REVISIT:2026-10-05 x」` 巢狀不報。
- 半形整類不認這個修法本身是對的。`"` 分不出開與收,拿掉後落單的 `5"` 不會再把句中 REVISIT 藏起來。
- 代價是半形引號裡的範例句現在會被擋。這個取捨在改法字串、skill 說明、計劃三處都明講了「改用行內程式碼包起來」。

## 沒問題的項目

- 測試 `t_revisit_misplaced_ignores_mentions` 與 `t_revisit_misplaced_review_r1` 同步改成全形案例,並新增 ③b 釘住「半形整類不認」。
  ③b 同時覆蓋 r2 兩席提出的組合(落單 `5"` 後接一對 `"…"`)和原本被算成範例的 `"REVISIT:…"`。
- 純風格的差異不列。

## 固定席節點(lens.txt 參考)

- bound-tests-gate 等固定席的 INVARIANT 綁定與這段改動無牽連,沒有看到衝突。

severity 總結:clean(無 finding)
