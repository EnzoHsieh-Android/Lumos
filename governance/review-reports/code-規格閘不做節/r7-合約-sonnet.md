severity: major

我讀了修補差異全文,對照 working tree 的圖譜與手冊。S37–S44 的測試我真的跑過(`-k nogo_light_major`、`lumos_entry`、`door_scans_raw`、`ledger_unreadable`),全綠。`lumos spec-trace` 顯示 44 條全綁、懸空 0。`lumos lint` 對計劃與 Systems/規格閘都是 0 問題。另外我在暫存副本加了兩支探測測試,跑完已刪。

我跑測試時 `$TMPDIR` 下留了 `gctl-run-*` 目錄。但同時段別的會談也在產生,我分不出哪些是自己的,所以沒刪,請使用者或原會談自行認領。

先講白話:新規則叫做「帳上任何一筆輕量審抓到 major,只要它看過的被略過行等於現在這幾行就擋」。它需要拿到「那筆 major 看過哪幾行」才能比對。拿不到時,規則是靜默放過,不是擋下。拿掉窗口 ratchet 之後,這個靜默放過就變成漏洞。

severity: major
blocking: 是 — 窗口 ratchet 拿掉後,「沒有快照、也沒有規格閘留痕」的 major 會被靜默丟掉,推送前放行(我重現了)。
引句:「兩樣都沒有就比不了、不進索引。」
問題:`_nogo_ctx` 只在 major 之前出現過同編號的規格閘留痕時,才記下 `gate_sha`。`_nogo_major_lookup` 在快照缺或驗不過、又沒有 `gate_sha` 時,`fp` 是 None,這筆 major 不進索引。同時推送前傳 `ratchet=False` 給 `_light_gate_fails`,窗口裡的 major 也不再擋。結果是 major 完全沒有效力。
失敗情境:這正是 S39 的流程,做完、全綠、沒有規格閘留痕的計劃:
1. 記一筆 major,漏帶 `--snapshot`,或快照後來被清掉。
2. 再記一筆綁好的乾淨輕量審。
3. 推送前 rc0。

我在暫存副本重現:`_ngl_review(severity="major", no_snapshot=True)` 加一筆乾淨審,`_ngl_push` 回 0。修補前的窗口 ratchet 會擋住這個情境。
文件也講過頭:計劃寫「快照刪掉也洗不掉」,S26 的精神是 major 洗不掉。沒有留痕時這句不成立,而且沒寫成範圍外,也沒有 REVISIT。現有測試 S40 ② 只測了「有留痕」那一邊。
file: `scripts/lumos:9276`(`_nogo_major_lookup`)
file: `scripts/lumos:9186`(`_nogo_ctx` 的 `gate_sha`)

severity: minor
blocking: 否 — 屬於設計天花板,沒有比 r5 更寬;但計劃沒承認,也沒給回頭條件。
引句:「跟這份計劃現在被略過的行(正規化後,_nogo_line_key)整份相同,就照擋。」
問題:比對是「整份被略過行的集合」相等。major 之後在不做清單多加一條無害的「不做扣款」,整份指紋就變了,major 脫鉤。原本被點名的夾帶行還在,只換一個審查員重審一次。
失敗情境:我在暫存副本重現,另加一行被略過行、重跑規格閘、再記一筆乾淨審,推送前 rc0。文件只寫「那幾行真的改了字才重新來過」,沒說加行也算改。
file: `scripts/lumos:9276`

severity: minor
blocking: 否 — 守衛本身的行為仍有 S43 測試把關,但「改了沒 bump 會紅」的說法對掃法不成立。
引句:「掃法寫死在函式裡,常數只進門判定規則指紋、讓指紋跟著掃法變」
問題:`_DOOR_SCAN_RAW` 全 repo 只出現在常數定義、版本註解和 `f"scan_raw=…"` 這一處。`_door_keyword_hits` 沒讀它。舊的 `_DOOR_SCAN_FENCED` 是真開關,翻它會改行為。現在把掃法改回剝行內標記,指紋與 `t_door_rule_version_pin` 都不會變,不會逼人升版。Systems/規格閘 KEY 與 `_DOOR_RULE_VERSION` 註解仍寫「改了任一支沒 bump 就紅」,對這一項是假的。S43 的行為測試會紅,但版本號不會被強制升。
file: `scripts/lumos:8073`
file: `scripts/lumos:8127`
file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:38`

severity: minor
blocking: 否 — 只是說法不一致。
引句:「代價:別份計劃被略過的行跟某筆舊 major 看過的一字不差,也會被擋」
問題:你要求各處說法一致,但「兩份無關計劃被略過行一字不差也被擋」這個代價只寫在三處:這支函式的 docstring、計劃〈實務隱患〉、計劃的 REVISIT。Systems/規格閘.md 的新規則段與新 PITFALL 沒寫代價。design-loop 的 SKILL.md 與 templates.md 只寫「帳上任何編號…就照擋」,沒說會誤擋無關計劃。擋下訊息有講迴圈編號,但手冊沒預告。REVISIT 靠治理事件 `note` 含「迴圈 X 的輕量審」來數,而 `_nogo_light_block_event` 把 `note` 截在 200 字。head 最多列 6 個危險詞再接 `迴圈 X`,編號很長時可能被截掉,量不到。
file: `scripts/lumos:9369`
file: `skills/lumos-design-loop/templates.md:69`

severity: minor
blocking: 否 — 說法誇大。
引句:「帳檔權限壞掉時每次推送都會被擋,要先修好帳檔」
問題:`_spec_gate_push_check` 在 `plans` 為空時先 `return 0`,讀帳在 `_spec_gate_push_scan` 裡才發生。所以只有推送碰到候選計劃,帳壞才擋,不是每次推送。方向(fail-closed)沒問題,只是範圍寫大了。
file: `scripts/lumos:9435`

severity: minor
blocking: 否 — 舊說法殘留。
引句:「留痕另記算法版本 `nogo_rows_v`(2;舊留痕沒有這欄=1,只去空白)」
問題:有兩處舊說法沒跟上。
- 計劃做法第 5 點要求同步 `雙向門放行_計劃`,但這份沒在修補裡。它的第 48 行仍寫「版本升為 3」,第 43 行仍寫「掃全文可見行」。現在是版本 5、掃每一行原文。
- Systems/規格閘 的「留痕」KEY 仍只列 `nogo_rows_sha`,沒有 `nogo_rows_v`,只有長段落提到。
file: `docs/lumos-toolchain-knowledge/Projects/雙向門放行_計劃.md:48`
file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:38`

其餘我查過,沒有問題:
- 窗口 ratchet 的舊說法在手冊裡已清掉,只剩上面列的殘留。
- S19 與 S26 的條款文字和測試一致。
- 入口 WHY 有寫代價與範圍外,出處檔存在。
- 新增的 REVISIT 行格式正確。
- 「完整設計審的 major 被當輕量審」那條,S41 的測試確實驗到。

最高等級 major,blocking 1 條。
