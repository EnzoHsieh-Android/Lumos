severity: minor

整份 diff 讀完,逐 hunk 走過參數組合、例外、環境、掛鉤。沒有確認會出錯的行為,只有三條 minor,都是測試保護不足。

**已走過、判定沒問題的路徑**
- **參數與放置**:`-k ""` 判為沒篩選而被擋,跟 `_fanout_wanted` 同口徑。`--help` 與 argparse 錯誤在判斷之前就以 2 結束。判斷之前沒有開子程序、也沒有建暫存目錄,所以 `--list --shard` 這類組合不會提早漏過。
- **環境三條路**:
  - 推送前閘在 `scripts/hooks/pre-push` 393 行 export `LUMOS_PUSH_ATTEMPT`。
  - 切片子程序帶 `LUMOS_FANOUT_CHILD`,而且 `CLAUDECODE` 早已被拿掉。
  - CI 沒有 `CLAUDECODE`。三條路都不會誤擋。
- **誰讀 `CLAUDECODE`**:grep 整個 `scripts`,只有 `scripts/scenario_probe.py:1162`,而且它本來就會拿掉,沒人依賴它被保留。
- **執行器格式**:執行器 `scripts/test_lumos.py:49970` 印的是 `✗ FAILED {t.__name__}({N} 條斷言)`,跟掛鉤的正則 `t_[A-Za-z0-9_]*` 對得上。
- **掛鉤 shell 設定**:掛鉤只開 `set -u`,沒有 `-e` 或 pipefail。`pp_q` 在 `scripts/hooks/pre-push:130` 定義,早於呼叫處。log 檔不存在時 `grep 2>/dev/null` 吞掉錯誤,走「看完整輸出」那支。
- **逃生門理由**:`LUMOS_ALLOW_FULL_SUITE` 的理由判法(`1`、十個句點被擋)和 S1、S2 的真值格對得上。

**Findings**

1.
severity: minor
blocking: 否
引句:「r = _sp.run([sys.executable, me], env=env, capture_output=True, text=True, timeout=60)」
`t_runner_chat_full_suite_block_process` 的環境是從頭組的,沒有 `LUMOS_FANOUT_CHILD`,也沒有任何遞迴標記。如果有人把判斷改壞(例如拿掉 `snap.get("CLAUDECODE") != "1"` 那段,或把 `args.keyword or args.suite or args.list` 翻轉),這支無參數子程序就會真的跑全套。
全套裡又包含這支測試本身,於是每層再開一個無標記的全套,有炸程序的風險。`subprocess.run` 逾時只殺母程序,切片子程序自成行程群組,殺不到,會變成孤兒。這就是記憶裡「變異會炸程序」那一型。
測試也沒有第二道保險,例如開子程序前先確認 `_chat_full_suite_block` 會擋,或在子程序環境放一個遞迴深度標記。
未能重現:我在 CLAUDECODE 對話裡不能真的跑全套,也不能把守衛改壞去試,所以只憑程式結構判斷,自降一級。
佐證:`scripts/test_lumos.py:30907`、`scripts/test_lumos.py:30915`。

2.
severity: minor
blocking: 否
引句:「_os_env.environ.pop("CLAUDECODE", None)」
計劃做 1 的核心之一是「把 `CLAUDECODE` 從環境拿掉」,但沒有任何測試直接驗它。S3 的 `-k` 那格只驗「不被擋」。
把這行刪掉,`t_runner_chat_full_suite_block` 與 `t_runner_chat_full_suite_block_process` 照綠。只有在對話裡跑 `t_runner_default_fanout_*` 這類會開無 `-k` 沙盒執行器的測試時才會間接紅,在 CI 與一般終端機跑不出來。
建議 S3 前置那格的子程序測試能印出環境值,斷言 `CLAUDECODE` 不在。

3.
severity: minor
blocking: 否
引句:「if [[ "$_n" -gt 10 ]]; then echo "       (還有 $((_n - 10)) 支,看上面的完整輸出)"; fi」
S4 的測試只涵蓋兩支紅與零支紅。「超過 10 支」的截斷與「還有 N 支」文字沒有任何案例。
把 `head -10` 改成 `head -3`,或把 `_n - 10` 寫錯,測試都照綠。這是規格預期值表以外的分支,但程式有寫,沒有被保護。

**總結**:檔級最高為 minor,三條皆 minor、blocking 否。

**圖譜鏡頭**
- **`bound-tests-gate` 與 `測試假綠形態` 的 INVARIANT**:沒有被破壞。
- **新增測試的證據強度**:`t_runner_chat_full_suite_block` 的真值格是照預期值表寫死的,翻紅釘能指到具體改壞。例如拿掉 `LUMOS_PUSH_ATTEMPT` 豁免,S2 第二格會紅。
- **推送前閘的假身**:`t_prepush_blocked_last_line_is_next_step` 的假執行器補了 `✗ FAILED` 行,對應正確。
- **「表態」宣稱**:這份 diff 只動 bash 與測試執行器,說法一致。

審查過程沒有在 `/tmp/lumos-seat-work/...` 建任何暫存目錄,也沒有改任何檔。
