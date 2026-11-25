severity: minor

守 0、1、2 支、同名重複、剩餘時間為負或極大、單平台 `merge_off` 這幾項,我實跑 `_kill_merge_ready` 後都符合設計。多平台、中斷落點、舊帳型別和 `ran_solo` 只靠讀碼判斷。只有一條 minor,而且是原有漏查。

## Finding

severity: minor
blocking: 否。只是記帳標籤失準,不影響判定、rc 與擋放行,所以是 minor。

file: `scripts/lumos:29167` 與 `scripts/lumos:79059`

引句:「        _kill_merge_off(mg, c.plat, "中斷", quiet=True)」

- 失敗場景:`should_stop` 在總時限到時也會回真(`_ChoiceKillRun.stop`)。量單支基準途中或合併基準之前總時限用完,`hk.between()` 會丟 `_KillHalt`。
- 這時 `_kill_merge_iter` 的 `except _KillHalt` 會把 `mg.plats[平台]` 記成 `(False, "中斷")`,run 事件的 `merge_off` 就帶 `{平台: 中斷}`。
- 但這次沒有收到任何訊號,`run.interrupted` 是 False,事件看起來互相矛盾。靠 `merge_off` 判斷「是不是被人中斷」的讀者會被誤導。
- 我沒能實跑出這一條,只有讀碼。
- 歸因:有證據的原有漏查。修前版本同樣用 `mg.off[plat] = "中斷"`,計劃把「中斷」定成唯一原因,沒有區分時限到。
- 建議:加一個固定原因,例如 `時限到`,或在文件寫明「中斷」包含時限用完。

## 三問

1. 原問題的修復效果:
   - 把 `merge_off` 改由 `plats` 算出,不再另存一份字典。我檢查了 `scripts/lumos` 裡所有寫入點,只剩 `_kill_merge_off` 一處寫 `plats[平台] = (False, 原因)`,斷路器與啟用兩處也寫 `plats`,沒有第二份來源。
   - `_ran_solo` 改名後,殘留引用我只在 `scripts/lumos` 搜過一次,沒有舊 `_single` 的殘留。
   - 還沒回頭用修前版本 `a95e6509a` 對照。
2. 修補處的正常、錯誤與相鄰路徑,都用 `python3.14 -I` 載入修後 `scripts/lumos` 實跑 `_kill_merge_ready`:

| 輸入 | 預期 | 修後結果 |
|---|---|---|
| 守 0 支 | 合併道不足 2 支 | 不合併,原因 `合併道不足 2 支` |
| 守 1 支 | 合併道不足 2 支 | 同上 |
| 守 2 支但同名 | 去重後 1 支,合併道不足 2 支 | 不合併,原因 `合併道不足 2 支` |
| 2 支不同名,剩餘 1800 秒 | 合併 | 通過,`plats` 空 |
| 剩餘 -5 秒 | 時限不夠,提示「剩 0 秒」 | 印「剩 0 秒、約需 30 秒、--max-seconds 100」 |
| 剩餘剛好 30 秒 | 剩餘因耗時略少於門檻,判時限不夠 | 時限不夠,印「剩 29 秒」,符合預期 |
| 剩餘 1e9 秒 | 合併 | 通過,不印字 |

   - 守 0 支時 `_choice_merge_cmd` 用空名單組指令沒有丟例外。
   - 「已花秒數很大」靠 `x = ceil((now - t0 + est + 60) / 100) * 100` 自然拉高,沒有上限,是正確行為。
   - 測試:`-k choice_kill_merge_off_reasons` 15 案全過,`-k choice_kill_merge_budget_hint` 8 案全過。
   - rc 優先序與 `--json` 純度:`--json` 的欄位過濾表已跟著改成 `_ran_solo`,讀碼看來沒有洩漏私有欄位。
3. 新發現的案例前後對照:「時限到記成中斷」修前修後結果相同,見上方歸因。

## 其餘邊界的讀碼判斷

- 單平台時,量基準途中被中斷,`merge_off` 是 `中斷`、不印字,和計劃一致。
- 多平台且一合併一不合併時,`run.merge_off` 只含沒啟用的那個,和計劃一致。
- 斷路器跳開時 `plats[平台] = (False, "斷路器")`,`merge_off` 的過濾排除它;`_kill_merge_off` 只在合併啟用前被呼叫,不會互相覆蓋。
- 在合併基準之後被打斷,`plats` 保持 `(True, "")`,`merge_off` 不記,和計劃一致。
- 基準量不齊:`merge_need` 現在記全部支數與全部支數乘已量平均,提示的 `--max-seconds` 和重跑時從頭量基準的做法一致。
- 舊帳缺 `merge_kind`、`single_runs` 時用 `or {}`、`or 0` 讀成空字典與 0,不會出錯。型別錯的整行會被 `_GOV_FIELD_TYPES` 跳過,這是既有行為,不是這次引入。
- `on_row` 只用 `row.get("ran_solo")`,舊版 kill 列沒有這欄時算 False、不拋例外。
- `bool` 是 `int` 的子類,`single_runs: true` 也會通過型別檢查,這是原有的寬鬆,不影響判定。

## 圖譜固定席

hook 沒附節點(鏡頭計算超時),我沒有逐節點判。`Systems/guard-kill` 兩條 ★INVARIANT★ 的看法如下,理由是讀碼,沒有逐條實跑:

- `rc` 優先序:這次 diff 只改標記欄位名、`mg.plats` 記帳和一道提前的合併判斷,沒有動 `verdicts`、`rc` 計算,不影響。
- `--json` 純度:`_ran_solo` 已加進過濾表,`merge_off` 改由 `plats` 算出,不經 `--json`,不影響。

## 未驗範圍

- 沒有實跑完整的 `choice-kill` 搭配假 Gradle。
- 沒有實跑多平台合併加不合併。
- 沒有實跑中斷落在量基準第一支之前或最後一支之後。
- 沒有回頭對 `a95e6509a` 做修前對照。

## 環境注意

我跑測試後,repo 根的 `docs/.kill-log.jsonl` 顯示為已修改。可能是測試寫入,也可能是別的會談;我沒有碰它,請收貨時自行判斷。

我的探測腳本在 `/tmp/lumos-seat-work/code-選擇點變異加速第二段/邊界-sonnet/probe.py`,尚未清理;載入模組時它的暫存目錄 `gctl-probe-*` 也留在系統暫存區。

總結:最高嚴重度 minor,blocking 0 條。
