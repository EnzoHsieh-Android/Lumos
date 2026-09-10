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
  - scope/guards-gates
summary: |-
  FLAG:TECHNICAL
  KEY:★症狀★——code-loop pass 綁 HEAD sha 嚴格等值,但 pass 自己會往★tracked★的 docs/.governance-log.jsonl append 一行;照「先 commit 乾淨再 push」的普遍直覺把這行 commit 進去,HEAD 前進 → pass 立刻自失效 → 重記 pass 又產生新帳行 → 追尾循環,每圈重付全套 pre-push 閘(2026-08-04 design-loop 重設計終審放行實戰:追尾三圈才發現)。設計者預期順序「pass→先 push→後補 commit 帳」沒寫在任何地方
  KEY:★修法(2026-08-04)★——簿記白名單豁免(可重算):留痕 sha 之後的 commit ★只動簿記檔★(docs/.governance-log.jsonl/docs/.usage-log.jsonl/governance/anchor-baseline.json/governance/code-loop/)且留痕 sha 是目標 sha 的★祖先★(merge-base --is-ancestor;改寫史拒認)→ 留痕仍有效;任何其他檔一動照樣失效。「HEAD 移動→作廢」原意=pass 不得蓋到新★代碼★,豁免精化而非放寬 [test:t_codeloop_pass_survives_bookkeeping_commits]
  KEY:配套——pass/skip 成功訊息加一行順序提示(其後只准簿記檔 commit);與 [[Issues/code-loop守衛main-direct盲區]] 同屬「守衛機制正確、組合場景有洞」族
---
# code-loop-pass 自失效追尾

pass 留痕綁 HEAD sha 嚴格等值 × pass 自己的 tracked 副作用（治理帳一行）＝把留痕 commit 進去就自失效的追尾循環。詳見 summary；修法測試 `t_codeloop_pass_survives_bookkeeping_commits`（豁免翻紅釘＋兩枚收緊釘：code commit 不放行、改寫史拒認）。

發現脈絡：2026-08-04 design-loop 重設計終審豁免放行時實戰踩中，追尾三圈（每圈重付 anchor verify＋全套測試＋pitfalls 掃描）才定位。設計預期的「pass→先 push→後補 commit 帳」順序未見於任何文件——判定為設計縫隙而非誤用。

## 2026-09-08 新形態:共用主線上,兩個 session 互相把對方的留痕打掉

**症狀最難查的地方:本機閘全綠,只有 CI 紅。**

當天的兩段(兩段都不是閘壞掉):

1. **留痕住在一個要另外提交的檔裡。** `code-loop pass` 往 `docs/.governance-log.jsonl`
   append 一行,而我推的時候還沒提交那個檔——**本機看得到留痕、遠端看不到**,
   所以本機 `code-loop check` 放行、CI 判「tier=high 代碼無 code-loop 留痕」。
2. **補提交帳本之後又被擋**,訊息換成「留痕 sha 過時、非純簿記增量」。
   查出來是:**另一個 session 在我 pass 之後往同一條主線提交了 README、圖檔、文件**。
   簿記白名單只收帳本類的檔,那些不在名單裡,所以留痕對新的 HEAD 就失效。

### 同事點出的更根本角度(我採納)

★問題不只是「順序寫錯」,是留痕的錨點跟簿記的儲存位置互相打架。★
留痕綁「被推上去的那個 sha」,而留痕本身住在一個必須另外提交的檔裡
——**「提交留痕」這個動作本身就會改變 sha,它在追一個因為自己而移動的目標**。
簿記白名單豁免就是為了繞開這件事,方向是對的;但白名單一旦漏收一種檔,
症狀就是「本機全綠、CI 才紅」,而那是最難查的一型。

### 現在白名單漏了什麼(2026-09-08 查證,不是推測)

判準是 `f in _BOOKKEEPING_FILES or f.startswith(_BOOKKEEPING_DIR)`,
名單是九個完整路徑加一個目錄前綴 `governance/code-loop/`。所以:

- `governance/review-reports/**`(審查卷證)**不在名單內**。正常流程裡它們跟被審的碼
  同一筆提交、在 pass 之前,所以踩不到;順序一亂就會踩到。
- ★`governance/replay/<編號>/verdict.json` 也不在名單內,而它是 `loop replay --freeze`
  在 pass 與 push **之後**才產生的★——也就是說收工凍結判定這個動作,
  結構上就會讓剛剛那筆留痕對下一次推送失效。目前不痛是因為每一批都會重新 pass 一次。
  ★2026-09-10 起凍結判定挪到 pass 之前、併進功能那個提交★(見 [[Projects/提交推送規範_計劃]];凍結記的是檔案內容指紋
  不是提交編號,併進去不影響回放)——這條結構問題照新順序做就不會發生,推送後也不再多一個「凍結判定」提交。

### 可以立刻用的三條

1. **`code-loop pass` 之後要先提交治理帳,再推。** 順序反了就是「本機綠、CI 紅」。
2. **高風險那批推之前,先跟同工作區的人約一段沒有人提交的窗口。**
   共用主線上,對方任何一筆非簿記提交都會把你的留痕打掉。
3. **白名單的內容要跟「什麼算簿記」的定義同源**(同事的建議),不要各自維護
   ——否則下次有人加一種新的帳本檔或卷證目錄,同一顆雷會再炸一次。
   REVISIT:2026-12-08 若再踩到一次(或要動這段判定),把 `governance/replay/`
   與 `governance/review-reports/` 一起納入,並且改成從單一定義推出來。

