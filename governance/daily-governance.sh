#!/bin/bash
# 每日治理 wrapper:一個喚醒窗內「連續」跑 治理日報 → 自主迭代 loop → lint-watch 版本掃描。
#
# 為什麼合併:閉蓋(clamshell)的 Mac 幾乎一直在睡,launchd StartCalendarInterval
# 不會把機器叫醒、且只在 FullWake 補跑 GUI agent。解法是用 pmset 每天叫醒「一次」:
#   sudo pmset repeat wakeorpoweron MTWRFSU 09:28:00
# 那一次喚醒只夠跑「一段連續工作」——分成 09:30 / 10:10 兩支,機器會在中間又睡著、
# 第二支照樣漏。故把兩件事串成這一支,趁機器醒著一口氣跑完(腳本執行中系統不會 idle-sleep)。
#
# 由 launchd com.enzo.lumos.daily-governance(09:30)觸發。各子腳本仍各自寫自己的 log。
# 第 3 步 lint-watch-check:每日查 linter 新版 → 候選暫存 governance/lint-upgrades/ + LINE 通知。
set -uo pipefail   # 不用 -e:前一支失敗不擋後一支

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ts() { date '+%Y-%m-%d %H:%M:%S'; }

mkdir -p "$DIR/logs"

# ★整段包進 main() 最後才呼叫(2026-09-05 第四輪稽核):bash 是邊讀邊執行,腳本在跑的時候(自主迴圈那段可跑三小時)
# 被人改檔,回來會從新檔的同一個 byte 位置接著讀,讀到半行就 syntax error 整支死掉——今天 09:30 那次就這樣,
# lint-watch/doctor/testmap 全沒跑。包成函式=先整份讀完再執行,改檔只影響下一次。
main() {
  echo "[$(ts)] daily-governance wrapper 開始"

  # 1) 治理日報(自設 PATH/token;log → governance.log)
  "$DIR/ai-governance-research.sh" >> "$DIR/logs/governance.log" 2>&1
  echo "[$(ts)] 治理日報 段結束 rc=$?"

  # 2) 自主迭代 loop(dry-run;log → autonomous.log)
  #    2026-09-05 暫停派工(README 審視 d3,見圖譜 Projects/README審視五修_計劃):七週週報收斂 0、待放行 0、每週 210–330 美元;
  #    dry-run 永遠走不到開 PR。開關沿用 repo 的 *_OFF 慣例,但預設 1(=暫停);要臨時開回:LUMOS_AUTOLOOP_OFF=0。REVISIT 2026-10-05 決定給它真產出路徑或正式退場。
  if [ "${LUMOS_AUTOLOOP_OFF:-1}" != "1" ]; then
    "$DIR/autonomous-loop.sh" --dry-run 6 >> "$DIR/logs/autonomous.log" 2>&1
    echo "[$(ts)] 自主 loop 段結束 rc=$?"
  else
    echo "[$(ts)] 自主 loop 段暫停中(2026-09-05 d3;LUMOS_AUTOLOOP_OFF=0 可開回)" >> "$DIR/logs/autonomous.log" 2>&1
    echo "[$(ts)] 自主 loop 段暫停中(2026-09-05 d3)"
  fi

  # 3) lint-watch 版本掃描(fail-open;log → lint-watch.log)
  "$DIR/lint-watch-check.sh" >> "$DIR/logs/lint-watch.log" 2>&1; rc=$?
  echo "[$(ts)] lint-watch 段結束 rc=$rc"

  # 4) doctor 每日跑(fail-open;log → doctor-daily.log)
  # intake守衛 T4 排程線(2026-08-30 d1,外家 r3 唯一補件):T4 的滾動窗計數器住在 doctor 的
  # [I] 段;此前 doctor 只在 push/CI 跑——「doctor 每天跑」曾是未查證的假宣稱,這行讓它成真。
  ( cd "$DIR/.." && python3 scripts/lumos doctor --ci ) >> "$DIR/logs/doctor-daily.log" 2>&1; rc=$?  # --ci=治理事件入帳(回訪掃描 v3 接電條款:無此則 nags 14 天升級鏈斷路)
  echo "[$(ts)] doctor 段結束 rc=$rc"

  # 5) testmap 每日重建(2026-09-05 第二輪審視 d5:建過一次後落後 614 個 commit 沒人重建;0.6 秒)
  ( cd "$DIR/.." && python3 scripts/lumos testmap build ) >> "$DIR/logs/testmap.log" 2>&1; rc=$?
  echo "[$(ts)] testmap 重建 rc=$rc"

  echo "[$(ts)] daily-governance wrapper 完成"
}

main "$@"
