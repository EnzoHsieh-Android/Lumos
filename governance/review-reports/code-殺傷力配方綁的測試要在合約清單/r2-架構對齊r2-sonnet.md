severity: minor

分層與依賴(問1):新函式全落在 `scripts/lumos:15000-15150` 的殺傷力配方區,依賴方向照舊(配方區 -> 共用工具 _sh_quote `scripts/lumos:438`、_path_special_chars `scripts/lumos:32427`、_kill_esc `scripts/lumos:14786`、_kill_show `scripts/lumos:14792`)。doctor 段只多一行呼叫(`scripts/lumos:3388` 一帶),不跨層直呼。_KNOWN_GATES 與 _GOV_LOCAL_PAIRS(`scripts/lumos:1319` 一帶)都補了 check-p2t,與 check-p2s 同做法。提醒走 stderr「⚠ 提醒:」、落帳走 gov_events {gate,kind:warned,hard:False,nodes},與 `_kill_add_warn`、doctor P2s 段一致。上一輪兩個修正(_kill_cmd_arg 內用既有 _sh_quote、_kill_find_contract 讓 kill-add 與 audit 共用)方向對,沒有新增第二套跳脫或第二套定位。

## F1 不能貼的字的處理方式有兩套
severity: minor
blocking: 否
引句:「return None if _path_special_chars(s) else _sh_quote(s)」
說明:既有 `_kill_node_arg`(`scripts/lumos:14683`)遇控制字元時回佔位字 `'<筆記名含控制字元,先改檔名>'`,指令照樣印出;新的 `_kill_cmd_arg` 遇控制字元回 None,呼叫端再各自分支成「不印可貼的指令」加一段 unsafe 文字(`_kill_binding_msg` 內三處分支)。同一份提醒裡節點名走佔位字、合約片段與平台名走 None 分支,是同一個問題兩種收法。結構對、安全性等價,只是慣例分岔;建議之後讓 `_kill_cmd_arg` 也回佔位字、省掉呼叫端的 None 分支,或在註解寫明為何不同。

## F2 合約行定位只收斂了 kill-add 與 audit,bind 還是自己一套
severity: minor
blocking: 否
引句:「kill-add 定位與 doctor 對回合約行共用這一支,不另寫第二套。」
說明:`cmd_guard_bind` 的定位(`scripts/lumos:14576`)仍是手寫迴圈,且去標記用 TEST_REF_RE 而非 INV_TAG_RE;新註解宣稱「不另寫第二套」,但 bind 這條同族路徑沒併。bind 去標記的集合不同可能是刻意的(它要改的就是 [test:]),但沒在 `_kill_find_contract` 註解裡交代。另外 `_doctor_p2_unbound` 把 warn_soft 區域函式當參數傳入(`scripts/lumos:1669` 定義在 run_doctor 內),而 P2s 段是直接內嵌在 run_doctor,屬抽法不同;結構可接受,僅記錄。

不對齊共 2 條,其中 major 0 條
