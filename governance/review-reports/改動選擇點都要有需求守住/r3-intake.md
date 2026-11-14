# r3 收貨紀錄(改動選擇點都要有需求守住,上限輪)

六席(正確性、邊界、整合、資源、通才、架構對齊;皆 sonnet)全到後才一次從逐字稿存進卷證;收貨前沒動被審材料。quote-check 六席全錨。共 54 條(c 6、b 10、i 12、z 10、t 12、a 4),blocking 25。使用者 2026-11-14 收貨期間授權無人值守(「遇事不決看論文、上網搜最佳解」),判讀一律先查論文原文。

## 分組(依根因)

| 組 | 根因 | 發現 | 最高 | 處置 |
|---|---|---|---|---|
| J1 | 選擇點以「節點起始行」判,左遞迴的鏈式呼叫與跨行運算起點在上一行 | c1、t1、b2、t2、t9 | major | 折:每列加錨點(運算子、方法名、運算元、陳述起始)所在行;API 只替換方法名;同欄外層優先排序;面試題做成自動測試 S25 |
| J2 | 有效處置與種子用 line_sha,同檔同文字不同上下文的行互相遮蔽、rebase 改行號讓種子變 | c2、t3、b4、z3、i3、c5 | major | 折:改用行指紋(那一行與前後各 2 行);種子只用行指紋集合 |
| J3 | 一行一個壞法的迴圈與唯一性矛盾 | c3、i2、b6 | major | 折:寫成明確迴圈(類別→節點→候選,排除就換下一個);唯一性只在身分段 |
| J4 | 公式 1 複合節點遞迴在 ast-grep 做不出來、旗標列與預期值表衝突 | b1、i1、t5、z10 | major | 折:照論文精神但承認做不到遞迴,乾範圍就是命中節點;旗標只乾引用本身與條件恰為旗標的 if;差異⑦與天花板 2 寫明 |
| J5 | cmd_guard_kill 迴圈內拿不到 weak、中斷沒有檢查點 | c4、z5、z6、i8 | major | 折:on_row 列每條配方結束時蓋好可知的 weak、flaky 標未定;加 should_stop;中斷用 defer 模式在配方之間停 |
| J6 | 沒裝 ast-grep 就擋,跟規格閘放行先例、豁免與回退矛盾 | b3、i4 | major | 折:先判不需要 ast-grep 的條件;沒裝算不出來、只提醒記 unverified |
| J7 | 成本沒上限、max-mutants 餓死沒跑過的行 | z1、z2 | major | 折:stop_group_on 含編不過與逾時、--max-seconds、沒跑過的優先、survived 只在守的測試變了才重跑 |
| J8 | 讀帳時限與逾時語意、大檔整批失敗 | z4、i12 | major | 折:讀帳另給時限、時限用完算不出來、git 回錯才擋;先篩大檔;只讀有增行的檔;bad 在 light 之前併入 |
| J9 | 推送範圍起點 | i5 | major | 折:用單一來源 _push_range_start |
| J10 | 乾節點規則與論文條件不符 | b5、b7、b8、c6、z9 | major | 折:提早回傳限空容器(A.1.22)、整個 delay 呼叫乾(A.1.4)、null 比較乾(A.1.10)、=== 只換 !==、log 認呼叫鏈根接收者、size == 0 也乾 |
| J11 | 架構對齊:兩套掃描、另開放行路徑 | a1、a2 | major | a2 折:放行改用既有 lint-waive(choice: 前綴、放行檔、origin、AI 放行要 ack);a1 折:兩套掃描並存的理由與 REVISIT 2027-03-15 寫進範圍 6 |
| J12 | ast-grep 呼叫的安全與細節 | i6、t7、b9、z7 | minor | 折:沿用 _lint_wt_allow 的設定路徑限制與旗標黑名單、_lint_wt_begin/_reap、TemporaryDirectory、一次掃整個暫存目錄、rc 0/1、byteOffset、0 起算換算、ERROR 節點略過 |
| J13 | 其他:point 冪等讀帳、差異清單、帳量、SBR 細節、加括號、RETIRE-IF 分母、CI 不接 | i7、i10、i11、z8、t6、t8、t10、t12、i9 | minor | 折 |
| — | 放行 | t11、a3、a4、b10 | minor | 放行:t11 繞法都在已承認的威脅模型與天花板內;a3 兩張表的理由已寫;a4 rc 3 語意照新增告警那道(手冊有寫);b10 定位與理由的輸入邊界屬單人威脅模型,實字沿用 `_real_chars` |

## 先查世界

- J1 PRIOR-ART:tree-sitter-kotlin grammar.js 的 call_expression、navigation_expression 是左遞迴(https://github.com/fwcd/tree-sitter-kotlin);論文 2.2 的 point mutation 以 (file, line) 請求、產生在那一行的節點(https://arxiv.org/pdf/2102.11378)——錨點行即「那一行」。
- J2 PRIOR-ART:論文 3.2.4 要每次快照穩定回報同一批壞法(https://arxiv.org/pdf/2102.11378);行指紋不含行號,rebase 不變。
- J4 PRIOR-ART:論文 3.1 公式 1;ast-grep 規則的 `matches` 互相引用會被判循環(r3 邊界席查證);方向:對 — 語法樹方向不變,只承認遞迴這一點做不到(https://arxiv.org/pdf/2102.11378、https://ast-grep.github.io/guide/rule-config/utility-rule.html)。
- J10 PRIOR-ART:論文附錄 A.1.4(SleepFor 整句)、A.1.10(null 比較)、A.1.22(回傳空容器)、A.1.23(=== 只換 !==)原文(PDF 第 15–19 頁)。
- J6 PRIOR-ART:規格閘既有「算不出來就放行」、新增告警閘「工具沒裝自動放行並記帳」(repo 內先例)。
- J11 PRIOR-ART:既有放行機制 lint-waive 與放行檔(repo 內先例,`_lint_waivers_add`)。
- 其餘:內部接線。

## 重現

| id | 重現 | 結果 |
|---|---|---|
| c1、t1、b2 | 讀 grammar.js 第 1204、1218 行:`seq($._expression, $.call_suffix)`、`seq($._expression, $.navigation_suffix)` | HIT |
| c4、z6、i8 | 讀 cmd_guard_kill:weak 在迴圈後蓋章 | HIT |
| b3、i4 | 讀快照:S6 擋、S21 不要求、舊否決比對寫算不出來放行 | HIT |
| b5 | 讀論文 PDF 第 19 頁 A.1.22:觸發條件是回傳空容器 | HIT |
| a2 | 讀 scripts/lumos 的 _lint_waivers_add:放行檔帶 origin 與 acked | HIT |
