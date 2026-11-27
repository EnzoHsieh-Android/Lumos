severity: clean

這輪修補我看過,沒有會做錯事的地方。

**修補 ① 的驗收**(`_KillCompile.units()` 擋 .git 底下的路徑)
- `".git" in (x.lower() for x in Path(...).parts)` 對產生器做 `in` 是逐項比對,語法與語意都對。
- `sub/.GIT/y.kt`、`.GIT/…` 的路徑每段轉小寫後等於 `.git`,會被擋。一般檔(`A.kt`)的路徑段不會誤中。
- 新案例 H 的檔 `sub/.GIT/y.kt` 真的建在暫存工作樹裡,所以 `realpath` 在區分大小寫的檔案系統上也會落到那個路徑,改回舊寫法時 H 會被收進合批,測試會變紅,抓得到改壞。
- `python3.14 scripts/test_lumos.py -k choice_compile_units_guards` 實跑 1 passed。

**修補 ② 的驗收**(`Systems/規格閘` 那條 REVISIT 改成日期型)
- 格式是 `REVISIT:YYYY-MM-DD 一句要做什麼`,符合專案規定。
- 先前「寫下就成立」的問題已經消除。

**同類位置**
- `scripts/lumos:14917` 與 `scripts/lumos:14933` 是另一個功能(plan 路徑判斷)。前者已經有 `.lower()`。
- 後者 `os.path.join(root, ".git")` 區分大小寫,但它只影響提示字樣,不在這次 diff 內,也不會做出錯的行為,所以不報。

總結:最高等級是 clean
