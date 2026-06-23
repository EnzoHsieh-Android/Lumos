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

## 2026-06-21 觀察 + skip-空轉 bug 修復
- **覆蓋檢查首次實戰生效** ✅:loop 選到 backlog 的「judge 單一不可靠」gap,orchestrator 認出「已被 judge-perturbation spec 覆蓋(評估後放棄)」→ skip、不重做。昨天加的覆蓋檢查機制 work 了。
- **但暴露 skip-空轉 bug**:skip 後「當天結束、不循環選下一個」→ backlog 頂部是已覆蓋 gap 時整天空轉,下面真 gap 永遠輪不到。
- **修時又發現「重加洞」**:單純加 while 循環不夠——skip 的 gap 被 pop 出 backlog 後,下一輪 `add_gaps`(當日 gaps)會把它**重新加回**(dedup 只看「在不在 backlog」),可能又選又 skip 撞 cap。
- **完整修(16 test 綠)**:① autonomous-loop.sh 主流程包 while,skip→continue 選下一個(SKIP_CAP=3 防空燒);② gap_select 加 **covered 機制**(`covered.jsonl`):orchestrator 判 skip 的 gap 由 `mark_covered` 永久記下,`add_gaps`/`select` 都跳過——堵重加洞、已放棄/已覆蓋的 gap 永久排除。
- 待下次 cron 實戰驗證循環 + covered 排除。

## 2026-06-22 修復後首次「正常展開」實戰(audit-trail-persistence)
- 選 backlog[1]「治理留痕」→ 6 輪 design-loop → **未收斂、不放行、pending 空(正確)**。dry-run 沒碰 repo。
- canary:r1 missed(blocker)/r2 caught(major)/r3 missed(major)/r4-r6 caught(blocker)。**opus 單家族 canary missed 2/6 ≈ 33%**。
- 4 輪 caught 但 severity 一直 ≥major → 建不出「連 2 輪 clean/minor tail」→ 撞 cap 6 正確不放行。auditor 抓到的是**真 blocker**(捏造路徑/orchestrator 隔離違反/ts-sort 跟 append-order 矛盾/invalid bash/module import 路徑),非 canary 誤報。
- 卡點:新組件 audit_writer.py 每輪修完又冒新問題(組件多、互相牽動)= **gap 偏大、該拆小**的訊號。
- **副作用待議**:未收斂的 gap 被 select 的 pop_top 消費掉、不回 backlog → 除非日報重報否則此真 gap 遺失,且重報也是從頭 brainstorm(沒記住「上次卡在 audit_writer.py」)。
- 側證跨家族價值:opus missed 2/6 正是 Qwen 第二 auditor 能補的點(呼應 cross-family-audit 討論)。

## 2026-06-23 重大發現:orchestrator 一直在「模擬」而非真跑
- 06-23 10:10 loop 報 converged(check-t-sentinel-combo, cross_verdict=endorsed, rounds:5),但 scratch `spec/` 空、無 `.canary-log.jsonl`、kg 空。
- orchestrator result 白紙黑字:「intellectual **simulation**」「**no files written, no CLI executed**」「**Simulated** opus auditor/judge」「**Simulated** cross_audit returns」。
- 即 orchestrator 把 dry-run 誤解成「腦內模擬、什麼都不真做」——spec/canary/auditor/cross_audit 全是它自說自話,converged/endorsed 全幻覺;qwen 那個 finding 是 orchestrator 編的、qwen 根本沒真審。
- **架空整個 loop**:canary 防放水、judge severity、cross-family 補盲全是假的。很可能從 06-20 上線起一直如此(當時沒查 scratch 真產出、誤以為『spec 品質高』)。
- 修:orchestrator-prompt 加「⚠ 執行紀律」塊(dry-run≠模擬、必須真執行所有工具、收尾前自查 spec+canary-log 必須存在)。**待下次 cron(06-24 10:10)驗證 orchestrator 是否改為真跑**(查 scratch spec/canary-log 有沒有真產出)。
