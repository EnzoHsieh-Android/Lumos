# Code Review — payload-L-late.patch

审查范围:11 個 commit(對帳排除補登→事後改用權威紀錄修正、對帳時間少 8 小時、LINE 綁定洗白修正、SMS OTP 5→15→revert 回 5、後台 OTP 查詢工具、會員統計分頁、POS 請求日期預設、手機版 RWD 三次迭代修正、對帳自癒排程 22:30→23:00)。已對照完整程式碼快照逐檔核實,並實際 `dotnet build`(0 error)與 `dotnet test LandmarkMember.Tests`(22/22 pass)。

## 第一部分:逐檔裁決

| 檔案 | 判定 | 一句話理由 |
|---|---|---|
| LandmarkMember.Pos/Repositories/Implementations/ReconciliationRepository.cs | clean | 最終版用 `NOT EXISTS(InvoiceOrders WHERE InvFlag='SUPPLEMENT')` 取代純 UserID 判斷,已對照 InvoiceSupplementRepository 的實際寫入路徑(同一 Tx 寫 Orders.UserID='SVC_DESK'+InvoiceOrders.InvFlag='SUPPLEMENT')驗證邏輯自洽,無漏排/誤排 |
| LandmarkMember.Server/Repositories/Implementations/EventLogRepository.cs | clean | `SpecifyKind(CreatedAt, Utc)` 修正已對照 DB schema(`ReconciliationLog.CreatedAt DEFAULT GETUTCDATE()`)與既有 `SchedulerHeartbeatRepository` 同型修正確認一致 |
| LandmarkMember.Server/Repositories/Implementations/CustomerRepository.cs | clean | `RegisterSource=ISNULL(NULLIF(@RegisterSource,''),RegisterSource)` 已核對兩個呼叫點(RegistrationService.cs:299,399)皆傳 `request.Store`,無「刻意傳空字串清空」的合法用例被誤傷;新增的會員統計兩支查詢皆為參數化唯讀 SQL |
| LandmarkMember.Server/Repositories/Interfaces/ICustomerRepository.cs | clean | 純介面新增,與實作簽章一致 |
| LandmarkMember.Server/Configuration/SmsSettings.cs | clean | 本輪淨效果 5→15→5(同日 revert),已核對三處(class 預設/appsettings.json/appsettings.Production.json)最終值一致回到 5 |
| LandmarkMember.Server/appsettings.json | clean | 同上,淨效果為 no-op,已核對最終值 |
| LandmarkMember.Server/appsettings.Production.json | clean | 同上 |
| LandmarkMember.Server/Controllers/Admin/AdminSmsLookupController.cs | major | 回傳明碼 OTP(`dto.Code=log.VeriCode`)的端點完全沒有限流,見 findings |
| LandmarkMember.Server/Models/DTOs/Admin/SmsLookupDto.cs | clean | 純 DTO,欄位與 controller 填值一致 |
| LandmarkMember.Server/Repositories/Implementations/SmsLogRepository.cs | clean | `GetLatestByPhoneAsync` 參數化查詢,`ORDER BY Seq DESC` 語意正確 |
| LandmarkMember.Server/Repositories/Interfaces/ISmsLogRepository.cs | clean | 介面新增與實作一致 |
| LandmarkMember.Server/Controllers/Admin/AdminMemberStatsController.cs | clean | 純唯讀端點,`days` 有 `Math.Clamp(1,365)` 防呆 |
| LandmarkMember.Server/Models/DTOs/Admin/MemberStatsDto.cs | clean | 純 DTO |
| LandmarkMember.Server/wwwroot/admin/logs/index.html | clean | 本輪含兩次自我修正(`table.fit` 補窄表格留白、pill `flex-wrap` 補手機版跑版),已核對 CSS 特異性(`table.fit` class 選擇器優先度高於單一 `table` 元素選擇器,與宣告順序無關)確實生效;`api()` GET 查詢參數傳遞方式核對無誤 |
| LandmarkMember.Pos/appsettings.json | clean | `ReconSelfHeal.Hour/Minute` 22:30→23:00 純數值改動 |
| LandmarkMember.Server/Repositories/Implementations/SchedulerHeartbeatRepository.cs | clean | 僅改一行顯示用註解文字,不影響邏輯 |
| docs/landmark-knowledge/Systems/維運儀表板.md | clean | 已核對最終內容:對帳排除補登的 KEY 條目被正確整條取代(非疊留舊版造成矛盾陳述),各分頁新增條目與程式碼行為一致 |
| docs/landmark-knowledge/Systems/認證與註冊.md | clean | RegisterSource 修正的敘述與實際 SQL 一致 |
| docs/landmark-knowledge/Systems/SMS簡訊.md | clean | 已核對最終「現值 5 分鐘」與 code 三處實際值一致(revert 後未留 15 分鐘殘留描述) |
| docs/landmark-knowledge/Projects/對帳假差異自癒_計劃.md | clean | 排程時間敘述與 appsettings.json / SchedulerHeartbeatRepository 註解一致改為 23:00 |
| docs/landmark-knowledge/Verification/2026-07-16_對帳假差異自癒_lab_E2E.md | clean | 僅同步排程時間描述,驗證內容本身未受本輪影響 |

## 第二部分:Findings

### F1 [major] 後台 OTP 查詢端點完全沒有限流,可被當即時竊碼 oracle 用

- **file:line**: `LandmarkMember.Server/Controllers/Admin/AdminSmsLookupController.cs:19-41`(`[ApiController]`/`[Route]`/`Lookup` 方法皆無 `[EnableRateLimiting(...)]`)

- **對照**: 同一份程式碼庫裡,凡是碰 SMS/OTP 的端點都掛了限流——`LandmarkMember.Server/Controllers/Internal/AuthController.cs:48` 掛 `[EnableRateLimiting("auth")]`、`LandmarkMember.Server/Controllers/Internal/RegisterController.cs:36` 送碼端點掛 `[EnableRateLimiting("sms")]`,其餘驗證端點掛 `"auth"`。`Program.cs:191-220` 定義的 `"auth"`(每 IP 每分鐘 10 次)與 `"sms"`(每 IP 每小時 `IpMaxSendsPerHour`)兩個 policy 明確是為了防「濫發 / 灌爆 OTP 相關端點」而設。`AdminSmsLookupController` 是本輪新增、同樣讀寫 `SMS_Log`/直接碰 OTP 的端點,卻沒有套用任兩個既有 policy 之一,也沒有新開一個。

- **具體失敗場景**:攻擊者取得(或內部人員外洩)維運儀表板共用金鑰 `AdminSettings.LogViewerKey`——這把 key 本是設計給「唯讀看 log」用(`AdminKeyMiddleware.cs` 對全部 `/api/admin/*` 一視同仁)。拿到這把 key 後,攻擊者可對 `GET /api/admin/sms/lookup?phone=<受害者手機>&key=...` 不設任何間隔地輪詢(此端點無 `[EnableRateLimiting]`、`Program.cs` 也沒有全域套用速率限制到 `/api/admin` 路徑)。`SmsSettings.ExpiryMinutes=5`、`CodeLength=4`,窗口短但輪詢無成本;一旦受害者觸發簡訊註冊/綁定流程,攻擊者在 5 分鐘內即可從此端點直接讀到明碼 `dto.Code=log.VeriCode`(`AdminSmsLookupController.cs:81`),搶在受害者之前呼叫 `POST /api/internal/register/bind`(對應 `RegisterationService.cs:299` 呼叫的 `UpdateLineBindingAsync`)完成帳號綁定/接管。這把同一把 key 原本只用於檢視錯誤紀錄等唯讀資訊,現在多了一條「直接兌現成帳號接管」的路徑,且此路徑本身沒有任何節流。

- **備註**:程式碼註解已自陳「看得到 OTP=帳號接管向量」並加了 `Event_Log` 稽核留痕,顯示作者知道風險、但緩解手段止於「事後看得到誰查過」,未攔「查太快/查太多」這一層——而這正是同專案對其他 OTP 相關端點一貫採取的攔法。

## 未列入 findings 的已查核疑慮(排除原因)

- **AdminSmsLookupController 缺少速率限制是否為個案**:核對 `LandmarkMember.Server/Controllers/Admin/` 下其餘 9 個 controller,無一掛 `[EnableRateLimiting]`(整個 admin 分頁架構本就只靠共用 key 保護,不靠限流)。因此「admin 端點沒限流」本身不是本輪新增的個案問題,但本輪新增的是「唯一一個直接吐出可即時兌現之秘密(OTP)」的 admin 端點,與同庫其它 SMS 端點的防護基準不一致,故仍記為 major、而非視為既有架構免責。
- **前端 `querySms` 對後端 400 回應只顯示通用錯誤訊息**(`index.html` `querySms` 函式,`if(!r){smsError.value='查詢失敗…'}`):後端已有獨立前端 regex 擋掉格式錯誤,實際觸發後端 400 分支機率低,且屬訊息精確度而非行為錯誤,依裁決紀律不單獨列為 finding。
- **`GetDailyNewMemberCountsAsync` 沒有查詢上限窗口的顯式上界**:`WHERE CreateDate >= DATEADD(DAY, -(@Days-1), CAST(GETDATE() AS date))` 无需上界(`CreateDate` 不可能晚於現在),非漏洞。
