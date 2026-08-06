---
type: project
status: doing
created: 2026-08-06
updated: 2026-08-06
tags:
  - type/project
  - status/doing
summary: |
  KEY:三件借鑒落地計劃(2026-08-06 調研日報三 gap × ClawBench/evidra 深讀)——S1 席位自證粗篩(零 AI 掃 review-reports 留痕:引了沒讀過的檔/有講沒做/越界另記帳)｜S2 canary+考卷 SNR 效度自檢(每題醒睡分辨力÷重跑雜訊,SNR<1=量運氣該換題)｜S3 Growth test 準入三問(新閘前必答:真害過人嗎/風格類出界/既有小修蓋得住)
  KEY:PRIOR-ART=borrow-design:ClawBench(openclaw/shellbench)trace-scoring+SNR 變異分解+judge 永不救活機械紅燈;evidra(vitas/evidra)prescribe/report 對帳+retry/repair/thrashing 三分+detector≤15 防膨脹
  KEY:刻意不搬(防回鍋)——動力系統診斷(過重/散文空轉)、Prometheus+簽名鏈(多租戶需求)、pass^k 多次重跑(成本×3 留未來)
  FLAG:DECISION
---
# 驗證層自證三件_計劃

> 緣起:2026-08-06 調研日報三個 gap(唯讀席不會喊卡/辯方攔不住越界/canary 考卷效度沒查過)＋同日 GitHub 深讀兩個新星專案(ClawBench、evidra),三個 gap 都找到已被世界驗證的機械解法。主軸=「這一席到底看到了什麼」不再信自述,改查留痕。

PRIOR-ART: ① 最小解層級——全數是既有留痕(review-reports 席報告/處置帳/每週考卷 runner)上加零 AI 讀取面,無新治理層、無新依賴。② 世界解=真搜真讀兩個 repo:**ClawBench**(openclaw/shellbench,⭐134,MIT)——trace-based scoring(read-before-write/self-verification 從執行軌跡機械判)、每題 SNR=跨模型變異÷同模型重跑變異(40 題殺 21 題雜訊題)、13 種失敗模式決定論分類、「judge 永不救活機械紅燈」寫成測試守著;**evidra**(vitas/evidra,⭐15,Apache-2.0)——prescribe→execute→report 三步協議+8 個純函數 signal(protocol_violation 對帳「有講沒做/有做沒講」、retry/repair/thrashing 三分、Growth test 準入三問+detector≤15 硬上限、明文禁 ML/自適應閾值=「同證據恆同分」)。③ 裁定=**borrow-design**(兩邊都只搬設計不搬碼:ClawBench 是 python 評測 harness、evidra 是 Go+Prometheus 多租戶棧,依賴與場景都不合;演算法本身零依賴可自寫)。

## 三件(按便宜×對上日報 gap 排序)

### S1 席位自證粗篩(borrow ClawBench trace-scoring + evidra protocol_violation)
零 AI 腳本吃 review-reports 既有留痕。**「引句對得上凍結快照嗎」已有 `lumos quote-check` 上線(收貨流程織入,rc1 欄位即名 `unverified`)——S1 不重造**,只做 quote-check 沒蓋的兩類:
- **有講沒做對帳**(evidra protocol_violation 直搬語彙):派工宣告要查的範圍/鏡頭沒出現在報告=`unreported`;報告引用了派工範圍外的檔=`out_of_scope`(越界另記一本、不進收斂帳——日報 gap② 的機械解)。
- **file:line 指涉實在性**:席 finding 引的 repo 檔案路徑/行號機械驗存在與在範圍內(borrow ClawBench read-before-write 精神;與 quote-check 的分工=quote-check 驗「引句↔spec 快照」,S1 驗「指涉↔repo 現實」,同 refcheck 之於 spec 的關係)。
- 產出:每輪 loop 收貨時 rc0 報表,先觀測不擋(canary 降級同款路徑:先量命中率再議升閘)。

### S2 canary/考卷 SNR 效度自檢(borrow ClawBench variance decomposition)
- 公式:每題 SNR=醒席/睡席(或跨模型)分辨力÷同席重跑雜訊;SNR<1 的題=在量猜運氣,標記換題。
- 對象:canary 記錄帳 `docs/.canary-log.jsonl`(355 筆,含 type a-d/caught-missed/auditor,可分組)+每週檢索考卷;掛進既有每週 runner(`governance/autonomous-loop.sh` 驅動 `governance/eval/` 腳本),不建新排程。⚠ `governance/canary-samples/` 目前只有 README 空殼(存放慣例未落地),S2 不依賴它。
- 同場補:canary 型別改派工當下隨機抽(日報 gap③「固定輪替=可猜」)。

### S3 Growth test 準入三問(borrow evidra scope boundaries)
- 治理帳/skill 加新閘/新 detector 前必答:①這 pattern 真造成過事故嗎(要能指到事故節點/日報)②是不是風格偏好類關切(出界)③既有機制小修蓋得住嗎。答不全=不准加。
- 落點:lumos-project-notes 或 design-loop skill 文本一段,零代碼。

## 刻意不搬(記帳防回鍋)
- ClawBench 動力系統診斷(特徵向量/參與比/本徵值/regime 分類)——對單人治理迴圈過重,散文空轉風險;日報實證 design-loop 對 shell/glue 散文空轉。
- evidra Prometheus metrics/Ed25519 簽名鏈/signal spec 版本遷移儀式——多租戶平台需求,零依賴家規排除。
- ClawBench pass^k 多次重跑——席位跑三次成本×3,先靠 S1/S2 便宜半,重跑留未來方向。

## 射程聲明(borrow evidra 誠實文化)
S1 測的是「報告與留痕的協議內一致性」,不是真實世界正確性——席若一致地說謊(引句自己編但格式對)抓不到;那層靠既有辯方+canary。S2 的 SNR 需要醒/睡兩態樣本,睡態樣本現只有 missed 留痕,樣本少時 SNR 本身不穩(min样本數待定)。

## 實務隱患
- **併發**:S1/S2 皆為離線批次讀取(收貨時/每週 runner 單進程),不進熱路徑、無共享資源競爭;review-reports 為 append-only 檔案,掃描與寫入不同時。
- **效能**:全量重放歷史 review-reports 為一次性驗收動作,常態每輪只掃當輪 3-5 份報告,量級 KB,無效能面。
- **資源**:純檔案讀取+stdout 報表,無連線/鎖。
- **[prod-irreversible]**:三件皆無不可逆動作——S1 rc0 觀測不擋、S2 產清單人裁換題、S3 純文本;回滾=刪腳本/revert 文本,無資料遷移。
- **[self-governance] 誤擋逃生口**:S1 v1 恆 rc0(觀測),不存在誤擋;未來若升閘須另立計劃過 loop,並依 Growth test 三問(S3)自審——升閘決策本身留痕於治理帳。S2 換題為人裁非自動,誤判 SNR 最壞=誤換一題,樣本少時射程聲明已載明不穩。

## 審計修正紀錄
- **pre-flight(2026-08-06,機械排乾,不算 loop findings)**:①S2 資料源 `governance/canary-samples/` 實為 README 空殼,改指 `docs/.canary-log.jsonl`+補每週 runner 真實路徑 ②S1「看了沒」與已上線 `lumos quote-check` 機制重複(PRIOR-ART 鐵則①漏查自家),改為 quote-check 分工聲明+只留未覆蓋的兩類 ③驗收線誤把 canary-missed(沒看出植入的假)當 unverified_citation(自己引不實指涉)證據,兩種失敗模式已切開。

## 驗收線(先粗)
- S1:對歷史 review-reports(32 份)全量重放,人工抽 10 筆比對粗篩判定與人工判定一致;殺傷力驗證=至少找到一筆真實的 `out_of_scope` 或指涉不實案例(⚠ canary-missed 記錄測的是「沒看出植入的假」,與 S1 抓的「自己引了不實指涉」是兩種失敗模式,不得直接拿 missed 帳當 S1 命中證據——殺傷力案例得從重放結果人工確認)。
- S2:對 `docs/.canary-log.jsonl` 分組算出每 canary 型別 SNR 並產出「該換題清單」;清單非空且人審同意其中至少一題確實該換。
- S3:skill 文本 diff+下一次新機制提案實際走過三問留痕。
