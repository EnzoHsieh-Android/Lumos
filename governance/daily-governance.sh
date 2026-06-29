#!/bin/bash
# 每日治理 wrapper:一個喚醒窗內「連續」跑 治理日報 → 自主迭代 loop。
#
# 為什麼合併:閉蓋(clamshell)的 Mac 幾乎一直在睡,launchd StartCalendarInterval
# 不會把機器叫醒、且只在 FullWake 補跑 GUI agent。解法是用 pmset 每天叫醒「一次」:
#   sudo pmset repeat wakeorpoweron MTWRFSU 09:28:00
# 那一次喚醒只夠跑「一段連續工作」——分成 09:30 / 10:10 兩支,機器會在中間又睡著、
# 第二支照樣漏。故把兩件事串成這一支,趁機器醒著一口氣跑完(腳本執行中系統不會 idle-sleep)。
#
# 由 launchd com.enzo.lumos.daily-governance(09:30)觸發。各子腳本仍各自寫自己的 log。
set -uo pipefail   # 不用 -e:前一支失敗不擋後一支

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ts() { date '+%Y-%m-%d %H:%M:%S'; }

echo "[$(ts)] daily-governance wrapper 開始"

# 1) 治理日報(自設 PATH/token;log → governance.log)
"$DIR/ai-governance-research.sh" >> "$DIR/logs/governance.log" 2>&1
echo "[$(ts)] 治理日報 段結束 rc=$?"

# 2) 自主迭代 loop(dry-run;log → autonomous.log)
"$DIR/autonomous-loop.sh" --dry-run 6 >> "$DIR/logs/autonomous.log" 2>&1
echo "[$(ts)] 自主 loop 段結束 rc=$?"

echo "[$(ts)] daily-governance wrapper 完成"
