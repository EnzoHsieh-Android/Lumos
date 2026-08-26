# code-dref r2 delta 席(r1 折入回歸)
sha256 已核對 = e2e7a7549bb18216da0a3d852f5871bb46d4e986f739b50e90620f642fd04596。

### d-f1
severity: blocker
引句:「struct = {k: (s, e, kind) for k, s, e, kind in fm_structure(fm)}」
佐證:file: `governance/review-reports/code-dref/r2-delta.patch:327`
說明:r2-delta.patch 只補了 _dref_remove_ref(prune 共用)的清空鍵,cmd_dref_promote 手刪 _ai 那段(patch 320-327)沒動,327 行還是沒清理的舊行。實測:只有一條 _ai 的節點 promote 後留裸 decision_refs_ai:(YAML null,同 _dref_remove_ref 註解講的「裸鍵比沒鍵更糟」)。promote 一次一條是最常見操作,易撞。附:工作目錄已有沒收進凍結 patch 的修法(連同新測試 t_dref_promote_empty_key_cleanup,尚未 commit)——就凍結材料本身,第④條只做一半。

### d-f2
severity: major
引句:「return na[1] and nb[1] and na == nb」
佐證:file: `governance/review-reports/code-dref/r2-delta.patch:100`
說明:s1-f3 說「修註解」,實際改動連守衛本身砍了(換成只剩 na == nb)。現行 spec 第 138 行白紙黑字要 _dref_same 留空-did 守衛(照抄 E2 _hits,r3 d-f5 抓過)。這次刪沒留決策紀錄、spec 沒同步。目前因 _dref_parse 正則要 #d 後≥1 數字、did 不可能空,砍掉暫不炸(所有呼叫點不是先過 _dref_norm 就是被 if not na or not nb 擋),但繞過設計流程悄悄放寬 spec 白紙黑字要留的防線,超出 s1-f3 原本只要求「修註解」的範圍。

### d-f3
severity: minor
引句:「fm 就地改;呼叫端負責去重檢查(此函式只管插入)。」
佐證:file: `scripts/lumos:8805`
說明:_fm_list_insert 本身沒檢查欄位型別是不是 list,docstring 只寫呼叫端負責去重、沒提也要驗 kind。兩個現有呼叫點剛好都有先驗，現不出事；但實測餵 kind=scalar 欄位它不吭聲插一行 - "..." 弄壞 frontmatter 不報錯。純靠呼叫端紀律，第三個呼叫點忘驗就複製坑。

## 掃過但乾淨的面
- 第①條 valid 判斷改對(coverage_scan+candidates），退回 truthy t_dref_promote_coverage_advisory 翻紅有咬合。第②條 _node_decisions 讀 fm_lines 對，退回 load_raw_for_edit t_dref_crlf 兩斷言翻紅。第③條 _fm_list_insert 純抽取，去重/引號/控制字元守衛留原地無副作用。第⑤條 dispatch try/except 不誤吞正常路徑（成功路徑無這三種例外）。第⑦條 promote kind 驗證實測 scalar rc2 檔案沒被動。錯誤訊息統一對齊全檔 9 處模板。
