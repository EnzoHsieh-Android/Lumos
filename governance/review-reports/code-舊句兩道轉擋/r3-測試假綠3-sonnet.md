severity: minor

總覽:修補新增或改過的斷言,17 種改壞全部翻紅;另外補做的 15 種有 6 種改壞後仍綠(M30、M34、C1、C2、H1 到 H4、M36)。其中 4 條值得記成 finding,都是測試守得不夠緊,產品行為本身對。原版工作目錄我沒動,實驗全在 `/tmp/lumos-seat-work/code-舊句兩道轉擋/測試假綠3-sonnet/` 的 clone 裡。

## F1 巢狀太深只測了 2 個呼叫端,另 2 個走同一支 `_note_reread_json` 的呼叫端改回原寫法仍全綠
severity: minor
blocking: 否

引句:「已提交的紀錄巢狀太深(13 萬層陣列,不到 256 KB)→ 判不了、rc1、點名那個檔講讀不成 JSON」

- 失敗場景:`_note_reread_json` 有 4 個呼叫端。
  - 設定檔:`scripts/lumos` 的 `_note_reread_config`,`cfg = _note_reread_json(text)`。
  - 判定者報告:`cmd_note_audit_reread_record`,`items = _note_reread_json(block) if block is not None else bad`。
  - 已提交紀錄:`_note_reread_verdict_doc`。
  - 工作目錄紀錄:`_note_reread_wt_verdicts`。
  - 修補只替後兩個加了深層巢狀測試。把前兩個改回 `json.loads`,`-k t_reread_block` 與 `-k t_note_audit_reread` 仍是 91 與 130 全過。
- 重現,設定檔那一支:
  - 指令:`.lumos/config.json` 放 13 萬層 `[`,跑 `reread-check --gate`。
  - 修前 88322e46:rc1,「判不了:沒預料到的錯誤(RecursionError)」。
  - 修後 a4d42fea:rc1,「.lumos/config.json 讀不成 JSON,回頭重讀照預設 block」。
  - 把設定檔那行改回 `json.loads`(C1):退回「沒預料到的錯誤(RecursionError)」。
- 重現,報告那一支:
  - 指令:報告的 json 區塊放 13 萬層 `[`,跑 `reread-record`。
  - 修前:rc1,Traceback。
  - 修後:rc2,「找不到完整、解析得了的 ```json 區塊」。
  - 把報告那行改回 `json.loads`(C2):退回 Traceback、rc1。
- 同一案例:

| claim | input | expected | case_source | before | after | 歸因 |
|---|---|---|---|---|---|---|
| 設定檔深層巢狀不再是「沒預料到的錯誤」 | 13 萬層 `[` 的 config.json | 讀不成 JSON | 我補的案例 | 沒預料到的錯誤(RecursionError) | 讀不成 JSON | 有證據的原有漏查 |
| 報告深層巢狀不崩出堆疊 | 13 萬層 `[` 的 json 區塊 | rc2 乾淨訊息 | 我補的案例 | Traceback | rc2 | 有證據的原有漏查 |

- 歸因說明:修前沒有這兩個測試,修補補了同族兩支卻漏了另兩支。產品現況正確,缺的只是守衛。

## F2 修補新增的 head_sha 記被推頂端,只有「有東西」那筆有測試
severity: minor
blocking: 否

引句:「head_sha 一律記被推頂端(算得出來時;算不出來 _gate_event 補 HEAD)」

- 失敗場景:`_note_reread_ledger` 給 skipped(param、skipped)、none、covered 與 undecidable 這四種帳新傳了 `head_sha=tip`。
  - 把這 4 處拿掉(H1 到 H4),`-k t_reread_block` 與 `-k t_note_audit_reread` 仍全過(91 與 130)。
  - 測試只在 `t_reread_block_ledger_fits_4k` ④驗了「有東西」那筆。
  - 後果:推非 HEAD 的 ref 時,這幾種帳的 head_sha 會悄悄記成 HEAD,帳綁錯提交。
- 重現:範圍 `base..c1`(c1 只動文件),HEAD 在更後面的 c2,跑 `reread-check --gate`,看 none 事件的 head_sha。
  - 修前 88322e46:head_sha 等於 HEAD(c2)。
  - 修後 a4d42fea:head_sha 等於 c1。
  - H2 改壞:退回 c2。
- 同一案例:

| claim | input | expected | case_source | before | after | 歸因 |
|---|---|---|---|---|---|---|
| none 帳的 head_sha 是被推頂端 | 範圍終點 c1、HEAD 為 c2 | head_sha 等於 c1 | 我補的案例 | c2(HEAD) | c1 | 有證據的原有漏查 |

- 歸因說明:這個行為是修補新加的,而且是對的,只是沒有測試守。

## F3 清掉繼承略過變數的測試,觀察不到「整族前綴清除」這個性質
severity: minor
blocking: 否

引句:「清除範圍縮成只清其中一個(或寫死名單漏掉)就有一支紅」

- 失敗場景:`_isolate_environment` 的清除迴圈改成寫死名單,剛好列 `LUMOS_SKIP_REREAD_CHECK`、`LUMOS_SKIP_NOTE_SHAPE`、`LUMOS_SKIP_DRIFT_CHECK` 這三個(M30)。
  - `-k t_runner_drops_inherited_skip_env` 仍是 3 passed、0 failed。
  - 但這份名單漏了其他同族變數。實測 `LUMOS_SKIP_NOTE_AUDIT=1 LUMOS_SKIP_CODE_LOOP=1 LUMOS_SKIP_FIX_CHECK=1 LUMOS_SKIP_BOUND_TESTS=1 LUMOS_SKIP_LINT_NEW=1 python3.14 scripts/test_lumos.py -k t_note_audit`:
    - 現況(前綴清除):342 passed、0 failed。
    - M30 改壞:`t_note_audit_code_review_r2_regressions` 紅,rc1。
  - 筆記與註解宣稱「清整族(前綴)不列名單:新加的略過變數不用回來補」,測試只用 3 個變數,這個性質沒被守。
- 對照:拿掉整段(M27)是 7 條斷言紅,只清 `LUMOS_SKIP_REREAD_CHECK`(M28)是 5 條紅,漏掉 `LUMOS_SKIP_DRIFT_CHECK`(M31)也紅。

| claim | input | expected | case_source | before | after | 歸因 |
|---|---|---|---|---|---|---|
| 名單改寫死三個 | M30 改壞 | 該紅 | 我設計的改壞 | 修前沒有此測試 | 仍綠 | 未判定:修前是 main() 清前綴的另一種寫法,沒有可比的測試 |

## F4 帳來源欄 ci 對 hook 的區分只驗 ci 這一邊
severity: minor
blocking: 否

引句:`got[-1].get("note", "").endswith("來源 ci")`

- 失敗場景:把 `_note_reread_ledger_found` 的來源寫死成 `ci`(M36),`-k t_reread_block` 與 `-k t_note_audit_reread` 仍是 91 與 130 全過。
  - 本機掛鉤跑的帳全被標成 ci,事後依來源統計會分不出本機與 CI。
- 歸因:有證據的原有漏查。
  - 修前版本把同一處 `src` 寫死成 `"ci"`(B36),`-k t_reread_block` 仍是 84 passed、0 failed。
  - 修補把 `"來源 ci;" in` 改成 `endswith("來源 ci")`,仍然只驗 ci 一邊。

## 已驗主張(正向)
修前一律指 88322e46,修後指 59f8f92b(a4d42fea 只多卷證)。

| claim | input | expected | case_source | before | after | 結論 |
|---|---|---|---|---|---|---|
| 工作目錄紀錄的守門在 prepare 與 `drift ack --kind reread` 兩邊都有效 | 符號連結、FIFO、超過 256 KB、形狀壞(不是物件、rows 不是清單)、13 萬層巢狀、資料夾是符號連結,各一組 | prepare 不崩、不算「只差提交」;ack 回 rc2 | `t_reread_wt_records_guarded` 17 條 | 深層巢狀 prepare 崩出堆疊(我用報告區塊另行重現) | 全綠 | 已修復。M1 到 M7 與 A1 到 A4 各自翻紅,A0 對照組綠 |
| 提交指令列具體檔名 | 三個呼叫點(record、prepare、check) | 列檔名,不列整個資料夾 | `t_note_audit_reread_prepare_skips_uncommitted_records`、`t_note_audit_reread_record`、`t_reread_block_hook_and_ci_wiring` | 列整個資料夾 | 列檔名 | 已修復。M9、M24、M25、M26、M33 三處各自翻紅 |
| 帳整行不超過 4096 位元組 | 條目數 1 到 60 × 條目長度 ×1 到 ×20 × 沒對照 0 到 50 篇 | 每組整行 ≤ 4096 | `t_reread_block_ledger_fits_4k` 的 ② | 部分組合超過(例如 4120) | 全部不超過 | 已修復。M14、M15、M16、M17 與 nodes 上限改 None 都翻紅 |
| 大小訊息印位元組 | 上限加 1 位元組 | 兩個數字不同;剛好等於上限照寫 | `t_reread_record_refuses_unreadable_size` | 都取整成 256 KB | 262145 對 262144 | 已修復。M11、M12、M13 翻紅 |
| 判不了的 skipped 帳也帶 state | warn 加壞紀錄 | state 為 undecidable | `t_reread_block_undecidable` 的 ⑤ | 沒有 state | 有 | 已修復。M18 翻紅 |
| 預設 hook 路徑與相對路徑有行為測試 | `.git/hooks` 錯字、相對路徑不接根 | 紅 | `t_hooks_path_dir_shared` | 只讀原始碼字串 | 行為斷言 | 已修復。M19、M20 翻紅 |
| 清略過變數併進 `_isolate_environment` 後順序仍對 | 迴圈挪到 `LUMOS_SKIP_CLAUDE_PLUGIN` 設為 1 之後 | 紅 | `t_runner_isolates_claude_plugin` | 在 main() 先清 | 在函式內先清 | 順序有守(M29b 紅)。但 `-k t_runner_drops...` 與 `-k t_install` 本身看不到,守衛靠另一支測試 |

- 未判定:
  - 工作目錄 FIFO、符號連結只驗了 prepare 與 ack,沒單獨驗 `reread-check` 的 `_note_reread_wip_left` 路徑(共用同一支函式,沒另造案例)。
  - `_note_reread_add_cmd` 的 `shlex.quote` 對非 ASCII 數字檔名沒測,也沒看到會出事的情境。
  - Windows 沒驗:repo 沒有 Windows CI,`mkfifo` 缺時整支測試跳過。

## 改壞實驗總表
指令:`python3.14 scripts/test_lumos.py -k <子集>`,在 clone 上改後清 `__pycache__`(用 `--shared` clone 逐一重建,等同清過)。

| 編號 | 改了哪裡、怎麼改 | 跑哪個 -k | 結果 |
|---|---|---|---|
| M1 | wt_verdicts 拿掉符號連結判斷 | t_reread_wt_records_guarded | 紅(符號連結組) |
| M2 | 拿掉 `is_file` | 同上 | 紅(FIFO 組逾時 rc=-9) |
| M3 | 拿掉大小上限 | 同上 | 紅(太大組) |
| M4 | 拿掉資料夾符號連結判斷 | 同上 | 紅 |
| M5 | uncommitted 不驗形狀 | 同上 | 紅(rows 非清單組) |
| M6 | `_note_reread_json` 不接 RecursionError | 同上 | 紅(巢狀組與行程內替身) |
| M7 | wt_verdicts 只接 OSError | 同上 | 紅 |
| A0 | ack 改用自寫迴圈,四道守門全留(對照組) | 同上 | 綠(預期) |
| A1 到 A4 | 同一自寫迴圈,分別拿掉:資料夾連結、符號連結、大小、`is_file` | 同上 | 各自紅 |
| M9 | add_cmd 改列整個資料夾 | wt、prepare_skips、record、hook_and_ci 等 | 多支紅 |
| M24 | 只改 record 那一處 | t_note_audit_reread_record、t_reread_block | 紅 |
| M25 | `_note_reread_wip_left` 回空 | prepare_skips | 紅 |
| M26 | 只改 check 那一處 | prepare_skips | 紅 |
| M33 | 只改 prepare 那一處 | prepare_skips | 紅 |
| M11 | 提示只講最長那行 | refuses_unreadable_size | 紅 |
| M12 | 大小訊息改回取整 KB | 同上 | 紅 |
| M13 | `size > max_bytes` 改 `>=` | 同上 | 紅(對照組) |
| M14 | 量時不傳 head_sha | ledger_fits_4k | 紅 |
| M15 | 清單放回 note | 同上 | 紅 |
| M16 | `_gate_event_fit` 只處理第一個鍵 | 同上 | 紅 |
| M17 | 寫帳不傳 head_sha | 同上 | 紅 |
| nodes 上限 | nodes_cap 20 改 None | 同上 | 紅(⑤) |
| M18 | warn 下 skipped 不帶 state | t_reread_block_undecidable | 紅 |
| M19 | 預設 hook 路徑 hooks 改 hook | t_hooks_path_dir_shared | 紅 |
| M20 | 相對路徑不接根 | 同上 | 紅 |
| M23 | 來源欄寫死 hook | hook_and_ci_wiring | 紅 |
| M27 | 拿掉清略過變數迴圈 | t_runner_drops_inherited_skip_env | 紅 |
| M28 | 只清 REREAD_CHECK | 同上 | 紅 |
| M31 | 寫死名單漏 DRIFT_CHECK | 同上 | 紅 |
| M29 | 迴圈挪到 CLAUDE_PLUGIN 設定之後 | t_runner_drops...、t_install | 綠;改跑 t_runner_isolates_claude_plugin 則紅 |
| J1 | prepare 不印「記得提交」 | prepare_skips | 紅 |
| M30 | 寫死名單恰好三個 | t_runner_drops... | 綠(F3) |
| M34 | uncommitted 不再略過 tip 已有的檔名 | prepare_skips、wt_guarded | 綠。要工作目錄那份改過內容才有差別,合理情境很窄,不標 finding |
| C1 | 設定檔改回 `json.loads` | t_reread_block、t_note_audit_reread | 綠(F1) |
| C2 | 報告改回 `json.loads` | 同上 | 綠(F1) |
| C3 | 已提交紀錄改回 `json.loads` | 同上 | 紅(對照) |
| H1 到 H4 | param/skipped、none、covered、undecidable 不傳 head_sha | 同上 | 綠(F2) |
| M36 | 來源欄寫死 ci | 同上 | 綠(F4) |

preserve 子集全綠:`-k gate_event` 5、`t_drift_m1_events_and_budget` 16、`t_guard_kill_rc_precedence` 4、`t_guard_kill_json_purity` 6、`t_reinject_preserves_outside` 3、`t_drift_ack` 62、`t_runner` 82、`t_command_index_complete` 14。

## 測試本身的正確性
- 行程內把 `sys.modules["json"]` 換成替身,放在 `try/finally` 裡還原,沒問題。替身只讓 `loads` 丟 RecursionError。
  - 換成會讓內容照樣解得開的實作,對照 `got == ({}, [])` 的寫法,測試會紅,不是空轉。
  - 工作目錄紀錄全被忽略時,③ 單獨會假綠,但 ④ 對照組會紅。
- 暫存目錄全由 `_isolate_environment` 的拋棄式 TMPDIR 在收尾清掉,沒看到殘檔害別的測試。FIFO 組逾時後 `rmtree` 也能清。
- 13 萬層巢狀:這台 Python 3.14 的上限固定約 16 MB,`ulimit` 改不動(測過預設 8176 KB,硬上限 65520 KB 也一樣);不到 256 KB 的檔最深約 13.1 萬層,逼近上限。
- `t_runner_drops_inherited_skip_env` 從 1 個子行程變 3 個:單跑 37.7 秒(餘裕 5x),不影響 180 秒上限。

## 三問
1. 原問題的修復效果有何行為證據?
   - 工作目錄紀錄的守門:7 種壞檔都不崩,見上表。
   - 帳長度:整行 ≤ 4096。
   - 訊息:位元組數。
   - 提交提示:改列具體檔名。
   - warn 下判不了的 skipped 帳:帶 state。
   - 這些由改壞實驗與 before/after 重現支撐。
2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?
   - 正常路徑與已測的錯誤路徑都成立,preserve 子集全綠。
   - 相鄰路徑有 4 處測試不緊(F1 到 F4),產品行為本身都對。
3. 新發現的同一案例修前、修後各是什麼結果?
   - F1:設定檔修前「沒預料到的錯誤」、修後「讀不成 JSON」,報告修前 Traceback、修後 rc2。
   - F2:none 帳的 head_sha 修前是 HEAD、修後是被推頂端。
   - F3、F4 沒有可比的修前測試,見上表。

## 圖譜鏡頭(固定席)
- `Issues/code-loop守衛main-direct盲區`:修補只動 `scripts/lumos` 與 `scripts/test_lumos.py`,沒碰 `scripts/hooks/pre-push`,tier 判定與 code-loop check 的 merge-base 邏輯不受影響。
- `Systems/reversibility-governance-ledger`、`存量漂移守衛`、`筆記內容閘`:共用的 `_gate_event_fit` 被拆成 `_gate_event_fit_drop` 並允許鍵清單。單一字串鍵行為不變(`-k gate_event` 5 與 `t_drift_m1_events_and_budget` 16 全綠),所以「行為不變」的說法仍成立。
- `Systems/guard-kill` 兩條 INVARIANT:rc 優先序 4 與 JSON 純度 6 全綠,diff 沒碰。
- `Systems/lumos-cli-read`、`lumos-cli-lifecycle`、`pitfalls-code-loop`:search 排除 superseded、re-inject 保留 sentinel 之外內容(`t_reinject_preserves_outside` 3 全綠)、PITFALL_CLASSES 與 difficulty 的同步,這次改動都沒碰,不影響。
- 其餘「超出上限只列名」的節點,我沒讀。

最高等級:minor
