# 外部稽核 r2:機制空轉盤點(2026-09-05)

> 稽核方法:開碼(`scripts/lumos`)、翻帳(`docs/.governance-log.jsonl` 23934 行、`docs/.usage-log.jsonl` 415 行、`docs/.bypass-log.jsonl`/`.kill-log.jsonl`/`.signoff-log.jsonl`/`.ci-log.jsonl`、`governance/logs/autonomous.log` 528 行)、翻真實逐字稿(`~/.claude/projects/-Users-enzo-harness-lumos-toolchain/*.jsonl`)。每條先給指令/檔案+輸出摘要,再判定。判定值:①名副其實 ②言過其實 ③空轉 ④不自洽。上一輪(`readme-audit-2026-09-05.md`)處理過的項目(Stop hook、pre-commit、code-loop pass、自主迴圈存在性、鏡頭利用率、處置閘、合約鏈、成本)不重做。
>
> 誠實聲明:過程中一次誤把 `--help` 當 repo 路徑餵給 `replay_weekly.py`,在 cwd 建出 `./--help/governance/replay/` 空目錄——已 `rm -rf` 清掉,`git status` 確認乾淨,未進版控。

---

## 1. `lumos doctor --verbose` 二十多道檢查 vs 治理帳

**證據**(`scripts/lumos` 裡所有會寫 `docs/.governance-log.jsonl` 的 `gate` 值 vs 帳裡實際出現的 `gate` 值,python 掃全 23934 行):

程式碼裡定義的 gate:`anchor-approve bound-tests canary check-cascade check-e1 check-e2 check-e3 check-j check-k check-lint-decl check-r check-revisit check-s check-s2 ci code-loop delguard design-loop doctor-run kill L2 signoff`

帳裡實際出現過的:`check-s(19404) check-e1(1962) check-s2(890) check-e3(395) doctor-run(393) anchor-approve(265) check-cascade(214) code-loop(130) check-revisit(96) design-loop(94) delguard(63) bound-tests(28)`

**從沒響過**(2026-07-02 建帳以來,同一份 `docs/.governance-log.jsonl`,零筆):`check-e2`(建在被推翻決策上)、`check-j`(regen 來源守衛)、`check-k`(★COMBO★ 組合覆蓋)、`check-lint-decl`(lint.json 格式壞掉)、`check-r`(可逆性回退綁定違規/標錯位置)。

**判定關鍵**:查了每道的觸發條件(`scripts/lumos` 對應行號)才發現這 5 道**不是空跑**——它們是「違規才響」的硬檢查,不是「每次都印」的巡檢:
- `check-r` 只在 ★IRREVERSIBLE★/★CHECKPOINT★ 標錯位置(標在非 Systems 節點)或沒寫回退時才響;本專案目前 0 篇違規。
- `check-lint-decl` 只在 `.lumos/lint.json` **存在但解析失敗**時才響;本專案根本沒有 `.lumos/lint.json`(見 §9),條件不成立,不是「查了沒查到」而是「沒有可查的東西」。
- `check-j`/`check-k`/`check-e2` 條件更窄(regen 節點需 from-scratch 標記、★COMBO★ 需特定標記組合、check-e2 需要「決策被推翻+有下游節點在推翻前建到它上面」的時序巧合)。

**`ci`/`kill`/`L2`/`canary`/`signoff`**:一開始以為也是「從沒響」,但翻 code 才發現這 5 個 gate 名稱不寫進 `docs/.governance-log.jsonl`,而是各自寫自己的帳本(`docs/.ci-log.jsonl` 91 筆、`.kill-log.jsonl` 4 筆、`.bypass-log.jsonl` 66 筆、`.canary-log.jsonl`、`.signoff-log.jsonl` 8 筆),只在 `lumos gov` 讀時才彙整顯示成這些 gate 名——**這不是空轉,是我一開始只查了一本帳、沒查到另外五本**(踩了 CLAUDE.md 自己寫的「查得到才算先行」的反例,已回頭核對)。

**「每天都響、同一批連續兩週沒人處理」**(用 `nodes` 欄按日期去重統計):
`check-s`(L4 自足性審計提醒,軟性、不擋)歷史上有多批節點被連續標記遠超 2 週:`reversibility-governance-ledger` 40 個不同日、`design-loop` 39 天、`pitfalls-code-loop` 35 天、`retrieval-ranking` 29 天、`lumos-cli-read`/`lumos-cli-write` 各 28 天、`loop-convergence-recording` 32 天。但這些**最後都被批次清掉**:`git log` 找到 `7e5d361`(2026-08-24)`fix(gov): 清掉兩組 44/40 天空轉——CLI 讀/寫兩篇樞紐筆記自足性審計...`,對應 `lumos-cli-read`/`lumos-cli-write` 兩篇的 `self_audit` 欄位確實蓋上 `sonnet/2026-08-21` 或之後日期。**今天(09-05)唯一被 check-s 連續點名的是 `codex-harness`**——但這篇是今天(2026-09-05)才建的新節點,還沒來得及自審,不算「響了沒人理」。

**判定:①名副其實(帶但書)**。check-s 這類軟提醒**會**被長期忽略(30+ 天常態),但**最終**在幾次批次清帳(08-21、08-24、08-30 前後)裡被处理掉,不是永久空轉;5 道「從沒響」的硬檢查是因為違規真的沒發生或條件不成立,不是死碼。

---

## 2. 每週回放 `governance/autonomous_loop/replay_weekly.py`

**證據**:`governance/replay/.weekly-stamp` = `2026-W36`(本週已跑過);`governance/autonomous-loop.sh` 的 `run_replay()` 每天呼叫、靠週戳記防重跑。`governance/logs/autonomous.log` 528 行裡搜 `回放週跑` 且非「本週已跑」的只有 **2 筆真跑**:
```
2026-08-27 09:37:31  frozen=[dref-v4, code-dref, code-toolfix, ...] unfreezable=[...]
2026-08-31 10:18:52  frozen=[entry-latch, code-entry-latch, graph-usage-stat-std, ...] unfreezable=[...]
```
（機制本身 2026-08-26 才落地,至今 09-05 共 10 天,只到得了 2 個 ISO 週邊界,這是設計上的「每週一次」,不是漏跑。）

**回放結果(紅/翻案)看不到**:兩筆日誌只截了 `head -1 | cut -c1-160`,而 `red`/`stale`/`errors` 三個關鍵欄位在 JSON dict 裡排在 `unfreezable`/`replayed`/`skipped` 之後,常常被 160 字元截斷吃掉——**帳面本身有盲區,審計看不到「這兩次跑到底有沒有紅」**。兩次都有 `LINE 200`(推播成功),但 `build_msg()` 只要 `unfreezable` 非空就會送(不代表一定有紅)。

`governance/replay/*/verdict.json` 共 41 個 golden,mtime 全部等於各自凍結時間(08-26/09-02/09-03/09-04/09-05 分批),**沒有任何一個 verdict.json 在凍結之後被重寫過**——與「回放發現漂移就要人工重凍」的設計一致地指向同一結論:**目前為止沒有任何一次回放翻案**。

**判定:②言過其實**。機制本身在跑(不是空轉),但（a）跑了 10 天只補齊了新凍結、還沒真正走完一輪「舊帳輪替抽查」（`.rotation-cursor` 裡 `done` 只有 21/41、`cycle_started` 是空字串,代表一整輪都還沒跑完一次)（b）它宣稱要抓的「邏輯漂移/翻案」目前**零命中**,但因為帳面截斷看不出這是「真的沒漂移」還是「紅色被截斷吃掉沒人發現」——**這本身就是一個空轉風險:凍結越堆越多(41 個),回放預算固定 300 秒、每週只抽 5 個舊包,舊包要等很多週才輪得到一次,真正發生漂移可能要很久才被抽中一次。**

---

## 3. 情境探針週抽 `governance/scenarios/history.jsonl`

**證據**:`history.jsonl` 只有 3 筆(W34 2026-08-23、W35 2026-08-24、W36 2026-08-31),`autonomous.log` 確認之後(09-01~09-05)每天都是「本週已抽過,跳過」——探針本身**是**每週真跑,不是空轉。

三週失敗題:
- W34:`a03-related-weak-edge`
- W35:`d01-writeback-after-code`
- W36(最近一次,08-31):`s09-writeback`、**`s15-new-verification`**

**`s15-new-verification` 是有歷史的迴歸**:`git log -p` 找到這題 2026-07-24(commit `372e88d`)加入時「整理後 32 情境全過」,即當時是過的;到 08-31 週抽變成 0/8 裡的失敗題之一。09-02 的 ablation 實驗（`governance/eval/ablation-lumos-first/2026-09-02/`）**明確承認**這題兩組(with/without)都是 0/3,並在 Verification 筆記 `2026-09-02_修法A_lumos先行ablation結果.md` 寫明:「s15-new-verification 兩組皆 0/3(**既有失敗,與本案無關,週抽查 08-31 已紅過**)」——**這是一句「知道壞了、但決定先不管」的原文**。到今天(09-05,距 08-31 已 5 天,距最初疑似迴歸的窗口可能更久),`governance/scenarios/commands.jsonl` 裡 s15 的題目文字/expect 從未被修改過(git log 只看到新增,沒有修改),也沒有找到任何後續 commit 或決策節點針對 s15 做修復。

**判定:③空轉(對「失敗會被修」這個假設而言)**。探針本身有在跑、失敗有被記錄、也有被人在筆記裡點名承認——**但承認之後沒有觸發任何修復動作**,已知失敗至少掛了 5 天以上(從最近一次確認的 08-31 到今天),而且 09-02 的實驗報告是在「已知這題壞」的前提下**選擇繞過而非先修**。

---

## 4. 治理日報 `governance/ai-governance-research.sh` → `governance/reports/governance-*.json`

**證據**:`grep -rn 'reports/governance-' governance/*.sh` 只命中 `governance/autonomous-loop.sh:40,130`——這是**唯一**讀這批日報檔的程式。細看用法:`autonomous-loop.sh` 第 289 行 `gap_select.select('$REPORT', ...)` 直接把當天日報路徑餵給選 gap 的邏輯,`governance/logs/autonomous.log` 裡**每一天**(08-27 到 09-05,無漏)都有一行「選中 gap:{...}」,且 `weakness`/`suggestion` 內容逐日不同、`source_date` 對得上當天日報——**這是機械可驗的每日真消費,不是猜的**。`governance/reports/governance-2026-09-0{1..5}.json` 五個檔都在、大小 6.7k–8.3k、mtime 對得上早上 09:3x 產出時間。

**判定:①名副其實,推翻稽核提問裡的預設**。稽核題目原本假設「唯一消費者是已暫停的自主迴圈,現在白產」——查證後發現這個假設本身錯了:`autonomous-loop.sh` **非 dry-run**(真的自動開 PR)那條路徑在 2026-07-29 才被停用(confused-deputy 風險),但 **dry-run 模式(選 gap→brainstorm→備 pending 等人放行)一直在跑,而且是每日日報的唯一消費路徑,也確實每天都消費**。這是「肯定斷言也要查」的一個好例子——沒有先查證就會誤判成空轉。

---

## 5. `lumos gov`:L2 bypass 帳

**證據**:`docs/.bypass-log.jsonl` 共 **66 筆**,涵蓋 2026-06-29 至 2026-08-31;**最近 30 天(08-06~09-05)只有 5 筆**,分別是 08-26×2、08-31×3;**最近 5 天(09-01~09-05)是 0 筆**。

**有沒有人看了帳做決定**:全文搜尋 `bypass.*率`/`bypass.*次數`/`L2.*次數` 在 `docs/lumos-toolchain-knowledge/` 內**沒有任何命中**。唯一提到 bypass 帳的 Issue(`簿記白名單漏canary與bypass帳.md`)談的是「bypass 帳自己會不會被 commit 進版控」的簿記 bug(已 2026-08-27 根治),**不是**「看了 bypass 頻率後調整規則」。對照組:同樣是 `lumos gov` 第 4 源的 canary 帳,`Systems/canary-audit.md` 明文寫「連 2 次 missed 升級:換更強模型...升級前先 `lumos gov --since 7` 看 missed 史」——這是一個**真的被讀來做決策**的帳;bypass 帳沒有對應的消費規則。

**判定:③空轉**。帳本身機械記錄正確(66 筆逐一可查、無漏記跡象),但沒有找到任何「看了這本帳因而改變行為」的證據——它只被動存在,沒有下游消費邏輯或人工複查慣例。

---

## 6. 入口栓 entry-latch 與逃逸帳 escape-log

**證據**:
- `docs/.escape-log.jsonl`(`lumos loop escape` 寫入處)**存在但 0 行**。計劃筆記 `Projects/loop數據收集_計劃.md` 自己寫明:「**現況 0 筆=還沒人記,不等於零逃逸**」——這是專案自己承認的空白,不是我猜的。
- 攔截帳用零工具慣例(裁定文字裡手寫 `★圖譜攔截★站:...`),`grep -rn "★圖譜攔截★" docs/*-knowledge` 只找到出現在 `Projects/loop數據收集_計劃.md` 自己內部:一份「種子表」(2026-08-30 一天三筆,回溯記錄、按設計**不計入**週報 grep 流)+ 一筆 2026-08-31 的真實記號——而那筆恰好是**同一份計劃自己對自己的重開決策**(「B(使用率 held 池)死」)。也就是說:記號慣例 08-31 生效以來 5 天,**除了計劃節點自己引用自己那一次,沒有找到任何獨立提案被這個機制真的攔下**。
- entry-latch(`loop next` 首輪印既有節點)本身有 28 條測試綠、一次真事故重放成功(2026-08-29 燒兩輪設計審才發現的近名節點,08-30 上線後同題「開迴圈第一秒就在眼前」)——**這部分是真的有效**,但那是上線驗證當天的示範重放,不是後續 5 天內的獨立自然案例。

**判定:③空轉(逃逸帳)/①名副其實(entry-latch 本身,但樣本只有 1 個上線示範)**。逃逸帳完全零使用,且專案自己已經承認;攔截帳的記號慣例 5 天內只有 1 筆自我指涉的記錄,還不足以判斷它有沒有在真實開案場景裡發揮作用。

---

## 7. cochange / delguard / Check S 提醒

**Check S** 見 §1(結論:長期忽略但最終批次清帳)。

**delguard(code 側刪除傳播守衛)**:`docs/.governance-log.jsonl` 裡 `gate=delguard` 共 **63 筆,kind 全部是 `degraded`**,涵蓋 2026-08-21 至今天 09-05(幾乎每天,含今天已 2 筆,12:06、12:21)。翻 code(`_delguard_log_degraded`)才發現:**這個 log 只在超時/內部錯誤(fail-open 放行)時才寫**,成功掃描(不論有沒有命中)完全不進治理帳、只印在終端機——**所以這 63 筆不是「63 次違規」,是「63 次守衛根本沒有真的檢查、直接放行」**。而且**全部 63 筆 reason 都是 `timeout`**:deadline 曾在 2026-08-27 從 5 秒調到 15 秒(code 註解:「一 session 降級多次→15」),但調整之後(08-27 到 09-05,9 天)**超時仍持續發生、幾乎每天都有**——說明那次調整沒有真正解決問題,而且沒人再回頭處理。

**cochange(漏改夥伴檔提醒)**:`pre-commit` 每次 commit 都呼叫(`scripts/lumos cochange check --staged`),但**輸出只印到終端機、完全不落地任何帳本或檔案**——沒有 `.cochange-log.jsonl` 這種東西。抽 5 個最近的真實 commit(`9ed55bb`、`93daa4c`、`0a51a6d`、`ad354e5`、`f1956c2`)重放 `cochange check --diff <parent>..<commit>`:前 4 個(純簿記/卷證 commit)無警告;`f1956c2`(2026-08-24)重放出**真警告**:「改了 `lumos-entry-hook.py` 但沒動 `工具鏈補強十件_計劃.md`/`test_lumos.py`(過去 100% 一起改,共 3 次)」——往後查 `git log`,這兩個檔在那之後也沒有被回頭補上。**由於沒有任何持久化的帳,無法系統性回答「30 天內響了幾次」——這本身就是稽核盲區:一個天天在跑、偶爾抓到真問題的機制,卻沒有留下任何可事後稽核的痕跡。**

**判定**:delguard=**③空轉**(每次呼叫都因超時直接放行,實際檢查能力可能長期是 0,只是「壞掉的方式」被誠實記了帳);cochange=**④不自洽**(機制本身會抓到真問題,但完全沒有留痕機制去驗證有沒有人理會它)。

---

## 8. `guard kill` / `signoff` / `spec-trace` / `testmap build` / `link-candidates` / `decision-refs` / `self-audit` 使用頻率

`docs/.usage-log.jsonl`(415 筆)**只記 `context`/`show` 兩種子指令**,以下數字全部改查各自的專屬帳本或旁證:

| 指令 | 帳本 | 總筆數 | 最近一次 | 距今 |
|---|---|---|---|---|
| `guard kill` | `.kill-log.jsonl` | 4 | 2026-08-22 | 14 天 |
| `signoff` | `.signoff-log.jsonl` | 8 | 2026-08-08 | 28 天 |
| `spec-trace` | 無(唯讀指令,設計上不留痕) | — | — | 查不到 |
| `testmap build` | `.lumos/testmap.json` mtime | 只跑過 1 次 | 2026-08-08 | **28 天、614 個 commit 沒重建** |
| `link-candidates` | 無專屬帳;`git log --grep` 全庫 0 命中 | — | — | 查不到有人真的跑過 |
| `decision_refs` | 計劃節點自述 | 真回填 8 條 refs/5 節點,一次性批次(2026-08-27) | 2026-08-27 | 9 天;之後全量回填被明文列為「低優先、非阻塞」暫緩 |
| `self-audit` | 各節點 `self_audit:` 欄位 | 見 §1,批次落在 08-21/08-24/08-30 | 08-30 | 6 天(但只覆蓋當時被點名那批,非常態) |

**testmap 細節**:`.lumos/testmap.json` 的 `built_at_commit` 是 `3439fab...`,`git rev-list --count 3439fab..HEAD` = **614**,即這份「檔案↔測試依賴地圖」落後 HEAD 614 個 commit、28 天。程式碼裡確實有陳舊三訊號會判斷 `stale: true`(比對 `built_at_commit` 是否為 HEAD 祖先、diff 範圍是否碰到地圖涉及的檔案),但這個判斷只在有人手動跑 `lumos testmap affected --diff ...` 時才會被看到——而**没有任何證據**這 28 天內有人真的跑過 `testmap affected`(無帳、無 review-reports 提及)。

**判定**:`guard kill`=①名副其實但使用稀疏(4 次都對應真實合約殺傷力驗證,非空轉,只是低頻);`signoff`=①名副其实但更稀疏(8 條都對應真實業務決策簽核,28 天沒有新的不代表機制壞,只是這段時間沒有需要人簽核的業務決策);`testmap build`=**③空轉**(建過一次就沒人維護,陳舊守衛存在但沒人觸發去看);`link-candidates`=**③空轉**(`Systems/retrieval-ranking.md` 自己標「S1=lumos link-candidates 補鏈候選(唯讀,人裁待辦)」,「待辦」從 2026-08-07 掛到今天,29 天沒有任何 git 紀錄顯示真的被跑來裁過);`decision_refs`=①名副其實(範圍小但有真實交付與驗證,誠實標注覆蓋窄)。

---

## 9. pitfalls 的 linter 橋(compose-metrics / sqlfluff-sarif / stylelint-sarif / lint-watch)

**本 repo 自己沒有 `.lumos/lint.json`**(`find . -iname lint.json` 只查到 `docs/methodology` 等文件裡的文字提及,repo 根目錄下沒有這個宣告檔)——lumos-toolchain 自己是純 Python 專案,沒有接自己的 linter 橋。

**code 裡的誠實自白**(`scripts/lumos` doctor 區塊,2026-08-29 註解):
> 「★2026-08-29 誠實化★:原訊息只說『格式健康』,讀起來像 linter 有在保護這個專案——實際上**所有自動路徑(pre-push 三處、tier 判定)都帶 `--no-lint`,CI 也不跑 pitfalls**,真正會執行 linter 的 `_lint_run_and_parse` **只有兩個手動呼叫者**。」

機械覆核:`grep -rn "\-\-no-lint" scripts/hooks/pre-push` 命中 3 處(全部 `--no-lint`);`.github/workflows/ci.yml` 全文沒有任何一處呼叫 `pitfalls`(只呼叫 `code-loop check`,而其內部同樣不主動跑真 linter)。

**外部消費專案覆核**(本機上找得到的兩個曾被驗證的消費端):
- `~/backend/LandmarkMember/.lumos/lint.json`:mtime **2026-07-06**(驗證當天),之後從未再改;`testmap.json` mtime 2026-07-28;`git log`(Landmark 自己的 repo)搜尋 `lint|sarif|sqlfluff|compose` **零命中**——Landmark 自己的提交歷史裡從來沒有出現過任何跟這個 lint 橋相關的字眼,對應到它自己的 `docs/.governance-log.jsonl` 也**查不到任何 lint 相關 gate**。
- `compose-metrics-adapter` 宣稱驗證過的「KDS」專案:全機掃描 `compose-baseline.json`/`compose-metrics.json`(這個功能運作必需的兩個宣告檔)**在整台機器上完全找不到**(`~/Compass_KDS`、`~/Citrus_KDS` 都沒有),`~/Citrus_KDS/.lumos/` 只有 `lint.json`(mtime 2026-07-27,一個月沒動)+ `config.json`,**沒有** compose-metrics 需要的設定檔。

**判定:③空轉**。這一整條偏科 linter 橋(SARIF 通用橋+ C#/Kotlin/SQL 專用適配)是靠**單次真機驗證**(2026-07-04~07-06)拿到「已交付」的標籤,但驗證之後:①本 repo 自己所有自動化路徑都明確繞過真跑 linter(code 自己承認)②唯二能查到的外部消費專案,一個(Landmark)一個月沒有任何跟進使用痕跡、另一個(KDS)連設定檔都已經不存在。目前找不到任何機械證據支持這條線在驗證之後有被任何專案在日常流程裡真正使用過。

---

## 10. `valid_under`/`revalidate_when` 與 `lumos archive`

**覆蓋率**:`docs/lumos-toolchain-knowledge/Verification/` 共 **170** 篇,`valid_under` 163 篇有填、`revalidate_when` 163 篇有填(96%,同一批 7 篇缺兩者皆缺,多為早期 2026-07 文件)。

**>90 天沒更新**:機械掃描 `date:` 欄位,**0 篇**超過 90 天。但這個「0」不是機制有效的證據——是**專案本身還沒滿 90 天**(最早的知識圖譜設計文件約 2026-06-19/20,到今天 09-05 是 77~78 天),TTL 機制目前**還沒有機會被真正考驗過**。16 篇早期筆記(2026-07-02~07-20)連 `date:` 欄位都沒填(用檔名日期代替),但也都在 90 天窗口內。

**`lumos archive`(預設 180 天滾動歸檔)**:`git log --all --grep="lumos archive|滾動歸檔"` 全庫 **零命中**——從未被執行過。同樣因為專案不到 180 天,**這不是空轉,是條件還沒成立**;但也代表這個工具至今是純理論存在,完全沒有真實運行資料能驗證它的行為(移檔/連結正規化邏輯)在真實 vault 規模下對不對。

**判定:①名副其實(欄位紀律好)+ 待驗證(TTL/archive 機制本身年齡不夠,無法判斷)**。不是空轉,但也不能標「有效」——只能誠實寫「還沒到考驗的時候」。

---

## 11. 派工鏡頭 dispatch-lens 的真實投遞率

**方法**:掃 `~/.claude/projects/-Users-enzo-harness-lumos-toolchain/*.jsonl`(25 個逐字稿檔),找 `type=assistant` 且 `tool_use.name in (Agent, Task)` 的呼叫,檢查其 `input`(即實際派工詞,若 hook 用 `updatedInput` 改過,這裡看到的就是改過的版本)。

- 含派工詞觸發標記 `LUMOS-IMPACT:` 的真實派工:**39 筆**(集中在 `26a6b57a...jsonl` 裡的多輪代碼審/設計審——`lens-stage0`、`架構對齊席`、`r2 defender`、`r3 s1 通才席` 等真實審查輪次,不是我這次稽核自己觸發的)。
- 這 39 筆裡,`input` 內容包含 hook **實際注入**的文字 `本次改動的固定席節點`(`_LENS_HEADER` 的核心片語)的:**0 筆**。
- 全庫(含所有 sidechain 子代理逐字稿)搜尋 `自動附加` 或 `LUMOS-LENS`,`isSidechain=true` 的訊息裡:**0 筆**。

也就是說:39 次觸發條件成立的派工,**沒有任何一次能在逐字稿裡找到 hook 真的把節點清單塞進子代理看到的內容**。這與圖譜自己的紀錄互相印證——`Projects/loop數據收集_計劃.md` 裡記著另一個更早的人工標記格式:「★清單早就算得出來★...這仍是假設不是證據(**同格位 08-29 上線後 0 執行**);REVISIT:2026-10-03 grep 派工單看標記出現率」——這條 REVISIT 排定 10 月才要查,但用今天的資料提前查一次,答案是**目前為止仍是 0**。

**判定:③空轉**。機制設計完整、有 28+ 條單元測試、有一次上線示範重放成功(§6 提到的近名節點事故重放),但在**真實**代碼審派工的 39 次機會裡,一次都沒有觀察到子代理真的收到過注入內容——樣本雖然只涵蓋這台機器上看得到的逐字稿,但覆蓋的正是這個專案自己過去幾週最活躍的審查迴圈(lens-stage0、code-codex 系列),不是隨便抽到的冷門角落。

---

## 12. 其他發現

**a. `governance/autonomous_loop/replay_weekly.py` 的輸出被自己的呼叫端截斷,砍掉最關鍵的欄位**——見 §2。`autonomous-loop.sh` 用 `head -1 | cut -c1-160` 記日誌,而 Python 端 dict 順序把 `red`/`stale`/`errors` 排在後面,已知的 `unfreezable` 清單往往就把 160 字元用完。這是一個「設計了但沒被自己的日誌格式接住」的例子:機制本身可能有抓到紅燈,但連開發者自己看 `autonomous.log` 都看不到。

**b. `.lumos/testmap.json` 與「陳舊三訊號」守衛互相矛盾的可能性**:守衛程式碼存在且邏輯完整(§8),但因為沒人在這 28 天內呼叫過 `testmap affected`,這個守衛本身也從未被執行過一次——**一個檢查「地圖過不過期」的機制,本身也過期了、也沒人管**,是雙重空轉。

**c. `governance/backlog-archive.jsonl` 為稽核過程中新出現的未追蹤檔**(`git status` 顯示 `??`),推測是背景執行的自主迴圈 backlog 衰減腳本在稽核期間自動產生——不是我改的,但提醒:本次稽核視窗內 autonomous-loop 仍在背景真實運作(佐證 §4 的每日消費結論)。

**d. 數字對不上的例子**:`compose-metrics-adapter` 的 Verification 筆記寫「KDS 真機端到端(21 non-skippable baseline...)」,但 §9 machine-level 掃描找不到任何 `compose-baseline.json` 存在於這台機器上任何一個專案——「21」這個數字目前無法用任何現存檔案覆核,只能相信筆記文字本身,這正是知識圖譜「查得到才算」原則要提防的情況:**筆記講的驗證曾經發生過,但佐證檔案已經不在了,無法重驗。**

---

## 總表

| # | 機制 | 判定 | 一句話 |
|---|---|---|---|
| 1 | doctor 二十多道檢查 | ①(帶但書) | 5 道從沒響是條件未成立非死碼;check-s 長期忽略但有批次清帳先例 |
| 2 | 週回放 replay_weekly | ②言過其實 | 真跑但只跑 2 次、帳面截斷看不到紅燈欄位、一輪抽樣還沒跑完 |
| 3 | 情境探針週抽 | ③空轉(對修復而言) | s15-new-verification 已知失敗 5+ 天,筆記承認但選擇繞過不修 |
| 4 | 治理日報 | ①名副其實 | 稽核題目的假設本身是錯的,dry-run 迴圈每天真消費 |
| 5 | L2 bypass 帳 | ③空轉 | 帳記錄正確,但無任何「看帳做決定」的下游消費 |
| 6 | entry-latch/escape-log | ③空轉(escape-log)/①(entry-latch 單一驗證) | 逃逸帳 0 筆(專案自己承認);攔截帳 5 天內僅 1 筆自我指涉 |
| 7 | cochange/delguard | ③(delguard)/④(cochange) | delguard 63 次全因超時放行、調參無效;cochange 抓到真問題但零留痕 |
| 8 | guard kill 等 7 指令 | 混合 | testmap/link-candidates 空轉;kill/signoff/decision_refs 低頻但真實 |
| 9 | linter 橋 | ③空轉 | code 自己承認自動路徑不跑;兩個外部消費專案均無跟進痕跡 |
| 10 | valid_under/archive | ①(帶但書) | 欄位紀律好,但機制年齡不足 90/180 天,未受過真實考驗 |
| 11 | dispatch-lens | ③空轉 | 39 次真實觸發,0 次確認注入內容送達子代理 |
