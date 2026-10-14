severity: major

**Finding 1(決策內容可以手改追加殘留,不動索引也不動問答帳,分級判 light)**

severity: major
blocking: 是 — 殘留的反例清單寫在決策內容裡,分級只看索引的鍵與問答帳列,攻擊者直接改決策文字就能讓新反例不經高風險審進主線。
引句:「同一筆決策追加反例不動索引的鍵,看問答比看可手改的索引貼近要擋的動作」
攻擊步驟:
- 輸入:起點已有 `Systems/S#d12`,內容是「residual c1 … checker:sonnet/2026-10-01」,索引與 c1 的 untestable 問答都已在主線。下一個提交只改那篇筆記的 d12 內容,尾端加「另 c2 c3 c4 整個刪帳繞過也殺不掉」,不碰索引、不碰治理帳、不碰程式。
- 結果:`_residual_tier_hits` 回 `{}`,`_pitfall_tier` 回 `('light', '改動裡沒有程式檔(只有文件/資料/圖譜)')`。
- 鏡頭的新增殘留段也不出現,因為 `new_res` 與 `new_rows` 都是空的。
- 非 cases 模式的 `_residual_check` 只要求至少一個反例有 untestable 問答且內容有 checker:,所以 doctor 也照過。
- 缺口:r4 G1 的修法只在 `--add` 與新問答列的路徑上要求第二個代理問答。直接編輯已索引決策的內容,三條偵測(索引鍵、問答新增、守的檔被改)都看不到。
實驗證據:在實驗 repo 用 `_residual_tier_hits(R, 起點..HEAD)` 實跑,輸出 `hits: {}`,`tier: ('light', …)`。
file: `scripts/lumos:2061`(`_residual_tier_hits` 沒有任何讀決策內容的路徑)

**Finding 2(索引壞掉時升了 high,但派工鏡頭不出新增殘留段、也不出必答題)**

severity: minor
blocking: 否 — 推送仍會升 high 過審,只是審查席沒被要求逐條答;doctor 會報索引讀不出,另有一道擋。
引句:「new_res = (set(hguard) - set(bguard)) if hst == "ok" else set()」
攻擊步驟:
- 輸入:起點沒有索引,頂端提交把 `governance/residual-index.json` 寫成 `{bad`,同時在圖譜加殘留。
- 結果:`_residual_tier_hits` 回 `{'head_bad': True}`,所以分級是 high。但 `_lens_residual_section(R, base, head, vault)` 回 `[]`,鏡頭沒有新增殘留段,也沒有「逐條必答」那題。
- 影響:r4 G2 要保證「審查席被要求看新增殘留」,這條路徑上保證不成立。
實驗證據:`A hits: {'head_bad': True}`、`A lens: []`。
file: `scripts/lumos:2282`

**Finding 3(用假節點名的 untestable 問答列洗掉鏡頭的 5 條上限,真正的殘留被擠出清單)**

severity: minor
blocking: 否 — 被擠掉的那條只剩一句「另有 N 條未列,自己翻 diff」,審查席仍可自己翻,但逐條必答被稀釋。
引句:「一次最多列幾條合約」
攻擊步驟:
- 輸入:同一次推送在治理帳手寫 5 列 `gate=residual-ask`、`verdict=untestable`、節點 A0 到 A4 的問答(任意假節點),再加真正的殘留合約,節點名排序在後(`Systems/Z`)。
- 結果:`asks_untestable_added: 6`,鏡頭 `sorted(want)` 先列 A0 到 A4,最後只印「(另有 1 條合約未列,自己翻 diff …)」,真正那條的殘留指標與決策內容完全沒有進派工詞。
- 細節:假列的 `checker` 欄位缺漏時,鏡頭顯示 `checker:?`,審查席無法從上面分辨哪些是假的。
實驗證據:`B hits: {…'asks_untestable_added': 6}`,`B lens` 只列出 A0 到 A4 與「另有 1 條合約未列」。
file: `scripts/lumos:2295`

沒找到洞的部分(已用實驗或讀碼確認):
- 問答列寫成讀不出判定的壞列,會被算成 untestable。
- 同一次推送刪一列 testable 再加一列 untestable,會同時觸發 `asks_dropped` 與 `asks_untestable_added`。
- 跳脫的閘名 `residual\u002dask`,分級與驗法讀者都用位元組過濾,兩邊一致讀不到,沒有新增與驗證的落差。
- 單列內夾 `\r` 或雙物件,分級端解析失敗一律算 untestable。
- 決策內容經 `_plain_label` 把 ─ 換成 -,再經 `_frame_injected` 與 `_lens_visible`,無法偽造框線關閉;全形或相近字元的框線只能出現在單行中間,實用性低,未列為 finding。

實驗已清掉(scratchpad 的 `cr-rc5-資安/`)。

最高等級 major,blocking 1 條。
