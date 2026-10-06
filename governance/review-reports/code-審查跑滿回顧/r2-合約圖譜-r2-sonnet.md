severity: minor

席:合約圖譜-r2-sonnet(立場:接手的人,預設文件與現實對不上)。材料:/tmp/code-capretro-r2.patch、repo 現檔、規格 `docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md`、固定席(`lumos impact --diff ce2a961f..HEAD` 自跑)。

## 做了什麼(證據,不是 finding)
- 在 /tmp/r2-sonnet-mut 複製 repo(不含 .git)跑 `python3 scripts/test_lumos.py -k t_cap_retro`:215 passed、0 failed。另跑既有 `-k t_loop_next`(76 過)、`t_canary_record`(29 過)、`t_gov_`(156 過)、`t_loop_list`(19 過)、`t_gov_stats_gate_drift`(5 過),全綠。repo 本身沒動。
- 變異抽查(只改臨時副本的 scripts/lumos,每次只跑該支測試),結果:
  - 治理帳補換行拿掉 → `t_cap_retro_gov_tail_newline` 紅(2 條)。
  - `_retro_read_bytes` 拿掉 O_NOFOLLOW → `t_cap_retro_fifo_symlink_not_read` 紅(符號連結被跟隨,第八步判 ✓)。
  - 拿掉 O_NONBLOCK → 同一支測試紅(處置閘、--check、retro-stats 三條逾時)。
  - 審查帳切行 `split("\n")` 改回 `splitlines()` → `t_cap_retro_ledger_line_separators` 紅。
  - `--record` 指紋改成再讀一次檔 → `t_cap_retro_record_reads_once` 紅。
  - `--write` 的 O_EXCL 改成 O_TRUNC → `t_cap_retro_template_write_no_clobber` 紅(回顧檔被覆寫)。
  - `_cap_retro_next_lines` 拿掉範圍檢查 → `t_cap_retro_next_hint_scope_only` 紅(3 條)。
  - 凍結兩趟拿掉 `retro_skip=True` → `t_cap_retro_out_of_scope_not_checked` 的新斷言(帳上沒有 result_sha256)紅。
  - `_cap_retro_template_cmd` 拿掉 `_esc_clean` → `t_cap_retro_printed_cmd_escaped` 紅(doctor 那條)。
  - `_cap_retro_check` 拿掉孤立代理字元檢查 → `t_cap_retro_surrogate_no_crash` 紅。
  - accept-risk 帳壞的出口訊息改回講 `--skip` → `t_cap_retro_accept_risk_ledger_bad_exit` 紅。
  - `_retro_norm_path` 的 resolve 拿掉 ValueError → `t_cap_retro_nul_path_no_traceback` 紅。
  - 以上 12 種變異全部被抓到。只有 `_retro_has_dossier` 外層 `except (OSError, ValueError)` 單獨拿掉不會紅:Python 3.14 的 `Path.is_dir/is_file` 自己吞 ValueError,而且內層 `_retro_norm_path` 已接住,所以那兩處外層是冗餘守衛,不算缺陷。
- 既有行為:`_loop_records` 改成走 `_canary_ledger_scan`,對舊呼叫端的差別只有三點:切行改 `split("\n")`、非物件行與 loop 欄非字串的列改成跳過(舊碼會 AttributeError)、解碼失敗照舊丟 UnicodeDecodeError。真帳 3MB/3039 列掃一次 0.03 秒。loop next、canary record、gov、doctor、loop list 的既有測試全綠;`_gate_event` 與 `_append_governance_log` 只多「檔尾缺換行先補一個」,對尾端正常的帳輸出位元組不變。沒找到既有輸出被改的證據。
- 手冊:`grep -- '--template >'` 在 skills/ 與 docs/(排除卷證)沒有殘留重導向;六處手冊(含 templates.md §9)都是 `--template --write` 加「過期改好再記」;程式的旗標(`--write` 只能跟 `--template`、已存在回 2)與訊息跟手冊一致;templates.md §9 的八個族名、欄位下限(why_cap 20 字、other 要 note)跟 `_RETRO_FAMILIES` 與 `_cap_retro_check` 一致。`lumos spec-trace` 對 S1–S17 顯示綁 16、靠人 1、未標 0、懸空 0;計劃與 Systems/loop-retro.md 引的 `[test:]` 名稱全部存在。

## Findings

### F1 Systems/loop-retro.md 的 PITFALL 寫「只讀自己的一般檔」,程式與測試明確相反
severity: minor
blocking: 否 — 只是圖譜敘述跟程式對不上,不影響行為。
- 輸入:接手的人讀 Systems/loop-retro.md 最後一條 PITFALL(代碼審 r1 併發、邊界席):「…只讀自己的一般檔(不跟隨捷徑、非阻塞開檔)…」。
- 走到哪:去看 `_retro_read_bytes`,它的 docstring 寫明不要求是自己的檔;`t_cap_retro_read_not_owner_ok` 就是釘「別人的檔也要判已記回顧」。
- 壞在哪:筆記的「自己的」三個字跟程式相反;後面的人照筆記會把 `_regular_own_fd` 的擁有者檢查加回去,讓共用機器或 CI 換帳號 checkout 時合格回顧一律判過期。這屬於「筆記摘要行(線索)跟程式不一致」,依專案規則以程式為準。
- 引句:「共用機器或 CI 用別的帳號 checkout 時,合格回顧會被判成過期」
- 佐證行:file: `docs/lumos-toolchain-knowledge/Systems/loop-retro.md:26`(「只讀自己的一般檔」);file: `scripts/lumos:13123`(`_retro_read_bytes` docstring:★不要求「是自己的檔」★)附近;file: `scripts/test_lumos.py:69858`(`t_cap_retro_read_not_owner_ok`,行號為現檔近似值,用 grep 該函式名可定位)。
- 重現:`grep -n "只讀自己的一般檔" docs/lumos-toolchain-knowledge/Systems/loop-retro.md` 對照 `grep -n "不要求" scripts/lumos | grep own`。

### F2 狀態「沒有」印的指令在「已起草、尚未 --record」時照貼會回 2
severity: minor
blocking: 否 — 只是提示誤導,出口(--check、--record)在同一行後半段。
- 輸入:迴圈已記 extra-round 人裁,代理已把 `cap-retro.json` 寫好,但還沒 `--record`;這時 `canary record` 記 r4。
- 走到哪:狀態是 none(人裁之後沒有 recorded 也沒有 skipped),`_cap_retro_record_block` 走「沒有」分支,印 `怎麼做:lumos loop retro crx --template --write(派沒參與這個迴圈的乾淨代理起草),…--check 過了再 --record`。
- 壞在哪:檔已經存在,照貼第一條指令回 2 並印「回顧檔已經存在…不覆寫」。修補前是重導向會清空檔,修補後變成無害但誤導;訊息沒分「檔不存在(要產骨架)」與「檔存在但沒記(去 --check/--record)」。處置閘、doctor、retro-stats、loop next 共用同一個 `_cap_retro_fix_cmd`,四處都一樣。
- 引句:「怎麼做:{_cap_retro_template_cmd(root, loop_id)}(派沒參與這個迴圈的乾淨代理起草),」
- 佐證行:file: `scripts/lumos:13330`(`_cap_retro_template_cmd`);file: `scripts/lumos:13340`(`_cap_retro_fix_cmd` 只分 stale 與其他)。
- 重現(臨時副本,借測試輔助函式):
  `@T._cap_real_cutoff def go(): c=T._cr_repo(); T._cr_loop(c); T._cr_decide(c); T._cr_write_retro(c); r=T._cr_record(c,"r4"); r2=T._cr_retro(c,"--template","--write")`
  輸出:canary rc=2 且訊息含 `--template --write`;`--template --write` rc=2「擋下:回顧檔已經存在(governance/review-reports/crx/cap-retro.json),不覆寫」。

### F3 規格與圖譜沒跟上第一輪修補(修補引起)
severity: minor
blocking: 否 — 純文件漂移,條款綁的測試仍綠。
- 輸入:接手的人只讀規格 `審查跑滿回顧_計劃.md` 與 `Systems/loop-convergence-recording.md`。
- 走到哪與壞在哪(都是程式現檔對照得到):
  1. 計劃〈二〉的 `--template` 小節沒有 `--write`,條款 S1–S17 沒有任何一條涵蓋 r1 修補(`--write` 不覆寫、讀檔不跟隨捷徑與管線、`split("\n")` 切行、治理帳補換行、孤立代理字元)。這些只靠 Systems/loop-retro.md 的 PITFALL 帶 `[test:]`,規格的驗收條件與實作脫節。
  2. 計劃〈三〉3 與 S6 寫 loop next 判到 cap-reached「輸出應多印記人裁的指令」,現在循序單審、light、舊迴圈、帳壞一律不印,規格沒寫這個例外(t_cap_retro_next_hint_scope_only 只在 Systems 與手冊側有交代)。
  3. 計劃 S3、〈三〉1、〈四〉與 loop-convergence-recording.md 的 d7 那條 WHY 寫「過期」也印 `--template` 指令;現在過期只印「改好現有回顧檔…(或刪掉後 …--template --write 重建)」。S3 字面上因為句中仍有 `--template` 勉強成立,但語意已變。
  4. 治理帳寫入器(`_gate_event`、`_append_governance_log`)多了「檔尾缺換行先補」,記在 loop-retro.md,但管這兩支寫入器行為的 Systems/reversibility-governance-ledger.md 沒提。
- 引句:「cap-decision 不收的迴圈(循序單審、light、舊迴圈、帳壞)不叫人記人裁——照做會回 2(代碼審 r1 合約席)」
- 佐證行:file: `docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md:113`(--template 小節無 --write)、`:124`、`:129`、`:145`、`:148`;file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:34`;file: `scripts/lumos:13483-13500`(`_cap_retro_next_lines`)。
- 重現:`grep -n -e "--write" docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md` 無輸出。

### F4 幾支新測試只驗到表面(測試形狀弱,不是行為缺陷)
severity: minor
blocking: 否 — 變異抽查中對應行為都被其他測試抓到,這幾條只是守衛偏弱。
- `t_cap_retro_single_fail_banner` 只數原始碼裡 `⛔ DISPOSAL GATE FAIL` 這串字出現幾次;帳壞那條路若改成印 `⛔ DISPOSAL  GATE FAIL`(多一個空白)或改字就繞過,測試仍綠;它沒驗帳壞那條路真的呼叫 `_disposal_fail_banner`。
- `t_cap_retro_ledger_line_separators` 的 docstring 與標籤寫 U+2028/U+0085,實際只塞 `\u0085`,U+2028/U+2029 沒測(`split("\n")` 本身涵蓋,但測試宣稱的範圍比實際大)。
- `t_cap_retro_existing_gate_steps_unchanged` 只手動呼叫六支既有處置閘測試,規格 S15 寫「既有處置閘相關測試應全部維持綠」;條款綁定與凍結回放兩支被註解排除在外(全套測試會跑,但這條綁定的證據範圍小於條款字面)。
- `--write` 單獨使用(沒帶 `--template`)回 2 的分支沒有測試。
- 引句:「n = src.count("⛔ DISPOSAL GATE FAIL")」
- 佐證行:file: `scripts/test_lumos.py:69689`(`t_cap_retro_single_fail_banner`,行號近似,以函式名定位);file: `scripts/test_lumos.py:69452`(`t_cap_retro_existing_gate_steps_unchanged`)。
- 重現:臨時副本把 `_disposal_retro_ledger_bad` 的 `_disposal_fail_banner(loop_id, None, ["跑滿回顧"])` 換成 `print(f"⛔ DISPOSAL  GATE FAIL ({loop_id}: 跑滿回顧)")`,`-k t_cap_retro_single_fail_banner` 預期仍綠(推論,未實跑,故未列為缺陷)。

總結:最嚴重 minor,blocking 0 條
