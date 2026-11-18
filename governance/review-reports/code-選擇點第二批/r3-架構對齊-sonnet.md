severity: clean

本席只判「跟既有做法一不一致」。這份修補沒有不一致,所以零 finding。

## 三問答覆

**1. 分層與依賴方向:對齊。**
- `scripts/lumos` 的改動只在 `_render_gov_choice` 內,排序鍵換成 `_row_key`。它仍透過 `_gov_choice_by_row`(`scripts/lumos:17925`)取表,沒有另外讀帳,依賴方向不變。
- `api.yml` 新增的 `value-direct` 以 `matches: value-pos` 疊在既有 util 上,沒有重寫判斷。`value-pos` 仍與 `sbr.yml:13` 一字不差,`t_choice_samples_batch2` 的 S6 比對通過。
- 把共用片段各抄一份,是這批規則本來的做法(ast-grep 的 utils 只在同一份規則文件裡有效)。C-36 與 C-37 兩份 `literal-arg` 的新分支內容相同,延續這個做法。
- `nthChild` 搭配 `reverse` 與 `has`,是 `value-pos` 已經用過的組合,沒有新語法。

**2. 命名與錯誤處理:對齊。**
- `_row_key` 是巢狀 helper,命名同 `scripts/lumos:16608` 的 `_bk`,render 函式內放巢狀 helper 在 repo 有多處先例(`scripts/lumos:3479`、`scripts/lumos:10013`)。
- 錯誤處理是回退到 `10**9`,與修前的做法一致,沒有新增 rc 或訊息路徑,也沒有帳本事件。
- 附帶一點:`scripts/lumos:18033` 同區的排序鍵用 `isdigit` 沒有長度上限,但它排的是工具自己產生的列號,不是帳本裡可被塞入的字串,不在本次差異內。我判不影響,不列。

**3. 第二種做法:沒有。**
- 沒有新讀帳方式、放行檔格式或隔離工作樹。
- `value-direct` 是在原判斷上加一層,不是另一套判斷。
- 樣本沿用 `// HIT C-xx` 與 `// MISS C-xx` 格式。樣本裡用到沒定義的 `d`,與既有樣本用未定義的 `go()`、`done()` 一樣,只有 ast-grep 會讀,不編譯。

## 圖譜鏡頭
鏡頭計算超時,派工詞允許不補算。我沒有讀圖譜節點,所以沒有針對圖譜固定席逐條判。

## 修補鏡頭與歸因
- 原問題的修復效果:本席不查規則行為本身,那是正確性席的範圍。結構上,`value-used` 全部改引用 `value-direct`,與「巢狀分支一律當不確定」的目的一致。
- 相鄰路徑:`sbr.yml` 沒動,C-18 與 C-34 的 `value-pos` 比對仍綠。
- 已跑,在修後版本 `87093835` 的臨時 clone 上:
  - `python3.14 scripts/test_lumos.py -k choice_samples`:33 passed,0 failed,含 `t_choice_samples_batch2`(每個 HIT 都中、每個 MISS 都沒中)。
  - `python3.14 scripts/test_lumos.py -k choice_by_row`:6 passed,0 failed,含 `t_gov_stats_choice_by_row`。
- 未驗:修前版本 `6cc9ad8c` 沒有開 worktree 對照。原因是零 finding,沒有需要比較修前修後的新發現。因此「已修復」只有修後測試通過的證據,不能證明回歸或修復因果,歸因「未判定」。
- 另一個未驗項:`_row_key` 在超過 4300 位數字列號下確實不丟例外,我沒有實跑。
- 臨時目錄已用字面絕對路徑刪除。

最嚴重:clean;blocking 共 0 條
不對齊共 0 條,其中 major 0 條
