# 分段受控例子

experiment.json保留四個完整可執行版本的原文、提交與樹碼、固定probe與六個案例，以及24次原始結果。臨時Git repo已清理；歷史SHA是當次指紋，重放應從原文重建，不假設舊物件仍存在。

修前的負數案例失敗；僅修補與正確抽取helper後六項都通過；錯誤抽取helper版把上限改5，原問題仍通過，但上限與caller兩項保留案例失敗。這是定位區間的受控例子，不以提交先後本身證因果。

重放：將每個versions.source寫入獨立目錄product.py，probe_source寫成probe.py，依cases逐個執行：

```text
python3.14 -I <probe.py> <版本/product.py> '<一個cases JSON物件>'
```

預期結果見expected_rc，故意退化的失敗是預期觀測，不稱24項正式測試通過。
