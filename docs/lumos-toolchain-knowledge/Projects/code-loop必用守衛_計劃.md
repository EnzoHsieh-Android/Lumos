---
type: project
status: done
created: 2026-07-05
updated: 2026-07-05
tags:
  - type/project
  - status/doing
related:
  - "[[pitfalls-code-loop]]"
  - "[[主動影響幅度偵測_計劃]]"
  - "[[anchor-integrity]]"
summary: |-
  FLAG:DECISION
  KEY:收 code-loop「靠記得調用」破口——pitfalls tier=high 目前只 pre-push advisory、靠 Claude 記得跑 code-loop。補「訊號→必須使用」:Stop hook 注入 nag(不會忘)+ pre-push 升 blocking(做完那點硬擋)+ skip-marker 顯式逃生留痕
  KEY:判定式(三處共用)=tier=high(pitfalls --diff)AND 無有效 code-loop 收斂紀錄 AND 無 skip-marker → 該擋/nag
  KEY:Stop hook 只注入不擋(Stop 分不出做完/中途,擋會每回合卡死);pre-push 才硬擋(well-defined 做完點)
  KEY:收斂綁 HEAD sha 防過時(收斂是對某 diff 狀態、非永久通行證;HEAD 移動+新 high→作廢重跑,同 anchor);skip-marker 也綁 HEAD
  DECISION:硬度=Stop 注入 nag + pre-push 升 blocking + skip-marker(顯式繞+留痕,同 bypass-log);--no-verify 仍 git-native 繞得過(使用者自負)
  DECISION:直接 writing-plans+TDD(hook+gate glue+一條 staleness 規則,無深演算法,design-loop 對 glue 空轉)
  KEY:誠實天花板=非 oracle——關掉「忘了」(Stop push)+「隨手漏」(pre-push 擋),關不掉「刻意繞+不誠實」;同 design-loop/impact「push+摩擦+地板非 oracle」
  DEP:[[pitfalls-code-loop]]
  TEST:待實作
verified_by:
  - "[[Verification/2026-07-05_code-loop必用守衛]]"
decisions:
  - content: 撤除 Stop hook 每回合 code-loop nag,強制改由 pre-push git hook 單點把關
    context: 每回合 Stop 注入 nag(tier=high 未過 code-loop)實際使用太擾民,連續刷屏;pre-push 本就在 push 時 blocking 擋,Stop nag 只是提前提醒、非必要
    why_chosen: push 才是真正需要把關的時點;移除 Stop nag 保留 pre-push 強制,安靜且不失守
    decided: 2026-07-06
    valid: true
---
# code-loop 必用守衛_計劃

> 收「看到訊號還要記得調用 code-loop」的破口(使用者點出)。借鏡 [[主動影響幅度偵測_計劃]] 的 push 注入。**不是新 review 機制,是給既有 code-loop 加「必用」守衛**。

## 背景:破口
`pitfalls --diff` tier=high 目前只在 **pre-push advisory 提醒**(stderr、不擋),真的跑 `lumos-code-loop` **靠 Claude 記得調用**。「忘了看/忘了跑」是破口(pull 非 push)。**lumos 不能 spawn agent → 不能自動跑 code-loop**,最多做到「把訊號推到眼前 + 做完點硬擋」。

## §1 架構(三守衛點,共用判定式)
**判定式**:`tier=high(pitfalls --diff --no-lint)` AND `無有效 code-loop 收斂紀錄` AND `無 skip-marker` → 成立(該擋/nag)。
- **Stop hook**(Claude Code,每回合末):成立 → **注入 nag**(additionalContext:「本分支 tier=high 代碼未過 code-loop;push 前必須跑 `lumos-code-loop` 或 `lumos code-loop skip`」)。**不擋回合**——Stop 分不出「做完」vs「中途」,擋會開發中每回合卡死。
- **pre-push hook**(git,做完那點):成立 → **rc1 擋 push**(從現有 advisory 升級)。
- 共用:三處都跑 `pitfalls --diff <merge-base>..HEAD --no-lint --json` 取 tier。

## §2 收斂紀錄 + staleness(關鍵正確性)
- code-loop 用既有 canary/loop 原語,**loop-id = `codeloop/<branch>`**。跑完 `lumos loop status <id> --gate` exit 0 = 收斂。
- **綁 HEAD sha 防過時**:收斂紀錄存**當時 HEAD sha**;判定時比對當前 HEAD——不符(之後又 commit 新 tier=high 代碼)→ **舊收斂作廢、要重跑**。收斂是對「某個 diff 狀態」,非永久通行證(同 [[anchor-integrity]]「收斂of什麼」)。

## §3 skip-marker(顯式逃生 + 留痕)
- `lumos code-loop skip --note "<理由>"` → 寫 marker(branch + HEAD sha + 理由 + ts → 治理帳,同 bypass-log 哲學)。判定時當前 HEAD 有 marker → 放行。
- **綁 HEAD**:skip 對特定 HEAD;新代碼進來 marker 失效(不能一次 skip 永久放水)。
- 「明擋、可顯式繞、留痕」——比 `--no-verify`(無痕)正派。`--no-verify` 仍 git-native 繞得過(沒有 git 閘擋得住它),使用者自負。

## §4 誠實天花板
- **非 oracle**:Stop 注入可被 Claude 無視;pre-push 可 --no-verify。**能關的**:「忘了看」(Stop push 到眼前)、「隨手漏」(pre-push 硬擋)。**關不掉**:「刻意繞 + 不誠實」——lumos 不能替你跑 agent、git 不防 --no-verify。同 design-loop/impact:**push + 摩擦 + 地板,非 oracle**。
- **tier=high 假陽** → skip-marker 是逃生閥(不卡死、且留痕可審)。

## §5 測試(TDD)
- **判定式單元**:tier=high∧無收斂∧無skip→成立(擋);有收斂(HEAD 相符)→放;收斂但 HEAD 移動+新 high→作廢再擋;有 skip-marker(HEAD 相符)→放;tier≠high→不成立(不誤傷)。
- **Stop hook**:成立注入 nag、否則靜默;additionalContext 格式(含跑法/skip 法)。
- **pre-push**:成立 rc1 擋、否則放;訊息含跑法/skip 法。
- **`lumos code-loop skip`**:寫 marker(branch+HEAD+note)+留痕;綁 HEAD(HEAD 移動失效)。
- **回歸**:tier≠high 分支 Stop 不 nag、pre-push 不擋。

## 落地後回指
Verification `plan_refs` 回指本節點;本節點 TEST/status;更新 lumos-project-notes/CLAUDE.md 使用指南(Stop hook nag + pre-push code-loop 硬擋 + `code-loop skip` 指令);design-loop/code-loop skill 若需提及收斂紀錄綁 HEAD。
