severity: major

F1
severity: major
blocking: 是
引句:「if os.path.basename(tk) in _SHELLS and i + 2 < len(toks) and _SHELL_C_RE.match(toks[i + 1]):」
file: `governance/eval/lens-utilization/recount.py:930`
r3 新增的巢狀 shell 遞迴(補 r2 通才 D1)只在 `-c`/`-lc` 這種殼名「緊接下一個 token」時才觸發,`bash -x -c "…"`、`bash -l -c "…"`、`bash --noprofile -c "…"` 這類把 `-c` 隔開一個旗標、或用長選項的常見寫法完全沒涵蓋到。實跑 `m._search_events('bash -x -c "lumos search __NO_HIT_ABC__ --json"', '{"results": [], "candidates": 0}', False, "T")` 回傳 `[]`——不是「判不出」,是整段搜尋(含裡面真的零命中)直接消失不見,正是這整條修正鏈要堵的「數太少」那一類錯誤,而且測試 `t_lens_recount_search_nested_shell` 也只驗了 `bash -c "…"`、`zsh -lc '…'` 兩種緊貼形式,沒有覆蓋到這個缺口。

其餘重點檢查過但沒找到可重現的問題:`_drop_comment` 對 URL(`https://x.com/y#section`)、`熱門#標籤`(# 緊貼非空白字元)、混合行尾註解都實跑驗證正確,不會誤剝;巢狀 shell 遞迴本身不會多算(`bash -c "lumos search x" & bash -c "lumos search y"`、`bash -lc "lumos search x; lumos search y"` 都各自算對),也不會無限遞迴(遞迴每層必吃掉至少「殼名 -c」這段長度,3 層嵌套與刻意構造的退化輸入都能正常終止並回傳);`_SEARCH_VALUE_ABBR` 縮寫集合跟 `lumos search -h` 實際旗標表比對過,`--path`/`--top` 是僅有以 p/t 開頭的旗標,縮寫判斷跟真的 argparse 行為一致,沒有誤吃合法查詢詞的场景;矛盾檢查(計數 0 但看得到命中行 → 判不出)在單一搜尋自己的真實輸出下不會誤觸發,只有人為把兩個不相關指令的輸出接在一起才會,而這正是 r2 這條修正本來要抓的情況,不是新回歸。

全份最高嚴重度是 major,blocking 共 1 條。
