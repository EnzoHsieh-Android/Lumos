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
# 負數發現計數在追加前拒收_計劃


## 問題與最小解

把發現數量填成負數，記帳入口仍回成功；兩席零發現報告的對照中，數量0可過處置閘，數量-1則先寫進不可撤回的追加帳、再被閘當成「有發現但無處置帳」拒絕。出處為negative-findings-counter卷證的實際CLI、兩種輸入及完整stdout/ledger。本案解的是輸入錯誤造成的重記，不能拿它證明修復回歸率或真實審查輪數已降低。

最小修復沿用cmd_canary對tokens、wallclock_min、scope_lines的非負檢查形狀，只在findings顯式給負數時、追加前回rc2。保留省略、0與正整數；不把全輪findings-set長度等同單席findings，不保留none為特殊ID，不改舊帳讀側、不改輪數上限、不解Windows。

PRIOR-ART: Python官方argparse文件的type章節區分型別轉換與後續驗證；int能轉負數，不等同數量有效。官方error方法對非法參數回2。既有cmd_canary成本欄已用下游非負檢查，借相同形狀、不增依賴或另造解析器。來源 https://docs.python.org/3/library/argparse.html#type 與 https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.error ，2026-10-06實讀。
RETIRE-IF: 既有共用數量驗證器能覆蓋cmd_canary所有CLI與直接入口、在追加前拒收負數並保持省略/0/正數控制時，刪本地重複分支、由同一組測試守共用驗證器。
REVISIT:2026-10-20 在canary寫入及本案卷證入口核對十份實際使用收據，區分「輸入錯誤拒收」與「修復造成的新缺陷」，不以合成案例冒稱審查輪數改善。

## 驗收

- [S1] 當發現數量為負數，記帳器應回rc2、指出--findings與負值，不追加帳列、不印成功訊息；已有帳逐位元不變、未有帳不建立帳本，普通及最佳化皆成立。 [test:t_canary_negative_findings_rejected]
- [S2] 當發現數量省略或為0及正整數，記帳器應保持原成功行為及欄位省略/值，不新增集合數量等式；有效零發現兩席應仍通過處置閘。 [test:t_canary_negative_findings_rejected] [test:t_canary_findings] [test:t_canary_carrier_quote_positive_controls]
- [S3] 當載體證據不完整或驗後換檔，記帳器應保持前案的提前拒收（PR20已合併main，主線CI待驗）；正規零發現輪與合法引句控制不受數量檢查影響。 [test:t_canary_carrier_zero_quote_rejected] [test:t_canary_carrier_invalid_report_encoding] [test:t_canary_carrier_evidence_changes_before_hash]

## 最小實驗與紅燈

未改生產碼前，實际CLI合法0兩席record都rc0、gate rc0；負數-1兩席record仍rc0、gate rc1，hash同份材料且合法對照可過，非其他閘代打。正式新測試普通及最佳化首版共14通過/16失敗/0略過；擴充首筆負數不建帳控制後，另留正式紅燈收據：合法控制全部通過，負數拒收與帳本不變都翻紅。原紅、來源sha及命令保存，後續綠燈不得覆蓋原收據。

## 回退

只回退本案負數入口檢查，保留主線既有引句/編碼/換檔防線及全部原帳；退回後負數重記風險恢復，需重新跑同一組紅綠與合法控制，不刪歷史資料、不修改已追加的canary列。生產入口還未動，先依規格閘判門與必要設計審通過後實作。


## 實務隱患

已排除:金流:僅本機審查數量欄位，不計算金額或發送款項。
已排除:對外送出:只驗參數並追加既有本機帳，本案拒收不發網路請求。
已排除:不可逆:不改帳格式或既有列，拒收不追加；回退程式不需收回已送資料，既有錯帳仍不清除。
守衛面:本案正是追加前數值邊界，不能排除；六席正式設計審後再實作。
併發:拒收分支只讀已解析整數，不寫共享狀態，不新增鎖；合法寫入仍沿用既有追加流程。
效能與資源:常數比較、一次stderr診斷，不新增檔案開啟、背景工作、依賴或第二套解析器。
回退:保留前案的UTF8、引句與驗後換檔防線；本案撤回只恢復負數舊風險，不能刪帳洗掉它。

擴充首筆負數不建帳後，正式紅燈14通過/20失敗/0略過；本機來源生產84d013c為前案PR20版本，前案PR CI已通過，main CI待驗。新案推送以交付後主線為基底並重驗控制，不把候選版本當已部署主線。

前掃PF1量到S2少綁真正驗兩席空輪的測試，語意HIT；恢復引用既有的新測試方法，沒有改核心裁定或測試。該方法整體紅包含負數檢查失敗，合法空輪控制本身已綠，不把條款紅誤稱合法路徑紅。前案PR20完整SHA 1a042f1efffb4999c6ad3fba6e3665766518fc95實際CI green/success，已合併main 8292a1d8f7aa15a4b05a78f86ae28d85be7db579；main CI正在跑，待真實查證才記完成。
