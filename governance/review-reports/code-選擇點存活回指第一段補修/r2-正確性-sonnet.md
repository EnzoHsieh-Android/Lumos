severity: minor

圖譜固定席判定:本輪只改 `scripts/lumos`、`scripts/test_lumos.py` 與四篇筆記,行為都落在 guard-kill、規格閘、選擇點計劃三篇的家內。這三篇對應的合約行(★INVARIANT★)沒被碰到;改到的筆記句子跟程式現況一致。沒有圖譜面的新問題。

我沒找到會做出錯行為的洞。逐 hunk 走過的結果如下:
- `store` 的基準檔寫失敗另包 try,覆蓋資料照用。基準檔被資料夾佔住的案例我跑過,綠。
- 殘留舊基準檔不會跟新覆蓋資料錯配:`cached()` 取不到時會先刪掉兩個檔再重量。
- `_choice_cov_base_read`:`bool`、字串、NaN、Infinity、負數、超大整數(OverflowError)都回 None。三萬層巢狀 JSON 也沒拋例外。
- `_KillPrep._src_pkgs` 以平台根為鍵只掃一次,沒有別的同名方法衝突。
- 新測試(`t_choice_cov_src_pkgs_edges`、`t_choice_cov_base_read_rejects`)我實跑,2 passed。`t_choice_cov_resume_old_cache` 我只讀碼、沒跑,翻紅釘看來成立(先確認 `bases` 數量,再比對重量與 reach)。

以下三條都是小問題,不阻擋。

severity: minor
blocking: 否
file:line `scripts/lumos`:79808 附近(`_choice_cov_src_pkgs`、`_CHOICE_COV_SRC_SKIP`)。改成共用 `CODE_SKIP_DIRS` 後,跳過清單在任何深度比對資料夾名,所以 `bin`、`obj`、`dist`、`publish`、`vendor` 這幾個名字連同套件路徑段一起被跳過。另外,`src` 底下名字以 `test` 開頭的資料夾,即使是主程式也被當測試資料夾跳過。
具體輸入(我已實跑):
- `app/src/main/java/com/a/vendor/V.kt`(`package com.a.vendor`)沒收進套件集合。`com.a.dist` 同樣沒收。
- 單純的 Java 目錄結構 `src/testapp/A.kt`(`package testapp`)也沒收。
後果:只碰這些套件的 Robolectric 測試,專案類別有紀錄數是 0,被標「覆蓋接不起來」。如果前 5 支 Robolectric 測試都這樣,斷路器會把整個平台組的覆蓋關掉。方向是多跑、變慢,不會判錯。被改到的檔自己的套件仍會經 `req[g]["pkg"]` 補進去,所以不影響被改的那行。
引句:「_CHOICE_COV_SRC_SKIP = frozenset(CODE_SKIP_DIRS | {".gradle"})」

severity: minor
blocking: 否
file:line `scripts/test_lumos.py`:`t_choice_cov_src_pkgs_edges`(新增)。新測試只把 `_CHOICE_COV_SRC_MAX` 壓到 1,來驗證看滿上限就停並提醒。這次新增的另一道上限 `_CHOICE_COV_SRC_ENTRIES`(走訪檔數,含非原始碼)沒有任何案例。把 `or entries > _CHOICE_COV_SRC_ENTRIES` 整段拿掉,測試仍全綠。這道上限保護的是「非 .kt/.java 的檔很多」的資源情境,測試守不住。覆蓋面可更完整,屬小問題。
引句:「if seen > _CHOICE_COV_SRC_MAX or entries > _CHOICE_COV_SRC_ENTRIES:」

severity: minor
blocking: 否
file:line `scripts/lumos`:79802 附近(`_CHOICE_COV_PKG_RE`)。這條正規式在 8KB 內取第一個以 `package` 開頭的行,沒有略過區塊註解。我已實跑:檔首是 `/*`、下一行 `package notreal`、再 `*/`、最後才是真的 `package real` 時,收進去的是 `notreal`,真的 `real` 沒收。這是舊行為,但本輪重寫了這條正規式而沒處理。後果跟第一條同方向,漏收的套件讓那幾支被判不明、照跑。授權標頭裡出現這種行的機率低。
引句:「_CHOICE_COV_PKG_RE = re.compile(r"^[ \t\ufeff]*package[ \t]+([\w.`]+)", re.M)」

總結:最高等級是 minor
