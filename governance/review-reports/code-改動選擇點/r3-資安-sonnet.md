severity: clean

我只審修補差異,範圍是 `scripts/lumos`、筆記和技能文件。三類都已看,沒有發現能被利用的洞。

## ① 提示注入:已看,無
- 新的警告訊息會印測試名,印之前都經過 `_kill_esc`。
- 其他訊息只印數字和固定字串。
- 這些輸出沒有把自由文字送進給 AI 的派工詞、hook 附加段或指令。

## ② 讀寫與執行越界:已看,無
- 整批掃描 `_choice_scan_batch` 用參數清單呼叫 ast-grep,不開 shell。
  - 工具路徑照 `_lint_wt_resolve_tool` 解成 PATH 上的絕對路徑,不吃 repo 裡的同名檔。
  - 設定檔限定在工具鏈的 `configs/ast-grep/` 底下,不帶 `-U`、`-i`、`--custom-languages`。
  - 工作目錄是全新的暫存目錄,檔名只用序號 `N.kt`,不用 repo 路徑,所以沒有捷徑跟過去或路徑穿越。
  - 輸出用 `names[Path(d["file"]).name]` 對回原檔,對不上會丟 `KeyError`,`_choice_scan_batch` 接住後退回逐檔。
- `_choice_test_blobs` 的 `git grep -z -o -w -F -I` 也都是參數清單。
  - 測試名一律放在 `-e` 後面,開頭有 `-` 也不會被當成選項。
  - `-F` 不解析正規式。
  - 路徑樣式 `*{ext}` 來自平台設定,沒有外部可控的來源。
  - 平台根先經 `_choice_plat_prefix` 用 `realpath` 比對,不在 repo 裡就回 `None`,只讀、不寫。
- 這一輪修補沒有新增密鑰、信箱,也沒有下載網址。

## ③ 非刻意、一步就能繞過的守衛:已看,無
- `_CHOICE_TESTS_UNKNOWN`(測試所在檔的雜湊查不完或找不到時記的 `?` 標記)只會讓「存活的行」重跑,方向偏安全。
- `_choice_push_stale_tests` 遇到這個標記就不比較,影響的只是「另一組守的測試」那句提醒,擋不擋的判定沒變。
- 測試檔名帶空白或中文時,`-z` 輸出不會被引號包起來,後面再用 `nfc()` 正規化,不會漏掉。
- 整批掃描失敗(逾時、rc 異常、輸出過大、剖不了)會退回逐檔掃描,不會靜默通過。
- 掃描時限用完時,`max(deadline, now + _CHOICE_GUARD_FLOOR)` 保證碰到的計劃至少還有 5 秒,不會因為時限用光就放行。

## 順手提一句(minor、blocking 否,屬範圍外)
`governance/anchor-baseline.json` 的 `test_lumos.py` 雜湊由 AI 代簽更新,note 引用了使用者睡前的授權。這是使用者明確授權的刻意流程,不是非刻意走過去的守衛,所以不列發現。

圖譜鏡頭:尾端沒附固定席,這次不判。

最嚴重:clean;blocking 共 0 條
