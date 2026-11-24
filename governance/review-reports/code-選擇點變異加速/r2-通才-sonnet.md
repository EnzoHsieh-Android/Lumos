severity: major

鎖檔 `/Users/enzo/.cache/lumos/dispatch-lens/a58fc97a…json.warming` 不存在,沒有要處理的鎖。我也沒碰過任何鎖。

## Finding

### 1. 快篩逾時上限的修補沒有任何測試守住呼叫端接線
severity: major
blocking: 是
引句:「rc, tail, _el, to = _kill_run(mcmd, c.run_dir, _choice_merge_screen_cap(m_el, c.floor, mg.remaining()), merge=mg)」
file: `scripts/lumos:29075`(修後版,`_kill_merge_screen` 內)
file: `scripts/test_lumos.py`(`t_choice_kill_merge_screen_cap`)

- **失敗場景:** 修補宣稱要擋「單次快篩超出 `--max-seconds` 好幾分鐘」。守這件事的測試只直接呼叫 `_choice_merge_screen_cap` 這個純函式,例如 `_choice_merge_screen_cap(10.0, 20.0, 30.0) == 30.0`。
- 它的端到端那案只證明「快篩 4 秒、上限約 7.5 秒 → 通過」。這條在修前碼(`max(m_el * 5, c.floor)`)也會過。
- 所以有人把呼叫端改回不帶剩下時限,helper 與全部測試照綠,被保護的行為(快篩不超過剩下總時限)就沒了。
- **重現(修後版,臨時 worktree):**
  1. 把該行改成 `_kill_run(mcmd, c.run_dir, max(m_el * 5, c.floor), merge=mg)`。
  2. 跑 `python3.14 scripts/test_lumos.py -k t_choice_kill`。
  3. 輸出 `223 passed, 0 failed`,沒有任何一支翻紅。
- **歸因:** 有證據的修復回歸不成立,屬於修補自帶的測試缺口。
  - 修後:改壞後全綠(如上)。
  - 修前:該 helper 與對應測試不存在,上限就是 `max(m_el*5, floor)`,同一改壞等於修前行為,所以可比較。
  - 補法:加一案,讓合併基準耗時大、總時限只剩幾秒,斷言快篩的 `timeout` 小於等於剩下時限,或在 `_kill_run` 上攔截 timeout 參數。

### 2. 新測試 `t_choice_kill_merge_budget_reestimate` 約 58 秒牆鐘
severity: minor
blocking: 否
引句:「root, fake = _ckm_repo(2, {"__base_sleep__": 6})」
file: `scripts/test_lumos.py`(該測試內三處真實 `time.sleep` 與 11 秒、6 秒總時限)

- **失敗場景:** 這支測試用真實睡眠湊時限,在修後版單跑實測 `real 60.21s`。其餘四支新測試分別是 4.95、18.06、4.95 秒,以及 `merge_edges` 11.4 秒。
- 全套約 8 分鐘,單這一支就多約 12%。
- 睡眠與時限若成比例縮小(例如 6 秒改 1.5 秒、總時限 11 秒改 3 秒),判準不變,耗時可降約四分之一。
- **歸因:** 修補新增的測試成本,修前不存在。

## 已驗主張

- **修補的正常路徑**:`t_choice_kill_merge_{budget_reestimate,signal_race,screen_cap,edges,no_lane_chunk}` 在修後版各自單跑全綠(3、2、5、7、2 passed)。
- 以 `-k t_choice_kill` 跑整組(含變異後),`223 passed, 0 failed`。
- 以下三項是讀程式碼的判斷,沒有逐一翻紅實驗:
  - 訊號競態:`on_signal` 先設 `interrupted` 再掃登記表,`_kill_run` 先登記再讀 `interrupted`。兩個交錯順序都會至少收掉一次,沒有漏洞。
  - 重估:`_kill_merge_singles` 的截斷判斷(`b_to and cap < full` 才不寫基準)與單支流程用完整上限重量的行為一致。逐支路徑 `max(600.0, floor)` 不受剩下時限限制,所以「重量一次」成立。
  - `judged` 去重:把 `on_row` 的 `judged` 拿掉後,全檔只剩 `_ChoiceKillRun.finish` 一處算。`add()` 恆設 `p["plats"]`,手工構造的 plan 缺這個鍵時也會安全退成 `single`。
引句:「if merge is not None and merge.interrupted:   # 訊號在登記之前就來過:回呼沒看到這支,當場收掉」
引句:「if b_to and cap < full:   # 被剩下時限截斷:不算這支的基準」
引句:「plats = p.get("plats") or ()」

## 三問回答

1. **原問題的修復效果有何行為證據?**
   - 時限重估、訊號競態、無合併道、單檔與合計上限卡線這幾項,各有新測試在修後全綠。
   - 修前那一邊我只讀 patch 與 binding,沒有在修前 worktree 重跑這些新測試。它們在修前不存在,所以能不能比較未判定。
   - 快篩上限這一項,行為證據不足(finding 1)。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - `_kill_run` 的 `merge` 由 bool 改成物件。全檔只剩兩處呼叫端傳 `merge=mg`,沒有殘留 `merge=True`。
   - 抽出 `_gradle_module_parts` 後,`_gradle_test_module` 與 `_gradle_unit_test_task` 的行為都回到各自原本的回傳形狀,沒有相鄰呼叫端被弄壞。
   - 完整重估後不合併、退回逐支的路徑,有 `budget_reestimate` 第二案覆蓋。
3. **新發現的同一案例在修前、修後各是什麼結果?**
   - finding 1 只在修後版驗了(改壞接線仍全綠)。修前的碼就等於那個改壞版,所以兩版行為相同、沒有新回歸,屬修補未被測試守住。
   - finding 2 是修補新增的測試成本。

## 未驗範圍

- 沒有真 Gradle,所有結論都靠假 Gradle。
- 沒有重跑修前版的測試。
- 沒有檢查其他席負責的資料狀態類情境。
- 圖譜固定席(guard-kill 的兩條 INVARIANT:rc 優先序與 `--json` 純度)判不受影響。這次改動沒動 `rc` 計算或 `--json` 輸出,`judged` 也沒進結果列。

## 清理

- 已移除臨時 worktree `…/通才-sonnet/after`、`lumos_after.py` 與席目錄。
- 變異實驗只改了那個臨時 worktree,沒碰 repo 本體。

總結:最高嚴重度 major
