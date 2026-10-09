severity: major

整體讀完，spec 對 S1、S3 的宣稱跟程式相符（見各節）。S2 與「全部對上才從同一批 bytes 載入」這個核心承諾在 `scan --semgrep` 路徑上不成立，下面 BND-1 附可重現的反例。

## 逐節結論

- 問題與最小解：已讀。BND-1 的反例推翻了這一節的主張。
- 做法與驗收（段落）：「全部對上才從同一批 bytes 載入」不成立，見 BND-1。其餘宣稱經實測相符：10 MiB 上限、模組名同標準 import、錯誤留在 parser 建立期、佔位入口不 import sidecar。
- S1：已讀，無 finding。我把 `test_quality_semgrep.py` 刪掉後測了 `scan`、`capture`、`capabilities`、無子命令、`test-quality --help`，全部回 2 並輸出 `complete:false` 與 `not_assessed`。`capture --output-dir` 指定的目錄沒有建立。
- S2：有 finding，見 BND-1。
- S3：已讀，無 finding。`--vault X`、`--vault=X`、縮寫 `--vau` 都回結構化錯誤。`--version`、`--help` 在缺檔時照常。
- 回退：已讀，無 finding。
- 實務隱患：只列四個「已排除」項，缺併發、效能、資源，見 BND-4。

---

ID: BND-1
severity: major
blocking: 是
引句:「CLI 綁定三支 sidecar 的內容指紋；每支先讀最多 10 MiB 的 bytes，全部對上才從同一批 bytes 載入。」
審材外佐證 file: `scripts/test_quality_semgrep.py:10`、`scripts/lumos:49470`
問題與判準：
- **根因：** `_test_quality_load_bundle` 依字典順序 exec：semgrep、scan、test_quality。semgrep 的第 10 行有頂層 `from test_quality import CaptureInterrupted, CaptureTimeout, run_capture_command`。exec 到這一行時 `sys.modules['test_quality']` 還沒登記。
- **後果：** Python 會走標準 import，從磁碟載入 `test_quality.py`，包含讀寫 `__pycache__`。已驗 bytes 之後才登記，覆蓋 `sys.modules` 的那一筆。semgrep 因此永遠綁在一份「磁碟版（可能是 stale bytecode）」的 `run_capture_command`、`CaptureTimeout`、`CaptureInterrupted` 上，不是已驗 bytes 的那份。
- **影響範圍：** 凡是 `scan --semgrep` 呼叫 `semgrep.scan`（`test_quality_scan.py:306-307`）的路徑。這正是 spec 要防的「同時間戳同大小舊 bytecode 回到舊判讀」。
- **測試缺口：** 現有測試 `scripts/test_test_quality_cli.py:760` 只對 `capture` 路徑造 stale pyc，沒覆蓋 semgrep 這條，所以沒被抓到。spec 的 S2 只標 manual，同樣沒涵蓋。
- **同源副作用：** 部分更新時，磁碟版與已驗 bytes 之間有第二次讀檔的空窗，磁碟版可以是另一個版本。

可重現命令（`python3.14`，`<ws>` 是 `/tmp/lumos-seat-work/測試品質部署配套校驗/邊界-sonnet`）：
1. 用 `git archive HEAD` 取出 `scripts/lumos` 和三支 sidecar 到 `<ws>/c/scripts`。
2. 先把 `test_quality.py` 裡 `    import time\n    buffers` 換成同長度的 `    1/0` 加空白再接 `\n    buffers`，用 `py_compile` 產生 pyc。
3. 用 `shutil.copyfile` 把原始 source 蓋回去，並用 `os.utime(ns=...)` 還原 mtime，大小相同。`shasum -a 256 test_quality.py` 為 `97b1f6e9…ad01d`，與 `_TEST_QUALITY_BUNDLE_DIGESTS` 一致。
4. 在 `<ws>/proj` 執行 `python3.14 ../c/scripts/lumos test-quality scan --semgrep ./fakesg a.test.js`。

輸出：
```
File ".../c/scripts/test_quality_semgrep.py", line 75, in scan
    returncode, stdout, _ = run_capture_command(command, BACKEND_TIMEOUT, cwd=root, env=env)
File ".../c/scripts/test_quality.py", line 82, in run_capture_command
    import time          ← 行號指向 source，內容卻是 stale bytecode
ZeroDivisionError: division by zero
```
- **對照：** 同一 fake 命令在未動手腳的 `a` 目錄只回「掃描不完整 … unavailable」，沒有 traceback。
- **身分比對：** 乾淨 bundle 也一樣。`semgrep.run_capture_command is sys.modules['test_quality'].run_capture_command` 為 False，`CaptureTimeout` 也不是同一個物件。
- **另一組反例：** 把 stale 版的 `CaptureTimeout` 基底換成 `Exception`，semgrep 端看到 `Exception`，已驗模組是 `ValueError`。

---

ID: BND-2
severity: minor
blocking: 否
引句:「部署不完整亦不妨礙既有 --help、--version 入口。」
審材外佐證 file: `scripts/lumos:49486`
問題與判準：
- **eager load：** `main()` 第一行無條件載入整包 sidecar，對所有指令生效，不只 test-quality。
- **例外清單：** 只接 `OSError/ValueError/ImportError/SyntaxError`，以外的例外會讓每個指令都崩。
- **FIFO 反例：** 讀檔用 `open("rb").read(...)`，沒擋特殊檔。把 `test_quality_scan.py` 換成 FIFO（`mkfifo`）後，`python3.14 lumos --version` 阻塞超過 8 秒（subprocess timeout 實測 HANG）。
- **spec 缺口：** spec 對「部署不完整」只講缺檔、混裝、不可讀，沒講特殊檔，也沒承諾其他指令不受影響的機制。
- **已查無問題：** 符號連結指向 `/dev/null` 回「配套版本不一致」，權限 000 回結構化 `Permission denied`，目錄屬 `OSError`，CRLF 版本通過驗證且可載入。
- 風險低（要人為造 FIFO），標 minor。

---

ID: BND-3
severity: minor
blocking: 否
引句:「完整配套註冊既有子命令；不完整配套註冊不 import sidecar 的佔位入口。」
審材外佐證 file: `scripts/test_quality_scan.py:295`
問題與判準：
- **報告指紋：** 報告的 `adapter_source_sha256` 是報告產生時重新從磁碟讀 `test_quality_semgrep.py` 的 bytes 再雜湊，不是載入時驗過的那份。
- **更新空窗：** 載入後、報告前若有 `lumos update` 換檔，報告記的指紋會對應沒被執行的版本。
- **關聯：** 與 BND-1 同源（部署後仍有二次磁碟讀取），spec 完全沒提。
- **修法方向：** 載入時把驗過的 digest 存起來給報告用。

---

ID: BND-4
severity: minor
blocking: 否
引句:「已排除:不可逆:不刪檔、不更新安裝來源、不修改歷史卷證。」
審材外佐證 file: `scripts/lumos:22751`
問題與判準：
- **併發：**
  - `_vendor_toolchain` 用 `shutil.copy2` 非原子逐檔覆蓋（`lumos` 排第一、sidecar 在後）。
  - 同時跑 `lumos test-quality` 的程序會短暫看到新 CLI 配舊或半寫 sidecar，被擋成「配套版本不一致，請 lumos update」。
  - 這是 fail-closed，沒有假綠；經 `lumos update` 結束後恢復。
  - 兩個程序同時更新時三支各自檢查，不會互相污染。
  - 但 spec 的「實務隱患」沒有併發項，也沒有這個瞬態拒絕的說明。
- **效能：** 實測 `_test_quality_load_bundle` 約 8 ms/次（三支合計約 40 KB），`lumos --version` 約 0.6 s，無感。有一個可累加成本：semgrep 的磁碟 import 會額外讀寫 pyc（BND-1）。
- **資源：** 每支最多讀 10 MiB+1 bytes，三支合計約 30 MiB 上限，沒有累積。
- **回滾：** 純還原 `scripts/lumos` 即可，無狀態殘留。
- **補強建議：** spec 應補一行「更新期間拒絕為預期行為」，並把併發、效能、資源各寫一句「無＋為什麼」。

---

總結最嚴重 severity: major；blocking 共 1 條
