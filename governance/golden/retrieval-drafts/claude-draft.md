# Claude 草案(盲寫)

## 1. 排序公式與資料流
- Token:CJK 連續段切字元 bigram + ASCII \w+ 小寫詞,查詢同法。~100 節點每次查詢即時全掃建記憶體倒排(免持久索引,量測 <0.5s 才成立,超標再快取)。
- BM25F:虛擬文件 tf = 4×title(stem+aliases) + 3×KEY行 + 3×tags + 2×summary其餘 + 1×body;長度用加權長;Whoosh 公式 B=0.75/K1=1.2;IDF=log(N/(df+1))+1。
- search 預設 ranked top-20 帶分數與命中欄位徽章;--top N;--files-only/--regex 保留(regex 模式不排序,照舊)。

## 2. 相關推薦分數
- rel(a,b)=0.5×BFS-decay(1/2^(k-1),k=無向最短距,每節點一次,k≤3) + 0.3×共引(被同節點共同引用次數,同一行×2,cap 3) + 0.2×Jaccard(無向鄰域)。邊型權重進 decay:verified_by/plan_refs=1.0,related=0.9,body-wikilink=0.7(合約鏈邊比散文連結硬)。
- 融合:search 場景純 BM25F(v1 不混圖,LEGO 教訓適用於「推薦」非「查詢」);推薦場景(context/impact)純圖分。真正融合點=impact hook(見 3)。
- 介面:context 尾部加「相關節點 top-8(分數)」;不開新頂層命令(44 不變,省六處計數同步)。

## 3. hook 降噪
- 每節點分 = BFS-decay×邊型權 + direct 引用 2.0 + pitfall 命中 +1.5;含 ★INVARIANT★ 的節點 ×1.3(合約優先浮出)。
- top-10 + 閾值 0.15 以下省略;尾行「+N 低分節點(--json 全量)」。
- 去冗餘(MMR-lite):同主題姐妹節點(X_計劃/X_實作計畫 同前綴)只列最高分+「(+姐妹 N)」。事故(pitfall)不降噪全列。

## 4. CLI 變更
search --top/--ranked 預設;impact --top(default 10);context 加相關節點段。無新頂層命令。

## 5. frecency
v1 不做:要開「讀取事件帳」= 新寫入面(hook 每次讀都寫檔)+成本未證;等 1-3 落地後拿事件帳 A/B 再議(記 v2)。

## 6. 評測(驗收核心)
- 金標一:cochange 規則當免標註 proxy——歷史高共改節點對=相關(自家狗糧)。
- 金標二:人工標 20 查詢×相關節點(本 vault+Landmark vault)。
- 指標 P@5/MRR;A/B:bigram vs substring、BFS-decay vs 現行 hop、±共引。腳本 governance/eval/retrieval_eval.py。

## 7. 最可疑點
Borodin BFS 最佳出自有向 web 圖(B/F 交替語意);本 vault 無向化後 1/2^k 是否仍優、以及密集叢集「在題」時抗劫持反而可能壓掉真相關——評測第一題就驗這個。
