severity: minor

整體結構對齊,沒有第二種做法,也沒有跨層直呼。唯一不齊的是一處 PITFALL 寫法,屬 minor。

**問 1 分層與依賴方向:對齊**

- `scripts/lumos` 只動 `_GOV_FIELD_TYPES` 這張型別表和它上方的註解。呼叫關係沒變:讀帳端 `_gov_event_types_ok` 照舊遍歷這張表。
- `run_id` 從 `dict.fromkeys(...(str,))` 拆出來,另立一條 `(str, int, type(None))` 的獨立項,形狀和既有的 `"round": (str, int, type(None))`(`scripts/lumos:18315`)一致。拆出後 `"secs"`、`"round"` 也都是各自獨立項,沒有新抽象。
- 測試端用既有的 `_ppc_sigint_default`(`scripts/test_lumos.py:85520`),以 `preexec_fn=` 帶入。同樣的呼叫端在 `31137`、`85535`、`86344`、`139086` 都有。
- 測試 `t_choice_kill_interrupt` 的 Popen 沒有多一層包裝,也沒有另寫一個還原 SIGINT 的函式。
- 引句:「+    "run_id": (str, int, type(None)),」
- 引句:「stdin=subprocess.DEVNULL, preexec_fn=_ppc_sigint_default)」

**問 2 命名與錯誤處理:對齊,有一處 minor**

- 測試斷言沿用 `t_ci_status_and_gov` 的 `check("…", cond, r.stdout[-400:])` 寫法。夾具也是同一種:`_ci_run(root, v, env, "gov", "--since", "9999")` 搭配 `log.open("a")` 追加一行 JSON。
- 這行 JSON 的欄位集和 `scripts/lumos:67094` 的 `_ci_record` 寫端(`run_id: None, attempt: 0, workflow: ""`)一致。
- PITFALL 行有 `[出處:]`、`[根因:]`、`[修法:]`、`[test:]`,必有鍵齊全,和 `Systems/測試執行器.md` 既有行同形。
- `[同族:]` 的寫法也跟上一條 SIGINT 的 PITFALL 一致。
- 不齊的一處:`reversibility-governance-ledger.md` 新增那條 PITFALL 的 `[修法:]` 裡寫了「代碼審 code-選擇點CI紅燈 r1 c1」。這是審查輪次的過程紀錄,專案 CLAUDE.md 說過程紀錄不寫進筆記。
- 鄰居的做法是把審查出處放在 `[出處:]` 裡(例:同檔的 `[出處:governance/review-reports/code-android寫法回合結束檢查/r6-資安-sonnet.md F1]`)。這裡是結構對、只有放的位置不同。
- 引句:「修法:run_id 收字串、整數與 null(ci-wait 等不到 run 時寫 null,代碼審 code-選擇點CI紅燈 r1 c1)」

**問 3 第二種做法:沒有**

- 沒有新增另一套 SIGINT 還原機制,也沒有新增另一種多型欄位的登記方式。
- 修補過的註解帶日期,承認過去疏漏。這和 `_GOV_FIELD_TYPES` 上方既有的「2026-10-01 對本 repo 八本帳逐欄統計過」是同一種寫法。
- 引句:「# 新增欄位時一起補進來,而且要核對各帳寫端會寫的值(含 null),不只看帳檔現存的行」

## a1 PITFALL 修法欄混入審查輪次紀錄
severity: minor
blocking: 否
引句:「修法:run_id 收字串、整數與 null(ci-wait 等不到 run 時寫 null,代碼審 code-選擇點CI紅燈 r1 c1)」

補充:r2-snapshot.patch 裡 `skills/lumos-project-notes/commands/INDEX.md` 有刪掉「改動選擇點」那列的變動,但 `r2-repair.patch` 沒碰這個檔。我查到主線 `e377a6a03` 的 INDEX.md 有 2 處 `choice-points`,`c478bdcb3` 是 0 處,所以這比較像主線超前造成的基底差異。我沒追查它的來源,也沒當作對齊問題列。

不對齊共 1 條,其中 major 0 條
最嚴重:minor;blocking 共 0 條
