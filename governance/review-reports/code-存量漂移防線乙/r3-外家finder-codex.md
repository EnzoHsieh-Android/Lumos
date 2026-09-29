severity: major

## F1 深層 Python 輸入在必要的 Python 3.9 執行環境直接殺死程序

severity: major  
blocking: 是 — `drift scan/check` 可被合法大小的受控原始碼以 SIGSEGV 終止，新增的例外處理沒有兌現防當機目的。  
引句:「+    except (SyntaxError, ValueError, MemoryError, RecursionError):」  
file: `scripts/lumos:25855`

1. 放入含 `foo` 且有 500,000 個一元負號的 `.py`；`_defines` 先命中名稱，再進 `_ast.parse`。必要執行環境 Python 3.9 在拋出可捕捉例外前已崩潰。
2. 最小重現：

   ```sh
   /usr/bin/python3 -c "import runpy; d=runpy.run_path('scripts/lumos',run_name='review'); T=d['_DriftProbeTree']; t=object.__new__(T); t._text={'x.py':'# foo\n'+'-'*500000+'1\n'}; t._py={}; print(t._defines('x.py','foo',False))"; echo rc=$?
   ```

   輸出：

   ```text
   rc=139
   ```

3. `MemoryError`／`RecursionError` 的 Python 層捕捉接不到 SIGSEGV；帶路徑或不帶路徑的 `when-symbol:foo` 都能走到這條路，整個檢查程序死亡。

## F2 候選條件的 OR 判定遇到 unknown 就提前停止

severity: minor  
blocking: 否 — 最終仍 fail-closed，但本可確定且可逐行表態的 finding 被錯報成不可表態的全域判不了。  
引句:「+        if hit is None or hit:」  
file: `scripts/lumos:26094`

1. 候選規則是「任一條件受這次推送影響」；前一個條件為 `None`、後一個條件為 `True` 時，整行候選結果應為 `True`。
2. 現在遇到第一個 `None` 就回傳，完全不看後面的確定命中。例如修改一支讀不出的程式檔，同時新增 `[when-file:x.txt]` 指定的檔案。
3. 最小重現：

   ```sh
   /usr/bin/python3 -c "import runpy; d=runpy.run_path('scripts/lumos',run_name='review'); E=type('E',(),{'resolve':lambda s,x:'Projects/P.md'}); ch={'touched':{'x.txt'},'code_shape':False,'code_touched':['bad.py']}; print(d['_drift_probe_is_candidate']([('symbol','foo'),('file','x.txt')],ch,'docs/kg/',E(),lambda:None))"
   ```

   輸出為 `None`；`when-file:x.txt` 已確定受影響，應為 `True`。後續 `_drift_probe_candidates` 因此不評估整行，也不產生可用 `drift ack` 表態的 finding。

## F3 NFD 重讀會重新使用完整 timeout，突破 scan 的總預算

severity: minor  
blocking: 否 — 判定仍保守，但一次 NFD 回讀可讓宣告的總預算接近翻倍。  
引句:「+        again = _nodehome_cat_blobs(root, [f"{where}:{unicodedata.normalize('NFD', paths[i])}" for i in retry],」  
file: `scripts/lumos:25930`

1. 第一次 NFC 批次讀取與第二次 NFD 重讀都收到相同的 `timeout`，第二次啟動前沒有重算 deadline 剩餘時間。
2. 最小重現以兩次各耗 0.03 秒的讀取模擬 0.04 秒預算：

   ```sh
   /usr/bin/python3 -c "import runpy,time; d=runpy.run_path('scripts/lumos',run_name='review'); f=d['_drift_cat_nfc']; calls=[]; f.__globals__['_nodehome_cat_blobs']=lambda r,s,timeout:(calls.append(timeout),time.sleep(.03),([None] if len(calls)==1 else [b'x']))[2]; t=time.monotonic(); f('.', 'a'*40, ['café.py'], .04); print(calls,round(time.monotonic()-t,3))"
   ```

   輸出：

   ```text
   [0.04, 0.04] 0.066
   ```

3. 60 秒 scan/check 預算同理可在第一次讀取接近 60 秒後，再啟動另一個最長 60 秒的 NFD 批次讀取。

## F4 副檔名判斷比文件宣稱的「字母開頭」更窄

severity: minor  
blocking: 否 — 只造成 scan 的具體誤列，不影響推送閘回傳碼。  
引句:「+    if path in tree.files or "/" in path or re.search(r"\.[A-Za-z][A-Za-z0-9]*$", path):」  
file: `scripts/lumos:26238`

1. 說明宣稱副檔名只須以字母開頭，但正則要求後續字元全部是 ASCII 英數。
2. 尚未建立的根目錄檔 `plugin.c++` 副檔名以 `c` 開頭，仍被列為「不像檔案路徑」：

   ```sh
   /usr/bin/python3 -c "import runpy; d=runpy.run_path('scripts/lumos',run_name='review'); T=type('T',(),{'files':set()}); print(d['_drift_probe_path_warn']('symbol','plugin.c++::load',T()))"
   ```

   輸出包含：

   ```text
   when-symbol 的路徑 plugin.c++ 在樹上找不到、也不像檔案路徑
   ```

3. 同形狀也涵蓋以字母開頭但含 `_`、`+`、`-` 或非 ASCII 字母的合法副檔名。

## 逐塊覆核

- 圖譜計劃與 Systems 更新：已看，除上述契約落差外無 finding。
- `_NotelinesNet` 延遲淨差異及失敗回傳：已看,無 finding。
- 路徑正規化後重驗、`.` 拒絕：已看,無 finding。
- BOM 解碼、讀不出內容的三態傳遞：已看,無 finding。
- 批次 prefetch、scan/check 共用語料：已看，除 F2、F3 外無 finding。
- 考試重放、有限 budget 驗證、表態指令分行、shebang 共用：已看,無 finding。
- 新增回歸測試：已看，未另見測試執行邏輯 finding；覆蓋缺口列於 F1–F4。

最嚴重等級 major，blocking 共 1 條。