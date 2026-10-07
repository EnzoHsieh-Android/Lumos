severity: major

FINDING R2-RESOURCE-01：觀察成立，但只能歸因為回歸守衛缺陷

severity: major
blocking: 是

引句：「這個測試吞掉 `DataError`，卻沒有在沒丟錯時失敗」

file: `governance/review-reports/code-review-convergence-eval/r2-resource.md:13`  
file: `governance/eval/test_review_convergence.py:175`  
file: `governance/eval/test_review_convergence.py:178`  
file: `governance/eval/test_review_convergence.py:187`

1. agree／假綠：成立。

固定版本 `c909bf980125dc90f1696372205e322e2ac877c7` 的迴圈只處理「有丟出 `DataError`」的情形；目錄呼叫正常回傳時不會失敗。唯一後續斷言只是正常檔案仍回傳 `fixed-payload`。

局部記憶體實驗直接抽取固定 blob 內嵌腳本，令目錄呼叫回傳 bytes、正常呼叫回傳 `fixed-payload`，結果為：

`exact_script_pass=True directory_calls=80 directory_exceptions=0 normal_calls=1`

因此「正常檔案仍可讀」不能反證假綠；80 次目錄均未被拒絕時，原測試確實仍通過。

2. agree／現場斷言合約：違反。

引句：「修 bug 的「還原翻紅釘」必須配一條**前置斷言證明現場成立**(被測那條路真的被執行到)」

file: `governance/review-reports/code-review-convergence-eval/r2-graph-lens.txt:12`  
file: `governance/eval/review_convergence.py:29`  
file: `governance/eval/review_convergence.py:34`

描述符修補針對的現場是「非一般檔案被拒絕後，例外路徑關閉 fd」。測試沒有拒絕次數、沒有 `else` 失敗，也沒有任何等價前置斷言。嘗試以最後的正常檔案讀取推翻判準失敗：該斷言只能間接檢查 fd 尚可使用，不能證明非一般檔案拒絕分支曾被執行。

3. concern／修補造成產品回歸：不能成立。

file: `governance/eval/review_convergence.py:24`  
file: `governance/eval/review_convergence.py:29`  
file: `governance/eval/review_convergence.py:33`  
file: `governance/review-reports/code-review-convergence-eval/r2-resource.md:21`

固定模組在 `fstat` 判定非一般檔案後丟出 `DataError`，並由例外路徑關閉 fd。以固定模組原文做記憶體內 I/O 替身實驗，得到：

`result=DataError:nonregular-input events=[('open', '.'), ('close', 41)]`

這證明固定版本的相關產品路徑在該條件下是「拒絕且關閉」。真實 before 證據只有測試不存在，不能當作產品 before 失敗，也不能建立產品行為退化。可歸因本輪修補的是「新增測試違反硬合約、可假綠」；不可稱為「修補造成產品回歸」。

裁決：維持 major／blocking，但阻斷理由僅是硬合約下的回歸守衛失效，不是已證實的產品回歸。所有實驗均由固定 Git blob 經 stdin 在記憶體執行，未落檔、未外呼，亦未採用後續作者修補作為證據。