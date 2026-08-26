### ext-f1
severity: blocker
引句:「觸發=審查席帳列(loop+auditor;結局帳 --outcome 除外)。★不要求 round★——light/循序」
佐證:file: `scripts/lumos:4020`
說明:未解。`--outcome` 可與 `--findings-set`、`--folded-set` 等處置旗標同時使用；參數層沒有互斥。只要補一個合法 `--outcome converged`，`outcome is None` 即為假，整段報告必附及嚴重度對帳守衛便被跳過。處置帳雖已綁 round 與 auditor，仍可用假冒結局欄低報 severity，重現原 blocker 的核心危害。

### ext-f2
severity: clean
引句:「engine_rev 不同=過期,但只跳過「重算」;帳被動/檔被動的完整性檢查照跑」
佐證:file: `scripts/lumos:603`
說明:已解。repo 內已提交 golden 會先與 HEAD blob 比對，工作樹竄改列紅並回傳 rc1；尚未提交的 golden 只提醒。即使 `engine_rev` 過期，也只略過判定重算，帳列集合與凍結卷證完整性仍會檢查，不能再靠改版本欄位提早返回。repo 外或未追蹤副本屬明示的未受版控保護提醒範圍，沒有冒充成已受保護。

### ext-f3
severity: clean
引句:「seen 只記「真的回放過的」新包——預算見底被 skip 的新包保留必跑資格。」
佐證:file: `governance/autonomous_loop/replay_weekly.py:147`
說明:已解。新包只有實際進入 `out["replayed"]` 才寫入 seen；預算不足而 skip、執行前逾時或未開始的包都保留新包資格。升級全量分支中的 `sample + rest` 不會重新傷到新包，因為所有 new 已在 base，rest 只可能是既有 seen 的存量包；done 也另以 replayed 交集推進。

結論:否決維持(--outcome 可偽裝處置帳，繞過寫側嚴重度守衛，ext-f1 blocker 未解)。
