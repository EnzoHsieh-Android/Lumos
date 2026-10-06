severity: major

## PF1

severity: major  
blocking: 是

逐字spec引句:「當載體報告零引句且快照可讀，記帳器應以 rc2 拒收」

判準：驗收測試必須進入「載體全錨」實際分支。

實測觀察：未執行真 CLI；靜態查碼及既有收據顯示原版確為 16 pass／24 fail。但兩支新測試均未傳 `--loop`，而報告及載體驗證受 `if loop and auditor` 控制。因此負向測試無法透過預定分支轉綠；正向控制即使通過，也沒證明全錨載體未被誤擋。若為讓測試轉綠而把檢查移到全域，反會擴張核心範圍。

file: `scripts/lumos:9514`  
file: `scripts/lumos:9565`  
file: `scripts/test_lumos.py:25619`  
file: `scripts/test_lumos.py:25662`

具體錯行為：測試可能逼出非 loop 記帳的新限制，或持續測不到真正載體分支。應在每個案例加入唯一 `--loop`，正向案例避免輪次互相污染。

## PF2

severity: major  
blocking: 是

逐字spec引句:「只在已讀取有效 UTF-8 快照時辨認零引句；不把讀不到快照誤報成零引句。」

判準：既然宣稱只對有效 UTF-8 判零引句，機械驗收須涵蓋「檔案存在但不是 UTF-8」。

實測觀察：未執行真 CLI。現寫側以嚴格 UTF-8 解碼快照，卻只捕捉 `OSError`；`UnicodeDecodeError` 會逸出成 traceback。讀側處置閘則明確同時捕捉兩者。S4 測試只使用不存在的路徑，無法驗證 spec 的 UTF-8 語意。

file: `scripts/lumos:9568`  
file: `scripts/lumos:9569`  
file: `scripts/lumos:22928`  
file: `scripts/test_lumos.py:25635`

具體錯行為：非 UTF-8 快照可能 traceback，而非沿既有文字／IO 錯誤出口 rc2；新增二進位快照案例並釘住不誤報「沒有引句」。

四項核對：①術語／旗標已核對，主要問題是測試漏 `--loop`；②引用均存在，未見壞引用；③核心範圍文字無直接矛盾，但 PF1 會誘發實作擴域；④CLI、處置閘、引句抽取器、三支測試、Systems 責任及兩條合約、兩份收據均已核對。

最嚴重：major；blocking 數：2。