severity: major

## rmax-resources-F1

severity: major  
blocking: 是

引句:「每份清單於本次呼叫按提交SHA快取，僅候選路徑送進既有分類器，不重建所有Systems筆記。」

觀察：`route_cache` 永不淘汰，而每個值保存 `_nodehome_list` 回傳的完整 `files` 字典及 `all_paths` 清單，不只是候選路徑。若 K 個提交都有測試家寫回候選、repo 有 P 條路徑，尖峰記憶體會由逐版可釋放變成 O(K×P)。

file: `scripts/lumos:26881`  
file: `scripts/lumos:27456`  
file: `scripts/lumos:27485`

判準：跨提交共用清單可以減少重讀，但不能把每個歷史版本的完整樹保留到整次檢查結束。線性歷史通常只需目前提交與相鄰父版，可用小型 LRU、使用次數淘汰或只保存候選所需的壓縮版面資料。

具體輸入 → 錯結果 → 可執行證據：在十萬路徑 repo 推送數百個提交，每個提交都改一支已宣告測試、其家及一支正式程式；每版 `ls-tree -r` 結果都被留存，pre-push 可能因記憶體耗盡被終止，而不是產生 home-check 判定。新增一個大量路徑×大量提交的子程序測試，量測尖峰 RSS 或限制 address space，並斷言結果完成且快取常駐版本數有界。現有一／十提交收據只數 git 程序，殺不掉這個保留量問題。

本席未動態重現：環境唯讀且沒有可用的自有 writable tmp；這是依資料結構生命週期作出的靜態結論。

## rmax-resources-F2

severity: major  
blocking: 是

引句:「side.where, side._reader, side.shebang = sha, read, shebang」

觀察：新路由證據把提交 SHA 的 reader 用來判定無副檔名候選的 shebang；但 `_nodehome_reader` 在 SHA 等於工作目錄 HEAD 時，先取得一次 `git diff` 清單，稍後對當時未變的路徑直接讀工作目錄。兩步之間沒有身份綁定。

file: `scripts/lumos:26933`  
file: `scripts/lumos:26942`  
file: `scripts/lumos:26947`  
file: `scripts/lumos:27497`

判準：作為某提交／父版的路由證據，其內容必須來自該 Git 物件；不能由稍後可能被其他會談或編輯器改動的工作目錄補值。可讓 route 專用 reader 強制 `git show`，或依 `_nodehome_list` 取得的 blob OID 讀同一物件。

具體輸入 → 錯結果 → 可執行證據：HEAD 中已改動但沒有 shebang 的 `tests/check` 與其測試家同提交；建立 reader 時工作目錄乾淨，隨後另一程序在實際讀首行前加上 shebang。路由會把未提交內容當成 HEAD 證據而錯誤放行；反向移除 shebang則會誤拒。加入具同步屏障的 diff-mode 測試：固定提交內容，讓工作目錄在 changed-list 與 read 之間變動，兩個方向都應始終依提交 blob 判定。現有 staged/index 的 shebang 正反控制沒有覆蓋這個 push/HEAD 競態。

本席未動態重現，原因同上。

## 固定節點判定

- `Systems/design-loop`：處置閘第五步與條款檢查未改；H 僅收緊載體快照讀取錯誤，未破壞該 invariant。
- `Systems/pitfalls-code-loop`：沒有正式硬合約；本批未改 pitfalls 分級或處置語意。
- `Systems/bound-tests-gate`：固定席合約測試的選取、執行及 blocked 判定未改。
- `Systems/guard-kill`：rc 優先序與 JSON 純度路徑均未觸及。
- `Systems/授權與歸屬`：未改 vendored toolkit 清單、移除流程或授權檔頭。
- `Systems/測試假綠形態`：新增控制具前置狀態及變異證據；正式 invariant 未破壞，但上述大量快取與 push/HEAD 競態尚無殺傷控制。
- `Systems/lumos-cli-read`：search 的 superseded/stale 過濾路徑未改。
- `Systems/lumos-cli-lifecycle`：re-inject sentinel 外 byte-equal 行為未改。
- 圖譜欄位：本批新增 WHY 均有出處；新增 PITFALL 均有出處與防回歸入口，未套用比 AGENTS v1.0 更嚴的欄位要求。

僅列名鏡頭：`loop-convergence-recording`、`reversibility-governance-ledger`、`lumos-deinit`、`check-t-sentinel`、`節點範圍與索引守衛`、`check-r-guard`、`doctor-irreversible-hint`、`cochange-guard`、`lumos-refcheck`、`canary-audit`、`slim-get-一行安裝`、`slim-install-安裝器`、`slim-uninstall-一行卸載`、`雙向門放行_計劃`、`異常派工單回報輸入錯誤_計劃`、`引用座標依實際換行_計劃`、`規格落成可驗收條件_計劃`、`逃逸自動記_計劃`、`core-invariant-baseline`、`judge-severity-gate`。

## 已讀材料

- source：`governance/review-reports/code-convergence-input-guards/r1-source.patch`，524/524 行。
- graph：`governance/review-reports/code-convergence-input-guards/r1-graph.patch`，534/534 行。
- full-index：`governance/review-reports/code-convergence-input-guards/r1-file-index.txt`，238/238 行。
- lens：使用者附加的 LUMOS-IMPACT 固定席內容，以及 `scripts/lumos` 的 canary identity、nodehome reader/list/cache/evaluate 定點上下文。
- 規則：`/Users/enzo/.agents/skills/lumos-project-notes/SKILL.md`、`lumos-code-loop/SKILL.md`、`python-idioms/SKILL.md`。
- 未讀其他席報告、raw 報告、bundle、舊探針或 12914 行完整快照；未重跑測試。

最高級：major  
blocking finding：2