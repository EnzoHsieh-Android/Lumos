severity: minor

我在 macOS(Python 3.14.6)與 `python:3.14-slim` 容器各跑一次 ab35a0f8 的 `-k android_ui_attribution`(54 個)、`-k android_evidence`(7 個)、`-k license_headers`(8 個),都全過。圖譜面的核對也沒問題:筆記指到的測試名都存在,計劃 lint 0 問題,範本已登記進 `_VENDORED_TREE_FILES`。

收據流程本身沒撞牆,有的是文件與實測對不上的地方。我另外手動驗了「修前版腳本」與「修後版腳本」在 `LC_ALL=C` 下的行為,見第 1 條。

## 1. 「LC_ALL=C 會崩潰」的根因寫錯,測試模擬的是另一種環境
severity: minor
blocking: 否
引句:「Linux 在 LC_ALL=C 下檔案系統編碼是 ascii,傳給分析工具的中文路徑在參數編碼那一步就失敗」
file: `docs/lumos-toolchain-knowledge/Projects/Android介面寫法分流_計劃.md:34`、同檔 `:68`(「範本帶中文,LC_ALL=C 的環境原本會崩潰」)、`scripts/test_lumos.py:18013`(「非 UTF-8 的環境(LC_ALL=C)」)
歸因:有證據的原有漏查。這句根因是這輪修補才寫進筆記的;修補前的腳本也沒在 `LC_ALL=C` 下崩潰,見下方證據。

照這句做會出錯的地方:接手者讀到「根因:LC_ALL=C 下 ascii」,會以為只要 `LC_ALL=C` 就會崩。實測不是這樣。

- Python 3.7 以上遇到 C/POSIX 語系會自動開 UTF-8 模式(PEP 540)。
- 容器內用修前版腳本(`git show e3ea2c16:scripts/templates/android-receipt-rerun.sh`)、`env -u LANG LC_ALL=C`、中文路徑與中文比對值:結果是 `OK Q1 ... rc=0`,沒有崩潰。
- 只有再加 `PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`,修前版才報 `UnicodeEncodeError: 'ascii' codec can't encode character '\u7532'`,rc=1。
- 修後版(`ab35a0f8`)在同樣兩種環境都回 rc=0。

測試是靠強制 `PYTHONUTF8="0"` 與 `PYTHONCOERCECLOCALE="0"` 才讓拿掉 `PYTHONUTF8=1` 後翻紅。護欄本身有效,它擋的是「UTF-8 模式被關掉或編碼不是 UTF-8 的語系」。但 PITFALL 的 `[根因:]` 與測試註解把它說成 `LC_ALL=C`,是不實的因果。接手者之後若看到「CI 在 LC_ALL=C 下崩潰」,會被誤導去查錯方向。

建議把根因改寫成「UTF-8 模式被關掉或語系編碼不是 UTF-8(例如 `PYTHONUTF8=0`、`en_US.ISO-8859-1`)」,並註明 3.7 以上的 `LC_ALL=C` 本來就會自動進 UTF-8 模式。

## 2. 回傳碼 2 的語意只在 reference.md 和家節點第二段更新,其餘四處還是舊的
severity: minor
blocking: 否
引句:「2 收據本身寫錯(標頭沒被解析到、一條 expect 都沒有、manifest 列的查詢不在檔裡、查詢指到不存在的 artifact 或 requires)」
file:
- `docs/lumos-toolchain-knowledge/Systems/macrobenchmark-adapter.md:49`(同一節點第一段;第二段已補「分析工具執行不了回 2」)
- `scripts/templates/android-receipt-rerun.sh:5`(檔頭「全部相符回 0、比對不符回 1、收據本身寫錯回 2」)
- `skills/lumos-android-evidence/SKILL.md:138`(「回 2 是收據本身寫錯,照它印的原因修」)
- `docs/lumos-toolchain-knowledge/Projects/Android逐層診斷_計劃.md:67`(S10:「收據本身寫錯時應回 2」,綁 `t_android_evidence_rerun_refuses_empty`)

歸因:有證據的修復回歸。e3ea2c16 沒有「分析工具執行不了回 2」,ab35a0f8 新增它,但只更新了 reference.md 與家節點第二段。

照做的失敗場景:
- 照 SKILL.md:138 跑 `rerun.sh`,環境沒裝 `trace_processor` 也沒設 `TP`,得到 rc=2。
- SKILL 說「回 2 是收據本身寫錯」,接手者可能去改 `queries.sql` 或 `manifest.json`。stderr 其實印的是「擋下:執行不了分析工具 … 用 TP=… 指定」,會把人導回正確處,但文件彼此矛盾。
- 「分析工具執行不了回 2」這條只被 `t_android_ui_attribution_receipt_rerun` 守著。改 `rerun.sh` 的人看 S10,不會知道還有這支測試綁了它。
- 檔頭的 Python 3.7 要求也只在腳本內的 shell 註解和 reference.md 有,家節點與計劃沒寫。這個差異很小。

## 3. L1 判讀用的「四類總和」只存在人工加總,重跑腳本無法驗證
severity: minor
⚠
blocking: 否
引句:「比兩邊 triage 挑出的卡頓幀(挑不出就用全部的幀)四類總和」
file: `skills/lumos-android-evidence/SKILL.md:55`(「兩邊的四類數字寫進 `why_escalated`」在同段第 4 點);`scripts/templates/android-ui-attribution.sql:94`(輸出是每幀一列)
歸因:有證據的原有漏查。這是新增流程的設計缺口,不是這輪修補引入的。

失敗場景:
- 查詢輸出每幀一列,`expect` 只能釘單一幀 `f<幀起點>:compose_ns=…`。
- SKILL 要求依「跨多幀四類總和、哪一類長最多」分流,並把總和寫進 `why_escalated`。這些總和沒有任何查詢輸出,是 AI 手動加總。
- 三個月後的接手者跑 `rerun.sh` 回 0,只證明那一幀對得上,不證明「Compose +6793ms」這種分流依據。
- 驗收紀錄 S9 寫的就是這類跨幀總數。
- 我沒有實驗室 Trace,所以不能證明這在實務上會造成誤判;只是此處的可重跑性比文件暗示的弱。

## 已核對、沒問題
- 兩個 rc=0/1/2 測試(`t_android_evidence_rerun_refuses_empty` 與 `t_android_ui_attribution_receipt_rerun`)在 macOS 與 Linux 都綠。
- 收據檔頭兩處 BOM 分開拿掉會各自翻紅,依程式邏輯推演;我沒有逐一實跑變異。
- 分析工具不存在時:`except OSError` 回 2,`finally` 刪暫存檔。測試用 `TMPDIR` 檢查暫存目錄是空的,這條有效。
- 範本整份貼進 `queries.sql`:全檔只有 `ORDER BY f.ts;` 一行以分號結尾,不會被截斷。
- `{{NAME}}` 由 lumos 替換(`note-audit-reread.md` 等)、`__NAME__` 由 AI 手動替換,reference.md 的這段說明與實況一致。
- 驗收紀錄 `valid_under` 寫「第二輪修正後的版本」。第三輪修補沒動 `android-ui-attribution.sql`(`git diff e3ea2c16 ab35a0f8` 不含它),範本與紀錄對得上。

回答三問:
1. 修復效果:UTF-8 模式、BOM、工具不存在回 2 三項在兩個環境都有效。第 1 條提到的是文件對根因的描述不實,不是修補無效。
2. 修補處的相鄰路徑:正常、錯誤、`TP` 不存在、CRLF、含中文路徑都沒發現新壞處。
3. 新案例在修前修後的結果:
   - 案例:`LC_ALL=C`(不強制關 UTF-8 模式)。修前 rc=0,修後 rc=0。
   - 案例:`PYTHONUTF8=0`。修前 rc=1 並噴 `UnicodeEncodeError`,修後 rc=0。

總結:最高嚴重度 minor
