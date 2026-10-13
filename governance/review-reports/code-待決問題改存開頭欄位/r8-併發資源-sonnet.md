severity: major

我沒有寫任何檔,也沒有清暫存。實驗都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r8-併發資源-sonnet/`,修前版在該目錄的 `before/`,修後版在 `after/`。有一個失誤要先講:我誤跑了一次 `git checkout -q --detach`,把 repo 的 HEAD 暫時脫離分支。我立刻用 `git switch` 切回 `EnzoHsieh-Android/qo-frontmatter`,提交仍是 d9c9b820,`git status` 乾淨。

1. 帳追加遇到 flush 失敗時截不回原長度,會把半行留在帳上,之後的簽核也被黏壞
引句:「fh.truncate(log_pos)」
severity: major
blocking: 是
- file: `scripts/lumos:9145`。`fh` 是帶緩衝的 `open(log,"ab")`,它的 `truncate()` 會先 flush。追加那一步若因寫滿或檔案過大而失敗,緩衝裡的殘餘還在,回滾時 flush 又失敗,截斷根本沒執行。這時訊息會寫「簽核帳還原失敗…帳可能留有半行」,帳上確實留著半行。
- 重現:先造一份 481 位元組的帳,在 `v4/` 下 `(ulimit -f 1; python3.14 after/scripts/lumos --vault docs/k signoff Systems/S --note x 2>&1 | cat)`。結果:rc 2,帳變成 512 位元組,尾端是半行;筆記有還原。
- 再跑一次成功的簽核,新行會黏在半行後面,整行變成壞 JSON。實測第 1 行壞、長度 140,`third after failure` 那筆簽核在帳裡讀不出來。
- 修前版:同一情境下帳逐位元回到原狀(`cmp` 相同),因為修前用 `log.write_bytes(log_before)` 重寫整份。
- 建議改法:用 `os.ftruncate(fh.fileno(), log_pos)` 之前先丟棄緩衝,或用 `buffering=0` 的原始檔案物件。
- 現有測試 `_PartialAppend` 是把 `truncate` 直接轉給真檔,沒有走真實緩衝路徑,所以抓不到這條。
- 歸因:有證據的修復回歸。兩版命令與結果如上。

2. 檢查寫入目標時丟出的 `WriteBlocked` 不在 signoff 的 try 接得住的範圍,筆記留著簽核戳記,訊息卻說「檔案沒動」
引句:「why = _write_refusal_reason(log)」
severity: major
blocking: 是
- file: `scripts/lumos:9129`。`_write_refusal_reason` 在 stat 失敗時丟 `WriteBlocked`。`WriteBlocked` 是 ValueError 與 RuntimeError 的子類,不是 OSError 或 UnicodeError,所以下面的 `except (OSError, UnicodeError)` 接不到。此時筆記已被 set 寫成 `signed_off`,卻沒有任何回滾。
- 重現(`t4.py` 注入帳檔 stat 失敗):`python3.14 t4.py after/scripts/lumos statfail`。結果:rc 2,訊息「檢查寫入目標 .signoff-log.jsonl 的連結狀態失敗:EIO sim;檔案沒動」。但筆記有 `signed_off: "2026-10-13"`,帳沒有新行,也就是筆記有戳記、帳沒有留痕。
- 修前版:同樣注入下直接噴 PermissionError 堆疊,筆記一樣沒回滾。
- 這是注入故障才出現的情境,不是自然發生的。
- 歸因:有證據的原有漏查(筆記不回滾)。修補新增的「檔案沒動」是不實的訊息。

3. 一行很長的 `- - - …` 讓清單範圍外的檢查變成平方級
引句:「text, prefixes = text[2:].lstrip(" "), prefixes + 1」
severity: minor
blocking: 否
- file: `scripts/lumos:7206`,同樣的剝前綴迴圈還在 `scripts/lumos:7211` 起的 `_pq_flow_questionish`、`_pq_questionish_key`、`_pq_structure_marker_problem`。每剝一次就複製整行,一行有 n 個 `- ` 就是 O(n²)。
- 實測 `_pq_scan`,單行 `  - ` 加上 n 個 `- `:n=20000 約 0.05 秒,40000 約 0.35 秒,80000 約 1.8 秒。n=250000(約 500KB)是 8.77 秒。
- 修前版 n=80000 約 0.0003 秒。
- 一個命令可能多次讀同一份筆記,時間會疊加。
- 建議改法:用索引往前走,最後只切一次。
- 其他我造的最壞輸入都是線性,沒有平方級:80000 個 `{a: b}` 片段、80000 層巢狀 `[`、80000 個 ZWJ 或 FE0F emoji、80000 個軟連字號、800k 個漢字、8 萬行 block scalar、8 萬個頂格鍵。記憶體峰值約 35MB。
- 歸因:有證據的修復回歸。

4. 另一個不拿鎖的程序在失敗瞬間追加的行,會被截回原長度一起截掉
引句:「log_pos = fh.tell()」
severity: minor
blocking: 否
- file: `scripts/lumos:9145`。
- 重現:`python3.14 t5.py after/scripts/lumos`。在第一次 `fsync` 時由另一個檔案把手追加 `{"other-process":1}`,再讓 `fsync` 失敗。結果:帳只剩 `{"old":1}`,別人的行消失。
- 這個情境要有不拿鎖的寫帳者,而且得剛好在失敗的瞬間追加,條件很苛。
- 修前版會用 `write_bytes(log_before)` 整份蓋掉,同樣丟行,只會更糟。
- 歸因:有證據的原有漏查。

5. `_write_refusal_reason` 檢查之後、`open(log,"ab")` 之前,帳檔被換成符號連結時會寫穿
引句:「fh = open(log, "ab")」
severity: minor
blocking: 否
- file: `scripts/lumos:9131`。`open` 會跟著連結走,沒有用 `O_NOFOLLOW`。
- 重現:`python3.14 t6.py after/scripts/lumos`。在檢查函式回來後把帳換成指向 `outside.txt` 的連結。結果:rc 0,簽核行寫進 `outside.txt`。
- 這需要攻擊者在微秒級時序內有目錄寫入權。
- 修前版根本沒有這道檢查,所以不是修補造成的。
- 歸因:有證據的原有漏查。

6. ⚠ 併發測試的穩定度有兩處疑慮,且測試抓不到第 1 條
引句:「rcs = [pp.wait() for pp in procs]」
severity: minor
blocking: 否
- 乙 patch 把 `communicate()` 換成 `wait()`,但程序還是 `stdout=PIPE`、`stderr=PIPE`。任何一個程序輸出超過管道容量(約 64KB)就會卡死,測試會掛住而不是變紅。目前輸出很小,所以現在不會發作。
- 簽核測試⑤用 `ready` 檔等輔助程序,上限 5 秒,接著 `proc.wait(timeout=5)`。機器負載重時輔助程序載入慢,可能超時或沒搶到先手。這種情況通常是通過但沒驗到先後順序,偶爾會丟 `TimeoutExpired`。
- 歸因:未判定。

**三問**
- ① 原問題的修復效果:
  - 帳追加失敗時,輕微失敗(例如 `OSError` 在 write 本身)能截回原長度,筆記也能在鎖內還原。我用注入 `fsync` 失敗驗過,筆記還原、帳回原長度。
  - 鎖內才讀原稿也成立,沒有蓋掉先拿鎖的別人。
  - 證據是 `t5.py` 的 stdout 與帳內容。
- ② 修補處的正常、錯誤與相鄰路徑:
  - 正常:`signoff` 成功,stdout 兩行,帳多一行。
  - 錯誤路徑有兩處不成立,見 1 和 2。
  - 相鄰:`WriteBlocked` 從 `main` 最外層統一轉成 rc 2,直接呼叫 `main()` 的入口也一樣。`decision-add` 的換行拒寫只走 `ValueError`,同樣是 rc 2。這兩條在我測的範圍內都成立。
- ③ 同一案例修前與修後:
  - 案例 1(`ulimit -f 1`):修前帳逐位元還原;修後帳留 512 位元組,含半行。
  - 案例 2(注入 stat 失敗):修前是 PermissionError 堆疊加筆記留戳記;修後是 rc 2 與「檔案沒動」,筆記仍留戳記。
  - 案例 3(250000 個 `- `):修前接近 0 秒;修後 8.77 秒。

圖譜鏡頭的回應如下。
- `Systems/lumos-cli-write.md` 的 118 行寫「帳任一步失敗用同一 fh 截回原長度…逐邊照實回報」。第 1 條實測此句不成立,而且測試名單裡的 `t_qfm_r8_signoff_and_write_refusal` 抓不到,這句得改成有條件的說法。
- `Systems/lumos-cli-read.md` 的 118、120 行描述清單外單一鍵名規則與看不見字元規則,和程式行為相符。沒有提到前綴剝除的效能邊界。
- `Systems/規格閘.md` 的 86 行把「長行平方級回溯」列為上一代做法被否決的理由,但新規則又長出同族的平方級(第 3 條)。

整體結論:甲、乙兩條單一規則在我測的範圍內行為一致,效能除前綴剝除外是線性;丙條的簽核回滾在錯誤路徑上有兩處破洞(第 1、2 條,會留下半行帳或不一致的筆記與帳),這兩條需在合併前處理。
