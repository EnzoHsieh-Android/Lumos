severity: minor

整體讀完,沒有會做出錯誤行為、破壞合約或損壞資料的洞。只有一條 minor(F1)。

### F1
severity: minor
blocking: 否
file: `scripts/lumos`:`_lint_new_cli_items`(diff 檔裡 `cmd_lint_new` 後面那段)
引句:「…其餘 {len(new) - _LINT_NEW_CLI_SHOW} 條沒列(全部看 lumos code-loop check --diff {lv.get('range')} --json)」

失敗場景:`lint-new` 的設計是不寫治理帳。超過 20 條時它卻叫人去跑 `code-loop check --diff … --json` 看全部。那支指令不是唯讀,會寫帳,也會真跑合約測試。

實跑(臨時 repo,25 條 BAD):
```
$ lumos lint-new --diff $B..HEAD
  …其餘 5 條沒列(全部看 lumos code-loop check --diff 68e5cab4…..HEAD --json)
治理帳行數 4 → 4(lint-new 沒寫帳)
$ lumos code-loop check --diff $B..HEAD --json   # rc=1
治理帳行數 4 → 7,多了:
  bound-tests/no-pins、lint-new/fail-open、code-loop/blocked(hard:true)
```
照提示做會多出一筆硬擋帳,污染擋下統計,正是 `lint-new` 想避免的事。

建議:提示改成「用 `--json` 的唯讀指令」,或在 `lint-new` 加 `--json` / `--all`。

測試缺口(不另標條):`t_lint_new_cli_status_codes` ③只驗印了 20 條和「5 條」,沒驗提示指令無副作用。把提示改成別的指令,測試照綠。

### 實驗結果(臨時 repo,已刪)
- `lint-new --diff $B..HEAD`:
  - 有新增告警時 rc1,印 `app.py:2 [R1] no BAD` 和填好指紋的放行指令。
  - 三點範圍 `main...HEAD` 同樣判 blocked。
  - `HEAD..HEAD` 判 no-files、rc0。
  - `nosuch..HEAD` 判 env-unavailable、rc3。
  - 不帶 `--diff` 時 rc2、印用法。
  - `LUMOS_SKIP_LINT_NEW=1` 判 off、rc0。
- 一條命令沒裝工具、另一條正常:判 env-unavailable、rc3,印「沒裝 nosuchtool-xyz」。推送前閘同一情境自動放行。
- 壞設定:
  - `lint_new` 設成字串、`budget_sec` 設成 "abc" 或 null、config 整份是 `[]`,都沒有 traceback。
  - `.lumos/lint.json` 寫壞時判 no-config、rc0。這跟推送前閘同判,訊息說「檔不在」但實際是壞掉,屬既有行為。
- `code-loop pass` 被擋:rc2,印擋下原因、放行指令和「代碼審還不能記通過」。沒有 marker,也沒有 passed 帳,只多一筆 `code-loop-pass/blocked/hard`,帶 `blocks:["lint_new"]`。
- detached HEAD 下 pass 同樣被擋;那筆帳的 ref 是 "HEAD"。
- pass 放行:工具沒裝時 rc0,寫留痕,並記一筆 `lint-new` 自動放行帳。
- `gov` 和 `gov --stats` 認得新閘名 `code-loop-pass`,顯示「硬擋 1 次」,沒有報錯。
- 相關測試全綠:`-k lint_new_cli`、`-k codeloop_pass_requires`、`-k loop_close`,共 27+9 筆。我另跑了 `-k known_gate` 和 `-k gov_stats`,只確認執行完畢,沒看到結果。

### 逐項檢查
- **推送前閘不帶新選項的路徑**:逐行比對。`mech_only` 預設 False。`kg` 建構改成 `keep_going or mech_only`,等於原值。`_sec_stop`、`_e2e_stop`、`bt` 都是 `if mech_only else 原式`。結尾判斷多了 `or mech_only`。這些都不改變原行為。
- **新舊互讀**:`_KNOWN_GATES` 已登記。`LOOP_NOT_CLOSE_EVENTS` 只列 `("code-loop","blocked")`,新閘名不同,不會被當成關門事件。`_SLOT_METRIC_KINDS` 與新閘無關。
- **寫一半**:擋下時先印訊息和寫帳,然後 `return False`,後續 `_codeloop_write` 不會執行,沒有寫一半的留痕。帳寫不進去時 `_gate_event_or_warn` 只警告,不改判定。
- **冪等**:重跑 pass 只重判。每次被擋就多追加一筆硬擋帳,符合設計。
- **不可逆**:沒有刪改既有留痕或帳。
- **新增程式的改壞測試**:
  - 拿掉 `or mech_only`:⑨b 紅。
  - 不跳過 e2e、安全證據或合約測試:⑨ 紅。
  - 擋下少了 `hard` 或 `blocks`:① 紅。
  - 機械檢查移到驗證之後:②③ 紅。
  - 退出碼表任一格改掉:④⑤⑥ 紅。
- **覆蓋缺口**:pass 在「算不出分岔點」(沒有主線)時放行並記帳,這條只在文件宣稱,沒有 pass 層級的測試。但那是 `_codeloop_guard_verdict` 既有路徑,推送前閘會走到,所以只算覆蓋可更完整,不標條。

### 圖譜鏡頭
- `Systems/pitfalls-code-loop.md`:★INVARIANT★ 沒有。有效 RULE 共四條:兩條資安席範圍、一條資源席、一條 `pass 放行不代表這個迴圈審的是這條分支`。這次改動不影響其中任何一條。
  - 新增的 WHY 與正文描述和程式一致。
  - 一個行為變化要留意:pass 之後又提交程式再 pass,會被舊表態擋下。文件已明講,舊測試也據此補了 `_answer_stack_questions`。
- `Systems/棧別提問表態閘.md`:沒有 INVARIANT 或有效 RULE 被破壞。推送前判法不變,只多了「pass 前也跑」,與程式一致。
- `skills/lumos-code-loop/SKILL.md`:新增步驟和程式行為一致(`rc0` 才派、`rc3` 不算乾淨、pass 先跑兩道)。照做不會做錯。

總結:最嚴重是 minor(F1,`lint-new` 的「看全部」提示會叫人跑寫帳的指令),會擋 0 條。
