severity: major

# r3 正確性席(sonnet)

驗法:把 scripts/lumos 每個寫治理帳的呼叫點(`_gate_event` / `_gate_event_or_warn` / `_gate_event_fit` / `_append_governance_log` / `_bound_tests_log` / `_delguard_log_result` / doctor 的 `gov_events.append`)逐一列出(閘名、種類、hard),套「閘名+種類在名單上且 hard 恰好 False」。再反向驗名單 11 列每個組合是否真有寫入點。結果:名單上的組合除一個外都存在;種類與 hard 的組合沒有收進擋人(blocked 一律 hard=True 或不在名單)、drift-check / nodehome-check 的 warned、note-shape 的 warned 都不在名單,r2 的修正(白名單加 hard 恰好 False)方向改對了。查到的洞在「同一個閘名+種類底下混了不同性質的事件」與「忽略規則內容」。r2 折入的項目(skipped-flag、unfilterable、shallow-skip、提醒模式 warned、舊 vault 補 docs/.gitignore、兩本依時間排序)沒有再報。

1. bound-tests/green 會裝進「部分測試根本沒跑」的略過,被名單整包收進本機帳
severity: major
blocking: 是(判準:照字面實作,自動放行/略過痕跡會進本機帳,違反本案自己的守衛面承諾「略過與自動放行照舊進版控」)
引句:「| bound-tests | green |」
佐證:
- file: `scripts/lumos:42732`:多平台設定下某平台沒設 run_cmd,該支記成 `no-cmd` 並繼續跑別的平台(Issues/多平台設定下測試指令被默默略過 的修法就是「記成沒跑」)。
- file: `scripts/lumos:42763`:只有「全部都是 no-cmd」才回 no-config;混著有綠的 results 會往下走。
- file: `scripts/lumos:42895-42896`、`scripts/lumos:42905`:`_nocmd`、`_not_run` 只進回傳值的 reason / not_run,沒進帳。
- file: `scripts/lumos:42952-42953`:仍呼叫 `_bound_tests_log(repo_root, "green", sorted({r[0] for r in results}), f"{ran} 綠", …)`,節點含沒跑的那幾支,hard=False(`scripts/lumos:42460-42466` 只有 red-blocked 為真)。
具體場景:多平台專案,平台 A 有 run_cmd、平台 B 沒設;推送波及兩邊的合約,B 的測試沒跑、閘判 green 放行。帳上只有 gate=bound-tests kind=green hard=False,分不出這一筆夾帶「N 支沒跑」。名單收它 → 這筆「自動放行/略過」只在本機帳,CI 與別台機器看不到,而這正是 2026-09-11 那條 Issue 要讓人看見的東西。
建議:green 事件在有 no-cmd 時改記別的種類(或名單改成「寫帳時就不把有 not_run 的算 green」),或名單不收 green、改收更窄的條件;防漂移釘 [S6] 要加一條「名單上的種類不得混入略過語意」的對照。

2. 既有 vault 新建 docs/.gitignore「內容同新建 vault 的那份」會把繞道、簽核、殺傷力、審計四本帳對「尚未建立」的專案改成忽略,跟〈不做〉相衝
severity: major
blocking: 是(判準:照字面實作,更新後消費專案首次寫出的 bypass / canary / kill / signoff 帳不再進版控,漏掉合約;⚠ 判斷依據是〈範圍〉不動這五本的承諾,不是已查到的某條 CI 讀者)
引句:「內容同新建 vault 的那份;已追蹤的檔不受 .gitignore 影響」
佐證:
- file: `scripts/lumos:20878-20881`:新建 vault 的 docs/.gitignore 內容含 `.bypass-log.jsonl`、`.canary-log.jsonl`、`.kill-log.jsonl`、`.signoff-log.jsonl`、`.usage-log.jsonl`、`.ci-log.jsonl`。
- file: `scripts/lumos:20865-20881`(註解):2026-08-21 之前建的 vault 沒有 docs/.gitignore,帳檔當時是照「沒被忽略」的狀態運作。
- file: `scripts/lumos:20894-20911`:`_init_additive_setup` 現況只處理 governance/.gitignore。
具體場景:2026-08 前建的消費專案,還沒發生過 bypass(`docs/.bypass-log.jsonl` 不存在)。跑 `lumos update` → 照字面建出含那四行的 docs/.gitignore。之後第一次繞過 L2(`scripts/hooks/post-commit:93` 寫該檔)→ 被忽略,不再出現在 git status、不被提交,別台機器與 CI 看不到繞道痕跡。「已追蹤的檔不受影響」只救「已存在且已追蹤」的帳,救不到「之後才第一次產生」的帳。本案另一處明說繞道與五本帳「照舊進版控」,這裡實際把它們在舊 vault 改成不進。
建議:既有 vault 補建的 docs/.gitignore 只放本案新增的兩行(`.governance-local.jsonl`、`.usage-local.jsonl`),不要照搬新建 vault 的整份;或明講這是有意跟新 vault 對齊並進〈天花板〉。

3. 名單的 check-j/warned 在程式裡不存在,[S6] 只驗種類、驗不出
severity: minor
blocking: 否(判準:多收一個不存在的組合無害,只是名單與〈盤點〉「真的存在」的說法不符)
引句:「doctor 寫的 check-* 各閘(以 `_KNOWN_GATES` 裡 check- 開頭的閘名為準,實作時逐一列進常數,不用前綴比對)」
佐證:file: `scripts/lumos:3394`(check-j 只寫 blocked、hard=True)、`scripts/lumos:5787`(check-j 只寫 shallow-skip);沒有 check-j/warned 的寫入點。其餘 check-*(cascade、revisit、e1、e2、e3、lint-decl、k、p2、p2s、r、s、s2–s11、s16)都有 warned 且 hard=False(`scripts/lumos:1915`、`2610`、`3200-3224` 等)。[S6] 寫的是「種類 應 都有寫入點」,check-j 的 warned 這個種類在別的閘有寫入點,所以釘子不會紅。實作者若按「check-* 全列 warned」生成,多一條死項;更糟的是日後有人在 check-j 加 warned(hard 可能為真,走 `scripts/lumos:3394` 旁的風格)就自動被收。
建議:名單逐閘列(不含 check-j),[S6] 改成逐「閘+種類」驗有寫入點。

4. 〈盤點〉與表裡把 delguard/ok 描述成「沒事」,實際 ok 也記有命中的提醒
severity: minor
blocking: 否(判準:歸類結果仍是純提醒觀察,不影響擋放;只是描述不準,日後有人用「ok=沒事」去推讀法會錯)
引句:「| delguard | ok |」
佐證:file: `scripts/lumos:37050`(`_delguard_log_result(gr, "degraded" if _partial else "ok", …, hits, …)`,hits 非空也記 ok、nodes 帶命中的筆記)、`scripts/lumos:36960-36962`、`scripts/lumos:8238-8240`(gov 呈現端同樣把 ok/degraded 當 advisory 折疊)。盤點段「刪除守衛:沒事」的說法不準;名單本身可留。

5. 無 pins / 無綁定 / 無 vault 的零覆蓋事件是例行寫入,但〈做法〉排除清單沒列,[S1] 在這類專案不成立
severity: minor
blocking: 否(判準:都不在名單、會進版控帳,守衛面安全;只是 [S1]「一個位元組都不變」的前提沒講清)
引句:「判斷不了(range-unavailable、diff-unavailable、no-config、whole-suite-deferred)」
佐證:file: `scripts/lumos:42868`(`kind = why.split(":", 1)[0]` 後直接 `_bound_tests_log`,種類為 no-pins / no-bound / no-vault / diff-unavailable);`scripts/lumos:42530`(沒綁合約的消費專案每次推送都回 no-pins);`scripts/lumos:42986` 起的註解說這三種零覆蓋刻意分開記,為了讓消費專案接入靜默失效看得見,所以留版控是對的。但:①清單舉的「判斷不了」少了 no-pins/no-bound/no-vault;②`scripts/lumos:42865` 註解說 diff-unavailable 已沒有來源,清單寫了它但程式不會產生。建議把這三種補進排除清單、把 diff-unavailable 拿掉或註明,並在〈天花板〉3 加一句「沒有合約綁測試的專案推送仍會髒」。

6. S18 / spec-gate 合併讀的幾處細節
severity: minor
blocking: 否(判準:都是軟提醒段,`--ci` 不跑;偏差方向是多提醒或少提醒)
引句:「S18 度量改用擴充後的 `_gov_metric_events` 讀兩本」
佐證:
- file: `scripts/lumos:3867-3869`:`if not ok_rows or not gl.is_file(): return out` 要一併改成「兩本都不在才返回」,否則版控帳不存在、只有本機帳的專案整段靜默不判。
- file: `scripts/lumos:3695-3706`、`3826`:`_gov_metric_events` 只讀檔尾(24MB 上限)。「最舊一筆取兩本最小」時,若版控帳被檔尾截到只剩近幾週、本機帳更舊,暖機護欄(最舊一筆不早於 N 週前就不判)會被本機帳的舊時間誤放行,版控帳那半的種類(例如 blocked)被低估,用 `<=` 的度量會誤判成立。應該是「各帳各自檢查自己的覆蓋範圍,取較晚的最舊時間」或至少只對被名單收進本機的種類用本機帳的最舊時間。
- file: `scripts/lumos:2869-2877`:spec-gate 後半現在靠檔內順序取最後一筆;改成「依時間排序」時 ts 是各機器本機時區的 ISO 字串(`scripts/lumos:1424`),不同時區的字串排序不等於時間排序,要用 `fromisoformat` 比;spec 只寫「依時間排序」。

總結:名單 11 列中 10 列的組合都真實存在且 hard 皆為 False,擋人(blocked / red-blocked / unfilterable)、繞道(skipped*、shallow-skip)、自動放行(fail-open、degraded、red-advisory)沒有被收進;但 bound-tests/green 會夾帶「部分測試沒跑」的略過(finding 1),以及既有 vault 補建 docs/.gitignore 照搬新 vault 內容會把舊專案日後才產生的繞道、簽核、審計帳變成不進版控(finding 2),這兩條是 blocking;其餘 4 條為 minor。
