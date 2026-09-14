severity: major

## F1 官方文件教的 dart 宣告寫法,會讓官方推薦的驗收指令 `lumos lint-check --smoke` 誤報失敗
severity: major
blocking: 是
引句:「dart analyze --format=json {LINT_FILES} 2>/dev/null | python3 scripts/lumos dart-sarif --out {LINT_SARIF_OUT}」
file: `scripts/lumos:20981-20982`(同段文字也逐字出現在 `docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md:119` 與 `docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md:154`,三處都是這次新增)

三個月後接手的人照這三份文件把上面這行原封放進消費 Flutter 專案的 `.lumos/lint.json`(鍵名 `"dart"`),推送前那道新增告警閘(`_lint_new_verdict`)完全沒問題——我實測過,乾淨/新增/環境不可用三態都正確判定。但 doctor 的 Check F 明確教人「接好之後跑 `lumos lint-check --smoke` 驗它真的跑得動」,這一步會現場翻紅。

**最小重現**(全部在臨時目錄跑,未動 repo):
```
$ cat .lumos/lint.json
{ "dart": ["dart analyze --format=json {LINT_FILES} 2>/dev/null | python3 <repo>/scripts/lumos dart-sarif --out {LINT_SARIF_OUT}"] }
$ python3 <repo>/scripts/lumos lint-check --smoke
✗ lint-check: .lumos/lint.json 有 1 個問題:
  [dart] 冒煙失敗:命令跑不出可解析 SARIF(task 不存在/工具沒裝?)｜dart analyze --format=json {LINT_FILES} 2>/dev/null | python
```
這台機器確實裝了 Dart 3.13.3、宣告完全照文件寫。

**根因**:`cmd_lint_check --smoke`(`scripts/lumos:17186-17191`,這次沒改動)直接把宣告字串原樣丟給 `_lint_run_and_parse`,不會替換 `{LINT_FILES}` token(那個替換只在新增告警閘 `_lint_new_verdict` 裡做,`scripts/lumos:18220-18238`)。字面上的 `{LINT_FILES}` 餵給 `dart analyze` 會被當成不存在的路徑,dart 印出用法說明(非 JSON)到 stdout;而這支新指令的核心設計恰好就是**讀不懂就 rc2、不寫結果檔**(這正是這次 diff 要修的「假綠」問題),於是 `_lint_run_and_parse` 讀到空檔判 `ok=False`,`--smoke` 把它算成「命令跑不動」。

這不是這次 diff 直接改壞的程式(`cmd_lint_check` 本身沒被動到),但它是這次 diff **新推廣、寫進三份文件的官方 Dart 宣告寫法**唯一會踩到的雷:我對照過同一份 `pitfalls-lint-adapter.md` 裡既有的 Python-semgrep 範例(`{ "py": ["semgrep … {LINT_FILES}"] }`,未改動),照理該有同樣的洞,但我實測發現 ruff/sqlfluff/stylelint 三支既有橋接對著不存在的路徑跑,**要嘛照樣吐得出一份可解析的 SARIF(ruff 對壞路徑吐一個 `E902 io-error` 的假 result,`ok=True`)、要嘛在解析失敗時退回空陣列**(sqlfluff/stylelint 的 `cmd_sqlfluff_sarif`/`cmd_stylelint_sarif` 對非法 JSON 一律 `data = []`,一定寫出零筆結果的合法 SARIF)——**只有 dart 這支因為刻意選了「讀不懂就不寫檔」而被 `--smoke` 的這個既有缺口燒到**。三個月後的人會看到「dart 沒裝」這種誤導字樣,而 dart 明明裝好也接對了。

## F2 README.en 把 09-14 才真跑過的 Dart 橋接,塞進標「as of 2026-09-13」的段落
severity: minor
blocking: 否
引句:「piped through `lumos dart-sarif`」
file: `README.en.md:262`(新增列;同段落標題句「every stack has been put through the gate for real」在 `README.en.md:252`,這次未改動)

新增的 Dart 列被放進「As of 2026-09-13, every stack has been put through the gate for real」這句話管的表格裡,等於宣稱 Dart 也是 2026-09-13 之前就實測過。但同一批 diff 寫進圖譜的 `docs/lumos-toolchain-knowledge/Systems/pitfalls-lint-adapter.md` 明講「## Dart 橋接:讀不懂就失敗,不吐空結果（2026-09-14）」,`linter精選目錄.md` 也寫「2026-09-14 起用 `lumos dart-sarif` 轉」——真實驗證日期是 09-14,晚於段落宣稱的 09-13 一天。三個月後想用日期重建時間線的人,會看到同一份 PR 對同一件事寫兩個不同日期。不影響任何機械閘,純文件內部日期矛盾。

## 舊句「Dart 沒有轉換器/接不上」全文檢索
排除 `governance/review-reports/` 與 `governance/replay/`(卷證)後,全 repo 沒有找到任何殘留的舊句在講「Dart 沒有 SARIF 轉接器」「Dart 這塊接不上」——README.en.md、`linter精選目錄.md`、`pitfalls-lint-adapter.md` 三處舊句都在這次 diff 裡被同步改掉,沒有漏改的分身。中文版 `README.md` 本來就沒有這張逐棧 gate 表格,不存在對不上的問題。

## 消費專案拿不拿得到 `lumos dart-sarif`
拿得到,而且不用做任何額外動作。`scripts/lumos` 整支在 `_VENDORED_TOOLKIT`(`scripts/lumos:13623`)清單裡,`lumos update`/`bootstrap` 是整檔複製,消費專案跑一次 `lumos update` 就連 `dart-sarif` 子指令一起拿到,不需要另外裝 skill 或改設定。要用的話跟其他棧一樣得自己在專案的 `.lumos/lint.json` 裡宣告(`"dart": ["dart analyze --format=json {LINT_FILES} …"]`,鍵是不帶點的副檔名 `dart`,這點三份文件都沒有像 `pitfalls-lint-adapter.md:106` 的 Python 範例那樣給出完整 `{"dart": […]}` JSON 片段,但跟既有 sqlfluff/stylelint 兩支橋接的文件風格一致,不是這次新開的落差,不另外列成 finding)。

## 端到端實測記錄(供核對)
- `python3 scripts/test_lumos.py -k dart_sarif`:12/12 通過,含真機 `dart analyze` 端到端。
- `python3 scripts/test_lumos.py -k sarif`:40/40 通過(sqlfluff/stylelint 兩支既有橋接無回歸)。
- `python3 scripts/test_lumos.py -k docs_command_count`:5/5 通過,74 個頂層命令的宣稱在 AGENTS.md / ARCHITECTURE.md / reference.md 三處都跟 `--help` 的 argparse choices 機械對上。
- 自建臨時 Flutter 專案(`.lumos/lint.json` 宣告 `"dart"`,鍵名不帶點):新函式的沒用到變數被新增告警閘正確擋下(`status: blocked`);把 dart 移出 PATH 後正確判 `env-unavailable` 並自動放行記帳,不會誤判成乾淨。這兩條路徑跟文件宣稱完全一致。

## 圖譜固定席逐條判斷
以下節點的 ★INVARIANT★/★RISK★ 宣稱都跟 dart-sarif 這次改動的程式路徑沒有交集,判不影響,理由各一句:
- `Systems/guard-kill.md`(★INVARIANT★,rc 優先序/JSON purity):diff 完全沒有碰 `cmd_guard_kill`/verdict 組字邏輯,只新增獨立的 `cmd_dart_sarif`。
- `Systems/授權與歸屬.md`(★INVARIANT★,LICENSE 白名單/SPDX 檔頭):新程式碼插在既有函式中間,`scripts/lumos` 檔頭與 `_VENDORED_TOOLKIT`/白名單清單一個字都沒變。
- `Systems/lumos-cli-read.md`(★INVARIANT★,search 排除 superseded):與 `cmd_search`/vault 過濾完全無關的另一段程式。
- `Systems/lumos-cli-lifecycle.md`(★INVARIANT★,re-inject 只動 sentinel 之間):AGENTS.md 改的「74 個頂層命令」那行在 `LUMOS:GRAPH-DISCIPLINE:END`(第 67 行)之後,不在 sentinel 保護區間內。
- `Systems/design-loop.md`(★INVARIANT★,處置閘第五步):disposition 判定路徑未被觸及,dart-sarif 只是多一種可宣告的社群 linter 橋接。
- `Systems/pitfalls-code-loop.md`(★RISK★):新增告警閘呼叫 `_lint_new_verdict` 的既有路徑沒變,只是新增一種可被 `.lumos/lint.json` 宣告的指令。
- `Systems/loop-convergence-recording.md`(★RISK★):與 canary/loop 收斂記錄機制無關。
- `Systems/lumos-deinit.md`(★RISK★):`_VENDORED_TOOLKIT`/`_VENDORED_TREE_FILES` 兩張清單本次都沒有新增或刪除任何檔案項目。
- 其餘 11 篇「超出上限只列名」的節點(reversibility-governance-ledger / 節點範圍與索引守衛 / check-r-guard / doctor-irreversible-hint / cochange-guard / check-t-sentinel / lumos-refcheck / bound-tests-gate / canary-audit / slim-get-一行安裝 / slim-install-安裝器 / slim-uninstall-一行卸載 / 測試假綠形態 / core-invariant-baseline / judge-severity-gate):都只是因為「about_code 掛 scripts/lumos」被牽連列出,這次改動不涉及它們各自守的機制(doctor 巡檢項、刪除傳播、bound-tests、canary、安裝腳本等),判不影響。

最高等級為 major(F1:官方文件教的 dart 宣告寫法會讓官方驗收指令 `lumos lint-check --smoke` 現場誤報失敗)。
