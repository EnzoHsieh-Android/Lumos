severity: minor

我跑過比較模式,沒找到 blocking 問題。幾個擔心的點結果如下:

- **TOCTOU**:最後一段路徑被換成符號連結會被 `O_NOFOLLOW` 擋掉。FIFO、目錄、`/dev/null` 符號連結、含 NUL 的路徑都算讀不到,沒有卡住,也沒有 traceback。
- **檔案代號**:`with os.fdopen` 讓所有路徑都會關閉,我沒找到洩漏。
- **MemoryError**:比較模式的表格最後才印,所以不會印出一半。凍結流程在寫 verdict 之前就丟出去,不會凍成假答案。回放流程的輸出沒有紅標記字樣,週跑會記成 `replay:<id>:rc1`,不會誤判成漂移。
- **寫側事件寫入失敗**:`_gate_event_or_warn` 只警告、不改判定,寫側仍 rc2 擋下。

1. 128MB 上限擋不住記憶體尖峰
severity: minor
blocking: 否
引句:「比較模式單檔上限:帳上最大的真實快照約 72 MB,留一倍餘裕」
file: `scripts/lumos:26679`
- 實測比較模式的尖峰記憶體(RSS):
  - 103MB 快照(ASCII 加一個 emoji,字串變 UCS4):約 2.5GB。
  - 約 128MB、CRLF 加 emoji:約 3.3GB。
  - 約 113MB 的報告(`引句：「x」` 重複 700 萬列):約 6GB、耗時 28 秒。
- 上限只限制檔案位元組,放大倍數有 25 到 50 倍。
- 主要放大來源:`data` 位元組還活著時就做 `decode` 和兩次 `replace`,加上 `_quote_norm` 和每條引句一列結果。
- 帳上最大真實檔 72MB 不會出事。這個上限不是記憶體的安全邊界,注解的「留一倍餘裕」說大了。
- 建議:`decode` 前先 `del data`,或把上限降到 32MB 左右。

2. 上層目錄被換成符號連結時,仍可讀到 repo 外的檔 ⚠
severity: minor
blocking: 否
引句:「if not fp.is_relative_to(root_real):」
file: `scripts/lumos:26728`
- 先 `resolve()`、判在 repo 內,之後才 `os.open`。
- `O_NOFOLLOW` 只擋最後一段,中間任何一層目錄在這兩步之間被換成指向 repo 外的符號連結,都騙得過。
- 這個時序我沒實際打出來。依單人、AI 依序操作的威脅模型,放行並寫明理由即可。
- 要補的話,最後再用 `os.path.realpath` 比對一次實際開到的路徑。

3. 比較模式的 `_read` 自己再寫一份「開一次檔、判一般檔」,沒用同檔既有的 `_regular_own_fd`
severity: minor
blocking: 否
引句:「fd = os.open(fp, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))」
file: `scripts/lumos:1387`
- `_regular_own_fd(path, flags, require_owner=False)` 已經做同樣的 `O_NOFOLLOW`、`O_NONBLOCK` 和 `S_ISREG` 判定。
- 它的注解還明寫過「原本另抄一份還少了擁有者檢查」這類教訓。現在這支又是一份平行實作。
- 之後兩邊改了其中一份,另一份不會跟著變。

4. 大小上限和超大檔略過分支沒有測試
severity: minor
blocking: 否
引句:「if st.st_size > _QUOTE_COMPARE_MAX_BYTES:」
file: `scripts/test_lumos.py:27077`
- 這輪補了 FIFO 和單獨 `\r` 的測試,但 `st_size` 超限和「讀到 N+1 位元組」兩條分支都沒有測試覆蓋。
- 把這兩條分支刪掉,測試仍全綠。
- 可以把 `_QUOTE_COMPARE_MAX_BYTES` 在同程序內臨時改小,用 stub 驗證略過計數會加一。

實驗目錄已刪除。

總結:最高等級 minor,blocking 共 0 條
