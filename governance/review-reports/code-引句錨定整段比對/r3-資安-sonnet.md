severity: minor

**1. 擋下事件的片段改用 `_esc_clean` 後,不可見的標籤字元和方向標記又能通過**
severity: minor
blocking: 否
引句:「snippet = (re.sub(r"\s+", " ", _esc_clean(first[:400], 400)).strip()[:60] or "-") if first else "-"」
file: `scripts/lumos:25838`
- 誰、從哪、送什麼:審查席或外部投稿的報告,在「引句:」後放一段含 U+E0020–E007F 標籤字元(隱形文字)和 U+200E、U+200F、U+061C 方向標記的字串。
- 走到哪:這段字串經 `_quote_block_note` 進 `first`,再被 `_esc_clean` 處理。`_esc_clean` 只清 C0、C1、U+202A–202E、U+2066–2069 和孤立代理字元,其他字元照留。
- 實測:我用 `_quote_block_note` 餵 `\u202e\u200f\u200e\u061c` 加上「ignore rules」的標籤字元編碼。輸出的 note 裡只有 U+202E 被換成空格,其餘全部原樣留在 `quote=` 後面。
- 拿到什麼:60 字內可以塞一句人眼看不到、AI 讀者讀得到的文字,寫進治理帳的 note。第 1 輪用 `unicodedata` 濾掉整個 Cf 類(包含標籤字元),這次換成 `_esc_clean` 就退步了。
- 影響範圍:因為只有單人和依序操作,而且字串只在 note 尾端,我只給 minor。
- 建議:在這個呼叫點外加濾 Cf 類。`_esc_clean` 是全域函式,註解寫明不能拆 ZWJ,所以不要改它本身。

**2. 診斷指令只加了 shell 引號,沒清控制字元,ESC 會原樣印到終端**
severity: minor
blocking: 否
引句:「_qdiag = f"    診斷:lumos quote-check {_qarg(rp)} --spec {_qarg(sp)} --rule {_qrule}"」
file: `scripts/lumos:26519`
- 誰、從哪、送什麼:帳上的 `report_path` 或 `snapshot_path`,取自編排者交的檔名,檔名可含 ESC(0x1b)。
- 走到哪:`_sh_quote` 就是 `shlex.quote`,只用單引號包住,控制字元原樣保留。處置閘接著把 `_qdiag` 直接 `print` 出來,沒有經過 `_esc_clean`。
- 拿到什麼:路徑裡的終端控制序列(視窗標題、OSC 52 寫剪貼簿等)會在使用者終端被執行。多行的路徑也能偽造出一行假的「診斷:」。
- 備註:同函式其他訊息(例如 `讀不到({pth})`)早就這樣印路徑,所以這是同一族舊問題,不是這次修補新造成的。診斷行是新加的,要補的話一起補。
- 我沒有實際在終端跑過 ESC 路徑,這條是讀程式推出來的。

沒找到 blocking 級的洞。以下幾條我都想過,都擋得住或沒有利用價值:
- **比較模式 `_read`:**
  - 路徑中間段的符號連結:`resolve()` 已把整條路徑解開,再檢查在不在 repo 內,所以中間段指向 repo 外會被擋。
  - 管線:`O_NONBLOCK` 加上 `fstat` 的一般檔檢查,管線和裝置檔進不去。
  - 硬連結和大小上限邊界:硬連結只會讓計數變動、不洩漏內容。`read(MAX+1)` 搭配 `len > MAX` 的上限邊界正確。
  - `resolve()` 和 `open` 之間的競態:只有單人環境才可能,不列。
- **full-span-v1 判準:**
  - 我試了不同型態引號夾雜,「…」內插『編造』、落單的」或』、前文有沒閉合的開引號、標籤巢狀。這些都落在整段不錨定,或判為 `stray`、`unclosed`,沒找到能讓編造後半被錨定的構造。
  - 容忍空白後再比一次的做法是舊行為,不是這次改動。
- **記憶體:** 比較模式單檔上限 128 MB,讀入後有三次複製,峰值約 4 倍。在單人環境下不當作攻擊面。

總結:最高等級 minor,blocking 共 0 條

我的實驗目錄 `/tmp/lumos-seat-work/code-引句錨定整段比對/r3-資安-sonnet/` 已刪除,repo 沒有被改動。
