severity: blocker

F1
severity: blocker
blocking: 是
引句:「不算 `@@` 行號、上下文行、`index` 那行——rebase 只會改到那些,改動本身沒變就還算同一版。」

`_patch_file_changes`(scripts/lumos:14892 起)把 `index <old>..<new>` 這一行——git 二進位 diff 裡唯一帶內容雜湊的地方——排除在指紋之外,而二進位檔的實際差異只出現在該行。我用兩份手造的二進位 diff(同檔名、`index aaaaaaa..bbbbbbb` vs `index ccccccc..ddddddd`,內容完全不同)餵給實際的 `_patch_file_changes`,兩次算出**同一個** sha256(`3091d254...`)。接着做了全流程重現:資安席在 r1 只看過 `index aaaaaaa..bbbbbbb` 那版 `asset.bin`,判定輪 r2 把它換成內容完全不同的 `index ccccccc..ddddddd`(模擬惡意置換二進位檔),跑 `lumos loop status --disposal` 結果是:
```
[disposal] 資安席: ✓ — r1 資安-sonnet(看過的檔涵蓋最後一版 1 個)
✅ DISPOSAL GATE PASS ... rc=0
```
處置閘「資安席看過的檔涵蓋最後一版」這條核心保證,對任何二進位檔改動完全失效——只要 git 印出的是預設無 `--binary` 的 `Binary files a/X and b/X differ`(本 repo 及一般 `git diff` 皆如此),資-安席審過舊版二進位檔後,判定輪把它換成任意不同內容的二進位檔,問閘照樣判「涵蓋」放行。這正是這一整支功能存在的理由(防止「同一支檔換成含後門的內容照樣算資安席看過」),而它對二進位檔這個類別完全沒擋住。

F2
severity: major
blocking: 是
引句:「if v.get("not_run"):」

`cmd_bound_tests` 的 `if st == "red":`(scripts/lumos:22639 起)分支只印 `v["red"]` 清單與固定文字,從不讀 `v["reason"]` 或 `v.get("not_run")`;而「另有 N 支沒跑——平台 X 沒設測試指令」這段只在 diff 加的 `if st in ("green",):` 分支(上面引的那行)裡印。我用診斷閘測試 ③ 的同一種 fixture(py 平台有指令但綁定懸空、other 平台無 run_cmd)實際跑了三種呼叫並附完整輸出:
- `lumos bound-tests --diff HEAD~1..HEAD`(純文字):只印 `t_ghost` 懸空紅,完全不提 `other`/`t_x`/「沒設測試指令」。
- `lumos bound-tests --diff HEAD~1..HEAD --advisory`(低風險 pre-push 實際會走的那條路,`lumos-code-loop/SKILL.md` 步驟 4 寫明):同樣只印懸空紅,隻字不提另一平台沒跑。
- 對照 `lumos code-loop check --diff HEAD~1..HEAD`(純文字):正確印出「另有 1 支沒跑——平台 other 沒設測試指令…」。
`--json` 模式下 `reason`/`not_run` 兩個欄位都在(我也印出來核對過),所以底層資料是對的,純粹是 `cmd_bound_tests` 的人讀輸出在「red」分支漏接。這與本次改動自己的設計目標(「訊息點名平台」「零覆蓋不再靜默」)直接矛盾,而且 `t_bound_tests_multiplatform_missing_cmd` 這支新測試裡對應的懸空紅場景(③)只驗了 `--json`,沒有任何測試驗純文字/`--advisory` 輸出,所以這個漏洞沒被目前的測試檔案抓到。

LUMOS-IMPACT: 1f28cd6b..HEAD 判讀
- canary-record未落盤事件.md:不影響——本次 diff 沒有碰 `canary record`/`second` 的寫入或 readback 邏輯,只重用既有 `_prov_check` 做既有 sha 重驗(讀側,未改語意)。
- design-loop.md(處置閘第五步 ★INVARIANT★):不影響——第五步「條款綁定」`_disposal_clause_step` 本體未改,本次只在它之後加第六步「資安席」,呼叫順序與既有條件(生效日、審材類型)未變,測試 `t_disposal_security_seat_cutoff` 也驗過設計審迴圈仍走 `_disposal_clause_step` 邏輯不受影響。
- bound-tests-gate.md(紅/懸空/不可信→blocked=True rc1;沒指令→不擋 ★INVARIANT★):rc/blocked 判定本身沒被破壞——我復現的 F2 只是訊息遺漏,`bt["status"] in ("red","unfilterable")` 那條擋人邏輯完全沒動,懸空紅照樣觸發 blocked;`no-config`(全部沒指令)仍是不擋的路徑,`t_bound_tests_multiplatform_missing_cmd` 全數綠燈也驗到這點。
- canary-audit.md(record/second 持久化與 telemetry-only ★INVARIANT★):不影響——本次沒碰 record/second 指令本體。
- guard-kill.md(rc 優先序、--json 純度 ★INVARIANT★):不影響——`cmd_guard_kill` 唯一改動是把內嵌 JSON 讀取換成 `_config_has_top_run_cmd()`,行為等價(同樣 try/except 吞例外回 False),`file=(sys.stderr if as_json else sys.stdout)` 這行完全沒動,JSON 純度與 rc 優先序邏輯都未觸及。
- slim-get/slim-install/slim-uninstall 全部 ★INVARIANT★:不影響——本次 diff 完全沒碰安裝器/CLAUDE.md 注入/manifest 相關程式碼,列出來只是因為 `scripts/lumos`、`scripts/test_lumos.py` 是共用大檔。

總結:最嚴重 severity 是 blocker(F1);blocking 共 2 條(F1、F2)。
