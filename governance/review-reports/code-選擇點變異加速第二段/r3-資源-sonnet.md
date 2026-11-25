severity: clean

# 資源席 r3 報告

**hook 固定席段:有附上。** 共 9 個節點有列內容,其餘只列名。

## 修補差異的實際內容
r3-repair.patch 對 `scripts/lumos` 只有三處行為相關的改動:
- 新增常數 `_CHOICE_MERGE_TRIPPED = "斷路器"`,`_kill_merge_breaker` 與 `_choice_kill_report` 的 `merge_off` 過濾改用它。
- 在 `_kill_merge_iter` 的 `except _KillHalt` 裡,原因由固定的「中斷」改成 `"中斷" if mg.interrupted else "時限到"`。
- `cmd_guard_kill` 的 docstring 只多了 `ran_solo` 一詞。

其餘是筆記、計劃和測試。這份修補沒有新增任何子程序、迴圈、讀檔或時間預算算式,所以三個資源問題都只能對舊碼路徑查證。

## 三問

**①子程序有沒有沒收乾淨(中斷與時限到兩條停法)**
- 結論:沒有新增的殘留。
- 量基準途中被收掉,是在 `_kill_merge_base` 裡兩種情況:`c.hk.between()` 因 `should_stop` 丟 `_KillHalt`,或 `_kill_run` 回來後見 `mg.interrupted` 才丟 `_KillHalt`。
- 兩處都是同步 `_kill_run` 結束之後才丟,丟出時沒有子程序在跑。
- 合併呼叫被訊號中斷時,`on_signal` 會用 `_kill_proc_group` 收掉合併程序群組。這段修補前後都沒動。
- 時限到那條不需要收程序:時限是在每次 `between()` 或快篩前的 `should_stop` 檢查才發現,那時前一支已跑完。
- 訊號與時限同時成立時,`mg.interrupted` 為真,標籤記「中斷」。這只影響標籤,不影響收程序。
- 判定:不影響子程序收尾。

**②時間預算會不會誤擋或誤放**
- 結論:修補沒碰預算算式。
- `merge_off` 多記一個「時限到」值,不改任何門檻。
- 新測試用 `__base_sleep__: 2`、3 秒後停,只多約 4 秒測試時間,沒有不穩定的卡線,也沒有變慢機器上必紅的條件。

**③大輸入讀進記憶體或二次方工作**
- 結論:沒有。
- `_CHOICE_MERGE_TRIPPED` 是字串常數。
- `merge_off` 與 `merge_unclean` 的字典鍵是固定種類原因,鍵數有上限。
- 新增的 `ran_solo` 是每列一個布林值。

## 已驗主張(皆為讀碼比對,未實跑)

| claim | input | expected | case_source | before | after | 歸因 |
|---|---|---|---|---|---|---|
| 量基準途中總時限到,記「時限到」,不印,`interrupted` 為假 | 單支基準 2 秒,3 秒後 `should_stop` 為真 | `plats` 為 `{kotlin-junit: (False, 時限到)}` | `t_choice_kill_merge_off_reasons` 新增案 | 固定記「中斷」(`git show 95977c10` 的 `_kill_merge_iter`) | 依 `mg.interrupted` 分「中斷」與「時限到」 | 有證據的修復,以讀碼比對,未重跑測試 |
| 訊號中斷仍記「中斷」 | 量基準途中收到第一個訊號,`on_signal` 設 `interrupted` 為真 | 記「中斷」 | 既有 `t_choice_kill_merge_interrupt` | 記「中斷」 | 記「中斷」 | 未判定:這支測試沒有實跑 |
| 斷路器那筆不進 `merge_off` | 平台原因為「斷路器」 | `merge_off` 不含它 | 常數替換,字串值不變 | 字面「斷路器」 | `_CHOICE_MERGE_TRIPPED`,字面相同 | 無行為差異 |

## 圖譜固定席判定
- **guard-kill 的 rc 優先序合約**:不影響。修補沒動 rc 計算,只改 `plats` 的標籤。
- **guard-kill 的 `--json` 純度合約**:不影響。`ran_solo` 在 `_ran_solo` 輸出過濾清單裡(file: `scripts/lumos:28619`),新增的 `print` 只走標準錯誤。
- **其他固定席節點**(lumos-cli-read、bound-tests-gate、測試假綠形態、design-loop、lifecycle 等):不影響。修補只動 choice-kill 的標籤與筆記字句,不碰這些節點宣稱的行為。

## 未驗範圍
- 沒實跑 `-k choice_kill_merge` 子集,也沒做修前修後的實跑對照。
- 這個 repo 的同時寫入不在審查範圍內。

總結:沒有發現,最高嚴重度 clean,blocking 0 條。
