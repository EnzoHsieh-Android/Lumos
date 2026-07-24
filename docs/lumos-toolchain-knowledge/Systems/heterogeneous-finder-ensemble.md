---
type: system
status: done
created: 2026-07-09
updated: 2026-07-09
self_audit: sonnet/2026-07-24
verified_by:
  - "[[Verification/2026-07-09_loop三輪壓縮]]"
related:
  - "[[pitfalls-code-loop]]"
  - "[[convergence-evidence-gate]]"
  - "[[loop-convergence-recording]]"
  - "[[canary-audit]]"
tags:
  - type/system
  - status/done
summary: |-
  FLOW:code-loop 一輪 panel → 各 finder 產 finding-key(LLM reviewer 手動 --finder｜pitfalls --diff SARIF linter/regex 自動 --from-pitfalls｜測試失敗/mutation 存活)→ `lumos loop capture-counts` 跨 finder 正規化+數重疊 → capture_counts → `canary record --capture-counts` → `loop status --gate --panel` 判 capture-recapture 殘餘那條
  KEY:code review ≠ spec review——程式碼可執行+可靜態分析,最佳解是**異質 ensemble** 非純 LLM panel(文獻:AutoSafeCoder｜Multi-Agent Code Verification via Info Theory arxiv 2511.16708 submodularity｜Greptile TREX｜CodeRabbit sandbox｜PBR defect-type mapping)
  KEY:異質 = 買真獨立票——確定性驗證器(SARIF linter/測試/type/mutation)錯誤剖面與 LLM 正交,直擊「9 judge 2 票」相關性天花板(純 LLM panel 即使多樣仍相關);重疊(同洞多 finder 中)= 更強收斂信號
  KEY:capture_counts 語意=各 distinct finding-key「被幾個 finder 找到」的次數列表;跨 finder 正規化(casefold+strip)、finder 內去重;降序回傳決定性。餵 _estimate_remaining_defects(Chao1)算殘餘
  KEY:--from-pitfalls <range> 按 `source` 分組——每個 linter driver / pitfalls 內建各一個確定性 finder(免手貼);共用 _pitfall_diff_collect(純計算不印,與 _pitfall_diff_mode 印分離);capture-counts 是 vault-free 純機械原語
  KEY:誠實邊界——重疊計數機械化只買「算術正確」不買「finding 正確」;capture-recapture 小樣本出極端值當一個信號非 oracle;辯方可執行 falsification(跑測試/repro 殺假陽)是 code-loop 另一半、非本節點
  DEP:[[pitfalls-code-loop]](--from-pitfalls 收割 pitfalls --diff 命中)｜[[convergence-evidence-gate]](loop status --panel 消費 capture_counts)｜[[loop-convergence-recording]](_estimate_remaining_defects/canary record --capture-counts)｜[[canary-audit]]
  TEST:t_capture_counts_from_finders(5)+t_loop_capture_counts_cli(7)+t_loop_capture_counts_from_pitfalls(5)+t_pitfalls_diff(11)+t_pitfalls_lint_integration(15,重構後逐鍵不變);865 passed
  VERIFY:[[2026-07-09_loop三輪壓縮]]
decisions:
  - content: |-
    id: d1
      code-loop 繼承 design-loop 的 panel 機制 + capture-recapture 收斂,但 panel 成員換成
      「LLM reviewer + 確定性工具(SARIF linter/測試/type/mutation)」的異質組合、辯方改可執行反證
      ——不是「design-loop 換 canary 名字」。
    context: 使用者質疑「code-loop 可以沿用 design-loop 慣例嗎?程式碼的 review 方式不該不一樣?」上網找解(PRIOR-ART 先問世界)
    alternatives_considered:
      - "純 LLM 多樣 panel(照搬 design-loop):問題=同族 LLM 錯誤相關,撞『9 judge 2 票』天花板"
      - "只靠既有 mutation 冒煙:抓不到審查層敷衍,且非跨 finder 重疊信號"
    why_chosen: 文獻(submodularity)證異質分析器各加獨立資訊;確定性工具與 LLM 錯誤剖面正交=真獨立票;且 lumos 已有 SARIF linter(.lumos/lint.json)/測試 gate/mutation,大半是接線既有件
    trade_offs: 需編排者把各 finder 命中收齊(--from-pitfalls 已把 linter 那半自動化);端到端無人跑仍待自主 orchestrator(暫停中)
    decided: 2026-07-09
    valid: true
  - content: |-
    id: d2
      便利原語(--from-pitfalls 自動收割 linter 命中)與端到端無人跑是兩件事;前者不卡自主 loop 暫停,現在就做。
    context: 使用者追問「linter 命中→餵進去仍手動串」何意,釐清我把兩者混淆
    why_chosen: 手動路徑最煩的一步(手貼 linter file:line)純 lumos 機械可消,與自主 orchestrator 無關
    decided: 2026-07-09
    valid: true
---
# heterogeneous-finder-ensemble

code-loop 三輪壓縮 panel 的**異質 finder ensemble** 接線——把「程式碼可執行 + 可靜態分析」這個 spec review 沒有的結構優勢,落成 capture-recapture 的獨立票來源。

## 為什麼 code review 要和 spec review 不一樣
design-loop 審 spec(散文),只有 LLM 審計員這一種 finder;完整性理論上不可判定(散文無限可細化)。code-loop 審 diff(程式碼),多了**確定性驗證器**:SARIF linter、測試、type checker、mutation。這些的錯誤剖面**與 LLM 正交**——LLM 漏的 off-by-one,linter 的 rule 可能剛好抓;linter 抓不到的業務語意錯,LLM 抓。

純 LLM panel 就算派多樣 reviewer,錯誤仍相關(同模型家族、同盲點)——這是「9 judge 2 票」天花板。摻確定性工具才買到**真獨立票**。文獻用 submodularity 數學證明異質分析器各加獨立資訊([Multi-Agent Code Verification via Info Theory](https://arxiv.org/html/2511.16708);[AutoSafeCoder](https://arxiv.org/pdf/2409.10737) = Coding + Static-Analyzer + Fuzzing 三種不同 agent;Greptile TREX / CodeRabbit sandbox 則證「先跑再信」的可執行反證)。

## 機械件
- **`_capture_counts_from_finders(finders)`**:跨 finder 正規化(casefold+strip)、finder 內去重、數每個 distinct key 被幾個 finder 找到、降序回傳。純函式。
- **`lumos loop capture-counts --finder ... [--from-pitfalls <range> --repo <root>]`**:算 capture_counts + Chao1 殘餘估計 + 吐可貼的 `canary record --capture-counts` 串。`--from-pitfalls` 自動跑 `pitfalls --diff`、按 `source` 分組成確定性 finder(免手貼)。vault-free 純機械原語。
- **`_pitfall_diff_collect`**:從 `_pitfall_diff_mode` 抽出的純計算(不印),供「印」與「收割」共用;pitfalls diff/lint JSON 逐鍵不變。

## 一輪怎麼跑(編排者視角)
1. 派 W 個乾淨 LLM reviewer(panel_width 由 tier 決定,見 [[risk-tiered-review]]),各回 findings。
2. 把每個 reviewer 的 findings 正規化成 `file:line` → 一個 `--finder`。
3. `lumos loop capture-counts --finder "<A>" --finder "<B>" --from-pitfalls <base>..HEAD --repo .` → 自動併入 linter/regex 確定性 finder、算重疊。
4. 拿輸出的 `--capture-counts <串>` → `lumos canary record caught --loop code-<topic> --round rN --capture-counts <串> ...`。
5. `lumos loop status code-<topic> --gate --panel` → capture-recapture 殘餘 <1.0 + 輪有效 + 存活 max≤minor 三條合取才 PASS。

## 誠實邊界
- 機械化只買「重疊算術正確」,不買「finding 本身正確」——finding 真偽仍靠 reviewer + 辯方可執行反證。
- capture-recapture 小樣本會出極端值,當一個收斂信號、非 oracle。
- 端到端無人跑(自動派 reviewer + linter + 判收斂)屬自主 orchestrator,暫停中(2026-07-07);目前是**手動路徑一鍵化**。
