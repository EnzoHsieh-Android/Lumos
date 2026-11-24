severity: clean

資源席(資源-sonnet)本輪零 finding。r3-repair.patch 只動文件、錨點基準檔與測試檔,沒有改產品程式碼。資源面能查的只有新增或改動的測試,這部分沒有問題。

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/baf3be87…json.warming` 檢查時不存在,所以沒有可刪或不可刪的問題。

## 已驗主張

**1. 新測試 `t_choice_kill_merge_budget_edge` 不留殘局。**
引句:「m._kill_run = orig」
- 它換掉 `_kill_run` 的動作包在 try/finally 裡,例外時也會還原。
- 它不開子程序、不建暫存目錄,耗時固定(單支 2 秒由假的 `_kill_run` 回傳)。
- 修後:`python3.14 scripts/test_lumos.py -k choice_kill_merge_budget_edge` 通過 2 項,實測 4.6 秒(上限 180 秒,餘裕 39 倍)。
- 修前版本沒有這支測試,不適用兩版比較。

**2. `t_choice_kill_merge_screen_cap` 新增的端到端段落會收乾淨。**
引句:「m._CHOICE_MERGE_UNIT_SECS = saved」
- 模組屬性在 finally 還原,暫存目錄由 `_ck_cleanup(root, fake, tmp)` 清。
- 快篩睡 6 秒,被剩下時限收掉,沒有拖成整段,`[one, "1", "end"] not in rows` 驗到了這點。
- 我跑完後 `/var/folders/tc/xmllmxtn4q5704lsy80wc1kw0000gn/T/` 底下沒有 `gctl-ckm-*` 殘留。`gctl-run-*` 等目錄是別人的測試在用,我沒動。
- 修後:`-k choice_kill_merge_screen_cap` 通過 6 項,實測 29.4 秒,餘裕 6 倍。
- 修前版本沒有這段,不適用兩版比較。

**3. 重估測試換回原版後,耗時餘裕仍在上限內。**
引句:「重估測試 t_choice_kill_merge_budget_reestimate 整支換回加速前原版」
- 機器負載 8.7 時,修後 59.3 秒,修前 63.7 秒,各跑一次,上限 180 秒,餘裕約 3 倍。
- 測試輸出對修前那次標了「餘裕不足 3 倍」的警告,不屬於不穩定。兩版都通過 3 項,所以修補沒讓耗時變差。
- 它用的是真睡眠加絕對時限,餘裕比其他兩支窄,但在這台忙碌機器上沒有紅過。

**4. 子程序殘留。** 跑完後 `ps` 只看到別的席(正確性-sonnet)的 gradlew 假程序,我這邊沒有殘留。

## 三問

- **修復效果:** 新增的測試通過。我沒有造出會讓這些測試翻紅的壞改法,所以「測試抓得住」這點未判定。
- **相鄰路徑:** 這兩支測試的收尾路徑(例外、還原、清暫存)在讀碼與實跑上都成立。
- **同一案例修前修後:** 這輪只有測試檔和文件的改動,沒有可比的產品行為案例,未判定。

## 未驗範圍

- 沒有在更高負載下重跑 screen_cap 的 3 秒總時限案例。它的餘裕是合併基準加假 Gradle 啟動要在約 1 秒內完成,否則快篩不開跑、`"start"` 會缺。這次負載 8.7 下沒紅,但沒壓到極限,只能說未見失敗。
- `t_choice_kill_merge_screen_cap` 新段落裡,`_ckm_repo(...)` 出現在 `try` 之前。它若丟例外,`tmp` 會漏清。這是測試輔助函式先例的寫法,沒有具體觸發場景,所以不報。

收工:`before`、`after` 兩個 worktree 與我建的暫存目錄都已移除。

總結:最高嚴重度 clean
