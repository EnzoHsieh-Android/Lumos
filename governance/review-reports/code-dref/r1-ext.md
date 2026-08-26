### ext-f1
severity: blocker
引句:「+                if d.get("valid", True):   # 只看翻案(valid:false)決策」
佐證:file: `governance/review-reports/code-dref/r1-snapshot.patch:259`
說明:`parse_decisions()` 保留字串值，所以翻案決策的 `valid` 是字串 `"false"`；在 Python 中非空字串為真，這裡會把所有 `valid:false` 決策直接 `continue`。結果 `_dref_coverage_scan` 永遠漏掉有 id 與無 id 的翻案決策。第一次 promote 仍會令正欄非空，使 E2 從節點級警告切換成只看正欄 ref；其他翻案落後邊因此可被連帶靜默，卻沒有設計承諾的覆蓋提醒。應改成與 E2 一致的字串判斷，例如 `str(d.get("valid", "true")).lower() != "false"` 時才跳過。

結論:否決成立（覆蓋掃描漏掉全部翻案決策，promote 可在無警告下造成 E2 靜默漏報）。
