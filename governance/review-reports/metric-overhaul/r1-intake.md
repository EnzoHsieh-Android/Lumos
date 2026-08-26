# r1-intake — 首輪排乾(2026-08-26,loop=metric-overhaul)

排乾員唯讀掃描 7 命中,全屬排乾類修真檔(語意類修正前後如下),不算 findings;佐證均經排乾員開檔重現。
1. S0/S4 與標註刷新條款撞名(存在類)→ 兩處標明出處。
2. [S1] 範圍矛盾(語意類):原文只點名 P@8/nDCG@8/hook,search 主閘 nDCG@5 未列。修正後:全品質尺列名(nDCG@5/MRR/R@10/P@8/nDCG@8/lift),並記 hook_p=fusion_p 同數字事實與兩處收斂點(:339/:382)。
3. pin_noise 矛盾(語意類):新增 [S3b] 明裁固定席噪音閘維持「未標=噪音」(策展訊號非排序尺)。
4. 消融 rc3 閘存在理由被抽(語意類):新增 [S3c] 裁退場、coverage 標記接手。
5. Landmark 連紅次數:帳上重算=4 次(08-05/12/19/26),文件補次數;我對使用者口頭說過「五次」是錯的,已更正。
6. DEP 補地基盤點連結。
其餘機械宣稱(6 項)逐條屬實:_labels_of 位置/08-22 消融出處/刻意不做原句/三件基礎設施/history 欄形/metric_rev 不存在。

## r1 收貨補記(外家席)
ext 兩條 finding 引句 quote-check 全數錨定失敗(改寫非逐字)。依「可疑席不准直接丟、先機械重現」紀律,編排者重現:
- ext-f1:_macro 等權平均(retrieval_eval.py:314/:436)HIT;單題 1/8 覆蓋反例算術 1/6=0.167 > 門檻緊繃度 0.033 HIT → 撈回,severity blocker 維持。
- ext-f2:repin 合約 unjudged==0(refresh_labels.py help :6)HIT;「repin 時兩尺重合→雙報期學不到門檻映射」邏輯成立 → 撈回,severity major 維持。
重現指令與輸出見 session 留痕;撈回≠豁免,兩條照折。
