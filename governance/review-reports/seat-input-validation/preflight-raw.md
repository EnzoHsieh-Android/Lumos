severity: major

PF1  
severity: major  
blocking: 是  
引句:「格式錯誤應明講哪個欄位錯，避免工具崩潰被誤判成審查內容有問題。」

機械驗收只要求 stderr 含「擋下:」，未驗診斷是否指出頂層、`materials` 或項目索引。  
原句→建議：明講哪個欄位錯 → 分別斷言 `dispatch`、`materials`、`materials[i]` 等定位資訊。  
可執行反證：讓所有壞形態統一拋 `ValueError("bad dispatch")`，現有斷言仍會通過，但不符合核心目的。  
source佐證 file: `scripts/test_lumos.py:34027`  
source佐證 file: `scripts/test_lumos.py:34029`  
此項影響核心裁定第1點，需交正式席處置，不自行改裁定。

PF2  
severity: major  
blocking: 是  
引句:「全部資料形態驗完才讀材料或寫越界帳；不改報告、派工單、主線來源或使用者配置。」

測試只證明尾端錯項會回 rc2 且帳本不變，沒有證明錯項被發現前未讀取前面的材料。逐項「先讀再驗下一項」的錯誤實作仍可通過。  
原句→建議：全部驗完才讀材料 → 增加可觀測的讀取順序斷言。  
可執行反證：第一項放命名管道、第二項放 `{}`；正確實作應立即 rc2，逐項讀取實作會在管道阻塞並逾時。Windows 已排除，適用本案平台。  
source佐證 file: `scripts/test_lumos.py:34015`  
source佐證 file: `scripts/test_lumos.py:34019`  
source佐證 file: `scripts/test_lumos.py:34032`  
此項影響核心裁定第3點，需交正式席處置，不自行改裁定。

已完整前掃四項；未定義詞、壞引用、範圍矛盾無命中，機械宣稱語意有以上兩項。

已讀：`CLAUDE.md`、`governance/review-reports/seat-input-validation/preflight-source-spec.md`、`scripts/lumos` 的 `cmd_seat_check`、`scripts/test_lumos.py` 的三個指定測試、`docs/lumos-toolchain-knowledge/Projects/驗證層自證三件_計劃.md` 的 S1／射程／輸入條款。