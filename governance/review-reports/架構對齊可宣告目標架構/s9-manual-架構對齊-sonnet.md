**架構對齊審查:s9 diff(feat 對 main,兩支新檔)**

我分兩組判。範圍內只有 `app/Domain/Order/OrderRepository.py`,照「[目標架構]」的規則。範圍外是 `app/Billing/CheckoutController.py`,仍比鄰居 `RefundController.py` 和 `InvoiceController.py`,但目標規則 2、3 是針對範圍外舊碼講的,所以也拿來判它。規則 1 只管 Domain 層,沒有套到 Checkout。

**問 1:分層與依賴方向**

*A 組 `OrderRepository.py`,照目標規則判:不對齊。*
- `OrderRepository.py:1` 在 Domain 層直接 `import db`,`:6` 和 `:9` 直接 `db.execute(...)`。規則的違反範例就是這個形狀(「Order.py 裡 import db」)。
- 範圍內的既有檔 `Order.py:1-10` 沒有任何基礎設施依賴,所以這支新檔也跟範圍內的寫法不同。
- 這是 major。
  - 目標規則:「Domain 層不依賴框架與資料庫型別,不 import db 或 HTTP 套件」

*B 組 `CheckoutController.py`,照目標規則判:不對齊,兩處都是 major。*
- 範圍外直接建領域物件。
  - `CheckoutController.py:5`(patch 內第 5 行)寫 `Order(req["id"], req["lines"])`,規則的違反範例正是「舊 Controller 裡 Order(...)」。
  - 目標規則:「範圍外的舊碼只能透過應用服務進入新模組,不直接 new 或讀寫領域物件」
- 範圍外直接改聚合內部欄位。
  - `CheckoutController.py:6` 寫 `order._status = "paid"`,繞過 `Order.pay()`(`Order.py:7-10`)。
  - 繞過後少了 `Order.py:8-9` 的「空訂單不可付款」檢查,等於在聚合根外再寫一份「付款」。
  - 目標規則:「業務不變規則只寫在聚合根方法裡,外部不得直接改聚合內部欄位」
- 兩處反方向的依賴(範圍外繞過入口)都成立。
- 以鄰居來比,Controller 直接碰外部資源(`RefundController.py:4` 直接打 db)是本層本來的做法,這點本身不算跨層。

**問 2:命名與錯誤處理**

- 對齊。`CheckoutController.py` 的頂層函式 `checkout(req)` 對應 `refund(req)`(`RefundController.py:3`)和 `create_invoice(req)`(`InvoiceController.py:3`)。
- 三支都沒有 try/except、沒有日誌,回傳都是 dict(`{"ok": True}`,同 `RefundController.py:5`)。
- `OrderRepository.py` 的類別與方法命名(`save`、`update_line_qty`)和範圍內的 `Order.py` 沒有衝突。

**問 3:第二種做法**

- 沒有鄰居可比的新做法,標 ⚠ 交編排者:`CheckoutController.py:1,7` 引入 `requests` 打外部 HTTP。鄰居全都沒有 HTTP client,專案沒有既有做法可對,我不硬判。
- 已算在問 1 的「第二種做法」:`CheckoutController.py:6` 手改 `_status` 等於在聚合根外複製了 `Order.pay()` 的行為。
- ⚠ `OrderRepository.py:8-9` 的 `update_line_qty` 直接改 `order_lines` 表,繞過 `Order` 聚合。
  - 規則 2 的字面是「外部不得直接改聚合內部欄位」,指記憶體裡的欄位。
  - 這裡改的是資料庫列,不確定算不算違反,我沒有計入。
- ⚠ `OrderRepository.py:6` 讀 `order._status`(私有欄位)。規則字面禁止的是「改」,這裡只是讀,我沒有計入。
- 專案裡也沒有「應用服務」這一層(`git ls-files` 只有 Controller 和 Domain)。規則 3 指定的入口目前不存在,所以 `CheckoutController` 沒有東西可以改走。

**不對齊共 3 條,其中 major 3 條。**
- 兩個 ⚠ 判不準,不計入:`update_line_qty` 是否違反規則 2,以及 `requests` 是否算第二種 HTTP client。
- 另有一個 ⚠ 是規則 3 的入口(應用服務)不存在。

1. `OrderRepository.py:1,6,9`:Domain 層 import db。
2. `CheckoutController.py:5`:範圍外 new 領域物件。
3. `CheckoutController.py:6`:範圍外直接改聚合內部欄位。
