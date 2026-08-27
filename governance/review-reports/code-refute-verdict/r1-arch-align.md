# r1 架構對齊席（claude/sonnet）
severity: major

FINDING 1 — major（引入第二種做法：兩姊妹欄同一 edge case 行為不一致）
file:line: scripts/lumos:3972（新增前置 guard）對比 scripts/lumos:4014（finding-kind 慣例）
引句: `if any(x is not None for x in (fo_set, ac_set, accept_reasons, refute_verdicts)) and f_set is None:`
--refute-verdict 進了「缺 findings-set 就 rc2」的守衛，但樣板 --finding-kind 沒進（它在 if f_set is not None 內，缺 findings-set 時整塊被跳過＝靜默丟棄）。兩個平行選配欄對同一情境一個報錯一個靜默丟＝第二種做法。
修法: 把 finding_kinds 也加進 3972 的 tuple（順帶修 finding-kind 的靜默丟失）。

對齊點2（子集 <=F vs 全集 !=F）: 站得住——辯方只審部分發現，子集判準正確；disposal gate（11010-11035）只讀 findings_set/folded_set/accepted_set，不讀 refute_verdicts，子集不接觸全集對帳，無連帶不一致。
對齊點3（有無更該用的既有原語）: 無偏離——folded_set 無法區分 agree/concern，evidence 內容與 accept_reasons 只在 accepted 那批重疊、cover 不到 folded 的 agree/concern，新增獨立欄捕捉嚴格更多資訊，非冗餘。
六處對稱性逐處核對: 全部忠實對稱。唯一偏離＝多接且只接一半的第七處（FINDING 1）。
