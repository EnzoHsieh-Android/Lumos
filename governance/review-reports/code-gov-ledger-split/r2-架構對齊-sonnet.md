severity: minor

## 問1 分層與依賴方向
結構對。_gov_ts 放在 _gov_ledger_rows_by_time 之前、同在治理帳工具段,被度量段(_gov_metric_events)與合讀共用,方向由上層讀者呼叫下層小工具,跟 _gov_tail_bytes(`scripts/lumos:3809`)被度量與增速段共用的做法一致。合讀改用 _gov_tail_bytes + _drift_jsonl_iter(`scripts/lumos:33724`),上一輪「另寫一套解析」已收斂,沒有跨層直呼。_ensure_docs_gitignore 改走 _write_lf(`scripts/lumos:17727`),也是 vault 唯一寫入原語,對齊。

## 問2 命名與錯誤處理
命名 _docs_ledger_path 與 _ci_log_path(`scripts/lumos:38694`)的「<範圍>_path」形狀一致。訊息語氣(白話、附出處)與鄰居一致。「不跟捷徑」的判法有分歧,見 F1、F2。

## 問3 第二種做法
沒有自創解析器;_gov_ts 把兩處重複收成一份,是收斂不是新增。剩下的是同一做法套得不齊,見 F1、F3。

## F1 本機帳只擋寫不擋讀,「不跟捷徑」判法在讀寫兩側不一致
severity: minor
blocking: 否
引句:「raw, _start = _gov_tail_bytes(p)」
file: `scripts/lumos:3809`
說明:_gov_tail_bytes 直接 stat/open,會跟著捷徑讀;度量段 _gov_metric_events 對本機帳同樣如此。既有的「不跟捷徑」寫法是讀取側先判 is_symlink 再讀(`scripts/lumos:3829` 的 _doctor_cfg_bytes、`scripts/lumos:33745` 的 _drift_load_acks)。這批只在兩支寫入器加了 is_symlink,讀者仍跟過去,同一個威脅模型(被提交進來的捷徑)只防了一半。

## F2 第三支本機帳寫入點 _usage_log 沒有同樣的捷徑檢查
severity: minor
blocking: 否
引句:「p = _docs_ledger_path(env.vault.parent, USAGE_LOCAL_LOG_NAME)」
file: `scripts/lumos:1458`
說明:_gate_event 與 _append_governance_log 對本機帳加了 is_symlink 擋(`scripts/lumos:1458`、`scripts/lumos:1535`),但同為被忽略本機帳的 .usage-local.jsonl 在 _usage_log 直接 open 追加,沒有同一道檢查。同類檔、兩種寫法。

## F3 _gov_ts 已吞例外,合讀排序鍵的外層 try 成了重複防護;_docs_ledger_path 只換了一半呼叫點
severity: minor
blocking: 否
引句:「except (OverflowError, OSError, ValueError):」
file: `scripts/lumos:3809`
說明:_gov_ts 內部已接 (ValueError, OverflowError, OSError) 回 None,key() 裡 t.timestamp() 外包的 try 仍保留一份例外清單,等於兩處各接一次,正是這輪要消掉的「兩處各寫、接的例外不一樣」。另外 _gate_event 的 else 分支仍寫 `docs / ".governance-log.jsonl"`,同一行三元式一邊用 _docs_ledger_path、一邊手拼路徑,與 `scripts/lumos:38694` 的單一路徑函式做法不齊。

不對齊共 3 條,其中重大 0 條
