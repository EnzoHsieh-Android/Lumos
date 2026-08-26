### arch-f1 search_gate/hook_p_gate 門檻在 main() 覆寫塊又寫了一份,違反本檔「唯一實作」紀律
severity: major
引句:「_v["hook_p_gate"] = _ce["p"] is not None and _ce["p"] >= 0.70 and not _ce["weak"]」
佐證:file: `governance/eval/retrieval_eval.py:484`
佐證:file: `governance/eval/retrieval_eval.py:534`
說明:report_goldset 是 gate 布林唯一組裝點;覆寫塊把 15.0/0.70 門檻原樣重打(同段對 beats() 卻正確複用)。日後調門檻只改一處,另一處靜默留舊值。應抽 _search_gate/_hook_gate helper 兩處同呼。

## 對齊良好的面
_condense 判準=collect_unjudged 補數且有同源斷言測試;CONDENSED_REV 擺放同 SEARCH_TOUCH 慣例;_ratchet_base 只抽查找、方向語意留席;history 新欄兩種既有慣例各自對號;測試全照 t_+check() 慣例。
