---
type: system
status: done
created: 2026-07-03
updated: 2026-07-10
tags:
  - type/system
  - status/done
verified_by:
  - "[[Verification/2026-07-03_convergence-evidence-gate]]"
  - "[[Verification/2026-07-09_loop三輪壓縮]]"
  - "[[Verification/2026-07-10_審計loop研究硬化]]"
summary: |-
  KEY:[2026-07-10]panel 輪有效升級 near-perfect——caught≥2 且 0 missed(中段分數弱訊號不背書收斂;borrow mutation score 文獻,見[[Projects/收斂閘caught-rate修正_計劃]])
  FLOW:每輪 canary record --findings N(辯方存活折入條數)→loop status --gate --spec <md> --repo <root>→K-streak(必要)∧G1(_refcheck_scan 引用座標 0 missing/0 超界)∧G2(findings 單調不增+末輪≤1+末步下降,K=1 退化末輪=0)→全過 GATE PASS rc0｜cross_audit:_build_prompt sentinel 定界+_parse_worst 末行優先回(sev,parse_fallback)→§2.5c 計票:≥major 經機械驗證存活才 +1 reject,全反證=endorsed-after-refute 放行
  KEY:收斂判準從「輪次算術」升級「證據錨」——「連 K 輪各挖 5 條 minor」與 [1,1] 穩態涓流不再算收斂;輪次紀律保留為必要條件非充分條件(退役的是充分性)
  KEY:向後相容三條——不帶 --gate 輸出與 rc 分毫不變;不給 --findings 鍵不寫;run_cross_audit 既有鍵不動只增 parse_fallback
  KEY:G2 fail-closed(tail-K 缺 findings 欄位即擋)+ 欄位互證(clean⇒0、minor⇒≥1,矛盾即擋);G1 用 _refcheck_scan 只驗 spec→repo 指涉、不驗內部一致性(canary 保留地)
  KEY:Confident Liar 條款(§2.5c)——unanchored(指控與 ground-truth 無字串交集)單獨不撐 reject;parse_fallback 遍不計票;disputed 門票從「qwen 喊 major」改「喊的 major 驗過還站著」
  KEY:誠實天花板——findings 數源頭仍是 LLM 裁決(gate 機械化算術非數字正確性);枯竭≠挖乾(同門盲點趨同);sentinel 擋混淆不擋對抗注入;§2.5c 是 prompt 層散文契約無機械回歸守衛;換 loop_id 洗紀錄/--spec 無綁定向量留 v2(spec hash 綁定)
  KEY:平行 panel 收斂(2026-07-09,`--panel`,見 [[loop三輪壓縮_計劃]])——G2 序列枯竭是**循序深度**信號、配不上平行拓樸;panel 模式改 capture-recapture 殘餘估計(從 W 獨立審計員 findings 重疊估母體枯竭,取代 findings 序列遞減)+ 輪有效(caught≥2且0missed,near-perfect)+ 存活 max≤minor;無 capture_counts=fail-closed;legacy K-streak∧G1∧G2(無 --panel)完全不變
  DEP:[[lumos-refcheck]](G1 消費 _refcheck_scan)｜[[canary-audit]](記錄面)｜cross_audit.py
  TEST:t_canary_findings 3 + t_loop_gate 16 checks(CLI)+ TestCrossAudit 新 4(unittest);352 passed 全綠
  VERIFY:[[2026-07-03_convergence-evidence-gate]]
decisions:
  - content: 方案 A(判準增強落在既有 loop status 的 --gate 旗標);否決 B 統計離散度模型與 C 只修 cross_audit 定界
    id: d1
    context: B 的權重/閾值全是拍腦袋參數,把「一致≠正確」換成「權重≠正確」,違反 mechanical-not-motivational;C 只治複核端不動判準本體
    why_chosen: 每道錨都是確定性核對(rc/字串比對/整數單調性),零權重參數;複用已落地 refcheck;向後相容
    decided: 2026-07-03
    valid: true
  - content: 「留痕完整」不設錨——它是 K-streak 的邏輯後果({streak 通過}⊆{留痕完整}恆真),另設=零判別力裝飾
    id: d2
    context: design-loop R1 辯方對此 major 反駁失敗、維持原判,導致當輪拆錨重構(gate 從三錨收斂為兩錨)
    why_chosen: 誠實拆除不湊門面;歸因回歸測試(缺 severity 斷在 K-streak)固定此結論、防未來重新發明空錨
    decided: 2026-07-03
    valid: true
  - content: cross_reject 計票改「≥major 經機械驗證存活才 +1」,全反證=endorsed-after-refute 放行
    id: d3
    context: qwen disputed 三連(refcheck/loop-stall×2/本 spec)的 ≥major 指控經機械驗證全數不成立,仍消耗放行預算逼人裁;本 spec 自己的放行路徑上 _parse_worst fallback 撿引文誤報 blocker 現場重演
    why_chosen: 自信但經不起機械驗證的否決不該有否決權;disputed 升級人核精神保留,只改門票條件
    decided: 2026-07-03
    valid: true
---
# convergence-evidence-gate

design-loop 收斂判準升級:**輪次算術 → 機械證據錨 + 發現枯竭**。四組件:`canary record --findings`(記錄面)、`loop status --gate`(判準面)、cross_audit sentinel 定界+解析硬化(根因修)、§2.5c 計票語意(prompt 層)。

## 動機
「連 K 輪一致」量的是穩定不是正確——審計員可每輪自信地漏同一個洞,跨家族複核可連兩輪言之鑿鑿指控不存在的問題(7/2-7/3 日報 + qwen disputed 三連實證)。收斂的最後一判改錨在騙不過的東西上:機器核對的引用座標、機械可讀的發現枯竭序列、經得起實跑反證的否決。

## 消費端
- 自動 loop:`governance/autonomous_loop/orchestrator-prompt.md` 步驟 6(--findings)/8(--gate)+ §2.5c 計票。
- 手動 loop:`skills/lumos-design-loop/SKILL.md` 硬閘/步驟 5/步驟 8。
- 方法論:`docs/methodology/圖譜即合約.md` loop 表證據閘列 + 原則 5 計票句。

## 相關
- 設計稿:`docs/design/2026-07-03-convergence-evidence-gate.md`(design-loop 4 輪、canary 4/4、R1 辯方維持 major 拆錨重構;qwen disputed 經人裁機械反證後放行)。
- 實作計畫:`docs/superpowers/plans/2026-07-03-convergence-evidence-gate.md`。
