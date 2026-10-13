severity: minor

我跑了實驗、讀了修補的程式碼,沒找到 blocking 級問題。唯一的發現是新判準對過短引句的多餘成本,屬 minor。`python3.14 scripts/test_lumos.py -k quote` 173 條全過。

**1. full-span-v1 對「過短引句」仍整份掃快照,時間白花**
severity: minor
blocking: 否
引句:「    anchored = nq in hay or nq.replace(" ", "") in hay_ns」
file: `scripts/lumos:25849`(`_quote_anchor_row`,新判準專用)
- 輸入:報告含大量不足 10 字的引句(例如 `引句：「Zq123」`),快照約 2400 萬字元(約等於帳上最大的 72 MB 快照)。
- 走到哪:`too_short` 已經成立,`ok` 一定是 False。但 `anchored` 還是先跑兩次子字串搜尋(`nq in hay`、`nq.replace(" ", "") in hay_ns`),每條要整份掃快照。
- 實測:1000 條短引句、報告只有 21 KB,legacy 與 full-span-v1 各約 28 秒,每條約 28 ms。報告 1 MB 就約 24 分鐘。
- 寫側擋下時 `_quote_block_note` 兩版判準各跑一次,成本加倍。處置閘與回放也各跑一次。
- 修法:把 `anchored` 改成先判 `too_short`,例如 `anchored = (not too_short) and (...)`。這會讓 `ok` 與其他欄位的值完全不變。
- 舊判準的同一個形狀依約「一字不改」,不用動。
- 這和已立的 Issue(未閉合標籤二次方成本)是同一類報告大小問題。它是另一種輸入形狀,Issue 沒涵蓋。

**逐項檢查結果**
- **MemoryError 兩處一致:** `_quote_block_note` 與處置閘都是先 `except MemoryError: raise`,再 `except Exception`。寫側主判斷 `_quote_rows(...)` 沒包 try,也會往外丟。三處行為一致,而且這時不會寫事件也不會寫帳。
- **寫側事件與帳寫入順序:** 擋下時只寫事件、不寫帳。`rec["quote_rule"]` 只在檢查全過後才蓋章,排在檢查之後、寫帳之前,沒有半寫狀態。`_validated_sha["--report"]` 與 `_rtext` 來自同一份位元組。事件已記下的擋下之後,`sha` 不符的回頭檢查才擋,這個順序可接受。
- **新判準的時間與記憶體:**
  - 未閉合標籤:10 萬個 0.12 秒、200 萬個 3.0 秒,是線性。對照舊判準 10 萬個要 110 秒。
  - 巢狀、大量落單收尾引號、10 萬條真引句:都在 0.5 秒內。
  - 記憶體:200 萬個未閉合標籤(約 8 MB 報告)約 2 GB,每個標籤一個 row dict。舊判準也是每標籤一個 row,所以不是退步。
  - 擋下事件多算另一版判準,24M 字元快照約 0.6 秒、462 MB,可接受。
- **處置閘例外範圍:**
  - `_qdiag` 在 try 之外組出,但路徑含控制字元或孤立代理字元時走「不印可照貼指令」的分支。
  - 其餘路徑經 `_drift_sh` 加引號,不會丟例外。
  - 判準丟例外、`MemoryError` 的分流正確。
- **拿掉比較模式的殘骸:** 我 grep 了 `scripts`、`docs`、`ARCHITECTURE.md`。沒有 `compare-rules`、`_QUOTE_COMPARE*`、`qc_compare`、`qc_repo` 的殘留引用。剩下的提及都是計劃與驗證筆記裡「已拿掉」的說明。
- **擋下事件的片段跳脫(`_kill_esc`):** 控制、格式、行段分隔字元都以 `\uXXXX` 寫出,片段排最後。有一點很小的不精確:`_kill_esc` 不跳脫反斜線,報告裡手寫的字面 `\u202e` 與真字元的跳脫結果無法區分,所以「無損」說過頭了。這只影響人讀的片段,`gov --stats` 只看 `quote-rule:` 開頭,所以不是 finding。

實驗目錄 `/tmp/lumos-seat-work/code-引句錨定整段比對/r5-資源-sonnet/` 已刪,repo 沒被改動(`git status` 仍是原本 3 個未追蹤的卷證檔)。

總結:最高等級 minor,blocking 共 0 條
