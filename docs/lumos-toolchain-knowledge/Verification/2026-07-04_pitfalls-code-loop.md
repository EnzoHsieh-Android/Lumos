---
type: verification
status: pass
created: 2026-07-04
updated: 2026-07-04
tags:
  - type/verification
  - status/pass
related:
  - "[[Systems/pitfalls-code-loop]]"
valid_under: cmd_pitfalls 三模式(PITFALL_CLASSES 詞表+剝除對齊 assess_spec 含防呆+--check 節檢查+--diff pattern/@@ 行號推導/形態類軸/過濾繼承 Check H);cmd_loop_status --gate 的 --spec 可選(G1 skip);lumos-code-loop skill 對抗紀律;接線四檔
revalidate_when: 改 PITFALL_CLASSES 詞表或黑名單(漂移守衛擋);改 _PITFALL_DIFF_PATTERNS;改 cmd_loop_status gate 段;改 code-loop skill 三道防污染;改 difficulty.RISK_CLASSES/_BLACKLIST(漂移守衛連動)
summary: |-
  TEST:t_pitfalls_spec 9 checks(通用3問/類追問/--check rc/剝除/md 不存在 rc2)+ t_pitfalls_diff 11 checks(命中/skip .md·測試檔/tier/形態軸/行號值 3與5/併發寫入 INSERT)+ TestPitfallsDrift 2(類名≡RISK_CLASSES、黑名單≡_BLACKLIST 非恆綠)+ t_loop_gate 案14翻契約(缺--spec→G1 skip rc0)+ t_loop_gate_no_spec(G1 skip 但 G2 擋);374 passed 0 failed 無回歸
  VERIFY:行號推導人工+機器雙驗;pattern 去重疊(SELECT/寫入)證第6條非死碼;三道防污染語意經 review 逐條確認;gate G2 段一字未動比對
---
# 2026-07-04 pitfalls-code-loop 驗證

`python3 scripts/test_lumos.py`:374 passed 0 failed(t_pitfalls_spec 9 + t_pitfalls_diff 11 + gate 案14/no-spec 新斷言,含行號值與併發寫入回歸釘)。
`python3 scripts/test_autonomous_loop.py`:全綠(TestPitfallsDrift 2 tests——類名/黑名單漂移即紅,經 review 確認非恆綠)。
審查攔下三個真缺陷:Task 2 pattern 遮蔽死碼(SELECT→效能/寫入→併發去重疊)+ 行號只驗 type(補值斷言)、Task 4 四型表格標示歧義(統一 (N−1) mod 4 對映)。gate G2 段經 review `git show` 逐段比對一字未動。
code-loop skill 對抗紀律 1:1 對映 design-loop,三道防污染語意逐條確認、CLI(loop status --gate 無 --spec)與落地一致。
