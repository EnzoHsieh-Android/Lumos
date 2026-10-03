severity: clean

R2C1 驗收：原問題已消失。  
severity: clean  
blocking: 否  
引句:「讀碼題不再依命令regex猜檔案；其他題仍走原本的順序判準。」  
file: `scripts/scenario_probe.py:185`  
與原報告比較：`grep 'scripts/lumos' README.md` 原為 `True`，現於 Claude、Codex 兩條 runner 均為 `False`；`find . -type f | grep scripts/lumos` 也為 `False`。判定改看成功工具結果內的專用來源標記，不再把命令參數或檔名清單當讀碼證據。

R2C2 驗收：原問題已消失。  
severity: clean  
blocking: 否  
引句:「只信成功工具的回傳；缺串流前提為 unknown，完整但沒讀到為 absent。」  
file: `scripts/scenario_probe.py:93`  
與原報告比較：`cd scripts && cat lumos` 原為 `False`，現於 Claude、Codex 兩條 runner 均為 `True`；相對路徑讀取不再依賴命令中逐字出現 `scripts/lumos`。

驗證：`r3-paired-cases.json` 的七組成對案例符合上述結果；本機 `python3.14 scripts/test_lumos.py -k source_probe` 為 59 passed、0 failed。僅驗收 R2C1／R2C2，未掃新項、未改檔。

總結：最嚴重 severity clean；blocking 0 條。
