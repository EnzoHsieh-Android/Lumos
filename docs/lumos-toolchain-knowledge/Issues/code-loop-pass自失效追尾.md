---
type: issue
status: resolved
created: 2026-08-04
updated: 2026-08-04
related:
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Issues/code-loop守衛main-direct盲區]]"
  - "[[Projects/code-loop必用守衛_實作計畫]]"
tags:
  - type/issue
  - status/resolved
summary: |-
  FLAG:TECHNICAL
  KEY:★症狀★——code-loop pass 綁 HEAD sha 嚴格等值,但 pass 自己會往★tracked★的 docs/.governance-log.jsonl append 一行;照「先 commit 乾淨再 push」的普遍直覺把這行 commit 進去,HEAD 前進 → pass 立刻自失效 → 重記 pass 又產生新帳行 → 追尾循環,每圈重付全套 pre-push 閘(2026-08-04 design-loop 重設計終審放行實戰:追尾三圈才發現)。設計者預期順序「pass→先 push→後補 commit 帳」沒寫在任何地方
  KEY:★修法(2026-08-04)★——簿記白名單豁免(可重算):留痕 sha 之後的 commit ★只動簿記檔★(docs/.governance-log.jsonl/docs/.usage-log.jsonl/governance/anchor-baseline.json/governance/code-loop/)且留痕 sha 是目標 sha 的★祖先★(merge-base --is-ancestor;改寫史拒認)→ 留痕仍有效;任何其他檔一動照樣失效。「HEAD 移動→作廢」原意=pass 不得蓋到新★代碼★,豁免精化而非放寬 [test:t_codeloop_pass_survives_bookkeeping_commits]
  KEY:配套——pass/skip 成功訊息加一行順序提示(其後只准簿記檔 commit);與 [[Issues/code-loop守衛main-direct盲區]] 同屬「守衛機制正確、組合場景有洞」族
---
# code-loop-pass 自失效追尾

pass 留痕綁 HEAD sha 嚴格等值 × pass 自己的 tracked 副作用（治理帳一行）＝把留痕 commit 進去就自失效的追尾循環。詳見 summary；修法測試 `t_codeloop_pass_survives_bookkeeping_commits`（豁免翻紅釘＋兩枚收緊釘：code commit 不放行、改寫史拒認）。

發現脈絡：2026-08-04 design-loop 重設計終審豁免放行時實戰踩中，追尾三圈（每圈重付 anchor verify＋全套測試＋pitfalls 掃描）才定位。設計預期的「pass→先 push→後補 commit 帳」順序未見於任何文件——判定為設計縫隙而非誤用。
