# 問世界第二輪:brownfield 節點還原的世界解調研(2026-08-24,Enzo 指示網搜)

> 由 general-purpose agent 網搜六方向產出;摘錄要點+全部來源連結。折入結論見計劃筆記 PRIOR-ART 與各步驟「世界解:」標記。

## 1. Feature location / concept location
Wilde & Scully「Software Reconnaissance」(1995);Chen & Rajlich ASDG(2000);PROMESIR(TSE 2007);Dit/Revelle/Gethers/Poshyvanyk 分類學綜述(2013)。四族:文字(IR)/靜態(依賴圖)/動態(執行軌跡)/歷史(co-change);混合勝單一。Reconnaissance 招:功能會踩/不會踩兩情境各跑一次收軌跡相減=該功能專屬 code;兩情境交集=共用基礎設施(承重牆機械化定義)。minify 靜態定位查不到成熟解(動態法/source map 之外);Spring 框架感知分析器(JASMINE/TAI-E/YASA,未確認成熟度)對零依賴哲學太重。
折入:步驟 1 第四級動態差分錨點+錨點信度分級(兩獨立技術交叉才高信度);步驟 2 第三來源 co-change+軌跡交集。

## 2. Software archaeology / MSR
Hipikat(Cubranic & Murphy ~2003-2005:code/bug 單/郵件/文件連成專案記憶);git pickaxe(-S/-G)與 log -L;MSR 綜述:設計理由主要在 issue tracker;ADR 體系(Nygard 2011、adr-tools、log4brains);CommitDistill(2026,未確認成熟度)。squash 後:中間 commit 沒了,但 squash 訊息留 PR 號,PR/issue 討論串存活——第一現場移到 forge。
折入:步驟 3 招式具體化(-S/-G/-L、blame ^ 重跳、squash→PR 號→討論串、issue 優先);決策四欄與 Nygard ADR 同構(確認對齊,不引工具)。不採:log4brains 是往後寫的工具,對往回挖沒幫助;CommitDistill 太新。

## 3. Feathers《Working Effectively with Legacy Code》(2004)
characterization tests(釘現在的行為,不判對錯)、seams(不改這裡 code 就能換行為的切點)、legacy change algorithm;golden master/approval testing(Nicolas Carlo 整理);approval 100% 覆蓋也要配 mutation 驗證會翻紅。
折入:步驟 5 「待 seam」標記、golden master 適合 AI 代產、mutation 當升格驗收、語意對齊(測試證「改了就壞」是真的,不證行為是對的)。不採:整套「先測試後改碼」為改碼設計,知識還原流程只吸收這段。

## 4. Strangler fig / Living documentation
Strangler fig(Fowler 2004;Azure/AWS 正式 pattern)=漸進接管正典——惰性生長的世界名字。Martraire《Living Documentation》(2019):知識多半已在系統裡只是形式不對;curation 勝 creation;就地增註。
折入:步驟 0 先策展再自產;步驟 4 知識分工(短半衰期進 code 註解,長脈絡進圖譜)。不採:自動生成鏈預設有人維護 code 內標記,對接手第 0 天沒用。

## 5. 2024-2026 AI 專用做法
ArchAgent(arXiv 2601.13007:靜態分析+LLM,消融證明餵依賴脈絡提升正確率——支持步驟 2 在步驟 4 前);DocAgent(arXiv 2504.08725:五 agent 含 Verifier,依賴拓撲序先底層後上層,消融證明順序至關重要;Truthfulness 檢查=引用實體存在性,細節未確認);DeepDiscovery(2026,未確認);hallucination 文獻 factuality vs faithfulness——逆向補 why 是 faithfulness 風險,主流解 citation-grounded(=lumos 證據身分制的文獻名字);Aider repo map(tree-sitter+PageRank+預算截斷)、Cline Memory Bank、CLAUDE.md 慣例——「先建 map 再動手」已是業界標配。
折入:步驟 6 前置引用實體機械掃描;步驟 3 推測不准引具體識別子;步驟 4 拓撲序;步驟 0 可拿 repo map 思路當初稿產生器(保持惰性)。

## 6. Architecture recovery
Reflexion Models(Murphy/Notkin/Sullivan,FSE 1995):人猜高層模型→工具算實際依賴對帳(收斂/背離/缺席)→迭代;NetBSD 25 萬行幾小時可用。自動聚類族(整倉攤平)不採——違反惰性哲學、對業務 why 無貢獻;綜述:僅約 54% recovery 方法有工具。
折入:步驟 0 導覽頁=reflexion 式假設+三態對帳鉤。

## 綜合排序(調研員裁)
1. 動態差分定位(補唯一能力死角,一招帶承重牆機械化) 2. reflexion 假設對帳(成本近零,把最弱一步變會收斂) 3. 引用實體機械掃描(便宜可重算,正對「閘只留可重算的」)。緊追:seam/golden master/mutation;squash→PR 考古路線。

## 誠實聲明
minified 靜態定位查不到成熟解;software archaeology 一詞出處年份未確認;JASMINE/TAI-E/YASA、DeepDiscovery、DocAgent Verifier 內部機制、CommitDistill 成熟度皆未確認;書名/工具/論文皆有搜尋實據無自造。

## Sources
- Dit et al., Feature Location in Source Code: A Taxonomy and Survey (2013) https://onlinelibrary.wiley.com/doi/full/10.1002/smr.567
- Murphy & Notkin, Software Reflexion Models (FSE 1995) https://www.cs.ubc.ca/~murphy/papers/rm/fse95.html
- MSR for software architecture — systematic mapping (2025) https://www.sciencedirect.com/science/article/pii/S0950584925000163
- Hipikat https://www.semanticscholar.org/paper/fc041feb5271efca959d0f54722338d419330cf0
- Git pickaxe https://git-scm.com/book/en/v2/Git-Tools-Searching ; blame 招式 https://tekin.co.uk/2020/11/patterns-for-searching-git-revision-histories
- GitHub squash merge https://docs.github.com/en/pull-requests/reference/pull-request-merges
- log4brains https://github.com/thomvaill/log4brains ; ADR tooling https://adr.github.io/adr-tooling/
- Characterization test https://en.wikipedia.org/wiki/Characterization_test ; understandlegacycode.com https://understandlegacycode.com/blog/characterization-tests-or-approval-tests/
- Strangler fig https://en.wikipedia.org/wiki/Strangler_fig_pattern ; Azure https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig
- Martraire, Living Documentation https://www.oreilly.com/library/view/living-documentation-continuous/9780134689418/
- ArchAgent (2026) https://arxiv.org/abs/2601.13007 ; DocAgent (2025) https://arxiv.org/abs/2504.08725
- Hallucination survey https://dl.acm.org/doi/10.1145/3703155 ; faithfulness https://arxiv.org/pdf/2501.00269
- CommitDistill (2026) https://arxiv.org/html/2605.18284
- repo map / memory bank 實務 https://hackernoon.com/the-complete-guide-to-ai-agent-memory-files-claudemd-agentsmd-and-beyond
