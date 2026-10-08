severity: minor

## F1 提醒輸出管道與 guard kill 既有的 ⚠ 慣例不完全相同
severity: minor
blocking: 否
引句:「設時間失敗(`os.utime` 丟出 OSError)不擋:印一行提醒到標準錯誤,照常跑測試」
file: `scripts/lumos:13839`
1. cmd_guard_kill 內「⚠ 提醒」有兩種既有寫法:config 衝突與 repo 未提交變更的 ⚠ 用 `file=(sys.stderr if as_json else sys.stdout)`(約 13839、13894 行),kill-log 寫入失敗的 ⚠ 固定 stderr(約 14008 行)。
2. spec 寫「一律標準錯誤」,與後者一致、且不破壞 `--json` 純度(★INVARIANT★ t_guard_kill_json_purity),不是引入新做法,故只列 minor。
3. 建議實作時跟 kill-log 那條同形(⚠ 開頭、固定 stderr),並在 spec 註明「同 kill-log ⚠」;非 --json 模式下提醒不會出現在 stdout 是預期。
4. 失敗場景:無(不會出錯),僅文件精度。

其餘各節:
- 範圍/做法:已讀,無 finding。核對「在 `cmd_guard_kill` 每個平台組開工作樹之後」:套壞法(`open(target,"w")` 寫檔後、`_kill_run` 前,約 13946 行)與 `git checkout` 成功(`rv.returncode != 0` 時 break 之後)兩個位置都在同一迴圈內,與既有流程順序相容;`os` 在該函式已被使用(os.path.realpath),不需新 import 層級。
- PRIOR-ART/既有做法:已讀,無 finding。專案裡處理快取的既有做法只有 `sys.dont_write_bytecode = True`(scripts/lumos:39921,唯讀指令不留 .pyc)與測試裡 `PYTHONDONTWRITEBYTECODE=1`(scripts/test_lumos.py:39848),都是「關寫快取」而非「改修改時間」,對象是 lumos 自己或 hook 子程序,與 guard kill 對使用者專案測試的處境不同;spec 已說明不選甲的理由(`_kill_run` 另有 3 處呼叫)。既有 `os.utime` 全在測試裡造舊檔,產品碼無先例,但這不是「第二種做法」(沒有既有的處理同一問題的做法)。
- 條款 S1-S3、回退、實務隱患:已讀,無 finding(架構面)。引句核對:「文件守衛測試從 `cmd_guard_kill` 原始碼抽 verdict 值域,別新增 `"verdict": "…"` 字面」與提醒訊息不含此字面相容。

最高等級:minor;blocking 共 0 條
