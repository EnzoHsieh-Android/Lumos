severity: minor

鎖檔 `a58fc97a…json.warming` 不存在(ls 與 cat 都回「No such file」),沒有可處理的鎖,照派工詞審查。我沒建 worktree,只在臨時目錄放過一份 `scripts/lumos` 修後版本的文字拷貝,已用字面路徑刪掉並移除該目錄。對照用的鄰居程式碼是修後 `scripts/lumos` 的 `_kill_run`、`cmd_guard_kill` 單支基準段、`_gradle_test_module`、`_KillMerge`,以及全檔的 `time.monotonic()` 期限算法。

## 三問

**1. 分層與依賴方向:對齊。**
- `_kill_run` 的 `merge` 參數從布林改成 `_KillMerge` 物件,登記後讀 `merge.interrupted`。這跟既有的 `started`(`_BtProcs` 物件,呼叫 `started.launch(_popen)`)是同一種「由呼叫端傳入協作物件」的做法,沒有新增跨層方向。
- `_KillHooks.merge` 屬性和 `hk.merge = merge` 這條連線被拿掉。判法 `judged` 只在 `_ChoiceKillRun.finish` 算一份,`_KillHooks` 不再知道合併。這讓兩個類別的邊界比修前更乾淨,方向對。
- `_kill_merge_in_lane` 放在 `_kill_merge_iter` 旁邊,跟同區的 `_kill_merge_*` 命名與層次一致。

**2. 命名與錯誤處理:對齊。**
- `_choice_merge_screen_cap(m_el, floor, remaining)` 的簽名與寫法,跟鄰居 `_choice_merge_base_cap(total, floor, remaining)` 一模一樣(純函式、都在同一處、都用 `max(remaining, 1.0)` 保底)。
- 期限都走 `mg.remaining()`,底層是 `time.monotonic()`,跟全檔的期限算法(`deadline - time.monotonic()`)一致。這次沒有混進 `time.time()` 當期限。
- 被截斷的基準回 `False`、讓平台組退回逐支,走的是既有的「條件不合就原樣交 `plist`」降級路徑,沒有新增例外型別。

**3. 第二種做法:有兩處,都不到 major。**
- 好的一處:修補把 `_gradle_unit_test_task` 原本複製的模組路徑驗證抽成 `_gradle_module_parts`,讓 `_gradle_test_module` 與它共用。這正是在消除第二種寫法。
- 一處值得記錄,見下方 finding 1。
- 我沒找到訊號處理的第二種做法。修補沒有用 `pthread_sigmask`,也沒另開登記表,仍走既有的 `_KILL_RUN_LIVE` 加 `_kill_proc_group`。

## Findings

1. 單支基準的量測迴圈有兩份,各寫各的
severity: minor
blocking: 否
引句:「measured, full = [], max(600.0, c.floor)」
file: `scripts/lumos:28480`(`cmd_guard_kill` 既有的逐支基準 `_kill_run(cmd, run_dir, max(600.0, floor))`,寫入 `baselines[cmd] = (b_rc, b_tail, b_elapsed, b_to, bool(mstate["unsure"]))`)
說明:`_kill_merge_singles` 自己重寫了一個「跑 `_kill_run` 然後存五元組進 `baselines`」的迴圈,連 `max(600.0, floor)` 這個上限字面都再寫一次,跟 `cmd_guard_kill` 裡的那段是兩份。
為何不到 major:計劃〈做法〉2 明講要在開跑時先量齊、存進「同一份 `baselines`」,五元組形狀與鍵相同,逐支流程用同一份。這是結構對、只是日後改基準上限或記錄欄位時要記得改兩處。
歸因:有證據的原有漏查。`_kill_merge_base` 的 `for` 迴圈在修前版就有一份同形狀的量測(見 r2-repair.patch 被刪掉的 `_kill_run(cmd_of[m], … min(max(600.0, c.floor), …))` 那幾行);修補只是把它搬進新函式並加了重估。我沒有跑修前與修後版對照,所以歸因只憑 patch 文字,不是執行結果。

## 不對齊共 1 條,其中 major 0 條

## 已驗主張
- 修補把 `_kill_run` 的合併標記改成傳 `_KillMerge`,跟既有 `started` 協作物件同一種做法。
引句:「if merge is not None and merge.interrupted:   # 訊號在登記之前就來過:回呼沒看到這支,當場收掉」
file: `scripts/lumos:28192`(`started=None` 參數與 `started.launch`)
- 修補拿掉 `_KillHooks.merge`,判法改只在 `_ChoiceKillRun` 算一份。
引句:「plats = p.get("plats") or ()」
- 修補抽出共用的模組路徑驗證。
引句:「_gradle_test_module 與合併快篩的 _gradle_unit_test_task 共用」
file: `scripts/lumos:77449`

## 三問回答
- 原問題修復效果:這席只判一致性,沒跑兩版測試,不做行為判斷。上面的「歸因」只憑 patch 文字。
- 相鄰呼叫路徑:不傳 `merge` 的呼叫端(`_kill_run` 的 `merge=None`、`started` 路徑)行為不變。`merge is not None` 對舊的布林 `merge=True` 沒有殘留呼叫端:修補把兩處 `merge=True` 都改成 `merge=mg`,但我沒有 grep 全檔確認,這點未判定。
- 新發現的同案例修前修後結果:finding 1 是結構重複,不是行為,沒有可比較的案例,標未判定。

總結:最高嚴重度 minor
