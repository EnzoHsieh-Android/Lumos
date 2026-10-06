# 兩版案例可比性受控實驗

experiment.json保留所有產品與probe原文、命令、輸入／預期值指紋、實際載入路徑和原始輸出。臨時目錄已由TemporaryDirectory清理，原始命令的臨時路徑是當次執行證據，不是可永久引用的工作區。

重放：將product_sources的三份原文各寫入獨立目錄的product.py，將probe_source寫為probe.py，再用Python 3.14逐一執行：

```text
python3.14 -I <probe.py> <before/product.py> 8
python3.14 -I <probe.py> <after_unchanged/product.py> 5
python3.14 -I <probe.py> <after_regressed/product.py> 5
python3.14 -I <probe.py> <after_unchanged/product.py> 8
python3.14 -I <probe.py> <after_regressed/product.py> 8
```

預期退出碼依序0、1、0、0、1。最後一個錯載版本案例故意兩端都跑before，兩邊均0，但loaded指出沒有載入after；不能用「打算驗after」的標籤代替實際來源。

這是人工最小實驗，不是CLI驗收或日後審查收斂成效。來源：
- pytest對環境隔離與不穩定測試的解釋：https://docs.pytest.org/en/stable/explanation/flaky.html
- SWE-bench修復／保留既有行為的兩組測試觀念：https://www.swebench.com/SWE-bench/api/harness/
