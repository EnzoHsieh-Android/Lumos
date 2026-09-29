severity: minor

## F1 --budget 給很大的有限數,守衛放行、--at 模式仍以 OverflowError 崩潰
severity: minor
blocking: 否 — 只有手打極端參數才會碰到,不影響推送閘,且有明確的一行修法
引句:「if not _m.isfinite(budget) or budget <= 0:」
1. 守衛註解自述要擋 inf 傳給 subprocess 逾時的 OverflowError,但只擋了非有限數;有限的大數照樣放行。
2. 重現(在 clone-ns 根目錄,唯讀):`python3 scripts/lumos drift scan --at HEAD --budget 1e10`
   輸出:traceback 尾端 `OverflowError: timestamp too large to convert to C _PyTime_t`(來源:_DriftProbeTree._read 把 max(1, deadline - monotonic()) 當 timeout 傳給 cat-file 的 subprocess.run)。
3. 對照:`--budget 1e5 --at HEAD` 正常;`inf`、`nan`、`-1`、`0` 都回「擋下」rc 2;`1e-9` 正常(全部判不了)。門檻約 9.2e9 秒(int64 奈秒)。
4. 預設(不帶 --at)走工作目錄,不開 subprocess,所以不崩;只有 --at 走 git 那條會崩。修法是把上限夾在合理值(例如 min(budget, 86400))。同機在 python3.9 與 3.12+ 都重現。

## F2 樹上只要有一支路徑含換行的程式檔,git 版的所有不帶路徑 symbol/test 條件永遠判不了
severity: minor
blocking: 否 — 條件極罕見(檔名含換行),且判不了會落到有單次略過出口的失敗保守方向;此行為不是這份差異新引入,但這份差異新增的 NFD 重讀與 prefetch 沿用同一條批次讀取
引句:「blobs = _drift_cat_nfc(self.root, self.where, todo, left)」
1. 輸入:提交的樹裡有 `src/a\nb.py`(用 hash-object + update-index --cacheinfo 造)與一般檔 `src/ok.py`。
2. 走到:corpus() 把全部程式檔一批交給 _read → _drift_cat_nfc → _nodehome_cat_blobs;後者「路徑裡有換行時批次讀取表達不了,整批當判不了」回 None。
3. 實測(git 版樹):`tree.one("symbol","ok_fn")` 回 None(判不了);移除換行檔後同一呼叫回 True。連帶 `nl_fn`、`bomfn` 等也都是 None。
4. 影響:drift check 把「判不了」算要處理(_drift_report_must 印「判不了就放行等於一條繞過的路,所以算要處理」),該專案只要有候選的不帶路徑條件就被擋,只能用 LUMOS_SKIP_DRIFT_CHECK=1。disk 模式不受影響(逐檔讀)。⚠ 未在完整 lumos 專案端到端重現,只在 _DriftProbeTree 層級重現。

## F3 型別點號限定名寫成 pkg.Class::method,新的路徑警告規則放過、條件永遠不成立
severity: minor
blocking: 否 — 只是漏警告,不會誤擋
引句:「if path in tree.files or "/" in path or re.search(r"\.[A-Za-z][A-Za-z0-9]*$", path):」
1. 輸入:`[when-symbol:app.Config::load][by:2030-01-01]`,樹上沒有名為 app.Config 的檔。
2. `_drift_probe_path_warn("symbol","app.Config::load",tree)` 回 None(不警告),`tree.one(...)` 回 False;對照 `Config::load` 有警告。
3. 原因:`.Config` 符合「字母開頭的副檔名」。Python 點號限定名、Java/C# 命名空間常這樣寫,結果是沒人看得到的死條件——這正是這條警告要抓的形狀。作者已知 Makefile 類的分不出來並寫進提示,這個形狀提示沒講。

## 其他已看,無 finding
- _probe_parse 正規化再驗:`.`、`./`、`./.`、`a/..`、`\`、` `(空)皆判錯;`a\..\b`→b、`src/`→src、`src//a.py`→src/a.py、`a/./b.py`、尾端斜線、NFD 與 NFC 兩種寫法都合法值不誤判;全形斜線不被當分隔(與樹上檔名一致,合理)。symbol 版 `./::x`、`a/..::x` 判錯、`a::x` 正常。已看,無 finding。
- _drift_decode / shebang:BOM 後接 #! 正確識別為 python 腳本;只有 BOM、空檔、UTF-16 BOM、非 UTF-8 位元組皆不崩(UTF-16 沒副檔名腳本靜默不進語料,Python 本來也跑不了,不標);200 字元邊界含多位元組字元(#! 加 198 個中文)不誤判,因為只看第一行且以字元切、不會切斷字元。已看,無 finding。
- _drift_cat_nfc:git 存 NFD、樹清單 NFC 時重讀成功(café.py 條件 True);兩種寫法都不存在回 None 不崩;路徑本身已是 NFD 不重試。已看,無 finding(換行路徑見 F2)。
- _drift_py_names:試了 NUL、語法錯、括號過深、深層巢狀 def/if/dict、極長 unary/not/lambda 鏈、lone surrogate、5000 位大整數、Python 2 語法、八進位舊寫法,在 3.9 與 3.12 都是回 None 或正常回集合,無一逃出例外(SyntaxError/ValueError/MemoryError/RecursionError 涵蓋得夠)。已看,無 finding。
- _drift_probe_path_warn 其餘案例:`v1.2::x`、`Makefile::x`、`foo.::x`、`Config::load`、`中文::x` 警告;`.env::X`、`a.B::c`、`src/v1.2::x`、`中文.py::x` 不警告,符合設計。
- 表態指令一種一行、--budget inf/nan/-1/0/1e-9 行為正確(大有限數見 F1)。_NotelinesNet 失敗編碼(git 失敗整次回 None)已讀,無 finding。

最嚴重等級 minor,blocking 共 0 條。
