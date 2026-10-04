---
type: project
status: doing
created: 2026-10-04
updated: 2026-10-04
tags:
  - type/project
  - status/doing
  - scope/guards-gates
related:
  - "[[Issues/治理帳多個寫入者都沒上鎖]]"
lands_in:
  - Systems/pitfalls-code-loop
  - Systems/棧別提問表態閘
  - Systems/reversibility-governance-ledger
---
# code-loop治理帳寫讀契約_計劃

## 問題與範圍

前一個讀側小案在設計首輪被可重現交錯擋下，卷證留在原登記倉庫 `/Users/enzo/orca/workspaces/lumos-toolchain/aspidochelone` 的本機提交 `b1c53dcc68e3a8e91129184ac9c2e1637187e75d`，具體檔案為 `governance/review-reports/design-codeloop-ledger-lines/` 及 `Verification/2026-10-04_code-loop治理帳讀側縮案停手`；本乾淨 clone 不含該分支，該卷證不是本案通行證。主線的治理帳先有一筆完整舊表態、尾端再有無換行的短寫時，下一次 `_codeloop_dispositions_gov_log` 仍回成功，但新 JSON 會接在殘尾上；乾淨 checkout 的讀者跳過融合列而採舊表態。新案只處理**同一本治理帳的「寫入成功 ↔ 完整列可讀回」契約**，不帶入先前分支座標候選碼，不藉改名重置前案的三輪代碼審失敗。

四個直接寫入入口（通用 gate 事件、`_append_governance_log`、code-loop pass/skip、code-loop dispositions）都必須走同一個 append 協定：沿用專案 `_excl_lock_try` 的獨佔鎖檔方法，以 `docs/.governance-log.jsonl.lock` 為同一鎖鍵，等待上限 2 秒、鎖檔過期門檻 900 秒；拿不到鎖即回失敗，不作無鎖寫入。鎖內檢查既存尾端是否以 LF 結束，整筆 UTF-8 JSON 與 LF 以單次 bytes 寫入並驗回報長度，釋放時只刪自己的鎖。已有無換行尾列或短寫時保留原帳、回報寫入失敗並停止後續寫者接上它；不自動補 LF、截斷或把殘尾升格為已提交紀錄。這個契約不承諾斷電後的耐久性。`pass/skip` 及 `dispositions` 的成功訊息與 marker 只能在治理帳成功寫入後出現；best-effort 事件維持「寫帳失敗不改原閘判定」，但須回失敗並顯示既有警告。`_loop_gov_mark` 及其 `cmd_loop_rewrite` 等聲稱「入治理帳」的呼叫端必須依回傳值改訊息，不能吞錯後宣稱記帳成功。

讀側共用「原始 bytes 以 LF 結尾、嚴格 UTF-8、JSON 物件」才算一列的判準；本案盤點並遷移 `scripts/lumos` 內直接消費同帳的 rewrite 血緣、doctor 帳成長與 spec-gate 統計、`gov` 彙整、迴圈關門、逃逸統計、lint-new 統計，以及 code-loop 留痕／表態 fallback。壞列前後的好列仍可用，尾列無 LF 不算答案；各統計保留原有去重與篩選，不能因共用解析器改變其他語意。若掃帳逾時或 I/O 失敗，`code-loop check` 的表態路徑不得把未知當成已核對通過。非治理帳與其他六類修復（分支座標、docs 資格、錨點交錯、卷證有界讀取）不在本案。

## 驗收條款

- [S1] 當帳尾有無 LF 殘尾時，任一治理帳寫者應回報失敗、保留原始帳 bytes，且不把新 JSON 接到殘尾。 [test:t_codeloop_ledger_record_integrity]
- [S2] 當空帳或完整尾列上有兩個合作寫者交錯寫入時，共用 append 協定應讓每筆成為獨立 LF 結尾 JSON 物件，依檔案順序可讀回。 [test:t_codeloop_ledger_record_integrity]
- [S3] 當注入短寫、寫入例外或鎖取得失敗時，重要的 `pass/skip` 與 `dispositions` 應回失敗且不留下新 marker，後續寫者亦不得接在未提交尾列後。 [test:t_codeloop_ledger_record_integrity]
- [S4] 當通用治理事件或設計迴圈關門事件寫入失敗時，該入口應保留原閘判定、回報 telemetry 寫入失敗，且 `cmd_loop_rewrite` 等呼叫端不得宣稱帳已記錄。 [test:t_codeloop_ledger_record_integrity]
- [S5] 當治理帳有無 LF 尾列、含 `0xff` 的列或通過文字預篩的 JSON 陣列列時，`scripts/lumos` 所有同帳讀者應只採完整 LF 結尾的嚴格 UTF-8 JSON 物件，保留壞列前後的有效答案與行序。 [test:t_codeloop_ledger_record_integrity]
- [S6] 當有適用題、沒有 marker 且治理帳讀取失敗或超出表態預算時，真 `code-loop check --json` 應阻擋並說明讀帳未完成，不能經外層例外或逾時回 `blocked=False`。 [test:t_codeloop_ledger_record_integrity]

最小紅燈：在獨立暫存 Git repo 寫入有效舊表態＋`{"cut":`，呼叫現行寫者寫新 SHA，斷言「回報失敗、讀者仍只看舊紀錄、帳尾未接新 JSON」；main 現況回 `(True, "")` 且融合列含新 SHA。另以無 marker 的 `check --json` 驗異常解碼、非物件與表態預算，不用單純內部函式測試冒充 CI 守衛。先釘此紅燈再動實作，修後跑相關子集，完整測試留給推送前閘。

PRIOR-ART: [Python `FileIO.write`](https://docs.python.org/3/library/io.html)回報實際位元組數，需驗短寫；專案已由 [[Issues/治理帳多個寫入者都沒上鎖]] 裁定沿用 `_excl_lock_try`，不另加 `fcntl.flock` 第二套鎖。借用既有 `_ledger_append` 的「一筆 bytes 寫入並驗長度」做法，但此帳需四類寫者共用鎖、拒絕既存殘尾；無第三方依賴。外部文件只支持 I/O 判準，不能證明收斂率會提高。

RETIRE-IF: 若主線最小交錯在乾淨 clone 無法翻紅，停止本案重查基準；若共享 append 協定仍需重寫所有閘判定或無法保持原帳不可改，停止擴案回 [[Issues/治理帳多個寫入者都沒上鎖]] 重定邊界。首次實作與每次重開分支座標案之前重跑寫者→無 marker 讀者反例。

## 回退

回退此修法不截斷治理帳；回退版若仍可把尾列當答案，或在半列後宣稱新寫入成功，停止推送與 CI 放行，直到另一道獨立守衛擋住該路徑或重驗新版。保留本案反例與帳本原始 bytes 供排查。若鎖策略在某平台不可用，重要留痕與表態寫入須明確失敗，不得退化成無鎖成功。

## 實務隱患

已排除:金流:不涉及金額或付款。
已排除:對外送出:本案不推送或部署。
已排除:不可逆:不重寫既有帳列；新增 append 仍保留原始紀錄。
守衛面:讀錯治理帳可把無效表態或舊留痕當作新答案，須用無 marker 真入口、寫入故障與交錯配對驗證。
