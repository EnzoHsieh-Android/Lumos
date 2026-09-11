severity: minor

F1
severity: minor
blocking: 否
引句:「另外 {len(v['not_run'])} 支沒跑——{v['reason'].split('——', 1)[-1]}」
file: `scripts/lumos:22668`
`cmd_bound_tests` 紅燈分支用 `v['reason'].split('——', 1)[-1]` 想抓出「沒跑的平台」那句說明,但 `red[:6]` 裡任一支紅測試的 `d`
欄位是 `f"rc={rc} {tail[-120:].strip()}"`(見 `scripts/lumos:22381`,拼進 `reason` 的位置早於 `_nc_note`)——只要那支失敗測試自己輸出的尾
120 字元裡含有「——」(本專案 `check()`/print 訊息全篇慣用這個分隔符,同一支跑在自己 repo 的合約測試失敗時輸出很可能就帶),
`split('——', 1)[-1]` 抓到的就是「該測試輸出裡『——』後面那段」而不是 `_nc_note` 的平台說明,印出來的訊息會把失敗測試的部分輸出當成
「沒跑的平台原因」秀給人看、並重複一次「另外/另有 N 支沒跑」字樣。已用等價字串重現(見下),不影響擋/放行的 rc,純粹是訊息內容出錯:
```
reason = "受波及合約的測試沒過:t_x [t_x] rc=1 assertion 沒過——期望是 true 實際是 false"
         ";另有 1 支沒跑——平台 android 沒設測試指令(...),這些平台受波及的合約測試沒有跑"
reason.split('——', 1)[-1]
=> "期望是 true 實際是 false;另有 1 支沒跑——平台 android 沒設測試指令(...),這些平台受波及的合約測試沒有跑"
```
`st in ("green",)` 分支(`scripts/lumos` 同一函式稍下方)用同一招,但綠燈時 `reason` 不含測試輸出尾巴,不會踩到;`unfilterable`
分支直接印整段 `v['reason']`(不做 split),也不受影響——只有紅燈分支有這個縫。

LUMOS-IMPACT: 1f28cd6b..HEAD
- Systems/design-loop.md(★INVARIANT★ 處置閘第五步・條款綁定):本輪 delta 沒有碰 `_disposal_clause_step`;新增的「資安席」是獨立的第
  六步函式 `_disposal_security_step`,跟第五步邏輯互不相干。不影響。
- Systems/bound-tests-gate.md(★INVARIANT★ 合約綁測試逐支真跑,紅/懸空/偽證據/證不出跑過→blocked;沒 run_cmd/無固定席/沒綁→不擋但
  寫帳):本輪把「有平台沒 run_cmd」從「整批 no-config、有 run_cmd 的平台也不跑」改成逐平台判——有 run_cmd 的平台仍照樣真跑、紅照樣
  擋,沒 run_cmd 的那幾支才記成「沒跑」不擋;新測 `t_bound_tests_multiplatform_missing_cmd` 已驗過紅燈仍擋、懸空仍紅、單平台無指令
  仍走舊的 no-config 路徑。這是把「同一條不變量」實作得更精準(以前一個平台漏配就會連帶讓其他平台的真紅測試也不跑),不是破壞它。
- Systems/canary-audit.md、Systems/guard-kill.md:本輪完全沒碰 canary record/second 的落盤與 rc 邏輯、也沒碰 `cmd_guard_kill`;
  `_disposal_security_step` 只是印出一條建議使用者事後執行的 `canary record none` 指令(且已補上 shlex 引號),不觸碰 record 本身
  的實作。不影響。
- Systems/slim-get-一行安裝.md、Systems/slim-install-安裝器.md、Systems/slim-uninstall-一行卸載.md、Systems/授權與歸屬.md:本輪
  對 `_sync_global_hooks`/`_install_codex_agent`/`enforcement_status` 的改動只是把三席的模型常數(terra/astra)換成共用的
  `_CODEX_SEAT_MODEL`("gpt-5.6-sol"),印出的人讀訊息字串跟著換;沒有動到 `.ps1` 內容、CLAUDE.md sentinel 注入/還原、manifest 寫入
  與清除、Windows shim 偵測、或 `_VENDORED_TOOLKIT`/SPDX 白名單的任何一行邏輯。d6 三席/teardown 測試本輪仍全綠。不影響。

以上為本輪(r3 delta)逐 hunk 核對後的唯一發現。二進位檔指紋修法(F1/代碼審 r2 通才,取 index post-blob + GIT binary patch 資料行)
已用真實 git 產生的多組情境(單純內容變更、新增、刪除、rename+小改、pure rename、`--binary` 完整 binary patch 格式)實測驗證——不同
內容一律得到不同指紋、rebase 型的 index/行號差異一律得到相同指紋,未發現繞過方式;隨附的新單元測試 `t_patch_fingerprint_binary_and_
quoting`、`t_bound_tests_multiplatform_missing_cmd`、`t_codex_d6_agent_toml`、`t_disposal_security*` 全數執行過,皆綠。shlex 引號
修法(G3)經 `_disposal_security_step` 直接呼叫驗證,對含分號的迴圈編號正確加上單引號。

總結:全份最高 severity 為 minor,blocking 條數 0(F1 為 minor/不擋)。
