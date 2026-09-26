severity: major

## F1 撤回擋下走「拿不到鎖印擋下、不拋例外」,但 `escape` 子指令的 dispatch 沒有其他寫入指令那層 try/except 可以借

severity: major
blocking: 是——照 spec 字面(「拿不到鎖時照其他寫入指令一樣印『擋下:…』」)去接既有模式,會漏接例外,使用者看到 Python traceback 而不是擋下訊息,直接違反 [S4]「拿不到寫入鎖時應印擋下訊息而不是拋出例外」這個有綁定測試的合約。

引句:「拿不到鎖時照其他寫入指令一樣印「擋下:…」,不讓例外直接冒出來」

file: `scripts/lumos:13789-13791` `_vault_write_lock` 搶不到鎖 60 秒後直接 `raise RuntimeError(...)`,本身不印任何「擋下」訊息、也不吞例外。
file: `scripts/lumos:31742-31752` `set`/`append`/`remove`/`new`/`self-audit` 這些「其他寫入指令」之所以能把 `RuntimeError` 變成「擋下:{e}」,是因為 dispatch 層(`args.cmd in ("set","append","remove")` 等分支)外面包了 `try: ... except (ValueError, RuntimeError) as e: print(f"擋下:{e}", ...); return 2`——這層 try/except 包在 argparse dispatch,不在 `cmd_set` 內部。
file: `scripts/lumos:31663-31666` `args.lcmd == "escape"` 直接 `return cmd_loop_escape(env, ...)`,dispatch 這裡完全沒有 try/except 包著。`cmd_loop_escape` 本體(9404-9536,manual/list/auto 三分支)裡也沒有任何 `try/except RuntimeError`。

結果:現有「其他寫入指令」能把鎖逾時變成擋下訊息,靠的是它們掛在 `set`/`append`/`remove`/`new`/`self-audit` 這幾個有 try/except 的 dispatch 分支下;`escape` 這個子指令從一開始就不在這個保護傘裡(現有 `_auto_escape` 已經在用 `_vault_write_lock`,今天鎖逾時一樣會讓 `--auto` 直接噴 traceback,是既有缺口)。spec 只講「照其他寫入指令一樣」,沒有指名要在哪一層接:如果實作者依樣把 `--withdraw` 的「讀帳確認目標→寫入」包進 `_vault_write_lock`、卻沒有另外在 `cmd_loop_escape` 內部(或 dispatch 的 `args.lcmd == "escape"` 那行外面)自己包一層 try/except,S4 這條就會在鎖逾時的邊界情境下失敗——而這正是 spec 特別點名要防的情境。

需要在條款 S4 旁邊明講:要嘛在 `cmd_loop_escape` 的 `--withdraw` 分支自己包 `try/except RuntimeError`(印擋下訊息、回 2),要嘛把 `args.lcmd == "escape"` 那行也納入 dispatch 層既有的 try/except 保護傘——兩者選一,但 spec 目前的寫法會讓實作者以為「其他寫入指令都這樣、我複製那個模式就好」,而真正能接住例外的那層,`escape` 根本沒有掛上去。

已看,無:三份操作說明的逃逸記帳範例現況確實都只示範最基本的 `--stage/--severity/--desc`(scripts/lumos 之外查證:skills/lumos-design-loop/SKILL.md:61、skills/lumos-code-loop/SKILL.md:54、skills/lumos-project-notes/commands/06-代碼審與推送.md:27 均未提 --defect-ref/--sha/--missing-defect-ref),第二節「三份操作說明…同一次改動裡同步補上」的落點判斷正確,不是漏列;`_escape_rows_for` 五個呼叫點(scripts/lumos:2301 健檢撤除條件分子、6303 小改動閘歷史、7082 治理帳統計、9344 自動記去重、18551 問閘尾漏斗)spec 第三節逐一點名處理方式,經逐點比對函式簽名與呼叫脈絡,五個都對得上、沒有漏接的讀者,第四節新增的 escape-stats 與 rule-gap(自己讀法)兩個額外讀者也都在 S13/S14 的列舉裡;`_loop_anchor_tier`(scripts/lumos:17905-17908,帳上第一筆帶 tier 值)、`_plan_for_loop`(scripts/lumos:9293-9298)、`gate=design-loop kind=converged` 同時承接設計審與代碼審處置閘過關(scripts/lumos:8392/8495/9244/9684/9797/18584,經 r2 重現表驗證非重現不到、計劃第四節已補說明)、`gate=code-loop kind=passed` 恆 `nodes=[]`(scripts/lumos:28320-28327)這幾條機制層宣稱皆核對成立;審查帳 kind 值域 caught/missed/none(scripts/lumos:30705)與 S1 描述一致;實地核對「代碼審記到 major 自動記」的衍生迴圈名(如「驗收前提欄位可改」,unprefixed 只留 spec-gate 留痕、prefixed code- 版本才有真實 none 輪次)會落到 `plan` 分類而非 `design`——這與 section 一括號裡「所以自然落在 design 或 plan」的用語一致,是明講過的行為,不是被漏掉的邊界;三份操作說明的落點(lumos-design-loop/lumos-code-loop/lumos-project-notes)三個檔案路徑都存在且是正確的入口;第 2 輪指出的問題(撤回紀錄本身各讀者處理、手動記帳佐證、放行判定優先序、規格閘留痕誤判為審查紀錄)在本稿條款 S1/S3/S13/S14/S16 與第三節「讀的一側一律認得撤回紀錄」段落中都已寫成可執行判準,逐條核對過與程式碼現況相容,未見殘留。

最後一行總結:severity=major,blocking 共 1 條。
