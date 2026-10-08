severity: major

審查鏡頭:回滾與時序。對照碼:/Users/enzo/harness/lumos-d3(HEAD b4637da0),spec:/tmp/d3-r1.md。唯讀,未改檔。
圖譜固定席:派工時沒有附上合約/事故節點給我;我自己對 Systems/guard-kill 的兩條 ★INVARIANT★ 做了判斷(見末節)。

## F1 kill-add 的「合約清單」在鎖外才讀,spec 沒規定清單從哪來
severity: major
blocking: 是——寫入已成功之後的比對讀到別人改過的筆記,會印出與事實相反的提醒或對不回,而 spec 沒定義這些路徑。
spec 段落:範圍第一條「寫入成功後,比對這次實際寫進去的那條配方跟那條合約行的測試清單」、PRIOR-ART「kill-add 的提醒接在既有的鎖外提醒 `_kill_add_after_lock`/`_kill_add_warn` 旁」。
問題:`_kill_add_after_lock` 在放掉寫入鎖之後才跑(`scripts/lumos:15217`),而 `warn_box` 裡只放配方(`scripts/lumos:15335` `warn_box.append(recipe)`),合約行的 `refs`(`scripts/lumos:15289`)是鎖內讀的、沒有交出來。spec 沒說清單是「鎖內抓好隨 warn_box 帶出」還是「鎖外重讀筆記」。若照 PRIOR-ART 的字面(鎖外、用 `_kill_read_recipes`/`extract_contracts` 重讀),就是讀—檢查—使用的時間差:
- 例 1:A 跑 `kill-add --test T`(T 不在清單)寫入成功,放鎖;B 在這一瞬間 `guard bind` 把 T 加進清單。A 的比對讀到新清單 → 不提醒(漏報);反過來 B 若 `remove`/改掉那條 `[test:]`,A 印出的清單內容與寫入當下不同。
- 例 2:B 在鎖外空窗 `kill-rm` 了 A 剛寫的配方,或把合約行改寫(regen),A 重讀時「找不到那條配方/合約行」。spec 只定義了「未定義平台前綴 → 不比、不提醒、不失敗」,沒有定義「找不到合約行」「配方已不在」;若實作成「清單是空的」就會誤印「這條合約還沒綁任何測試」。
- 例 3:--try 還在後面跑(`scripts/lumos:15228`),提醒若在 try 之後才讀筆記,窗口更大。
退回後的行為:這些都是只印 stderr 的提醒,所以不會留下壞資料,但維運者收到的是與當下筆記狀態相反的提醒,要回頭查才知道是時間差。
修法方向:清單(含解析所需的 `refs`、當時的平台設定)在 `_guard_kill_add_locked` 鎖內就解析好,隨 warn_box 一起帶出,鎖外只做比對;spec 要明寫「以寫入當下那份為準」。
引句:「寫入成功後,比對這次實際寫進去的那條配方(含「只更新 covers」那條路徑沿用的既有配方)跟那條合約行的測試清單」

## F2 寫入成功之後的比對遇到設定檔讀不了/平台不在設定,spec 只處理了 ValueError
severity: major
blocking: 是——寫入已落盤後若比對丟出未攔的例外,kill-add 以 traceback 結束(rc 非 0),使用者重跑會被「判重」擋下,留下已寫入但看似失敗的殘局。
spec 段落:範圍第一條末句「合約行有未定義的平台前綴(解析丟 ValueError)時不比、不提醒、不讓 kill-add 失敗」;PRIOR-ART 的 resolve_test_refs 描述。
問題:`resolve_test_refs(合約行, 平台表, 預設平台)` 要的平台表來自 `_kill_cfg_load`,它在 config.json 壞掉時回 `(None, 原因)`(`scripts/lumos:14689-14712`),此時 `pdata` 是 None,取 `pdata["platforms"]` 直接 TypeError。另外配方自己的 platform 不在設定裡(`_kill_recipe_judge` 的 `noplat`,`scripts/lumos:14835`)時,「配方的 (平台, 方法)」對不上清單任何一項,會被判成「不在清單上」而誤報——其實是平台設定錯,P2 前兩則已經在講。spec 的例外保護只寫了 ValueError;既有 `_kill_add_warn` 是整段 `except Exception`(`scripts/lumos:15014`),新提醒沒被要求同樣兜底。
具體例:`.lumos/config.json` 手改到一半是壞 JSON,`kill-add --test X` → 配方寫入成功 → 比對時 `pdata=None` → TypeError → 使用者看到 traceback,再跑一次得到「同一條…已經有了」擋下。退回(revert)這支提交後這個殘局會消失,但在 revert 之前沒有任何提示說「配方其實已寫入」。
doctor 側同理:spec 說這一則「不掛在它們的掃描裡」,等於自己再讀一次設定檔(`_kill_p2_scan` 已回傳 `ctx`/`cfg_err`,`scripts/lumos:15060`);兩次讀取之間 config 被改(doctor 要跑好幾支 git,P2 前兩則各自有逾時預算)會得到 P2 說「設定讀不了」而第三則照常比對、或相反。spec 沒說 cfg_err 時第三則要不要跳過,也沒說要不要共用 `_p2["ctx"]`。
修法方向:新提醒各自 `except Exception` 兜底成一行「沒比對」;cfg_err 與 noplat 明定「不比」;doctor 第三則共用 P2 的 ctx。

## F3 治理帳新事件 check-p2t 的登記面 spec 沒寫,回退節因此講得不對
severity: major
blocking: 是——漏掉登記實作就會紅或寫錯帳,且回退節宣稱的「不改資料」與實際不符。
spec 段落:範圍第二條「gov_events 記 `check-p2t`」、回退「退回本案的提交即可:只多兩處提醒,不改資料與判定」。
問題:
1. `_KNOWN_GATES`(`scripts/lumos:7993`)沒登記新閘名時,`t_gov_stats_gate_drift`(`scripts/test_lumos.py:6537`,掃全檔 `"gate": "字面值"` 必須全在名單內)會翻紅;spec 的驗收條款 S1/S2 沒有任何一條涵蓋這件事。
2. `_GOV_LOCAL_PAIRS`(`scripts/lumos:1320-1330`)是手列清單,`check-p2`、`check-p2s` 都在裡面;新閘名沒加進去,`_gov_routes_local`(`scripts/lumos:1436-1442`)回 False,`--ci` 的 doctor 就把它寫進「版控帳」(git 追蹤的檔)而不是本機帳。後果:每次 CI/例行 doctor 讓版控帳多髒一筆,別人的工作目錄出現不是自己造成的改動(全域規則的並行會談一條)。
3. 回退:提交 revert 後,已寫進帳裡的 `check-p2t` 行不會消失。舊版工具讀到它——我查了讀側:`_render_gov_stats` 用 `agg.setdefault(r["gate"], …)` 照收、只在「沒出現的閘」清單用 `_KNOWN_GATES`(`scripts/lumos:8060-8081`),不會崩潰,只是統計表多一列沒登記的閘。唯一會被回退弄壞的地方:若有人依 RETIRE-IF 把撤除條件寫成機器式 `[retire:度量 check-p2t.warned = 0 近8週]`,revert 後 `_KNOWN_GATES` 沒有該閘,`scripts/lumos:4263` 會判「度量的閘不在已知閘清單裡」,整批筆記的 lint 變紅。
4. 所以回退節實際要寫:revert 後帳裡殘留的事件行無害但不會被清;若用了度量式撤除,要先改掉那條。
引句:「退回本案的提交即可:只多兩處提醒,不改資料與判定。」

## F4 「沒帶 --test 一定不會觸發」與「只更新 covers 沿用既有配方也比對」互相矛盾
severity: minor
blocking: 否——只影響只更新 covers 時要不要印提醒,不影響寫入與資料。
spec 段落:範圍第一條。
問題:`_guard_kill_add_locked` 在只補 covers 時把 `recipe = r`(既有那條,`scripts/lumos:15327`)放進 warn_box,此時使用者沒帶 `--test`(`test_arg is None`)。spec 同一條裡先說比對「含只更新 covers 那條路徑沿用的既有配方」,結尾又說「沒帶 `--test` 時配方的測試一定取自清單,不會觸發」。對一條先前刻意用清單外測試寫入的既有配方,`kill-add … --covers java-concurrency`(不帶 --test)會不會再印一次提醒?兩句話答案相反。S1 的測試句型也只列了 --test 的情形。
修法方向:明定規則是「看配方實際的 test,不看這次有沒有帶 --test」並補一格測試,或明定只更新 covers 不印。

## F5 兩則提醒同時成立時 stderr 行數合約沒定
severity: minor
blocking: 否——是既有測試格式與 spec 的對接缺口,實作時才會翻紅,不影響資料。
spec 段落:範圍第一條「stderr 多一行提醒」。
問題:`_kill_add_warn` 的註解與 `t_guard_kill_add_warns_drifted_recipe`(`scripts/test_lumos.py:66973` 起)釘「恰好一行提醒」(`len(extra) == 1`、`len(_kr_err_lines(r)) == base_err + 1`)。配方原文對不上(drifted)而且 `--test` 又在清單外時,舊提醒一行加新提醒一行共兩行;spec 沒說是合併成一行、各印一行、還是先後順序。那組測試的 fixture 的 base 不帶 `--test`,所以不會紅,但日後任何帶清單外 `--test` 的 kill-add 測試都會多一行,斷言行數的測試要逐支檢查。
修法方向:spec 明寫「兩則各一行、先原文失配後未綁」(或合併),並在 S1 補同時成立的一格。

## F6 配方的 invariant 片段在 kill-add 與 doctor 的匹配口徑不一致
severity: minor
blocking: 否——只造成 doctor 把合法配方算進「另有 N 條對不回」,不影響寫入。
spec 段落:PRIOR-ART「對回合約行用 `extract_contracts` 加去標記後『含片段』」、範圍第三條。
問題:kill-add 定位合約行是對整行(含 `KEY:★INVARIANT★ ` 前綴)去標記後做子字串(`scripts/lumos:15276`,`INVARIANT_RE.match` 後 `invariant_substr in INV_TAG_RE.sub("", lines[i])`);`extract_contracts` 回傳的是 `mi.group(1)`,也就是前綴之後的文字(`scripts/lumos:5139`、`5169-5181`),且只掃 summary。配方片段只要含到前綴字樣(例:`INVARIANT★ guard kill rc`)或行首括號日期(`KEY:(2026-10-01) ★INVARIANT★`),kill-add 接受、doctor 判成「對不回合約行」。另外 spec 的「恰好對到一行」與 kill-add 的「多於一條就擋」同向,但 kill-add 是掃整段 frontmatter 的行、doctor 只掃 summary,兩者在 summary 之外出現 KEY 行時不一致。
修法方向:doctor 用跟 kill-add 同一支定位邏輯(抽共用),不另寫一份。

## F7 RETIRE-IF 的度量讀不到 rtb 的帳,且「另有 N 條」行不是事件
severity: minor
blocking: 否——是撤除條件的可量性,不影響功能。
spec 段落:RETIRE-IF「連續 60 天 doctor 這一則提醒在本工具鏈與 rtb 都是 0 筆、而且 kill-add 沒印過這個提醒」。
問題:`check-p2t` 若照 `check-p2` 走本機帳(F3),各庫的本機帳互相看不到;kill-add 的提醒完全不落帳(`_kill_add_warn` 只印 stderr)。所以「rtb 都是 0 筆」「kill-add 沒印過」這兩半都沒有機械來源,60 天後沒人能判。同時「另有 N 條配方對不回合約行」那行,spec 沒說它不落帳、也沒說 N>0 但沒有未綁配方時 doctor 要印 ok 還是 warn_soft;若走 warn_soft 就是永久噪音(目前沒有任何檢查能讓這 N 條消失)。
修法方向:撤除條件改成能查的(例如只看本庫本機帳的 check-p2t 筆數,並明寫 rtb 靠它自己回報),並定 N>0 的呈現方式。

## 逐節

- 開頭 summary(WHY/出處/因/不選):已讀,無 finding。「kill-add 沒帶 --test 時從清單取」與 `scripts/lumos:15291-15300` 相符。
- 白話與 PRIOR-ART:見 F1、F2、F6。PRIOR-ART 引用的函式皆存在(`resolve_test_refs` `scripts/lumos:5619`、`_kill_method_name` `14650`、`_kill_note_skipped` `15020`、`_kill_read_recipes` `14619`、`extract_contracts` `5169`、`_kill_add_after_lock` `15217`、`_kill_add_warn` `14992`)。「各提醒自己一個例外保護」在 doctor 側成立(P2 二則都有),kill-add 側 spec 沒要求,見 F2。
- 範圍:見 F1、F2、F4、F5、F7。
- 實務隱患:多平台 ref 與大圖譜兩點已讀,無 finding(doctor 不跑 git 屬實,但第三則自己再讀一次設定,見 F2)。
- 驗收條款:S1、S2 已讀;缺 F1(鎖外時間差)、F2(設定壞)、F4、F5 的格,見各條。
- 回退:見 F3。
- 天花板:已讀,無 finding。

## 實務隱患(回滾與時序鏡頭逐類)

- 退回後的行為:提醒類功能退回後 stderr/doctor 輸出消失,筆記與配方資料不受影響;殘留物只有已落帳的 check-p2t 行(F3,舊版讀不崩潰,已查讀側)。
- 版本:doctor 讀工作目錄(`_kill_read_recipes(vault / rel)` 與 `notes`),與 bound-tests 閘讀「工作樹版節點」一致(Systems/bound-tests-gate 第 105 行說明),所以尚未提交的 `guard bind` 會讓 doctor 先靜默而推出去的提交仍缺綁定;spec 沒寫「讀工作目錄、不看 HEAD」,屬於沒說明但行為一致,不列 blocking。
- 平台設定檔兩次之間被改:見 F2。
- 並行寫入:kill-add 寫入本身有鎖(`scripts/lumos:15207`),比對在鎖外,見 F1。
- 金流/對外送出/不可逆/守衛面:spec 已排除,我同意——比對只讀,不改閘的判定。
- 對固定席合約(Systems/guard-kill):`guard kill rc 優先序`(rc 與 survived/drifted 關係)與 `guard kill --json` stdout 純度——新提醒只在 kill-add 的 stderr 與 doctor 輸出,不碰 `cmd_guard_kill`;判「不影響」。但 `kill-add --try` 的輸出順序(提醒在試跑之前)沒釘,不影響上述兩條合約。

severity: major
blocking 3 條(F1、F2、F3)。
