severity: major

## 問 1:分層與依賴方向

結論:呼叫方向沒變,也沒有跨層直呼。唯一的重複實作放在第 3 問。
- 呼叫方向仍是「`scripts/lumos`(CLI 入口)呼叫 sidecar(輔助檔)」,sidecar 不反向 import CLI。這跟舊版 `from test_quality import add_parser`(`scripts/lumos:49706` 的 else 分支)一致。
- 檔名清單從共用白名單 `_VENDORED_TOOLKIT`(`scripts/lumos:22331`)推導(`scripts/lumos:49450`),並與指紋表交叉核對(`scripts/lumos:49451`)。這延續了「安裝端與移除端共用單一常數」的既有做法(`docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:29`)。
- 指紋演算法直接呼叫既有 `_vendored_digest`(`scripts/lumos:22361`、用於 `scripts/lumos:49457`),沒有另寫一套 sha256 與換行處理。
- 小觀察,不列為發現:
  - 預期指紋表放在 `scripts/lumos:49445`,離既有指紋區塊(`_VENDORED_MANIFEST` 在 `scripts/lumos:22358`、`_vendored_digest` 在 `scripts/lumos:22361`)很遠。
  - 計劃只守 `lumos` 入口。評測腳本仍直接 `from test_quality import ...`(`governance/eval/test_quality_handbook.py:24`),不經過配套校驗。計劃已聲明「這只證版本配套一致」,範圍有寫清楚。

## 問 2:命名與錯誤處理

結論:結構對,有兩處小不一致,都是 minor。

ID: ARC-4
severity: minor
blocking: 否
引句:「正式 argparse 解析後只對 test-quality 回結構化錯誤；其他指令照既有流程。」
file: `scripts/lumos:50513`
敘述:
- 部署不完整時,JSON 錯誤用 `{"verdict":"not_assessed","complete":false,"reason"}` 加退出碼 2。這跟 `scripts/test_quality.py:368` 的錯誤形狀一致,沒問題。
- 不一致一:緊接著的 `except ModuleNotFoundError` 分支(`scripts/lumos:50516` 到 `scripts/lumos:50521`)仍輸出純文字到 stderr、退出碼 2,同一個子命令因此有兩種錯誤格式。配套載入成功時 `test_quality` 已在 `sys.modules`,這個分支走不到,是遺留的死碼。
- 不一致二:`lumos` 這裡用緊湊的 `json.dumps`,`test_quality.dump`(`scripts/test_quality.py:224`)用 `indent=2`。

## 問 3:第二種做法

ID: ARC-1
severity: major
blocking: 是
引句:「CLI 綁定三支 sidecar 的內容指紋；每支先讀最多 10 MiB 的 bytes，全部對上才從同一批 bytes 載入。」
file: `scripts/lumos:22358`
敘述:
- ⚠ 我判成 major,但有反方論點,請編排者裁定。
- 專案已有一套記錄「這三支檔的內容指紋」的機制:`_VENDORED_ALL` 含 `test_quality*.py`(`scripts/lumos:22331`、`scripts/lumos:22355`),`_vendored_manifest_write` 在安裝與更新時寫進 `.lumos/vendored.json`(`scripts/lumos:22367`),`_vendored_state` 再讀回來比對(`scripts/lumos:22381`)。
- 本設計另開一張寫死在原始碼裡的 `_TEST_QUALITY_BUNDLE_DIGESTS`(`scripts/lumos:49445`)。這張表要和 sidecar 在同一個提交手動同步,圖譜 `Systems/lumos-cli-lifecycle.md:172` 已為此記了坑。
- 計劃的 PRIOR-ART 只說沿用 `_vendored_digest` 函式,沒提到既有的 manifest,也沒說明為什麼不能用它。
- 反方論點:manifest 是安裝當下的事實紀錄,混裝時也會把混裝內容記進去。它回答的是「檔案有沒有被改過」,不是「sidecar 跟這支 CLI 是否同一版」。來源 repo 與全域 symlink 也沒有 manifest。所以多一張「CLI 與 sidecar 配套」的表可能有理由。
- 缺口:計劃沒有寫出這個理由,也沒有交代兩套指紋之間的分工。

ID: ARC-2
severity: minor
blocking: 否
引句:「沿既有工具檔指紋函式 `_vendored_digest`（換行統一成 LF 再算 SHA-256），以及 Python 標準模組載入規則」
file: `scripts/lumos:49463`
敘述:
- ⚠ 偏 minor,請編排者確認。
- 計劃的 PRIOR-ART 說沿用標準模組載入規則,實作卻是 `spec_from_file_location` 加手動寫入 `sys.modules`,再 `exec(compile(raw, ...))`(`scripts/lumos:49471` 到 `scripts/lumos:49474`),並自己做失敗回復。
- 專案裡已有另一種「依路徑載入模組」的寫法:`_handoff_load_hook` 用 `spec_from_file_location` 加 `exec_module`,並關掉寫 bytecode(`scripts/lumos:48918` 到 `scripts/lumos:48930`)。新寫法是第三種載入方式。
- 「驗過的 bytes 就是執行的 bytes」這個需求,`_handoff_load_hook` 確實做不到,所以有存在理由。
- 缺口:計劃的 PRIOR-ART 寫成「標準載入」,沒有交代跟 `_handoff_load_hook` 的差別。
- 其餘測試品質輔助檔(sidecar)彼此的 import 仍是一般 `from test_quality import ...`,依賴 `sys.modules` 預先登記。這是這個手動載入帶來的隱性前提。

ID: ARC-3
severity: minor
blocking: 否
引句:「完整配套註冊既有子命令；不完整配套註冊不 import sidecar 的佔位入口。」
file: `scripts/lumos:49486`
敘述:
- 載入時機不同於既有的延後載入。
- `_test_quality_load_bundle()` 是 `main()` 的第一句(`scripts/lumos:49486`),任何指令(包括 `--help`、`--version`、與測試品質無關的指令)都會先讀檔、算雜湊,並 exec 三支 sidecar。
- 既有做法是 `scripts/test_quality.py` 內 `test_quality_scan`、`test_quality_semgrep` 只在用到時才 import(`scripts/test_quality.py:194`、`scripts/test_quality.py:355`、`scripts/test_quality.py:361`)。`_handoff_load_hook` 也只在該指令執行時才載入。
- 舊版只在建 parser 時 import `test_quality` 一支,所以這是從「一支輔助檔提前載入」擴大成「三支全部提前 exec」。
- 配套完整性要在建 parser 時決定,所以 `test_quality` 提前載入有必要。scan 與 semgrep 也一起提前 exec 就不是必須。

## 問 4:落點

ID: ARC-5
severity: minor
blocking: 否
引句:「Systems/test-quality-cli」
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:172`
敘述:
- 計劃 `lands_in` 只列 `Systems/test-quality-cli`。
- 實際改的是 `scripts/lumos` 裡的安裝與白名單機制。「改 sidecar 必須同步更新指紋表」這條維護規則,已經寫在 `Systems/lumos-cli-lifecycle` 第 172 行,該節點負責 `_VENDORED_TOOLKIT` 與 vendored 的安裝更新。
- 兩個 sidecar 的家是 `Systems/test-quality-scan` 與 `Systems/test-quality-multilang`(`test_quality_scan.py`、`test_quality_semgrep.py` 只列在這兩篇的 about_code)。它們的變更現在會牽動 `lumos` 的指紋表,但 `lands_in` 沒提到這層關係。
- 建議把 `Systems/lumos-cli-lifecycle` 補進 `lands_in`。`test-quality-cli` 保留,放 PITFALL 與取捨;開新節點沒有必要。

不對齊共 5 條,其中 major 1 條
總結最嚴重 severity: major；blocking 共 1 條
