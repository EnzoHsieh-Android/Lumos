severity: major

資安-r4-sonnet 第 4 輪報告。鏡頭:攻擊者視角(終端跳脫、符號連結、寫出 repo 外、帳偽造)。
實跑環境:臨時 repo(照 test_lumos.py 的 `_cr_repo`/`_cr_loop` 造帳),沒碰真帳。
r3 新規則本身(`_retro_gov_path_err`、`_drift_ledger_path_err` 加一般檔檢查、`_ledger_lines` 行為、`_json_text_escaped`、`_cap_retro_fix_cmd` 狀態表、`_fix_bad_strings(nul=False)`、cap-decision 指令的 shlex.quote + `_esc_clean`)逐項試過,沒找到可利用的洞:
- `_json_text_escaped` 對 C0/C1/DEL/雙向/零寬/tag 字元/U+2028/U+0085 全部換成 \uXXXX 且 json.loads 讀回值不變(19 種字元實測)。
- 20 處讀者改 `_ledger_lines` 後,尾端多出的空字串都被各自的 strip 或 json 例外吃掉,沒有行為差異。
- 治理帳是符號連結、管線、資料夾、docs 是捷徑,retro 一族都 fail-closed;帳上的 loop 字串含 `..` 時讀回顧檔被 `_retro_path_unsafe` 擋成 dossier。
- 提示指令的編號 shlex.quote 後再截斷 400 字,截斷只會丟尾、不會把引號內的字元變成引號外,試不出注入。
以下是找到的三條。

### F1 跑滿上限提示與處置閘橫幅把帳上輪次編號原樣印到終端(終端跳脫注入)
severity: major
blocking: 是 — 帳上任一輪的 round 字串帶 ESC/C1 控制序列,loop next 與處置閘就把它原樣送進終端;`canary record --round` 與提交進版控的審查帳都能植入
- 輸入:`lumos canary record none --loop crx --round $'r3\x1b]0;PWNED\x07' ...`(`cmd_canary` 只擋 `__` 開頭,不擋控制字元),或審查帳(docs/.canary-log.jsonl,版控)裡某列 `"round": "r2\u001b]0;PWNED\u0007\u009b31m"`。
- 走到哪:迴圈到上限(三輪)後跑 `loop next` 或 `loop status --disposal`。`_cap_hint_lines` 對每一輪印 `{x['round']}`(未過 `_esc_clean`);`_disposal_fail_banner` 的 `{rid}` 同樣原樣印;`loop status` 列表行也印原值。
- 壞在哪:終端收到 OSC 設標題、8 位元 CSI,輸出被改寫。r3 在同一支函式新加的記人裁指令那行有過 `_esc_clean`,但同函式的輪次行沒有——同函式兩種待遇;而且這支輸出是給編排者(含 LLM)讀的,被偽造的行會被當成工具說的話。
- 引句:「已經跑了 {len(h['rounds'])} 輪,到了分級 {h['tier']} 的上限 {h['cap']} 輪」
- 佐證行:file: `scripts/lumos:8969`(`lines.append(P + f"  {x['round']}:{f},最高 ...")` 原樣印輪次)
- 佐證行:file: `scripts/lumos:13618`(`_disposal_fail_banner` 的 rid 原樣印)
- 重現(實跑,輸出含原始 ESC 與 U+009B):
  ```
  LUMOS_PANEL_RETIRE_CUTOFF=2026-08-26 python3 /private/tmp/claude-501/r4/exp3.py
  record rc 0
  ['  r3\x1b]0;PWNED\x07.1\tnone\tclean\ts9-sonnet', '⛔ DISPOSAL GATE FAIL (crx 輪 r3\x1b]0;PWNED\x07: G3)', '    r3\x1b]0;PWNED\x07:折 0 條,最高 clean', ...]
  ```
  另 /private/tmp/claude-501/r4/exp2.py 用改帳方式重現 `loop next` 與處置閘的 `[cap-hint]` 段(`'    r2\x1b]0;PWNED\x07\x9b31m:折 1 條,最高 minor'`)。
- 備註:這行不是 r3 新增,但在 r3 改動的函式裡,第 4 輪的「終端跳脫」鏡頭正好踩到;一條統一規則(印出前整行過 `_esc_clean`,或寫入端 `canary record --round` 拒控制字元)即可。

### F2 全帳讀者只擋「不存在」、不擋非一般檔:治理帳或審查帳是指向 /dev/zero 的符號連結時整個 lumos 吃光記憶體
severity: major
blocking: 是 — 版控能存符號連結;維護者或 CI 拉下惡意分支後跑任何走這些讀者的指令(loop list、推送前掛鉤的代碼審留痕讀者…)就 OOM
- 輸入:分支提交 `docs/.governance-log.jsonl -> /dev/zero`(審查帳 `.canary-log.jsonl` 同理,`_canary_ledger_scan` 用 `read_bytes`)。
- 走到哪:r3 把約 20 處讀者換成 `_ledger_lines(path.read_text(...))`,只前置 `path.exists()`/`is_file` 一類判斷;跟隨捷徑、不判一般檔、不限大小。跑滿回顧一族自己用 `_retro_gov_path_err` 擋住了,其餘 20 處沒有。
- 壞在哪:`read_text` 對無窮檔案不會結束,記憶體持續成長。
- 引句:「for line in _ledger_lines(path.read_text(encoding="utf-8", errors="replace")):」
- 佐證行:file: `scripts/lumos:10447`(`_loop_close_stamps`)
- 重現(實跑):
  ```
  V=$(python3 /private/tmp/claude-501/r4/exp5.py | tail -1)   # 造 repo 並把 docs/.governance-log.jsonl 換成 -> /dev/zero
  python3 scripts/lumos --vault "$V" loop list --all &  sleep 6; ps -o rss= -p $!
  → 1986976   (約 2GB,6 秒,仍在長;kill -9 才停)
  ```
- 備註:計劃〈誠實界線〉只承認「其他閘跟隨捷徑往外追加」(寫端),沒提讀端無界讀取;共用一支讀帳小函式(開檔判一般檔、設上限、再 `_ledger_lines`)就能把 20 處一併收掉,也順手解決 F3 的讀端。

### F3 非跑滿回顧的閘仍經符號連結寫出 repo 外,r3 的帳尾補換行還擴大了這條路(已記於計劃,仍是可重現的寫出 repo 外)
severity: minor
blocking: 否 — 計劃〈誠實界線〉已承認並排了 REVISIT 2026-11-06;寫入內容恆以 `{"ts": ` 開頭,測不出能變成可執行內容的路徑,實際危害是破壞檔案內容
- 輸入:`docs/.governance-log.jsonl -> <repo 外任一個自己擁有的檔>`,之後任何走 `_gate_event` 的閘(doctor、canary 擋下、code-loop…)。
- 走到哪:`_gate_event` → `_ledger_tail_needs_newline(follow=True)` 讀外部檔最後一個位元組 → `open(path, "a")` 追加。
- 壞在哪:r3 把帳尾檢查改成跟隨捷徑,所以外部檔缺換行時還會先補一個 `\n`(r3 前是直接黏在後面);外部檔因此被多寫一個位元組。
- 引句:「捷徑指到 repo 外時其他閘照舊會往外面追加(既有行為,`_gate_event` 是所有閘共用的寫入器,不在本案改)」
- 佐證行:file: `scripts/lumos:1518`(帳尾檢查 follow=True)
- 重現(實跑 /private/tmp/claude-501/r4/exp6.py):
  ```
  True
  'keep=1\n{"ts": "2026-10-06T11:21:44+08:00", "commit": "", "gate": "canary", "kind": "blocked", ...}\n'
  ```
- 備註:`_retro_gov_path_err` 已經是現成的檢查,收進 `_gate_event` 的共用寫入路徑就能一次關掉;REVISIT 到期前這條維持 minor。

總結:最嚴重 major,blocking 2 條
