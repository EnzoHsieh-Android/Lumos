severity: major

## z1 殺傷力收尾期間第二個以後的訊號只記下,收尾卡住或很慢時沒有任何辦法中止程序
severity: major
blocking: 是
歸因:有證據的修復回歸(修前第二個訊號會中斷收尾,修後只記下;兩版查證見下)
引句:「★之後的★只記下、不再丟——收尾(worktree remove、刪暫存資料夾)不被第二個訊號打斷」
file: `scripts/lumos:75752`(_situation_rule_signals,`_on` 處理器的 `if not defer and len(got) == 1: raise KeyboardInterrupt`)
file: `scripts/lumos:27560`(_isolated_worktree 的 finally 裡 `git worktree remove --force` 與 `worktree prune` 都沒有 timeout)

失敗場景:
1. 輸入:殺傷力跑到一半收到第一個 SIGTERM,走到 `_isolated_worktree` 的 finally。此時 `git worktree remove --force` 要很久,例如工作樹裡有 Gradle 的大 build 目錄,或 git 掛住。
2. 使用者或對話工具再送 SIGTERM、SIGINT、SIGHUP:`_on` 只做 `got.append`,沒有任何動作。
3. 程序只剩 SIGKILL 或 SIGQUIT 能停。`git worktree remove` 沒有時間上限,所以停不停得下來完全看那個子程序要跑多久。

最小重現(已在本機跑過)。做法:把 PATH 前面放一支 git 殼,遇到 `worktree remove` 就 sleep 20。再用 `_situation_rule_signals()` 包住 `_isolated_worktree`,等進入後依序送 TERM、2 秒後 TERM、1 秒後 INT 與 HUP。
- 修後(f04090128):四個訊號送完 3 秒後程序仍活著(`after: still alive 7s after first signal`),到約 20 秒 cleanup 做完才結束。
- 修前(1d535b07b):同樣輸入,第二個訊號就讓程序立刻結束(`before: exited`)。代價是工作樹殘骸留在系統暫存(實測留下 `lumos-seatexp-*/wt`,我已刪)。

這是設計取捨:收乾淨換掉了能中止。但它沒有任何逃生口,例如累計 N 個訊號或超過 T 秒後放行,而收尾的 subprocess 又沒有 timeout。測試 `t_situation_rule_double_signal` 只驗收尾快速完成的情形,抓不到這條。

## z2 寫計劃到記帳整段訊號一律延後,搶寫入鎖最長 60 秒對 SIGTERM 與 Ctrl-C 完全無反應
severity: minor
blocking: 否
歸因:有證據的修復回歸(修前這段沒有延後;但上限 60 秒,不是無限)
引句:「defer=True(寫計劃到記治理帳那段):一律只記下,呼叫端在檢查點看清單決定 rc」
file: `scripts/lumos:75866`(`with _situation_rule_signals(defer=True)` 包住 `_situation_rule_locked_write`)
file: `scripts/lumos:30684`(`_vault_write_lock`,最多 60 秒輪詢,留下的過期鎖不會自動接手)

失敗場景:
1. 輸入:別的程序持有筆記庫寫入鎖,或留下殘留鎖。
2. `_vault_write_lock` 在 defer 範圍內輪詢,最長 60 秒。這段時間 SIGTERM、SIGINT 都只被記下。
3. 實測:另一程序持鎖 10 秒,在等鎖的程序上先後送 TERM 與 INT。4 秒後程序仍活著,拿到鎖後才結束(`done after 9.5 sigs [15]`)。
4. 修後的行為是搶不到鎖就回 rc 2(照 60 秒逾時),拿到鎖才發現有訊號而不寫。結果正確,但最長 60 秒停不下來。
5. 修法方向:等鎖時不延後,或延後範圍只從拿到鎖之後開始。

## 附:三問、圖譜鏡頭
- 三問①(殘留程序):
  - 單一 SIGTERM 或 Ctrl-C 的收尾路徑:走 `_kill_run` 的 `except KeyboardInterrupt`,收程序群組後 `proc.wait()`。我只讀碼,未實跑。
  - 兩個訊號的情形:z1 實測確認第二個訊號不再引發例外,所以不會中斷 `_kill_run` 的收尾。我只用 shim git 驗了 worktree 收尾這一段,沒有實跑 `_kill_run` 的程序群組。
  - 競態窗口:第一個訊號若剛好落在 `except subprocess.TimeoutExpired` 區塊內的 `_kill_proc_group` 之前,`except KeyboardInterrupt` 接不到,程序群組可能殘留。這是修前就有的窄窗口,我沒有實測,未判定。
- 三問②(時間預算):
  - 殺傷力基準每次最長 600 秒,另有 `LUMOS_KILL_TIMEOUT_FLOOR`(下限預設 20 秒)與壞法的 5 倍上限。這些我沒有改動也沒有驗證大輸入。
  - 寫入鎖等待見 z2。
- 三問③(記憶體與二次方工作):本輪修補沒有新增整檔讀入或二次方迴圈,我只翻了差異裡的相關段落,沒有做大輸入的實測,未判定。
- `--keep-worktree` 加建樹失敗(G7 repair):讀碼確認 `keep and wt.ok` 為假,走 else 分支,`shutil.rmtree(parent)` 照收,不寫標記,`on_keep` 照叫。我沒有實跑。若建樹時被中斷,`except BaseException` 會先收暫存資料夾。若 `git worktree add` 已登記到一半,因 `wt.ok` 為假而不跑 `prune`,登記可能殘留。這是修前就有的行為,未判定。
- 離開 with 後被記下的訊號:
  - 殺傷力段的訊號沒被吞掉,第一個已轉成 KeyboardInterrupt,走 rc 2。
  - 提交段記到的訊號,在 `_situation_rule_commit` 內按檢查點處理成 rc 2、rc 1 或 rc 0。
  - 記帳當中收到的訊號,帳記完後程序以 rc 0 正常結束。訊號沒有轉成終止,這是設計明講的。
- 圖譜鏡頭:派工詞說鏡頭計算超時、沒附固定席節點。以下只依差異判斷。
  - `Systems/guard-kill` 的修補:註記工作樹沒建起來時不留標記。判定不影響其他合約。
  - 計劃檔的修補:只是範圍 4、5 的文字對齊。判定不影響行為合約。
  - `.lumos/lint-waivers.json` 的簿記:判定不影響行為。
- 殘留檢查:實驗的子程序都已收掉,`ps` 確認沒有我開的 pid。暫存目錄(含 `lumos-seatexp-*` 殘骸)已用字面絕對路徑刪除。

最嚴重:major;blocking 共 1 條
