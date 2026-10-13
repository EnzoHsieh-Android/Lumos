severity: minor

**1. 主流程等待迴圈在第 0 條工作執行緒先結束後變成空轉,吃滿一顆核心**
severity: minor
blocking: 否
引句:「while any(th.is_alive() for th in threads) and not errs:」
file: `scripts/lumos:48248-48249`(diff 內第 248、249 行)
1. 時序:佇列領完後,`threads[0]` 先拿到 `queue.Empty` 並離開。其他工作者還在跑慢測試。
2. 走到 `threads[0].join(0.1)` 時,已結束的執行緒會立刻返回,不會睡 0.1 秒。`any(is_alive)` 仍為真,迴圈沒有任何等待地一直轉,直到最後一支測試結束。
3. 這段尾巴在不等長的測試上很常見,負載會落在還在跑的測試上。
4. 重現:在臨時目錄用本 diff 的 `_run_bound_tests`,`parallel=2`,一支瞬間完成、一支睡 4 秒。實測結果是 `wall 4.1 main-proc cpu 4.0`,主程序在整個等待期間 CPU 時間約等於牆上時間。
5. 影響:並行閘本來就在跟同時跑的測試搶 CPU。多出一顆空轉的核心會拖慢它們,拖慢又會推高 `LUMOS_TEST_TIMEOUT` 誤判逾時紅的機率。我沒有實際逼出誤判,所以不升級。
6. 修法是改成 `for th in threads: while th.is_alive() and not errs: th.join(0.1)`,或用 `Event` 等待。

## 最壞時序逐項判定(沒找到錯,不列為 finding)

- **共用的 todo、errs、seen、lock:**
  - 一條執行緒剛 `append(errs)`、另一條剛 `get_nowait` 到工作時,後者會把那一支跑完(最多到它自己的逾時),結果被丟掉,主流程已經 `raise errs[0]`。
  - `list.append` 在 CPython 下是原子操作,主流程不加鎖讀 `errs` 沒問題。
  - 只有在 `errs` 為空而且所有執行緒都結束時才會往下組結果。此時每個 job 都已經寫進 `seen`,因為工作者只會因為「佇列空」或「errs 有值」離開。所以不會有「errs 有值卻拿不完整的 seen 去組結果」。最後那次 `if errs` 檢查也涵蓋了「最後一條執行緒剛出錯就結束」的時序。
- **`tails` 與 `results`:** 只在主流程、工作者全部結束之後才讀寫,沒有競爭。
- **子程序:**
  - 每個 `_kill_run` 各自開 `TemporaryFile`,各自 `start_new_session`,逾時時只殺自己的程序群組,同時跑不會互相影響。
  - 出錯往外丟後,已開跑的子程序會成為孤兒,跑到自己的逾時為止,daemon 執行緒隨程式結束消失。這是 diff 註解明講的取捨,跟循序時按 Ctrl-C 同形。
  - 我用 8 個 `t_bound_tests_parallel_error_stops` 同時跑,全綠,耗時 0.1 到 0.3 秒。
- **被跑的測試彼此互踩:**
  - `_isolate_environment`(`scripts/test_lumos.py:36169`)每次執行都會建自己的 `gctl-run-*` 根,把 `TMPDIR`、`HOME`、`.gitconfig` 都換掉。
  - 清舊殘骸時只刪標了 `.finished` 或超過一天的根,不會刪別人正在跑的。
  - 我在複製出來的 repo 裡同時跑 4 支(`t_bound_tests_gate`、`t_guard_kill_rc_precedence`、`t_reinject_preserves_outside`、`t_guard_kill_json_purity`),全綠,`git status` 乾淨。
- **新測試在負載下會不會誤紅:**
  - `S2` 的「同時跑」判定要求別支在 2 秒內出現,不靠計時,可以接受。
  - `S4` 的 `1.8 <= secs < 3.5` 與 `S5` 的 `took < 5` 在極端負載下有邊界,但給不出具體失敗場景,不標。

## 圖譜鏡頭(固定席)

- **guard-kill 的 INVARIANT(rc 優先序、`--json` 純度):** 這份 diff 只動 `_run_bound_tests`、`_bound_tests_check`、`_bound_tests_log` 和新的 `_bound_tests_parallel`。`_kill_run` 本身沒改,guard kill 的 rc 與 JSON 路徑也沒碰。上面實跑的 `t_guard_kill_rc_precedence` 與 `t_guard_kill_json_purity` 都綠。
- **lumos-cli-lifecycle 的 INVARIANT(re-inject 保留 sentinel 之外內容):** 沒碰。`t_reinject_preserves_outside` 實跑綠。
- **bound-tests-gate 的 INVARIANT(逐支真跑,任一紅、懸空、偽證據、方法名不合法或證不出跑過就擋,rc1):** 判定邏輯沒變。去重鍵 `(root, cmd)`、逾時、`_ran_evidence_check` 都照舊,只是改成先排計畫、跑完再照原順序組結果。同一支被兩篇綁時,兩筆結果都在。無 `run_cmd`、懸空這類項目仍照原樣出現在結果裡。
  - 要記住的一點是 `secs` 語意變了,從逐項相加改成牆上時間,並多了 `secs_kind: wall`。這不影響擋與不擋的判定。
- **測試假綠形態(前置斷言):** 新增的 `S2`、`S5` 都有前置檢查,例如「各支有沒有看到別支同時在跑」和「RAISED」,不是只看 rc。
- **design-loop、reversibility-governance-ledger 等:** 沒有牴觸。多的 `secs_kind` 是新增欄位,舊的讀帳端不會被它破壞。
- 其餘名單裡標「只列名」的節點,我沒有逐條讀。

總結:最高等級 minor
