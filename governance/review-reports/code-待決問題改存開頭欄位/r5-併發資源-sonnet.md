severity: major

**Finding 1:空值或清單值的頂格鍵底下藏的阻塞題,會被靜默吞掉,規格閘放行**

severity: major
blocking: 是

- 引句:「for k2 in range(i + 1, len(fm_lines) if not owns else i + 1):」
- 佐證 file: `scripts/lumos`(`_pq_scan` 的切斷檢查,修後版)
- 問題:修補把「值空著或以 `|` `>` 開頭的頂格鍵」整個排除在切斷檢查外,範圍縮成空,理由是 `decisions:` 底下的 `  - id: d1` 是它自己的內容。但這會連 `  - id: Q2`(題目開頭)一起放過。
- 最小重現:把 `Q1`(`blocking: false`)和 `Q2`(`blocking: true`)這兩題,中間夾一行 `lands_in:`(或 `tags:` 加 `  - a`)。命令:`python3.14 $W/t3.py <lumos>`,腳本在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r5-併發資源-sonnet/t3.py`。
- 修前(d6bb423f):`pq_parse` 回 `errs=[(10,"…頂格的 'lands_in' 把清單切斷了…")]`,只剩 `['Q1']`,有報錯。
- 修後(48b327b0):`errs=[]`、題目只剩 `['Q1']`,沒有任何報錯。阻塞的 Q2 消失,規格閘看不到它。
- 修法方向:owns 的鍵仍要檢查 `^  - id: Q[1-9][0-9]{0,5}` 這種題號形狀的行,只放過非題號的 id(例如 `d1`)。
- 歸因:有證據的修復回歸。r3 補的反例在 r4 修補裡被放寬後又開了洞。
- 查證命令:對兩版 `scripts/lumos` 各跑一次 `python3.14 t3.py`,結果如上。

**Finding 2:守衛分派統一接 OSError 會把原本的追蹤改成「擋下」rc2**

severity: minor
blocking: 否

- 引句:「except (RuntimeError, OSError) as e:   # ★不接 ValueError★」
- 佐證 file: `scripts/lumos`(`main()` 的 `guard` 分支)
- 檢查結果:`cmd_guard_settle` 和 `cmd_guard_kill` 已在內部接 OSError,沒有把 OSError 當成正常回傳碼流程的子指令。
- 實跑 `python3.14 scripts/test_lumos.py -k guard`:819 passed、0 failed。
- 行為變化:沒被內部接住的 OSError(例如 `scaffold` 寫輸出夾失敗、`lumos guard list | head` 的 BrokenPipe)從追蹤 rc1 變成「擋下」rc2。
- 歸因:有證據的修復回歸(行為變了),但屬於刻意設計。
- 查證:前面的 guard 測試套件、加上靜態掃描 `cmd_guard_*` 的 `OSError` 使用處。

**其餘鏡頭,沒有發現**

- 平方級檢查:`_pq_bad_char`、`_pq_blank`、`_pq_scan` 都是線性。
  - `_pq_bad_char` 對 8 萬個「旗幟加標籤」序列耗時 0.64 秒、峰值 2.1MB;n 加倍,時間也約加倍。
  - 超長單串標籤(合法與不合法)、8 萬個「一字加一標籤」都是線性。
  - `_pq_scan` 在 4 萬行、8000 題、8 萬行頂格鍵、交錯頂格鍵與縮排行的輸入下都在 0.13 秒內。
  - 決策連結判定沒有改動,只用既有路徑。
- 同時寫入測試:16 個程序各自輸出很小,`communicate()` 依序收,不會卡住。連跑 4 次 `t_qfm_decision_add_shares_lock` 全過,約 5.8 到 7.7 秒。
- 鎖與符號連結:`_vault_lock_where` 以 vault 的 realpath 取雜湊,`_vault_write_lock` 登記的也是 realpath,`_vault_lock_held_for` 只解析資料夾,三者對得上。
  - 實測 vault 是符號連結、筆記是指到庫外的符號連結、兩者並用,修前修後都寫得進。
  - 一個既有現象(修前修後相同,不擋合併):`_write_lf` 用 `os.replace`,符號連結被換成一般檔,庫外原檔不會被更新。

**圖譜鏡頭**

- 已讀 `lumos-cli-write.md`、`lumos-cli-read.md`、`規格閘.md`。
- `lumos-cli-write.md` 已補上「守衛子指令在分派層統一接」和「筆記本身是符號連結時只解析它所在的資料夾」兩句,與程式一致。
- 沒找到與切斷檢查相關、會和 Finding 1 衝突的筆記宣稱。
- 計劃筆記說「清單被切斷會報錯」,Finding 1 的情況與此不符。

**三問**

1. 原問題(長旗幟序列平方級、`decisions:` 後接題目被誤擋)的修復效果:
   - 線性已用 8 萬旗幟序列量過,修前修後都是線性。
   - 合法的 `decisions:`、`lands_in:` 後接內容不再被誤擋。
   - 代價是 Finding 1 的漏報。
2. 修補處的正常、錯誤與相鄰呼叫路徑:
   - 守衛 819 個測試全過。
   - 鎖和符號連結路徑一致。
   - 錯誤路徑中,`owns` 鍵底下的題目行不再報錯,屬於退化。
3. 新發現案例的修前與修後:
   - Finding 1:修前報「切斷」,修後無聲遺失 Q2。
   - Finding 2:修前追蹤 rc1,修後「擋下」rc2。

**總結:** 資源與鎖都沒問題,但 `_pq_scan` 對「空值或清單值頂格鍵」完全不查題目行,會讓阻塞題靜默消失,規格閘放行,這是會擋合併的一條。

臨時檔案都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r5-併發資源-sonnet/`,等編排者收貨後刪。
