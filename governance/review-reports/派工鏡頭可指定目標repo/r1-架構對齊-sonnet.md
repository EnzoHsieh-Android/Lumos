severity: minor

我只讀了材料和 lens-repo(`/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo`)的 scripts/hooks/claude/*.py、scripts/lumos、scripts/test_lumos.py,沒改任何東西。

整體沒有引入第二種做法,也沒有跨層直呼。四條都是照既有寫法補強即可的偏差。

先釐清兩件事。
- 帶有 `_trusted_lumos` 的掛鉤其實是四支:dispatch-lens-hook、check-graph-sync、lumos-entry-hook、impact-hook。不是五支。
- 守衛(`scripts/test_lumos.py:17450` 一帶)是用正規式 `def _trusted_lumos\(\):.*?\n    return None\n` 抽函式比對。只要新的資料夾版函式不叫 `_trusted_lumos`,計劃另寫一支、不改逐字複本的做法就不會讓守衛紅。這點對齊。

原因代碼表分開也對齊既有做法。
- 掛鉤自己的 `LENS_FAIL_REASONS`(dispatch-lens-hook.py:54)本來就是只收 lumos 印出的代碼。
- lumos 端 `_dispatch_lens_fail`(scripts/lumos:48752)的註解指向它。
- 掛鉤自己產生的六個 `repo_*` 代碼 lumos 從來看不到,放另一張表是合理的。
- 只有一個小提醒:lumos 該函式註解寫「六種」,加了 `spec_missing`、`spec_outside_repo`、`no_knowledge` 後要跟著改,否則會過期。

---

severity: minor
blocking: 否 — 掛鉤在信任確立前不能跑 git,所以不能照專案一貫用 git 解析 gitdir,是有理由的偏離;缺的是已有的防護寫法沒帶過來。
引句:「找到共用的 git 資料夾;都沒有就不是 repo 根」
對照:file: `scripts/lumos:27052`(`_events_main_trusted` 讀 `.git/worktrees/*/gitdir`,有處理相對路徑、有反向驗證)、file: `scripts/lumos:26910`(`_events_root` 用 `_lens_git(… --git-common-dir)`)
判定理由:專案裡沒有人解析「工作樹 `.git` 檔裡的 `gitdir:` 加 `commondir`」,所以這是一套新寫的手工解析。既有的 `_events_main_trusted` 有兩項防護,計劃都沒寫:
- 新版 git 可以把 gitdir 寫成相對路徑,要照 `.git` 檔所在目錄解讀。
- `.git` 檔可被改成指向別的 repo,所以要驗證反向指回。

建議把這兩條補進做法 2。不補的話,相對路徑的工作樹會被誤判成 `repo_not_root`,或被導去別人的 git 資料夾。

---

severity: minor
blocking: 否 — 新舊兩套檢查現在都在同一支掛鉤內,沒有跨檔漂移的風險;缺的只是漂移守衛。
引句:「所以另寫一支資料夾版,不改它」
對照:file: `scripts/hooks/claude/dispatch-lens-hook.py:308`(`_trusted_lumos` 內的 `_ok`),守衛在 `scripts/test_lumos.py:17450` 一帶
判定理由:資料夾版會把「擁有者是自己、自己與父目錄都不是 group/other 可寫」的判準再寫一次。專案既有的手法是複製加守衛,新的這份只靠註解和人記得。
- 做法 2 要求資料夾、父目錄、git 資料夾(工作樹時連共用的那個)都檢查,比 `_ok` 多一層,這個差別是故意的,沒問題。
- 建議驗收條款加一條測試,比對兩邊都擋 group/other 可寫與非自己擁有者。

---

severity: minor
blocking: 否 — 掛鉤自己多跑一次 git 沒有安全問題,但責任重疊,而且會吃掛鉤的逾時預算。
引句:「擋下的路徑一次 git 都不跑。」
對照:file: `scripts/hooks/claude/dispatch-lens-hook.py:371`(掛鉤只用 subprocess 叫 `lumos dispatch-lens --repo`,自己不跑 git)、file: `scripts/lumos:47386`(`_lens_git`)
判定理由:現有掛鉤把「找 repo 根」整個交給 lumos。計劃讓掛鉤在信任檢查之後自己跑一次 `git -C … rev-parse --show-toplevel`,再把同一個路徑交給 lumos 又跑一次。
- 這是掛鉤層第一次直接呼叫 git,要另外算進 `_inner_budget`。
- 「只收 repo 根」可以改成由 lumos 的 `--repo` 路徑去判。
- 若堅持留在掛鉤,請在計劃寫明為何不下放,並寫明這次 git 呼叫的逾時從哪裡扣。

---

severity: minor
blocking: 否 — 屬刻意的更嚴格規則,但沒和既有標記對照寫明。
引句:「同一份派工詞出現兩行以上,視為不合格」
對照:file: `scripts/hooks/claude/dispatch-lens-hook.py:164`(`find_marker`)、file: `scripts/hooks/claude/dispatch-lens-hook.py:273`(`find_spec_marker`)
判定理由:既有標記一律「取第一個命中、其餘忽略」,而且用 `\S+`。新標記改成「重複就整個拒絕」,並用 `(.+?)` 允許路徑含空白。
- 理由充分:路徑有注入面,重複標記有歧義。
- 但同一個掛鉤裡兩種標記的重複語意不一樣。建議在計劃或掛鉤註解寫明這是刻意不同,避免之後有人「統一」成取第一個。

---

共 4 條不對齊,全是 minor,major 0 條。
