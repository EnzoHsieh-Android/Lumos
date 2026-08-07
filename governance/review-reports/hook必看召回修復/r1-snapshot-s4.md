---
type: project
status: doing
created: 2026-08-07
updated: 2026-08-07
tags:
  - type/project
  - status/doing
summary: |
  KEY:治全系統唯一紅燈(hook P@8 0.639/must recall 0.6)——2026-08-07 驗屍 11 筆必看 miss 歸因:①直連被動態閾砍 6 筆(direct 基底 0.30+L≈0<動態閾 0.65×max_free;v1.1/v1.2 買精度的明碼代價)②檔名變體 2 筆③連結缺失 3 筆
  KEY:兩帖藥=R1 直連保底席(free 池零 direct 才觸發,補 min(N,缺口) 個 rescued 標記,名額外加)+R2 basename 唯一才容錯比對;第三帖(Drift 符號錨/TLR 補連結)deferred 另立
  KEY:裁決=考卷 A/B 沿 PPR 慣例(train 網格→held 確認→±0.02 帶寬→輸刪碼);不動閾/基底/固定席;不為過卷補語料引用(Goodhart)
  FLAG:DECISION
---
# hook必看召回修復_計劃

> 緣起:2026-08-07 全系統掃描——每週考卷唯一連續紅燈=hook P@8 0.639(閘 0.70)、must_in_out_recall 0.6。對 goldset 快照(285d429c)全量重放驗屍,11 筆必看 miss 逐筆歸因,三種死法比例定案,藥按病開。

PRIOR-ART: ① 最小解層級——全數為既有 impact --ranked 管線的謂詞/參數小修+考卷 A/B 裁決,無新機制、無新依賴;落點=`cmd_impact` ranked 分支 free/thresh 計算段(scripts/lumos ~11966 起)與 `_impact_reverse_lookup` token 比對(~11429)。裁決模式沿 [[Projects/檢索PPR邊權_計劃]] 慣例(train 網格→held 確認→±0.02 帶寬→輸=刪碼),**帶一處明示偏離**:勝出軸=must recall 非 P@8(本計劃修的是 recall 紅燈,P 是護欄非獎盃),見驗收線。② 內部 prior-art:[[Verification/2026-07-11_hook面v1.1轉正]]——v1.1 調參(閾 0.25→0.55/direct 基底 0.5→0.3)買精度 +20pp 的**明碼代價=必看視野 28/30→19/30**,本紅燈即該筆交易的帳單;固定席機制(合約/事故 direct 保送)已存在,本計劃的保底席為其無標記版之延伸。③ 世界解(2026-08-07 調研,列第三帖藥、本計劃不做):Drift(fiberplane)`路徑#符號@sha` 錨定+AST 指紋過期偵測;TLR(LLM 連結恢復,arXiv 2509.05585/2508.12232)——僅離線候選生成+人放行姿勢合法(同證據恆同分家規)。④ 裁定=borrow-design(裁決協定借自家、錨定思路借 Drift 但 deferred)。

## 驗屍證據(2026-08-07,快照 285d429c 全量重放,11 筆必看 miss)

| 死法 | 筆數 | 機轉 | 例 |
|------|------|------|-----|
| ①直連被閾砍 | 6 | 反查 direct 有中;direct 基底 0.30+L(delta code 字串 vs 中文筆記詞彙相似≈0)<動態閾(現行係數 `LUMOS_IMPACT_DYN_COEF`=0.65,閾=0.65×max_free,E14 當場≈0.55——非係數本身;⚠ [[Systems/retrieval-ranking]] 節點仍記舊係數 .55,已過期待同步)→ 被砍。E14 全場僅 2 候選、前 8 有空位,唯一 direct 仍出局 | E14 `lint-watch-check.sh`→`lint-version-watch` raw 層 direct 命中、ranked 層消失 |
| ②檔名變體 | 2 | 節點引檔名/變體非完整路徑,反查只認 token 一字不差 | E18 `cross-family-audit`、E20 `convergence-evidence-gate` |
| ③連結缺失 | 3 | 節點壓根無該檔引用;hop1 可達但衰減+L=0 | E05/E12 三筆 Verification/計劃節點 |

> 語意鴻溝的真實老巢:delta=code 字串、節點=中文散文,BM25F 相似分近乎隨機——機制卻以 L 為 direct 的救生索。

## 兩帖藥(本計劃範圍)

### R1 直連保底席(治死法①)
- 規則:free 池(動態閾後)中 direct 節點數=0 且存在被閾砍的 direct → 以分數最高的 min(N,缺口) 個補入輸出,標 `rescued: true`(觀測欄位,籍貫沿 results 既有 `origin` 欄語意,eval 可分拆歸因);**名額外加不擠掉過閾者**,仍受 --top 上限;N 由 train 網格定(候選 1/2)。
- 刻意保守:僅「free 池零 direct」時觸發——單體檔 19 direct 的舊噪音場景(v1.0 病)free 池必有 direct,保底不觸發,精度不回退。
- 固定席不動(合約/事故保送機制原樣)。

### R2 檔名變體容錯(治死法②)
- 反查比對加一條:token 以 `/<basename>` 結尾或 token==basename 也算命中,**且該 basename 在 repo 唯一**(多檔同名=歧義,跳過不猜);命中標 `hit: basename-match`(與 body-inline-code 分開記,eval 可歸因)。

### 刻意不做(記帳防回鍋)
- 死法③(連結缺失)=第三帖藥:Drift 式符號錨/TLR 離線補連結——等 R1+R2 落地後看殘餘 recall 再議,另立計劃。
- 不動閾值本身(0.55 買到的精度不退)、不動 direct 基底、不動固定席、不碰 search 面。
- 不為過考卷回頭補 goldset 語料的引用(污染考卷=Goodhart)。

## 實務隱患
- **併發/效能/資源**:純排序謂詞,無新 I/O;basename 唯一性檢查=新建一次性 basename→路徑索引(O(repo 檔數) 單次建立,impact 呼叫內存活;如實承認是新 I/O,非既有快取——impact 管線現無檔案枚舉快取)。
- **[self-governance]**:排序 advisory+考卷機械裁決;最壞=兩臂皆輸、刪碼零殘留(沿 PPR 前例)。誤救(rescued 進了不相關節點)=P@8 掉,考卷會抓。
- **[prod-irreversible]**:不適用,純讀+git 可逆。

## 審計修正紀錄
- **pre-flight(2026-08-07,機械排乾,不算 loop findings)**:①動態閾數字勘誤——0.55 是 E14 當場閾值(0.65×max_free),現行係數實為 0.65(v1.2 調緊),原文誤標;連帶發現 [[Systems/retrieval-ranking]] 節點仍記舊係數,列同步義務 ②「既有 ls-files 快取」不存在,改為如實承認新建一次性 basename 索引 ③R1 touchpoint 行段修正+刪 `_reco_fused` 誤指(那是 dormant 的推薦面) ④裁決規則補「平局不轉正」並明示偏離 PPR 慣例之處(勝出軸=recall)。

## 驗收線(A/B,裁決規則沿 PPR 計劃慣例)
- 兩臂:A=baseline 現行;B=R1+R2(R1 的 N 於 train 網格 1/2 選定後凍結)。
- gate(兩條合取):①護欄=held 上 B 臂 P@8 不劣於 A 超 0.02 ②勝出=held must_in_out_recall 提升至少一筆(以救回筆數計 ≥+1);兩條都過才轉正,**只不劣不提升=平局留 baseline**(對齊 PPR 慣例「平局不過」精神;勝出軸取 recall 為明示偏離,理由見 PRIOR-ART)。rescued/basename-match 兩欄位可歸因分拆如實記錄。
- 轉正=B 過 gate;記 `retrieval-eval-history.jsonl`;輸=刪碼留墓碑。
- 測試:`t_impact_direct_rescue`(零 direct 觸發/有 direct 不觸發/名額上限/rescued 欄位)、`t_impact_basename_match`(變體命中/多檔同名跳過/hit 欄位)。
