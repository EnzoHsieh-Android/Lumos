---
type: project
status: doing
created: 2026-10-06
updated: 2026-10-06
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/design-loop
---
# 載體快照非法編碼受控拒收_計劃

## 目標與實作前範圍

把已知的載體快照解碼例外變成可修正的拒收訊息，避免把輸入錯誤當程式故障而重開審查。本節為實作前紀錄（初版34條控制）：當時只做獨立查證與紅測試，生產入口尚未修改；後續成果另按固定來源寫Verification，不將本段當完成狀態。

既有 [[Issues/主程式讀取路徑漏接UnicodeDecodeError]] 要求逐入口判斷；[[Projects/載體零引句在記帳前拒收_計劃]] 曾重現但刻意排除此情況，若改rc2須另立輸入契約與正反控制。本案只補這一個入口，不關閉整個Issue、不重寫前案範圍。

PRIOR-ART: Python官方例外階層顯示UnicodeDecodeError不屬OSError；codecs文件的strict預設遇解碼錯誤拋UnicodeError，replace會改寫壞字元。沿用cmd_quote_check與報告入口既有受控rc2形狀，不新增依賴、共用層或解析器。來源 https://docs.python.org/3/library/exceptions.html#UnicodeDecodeError 與 https://docs.python.org/3/library/codecs.html#error-handlers ，2026-10-06實讀。
RETIRE-IF: cmd_canary若改用與quote-check共用的嚴格解碼入口，且本案所有普通/最佳化與同份原始bytes指紋控制持續綠，於該入口改動時移除本地重複捕捉；不以吞掉錯誤或替換字元當退場。

落點與沿用合約見 [[Systems/design-loop]]。本案不改處置閘第五步；既有四支相依回歸在規格閘真跑全綠。

## 驗收條款

- [S1] 當其餘參數與報告合法、載體快照包含非法UTF8 bytes，記帳器應回rc2、指出--snapshot與編碼錯誤、不吐traceback或成功訊息、不追加成功canary帳；已有帳逐位元不變、未有帳不建檔，普通及最佳化皆成立。 [test:t_canary_carrier_invalid_snapshot_encoding]
- [S2] 當載體快照有效UTF8且引句全錨，記帳器應保持LF/CRLF成功與同份bytes指紋；非載體的既有rawbytes雜湊政策應保持，不連帶強制解碼。 [test:t_canary_carrier_invalid_snapshot_encoding] [test:t_canary_carrier_quote_positive_controls]
- [S3] 當其他證據或數量不合法，記帳器應保留既有零引句、報告非法編碼、驗後換檔與負數拒收；缺檔OSError分流不得改成編碼診斷，不新增集合數量等式。 [test:t_canary_carrier_zero_quote_rejected] [test:t_canary_carrier_invalid_report_encoding] [test:t_canary_carrier_evidence_changes_before_hash] [test:t_canary_negative_findings_rejected]

- [S4] 當快照讀入階段出現非編碼且非I/O程式例外，記帳器應保留原例外，不改報成UTF8輸入rc2，成功帳不追加。 [test:t_canary_carrier_invalid_snapshot_encoding]

## 最小重現

主線8292a1d8的CLI84d013c與前項候選CLI52c9c4d7都以相同合法引句報告、先合法後非法快照對照：合法rc0且成功落帳，非法rc1/UnicodeDecodeError且帳不變，普通及最佳化相同。兩個來源的原始CLI收據各保存，不是負數修復回歸；正式紅測試另留來源指紋，後續綠燈不可覆蓋原紅。乾淨唯讀查證員找到前案已知探針與局部處理決策，沒有依0筆搜尋推定沒人處理。

## 回退

只回退本案快照解碼錯誤的受控拒收分支；保留前案零引句、報告編碼、換檔與負數守衛、原帳及測試。回退後恢復該輸入的rc1/traceback風險，但仍不得追加錯帳；重驗本案紅綠與合法對照，不刪帳或換ID洗歷史。

## 實務隱患

已排除:金流:只驗本機證據輸入，不計算或傳送款項。
已排除:對外送出:拒收不發網路請求，合法寫入沿用原出口。
已排除:不可逆:只收緊非法輸入且保留原追加帳，不遷移或刪帳。
守衛面:本案正是入口邊界，不能排除；規格閘及必要正式設計審過後才實作。
併發:不新增鎖或跨程序版本保證，保留同份讀入bytes與指紋核對。
效能與資源:只捕捉特定解碼例外，不吞Exception、不另讀快照或新增背景工作。
回退:不擴成全repo編碼整治，不改非載體政策與OSError分流；Windows排除。

REVISIT:2026-10-20 在本案CLI與卷證入口核對十份真實編碼拒收及恢復收據，區分輸入問題與修復回歸；沒有實際收據前不宣稱審查輪數下降。

## 初版34條控制的來源釘定（實作前）

正式舊碼紅測試34條：20通過/14失敗/0略過。合法LF/CRLF載體、report解析與原bytes指紋、非載體政策都通過；負數修復守衛仍是主線原碼。來源與red-source-bind釘定，若後續增減測試必另列版本，不改本份紅燈。前項PR21已合併main，合併前後整棵base樹無差、當前兩支來源SHA未變，僅快進基底；本案生產仍未實作。

規格閘：三條全綁、句式與回退有效，S1/S2紅、S3綠，相依四支全綠。S2引用整支新測試所以隨非法編碼斷言一起紅，20條通過包含合法、指紋與帳不變控制，不把條款紅說成合法路徑退化。

## 前掃折入與第三個測試版本（實作前）

PF-1量到廣泛吞Exception也能讓初版控制通過；原觀察為靜態，本次在隔離mutant實跑後HIT。加Runtime控制後38條旧碼24/14，壞廣捕捉36/2；再加IO分流後42條舊碼28/14，壞mutant38/4。初版34的20/14仍原樣存各自來源；不取代或混稱版本。新增S4只是把原不吞未知錯誤的限制接上控制；生產尚未實作。
