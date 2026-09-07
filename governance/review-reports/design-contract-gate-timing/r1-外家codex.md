severity: major  
blocking:是  
引句:「把呼叫搬到風險分級之外(每次推送都跑)」  
位置:[計劃:30](/Users/enzo/harness/lumos-toolchain/docs/lumos-toolchain-knowledge/Projects/合約測試閘什麼時候跑_計劃.md:30)、[lumos:18766](/Users/enzo/harness/lumos-toolchain/scripts/lumos:18766)

`_bound_tests_check` 對 `EMPTY_TREE..sha` 有明確特判，直接記 `diff-unavailable`、ran=0 並放行。這不是推測；治理帳今天也已有 `bound-tests/diff-unavailable` 實例。單純把呼叫搬出去，首推仍完全不跑合約測試，和計劃及既有 ★INVARIANT★ 的「每次推送」衝突。

真檔引句:「新分支首推無 merge-base,受波及範圍不可算」  
位置:[lumos:18767](/Users/enzo/harness/lumos-toolchain/scripts/lumos:18767)

3. 「沒東西可跑時秒級返回」不成立；impact 成本明顯隨 diff 擴大。  
severity: minor  
blocking:否  
引句:「沒有綁定測試時它本來就會自己記一筆『沒東西可跑』的帳、秒級返回。」  
位置:[計劃:32](/Users/enzo/harness/lumos-toolchain/docs/lumos-toolchain-knowledge/Projects/合約測試閘什麼時候跑_計劃.md:32)、[lumos:18671](/Users/enzo/harness/lumos-toolchain/scripts/lumos:18671)

實測：

- 小範圍 `60b5f31^..60b5f31`：6 檔、110 行異動，三次分別 3.27、3.28、3.28 秒。
- 大範圍 `EMPTY_TREE..HEAD`：2336 檔、394,917 行；跑到 208.31 秒仍未完成，人工中止。
- 原因是判定 `no-pins/no-bound` 前，必須先完整執行 `cmd_impact_diff`。

因此只能說「找不到測試後不再支付測試執行成本」，不能宣稱整支 check 秒返。低風險延遲量測也不能只量測試的 28 秒，必須把 impact 成本納入，尤其是大推送與首推策略。

4. `pitfalls 少跑一次` 不是所有路徑都能省，只對 high 路徑成立。  
severity: minor  
blocking:否  
引句:「風險分級改讀這支的輸出,`pitfalls` 因此少跑一次。」  
位置:[計劃:33](/Users/enzo/harness/lumos-toolchain/docs/lumos-toolchain-knowledge/Projects/合約測試閘什麼時候跑_計劃.md:33)、[pre-push:141](/Users/enzo/harness/lumos-toolchain/scripts/hooks/pre-push:141)、[lumos:18830](/Users/enzo/harness/lumos-toolchain/scripts/lumos:18830)

呼叫關係是：

- 現況 low：hook 判 tier 一次，共 1 次。
- 改後 low：`code-loop check` 內判 tier一次，共仍是 1 次。
- 現況 high：hook 判 tier、印明細、check 內再判 tier，共 3 次。
- 改後 high：check 內判 tier、印明細，共 2 次。

所以確實能在 high 省一次，但 low 完全沒省。第 33 行若當成整體效益會高估；應改成「僅 high 路徑由 3 次降為 2 次」。

5. 回頭條件有日期接線，但沒有一個直接產出三態比例的統計查詢。  
severity: minor  
blocking:否  
引句:「REVISIT:2026-10-07 看治理帳 bound-tests 這一格:green/red/skipped 各幾筆。」  
位置:[計劃:82](/Users/enzo/harness/lumos-toolchain/docs/lumos-toolchain-knowledge/Projects/合約測試閘什麼時候跑_計劃.md:82)、[lumos:3690](/Users/enzo/harness/lumos-toolchain/scripts/lumos:3690)

實跑結果：

- `lumos gov --stats` 只顯示 `bound-tests` 合計 26 筆，不分 green/red/skipped。
- `lumos gov --full | rg '\[bound-tests/'` 能列出逐筆 kind，現在可再靠外部文字處理自行計數。
- 現有帳中可見 green、no-pins、diff-unavailable；沒有 skipped。

所以資料存在，但計劃所寫的「這一格」不能直接回答門檻。應把可重算的完整指令寫進 REVISIT，或讓 `gov --stats` 增加 kind 分帳；否則到期時仍靠人工臨時拼查詢。

第三條路是把 bound-tests 從 `code-loop check` 拆成獨立的唯讀判定入口，例如 `lumos bound-tests check --diff … --json`：pre-push 每個有效 ref 都先跑它，再獨立跑一次 pitfalls 並處理 code-loop 留痕。這能保持「測試與風險分級正交」、避免 rc1 與錯誤訊息混用，也不必為了跑合約測試把整支 code-loop 搬出去。代價是新增一個薄 CLI 接口，但核心仍直接重用現有 `_bound_tests_check`，不是複製實作。

既有圖譜裁定支持「不分 tier 真跑」，沒有找到要求維持 high-only 的裁定；真正衝突的是目前實碼接線，以及新分支首推的 fail-open 特例。結論：方向 (a) 合理，但按目前計劃字面只搬呼叫會產生錯誤處置，而且仍漏首推，不能進實作。
