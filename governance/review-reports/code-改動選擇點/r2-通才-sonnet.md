severity: minor

第一輪有兩份臨時暫存被留下:我跑 `t_choice` 子集時磁碟曾 100% 滿(約 1.1GB 可用),第一輪出現 11 支紅,我當時只看到摘要尾端,沒能指出是哪 11 支,所以只能推測與 ENOSPC 有關。磁碟剩 5.5GB 後在 4dd1ed800 的臨時副本重跑 `python3.14 scripts/test_lumos.py -k t_choice`,結果 216 passed, 0 failed。這輪沒有明確的修補回歸或功能錯誤,只有兩條 minor。

## g1 選擇點放行被排出推送小結的「AI 放的還沒人看過」提醒
severity: minor
blocking: 否 因為只少了推送端的提醒,doctor、`lint-waive --list` 與 `--ack --all` 仍看得到。
引句:「    lint, sit, _choice = _lint_waivers_split(cur)」
file: `scripts/lumos:42431-42438`、`scripts/lumos:80321-80324`
- 輸入:放行檔裡有 AI 放的 `choice:` 放行(origin 為 ai、acked 為 false)。
- 壞在:`_lint_waivers_ai_pending` 現在只數 lint 與 sit 兩份,選擇點放行兩邊都不算。推送小結(`ai_pending`、`ai_pending_situation` 那兩句)因此永遠不提這批放行。
- 影響:選擇點放行主要由 AI 下「不適用」判斷,推送端原本的人工複核提醒對它失效。
- 計劃相符性:計劃〈存活的處置〉還寫著選擇點放行走 `_lint_waivers_ai_pending` 的 `--ack` 流程,與程式不符。
- 預期:選擇點放行要有自己的一句計數,或計劃改寫。實際:兩邊都沒有。
- 查證(兩版跑同一支探針,放行檔 `{"waivers":[{"key":"choice:A.kt:abcd","origin":"ai","acked":false}]}`):
  - 修前 7826895c1:`_lint_waivers_ai_pending(d)` 回 1,`situation=True` 回 0。
  - 修後 4dd1ed800:兩者都回 0。
- 歸因:有證據的修復回歸。這是 g6 修補刻意拆分造成的副作用,推送小結那一端沒有補上。

## g2 守的測試雜湊每次要 N 次全樹 git grep,逾時時雜湊隨速度浮動
severity: minor
blocking: 否 因為最壞是 survived 的行多跑一次,不會讓判定出錯。
引句:「        r = _lens_git_dl(rr, "grep", "-l", "-F", "-e", n, at_sha, "--", deadline=deadline)」
file: `scripts/lumos:77848-77861`、`scripts/lumos:78151`
- 輸入:守的測試很多、repo 很大,`git grep` 在時限內查不完。
- 壞在:`_choice_test_blobs` 對每支測試各做一次整棵樹的 `git grep` 加一次 `rev-parse`,N 支就是 2N 次 git。
- 影響:時限內沒查完的測試只記空字串,這時 `tests_sha` 取決於「這次查完到第幾支」。查完幾支隨機器速度變動,同樣的測試內容兩次雜湊不同。`_choice_kill_pick` 的「守的測試沒變就不重跑 survived」因此失效,每次都重跑。
- 更便宜的做法:一次 `git grep -F -e n1 -e n2 …` 配 `-n`,或先 `git ls-tree` 取測試檔清單再讀,不必每支測試掃全樹。
- 歸因:有證據的修復新增(r1 g1 補強測試內容比對的副作用)。修前 `_choice_tests_sha` 只算名字,沒有這個查詢。我沒有造出會逾時的環境,逾時時的雜湊浮動是照程式推演;有 `deadline` 的行為本身由 `t_choice_kill_rerun_rules` 覆蓋。

## 圖譜鏡頭
- 本次沒附固定席節點,我只依 diff 對照計劃與 `Systems/guard-kill.md`、規格閘、kotlin 規則包的改動:
  - 計劃〈範圍〉1 寫「ast-grep 不在 → rc 3」,實際改成「有檔算不出來」也回 rc 3;`choice-points` 的 rc 說明沒同步,措辭層級,不影響行為。
  - `guard-kill` 的兩條合約(不傳新參數時輸出與 rc 不變、skipped 不進 rc)我讀過 `_KillHooks` 的改動,只新增 `killed_weak` 鍵,`stop_group_on` 為 None 時不動,不破壞。

## 三問
1. **原問題的修復效果有何行為證據?**
   - `t_choice_kill_weak_evidence`、`t_choice_kill_same_name_two_platforms`、`t_choice_unique_overlapping`、`t_choice_push_cap_waive_stable`、`t_choice_points_str_concat_chain`、`t_choice_scan_per_file`、`t_choice_points_pick_order`、`t_choice_guard_kill_new_params`、`t_choice_range_mainline_slash_remote`、`t_gov_stats_choice_dedup`、`t_choice_ledger_write_semantics` 共 11 支在修後版本全部通過。其餘 `t_choice` 子集也全綠,共 216 支。
   - 我只有修後版本的跑法,沒在修前版本跑同一批,所以「修前紅、修後綠」沒親自驗。
   - 另有一條我自己在修前、修後都跑的真實 ast-grep 實測。用 `_choice_scan` 加 `_choice_file_points` 跑真規則,修後版本:`name + ": " + id` 與 `f1 + id + "/"` 都沒有壞法(status none),`a + b + c` 照常挑到 `$A - $B`。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - `_choice_scan`、`_choice_compute` 的新回傳形狀,我 grep 了全部呼叫端(`choice-points`、`choice-kill`、推送前、`_choice_waive_target`),四處都已改成處理三元組與 `unverified`,沒有遺漏。
   - `_count_overlapping` 取代 `str.count` 後,repo 內已無其他把 `old` 當 `str.count` 數的地方(grep 確認)。
   - 通過的路徑:per-file 掃描單檔 15ms 一次,實測夠快。
   - 未通過的相鄰路徑:g1(放行檔計數)。
3. **新發現的同一案例修前、修後各是什麼結果?** g1 修前回 1、修後回 0(有兩版證據)。g2 沒有修前對照,因修前沒有這個查詢。

## 已驗範圍與未驗範圍
- 已驗:`_choice_err_cover`、`_choice_iv_cover` 二分的區間語意與原本的雙層迴圈等價(讀碼推演);`_choice_identity` 的視窗切片位移計算(讀碼推演);`_choice_gate_event` 對 `None`/`False` 的處理與 `_gate_event_fit` 改動的清單縮減路徑;`gov --stats` 去重鍵對 choice 事件的鑑別子(各筆自帶 token,不會被誤折)。
- 未驗:
  - 括號隔開的字串串接,例如 `url + ("/" + id)`。這輪抽到的是 `$B`,能編譯;換種子可能抽到 `$A - $B` 而編不過,屬啟發式的上限,我沒造出會紅的案例。
  - 真 Android 專案的端到端耗時(計劃已列 S26 手動驗收)。
  - `sbr.yml` 改成 `inside: {not: {kind: statements}}` 後「命中集合與修前相同」的宣稱,我只看到筆記的比對說法,沒獨立重跑對照。

最嚴重:minor;blocking 共 0 條
