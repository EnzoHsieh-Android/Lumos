severity: minor

# 邊界-sonnet 第 2 輪報告(邊界與測試品質)

我在修後版 02fd3bdf5 的複本上做了 11 個具體改壞(包含卡線值),每次改前清過 `__pycache__`,跑對應的 `-k` 測試。10 個讓測試翻紅,1 個沒紅(見 finding 1)。沒有跑修前版(before)的對照,所以所有歸因都是未判定。分支的 `.lumos/lint-waivers`、governance 等檔我都沒碰。

## 已驗主張

引句:「if b_to and cap < full:   # 被剩下時限截斷:不算這支的基準」
- 把這行改成 `if False:`,`t_choice_kill_merge_budget_reestimate` 紅。bravo 被記成 abort,斷言「六列都 survived」失敗。
- 把上限改成 `cap = full`,同一支測試紅。

引句:「if measured and mg.remaining() < sum(measured) / len(measured) * left * _CHOICE_MERGE_BUDGET_K:」
- 整段重估拿掉(改成 `if False and ...`),同一支測試紅。合併模式交出的列是空的,跟 `--no-merge` 不一致。

引句:「if merge is not None and merge.interrupted:   # 訊號在登記之前就來過:回呼沒看到這支,當場收掉」
- 拿掉這道檢查,`t_choice_kill_merge_signal_race` 兩案都紅。合併基準與合併快篩各多等 60 秒,出現 end。

引句:「return min(max(m_el * 5, floor), max(remaining, 1.0))」
- 乘數 5 改成 1:`screen_cap` 的 3 條斷言紅,端到端那案(快篩 4 秒應通過、judged merged)也紅。
- 拿掉 `min(..., max(remaining, 1.0))`:剩 30、剩負數兩案紅。

引句:「or not _kill_merge_in_lane(c, chunk, lane):」
- `_kill_merge_in_lane` 改成永遠回 True,`t_choice_kill_merge_no_lane_chunk` 兩條斷言都紅。壞法 2 多一次合併呼叫,也進了存活集合。

引句:「if max(sizes) > _CHOICE_MERGE_FILE_MAX or sum(sizes) > _CHOICE_MERGE_TOTAL_MAX:」
- 單檔上限的 `>` 改成 `>=`:「單檔剛好等於上限」那案紅。

引句:「if mg.remaining() < len(uniq) * _CHOICE_MERGE_UNIT_SECS * _CHOICE_MERGE_BUDGET_K:」
- `<` 改成 `<=`:「剩 45.0 秒、門檻 45」那案紅。

引句:「c.hk.between()」
- 拿掉量單支基準之前的這道停止旗標檢查,`t_choice_kill_merge_edges` 的「量基準中途總時限到」案紅。第三支基準照跑了,四支都量了。

## Finding

1. 量基準中途重估的 `<` 邊界沒有測試釘住
severity: minor
blocking: 否
引句:「if measured and mg.remaining() < sum(measured) / len(measured) * left * _CHOICE_MERGE_BUDGET_K:」
file: `scripts/lumos:28984`(修後版,`_kill_merge_singles` 內)
失敗場景:剩下時限剛好等於「還沒量的支數 × 已量平均耗時 × 1.5」時,規格條款寫的是「超過才不量」,實作也是 `<`。我把 `<` 改成 `<=`,`-k choice_kill_merge_budget` 仍是 3 passed、0 failed。這個改壞不會被抓到,後果是在邊界值上多一次「不合併」,屬於覆蓋面不完整。同一輪對開跑那道門的 `<`(45.0 與 44.99)已經補了卡線案,重估這道漏了。
重現:改壞後跑 `python3.14 scripts/test_lumos.py -k choice_kill_merge_budget`,結果是 3 passed、0 failed。
歸因:未判定。重估是修補新增的行為,這個測試缺口隨修補一起出現,但我沒跑修前版。

## 三問

1. 原問題的修復效果:只有修後版的行為證據,沒跑修前版。上面兩個變異證明「時限不夠量齊時交出的列等於 `--no-merge` 的列、被截斷的基準不記 abort、重量一次」是測試真正守住的行為。重估本身(M1)與截斷不寫基準(M2)各自被不同的斷言抓到。
2. 修補處的正常、錯誤與相鄰路徑:
   - 訊號落在看旗標之後、登記之前的空窗,基準與快篩兩處都被測試釘住。
   - 快篩上限的三種輸入(正常、剩餘時限小於下限、負數)都被測試釘住。
   - 單檔與合計大小的卡線被釘住(合計條件的拿掉我沒單獨試,只改了單檔的 `>=`)。
   - rc 127 與 128 的分界我沒單獨改壞,因此未驗。
   - 未驗範圍:合併基準自身的上限公式、`_kill_merge_restore` 還原失敗的路徑、第二個訊號強制結束。
3. 新發現的同一案例在修前、修後各自的結果:finding 1 只跑了修後版,修前版不能比較,歸因未判定。

我沒有評估真實 Gradle 與假 Gradle 的落差。假 Gradle 只模擬 `__base_sleep__` 與 `__msleep__` 的耗時以及 `big`、`hang` 等模式。唯一偏離真實的地方是 `t_choice_kill_merge_budget_reestimate` 要跑約 64 秒,測試腳本自己標了「餘裕不足 3 倍」(上限 180 秒)。

## 清理

before 我沒建。after 的 worktree 已用 `git -C /Users/enzo/harness/lumos-choice-speed worktree remove --force` 移除,臨時目錄 `/tmp/lumos-seat-work/code-選擇點變異加速/邊界-sonnet` 也已刪除。派工詞指向的 `.warming` 鎖檔不存在,我沒處理。

總結:最高嚴重度 minor
