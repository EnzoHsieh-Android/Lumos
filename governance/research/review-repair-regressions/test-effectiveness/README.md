# 高風險保留案例抓錯能力：受控實驗

這八筆執行只驗證判讀方法，不是產品合約測試或真實收斂效果。固定案例定義要求負數歸零、上限保持8；基線及錯誤版只改上限8→5，另有語法無效版。

| 版本 | 只驗負數修復 | 再驗上限保留 |
|---|---|---|
| 正常基線 | 綠 | 綠 |
| 上限錯誤 | 綠：未偵測這種錯誤 | 紅：正確上限斷言失敗 |
| 還原原版 | 綠 | 綠 |
| 語法無效 | 紅：未判定 | 紅：未判定 |

原文、內容指紋、實際命令／目錄／輸出及判讀在experiment.json。有效載入時probe記實際module原文指紋與函式載入檔案；無效版未載入，不稱行為執行。命令使用新建空目錄與python3 -B，避免舊模組快取。實驗臨時目錄已清理，歷史路徑只供查核，重放從保存原文重建：

```python
import json, tempfile, subprocess, hashlib
from pathlib import Path
record=json.loads(Path("experiment.json").read_text())
with tempfile.TemporaryDirectory() as root:
    for index,row in enumerate(record["runs"]):
        dest=Path(root)/str(index)
        dest.mkdir()
        for filename,source in [("product.py",record["sources"][row["version"]]),("probe.py",record["probes"][row["case"]])]:
            assert hashlib.sha256(source["text"].encode()).hexdigest()==source["sha256"]
            (dest/filename).write_text(source["text"])
        result=subprocess.run(row["command"],cwd=dest,capture_output=True,text=True,timeout=10)
        assert result.returncode==row["returncode"]
        if row["version"]=="upper_fault" and row["case"]=="repair_and_preserve":
            assert "upper-preserve violated" in result.stderr
            assert "actual=5 expected=8" in result.stdout
        if row["version"]=="syntax_invalid":
            assert "SyntaxError" in result.stderr
            assert "executed:" not in result.stdout
```

不以八次執行稱八個正式測試全綠，不以退出碼認定有效偵測，不推論其他錯誤都會被抓到。

每個固定probe預先安排原版→上限錯誤→還原原版，且在同一乾淨目錄重寫產品源與驗載入指紋。輸入、預期與probe固定，純本地算術無外部端點、身分、資料庫、時間與亂數；無可控外部狀態需重置。語法無效是另外兩筆未判定例子。
