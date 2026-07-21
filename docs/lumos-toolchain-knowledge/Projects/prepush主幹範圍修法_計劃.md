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
  KEY:code-loop check 改動——加選配 `--diff <a..b>`(r1 折入:名對齊全 CLI,原擬 --range 不一致)+`--at-sha`/`--branch`(r1 最重 major:留痕比對原讀 checkout HEAD,推非當前 checkout 分支時 tier 對 range 算、留痕卻查錯分支=誤放/誤擋;改由 hook 傳被推送 ref 座標);不給=現行為不變(向後相容)
  KEY:落地同步義務(r1 折入)——①anchor:scripts/hooks/pre-push 是錨點檔,改後落地 push 先卡自身 anchor verify→序含 `lumos anchor approve --note` ②既有 t_codeloop_guard_prepush(test_lumos.py:6494)餵 dummy sha,stdin 變 load-bearing 後失真→重寫真 sha ③Issue open→清償 ④code-loop必用守衛計畫「merge-base 同 pre-push」句失真同步 ⑤Verification
  KEY:★風險面★self-governance=high(動 pre-push 守衛本身)——spec 過 design-loop 非 light([[Issues/code-loop守衛main-direct盲區]] 排程時明裁);實作後本 hook 改動自己就會被新邏輯檢到(自舉驗證:改完 push 時新範圍演算法應對本 diff 判 high→要求 code-loop)
  TEST:見 body 測試策略——--diff CLI 格數/新舊相容/留痕座標(推非當前 checkout 分支查對 ref)/hook 假 stdin 模擬(main-direct/新 ref fallback/首推 main 空 diff/shallow 無物件/刪除 ref/空 stdin/多 ref 混合迴圈/stdin 先讀);既有 t_codeloop_guard_prepush 重寫(dummy sha→真 sha)
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
  - `remote_sha` 全零（新 ref，遠端無基準）→ fallback `git merge-base <local_sha> main|master`；**若 merge-base ∈ {無, local_sha 本身}（r1 s2-F1 折入：首推 main／main-tip 自比得空 diff＝重現盲區）→ fail-open 放行＋advisory**（「新 ref 無基準,風險檢跳過」——沿「寧漏勿誤擋」）。
  - **`remote_sha` 非全零但本地無此物件（r1 s3-F3 折入：shallow clone／歷史分岔）→ `git cat-file -e <remote_sha>` 探測失敗即比照「無基準」fail-open＋advisory**（原會裸範圍送 pitfalls 報錯靜默吞、且不印 advisory＝與新 ref 路徑不對稱）。
  - 一般情形 → 範圍 = `<remote_sha>..<local_sha>`。
- **聚合**：對每個有效範圍跑 `pitfalls --diff <range> --no-lint --json`；**逐 ref 獨立判——某 ref 判 high 即對「該 ref」走 code-loop check 硬擋（用其 --at-sha/--branch 座標，見 #2b）；非全域「整體 high」**（r1 修正：全域 high 會用一個 range 的判定套到別 ref 的留痕＝留痕脫鉤根源）。第一個 high ref 未過即擋、其餘 ref 可短路（成本＋明確性；r1 s3-F2 折入）。standard＋棧命中 → advisory；test-layers 逐範圍 advisory。多 ref push 常見於 `--all`/批次同步——逐 ref 迴圈變數每輪重置。
- **無 stdin 行**（無實際推送）→ 跳過代碼風險段（其餘 anchor/測試/doctor 照舊）。
- 原 merge-base 推導整段移除（被 stdin 範圍取代——分支 push 時 remote_sha..local_sha 天然等價於原意圖且更準：只檢真正要推的東西）。

### #2 `lumos code-loop check --diff <a..b> [--at-sha <sha>]`（選配；r1 折入：旗標改名＋留痕座標）

- **旗標名＝`--diff`（r1 s4-F3 折入，原 `--range` 與全 CLI 不一致）**：對齊 `pitfalls --diff`/`cochange --diff`/`test-layers --diff`/`impact --diff` 全用 `--diff <A..B>`。給了 → 跳過 merge-base 推導（:9464 段），直接以該範圍跑 pitfalls 算 tier。不給 → 現行為分毫不變（向後相容）。格式非 `<sha>..<sha>`／git 解不開 → 沿 fail-open（unknown tier、不 blocked）＋stderr 一句。
- **★留痕座標脫鉤（r1 最重 major，codex-finder＋s2＋s4 三席互證）★**：現行 `_codeloop_guard_verdict` 的 pass/skip 留痕比對讀「**當前 checkout** 的 branch/HEAD」（:9502-9517 `_codeloop_git_branch`/`_codeloop_git_head`）；但 hook 逐 ref 檢的是**被推送 ref 的 local_sha**（可非當前 checkout——`git push origin featB:featB`、`--all`、代人推）。tier 用 range 算對了，留痕卻查錯分支 → **誤放**（借不相干分支的有效 pass）或**誤擋**（已收斂分支查錯檔）。修法：`code-loop check` 加 `--at-sha <sha>`＋`--branch <name>`（由 hook 傳被推送 ref 的 local_sha 與 `local_ref` 末段），留痕比對改對這兩者，不再讀 checkout。不給則沿現行讀 checkout（向後相容）。

### #2b hook 逐 ref 傳留痕座標
hook 對每個有效範圍呼叫 `code-loop check --diff <range> --at-sha <local_sha> --branch <local_ref 末段>`——tier 與留痕同軌對齊「這一條 ref」。

### #3 家規 advisory（純散文，一行）

`lumos-code-loop` SKILL `## 一眼看懂` 的「**何時**:」條末補一句（r1 s4-F5 折入落點精確化）：「gate/守衛類 code **建議** feature branch（pre-push 對 branch 與 main-direct 現已同軌檢查，此為縱深建議非機械強制）」。不動 CLAUDE.md 紀律區塊（避免觸發紀律區塊漂移守衛 Check D 的模板同步面——範圍刀）。

## 落地同步義務（r1 s4-F1/F6 折入，同一 commit）

1. **anchor baseline（最重）**：`scripts/hooks/pre-push` 是錨點檔（`governance/anchor-baseline.json`＋`ANCHOR_FILES`）——改 hook 後 sha 變，落地 push 自己會先卡在 hook 內的 `anchor verify`（:29）。落地序：改完 → `lumos anchor approve --note "prepush 範圍修法落地"` → 再 push（否則進不到新 tier 邏輯）。
2. **既有測試重寫**：`t_codeloop_guard_prepush`（test_lumos.py:6494 起）餵的 stdin 是字面 `dummy` sha——現行不讀 stdin 故無妨，但 stdin 變 load-bearing 後 `dummy..dummy` 會讓 pitfalls 報錯靜默 fail-open、既有斷言失真。改餵真 sha（`git rev-parse HEAD`/`main`）。
3. `Issues/code-loop守衛main-direct盲區` status open→改（修法落地即清償主軸）。
4. `Projects/code-loop必用守衛_實作計畫`「merge-base 取法同 pre-push」句落地後失真——同步。
5. Verification 節點（plan_refs 回指）。

## 明確不做（範圍刀）

- 不做 push 範圍的 doctor/測試段範圍化（那兩段本來就是全量語意，與範圍無關）。
- 不動 pass/skip 留痕的 sha 語意。
- 不做 CLAUDE.md 紀律區塊改動。
- 不做 force-push/rewrite 特判（remote_sha..local_sha 對 force push 天然給出新舊差集之外的東西——git 語意如此，誠實記載於隱患）。

## 測試策略

1. `code-loop check --diff`：合法範圍算 tier（造含 .py 變更的範圍→tier 判定跑通）／不給 --diff 現行為不變（既有測試不紅）／壞格式 fail-open 不 blocked／`--at-sha`/`--branch` 使留痕查指定座標非 checkout。
2. hook 模擬（臨時 git repo＋餵假 stdin，沿 `t_codeloop_guard_prepush` 既有 subprocess＋input 模式）：main-direct push→風險段執行／新 ref＋main→fallback／新 ref＋無 main→fail-open＋advisory／**首推 main（mb==local_sha）→fail-open＋advisory（r1）**／**remote_sha 非全零但本地無此物件→fail-open＋advisory（r1）**／刪除 ref→跳過／空 stdin→風險段跳過其餘照舊／**多 ref 混合單次 push（一刪＋一推＋一新）→逐 ref 迴圈各自處理（r1 s3-F4，核心迴圈正確性）**／stdin 先讀不被後段吃。
3. **留痕座標（r1 最重）**：checkout 在 main、push featB→`--at-sha`/`--branch` 使留痕查 featB 非 main（誤放/誤擋雙向案例）。
4. 迴歸：一般分支 push 新舊範圍等價；`t_codeloop_guard_prepush` 重寫後仍綠。

## 審計修正紀錄

**pre-flight（2026-07-21）**：1 命中——新 ref fallback 分岔缺測試項＋空 stdin 跳過缺測試項，補測試策略。

**r1（2026-07-21，high panel W=4 sonnet 異鏡頭＋Codex 帶餌 finder＋無餌否決席）**：canary s2/s3/s4 caught、**s1 missed（summary↔body「空 stdin 提前 exit0 vs 只跳風險段」矛盾未抓，通才席漏鏡像面）→ 輪無效**；s1 findings 剔除（其主 finding＝留痕脫鉤已由 codex-finder＋s2＋s4 獨立三席互證浮回，無損）。canary token（--push-base/PUSH_RANGE_MAX/hook-sync.log）溯源排除不折。真 findings 折入 v2：
- **★留痕座標脫鉤（major，三席互證，本輪最重）★**：pass/skip 留痕讀 checkout HEAD、tier 讀被推送 range——非當前 checkout 分支 push 時借錯分支留痕誤放/誤擋 → `--at-sha`/`--branch` 由 hook 傳；聚合改逐 ref 獨立判非全域 high。
- **首推 main mb==local_sha 空 diff（major，s2）**：重現盲區 → 併入 fail-open+advisory。
- **shallow/remote_sha 本地無物件（major，s3）**：cat-file -e 探測 → fail-open+advisory（原不對稱靜默）。
- **既有 t_codeloop_guard_prepush 崩（major，s3）**：dummy sha 在 stdin load-bearing 後失真 → 重寫真 sha，列同步義務。
- **anchor baseline 落地卡關（major，s4）**：改 hook 先卡自身 anchor verify → 落地序含 anchor approve，列同步義務。
- **聚合成本/多 ref 迴圈無測試（s3）**：短路＋逐 ref 迴圈重置＋多 ref 混合測試格。
- **自舉驗證因果不成立（minor，codex-finder）**：glob claim 保底 high 與新邏輯對錯無關 → 誠實改。
- **--diff 命名/advisory 落點/同步清單（minor，s4）**：全折。

## 實務隱患

- **自舉面（r1 s?-誠實修正）**：本改動落地 push 時會判 high——但 tier=high **來自 `pitfall_when: glob:scripts/hooks/pre-push` 既有 claim 保底命中**（碰該檔即 high），**與新範圍演算法對錯無關**。故「有觸發 high」不能當「新邏輯正確」的自舉證據——真驗證靠 hook 模擬測試（測試 2/3），不靠落地那次 push 的 tier 值。
- **fail-open 面**：新 ref 無基準時放行——與現行精神一致，但攻擊面誠實記載：故意用新 branch 首推繞檢。縱深＝家規 advisory＋CI。
- **force-push 語意**：remote_sha..local_sha 對 rewrite 歷史只涵蓋新側——git 原生語意，不特判，記載即可。
- **stdin 消費順序**：bash 中若測試段先跑會吃掉 stdin——spec 明定最先讀；測試 2 有專門格。
