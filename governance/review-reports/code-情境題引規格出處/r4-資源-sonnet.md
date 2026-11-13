severity: minor

## z1 第二個訊號強制結束時,收尾裡卡住的 git 子程序變成孤兒
severity: minor
blocking: 否
歸因:有證據的修復回歸(修前第二個以後的訊號只記下、不強制結束,收尾的 git 不會被丟下;修後新增強制結束路徑才出現)
引句:「for proc in list(_KILL_RUN_LIVE.values()):」
file: `scripts/lumos:75805`(7e2c292e3 版);被丟下的 git 呼叫在 `scripts/lumos:27591`、`scripts/lumos:27594` 附近的 `_isolated_worktree` 收尾與 `_isolated_worktree_sweep`

失敗場景:
1. 輸入:收尾時 `git worktree remove --force` 卡住(例如大 build 目錄、慢磁碟),先送第一個 SIGTERM,再送第二個 SIGTERM。
2. 走到的行:`_situation_rule_force_exit` 只收 `_KILL_RUN_LIVE` 裡的測試程序群組,然後 `os._exit`。收尾用 `subprocess.run` 開的 git 不在那張表裡,沒人收。
3. 實測:我用假 `git` 在 `worktree remove` 時執行 `sleep 301`,載入 7e2c292e3 的 `scripts/lumos`,在 `_situation_rule_signals()` 裡包 `_isolated_worktree`,送 SIGTERM 兩次。
   - 第二個訊號後 rc=2,0.0 秒內結束,訊息正確。
   - `ps` 看到 `sleep 301` 的 ppid=1,是孤兒。我已手動 kill 並刪掉暫存資料夾。
4. 影響:用 Ctrl-C 時整個前景群組都會收到 SIGINT,git 會一起死,不受影響。只對外部只送單一 pid 的 SIGTERM 或 SIGHUP 有影響。卡住的 git 繼續佔著工作樹登記,事後清殘骸遇到它還在寫也可能互相踩。
5. 修前版本 f04090128:沒有強制結束路徑,第二個訊號只記下,收尾等 git 做完,沒有孤兒,但程序可能卡很久,這正是 r3 要修的問題。
6. 建議:在 `_isolated_worktree` 與 sweep 的 git 呼叫登記到一張表,讓 force_exit 一併收掉;或讓這些 git 呼叫用 `start_new_session` 開,並登記進 `_KILL_RUN_LIVE`。

## z2 中斷落在建鎖檔與寫入程序編號之間,留下空殘鎖,`drop_lock` 認不得
severity: minor
blocking: 否
歸因:有證據的修復回歸(修前等鎖期間 `defer=True`,處理器只記下、不丟 KeyboardInterrupt,這個視窗走不到;修後等鎖時第一個訊號照樣中斷、第二個訊號強制結束,視窗才可達)。視窗本身是 `_excl_lock_try` 的原有寫法。
引句:「if lock.read_text(encoding="utf-8").split("\n", 1)[0] == str(os.getpid()):」
file: `scripts/lumos:70695` 的 `_excl_lock_try`:`os.open(O_CREAT|O_EXCL)` 之後、`os.write` 之前只接 `OSError`,不接 KeyboardInterrupt。

失敗場景:
1. 輸入:寫入鎖剛好空著、這個程序剛用 `O_EXCL` 建好鎖檔,還沒寫入第一行程序編號時,收到第一個訊號(轉成 KeyboardInterrupt)或第二個訊號(`os._exit`)。
2. 走到的行:`_situation_rule_drop_lock` 讀到空字串,第一行不等於自己的 pid,所以不刪。
3. 實測:把 `os.fstat` 換成丟 KeyboardInterrupt,呼叫 `_excl_lock_try` 後再呼叫 `_situation_rule_drop_lock`,結果 `exists after drop: True ''`,下一次 `_excl_lock_try` 回 False。
4. 後果:殘鎖不會自動接手(`_excl_lock_try` 的說明明寫不接手)。下一次人裁或 set/append 要等滿 60 秒才拒絕,要人手動清鎖。
5. 機率很低(微秒級視窗),但修補宣稱「不留自己建的殘鎖」,這個視窗沒蓋到。測試 `half` 案例先寫好了 owner,沒涵蓋空檔。
6. 修前版本 f04090128:同一視窗只有 SIGKILL 才走得到。

## 附:三問、圖譜鏡頭

- 範圍:r4-repair.patch 全部 hunk(`scripts/lumos`、測試、筆記、兩份手冊)都讀過,執行緒與併發不審。
- 命令與結果:
  - 在 7e2c292e3 的 `scripts/` 解包副本上跑 `python3.14 scripts/test_lumos.py -k situation_rule_double_signal`:12 passed(最慢 6.3 秒)。
  - `-k situation_rule_force_kills`:2 passed(0.4 秒)。
  - `-k situation_rule_write_phase`:4 passed(10.0 秒)。
  - 三輪跑完後 `ps` 沒有我開的殘留程序,暫存全部用字面絕對路徑刪除。
- 問一,子程序收不收:
  - 第二個訊號 0.0 秒內結束,且收掉 `_KILL_RUN_LIVE` 內的測試群組,有測試(`t_situation_rule_force_kills_live_group`)和我的實驗佐證。
  - 例外是收尾的 git 子程序(見 z1)。
  - 測試自己另開 session 的孫程序逃出群組,修補與筆記都已誠實講明,不重複報。
  - `_KILL_RUN_LIVE` 在 `proc.wait()` 完成到 `finally` 的 `pop` 之間,理論上有幾個位元組碼的 pid 重用視窗(`killpg` 打已收掉的 pid)。我構造不出可重現的輸入,判為 ⚠ 未判定。
- 問二,時間預算:
  - 等鎖期間收到訊號,測試顯示 3 秒內結束。
  - 殺傷力段本身的逾時沒有改動。
  - 補記事件在拿鎖期間先呼叫 `_gate_event_build`(會問 git),這一步在 `st.defer=True` 下第一個訊號延後,只有第二個訊號能中止。可接受,未見超時證據。
- 問三,記憶體:
  - 本次改動沒有新的整檔讀入或二次方工作。
  - `_KILL_RUN_LIVE` 在 `finally` 裡 `pop`,不累積。
- `os._exit` 與 flush:
  - 強制結束前會先 `flush` 標準輸出與標準錯誤,再用 `os.write(2)` 直寫補記事件那行。事件字串在進入寫計劃與記帳之前就先算好,處理器內只印,所以補記事件那行不會留在緩衝區。
  - 標準輸出管道塞滿時 `flush` 理論上會阻塞,我沒有實測,未判定。
- repair 與 preserve 分開看:
  - repair:G1 三項(第二個訊號結束、等鎖中斷、補記事件)有測試守且測試通過。
  - preserve:單一 SIGTERM 或 Ctrl-C 的溫和收尾由 `t_situation_rule_term_signal` 與 `t_situation_rule_interrupt` 守。我沒有另外跑這兩支,未判定。
- 圖譜鏡頭:`LUMOS-LENS` 因鏡頭計算超時沒有固定席筆記,依派工詞不補算。
  - 改動牽連到的筆記:`Systems/guard-kill`(第 8 條中斷收尾與殘骸說法)、`Projects/情境題答案要引規格出處與回寫循環_計劃`、`Systems/規格閘`、`Systems/棧別提問表態閘`。
  - 筆記更新後與程式一致。
  - 但 guard-kill 第 8 條沒提收尾的 git 子程序可能留成孤兒(對應 z1)。
- 引句:「第二個訊號強制結束不等收尾,隔離工作樹與暫存資料夾會留下殘骸」

最嚴重:minor;blocking 共 0 條
