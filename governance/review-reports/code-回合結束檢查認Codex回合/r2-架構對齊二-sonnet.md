severity: minor

**1. 分層與依賴方向**
- `_kept_start` 放在 `scripts/hooks/claude/stop-lint-hook.py:230`。它夾在 `_turn_start`(`:210`)、`_turn_key`(`:219`)和 `_on_prompt`(`:243`)中間,跟這幾個回合起點小函式同一層,沒有往共用模組或別的層伸手。
- 它判時刻是呼叫既有的 `_turn_start(rec)`,沒有自己重寫,判法正確。
- 讀紀錄的 `json.loads(path.read_text(...))` 加 `except (OSError, ValueError, RecursionError)`,跟收工那段(`:423-424`)是同一套例外清單,但是在 `_kept_start` 裡另外寫了一份。`_hookshared.py` 目前沒有「讀快取 JSON」的共用函式(我搜 `json.loads` 和 `def .*json` 都沒有),所以不算跨層直呼,細節見第 3 問。
- 引句:「        rec = json.loads(path.read_text(encoding="utf-8"))」
- 對照:`scripts/hooks/claude/stop-lint-hook.py:423`

**2. 命名與寫法**
- 命名:`_kept_start` 帶底線前綴,沒有動詞,跟鄰居 `_turn_start`、`_turn_key` 的「名詞片語」一致。
- docstring:跟鄰居一樣引了出處(官方 `codex-rs/core/src/session/turn.rs`,加代碼審 r1 審查席 F1),格式跟 `_turn_key` 的 docstring 一致。
- 筆記 PITFALL 欄位:`[出處:][根因:][修法:][test:]` 四欄齊全,順序跟鄰居一致。鄰居是 `:24` 的 pthread_sigmask 那條,同樣是 `[出處][根因][修法][test]`。
- 測試步驟編號:⑤⑥ 接在 ①-④ 後面,測試也用同一套 `_slh_run`、`_slh_block`、`_slh_calls` 輔助函式,風格一致。
- 引句:「        import time as _t」
- 對照:測試檔的 `import time as _t`(`scripts/test_lumos.py:6165`)這種函式內匯入是既有寫法,所以不列。

1. 測試函式 docstring 的「翻紅釘」沒補新增的 ⑤⑥(`scripts/test_lumos.py:133372`)
severity: minor
   blocking: 否
   - 引句:「        # ⑤ 代碼審 r1 審查席 F1:Codex 回合中途插話以同一個 turn_id 再送一次送出提示(官方 core/src/session/turn.rs 的 steer 走同一個」
   - 既有:docstring 只列「①②紅、④紅、③紅」,各步都寫了翻紅條件;新增的 ⑤⑥ 沒補對應的翻紅條件(例如「`_kept_start` 拿掉 → ⑤ 紅」)。
   - 其他測試的 docstring 都把全部步驟的翻紅條件寫進去,所以這裡跟鄰居不一致,但結構是對的。

**3. 第二種做法**
1. `_kept_start` 另寫了一份「讀起點紀錄檔並接住壞檔」的邏輯,跟收工那段(`:421-425`)重複
severity: minor
   blocking: 否
   - 引句:「    except (OSError, ValueError, RecursionError):」
   - 既有:`scripts/hooks/claude/stop-lint-hook.py:423-424`
   - 兩處的例外清單完全相同。這個鉤子的筆記 WHY(`回合結束寫法檢查.md:30` 附近,「各支複本」)明說「讀壞輸入只是功能退化」所以不抽共用,且 `_hookshared.py` 沒有現成函式,所以我判成 minor 不是 major。⚠ 交編排者:要不要讓 `_on_stop` 也改呼叫 `_kept_start` 風格的讀取函式?那會牽動收工那段已有測試守的行為,我不建議強求。
- 判時刻的邏輯沒有另抄,`_kept_start` 直接呼叫 `_turn_start`,所以沒有 major。

不對齊共 2 條,其中 major 0 條
