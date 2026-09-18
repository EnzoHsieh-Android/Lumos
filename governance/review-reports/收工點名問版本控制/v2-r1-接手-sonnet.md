severity: blocker

# 審查範圍與方法
逐節讀 `docs/lumos-toolchain-knowledge/Projects/收工點名問版本控制_計劃.md`(= 被審材料 `v2-r1-work.md`),對照 `scripts/hooks/claude/check-graph-sync.py`、`scripts/lumos`、`scripts/test_lumos.py`、`docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md`、`Systems/lumos-cli-lifecycle.md` 與卷證目錄實跑查證。鏡頭:整合與知識同步,假設三個月後只拿到這份計劃接手。

---

## frontmatter / 白話 / 第二版說明
已讀,無 finding。血緣、重寫理由、卷證路徑三者互相對得上(卷證目錄確實存在七份席報告)。

## 實測證據 / 根因
已讀,無 finding(前掃已驗過的事實範圍,本輪不重驗)。

## 方案:觸發條件寬鬆,檔案清單精確 / 為什麼這樣分工
severity: minor
blocking: 否 — 這節只解釋「觸發 vs 清單」兩層內部分工是否合理,沒承諾要處理跨閘重複,不算違背自己條款。
「為什麼這樣分工」只交代 Stop hook 內部觸發判準與清單判準的分工,沒有回答外部分工問題:Stop hook 改用工作樹語意後,清單會跟 pre-commit(看已暫存)、pre-push(看提交範圍)在同一批未提交檔上重疊產生提醒,三道閘各自何時各自印什麼,計劃沒有一節講清楚。
file: `docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:29-32`(三個時機表已經是三處各自呼叫 `impact --sync-check`,本計劃沒有更新這張表去反映 Stop hook 清單語意改變後三者關係)

## 新方案自帶的一個張力(嘮叨) / 誠實改口(訊息措辭)
severity: clean
blocking: 否 — 查證判準:改口後的舊詞「這一輪改了 N 個」有沒有被別處依賴。
已用 `grep` 查過 `scripts/test_lumos.py`、`scripts/scenario_probe.py`、`README.md`、`README.en.md`、`AGENTS.md`、`CLAUDE.md`:沒有任何測試斷言、探針比對或文件逐字引用這句舊訊息本文(`scripts/test_lumos.py:33010` 只斷言 `STOP_BLOCK_HEAD` 首行常數與 `"寫回"`、`"src/app.py"` 是否出現,不比對本文措辭;`scripts/scenario_probe.py:274` 只認 `LUMOS-STOP` 這個首行標頭與 `hook_run_id=`,不解析本文)。改口不會打破既有測試或工具。這節屬於本輪查得最乾淨的一節。

## 第一輪發現的去向
severity: blocker
blocking: 是 — S4 條款字面要求「不應因為它已不存在而被略過」,但重用的函式結構性做不到,對真實檔案失敗。
「新路徑沿用同一支函式即繼承,不另寫」這個決定是在舊問題(FIFO/特殊檔開檔卡住)脈絡下做的,沒考慮新問題:`_shebang_script` 靠 `p.is_file()` 開檔讀首行判斷副檔名以外的程式碼檔,而刪除的檔案在工作樹上已經不存在,`is_file()` 恆假,函式恆回 False。本 repo自己有 7 支追蹤中的無副檔名檔案依賴這條 shebang 判準(含 `scripts/lumos` 本身),若其中任一支被整支刪除,S4 會靜默漏掉它——正是這份計劃通篇在修的「少報看起來像正常運作」那個病,在 S4 自己的驗收路徑上重演。
引句:「既有程式碼已有防護(先判位置再開檔、非普通檔不開),新路徑沿用同一支函式即繼承,不另寫」
file: `scripts/hooks/claude/check-graph-sync.py:245-257`(`_shebang_script`:`if not p.is_file(): return False`)
file: `scripts/lumos:1`(`#!/usr/bin/env python3`,無副檔名,純靠 shebang 判準才被算成程式碼檔)

## PRIOR-ART
已讀,無 finding。「本 repo 4074 個追蹤檔實測跑一次約 30 至 40 毫秒」已用 `git -C <repo> ls-files | wc -l` 與 `time git status --porcelain` 現場重跑核對(4074 檔、34ms),數字準確。

## 撤除條件(RETIRE-IF)
severity: blocker
blocking: 是 — 撤除條件的可執行性是這版對 v1「簡化席 major(撤除條件寫了等於沒寫)」的直接答案,若答案本身不可執行就是同一個病沒真的治好。
卷證目錄 `governance/review-reports/收工點名改量檔案樹/` 裡只有 `.md`/`.json`/`.txt`,沒有任何 `.py` 產生器檔;`baseline-before-fix.txt` 本身是一份執行輸出紀錄(9 情境的 PASS/FAIL 表),不是可重跑的腳本。用 `find` 在整個 repo 樹(含 untracked)搜尋不到任何比對得上「情境產生器」這個角色的檔案。更根本的是:整個卷證目錄在 `git status` 下是 `??`(untracked),三個月後任何人 clone 乾淨版本都拿不到這份東西,「每季重跑」字面上無事可跑。
引句:「查得到的版本:卷證裡有一份可重跑的情境產生器(`baseline-before-fix.txt` 那支)。**每季重跑一次**」
file: `governance/review-reports/收工點名改量檔案樹/baseline-before-fix.txt`(僅為文字輸出,經 `file` 指令確認是純文字紀錄而非腳本;同目錄無 `.py`)

## 條款 S1–S6
severity: major
blocking: 是 — S5 的驗收步驟按字面操作會得出假結論(以為同步了,實際上多數部署位置沒動)。
S5 與驗收條件 #6 都把「安裝指令」寫成單數、一次跑完就能同步「所有已部署的位置」,但 `scripts/lumos` 裡 `cmd_install`(全域 `~/.local/bin` + `~/.claude/hooks`)與 `cmd_update`(vendor 進消費專案的複本)是兩支不同函式、兩個不同入口,而且 `cmd_update` 必須在**每一個**接入專案自己的 repo 裡各跑一次——本機實測目前有 20+ 個接入專案各自 vendor 了這支 hook 檔。計劃自己的〈回退〉節其實已經把這兩種指令分開寫對(「全域複本…重跑一次安裝指令」vs「每個接入專案…各跑一次更新指令」),但 S5 與驗收條件 #6 又把它們合併成一句「跑一次安裝指令」,新舊段落銜接處自相矛盾。
引句:「[S5] 當 repo 裡的 hook 檔被改動後,安裝器應把它同步到所有已部署的位置,否則實際生效的仍是舊版 [manual:改完跑一次安裝指令,再去已部署的位置對 sha256,兩邊要一致]」
引句:「每個接入專案裡各自的複本(每個專案各跑一次更新指令)」
file: `scripts/lumos:14387`(`def cmd_install`,只動 `~/.local/bin` 與 `~/.claude` 全域 hooks)
file: `scripts/lumos:15490`(`def cmd_update`,vendor 進消費專案的複本走這支,不是 `cmd_install`)

S1、S2、S3、S6 已讀,無 finding——四條都是「輸入條件 → 應有輸出」的直述句,語意明確,三個月後可直接對照測試名字判斷過沒過。

## 落點還撐得住嗎(Systems/graph-sync-coverage)
severity: major
blocking: 是 — 內容落錯家,之後「查這支 hook 為什麼這樣分發」的人會先撲空。
`Systems/graph-sync-coverage.md` 現況只 52 行,`about_code` 只列 `check-graph-sync.py` 與 `scripts/lumos`,整篇聚焦「三個時機各印什麼」,完全沒有提到部署/分發機制。本計劃要塞進去的三類部署位置、`install` 與 `update` 分工這一整段,實質上是 `scripts/lumos` 的 install/update 生命週期,而這個 repo 已經有專責節點 `Systems/lumos-cli-lifecycle.md`(`about_code: get.sh, scripts/lumos`),其開頭就在講「機器層(install/uninstall)只動 ~/.local/bin + ~/.claude…專案層(init/update/deinit)只動本 repo」這套兩層分工——跟本計劃 S5/回退節要交代的正是同一件事。`lands_in` 只寫了 `graph-sync-coverage`,沒有把部署這塊分流到 `lumos-cli-lifecycle`,這篇既有節點反而不會被更新去反映「hook 檔现在多一種同步失敗模式」。
file: `docs/lumos-toolchain-knowledge/Systems/graph-sync-coverage.md:1-32`(現況範圍與 about_code)
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:91-93`(`about_code: get.sh, scripts/lumos`;FLOW 行已明寫機器層/專案層兩層分工)

## 這份計劃沒交代、但接手的人一定會問的事
severity: major
blocking: 是 — 這是 task 指名要查的第二個重點,查到的是一個真實、已被測試鎖住的耦合,計劃完全沒提。
`scripts/lumos` 的 `lumos handoff` 指令透過 `importlib` 直接匯入 `check-graph-sync.py`,重用它的 `collect_turn_actions` 與 `EDIT_TOOLS` 兩個名字去解析上一輪動了哪些檔(`_handoff_load_hook` 明文檢查這兩個名字存在,`_handoff_intent_inner` 對 Codex 逐字稿直接呼叫 `mod.collect_turn_actions(tp)`;`_handoff_claude_turn` 對 Claude 逐字稿重用 `EDIT_TOOLS` 常數)。`scripts/test_lumos.py` 的 `t_handoff_hook_import_is_pure` 證明這個耦合是刻意且被鎖住的(它稽核「匯入 hook 只准匯出接手視圖要用的兩個名字」),但那條測試只鎖「匯入本身無副作用」,不鎖「這兩個名字被改動後 `lumos handoff` 的輸出是否還對」。本計劃的驗收條件與「第一輪發現的去向」表完全沒提到 `lumos handoff`,若 S1/S2 的實作把 `collect_turn_actions` 改成呼叫 `git status`(或改變它的回傳語意),`lumos handoff` 會在沒有任何測試翻紅的情況下悄悄改變行為。
file: `scripts/lumos:28488-28624`(`_handoff_load_hook`、`_handoff_claude_turn`、`_handoff_intent_inner`)
file: `scripts/test_lumos.py:36244`(`t_handoff_hook_import_is_pure`,鎖的是匯入純淨度、不是行為對等)

## 跟既有三道閘的分工
併入前面「方案」節已寫的 minor finding,不重複列。

## 實務隱患
已讀,無 finding。三項已排除的理由(金流/對外送出/不可逆)站得住,守衛面照走設計審合理。

## 回退
已讀,無 finding(本節的措辭其實比 S5/驗收條件 #6 更準確,見上面 S1–S6 那條 finding 的對照引句)。

## 驗收條件
已讀,無 finding 除上述 #1(情境產生器)與 #6(安裝指令)已在別處列出。第 5 步(拆前清 `__pycache__`)正確對齊本專案已知的翻紅陷阱慣例。

---

# 總結
最嚴重等級:blocker。blocking 共 5 條:①S4 刪除檔偵測對無副檔名 shebang 檔結構性失效、②RETIRE-IF 依賴的情境產生器不在版控、甚至不在卷證目錄裡、③S5 與驗收條件 #6 混淆「安裝指令」與「更新指令」、④落點誤放進 `Systems/graph-sync-coverage`(該屬 `Systems/lumos-cli-lifecycle`)、⑤`lumos handoff` 對 `collect_turn_actions`/`EDIT_TOOLS` 的既有耦合未被計劃提及或驗收。另有 1 條 minor(三道閘分工未交代)不計入 blocking。
