# 判讀準則:kt-jackson-default-typing(Jackson 開全域預設型別)

依據:Jackson 官方文件 https://github.com/FasterXML/jackson-docs/wiki/JacksonPolymorphicDeserialization ——預設型別在內容來源不可信時有安全洞(攻擊者能指定要建的類別),「內容來源不可信時不建議」;兩端都由同一方控制時可以接受。

每處命中看前後 20 行(ctx 檔標頭有原檔路徑,原檔在本機語料目錄,必要時打開整支看這個 ObjectMapper 拿去解析什麼)。判:
- TP:正式碼,這個開了預設型別的 mapper 會拿去解析**可能來自外部的 JSON**(HTTP 請求本體、對外 API 回應、訊息佇列、使用者上傳、深層連結或 Intent 帶進來的字串),或看不出來源限制(通用的全域 mapper、Bean 給全專案用)。
- FP,理由欄開頭寫「FP型:<型>;」:
  - 可信來源:只拿來序列化/反序列化 App 或服務自己寫的資料(自己的 Redis 快取、Session 儲存、本機檔、記憶體深拷貝),外部碰不到。
  - 已防護:用了限制性的 PolymorphicTypeValidator(例:`BasicPolymorphicTypeValidator.builder().allowIfSubType("com.mycompany.")` 只放自己套件),不是 `LaissezFaireSubTypeValidator` 或允許 Any/Object。
  - 測試或範例碼:測試、sample、demo、教學。
  - 函式庫原始碼複本。
- UNSURE:看完判不出,寫缺什麼。
輸出:每處一行 TSV:序號<TAB>檔:行<TAB>TP|FP|UNSURE<TAB>理由(一句)。最後一行總計。
