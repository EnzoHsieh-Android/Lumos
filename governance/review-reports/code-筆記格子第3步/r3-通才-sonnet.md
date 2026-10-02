severity: minor

**R3U1**
severity: minor
blocking: 否 — 只在 stderr 本身壞掉時發作,而且是讓指令崩掉,不會放行該擋的推送
1. 把 `_drift_retire_quiet` 拿掉之後,`_drift_retire_report` 的 except 分支和 `_drift_retire_guarded` 的兜底分支都改成直接 `print(..., file=sys.stderr)`。stderr 撞上 BrokenPipe 或已關閉時,這句 print 會再丟一次例外。呼叫端 `cmd_drift_check` 沒有包它,例外會一路冒出去。
2. 後果有兩個:這一筆撤除條件帳不會寫(印出失敗後的記帳那步被整段跳過),指令也以 traceback 結束。
3. 重現:把 `sys.stderr` 換成 `write` 會丟 `BrokenPipeError` 的物件,再呼叫 `m._drift_retire_report("/tmp","block","a"*40,"b"*40,[{"path":"x.md","line":1,"text":"t"}],[],[])`。結果是 `escaped BrokenPipeError`。上一輪(r2)有 `_drift_retire_quiet` 擋著,這是 r3 改回去才出現的退步。
4. 鄰居 m1 與 c1 到 c5 同樣沒擋,所以是「跟鄰居一致地脆弱」。不過 r1 的併發資源席原本指出的就是這個洞,退回去等於把它重新打開。
5. 建議:兩處只在 except 內多包一層 try/except,不必回到另寫小工具。

引句:「print(f"存量漂移檢查:RULE 撤除條件的清單印到一半出錯({type(ex).__name__}),判定照舊", file=sys.stderr)」

**R3U2**
severity: minor
blocking: 否 — 只影響一行提醒的排版,不影響判定或任何指令的結束碼
1. S18 的 fail-open 現在直接印例外訊息 `{_e18}`,沒有經過 `_esc_clean`。例外訊息可能含路徑、換行或控制字元。改前只印 `type(...).__name__`,改後的寫法跟「印出前清控制字元」那條不一致。
2. 例外多半是自己程式內部的訊息,可達性低。想一致的話包一層 `_esc_clean(str(_e18), _DOCTOR_LINE_MAX)`。

引句:「ok(f"度量式撤除條件觀測跳過(fail-open:{_e18})")」

**逐項核對(通才鏡頭,未發現 blocking 或 major)**
1. 實測方式:把 384f4574 與 1685194c 各 clone 到臨時目錄,各跑一次 `doctor`、`doctor --ci`、`doctor --verbose`、`drift scan`。在 repo 自己的圖譜上,輸出除了第一行的 vault 路徑,完全相同,結束碼也一致。
2. 在自造的小消費 vault 上,新舊的差異都在預期內:
   - 單行 summary 的 `RULE`(S16)和單行引號的 `FACT`(S19)改後會被判到。
   - 續行、tab 續行、CRLF 在新舊版的判讀一致。
   - 設定檔是 symlink 時 doctor 不崩。差別只在 S16 截斷顯示的筆數,是新多了 A.md 這條造成的。
3. `lumos note-shape --staged` 在改後行為不變:新舊輸出逐字相同、結束碼都是 1。這是預期的,因為 `_ns_summary_logical` 改成收片段再 `" ".join`,語意和原本的 `+= " " + s` 等價。
4. 修正有成立:
   - S16 到 S19 共用 `_note_summary_entries`。
   - S16 清了控制字元。
   - S18 的 try 範圍涵蓋 `warn_soft`。
   - `_lint_new_config(from_snapshot)` 在 symlink 設定檔下回預設,不讀捷徑。
   - `_drift_jsonl_iter` 讓帳增速段與度量段不再留整份清單。
   - 子集測試 `slots_doctor_reminders`(36 筆)、`slots_retire`(34 筆)、`doctor_lists_stale`(8 筆)全過。

**圖譜鏡頭(派工附的節點筆記)**
1. `Systems/lumos-cli-read`:這份 diff 的程式行為和摘要新寫的 S16 到 S19 描述吻合,對上的行為有 `_note_summary_entries`、`_doctor_cfg_bytes` 和 lint-new 吃快照。沒有破壞該節點宣稱的行為或合約。
2. `Systems/存量漂移守衛`:筆記說「先印後記」,程式也是先印後記,兩邊一致。R3U1 是程式比筆記多出的一個脆弱點,不是筆記說錯。
3. `Issues/撤除條件檢查末輪遺留四項` 與 `Projects/筆記格子寫法與過期檢查_計劃`:只是文字和 S13 的測試綁定更新,不影響合約。

最高嚴重度 minor,blocking 0 條
