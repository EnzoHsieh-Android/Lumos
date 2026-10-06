severity: clean  
verdict: evidence

先驗觀察：probe 得到 `{'materials': []}`；現行程式以 `json.loads` 解析後取 `materials`，空清單立即回 vacuous rc0。`scripts/lumos:23296-23310`

判準的最強支持：

- spec 明定「JSON 頂層必須是 dict；只接受缺省／null／清單型 materials」；此解析結果符合。`governance/review-reports/seat-input-validation/r1-snapshot.md:34`
- spec 又明定「缺省、null 與 [] 保留 vacuous rc0」。`governance/review-reports/seat-input-validation/r1-snapshot.md:35`
- 驗收條款逐字要求：「當 materials 缺省、null 或空清單時，席位對帳應保持 rc0 與 vacuous」。`governance/review-reports/seat-input-validation/r1-snapshot.md:43`
- 原 S1 同樣規定「materials 為空的輪豁免不判(vacuous 豁免)」。`docs/lumos-toolchain-knowledge/Projects/驗證層自證三件_計劃.md:33`

客觀反證：重複鍵確實會遮掉前一個 `must-read.md`，RFC 8259 的鍵應唯一也支持把它視為資料品質風險；但本案沒有「拒絕原始 JSON 重複鍵」條款，裁定邊界是 `json.loads` 後的 dict 與 materials 形態。依現有必守條款，將解析後的 `[]` 判為 vacuous rc0 不構成本案必修違規。