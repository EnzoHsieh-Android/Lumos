結論: 修改後可核可

這張表的骨架可用，但目前有些格子「問得太窄」，有些證據則「證明不了該格宣稱的防護」。以下必改完成後，可作為第一版提問與最低證據基準；不能據此宣稱已完整符合 ASVS。

已讀背景定義：**`behavior` 已包含非法操作、合法成功對照與前置斷言**，所以不是只有正常路徑，不必另創 `negative_test`。以下逐類列出修改；未修改任何檔案。

1. **必改｜authz-object：補功能、欄位與跨租戶授權，補非 HTTP 入口。**

   原文：「能不能讀、改、刪不屬於他的 {資產}?」；入口列到「file_download、admin」。

   所有權檢查涵蓋不了「一般會員呼叫管理功能」或「修改自己的資料時夾帶管理員欄位」。表列 API3、API5，但題目沒有真正問到；背景的 `kind` 是單值，也不能假設 `message_consumer` 同時會套用 `http_api`。這對應 API1／3／5 的不同授權層次。[OWASP API Top 10 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/)

   **改成：**「{角色} 是否只能在獲准的租戶、物件、功能及欄位範圍內操作 {資產}？包含新增、批次操作、讀取與修改欄位；拒絕時不得洩漏資料或產生未授權副作用。」
   
   入口追加 `webhook_in、message_consumer、batch、cli`。最低證據維持原集合；測試須對應實際宣稱的授權維度。

2. **必改｜authn-identity：補帳號恢復、機器身分與瀏覽器條件。**

   原文：「身分從哪來、何時可信?偽造、過期、撤權後會怎樣?」「http_api 另問」。

   題目沒有明確涵蓋密碼重設、登入濫用、session fixation，以及 webhook／訊息來源驗證。這些不是一般登入成功案例能帶過的；WSTG 特別列出密碼變更／恢復及替代認證通道。[WSTG v4.2](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/)

   **追加：**「依所用機制檢查登入嘗試限制、帳號恢復、session 更新與登出失效、token 簽章及 issuer／audience；webhook／訊息驗證來源、內容完整性與重放限制。」
   
   「http_api 另問」改為「**凡瀏覽器可達且涉及 cookie、跨來源或自動附帶憑證的入口，另問**」。入口追加 `batch、cli`；身分包含服務帳號與作業執行者。`behavior、review` 可維持。

3. **必改｜input-injection：明列輸出端注入與不安全解析。**

   原文：「輸入會不會被當成指令、查詢或路徑執行?」

   容易漏問儲存型／DOM XSS、CSV 公式注入、XXE、不安全反序列化；尤其資料先存入資料庫，再由管理頁或匯出使用時。ASVS 5 V1 明列這些不同處理情境。[ASVS 5.0.0 V1](https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0_release/5.0/en/0x10-V1-Encoding-and-Sanitization.md)

   **改成：**「來自請求、檔案、訊息、儲存資料或第三方回應的不可信內容，在查詢、命令、模板、HTML／JavaScript、CSV、XML 與反序列化時，會不會改變原定語意或觸發非預期執行？」
   
   「全部」合理。保留原最低證據，但每條護欄須指出測試與靜態規則實際覆蓋哪個處理點，不能以任意掃描結果充數。

4. **必改｜flow-abuse：補合法使用者濫用與資源上限，調整證據含義。**

   原文：「讓 {資產} 被他人操作生效、超賣或耗盡」；最低「behavior、concurrency、review」。

   合法使用者也能濫刷優惠、發送付費簡訊、反覆匯出或觸發昂貴查詢。背景的 `concurrency` 定義偏向「他人操作不生效」，不足以承擔整個 API4／API6。[API4:2023](https://api-security.owasp.org/editions/2023/en/0xa4-unrestricted-resource-consumption/)

   **改成：**「合法或非法身分在重送、並發、跳步驟、竄改業務參數或大量操作時，能否繞過流程、重複生效、超賣，或耗盡運算、儲存、佇列及第三方費用配額？」
   
   入口追加 `export、file_download、admin、outbound_call、batch、cli`。最低證據可保留，但同步將 `concurrency` 定義擴成「驗證宣告的重複生效、業務一致性與資源上限，並有合法流量對照」。允許本機降低配額後的小規模測試，**不要求每個單人專案做大型壓測**。

5. **必改｜data-exposure：補快取、暫存與資料生命週期。**

   原文：「錯誤訊息、日誌、回應欄位」。

   這只覆蓋部分外洩管道，沒有明確問到共用快取、匯出暫存、備份、保留與刪除。ASVS 4 的架構要求也將資料分級、保留、隱私與保護措施納入設計。[ASVS 4.0.3 V1.8](https://raw.githubusercontent.com/OWASP/ASVS/v4.0.3/4.0/en/0x10-V1-Architecture.md)

   **改成：**「回應、錯誤、日誌、快取、匯出／暫存及備份，是否洩漏敏感資料或其存在性？保存期限、刪除與跨使用者隔離是否符合資料分級？」
   
   `behavior、review` 與「全部」可保留；主張涉及備份或實際儲存設定時，另須 `deployment`。欄位是否有權讀取由 authz 負責，這類負責資料經其他管道逸出。

6. **必改｜file-handling：補惡意檔案、解壓與處理器風險。**

   原文：「讀寫到別的檔或塞爆空間」。

   不只路徑穿越與磁碟空間；也要考慮可執行內容、格式偽裝、壓縮炸彈及處理器耗盡資源。ASVS 5 V5 明確要求考慮解壓後大小與下載者處理檔案的安全。[ASVS 5.0.0 V5](https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0_release/5.0/en/0x14-V5-File-Handling.md)

   **改成：**「檔案的實際格式、內容、路徑、連結及解壓後大小是否受限？能否越界讀寫、被當程式執行、傷害下載者，或耗盡處理器與儲存資源？」
   
   入口追加 `message_consumer、batch、cli、outbound_call`，涵蓋附件、匯入及遠端檔案。保留原最低證據；反例至少涵蓋實際使用的解析／儲存邊界。防毒可依用途採用，不應強制每案配置。

7. **必改｜outbound：入口漏配，應沿資料流追到真正外呼。**

   原文：「適用入口：outbound_call、webhook_in」。

   URL 匯入 API、圖片處理、PDF 產生、佇列工作都可能引發外呼；目前沒有規則保證它們另登記 `outbound_call`，因此會漏問。

   **入口欄改成：**「全部；不會直接或間接發起外呼者，附理由判不適用。」
   
   **模板追加：**「重新導向及 DNS 解析後的目的地是否仍受限？是否阻擋內網／metadata 等非預期目的地？第三方回應是否驗證格式、大小及內容，並限制逾時、重試與憑證轉送？」
   
   保留 `behavior、review`；以本機模擬目的地驗證「實際沒有送出禁止請求」，不能只測 URL 檢查函式。SSRF 與第三方 API 消費風險可同類保留，但應分別列測試目標。[API7／API10](https://api-security.owasp.org/editions/2023/en/0x11-t10/)

8. **必改｜secrets-crypto：秘密掃描不能證明加密與傳輸安全。**

   原文：「秘密、金鑰、憑證放哪、誰讀得到、傳輸有沒有保護?」；最低「secret_scan、review」。

   掃不到秘密，不代表 TLS 驗證、金鑰輪替、密碼雜湊或加密使用正確。

   **建議拆成兩列，避免無關證據聯集：**
   
   `secrets-management`：「秘密是否外洩、最小授權、可輪替及撤銷？」最低 `secret_scan、deployment、review`。
   
   `crypto-transport`：「敏感資料傳輸與儲存是否使用合適的標準機制？憑證、金鑰與密碼驗證是否正確？」最低 `behavior、deployment、review`。
   
   後者的 `behavior` 至少驗證所宣稱的失敗條件，例如錯誤憑證或遭竄改內容遭拒絕，不要求自行證明密碼學演算法。工具追加既有 runner；不能把「設定與容器掃描」當成 `secret_scan` 的同義詞。[ASVS 4.0.3 V1.6／V1.9](https://raw.githubusercontent.com/OWASP/ASVS/v4.0.3/4.0/en/0x10-V1-Architecture.md)

9. **必改｜supply-chain：已知漏洞掃描與來源可信要分開驗。**

   原文：「新加的依賴、映像、工具從哪來、版本怎麼釘、誰核可?」

   「新加」漏掉既有依賴新披露漏洞；漏洞資料庫也不能證明套件、安裝腳本或 CI 工具來源可信。

   **改成：**「目前使用的直接／間接依賴、映像、建置工具與 CI 動作，來源、版本／digest、完整性及執行權限是否受控？是否持續處理新披露漏洞？」
   
   `dependency_scan、review` 可保留，但補明「review 必須核對來源、鎖定方式及安裝／建置權限；掃描須涵蓋實際交付依賴」。不必第一版就要求完整企業級來源證明平台。

10. **必改｜config-deploy：補 API 清冊與執行環境證據。**

    原文：「部署設定、容器、對外開的埠與預設帳號」；對應「API8、API9」。

    目前模板並沒有真正問到 API9 的舊版本、測試端點與清冊管理；設定檔掃描也不能證明部署後端點不可達。[API9:2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/)

    **改成：**「各部署環境的服務權限、公開端點、管理／除錯介面、預設帳號與設定是否受控？API 主機、版本及測試／退役端點是否有清冊並落實停用？」
    
    最低改為 `config_scan、deployment、review`；宣稱「外部不可達」時另須有 `behavior` 實測，不能由檔案設定推定。

11. **必改｜audit：只審文字，無法證明事件真的留下紀錄。**

    原文：「事後查得到嗎?紀錄本身會不會被改?」；最低「review」；工具「—」。

    應實際觸發成功、拒絕及失敗事件，驗證紀錄內容與保護措施。ASVS 5 V16 包含認證／授權事件、日誌注入防護及防竄改。[ASVS 5.0.0 V16](https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0_release/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md)

    **最低改成：**`behavior、deployment、review`；工具改成「既有單元與整合測試 runner、人工或獨立審查」。
    
    **模板追加：**「成功、拒絕與安全控制失敗是否留下可關聯事件？能否注入假紀錄、刪改紀錄或讓秘密進入紀錄？」
    
    入口改成「全部；依安全事件適用性處置」。不要求單人專案購買 SIEM。

12. **必改｜frontend-origin：從責任歸屬改成可測的防護問題。**

    原文：「前端跨來源、cookie、CSRF 與畫面上的敏感資料誰負責?」

    「誰負責」是設計分工，不能直接導出安全驗收。也漏問點擊劫持、瀏覽器儲存與訊息來源驗證。ASVS 5 V3 包含這些瀏覽器邊界控制。[ASVS 5.0.0 V3](https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0_release/5.0/en/0x12-V3-Web-Frontend-Security.md)

    **改成：**「不可信網站能否代送敏感操作、讀取回應、嵌入敏感畫面或偽造跨視窗訊息？cookie、瀏覽器儲存及登出後資料如何保護？」
    
    `behavior、review` 可保留，工具追加「瀏覽器整合測試 runner」。跨來源行為應有真實瀏覽器驗證，僅檢查回應標頭不足。
    
    與 authn 的 cookie／CSRF 題目可共用護欄和證據；`arch-fe-origin` 的既有答案只能沿用分工或決策，不能直接當驗證完成。

13. **必改｜人工替代欄：不能把所有人工核對都叫 deployment。**

    原文：「static_analysis 換成 deployment（人工核對紀錄）」「secret_scan 換成 deployment」「dependency_scan 換成 deployment」。

    背景將 `deployment` 定義為「實際部署設定符合」；人工查原始碼、秘密及套件漏洞並不符合這個定義。問題是證據語意錯置，不是完全禁止人工替代。

    **替代欄統一改成：**「無合適工具時，提出限期人工替代方案，列明原檢查目的、範圍、方法、原始查核材料、限制與重驗條件；經核可後採用，不視為已完成原掃描。」
    
    如需機械換算，應同步增加明確的 `manual_verification` 種類，或正式擴充並更名背景定義；不能只改這張表。套件人工查核至少要有套件／版本清單與公告來源，不能只確認鎖檔存在。

14. **必改｜全表共同規則：補安全失敗路徑與 @repo 覆蓋範圍。**

    原文：「每類都含 review」及「每個 repo 根問一次」。

    `review` 的存在不能自動保證每類都考慮防護服務逾時、例外與依賴失效；一個 repo 也可能包含多個服務及部署環境。

    **追加兩句：**
    
    「每條護欄須說明防護所依賴的服務逾時、例外或不可用時如何安全失敗；適用者以 behavior 驗證，不得默認放行。」
    
    「@repo 只合併出題；證據須列明涵蓋的服務、部署環境、依賴清單與秘密來源。單一服務或開發環境結果不得代表全部。」
    
    安全失敗亦是 ASVS 5 V16.5 的明確要求。[ASVS 5.0.0 V16.5](https://raw.githubusercontent.com/OWASP/ASVS/v5.0.0_release/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md)

15. **建議｜工具可取得，但應標明能力與輸出邊界。**

    原文：「既有單元與整合測試 runner、靜態分析、模糊測試、動態掃描」。

    免費、本機執行的工具路線可行，例如 [Semgrep CE](https://semgrep.dev/products/community-edition/)、[Gitleaks](https://github.com/gitleaks/gitleaks)、[Trivy](https://trivy.dev/docs/latest/guide/) 與 ZAP；[ZAP 可輸出 SARIF](https://www.zaproxy.org/docs/desktop/addons/report-generation/templates/)。但「可產生某種報告」不等於「能產生所有種類證據」。

    **欄名改成：**「可用工具類別〔各自產生的 evidence kind；必要／補充〕」。
    
    例如動態掃描產生 `dynamic_scan`，不能直接抵 `behavior`；fuzzer 的「沒有當機」也不能證明授權正確。每類補列「人工或獨立審查 → review」，與背景一致。工具安裝不等於已有可用測試、故障配方或校準材料。

16. **建議｜保留主要類別，補標準追溯與條件式缺口。**

    原文：「其餘章節對應是本篇自建、未逐條核對 ASVS 原文」。

    不建議整批合併：authn／authz、注入／檔案、授權／資料外洩分別有不同驗證目的。真正需要去重的是共享控制及證據；反而 `secrets-crypto` 適合拆分。

    **追加：**「標準對應僅為查閱索引，不表示符合；引用使用版本化條款或測試 ID，並列明本表承接的範圍。」
    
    至少補核對：authn 的 CSRF／CORS 對應 ASVS 5 V3；outbound 的外呼設定對應 V13；data-exposure 的資訊洩漏可補 WSTG INFO。另加一條條件提示：「使用原生擴充、影像／文件解析器或不安全記憶體程式碼時，評估記憶體錯誤與整數邊界，按需加入 fuzz／sanitizer 證據。」[CWE Top 25 2025](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html) 適合作為這類補漏清單，不宜把全部項目無條件變成每個 Web 專案的必驗項。


