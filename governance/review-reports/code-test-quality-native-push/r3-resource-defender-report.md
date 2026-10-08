結論：**concern**。觀察成立，但現有證據不足以維持 **major**，也不足以把「所有成功／失敗完成後一律 `killpg`」視為既有合約。

- **觀察成立：是。** `finally` 明確受限於「`if proc is not None and proc.poll() is None:`」；launcher 已以 rc=1 結束時，`poll()` 非 `None`，不會執行 `killpg`。file: `governance/eval/test_quality_handbook.py:249`
- worker 關閉繼承的 stdout/stderr 後，`communicate()` 可以完成；標準 `Popen.poll()` 只判斷直接 child，不保證同群組 descendants 已結束。`run_model` 與直接 caller 都沒有後續群組清理。file: `governance/eval/test_quality_handbook.py:270`、file: `governance/eval/test_quality_handbook.py:409`
- 指定重現卷證顯示 fake launcher rc=1 後 worker 仍存活；本席未另行重跑 worker，亦未呼叫外部／付費模型。

- **判準成立：僅部分。** 圖譜明示的問題是「模型命令逾時只停止claude直屬程序，子工作者仍可能繼續消耗」，防回歸也只驗逾時。file: `docs/lumos-toolchain-knowledge/Systems/test-quality-handbook.md:54`
- S8 的明示合約限定於「當收證被取消、逾時或輸出超限時，工具應停止該POSIX命令群組」，沒有涵蓋一般 rc≠0 或成功完成。file: `docs/lumos-toolchain-knowledge/Projects/測試品質工具接線_計劃.md:63`
- 修後新增的是測試控制歸屬，且逐字限定「此為所有權補齊，不宣稱已證 runtime 回歸」；計劃也明說「沒有改治理閘、合約或審查上限」。file: `docs/lumos-toolchain-knowledge/Systems/test-quality-handbook.md:59`、file: `docs/lumos-toolchain-knowledge/Projects/測試品質工具接線_計劃.md:69`
- rc=1 不會形成假成功：有效性要求 `rc == 0`，最終 runner 也會回失敗。file: `governance/eval/test_quality_handbook.py:283`、file: `governance/eval/test_quality_handbook.py:416`

**major 不維持的理由：**目前實證是人工 fake launcher 可造成資源殘留，但尚未證明真實 `claude -p` 具有「launcher 先退出、同組付費 worker 關閉管線後繼續運作」的可達路徑；可見結果仍正確標成 invalid。資源清理缺口值得保留為 concern，但「所有完成／失敗均須 killpg」是新增生命週期政策，不是現有合約或標準 subprocess 語意。

固定版本核對：修前、修後及工作樹的產品檔 blob 均為 `3746de6b9f2f31dbbecc3c486e37e3814933f592`。

未驗範圍：未讀其他席報告、未掃其他問題、未重跑真實 Claude launcher。補讀量為 **1,430 個 whitespace-delimited words**（含必要 skill、兩篇指定圖譜、兩份指定 JSON、三次 Lumos 查詢及本機 Python docstring；版本差異僅重複核對同兩篇內容）。