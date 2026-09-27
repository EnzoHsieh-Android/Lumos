severity: major

〈白話〉〈依據〉已讀,無 finding。

〈PRIOR-ART / RETIRE-IF / REVISIT〉已讀——PRIOR-ART 聲稱「全部借本 repo 既有形狀,不發明新做法」並逐條列出①-⑤,但唯獨漏列本 repo 已有的檔案鎖形狀,見下方 F2。

## F1 治理帳鎖只蓋兩個寫入器,漏掉第三個既有寫入器

severity: major
blocking: 是 —— 不改的話,S7 承諾的「兩個行程同時寫,兩筆都完整落帳」只在「note-shape × code-loop」這一種組合成立,note-shape/code-loop 與 anchor-approve、spec-gate、escape-auto、delguard、doctor --ci 同時寫時仍會壞行,而這些都是本機真實會用到的指令,判定結果可能悄悄消失且沒人知道。

引句:「兩個行程同時寫可能產生壞行,而讀端遇到壞行會靜默跳過」

- file: `scripts/lumos:856-932` `_gate_event` 目前是 `open(docs / ".governance-log.jsonl", "a", ...)` 直接 append,沒有鎖;spec 打算改成這支連同 `_codeloop_gov_log` 一起拿鎖。
- file: `scripts/lumos:28796-28819` `_codeloop_gov_log` 寫的是 `Path(repo_root) / "docs" / ".governance-log.jsonl"`——與 `_gate_event` 是同一支檔,同樣沒有鎖。
- file: `scripts/lumos:951-973` `_append_governance_log` 是第三個獨立寫入器,寫的是 `vault.parent / ".governance-log.jsonl"`(同一支檔),同樣直接 `open(path, "a")` 沒有鎖,spec 全文沒有提到這支函式。
- file: `scripts/lumos:556` design-loop、`scripts/lumos:6129` spec-gate-run、`scripts/lumos:9583` escape-auto-failed、`scripts/lumos:19798` anchor-approve、`scripts/lumos:23796,23809` delguard、`scripts/lumos:28855` bound-tests——這六個呼叫點全部經 `_append_governance_log` 寫進同一支帳,全部不在 S7 的鎖保護範圍內。
- file: `docs/lumos-toolchain-knowledge/Projects/筆記形狀擋_計劃.md`(即本 spec)〈回退〉第 4 點另有一句:「它讓舊的寫入者也不會交錯」——這句話宣稱共用鎖涵蓋「舊的寫入者」(複數、泛稱),與〈治理帳寫入加鎖〉段落明寫「只鎖 `_gate_event` 與 `_codeloop_gov_log` 兩者」互相矛盾:上面列的六個既有呼叫點都是「舊的寫入者」,但都經 `_append_governance_log`,不在這兩者之列。

編號重現:
1. 使用者 A 在某工作目錄執行 `git commit`(觸發 note-shape,經 `_gate_event` 取鎖後寫一行 blocked/passed 事件)。
2. 同一秒使用者 B 在同一個工作目錄執行 `lumos anchor approve`(經 `_append_governance_log` 直接 append,不取鎖、不等 A 的鎖)。
3. 若 B 的 `write()` 落在 A 持鎖寫入那一行 JSON 的中途(spec 自己在同一段承認「兩個行程同時寫可能產生壞行」正是這個前提),兩筆合併成一行壞 JSON。
4. 讀端(`lumos gov`)遇到壞行靜默跳過(spec 原文承認),A 或 B 這筆判定紀錄消失不留痕——而 note-shape 現在是「每次提交都要寫 blocked/passed」(收窄前只有少數事件會寫帳),等於把寫帳頻率拉高到「每個人每次 commit/push」,反而放大了這個沒堵住的洞被踩到的機率。

## F2 鎖本身的實作細節未指定,且漏列本 repo 既有的鎖形狀

severity: major
blocking: 是 —— 沒有指定鎖檔位置、逾時秒數、過期回收機制,實作者字面照做很可能重新發明一把沒有「陳屍鎖自動接手」的鎖;一旦持鎖程序中途被殺,鎖檔殘留會讓後續所有提交/推送永遠卡在等鎖,直到有人手動介入——這正是本輪要看的「鎖檔殘留、鎖等很久」情境。

引句:「改成兩者寫入時拿同一把治理帳檔案鎖」

- file: `scripts/lumos:14229-14274` `_vault_write_lock` 是本 repo 既有、經過三輪代碼審打磨的檔案鎖範式:鎖放 `~/.cache/lumos/vault-lock/`(不可信目錄會退回筆記庫自己裡)、逾時 60 秒 `raise RuntimeError`、可重入(`_VAULT_LOCK_HELD`)。
- file: `scripts/lumos:28183` `_excl_lock_try(lock, stale_sec)` 是這支鎖真正的原語:獨佔建鎖檔、寫程序編號、過期(逾 `stale_sec`)用換名原子接手;另一個既有用戶是派工鏡頭快取鎖(`_LENS_LOCK_STALE_SEC`,約 `scripts/lumos:28242-28243`)。
- file: `scripts/lumos:14233-14234` 這支函式的說明原話留有教訓:「第三輪另開了一套 flock,是專案裡第二種鎖」——本 repo 過去代碼審已經抓過「同一件事另開第二套鎖機制」這個錯誤形狀,而 PRIOR-ART 段落完全沒提到要沿用 `_excl_lock_try`,也沒提到不沿用的理由。
- spec 說「等鎖逾時照既有 rc 協議印『擋下:…』回 2,不丟裸例外」,但既有的 `_vault_write_lock` 逾時本身就是直接 `raise RuntimeError`(裸例外,要靠呼叫端包 try/except 才轉成 rc2,見 F3)——spec 沒有講清楚新鎖打算重用哪一段行為、逾時秒數多少、鎖檔放哪裡、多久沒動就當作死掉自動接手,這些都是「鎖檔殘留」發生後決定損害範圍的參數。

編號重現:
1. 實作者依字面「拿同一把治理帳檔案鎖」寫一支最簡單的鎖(例如 `open(lockpath, "x")` 排他建立、寫完 `os.remove`),沒有比照 `_excl_lock_try` 做「逾時當作死掉、換名原子接手」。
2. 某次 `lumos code-loop pass` 在持鎖期間被使用者 Ctrl-C、CI runner 逾時 SIGTERM、或機器斷電殺掉,鎖檔沒有被移除。
3. 之後同一個工作目錄裡任何人執行任何一次 `git commit`(note-shape 現在每次提交都要落帳)或 `lumos code-loop pass/skip` 都會卡在等鎖,而且沒有過期回收路徑——所有後續提交/推送在逾時之後統一印「擋下」回 2,實質上等於整個團隊被鎖死,直到有人找到並手動刪掉那支鎖檔。
4. 這條路徑不是臆測的邊角案例:spec 自己點名的兩個寫入者之一(`_codeloop_gov_log`)目前寫入完全不到 1 秒(單次 append),按既有 `_VAULT_LOCK_STALE_SEC=30` 秒的判準,「30 秒還沒放掉當作死掉」這條經驗值合理,但 spec 沒有講新鎖要不要照抄這個數字——不寫清楚,實作者無從得知這個數字的來源與用意,容易憑感覺另定一個,而且很可能忘了做過期接手。

〈做法〉的〈範圍與行〉〈兩條規則〉已讀,無 finding(推送前新分支起點算法核對 `scripts/hooks/pre-push:216-233`,與 spec 描述一致;CI 段落宣稱「那一步要抓完整歷史」,查 `.github/workflows/ci.yml:16` 已是 `fetch-depth: 0`——GitHub 官方對這個參數的說明是抓「所有分支與標籤的完整歷史」,`refs/remotes/origin/*` 會涵蓋全部分支,不是只有正在測的那一條,不會出現 CI 只看得到單一分支、與本機算出不同範圍的問題)。

## F3 code-loop pass/skip 呼叫點目前沒有既有 try/except,鎖逾時會裸例外炸穿

severity: major
blocking: 是 —— 恰好是 S7 指名要測的「一個 note-shape、一個 code-loop」那條路徑,鎖逾時之後不會如 spec 所說印「擋下:…」回 2,而是 Python 未捕捉例外的裸 traceback,直接違反 spec 自己這句承諾。

引句:「等鎖逾時照既有 rc 協議印」

- file: `scripts/lumos:30325-30334` `cmd_code_loop` 的 `subcmd in ("pass", "skip")` 分支直接呼叫 `_codeloop_write(...)` 與 `_codeloop_gov_log(...)`,兩者外面完全沒有 `try/except` 包裹。
- file: `scripts/lumos:32300-32328` 這支檔真正示範「例外轉乾淨 rc2」的地方是 `decision-refs`/`decision-reindex`/`decision-add` 等 dispatcher,固定寫法是 `except (ValueError, RuntimeError, OSError) as e: print(f"擋下:{e}", file=sys.stderr); return 2`——但這層保護只包住那幾個 decision 系列指令,不包 `cmd_code_loop` 的 pass/skip 分支。
- 全檔搜尋 `except RuntimeError` 只有一處(`scripts/lumos:2718`,是掃描量超上限的另一件事,與治理帳寫入無關),代碼庫裡沒有「統一兜底把任何 RuntimeError 轉成 rc2」的機制——每個呼叫點各自負責包一層,而 code-loop pass/skip 這個呼叫點現在沒有。

編號重現:
1. 兩個人同時對同一個工作目錄執行 `lumos code-loop pass`(或一人 `pass`、另一人同時 `git push` 觸發 note-shape),兩者都要對 `docs/.governance-log.jsonl` 取同一把鎖。
2. 依 F2,鎖逾時的具體秒數與行為未定,但只要真的逾時,若新鎖沿用 `_vault_write_lock` 的做法(逾時 `raise RuntimeError`),這個例外會從 `_codeloop_gov_log` 內部一路往上炸穿 `cmd_code_loop` → `main()`,因為 30325-30334 這段沒有任何 `try/except` 接住。
3. 使用者看到的不是 spec 承諾的「擋下:…」白話訊息、rc=2,而是 Python 的原始 traceback,rc 是 Python 對未捕捉例外的預設值(1),與 spec 逐條要求的錯誤協議不符,而且恰好落在 S7 指名要驗的兩個呼叫者之一上。

〈紀律範本改寫〉〈消費專案的 CI〉已讀,無 finding。

〈條款〉S1–S6、S8、S9 已讀,無 finding;S7 見上方 F1、F3——S7 字面驗收只測「一個 note-shape、一個 code-loop」這一組,即使照樣通過,也不代表 F1 指出的其餘寫入器(anchor-approve、spec-gate、escape-auto、delguard、doctor --ci)组合安全。

〈回退〉已讀——第 4 點「治理帳的共用鎖留著:它讓舊的寫入者也不會交錯」與 F1 的內部矛盾已在 F1 引用,其餘各點無 finding。

〈實務隱患〉已讀——「資源併發」那行寫「寫治理帳走共用鎖」,對照 F1、F2、F3 的查證,這句話只在「note-shape 與 code-loop 兩者互寫」這個最窄的組合下成立,其餘組合與鎖本身的失效模式都沒有被這句話覆蓋到,建議這裡誠實列出範圍;其餘小節(守衛面、已排除三項)無 finding。

〈誠實界線〉已讀,無 finding。

【圖譜節點逐條判】
- Issues/筆記把程式現況寫進脈絡而漂移_rtb實測回饋:讀過 d1–d7,spec 對 d1(不留存程式碼推得出的東西)、d3(現況出口收窄成 `[src:]`)、d7(拆兩份計劃)的引用與節點內容一致,不影響它宣稱的行為——它是決策紀錄,本身不被這份設計執行,沒有合約可破壞。
- Systems/每支檔有家:節點的 `about_code` 列 `scripts/lumos`、`scripts/hooks/pre-commit`、`scripts/hooks/pre-push`,沒有 ★INVARIANT★/★IRREVERSIBLE★/★CHECKPOINT★ 或帶齊四欄的 `RULE:` 行(逐行查證,只有 `KEY:` 行)。本設計借用它的「起點算法」但不改動它自己的判定邏輯(`cmd_home_check`/`_nodehome_clamp_base` 等一行未動),不影響它宣稱的行為。

總結:最嚴重 severity 是 major;blocking 共 3 條(F1、F2、F3)。
