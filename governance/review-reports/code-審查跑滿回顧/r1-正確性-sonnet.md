severity: major

## 範圍與方法

- 逐 hunk 讀完 scripts/lumos 主體(1130 行);對照規格〈名詞〉合格回顧逐支走過 `_cap_retro_status` 的事件順序組合(人裁、回顧、再人裁、跳過、改檔、再 --record),實作與規格一致:D 取檔內最新一筆,E 取 D 之後最新一筆 recorded/skipped,skipped 不驗回顧檔,recorded 驗指紋再重跑檢查。這條沒找到會壞的輸入。
- 實跑環境:仿 `_cr_repo` 在臨時目錄造 repo 與帳(/private/tmp/claude-501/x/h.py、e1.py、e2.py),沒碰真帳、沒寫 repo 任何檔。

### F1 每個「回顧沒有/過期」的提示都印 `--template > cap-retro.json`,照貼會用空骨架覆寫已寫好的回顧檔
severity: major
blocking: 是 — 不可逆地毀掉人與代理已寫好的回顧內容,而且提示正好在最容易照貼的那一刻出現
- 輸入:有人裁紀錄的迴圈,回顧檔已寫好(或已 `--record` 後又改了一個字)。跑 `loop status --disposal`、`canary record` 新一輪、`loop next` 或 `doctor` 任一個。
- 走到哪:狀態是 none(檔寫了還沒 --record)或 stale(記過之後改了檔)→ `_cap_retro_template_cmd` 組出 `lumos loop retro X --template > governance/review-reports/X/cap-retro.json`,被 `_disposal_retro_step`(stale 分支緊接在「改好、--check 過了重新 --record」之後印出)、`_cap_retro_record_block`(「怎麼做」那行)、`_cap_retro_next_lines`、doctor I2、retro-stats 全部原樣印出。
- 壞在哪:`>` 重導向在 lumos 執行之前就把目標檔截成空檔;stale 分支同時叫人「改好」又叫人貼會清空這個檔的指令,兩句互相打架。模板也不看檔案存在與否,沒有 --force 或存在檢查。重現(e1.py 實跑):人裁 → 寫回顧 368 位元組 → --record → 改一個字 → `loop status --disposal` 印出 `lumos loop retro crx --template > governance/review-reports/crx/cap-retro.json` → 照貼執行後檔案變 1187 位元組的空骨架(`"why_cap": ""`),原內容沒了。檔在 governance/review-reports 底下通常未提交,救不回。
- 對照規格:〈二〉寫「骨架 JSON 印到標準輸出;該放的路徑與下一步指令印到標準錯誤(照 fix-check --record-template 的分流)」,沒有要求把重導向寫進每個提示;不可逆是本席鏡頭點名項。
引句:「    print(f"    {_cap_retro_template_cmd(root, loop_id)}")」
引句:「                         f"{_cap_retro_template_cmd(root, loop_id)}")」
- file: `scripts/lumos:13258`(`_cap_retro_template_cmd` 組 `--template >`)、`scripts/lumos:13361`(stale 分支印指令)、`scripts/lumos:13321`(record_block 的怎麼做行)
- 修法方向(不寫檔):只在 state 是 none 且檔不存在時才印重導向形式,其餘狀態只印 `--template` 不帶 `>`。

### F2 讀審查帳改用 `str.splitlines()`,遇到帳列裡的 U+2028/U+2029/U+0085 會把一列切成兩半、整列被當壞行吃掉,輪數少算
severity: minor
blocking: 否 — 輸入罕見,但會讓人裁紀錄記不進去,出口只有修帳
- 輸入:審查帳某一列的字串欄位(例如 note、auditor)含 U+2028 或 U+0085(貼自網頁的文字常見;`json.dumps(ensure_ascii=False)` 不會跳脫它們,而 \x0b/\x0c/\x1c-\x1e 會被跳脫所以不受影響)。
- 走到哪:`_retro_canary_load` 以 `text.splitlines()` 切行,該列被切成兩段,兩段都不是合法 JSON → `except (ValueError, RecursionError): continue` 靜默略過整列。同檔其他讀法(`loop status`、`loop next`、同檔 `_retro_gov_events` 的 `split(b"\n")`)都只在 `\n` 切,所以兩套讀法對同一本帳看到的列數不同。
- 壞在哪:e2.py 實跑:三輪帳,第三輪那列 note 含 U+2028。`loop next crx --json` 回 round 3、cap 3;`loop cap-decision crx --decision extra-round ...` 回 2「帳上只跑了 2 輪,還沒到 standard 的上限 3 輪」,記不了人裁。同理 `_cap_retro_record_block` 會把 r3 當成不在帳上的新一輪(`round_id in _retro_ledger_rounds(rows)` 為假)而誤擋或誤放,`--check` 的 evidence 與起草者比對也少一列。
引句:「    for ln in text.splitlines():」
- file: `scripts/lumos:12990`(`_retro_canary_load`);對照既有讀法 `scripts/lumos:11540` 一帶 `loop status` 的逐行讀、`_drift_jsonl_iter`(只在 \n 切行)
- 修法方向:改成 `text.split("\n")`,跟其他讀者同形。

## 判不影響或判定一致的項目

- 空集合/單一元素:`rounds` 為空的帳 → `cap-decision` 在 `_cap_hint_scope` 回 None 被擋(rows 空);`_cap_retro_check` 的 `families`/`changes` 空清單一律報錯,對得上。
- 冪等:`--record` 同一份檔重跑只多一筆 recorded,取最新一筆,指紋相同仍合格。`cap-decision` 同參數重跑會多一筆新的 D,使先前的 recorded/skipped 不再「在 D 之後」而回到「沒有」——這是規格〈名詞〉要的行為(之後再記人裁要重新回顧或跳過),不算 bug;提示文字有講。
- 新舊互讀:舊帳沒有 loop-retro 事件 → `_cap_retro_status` 的 di 為 None → applies False,第八步印 —,七步輸出不變(S3 測試對比其餘七步行)。舊程式讀新事件:`loop-retro` 已登記 `_KNOWN_GATES`;不在 design-loop/code-loop 底下,不進 `loop list` 關門判定。沒找到會壞的路徑。
- 寫一半:`cmd_loop_cap_decision` 先 `_gate_event` 再印提示,後面的 `_retro_dossier_seen` 即使丟例外,人裁已落帳;實測 report_path 含 NUL 也沒丟(`_retro_has_dossier` 先在資料夾判斷擋)。`_gate_event` 回 None(沒有 docs/)與 False 都走 `ok is not True` → rc 1,與規格一致。
- 衍生資料(同編號多筆):取「檔內順序最後一筆 D」與「D 之後最後一筆 E」,`_cap_retro_scan` 與 `_cap_retro_status` 用同一種取法;`cmd_loop_retro` 的 `dec` 用 `reversed(events)` 取最後一筆,與狀態判定同一筆。
- 時間:全程不比時間戳,只用檔內順序,無時區問題。
- 與既有事故/合約對照:canary-audit ★INVARIANT★「回報成功 ⟺ 落盤可讀回」——擋點在寫入之前 return 2、不印 ✓,不破;Issues/canary-record未落盤事件的 readback 路徑沒被改。design-loop 的 PITFALL「凡按迴圈編號讀審查帳要略過 spec-gate」——新讀者 `_retro_canary_load` 有略過,不破。loop-convergence-recording 的「巢狀極深 JSON 丟 RecursionError」——新讀者有接。design-loop ★INVARIANT★ 處置閘第五步等既有步驟:diff 只在尾端加第八步、橫幅 `_extra` 多一項,前七步判定行測試比對不變,不破。reversibility-governance-ledger:新事件走既有 `_gate_event`,未碰鎖與本機帳分流(loop-retro 不在 `_GOV_LOCAL_PAIRS`,進版控帳,與規格一致)。
- ⚠ 設計層(不計入 finding,判不準):人裁 `extra-round` 之後回顧合格,`canary record` 對 r5、r6 …… 的新一輪都放行(`st["state"] in ("recorded","skipped")` 直接回 None),人只授權了「再開一輪」。規格〈三〉1 的文字就是這樣寫,實作與規格一致;是否要限制只放一輪由設計裁。
- 角色卡:`LUMOS-ROLE-CARDS: on` 但尾端沒有附卡,略過。

總結:最嚴重 major,blocking 1 條
