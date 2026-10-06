severity: minor

席名:通才-r2-sonnet。範圍:diff 的 scripts/lumos 全部逐 hunk;測試與 skills 當查證材料。

## 查過、沒問題的(給收貨端對帳)
- `--write` 互斥:`--template/--check/--record/--skip` 先過「挑一個」的計數,`--write` 再要求必須同 `--template`;`--write --check`、`--write --skip` 都回 2,沒有漏口。
- FAIL 橫幅抽成 `_disposal_fail_banner`:正常路徑 `{loop_id} 輪 {rid}: …`、帳壞路徑 `{loop_id}: 跑滿回顧`,逐字等於修正前兩處的輸出。
- `_loop_records` 改走 `_canary_ledger_scan`,既有呼叫端是 `lumos:9303`、`9410`、`12391`、`13743`。行為差異只有三項:切行改 `split("\n")`(不再把含 U+2028 的列劈壞)、非物件列改成跳過(舊碼會 AttributeError)、整本非 UTF-8 照舊丟 UnicodeDecodeError。對正常帳輸出不變。整本讀入記憶體:實檔 3MB,和舊碼逐行 json.loads 同量級,可接受。
- 回滾:拔掉功能後,寫入器補換行只會在檔尾不完整時多一個空行,讀側都跳空行;`_loop_records` 的新讀法不依賴任何回顧代碼,留著安全。
- 過度設計:`_disposal_fail_banner` 兩個呼叫處、`_cap_retro_fix_cmd/_stale_hint` 各自有對應的不同提示文字,都有實用;沒有發現不需要的抽象。

### F1 錯誤訊息裡的指令編號沒加引號,照貼會執行編號裡的 shell 片段(修補引起)
severity: minor
blocking: 否 — 編號要是使用者自己給的、且要先有人裁紀錄與卷證資料夾才走得到,攻擊面窄;但訊息明說「照貼」,同一輪修補已替姊妹函式加了 shlex.quote,這一處漏了
- 輸入:`lumos loop retro 'x;touch PWNED' --check`(編號只含 `;`,過得了 `_retro_id_bad`),回顧檔不存在。
- 走到:`_cap_retro_check` 的讀檔失敗分支。
- 壞在哪:訊息印出 `lumos loop retro x;touch PWNED --template --write`,照貼會多執行 `touch PWNED`;而同一輪新增的 `_cap_retro_template_cmd` 對同一編號印的是 `lumos loop retro 'x;touch PWNED' --template --write`(有引號)。兩處不一致。`cmd_loop_retro` 的成功行 `下一步 lumos loop retro {loop_id} --record` 與 `--check` 後的 `--record` 提示也沒引號。
引句:「(lumos loop retro {_esc_clean(loop_id, 60)} --template --write 產骨架)」
- file: `scripts/lumos:13180` 附近的 `_cap_retro_check`(現檔查 `grep -n "產骨架" scripts/lumos`)。
- 重現(臨時目錄,不寫 repo):用 SourceFileLoader 載入 scripts/lumos,呼叫 `_cap_retro_check(tmpdir, "x;touch PWNED", None, [], None)`,輸出的訊息含未加引號的 `lumos loop retro x;touch PWNED --template --write`;呼叫 `_cap_retro_template_cmd(tmpdir, "x;touch PWNED")` 則是 `lumos loop retro 'x;touch PWNED' --template --write`。
- 附帶:`_esc_clean(...)` 套在已 quote 的字串外面,控制字元會被換成空格,帳上編號含控制字元時印出的指令不是原編號(只影響帳上異常編號,不另列)。

### F2 寫入器補換行只補了兩支,同帳的其他寫入器還是會把新事件黏到半行後面(修補引起)
severity: minor
blocking: 否 — 要先有「上一次寫一半」的斷尾才發生;但同一根因的路徑沒有一併處理
- 輸入:帳檔最後一個位元組不是換行(上次程序被殺),再記一筆。
- 走到:只有 `_gate_event` 與 `_append_governance_log` 呼叫了 `_ledger_tail_needs_newline`。審查帳的寫入器 `_jsonl_append_verified`(canary record 走它)、以及治理帳的另外兩個直接 `open(..., "a")` 寫入點(code-loop pass 留痕、另一處 `.governance-log.jsonl` 事件)沒有補。
- 壞在哪:審查帳是回顧擋點與處置閘第八步的資料來源。斷尾後下一次 canary record 會寫出 `{半行}{完整行}`,讀側丟掉整個黏合列,而 `_jsonl_append_verified` 的自驗讀不回該 token,回 2「落盤自驗失敗」,但那一行其實已在檔裡。
引句:「if _ledger_tail_needs_newline(path):」
- file: `scripts/lumos:9703`(`_jsonl_append_verified`)、`scripts/lumos:44178`、`scripts/lumos:44999`(都是 `open(..., "a")` 直接寫,沒有補換行)。
- 重現:臨時目錄造 `.canary-log.jsonl`,內容末尾放一行不帶換行的半截 JSON,再跑 `canary record`(單一測試形狀同 `t_cap_retro_bad_ledger_fail_closed`),觀察落盤自驗失敗。未實跑,依代碼路徑判定。

### F3 「回顧沒有」狀態印的指令在回顧檔已存在時必定回 2,而且沒提 --check/--record(修補引起)
severity: minor
blocking: 否 — 失敗是安全的(不覆寫),只是提示在最常見的中間狀態(已起草、還沒 --record)指向一條走不通的路
- 輸入:已用 `--template --write` 建好回顧檔、填了一半,但還沒 `--record`;此時跑 `lumos doctor`、`loop next`、處置閘或 `retro-stats`。
- 走到:狀態是 `none`(治理帳上沒有 recorded 事件),`_cap_retro_fix_cmd` 對 `none` 一律回 `_cap_retro_template_cmd`,也就是 `… --template --write`。
- 壞在哪:這條指令對已存在的檔回 2「回顧檔已經存在…要重來先自己刪掉」。使用者照貼得到一個叫他刪掉自己心血的訊息;doctor I2 的那行只印這條指令,看不到要做的其實是 `--check` 再 `--record`。
引句:「lumos loop retro {_shlex.quote(loop_id)} --template --write」
- file: `scripts/lumos` 的 `_cap_retro_fix_cmd`(現檔 `grep -n "def _cap_retro_fix_cmd" scripts/lumos`)。
- 重現:`_cr_repo()` 造迴圈、記人裁、跑 `loop retro crx --template --write` 後再跑 `lumos loop retro-stats`,「沒有」那行仍印 `--template --write`;再跑一次該指令得 rc=2。未實跑,依代碼路徑判定。

總結:最嚴重 minor,blocking 0 條
