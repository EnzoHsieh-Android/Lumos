# cb3 r1 架構對齊席

### arch-f1
severity: major
引句:「local msg; msg="$(echo "$out" | sed -n 's/^MSG://p' | head -1)"」
佐證:file: `governance/autonomous-loop.sh:250`
說明:run_replay 的 LINE 文字在 python 端組好、shell 只抽前綴;對照組 run_nags/run_exam 都是 bash 自己用 head/cut/grep/sed 組最終文字——「組 LINE 文字」的責任從 shell 移進 python,跟同檔另外兩個對照函式的分工不一樣。

### arch-f2
severity: minor
引句:「resolver 與 loop status 同一套 loop/round 篩選(r1 arch-f1 的第二種做法在此交代)。」
佐證:file: `scripts/lumos:3728`
說明:severity-check 吃帳列座標,姊妹收貨指令(quote-check/seat-check)一律吃檔案路徑——介面形狀分岔;作者已在註解自陳理由(對帳對象是帳列非檔案),非疏漏,列出讓人知道家族現在有兩種掛法。

### arch-f3
severity: minor
引句:「_SEV_WRITESIDE_CUTOFF = "2026-08-27"」
佐證:file: `scripts/lumos:3673`
說明:同檔既有兩個分界日常數(LUMOS_PANEL_K2_CUTOFF/RETIRE_CUTOFF)都是 env 可覆寫;新常數寫死。註解有講為何不給覆寫入口(防時戳造假後門),理由站得住,但手法確與既有分岔,列出示為刻意。

## 對齊良好的面
- _report_severities/_severity_check_row 標單一實作給兩處共用,同 _quote_rows 套路。
- rc 0/1/2 語意全案一致;spec_path 正規化完全比照 report/snapshot;argparse dest 前綴與 --repo 預設分法一致。
- replay_weekly 走 subprocess 不跨層 import,同家族模組一致;git 直呼 subprocess 同全檔慣例。
- run_replay 骨架(週戳/log/LINE/|| true)同 run_exam 家族;無參數同 run_probe 前例。
