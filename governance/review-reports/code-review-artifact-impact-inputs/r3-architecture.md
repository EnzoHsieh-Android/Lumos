severity: major
findings: 2

ID: R3-COR-1  
severity: major  
blocking: 是  
引句:「一般改名算新路徑；跨到被排除的簿記終點另保留舊程式、讀起點版本。」  
file: `scripts/lumos:24433`  
file: `docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md:31`

角色共用入口只有在終點屬 `_BOOKKEEPING_DIRS` 且已確定被排除時，才補回改名前的程式路徑，漏了兩個實際分支：

- 改名到 `_BOOKKEEPING_FILES`，例如 `src/tool.py → docs/.governance-log.jsonl`，不符合 `startswith(_BOOKKEEPING_DIRS)`，最後新舊兩側都被濾掉。
- 改名到簿記目錄的無副檔名附件，但首行因超限、特殊路徑、讀取失敗或期限耗盡而維持未知時，新側會被保守保留，補舊側的 `not _impact_diff_seed_ok(...)` 卻因此不成立；結果只剩無法判角色的新附件路徑，原 `.py` 的 backend 角色消失。

唯讀 in-memory 探針輸出：

```text
fixed-file []
unknown-head [('governance/review-reports/case/report', 'head')]
```

因此 impact 入口以 `--no-renames` 保留舊程式，但共享角色入口會漏掉同一支程式，兩個消費者判準分岔。現有 `t_impact_diff_bookkeeping_boundary_rename` 只覆蓋「目錄終點且分類已確定」的案例，抓不到上述反例。

ID: R3-GRAPH-1  
severity: minor  
blocking: 否  
引句:「Verification/2026-10-06_附件種子修復獨立驗收」  
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:48`  
file: `scripts/lumos:794`

新增的 `verified_by` 寫成純文字路徑，沒有 `[[...]]`。具名邊解析器只承認完整 wikilink；現場探針把目前值判為 `scalar`，加上雙括號才判為 `ok`。因此這筆驗證不會進正式 typed graph，與其他三個 Systems 節點的登記格式也不一致。

```text
plain ('scalar', 'Verification/2026-10-06_附件種子修復獨立驗收')
wikilink ('ok', ('Verification/2026-10-06_附件種子修復獨立驗收.md', ...))
```

架構對齊三問

1. 分層與依賴方向：新分類沿用 `_BOOKKEEPING_FILES`、`_BOOKKEEPING_DIRS`、既有 code-kind、首行判定及 raw parser，沒有另建目錄表；但 R3-COR-1 使 impact 與角色消費者在跨簿記改名上仍不一致。
2. 命名與失敗處理：模式、OID、刪檔舊側、staged 索引及工作目錄污染的判法一致；問題在於補償條件把「未知、所以保守保留」誤當成「已確認新側是程式」，丟失舊側角色資訊。
3. 第二種做法：未發現新 parser、新依賴或另一套副檔名表；批次總大小與 deadline 均為選填，舊 helper 未指定參數的語意保持。

固定席核對

1. `Systems/pitfalls-code-loop.md`：有影響；R3-COR-1 會讓共享角色選檔漏掉真正程式。
2. `Systems/lumos-cli-read.md`：未碰 search 的 superseded/stale 分流。
3. `Systems/bound-tests-gate.md`：未改合約綁定測試的阻擋判準。
4. `Systems/guard-kill.md`：未改 rc 優先序或 JSON stdout 合約。
5. `Systems/授權與歸屬.md`：未碰 vendored 授權白名單或 SPDX。
6. `Systems/測試假綠形態.md`：新增控制確實觸及模式、首行、改名與特殊路徑；但跨固定帳檔與未知終點仍缺控制。
7. `Systems/lumos-cli-lifecycle.md`：未碰 reinject 邊界。
8. `Systems/design-loop.md`：未改處置閘或條款綁定語意。

其餘固定席

- `Systems/loop-convergence-recording.md`
- `Systems/reversibility-governance-ledger.md`
- `Systems/lumos-deinit.md`
- `Systems/check-t-sentinel.md`
- `Systems/doctor-irreversible-hint.md`
- `Systems/cochange-guard.md`
- `Systems/節點範圍與索引守衛.md`
- `Systems/check-r-guard.md`
- `Systems/lumos-refcheck.md`
- `Systems/canary-audit.md`
- `Systems/slim-get-一行安裝.md`
- `Systems/slim-install-安裝器.md`
- `Systems/slim-uninstall-一行卸載.md`
- `Projects/雙向門放行_計劃.md`
- `Projects/規格落成可驗收條件_計劃.md`
- `Projects/逃逸自動記_計劃.md`
- `Systems/core-invariant-baseline.md`
- `Systems/judge-severity-gate.md`

材料與版本核對

- HEAD：`9a6e21e49a96677db09286a63beaf38f381a0104`
- 整合基準／merge-base：`56f38db9446a65a7fb7f0ef9da4073f2f3bb83b9`
- 完整實讀 `r3-source.patch` 708 行、`r3-graph.patch` 358 行，共 1066 行。
- source SHA-256：`6610f47277215a167f79cea1e4607471f29f12c9a2d0d7369793290ea81ed384`
- graph SHA-256：`28627f6966853f678ed3abd956a925d88229f2286de765b55f3a00651b183364`
- snapshot SHA-256：`efd9eef0b4c28a58a8173081655bc75a3e3c539211c791c254273fe21a5ffd2b`
- 三者均與 `r3-materials.json` 相符；source、graph 亦與凍結 Git 差異相符。
- `r3-snapshot.patch` 僅核對 24441 行及指紋，未宣稱全文讀取。

證據與未驗界線

- `r2-delivery-fix-check.json` 綁定凍結 HEAD、rc0；屬編排者既有執行，不是本席現場實測。
- `r2-final-lint-new.json` 綁 `77ad08f3`；該提交不是凍結 HEAD 的祖先，但兩版 source byte-equal。
- `r2-integrated-spec-push.json` 綁 `46ec9e7d`，且輸出只列另一篇計劃，未當成本功能目前版本的規格放行證據。
- `r2-integrated-subsets.json` 記載 73／64／25 條通過，但檔內沒有 head 或 source 指紋，未將它版本釘定為本席現場結果。
- 現場只執行 Git 指紋、版本核對及不落盤的 in-memory 反例探針；未跑全套或重算完整鏡頭。
- 工作樹存在既有髒帳與未追蹤卷證；被審 source／graph 檔本身與 HEAD 相同，探針未讀髒帳判行為。
- Windows、原混合分支 Python 結果判讀，以及既有設定讀取、name-status、角色內容兩趟讀取的完整正預算成本，均未驗且未宣稱封住。