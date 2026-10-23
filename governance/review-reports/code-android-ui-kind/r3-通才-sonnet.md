severity: major

## 1. 重跑腳本的 UTF-8 修補在 Linux 的 C 語系下仍崩潰,新測試在 Linux 上是紅的
severity: major
blocking: 是
引句:「重跑腳本 5 處編碼各拿掉一處都紅」
引句:「r = subprocess.run([tp, trace, '-q', f.name], capture_output=True, text=True, encoding='utf-8', errors='replace')」
file: `scripts/templates/android-receipt-rerun.sh:52`、`scripts/test_lumos.py`(`t_android_ui_attribution_receipt_rerun` 的 `trace-甲.bin` 那段)
歸因:有證據的修復回歸。修補自己加的測試在 Linux 上紅,而修補宣稱的修復效果在 Linux 上不成立。腳本把 manifest 裡含中文的 trace 路徑(UTF-8 解碼成 str)交給 `subprocess.run` 當參數,沒有處理檔案系統編碼。
失敗場景:這次修補只處理 stdin、stdout、stderr 和檔案內容的編碼,沒處理傳給子程序的命令列參數。macOS 的檔案系統編碼永遠是 utf-8,所以本機測試全綠。Linux 在 `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0` 下,檔案系統編碼是 ascii,`os.fsencode('甲')` 會拋例外。CI 在 `ubuntu-latest` 上跑。
最小重現(我用 `python:3.14-slim` 容器實跑):
- 在 `.lumos/receipts/x/` 放這份腳本。manifest 寫 `{"artifacts":[{"id":"t","path":"trace-甲.bin"}],...}`,`queries.sql` 帶一條 expect。
- 執行 `env -i LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0 TP=<假工具> sh rerun.sh`。
- 結果:`UnicodeEncodeError: 'ascii' codec can't encode character '\u7532'`,rc=1,有 Traceback。
- 直接跑測試:容器內 `python3 scripts/test_lumos.py -k android_ui_attribution_receipt_rerun`,結果是 `✗ 非 UTF-8 環境:中文路徑、中文輸出、中文比對值照樣比對相符回 0`、`3 passed, 1 failed`。
兩版查證:
- 修前:`46773fe6` 的腳本同樣用 `subprocess.run([tp, trace,…])`,Linux 下同樣崩(原有缺陷)。但那時沒有這條測試,CI 不紅。
- 修後:`e3ea2c16` 的 `-k android_ui_attribution` 在容器內是 51 passed、1 failed。同一組測試在 macOS 本機是 52 passed。
- 計劃筆記與 Verification 筆記都寫了「LC_ALL=C 的環境原本會崩潰」,現在對 Linux 是錯的。
建議修法:把命令列參數編成 bytes 傳進去,例如 `[os.fsencode(tp) ...]` 改成 `tp.encode('utf-8')`、`trace.encode('utf-8')`,或在腳本內先檢查可編碼性。

## 2. 重跑腳本沒有收據與 stdout 的 Python 下限說明(minor)
severity: minor
blocking: 否
引句:「sys.stdout.reconfigure(encoding='utf-8', errors='replace')」
file: `scripts/templates/android-receipt-rerun.sh:12`
歸因:有證據的修復回歸
失敗場景:`reconfigure` 需要 Python 3.7 以上。消費專案裡的 `python3` 若是 3.6 以下,原本能跑的收據重跑會變成 AttributeError。reference.md 只寫「需要 python3(標準庫)」,沒寫版本。⚠ 我沒能實測舊版 Python,影響面很小,只當提醒。

## 3. 其餘修補處的驗收(無新增問題)
- **未收尾子樹**:SQL 的 `tree` 遞迴加了 `WHERE s.dur >= 0`,`kids` 只加總已收尾的子區段。我讀完整條 CTE 鏈,沒找到破口。
- **未收尾子樹的測試**:`t_android_ui_attribution_sums` 在 macOS 與 Linux 都綠。
- **同分取名稱**:`ORDER BY SUM(self_ns) DESC, name` 有測試。
- **授權守衛**:`spdx_for` 按副檔名認註解符號,前置用假檔名驗,不依賴清單。`-k license_headers` 8 個全綠。
- **複製清單**:`_VENDORED_TREE_FILES` 已登記新 sql。`-k vendored_file_list` 5 個全綠。專案裡其他地方沒有另一份要同步的範本清單(搜 `android-receipt-rerun` 只出現在 `scripts/lumos`、測試、skill、reference 和筆記)。

## pitfalls manifest 逐條
- `android-receipt-rerun.sh:15` 的 `open(`:誤報。`json.load(open(...))` 是一次性腳本,行程結束就關,沒有長時間佔用。
- `android-ui-attribution.sql` 的 31、47、52、68、78 行(`SELECT…FROM`):全部誤報。這些行都在同一條遞迴 CTE 裡,不在迴圈內,沒有 N+1。

## 固定席筆記
- **授權與歸屬 INVARIANT**:新 sql 有 SPDX,沒把授權檔放進白名單,守衛仍然有效。
- **bound-tests-gate、guard-kill、lumos-cli 等**:與這次改動無直接牽連。

## 三問
1. **修復效果的行為證據**:G2-unfinished 在 macOS 和 Linux 都成立。G2-enc 只在 macOS 成立,Linux 下只有 manifest 路徑含中文的情況仍崩(見第 1 條)。G2-test 成立。
2. **修補處的正常、錯誤、相鄰路徑**:相鄰路徑(trace 路徑含非 ASCII,且 Linux 檔案系統編碼是 ascii)沒被覆蓋。新測試在這條路上就是紅的。
3. **新發現案例的修前修後**:第 1 條在修前和修後都崩(原有缺陷)。修補新增的測試讓 Linux CI 從綠變紅。

總結:最高嚴重度 major
