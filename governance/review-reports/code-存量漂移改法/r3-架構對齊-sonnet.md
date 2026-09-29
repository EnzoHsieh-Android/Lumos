severity: minor

## 問 1 分層與依賴方向
`_nfc_child`/`_phys_path` 放在 `nfc` 正下方(file: `scripts/lumos:387-414`),屬檔頭通用工具層,位置對。`_drift_git_arg` 呼叫 guard 區段的 `_guard_raw_git_path`(file: `scripts/lumos:12188`),drift 段(27xxx)往下呼叫 guard 段,且同段既有的 `_drift_fix_clean_err` 已這樣用(file: `scripts/lumos:27758`),方向一致。`_drift_sh` 呼叫的 `_sh_quote` 定義在代碼審收尾段(file: `scripts/lumos:34550`),drift 段依賴到更後面的段落,見 F1。

## 問 2 命名與錯誤處理
`_nfc_child` 沿用 `_plan_file_exists` 原本「OSError 當沒有」的處理;`_phys_path` 找不到回原路徑讓呼叫端照報,與同族函式一致。`_drift_git_arg` 查不到退回索引鍵,而同段 `_drift_fix_clean_err` 遇到 None 是回錯誤(file: `scripts/lumos:27759-27761`);前者是提示文字、後者是閘,語意不同,不列。命名前綴 `_nfc_`/`_phys_`/`_drift_` 與既有一致。

## 問 3 第二種做法
`_plan_file_exists` 已收斂到 `_nfc_child`,是收斂。但檔案系統側 NFC 找項目還有一處沒收(F2)。`_drift_sh` 建在 `_sh_quote` 上是收斂於既有 helper,但檔內仍有多處直接 `shlex.quote`(file: `scripts/lumos:1062`、`11250`、`11456`、`12881`),屬既有債,不歸這份 diff。

## F1 _drift_sh 依賴的 _sh_quote 住在代碼審收尾段
severity: minor
blocking: 否
引句:「其他字元一律交給 _sh_quote。」
file: `scripts/lumos:34550`
1. `_sh_quote` 是代碼審提交指令段的區域 helper(file: `scripts/lumos:34546` 只有那一處使用),drift 段(`scripts/lumos:27615`)改成依賴它,等於 drift 段依賴 code-loop 段的工具,而不是檔頭通用層。
2. 結構對(執行期可解析),只是通用 shell 引號 helper 的位置不在通用層;⚠ 是否要搬到 `nfc` 附近由作者裁。

## F2 檔案系統 NFC 找項目仍有一處內聯,沒被收進 _nfc_child
severity: minor
blocking: 否
引句:「檔案系統側 NFC 找檔收成通用的 _nfc_child/_phys_path」
file: `scripts/lumos:9813`
1. `_loop_plan_rel` 一帶用 `{nfc(q.name): q.name for q in proj.iterdir()}` 再查表(file: `scripts/lumos:9813-9819`),做的是同一件事:磁碟 NFD 名對 NFC 鍵找實際項目。
2. 這份 diff 宣稱收成通用,但只改了 `_plan_file_exists`;此處是同形狀、需要「回實際名稱」,`_nfc_child(proj, cand)` 可直接取代。現況是兩種寫法並存。
3. 其餘 `nfc(...)` 多為字串比對,不涉磁碟項目,不列。未能證明是 major(該處是 diff 外既有程式碼,不是這份 diff 新引入),故 minor。

不對齊共 2 條,其中 major 0 條
最高等級:minor
