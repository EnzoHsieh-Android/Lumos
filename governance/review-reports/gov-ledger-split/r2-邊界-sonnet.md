severity: major

# r2 邊界席(sonnet)——治理帳例行紀錄分流_計劃(第 2 版修訂稿)

查證方式:對照 scripts/lumos 現況;用 /tmp 暫時 git repo 實驗「停止追蹤後別台機器 pull」;統計 docs/.governance-log.jsonl 實際的 (閘, 種類, hard) 組合。r1 邊界席已報的不重報,只檢查折入對不對:r1 #1(繞道種類)折得不完整(見 finding 2)、r1 #5/#6/#8/#9 因改沿用 .ci-log 做法已消掉、r1 #10 已折對。

## 1.
severity: major
blocking: 是(判準:分流規則的預設方向與「分錯只會偏吵,不會偏丟」互相矛盾,依字面實作會讓未列種類的觀察型閘事件丟本機,屬守衛面主風險,實作者無從選邊)

引句:「新增的閘或種類沒放進名單,就照舊進版控帳——分錯只會偏吵,不會偏丟。」

問題:〈做法〉1 的規則是「閘在觀察型名單 且 hard 為假 且 種類**不在**留痕名單」才進本機帳。種類這條是黑名單:觀察型閘裡一個沒列在留痕名單的新種類,依規則會進**本機帳**,不是「照舊進版控帳」。只有「新增的閘」這半句成立(閘名不在觀察型名單就留版控)。「新增的種類」那半句與規則相反。實際已有多個未列種類走到這條路:`drift-check` 的 `warned`(warn 模式不擋,scripts/lumos:34860)、`note-shape` 的 `warned`(scripts/lumos:29855)、`nodehome-check` 的 `warned`(scripts/lumos:27372)。這些是「本來要擋、因設定成 warn 而放行」的痕跡,性質同「放寬設定」,但不在留痕名單上,會丟本機。〈實務隱患〉守衛面「略過、繞道、自動放行與主動決定的種類一律留」同樣建立在名單完整上,而名單完整與否正是 finding 2 查出不完整的地方。要嘛規則改成白名單(只有明列的觀察型種類進本機),要嘛把那句「新增種類照舊進版控」刪掉、承認未列種類偏向本機。
file: `scripts/lumos:34860`、`scripts/lumos:29855`、`scripts/lumos:27372`

## 2.
severity: major
blocking: 是(判準:r1 邊界席 #1 的折入不完整;留痕名單漏掉程式裡實際存在、性質就是人為繞過或工具失效自動放行的種類,這些痕跡會在別台機器與 CI 消失,直接違反 S2 與守衛面三道保險的第三道)

引句:「種類不在「留痕種類」名單上:skipped、skipped-env、fail-open、relaxed、degraded(略過、繞道、放寬設定、工具出錯自動放行的痕跡)」

問題:名單用的是種類的**字面值**,但 `bound-tests`(在觀察型名單上)實際寫的種類不是這些字面值:
- `skipped-flag`:人下旗標並留了理由的跳過,程式註解自己寫「前者是人當下決定並留了理由」(scripts/lumos:42840-42844),不等於 `skipped`,會進本機帳。這正是 r1 #1 要保住的「人主動繞過」痕跡。
- `range-unavailable`(scripts/lumos:42851、43017)、`diff-unavailable`(scripts/lumos:42868 一帶,why 的前綴)、`no-config`(scripts/lumos:42890)、`unfilterable`(scripts/lumos:42945)、`whole-suite-deferred`(scripts/lumos:42881):工具算不出或不能跑而放行,`_bound_tests_log` 註解稱「fail-open 四情境…都寫 gate=bound-tests 帳,零觸發看得見」(scripts/lumos:42438 前後)。種類名都不是 `fail-open`,全進本機帳。
- `check-j` 的 `shallow-skip`(scripts/lumos:5787):淺層 clone 跳過檢查,閘名屬「check-*」,hard 為假,種類不在名單,進本機帳。
實測 docs/.governance-log.jsonl 現存 `bound-tests skipped-flag` 14 筆、`diff-unavailable` 3 筆、`range-unavailable` 1 筆,折入後這些在新副本與 CI 上看不到。S2 的測試只涵蓋「略過或繞道痕跡」的名單內種類,抓不到這個缺口。
file: `scripts/lumos:42844`、`scripts/lumos:42851`、`scripts/lumos:42868`、`scripts/lumos:42881`、`scripts/lumos:42890`、`scripts/lumos:42945`、`scripts/lumos:5787`

## 3.
severity: major
blocking: 是(判準:既有消費專案(本 repo 自己的 vault 就是這型)拿不到忽略規則,本機帳變成「未追蹤但會被 git add -A 收走」的檔,S1 目標在這類專案達不到,且「偏吵不偏丟」的相容宣稱不成立)

引句:「既有 vault 由 `_init_additive_setup` 補——`docs/.gitignore` 存在而缺這一行就在尾端追加,不存在就不建(維持「只加不覆寫」)。」

問題:scripts/lumos:20870-20874 的註解寫明「2026-06-26 起一直寫在 vault 內」,即早期專案的忽略檔在 `<vault>/.gitignore`(本 repo 的 docs/lumos-toolchain-knowledge/.gitignore 就是,內容只有四行,不含治理帳以外的帳),`docs/.gitignore` 根本不存在。對這類專案,補丁的「不存在就不建」等於不補。「維持只加不覆寫」的理由也不成立:建一個**不存在**的檔不是覆寫,同一個函式的 `governance/.gitignore` 就是「不存在就建」(scripts/lumos:20896-20898)。後果:本機帳在這些專案是未追蹤檔(`git status` 仍髒,S1 不達成),任何人用 `git add -A` 或 IDE「全部暫存」就把一本每台機器各自追加的 JSONL 提交進版控,之後兩台機器各自 append 同一檔,合併時行尾衝突。這不是「只會看到一個未追蹤的檔」。本 repo 因為用根 `.gitignore`、不走這條,測不到;S5 也只測「存在/已有/不存在不建」三格,沒有「vault 內有 .gitignore 而 docs/ 沒有」那格。
file: `scripts/lumos:20870`、`scripts/lumos:20885`、`scripts/lumos:20896`

## 4.
severity: major
blocking: 是(判準:尾端沒換行的 docs/.gitignore 依字面追加會把兩行黏成一行,同時弄壞原有的 `.ci-log.jsonl` 忽略與新規則,屬可重現的功能性破壞)

引句:「`docs/.gitignore` 存在而缺這一行就在尾端追加」

問題:`_write_lf` 是整檔覆寫原語(tmp 檔加 os.replace,scripts/lumos:17605),要「追加」只能先讀整檔再寫回。〈做法〉4 沒規定尾端無換行的處理,也沒規定「缺這一行」怎麼比對。具體場景:人手改過的 `docs/.gitignore` 結尾是 `.ci-log.jsonl`(無 `\n`)。直接把 `.governance-local.jsonl\n` 接上去得到 `.ci-log.jsonl.governance-local.jsonl`——原本的 `.ci-log.jsonl` 規則失效(.ci-log 變成 dirty)、新規則也沒生效。比對方式未定也有洞:用子字串判「已有」,遇到註解行 `# .governance-local.jsonl` 或 `.governance-local.jsonl.bak` 會誤判為已有而不補;用整行相等,遇到 CRLF 檔(`.governance-local.jsonl\r`)會漏判而每次 init 都重複追加,違反 S5「已有就不重複」。S5 的測試名只列了三格,沒涵蓋無尾換行與 CRLF。程式裡可抄的先例:scripts/lumos:24310 一帶的 `_pull_source_or_abort` 追加 JSONL 時就有 `sep = "" if raw.endswith("\n") else "\n"` 這步。
file: `scripts/lumos:17605`、`scripts/lumos:20885`

## 5.
severity: major
blocking: 是(判準:停止追蹤的提交一落地,其他每台機器上的 `git pull` 會被擋或刪檔;spec 的相容與回滾節完全沒談,且唯一能自動化解的路徑依賴 `_BOOKKEEPING_FILES` 裡那一項,spec 沒要求保留)

引句:「使用紀錄帳停止追蹤」

問題:spec〈相容〉只說消費專案不受影響,沒談**本 repo 的其他 clone**。實驗(/tmp/gt,上游 `git rm --cached` 後提交):
(a)別台機器該檔已被 `lumos show` 追加過(每次 show/context 都會,scripts/lumos:16186)→ `git pull --ff-only` 直接報 `Your local changes to the following files would be overwritten by merge` 並中止;
(b)該檔乾淨 → pull 成功,但**把磁碟上的檔刪掉**(`delete mode 100644`),該機器的使用紀錄歷史就此消失,與〈實務隱患〉「停止追蹤不刪磁碟上的檔」只在做提交的那台機器成立;
(c)工具鏈來源 clone 走 `_pull_source_or_abort` 的聯集合併(scripts/lumos:20585-20640)可以救(實際讀過:先 checkout 回 HEAD、pull、再把本機獨有行補回),但它判定「可併」靠 `p in _BOOKKEEPING_FILES`(scripts/lumos:24193)。停止追蹤後實作者很容易順手把 `docs/.usage-log.jsonl` 從該白名單與 `_COCHANGE_DEFAULT_EXCLUDE`(scripts/lumos:36525)移掉,那條救援路徑就斷,所有機器的 `lumos update`、`bootstrap --pull` 在來源髒了時被 fail-closed 擋住,重現 scripts/lumos:20553 註解記的 2026-09-06 事故。spec 沒有任何一句要求這兩處保留該項,驗收條款也沒有「來源 clone 髒了 usage-log 再 pull」那格。
file: `scripts/lumos:16186`、`scripts/lumos:20553`、`scripts/lumos:24193`、`scripts/lumos:36525`

## 6.
severity: minor
blocking: 否(判準:缺欄位或非布林的 hard 目前沒有呼叫端會產生,屬規格未定而非現況錯誤)

引句:「這筆不是擋人的紀錄(`hard` 為假)」

問題:極端輸入沒定義。`_gate_event_build` 一律 `bool(hard)`(scripts/lumos:1287),但 `_append_governance_log` 收的是呼叫端自組的 dict,批次寫入器本身不補欄位(scripts/lumos:1410-1432)。事件缺 `hard` 鍵,或 `hard` 是字串 `"false"`、`0`、`None`:字面「為假」會把缺欄位算成假而進本機帳,與整份 spec 的「不確定就留版控」原則相反;字串 `"false"` 用 `bool()` 是真(留版控)、用 `is True` 是假(進本機),兩種實作結果不同。目前所有呼叫端都帶布林(盤點全檔 gov_events,25 處 `hard=` 皆布林字面值),所以不是現況缺陷,但分流函式要寫成「只有 `hard is False` 才可能進本機」或明說缺欄位算真,這是 spec 該定的一句。同理 `kind`、`gate` 不是字串(例如 list)時,拿它對 frozenset 做 `in` 會丟 TypeError,而 `_append_governance_log` 只吞 OSError(scripts/lumos:1428-1432),會讓 `doctor --ci` 整個崩;spec 沒說分流判斷要整段包 try、出錯一律留版控。
file: `scripts/lumos:1287`、`scripts/lumos:1428`

## 7.
severity: minor
blocking: 否(判準:實作時會踩到的銜接缺口,不影響已定的行為,補一句即可)

引句:「取路徑的函式跟版控帳同一個資料夾(`<docs>/.governance-local.jsonl`),照 `CI_LOG_NAME`/`_ci_log_path` 的樣子寫。」

問題:`_ci_log_path(env)` 吃 env、用 `env.vault.parent`(scripts/lumos:38525);`_gate_event` 手上只有 `repo_root`、自己算 `root / "docs"`(scripts/lumos:1340-1341),`_append_governance_log` 吃 `vault` 用 `vault.parent`(scripts/lumos:1426)。三處本來就用兩種方式算「同一個資料夾」,一支「照 `_ci_log_path` 寫」的函式吃 env 就接不上前兩個寫入器。standalone vault(`_vault_in` 回 d 本身,scripts/lumos:21799 以下)時 `vault.parent` 是 repo 的**上一層**,與 `repo_root/docs` 不同——這在版控帳上是既有的歧異,但分流之後同一批事件的兩本帳會寫到兩個不同資料夾。spec 該指定函式簽名(吃 docs 目錄 Path)並說兩種呼叫端各自怎麼得到它。
file: `scripts/lumos:1340`、`scripts/lumos:1426`、`scripts/lumos:38525`

## 8.
severity: minor
blocking: 否(判準:只影響一句 doctor 軟提醒的準確度,不擋任何東西)

引句:「帳本成長段照舊只量版控帳,另外對本機帳加一行同門檻的軟提醒(超過上限只提醒,不擋)。」

問題:「同門檻」有兩條:檔案大小 5 MB 與「近 7 日均值 > 前 7 日均值 2 倍」(scripts/lumos:2238-2290)。本機帳是新檔。成長率那條的視窗判斷是 `_from == 0 or oldest <= 今天-15 天`(scripts/lumos:2272),小檔 `_from == 0` 恆成立,所以檔齡不到 15 天也會比。穩態每天 r 筆(r≥7)、檔齡 D 天:D=8 時前 7 日只有 1 天資料,倍數 7;D=9 為 3.5;D=10 為 2.33;三個值都 > 2 → 誤報「長得比平常快」。檔齡 ≥ 11 天才回到 1.75 以下。每個新 worktree、新雲端工作階段、換機器都重來一次,spec 沒說這條要加暖機門檻(檔齡 ≥ 15 天才比成長率)或只比大小。此外該提醒要不要也寫 `ledger-growth` 事件(寫了會進本機帳,自己餵自己)沒定。
file: `scripts/lumos:2272`、`scripts/lumos:2275`

## 逐節覆核

- 〈盤點〉:四個寫入點(`scripts/lumos:1358`、`1429`、`42423`、`43253`)與 7 本追蹤帳(`git ls-files` 實查)吻合。已讀,無 finding。
- 〈範圍〉:已讀,無 finding。
- 〈做法〉2(本機帳):docs/ 不存在時的行為與 `_gate_event` 回 None 一致;路徑函式的銜接缺口見 finding 7。
- 〈做法〉3(寫入器):各自開檔各自吞錯的設計成立;`_append_governance_log` 開頭的 `if not commit: return`(scripts/lumos:1421)在無 HEAD 時連本機帳一起跳過,與現況一致,不算新洞。極端輸入見 finding 6。
- 〈做法〉5(讀者):`cmd_gov` 的 `load` 對不存在的檔會直接跳過(scripts/lumos:8135 以下),空帳、缺帳安全;`load` 以 `name.lstrip(".").replace(...)` 命名載入源,新檔會印成 `governance-local`,無其他用該名字的比對。已讀,無 finding(除 finding 8)。
- 〈實務隱患〉:相容、回滾兩句見 finding 3、5。
- 〈驗收條款〉:S2、S5 的測試覆蓋缺口已併入 finding 2、4。
- 〈天花板〉、〈審計修正紀錄〉:已讀,無 finding。

總結:最嚴重 severity 為 major,blocking 共 5 條(finding 1、2、3、4、5)。
