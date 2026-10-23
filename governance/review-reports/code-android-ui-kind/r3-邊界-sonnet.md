severity: minor

審查範圍:修補差異 46773fe6..e3ea2c16。我用 python3 sqlite3 在臨時目錄造假表,並用假 trace_processor 跑重跑腳本,臨時目錄已刪。

**修補驗收**
- **沒收尾區段的修補有效。** 我造了這幾種輸入,四類加總都等於幀長:
  - 沒收尾的 measure 底下掛 layout(也沒收尾)再掛已收尾的 measure,結果是 (0,0,3,7),加總 10。
  - NULL 名稱區段底下有沒收尾的 inflate 和已收尾的 inflate,結果是 xml 2、other 8。
  - 沒收尾的函式區段是葉子。
  - 沒收尾的幀直接不輸出。
  - 幀掛在沒收尾的 Looper 底下,結果是 (0,0,4,6)。
  - 空表和 dur 0 的幀不崩。
- **同分決勝正常。** 大小寫不同的 `a.B` 與 `A.B` 同分時取 `A.B`,二進位排序,結果確定。NULL 名稱不會進 `fn`,因為 `is_fn` 對 NULL 為假。
- **規模正常。** 2000 幀、20 萬個區段、500 種名稱,約 0.8 秒,`IS` 連接沒有造成平方級的慢。
- **編碼修補有效。** 我在 `LC_ALL` 設為 C、POSIX、空字串、`zh_TW.Big5`、`en_US.ISO8859-1` 五種環境下試過。中文 session 名、中文比對值、中文 stderr 都回 0。中文值不符回 1,收據寫錯回 2 並印出中文原因。

## 1. queries.sql 開頭帶 BOM 時,第一條查詢被靜默丟掉,即使它比對不符整體仍回 0
severity: minor
blocking: 否
引句:「heads = re.findall(r'^--\s*\[(Q\d+)\]', text, re.M)」
file: `scripts/templates/android-receipt-rerun.sh:19`
歸因:有證據的原有漏查。修前 `46773fe6:scripts/templates/android-receipt-rerun.sh:14,16,19` 的讀檔和兩條正則跟修後逐字相同,修補沒碰這一段。
場景:
- 重現:`queries.sql` 開頭有 UTF-8 BOM,Q1 寫 `expect=f1:compose_ns=999`、Q2 寫 `expect=f1:compose_ns=5`,假 trace_processor 回 5。
- 無 BOM:印 `BAD Q1`、`OK Q2`,rc=1。
- 有 BOM:只印 `OK Q2`,rc=0。
- 原因:`^` 配不到 `\ufeff-- [Q1]`,`qs` 和 `heads` 兩邊一起漏掉 Q1,「標頭數等於條數」的檢查因此照過。
- 單條查詢帶 BOM 時,會落到「沒有任何一條帶 expect」而回 2,所以這個假過只發生在多條查詢時。
- 修法:改用 `encoding='utf-8-sig'` 讀。

## 2. manifest.json 帶 BOM 時整支腳本以 traceback 結束,不是「收據寫錯」的 rc 2
severity: minor
blocking: 否
引句:「man = json.load(open(f'{here}/manifest.json', encoding='utf-8'))」
file: `scripts/templates/android-receipt-rerun.sh:15`
歸因:未判定。這行是修補新加的 `encoding='utf-8'`,但修前不指定編碼時,UTF-8 環境下同樣會因 BOM 丟 `JSONDecodeError`,所以我判斷不是修復回歸。我沒有在修前版本實跑。
場景:
- 我在修後版本實跑,BOM 的 manifest 丟出 `JSONDecodeError: Unexpected UTF-8 BOM`,腳本沒有走到回 2 的收據錯誤處理。
- 腳本檔頭宣告「收據本身寫錯回 2」,但實際結束碼是 Python 未捕捉例外的 1,跟「比對不符」混在一起。
- 修法:用 `utf-8-sig` 讀。

## 3. 授權守衛的副檔名判斷區分大小寫
severity: minor
blocking: 否
引句:「return _spdx_sql if f.endswith(".sql") else _spdx」
file: `scripts/test_lumos.py:53904`
歸因:有證據的原有漏查。這個分派函式是本次 diff 新增的,從來沒處理過大寫副檔名,不是修補才引入。
場景:
- 若有被複製的範本叫 `x.SQL`,會被要求用 `#`,而 `--` 的正確標示反而判為缺標示。
- 目前清單裡只有小寫 `.sql`,所以沒有現行失敗。
- 失敗方向是多擋,不會放行沒標示的檔。
- 修法:`f.lower().endswith(".sql")`。
- 沒有副檔名的檔走 `#`,合理。

## pitfalls manifest 逐條判斷
- `scripts/templates/android-receipt-rerun.sh:15` 的 open():**誤報**。這是一次性腳本,開檔只讀一次,程序結束即釋放,沒有迴圈。
- `scripts/templates/android-ui-attribution.sql:31, 47, 52, 68, 78` 的 N+1:**全部誤報**。這幾行是 CTE 內的 `SELECT ... FROM`,沒有應用層迴圈,是單一查詢。遞迴 `tree` 走的是整體連接,上面的規模測試也顯示沒有退化。

## 圖譜鏡頭
- 固定席各條 INVARIANT 牽連的是 `scripts/lumos` 與 `scripts/test_lumos.py`。授權與歸屬那條要求「每支被複製的檔至少有 SPDX 註解行」,修補後的前置斷言直接驗了 `.sql` 與 `#` 檔兩個方向。
- 缺口:修補紀錄自承「這輪沒有再對 .sql 拿掉 SPDX 行驗一次紅」。
- 其餘固定席節點(lumos-cli-read、guard-kill、bound-tests-gate、design-loop、lifecycle 等)與這份 diff 無實質牽連,我沒發現被破壞的跡象。
- 備援段的表態記錄沒有逐條核對。

## 最後三問
1. 沒收尾區段的修補在各層(幀、中間、葉子、連續多層、NULL 名稱底下)是否都收斂?是,四類加總恆等於幀長。
2. 編碼修補在 locale 邊界是否站得住?C、POSIX、空字串、Big5、ISO8859-1 都站得住。BOM 與 CRLF 的另外兩個洞是原有的,不是修補造成的。
3. 修補有沒有引入新問題?沒有證據顯示有。

總結:最高嚴重度 minor
