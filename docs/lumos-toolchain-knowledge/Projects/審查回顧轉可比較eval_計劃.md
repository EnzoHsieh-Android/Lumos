---
type: project
status: done
created: 2026-10-07
updated: 2026-10-07
tags:
  - type/project
  - status/done
  - scope/evals
lands_in:
  - Systems/review-convergence-eval
---
# 審查回顧轉可比較eval_計劃

白話：把「為什麼跑滿」的回顧變成能按同一道題、同一把尺比較的資料；缺資料就說不知道，不把格式合格當修補有效。

WHY:沿用既有母體與證據，不將兩份人裁回顧當全體樣本 [出處:2026-10-07使用者補強指示、eval_reuse_check唯讀核對及當次retro-stats]
PRIOR-ART:借用既有全迴圈分輪、回顧判定與A/B缺場思路；Anthropic建議同題多次trial、結果與trace分開及修復／保留兩組驗收 https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents 。Google SRE以證據與行動項做回顧 https://sre.google/sre-book/postmortem-culture/ 。不新增依賴、模型執行器或產品閘。
RETIRE-IF:既有eval框架可提供相同全體帳上樣本、固定案例與成對品質比較時，刪除此衍生入口；連續十份實輪資料沒有改善可比性且補資料成本較高時，保留原始卷證並撤掉自動彙整。
REVISIT:2026-10-21 核對首批實輪receipt的完整性、漏報及成對樣本；不足實輪不宣稱優化有效，重估是否保留此入口。

## 做法

獨立零依賴eval工具提供cohort、template、compare三種唯讀入口，結果僅印stdout。母體從原始審查帳按編號收集code迴圈，不以有人裁作篩選。分輪與漏斗沿用既有讀法的語意；回顧狀態另外查既有retro-stats，context不能代替原輪帳。各code編號全列，重記編號可能代表同一任務，觀察編號數不當獨立任務數或全生產分母。

cohort輸出來源指紋、實際分輪與成本已知／未知；template另產待補案例骨架；不從末輪嚴重度、折入數、關门事件或family推算收斂或因果。無完整成本資料不灌零；重複token相同原件只計一次，有衝突則保留問題與未知。帳缺失、非法JSON/UTF-8、非一般檔或超限回錯，不輸出完整資料集的假象。

案例釘起點commit、輸入／判準／環境指紋與finding來源；group ID負責同根因不跨train/held，分組須人工核對，生成骨架不自動填補未知。固定seed的group雜湊只決定split，不代表樣本獨立或未受訓練污染。

兩組的模型固定一致，workflow與dispatch指紋由manifest明訂。每題每組有同數repeat編號；比較讀取帶SHA的JSON原始receipt，核對案例、試行、實際載入的起點／產物與結果欄位。repair、preserve、新缺陷分開；已執行而失敗的產品驗收仍進分母；未完成、未知、載入錯源、指紋改變、同slot重複與缺場保留原因，不選最後一次或最好一次。僅在相同case及repeat雙方皆有效時計算成對品質差；輪數差只算雙方品質通過的場次，成本有完整資料才给均值，另列覆蓋數與split分層。

receipt核對只證紀錄一致，不是對產品重新執行、不是真人簽核或安全隔離；原始輸出與人工裁定仍需留存。工具不執行manifest或receipt內的命令，不載入外部repo程式。先以受控反例證明拒絕錯判，再以真實帳本試行；合成trial不當模型成效。

## 條款

- [S1] 當沒有滿輪人裁、輪次混用或成本缺件時，資料集應保留帳上code樣本與未知，且參考context不能覆蓋原始分輪 [test:t_review_eval_cohort]
- [S2] 當案例起點、輸入、判準、分組或模型條件不齊／矛盾時，manifest應拒收而不補造值 [test:t_review_eval_case]
- [S3] 當實際載入來源、receipt雜湊、執行狀態或結果資料不符時，試行應列未判定並保留原因；產品驗收失敗仍是有效負例 [test:t_review_eval_trials]
- [S4] 當少輪但退化、缺一側、試行重複或成本未知時，比較應按同題同repeat保留分母、先品質後成本且不報虛假改善 [test:t_review_eval_comparison]

## 實務隱患

已排除:金流:只讀本機紀錄與印出衍生JSON
已排除:對外送出:不呼叫服務或執行模型
已排除:不可逆:不改原始帳、回顧或產品資料
已排除:守衛面:不影響審查放行、輪數或既有閘判定

## 回退

刪除此工具及專屬測試入口，保留原始審查帳、回顧與來源卷證；衍生JSON可重建。錯誤分組或判準應修正manifest並重新比較，不覆寫歷史原件。
