# Dry-run 觀察(Task 7 起頭)

## 第一次端到端 dry-run(2026-06-20,MAXR=2)
**整合驗證成功:流水線端到端跑通。**
- 日報 fallback(06-19)→ gap_select 自主選中 gap(L3 腐化偵測信心門檻)→ orchestrator → 放行閘(未收斂→正確不放行) ✅
- orchestrator 自主 brainstorm 出真 spec(`l3-threshold-calibration`)+ 嵌套 spawn opus auditor+judge + 自判 caught/missed + `lumos canary record` ✅
- design-loop 真跑 2 輪:R1 caught/blocker(折一堆真錯)、R2 missed(--skip-time-check 未識別) ✅
- **成本**:16 分鐘 / 2 輪(brainstorm + 2×[auditor+judge] opus)。完整 6 輪估 ~40-50 分鐘。對齊成本節「單日 ≤14 agent」量級。
- $0 OAuth headless,orchestrator 不誤改 repo(record 寫 /tmp scratch)。

## 發現的真問題(上 cron 前要調)
1. **gap 去重要排「已落地」的**:orchestrator 選的 L3 門檻 gap,其實已被 `rot-eval`(已收斂 ready)覆蓋——`gap_select` 沒查「docs/design 已有對應主題」。對齊 spec「第二·五步回顧落地」。改進:gap_select 排掉已有對應 spec 的 gap。
2. **dry-run 不該碰 repo**:orchestrator 在 `docs/design/` 寫真 spec,未收斂/dry-run 也留在 repo。應寫到 scratch,**收斂後**才移進 repo/pending(dry-run 完全不碰 repo)。
3. **R2 missed(canary type b 被合理化)**:又一次印證 canary 自評弱、type b 在某些 spec 不公平(spec 已列「最弱環」)。
4. MAXR=2 不夠收斂;真觀察要 MAXR=6。

## 結論
**Task 6 整合達成**(流水線串通、orchestrator 能自主跑完 brainstorm+design-loop)。**先不上 cron**——待調問題 1(gap 去重)+ 2(dry-run 不碰 repo)再上,否則會在 repo 留半成品 spec、重複做已落地的 gap。

## 第二次 dry-run(2026-06-20,調後驗證)
- **調 2 成功**:dry-run repo 完全未被碰(git status == baseline、docs/design 無新 auto spec)。orchestrator 寫 scratch,收斂後才入庫。
- **整條鏈活起來的證據**:今早 9:30 日報(新路徑+昨晚改的 prompt:主軸=驗證層、對抗視角)自動產出一個**打臉 lumos 收斂機制**的 gap——「別讓被審者自填收斂門檻,讓 judge 覆蓋 severity / 收斂改述成『尚未被駁倒』」。autonomous loop 自動選中它、brainstorm 出 `judge-severity-gate` spec、跑 design-loop。**日報對抗視角 → 自動選中 → 要改進 lumos 自己的最弱環(F-R3-1)。**
- **發現 parse bug 並修**:orchestrator result 在真 JSON 前夾敘述,敘述含 `{clean,minor}` 干擾,貪婪 regex 抓偏 → 改 `orchestrator_result.extract_json`(從最後一個 { 往前試,TDD 2 test)。
- orchestrator 行為正常:judge-severity-gate 2 輪都 blocker/major → 未收斂 → 正確不放行。

## 設計缺口(MAXR=6 觀察發現):未收斂但有價值的 spec 會丟在 scratch
judge-severity-gate(loop 自己挑的、修自己最弱環、6 輪磨到 R6 minor、雙源損益論證)撞 cap 未收斂 → 按設計 dry-run 不入庫 → 躺在 /tmp 等被清。**改進方向**:未收斂但「接近 + 有價值」的 spec 該有去處(如 governance/pending-unconverged/ 或 backlog 標『已展開、R6 minor、待人決』),而非直接丟。本次人工撈出存 docs/design/2026-06-20-judge-severity-gate.md(標 DRAFT/未收斂)。
