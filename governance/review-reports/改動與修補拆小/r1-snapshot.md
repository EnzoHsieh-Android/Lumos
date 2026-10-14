---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
lands_in:
  - Systems/review-convergence-eval
  - Systems/pitfalls-code-loop
related:
  - "[[Verification/2026-10-14_修補大小與下一輪major回放]]"
  - "[[Projects/代碼審修復穩定性試行_計劃]]"
---
# 改動與修補拆小_計劃

代碼審常跑滿三輪仍有 major。帳本回放([[Verification/2026-10-14_修補大小與下一輪major回放]])顯示兩件事跟收不了斂有關:第一輪的改動越大越容易跑滿,每輪修補寫得越多下一輪越容易有 major;控制上一輪折入條數、第幾輪與分級之後,修補行數仍有獨立的關係。這份計劃做兩件事:把「先拆小、最小修法」寫成所有代碼審的建議(不擋),並把回放做成既有收斂評估工具的子指令,四週後用同一支工具比前後。

WHY:先對所有代碼審給建議、四週後用回放比前後,不在修復穩定性試行剩下三案試硬上限 [出處:2026-10-14 使用者裁;設計審 `修補大小上限試行` r1 四席] [因:三案約六個續輪判不出差別;編排者當場數行數有漏數新檔、併主線灌入、單位對不上等問題,事後由工具從凍結材料算就沒有] [不選:三案試硬上限;只記錄不給建議;改處置閘或加機械擋]
PRIOR-ART: Google Small CLs(https://google.github.io/eng-practices/review/developer/small-cls.html)主張小而自足的變更較易審、較易看出引入的 bug;本 repo 既有的收斂評估工具 `review_convergence.py` 已有讀帳與 JSON 輸出的骨架,回放接成它的子指令,不另開一支工具。
RETIRE-IF: 2026-11-11 用 `repair-size --since 2026-10-15` 比前後:若建議上線後第一輪新增超過 600 行的迴圈比例沒有下降(沒人照做),或跑滿三輪的比例沒有下降,就撤掉代碼審手冊那一行建議;子指令保留當觀測工具。

## 範圍

- 做:①收斂評估工具新增 `repair-size` 子指令;②代碼審手冊加一行建議(開審前改動新增超過約 600 行先考慮拆案;修補用最小修法,不夾帶重構與新機制);③驗證筆記改成指向子指令、改用更嚴謹的分析數字。
- 不做:不擋推送、不改處置閘、不改必派席與三輪上限;不在修復穩定性試行加條款(那邊的 S6 已撤案,見 `governance/review-reports/修補大小上限試行/r1-intake.md`);不讀設計審迴圈(凍結材料是整份文字,沒有新增行可數)。

## 做法

- **子指令** `python3 governance/eval/review_convergence.py repair-size <repo 根> [--since YYYY-MM-DD] [--bootstrap N]`,唯讀、印 JSON:
  - 讀帳:`<repo>/docs/.canary-log.jsonl`,沿用工具既有的讀檔上限、逐行解析、token 去重與排除 `kind == "spec-gate"` 的列(跟 `cohort` 同一套)。只取名字以 `code-` 開頭的迴圈;分級取該迴圈第一筆帶 `tier` 的列,只留 standard 與 high,沒有 tier 的迴圈列進 `skipped`(原因 no-tier)。每輪折入數 = 該輪帶 `findings_set` 那一筆(載體席)的 `folded_set` 加 `accepted_set` 條數。輪次取 `round` 欄位 `rN` 的 N;帳上輪數 3 以上叫「跑滿三輪」。
  - 讀卷證:第 N 輪凍結材料 `<repo>/governance/review-reports/<迴圈>/rN-snapshot.patch`;席報告用該輪各筆帳的 `report_path` 找,不靠檔名猜。
  - 修補新增行數(只算 N≥2):第 N 輪凍結 patch 裡以 `+` 開頭、不含 `+++` 檔頭的內容行,扣掉第 N-1 輪已有的同內容行(逐行序列比對);所屬檔案是簿記的不算。簿記判準直接載入 `<repo>/scripts/lumos` 讀 `_BOOKKEEPING_FILES` 與 `_BOOKKEEPING_DIRS`(同 `scripts/test_lumos.py` 載入主程式的做法),不在工具裡另抄一份;載入失敗 rc 2。超過 5000 行(重定基底)的輪排除並列在 `skipped`。
  - 發現與落點:從席報告本文解析(帳上的 `severity` 只是整份報告的最高值)。檔首第一個 `severity:` 行之後,每個頂格的 `severity: <值>` 行開始一條發現,到下一條為止;那段裡 `引句:「…」` 的內容去掉空白後,只出現在第 N 輪新改的行 → 差異內,只出現在沒變的行 → 差異外,兩邊都有、沒引句、錨不到各自另計。下一輪差異內 major = 差異內(含兩邊都有)且嚴重度 major 或 blocker 的條數;同時輸出不分落點的全部 major。
  - 摘要:①修補行數依排序等量切四組,各組下一輪差異內有 major 的比例;②依上一輪折入數分 8 層(1、2、3、4–5、6–8、9–12、13–20、21 以上),層內以中位數分大小兩半,Mantel-Haenszel 合併勝算比與加權機率差;③邏輯迴歸(log2 修補行數、log2 上一輪折入、第 3 輪以後、分級 high),以迴圈為單位重抽 `--bootstrap` 次(預設 500,固定種子)取 95% 區間;④第一輪凍結 patch 的新增行數依排序等量切四組,各組跑滿三輪與第三輪帳上最高仍 major 以上的比例。帶 `--since` 時,迴圈依首筆帳的 `ts` 日期分成之前、之後兩組,各算跑滿三輪比例與第一輪新增超過 600 行的比例。
  - 錯誤:帳本讀不了或有非物件列 → rc 2(同 `cohort`);單一凍結 patch 或席報告讀不了、超過大小上限 → 那一輪進 `skipped` 附原因,不補值、其他照算。
- **手冊建議**:代碼審手冊第 1 步(凍結材料)加一行;細節與依據放 `reference.md`,入口頁不寫日期與事故。
- **手冊門檻說明**:`reference.md` 那段一句話講清三個數字各管什麼:600 行是建議開審前拆案、1800 行是單席審材上限(超過拆開審)、5000 行是回放時排除重定基底。
- **驗證筆記**:正文改成指向子指令,數字換成子指令輸出(簿記判準改用主程式那組,四分組數字會跟舊版略有不同,筆記註明);舊的「併進修復穩定性試行」那行 WHY 標成作廢、指向本計劃;內嵌腳本拿掉。

## 驗收條款

- [S1] 當對一個含簿記檔、重定基底大差異與多輪凍結 patch 的小型假 repo 跑 `repair-size` 時,每輪的修補新增行數 應 不含簿記檔、應 扣掉上一輪已有的同內容行,超過 5000 行的輪 應 排除並列在 skipped [test:t_review_eval_repair_size]
- [S2] 當席報告的發現引句只落在上一輪沒變的行時,那條 應 不算進「下一輪差異內 major」、但 應 算進全部 major [test:t_review_eval_repair_size]
- [S3] 當同一份輸入跑兩次時,輸出 應 完全相同(重抽用固定種子);測試用的小型假 repo 帶 `--bootstrap 50`,整組在包裝測試的 90 秒逾時內跑完 [test:t_review_eval_repair_size]
- [S4] 當帳本有非物件列、凍結 patch 讀不到或超過大小上限時,子指令 應 以 rc 2 說明或把那一輪列進 skipped,不得補值 [test:t_review_eval_repair_size]
- [S5] 當帶 `--since` 時,迴圈 應 依首筆帳日期分成之前、之後兩組,各自輸出跑滿三輪比例與第一輪超過 600 行的比例 [test:t_review_eval_repair_size]
- [S7] 當讀驗證筆記 `Verification/2026-10-14_修補大小與下一輪major回放` 時,正文 應 指向 `repair-size` 子指令、數字 應 與子指令在 cacbdf0b 上的輸出一致,舊的併進試行那行 WHY 應 標成作廢 [manual:在 cacbdf0b 副本跑 repair-size,逐一對照筆記數字;看那行 WHY 帶 status:superseded 與被取代]
- [S6] 當讀代碼審手冊時,第 1 步 應 有一行開審前拆案與最小修法的建議,並指到本計劃 [manual:打開 skills/lumos-code-loop/SKILL.md 第 1 步確認那一行在、連結指得到本計劃]

## 回退

- 子指令:刪掉 `repair-size` 的分派與函式、`RepairSizeTests` 與 `t_review_eval_repair_size`,其他子指令不受影響。
- 手冊:刪掉那一行與 reference 的段落。
- 驗證筆記:還原那次提交裡筆記的改動。
- 三者互不依賴,可以單獨還原。

## 實務隱患

已排除:金流:這次只讀本機帳本與卷證,沒有任何付款
已排除:對外送出:子指令只印到標準輸出,不連網、不寄送
已排除:不可逆:唯讀分析,不寫任何檔、不改帳本
已排除:守衛面:手冊只加建議,不改任何閘、不擋推送
- 回放是事後觀察:「題目本身難」量不到,迴歸只排除量得到的因素;四週前後比較還會受同期其他改動影響,結論要保守。
- 卷證格式之後若改(凍結 patch 改名、席報告格式變),子指令要跟著改;讀不懂的會進 skipped 而不是默默算錯。

REVISIT:2026-11-11 跑 `repair-size --since 2026-10-15`,照 RETIRE-IF 判建議留或撤,交使用者裁

