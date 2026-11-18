severity: major

## g1 撤號守衛只把「已撤列號」那一側正規化，表裡的列號寫成前導零或全形數字照樣漏過
severity: major
blocking: 是——撤號守衛可被繞過而測試照綠，被保護的是計劃範圍 4 的「列號不重用」。

這次修補（r3 b1）只把 `_choice_retired` 收緊成 `C-[1-9][0-9]*`。比對另一側沒動：表列的辨識 `_CHOICE_ROW_RE = r"^\|\s*C-\d+\s*\|"`，在 Python 3 的 `str` 正規式裡 `\d` 會收全形數字和前導零。

- 輸入：型錄寫 `已撤列號:C-40`，表裡新增一列 `| C-040 | …`，或 `| C-４０ | …`。
- 路徑：`choice_tables` 到 `_choice_retired_problems`，用 `r["id"] in retired` 做字串比對。
- 預期：擋下「列號不准重用」。
- 實際：`C-040` 和 `C-４０` 兩列都回 `[]`，同一個撤號編號靜默重用。`C-40` 本身仍正常被擋。

修補只補了「撤號行寫成全形或前導零」，沒補到「表列寫成全形或前導零」。新增的三條測試（全形、前導零、混合）都只動撤號行。

引句:「ids = re.findall(r"C-[1-9][0-9]*", val)」
file: `configs/ast-grep/kotlin-android/check.py:1389`（`_CHOICE_ROW_RE` 仍是 `C-\d+`）

重現指令（在臨時副本裡跑 `choice_tables(_CB2_SYN_CAT.format(retired="C-40", extra=row))`）：

| 表裡的列號 | 修前 87093835 | 修後 59c41038 |
|---|---|---|
| `C-40` | 擋 | 擋 |
| `C-040` | `[]`（漏） | `[]`（漏） |
| `C-４０` | `[]`（漏） | `[]（漏）` |

歸因：有證據的原有漏查。兩版結果相同，這次修補沒造成回歸，但它宣稱收回的「撤號守衛靜默漏擋」在表列這一側仍然存在。
最小修法：表列正規式也改成 `C-[1-9][0-9]*`，並讓不合格的列號報錯。這樣表列、規則 id、樣本標記三處用同一條規則。

## 圖譜鏡頭（固定席逐條判）
- `Systems/kotlin規則包.md`：影響，且就是 g1 所在的家。牽連檔有 `check.py` 和 `test_lumos.py`，撤號守衛的合約落在這裡。
- `Systems/bound-tests-gate.md` 的 ★INVARIANT★：不影響。這次沒動閘的邏輯，只動了 `check.py` 的正規式與測試內容。
- `Systems/guard-kill.md`、`lumos-cli-lifecycle.md`、`測試假綠形態.md`、`lumos-cli-read.md`：不影響，改動沒碰到它們的合約主題。
- `pitfalls-code-loop.md`、`loop-convergence-recording.md`：不影響，`scripts/lumos` 的流程沒有改動。
- 殘留與 `residual-ask`：鏡頭算不出來。diff 裡沒有 `residual-index.json` 或治理帳的變動，無從判斷，如實標未判定。

## 三問（含證據）
1. **原問題修復效果**
   - claim：撤號行寫成全形或前導零時，不再靜默放過。
   - input：`已撤列號:C-４０`、`C-040`、`C-４0`，表裡有 C-40。
   - expected：報「已撤列號那一行要寫…」。
   - before/after：修後 `-k choice_table_batch2` 16 項全過，三條新增斷言在內。修前沒有這三條斷言，未判定修前的實際輸出。
   - comparison：只驗了撤號行這一側，表列那一側見 g1。
2. **相鄰路徑是否仍成立**
   - claim：C-34、C-36、C-37 的樣本新增行與既有行都成立。
   - input：`-k choice_samples_batch2`、`-k choice_table_batch2`。
   - expected：全過。
   - after：16 passed, 0 failed。
   - before：沒跑。
   - comparison：修補沒動規則 yml，只動樣本與 check.py 的撤號判斷，既有行為沒有被改動的證據。
3. **新發現的同一案例修前修後**：見 g1 的表，兩版相同。

**未驗範圍**：
- 沒逐條拿掉規則子句做變異（這是編排者手動掃描的部分）。
- 沒驗括號包住的常數 key 與引數巢狀的輸出平方成長，這兩條 r3 已放行。
- 沒驗 `lumos lint-new`、型錄全檢查。

其他角度逐行、被刪行為、重用、簡化、效率、慣例都沒找到有具體失敗情境的候選。

最嚴重:major;blocking 共 1 條
