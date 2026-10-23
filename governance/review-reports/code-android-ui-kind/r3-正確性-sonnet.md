severity: major

## 1. 新增的非 UTF-8 環境測試在 Linux 上必紅,CI(ubuntu-latest、Python 3.14)會擋下
severity: major
blocking: 是
引句:「env_c.update(LC_ALL="C", PYTHONUTF8="0", PYTHONCOERCECLOCALE="0", TP=str(fake))」
file: `scripts/test_lumos.py:18013`(`t_android_ui_attribution_receipt_rerun` 的 `env_c`;中文路徑 `trace-甲.bin` 在同函式的 manifest 寫入處)。重跑腳本相關行是 `scripts/templates/android-receipt-rerun.sh:57`,`subprocess.run([tp, trace, ...])`。
歸因:有證據的修復回歸。這支新測試與五處 UTF-8 修補都是這次修補才加的。
具體失敗場景:
- 輸入:manifest 的 artifact 路徑是 `trace-甲.bin`,環境是 `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`。
- 走到 `android-receipt-rerun.sh:57` 的 `subprocess.run([tp, trace, ...])` 時,POSIX 會用檔案系統編碼把 argv 編碼。
- Linux 在這組環境下的檔案系統編碼是 ascii,於是 `UnicodeEncodeError`。
- macOS 的檔案系統編碼固定是 utf-8,所以作者本機看不到。
- 修補的「中文路徑照樣比對相符回 0」在 Linux 上沒成立。

最小重現(我在 Linux 容器跑,`python:3.14-slim`,CI 同為 Linux 加 3.14):
- 把工作樹複製進容器,執行 `python3 scripts/test_lumos.py -k android_ui_attribution_receipt_rerun`。
- 結果:`✗ 非 UTF-8 環境:中文路徑、中文輸出、中文比對值照樣比對相符回 0  rc=1 ... UnicodeEncodeError: 'ascii' codec can't encode character '\u7532'`,最後 `3 passed, 1 failed`。
- 同一個測試在 macOS 的 `python3.14 scripts/test_lumos.py -k android_ui_attribution` 是 52 passed。

修前 46773fe6 沒有這支測試。同樣環境下的腳本會更早崩在 `NamedTemporaryFile` 的編碼,所以修前也不成立。這輪的差別是 CI 會因此變紅。

可行的修法(二選一):
- 測試把 `trace-甲.bin` 換成 ASCII 路徑,只讓中文出現在查詢輸出與比對值。
- 或拿掉 `PYTHONUTF8=0`,改用會真的讓 Python 退到非 UTF-8 的環境。
- 另外要承認:Linux 上只要檔案系統編碼是 ascii 或 Big5,而 manifest 路徑含中文,腳本還是會崩。這時要先把 trace 路徑改成可用 `os.fsencode` 編碼的形式,或在文件裡限定這種情況不支援。

## 已驗主張
- **沒收尾子樹**
  - 遞迴那步的 `WHERE s.dur >= 0` 搭配 `kids` 只算 `main`(`dur >= 0`),語意一致。
  - 兩種情境加總都等於幀長:沒收尾的區段底下有已收尾的後代,或同名區段在別處出現過。
  - 例:`doFrame 10 / traversal 5 / measure -1 / Compose:a 3` 得 (0, 0, 5, 5)。
  - 這個過濾也避開了「名稱在別處出現」的差異。
- **同分排序**
  - `ORDER BY SUM(self_ns) DESC, name` 沒問題。
  - `a.B` 與 `a.A` 同分取 `a.A`。
- **授權守衛前置**
  - 我在乾淨 clone 拿掉 `.sql` 的 SPDX 兩行,`t_license_headers_travel_with_vendored_files` 紅:`['scripts/templates/android-ui-attribution.sql']`。
  - 守衛仍然有效。`spdx_for` 的假檔名前置不依賴清單裡有沒有 `.sql`。
- **NULL 名稱、draw 只認框架名稱、自身時間取 0、註解不以分號結尾**
  - 這四項沒被這次修補弄壞。
  - `t_android_ui_attribution_inherit`、`pipeline`、`sums`、`receipt_rerun` 第一段在 macOS 都綠。
- **pitfalls manifest**
  - `android-receipt-rerun.sh:15` 的 `open(`:誤報。
  - 改動前後的 `json.load(open(...))` 都只讀一次,程式結束時直譯器會回收,沒有長跑累積。
  - `android-ui-attribution.sql` 五條 N+1:誤報。這是單一查詢裡的 CTE,不是迴圈呼叫。
- **圖譜固定席**
  - 這次只動範本、測試與 skill、筆記。
  - 授權與歸屬的 INVARIANT 由上面的守衛翻紅證實仍然綁得住。
  - 其他固定席的合約(search 預設、guard kill、re-inject 等)沒有牽連到這次改動的符號。
- **角色卡**
  - be-api-compat 和 be-authz 不適用:沒有 HTTP 端點、欄位或授權。
  - 唯一對外的合約是第一欄 `frame` 的字串鍵 `f<ts>`,沒變。

## 未驗範圍
- 沒有真的 `trace_processor`:`IS` 連接的效能和 `MAX(a, b)` 在 trace_processor 上的行為,只用 Python 的 sqlite3 驗過。
- 沒有逐一拿掉重跑腳本的五處編碼去驗翻紅。macOS 檔案系統編碼固定 utf-8,驗了也不代表 Linux。
- 沒有檢查 `docs/` 筆記內容。

## 三問
1. 原問題的修復效果:
   - 沒收尾子樹與同分排序兩項,有行為證據,且我獨立核對成立。
   - 編碼那項在 macOS 成立,在 Linux 不成立。測試本身在 Linux 變紅,所以「非 UTF-8 環境可重跑」目前有證據的部分只限 macOS。
2. 修補處的正常、錯誤與相鄰路徑:
   - 預設 UTF-8 環境、錯誤收據回 2、授權守衛、NULL 名稱與 draw 判定都仍成立。
   - 相鄰路徑裡,只有「非 UTF-8 加中文路徑」在 Linux 壞掉。
3. 新發現的案例修前、修後各是什麼結果:
   - 案例是 `LC_ALL=C PYTHONUTF8=0` 加中文 trace 路徑,在 Linux 上跑。
   - 修前:`NamedTemporaryFile` 寫入時 `UnicodeEncodeError`。
   - 修後:通過寫入,卻在 `subprocess.run` 的 argv 編碼處 `UnicodeEncodeError`。結果仍是崩潰,只是位置不同。

總結:最高嚴重度 major
