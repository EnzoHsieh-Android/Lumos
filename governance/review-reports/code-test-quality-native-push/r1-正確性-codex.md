severity: major

finding: F1 JUnit suite 的 `failures` 統計未被核對，無效基準與還原可被當成全綠，最後輸出 `detected`
severity: major
blocking: 是
引句:「Suite-level errors must not disappear behind passing testcase rows.」
file: `scripts/test_quality.py:87`
file: `scripts/test_quality.py:233`
file: `scripts/test_quality.py:243`
file: `scripts/test_test_quality_cli.py:137`

`junit()` 只拒絕 `<error>` 節點及 `errors>0`，完全忽略 `testsuite/testsuites` 的 `failures`。因此 `<testsuite tests="1" failures="1">` 仍可因唯一 testcase 沒有 `<failure>` 子節點而被解析成 passed；`check()` 隨後只看 testcase 衍生狀態，把這種自相矛盾的 baseline/restored 當成全綠。這屬於工具明示負責的收證內容一致性，不涉及「報告來源可偽造」或業務 verdict 邊界。

最小重現：

```sh
TMPDIR=/tmp/lumos-seat-work/code-test-quality-native-push/correctness \
python3.14 /tmp/lumos-seat-work/code-test-quality-native-push/correctness/repro_suite_failure_count.py
```

實際輸出：

```text
baseline 0 executed ... status passed
fault 0 executed ... status failure
restored 0 executed ... status passed
check 0 ... "fault_evidence": "detected"
```

重現中的 baseline 與 restored 原始 XML 都宣告 `failures="1"`，預期 capture 應回 rc 2、check 應回 invalid；實際三份 capture 都回 executed，check 回 rc 0 detected。既有 22 項測試全綠，但只覆蓋直接 `<error>`，未覆蓋 `failures>0` 與 testcase 列不一致的案例。

固定席合約影響：

- S1 掃描完整性：已讀,無 finding。
- S2 PHP 掃描適配：已讀,無 finding。
- S3 基準及還原全綠、環境錯不得算 detected：受 F1 直接破壞。
- S4 `not_assessed` 與報告真實性邊界：已讀,無 finding；F1 不要求來源認證。
- S5 Node/Laravel 原生卷證：受 F1 的共同 JUnit 核對入口影響。
- S6 C#/Android/iOS 原生卷證：受 F1 影響；這些 reporter 的原始 XML 均帶 `failures` 聚合欄位。
- S7 無效原生結果須回 invalid：受 F1 直接破壞。
- 授權檔不得進 `_VENDORED_TOOLKIT`：已讀,無 finding；端到端移除測試 4 passed。
- vendored 工具須帶 SPDX：已讀,無 finding；`scripts/test_quality.py` 有 SPDX，授權測試 7 passed。

資料狀態五問：

- 新舊互讀：schema 固定為 v1，已讀,無 finding。
- 寫一半：格式仍合法但遺失 failure testcase、只剩聚合 `failures` 的報告會假綠，對應 F1。
- 衍生資料：suite 聚合欄位與 testcase 衍生狀態未交叉核對，對應 F1。
- 時間：新 report 與執行後來源重讀有守衛，已讀,無 finding。
- 不可逆：輸出目錄與 report 要求全新；本機命令副作用隔離是明示邊界，已讀,無 finding。

其餘 hunk：已讀,無 finding。

總結: 最嚴重 severity major，blocking 1 條。