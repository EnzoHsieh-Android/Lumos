### ext-f1 整卷 coverage 門檻擋不住單題低覆蓋造成的假綠，condensed 在這份小卷上可比舊偏差更嚴重

severity: blocker

引句:「整卷 coverage 低於門檻時 gate 結論標弱證據不轉綠」

佐證:file: `governance/eval/retrieval_eval.py:314`

佐證:file: `governance/eval/retrieval_eval.py:436`

佐證:file: `docs/lumos-toolchain-knowledge/Verification/2026-08-22_評測尺三修.md:102`

現行 macro 對每題等權平均，但 [S2] 只用整卷 coverage 決定能否轉綠。致命反例：edit train 六題中五題各 8/8 已判，第六題僅 1/8 已判且該筆相關；整卷 coverage 仍為 41/48=85.4%，遠高於暫定 0.5，但第六題 condensed P@8 會成為 1.0，並以完整一題權重進 macro，可把總分抬高最多 1/6≈0.167。此卷既有紀錄指出門檻與實測只差約 0.033、每格已達 2.1%，所以這個選擇性缺標偏差足以直接翻轉 gate；逐題「附印」coverage 並不能阻止假綠。

### ext-f2 雙報截至 repin 無法證明新門檻已重錨，08-17 的 history 不可比理由仍未被解掉

severity: major

引句:「過渡期雙報直到下次 repin，gate 門檻在雙報期末重錨」

佐證:file: `docs/lumos-toolchain-knowledge/Projects/標註刷新_計劃.md:61`

佐證:file: `governance/eval/retrieval_eval.py:496`

佐證:file: `governance/eval/retrieval_eval.py:528`

既有 repin 合約要求評測母體 unjudged==0；到達該終點時，condensed 已無未標項可剔除，新舊尺理應重合，不能提供偏差區間內的門檻映射。過渡期雖會印兩行，spec 卻沒有重錨方法、最低配對輪數、不同 coverage 分層或允收誤差，驗證也只 grep「同時含新舊兩行」。此外既有比較本來就依 goldset_rev 隔離不同標註版本；新增 metric_rev 只是把不可比正式記帳，沒有恢復 history 的可比性，因此 08-17「既有門檻與 history 失效」的核心理由仍成立。
