severity: major

## F1 S18 度量:本機帳不存在或被刪時,只看版控帳的暖機護欄放行,走本機帳的閘被數成 0 筆而誤報「該撤」
severity: major
blocking: 是

引句:「# ★事件兩本合起來數,「最舊一筆」照舊只看版控帳★(治理帳例行紀錄分流_計劃〈做法〉6):」
file: `scripts/lumos:3976-3981`(`_doctor_metric_lines`);判定處 `scripts/lumos:3988-3994`;程式內建的建議話 `scripts/lumos:1304-1308` 區的 doctor 提醒「太大的可以直接刪,只影響本機統計」

失敗場景:
1. 一條有效 RULE 寫 `[retire:度量 check-s.warned == 0 近4週]`(撤除條件=四週內這道閘沒喊過)。`check-s`/`warned` 在 `_GOV_LOCAL_PAIRS` 名單上,所以分流後它的事件只寫本機帳。
2. 新機器 clone、CI 工作目錄、或照 doctor 自己的建議把 `.governance-local.jsonl` 刪掉:版控帳還在,而且裡面有 100 天前的舊事件,所以 `oldest`(只取版控帳)早於 cutoff,暖機護欄 `oldest > cutoff` 不成立、放行。
3. 本機帳不存在,`evs` 裡 check-s/warned 為 0 筆,`0 == 0` 成立,印出「這條限制該撤」。實際上兩週前那台機器剛喊過。
4. 最小重現(已實跑,臨時目錄 /tmp/gls-r1/rep:版控帳只有一筆 100 天前的 code-loop,本機帳有一筆 2 天前的 check-s warned,RULE 帶上述 retire):
   - 有本機帳:`[S18] ✓ 沒有成立的度量式撤除條件`
   - 把 `docs/.governance-local.jsonl` 移走:`[S18] ⚠ 1 條 RULE 的度量式撤除條件成立了…近 4 週 check-s.warned 0 筆(== 0 成立),這條限制該撤`
   同一個專案、同一批事實,只因本機帳不在就從沒事變成建議撤規則。分流前這些事件在版控帳,clone 下來就帶著,不會誤報。
5. 度量種類白名單含 `warned`、`hinted`,正好覆蓋本機名單裡的 check-* 與 note-shape,所以不是理論路徑。

## F2 沒有 docs/ 的佈局:忽略規則永遠補不上,doctor 叫人跑的 lumos update 是空操作
severity: minor
blocking: 否

引句:「- docs/ 不存在:什麼都不做(不建資料夾——獨立 vault 佈局建了反而改變「有沒有 docs/」的判斷)。」
file: `scripts/lumos:21034-21040`(`_ensure_docs_gitignore`);寫入端 `scripts/lumos:1526-1528`(`_append_governance_log` 用 `vault.parent`,不看 docs/)

失敗場景:
1. repo 的 vault 在 `root/foo-knowledge`(沒有 `root/docs/`),`vault.parent` 就是 `root`。`_append_governance_log`(doctor --ci、spec-gate)把本機帳寫到 `root/.governance-local.jsonl`。
2. `_ensure_docs_gitignore(root / "docs")` 看到 docs 不是資料夾直接 `return []`,根目錄 .gitignore 也沒有這兩行,檔案以未追蹤檔出現,`git add -A` 就進版控。
3. 之後 doctor 的 `_local_ledger_doctor_msgs` 會喊「沒被 .gitignore 忽略」並叫人「跑一次 lumos update 補忽略規則」,但 update 走到的就是 (2) 這個空操作,提醒永遠消不掉。⚠ 這種佈局在實務上有多少沒確認(測試只覆蓋 docs/<slug>-knowledge),所以只標 minor。

## F3 新的合讀函式又用 splitlines 切行,含 U+2028 的帳行整行被丟
severity: minor
blocking: 否

引句:「        for ln in text.splitlines():」
file: `scripts/lumos:8268-8280` 附近 `cmd_gov.load` 的註解已明講此坑並改走 `_drift_jsonl_parse`;新函式在 `scripts/lumos:1344-1355`

失敗場景:
1. 帳行用 `json.dumps(..., ensure_ascii=False)` 寫入,字串裡的 U+2028 原樣保留。
2. 一筆 `{"kind":"spec-gate-run","nodes":["Projects/a b_計劃.md"],...}` 寫進本機帳。
3. `_gov_ledger_rows_by_time` 的 `text.splitlines()` 在 U+2028 處把一行劈成兩段,兩段都 `json.loads` 失敗被跳過。實跑:一行這樣的帳,函式回 0 筆。
4. 後果:doctor S 的「最近一次規格閘」少那份計劃;`cmd_gov` 自己讀得到(走 `_drift_jsonl_parse`),兩個統計類讀者對同一本帳看到不同東西。舊程式也是 splitlines,所以不算新回歸,但新函式本來就是要給統計類讀者共用的那一支,應該跟 `cmd_gov` 同一種讀法。

## 已走過沒問題的範圍
- `_gov_routes_local`:gate/kind 非字串(None、list)在 `isinstance` 就回 False,進版控帳;hard 缺欄、0、None、"false" 用 `is False` 嚴格比對,全部進版控帳;`_gate_event_build` 已 `bool(hard)`,hard=0 傳進來變 False,配對命中才走本機,合理。code-loop、fix-check、design-loop 不在名單,實查 `_codeloop_gov_log`、dispositions 寫入點、`_fix_check_events`、`_escape_released_loops`、`_loop_close_stamps`、重寫血緣查詢、`_lint_new_autopass_count` 都直接寫/讀版控帳,未被分流影響。`test_autonomous_loop.py` 讀的 converged 也在版控帳。
- `_append_governance_log`:先寫版控批、後寫本機批,各自 try/except OSError;本機帳寫不進去(測試 S4)不會吞掉版控批,反過來版控批失敗也不擋本機批。同一批共用一個 ts 與 commit,沒有重複或漏寫。`_gate_event` 的 False 回傳約定兩本一致。
- 時間排序:台北 +08:00 與 UTC 混用實跑,00:30+08:00(=16:30Z)< 16:45Z < 17:00Z,順序正確;沒帶時區當本機時間;ts 缺、非字串、解析不了排最前;year-1 之類溢位被 except 接住;同時間保留讀入順序(版控帳在前),新事件都寫本機帳,所以「後寫者勝」方向對。
- 新舊互讀:舊帳裡留在版控帳的例行事件與本機帳是兩個不同事件,不會重複計數(沒有搬遷動作);cmd_gov 的 dedup 鍵含 commit/nodes/gate/kind,跨兩本相同事件才會折,語意同以前。舊版 lumos 看不到本機帳只是少看統計,不影響判定類讀者。
- `_ensure_docs_gitignore`:CRLF 沿用、尾端沒換行先補、行首空白不算有、已有不重複、二進位追加不整檔改寫;docs/.gitignore 是目錄或不可讀時 OSError 回 []。BOM 開頭只會多補一行重複,無害。
- `_local_ledger_doctor_msgs`:git 逾時/不在 repo(128)不提醒;已追蹤的檔 check-ignore 結果被 `not tracked` 擋掉,不誤報。
- `_usage_log`:實查整個 repo 沒有任何程式讀 `.usage-log.jsonl`,舊帳凍結不影響讀者;`_BOOKKEEPING_FILES`、cochange 排除清單多加的兩個本機帳名只是白名單。
- 測試改動:`_gov_since` 用多重集合差,同秒同內容事件計數正確;`_gate_rows`、`_m1_events` 重新 dumps/loads 無損;t_delguard 改讀版控帳驗 degraded、本機帳驗 ok 與寫入點一致。
- pitfalls manifest:三條 `open(`(`scripts/lumos:1454`、`1531`、`21064`)都在 `with` 內,誤報;`ruff E702`(`scripts/test_lumos.py:38466`)是 t_delguard_logs_ok_too 開頭原有的 `root = ...; vault = ...` 一行,不在本 diff 新增的行裡,與本案無關。
- 圖譜鏡頭:派工尾端沒有附 LUMOS-IMPACT 固定席筆記,未能逐條判;以程式碼實查代替(判定類讀者只讀版控帳這條合約,見上方 `_gov_routes_local` 一項)。
- 角色鏡頭:本案只改後端單檔 Python 與測試,沒有附到角色卡,略過。

總結:分流判定與兩批各自吞錯都站得住,但度量撤除條件的暖機護欄只看版控帳,本機帳缺席時會對走本機帳的閘誤報「該撤」,另有兩處較輕的邊界問題。
