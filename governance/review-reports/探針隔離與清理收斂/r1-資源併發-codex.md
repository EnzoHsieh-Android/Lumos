severity: blocker
審材：governance/review-reports/探針隔離與清理收斂/r1-snapshot.md

## 開場與 PRIOR-ART／RETIRE-IF

severity: major
blocking: 是
引句:「連續四週量到逐次複製成本超過模型執行總耗時的兩成」
finding: 退場條件需要副本建立／模型耗時資料，但驗收、JSON、歷史都沒要求記建立或清理耗時；現有結果只記模型秒數。四週後仍算不出門檻。file: `scripts/scenario_probe.py:683`、file: `scripts/scenario_probe.py:777`、file: `scripts/scenario_probe.py:981`。

## 根因與取捨

severity: blocker
blocking: 是
引句:「所有題目及重試改用各自副本，跑完在 `finally` 刪除」
finding: 若逐次直接從仍可編輯的來源重複複製，批次失去固定基線；同題兩次重試可讀到不同版本，卻被當模型隨機性。現行主流程先建立一次共用快照。最小重現：`--runs 2` 時第一場期間改來源 CLAUDE.md，第二場複製不同內容。file: `scripts/scenario_probe.py:905`、file: `scripts/scenario_probe.py:921`。

severity: blocker
blocking: 是
引句:「探針應讓各次得到不同乾淨副本；前一次修改提交、索引、Git 設定與未追蹤檔後，下一次看不到污染」
finding: repo 副本彼此獨立，但 Claude runner 仍共用真 HOME、skills、hooks；平行程序改全域狀態後，批末健康檢查之前，別的場次可能已繼續評分。file: `scripts/scenario_probe.py:726`、file: `scripts/scenario_probe.py:951`。最小重現：並行探針 A 改 ~/.claude/skills，B 的後續題在健康檢查前用到污染 skills。

## 驗收條款

severity: major
blocking: 是
引句:「跑完在 `finally` 刪除；不再靠共用副本的 `checkout`/`clean` 回復」
finding: `--timeout` 目前只包模型程序，rsync 和 rmtree 無截止時間；掛住的檔案系統使流程到不了 rc3。file: `scripts/scenario_probe.py:538`、file: `scripts/scenario_probe.py:905`、file: `scripts/scenario_probe.py:658`、file: `scripts/scenario_probe.py:736`。最小重現：PATH 中 rsync 替身停 30 秒、`--timeout 1`，一秒後仍無結果。

severity: major
blocking: 是
引句:「`--keep` 明確保留每次副本並印其路徑，僅供本機診斷」
finding: `--keep` 由保留一份變成題數×runs份完整 repo，無副本數或空間提示。最小重現：2 GiB repo、10題×3runs×4程序，可留約240 GiB，磁碟耗盡時先前副本不回收。file: `scripts/scenario_probe.py:538`。

## 先紅後綠、實務隱患、回退、審計修正紀錄

已讀，無額外 finding。

總結：最嚴重 severity blocker；blocking 5 條。
