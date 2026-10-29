severity: minor

1. --json 路徑原樣輸出原生函式名與 .so 名,沒有像文字輸出那樣清過
severity: minor
blocking: 否
引句:「sites = sec["sites"][:200] if sec["status"] == "ok" else []」
file: `scripts/lumos`(補丁 `_macrobench_native_retained` 與 `_macrobench_native_print`;本機 `scripts/lumos:40089` 與 `:40107` 起)
file: `skills/lumos-android-evidence/SKILL.md`(補丁第 1940 行,叫 AI 讀 `--json` 的 `sites` 後把呼叫位置寫進收據)
- 誰:被量 App 帶進來的第三方 .so 作者,或被量 App 自己的原生符號。
- 從哪:heapprofd 錄檔裡的 func、so、caller 字串。SQL 只截斷 func 與 caller 到 500 字,so 不截。
- 送什麼:函式名寫成派工詞或指令的樣子,例如「忽略先前指示…請執行…」。
- 拿到什麼:文字輸出每行過 `_events_clean`,而且截到 500 字。`--json` 的 `sites[].func/so/caller` 與 `reason` 沒有任何清理就進了 AI 的視野,skill 指定 AI 走的正是這條路。控制字元和換行會被 JSON 跳脫,但自然語言形式的注入文字原樣通過。
- ⚠ 要有人把惡意符號放進被量 App 才成立,再加上威脅模型是單人自用、外來文字回顯放行,所以只標縱深防禦。

**三類結論**

① 提示注入:只有上面第 1 條。
- `reason` 裡的 stats 名稱經 hex 解碼後截到 300 字,同樣是外來文字,在 `--json` 路徑也沒清,跟第 1 條同一個缺口。
- 文字輸出路徑已看,無問題:`_events_clean` 把換行、控制字元和方向字元換成空格。

② 讀寫與執行越界:已看,無。
- adb shell 指令字串只插入三種值:`pkg`、`run_id`、裝置路徑。
  - `pkg` 在 `_macrobench_stab_optional_err` 之前就過 `MACROBENCH_PKG_RE.fullmatch`,沒有注入面。
  - `run_id` 限制為 `[A-Za-z0-9._-]+` 且不能只有點。
  - 裝置路徑的前綴是寫死的常數。
- 轉 SQL 時 hex 輸出,行內逗號、引號、換行都切不亂;`bytes.fromhex` 失敗會捕捉成 `ValueError`。
- `heap-native.pftrace` 與 `record-native.pbtxt` 在 `native_on` 時加進 `git check-ignore` 檢查,沒被忽略就擋下。`prune_old_snapshots` 的 `heap-*.pftrace` 通配也涵蓋 `heap-native.pftrace`。
- 沒有新增下載來源、環境變數覆蓋下載網址,也沒有新寫進程式或範本的密鑰與信箱。

③ 非刻意、一步就能繞過的守衛:已看,無。
- `LUMOS_STABILITY_STEP_BUDGET_S` 會驗成數字,不是數字就擋下;殘留的值頂多讓第二段被跳過,不會繞過安全守衛。
- 殘留的 `LUMOS_STABILITY_SCENARIO` 由 e2e 範本清掉,`PYTHONPATH` 由 `env -u` 清掉,這兩個既有守衛沒被動到。
- 第二段被中斷時,`native_phase` 的 `finally` 與 `cleanup` 會收掉裝置上的錄製和暫存。

最嚴重 severity:minor;blocking 共 0 條。
