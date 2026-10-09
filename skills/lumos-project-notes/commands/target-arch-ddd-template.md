# DDD 目標架構範本

專案想讓新模組照 DDD(領域驅動設計)寫、又不想被架構對齊審查席判成「跟舊鄰居不一樣」時,用這份範本開一篇目標架構節點,再在 `.lumos/config.json` 的 `arch_targets` 宣告哪些目錄照它審。機制本身見 [06-代碼審與推送.md](06-代碼審與推送.md) 的 `arch_targets` 那一列;單源 Projects/架構對齊可宣告目標架構_計劃、Projects/DDD目標架構範本_計劃。

## 採用步驟

1. 開節點:`lumos new system DDD目標架構 --responsibility "照 DDD 寫的新模組該遵守的目標寫法;不管任何程式檔,規則套用的目錄由 .lumos/config.json 的 arch_targets 宣告"`(不帶 `--code`:它規範的是範圍內的寫法,不是自己的程式檔)。
2. 把下面範本區塊的 `summary` 九條 RULE 行貼進那篇的摘要,正文照需要貼。用不到的規則整行刪掉。
3. **把 `<採用日>` 換成今天、`<回頭日>` 換成打算回頭檢查的日期(建議一年後)**——沒換就照抄,`lumos lint` 會逐條印「日期要寫成 YYYY-MM-DD」警告(筆記格子目前只提醒不擋,所以要自己換掉);日期的用意是規則要有人確認過才生效,到回頭日要再裁一次還留不留。
4. 在 `.lumos/config.json` 加宣告(路徑照專案實際目錄改;第一條命中算數,範圍內還留著的舊碼用前面一條 `none` 切回鄰居基準):

```json
{
  "arch_targets": [
    {"path": "app/Domain/Legacy/**", "node": "none"},
    {"path": "app/Domain/**", "node": "Systems/DDD目標架構"},
    {"path": "app/Application/**", "node": "Systems/DDD目標架構"}
  ]
}
```

宣告與規則只讀「分支從主線分出來那一刻」的版本:加宣告的那次推送照舊比鄰居,合進主線之後才生效。

## 為什麼是這九條

- **前七條是 DDD 的骨架**:不變規則守在聚合裡、聚合之間鬆綁、基礎設施往外推、應用服務只協調、值物件不可變。審查席判得出「違反長怎樣」的才寫成規則;「模型要貼近業務語言」這類審不動的不寫。
- **第八條壓住 DDD 的副作用**:照教條寫容易長出一堆只轉手的層與介面——Ousterhout 說的淺模組,每多一層就多一份要維護、要測的東西。深模組是對外介面窄、裡面藏得深;聚合根本來就是這種形狀,邊界劃在聚合,不是劃在每個類別。
- **第九條讓測試跟著深模組走**:從聚合根與應用服務的公開方法驗結果,內部怎麼重寫測試都不必改,也讓「斷言內部欄位等於某值」這種只會跟著實作走的測試寫不進來。lumos 的〈實作測試品質〉(見 [03-寫回圖譜.md](03-寫回圖譜.md))要求斷言實際行為、綁死內部結構就驗一次重構,但刻意不規定架構;選了 DDD 的專案用這條把「從哪個邊界測」講死。

## 範本

```markdown
---
type: system
status: doing
responsibility: 照 DDD 寫的新模組該遵守的目標寫法;不管任何程式檔,規則套用的目錄由 .lumos/config.json 的 arch_targets 宣告
aliases:
  - 領域驅動設計規則
  - 聚合根規則
  - 新模組架構規則
tags:
  - type/system
  - status/doing
summary: |-
  RULE:Domain 層不依賴框架、資料庫與外部服務型別(不 import ORM、HTTP client、框架 facade 或容器)。違反長怎樣:Order 實體裡用 ORM 查詢、或建構子注入 HTTP client [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:業務不變規則只寫在聚合根的方法裡,外部不得直接改聚合內部欄位或子物件。違反長怎樣:Service 裡寫 order.status = PAID、或從外面直接改 order.lines 裡某一筆的數量 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:聚合之間只用 ID 參照,一個交易只改一個聚合;跨聚合的連動用領域事件或應用服務分兩步。違反長怎樣:Order 直接持有 Customer 物件並在同一交易裡改 Customer 的點數 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:Repository 以聚合為單位整包載入與存回,不提供改單一子物件的方法;介面放在 Domain,實作放在 Infrastructure。違反長怎樣:OrderRepository.updateLineQty(orderId, lineNo, qty) [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:應用服務只做協調(載入聚合、呼叫聚合的行為方法、存回、發事件),不寫業務判斷。違反長怎樣:應用服務裡 if order.total > 1000 then 打折 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:範圍外的舊碼只能透過應用服務進入新模組,不直接建立或讀寫領域物件。違反長怎樣:舊 Controller 裡 new Order(...) 後自己呼叫 repository 存檔 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:值物件不可變,建構時就驗證合法性,相等性看值不看身分。違反長怎樣:Money 有 setAmount()、或可以建出負數金額再於別處檢查 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:模組邊界劃在聚合(深模組):對外只露聚合根的行為方法與應用服務,不為每個值物件、每層轉手另開介面。違反長怎樣:只有一個實作、只是轉呼叫的 IOrderService 介面,或值物件各自一個 Factory 與 Interface [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
  RULE:測試只經由聚合根與應用服務的公開方法驗行為,不讀寫領域物件的內部欄位、不 mock 領域物件本身;外部依賴(資料庫、外部服務)才用替身。違反長怎樣:測試裡斷言 order._status、或 mock 掉 Order.pay() 再驗應用服務 [依據:人] [since:<採用日>] [retire:人裁] [until:<回頭日>] [confirmed:<採用日>]
---
# DDD目標架構

> 白話:這篇是「照 DDD 寫的新模組」該長什麼樣的規則清單。專案在 .lumos/config.json 的 arch_targets 宣告哪些目錄照這篇審,架構對齊審查席就改拿上面的 RULE 行當標準,不再要求新模組跟舊鄰居長得一樣;範圍外的舊碼照舊比鄰居。
```

## 調整與撤除

- 用不到某條(例如沒有領域事件)就刪掉那一行,或加 `[status:superseded]` 並寫 `[被取代:…]`;架構對齊席只看沒作廢的 RULE 行。
- 規則有對應的架構測試(例:ArchUnit、NetArchTest、Konsist、Deptrac)時,在那一行加 `[test:<測試名>]`,讓機器守、審查席補看。
- 到回頭日(`until`)要人裁一次還留不留;過期的規則照樣附給審查席,但會加註「已過 until,待人裁」。
