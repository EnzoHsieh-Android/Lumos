severity: minor

ID: A1
severity: minor
blocking: false
引句:「with self.assertRaisesRegex(ValueError, 'invalid finding location'):」
file: `scripts/test_test_quality_scan.py:169`

既有 backend 邊界控制走真 CLI 與無害 fake backend，驗 rc、status 與 complete。新控制用 SourceFileLoader 直接呼叫 `backend_findings()`，只證 helper 拋例外，沒有守住 `scan()` 收斂成 unavailable 與 CLI 不完整報告的公開合約。保留直接控制量 decode 次數，另讓越界行號沿 fake Semgrep 真入口驗結構化拒收。

程序群、bundle digest、結果轉換與其他圖譜責任已讀，無 finding。

總結：最嚴重 severity minor，blocking 0。
