severity: clean

**鎖檢查**：`/Users/enzo/.cache/lumos/dispatch-lens/170757806b0583f77f6270f87c61e53d00f5d3ae4258a1121b929ce0d3d7f2dc.json.warming` 不存在（ls、cat 都回「No such file」），沒有東西要刪，沒動鎖。圖譜鏡頭改讀備份 `/tmp/lumos-seat-work/code-選擇點第二批/lens-r4.txt`。

## 三類逐項

- **①提示注入：已看，無。**
  - `gov --stats` 新增的「依列號」小節會把帳本欄位（`row`、放行理由標籤）印出來給 AI 讀，列號走 `_kill_esc(row)[:20]`，標籤走 `_kill_esc(w)`。
  - 放行標籤沒截長度，但標籤是既有欄位，這輪沒有新增注入面，也沒有攻擊路徑。
- **②讀寫與執行越界：已看，無。**
  - 新讀檔只有 `_choice_sample_marks` 對 `<rules_dir>/samples/*.kt` 的 glob，以及 `choice_rule_ids` 讀 `rules-choice/`。路徑來自 repo 內固定的 `CHOICE`，沒有外來路徑，也沒有 shell 插值、下載或環境變數覆蓋。
  - 新增的 `!!`、`?:` 編輯只產生給差異式變異測試用的壞法，輸入是 repo 自己的原始碼。
  - 新增程式、範本與文件裡沒有新寫的密鑰或信箱。
- **③非刻意繞過守衛：已看，無。**
  - 撤號守衛 `_choice_retired` 的正規式原本用 `\d`，會收全形數字與前導零。照常寫成 `C-040` 或 `C-４０` 時，字串比不上表裡的 `C-40`，守衛會靜默漏擋。
  - 修後改成 `C-[1-9][0-9]*`，這兩種寫法會報「已撤列號那一行要寫…」，不再靜默放過。
  - 「撤掉列號後又用另一種寫法重用列號」屬刻意換編號，歸範圍外。

## 圖譜鏡頭

- **kotlin規則包、bound-tests-gate、guard-kill、lumos-cli-lifecycle、lumos-cli-read、測試假綠形態**：不影響。改動都落在 `check.py` 的選擇點表讀取與撤號檢查，以及 `scripts/lumos` 的 `gov --stats` 選擇點段。沒碰 re-inject sentinel、搜尋過濾，也沒碰 guard kill 的 rc 優先序與 JSON 純度。
- **pitfalls-code-loop、loop-convergence-recording**：不影響。沒改這兩處的程式路徑。

## 三問

- **①原問題的修復效果**：本席只核對了其中一項（全形數字與前導零的撤號寫法，看 r3 b1 是否補好）。
  - claim：`已撤列號:` 行寫成全形數字或前導零，修前被當成另一個列號而漏擋，修後報錯。
  - input：`_choice_retired` 吃 `C-４０`、`C-040`、`C-0`，另以 `C-40`、`C-40、C-41`、`C-10` 當對照。
  - expected：全形、前導零與 `C-0` 報錯，半形正常寫法照收。
  - before（87093835）：`C-４０`、`C-040`、`C-0` 都被收成 `{'C-４０'}`、`{'C-040'}`、`{'C-0'}`，rc 無問題，也就是會漏擋。
  - after（59c41038）：這三種都回 `(set(), '已撤列號那一行要寫…')`，`C-40`、`C-10` 與 `C-40、C-41` 照常解析。
  - comparison：修前靜默放過、修後報錯，修復成立。
  - 驗證指令：`python3.14 -I exp.py <before 或 repo 路徑>`；`python3.14 scripts/test_lumos.py -k choice_table_batch2` 結果為 16 passed、0 failed。
- **②修補處的正常、錯誤與相鄰路徑**：
  - 正常：`C-40`、`C-10`、`C-40、C-41` 都照常解析，見上面的對照結果。
  - 錯誤：全形、前導零、`C-0` 都有明確的報錯訊息。
  - 相鄰：「前面帶清單符號、多寫一行、粗體、縮排」這幾條路徑在 `choice_table_batch2` 的案例裡仍綠。
  - 本席沒有另外重驗「樣本標記指向不在表裡的列號」那條路。
- **③新發現的同案例前後結果**：沒有新 finding，不適用。

**未驗範圍**：沒跑不帶 `-k` 的全套，也沒跑 ast-grep 實際掃樣本；變異編輯的語意正確性屬別席。

最嚴重:clean;blocking 共 0 條

已用字面絕對路徑刪掉 `/private/tmp/lumos-seat-work/code-選擇點第二批/資安-sonnet`（自己建的副本與 worktree）。
