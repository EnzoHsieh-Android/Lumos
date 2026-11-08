severity: minor

**問 1 分層與依賴方向:對齊,只有定義順序一條小出入**

`_read_turn_rec` 放在 `_kept_start` 正下方,和其他起點紀錄小函式同在 `stop-lint-hook.py` 的上半部。它沒有往共用模組放,也沒有跨層直呼。兩個呼叫端都在同一支鉤子裡:送出提示那條路徑經 `_kept_start` 呼叫它,收工的 `_on_stop` 直接呼叫它。這和既有做法一致:`_turn_start`、`_turn_key`、`_kept_start` 都是本檔的私有小函式,由 `_on_prompt` 和 `_on_stop` 取用,`sh` 只拿來取快取目錄和驗目錄。路徑解析(`sh._stop_dir_ok(turn_dir)`)留在 `_on_stop`,讀檔動作才抽出,責任切法和 `_claim` 一樣。

引句:「rec = _read_turn_rec(turn_dir / sid) if sh._stop_dir_ok(turn_dir) else None」
file: `scripts/hooks/claude/stop-lint-hook.py:230`(`_kept_start`)、`scripts/hooks/claude/stop-lint-hook.py:240`(`_read_turn_rec`)、`scripts/hooks/claude/stop-lint-hook.py:414`(`_on_stop`)

1. 定義順序:`_read_turn_rec` 排在呼叫它的 `_kept_start` 後面。
   - 鄰居的慣例是被呼叫者先定義:`_turn_start` 先於 `_kept_start`,`_killpg` 先於 `_alive_group` 和 `_kill_all`,`_claim` 先於 `_on_stop`。
   - Python 執行不會出錯,結構也對,只是和檔內慣例不一致。
引句:「def _read_turn_rec(path):」
file: `scripts/hooks/claude/stop-lint-hook.py:210`(`_turn_start` 排在 `_kept_start` 之前,可對照)

severity: minor
blocking: 否

**問 2 命名與寫法:對齊**

函式名 `_read_turn_rec` 用底線開頭加動詞、受詞,和 `_turn_start`、`_turn_key`、`_kept_start` 同一套。docstring 先寫回傳值,再用括號標「代碼審 rN 席」出處,和 `_mark_event`、`_killpg` 的寫法相同。行內註解 `# 深層巢狀的 JSON(代碼審 r2 邊界席 F1)` 也是從原處原樣搬過來,位置和 `main()` 的 `# 壞 JSON、深層巢狀…` 同款。

測試 ⑦ 沿用 ⑥ 的註解格式(`# ⑦ 代碼審 r2 審查二席:…`),`check(f"⑦…")` 的標籤格式、`_slh_run`、`_j.loads` 也都是同檔的用法。新增的「翻紅釘」補在原 docstring 的同一行格式後面。筆記是在既有 PITFALL 的 `[修法:]` 後面接一句,沒有另開行,`[test:]` 仍是同一個鍵,符合同檔 PITFALL 寫法(`回合結束寫法檢查.md` 第 20、24、28 行)。

引句:「⑦ 代碼審 r2 審查二席:起點紀錄壞掉(時刻不合法、深層巢狀 JSON)時」
引句:「讀起點紀錄送出提示與收工共用 _read_turn_rec(r2 架構對齊席:原本兩處各寫一份)」
file: `scripts/test_lumos.py:133380`(⑥ 的註解格式)
file: `docs/lumos-toolchain-knowledge/Systems/回合結束寫法檢查.md:32`

⚠ 交編排者,不列為不對齊:筆記新加的那句「Python 3.14 解析深層巢狀 JSON 不再丟 RecursionError,那個攔截只對舊版直譯器有作用」,和同檔第 13 行 WHY 的「深層巢狀(RecursionError)」並列。兩者不矛盾,但讀的人要自己看出一個說的是舊版直譯器。這屬於筆記內容準確度,不是做法不一致。

**問 3 第二種做法:沒有另抄的讀紀錄邏輯**

修補後 `stop-turn` 紀錄只有 `_read_turn_rec` 一處讀檔:`_kept_start` 和 `_on_stop` 兩個呼叫端都改走它,`json.loads(...read_text...)` 加那組例外的複本已經刪掉。時刻判斷統一走 `_turn_start`。我在 `scripts` 底下 grep `stop-turn`,只有 `stop-lint-hook.py` 和 `test_lumos.py` 出現,沒有第三處讀。

`_on_stop` 內「是 dict、`prompt_id` 相符、再取 `_turn_start`」的判斷,和 `_kept_start` 結尾那行長得類似。兩處的差別是 `_on_stop` 要把「缺紀錄、編號不符、時刻壞」分開印不同訊息,而且兩邊都呼叫同一個 `_turn_start`,所以不算第二種判時刻的做法。`main()` 讀 stdin 的 `json.loads` 對象是 payload,不是起點紀錄,不算重複。

引句:「rec = _read_turn_rec(path)」
引句:「since = _turn_start(rec) if isinstance(rec, dict) else None」
file: `scripts/hooks/claude/stop-lint-hook.py:534`(`main()` 讀 stdin,對象不同)

不對齊共 1 條,其中 major 0 條
