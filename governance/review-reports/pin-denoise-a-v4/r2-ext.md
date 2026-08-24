## 1. major

引句:「④`eval_edit`:★只動兩處★——`out_nodes`/`must_in_out` 讀 results ∪ lane(cap 內計入),`free` 明文排除 lane」

問題：`eval_edit` 還有第三個必須 opt-in 的消費點 `output_top3_must`。此函式明定衡量「人打開 hook 先看到的三行」，卻只讀 `res[:3]`；lane 成為 hook 尾端可見輸出後，當 results 少於 3 條時，lane 會補入人眼前三行，但指標仍忽略它。Spec 的「只動兩處」及測試清單均未涵蓋此路徑，會令 `out_top3_must` 在 lane-only／results<3 案例靜默失真，直接破壞本案宣告的觀測尺。

查證：`governance/eval/retrieval_eval.py:266`、`governance/eval/retrieval_eval.py:275`、`governance/eval/retrieval_eval.py:355`、`governance/eval/retrieval_eval.py:362`

最嚴重 severity：major
