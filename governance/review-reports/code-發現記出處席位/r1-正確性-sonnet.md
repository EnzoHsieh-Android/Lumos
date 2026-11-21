severity: major

審查範圍:逐 hunk 讀完整份 diff,對照計劃 S1–S12 與預期值表,並實跑 `python3.14 scripts/test_lumos.py -k finding_seat`(43 passed)。固定席節點這次沒附(LUMOS-LENS 說鏡頭計算超時),所以固定席判定不適用;圖譜面只對照了 diff 內的 `Systems/loop-convergence-recording` 與 `Systems/canary-audit` 兩篇,見文末。

## Findings

### c1 輪次記號正則吃掉模型版本號
severity: major
blocking: 是
file: `scripts/lumos:18068`(`_SEAT_ROUND_MARK_RE`)與 `scripts/lumos:18103`(`_seat_noise_counts` 的 sub)
具體失敗場景:輪次記號的正則 `\d+` 只要後面跟 `-字母…` 就會被刪,模型名裡的版本號也中招。同一席不同模型會被併成一列,違反計劃〈做法〉的「不同模型不合併」與 S8 的「同一席不同模型分開列」。
- 實跑 `_SEAT_ROUND_MARK_RE.sub("", n)`:`外家-gemini-2-flash` 和 `外家-gemini-3-flash` 都變成 `外家-gemini--flash`。
- 真帳 `docs/.canary-log.jsonl` 裡也有:`外家codex-gpt-5.6-terra` 變 `外家codex-gpt-5.-terra`,`r2-codex` 變 `-codex`,`s6-external-premise-gemini-3-flash` 變 `…gemini--flash`。
- 結果是逐席沒用率在 `gov --stats` 印出被刪壞的席名,gemini-2 與 gemini-3 的沒用率混成一列。測試只用 `架構對齊r2-sonnet` 這種好情形,抓不到。
- 最小重現:`python3.14 -c "import re;R=re.compile(r'(?:-?r\d+|\d+)(?=-[A-Za-z][\w.]*$)');print(R.sub('','外家-gemini-2-flash'),R.sub('','外家-gemini-3-flash'))"`,兩個輸出相同。
引句:「_SEAT_ROUND_MARK_RE = re.compile(r"(?:-?r\d+|\d+)(?=-[A-Za-z][\w.]*$)")」

### c2 首筆帳取最小值沒有測試鎖住
severity: major
blocking: 是
file: `scripts/lumos:19587`,測試 `scripts/test_lumos.py` 的 `t_canary_record_finding_seat`
具體失敗場景:必填判定的「首筆帳」取 `min(keys)`,但沒有測試鎖住它。
- 我在複製的 repo 把 `min(keys)` 改成 `max(keys)`,`t_canary_record_finding_seat` 照樣全綠(34 passed, 0 failed)。
- 原因是 S6 只造了「單筆帳且早於生效日」的迴圈(`code-fs-old`),其他迴圈的帳全在生效後。沒有「首筆在生效前、後面輪次在生效後」的混合迴圈。
- 改壞後的真實後果:11-21 開的舊迴圈,到 11-23 記 r2 載體時被誤判成必填,rc 2 擋下。
- 這是 S6「首筆帳早於生效日不必填(不回溯舊迴圈)」唯一的驗證點,屬於測試抓不住錯,依 severity 判準算 major。
- 對照:把空帳那條改成 `else 0.0` 會被測試抓到(1 failed),把「席名比對加上本筆自己的 auditor」拿掉也會被抓到(2 failed)。
- 最小重現:在 `scripts/lumos` 把 `first = min(keys) if keys else …` 的 `min` 換成 `max`,跑 `python3.14 scripts/test_lumos.py -k canary_record_finding_seat`,結果 34 passed。
- 建議補一條測試:同一個迴圈先記一筆生效前的帳(用 `_ledger_patch_last` 改 ts),再記一筆生效後的載體,不帶席位,預期 rc 0。
引句:「first = min(keys) if keys else _loop_ts_key(str(rec.get("ts") or ""))」

### c3 兩處文件沒寫席名不帶輪次
severity: minor
blocking: 否
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:55`,以及 `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md` 新增的段
具體失敗場景:S12 要求手冊與筆記「逐處讀,確認三處都講到必填條件、值要是同輪席名、重現不到的也要標、席名不帶輪次」。
- 06 命令速查那一列和 `loop-convergence-recording` 那一段都沒有寫「席名不帶輪次」,只有 `lumos-code-loop/SKILL.md` 第 6 步有。
- 照 06 速查做的人會把 `正確性r2-sonnet` 這種席名記進帳,統計雖會去輪次記號(正則見第一條),但仍違反 S12 所列的三處同寫。
- 06 與 loop-convergence 有講必填、同輪帳上、重現不到,只缺這一項。
引句:「席名照那一席記帳時的 `--auditor` 抄,載體最後記;2026-11-22 起新開的代碼審迴圈必填」

## 逐項檢查後判為正確的部分

- **生效日與時區**:`_FINDING_SEAT_SINCE` 是 `2026-11-22T00:00:00+08:00`,以 `_loop_ts_key` 換成 UTC 秒比較。台北 11-22 01:00(UTC 11-21 17:00)判必填,11-21 23:59+08 判不必填,都對。無時區或讀不動的帳上時間,必填路徑擋下不放行。環境變數 `9999-12-31T00:00:00+08:00` 也讀得成。
- **空帳**:`first=None` 時走到擋下,fail closed;空帳拿本筆時間比,有測試鎖住(改成 `0.0` 會紅)。
- **寫一半**:兩種擋下(必填缺漏、席名比不中)都在 `path` 寫帳之前 return 2,不留半寫帳。`_finding_seat_write_block` 放在 `_loop_records_checked_ex` 讀帳之後,之前的 `_round_format_write_block` 已擋壞帳,`rows_err` 不會悄悄走到比對。
- **重記與同輪多筆載體**:席名只認 `round_id` 同輪帳上的 auditor,加本筆自己的;上一輪的席被擋(測試有)。統計取同 (迴圈, 輪) 最後一筆,依據是 `gov` 的 `_raw` 保持帳檔追加順序,沒被排序,所以「最後」就是帳上最後。
- **新舊互讀**:舊帳沒欄位時 `finding_seats` 取不到,統計整列略過;型別壞掉在 `_gov_event_types_ok` 整列丟棄(與 `finding_sources` 同做法)。處置閘不讀這欄,S10 測試覆蓋三種帳。舊程式讀新帳,多出的欄位被忽略。
- **窗口邊界**:`_seat_noise_window_start` 取 `max(gov 起算點, now−56 天)`,55 天算、57 天不算,測試鎖得住。
- **新增告警**:C901 放行理由屬實,`cmd_canary` 本來就極複雜,這次新增的邏輯已拆成獨立函式。

## 圖譜鏡頭

固定席節點沒附,無法逐條判;下面是 diff 內兩篇的判定。
- `Systems/loop-convergence-recording`:新增的段只加不改既有行為;「載體最後記」那條沿用,不破壞既有合約。
- `Systems/canary-audit`:d6 只註記 d4 不涵蓋這項,不動 d4 本身;決策欄位完整。

severity: major
(最高)
