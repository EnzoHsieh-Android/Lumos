severity: major

## 1. 新增的 LC_ALL=C 測試在 Linux(CI 用的環境)是紅的,編碼修補沒有收完
severity: major
blocking: 是
引句:「UnicodeEncodeError」(取自修補自己貼的程式註解:非 UTF-8 的環境(LC_ALL=C)照系統預設編碼會在寫暫存檔或印結果時崩潰)
file: `scripts/templates/android-receipt-rerun.sh:9`、`scripts/test_lumos.py:18017`
歸因:有證據的修復回歸。修補自己新加的測試在 CI 環境是紅的,而它宣稱修好的缺陷在 Linux 上仍會崩潰。
具體失敗場景:
- 這個測試把 `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0` 並用「trace-甲.bin」這種中文路徑。
- macOS 的檔案系統編碼固定是 utf-8,所以在作者的機器上綠。
- Linux 上這組環境的檔案系統編碼是 ascii。`os.path.join(root, a['path'])` 產生的中文路徑傳進 `subprocess.run([tp, trace, ...])` 時會被 `os.fsencode` 拒絕。
- 修補加的 `reconfigure`、`open(..., encoding=)`、`NamedTemporaryFile(encoding=)`、`subprocess.run(encoding=)` 都管不到這一條。
- 失敗的是「讀 manifest 的中文路徑再交給外部程式」這一步,根本不是修補列的 5 處。
- 我用 `python:3.14-slim`(Linux,與 `.github/workflows/ci.yml` 的 ubuntu-latest 加 Python 3.14 同版本)重現:
  - 執行 `python3 scripts/test_lumos.py -k android_ui_attribution_receipt_rerun`。
  - 結果:`✗ 非 UTF-8 環境:中文路徑、中文輸出、中文比對值照樣比對相符回 0 rc=1 ... subprocess.py ... UnicodeEncodeError: 'ascii' codec can't encode character '\u7532'`。
  - 整體 `51 passed, 1 failed`。
- 修前(`46773fe6`)的腳本在同一案例也紅,錯誤是 `UnicodeDecodeError`。可見修補把錯誤往後推了一步,沒有收完。
- 推上去 CI 會紅。接手者在 Linux 專案(`LANG=C`)照 skill 跑 `rerun.sh`,碰到中文的 artifact 路徑或 manifest 仍會 Traceback。
- 最小修法:我把 `exec python3 -` 改成 `exec env PYTHONUTF8=1 python3 -`,同一個 Linux 容器內該測試 4 項全綠。
- 修前修後查證:
  - 命令:`git show 46773fe6:scripts/templates/android-receipt-rerun.sh` 放進 Linux 容器跑同一案例,結果是 2 項紅。
  - 命令:`e3ea2c16` 版在同一容器跑,結果是 1 項紅(中文路徑那項)。
- 上述兩個容器重現都是真跑出來的輸出,不是推論。

## 2. 驗收紀錄與計劃只寫「LC_ALL=C 原本會崩潰」,會讓接手者以為 Linux 已驗過
severity: minor
blocking: 否
引句:「`t_android_ui_attribution_receipt_rerun` 在預設與 LC_ALL=C 兩種環境各跑一次」
file: `docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md:51`
歸因:有證據的修復回歸。這是第 1 條的知識同步面。
具體失敗場景:
- 這句話宣稱兩種環境都驗過,但只在 macOS 上成立,Linux 上是紅的。
- 第 1 條修好後,這句話要補一個前提:CI 是 Linux,中文路徑要靠 UTF-8 模式才收得到。
- 查證命令:Linux 容器內跑 `-k android_ui_attribution_receipt_rerun`,結果是紅,證據同第 1 條。

## 3. 已確認一致、沒有發現的部分(供第三問參考)
severity: minor
blocking: 否
引句:「自身時間取 0」(計劃實務隱患節,行內寫著 `[test:t_android_ui_attribution_sums]`)
file: `docs/lumos-toolchain-knowledge/Projects/Android介面寫法分流_計劃.md:41`
歸因:未判定
- 這條沒有失敗場景,僅記錄我核對過的結果,不構成缺陷。
- **規則一致**:四類名單、draw 只認框架名稱、NULL 名稱跟祖先、沒收尾的子樹不走、自身時間取 0、同分照名稱排、註解不以分號結尾,在範本檔頭、計劃規則表與實務隱患、家節點、skill、reference.md 講法一致。
  - 唯一例外:範本檔頭沒寫 NULL、沒收尾、取 0、同分這幾條。這只是文字不全,不構成失敗。
- **測試各自守著規則**(我在臨時 clone 逐條拿掉實作,測試各自翻紅):
  - 拿掉 `WHERE s.dur >= 0`:`t_android_ui_attribution_sums` 紅,compose 3、pipeline 5、other 5,加總 13 大於幀長 10。
  - `IS` 改回 `=`:`t_android_ui_attribution_inherit` 紅。
  - 拿掉 `, name`:`t_android_ui_attribution_compose_fn` 紅。
  - `.sql` 檔頭兩行拿掉,或改成 `#`:`t_license_headers_travel_with_vendored_files` 兩種都紅。這補上了修補紀錄自己標的 uncovered。
- **指令與參數存在**:`lumos compose-metrics --audit`、`--repo`、`--json` 都在。skill 與 reference.md 的 `cp` 路徑和 `_VENDORED_TREE_FILES` 的登記都對得上。
- **Trace 重算未驗**:驗收紀錄寫的「三種注入 L1 增量不變」要實驗室 Trace,我這邊沒有 `trace_processor`,無法獨立核對,只能標為未驗。
- **措辭預期過期**:驗收紀錄 `valid_under` 寫「第二輪修正後的版本」。以後範本再動就要同步改,屬措辭精度。

## 三問
1. **修復效果有沒有行為證據?** G2-unfinished 有:拿掉 `WHERE` 就紅,補上就綠,兩種名稱出現情況都得 (0,0,5,5)。G2-test 的兩項(同分、授權前置)也有。G2-enc 只有一半:macOS 綠,Linux 紅(第 1 條)。
2. **修補處的正常、錯誤、相鄰路徑?** 正常路徑(預設環境、整份範本貼入)綠,收據寫錯回 2 且印中文原因也綠。相鄰路徑「Linux 加 ASCII 檔案系統編碼加中文 artifact 路徑」是上一輪沒人看的角落,現在是紅的。
3. **新發現的案例修前修後各是什麼結果?** 中文路徑加 `LC_ALL=C` 在 Linux:修前 `UnicodeDecodeError`(紅),修後 `UnicodeEncodeError`(仍紅)。加上 `env PYTHONUTF8=1` 後綠。

臨時目錄 `/private/tmp/lumos-seat-work/code-android-ui-kind/整合-sonnet` 已刪。我為了跑 Linux 容器啟動了 Docker Desktop,沒有關。

總結:最高嚴重度 major
