severity: minor

我讀了三份修補檔,對照 `/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/` 裡的掛鉤、計劃與兩篇 Systems 節點,並實際跑了測試。

**已確認與程式一致的部分**
- **行程群組收法**:說法與 `scripts/hooks/pre-push` 一致,有兩處:`_pp_kill_jobs` 先對 `-pid` 整組送 TERM,失敗才退回只送本人;起片時先 `os.setpgid(0,0)` 再 `execv`。非組長的子殼確實走退回路徑。`$PY` 是絕對路徑,`execv` 不會找不到。
- **start_new_session 的歸屬**:計劃說測試自己用 `start_new_session` 起的子行程由那支測試負責,與程式一致,片的群組收不到它們。
- **只有子殼收到 HUP**:實際路徑是子殼的 HUP 陷阱收片、`exit 129`,`_grc` 非零,`_rc=1`,掛鉤 `exit 1`。「回 1」與程式一致。
- **綁定測試有殺傷力**:`t_prepush_interrupt_stops_every_gate` 跑了 34 條全綠,我再在複製的工作樹上做了三種破壞,各自紅燈:
  - 拿掉子殼的 HUP 陷阱,⑪ 紅。
  - 子殼 HUP 陷阱改成 `exit 0`,⑪ 紅(rc=0)。
  - 整組收改成只收本人,⑩ 與 ⑪ 紅。
  - 整組收拿掉退回路徑,⑥⑦⑨⑩ 紅。
- **善後**:複製的工作樹已刪,沒有殘留的 `sleep` 或 `lumos-prepush` 暫存。
- **四句原因句**:計劃第 63 行的四句與 `pp_cl_reason` 及 `_PPC_KIND_SENTENCES` 逐字相同。「ref 名不含 ASCII 控制字元」那句修補,與 `bound-tests-gate` 第 128 行的 U+2028、U+0085 說法相容。
- **其他**:S13 的 WHY 修補與 `t_code_loop_keep_going_pass_sites_keep_blocks` 的 AST 守衛一致。固定席節點裡的 INVARIANT(`lumos-cli-read`、`guard-kill`)這次改動沒碰到;`code-loop守衛main-direct盲區` 與這次改動無關。

以下四條都不放行相關。

severity: minor
blocking: 否 — 只是條款沒跟上新增的斷言,行為本身有測試守住
引句:「⑪只對跑測試的子殼送 HUP(代碼審 r3 邊界席 2、合約席 3:原本只有主殼收到訊號的情境」
問題:S10 條款(計劃第 105 行)這輪沒動,修補只把第 116 行的 S1–S17 改成 S1–S18。S10 現在只講「收掉全套測試的各片,不留 ppid=1 的孤兒」。新增的斷言有兩類:片自己起的孫行程要一併收掉(⑩,共三處),子殼單獨收到 HUP 要收片且掛鉤不放行(⑪)。這兩類只出現在〈做法〉第 2 點的散文和測試 docstring,沒有可驗收的條款句。
失敗情境:有人把「整組收」退回「只收片本人」,或拿掉子殼 HUP 陷阱,測試會紅,但對照條款找不到被違反的那一句,看不出這是被規格保護的行為。
佐證:計劃 `docs/lumos-toolchain-knowledge/Projects/推送前一次列出全部擋下原因_計劃.md:105`;`scripts/test_lumos.py:65025`。

severity: minor
blocking: 否 — 程式行為正確,只是測試比條款鬆、使用者看到的訊息誤導
引句:「子殼結束碼非零,掛鉤當成測試沒過擋下(不能放行;擋下時照設計把測試 log 複製一份到 TMPDIR 給人看」
問題:實際路徑是子殼 `exit 129`,`_grc=129`,`_rc=1`,掛鉤印「擋下:test_lumos.py 有紅」後 `exit 1`。這個回 1 沒寫進計劃或 Systems 節點(只說「由它自己的 HUP 陷阱收」),⑪ 只驗 `rc not in (0, None)`。
失敗情境:子殼被掛斷時,使用者會看到「有紅」,但「紅的是這幾支」是空的(沒有任何測試真的紅)。把回傳碼換成別的非零值(例如直接回 129)不會讓 ⑪ 紅,等於這個回傳碼沒被釘住。
佐證:`scripts/test_lumos.py:65025`;`scripts/hooks/pre-push:829`、`pre-push:862`。

severity: minor
blocking: 否 — 掛鉤現況沒有被漏掉的寫法,是守衛視野比修補前變窄
引句:「${…}、$(…) 先收成一個字,免得下面按 {}() 切段時把它們切開」
問題:新掃描器先把所有 `$(…)` 與 `${…}` 收成 `$x`,所以指令替換裡的「寫進檔案又 `2>/dev/null` 沒包組」整段看不見。引號內容也先換成 x,`"$(…)"` 同樣被遮住。我把新舊掃描器各跑同一批字串:`v="$(printf x >> "$f" 2>/dev/null)"` 與 `v=$(printf x >> "$f" 2>/dev/null)` 舊正則回 [1]、新的回 []。指令替換裡的重導向開檔失敗訊息會漏到掛鉤的 stderr,這正是守衛要擋的形狀。作者補的 7 個手寫例子裡沒有這一型。另外 `&>>` 也漏(舊正則抓得到,新的抓不到),但掛鉤目標是 bash 3.2,影響較小。
失敗情境:日後有人在 `$(…)` 裡寫 `printf x >> "$_f" 2>/dev/null`,④ 照綠,開檔雜訊漏出。這與測試 docstring 的「同族一次掃完」不符。
佐證:`scripts/test_lumos.py:64647`;我另外手測的對照在對話裡。我 grep 過 `scripts/hooks/pre-push`,目前沒有這型寫法。

severity: minor
blocking: 否 — 句子現在三處一致,風險只在日後有人改計劃
引句:「(不從掛鉤或 scripts/lumos 讀,免得跟著一起錯;要改句子先改計劃那段)」
問題:四句原因句雖然定了計劃第 63 行為正本,但沒有任何測試讀計劃。`t_prepush_cl_reason_table_matches_lumos` 只比掛鉤對測試常數,所以「先改計劃再改兩處」純靠自律。
失敗情境:有人先改計劃,或只改計劃,所有測試仍綠,正本與實作靜默分岔。補一條讀計劃那一行、逐字比對四句的守衛即可。
佐證:`scripts/test_lumos.py:64692`、`scripts/test_lumos.py:64694`;計劃第 63 行。

最高等級 minor,blocking 0 條。
