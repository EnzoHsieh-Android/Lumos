severity: major

**固定席摘要(圖譜鏡頭)**:這次牽連的固定席是 guard-kill 的兩條 INVARIANT(rc 優先序、`--json` 輸出純淨)、bound-tests-gate、lumos-cli-read 等。修補碰到 guard-kill 共用路徑的只有兩處:`_kill_run` 的 docstring,以及 `_kill_measure_singles` 多回第 5 項。後者在合併快篩不給 `after` 時,`spent` 等於 `got[2]`,行為不變。rc 優先序與 JSON 純淨沒有被碰到,判定:這兩條 INVARIANT 未受影響。

**已確認沒有問題**:
- 搬移與改名後,`_CovBase` 在 `scripts/lumos` 已無殘留。
- `_choice_merge_init_write` 改走 `_choice_init_file_write` 後,寫失敗仍回 False、仍印同一行警告並把 `init` 設為 None,行為不變。
- `_kill_signal_marked` 與原本 `_KillMerge.on_signal` 的語意一致。
- `_choice_ledger_status` 抽出 `disp_of` 與 `_choice_reach_fill` 後行為不變。`guard if rng else None` 只在 `rng` 為真時才取值,所以沒有未定義變數的問題。

**finding 1**
severity: major
blocking: 是
`scripts/lumos:29230` 的 `_KillCovBase.cached()`:覆蓋路徑自己做的名稱檢查(`_test_name_ok` 加 `_name_collision_reason`,不合就記「名稱檢查沒過」)沒有任何專屬測試。`scripts/test_lumos.py` 在 149000 行之後找不到「名稱檢查沒過」,只有合併快篩那組測試用過 `b,Case`。這道檢查保護的是「含逗號等特殊字元的名字不進 `--tests` 指令」與「撞名時壞法打紅的可能是別支測試」。
引句:「            if not _test_name_ok(m) or _name_collision_reason(m, self.c.pentry, self.c.pentry["root"], self.c.coll_cache):」
重現:在複製的 repo 把這個條件改成 `if False:`,跑 `python3.14 scripts/test_lumos.py -k choice_cov`,結果 66 passed, 0 failed,全綠。

**finding 2**
severity: major
blocking: 是
`scripts/lumos:80193` 的 `_choice_cov_prune` 呼叫(續跑快取只留最近 2 個 at_sha)沒有測試。上輪的 F14 修了這個清除,但沒有專屬測試,`_CHOICE_COV_KEEP` 也沒有任何測試引用。
引句:「    _choice_cov_prune(rr, at_sha)   # 續跑快取只留最近幾個 at_sha:每次 choice-kill 開頭清,不論開不開覆蓋」
重現:把這行註解掉,跑 `-k choice_cov`,結果 66 passed, 0 failed,全綠。後果是 `choice-cov/` 無限增長。

**finding 3**
severity: major
blocking: 是
`_KillPrep._analyze` 的時間門(剩下的時間不夠「逾時加一個壞法的預估」就不做,記「時間不夠」)沒有測試。上輪的 F6 加了這道門,新增的 `t_choice_cov_*` 沒有一支讓它觸發。
引句:「        if self.remaining() < cap + (sum(els) / len(els) if els else _CHOICE_MERGE_UNIT_SECS):」
重現:把整段 `if` 改成 `if False:`,跑 `-k choice_cov`,結果 66 passed, 0 failed,全綠。

**finding 4**
severity: minor
blocking: 否
`t_choice_cov_init_scripts` 用字串包含來測分析腳本(`"dependsOn" in ana`、`"noclasses" in ana`)。把 `dependsOn(...)` 裡的任務名單改錯,例如 `compile${v}Kotlin` 打成 `compile${v}Kotlinn`,這個測試仍然綠。假 Gradle 也不執行初始化腳本,所以「分析前先編譯」這條上輪 F4 的修法沒有一條真正執行到它的測試。這項我沒有實際跑過,是依測試寫法推論。
引句:「          all(k in ana for k in ("CoverageBuilder", "Analyzer", "ExecFileLoader", "jacocoAnt", "dependsOn", "lumosCovVariant", "noclasses")), ana[:400])」

**finding 5**
severity: minor
blocking: 否
`scripts/lumos`(`_KillCovBase.store`)寫 `dst + ".tmp"` 後 `os.replace`,中途 `OSError` 時 `.tmp` 檔不清。續跑快取資料夾裡可能殘留 `.tmp`,雖然會被 prune 一起清掉,但同一個 at_sha 內不會。影響小。
引句:「            with open(dst + ".tmp", "wb") as fh:」

總結:最高等級是 major(finding 1 到 3,名稱檢查、清快取、分析時間門三處都能改壞而測試全綠)。

我另外讀的各條路徑與抽出的 helper(`_kill_measure_singles` 的 `spent`、`red_rerun`、`_choice_cov_sha` 回 None 與 `_choice_kill_pick` 的處理、`_choice_reach_cur` 的時限)沒有找到會做出錯行為的洞。三個翻紅實驗用的臨時目錄已用字面絕對路徑刪除。
