severity: minor

## Finding

### delivery-資安-security-nodes-codex-F1

severity: minor  
blocking: 否

引句:「每個案例在治理卷證本案目錄的 real-input-receipts/ 保存獨立JSON：case_id、時間、CLI提交與SHA256、report/snapshot bytes的SHA256、原命令參數、拒收rc/stdout/stderr、帳前後SHA256或不存在、失敗類型（編碼/I/O）、配對修正後重試的命令/rc/成功帳token/材料與帳雜湊。」

審材外佐證file: `scripts/lumos:9702`  
審材外佐證file: `scripts/lumos:9705`  
審材外佐證file: `scripts/lumos:9727`

觀察：新增收據格式要求保存原始命令參數及完整 stdout/stderr，但只用散文要求「非敏感」，沒有欄位白名單、遮罩規則或保存授權。實際入口會把呼叫者提供的 report/snapshot 路徑及底層 I/O 錯誤寫進 stderr，並輸出帶原始路徑的重跑命令。若卷證被提交、打包或交給其他審查席，可能洩漏本機路徑、材料名稱或輸出中的敏感資料。

是否本批新增：是。原 CLI 的路徑輸出既有；本批新增的是把原始參數及完整輸出納入治理卷證的收集格式。

攻擊路徑需要操作者實際保存或分享收據，且文件明載沒有自動收集器，因此定為 minor、非阻擋。建議預設只保存雜湊、退出碼及允許清單欄位；需要完整輸出時先做秘密掃描與路徑遮罩，並明定誰可核准、卷證是否可提交。

## 安全鏡頭

- 誰／權限：入口由本機 repo 操作者或審查編排者執行，未看到材料文字自行取得執行權限。除 F1 的卷證保存邊界外，已讀範圍無 finding。
- 可執行入口：核對 `cmd_canary`、`cmd_home_check` 與補助測試路由。snapshot/report 只作讀取、解碼、雜湊及解析；已讀範圍未見由材料內容進入 `eval`、`exec` 或 shell 的路徑，無 finding。
- 不可信輸入：負數 findings、非法 UTF-8、讀取失敗、材料 ABA、角色卡文字及測試宣告均採拒收或撤回補助證據；無新增越權 finding。
- 秘密／注入：命令參數和完整輸出的保存規格有 F1。遠端 Git bundle 驗證只還原物件並核對 commit/tree/blob，已讀文字沒有要求 checkout 或執行其中程式，無額外 finding。
- 收益：守衛收益是避免未驗材料落入只進不出的治理帳，以及避免途中替換的測試宣告取得背書；沒有觀察到擴張產品或網路權限。

## Graph lens 逐項判定

- `Issues/canary-record未落盤事件.md`：影響；本批直接改變拒收時是否追加 canary 帳及失敗留痕。
- `Systems/lumos-cli-read.md`：不影響；未改 search 的 stale/superseded 過濾。
- `Systems/design-loop.md`：影響；`cmd_canary` 輸入驗證與處置帳屬其入口。
- `Systems/pitfalls-code-loop.md`：不影響；已讀差異沒有改 pitfalls 風險分級。
- `Systems/bound-tests-gate.md`：不影響；補助測試路由不改 code-loop 綁定測試閘的執行語意。
- `Systems/guard-kill.md`：不影響；未改七態、退出碼或 JSON 純度。
- `Systems/授權與歸屬.md`：不影響；未動授權檔白名單或 vendored 刪除流程。
- `Systems/測試假綠形態.md`：影響；本批驗證大量依賴先紅後綠、故障注入與現場前置斷言。
- `Systems/loop-convergence-recording.md`：影響；處置帳、修補歸因和跑滿回顧證據直接進入收斂紀錄。
- `Systems/lumos-cli-lifecycle.md`：不影響；未改安裝、啟動或版本生命週期。
- `Systems/reversibility-governance-ledger.md`：影響；拒收仍可能寫 blocked telemetry，且成功帳不可撤回。
- `Systems/lumos-deinit.md`：不影響；沒有卸載或刪檔路徑變更。
- `Systems/節點範圍與索引守衛.md`：影響；補助測試證據改為固定 index tree 並處理 ABA。
- `Systems/check-t-sentinel.md`：不影響；已讀差異未改 sentinel。
- `Systems/doctor-irreversible-hint.md`：不影響；未改 doctor 不可逆提示。
- `Systems/check-r-guard.md`：不影響；未見 check-r 判定變更。
- `Systems/cochange-guard.md`：不影響；未改共同變更規則。
- `Systems/lumos-refcheck.md`：不影響；未改引用完整性檢查。
- `Systems/canary-audit.md`：影響；report/snapshot、findings 及處置清單都經 canary 入口。
- `Systems/slim-get-一行安裝.md`：不影響；未改下載入口。
- `Systems/slim-install-安裝器.md`：不影響；未改安裝器。
- `Systems/slim-uninstall-一行卸載.md`：不影響；未改卸載器。
- `Projects/雙向門放行_計劃.md`：不影響；沒有改雙向門的放行條件。
- `Projects/規格落成可驗收條件_計劃.md`：影響；快照拒收條款及其驗證以 spec gate 收貨。
- `Projects/引用座標依實際換行_計劃.md`：影響；載體席仍以引句能否錨回 snapshot 作寫入前判定。
- `Projects/逃逸自動記_計劃.md`：影響；被擋輸入會留下治理 blocked 事件。
- `Projects/異常派工單回報輸入錯誤_計劃.md`：影響；非法編碼、讀取失敗及角色卡診斷都屬輸入錯誤界線。
- `Systems/core-invariant-baseline.md`：不影響；未改核心 invariant 基線。
- `Systems/judge-severity-gate.md`：影響；report severity 正規化及 findings 計數會決定記帳能否通過。
- 鏡頭所稱「1 個新增／改名檔未列」：名稱不可得，無法判定影響，未假填不影響。

## 閱讀與限制

- 固定 HEAD：已核對為 `c09d12037d1f0d5a5ce92bd09ccda1ed048a2319`。
- 指定 patch：實讀 904／2,291 行。
- mirror：57／57 行。
- 規則：`lumos-project-notes` 94 行、`CLAUDE.md` 101 行。
- 搜索輸出：327 行；重讀 0 行。
- 同版程式佐證：472 行。
- 工具端可精確計數合計：1,956 行；另有對話內派工及 AGENTS 正文未取得機器行數，因此實際總數更高。
- 一次寬搜尋意外返回 268 行，超過單次 150 行及全席 1,800 行限制；這是本席執行限制，未隱去。
- 未讀 patch：`151–865`、`1184–1533`、`1611–1678`、`1778–2031`，共 1,387 行。
- 因材料本身已超額且存在上述未讀範圍，本報告不是完整 clean，只對實讀安全範圍提出一項 minor finding。