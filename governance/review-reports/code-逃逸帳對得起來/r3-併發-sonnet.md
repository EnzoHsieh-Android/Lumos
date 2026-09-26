severity: clean

已看,無:這一輪只找 blocking 級,聚焦兩件事——①驗第 2 輪「escape-stats 一次讀帳」是否讓撤回數與逃逸列來自同一份讀取;②撤回、自動記、手動記帳在寫入鎖下的時序有沒有能讓上線後出錯或違反條款的洞。兩者都逐一實跑驗證,沒有找到 blocking 級問題。

驗證過程與依據:

1. `_escape_stats()`(scripts/lumos:9900-9942)裡 `raw = _escape_raw_rows(env)` 只呼叫一次,`gone`(撤回目標集合)與 `rows`(進統計的逃逸列)都從同一個 `raw` 切出來,不是分兩次各自讀檔——結構上撤回數與逃逸列必然來自同一份讀取,第 2 輪的折入是真的。審查帳那邊 `by_loop = _escape_review_rows_by_loop(env)` 也只呼叫一次。

2. 撤回(`_escape_withdraw`)、自動記(`_auto_escape`)、手動記(`cmd_loop_escape` 記帳分支)三者寫入都包在 `_vault_write_lock(env.vault)` 裡,鎖檔位置由 `os.path.realpath(vault)` 的 sha256 算出(scripts/lumos:14199),同一個 vault 不同行程算出同一把鎖,互斥成立(不是只在同一行程內互斥)。

3. 實跑三組真實併發實驗(獨立 subprocess,不是同行程 thread 假併發),程式在 /private/tmp/…/scratchpad/escimpl/exp3-併發/conc_test.py 與 auto_worker.py,跑在複製出來的 exp3-併發/repo(唯讀,沒動正式 repo):
   - 12 個行程同時對同一迴圈手動記帳:12 個都成功、逃逸帳寫出恰好 12 行、12 個不重複 token、0 行壞損——沒有遺失寫入或半行。
   - 20 個行程混合「撤回同一個 token」「跑 escape-stats --json」「手動記帳」同時打同一本帳:撤回恰好 1 個成功、其餘 6 個全部因「已經撤回過了」擋下(rc2),沒有雙撤回、沒有例外洩漏到 stderr(逐一檢查過 Traceback 字串)、escape-stats 全程沒有噴錯。
   - 10 個行程同時呼叫 `_auto_escape` 記同一個 (迴圈,站名,sha):去重在鎖內完成,10 個裡恰好 1 個真的寫入,其餘 9 個都印「同一個 sha 已經記過,不重複」——去重不是只防同行程、也防跨行程競態。

4. `python3 scripts/test_lumos.py -k escape` 128 支全過,含 `t_escape_review_r2_fixes`(2.0s)、`t_escape_withdraw_validation`(含鎖拿不到印擋下不拋例外的釘子)。

沒找到能讓上線後出錯或違反條款的併發洞。找到但夠不上 blocking 的觀察(照要求不硬湊成 minor,只記一句留給下一輪參考):`_auto_escape`(scripts/lumos:9523)與手動記帳(scripts/lumos:9744-9760)裡,`review_ids`(用來決定 `loop_kind` 寫 design 還是 plan)是在拿到寫入鎖**之前**掃審查帳算出來的;如果掃描當下與真正落盤之間,另一個行程剛好把這個迴圈的第一筆審查紀錄寫進去,這一筆逃逸有機會被寫成 `plan` 而不是 `design`。這只影響單一欄位分類、不影響去重/撤回/計數正確性,視窗極窄(逃逸記帳與審查記帳同秒發生的機率低),沒有能讓它現形的具體壞資料後果,所以沒開成正式的 F 條目。
