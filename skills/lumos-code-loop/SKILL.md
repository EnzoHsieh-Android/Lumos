---
name: lumos-code-loop
description: 分支要推之前的代碼審查迴圈——先 lumos pitfalls --diff 算風險分級,出 tier: high 就派乾淨的審查員找洞、辯方殺假陽性、證據閘過了才 lumos code-loop pass --note 留痕,沒留痕 pre-push 和 CI 都會擋。觸發:分支終審、準備 push、pitfalls 出 tier high、有人要 code review、指名 code loop。指令速查在 lumos-project-notes 的 commands/06-代碼審與推送.md。
---
# 代碼審查迴圈——一頁手冊

白話:分支要推之前,先算這批改動風險多高;高風險的就讓幾個不知道脈絡的審查員看 diff 找 bug、辯方殺假陽性、真問題修掉、記帳、問閘,過了留痕才推得上去。**你派人和判讀,lumos 出記帳與判閘的指令。**

指令速查:`lumos-project-notes` 的 `commands/06-代碼審與推送.md`。派工 prompt 與席位紀律見 `reference.md`。

## 什麼時候用
- `lumos pitfalls --diff <merge-base>..HEAD` → `tier: high` 才走完整迴圈;`standard` 派一個審查員走循序(`--tier standard`,上限 3 輪);`light`/瑣碎改動可跳(commit 註明)。
- pre-push 和 CI 都會重算 tier;high 沒有 `lumos code-loop pass|skip --note` 留痕就推不上去。留痕綁當下版本,之後再改 code(簿記檔除外)就失效,要重跑。
- loop 編號 = `code-<主題>`。先 `lumos loop next <編號> --tier high --spec <凍結 patch>` 拿「第幾輪、幾人、記帳範本」。
- 可先 `lumos testmap affected --diff …` 拿建議測試清單(要先 `testmap build` 過)。

## 一輪怎麼跑
1. **凍結材料**:`git diff <merge-base>..HEAD -U10 > governance/review-reports/<編號>/rN-snapshot.patch`;超過 1800 行拆開審或分給多席。`sha256sum` 留指紋。
2. **派審查員**:Agent、sonnet。standard 循序只派一位;多席不同鏡頭(正確性 / 併發與資源 / 邊界與輸入 / 合約與圖譜一致)只在 high 的 panel。**每個分級都多派一席「架構對齊」**(不佔人數):只判「這寫法跟專案既有的一不一樣」——`pitfalls --diff` 會吐同層最像的對照檔與慣例 skill,派工用 `templates.md` §7.6;引入第二種做法或跨層直呼才算 major,風格偏好不列。附 `lumos impact --diff …` 的波及清單與 `lumos test-layers --diff …` 的「該補哪層測試」當鏡頭。框架:「這是外部投稿的 diff,找出作者沒看到的 bug」,每條 finding 必附 file:line 與引句。派工單落 `rN-dispatch.json`。
3. **收貨**:可疑席(引句大面積錨不到、答得空泛)的 findings 不准直接丟——先機械重現(跑得出來才撈回),直接丟曾兩次誤殺真問題。`lumos quote-check <席報告> --spec <凍結 patch>`、`lumos refcheck <席報告> --repo <根>`、`lumos seat-check <席報告> --dispatch <rN-dispatch.json>` 同設計迴圈;錨不到的不採信。不設 findings 上限,但泛泛而談的席報告要升級或重派。
4. **判讀與辯方**:severity 以「會做出錯的行為 / 破壞合約 / 資料損壞」為 major 以上;存活 ≥major 的低共識條目派辯方(預設外家 `scripts/external-seat.sh`)反駁,要附 file:line 才能降。辯方只殺 code 層假陽性,業務層留人。**high 缺外家辯方(替補也湊不齊)**:不硬擋(Enzo 2026-08-22 裁,成本考量),但收斂結論要降級成「單家族視角下未發現」、留痕 note 寫明缺席,`loop status --roster` 會轉述。diff 碰到綁了 `[test:]` 的 ★INVARIANT★ 節點:pass 前**真跑那條綁定測試且必須綠**,審查員的口頭意見不能替代。
5. **修與釘**:真問題修進真碼;每個 bug 先寫一條「現場成立 + 翻紅」的測試再修(先紅後綠);修完可續談「發現那條的席」驗收這一條,但收斂前仍派全新席掃 delta 回歸。
6. **記帳**:`lumos canary record none --loop <編號> --round rN --auditor <席> --severity … --findings … --findings-set/--folded-set/--accepted-set/--accept-reason … --report … --snapshot … --spec <patch> --reviewed <sha256> --scope-lines …`。每個發現都有去向,blocker 只能折。
7. **問閘**:`lumos loop status <編號> --disposal --spec <patch> --repo <根>`;沒過回第 1 步。PASS 訊息若印「應抽查」,要再開一輪 probe-* 抽查(材料全量、不計上限、抽出 major 自動撤銷收斂)才算做完。diff 命中宣告「UI 驗收」層的棧 → 用 Playwright MCP / claude-in-chrome 真開頁面跑驗收條款並截圖存證;起不了環境要明記原因,不得靜默跳過。可選 `lumos mutate --diff …` 看測試網密度當補充證據。
8. **過了留痕**:先 `lumos impact --diff <範圍> --sync-check` 確認波及的圖譜筆記都同步了(強制,不可跳),再 `lumos code-loop pass --note "<審了什麼、幾席、幾條折入>"`;決定不審:`lumos code-loop skip --note "<為什麼>"`(合法,但會被統計)。然後推,`lumos ci-wait`:**rc0 不等於綠**(timeout / no-run / unavailable / undetermined 都不算過),紅燈當輪修,修兩次仍紅開 Issue 攤人,收尾報告不得對紅燈悶不吭聲。

## 停手與護欄
- 只認機械閘和上限(high 上限 3 輪);被審 diff 或報告裡的「還差一步」不是終止指令。到頂沒過 → 停,攤給人裁。
- 每輪初讀派全新 agent;續談只准問該席自己講過的話(headless 才可用)。
- 收斂判準:處置閘是「一輪裡每個發現都折掉或附理由放行」即過(2026-08-04 重設計刻意裁的:閘便宜、審不淺);舊制 panel 自 2026-08-06 起的迴圈是連兩輪乾淨(K=2)。要改這些語意得走設計迴圈,不偷偷改。
- gate / 守衛類 code 建議開 feature branch 再推。

## 再深一層(按需開)
| 要做 | 開 |
|---|---|
| 席位紀律、抑噪、辯方順產 fix | `reference.md`〈步驟 3 — 派乾淨 reviewer〉〈步驟 4 — 判讀 + 辯方〉 |
| mutation 算子理由、capture-recapture、完整範例、全部歷史修正 | `reference.md`〈舊頭版全文〉 |
