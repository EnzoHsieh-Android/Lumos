severity: major

範圍:架構對齊鏡頭(範圍解析、共用函式、範本載入、設定讀取、閘名與事件、掛鉤、CI、紀錄檔與項目檔形狀、每支檔有家)。對照 negguard repo 的 `scripts/lumos`、`scripts/hooks/pre-push`、`.github/workflows/ci.yml`、`governance/anchor-baseline.json` 核對。前兩輪的架構折法(開關 `note_reread.gate`、`_nodehome_name_status(norm=False)`、閘名、範本共用、紀錄檔形狀、頂端無資料夾)照現況查過,落實無誤。

## F1 改掛鉤與測試檔會讓錨點驗證紅,計劃全文沒有重簽基準線這一步
severity: major
blocking: 是
引句:「在存量漂移檢查那一段(逐 ref、帶推送參數)之後加一段」
file: `scripts/lumos:19197`
1. `ANCHOR_FILES` 列了 `scripts/hooks/pre-push` 與 `scripts/test_lumos.py`(同一常數,`scripts/lumos:19197-19201`),基準線 `governance/anchor-baseline.json` 第 7 行存著 pre-push 的 sha256。
2. 推送前掛鉤自己在 `scripts/hooks/pre-push:239` 跑 `anchor verify`,不符就擋;CI 的 `Anchor verify (baseline 缺失必紅)` 那步(`.github/workflows/ci.yml:181` 附近)也跑。近幾次動掛鉤的提交(a60bf31e、d6688f76)都同時動了 `governance/anchor-baseline.json`,是既有做法:改錨點只能走 `lumos anchor approve --note`(重算加治理帳事件)。
3. 這份計劃要改掛鉤(第 4 節)、改 `scripts/test_lumos.py`(S1 到 S14 全是新測試),但〈做法〉〈回退〉〈條款〉〈上線〉都沒提 `lumos anchor approve --note`。照字面實作:實作提交只含程式、掛鉤、測試、筆記,推送前掛鉤的 anchor verify 對新掛鉤與新測試檔算出的雜湊對不上基準線 → 整個推送被擋(且掛鉤本身這一道在我方新增的 reread 段之前就先擋了)。CI 同樣紅。
4. 回退也一樣:revert 掛鉤那一處(〈回退〉第一條)會再讓雜湊變一次,要再簽一次基準線;〈回退〉沒寫。
5. 建議:〈上線〉的「推送前的順序」加一步「掛鉤與測試檔改完後 `lumos anchor approve --note "<理由>"`,基準線併進同一個功能提交」;〈回退〉的兩種回退各加同一步;S9 的實作驗收加「anchor verify 過」。

## F2 「掛鉤裡唯一不照 128 以上一律停」的說法跟同檔現況不符,理由站得住但引用的先例錯了
severity: minor
blocking: 否
引句:「這道只提醒,被外部砍掉不該擋推送(CI 那邊同理吞掉)」
file: `scripts/hooks/pre-push:215`
1. 計劃第 4 節要求在掛鉤註解寫「這是掛鉤裡唯一不照 128 以上一律停的一段」。同檔已有兩處只提醒的呼叫完全不看回傳碼:`bound-tests --advisory ... || true`(`scripts/hooks/pre-push:215`、`217`)與 `test-layers ... 2>/dev/null || true`(`scripts/hooks/pre-push:499`),含 130 也一併吞掉。所以「唯一」不成立;照寫進註解會是一句錯話。
2. 實際的既有分法是:會擋的閘過 `pp_stop_if_signaled`(表頭註解 `scripts/hooks/pre-push:47-49` 的清單),只提醒的全吞。本案「只停 130」是第三種形狀。理由(只提醒的被 OOM 砍掉不該擋推送)站得住,先例上也偏向「全吞」;保留 130 這一條是 r1 的取捨,不算錯。
3. 建議:註解改寫成「只提醒的呼叫本來就不擋(比照 bound-tests advisory、test-layers);這裡另外保留 Ctrl-C(130)停下」,並在 `pp_stop_if_signaled` 表頭註解的清單旁註明只提醒段不在其內,免得下一個維護者以為漏了。理由放行:只是註解精度,不改行為。

最高等級:major;blocking 共 1 條
