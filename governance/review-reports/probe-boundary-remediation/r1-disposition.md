severity: blocker

編排者處置彙總，非獨立審查席。這九條由四份獨立席報告的十條去重而來；M1與C3是同一混合題序問題。原始席位與重現細節見 r1-intake.md 和各席報告。審材：`r1-snapshot.patch`。

C1 巢狀 bare Git
severity: blocker
blocking: true
引句:「副本不接受另一套Git資料或指到副本外的工作樹連結。」
file: `scripts/scenario_probe.py:535`
臨時外層 repo 含 bare nested.git，副本仍接受且它自身 remote 可向外推；折入 bare 形狀前置拒絕及紅綠測試。

C2 假身分遺失
severity: major
blocking: true
引句:「只保留 Git 歷史所需的檔案格式欄位、設定副本專用 hooksPath、假身分」
file: `scripts/scenario_probe.py:580`
白名單重建漏 user.*，模型提交回落本機身分；折入副本設定假身分及紅綠測試。

C3 最後普通題未保留
severity: major
blocking: true
引句:「讀碼標記的現場永不保留；普通題只保留最後一場通過隔離驗收的副本。」
file: `scripts/scenario_probe.py:1042`
普通題後接讀碼題時 keep 留零份；量測席 M1 同報，折入逐場保留策略及混合題測試。

B1 大小寫變體
severity: blocker
blocking: true
引句:「if name == ".git" or name == ".gitmodules":」
file: `scripts/scenario_probe.py:549`
macOS 上 .GIT 巢狀倉庫漏過；折入大小寫折疊拒絕及紅綠測試。

B2 Git trace 寫來源
severity: major
blocking: true
引句:「remote = subprocess.run(["git", "remote"], cwd=str(work), env=genv,」
file: `scripts/scenario_probe.py:593`
父環境 GIT_TRACE 指來源檔，儀器自己的 Git 呼叫追加內容；折入環境清洗及 byte-equal 測試。

M2 重試逐場時間遺失
severity: major
blocking: true
引句:「if res.get("limit_hit") and waited < a.wait_on_limit:」
file: `scripts/scenario_probe.py:1075`
限額後重試只留下成功那次的逐場時間；折入 retry_attempts 結構與時間測試。

M3 故障注入漏清臨時副本
severity: minor
blocking: false
引句:「raise mod.SourceProbeCleanupError("forced cleanup failure")」
file: `scripts/test_lumos.py:37280`
測試故意跳過刪除卻未補清理；折入測試結尾實際清理。

A1 清理函式命名過窄
severity: minor
blocking: false
引句:「讀碼標記的現場永不保留；普通題只保留最後一場通過隔離驗收的副本。」
file: `scripts/scenario_probe.py:1052`
普通題及基線已共用清理，舊名仍限 source；折入通用名稱。

A2 雙套嘗試生命週期
severity: major
blocking: true
引句:「baseline 已套用 arm；每場從它複製，不能讓前場或來源的後續修改滲入。」
file: `scripts/scenario_probe.py:1018`
舊 _run_source_attempt 無生產呼叫，main 另有實作；刪舊 helper，直接測試改走正式 main 或真實副本路徑。
