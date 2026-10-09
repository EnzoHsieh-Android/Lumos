severity: minor

ID: R4-COR-1
severity: minor
blocking: false
引句:「[防回歸:test_semgrep_backend]」
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-multilang.md:51`
file: `scripts/test_quality_semgrep.py:25`
可重現理由：倉庫中不存在 `test_semgrep_backend`；現有 scanner 測試也沒有送入合法 finding 來驗證「只 decode 一次」或超出來源行數的拒收。把 adapter 換回 `03a46da6` 舊版後，三項 Semgrep 相關 scanner 控制仍全部通過，證明目前測試無法辨別這次修補。圖譜所列防回歸測試因此是空指向。應補一項至少含多筆合法 finding 與越界 line 的獨立測試，再填入實際測試名。

ID: R4-COR-2
severity: minor
blocking: false
引句:「global `--vault` 案例先建立有效 source」
file: `docs/lumos-toolchain-knowledge/Verification/測試品質第四輪修補驗證.md:21`
file: `scripts/test_test_quality_cli.py:750`
file: `scripts/test_test_quality_cli.py:751`
可重現理由：測試將 `sample.py` 寫入 `self.root`，但啟動 CLI 時沒有設定 `cwd=self.root`，傳入的又是相對路徑 `sample.py`；它實際相對測試程序的 repo cwd 解析，而該處沒有此檔。測試雖因 bundle 檢查較早執行而通過，卻沒有建立圖譜聲稱的「有效 source」，因此未隔離部署缺檔這個單一失敗原因。應設定 `cwd=self.root` 或傳入絕對來源路徑。

已讀並動態驗證 `model_command` 的 rc1 descendant 與 timeout 路徑，兩項皆能清理 worker；Semgrep 越界行號會結構化拒收；`scripts/lumos` 內嵌 digest 與 sidecar SHA-256 相符。除上述測試與圖譜證據缺口外，無其他 finding。

總結最嚴重 severity: minor；blocking: 0。
