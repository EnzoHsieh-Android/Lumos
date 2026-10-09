severity: major

## Finding MT-1

severity: major
blocking: true
引句:「`--vault` 控制也改在它建立 source 的暫存目錄執行」
file: `scripts/test_test_quality_cli.py:786`
file: `scripts/test_test_quality_cli.py:795`

測試把來源建立在 `self.root`，但 `subprocess.run` 未設定 `cwd=self.root`；相對路徑實際從外層測試工作目錄解析。於 repo 外的臨時 clone 刪除 fixture 建立行後，單跑案例仍為 OK。因此 fixture 完全沒有參與判定；缺少 scanner 的部署檢查先行，讓案例假綠。最小修法是在本案例的 `subprocess.run` 加 `cwd=self.root`，並保留有效來源建立與專屬 reason 斷言。

CLI worker 控制回退後會翻紅；Semgrep decode 移回迴圈或拿掉行號上界後也會翻紅。其餘無 finding。

總結最嚴重 severity: major；blocking: 1。
