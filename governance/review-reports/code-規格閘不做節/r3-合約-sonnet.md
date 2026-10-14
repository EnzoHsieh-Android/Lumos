severity: major

我讀了 snapshot 與 repair 兩份 patch,在 `spec-gate-nondo` 的 `scripts/lumos`(d95e45a9)上實跑 `_nogo_line_says_nogo` 與 `_nogo_skip_lines` 驗證。`_NG_PRE_SHA` 我用基底提交 e0da694b 的舊程式重算,結果相符,所以 S9 第③點是真的。

severity: major
blocking: 是 — 風險高的計劃可被判成風險低,繞過設計審,而計劃宣稱的「每一句都要以否定片語開頭」沒擋住這型。
引句:「每個非空子句都要以否定片語(`_NOGO_NEG_PREFIX_RE`」
問題:切子句的 `_NOGO_CLAUSE_SPLIT_RE` 只切標點和少數轉折詞,不切「、」「且」「改用」「然後」「—」「/」。「不做」後面接這些連接方式的要做事項,會被當成同一句否定,整行跳過。計劃正文與 `Systems/規格閘.md` 都寫成「任何一句不是否定開頭就整行照掃」,實際沒做到。測試的 high 清單只列了有切點的寫法(「但」「and」「同時」),所以沒抓到。
具體失敗情境:實跑結果,下列行 `_nogo_line_says_nogo` 全回 True(被跳過),其中的扣款不算進風險,計劃可判成風險低而不派設計審:
- `- 不做退款、改接 Stripe 扣款`
- `- 不做退款且實作扣款`
- `- 不做退款改用扣款`
- `- 不做退款 — 扣款`
- `- 不做退款/直接扣款`
同一類的還有只靠開頭前綴就放行的 `- 排除退款以外的扣款`、`- 不含稅金額扣款`。相對地,`- 不做退款。扣款` 和 `- 不做退款,本版會扣款` 會照掃。
這是 r2 修的「前綴可被藉口放行」的同一族,只是換了連接詞。
佐證:file: `scripts/lumos:7928`(`_NOGO_CLAUSE_SPLIT_RE`)、`scripts/lumos:7995`(`_nogo_line_says_nogo`)、`scripts/test_lumos.py`(`t_spec_gate_nogo_item_needs_negation` 的 high 清單)。

severity: major
blocking: 是 — 計劃的 [S6] 條款說的行為,綁定的測試沒有驗,條款與測試對不上。
引句:「或把 `_nogo_skip_lines` 換成另一個函式時(在同一個程序裡換再算),門判定規則的輸入指紋應跟著變」
問題:r1 之後,指紋只收 `_NOGO_SKIP_LOGIC_VERSION` 這個數字,不收函式本身。`_door_rule_fingerprint` 執行時不讀 `_nogo_skip_lines`,換掉它指紋不會變。`t_door_rule_fingerprint_covers_nogo` 只換六支正則與版本常數,沒有換函式的一段,也沒有「斷言真的換到了」的對應檢查。條款文字沒跟著改成「版本號」。函式本體由另一支 `t_nogo_skip_logic_version_pin` 用原始碼雜湊守,它綁在〈做法〉4,沒綁任何 [S] 條款。結果是 [S6] 的字面行為既不成立也沒被測。
具體失敗情境:有人把 `_nogo_skip_lines` 整個換掉,按條款字面期待指紋會變,實際不變。能擋住的只有雜湊釘值那支測試,而它沒在 [S6] 的 [test:] 裡。
佐證:計劃 [S6] 行(snapshot 第 74 行),`scripts/test_lumos.py` 的 `t_door_rule_fingerprint_covers_nogo`。

severity: minor
blocking: 否 — 只是說明與文件措辭不準,判斷行為本身不受影響。
引句:「另跳過 `## 不做` 節的清單項目,見 [[Projects/規格閘不把不做節的詞算進風險_計劃]]」
問題:`雙向門放行_計劃.md` 兩處(關鍵字表命中那段、〈落地紀錄〉的規則版本)寫成「跳過 `## 不做` 節的清單項目」。實際只跳過「每一句都以否定片語開頭的行」。`Systems/規格閘.md` 寫對了,兩篇口徑不一致。
具體失敗情境:讀雙向門那篇的人以為不做清單整段都不掃,會在清單裡寫「做扣款」還以為沒事。
佐證:file: `docs/lumos-toolchain-knowledge/Projects/雙向門放行_計劃.md`(patch 內 +2026-10-14 起那兩行)。

severity: minor
blocking: 否 — 只影響註解可信度。
引句:「把 _NOGO_H2_RE / _NOGO_ITEM_RE / _NOGO_NEG_RE 換掉」
問題:`t_door_rule_fingerprint_covers_nogo` 的 docstring 還寫舊名 `_NOGO_NEG_RE`,這個常數已不存在,改成了 `_NOGO_NEG_PREFIX_RE`、`_NOGO_NEG_HEADER_RE`、`_NOGO_CLAUSE_SPLIT_RE`、`_NOGO_REF_TOKEN_RE`。
具體失敗情境:有人照 docstring 去找 `_NOGO_NEG_RE`,找不到,不知道實際換了哪幾支。
佐證:file: `scripts/test_lumos.py`(該測試 docstring)。

沒發現問題的部分:
- 版本號 `_DOOR_RULE_VERSION`=2、指紋釘值與 doctor 篩選(只數現行版本)互相一致。
- 停止條件(各種標題、`<!--`/`-->`、空行後散文)實跑與測試相符。
- `Systems/規格閘.md` 對 `pitfalls --check` 仍掃不做節的說明與計劃一致。

最高等級 major,blocking 共 2 條。
