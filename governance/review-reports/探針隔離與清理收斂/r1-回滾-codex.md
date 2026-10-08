severity: major
審材：governance/review-reports/探針隔離與清理收斂/r1-snapshot.md

前言、PRIOR-ART、RETIRE-IF、根因與取捨、驗收條款、先紅後綠與邊界、實務隱患：已讀，無 finding。

severity: major
blocking: 是
引句:「回退本案實作時保留 r4 原始卷證與新反例，恢復原案未放行狀態；不能把舊共用副本測得的分數當新判準證據。」
回退章節只禁止混用舊分數，沒有要求替新的「逐次副本」量測制度建立版本邊界。現行歷史與 JSON 輸出只寫 `GRADER_VERSION`；它目前識別讀碼判準，沒有沙盒／儀器版本或執行提交。照 spec 實作後若先產生成績、再撤回，新制、撤回後舊制及先前共用副本的紀錄仍會同標為 `2026-10-03-source-results`，事後無法機械辨識哪些分數可比較；這也使「不能把舊共用副本測得的分數當新判準證據」無法執行。應新增獨立且持久的儀器版本或提交識別，寫入 `--out` 與 history，並把「改版、撤回各產生不同標記，舊列不改寫」列成驗收條款。file: `scripts/scenario_probe.py:89`、file: `scripts/scenario_probe.py:820`、file: `scripts/scenario_probe.py:981`。
最小重現：以相同 summary、不同 ts 各呼叫一次 `history_record` 代表改版前後；現行輸出除了 ts 完全相同，皆只有 `grader=2026-10-03-source-results`，撤回後無欄位可辨識分版。

審計修正紀錄：已讀，無 finding。

總結：最嚴重 severity major，blocking 1 條。
