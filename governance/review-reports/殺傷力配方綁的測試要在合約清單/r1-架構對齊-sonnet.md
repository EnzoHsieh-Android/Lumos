severity: minor

## 問 1 分層與依賴方向
大方向一致:doctor 提醒併進 P2 段當第三個提醒、各自例外保護,kill-add 提醒接在鎖外;比對只用既有 `resolve_test_refs`、`_kill_method_name`、`_kill_read_recipes`,沒有跨層直呼。對照 `scripts/lumos:3365`、`scripts/lumos:3384`(P2 段兩則提醒與例外保護)、`scripts/lumos:15217`(`_kill_add_after_lock` 在鎖外迴圈 `_kill_add_warn`)。
引句:「doctor 的提醒併進既有的 P2 段(殺傷力配方專屬、warn_soft、`_kill_note_skipped` 跳過規則、各提醒自己一個例外保護、gov_events 落帳),當第三個提醒」
唯一缺口見 F1(新閘名沒登記)與 F2(kill-add 鎖外拿不到合約行)。

## 問 2 命名與錯誤處理
提醒前綴「⚠ 提醒:」與 stderr 單行、不擋、判斷出錯也不崩潰,與 `_kill_add_warn`(`scripts/lumos:14992`、`scripts/lumos:15014` 的 except 分支)同形。`check-p2t` 命名沿 `check-p2`、`check-p2s`。但「合約行有未定義的平台前綴時不比、不提醒」與既有 `_kill_add_warn` 的做法不同:既有做法是出錯也印一行「沒驗」,不是靜默。見 F3。
引句:「合約行有未定義的平台前綴(解析丟 ValueError)時不比、不提醒、不讓 kill-add 失敗。」

## 問 3 第二種做法
測試名比對:用 `resolve_test_refs` 加 `_kill_method_name`、比 (平台, 方法) 對,與既有背書比對同一套(`scripts/lumos:46082` 也是 `r["platform"] == plat and _kill_method_name(r["test"], mp) == name`),沒有另起一套。
對回合約行:doctor 側用 `extract_contracts` 加去標記後含片段,與 guard kill 的 `scripts/lumos:13538` 同形;但 kill-add 側既有定位用 `INVARIANT_RE.match` 逐行掃加 `INV_TAG_RE.sub`(`scripts/lumos:15276`),本設計對 kill-add 側沒講用哪條,見 F2。doctor 側另走一次獨立的逐篇讀配方迴圈,不重用 `_kill_p2_scan`(`scripts/lumos:15028`)已掃的結果,是刻意(材料有交代),結構上算兩次掃描但不算第二種判法。
引句:「配方讀取用 `_kill_read_recipes`,對回合約行用 `extract_contracts` 加去標記後「含片段」。」

## 問 4 落點
lands_in 寫 Systems/guard-kill 與本案內容相符:`_kill_*` 與 doctor P2 都屬 guard kill 家的檔(`scripts/lumos`),沒有要新開節點。
引句:「RETIRE-IF: 連續 60 天 doctor 這一則提醒在本工具鏈與 rtb 都是 0 筆、而且 kill-add 沒印過這個提醒,就把 doctor 那一則拿掉(kill-add 的提醒留著)。」
註:設計沒寫要把 `check-p2t` 登進 `_KNOWN_GATES`,見 F1。

## F1 新閘名 check-p2t 沒講要登記到閘名清單
severity: minor
blocking: 否
引句:「gov_events 記 `check-p2t`;自己一個例外保護。不跑 git。」
對照:既有兩則提醒的閘名都登在 `_KNOWN_GATES`(`scripts/lumos:7993`、註解與常數在 `scripts/lumos:8022`-`scripts/lumos:8024`)與 doctor 寫 warned 的清單(`scripts/lumos:1329`);`scripts/lumos:1486` 對不在名單的閘名會直接不寫、只印警告。不登就是靜默漏帳,與 P2、P2s 做法不一致。

## F2 kill-add 側對回合約行的做法沒講,易長出第二套定位
severity: minor
blocking: 否
引句:「不在清單解析出的 (平台, 方法) 裡 → 寫入照常、rc 照常,stderr 多一行提醒」
對照:合約行在鎖內讀(`scripts/lumos:15276`-`scripts/lumos:15287`,已取得 `line` 與 `refs`),提醒卻在鎖外(`scripts/lumos:15217`),`warn_box` 只裝配方(`scripts/lumos:15311`)。材料只說 doctor 用 `extract_contracts`,沒說 kill-add 是把鎖內那行帶出來、還是鎖外重讀再用 `extract_contracts` 找一次。若鎖外重讀就是第二套定位(既有 kill-add 用 `INVARIANT_RE` 加 `INV_TAG_RE.sub`);建議明寫沿用鎖內已定位的那行。判不準是否會成 major,標 ⚠。

## F3 未定義平台前綴時靜默跳過,與既有鎖外提醒「出錯也印一行沒驗」不同
severity: minor
blocking: 否
引句:「合約行有未定義的平台前綴(解析丟 ValueError)時不比、不提醒、不讓 kill-add 失敗。」
對照:`_kill_add_warn` 的 except 分支(`scripts/lumos:15014`-`scripts/lumos:15016`)判斷出錯仍印「沒驗」一行;doctor P2 的例外兜底也是 warn_soft 講「算不出來」(`scripts/lumos:3385`)。本設計對同類情形改成靜默,結構上仍是 try/except 不崩,只是訊息策略不一致。

不對齊共 3 條,其中 major 0 條
