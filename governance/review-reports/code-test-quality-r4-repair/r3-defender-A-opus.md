判決：維持 major

我實際跑過了，這個問題成立。我能找到的辯護理由只能減輕它造成的實際後果，推不翻「同一項政策有兩份實作，其中一份沒補到」這件事。

**1. model_command 確實會把已經正常退出的 launcher 誤判為逾時**
- 程式在 `governance/eval/test_quality_handbook.py:235-244`。它用 `Popen(..., start_new_session=True)` 開程序，再用 `proc.communicate(timeout=timeout)` 等。`communicate` 要等到兩條管線都讀到檔尾才會返回；只要還有 worker 握著繼承來的 stdout，它就一直等到逾時，然後拋出 `TimeoutExpired`。
- 實驗腳本放在 `/tmp/lumos-seat-work/code-test-quality-r4-repair/辯方A-opus/`。fake launcher 先 `Popen(['sleep','30'])`，印出一行 `{"type":"result","subtype":"success"}` 後以 `exit 0` 退出，timeout 設 3 秒。
  ```
  == c (c4982cb1)  TIMEOUT '{"type":"result","subtype":"success"}\n' 3.01
  == p (10d40f30)  TIMEOUT '{"type":"result","subtype":"success"}\n' 3.01
  ```
  launcher 的 rc 是 0，輸出也完整，結果還是被判成逾時。worker 最後有被清掉，因為 `:241` 和 `:251` 有 `killpg`；我只對自己記下的 PID 補確認，結果是 `worker gone`。

**2. 對呼叫端的影響，以及有沒有不能共用的正當理由**
- `run_model`（`test_quality_handbook.py:270-276`）接到 `TimeoutExpired` 後，會設成 `rc=None`、`stderr='model-timeout'`。依 `:281-283` 的規則，這場就算 `valid=False`。這是往安全那邊錯：成功的場次被丟掉當無效，不會被誤記成成功或算錯分數。代價是白等滿整段 timeout、白花一次模型費用，有效場次也跟著變少。`historical_handbook_trial.py:19` 直接 import 這支 `run_model`，所以影響一樣。
- 這一點我替被審方減輕：真實的 `claude -p` 留下握著它自身 stdout 的 worker，機率應該不高。Bash 工具開的子程序有自己的管線，而且 behavior lane 只放行 `Bash(python3 verify.py)`。不過這只是推論，我沒有實測證明。
- 找不到正當理由說 handbook 不能共用：
  - `governance/eval` 已經有直接 import `scripts/` 模組的先例：`governance/eval/ablation_lumos_first.py:28` 的 `sys.path.insert(0, str(ROOT / "scripts"))`，旁邊註解還寫著「判準單一實作來源」。
  - `governance/eval/test_quality_corpus.py:31` 本來就把 `scripts/test_quality.py` 整份複製進凍結副本，所以部署邊界或凍結副本都不構成障礙。
  - 本輪也已經替 `run_capture_command` 補了 `cwd` 和 `env` 參數。
  - 真正的介面差異只有兩點：共用 runner 回傳 bytes、逾時時拋 `ValueError`，而且有 10 MiB 輸出上限，stream-json 事件流可能碰到這條線。這只代表不能直接換掉，不代表不能共用。

**3. 圖譜筆記怎麼寫**
- `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:58`：本輪在同一段裡加了「worker 繼承 stdout/stderr 時還會讓已退出的 launcher 被誤判逾時」，下一句接著寫「CLI capture 與 handbook model runner 都建立獨立 POSIX 程序群，必須採同一項返回前清理政策」。但這段列的防回歸測試全是 capture 那邊的，沒有一支是 handbook 的。
- `test-quality-multilang.md:56`：只講 Semgrep backend 改用共用 runner，沒有提到 handbook。
- 更關鍵的是：B1 原報告（`governance/review-reports/code-test-quality-r4-repair/r2-boundary-report.md:6`）引的正是這句「CLI capture 與 handbook model runner…」，而修補分組 `r2-fix.json` 的 G2 只列了 `scripts/test_quality_semgrep.py:scan` 一條路徑。也就是說，審查員已經點名的同族路徑沒有掃到。
- 有一點對被審方有利：「返回前清理」這半句，handbook 在 `:247-255` 的 finally 裡無條件 `killpg`，確實做到了。不成立的是本輪新加的「不誤判逾時」那半句。

**4. 是本輪造成的，還是修補前就有？**
- 程式碼的缺陷修補前就存在。`git diff 10d40f30 c4982cb1 -- governance/eval/test_quality_handbook.py` 是空的，兩版逐位元比對（cmp）也完全相同，最後一次改到這支檔的是 `782829d0`。兩版實跑結果也一樣，見第 1 點。
- 但本輪做了兩件事：把「誤判逾時」寫進一段聲稱兩邊共用的政策，以及修 B1 時沒處理它點名的 handbook 路徑。所以「保留第二種做法，而且筆記寫得跟程式碼對不上」這個問題，確實落在本輪。

**最小修法建議**（兩條擇一）
- **甲，在原地補上**：把 `model_command` 裡那一次 `communicate(timeout=timeout)` 改成一個迴圈。每次 `proc.communicate(timeout=0.1)`；接到 `TimeoutExpired` 時，若 `proc.poll() is not None`，就 `killpg` 整個群組再繼續 `communicate()`；若已過截止時間，就照原本的方式清群組再 raise。Python 文件保證 `communicate` 逾時後再呼叫不會遺失輸出。
- **乙，共用 runner**：仿照 `ablation_lumos_first.py:28` 的做法 import `run_capture_command(cmd, timeout, cwd=directory)`，把 bytes 解碼成字串，並把逾時的 `ValueError` 轉成 `TimeoutExpired`。但要先處理 10 MiB 上限碰到 stream-json 事件流的問題。

兩條都要在 `governance/eval/test_test_quality_handbook.py` 加一支先紅的測試：用 fake launcher 開一個繼承管線的 `sleep` worker 後 `exit 0`，斷言 `model_command` 回傳 rc 0、沒有拋逾時，而且 worker 已被清掉。再把這支測試名加進 `test-quality-cli.md:58` 的防回歸欄，並把 handbook 這條路徑補進 `r2-fix.json` 的 G2。如果決定不修，至少要把 `test-quality-cli.md:58` 改成「不誤判逾時目前只有 capture runner 做到」，並附一行 `REVISIT:`。
