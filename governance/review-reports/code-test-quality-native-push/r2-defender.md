A — ARCH-2

agree: 現象成立；測試跨越 handbook 所屬測試套件，單跑 handbook 15 項不會執行它。

evidence: 修正紀錄已把 `model_command` 綁到 `t_test_quality_cli`，而該入口會執行完整 `scripts/test_test_quality_cli.py`；受控核對中 handbook 15/15 與該 CLI 控制皆綠。

concern: 這是測試所有權與維護入口不一致；現有修正關卡沒有漏守，也沒有已證 runtime 錯誤或成立合約遭破壞，不足以定 major。宜把控制移到 handbook 套件並調整關卡綁定。

severity: minor  
blocking: 否  
引句:「path = TOOL.parent.parent / "governance/eval/test_quality_handbook.py"」  
file: `governance/review-reports/code-test-quality-native-push/r2-repair.patch:2485`  
file: `scripts/test_test_quality_cli.py:477`  
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-handbook.md:37`  
file: `governance/review-reports/code-test-quality-native-push/r1-fix.json:76`  
file: `scripts/test_lumos.py:75991`

B — S1

agree: 現象成立；UTF-16 的無害內部 entity 未命中 ASCII bytes 檢查，`junit()` 回傳 `::ok`、`passed`；同內容的 ASCII DTD 控制則拋出既定拒收錯誤。

evidence: 原測試只覆蓋 ASCII DTD；系統邊界又明載報告真實性不由此工具證明。此繞過沒有增加偽造報告的權限，本次也沒有證明外部檔案讀取、高倍擴張或資源耗盡。

concern: 泛編碼的 DTD 拒收邊界確實不完整，仍應以編碼感知的拒收方式修補並增加 UTF-16 控制；現有證據不足以稱為 major 安全或業務缺陷。

severity: minor  
blocking: 否  
引句:「if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():」  
file: `governance/review-reports/code-test-quality-native-push/r2-repair.patch:1368`  
file: `scripts/test_quality.py:128`  
file: `scripts/test_test_quality_cli.py:262`  
file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:27`

總結最嚴重 severity: minor；blocking 條數: 0
