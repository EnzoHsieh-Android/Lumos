severity: minor

我只讀了 r3-repair.patch、r3-snapshot.patch,以及固定版本 4ef433e 的 `scripts/lumos` 與 `scripts/test_lumos.py`。上輪席報告與 intake 沒讀。下面 `lumos:` 行號都是 4ef433e 版的行號。

## 一、分層與依賴方向

這一輪修補沒有跨層直呼。

- 判定函式沒有寫帳或印訊息。`_cap_world_case` 與 `_cap_retro_fix_cmd` 仍是純函式,回字串或情況值。印訊息的是命令層 `cmd_loop_cap_decision`。
  - 對照 file: `scripts/lumos:22406`(`_cap_world_case`)、`scripts/lumos:22682`(`_cap_retro_fix_cmd`)。
- 共用判定沒有反過來依賴呼叫端。這輪新增的只是命令層先組好一個輸入,再交給共用判定。
- 有一個依賴上的小注意,記在 A1:命令層第一次自己組了一個假事件,餵給共用判定 `_cap_world_case`。其他呼叫端給它的都是從帳上讀到的真事件。這不算跨層,但輸入來源跟別處不一樣。

我沒有找到不對齊的地方。

## 二、命名與錯誤處理

命名跟鄰居一致。

- 變數從 `_gerr` 改成 `gerr`,跟 `cmd_loop_retro` 的 `events, gerr = _retro_gov_events(...)` 同名。file: `scripts/lumos:22989`。
- 兩支新測試命名是 `t_cap_retro_template_write_world_fill` 與 `t_cap_decision_world_fill_ledger_unreadable`,跟 `t_cap_decision_world_fill_reads_ledger`、`t_cap_retro_fix_cmd_world_fill_everywhere` 同族。
- 測試也同樣掛 `@_cap_real_cutoff`,docstring 開頭同樣是 `[代碼審 rN …]` 標記。
- 換掉模組函式的寫法,跟同層的 `t_cap_decision_world_fill_reads_ledger`、`t_prepush_nogo_std_reads_gov_once` 一致:
  - 先存 `orig`。
  - 在 `try/finally` 裡指派 `m._retro_gov_events = flaky`,`finally` 還原。
  - 用 `contextlib.redirect_stdout` 在行程內收輸出。
  - 另有 `check("A1 前置…")` 證明被測那條路真的走到。
  - 對照 file: `scripts/test_lumos.py:103743`(原 t_cap_decision_world_fill_reads_ledger),以及 4ef 版測試檔裡 78760 起的 `t_prepush_nogo_std_reads_gov_once`。
- 「讀終端輸出」那支用子行程跑 `_cr_retro(c, "--template", "--write")` 再讀 `r.stderr`,跟 `_cr_record`、`_cr_gate` 的寫法一致。

讀帳失敗的處理跟鄰居不一致,見下面 A1。

### A1 讀不到帳時,不報原因、也不走既有的 gov-bad 路,改成自己組一個假的人裁事件
severity: minor
blocking: 否 — 結構上仍走唯一決定處(`_cap_world_case`、`_cap_retro_fix_cmd`),沒有另立第二個判定函式;只是處理方式跟其他 `_retro_gov_events` 呼叫端不同。
引句:「dec = ({"decision": decision} if gerr else next((e for e in reversed(evs) if _retro_is_decision(e)), None))」
file: `scripts/lumos:22989-22991`(`cmd_loop_retro` 讀不到帳就擋下 rc 2,不繼續)
file: `scripts/lumos:22624-22636`(`_cap_retro_status` 讀不到帳就判 `state="gov-bad"`)
file: `scripts/lumos:22892-22894`(`_cap_retro_next_lines` 對 gov-bad 印「判不了有沒有人裁紀錄:原因」,並給 `_cap_retro_fix_cmd(root, loop_id, 'gov-bad')`)
file: `scripts/lumos:68638-68642`(`_codeloop_pass_accept_risk` 讀不到帳回 `(False, err)`)
file: `scripts/lumos:22223-22225`(`_retro_gov_events` 的說明要求呼叫端「當成帳壞(fail-closed)」)

說明:專案裡其他讀帳失敗的呼叫端都有兩件事。

- 把原因帶出來:印出、回傳,或放進 `problems`。
- 指向「修帳」的出口。`_cap_retro_fix_cmd_body` 的 gov-bad 那一支叫人把治理帳換回一般檔,或改權限。

這一輪新增的那一支有三個不同:

1. `gerr` 被吞掉,沒有任何輸出。
2. 它用 `'none'` 狀態的指令,也就是叫人跑 `--template --write`。但同一個帳壞時,`cmd_loop_retro` 會在開頭回 2,印「擋下:{gerr}」。使用者照做會撞牆,跟 `_cap_retro_fix_cmd` 說明裡「每種狀態都給走得通的指令」不合。
3. 它用 `{"decision": decision}` 這種沒有 `ts` 的假事件餵 `_cap_world_case`,靠「`ts` 不是字串就判 required」這條偏嚴規則。偏嚴方向跟 gov-bad 的 fail-closed 同向,但手法是新的。

⚠ 這條我判 minor,不判 major。理由是它沒有另立判定函式,偏嚴方向也和既有的 fail-closed 同向,而且這支提示只印不擋。是否算「引入第二種讀不到帳的處理」,由編排者裁。若認為算,這條升為 major。

## 三、第二種做法

- 測試端沒有引入第二套換掉模組函式的寫法,見第二節。讀 git 的部分,這輪沒有改動,只改了 docstring,依舊用 `subprocess.run(["git","-C",…])`。
- 讀不到帳的失效方向:專案現有的是「擋下」、「判 gov-bad」、「回 `(False, err)`」三種,都是帶著原因 fail-closed。這輪新增的是第四種「吞掉原因、用呼叫端手上的值組事件、照偏嚴繼續」。是否構成第二種做法,取決於 A1 的 ⚠ 判斷。依我的嚴重度錨,結構上沒有新增判定者,所以只列 minor。
- 另外,`_cap_retro_scan` 的單迴圈失敗分支會塞 `{}` 當 decision,`_cap_world_case({})` 回 `ignored`。那一支偏寬。專案裡本來就有偏寬、偏嚴兩種,這輪沒有造成新的分歧,只是加一個偏嚴的點。file: `scripts/lumos:22766`。

不對齊共 1 條,其中 major 0 條
