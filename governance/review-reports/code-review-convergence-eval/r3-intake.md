# 第三輪收貨與處置

八個有效席全部收齊後才修，規格major另由乾淨辯方同意。原資安席接觸舊報告而排除，原件保留；r3-security是隔離材料上的新冷席。通才2600、架構至少3229行超限，屬弱證據；其他席按實讀記帳，不灌零成本。

| ID | 重現 | 處置與歸因 |
|---|---|---|
| preconditions | HIT | 規格及辯方同意三個新測試缺獨立前置斷言，formal invariant違反major；補實際字元、磁碟讀回、型別與大小。非產品回歸。 |
| numeric-equivalence | HIT | 架構同輸入驗c909接受1/1.0、cd0誤報衝突；直接歸因規範序列指紋。改逐項JSON語義比較，數值相等而布林獨立；巢狀及反序先紅後綠。只有此項列產品regression_set。 |
| record-reason | HIT | 正常產品已拒收，舊測試只驗DataError可能假綠；改釘input-record-limit並核磁碟大小，非產品回歸。 |
| template-boundary | HIT | 兩端均接受129字loop，屬既有邊界不一致；共用manifest識別規則並在真正CLI拒收。 |
| template-case | HIT | 邊界席指出守衛漏掉128/129案例；補長度現場斷言及helper/CLI正反例，非產品回歸。 |

25案紅綠在r3-fixes-before/after.log，兩個新增行為案例修前紅、修後綠，23個保留候選均仍綠。三個現場斷言是守衛增強，不虛構產品修前失敗。原23案固定兩端r3-paired保留19、修好4；來源bundle與restore紀錄保存可還原版本。

quote-material只把原snapshot、graph鏡頭及派工允許讀的cd0原始葉子合併以核引用；原派工單、snapshot與binding不改。它不是新審輪，也不把合併行數冒充每席實讀。機械錨定不證明語義成立。

receipt指紋不代表独立產品執行；尚無真實模型試行或實輪轮數改善證據。2026-10-21首次實輪入口重驗保留、回歸、缺件及成本。
