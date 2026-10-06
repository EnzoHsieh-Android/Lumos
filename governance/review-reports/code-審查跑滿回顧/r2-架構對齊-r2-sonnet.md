severity: major

# 架構對齊-r2-sonnet 報告(第 2 輪)

## 三問

**1 分層與依賴方向**:這輪新增的 `_canary_ledger_scan`、`_loop_records_checked` 疊在既有 `_loop_records` 之上,方向正確:舊的 `_loop_records` 改成薄包裝,刪掉 `_retro_canary_load`/`_retro_canary_rows` 兩支,審查帳的讀法收成一套(scripts/lumos 新檔 `_canary_ledger_scan` 之後)。`_disposal_fail_banner` 是處置閘內部共用,沒有跨層直呼。治理帳寫入器 `_gate_event` 與 `_append_governance_log` 都在寫前呼叫 `_ledger_tail_needs_newline`,依賴方向沒問題,但這支新函式跟既有的檔尾補換行是兩份(見 F1)。`_cap_retro_*` 沒有直呼 `cmd_*`,分層沒有反向。

**2 命名與錯誤處理**:新函式 `_retro_read_bytes` 回 `(位元組, 錯誤或 None)`,與 `_regular_own_fd` 的「失敗回 None」不同形;`_loop_records_checked` 回 `(列, 原因或 None)` 與舊 `_retro_canary_rows` 同形,一致。`_esc_clean(_retro_safe(x))` 的兩段式清理只在部分呼叫點使用(見 F3)。處置閘 FAIL 橫幅 `_disposal_fail_banner` 命名與參數(rid=None 表示帳壞)清楚,正常與帳壞兩路都改用它,沒有留舊的 print。

**3 第二種做法**:查到三處又自寫了一套:(a) 補檔尾換行(F1);(b) 讀回顧檔開檔(F2,docstring 明講「不沿用 _regular_own_fd」,但該函式早有「另抄一份」被架構席打回的前科);(c) 終端消毒多了 `_retro_safe` 與 `_esc_clean` 並存(F3)。`--template --write` 的 O_EXCL 建檔寫法與專案內另外兩處(`.gitignore` 建檔、逃逸帳建檔)是同一種手寫模式,沒有共用函式但也沒有第三種,不單獨立案。讀審查帳已收成一套;讀治理帳沒有新增函式,只改了 docstring,但它與既有的兩本合讀函式並存(F5)。

---

### F1 補檔尾換行又寫了一份,既有的 `_drift_ledger_append` 內嵌版沒共用
severity: major
blocking: 是 — 同一件事(帳檔尾不是換行就先補)出現第二套實作,既有那套日後改守衛時會漂
- 輸入→走到哪:任何治理帳寫入(`_gate_event`、`_append_governance_log`)走到新加的 `_ledger_tail_needs_newline`;另一條路 `drift fix` 的表態檔與修復帳走 `_drift_ledger_append`,自己用 `fh.seek(-1, 2)` 讀最後位元組、不是換行就另開一次 `open(fp, "a")` 寫一個 "\n"。
- 壞在哪:兩份判準不同——新版會擋非一般檔(`S_ISREG`)、回傳旗標讓呼叫端把換行併進同一次寫入(單次寫入);舊版不擋非一般檔、換行單獨先寫一次(兩次寫入)。同一個動作兩種語意,專案慣例是抽共用函式(見 `_gov_routes_local` 的「兩支寫入器共用這一支判定,不各抄一份」)。
引句:「    """帳檔非空而且最後一個位元組不是換行(上一次寫一半)→ True。追加前先補一個換行」
- file: `scripts/lumos:1508`(新) 對 `scripts/lumos:35311`(既有 `fh.seek(-1, 2)` 那段,在 `_drift_ledger_append` 裡)
- 重現:`grep -n 'seek(-1' /Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos` 輸出兩行:1517(`f.seek(-1, os.SEEK_END)`)與 35311(`fh.seek(-1, 2)`)。

### F2 讀回顧檔不用 `_regular_own_fd`,自寫 O_NOFOLLOW|O_NONBLOCK|fstat 開檔(第二種做法)
severity: major
blocking: 是 — 開檔防護(不跟捷徑、不卡管線、確認一般檔)出現第二套,而 `_regular_own_fd` 的 docstring 本身就記著「原本另抄一份還少了擁有者檢查」被架構對齊席打回
- 輸入→走到哪:`cmd_loop_retro --check/--record`、`_cap_retro_status`、`_cap_retro_check` 都走新函式 `_retro_read_bytes`。它用 `os.open(... O_NOFOLLOW | O_NONBLOCK)` 加 `os.fstat` + `S_ISREG`,與 `_regular_own_fd` 逐步相同,只少最後一步擁有者(`st_uid`)檢查。
- 壞在哪:差別只有「不檢查擁有者」,這個差別可以用一個參數(例如 `_regular_own_fd(path, flags, mode, own=True)`)表達,不必另抄整段;現在日後若 `_regular_own_fd` 補了新防護(例如 flags 或 fstat 條件),回顧檔讀取不會跟著。docstring 的理由(CI 別的帳號 checkout)成立,但解法層次不對:該擴參數而不是複製。
引句:「    ★不要求「是自己的檔」★(不沿用 _regular_own_fd):共用機器或 CI 用別的帳號 checkout 時,合格回顧會被判成過期」
- file: `scripts/lumos:1339`(`_regular_own_fd` 及其 docstring「代碼審 code-gov-ledger-split-2 r2 架構對齊席:原本另抄一份還少了擁有者檢查」)
- 重現:`sed -n 1339,1356p /Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos` 與 `sed -n "$(grep -n 'def _retro_read_bytes' /Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos | cut -d: -f1),+20p" /Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos` 並排,可見相同的 flags 與 `S_ISREG` 判斷。

### F3 `_retro_safe` 與既有 `_esc_clean` 並存成兩段式清理,呼叫點不一致
severity: major
blocking: 是 — 終端消毒有了第二套規則,且套用不一致,漏套的點會讓孤立代理字元印到終端時炸出堆疊
- 輸入→走到哪:專案既有的終端與帳顯示消毒是 `_esc_clean`(控制字元、C1 換空格、截斷)。這輪新增 `_retro_safe`(孤立代理字元換 U+FFFD),使用方式是 `_esc_clean(_retro_safe(x), n)` 兩段套。全檔 `_retro_safe` 共 17 處、兩段式只 8 處;其餘如 `cmd_loop_cap_decision` 的 `_esc_clean(loop_id, 60)`、`cmd_loop_retro` 的 `_esc_clean(rel, 200)`、`print(f"✗ 回顧不合格({rel}):")` 都只用 `_esc_clean` 或完全不套。
- 壞在哪:`_esc_clean` 的判斷 `ch >= " " and not ("\x7f" <= ch <= "\x9f")` 讓 U+D800–U+DFFF 原樣通過。專案已有 Cs 類別的共用判斷(`_path_special_chars` 與 `_PATH_SPECIAL_CATS` 的 Cs,見 scripts/lumos:32232 一帶註解「不另抄一組」)。正確層次是把代理字元處理併進 `_esc_clean`(或讓它成為 `_esc_clean` 的一個步驟),而不是另開一支、要呼叫端記得兩支都套。⚠ 孤立代理字元能否經 `loop_id` 進入 `cmd_loop_cap_decision` 取決於 argv 解碼(`_retro_id_bad` 沒擋 Cs);我沒實跑,所以「漏套會炸」這一半標 ⚠,「第二套並存、套用不一致」這一半可由 grep 重現。
引句:「    """孤立代理字元換成 U+FFFD:印到終端或 json.dumps(ensure_ascii=False) 時才不會整支炸掉(代碼審 r1 邊界席)。」
- file: `scripts/lumos:10927`(`_esc_clean`)、`scripts/lumos:32232`(Cs 共用註解)
- 重現:`grep -c '_retro_safe' scripts/lumos` 得 17;`grep -c '_esc_clean(_retro_safe' scripts/lumos` 得 8。

### F4 `--template --write` 與同層 `fix-check --record-template` 的提示分流不一致
severity: minor
blocking: 否 — 命名與提示的不一致,不影響行為
- 輸入→走到哪:這輪把回顧骨架的提示從 `--template > 檔`(照貼會截斷已寫好的回顧)改成 `--template --write`,並在 help 說「別用 > 重導向,會先清空已寫好的回顧」。同層的 `fix-check --record-template` 仍在 `_fix_status`(約 scripts/lumos:12672)印 `... --record-template > <檔>`,正是這輪判定為有害的同一種重導向寫法。
- 壞在哪:兩個「產骨架」指令對同一種風險用了兩套處理(一個有 `--write` + O_EXCL,一個印重導向指令),使用者從 `loop next` 看到兩種寫法。
引句:「help="跟 --template 一起用:回顧檔不存在時直接建出來;已存在回 2、不動檔(別用 > 重導向,會先清空已寫好的回顧)」
- file: `scripts/lumos:12672`、`scripts/lumos:12518`
- 重現:`grep -n 'record-template >' /Users/enzo/harness/lumos-toolchain-cap-retro/scripts/lumos` 仍有輸出。

### F5 ⚠ `_retro_gov_events` 是第三套治理帳讀法,缺既有「只讀一般檔」守衛
severity: minor
blocking: 否 — 判不準影響面,標 ⚠
- 輸入→走到哪:`_retro_gov_events` 用 `(Path(root) / "docs" / GOV_LOG_NAME).read_bytes()` 讀版控帳;專案既有 `_gov_ledger_rows_by_time` 先 `p.is_file()` 才讀(docstring「特殊裝置檔、管線不讀,免得讀不到底」),逐行解析另有 `_drift_jsonl_iter`。diff 在這支函式只加了 docstring(說明「只讀版控帳是對的」),沒補一般檔守衛。
- 壞在哪:docs/.governance-log.jsonl 若是管線,`read_bytes()` 會卡住;既有讀者擋掉。函式主體不是這輪新寫,但這輪加註「是對的」並把它當回顧判定的唯一讀法。⚠ 未實跑管線情境。
引句:「    ★只讀版控帳(docs/.governance-log.jsonl)是對的★:_gate_event 只把 _GOV_LOCAL_PAIRS 白名單裡、hard=False 的「閘名+種類」分流到本機帳,」
- file: `scripts/lumos:1400`(`_gov_ledger_rows_by_time` 內 `if not p.is_file()`)

---

不對齊共 5 條,其中 major 3 條
總結:最嚴重 major,blocking 3 條
