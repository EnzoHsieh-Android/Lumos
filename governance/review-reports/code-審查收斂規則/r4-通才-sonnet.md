severity: minor

我讀了修補差異和完整改動,也跑了 `-k audit`(442 項)、`-k residual`(274 項)、`-k gov`(252 項)、`-k pitfalls_tier`(20 項),全部通過。另外實測 `_residual_tier_hits` 在 20MB 的真實治理帳上約 0.2 秒。

severity: minor
blocking: 否 — 只多升一次 high,不會漏擋也不會弄壞功能,代價是多過一次代碼審。
引句:「原本只有(節點, 指標),同節點兩條合約指同一筆決策時,拿掉其中一條的標記、或縮小其中一條的守備都被另一條蓋住)。」
問題:殘留的身分鍵從(節點, 殘留指標)改成(節點, 合約指紋, 殘留指標)。指紋是合約內文的雜湊,所以只改一個字(例如修錯字)就會換鍵。pitfalls 會同時算出一筆「新增殘留」和一筆「拿掉殘留」,理由文字還會寫成「推送範圍裡拿掉殘留(拿掉殘留要過代碼審)」。實際上殘留標記還在,只是合約句子動了。
具體失敗情境:有人修一個帶 `[residual:…]` 的合約行的錯字,再跑 `guard residual --reindex`。我拿 `_residual_index_view` 驗過:指紋由 aaaa 變 bbbb,新增集合和拿掉集合各一筆,所以這次推送被升 high。改字確實會讓舊問答對不上(doctor 本來就會唸),所以升級大致合理,但理由文字會誤導審查席。
佐證:``scripts/lumos: `44538` ``(鍵的組法)、``scripts/lumos: `_residual_tier_hits` 的 added/removed 段``

已讀,無 finding 的部分:
- `guard audit` 多記一筆 `guard-audit`:閘名已進 `_KNOWN_GATES`,不在 `_GOV_LOCAL_PAIRS`,所以進版控帳。目錄 `docs/` 不存在時 `_gate_event` 回 None,審計照常成功、不印警告。寫不進去只印一句警告,不改審計結果。審計當下算的指紋和問答用同一支 `_residual_claim_fp`,`INV_TAG_RE` 會剝掉 `[residual:]` 與 `[audit:]`,兩邊對得上。
- 既有讀帳者:`_gov_vc_gate_events` 改收閘名 tuple,舊的字串呼叫(`loop-retro`)行為不變。`_ResidualAsks` 把審計事件放在 `.audits`,沒混進問答表,doctor 與 `--reindex` 不帶 cases 的路徑不受影響。
- 先後比較:`_seq` 在 `_residual_ask_index` 裡對合併後的事件序列統一編號,同一秒的問答和審計靠它分先後。沒帶時區的 ts 會補本機時區。
- 沒有殘留的 repo、舊索引:`brows` 為空就直接回 0;起點版本沒有帳檔回 "missing";`hst` 為 bad 時,只在起點有殘留或這次動過索引才升 head_bad,沒有殘留的 repo 不會被誤升。
- 外層看門:只有「新增殘留」本身會升 high,這是設計意圖。純程式、純帳的推送在帳檔被碰到時只多做一次比對,不會升級。
- 逃逸帳、contracts:沒有變動,測試也綠。
- 效能:`GOV_LOG_REL` 讀 20MB 帳檔、比兩版列集合只花 0.08 秒。
- `_residual_case_key` 去掉字母與數字之間的連字號:前後相鄰字元一定存在(頭尾已剝),不會越界。

最高等級 minor,blocking 0 條。
