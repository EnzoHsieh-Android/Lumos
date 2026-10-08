severity: minor

## 類1 不可信輸入流到危險操作
已看。本機帳的三支寫入器(_gate_event、_append_governance_log、_usage_log)寫入前都過 _local_ledger_writable,捷徑與非一般檔不寫;_ensure_docs_gitignore 用 O_NOFOLLOW、O_EXCL、O_APPEND,並擋捷徑、硬連結、非一般檔。唯一不對稱處見 F1。

## 類2 判定繞過
已看,無。判定類讀者(code-loop、fix-check、design-loop)仍只讀版控帳;_GOV_LOCAL_PAIRS 是白名單且要求 hard 恰為 False,不含任何判定閘。兩本合讀(_gov_ledger_rows_by_time)與度量段只用於 doctor 顯示與提醒,偽造本機帳行最多讓 doctor 多印一行「該撤」,不影響 CI 或 pre-push 放行。_BOOKKEEPING_FILES 新增兩個本機帳路徑,只是資料檔,不能夾帶可執行碼。

## 類3 密鑰與個資
已看,無。讀者跟捷徑讀帳(舊行為,cmd_gov 一直如此),但只解析成 JSON 物件並過 _gov_event_types_ok,印出的只有 gate、kind、note 欄;_ensure_docs_gitignore 印出的只有 docs/.gitignore 路徑與固定兩行。沒有把家目錄檔內容寫進 repo 的路徑。

## 類4 加密與傳輸
已看,無。這份 diff 沒有網路或加密相關改動。

## 類5 執行邊界
已看。doctor 新增的 git 呼叫走 _lens_git,參數是固定常數檔名並帶 `--`,沒有注入面。_ensure_docs_gitignore 的 O_EXCL 與 O_NOFOLLOW 用法正確,懸空捷徑也走「是捷徑」分支而不寫。若 docs 目錄本身被 repo 提交成指向外部的捷徑,補忽略規則只會往那個目錄追加固定兩行文字,內容不受攻擊者控制,無實質後果。

## 類6 行動端
已看,無。

## 新依賴
已看,無(只新增標準庫 heapq)。

## F1 版控帳寫入路徑仍跟捷徑寫(與新增的本機帳防護不對稱)
severity: minor
blocking: 否
引句:「        with open(path, "a", encoding="utf-8") as f:」
佐證行(file): `scripts/lumos:1470`
攻擊路徑(推論,此行為本批之前就存在、本批沒有改動):
1. 誰:惡意 repo 作者。
2. 入口:提交 docs/.governance-log.jsonl 為指向受害者家目錄檔的捷徑(git 可存捷徑),受害者 clone 後跑 lumos 的 hook 或 doctor。
3. 送什麼:_gate_event 對版控帳的「blocked / skipped」事件走 open(path,"a") 並跟捷徑,追加一行以 `{"ts"` 或欄位鍵開頭的 JSON 文字,note 欄含部分可被攻擊者影響的內容。
4. 拿到什麼:往目標檔追加一行 JSON 垃圾。行首固定是 `{"` 開頭的 JSON,不是合法 shell 或 authorized_keys 條目,沒找到能產生執行或提權的內容,因此只算完整性污染,不構成可利用的洞。新增的 _local_ledger_writable 註解自己點出「可指向 repo 外」,同樣的防護沒套到版控帳(版控帳要保持舊行為以免破壞 CI 流程,屬已知取捨)。

總結:這批改動新增的本機帳寫入、忽略規則補寫與兩本合讀都有擋捷徑與非一般檔,判定類讀者仍只讀版控帳,沒找到能被利用的洞,只留一條版控帳寫入仍跟捷徑的既有不對稱供參考。
