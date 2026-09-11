severity: major

## 三問逐答

**1. 分層與依賴方向**

新碼的分層跟鄰居一致:兩支 hook(`scripts/hooks/pre-commit:122-126`、`scripts/hooks/pre-push:193-204`)都只呼叫 `lumos home check`、印訊息、判 rc——不在 shell 裡重寫任何判定邏輯,跟 `cmd_cochange_check`/`cmd_delguard_check` 被 hook 呼叫的方式同構(注意 hook 內文自己就寫「這裡跟 cochange / delguard 一樣只呼叫、不碰內容」,`scripts/hooks/pre-commit:115-121`)。`scripts/lumos` 內部新增的 `cmd_home_check` 也是先驗證環境、組資料,再呼叫一批 `_nodehome_*` 私有函式——跟 `cmd_cochange_check`(呼叫 `_cochange_*`)是同一種 cmd/_helper 分層。讀版本策略(直讀磁碟、不同才走 `git show`)明確引用 `_vendored_state`(`scripts/lumos:13519-13554`)既有先例(見 `_nodehome_reader` docstring)。這條沒有發現跨層直呼。

**2. 命名與錯誤處理**

`_nodehome_config` 逐句對照 `_stack_questions_config`(`scripts/lumos:16394-16421`)——鍵名同樣叫 `mode` 不叫 `gate`(同一句註解理由)、bool 單獨擋、壞值退預設並留 warning,連命名手感都一致,這條做得很好。訊息也遵守「白話三段式」(發生什麼→為何在意→指令獨立一行),例如 `scripts/hooks/pre-push:200`。但有一處跟緊鄰的既有寫法不一致:`cmd_new` 裡舊的 `plan_rels`/`sys_rels` 寫回(`scripts/lumos:12478-12493`)用 `try/except (OSError, ValueError, RuntimeError)` 包住 `cmd_append`,失敗也要印「筆記建好了,但…」再繼續處理其餘項目,最後才用 `rc_side` 彙總回傳——這條 try/except 是先前一輪架構審查特地加的(見同段註解「第四輪架構席」)。新加的 `--code`/`--responsibility` 寫回(`scripts/lumos:12469-12475`)完全沒有 try/except,只看 `cmd_append`/`cmd_set` 的回傳值,而且第一支寫失敗就整段 `return 2`,不會像鄰居那樣把剩下的項目都跑完再彙總。`cmd_set`/`cmd_append` 內部走 `atomic_write_verify`/`_vault_write_lock`,跟鄰居程式碼同樣可能丟出 `OSError`/`RuntimeError`——不接住的話這段會直接讓例外往上炸穿,而不是照鄰居的規矩印「筆記建好了,但…」。

**3. 第二種做法**

檢查了 prompt 點名的四個典型(讀 git 的包裝、設定讀法、反引號抽取、照日期生效的機制):讀 git 全部走既有的 `_lens_git`,沒有另包;設定讀法完全比照 `_stack_questions_config`;反引號抽取不但沒有另寫,還把 `_refcheck_scan` 裡原本內嵌的抽取邏輯拆成共用函式 `_node_code_ref_tokens`(`scripts/lumos:17371` 附近),讓 `_impact_reverse_lookup`(`scripts/lumos:20596` 附近)也改呼叫它,是在**減少**重複;處置閘照日期生效的機制(`_LANDING_GATE_SINCE`/`_disposal_landing_step`)逐句仿造 `_CLAUSE_GATE_SINCE`/`_disposal_clause_step`,連註解都寫「同 _CLAUSE_GATE_SINCE」。這四類都合格。但在這四類之外,抓到兩處新的「第二種做法」,詳見下面 F1、F3。

## 發現

### F1 計劃落點鏡頭自己重寫了一套合約行偵測,沒有用既有的 `_lens_contract_lines`
severity: major
blocking: 是 — 這個 repo 已經有 `_lens_contract_lines(text)`/`_lens_contract_rows(text)`(`scripts/lumos:21721-21750`),專門用 `INVARIANT_RE`/`CHECKPOINT_RE`/`IRREVERSIBLE_RE` 這三個既有正規式抓 KEY 行裡的合約標記,而且就在同一支 `cmd_dispatch_lens_spec` 附近(不到 900 行之外)。新加的 `_nodehome_landing_sizes`(`scripts/lumos:22594-22622`)要算「這篇有幾條合約」時,卻自己另外寫了一條正規式 `re.match(r"\s*KEY:★(INVARIANT|IRREVERSIBLE|CHECKPOINT)★", l)`,而不是呼叫 `len(_lens_contract_lines(text))`。兩套判法還不等價:`INVARIANT_RE` 允許 `KEY:` 後面接一段 `(...)` 再接 `★INVARIANT★`(本圖譜實際筆記常這樣寫,例如本次 diff 自己新增的 `KEY:處置閘第六步「落點」(2026-09-11,…)`),新規式要求 `KEY:` 後直接貼 `★`,遇到帶括號說明的 KEY 行會算漏——這正是「兩套算法一定分岔」的具體案例,而這句話本來就是這份 diff 自己(`Systems/每支檔有家.md`)在講「別人的檔」抽取時強調的原則,這裡卻沒有對自己套用。
引句:「contracts = sum(1 for l in summ.splitlines() if re.match(r"\s*KEY:★(INVARIANT|IRREVERSIBLE|CHECKPOINT)★", l))」
佐證 file: `scripts/lumos:22618`(既有做法對照:`scripts/lumos:21721-21730`)

### F2 `cmd_new` 新增的 `--code`/`--responsibility` 寫回,沒有照鄰居的 try/except+彙總慣例
severity: minor
blocking: 否 — 命名與整體結構(先驗證再建檔、失敗印「筆記建好了,但…」)跟鄰居一致,只有例外處理的收斂方式不同,不構成第二種做法。
引句:「筆記建好了,但 --code 有一支沒寫進 about_code」
佐證 file: `scripts/lumos:12469-12475`(既有做法對照:`scripts/lumos:12478-12493`,含「第四輪架構席」加 try/except 的理由註解)

### F3 `home check` 對「--staged 與 --diff 同給」採用跟 `cochange check` 不同的解法 ⚠
severity: major
(⚠ 判不準)
blocking: 是 — 若成立即符合「引入第二種做法」;但 diff 內註解顯示這是「第二輪外家席」已經討論過的刻意決定,不是疏漏,判準上仍記為 major 供收斂時複核。
本專案既有的 `--staged`/`--diff` 雙模式先例是 `cochange check`:兩個都給的時候不報錯,說明白寫著「--diff 優先」,是「靜默選邊」的路線。新的 `home check` 改用 `argparse` 的 `add_mutually_exclusive_group()`,兩個都給直接 rc2 用法錯誤,而且旁邊註解明講是刻意不跟 `cochange` 那條路線一樣。這是同一個 CLI 裡,對結構相同的「雙模式旗標衝突」問題給出兩種不同解法。
引句:「兩個同給=用法錯誤(rc2),不靜默選邊(第二輪外家席)」
佐證 file: `scripts/lumos:25607`(既有做法對照:`scripts/lumos:25599-25600`)

### F4 推送前波及範圍多了一套獨立的「找起點」演算法 ⚠
severity: minor
(⚠ 判不準)
blocking: 否 — 有明確的技術理由(擋新違規的閘不能容忍把 1900 多個提交當新改動),且沒有另包 git 呼叫(仍用既有 `git` 直呼慣例),證據不夠強到判 major。
`scripts/hooks/pre-push` 原本只有一套算「這次推送範圍」的邏輯(`_range`,新分支/物件缺失一律退到空樹兜底,`scripts/hooks/pre-push:164-172`)。新加的 `_hrange`(`scripts/hooks/pre-push:178-192`)為了不把整段歷史當新違規,另外用 `git rev-list --not --remotes` 找「不在任何遠端分支上的提交」當起點,是同一支腳本裡第二套獨立的範圍推導演算法,原本沒有這種「找最早未發佈提交」的寫法可對照。
引句:「★新分支不沿用上面的空樹兜底★」
佐證 file: `scripts/hooks/pre-push:178-192`(既有做法對照:`scripts/hooks/pre-push:164-172`)

總結:最高 severity major,blocking 共 2 條
