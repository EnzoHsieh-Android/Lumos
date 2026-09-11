# GraphRAG 對節點關聯 調研——來源與逐條讀到的內容(2026-09-11)

只記「實際打開讀到的」;沒讀到原文的標明。數字照原文,不自己換算。

## A. 本 repo 既有結論(先讀,避免重做)

- `Projects/檢索優化_調研`(2026-07-10):BM25F、HippoRAG(PPR)、LEGO-GraphRAG(圖分數必須與詞彙分數融合)、Borodin 2005 小圖實證(千級節點上 BFS 距離衰減 78% 勝 PageRank 48%)、共引+Jaccard、frecency(前提是要有「節點被誰讀過」的帳)。裁定 v1=BFS-decay+共引+Jaccard 與 BM25F 融合;PPR 留 v2。
- `Projects/檢索PPR邊權_計劃` + `Verification/2026-07-28_PPR邊權消融`:PPR 邊權**消融殺除**——edit 卷 train baseline nDCG@8 0.9831,PPR w0.2/0.4/0.6 約 0.981;前提 valid_under:train 有效題 n=5、free 池中位 3 席(池 ≤ k 時重排對 P@8 零鑑別)。
- `Systems/retrieval-ranking`:現行三面——search(CJK bigram+BM25F,nDCG@5 0.8556,n=30)、recommend(dormant)、impact/編輯時推播(固定席=事故+合約、動態閾、保底席、硬合約參考道、about_code 語意欄;held hook P@8 0.6842→0.7467)。
- `Projects/固定席扇出降權_計劃`:誠實天花板=判準文字與考卷裁決同源;train 8 題、過擬合風險高。
- `Projects/結構訊號補鏈D3_計劃`(todo):程式結構耦合補鏈,★啟動條件=出現 D1/D2 接不住、結構耦合接得住的實證 miss,目前零實證。
- 規模:本 repo 圖譜 475 篇、約 3,024 個 `[[…]]` 連結(2026-09-11 數);消費專案 Landmark 約 284 篇(記憶)。都是小圖。
- `docs/.usage-log.jsonl`:2026-07-29 起 778 筆,欄位只有 `ts`/`node`/`cmd`(show/context);`governance/runtime/hook-events.jsonl` 記 hook 跑了沒,不記推了哪些節點。(推播與查詢有沒有別處記帳 → 另派乾淨 agent 覆核,結果見筆記)

## B. 外部(7 月後,或 7 月那篇沒涵蓋的)

1. **RAG vs. GraphRAG: A Systematic Evaluation and Key Insights**(arXiv 2502.11371 v3,讀 HTML 全文摘要)
   - 單跳、細節型:RAG 贏(NQ F1 64.78 vs RaptorRAG 60.04);「RAG excels on detailed single-hop queries」。
   - 多跳:GraphRAG 小贏(MultiHop-RAG HippoRAG2 70.27% vs RAG 67.02%;HotpotQA Community-GraphRAG Local 61.66 vs RAG 60.04)。
   - 查詢導向摘要:RAG 較好(SQuALITY ROUGE-2 10.08 vs Community-GraphRAG Global 6.99)。
   - 用模型抽的知識圖丟資訊:答案實體只有約 65.8%(HotpotQA)/65.5%(NQ)進得了圖;triplets-only 檢索準確 39.20% vs RAG 88.60%。
   - 混合:Selection(依題型分流)+1.1%;Integration(兩者合併)+6.4%,「Integration generally achieves higher performance than Selection」。
2. **When to use Graphs in RAG(GraphRAG-Bench,ICLR 2026)**(arXiv 2506.05690 摘要頁+GitHub README)
   - 摘要原話:「GraphRAG frequently underperforms vanilla RAG on many real-world tasks」;題型四級:事實檢索、複雜推理、情境摘要、創意生成。
   - ⚠ 各題型的具體數字不在摘要頁與 README,**沒讀到全文,不引數字**。
3. **LazyGraphRAG**(Microsoft Research blog)
   - 索引期:NLP 名詞片語抽概念+共現圖+圖統計切階層社群,**不用 LLM 摘要**;索引成本 = vector RAG、為完整 GraphRAG 的 0.1%。
   - 查詢期:LLM 把查詢拆成 3–5 個子查詢、再用概念圖裡相符的概念改寫子查詢;best-first(相似度)+ breadth-first(社群)迭代加深;LLM 逐句做相關性測試,成本由單一「相關性測試預算」控制。
   - 預算 500 時 local/global 兩類題都勝過其他方法,查詢成本為 GraphRAG global search 的 4%。
4. **Claude Code:agentic search 取代 RAG**(Boris Cherny 在 X 的貼文,經搜尋結果引文)
   - 「Early versions of Claude Code used RAG + a local vector db, but we found pretty quickly that agentic search generally works better. It is also simpler and doesn't have the same issues around security, privacy, staleness, and reliability.」
5. **GRASP: Graph Agentic Search over Propositions**(arXiv 2605.16598,2026-05,摘要頁)
   - 把多跳問題拆成有相依順序的計劃,依複雜度調子 agent 數;三層圖(實體 / 命題 / 段落),命題層用 reciprocal-rank voting 拉召回。
   - MuSiQue、2WikiMultihopQA 最高準確,token 比 IRCoT+HippoRAG2 少 40–50%;LongBench 領先且比次佳少 30% token。
6. **LocAgent: Graph-Guided LLM Agents for Code Localization**(ACL 2025,搜尋結果)
   - 把 codebase 解析成有向異質圖(顯性+隱性關係),給 agent 一組統一的圖探索工具做多跳導航;fine-tune 開源模型可比專有模型,成本降 86%。⚠ 沒讀全文,定位準確率數字未引。

## C. 沒查 / 沒讀到的(誠實缺口)

- GraphRAG-Bench 全文各題型數字;PathRAG(路徑式提示)、RAPTOR、Graphiti(雙時間軸邊)只憑印象,**本次沒讀原文,不當證據用**。
- 消費專案圖譜的連結密度、候選池大小:沒量。

## D. 乾淨 agent 覆核(2026-09-11,原始問題:lumos 記不記推播、查詢、讀取的工作階段、有沒有離線量測)

- (a) 推播清單:lumos 不記;Claude Code 逐字稿有(hook_additional_context,帶 sessionId/toolUseID/全文;「必看」段無分數、「可能相關」段有分數)。dispatch-lens 快取是效能快取,不是紀錄帳。impact hook 只認 Edit/Write/MultiEdit/apply_patch。
- (b) search 查詢:lumos 不記(實跑兩次、usage-log 行數不變);查詢與輸出只在逐字稿的 Bash 輸出裡(推論)。
- (c) 讀取對 session:沒有欄位;usage-log 只有 {ts,node,cmd}、無時區;「每支命令寫進 usage-log」已被 全repo審視 F08 否決;usage-log 至今無人讀,退場期限 REVISIT 2026-11-19。
- (d) 離線量測:有——`governance/eval/lens-utilization/recount.py`(主session鏡頭利用率_計劃),2026-09-04 跑過一次;人工抽樣 REVISIT 2026-09-17 未做。
- 據此修正建議一的做法(見筆記「建議一」★修正★段)。
