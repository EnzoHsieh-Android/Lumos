severity: minor

1. severity: minor；blocking: false  
   逐字引句：「原完整主線CLI對三項新測試66綠94紅；新合法路徑正例在原CLI5綠。」  
   file: `docs/lumos-toolchain-knowledge/Verification/2026-10-06_異常派工單輸入驗證.md:26`  
   指定卷證無法重算這組數字：`full-validation.json:91` 起只記 10686／2 與重驗結果；`r1-F1-control.json:7` 起只記控制組 160 綠，以及補測後 161 綠 4 紅。第 31 行僅泛指另一目錄，未指出承載 66／94／5 的確切收據，下一 session 不能靠本案指定卷證核實。

2. severity: minor；blocking: false  
   逐字引句：「第二輪編排者誤把空處置清單寫成none，造成協議擋下，第三輪按既有零發現用法通過。」  
   file: `docs/lumos-toolchain-knowledge/Verification/2026-10-06_異常派工單輸入驗證.md:27`  
   這句未明寫 `none` 被解析成假 finding ID。`r3-disposal.json:3` 同時顯示 r2「折 1 條、最高 clean」及 r3「0 條發現」，留下表面矛盾。應明確說明 r2 的「折 1」只是錯誤記帳產生的假 ID，不是新 bug，且原帳未改寫。

3. severity: minor；blocking: false  
   逐字引句：「這篇驗固定來源的輸入修復與測試，交付CI另據實留帳。」  
   file: `docs/lumos-toolchain-knowledge/Verification/2026-10-06_異常派工單輸入驗證.md:20`  
   沒有明說本案最終 push／CI 尚未完成。唯讀 git 狀態顯示目前分支沒有 upstream，最終驗證紀錄仍未追蹤且三個反向連結尚未提交；僅靠 `status: doing` 不足以讓下一 session 分辨「待交付」與「已有另一篇收據」。

其餘指定項目核對一致：來源雜湊、10686 綠 2 紅及兩項重驗、三個單一 `[[Systems/...]]` 與雙向 `verified_by`、Windows 排除與實務輪數 REVISIT、兩個反引號修正的嚴格欄位閉包，以及 d050 舊案 CI 的固定射程，均未冒稱目前功能分支已通過主線 CI。未改檔、未重跑四輪。