severity: major

我只讀了指定的 r7 檔(`r7-repair-binding.json`、`r7-behavior-cases.json`、`r7-repair-review-甲.patch`)和三篇固定席節點。修前(19bd4719)與修後(36d4ffed)的 `scripts` 各解到 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r7-併發資源-sonnet/{before,after}`。下面的重現都在那個目錄跑。

1. `signoff` 寫帳失敗時,還原用的是搶鎖前讀的舊筆記,會把別的程序剛寫成功的改動蓋掉。
severity: major
   - blocking: 是
   - 引句:「original = _signoff_read_original(path)」
   - 佐證 file: `scripts/lumos:9138`(搶鎖前讀 `original`)、`scripts/lumos:9149`(之後才拿鎖)、`scripts/lumos:9088`(還原寫回 `original`)。搶鎖最多等 60 秒,這段時間別人隨時能寫成功。
   - 最小重現(`race2.py`):
     - 程序 H 先拿寫入鎖,等 3 秒,把筆記 `status: doing` 改成 `done` 後放鎖。
     - 1 秒後跑 `signoff`,同時讓帳檔寫不進去(把 `.signoff-log.jsonl` 做成目錄)。
     - 命令:`./mk.sh $PWD/v2 && python3.14 race2.py after v2`
   - 修後結果:rc2,訊息說「筆記已還原」,筆記回到 `status: doing`,H 已成功的改動消失。
   - 修前(`./mk.sh $PWD/v3 && python3.14 race2.py before v3`):rc2,筆記是 `status: done`,H 的改動保留。
   - 第二個版本(`race1.py`):用 `set Systems/S status done` 當並行寫入者,它回 rc0 並印「✓ set」。signoff 失敗後筆記回到 `doing`,所以對使用者是成功的寫入被靜默吃掉。
   - 兩個 signoff 同時跑時,後者帳失敗,也會把前者剛蓋的 `signed_off` 戳記還原掉,但前者的帳列還在。
   - 節點 `lumos-cli-write.md:118` 寫「帳失敗逐位元還原兩邊」,在並行下不成立。
   - 歸因:有證據的修復回歸。修前沒有搶鎖前讀取,也沒有還原,不會有這個蓋寫。

2. 帳檔「讀得到前一版本以外的狀態」時,還原會把整本簽核帳截成 0 位元組。
severity: major
   - blocking: 是
   - 引句:「log_before = b""」
   - 佐證 file: `scripts/lumos:9110`(預設空值)、`scripts/lumos:9093`(`log.write_bytes(log_before)`)、`scripts/lumos:9111-9112`(讀帳放在 `try` 裡)。
   - 成因:`log_before` 預設是 `b""`,讀既有帳檔失敗時它仍是空的。`log_existed` 是真,還原就把這個「沒讀到」當成原內容,用 `write_bytes` 截斷重寫。
   - 最小重現:帳檔設成可寫不可讀。
     ```
     ./mk.sh $PWD/v6_after
     printf '{"old":1}\n{"old":2}\n' > v6_after/.signoff-log.jsonl
     chmod 0200 v6_after/.signoff-log.jsonl
     python3.14 after/scripts/lumos --vault $PWD/v6_after/kg signoff Systems/S --note n
     chmod 0600 v6_after/.signoff-log.jsonl
     wc -c < v6_after/.signoff-log.jsonl
     ```
   - 修後結果:rc2,訊息只說「筆記已還原」,帳檔從 18 位元組變成 0,舊簽核紀錄全毀,檔裡沒有 `signed_off`。
   - 修前(同命令換 `before`):rc0,舊紀錄保留並追加一行,檔 111 位元組。
   - 另外,還原是截斷後重寫整本帳,不是原子換名。遇到磁碟滿這類失敗,重寫到一半再失敗,帳只剩一半。
   - 這是 append-only 治理帳,不該有任何路徑能把它截空。
   - 歸因:有證據的修復回歸。

3. 還原本身失敗時,訊息前後矛盾,而且沒講清楚留下了什麼狀態。
severity: minor
   - blocking: 否
   - 引句:「raise WriteBlocked(f"簽核記錄寫不進去:{exc};筆記已還原{tail}") from exc」
   - 佐證 file: `scripts/lumos:9121`、`scripts/lumos:9090`。
   - 重現(`restorefail.py`):`./mk.sh $PWD/v5; python3.14 restorefail.py`。
   - 輸出是「…;筆記已還原;筆記還原失敗:EACCES」。字串寫死「筆記已還原」,不管還原有沒有成功。
   - 實際狀態是筆記有 `signed_off` 戳記、帳沒有那一列,訊息沒講這一點。
   - 帳根本沒動過的情況(例如帳檔是目錄)也會多印「簽核帳還原失敗」,雜訊會蓋掉真正的原因。
   - 歸因:有證據的修復回歸(修前沒有還原步驟,也沒有這句話)。

4. 其餘鏡頭沒有找到會擋合併的問題。
   - 效能(`perf.py`、`cli.py`):`pq_parse` 在這些最壞輸入下都是線性,倍增 n 時間約倍增(ratio 約 2.0),沒有平方級。節點 `lumos-cli-read.md:118` 說「一次線性掃描」成立。
     - 4 萬題:0.67 秒。
     - 4 萬決策:0.36 秒。
     - 4 萬行 block scalar,不論合法或每行都違規:不到 0.04 秒。
     - 4 萬個頂格鍵、4 萬個純量清單項、12 萬行、多段:都在 0.13 秒以內。
     - 16 萬字的單行值:0.04 秒。
     - 16 萬個旗、16 萬組 ZWJ:0.44 秒。
     - 標籤字串、零寬字:毫秒級,錯誤只回第一個。
     - 長串組合記號的正規化也不是平方級。
     - 記憶體:峰值約 170MB(4 萬題、20 萬行的那組)。
   - 唯一的放大是輸出量:每行違規回一筆錯誤。`lint` 對 2 萬壞行印出約 4MB,是線性,不擋。
   - 16 個 `signoff` 同時跑(同一篇):全成功,帳 16 列且都是合法 JSON,耗時 1.6 秒。
   - 16 個程序的同時寫入測試:
     - 空載 5.7 秒;30 個忙迴圈壓住 10 核下,`t_qfm_decision_add_shares_lock` 10.6 秒、`t_qfm_frontmatter_writers_take_lock` 14.4 秒。
     - 測試超時上限是 180 秒,兩支都過,穩定。
   - 符號連結檢查與寫入之間的時序縫:
     - 讀檔前的檢查與實際讀取之間若被換成連結,會讀到連結目標的內容。
     - 寫入端用 `os.replace`,換掉的是連結本身,不會寫穿到目標,所以沒有逃出筆記庫的寫入。
     - 利用這個縫需要同時有庫內寫權限的攻擊者,我沒有造出重現,只列為 ⚠ 不升級。
   - 新增的 `WriteBlocked` 同時繼承 `ValueError` 和 `RuntimeError`。我用語法樹掃了「只接 `ValueError`、`try` 內含會丟這信號的呼叫」的地方,只有 `_drift_fix_load`(`scripts/lumos:39817`)。它現在會把符號連結筆記當壞檔略過,是行為變動,不是丟寫入。

**三問**

① 原問題的修復效果:`-k qfm_r7` 21 過 0 敗,`-k signoff` 15 過、`-k summary_line` 27 過、`-k drift_fix` 161 過。`-k qfm_r6` 是 12 過 1 敗,敗的是 `t_qfm_r6_tool_flow_and_repo_compatibility`,原因是我解出來的目錄不是 git repo、`git show HEAD:scripts/lumos` 失敗,是我的環境造成的,不算產品問題。擋下符號連結與統一 rc2 的行為證據成立。但「帳失敗逐位元還原」只在單程序、帳可讀的情況成立,見 1、2。

② 修補處的相鄰路徑:
- 正常路徑(`signoff` 成功、`summary-line` 成功、16 個程序同時寫)都成立。
- 錯誤路徑中,單程序帳寫入失敗成立;並行蓋寫(1)和帳讀不到(2)不成立;還原也失敗時訊息矛盾(3)。
- 鎖逾時、BOM、CRLF 等拒寫維持 rc2。

③ 新發現案例的修前與修後:
- 案例 1:修前保留別人的改動(`status: done`);修後被蓋回 `doing`。
- 案例 2:修前 rc0、舊帳保留並追加;修後 rc2、帳檔 0 位元組。
- 案例 3:修前沒有還原步驟,所以沒有這句訊息;修後有。

總結:這輪的 `signoff` 先寫筆記再寫帳加上雙邊還原,在還原用的快照時機和帳檔缺省值上各有一處會毀資料,另有一處失敗訊息矛盾;`pq_parse` 的效能和併發鎖都沒有問題。
