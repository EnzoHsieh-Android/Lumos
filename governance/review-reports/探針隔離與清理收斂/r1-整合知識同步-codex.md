severity: major
審材：governance/review-reports/探針隔離與清理收斂/r1-snapshot.md

## 前言／與既有試行的關係

severity: major
blocking: 是
引句:「本計劃先修量測儀器的共同邊界，之後才用其餘試行案例判斷三輪能否收斂。這不是自動取得第5輪代碼審名額。」
finding: 規格沒有裁定本次實作及其代碼審算「第1案後續」、「第2個新工作」，還是五案試行之外的前置工作。既有試行表仍有第2至5格待登記，且明載同案續修不得換號洗輪次；三個月後接手者會得到三種都說得通的記帳方式，五案的輪次、成本及收斂率因此不可比較。最小重現：完成本計劃並開一個新 code-loop，若登記為第2案則剩3個新工作；若視為第1案續修則形成未授權的第5輪；若排除於試行則這次真實審查成本不進樣本。三種結果均符合目前文字。佐證：`docs/lumos-toolchain-knowledge/Projects/代碼審修復穩定性試行_計劃.md:48`、`docs/lumos-toolchain-knowledge/Projects/代碼審修復穩定性試行_計劃.md:122`。應在本計劃直接指定唯一歸屬與回寫原試行表的時點。

## PRIOR-ART／RETIRE-IF

已讀，無 finding。

## 根因與取捨

severity: major
blocking: 是
引句:「刪除本次副本並報儀器錯誤；不得當作模型失敗。」「`--keep` 明確保留每次副本並印其路徑，僅供本機診斷」
finding: 失敗副本的處置互斥。有效 Git 設定驗收失敗時，前文要求刪除副本；`--keep` 又要求保留每次副本，S2與S3也分別重述這兩種結果，沒有寫哪條優先。最小重現：準備含 local include、有效 remote 與外部 hooksPath 的合法頂層 repo，執行 `scenario_probe.py --keep --repo <repo>`；實作者依S2會刪除唯一能診斷的副本，依S3則保留本來被要求清掉的拒絕現場。現行 `--keep` 只控制最終共用副本清理，無法替規格提供既有先例，見 file: `scripts/scenario_probe.py:846`、file: `scripts/scenario_probe.py:988`。應明定 setup／驗收失敗時 `--keep` 是否生效，以及保留路徑如何輸出。

## 驗收條款

severity: major
blocking: 是
引句:「刪除失敗為 fatal 儀器錯誤：當次不算有效分數、整批 inconclusive、退出碼 3、後續 runner 零呼叫。」
finding: S4只要求執行期標成 inconclusive，沒有要求 `--history` 持久欄位保存該狀態；現行 `history_record` 只存 passed、total、failed、excluded，未存 inconclusive。最小重現：第一題有效通過，第二題 runner 完成後副本刪除失敗；主輸出可顯示整批 inconclusive、rc3，但歷史仍可能寫成 `passed=1,total=1`，後續只讀歷史者會看到100%通過。file: `scripts/scenario_probe.py:820`、file: `scripts/scenario_probe.py:985`。既有圖譜已把相同欄位缺口列為未解資料口徑問題；本規格新增 fatal 語意後仍未把它接入測試。應增加歷史紀錄的 `inconclusive`／fatal 原因與回歸斷言，並指定舊讀者相容方式。

S1、S2、S3、S5其餘語意已讀，無 finding。

## 先紅後綠與邊界

已讀，無 finding。

## 實務隱患

已讀，無 finding。

## 回退

已讀，無 finding。

## 審計修正紀錄

已讀，無 finding。

總結：最嚴重 severity major，blocking 3 條。
