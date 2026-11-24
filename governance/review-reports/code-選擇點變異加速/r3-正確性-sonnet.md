severity: minor

這輪正確性審的結論是沒有 major,只有一條 minor。快篩上限的端到端案例和重估卡線測試,都走到了被宣稱守住的那一行,改壞呼叫端或比較式都會翻紅。

## 發現

1. 重估卡線測試分辨不出「平均」被改成「總和」
severity: minor
blocking: 否
引句:「翻紅釘:< 改 <= → 剩 6.0 那案收手而紅;拿掉重估 → 剩 5.99 那案量齊而紅。」
file: `scripts/lumos:28972`(`_kill_merge_singles` 裡的 `sum(measured) / len(measured) * left`)
- 失敗場景:測試固定每支耗時 2.0 秒、三支。只有 i=1 那一步會收手,那時 `measured` 只有一個值,平均、總和、最後一筆三種算法結果相同。
- i=2 那步在剩 6.0 的案例裡是 6.0 < 6.0,不會收手,所以也分不出差別。
- 重現:我把 `sum(measured) / len(measured) * left` 改成 `sum(measured) * left`。`-k t_choice_kill_merge_budget` 仍是 8 passed,`-k t_choice_kill_merge_edges` 是 7 passed。
- 影響:實測耗時有 2 筆以上時,總和會高估剩餘需要的時間,太早收手、少合併。這是保守方向,不會放行錯誤結果。
- 歸因:未判定。這是新測試沒覆蓋到的面向,沒有修前對照,因為修前沒有這支測試。

## 已驗主張

引句:「呼叫端不帶剩下時限 → 上限 30,快篩睡滿 6 秒寫出 end 而紅。」
- 主張:快篩上限的端到端案例真的守住呼叫端要傳剩下時限。
- 做法:把 `_kill_merge_screen` 裡的 `_choice_merge_screen_cap(m_el, c.floor, mg.remaining())` 改成 `max(m_el * 5, c.floor)`。
- 結果:`-k t_choice_kill_merge_screen_cap` 變成 5 passed、1 failed。失敗的是 `r2 通才 #1`,log 顯示快篩的 `1 start` 和 `1 end` 都寫出了。還原後是 6 passed、0 failed。
- 穩定性:還原後我單獨跑 2 次都是 6 passed;另外 4 個程序同時跑,而且同機有別席的 4 個程序也在跑,結果全是 6 passed。因此我沒有看到固定 3 秒總時限造成的隨機紅。
- 還原:測試把 `_CHOICE_MERGE_UNIT_SECS` 在 `finally` 還原,`tmp` 用 `_ck_cleanup` 清掉。

引句:「已量 2 秒、剩兩支、剩 {rem} 秒(門檻 6)→」
- 主張:卡線測試守住 `<` 和 1.5 倍乘數這兩處,兩個案例的預期值我逐步手算過。
- 走過的路徑:剩 6.0 時,i=1 是 6.0<6.0,不收手,最後量齊 3 支。剩 5.99 時,i=1 收手,只剩 1 支在 `baselines`。
- 結論:`<` 改 `<=`、拿掉重估、乘數改 1.4 或 1.6,各自會讓其中一案翻紅。
- 還原:`_kill_run` 在 `finally` 換回原值。

我也驗了正常路徑沒被改壞。這份修補只動測試檔、計劃筆記和 guard-kill 筆記,`scripts/lumos` 在 r3-repair.patch 裡沒有改動,所以修前修後的程式行為相同。修前沒有這兩支測試,因此原問題的修復效果只能用「對修後程式做變異」的證據,沒有修前對照。

未驗的範圍:
- 只讀了 `r3-repair.patch`,沒有逐項核對 `r3-behavior-cases.json` 的選例。
- 帳本、訊號、斷路器這些路徑不在本席鏡頭內。
- 圖譜鏡頭的 `lens.txt` 沒有讀。

屬於小型測試衛生的一點,我沒有單獨列 finding:新增的端到端案例裡,`tmp = mkdtemp(...)` 在 `try` 之前,`_ckm_repo` 若丟例外,暫存目錄不會被清。

我的 worktree 已移除,臨時目錄下的檔案也已刪;目錄本身因為最後一步 `rmdir` 的指令回了非零,我沒有再確認它是否已不在。

總結:最高嚴重度 minor
