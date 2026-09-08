severity: blocker
# r1 正確性席(sonnet)——棧別提問表態閘


## Findings

### C1 CI 讀不到 dispositions,tier=high 命中棧的推送在 CI 會被永久誤擋
severity: blocker
blocking: 是——不改,實作者只碰 DEP 列的函式就會交出「本機 pass 正確、CI 一律 BLOCKED」的系統。
spec 只在 DEP 列 `_codeloop_write`/`cmd_code_loop`,沒提到 `_codeloop_read_from_ledger`——但 `governance/code-loop/` 整個被 `.gitignore` 排除(已用 `git check-ignore` 驗證),CI 的乾淨 checkout 一定沒有那個 marker 檔,`check` 這時 100% 落到 `_codeloop_read_from_ledger` 重建的記錄,而那支重建函式的回傳字典寫死只有 `status/head_sha/note/ts`,沒有任何管道帶出 `dispositions`。
引句:「形狀好就寫進留痕記錄的 `dispositions` 欄與治理帳事件」
file: `scripts/lumos:20146` `_codeloop_read_from_ledger` 回傳 `{"status":..., "head_sha":..., "note":..., "ts":..., "_source": "ledger"}`,無 dispositions 鍵;file: `scripts/lumos:20728` 起 `cmd_code_loop` 的 `check` 走 `_codeloop_guard_verdict` → `_codeloop_read`,CI 呼叫路徑見 `.github/workflows` 內 `code-loop check --diff ... --repo .`(fetch-depth:0 全新 checkout)。
連帶:`cmd_gov` 讀 `.governance-log.jsonl` 的 `load()` mapper(file: `scripts/lumos:4666`)也是寫死欄位白名單(ts/commit/gate/kind/hard/nodes/detail),同樣不會把 dispositions 帶進 `rows`,S6 的死題候選統計字面上做不出來——除非額外改這兩支,而 spec 完全沒提。

### C2 `test:<名>` 錨點沒有走既有的多平台測試索引,polyglot repo 會全部誤判為懸空
severity: major
blocking: 是——consuming repo 一旦是 swift+node 這種多棧並存,`test:` 證據會被判「名字掃不到」,合法的 satisfied 表態被誤擋成 BLOCKED。
本 repo 已經有專門為「一個 repo 多個測試 profile」設計的機制(`load_platforms`/`_platform_test_index`/`resolve_test_refs`,含 `平台:名` 前綴語法),bound-tests-gate(spec 自己引為對齊對象)就是用這套;但 spec body 只寫單一 profile 呼叫,而 frontmatter KEY 卻自稱「profile 感知」,兩處對不上。
引句:「用該 repo 的 test profile 跑 `discover_test_methods`」
file: `scripts/lumos:3312` `load_test_profile` 只讀 `.lumos/config.json` 單一 `test_profile` 鍵;file: `scripts/lumos:7893` `_platform_test_index`/`load_platforms` 才是多平台版本;同日姊妹計劃 `docs/lumos-toolchain-knowledge/Projects/iOS與Node後端補棧_計劃.md` 明確會產生 iOS(swift)+Node 同 repo 並存的情境。

### C3 派工鏡頭 20 分鐘快取會讓 S5 的表態附件失效卻不報錯
severity: major
blocking: 是——審查席會在不知情下審到舊版(缺表態或表態被更正前的版本),對稱辯方機制因此失去材料來源的即時性保證。
`cmd_dispatch_lens` 的快取 key 只含 `(repo, base_sha, head_sha, schema)`,`code-loop pass --dispositions` 不改 head_sha,TTL 是 1200 秒——同一輪 code-loop 週期內(先派席、implementer 補表態、再派下一輪)重複呼叫鏡頭,20 分鐘內會直接吃到「表態出現前」的舊快取,沒有任何失效訊號。
引句:「派工鏡頭 diff 模式把 pass 記錄裡的表態附進派工單(有才附)」
file: `scripts/lumos:19093` `_lens_cache_read(path, ttl_sec=1200)`;file: `scripts/lumos:19086` `_lens_cache_path` 的 key 只吃 `repo_root|base_sha|head_sha|schema`,不含 code-loop 記錄狀態。

### C4 `code-loop skip` 與新表態閘的關係整篇沒交代——不管怎麼裁都有洞
severity: blocker
blocking: 是——兩種裁法都會讓實作者做出「照文件操作卻被擋」或「整個閘形同虛設」的系統,而 spec 沒有給出任何一種裁定。
S2/S3 全程只講 `pass --dispositions`,但 `check` 描述的是「讀當前 sha 的 pass 記錄」而現有程式碼把 `passed`/`skipped` 一視同仁地當有效留痕;pre-push 自己印給人看的逃生口原文就是 `lumos code-loop skip --note "..."`。若 skip 也要表態,使用者照官方印出的指示做仍會被擋;若 skip 豁免表態,那就是本計劃自己列為相關風險的「只退場不痛的機制」——一個不用回答任何棧問題的無痛退場。
引句:「讀當前 sha 的 pass 記錄,逐問核對——缺表態」
file: `scripts/lumos:20635-20650` `_codeloop_guard_verdict` 第 4 步同時接受 `rec_status in ("passed","skipped")`;file: `scripts/hooks/pre-push:199` 印給使用者的逃生指令正是 `lumos code-loop skip --note "為什麼跳過"`。

### C5 「留痕帳歷來 0 筆提到檢核答案」與帳本實測不符
severity: minor
blocking: 否——不影響任何要蓋的機制怎麼寫,只是立案理由的事實基礎有誤,不改變實作路徑。
`docs/.governance-log.jsonl` 裡 `gate=code-loop` 且狀態為 passed/skipped 的 175 筆事件中,19 筆的 `note`/`detail` 已經含「棧別檢核答」或「棧檢核」字樣的實際回答(如 2026-07-19/07-21/07-22/07-24 各筆),不是 0。
引句:「留痕帳(governance/code-loop 與治理帳)歷來 0 筆提到檢核答案」
file: `docs/.governance-log.jsonl` 例如 commit `4fdf8ca`(2026-07-19)、`d382e0e`(2026-07-21)的 `detail` 欄含「棧別檢核答案=…」「併發檢核答:…」字樣;`grep '"gate": "code-loop"' docs/.governance-log.jsonl | grep -c "檢核答\|棧檢核"` = 19。

## 逐節掃過、無 finding 的部分
frontmatter `related` 十條連結全部存在;DEP 列六支函式與三份文件都存在;`_pitfall_diff_collect` 的 `stack_questions` 資料結構、`_stack_key_for_file` 的 node/vue 分流、pre-push 的 tier=high/standard 分支邏輯,都與 spec 描述一致,已讀,無 finding。S1/S2/S3/S4/S6/S7 驗收條款本身敘述內部一致,問題出在它們共同依賴、卻沒點名要改的旁支函式(即 C1)。「刻意不做」節、REVISIT 節已讀,無 finding。

## 實務隱患鏡頭逐條
- 併發:「無」——`check` 是純讀 + append-only 事件寫,pre-push 與 CI 同時跑不會互相污染;`_codeloop_write` 本身非原子覆寫,但那是既有行為,本 spec 沒有加重它。
- 效能:`discover_test_methods(Path('.'))` 在本 repo 實測 0.035 秒(704 個方法),量體小;改走多平台索引後的疊加成本屬待驗。
- 資源:「無」——留痕檔與治理帳都是既有 JSON/JSONL 追加寫。
- 回滾:見 C4——閘誤擋時怎麼退,spec 沒有交代。

## 總結
最嚴重 severity 是 blocker(C1、C4),blocking 共 4 條(C1、C2、C3、C4)。
