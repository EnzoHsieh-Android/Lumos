# r1 intake

preflight-4: ran

開輪依據：推送前規格閘因第 59 行字樣「production」判本計劃風險高（原句是「不修改 production」，指不改原歷史產品碼）；照判定走設計審。實作已在本分支完成，本輪審的是計劃文字與實作是否相符。

## 前掃（便宜代理，四類）

- ① 未定義的詞 5 條：「轉態」補定義（同一支測試修復前紅、修復後綠）；「現場前置斷言」補定義（證明被測情境真的成立的那條斷言）；「無手冊控制對正式手冊」改寫為控制組／實驗組。「fixture」「受限 unittest 語法」判讀為後文已定義或非首次出現於本計劃的關鍵詞，不改。
- ② 壞引用：無。
- ③ 範圍矛盾 1 條：「固定三案」與「首批選錯 Java 端點、改正後另批重跑」。判讀：後者是固定前的資格預檢歷程，最終仍固定三案，不矛盾，不改。
- ④ 機械宣稱驗語意：S1、S2、S3 三條前掃皆判成立（historical_case_corpus.py 兩版各跑弱強測試、report 保存版本／檔案與測試 SHA／執行器 SHA／原始輸出／instrument、全部 qualified 才凍結）。編排者另實跑兩個入口：重播 9 秒 rc0、preflight_passed true，案例集 18 秒 rc0、controls_passed true、cells 12、model_calls 0。

## 收貨

四席收齊後才一次寫入卷證；通才席引句把全形標點抄成半形，退回只修引句後重收，四份全數錨定。手冊讀活檔一事三席（ARC-1、HND-1、GEN-3）獨立指出，GEN-3 實測前兩批 manifest 的手冊 1129 字、現行切出 1234 字；逾時懲罰兩席（GEN-2、BND-1）各自以 8 個方法實測 invalid。多席一致者直接折。本計劃屬不隨工具安裝的評測研究腳本，下一批模型實驗尚未開跑，方法論與入口缺陷以「下一批開跑前必須完成」七項折入計劃並設 REVISIT，已完成兩批的平手結論不受影響。

## 重現與處置

| id | source | severity | reproduce | disposal | evidence |
|---|---|---|---|---|---|
| ARC-1 | 架構對齊 | major | HIT | folded | 計劃改正為執行期切字串、前兩批全文在 manifest；前置清單第 1 項 |
| HND-1 | 接手 | major | HIT | folded | 同 ARC-1 |
| GEN-3 | 通才 | major | HIT | folded | 同 ARC-1 |
| HND-2 | 接手 | major | HIT | folded | RETIRE-IF 寫明資格只比索引、effect_candidates 是寫死清單、退場看 12 列 qualified；前置清單第 6 項 |
| GEN-1 | 通才 | major | HIT | folded | 檢出段補寫程式要求錯版也有斷言、與文字不一致；前置清單第 2 項 |
| GEN-2 | 通才 | major | HIT | folded | 前置清單第 3 項 |
| BND-1 | 邊界 | major | HIT | folded | 同 GEN-2 |
| GEN-4 | 通才 | major | HIT | folded | 前置清單第 4 項 |
| BND-2 | 邊界 | major | HIT | folded | 回退段補前置條件（UTF-8 語系等）；前置清單第 6 項 |
| ARC-2 | 架構對齊 | minor | HIT | folded | 前置清單第 1 項記評分依賴指紋 |
| ARC-3 | 架構對齊 | minor | HIT | accepted | 輸出欄位命名在既有評測腳本間本就不一致，統一要改多份已凍結卷證格式，收益只在命名 |
| ARC-4 | 架構對齊 | minor | HIT | folded | 前置清單第 6 項（環境錯誤寫成 invalid 卷證、mkdir 前先檢查） |
| HND-3 | 接手 | minor | HIT | folded | S1–S3 人工驗收補指令；回退段補前置條件 |
| HND-4 | 接手 | minor | HIT | folded | S2 人工驗收寫明 runner_sha256 只對應產生當下入口版本 |
| HND-5 | 接手 | minor | HIT | folded | 失敗索引補註 0 起算 |
| HND-6 | 接手 | minor | HIT | folded | 前置清單第 7 項擴充點 |
| HND-7 | 接手 | minor | HIT | folded | S3 人工驗收寫明原測試 SHA 由全文重算；前置清單第 6 項 |
| HND-8 | 接手 | minor | HIT | folded | 新增 REVISIT:2026-11-09 |
| GEN-5 | 通才 | minor | HIT | folded | 同 HND-2 |
| GEN-6 | 通才 | minor | HIT | folded | 同 HND-7 |
| GEN-7 | 通才 | minor | HIT | folded | 前置清單第 5 項 |
| GEN-8 | 通才 | minor | HIT | folded | 計劃補寫該 REVISIT 關閉與「預先凍結」的界線 |
| GEN-9 | 通才 | minor | HIT | folded | 計劃列為已知未處理風險並註明未量化 |
| GEN-10 | 通才 | minor | HIT | folded | 同 HND-3 |
| BND-3 | 邊界 | minor | HIT | folded | 同 HND-3 |
| BND-4 | 邊界 | minor | HIT | folded | 前置清單第 6 項逾時格保存輸出 |
| BND-5 | 邊界 | minor | HIT | folded | RETIRE-IF 補暫時性環境無效重跑規則 |
| BND-6 | 邊界 | minor | HIT | folded | 同 HND-2 |
| BND-7 | 邊界 | minor | HIT | folded | 前置清單第 6 項補原測試 SHA、instrument、直譯器與 git 版本 |
