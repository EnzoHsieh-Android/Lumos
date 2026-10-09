severity: minor

ID: R4-R2-REG-1
severity: minor
blocking: false
引句:「`--vault` 控制也改在它建立 source 的暫存目錄執行」
file: `docs/lumos-toolchain-knowledge/Verification/測試品質第四輪修補驗證.md:25`
file: `scripts/test_test_quality_cli.py:787`

最小重現：在 repo 根確認 `sample.py` 不存在後執行該案例，測試仍通過。案例把有效來源寫到 `self.root/sample.py`，但 `subprocess.run()` 沒有設定 `cwd=self.root`，相對參數仍從 repo 目錄解析。修補新增的 `cwd=self.root` 實際落在另一個呼叫。bundle 缺檔檢查較早執行，所以案例仍綠，但沒有建立驗證紀錄聲稱的有效來源前置條件。

CLI 程序群、Semgrep 邊界、bundle 指紋與 handbook runner 已讀，無其他 finding。

總結：最嚴重 severity minor，blocking 0。
