severity: minor

席名:通才-r3-sonnet(第 3 輪,鏡頭:通才,重點看使用者照提示操作會走到的路徑與第二輪修補自己引入的問題)。

已查、沒找到問題的部分(不編號,給收貨端知道看過哪裡):
- `_ledger_tail_needs_newline`、`_regular_own_fd`、`_esc_clean`、`_loop_records` 的其他呼叫者:`_regular_own_fd` 全檔只有 5 個呼叫處,新參數 `require_owner` 預設 True,舊呼叫行為不變;`_ledger_tail_needs_newline` 三個呼叫者(`_gate_event`、`_append_governance_log`、`_drift_ledger_append`)的路徑,`_drift_ledger_path_err` 本來就擋符號連結,所以改用不跟捷徑的開檔不會讓 `_drift_ledger_append` 漏補檔尾換行。
- `_ledger_lines` 讀 26MB(12 萬列)帳實測 0.12 秒;`cmd_loop_status` 與 `cmd_severity_check` 讀檔走文字模式(換行已被轉成 \n),換成 `_ledger_lines` 不改變列數。
- `--template --write` 的符號連結檢查:卷證資料夾是捷徑時回 2、repo 外不出現檔(實跑確認)。

### F1 回顧檔已在但讀不了或超過 256KB 時,提示叫人跑 --check,而 --check 又印同一句提示 (修補引起)
severity: minor
blocking: 否 — 有出口(`--skip` 與手動處理檔案),而且只有一句提示繞圈,沒有誤放行或誤擋帳。
- 輸入:回顧檔 `cap-retro.json` 存在且是一般檔,但大於 256KB(或權限 000);人裁已記、回顧沒記(狀態「沒有」)。
- 走到:`--check` 或處置閘 → `_retro_read_bytes` 回錯誤 → 組訊息時呼叫 `_cap_retro_fix_cmd(root, loop_id, 'none')`;該函式 `lstat` 到的是一般檔,走到「回顧檔已在、還沒記」那一支,叫人跑 `--check` 過了再 `--record`。
- 壞在哪:`--check` 就是剛剛印這句的指令,印出一模一樣的提示,形成繞圈;這正是第二輪聲稱要消滅的「兩條提示互相叫對方先做」。處置閘在超過 256KB 時還印「這筆人裁之後的回顧沒有」,跟檔案已存在矛盾。
引句:「return f"回顧檔已在、還沒記:{_retro_cmd(loop_id, '--check')} 過了再 {_retro_cmd(loop_id, '--record')}"」
- 佐證行:file: `scripts/lumos:13301`(`_cap_retro_status` 的 `none` 分支不看檔案讀不讀得了,直接回 `none`)
- 重現(臨時 repo,用測試的 `_cr_repo/_cr_loop/_cr_decide` 造帳):
  - `p.write_text("x"*300000)` 後跑 `loop retro crx --check`,實際輸出:`✗ 回顧檔超過 256KB(至少 300000 位元組):... → 回顧檔已在、還沒記:lumos loop retro crx --check 過了再 lumos loop retro crx --record`
  - 同一個檔跑處置閘:`[disposal] 跑滿回顧: ✗ — 人裁記了 extra-round,這筆人裁之後的回顧沒有 ...    回顧檔已在、還沒記:lumos loop retro crx --check 過了再 ...`
  - `chmod 000` 的檔同樣印出同一句提示。

### F2 卷證資料夾是符號連結時,提示叫人跑 --template --write,而 --write 會拒絕 (修補引起)
severity: minor
blocking: 否 — 拒絕訊息本身講清楚原因,使用者看得到出口,只是提示指令跟實際行為對不上。
- 輸入:`governance/review-reports/<編號>` 是指向 repo 外(或 repo 內別處)的符號連結,人裁已記,回顧檔不存在。
- 走到:處置閘第八步、`cap-decision` 成功訊息、`--check` 失敗訊息 → `_cap_retro_fix_cmd` 只 `lstat` 回顧檔本身(最後一段),資料夾是捷徑它看不出來,回「檔不在 → --template --write」。
- 壞在哪:使用者照貼 `--template --write`,被第二輪新加的檢查擋下回 2。第二輪的〈提示〉規格(計劃〈二〉)只涵蓋「回顧檔位置是資料夾或捷徑」,沒涵蓋「上層資料夾是捷徑」,兩個修補互相沒對上。
引句:「是捷徑、或解析後不在 repo 根底下——不在那裡建回顧檔」
- 佐證行:file: `scripts/lumos:13355`(`_cap_retro_fix_cmd` 只判 `os.lstat(p)`)
- 重現(臨時 repo,把 `rdir` 搬到 tmp 再 `os.symlink` 回來):
  - 處置閘印 `[disposal] 跑滿回顧: ✗ ... lumos loop retro crx --template --write`
  - 跑 `loop retro crx --template --write` 實際輸出:`擋下:卷證資料夾 governance/review-reports/crx 是捷徑、或解析後不在 repo 根底下——不在那裡建回顧檔`,rc=2
  - `--check` 同時印 `→ lumos loop retro crx --template --write`,rc=1。

### F3 計劃〈實務隱患〉仍寫處置閘讀帳迴圈用 splitlines,第二輪已改掉,內部不一致
severity: minor
blocking: 否 — 只是說明文字過期,不影響行為。
- 輸入:讀計劃〈誠實界線〉那條「代碼審 r1 修正時發現、不在本案範圍的既有缺口」。
- 走到:第二輪把 `cmd_loop_status`(處置閘讀審查帳的那段)與 `cmd_severity_check` 改成 `_ledger_lines`。
- 壞在哪:計劃這條沒跟著改,仍說「處置閘自己的讀帳迴圈…仍用 splitlines」;下一個讀的人會以為處置閘還有 U+2028 劈列問題,或白白再去修一次。同條也沒記第二輪順手把 `_drift_ledger_append` 併進共用帳尾檢查。
引句:「處置閘自己的讀帳迴圈、doctor S12、`_loop_close_stamps` 仍用 `splitlines` 切行」
- 佐證行:file: `docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md:188`;`scripts/lumos:11024`、`scripts/lumos:11256` 附近仍有別的 splitlines 讀帳點(跟這條說明要列的名單對不上,名單該核對一次)

總結:最嚴重 minor,blocking 0 條
