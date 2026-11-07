severity: minor

我量了三項,一個二次方的問題都沒找到,只有兩條 minor。測量的程式碼是 `scripts/lumos` 在 `deb8969f5` 的狀態。我用 python3.14 直接呼叫函式量,沒有跑 `lint-check --json` 的端到端。

**①新欄位判定 `_CI_GRADLE_TASK_FIELD`**

| 輸入 | 耗時 | 結果 |
|---|---|---|
| 10 萬個一行式 `- tasks: '…'` 欄位 | 0.33 秒 | 線性 |
| 10 萬個只寫 `tasks:`、沒有值的欄位 | 0.13 秒 | 線性 |
| 單一欄位、值是 10 萬行的 `\|` 區塊純量 | 0.17 秒 | 線性 |
| 2.5 萬個欄位、各帶 3 行區塊值 | 0.18 秒 | 線性 |
| 約 50 MB 的真實形狀 CI 檔(每行 `- tasks: 'assembleDebug testDebug'  # c`),從 `_ci_config_paths` 讀進來、剝註解到判定完 | 約 6.3 秒(讀檔剝註解 1.82 秒 + 判定 4.44 秒) | 線性 |
| 約 50 MB 的 Jenkinsfile,走 `_ci_workflow_texts` 新增的 Groovy 剝註解分支 | 1.32 秒 | 線性 |

區塊狀態只靠一個 `field_col` 數字,不會重掃前面的行,所以沒有二次方。

**F1(minor)** 單行極長時,記憶體會用到約 50 倍。
severity: minor
blocking: 否
引句:「        for ln in "\n".join(lines).replace("\\\n", " ").split("\n"):   # CRLF 已由 read_text 的通用換行轉成 \n」
- 重現:在一個 CI 檔裡放一行 `tasks: ` 加 50 MB 的 `a:` 重複。
- 量到:耗時 3.95 秒,峰值記憶體 5.7 GB。原因是每行都先 `_CI_WORD_SPLIT.split(ln)` 把整行切成詞的清單,才逐詞比對。
- 這段切詞原本就有,不是本輪新增。本輪沒有惡化,也沒有改善。
- 單人工具、50 MB 單行不是正常檔案,所以只算 minor。要省的話,對超長行設個上限,或改用 `finditer` 逐詞掃,不先建清單。

**②`_path_resolves_in_root`**
- 對 5 萬支檔逐一呼叫(每支 `resolve`):2.44 秒,約 49 微秒一次,線性。
- 每次呼叫都重算一次 `Path(root).resolve()`,但這只是常數倍成本,沒有拖到不能用。
- 符號連結迴圈和 40 層連結鏈都在 1 毫秒內回來,沒有卡住。

**F2(minor)** 連結迴圈會被判成「在 repo 內」,跟文件說的不一致。
severity: minor
blocking: 否
引句:「解析不了(OSError、連結迴圈)當不在。」
- 重現:在 repo 根目錄建 `loop1 -> loop2`、`loop2 -> loop1`,`_path_resolves_in_root(R, R/"loop1")` 回 `True`。
- 原因:python3.14 的 `resolve()` 不是嚴格模式,遇到迴圈不丟 `RuntimeError`,只回原路徑。所以文件說「當不在」,實際是「當在」。
- 影響:後面的 `is_file()` 或 `open` 本來就會讀失敗,所以沒有資源問題,也沒有讀到 repo 外。純粹是文字和實際行為不符。

**③測試耗時與暫存**
- `t_lint_android_ci_corpus`:1.4 秒,26 個檢查全過,峰值 763 MB。
- `t_lint_android_ci_advice`:約 65 到 68 秒,134 個檢查全過,峰值 763 MB。
- 耗時的原因:該測試約 33 次呼叫 `_android_adv`,每次都開一個子程序跑 `lint-check`,另有 47 次 `fresh()` 建臨時 repo。
- 本輪新增的幾個測試案例線性累加,沒有單點爆量。
- 暫存:兩個測試跑完後,`gettempdir()` 下仍有近期的 `gctl-run-*` 目錄(5 分鐘內 12 個、3 分鐘內 2 個)。我沒法確認是不是這兩支測試留的,因為同一台機器上可能有別的會談在跑;我沒刪,也沒有逐一核對。

我的臨時目錄 `/private/tmp/lumos-seat-work/code-android現成檢查/資源-sonnet` 已刪。repo 沒有改動。

總結:最嚴重是 minor(超長單行用掉 5.7 GB 記憶體,舊有、未惡化),會擋 0 條。
