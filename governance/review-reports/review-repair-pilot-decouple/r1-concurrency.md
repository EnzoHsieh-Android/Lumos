severity: blocker

### Frontmatter、導言、PRIOR-ART、RETIRE-IF

已讀無 finding。

### 範圍與條款

finding F1  
severity: major  
blocking: 是  
引句:「編排者應於開工前在候選表領試行序號，首輪 intake 再記同一序號與 loop id」  
具體錯誤行為：試行序號表與候選事件表是兩張分離的 Markdown 表；候選事件表甚至沒有「序號」欄。計劃也未規定兩張表必須以一次原子覆寫共同提交。寫入途中崩潰可留下「第 2 格已占但沒有候選事件」，或「已有合格候選事件但第 2 格仍待登記」。後續協調者沒有權威規則判斷該重用還是跳過序號，會重號、漏號或改變前四個樣本。

重現步驟：

1. 取得 `coord-lock`。
2. 只把五格登記表的第 2 格改成工作 A，尚未追加候選事件時終止程序；反向順序也可重現。
3. 重新接手後，兩張表對「第 2 格是否已消耗」給出不同答案。
4. 執行 `lumos loop next` 不會發現或修復矛盾；它只讀 `.canary-log.jsonl`。

file: `scripts/lumos:11138`  
file: `scripts/lumos:11147`

### 2026-10-04 收斂性診斷與下次試行的最小調整

已讀無 finding。

### 落點

finding F2  
severity: major  
blocking: 是  
引句:「入口與細則放入代碼審 skill 及其 reference；決策脈絡歸 Systems/pitfalls-code-loop」  
具體錯誤行為：工作樹內的 skill 已有試行入口，但本機 Codex 實際載入的 user-scope skill 仍指向 `/Users/enzo/harness/lumos-toolchain` 的舊版，沒有五次試行入口；其 reference 也直接從測試規則跳到記帳章節。計劃卻只以設計 PASS、快照 hash 與生效時間作第 2 案啟用條件，沒有要求先把正確 checkout 安裝到 user-scope。新會談因此可能完全看不到候選表、短鎖與唯一協調者規則，直接開始普通 code-loop，使人工互斥失效。回退同樣缺少同步已安裝 skill 的步驟。

重現步驟：

1. 執行 `readlink ~/.agents/skills/lumos-code-loop`，可見它指向 harness checkout。
2. 對工作樹與已安裝版本分別執行 `rg -n '五次修復試行' .../SKILL.md`。
3. 工作樹版本命中，已安裝版本不命中。
4. 不重新安裝 skill，只完成設計 PASS 與生效驗證後開新 Codex 會談；它不會由 skill 被導向候選表。

file: `skills/lumos-code-loop/SKILL.md:16`  
file: `/Users/enzo/.agents/skills/lumos-code-loop/SKILL.md:14`  
file: `skills/lumos-code-loop/reference.md:122`  
file: `/Users/enzo/.agents/skills/lumos-code-loop/reference.md:122`  
file: `install.sh:3`

### 試行登記與回顧入口

finding F3  
severity: blocker  
blocking: 是  
引句:「鎖殘留時不憑時間自動搶占，先查明原會談停止、記交接事件，再人工清鎖。」  
具體錯誤行為：這個恢復順序無法按字面完成。候選登記與交接都必須先取得同一個 `mkdir` 鎖；鎖殘留時，新會談卻被要求先記交接事件、再清鎖。新會談既不能重新 `mkdir`，也不能在未取得鎖時合法記交接。更早的崩潰——成功 `mkdir`、尚未寫 active 協調者——還會留下沒有 owner、會談 ID或操作階段的空目錄，無從查明是哪個會談持有。結果只能永久停住，或違反規則先刪鎖並冒著搶走仍存活持有者的風險。

重現步驟：

1. 會談 A 執行 `mkdir governance/review-reports/review-repair-pilot/coord-lock`。
2. 在寫入候選表及 active 協調者前終止 A。
3. 會談 B 再執行同一個 `mkdir`，得到已存在錯誤。
4. B 若先寫交接，違反「交接前先取得短鎖」；若先刪鎖，違反「記交接事件，再人工清鎖」。
5. 鎖目錄本身沒有 owner 資料，B 也無法由檔案確認 A 是否真的停止。

file: `scripts/lumos:36995`  
file: `scripts/lumos:37031`

finding F4  
severity: major  
blocking: 是  
引句:「同一秒以持短鎖寫入的候選表先後順序裁。」  
具體錯誤行為：互斥只保證兩個寫入者不在同一瞬間持鎖，沒有定義候選表必須 append-only、插入方向或單調事件序號。因此最終列序不必等於鎖取得順序；同秒事件的唯一裁定依據可被正常編輯操作反轉。實際 CLI 對 `.canary-log.jsonl` 特別使用實體 append 序而不按秒級時間排序，但候選表沒有接上同等語意。

重現步驟：

1. A、B 在同一秒嘗試領號。
2. A 先取得鎖，把候選 A 插在表頭下方，釋放。
3. B 隨後取得鎖，也把候選 B 插在表頭下方，釋放。
4. 最終表序是 B、A，但實際鎖取得順序是 A、B；依計劃裁定會把第 2 案給錯工作。
5. 若另一編排者選擇尾端追加，結果又不同，顯示計劃沒有唯一事件順序。

file: `scripts/lumos:10348`  
file: `scripts/lumos:15825`

### 2026-10-04 改道：第2至5案量代碼審，不等探針

finding F5  
severity: major  
blocking: 是  
引句:「新工作的程式、測試與完整 code-loop 審材須置於另一個獨立乾淨 worktree」  
具體錯誤行為：計劃只要求把路徑與基準提交寫進表，沒有規定在領號、首派及每輪凍結時執行哪些檢查，也沒有把該路徑、HEAD、乾淨狀態或差異範圍綁進治理帳。實際 `loop next/status` 只接受一般 `--repo` 與 `--spec`，不讀候選表，也不比對登記的 worktree／基準。編排者可以登記乾淨 worktree A，實際在髒的 aspidochelone 或另一個 HEAD 上製作快照與跑測試，現有 CLI 不會拒絕；試行樣本因此可混入明文排除的探針草稿。

重現步驟：

1. 在候選表記錄乾淨 worktree A 與其基準提交。
2. 留在目前髒工作樹 B，以 B 的差異建立審查快照。
3. 從 B 執行 `python3 scripts/lumos loop next <id> --tier ... --spec ... --repo .`，再依正常流程記帳與問閘。
4. CLI 不會拿候選表中的 A、基準提交或乾淨狀態與 B 比對；只要報告、hash 與 canary 帳一致，這項隔離違規不會成為閘條件。

file: `scripts/lumos:37031`  
file: `scripts/lumos:37039`  
file: `scripts/lumos:10390`  
file: `scripts/lumos:11147`

### 實務隱患

已讀無 finding。

### 回退

已讀無新增 finding；已安裝 skill 的回退同步缺口已併入 F2。

### 審計修正紀錄

已讀無 finding。

### 第1案逐案紀錄

已讀無 finding。

### 第1案例外續修授權

已讀無 finding。

最高嚴重度: blocker；blocking 總數: 5