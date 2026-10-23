severity: minor

## 1. 重跑腳本在分析工具缺失或崩潰時,會留下暫存查詢檔
severity: minor
blocking: 否
引句:「    r = subprocess.run([tp, trace, '-q', f.name], capture_output=True, text=True, encoding='utf-8', errors='replace')」
file: `scripts/templates/android-receipt-rerun.sh:57`
歸因:有證據的原有漏查。這一行只多了編碼參數,`delete=False` 加 `os.unlink` 的寫法修前就有,不是修復造成的回歸。
具體失敗場景:`TP` 指到不存在的程式時,`subprocess.run` 丟 `FileNotFoundError`。後面的 `os.unlink(f.name)` 沒跑到,每次重跑都在系統暫存目錄留一個 `.sql`。腳本以 Traceback 結束,退出碼是 1,和「比對不符」同碼,讀的人分不出是比對不符還是工具壞了。
查證:修前版 `git show 46773fe6:scripts/templates/android-receipt-rerun.sh` 與修後版 `e3ea2c16` 的這兩行結構相同,都沒有 `try/finally`。

我沒有在實際環境裡造這個失敗場景,結論是從兩版程式碼比對得出的。逾時也沒有保護:`subprocess.run` 沒帶 `timeout`,真的 trace_processor 卡住就會一直等。這條屬原有設計,不是本輪新增,所以只給 minor。

## 逐項查證結果

**①遞迴那步加回 `WHERE s.dur >= 0` 的成本:沒有退化。**
- 做法:我用 Python 內建 sqlite3 造假表,把修前 `46773fe6` 和修後 `e3ea2c16` 的 SQL 範本各跑一遍。
- 規模與結果:

| 規模 | 修前 | 修後 |
|---|---|---|
| 30.2 萬區段、2000 幀 | 1.27 秒 | 1.27 秒 |
| 39 萬區段、3 萬幀(每幀名稱都不同,`names` 因此很大) | 1.65 秒 | 1.74 秒 |
| 30 萬區段全掛在單一幀下 | 1.09 秒 | 1.06 秒 |

- 有沒有手動建 `parent_id` 索引結果都一樣,SQLite 自己建了自動索引。
- 新增的過濾只是對 `slice` 一個欄位的比較,沒有多一層巢狀迴圈,也沒有平方級行為。

**②測試多跑的兩次子程序:整體成本小,殘留風險也低。**
- 時間:`python3.14 scripts/test_lumos.py -k android_ui_attribution` 共 52 案例,整體 1.3 秒;收據重跑那支測試只要 0.4 秒。
- 殘留:`sp.run` 沒帶 `timeout`,但被呼叫的假分析工具只跑一次 `grep` 和 `printf`,不會卡住。`subprocess.run` 在例外或 Ctrl-C 時本身會收掉子程序。
- 暫存檔:假分析工具成功執行,`os.unlink` 有跑到,跑完後 `/tmp` 下沒有新的 `tmp*` 殘留。

**③記憶體:沒有新增整份大檔讀取。**
- 新增的 `reconfigure` 和 `encoding=` 不改變讀取量。
- 重跑腳本用 `capture_output` 把分析工具的完整輸出放進記憶體,這是修前就有的,而且查詢只回每幀一列。

## 三問回答
1. **修補的行為證據是否成立?** 成立。大資料量下用過濾和不用過濾的耗時一樣,測試也只多花不到 1 秒。
2. **修補處的錯誤與相鄰路徑呢?** 錯誤路徑(收據寫錯)在 LC_ALL=C 下仍回 2 並印出中文原因,見 `scripts/test_lumos.py` 新增的 `err3` 檢查。分析工具缺失的相鄰路徑沒有被補,即上面第 1 條。
3. **新發現的案例在修前修後各是什麼?** 只有第 1 條:修前修後行為相同,都是漏查,不是回歸。

總結:最高嚴重度 minor
