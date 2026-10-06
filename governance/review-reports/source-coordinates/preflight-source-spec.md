---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
  - risk/守衛面
lands_in:
  - Systems/lumos-refcheck
  - Systems/pitfalls-code-loop
  - Systems/測試假綠形態
---
# 引用座標依實際換行_計劃


白話：引用檢查像查門牌，檔案只有兩層樓，特殊字元卻被算成第三層，讓不存在的座標通過。先把樓層數算正確，仍保留原本只驗存在性、不驗業務語意的分工。

WHY:用共用引用驗證入口修正行數，避免審查與表態各補一套規則 [出處:2026-10-06 固定源碼最小重現與 Systems/lumos-refcheck 決策 d1、d2]

PRIOR-ART:Python 官方 str.splitlines 明列 Unicode 行／段落分隔符、NEL 與控制分隔符；它的邊界比 universal newlines 更廣。已有文字讀取層處理常見換行，只需保留讀取層正規化後的 LF 邊界。https://docs.python.org/3/library/stdtypes.html#str.splitlines

RETIRE-IF:共用引用驗證入口改為提供已釘版本的來源行陣列且本計劃的反例全部由該入口守住時，撤掉本次局部行分割；不得與新入口並存第二套。

## 現場與重現

- 兩個 LF 行的有效 Python 檔，第一行字串含 U+2028，第二行是 value = 1。現有共用函式對第 2 行回傳錯引文，對第 3 行回傳 ok。
- 工作樹與釘提交兩條讀法皆重現；實際 refcheck CLI 對第 3 行回 0；表態路徑證據消費端也回 True。
- 最小命令與原始結果保存於本案卷證。這是上線前既有的引用行數問題，與修正關卡便宜錯誤功能無關；共用函式在該功能前後相同，不記成該功能的修補回歸。

涉及程式：`scripts/lumos` 的共用引用驗證與既有消費端；`scripts/test_lumos.py` 的引用測試。

圖譜邊界：[[Systems/lumos-refcheck]] 決策 d1、d2；[[Systems/pitfalls-code-loop]] 表態證據；[[Systems/check-j-regen-guard]] 重生來源引用；[[Systems/測試假綠形態]] 現場與翻紅前置。

## 核心裁定

1. 共用入口仍是 _validate_repo_ref；修正它的兩條讀檔分支使用同一行數判法。借用既有 LF 分割，排除字串裡的 Unicode／控制分隔符，移除單一末尾 LF 帶來的額外空項；空檔沒有第 1 行，中間與末尾的實際空白行不得消失。
2. 保留現有文字讀取層的通用換行與 BOM／解碼方式；不改檔案 bytes、Git 調用、釘版合法性、引用抽取、治理格式或 CLI 返回碼。
3. 只驗檔案與行號範圍存在；不新增語意驗證、引句匹配、來源真假政策或新依賴。既有目錄與無行號短路保留。
4. 引用與表態證據繼續共用原入口；回傳 tuple 與 manifest 格式不變。實際不存在的行必須回 line_out_of_range，不可再以多算的分隔符證明存在。

## 驗收條款

- [S1] 當有效兩行來源第一行字串含 Unicode 或控制分隔符時，共用引用驗證應保持工作樹與釘提交的第 2 行引文為實際內容，第 3 行及跨到它的範圍回 line_out_of_range；合法範圍保持首尾引文。[test:t_refcheck_physical_unicode]
- [S2] 當 refcheck CLI 收到第 3 行的工作樹或合法釘版引用時，refcheck 應回 1 並保留 out_of_range 統計；引用第 2 行仍回 0 且引文正確。[test:t_refcheck_physical_cli]
- [S3] 當表態路徑證據消費端驗證同一釘提交的第 3 行時，表態證據檢查應回 False 並說明超界；有效第 2 行保持 True。[test:t_refcheck_physical_dispositions]
- [S4] 當來源是空檔、單一空行、末尾空白行、沒有末尾換行、常見換行或帶 BOM 時，共用引用驗證應保留原本正規化與引文邊界；反向範圍、缺檔、目錄與無行號語義不退化。[test:t_refcheck_physical_legacy]

## 實務隱患

- 守衛面：會讓原本錯誤通過的座標被擋下。保留四種實際消費／讀取對照、原有 refcheck 與表態範圍測試；不修原始報告掩蓋問題，漂移引用用原始固定版本重驗。
- 來源邊界：文字讀取層原有 CR／CRLF 正規化仍保留，目標是排除其餘分隔符，不擴張平台相容性工作。
- 空檔與尾端：只移除最後一個分割空項；連續 LF 的真實空白行保留。驗有效最後一行與下一行超界，不能只看引文是否含關鍵詞。
- 分層與資源：沿用共用驗證與原 Git timeout，測試只在臨時 Git repo 操作，不寫使用者工作目錄、不外呼。
- 已排除:金流:此案只讀來源，不操作帳務。
- 已排除:對外送出:不發送外部業務訊息。
- 已排除:不可逆:不改來源檔與生產資料，提交可還原。
- 守衛面仍有風險，依設計審與完整推送閘，不列風險低。

## 回退

回退本功能提交即可恢復原讀法；保留原始紅燈與固定源碼卷證，不把舊的 phantom 座標改寫成正確證據。沒有資料遷移或新增長駐機制。

## 驗收與重驗界線

機械對照只證明座標範圍與引文位置修正，不證明引文的業務語意，也不證明真實代碼審輪數下降。
REVISIT:2026-10-20 抽查近期使用引用檢查的十次審查，統計錯座標發現與同類修補回歸；有來源行陣列新入口時依 RETIRE-IF 撤掉局部分割。
