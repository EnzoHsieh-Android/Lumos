severity: minor

hook 有附上固定席段(guard-kill、lumos-cli-read、pitfalls-code-loop、loop-convergence-recording、bound-tests-gate、測試假綠形態、design-loop、lumos-cli-lifecycle 等)。

## Finding 1

severity: minor
blocking: 否。只影響 `merge_off` 帳上的原因字樣和印出的那一行字,不改判定,所以是 minor。

位置:file: `scripts/lumos:28995`、file: `scripts/lumos:28999`(`_kill_merge_base`)。
引句:「收到訊號(mg.interrupted)記「中斷」,否則是總時限到、記「時限到」;兩者都不印(接著就停;代碼審 code-選擇點變異加速第二段 r2 e1)。」

失敗場景:r2 e1 只在 `except _KillHalt` 那一處把「中斷」和「時限到」分開。`_kill_merge_base` 裡還有兩個 `return`,走到時不會經過這個 except,也不看訊號或總時限。
- 「基準量不齊」(`_kill_merge_singles` 回 False)
- 「合併道不足 2 支」(`len(lane) < 2`)

訊號或總時限在最後一支單支基準跑的時候到了,而這個平台組當時正好走這兩條路,就會發生:
- 帳上記的是「合併道不足 2 支」或「基準量不齊」,不是「中斷」或「時限到」。
- 標準錯誤印「這次不合併(…),照逐支跑」。
- 隨後 `cmd_guard_kill` 的逐支迴圈在 `hk.between()` 丟 `_KillHalt`,整次停下,「照逐支跑」不成立。

重現:在修後版本直接呼叫 `_kill_merge_base`,`mg.interrupted=True`、單支基準全紅,輸出如下。
`None {'app': (False, '合併道不足 2 支')} '⚠ app:這次不合併(合併道不足 2 支),照逐支跑\n'`

總時限到的版本也一樣:`should_stop` 為真而 `mg.interrupted` 為假,得到同樣結果。

歸因:有證據的原有漏查。修前 `_kill_merge_iter` 同樣只在 except 那處記「中斷」,這兩個 return 兩版都不看停止旗標。修前的 `95977c10` 讀碼推得,沒另外實跑,屬讀碼判定。

## 逐項核對

| claim | input | expected | case_source | before | after | 歸因 |
|---|---|---|---|---|---|---|
| 量基準途中總時限到,記「時限到」、不印、`interrupted` 假 | 守 4 支、單支基準 2 秒、3 秒後 `should_stop` 為真 | `plats == {kotlin-junit: (False, 時限到)}`,`mg.interrupted` 假,不印「這次不合併」 | `t_choice_kill_merge_off_reasons` 新增兩條 | 無條件記「中斷」,讀碼推得 | 17 passed 0 failed(實跑) | 修復成立 |
| 訊號到了仍記「中斷」(preserve) | 合併基準途中訊號 | `merge_off == {kotlin-junit: 中斷}` | `t_choice_kill_merge_interrupt` | 記「中斷」 | 8 passed(實跑) | 正常路徑成立 |
| 兩分支守得住(變異) | 把 `"中斷" if mg.interrupted else "時限到"` 改成永遠「時限到」 | `t_choice_kill_merge_interrupt` 轉紅 | 變異實跑 | — | 紅,值為 `merge_off: {'kotlin-junit': '時限到'}` | 守得住;「一律中斷」那邊靠新測試的「`mg.interrupted` 為假」那條擋,讀碼推得,沒另外變異。 |
| 斷路器常數不被撞名 | `_CHOICE_MERGE_TRIPPED = "斷路器"` 對上其他原因字串 | 其他原因不等於它 | 讀碼 | — | 不撞:其他原因是固定字串,或帶「合併基準:」前綴(`unclean` 的鍵是 classify 原字串,不進 `plats`) | 成立 |
| 舊帳記著「中斷」被新程式讀 | `merge_off` 舊值 | 不因值而出錯 | 讀碼 `scripts/lumos:18471`、`scripts/lumos:18565` | — | 只做 dict 型別登記和 `or {}`,不讀值,舊值照讀 | 成立 |
| S7 新列 | 單支 2 秒、守 3 支、剩 5.99、已花 33 | 約需 9、剩 5、`--max-seconds 200`(照未量的 2 支估會是 6 秒、100) | `t_choice_kill_merge_budget_hint` | 無對應案 | 讀碼核算 (33+9+60)=102 進位到 200,`int(5.99)=5`,與測試斷言一致;沒另外實跑該測試 | 成立 |
| S10 新列 | 十種原因、時限到 | 測試輸出逐項 ✓ | `t_choice_kill_merge_off_reasons` | — | 實跑全 ✓ | 成立 |

## 要點

- **訊號與總時限同時到:** `should_stop` 看 `st.got` 或時限,訊號處理器先記 `st.got` 再同步呼叫 `on_signal`,兩者之間沒有空窗,同時到記「中斷」是對的。
- **訊號在第一支前或最後一支後:** 第一支前由迴圈開頭的 `between()` 丟 `_KillHalt`,最後一支後由合併指令組出前的 `between()` 丟 `_KillHalt`,都經過修補點。唯一例外是 Finding 1 的兩個 return。
- **總時限剛好等於量完的時刻:** 每支前的 `between()` 先於重估,所以記「時限到」,不會變成「基準量不齊」。
- **新增的測試斷言有一條接近空轉:** 「run 的 `interrupted` 是假」。`kr` 是測試自己用 `SimpleNamespace(interrupted=False)` 手建的,所以那條斷言與修補無關。真實的 `_ChoiceKillRun` 路徑(`self.interrupted = bool(st.got)`)靠讀碼推得為假。這條沒有具體改壞的場景,所以不單獨列為 finding。
- **兩條 ★INVARIANT★(guard-kill):** rc 優先序和 `--json` 純度都不受影響。修補只改記帳字串、提示文字和常數抽取。`_kill_merge_off` 只寫標準錯誤,`cmd_guard_kill` 的差異只動 docstring。
- **其他固定席:**
  - lumos-cli-read(search 過濾)、lumos-cli-lifecycle(re-inject)、design-loop(處置閘):這份 diff 不碰那些程式。
  - bound-tests-gate:差異改的 `t_choice_kill_merge_off_reasons` 仍是 guard-kill 筆記綁的測試,方法名沒變。
  - 測試假綠形態:新增案例有前置斷言(`mg.plats` 與 `interrupted` 同時檢查),上面的變異實跑也確認它會紅。

未驗範圍:多平台中途中斷、`merge_off` 對舊帳消費者的下游行為(沒有讀值的程式)、全套測試。

總結:最高嚴重度 minor,blocking 0 條。
