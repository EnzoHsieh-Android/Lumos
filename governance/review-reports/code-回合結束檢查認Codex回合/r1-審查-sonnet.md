severity: major

總結:最高等級 major,共 2 條 finding,其中 blocking 1 條(F1),F2 不擋。

## 逐項查證結果(沒出 finding 的項目)

- **兩事件的 turn_id 同源,續做不換編號。**
  - `user_prompt_submit` 與 `stop` 的請求都取 `turn_context.sub_id`。
  - 引句:「Codex 的送出提示與收工事件沒有 prompt_id、帶 turn_id」
  - 佐證:file: `…/scratchpad/codexsrc/hook_runtime.rs.txt:708-722`(`inspect_pending_input`)與 `:431-433`(`run_turn_stop_hooks` 組 `StopRequest`)。
  - 我另外抓了主線 `codex-rs/core/src/session/turn.rs`,存在 `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-shearwater/5b6d202a-9139-47f7-b6b9-deb227707ba4/scratchpad/rv/turn.rs.txt`。
  - Stop 擋下後的續做是同一個迴圈的 `continue`(`turn.rs.txt:841`),同一個 `turn_context`,所以 `sub_id` 不變。
  - 擋下理由用 `record_response_item_and_emit_turn_item` 記成回應項目,不是 `TurnInput::UserInput`,所以續做不會重送 UserPromptSubmit。
  - 結論:「同一回合同批只擋一次、最多三批」這條在 Codex 下成立。
- **Claude Code 既有行為沒有實質回歸。**
  - 引句:「if isinstance(v, str) and v:」
  - Claude Code 的 `prompt_id` 是 UUID 字串。
  - 非字串的 `prompt_id`(數字、null、空字串)只有在 payload 自己帶 `turn_id` 時才改走 `turn_id`。
  - 在 Claude Code 上,payload 沒有 `turn_id`,這幾種情形原本也是「對不上就不檢查」,只有數字那一種原本會對上。現實裡不會送出,不構成 finding。
- **舊紀錄檔相容。**
  - 引句:「"prompt_id": _turn_key(payload), "t": time.time()}), encoding="utf-8")   # 鍵名照舊,值是回合編號」
  - 鍵名沒改,舊檔讀起來照舊。
- **其他用到回合編號的地方都已改成 `_turn_key`。**
  - 引句:「pid = _turn_key(payload)」
  - 佐證:file: `scripts/hooks/claude/stop-lint-hook.py:410`;`_claim` 用 `pid`、`--record-stop-block --prompt` 用 `str(pid)`。
  - 另一處 `scripts/lumos:41651` 是 `str(prompt)[:80]` 記帳,`:77969` 只是 help 文字,都不用改。
- **標記檔名。**
  - `_claim` 取 `_mark_name(pid)[:16]`。
  - turn_id 是 UUIDv7 時,前 16 字含毫秒時間,不同回合不撞。沒有具體失敗輸入,不標。
- **新測試。**
  - 我跑了 `python3.14 scripts/test_lumos.py -k stop_lint_hook_codex`,4 項全綠。
  - 引句:「翻紅釘:_turn_key 只認 prompt_id → ①②紅;改成 turn_id 優先 → ④紅;對不上照擋 → ③紅。」
  - 這三條翻紅路徑我逐項走過,成立。
- **角色卡。**
  - be-api-compat:起點紀錄檔的鍵名與值型別(字串)都沒變,對外沒有契約改動。
  - be-authz:這支鉤子沒有端點,也沒有讀寫別人的資料,不適用。
- **圖譜固定席。**
  - `測試假綠形態`、`授權與歸屬`、`lumos-cli-read`、`bound-tests-gate`、`canary-audit`、`guard-kill` 這幾篇都只因 `scripts/test_lumos.py` 掛上。
  - 這份 diff 只新增一個測試,沒有碰它們宣稱的行為或合約。
  - `測試假綠形態` 要求「還原翻紅釘配前置斷言證明現場成立」:①先驗起點檔寫了值,②驗 `--record-stop-block` 有被呼叫,前置斷言足夠。

## Findings

### F1 Codex 回合中途插話會重寫起點時刻,回合前半段改的檔不再被檢查

severity: major
blocking: 是

- **位置:** file: `scripts/hooks/claude/stop-lint-hook.py:240`(`_on_prompt`)。
- **引句:**
  引句:「tmp.write_text(json.dumps({"prompt_id": _turn_key(payload), "t": time.time()}), encoding="utf-8")」
- **失敗場景:**
  1. Codex 回合 `turn_id=T` 開始,UserPromptSubmit 記起點 `{T, t0}`。
  2. AI 寫了一個壞的 `.kt` 檔,修改時間在 t1。
  3. 使用者在回合還在跑時插話(steer)。
  4. 插話會以同一個 `turn_id=T` 再觸發一次 UserPromptSubmit,`_on_prompt` 無條件 `os.replace` 覆寫成 `{T, t2}`(t2 > t1)。
  5. 回合結束時 Stop 帶 `turn_id=T`,對得上,但 `since=t2`,t1 的壞檔早於起點,不算「這回合碰過」,該擋沒擋。
- **為什麼是這次改動帶來的:**
  - 改動前 Codex 一律不檢查,沒有這個問題。
  - 改成 `turn_id` 之後,「同一回合編號重複收到送出提示」變成可達路徑。
  - Claude Code 的 `prompt_id` 是每次送出提示各一個,沒有這個現象。
- **佐證(官方原始碼):**
  - file: `…/scratchpad/rv/turn.rs.txt:1044-1049`:`run_hooks_and_record_inputs` 對每個待處理輸入呼叫 `inspect_pending_input`。
  - 同檔 `:1066` 起的 `PersistContext::SteeredUserInput` 表示插話走同一條路,用同一個 `turn_context`。
  - file: `…/scratchpad/codexsrc/hook_runtime.rs.txt:708-722`:`TurnInput::UserInput` 會發 UserPromptSubmit 且 `turn_id = turn_context.sub_id`。
- **最小重現(逐字給鉤子,可直接跑):**
  1. `UserPromptSubmit{session_id:"s", turn_id:"T"}`
  2. 寫壞檔
  3. 再送一次 `UserPromptSubmit{session_id:"s", turn_id:"T"}`
  4. `Stop{session_id:"s", turn_id:"T"}`
  5. 結果:不擋。我是依 `_on_prompt` 與 `_turn_start` 的程式讀出來的,沒有實際跑這一串,但路徑單純,`os.replace` 覆寫沒有條件。
- **修法方向:** `_on_prompt` 讀既有紀錄;若其回合編號與這次相同,保留較早的 `t`,不覆寫。
- **測試缺口:** `t_stop_lint_hook_codex_turn_id` 沒有「同一個 `turn_id` 送兩次送出提示」的案例,這條改壞照綠。

### F2 Codex 路徑少了「同回合同批只擋一次、換回合重算」的測試

severity: minor
blocking: 否

- **位置:** file: `scripts/test_lumos.py`,新測試 `t_stop_lint_hook_codex_turn_id`。
- **引句:**
  引句:「check("②同一個 turn_id 收工、有新增告警 → 擋下並以 turn_id 記帳」」
- **失敗場景:**
  - 如果 `_on_stop` 裡 `_claim(sid, pid, batch, sh)` 的 `pid` 被改回 `payload.get("prompt_id")`,Codex 下會變成 `_mark_name(None)`,也就是固定前綴 `sid.lint-None-`。
  - 後果是整個會談只擋最多三批,之後每個回合都不擋。
  - 新測試的 ①②③④ 都只看第一次擋下,這個壞法全綠;既有的 `t_stop_lint_*` 只用 `prompt_id` 驅動,也抓不到。
- **嚴重度為什麼只標 minor:**
  - 現行程式 `_claim` 與 `--prompt` 共用同一個 `pid` 變數。
  - 這條防無限擋的判準由 `prompt_id` 路徑的既有測試保護。
  - 缺的只是 Codex 路徑的覆蓋,不是現行會出錯的行為。
- **建議:** 補兩步,用同一個 `turn_id` 再收工一次(批次相同要不擋)、換 `turn_id` 收工要再擋。

severity 總結:最高 major,blocking 1 條(F1)。
