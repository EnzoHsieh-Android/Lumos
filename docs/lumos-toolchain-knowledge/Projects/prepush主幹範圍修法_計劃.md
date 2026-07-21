---
type: project
status: doing
created: 2026-07-21
updated: 2026-07-21
tags:
  - type/project
  - status/doing
related:
  - "[[Issues/code-loop守衛main-direct盲區]]"
  - "[[Systems/pitfalls-code-loop]]"
  - "[[Projects/loop機械脊椎M1包_計劃]]"
summary: |-
  FLAG:DECISION
  KEY:問題=pre-push 的 tier/code-loop 守衛以 merge-base(HEAD,main) 算 diff——main-direct 時 mb==HEAD,整段檢查(pitfalls tier/棧檢核/test-layers/code-loop check)直接跳過;code-loop check(scripts/lumos:9464-9477)同病回「無 branch diff→standard」。實證=[[Issues/code-loop守衛main-direct盲區]]:M1包 gate code 判 high 卻放行,事後補審三輪才還帳
  KEY:方案裁定=①機械修(本計劃):pre-push hook 改讀 **stdin 推送範圍**(githooks(5) 標準合約:每行 `<local_ref> <local_sha> <remote_ref> <remote_sha>`,範圍=remote_sha..local_sha)——push 什麼就檢什麼,分支與 main-direct 同軌;+②家規 advisory 一行(gate 類 code 建議 feature branch,落 lumos-code-loop skill 非 CLAUDE.md——避免動紀律區塊觸發 Check D 模板同步面)。③並行=①+②即是
  KEY:hook 改動——**stdin 必須最先讀**(讀進陣列再跑測試段,防後續指令吃掉 stdin);逐推送 ref 檢:刪除 ref(local_sha 全零)跳過;新 ref(remote_sha 全零)→fallback merge-base(main|master),再無→fail-open 放行+advisory 印一句(寧漏勿誤擋,沿現行精神);**任一 ref 的範圍判 high 即 high**;pitfalls/棧檢核/test-layers/code-loop check 全部改吃推送範圍
  KEY:code-loop check 改動——加選配 `--range <a..b>`:給了則跳過 merge-base 推導、直接以該範圍算 tier(scripts/lumos:9464 段);不給=現行為不變(向後相容);pass/skip 留痕比對邏輯不動(仍對 HEAD)
  KEY:★風險面★self-governance=high(動 pre-push 守衛本身)——spec 過 design-loop 非 light([[Issues/code-loop守衛main-direct盲區]] 排程時明裁);實作後本 hook 改動自己就會被新邏輯檢到(自舉驗證:改完 push 時新範圍演算法應對本 diff 判 high→要求 code-loop)
  TEST:見 body 測試策略——--range CLI 格數/新舊行為相容/hook 以臨時 git repo+假 stdin 模擬(main-direct push 範圍命中/新 ref fallback/刪除 ref 跳過/stdin 先讀不被測試段吃)
  DEP:scripts/hooks/pre-push｜scripts/lumos code-loop check(:9451-9479)｜[[Systems/pitfalls-code-loop]]
  PRIOR-ART:①最小解=hook 讀 stdin 是 git 原生合約,零新機制;code-loop check 加一選配旗標 ②世界解=githooks(5) 官方文件明定 pre-push stdin 格式,業界 hook(husky/lefthook)皆此模式——標準做法非發明 ③裁定=borrow(git 官方合約原生用)
---
# prepush主幹範圍修法_計劃

> **狀態**：spec 完成，待 design-loop（self-governance=high）。緣起：[[Issues/code-loop守衛main-direct盲區]]（M1 包 gate code 判 high 卻從門下鑽過，事後補審三輪還帳——事前擋的價值實證）。

## 問題

`scripts/hooks/pre-push` 的代碼風險段以 `git merge-base HEAD main` 起算 diff：main-direct 時 mb==HEAD，`[[ -n "$mb" && "$mb" != "$head_sha" ]]` 為假 → **pitfalls tier／棧別檢核／test-layers／code-loop check 四件全部靜默跳過**。`lumos code-loop check`（scripts/lumos:9464-9477）同病：merge-base==HEAD → 回「無 branch diff」tier=standard → OK。

## 規格

### #1 hook 改讀 stdin 推送範圍（githooks(5) 標準合約）

- **stdin 最先讀**：hook 開頭（anchor verify 之前）把 stdin 逐行讀進陣列——防止後續任何指令（測試段等）繼承並吃掉 stdin。每行格式 `<local_ref> <local_sha> <remote_ref> <remote_sha>`。
- **逐 ref 推導檢查範圍**：
  - `local_sha` 全零（刪除遠端 ref）→ 跳過該行。
  - `remote_sha` 全零（新 ref，遠端無基準）→ fallback `git merge-base <local_sha> main|master`；再無 → **fail-open 放行**並印一句 advisory（「新 ref 無基準,風險檢跳過」——沿現行「寧漏勿誤擋」精神）。
  - 一般情形 → 範圍 = `<remote_sha>..<local_sha>`。
- **聚合**：對每個有效範圍跑 `pitfalls --diff <range> --no-lint --json`；**任一範圍 tier=high 即整體 high**（走 code-loop check 硬擋分支，`--range` 傳該範圍）；standard＋棧命中 → advisory 照現行；test-layers 逐範圍 advisory。
- **無 stdin 行**（無實際推送）→ 跳過代碼風險段（其餘 anchor/測試/doctor 照舊）。
- 原 merge-base 推導整段移除（被 stdin 範圍取代——分支 push 時 remote_sha..local_sha 天然等價於原意圖且更準：只檢真正要推的東西）。

### #2 `lumos code-loop check --range <a..b>`（選配）

- 給了 `--range` → 跳過 merge-base 推導（:9464 段），直接以該範圍跑 pitfalls 算 tier。
- 不給 → 現行為分毫不變（向後相容；其他呼叫點不受影響）。
- `--range` 格式非 `<sha>..<sha>`／git 解不開 → 沿現行 fail-open 慣例（unknown tier、不 blocked）＋stderr 一句。
- pass/skip 留痕比對（對 HEAD 的 sha 檢查）不動。

### #3 家規 advisory（純散文，一行）

`lumos-code-loop` skill〈何時用〉補：「gate/守衛類 code **建議** feature branch 開發（pre-push 對 branch 與 main-direct 現已同軌檢查，此為縱深建議非機械強制）」。不動 CLAUDE.md 紀律區塊（避免觸發 Check D 模板同步面——範圍刀）。

## 明確不做（範圍刀）

- 不做 push 範圍的 doctor/測試段範圍化（那兩段本來就是全量語意，與範圍無關）。
- 不動 pass/skip 留痕的 sha 語意。
- 不做 CLAUDE.md 紀律區塊改動。
- 不做 force-push/rewrite 特判（remote_sha..local_sha 對 force push 天然給出新舊差集之外的東西——git 語意如此，誠實記載於隱患）。

## 測試策略

1. `code-loop check --range`：合法範圍算 tier（造含 .py 變更的範圍→tier 判定跑通）／不給 --range 現行為不變（既有測試不紅）／壞格式 fail-open 不 blocked。
2. hook 模擬（臨時 git repo＋餵假 stdin）：main-direct push（remote..local 含 code 檔）→ 風險段執行（輸出含 pitfalls 標記）／新 ref（remote 全零＋無 main）→ fail-open 放行＋advisory 句／刪除 ref 行→跳過／stdin 先讀：hook 後段有讀 stdin 的指令時範圍仍正確。
3. 迴歸：分支 push 情境（有 merge-base 的一般 push）新舊範圍等價案例。

## 實務隱患

- **自舉面（最重）**：本改動自己就是 gate 類 code——落地 push 時，新範圍演算法應對本 diff 判 high 並要求 code-loop（自己驗自己；若沒觸發＝新邏輯有洞的即時訊號）。
- **fail-open 面**：新 ref 無基準時放行——與現行精神一致，但攻擊面誠實記載：故意用新 branch 首推繞檢。縱深＝家規 advisory＋CI。
- **force-push 語意**：remote_sha..local_sha 對 rewrite 歷史只涵蓋新側——git 原生語意，不特判，記載即可。
- **stdin 消費順序**：bash 中若測試段先跑會吃掉 stdin——spec 明定最先讀；測試 2 有專門格。
