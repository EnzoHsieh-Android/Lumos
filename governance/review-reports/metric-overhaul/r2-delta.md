### d-f1 「repin 時兩尺數值恆等」在 search 面 MRR 不成立
severity: major
引句:「repin 合約=評測母體 unjudged==0,此時 condensed 與舊尺**數值恆等**」
佐證:file: `governance/eval/retrieval_eval.py:338`
佐證:file: `governance/eval/retrieval_eval.py:44`
說明:觸及集=兩臂各前 10,但 MRR 掃全量 legacy 列表;第 11 名以後的未標節點讓兩尺 index 走法不同,恆等破功。ndcg@5/recall@10/P@8/nDCG@8 視窗都在觸及集內確實恆等——例外精確限縮在 MRR,spec 文字「全部品質尺恆等」沒挑出來。

### d-f2 棘輪鍵擴後切換輪必然「無基線重置」,與「零重錨」自我矛盾
severity: major
引句:「棘輪同尺比較鍵擴為 (goldset_rev, metric_rev)——公式版本與標註資料版本是兩條軸,棘輪兩處(:300/:528)同步收」
佐證:file: `governance/eval/retrieval_eval.py:295`
佐證:file: `governance/eval/retrieval_eval.py:508`
說明:新 metric_rev 第一筆結構上保證落「找不到同鍵 PASS→這次當基線」分支——切換輪(唯一需要驗連續性的時刻)棘輪自動放行,condensed 實作若有 bug 會被收作新基線。基線重置=隱性重錨且無驗證,被悄悄繞過而非解決。

### d-f3 [S5] 用正文改「刻意不做」記翻案,繞過 decision-supersede 機制——標準查法假陰性
severity: major
引句:「段補被翻註記(2026-08-26 Enzo 裁,詳本計劃 d1)」
佐證:file: `scripts/lumos:6576`
說明:標註刷新_計劃無 decisions 條目,「刻意不做」是正文;lumos decisions --superseded 只讀 frontmatter——照字面做,下個 session 標準查法查「翻案了嗎」得到「無」。正確做法=回溯補一條 08-17 decisions 條目再 decision-supersede 指向本計劃 d1。

## 其餘查過未達 major
nested 欄與兩個既有讀者乾淨;ceil(k/2) 在 n=1 題庫的安全網弱化屬已劃邊界。
