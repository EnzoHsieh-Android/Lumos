# code r2 delta 席(全新;修正批回歸)

**D2-1**|major|blocking:是(判準:違反 _el_related_nodes docstring 明載的 EL-10 保證,本批新引入迴歸)
引句:「子字串召回、token 記分——0 分=無任何 query token 命中,不冒充相關」
佐證:scored 的 >0 資格濾 vs _rank_fields 不含 decisions 內容。實測:詞只出現在 decisions: content 的節點——候選收集(可見行含 frontmatter)命中、記分 0 分、被濾成 nodes:[]。舊碼無此問題;EL-10 測試恰好 body 同詞,沒翻紅。F1 修假陽性順手殺真陽性。

**D2-2**|major|blocking:否(不動 rc/JSON;但每次觸發都是噪音)
引句:「檔名查無訊號就退回編號,兩者皆無才誠實未查」
repo 的 code-loop --spec 慣例檔名清一色 rN-snapshot.*(實掃 20+ 篇),殘渣恆為 snapshot;構造 spec=r1-snapshot+loop_id 無訊號,印出「lumos search "snapshot"」無意義建議。「首輪+--spec」路徑原測試從沒真跑過(唯一帶 --spec 的測試打在第 2 輪被 EL-1 短路)。

抑噪:spec 有訊號不被 loop_id 蓋掉(實測);spec 無訊號 loop_id 有訊號正確退回;141 個真實 loop 值跑濾網無 3 字母以上有意義詞誤傷;_實作計畫/_計劃 末字不同不可能雙吻合,剝序無關;monkeypatch 注錯 finally 還原乾淨無跨測試污染。

severity: major
