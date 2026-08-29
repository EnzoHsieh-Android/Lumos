---
type: project
status: doing
created: 2026-08-29
updated: 2026-08-29
tags:
  - type/project
  - status/doing
decisions:
  - content: Enzo 2026-08-29 裁:只做 S1(impact manifest 進派工必附材料,經 loop next 吐 impact_cmd + dispatch materials + seat-check 自動涵蓋),S2([Y] 符號檢查改標準庫 ast)另案追蹤不併入;S1 走完整設計審(非 light)
    id: d1
    context: 實帳 74 份派工單只有 8 份提到 impact,2026-08-29 當天 code-refute-verdict 那輪就漏(材料只有 patch+兩支原始碼),而該批真跑 impact 吐 25 個節點含釘住的合約/事故節點——「建了沒人跑」再現。觸發=讀 OmO 看它用 codegraph/LSP/AST-Grep 做結構檢索,回頭盤點自家的圖譜側鏡頭有沒有真的接上
    why_chosen: S1 只把三件既有原語(impact --json / loop next 指令模板慣例 / seat-check 材料對帳)接起來,不新增閘不改 rc 語意,解的是有數字的真問題(8/74);S2 與 S1 無相依、且 AST 未必勝過正則(可能只是換一種漏法)須先量,分開才不會讓審查賣點分散。走完整設計審而非 light:雖不改 rc,但會改變 seat-check 的 unreported 指標語意(新舊帳不可直接比),碰收貨機制與派工紀律,寧嚴不寬
    decided: 2026-08-29
    valid: true
---
# impact鏡頭機械化_計劃

> **★已裁(Enzo 2026-08-29,見 d1):只做 S1,走完整設計審;S2 另案追蹤不併入本案。★** 下方〈待裁〉保留為裁定當下的比較紀錄,不是還開著的選項。S2 一節留著當追蹤條目,**本案不實作**。

PRIOR-ART: **借用既有原語為預設,不自建、不加依賴**——S1 用既有 `lumos impact --diff --json`(已建、已測)+ 既有 `loop next` 席位表輸出 + 既有 `seat-check` 材料對帳三件現成物,只把它們接起來;S2 用 **Python 標準庫 `ast`**(零依賴),不採 AST-Grep / LSP / codegraph 這類外部依賴(撞零依賴家規,且本專案主要只有 python+shell,不需要跨 25 語言)。外部觸發=讀 OmO(2026-08-28~29)看到它用 codegraph/LSP/AST-Grep 做結構檢索,借**想法**不借工具。

## 問題(有數字)

**S1 · impact 鏡頭建了但九成沒在跑。** code-loop 手冊第 3 步寫著「派 reviewer 前跑 `lumos impact --diff --json`、附 manifest 當第二鏡頭」,但實帳:**74 份派工單只有 8 份提到 impact**。2026-08-29 當天那輪(`code-refute-verdict`)就漏了——派工單材料只有凍結 patch + 兩支原始碼,沒附波及清單;而那批改動真跑 impact 會吐 **25 個節點**(含 `canary-audit`、`測試假綠形態`、`design-loop` 等釘住的合約/事故節點)。
→ 這正是「靠自律 = 建了沒人跑」的又一例(同 [[Projects/建了沒人跑批次裁定_計劃]] 的形態)。8/74 已經證明自律路走不通。

**S2 · 符號比對是純正則,`ast` 一次都沒用過。** doctor [Y]「筆記點名的方法或類別,程式碼裡找不找得到」用 `shape_re` 正則判形狀 + inline-code 抽取;`grep -c "import ast" scripts/lumos` = **0**。對 .py 檔,標準庫 `ast` 能給真的符號表(def/class/賦值),零依賴。

## 提案

### S1 · impact manifest 進派工必附材料(本案主體)

1. `lumos loop next` 的輸出多一段 **`impact_cmd`**:直接吐出該輪要跑的 `lumos impact --diff <範圍> --json > <目錄>/rN-impact-manifest.json`(比照既有 `record_cmd`/`disposal_cmd` 的慣例——**指令模板由工具產,不靠人記**)。
2. 派工單 `rN-dispatch.json` 的 `materials` **納入該 manifest 路徑**(既有欄位,不新增 schema)。
3. `seat-check` 因此**自動涵蓋**:它本來就對帳「dispatch 宣告的 materials 有沒有被報告觸及」,manifest 進了 materials 就會被算進 `unreported`。**不新增閘、不改 rc 語意**(seat-check 恆 rc0 觀測)。

★刻意不做的★:不硬擋「沒附就不准派」。理由=撞「前置加重一律拒」的精神較不明確,且 seat-check 的觀測定位是既有設計;先讓它**可見**,累積幾輪再決定要不要升硬擋(重驗條件見下)。

### S2 · [Y] 符號檢查加 AST 後端(★本案不做,另案追蹤★)

對 `.py` 檔改用標準庫 `ast` 取真符號表(def/class/module 級賦值),取代正則形狀猜測;非 .py 檔維持現行正則。預期收益=減少 [Y] 的假陰/假陽(現在靠形狀猜「這串像不像符號」)。**零依賴、可獨立回滾**。

## 實務隱患(逐類答)

- **併發/效能**:`impact --diff` 每輪多跑一次,單次為秒級(既有指令,已在 hook 路徑用過);S2 的 `ast.parse` 對單檔 python 亦為毫秒~秒級。**已排除**:不進熱路徑、不是迴圈內重複呼叫。
- **資源/連線/鎖**:已排除——純讀檔與純計算,無連線、無鎖、無交易。
- **回滾路徑**:S1 動 `loop next` 輸出與派工慣例文字,`git revert` 即回;manifest 是**新增產物檔**,不覆蓋既有檔,回滾後殘留檔無害(可留可刪)。S2 為 [Y] 的後端替換,回滾即回正則。
- **不可逆/對外**:已排除——不寄送、不碰正式環境、不刪東西。
- **★真隱患:manifest 進 materials 會改變 seat-check 的既有數字★**——`unreported` 從此會多一類命中(審查員沒引用 manifest 就算 unreported),**歷史帳與新帳的同一指標語意會斷層**。處置:seat-check 恆 rc0 不影響任何判定,但**治理帳的趨勢比較要標生效日**;需在 [[Systems/design-loop]] 收貨段記一句「2026-08-29 起 materials 含 impact manifest,unreported 數與此前不可直接比」。
- **★真隱患:manifest 可能很長,吃掉審查員注意力★**——25 個節點若全文貼上會很可觀。處置:manifest 是 **JSON 路徑當材料**(審查員自己讀),不是全文貼進派工詞;且既有 impact 已有「固定席全保、非固定 top-8」的收斂規則,不是無上限。
- **與「前置加重一律拒」教義**:S1 不加席、不加輪;多一次秒級指令與一份給審查員的清單,**屬於把既有材料接上,不是加重審查強度**。但這條判斷不是零爭議,故 S1 刻意停在「可見」不做「硬擋」。
- **應試化**:manifest 是**資料**不是評分表,不涉「照字面滿足」的鑽洞面;已排除。

## 待裁

- **範圍**:只做 S1?還是 S1+S2 一起?
- **分級**:S1 動到派工/收貨的既有慣例(雖不動 rc 語意),是否要走完整設計審、或走 light 檔?

## 誠實天花板與重驗條件

- **8/74 這個數字只證「沒附」,不證「附了就會更好」**——沒有任何自家實測顯示附 manifest 會提高 findings 品質。本案的正當性是「機制建了就該真的接上」,不是「有證據證明它有效」。
- **重驗條件**:S1 上線後累積 **≥5 輪**,看 ①派工單附 manifest 的比例是否真的接近 100%(沒有就是機械化沒生效)②`seat-check` 的 `unreported` 有沒有大量命中 manifest(若審查員普遍不讀,代表「附了也沒用」,該回頭檢討是不是要改成貼摘要而非給路徑)。任一為否 → 回頭調整或退回。
- S2 若做:以 doctor [Y] 在本 repo 的命中數變化為觀測,**不預設 AST 一定比正則好**(可能只是換一種漏法),要看實際差異再判。

## 相關

- 現況機制:[[Systems/design-loop]](收貨三道、派工編制)、[[Systems/graph-sync-coverage]]
- 同形態前例:[[Projects/建了沒人跑批次裁定_計劃]](建了沒人跑的處置慣例)
- 觸發來源:OmO 的 codegraph/LSP/AST-Grep(2026-08-29 讀;借想法不借依賴),見 [[Projects/席位人格化_計劃]] 同批外部對照
