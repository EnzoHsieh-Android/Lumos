severity: minor

## Finding SEC6-01
severity: minor
blocking: 否
引句:「既有目標是裝置或 FIFO」
file: `scripts/scenario_probe.py:62`
- 誰:對 `--out` 或 `--history` 所在目錄有寫入權的另一個本機使用者。
- 從哪:在可預測的輸出檔名位置預先建一個 FIFO,自己在另一端當讀者。
- 送什麼:`mkfifo <out>`。開跑前檢查 `_output_target_problem` 對 FIFO 回 None,放行。
- 拿到什麼:探針的結果 JSON 直接流進攻擊者的讀端。繞過了執行者設定的 umask,例如 077。修前 FIFO 會被換成 0600 的普通檔。若目錄本來就讓攻擊者讀得到 0644 檔,就沒有額外收穫。
- 重現(`umask 077` 下對 FIFO 呼叫 `_atomic_write_text`):
  ```
  prob None
  fifo reader got [b'SECRET-RESULT'] still fifo True
  ```
- 其他實驗:
  - 新檔權限是 0644。
  - 預先放的硬連結不會被寫穿,受害檔內容仍是 V。
  - 輸出檔繼承硬連結對象的權限 0666,見 SEC6-02。
- 歸因:修復回歸。修前是原子取代,不會寫進 FIFO。這是「裝置/FIFO 直接寫」帶來的,屬推論性的縱深防禦。
- 備註:FIFO 沒有讀端時會阻塞,那是 DoS,不報。

## Finding SEC6-02
severity: minor
blocking: 否
引句:「新建檔、」
file: `scripts/scenario_probe.py:63`
- 誰:對輸出目錄有寫入權的本機使用者。
- 從哪:預先放一個硬連結,指向執行者擁有的 0666 檔。
- 送什麼:`ln <執行者的0666檔> <out>`。`old.st_uid == geteuid()` 成立,於是沿用 0666 權限。
- 拿到什麼:新輸出檔變成全域可寫。內容不會被寫穿,因為是 `os.replace` 換目錄項。這只是權限被帶進來,需要執行者本來就有 0666 的檔,所以是推論。
- 重現:同上實驗,硬連結後 `h.json` 為 0o666,受害檔內容未變。
- 另一點:新檔權限從修前的 0600(`mkstemp`)放寬為 `0666 & ~umask`,預設是 0644。`--history` 修前就是 0666 & ~umask,沒有變化。
- 歸因:修復回歸(權限放寬),需求來自先前審查。

## 六類逐類
1. 不可信輸入流到危險操作:
   - 暫存檔用 `mkstemp` 式的隨機名加 O_EXCL,固定前綴 `.probe-out-` 不構成競爭。
   - 目標是 symlink 時 `os.replace` 換的是連結本身,不會寫穿。
   - 檢查與寫入之間的時間窗只有微秒,不是批次長度。
   - 把檔換成 symlink 時,`O_NOFOLLOW` 會讓 `--history` 的 `os.open` 失敗,屬 DoS,不報。
   - 父目錄是連結的情況沒有處理,但那需要攻擊者控制祖父目錄。這是原有行為,不是新增的洞。
   - `old.st_uid==euid` 能被硬連結騙過,只影響權限位元,見 SEC6-02。
2. 登入與權限:已看,無。
3. 密鑰與個資:結果檔新檔權限變寬,見 SEC6-02。歷史檔權限不變。
4. 加密與傳輸:已看,無。
5. 執行邊界:
   - 報表 `text()` 流程是先加倍反斜線,再把非可列印字元轉成可見序列,最後轉義 `: @ ~ www.`(含大小寫)。
   - HTTP://、ftp://、mailto:、email 都靠 `:` 與 `@` 被轉義而失效。
   - 全形冒號與全形句點不是 GFM 自動連結的觸發字元,Zl/Zp 與 bidi 字元都已轉義。
   - `<`、`&` 由 `html.escape` 處理。
   - tty 測試的子程序碼是固定字串,只帶常數路徑 `GRAPHCTL`,沒有外部輸入或命令拼接。
6. 行動端:無。
- 新依賴:無。只新增了標準庫 `unicodedata`,以及腳本間的匯入。

看過的檔:`governance/eval/ablation_lumos_first.py`、`scripts/scenario_probe.py`、`scripts/test_lumos.py`(r6-snapshot.patch 內的三個產品與測試檔)。另外跑了 archive 出來的 `scripts/scenario_probe.py` 實驗,實驗目錄已 `rm -rf`。七篇圖譜筆記只看過 `ablation-lumos-first.md` 的文字,沒有逐篇細看,它們不是程式碼。

總結:最高嚴重度 minor
