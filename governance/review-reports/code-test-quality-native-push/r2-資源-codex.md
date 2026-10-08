severity: major

R2-RES-1：deinit 仍會留下無副檔名主程式的 bytecode，原 b2 只部分修復。  
severity: major  
blocking: 是  
引句:「+    names = {Path(p).stem for p in _VENDORED_TOOLKIT if p.endswith(".py")}」  
清理集合排除了 vendored 的無副檔名 `scripts/lumos`；但 vendored `scripts/test_lumos.py` 會用 `SourceFileLoader` 載入它，實際產生 `scripts/__pycache__/lumoscpython-314.pyc`。deinit 刪掉來源後仍留下該工具 bytecode，違反 `lumos-deinit.md` 所記「完整卸載工具自身 bytecode」的修復目的。  
file: `scripts/lumos:21970`  
file: `scripts/lumos:22144`  
file: `scripts/test_lumos.py:231`  
最小重現：

```text
python3 /tmp/lumos-seat-work/code-test-quality-native-push/r2-resource/probe_deinit_bytecode.py
{'before': ['lumoscpython-314.pyc'], 'removed': ['scripts/lumos'], 'after': ['lumoscpython-314.pyc']}
AssertionError: deinit left bytecode generated from the vendored scripts/lumos entry point
```

R2-RES-2：新增 results 附件排除後，程式改名進該目錄會從角色／棧別分類中整筆消失。  
severity: major  
blocking: 是  
引句:「+_IMPACT_RECORD_DIRS = (*_BOOKKEEPING_DIRS, "governance/eval/results/")」  
`_impact_diff_seed_ok` 已用新集合排除 `governance/eval/results/` 的一般附件，但改名補償仍只判 `_BOOKKEEPING_DIRS`。因此 `service.py` 改名成 `governance/eval/results/run/report.txt` 時，新側被排除、舊側又未補回，`_review_role_changed_files` 回空集合；角色卡及棧別題可能被記成未觸發。這是 r4 修補造成的回歸；基準版仍會保留該改動。  
file: `scripts/lumos:44061`  
file: `scripts/lumos:26518`  
最小重現：

```text
python3 /tmp/lumos-seat-work/code-test-quality-native-push/r2-resource/probe_impact_rename.py
# HEAD: changed=[]，AssertionError，rc1

PROBE_TOOL=/tmp/lumos-seat-work/code-test-quality-native-push/r2-resource/base-5d8/scripts/lumos \
  python3 /tmp/lumos-seat-work/code-test-quality-native-push/r2-resource/probe_impact_rename.py
# base: changed=[('governance/eval/results/run/report.txt', ...)]，rc0
```

R2-RES-3：i2 宣稱移除固定舊數量，但 dry-run 仍顯示「5 檔」。  
severity: minor  
blocking: 否  
引句:「+    """白名單移除 vendored 工具組:① _VENDORED_TOOLKIT 的精確檔名;」  
目前 `_VENDORED_TOOLKIT` 有 8 個精確檔名，`deinit --dry-run` 仍輸出「白名單:5 檔」，與 r1-fix 的 i2 處置不一致；實際刪除仍走白名單，影響是預演資訊失真。  
file: `scripts/lumos:21573`  
file: `scripts/lumos:22144`

```text
lumos deinit --dry-run
移除 vendored 工具組(白名單:5 檔 + hooks/templates 兩夾)
```

鏡頭：process group、SIGTERM、KeyboardInterrupt、timeout、pipe EOF、雙管線與輸出上限。  
已讀,無 finding  
引句:「+        with selectors.DefaultSelector() as selector:」  
`test_test_quality_cli.py` 33 項全綠；另以真子工作者驗 timeout、pipe 先 EOF 後逾時、KeyboardInterrupt，三者皆清掉 process group。stdout/stderr 各 2 MiB 同時輸出可完整收取；30 MiB writer 在完成 marker 前被上限中止。SIGTERM 既有控制亦通過。Windows 路徑依 `test-quality-cli.md` 明定仍未取得資格，本席未把 POSIX 結果外推到 Windows。

鏡頭：fake claude 與模型逾時。  
已讀,無 finding  
引句:「+        proc = model_command(cmd, directory, timeout)」  
`test_model_timeout_stops_worker_without_paid_call` 通過：PATH 明確解析至 fake `claude`，工作者確實啟動後被整組停止，沒有模型付費或外部呼叫。

鏡頭：JUnit 總數、資料及輸出邊界。  
已讀,無 finding  
引句:「+    validate_suite_counts(root)」  
suite/root failure 摘要矛盾均拒收，一致摘要保留正常 capture；來源、receipt、XML 與即時 stdout/stderr 均有 10 MiB 邊界。未發現本修補新增的錯誤接受或無界累積。

鏡頭：歷史 grammar 重構保留。  
已讀,無 finding  
引句:「+        validate_node_access(node, scopes)」  
基準 `5d8f0ec7` 與 HEAD 的 historical controls 案例逐字相同，8 類狀態完全一致；兩版 `test_test_quality_handbook.py` 各 15 項全綠。抽出的 validation、scenario、importer、controls 與 score helper 未見語意漂移。

已讀材料：`r2-runtime.patch` 1128 行、`r2-history.patch` 620 行、`r2-repair-binding.json`、`r1-fix.json`、`r1-intake.md`；並查基準提交與相關 `r1-evidence.patch`／`r1-history.patch`。`r2-repair.patch` SHA-256 與 binding 的 `0dcdc6f2…f988f3a` 相符。

圖譜與固定鏡頭逐條判斷：

- `vendored測試套件在消費端假紅`：新增 `scripts/test_test_quality_cli.py` 不在 vendored 白名單，來源 runner 另有 `_need_src`，未新增消費端假紅。
- `lumos-cli-lifecycle` 的 reinject sentinel 外 byte-equal 合約：本 patch 未碰 reinject 路徑。
- `lumos-deinit`：四重 vault 刪除閘未受影響；工具 bytecode 完整移除與預演敘述分別對應 R2-RES-1、R2-RES-3。
- `lumos-cli-read` 的 superseded/stale search 合約：搜尋路徑未改。
- `bound-tests-gate`：正式 `cmd_impact --diff` 使用 `--no-renames`，刪除舊側仍會成為固定席種子；R2-RES-2 影響角色／棧別分類，未證成 bound-tests 合約本身失效。
- `guard-kill` 的 rc 優先序與 JSON 純度：相關函式未改。
- `授權與歸屬` 兩條合約：白名單沒有 LICENSE/COPYING/NOTICE；`scripts/lumos` 與新增 vendored Python 檔的 SPDX 標示未被本輪破壞。
- `測試假綠形態`：process、輸出與 fake provider 控制都有子程序已進入、marker 或 PATH 身份前置；R2-RES-1 是未涵蓋無副檔名 cache 形態，未發現既有斷言由其他失敗路徑代打。
- 固定鏡頭其餘超出上限節點只核對名稱，未擴大審查範圍。

總結: 最嚴重 severity major；blocking 2 條。
