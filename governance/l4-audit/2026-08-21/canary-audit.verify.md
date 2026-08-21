# canary-audit 主張驗證

C1 [✅] `record` 的 `kind` choices 含 `caught`/`missed`/`none` | 證據: scripts/lumos:14246 `cr.add_argument("kind", choices=("caught", "missed", "none"))`

C2 [✅] panel/light/循序(legacy)/verify-progress/settle 五處判定皆已納入 `kind=none`,且嚴重度合取不盲讀 none 列 | 證據: scripts/lumos:3568-3596(panel:`_panel_round_conjuncts` 輪有效判斷讀 none_recs、maxsev 讀 `caught_recs + none_recs`)、scripts/lumos:4423-4425(light ratchet 讀 `kind in ("caught","none")`)、scripts/lumos:4460-4461(legacy/循序 K-streak `good()` 讀 `kind in ("caught","none")`)、scripts/lumos:4166-4168(verify-progress `caught_ok`)、scripts/lumos:4263-4269(settle `is_caught_round`)

C3 [✅] `t_loop_panel_none_kind` 存在且涵蓋三向斷言(有效/不盲/單席仍無效) | 證據: scripts/test_lumos.py:9312-9358(①none×2乾淨→rc0 於 9333-9337;②none 帶 major → rc1 且斷言 `falsification+ODC(存活 max≤minor): ✗` 於 9348-9351;③單席 none → rc1 於 9353-9358)

C4 [✅] `lumos gov` 仍將 `.canary-log.jsonl` 當第 4 源唯讀彙整,不做判定/gate 邏輯 | 證據: scripts/lumos:3002-3011(`# 第 4 源:canary 審計留痕...` `load(".canary-log.jsonl", ...)`);`cmd_gov` 全函式(scripts/lumos:2953-3132)只印報表無 return 1/2 之類 gate 判定

C5 [✅] `cmd_canary` 本體與 `record` 子命令未被移除 | 證據: scripts/lumos:3195(`def cmd_canary(...)`)、scripts/lumos:14238-14246(`cp = sub.add_parser("canary", ...)`、`cr = csub.add_parser("record", ...)`)

C6 [✅] dedup key 第 5 鑑別子用 `r.get("token","")` 而非 `r["token"]` | 證據: scripts/lumos:3024-3025(`# ...必須用 .get 不可 r["token"]` `k = (r["commit"], frozenset(r["nodes"]), r["gate"], r["kind"], r.get("token", ""))`)

C7 [✅] `--token` 未給時用 `secrets.token_hex(4)` 隨機鑄造,非時間戳 | 證據: scripts/lumos:3205-3207(`import secrets` `token = "CANARY-" + secrets.token_hex(4)   # 隨機,非時間戳(同秒不撞)`)

C8 [✅] schema 至少含 `{ts,kind,auditor,token,note}`,另有 `--loop`/`--severity`/`--scope-lines`/`--canary-type`/`--probe` 選配欄 | 證據: scripts/lumos:3208-3209(基本欄)、3210-3211(loop)、3214-3217(canary_type/probe)、3231-3232(severity)、3266-3272(scope_lines 屬 tokens/wallclock_min/scope_lines 選配組)

C9 [✅] canary 寫入獨立 `<vault.parent>/.canary-log.jsonl`,與 doctor 用的 `.governance-log.jsonl` 不同檔 | 證據: scripts/lumos:3353(`path = env.vault.parent / ".canary-log.jsonl"`)對照 scripts/lumos:2988(`load(".governance-log.jsonl", ...)`,cmd_gov 內以不同檔名讀取)

C10 [✅][歷史] 協議核心流程(偷植純加性 canary、唯一 token、不告知、caught/missed 判決、missed 判決作廢換新 canary)文字仍保留於設計稿 | 證據: docs/design/2026-06-19-canary-audit.md:23-27

C11 [✅][歷史] v1 canary 僅收純加性瑕疵、明確禁止「與另一節矛盾的需求」類非局部瑕疵,條款文字仍存 | 證據: docs/design/2026-06-19-canary-audit.md:23,61,77(「v1 只收純加性瑕疵,禁矛盾需求等非局部型」)

C12 [✅][歷史] panel 變體(N 席各配不同 canary、漏抓自己那個從投票剔除)文字描述仍存 | 證據: docs/design/2026-06-19-canary-audit.md:29(「panel 變體:若一輪派 N 個獨立審計員,每個各給自己的 canary;漏抓自己 canary 的那個,從投票中剔除」);程式碼面僅見型別隨機分派邏輯(scripts/lumos:4859-4870),未見「剔除席位」的機械實作,與主張「僅文字描述、從未機械實作」一致

C13 [✅][歷史] d4(2026-08-04)canary 降級為觀測:disposal 閘不消費 caught/missed,missed 不作廢 findings | 證據: scripts/lumos:9391(docstring「★canary caught/missed 不進合取(d4:觀測非閘;missed 不作廢 findings)★」)、scripts/lumos:9536-9542(「── canary 觀測(不進合取——d4;none=停用制無植入輪——d5) ──」,僅列印不進 `fails`)

C14 [✅][歷史] `--canary-type`/`--probe` 搭配 `canary-stats` 做型別×探針×caught 報表,D 案(型別記錄攢滿 15 筆才開工)文字與程式碼仍在 | 證據: scripts/lumos:4088-4126(型別×探針×caught 表組裝)、scripts/lumos:4121-4123(「attr 攢滿 15 筆=D 案開工條件」印出行)、scripts/lumos:14323(`lcs = lsub.add_parser("canary-stats", ...)`)

C15 [✅][歷史] `loop next` plant-canary 階段印 `scope_cap`(軟上限 1800 行/≈30K token),`--scope-lines` 超標標記 `scope_oversize` | 證據: scripts/lumos:4592(`_CANARY_SCOPE_SOFT_CAP_LINES = 1800`)、scripts/lumos:4913-4922(`out["scope_cap"] = ...超過 1800 行...`)、scripts/lumos:3273-3278(`cmd_canary` 內 `scope_lines > _CANARY_SCOPE_SOFT_CAP_LINES` → `rec["scope_oversize"] = True`)

✅15 ❌0 ❓0 ⏭0
