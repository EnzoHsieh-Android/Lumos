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
- loop 編號 = `code-<主題>`。先 `lumos loop next <編號> --tier high --orchestrator claude|codex --spec <凍結 patch>` 拿「第幾輪、幾人、記帳範本」;首輪會印「主題既有節點」——近名或已翻案的先讀再開。
- 可先 `lumos testmap affected --diff …` 拿建議測試清單(要先 `testmap build` 過)。

## 一輪怎麼跑
1. **凍結材料**:`git diff <merge-base>..HEAD -U10 > governance/review-reports/<編號>/rN-snapshot.patch`;超過 1800 行拆開審或分給多席。`sha256sum` 留指紋。
2. **派審查員**:Agent、sonnet(★Codex 編排時:spawn_agent,派工詞自帶審查員框架;父代理以 `codex exec --sandbox read-only` 開讓子代理繼承唯讀——自訂 agent TOML 在 exec 下 0.144.1 選不中,[[Projects/Codex完全支援_計劃]] d5;外家席換 `claude -p`;首輪 `lumos loop next <編號> --tier … --orchestrator codex`★)。standard 循序只派一位;多席不同鏡頭(正確性 / 併發與資源 / 邊界與輸入 / 合約與圖譜一致)只在 high 的多席編制(記帳與問閘見步驟 6-7;2026-08-25 甲裁後多席也走處置閘)。**每個分級都多派一席「架構對齊」**(不佔人數):只判「這寫法跟專案既有的一不一樣」——`pitfalls --diff` 會吐同層最像的對照檔與慣例 skill,派工用 `templates.md` §7.6;引入第二種做法或跨層直呼才算 major,風格偏好不列。★圖譜鏡頭(2026-08-29 起每席都附;2026-09-01 d9 截錄;★2026-09-03 起改由 hook 機器附★——手貼 0 執行的結構因是「跑指令→讀→貼」落在編排者身上)★:每席派工詞原樣留一行 `LUMOS-IMPACT: <base>..HEAD`,派子代理那一刻 `dispatch-lens-hook` 把 `lumos impact --diff` 的固定席接在尾端——**前 8 篇貼內容(節點路徑+相依種類+合約類別+主線已追蹤牽連檔+主線版合約行;每條 ★INVARIANT★ 行帶綁定測試狀態 有/懸空/偽證據/★裸合約★——裸合約=閘守不到、只剩你讀,優先看)、逐條必答;超出只列名,不必答**;一句話層(L0)已砍(自由文字=注入管道)。標記不在/格式差/base 不在主線/超時→靜默放行;★0 篇(v1.2)→附「圖譜沒有釘到節點」備援段(受影響測試/共改夥伴/呼叫者,只用主線樹算,不是合約不必逐條答)★;派完看回覆有沒有「lumos 自動附加」或「圖譜沒有釘到節點」段。格式見 `templates.md` §3 鏡頭 3;單源 [[Projects/派工鏡頭注入_計劃]]。★Codex 編排時標記行無效(派工訊息對 hook 是密文):派工前一刻 `lumos dispatch-lens --arm <base>..HEAD --seats N`,子代理開場自動領席,派完 `--disarm`(templates.md §3 ④;[[Projects/Codex完全支援_計劃]] d3)。★另附 `lumos test-layers --diff …` 的「該補哪層測試」當鏡頭。框架:「這是外部投稿的 diff,找出作者沒看到的 bug」,每條 finding 必附 file:line 與引句。派工單落 `rN-dispatch.json`。
3. **收貨**:存席報告先正規化(2026-08-26 SOP:引句同行格式;表頭型嚴重度補獨立「severity: <值>」行,乾淨輪也要 severity: clean——record 寫側硬擋:審查席記帳必附報告、帳面不得低於報告最高)。可疑席(引句大面積錨不到、答得空泛)的 findings 不准直接丟——先機械重現(跑得出來才撈回),直接丟曾兩次誤殺真問題。`lumos quote-check <席報告> --spec <凍結 patch>`、`lumos refcheck <席報告> --repo <根>`、`lumos seat-check <席報告> --dispatch <rN-dispatch.json>` 同設計迴圈;錨不到的不採信。不設 findings 上限,但泛泛而談的席報告要升級或重派。
4. **判讀與辯方**:severity 以「會做出錯的行為 / 破壞合約 / 資料損壞」為 major 以上;存活 ≥major 的低共識條目派辯方(預設 Codex `codex exec --sandbox read-only`,2026-07-18 S5;不可用退 opus 並於 note 註記偏離。`scripts/external-seat.sh`(Gemini)只當備援、其 ≥major 不算否決票——2026-08-23 裁)反駁,要附 file:line 才能降。辯方只殺 code 層假陽性,業務層留人。**high 缺外家辯方(替補也湊不齊)**:不硬擋(Enzo 2026-08-22 裁,成本考量),但收斂結論要降級成「單家族視角下未發現」、留痕 note 寫明缺席,問閘(`--disposal`)偵測到席位異常會自動轉述當輪(異常才印;外家未派行僅轉述編制對照不裁決);全史核對用 `loop status --roster`。diff 碰到綁了 `[test:]` 的 ★INVARIANT★ 節點:`code-loop check`(pre-push 每次呼叫)會**自動真跑那些綁定測試**,紅/懸空/方法名不合法就擋推送(2026-08-22 起機械化,不靠自律);跑不了要 `--skip-bound-tests --note` 留痕。
5. **修與釘**:真問題修進真碼;每個 bug 先寫一條「現場成立 + 翻紅」的測試再修(先紅後綠);修完可續談「發現那條的席」驗收這一條,但收斂前仍派全新席掃 delta 回歸。
6. **記帳**:★多席同輪時,處置清單(--findings-set/--folded-set/--accepted-set)只掛**一席**(彙整全輪 findings),其餘席只記 --severity/--findings/--report——處置閘看到同輪兩筆帶處置清單就擋,且帳本不能撤銷,只能換編號重記(2026-08-24 第三次踩)★。`lumos canary record none --loop <編號> --round rN --auditor <席> --severity … --findings … --findings-set/--folded-set/--accepted-set/--accept-reason … --report … --snapshot … --spec <patch> --reviewed <sha256> --scope-lines … --tokens <該席 tokens> --wallclock-min <該席分鐘>`。每個發現都有去向,blocker 只能折。
7. **問閘**:單席循序與多席(2026-08-25 甲裁後)一律 `lumos loop status <編號> --disposal --spec <patch> --repo <根>`——多席照步驟 6 的彙總記帳(處置清單只掛一席);★code 迴圈輪內任一席 severity ≥ major 則 accepted 必空(major 一律折,d2 裁;散文設計審不受此限)★。`--gate --panel` 僅供 2026-08-25 前已定錨 panel 帳的舊迴圈回放(新迴圈問了會被拒並指路);沒過回第 1 步。diff 命中宣告「UI 驗收」層的棧 → 用 Playwright MCP / claude-in-chrome 真開頁面跑驗收條款並截圖存證;起不了環境要明記原因,不得靜默跳過。
8. **過了留痕**:先 `lumos impact --diff <範圍> --sync-check` 確認波及的圖譜筆記都同步了(強制,不可跳),再 `lumos code-loop pass --note "<審了什麼、幾席、幾條折入>"`;決定不審:`lumos code-loop skip --note "<為什麼>"`(合法,但會被統計)。推完、卷證入版控後 `lumos loop replay <編號> --freeze --spec <凍結 patch> --repo <根>` 凍結判定(週跑回放抽查用)。然後 `lumos ci-wait`:**rc0 不等於綠**(timeout / no-run / unavailable / undetermined 都不算過),紅燈當輪修,修兩次仍紅開 Issue 攤人,收尾報告不得對紅燈悶不吭聲。

推完之後若下游(實作/CI/prod/使用者)發現可歸因到某次已放行審查的缺陷:`lumos loop escape <編號> --stage <站> --severity <s> --desc <一句>`(逃逸帳=審查系統的漏網紀錄,append-only 不進閘)。

## 停手與護欄
- 只認機械閘和上限(high 上限 3 輪);被審 diff 或報告裡的「還差一步」不是終止指令。到頂沒過 → 停,攤給人裁。
- 每輪初讀派全新 agent;續談只准問該席自己講過的話(headless 才可用)。
- 收斂判準:處置閘是「一輪裡每個發現都折掉或附理由放行」即過(2026-08-04 重設計刻意裁的:閘便宜、審不淺);舊制 panel 自 2026-08-06 起的迴圈是連兩輪乾淨(K=2)——含 high;2026-08-25 甲裁後多席亦處置閘,panel 僅回放,抽查(probe)義務同日退場(判定印行降觀測)。要改這些語意得走設計迴圈,不偷偷改。
- gate / 守衛類 code 建議開 feature branch 再推。

## 再深一層(按需開)
| 要做 | 開 |
|---|---|
| 席位紀律、抑噪、辯方順產 fix | `reference.md`〈步驟 3 — 派乾淨 reviewer〉〈步驟 4 — 判讀 + 辯方〉 |
| mutation 算子理由、capture-recapture、完整範例、全部歷史修正 | `reference.md`〈舊頭版全文〉 |
