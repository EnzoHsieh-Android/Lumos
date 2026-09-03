# v2 r1 席報告:架構對齊(sonnet,不佔人數)

## 問1 分層與依賴方向:一處對齊、一處 ⚠、一處已由推論解掉
**產出落點對齊**:v2 寫死 `governance/eval/gate-omission/<日期>/`,與鄰居 `ablation-lumos-first/<date>/` 同款,
r1(v1)的「產物落點沒定」已解。

**讀治理帳的路徑仍未表態,但鄰居本身就不只一種做法(⚠,不計入不對齊)**:
`retrieval_eval.py:22` 走 `_lum()` subprocess 呼 CLI 拿 JSON;但 `k1_stop_replay.py:11` 直接用
SourceFileLoader 把 `scripts/lumos` 當模組載入重用私有函式(理由寫明「單一實作」),
且 `k1_stop_replay.py`/`cd_fix.py:13`/`ledger_analysis.py:15` 都直接 open 原始帳。鄰居不一致,交編排者。
引句:「迴圈歸類用 `_roster_kind()`(`scripts/lumos:5750-5757`,`code-` 前綴=代碼審)」

**派審查員的機制由沙盒選擇間接解掉,但沒有一句明講**:
`cmd_loop_next` docstring 寫「lumos 不 spawn agent,編排仍是 Claude」(`scripts/lumos:6092`)
——design-loop 現場派 Agent 不經沙盒(審查員就在當前 session 讀真 repo)。
v2 選了 scenario_probe 式沙盒,★這只有在審查員是獨立行程(headless claude -p)時才有意義★
——現場派 Agent 沒有「副本」可拔 remote。邏輯上已定案,只是沒明講「派工用 headless,不用 loop next 現場派」。
severity: minor
blocking: 否
引句:「本案要派活的 AI 面板去讀材料,風險屬性同探針」

## 問2 命名與錯誤處理:落點對齊,重試次數自我矛盾、一支旗標漏抄
**落點/檔名對齊**:核對鄰居實際慣例——輸出目錄(`ablation_lumos_first.py:283`)、
逐場檔名帶時間戳永不覆寫(:145)、三個彙總檔(:292,325,327)。v2 引用基本吻合。
唯一 note:三個彙總檔在鄰居那邊★每次重跑會被覆寫★,「永不覆寫」真正對應的是逐場檔名那條;
spec 把兩者寫在同一括號裡,壓縮到容易誤讀。措辭精度問題,不單獨列。

**★重試哲學自我矛盾★**:同一個 M4<90% 門檻,一處說「補跑一次」、一處說「連續三次補跑」,
對同一個預先寫死的門檻給了兩個數字——與 spec 自己標榜「結果出來前寫死、不留模糊」衝突。
severity: minor
blocking: 否
引句:「M4 < 90% → 本批作廢,補跑一次;仍不足則只報「初步」並明列缺的場次。」
引句:「連續三次補跑仍不足 90% 有效場次 → 記部分結果,結論降級為「初步」並明列缺的場次。」

**`--max-per-window` 沒被提到**:鄰居除 `--wait-on-limit` 與逐題補缺外,還有
`--max-per-window`(預設 50,`ablation_lumos_first.py:271`)專門處理帳號用量、「留餘裕給人用」。
v2 只點名前兩者,沒交代要不要沿用。遺漏而非錯誤。
severity: minor
blocking: 否
引句:「撞窗口照 [[Projects/修法A_lumos先行ablation_計劃]] 既有的 `--wait-on-limit` / 逐題補缺機制處理」

## 問3 第二種做法:沙盒選擇對齊,位置回傳是未交代的跨層改動
**沙盒 vs worktree:對齊,且正確解掉 v1 的 major②**。核對三個既有隔離做法:
`guard_kill` 用 worktree 對固定測試指令做確定性突變重跑,沒有開放式 AI(`scripts/lumos:6848`);
`loop_replay` 完全唯讀不執行(`:451`);`retrieval_eval.py:255-259` 的 pin_snapshot 也用 worktree 但只釘定內容供讀取。
★`scenario_probe.py` 才是唯一一個「派有 Bash/Edit/Write、行為開放的活 AI」的既有做法★,
也正因如此才踩過 2026-08-23 推上遠端的事故。v2 選沙盒不選 worktree 的理由站得住。

**★引句位置區間重疊:沒交代這是不是跨層改動共用原語★**:
`_quote_rows`(`scripts/lumos:11445-11475`)只回 `[{'quote','ok',...}]`,判定是 `nq in hay` 存在性,
完全沒有位置/offset;而它是「T4 抽出供 CLI 與 disposal gate 共用——★單一實作★」的原語,
兩個生產端消費者(`:11796` CLI、`:11672` disposal gate)都只取 ok/too_short。
要做到位置區間重疊,今天不存在的能力必須新建:①直接改 `_quote_rows` 讓它多回傳位置
——★這會動到 disposal gate 依賴的共用原語★,任何行為變化都要對 production gate 做回歸保證;
或②只借用真正可重用的正規化單一實作 `_quote_norm`(docstring 明寫「嚴禁第二份實作」,`:11429-11439`)
自己另寫一支帶位置的比對函式,不碰 `_quote_rows`。
★spec 引用的是 `_quote_rows`(存在性函式)而不是 `_quote_norm`(正規化函式),卻又需要位置★
——這兩件事之間的落差、以及會不會動到 disposal gate 吃的那份共用原語,spec 完全沒有意識到、沒有表態。
severity: major
blocking: 是
引句:「逐條比對用既有 `quote-check` 的正規化邏輯(`_quote_rows`,`scripts/lumos:11445-11475`),★方向與該工具原生用途一致★」
引句:「兩條引句在 `r(N-1)` 快照裡的錨定位置**區間重疊**即算同一條」

不對齊共 4 條,其中 major 1 條。
