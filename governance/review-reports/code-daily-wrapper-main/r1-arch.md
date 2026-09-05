severity: minor

- [minor] 整份腳本包進 main() 最後才呼叫,是全 repo 唯一一支這樣寫的 shell 腳本,但有寫明且可查證的正當理由,不算 major。
  位置:`governance/daily-governance.sh:22`
  引句：「main() {」
  why: grep -rln '^main()\s*{' --include="*.sh" 掃整個 repo 只有 daily-governance.sh 一支包 main();三支對照腳本(ai-governance-research.sh、lint-watch-check.sh、autonomous-loop.sh)一律是「set 旗標後一路往下執行」的扁平寫法。所以這是專案裡原本沒有的做法。但理由寫在腳本註解(daily-governance.sh:19–21)、能對到真事故(第二輪審視六修_計劃.md:57 記 2026-09-05 09:37–12:42 邊跑邊改讀到半行 syntax error);風險只精準命中 daily-governance.sh(它是活著等三小時的外層行程),不是三支子腳本的共通風險,沒理由要求它們比照。判 minor。值得記一筆:之後別的長跑 wrapper 遇到同款風險,沿用這個做法而不是各自重新發明。

- [clean] main() 內部呼叫對象、順序、ts()/rc=$?/日誌導向寫法,跟改動前逐行相同,沒有引入第二種呼叫方式。
  位置:`governance/daily-governance.sh:26`
  引句：「$DIR/ai-governance-research.sh" >> "$DIR/logs/governance.log" 2>&1」
  why: 五段呼叫順序、參數、log 目的地、echo "[$(ts)] ... rc=$?" 寫法完全沒變,只是搬進函式體。set -uo pipefail 維持原樣(註解「不用 -e」是原本的既有選擇)。分層與依賴方向沒變,沒有新增跨層直呼。

- [clean] 新測試的位置、check() 用法、docstring 寫法、路徑算法跟緊鄰測試一致,沒有另造一套慣例。
  位置:`scripts/test_lumos.py:25860`
  引句：「p = Path(GRAPHCTL).resolve().parent.parent / "governance" / "daily-governance.sh」
  why: 路徑算法跟緊鄰 t_scenario_probe_per_scenario_max_turns(test_lumos.py:25804)同款;check(name, cond, detail) 三參數簽名一致;docstring「第 N 輪稽核(日期):為什麼+守衛什麼」跟 t_delguard_logs_ok_too、t_codex_stop_block_once 同款。subprocess.run(["bash","-n",...]) 是全 repo 第一次出現,但專案本來就沒有 shell 語法檢查 helper 可重用,且實跑整支 wrapper 在單元測試裡不可行,靜態比對 + bash -n 是限制下合理的最小驗證,不算引入第二種做法。

lumos 自動附加:派工詞尾端有附節點。autonomous-iteration-loop ★RISK★:沒動自主迴圈邏輯(呼叫方式、LUMOS_AUTOLOOP_OFF 語意、--dry-run 6 原樣搬進 main())。bound-tests-gate ★INVARIANT★:新測試是真實方法可被 -k 執行到,非懸空非偽證據,不在 [test:t_bound_tests_gate] 綁定範圍內,沒碰。canary-audit / guard-kill / slim-get / slim-install / slim-uninstall / 測試假綠形態 各 ★INVARIANT★:只在 test_lumos.py 尾端新增獨立測試,沒改任何既有測試邏輯與相關程式,全部沒碰。超出上限只列名的六篇:未觸及 scripts/lumos 本體,無關。
