severity: major

已讀材料：
- `governance/review-reports/code-test-quality-native-push/r1-snapshot.patch`：完整 1374 個改動檔名均納入覆蓋。
- `governance/review-reports/code-test-quality-native-push/r1-evidence.patch`
- `governance/review-reports/code-test-quality-native-push/r1-integration.patch`
- `governance/review-reports/code-test-quality-native-push/r1-history.patch`
- `CLAUDE.md`
- `/tmp/lumos-push-lens.txt`：內容為空，故依指示改讀固定席 `Systems/test-quality-cli.md` 與 `Systems/授權與歸屬.md`。
- `python-idioms` 的邊界驗證、秘密不得進日誌／repo、避免 shell 注入條款。
- 未讀其他席報告。

ID: g1
severity: major
blocking: 是
引句:「(args.out/'stdout.txt').write_bytes(out)」
問題：`capture` 無條件把完整命令列、stdout、stderr 與 JUnit report 寫進可提交的收證目錄，沒有秘密值攔截、遮蔽或明確的敏感輸出拒收機制。命令即使是可信本機命令，argv 或正常測試報告仍可能含 token；「可信」只說明是否允許執行，不能授權把秘密永久寫入卷證。
file: `scripts/test_quality.py:145`
file: `scripts/test_quality.py:166`
file: `scripts/test_quality.py:169`
file: `scripts/test_quality.py:183`

攻擊者：能讀取後續提交卷證的公開 repo 使用者或其他未授權讀者。
入口：維護者執行 `lumos test-quality capture`，再依既有流程保存或提交產物。
輸入：命令 argv、stdout、stderr 或 JUnit XML 中的 API token、密碼或其他憑證。
所得：秘密會原樣留在 `receipt.json`、`stdout.txt`、`stderr.txt` 或 `report.xml`，攻擊者可取得並使用該憑證。

最小重現：
```sh
mkdir -p /tmp/lumos-seat-work/code-test-quality-native-push/security
python3.14 scripts/lumos test-quality capture \
  --out /tmp/lumos-seat-work/code-test-quality-native-push/security/leak-repro \
  --source scripts/test_quality.py \
  --test-source scripts/test_test_quality_cli.py \
  --language fixture --framework junit --junit-stdout -- \
  python3.14 -c 'print("<testsuite><testcase classname=\"Leak\" name=\"passes\"/><system-out>DEMO_API_KEY=sk-demo-not-real-123456789</system-out></testsuite>")'
rg -n 'DEMO_API_KEY|sk-demo' \
  /tmp/lumos-seat-work/code-test-quality-native-push/security/leak-repro
```
結果：capture 回傳成功，假 token 同時出現在 `stdout.txt:1`、`report.xml:1` 與 `receipt.json:9`。應在產物進入持久目錄前拒收或遮蔽敏感 argv／輸出，並讓收證狀態翻紅；只在寫入後警告仍會留下秘密。

固定席核對：
- `test-quality-cli`：其責任明定為「明示本機命令收證與JUnit一致性核對」，並說明外部服務隔離由呼叫者負責。g1 不把無沙盒或 `not_attested` 當缺陷；問題是收證層會永久複製秘密。file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:6`
- `授權與歸屬`：新增三支 vendored Python 檔都有 SPDX 標示，`_VENDORED_TOOLKIT` 未納入 LICENSE/COPYING/NOTICE，未違反固定合約。file: `docs/lumos-toolchain-knowledge/Systems/授權與歸屬.md:16`

其餘安全邊界已讀，無 finding：
- CLI 使用 argv list 呼叫 subprocess，未經 shell；明示可信 Semgrep executable 屬既定信任邊界。
- 來源掃描以 AST／文字處理為主，不執行受掃來源；symlink、單檔大小、XML DTD/entity、逾時與程序群組均有防護。
- `no sandbox`、外部服務不隔離與 `not_attested` 均為明示能力限制，本席未列為 bug。
- 原生／歷史實驗的子程序入口、暫存目錄與限制式 AST 均逐 hunk 核對，未找到可證實的額外逃逸或命令注入。
- `python3.14 scripts/test_test_quality_cli.py`：22 tests，通過。
- `python3.14 scripts/test_test_quality_scan.py`：21 tests，通過。

Generated evidence 覆蓋與限制：
- 巨量 generated XML／JSON／log 未逐行人工審閱；以完整 `r1-snapshot.patch` 的 1374 檔名清單、秘密／個資模式搜尋、壓縮檔成員名掃描及 manifest 雜湊核驗覆蓋。
- `test-quality-native-consumers-20261008`：manifest 142 筆，缺檔 0、hash 不符 0；唯一未列入的 `README.md` 由其自身明示排除。
- `test-quality-three-platforms-20261008`：manifest 729 筆，缺檔 0、hash 不符 0；唯一未列入的 `README.md` 同樣明示排除。
- 未發現真實 API key、Bearer token、私鑰或常見平台 token。掃到的 `password`／`token` 多為套件描述、設定名稱或空值。
- generated evidence 含 `/Users/enzo/...` 絕對路徑及第三方套件作者公開 email；這些是本機結構與公開依賴中繼資料，未找到憑證或可單獨取得權限的利用鏈，故不另立 finding。

總結：最高 severity 為 major；blocking 數 1。