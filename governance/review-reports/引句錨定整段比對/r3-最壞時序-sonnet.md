severity: major

我沒有改 repo,也沒有在 /tmp/lumos-seat-work 建任何東西,所以不用清理。以下 finding 都是用程式碼和測試對照出來的,沒有實際執行新判準,因為它還沒實作。

## 1. 隔離閥開著時凍結,會凍出關閥後必漂移的 golden(含週跑自動補凍)
severity: major
blocking: 是
引句:「處置閘與回放對所有帳一律走舊判準(印警告),同時把 `write_rule` 設 `legacy`」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos:1139-1175`
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/governance/autonomous_loop/replay_weekly.py:90-105`

1. 起點:迴圈 L 的載體列蓋 `full-span-v1`,內容是巢狀引句。這是舊判準不過、新判準過的那 45/3032 類。L 已收斂,但 `governance/replay/L/verdict.json` 還沒有。
2. 時序:週一有人開 `read_override: "legacy"` 止血。週二 `replay_weekly.py` 的「補漏凍結」對 L 跑 `loop replay L --freeze`。
3. 走到:`_loop_status_disposal` 照字面讀到隔離閥,載體用舊判準判。程式把 `verdict: {rc, fails}` 原樣凍進 golden,值是 `rc=1, fails=["quote"]`。
4. 設計上看不到這件事:golden 只存 `{rc, fails}`,不存判準版本或隔離閥狀態。〈回退〉只講「已凍結的迴圈回放會漂移」,沒講「閥開著時新凍結」。
5. 週五修好新判準、拿掉閥。回放按章用新判準判,得 `rc=0`,和 golden 不同,報「邏輯漂移:同一份凍結輸入重算判定不同」。
6. 這個漂移不是「關閥後回到一致」,而是永久紅。唯一出路是 `--freeze --note` 重凍,等於人工把紅燈洗成標準答案。這正是〈回退〉第三點自己警告過的事。
7. 預期做法:隔離閥開著時 `--freeze` 直接 rc2 拒凍,並讓 `replay_weekly` 在閥開著時跳過補漏凍結;或在 verdict 裡記 `rule_mode` 並讓回放比對。
8. 測試缺口:`t_quote_full_span_replay_follows_stamp` 只測章刪掉的情況,沒有任何測試涵蓋「閥開時凍結再關閥回放」。

## 2. 寫側為求 kind 同時跑兩版判準,新判準丟例外時,回退手段擋不住
severity: major
blocking: 是
引句:「由寫側同時用另一版判準算一次得出」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos:10964-10985`
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos:1622`

1. 起點:新判準 `full-span-v1` 對某類輸入丟例外。例如掃描時遇到某種跳脫或超深巢狀,導致 RecursionError 或 IndexError。
2. 時序:人照〈回退〉第二點設 `write_rule: legacy` 加 `read_override: legacy`。這時寫側用舊判準,舊判準擋下一個載體。
3. 照字面,擋下後仍要「同時用另一版判準算一次」才能填 `kind=legacy-only`。這次被算的是壞掉的新判準,所以例外在擋下訊息印出前或 `return 2` 前炸出來。
4. 結果:用戶看到 traceback。rc 不是 2,沒有 blocked 事件,下游若依 rc 判斷會走錯支。
5. 根因:現有 `_gate_event_or_warn` 保證「永遠不改變呼叫端判定」,但它只包住寫入,不包住組 note 的計算。spec 沒要求 kind 的計算要 try/except,也沒規定失敗時退成 `kind=unknown`。
6. 同理,`--compare-rules`、`gov` 和 `cats` 的計算也沒規定例外怎麼處理。
7. 預期做法:另一版判準的求值整段包 try/except,失敗時 `kind=unknown cats=err` 且擋下照舊;並在〈回退〉說明隔離閥與 `write_rule=legacy` 都不隔離這條路徑。
8. 測試缺口:`t_quote_full_span_compare_and_event` 沒有「其中一版丟例外」的案例。

## 3. `quote` 欄截斷 200 字,讓 `seat-check` 對長引句誤報出界並寫帳
severity: minor
blocking: 否
引句:「`quote` 欄最多存 200 字,超過截斷並加」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos:26787-26809`

1. `seat-check` 用 `_quote_rows(rtext, "")` 取 `q["quote"]`,再 `_quote_norm` 去材料裡找子字串。
2. 新判準的 `quote` 欄超過 200 字時尾巴會被換成「…(截斷)」。正規化後這段文字不在任何材料裡,於是 `anchored=False`。
3. 於是任何超過 200 字的合法引句,都被判成 `out_of_scope`,並且 `ledger` 有給時寫進出界引句帳(`seat-check` 是只觀測、不擋)。
4. spec 在 S4 把截斷當成輸出格式,但沒把「比對用完整文字、顯示用截斷文字」分成兩個欄位。
5. 預期做法:另帶 `full`(或只在顯示層截斷)。補一個 `seat-check` 長引句測試。

## 4. 把 `write_rule` 改回 `legacy` 的繞過,事後不可辨
severity: minor
blocking: 否
引句:「之後新記的帳蓋 `legacy`、寫側用舊判準」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos:10966-10985`

1. 時序:第二階段後,載體的後半編造被 `full-span-v1` 擋下,留下 `quote-rule:` 的 blocked 事件。
2. 有人(或有工具權限的編排者)把 `.lumos/config.json` 的 `write_rule` 改成 `legacy`,再記一次。舊判準放行,載體蓋 `quote_rule=legacy`。
3. 處置閘只印「引句判準:legacy(帳上章)」。`_QUOTE_RULE_STAMP_SINCE` 的警告只對「沒有章」的列觸發,不對「第二階段之後蓋 legacy」的列觸發。
4. 擋下事件和後來的 legacy 載體之間沒有任何連結。結果是 Issue 要擋的「編造後半」又能過,而且從帳面看不出來。
5. spec 的〈實務隱患〉只講「刪章」,沒有涵蓋「蓋 legacy」。
6. 預期做法:第二階段起加第二個常數,處置閘對「`ts` 晚於它且章為 legacy」的載體印警告;或在寫側同輪出現過 `quote-rule:` 擋下後蓋 legacy 時印警告。

## 5. 寫側讀兩次設定會讓章和檢查用的判準不同
severity: minor
blocking: 否
引句:「寫側(`cmd_canary` 驗載體引句那段)用 `write_rule` 檢查;檢查通過、寫入的那一列帶 `quote_rule=<write_rule>`」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos:10955-10985`
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos:11010-11087`

1. 檢查在約第 10965 行,`_jsonl_append_verified` 在第 11087 行附近,中間還有 sha 重驗和 T6 定錨掃帳。`_bound_tests_parallel` 這個範本每次呼叫都重新讀 config。
2. 時序:`canary record` 先讀到 `legacy`,用舊判準檢查通過。中途另一個會談或 `git pull --rebase` 把 config 改成 `full-span-v1`。章在寫列時才取值,結果是 `full-span-v1`。
3. 結果:一筆舊判準檢查的後半編造載體蓋上新判準章,處置閘必紅。帳只進不出,只能換迴圈編號整輪重記。
4. 機率很低(窗口是毫秒級),但後果是不可逆。
5. 預期做法:`write_rule` 在寫側開頭讀一次存成區域變數,檢查、`kind`、章、事件全用同一值。

## 6. 讀設定的專案根沒說清楚
severity: minor
blocking: 否
引句:「手動 `lumos quote-check <報告> --spec <快照>`:預設用 `write_rule`」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos:26515`
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos:12997-13003`

1. `cmd_quote_check(report, spec, as_json)` 是 vault-free,簽章沒有 `env` 或 root。要讀 `quote_check.write_rule` 就得靠 cwd。
2. 處置閘用 `--repo` 或 `_vault_repo_root(env)`。`seat-check` 和 `loop replay` 也是各有各的 root。
3. 時序:在 worktree A 對 worktree B 的報告跑 `quote-check`,或週跑在 main 跑回放時 worktree 的 config 不同。同一份報告可能因為 cwd 不同被判成不同結果。
4. spec 沒規定 `quote-check` 預設值從哪個根讀,也沒規定處置閘讀的是 `--repo` 還是 vault 根。
5. 預期做法:寫明「`quote-check` 以 cwd 向上找 `.lumos/config.json`,找不到用程式預設」,並規定處置閘和回放以 `_dsp_root`/`root` 為準。

## 7. 零引句擋下是否記事件,spec 沒定
severity: minor
blocking: 否
引句:「寫側擋下載體時(不論哪一版判準擋的),用 `_gate_event_or_warn(..., "canary", "blocked", note, hard=True)` 記一筆」
file: `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos:10967-10972`

1. 寫側有一條「載體報告沒有引句」的擋下(`_qrows is None`),不在「引句錯誤」那串訊息裡。
2. note 規格的 `cats` 集合只有 unclosed、stray、miss、short,沒有 none。照字面,零引句擋下要不要記事件、`kind` 填什麼都沒定。
3. 若記:`kind` 無法算(兩版都 None)。若不記:`gov --stats` 的「引句判準」那一格會漏算一類寫側擋下。
4. 預期做法:明寫「不記」或加 `cats=none`。

## 已讀、無 finding 的項目
- **同一輪重記與換載體**:`_disposal_round_groups` 不去重,同輪兩個載體是 rc2。換載體必須換迴圈編號,不會出現同輪兩個章。S5「同輪有無章的非載體列不影響」和 `latest` 取載體的現行取法一致。
- **`gov --stats` 讀到正在寫入的治理帳**:讀者遇到半截行會 `ValueError` 跳過,只少算一筆,不會拿到壞值。`id=` 隨機碼也避開了去重折疊。`_rej` 的分類是子字串,前綴 `quote-rule:` 目前不和 `report-not-normalized` 或 `findings-over-reported` 撞。
- **別的工作樹寫帳與讀帳**:舊版程式寫的帳沒有章、照舊判準判,這和當時寫側一致。〈兩階段上線〉已承認舊版讀新章會誤判。

總結:最高等級 major,blocking 共 2 條
