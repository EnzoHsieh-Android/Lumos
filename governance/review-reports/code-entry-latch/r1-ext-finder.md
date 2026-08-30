F1|major|引句:「if any(t in low for t in tokens):」|scripts/lumos:5819|候選用子字串命中，但 BM25F 用完整 ASCII token；例如查 `foo bar` 會召回只含 `foobar` 的文件，得分即使為 0 仍被列為相關節點。無分數門檻下可輸出完全無關的 top-5，違反 advisory 的相關節點語意。

F2|major|引句:「_r = _el_near_ratio(_stem, name)」|scripts/lumos:9729|B 直接比較完整檔名，未剝除 Project 慣例後綴 `_計劃`；例如 `支付_計劃` 與 `登入_計劃` 僅靠共同後綴，相似度就恰達 0.6 而誤報近名。這會讓短中文計劃名稱大面積互相誤鳴。

F3|minor|引句:「if any(_el_is_cjk(ch) for ch in t):」|scripts/lumos:5766|`_el_is_cjk` 宣告支援假名與韓文，但上游 `_rank_tokenize` 只產出漢字及 ASCII token，因此純假名或韓文主題永遠得到空 tokens 並被判「無主題訊號」。A 對這些合法檔名不會查圖譜。

severity: major
