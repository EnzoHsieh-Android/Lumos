severity: major

B1
severity: major
blocking: 是
引句:「既有的 _delguard_parse_diff 只用「 b/(.+)$」抓、不處理引號,所以不能直接拿來用。」
file: `scripts/lumos:3978` 與 `scripts/lumos:18124-18128`、`scripts/lumos:20687-20688`、`scripts/lumos:20716`、`scripts/lumos:20856`、`scripts/lumos:17746`、`scripts/lumos:17889` ——這 8 處都是同一招:呼叫 git 時帶 `-c core.quotePath=false`,讓 CJK 檔名從源頭就不被轉成八進位跳脫的引號字串,其中 18124 行的註解原文是「core.quotePath=false:CJK 檔名不轉義加引號(否則 "+++ b/" 前綴比對全失效…),同 test-layers/impact-diff 先例」——專案自己稱之為「先例」。這份 diff 新增的 `_git_unquote_path`(`scripts/lumos:14869-14879`)反其道而行:讓 patch 先被印成加引號的八進位跳脫格式,再用 `codecs.escape_decode` 手刻一支反解碼器把它還原,是全 repo唯一一處用這個技巧處理 CJK 路徑的地方。真正一致的做法是在 `skills/lumos-code-loop/SKILL.md`「凍結材料」那行($`git diff <merge-base>..HEAD -U10 > …patch`$,此 diff 未改動這行)加上 `-c core.quotePath=false`,讓落盤的凍結 patch 本來就不帶引號,`_patch_files_from_text` 就不需要這支獨立的反解碼路徑。我實際跑了這份新函式(見下)確認它本身邏輯是對的(CJK、反斜線、tab、emoji、mode-only diff 全部過),所以這不是功能缺陷,而是引入了跟專案既有「另一套路徑還原」明確衝突的第二種做法——未能重現成翻紅測試(因為它本身沒 bug),故只以架構鏡頭判 major,不當作功能 blocker。

LUMOS-IMPACT 逐條(b4926d9c..HEAD)：

- Issues/canary-record未落盤事件.md [事故]:不影響。這份 diff 沒有改 `canary record` 的寫入/落盤路徑,新增的 `_prov_check`/`_disposal_security_step` 只是「讀」既有帳本欄位(report/snapshot sha256),寫入端行為原樣。
- Systems/design-loop.md ★INVARIANT★(處置閘第五步條款綁定,`.md` 計劃才驗、`code-` 開頭一律 skip):不影響。新增的第六步「資安席」只加在 `_disposal_clause_step` 之後(`scripts/lumos:15398-15406`),不改它的判斷邏輯與 skip 條件,兩步各自獨立回 fail/ok/skip。
- Systems/bound-tests-gate.md ★INVARIANT★(紅/懸空/偽證據/★unfilterable★→擋,算不出→不擋只記帳):不影響、且更貼合這條合約。舊版一個平台沒指令就整批 `return None, "no-config"`,會把另一個平台上本來會判「紅」的懸空/偽證據測試一起吞成「不擋」;新版讓有指令的平台照跑,懸空/偽證據照樣進「紅」擋(t_bound_tests_multiplatform_missing_cmd 的 ③ 已驗證,實測通過)。
- Systems/canary-audit.md ★INVARIANT★(record/second 落盤才算成功、second 不影響 rc):不影響,這份 diff 沒有改 `canary record`/`second` 的落盤或 rc 判斷。
- Systems/guard-kill.md ★INVARIANT★(rc 優先序;--json 模式 stdout 純度):不影響。`cmd_guard_kill` 那段改動只是把原本內嵌的 `json.loads` 換成呼叫 `_config_has_top_run_cmd`,`file=(sys.stderr if as_json else sys.stdout)` 這行印出邏輯完全沒動,--json 時警告仍走 stderr。
- slim-get/slim-install/slim-uninstall(共 15 條 ★INVARIANT★):不影響,這份 diff 完全沒有碰安裝器/CLAUDE.md 注入/manifest/卸載相關的任何函式,牽連檔只是因為同屬 `scripts/lumos` 這支大檔案而被列入,實際 hunk 都在 loop/disposal/roster/bound-tests 這幾段。
- 其餘「超出上限,只列名」的固定席(授權與歸屬、測試假綠形態、lumos-cli-read/lifecycle、pitfalls-code-loop、loop-convergence-recording、節點範圍與索引守衛、lumos-deinit、reversibility-governance-ledger、check-r-guard、core-invariant-baseline、cochange-guard、doctor-irreversible-hint、check-t-sentinel、judge-severity-gate、lumos-refcheck):逐一核對過diff 全文後皆不影響——這份 diff 沒有觸及 doctor 檢查、refcheck、co-change 守衛、可逆性帳本或授權機制的任何程式碼。

總結:最嚴重 severity 是 major(B1:凍結 patch 檔名解析走了跟專案既有「呼叫 git 時用 `-c core.quotePath=false` 避開 CJK 引號跳脫」明顯不同的第二條路,自己手刻八進位反解碼器),blocking 共 1 條。
