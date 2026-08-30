# r3 兩席彙總(intake-guard v3;上限輪)
severity: blocker

| 席 | 結果 |
|---|---|
| 內部 delta(claude/sonnet) | 0 blocker;3 major blocking(F2/F3/F4)+ 2 minor;★其餘逐項驗證通過,含 PRIOR-ART 訂正「誠實」、宣告行判定「閉合」、T4「機械可讀」★ |
| 外家否決(codex) | 否決成立 blocker——★但只剩一條:T4 宣稱「doctor 每天跑」不實(daily-governance.sh 沒跑 doctor);其餘全讓步:「最後一步是人」不構成否決、27/16 可重現、T4 已達機械可實作、★值得進實作,補這一線後 r2 否決理由即消失★ |

## 收斂軌跡
r1=10 blocker(方案性)→ r2=1 blocker(數字)+定義缺口 → r3=內部 0 blocker、外家單一補件條件。逐輪縮小、可局部化——與 impact-鏡頭機械化(每輪不同結構性死因)相反形。

## r3 剩餘四件(各為一句話裁定/一條線)
1. ★外家★T4 接每日排程:daily-governance.sh 補 doctor(或明訂靠 push/CI 的 doctor 觸發並承認非每日保證)。
2. ★內部 F2★code 迴圈被計數卻無可遵守的慣例——code-loop skill 零前掃步驟;code-batch2/3 的 intake 是「撈回紀錄」不是前掃紀錄(v3 撤範圍刀時把兩種 intake 當一種)。修=T2/T4 範圍恢復為非 code 迴圈(這次理由對了)。
3. ★內部 F3★處置閘③只掃判定輪,而 intake_path 掛 r1 帳列 → 重驗常態掃不到。修=③ 對 intake 全輪掃(一句話)。
4. ★內部 F4★T4 觸發後恆真、無復位——會退化回 546 形態;條件(c) 近乎恆真(16 缺席目錄 9 個有 blocker 輪)。修=改滾動窗(最近 6 個非 code 迴圈),窗內達標自然靜默。
另 2 minor:數法補「排除非目錄項」(27 vs 28);母體 glob 統一。

## 處置
三輪到頂未機械收斂 → 停,攤給人裁(記「達上限未收斂」)。攤牌選項含:折入上述四件後人裁放行進實作(外家已明示此路)/不做。
