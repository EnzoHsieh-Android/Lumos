severity: major

（來源：檢索核心重建 設計審 r1 外家否決席，codex-cli，2026-09-14；逐字稿切出的本體）


1. 權重數字不變，不代表校準仍然有效
severity: major
blocking: 是；必須把全庫統計視為新的排序模型驗證。
S5 同時改變各詞 IDF 與長度正規化，對不同節點的影響並非共同乘數，因此固定欄位權重與型別先驗仍可能改變相對排名。
應分別比較「只擴候選」「只換統計」「兩者合併」，並把既有校準列為待重驗，不能直接宣稱沿用已驗證資產。
引句:「不動已校準的欄位權重與型別先驗。」
file: `scripts/lumos:2751`
file: `scripts/lumos:2769`

2. 預先斷詞仍會被 FTS5 再次斷詞
severity: major
blocking: 是；索引 token 必須與既有 token 一對一對應。
記憶體實測：既有斷詞器輸出 `foo-bar, foo, bar`，直接空白串接餵入預設 FTS5 後變成兩個 `foo`、兩個 `bar`，完整 token 消失，頻率與長度也改變。
S2 必須指定可逆 token 編碼或確切 tokenizer 設定，並驗證索引統計與 BM25F 統計一致；[SQLite 官方文件](https://www.sqlite.org/fts5.html#tokenizers)也明列 FTS5 自身的斷詞階段。
引句:「不引入新依賴、不引入第二套切詞語意。」
file: `scripts/lumos:2667`
file: `scripts/lumos:2760`

3. 查詢編譯契約未定，候選結果可以相差數十倍
severity: major
blocking: 是；必須先固定多詞、複合詞、單字與特殊字元的查詢規則。
重跑「BM25 檢索 排序」，token 全 AND 得 8 篇、全 OR 得 204 篇，而單字「字」也無法靠既有 bigram token 命中只寫「文字」的文件。
參數化 MATCH 傳入 `foo-bar` 仍實測報 `no such column: bar`，因此必須指定 token 分組、FTS 語法引用及 `--regex`／`--no-any`／`--cjk-loose` 的相容行為，不能只寫「不必連在一起」。
引句:「多詞查詢不再要求那幾個字連在一起出現。」
file: `scripts/lumos:2667`
file: `scripts/lumos:3008`
file: `scripts/lumos:3067`

4. 排序欄位無法覆蓋入口召回的資格欄位
severity: major
blocking: 是；共用索引必須保留每條路徑的可見文字與資格判準。
入口召回明確接受只出現在 frontmatter／decisions 的零分候選，並刻意納入 superseded；S2 的五欄索引會漏掉這類「已裁不做」的決策。
另一方面，現有排序正文包含程式碼，但搜尋預設排除程式碼，直接拿排序正文建立候選索引又會產生原本禁止的命中。
引句:「索引欄位對齊既有排序欄位（標題／別名／摘要／標籤／正文）。」
file: `scripts/lumos:2696`
file: `scripts/lumos:3009`
file: `scripts/lumos:8233`

5. 關聯推薦不是第三個全文搜尋器
severity: major
blocking: 是；必须保留圖結構與行級共引資料，才能承諾推薦行為。
`_reco_scores` 的候選來自 BFS 與解析後的 wikilink 共引，分數刻意區分同行乘二、同節點乘一，並計算鄰域 Jaccard。
五個平坦全文欄位不能還原这些關係；S6 必須說明索引僅加速引用者定位，或另存連結與行位置，不能直接把推薦換成文字 MATCH。
引句:「搜尋的候選階段、動手前的入口召回、關聯推薦，三者現在各自掃檔或共用剝碼原語；改成都問同一份索引。」
file: `scripts/lumos:9599`
file: `scripts/lumos:9626`

6. 微秒級 SQL 查詢沒有證明完整搜尋很快
severity: major
blocking: 是；效能驗收必須包含實際 CLI 的載入、更新、排序與輸出。
只讀記憶體重跑 513 篇：建索引 0.712 秒、SQL 查詢 0.13–1.63 毫秒，但沿用候選集 BM25F 重排另需 9–296 毫秒，初始化圖譜另需約 86 毫秒，現行 CLI 為 452–476 毫秒。
這個簡化實驗未涵蓋磁碟提交、刪改增量、互斥或 regex，且現有入口仍先讀完整圖譜；S1 必須固定端到端量測邊界，並指定全庫統計如何避免再次全庫讀檔斷詞。
引句:「這只證明「可行且快」，不證明排序品質不退步」
file: `scripts/lumos:320`
file: `scripts/lumos:2756`
file: `scripts/lumos:28080`

7. 修改時間與篇數無法判斷索引語意是否過期
severity: major
blocking: 是；索引有效性必須綁定語料身分、文件清單與索引語意版本。
CLI 升版改了斷詞器或合成標籤規則時，Markdown 的修改時間與篇數可以完全不變，S7 仍會接受語意已過期的索引。
應把 vault 身分、路徑清單及索引／合成規則版本纳入有效性判定，並測試同篇數刪增、改名及保留時間戳的內容替換。
引句:「判失效看檔案修改時間與篇數」
file: `scripts/lumos:2667`
file: `scripts/lumos:2696`

8. 退回現況會撤銷功能承諾，不只是變慢
severity: major
blocking: 是；降級路徑必須明訂與主路徑一致的語意或明確列出能力差異。
S3 承諾不看字面鏡像標籤、S4 讓多詞回退退場，但 S7 退回現況掃檔會重新搜尋原始 frontmatter，並依賴那個已宣布退場的回退機制。
「所有測試仍要能跑」不能決定哪些結果應相同；必須強制覆蓋 FTS5 缺席、索引損壞及不可寫環境，對照候選、排序與標籤語意。
引句:「索引不存在或壞掉要**出聲並退回現況的掃檔路徑**」
file: `scripts/lumos:3009`
file: `scripts/lumos:3089`

9. 子程序出聲，hook 使用者仍然聽不到
severity: major
blocking: 是；降級訊號必須穿過真正的注入消費端。
impact hook 捕捉子程序 stdout／stderr，成功時只解析 stdout 最後一行 JSON，沒有轉送成功路徑的 stderr。
因此 CLI 印降級警告仍可形成 spec 禁止的靜默降級；應把降級狀態放進 JSON 合約，並測試最終注入內容確實呈現。
引句:「不得靜默降級（靜默降級＝使用者以為在用索引、其實在跑慢路徑）。」
file: `scripts/hooks/claude/impact-hook.py:840`
file: `scripts/hooks/claude/impact-hook.py:870`

10. 現有金標評測比較的不是本次改動前後
severity: major
blocking: 是；驗收必須固定兩版程式，直接比較舊新版結果。
評測器目前比較同一版程式的 legacy 字母序與 ranked，兩臂均帶 `--no-any`；候選層一起改後，即使兩者都退步，ranked 相對 legacy 仍可通過。
S12 必須指定旧新版可執行檔、相同語料及相同查詢設定，另外覆蓋預設多詞路徑，不能拿既有 gate PASS 代替前後不退步。
引句:「速度、金標三指標、召回率三面各跑一次前後對照。」
file: `governance/eval/retrieval_eval.py:115`
file: `governance/eval/retrieval_eval.py:337`

11. 小型舊金標不能單獨證明擴召回後品質不退步
severity: major
blocking: 是；必须先處理新候選標註與評測涵蓋範圍。
實讀金標為 34 題搜尋、23 題編輯，固定於 `7fd214f`；新候選未標時，舊尺計零、condensed 尺剔除，兩者都不能判定新候選是否正確，而且固定舊快照不會驗到 S10 的本輪別名回填。
S12 應強制啟用既有消融未標閘、對新舊候選聯集盲標，另補獨立多詞與跨庫題並報逐題差異及不確定區間；這 57 題最多支持有限回歸檢查，不能支持泛化的不退步宣稱。
引句:「真正算數的只有金標三指標。」
file: `governance/eval/retrieval-goldset.json:2`
file: `governance/eval/retrieval_eval.py:187`
file: `governance/eval/retrieval_eval.py:253`
file: `governance/eval/retrieval_eval.py:401`

總結：最嚴重 severity 是 major，blocking 共 11 條。
