severity: minor

## c1 等寫入鎖時被中斷,若落在「鎖檔剛建好、程序編號還沒寫進去」之間,殘鎖收不掉
severity: minor
blocking: 否
歸因:有證據的原有漏查(鎖檔建立在 `_excl_lock_try` 裡,修補沒動它;修補新加的 `_situation_rule_drop_lock` 宣稱要補這個窗口,但補不到)
引句:「等鎖時被中斷(KeyboardInterrupt 可能落在 _excl_lock_try 建好鎖檔、還沒進 try 的那幾行之間,鎖自己的收尾接不到)」
file: `scripts/lumos:70695`(`_excl_lock_try` 的 `os.open` 到 `os.write` 之間)
1. 輸入:等鎖時第一個終止訊號,剛好在 `os.open(O_CREAT|O_EXCL)` 之後、`os.write` 之前進來。處理器丟出的 KeyboardInterrupt 不是 OSError,所以 `_excl_lock_cleanup_failed` 不會跑。鎖檔留下,內容是空的。
2. `_situation_rule_drop_lock` 比對「第一行 == 自己的 pid」。空檔的第一行是空字串,不等於 pid,所以不刪。檔案留在磁碟上,而這支程式不自動接手既有鎖,下一次人裁或 set/append 要等滿 60 秒才拒絕。
3. 重現:載入模組,把 `os.write` 換成會丟 KeyboardInterrupt 的版本(fd 2 除外),呼叫 `_vault_write_lock`。
   - 修後 `7e2c292e`:中斷後鎖檔仍在且內容為空(`''`);再呼叫 `_situation_rule_drop_lock` 之後鎖檔仍在。
   - 修前 `f0409012`:修前沒有 drop_lock,同一個中斷同樣留下殘鎖,沒有任何收掉的機會。我沒另外跑修前版。
4. 窗口只有微秒,所以只標 minor。若要補,drop_lock 可改成「檔案是空的,或第一行是自己的 pid」就刪。檔案是空的表示建檔的人還沒寫完。

## c2 關終端時核心與 shell 各送一次 SIGHUP,記帳那段改成第二個就強制結束,帳可能沒記
severity: minor
blocking: 否
歸因:有證據的修復回歸(修前 `_on` 只在第一個訊號丟例外,第二個以後只記下;修後第 2 個一律 `_situation_rule_force_exit`。我是從 `git show` 的修前碼與修補差異推出來的,沒跑修前版)
引句:「r2 的「第二個以後只記下」撤回:收尾卡住時(git 掛住、大 build 目錄)沒有任何辦法中止(代碼審 r3 資源 z1 實測卡 20 秒)。」
file: `scripts/lumos:75818`(`_situation_rule_signals` 的 `_on`)
1. 輸入:關終端造成兩次 SIGHUP。修前的註解自己寫「關終端時核心與 shell 各送一次 SIGHUP」。
2. 兩次若落在計劃已寫入、`_gate_event` 還沒完成的時候,修後會立刻 `os._exit(1)`。治理帳可能沒記。補記事件印到已關閉的終端,看不到。
3. 重跑會被「已寫過」擋下,訊息叫人先刪計劃那一行再重跑,等於重跑一次殺傷力。這救得回來,但成本不小。
4. 重現:在 `_situation_rule_signals()` 裡設 `st.defer=True`,對自己連送兩次 SIGHUP。
   - 修後:印出提示與 `FORCED-DURING-RECORD`,`rc=1`,後面的 print 沒執行,程序已離開。
   - 修前:第二個只記下,程序不被終止,記帳會走完。
5. 這是兩段式的取捨,不是實作錯誤。
   - 兩次 SIGHUP 通常間隔很短,所以「按兩次」這條規則對 SIGHUP 等於一次就強制結束。
   - 第一個訊號被視為溫和收尾的前提不成立,收尾也不會被保護。
   - 建議:SIGHUP 不計入「第二個」,或兩個訊號間隔很短時視為同一個。

## 附:三問、圖譜鏡頭

**三問**
- ①原問題修復的行為證據:`python3.14 scripts/test_lumos.py -k situation_rule` 在修後版 143 passed、0 failed。這只證明測試通過,不證明問題解決。我另外跑的實驗只有一項。
  - 對自己送兩次 SIGHUP,第二個確實 `os._exit`,rc 等於 `st.force_rc`。這證明強制結束路徑有接上。
  - 我只驗了處理器本身,沒有真的在殺傷力、等鎖、寫入、記帳每個階段各送兩次訊號,那幾個出口未判定。
- ②修補處的正常、錯誤與相鄰路徑:
  - 邏輯上我讀過,沒發現矛盾:`st.lock` 在整個 commit 期間都設著;drop_lock 只刪第一行等於自己 pid 的鎖,等別人持有的鎖時被中斷不會刪到別人的。
  - `_KILL_RUN_LIVE` 只在 `_kill_run` 登記並在 finally 清掉。`Popen` 到登記之間有極小空窗,這是原本就有的缺口。
  - 「已寫過」三種判定:同段同列用 `any(...)` 比整串事件,不是只取第一筆;別段別列取 `evs[0]` 只拿來做訊息;帳壞原因由 `ruled()` 的第二個回傳值帶出。從程式讀來正確,沒跑多筆同條款事件的案例,未判定。
  - `_disk_spelling(vault, prel)` 需要 Path 型的根,`env.vault` 是 Path;讀不到清單時回 None,呼叫端已處理。
  - `on_keep(None)` 只有 guard kill 一個呼叫端(`scripts/lumos:27882`),已處理 None。
- ③新發現案例修前修後對照:c1 是原有缺口;c2 是修後行為改變。細節見各條。

**圖譜鏡頭**:這次沒有附固定席筆記(範圍計算逾時),沒有逐條判。我看過修補差異裡四篇筆記的改動(`Systems/guard-kill`、`Systems/棧別提問表態閘`、`Systems/規格閘`,以及計劃筆記),沒發現與程式碼矛盾的敘述。
引句:「★第二個★訊號:強制結束(_situation_rule_force_exit)——收掉還在跑的測試程序群組、刪自己的寫入鎖檔、印 st.force_msg、os._exit(st.force_rc),」

最嚴重:minor;blocking 共 0 條
