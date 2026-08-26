### ext-f1
severity: major
引句:「人剪錯 AI 可能重加=接受的窄覆蓋成本,靠 candidates 讀側去重把「已填的」擋掉,只有「人主動剪掉的」可能重列」
佐證:file: `governance/review-reports/dref-v4/r1-snapshot.md:120`
說明:振盪窗口沒有關。prune 移除 ai-ref 後，該 ref 立即退出「已填」集合；backlog 的候選減已填重新變成非空，candidates 也會再次列出同一 ref，下一輪 Claude 可原樣 add-ai。現有 exact-dedup 也只阻止欄內仍存在的值，刪除後不留任何記憶，見 `scripts/lumos:8822`。這不是「窄覆蓋成本」：覆蓋窄描述哪些 ref 找不到；此處是已找到、已人工否決的 ref 無法維持否決，會反覆消耗抽查並推翻人的校正。若本次只允許一次性批次且永不重跑，可接受；但 spec 定義的是可反覆執行的 backlog 流程，未釘單次邊界，因此成立為實作前 major。

### ext-f2
severity: clean
引句:「判準=集合差★(v4 B 席:候選集 − 已填 ≠ 空;不是「兩欄皆空」——後者漏「補一條但還有候選」的節點)」
佐證:file: `scripts/lumos:318`
說明:集合差本身比 v3「三欄皆空」正確且更簡。候選應使用完整 `<rel>#dN` 作集合元素；如此可正確處理部分回填、同節點多決策、正欄與 ai 欄重複，以及已填但不屬當前候選的 ref。既有 `build_typed_index` 集中定義三具名邊並按來源、目標、邊型去重，足以讓 backlog/candidates 共用同一口徑。實作時須共用同一候選產生函式，不能各自重寫篩選。

### ext-f3
severity: clean
引句:「count-based expected_check:此 ref 正欄恰一份、不在 _ai★,v4 r3-c 精確化——語意是「此 ref 不在 _ai」非「整欄空」」
佐證:file: `scripts/lumos:8838`
說明:此精確化正確。promote 的後置條件只涉及被搬移的特定 ref；`decision_refs_ai` 中其他尚未審核的 ref 應保留，不能要求整欄為空。檢查應對原子寫回後重新解析的兩個 list 計數：正欄等於一、ai 欄等於零；不能沿用 `_append_decision_ref` 現有的「至少存在一份」檢查。

### ext-f4
severity: clean
引句:「dangling→rc=2 拒★(防失效 ref 蓋章洗白繞過不對稱信任)」
佐證:file: `scripts/lumos:1270`
說明:雙欄下的不對稱信任仍成立：E2 現行只讀 `decision_refs`，E3 讀兩欄聯集；prune 正欄會解除抑制，promote 則是唯一把 ai-ref 帶入 E2 信任面的操作。promote 先重驗節點與決策 id 存在、再原子搬移並做特定 ref 計數，可以擋 dangling 直接洗入正欄。允許已翻案但仍存在的決策被 promote 也與 E2 的精確命中語意相容，不是繞過。

### ext-f5
severity: minor
引句:「v4 只加 5 個讀多寫少的 suggest 原語,不動 E2/E3 讀側」
佐證:file: `governance/review-reports/dref-v4/r1-snapshot.md:121`
說明:規格口徑自相矛盾：正文稱五個原語，實際列出 V1 到 V6，共六個，即 backlog、candidates、add-ai、list、prune、promote。這不破壞安全模型，但會讓實作範圍、argparse 接線及測試數量產生歧義，實作前應統一改成六個。

結論:否決成立(v4 的集合差與 promote 精確化確實比 v3 乾淨，但刪除否決記憶後，人工 prune 會被下一輪 backlog/candidates 原樣重列；spec 把持久的人機衝突誤稱為窄覆蓋成本，尚未封住振盪)。
